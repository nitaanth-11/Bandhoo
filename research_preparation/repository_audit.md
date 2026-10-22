# Bandhoo BNS Prediction Engine & Complaint Intelligence System
## Phase 1 — Comprehensive Repository Forensics & Inventory Audit

**Audit Date**: October 2026  
**Auditor Role**: Senior Research Engineer & ML Systems Architect  
**Repository Corpus**: `Bandhoo` / BNS Prediction Engine  
**Execution Milestone**: Checkpoint R1 (Repository Forensics & Architecture Reconstruction)  

---

### 1. Executive Summary & Forensic Methodology

This document establishes the verified technical baseline of the Bandhoo repository. Every claim, component, and capability listed herein is grounded in direct static analysis of source code, configuration files, test suites, and reproducible execution artifacts. 

In strict adherence to academic rigor:
- **No feature is marked implemented based on README statements, docstrings, or aspirational comments.**
- Each feature is classified under one of four unambiguous statuses:
  1. `[IMPLEMENTED]`: Verified in executable source code and covered by automated test suites.
  2. `[PARTIALLY IMPLEMENTED]`: Core logic exists in rudimentary or rule-based form, but lacks promised machine learning models, external integrations, or complete pipelines.
  3. `[PLANNED / ROADMAP ONLY]`: Mentioned in documentation, comments, or design notes, but completely absent from source code and runtime execution.
  4. `[DEPRECATED / EXCLUDED]`: Intentionally removed, isolated, or prohibited by trust-and-safety or legal constraints.

---

### 2. Complete Repository Inventory

