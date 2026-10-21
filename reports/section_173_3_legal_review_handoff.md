# BNSS Section 173(3): Legal Review Handoff

**Prepared:** 2026-10-21 by the Bandhoo maintainer session.
**For:** QLR 1, QLR 2, the adjudicator (ADJ), the second checker (SC), the source-acquisition owner (SAO), the evaluation lead (EL), the maintainer (MNT) and the project owner (PO).
**Covers:** RB-52 / Q-16, RB-53 / Q-17, and the seven-year boundary (RB-09; decisions D-1 to D-3).
**Status:** handoff only. Nothing here is approved, implemented or validated. No blocker is closed. Bandhoo remains internal-testing-only.

## 1. Before anything else: reviewer assignment is pending

All roles in `reports/reviewer_assignment_template.md` are **unfilled**: no names, qualifications, independence declarations or dates. The PO approval block (Part 3) is blank, including the PO's own name. **No review in this handoff can start until the PO appoints reviewers** using that template.

| Role (template section) | Needed here for | Assignment |
|---|---|---|
| QLR 1 (§2.1) | All legal questions (§4) | **Pending: not appointed** |
| QLR 2 (§2.2) | All legal questions, independently of QLR 1 | **Pending: not appointed** |
| ADJ (§2.3) | Any QLR disagreement | **Pending: not appointed** |
| SC (§2.4) | Checking the quoted passages against the source PDFs before the QLRs rely on them | **Pending: not appointed** |
| EL (§2.5) | A live evaluation if RB-53 is to be closed without a guard change (§3.2) | **Pending: not appointed** |
| SAO (§2.6) | The missing sources in §5 | **Pending: not appointed** |
| PO approval (Part 3) | Confirming qualifications, approving assignments, and approving user-facing changes | **Not given** |

**Who must act:** the project owner. The PO completes Parts 2–4 of the template: name, Bar Council enrolment, qualification evidence seen, independence and conflict declaration, scope, date appointed, signatures. The PO then approves in Part 3. The template's rules apply: QLR 1, QLR 2 and the ADJ must be three different people, none involved in Bandhoo development. This handoff fills in **none** of those fields.

## 2. The four stages, kept separate

Every item below is currently at stage 1. Passing one stage does not imply the next.

| Stage | Meaning | Who | Where recorded |
|---|---|---|---|
| 1. **Proposal** | A described change with evidence and tests. *Current state of A, B and RB-53.* C has no proposal, only open decisions. | MNT (prepared) | `reports/section_173_3_remediation_proposal.md` |
| 2. **Legal approval** | Two QLRs agree, or the ADJ resolves their disagreement, on the legal questions in §4. | QLR 1 + QLR 2, or ADJ | §7 forms, then copied to `reports/legal_review_checklist.md` and `reports/legal_review_execution_checklist.md` Stage 2 |
| 3. **Implementation approval** | Technical approval of the exact change, plus PO approval for user-facing advice. Requires stage 2. | MNT + PO | Change record (`reports/post_review_change_protocol.md` §3); execution checklist Stage 3 |
| 4. **Completed validation** | Gates 5–9 recorded for the implemented change: test fails before and passes after; full offline suite; benchmark comparison; side-effect review; rollback. | MNT; checked by the approvers | Change record; then the register status may be changed by the approvers |

The dry runs in proposal §5 were on scratch copies. **They are not stage 4.**

## 3. The items

### 3.1 RB-52 / Q-16: missing registry data reported as "legally INAPPLICABLE" (Change A)

- **What happens:** in Gemini mode, with a single offence that has no Bandhoo template and is outside the 14-section registry, citing s.173(3) causes `legal_engine/service.py` lines 777–784 to say: "Section 173(3) BNSS preliminary enquiry is legally INAPPLICABLE to Section {n} … because BNS Section {n} does not have a verified BNSS Schedule I entry…". The citation may come from the complainant or from Gemini. Missing data is turned into a legal conclusion. Reproduced offline for BNS 308 and 329 (register §10.1). When only the complainant cited s.173(3), Gemini's FIR advice is also discarded.
- **Change A (proposed):** a 6-line branch, placed before the conditional branch, for sections with no registry entry. It returns: "Section 173(3) BNSS applicability to Section {n} ({title}) cannot be determined from the available registry data: {registry reason} {statutory paraphrase} {caveat}". No other branch changes. Full text and diff: proposal §A.2.
- **Classification:** potential implementation defect. It is still **path B**, because it changes s.173(3) advice wording. The legal question is narrow; no interpretation is added.

