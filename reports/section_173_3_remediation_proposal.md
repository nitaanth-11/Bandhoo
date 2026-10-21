# BNSS Section 173(3) Remediation Proposal

**Prepared:** 2026-10-21 by the Bandhoo maintainer session, for the qualified legal reviewers (QLR 1, QLR 2), the adjudicator (ADJ), the maintainer (MNT), the evaluation lead (EL) and the project owner (PO).
**Status:** **Proposal only. Nothing here is approved or implemented.** Production code, prompts, tests, corpus, benchmark labels and thresholds are unchanged. No blocker is closed, and no reviewer has been appointed (`reports/reviewer_assignment_template.md`). Bandhoo remains internal-testing-only.

This proposal contains three **separately gated** changes. Each follows `reports/post_review_change_protocol.md`, one issue per change, with its own change record.

| Change | Blocker / queue | Type | Depends on the seven-year question? | Depends on the Maharashtra question? | Proposed for implementation after approval? |
|---|---|---|---|---|---|
| **A**: unknown registry data | RB-52 / Q-16 | Potential implementation defect; path B | No | No | Yes |
| **B**: prompt timing sentence | RB-08.a, RB-53 / Q-01 Step 1, Q-17 Step 1 | Transcription discrepancy in prompt; path B | No | No (keeps "fourteen days") | Yes |
| **C**: seven-year boundary | RB-09 (with RB-10, RB-13) | Legal interpretation; path B | It *is* that question | No | **No.** Decision record only. |

**Evidence base:**
- `reports/section_173_3_boundary_impact.md`, the "impact assessment";
- `reports/section_173_3_case_law_review_dossier.md`, the "dossier";
- `reports/release_blocker_register.md` §10 (RB-52, RB-53);
- `reports/approved_correction_queue.md` (Q-01, Q-16, Q-17).

**Dry runs (§5):** both proposed edits were applied only to **scratch copies** of the project outside the repository, to check feasibility. These dry runs are **not** gate passes. Every gate must be repeated and recorded at implementation time, after approval.

---

## Change A: report unknown registry data as undetermined (RB-52, Q-16)

### A.1 Problem

**Location:** `legal_engine/service.py`, `_single_offence_procedure`, lines 758–784. This path runs in Gemini mode for a single supported offence that has no section template. When:
- s.173(3) is cited, and
- the section has **no registry entry** (any BNS section other than 115, 117, 303, 304, 305, 306, 309, 310, 314, 316, 318, 324, 351, 352),

the generic `else` branch (lines 777–779) leads to the return at lines 781–784. That return reads "Correction of procedural advice: Section 173(3) BNSS preliminary enquiry is legally INAPPLICABLE to Section {n} … because BNS Section {n} does not have a verified BNSS Schedule I entry in this registry. Section 173(3) BNSS applicability cannot be affirmed without verified statutory classification.."

A conclusion of law is drawn from missing data. The registry's own reason (`schedule_registry.py` lines 386–387) and the multi-offence audit say only that applicability "cannot be affirmed".

### A.2 Proposed change (minimal; not applied)

Add one branch, before `if elig_info.get("conditional"):` (currently line 765). It uses `resolve_schedule_classification`, which `service.py` already imports and uses in the same way at line 714. No other line changes.

```python
                if not elig_info.get("eligible"):
                    max_p = elig_info.get("max_punishment")
+                   if not resolve_schedule_classification(top_pred.section)["verified"]:
+                       return (
+                           f"Section 173(3) BNSS applicability to Section {top_pred.section} ({top_pred.title}) "
+                           f"cannot be determined from the available registry data: {elig_info['reason']} "
+                           f"{BNSS_173_3_PROCEDURE_TEXT} {BNSS_173_3_CAVEAT_TEXT}"
+                       )
                    if elig_info.get("conditional"):
```

**Resulting text** (BNS 308, dry run): "Section 173(3) BNSS applicability to Section 308 (Extortion) cannot be determined from the available registry data: BNS Section 308 does not have a verified BNSS Schedule I entry in this registry. Section 173(3) BNSS applicability cannot be affirmed without verified statutory classification. Under Section 173(3) BNSS, on receipt of information …" The statutory paraphrase and caveat follow, as in the multi-offence audit.

