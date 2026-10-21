# Bandhoo: Complaint Structuring and Verification Workflow Implementation Plan

**Prepared:** 2026-10-21 by the Bandhoo maintainer session, for the project owner (PO), the maintainer (MNT), the evaluation lead (EL) and the qualified legal reviewers (QLR).
**Status:** **Plan only. Nothing is implemented or approved.** No code, prompt, test, corpus, benchmark label, threshold or existing report has been changed. Bandhoo remains internal-testing-only.

**Product goal (as set by the PO):**
- Turn a complainant's raw account into a standardised, police-ready complaint, and help police verify the account and its evidence quickly.
- Bandhoo is **not** a legal guide or chatbot for complainants.
- It does not judge truthfulness, guilt or credibility, and it does not replace police judgment.

**How the findings were established:**
- Read-only inspection of `main.py`, `legal_engine/`, `src/App.jsx`, the station and jurisdiction data, `requirements.txt`, the tests and the reports.
- One offline simulation (§5.1) using synthetic points and the repository's own data.
- No Gemini call, scraper run or `.env` access.

---

## 1. Current capabilities and missing capabilities

### 1.1 What exists today

| Area | Current implementation | Assessment against the new goal |
|---|---|---|
| API | FastAPI app in `main.py` (port 8001), three endpoints: `POST /api/get-jurisdiction`, `POST /api/classify-offence`, `GET /api/bns-stats`. CORS `allow_origins=["*"]`. | No complaint, case, evidence, clarification, report or submission endpoint. No authentication. No persistence: every request is stateless. |
| Narrative analysis | `LegalAnalysisService.analyze_complaint` (`legal_engine/service.py`): synonym normalisation, BM25 retrieval, optional Gemini evaluation, deterministic fallback, procedural audit. Returns `OffenceClassificationResponse` (`legal_engine/schemas.py`). | Built for **legal classification**, not complaint structuring |
| Fact separation | `FactExtractionBlock` with four lists of free-text strings: `stated_facts`, `inferred_facts`, `negated_events` and `missing_facts_to_clarify` (`schemas.py` lines 15–31). Gemini mode: filled from Gemini's JSON (`service.py` 1166–1180), then `_enrich_facts_block` (451–514). Fallback mode: `stated_facts` = the first four sentences split on "." (`service.py` 1382); `missing_facts_to_clarify` = fixed generic questions. Negations: regex patterns, including Hindi/Hinglish (`detect_negations`, line 169; `NEGATION_PATTERNS`). | A useful starting point, with gaps: (a) no link from any "stated fact" back to the complainant's words. In Gemini mode these are Gemini's paraphrases, so they could contain invented details. (b) Missing items are oriented to **legal elements** (e.g. 303(2) proviso questions), not to what a police officer needs to verify. (c) No people, dates, locations, amounts or evidence as structured entities. (d) No contradiction detection. (e) No evidence model. |
| Amounts | `legal_engine/amounts.py`: currency parsing with stated/ambiguous/unstated status | Reusable for loss extraction and amount contradictions |
| Jurisdiction (backend) | `/api/get-jurisdiction`: nearest point in a KD-tree over `police_stations_data.json` coordinates (Euclidean on latitude/longitude) | **Methodologically unsound for jurisdiction** (§5.1) |
| Jurisdiction (frontend) | `src/App.jsx` first runs a client-side point-in-polygon test against `mumbai_police_jurisdictions.geojson`. It then calls the backend and **overwrites the polygon result with the backend's nearest-centre result** (`App.jsx` ~440–475). | The correct method is overridden by the weaker one |
| Station data | 91 stations. Every station's latitude and longitude is **exactly its polygon's centroid** (0 m difference for all 91). `contact`, `address` and `ward` are empty for all 91. The GeoJSON has 91 non-overlapping polygons. Provenance of the source file (`mumbai_police_station.kml_`) and its date are not documented. | No verified station address, contact or official boundary source |
| Geocoding | The frontend sends coordinates and typed addresses to OpenStreetMap Nominatim (`App.jsx` 488, 611) | Third-party data transfer with no consent, privacy notice or usage-policy handling |
| "FIR" flow (frontend) | Labels "LODGE ELECTRONIC FIR" and "Authenticate & Register FIR". `handleFIRSubmit` creates a **random "FIR number"** `MUM-<1000–9999>/<year>` in the browser and marks it submitted (`App.jsx` 670–680). | **Misrepresents filing.** Nothing is sent to police. |
| Evidence upload (frontend) | Stores only the file name and size. The UI says "Identity document **verified**" and "Supporting document **verified**". An identity document (Aadhaar / DL / passport) is **required** before "submit". | **Misrepresents verification.** It also collects sensitive identity documents without need. |
| Police fields (frontend) | Pre-filled defaults: officer "R. K. Patil, Inspector", status "Investigation Started", remarks "Case registered online, preliminary inquiry initiated.", offence "Theft", sections "Section 303 (Theft)". Shown on the receipt (`App.jsx` 284–286, 1647–1649). | **Fabricated police entries** |
| Dispatch email (frontend) | Builds `<station>.ps@mumbaipolice.gov.in` from the station name (`App.jsx` 1686, 1732). The body states the FIR was "registered electronically under Section 173 … BNSS" and "(E-Signed Authentically Digitally)". | **Invented contact address and false status claims.** No dataset holds any station email. |
| Frontend legal fallback | If the backend is offline, a keyword fallback assigns hard-coded BNS sections and advice such as "Initiate FIR registration immediately" (`App.jsx` ~570–590) | Unaudited legal advice, outside every backend safeguard and outside the legal review gates |
| Tests | 228 offline tests (11 files) cover the legal engine, corpus and benchmark metrics | **No test** covers `main.py` endpoints, jurisdiction, the frontend, or any structuring behaviour |
| Evaluation | Benchmark of 50 synthetic cases with fields such as `material_missing_facts` and `expected_uncertainty`. `reports/independent_evaluation_plan.md`. | Measures legal classification, not structuring or police usability |
| LangGraph | **Not used** (§8) | — |