### 3.2 RB-53 / Q-17: DSP permission and fourteen-day wording passes through (Change B, plus an unresolved check)

- **What happens:** prompt line 59 (`legal_engine/llm_client.py`) says DSP permission is given "within 14 days". The check at `service.py` lines 785–788 returns Gemini's text unchanged in two situations:
  - **(a)** the text cites "173(3)", mentions DSP and "14" or "fourteen", and the offence is in range (reproduced for BNS 304);
  - **(b)** the text describes the enquiry or the timing **without** the literal "173(3)", for any non-templated single offence (reproduced for BNS 305 and 329). For 305 this also bypasses Bandhoo's own seven-year audit.
- **Change B (proposed):** replace **only** line 59 with "It is discretionary: with prior permission from an officer not below the rank of Deputy Superintendent of Police (DSP), the officer in charge may either (i) conduct a preliminary enquiry to ascertain whether a prima facie case exists, within a period of fourteen days, or (ii) proceed with investigation when a prima facie case exists." "Fourteen days" is kept; no other prompt line changes. See proposal §B.2.
- **Not solved by Change B:** route (b), and Gemini rephrasing. Fixing the pass-through check would be a **separate** path-B change, and no proposal for it exists yet. RB-53 can close only by one of these routes:
  - **(i)** an approved check fix with tests; or
  - **(ii)** a recorded QLR and PO decision that Change B suffices, backed by an approved live evaluation (Q-15, EL).

### 3.3 Seven-year boundary (RB-09; decision record only, Change C)

- **Bandhoo's current rule:** it reads "made punishable for three years or more but less than seven years" by the **maximum** term. Exactly seven years is treated as **out**; exactly three years as **in**. The code labels this "pending qualified legal review", but its correction text says "legally INAPPLICABLE" (impact assessment I-2).
- **Affected cognizable rows:** 117(2), 117(4), 305, 306, 316(3), 316(4), 318(4).
- **The two judgments differ, and neither analyses the point:**
  - *Imran Pratapgadhi v. State of Gujarat*, 2025 INSC 410, para 28 (PDF p.28), treats BNS 57 (maximum seven years) as not "less than 7 years", then notes s.57 is "on the face of it, … not applicable".
  - *Ashish Dave v. State of Rajasthan*, 2026 INSC 244, para 25 (PDF p.20), treats an FIR under BNS 308(2) and 318(4) (each maximum seven years) as within the category, because no offence "may extend to more than seven years".
- **Nothing here chooses between them.** No change to the rule or its strings is proposed.

### 3.4 Maharashtra (Q-01 Step 2): remains blocked

L.C. Bills VI and XVII of 2026 would change "fourteen days" to "six weeks" in s.173(3)(i) for Maharashtra. Their **enactment status is UNKNOWN**: no assent, Act number, Gazette publication or commencement has been found. Neither bill is to be treated as law. Change B keeps "fourteen days". Any six-week wording waits for official enactment **and** commencement evidence (S1-3, SAO), then QLR and PO approval.

## 4. Questions to answer

### 4.1 Legal questions (QLR 1 and QLR 2 independently; ADJ on disagreement)

