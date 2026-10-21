# BNSS Section 173(3): Seven-Year Boundary Impact Assessment

**Prepared:** 2026-10-21 by the Bandhoo maintainer session, for the qualified legal reviewers (QLR 1, QLR 2), the adjudicator (ADJ), the maintainer (MNT) and the project owner (PO).
**Status:** Technical impact assessment. **Not a legal opinion.** Nothing in this document is approved or decided. No code, prompt, test, benchmark label, threshold, procedural advice or existing report has been changed. No blocker is closed. No reviewer has been appointed (`reports/reviewer_assignment_template.md`). Bandhoo remains internal-testing-only.

**Builds on:**
- `reports/section_173_3_case_law_review_dossier.md` (the "dossier"): passages, page references and review questions QR-A to QR-F;
- `reports/release_blocker_register.md`: RB-08, RB-08.a, RB-09, RB-10, RB-11, RB-13;
- `reports/approved_correction_queue.md`: Q-01, Q-07, Q-12;
- `reports/legal_review_execution_checklist.md`: Stage 2B.

**How this was established:**
- Read-only inspection of the code and tests.
- Offline probes that call Bandhoo's deterministic procedure functions directly, with constructed predictions and, where stated, **simulated** Gemini text (§1.4). Probe scripts are in the session scratchpad, not in the repository.
- No Gemini call, no `.env` access, no scraper run, no test or benchmark edit.

---

## 1. Current behaviour

### 1.1 How Bandhoo decides whether s.173(3) applies

**Layer 1: eligibility rule** (`legal_engine/schedule_registry.py`)

| Step | Location | Behaviour |
|---|---|---|
| Constants | lines 25–26 | `BNSS_173_3_MIN_YEARS = 3.0`, `BNSS_173_3_CEILING_YEARS = 7.0` |
| Stated reading | module docstring, lines 12–15; `BNSS_173_3_RANGE_READING_NOTE`, lines 44–48 | "Eligibility is computed from the maximum term in each row; an offence whose maximum term is seven years or more is outside that range." The note says exactly seven years is "outside 'less than seven years'" and exactly three years is "within 'three years or more'". It adds: "This reading is pending qualified legal review." |
| Per-row test | `_row_173_3_status`, lines 336–360 | Checked in this order: non-cognizable → out; `max == 7.0` → out, with the qualifier "on the maximum-term reading … (interpretation pending qualified legal review)" (lines 340–344); `max > 7.0` → out ("exceeds"); `max < 3.0` → out; otherwise **in**, with a "pending qualified legal review" qualifier when `max == 3.0`. |
| Section-level result | `check_bnss_173_3_eligibility`, from line 363 | A section not in the registry is **not eligible**: "applicability cannot be affirmed without verified statutory classification". Where all rows agree, the result is eligible or not eligible. Where rows disagree, the result is **conditional**. |

**Layer 2: whether cognizability is known** (`legal_engine/service.py` `_determine_schedule_metadata`, lines 393–420)
- A prediction's `is_cognizable` is set only when every Schedule I row agrees.
- Section 318 (rows 318(2)/(3) non-cognizable, 318(4) cognizable) therefore reaches the procedure logic as `None`.
- Sections 305, 306, 117 and 316 reach it as `True`.

**Layer 3: building the procedural recommendation** (`service.py` `_audit_and_qualify_procedural_recommendation`, from line 516)