### 1.2 Missing capabilities

1. Case record with an immutable original statement and append-only clarifications.
2. Entity extraction (people, roles, dates and times, locations, events, losses, injuries, witnesses, evidence references), each grounded in the exact words of the source.
3. Separate status for each item: complainant statement / evidence supplied / independently verified / unverified claim / missing / AI inference. Separate assertion polarity: asserted / explicitly denied / not provided / uncertain.
4. Police-oriented missing-information checklist and limited follow-up questions.
5. Contradiction detection that is neutral, preserves both statements, and lets the complainant clarify.
6. Evidence intake as **metadata and custody** (what was supplied, when, its hash), never as authentication.
7. Standardised police-ready report and officer verification checklist.
8. Polygon-based jurisdiction with uncertainty handling, and an honest submission-status model.
9. Verification trail (who, what, how, when), access control and privacy controls.
10. Tests and a police-review evaluation for all of the above.

---

## 2. Proposed end-to-end workflow

```
Complainant account (text, any supported language)
   │
   ▼
[1] Intake: store the original statement immutably (text, language, received_at, SHA-256)
   │
   ▼
[2] Extraction: deterministic extractors (dates/times, amounts, phones, vehicle numbers, negations)
   │            + optional LLM extractor, which must quote a source span for every item
   │            → span check: an item whose quoted span is not found verbatim is rejected,
   │              or relabelled as an AI inference
   ▼
[3] Classification of each item: provenance, verification status and polarity (§4)
   │
   ▼
[4] Gap and conflict checks: missing-information checklist (police-oriented);
   │                         contradiction rules across statements and items
   ▼
[5] Clarification loop (only if needed): at most N targeted questions per round.
   │   Answers are stored as NEW statements; originals are never edited.
   │   "Don't know" is recorded as unknown_to_complainant, not as missing.
   ▼
[6] Evidence intake: metadata, hash and custody; linked to items; status "supplied – not examined"
   │
   ▼
[7] Jurisdiction: point-in-polygon on the incident location with an uncertainty status (§5)
   │
   ▼
[8] Report generation: standardised police-ready report (§2.1) plus officer verification checklist.
   │   Candidate legal provisions appear in a separate, labelled block (§2.2).
   ▼
[9] Police review (authenticated officer): records verification events (method, result, time).
   │   Only this step can mark an item "independently verified".
   ▼
[10] Status: draft → ready for police review → presented to police (recorded by police)
     → [electronic submission only with an authorised integration, of which none exists]
```

Every step writes trail events (§6). Steps 1–8 run without police. Steps 9–10 need authenticated police users and are gated (stage 5).

### 2.1 Police-ready report (fixed section order)

