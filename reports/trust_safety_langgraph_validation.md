# Validation: Frontend Trust-and-Safety Fixes and LangGraph Complaint-Structuring Workflow

- **Date:** 2026-10-21
- **Scope:** the change recorded in `reports/trust_safety_langgraph_change_record.md`, checked against the rollback snapshot `Bandhoo_snapshots/bandhoo_pre_trustsafety_langgraph_20261021T084552` (manifest sha256 `696610de0ba7023b9c32e5ef353c74c3e4a8f7bee214f672330fad9f91e4badd`).
- **Status of Bandhoo:** internal testing only. It is not legally validated and not production-ready.
- **Data used:** synthetic statements and coordinates only. `.env` was not read (`BANDHOO_SKIP_DOTENV=1`, Gemini keys blank). No Gemini call was made and the scraper was not run.
- **What this task changed:** only this report was created. No production code, tests, corpus, benchmark labels, existing reports, snapshots or backups were changed (see §8).

> **This validation is not independent.** The same assistant session that implemented the change carried out this validation. The findings below have reproduction steps so that a separate reviewer can confirm them. That review still needs to happen before any status change.

---

## 1. Summary

| Area | Result |
|---|---|
| LangGraph workflow | Core properties hold. They are covered by named tests and confirmed with probes: the statement can't be replaced, quotes are exact, source attribution is kept separate from verification, contradictions are neutral, there is no Gemini or network use, and the execution order is as documented. **Four defects** in how failures are handled, and **two** in how missing details and contradictions are reported. |
| Frontend | No false claims of an FIR being registered, a complaint being submitted, evidence being verified, an officer having reviewed it, a digital signature, or a confirmed jurisdiction. **One defect:** an absent or unknown review route is displayed as "Ready for police review". **One low-severity gap** in reconciling local and backend jurisdiction results. |
| API and privacy | Classification response is unchanged. The structuring endpoint returns a draft only. The jurisdiction endpoint is safe for missing coordinates, outside points, boundary proximity and ambiguity. **One privacy defect:** the LangSmith tracing guard misses two environment variables that switch tracing on. |
| Regression and build | 267 passed (full offline suite). 228 passed (original suite on system Python). Node 16/16 passed. Production build OK. Fallback benchmark identical apart from timing fields. Labels and thresholds unchanged. |
| Change control | Only intended differences from the rollback snapshot (3 modified, 12 added). Blocker register Appendix B: 16/17 match. The `main.py` mismatch is caused by this change and is **not** concealed. A baseline refresh is proposed in §6, not applied. |
| **Verdict** | **Safe to continue internal testing with synthetic data only**, subject to the conditions in §7. Not suitable for real complainant data. |

---

## 2. Verified behaviours

The tests named below are in `tests/test_complaint_graph.py` (CG), `tests/test_jurisdiction_and_api.py` (JA) and `src/trustSafety.test.js` (Node; run through `tests/test_frontend_trust_safety.py`).

Probes are throwaway scripts kept outside the repository: `probe_graph.py` (P1–P10), `probe_api.py` and `probe_front.mjs`. Their outputs are quoted below, and the exact commands are in Appendix A.

### 2.1 LangGraph workflow

**Original statement preserved; replacement rejected**
- Tests:
  - CG `test_original_statement_cannot_be_replaced_by_a_node`
  - CG `test_statement_model_is_frozen_and_hash_recorded`
- Probe P5: a node returning a new `original_statement` raises `ImmutableStatementError` ("The original complainant statement cannot be changed.").
- **Caveat:** the run aborts with no report. See D-5.

**Extracted facts keep exact quotes**
- Tests:
  - CG `test_every_statement_fact_quotes_the_statement_exactly`
  - CG `test_fact_with_mismatched_span_is_rejected`

**Unsupported facts can't silently become established**
- Tests:
  - CG `test_unsupported_llm_fact_rejected_and_grounded_inference_labelled`
  - CG `test_invalid_extractor_output_is_an_explicit_error`
  - CG `test_validation_catches_a_status_set_without_an_event`
- Facts carry `provenance` and `verification_status`. Only `complainant_statement` facts go into the factual sections of the report. AI inferences go into a separate `ai_inferences` list (`complaint_engine/graph.py:238`, `:285`).

**Attribution and verification are separate**
- Tests:
  - CG `test_uploaded_evidence_alone_is_never_verified`
  - CG `test_unauthorised_or_incomplete_verification_events_are_rejected` (4 cases)
  - CG `test_authorised_verification_event_marks_only_its_target`
  - CG `test_api_request_cannot_carry_verification_events`
