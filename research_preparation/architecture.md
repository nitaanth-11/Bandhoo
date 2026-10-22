# Bandhoo System Architecture Specification
## Phase 2 — End-to-End Architectural Reconstruction & Technical Blueprint

**Date**: October 2026  
**Auditor**: Senior Software Architect & Research Systems Engineer  
**Component**: End-to-End System Architecture  
**Execution Milestone**: Checkpoint R1 (Repository Forensics & Architecture Reconstruction)  

---

### 1. Architectural Philosophy & Design Constraints

Bandhoo is designed as an **augmented citizen-assistance and legal-decision-support system** for reporting incidents under the **Bharatiya Nyaya Sanhita (BNS), 2023** and procedural compliance under the **Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023**.

The architecture adheres to four foundational engineering and trust invariants:
1. **Zero-Hallucination & Provenance Guarantee**: The system never generates ungrounded statutory citations or attributes unstated facts. Every extracted detail is anchored to verbatim character offsets (`SourceSpan`).
2. **Draft-Only Non-Registration Boundary**: Bandhoo explicitly prohibits claiming the generation of official First Information Reports (FIRs), electronic signatures, or direct police filing. It outputs draft instruments requiring in-person or official verification.
3. **Deterministic Procedural Safeguards**: High-stakes procedural determinations (cognizability, bailability, jurisdictional ambiguity, Section 173(3) BNSS preliminary inquiry eligibility) are governed by verified statutory tables and mathematical containment, never free-form LLM generation.
4. **Resilient Offline Fallback**: The entire pipeline functions in a zero-network, local offline environment without foundation model dependencies, using BM25Okapi lexical retrieval and rule-based heuristic classifiers.

---

### 2. Multi-Tier End-to-End Architecture Decomposition

```
[ Citizen User / Client (React 19 / Leaflet GIS) ]
                         │
                         ▼ HTTPS (JSON Payloads)
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI REST API Server                         │
│                               (main.py)                                │
└───────┬───────────────────┬───────────────────┬──────────────────┬─────┘
        │                   │                   │                  │
        ▼                   ▼                   ▼                  ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐
│   Tier 1:    │    │   Tier 2:    │    │   Tier 3:    │    │  Tier 4:   │
│  Geographic  │    │  Statutory   │    │  LangGraph   │    │ Document & │
│ Jurisdiction │    │ Legal Engine │    │  Complaint   │    │ Relational │
│ (Polygon     │    │ (Retrieval,  │    │ Structuring  │    │ Persist.   │
│ Containment) │    │ LLM & Rules) │    │  (StateFlow) │    │ (SQLAlchemy│
└──────────────┘    └──────────────┘    └──────────────┘    └────────────┘
```

---

### 3. Deep Component Specifications

#### Component 1: Geographic Jurisdiction Engine (`complaint_engine/jurisdiction.py`)
- **Purpose**: Establishes whether an incident's geographic coordinates fall unequivocally within a designated Mumbai Police Station administrative area.
- **Input Schema**:
  ```python
  latitude: float  # WGS84 decimal degrees
  longitude: float # WGS84 decimal degrees
  path: Optional[str] # Path to GeoJSON boundary file
  ```
- **Output Schema**:
  ```python
  JurisdictionAssessment(
      status: str,              # "inside" | "near_boundary" | "outside_all" | "multiple" | "no_location" | "data_unavailable"
      station: Optional[str],   # Station name if unequivocally confirmed, else None
      distance_to_boundary_m: Optional[float], # Distance to closest edge in meters
      method: str,              # "polygon_containment"
      message: str,             # Standardized citizen notice
      boundary_data: dict       # Provenance metadata
  )
  ```
