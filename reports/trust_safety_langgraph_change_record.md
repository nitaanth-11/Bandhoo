# Change Record: Frontend Trust-and-Safety Fixes and LangGraph Complaint-Structuring Workflow

**Date:** 2026-10-21. **Prepared by:** the Bandhoo maintainer session.
**Approval relied on:** the project owner's instruction of 2026-10-21. It approved:
- the frontend trust-and-safety fixes;
- the use of LangGraph as a required architectural component.

That approval is **not** legal approval. It does not cover the Section 173(3) proposals (Change A, Change B/RB-53, Change C/D-1 to D-3) or anything relating to the Maharashtra bills, which remain separately gated and unchanged.

**Status:** implemented and tested offline. Bandhoo remains internal-testing-only. **Nothing here is legally validated or independently evaluated.**

## 1. Rollback snapshot (taken before any file was modified)

| Item | Value |
|---|---|
| Path | `/Users/tanaya/Desktop/Bandhoo_snapshots/bandhoo_pre_trustsafety_langgraph_20261021T084552/` |
| Contents | `project/` (118 files), `MANIFEST.sha256`, `PERMISSIONS.txt`. Excludes `.env`, `node_modules`, caches, `.venv`. |
| Manifest SHA-256 | `696610de0ba7023b9c32e5ef353c74c3e4a8f7bee214f672330fad9f91e4badd` |
| Verification | 0 mismatches against the working tree when taken; made read-only |
| Pre-change test result | 228 passed, 1 warning (upstream SDK deprecation) |
| Pre-change benchmark | Fallback benchmark run saved outside the repository for comparison |

The original baseline snapshot (`bandhoo_baseline_20261020T210347`) and the protected corpus backup are untouched.

## 2. Files changed

**Modified (3):**

| File | Change |
|---|---|
| `src/App.jsx` | Trust-and-safety fixes (§3) and display of the structured record |
| `main.py` | Optional `BANDHOO_SKIP_DOTENV=1`; `/api/get-jurisdiction` now uses polygon containment; new `POST /api/v1/complaints/structure`; KD-tree removed. `/api/classify-offence` unchanged. |
| `requirements.txt` | `langgraph>=1.2.16` with environment notes |

**Added (11):**
- `complaint_engine/__init__.py`, `models.py`, `extraction.py`, `checks.py`, `jurisdiction.py`, `graph.py`;
- `src/trustSafety.js` and `src/trustSafety.test.js`;
- `tests/test_complaint_graph.py`, `tests/test_jurisdiction_and_api.py`, `tests/test_frontend_trust_safety.py`.

**Environment:** a project virtual environment `.venv/` (git-ignored, Python 3.14.6, `--system-site-packages`). It contains `langgraph` 1.2.16, `langchain-core` 1.6.12 and `langgraph-checkpoint` 4.3.0. The system Python was not modified.

**Not changed:**
- legal classification code (`legal_engine/`), prompts, corpus, benchmark labels, thresholds;
- every existing report, register and queue (all blockers still Open; all queue entries still Blocked);
- snapshots and backups.

**Expected mismatch:** `release_blocker_register.md` Appendix B now differs for `main.py` (16/17 hashes match), because `main.py` was intentionally changed. The register was not edited. Updating its baseline hash is a PO decision.

## 3. Frontend trust-and-safety fixes (`src/App.jsx`)

| # | Was | Now |
|---|---|---|
| 1 | Random "FIR number" `MUM-<random>/<year>`; "LODGE ELECTRONIC FIR", "Authenticate & Register FIR"; email stating the FIR was "registered electronically" | No FIR number. Buttons read "Prepare complaint draft" / "Create complaint draft". The view is titled "COMPLAINT DRAFT (NOT AN FIR)". |
| 2 | Uploads shown as "Identity document verified" / "Supporting document verified" | "Attached to this draft: <name>. Not sent anywhere and not verified." (`attachmentLabel`) |
| 3 | Mandatory identity-document upload; ID number required | Identity upload removed ("Do not upload identity documents. The police verify identity in person."). ID type optional. |
| 4 | Invented `<station>.ps@mumbaipolice.gov.in` address and `mailto:` link | Removed. "Copy draft text" with no recipient. Notice: Bandhoo has no verified police contact details and does not send complaints. |
| 5 | Prefilled officer "R. K. Patil, Inspector", "Investigation Started", "Case registered online…"; contact fallbacks "100 / 112", "100"; address fallback "Mumbai Headquarters" | Removed. A blank "For police use only" block. "Not available in Bandhoo data" where no data exists. |
| 6 | "(E-Signed Authentically Digitally)"; "Digital Signature / E-Sign" | "Complainant's typed name (this is not a digital signature)" |
| 7 | Hard-coded legal fallback (sections and "Initiate FIR registration immediately") when the backend was unavailable | Neutral state: "Automatic analysis is unavailable right now. No legal sections have been suggested." (`analysisUnavailableState`) |
| 8 | Only "submitted" / "registered" states | Four separate statuses: draft created / submission attempted / receipt confirmed / FIR registered (`statusLadder`). Each needs its own evidence. The app can only record "draft created". |
| 9 | Backend nearest-centroid result overwrote the frontend polygon result; a nearest-centroid fallback was used when the backend was down; jurisdiction was assigned for the default map centre | Local containment is authoritative (`assessJurisdiction`). The backend is only a cross-check, and disagreement means confirmation is needed (`reconcileJurisdiction`). There is no nearest-centroid fallback. "Police jurisdiction requires confirmation." is shown when the location is missing, outside all polygons, within 100 m of a boundary, ambiguous, or in conflict. No jurisdiction is assessed until the complainant picks a location. |
| 10 | Claims of filing, delivery or verification across labels | Removed: "verified boundary", "official BMC coordinates", "Police Station Headquarters" (for centroid markers), the "electronic FIR is legally recognised…" paragraph, "OpenAI & HuggingFace", "LogReg", "✓ RAG Corpus Match", the Section 465/468 penalty text, and the "under Section 173 BNSS" declaration. Neutral wording replaces them. |

