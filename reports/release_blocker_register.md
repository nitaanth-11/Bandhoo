# Bandhoo Release Blocker Register

**Prepared:** 2026-10-20. **Classification:** internal testing only. Bandhoo is **not** legally validated and **not** ready for public release.

Every blocker below is **Open**. This register records what is known; it does not resolve any legal question.

## 1. Checkpoint verification (performed 2026-10-20)

| Check | Result |
|---|---|
| `reports/source_verification_matrix.md` | **Missing.** The file does not exist and nothing in the repository references it. The source-verification task did not produce its deliverables (see RB-01). |
| `reports/source_verification_summary.md` | **Missing.** Same as above. |
| Reports present and read | `legal_review_checklist.md`, `independent_evaluation_plan.md`, `corpus_integrity_audit.md`, `corpus_data_quality_report.md`, `corpus_corrections_log_2026-10-20.json`, `release_readiness_2026-10-20.md`, `CORPUS_UPDATE_WORKFLOW.md` |
| Corpus `bns_rag_dataset.json` | SHA-256 `7c7e3322b277e8bd9ecfaf301641bd6bffeb6c3709ae933160e86aa4cb127e5b`. Matches the reviewed migration output recorded earlier. |
| Backup `reports/backups/bns_rag_dataset.pre_integrity_migration_2026-10-20.json` | SHA-256 `d053ce3de31ef17d985b03251e9178d38b3ed70144dc2abe7802c1f873783807`. Unchanged and read-only. |
| `public/bns_rag_dataset.json` | Same hash as the backup (intentionally not migrated; unused by the app). |
| Benchmark labels `benchmark/bns_synthetic_benchmark_50.json` | SHA-256 `36f2e00dc517fe03664a3fb9b58fd8e627ebc1ce3f4331e2f637e83c78583892`. Matches the value recorded after the round-3 label review. |
| Production code | No file modified after `independent_evaluation_plan.md` was written (modification-time scan). No code checksums had been recorded before today, so this rests on modification times and git status, not on hash comparison. Baseline hashes for future checks are in Appendix B. |
| Version control | Single commit (`1ad5bb6`). Uncommitted changes: `.gitignore`, `bns_rag_dataset.json`, `main.py`, `public/bns_rag_dataset.json`, `scrape_bns.py`, `src/App.jsx`. Untracked: `benchmark/`, `legal_engine/`, `reports/`, `tests/`, `pytest.ini`, `requirements.txt`. The `main.py`, `src/App.jsx` and `public/` changes predate this work. Nothing was reset, cleaned or discarded. |
| Test suite | **228 passed, 1 warning** (upstream GenAI SDK deprecation), run offline with Gemini disabled. |
| Gemini / `.env` | No API call made; `.env` not read. |

### Inconsistencies and unverified claims in existing reports

| Location | Issue |
|---|---|
| `corpus_data_quality_report.md` (table row and recommendation 1) | Still lists Section 54 as a "genuine gap" to re-extract. The report's own superseded notice and `corpus_integrity_audit.md` correct this (Section 54 is a deeming provision). The body was not rewritten, to preserve the record. |
| `legal_engine/schedule_registry.py` lines 39 and 59; checklist LR-14 | "*Lalita Kumari v. Government of Uttar Pradesh*, (2014) 2 SCC 1" was written from general knowledge. **Not verified**; the judgment is not held (RB-02). |
| `legal_engine/service.py` line 1028; checklist LR-16 | Referral to the "Consumer Disputes Redressal Commission or Legal Metrology Department under the Consumer Protection Act, 2019" is **not verified** against that Act. |
| `legal_engine/service.py` lines 1014 and 1035; checklist LR-17 | Cites "Section 2(22)" for movable property. The available Gazette copy defines it at 2(21) (RB-23). |
| Checklist LR-14 | Mentions an SCC Online blog post (January 2026) seen only as a search result. It was not read in full and is not authority. |

## 2. How to read this register

| Field | Meaning |
|---|---|
| Class | **C** = confirmed against the single available Gazette copy (passage read manually; the difference is clear in that copy). **S** = suspected (automated comparison only, or possible extraction artefact). **I** = unresolved legal interpretation. **M** = missing source or evidence. **E** = evaluation limitation. **P** = process or operational gap. |
| Note on C | Confirmed against one copy is **not proof of an error**. Closure needs either a second authoritative copy (e.g. India Code or eGazette) or confirmation by a qualified reviewer. |
| Impact | **High** = can change offence predictions or procedural advice for common complaints. **Medium** = affects less frequent outputs, metrics or user-facing wording. **Low** = no current effect on outputs. |
| Responsible | QLR = qualified Indian criminal-law reviewer. ADJ = adjudicator. EL = evaluation lead. MNT = Bandhoo maintainer. PO = project owner. No individuals have been assigned. |
| Status | Open, In review, Closed. All are Open today. |