- **Algorithms & Decision Rules**:
  - **Ray-Casting Algorithm (`_point_in_ring`)**: Tests ray intersections along the positive X-axis. Supports exterior rings and excludes interior holes (`point_in_geometry`).
  - **100-Meter Safety Buffer (`distance_to_boundary_m`)**: Projects spherical coordinate differences to metric distances ($1^\circ \text{ lat} \approx 111,000\text{ m}$, $1^\circ \text{ lon} \approx 111,000 \cdot \cos(\text{lat})\text{ m}$). If minimum distance to any polygon segment is $\le 100\text{ m}$, status is forced to `"near_boundary"`, zeroing station assignment.
  - **Ambiguity & Overlap Guard**: If coordinates fall into $> 1$ polygon, status is forced to `"multiple"`, station is set to `None`, and the citizen is prompted for police confirmation. Nearest-centroid guessing is strictly prohibited.
- **Test Coverage**: `tests/test_jurisdiction_and_api.py:37-98` (12 test cases).

---

#### Component 2: Lexical Statutory Retrieval Engine (`legal_engine/retrieval.py`)
- **Purpose**: Retrieves candidate sections from Bharatiya Nyaya Sanhita, 2023 for a narrative.
- **Input Schema**:
  ```python
  query: str                    # Standardized incident narrative
  top_k: int = 10               # Maximum candidates requested
  min_raw_score: float = 0.0    # Absolute BM25 floor
  relative_threshold: float = 0.35 # Pruning ratio relative to top candidate
  ```
- **Output Schema**:
  ```python
  List[Tuple[int, float]]       # List of (section_number, normalized_relevance_score)
  ```
- **Algorithms & Decision Rules**:
  - **Alphanumeric Tokenizer (`tokenize_legal_text`)**: Regex tokenization `\b[a-zA-Z0-9_\-]{2,}\b`, lowercased.
  - **BM25Okapi**: Evaluated over 358 verified BNS sections using document string $D = \text{Title} + \text{Keywords} + \text{Statutory Text} + \text{Scraped Legacy Block}$.
  - **Dynamic Relative Pruning**: Given top raw score $S_{\max}$, prunes candidate $i$ if $\frac{S_i}{S_{\max}} < 0.35$. Prevents tail hallucination and irrelevant candidate padding.
  - **Clause-Level Segmentation (`retrieve_clause_level`)**: Splits compound narratives across sentence delimiters and conjunctions (`and then`, `aur phir`, `after that`, `lekin`), evaluates BM25 over individual clauses, and takes $\max(S_{\text{global}}, S_{\text{clause}})$ per section, preventing single-offence dominance in compound crimes.
- **Test Coverage**: `tests/test_retrieval_and_quality.py:1-60`.

---

#### Component 3: Legal Safeguards, Grievance Gating & Contradiction Engine (`legal_engine/service.py`)
- **Purpose**: Intercepts non-penal disputes, resolves explicit negations, and verifies alternative statutory ingredients.
- **Input Schema**: `NarrativeInput(narrative: str)`
- **Output Schema**: `OffenceClassificationResponse`
- **Algorithms & Decision Rules**:
  - **Grievance Gate (`_detect_non_penal_grievance`)**: Regex screening for commercial/pricing disputes, employee performance reviews, and metaphorical language. Bypasses penal retrieval and outputs civil guidance.
  - **Negation Resolver (`detect_negations`)**: Scans for English, Hindi, and Hinglish negations of violence, weapons, injury, or force.
  - **Element Contradiction Verification (`_validate_candidate_elements`)**:
    - *Robbery (BNS Section 309)*: Evaluates the 4 statutory alternatives (death, hurt, wrongful restraint, or threat of instant harm). If theft is non-confrontational or violence is negated, sets applicability score $= 0.0$ and logs an explicit contradiction note.
    - *Theft (BNS Section 303)*: Evaluates property value against the Section 303(2) proviso threshold ($\text{Rs } 5,000$).
  - **Procedural Law Audit (`_audit_173_3_claims`)**: Maps candidate sections to the verified BNSS Schedule I registry (`schedule_registry.py`). Checks Section 173(3) BNSS eligibility (offences punishable with 3–7 years) and attaches mandatory caveats regarding *Lalita Kumari v. Govt of UP* and ongoing constitutional petitions.
- **Test Coverage**: `tests/test_adversarial_grievance_audit.py`, `tests/test_procedural_law_audit.py`, `tests/test_legal_accuracy_audit.py`.

---

