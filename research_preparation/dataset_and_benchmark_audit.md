# Dataset and Benchmark Forensic Audit

This document provides a comprehensive, evidence-based audit of all statutory datasets, evaluation benchmarks, and reported metrics in the Bandhoo repository.

---

## 1. Executive Summary of Datasets

| Dataset / Corpus Identifier | File Path | Total Records | Data Origin | Annotation & Provenance | Clinical / Legal Review | Primary Purpose in System |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BNS Statutory Corpus** | `bns_rag_dataset.json` | 358 sections | Gazette of India, BNS 2023 | Statutory text curated with schedule registry cross-referencing | Verified against Ministry of Law statutory text | Inverted index corpus for Okapi BM25 candidate retrieval |
| **BNS Procedural Registry** | `legal_engine/schedule_registry.py` | 358 entries | BNSS 2023 First Schedule Part I | Manually codified legal rules (cognizability, bailability, court) | Audited against official gazetted tables | Deterministic procedural classification and 173(3) eligibility checks |
| **BNS Synthetic Benchmark 50** | `benchmark/bns_synthetic_benchmark_50.json` | 50 cases | Fictional scenarios | Authored to test statutory elements, negations, and multilingual phrasing | **None**. 8 cases marked `provisional_pending_legal_review` | Micro/macro evaluation of BNS legal section prediction and fallback |
| **Structuring Benchmark 34** | `benchmark/structuring/structuring_cases.json` | 34 cases | Fictional scenarios | Clause-level fact annotations across 7 entity categories | Synthetic developer ground truth | Evaluation of LangGraph fact extraction, grounding, and draft compilation |
| **Jurisdiction Benchmark 11** | `benchmark/structuring/structuring_cases.json` | 11 cases | GeoJSON + coordinates | Synthetic polygons and real Mumbai boundary coordinates | Verified against spatial ray-casting invariants | Evaluation of point-in-polygon containment and 100m boundary buffer |

---

## 2. BNS Statutory Corpus & Procedural Registry Audit