**Related fixes:**
- **No prefilled form values:** no default offence ("Theft"), legal section ("Section 303"), or suspect "Unknown". Blank fields print as "Not provided", never as "Same as Complainant" or "None".
- **Machine suggestions are not copied into the draft silently.** The complainant can add them with an explicit button, and they are marked "Machine-suggested, not legally reviewed".
- **Third-party geocoding** (OpenStreetMap Nominatim address search and reverse geocoding) is **off** (`EXTERNAL_GEOCODING_ENABLED = false`) until a data-handling policy is approved. Map tiles still load from OpenStreetMap.
- **Clicking a directory entry** only moves the map. It no longer sets the incident location to an area centre.
- **Structured record panel:** after a draft is created, the frontend calls Bandhoo's own `/api/v1/complaints/structure` (no external service) and shows the review route, missing information, questions, possible inconsistencies, jurisdiction and evidence status, labelled "machine-assisted, nothing verified".
- **Lint:** 3 findings remain (2 errors, 1 warning), all present before this change. Two earlier errors were removed. The production build succeeds.

## 4. LangGraph complaint-structuring workflow (`complaint_engine/`)

**Graph** (`graph.py`, `StateGraph` over an explicit `TypedDict` state `ComplaintState`):

```
intake ─┬─▶ extract_facts ─▶ attribute_sources ─▶ detect_missing ─▶ detect_contradictions
        │       ─▶ associate_evidence ─▶ assess_jurisdiction ─▶ validate_and_route
        └─(invalid input)─────────────────────────────────────▶ validate_and_route
validate_and_route ─┬─▶ human_review ──┐
                    └─▶ police_review ─┴─▶ build_report ─▶ END
```

| Requirement | How it is met |
|---|---|
| Original statement immutable | `Statement` is a frozen Pydantic model with a SHA-256. A state reducer (`keep_original`) raises `ImmutableStatementError` if any node tries to replace it. The validation node re-hashes it. Clarifications are separate statements. |
| Exact source quotations | Every fact has `SourceSpan`s. `attribute_sources` rejects any fact whose span does not equal `statement.text[start:end]`, and validation re-checks it. |
| Unsupported facts | An optional extractor (injected by trusted code; **not used by the API**) is accepted only with verbatim quotations. Inferences need `inference: true` plus verbatim basis quotations, and are kept as "AI-generated inference". All others are rejected with a reason. |
| Separation of information | Report sections: complainant statements; facts (each "Unverified claim"); supporting evidence provided (not examined, not verified); independently verified (only through accepted police verification events); missing information; AI inferences; explicit denials; rejected items. |
| Uploads are not proof | `EvidenceItem` defaults to `supplied_not_examined` / `not_assessed` / `unverified`. Only `apply_verification_events` changes them, for an event from the `police_officer` role with an authorisation reference and method. The public API forbids extra fields, so it cannot carry events. |
| Neutral contradictions | Rule detectors: different dates, times (60 minutes or more apart), amounts, numbers of people, vehicle numbers, and denial against assertion (injury, weapon, witness). Both quotations are kept; the wording is neutral and tested against a list of dishonesty words. Nothing is resolved automatically. |
| Missing information | Fields what / when / where / who / loss value / medical attention / evidence / witnesses, each with status `open`, `explicitly_denied` or `unknown_to_complainant`. At most 5 neutral questions. |
| Jurisdiction | `jurisdiction.py`: polygon containment (holes and MultiPolygons supported), distance to boundary, statuses `inside` / `near_boundary` / `outside_all` / `multiple` / `no_location` / `data_unavailable`. A station is named only for `inside`. The boundary file hash is recorded, and its provenance is marked unverified. |
| Human-review routing | `validate_and_route` sends a case to human review on: validation failures, node errors, contradictions, unconfirmed jurisdiction, missing core fields, rejected items, or high-risk indicators (e.g. weapon, sexual offence, child, threat to life). |
| Failures and retries | Each node is wrapped: an unexpected exception becomes a recorded `NodeError` and the run continues to human review. The optional extractor is retried up to `llm_max_attempts` (default 3) for transient errors. Invalid output is an explicit error and is not retried. |
| No overclaiming | There is no checkpointer, database or durable audit trail. The report states "persistence: none" and "submission_status: draft_only". The processing log is in memory only. |
| No external data transfer | Deterministic extraction only through the API. The workflow refuses to start if LangSmith tracing is enabled, unless `BANDHOO_ALLOW_EXTERNAL_TRACING=1` is set under an approved policy. |
| Legal separation | The record does not include legal provisions. `/api/classify-offence` and `legal_engine/` are unchanged. |

## 5. Tests

| Run | Command | Result |
|---|---|---|
| Full offline suite (project venv) | `GEMINI_API_KEY="" GOOGLE_API_KEY="" BANDHOO_SKIP_DOTENV=1 .venv/bin/python -m pytest -q -p no:cacheprovider` | **267 passed**, 1 warning (upstream SDK deprecation) |
| Original suite (system Python 3.14, no LangGraph) | the same with the 3 new test files ignored | **228 passed** (unchanged) |
| Frontend logic and static checks | `node --test src/trustSafety.test.js` (also run by `tests/test_frontend_trust_safety.py`) | **16 passed** |
| Fallback benchmark | `benchmark/evaluate_benchmark.py --mode fallback --out <scratch>` before and after | **Identical** apart from timestamps and timings. Labels and thresholds unchanged. |
| Production build | `vite build --outDir <scratch>` | Succeeds |

**New tests cover:**
- every removed frontend claim (static checks);
- the backend-unavailable state;
- the status ladder;
- jurisdiction containment, boundary, hole, overlap, outside, missing location and missing data;
- the backend no longer returning nearest-centroid guesses;
- graph node order;
- the invalid-input branch;
- node-failure recovery;
- immutability of the original statement;
- exact quotations;
- rejection of forged spans;
- grounded and ungrounded extractor output;
- retries and invalid output;
- missing details versus denial versus "unknown";
- neutral contradictions;
- evidence staying unverified;
- rejection of unauthorised verification events;
- rejection of extra API fields;
- validation catching a forged status;
- a deterministic police-review route;
- the API endpoints, including `/api/classify-offence` still working.