| # | Section | Content rules |
|---|---|---|
| 1 | Header | Case ID, report version, generated time, generation mode (deterministic / LLM-assisted, using the existing `inference_status` values), and a fixed banner: "Prepared from the complainant's account. Not a registered FIR. Contents are unverified unless marked verified by a police officer." |
| 2 | Complainant and incident details | Complainant (as provided), incident date and time (as stated, with any normalised value marked "derived"), location (as stated; geocode marked "derived"), jurisdiction status (§5) |
| 3 | Chronology | Events ordered by stated or derived time. Each entry cites its statement and span. Undated events are listed separately, never placed by guessing. |
| 4 | Persons and alleged roles | Complainant, victim, suspects, witnesses, others, each with the role **as alleged by the complainant** and its source span |
| 5 | Losses and injuries | Items and amounts as stated (with any amount ambiguity), injuries as stated, any medical reference |
| 6 | Evidence and witness references | Each evidence item: type, description, supplied time, hash, linked claims, status ("supplied – not examined" by default) |
| 7 | Missing information | Open items, questions asked, answers, "unknown to complainant" |
| 8 | Contradictions requiring clarification | Neutral template: "Statement S1 (time) says X; statement S3 (time) says Y". Status: open / clarified by complainant / noted by officer. **Never labelled as dishonesty.** |
| 9 | AI-generated inferences | Listed separately, each with its basis items and method. Never mixed into sections 2–6. |
| 10 | Potentially relevant legal provisions | Separate block (§2.2) |
| 11 | Officer verification checklist | Generated checklist (§4.6) with blank result fields |
| 12 | Record of changes and clarifications | Trail summary: statements, clarifications, evidence additions, verification events, with times and actors |

Style: short factual lines, complainant's words quoted where material, no adjectives about credibility, no legal essay. Output as JSON (canonical) and a printable rendering; the printable form is derived from the JSON.

### 2.2 Legal provisions block

- Source: the existing `/api/classify-offence` result, **unchanged**.
- Shown as "Potentially relevant provisions (machine-generated, not legally reviewed)", with each section's status (`is_cognizable` / `is_bailable`, `None` = unverified), `inference_status` and `unverified_exclusions`.
- **`recommended_action` (procedural advice) is excluded** from the report until the separately gated legal reviews are resolved: Change A (RB-52/Q-16), Change B/RB-53 (Q-01 Step 1, Q-17), and Change C (D-1 to D-3). This plan does not alter, decide or bypass any of those gates.
- Maharashtra status: L.C. Bills VI and XVII and L.A. Bill XXX remain **UNKNOWN and are not treated as law** (`reports/section_173_3_g1_g2_verification.md`). The block must not reflect them.

---

## 3. Proposed data structures and API changes

### 3.1 Principles

- **Additive and backward compatible:**
  - `OffenceClassificationResponse` and `/api/classify-offence` are not changed;
  - `/api/get-jurisdiction` stays as it is until stage 4, then is deprecated in favour of a new resolver.
- A new package is proposed: `complaint_engine/` (sibling of `legal_engine/`), with plain functions and Pydantic models, matching the existing service style.
- The canonical record is JSON. The printable report is generated from it.

### 3.2 Core models (Pydantic; proposed fields)

| Model | Key fields |
|---|---|
| `Statement` | `statement_id`, `case_id`, `kind` (`original` / `clarification` / `answer`), `text` (verbatim), `language`, `received_at` (server UTC), `sha256`, `answers_question_id` (optional), `supersedes`: **never**. Statements are immutable. |
| `SourceSpan` | `statement_id`, `start`, `end`, `quote` (must equal `statement.text[start:end]`) |
| `MaterialItem` | `item_id`, `kind` (`person`, `role`, `datetime`, `location`, `event_action`, `loss_property`, `injury`, `witness`, `vehicle`, `communication`, `other`), `value_raw`, `value_normalised` (optional, labelled `derived`), `spans: [SourceSpan]`, `provenance`, `verification_status`, `polarity`, `display_category` (derived; §4.1), `extraction_method` (`rule:<name>` / `llm:<model>` / `form_entry`), `created_at` |
| `EvidenceItem` | `evidence_id`, `type` (photo / document / receipt / screenshot / medical record / CCTV reference / other), `description_by_complainant`, `file` (optional: name, size, MIME type, `sha256`, `received_at`) or `reference_only: true`, `linked_item_ids`, `custody_status` (`supplied_not_examined` default; `examined_by_police`), `authenticity_status` (`not_assessed` default; only a police verification event may change it) |
| `MissingInfo` | `missing_id`, `field`, `why_needed` (operational wording), `priority`, `question_id` (optional), `status` (`open` / `answered` / `unknown_to_complainant` / `declined` / `not_applicable`) |
| `Question` | `question_id`, `text`, `targets` (missing or contradiction IDs), `asked_at`, `round` |
| `Contradiction` | `contradiction_id`, `field`, `item_ids`, `spans` (both sides, quoted), `detector` (`rule:<name>` / `llm:<model>`, LLM ones labelled AI inference), `neutral_summary`, `status` (`open` / `clarified_by_complainant` / `noted_by_officer`), `clarification_statement_id` (optional) |
| `Inference` | `inference_id`, `text`, `basis_item_ids`, `method`, `requires_verification: true` (always) |
| `VerificationEvent` | `event_id`, `target` (item or evidence ID), `verifier` (authenticated officer ID and role, from the session, never typed), `method` (free text plus a code, e.g. "inspected original document", "contacted witness"), `result` (`consistent` / `inconsistent` / `could_not_verify` / `not_applicable`), `note`, `at` |
| `JurisdictionResult` | `location_source` (`device_gps` / `map_pin` / `geocoded_address` / `typed_only` / `unknown`), `accuracy_m` (if known), `point`, `status` (`inside_one` / `near_boundary` / `outside_all` / `no_location`), `polygon_name`, `distance_to_boundary_m`, `boundary_dataset` (name, SHA-256, provenance status) |
| `SubmissionStatus` | `state` (`draft` / `ready_for_police_review` / `exported_by_complainant` / `presented_to_police` (police-recorded) / `electronically_submitted` (only with an authorised integration and its receipt)), `recorded_by`, `at`, `external_reference` (only from a real integration) |
| `TrailEvent` | `seq`, `event_id`, `case_id`, `at` (server UTC), `actor_type` (`complainant` / `system` / `ai` / `police`), `actor_ref`, `action`, `target_ref`, `payload_ref`, `prev_hash`, `hash` (hash chain for tamper evidence) |
| `ComplaintCase` | `case_id`, `schema_version`, `status`, `statements`, `items`, `evidence`, `missing`, `questions`, `contradictions`, `inferences`, `jurisdiction`, `legal_block` (stored copy of the classifier output plus its `inference_status`), `submission`, `trail_head_hash` |

