# BNSS Section 173(3): G-1 and G-2 Verification Record

**Prepared:** 2026-10-21 (work done 02:29–03:30 IST) by the Bandhoo maintainer session.
**For:** the project owner (PO), the second checker (SC), the source-acquisition owner (SAO), QLR 1, QLR 2 and the adjudicator (ADJ).
**Covers:** gaps G-1 and G-2, and triage items T-1, T-2, T-4 and T-5 in `reports/section_173_3_new_findings_triage.md`.

**Status:** evidence-acquisition record.
- **G-1 independent verification is not done and is pending.** The operator is the dossier's author and cannot act as the SC (§1).
- G-2 enactment status remains **UNKNOWN** for every bill.
- No legal determination is made. No register, queue, report, code, test, corpus or benchmark file is changed.

Bandhoo remains internal-testing-only.

---

## 0. Stages

Each stage is distinct. Completing one does not complete the next.

| Stage | Meaning | G-1 (judgments) | G-2 (Maharashtra bills) | Changes A, B/RB-53, C (D-1 to D-3) |
|---|---|---|---|---|
| **1. Source acquisition** | Obtaining documents from official hosts; recording URL, TLS, hash and identity | **Done** for SC-IP, SC-AD, the *Lalita Kumari* 2013 judgment and the S.C.R. **Not done** for the 5 Mar 2014 order (official copy not found) or the SCC report (inaccessible). | **Partly done:** bill texts and Gazette publications obtained. No Act, assent or commencement record found. | Not applicable |
| **2. Independent verification** | SC (independent of the dossier author) compares the sources with the transcriptions | **Pending:** no SC appointed. Worksheet prepared (§2.5). | **Pending:** no SC appointed | Not applicable |
| **3. Legal approval** | QLR 1 and QLR 2 agree, or the ADJ resolves | Not started | Not started | Not started; all Blocked |
| **4. Implementation approval** | MNT and PO approve an exact change (change protocol) | Not applicable | Not applicable | Not given |
| **5. Completed validation** | Gates 5–9 recorded for an implemented change | Not applicable | Not applicable | Not done. Scratch dry runs are **not** validation. |

## 1. Independence and assignments

- **Operator:** the Bandhoo maintainer session, which wrote `reports/section_173_3_case_law_review_dossier.md`. Under the reviewer assignment template (Part 1, rule 2) **it must not act as the SC**.
- Everything in §2 below is source acquisition and preparation. **It is not the G-1 check.**
- `reports/reviewer_assignment_template.md` (checked 2026-10-21): QLR 1, QLR 2, ADJ, SC, EL and SAO are all **"Assignment pending: not appointed"**, and **PO approval is "Not given"**.
- No name, qualification, approval or date is recorded here.

---

## 2. G-1: Independent judgment verification (Workstream A)

### 2.1 Evidence table

| # | Document | Issuing court, date, case number | Official URL | SHA-256 | Status |
|---|---|---|---|---|---|
| A1 | *Imran Pratapgadhi v. State of Gujarat*, 2025 INSC 410 (54 pp.) | Supreme Court of India; judgment of 28 Mar 2025; Criminal Appeal No. 1545 of 2025 | `https://api.sci.gov.in/supremecourt/2025/3511/3511_2025_4_1501_60508_Judgement_28-Mar-2025.pdf` | `896f08f97519248a7f004350d43b72ffc296144e817c0be8b0365bd28f0d5a58` | **Verified** (provenance: re-downloaded 2026-10-21, TLS verified, hash identical to the earlier retrievals; PDF created 2025-03-28). **Quotation check: pending SC.** |
| A2 | *Ashish Dave v. State of Rajasthan*, 2026 INSC 244 (23 pp.) | Supreme Court of India; order of 27 Feb 2026; Criminal Appeal (number blank in PDF) arising out of SLP (Crl.) No. 19369 of 2025 | `https://api.sci.gov.in/supremecourt/2025/68616/68616_2025_2_34_68884_FinalOrder_27-Feb-2026.pdf` | `3350c58215253837483fbe01397717b841f08cbb25ac2d5cbfb31edaff81bc0b` | **Verified** (provenance; PDF created 2026-03-16). **Quotation check: pending SC.** |
| A3 | *Lalita Kumari v. Govt. of U.P. & Ors.*, original judgment (93 pp.) | Supreme Court of India (five-judge bench: P. Sathasivam CJI, Dr. B.S. Chauhan, Ranjana Prakash Desai, Ranjan Gogoi, S.A. Bobde JJ.); 12 Nov 2013; W.P. (Crl.) No. 68 of 2008 with connected matters | `https://api.sci.gov.in/jonew/judis/40960.pdf` | `358a73362bb57582fcd2399bd40a5f4e60b14e6a5870383dbc67b1b7ec3a57a6` | **Verified** (provenance; PDF created 2013-11-13; signature block "NEW DELHI; NOVEMBER 12, 2013."). **Quotation check: pending SC.** |
| A4 | [2013] 14 S.C.R. 713, *Lalita Kumari v. Govt. of U.P. and Ors.* (90 pp.) | Supreme Court Reports (official reporter), published on the Supreme Court's asset store | `https://cdnbbsr.s3waas.gov.in/s3ec0490f1f4972d133619a60c30f3559e/documents/aor_notice_circular/31.pdf` | `2dee8917c4dd55d61f6ba224d110083ae1ae074bb345ff4dd9c1c08b3c1a161c` | **Verified** (provenance). The text layer is **OCR** (PDFium, created 2021-10-22), so emphasis cannot be read by machine and the SC must check visually. |
| A5 | **Supreme Court order of 5 Mar 2014**, reported as Crl.M.P. No. 5029 of 2014 in W.P. (Crl.) No. 68 of 2008, said to modify para 111(vii) | Supreme Court of India (reported) | **Not found** | — | **Searched, not found** (official copy). See §2.3. |
| A6 | SCC report, (2014) 2 SCC 1 | Eastern Book Company (subscription reporter) | — | — | **Inaccessible** (subscription; not accessed, nothing bypassed). The 119/120 numbering in A1/A2 is **not** verified as SCC numbering. |
| A7 | Manupatra print MANU/SC/1166/2013 (LK-MPHC) | Third-party reporter, hosted on mphc.gov.in | (dossier §1) | — | **Located but not independently verified** (TLS unverified when obtained). Used for comparison only. |

### 2.2 *Lalita Kumari*: paragraph numbering and direction (vii)

All comparisons below are the maintainer's machine comparison, pending the SC.

**Paragraph numbering:**

| Source | "Counter claims" passage | Conclusions / directions | Direction (vii) location |
|---|---|---|---|
| A3 official 2013 copy | **110)** (PDF pp.88–89) | **111)** (i)–(viii) (PDF pp.90–92) | PDF p.92 |
| A4 S.C.R. | **110.** (printed p.800; PDF p.88) | **111.** (printed pp.800–802) | printed p.802 (PDF p.90); headnote "[Para 111 vii] [802-C]" |
| A1 *Imran Pratapgadhi* (quoting) | — | "Paragraph 120", "120.1"–"120.8", footnote "(2014) 2 SCC 1" (PDF pp.21–24); "paragraph 120.2" (p.25) | "120.7" (PDF p.23) |
| A2 *Ashish Dave* (quoting) | "**119.**" (PDF pp.11–12), footnote 7 "(2014) 2 SCC 1." | — | — |
| A6 SCC report | **Not verified** | **Not verified** | **Not verified** |

**Direction (vii), compared:**

| Source | Wording (machine extraction) | Status |
|---|---|---|
| A3 official 2013 copy, para 111(vii), PDF p.92 | "(vii) While ensuring and protecting the rights of the accused and the complainant, a preliminary inquiry should be made time bound and in any case it should not exceed **7 days**. The fact of such delay and the causes of it must be reflected in the General Diary entry." | Verified source; text pending SC |
| A4 S.C.R., para 111(vii), printed p.802 | Same words, "should not exceed 7 days" (OCR noise aside) | Verified source; text pending SC |
| A7 Manupatra print, 111(vii) | "…should not exceed fifteen days generally and in exceptional cases, by giving adequate reasons, six weeks time is provided…" | Not independently verified |
| A1 *Imran Pratapgadhi*, quoted "120.7", PDF p.23 | "…a preliminary inquiry should be made time-bound and in any case it should not exceed fifteen days generally and in exceptional cases, by giving adequate reasons, six weeks' time is provided…" | Verified source; quotation pending SC |
| A5 order of 5 Mar 2014 | Secondary copies (Indian Kanoon doc 59058631; a Scribd upload) are reported to modify clause (vii) to "fifteen days generally … six weeks". **Not read from an official copy.** | Searched, not found (official) |

**Other word differences between A3 para 111 and A1's "120" quotation** (machine word diff; for the SC to confirm):
- numbering: 111)(i)–(viii) against 120.1–120.8;
- "Registration" against "**The** registration" in (i)/120.1;
- "over 3 months delay" against "3 months**'** delay" in (vi)/120.6;
- "Matrimonial disputes/ family disputes" against "…disputes/family disputes";
- "time bound" against "time-bound" in (vii);
- "said **Diary**" against "said **diary**" in (viii).

A1 also marks 120.1 and 120.2 in **bold** and adds "(emphasis added)".

**A3 para 110 against A2's "119." quotation:**
- "counter claims" against "counterclaims";
- A2 adds "…." and stops after "…whether a cognizable offence has been committed". A3 continues: "But, if the information given clearly mentions the commission of a cognizable offence, there is no other option but to register an FIR forthwith. …";
- A2 marks the second half of the quotation in bold and adds "[Emphasis supplied]".