**Not tested:** browser rendering and DOM behaviour (there is no browser test harness); live Gemini (not called).

## 6. Limitations

1. **Extraction is basic.** It is rule-based and English-centred, with negation patterns from the legal engine (English, Hindi, Hinglish). It will miss facts and may mislabel some. No accuracy has been measured, so no accuracy claim is made.
2. **No persistence or audit trail.** No authentication, no police verification interface, and no stored records. Verification events can only come from trusted server code.
3. **Boundary data provenance is unverified.** The 100 m near-boundary threshold is a design choice, not a measured value. The frontend does not yet use GPS accuracy.
4. **Gemini can still receive narratives.** `/api/classify-offence` still calls Gemini when a key is configured, and the frontend still displays its suggestions and procedural note (relabelled as machine-generated and not legally reviewed). That logic is under the separate legal gates and was not changed. Only synthetic data should be used.
5. **Map tiles** are still requested from OpenStreetMap. The API URL `http://localhost:8001` is hard-coded.
6. **Marathi strings** were written by the maintainer session and need review by a native speaker.
7. **Contradiction detection can flag legitimate differences** (e.g. two different items with different values). These are presented as requests for clarification, not findings.
8. **Three lint findings** that predate this change remain.

## 7. Rollback

```bash
SNAP=/Users/tanaya/Desktop/Bandhoo_snapshots/bandhoo_pre_trustsafety_langgraph_20261021T084552
P=/Users/tanaya/Desktop/Bandhoo
shasum -a 256 "$SNAP/MANIFEST.sha256"   # expect 696610de0ba7023b9c32e5ef353c74c3e4a8f7bee214f672330fad9f91e4badd
(cd "$SNAP/project" && shasum -a 256 -c ../MANIFEST.sha256 | grep -vc ': OK$')   # expect 0
# 1. Restore the three modified files (with their recorded permissions)
for f in main.py requirements.txt src/App.jsx; do
  cp "$SNAP/project/$f" "$P/$f"; chmod "$(grep "  ./$f\$" "$SNAP/PERMISSIONS.txt" | cut -d' ' -f1)" "$P/$f"
done
# 2. Move the added files aside (do not delete)
mkdir -p "$P/../Bandhoo_rolled_back_$(date +%Y%m%dT%H%M%S)" && mv "$P/complaint_engine" "$P/src/trustSafety.js" "$P/src/trustSafety.test.js" \
  "$P/tests/test_complaint_graph.py" "$P/tests/test_jurisdiction_and_api.py" "$P/tests/test_frontend_trust_safety.py" \
  "$P/../Bandhoo_rolled_back_"*/
# 3. Verify and test (system Python; LangGraph not needed after rollback)
(cd "$P" && shasum -a 256 -c "$SNAP/MANIFEST.sha256" | grep -vc ': OK$')   # expect 0
(cd "$P" && GEMINI_API_KEY="" GOOGLE_API_KEY="" python3.14 -m pytest -q -p no:cacheprovider)   # expect 228 passed
# 4. Optional: remove the project virtual environment
# rm -rf "$P/.venv"
```

This change record is not in the snapshot. Keep it, or move it aside, when rolling back.

## 8. Next steps (not done here)

- The PO decides whether to update the register's Appendix B baseline hash for `main.py`.
- Data-handling policy for Gemini, geocoding and map tiles.
- Authentication and a police verification interface before any verification events are recorded.
- Persistence and an append-only audit trail, implemented and tested before any claim of auditability.
- Evaluation of extraction quality and of police usability, as in `reports/complaint_structuring_verification_implementation_plan.md` §7.
- The legal gates for Section 173(3) and the Maharashtra bills remain with the appointed reviewers. None are appointed yet.

---

## 9. Addendum (2026-10-21): fixes for the validation defects

**Scope:** the defects confirmed in `reports/trust_safety_langgraph_validation.md`, on the instruction of 2026-10-21 ("Fix the confirmed LangGraph workflow defects… Keep the scope narrow"). The defect IDs below are that report's IDs. They are **not** the Section 173(3) "Change C / D-1 to D-3" items named at the top of this record, which are untouched.

**Not changed:**
- legal engine, classification rules, corpus, benchmark labels and thresholds;
- Section 173(3) proposals and Maharashtra amendment status;
- both earlier snapshots and the read-only backup;
- the blocker register (Appendix B still lists `main.py` as `54ecd10e5097b1ad`; the file is now `f3cc144de24f1a63`, an intended change that remains unreconciled pending the baseline-refresh decision).

No persistence, authentication or police integration was added. The validation report was not edited; it records the state before these fixes.

### 9.1 Rollback snapshot (taken before any file was modified)

| Item | Value |
|---|---|
| Path | `/Users/tanaya/Desktop/Bandhoo_snapshots/bandhoo_pre_langgraph_defect_fixes_20261021T093926/` |
| Contents | `project/` (131 files), `MANIFEST.sha256`, `PERMISSIONS.txt`. Same exclusions as §1. Read-only. |
| Manifest SHA-256 | `e4e5a792f18a81d2b77c757e088b9b18cee3ebbe2b8da438e62c1b4b1eaee215` |
| Verification | 0 mismatches against the working tree when taken |

### 9.2 Defects fixed

