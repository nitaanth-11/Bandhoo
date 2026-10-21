# BNS Corpus Data Quality Report

> **Superseded in part (2026-10-20).** See `reports/corpus_integrity_audit.md` for the re-verified findings and the migration that followed. Corrections to this report:
> - **Section 54 does not have a missing punishment.** It is a deeming provision with no punishment clause; the genuine gaps were Sections 111, 120 and 264.
> - **The "twelve non-punishment fields" claim was imprecise.** Only Sections 2, 4 and 32 contain no punishment; the other nine contain the real punishment clause preceded by part of the offence description.
> - **Low similarity scores and differing records must not be assumed erroneous** without individual review; many differences are formatting or extraction noise.
> - **Sources:** verification used the PRS-hosted copies of the 25 December 2023 Gazette texts; later amendments were not checked.
> - `corpus_data_quality_details.json` reflects the corpus **before** the migration.

**Scope:** `bns_rag_dataset.json` (358 records; byte-identical copy in `public/`).
**Date:** 2026-10-20. **Status:** findings only, written before the migration.

## Method and evidence

- **Statutory text:** Gazette of India (Extraordinary), *The Bharatiya Nyaya Sanhita, 2023* (No. 45 of 2023, 25 December 2023), PDF hosted by PRS Legislative Research, converted to text with `pypdf`.
- **Procedural classification:** Gazette text of the *Bharatiya Nagarik Suraksha Sanhita, 2023* (No. 46 of 2023), First Schedule, Part I.
- **Comparison:** every record was matched to its Gazette section and scored with a token-level `difflib` similarity, after stripping the corpus's embedded "BNSS Classification" block. The script is `reports/corpus_audit.py` and per-section results are in `reports/corpus_data_quality_details.json`.
- **Limits of the method:**
  - Similarity is a screening signal, not verification. Gazette margin notes and page furniture lower the score for short sections; a manual spot check of Section 97 (score 0.50) found the corpus text identical to the Gazette.
  - Schedule I rows that wrap across lines are not always parsed, so only mismatches confirmed by reading the Gazette rows are reported below.
  - Amendments after 25 December 2023 were not checked.
  - None of this is a qualified legal review.

## 1. Section 309 punishment field

| Field | Corpus value | Gazette text |
|---|---|---|
| `punishment` | "punishable as such: but it is not robbery, unless Z is put in fear of the instant death of his child." | Section 309(4): "Whoever commits robbery shall be punished with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine; and, if the robbery be committed on the highway between sunset and sunrise, the imprisonment may be extended to fourteen years." |

**Cause:** the field holds the end of Illustration (d). It appears to have been extracted from the first occurrence of "punishable" in the section rather than from the punishment clause.

**Impact:**
- The field is sent to Gemini as "Punishment" in the retrieval context.
- It is returned to API clients in `predictions[].punishment`.
- Procedural text about robbery comes from the Schedule I registry, not this field, so it is unaffected.

**Same extraction pattern elsewhere:**
- **Non-punishment text in the field:** Sections 2, 4, 13, 32, 56, 58, 71, 148, 199, 251, 252 and 341. Examples: Section 32 (a general exception) holds "punishable with death, nothing is an offence…"; Section 2 holds part of a definition.
- **Truncated punishment wording:** Sections 311 and 312 read "shall be punished shall not be less than seven years."
- **Paraphrased rather than quoted:** Section 118's punishment field, although the record's `source` cites the Gazette.

## 2. The 67 sections with empty punishment fields

| Group | Sections | Assessment |
|---|---|---|
| Gazette section contains a punishment clause | **54, 111, 120, 264** | **Genuine gaps.** Sections 111 and 120 are also truncated (see Section 3 of this report). |
| Gazette section contains no punishment clause | The other 63 (definitions, general exceptions, interpretation and abetment rules, etc.) | An empty field is expected. It should be represented explicitly (e.g. `"punishment": null` with a reason) rather than as an empty string. |

The full list is in `summary.empty_punishment` in the details file.

## 3. Statutory text fidelity and the blanket `verified: true`

All 358 records have `verified: true`. There is no per-record provenance (source document, date or checker), and `source` is a fixed string on 357 records.

Similarity of corpus text to the Gazette (embedded classification block removed):