- API probe:
  - an extra `trusted_verification_events` field returns 422;
  - an injected evidence `verification_status` returns 422;
  - `independently_verified` is `[]`.

**Contradictions keep both accounts without resolving them**
- Tests:
  - CG `test_contradictions_are_neutral_and_preserve_both_statements` (both spans quote their source exactly; no dishonesty wording; routed to human review)
  - CG `test_no_contradiction_for_a_single_consistent_account`
- **Gap:** dates with no year are not compared. See D-7.

**Missing details, denials, "don't know" and inferences represented**
- Tests:
  - CG `test_missing_core_details_and_questions`
  - CG `test_explicit_denial_and_unknown_are_not_reported_as_missing`
- **Defects:**
  - D-6: "I do not know \<anything\>" is attributed to *who*.
  - D-9: non-English place and time details are reported as missing.

**Failures route to human review**
- Tests:
  - CG `test_node_failure_is_recorded_and_routed_to_human_review` (fault in `detect_contradictions` only)
  - CG `test_invalid_input_skips_processing_and_routes_to_human_review`
  - CG `test_transient_extractor_failures_are_retried`
  - CG `test_extractor_exhausting_retries_keeps_deterministic_results`
- Probes:
  - faults in `extract_facts` and `attribute_sources` route to `human_review_required` and keep the statement.
- **Defects:** failures in `intake`, `validate_and_route` and `build_report`, and the immutability abort, do not fully meet the requirement. See D-2, D-3, D-4 and D-5.

**API does not invoke Gemini through the optional extractor**
- Code:
  - `main.py:130` calls `run_structuring(data)` with no `configurable`, so no `llm_extractor` is passed;
  - the report header says `extraction_mode: "deterministic"` (`graph.py:262`).
- Probe P10: with `socket.connect` and `socket.create_connection` blocked, both the workflow and `POST /api/v1/complaints/structure` returned 200, with `errors: []` and no network attempt.
- No repository test asserts this directly (see §4).

**Actual execution order matches the documented order**
- Test: CG `test_nodes_run_in_order_and_report_is_built`.
- Probe P1: the compiled edges are exactly those drawn in change record §4. Conditional edges run from `intake` (to `extract_facts` or `validate_and_route`) and from `validate_and_route` (to `human_review` or `police_review`).
- Probe P2 execution log:
  1. intake
  2. extract_facts
  3. attribute_sources
  4. detect_missing
  5. detect_contradictions
  6. associate_evidence
  7. assess_jurisdiction
  8. validate_and_route
  9. human_review (logs 2 events)
  10. build_report

### 2.2 Frontend (`src/App.jsx`, `src/trustSafety.js`)

**No FIR number, registration or submission claim**
- Node tests:
  - `App.jsx contains no fabricated FIR numbers or registration claims`
  - `a draft does not establish any later status`
  - `each status needs its own evidence; …`
  - `draft notice states it is not submitted, not confirmed and not an FIR`
- `App.jsx`:
  - titles read "COMPLAINT DRAFT (NOT AN FIR)" (`:97`, `:663`, `:1449`);
  - the status ladder records the draft only (`:1455`).
- Vocabulary sweep: every remaining use of registered, submitted, verified, signature, confirmed or FIR is negated or neutral.

**No "evidence verified", officer review, contact or e-sign claims**
- Node tests:
  - `App.jsx contains no verified-upload, invented contact, officer or e-sign claims`
  - `attachment label never claims verification`
- `App.jsx`:
  - "For police use only (to be completed by the receiving officer)" stays blank (`:123`);
  - the typed name is marked "not a digital signature" (`:124`, `:1560`).

**No confirmed jurisdiction unless the point is inside exactly one polygon**
- Node tests:
  - `containment: clearly inside one polygon`
  - `near a shared boundary needs confirmation`
  - `outside all polygons and missing location need confirmation`
  - `backend result cannot override local containment`
  - `without local boundary data, only a backend polygon-containment result is accepted`
  - `holes are excluded from containment`
- `App.jsx`:
  - `updateLocation` treats local containment as authoritative (`:417`–`:431`);
  - no jurisdiction is computed for the default map centre (`:249`);
  - `clearLocation` resets the result (`:455`).

**No nearest-centre override**
- `App.jsx:433` keeps the local result when the backend is down. `App.jsx:692` shows station details only after confirmed containment.
- The KD-tree has been removed from `main.py`.
- JA `test_get_jurisdiction_endpoint_never_returns_a_nearest_centroid_guess`.

