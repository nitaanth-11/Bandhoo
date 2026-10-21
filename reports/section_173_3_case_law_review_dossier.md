# BNSS Section 173(3): Case-Law Review Dossier

**Prepared:** 2026-10-21 by the Bandhoo maintainer session, for the qualified legal reviewers (QLR 1, QLR 2), the adjudicator (ADJ) and the project owner (PO).
**Status:** Evidence pack for qualified legal review. **This is not a legal opinion.** No blocker is closed, nothing is approved, and no code, prompt, template, corpus record, benchmark label or threshold has been changed. Bandhoo remains internal-testing-only.

Related records:
- `reports/release_blocker_register.md`: RB-02, RB-03, RB-08, RB-08.a, RB-09, RB-10, RB-11.
- `reports/approved_correction_queue.md`: Q-01 (Blocked).
- `reports/legal_review_execution_checklist.md`: S1-2, S1-3, S1-4, S1-5 and Stage 2B.
- `reports/source_verification_matrix.md` §5 and §11.
- `reports/reviewer_assignment_template.md`: no reviewer is appointed yet.

## 0. How to read this dossier

Each passage is labelled with one of these types.

| Label | Meaning |
|---|---|
| **Statute (quoted by the Court)** | Statutory text reproduced in the judgment. |
| **Earlier judgment (quoted)** | Text the Court reproduces from another judgment. It is not the Court's own reasoning. |
| **Court's reasoning** | The Court's own words, other than its conclusions or orders. |
| **Court's stated conclusion** | Text the Court itself labels as conclusions (e.g. Imran Pratapgadhi para 42). |
| **Order / disposal** | The operative direction. |

Which statements are binding ratio and which are observations is **a question for the QLR**. The labels above describe only where the text sits in the judgment.

**Quotation method.**
- Quotations are transcribed from `pypdf` text extractions of the official PDFs.
- Words that the extraction split (e.g. "infor mation", "opt ion") are rejoined. Nothing else has been changed.
- The extraction does not show bold or italics. Where the Court wrote "[Emphasis supplied]" or "(emphasis added)", that marker is reported, but the emphasised words cannot be identified from the extraction. The QLR should check emphasis in the PDF.
- Ellipses "…" mark omissions made in this dossier. Ellipses inside a quotation that appear in the judgment itself are noted.

**Page references** are PDF page numbers. In both documents they equal the printed page numbers: Imran Pratapgadhi prints "Page N of 54", and Ashish Dave prints the page number at the top of each page.

## 1. Sources and retrieval

| Code | Document | Official URL | Retrieved | Result | SHA-256 |
|---|---|---|---|---|---|
| **SC-IP** | *Imran Pratapgadhi v. State of Gujarat*, 54 pages | `https://api.sci.gov.in/supremecourt/2025/3511/3511_2025_4_1501_60508_Judgement_28-Mar-2025.pdf` | 2026-10-21 (twice, for consistency) | HTTP 200, `application/pdf`, TLS certificate verified | `896f08f97519248a7f004350d43b72ffc296144e817c0be8b0365bd28f0d5a58` (identical on both retrievals) |
| **SC-AD** | *Ashish Dave v. State of Rajasthan*, 23 pages | `https://api.sci.gov.in/supremecourt/2025/68616/68616_2025_2_34_68884_FinalOrder_27-Feb-2026.pdf` | 2026-10-21 (twice) | HTTP 200, `application/pdf`, TLS certificate verified | `3350c58215253837483fbe01397717b841f08cbb25ac2d5cbfb31edaff81bc0b` (identical on both retrievals) |
| G-BNSS | BNSS 2023 (No. 46 of 2023), Gazette of India Extraordinary, 25 Dec 2023 | PRS-hosted Gazette PDF (see matrix §1.1) | 2026-10-20 | Single copy; second full official copy **not** obtained | — |
| G-BNS | BNS 2023 (No. 45 of 2023), same Gazette date | PRS-hosted Gazette PDF | 2026-10-20 | Single copy | — |
| LK-MPHC | *Lalita Kumari v. Govt. of U.P.*, Manupatra print (MANU/SC/1166/2013) | mphc.gov.in (TLS **not** verified; see matrix §1.1) | 2026-10-20 | Third-party reproduction | — |

**Retrieval failures and gaps:**
- The **original *Lalita Kumari* judgment (W.P. (Crl.) No. 68 of 2008, decided 12.11.2013) has not been independently obtained** from the Supreme Court or from the SCC report, (2014) 2 SCC 1. See §5.
- The SCC report of *Imran Pratapgadhi*, cited by SC-AD as "(2026) 1 SCC 721", was not inspected.
- No High Court decision on BNSS s.173(3) has been sought.
- No search snippet, blog or summary was used as a source for any statement in this dossier. A blog was used only to locate the SC-IP URL; the document itself came from the official host.
- **No second-checker (SC) has verified these transcriptions.**

## 2. Statutory text available to the project

### 2.1 BNSS s.173(3), central text

G-BNSS s.173(3):

> "Without prejudice to the provisions contained in section 175, on receipt of information relating to the commission of any cognizable offence, which is made punishable for three years or more but less than seven years, the officer in charge of the police station may with the prior permission from an officer not below the rank of Deputy Superintendent of Police, considering the nature and gravity of the offence,— (i) proceed to conduct preliminary enquiry to ascertain whether there exists a prima facie case for proceeding in the matter within a period of fourteen days; or (ii) proceed with investigation when there exists a prima facie case."

**Word-by-word comparison with the two judgments (automated, then read manually):**
- SC-IP reproduces s.173(3) at PDF p.18, and SC-AD at pp.14–15.
- Both are identical to G-BNSS except that "section 175" is capitalised as "Section 175". SC-AD also has a spacing difference ("offence, —").
- Both judgments therefore reproduce, on the Supreme Court's own host, the complete s.173(3), including the "without prejudice to … Section 175" words and limb (ii).
- This is a quotation inside a judgment, not a copy of the Act. It does not satisfy checklist step S1-2 (a second authoritative copy of the BNSS). This dossier does not change S1-2.

### 2.2 The fourteen days, and the Maharashtra six-week proposal

| Item | Text | Status |
|---|---|---|
| Central BNSS text (G-BNSS; also quoted in SC-IP p.18 and SC-AD p.15) | "…within a period of fourteen days" in clause (i) | The only text available to the project; current law as far as the project's sources show |
| Maharashtra L.C. Bill No. VI of 2026, clause 6 (passed by the Legislative Council 24 Mar 2026) and L.C. Bill No. XVII of 2026, clause 7 (passed by the Legislative Council 8 Jul 2026) | Would substitute "six weeks" for "fourteen days" in s.173(3)(i) for Maharashtra | **Enactment status UNKNOWN.** No assent, Act number, Gazette publication or commencement found (checklist S1-3). **Neither bill is treated as current law.** |

