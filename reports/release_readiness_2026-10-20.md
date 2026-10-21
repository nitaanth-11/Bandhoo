# Bandhoo Release-Readiness Check (2026-10-20)

**Verdict:** suitable for continued **internal testing**. **Not ready for public release** as a source of legal information until the priority items in Section 7 have qualified legal review.

All checks below were run in this session. No live Gemini calls were made and `.env` was not read.

## 1. Backup and corpus integrity

| Check | Result |
|---|---|
| Current `bns_rag_dataset.json` vs reviewed dry-run output | Byte-identical (SHA-256 `7c7e3322…127e5b`). |
| Pre-migration backup `reports/backups/bns_rag_dataset.pre_integrity_migration_2026-10-20.json` | Readable, 358 records, no migration fields. SHA-256 `d053ce3d…3783807`, identical to the scratch backup and to `public/bns_rag_dataset.json`. Now **read-only**. |
| Fields changed vs backup | Statute text: Sections 111 and 120 only, plus 201 scraped blocks moved verbatim to `scraped_procedural_classification`. Punishment: the 18 reviewed sections only. Source: 111 and 120. Title, chapter and keywords: none. Keys added: 4. Keys removed: none. 163 records changed `verified` from true to false. |

**Safeguards added** (Section 3 lists the defects they address):

| File | Change |
|---|---|
| `legal_engine/corpus_guard.py` | Refuses scraper writes to the live corpus files or to any migrated corpus. Provides a verified-backup helper. |
| `scrape_bns.py` | Writes only to `scraper_staging/` (git-ignored). Every write is guarded, and the guard runs before any network work. It no longer writes `public/`. |
| `reports/apply_corpus_corrections.py` | Already refused to run on migrated data and exited on validation failure before writing. It now also takes a verified, timestamped backup and replaces the dataset atomically. |
| `reports/CORPUS_UPDATE_WORKFLOW.md` | Documents the update procedure and the known scraper defects. |
| `tests/test_corpus_guard.py` (12 tests) | Covers the guard, the backup checksum and read-only state, guarded scraper writes (static AST check, because importing the scraper triggers an NLTK download), the refusal on migrated data, and the no-write-on-failure path. |

The scraper was **not run**.

## 2. Downstream compatibility

| Component | Finding |
|---|---|
| Corpus loader | Loads the new fields. Legacy-format files (embedded block, no verification) still load, with the block split out at load time. |
| BM25 indexing | Every document still contains its statutory text plus the legacy scraped wording (index parity). Running the pre-migration corpus through the current code reproduces the saved pre-migration benchmark exactly, so the loader change alone altered nothing. |
| Gemini context | For all 358 records, the context has no "BNSS Classification" block and no "As prescribed…" text. Every record with `verified=false` carries a "NOT verified" line; verified ones do not. Empty punishments read either "No punishment clause in this section…" or "Not available in the corpus. Do not infer a punishment." |
| Response schemas | Unchanged. `predictions[].punishment` returns corrected text or an empty string, never invented text. |
| Fallback | Unaffected by the new fields; punishment fields are not indexed or scored. |
| Assumptions about `verified=true` or the old block wording | None in runtime code. The only references to "BNSS Classification" are the deliberate splitting patterns. |

## 3. Scraper and update-workflow risks

| Risk | Status |
|---|---|
| Scraper overwrote the live corpus and `public/` with no backup, restoring all defects | **Fixed** (staging-only output, guarded writes, tests). |
| Scraper defects remain in its logic (punishment extraction, embedded metadata, no verification, pre-enactment cross-references) | Documented; staged output must go through the workflow. |
| `bns_finetune_dataset.json` and `bns_scenarios_dataset.json` still contain the old defective punishments (including Section 309) and invented "As prescribed…" text | Not used by any code. Reported only; do not use for training. |
| `public/bns_rag_dataset.json` is now stale | Unused by the app; left unchanged by design. |
| Scraper needs `nltk`, which is not installed or listed as a requirement | Already noted as optional in `requirements.txt`. |

## 4. Benchmark regression analysis (BM-02, BM-31)

**Method:** an ablation run with the current code.
- Reverting only the Section 111 and 120 text reproduces the pre-migration scores exactly for all 50 cases.
- Reverting only the punishment fields changes nothing.

The sole cause is therefore the restored statutory text, acting through BM25 corpus statistics: average document length rose from 188.55 to 190.66, and term rarity weights fell (e.g. "extortion" 4.62→4.37, "robbery" 3.17→3.10). No threshold or ranking code changed.

