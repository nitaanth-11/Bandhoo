# Research Paper Outline & Publication Plan

**Working Title**:  
*Bandhoo: A Hybrid Lexical-Semantic Legal Decision Support Engine for Incident Structuring and Statutory Retrieval under the Bharatiya Nyaya Sanhita*

**Target Venues**:  
- *Artificial Intelligence and Law (Springer)*
- *ACM Conference on Computer Science and Law (CS&Law)*
- *ACM Conference on Fairness, Accountability, and Transparency (FAccT)*
- *EACL / EMNLP LegalNLP Workshop*

---

## Abstract
The recent enactment of the Bharatiya Nyaya Sanhita (BNS), 2023, and the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023, has introduced substantial structural reforms to criminal jurisprudence in India, creating acute operational challenges for citizens and front-desk police personnel navigating new statutory provisions. While Large Language Models (LLMs) offer promising natural language interfaces for legal assistance, unconstrained generative architectures are susceptible to severe factual hallucinations, legal misclassifications under explicit factual negations, and fabricated procedural numbers. 

In this paper, we present **Bandhoo**, a hybrid, transparent legal decision-support system designed to structure unstructured citizen incident narrations, retrieve applicable BNS statutory sections, assign territorial police jurisdictions, and generate audit-grounded legal complaint drafts. Bandhoo addresses core vulnerabilities of standard legal RAG pipelines through three foundational mechanisms: (1) **decoupled scoring with contradiction overrides**, ensuring that lexical BM25 similarity cannot inflate prediction scores when narrative facts explicitly negate essential statutory elements; (2) **clause-level multi-action narrative segmentation with max-pooling**, preventing primary offences from drowning out secondary penal charges in compound complaints; and (3) **exact-span grounded fact extraction within a LangGraph StateGraph**, enforcing character-level substring identity between extracted facts and the citizen's original statement. Territorial police jurisdiction is assigned via point-in-polygon ray-casting equipped with a 100-meter equirectangular boundary buffer that strictly refrains from guessing station assignments in ambiguous border zones. 

Evaluated across a 50-case multilingual statutory benchmark (English, Hindi, and Hinglish) and a 34-case complaint-structuring benchmark, Bandhoo achieves an 85.39% heldout fact extraction recall (+33.70 percentage point gain over baseline) while sustaining a 98.72% precision, a 2.56% unsupported fact rate, 0.00% false positives on contradicted statutory provisions, and 100% draft integrity pass across all cases. A transparent, offline deterministic fallback engine guarantees resilience during cloud outages. Bandhoo is explicitly framed as an assistive decision-support prototype rather than an autonomous judicial authority, establishing a rigorous engineering paradigm for responsible AI in public legal administration.

**Keywords**: Legal Information Retrieval, Bharatiya Nyaya Sanhita (BNS), Trustworthy NLP, Statutory Charge Prediction, LangGraph, Exact-Span Fact Extraction, Point-in-Polygon Jurisdiction, Public Service Decision Support.

---

## 1. Introduction (IMRAD: Introduction)
- **1.1 Background & Context**: The statutory transition from IPC 1860 / CrPC 1973 to BNS 2023 / BNSS 2023 in India; practical difficulties faced by citizens articulating grievances and front-desk police scribes compiling First Information Reports (FIRs).
- **1.2 The High-Stakes Failure Modes of Generic Legal AI**:
  - Keyword inflation in RAG: BM25 matching taking/violence keywords in complaints explicitly stating "no weapons used, no one hurt", falsely alleging Robbery (BNS Section 309).
  - Generative hallucinations in complaint drafting: LLMs inventing suspect names, weapon types, or officer credentials.
  - Jurisdictional misallocation: Naive centroid-based GIS lookups routing complaints to wrong stations, triggering procedural friction and Zero FIR transfers under Section 173(1) BNSS.
- **1.3 Architectural Overview of Bandhoo**: A hybrid lexical-rule-LLM engine with deterministic safety gates, exact-span extraction, and offline fallback.
- **1.4 Summary of Research Contributions**:
  1. Decoupled scoring eliminating contradiction false positives (0.00% FP on negated charges).
  2. Multi-action clause segmentation with max-pooling for composite complaints.
  3. Exact-span fact grounding reducing unsupported assertions to 2.56%.
  4. 100-meter buffered geographic point-in-polygon territorial allocation.
  5. Transparent offline deterministic fallback preserving availability.

---