### 2.1 Statutory Text Hygiene
- **Source**: `bns_rag_dataset.json` ([legal_engine/corpus.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/corpus.py#L30-L80)).
- **Content**: 358 statutory sections covering Chapters I to XX of the Bharatiya Nyaya Sanhita, 2023.
- **Sanitization Pass (`split_scraped_classification`)**:
  Web-scraped legal corpora frequently include obsolete procedural classifications copied from Indian Penal Code (IPC) / Code of Criminal Procedure (CrPC) legacy tables. Bandhoo implements an explicit sanitization function that discards raw scraped classification strings and instead links every section to an internally audited procedural registry ([legal_engine/schedule_registry.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/schedule_registry.py#L1-L150)).
- **Section 303(2) Petty Theft Proviso**:
  The corpus explicitly flags Section 303(2) theft where value $< ₹5{,}000$ and property is restored as a special conditional entry requiring community service, which affects cognizable and bailable determination.

---

## 3. BNS Synthetic Benchmark 50 Audit

### 3.1 Dataset Demographics and Category Distribution
- **Source File**: [benchmark/bns_synthetic_benchmark_50.json](file:///c:/Users/nitaa/Downloads/Bandhu/benchmark/bns_synthetic_benchmark_50.json).
- **Total Cases**: 50.
- **Language Breakdown**:
  - English: 26 cases (52%)
  - Hindi (Devanagari script): 12 cases (24%)
  - Hinglish (Romanised Hindi): 12 cases (24%)
- **Split Distribution**:
  - Development Set: 35 cases (70%)
  - Held-out Set: 15 cases (30%)
- **Statutory Categories (12 Distinct Legal Scenarios)**:
  1. *Direct Theft* (5 cases): Pocket, automobile, shoplifting, varying values.
  2. *Found Property Converted* (4 cases): BNS Section 314 dishonest misappropriation.
  3. *Snatching* (4 cases): BNS Section 304 sudden/quick/forcible seizure from person.
  4. *Robbery Circumstances* (6 cases): BNS Section 309 via hurt, wrongful restraint, weapons, and instant threats.
  5. *Attempted Offences* (4 cases): BNS Section 62 read with primary offences.
  6. *Explicit Negation* (4 cases): Narratives negating weapons, force, or injury to test contradiction handling.
  7. *Compound Multi-Offences* (4 cases): Composite crimes (theft + house trespass, assault + extortion).
  8. *Ambiguous / Commercial Complaints* (4 cases): Civil transaction disputes testing missing fact identification.
  9. *Missing Material Facts* (4 cases): Unstated property values and unverified criminal histories under Section 303(2).
  10. *Misleading Keyword Traps* (4 cases): Metaphorical phrases ("daylight robbery", "samay loot liya", "snatched credit").
  11. *Paraphrased / Complex Narratives* (4 cases): Formal legalistic prose, Mumbai train colloquialisms.
  12. *Insufficient / Vague Information* (3 cases): Ultra-brief statements testing hallucination suppression.

### 3.2 Provisional Status and Ground-Truth Label Limitations
A critical finding of this audit is that **no case in the benchmark has been evaluated or certified by a practicing criminal advocate, judge, or police officer**.

Furthermore, 8 of the 50 cases (16%) carry the flag `"review_status": "provisional_pending_legal_review"` due to documented statutory discrepancies in the synthetic cases:
- **BNS-BM-17 (Dacoity under BNS 310(1))**: The synthetic scenario states two armed men robbed a bank branch. However, Section 310(1) BNS strictly requires **five or more persons** acting conjointly. With only two actors, the legal classification is Robbery (Section 309), not Dacoity.
- **BNS-BM-20, BNS-BM-21, BNS-BM-22 (Attempted Offences)**: Labelled as `expected_bailable = true`. However, under Section 62 BNSS Schedule I, bailability follows the substantive offence attempted. Since the attempted offences (Sections 303(2), 304(2), 305) are non-bailable, labelling them bailable creates an internal legal contradiction.
- **BNS-BM-28, BNS-BM-30, BNS-BM-31, BNS-BM-45**: Theft occurring inside a dwelling/building where Section 305 BNS should have been co-labelled; BM-31 labels Section 316 (CBT) without an affirmative statement of entrustment.

### 3.3 Metric Definitions and Exact Identities
The evaluation scripts ([benchmark/evaluate_benchmark.py](file:///c:/Users/nitaa/Downloads/Bandhu/benchmark/evaluate_benchmark.py#L40-L120)) and test suite ([tests/test_benchmark_metric_identities.py](file:///c:/Users/nitaa/Downloads/Bandhu/tests/test_benchmark_metric_identities.py#L31-L76)) enforce the following mathematical identities across all partitions:

1. **Prediction Partition**: $\text{Total Predictions} = \text{True Positives} + \text{False Positives}$.
2. **Micro Precision**:
   $$\text{Precision}_{\text{micro}} = \frac{\text{True Positives}}{\text{Total Predictions}}$$
   *(Note: Plausible alternatives count as correct in the numerator, making precision a lenient metric).*
3. **Micro Recall**:
   $$\text{Recall}_{\text{micro}} = \frac{\text{Relevant Sections Retrieved}}{\text{Total Ground Truth Relevant Sections}}$$
   *(Note: Plausible alternatives are excluded from the numerator, making recall a strict metric).*
4. **Unsupported Section Rate**:
   $$\text{Unsupported Rate} = \frac{\text{False Positives}}{\text{Total Predictions}} = 1.0 - \text{Precision}_{\text{micro}}$$
5. **Partition Additivity**:
   $$\text{Overall (50)} = \text{Dev (35)} + \text{Holdout (15)} = \text{English (26)} + \text{Hindi (12)} + \text{Hinglish (12)}$$
   $$\text{Overall (50)} = \text{Excluding Provisional (42)} + \text{Provisional Only (8)}$$

---

## 4. Complaint-Structuring Benchmark 34 Audit

### 4.1 Dataset Structure and Gold Fact Breakdown
- **Source File**: [benchmark/structuring/structuring_cases.json](file:///c:/Users/nitaa/Downloads/Bandhu/benchmark/structuring/structuring_cases.json).
- **Cases**: Exactly 34 cases (20 Development cases + 14 Heldout cases).
- **Gold Fact Inventory (220 Total Annotated Facts)**:
  - `datetime`: 52 gold facts (31 Dev, 21 Heldout)
  - `action`: 50 gold facts (29 Dev, 21 Heldout)
  - `people`: 40 gold facts (23 Dev, 17 Heldout)
  - `loss`: 33 gold facts (20 Dev, 13 Heldout)
  - `location`: 25 gold facts (15 Dev, 10 Heldout)
  - `witness`: 12 gold facts (6 Dev, 6 Heldout)
  - `evidence`: 8 gold facts (7 Dev, 1 Heldout)

### 4.2 Verified Structuring Performance (Baseline vs. Updated System)
A direct audit of [benchmark/structuring/results_baseline.json](file:///c:/Users/nitaa/Downloads/Bandhu/benchmark/structuring/results_baseline.json) versus [benchmark/structuring/results_after.json](file:///c:/Users/nitaa/Downloads/Bandhu/benchmark/structuring/results_after.json) yields the exact performance deltas:

| Metric Category | Baseline Value | Updated System Value | Absolute Delta | Relative Improvement | Evaluation Split |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Heldout Fact Extraction Recall** | **51.69%** (46 / 89) | **85.39%** (76 / 89) | **+33.70 pp** | **+65.20%** | Heldout (14 cases) |
| **Heldout Fact Extraction Precision** | **100.0%** (47 / 47) | **98.72%** (77 / 78) | **-1.28 pp** | -1.28% | Heldout (14 cases) |
| **Heldout Unsupported Fact Rate** | **0.00%** (0 / 47) | **2.56%** (2 / 78) | **+2.56 pp** | N/A (1 unsupp + 1 over) | Heldout (14 cases) |
| **Heldout Draft Integrity Checks** | **0.0%** (0 / 14) | **100.0%** (14 / 14) | **+100.0 pp** | Complete pass | Heldout (14 cases) |
| **All-Cases Fact Recall** | **58.18%** (128 / 220) | **94.09%** (207 / 220) | **+35.91 pp** | **+61.72%** | All (34 cases) |
| **All-Cases Fact Precision** | **100.0%** (129 / 129) | **98.17%** (215 / 219) | **-1.83 pp** | -1.83% | All (34 cases) |
| **All-Cases Unsupported Fact Rate** | **0.00%** (0 / 129) | **2.28%** (5 / 219) | **+2.28 pp** | 4 unsupp + 1 over | All (34 cases) |
| **All-Cases Draft Checks** | **0.0%** (0 / 34) | **100.0%** (34 / 34) | **+100.0 pp** | Complete pass | All (34 cases) |

#### Analysis of the Improvement
In the baseline system, action clauses and property loss verbs were largely unextracted because deterministic regexes were limited to simple nouns. The baseline had 0% draft integrity pass because drafts lacked proper procedural disclaimers. The updated system added multi-action verb extraction and exact character span grounding, lifting heldout recall from 51.69% to 85.39% (+33.70 percentage points) while maintaining a precision of 98.72% and passing 14/14 draft checks.

---

## 5. Jurisdiction Benchmark 11 Audit

- **Cases**: Exactly 11 cases (`J01`–`J11`) in [benchmark/structuring/structuring_cases.json](file:///c:/Users/nitaa/Downloads/Bandhu/benchmark/structuring/structuring_cases.json#L850-L950).
- **Coverage**:
  - Inside unambiguous polygon: 4 cases (assigned to correct station).
  - Outside all station boundaries: 2 cases (correctly returned `status: "outside_all", station: null`).
  - Near boundary ($\le 100\text{ m}$ to edge): 3 cases (correctly returned `status: "near_boundary", station: null`).
  - Missing / non-finite coordinates: 2 cases (correctly returned `status: "no_location", station: null`).
- **Verified Benchmark Result**: **11/11 correct (100%)**, with **0 unsafe jurisdictional assignments**.

---

## 6. Audit of Test Suite Counts and Metric Claims

The user request and historical reports cite three distinct test counts:
1. `"228 original tests"`
2. `"346 offline tests"`
3. `"391 Python unit tests / 414 total tests"`
4. `"23 frontend tests"`

### Reconstructed Forensic Chronology
- **Phase A (Baseline Legal Engine)**: Contained **228 tests** covering statutory corpus loading, BM25 retrieval, schedule registry mapping, and currency extraction (`reports/baseline_and_rollback_audit.md`).
- **Phase B (LangGraph Structuring Pipeline)**: Added 118 tests covering StateGraph nodes, exact span validation, contradiction checks, and jurisdiction containment, bringing the Python suite to **346 tests** (`reports/trust_safety_langgraph_change_record.md`).
- **Phase C (Current Verified Repository State)**: Added tests for async PostgreSQL persistence, bilingual ReportLab PDF compilation, official email routing, and missing persons intake, bringing the active suite to:
  - **391 Python unit & integration tests** in `pytest` (21 test files).
  - **23 Frontend trust and safety tests** in Node.js (`src/trustSafety.test.js`).
  - **Total: 414 automated tests**, all passing with 0 failures.

> [!CAUTION]
> **Academic Integrity Warning**:
> Test counts (e.g., 391 Python tests, 23 JS tests) measure **codebase regression coverage and software verification**. They must **never** be cited as an evaluation accuracy metric or confused with benchmark case counts.

---

## 7. Potential Leakage, Annotation Bias, and Threats to Validity

1. **Synthetic Data Contamination**:
   All 50 BNS cases and 34 structuring cases were synthetically authored by the engineering team. Fictional complaints often feature more coherent grammatical structure than real-world emergency calls or handwritten citizen complaints.
2. **"Previously Inspected" Holdout Contamination**:
   The 15 heldout BNS cases and 14 heldout structuring cases are technically "previously inspected" regression suites used during development iterations, rather than a pristine, never-before-seen blind test split.
3. **Lexical Vocabulary Overlap**:
   The synonym translation table (`legal_engine/synonyms.py`) was expanded using patterns observed during benchmark development, creating a degree of lexical feature leakage.
4. **Lack of Judicial Ground Truth**:
   Because ground truth labels were not established by judicial officers or public prosecutors, the benchmark measures **conformance to engineered statutory rules**, not real-world judicial rulings.
