# Bandhoo BNS Legal Classification Benchmark (v1.0)

## Overview
This benchmark evaluates the legal accuracy, generalization, and procedural reliability of **Bandhoo**—a Mumbai crime-reporting and legal-provision classification engine based on the **Bharatiya Nyaya Sanhita (BNS), 2023** and procedural mandates under the **Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023**.

Unlike hand-written unit tests that test fixed isolated fixtures, this benchmark comprises **50 diverse, realistic, and strictly fictional complaints** across English, Hindi, and Hinglish.

---

## 4-Tier Classification Schema

Every case is tagged with one of four legal certainty tiers:

| Tier | Category | Description | Engine Expectation |
| :--- | :--- | :--- | :--- |
| **Tier A** | **Supported candidate provision** | Narrative facts prima facie satisfy all essential statutory elements of one or more candidate provisions. | Relevant section(s) must appear in top candidate predictions with positive applicability scores. |
| **Tier B** | **Plausible alternative / Clarification needed** | Narrative points towards a legal domain, but material facts (e.g., property value, initial entrustment, or consent) are unverified or ambiguous. | Engine must output plausible sections, identify missing material facts, and express qualified uncertainty rather than premature finality. |
| **Tier C** | **Contradicted provision** | Specific statutory elements are legally or factually negated by complaint facts (e.g. metaphorical grievances like "daylight robbery pricing" or stealth theft negating robbery). | Contradicted provisions (e.g. Section 309 Robbery) must be strictly excluded or assigned 0.0 applicability. |
| **Tier D** | **Insufficient information** | Complaint is too brief, vague, or incoherent to justify any penal classification. | Engine must refrain from hallucinating penal sections and recommend clarification. |

---

## Dataset Schema

Each benchmark record in `bns_synthetic_benchmark_50.json` adheres to the following specification:

```json
{
  "case_id": "BNS-BM-14",
  "category": "robbery_statutory_circumstances",
  "language": "English",
  "narrative": "Two men cornered me in an alley near Kurla station. One man pinned both my arms tightly against the brick wall, physically restraining me so I could not move, while the other reached into my pockets and took my wallet and watch. No weapons were produced and they did not hit me.",
  "classification_type": "A",
  "relevant_candidate_sections": [309],
  "plausible_alternatives": [303],
  "contradicted_sections": [],
  "explicitly_supported_elements": [
    "Voluntary causing of wrongful restraint in order to the committing of theft (BNS Section 309)",
    "Theft of movable property (wallet and watch)"
  ],
  "unestablished_elements": ["Suspects' identities"],
  "contradicted_elements": ["Weapons used", "Actual physical blows or bodily injury caused"],
  "material_missing_facts": ["Value of wallet and watch"],
  "expected_uncertainty": "Robbery is established despite absence of weapons or injury because wrongful restraint satisfies the statutory alternative of Section 309.",
  "expected_attempt": false,
  "verified_schedule_applicable": true,
  "expected_cognizable": true,
  "expected_bailable": false,
  "legal_rationale": "Under BNS Section 309, theft is robbery if the offender for that end voluntarily causes or attempts to cause death, hurt, OR wrongful restraint. Physical pinning of arms constitutes wrongful restraint under Section 126 BNS, making the theft robbery. Absence of weapons or injuries does NOT negate Section 309. Cognizable and Non-bailable under BNSS Schedule I Part I.",
  "source_reference": "BNS, 2023 Sec 309; BNSS, 2023 First Schedule Part I (Entry for Section 309)",
  "review_status": "verified_authoritative"
}
```

---

## Distribution of Cases

### Language Breakdown
- **English**: 26 cases (52%)
- **Hindi (Devanagari)**: 12 cases (24%)
- **Hinglish (Colloquial Latin script)**: 12 cases (24%)
- **Total**: 50 cases

### Category Breakdown
1. **Direct Theft** (5 cases): Stealth taking, varying values, unstated values, pocket/car.
2. **Found Property Converted** (4 cases): BNS Section 314 dishonest conversion of lost articles on public roads.
3. **Snatching** (4 cases): BNS Section 304 sudden/quick/forcible seizure from person.
4. **Robbery Statutory Alternatives** (6 cases): BNS Section 309 via wrongful restraint, threat of instant hurt, actual injury, and weapons.
5. **Attempted Offences** (4 cases): Interrupted actions under BNS Section 62 read with primary offences.
6. **Explicit Negation** (4 cases): Narratives explicitly negating weapons, force, or hurt, testing contradiction handling.
7. **Compound Offences** (4 cases): Narratives alleging multiple offences (theft + house-breaking, hurt + theft, trespass + insult).
8. **Ambiguous Complaints** (4 cases): Civil commercial transactions vs criminal breach of trust / cheating, where material facts (entrustment, inducement, title) need clarification before any procedural route can be stated.
9. **Missing Material Facts** (4 cases): Unstated property values and missing criminal histories under Section 303(2) proviso.
10. **Misleading Keywords** (4 cases): Metaphorical phrases ("daylight robbery", "samay loot liya", "snatched promotion") testing immunity to keyword traps.
11. **Paraphrased Narratives** (4 cases): Complex syntax, formal legalistic prose, and colloquial train idioms.
12. **Insufficient Information** (3 cases): Ultra-brief or incoherent complaints testing uncertainty handling.

