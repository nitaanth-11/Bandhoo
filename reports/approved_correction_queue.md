# Bandhoo Correction Queue

**Prepared:** 2026-10-21. **For:** the project owner (PO), qualified Indian criminal-law reviewers (QLR), the adjudicator (ADJ), the second checker (SC), the evaluation lead (EL) and Bandhoo maintainers (MNT).

**Despite the file name, nothing in this queue is approved.** Every entry is a **proposal only** and is currently **Blocked**. No fix has been implemented. Bandhoo remains internal-testing-only and is not legally validated.

Each entry needs the evidence and approvals in `reports/post_review_change_protocol.md` and `reports/legal_review_execution_checklist.md` (Stages 1–3) before it may move to "Approved". Queue IDs (`Q-xx`) are local to this document; each is mapped to existing RB, LR and remediation-plan IDs.

## Sources inspected for this queue

| Code | Document | Provenance | Inspected | Scope and limits |
|---|---|---|---|---|
| G-BNS | BNS 2023 (No. 45 of 2023), Gazette of India Extraordinary, 25 Dec 2023 | PRS-hosted PDF | 2026-10-20 and 2026-10-21 | Single copy. Central legislation. |
| G-BNSS | BNSS 2023 (No. 46 of 2023), incl. First Schedule, same date | PRS-hosted PDF | Same | Single copy. Central legislation. |
| MH-LC6-P | Maharashtra L.C. Bill No. VI of 2026, "A Bill to amend the Bharatiya Nagarik Suraksha Sanhita, 2023, in its application to the State of Maharashtra", "(As passed by the Legislative Council on the 24th March, 2026.)" | Maharashtra Legislature Secretariat website (mls.org.in), 9-page PDF | 2026-10-21 | **Maharashtra bill, not an Act.** Assent, Act number and commencement not found. Includes an extract of the current BNSS s.173(3) preamble and clause (i). |
| MH-LC6-I | Same bill as introduced (18 March 2026), published in the Maharashtra Government Gazette Extraordinary, Part V-A | PRS-hosted PDF | 2026-10-21 | Bill as introduced. |
| MH-LC17 | Maharashtra L.C. Bill No. XVII of 2026, same short title, "introduced in the Maharashtra Legislative Council on the 3rd July 2026", published under the authority of the Governor | PRS-hosted PDF | 2026-10-21 | Bill as introduced; relationship to L.C. Bill VI unknown. |
| SO-2790 | S.O. 2790(E), 16 July 2024, Ministry of Law and Justice (Legislative Department), Gazette of India Extraordinary Part II, Sec. 3(ii) | egazette.gov.in | 2026-10-21 | Central notification under s.8 of the General Clauses Act: references to the IPC, CrPC and Indian Evidence Act in other laws are read as references to the BNS, BNSS and BSA. **Not a copy of BNS or BNSS text.** |
| CPA-PRS | Consumer Protection Act, 2019 (No. 35 of 2019) | PRS-hosted PDF | 2026-10-20 | As enacted; single copy. |
| LMA-PRS | Legal Metrology Act, 2009 (No. 1 of 2010), [13th January, 2010] | PRS-hosted PDF | 2026-10-21 | As enacted; amendments and rules (including any packaged-commodity rules) not inspected. |
| LK-MPHC | *Lalita Kumari v. Govt. of U.P.*, Manupatra print MANU/SC/1166/2013 | mphc.gov.in (TLS unverified) | 2026-10-20 | Third-party reporter print. |

**Not obtained:**
- India Code copies of the BNS, BNSS, CPA and Legal Metrology Act (HTTP 403 or error page on 2026-10-20 and again on 2026-10-21);
- any second full copy of the BNS or BNSS;
- the Supreme Court or SCC copy of *Lalita Kumari*;
- Maharashtra assent or commencement records;
- any central amending Act after 25 Dec 2023, of which none was found. **That is not evidence that none exists.**

Central legislation, Maharashtra instruments, judicial decisions and administrative notifications are kept separate in the entries below.

## Queue summary