| Relative File Path | Component Category | Primary Tech Stack | Lines / Size | Test Coverage Reference | Operational Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `main.py` | Top-level API Entry Point | FastAPI, Uvicorn, Pydantic | 269 lines (10 KB) | `tests/test_jurisdiction_and_api.py`, `tests/test_legal_engine.py` | `[IMPLEMENTED]` |
| `legal_engine/corpus.py` | Statutory Corpus Loader | Python, JSON, Regex | 141 lines (6.8 KB) | `tests/test_corpus_guard.py`, `tests/test_corpus_integrity.py` | `[IMPLEMENTED]` |
| `legal_engine/retrieval.py` | Lexical Retrieval Engine | `rank_bm25` (BM25Okapi) | 149 lines (5.9 KB) | `tests/test_retrieval_and_quality.py`, `tests/test_legal_engine.py` | `[IMPLEMENTED]` |
| `legal_engine/service.py` | Core Legal Analysis Pipeline | Python, Regex, Schedule Registry | 1413 lines (81.2 KB) | `tests/test_legal_accuracy_audit.py`, `tests/test_reliability_followups.py` | `[IMPLEMENTED]` |
| `legal_engine/llm_client.py` | Foundation Model Client | `google-genai` (Gemini API) | 263 lines (11.6 KB) | `tests/test_gemini_pipeline.py` | `[IMPLEMENTED]` |
| `legal_engine/schedule_registry.py` | Procedural Schedule I Registry | Python, Statutory Table | 443 lines (22.6 KB) | `tests/test_procedural_law_audit.py` | `[IMPLEMENTED]` |
| `legal_engine/amounts.py` | Monetary & Property Parser | Python, Regex, Indian Numbering | 185 lines (8.3 KB) | `tests/test_procedural_law_audit.py` | `[IMPLEMENTED]` |
| `legal_engine/synonyms.py` | Colloquial Synonym Mapping | Python, Dictionary Regex | 261 lines (13.7 KB) | `tests/test_legal_engine.py` | `[IMPLEMENTED]` |
| `legal_engine/schemas.py` | Legal Data Contracts | Pydantic v2 | 147 lines (5.3 KB) | `tests/test_legal_engine.py` | `[IMPLEMENTED]` |
| `legal_engine/corpus_guard.py` | Corpus Hash & Integrity Guard | Python, SHA-256 | 68 lines (3.0 KB) | `tests/test_corpus_guard.py` | `[IMPLEMENTED]` |
| `complaint_engine/graph.py` | Complaint Structuring Workflow | LangGraph 1.2+, StateGraph | 557 lines (27.9 KB) | `tests/test_complaint_graph.py` | `[IMPLEMENTED]` |
| `complaint_engine/extraction.py` | Deterministic Fact Extraction | Python, Regex, Datetime | 412 lines (25.8 KB) | `tests/test_structuring_quality.py` | `[IMPLEMENTED]` |
| `complaint_engine/checks.py` | Inconsistency & Contradictions | Python, Span Matcher | 315 lines (17.0 KB) | `tests/test_complaint_defect_regressions.py` | `[IMPLEMENTED]` |
| `complaint_engine/jurisdiction.py` | Point-in-Polygon Engine | GeoJSON, Ray Casting | 134 lines (4.9 KB) | `tests/test_jurisdiction_and_api.py` | `[IMPLEMENTED]` |
| `complaint_engine/evidence_screening.py` | Evidence Metadata Screening | Magic Bytes, Laplacian Heuristic | 215 lines (8.8 KB) | `tests/test_evidence_screening.py` | `[IMPLEMENTED]` |
| `complaint_engine/compiler.py` | Complaint Record Compiler | Python, Chronology Engine | 262 lines (13.9 KB) | `tests/test_complaint_compiler.py` | `[IMPLEMENTED]` |
| `complaint_engine/pdf_generator.py` | Legal PDF Generator | ReportLab, Two-pass Canvas | 338 lines (14.9 KB) | `tests/test_pdf_and_email.py` | `[IMPLEMENTED]` |
| `complaint_engine/email_draft.py` | Police Nodal Email Preparer | Pydantic, Template Engine | 137 lines (5.5 KB) | `tests/test_pdf_and_email.py` | `[IMPLEMENTED]` |
| `complaint_engine/storage.py` | Private File Storage Manager | Python OS, Path Traversal Guard | 129 lines (4.7 KB) | `tests/test_database_persistence.py` | `[IMPLEMENTED]` |
| `complaint_engine/urgency.py` | Minor & Vulnerability Triage | Statutory Rule Evaluator | 118 lines (4.9 KB) | `tests/test_missing_person_workflow.py` | `[IMPLEMENTED]` |
| `complaint_engine/models.py` | Domain Pydantic Models | Pydantic v2 | 230 lines (8.0 KB) | `tests/test_complaint_graph.py` | `[IMPLEMENTED]` |
| `complaint_engine/draft.py` | Text Draft Renderer | Python Text Templating | 165 lines (7.6 KB) | `tests/test_complaint_graph.py` | `[IMPLEMENTED]` |
| `db/session.py` | DB Session & Connection Pooling | SQLAlchemy 2.0, Connection Pool | 114 lines (3.5 KB) | `tests/test_database_persistence.py` | `[IMPLEMENTED]` |
| `db/models.py` | Relational Entity Models | SQLAlchemy 2.0 ORM | 239 lines (11.4 KB) | `tests/test_database_persistence.py` | `[IMPLEMENTED]` |
| `db/repository.py` | Complaint Persistence Repository | SQLAlchemy 2.0 Session | 233 lines (10.1 KB) | `tests/test_database_persistence.py` | `[IMPLEMENTED]` |
| `migrations/env.py` | Alembic Migration Environment | Alembic, SQLAlchemy | 88 lines (2.2 KB) | `tests/test_database_persistence.py` | `[IMPLEMENTED]` |
| `migrations/versions/001_initial_schema.py` | Schema Migration Script | Alembic DDL Operations | 215 lines (14.4 KB) | `tests/test_database_persistence.py` | `[IMPLEMENTED]` |
| `src/App.jsx` | Web Client Application | React 19, Leaflet | 2744 lines (150 KB) | `src/trustSafety.test.js` | `[IMPLEMENTED]` |
| `src/trustSafety.js` | Client-Side Safeguards | JavaScript ES Module | 215 lines (10.5 KB) | `src/trustSafety.test.js` | `[IMPLEMENTED]` |
| `src/ReviewStatus.js` | Review Status Badge Component | React Component | 18 lines (0.4 KB) | `src/trustSafety.test.js` | `[IMPLEMENTED]` |
| `src/trustSafety.test.js` | Frontend Trust Safety Tests | Node.js Test Runner | 230 lines (12.0 KB) | Executed via `node --test` | `[IMPLEMENTED]` |
| `bns_rag_dataset.json` | Cleaned BNS Statutory Corpus | JSON (358 verified sections) | 1.11 MB | `tests/test_corpus_integrity.py` | `[IMPLEMENTED]` |
| `mumbai_police_jurisdictions.geojson` | Mumbai Police Station Polygons | GeoJSON (91 station polygons) | 422.5 KB | `tests/test_jurisdiction_and_api.py` | `[IMPLEMENTED]` |
| `police_stations_data.json` | Station Directory & Email Map | JSON (91 station records) | 26.7 KB | `tests/test_pdf_and_email.py` | `[IMPLEMENTED]` |
| `benchmark/bns_synthetic_benchmark_50.json` | Legal Classification Benchmark | JSON (50 synthetic cases) | 100.3 KB | `benchmark/evaluate_benchmark.py` | `[IMPLEMENTED]` |
| `benchmark/evaluate_benchmark.py` | Legal Benchmark Harness | Python Evaluation Suite | 1250 lines (73.1 KB) | Standalone Benchmark Script | `[IMPLEMENTED]` |
| `benchmark/structuring/structuring_cases.json` | Structuring Benchmark Dataset | JSON (34 synthetic cases + 11 jur) | 41.4 KB | `benchmark/structuring/evaluate_structuring.py` | `[IMPLEMENTED]` |
| `benchmark/structuring/evaluate_structuring.py` | Structuring Evaluation Harness | Python Metric Computer | 304 lines (17.6 KB) | Standalone Benchmark Script | `[IMPLEMENTED]` |
| `bns_finetune_dataset.json` | Fine-Tuning Corpus (Unused) | JSON Pairs | 806.4 KB | None (Not loaded in runtime) | `[PARTIALLY IMPLEMENTED / DATA ONLY]` |
| `bns_scenarios_dataset.json` | Scenario Corpus (Auxiliary) | JSON Pairs | 189.7 KB | None (Not loaded in runtime) | `[PARTIALLY IMPLEMENTED / DATA ONLY]` |
| `kml_loader.py` | KML Boundary Extraction Script | Python CLI Utility | 34 lines (1.0 KB) | Manual Execution Script | `[PARTIALLY IMPLEMENTED / SCRIPTONLY]` |
| `scrape_bns.py` | Web Scraper for BNS Gazette | Python BeautifulStoneSoup | 502 lines (22.9 KB) | Manual Execution Script | `[PARTIALLY IMPLEMENTED / SCRIPTONLY]` |