Sources referred to as "Gazette copy" are the PRS-hosted PDFs of the BNS (Act 45 of 2023) and BNSS (Act 46 of 2023), Gazette of India Extraordinary, 25 Dec 2023, text extracted with `pypdf`.

## 3. Missing sources and process gaps

| ID | Ref | Class | Blocker | Impact | Evidence available | Evidence needed | Resp. | Status | Closure condition |
|---|---|---|---|---|---|---|---|---|---|
| RB-01 | — | P | Source-verification matrix and summary were never produced. | Medium | This register and the checklist cover part of the ground. | A matrix mapping each statutory claim in code and corpus to its source, passage and verification status. | MNT, QLR | Open | Both files exist, and every entry has a source and status. |
| RB-02 | LR-14 | M | *Lalita Kumari* judgment not available; citation and summary unverified. | High (appears in every 173(3) caveat) | Citation text in code only. | Judgment text from an authoritative reporter or the Supreme Court website; any later decisions on 173(3). | QLR | Open | Citation and summary confirmed or corrected by QLR. |
| RB-03 | All statutory items | M | Single source copy; India Code copy not obtained; no check for amendments to the BNS or BNSS after 25 Dec 2023. | High | PRS-hosted Gazette PDFs (25 Dec 2023). | A second authoritative copy; a consolidated or amended text if any amendments exist. | MNT, QLR | Open | Second copy obtained and compared; amendment status confirmed by QLR. |
| RB-04 | LR-16 | M | Consumer Protection Act, 2019 referral wording unverified. | Medium (non-penal responses) | Template text only. | The Act and forum structure, checked by QLR. | QLR | Open | Wording approved or replaced. |
| RB-05 | LR-25 | S | The 15 corrections applied on 2026-10-20 rest on one source copy (machine-checked transcription). | Medium | Corrections log; automated ordered-match check. | Second-copy confirmation. | QLR or MNT | Open | Each correction confirmed against a second authoritative copy. |

## 4. Unresolved legal interpretations (affect predictions or procedural advice)

| ID | Ref | Class | Blocker | Impact | Evidence available | Evidence needed | Resp. | Status | Closure condition |
|---|---|---|---|---|---|---|---|---|---|
| RB-06 | LR-09 | I | BNS 303(2) proviso at FIR registration: may theft under Rs 5,000 with property returned be treated as non-cognizable when first conviction is unknown? Bandhoo leaves classification unknown. | High | BNS 303(2) and both BNSS Schedule rows (Gazette copy). | QLR opinion; any judicial or departmental guidance. | QLR, ADJ | Open | Written decision on the rule Bandhoo should apply, and on the user-facing wording. |
| RB-07 | LR-10 | I | Valuation of "stolen property" (aggregate vs per item; market vs purchase value). Bandhoo treats any single item of Rs 5,000 or more as meeting the threshold and ambiguous totals as unknown. | High | Parser rules (`amounts.py`). | QLR opinion; case law on valuation. | QLR | Open | Decision recorded; parser rules confirmed or change approved. |
| RB-08 | LR-11 | I | BNSS 173(3) paraphrase, "discretion" characterisation, 14-day timing, and whether citizen advice should mention 173(3). | High | Gazette text of 173(3); Bandhoo paraphrase. | QLR review. | QLR | Open | Wording approved or replaced. |
| RB-09 | LR-12 | I | "Punishable for three years or more but less than seven years" read by maximum term. Affects 7-year offences (117(2), 305, 306, 316(3)–(4), 318(4)) and 3-year offences (303(2) first conviction, 304(2)). | High | Gazette text; code labels the reading "pending review". | QLR opinion; commentary or case law. | QLR, ADJ | Open | Reading decided; boundary handling confirmed. |
| RB-10 | LR-13 | I | Several offences in one complaint: citing BNSS 174(4) at the information stage; 173(3) when one offence is 7 years or more. | High | Gazette text of 174(4). | QLR opinion. | QLR | Open | Decision recorded; multi-offence advice approved or changed. |
| RB-11 | LR-14 | I | Relationship between 173(3) and *Lalita Kumari*. | High | None authoritative (see RB-02). | Judgment and later authority. | QLR | Open | QLR position recorded; caveat wording approved. |
| RB-12 | LR-15 | I (and C) | BNS 324(4) band "less than one lakh" vs Schedule I row 324(4) "less than 2 lakh" (both read manually in the Gazette copy). Classification for Rs 1–2 lakh losses is unresolved. | Medium | Both passages in the Gazette copy. | Second copy; any corrigendum; QLR opinion. | QLR | Open | Applicable classification decided. |
| RB-13 | LR-03(b) | I | Which theft term governs 173(3): 3 years (first conviction) or the Schedule row's 1–5 years (repeat)? | Medium | Gazette copy (BNS and Schedule). | QLR opinion. | QLR | Open | Decision recorded. |
| RB-14 | LR-02(c), LR-05(b) | I | Sub-section-dependent advice: 117 bailability shown as depending on the sub-section; 316(3)–(5) flagged by keywords ("employee", "agent", etc.). | Medium | Registry rows; keyword lists. | QLR opinion on adequacy. | QLR | Open | Approach approved or change specified. |
| RB-15 | LR-04(c) | I | Whether Section 134 should be offered as an alternative when force is used on a person in an attempted theft. | Medium | BNS 134 and Schedule row (Gazette copy). | QLR opinion. | QLR | Open | Decision recorded. |
| RB-16 | LR-16 | I | All user-facing procedural templates (theft, robbery, CBT, grievous hurt, mischief, misappropriation, multi-offence, vague, non-penal). | High | Template text in `service.py`. | QLR review of each statement. | QLR | Open | Every template approved or a change specified. |
| RB-17 | LR-18 | I / S | Registry classifications for 14 sections, transcribed by the developer from the Gazette copy. They drive `is_cognizable`, `is_bailable` and 173(3) checks. | High | Registry; Gazette copy. | QLR confirmation; second copy. | QLR | Open | All 14 rows confirmed. |