**Backend down**
- Classification failure sets `analysisUnavailableState()` (`App.jsx:510`), which carries no sections or advice. Node test: `backend unavailable state carries no legal sections or advice` (it covers the helper; the wiring was checked by inspection).
- Structuring failure sets the panel to "unavailable" and keeps the local draft (`App.jsx:604`–`:609`).

**Blank fields**
- Every printed field falls back to "Not provided" (`App.jsx:658`, `:1467`–`:1503`, `:1560`–`:1561`). Checked by inspection; no automated test.

**Uploads**
- Labelled "…Not sent anywhere and not verified." (`attachmentLabel`).
- Only the type, file name and size go to the local backend (`App.jsx:597`–`:600`). File contents are not sent.
- The mandatory ID upload has been removed. Node test: `App.jsx has no hard-coded legal fallback or mandatory identity upload`.

**Machine suggestions are not auto-filled**
- They are added only on request, marked "Machine-suggested, not legally reviewed" (`App.jsx:646`). Checked by inspection.

**External geocoding off**
- `EXTERNAL_GEOCODING_ENABLED = false` guards both Nominatim calls (`App.jsx:440`, `:521`). Node test: `external geocoding is disabled by default`.

### 2.3 API

**Classification compatibility**
- JA `test_classify_offence_endpoint_still_available`.
- API probe: the `/api/classify-offence` response keys equal `OffenceClassificationResponse.model_fields`, and `inference_status` is `fallback_llm_unavailable`.
- `/api/bns-stats` GET returns 200.

**`/api/v1/complaints/structure` returns a draft only**
- JA `test_structure_endpoint_returns_unverified_draft_record`.
- API probe:
  - `submission_status` is "draft_only (Bandhoo has no police-submission integration)";
  - `persistence` is "none (this record is not stored by Bandhoo)";
  - the header reads "Structured complaint record (draft, not an FIR)";
  - `legal_provisions` is "Not included…".

**Jurisdiction: missing coordinates**
- API probe: `{}` returns 422; latitude only returns 422; `NaN` returns 200 with `status: no_location`.
- JA `test_missing_location_and_missing_data`.

**Jurisdiction: outside all polygons**
- API probe at (18.95, 72.70): `station` None, `details` None, `status: outside_all`, `method: polygon_containment`.
- JA `test_outside_all_polygons_requires_confirmation`, `test_real_boundaries_point_at_sea_gets_no_station`.

**Jurisdiction: boundary proximity**
- API probe at (19.1197, 72.8464): `near_boundary` at 35.5 m, `station` None.
- JA `test_near_shared_boundary_requires_confirmation`.

**Jurisdiction: overlap or disagreement**
- JA `test_overlapping_polygons_are_ambiguous` returns `multiple` with `station` None.
- Frontend and backend disagreement: see the Node test above and D-8.

**Inside**
- API probe at (19.0176, 72.8562) returns `inside`, RAK Marg.
- JA `test_real_boundaries_each_polygon_interior_point_maps_to_its_own_polygon` (re-checked: all 91 polygons were assessed, none skipped, and all 91 are `inside`).

**No authentication, persistence, verification or submission implied**
- Endpoint docstrings (`main.py:107`, `:125`) and the report fields above.
- Nothing is written to disk by either endpoint (code inspection).

---

## 3. Defects

Severity scale:
- **High:** could mislead a complainant or officer during normal use, or leak data by default.
- **Medium:** misleading output or a privacy gap under a plausible condition.
- **Low:** an edge case, or a fault that needs an internal error.

None are High. **No fixes were made in this task.** No repository tests were added either, because the deliverable was limited to this report. Each reproduction step below is enough to turn into a regression test once a fix is approved.

### Summary table

| ID | Severity | Area | Defect |
|---|---|---|---|
| D-1 | Medium | Frontend | An absent or unknown review route is shown as "Ready for police review". |
| D-2 | Medium | Workflow | If `validate_and_route` fails, the report has `review: null`, so no route is recorded. Combined with D-1, the UI shows "Ready for police review". |
| D-3 | Medium | Workflow | If `intake` fails, the API report omits the complainant's statement. |
| D-6 | Medium | Missing details | "I do not know \<anything\>" marks *who* as `unknown_to_complainant`. |
| D-7 | Medium | Contradictions | Dates without a year are never compared. A conflict is silently missed and the report shows `contradictions: []`. |
| D-9 | Medium | Language | Hinglish and Marathi statements yield almost no facts, and details that were given are listed as missing. |
| D-10 | Medium | Privacy | The tracing guard misses `LANGSMITH_TRACING_V2=true` and `LANGCHAIN_TRACING=true`, both of which LangSmith treats as on. |
| D-4 | Low | Workflow and API | If `build_report` fails, `main.py` raises a KeyError and returns HTTP 500. The frontend keeps the local draft. |
| D-5 | Low | Workflow | A replacement attempt is rejected by aborting the whole run, with no report and HTTP 500, rather than recording an error and routing to human review. |
| D-8 | Low | Frontend | `reconcileJurisdiction` treats backend `near_boundary`, `outside_all` or `multiple` with no station as agreeing with a local `inside` result. |