---

## Review Status and Provisional Labels

- `verified_authoritative` is the status assigned when the synthetic cases were built. **No case has a documented review by a qualified legal professional.**
- `provisional_pending_legal_review` marks eight cases whose statutory labels have specific documented concerns: BNS-BM-17, BNS-BM-20, BNS-BM-21, BNS-BM-22, BNS-BM-28, BNS-BM-30, BNS-BM-31 and BNS-BM-45. **Their labels are unchanged.**
- Each provisional case carries:
  - `label_review_notes`: a one-paragraph summary of the concern;
  - `label_review`: findings against the BNS text and BNSS First Schedule, the sources used, and `proposed_label_corrections_not_applied` (each with the current value, a proposed value and its statutory basis) for a qualified reviewer to accept or reject;
  - `review_history`: a dated audit trail of every metadata change.
- The review was an automated statutory cross-check, not a qualified legal review. Summary of concerns:
  - BM-20/21/22: `expected_bailable=true` conflicts with the Section 62 Schedule I row (bailability follows the offence attempted; Sections 303(2)/304(2)/305 are non-bailable). It would fit only if Section 134 (cognizable, bailable) were the intended offence, which is not labelled.
  - BM-17: lists Section 310 although only two offenders are described (Section 310(1) requires five or more).
  - BM-28/30/31/45: Section 305 (theft in a building used as a dwelling or for the custody of property) is unlabelled; BM-31 labels Section 316 without stated entrustment; BM-30's Section 306 depends on whether the "purana servant" was still employed.
- The evaluator reports `overall_metrics` (all 50 cases, including provisional ones), `overall_metrics_excluding_provisional` (42 cases) and `provisional_cases_only_metrics` (8 cases). Overall counts equal the sum of the other two, and the evaluator asserts this.

---

## Evaluation Metrics

1. **Precision & Recall** (micro-averaged over section instances):
   - **Precision**: Predicted sections that belong to `relevant_candidate_sections` **or** `plausible_alternatives`, divided by all predicted sections. This is lenient because plausible alternatives count as correct.
   - **Recall**: Ground-truth `relevant_candidate_sections` present among the final predictions, divided by all relevant sections. This is strict because plausible alternatives are not credited.
2. **Unsupported Section Rate**: Predicted sections absent from both label pools, divided by all predicted sections. It equals **1 − micro precision** and is not an independent metric. "Unsupported" means "not in the benchmark labels", not "legally unsupported by the facts".
3. **Retrieval Recall@k** (k = 3, 5, 8, 10): A diagnostic of single-pass `BM25LegalRetriever.retrieve(top_k=10, relative_threshold=0.35)`. It is **not** the service's candidate pool. The service uses `retrieve_clause_level(max_k=8)` and never validates more than 8 candidates, so Recall@10 is not achievable recall for the deployed pipeline. The relative threshold can also return fewer than k candidates.
4. **Production Candidate Recall**: Relevant sections found in the same `retrieve_clause_level(min_raw_score=0.0, relative_threshold=0.35, max_k=8)` call the service makes, divided by all relevant sections.
5. **Contradicted False-Positive Rate**: Cases where a provision in `contradicted_sections` was returned with score > 0, divided by cases listing at least one contradicted section (most list Section 309).
6. **Attempt Handling Correctness**: Whether attempted offences are flagged as attempts rather than completed offences.
7. **Negation & Misleading Keyword Immunity**: Rate at which negated provisions or metaphorical keyword traps are correctly zeroed out or excluded.
8. **Fact/Inference Separation**: Presence of explicit distinction between stated physical facts and legal inferences in the facts block.
9. **Procedural Classification Correctness**: Cases where the **top-ranked** prediction's `(is_cognizable, is_bailable)` equals the labelled pair, divided by cases with `verified_schedule_applicable=true` and a non-null `expected_cognizable`. A correct classification on a lower-ranked offence still counts as a miss.

All denominators are reported in `counts_and_denominators` for each partition (overall, excluding provisional, provisional only, development, previously inspected holdout, and each language).
