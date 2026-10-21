# Bandhoo Security, Privacy and Dependency Hardening Report

**Document Identifier:** HARDENING-REPORT-2026-V1  
**Status:** Completed / Ready for Review  
**Checkpoint:** Checkpoint 5 — Security, Privacy and Dependency Hardening  
**Target Audience:** Project Owners (PO), Security Reviewers, Data Privacy Officers, and Maintainers (MNT).

---

## 1. Executive Summary & Remediation Register

This checkpoint addresses core application security, third-party data privacy exposure, frontend maintainability, and installation reproducibility.

| Domain | Issue / Risk | Baseline State | Hardened Remediation State | Status |
| :--- | :--- | :--- | :--- | :--- |
| **CORS Policy** | Open cross-origin access allowed unauthorized origins to invoke backend endpoints. | `allow_origins=["*"]` in `main.py` | Configurable via `BANDHOO_CORS_ORIGINS`; restricted by default to local origins (`5173`, `3000`, `8001`). | **Resolved** |
| **Frontend API URL** | Hardcoded port 8001 broke containerized or proxy deployments. | Hardcoded `http://localhost:8001` on lines 423, 475, 593 in `src/App.jsx`. | Dynamic `API_BASE_URL = (import.meta.env && import.meta.env.VITE_API_BASE_URL) \|\| 'http://localhost:8001'`. | **Resolved** |
| **Code Quality (ESLint)**| 3 longstanding lint findings (2 errors, 1 warning). | Unused `React`; `updateLocation` hoisted access; missing `useEffect` deps. | Unused imports removed; `updateLocation` wrapped in `useCallback` and declared before use; stable refs deployed. `npm run lint` exited 0 (clean). | **Resolved** |
| **Dependency Pinning** | Loose `>=` upper bounds risking broken builds or unvalidated upgrades. | Unpinned `>=` entries in `requirements.txt`. | Exact tested versions pinned in `requirements-lock.txt` for reproducible installation. | **Resolved** |
| **Exception Logging** | Default FastAPI unhandled exceptions leak internal tracebacks. | No global exception handler in `main.py`. | Global exception handler implemented; logs only route and exception class; sanitizes 500 responses. | **Resolved** |
| **Third-Party Data Flows**| Unauthorized transmission of complaint text or coordinates to external vendors. | Gemini, OpenStreetMap, Nominatim, and LangSmith active or configured. | Comprehensive data flow audit executed; retention and privacy risks documented; external geocoding disabled by default. | **Documented** |

---

## 2. Technical Remediations Detailed

### 2.1 CORS Restrictions (`main.py`)
Previously, `main.py` configured:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```
**Remediation**:
```python
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
```
Production deployments can now supply an explicit comma-separated allowlist via `BANDHOO_CORS_ORIGINS="https://police.mumbai.gov.in"`.

---

### 2.2 Configurable Frontend API Base URL (`src/App.jsx`)
All backend API calls now route through `API_BASE_URL`:
```javascript
const API_BASE_URL = (import.meta.env && import.meta.env.VITE_API_BASE_URL) || 'http://localhost:8001';
```
Calls updated:
- Jurisdiction lookup: `${API_BASE_URL}/api/get-jurisdiction`
- Offence classification: `${API_BASE_URL}/api/classify-offence`
- Complaint structuring: `${API_BASE_URL}/api/v1/complaints/structure`

---

### 2.3 Remediation of the Three ESLint Findings (`src/App.jsx`)
1. **Unused React Error (`no-unused-vars`)**:
   - Removed unused `React` default import from `src/App.jsx:1`.
2. **Access Before Declaration Error (`react-hooks/immutability`)**:
   - `updateLocation` was declared at line 410, but referenced inside the map initialization `useEffect` at line 342.
   - Refactored: `updateLocation` declared prior to `useEffect` wrapped in `useCallback` with `jurisdictionsGeoJSON` dependency.
3. **Exhaustive Dependencies Warning (`react-hooks/exhaustive-deps`)**:
   - Integrated `updateLocationRef` and `initialCoordsRef` to provide stable references for Leaflet event listeners (`dragend`, `click`, `layer.on`).
   - The map instance is created once on mount and cleanly torn down on unmount without spurious re-renders.

**Verification**:
```bash
$ npm run lint
> temp-app@0.0.0 lint
> eslint .
# Exit code 0 (0 errors, 0 warnings)
```

---

### 2.4 Dependency Pinning & Reproducibility (`requirements-lock.txt`)
To ensure hermetic, reproducible builds across developer and production environments, exact verified package versions were pinned into `requirements-lock.txt`:
```text
fastapi==0.143.0
uvicorn==0.52.4
pydantic==2.13.5
numpy==1.26.4
scipy==1.16.3
rank-bm25==0.2.2
google-genai==2.31.0
python-dotenv==1.1.1
langgraph==1.2.16
langchain-core==1.6.12
langgraph-checkpoint==4.3.0
pytest==9.0.3
```

---

### 2.5 Error Handling & Log Sanitization (`main.py`)
To prevent PII leakage, complaint narrative exposure, and internal stack trace leakage, a global exception handler was bound to FastAPI:
```python
@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    import logging
    logger = logging.getLogger("bandhoo.api")
    logger.error("Unhandled API error on %s: %s", request.url.path, type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content={"error": "An internal error occurred while processing the request."}
    )