**A4 S.C.R. against A3:** no word differences other than OCR artefacts (margin letters, running heads, "fo,r", "nc;>t") and the numbering style "111." against "111)". The S.C.R. contains **no reference** to any later modification: its only occurrences of "modif-" concern the Code of 1872.

**What this does not decide:**
- whether the 2013 direction (vii) was modified, and by what wording;
- which text is operative;
- which numbering to cite;
- whether any *Lalita Kumari* time limit bears on BNSS s.173(3).

All four are QLR questions (§4).

### 2.3 The 5 March 2014 order (separate document)

| Search | Date | Result |
|---|---|---|
| Official Supreme Court judgment archive (`api.sci.gov.in/jonew/judis/<id>.pdf`), calibrated by date: ID 41100 is from 17 Dec 2013, 41300 from 6 Mar 2014 (PDF created 7 Mar 2014), 41500 from 2 May 2014 | 2026-10-21 | IDs **41255–41360** scanned (106 IDs, one request per second). They cover documents dated about 21 Feb to late Mar 2014. **No *Lalita Kumari* document.** Nine IDs return empty (41256, 41266, 41287, 41293, 41295, 41296, 41302, and two in 41311–41360). Empty responses were retried once with the same result. |
| Web searches (4) for the official copy: "5029 of 2014", "05.03.2014", "orderpdfold", api.sci.gov.in | 2026-10-21 | No official copy. Secondary copies only: Indian Kanoon "Lalita Kumari vs Govt.Of U.P.. on 5 March, 2014" (`https://indiankanoon.org/doc/59058631/`), reported to contain a record of proceedings ("Crl.M.P. No.5029 of 2014, is disposed of in terms of the signed order") and the signed order; Scribd document 211348777. **Not relied on.** |
| Other-court reference (already in the log) | 2026-08-11 | The Delhi High Court CONT.CAS(C) 582/2023 order refers to the "judgment dated 12th November, 2013, and 05th March, 2014". **It confirms that the order existed. It is not a substitute for the order.** |

**Status:** the Supreme Court's own copy was searched for and not found; its wording and operative status are **not verified**.

**Next:** the SAO requests a certified copy from the Supreme Court Registry, or the Court's record of proceedings for Crl.M.P. No. 5029 of 2014 in W.P. (Crl.) No. 68 of 2008. The SC then compares it with A3, A4, A1 and A7.

### 2.4 Method used to prepare the worksheet

These steps are reproducible offline once the files are downloaded.

1. Download each official PDF; confirm the SHA-256 values in §2.1.
2. Extract characters with `pdfminer.six` 20240706, recording each character's font name and size (script `charlines.py`, SHA-256 `3674d359623c670477caa60d670b02d9ea33c8243fda61f1e70036cbac98b6e3`).
   - Style is taken from the embedded font name. Bold: `Bold/Black/Heavy/Semibold`. Italic: `Italic/Oblique`.
   - Fonts present include `BookmanOldStyle`, `BookmanOldStyle-Bold`, `BookmanOldStyle-Italic` and `BookmanOldStyle-BoldItalic` (A1, A2), and `DejaVuSans`, `DejaVuSans-Bold`, `DejaVuSans-Oblique` and `DejaVuSans-BoldOblique` (A3).
   - Characters smaller than 80% of the line's median size are treated as superscripts (footnote markers).
3. Render each passage (script `render_passages.py`, SHA-256 `1e06ecb8cf7b6ca36f60453814729eb9b8d49f22028322941a3d50234adb5800`; passage specification `spec.json`, SHA-256 `f355a7b4d80e196a2bbad8c3569c4b340235f6a38fb9ecddbf9b7e849fb9390c`):
   - fragments on the same baseline are merged;
   - running heads ("Criminal Appeal No.1545 of 2025 / Page N of 54"), bare page numbers and footnote lines (A1, A2: ≤11 pt starting with a number) are removed. Footnotes are listed separately per passage;
   - lines are joined with one space, except that a line ending in "-" joins without a space (the hyphen is kept);
   - runs of spaces are collapsed (justified text produces double spaces);
   - passages are located by start and end anchors compared on letters and digits only.
4. Markup in the worksheet:
   - `**bold**`, `*italic*`, `***bold italic***`;
   - `^n` = superscript footnote marker;
   - `⟦p.N⟧` = a PDF page break inside the passage.
5. **Limitations:**
   - Emphasis produced by other means (synthetic bold, underlining) is not detected.
   - Bold paragraph numbers are typographic formatting, not necessarily the Court's added emphasis.
   - Quotation marks and apostrophes are reproduced as encoded in the PDF.
   - The S.C.R. (A4) is OCR text and is not in the worksheet. The SC must read A4 visually.
   - **This is machine extraction, not verification.**

The scripts are in the session scratchpad, outside the repository, and are temporary. The SC may use any method but should **confirm visually against the rendered PDF**.

### 2.5 Second-checker worksheet