1. **No offence predicted** (line 547) → the clarification template. If s.173(3) was cited, Bandhoo adds that it "is legally inapplicable to vague complaints lacking prima facie allegations of a cognizable offence" (line 557).
2. **Several supported offences** (score ≥ `PROCEDURAL_SUPPORT_SCORE_FLOOR` = 0.5, line 131) → `_multi_offence_procedure` (lines 808–868). The output is fully deterministic; Gemini's recommendation text is not used. The route text says s.173(3) is "assessed offence by offence; on the maximum-term reading (pending qualified legal review) it does not apply to an offence whose maximum term is seven years or more" (lines 837–838). A per-offence audit (`_audit_173_3_claims`, lines 726–736) is added **only if s.173(3) was cited** in the narrative or in Gemini's text.
3. **One supported offence** → `_single_offence_procedure` (from line 739):
   - **Section-specific template, deterministic** (`_section_procedure_note`, lines 698–710): 303 (theft), 309 (robbery), 316 (criminal breach of trust), 117 (grievous hurt), 324 (mischief). Gemini's text is ignored.
   - **Section 314 alone** → non-cognizable template.
   - **Any other section, Gemini mode, Gemini text longer than 20 characters** (lines 758–788):
     - If s.173(3) is cited and the offence is not eligible, Gemini's text is **replaced** by "Correction of procedural advice: Section 173(3) BNSS preliminary enquiry is legally INAPPLICABLE to Section N … because …" (lines 765–783). The reason for a seven-year-or-more maximum is at lines 773–776.
     - If s.173(3) is cited, the offence is eligible, and Gemini's text lacks "DSP" or "14"/"fourteen", the statutory note is appended (lines 785–787).
     - **Otherwise Gemini's text is returned unchanged** (line 788).
   - **Any other section, fallback mode** → general template: "information recorded under Section 173(1) BNSS for FIR registration" when cognizable (lines 790–806). s.173(3) is mentioned only if it was cited.

**Layer 4: Gemini system prompt** (`legal_engine/llm_client.py` `SYSTEM_PROMPT`, from line 33)
- Line 58: "Applies ONLY to cognizable offences punishable for three years or more but less than seven years."
- Line 59: the timing sentence (Q-01; RB-08.a).
- Line 60: "NEVER recommend Section 173(3) for vague or ambiguous complaints where no penal offence is established…"
- Line 63: "NEVER recommend Section 173(3) for offences punishable with 7 years or more (such as Robbery Sec 309, Murder Sec 103, Dacoity Sec 310, Rape Sec 64), where information is recorded under Section 173(1) BNSS for direct FIR registration."

### 1.2 Offences with a maximum of exactly seven years

These are the registry rows on the boundary. Under the current rule all are **outside** s.173(3). The terms are single-copy readings (G-BNS / G-BNSS).

| Row | Registry line | Cognizable | Current 173(3) result | Where users see it |
|---|---|---|---|---|
| 117(2) grievous hurt | 107 | Yes | Out (boundary qualifier) | Grievous-hurt template, lines 669–676: "Each sub-section is punishable with seven years or more, so on the maximum-term reading … Section 173(3) BNSS does not apply." |
| 117(4) grievous hurt by a group | 113 | Yes | Out | Same template |
| 305 theft in a dwelling house etc. | 147 | Yes | Out | General template (no mention); correction text if 173(3) is cited (Gemini mode) |
| 306 theft by clerk or servant | 154 | Yes | Out | As 305 |
| 316(3) CBT by carrier etc. | 197 | Yes | Out | CBT template, lines 655–660 (when capacity keywords match) |
| 316(4) CBT by clerk or servant | 199 | Yes | Out | CBT template |
| 318(4) cheating, dishonestly inducing delivery | 221 | Yes | Out | Section 318 is conditional overall; 318(4) is excluded in every audit or correction text |
| 351(3) criminal intimidation (threat of death etc.) | 260 | **No** | Out (non-cognizable; the boundary does not decide it) | — |

**Not in the registry** (no Schedule I entry, so never eligible, whatever the boundary): for example BNS 308(2) extortion and BNS 57, the seven-year offences in the two judgments.

### 1.3 How the layers interact

| Mode and path | Who writes the advice | Boundary rule applied by | 173(3) mentioned to the user? |
|---|---|---|---|
| Fallback, any path | Deterministic templates | Registry and service strings | Only in templates for 303, 316 and 117 (always), or when 173(3) is cited |
| Gemini, multi-offence | Deterministic | Registry and service strings | Route sentence (line 838) only when a cognizable candidate exists; audit only if cited |
| Gemini, single offence with a template (303, 309, 316, 117, 324) | Deterministic | Registry and service strings | As fallback |
| Gemini, single offence without a template (e.g. 305, 306, 318, 308, 304) | **Gemini**, audited only if 173(3) is cited | Prompt lines 58 and 63 shape Gemini's text; the registry overrides only when 173(3) is cited | Depends on Gemini |

The boundary is therefore encoded in **at least eight places**:
- the registry constant and docstring;
- the range note;
- `service.py` lines 532, 658, 674, 773–776 and 838;
- prompt lines 58 and 63.

Any future change must update all of them together.

### 1.4 Probe results (offline; simulated Gemini text where stated)