Neither judgment mentions either Maharashtra bill. The six-week figure in the bills coincides with the "six weeks" in *Lalita Kumari*'s direction 120.7 (§5). This dossier draws no inference from that coincidence.

### 2.3 Punishment terms relevant to the Court's applications (G-BNS, G-BNSS Schedule I)

Used in §3.6 and §4.6. These are single-copy readings.

| BNS provision | Maximum term (G-BNS) | Schedule I row (G-BNSS) | Charged in |
|---|---|---|---|
| s.57 | "may extend to seven years and with fine" (also quoted at SC-IP p.16) | Classification follows the offence abetted (row not relied on here) | SC-IP |
| s.196(1) | "may extend to three years" (as quoted at SC-IP p.11) | — | SC-IP |
| s.197(1) | "may extend to three years" (as quoted at SC-IP p.14) | — | SC-IP |
| s.299 | "may extend to three years" | — | SC-IP |
| s.302 | "may extend to one year" | — | SC-IP |
| s.308(2) | "may extend to seven years, or with fine, or with both" | Punishment column "Imprisonment for 7 years, or fine, or both"; "Cognizable"; "Non-bailable" (column-split extraction, reassembled) | SC-AD |
| s.318(4) | "may extend to seven years, and shall also be liable to fine" | Punishment column "Imprisonment for 7 years and fine"; "Cognizable"; "Non-bailable" (column-split extraction, reassembled) | SC-AD |
| s.351(2) | "may extend to two years, or with fine, or with both" | Punishment column "Imprisonment for 2 years, …"; "Non-cognizable"; "Bailable" | SC-AD |

---

## 3. Judgment 1: *Imran Pratapgadhi v. State of Gujarat*

### 3.1 Identification

| Field | Value (as printed in SC-IP) |
|---|---|
| Title | Imran Pratapgadhi … Appellant versus State of Gujarat and Anr. … Respondents (p.1) |
| Case number | Criminal Appeal No. 1545 of 2025 (p.1), criminal appellate jurisdiction |
| Neutral citation | 2025 INSC 410 (p.1) |
| Report citation | "(2026) 1 SCC 721" is given in SC-AD footnote 8 (p.15). The SCC volume was not inspected. |
| Nature | "J U D G M E N T", marked "REPORTABLE" (p.1) |
| Bench | Abhay S. Oka, J. (author) and Ujjal Bhuyan, J. (signatures, p.54). Para 43: "Though this judgment is authored by one of us (Abhay S. Oka, J.), it is based on valuable inputs by Ujjal Bhuyan, J." |
| Date | "New Delhi; March 28, 2025" (p.54) |

### 3.2 The legal issue before the Court

- **Matter (paras 3–5, pp.2–4):**
  - An FIR was registered at Jamnagar against the appellant for "offences punishable under Sections 196, 197(1), 302, 299, 57 and 3(5)" of the BNS (para 3, p.2). It arose from a poem recited in the background of a video posted on social media (para 2).
  - The High Court rejected his petition under s.528 BNSS read with art. 226, holding that "as the investigation is at a very nascent stage, interference cannot be made" (para 5, p.4).
- **The s.173 question, as framed by the Court (para 20, p.16), Court's reasoning:** "The question is whether in the facts of the case, it was obligatory under sub-Section (1) of Section 173 of the BNSS to register FIR."
- **The other issues decided** concern the ingredients of BNS ss.196, 197, 299, 302 and 57, art. 19(1)(a) and 19(2), and the High Court's power to quash at a nascent stage (paras 13–19 and 32–41).

### 3.3 Passages on s.173(1), s.173(3) and *Lalita Kumari*