## 5. Statutory-text and citation discrepancies

### 5.1 Confirmed against the single available Gazette copy (passage read manually)

| ID | Ref | Class | Blocker | Impact | Evidence available | Evidence needed | Resp. | Status | Closure condition |
|---|---|---|---|---|---|---|---|---|---|
| RB-18 | LR-01 | C | s.115(2): stored "section 120" vs Gazette "section 122". | High (frequently retrieved) | Both passages quoted in LR-01. | Second copy; approval to correct. | QLR or MNT | Open | Text confirmed and correction applied through the change protocol, or difference explained. |
| RB-19 | LR-02 | C | s.117(2) cross-reference ("sub-section (3)" vs "sub-section (2) of section 122"); s.117(4) missing "acting in concert", "or community", "similar". | High | Both passages in LR-02. | As RB-18. | QLR | Open | As RB-18. |
| RB-20 | LR-08 | C | s.351: "treating" vs "threatening"; word order "threatens by any means, another" vs "threatens another by any means". | Medium | LR-08. | As RB-18. | QLR or MNT | Open | As RB-18. |
| RB-21 | LR-03(a) | C | s.303 Explanation 2: "effects" vs "affects". | Low–Medium | LR-03. | As RB-18. | QLR | Open | As RB-18. |
| RB-22 | LR-24 (subset) | C | Cross-references read manually in the Gazette copy: s.71 (67 vs 70), s.89 (86 vs 88), s.148 (145 vs 147), s.199 (list differs), s.264 (257–259 vs 259–261), s.341 (336 vs 338). | Medium | LR-24 table; Gazette passages. | As RB-18. | MNT, QLR | Open | As RB-18. |
| RB-23 | LR-17 | C | Non-penal template cites "Section 2(22)"; the Gazette copy defines "movable property" at 2(21). | Medium (user-facing citation) | Gazette 2(21) passage. | Second copy. | MNT, QLR | Open | Citation corrected through the change protocol. |
| RB-24 | LR-28 | C | s.119 title: "illegal to an act" vs margin heading "illegal act". | Low | Gazette margin heading. | Second copy. | MNT | Open | Title corrected. |
| RB-25 | LR-04, LR-05, LR-06 | C for s.316 (read manually); S for s.304 and s.318 (automated only) | Minor wording: s.304 "moveable"/"movable"; s.316 illustration "a lakh"/"one lakh"; s.318 illustration "diamond"/"diamonds". | Low | Checklist items. | Second copy. | MNT | Open | Corrected or accepted as immaterial. |

### 5.2 Suspected (automated comparison only)