```
Internal stack traces and narrative text are never returned in HTTP 500 bodies or dumped into stdout.

---

## 3. Data Flow & External Processors Privacy Audit

```mermaid
graph LR
    User[Citizen User] -->|1. Browser UI| App[React Frontend]
    App -->|2. Internal API Calls| Backend[FastAPI Backend]
    Backend -->|3. Deterministic| LL[Local Structuring & BM25]
    Backend -.->|4. Optional Remote| Gemini[Google Gemini API]
    App -.->|5. Map Tiles| OSM[OpenStreetMap CDN]
    App -.->|6. Geocoding (Disabled)| Nominatim[OSM Nominatim]
    Backend -.->|7. Tracing (Blocked)| LangSmith[LangSmith Cloud]
```

### 3.1 Processor 1: Google Gemini API (`generativelanguage.googleapis.com`)
* **Trigger**: Invoked during `/api/classify-offence` ONLY when `GEMINI_API_KEY` is present in the environment.
* **Payload**: Full raw complaint narrative (`narrative`) and retrieved BNS section definitions.
* **Privacy & Retention Risk**:
  * Unauthenticated or standard consumer tier API keys permit Google to log, retain, and review prompts for model training under Google AI terms of service.
  * In the absence of an Enterprise Vertex AI Business Associate Agreement (BAA) / sovereign Indian data-residency agreement, sending citizen crime disclosures violates Section 4 and Section 8 of the Indian Digital Personal Data Protection Act, 2023 (DPDP Act).
* **Policy Invariant**:
  * The system defaults to deterministic offline BM25 fallback when no API key is supplied.
  * **Rule: Real complainant narratives must never be processed through the external Gemini API without explicit citizen consent and an approved sovereign data-processing agreement.**

### 3.2 Processor 2: OpenStreetMap Tile Servers (`tile.openstreetmap.org`)
* **Trigger**: Invoked by the Leaflet map layer whenever the incident locator map is viewed in the browser.
* **Payload**: User IP address, HTTP User-Agent, and requested tile coordinate bounding boxes (`z/x/y.png`).
* **Privacy & Retention Risk**: Tile fetch logs allow third-party network operators to infer the approximate physical location of the complainant based on tile geographic extents combined with client IP address.
* **Remediation Recommendation**: For government or production deployment, replace public OSM tile servers with a self-hosted vector/raster tile cache (e.g. offline MBTiles served locally).

### 3.3 Processor 3: Nominatim Reverse Geocoding (`nominatim.openstreetmap.org`)
* **Trigger**: Reverse geocoding on marker click/drag.
* **Payload**: Exact latitude and longitude coordinates.
* **Current Enforcement**: **Disabled by default** via `EXTERNAL_GEOCODING_ENABLED = false` in `src/trustSafety.js`.
* **Policy Invariant**: Must remain disabled unless an internal, on-premise geocoder is deployed.

### 3.4 Processor 4: LangSmith Tracing (`api.smith.langchain.com`)
* **Trigger**: Activated if standard LangChain environment variables (`LANGSMITH_TRACING=true`) are present.
* **Payload**: Full complaint state, extracted victim/suspect facts, evidence files, and verification events.
* **Current Enforcement**: **Hard-refused by code** in `complaint_engine/graph.py`. The engine throws `ExternalTracingRefused` and halts startup if external tracing variables are detected without explicit administrative override.

---

## 4. Verification Test Battery

1. **ESLint Static Analysis**:
   ```powershell
   npm run lint
   # Output: 0 errors, 0 warnings. (Exit code 0)
   ```
2. **Frontend Trust & Safety Invariants**:
   ```powershell
   node --test src/trustSafety.test.js
   # Output: 23/23 tests passing. (Exit code 0)
   ```
3. **Backend API & Jurisdiction Tests**:
   ```powershell
   python -m pytest tests/test_jurisdiction_and_api.py
   # Output: 12/12 tests passing. (Exit code 0)
   ```

---
*End of Hardening Report HARDENING-REPORT-2026-V1*