**Instructions for the SC** (to be completed only by an appointed SC who is independent of the dossier's author):
1. Re-download A1–A4 and confirm the hashes in §2.1. Stop if any differs.
2. For each passage below, open the PDF at the stated page. Confirm, by visual reading:
   - (a) the wording, including punctuation, word for word;
   - (b) the bold, italic and bold-italic spans;
   - (c) the PDF page and printed paragraph number;
   - (d) the passage type label (descriptive only).
3. Record each difference in the "SC result" line: wording, punctuation, emphasis, numbering, or extraction artefact.
4. Compare the dossier's text (sections in the "Dossier ref" column) with your reading. Note any dossier transcription error.
5. Read A4 (S.C.R.) paras 110–111 visually against LK-02 and LK-03, and note any difference other than numbering style.
6. Sign and date each entry and the index. Give the completed worksheet to QLR 1 and QLR 2 **without legal comment**.

#### Worksheet index

| ID | Document | PDF page(s) | Printed para / direction | Passage type | Dossier ref | SC: wording matches PDF? | SC: emphasis matches PDF? | SC initials / date |
|---|---|---|---|---|---|---|---|---|
| IP-01 | *Imran Pratapgadhi* (2025 INSC 410) | 2 | 3 | Facts (offences charged) | §3.2 | ____ | ____ | ____ |
| IP-02 | *Imran Pratapgadhi* (2025 INSC 410) | 16 | 19 | Statute quoted (BNS s.57) + Court's reasoning | §2.3, §3.5 | ____ | ____ | ____ |
| IP-03 | *Imran Pratapgadhi* (2025 INSC 410) | 16 | 20 (opening) | Court's framing of the question | §3.2 | ____ | ____ | ____ |
| IP-04 | *Imran Pratapgadhi* (2025 INSC 410) | 18 | 20 (statute quoted: s.173(3)) | Statute quoted | §2.1, §3.3 | ____ | ____ | ____ |
| IP-05 | *Imran Pratapgadhi* (2025 INSC 410) | 19 | 20 (after quotation) | Court's reasoning | §3.3 | ____ | ____ | ____ |
| IP-06 | *Imran Pratapgadhi* (2025 INSC 410) | 21 | 22 | Court's reasoning | §3.3 | ____ | ____ | ____ |
| IP-07 | *Imran Pratapgadhi* (2025 INSC 410) | 22–24 | 22 (Lalita Kumari quoted as "120") | Earlier judgment quoted | §3.3, §5.1 | ____ | ____ | ____ |
| IP-08 | *Imran Pratapgadhi* (2025 INSC 410) | 24–25 | 23 | Court's reasoning | §3.3 | ____ | ____ | ____ |
| IP-09 | *Imran Pratapgadhi* (2025 INSC 410) | 25–26 | 24 | Court's reasoning | §3.3 | ____ | ____ | ____ |
| IP-10 | *Imran Pratapgadhi* (2025 INSC 410) | 26 | 25 | Court's reasoning | §3.3 | ____ | ____ | ____ |
| IP-11 | *Imran Pratapgadhi* (2025 INSC 410) | 27 | 26 (last sentence) | Court's reasoning | §3.3 | ____ | ____ | ____ |
| IP-12 | *Imran Pratapgadhi* (2025 INSC 410) | 28 | 27 (last sentence) | Court's reasoning | §3.3 | ____ | ____ | ____ |
| IP-13 | *Imran Pratapgadhi* (2025 INSC 410) | 28 | 28 | Court's reasoning (application) | §3.3, §3.5 | ____ | ____ | ____ |
| IP-14 | *Imran Pratapgadhi* (2025 INSC 410) | 30–31 | 29 (part) | Court's reasoning | §3.3 | ____ | ____ | ____ |
| IP-15 | *Imran Pratapgadhi* (2025 INSC 410) | 31 | 31 | Court's reasoning (finding) | §3.3, §3.4 | ____ | ____ | ____ |
| IP-16 | *Imran Pratapgadhi* (2025 INSC 410) | 41–42 | 36 | Court's reasoning (finding) | §3.3 | ____ | ____ | ____ |
| IP-17 | *Imran Pratapgadhi* (2025 INSC 410) | 47–49 | 42(i)–(ii) | Court's stated conclusion | §3.3 | ____ | ____ | ____ |
| IP-18 | *Imran Pratapgadhi* (2025 INSC 410) | 49 | 42(iii) | Court's stated conclusion | §3.3 | ____ | ____ | ____ |
| IP-19 | *Imran Pratapgadhi* (2025 INSC 410) | 50–51 | 42(v) | Court's stated conclusion | §3.3 | ____ | ____ | ____ |
| IP-20 | *Imran Pratapgadhi* (2025 INSC 410) | 54 | 43–44; signature block | Order / disposal | §3.1, §3.3 | ____ | ____ | ____ |
| AD-01 | *Ashish Dave* (2026 INSC 244) | 1–2 | 4 | Facts (offences in FIR) | §4.2 | ____ | ____ | ____ |
| AD-02 | *Ashish Dave* (2026 INSC 244) | 5 | 8 | Court's reasoning | §4.3 | ____ | ____ | ____ |
| AD-03 | *Ashish Dave* (2026 INSC 244) | 7 | 13 | Court's reasoning | §4.4 | ____ | ____ | ____ |
| AD-04 | *Ashish Dave* (2026 INSC 244) | 11–12 | 22 (incl. Lalita Kumari quoted as "119.") | Court's reasoning + earlier judgment quoted | §4.3, §5.1 | ____ | ____ | ____ |
| AD-05 | *Ashish Dave* (2026 INSC 244) | 12 | 23 (Court's text) | Court's reasoning | §4.3 | ____ | ____ | ____ |
| AD-06 | *Ashish Dave* (2026 INSC 244) | 14–15 | 23 (statute quoted: s.173(3)–(4)) | Statute quoted | §2.1, §4.3 | ____ | ____ | ____ |
| AD-07 | *Ashish Dave* (2026 INSC 244) | 15–19 | 24 (Imran Pratapgadhi quoted) | Earlier judgment quoted | §4.3 | ____ | ____ | ____ |
| AD-08 | *Ashish Dave* (2026 INSC 244) | 19–20 | 24 (after quotation: "The crux …") | Court's reasoning | §4.3 | ____ | ____ | ____ |
| AD-09 | *Ashish Dave* (2026 INSC 244) | 20–21 | 25 | Court's reasoning (application) | §4.3, §4.5 | ____ | ____ | ____ |
| AD-10 | *Ashish Dave* (2026 INSC 244) | 21 | 27 (opening) | Court's reasoning | §4.3 | ____ | ____ | ____ |
| AD-11 | *Ashish Dave* (2026 INSC 244) | 23 | 28–30; signature block | Order / disposal | §4.1, §4.3 | ____ | ____ | ____ |
| LK-01 | *Lalita Kumari*, official 2013 copy (judis 40960) | 1 | Caption | Caption | §5 | ____ | ____ | ____ |
| LK-02 | *Lalita Kumari*, official 2013 copy (judis 40960) | 88–89 | 110 | Judgment text | §5.1 | ____ | ____ | ____ |
| LK-03 | *Lalita Kumari*, official 2013 copy (judis 40960) | 90–92 | 111 (i)–(viii) | Conclusions / directions | §5.1, §5.2 | ____ | ____ | ____ |
| LK-04 | *Lalita Kumari*, official 2013 copy (judis 40960) | 93 | 112; signature block | Disposal and coram | §5 | ____ | ____ | ____ |

#### IP-01: *Imran Pratapgadhi* (2025 INSC 410), para 3, PDF p. 2

- **Passage type:** Facts (offences charged). **Dossier:** §3.2. **Words:** 59.
- **Styled runs detected:** bold: "3.".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **3.** The appellant is a Member of the Rajya Sabha. The 2^nd respondent is the first informant at whose instance a First Information Report (for short, ‘FIR’) was registered with Jamnagar Police Station for the offences punishable under Sections 196, 197(1), 302, 299, 57 and 3(5) of the Bharatiya Nyaya Sanhita, 2023 (for short, ‘the BNS’).

#### IP-02: *Imran Pratapgadhi* (2025 INSC 410), para 19, PDF p. 16

- **Passage type:** Statute quoted (BNS s.57) + Court's reasoning. **Dossier:** §2.3, §3.5. **Words:** 48.
- **Styled runs detected:** bold: "19. “".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **19.** Section 57 of the BNS is alleged to be applicable, which reads thus: **“**57. Abetting commission of offence by public or by more than ten persons.—Whoever abets the commission of an offence by the public generally or by any number or class of persons exceeding ten,

#### IP-03: *Imran Pratapgadhi* (2025 INSC 410), para 20 (opening), PDF p. 16

- **Passage type:** Court's framing of the question. **Dossier:** §3.2. **Words:** 27.
- **Styled runs detected:** bold: "20.".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **20.** The question is whether in the facts of the case, it was obligatory under sub-Section (1) of Section 173 of the BNSS to register FIR.

#### IP-04: *Imran Pratapgadhi* (2025 INSC 410), para 20 (statute quoted: s.173(3)), PDF p. 18

- **Passage type:** Statute quoted. **Dossier:** §2.1, §3.3. **Words:** 107.
- **Styled runs detected:** italic: "i prima facie ii prima facie".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> (3) Without prejudice to the provisions contained in Section 175, on receipt of information relating to the commission of any cognizable offence, which is made punishable for three years or more but less than seven years, the officer in charge of the police station may with the prior permission from an officer not below the rank of Deputy Superintendent of Police, considering the nature and gravity of the offence,— (*i*) proceed to conduct preliminary enquiry to ascertain whether there exists a *prima facie* case for proceeding in the matter within a period of fourteen days; or (*ii*) proceed with investigation when there exists a *prima facie* case.

#### IP-05: *Imran Pratapgadhi* (2025 INSC 410), para 20 (after quotation), PDF p. 19

- **Passage type:** Court's reasoning. **Dossier:** §3.3. **Words:** 138.
- **Styled runs detected:** none.
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> Sub-Section (1) provides for giving information relating to the commission of a cognizable offence. It may be given orally or by electronic communication to the officer-in-charge of a police station. If the information discloses the commission of a cognizable offence, it is mandatory to record the substance of the information in a book to be kept by the officer in the form prescribed by the State Government. No further inquiry can be made by the police officer if the information discloses the commission of a cognizable offence. Therefore, subject to the exception carved out by sub-Section (3) of Section 173, which we will deal with later, it is mandatory to record the information in a book. Thus, it is mandatory to register the FIR if information received discloses the commission of a cognizable offence.

#### IP-06: *Imran Pratapgadhi* (2025 INSC 410), para 22, PDF p. 21

- **Passage type:** Court's reasoning. **Dossier:** §3.3. **Words:** 71.
- **Styled runs detected:** bold: "22."; bold italic: "Lalita Kumari v. Govt. of U.P.".
- **Footnotes on these pages (excluded from the text):** 2 (2014) 2 SCC 1.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **22.** Sub-Section (1) of Section 173 of BNSS is substantially the same as Sub-Section (1) of Section 154 of the Code of Criminal Procedure, 1973 (for short, ‘the CrPC’). Therefore, the law laid down by this Court in the case of ***Lalita Kumari v. Govt. of U.P.***^2 on Section 154 of the CrPC will be relevant. Paragraph 120 of the said decision containing conclusions/directions reads thus:

#### IP-07: *Imran Pratapgadhi* (2025 INSC 410), para 22 (Lalita Kumari quoted as "120"), PDF p. 22, 23, 24

- **Passage type:** Earlier judgment quoted. **Dossier:** §3.3, §5.1. **Words:** 445.
- **Styled runs detected:** bold: "“120. 120.1. The registration of FIR is mandatory under Section 154 of the Code, if the…"; italic: "a b c d e"; bold: "120.7. 120.8. ”".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **“120.** In view of the aforesaid discussion, we hold: **120.1. The registration of FIR is mandatory under Section 154 of the Code, if the information discloses commission of a cognizable offence and no preliminary inquiry is permissible in such a situation. 120.2. If the information received does not disclose a cognizable offence but indicates the necessity for an inquiry, a preliminary inquiry may be conducted only to ascertain whether cognizable offence is disclosed or not. 120.3.** If the inquiry discloses the commission of a cognizable offence, the FIR must be registered. In cases where preliminary inquiry ends in closing the complaint, a copy of the entry of such closure must be supplied to the first informant forthwith and not later than one week. It must disclose reasons in brief for closing the complaint and not proceeding further. **120.4.** The police officer cannot avoid his duty of registering offence if cognizable offence is disclosed. Action must be taken against erring officers who do not register the FIR if information received by him discloses a cognizable offence. **120.5.** The scope of preliminary inquiry is not to verify the veracity or otherwise of the information received but only to ascertain whether the information reveals any cognizable offence. ⟦p.23⟧ **120.6.** As to what type and in which cases preliminary inquiry is to be conducted will depend on the facts and circumstances of each case. The category of cases in which preliminary inquiry may be made are as under: (*a*) Matrimonial disputes/family disputes (*b*) Commercial offences (*c*) Medical negligence cases (*d*) Corruption cases (*e*) Cases where there is abnormal delay/laches in initiating criminal prosecution, for example, over 3 months' delay in reporting the matter without satisfactorily explaining the reasons for delay. The aforesaid are only illustrations and not exhaustive of all conditions which may warrant preliminary inquiry. **120.7.** While ensuring and protecting the rights of the accused and the complainant, a preliminary inquiry should be made time-bound and in any case it should not exceed fifteen days generally and in exceptional cases, by giving adequate reasons, six weeks' time is provided. The fact of such delay and the causes of it must be reflected in the General Diary entry. **120.8.** Since the General Diary/Station Diary/Daily Diary is the record of all information received in a police station, we direct that all information relating to cognizable offences, whether resulting in registration of FIR or leading to an inquiry, must be mandatorily and meticulously ⟦p.24⟧ reflected in the said diary and the decision to conduct a preliminary inquiry must also be reflected, as mentioned above.**”** (emphasis added)

#### IP-08: *Imran Pratapgadhi* (2025 INSC 410), para 23, PDF p. 24, 25

- **Passage type:** Court's reasoning. **Dossier:** §3.3. **Words:** 420.
- **Styled runs detected:** bold: "23."; bold italic: "Lalita Kumari ,"; italic: "prima facie"; bold italic: "Lalita Kumari ,"; italic: "prima facie prima facie"; bold italic: "Lalita Kumari".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **23.** Section 154 of the CrPC does not provide for making any preliminary inquiry. However, as held in the case of ***Lalita Kumari***^2***,*** a preliminary inquiry is permissible if the information received does not disclose a cognizable offence and indicates the necessity for an inquiry. A preliminary inquiry must be conducted only to ascertain whether a cognizable offence is disclosed. However, sub-Section (3) of Section 173 of the BNSS makes a significant departure from Section 154 of the CrPC. It provides that when information relating to the commission of a cognizable offence which is made punishable for 3 years or more but less than 7 years is received by an officer-in-charge of a police station, with the prior permission of a superior officer as mentioned therein, the police officer is empowered to conduct a preliminary inquiry to ascertain whether there exists a *prima facie* case for proceeding in the matter. However, under Section 154 of the CrPC, as held in the case of ***Lalita Kumari***^2***,*** only a limited preliminary inquiry is permissible to ascertain whether the information received discloses a cognizable offence. Moreover, a preliminary inquiry can be made under the CrPC only if the information does not disclose the ⟦p.25⟧ commission of a cognizable offence but indicates the necessity for an inquiry. Sub-Section (3) of Section 173 of the BNSS is an exception to sub-Section (1) of Section 173. In the category of cases covered by sub-Section (3), a police officer is empowered to make a preliminary inquiry to ascertain whether a *prima facie* case is made out for proceeding in the matter even if the information received discloses commission of any cognizable offence. That is very apparent as sub-Section (3) of Section 173 refers explicitly to receiving information relating to the commission of a cognizable offence. Therefore, in a case where sub-Section (3) of Section 173 is applicable, even if the information pertaining to the commission of any cognizable offence is received, an inquiry can be conducted to ascertain whether a *prima facie* case exists for proceeding in the matter. The intention appears to be to prevent the registration of FIRs in frivolous cases where punishment is up to 7 years, even if the information discloses the commission of the cognizable offence. However, under Section 154 of the CrPC, the inquiry permitted by paragraph 120.2 of the decision in the case of ***Lalita Kumari***^2 is limited only to ascertain whether the cognizable offence is disclosed.

#### IP-09: *Imran Pratapgadhi* (2025 INSC 410), para 24, PDF p. 25, 26

- **Passage type:** Court's reasoning. **Dossier:** §3.3. **Words:** 83.
- **Styled runs detected:** bold: "24."; italic: "prima facie prima facie".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **24.** Under sub-Section (3) of Section 173 of the BNSS, after holding a preliminary inquiry, if the officer comes to a conclusion that a *prima facie* case exists to proceed, he ⟦p.26⟧ should immediately register an FIR and proceed to investigate. But, if he is of the view that a *prima facie* case is not made out to proceed, he should immediately inform the first informant/complainant so that he can avail a remedy under sub-Section (4) of Section 173.

#### IP-10: *Imran Pratapgadhi* (2025 INSC 410), para 25, PDF p. 26

- **Passage type:** Court's reasoning. **Dossier:** §3.3. **Words:** 218.
- **Styled runs detected:** bold: "25.".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **25.** Before we go into the applicability of sub-Section (3) of Section 173 of the BNSS to the facts of the case, we must deal with sub-Section (1) of Section 173. Take a case where a person approaches an officer-in-charge of a police station either personally or by electronic communication and alleges that he has seen ‘A’ assaulting ‘X’ with a stick. If the injury caused is simple, it will be an offence punishable under Section 115 (2) of the BNS. As per the first Schedule of the BNSS, it is a non-cognizable offence. Therefore, based on such information, FIR cannot be registered. If grievous hurt is caused, it will be an offence punishable under Section 117 (2) of the BNS, which is a cognizable offence. Therefore, the allegations made in the information furnished to an officer-in-charge of a police station must be examined by the officer only with a view to ascertain whether a cognizable offence is made out. Taking the information as correct, the officer has to determine whether it makes out a case of the commission of a cognizable offence. If the allegation makes out a case of a cognizable offence, unless the offence falls in sub-Section (3) of Section 173, it is mandatory to register FIR.

#### IP-11: *Imran Pratapgadhi* (2025 INSC 410), para 26 (last sentence), PDF p. 27

- **Passage type:** Court's reasoning. **Dossier:** §3.3. **Words:** 28.
- **Styled runs detected:** none.
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> This act on the part of the police officer will not amount to making a preliminary inquiry which is not permissible under sub-Section (1) of Section 173.

#### IP-12: *Imran Pratapgadhi* (2025 INSC 410), para 27 (last sentence), PDF p. 28

- **Passage type:** Court's reasoning. **Dossier:** §3.3. **Words:** 22.
- **Styled runs detected:** none.
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> This exercise does not amount to making a preliminary inquiry which is prohibited under sub-Section (1) of Section 173 of BNSS.

#### IP-13: *Imran Pratapgadhi* (2025 INSC 410), para 28, PDF p. 28

- **Passage type:** Court's reasoning (application). **Dossier:** §3.3, §3.5. **Words:** 121.
- **Styled runs detected:** bold: "28."; italic: "prima facie".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **28.** Sub-Section (3) of Section 173 of the BNSS confers a discretion on the officer receiving information relating to the commission of a cognizable offence to conduct a preliminary inquiry to ascertain whether a *prima facie* case exists to proceed. This option is available when the offence alleged is made punishable for 3 years or more but less than 7 years. In the facts of the case, all the offences except the offence under Section 57 of the BNS are punishable by imprisonment for less than 7 years. Section 57, on the face of it, is not applicable. Therefore, this option was also available to the police officer in the present case. The officer did not exercise the said option.

#### IP-14: *Imran Pratapgadhi* (2025 INSC 410), para 29 (part), PDF p. 30, 31

- **Passage type:** Court's reasoning. **Dossier:** §3.3. **Words:** 262.
- **Styled runs detected:** italic: "prima facie prima facie".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> Therefore, when an allegation is of the commission of an offence covered by the law referred to in clause (2) of Article 19, if sub-Section (3) of Section 173 is applicable, it is always appropriate to conduct a preliminary inquiry to ascertain whether a *prima facie* case is made out to proceed against the accused. This will ensure that the fundamental rights guaranteed under sub-clause (a) of clause (1) of Article 19 remain protected. Therefore, in such cases, the higher police officer referred to in sub-Section (3) of Section 173 must normally grant permission to the police officer to conduct a preliminary inquiry. Therefore, when the commission of cognizable offences is alleged, where punishment is for imprisonment up to 7 years, which is based on spoken or written words, it will always be appropriate to exercise the option under sub-Section (3) of Section 173 and conduct a preliminary inquiry to ascertain whether there exists a *prima facie* case to proceed. If an option under sub-Section (3) is not exercised by the police officer in such a case, he may end up registering an FIR against a person who has exercised his fundamental right under Article 19 (1)(a) even though clause (2) of Article 19 is not attracted. If, in such cases, ⟦p.31⟧ the option under sub-Section (3) of Section 173 is not exercised, it will defeat the very object of incorporating sub-Section (3) of Section 173 of the BNSS and will also defeat the obligation of the police under Article 51-A (a).

#### IP-15: *Imran Pratapgadhi* (2025 INSC 410), para 31, PDF p. 31

- **Passage type:** Court's reasoning (finding). **Dossier:** §3.3, §3.4. **Words:** 44.
- **Styled runs detected:** bold: "31.".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **31.** In the facts of the case, even without taking recourse to sub-Section (3) of Section 173 of the BNSS, the information furnished to the police officer did not attract the offences punishable under Sections 196, 197, 299 and 302 of the BNS.

#### IP-16: *Imran Pratapgadhi* (2025 INSC 410), para 36, PDF p. 41, 42

- **Passage type:** Court's reasoning (finding). **Dossier:** §3.3. **Words:** 55.
- **Styled runs detected:** bold: "36."; italic: "prima facie".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **36.** In the instant case, as we have seen, no *prima facie* case can be said to have been made out against the appellant qua the sections invoked. In such a case, registration of the FIR appears to be a very mechanical ⟦p.42⟧ exercise and is a clear abuse of the process of law.

#### IP-17: *Imran Pratapgadhi* (2025 INSC 410), para 42(i)–(ii), PDF p. 47, 48, 49

- **Passage type:** Court's stated conclusion. **Dossier:** §3.3. **Words:** 313.
- **Styled runs detected:** bold: "42."; italic: "prima facie"; bold italic: "Lalita Kumari ,"; italic: "prima facie prima facie prima facie".
- **Footnotes on these pages (excluded from the text):** 10 (2015)  SCC 1.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **42.** Following is the summary of our conclusions: (i) Sub-Section (3) of Section 173 of the BNSS makes a significant departure from Section 154 of CrPC. It provides that when information relating to the commission of a cognizable offence which is made punishable for 3 years or more but less than 7 years is received by an officer-in-charge of a police station, with the prior permission of a superior officer as mentioned therein, the police officer is empowered to conduct a preliminary inquiry to ascertain whether there exists a *prima facie* case for ⟦p.48⟧ proceeding in the matter. However, under Section 154 of the CrPC, as held in the case of ***Lalita Kumari***^2***,*** only a limited preliminary inquiry is permissible to ascertain whether the information received discloses a cognizable offence. Moreover, a preliminary inquiry can be made under the CrPC only if the information does not disclose the commission of a cognizable offence but indicates the necessity for an inquiry. Sub-Section (3) of Section 173 of the BNSS is an exception to sub-Section (1) of Section 173. In the category of cases covered by sub-Section (3), a police officer is empowered to make a preliminary inquiry to ascertain whether a *prima facie* case is made out for proceeding in the matter even if the information received discloses commission of any cognizable offence. (ii) Under sub-Section (3) of Section 173 of the BNSS, after holding a preliminary inquiry, if the officer comes to a conclusion that a *prima facie* case exists to proceed, he should immediately register an FIR and proceed to investigate. But, if he is of the view that a *prima facie* case is not made out to proceed, he should immediately inform the first informant/complainant so that ⟦p.49⟧ he can avail a remedy under sub-Section (4) of Section 173.

#### IP-18: *Imran Pratapgadhi* (2025 INSC 410), para 42(iii), PDF p. 49

- **Passage type:** Court's stated conclusion. **Dossier:** §3.3. **Words:** 183.
- **Styled runs detected:** none.
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> (iii) In case of the offence punishable under Section 196 of the BNS to decide whether the words, either spoken or written or by sign or by visible representations or through electronic communication or otherwise, lead to the consequences provided in the Section, the police officer to whom information is furnished will have to read or hear the words written or spoken, and by taking the same as correct, decide whether an offence under Section 196 is made out. Reading of written words, or hearing spoken words will be necessary to determine whether the contents make out a case of the commission of a cognizable offence. The same is the case with offences punishable under Sections 197, 299 and 302 of BNS. Therefore, to ascertain whether the information received by an officer-in-charge of the police station makes out a cognizable offence, the officer must consider the meaning of the spoken or written words. This act on the part of the police officer will not amount to making a preliminary inquiry which is not permissible under sub-Section (1) of Section 173.

#### IP-19: *Imran Pratapgadhi* (2025 INSC 410), para 42(v), PDF p. 50, 51

- **Passage type:** Court's stated conclusion. **Dossier:** §3.3. **Words:** 179.
- **Styled runs detected:** italic: "prima facie".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> (v) Clause (2) of Article 19 of the Constitution carves out an exception to the fundamental right guaranteed under sub-clause (a) of clause (1) of Article 19. If there is a law covered by clause (2), its operation remains unaffected by sub-clause (a) of clause (1). We must remember that laws covered by the clause (2) are protected by way of ⟦p.51⟧ an exception provided they impose a reasonable restriction. Therefore, when an allegation is of the commission of an offence covered by the law referred to in clause (2) of Article 19, if sub-Section (3) of Section 173 is applicable, it is always appropriate to conduct a preliminary inquiry to ascertain whether a *prima facie* case is made out to proceed against the accused. This will ensure that the fundamental rights guaranteed under sub-clause (a) of clause (1) of Article 19 remain protected. Therefore, in such cases, the higher police officer referred to in sub-Section (3) of Section 173 must normally grant permission to the police officer to conduct a preliminary inquiry.

#### IP-20: *Imran Pratapgadhi* (2025 INSC 410), para 43–44; signature block, PDF p. 54

- **Passage type:** Order / disposal. **Dossier:** §3.1, §3.3. **Words:** 86.
- **Styled runs detected:** bold: "43. 44. New Delhi; March 28, 2025".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **43.** Though this judgment is authored by one of us (Abhay S. Oka, J.), it is based on valuable inputs by Ujjal Bhuyan, J. **44.** In the circumstances, the impugned order deserves to be set aside. We, accordingly, quash and set aside the impugned order. We also quash and set aside FIR No. 11202008250014 of 2025, registered with City A-Division Police Station, Jamnagar, and further proceedings based thereon. The Appeal is accordingly allowed. ……………………..J. (Abhay S. Oka) ……………………..J. (Ujjal Bhuyan) **New Delhi; March 28, 2025**

#### AD-01: *Ashish Dave* (2026 INSC 244), para 4, PDF p. 1, 2

- **Passage type:** Facts (offences in FIR). **Dossier:** §4.2. **Words:** 142.
- **Styled runs detected:** bold: "4.".
- **Footnotes on these pages (excluded from the text):** 1 Hereinafter, referred to as the “complainant-company”.; 2 For short, ‘BNS’.; 3 For short, ‘IPC’..
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **4.** The appellant before us, Ashish Dave, was serving as the Channel Head of a well-known media ⟦p.2⟧ house by name of Zee Rajasthan and Zee 24 Ghanta (West Bengal). The said media house is owned by a company named Zee Media Corporation Limited (ZMCL)^1. It appears that relations between the media house and the appellant herein ran into choppy waters in the year 2025, pursuant to which the authorised representative of the company approached Police Station Ashok Nagar, District Jaipur City (South), Rajasthan with a complaint, which straightaway came to be registered as FIR No.257 of 2025 dated 4^th September, 2025 for the offences punishable under Sections 308(2), 318(4) and 351(2) of the Bharatiya Nyaya Sanhita, 2023^2 (corresponding to Sections 384, 420, and 506 of the Indian Penal Code, 1860^3 respectively).

#### AD-02: *Ashish Dave* (2026 INSC 244), para 8, PDF p. 5

- **Passage type:** Court's reasoning. **Dossier:** §4.3. **Words:** 54.
- **Styled runs detected:** bold: "8.".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **8.** We are indeed surprised to note that the officials of Police Station Ashok Nagar, Jaipur City (South), acting with unusual expediency, accepted the said complaint and, without even making a bare attempt to verify the allegations made therein by semblance of a preliminary enquiry, straightaway proceeded to register the FIR for grave offences.

#### AD-03: *Ashish Dave* (2026 INSC 244), para 13, PDF p. 7

- **Passage type:** Court's reasoning. **Dossier:** §4.4. **Words:** 22.
- **Styled runs detected:** bold: "13."; italic: "supra ex facie,".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **13.** We are convinced that the complaint reproduced *supra*, *ex facie,* discloses no material whatsoever warranting registration of a First Information Report.

#### AD-04: *Ashish Dave* (2026 INSC 244), para 22 (incl. Lalita Kumari quoted as "119."), PDF p. 11, 12

- **Passage type:** Court's reasoning + earlier judgment quoted. **Dossier:** §4.3, §5.1. **Words:** 165.
- **Styled runs detected:** bold: "22."; italic: "prima facie"; bold italic: "Lalita Kumari v. Govt. of U.P."; bold: "“119. However, if no cognizable offence is made out in the information given, then the …".
- **Footnotes on these pages (excluded from the text):** 7 (2014) 2 SCC 1..
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **22.** In the given facts, the least that was expected from the police officials was to either require the complainant-company to furnish supporting material and details to *prima facie* make out the allegations made in the FIR, or else to hold a preliminary inquiry before registering the formal FIR. This conclusion finds support from the following observations made by this Court in ***Lalita Kumari v. Govt. of U.P.***^7 : - **“119.** Therefore, in view of various counterclaims regarding registration or non-registration, what is necessary is only that the information given to the police must disclose the commission of a cognizable offence. In such a situation, registration of an FIR is mandatory. **However, if no cognizable offence is made out in the information given, then the FIR need not be registered immediately and** ⟦p.12⟧ **perhaps the police can conduct a sort of preliminary verification or inquiry for the limited purpose of ascertaining as to whether a cognizable offence has been committed….”** [Emphasis supplied]

#### AD-05: *Ashish Dave* (2026 INSC 244), para 23 (Court's text), PDF p. 12

- **Passage type:** Court's reasoning. **Dossier:** §4.3. **Words:** 98.
- **Styled runs detected:** bold: "23."; italic: "prima facie".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **23.** The new regime under the BNSS specifically deals with such situations and provides an additional safeguard where the complaint is for offences carrying punishment between three to seven years. Sub-section (3) of Section 173 BNSS empowers the officer in charge of a police station, with prior permission of a superior officer, to conduct a preliminary inquiry to ascertain whether there exists a *prima facie* case for proceeding in the matter where the alleged offence is punishable with imprisonment for a term between three and seven years. For ease of reference, Section 173 BNSS is reproduced hereinunder:

#### AD-06: *Ashish Dave* (2026 INSC 244), para 23 (statute quoted: s.173(3)–(4)), PDF p. 14, 15

- **Passage type:** Statute quoted. **Dossier:** §2.1, §4.3. **Words:** 232.
- **Styled runs detected:** bold: "(3) Without prejudice to the provisions contained in Section 175, on receipt of informa…".
- **Footnotes on these pages (excluded from the text):** 8 (2026) 1 SCC 721..
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **(3) Without prejudice to the provisions contained in Section 175, on receipt of information relating to the commission of any cognizable offence, which is made punishable for three years or more but less than seven years, the officer in charge of the police station may with the prior permission from an officer not below the rank of Deputy Superintendent of Police, considering the nature and gravity of the offence, —** ⟦p.15⟧ **(i) proceed to conduct preliminary enquiry to ascertain whether there exists a prima facie case for proceeding in the matter within a period of fourteen days; or (ii) proceed with investigation when there exists a prima facie case. (4)** Any person aggrieved by a refusal on the part of an officer in charge of a police station to record the information referred to in sub-section (1), may send the substance of such information, in writing and by post, to the Superintendent of Police concerned who, if satisfied that such information discloses the commission of a cognizable offence, shall either investigate the case himself or direct an investigation to be made by any police officer subordinate to him, in the manner provided by this Sanhita, and such officer shall have all the powers of an officer in charge of the police station in relation to that offence failing which such aggrieved person may make an application to the Magistrate.” [Emphasis supplied]

#### AD-07: *Ashish Dave* (2026 INSC 244), para 24 (Imran Pratapgadhi quoted), PDF p. 15, 16, 17, 18, 19

- **Passage type:** Earlier judgment quoted. **Dossier:** §4.3. **Words:** 873.
- **Styled runs detected:** bold: "24."; bold italic: "Imran Pratapgadhi v. State of Gujarat"; bold: ", “23. However, sub-Section (3) of Section 173 of the BNSS makes a significant departur…".
- **Footnotes on these pages (excluded from the text):** 8 (2026) 1 SCC 721..
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **24.** This provision was considered by this Court in ***Imran Pratapgadhi v. State of Gujarat***^8**,** wherein ⟦p.16⟧ the scope of Section 173 BNSS has been explained as follows: - **“23.** Section 154 of the CrPC does not provide for making any preliminary inquiry. However, as held in the case of Lalita Kumari, a preliminary inquiry is permissible if the information received does not disclose a cognizable offence and indicates the necessity for an inquiry. A preliminary inquiry must be conducted only to ascertain whether a cognizable offence is disclosed. **However, sub-Section (3) of Section 173 of the BNSS makes a significant departure from Section 154 of the CrPC. It provides that when information relating to the commission of a cognizable offence which is made punishable for 3 years or more but less than 7 years is received by an officer-in-charge of a police station, with the prior permission of a superior officer as mentioned therein, the police officer is empowered to conduct a preliminary inquiry to ascertain whether there exists a prima facie case for proceeding in the matter. However, under Section 154 of the CrPC, as held in the case of Lalita Kumari, only a limited preliminary inquiry is permissible to ascertain whether the information received discloses a cognizable offence. Moreover, a preliminary inquiry can be made under the CrPC only if the information does not disclose the commission of a cognizable offence but indicates the necessity for an inquiry. Sub-Section (3) of Section 173 of the BNSS is an exception to sub-Section (1) of Section 173.In the category of cases covered by sub-Section (3), a police officer is empowered to make a preliminary inquiry to ascertain whether** ⟦p.17⟧ **a prima facie case is made out for proceeding in the matter even if the information received discloses commission of any cognizable offence. That is very apparent as sub-Section (3) of Section 173 refers explicitly to receiving information relating to the commission of a cognizable offence. Therefore, in a case where sub-Section (3) of Section 173 is applicable, even if the information pertaining to the commission of any cognizable offence is received, an inquiry can be conducted to ascertain whether a prima facie case exists for proceeding in the matter. The intention appears to be to prevent the registration of FIRs in frivolous cases where punishment is up to 7 years, even if the information discloses the commission of the cognizable offence. However, under Section 154 of the CrPC, the inquiry permitted by paragraph 120.2 of the decision in the case of Lalita Kumari is limited only to ascertain whether the cognizable offence is disclosed.** 24. Under sub-Section (3) of Section 173 of the BNSS, after holding a preliminary inquiry, if the officer comes to a conclusion that a prima facie case exists to proceed, he should immediately register an FIR and proceed to investigate. But, if he is of the view that a prima facie case is not made out to proceed, he should immediately inform the first informant/complainant so that he can avail a remedy under sub-Section (4) of Section 173. **25. Before we go into the applicability of sub-Section (3) of Section 173 of the BNSS to the facts of the case, we must deal with sub-Section (1) of Section 173. Take a case where a person** ⟦p.18⟧ **approaches an officer-in-charge of a police station either personally or by electronic communication and alleges that he has seen ‘A’ assaulting ‘X’ with a stick. If the injury caused is simple, it will be an offence punishable under Section 115 (2) of the BNS. As per the first Schedule of the BNSS, it is a non-cognizable offence. Therefore, based on such information, FIR cannot be registered. If grievous hurt is caused, it will be an offence punishable under Section 117 (2) of the BNS, which is a cognizable offence. Therefore, the allegations made in the information furnished to an officer-in-charge of a police station must be examined by the officer only with a view to ascertain whether a cognizable offence is made out. Taking the information as correct, the officer has to determine whether it makes out a case of the commission of a cognizable offence. If the allegation makes out a case of a cognizable offence, unless the offence falls in sub-Section (3) of Section 173, it is mandatory to register FIR.** [……] **28. Sub-Section (3) of Section 173 of the BNSS confers a discretion on the officer receiving information relating to the commission of a cognizable offence to conduct a preliminary inquiry to ascertain whether a prima facie case exists to proceed. This option is available when the offence alleged is made punishable for 3 years or more but less than 7 years. In the facts of the case, all the offences except the offence under Section 57 of the BNS are punishable by imprisonment for less than 7 years. Section 57,** ⟦p.19⟧ **on the face of it, is not applicable. Therefore, this option was also available to the police officer in the present case. The officer did not exercise the said option.”** [Emphasis supplied]

#### AD-08: *Ashish Dave* (2026 INSC 244), para 24 (after quotation: "The crux …"), PDF p. 19, 20

- **Passage type:** Court's reasoning. **Dossier:** §4.3. **Words:** 177.
- **Styled runs detected:** bold italic: "Lalita Kumari (supra)"; bold: ","; italic: "prima facie".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> The crux of the above observations, therefore, is that under the regime of Section 154 of the CrPC, as explained in ***Lalita Kumari (supra)*****,** a preliminary inquiry is permissible only for the limited purpose of ascertaining whether the information discloses the commission of a cognizable offence. However, the scheme of Section 173(3) of the BNSS travels a step further and exposits situations where preliminary inquiry may be made even where the complaint is filed for cognizable offences. The said provision empowers the police officer, even in a case where the information may ostensibly disclose the commission of a cognizable offence punishable between three and seven years, to conduct a preliminary inquiry so as to ascertain whether there exists a *prima facie* case for proceeding in the matter. Thus, the legislative intent behind incorporating sub-section (3) of Section 173 appears to be to provide a safeguard against mechanical registration of FIRs in cases where the allegations, though couched in the language of a ⟦p.20⟧ cognizable offence, may in substance be vague, speculative or inherently doubtful.

#### AD-09: *Ashish Dave* (2026 INSC 244), para 25, PDF p. 20, 21

- **Passage type:** Court's reasoning (application). **Dossier:** §4.3, §4.5. **Words:** 208.
- **Styled runs detected:** bold: "25."; italic: "“prima facie” prima facie".
- **Footnotes on these pages (excluded from the text):** 9 1992 Supp (1) SCC 335..
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **25.** None of the offences alleged in the impugned FIR carries imprisonment which may extend to more than seven years, thereby bringing the case within the category where the option of conducting a preliminary enquiry under Section 173(3) of the BNSS was clearly available to the police authorities. However, the police officials did not choose to exercise this option, and the FIR came to be registered straightaway in a mechanical manner without even a semblance of verification of the fictional and conjectural allegations made in the complaint. In the given facts, where the complaint contained vague allegations and was completely bereft of particulars, the situation clearly warranted a preliminary enquiry so as to arrive at the necessary *“prima facie”* satisfaction as to the commission of a cognizable offence. Though there is no hard and fast criterion for determining when such *prima facie* satisfaction may arise, the very object of permitting a preliminary enquiry is to prevent initiation of criminal proceedings on the basis of frivolous or speculative allegations. The allegations contained in ⟦p.21⟧ the complaint being so indeterminate and lacking in basic particulars, we are of the opinion that the police authorities ought to have exercised the option available under Section 173(3) of the BNSS.

#### AD-10: *Ashish Dave* (2026 INSC 244), para 27 (opening), PDF p. 21

- **Passage type:** Court's reasoning. **Dossier:** §4.3. **Words:** 76.
- **Styled runs detected:** bold: "27."; bold italic: "State of Haryana v. Bhajan Lal . Bhajan Lal (supra)".
- **Footnotes on these pages (excluded from the text):** 9 1992 Supp (1) SCC 335..
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **27.** The scope of powers of the High Court under Section 482 CrPC (528 of the BNSS) for quashing of the FIR was extensively considered by this Court in the case of ***State of Haryana v. Bhajan Lal***^9***.*** We are of the firm opinion that the case of the appellant is covered by the observations made by this Court in ***Bhajan Lal (supra)*** in paras 102(1), (2) & (5) of the judgment which read thus:

#### AD-11: *Ashish Dave* (2026 INSC 244), para 28–30; signature block, PDF p. 23

- **Passage type:** Order / disposal. **Dossier:** §4.1, §4.3. **Words:** 125.
- **Styled runs detected:** bold: "28. 29. 30. 31. ….……………………J. (VIKRAM NATH) ...…………………….J. (SANDEEP MEHTA) NEW DELHI; FE…".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **28.** In view of the discussion made hereinabove, there is no doubt in our mind that allowing the continuance of investigation pursuant to the impugned FIR against the appellant is nothing short of a gross abuse of the process of law. **29.** Hence, the impugned order dated 26^th November, 2025 passed by the High Court is set aside. As a consequence, FIR No.257 of 2025 dated 4^th September, 2025 registered at Police Station Ashok Nagar, District Jaipur City (South), Rajasthan and all proceedings sought to be taken against the appellant in pursuance thereof, are quashed. **30.** The appeal stands allowed accordingly. **31.** Pending application(s), if any, shall stand disposed of. **….……………………J. (VIKRAM NATH) ...…………………….J. (SANDEEP MEHTA) NEW DELHI; FEBRUARY 27, 2026.**

#### LK-01: *Lalita Kumari*, official 2013 copy (judis 40960), para Caption, PDF p. 1

- **Passage type:** Caption. **Dossier:** §5. **Words:** 19.
- **Styled runs detected:** bold: "WRIT PETITION (CRIMINAL) NO. 68 OF 2008".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> **WRIT PETITION (CRIMINAL) NO. 68 OF 2008** Lalita Kumari .... Petitioner (s) Versus Govt. of U.P. & Ors. .... Respondent(s)

#### LK-02: *Lalita Kumari*, official 2013 copy (judis 40960), para 110, PDF p. 88, 89

- **Passage type:** Judgment text. **Dossier:** §5.1. **Words:** 215.
- **Styled runs detected:** italic: "ex facie".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> 110) Therefore, in view of various counter claims regarding registration or non-registration, what is necessary is only that the information given to the police ⟦p.89⟧ must disclose the commission of a cognizable offence. In such a situation, registration of an FIR is mandatory. However, if no cognizable offence is made out in the information given, then the FIR need not be registered immediately and perhaps the police can conduct a sort of preliminary verification or inquiry for the limited purpose of ascertaining as to whether a cognizable offence has been committed. But, if the information given clearly mentions the commission of a cognizable offence, there is no other option but to register an FIR forthwith. Other considerations are not relevant at the stage of registration of FIR, such as, whether the information is falsely given, whether the information is genuine, whether the information is credible etc. These are the issues that have to be verified during the investigation of the FIR. At the stage of registration of FIR, what is to be seen is merely whether the information given *ex facie* discloses the commission of a cognizable offence. If, after investigation, the information given is found to be false, there is always an option to prosecute the complainant for filing a false FIR.

#### LK-03: *Lalita Kumari*, official 2013 copy (judis 40960), para 111 (i)–(viii), PDF p. 90, 91, 92

- **Passage type:** Conclusions / directions. **Dossier:** §5.1, §5.2. **Words:** 420.
- **Styled runs detected:** none.
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> 111) In view of the aforesaid discussion, we hold: (i) Registration of FIR is mandatory under Section 154 of the Code, if the information discloses commission of a cognizable offence and no preliminary inquiry is permissible in such a situation. (ii) If the information received does not disclose a cognizable offence but indicates the necessity for an inquiry, a preliminary inquiry may be conducted only to ascertain whether cognizable offence is disclosed or not. (iii) If the inquiry discloses the commission of a cognizable offence, the FIR must be registered. In cases where preliminary inquiry ends in closing the complaint, a copy of the entry of such closure must be supplied to the first informant forthwith and not later than one week. It must disclose reasons in brief for closing the complaint and not proceeding further. ⟦p.91⟧ (iv) The police officer cannot avoid his duty of registering offence if cognizable offence is disclosed. Action must be taken against erring officers who do not register the FIR if information received by him discloses a cognizable offence. (v) The scope of preliminary inquiry is not to verify the veracity or otherwise of the information received but only to ascertain whether the information reveals any cognizable offence. (vi) As to what type and in which cases preliminary inquiry is to be conducted will depend on the facts and circumstances of each case. The category of cases in which preliminary inquiry may be made are as under: (a) Matrimonial disputes/ family disputes (b) Commercial offences (c) Medical negligence cases (d) Corruption cases (e) Cases where there is abnormal delay/laches in initiating criminal prosecution, for example, over 3 months delay in reporting the matter without ⟦p.92⟧ satisfactorily explaining the reasons for delay. The aforesaid are only illustrations and not exhaustive of all conditions which may warrant preliminary inquiry. (vii) While ensuring and protecting the rights of the accused and the complainant, a preliminary inquiry should be made time bound and in any case it should not exceed 7 days. The fact of such delay and the causes of it must be reflected in the General Diary entry. (viii) Since the General Diary/Station Diary/Daily Diary is the record of all information received in a police station, we direct that all information relating to cognizable offences, whether resulting in registration of FIR or leading to an inquiry, must be mandatorily and meticulously reflected in the said Diary and the decision to conduct a preliminary inquiry must also be reflected, as mentioned above.

