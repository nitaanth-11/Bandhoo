# BNS Corpus Integrity Audit and Migration (2026-10-20)

**Scope:** `bns_rag_dataset.json`, the corpus the backend loads. `public/bns_rag_dataset.json` is a frontend asset the app never fetches; it was deliberately left unchanged and now differs from the backend corpus.

**Status:** migration applied and verified. This is an automated and manual comparison with the Gazette text. **It is not a qualified legal review.**

## 1. Sources and their limits

| Purpose | Document |
|---|---|
| Statutory text | *The Bharatiya Nyaya Sanhita, 2023* (No. 45 of 2023), Gazette of India Extraordinary, Part II, Section 1, 25 December 2023 |
| Procedural classification | *The Bharatiya Nagarik Suraksha Sanhita, 2023* (No. 46 of 2023), First Schedule, Part I, same Gazette date |

- **Single source.** Both are the PDF copies hosted by PRS Legislative Research, converted to text with `pypdf`. The India Code copy could not be downloaded, so there was no second-source cross-check.
- **Amendments after 25 December 2023 were not checked.**
- **Extraction noise.** The extracted text contains margin headings, page headers and kerning splits (e.g. "V oluntarily"). The migration repairs kerning splits only where the joined word exists in the corpus vocabulary, and accepts skipped Gazette words only when they form section titles (margin headings) or one explicitly reviewed heading (Section 119; see Section 6).

## 2. Re-verification of the earlier audit claims

| Earlier claim | Finding after reading the records and the Gazette |
|---|---|
| Section 309 punishment field contains illustration text | **Confirmed.** It held the end of Illustration (d). Cause: `scrape_bns.py` `extract_punishment` takes the first sentence containing "punishable" plus a penalty word. |
| Twelve other punishment fields contain non-punishment text | **Imprecise.** Only Sections 2, 4 and 32 hold no punishment at all (a definition, the general list of punishments, a general exception). Sections 13, 56, 58, 71, 148, 199, 251, 252 and 341 hold the real punishment clause, preceded by part of the offence description. Within those, 56 omitted the public-servant limb and 341 covered only sub-section (1) of three. Separately, Sections 311 and 312 held a garbled fragment. |
| Sections 111 and 120 truncated | **Confirmed.** Section 111 held only an Explanation ("proceeds of any organised crime") that does not appear in the Gazette text. Section 120 began at its Illustrations. |
| Missing punishments in Sections 54, 111, 120, 264 | **Section 54 was wrong.** It is a deeming provision ("shall be deemed to have committed such act or offence"); an empty punishment field is correct. The genuine gaps were 111, 120 and 264. |
| 201 records embed "BNSS Classification" blocks | **Confirmed.** 187 of them fell within the 1,200 characters sent to Gemini as "Official Text". |
| Embedded classifications conflict for Sections 87, 90, 276 | **Confirmed** by reading the Gazette Schedule I rows (87 and 90 are cognizable; 276 is non-bailable). |
| Sections 354, 355, 357 need manual review | **Consistent with the Gazette**, read by row position in the column-split extraction. Lower confidence; recorded as `consistent_manual_positional_reading`. |
| Blanket `verified: true` | **Confirmed.** Replaced with per-record evidence (Section 4). |
| "58 differing records" (counter-based comparison) | Superseded by the stricter ordered comparison (Section 4), which flags 107 records. **Neither figure means 58 or 107 errors.** Many differences are formatting or tokenisation (e.g. "subsection" vs "sub-section", "moveable" vs "movable", a corpus-only preamble in Section 1). Each record needs individual review before it is treated as erroneous. |

## 3. Corrections applied

Every replacement was transcribed by hand from the Gazette text and then checked automatically. Its words must occur in the Gazette section in the same order, with no substituted, added or reordered words; skipped Gazette words may only be margin headings, and these are listed in the log. Full previous and new values, sources and skipped margin headings are in `reports/corpus_corrections_log_2026-10-20.json`.

| Section | Field | Correction |
|---|---|---|
| 309 | punishment | Illustration text replaced with Sections 309(4), 309(5) and 309(6) punishment clauses (sub-sections in `punishment_provisions`). |
| 311, 312 | punishment | Garbled fragment replaced with "the imprisonment with which such offender shall be punished shall not be less than seven years." |
| 264 | punishment | Empty field filled with clauses (a) intentional and (b) negligent. |
| 111 | text, punishment | Full text of sub-sections (1)–(7) with the Explanation and proviso restored; punishments for 111(2)–(7). |
| 120 | text, punishment | Sub-sections (1) and (2) restored around the existing Illustrations; punishments for 120(1) and 120(2). |
| 13, 56, 58, 71, 148, 199, 251, 252 | punishment | Leading offence-description fragment removed; verbatim punishment clause kept (56 now includes the public-servant limb). |
| 341 | punishment | Punishments for 341(1), (2) and (3). The old field cited section 336 where the Act cites 338. |
| 2, 4, 32 | punishment | Cleared; `punishment_status: no_punishment_clause` (manual review). |
| 54 | — | No change; recorded as `no_punishment_clause` (manual review). |
| 201 records | text | Scraped "BNSS Classification" block moved verbatim into `scraped_procedural_classification`. |

