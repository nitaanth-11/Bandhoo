# Bandhoo Post-Review Change Protocol

**Applies to:** any change to legal content or procedural logic. That means:
- the statutory corpus (`bns_rag_dataset.json`);
- the Schedule I registry (`legal_engine/schedule_registry.py`);
- procedural advice templates, validation rules and amount parsing (`legal_engine/service.py`, `legal_engine/amounts.py`);
- the Gemini system prompt (`legal_engine/llm_client.py`);
- benchmark labels (`benchmark/build_dataset.py` and `benchmark/bns_synthetic_benchmark_50.json`).

**Does not apply to:** refactoring that leaves outputs unchanged. Even then, gates 6–7 must still pass.

**Status:** Bandhoo remains internal-testing-only. Following this protocol does not make Bandhoo legally validated.

## 1. Change types and approval paths

| Path | Use when | Approvals required |
|---|---|---|
| **A. Transcription correction** | Stored text differs from the official text and the correct wording is not in doubt: a cross-reference number, a spelling, a missing word, a truncated passage, a title. No interpretation is involved. | Maintainer, plus a second person who compares the passage against the source (a QLR is not required). If only one source copy exists, the change is recorded as "single-source" and stays open in the blocker register until a second copy confirms it. |
| **B. Substantive legal interpretation** | Anything that changes what Bandhoo concludes or advises: classification rules, Section 173(3) or 174 logic, the 303(2) proviso, valuation rules, offence-element validation, procedural template wording, prompt instructions, benchmark labels. | Two qualified Indian criminal-law reviewers (QLR) in agreement, or adjudicator (ADJ) decision on disagreement; plus maintainer; plus project owner (PO) for changes to user-facing advice. |
| **C. Classification metadata** | Adding or changing Schedule I rows in the registry. | Path A if transcribing a row whose reading is clear in the printed Schedule; path B if the row is ambiguous, conflicts with the BNS text (e.g. the s.324 bands) or needs interpretation to map to sub-sections. |

If there is any doubt about whether a change is A or B, treat it as **B**.

## 2. Gates

Each change record (Section 3) must show every gate as passed before the change is merged.

### Gate 1 — Identify the authoritative source

- Name the document: title, Act number, Gazette date, part and section, publisher or host, URL, and the date accessed.
- Preferred sources are the Gazette of India or India Code, including any amending Act or corrigendum.
- Not acceptable as authority: secondary websites, including the scraper source `devgan.in`; blogs; LLM output; `bns_finetune_dataset.json`; `bns_scenarios_dataset.json`; `public/bns_rag_dataset.json`; Bandhoo's own outputs.
- State whether amendments after the source date were checked. If they were not, say so.

### Gate 2 — Record the exact passage and provenance

- Quote the passage verbatim, marking sub-section and clause.
- Note any extraction artefacts (PDF word splits, margin headings) and how they were handled.
- For case law, give the full citation, the court, the date and the paragraph relied on. A citation must not be added unless the judgment text has been read. (The current *Lalita Kumari* citation fails this gate: blocker RB-02.)
- For corpus changes, record the transcription in a migration script modelled on `reports/apply_corpus_corrections.py`. Its `transcription_check` must pass: same words in the same order; skipped Gazette words only margin headings.

### Gate 3 — Qualified legal review (path B and C-ambiguous)

- Two QLRs review independently. They record:
  - the question;
  - their conclusion;
  - the authority relied on;
  - their confidence;
  - any remaining uncertainty.
- Disagreements go to the ADJ. If the matter is still unresolved, the change is **not** made: the issue stays open and Bandhoo keeps uncertainty-preserving behaviour (e.g. "unknown" classification, explicit caveat).
- Record decisions in `reports/legal_review_checklist.md` against the item ID.

### Gate 4 — Propose a minimal change

- **One issue per change.** Do not bundle unrelated corrections.
- Change only the affected record, row, template sentence or rule.
- Do not change retrieval thresholds, ranking logic, scoring weights or benchmark labels as a side effect.
- Prefer preserving uncertainty over asserting a conclusion the review did not reach.
- Corpus changes go through a migration script that refuses to run on already-changed data, takes a verified backup (`legal_engine.corpus_guard.backup_with_verification`), writes atomically, and logs previous and new values. Never edit `bns_rag_dataset.json` by hand. Never copy scraper output over it.

### Gate 5 — Regression test

Add a deterministic test that **fails before the change and passes after it**. Record both runs. Examples:
- a corpus test asserting the corrected passage;
- a registry test asserting the classification row;
- a service test asserting the advice wording or classification for a narrative that exercises the issue.

No test may call Gemini; use mocks for LLM paths.

### Gate 6 — Offline tests