**Wording choices for reviewers** (no choice is made here):
1. Keep or drop the existing "Correction of procedural advice:" prefix. The proposal drops it, because Gemini's text may not have claimed anything about s.173(3) (e.g. when only the complainant cited it). The prefix would wrongly imply that Gemini was corrected.
2. Keep or drop the statutory paraphrase and caveat. The proposal keeps them, for consistency with the multi-offence audit (`_audit_173_3_claims`, lines 726–736).
3. Whether Gemini's discarded recommendation should also be shown. The proposal does **not** show it: this matches current behaviour, and showing it would pass unaudited advice to users. Showing it would be a separate change.

The change infers **no legal conclusion**. It neither affirms nor denies applicability, and it does not touch the seven-year rule (Change C).

### A.3 Acceptance tests (proposed; to be added only at implementation)

Proposed file: `tests/test_inspection_regressions.py`, a new section. It uses the existing `fallback_service` and `corpus` fixtures and calls `_audit_and_qualify_procedural_recommendation(predictions, None, narrative, raw_action)` directly. No Gemini call.

| Test | Input | Assertions | Before / after |
|---|---|---|---|
| `test_unregistered_section_173_3_cited_by_gemini_is_undetermined` | BNS 308; narrative "He demanded money threatening to publish false news."; Gemini text "A preliminary enquiry under Section 173(3) BNSS may be held." | `"inapplicable" not in out.lower()`; `"cannot be determined from the available registry data" in out`; `"Section 308" in out` | **Fails before** (output says "legally INAPPLICABLE"); passes after |
| `test_unregistered_section_173_3_cited_by_narrative_is_undetermined` | BNS 308; narrative adds "Under Section 173(3) police must enquire first."; Gemini text "Register an FIR for extortion and investigate the demand." | As above | Fails before; passes after |
| `test_unregistered_section_329_is_undetermined` | BNS 329; narrative cites s.173(3); Gemini text "Record the complaint of criminal trespass and investigate." | As above, with "Section 329" | Fails before; passes after |
| `test_173_3_correction_paths_unchanged` | The nine scenarios U1–U9 in §5.1 | Output equals the string captured **before** the change (golden outputs stored in the test) | Passes before and after |

### A.4 Relevant existing tests (expected unchanged)

| Test | File and line | Why relevant |
|---|---|---|
| `test_case_4_user_narrative_mentions_173_3`, `test_case_5a_punishment_above_7_year_ceiling`, `test_case_5b_…_non_cognizable`, `test_case_8_prompt_injection_cannot_override_validation` | `tests/test_procedural_law_audit.py` 281, 334, 370, 537 | They use mocked Gemini text citing s.173(3); they exercise the robbery template and the s.314 path |
| `test_173_3_eligibility_by_maximum_term`; `test_theft_action_does_not_misstate_173_3` | `tests/test_inspection_regressions.py` 244, 248 | Registry eligibility and template wording |
| `test_schedule_registry_173_3_eligibility_helper` | `tests/test_procedural_law_audit.py` 581 | Eligibility helper |
| `test_boundary_punishment_terms_flag_interpretation` | `tests/test_reliability_followups.py` 221 | The seven-year qualifier (must not change) |

**No existing test covers the unregistered-section path.** The dry-run suite passed unchanged (§5.2), which is exactly why new tests are needed.

### A.5 Side-effect checks (gate 8)

| Check | Expected |
|---|---|
| Seven-year correction (305), conditional rows (318), non-cognizable (314, 351), eligible (304), robbery template (309) | Byte-identical output (U1–U6) |
| Multi-offence audit (308 + 318 + 351) | Byte-identical (U7). It already uses the hedged reason. |
| Fallback mode (308 with s.173(3) cited) | Byte-identical (U8). The path is unreachable without Gemini text. |
| Unregistered section with s.173(3) not cited (329) | Byte-identical (U9). The Gemini text passthrough is unchanged (RB-53 is separate). |
| `is_cognizable` / `is_bailable` for any section | Unchanged. No registry or metadata code is touched. |
| Imports | Unchanged. `resolve_schedule_classification` is already imported (`service.py` lines 23–29). |
| Diff scope | `diff` against the pre-change snapshot copy of `service.py` shows exactly the 6 added lines |