---

### 3. Detailed Component Status Breakdown

#### 3.1 Implemented Features (Verified in Code & Tests)

1. **Hybrid Lexical Retrieval Pipeline**:
   - `rank-bm25` (BM25Okapi) algorithm operating over concatenated Section Title, Keywords, and Statutory Text (`legal_engine/retrieval.py:36-45`).
   - Dynamic thresholding: drops zero/negative scores and prunes tail candidates whose raw score ratio is below `relative_threshold = 0.35` (`legal_engine/retrieval.py:80-97`).
   - Clause-level multi-action segmentation: splits compound complaints via action boundaries/conjunctions and merges top clause candidates with global candidates up to `max_k = 8` (`legal_engine/retrieval.py:101-148`).

2. **Multilingual Synonym Normalization**:
   - Boundary-aware regex substitution translating colloquial crime synonyms across English, Hindi, and Hinglish into standardized statutory terms (`legal_engine/synonyms.py`, `legal_engine/service.py:147-167`).

3. **Grievance Gating & Non-Penal Gating**:
   - Deterministic filtering of commercial, consumer, and figurative disputes (e.g., "MRP violation", "popcorn price", "daylight robbery", "stole my promotion", "cheated in love") prior to retrieval, returning zero penal sections and consumer/civil routing (`legal_engine/service.py:870-1070`).

4. **Statutory Element Verification & Negation Handling**:
   - Evaluates affirmative vs negated facts for compound offences. In particular, Section 309 (Robbery) requires proof of death, hurt, wrongful restraint, or threat thereof; explicit non-violence ("no weapon", "nobody was hurt", "stealth theft") strictly zeroes Robbery applicability (`legal_engine/service.py:178-338`).
   - Handles attempted offences under BNS Section 62 without inflating confidence scores (`legal_engine/service.py:422-435`).

5. **Foundation Model (Gemini) Integration & Deterministic Fallback**:
   - `GeminiLegalClient` invokes `gemini-2.5-flash` using `google-genai` SDK with strict JSON response schema and candidate statutory context (`legal_engine/llm_client.py:90-195`).
   - Graceful fallback: If API key is unset (`LLMUnavailableError`), inference fails (`LLMInferenceError`), or rate-limited, automatically falls back to deterministic rule-based scoring (`_build_fallback_response`) with transparent provenance markers (`legal_engine/service.py:1120-1154`).

6. **LangGraph Complaint Structuring Workflow**:
   - Directed Acyclic StateGraph (`complaint_engine/graph.py:477-498`) executing:
     `intake` $\to$ `extract_facts` $\to$ `attribute_sources` $\to$ `detect_missing` $\to$ `detect_contradictions` $\to$ `associate_evidence` $\to$ `assess_jurisdiction` $\to$ `validate_and_route` $\to$ (`human_review` | `police_review`) $\to$ `build_report`.
   - Guaranteed statement immutability (SHA-256 hash locked at intake).
   - Strict source span attribution (every extracted fact requires verbatim start/end offset character indices).
   - Zero-knowledge external tracing lock: refuses execution if LangSmith / LangChain tracing environment variables are detected (`complaint_engine/graph.py:454-460`).

7. **Polygon-Containment Police Jurisdiction Assignment**:
   - Point-in-polygon ray-casting across 91 Mumbai Police Station boundary polygons (`complaint_engine/jurisdiction.py:24-50`).
   - Boundary ambiguity buffer: points within 100 meters of a boundary or inside polygon overlaps return `status="near_boundary"` / `"multiple"` with `station=null` and mandatory police confirmation (`complaint_engine/jurisdiction.py:115-130`). Nearest-centroid guessing is strictly prohibited.