| Queue ID | Item | Existing IDs | Classification | Priority | Status |
|---|---|---|---|---|---|
| Q-01 | BNSS 173(3) timing language (prompt and templates), including the Maharashtra bills | RB-08.a, RB-08, RB-03; P0-1 | Transcription discrepancy (prompt); **jurisdiction-specific amendment risk (new)**; interpretation for the rest | P0 | Blocked |
| Q-02 | BNS 303(2) proviso wording in the prompt | RB-06.a, RB-06, RB-07; P0-2 | Legal interpretation (prompt states it as settled) | P0 | Blocked |
| Q-03 | Movable-property cross-reference "2(22)" | RB-23, LR-17; P0-3 | Transcription discrepancy (citation) + legal interpretation (accompanying statement) | P0 | Blocked |
| Q-04 | Forgery wording "Section 336/338" | LR-17.a; P0-4 | Suspected discrepancy (label vs content) + procedural advice | P0 | Blocked |
| Q-05 | Consumer Commission referral wording | RB-04.a; P0-5 | Procedural advice | P0 | Blocked |
| Q-06 | "Legal Metrology Department under the Consumer Protection Act, 2019" | RB-04.b; P0-5 | Transcription discrepancy (attribution) + procedural advice | P0 | Blocked |
| Q-07 | Section 173(3) examples in the prompt (324, 103, 64) | RB-16.a; P1-4 | Suspected discrepancy (324); consistent with single copy (103, 64) | P1 | Blocked |
| Q-08 | Stored text: s.115, 117(2), 117(4), 303, 304, 316, 318, 351 | RB-18–RB-21, RB-25; LR-01–LR-08; P1-1 | Transcription discrepancy (single copy); interpretation where elements change | P1 | Blocked |
| Q-09 | s.324 bands vs Schedule I | RB-12, LR-15; P1-2 | Legal interpretation (conflict within the copy) | P1 | Blocked |
| Q-10 | Punishment fields and earlier corrections | RB-29, RB-05, RB-30; LR-25–LR-27 | Suspected discrepancy (single copy) | P1 | Blocked |
| Q-11 | Schedule I: 14 registry rows; s.87, 90, 276, 354, 355, 357 | RB-17, RB-32–RB-35; LR-18–LR-22; P1-3, P1-4 | Legal interpretation (registry); transcription discrepancy (scraped blocks) | P1 | Blocked |
| Q-12 | Advice templates generally | RB-16, LR-16; P1-4 | Procedural advice | P1 | Blocked |
| Q-13 | Remaining corpus records | RB-22, RB-24–RB-28, RB-31; LR-24, LR-28, LR-29; P1-5 | Transcription discrepancy (RB-22, RB-24); suspected (rest) | P1 | Blocked |
| Q-14 | Eight provisional benchmark cases | RB-37–RB-44; LR-30–LR-37; P2-1 | Legal interpretation (labels) | P2 | Blocked |
| Q-15 | Independent evaluation | RB-45–RB-48; P2-2, P2-3 | Evaluation issue | P2 | Blocked |
| Q-16 | Unknown registry entry reported as s.173(3) "legally INAPPLICABLE" (single-offence path) | RB-52 (added 2026-10-21) | Potential implementation defect (procedural advice) | P0 | Blocked |
| Q-17 | Gemini "DSP permission … within 14 days" wording passes through without a statutory note | RB-53, RB-08.a; depends on Q-01 Step 1 (added 2026-10-21) | Potential implementation defect (procedural advice) | P0 | Blocked |

## Common requirements for every entry

These apply to every entry and are not repeated below unless an entry adds something.

- **Benchmark comparison (protocol gate 7):**
  - save the current `benchmark/evaluation_report_fallback.json`;
  - run `python benchmark/evaluate_benchmark.py --mode fallback`;
  - compare case by case with identical metric definitions, with and without the 8 provisional cases;
  - explain every changed prediction;
  - for corpus-text changes, add an ablation reverting only the change;
  - **never change labels to improve metrics.**
  Prompt-only changes cannot affect the fallback benchmark. Their effect on live output can only be measured in an approved live evaluation (Q-15).
- **Rollback (gate 9):**
  - take a fresh snapshot and manifest before each implementation batch (the 2026-10-20 baseline in `reports/baseline_and_rollback_audit.md` predates later reports);
  - code: restore files from that snapshot, verifying hashes;
  - corpus: restore the verified backup created by the migration;
  - record paths and SHA-256 hashes in the change record.
- **Tests (gates 5–6):** a regression test that fails before and passes after; targeted tests; the full offline suite with Gemini disabled. Any changed expectation in an existing test must be justified in the change record.

---

## P0 entries

### Q-01. BNSS Section 173(3) timing language