### A.6 Benchmark comparison (gate 7)

1. Before the change: `GEMINI_API_KEY="" GOOGLE_API_KEY="" python benchmark/evaluate_benchmark.py --mode fallback --out <scratch>/before.json`. Using `--out` avoids overwriting `benchmark/evaluation_report_fallback.json`.
2. After the change: the same command with `--out <scratch>/after.json`.
3. Compare case by case, ignoring only `metadata.evaluation_date_utc` and `case_results[*].elapsed_sec`. **Expected: identical.** The fallback evaluator passes no Gemini text, so the path cannot be reached.
4. Labels are not touched. Live effect is measurable only in an approved live evaluation (Q-15). No live run is part of this change.

### A.7 Rollback (gate 9)

1. Before implementation, take a fresh snapshot and manifest, as in `reports/baseline_and_rollback_audit.md`. The 2026-10-20 baseline predates later reports.
2. Record the pre-change SHA-256 of `legal_engine/service.py`. Today its first 16 hex characters are `a64d55fe2015f6fe` (register Appendix B).
3. To roll back: copy `service.py` from the fresh snapshot, verify that the hash equals the recorded pre-change value, then re-run the full offline suite (expect 228 passed, since the new tests are reverted along with the code) and the gate-7 comparison.

### A.8 Approvals required

**Path B:**
- QLR 1 and QLR 2 in agreement, or ADJ, on the replacement wording and the three wording choices in A.2;
- MNT;
- PO (user-facing advice).

Status: **Not approved.**

---

## Change B: correct the s.173(3) timing sentence in the Gemini prompt (Q-01 Step 1; Q-17 Step 1)

### B.1 Problem

`legal_engine/llm_client.py` `SYSTEM_PROMPT` line 59 currently reads:

```
     * It is discretionary with prior permission from an officer not below the rank of Deputy Superintendent of Police (DSP) within 14 days, or police proceed directly with investigation when a prima facie case exists.
```

The sentence attaches "within 14 days" to DSP permission. BNSS s.173(3)(i) (G-BNSS; also quoted in SC-IP p.18 and SC-AD p.15) attaches "within a period of fourteen days" to the preliminary enquiry. The registry text `BNSS_173_3_PROCEDURE_TEXT` already follows the statute.

Gemini text that copies line 59 reaches users verbatim (RB-53, route (a)). Neither judgment discusses the period (dossier §3.5, §4.5), so this correction does not depend on the case law or on the seven-year question.

### B.2 Proposed change (one line; not applied)

Replace line 59 only, keeping its five-space indentation:

```
     * It is discretionary: with prior permission from an officer not below the rank of Deputy Superintendent of Police (DSP), the officer in charge may either (i) conduct a preliminary enquiry to ascertain whether a prima facie case exists, within a period of fourteen days, or (ii) proceed with investigation when a prima facie case exists.
```

**What changes:**
- "within 14 days" moves to clause (i) as the statutory phrase "within a period of fourteen days".
- "or police proceed directly with investigation" becomes "(ii) proceed with investigation". This follows the statute, where both limbs sit under the permission clause, and the existing `BNSS_173_3_PROCEDURE_TEXT`.

**What does not change:** "It is discretionary" (its adequacy is RB-08 / dossier QR-A3); every other prompt line, including 58, 60–64 and the section examples (Q-07); "fourteen days" (no six weeks).

**Points reviewers must confirm** (dossier QR-E1, QR-F1 to QR-F3):
1. That moving limb (ii) under the permission clause, as in the statute, is acceptable as part of this one-line correction. The current wording ("police proceed directly") can be read as not needing permission.
2. That "considering the nature and gravity of the offence" and "without prejudice to … section 175" stay **out** of this change. Adding them would be separate changes needing separate approval.
3. That approving this line is **not** an endorsement of prompt line 63 (seven-year examples; Change C) or line 60 (vague complaints; impact assessment D-5).

### B.3 Acceptance tests (proposed)