All reproduction commands below run from the project root with `GEMINI_API_KEY="" GOOGLE_API_KEY="" BANDHOO_SKIP_DOTENV=1 .venv/bin/python -B`.

### D-1 (Medium): unknown review route displayed as "Ready for police review"

- **Location:**
  - `src/App.jsx:1575`: `structured.summary.route === 'human_review_required' ? 'Needs human review' : 'Ready for police review'`
  - `src/trustSafety.js:176` returns `'unknown'` when `report.review` is missing.
- **Reproduction:**
  1. Run `node -e "import('./src/trustSafety.js').then(m => console.log(m.structuredSummary({header:{}}).route))"`. It prints `unknown`.
  2. Feed that summary to the ternary at `App.jsx:1575`. It renders "Ready for police review".
- **Impact:** the UI shows a review-readiness claim the workflow never made.
- **Suggested fix (not applied):** show "Ready for police review" only when `route === 'ready_for_police_review'`, and show "Needs human review" in every other case.

### D-2 (Medium): `validate_and_route` failure leaves the report with no review decision

- **Location:**
  - `complaint_engine/graph.py:314`–`327`: `_guard` returns errors only.
  - `graph.py:228`: `human_review` sets no `review`.
- **Reproduction:**
  ```python
  from complaint_engine import build_graph, run_structuring
  from complaint_engine.models import ComplaintStructureRequest
  def boom(s, c): raise RuntimeError("x")
  st = run_structuring(ComplaintStructureRequest(statement="On 14/10/2026 at 9 pm two men snatched my phone near Andheri Station."),
                       graph=build_graph({"validate_and_route": boom}))
  print(st["report"]["review"])   # None
  ```
- **What works:** the graph does take the `human_review` branch (`_after_validation`).
- **What fails:** the record a consumer receives carries no route. With D-1, the frontend would say "Ready for police review".
- **Suggested fix (not applied):** have `human_review` set a `ReviewDecision(route="human_review_required", …)` when none exists.

### D-3 (Medium): `intake` failure drops the statement from the API report

- **Reproduction:** as for D-2, with `{"intake": boom}`. The report shows `review.route == "human_review_required"` and `complainant_statements == []`. `st["raw_input"].statement` still holds the text, but `main.py:130` returns only `report`.
- **Impact:** "failures route to human review without losing the input" holds inside the graph state but not in the API response. The frontend still has its local draft, so a frontend user does not lose text. An API-only consumer would.
- **Suggested fix (not applied):** have `build_report` fall back to `raw_input` (labelled as unprocessed) when no `Statement` was created.

### D-4 (Low): `build_report` failure returns HTTP 500

- **Reproduction:** with `{"build_report": boom}`, `"report" in st` is `False` and `errors` names `build_report`. `main.py:130` then raises `KeyError: 'report'`, and FastAPI returns 500.
- **Impact:** the frontend shows "unavailable" and keeps the draft (`App.jsx:609`). No false claim is made. This needs an internal fault to trigger.

### D-5 (Low): immutability violation aborts the run

- **Reproduction:** probe P5. A node returning `{"original_statement": Statement.create("S1", "original", "other")}` raises `ImmutableStatementError`. No state or report is returned, and through the API this would be a 500.
- **What works:** the safety property holds, because the replacement is rejected.
- **What fails:** the routing property does not. This failure is not recorded and sent to human review. The existing test asserts the abort, so this is current design, not an accident. It is listed so that a reviewer can decide whether aborting is the intended behaviour.

### D-6 (Medium): "I do not know …" is attributed to *who*

- **Location:** `complaint_engine/checks.py:43`. The *who* pattern matches any `I/we do not / don't / did not / didn't know|recognise …`, whatever follows.
- **Reproduction:**
  ```python
  st = run_structuring(ComplaintStructureRequest(statement="Someone took my bag at Dadar Market. I do not know the date."))
  print({m.field: m.status for m in st["missing"]})
  # {'when': 'unknown_to_complainant', 'who': 'unknown_to_complainant', ...}
  ```
- **Impact:** the record says the complainant doesn't know who was involved, which they never said. The *who* question is then suppressed.
- **Note:** the passing test `test_explicit_denial_and_unknown_are_not_reported_as_missing` uses "I don't know who took it", so it cannot catch this.

