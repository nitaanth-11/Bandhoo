import json
import os
import re
# BANDHOO_SKIP_DOTENV=1 lets tests import the app without reading .env.
if os.environ.get("BANDHOO_SKIP_DOTENV") != "1":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from complaint_engine import ComplaintStructureRequest, assess_point, structure_for_api

app = FastAPI()

# CORS restrictions: configurable via BANDHOO_CORS_ORIGINS; defaults to local development origins.
CORS_ORIGINS_ENV = os.environ.get("BANDHOO_CORS_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in CORS_ORIGINS_ENV.split(",") if o.strip()] or [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    import logging
    logger = logging.getLogger("bandhoo.api")
    logger.error("Unhandled API error on %s: %s", request.url.path, type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content={"error": "An internal error occurred while processing the request."}
    )

from legal_engine.synonyms import DEFAULT_SYNONYM_MAP as SYNONYM_MAP


def translate_synonyms(text: str):
    """
    Scans the narrative text, locates matched synonyms, and outputs a 
    standardized format for classification (RAG & Logistic Regression).
    """
    if not text:
        return "", []
    
    translations = []
    standardized_text = text
    
    # Sort keys by length descending so that multi-word terms match before single words
    sorted_syns = sorted(SYNONYM_MAP.keys(), key=len, reverse=True)
    
    for syn in sorted_syns:
        pattern = r'\b' + re.escape(syn) + r'\b'
        if re.search(pattern, standardized_text, re.IGNORECASE):
            std_term = SYNONYM_MAP[syn]
            translations.append({
                "synonym": syn,
                "standard_term": std_term
            })
            standardized_text = re.sub(pattern, std_term, standardized_text, flags=re.IGNORECASE)
            
    return standardized_text, translations

# ── Load the police stations dataset ──
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "police_stations_data.json")

if not os.path.exists(json_path):
    raise FileNotFoundError(f"Required station dataset not found at: {json_path}")

with open(json_path, "r", encoding="utf-8") as f:
    stations_data = json.load(f)

# Filter for Subtype = 'Station'. Note: the coordinates are jurisdiction-polygon centroids, not station
# addresses, and the dataset has no contact details. Jurisdiction is assessed by polygon containment.
stations = [s for s in stations_data if s['subtype'] == 'Station']
stations_by_name = {s['name']: s for s in stations}

# ── Initialize Modular Legal Engine ──
from legal_engine import (
    BNSCorpus,
    BM25LegalRetriever,
    GeminiLegalClient,
    LegalAnalysisService,
    NarrativeInput,
    OffenceClassificationResponse
)

legal_corpus = BNSCorpus()
legal_retriever = BM25LegalRetriever(legal_corpus)
gemini_client = GeminiLegalClient()
legal_service = LegalAnalysisService(
    corpus=legal_corpus,
    retriever=legal_retriever,
    llm_client=gemini_client,
    synonym_map=SYNONYM_MAP
)

print(f"[LegalEngine] Loaded {len(legal_corpus.sections_by_num)} verified BNS sections.")
print(f"[LegalEngine] BM25 Index initialized: {legal_retriever.bm25 is not None}")
print(f"[LegalEngine] Gemini LLM active: {gemini_client.is_available} (Model: {gemini_client.model_name})")


# ── Pydantic Models ──

class Location(BaseModel):
    latitude: float
    longitude: float


# ── Endpoints ──

@app.post("/api/get-jurisdiction")
async def get_jurisdiction(loc: Location):
    """
    Polygon-containment jurisdiction estimate. A station is named only when the point lies inside exactly
    one polygon and is not near a boundary; otherwise station is null and confirmation is required.
    """
    result = assess_point(loc.latitude, loc.longitude)
    return {
        "station": result.station,
        "status": result.status,
        "method": result.method,
        "distance_to_boundary_m": result.distance_to_boundary_m,
        "message": result.message,
        "boundary_data": result.boundary_data,
        "details": stations_by_name.get(result.station) if result.station else None,
    }


@app.post("/api/v1/complaints/structure")
async def structure_complaint(data: ComplaintStructureRequest):
    """
    Structures a complainant's account into a source-attributed record (LangGraph workflow).
    Deterministic extraction only: no external model or geocoding service is called. Nothing is stored,
    verified or submitted. Verification events cannot be supplied through this endpoint.
    If the statement could not be structured, the response is an error (500, or 503 when external tracing
    is configured) that returns the received statement verbatim with "review_status_unavailable".
    """
    status, body = structure_for_api(data)
    return body if status == 200 else JSONResponse(status_code=status, content=body)


@app.post("/api/classify-offence", response_model=OffenceClassificationResponse)
async def classify_offence(data: NarrativeInput):
    """
    Intelligent BNS legal section classifier.
    Combines BM25 statutory retrieval with Google Gemini legal reasoning.
    Preserves complete backwards-compatibility with existing frontend.
    """
    result = legal_service.analyze_complaint(data)
    return result


@app.get("/api/bns-stats")
async def bns_stats():
    """Return health and statistics about the loaded BNS legal engine."""
    return {
        "sections_loaded": len(legal_corpus.sections_by_num),
        "bm25_ready": legal_retriever.bm25 is not None,
        "llm_available": gemini_client.is_available,
        "llm_model": gemini_client.model_name if gemini_client.is_available else "offline",
        "excluded_sections": legal_corpus.excluded_sections
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)