**BM-02** (verified label; bicycle theft):
- The service considers at most 8 candidates.
- Section 43 (start of the right of private defence of property) rose from about 0.74 to 0.76 relative to the top score and displaced Section 338 as the 8th candidate. Section 338 had been filtered out by the fallback keyword check; Section 43 passes it.
- Result: one extra false positive. Section 43 is legally irrelevant here, so this change is **not** more defensible, but it is a boundary effect of correct data, not a code defect.
- The relevant Section 303 is still found. The top prediction (Section 35) was wrong before and after, so procedural correctness is unaffected.

**BM-31** (provisional label; tenant disposes of owner's furniture):
- Before the migration, Sections 316 and 314 were near-tied (316 at 1.000, 314 at 0.986). The restored Section 111 legitimately contains "criminal breach of trust", which lowered the rarity weight of "breach" (3.99→3.85) and "trust" (4.37→4.16). The order flipped (314 at 1.000, 316 at 0.998).
- **Procedural correctness fell from 12/32 to 11/32 because of BM-31 alone.** The metric compares only the top prediction. Section 314 is non-cognizable and bailable; the label expects the cognizable, non-bailable result implied by its disputed Section 316 label.
- Defensibility: the label review found Section 316 unsupported (no entrustment stated). Section 314 is a labelled plausible alternative. Neither is the best answer (Section 303, which is absent before and after).
- The user-facing procedural advice still names the cognizable route (Sections 316 and 305 via the multi-candidate review).
- The result was **not** forced back. Excluding the eight provisional cases, procedural correctness is unchanged at 10/24.

## 5. Tests

**Full suite: 228 passed, 1 warning** (upstream GenAI SDK deprecation). Gemini behaviour is covered by mocked tests only.

## 6. Fallback benchmark (offline; 0 live calls, 0 cached)

| Same definitions | Pre-migration baseline | Current |
|---|---|---|
| Prediction precision (all 50) | 18.78% (43/229) | 18.70% (43/230) |
| Prediction recall | 56.25% (36/64) | 56.25% (36/64) |
| Production candidate recall | 65.62% (42/64) | 65.62% (42/64) |
| Recall@10 (diagnostic) | 71.88% (46/64) | 71.88% (46/64) |
| Procedural correctness (top prediction) | 12/32 | 11/32 |
| Excluding 8 provisional: precision / recall / procedural | 17.22% / 58.14% / 10 of 24 | 17.13% / 58.14% / 10 of 24 |

- Cases with changed predictions: BM-02, 03, 07, 26, 29, 31, 45, 46. All except BM-02, BM-31 and BM-45 (35 swapped for 315, both unlabelled) are order-only changes.
- The current run is identical to the post-migration report.
- Counts reconcile: overall = excluding provisional + provisional; overall = development + holdout; true positives + false positives = predictions.
- The holdout remains "previously inspected".

## 7. Issues requiring qualified legal review (priority order)

1. **Statutory text of core offences.** Sections 115, 117, 303, 304, 316, 318, 324 and 351 differ from the Gazette. Of the 27 records whose cross-references differ, Section 115 cites "section 120" where the Act cites 122. These sections drive most predictions.
2. **The transcribed corrections:** punishments for Sections 309, 311, 312, 264, 13, 56, 58, 71, 148, 199, 251, 252 and 341, and the restored text of Sections 111 and 120.
3. **Procedural open questions:** the Section 303(2) proviso at FIR registration; the Section 173(3) maximum-term reading and *Lalita Kumari*; the Section 324(4)/(5) value bands.
4. **Schedule I classifications:**
   - Sections 87, 90 and 276: the scraped values conflict with the Gazette.
   - Sections 354, 355 and 357: read by row position only.
5. **Benchmark labels:** the 8 provisional cases (BM-17, 20, 21, 22, 28, 30, 31, 45), including BM-31's disputed Section 316 label.
6. **Remaining corpus records:**
   - 80 other "differs" records and 56 "possibly incomplete" records.
   - 13 unverified punishment fields.
   - The Section 119 title ("illegal to an act").
   - Section 303 "effects" vs "affects".
7. **Source limits.** Only one source copy was used (PRS-hosted Gazette PDFs of 25 Dec 2023), and later amendments were not checked.

## 8. Non-legal risks still open

- **Live Gemini path:** tested only with mocks. `benchmark/evaluation_report_live.json` is stale (5 cases).
- **Fallback precision:** about 18%. General sections (35, 97, 345, 43) dominate, and retrieval tuning was out of scope.
- **BM25 index:** still includes the scraped classification wording, for parity. Removing it is a separate retrieval decision that needs re-benchmarking.
- **Model name:** the default Gemini model name is unconfirmed.