| ID | Fix | Where |
|---|---|---|
| D-1 | The frontend derives the review status only from the backend decision. "Ready for police review (not submitted; not yet reviewed by police)" is shown only for a `ready_for_police_review` decision with `validation_passed: true`, no reasons, no errors and `processing_status: "complete"`. "Needs human review" is shown for `human_review_required`. Anything else (missing, invalid, unknown or failed) shows "Review status unavailable; human review required". The panel's failure text now also says the review status is unavailable. | `src/trustSafety.js` (`reviewRoute`, `reviewStatusLabel`), new `src/ReviewStatus.js`, `src/App.jsx` |
| D-2 | Added the route `review_status_unavailable`. `_is_ready` is the single readiness test: a `ReviewDecision` object, ready, validated, with no reasons and no errors in the run. The conditional edge uses it, so a dict, string or inconsistent decision no longer crashes the run or reaches `police_review`. `human_review` and `build_report` write `effective_review()`, so a missing or invalid decision, or a failure after a ready decision, is reported as `review_status_unavailable`. | `complaint_engine/models.py`, `complaint_engine/graph.py` |
| D-10 | `external_tracing_settings()` checks `LANGSMITH_TRACING`, `LANGSMITH_TRACING_V2`, `LANGCHAIN_TRACING`, `LANGCHAIN_TRACING_V2` and `LANGCHAIN_HANDLER`. Any value other than empty, false, 0, no or off counts as on, case-insensitively. It runs on every `run_structuring` call as well as in `build_graph`, and raises `ExternalTracingRefused`; the API returns 503. As a second barrier, each run executes inside `langsmith.tracing_context(enabled=False)` with langchain's `tracing_v2_callback_var` cleared, so no tracer is attached even if the check were bypassed. The opt-out `BANDHOO_ALLOW_EXTERNAL_TRACING=1` is unchanged and still needs an approved policy. The guard does not depend on an API key. | `complaint_engine/graph.py` |
| D-3 | `build_report` sets `processing_status`: `complete`, `incomplete` (a step failed; human review), `invalid_input` (empty statement), or `failed` (intake did not complete). A failed report carries `received_input` (verbatim statement, clarifications, SHA-256). `structure_for_api` turns `failed` into HTTP 500 with the received statement and `review_status_unavailable`, so it is never a partial success. | `complaint_engine/graph.py`, `main.py` |
| D-6 | The single "I do not know …" pattern was split by category. *who* needs an identity object (who, him, them, the man, his name…), "recognise", or "see his face". *when* needs date, time, day or when. *where* (new) needs where, place, location or address. *loss_value* (new) needs how much, value, cost or price. "I do not know the date" no longer marks *who*. | `complaint_engine/checks.py` |
| D-7 | Dates are compared on day and month when either lacks a year. "14 October" and "15 October" are flagged; "14 October" and 14/10/2026 are not. No year is inferred (normalised values keep `????`). Both exact quotations are kept, and the summary adds "(no year was given; none is assumed)". | `complaint_engine/checks.py` |
| D-9 | **Investigation:** the extractor had no Hindi or Marathi patterns, and sentence splitting ignored the danda (।). Every unread detail was reported as `open` missing.<br>**Narrow patterns added**, each needing a clear marker:<br>• Hinglish: "N baje" (time, not normalised); kal/aaj/parso (+ raat/shaam/subah/dopahar); "do/teen… aadmi/ladke/log…" (person count); "\<Capitalised name\> [place word] ke paas/saamne/bahar…" (place).<br>• Marathi: "N वाजता" (time); काल/आज/परवा (+ रात्री…); dates with Marathi month names (yearless dates normalise to `????-MM-DD`); "दोन माणसांनी…" (person count); "\<name\> स्टेशन/मार्केट…" before जवळ/समोर… (place).<br>**Language check:** `checks.language_profile` marks coverage `limited` when ≥20% of letters are Devanagari, or ≥3 distinct romanised Hindi/Marathi marker words appear. Then:<br>• details not found are `not_determined`, not `open`;<br>• no questions are generated for them;<br>• the case is routed to human review with a note to read the original statement;<br>• the report includes `language_coverage`.<br>This is **not** comprehensive multilingual support. | `complaint_engine/extraction.py`, `complaint_engine/checks.py`, `complaint_engine/graph.py`, `src/trustSafety.js` |
| D-4 | Fixed by the D-3 mechanism. If `build_report` fails, the API now returns 500 with the received statement, not a `KeyError` traceback. | `complaint_engine/graph.py`, `main.py` |
| D-5 | Kept the abort inside the graph: the replacement is still rejected, and the existing test still requires the exception. `structure_for_api` now converts it into a 500 response with the original statement and `review_status_unavailable`. The response does not include the replacement text. | `complaint_engine/graph.py` |
| D-8 | `reconcileJurisdiction` treats any backend disagreement with a local `inside` result as a conflict: a different station, or a non-inside status such as `near_boundary`, `outside_all` or `multiple`. A missing backend result (unreachable) leaves the local result unchanged. | `src/trustSafety.js` |

### 9.3 Files changed (against the §9.1 snapshot)

| File | Before (sha256 prefix) | After | Reason |
|---|---|---|---|
| `complaint_engine/models.py` | `071ed91114c2cba8` | `ec312a6f87fb6933` | D-2 route value; D-9 `not_determined` status |
| `complaint_engine/checks.py` | `f367198ee1f7e9d0` | `6a20d8dbb2f33ab4` | D-6, D-7, D-9 (language profile, `not_determined`) |
| `complaint_engine/extraction.py` | `3a707ce6b064e9ee` | `5854f1f3b09e4cb7` | D-9 patterns, danda sentence split, Marathi date normalisation |
| `complaint_engine/graph.py` | `254c78b935e4f222` | `d8b79529b01cbf8b` | D-2, D-3, D-4, D-5, D-9 routing note, D-10; workflow version 0.1 → 0.2 |
| `complaint_engine/__init__.py` | `d0c0347f6f2c766c` | `bf18be70cd69f606` | exports `structure_for_api` |
| `main.py` | `ea8b6b43cd54e2f1` | `f3cc144de24f1a63` | the endpoint uses `structure_for_api` (error responses) |
| `src/trustSafety.js` | `56c2775ecbc9316e` | `db34ff3ba570a0af` | D-1 review status; D-8; `not_determined` label |
| `src/App.jsx` | `3e8f87223770122d` | `5388ff48c520a75e` | D-1: renders `<ReviewStatus>`; failure text |
| `src/trustSafety.test.js` | `cb965610f1e2a1e5` | `dc0a739d80d0c799` | 6 new tests (existing tests unchanged) |
| `src/ReviewStatus.js` (new) | — | `ca420110b423ab4a` | D-1 component, renderable in Node tests |
| `tests/test_complaint_defect_regressions.py` (new) | — | `e0f222eb1a27d280` | 53 regression tests |
| `reports/trust_safety_langgraph_change_record.md` | — | — | this addendum |