| ID | Ref | Class | Blocker | Impact | Evidence available | Evidence needed | Resp. | Status | Closure condition |
|---|---|---|---|---|---|---|---|---|---|
| RB-26 | LR-24 | S | Remaining cross-reference differences: s.2, 29, 30, 99, 122, 136, 155, 159, 186, 200, 211, 212, 237, 240, 249, 265, 339, 342. s.113 and s.167 are probably footnote noise (Act years). | Medium | Automated diff pairs (checklist LR-24). | Manual reading and second copy. | MNT, QLR | Open | Each record classified as error, noise or acceptable; errors corrected through the protocol. |
| RB-27 | LR-29, Appendix A.1 | S | 80 further records marked `differs_from_gazette_needs_review` (beyond the core offences and cross-reference records). Many are likely formatting or extraction artefacts. | Medium | `verification.evidence` per record. | Manual review per record. | MNT, QLR | Open | Every record reviewed and its outcome recorded. |
| RB-28 | LR-29, Appendix A.2 | S | 56 records marked `possibly_incomplete`. Some only reflect margin headings (s.97 checked; operative text matches). | Medium | Coverage figures per record. | Manual review. | MNT | Open | As RB-27. |
| RB-29 | LR-26 | S | 13 unverified punishment fields (s.70, 113, 118, 124, 125, 206, 211, 221, 222, 260, 263, 316, 323). Returned to API clients and shown to Gemini. | Medium | Automated non-match. | Manual review; second copy. | MNT, QLR | Open | Each field confirmed or corrected. |
| RB-30 | LR-27 | S | 63 records classified "no punishment clause" by automated pattern check. | Low | Pattern check. | Spot check. | MNT | Open | Spot check complete; exceptions corrected. |
| RB-31 | LR-07 | S | s.324 wording differences, mostly PDF artefacts. | Low | Automated diff. | Manual confirmation. | MNT | Open | Confirmed as immaterial or corrected. |

## 6. Schedule I classification conflicts

Scraped classification blocks are **not used** for procedural output. They matter only if the registry is extended or the blocks are relied on later.

| ID | Ref | Class | Blocker | Impact | Evidence available | Evidence needed | Resp. | Status | Closure condition |
|---|---|---|---|---|---|---|---|---|---|
| RB-32 | LR-19 | C | s.87: scraped block "Non-cognizable" vs Gazette copy "Cognizable". | Low today; High if registry extended | Gazette row; scraped block. | Second copy; QLR confirmation. | QLR | Open | Correct classification recorded; block corrected or discarded. |
| RB-33 | LR-20 | C | s.90(1)–(2): scraped "Non-cognizable" vs Gazette "Cognizable". | As RB-32 | As RB-32 | As RB-32 | QLR | Open | As RB-32. |
| RB-34 | LR-21 | C | s.276: scraped "Bailable" vs Gazette "Non-bailable". | As RB-32 | As RB-32 | As RB-32 | QLR | Open | As RB-32. |
| RB-35 | LR-22 | S | s.354, 355, 357 read by column position only (agree with scraped blocks). | Low | Positional reading. | Printed Schedule page. | MNT | Open | Confirmed from the printed page. |
| RB-36 | LR-23 | S | 195 scraped blocks never checked; their words remain in the BM25 index. | Low (outputs); retrieval effect unknown | Blocks flagged `not_checked_against_gazette`. | Decision on verify, discard or replace; re-benchmark if removed from index. | PO, MNT | Open | Decision recorded and implemented through the protocol. |

## 7. Provisional benchmark cases

Labels are unchanged. Proposed corrections are recorded in each case's `label_review` and have **not** been applied.

| ID | Case | Class | Open question | Impact | Evidence available | Evidence needed | Resp. | Status | Closure condition |
|---|---|---|---|---|---|---|---|---|---|
| RB-37 | BNS-BM-17 (LR-30) | I | Section 310 with two offenders; Section 311 "uses any deadly weapon". | Medium (metrics) | Statutory text; label review. | QLR labels. | QLR, ADJ | Open | Final labels recorded and applied through the protocol. |
| RB-38 | BNS-BM-20 (LR-31) | I | Bailability of attempted theft; Section 134 alternative. | Medium | As above | As above | QLR, ADJ | Open | As RB-37. |
| RB-39 | BNS-BM-21 (LR-32) | I | Attempted chain snatch: 62+304 vs 134; bailability. | Medium | As above | As above | QLR, ADJ | Open | As RB-37. |
| RB-40 | BNS-BM-22 (LR-33) | I | Attempt under 303 or 305; bailability. | Medium | As above | As above | QLR, ADJ | Open | As RB-37. |
| RB-41 | BNS-BM-28 (LR-34) | I | Section 305 for a garage; 331 sub-section. | Medium | As above | As above | QLR, ADJ | Open | As RB-37. |
| RB-42 | BNS-BM-30 (LR-35) | I | "Purana servant" (306); 305, 331; 115 vs 118; robbery via hurt while carrying away. | Medium | As above | As above | QLR, ADJ | Open | As RB-37. |
| RB-43 | BNS-BM-31 (LR-36) | I | 316 without entrustment; 303 vs 314; trespass provisions. This case alone accounts for the 12/32 → 11/32 procedural change. | Medium | As above | As above | QLR, ADJ | Open | As RB-37. |
| RB-44 | BNS-BM-45 (LR-37) | I | Section 305 (dwelling); 329 relevant or plausible. | Medium | As above | As above | QLR, ADJ | Open | As RB-37. |