| Para | PDF page(s) | Type | Text |
|---|---|---|---|
| 20 | 16–19 | Statute (quoted) | Full text of s.173(1)–(4) (pp.16–19); s.173(3) as in §2.1. |
| 20 (after the quotation) | 19 | Court's reasoning | "If the information discloses the commission of a cognizable offence, it is mandatory to record the substance of the information in a book to be kept by the officer in the form prescribed by the State Government. No further inquiry can be made by the police officer if the information discloses the commission of a cognizable offence. Therefore, subject to the exception carved out by sub-Section (3) of Section 173, which we will deal with later, it is mandatory to record the information in a book. Thus, it is mandatory to register the FIR if information received discloses the commission of a cognizable offence." |
| 21 | 20–21 | Statute (quoted) | CrPC s.154(1)–(3). |
| 22 | 21 | Court's reasoning | "Sub-Section (1) of Section 173 of BNSS is substantially the same as Sub-Section (1) of Section 154 of the Code of Criminal Procedure, 1973 … Therefore, the law laid down by this Court in the case of Lalita Kumari v. Govt. of U.P. on Section 154 of the CrPC will be relevant. Paragraph 120 of the said decision containing conclusions/directions reads thus:" (footnote 2: "(2014) 2 SCC 1") |
| 22 | 22–24 | Earlier judgment (quoted) | *Lalita Kumari* "120. In view of the aforesaid discussion, we hold:" 120.1–120.8 (120.1–120.5 on p.22; 120.6–120.7 on p.23; 120.8 ends on p.24), followed by "(emphasis added)". Compared with LK-MPHC in §5. |
| 23 | 24–25 | Court's reasoning | "Section 154 of the CrPC does not provide for making any preliminary inquiry. However, as held in the case of Lalita Kumari, a preliminary inquiry is permissible if the information received does not disclose a cognizable offence and indicates the necessity for an inquiry. A preliminary inquiry must be conducted only to ascertain whether a cognizable offence is disclosed. However, sub-Section (3) of Section 173 of the BNSS makes a significant departure from Section 154 of the CrPC. It provides that when information relating to the commission of a cognizable offence which is made punishable for 3 years or more but less than 7 years is received by an officer-in-charge of a police station, with the prior permission of a superior officer as mentioned therein, the police officer is empowered to conduct a preliminary inquiry to ascertain whether there exists a prima facie case for proceeding in the matter. However, under Section 154 of the CrPC, as held in the case of Lalita Kumari, only a limited preliminary inquiry is permissible to ascertain whether the information received discloses a cognizable offence. Moreover, a preliminary inquiry can be made under the CrPC only if the information does not disclose the commission of a cognizable offence but indicates the necessity for an inquiry. Sub-Section (3) of Section 173 of the BNSS is an exception to sub-Section (1) of Section 173. In the category of cases covered by sub-Section (3), a police officer is empowered to make a preliminary inquiry to ascertain whether a prima facie case is made out for proceeding in the matter even if the information received discloses commission of any cognizable offence. That is very apparent as sub-Section (3) of Section 173 refers explicitly to receiving information relating to the commission of a cognizable offence. Therefore, in a case where sub-Section (3) of Section 173 is applicable, even if the information pertaining to the commission of any cognizable offence is received, an inquiry can be conducted to ascertain whether a prima facie case exists for proceeding in the matter. The intention appears to be to prevent the registration of FIRs in frivolous cases where punishment is up to 7 years, even if the information discloses the commission of the cognizable offence. However, under Section 154 of the CrPC, the inquiry permitted by paragraph 120.2 of the decision in the case of Lalita Kumari is limited only to ascertain whether the cognizable offence is disclosed." |
| 24 | 25–26 | Court's reasoning | "Under sub-Section (3) of Section 173 of the BNSS, after holding a preliminary inquiry, if the officer comes to a conclusion that a prima facie case exists to proceed, he should immediately register an FIR and proceed to investigate. But, if he is of the view that a prima facie case is not made out to proceed, he should immediately inform the first informant/complainant so that he can avail a remedy under sub-Section (4) of Section 173." |
| 25 | 26 | Court's reasoning | Example: simple hurt (BNS 115(2), non-cognizable, "FIR cannot be registered") compared with grievous hurt (117(2), cognizable). "Taking the information as correct, the officer has to determine whether it makes out a case of the commission of a cognizable offence. If the allegation makes out a case of a cognizable offence, unless the offence falls in sub-Section (3) of Section 173, it is mandatory to register FIR." |
| 26–27 | 27–28 | Court's reasoning | For speech offences, reading or hearing the words to decide whether a cognizable offence is made out "will not amount to making a preliminary inquiry which is not permissible under sub-Section (1) of Section 173" (para 26, p.27). Para 27 (pp.27–28): "This exercise does not amount to making a preliminary inquiry which is prohibited under sub-Section (1) of Section 173 of BNSS." |
| 28 | 28 | Court's reasoning | "Sub-Section (3) of Section 173 of the BNSS confers a discretion on the officer receiving information relating to the commission of a cognizable offence to conduct a preliminary inquiry to ascertain whether a prima facie case exists to proceed. This option is available when the offence alleged is made punishable for 3 years or more but less than 7 years. In the facts of the case, all the offences except the offence under Section 57 of the BNS are punishable by imprisonment for less than 7 years. Section 57, on the face of it, is not applicable. Therefore, this option was also available to the police officer in the present case. The officer did not exercise the said option." |
| 29 | 30–31 | Court's reasoning | "…when an allegation is of the commission of an offence covered by the law referred to in clause (2) of Article 19, if sub-Section (3) of Section 173 is applicable, it is always appropriate to conduct a preliminary inquiry to ascertain whether a prima facie case is made out to proceed against the accused. … Therefore, in such cases, the higher police officer referred to in sub-Section (3) of Section 173 must normally grant permission to the police officer to conduct a preliminary inquiry. Therefore, when the commission of cognizable offences is alleged, where punishment is for imprisonment up to 7 years, which is based on spoken or written words, it will always be appropriate to exercise the option under sub-Section (3) of Section 173 and conduct a preliminary inquiry … If, in such cases, the option under sub-Section (3) of Section 173 is not exercised, it will defeat the very object of incorporating sub-Section (3) of Section 173 of the BNSS and will also defeat the obligation of the police under Article 51-A (a)." |
| 31 | 31 | Court's reasoning (finding) | "In the facts of the case, even without taking recourse to sub-Section (3) of Section 173 of the BNSS, the information furnished to the police officer did not attract the offences punishable under Sections 196, 197, 299 and 302 of the BNS." |
| 36 | 41–42 | Court's reasoning (finding) | "…no prima facie case can be said to have been made out against the appellant qua the sections invoked. In such a case, registration of the FIR appears to be a very mechanical exercise and is a clear abuse of the process of law." |
| 42(i) | 47–48 | Court's stated conclusion | Repeats para 23 from "Sub-Section (3) of Section 173 of the BNSS makes a significant departure…" to "…even if the information received discloses commission of any cognizable offence." |
| 42(ii) | 48–49 | Court's stated conclusion | Repeats para 24. |
| 42(iii) | 49 | Court's stated conclusion | Repeats the para 26 reasoning: reading or hearing the words "will not amount to making a preliminary inquiry which is not permissible under sub-Section (1) of Section 173." |
| 42(v) | 50–51 | Court's stated conclusion | Repeats para 29 on art. 19(2) offences: "…if sub-Section (3) of Section 173 is applicable, it is always appropriate to conduct a preliminary inquiry … the higher police officer referred to in sub-Section (3) of Section 173 must normally grant permission to the police officer to conduct a preliminary inquiry." |
| 44 | 54 | Order / disposal | "…the impugned order deserves to be set aside. We, accordingly, quash and set aside the impugned order. We also quash and set aside FIR No. 11202008250014 of 2025, registered with City A-Division Police Station, Jamnagar, and further proceedings based thereon. The Appeal is accordingly allowed." |

### 3.4 What the Court decided (described, not characterised as ratio)

1. **Order (para 44):** the High Court's order was set aside; the FIR and the proceedings were quashed; the appeal was allowed.
2. **Findings on which the order rests:** the information did not attract ss.196, 197, 299 or 302 (para 31); s.57 was "on the face of it, … not applicable" (paras 19, 28); no prima facie case was made out, and registration was "a clear abuse of the process of law" (para 36).
3. **The Court states in para 31 that its finding did not depend on s.173(3)** ("even without taking recourse to sub-Section (3) of Section 173").
4. **Propositions on s.173 that the Court lists among its conclusions** (para 42(i)–(iii), (v)):
   - 173(3) is "an exception to" 173(1);
   - within its category, a preliminary inquiry may be made "even if the information received discloses commission of any cognizable offence";
   - post-inquiry steps: immediately register an FIR, or immediately inform the informant so that 173(4) can be used;
   - reading the words is not a prohibited inquiry under 173(1);
   - for art. 19(2)-type speech offences, the higher officer "must normally grant permission".
5. Whether the propositions in item 4 are binding on later benches is **for the QLR**. This is relevant because of item 3.

### 3.5 Limits on what SC-IP decided (as far as the text shows)