Proposed new test file: `tests/test_prompt_content.py`. It imports `SYSTEM_PROMPT` from `legal_engine.llm_client` and makes no Gemini call.

| Test | Assertion | Current prompt | Proposed prompt |
|---|---|---|---|
| `test_prompt_does_not_attach_period_to_dsp_permission` (a) | `not re.search(r"\(DSP\)\s+within\s+(?:14\|fourteen)\s+days", SYSTEM_PROMPT)` | **Fails** | Passes |
| (b) | `not re.search(r"permission[^.\n]{0,100}within (?:a period of )?(?:14\|fourteen) days", SYSTEM_PROMPT, re.I)` | **Fails** | Passes |
| `test_prompt_attaches_fourteen_days_to_preliminary_enquiry` | `re.search(r"preliminary enquiry[^.\n]{0,120}within a period of fourteen days", SYSTEM_PROMPT)` | **Fails** | Passes |
| `test_prompt_keeps_fourteen_days_not_six_weeks` | `"fourteen days" in SYSTEM_PROMPT and "six weeks" not in SYSTEM_PROMPT` | Fails (prompt says "14 days") | Passes |

These results were checked in memory against the current and proposed text (§5.3).

**Scope check (acceptance, not a permanent test):** comparing the pre-change snapshot copy of `llm_client.py` with the new file shows exactly one changed line (59). All other lines are identical, and the line count is unchanged.

### B.4 Relevant existing tests

| Test | File and line | Relevance |
|---|---|---|
| `test_173_3_text_matches_statutory_conditions` | `tests/test_inspection_regressions.py` 224–229 | The constant contains "fourteen days" (unchanged) |
| `test_theft_action_does_not_misstate_173_3` | same file, 248–255 | Templates have no "permission … within 14 days" (unchanged) |
| `test_case_3_cognizable_offence_partial_vagueness` | `tests/test_procedural_law_audit.py` 236 | Its **docstring** (line 245) repeats "prior DSP permission within 14 days". No assertion depends on it. Revising the docstring would need a justification in the change record. |

There is currently **no** prompt-content test (Q-01). The dry-run suite with Change B passed 228/228 (§5.2).

### B.5 Side-effect checks (gate 8)

| Check | Expected |
|---|---|
| Other prompt instructions (lines 33–58, 60 onward) | Unchanged (scope check) |
| Deterministic templates and registry text | Unchanged. No code outside line 59. |
| RB-53 guard (`service.py` 785–788) | Unchanged. Gemini text that copies the new line would contain "173(3)"/DSP/"fourteen" and still pass verbatim, but now with correct attachment. Route (b) is unaffected. **This is why RB-53 needs either a separate guard change or a recorded decision that this step is sufficient** (register §10.2). |
| Gemini output generally | Not measurable offline. Needs an approved live evaluation (Q-15). |

### B.6 Benchmark comparison (gate 7)

As A.6. **Expected: identical**, because the prompt is not used in fallback mode (confirmed in the dry run, §5.4). This gate cannot show the effect on live output. That requires a separately approved live evaluation with a quota budget (`reports/independent_evaluation_plan.md`).

### B.7 Rollback

1. Fresh snapshot before implementation.
2. Record the pre-change SHA-256 of `llm_client.py` (first 16 hex characters today: `99f7f3fce32cc217`, register Appendix B).
3. Restore from the snapshot, verify the hash, and re-run the suites.

### B.8 Approvals required

**Path B** (Q-01 Step 1):
- QLR sign-off on the text and the three points in B.2;
- MNT;
- PO (user-facing advice, through Gemini output).

Status: **Not approved.**

---

## Change C: seven-year boundary (RB-09). Decision required; no change proposed

### C.1 What is undecided

BNSS s.173(3) applies to information about a cognizable offence "made punishable for three years or more but less than seven years". Bandhoo reads this by **maximum term**: a maximum of exactly seven years is outside, and exactly three years is inside (`schedule_registry.py` lines 25–26, 44–48, 336–360).