#### LK-04: *Lalita Kumari*, official 2013 copy (judis 40960), para 112; signature block, PDF p. 93

- **Passage type:** Disposal and coram. **Dossier:** §5. **Words:** 49.
- **Styled runs detected:** bold: "(P. SATHASIVAM) (DR. B.S. CHAUHAN) (RANJANA PRAKASH DESAI) (RANJAN GOGOI) (S.A. BOBDE)".
- **Footnotes on these pages (excluded from the text):** none.
- **SC result:** wording ____ · emphasis ____ · page/para ____ · differences ____ · initials/date ____

> 112) With the above directions, we dispose of the reference made to us. List all the matters before the appropriate Bench for disposal on merits. ………………………………CJI. **(P. SATHASIVAM)** ………….……………………J. **(DR. B.S. CHAUHAN)** ………….………………………J. **(RANJANA PRAKASH DESAI)** ……….………………………J. **(RANJAN GOGOI)** ………….……………………J. **(S.A. BOBDE)** NEW DELHI; NOVEMBER 12, 2013.

**G-1 status: PENDING.** No independent check has been performed. Inspecting and extracting the files, as done here, does not complete G-1.

---

## 3. G-2: Maharashtra legislation (Workstream B)

### 3.1 Search log (2026-10-21)

| # | Source (issuing authority) | Method and terms | Coverage | Result | Status |
|---|---|---|---|---|---|
| B1 | Maharashtra Government e-Gazette (Directorate of Government Printing, Government of Maharashtra), `https://egazzete.mahaonline.gov.in/Forms/GazetteSearch.aspx` (TLS verified) | Search form, Division "CENTRAL SECTION", dates 01/01/2026–21/10/2026, Extra-Ordinary and Ordinary, **every section** offered except Part two (supplement) and Part two (change in name): Parts 1, 1-L, 1-A, II (Sankirn), IV (Marathi), IV-A, IV-B, IV-C, V (Marathi), V-A (English), VI, VII (Hindi), VIII (English), Rajpatra Part-II, Part-XII. All result pages read. Descriptions scanned for "Nagarik", "Suraksha Sanhita", "Nyaya Sanhita", "BNSS", "BNS", "नागरिक सुरक्षा", "न्याय संहिता", "173", "Criminal Procedure", "फौजदारी प्रक्रिया", "preliminary enquiry", "प्राथमिक चौकशी" | **1,952 notices** | Only **bill publications** of L.C. Bills VI and XVII and L.A. Bill XXX (§3.3), plus ten Home Department notifications under the BNSS (§3.4). **No Act, Ordinance or commencement notification** relating to any of the three bills. Latest Maharashtra Act: **No. LIV of 2026**, 6 Oct 2026 (Dr. Babasaheb Ambedkar Technological University (Amendment) Act, 2026; Gazette copy obtained, SHA-256 `d9e8c48e…89bc0`). | **Searched, not found** (Act and commencement) |
| B2 | Maharashtra Legislature Secretariat, `https://mls.org.in/` | Pages: `Vidheyake_Assembly-2026.aspx` and `Vidheyake_Council-2026.aspx`, and their stage lists: `…Assembly-2026-L-C-Bill-introduce`, `…Assembly-2026-L-A-Bill`, `…Assembly-2025-L-C-Bill-pass`, `…Council-2026-L-A-Bill`, `…Council-2026-L-C-Bill-introduce`, `…Council-2026-L-C-Bill-pass`; plus the unlinked `…Assembly-2026-L-C-Bill-pass` | 7 pages | L.C. Bills VI and XVII: listed as introduced in and **passed by the Council**. **There is no 2026 list of Council bills passed by the Assembly**: the unlinked 2026 URL returns 404, and only a 2025 page exists. L.A. Bill XXX: listed as introduced in the Assembly and among "Assembly's 2026 bills passed by the Council". **It is not in the Assembly's own 2026 "passed" list** (L.A. Nos. 8, 9, 15, 16, 17, 20, 21, 22, 23, 27, 28, 33, 34, 35), although its "as passed" text states Assembly passage on 25 Mar 2026. This inconsistency is unresolved. | Partly located |
| B3 | Same, 2026 session business reviews (from the log) | Scanned PDFs read visually | 4 PDFs | Counts only; no bill titles | Searched, not found (titles) |
| B4 | Law and Judiciary Department, `https://lj.maharashtra.gov.in/` (from the log, same day) | Site search; law-list categories | 26 entries | No 2026 Act; the listings are incomplete | Searched, not found |
| B5 | Bombay High Court library mirror (from the log, same day) | Acts 2026.53–60 | — | Up to No. LIII; lags the Gazette | Searched, not found |