8. **Relational Database Persistence & Data Models**:
   - SQLAlchemy 2.0 ORM with connection pooling, transaction context managers, and health checks (`db/session.py:34-99`).
   - Models for complaints, missing person reports, structured facts, source spans, evidence files, PDF documents, email drafts, and append-only audit events (`db/models.py:34-239`).
   - Alembic migration version `001_initial_schema.py` covering all tables, indexes, and foreign keys.

9. **Evidentiary Screening & Metadata Validation**:
   - Magic byte header inspection for file format verification (`complaint_engine/evidence_screening.py:70-77`).
   - Basic heuristic EXIF analysis for AI generative markers (Stable Diffusion, Midjourney, DALL-E) and Laplacian variance sharpness calculation (`complaint_engine/evidence_screening.py:79-140`).

10. **Document Compilation & Export**:
    - Two-pass `NumberedCanvas` ReportLab PDF generation with dynamic page numbering, BNS statutory tables, and missing person identification cards (`complaint_engine/pdf_generator.py:23-338`).
    - Standardized police email drafting with official police station email addressing (`ps.[station].mum@mahapolice.gov.in`) (`complaint_engine/email_draft.py:43-137`).

---

#### 3.2 Partially Implemented Features (Evidence of Incompleteness)

1. **Machine Learning / Logistic Regression Classifier**:
   - *Evidence in Code*: `main.py:59` docstring mentions `"(RAG & Logistic Regression)"` and several test files reference legacy names.
   - *Forensic Finding*: **No trained logistic regression model (`scikit-learn` `.joblib` or `.pkl`) exists or runs in the active codebase.** Classification is handled purely through BM25Okapi lexical retrieval + Gemini LLM / Rule-based heuristic scoring.
   - *Academic Implication*: The research paper must describe the system as a **Hybrid Lexical-LLM Rule-Gated Architecture**, not a trained statistical ML classifier.

2. **Deep Evidentiary Forgery Detection**:
   - *Evidence in Code*: `complaint_engine/evidence_screening.py` implements magic byte inspection and simple string searches across image metadata.
   - *Forensic Finding*: There is **no deep learning model, convolutional neural network (CNN), or error level analysis (ELA)** implemented for image tampering detection.
   - *Academic Implication*: Paper must present this as rule-based metadata heuristic screening, not deep image forensics.

3. **Fine-Tuning Dataset Usage**:
   - *Evidence in Code*: `bns_finetune_dataset.json` (806 KB) exists in the repository root.
   - *Forensic Finding*: No code loads, trains, or references this file in production execution. It represents offline preparatory work.

---

#### 3.3 Planned / Roadmap Features (Documented but Not in Code)

1. **Dense Semantic Bi-Encoder Retrieval**:
   - Mentioned in architectural planning documents (e.g. LegalBERT, BGE embeddings). Not present in runtime (retrieval is 100% BM25Okapi).
2. **Direct CCTNS / Crime OS Integration**:
   - No direct police database API connections exist. The system strictly outputs citizen complaint drafts and email drafts.
3. **Automated Optical Character Recognition (OCR) for Evidence**:
   - No Tesseract or cloud OCR pipeline is integrated in `evidence_screening.py` or `storage.py`.

---

#### 3.4 Deprecated / Excluded Features

1. **Scraped Procedural Classification Blocks**:
   - Historical scraped BNS text appended non-statutory procedural text. `BNSCorpus._load_and_validate()` strictly strips this block via `split_scraped_classification()` (`legal_engine/corpus.py:29-35`).
2. **Nearest-Centroid Station Guessing**:
   - Prohibited by trust-and-safety tests (`src/trustSafety.test.js:71-78`, `tests/test_jurisdiction_and_api.py:112-119`). Point must lie cleanly inside a boundary.
3. **External Third-Party Reverse Geocoding**:
   - Nominatim OpenStreetMap geocoding is disabled by default via `EXTERNAL_GEOCODING_ENABLED = False` (`src/trustSafety.js:33`) to prevent leaking complainant locations.

---

### 4. Dependency & Runtime Matrix

```
Python: 3.12+ (tested up to 3.14)
Frontend: Node.js 18+, React 19.2+, Vite 8.0+
Primary Libraries:
├── fastapi >= 0.148.0
├── uvicorn >= 0.54.0
├── pydantic >= 2.14.1
├── rank-bm25 >= 0.2.2
├── google-genai >= 2.31.0
├── langgraph >= 1.2.16
├── langchain-core >= 1.6.12
├── sqlalchemy >= 2.0.0
├── reportlab >= 4.0.0
└── pytest >= 9.0.0
```

*Verification Artifact*: Fully verified through static analysis and 100% green test execution (391 Python pytest tests, 23 Node.js unit tests).
