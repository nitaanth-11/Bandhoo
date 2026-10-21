# BNSS Section 173(3): Source Acquisition Log

**Prepared:** 2026-10-21 (searches run 02:00–03:00 IST) by the Bandhoo maintainer session, for the project owner (PO), the second checker (SC), the source-acquisition owner (SAO), the evaluation lead (EL) and the qualified legal reviewers (QLR 1, QLR 2).
**Covers:** gaps G-1 to G-6 in `reports/section_173_3_review_readiness.md` §B.
**Status:** acquisition record only.
- No reviewer is appointed, so nothing here is SC-verified or QLR-reviewed.
- No legal conclusion is drawn. No blocker is closed; every correction-queue entry remains Blocked.
- The documents listed in "Related records" below are not modified; findings that affect them are listed in §8 for the PO to act on.

Bandhoo remains internal-testing-only.

**Related records:**
- `reports/section_173_3_case_law_review_dossier.md` (the "dossier");
- `reports/section_173_3_legal_review_handoff.md` (the "handoff");
- `reports/source_verification_matrix.md`;
- `reports/source_verification_summary.md`.

## 0. Status vocabulary and method

| Status | Meaning |
|---|---|
| **Located and verified** | Obtained from the issuing authority's own host with TLS verified. Identity checked against the document's own header and signature. SHA-256 recorded. *"Verified" means provenance and identity only; content still needs SC checking where quoted.* |
| **Located, not independently verified** | Seen on an official host but not fully checked, or seen only in a secondary source |
| **Searched, not found** | The named sources were searched on the stated date without result. **Not proof that the item does not exist.** |
| **Inaccessible** | The source exists or is expected, but could not be retrieved from this environment (HTTP error, no connection, subscription) |
| **Not yet searched** | No search made |

**Method:**
- Downloads used `curl` with certificate verification on (no warnings bypassed), and went to isolated scratch directories outside the repository.
- PDF text was extracted with `pypdf`. Scanned pages were read as images.
- Web searches were used only to **locate** documents. No statement below rests on a search snippet, blog or news report unless it is explicitly labelled *secondary*.
- No Gemini call was made, no `.env` was read, and no scraper was run.

---

## G-1. Second-checker verification of the judgment quotations

| Field | Record |
|---|---|
| Question | Do the quotations, PDF page numbers, paragraph numbers and Court-marked emphasis in dossier §3.3, §4.3 and §5.1 match the official PDFs exactly? |
| Sources | *Imran Pratapgadhi v. State of Gujarat*, Criminal Appeal No. 1545 of 2025, 2025 INSC 410, Supreme Court of India, 28 March 2025: `https://api.sci.gov.in/supremecourt/2025/3511/3511_2025_4_1501_60508_Judgement_28-Mar-2025.pdf`, SHA-256 `896f08f97519248a7f004350d43b72ffc296144e817c0be8b0365bd28f0d5a58`. *Ashish Dave v. State of Rajasthan*, arising out of SLP (Crl.) No. 19369 of 2025, 2026 INSC 244, Supreme Court of India, order dated 27 February 2026: `https://api.sci.gov.in/supremecourt/2025/68616/68616_2025_2_34_68884_FinalOrder_27-Feb-2026.pdf`, SHA-256 `3350c58215253837483fbe01397717b841f08cbb25ac2d5cbfb31edaff81bc0b` |
| Status | **Located and verified** (provenance; hashes identical on two retrievals, 2026-10-21). **Quotation check: not done.** It requires an SC independent of the dossier's author (this session). |
| Done this round | Confirmed that emphasis is recoverable: both PDFs embed named fonts with style suffixes (e.g. `BookmanOldStyle-Bold`, `BookmanOldStyle-Italic`, `BookmanOldStyle-BoldItalic`, `Calibri-Bold`, `Arial-ItalicMT`). A font-aware extraction found 120 styled text runs in *Imran Pratapgadhi* and 45 in *Ashish Dave*. This was a feasibility test only; its output is **not** a verification record. |
| What it does not establish | That the dossier's transcriptions are correct |
| Next action; owner | The **SC** runs the procedure below and records the results against dossier section IDs. The **PO** must appoint the SC first. |