- **Context:** offences based on spoken or written words, and art. 19(1)(a) and 19(2). The "always appropriate" and "must normally grant permission" statements (paras 29, 42(v)) are expressly limited to "an offence covered by the law referred to in clause (2) of Article 19".
- **The fourteen-day period** in 173(3)(i) is **not discussed** anywhere. It appears only in the quoted statute (p.18). The judgment says nothing about when the period starts, how it relates to DSP permission, or what follows if it is exceeded.
- **The DSP permission process** is discussed only in para 29 and para 42(v), in the art. 19(2) context ("must normally grant permission"). Who applies, when, and in what form are not discussed.
- **The "without prejudice to … Section 175" words** are quoted (p.18) but not discussed.
- **The range boundaries** are not analysed. Para 28 applies the range to the charged offences: "all the offences except the offence under Section 57 … are punishable by imprisonment for less than 7 years".
  - s.57 carries "may extend to seven years" (quoted by the Court, p.16).
  - Para 28 therefore treats a seven-year-maximum offence as not "less than 7 years". This is an application, not a stated rule.
  - Para 23 describes the purpose as frivolous cases "where punishment is up to 7 years", and para 29 says "where punishment is for imprisonment up to 7 years". How these phrases relate to "less than seven years" is not discussed.
  - The three-year floor is not discussed. s.302 (up to one year) is included in "all the offences except … Section 57" without separate comment.
- **Multi-offence complaints** and s.174(4) are not discussed.
- **The officer "did not exercise the said option"** (para 28). The judgment therefore did not review how a 173(3) inquiry was actually conducted.

### 3.6 Relationship to the topics in this dossier

| Topic | What SC-IP says | Location |
|---|---|---|
| Preliminary-enquiry period (14 days) | Statutory quotation only; no discussion | p.18 |
| DSP permission | "with the prior permission of a superior officer as mentioned therein" (paraphrase); "must normally grant permission" for art. 19(2) offences | paras 23, 29, 42(i), 42(v) |
| Cognizability | 173(3) applies to information "relating to the commission of a cognizable offence"; reading the words to decide cognizability is not an inquiry | paras 23, 25–27, 42(iii) |
| FIR registration | Mandatory under 173(1) if a cognizable offence is disclosed, "unless the offence falls in sub-Section (3)"; after an inquiry, register immediately or inform the informant | paras 20, 24, 25, 42(ii) |
| *Lalita Kumari* | "will be relevant" to 173(1) (para 22); its para 120.2 inquiry is limited to whether a cognizable offence is disclosed, whereas 173(3) is "a significant departure" | paras 22, 23 |

---

## 4. Judgment 2: *Ashish Dave v. State of Rajasthan*

### 4.1 Identification

| Field | Value (as printed in SC-AD) |
|---|---|
| Title | Ashish Dave … Appellant(s) versus The State of Rajasthan and Another … Respondent(s) (p.1) |
| Case number | "CRIMINAL APPEAL NO(S). [blank] OF 2026 (Arising out of SLP(Crl.) No(s). 19369 of 2025)" (p.1). **The appeal number is blank in the PDF**; it was not identified from any other source. |
| Neutral citation | 2026 INSC 244 (p.1) |
| Report citation | None shown in the document; not identified |
| Nature | "O R D E R", marked "REPORTABLE" (p.1). It is an **order**, not titled a judgment. |
| Bench | Mehta, J. wrote the order (p.1); signed by Vikram Nath, J. and Sandeep Mehta, J. (p.23) |
| Date | "NEW DELHI; FEBRUARY 27, 2026." (p.23) |

### 4.2 The legal issue before the Court

- **The FIR (para 4, pp.1–2):** FIR No. 257 of 2025 dated 4 September 2025, Police Station Ashok Nagar, Jaipur City (South), registered on a complaint by the appellant's former employer (a media company), "for the offences punishable under Sections 308(2), 318(4) and 351(2)" of the BNS.
- **The High Court:** the Rajasthan High Court dismissed the s.528 BNSS quashing petition on 26 November 2025 (paras 9, 11, 14–15, pp.5–8).
- **The question decided:** whether the FIR should be quashed. The Court's analysis concerns the vagueness of the complaint (paras 6–8, 13–21), the police's failure to verify or to hold a preliminary inquiry (paras 8, 22–25), and the *Bhajan Lal* categories (para 27).

### 4.3 Passages on s.173(1), s.173(3) and *Lalita Kumari*