## 2. Related Work
- **2.1 Legal Information Retrieval & Statutory Question Answering**: Lexical vs dense retrieval in statutory corpora (Okapi BM25, COLIEE, ILDC).
- **2.2 Fact Extraction and Legal Structuring**: Extractive vs abstractive summarization in legal NLP, event extraction, temporal anchoring.
- **2.3 Trustworthy & Responsible AI in Criminal Justice**: Hallucination suppression, decision deferral, human-in-the-loop gates (*Lalita Kumari v. Govt of UP* guidelines).
- **2.4 Geographic Information Systems in Policing**: Jordan curve ray-casting, boundary uncertainty buffers, police station jurisdiction mapping.

---

## 3. Problem Formulation & Mathematical Foundations
- **3.1 Mathematical Nomenclature & Symbols**: Formal definition of statutory corpus $\mathcal{C}$ ($N=358$), query $q$, narrative $x$, and scores.
- **3.2 Statutory Retrieval as Dynamic Relative-Threshold Ranking**:
  - Okapi BM25 ranking function ($k_1=1.5, b=0.75, \epsilon=0.25$).
  - Dynamic relative pruning filter $\Phi(s, s_1, \tau_{\text{rel}}=0.35, \sigma_{\text{floor}})$.
- **3.3 Multi-Action Narrative Decomposition & Max-Pooling**: Syntactic segmentation operator $\Psi(x)$ and score aggregation $S_{\text{rag}}(j) = \max(\tilde{s}_{\text{global}}(j), \max_k \tilde{s}_{c_k}(j))$.
- **3.4 Statutory Element Contradiction & Score Decoupling**: Proof of zero score inflation ($\chi_j = 1 \implies S_{\text{final}} = 0.0$).
- **3.5 Exact-Span Fact Inclusion Mapping**: Character substring predicate $\mathcal{V}(s_i)$ and fact admission criterion.
- **3.6 Spatial Containment & Equirectangular Boundary Distance**: Jordan curve winding number $\Omega(p, R)$, segment projection parameter $t^*$, and 100-meter threshold $\theta_d = 100.0\text{ m}$.
- **3.7 Conjunctive Safety Gate & Human-Review Routing**: Multi-criteria 8-dimensional gate vector $\mathbf{g} \in \{0, 1\}^8$.

---

## 4. System Architecture & Methodology (IMRAD: Methods)
- **4.1 Architectural Topology**: 4-tier model (Client UI, FastAPI Backend, Legal Engine, LangGraph Structuring, PostgreSQL Persistence).
- **4.2 The Legal Classification Engine (`legal_engine/`)**:
  - Synonym normalisation across English, Hindi, and Hinglish (`synonyms.py`).
  - Two-stage non-penal grievance filter (`service.py`).
  - BM25 statutory retrieval and clause-level segmentation (`retrieval.py`).
  - Google Gemini 2.5 Flash orchestration with few-shot prompting (`llm_client.py`).
  - Deterministic BM25 keyword overlap fallback (`service.py`).
  - Procedural Schedule I registry mapping & Section 173(3) BNSS audit (`schedule_registry.py`).
- **4.3 The Complaint Structuring Engine (`complaint_engine/`)**:
  - LangGraph StateGraph assembly, `keep_original` reducer, immutable statement hashing (`graph.py`).
  - Deterministic regex and grounded LLM fact extraction (`extraction.py`).
  - Missing field detection and internal contradiction checks (`checks.py`).
  - Ray-casting point-in-polygon containment with boundary buffer (`jurisdiction.py`).
  - Evidence screening: MIME magic inspection, byte variance sharpness, generative tool regex, dHash duplicate detection (`evidence_screening.py`).
  - ReportLab bilingual PDF compilation and official email dispatch drafting (`pdf_generator.py`, `email_draft.py`).

---

## 5. Experimental Setup
- **5.1 Datasets & Benchmarks**:
  - BNS Statutory Corpus: 358 verified sections with audited procedural schedules.
  - BNS Synthetic Benchmark 50: 50 cases across English, Hindi, Hinglish, 12 categories, 35 dev / 15 heldout.
  - Complaint Structuring Benchmark 34: 34 cases, 220 gold facts across 7 entity categories.
  - Jurisdiction Benchmark 11: 11 spatial test cases across 102 Mumbai police stations.
- **5.2 Evaluation Metrics**:
  - Fact extraction recall, precision, unsupported rate, draft integrity.
  - Candidate retrieval recall @ $k=3, 5, 8, 10$, production candidate recall.
  - Contradicted false positive rate, non-penal gate specificity/sensitivity.
  - Procedural classification correctness under BNSS Schedule I.