**Not changed:**
- Titles, chapters, keywords, and statutory text other than Sections 111 and 120.
- `public/bns_rag_dataset.json`, benchmark labels, retrieval thresholds, frontend files.

## 4. Per-record verification status

All `text_status` values come from an **ordered word comparison** with the Gazette section after removing punctuation and sub-section markers. It is not a similarity score.

| `text_status` | Records | Meaning | `verified` |
|---|---|---|---|
| `consistent_with_gazette` | 193 | Same words in the same order; skipped Gazette words are margin headings only; ≥ 90% of Gazette words present. | true |
| `restored_from_gazette` | 2 (111, 120) | Restored by checked transcription. | true |
| `differs_from_gazette_needs_review` | 107 | At least one word altered, added or reordered, or a cross-referenced number not in the Gazette section. **Needs individual review; not assumed erroneous.** | false |
| `possibly_incomplete` | 56 | No altered words, but Gazette words are absent. These may be truncation or unparsed margin headings (e.g. Section 97 was checked manually and its operative text matches). | false |

- **Cross-referenced numbers differ in 27 records:** 2, 29, 30, 71, 89, 99, 113, 115, 122, 136, 148, 155, 159, 167, 186, 199, 200, 211, 212, 237, 240, 249, 264, 265, 339, 341, 342.
  - Several match a numbering offset of two (e.g. Section 89 cites 86 where the Act cites 88; Section 115 cites 120 where the Act cites 122). This is consistent with a pre-enactment source text.
  - This is the strongest substantive signal and the first priority for review.
- **Registry offences:** of the 14 offences in `schedule_registry.py`, Sections 305, 306, 309, 310, 314 and 352 are consistent. Sections 115, 117, 303, 304, 316, 318, 324 and 351 differ and need review. Procedural classification for these comes from the registry, not the corpus text, so it is unaffected.
- **Punishment status:**

  | `punishment_status` | Records |
  |---|---|
  | `consistent_with_gazette` (contiguous match) | 263 |
  | `verified_against_gazette` (corrected) | 15 |
  | `no_punishment_clause` (4 manual, 63 automated pattern check) | 67 |
  | `unverified` | 13 |

  The 13 unverified fields are Sections 70, 113, 118, 124, 125, 206, 211, 221, 222, 260, 263, 316 and 323. Some contain only minor wording or extraction differences; they were not corrected without review.

## 5. Corpus record schema

The existing keys keep their meaning, so all current consumers work unchanged. New keys are additive.

| Key | Type | Meaning |
|---|---|---|
| `section` | int | BNS section number. |
| `title`, `chapter`, `keywords` | str, str, list | Unchanged (keywords feed BM25 and the fallback keyword check). |
| `text` | str | **Statutory text only.** Never contains scraped procedural metadata. Sub-section markers ("(1)", "(a)") are kept inline. |
| `punishment` | str | Punishment wording. Empty when the section has no punishment clause. Multi-limb corrections use `Section N(k): …` labels (added metadata, not statute). |
| `punishment_status` | enum | `verified_against_gazette`, `consistent_with_gazette`, `no_punishment_clause`, `unknown`, `unverified`. |
| `punishment_provisions` | list, optional | `[{sub_section, text}]` for corrected multi-sub-section punishments (309, 111, 120, 341). |
| `scraped_procedural_classification` | object or null | `{text, status: "unverified_secondary_source", gazette_check, gazette_check_note, source_note}`. Scraped, non-statutory, never shown to Gemini. `gazette_check` is one of `not_checked_against_gazette`, `conflicts_with_gazette_schedule_i`, `consistent_manual_positional_reading`. |
| `verified` | bool | Kept for compatibility. True only when `verification.text_status` is `consistent_with_gazette` or `restored_from_gazette`. Not a legal verification. |
| `verification` | object | `text_status`, `punishment_status`, `method` (`automated_ordered_comparison` or `manual_transcription_automated_check`), `punishment_method` (`manual_review` or `automated_pattern_check`), `source_document`, `checked_on`, `evidence` (`corpus_only_token_count`, `corpus_only_tokens_sample`, `corpus_only_numbers`, `cross_reference_numbers_differ`, `gazette_token_coverage`, `ordered_comparison_problems_sample`), `note`, `legal_review: "not performed"`. |
| `source` | str | Unchanged, except Sections 111 and 120, which now cite the Gazette. |
| `schedule_i_status` | str | Legacy; the loader still overrides it from `schedule_registry.py`. |

