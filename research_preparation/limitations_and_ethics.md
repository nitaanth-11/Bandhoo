# Limitations, Ethical Considerations & Reproducibility Protocol

This document provides a rigorous, transparent account of the ethical considerations, operational limitations, privacy protections, and reproducibility requirements governing the Bandhoo (BNS Prediction Engine) research study.

---

## 1. System Role & Ethical Positioning

### 1.1 Decision Support vs. Judicial Adjudication
- **Explicit Role Definition**: Bandhoo is designed and evaluated strictly as an **assistive, citizen-facing decision-support prototype**.
- **No Substitute for Legal Authority**:
  The system is **not** an autonomous legal authority, judicial magistrate, or investigating officer. It does not possess statutory authority to register First Information Reports (FIRs) under Section 173 BNSS, adjudicate guilt or innocence, issue warrants, or alter police records.
- **Human-in-the-Loop Safeguard**:
  Every generated report is explicitly stamped:
  > *"Structured complaint record (draft, not an FIR). Prepared from the complainant's account. Nothing in this record has been verified unless marked as independently verified by an authorised police officer. It has not been submitted to the police."*

---

## 2. Limitations Analysis

### 2.1 Synthetic Benchmark and Lack of Advocate Validation
- **Synthetic Origin**: All 50 BNS cases in `bns_synthetic_benchmark_50.json` and 34 cases in `structuring_cases.json` were authored synthetically by software engineers.
- **Absence of Clinical Legal Audit**: No benchmark cases were evaluated or certified by practicing criminal defense advocates, public prosecutors, or judicial officers.
- **Provisional Ground Truth Discrepancies**: 8 of the 50 cases (16%) contain documented statutory discrepancies (e.g., BM-17 dacoity with only 2 perpetrators; BM-20/21/22 bailability conflicts with Schedule I of BNSS). The system's measured accuracy must be understood as conformance to engineered statutory rules rather than courtroom rulings.

### 2.2 Statutory Transition and Legal Uncertainty
- **Newly Enacted Code**: The Bharatiya Nyaya Sanhita (BNS), 2023 and Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 came into full force on July 1, 2024, replacing the Indian Penal Code, 1860 and Code of Criminal Procedure, 1973. Judicial interpretation of ambiguous provisions (such as the Section 173(3) preliminary enquiry ceiling or Section 303(2) community-service proviso) remains unsettled across Indian High Courts and the Supreme Court.
- **Section 173(3) BNSS Constitutional Tension**: Section 173(3) introduces a preliminary inquiry for offences punishable between 3 and 7 years. Whether this provision compromises mandatory FIR registration established in *Lalita Kumari v. Govt of UP (2014) 2 SCC 1* is subject to active constitutional debate. Bandhoo treats Section 173(3) as an advisory audit flag rather than a binding administrative directive.

### 2.3 Generalization Limits Beyond Mumbai
- **Territorial Scope**: The point-in-polygon spatial registry is currently configured exclusively for the 102 municipal police stations of Greater Mumbai.
- **Cartographic Precision**: The GeoJSON boundary dataset's official survey provenance and date are unverified. While the 100-meter ambiguity buffer prevents border misallocations, rural jurisdictions or jurisdictions lacking digitized GIS polygons cannot currently be serviced.
- **Language Scope**: While the system processes English, Devanagari Hindi, and Hinglish, it has limited vocabulary coverage for Marathi, Gujarati, Tamil, Telugu, and other regional Indian languages.

### 2.4 External API Dependency and Latency
- Live semantic reasoning depends on external cloud LLM inference (Google Gemini 2.5 Flash). Under network latency, rate-limiting, or upstream 503 errors, the system must degrade to local BM25 fallback. While the fallback ensures uninterrupted availability and maintains safety gates, it exhibits lower micro-F1 (28.07% fallback vs 61.54% live LLM).

---

## 3. Privacy, Data Protection & Trust-Safety Invariants

### 3.1 Nonce Hashing and Statement Immutability
- The complainant's narrative is captured verbatim at intake and hashed using SHA-256 (`original_sha256`).
- A custom StateGraph reducer (`keep_original`) prevents subsequent nodes or LLM calls from altering the citizen's original words. Any attempt to modify the original statement triggers an `ImmutableStatementError` that terminates the workflow and logs an alert.

### 3.2 Blocked External Tracing and Telemetry
- To protect citizen privacy in high-stakes legal situations, all external LLM telemetry and tracing frameworks (LangSmith, LangChain Tracing V1/V2) are strictly blocked by `_refuse_external_tracing()` in [complaint_engine/graph.py](file:///c:/Users/nitaa/Downloads/Bandhu/complaint_engine/graph.py#L445-L480).
- If external tracing environment variables are detected active, the workflow refuses execution to prevent private complaint narratives from leaking to third-party logging clouds.

### 3.3 Zero Autonomous Registration
- The application UI contains no fake or pre-generated FIR registration numbers, no fabricated officer credentials, and no automated police station submission webhooks. All submissions require physical verification or explicit user confirmation.

---

## 4. Reproducibility Protocol

To ensure full academic reproducibility of all results reported in the research paper:

### 4.1 Computational Environment
- **Operating System**: Windows 11 / Linux (Ubuntu 22.04 LTS tested)
- **Python Runtime**: Python 3.11.x (tested on 3.11.9)
- **Node.js Runtime**: Node.js v18.x or v20.x

### 4.2 Software Dependencies
- All exact Python dependencies are frozen in `requirements.txt` and `requirements-lock.txt`:
  - `fastapi>=0.110.0`, `uvicorn>=0.28.0`, `pydantic>=2.6.0`
  - `rank_bm25==0.2.2`, `google-genai>=0.1.0`
  - `langgraph>=0.0.30`, `langchain-core>=0.1.30`
  - `sqlalchemy>=2.0.28`, `asyncpg>=0.29.0`, `alembic>=1.13.1`
  - `reportlab>=4.1.0`, `python-magic>=0.4.27`
  - `pytest>=8.1.0`, `pytest-asyncio>=0.23.0`

### 4.3 Deterministic Benchmark Execution Commands
To reproduce the evaluation tables without external API calls:

```bash
# 1. Run Complete Automated Pytest Regression Suite (391 tests)
pytest -q

# 2. Run Metric Identity & Arithmetic Assertion Suite (5 tests)
pytest tests/test_benchmark_metric_identities.py -q

# 3. Run Targeted Algorithm and GIS Tests (46 tests)
pytest tests/test_retrieval_and_quality.py tests/test_jurisdiction_and_api.py tests/test_complaint_graph.py -q

# 4. Run Frontend Trust & Safety TAP Suite (23 tests)
node src/trustSafety.test.js

# 5. Execute 50-Case BNS Classification Benchmark (Deterministic Fallback)
python benchmark/evaluate_benchmark.py --mode fallback

# 6. Execute 34-Case Complaint Structuring Benchmark
python benchmark/structuring/evaluate_structuring.py
```