| ID | Scenario | Output (abridged, verbatim fragments) |
|---|---|---|
| P-A | 305, fallback, 173(3) not cited | "Classified as COGNIZABLE under BNSS Schedule I; information recorded under Section 173(1) BNSS for FIR registration." No 173(3) mention. |
| P-B | 305, simulated Gemini text citing 173(3) | "Correction of procedural advice: Section 173(3) BNSS preliminary enquiry is **legally INAPPLICABLE** to Section 305 … because its maximum punishment is seven years or more, outside the 'less than seven years' range of Section 173(3) on the maximum-term reading (pending qualified legal review). Information must be recorded under Section 173(1) BNSS for FIR registration without Section 173(3) preliminary enquiry." |
| P-C | 305, simulated Gemini text not citing 173(3) | Gemini text returned unchanged |
| P-D | 318 (conditional), 173(3) cited | "…legally INAPPLICABLE to Section 318 (Cheating) because Section 318(2) is classified as NON-COGNIZABLE …; Section 318(4) is punishable with up to 7 years; on the maximum-term reading this is outside … (interpretation pending qualified legal review) (Cheating).. Procedure depends on verified Schedule I classification of the offence." |
| P-E | 308 extortion (not in registry), 173(3) cited | "…legally INAPPLICABLE to Section 308 (Extortion) because BNS Section 308 does not have a verified BNSS Schedule I entry in this registry. Section 173(3) BNSS applicability cannot be affirmed without verified statutory classification.." |
| P-F | Multi-offence, 173(3) cited, with real schedule metadata (318 conditional → `None`; 351 non-cognizable → `False`; 308 not in registry → `None`). Run for 318 + 351, and for 308 + 318 + 351 (the SC-AD offence set). | "The candidates imply different procedural routes … The procedural route cannot be determined until the material facts are verified." The audit then goes offence by offence: 318(4) "outside the 'less than seven years' range … (interpretation pending qualified legal review)"; 308 "applicability cannot be affirmed without verified statutory classification" (hedged, unlike P-E); 351 non-cognizable. The line-838 sentence does not appear because no candidate resolves to cognizable. |
| P-G | 117, fallback | "Each sub-section is punishable with seven years or more, so on the maximum-term reading of 'punishable for' (pending qualified legal review) Section 173(3) BNSS does not apply." |
| P-H | 304 snatching (in range), simulated Gemini text copying prompt line 59 ("…prior permission from an officer not below the rank of Deputy Superintendent of Police (DSP) within 14 days…") | **Returned verbatim.** The text contains "173(3)", "DSP" and "14", so the guard at lines 785–786 adds no statutory note. |

### 1.5 Tests that encode the current interpretation

Under the change protocol, any change to these tests would need a recorded justification.

| Test | Location | What it fixes in place |
|---|---|---|
| `test_173_3_eligibility_by_maximum_term` | `tests/test_inspection_regressions.py` 232–245; boundary rows at 236 (316(4)), 238 (117(2)), 239 (305) | Seven-year rows → `eligible is False` |
| `test_cbt_by_employee_does_not_offer_173_3` | same file, 259–264 | 316(4) note contains "Section 173(3) BNSS does not apply" |
| `test_boundary_punishment_terms_flag_interpretation` | `tests/test_reliability_followups.py` 221–224 | The 305 reason carries "pending qualified legal review" (the boundary is flagged, not settled) |
| `test_schedule_registry_173_3_eligibility_helper` | `tests/test_procedural_law_audit.py` 581 onward; comment at 600, assertion at 603 | Bare 316 is `conditional`. This outcome would survive a boundary change because 316(5) (life) stays out, but the comment states the current reading. |
| `test_173_3_text_matches_statutory_conditions` | `tests/test_inspection_regressions.py` 224–229 | The text contains "three years or more but less than seven years". This is statutory wording and does not depend on the boundary reading. |
| Robbery tests (case 4, case 5a) | `tests/test_procedural_law_audit.py` 281 onward, 334 onward | 309 (ten years) is out. Not boundary-sensitive. |