| ID | Question | Maps to |
|---|---|---|
| L-A1 | For a section with no verified Schedule I data, is "cannot be determined from the available registry data" an accurate and adequate statement to a citizen about s.173(3)? | RB-52; proposal A.2 |
| L-A2 | Should that statement keep or drop the prefix "Correction of procedural advice:"? (Proposed: drop it, since Gemini may not have claimed anything.) Should it repeat the statutory paraphrase and caveat? (Proposed: keep them.) | A.2 choices 1–2 |
| L-A3 | When a citizen raises s.173(3), may Bandhoo withhold Gemini's otherwise unaudited FIR advice (proposed, as today), or should that advice also be shown? | A.2 choice 3 |
| L-B1 | Is the replacement line 59 faithful to s.173(3)(i)? In particular, does "within a period of fourteen days" govern the preliminary enquiry and not the DSP permission? | RB-08.a; QR-B1, QR-E1 |
| L-B2 | Is it correct to place limb (ii) ("proceed with investigation") under the permission clause, as the statute's structure suggests, replacing "police proceed directly"? | B.2 point 1; QR-E1(b) |
| L-B3 | May "considering the nature and gravity of the offence" and "without prejudice to … section 175" be left out of this one-line correction, as separate later changes? Does keeping "It is discretionary" raise any concern? | B.2 point 2; QR-F3; RB-08 |
| L-B4 | For RB-53: when Gemini's text mentions a preliminary enquiry, DSP permission or a time period, what must the user see? Options: the statutory note appended; replacement by approved text; or the prompt fix alone. | RB-53 closure route |
| L-C1 (**D-1**) | Does "made punishable for three years or more but less than seven years" include an offence whose **maximum** term is exactly seven years? Is the maximum term the right measure? How are exactly-three-year offences, minimum terms, and different first/repeat terms treated? | RB-09, RB-13; QR-D1, QR-D2 |
| L-C2 (**D-2**) | What weight do SC-IP para 28 and SC-AD para 25 carry on L-C1: holding, observation, or application without analysis? How should their different treatment of seven-year offences be weighed? Must other authority (including the Bombay High Court) be considered first? | QR-A1, QR-A2, QR-A5 |
| L-C3 (**D-3**) | Where several offences are alleged with different maxima or classifications, e.g. 308(2) + 318(4) + 351(2), is s.173(3) assessed per offence or per case? What is the effect of s.174(4)? | RB-10; QR-D4 |
| L-C4 | Until L-C1 is decided, may the seven-year correction keep saying "legally INAPPLICABLE" (`service.py` line 782), or must it be qualified? | Impact I-2; C-I2 |

### 4.2 Engineering questions (MNT; PO where noted)

| ID | Question |
|---|---|
| E-A1 | Is detecting "no registry entry" with `resolve_schedule_classification(section)["verified"]` (already imported; used at `service.py` line 714) the narrowest correct test? Does it leave all other branches byte-identical? (Dry run: 9/9 unchanged scenarios.) |
| E-A2 | Golden-output fixtures for scenarios U1–U9 (proposal §5.1): captured from the pre-change code and stored in the new test. |
| E-B1 | Does the one-line diff touch only line 59, leaving the rest of `SYSTEM_PROMPT` byte-identical? |
| E-B2 | Should the misleading docstring in `tests/test_procedural_law_audit.py` line 245 be revised in the same change record, with a justification, or separately? |
| E-R1 (PO, EL) | If route (i) is chosen for RB-53, a separate proposal is needed for the check fix. It should cover route (b) detection without "173(3)", the false-positive risk, and tests. If route (ii) is chosen, a live-evaluation plan and budget are needed under `reports/independent_evaluation_plan.md`. |
| E-C1 | After L-C1 to L-C3, scope a single coordinated change across all eight locations (proposal §C.3), with a consistency test so that the registry, templates and prompt cannot diverge. |

## 5. Evidence

### 5.1 To examine (available)

| Evidence | Where | Use |
|---|---|---|
| BNSS s.173(3) text | G-BNSS (PRS-hosted Gazette PDF, single copy). Also quoted in SC-IP PDF p.18 and SC-AD PDF pp.14–15; dossier §2.1 shows the word-by-word match. | L-B1 to L-B3, L-C1 |
| *Imran Pratapgadhi*, 2025 INSC 410 (SHA-256 `896f08f97519248a7f004350d43b72ffc296144e817c0be8b0365bd28f0d5a58`) | Official PDF `api.sci.gov.in/…/3511_2025_4_1501_60508_Judgement_28-Mar-2025.pdf`. Dossier §3: paras 20–31, 42, 44 with page references. | L-C1, L-C2 |
| *Ashish Dave*, 2026 INSC 244 (SHA-256 `3350c58215253837483fbe01397717b841f08cbb25ac2d5cbfb31edaff81bc0b`) | Official PDF `api.sci.gov.in/…/68616_2025_2_34_68884_FinalOrder_27-Feb-2026.pdf`. Dossier §4: paras 22–25, 27–29. | L-C1 to L-C3 |
| Punishment terms (BNS 57, 308(2), 318(4), 351(2)) and Schedule rows | G-BNS and G-BNSS single copies; dossier §2.3 | L-C1, L-C3 |
| Bandhoo behaviour (code, probes) | Impact assessment §1 and §1.4; register §10.1 and §10.2 | All |
| Proposed wording and dry-run results | Proposal §A.2, §B.2 and §5 | L-A*, L-B* |

### 5.2 Missing (reviewers should note any reliance on its absence)