| Para | PDF page(s) | Type | Text |
|---|---|---|---|
| 8 | 5 | Court's reasoning | "…the officials of Police Station Ashok Nagar, Jaipur City (South), acting with unusual expediency, accepted the said complaint and, without even making a bare attempt to verify the allegations made therein by semblance of a preliminary enquiry, straightaway proceeded to register the FIR for grave offences." |
| 22 | 11 | Court's reasoning | "In the given facts, the least that was expected from the police officials was to either require the complainant-company to furnish supporting material and details to prima facie make out the allegations made in the FIR, or else to hold a preliminary inquiry before registering the formal FIR. This conclusion finds support from the following observations made by this Court in Lalita Kumari v. Govt. of U.P.:" (footnote 7, p.11: "(2014) 2 SCC 1.") |
| 22 | 11–12 | Earlier judgment (quoted) | "119. Therefore, in view of various counterclaims regarding registration or non-registration, what is necessary is only that the information given to the police must disclose the commission of a cognizable offence. In such a situation, registration of an FIR is mandatory. However, if no cognizable offence is made out in the information given, then the FIR need not be registered immediately and perhaps the police can conduct a sort of preliminary verification or inquiry for the limited purpose of ascertaining as to whether a cognizable offence has been committed….", followed by "[Emphasis supplied]". **The quotation ends with an ellipsis in the original order.** See §5 for the omitted words. |
| 23 | 12 | Court's reasoning | "The new regime under the BNSS specifically deals with such situations and provides an additional safeguard where the complaint is for offences carrying punishment between three to seven years. Sub-section (3) of Section 173 BNSS empowers the officer in charge of a police station, with prior permission of a superior officer, to conduct a preliminary inquiry to ascertain whether there exists a prima facie case for proceeding in the matter where the alleged offence is punishable with imprisonment for a term between three and seven years." |
| 23 | 12–15 | Statute (quoted) | s.173(1)–(4) in full; s.173(3) on pp.14–15 as in §2.1; "[Emphasis supplied]". |
| 24 | 15–19 | Earlier judgment (quoted) | "This provision was considered by this Court in Imran Pratapgadhi v. State of Gujarat [fn 8: "(2026) 1 SCC 721."], wherein the scope of Section 173 BNSS has been explained as follows:" It then quotes SC-IP paras 23, 24 and 25 (with "[……]" marking an omission after para 25) and para 28, followed by "[Emphasis supplied]". The quoted text matches SC-IP §3.3, apart from extraction spacing. |
| 24 (after the quotation) | 19–20 | Court's reasoning | "The crux of the above observations, therefore, is that under the regime of Section 154 of the CrPC, as explained in Lalita Kumari (supra), a preliminary inquiry is permissible only for the limited purpose of ascertaining whether the information discloses the commission of a cognizable offence. However, the scheme of Section 173(3) of the BNSS travels a step further and exposits situations where preliminary inquiry may be made even where the complaint is filed for cognizable offences. The said provision empowers the police officer, even in a case where the information may ostensibly disclose the commission of a cognizable offence punishable between three and seven years, to conduct a preliminary inquiry so as to ascertain whether there exists a prima facie case for proceeding in the matter. Thus, the legislative intent behind incorporating sub-section (3) of Section 173 appears to be to provide a safeguard against mechanical registration of FIRs in cases where the allegations, though couched in the language of a cognizable offence, may in substance be vague, speculative or inherently doubtful." |
| 25 | 20–21 | Court's reasoning (application) | "None of the offences alleged in the impugned FIR carries imprisonment which may extend to more than seven years, thereby bringing the case within the category where the option of conducting a preliminary enquiry under Section 173(3) of the BNSS was clearly available to the police authorities. However, the police officials did not choose to exercise this option, and the FIR came to be registered straightaway in a mechanical manner … In the given facts, where the complaint contained vague allegations and was completely bereft of particulars, the situation clearly warranted a preliminary enquiry so as to arrive at the necessary "prima facie" satisfaction as to the commission of a cognizable offence. Though there is no hard and fast criterion for determining when such prima facie satisfaction may arise, the very object of permitting a preliminary enquiry is to prevent initiation of criminal proceedings on the basis of frivolous or speculative allegations. The allegations contained in the complaint being so indeterminate and lacking in basic particulars, we are of the opinion that the police authorities ought to have exercised the option available under Section 173(3) of the BNSS." |
| 27 | 21–22 | Court's reasoning; earlier judgment (quoted) | "…the case of the appellant is covered by the observations made by this Court in Bhajan Lal (supra) in paras 102(1), (2) & (5)…" (fn 9: "1992 Supp (1) SCC 335."), followed by the quoted categories. |
| 28–30 | 23 | Court's reasoning; order | Para 28: "…allowing the continuance of investigation pursuant to the impugned FIR against the appellant is nothing short of a gross abuse of the process of law." Para 29: "…the impugned order dated 26th November, 2025 passed by the High Court is set aside. As a consequence, FIR No.257 of 2025 dated 4th September, 2025 … and all proceedings sought to be taken against the appellant in pursuance thereof, are quashed." Para 30: "The appeal stands allowed accordingly." |

### 4.4 What the Court decided (described, not characterised as ratio)

1. **Order (paras 29–30):** the High Court's order was set aside, the FIR and all proceedings were quashed, and the appeal was allowed.
2. **Basis stated for the order:**
   - the complaint "ex facie, discloses no material whatsoever warranting registration of a First Information Report" (para 13, p.7);
   - the allegations are "so absurd, vague and inherently improbable" (para 19, pp.9–10);
   - the case is covered by *Bhajan Lal* categories (1), (2) and (5) (para 27);
   - continuing the investigation is "a gross abuse of the process of law" (para 28).
3. **Statement on s.173(3) applied to the facts (para 25):** the case was "within the category where the option … was clearly available", the situation "clearly warranted a preliminary enquiry", and the police "ought to have exercised the option".
4. **Synthesis of the earlier law (para 24, "The crux…"):** 173(3) "travels a step further" than *Lalita Kumari*'s CrPC position, and its purpose is "a safeguard against mechanical registration of FIRs".
5. Whether item 3 is part of the reason for the order (item 2), or a supporting observation, is **for the QLR**.

### 4.5 Limits on what SC-AD decided (as far as the text shows)

- **It is an order of a two-judge bench**, decided on particular facts: a vague corporate complaint against a former employee.
- **The fourteen-day period** is **not discussed**. It appears only in the quoted statute (p.15).
- **The DSP permission process** is not discussed beyond the paraphrase "with prior permission of a superior officer" (para 23).
- **"Without prejudice to … Section 175"** is quoted but not discussed.
- **The range is paraphrased** as "between three to seven years" and "between three and seven years" (para 23, p.12), and in para 24 as "punishable between three and seven years".
  - Para 25's test is that no offence "carries imprisonment which may extend to more than seven years".
  - In G-BNS, BNS 308(2) and 318(4), both charged here, carry a maximum of exactly seven years (§2.3). The statute's words are "less than seven years".
  - **The Court did not discuss this boundary.** This dossier does not decide what para 25 implies for it.
- **One charged offence, 351(2), is non-cognizable** in G-BNSS Schedule I. SC-AD does not discuss how 173(3) operates when the charged offences have different classifications.
- **Consequence of not holding an enquiry:** the order does not say that failure to hold a 173(3) enquiry invalidates an FIR in general. The FIR was quashed on the *Bhajan Lal* grounds and as an abuse of process (paras 27–28).

### 4.6 Relationship to the topics in this dossier

| Topic | What SC-AD says | Location |
|---|---|---|
| Preliminary-enquiry period (14 days) | Statutory quotation only | p.15 |
| DSP permission | Paraphrase only: "with prior permission of a superior officer" | para 23 |
| Cognizability | 173(3) applies "even where the complaint is filed for cognizable offences" | para 24 (after the quotation) |
| FIR registration | Criticises registration "straightaway in a mechanical manner"; police "ought to have exercised the option available under Section 173(3)" | paras 8, 25 |
| *Lalita Kumari* | Quotes para "119" in support of requiring details or a preliminary inquiry; "under the regime of Section 154 … a preliminary inquiry is permissible only for the limited purpose…" | paras 22, 24 |

---

## 5. *Lalita Kumari*: status, numbering and limits

**Status:** the original Supreme Court judgment (W.P. (Crl.) No. 68 of 2008, decided 12.11.2013) **has not been independently obtained** from the Supreme Court or from the SCC report, (2014) 2 SCC 1.
- The project has the Manupatra print (LK-MPHC), whose host's TLS certificate could not be verified.
- It also has the quotations in SC-IP and SC-AD.
- Both judgments footnote the case as "(2014) 2 SCC 1".
- LK-MPHC lists a five-judge coram (P. Sathasivam, C.J.I., B.S. Chauhan, Ranjana Prakash Desai, Ranjan Gogoi and S.A. Bobde, JJ.). This has not been confirmed from an official copy.

### 5.1 Paragraph numbering

The two Supreme Court judgments number the paragraphs differently from LK-MPHC. The offset is consistently nine.