## 8. Evaluation limitations

| ID | Ref | Class | Blocker | Impact | Evidence available | Evidence needed | Resp. | Status | Closure condition |
|---|---|---|---|---|---|---|---|---|---|
| RB-45 | Eval plan §1 | E | No independently sourced, legally reviewed test set. The 50-case benchmark was used during development; its "holdout" was previously inspected. | High | `independent_evaluation_plan.md` | New cases, double-labelled and adjudicated, sealed test split. | EL, QLR | Open | Final-test report in the plan's format. |
| RB-46 | Eval plan §8 | E | No recent genuine live Gemini results; `evaluation_report_live.json` (5 cases) is stale; Gemini behaviour is tested only with mocks. | High | Mocked tests; inference-status recording in the evaluator. | Approved live run on validation and test sets, reported separately from fallback and cached results. | EL, PO | Open | Live results published per the plan. |
| RB-47 | Eval plan §1, §7 | E | Current metrics are not interchangeable, and the planned metrics are not implemented (strict precision, abstention, per-offence procedural accuracy, serious-error tagging). | Medium | Metric documentation in evaluator and README. | Evaluator extension, built and tested on development data only. | MNT, EL | Open | Metrics implemented and tested. |
| RB-48 | Release readiness §6 | E | Fallback offence-prediction precision about 18.7% (synthetic development data); general sections (35, 97, 345, 43) dominate. | High (if fallback serves users) | Benchmark reports. | Independent evaluation; decision on fallback's role. | PO, EL | Open | Measured on the independent test set and accepted by PO. |
| RB-49 | — | P | Default Gemini model name unconfirmed. | Medium | Code default only. | Confirmation by an authorised operator (no API call made here). | MNT | Open | Model ID confirmed and recorded. |

## 9. Operational risks (not legal blockers, tracked for release)

| ID | Class | Item | Impact | Status | Closure condition |
|---|---|---|---|---|---|
| RB-50 | P | `bns_finetune_dataset.json`, `bns_scenarios_dataset.json` and `public/bns_rag_dataset.json` contain pre-migration defects. They are unused by the backend. | Low (unless used) | Open | Regenerated from the reviewed corpus, or deleted by decision. |
| RB-51 | P | `scrape_bns.py` extraction defects persist. Writes are guarded and go to staging only. | Low | Open | Scraper fixed, or retired by decision. |

## 10. Potential implementation defects (added 2026-10-21)

These come from `reports/section_173_3_boundary_impact.md` §3.2 (items I-1 and I-3).

**Class D** = potential implementation defect: Bandhoo's output contradicts its own stated rule or data, whatever the answer to any open legal question. Class D is used only in this section; the class definitions in §2 are unchanged.

The items are "potential" because confirming a defect and approving a fix both go through `reports/post_review_change_protocol.md`. **No fix has been implemented.** Proposals: `reports/section_173_3_remediation_proposal.md`. Queue entries: Q-16 and Q-17 in `reports/approved_correction_queue.md`.

| ID | Ref | Class | Blocker | Impact | Evidence available | Evidence needed | Resp. | Status | Closure condition |
|---|---|---|---|---|---|---|---|---|---|
| RB-52 | Impact I-1; Q-16 | D | Single-offence path (Gemini mode) tells the user that Section 173(3) is "legally INAPPLICABLE" when the section has **no registry entry**. Missing data is presented as a legal conclusion. | High (Gemini mode; any BNS section outside the 14 registry sections) | Code reading; offline probes, 2026-10-21 (BNS 308 and 329; §10.1) | Approved wording; regression tests (§10.1) | MNT, QLR, PO | Open | §10.1 closure criteria met and recorded |
| RB-53 | Impact I-3; RB-08.a; Q-17; Q-01 | D | Gemini text stating that DSP permission is to be given "within 14 days" reaches the user unchanged, with no corrective statutory note. | High (Gemini mode; single non-templated offence) | Code reading; offline probes, 2026-10-21 (BNS 304, 305, 329; §10.2) | QLR sign-off on Q-01 Step 1; decision on the passthrough guard; tests; live-evaluation evidence (§10.2) | MNT, QLR, PO, EL | Open | §10.2 closure criteria met and recorded |