### 3.2 Bill-by-bill enactment checklist

| Item | **L.C. Bill No. VI of 2026** (BNSS; clause 6: "six weeks" for "fourteen days" in s.173(3)(i)) | **L.C. Bill No. XVII of 2026** (BNSS; clause 7: same substitution) | **L.A. Bill No. XXX of 2026** (BNS ss.72 and 75) |
|---|---|---|---|
| Bill text and publication | **Verified.** Introduced in the Council on 18 Mar 2026. Gazette: Part V-A, Ext. No. 20, 18 Mar 2026 (SHA-256 `754b0ae995535109b99da99770153a80ce6270d0ab1a2abc48c068dd2de1b39c`). | **Verified.** Introduced in the Council on 3 Jul 2026. Gazette: Part V Ext. 60; Part V-A Ext. 44; Part VII Ext. 53 (Hindi); Part VIII Ext. 81 (SHA-256 `25bf19e62efa3ef441a62fa8f77a63b7b398118bfebdd0206c5767aa0379145f`), all 3 Jul 2026. | **Verified.** Introduced in the Assembly on 25 Mar 2026. Gazette: Part V Ext. 33; Part V-A Ext. 26; Part VII Ext. 28; Part VIII Ext. 41 (SHA-256 `c77297f9066b704bfed366718367a78a202072ac62193104f46c70a5bde42929`), all 25 Mar 2026. |
| Passage by the Council | **Verified:** "(As passed by the Legislative Council on the 24th March, 2026.)" (Legislature copy, SHA-256 `a21184fe23b0dbf4d5d4c5df54f662c9123e68572ec9ed09cad9f511dffcf938`) | **Verified:** "(As passed by the Legislative Council on the 8th July, 2026.)" (SHA-256 `1d2ecbc1d7cf4f9dfbb61b8eb96e7f8af145ebfe449f3cba40559918a18b0af8`) | **Verified:** "(As passed by the Legislative Council on the 25th March, 2026.)" (SHA-256 `3afa7daca03b9cce5962894c6e15cb3034a755f10745293b8bc8505af31a5c16`) |
| **1. Passage by the Assembly** | **Searched, not found.** No 2026 list of Council bills passed by the Assembly; the session reviews give counts only. | **Searched, not found** (as Bill VI) | **Located, not independently verified:** the "as passed" text states "(As passed by the Legislative Assembly on the 25th March, 2026.)", but the Assembly's own 2026 passed list omits No. 30 (B2) |
| **2. Assent and its date** | **Searched, not found.** Who must assent (Governor, or President on reservation) is a QLR question. | **Searched, not found** | **Searched, not found** |
| **3. Act number and Gazette publication** | **Searched, not found** (B1: Acts up to LIV, 6 Oct 2026; none is this bill) | **Searched, not found** | **Searched, not found** |
| **4. Commencement** | **Searched, not found.** No commencement notification in B1. The bill's clause 1 has no commencement sub-clause (extracted text); how commencement would be fixed is a QLR question. | **Searched, not found** (as Bill VI) | **Searched, not found** (as Bill VI) |
| **5. Final enacted text and provisions** | **Not available** (no Act). The bill (as passed by the Council) amends, among others, s.173(3)(i). | **Not available.** The bill amends, among others, ss.15, 129, 170, 173(3)(i) and 482 (per its Statement of Objects). | **Not available.** The bill would amend s.72(1) (insert "or section 124") and s.75(1)–(2) (add clauses (v)–(viii)). |
| **Status** | **UNKNOWN. Not law.** | **UNKNOWN. Not law.** | **UNKNOWN. Not law.** |