### D-7 (Medium): contradictions in dates without a year are not detected

- **Reproduction:** probe P6. Statement "On 14 October two men took my bag." plus clarification "It was on 15 October." gives dates `????-10-14` and `????-10-15`, and `contradictions: []`.
- **Impact:** the most common way of giving a date is not checked, and an empty list can read as "consistent". The full-year restriction is deliberate, to avoid false flags. However, it is not stated in change record §6 or in the report output.
- **Suggested fix (not applied):** compare month and day when both lack a year, or add a report note that yearless dates are not compared.

### D-8 (Low): status-only backend disagreement treated as agreement

- **Location:** `src/trustSafety.js:139` (`reconcileJurisdiction`). It flags a conflict only when `backend.station` is set and differs.
- **Reproduction:** `probe_front.mjs` prints the following.

  | Local result | Backend result | Reconciled output |
  |---|---|---|
  | `inside` (Alpha) | `{station: null, status: 'near_boundary'}` | `{confirmed: true, stationName: 'Alpha', status: 'inside'}` |
  | `inside` (Alpha) | `{station: null, status: 'outside_all'}` | `{confirmed: true, stationName: 'Alpha', status: 'inside'}` |

- **Impact:** today the root and `public/` GeoJSON copies are identical (sha256 prefix `f88332242a4bc833`), and both sides use 100 m, so the two results agree in practice. This only matters if the copies diverge.
- **Note:** the Node test `backend result cannot override local containment` covers named-station disagreement only.

### D-9 (Medium): non-English statements yield almost no facts

- **Reproduction:** probe P8.
  - "Kal raat 9 baje do aadmi ne Dadar station ke paas mera phone cheen liya. Koi chot nahi aayi." The only fact extracted is the denial "Koi chot nahi". *when*, *where* and *who* are listed as missing.
  - The same account in Marathi: no facts extracted, and the same fields are listed as missing.
- **Impact:** the missing-information list and the questions wrongly say that time, place and persons were not given. Change record §6.1 states the English-centred limitation but not this consequence.
- **Suggested handling:** treat this as a known limitation for internal testing. Before any wider use, either add a language check that routes non-English statements to human review with a note, or add reviewed multilingual patterns.

### D-10 (Medium): tracing guard does not cover every LangSmith switch

- **Location:** `complaint_engine/graph.py:341`. It checks `LANGSMITH_TRACING` and `LANGCHAIN_TRACING_V2` only.
- **Background:** LangSmith (`.venv/.../langsmith/utils.py:139`) enables tracing on `{LANGSMITH,LANGCHAIN}_TRACING_V2`, falling back to `{LANGSMITH,LANGCHAIN}_TRACING`, when the value is `"true"`.
- **Reproduction:** run `build_graph()` once under each variable. No graph was invoked, so no data was sent.

  | Variable set to `true` | `tracing_is_enabled()` | `build_graph()` |
  |---|---|---|
  | `LANGSMITH_TRACING_V2` | True | built (not refused) |
  | `LANGCHAIN_TRACING` | True | built (not refused) |
  | `LANGSMITH_TRACING` | True | refused |

- **Further gap:** the default graph is cached on first use (`graph.py:368`–`372`), so the check is not repeated if the environment changes later.
- **Impact:** if an operator sets one of the unguarded variables and a LangSmith API key exists, complaint text could be sent to LangSmith. `langsmith` is installed in `.venv`.
- **Suggested fix (not applied):** ask `langsmith.utils.tracing_is_enabled()` directly, or check all four variables; and check per run.

---

## 4. Tests that exercise less than their names claim