| Field | Content |
|---|---|
| IDs | RB-08.a (prompt timing); RB-08 (wording and discretion); RB-03 (amendments); remediation plan P0-1. **New in this queue:** Maharashtra amendment bills affecting 173(3)(i), recorded here under RB-03 (amendment status). |
| Affected locations | `legal_engine/llm_client.py` `SYSTEM_PROMPT`, line 59: "It is discretionary with prior permission from an officer not below the rank of Deputy Superintendent of Police (DSP) within 14 days, or police proceed directly with investigation when a prima facie case exists." Also every place stating the fourteen-day period: `legal_engine/schedule_registry.py` `BNSS_173_3_PROCEDURE_TEXT` (line 28, "within a period of fourteen days"); `legal_engine/service.py` docstring (line 530) and the templates that embed the constant (`_theft_procedure_note`, `_cbt_procedure_note`, `_single_offence_procedure`, `_audit_173_3_claims`). Tests asserting the wording: `tests/test_inspection_regressions.py` (line 228: `"fourteen days" in text`; lines 252–254: no "permission … within 14 days"). |
| Current behaviour | Service templates attach the fourteen days to the preliminary enquiry. The prompt attaches "within 14 days" to DSP permission. Gemini's own recommendation text is passed to users for single non-templated offences (`service.py` lines 759–788). All texts state fourteen days without any jurisdictional qualification. |
| Evidence | **Central text:** G-BNSS 173(3)(i): "proceed to conduct preliminary enquiry to ascertain whether there exists a prima facie case for proceeding in the matter within a period of fourteen days". **Second, official-host reproduction** of the same preamble and clause (i): extract printed in MH-LC6-P (Maharashtra Legislature Secretariat); wording identical; limb (ii) elided. **Maharashtra instruments (bills only):** MH-LC6-I/P clause 6 and MH-LC17 clause 7: "In section 173 of the said Sanhita, in sub-section (3), in clause (i), for the words "fourteen days" the words "six weeks" shall be substituted." MH-LC17 Statement of Objects (vi): "The time period for conducting preliminary enquiry to ascertain whether there exists a prima-facie case for proceeding in cognizable cases is proposed to be increased from fourteen days to six weeks". **Status of the Maharashtra amendment: unknown** (passed by the Legislative Council on 24 March 2026 per MH-LC6-P; a second bill introduced on 3 July 2026; no assent or commencement found). **Judicial:** LK-MPHC para 111(vii) (fifteen days generally, under CrPC). Not used to decide anything. |
| Classification | Prompt: **transcription discrepancy** (prompt vs statutory structure, now in two official-host reproductions). Jurisdiction: **source gap / amendment risk** (Maharashtra). Start point, consequence of delay, and the relationship with *Lalita Kumari*: **legal interpretation**, unresolved (RB-08, RB-11). |
| User-facing risk | High for Mumbai users. (1) The prompt may tell users DSP permission must come within 14 days. (2) If the Maharashtra amendment is or becomes law, every Bandhoo statement of "fourteen days" would be wrong in Maharashtra. |
| Required source verification | (a) Confirm the BNSS 173(3) text in a second full official copy (S1-2). (b) Determine whether the Bharatiya Nagarik Suraksha Sanhita (Maharashtra Amendment) Act, 2026 received assent, its Maharashtra Act number and its commencement date, from the Maharashtra Government Gazette or Law and Judiciary Department (S1-3). (c) Determine which bill text was enacted (L.C. Bill VI or XVII). |
| Required approvals | Prompt alignment: QLR sign-off (path B) + MNT. Any jurisdiction-specific wording: QLR + PO. |
| Proposed minimal change (proposal only) | Step 1 (independent of the Maharashtra question): rewrite prompt line 59 to mirror the statutory structure. Prior DSP permission governs the choice between (i) a preliminary enquiry, within the period stated in clause (i), and (ii) investigation where a prima facie case exists. Reuse `BNSS_173_3_PROCEDURE_TEXT`. Step 2 (only after (b) is answered): if a Maharashtra amendment is in force, add a jurisdiction note approved by the QLR (for example, that the period differs in Maharashtra from a stated date), updating the constant, templates and tests together. **Do not** change the period on the strength of a bill. |
| Regression tests | New prompt-content test (none exists today): no "permission … within 14 days" pattern; the constant is present. If Step 2 proceeds: tests that the period statement matches the approved jurisdiction rule, and revision of `tests/test_inspection_regressions.py` line 228 with justification. |
| Acceptance criteria | Prompt matches the statutory structure; all tests pass; fallback benchmark unchanged (prompt not used in fallback); the jurisdiction decision recorded with its source, or explicitly recorded as pending. |
| Rollback | Restore `llm_client.py` (and, for Step 2, `schedule_registry.py`, `service.py`, tests) from the pre-change snapshot. |
| Dependencies and blocker status | **Blocked:** reviewers unassigned; Step 1 awaits QLR sign-off; Step 2 awaits S1-3 enactment evidence. |

### Q-02. BNS Section 303(2) proviso wording in the Gemini prompt

| Field | Content |
|---|---|
| IDs | RB-06.a; RB-06, RB-07; LR-09, LR-10; P0-2 |
| Affected location | `legal_engine/llm_client.py` `SYSTEM_PROMPT`, lines 65–67: "If property value is ₹5,000 or more, or repeat offender: Cognizable and non-bailable…"; "If property value is under ₹5,000, first-time offender, and property restored/returned: Section 303(2) proviso applies (punishable with community service; classified as non-cognizable and bailable under BNSS Schedule I, requiring procedure under Section 174 BNSS)." Gemini reasoning surfaces through `predictions[].reasoning` (`service.py` line 1217). |
| Current behaviour | The prompt states the proviso outcome as settled. Service logic (`_determine_schedule_metadata`, `_theft_procedure_note`) leaves classification unknown below Rs 5,000 and explains both pathways. A response can therefore contain contradictory statements. |
| Evidence | G-BNS 303(2) proviso ("a person is convicted for the first time"); G-BNSS rows (the "less than 5,000 rupees" row does not mention first conviction). Single copies; no second copy yet. |
| Classification | **Legal interpretation** (unresolved), surfaced as an internal inconsistency confirmed by code inspection. |
| User-facing risk | High: a user may be told a theft is non-cognizable and NCR-only when that cannot be determined from a complaint, discouraging an FIR. |
| Required source verification | S1-1 (303(2)), S1-2 (Schedule rows), S1-3 (amendments). |
| Required approvals | QLR (path B), MNT, PO. |
| Proposed minimal change (proposal only) | Replace lines 66–67 with neutral instructions: state both Schedule I rows as written; state that the BNS proviso also requires a first conviction, which cannot be established from a complaint; state that FIR-stage treatment is unresolved; never infer first conviction or prior record from narrative wording; never state that the proviso "applies". **No answer on FIR-stage cognizability or valuation is encoded.** |
| Regression tests | Prompt-content test (no "proviso applies"; uncertainty wording present). Service test with a mocked Gemini payload asserting "proviso applies; non-cognizable": metadata stays `None` and both pathways remain. Existing proviso tests stay green. |
| Acceptance criteria | No settled-proviso statement remains in the prompt; QLR records that no interpretation was encoded. |
| Rollback | Restore `llm_client.py`. |
| Dependencies and blocker status | **Blocked:** QLR unassigned. The substantive RB-06/RB-07 decisions remain open and are not required for this neutralising change. |