Run with Gemini disabled (`GEMINI_API_KEY="" GOOGLE_API_KEY=""`). `.env` is not read by the operator.

1. Targeted tests for the affected area (e.g. `tests/test_corpus_integrity.py`, `tests/test_corpus_guard.py`, `tests/test_procedural_law_audit.py`).
2. Full suite: `python -m pytest -q`.

All tests must pass. Any test whose expectation changes must be justified in the change record, as a test that encoded the defect, and approved under the same path as the change.

### Gate 7 — Benchmark comparison without relabelling

1. Save the current `benchmark/evaluation_report_fallback.json`.
2. Run `python benchmark/evaluate_benchmark.py --mode fallback`.
3. Compare **case by case**: predicted sections, scores, procedural match. Report metrics before and after using identical definitions, with and without provisional cases.
4. Explain every changed prediction. Corpus text changes alter BM25 corpus statistics for every query; isolate their effect with an ablation (revert only the change and confirm the old results reproduce).
5. **Benchmark labels must not be changed to improve metrics.** Label changes are separate path B changes with their own records.
6. A metric drop is not by itself a reason to reject a legally correct change. A metric gain is not by itself a reason to accept one.

Live Gemini evaluation is not part of this gate. It requires separate approval and a quota budget, under `reports/independent_evaluation_plan.md`.

### Gate 8 — Review unintended effects

Check and record effects on:
- **Related provisions:** sub-sections, cross-referenced sections, provisions sharing keywords (e.g. 303/305/306; 316 sub-sections; 117/118/122).
- **Procedural advice:** single- and multi-offence templates, Section 173(3) statements, 174(4) routing, non-penal responses.
- **Gemini context:** the "Text Verification" and "Punishment" lines (`BNSCorpus.format_for_llm_context`).
- **Schedule metadata:** `is_cognizable` and `is_bailable` for affected sections.
- **Records:** the blocker register and checklist entries that the change touches.

### Gate 9 — Approval, uncertainty and rollback

Record in the change record:
- **Approvals:** name, role, date and path.
- **Remaining uncertainty:** e.g. single-source, amendment status unchecked, interpretation pending.
- **Rollback:**
  - For corpus changes: restore the verified backup created at gate 4 (its path and SHA-256 are recorded), then re-run gates 6–7.
  - For code changes: revert the commit.
  - The protected pre-migration backup (`reports/backups/bns_rag_dataset.pre_integrity_migration_2026-10-20.json`, SHA-256 `d053ce3de31ef17d985b03251e9178d38b3ed70144dc2abe7802c1f873783807`) is never modified or deleted.
- **Register updates:** update the blocker register status and the checklist decision field.

## 3. Change record template

Copy this block into the change description (pull request or a file under `reports/changes/`) for every change.

```
Change ID:
Blocker / checklist IDs:
Path: A (transcription) / B (interpretation) / C (classification)
Summary of change:

Gate 1  Source: title, Act no., Gazette date, section, host/URL, accessed on; amendments checked? (yes/no, how)
Gate 2  Exact passage (verbatim, sub-section marked):
        Extraction artefacts and handling:
        Case-law citation and paragraph (if any; judgment text read? yes/no):
Gate 3  QLR 1: conclusion, authority, confidence, date
        QLR 2: conclusion, authority, confidence, date
        Adjudicator (if needed):
        Unresolved points:
Gate 4  Files and records changed:
        Migration script / log path (corpus changes):
        Backup path and SHA-256:
Gate 5  Regression test name; failing-before output; passing-after output:
Gate 6  Targeted tests result; full-suite result (count, warnings):
Gate 7  Benchmark before/after (identical definitions, with and without provisional cases):
        Changed cases and explanation:
        Ablation result (if corpus text changed):
Gate 8  Related provisions checked:
        Procedural advice checked:
        Gemini context checked:
Gate 9  Approvals (name, role, date):
        Remaining uncertainty:
        Rollback instructions:
        Blocker register / checklist updated: yes/no
```

## 4. What this protocol forbids

- Changing statutory text, classifications or advice from memory, a secondary website or model output.
- Treating a difference from one Gazette copy as proof of an error without the path A second-copy step or QLR confirmation.
- Relabelling benchmark cases to improve metrics, or relabelling without a path B record.
- Tuning retrieval thresholds or ranking logic as part of a legal-content change.
- Running `scrape_bns.py` against the live corpus (the guard refuses it), or copying staged scraper output over the corpus.
- Reading `.env`, exposing secrets, or calling Gemini outside an approved live evaluation.
- Overwriting or deleting existing backups and reports. Superseded reports get a dated notice; they are not rewritten.
- Describing Bandhoo as legally validated or ready for public release.