| Test | Finding |
|---|---|
| JA `test_get_jurisdiction_endpoint_inside_a_polygon` | **The inside branch never runs.** Its test point (the vertex average of `features[0]`, Cuffe Parade) assesses as `near_boundary`, so only `station is None` is checked. The name claims an inside result. The real inside case is covered by the API probe (RAK Marg) and by `test_real_boundaries_each_polygon_interior_point…`, not by this test. |
| CG `test_clean_case_routes_to_police_review_without_claiming_verification` | The route assertion is conditional on `jurisdiction.status == "inside"`. It does run today (the RAK Marg point is inside), but the test would pass silently if the boundary data changed. The unconditional route test is `test_police_review_route_with_synthetic_boundaries`. |
| CG `test_node_failure_is_recorded_and_routed_to_human_review` | Covers a fault in `detect_contradictions` only. Faults in `intake`, `validate_and_route` and `build_report` behave differently (D-2, D-3, D-4). |
| CG `test_explicit_denial_and_unknown_are_not_reported_as_missing` | Uses "I don't know who…", so it cannot detect the over-broad *who* pattern (D-6). |
| CG `test_all_expected_nodes_present` | Checks set membership only. The order is covered by `test_nodes_run_in_order_and_report_is_built`. |
| Node `backend result cannot override local containment` | Tests named-station conflict only, not a status-only disagreement (D-8). |
| Node `backend unavailable state carries no legal sections or advice` | Tests the helper, not that `App.jsx` calls it. The wiring was checked by inspection (`App.jsx:510`). |
| Node `App.jsx contains no …` (3 tests) | Static source-text absence checks. They do not render the UI, so reworded claims or claims built at runtime would not be caught. There are no DOM or component tests. |
| `tests/test_frontend_trust_safety.py` | Silently skipped when Node is not installed. It ran (16/16) in this validation. |
| (none) | No repository test asserts that `/api/v1/complaints/structure` makes no external call or passes no extractor. This is covered only by probe P10 and code inspection. |

---

## 5. Test and build results

| Check | Command | Result |
|---|---|---|
| Full offline suite (`.venv`, Python 3.14.6, langgraph 1.2.16) | `GEMINI_API_KEY="" GOOGLE_API_KEY="" BANDHOO_SKIP_DOTENV=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider` | **267 passed**, 1 warning (`google.genai` DeprecationWarning about `_UnionGenericAlias`) |
| Original suite (system Python, no LangGraph) | `/usr/local/bin/python3.14 -B -m pytest -q -p no:cacheprovider --ignore` the 3 new test files | **228 passed** (the same count as before the change) |
| New tests only | the 3 new files | **39 passed** |
| Frontend unit tests | `node --test src/trustSafety.test.js` (Node v26.11.1) | **16/16 passed** |
| Production build | `npx --no-install vite build --outDir <scratch> --emptyOutDir` (vite 8.0.16) | **OK**: 18 modules; JS 395.55 kB (gzip 117.61 kB); CSS 14.01 kB. Output went to scratch, not `dist/`. |
| Lint | `npx --no-install eslint src` | 3 findings: 2 errors and 1 warning, all of which predate the change (unused `React`; `updateLocation` accessed before declaration at `App.jsx:341`; `useEffect` dependencies at `:405`). |
| Fallback benchmark | `benchmark/evaluate_benchmark.py` (fallback mode), output to scratch | Compared with the pre-change run: **only 7 differences**, 6 `elapsed_sec` values and `evaluation_date_utc`. All metrics and case results are identical. For example: procedural correctness 34.38% (11/32), gate false-positive rate 0.00% (0/43), 37 material errors. |
| Committed benchmark report, labels, thresholds | sha256 comparison | Unchanged (§8) |

---

## 6. Residual limitations

### 6.1 Privacy

1. **Map tiles:** these are requested from `tile.openstreetmap.org` (`App.jsx:310`). Tile coordinates reveal the area being viewed. No statement text is sent.
2. **Classification uses Gemini when a key is set:** `/api/classify-offence` sends the narrative to Gemini whenever a key is configured, and the frontend calls it (`App.jsx:474`). Its suggestions and procedural note are still displayed, relabelled as machine-generated. This sits outside the new workflow and under the separate legal gates.
3. **Tracing:** see D-10.
4. **CORS:** `allow_origins=["*"]` (`main.py:21`–`25`). Any web page open in the same browser can call the local API.
5. **Hard-coded API address:** the frontend calls `http://localhost:8001` over plain HTTP. There is no authentication.
6. **No data-handling policy is approved.** Use synthetic data only.

### 6.2 Jurisdiction data

1. The provenance of the boundary GeoJSON is unverified. It is labelled "unverified" in every response.
2. Station coordinates are polygon centroids. There are no contacts, addresses or ward data, and none were added.
3. The 100 m near-boundary threshold is a design choice that hasn't been validated.
4. GPS accuracy is not used.
5. Points inside a polygon but within 100 m of the coast or the outer edge are reported as `near_boundary`, not `inside`. This is safe but strict.
6. Two copies of the GeoJSON must stay identical, because D-8 depends on it. They are identical today.

### 6.3 Language

1. Extraction is English-centred (D-9). Hinglish handling is limited to some negation patterns. Marathi text yields no facts.
2. The Marathi UI strings were written by the implementing session and need review by a native speaker.
3. No measurement of extraction accuracy exists. No accuracy claim is made.

### 6.4 Reproducibility