The two Supreme Court decisions in the dossier apply the range differently to seven-year offences, and **neither analyses the point**:
- *Imran Pratapgadhi*, 2025 INSC 410, para 28 (PDF p.28), treats BNS 57 (maximum seven years) as not "less than 7 years". The Court then notes s.57 is "on the face of it, … not applicable".
- *Ashish Dave*, 2026 INSC 244, para 25 (PDF p.20), treats an FIR under BNS 308(2) and 318(4) (each maximum seven years) as within the category, because no offence "may extend to more than seven years".

**This proposal does not choose between these readings.** It does not modify the registry rule or any of its repeated strings.

### C.2 Decisions required (from impact assessment §4)

| ID | Question | Decision owner | Decision | Approval |
|---|---|---|---|---|
| D-1 | Meaning of "less than seven years" for an offence whose maximum term is exactly seven years. Is the maximum term the right measure? (RB-09, RB-13) | QLR 1, QLR 2; ADJ | ____ | Not approved |
| D-2 | Weight of SC-IP para 28 and SC-AD para 25 (holding, observation, or unanalysed application) | QLR 1, QLR 2; ADJ | ____ | Not approved |
| D-3 | Multi-offence complaints: per offence or per case; effect of an out-of-range or non-cognizable offence; s.174(4) (RB-10) | QLR 1, QLR 2; ADJ | ____ | Not approved |
| C-I2 | Whether the "legally INAPPLICABLE" prefix on the seven-year correction (`service.py` line 782) should remain while the reading is "pending qualified legal review" (impact assessment I-2). Its wording depends on how firm the D-1 decision is. | QLR; PO | ____ | Not approved |

### C.3 Locations that would change together after a decision

These are listed so a later change can be scoped. **None is to be changed now.**

| Location | Current content |
|---|---|
| `schedule_registry.py` lines 12–15 (docstring), 25–26 (constants), 44–48 (range note), 336–360 (`_row_173_3_status`) | Maximum-term reading; seven years excluded; "pending qualified legal review" |
| `service.py` line 532 (docstring), 655–660 (CBT note), 669–676 (grievous-hurt note), 773–776 and 782 (correction), 837–838 (multi-offence route) | Seven years or more excluded |
| `llm_client.py` lines 58, 63 | "less than seven years"; "NEVER recommend Section 173(3) for offences punishable with 7 years or more" (overlaps Q-07) |
| Tests | `tests/test_inspection_regressions.py` 236, 238, 239 (eligibility rows), 259–264 (316(4) "does not apply"); `tests/test_reliability_followups.py` 221–224; comment at `tests/test_procedural_law_audit.py` 600 |

### C.4 Acceptance-test plan, by decision outcome

The tests depend on the decision, so none can be written now. Whichever reading is adopted:
- every location in C.3 must change in one coordinated, single-issue change;
- the tests at `tests/test_inspection_regressions.py` 236/238/239 and 259–264 must assert the decided outcome for 117(2), 117(4), 305, 306, 316(3), 316(4) and 318(4), with each changed expectation justified (gate 6);
- a test must check that the user-facing strings and prompt line 63 state the same rule as the registry, so the eight locations cannot diverge;
- the "pending qualified legal review" qualifier is kept or removed **only** as the decision record states (`tests/test_reliability_followups.py` 221–224);
- three-year cases (303(2) first conviction, 304) keep their current tests unless D-1 also decides that boundary.

### C.5 Side effects, benchmark and rollback (for the later change)

- **Side effects (gate 8):**
  - CBT, grievous-hurt, theft (303(2)), multi-offence and correction texts;
  - the 318 conditional result. If seven-year rows become eligible, 318 becomes conditional rather than uniformly ineligible;
  - RB-52 (Change A) is unaffected: unregistered sections stay undetermined.
- **Benchmark (gate 7):** no scored label encodes the boundary (impact assessment §1.5). Run the A.6 comparison anyway. The free text of BNS-BM-32, BM-33 and BM-34 cites s.173(3). Any revision of it is a separate EL/QLR item. **Labels are not changed to fit any decision.**
- **Rollback:** restore `schedule_registry.py`, `service.py`, `llm_client.py` and the revised tests from the fresh pre-change snapshot, verify hashes, and re-run the suites.

### C.6 Status

**Blocked** pending D-1 to D-3. **No change proposed.**

---

## 4. Maharashtra amendment (Q-01 Step 2): remains blocked