### Q-03. Movable-property cross-reference

| Field | Content |
|---|---|
| IDs | RB-23, LR-17; P0-3 |
| Affected locations | `legal_engine/service.py` `_build_non_penal_response`: docstring line 1014 and response text line 1035 ("Under Section 303 read with Section 2(22) of the BNS, 2023, penal offences against property strictly apply to corporeal movable property; intangible concepts … cannot be the subject of penal theft or robbery."). Test encoding the citation: `tests/test_adversarial_grievance_audit.py` lines 70, 81–82 (`assert "2(22)" in action`). |
| Current behaviour | Every intangible or career-grievance response cites 2(22). |
| Evidence | G-BNS: "(21) "movable property" includes property of every description, except land…"; "(22) "number".—…". Single copy; no second copy yet. |
| Classification | Citation: **transcription discrepancy** (single copy). The "intangible concepts … cannot be the subject of penal theft" sentence: **legal interpretation**. |
| User-facing risk | Medium: a wrong citation in deterministic output shown in both Gemini and fallback modes; possible overstatement of the law on intangibles. |
| Required source verification | S1-1: confirm the clause number in a second copy. |
| Required approvals | (a) Citation: MNT + SC (path A). (b) Sentence: QLR (path B). |
| Proposed minimal change (proposal only) | (a) Replace "2(22)" with "2(21)" at lines 1014 and 1035; change the test assertion to "2(21)" with a gate-6 justification (the test encoded the discrepancy). (b) Change the intangible-property sentence only as the QLR specifies. |
| Regression tests | Updated `test_scenario_3_workplace_grievance_insufficient_facts` ("2(21)" present, "2(22)" absent); a test restricting template "Section 2(n)" citations to an approved list. |
| Acceptance criteria | Second-copy confirmation recorded; tests pass; non-penal gate fires on the same cases as before. |
| Rollback | Restore `service.py` and the test file. |
| Dependencies and blocker status | **Blocked:** S1-1 not obtained (India Code blocked; no other official full copy found). |

### Q-04. Forgery wording

| Field | Content |
|---|---|
| IDs | LR-17.a; P0-4 |
| Affected location | `legal_engine/service.py` `_build_non_penal_response`, line 1039: "…criminal breach of trust (Section 316), cheating (Section 318), forgery of records (Section 336/338), or criminal intimidation (Section 351)…" |
| Current behaviour | Workplace or intangible grievances are pointed to "forgery of records (Section 336/338)". |
| Evidence | G-BNS 336(1) concerns false documents or false electronic records; G-BNS 338 concerns valuable securities, wills, authority to adopt, etc. A margin heading on forgery of Court records or public registers appears among ss.337–341 in the extraction; its section was not confirmed. Sections 336–340 not read in full. |
| Classification | **Suspected discrepancy** (label vs content); correct scope is **procedural advice / legal interpretation**. |
| User-facing risk | Medium: a complainant may be pointed to an inapplicable provision. |
| Required source verification | S1-1: ss.336–340 read in full in a second copy. |
| Required approvals | Confirm the intended scope (MNT + QLR); QLR approval of wording (path B). |
| Proposed minimal change (proposal only) | After scope confirmation, either cite only the QLR-confirmed provision(s), or remove section numbers ("forgery-related offences, subject to the facts"). No other template text changes. |
| Regression tests | Test that sections cited in the non-penal template are from an approved list and exist in the corpus with matching titles. |
| Acceptance criteria | QLR-approved wording; tests pass. |
| Rollback | Restore `service.py`. |
| Dependencies and blocker status | **Blocked:** S1-1; QLR unassigned. |

### Q-05. Consumer Commission referral wording

| Field | Content |
|---|---|
| IDs | RB-04.a; P0-5 |
| Affected location | `legal_engine/service.py` `_build_non_penal_response`, consumer-pricing text (lines 1018–1028): "…For retail overcharging or pricing grievances without criminal acts, recourse lies before the Consumer Disputes Redressal Commission or Legal Metrology Department under the Consumer Protection Act, 2019." Test constraint: `tests/test_adversarial_grievance_audit.py` line 65 (`"consumer protection act" in res.recommended_action.lower()`). |
| Current behaviour | Every "daylight robbery"-style pricing complaint gets this referral. |
| Evidence | CPA-PRS: ss.28(1), 42(1), 53(1) establish District, State and National Consumer Disputes Redressal Commissions. s.2(6)(iv) defines a complaint including that a trader "has charged … a price in excess of the price— (a) fixed by or under any law…; (b) displayed on the goods or any package…; (c) displayed on the price list…; (d) agreed between the parties". As enacted; no second copy; amendments not checked. |
| Classification | **Procedural advice** (appropriateness of the referral; scope narrower than "high prices"). |
| User-facing risk | Medium: users with merely high prices may be told they have a consumer remedy. |
| Required source verification | S1-6: second copy of the CPA and amendments or rules. |
| Required approvals | QLR (path B), MNT, PO. |
| Proposed minimal change (proposal only) | Keep the Act name. Qualify the Commission sentence to the s.2(6)(iv) ground (a price above one fixed by law, displayed or agreed). Decided together with Q-06. |
| Regression tests | Existing line-65 assertion retained; new assertion that the qualifier is present. |
| Acceptance criteria | QLR-approved wording; the non-penal gate fires on the same cases. |
| Rollback | Restore `service.py`. |
| Dependencies and blocker status | **Blocked:** S1-6 (India Code blocked); QLR unassigned. |