- **5.3 Test Suite & Regression Verification**: 391 Python unit/integration tests (`pytest`) + 23 Frontend TAP tests (`src/trustSafety.test.js`) = 414 automated tests.

---

## 6. Results & Quantitative Analysis (IMRAD: Results)
- **6.1 System Implementation Verification**: Presentation of Table 1 (17 components verified).
- **6.2 Complaint Structuring Performance**:
  - Presentation of Table 3 (Baseline vs Updated System).
  - Heldout recall improvement: 51.69% $\to$ 85.39% (+33.70 pp, +65.20% relative).
  - Near-zero hallucination: 98.72% precision, 2.56% unsupported fact rate.
  - Draft integrity: 100% (14/14 heldout cases passed).
- **6.3 Legal Retrieval & Safeguard Evaluation**:
  - Presentation of Table 4 (Deterministic Fallback Mode on 50 cases).
  - 0.00% contradicted false positive rate (40/40 contradicted cases correctly suppressed).
  - 0.00% grievance gate false positive rate (43/43 affirmative crimes preserved).
- **6.4 Jurisdiction Territorial Allocation**:
  - Presentation of Table 5 (11/11 cases passed, 0.0% unsafe boundary assignments).
- **6.5 Mode Comparison**:
  - Presentation of Table 6 (Live Gemini 2.5 Flash vs Offline BM25 Fallback).
- **6.6 Computational Efficiency & Latencies**:
  - Presentation of Table 8 (BM25: 1.2ms, GIS: 0.15ms, Structuring: 12ms, PDF: 55ms).

---

## 7. Error Analysis & Case Studies (IMRAD: Discussion Part 1)
- **7.1 Missing Property Valuation (BNS-BM-01, BM-02)**: Section 303(2) proviso ambiguity when value $< ₹5{,}000$ cannot be determined.
- **7.2 Non-Penal Gate Leakage (BNS-BM-48)**: Commercial disputes using the word "cheated" passing through due to conservative safety bias.
- **7.3 Passive Voice Syntactic Omissions (Structuring H04, H13)**: Agentless passive sentences missing active regex predicates.
- **7.4 Benchmark Ground-Truth Fragility (BNS-BM-17)**: Dacoity label requiring 5 persons applied to a 2-person scenario.
- **7.5 Territorial Boundary Ambiguity**: 100-meter buffer returning `station: null` to avoid illegal jurisdictional assignments.

---

## 8. Discussion & Practical Implications (IMRAD: Discussion Part 2)
- **8.1 The Necessity of Decoupled Scoring in Legal RAG**: Why lexical similarity must be subordinate to statutory element satisfaction.
- **8.2 Exact Spans as the Antidote to Generative Hallucination**: Eliminating invented facts in legal administrative drafting.
- **8.3 Operationalizing Safety Gates in High-Stakes Public Systems**: Fail-safe human review routing.
- **8.4 Impact of Statutory Transition on Legal Informatics**: Handling ongoing statutory interpretation during early enactment of new criminal codes.

---

## 9. Ethical Considerations & Limitations
- **9.1 System Role as Decision Support**: Explicit disclaimers, no automated FIR generation.
- **9.2 Benchmark Limitations & Lack of Advocate Certification**: Synthetic data caveats, 8 provisional cases acknowledged.
- **9.3 Privacy & Data Security**: Statement hashing, immutable nonce verification, blocked third-party telemetry.
- **9.4 Territorial & Language Generalization**: Current restriction to Mumbai boundaries and English/Hindi/Hinglish vocabulary.

---

## 10. Conclusion & Future Work
- **10.1 Summary of Findings**: Proof that hybrid lexical-rule-LLM architectures with decoupled scoring achieve high recall and zero-hallucination compliance.
- **10.2 Future Directions**: Integration of fine-tuned bilingual legal bi-encoders (BGE-M3), expansion to all 36 States/UTs of India, CCTNS e-FIR interoperability, and advocate-certified benchmark expansion.

---

## References
*(Complete formal academic citations conforming to ACM / Springer bibliography styles).*

---

## Appendix
- **Appendix A**: Complete Publication-Ready Pseudocode for Algorithms 1 to 10.
- **Appendix B**: Pydantic JSON Request & Response Schemas.
- **Appendix C**: 12 Legal Case Categories in BNS Benchmark 50.
- **Appendix D**: Full Relational Schema & Migration DDL.