### 10.1 RB-52: an unknown registry entry is reported as "legally INAPPLICABLE"

| Field | Content |
|---|---|
| Exact code location | **Where the condition is met:** `legal_engine/service.py`, `_single_offence_procedure`, lines 758–784. When `cites_173_3` is true and `check_bnss_173_3_eligibility` returns `eligible: False`, the generic `else` branch (lines 777–779) applies to a section with no registry entry. It takes the registry's reason (line 778) and sets "Procedure depends on verified Schedule I classification of the offence." (line 779). Lines 781–784 then return "Correction of procedural advice: Section 173(3) BNSS preliminary enquiry is legally INAPPLICABLE to Section {n} ({title}) because {reason}. {correct_proc}". **The reason itself** comes from `legal_engine/schedule_registry.py` lines 386–387: "…does not have a verified BNSS Schedule I entry in this registry. Section 173(3) BNSS applicability cannot be affirmed without verified statutory classification." Registry contents: `VERIFIED_SCHEDULE_I`, from line 87. |
| Trigger conditions | All must hold: (1) Gemini mode, with Gemini's recommendation longer than 20 characters and not starting "Prima facie" (line 759). (2) Exactly one supported candidate (score ≥ 0.5), with no section template (303, 309, 316, 117, 324) and not s.314 alone. (3) The section is outside the 14 registry sections (115, 117, 303, 304, 305, 306, 309, 310, 314, 316, 318, 324, 351, 352). (4) s.173(3) is cited in the narrative **or** in Gemini's text (lines 542–544). **Not affected:** fallback mode, and the multi-offence path. Both repeat the registry's hedged "cannot be affirmed" reason (boundary impact P-F). |
| Reproduction (offline, 2026-10-21; simulated Gemini text; no network) | Call `_audit_and_qualify_procedural_recommendation` with one `SectionPredictionItem`, with `is_cognizable` taken from `_determine_schedule_metadata`. (a) BNS 308; Gemini text "A preliminary enquiry under Section 173(3) BNSS may be held." (b) BNS 308; the narrative contains "Under Section 173(3) police must enquire first."; Gemini text "Register an FIR for extortion and investigate the demand." (c) BNS 329; the narrative cites s.173(3); Gemini text "Record the complaint of criminal trespass and investigate." |
| Observed output | (a) and (b): "Correction of procedural advice: Section 173(3) BNSS preliminary enquiry is legally INAPPLICABLE to Section 308 (Extortion) because BNS Section 308 does not have a verified BNSS Schedule I entry in this registry. Section 173(3) BNSS applicability cannot be affirmed without verified statutory classification.. Procedure depends on verified Schedule I classification of the offence." (c): the same for "Section 329 (Criminal trespass and house-trespass)". In (b) and (c), Gemini's own recommendation is discarded. |
| Expected safe behaviour | State that s.173(3) applicability **cannot be determined from the available registry data**. Draw no legal conclusion either way. Match the registry message and the multi-offence audit. Whether Gemini's discarded recommendation should also be shown is a reviewer question: if shown, it would be unaudited. |
| Potential user impact | A complainant may be told that a police preliminary enquiry is "legally INAPPLICABLE" for, e.g., extortion or criminal trespass. This is a categorical statement Bandhoo has no basis for. It could lead the person to dispute a lawful police step. In (b) and (c) they also lose the FIR advice. |
| Required regression tests | (1) **Fails before, passes after:** cases (a), (b) and (c) contain no "INAPPLICABLE" or "inapplicable", and do contain the approved "cannot be determined" wording. (2) **Unchanged-output checks** against outputs captured before the change: 305 (seven-year correction), 318 (conditional rows), 314 and 351 (non-cognizable), 304 (eligible, note appended), the robbery template, multi-offence 308 + 318 + 351, and fallback 308. No Gemini calls. |
| Approval requirements | **Path B** (`post_review_change_protocol.md` §1: Section 173(3) logic and template wording). QLR 1 and QLR 2 in agreement (or ADJ), MNT, and PO (user-facing advice). The legal question is narrow: is the "cannot be determined" statement acceptable? It adds no interpretation. |
| Closure criteria | Approved wording implemented as a single-issue change. The regression test is recorded failing before and passing after. Targeted and full offline suites pass with Gemini disabled. The fallback benchmark comparison shows no change (gate 7). Unintended-effects review recorded (gate 8). Change record with rollback (gate 9). Status changed by the approvers. |
| Related | Boundary impact I-1. Independent of the seven-year question (RB-09). |