### Q-06. Legal Metrology attribution

| Field | Content |
|---|---|
| IDs | RB-04.b; P0-5 |
| Affected location | Same text as Q-05: "…or Legal Metrology Department under the Consumer Protection Act, 2019." |
| Evidence | CPA-PRS: no occurrence of "Legal Metrology". LMA-PRS (inspected 2026-10-21): the Legal Metrology Act, 2009 (No. 1 of 2010) provides in s.14(1) that "The State Government may, by notification, appoint a Controller of legal metrology, …" and in s.18 for "Declarations on pre-packaged commodities", including that "(2) Any advertisement mentioning the retail sale price of a pre-packaged commodity shall contain a declaration as to the net quantity…". The Act does not mention the Consumer Protection Act. Rules prescribing declarations, and amendments to the Act, were not inspected. |
| Classification | **Transcription discrepancy** in the attribution (the Legal Metrology authority is not created by the CPA). Whether any Legal Metrology referral is appropriate for these narratives: **procedural advice** for the QLR. |
| User-facing risk | Medium: users are directed to an authority under the wrong statute. |
| Required source verification | S1-7 continued: the current (amended) Legal Metrology Act and relevant rules; confirmation of the Maharashtra authority's name. |
| Required approvals | QLR (path B), MNT, PO. |
| Proposed minimal change (proposal only) | Remove "or Legal Metrology Department" from the CPA sentence. If the QLR wants a Legal Metrology mention, add it as a separate sentence attributed to the Legal Metrology Act, 2009, limited to the matters the QLR confirms (e.g. packaged-commodity price declarations), with wording approved by the QLR. |
| Regression tests | Test that "Legal Metrology" is not attributed to the Consumer Protection Act; if a mention is kept, that it names the approved statute. |
| Acceptance criteria | As Q-05. |
| Rollback | Restore `service.py`. |
| Dependencies and blocker status | **Blocked:** amended Act and rules not inspected; QLR unassigned. |

---

## P1 entries

### Q-07. Section 173(3) examples in the prompt

| Field | Content |
|---|---|
| IDs | RB-16.a; P1-4 |
| Affected location | `legal_engine/llm_client.py` `SYSTEM_PROMPT` lines 62–63: "NEVER recommend Section 173(3) for offences punishable with less than 3 years (e.g. Hurt Sec 115, Mischief Sec 324, Criminal Intimidation Sec 351)"; "…offences punishable with 7 years or more (such as Robbery Sec 309, Murder Sec 103, Dacoity Sec 310, Rape Sec 64)…" |
| Evidence | G-BNS/G-BNSS (single copies): s.103(1) "death or imprisonment for life", Schedule row 103(1) Cognizable, Non-bailable, Court of Session; s.64(1) rigorous imprisonment "not … less than ten years" up to life, row 64(1) Cognizable, Non-bailable, Court of Session; s.324(5)–(6) up to five years, rows Cognizable. |
| Classification | s.324 example: **suspected discrepancy** (sub-section dependent). s.103, s.64 examples: consistent with the single copy. |
| User-facing risk | Low–medium: a cognizable mischief causing large loss could be mis-steered. |
| Required source verification / approvals | S1-2; QLR (path B). |
| Proposed minimal change (proposal only) | Remove "Mischief Sec 324" from the under-3-years examples, or qualify it as "324(2)–(4)". |
| Regression tests / acceptance | Prompt-content test; QLR approval. |
| Rollback; status | Restore `llm_client.py`. **Blocked** (QLR unassigned). |

### Q-08. Stored statutory text of BNS 115, 117(2), 117(4), 303, 304, 316, 318, 351

| Sub-ID | IDs | Location (`bns_rag_dataset.json`, `text` field) | Current stored wording | Evidence (G-BNS, single copy) | Classification | Path |
|---|---|---|---|---|---|---|
| Q-08a | RB-18 / LR-01 | record 115 | "sub- section (1) of section 120" | "sub-section (1) of section 122" | Transcription discrepancy | A |
| Q-08b | RB-19 / LR-02 | record 117 | "except in the case provided for by sub-section (3)" | "sub-section (2) of section 122" | Transcription discrepancy | B (element) |
| Q-08c | RB-19 / LR-02 | record 117 | "When grievous hurt of a person is caused by a group of five or more persons on the ground of his, race, caste, … or any other ground" | "When a group of five or more persons acting in concert, causes grievous hurt to a person on the ground of his race, caste or community, … or any other similar ground" | Transcription discrepancy | B (element) |
| Q-08d | RB-21 / LR-03 | record 303 | Explanation 2 "effects the severance" | "affects the severance" | Transcription discrepancy | A (QLR if meaning matters) |
| Q-08e | RB-25 / LR-04 | record 304 | "any moveable property" | "any movable property" | Transcription discrepancy | A |
| Q-08f | RB-25 / LR-05 | record 316 | illustration "remits a lakh of rupees" | "remits one lakh of rupees" | Transcription discrepancy | A |
| Q-08g | RB-25 / LR-06 | record 318 | illustration "pledging as diamond articles" | "pledging as diamonds articles" | Transcription discrepancy | A |
| Q-08h | RB-20 / LR-08 | record 351 | "threatens by any means, another"; "by treating to cause death" | "threatens another by any means"; "by threatening to cause death" | Transcription discrepancy | B (element) |