No existing test file's assertions were changed.

### 9.4 Regression tests: before and after

Before the fixes, `tests/test_complaint_defect_regressions.py` failed at collection, because it imports `structure_for_api`, `REVIEW_UNAVAILABLE` and `ExternalTracingRefused`. The Node suite also failed to load (`ReviewStatus.js` missing). For per-test results, a scratch copy with tolerant imports was run against the unchanged code: **49 failed, 4 passed**.

**Failures caused by the defects:**

| Defect | Result before the fixes |
|---|---|
| D-2: routing exception | report `review` was `None` |
| D-2: missing decision | `TypeError` crash |
| D-2: dict or string decision | crash |
| D-2: inconsistent ready decision | reached `police_review` |
| D-3, D-4, D-5 | no error response and no preserved statement |
| D-6 | date, place, value and unrelated "don't know" cases mislabelled |
| D-7 | yearless conflicts: 0 contradictions |
| D-9 | no Hinglish or Marathi facts; details reported as `open` missing |
| D-10 | `LANGSMITH_TRACING_V2` and `LANGCHAIN_TRACING` were not refused; the check did not re-run per request; tracing was not disabled inside the run |

**Failures caused only by the new report fields:** `processing_status` and `language_coverage` did not exist yet.
- `test_successful_run_is_marked_complete`
- `test_mid_workflow_failure_is_marked_incomplete`
- `test_disabled_tracing_values_are_not_refused`
- `test_workflow_and_api_make_no_network_calls`
- `test_english_statement_keeps_full_coverage`
- the node-failure parametrisations for nodes whose failure was already routed to human review

**The 4 that passed before:**
- the clean-case baseline;
- "unknown identity does not imply unknown date";
- "same yearless date is not a conflict";
- "full and yearless same day is not flagged".

These are guard tests and are expected to pass before the fixes as well.

**Frontend before the fixes** (probe):
- the report without a review gave route `unknown`, which `App.jsx` rendered as "Ready for police review";
- D-8 status-only disagreements returned `confirmed: true` for near_boundary, outside_all, multiple and no_location.

**Corrected test case:** one parametrised case (a `human_review` failure in a case routed to police review) could never execute, because that node is not on the path. It was replaced by `test_human_review_step_failure_is_not_reported_ready`, which uses a case that goes through `human_review`.

**After the fixes:**
- the new Python file: 53 passed;
- the Node suite: 22/22 (16 existing + 6 new).

### 9.5 Test, build and network results

| Check | Result |
|---|---|
| Full offline suite (`.venv`) | **320 passed** (the 267 existing + 53 new), 1 upstream `google.genai` deprecation warning |
| Original suite (system Python, without the 4 LangGraph-dependent files) | **228 passed** |
| Node (`node --test src/trustSafety.test.js`) | **22/22** |
| Production build (`vite build`, output to scratch) | OK; JS 396.39 kB (gzip 117.90 kB) |
| Lint | the same 3 pre-existing findings (unused `React`; `updateLocation` before declaration; `useEffect` dependencies). None new. |
| Fallback benchmark | identical to the pre-change run except `elapsed_sec` and the run timestamp. No prediction, metric or label changed. |
| Network | `test_each_tracing_setting_is_refused_without_network` (8 cases), `test_tracing_is_disabled_inside_the_workflow_even_if_the_setting_check_is_bypassed` and `test_workflow_and_api_make_no_network_calls` all run with `socket.connect`, `connect_ex` and `create_connection` blocked, and record zero attempts. The bypass test first shows (control) that LangChain would construct a LangSmith tracer when the graph is invoked directly with `LANGSMITH_TRACING_V2=true`, then that `run_structuring` constructs none. |

### 9.6 Remaining limitations and test gaps

- **D-9 is partial.**
  - Only the listed expressions are recognised.
  - Hinglish times have no am/pm and are not compared.
  - Hinglish places need a capitalised name.
  - The Marathi place pattern takes one word before the place noun.
  - Marathi and Hindi negation, injury, weapon, evidence, witness and loss wording is largely unrecognised. Limited-coverage statements therefore go to human review rather than being structured.
  - The language check is a heuristic: a mostly English statement with a few Hindi words stays at full coverage.
  - None of this has been reviewed by a native speaker or measured.
- **The D-7 rule can flag legitimate different dates** in one account, as before. These are presented as requests for clarification.
- **D-5 still aborts inside the graph by design.** Only the API response changed.
- **Frontend rendering coverage:**
  - the review line is tested by rendering the production `ReviewStatus` component with `react-dom/server`;
  - the `App.jsx` wiring is checked statically;
  - there is still no full-page DOM test.
- **Error responses echo the complainant's statement** back to the caller, over the existing unauthenticated localhost API with CORS `*` (residual risk §6.1 in the validation report).
- **The tracing guard covers LangSmith/LangChain only.** It does not cover other instrumentation (e.g. OpenTelemetry exporters), and none is configured in this project.
- **Not addressed** (outside the defect list):
  - `test_get_jurisdiction_endpoint_inside_a_polygon` still never reaches its inside branch (validation report §4);
  - an `attribute_sources` failure leaves facts without display categories (routed to human review).
- **Validation is not independent.** Fixes and tests were written in the same session as the original implementation and its validation.

### 9.7 Rollback of this addendum's changes