### 3.3 Proposed endpoints (new; versioned under `/api/v1`)

| Method and path | Purpose | Stage |
|---|---|---|
| `POST /api/v1/structure` | **Stateless.** Text in → structured items, missing information, contradictions within the text, inferences. Nothing is stored. | 1 |
| `POST /api/v1/cases` | Create a case from an original statement. Returns case ID and structure. | 2 |
| `POST /api/v1/cases/{id}/statements` | Add a clarification or answer as a new statement. Re-runs the checks. | 2 |
| `POST /api/v1/cases/{id}/evidence` | Add evidence metadata (file optional; hash recorded) | 3 |
| `GET /api/v1/cases/{id}/report` | Police-ready report (JSON; printable rendering) | 3 |
| `POST /api/v1/jurisdiction/resolve` | Point-in-polygon resolution with status (§5) | 4 |
| `POST /api/v1/cases/{id}/verifications` | Officer verification events (**authenticated police role only**) | 5 |
| `GET /api/v1/cases/{id}/trail` | Trail export, with hash-chain check | 2 (complainant actions), 5 (police) |

### 3.4 Persistence (decision required)

There is no datastore today, and an earlier task scoped databases out. A verification trail requires durable, append-only storage.

**Proposal:** SQLite through the Python standard library `sqlite3` (no new dependency). Tables `cases`, `statements`, `events` (append-only), `evidence_meta`. Files are stored outside the repository, or not at all during internal testing (§6.2).

**PO decision required** (stage 0). The alternative is append-only JSON-lines files per case.

---

## 4. Representation of statements, evidence, gaps, contradictions and inferences

### 4.1 Two status dimensions, and the derived display category

Each item has a **provenance** (`complainant_statement` / `evidence_supplied` / `ai_inference` / `police_verification`) and a **verification status** (`unverified` / `supported_by_supplied_evidence` / `independently_verified` / `verification_inconsistent` / `could_not_verify`). It also has a **polarity** (`asserted` / `explicitly_denied` / `uncertain_hedged`). Missing information is a separate object, not an item.

The six required display categories are derived in this order (the first match applies):

| Display category | Rule |
|---|---|
| **Independently verified information** | At least one `VerificationEvent` from an authenticated officer with `result = consistent`. **No other path.** |
| **AI-generated inference** | `provenance = ai_inference`. This never changes into a fact, even if the complainant later confirms it: the confirmation becomes a new statement-derived item that cites the new statement. |
| **Supporting evidence provided** | `EvidenceItem` records and items whose only source is supplied material. Always shown with "supplied – not examined / not authenticated" until a police verification event says otherwise. |
| **Complainant's statement** | `provenance = complainant_statement`, with a valid span |
| **Unverified claim** | A complainant statement whose substance needs external confirmation (losses, injuries, identities, events involving others). In the report this is shown as a **flag on statement items**, and it is the default for every statement item. |
| **Missing information** | `MissingInfo` with `status = open` |

**Invariants**, enforced by tests:
- No item reaches "independently verified" without a police verification event.
- An upload never changes `authenticity_status`.
- An AI item never loses its AI label.
- Every statement item has at least one valid span.

### 4.2 Not provided, explicitly denied, uncertain