| Supreme Court quotation | Where quoted | LK-MPHC equivalent | LK-MPHC page | Comparison |
|---|---|---|---|---|
| "119. Therefore, in view of various counterclaims…" | SC-AD para 22, pp.11–12 | Para 110 ("counter claims") | p.39 | The quoted words match. **SC-AD ends its quotation with "…."** The LK-MPHC para 110 continues: "But, if the information given clearly mentions the commission of a cognizable offence, there is no other option but to register an FIR forthwith. Other considerations are not relevant at the stage of registration of FIR, such as, whether the information is falsely given, whether the information is genuine, whether the information is credible etc." |
| "120. In view of the aforesaid discussion, we hold:" 120.1–120.8 | SC-IP para 22, pp.22–24 | Para 111, (i)–(viii) | p.39 onward | Automated word comparison and manual reading: identical apart from numbering, an initial "The" in 120.1 ("The registration of FIR is mandatory…" against "Registration of FIR is mandatory…"), and hyphenation ("time-bound"). |
| "paragraph 120.2" | SC-IP para 23, p.25; SC-AD para 24 (quoting SC-IP), p.17 | Para 111(ii) | p.39 | — |

**Points to note:**
- The numbering used by the Supreme Court probably follows the SCC report, but this **has not been verified**.
- Bandhoo's code (`legal_engine/schedule_registry.py`, lines 37–42 and 58–61) cites "(2014) 2 SCC 1" without a paragraph number. Earlier project reports refer to "para 111" and "para 111(vii)". These are **LK-MPHC numbers**.
- Any reviewer citation should state which numbering it uses.

### 5.2 *Lalita Kumari* text relevant to timing

The directions quoted in SC-IP include 120.7 (p.23): "While ensuring and protecting the rights of the accused and the complainant, a preliminary inquiry should be made time-bound and in any case it should not exceed fifteen days generally and in exceptional cases, by giving adequate reasons, six weeks' time is provided. The fact of such delay and the causes of it must be reflected in the General Diary entry."

Neither SC-IP nor SC-AD discusses 120.7, or how it relates to the "fourteen days" in BNSS 173(3)(i).

### 5.3 What the later judgments do not resolve

These judgments must not be read as resolving every BNSS question that involves *Lalita Kumari*. Specifically, neither judgment:
- discusses whether *Lalita Kumari*'s time limits (120.7), categories (120.6) or diary requirements (120.8) apply to a s.173(3) enquiry;
- discusses whether 120.3 (supply of the closure entry to the informant within one week) applies to a 173(3) enquiry. SC-IP para 24 states a duty to "immediately inform" the informant, without reference to 120.3;
- addresses the s.173(3)/s.175 relationship.

Further:
- *Lalita Kumari* was decided by a five-judge bench on CrPC s.154 (per LK-MPHC). SC-IP and SC-AD are two-judge decisions on the BNSS. How these interact as precedent is for the QLR.

---

## 6. Bandhoo impact analysis

Read-only inspection on 2026-10-21. File and line references are to the current working tree, whose hashes match `release_blocker_register.md` Appendix B.

### 6.1 Where Bandhoo states s.173(3) advice

| Component | Location | Reaches users? |
|---|---|---|
| Gemini system prompt | `legal_engine/llm_client.py` `SYSTEM_PROMPT` (starts line 33), lines 56–64 | Indirectly. Gemini's recommendation text is passed to users for single non-templated offences (`legal_engine/service.py` lines 758–788; RB-08.a). |
| Statutory paraphrase | `legal_engine/schedule_registry.py` `BNSS_173_3_PROCEDURE_TEXT`, lines 28–35 | Yes, appended to procedural advice |
| Caveat | `schedule_registry.py` `BNSS_173_3_CAVEAT_TEXT`, lines 37–42 | Yes |
| Range reading note | `schedule_registry.py` `BNSS_173_3_RANGE_READING_NOTE`, lines 44–48; `OPEN_LEGAL_QUESTIONS`, lines 51–67 | Recorded as an open question |
| Eligibility logic | `schedule_registry.py` `_row_173_3_status`, lines 336–360; `check_bnss_173_3_eligibility`, from line 363 | Yes, through the service |
| Procedural templates | `service.py`: vague-complaint branch (lines 546–560); 173(3) claim audit and corrections (lines 726–736, 760–788); offence-specific notes (e.g. lines 588–590, 636–641, 659–675) | Yes |

### 6.2 Comparison table