**Procedure for the SC** (reproducible; Python 3 with `pypdf`; no network after download):
1. Download both PDFs from the URLs above. Run `shasum -a 256` and confirm the values above. Stop if they differ.
2. Open each PDF in an ordinary PDF viewer. For every row of dossier §3.3 and §4.3, find the passage on the stated page.
3. Compare word by word. Record every difference (wording, punctuation, capitalisation, footnote markers) in a table: dossier ref | PDF page | paragraph | difference | none/minor/material.
4. Confirm each paragraph number and page number. Confirm the passage type label (statute quoted / earlier judgment quoted / Court's reasoning / stated conclusion / order) by its position in the document. Labels are descriptive only; their legal weight is for the QLR.
5. **Emphasis:** where the Court wrote "[Emphasis supplied]" or "(emphasis added)", run the script below over the relevant page range. Record the bold, italic or bold-italic words. Then confirm visually in the viewer: italics used for case names and Latin phrases are not emphasis.
6. For dossier §5.1, compare the *Lalita Kumari* quotations (SC-IP para 22; SC-AD para 22) with the official judgment and the S.C.R. report located under G-4. Note that the official numbering is 110/111, not 119/120 (see G-4).
7. Sign and date the record. Give it to QLR 1 and QLR 2 without legal comment.

```python
# emphasis_spans.py: print bold/italic text runs with PDF page numbers.
# Usage: python -I emphasis_spans.py <dir containing pypdf> <pdf> [first_page last_page]
import sys, re
sys.path.insert(0, sys.argv[1])
from pypdf import PdfReader
r = PdfReader(sys.argv[2])
a, b = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1, len(r.pages))
for pno in range(a, b + 1):
    runs = []
    def visit(text, cm, tm, font_dict, font_size):
        name = str(font_dict.get("/BaseFont", "")) if font_dict else ""
        style = ("B" if re.search(r"Bold|Black|Heavy", name, re.I) else "") + ("I" if re.search(r"Italic|Oblique", name, re.I) else "")
        if style and text.strip():
            runs.append((style, text))
    r.pages[pno - 1].extract_text(visitor_text=visit)
    merged = []
    for s, t in runs:
        if merged and merged[-1][0] == s: merged[-1][1] += t
        else: merged.append([s, t])
    for s, t in merged:
        t = " ".join(t.split())
        if t: print(f"p{pno} [{s}] {t}")
```

---

## G-2. Maharashtra enactment and commencement (BNSS s.173(3), six weeks)

| Field | Record |
|---|---|
| Question | Was Maharashtra L.C. Bill No. VI of 2026 or L.C. Bill No. XVII of 2026 enacted? Each would substitute "six weeks" for "fourteen days" in BNSS s.173(3)(i). If enacted: Act number, assent, Gazette publication date, commencement, and which text. |
| **Conclusion** | **Enactment status remains UNKNOWN.** No enacted Act was found in any official source searched. That does **not** establish that neither bill was enacted. Neither bill is to be treated as law. |

**Searches made (2026-10-21):**

| # | Source (issuing authority) | Method | Result | Status |
|---|---|---|---|---|
| 2.1 | **Maharashtra Government e-Gazette** (Directorate of Government Printing, Stationery and Publications, Government of Maharashtra), `https://egazzete.mahaonline.gov.in/Forms/GazetteSearch.aspx` (TLS verified) | Search form: Division "CENTRAL SECTION"; Section "Part 8 (English)" (where English translations of Acts are published) and "Part 4 (Marathi)"; Gazette type Extra-Ordinary and Ordinary; dates 01/01/2026 to 21/10/2026; all result pages read | Part 8 Extra-Ordinary: 126 notices (21 Jan to 6 Oct 2026). Part 4 Extra-Ordinary: 72 notices (6 Jan to 6 Oct 2026). Ordinary: 0 in both. **No Act or Ordinance amending the BNSS.** BNSS appears once, as a **bill**: "Part VIII, Ext. 81, L. C. BILL No. XVII OF 2026 … Bharatiya Nagarik Suraksha Sanhita, 2023 in its application to the State of Maharashtra. Friday 3rd July 2026." Maharashtra Act numbers up to LIV of 2026 appear. Nos. 23, 25, 31 and 47 are not named by number in the Gazette's descriptions; their texts were checked in the Bombay High Court mirror (I to LIII). The latest is **Act No. LIV of 2026, published 6 Oct 2026** (Dr. Babasaheb Ambedkar Technological University amendment, per the Gazette's own description). | **Searched, not found** (Act). Bill XVII publication **located and verified**. |
| 2.2 | Bombay High Court library mirror, `…/libweb/legislation/acts/Stateact/2026acts/2026.NN.pdf` | Fetched NN = 53 to 60 | 53: present. 54 to 60: HTTP 404. The mirror **lags the Gazette** (Act LIV, in the Gazette since 6 Oct 2026, is absent). Acts I to LIII were text-searched in an earlier round: no BNSS amendment, and no occurrence of "173". | Searched, not found |
| 2.3 | **Law and Judiciary Department, Government of Maharashtra**, `https://lj.maharashtra.gov.in/` | Site search ("Nagarik Suraksha"; "नागरिक सुरक्षा"); all pages of the "कायदा यादी" (list of laws) category (26 entries); first pages of the "अधिनियम/कायदे/नियम" and "क्रमवारी लावलेली यादी" categories | No results; no 2026 Act listed. The listings are evidently **incomplete** (26 entries in total). The legacy URL `old-lj.maharashtra.gov.in/1297/Reprints-of-the-Act` returned 404. | Searched, not found; source incomplete |
| 2.4 | **Maharashtra Legislature Secretariat**, `https://mls.org.in/`: bill pages (`Vidheyake_Assembly.aspx`, `Vidheyake_Council.aspx`) and 2026 session business reviews (`PDF2026/budjet/…` and `PDF2026/monsoon/kamkajacha-aadhava-{assembly,council}.pdf`) | Pages fetched. The four review PDFs are scanned images and were read visually. 18 constructed URLs for a "Council bills passed by the Assembly" folder were tried. | The bill pages contain no 2026 bill list. The reviews give **counts only, no titles**. Monsoon session (22 Jun to 10 Jul 2026), Assembly: 22 government bills introduced, 21 passed, 9 Council bills passed. Budget session, Assembly: 22 introduced, 22 passed, 4 Council bills passed. All 18 constructed URLs returned 404. **Whether the Assembly passed L.C. Bill VI or XVII cannot be determined from these records.** | Searched, not found (Assembly passage) |
| 2.5 | Web search (two extended queries) | Exact Act title; Assembly passage with six weeks | Only the bill (Bombay High Court bill mirror) and secondary commentary on the central provision | Searched, not found |