```bash
SNAP=/Users/tanaya/Desktop/Bandhoo_snapshots/bandhoo_pre_langgraph_defect_fixes_20261021T093926
P=/Users/tanaya/Desktop/Bandhoo
shasum -a 256 "$SNAP/MANIFEST.sha256"   # expect e4e5a792f18a81d2b77c757e088b9b18cee3ebbe2b8da438e62c1b4b1eaee215
(cd "$SNAP/project" && shasum -a 256 -c ../MANIFEST.sha256 | grep -vc ': OK$')   # expect 0
# 1. Restore the modified files with their recorded permissions (this also restores this record without §9)
for f in complaint_engine/models.py complaint_engine/checks.py complaint_engine/extraction.py complaint_engine/graph.py \
         complaint_engine/__init__.py main.py src/trustSafety.js src/App.jsx src/trustSafety.test.js \
         reports/trust_safety_langgraph_change_record.md; do
  cp "$SNAP/project/$f" "$P/$f"; chmod "$(grep "  ./$f\$" "$SNAP/PERMISSIONS.txt" | cut -d' ' -f1)" "$P/$f"
done
# 2. Move the two added files aside (do not delete)
RB="$P/../Bandhoo_rolled_back_$(date +%Y%m%dT%H%M%S)"; mkdir -p "$RB"
mv "$P/src/ReviewStatus.js" "$P/tests/test_complaint_defect_regressions.py" "$RB"/
# 3. Verify and test
(cd "$P" && shasum -a 256 -c "$SNAP/MANIFEST.sha256" | grep -vc ': OK$')   # expect 0
(cd "$P" && GEMINI_API_KEY="" GOOGLE_API_KEY="" BANDHOO_SKIP_DOTENV=1 .venv/bin/python -m pytest -q -p no:cacheprovider)   # expect 267 passed
```

Rolling back further, to before the LangGraph integration, is §7, run after the steps above.

**Approvals:** the owner's instruction to fix the defects is the only approval. No reviewer has been named, and none is invented here. The baseline refresh proposed in the validation report (§8.4) has **not** been applied.

---

## 10. Addendum (2026-10-21): complaint-structuring quality

**Scope:** the owner's instruction of 2026-10-21 to validate and improve complaint-structuring quality, fixing only demonstrated weaknesses.

**Unchanged:**
- LangGraph (graph shape and node order unchanged);
- legal engine, classification rules, corpus, the legal benchmark and its labels and thresholds;
- Section 173(3) and Maharashtra items;
- snapshots, backup and blocker register.

No storage, authentication, officer portal or submission was added.

### 10.1 Rollback snapshot (taken before any file was modified)

| Item | Value |
|---|---|
| Path | `/Users/tanaya/Desktop/Bandhoo_snapshots/bandhoo_pre_structuring_quality_20261021T100732/` |
| Contents | `project/` (133 files), `MANIFEST.sha256`, `PERMISSIONS.txt`. Read-only. 0 mismatches when taken. |
| Manifest SHA-256 | `e8d6b3869851da8e0163aa5ceff0bf5c71a3618c4b70dfb0520decd27c43e499` |

### 10.2 Evaluation method (defined before measuring)

- **Cases:** `benchmark/structuring/structuring_cases.json` holds 34 synthetic cases.
  - **Dev split (20 cases):** used to find weaknesses.
  - **Held-out split (14 cases):** not used to choose fixes.
  - Groups covered: clear and complete; incomplete; contradictory dates, identities, amounts, person counts, times and injury/witness statements; uncertain or denied details; unsupported allegations; Hinglish; Marathi; missing and unknown locations.
  - It also has 11 jurisdiction cases:
    - 9 on synthetic boundaries (inside, near a shared edge, outside, in a hole, overlapping, no location, missing data file), where the expected answer is true by construction;
    - 2 safety checks on the repository's unverified boundary data.
- **Gold:** written from the annotation guide in `benchmark/structuring/evaluate_structuring.py` and frozen before the first run. SHA-256 `3ec97968733a8e038b058c6a40cf2cd3282c974df82f443c5e13e1a523ea1018`, unchanged since.
- **Metrics:** listed in that file's docstring.
  - extraction precision and recall per category (people, dates/times, places, alleged actions, losses, witnesses, evidence);
  - polarity accuracy (asserted / denied / uncertain);
  - unsupported-fact rate = (extracted items matching no gold item + items shown as asserted when the gold says denied or uncertain) ÷ items extracted;
  - missing-information status accuracy, false "missing" and missed "missing";
  - contradiction precision and recall;
  - language routing;
  - jurisdiction correctness and unsafe answers;
  - draft checks.
- **Integrity counts, which must all be 0:**
  - non-verbatim quotes;
  - verification claims without a police event;
  - non-draft submission status;
  - malformed or judgemental contradictions;
  - statements not preserved.
- **Limits of this evaluation:**
  - The same session wrote the cases, the gold and the fixes, and saw the held-out statements while writing them. The held-out split is therefore **not blind**; it was only excluded from choosing fixes. Some fixes (Hinglish relation words and verbs) were added for symmetry with dev-demonstrated Marathi gaps, and they also match held-out wording.
  - 34 cases is small.
  - **Nothing here measures real-world police effectiveness.**

### 10.3 Weaknesses found (baseline, dev split unless stated)

| # | Weakness | Evidence |
|---|---|---|
| W1 | Alleged actions were never extracted | action recall 0% (dev and held-out) |
| W2 | Items lost or damaged were never extracted; only money amounts were | loss recall 35% dev / 31% held-out |
| W3 | People: relations with "his/her" and names ("his brother Ganesh Jadhav"), roles ("the driver") and Marathi relation words were missed; names were not recorded | D07, D13, D16 |
| W4 | Common forms missed: "No one was there"; Marathi "पाहिले"; plural "transaction IDs"; "IMEI number"; places after "to"; places on transport ("in the crowded train"); parts of the day ("in the evening") | D05, D09, D13, D15, D17, D19, D20 |
| W5 | Denied evidence ("I do not have any CCTV footage") was reported as missing; damage ("broke my door lock") did not ask for a loss value | D20, D07 |
| W6 | A corrected identity across statements was not flagged | D07 (identity recall 0) |
| W7 | No readable draft. The frontend panel never showed the extracted facts or the verification checklist. | draft checks 0/34 |
| W8 | Found while fixing W1–W7: a time at a sentence end kept the full stop (“10 pm.”); speculation such as "must be the one who stole" would have marked the date and item in the same sentence uncertain; "I do not know who took it" marked "took" as *denied*; an explicit "I don't know the exact place" was dropped when a partial place was given | regression tests below |

