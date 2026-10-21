# Corpus Update Workflow

`bns_rag_dataset.json` is the statutory corpus the backend loads. It carries reviewed corrections and per-record verification evidence (`reports/corpus_integrity_audit.md`). It must never be replaced by raw scraper output.

## What the safeguards enforce

| Tool | Safeguard |
|---|---|
| `scrape_bns.py` | Writes only to `scraper_staging/` (git-ignored). `legal_engine.corpus_guard.assert_safe_scraper_output` refuses any write to `bns_rag_dataset.json`, `public/bns_rag_dataset.json`, or any file that is already a migrated corpus. It checks every output path before any network work and again before each write. It no longer writes a `public/` copy. |
| `reports/apply_corpus_corrections.py` | Refuses to run on an already-migrated dataset. Any validation failure exits before writing. Before writing, it takes a timestamped backup in `reports/backups/`, verifies it byte-for-byte, and replaces the dataset atomically (temporary file, then rename). |
| `reports/backups/bns_rag_dataset.pre_integrity_migration_2026-10-20.json` | Read-only file; SHA-256 `d053ce3de31ef17d985b03251e9178d38b3ed70144dc2abe7802c1f873783807`. |
| `tests/test_corpus_integrity.py`, `tests/test_corpus_guard.py` | Fail if the scraper defects return: wrong Section 309 punishment, truncated Sections 111/120, embedded classification blocks in `text`, blanket `verified: true`, or unguarded scraper writes. |

## Known scraper defects (do not reintroduce)

1. **Punishment extraction.** `extract_punishment` takes the first sentence containing "punishable" plus a penalty word, which can be illustration or definition text (Section 309, Sections 2, 4 and 32).
2. **Truncation.** Some sections were stored partially (Sections 111 and 120).
3. **Embedded metadata.** A scraped "BNSS Classification" block is appended to `text`. It is not statute, and it was wrong for Sections 87, 90 and 276.
4. **No verification.** Records were marked `verified: true` without evidence.
5. **Source text version.** Some cross-references differ from the enacted Act (27 records), which suggests a pre-enactment text.
6. **Derived datasets.** `generate_finetune_entries` and `generate_scenarios` invent "As prescribed…" punishment text when none was extracted. The existing `bns_finetune_dataset.json` and `bns_scenarios_dataset.json` still contain the old defective punishments (including Section 309) and are not used by the backend. Do not use them for training without regeneration from the reviewed corpus.

## How to change the corpus

1. Run the scraper (if needed) into `scraper_staging/` only. Treat its output as an unreviewed source.
2. Identify each proposed change by section and sub-section. Transcribe it from the authoritative Gazette text, never from scraped text or memory.
3. Add the change to a migration script modelled on `reports/apply_corpus_corrections.py`. The script must:
   - validate each replacement with the ordered Gazette comparison (`transcription_check`);
   - record previous value, new value, source, passage and method in a log;
   - take a verified backup before writing.
4. Dry-run the script on a copy, review the log, then apply. Confirm the applied file is byte-identical to the dry run.
5. Run `pytest`, the offline fallback benchmark (`python benchmark/evaluate_benchmark.py --mode fallback`), and compare predictions case by case with the previous report. Changing statutory text changes BM25 corpus statistics for every query.
6. Do not set `verified: true` by hand. It is derived from `verification.text_status`.
7. `public/bns_rag_dataset.json` is a frontend asset the app does not load. Update it only as a deliberate frontend decision.

## Source limitation

The current verification used the PRS-hosted copies of the 25 December 2023 Gazette texts of the BNS (Act 45 of 2023) and BNSS (Act 46 of 2023). Later amendments were not checked. Verification statuses are automated or manual text comparisons, not qualified legal review.
