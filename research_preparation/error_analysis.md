# Error Analysis & Failure Modes: BNS Legal & Structuring Engine

This document provides a rigorous, code-grounded error taxonomy based on benchmark failures, statutory edge cases, and architectural boundary conditions in the Bandhoo repository.

---

## 1. Error Taxonomy & Empirical Breakdown

Across the 50-case BNS classification benchmark and the 34-case complaint-structuring benchmark, observed errors fall into five primary failure categories:

```
Total Errors & Edge Cases
├── Category 1: Statutory Proviso and Unstated Material Quantums (e.g., Section 303(2))
├── Category 2: Non-Penal Gating Ambiguity & Mixed Civil-Criminal Phrasing
├── Category 3: Syntactic Inversion & Passive Voice Extraction Omissions
├── Category 4: Multi-Offender Statutory Threshold Incongruence (Dacoity vs Robbery)
└── Category 5: Territorial Boundary Ambiguity in Near-Border Jurisdictions
```

---

## 2. In-Depth Error Case Studies

### 2.1 Category 1: Statutory Proviso and Unstated Material Quantums
- **Observed Cases**: BNS-BM-01, BNS-BM-02, BNS-BM-03 (Direct Theft).
- **Observed Behavior**:
  The system outputs candidate Section 303 (Theft) with a valid prediction score, but returns:
  `"is_cognizable": null`, `"is_bailable": null`, and generates a qualified procedural advisory:
  > *"Procedural course under the BNSS, 2023 is conditional on unverified material facts (property value, property restoration, and prior conviction record). The value of the taken property is not stated."*
