# Bandhoo Legal-Risk Remediation Plan

**Prepared:** 2026-10-20. **For:** Bandhoo maintainers (MNT), qualified Indian criminal-law reviewers (QLR), the adjudicator (ADJ), the evaluation lead (EL) and the project owner (PO).

**Status:** plan only. **No fix has been implemented.** Bandhoo remains internal-testing-only and is not legally validated.

Every change below must follow `reports/post_review_change_protocol.md` (gates 1–9). Plan item IDs (`P0-1` … `P2-4`) are local to this document; each is mapped to existing blocker (RB-xx) and checklist (LR-xx) identifiers. Sub-items first noted here are marked **(new)**.

**Evidence base:**
- `reports/source_verification_matrix.md` and `reports/source_verification_summary.md`;
- the code locations below, inspected on 2026-10-20.

All source comparisons use single copies: the PRS-hosted Gazette PDFs of the BNS and BNSS (25 Dec 2023), the PRS copy of the Consumer Protection Act, 2019, and a Manupatra print of *Lalita Kumari*. Matching one copy is not legal verification.

## 0. Prerequisites (before any remediation)

| ID | Prerequisite | Why |
|---|---|---|
| PRE-1 | **Commit a baseline** of the current working tree, or make hashed file backups. `legal_engine/`, `tests/`, `reports/` and `benchmark/` are currently **untracked** in git (one commit, `1ad5bb6`). | Protocol gate 9 relies on "revert the commit"; that is impossible for untracked files. Committing is a decision for the PO. |
| PRE-2 | **Obtain a second authoritative copy** of the BNS and BNSS (India Code, eGazette or the Legislative Department), and check for amendments after 25 Dec 2023 (RB-03). | Required to close any path-A transcription item; India Code was blocked during verification. |
| PRE-3 | **Assign named reviewers** (QLR ×2, ADJ, second checker). | No individuals are assigned in the blocker register. |
| PRE-4 | **Record the pre-change benchmark report** (`benchmark/evaluation_report_fallback.json`) and the hashes in `reports/release_blocker_register.md` Appendix B. | Needed for gate 7 comparisons. |

## 1. Summary of findings

| Plan ID | Finding | Existing IDs | Kind | Priority |
|---|---|---|---|---|
| P0-1 | Gemini prompt ties "within 14 days" to DSP permission | RB-08.a, RB-08, LR-11 | Confirmed textual discrepancy (prompt vs G-BNSS) | P0 |
| P0-2 | Gemini prompt states the 303(2) proviso outcome as settled | RB-06.a, RB-06, RB-07, LR-09, LR-10 | Unresolved legal interpretation (prompt inconsistent with service logic) | P0 |
| P0-3 | Non-penal template cites "Section 2(22)" for movable property | RB-23, LR-17 | Confirmed textual discrepancy (single copy) | P0 |
| P0-4 | Non-penal template: "forgery of records (Section 336/338)" | LR-17.a | Confirmed label/content mismatch (single copy); scope unresolved | P0 |
| P0-5 | Consumer forum and "Legal Metrology Department under the Consumer Protection Act, 2019" referral | RB-04.a, RB-04.b, LR-16 | Partly confirmed (forum exists; overcharging ground); Legal Metrology attribution unsupported by the inspected CPA copy; appropriateness unresolved | P0 |
| P1-1 | Stored text of BNS 115, 117(2), 117(4), 303, 304, 316, 318, 351 | RB-18–RB-21, RB-25, LR-01–LR-08 | Confirmed textual discrepancies (single copy) | P1 |
| P1-2 | BNS 324 bands vs Schedule I row 324(4) | RB-12, LR-15 | Confirmed conflict within the inspected copy; interpretation unresolved | P1 |
| P1-3 | Schedule I: s.87, 90, 276 (conflicts); s.354, 355, 357 (positional) | RB-32–RB-35, LR-19–LR-22 | Confirmed (87, 90, 276); suspected agreement (354, 355, 357) | P1 |
| P1-4 | Hand-entered registry rows and advice templates, including other prompt examples | RB-16, RB-17, LR-16, LR-18; RB-16.a **(new)** | Interpretation unresolved; RB-16.a suspected issue | P1 |
| P1-5 | Remaining flagged corpus records | RB-22, RB-24, RB-26–RB-31, LR-24–LR-29 | Mixed: confirmed (cross-reference subset, s.119 title) and suspected | P1 |
| P2-1 | Eight provisional benchmark cases | RB-37–RB-44, LR-30–LR-37 | Interpretation unresolved | P2 |
| P2-2 | Independent, lawyer-reviewed evaluation data | RB-45 | Evaluation limitation | P2 |
| P2-3 | Separate evaluation of fallback, cached, mocked and live outputs | RB-46, RB-47 | Evaluation limitation | P2 |
| P2-4 | Source and amendment verification before public release | RB-02, RB-03 | Source unavailable | P2 |