| Missing | Effect | Owner |
|---|---|---|
| SC check of the dossier quotations, page references and emphasis (emphasis is not visible in the text extraction) | QLRs would rely on unchecked transcriptions | SC |
| Second full official copy of the BNSS (S1-2; India Code blocked) | s.173(3) and the Schedule rows rest on one PRS-hosted copy, plus the two judgments' quotations of s.173 | SAO |
| Official or SCC copy of *Lalita Kumari* (S1-4); SCC report (2026) 1 SCC 721 | The caveat wording and paragraph numbering cannot be confirmed | SAO |
| High Court decisions on s.173(3), including the Bombay High Court (S1-5) | L-C2 may need them | SAO |
| Maharashtra enactment and commencement evidence (S1-3) | The six-week change stays blocked | SAO |
| Genuine live Gemini output (RB-46, Q-15) | How often RB-53 occurs in practice, and whether Change B alone suffices, is unknown | EL, PO |

## 6. Acceptance tests required at implementation (after stages 2–3)

| Change | Must fail before and pass after (gate 5) | Must stay unchanged | Other gates |
|---|---|---|---|
| A | BNS 308, cited by Gemini; BNS 308, cited in the narrative only; BNS 329, cited in the narrative. Each: no "inapplicable"; contains the approved "cannot be determined" wording (proposal §A.3). | Golden outputs U1–U9; existing tests in proposal §A.4 | Full offline suite (Gemini disabled); fallback benchmark with `--out` to scratch, case by case, identical apart from timestamps; diff = only the added lines; fresh snapshot and rollback (§A.5–A.7) |
| B | `tests/test_prompt_content.py`: no "(DSP) within 14/fourteen days"; no "permission … within … days" (≤100 characters); "preliminary enquiry … within a period of fourteen days"; "fourteen days" present and "six weeks" absent (proposal §B.3) | Every other prompt line; `tests/test_inspection_regressions.py` 224–229, 248–255 | As A. The live effect needs Q-15. |
| RB-53 check fix | Defined only if route (i) is approved (E-R1) | — | Separate change record |
| C | Defined only after L-C1 to L-C3 (proposal §C.4) | — | Coordinated change; consistency test; no label changes |

## 7. How to record decisions

**Approval rule** (`post_review_change_protocol.md` §1 path B and gate 3):
- **QLR 1 and QLR 2 must agree**, or the **ADJ must resolve** their disagreement.
- The **MNT** must give technical approval, and the **PO** must approve any user-facing change.
- If the ADJ cannot resolve a question, nothing is changed and Bandhoo keeps its uncertainty-preserving behaviour.

**Each reviewer completes one form per question, independently.** Each form records the question, the conclusion, the authority relied on (with page or paragraph), confidence, remaining uncertainty, name and date. The completed forms are then copied:
- into `reports/legal_review_checklist.md` against LR-11, LR-12, LR-13 or LR-14, as applicable. RB-52 and RB-53 have no LR item yet; the PO or MNT should add one when reviewers are appointed;
- into the Stage 2 table of `reports/legal_review_execution_checklist.md`.

**Form (copy per question and per reviewer; leave blank until completed by the reviewer):**

| Field | Entry |
|---|---|
| Question ID (§4.1) | ____ |
| Reviewer role (QLR 1 / QLR 2 / ADJ) and name | ____ |
| Conclusion | ____ |
| Authority relied on (document, paragraph or page) | ____ |
| Evidence gaps relied on or noted (§5.2) | ____ |
| Confidence (high / medium / low) | ____ |
| Remaining uncertainty | ____ |
| Date | ____ |

**Decision status:**

| Item | Legal approval | Implementation approval (MNT + PO) | Validation | Register / queue status |
|---|---|---|---|---|
| Change A (RB-52 / Q-16) | Not given | Not given | Not done | Open / Blocked |
| Change B (Q-01 Step 1; Q-17 Step 1) | Not given | Not given | Not done | Open / Blocked |
| RB-53 closure route | Not decided | Not decided | Not done | Open / Blocked |
| D-1 to D-3 and L-C4 (RB-09, RB-10, RB-13) | Not given | n/a until decided | n/a | Open |
| Maharashtra (Q-01 Step 2) | Blocked: enactment status UNKNOWN | — | — | Blocked |

**Suggested order once reviewers are appointed:**
1. SC check of the dossier quotations.
2. L-A1 to L-A3 and L-B1 to L-B4. These are short questions, independent of the boundary.
3. L-C1 to L-C4, in parallel with the SAO's work on §5.2.

Changes A and B each get their own change record and a fresh snapshot before implementation.