| Field | Record |
|---|---|
| What is established | Both bills exist and were passed by the Legislative Council (24 Mar and 8 Jul 2026, recorded in an earlier round). L.C. Bill XVII was published in the Maharashtra Gazette (Part VIII, Ext. 81, 3 Jul 2026). **No Maharashtra Act or Ordinance amending the BNSS was published in Gazette Parts IV or VIII between 1 Jan and 21 Oct 2026**, as shown by the Gazette's own search. |
| What is not established | Whether either bill passed the Assembly. Whether either was reserved for the President's assent: if so, publication may follow later, and whether a reservation is required is a QLR question (art. 254(2)). Whether commencement has been notified. |
| Remaining uncertainty | High |
| Next action; owner | **SAO**: request from the Law and Judiciary Department, or the Legislature Secretariat, a written status of L.C. Bills VI and XVII of 2026 (Assembly passage; whether assent was given or the bill reserved; Act number). Re-run search 2.1 monthly. **SC**: compare any Act text with clause 6 (Bill VI) and clause 7 (Bill XVII). **QLR**: legal effect, once the evidence exists. |

**Additional finding (not one of the six gaps; affects BNS text, RB-03):**

| Field | Record |
|---|---|
| Document | **L.A. Bill No. XXX of 2026**, "Bharatiya Nyaya Sanhita (Maharashtra Amendment) Act, 2026" (short title in clause 1). Header: "(As passed by the Legislative Assembly on the 25th March, 2026.)" and "(As passed by the Legislative Council on the 25th March, 2026.)" |
| Source | Maharashtra Legislature Secretariat, `https://mls.org.in/` + path `council-bill/2026/विधानसभेची सन २०२६ ची विधानपरिषदेने संमत केलेली विधेयके/वि. स. वि. क्र. ३०/वि. स. वि. क्र. ३०   - Engish.pdf` (TLS verified). SHA-256 `3afa7daca03b9cce5962894c6e15cb3034a755f10745293b8bc8505af31a5c16`. Gazette publication of the bill: Part VIII, Ext. No. 41, 25 Mar 2026 (search 2.1). |
| Content (bill text) | Clause 2: in BNS s.72(1), "or section 124" to be inserted after "section 71". Clause 3: in BNS s.75(1), new clauses (v) to (viii) (lascivious electronic communication; threats to upload images; using media to defame a woman; using a woman's identity to outrage modesty or violate privacy); in s.75(2), a reference to the new clauses. |
| Status | Passed by both Houses (per the document). **No Act found** in Gazette Parts IV/VIII up to 21 Oct 2026, and no 2026 Act text in the Bombay High Court mirror mentions the "Nyaya Sanhita". **Enactment status UNKNOWN; not law.** |
| Why it matters | Bandhoo's corpus contains BNS ss.72 and 75. If this becomes law in Maharashtra, the Maharashtra text would differ. This is not part of the s.173(3) review. |
| Next action; owner | **PO**: decide whether to record it under RB-03 (this log does not edit the register). **SAO**: track as for G-2. |

---

## G-3. Additional official copy of the BNSS (and BNS)

| Field | Record |
|---|---|
| Question | Is the BNSS text Bandhoo relies on (G-BNSS, a PRS-hosted file) the official Gazette text? Is there a current consolidated official text, and any central amendment or corrigendum after 25 Dec 2023? |
| **Located and verified** | **The Bharatiya Nagarik Suraksha Sanhita, 2023 (No. 46 of 2023)**, Gazette of India Extraordinary, Part II, Section 1, 25 December 2023, identifier CG-DL-E-25122023-250884. Ministry of Law and Justice (Legislative Department). Official e-Gazette: `https://egazette.gov.in/WriteReadData/2023/250884.pdf` (TLS verified; 249 pages). SHA-256 `5e60e2afe30d0fe7eca4f8126301146b76c86a444e690581f81eb564843517fe`. **Byte-identical** to the project's G-BNSS file (`bnss_gazette.pdf`, the source of the BNSS extractions used in all earlier reports). |
| **Located and verified** | **The Bharatiya Nyaya Sanhita, 2023 (No. 45 of 2023)**, identifier CG-DL-E-25122023-250883: `https://egazette.gov.in/WriteReadData/2023/250883.pdf`. SHA-256 `67c92f7869420685e6cdc29b1bdde19fff91312b10241b3ed3e1163c5399600b`. **Byte-identical** to the project's G-BNS Gazette file. That file carries the same identifier and holds the punishment terms used in the seven-year analysis. |
| Located (not an amendment) | G.S.R. 148(E), 26 Feb 2026, Ministry of Electronics and Information Technology, Gazette of India Extraordinary Part II, Section 3(i): a corrigendum to G.S.R. 846(E) of 10 Feb 2026, replacing references to the BNSS with "the Bharatiya Nyaya Sanhita, 2023 (45 of 2023) read with the Bharatiya Nagarik Suraksha Sanhita, 2023 (46 of 2023)". `https://egazette.gov.in/WriteReadData/2026/270525.pdf`, SHA-256 `f487995c6657534763a59f0795af9ec0b6e69a997110067cb2096dbd171dfdf0`. **Does not amend the BNSS.** |
| Inaccessible | India Code (`indiacode.nic.in/bitstream/123456789/20099/3/A2023-46.pdf` and the `www.` host): HTTP 504 on 2026-10-21. Handle pages: no connection (curl status 000). This is the source for a current consolidated text. |
| Searched, not found | A central "(Amendment) Act" to the BNSS or BNS: one extended web search, which returned only the 2023 Acts. **The e-Gazette's own search was not used for this** (not yet searched). |
| What it establishes | The statutory text used by Bandhoo and the dossier (BNSS s.173 and Schedule I; BNS punishment terms) is the **official Gazette text as enacted**, not merely a third-party reproduction. |
| What it does not establish | It is the same document, so it is **not an independent second copy** for detecting extraction or transcription errors; text-level checks still need the SC. It does not show the current amended text. |
| Remaining uncertainty | Medium: amendment status after 25 Dec 2023 |
| Next action; owner | **SAO**: obtain the India Code consolidated text with its "as on" date, from another network or by certified copy, and search the e-Gazette for amending Acts or corrigenda to Acts 45 and 46 of 2023. **SC**: compare s.173–175 and the Schedule rows listed in readiness §B G-3. **PO**: may decide whether the provenance finding should be reflected in `source_verification_matrix.md`. |

---

## G-4. Official *Lalita Kumari* judgment and SCC report

| Field | Record |
|---|---|
| Question | Confirm the official text, the coram, the paragraph numbering and the conclusions of *Lalita Kumari v. Govt. of U.P.*, W.P. (Crl.) No. 68 of 2008 |
| **Located and verified** | **Official Supreme Court copy of the judgment dated 12 November 2013**: `https://api.sci.gov.in/jonew/judis/40960.pdf` (TLS verified; 93 pages). SHA-256 `358a73362bb57582fcd2399bd40a5f4e60b14e6a5870383dbc67b1b7ec3a57a6`. Caption: "WRIT PETITION (CRIMINAL) NO. 68 OF 2008, Lalita Kumari … Versus Govt. of U.P. & Ors." with connected matters. Signed by P. Sathasivam CJI, Dr. B.S. Chauhan, Ranjana Prakash Desai, Ranjan Gogoi and S.A. Bobde JJ.; "NEW DELHI; NOVEMBER 12, 2013." |
| **Located and verified** | **Official report [2013] 14 S.C.R. 713**, "LALITA KUMARI v. GOVT. OF U.P. AND ORS., NOVEMBER 12, 2013", same coram: `https://cdnbbsr.s3waas.gov.in/s3ec0490f1f4972d133619a60c30f3559e/documents/aor_notice_circular/31.pdf` (TLS verified; 90 pages). SHA-256 `2dee8917c4dd55d61f6ba224d110083ae1ae074bb345ff4dd9c1c08b3c1a161c`. The S3WaaS bucket ID in this URL appears on 65 lines of the `https://www.sci.gov.in/` home page, so it is the Supreme Court website's own asset store. |
| Located (different document) | `https://api.sci.gov.in/jonew/judis/39112.pdf` (SHA-256 `ecbdd40cfa02472dd06343bd7f4ac9746a98e16acbbbe122b63e9653dcdb6933`): the **reference order of 27 February 2012** in the same case. It is not the 2013 judgment. |
| Finding 1: paragraph numbering | Both official versions number the conclusions **para 111** ("111) In view of the aforesaid discussion, we hold:" in the official copy; "111." in the S.C.R.). The "counter claims" passage is **para 110**. This is the **same** numbering as the Manupatra print (LK-MPHC). SC-IP ("Paragraph 120"; "120.2") and SC-AD ("119.") use a **different** numbering, footnoted "(2014) 2 SCC 1". The SCC report was not obtained, so it is **not verified** that 119/120 is SCC numbering. |
| Finding 2: text of direction (vii) | Both official versions read, at para 111(vii): "…a preliminary inquiry should be made time bound and in any case it should not exceed **7 days**. The fact of such delay and the causes of it must be reflected in the General Diary entry." The Manupatra print (111(vii)) and SC-IP's quotation (120.7) instead read "…should not exceed **fifteen days generally and in exceptional cases, by giving adequate reasons, six weeks** time is provided." The wording otherwise matches the Manupatra print, apart from page markers and spacing. |
| Explanation located (partly verified) | **Official, other court:** Delhi High Court, CONT.CAS(C) 582/2023, *Madhya Bharat Papers Ltd. v. …*, date of decision 11 August 2026 (`https://delhihighcourt.nic.in/app/showFileJudgment/59211082026CCP5822023_101349.pdf`; SHA-256 `55c5fbc86c8c90370104cf0c36e0224748b5af2bccffde9bd9a380bd4e81027e`). It refers to the "judgment dated 12th November, 2013, and 05th March, 2014, passed by the Supreme Court in the case of Lalita Kumari" and to an inquiry "concluded within 15 days in normal cases, and 06 weeks" in exceptional ones. **Secondary:** LiveLaw and lawweb.in (March 2014) report that a Supreme Court order modified clause (vii) of para 111 from 7 days to 15 days, or six weeks in exceptional cases. **The Supreme Court's own copy of the 5 March 2014 order was not found** (one targeted web search). |
| Inaccessible | The SCC report (2014) 2 SCC 1: subscription publication, not accessed |
| What it establishes | The official judgment text and coram. The official numbering is 110/111. The 2013 judgment as delivered said **7 days**. A later modification to 15 days / six weeks is attested by an official High Court order and by secondary reports. |
| What it does not establish | The exact wording and date of the modification order from the Supreme Court's own record. Whether the SCC report uses 119/120 and incorporates the modification. Anything about how *Lalita Kumari* applies to BNSS s.173(3) (QLR). |
| Effect on existing records (for the PO; not edited here) | Dossier §5.1 and §5.2 and handoff L-C questions cite LK-MPHC 111(vii) and SC-IP 120.7 for "fifteen days / six weeks". That wording is the **modified** direction, not the 2013 text. Dossier §5.1's working assumption that the SC numbering "probably follows the SCC report" remains unverified. **The official paragraph number is 111.** Bandhoo's code cites "(2014) 2 SCC 1" with no paragraph number, so it is unaffected. |
| Next action; owner | **SAO**: obtain the Supreme Court's order of 5 March 2014 in W.P. (Crl.) 68 of 2008 (Supreme Court judgment portal or a certified copy) and, if possible, the SCC report. **SC**: compare (vii) across the 2013 judgment, the 2014 order and the quotations. **QLR**: decide which text is cited (handoff L-C, QR-C2). |

---

## G-5. High Court (and further Supreme Court) decisions on s.173(3)

| Field | Record |
|---|---|
| Question | Has any court analysed: the seven-year boundary; per-offence or per-case application; the fourteen-day period and DSP permission; vague complaints; or the relationship with *Lalita Kumari*? |
| Searched, not found | Four extended web searches (2026-10-21), including "Bombay High Court BNSS 173(3) … seven years" and "High Court … Section 173(3) … Lalita Kumari … less than seven years". **No High Court decision on these points was identified.** Results were secondary commentary on the two Supreme Court decisions (LiveLaw, SCC Online blog of 18 Aug 2026, Lexology, KS&K, DSK Legal, IJLAE) and were not relied on. |
| Not yet searched | The official judgment search on High Court websites (including the Bombay High Court) and the eCourts judgments portal. This needs search terms defined by the QLRs. |
| **Located (relevant pending matter)** | *Azad Singh Kataria v. Union of India*, **W.P.(Crl.) No. 461/2024**, Supreme Court of India, with connected matters (W.P.(C) 625/2024; W.P.(Crl.) 444/2024, 57/2025, 40/2025, 39/2025; Diary No. 57373/2024). **Official orders (verified):** Record of Proceedings dated 03-12-2025 (CJI, Ujjal Bhuyan J., N. Kotiswar Singh J.): "List on 11.12.2025 along with all the connected matters." (`https://api.sci.gov.in/supremecourt/2024/48206/48206_2024_1_21_66571_Order_03-Dec-2025.pdf`, SHA-256 `9b0c9048e149f3ba05fc24b1de946bd8ef399a508ac2a52ca08a59151fda588f`). Record of Proceedings dated 27-02-2026 (CJI, Joymalya Bagchi J.): "List on 15.05.2026." (`https://api.sci.gov.in/supremecourt/2024/48206/48206_2024_1_31_69141_Order_27-Feb-2026.pdf`, SHA-256 `234ea6c7ad3377ed72d4d2efdeb18561d909a82f113df14c8d44f88835a0d27d`). Interim-relief and stay applications are pending (IA 16331/2025, 26124/2025, 17495/2025). **Secondary only (LiveLaw, 28 Feb 2026):** "One of the provisions under challenge was Section 173 of the BNSS." The official orders do not state which provisions are challenged. |
| What it establishes | No High Court authority was found by web search. A Supreme Court matter that (per secondary reporting) challenges BNSS s.173 was pending and listed for 15 May 2026. |
| What it does not establish | The petition's grounds; any order after 27 Feb 2026; the outcome |
| Next action; owner | **QLR 1 and QLR 2**: define the High Court search scope. **SAO**: run it on official portals, and obtain the Kataria petition, its list of challenged provisions, and any order after 27 Feb 2026 from the Supreme Court's case status. **QLR**: assess relevance to D-1 to D-3 and to the caveat wording. |

---

## G-6. Live Gemini evaluation: not run (prerequisites only)

| Field | Record |
|---|---|
| Question | How often does genuine Gemini output carry the line-59 timing wording, or describe enquiry timing without "173(3)" (RB-53 routes (a) and (b))? Does that change after any approved Change B? |
| Status | **Not generated.** No live call was made in this or earlier rounds. Cached outputs (`benchmark/cache`) and mocked outputs are **not** evidence of current behaviour. |

**Prerequisites before authorisation** (all outstanding):

| # | Prerequisite | Owner |
|---|---|---|
| 6.1 | EL appointed (template §2.5) | PO |
| 6.2 | Written **PO approval** of the evaluation, recorded with its date | PO |
| 6.3 | **Budget and quota confirmed**: maximum calls, token limits, rate limiting, model ID confirmed by an authorised operator (RB-49). The key is held outside the repository; no one reads `.env` into logs. | PO, MNT |
| 6.4 | **Test cases** fixed in advance and sealed. They should include: in-range single offences without templates (e.g. 304); seven-year offences (305, 306, 318(4)); unregistered offences (e.g. 308, 329); complaints citing and not citing "173(3)"; vague complaints; multi-offence complaints. Development and sealed sets kept separate (`reports/independent_evaluation_plan.md`). | EL, with QLR input |
| 6.5 | **Expected-output criteria** defined before the run: e.g. no "permission … within 14/fourteen days" pattern; any preliminary-enquiry statement accompanied by the statutory wording; no categorical "legally INAPPLICABLE" from missing data; seven-year handling recorded but **not scored** until D-1 is decided | EL, QLR |
| 6.6 | **Privacy checks**: synthetic narratives only; no real complainant data; no personal identifiers; outputs stored without secrets; retention rule set | EL, PO |
| 6.7 | **Separation of results**: genuine-live, cached-live, mocked and fallback outputs labelled with `inference_status` and reported separately, never merged into one metric | EL, MNT |
| 6.8 | Review: QLR 1 and QLR 2 review the flagged outputs; the results feed RB-53's closure route (ii) only | QLR |

---

## 7. Summary for the project owner

### 7.1 Gaps actually resolved or narrowed

| Gap | Result |
|---|---|
| G-3 (provenance) | **Resolved for provenance:** Bandhoo's BNSS and BNS texts are byte-identical to the official Gazette of India publications (e-Gazette 250884 and 250883). A second copy for independent text checking, and the current consolidated text, are still needed. |
| G-4 (official judgment) | **Resolved for the 2013 judgment:** the official Supreme Court copy and the official S.C.R. report were obtained. Official numbering is 110/111, and the 2013 text of (vii) says 7 days. **New issue:** the "fifteen days / six weeks" wording appears to come from a 5 March 2014 modification, attested by an official Delhi High Court order; the Supreme Court's own copy of that order is still outstanding. |
| G-2 (Gazette search) | **Narrowed:** the official Maharashtra e-Gazette was searched systematically. No BNSS amendment Act or Ordinance was published between 1 Jan and 21 Oct 2026. Status stays **UNKNOWN**: Assembly passage and assent are not shown. |
| G-1 | Procedure and tooling prepared; emphasis is recoverable from the fonts. The check itself awaits an SC. |

### 7.2 Gaps still open, and why

| Gap | Why still open |
|---|---|
| G-1 | Needs an SC independent of the dossier's author (none appointed) |
| G-2 | Assembly passage and assent are not published in any record found. A written status from the Law and Judiciary Department or the Legislature Secretariat is needed (SAO). |
| G-3 | India Code is inaccessible (HTTP 504 / no connection); the e-Gazette has not yet been searched for amending Acts (SAO, SC) |
| G-4 | The 5 March 2014 order (Supreme Court copy) and the SCC report have not been obtained (SAO) |
| G-5 | No High Court decision found by web search; the official portals need a QLR-defined search. Kataria W.P.(Crl.) 461/2024 status after 27 Feb 2026 is unknown (SAO, QLR). |
| G-6 | Requires PO authorisation, budget and an EL (§G-6) |

### 7.3 Decisions that require appointed legal reviewers

- Handoff §4.1, L-A1 to L-A3 (Change A) and L-B1 to L-B4 (Change B and RB-53).
- Handoff §4.1, L-C1 to L-C4 (D-1 to D-3, seven-year boundary). Inputs: G-1 results; G-5 search; the Kataria challenge.
- Which *Lalita Kumari* text and numbering to cite: the 2013 text (7 days), the modified direction (15 days / six weeks), para 111 or 119/120 (QR-C2, QR-C4).
- The legal effect of any Maharashtra Act, and the assent route (art. 254(2)), once G-2 evidence exists. This applies to both L.C. Bills VI and XVII (BNSS) and L.A. Bill XXX (BNS).

### 7.4 Appointments and approvals needed before any implementation

1. **PO**: record their own name and approve assignments in `reports/reviewer_assignment_template.md` Part 3. Appoint QLR 1, QLR 2, ADJ, SC, EL and SAO. Set the SAO qualification. Confirm who holds the MNT role.
2. **SC**: complete G-1 before the QLRs rely on the judgments.
3. **QLR 1 and QLR 2** (ADJ on disagreement): answer the handoff questions on the §7 forms.
4. **MNT and PO**: implementation approval per change (A, B; RB-53 route; C only after D-1 to D-3), each with its own change record and a fresh snapshot.
5. **PO**: decide whether to update `source_verification_matrix.md` / `release_blocker_register.md` with the findings in §8. This log does not edit them.
6. **PO and EL**: authorise G-6 only if RB-53 route (ii) is chosen.

## 8. Findings that affect existing records (for the PO; no file edited)

| Finding | Records affected | Suggested owner action |
|---|---|---|
| G-BNSS and G-BNS are byte-identical to the official e-Gazette originals | Matrix §1.1 (sources described as "third-party hosted"); RB-03 | PO/MNT: add a dated addendum |
| *Lalita Kumari* official numbering 110/111; 2013 text of (vii) says 7 days; 5 March 2014 modification | Dossier §5.1 and §5.2; handoff L-C; matrix RB-02 / RB-11; checklist S1-4 | PO/MNT: addendum after the SC check; QLR decides the citation |
| Maharashtra e-Gazette search: no BNSS amendment Act up to 21 Oct 2026 | Checklist S1-3; readiness G-2 | Record the search (status stays UNKNOWN) |
| L.A. Bill XXX of 2026 (BNS ss.72, 75) passed both Houses on 25 Mar 2026; no Act found | RB-03 (amendments) | PO: decide whether to register it |
| *Azad Singh Kataria*, W.P.(Crl.) 461/2024, pending; reported challenge to BNSS s.173 | RB-11; handoff L-C2 | SAO/QLR: obtain the petition and later orders |

## 9. Documents obtained this round (scratch copies; not in the repository)

| Document | SHA-256 |
|---|---|
| e-Gazette BNSS (250884) | `5e60e2afe30d0fe7eca4f8126301146b76c86a444e690581f81eb564843517fe` |
| e-Gazette BNS (250883) | `67c92f7869420685e6cdc29b1bdde19fff91312b10241b3ed3e1163c5399600b` |
| G.S.R. 148(E) (270525) | `f487995c6657534763a59f0795af9ec0b6e69a997110067cb2096dbd171dfdf0` |
| *Lalita Kumari*, official SC copy, 12 Nov 2013 (judis 40960) | `358a73362bb57582fcd2399bd40a5f4e60b14e6a5870383dbc67b1b7ec3a57a6` |
| *Lalita Kumari*, [2013] 14 S.C.R. 713 | `2dee8917c4dd55d61f6ba224d110083ae1ae074bb345ff4dd9c1c08b3c1a161c` |
| *Lalita Kumari*, reference order 27 Feb 2012 (judis 39112) | `ecbdd40cfa02472dd06343bd7f4ac9746a98e16acbbbe122b63e9653dcdb6933` |
| Delhi High Court CONT.CAS(C) 582/2023, 11 Aug 2026 | `55c5fbc86c8c90370104cf0c36e0224748b5af2bccffde9bd9a380bd4e81027e` |
| *Kataria* order, 03-12-2025 | `9b0c9048e149f3ba05fc24b1de946bd8ef399a508ac2a52ca08a59151fda588f` |
| *Kataria* order, 27-02-2026 | `234ea6c7ad3377ed72d4d2efdeb18561d909a82f113df14c8d44f88835a0d27d` |
| L.A. Bill XXX of 2026 (as passed) | `3afa7daca03b9cce5962894c6e15cb3034a755f10745293b8bc8505af31a5c16` |
| Assembly business review, Monsoon 2026 | `b954b5edfeb928d2b6859075512abe86fbb6cdab09524cfea0eec4dd2b5f317c` |
| Assembly business review, Budget 2026 | `e8d02fc5cc606d169fe2f487d031a42a9655b64bc131362830c81db0e4a75d90` |
| Council business review, Monsoon 2026 | `fcfda5e7853b138ab9c6228e3f5313a5fc379289f22f22076f37bd087e0ae2f2` |
| Council business review, Budget 2026 | `2a66d16798542dcc1f7476eef495f6c9b487a4365ad1ea1db7fc80ec9c6e2179` |

Scratch copies are temporary. The SAO should re-download from the URLs above and confirm the hashes before relying on any file.