| Situation | Representation | Example |
|---|---|---|
| Not mentioned | `MissingInfo` (if the checklist field matters), status `open` | No time given |
| Explicitly denied | Item with `polarity = explicitly_denied` and a span | "No one was hurt". Reuses the existing `detect_negations` patterns (English and Hindi/Hinglish), extended, with span capture. |
| Complainant says they do not know | `MissingInfo.status = unknown_to_complainant`, citing the answer's span | "I don't know his name" |
| Hedged | Item with `polarity = uncertain_hedged` | "around 9 pm", "I think he had a knife" |
| Declined to answer | `MissingInfo.status = declined` | — |

### 4.3 Missing-information checklist (police-oriented, not legal elements)

**Core fields:**
- what happened;
- when (date; time or time window);
- where (place; landmark; whether a location point exists);
- who (complainant; victim if different; suspects or description; witnesses);
- loss or damage (items, value);
- injury and medical attention;
- evidence available (what, with whom).

**Incident-type extensions:** theft (item identifiers, when last seen); cyber or financial fraud (transaction IDs, bank or wallet, account, time); vehicle (registration, make, colour); assault (injuries, hospital).

**Question policy:**
- ask only for **open core fields that the officer needs**, at most 5 per round and at most 2 rounds;
- every question is neutral and short;
- no question suggests an answer ("Was it a knife?" is not allowed);
- the legal-element questions now produced by `_enrich_facts_block` (e.g. the 303(2) proviso) are **not** put to complainants. They stay inside the separate legal block.

### 4.4 Contradictions

- **Rule detectors** (deterministic, first):
  - different absolute dates for the same event;
  - times more than X minutes apart (X to be set in stage 2 tests);
  - different amounts for the same loss (reusing `amounts.py`);
  - different named places, or geocodes falling in different polygons;
  - suspect known in one place and unknown in another;
  - different counts of persons;
  - different descriptions of the same object (e.g. colour, registration).
  These run within a statement and across statements.
- **LLM-assisted candidates** (optional) are labelled AI inference and need a rule-checkable basis (both spans).
- **Handling:**
  - both quotes are shown side by side, and the complainant may clarify;
  - a clarification is a new statement, and the contradiction is marked `clarified_by_complainant`;
  - **both originals stay visible**;
  - nothing is resolved automatically;
  - no wording implies dishonesty;
  - unresolved items are passed to the officer as "requires clarification".