#### Component 4: Foundation Model Integration & Fallback Router (`legal_engine/llm_client.py` & `service.py`)
- **Purpose**: Generates grounded legal reasoning when online, routing to deterministic fallback when offline or errored.
- **Input Context**: Verbatim complainant narrative + Top-8 retrieved statutory texts formatted via `corpus.format_for_llm_context()`.
- **Output Schema**: JSON conforming to `OffenceClassificationResponse`.
- **Failure Conditions & Fallback Behavior**:
  1. `GEMINI_API_KEY` missing/blank $\to$ Routes to `_build_fallback_response()` with `inference_status = "fallback_llm_unavailable"`.
  2. Network timeout / 503 HTTP / quota exhaustion $\to$ Bounded exponential retry (3 attempts) $\to$ `_build_fallback_response()` with `inference_status = "fallback_llm_failed"`.
  3. No retrieval candidates meet BM25 floor $\to$ `inference_status = "fallback_llm_not_invoked"`.
  - In fallback mode: Normalized BM25 relevance scores are surfaced directly, statutory schedule classification is looked up deterministically, and candidate sections are qualified as machine-suggested.
- **Test Coverage**: `tests/test_gemini_pipeline.py:1-150`, `tests/test_reliability_followups.py:1-80`.

---

#### Component 5: LangGraph Complaint Structuring Engine (`complaint_engine/graph.py`)
- **Purpose**: Transforms unstructured incident narratives into an auditable, verifiable complaint record.
- **State Schema (`ComplaintState`)**:
  ```python
  statements: List[Statement]               # Immutably locked with SHA-256
  facts: List[FactItem]                     # Extracted facts with SourceSpan
  rejected_items: List[RejectedItem]         # Filtered items
  missing_info: List[MissingInfo]           # Unstated essential facts
  contradictions: List[Contradiction]       # Internal fact conflicts
  evidence: List[EvidenceItem]              # Attached supporting items
  jurisdiction: JurisdictionAssessment      # Containment assessment
  review: ReviewDecision                    # "ready_for_police_review" | "human_review_required"
  errors: List[NodeError]                   # Pipeline errors
  ```
- **Directed Graph Flow**:
  1. `intake`: Freezes raw statements, checks length ($10 \le \text{len} \le 8000$), generates statement UUIDs and SHA-256 hashes.
  2. `extract_facts`: Invokes deterministic rule-based extractor for 7 categories (`people`, `datetime`, `location`, `action`, `loss`, `witness`, `evidence`).
  3. `attribute_sources`: Validates that every extracted fact's span matches the original text verbatim ($text[start:end] == span$).
  4. `detect_missing`: Evaluates checklist of mandatory complaint fields (what, when, where, who, loss value, evidence, witnesses).
  5. `detect_contradictions`: Identifies temporal, spatial, or numerical conflicts between statements.
  6. `associate_evidence`: Connects evidentiary metadata to facts.
  7. `assess_jurisdiction`: Executes point-in-polygon containment.
  8. `validate_and_route`: Terminal router. If errors exist or missing information is flagged, routes to `human_review`; only routes to `police_review` if 100% validated.
  9. `build_report`: Serializes structured JSON report.
- **Zero-Knowledge Privacy Lock**: Detects environment variables `LANGSMITH_TRACING` or `LANGCHAIN_TRACING_V2`. If set without `BANDHOO_ALLOW_EXTERNAL_TRACING=1`, raises `ExternalTracingRefused` and halts execution (`complaint_engine/graph.py:454-460`).
- **Test Coverage**: `tests/test_complaint_graph.py:1-250`, `tests/test_structuring_quality.py:1-304`.

---

#### Component 6: Relational Database Persistence & Data Models (`db/`)
- **Purpose**: Provides atomic, relational persistence for citizen complaints, revisions, missing person dossiers, and append-only audit events.
- **Architecture**:
  - `SQLAlchemy 2.0` ORM connected to SQLite (`bandhoo_persistence.db`) or PostgreSQL (`DATABASE_URL`).
  - Connection pooling: `pool_size = 10`, `max_overflow = 20`, `pool_timeout = 30s`, `pool_recycle = 1800s`, `pool_pre_ping = True`.
  - Transaction management via `session_scope()` context manager with automatic rollback on error.