**Benchmark labels:**
- The scorer (`benchmark/evaluate_benchmark.py`, around line 388) scores `expected_cognizable` / `expected_bailable` only. No scored label encodes the seven-year reading, so a boundary decision would not change the metrics.
- However, the free-text fields of BNS-BM-32, BM-33 and BM-34 cite s.173(3) for 316/318 complaints. BM-34 reads: "Commercial contractual delay requires preliminary enquiry under Section 173(3) BNSS before registering penal cheating case under Section 318 BNS." That text differs from Bandhoo's current rule (318(4) excluded; 318(2)/(3) non-cognizable) and uses "requires".
- Recorded for the evaluation lead and the QLR. **Not changed.**

---

## 2. Judgment comparison (from the dossier)

All page references are PDF pages. "SC-IP" is *Imran Pratapgadhi v. State of Gujarat*, 2025 INSC 410 (28 March 2025). "SC-AD" is *Ashish Dave v. State of Rajasthan*, 2026 INSC 244 (order of 27 February 2026). Both are two-judge benches.

| Element | SC-IP | SC-AD |
|---|---|---|
| **Statute (quoted)** | s.173(3) in full, p.18: "…punishable for three years or more but less than seven years…" | Same, pp.14–15 |
| **Court's paraphrase of the range** | "made punishable for 3 years or more but less than 7 years" (paras 23, 28; 42(i)) | "offences carrying punishment between three to seven years"; "punishable with imprisonment for a term between three and seven years" (para 23, p.12); "punishable between three and seven years" (para 24, p.19) |
| **Purpose language** | "to prevent the registration of FIRs in frivolous cases where punishment is up to 7 years" (para 23, p.25); "where punishment is for imprisonment up to 7 years" (para 29, p.30) | "a safeguard against mechanical registration of FIRs in cases where the allegations … may in substance be vague, speculative or inherently doubtful" (para 24, pp.19–20) |
| **Application to the charged offences** | Para 28, p.28: "all the offences except the offence under Section 57 of the BNS are punishable by imprisonment for less than 7 years. Section 57, on the face of it, is not applicable. Therefore, this option was also available to the police officer in the present case." s.57 carries "may extend to seven years" (quoted at p.16). | Para 25, p.20: "None of the offences alleged in the impugned FIR carries imprisonment which may extend to more than seven years, thereby bringing the case within the category where the option … under Section 173(3) of the BNSS was clearly available". The FIR offences were 308(2), 318(4) (each maximum seven years in G-BNS) and 351(2) (two years, non-cognizable). |
| **What the application implies for seven-year offences (reported, not resolved)** | Treats s.57 (maximum seven years) as **not** "less than 7 years". The availability conclusion follows the statement that s.57 "on the face of it, is not applicable". Whether the Court's view of availability depended on that inapplicability is for the QLR. | Treats an FIR whose offences carry **up to** seven years as within the category. Its test ("may extend to more than seven years") is worded differently from the statute ("less than seven years"). |
| **Boundary analysed?** | No | No |
| **Order** | FIR quashed; the finding was reached "even without taking recourse to sub-Section (3)" (para 31, p.31); order at para 44 | FIR quashed under *Bhajan Lal* categories (1), (2), (5) and as an abuse of process (paras 27–29) |
| **Type of statement on the boundary** | An application within reasoning that the Court says was not needed for its finding (para 31) | An application in the course of the Court's view that the police "ought to have exercised the option" (para 25). Whether this is part of the reason for the order is QR-A2. |

**The tension, preserved:** for an offence with a maximum of exactly seven years, SC-IP para 28 points one way and SC-AD para 25 the other. Neither states a rule on the point. Neither refers to the other's treatment; SC-AD quotes SC-IP para 28 (p.18–19) without comment on s.57. This assessment **does not** treat either as controlling and does not resolve the difference. Statements that bind later courts, statements that are only observations, and any reading of "less than seven years" are all matters for qualified review (§4).

---

## 3. Impact and risk

### 3.1 Realistic cases where the current rule could mislead