| Topic | 1. Gemini prompt | 2. Deterministic logic | 3. Statutory text (G-BNSS; same in SC-IP p.18, SC-AD p.15) | 4. What SC-IP / SC-AD decided or said | 5. Open for QLR |
|---|---|---|---|---|---|
| **A. Fourteen days and DSP permission** | Line 59: "It is discretionary with prior permission from an officer not below the rank of Deputy Superintendent of Police (DSP) **within 14 days**, or police proceed directly with investigation when a prima facie case exists." | `BNSS_173_3_PROCEDURE_TEXT` (lines 28–35): "…with the prior permission of an officer not below the rank of Deputy Superintendent of Police … either (i) conduct a preliminary enquiry to ascertain whether a prima facie case exists, within a period of fourteen days, or (ii) proceed with investigation…" | Clause (i): "…preliminary enquiry to ascertain whether there exists a prima facie case for proceeding in the matter within a period of fourteen days" | **Neither judgment discusses the period.** Both only quote the statute. SC-IP paraphrases permission as "with the prior permission of a superior officer as mentioned therein" (para 23). | What the period governs and when it starts; whether the prompt's wording is materially misleading (QR-B1–B3, QR-E1) |
| **B. "Discretion" characterisation** | Line 59: "It is discretionary…" | Caveat (line 38): "This is a discretion available to the police, not a requirement" | "…may with the prior permission…" | SC-IP para 28: "confers a discretion on the officer". SC-IP para 29 and 42(v): for art. 19(2) speech offences it is "always appropriate" to hold an inquiry, and permission "must normally" be granted. SC-AD para 25: on vague complaints, the police "ought to have exercised the option". | Whether "discretion … not a requirement" is still adequate without mention of these statements (QR-A3, QR-D4) |
| **C. Seven-year boundary** | Line 58: "…three years or more but less than seven years." Line 63: "NEVER recommend Section 173(3) for offences punishable with 7 years or more…" | Maximum-term reading. A seven-year maximum is **outside** (lines 340–344, "interpretation pending qualified legal review"). Correction text at `service.py` 773–783 calls 173(3) "legally INAPPLICABLE" where the maximum is seven years or more. BNS 318(4) is held at max 7.0 (registry line 220). | "…made punishable for three years or more but less than seven years" | SC-IP para 28 treats BNS 57 (max seven years) as outside "less than 7 years" (application). SC-AD para 25 treats an FIR under BNS 308(2) and 318(4) (each max seven years in G-BNS) as within the category, because none "carries imprisonment which may extend to more than seven years". **Neither judgment analyses the boundary.** The applications appear to differ. | RB-09. QR-D1, QR-D2. |
| **D. Three-year floor** | Line 62: "NEVER recommend … less than 3 years" | Exactly three years is **inside** (lines 350–358) | "three years or more" | SC-IP para 28 does not separately address s.302 (max one year). No analysis in either. | RB-09 (QR-D2) |
| **E. Relationship with 173(1) / mandatory registration** | Line 56: no unconditional 173(1) FIR recommendation when cognizability facts are unverified. Line 63: seven-plus offences go to "173(1) BNSS for direct FIR registration". | Caveat (lines 38–41): the interaction with 173(1) and *Lalita Kumari* "is the subject of differing judicial and academic views and is not determined by this assessment" | 173(1) quoted in both judgments | SC-IP paras 20, 25: registration is mandatory if a cognizable offence is disclosed, "unless the offence falls in sub-Section (3)"; 173(3) is "an exception to sub-Section (1)" (paras 23, 42(i)). SC-AD para 24 adopts this. | Whether the caveat's "differing judicial and academic views" is still accurate (QR-C3) |
| **F. *Lalita Kumari*** | Not mentioned in the prompt | Caveat cites "(2014) 2 SCC 1 (mandatory registration of an FIR where information discloses a cognizable offence)" | — | SC-IP para 22: *Lalita Kumari* "will be relevant" to 173(1). Para 23: 173(3) "makes a significant departure". SC-AD para 24: 173(3) "travels a step further". | QR-C1–C4 |
| **G. Vague complaints** | Line 60: "NEVER recommend Section 173(3) for vague or ambiguous complaints where no penal offence is established; request factual clarification from the complainant instead." | `service.py` 526–527 (docstring): vague complaints "never warrant a preliminary enquiry under Section 173(3)". Line 557: "Preliminary enquiry under Section 173(3) BNSS is legally inapplicable to vague complaints lacking prima facie allegations of a cognizable offence". This branch runs only when no offence is predicted (line 547). | — | SC-AD para 22: the police should "either require the complainant-company to furnish supporting material and details … or else to hold a preliminary inquiry". Para 25: a vague complaint naming BNS offences "clearly warranted a preliminary enquiry". | Whether Bandhoo's vague-complaint wording conflicts with SC-AD, or deals with a different situation (no offence identified at all) (QR-D3) |
| **H. After the enquiry** | Not mentioned | Not mentioned (no reference to 173(4) or to informing the informant) | 173(4) quoted in both | SC-IP para 24, 42(ii): register an FIR immediately, or inform the informant immediately so that the 173(4) remedy can be used | Whether citizen advice should mention this (QR-A4) |
| **I. "Without prejudice to … section 175"** | Not mentioned | Not reproduced (matrix RB-08) | Present | Quoted, not discussed | RB-08 (QR-D5) |
| **J. Maharashtra** | Fourteen days, no jurisdiction note | Fourteen days, no jurisdiction note | Central text: fourteen days | Not mentioned | Status UNKNOWN (§2.2). No change while unknown (QR-B4). |

### 6.3 Observations for reviewers (not determinations)