| Field | Content (all sub-items) |
|---|---|
| User-facing risk | Medium: Gemini reasons over wrong cross-references and incomplete elements. Procedural metadata comes from the registry and is unaffected. |
| Required source verification | S1-1 (second full copy) and S1-3 (no amendment to these sections). |
| Required approvals | Path A: MNT + SC. Path B: QLR + MNT. |
| Proposed minimal change (proposal only) | A migration modelled on `reports/apply_corpus_corrections.py`: one entry per sub-item; replace only the differing passage; ordered-match validation; verified backup; atomic write; correction log; update `verification` evidence. Titles and keywords unchanged. |
| Regression tests | Per-section corpus tests asserting the corrected passages; validator rejects altered or reordered text. |
| Acceptance criteria | Validator passes; full suite passes; **benchmark ablation** (corpus text changes alter BM25 statistics for all queries); every changed prediction explained. |
| Rollback | Restore the migration's verified backup. |
| Status | **Blocked:** S1-1 not obtained. |

### Q-09. Section 324 bands vs Schedule I

| Field | Content |
|---|---|
| IDs | RB-12, LR-15; P1-2 |
| Location | `legal_engine/schedule_registry.py` entry 324 and `OPEN_LEGAL_QUESTIONS["324_value_bands"]`; `service.py` `_mischief_procedure_note` |
| Current behaviour | Cognizability is unknown unless the sub-section is known; the advice states the conflict as unresolved (safe). |
| Evidence | G-BNS 324(4) "less than one lakh rupees"; G-BNSS row 324(4) "less than 2 lakh rupees"; row 324(5) "one lakh rupees or upwards". |
| Classification | **Legal interpretation** (conflict within the inspected copy). |
| Risk | Low while uncertainty is preserved. |
| Required verification and approvals | S1-1–S1-3 (including any corrigendum); QLR and ADJ decision (path C). |
| Proposed minimal change (proposal only) | **None until decided.** Then encode the decided rule in the registry and the advice note. |
| Regression tests / acceptance | Boundary tests at Rs 99,999 / 1,00,000 / 1,50,000 / 2,00,000 once decided; benchmark comparison. |
| Rollback; status | Restore `schedule_registry.py` and `service.py`. **Blocked.** |

### Q-10. Punishment fields and earlier corrections

| Field | Content |
|---|---|
| IDs | RB-29 / LR-26 (13 unverified: s.70, 113, 118, 124, 125, 206, 211, 221, 222, 260, 263, 316, 323); RB-05 / LR-25 (15 corrections of 2026-10-20); RB-30 / LR-27 (63 automated "no punishment clause") |
| Location | `bns_rag_dataset.json` `punishment` and `punishment_status`; returned in `predictions[].punishment` and shown to Gemini |
| Evidence | Single-copy comparison; corrections log `reports/corpus_corrections_log_2026-10-20.json`. |
| Classification | **Suspected discrepancy** (RB-29, RB-30); single-source confirmations awaiting a second copy (RB-05). |
| Risk | Medium: incorrect or paraphrased punishment text reaches users. |
| Required verification and approvals | S1-1; MNT + SC (path A). |
| Proposed minimal change (proposal only) | Per field: confirm or replace with verbatim enacted wording through a migration. Never invent text; keep "unknown" where it cannot be confirmed. |
| Regression tests / acceptance | Corpus tests per corrected field; benchmark unaffected (punishment not indexed), but confirm. |
| Rollback; status | Migration backup. **Blocked:** S1-1. |

### Q-11. Schedule I classifications

| Field | Content |
|---|---|
| IDs | RB-17 / LR-18 (14 registry rows: 115, 117, 303, 304, 305, 306, 309, 310, 314, 316, 318, 324, 351, 352); RB-32–RB-34 / LR-19–LR-21 (scraped blocks for 87, 90, 276 conflict with the Gazette copy); RB-35 / LR-22 (354, 355, 357 positional reading) |
| Location | `legal_engine/schedule_registry.py` `VERIFIED_SCHEDULE_I`; `bns_rag_dataset.json` `scraped_procedural_classification` |
| Current behaviour | Registry rows drive `is_cognizable`, `is_bailable` and 173(3) checks; scraped blocks are not used for output. |
| Evidence | G-BNSS rows (single copy), transcribed by a developer. |
| Classification | Registry: **legal interpretation** (confirmation by a QLR). Scraped blocks: **transcription discrepancy** (87, 90, 276) or suspected agreement (354–357). |
| Risk | High if any registry row is wrong; low for unused scraped blocks. |
| Required verification and approvals | S1-2, S1-3; QLR (registry, path C); MNT + SC (scraped-block marking, path A). |
| Proposed minimal change (proposal only) | Registry: change only rows the QLR corrects. Scraped blocks: mark or correct data only; no registry additions without QLR. |
| Regression tests / acceptance | Registry tests per changed row; benchmark comparison. |
| Rollback; status | Restore `schedule_registry.py`; migration backup for data. **Blocked.** |