### 10.2 RB-53: Gemini's "DSP permission … within 14 days" wording passes through without a statutory note

| Field | Content |
|---|---|
| Exact code location | **Guard:** `legal_engine/service.py` lines 785–788. When s.173(3) is cited and the offence is eligible, the statutory note (`BNSS_173_3_PROCEDURE_TEXT` and caveat) is appended (line 787) **only if** Gemini's text lacks "173(3)", or lacks "deputy superintendent"/"dsp", or lacks "fourteen"/"14". Otherwise Gemini's text is returned unchanged (line 788). When s.173(3) is not cited at all, lines 760–787 are skipped and Gemini's text is returned unchanged. **Source of the phrasing:** `legal_engine/llm_client.py` `SYSTEM_PROMPT` line 59: "…prior permission from an officer not below the rank of Deputy Superintendent of Police (DSP) within 14 days…" (RB-08.a; Q-01). |
| Trigger conditions | Gemini mode, and a single supported offence with no section template. **Route (a):** s.173(3) cited, offence eligible, and Gemini's text contains DSP and 14/fourteen. Among non-templated registry sections, only BNS 304 is currently eligible. **Route (b):** s.173(3) not cited anywhere, any non-templated offence (registered or not), and Gemini's text describes the timing without the literal "173(3)". |
| Reproduction (offline, 2026-10-21; simulated Gemini text) | (a) BNS 304, narrative "A man snatched my phone and ran away.", Gemini text copying prompt line 59 → **returned verbatim**. (b) BNS 305 and BNS 329, Gemini text "Police may hold a preliminary enquiry with prior permission from the DSP within 14 days before registering an FIR." → **returned verbatim**. For 305 this also bypasses Bandhoo's own seven-year audit. Control: BNS 304, cited, without DSP or 14 → statutory note appended (guard works in that case). |
| Expected safe behaviour | User-facing text must not present the fourteen-day period as a limit on DSP permission. Where Gemini's text refers to a preliminary enquiry or DSP permission, the statutory wording or an approved correction should accompany or replace it. Out-of-range and unverified offences should get the existing audit whether or not the literal "173(3)" appears. The precise behaviour is for reviewers. |
| Potential user impact | The user may be told that DSP permission must be given within 14 days, or be left without the actual time frame for the enquiry. In route (b), a seven-year or unregistered offence can receive preliminary-enquiry advice that Bandhoo's own rule would not give. |
| Required regression tests | (1) **Prompt-content test**, fails before and passes after Change B: no match for `permission[^.\n]{0,120}within (14\|fourteen) days` in `SYSTEM_PROMPT`; "fourteen days" appears within the preliminary-enquiry clause. (2) **If a guard change is approved:** routes (a) and (b) produce the statutory note or an approved correction. (3) **Unchanged:** the control case, and `tests/test_inspection_regressions.py` lines 248–255. |
| Approval requirements | Prompt sentence: **path B** (Q-01 Step 1): QLR sign-off, MNT, and PO (user-facing). Guard change: a **separate path B** change. It changes s.173(3) logic and is **not** part of the current remediation proposal. |
| Closure criteria | Q-01 Step 1 implemented after sign-off, **and** either (i) an approved guard change with passing tests, or (ii) a recorded QLR and PO decision that the prompt correction alone is sufficient, supported by an approved live evaluation (Q-15) in which the phrasing no longer appears. Offline suites pass; gate 7 comparison recorded; status changed by the approvers. |
| Related | RB-08, RB-08.a, Q-01. Boundary impact I-3. Independent of the seven-year question (RB-09) and of the Maharashtra amendment (RB-03; status UNKNOWN). |

## Appendix A. Outstanding blockers by priority

1. **Legal review of core outputs:** RB-06 to RB-11, RB-16, RB-17. These decide what users are told about the theft proviso, 173(3), multi-offence procedure and classification.
2. **Sources:** RB-02, RB-03, then confirmation of the confirmed-in-one-copy discrepancies affecting frequent offences: RB-18, RB-19, RB-20, RB-23.
3. **Independent evaluation:** RB-45 and RB-46.
4. **Provisional benchmark labels:** RB-37 to RB-44.
5. **Remaining corpus and schedule items:** RB-12 to RB-15, RB-21, RB-22, RB-24 to RB-36.
6. **Potential implementation defects (added 2026-10-21):** RB-52 and RB-53 (§10). Each is independent of the seven-year question (RB-09) and can be reviewed separately; see `reports/section_173_3_remediation_proposal.md`.