1. **The prompt's timing wording (row A) is not addressed by either judgment.** The comparison is between the prompt and the statutory text only. This is RB-08.a, already classed as a transcription discrepancy. The case law neither supports nor undermines it.
2. **The deterministic seven-year reading (row C) is touched by both judgments in opposite-looking ways, and analysed by neither.** RB-09 already lists 318(4) as affected. Bandhoo's code states its reading is "pending qualified legal review", while the correction text at `service.py` line 782 states "legally INAPPLICABLE". Whether that wording is too strong is a QLR question, not a finding here.
3. **The caveat (row E/F)** says the 173(1)/173(3)/*Lalita Kumari* interaction is "the subject of differing judicial and academic views". Two reportable Supreme Court decisions now state a position on part of that interaction. Whether the caveat should change is for the QLR. This dossier does not change it.
4. **The vague-complaint wording (row G)** may concern a different situation from SC-AD: Bandhoo's branch runs only when no offence is identified, whereas SC-AD's complaint named specific offences. The QLR should decide whether "legally inapplicable" is accurate or should be qualified.
5. **Fourteen days compared with six weeks:** every Bandhoo statement says fourteen days, which matches the central text the project holds. The Maharashtra six-week change is a bill of **UNKNOWN** status. Nothing here supports changing Bandhoo's period, and Q-01 Step 2 remains blocked.

---

## 7. Questions for qualified Indian criminal-law reviewers

Each question has a blank answer field. The questions should be answered in `reports/legal_review_execution_checklist.md` Stage 2B, under the change protocol. This dossier records no answers.

### A. What the two judgments establish about s.173(3)

| ID | Question | Passages | Answer (QLR 1 / QLR 2 / ADJ) |
|---|---|---|---|
| QR-A1 | Which statements in SC-IP paras 23–25, 28–29 and 42(i)–(iii), (v) are binding propositions on s.173(3), given para 31 ("even without taking recourse to sub-Section (3)…")? | §3.3, §3.4 | ____ |
| QR-A2 | Is SC-AD para 25 ("ought to have exercised the option available under Section 173(3)") part of the reason for the order, or an observation alongside the *Bhajan Lal* basis (paras 27–28)? | §4.3, §4.4 | ____ |
| QR-A3 | Do SC-IP para 29 / 42(v) (speech offences: "always appropriate"; permission "must normally" be granted) and SC-AD para 25 (vague complaints) change how the "discretion" in 173(3) should be described to citizens? | §3.3, §4.3; row B | ____ |
| QR-A4 | Should Bandhoo's advice mention the post-enquiry steps in SC-IP para 24 / 42(ii) (immediate FIR, or immediate information to the informant for the 173(4) remedy)? | §3.3; row H | ____ |
| QR-A5 | Are there other Supreme Court or Bombay High Court decisions on 173(3) that must be considered before answering? (S1-5: High Court decisions not yet sought.) | §1 | ____ |

### B. Preliminary-enquiry timing and DSP permission

| ID | Question | Passages | Answer |
|---|---|---|---|
| QR-B1 | On the text of 173(3), does "within a period of fourteen days" govern the preliminary enquiry under clause (i), the grant of DSP permission, or something else? | §2.1 | ____ |
| QR-B2 | When does the fourteen-day period begin (receipt of information, grant of permission, start of the enquiry), and what follows if it is exceeded? Is any of this settled by authority? Neither SC-IP nor SC-AD discusses it. | §3.5, §4.5 | ____ |
| QR-B3 | Is any time limit for seeking or granting DSP permission stated in the BNSS or in any authority known to the reviewer? | — | ____ |
| QR-B4 | Until the Maharashtra amendment's status is established (UNKNOWN), should Bandhoo's statements of "fourteen days" carry any jurisdictional caveat, or remain unqualified? (No change is proposed while the status is unknown.) | §2.2 | ____ |

### C. *Lalita Kumari* under the BNSS

| ID | Question | Passages | Answer |
|---|---|---|---|
| QR-C1 | After SC-IP para 22 ("will be relevant") and paras 23 / 42(i) ("significant departure"; "exception to sub-Section (1)"), which parts of *Lalita Kumari* apply to information under BNSS 173(1)? Which apply to an enquiry under 173(3)? | §3.3, §5 | ____ |
| QR-C2 | Do *Lalita Kumari*'s 120.6 categories, 120.7 time limits (fifteen days / six weeks) and 120.8 diary requirement apply to a 173(3) enquiry? Neither later judgment addresses this. | §5.2, §5.3 | ____ |
| QR-C3 | Is Bandhoo's caveat ("…is the subject of differing judicial and academic views and is not determined by this assessment") still an accurate description after SC-IP and SC-AD? | Row E/F | ____ |
| QR-C4 | Is Bandhoo's one-line summary of *Lalita Kumari* ("mandatory registration of an FIR where information discloses a cognizable offence") accurate and sufficient? Which paragraph numbering should be cited (SCC 119/120, or the LK-MPHC 110/111)? Requires the official or SCC copy (S1-4). | §5.1 | ____ |

### D. Questions the judgments leave unresolved

| ID | Question | Passages | Answer |
|---|---|---|---|
| QR-D1 | Is an offence whose maximum term is exactly seven years (e.g. BNS 318(4), 308(2), 57, 117(2), 305, 306, 316(3)–(4)) within "less than seven years"? How should SC-IP para 28 (s.57 treated as outside) and SC-AD para 25 (308(2) and 318(4) treated as within) be read, given that neither analyses the point? (RB-09) | §3.5, §4.5; row C | ____ |
| QR-D2 | Is "made punishable for" read by the maximum term? How are exactly-three-year offences, minimum terms, and different first and repeat terms treated? (RB-09, RB-13) | Row D | ____ |
| QR-D3 | Is Bandhoo's statement that 173(3) is "legally inapplicable to vague complaints lacking prima facie allegations of a cognizable offence" (`service.py` line 557; prompt line 60) consistent with SC-AD paras 22 and 25? Or does it address a different situation (no offence identified at all)? | Row G | ____ |
| QR-D4 | How does 173(3) operate when a complaint alleges several offences with different terms or classifications? SC-AD's FIR included the non-cognizable 351(2); s.174(4) applies to multi-offence cases (RB-10). | §4.5 | ____ |
| QR-D5 | What is the effect of "Without prejudice to the provisions contained in section 175"? Must Bandhoo's paraphrase reproduce it? (RB-08) | §2.1; row I | ____ |

### E. Whether the current Gemini prompt is materially misleading

| ID | Question | Passages | Answer |
|---|---|---|---|
| QR-E1 | Is prompt line 59 ("…prior permission from an officer not below the rank of Deputy Superintendent of Police (DSP) within 14 days, or police proceed directly with investigation…") materially misleading to a citizen? In particular: (a) it attaches the period to permission; (b) "police proceed directly with investigation" omits that limb (ii) is also subject to the same permission clause; (c) it omits "considering the nature and gravity of the offence". | Row A | ____ |
| QR-E2 | Are prompt lines 60–63 (the "NEVER recommend" rules) materially misleading after SC-IP and SC-AD? In particular, line 63 for seven-year-maximum offences (QR-D1) and line 60 for vague complaints (QR-D3). | Rows C, G | ____ |
| QR-E3 | Does the prompt's omission of the "always appropriate" / "must normally grant permission" statements for speech offences (SC-IP para 29, 42(v)) make its advice misleading for such complaints? | Row B | ____ |

### F. Can a minimal prompt correction be approved on its own?

| ID | Question | Passages | Answer |
|---|---|---|---|
| QR-F1 | Can Q-01 Step 1 be approved before QR-B2, QR-C and QR-D are decided? Step 1 replaces line 59 with wording that mirrors the statutory structure, reusing `BNSS_173_3_PROCEDURE_TEXT`, and adds no interpretation. | Q-01; row A | ____ |
| QR-F2 | If approved, must the replacement keep "within a period of fourteen days" attached to clause (i) without stating when the period begins? | §2.1 | ____ |
| QR-F3 | Should the same minimal change also include "without prejudice to … section 175" and "considering the nature and gravity of the offence"? Or are those separate changes requiring separate approval? | §2.1 | ____ |
| QR-F4 | Should any prompt change wait until the deterministic texts (`BNSS_173_3_CAVEAT_TEXT`, `service.py` line 557 and lines 773–783) are reviewed, so that the prompt and the templates do not diverge? | §6.2 | ____ |
| QR-F5 | Does Q-01 Step 1 require only QLR sign-off plus MNT (path B in `post_review_change_protocol.md`), or also PO approval because it changes user-facing advice? | Q-01 | ____ |

---

## 8. What this dossier does not do

- It changes no code, prompt, template, corpus record, benchmark label, threshold or existing report.
- It does not close or downgrade any blocker (RB-02, RB-03, RB-08, RB-08.a, RB-09, RB-10, RB-11 remain Open). Q-01 remains Blocked.
- It does not mark any item approved, decided or verified.
- It does not change checklist step statuses. If the PO wishes, S1-5 can be updated to cite this dossier after an SC check.
- It does not treat either Maharashtra bill as law.
- It does not claim that either judgment settles any question listed in §7.

## 9. Next steps

1. **PO:** appoint the reviewers using `reports/reviewer_assignment_template.md`. No assignment exists today.
2. **SC:** check the quotations in §3.3, §4.3 and §5.1 against the PDFs (SHA-256 values in §1). Confirm the page and paragraph references, and the emphasised words, which were not visible in the extraction.
3. **Source-acquisition owner:**
   - obtain *Lalita Kumari* from the Supreme Court or SCC (S1-4);
   - confirm the Maharashtra amendment's status (S1-3);
   - search for Bombay High Court decisions on 173(3) (S1-5).
4. **QLR 1 and QLR 2:** answer §7 independently. Disagreements go to the ADJ.
5. Only after sign-off can Q-01 Step 1 move through `reports/post_review_change_protocol.md`.