---

## 2. P0 — Potentially misleading legal or procedural output

### P0-1. Section 173(3) timing attached to DSP permission in the Gemini prompt

| Field | Content |
|---|---|
| IDs | RB-08.a (new in source verification); parent RB-08 / LR-11 |
| Location | `legal_engine/llm_client.py`, `SYSTEM_PROMPT` (starts line 33), section 5, line 59: "It is discretionary with prior permission from an officer not below the rank of Deputy Superintendent of Police (DSP) within 14 days, or police proceed directly with investigation when a prima facie case exists." |
| How it reaches users | Gemini's `recommended_action` is passed through by `_single_offence_procedure` (`legal_engine/service.py` lines 759–788) when the single supported candidate has no dedicated template (e.g. 304, 305, 306, 318, 351). The 173(3) audit appends the correct statutory note only when the text lacks DSP or "14" wording, so a mis-attributed timing statement can pass through. Multi-offence and templated paths do not use Gemini's text. |
| Evidence | G-BNSS 173(3) (quoted in the matrix): "…may with the prior permission from an officer not below the rank of Deputy Superintendent of Police, considering the nature and gravity of the offence,— (i) proceed to conduct preliminary enquiry to ascertain whether there exists a prima facie case for proceeding in the matter within a period of fourteen days; or (ii) proceed with investigation when there exists a prima facie case." Bandhoo's own `BNSS_173_3_PROCEDURE_TEXT` (`legal_engine/schedule_registry.py` line 28) and service docstring (`service.py` line 530) already follow the statutory structure; only the prompt differs. |
| Kind | **Confirmed textual discrepancy** between the prompt and the inspected copy. |
| Statutory text vs open questions | The text links "within a period of fourteen days" to limb (i), the preliminary enquiry, and links DSP permission to the officer's choice of (i) or (ii). **Not decided here:** what the fourteen days runs from; the consequence of exceeding it; whether 173(3) is a discretion or a requirement in practice; its relation to *Lalita Kumari* (para 111(vii) of the inspected print refers to fifteen days generally, in a CrPC context). These remain RB-08, RB-09 and RB-11. |
| Potential harm | A complainant, or an officer reading the output, may believe DSP permission must be obtained within 14 days, or that the enquiry has no time limit. The user may misjudge whether police delay is lawful. |
| Proposed minimal remediation | Replace the line 59 sentence so the prompt reuses the statutory structure, ideally by inserting `BNSS_173_3_PROCEDURE_TEXT` and `BNSS_173_3_CAVEAT_TEXT` from `schedule_registry.py` (one source of truth). Add no new interpretation. Optional, separate change (category C): extend the 173(3) audit in `_single_offence_procedure` to flag "permission … within 14 days" phrasing in Gemini text. |
| Approvals | QLR sign-off on the prompt wording (path B per this plan's ordering; the change is textual alignment, so review should be short). MNT technical approval. PO approval if the optional audit change is made. |
| Regression tests | (1) New test: `SYSTEM_PROMPT` contains no "permission … within 14 days" pattern and does contain the procedure text constant. (2) New test: a mocked Gemini response for a 304-only case with "DSP permission within 14 days" text is corrected or annotated (only if the optional audit change is approved). (3) Existing `tests/test_inspection_regressions.py` 173(3) wording tests stay green. |
| Acceptance criteria | Prompt wording matches the registry constant; all tests pass; no change in fallback benchmark (prompt not used in fallback); the docstring of `tests/test_procedural_law_audit.py` (line 245, "prior DSP permission within 14 days") corrected for consistency. |
| Rollback | Revert the prompt change (requires PRE-1). No data migration involved. |
| Dependencies | PRE-1, PRE-3. Not blocked by RB-08/RB-11 (no interpretation added). Cannot be evaluated live without an approved live run (P2-3). |

### P0-2. Section 303(2) proviso stated as settled in the Gemini prompt

| Field | Content |
|---|---|
| IDs | RB-06.a (new in source verification); parents RB-06 / LR-09 (FIR-stage cognizability), RB-07 / LR-10 (valuation) |
| Location | `legal_engine/llm_client.py` `SYSTEM_PROMPT` lines 65–67. Line 66: "If property value is ₹5,000 or more, or repeat offender: Cognizable and non-bailable under BNSS Schedule I…" Line 67: "If property value is under ₹5,000, first-time offender, and property restored/returned: Section 303(2) proviso applies (punishable with community service; classified as non-cognizable and bailable under BNSS Schedule I, requiring procedure under Section 174 BNSS)." |
| How it reaches users | Gemini's per-candidate `reasoning` becomes `predictions[].reasoning` (`service.py` line 1217). Bandhoo's own metadata (`_determine_schedule_metadata`) and theft template (`_theft_procedure_note`) override cognizable/bailable and the procedural text when Section 303 is a supported candidate, so the user could see Gemini reasoning saying "non-cognizable" next to Bandhoo's "classification unknown". |
| Evidence | G-BNS 303(2) proviso requires that "a person is convicted for the first time"; the G-BNSS Schedule row for "less than 5,000 rupees" does not mention first conviction (both quoted in the matrix). Bandhoo's service logic treats this as unresolved (`OPEN_LEGAL_QUESTIONS["303_proviso_at_registration"]`, `schedule_registry.py` line 51). |
| Kind | **Unresolved legal interpretation**; the prompt is internally inconsistent with Bandhoo's service logic (confirmed by code inspection). |
| Potential harm | A user may be told the matter is non-cognizable and NCR-only when that cannot be determined from a complaint, discouraging FIR registration; or contradictory statements in one response undermine trust. "Repeat offender" (line 66) also invites Gemini to infer conviction history from narratives. |
| Proposed minimal remediation | Replace lines 66–67 with an instruction that mirrors the service's uncertainty-preserving position:<br>• state both Schedule I rows as written;<br>• state that the BNS proviso also requires a first conviction, which cannot be established from a complaint;<br>• state that FIR-stage treatment is unresolved;<br>• never infer first conviction or prior record from narrative wording;<br>• never state that the proviso "applies".<br>Reuse the `OPEN_LEGAL_QUESTIONS` wording. **Do not encode any answer on FIR-stage cognizability or valuation** (aggregate vs per item; market vs purchase value). |
| Approvals | QLR (path B): wording must not imply a conclusion. MNT. PO for user-facing effect. |
| Regression tests | (1) Prompt test: no "proviso applies" assertion; uncertainty wording present. (2) Service test with a mocked Gemini payload whose reasoning says "proviso applies; non-cognizable": `is_cognizable`/`is_bailable` remain `None` and the action keeps both pathways (extends existing `tests/test_inspection_regressions.py` theft tests). (3) Existing proviso tests (`tests/test_legal_accuracy_audit.py` scenarios 1, 4, 5; `tests/test_procedural_law_audit.py` case 7) stay green. |
| Acceptance criteria | No prompt statement presents the proviso outcome as settled; service outputs unchanged in fallback benchmark; QLR records that no interpretation was encoded. |
| Rollback | Revert prompt change (PRE-1). |
| Dependencies | PRE-1, PRE-3. Final wording of any **decision** depends on RB-06/RB-07 (blocked); this remediation only removes the premature conclusion. |

### P0-3. "Section 2(22)" cited for movable property

| Field | Content |
|---|---|
| IDs | RB-23 / LR-17 |
| Location | `legal_engine/service.py` `_build_non_penal_response` (starts line 1000): docstring line 1014 ("Correctly cites Section 303 read with Section 2(22)…") and the intangible-grievance response at line 1035 ("Under Section 303 read with Section 2(22) of the BNS, 2023, penal offences against property strictly apply to corporeal movable property; intangible concepts (e.g., promotions, work credit, …) cannot be the subject of penal theft or robbery."). Test encoding the current citation: `tests/test_adversarial_grievance_audit.py` lines 70, 81–82 (`assert "2(22)" in action`). |
| Evidence | G-BNS: "(21) "movable property" includes property of every description, except land and things attached to the earth…"; "(22) "number".—…" (matrix §2). |
| Kind | **Confirmed textual discrepancy** in a citation (single copy). The accompanying legal statement about intangible concepts is a separate **unresolved interpretation**. |
| Potential harm | Citing the wrong clause undermines credibility and may mislead anyone who checks the statute. The categorical statement that intangibles "cannot be the subject of penal theft" may overstate the law for some intangible-adjacent property (e.g. documents, data on media); this is for QLR review. |
| Proposed minimal remediation | (a) Path A: change "2(22)" to "2(21)" at lines 1014 and 1035 once PRE-2 confirms the clause number in a second copy. Update the test assertion to "2(21)" with the protocol gate-6 justification (the test encoded the discrepancy). (b) Path B, separate change: QLR review of the "intangible concepts … cannot be the subject of penal theft" sentence; change only if the QLR specifies wording. |
| Approvals | (a) MNT plus second checker; no QLR needed for the number. (b) QLR. |
| Regression tests | Updated `test_scenario_3_workplace_grievance_insufficient_facts` asserting "2(21)" and absence of "2(22)"; a new test that every "Section 2(n)" citation in templates is in an approved list. |
| Acceptance criteria | Second-copy confirmation recorded; tests pass; fallback benchmark unchanged except response text (non-penal cases BM-41–44 style); no other template affected. |
| Rollback | Revert the code change (PRE-1). |
| Dependencies | PRE-1, PRE-2. |

### P0-4. "Forgery of records (Section 336/338)" label

| Field | Content |
|---|---|
| IDs | LR-17.a (new in source verification); parent LR-16 / RB-16 |
| Location | `legal_engine/service.py` `_build_non_penal_response`, intangible-grievance text at line 1039: "…criminal breach of trust (Section 316), cheating (Section 318), forgery of records (Section 336/338), or criminal intimidation (Section 351)…" |
| Evidence | G-BNS 336(1) concerns making a false document or false electronic record; G-BNS 338 concerns forgery of a valuable security, will, authority to adopt, etc. A margin heading "Forgery of record of Court or of public register, etc." appears in the extraction around ss.337–341; its section was not confirmed; ss.336–338 were not read in full (matrix §9). |
| Kind | **Confirmed mismatch** between the label and the inspected section content (single copy); the correct scope is an **unresolved interpretation**. |
| Potential harm | A user with a workplace-records grievance may be pointed to an inapplicable provision (338) or miss the relevant one, misdirecting a complaint. |
| Proposed minimal remediation | **First confirm the intended scope with the MNT and QLR:** what kind of "records" the sentence is meant to cover (workplace documents, electronic records, public registers). Then, depending on that, either:<br>• cite only the provision(s) the QLR confirms; or<br>• remove section numbers and say "forgery-related offences, subject to verification of the facts".<br>Read ss.336–340 in full in a second copy before choosing. Make no change until scope and source are confirmed. |
| Approvals | QLR (path B), MNT. |
| Regression tests | Test that the non-penal template cites only an approved set of sections, each of which exists in the corpus with a matching title. |
| Acceptance criteria | QLR-approved wording; tests pass; no other template changed. |
| Rollback | Revert (PRE-1). |
| Dependencies | PRE-1, PRE-2, PRE-3. |

### P0-5. Consumer forum and Legal Metrology referral

| Field | Content |
|---|---|
| IDs | RB-04.a, RB-04.b (new in source verification); parents RB-04, LR-16 |
| Location | `legal_engine/service.py` `_build_non_penal_response`, consumer-pricing response lines 1018–1028, ending "…For retail overcharging or pricing grievances without criminal acts, recourse lies before the Consumer Disputes Redressal Commission or Legal Metrology Department under the Consumer Protection Act, 2019." Test constraint: `tests/test_adversarial_grievance_audit.py` line 65 asserts "consumer protection act" appears. |
| Evidence | CPA-PRS ss.28(1), 42(1), 53(1) establish District, State and National Consumer Disputes Redressal Commissions. s.2(6)(iv) defines a complaint including that a trader "has charged … a price in excess of the price— (a) fixed by or under any law…; (b) displayed on the goods or any package…; (c) displayed on the price list…; (d) agreed between the parties". The inspected CPA copy contains **no** reference to "Legal Metrology". No Legal Metrology source was inspected (matrix §9). |
| Kind | Forum existence and overcharging ground: **confirmed against available copy**. Attribution of a "Legal Metrology Department" to the CPA: **discrepancy observed**. Whether the referral is appropriate for the narratives that trigger it (e.g. "daylight robbery" about high prices): **interpretation unresolved**. |
| Potential harm | Users may be sent to a body under the wrong statute, or told they have a consumer remedy for prices that are merely high (the CPA ground covers charging above a fixed, displayed or agreed price). |
| Proposed minimal remediation | (1) Remove the words "or Legal Metrology Department" from the CPA attribution unless an authoritative source is obtained and the QLR approves a separately sourced mention (e.g. under the statute that actually governs it, once inspected). (2) Narrow the Consumer Commission sentence to the s.2(6)(iv) scope: where a price above one fixed by law, displayed or agreed was charged. Keep the Act name (the existing test stays valid). Changes are proposed only after the QLR confirms the intended scope; no other referral bodies are added. |
| Approvals | QLR (path B), MNT, PO (user-facing). |
| Regression tests | (1) Test that "Legal Metrology" is absent, or is attributed only to an approved source. (2) Existing line-65 assertion retained. (3) Test that the referral sentence includes the s.2(6)(iv) qualifier. |
| Acceptance criteria | QLR-approved wording; tests pass; non-penal gate behaviour unchanged (same cases fire). |
| Rollback | Revert (PRE-1). |
| Dependencies | PRE-1, PRE-3; for any Legal Metrology mention, the source gap in RB-04.b must be closed first. |

---

## 3. P1 — Statutory-text and procedural accuracy

### P1-1. Stored text of BNS 115, 117(2), 117(4), 303, 304, 316, 318, 351

| Field | Content |
|---|---|
| IDs | RB-18 (115), RB-19 (117(2), 117(4)), RB-21 (303), RB-20 (351), RB-25 (304, 316, 318); LR-01–LR-08 |
| Location | `bns_rag_dataset.json` records 115, 117, 303, 304, 316, 318, 351 (`text` field; `verification.text_status` currently `differs_from_gazette_needs_review`). Used by BM25 (`corpus.get_document_text`) and shown to Gemini (`corpus.format_for_llm_context`, line 113). |
| Evidence | Passages quoted in matrix §3, §4 and §8:<br>• 115(2) "section 120" vs G-BNS "section 122";<br>• 117(2) "sub-section (3)" vs "sub-section (2) of section 122";<br>• 117(4) missing "acting in concert", "or community", "similar";<br>• 351 "treating" vs "threatening", and different word order;<br>• 303 "effects" vs "affects";<br>• 304 "moveable" vs "movable";<br>• 316 illustration "a lakh" vs "one lakh";<br>• 318 illustration "diamond" vs "diamonds". |
| Kind | **Confirmed textual discrepancies** against a single copy. Not proof of legal error. |
| Potential harm | Gemini reasons over wrong cross-references and incomplete elements (117(4) group grievous hurt; 351 threat wording). Users may see wrong statutory text if it is surfaced. The registry, not this text, drives classification, so procedural metadata is unaffected. |
| Proposed minimal remediation | After PRE-2, apply a migration modelled on `reports/apply_corpus_corrections.py`:<br>• replace **only** the differing passages, with ordered-match validation, verified backup and correction log;<br>• one section per correction entry;<br>• leave the record's `verification` status as "restored_from_gazette" only where the full text is transcribed; otherwise record "corrected_passages" with evidence;<br>• do not change titles or keywords. |
| Approvals | Path A (MNT plus second checker) for 115, 303, 304, 316, 318. Path B (QLR) for 117(2), 117(4) and 351, because the words affect offence elements. |
| Regression tests | Per-section corpus tests (in the style of `tests/test_corpus_integrity.py`) asserting the corrected passages; the migration validator rejects altered or reordered text. |
| Acceptance criteria | Validator passes; full suite passes; **fallback benchmark compared case by case with an ablation** (text changes alter BM25 statistics for every query, as observed when s.111 and s.120 were restored); every changed prediction explained; no labels changed. |
| Rollback | Restore the verified backup created by the migration (path and SHA-256 recorded), then re-run tests and benchmark. |
| Dependencies | PRE-1, PRE-2 (a second copy is mandatory), PRE-3. |

### P1-2. BNS 324 value bands vs Schedule I

| Field | Content |
|---|---|
| IDs | RB-12 / LR-15; `OPEN_LEGAL_QUESTIONS["324_value_bands"]` (`schedule_registry.py` line 62) |
| Location | Registry entry 324 (`schedule_registry.py` line 224); `_mischief_procedure_note` (`service.py`, called from `_section_procedure_note` line 708). |
| Evidence | G-BNS 324(4) "less than one lakh"; G-BNSS row 324(4) "less than 2 lakh"; row 324(5) "one lakh rupees or upwards" (matrix §4). |
| Kind | **Confirmed conflict** within the inspected copy; **interpretation unresolved**. |
| Current behaviour | Cognizability left unknown for s.324 unless the sub-section is known; the advice states the conflict as unresolved. This is the safe position. |
| Potential harm | Low while uncertainty is preserved; losses of Rs 1–2 lakh could be misclassified if logic is changed prematurely. |
| Proposed minimal remediation | **No change** until the QLR/ADJ decision and a check for any corrigendum or amendment (PRE-2). Then encode the decision in the registry (category C) and update the advice note. |
| Approvals | QLR and ADJ (path B/C), MNT. |
| Regression tests | Registry tests for loss values of Rs 99,999, Rs 1,00,000, Rs 1,50,000 and Rs 2,00,000, once decided. |
| Acceptance criteria | Decision recorded with its source; tests pass; benchmark unchanged or explained. |
| Rollback | Revert the registry change (PRE-1). |
| Dependencies | PRE-2, RB-12 decision. |

### P1-3. Schedule I: s.87, 90, 276 conflicts; s.354, 355, 357 positional reading

| Field | Content |
|---|---|
| IDs | RB-32, RB-33, RB-34, RB-35; LR-19–LR-22 |
| Location | `bns_rag_dataset.json` records 87, 90, 276, 354, 355, 357, field `scraped_procedural_classification` (`gazette_check` values `conflicts_with_gazette_schedule_i` or `consistent_manual_positional_reading`). These sections are not in the registry. |
| Evidence | Matrix §6: G-BNSS rows 87 and 90 Cognizable; 276 Non-bailable; scraped blocks differ. s.354, 355 and 357 agree by positional reading only. |
| Kind | Confirmed (87, 90, 276); suspected agreement (354, 355, 357). |
| Current behaviour | Scraped blocks are **not** used for procedural output and are not shown to Gemini; their words are in the BM25 index only. |
| Potential harm | Low now; high if the blocks are later added to the registry or surfaced. |
| Proposed minimal remediation | (1) Path A: confirm s.354, 355 and 357 from the printed page or a second copy; update `gazette_check`. (2) Path A: correct or mark the three conflicting blocks (data change only, no registry addition). (3) Category C, separate: adding any of these sections to the registry needs QLR confirmation and tests. |
| Approvals | MNT plus second checker for (1)–(2); QLR for (3). |
| Regression tests | Corpus tests asserting the `gazette_check` values; registry tests if (3) proceeds. |
| Acceptance criteria | Gate 7 benchmark comparison (BM25 index wording changes if block text changes). |
| Rollback | Restore the migration backup. |
| Dependencies | PRE-2. |

### P1-4. Hand-entered registry rows, advice templates and other prompt examples

| Field | Content |
|---|---|
| IDs | RB-17 / LR-18 (registry); RB-16 / LR-16 (templates); RB-16.a **(new)**: prompt examples |
| Location | `VERIFIED_SCHEDULE_I` (`schedule_registry.py`); templates `_theft_procedure_note`, `_robbery_procedure_note`, `_cbt_procedure_note`, `_grievous_hurt_procedure_note`, `_mischief_procedure_note`, `_misappropriation_procedure_note`, `_single_offence_procedure`, `_multi_offence_procedure`, `_build_non_penal_response` (`service.py`); `SYSTEM_PROMPT` lines 62–63. |
| RB-16.a (new) | Prompt line 62 lists "Mischief Sec 324" among offences "punishable with less than 3 years". The registry and G-BNSS row 324(5)–(6) give up to 5 years (cognizable). Line 63 lists "Murder Sec 103" and "Rape Sec 64" as 7 years or more; these sections are not in the registry and were not source-checked in this exercise. **Suspected issue.** |
| Evidence | Registry rows were transcribed from G-BNSS (matrix §6); robbery and misappropriation template facts confirmed against the copy (matrix §9). |
| Kind | Interpretation unresolved (template adequacy, sub-section heuristics, 173(3) range reading RB-09, multi-offence RB-10); RB-16.a suspected. |
| Potential harm | Inaccurate or overconfident procedural advice to citizens. |
| Proposed minimal remediation | QLR review of each template sentence and registry row. Fix only the specific sentences the QLR identifies. For RB-16.a: remove the s.324 example or qualify it by sub-section, after QLR confirmation; source-check ss.103 and 64 before keeping them as examples. |
| Approvals | QLR (path B); PO for user-facing templates; registry row changes path C. |
| Regression tests | One test per changed sentence or row; prompt-content tests (none exist today). |
| Acceptance criteria | Each change carries a protocol change record; tests pass; benchmark compared. |
| Rollback | Revert (PRE-1). |
| Dependencies | PRE-1, PRE-2, PRE-3; RB-09, RB-10, RB-14 decisions where relevant. |

### P1-5. Remaining flagged corpus records

| Field | Content |
|---|---|
| IDs | RB-22 (confirmed cross-references: s.71, 89, 148, 199, 264, 341), RB-24 (s.119 title), RB-26 (suspected cross-references), RB-27 (80 differing), RB-28 (56 possibly incomplete), RB-29 (13 unverified punishments), RB-30 (63 automated "no punishment clause"), RB-31 (324 artefacts); LR-24–LR-29 |
| Location | `bns_rag_dataset.json` (`verification.evidence` per record); checklist Appendix A. |
| Kind | Confirmed for RB-22 and RB-24; suspected for the rest. **Not all are errors**; many are formatting or extraction artefacts. |
| Potential harm | Wrong cross-references in Gemini context; incomplete text lowers retrieval and reasoning quality. |
| Proposed minimal remediation | Manual review record by record, classifying each as error, artefact or acceptable. Correct only confirmed errors through path A migrations in small batches. Never bulk-replace the corpus with Gazette text. |
| Approvals | MNT plus second checker; QLR where meaning changes. |
| Regression tests | Corpus tests for corrected records; validator. |
| Acceptance criteria | Each batch: benchmark ablation and case-by-case explanation. |
| Rollback | Migration backup. |
| Dependencies | PRE-2. |

---

## 4. P2 — Evaluation and release controls

| Plan ID | IDs | Finding | Proposed remediation | Approvals | Acceptance / closure | Dependencies |
|---|---|---|---|---|---|---|
| P2-1 | RB-37–RB-44; LR-30–LR-37 | Eight provisional benchmark cases; labels unchanged; proposed corrections recorded in `benchmark/bns_synthetic_benchmark_50.json` (`label_review`). | Independent double labelling by two QLRs and ADJ adjudication. Apply decisions through `benchmark/build_dataset.py` with `review_history` entries. **Never relabel to improve metrics.** | QLR ×2, ADJ | Labels decided and recorded; metrics reported with and without the cases; label changes are separate commits from code changes. | PRE-3 |
| P2-2 | RB-45 | No independent, lawyer-reviewed evaluation data; the 50-case benchmark was used in development. | Execute `reports/independent_evaluation_plan.md` (case authoring, de-identification, double labelling, sealed test split). | EL, QLR, PO | Final-test report produced in the plan's format. | PRE-3; funding and time decision by PO |
| P2-3 | RB-46, RB-47 | Fallback, cached, mocked and live outputs must be evaluated separately; no recent live results; planned metrics not implemented. | Extend `benchmark/evaluate_benchmark.py` (it already records `inference_status`) to add strict precision, abstention, per-offence procedural accuracy and serious-error tagging, tested on development data only. Run live evaluation only with PO approval and a quota budget. | MNT, EL, PO | Mode-separated reports; mocked results never reported as performance. | P2-2 for the test set |
| P2-4 | RB-02, RB-03 | Source and amendment verification incomplete (India Code blocked; *Lalita Kumari* only via a third-party print with unverified TLS; amendments unknown). | Obtain official copies; re-run the source-verification matrix against them. | MNT, QLR | Matrix updated with a second source for every P0/P1 item. | None (can start immediately) |

---

## 5. Safe implementation order

| Category | Contents | Gate | Can start when |
|---|---|---|---|
| **A. Transcription or citation corrections** | P0-3(a) "2(22)" → "2(21)"; P1-1 for s.115, 303, 304, 316, 318; P1-3 (s.354/355/357 confirmation; marking the 87/90/276 blocks); P1-5 confirmed items (RB-22 cross-references; RB-24 s.119 title) | Path A: second source copy (PRE-2) plus second checker; regression test; benchmark ablation | PRE-1, PRE-2 complete |
| **B. Advice-template and prompt changes** | P0-1 (prompt 173(3) timing aligned with statutory structure, no new interpretation); P0-2 (remove settled proviso statements, uncertainty-preserving wording); P0-3(b) intangible-property sentence; P0-4 forgery label, after scope confirmation; P0-5 consumer and Legal Metrology wording, after scope and source confirmation; P1-1 for s.117(2), 117(4), 351; P1-4 template sentences and RB-16.a | Path B: QLR sign-off; tests; benchmark comparison | PRE-1, PRE-3; P0-4 and P0-5 also need their source and scope confirmation |
| **C. Substantive procedural-logic changes** | Any rule decided under RB-06 (303(2) at FIR stage), RB-07 (valuation), RB-09 (173(3) range reading), RB-10 (multi-offence), RB-12 (324 bands); registry additions (87, 90, 276); optional 173(3) audit of Gemini text (P0-1 option) | Path B/C: QLR and ADJ decision; regression tests on boundary cases; benchmark comparison; PO approval | The relevant legal decision is recorded |
| **D. Benchmark-label changes** | P2-1 (eight provisional cases) | Independent adjudication; separate change records | QLR ×2 and ADJ available |
| **E. Blocked until independent evaluation exists** | Retrieval or threshold tuning; fallback-precision work; any public-release decision; any performance claim beyond "development benchmark, fallback mode"; removing scraped wording from the BM25 index | Independent test set (P2-2) and mode-separated results (P2-3) | P2-2 and P2-3 complete |

Recommended first steps, in order:
1. PRE-1 to PRE-4.
2. P2-4 (source acquisition; unblocks category A).
3. Category B items P0-1 and P0-2. They are prompt-only, add no interpretation, remove misleading statements, and do not affect the fallback benchmark.
4. Category A P0-3(a).
5. Remaining A items in small batches.
6. B items needing scope confirmation (P0-4, P0-5).
7. C and D as decisions arrive.
8. E only after independent evaluation.

### Specific constraints

- **Section 173(3) timing (P0-1):** the remediation aligns the prompt with the statutory sentence structure. In the inspected copy, "within a period of fourteen days" is part of limb (i), the preliminary enquiry, and DSP permission precedes the choice between limbs. It does **not** decide when the period starts, the consequence of exceeding it, or how it relates to *Lalita Kumari*'s fifteen-day guidance (RB-08, RB-11 remain open).
- **Section 303(2) (P0-2):** the remediation **removes** a premature conclusion. It does not encode any answer on cognizability at FIR stage or on property valuation (RB-06, RB-07 remain open).
- **Forgery and consumer referral (P0-4, P0-5):** wording changes only after the intended scope is confirmed and the relevant provisions are read in an authoritative source. The proposals are narrow: remove unsupported attributions, qualify the CPA ground. No new bodies or sections are added without a source.

## 6. Existing tests affected by remediation

| Test | Current assertion | Affected by | Required handling |
|---|---|---|---|
| `tests/test_adversarial_grievance_audit.py` lines 70, 81–82 | `"2(22)" in action` | P0-3 | Update to "2(21)" with a gate-6 justification (the test encoded the discrepancy). |
| `tests/test_adversarial_grievance_audit.py` line 65 | "consumer protection act" in action | P0-5 | Keep; the remediation retains the Act name. |
| `tests/test_procedural_law_audit.py` line 245 (docstring only) | "qualified with prior DSP permission within 14 days" | P0-1 | Correct the docstring for consistency; no assertion change. |
| `tests/test_inspection_regressions.py` (173(3) wording, theft proviso), `tests/test_reliability_followups.py` (uncertainty preservation) | Uncertainty and wording guards | P0-1, P0-2, P1-2 | Must remain green. |
| None | `SYSTEM_PROMPT` content | P0-1, P0-2, RB-16.a | New prompt-content tests needed. |

## 7. What remains blocked

| Item | Blocked by |
|---|---|
| All category A work | PRE-2 (second source copy; amendment check) |
| Decisions on RB-06, RB-07, RB-09, RB-10, RB-11, RB-12 and the eight benchmark labels | QLR and ADJ availability (PRE-3) |
| *Lalita Kumari* citation closure | Supreme Court or SCC copy (RB-02) |
| Any Legal Metrology mention | An identified, inspected authoritative source (RB-04.b) |
| Performance claims and release decisions | Independent evaluation (P2-2, P2-3) |
| Rollback by commit revert | PRE-1 |

No blocker in `reports/release_blocker_register.md` is closed or changed by this plan.