- **Entity Relationship Model**:
  - `complaints`: Primary entity storing raw narration, SHA-256 hash, jurisdiction station, and compiled record.
  - `missing_person_reports`: Linked $1:1$ to `complaints`. Stores name, age, physical traits, birthmarks, and urgency level.
  - `structured_facts`: Linked $1:N$ to `complaints`. Stores fact categories, values, and polarity.
  - `source_spans`: Linked $1:N$ to `structured_facts`. Stores exact character start/end offsets.
  - `evidence_files`: Linked $1:N$ to `complaints`. Stores filenames, SHA-256 hashes, and private storage keys.
  - `generated_documents`: Linked $1:N$ to `complaints`. Stores generated PDF metadata and document hashes.
  - `email_drafts`: Linked $1:N$ to `complaints`. Stores recipient police station email, subject, body, and approval status.
  - `audit_events`: Append-only audit log tracking every revision, status transition, and compilation event.
- **Test Coverage**: `tests/test_database_persistence.py:1-120`.

---

#### Component 7: Document Compilation, PDF & Email Routing (`complaint_engine/`)
- **Purpose**: Generates high-fidelity legal PDF drafts and official police nodal email communications.
- **PDF Generation Engine (`complaint_engine/pdf_generator.py`)**:
  - Built with ReportLab using a custom `NumberedCanvas` that dynamically computes total pages ("Page X of Y").
  - Formats 12 distinct complaint sections, including official BNS statutory tables detailing Cognizable/Bailable classification, prescribed punishment, grounded reasoning, and supported elements.
  - Formats dedicated Missing Person physical profiles, including photo preview placeholders and birthmark registries.
- **Email Preparation Engine (`complaint_engine/email_draft.py`)**:
  - Generates standardized communication templates addressed to official police stations (`ps.[station].mum@mahapolice.gov.in`).
  - Cites statutory mandates (*Bachpan Bachao Andolan v. Union of India* for zero-waiting-period missing person complaints).
  - Enforces mandatory user confirmation prior to clipboard copying or transmission; strictly avoids direct automatic emailing (`mailto:` prohibited in web UI).
- **Test Coverage**: `tests/test_pdf_and_email.py:1-115`.

---

### 4. Component Interaction & Data Flow Sequence

```
Citizen Input (Web App / API)
       │
       ▼
1. Input Normalization & Gating
   ├─► translate_synonyms()
   └─► _detect_non_penal_grievance() ──[Non-Penal]──► Non-Penal Advisory Response
       │ [Penal Query]
       ▼
2. Statutory Retrieval & Ranking
   ├─► tokenize_legal_text()
   ├─► retrieve_clause_level() (BM25Okapi)
   └─► Relative threshold pruning (0.35)
       │
       ▼
3. Element Verification & Negation Resolution
   ├─► detect_negations()
   └─► _validate_candidate_elements() (Checks Sec 309/303/304 elements)
       │
       ▼
4. Inference Router
   ├─► LLM Available? ──[Yes]──► Gemini 2.5 Flash ──► _build_llm_response()
   └────────────────────[No]───► Rule-Based BM25  ──► _build_fallback_response()
       │
       ▼
5. LangGraph Complaint Structuring
   ├─► intake (SHA-256 Lock)
   ├─► extract_facts() & attribute_sources() (Verbatim Spans)
   ├─► detect_missing() & detect_contradictions()
   ├─► assess_point() (Polygon Containment & 100m Boundary Buffer)
   └─► validate_and_route() ──► ReviewDecision ("ready" | "human_review")
       │
       ▼
6. Compilation & Persistence (SQLAlchemy 2.0)
   ├─► compile_complaint_record()
   ├─► Save to DB (complaints, facts, missing_persons, audit_events)
   ├─► generate_complaint_pdf() (ReportLab Two-Pass NumberedCanvas)
   └─► prepare_complaint_email_draft() (ps.[station].mum@mahapolice.gov.in)
```