### 10.4 Changes

| Fix | What changed | File |
|---|---|---|
| W1 | **New fact kind `alleged_action`.** A curated verb list for theft, violence, threats, fraud and damage, plus a few Hinglish and Marathi verbs.<br>• Not after "I"/"we"; not "called" before a name.<br>• Polarity follows the existing negation and hedge rules.<br>• Speculation and hearsay cues ("must be", "I suspect", "everyone … says", "I heard") make **only the alleged action** uncertain.<br>• "I do not know / did not see …" is no longer read as a denial of what follows. | `extraction.py`, `models.py` |
| W2 | **New fact kind `property`.** An item noun with a possessive (or cash/money/jewellery), extracted only next to a loss or damage verb: after an active verb, before a passive one, or before a Hinglish/Marathi verb. Reported as `items_lost_or_damaged`; amounts stay in `losses`. | `extraction.py`, `graph.py` |
| W3 | Relations with my/his/her/their/our, optionally followed by a name (recorded as `name:…`); a short role list ("the driver", "the accused"…); Hinglish and Marathi relation words. | `extraction.py` |
| W4 | Witness "was/were there"; Hinglish "dekha" and Marathi "पाहिले/बघितले"; evidence plurals and IMEI; places after to/from/into, and on public transport; parts of the day. | `extraction.py` |
| W5 | Denied evidence → `explicitly_denied`. Damage words count as a loss needing a value. An explicit "I don't know the exact place/time/who" is kept even when a partial detail exists. | `checks.py` |
| W6 | A clarification with a correction cue ("actually", "sorry", "not \<Name\>") that names a different person from an earlier statement is flagged neutrally as `identity`, with both quotes. A new name without a correction is not flagged. | `checks.py`, `graph.py` |
| W7 | **`draft_text`**, rendered from the report. It contains:<br>• the account verbatim;<br>• every detail as a quotation with its statement ID and [denied]/[uncertain] marks;<br>• verified information (none unless there is a police event), AI inferences, missing information with questions, possible inconsistencies, supporting material, jurisdiction, the verification checklist, and a blank police-use block.<br>It states "NOT AN FIR" and "Not submitted to the police". The frontend shows it under the structured record in a collapsible section. | new `draft.py`, `graph.py`, `trustSafety.js`, `App.jsx` |
| W8 | The time pattern ends at "pm" before a full stop. The polarity changes are listed under W1. | `extraction.py`, `checks.py` |

### 10.5 Files changed (against the §10.1 snapshot)

| File | Before (sha256 prefix) | After |
|---|---|---|
| `complaint_engine/extraction.py` | `5854f1f3b09e4cb7` | `93f5c11968215a2a` |
| `complaint_engine/checks.py` | `6a20d8dbb2f33ab4` | `48a90bd91e16d3f6` |
| `complaint_engine/graph.py` | `d8b79529b01cbf8b` | `3200b561d965141b` |
| `complaint_engine/models.py` | `ec312a6f87fb6933` | `8cb44a07aed583c6` |
| `src/trustSafety.js` | `db34ff3ba570a0af` | `c706770028e81347` |
| `src/App.jsx` | `5388ff48c520a75e` | `2ea51d040b4e8775` |
| `src/trustSafety.test.js` | `dc0a739d80d0c799` | `b252f0071cb197c1` (1 test added) |
| `complaint_engine/draft.py` (new) | — | `6e4bda6ecc23ba29` |
| `tests/test_structuring_quality.py` (new) | — | `1e0fd9ba4b4af18e` (26 tests) |
| `benchmark/structuring/evaluate_structuring.py` (new) | — | `b88bc11acd8df481` |
| `benchmark/structuring/structuring_cases.json` (new) | — | `3ec97968733a8e03` |
| `benchmark/structuring/results_baseline.json` (new; pre-change code) | — | `4627e35516e91051` |
| `benchmark/structuring/results_after.json` (new) | — | `768684d79a6036cd` |
| this record | — | §10 appended |

No existing test was changed.

`tests/test_complaint_defect_regressions.py::test_unknown_place_is_recorded_for_place_only` failed once during the work. Its statement says "on the bus", which W4 now recognises as a place. That dropped the complainant's explicit "I don't know the exact place". The code was corrected (W5, last item); the test was not changed.

### 10.6 Regression tests: before and after

The final `tests/test_structuring_quality.py` was run against the snapshot code (`PYTHONPATH` set to the snapshot):
- **Before:** 24 failed, 2 passed. The 2 that passed are guard tests: own actions/naming are not alleged actions, and a new name without a correction is not flagged.
- **After:** 26 passed.

The Node test for the draft passthrough fails before (no `draftText`) and passes after.

### 10.7 Results

Synthetic cases only. Each cell is precision / recall.

| Category | Gold items (dev / held-out) | Baseline dev | After dev | Baseline held-out | **After held-out** |
|---|---|---|---|---|---|
| People | 23 / 17 | 100 / 87.0 | 100 / 100 | 100 / 47.1 | **100 / 58.8** |
| Dates and times | 31 / 21 | 100 / 96.8 | 100 / 100 | 100 / 95.2 | **100 / 95.2** |
| Places | 15 / 10 | 100 / 86.7 | 100 / 100 | 100 / 80.0 | **100 / 90.0** |
| Alleged actions | 29 / 21 | – / 0 | 90.9 / 100 | – / 0 | **94.4 / 81.0** |
| Losses | 20 / 13 | 100 / 35.0 | 100 / 100 | 100 / 30.8 | **100 / 100** |
| Witnesses | 6 / 6 | 100 / 66.7 | 100 / 100 | 100 / 83.3 | **100 / 100** |
| Evidence | 7 / 1 | 100 / 71.4 | 100 / 100 | 100 / 100 | **100 / 100** |
| **Micro** | 131 / 89 | 100 / 60.3 | 97.9 / 100 | 100 / 51.7 | **98.7 / 85.4** |