Neither the passage of a bill by one or both Houses, nor the absence of search results, establishes or rules out enactment.

### 3.3 Note on L.C. Bill XVII's Statement of Objects

The Statement of Objects refers to "the Maharashtra Act No. VII of 1981". That was an amendment to the Code of Criminal Procedure, 1973, which the bill proposes to carry into the BNSS (s.170). **It is not evidence of an earlier BNSS amendment Act.**

### 3.4 Home Department notifications under the BNSS in 2026 (Part IV-A; all opened and read)

None concerns a Maharashtra amendment Act or s.173.

| Date | Ext. No. | Number | Subject (from the notification text) | SHA-256 (first 16) |
|---|---|---|---|---|
| 08-01-2026 | 17 | PRO-1225/C.R.57(E-1519739)/Special-2 | Special Executive Magistrates (s.15), election period | `cbd5c94b1d3d6f1b` |
| 21-01-2026 | 48 | MISC-3625/C.R.197/Pol-3 | Amends a police-station notification (s.2(1)(u)) | `b6a1df452eab96af` |
| 21-01-2026 | 49 | BNSS-0925/C.R.102/Special-09 | Maharashtra Audio-Video Electronic Means Rules, 2026 (s.2(1)(a)) | `172c14810ed99345` |
| 06-02-2026 | 82 | PRO-0226/C.R.05/Special-2 | Special Executive Magistrates (s.15), annual fair | `1a8ed2f040973065` |
| 10-02-2026 | 87 | PRO-0624/C.R.31/Spl-2 | Special Executive Magistrates (s.15) | `5a2232fcb5fc6526` |
| 10-02-2026 | 88 | TTC-3625/C.R.167/Pol-3 | Declaration of police stations (s.2(1)(u)) | `7eb4d2b6bbc8840d` |
| 10-02-2026 | 89 | Sankirna-0624/448/C.R.59/Spl.1A | Tahsildars as Executive Magistrates; inquests (ss.14(1), 194(4)) | `25c75c016f485e9f` |
| 17-04-2026 | 176 | PRO-0426/C.R.08/Spl-2 | Special Executive Magistrates (s.15), bye-elections | `986479d2c73d628f` |
| 22-04-2026 | 178 | TTC-0325/C.R.160/Pol-3 | Declaration of police stations (s.2(1)(u)) | `d81ca98ef75ee89d` |
| 06-08-2026 | 328 | SUT-0526/CR.276/SPL-4 | Concerning extremist literature (recitals read; operative clause not recorded) | `e295e5a55fad0571` |