### Q-12. Advice templates generally

| Field | Content |
|---|---|
| IDs | RB-16 / LR-16; P1-4 |
| Location | `legal_engine/service.py`: `_theft_procedure_note`, `_robbery_procedure_note`, `_cbt_procedure_note`, `_grievous_hurt_procedure_note`, `_mischief_procedure_note`, `_misappropriation_procedure_note`, `_single_offence_procedure`, `_multi_offence_procedure`, `_audit_and_qualify_procedural_recommendation`, `_build_non_penal_response`; disclaimer in `legal_engine/schemas.py` |
| Evidence | Statute-specific statements matched individually in `reports/source_verification_matrix.md` §9. Advice quality not reviewed. |
| Classification | **Procedural advice.** |
| Risk | High (citizen-facing). |
| Required approvals | QLR (path B), PO. |
| Proposed minimal change (proposal only) | Change only sentences a QLR identifies; one change record per sentence group. |
| Regression tests / acceptance | One test per changed sentence. |
| Rollback; status | Restore `service.py`. **Blocked.** |

### Q-13. Remaining corpus records

| Field | Content |
|---|---|
| IDs | RB-22 (cross-references in s.71, 89, 148, 199, 264, 341: discrepancy observed); RB-24 / LR-28 (s.119 title); RB-26 (suspected cross-references); RB-27, RB-28 (80 differing, 56 possibly incomplete); RB-31 (s.324 artefacts) |
| Location | `bns_rag_dataset.json` |
| Classification | **Transcription discrepancy** (RB-22, RB-24); **suspected discrepancy** (others). **Not assumed erroneous.** |
| Risk | Medium (wrong cross-references in Gemini context; reduced retrieval quality). |
| Required verification and approvals | S1-1; MNT + SC; QLR where meaning changes. |
| Proposed minimal change (proposal only) | Record-by-record review; small migration batches for confirmed errors only; never bulk-replace with Gazette text. |
| Regression tests / acceptance | Per-batch corpus tests; benchmark ablation per batch. |
| Rollback; status | Migration backup. **Blocked:** S1-1. |

---

## P2 entries

### Q-14. Eight provisional benchmark cases

| Field | Content |
|---|---|
| IDs | RB-37–RB-44; LR-30–LR-37; P2-1 |
| Location | `benchmark/build_dataset.py` (source) and `benchmark/bns_synthetic_benchmark_50.json` (generated): BM-17, BM-20, BM-21, BM-22, BM-28, BM-30, BM-31, BM-45. Labels unchanged; `label_review.proposed_label_corrections_not_applied` holds proposals. |
| Evidence | Statutory statements relied on in each label review match the single Gazette copy (matrix §7). |
| Classification | **Legal interpretation** (gold labels). |
| Risk | Medium (metric validity); BM-31 alone explains the 12/32 → 11/32 procedural change. |
| Required approvals | Two QLRs labelling independently; ADJ for disagreements. |
| Proposed minimal change (proposal only) | Apply adjudicated labels through `build_dataset.py` with `review_history` entries; regenerate the JSON; one change record per case. **Labels are never changed to improve scores.** |
| Regression tests / acceptance | Dataset-builder consistency test; benchmark re-run with and without provisional cases; label changes kept separate from code changes. |
| Rollback; status | Restore `build_dataset.py` and the JSON from the snapshot. **Blocked:** reviewers unassigned. |

### Q-15. Independent evaluation

| Field | Content |
|---|---|
| IDs | RB-45 (no independent test set), RB-46 (no recent live results), RB-47 (planned metrics not implemented), RB-48 (fallback precision); P2-2, P2-3 |
| Location | `benchmark/evaluate_benchmark.py`; `reports/independent_evaluation_plan.md` |
| Classification | **Evaluation issue.** |
| Risk | High for any release decision: the 50-case benchmark is development data. |
| Requirements | Independently authored, lawyer-reviewed, adjudicated and sealed test set. Mode-separated reporting (fallback, cached, mocked, genuine live), with live runs only under PO approval and a quota budget. Serious errors listed individually. |
| Proposed minimal change (proposal only) | Evaluator extensions (strict and lenient precision, abstention, per-offence procedural accuracy, serious-error tagging), built and tested on development data only. |
| Status | **Blocked:** EL, QLRs and PO decisions not assigned. |

## Entries added 2026-10-21 (potential implementation defects)

These are recorded from `reports/section_173_3_boundary_impact.md` §3.2. Full fields are in `reports/release_blocker_register.md` §10. The proposed changes, acceptance tests and rollback steps are in `reports/section_173_3_remediation_proposal.md` (Changes A and B). Both entries are **proposals only** and **Blocked**. Existing entries Q-01 to Q-15 are unchanged.

### Q-16. Unknown registry entry reported as "legally INAPPLICABLE"