| Measure | Baseline dev | After dev | Baseline held-out | **After held-out** |
|---|---|---|---|---|
| Unsupported-fact rate | 0.0% (0/82) | 2.1% (3/141) | 0.0% (0/47) | **2.6% (2/78)** |
| Polarity accuracy | 79/79 | 131/131 | 45/46 | **74/76** |
| Missing-info status accuracy | 95.7% (4 false missing, 1 missed) | 100% (0, 0) | 89.8% (7, 1) | **92.9% (5, 1)** |
| Contradictions, precision / recall | 100 / 85.7 (6/7) | 100 / 100 (7/7) | 100 / 71.4 (5/7) | **100 / 71.4 (5/7)** |
| Language routing correct | 20/20 | 20/20 | 14/14 | **14/14** |
| Draft passes all checks | 0/20 | 20/20 | 0/14 | **14/14** |
| Integrity violations (5 counts) | 0 | 0 | 0 | **0** |

**Jurisdiction:** 11/11 correct and 0 unsafe, both before and after (no jurisdiction code changed). This shows agreement with the boundary data as given. Real-world jurisdiction correctness cannot be measured, because the boundary data's provenance is unverified.

**How to read these numbers:**
- **Dev scores after the fixes are fitted to the dev cases.** The held-out column is the better guide, and it is not blind (§10.2).
- **The baseline unsupported-fact rate of 0% reflects extracting very little.** After the fixes, the unsupported items are:
  - "taken" in "Nothing else was taken" and "nothing was taken" (shown as denied);
  - "took" in "I do not know who took it";
  - "damaged" in "was damaged".

  All are verbatim but outside the gold set.
- **The one overstated item** is H08's "I am sure … took" (speculation not recognised).

### 10.8 Test and build results

| Check | Result |
|---|---|
| Full offline suite (`.venv`) | **346 passed** (320 earlier + 26 new), 1 upstream deprecation warning |
| Original suite (system Python, without LangGraph-dependent files) | **228 passed** |
| Node (`node --test src/trustSafety.test.js`) | **23/23** |
| Production build | OK; JS 396.77 kB (gzip 117.99 kB) |
| Lint | the same 3 pre-existing findings; none new |
| Legal fallback benchmark | identical to the earlier run except timing fields |
| Network / Gemini | none used. The evaluator and tests run with Gemini keys blank and `.env` not read. The structuring-path no-network tests from §9 still pass. |

### 10.9 Remaining limitations (from the held-out errors and review)

- **People (held-out recall 58.8%):** unlisted roles are missed ("a delivery boy", "a bike rider", "a tea seller", "the man"). So are "five of them" and the Marathi oblique "एका माणसाने". The "who" field is then reported missing (3 of the 5 false "missing" cases).
- **Actions (held-out recall 81.0%):** verbs outside the list are missed ("opened", "shouted", "touch", bare "take"). The list will always be incomplete.
- **Identity:** the H04 correction "His name was actually Kishor Shinde" is missed, because the name pattern does not allow "actually".
- **Person counts:** H13 "There were five of them" is missed (no count phrase).
- **Places:** places in subject position are missed ("my house in Vikhroli was broken into").
- **Witnesses:** "Nobody else was present" ("else") is not read as a denial.
- **Losses:** "grabbed" does not trigger a missing loss value.
- **Speculation:** "I am sure … because" is not recognised as speculation.
- **Polarity is sentence-local.** A hedge ("Maybe …") marks every detail after it in the sentence uncertain, including places.
- **Hinglish and Marathi:** only the listed expressions are covered, without native-speaker review. Uncertain cases still route to human review.
- **No measurement on real complaints, and no police usability evaluation.** The draft format has not been reviewed by police.

### 10.10 Rollback of this addendum's changes

```bash
SNAP=/Users/tanaya/Desktop/Bandhoo_snapshots/bandhoo_pre_structuring_quality_20261021T100732
P=/Users/tanaya/Desktop/Bandhoo
shasum -a 256 "$SNAP/MANIFEST.sha256"   # expect e8d6b3869851da8e0163aa5ceff0bf5c71a3618c4b70dfb0520decd27c43e499
for f in complaint_engine/extraction.py complaint_engine/checks.py complaint_engine/graph.py complaint_engine/models.py \
         src/trustSafety.js src/App.jsx src/trustSafety.test.js reports/trust_safety_langgraph_change_record.md; do
  cp "$SNAP/project/$f" "$P/$f"; chmod "$(grep "  ./$f\$" "$SNAP/PERMISSIONS.txt" | cut -d' ' -f1)" "$P/$f"
done
RB="$P/../Bandhoo_rolled_back_$(date +%Y%m%dT%H%M%S)"; mkdir -p "$RB"
mv "$P/complaint_engine/draft.py" "$P/tests/test_structuring_quality.py" "$P/benchmark/structuring" "$RB"/
(cd "$P" && shasum -a 256 -c "$SNAP/MANIFEST.sha256" | grep -vc ': OK$')   # expect 0
(cd "$P" && GEMINI_API_KEY="" GOOGLE_API_KEY="" BANDHOO_SKIP_DOTENV=1 .venv/bin/python -m pytest -q -p no:cacheprovider)   # expect 320 passed
```

Earlier rollbacks (§9.7, §7) apply after this one, in that order.

**Approvals:** the owner's instruction is the only approval. No reviewer has been named. Bandhoo remains internal-testing-only; no real complainant data is authorised.