**Authoritative procedural metadata** (cognizable, bailable, triable by) lives only in `legal_engine/schedule_registry.py`. The corpus never supplies it to the service.

### Downstream consumers

- **`BNSCorpus` loader:**
  - Splits any legacy embedded block out of `text` at load time, so old-format files are safe.
  - Exposes `text_status`, `punishment_status`, `punishment_provisions`, `verification` and `scraped_procedural_classification`.
- **Gemini context (`format_for_llm_context`):**
  - "Statutory Text" (no scraped block).
  - A "Text Verification" line; unverified records are labelled "NOT verified".
  - Punishment, or "No punishment clause in this section…" / "Not available in the corpus. Do not infer a punishment." The old default "As prescribed by court / definition section" is removed.
- **BM25 (`get_document_text`):** still indexes title + keywords + text + the legacy scraped wording, so separating the block did not change retrieval. Whether to drop that wording from the index is a separate retrieval decision.
- **Service and API:** `predictions[].punishment` now carries the corrected values. Response schemas are unchanged.

## 6. Unresolved items

1. **The 107 `differs_from_gazette_needs_review` and 56 `possibly_incomplete` records** need individual review. The 27 with differing cross-references come first.
2. **Section 119 title** reads "…to constrain to an illegal to an act"; the Gazette margin heading reads "…to constrain to an illegal act." The title was not changed, because it was outside the reviewed correction set.
3. **Section 303 Explanation 2:** the corpus reads "effects the severance"; the Gazette text reads "affects the severance". This was flagged, not changed.
4. **Scraped classifications for Sections 87, 90 and 276 conflict with Schedule I.** They are retained only as unverified scraped data, never used for procedural output.
5. **The 13 unverified punishment fields** (Section 4).
6. **`scrape_bns.py` would reintroduce the defects** if re-run. It was not modified.
7. **`public/bns_rag_dataset.json`** is now stale relative to the backend corpus (unused by the app).

## 7. Backups, logs and reproducibility

- **Pre-migration corpus:** `reports/backups/bns_rag_dataset.pre_integrity_migration_2026-10-20.json` (SHA-256 `d053ce3d…3783807`, identical to `public/bns_rag_dataset.json`).
- **Migration script:** `reports/apply_corpus_corrections.py`. It refuses to run twice, and validation failures abort before writing. The applied result was byte-identical to the reviewed dry run.
- **Corrections log:** `reports/corpus_corrections_log_2026-10-20.json` (221 entries).
- **Tests:** `tests/test_corpus_integrity.py`.

## 8. Benchmark impact (offline fallback, identical metric definitions)

| | Before | After |
|---|---|---|
| Prediction precision (all 50) | 18.78% (43/229) | 18.70% (43/230) |
| Prediction recall | 56.25% (36/64) | 56.25% (36/64) |
| Production candidate recall | 65.62% (42/64) | 65.62% (42/64) |
| Recall@10 (diagnostic) | 71.88% (46/64) | 71.88% (46/64) |
| Procedural correctness (top prediction) | 12/32 | 11/32 |
| Excluding 8 provisional: precision / recall / procedural | 17.22% / 58.14% / 10 of 24 | 17.13% / 58.14% / 10 of 24 |

All scores shifted slightly because restoring Sections 111 (about 60 → 700 words) and 120 changed BM25 corpus statistics: average document length, and how rare common terms such as "property", "hurt", "robbery" and "extortion" are. No threshold or ranking logic changed.

Prediction changes:
- **Order only:** BM-03, 07, 26, 29, 46.
- **Extra false positive:** BM-02 gains Section 43.
- **Swap between unlabelled sections:** BM-45 swaps Section 35 for 315.
- **BM-31 (provisional):** the top prediction moves from Section 316 to 314, and 317 is replaced by 305. This is the one procedural-match loss; BM-31's Section 316 label is itself disputed.
- **Restored Section 111:** now appears in raw retrieval for BM-34 and BM-44, but not in their final predictions.

## 9. Requires qualified legal review

- The transcribed punishments for Sections 309, 311, 312, 264, 111, 120, 13, 56, 58, 71, 148, 199, 251, 252 and 341, against the official text and any later amendments.
- The 27 records with cross-reference differences, and the other differing or possibly incomplete records.
- Gazette Schedule I classifications for Sections 87, 90 and 276, and the positional reading for Sections 354, 355 and 357.
- Continuing open questions from earlier rounds: the Section 303(2) proviso at FIR registration, the Section 173(3) range reading, Section 173(3) and *Lalita Kumari*, and the Section 324 value bands.