- Maharashtra L.C. Bill No. VI of 2026 (clause 6; passed by the Legislative Council on 24 March 2026) and L.C. Bill No. XVII of 2026 (clause 7; passed by the Legislative Council on 8 July 2026) would substitute "six weeks" for "fourteen days" in s.173(3)(i) for Maharashtra.
- **Enactment status: UNKNOWN.** No Assembly passage, assent, Act number, Gazette publication or commencement has been found (checklist S1-3). **Neither bill is treated as law.**
- Change B keeps "fourteen days" and adds no jurisdiction note.
- Any six-week or Maharashtra-specific wording stays blocked until **official evidence of enactment and commencement** is obtained and recorded in Stage 1 (S1-3), and until QLR and PO approve the wording.
- It would then be a separate change touching the prompt, the registry constant, templates and tests together (Q-01 Step 2).

---

## 5. Dry-run evidence (scratch copies only; not gate passes)

All dry runs used copies under the session scratchpad. The repository was not modified. Gemini keys were blank, no `.env` was copied or read, and no network call was made.

### 5.1 Change A: output comparison (12 scenarios)

The proposed branch was applied to a scratch copy of `legal_engine/service.py`. `diff` showed only the 6 added lines. Outputs of `_audit_and_qualify_procedural_recommendation`, original against patched:

| Scenario | Changed? | After: "inapplicable" | After: "cannot be determined…" |
|---|---|---|---|
| A1 308, s.173(3) cited by Gemini | Yes | No | Yes |
| A2 308, cited in narrative only | Yes | No | Yes |
| A3 329, cited in narrative | Yes | No | Yes |
| U1 305 (seven years) | No | Yes (unchanged; Change C) | No |
| U2 318 (conditional rows) | No | Yes (unchanged) | No |
| U3 314 (non-cognizable) | No | Yes (unchanged) | No |
| U4 351 (non-cognizable) | No | Yes (unchanged) | No |
| U5 304 (eligible; note appended) | No | No | No |
| U6 309 (robbery template) | No | Yes (unchanged) | No |
| U7 multi 308 + 318 + 351 | No | No | No |
| U8 308, fallback (no Gemini text) | No | No | No |
| U9 329, not cited (passthrough) | No | No | No |

### 5.2 Full offline suite on scratch copies

- Change A applied: **228 passed**, 1 warning (upstream SDK deprecation).
- Change B applied: **228 passed**, 1 warning.
- Imports were confirmed to come from each scratch copy.

### 5.3 Change B: acceptance checks in memory

All four assertions in B.3 fail on the current prompt and pass on the proposed line. "No six weeks" holds in both. All other lines are identical.

### 5.4 Fallback benchmark on scratch copies

`evaluate_benchmark.py --mode fallback --out <scratch>` was run on an unpatched copy, the Change A copy and the Change B copy. Differences were limited to `metadata.evaluation_date_utc` and per-case `elapsed_sec`. All predictions, scores and procedural fields were **identical**. Headline metrics were unchanged, e.g. Recall@10 71.88% (46/64).

---

## 6. Approvals still required

| Item | Approvals | Status |
|---|---|---|
| Reviewer appointments (precondition for everything) | PO, using `reports/reviewer_assignment_template.md` | Not done |
| Change A (RB-52, Q-16) | QLR 1 + QLR 2 (or ADJ), MNT, PO | Not approved |
| Change B (Q-01 Step 1; Q-17 Step 1) | QLR sign-off, MNT, PO | Not approved |
| RB-53 closure route: guard change (separate proposal) **or** recorded decision that Change B suffices, plus a live evaluation | QLR, PO; EL for Q-15 | Not decided |
| Change C decisions D-1 to D-3 and C-I2 | QLR 1, QLR 2, ADJ; PO for wording | Not decided |
| Q-01 Step 2 (Maharashtra) | Official enactment and commencement evidence (S1-3); then QLR, PO | Blocked (status UNKNOWN) |

**Recommended order once reviewers are appointed:** A and B can go to the QLRs in parallel, as separate change records. C goes to QLR 1 and QLR 2 independently, with the ADJ on disagreement. Each implementation batch needs a fresh snapshot first.