- **Root Cause in Code**:
  In [legal_engine/service.py:409-418](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/service.py#L409-L418) and `assess_stolen_property_value(raw_narrative)`:
  BNSS Schedule I Part I creates a bifurcated procedural track for theft under BNS Section 303(2):
  1. If stolen property value $< ₹5{,}000$, property is returned, and it is a first-time conviction $\implies$ **Non-Cognizable, Bailable** (triable with community service).
  2. Otherwise $\implies$ **Cognizable, Non-Bailable** (imprisonment up to 3 years).
  When citizens omit the estimated monetary value of stolen property, neither the statutory proviso nor the main pathway can be definitively chosen.
- **Academic Assessment**:
  This is a **principled design safety feature**, not a system failure. Attempting to assign definitive cognizable status to an unvalued theft complaint would violate statutory rules.
- **Proposed Mitigation**:
  Implement dynamic conversational slot-filling in the frontend intake form: when theft or stolen property is detected without a currency amount, prompt the user specifically: *"What is the estimated value of the stolen item(s)?"*

---

### 2.2 Category 2: Non-Penal Gating Ambiguity & Mixed Civil-Criminal Phrasing
- **Observed Case**: BNS-BM-48 (`gate_false_negatives = 1`).
- **Narrative Pattern**:
  > *"The painting contractor cheated us on paint quality and overcharged the final bill by ₹20,000 compared to his written estimate. We feel completely robbed and want him arrested."*
- **Observed Behavior**:
  The grievance gate passed the complaint through to the penal classification engine instead of gating it out as a commercial pricing dispute. The system predicted BNS Section 318 (Cheating).
- **Root Cause in Code**:
  In [legal_engine/service.py:956-972](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/service.py#L956-L972):
  The non-penal grievance filter enforces a safety invariant: if affirmative financial, digital, or property crime keywords appear, the complaint is **never gated out**. The word `"cheated"` matched `affirmative_financial_digital` (`\b(?:cheated|cheating|fraud)\b`), preventing the commercial pricing filter from triggering.
- **Trade-off Analysis**:
  This false negative represents a deliberate conservative bias: **it is legally safer to let a civil breach of contract dispute pass to officer review than to accidentally suppress a genuine criminal cheating incident (BNS Section 318)**.
- **Proposed Mitigation**:
  Implement syntactic dependency analysis to verify whether `"cheated"` applies to tangible goods/inducement versus subjective quality disputes regarding services rendered.

---

### 2.3 Category 3: Syntactic Inversion & Passive Voice Extraction Omissions
- **Observed Cases**: Structuring Heldout Cases H04 and H13.
- **Observed Behavior**:
  In case H04, the action of forcing open a padlock was missed by regex extractors (`missed: H04:identity`, `missed: H13:number_of_persons`).
- **Narrative Pattern**:
  > *"On returning home, the front padlock was found smashed and the wooden door forced open."*
- **Root Cause in Code**:
  In [complaint_engine/extraction.py:124-135](file:///c:/Users/nitaa/Downloads/Bandhu/complaint_engine/extraction.py#L124-L135):
  The regex `ACTION_PATTERNS` relies predominantly on active verb constructions (e.g., `"broke into"`, `"smashed"`, `"took"`) and excludes the complainant's own actions via negative lookbehinds `(?<!\bI )(?<!\bwe )`. Passive agentless constructions (`"was found smashed"`, `"was forced open"`) do not follow the canonical `[Subject] [Action] [Object]` order, causing deterministic token extractors to miss the predicate.
- **Impact on Metrics**:
  Reduced heldout action extraction recall to $80.95\%$ (17/21 actions recovered) in the baseline, improved to $92.00\%$ overall when grounded optional LLM extraction was introduced.
- **Proposed Mitigation**:
  Incorporate lightweight dependency parsing (e.g., spaCy passive auxiliary patterns `auxpass` + `VERB`) into the deterministic extractor pipeline.

---

### 2.4 Category 4: Multi-Offender Statutory Threshold Incongruence (Dacoity vs Robbery)
- **Observed Case**: BNS-BM-17.
- **Narrative Pattern**:
  > *"Two armed men on a motorcycle entered the jewelry shop with drawn revolvers, threatened to shoot the owner, and fled with gold trays."*
- **Ground Truth vs System Output**:
  - Synthetic Ground Truth Label: Section 310 (Dacoity).
  - System Prediction: Section 309 (Robbery).
- **Statutory Analysis**:
  Under Section 310(1) BNS (and legacy Section 391 IPC):
  > *"When five or more persons conjointly commit or attempt to commit a robbery... every person so committing, attempting or aiding is said to commit dacoity."*
  Because the scenario explicitly specifies only **two actors**, the offence is statutorily Robbery under Section 309, **not Dacoity under Section 310**. The system correctly predicted Section 309, but was scored as a "miss" against the flawed synthetic benchmark label.
- **Academic Assessment**:
  Demonstrates benchmark ground-truth fragility in synthetic datasets. Confirms the necessity of the `provisional_pending_legal_review` partition.

---

### 2.5 Category 5: Territorial Boundary Ambiguity in Near-Border Jurisdictions
- **Observed Cases**: Jurisdiction Benchmark J03, J04, J09.
- **Observed Behavior**:
  When an incident coordinate is placed $45.2\text{ m}$ from the polygon boundary between two municipal police stations, the system returns:
  `"status": "near_boundary"`, `"station": null`, `"distance_to_boundary_m": 45.2`.
- **User Experience vs Legal Safety Conflict**:
  From an end-user UX perspective, a user expects a named police station. Returning `station: null` may appear as a system failure.
- **Legal Justification**:
  Under Indian criminal procedure, registering an FIR in the wrong territorial jurisdiction creates procedural jurisdictional friction (necessitating transfer as a "Zero FIR" under Section 173(1) BNSS). Near boundary lines, GPS consumer device inaccuracy ($\pm 15\text{ m}$) combined with unverified GeoJSON cartographic surveys creates a severe risk of misallocation.
- **Engineering Rule**:
  The system strictly refuses to guess centroids or nearest stations within the 100-meter safety zone, mandating manual verification by desk officers.

---

## 3. Systematic Summary Table of Failure Modes

| Failure ID | Failure Mode Description | Trigger Condition | System Behavior | Impact on Paper / System | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FM-1** | Missing property valuation | Citizen does not state ₹ quantum | Cognizable/Bailable status set to `None` | Prevents erroneous FIR registration | Dynamic UI prompt for estimated value |
| **FM-2** | Passive syntactic inversion | Narrative uses passive constructions | Deterministic regex misses action item | Drops recall in offline fallback mode | Lightweight dependency parse extractors |
| **FM-3** | Mixed civil-criminal grievance | Commercial dispute mentions "cheated" | Pass-through to penal prediction | Slight decrease in gate specificity | Clause-level intent classification |
| **FM-4** | Near-boundary coordinate ambiguity | Incident is $\le 100\text{ m}$ from polygon edge | Returns `station: null`, flags review | User must confirm station manually | Geodesic buffer + Zero FIR guidance |
| **FM-5** | Synthetic label discrepancies | Benchmark label conflicts with BNS text | System prediction marked false positive | Understates true clinical accuracy | Independent advocate audit of benchmark |