### 3.5 Effect on Bandhoo's Maharashtra use

**No amendment is verified, so no effect is recorded.**
- Each bill states that it amends the Sanhita "in its application to the State of Maharashtra". That is the bill's text, not a finding of law.
- If an Act is verified, the QLR must assess: its commencement date; its territorial scope against Bandhoo's Mumbai jurisdictions; and whether Bandhoo's statements ("fourteen days"; BNS ss.72 and 75 corpus text) need a jurisdiction note.
- How an amendment would apply to pending matters is **not** addressed. Corpus text is not changed.

### 3.6 Exact outstanding official records

| Bill | Records still needed |
|---|---|
| **L.C. Bill VI of 2026** | (1) A Legislature Secretariat record of Assembly passage, or of its status: the bill "as passed by both Houses", the Assembly proceedings, or a certified status. (2) A record of assent (Governor's, or the President's decision if reserved) with date. (3) The Maharashtra Government Gazette publication of the Act (Part IV and/or VIII) with Act number and the "First published, after having received the assent of …" line. (4) Any commencement notification, or the publication date if commencement depends on it (QLR to decide). (5) The enacted text, for SC comparison with clause 6. |
| **L.C. Bill XVII of 2026** | As Bill VI, items (1)–(5) (clause 7). Also: whether Bills VI and XVII were combined, superseded or withdrawn (a Legislature Secretariat record). |
| **L.A. Bill XXX of 2026** | (1) Resolution of the Assembly-list inconsistency (B2), by a Legislature Secretariat confirmation of Assembly passage on 25 Mar 2026. Then items (2)–(5) as above (clauses 2–3: BNS ss.72 and 75). |