Each case states what Bandhoo says now and why it could mislead **under each candidate reading**. Readings: **(X)** a maximum of exactly seven years is outside (current); **(I)** a maximum of exactly seven years is inside (consistent with SC-AD's application).

| ID | Realistic complaint | Mode / path | Current output | Risk if (I) is correct | Risk if (X) is correct |
|---|---|---|---|---|---|
| R-1 | House burglary or theft from a vehicle (305); theft by a domestic worker (306) | Fallback or Gemini, single offence | "information recorded under Section 173(1) BNSS for FIR registration" (P-A) | **Incomplete:** omits that a 173(3) enquiry may be an option | Low |
| R-2 | As R-1, and the complainant (illustrative) reports that the police intend to hold a preliminary enquiry under s.173(3) first | Gemini, 173(3) cited | "legally INAPPLICABLE … Information must be recorded under Section 173(1) … without Section 173(3) preliminary enquiry" (P-B) | **Misleading and categorical.** It could lead a citizen to dispute a lawful police step. | Wording stronger than Bandhoo's own "pending qualified legal review" qualifier |
| R-3 | Vendor fraud or online-purchase cheating with money transferred (318(4)), especially a vague complaint like SC-AD's | Any; 173(3) cited | 318(4) excluded (P-D, P-F) | Wrong exclusion for the very offence SC-AD treated as within the category | Low |
| R-4 | Extortion by threat of damaging publicity (308(2)), as in SC-AD | Gemini, 173(3) cited | "legally INAPPLICABLE … because BNS Section 308 does not have a verified BNSS Schedule I entry" (P-E) | Misleading | **Misleading under either reading:** missing registry data is presented as legal inapplicability |
| R-5 | Employee embezzlement (316(4)); grievous hurt (117(2)) | Any (template) | "Section 173(3) BNSS does not apply" (P-G and the CBT template), with the qualifier | Wrong exclusion, although qualified | Low |
| R-6 | A complaint alleging several offences, e.g. cheating, extortion and intimidation (an SC-AD-like pattern) | Multi-offence | If 173(3) is cited: offence-by-offence audit excluding 318(4) and leaving 308 unaffirmed (P-F). Where a candidate resolves to cognizable (e.g. 305 or 117 with another offence), the route adds "does not apply to an offence whose maximum term is seven years or more" (line 838). No case-level view. | Wrong exclusion of 318(4) and other seven-year offences | Whether one in-range offence alongside excluded ones permits 173(3) for the case is undecided (D-3) |
| R-7 | Gemini mode, single non-templated in-range offence (e.g. 304 snatching), Gemini repeats the prompt's timing sentence | Gemini, passthrough | Prompt-style "permission … (DSP) within 14 days" text reaches the user verbatim (P-H) | Same under both readings: a timing misstatement (RB-08.a) | Same |
| R-8 | Gemini mode, single non-templated seven-year offence, 173(3) not cited | Gemini, passthrough | Whatever Gemini writes under prompt line 63 ("NEVER recommend … 7 years or more") is returned unaudited (P-C) | Wrong exclusion with no "pending review" qualifier | Low |

### 3.2 Interpretation risks and candidate implementation defects

| Type | Item | Depends on the boundary decision? |
|---|---|---|
| **Legal-interpretation risk** | L-1: the "less than seven years" reading (registry lines 25–26, 340–344; service 532, 658, 674, 773–776, 838; prompt 58, 63). R-1, R-3, R-5, R-6, R-8. | Yes; that is the decision |
| Legal-interpretation risk | L-2: multi-offence application (R-6) | Partly |
| Legal-interpretation risk | L-3: categorical exclusion of vague complaints (`service.py` 526–527, 557; prompt 60), compared with SC-AD paras 22, 25 | No (separate question, D-5) |
| **Candidate implementation defect** (code does not do what its own stated rule says) | I-1: **missing registry entry shown as legal inapplicability**, in the single-offence correction path only. Line 782 says "legally INAPPLICABLE … because BNS Section N does not have a verified BNSS Schedule I entry" (P-E). The registry's own message, which the multi-offence audit repeats unchanged (P-F), says applicability "cannot be affirmed". That is a different statement. | **No**: wrong under either reading |
| Candidate implementation defect | I-2: **certainty mismatch.** The correction prefix "legally INAPPLICABLE" (line 782) wraps a reason that says "pending qualified legal review" (lines 774–775; P-B). | Partly. The fix to the wording depends on how certain the reviewers' decision is. |
| Candidate implementation defect | I-3: **timing text passes through unaudited.** Where Gemini's text cites 173(3), "DSP" and "14", it is returned verbatim with no statutory note (lines 785–788; P-H). Combined with prompt line 59, this delivers the RB-08.a misstatement. | **No** |
| Candidate implementation defect (cosmetic) | I-4: doubled full stops and a repeated "(Cheating)" in the conditional correction and audit texts (P-D, P-E) | No |
| Data / documentation | I-5: free text in benchmark cases BM-32, BM-33 and BM-34 (§1.5) | Partly; not scored |

"Candidate" because whether these are defects, and how to fix them, are themselves review decisions under `post_review_change_protocol.md`. **I-1, I-3 and I-4 are not currently recorded in the blocker register or the correction queue.** RB-08.a mentions the passthrough path generally. Whether to register them is a PO decision; this assessment does not modify the register.

### 3.3 Can a prompt-only correction proceed independently of the boundary question?

**Assessment: Q-01 Step 1 can be reviewed and decided independently of the boundary question, provided its scope is limited to line 59.** It still needs its own QLR sign-off.

Why it is separable:
1. It concerns what "within a period of fourteen days" attaches to (clause (i), the preliminary enquiry). That is a reading of the statutory structure. Neither judgment discusses the period (dossier §3.5, §4.5), and the seven-year question does not affect it.
2. The deterministic texts already attach the period to the enquiry (`BNSS_173_3_PROCEDURE_TEXT`). Step 1 brings the prompt into line with existing deterministic wording. It introduces no new interpretation.
3. Probe P-H shows the current line-59 wording can reach users verbatim (I-3). The risk of waiting is the same whatever the boundary decision.

Conditions that keep it separable:
- Step 1 must **not** edit prompt lines 58, 60 or 63, or the section examples (Q-07). Those depend on D-1, D-3 and D-5.
- Step 1 must keep "fourteen days" and must **not** introduce the Maharashtra six weeks (Q-01 Step 2; status UNKNOWN).
- Reviewers should record that approving Step 1 is **not** an endorsement of line 63. Otherwise an edited prompt could be read as reviewed as a whole.
- Fallback benchmark metrics cannot show the effect of a prompt change (the prompt is unused in fallback). Measuring it needs an approved live evaluation (Q-15).
- I-3 (the passthrough guard) is a code change, not a prompt change. It is outside Step 1 unless the reviewers decide to bundle it.

**Cannot proceed independently:** any change to the seven-year rule (L-1), the multi-offence wording (L-2), prompt line 63, the R-5 templates, or the tests in §1.5. These all wait for D-1 to D-3.

---

## 4. Review decisions required

No reviewer is assigned. "Decision owner" names the role from the execution checklist, not a person. Every decision field is blank, and every approval status is **Not approved**.

| ID | Question | Source and exact passage | Current Bandhoo behaviour | Decision owner | Decision | Approval status |
|---|---|---|---|---|---|---|
| D-1 | What does "made punishable for three years or more but less than seven years" mean for an offence whose **maximum** term is exactly seven years? Is the maximum term the right measure at all (RB-09, RB-13)? | BNSS s.173(3) (G-BNSS; SC-IP p.18; SC-AD pp.14–15). Dossier QR-D1, QR-D2. | Maximum-term reading. Exactly seven years is out; exactly three years is in. Labelled "pending qualified legal review" in the registry, but stated as "legally INAPPLICABLE" in the correction text (§1.1, §1.4). | QLR 1 and QLR 2 independently; ADJ if they disagree | ____ | Not approved |
| D-2 | What is the effect of SC-IP and SC-AD on D-1: binding statement, observation, or application without analysis? How should their different treatment of seven-year offences be weighed? | SC-IP para 28 (p.28), para 23 (p.25), para 29 (p.30), para 31 (p.31); SC-AD para 23 (p.12), para 24 (pp.19–20), para 25 (p.20). Dossier QR-A1, QR-A2. | Not reflected. Code and prompt predate the review of either judgment. | QLR 1, QLR 2; ADJ | ____ | Not approved |
| D-3 | When several offences are alleged with different maxima or classifications (e.g. 308(2) + 318(4) + 351(2)), is s.173(3) assessed per offence or per case? What is the effect of one offence being out of range or non-cognizable? How does s.174(4) interact? (RB-10) | s.173(3), s.174(4) (G-BNSS); SC-AD para 25 (p.20) ("None of the offences alleged…"); SC-IP para 28 (p.28) ("all the offences except…"). Dossier QR-D4. | Offence by offence (lines 726–736, 837–838); no case-level conclusion; route via 174(4) when any candidate is cognizable. | QLR 1, QLR 2; ADJ | ____ | Not approved |
| D-4 | Does "within a period of fourteen days" govern the preliminary enquiry (clause (i)) rather than DSP permission? When does it start? Is there any time limit for permission? | s.173(3)(i) (G-BNSS; SC-IP p.18; SC-AD p.15). Neither judgment discusses it. Dossier QR-B1 to QR-B3. | Registry text and templates attach it to the enquiry. Prompt line 59 attaches it to permission, and that wording can reach users verbatim (P-H). | QLR 1, QLR 2 | ____ | Not approved |
| D-5 | Are vague complaints categorically outside s.173(3), or is a fact-specific assessment required where the complaint names offences in the range? | SC-AD para 22 (p.11), para 24 (pp.19–20), para 25 (pp.20–21). Dossier QR-D3. | Categorical: "legally inapplicable to vague complaints lacking prima facie allegations of a cognizable offence" (line 557; docstring 526–527); prompt line 60. Applies only when no offence is predicted. | QLR 1, QLR 2 | ____ | Not approved |
| D-6 | Do *Lalita Kumari*'s time limits (120.7: "should not exceed fifteen days generally and in exceptional cases, by giving adequate reasons, six weeks' time is provided") apply to a s.173(3) enquiry? | *Lalita Kumari* 120.7 as quoted in SC-IP para 22 (p.23); LK-MPHC para 111(vii). Original judgment not yet obtained (S1-4). Neither later judgment addresses this. Dossier QR-C2. | Not mentioned. Bandhoo states fourteen days only. | QLR 1, QLR 2 | ____ | Not approved |
| D-7 | Which changes may be approved separately, and which must stay blocked? Proposed grouping for decision: **(a)** Q-01 Step 1, prompt line 59 only (§3.3); **(b)** I-1 and I-3 (independent of D-1) and I-4; **(c)** everything that depends on D-1 to D-3 or D-5 (§3.3, "cannot proceed"); **(d)** Q-01 Step 2 (Maharashtra). | `approved_correction_queue.md` Q-01, Q-07, Q-12; `post_review_change_protocol.md`; this document §3.2–§3.3. Dossier QR-F1 to QR-F5. | All Blocked. | QLR (legal content); PO (user-facing approval and registering I-1, I-3, I-4, I-5); MNT (technical) | ____ | Not approved |

---

## 5. Change gates

1. **Q-01 Step 1 is separate from the Maharashtra amendment.**
   - Step 1 keeps "fourteen days".
   - Maharashtra L.C. Bills VI and XVII of 2026 (six weeks) have enactment status **UNKNOWN**. No assent, Act number, Gazette publication or commencement was found (checklist S1-3).
   - Q-01 Step 2 stays blocked until enactment **and** commencement are established from an official source and the QLR and PO approve jurisdiction-specific wording.
2. **No change to the seven-year rule** while D-1 and D-2 are open:
   - registry constants and `_row_173_3_status`;
   - `service.py` boundary strings;
   - prompt lines 58 and 63;
   - the R-5 templates;
   - the tests in §1.5.
3. **When a decision is made**, every location in §1.3 must change together. The tests in §1.5 may be revised only with a recorded justification. The prompt cannot be checked with the fallback benchmark (it is not used there), so a live-evaluation plan (Q-15) is needed.
4. **Benchmark labels are not to be changed** to fit any decision. Any revision of the BM-32 to BM-34 free text is a separate EL/QLR item.
5. **No blocker is closed** by this document. RB-08, RB-08.a, RB-09, RB-10, RB-11 and RB-13 remain Open. Q-01 remains Blocked.
6. **No reviewer assignment is implied.** The roles in §4 are unfilled.
7. **Safety:** no `.env` access, no Gemini call and no scraper run occurred in preparing this assessment.

---

## 6. Repository effect of this assessment

- Created: this file only.
- Probe scripts are in the session scratchpad, outside the repository.
- One side effect was found and reversed. An early attempt to list registry rows used the system Python 3.11 without `-B`. The import failed, but first wrote four bytecode caches: `legal_engine/__pycache__/{__init__,corpus,retrieval,schedule_registry}.cpython-311.pyc`. They were removed. They are generated files, ignored by git and excluded from the baseline snapshot; no other file was touched.