| Field | Content |
|---|---|
| IDs | RB-52 (new); boundary impact I-1 |
| Affected location | `legal_engine/service.py` `_single_offence_procedure`, lines 758–784. The generic `else` branch (lines 777–779) and the return (lines 781–784) produce "…legally INAPPLICABLE to Section {n} ({title}) because {reason}" when `check_bnss_173_3_eligibility` reports no registry entry (`schedule_registry.py` lines 386–387). |
| Current behaviour | Gemini mode, single non-templated offence outside the 14 registry sections, s.173(3) cited in the narrative or by Gemini. Bandhoo replaces Gemini's recommendation with a categorical "legally INAPPLICABLE" statement whose own reason says applicability "cannot be affirmed". Reproduced offline for BNS 308 and 329. |
| Evidence | Code reading and offline probes (register §10.1). No statutory or judicial source is involved: the defect is the gap between the stated reason and the conclusion drawn from it. |
| Classification | **Potential implementation defect** that affects procedural advice. It introduces no new legal interpretation. |
| User-facing risk | High in Gemini mode: categorical, unsupported advice about police procedure, for most BNS sections. |
| Required source verification | None beyond the existing registry. |
| Required approvals | Path B: QLR 1 and QLR 2 (or ADJ) on the replacement wording, MNT, and PO (user-facing). |
| Proposed minimal change (proposal only) | Change A in the remediation proposal: before the generic `else`, detect a section with no registry entry (`resolve_schedule_classification(...)["verified"] is False`; already imported and used at `service.py` line 714). Return a "cannot be determined from the available registry data" statement instead of "legally INAPPLICABLE". **No other branch changes.** |
| Regression tests | Fails before, passes after: BNS 308 (cited by Gemini, and cited only in the narrative) and BNS 329. Unchanged-output checks for 305, 318, 314, 351, 304, the robbery template, multi-offence 308 + 318 + 351, and fallback 308. |
| Acceptance criteria | As register §10.1 closure criteria. The fallback benchmark is unchanged (this path is not reachable in fallback, which passes an empty Gemini text). |
| Rollback | Restore `legal_engine/service.py` from the pre-change snapshot taken at implementation time, verify its hash, and re-run the offline suite. |
| Dependencies and blocker status | **Blocked:** reviewers unassigned. Independent of RB-09 (seven-year boundary) and of the Maharashtra question. |

### Q-17. Gemini timing wording passes through without a statutory note

| Field | Content |
|---|---|
| IDs | RB-53 (new); RB-08.a; boundary impact I-3; **depends on Q-01 Step 1** |
| Affected locations | `legal_engine/llm_client.py` `SYSTEM_PROMPT` line 59 (the source of the phrasing). `legal_engine/service.py` lines 785–788: the passthrough guard returns Gemini's text unchanged when it contains "173(3)", DSP and 14/fourteen, or when s.173(3) is not cited at all. |
| Current behaviour | Reproduced offline: a 304 complaint with Gemini text copying line 59, and 305/329 complaints with uncited "DSP within 14 days" text, are all returned verbatim. |
| Evidence | G-BNSS 173(3)(i) attaches "within a period of fourteen days" to the preliminary enquiry. The same text is quoted in SC-IP p.18 and SC-AD p.15 (`reports/section_173_3_case_law_review_dossier.md` §2.1). Neither judgment discusses the period. |
| Classification | **Potential implementation defect** (guard), combined with the existing transcription discrepancy in the prompt (RB-08.a). |
| User-facing risk | High in Gemini mode: a timing misstatement about police procedure, and possible bypass of the seven-year audit (route (b)). |
| Required approvals | Prompt sentence: path B as Q-01 Step 1 (QLR sign-off, MNT, PO). Any guard change: a separate path B change. |
| Proposed minimal change (proposal only) | **Step 1 = Change B** in the remediation proposal: a one-line correction to prompt line 59, which is Q-01 Step 1 (keeps "fourteen days"; no other prompt text changes). **Step 2 (not proposed for implementation now):** a guard change at lines 785–788, to be specified in a separate proposal if reviewers decide that Step 1 is not sufficient. |
| Regression tests | Prompt-content test, failing before Step 1 (no "permission … within 14/fourteen days"; "fourteen days" in the enquiry clause). Step 2 tests only if Step 2 is approved. Existing: `tests/test_inspection_regressions.py` lines 248–255. The docstring of `tests/test_procedural_law_audit.py` line 245 repeats the faulty phrasing; revising it needs a justification in the change record. |
| Acceptance criteria | As register §10.2 closure criteria. The prompt is unused in fallback, so gate 7 is expected to show no change. Effect on live output needs Q-15. |
| Rollback | Restore `legal_engine/llm_client.py` (and, for Step 2, `service.py`) from the pre-change snapshot and verify hashes. |
| Dependencies and blocker status | **Blocked:** Q-01 Step 1 awaits QLR sign-off; reviewers unassigned. Independent of RB-09 and of Q-01 Step 2 (Maharashtra, status UNKNOWN). |

## Next required approval

The PO must **assign named reviewers**: QLR 1, QLR 2, ADJ, SC, EL and an owner for Stage 1. Without them no entry can progress. The first entries to put before a QLR are Q-01 Step 1 and Q-02, which are prompt-only, add no interpretation and do not affect the fallback benchmark. In parallel, the Stage 1 owner should obtain the Maharashtra enactment status (Q-01 Step 2) and a second full copy of the BNS and BNSS (Q-03, Q-08, Q-10, Q-11, Q-13).