1. `langgraph>=1.2.16` has no upper bound.
2. `.venv` was created with `--system-site-packages`, so results depend on the system Python packages.
3. There is no lock file.

---

## 7. Is it safe for further internal testing?

**Yes, with synthetic data only, under these conditions:**

1. **Before relying on the structured-record panel**, fix or explicitly accept D-1 and D-2 together. They are the only path by which the UI could show a review-readiness label the workflow didn't produce.
2. **Before running anywhere a LangSmith key might exist**, fix D-10, or confirm that none of `LANGSMITH_TRACING`, `LANGSMITH_TRACING_V2`, `LANGCHAIN_TRACING` or `LANGCHAIN_TRACING_V2` is set.
3. **Track D-3 to D-9 as open defects.** Testers should know that:
   - non-English statements produce wrong missing-detail lists;
   - "I do not know …" mislabels *who*;
   - contradictions between dates without a year are not flagged.
4. **No real complainant data,** and no use with the Gemini key set, until a data-handling policy is approved.
5. **No production, legal or police use.**
   - The existing blockers in `reports/release_blocker_register.md` stay open.
   - The Section 173(3) and Maharashtra amendment gates are unaffected by this change.
   - This validation is not an approval of them.

**Not demonstrated:** independent review (this validation is not independent), accuracy of extraction, police acceptance of the draft format, or any submission, verification, persistence or audit capability. None of these exist.

---

## 8. Change control

### 8.1 This validation task

Before starting this task, sha256 hashes of all 102 project files were recorded, excluding `.git`, `.venv`, `node_modules`, caches and `.env`. The table below shows the after-task check (output in Appendix B).

| Check | Expected |
|---|---|
| Project files differing from the pre-task hashes | none |
| Files added | only `reports/trust_safety_langgraph_validation.md` |
| Baseline snapshot `bandhoo_baseline_20261020T210347` (manifest `5125ea46…`, 105 files) | self-check passes, read-only |
| Rollback snapshot `bandhoo_pre_trustsafety_langgraph_20261021T084552` (manifest `696610de…`, 118 files) | self-check passes, read-only |
| Pre-migration backup (`d053ce3de31ef17d`) | unchanged, read-only |
| Appendix B | 16/17 match, `main.py` the only mismatch |
| `__pycache__` | none newly written |

### 8.2 Differences from the rollback snapshot

Every difference is intended; nothing else changed.

**Modified (3 files):**

| File | Snapshot sha256 (prefix) | Current sha256 (prefix) |
|---|---|---|
| `main.py` | `54ecd10e5097b1ad` | `ea8b6b43cd54e2f1` |
| `requirements.txt` | `3e024a17792c79f0` | `797066cb28ff7aec` |
| `src/App.jsx` | `0a2001554785f3a0` | `3e8f87223770122d` |

**Added (12 files, plus this report):**

| File | sha256 (prefix) |
|---|---|
| `complaint_engine/__init__.py` | `d0c0347f6f2c766c` |
| `complaint_engine/checks.py` | `f367198ee1f7e9d0` |
| `complaint_engine/extraction.py` | `3a707ce6b064e9ee` |
| `complaint_engine/graph.py` | `254c78b935e4f222` |
| `complaint_engine/jurisdiction.py` | `94576e146bd1b6b2` |
| `complaint_engine/models.py` | `071ed91114c2cba8` |
| `src/trustSafety.js` | `56c2775ecbc9316e` |
| `src/trustSafety.test.js` | `cb965610f1e2a1e5` |
| `tests/test_complaint_graph.py` | `f6681c64b1eee49b` |
| `tests/test_jurisdiction_and_api.py` | `2c059dc30339d934` |
| `tests/test_frontend_trust_safety.py` | `d98a2e36875b5e6e` |
| `reports/trust_safety_langgraph_change_record.md` | `f4ee4fd149b63e34` |

**Unchanged:**
- the corpus (`bns_rag_dataset.json` and its `public/` copy);
- benchmark labels (`benchmark/bns_synthetic_benchmark_50.json`);
- `benchmark/evaluate_benchmark.py` and the committed benchmark reports;
- `legal_engine/`;
- the GeoJSON and station data.

### 8.3 Blocker-register Appendix B mismatch (not concealed)

`reports/release_blocker_register.md` Appendix B lists `main.py` as `54ecd10e5097b1ad`. The current `main.py` is `ea8b6b43cd54e2f1`. The change is intended and explained in change record §2, but **the register has not been edited**. It still records the old value, and the mismatch is reported here.

### 8.4 Proposed baseline refresh (for approval; not applied)

**Proposed record: BR-2026-10-21-01**