---

## 4. Legal questions only appointed qualified reviewers can decide

QLR 1 and QLR 2 answer independently; the ADJ resolves any disagreement. Nothing is decided here.

1. **T-1:** Which text of *Lalita Kumari* direction (vii) is operative and should be cited: the 2013 text ("7 days"), the 5 Mar 2014 modified direction (once the official copy is verified), or both with explanation? Does either bear on BNSS s.173(3)? (Dossier QR-C2.)
2. **T-2:** Which paragraph references should Bandhoo's records use: official 110/111, the numbering of later judgments (119/120), or SCC numbering once verified? (QR-C4.)
3. **T-4 / T-5, once evidence exists:**
   - (a) The legal effect, the date of effect, and the territorial application of any enacted Maharashtra amendment.
   - (b) Whether assent by the Governor sufficed, or whether reservation for the President was required.
   - (c) How commencement is determined where an Act has no commencement clause.
   - (d) Whether Bandhoo's "fourteen days" or its BNS ss.72/75 text needs a Maharashtra qualification (QR-B4).
4. **T-3 (Kataria; unchanged from the triage):** whether the pending Supreme Court matter affects the s.173(3) decisions or requires a pause.
5. **Unchanged:** handoff L-A1 to L-A3 (Change A), L-B1 to L-B4 (Change B/RB-53), and L-C1 to L-C4 (D-1 to D-3). **These stay separately gated.**

## 5. Next actions (roles from the assignment template only)

| # | Action | Role |
|---|---|---|
| 1 | Record own name; appoint QLR 1, QLR 2, ADJ, SC, EL and SAO; approve in template Part 3 | **PO** |
| 2 | Complete the §2.5 worksheet (A1–A3 by machine extraction plus visual check; A4 visually) and sign | **SC** |
| 3 | Obtain the Supreme Court's copy of the 5 Mar 2014 order (Crl.M.P. No. 5029 of 2014 in W.P. (Crl.) No. 68 of 2008), by certified copy or record of proceedings | **SAO** |
| 4 | Compare the 2014 order with A3, A4, A1 and A7, and record the exact wording | **SC** |
| 5 | Obtain the SCC report (2014) 2 SCC 1 (licensed access) and map its paragraph numbering | **SAO**, then **SC** |
| 6 | Obtain the §3.6 records for each bill (Legislature Secretariat; Law and Judiciary Department; Gazette), and re-run search B1 monthly | **SAO** |
| 7 | Resolve the L.A. Bill XXX Assembly-list inconsistency with the Legislature Secretariat | **SAO** |
| 8 | Compare any enacted text with the bill clauses | **SC** |
| 9 | Decide §4 questions 1–4 on the handoff §7 forms | **QLR 1**, **QLR 2**; **ADJ** on disagreement |
| 10 | Decide whether to register the triage recommendations (RB-02.a, RB-54, RB-03.a, Q-18) and whether to add dated addenda recording this document's findings | **PO** |
| 11 | Live evaluation (G-6): only if the PO authorises it under the log's prerequisites | **EL**, **PO** |

## 6. Change control

- Only this document was created. No register or queue entry was added or closed. Every RB entry remains **Open** and every Q entry **Blocked**.
- Change A (RB-52/Q-16), Change B with RB-53 (Q-01 Step 1, Q-17), and Change C (D-1 to D-3) **remain separately gated**. Q-01 Step 2 (Maharashtra) remains blocked by G-2.
- Neither Maharashtra bill is treated as law. Corpus text, code, prompts, tests, benchmark labels and thresholds are unchanged.
- No Gemini call, scraper run or `.env` access occurred. All downloads went to the session scratchpad.