- **Evidence against statement** (e.g. a photo's embedded date differs from the stated date): shown as "for officer review" only. Metadata can be wrong or altered and is not assessed for authenticity.

### 4.5 AI inferences

Examples: a normalised date derived from "yesterday" (anchored to `received_at`), a suggested incident type, an LLM-suggested contradiction, and the legal block as a whole.

Each inference records its basis items and method, is listed in report section 9, and is never merged into the factual sections.

### 4.6 Officer verification checklist (generated)

One line per verifiable element, with blank result fields:
- each evidence item: "Inspect original of E-2 (receipt), supplied 10:14, SHA-256 …; not examined";
- each witness with contact: "Contact W-1";
- location: "Confirm the incident location lies within the stated jurisdiction (status: near boundary, 40 m)";
- each open contradiction: "Clarify C-1";
- each loss: "Verify ownership and value of items listed".

---

## 5. Jurisdiction and submission: current state and limitations

### 5.1 What actually works today

| Function | Status |
|---|---|
| Station list and map polygons (91) | **Functional as display data.** Source and currency not verified. Station coordinates are polygon centroids, not station addresses. |
| Backend station assignment | **Functional but unsound.** The nearest polygon centroid is not jurisdiction. Offline simulation, using 4,550 synthetic points sampled uniformly inside the 91 polygons with the same metric as the backend KD-tree: the nearest-centroid station differed from the polygon containing the point in **878 cases (19.3%)**. A point outside every polygon (latitude 18.95, longitude 72.70, at sea) still gets a station (Malabar Hill). This is a simulation of the algorithm, not a field accuracy measure. |
| Frontend point-in-polygon | Functional, but overwritten by the backend result whenever the backend is online |
| Location capture | Browser geolocation, map, or typed address geocoded through Nominatim (third party). The location source and accuracy are not recorded. |
| Station contact and submission | **Not functional.** No station contact data exists. The email address shown is constructed, not sourced. "FIR number", "registered", "verified" and "e-signed" are generated locally. **Nothing is delivered to any police system.** |

### 5.2 Proposed jurisdiction handling (stage 4)

1. **Server-side point-in-polygon** over the GeoJSON (standard-library ray casting; `shapely` optional). Return `inside_one`, `near_boundary` (distance to boundary below a threshold to be set, e.g. 100 m, or GPS accuracy larger than that distance), `outside_all` or `no_location`.
2. **Never assign a station** when the status is `outside_all` or `no_location`. Show "jurisdiction undetermined – police to confirm".
3. Record `location_source` and `accuracy_m`. A typed address that was not geocoded is `typed_only`, and no polygon is assigned.
4. **Boundary data provenance:** obtain the official Mumbai Police jurisdiction boundaries and their date (SAO or PO), record the dataset hash, and show "boundary data unverified" until then.
5. Frontend: stop overwriting the polygon result. Remove the centroid fallback.
6. Geocoding: make Nominatim opt-in, with a privacy notice; comply with its usage policy (rate limits, identification, attribution); or replace it after a PO decision.

### 5.3 Submission

- **No authorised integration exists.** Bandhoo must not claim filing, registration, delivery, an FIR number, verification of identity, or a digital signature.
- **States** (§3.2):
  - `exported_by_complainant` (the complainant printed or downloaded the report);
  - `presented_to_police` (recorded **by a police user** in stage 5);
  - `electronically_submitted` only through a future integration that is formally authorised, has a documented interface, and returns a verifiable acknowledgement. **No such integration is identified or assumed here.**
- **Station contact details:** shown only from an authoritative source, with its date. Until then: "Contact details not available in Bandhoo".

---

## 6. Verification trail and privacy

### 6.1 Trail

- **Append-only `TrailEvent` log per case**, hash-chained (`prev_hash`, `hash` = SHA-256 of the event plus the previous hash). Server-side UTC timestamps. Actor type and reference.
- **Recorded events:** case created (original statement hash); extraction run (method, model, versions); item created or relabelled (with reason); question asked; statement added; contradiction opened or clarified; evidence supplied (hash); report generated (version, hash); jurisdiction resolved (dataset hash); verification event (officer, method, result); status change.
- **The original statement is never edited.** Corrections are new statements. Items cite statements by ID and span. The report shows the change record.
- The trail export includes a chain check. A broken chain is reported, not repaired.

### 6.2 Privacy and data protection (decisions required; legal compliance not assessed here)

- **Data minimisation:**
  - remove the **mandatory identity-document upload**; identity is verified by police in person;
  - during internal testing, use **synthetic data only**, with no real complainant data and no real identity documents;
  - store evidence files only if the PO approves storage, encryption at rest and retention. Otherwise store metadata and hashes only.
- **Third parties:** complainant narratives go to Google Gemini (when enabled), and locations and addresses to Nominatim. Both need a PO decision, a privacy notice and consent before any real use. Gemini can stay off for structuring (the deterministic path exists).
- **Access control:**
  - authentication and roles (complainant / police officer / administrator) are needed before stage 5;
  - CORS `*` must be restricted;
  - complainants see only their own cases.
- **Logging:** no narrative or personal data in server logs. Trail payloads are stored in the database, not printed.
- **Law:** obligations under India's Digital Personal Data Protection Act, 2023 and any police data-handling rules are **not assessed** here. That needs qualified review before any real data is processed.

---

## 7. Test plan and measurable police-review criteria

### 7.1 Automated tests (offline; Gemini mocked; no new live calls)

| Area | Tests |
|---|---|
| Grounding | Every statement item's `quote` equals `statement.text[start:end]`. An LLM item with a non-matching quote is rejected or relabelled as an inference (mocked Gemini returns fabricated detail). |
| Categories | The display-category rules of §4.1. No path to "independently verified" without a police event. An upload never changes authenticity. AI items keep their label. |
| Polarity | Denied, not provided, unknown and hedged cases in English, Hindi and Hinglish, reusing and extending the negation tests |
| Missing information | Checklist fields per incident type. Question cap. No leading questions (pattern list). |
| Contradictions | Planted conflicts (date, time, amount, place, identity, count, description). No dishonesty vocabulary in any generated text (deny-list test). Clarification preserves both originals. |
| Trail | Append-only; the hash chain validates; tampering is detected; the original statement is immutable. |
| Jurisdiction | Point-in-polygon for synthetic points inside each polygon (expect 100% match with the containing polygon); near-boundary and outside-all statuses; no station returned for `outside_all`. |
| Submission claims | The frontend and report contain no "FIR No.", "registered", "verified" (for uploads), "E-Signed", or constructed email patterns (static string tests) |
| Regression | The existing 228 tests are unchanged and pass. `/api/classify-offence` output is byte-identical for the benchmark fallback run (gate 7 style comparison). |

### 7.2 Structuring benchmark (new, synthetic)

- **About 40 synthetic cases**, written by someone other than the developer (EL to arrange). They contain planted elements: 5–8 material facts each, 1–3 missing core fields, 0–2 contradictions, 0–2 explicit denials, and evidence references. Cases cover English, Hindi/Hinglish and Marathi.
- **Gold annotations:** two annotators; disagreements adjudicated.
- **Metrics** (thresholds fixed before running):

| Metric | Proposed threshold |
|---|---|
| Item extraction precision and recall per kind | Precision ≥ 0.90; recall ≥ 0.80 for core fields |
| Grounding rate (statement items with a valid span) | **= 100%** |
| Fabricated-fact rate (items unsupported by any span) | **= 0** |
| Missing-core-field recall | ≥ 0.90 |
| Contradiction recall / precision | ≥ 0.80 / ≥ 0.80 |
| Denial-versus-missing confusion | ≤ 5% |
| False "verified" or false "authentic" labels | **= 0** |
| AI inference shown as fact | **= 0** |

  Results are reported per mode: deterministic, live LLM (only with an approved live evaluation), and cached.

### 7.3 Police usability evaluation (controlled; stage 6)

- **Participants:**
  - serving police officers recruited through an authorised channel with institutional permission and informed consent; or, if that isn't possible, trained proxy reviewers, **reported separately and not described as police**;
  - target of at least 12 participants. The EL sets the final number with a pre-registered power rationale.
- **Material:** synthetic cases only (from §7.2), each in two forms: (A) the raw narrative plus evidence list; (B) the Bandhoo report.
- **Design:**
  - within-subjects and counterbalanced (each participant sees different cases in each condition; order randomised);
  - tasks are timed;
  - all metrics are fixed in a pre-registration document before any session.
- **Tasks and measures:**

  | Measure | Definition |
  |---|---|
  | Fact location | Time to answer 10 factual questions per case, and accuracy |
  | Missing evidence identified | Recall of the planted missing items |
  | Contradictions noticed | Recall of planted contradictions; false alarms |
  | Verified versus claimed | Proportion of items the participant correctly classifies as verified or unverified. **Key safety measure:** the rate at which an unverified claim is treated as verified. |
  | Workload and usability | NASA-TLX (raw) and SUS questionnaires |
  | Errors and comments | Free-text, coded by two coders |

- **Success criteria** (proposed, to be pre-registered):
  - (B) no worse than (A) on accuracy (non-inferiority margin set in advance);
  - (B) faster on fact location;
  - (B) not higher on the rate of treating unverified claims as verified.
  - **No usability or accuracy improvement is claimed until these results exist.**

---

## 8. LangGraph assessment (grounded in the codebase)

**Facts:**
- LangGraph is **not used** by Bandhoo. No project file imports or mentions `langgraph`, `langchain` or `StateGraph`.
- It is not in `requirements.txt`.
- It is not installed in the Python 3.14 environment the test suite uses.
- A `langgraph` 1.2.9 package exists globally in Homebrew Python 3.11 (`/opt/homebrew/lib/python3.11/site-packages`), as a dependency of a globally installed `langchain`. That is unrelated to the project.

| Criterion | Current or proposed service functions | LangGraph |
|---|---|---|
| Control flow | The pipeline in §2 is a linear sequence with one branch (questions needed or not). Human steps (clarification, police verification) happen in **separate HTTP requests**, often hours apart. | Graph edges and conditional routing; interrupts for human input. Its benefit is greatest for long-running agent loops. |
| State management | Case state must be **durable domain data** (statements, items, trail) anyway, for audit and police access | Checkpointer stores graph state. That would duplicate the domain store and the audit trail, and could diverge from them. |
| Traceability | Domain trail events (§6) give a legally meaningful record | Generic execution traces. Still needs the domain trail. |
| Retry handling | One optional LLM call per extraction. The existing deterministic fallback already handles failure (`inference_status`). | Built-in retry policies. A small gain for a single call. |
| Testing and determinism | Plain functions are directly unit-testable, matching the existing 228-test style | Adds a framework layer to mock and test |
| Dependencies and risk | None new (stdlib `sqlite3`) | New dependency tree (`langgraph`, `langchain-core`). Compatibility with the project's Python 3.14 is not verified. |

**Recommendation: do not adopt LangGraph now.** Implement the pipeline as explicit step functions over a typed `CaseState` (Pydantic), with each step writing trail events. This gives clear control flow, durable state and traceability with no new dependency.

**Reconsider LangGraph if, and only if,** a later stage needs at least one of these, documented with a concrete case:
- several LLM calls per request with conditional branching or tool use;
- resumable long-running executions that can't be modelled as status fields plus new requests;
- parallel sub-steps with join and retry semantics that become hard to maintain by hand.

Multi-agent architecture is **not** recommended. Nothing in the workflow needs autonomous agents.

---

## 9. Dependencies, risks and staged implementation order

### 9.1 Dependencies and decisions (PO unless stated)

| # | Item | Needed by |
|---|---|---|
| D1 | Approval of this plan and of frontend changes (an earlier task excluded frontend changes) | Stage 0 |
| D2 | Persistence choice (SQLite or JSON-lines), location, encryption, retention | Stage 2 |
| D3 | Gemini use for structuring (on or off), privacy notice, consent | Stage 1 (LLM extractor) |
| D4 | Nominatim use or replacement | Stage 4 |
| D5 | Authentication and roles design | Stage 5 |
| D6 | Official jurisdiction boundary source and station contact data (SAO or PO) | Stage 4 |
| D7 | EL appointment, and the structuring benchmark authors and annotators | Stage 6 (and benchmark in stage 1) |
| D8 | Police participation through an authorised channel, with consent and ethics process | Stage 6 |
| D9 | Data-protection review (QLR or appropriate adviser) before any real data | Before any non-synthetic use |

Reviewer appointments are outstanding (`reports/reviewer_assignment_template.md`: all six roles pending). This plan **does not** assign anyone.

### 9.2 Risks

| Risk | Mitigation |
|---|---|
| LLM invents details while "structuring" | Span grounding check; fabricated-fact rate = 0 gate; deterministic mode available |
| Reviewers read machine output as verified fact | Display-category invariants; banner; usability measure of claims treated as verified |
| Contradiction flags read as accusations | Neutral templates; deny-list test; complainant clarification first |
| Wrong station assigned | Polygon method; boundary and outside statuses; "police to confirm"; dataset provenance |
| False filing claims | Removal of fabricated FIR number, email, "verified" and e-sign; submission states recorded only by police or a real integration |
| Personal data exposure | Synthetic-only testing; minimisation; access control; restricted CORS; no log payloads |
| Legal block outdated or under review | Kept separate; `recommended_action` excluded; legal gates unchanged |
| Scope creep and complexity | Stateless stage 1 first; no LangGraph; additive API |

### 9.3 Stages and acceptance criteria

| Stage | Scope | Acceptance criteria |
|---|---|---|
| **0. Approvals and immediate de-risking** (no new features) | PO decisions D1–D3. Approved frontend corrections only: remove the random FIR number, the "Register/Lodge FIR" wording, "verified" upload labels, the mandatory ID upload, the constructed email address, the hard-coded officer/status/remarks, and the frontend legal fallback. Change wording to "Prepare complaint". | Static tests: none of the listed strings or patterns remain. The existing 228 tests pass. A change record under `post_review_change_protocol.md`; frontend user-facing changes need PO approval. |
| **1. Stateless structuring** | `complaint_engine` models; deterministic extractors; optional LLM extractor with span grounding; polarity; missing-information checklist; within-text contradictions; `POST /api/v1/structure` | §7.1 grounding, category, polarity, missing and contradiction tests pass. Structuring benchmark (deterministic mode): grounding 100%, fabricated facts 0, false verified 0, other thresholds reported against §7.2. `/api/classify-offence` byte-identical on the fallback benchmark. |
| **2. Cases, clarifications, trail** | Persistence (D2); cases; statements; questions loop; cross-statement contradictions; trail with hash chain | Immutability and hash-chain tests pass; clarifications preserve originals; trail export validates; question cap enforced |
| **3. Evidence and report** | Evidence metadata and hash; links; report JSON and printable form; officer checklist; legal block (classifier output, `recommended_action` excluded) | Report section order and content rules tested; upload never sets authenticity; banner present; legal block labelled; snapshot tests of report rendering on synthetic cases |
| **4. Jurisdiction and submission status** | Server point-in-polygon with statuses; location source and accuracy; frontend stops overwriting; Nominatim decision (D4); boundary provenance (D6); submission state model without integration | 100% containing-polygon match on synthetic points; outside and boundary statuses tested; no station for `outside_all`; no submission claim reachable without a police-recorded state |
| **5. Police verification** | Authentication and roles (D5); `VerificationEvent`; police-recorded `presented_to_police`; trail includes police actions | Only authenticated police can create verification events (tests); verified category reachable only through them; restricted CORS; access-control tests |
| **6. Evaluation** | Structuring benchmark at full size; police usability study (D7, D8) | Pre-registration completed before sessions; results reported against pre-set criteria, including failures. **No improvement claimed without results.** |

Each stage is a separate change set with its own tests, a fresh snapshot before implementation, and rollback by file restore.

**Not in this plan:**
- any change to legal logic or prompts (Changes A, B/RB-53 and C stay separately gated);
- any treatment of the Maharashtra bills as law;
- any police integration or contact data not supplied by an authoritative source.

---

## 10. What must be approved before implementation

1. **PO:** approve this plan; decisions D1–D3 for stages 0–1, then D2, D4, D5 and D6 before the later stages.
2. **PO:** approve the stage 0 frontend corrections. They remove misleading claims and change no legal logic.
3. **PO, with an appropriate adviser:** privacy and data-protection position (D9) before any non-synthetic data.
4. **PO:** appoint the EL (and, for the legal block, the reviewers already required by the legal review documents).
5. **MNT and PO:** implementation approval per stage under `reports/post_review_change_protocol.md`, with a fresh snapshot before each stage.