## Appendix B. Baseline SHA-256 Hashes & Controlled Refresh

### Historical Baseline (2026-10-20, first 16 hex characters)
The initial baseline recorded 17 key files before the complaint engine and trust/safety integration.

| File | Hash | Note |
|---|---|---|
| `legal_engine/__init__.py` | `d313c8e4c45d51df` | Original baseline |
| `legal_engine/amounts.py` | `35aeeeb80b4d3f3e` | Original baseline |
| `legal_engine/corpus.py` | `d5be04d2059f2dba` | Original baseline |
| `legal_engine/corpus_guard.py` | `27eb7bd2613ca296` | Original baseline |
| `legal_engine/llm_client.py` | `99f7f3fce32cc217` | Original baseline |
| `legal_engine/retrieval.py` | `6aef165b2df9f75f` | Original baseline |
| `legal_engine/schedule_registry.py` | `6f0af12b994706d7` | Original baseline |
| `legal_engine/schemas.py` | `8ce3535987fab323` | Original baseline |
| `legal_engine/service.py` | `a64d55fe2015f6fe` | Original baseline |
| `legal_engine/synonyms.py` | `4a8a830fec0ac0b0` | Original baseline |
| `main.py` | `54ecd10e5097b1ad` | Pre-LangGraph baseline |
| `scrape_bns.py` | `7e5c4440ff0a1d0f` | Original baseline |
| `benchmark/evaluate_benchmark.py` | `7a23da466d8ca567` | Original baseline |
| `benchmark/build_dataset.py` | `a736cc4c9be2fd05` | Original baseline |
| `bns_rag_dataset.json` | `7c7e3322b277e8bd` | Original baseline |
| `benchmark/bns_synthetic_benchmark_50.json` | `36f2e00dc517fe03` | Original baseline |
| Pre-migration backup (`reports/backups/bns_rag_dataset.pre_integrity_migration_2026-10-20.json`) | `d053ce3de31ef17d` | Unchanged, read-only |

### Refreshed Controlled Baseline: Record BR-2026-10-21-01 (Checkpoint 6)
Reconciled after Checkpoint 2 (deterministic defect fixes) and Checkpoint 5 (CORS, error sanitization, dependency lockfile, and ESLint remediation).

**1. Reconciled Core Production Files:**
| File | 2026-10-20 Hash | 2026-10-21 Hash | Provenance & Rationale |
|---|---|---|---|
| `main.py` | `54ecd10e5097b1ad` | `d848442f7e7632f5` | Reconciled: LangGraph integration (`ea8b6b43cd54e2f1`), hardened CORS whitelist, and top-level PII exception handler. |
| `requirements-lock.txt` | *(new)* | `e893b3d0c94a3245` | Pinned exact production runtime dependencies. |
| `src/App.jsx` | `0a2001554785f3a0` | `ce4187a92edd397c` | Trust/safety integration, configurable `API_BASE_URL`, and 0-warning ESLint refactor. |

**2. Complaint Engine Components (Added Row Group):**
| Component | Hash (first 16 hex chars) | Role |
|---|---|---|
| `complaint_engine/__init__.py` | `bf18be70cd69f606` | Package initialization |
| `complaint_engine/checks.py` | `56427e31a405edd9` | Contradiction, loss & unsupported checks |
| `complaint_engine/draft.py` | `6e4bda6ecc23ba29` | Verbatim narrative drafting & section mapping |
| `complaint_engine/extraction.py` | `fd3f7ec9eff770e7` | Deterministic entity & fact extraction |
| `complaint_engine/graph.py` | `18798991921aaa61` | LangGraph state graph & review workflow |
| `complaint_engine/jurisdiction.py` | `94576e146bd1b6b2` | Polygon containment & 100m buffer logic |
| `complaint_engine/models.py` | `adf946d8cf835faf` | Pydantic complaint models & schemas |

**3. Unchanged Baseline Invariants (100% Identity Preserved):**
All 16 other baseline files match their original 2026-10-20 hashes exactly (`legal_engine/*` [10 files], `scrape_bns.py`, `benchmark/evaluate_benchmark.py`, `benchmark/build_dataset.py`, `bns_rag_dataset.json`, `benchmark/bns_synthetic_benchmark_50.json`, and pre-migration backup).

*Note: All blockers (RB-01 through RB-53) remain OPEN. Refreshing the checksum baseline verifies technical and operational state integrity without prematurely closing substantive legal or external review blockers.*