| Similarity | Sections |
|---|---|
| ≥ 0.95 | 269 |
| 0.85–0.95 | 55 |
| 0.70–0.85 | 21 |
| < 0.70 | 13 |

Confirmed problems among the low scorers:
- **Section 111 (organised crime):** the corpus holds only the closing Explanation (60 words); the operative provision and punishment are missing (similarity 0.06).
- **Section 120:** the corpus starts at the Illustrations; the operative provision is missing.
- **Sections 112 and 113:** most Gazette wording is present (token coverage 0.75–0.78) but reordered or partly missing; manual comparison is needed.
- **Sections 97, 135, 153, 161, 180, 239, 281, 290 and 300:** short sections whose low scores are likely Gazette margin-note noise. Section 97 was checked manually and matches.

Other observations:
- 66 records were rewritten after the initial commit (an "IPC Section N" prefix was removed; none remain).
- Section 118 was inserted manually. Its text matches the Gazette (similarity 1.0).

**Conclusion:** `verified: true` is not backed by section-specific evidence and should not be read as legal verification. At least Sections 111 and 120 are incomplete.

## 4. Corpus records vs Schedule I metadata

### 4.1 Embedded "BNSS Classification" blocks inside the statutory text

- 201 records append a scraped "BNSS Classification" block (punishment summary, cognizable/bailable, court) to the `text` field. This is not part of the BNS.
- In 187 of them, the block falls within the first 1,200 characters that `BNSCorpus.format_for_llm_context` sends to Gemini under the heading **"Official Text"**.
- BM25 also indexes the block, so procedural words ("Cognizable", "Magistrate", "Non-bailable") affect retrieval.

Conflicts with the Gazette Schedule I, confirmed by reading the Gazette rows:

| Section | Corpus embedded block | Gazette Schedule I |
|---|---|---|
| 87 (kidnapping, abducting or inducing woman to compel marriage) | Non-cognizable, Non-bailable | **Cognizable**, Non-bailable |
| 90(1), 90(2) (death caused by act done with intent to cause miscarriage) | Non-cognizable, Non-bailable | **Cognizable**, Non-bailable |
| 276 (adulterating drugs) | Non-cognizable, **Bailable** | Non-cognizable, **Non-bailable** |

Automated flags for Sections 77, 78, 85, 91, 190, 319 and 337 were parser artefacts (multi-row or wrapped entries that agree on reading). Sections 354, 355 and 357 could not be checked because their Schedule rows are split across columns in the extracted text.

### 4.2 `schedule_i_status` field

- All 358 records store `"schedule_i_status": "unverified_schedule"`.
- At load time, `BNSCorpus` overrides this to `verified_schedule` for the 14 sections in `legal_engine/schedule_registry.py`. The stored field is therefore stale for those 14.

### 4.3 Registry vs corpus for the 14 registry sections

- **Titles:** match for all 14.
- **Registry classifications:** match the Gazette rows for all 14 (checked row by row in the earlier round).
- **Embedded blocks:** for Sections 305, 306, 314 and 352 they agree with the registry. The others have no embedded block.
- **Punishment fields:** only Section 309 is wrong (see Section 1 of this report). The fields for Sections 303 (including the community-service proviso) and 115 were read in full and are complete.

## Recommendations (not yet implemented; each needs approval)

1. Re-extract the punishment fields for Sections 309, 311, 312, 54, 264 and the sections listed in Section 1 from the Gazette text, and record the source of each correction.
2. Restore the full text of Sections 111 and 120, and review Sections 112 and 113.
3. Move the embedded "BNSS Classification" blocks out of `text` into a separate, clearly labelled field. Stop presenting them to Gemini as "Official Text". Correct or drop the classifications for Sections 87, 90 and 276. Changing `text` will change BM25 retrieval, so benchmarks must be re-run.
4. Replace the blanket `verified: true` with per-record provenance (`source_document`, `checked_on`, `similarity_to_gazette`, `checked_by`) and treat records below a review threshold as unverified.
5. Stop storing `schedule_i_status` in the dataset, or derive it from the registry when the corpus is built.

## Items requiring qualified legal review

- Whether the corrected punishment wording for Sections 309, 311 and 312 accurately represents the enacted text and any later amendments.
- The classifications for Sections 87, 90 and 276, and Sections 354, 355 and 357, which could not be checked automatically.