**Reason:**
- the approved trust-and-safety fixes;
- LangGraph integration (owner decision, Round 23).

**Exact intended differences:** the 3 modified and 12 added files in §8.2, with the sha256 values listed there. This validation report would be a 13th addition if the approver wants it included.

**Blocker-register change:**
- update Appendix B `main.py` from `54ecd10e5097b1ad` to `ea8b6b43cd54e2f1`;
- add the new files to a new appendix row group;
- keep the old value in an "as of 2026-10-20 baseline" note.

No blocker status changes. All blockers stay open.

**Preconditions:**
1. An authorised reviewer, separate from this session, confirms D-1 to D-10 and decides which must be fixed before the refresh.
2. If fixes are made, hashes are recomputed after them. The values above then become stale and must not be used.
3. Before refreshing, the full suite is re-run at 267 or more passing tests, along with the original suite at 228, the Node suite and the build.

**Procedure after approval:**
1. Create a new snapshot directory, e.g. `Bandhoo_snapshots/bandhoo_baseline_<timestamp>`, using the same method as the existing snapshots: copy the project, then record `MANIFEST.sha256`, `PERMISSIONS.txt` and `COMPARISON_SUMMARY.json`, then `chmod -R a-w`.
2. Record the new manifest sha256 in the blocker register through the authorised review process.
3. **Keep both existing snapshots.** Do not modify or delete either:
   - `bandhoo_baseline_20261020T210347`;
   - `bandhoo_pre_trustsafety_langgraph_20261021T084552`.
4. Keep the pre-migration backup unchanged.

**Approval:** not given. No approver has been named, and none is invented here.

### 8.5 Rollback

Follow change record §7 as written. It:
- verifies the snapshot manifest;
- restores the 3 modified files with their recorded permissions;
- moves the added files aside without deleting them;
- re-checks hashes, expecting 0 mismatches;
- runs the original suite on system Python, expecting 228 passed.

Two additions:

- **Move this report aside too.** Neither this validation report nor the change record is in the snapshot. Move both aside with the other added files, or keep them as history.
- **Use one fixed destination directory.** The `mv … "$P/../Bandhoo_rolled_back_"*/` glob in §7 is ambiguous if more than one `Bandhoo_rolled_back_*` directory exists. Set a variable once, e.g. `RB="$P/../Bandhoo_rolled_back_$(date +%Y%m%dT%H%M%S)"; mkdir -p "$RB"; mv … "$RB"/`.

---

## Appendix A: Probe commands

All probes run from the project root with `GEMINI_API_KEY="" GOOGLE_API_KEY="" BANDHOO_SKIP_DOTENV=1 .venv/bin/python -B <probe>`. The scripts live in the session scratchpad, not in the repository.

| Probe | What it does |
|---|---|
| `probe_graph.py` P1–P10 | Compiled edges; execution log; intake and `attribute_sources` faults; statement replacement; yearless dates; "I do not know"; Hinglish and Marathi; negation edge cases; socket-blocked workflow and API run. |
| `probe_api.py` | FastAPI `TestClient` calls to `/api/get-jurisdiction` (missing, partial, NaN, outside, near-boundary, inside), `/api/v1/complaints/structure` (extra field, status injection, empty statement, draft fields), `/api/classify-offence` and `/api/bns-stats`. |
| `probe_front.mjs` | `reconcileJurisdiction` disagreement cases, `structuredSummary` without a review, and `statusLadder({})`. |
| Inline checks | Faults in `extract_facts`, `validate_and_route` and `build_report`; tracing-guard check for each environment variable; Cuffe Parade test-point status; interior-point coverage (91/91). |

## Appendix B: Post-task integrity check output

Run on 2026-10-21 after this report was written.

| Check | Result |
|---|---|
| `shasum -a 256 -c` against the 102 pre-task hashes | 0 mismatches |
| Files added since the pre-task list | `reports/trust_safety_langgraph_validation.md` only |
| Files removed | none |
| Baseline snapshot `bandhoo_baseline_20261020T210347` | manifest `5125ea461052efb0…`, 105 files, 0 failures, 0 writable files |
| Rollback snapshot `bandhoo_pre_trustsafety_langgraph_20261021T084552` | manifest `696610de0ba7023b…`, 118 files, 0 failures, 0 writable files |
| Pre-migration backup | `d053ce3de31ef17d`, `-r--r--r--` |
| Appendix B | 16/17 match; mismatch: `main.py` (intended; §8.3) |
| New `*.pyc` or `.pytest_cache` files | none |
| `git status` | same entries as at the start of the task, plus no new top-level entries (`reports/` was already untracked) |
