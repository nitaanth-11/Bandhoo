# Bandhoo Legal-Review Execution Checklist

**Prepared:** 2026-10-21. **For:** the project owner (PO), qualified Indian criminal-law reviewers (QLR), the adjudicator (ADJ), the second checker (SC), the evaluation lead (EL) and Bandhoo maintainers (MNT).

**Status:** nothing in this checklist has been started, reviewed or approved. Bandhoo remains internal-testing-only and is not legally validated.

This checklist turns the existing reports into a tracked work sequence. It adds no findings and resolves no legal question. Identifiers RB-xx, LR-xx and P0-x/P1-x/P2-x come from:
- `reports/release_blocker_register.md`;
- `reports/legal_review_checklist.md`;
- `reports/legal_risk_remediation_plan.md`.

Step IDs (`S1-x`, `S2-x`, `S3-x`, `S4-x`) are local to this document.

## 0. Baseline and controlling documents

| Item | State (checked 2026-10-21) |
|---|---|
| Baseline snapshot | `/Users/tanaya/Desktop/Bandhoo_snapshots/bandhoo_baseline_20261020T210347/` (`reports/baseline_and_rollback_audit.md`). Manifest SHA-256 `5125ea461052efb0b0d38b437f0da22f02e4d1f110d67e0cdab0fcd9b779b2c1` matches; snapshot and original both verify 105/105; snapshot read-only. |
| Change protocol | `reports/post_review_change_protocol.md` (gates 1–9; path A transcription, path B interpretation, path C classification). |
| Evidence so far | `reports/source_verification_matrix.md` and `reports/source_verification_summary.md`. Single-copy sources only: PRS-hosted Gazette PDFs of the BNS and BNSS (25 Dec 2023), PRS copy of the Consumer Protection Act, 2019, and a Manupatra print of *Lalita Kumari* hosted on the Madhya Pradesh High Court site (TLS unverified). |

## The gate

**No change to statutory text, the Gemini prompt, procedural advice templates, procedural logic, Schedule I registry rows or benchmark labels may be made** until all of the following are recorded:
- the Stage 1 source evidence for that item;
- the Stage 2 decision (where interpretation is involved);
- the Stage 3 prerequisites.

All three must satisfy `reports/post_review_change_protocol.md`.

Matching a statutory source does not resolve a legal question. Passing tests does not approve a change.

## Roles and qualifications

Proposed minimums, to be confirmed or amended by the PO before assignment. No person has been assigned.

| Role | Proposed minimum qualification | Assigned | Date assigned |
|---|---|---|---|
| QLR 1 | Advocate enrolled with an Indian State Bar Council, with criminal-law practice including BNS/BNSS matters; no involvement in Bandhoo development | Unassigned | — |
| QLR 2 | Same as QLR 1; independent of QLR 1 | Unassigned | — |
| ADJ | Senior criminal-law practitioner or academic; not QLR 1 or 2 | Unassigned | — |
| SC (second checker) | Any careful reader independent of the change author; for text comparison only | Unassigned | — |
| EL | Evaluation lead, not a Bandhoo developer | Unassigned | — |
| MNT | Bandhoo maintainer (technical approval, implementation) | Unassigned | — |
| PO | Project owner (approvals for user-facing changes, live-evaluation budget, release decisions) | Unassigned | — |

Status values used below: **Not started**, **In progress**, **Evidence recorded**, **Decided**, **Disputed (to ADJ)**, **Provisional (unresolved)**, **Closed**. Every item is currently **Not started**.

---

## Stage 1 — Source acquisition

Source acquisition establishes **what the text says** in an authoritative copy. It does not decide what the text means; meaning belongs to Stage 2.

### Recording template (one per source)

| Field | Entry |
|---|---|
| Document title, Act or case number, date | |
| Publisher or host; URL or physical reference | |
| Access date; who accessed it | |
| Version or "as on" date; amendment status | |
| Exact passages checked (section, sub-section, clause, verbatim) | |
| Comparison with the current single copy (same / differs: how) | |
| Limitations (extraction quality, unofficial host, unverified TLS, missing pages) | |
| Recorded by; checked by (SC) | |

### Acquisition tasks

| Step | Blocker IDs | Source to obtain | Passages to check (minimum) | Current state of evidence | Assigned | Access date | Status |
|---|---|---|---|---|---|---|---|
| S1-1 | RB-03; enables RB-18–RB-26, RB-05, RB-23, RB-24 | **Second authoritative copy of the BNS 2023** (e.g. India Code, the Gazette of India e-Gazette, or the Legislative Department; none yet accessed). | s.2(21)–(22); 115(2); 117(2), (4); 303(1) Explanation 2, 303(2) and proviso; 304(1); 305; 306; 309(4)–(6); 310(1); 311; 316(1)–(5) and illustration; 318 and illustration (e); 324(3)–(6); 336–340; 351(1)–(4); s.119 margin heading; cross-references in s.71, 89, 148, 199, 264, 341; the 15 corrections in `reports/corpus_corrections_log_2026-10-20.json`. | Not obtained. Retried 2026-10-21: India Code BNS PDF again returned an error page (HTTP 403 / Akamai error). No other official full copy found (search of mha.gov.in, legislative.gov.in, egazette.gov.in returned only S.O. 2790(E), which is not the Act text). Still single-copy (PRS). | Unassigned | 2026-10-21 (attempted) | In progress: not obtained |
| S1-2 | RB-03; enables RB-08, RB-10, RB-12, RB-17, RB-32–RB-35 | **Second authoritative copy of the BNSS 2023, including the First Schedule** | s.173(1)–(4); 174(1), (2), (4); 175 (cross-referenced by 173(3)); Schedule I rows for BNS 62, 87, 90, 115(2), 117(2)–(4), 134, 276, 303(2) (both rows), 304(2), 305, 306, 309(4)–(6), 310(2)–(6), 314, 316(2)–(5), 318(2)–(4), 324(2)–(6), 331, 351(2)–(4), 352, 354, 355, 357. | Partial. Second official-host reproduction of **s.173(3) preamble and clause (i) only**, as an extract printed in Maharashtra L.C. Bill No. VI of 2026 (as passed by the Legislative Council, mls.org.in): wording identical to the PRS copy; limb (ii) elided. Full BNSS and First Schedule not obtained (India Code error page on 2026-10-21). | Unassigned | 2026-10-21 | In progress: partial |
| S1-3 | RB-03 | **Amendments, corrigenda and commencement notifications** for the BNS and BNSS after 25 Dec 2023, with effective dates. Include **Maharashtra state amendments**, since Bandhoo is built around Mumbai police jurisdictions. | Any change to the sections listed in S1-1 and S1-2; any corrigendum to Schedule I row 324(4); commencement date(s). | Bills only. **Enactment status UNKNOWN**: not established, and neither bill is treated as current law. L.C. Bill No. VI of 2026 ("As passed by the Legislative Council on the 24th March, 2026"; clause 6) and L.C. Bill No. XVII of 2026 ("As passed by the Legislative Council on the 8th July, 2026", mls.org.in copy; clause 7) each substitute "six weeks" for "fourteen days" in BNSS s.173(3)(i) for Maharashtra. No evidence found of Assembly passage, assent, an Act number, Gazette publication or commencement. Maharashtra Acts Nos. I–LIII of 2026 in the Bombay High Court library (latest first published 13 Aug 2026; No. LIV returned HTTP 404) include no BNSS amendment Act, and none contains "173"; this is **not** proof of non-enactment (the library may lag). Central: only S.O. 2790(E) found; no central amending Act or corrigendum found, which is **not** evidence that none exists. | Unassigned | 2026-10-21 | In progress: enactment status UNKNOWN |
| S1-4 | RB-02; enables RB-11 | **Full *Lalita Kumari v. Govt. of U.P.* judgment** (WP (Crl.) 68 of 2008, decided 12.11.2013) from the Supreme Court or a recognized reporter (SCC (2014) 2 SCC 1 if accessible). | Case details; bench; the conclusions paragraph (para 111 in the Manupatra print, which may be numbered differently in SCC); the equivalent-citation list; any paragraph a QLR relies on. | Official copy of the judgment itself **not obtained**. Retried 2026-10-21: no Supreme Court-hosted PDF found; one `api.sci.gov.in/jonew/judis/` file returned by search was an unrelated 2016 order. **Partial new evidence:** the Supreme Court's own judgment in *Imran Pratapgadhi* (2025 INSC 410, api.sci.gov.in) reproduces Lalita Kumari's conclusions as "Paragraph 120" (footnote: "(2014) 2 SCC 1"). Its 120.1 and 120.7 have the same wording as paras 111(i) and 111(vii) of the Manupatra print, apart from "The" at the start of 120.1 and punctuation ("time-bound", "weeks'"). This is a quotation inside a later judgment, not a copy of *Lalita Kumari*. | Unassigned | 2026-10-21 | In progress: official copy not obtained |
| S1-5 | RB-11 | **Later judgments interpreting BNSS s.173(3)** (Supreme Court and High Courts, including the Bombay High Court) | Holdings on preliminary enquiry under 173(3) and its relationship with *Lalita Kumari*. | Two Supreme Court judgments obtained from the Court's own host (api.sci.gov.in, TLS verified): *Imran Pratapgadhi v. State of Gujarat*, Crl. A. No. 1545 of 2025, 2025 INSC 410, 28 March 2025 (Abhay S. Oka and Ujjal Bhuyan, JJ.), and *Ashish Dave v. State of Rajasthan*, Crl. A. arising out of SLP (Crl.) No. 19369 of 2025, 2026 INSC 244, 27 February 2026 (Vikram Nath and Sandeep Mehta, JJ.). The second cites the first as "(2026) 1 SCC 721" (SCC volume not inspected). Passages are quoted in the acquisition record below. Not SC-checked; no interpretation drawn. High Court decisions, including the Bombay High Court's, not yet sought. | Unassigned | 2026-10-21 | In progress: two SC judgments obtained |
| S1-6 | RB-04.a | **Second copy of the Consumer Protection Act, 2019**, with amendments and relevant rules | s.2(6)(iv); 28(1); 42(1); 53(1); any provision on where and how a pricing complaint is filed. | Not obtained. India Code CPA PDF returned an error page (2026-10-20). PRS copy (as enacted) remains the only copy. Retried 2026-10-21: searches found only the India Code copy (still blocked) and secondary hosts (simpliance.in, taxheal.com), which were not used. | Unassigned | 2026-10-21 (attempted) | In progress: not obtained |
| S1-7 | RB-04.b | **Source for any "Legal Metrology" referral** (the statute and authority actually responsible, if the referral is to be kept) | Provisions creating the authority and covering pricing or labelling complaints. | Inspected the Legal Metrology Act, 2009 (No. 1 of 2010), PRS-hosted copy as enacted: s.14(1) State Government may appoint a "Controller of legal metrology"; s.18 declarations on pre-packaged commodities (details "as may be prescribed"). The Act does not mention the Consumer Protection Act. India Code consolidated copy returned an error page; amendments and rules not inspected. Retried 2026-10-21: a Legal Metrology (Packaged Commodities) Rules, 2011 copy on legalmetrology.nagaland.gov.in failed to download (no HTTP response) and was not obtained by other means. A Department of Consumer Affairs file (consumeraffairs.nic.in, `14-July-2024.pdf`) appeared in search results but was not downloaded or inspected. | Unassigned | 2026-10-21 | In progress: as-enacted copy inspected |
| S1-8 | RB-16.a | **Schedule I rows and punishments for BNS s.103 and s.64**, cited as examples in the Gemini prompt (`legal_engine/llm_client.py` line 63) | Punishment terms; classification rows. | Inspected in the single PRS copies: BNS 103(1) "death or imprisonment for life"; 64(1) rigorous imprisonment "not … less than ten years" up to life; Schedule rows 103(1), 103(2), 64(1): Cognizable, Non-bailable, Court of Session. Second copy not obtained. | Unassigned | 2026-10-21 | In progress: single copy checked |

**Stage 1 exit criterion for each item:** the recording template is complete, checked by the SC, and differences from the current single copy are listed. No legal conclusion is drawn.

### Stage 1 acquisition record — 2026-10-21

Recorded by the Bandhoo maintainer session (automated retrieval; **no SC check yet**). Statuses above were updated on 2026-10-21; Stages 2–4 are unchanged. Nothing below is a legal conclusion.

| Category | Document | Provenance | Passage checked | Limitations |
|---|---|---|---|---|
| Central legislation (notification) | S.O. 2790(E), 16 July 2024, Ministry of Law and Justice (Legislative Department), Gazette of India Extraordinary Part II, Sec. 3(ii), No. 2654 | egazette.gov.in (`WriteReadData/2024/255467.pdf`) | Under s.8 of the General Clauses Act, references to the IPC, CrPC and Indian Evidence Act in other laws are read as references to the BNS, BNSS and BSA | Not a copy of the BNS or BNSS text; does not satisfy S1-1 or S1-2 |
| Maharashtra instrument (bill) | L.C. Bill No. VI of 2026, "(As passed by the Legislative Council on the 24th March, 2026.)" | Maharashtra Legislature Secretariat (mls.org.in) | Clause 6: "In section 173 of the said Sanhita, in sub-section (3), in clause (i), for the words "fourteen days" the words "six weeks" shall be substituted." Extract of current s.173(3) preamble and clause (i) printed at the end of the bill | A bill; enactment status unknown |
| Maharashtra instrument (bill) | L.C. Bill No. VI of 2026 as introduced (18 March 2026), Maharashtra Government Gazette Extraordinary Part V-A | PRS-hosted PDF | Same clause 6 | A bill |
| Maharashtra instrument (bill) | L.C. Bill No. XVII of 2026, introduced 3 July 2026 | PRS-hosted PDF | Clause 7 (same substitution in 173(3)(i)); Statement of Objects (vi): "The time period for conducting preliminary enquiry … is proposed to be increased from fourteen days to six weeks" | A bill; relationship to Bill VI unknown |
| Maharashtra instrument (bill) | L.A. Bill No. CVI of 2025 | PRS-hosted PDF | Amends the Maharashtra Lokayukta Act, 2023 (references to s.173) | Not relevant to the BNS/BNSS text |
| Central legislation (other) | Legal Metrology Act, 2009 (No. 1 of 2010) | PRS-hosted PDF (as enacted) | s.14(1); s.18(1)–(2) | Amendments and rules not inspected |
| Central legislation | BNS s.103(1), s.64(1); BNSS Schedule rows 103(1), 103(2), 64(1) | Existing PRS Gazette copies | Quoted in S1-8 | Single copy |

**Unsuccessful retrieval attempts (2026-10-21):** India Code PDFs for the BNS (`…/20062/1/a202345.pdf`), BNSS (`…/20099/3/A2023-46.pdf`) and Legal Metrology Act (`…/2102/1/2009l.pdf`) each returned an HTML error page instead of the document.

**Manual acquisition steps still required:**
1. Download the BNS and BNSS (with the First Schedule) from India Code or the Gazette of India e-Gazette in an ordinary browser, or obtain a certified copy. Record the version or "as on" date.
2. Obtain the Maharashtra Government Gazette notification (or Law and Judiciary Department record) showing whether the Bharatiya Nagarik Suraksha Sanhita (Maharashtra Amendment) Act, 2026 received assent, its Act number, its commencement date, and which bill text was enacted.
3. Check the Gazette of India for any central amending Act or corrigendum after 25 Dec 2023, including any corrigendum to Schedule I row 324(4).
4. Obtain *Lalita Kumari* from the Supreme Court's records or the SCC report.
5. Obtain the current Consumer Protection Act, 2019, the Legal Metrology Act, 2009, and the relevant rules from an official source.

### Stage 1 acquisition record — 2026-10-21 (second pass)

Recorded by the Bandhoo maintainer session (automated retrieval; **no SC check yet**). Only the Stage 1 rows S1-3 to S1-7 above were changed. Stages 2–4, every blocker and every correction-queue item are unchanged. **Source matching only:** quoting a passage here does not decide how it applies to Bandhoo. That remains a QLR question.

#### Maharashtra instruments (BNSS s.173(3) amendment)

| Document | Provenance | Passage checked | Limitations |
|---|---|---|---|
| L.C. Bill No. XVII of 2026, "(As passed by the Legislative Council on the 8th July, 2026.)" | Maharashtra Legislature Secretariat, `https://mls.org.in/` + path `council-bill/2026/विधानपरिषदेची सन २०२६ ची संमत केलेली विधेयके/वि. प. वि. क्र. १७/L. C. BILL No. 17 - English.pdf` (TLS verified). SHA-256 `1d2ecbc1d7cf4f9dfbb61b8eb96e7f8af145ebfe449f3cba40559918a18b0af8` | Clause 7: "In section 173 of the said Sanhita, in sub-section (3), in clause (i), for the words "fourteen days" the words "six weeks" shall be substituted." The Statement of Objects says the period "is proposed to be increased from fourteen days to six weeks". | A bill passed by one House. Relationship to L.C. Bill VI not established. |
| Maharashtra Acts Nos. I–LIII of 2026 (negative search) | Bombay High Court library, `https://bombayhighcourt.gov.in/bhc/libweb/legislation/acts/Stateact/2026acts/2026.NN.pdf` (NN = 01–53; 54 returned HTTP 404). Latest: Act No. LIII, "First published, after having received the assent of the Governor in the "Maharashtra Government Gazette", on the 13th August 2026" | Short titles of all 53 Acts and a full-text search. No BNSS (Maharashtra Amendment) Act. The BNSS is mentioned only in Acts I, IV, XXXVIII and XLVII (Prevention of Begging, Prisons and Correctional, Scheduled Castes, Freedom of Religion). No extraction contains "173". | A court library mirror, not the Maharashtra Government Gazette, and it may lag. Absence is **not** proof that no Act exists. Whether assent is needed from the Governor or the President (Constitution art. 254(2)), and therefore where it would be recorded, is a legal question for the QLR and is not decided here. |
| News report: `https://www.outlookindia.com/national/maharashtra-wants-30-day-preventive-custody-can-state-change-criminal-law` | Outlook India (secondary) | Reports that the bill had not been approved by the Legislative Assembly | Secondary source; not evidence of status. Publication date not recorded. Used only as a lead. |

**Conclusion on Maharashtra status: UNKNOWN.** No assent, Act number, Gazette publication or commencement was found. Neither bill is to be treated as current law, and the Q-01 Step 2 precondition is not met.

#### Judicial sources (S1-4, S1-5)

| Document | Provenance | Passages checked (quoted, not interpreted) | Limitations |
|---|---|---|---|
| *Imran Pratapgadhi v. State of Gujarat*, Crl. A. No. 1545 of 2025, **2025 INSC 410**, Supreme Court of India, judgment of 28 March 2025 by Abhay S. Oka, J. (signed Abhay S. Oka and Ujjal Bhuyan, JJ.), 54 pages | `https://api.sci.gov.in/supremecourt/2025/3511/3511_2025_4_1501_60508_Judgement_28-Mar-2025.pdf` (official Supreme Court host; TLS verified). URL first seen on a third-party blog (advocategandhi.com); the document was obtained from the official host. SHA-256 `896f08f97519248a7f004350d43b72ffc296144e817c0be8b0365bd28f0d5a58` | Para 22: "Sub-Section (1) of Section 173 of BNSS is substantially the same as Sub-Section (1) of Section 154 of the Code of Criminal Procedure, 1973 … the law laid down by this Court in the case of Lalita Kumari v. Govt. of U.P. on Section 154 of the CrPC will be relevant." It then quotes Lalita Kumari "Paragraph 120" (120.1–120.8), with footnote "(2014) 2 SCC 1". Para 23: "Sub-Section (3) of Section 173 of the BNSS is an exception to sub-Section (1) of Section 173." Para 28: "Sub-Section (3) of Section 173 of the BNSS confers a discretion on the officer … This option is available when the offence alleged is made punishable for 3 years or more but less than 7 years." Para 42(i)–(ii): summary of conclusions repeating paras 23–24. | Not SC-checked. The case concerns BNS s.196 and speech offences, so the scope of each observation is for the QLR. |
| *Ashish Dave v. State of Rajasthan*, Crl. A. arising out of SLP (Crl.) No. 19369 of 2025, **2026 INSC 244**, Supreme Court of India, judgment by Sandeep Mehta, J. (signed Vikram Nath and Sandeep Mehta, JJ.), dated 27 February 2026, 23 pages | `https://api.sci.gov.in/supremecourt/2025/68616/68616_2025_2_34_68884_FinalOrder_27-Feb-2026.pdf` (official host; TLS verified). SHA-256 `3350c58215253837483fbe01397717b841f08cbb25ac2d5cbfb31edaff81bc0b` | Para 24 quotes paras 23–24 of *Imran Pratapgadhi* (footnote 8: "(2026) 1 SCC 721"), then: "the scheme of Section 173(3) of the BNSS travels a step further and exposits situations where preliminary inquiry may be made even where the complaint is filed for cognizable offences." Para 25: "None of the offences alleged in the impugned FIR carries imprisonment which may extend to more than seven years, thereby bringing the case within the category where the option of conducting a preliminary enquiry under Section 173(3) of the BNSS was clearly available". | Not SC-checked. The SCC report (2026) 1 SCC 721 was not inspected. The Lalita Kumari footnote 7 reads "(2014) 2 SCC 1". |
| Lead only: a neutral citation "2013 INSC 748" and "[2013] 14 S.C.R. 713" for *Lalita Kumari* | Search-result description of a third-party dataset mirror | — | Not seen in any official document. Use only to search the Supreme Court portal. |
| Not relevant: `https://api.sci.gov.in/jonew/judis/43730.pdf` | Official host | *Life Convict Lal Singh v. State of Punjab*, W.P. (Crl.) 181 of 2012, 29 June 2016 | Recorded only so that it is not rechecked. |

**Numbering note (no conclusion drawn):** both Supreme Court judgments number *Lalita Kumari*'s conclusions as paragraph 120 (for example, "paragraph 120.2"). The Manupatra print (LK-MPHC) numbers them as paragraph 111. Any QLR citation should use the reported paragraph numbering.

#### Unsuccessful retrieval attempts (second pass)

- India Code (BNS, BNSS, CPA, Legal Metrology Act): still blocked (error page or HTTP 403).
- `https://legalmetrology.nagaland.gov.in/documents/11/9_The_Legal_Metrology_Package_Commodities_Rules_2011.pdf`: no HTTP response. Certificate or other warnings were **not** bypassed.
- Consumer Protection Act, 2019: no official current copy found. Secondary hosts (simpliance.in, taxheal.com) were not used.
- Second full BNS or BNSS: not obtained.

**Manual acquisition steps still required** (unchanged from the first pass, with these additions):
- (step 2) Check the Maharashtra Government Gazette, or the Law and Judiciary Department, for L.C. Bills VI and XVII of 2026. Record Assembly passage, assent (Governor or President), Act number and commencement, or record that none exists as on the date checked.
- (step 4) Search the Supreme Court judgment portal for *Lalita Kumari* (W.P. (Crl.) 68 of 2008, 12.11.2013; possible neutral citation 2013 INSC 748), or obtain the SCC volume (2014) 2 SCC 1.
- (S1-5) The SC checks the passages quoted above against the PDFs (SHA-256 values given). Search for Bombay High Court decisions on BNSS s.173(3).

---

## Stage 2 — Qualified legal review

Each item needs the Stage 1 evidence listed. Two QLRs decide independently; disagreements go to the ADJ. Unresolved items are marked **Provisional (unresolved)**, and Bandhoo keeps its current uncertainty-preserving behaviour.

Every Stage 2 table ends with the same five tracking columns: **Reviewer** (currently Unassigned), **Decision**, **Notes**, **Approval date** (all currently "—") and **Status** (currently Not started).

### 2A. BNS substantive and textual questions

| IDs | Exact question | Evidence needed | Reviewer | Decision | Notes | Approval date | Status |
|---|---|---|---|---|---|---|---|
| RB-06 / LR-09 | At the information or FIR stage, may theft of property under Rs 5,000 that has been returned or restored be treated as non-cognizable, given that the BNS 303(2) proviso also requires a first conviction known only after trial? Is leaving classification "unknown" correct? | S1-1 (303(2)); S1-2 (both Schedule rows); S1-3 | Unassigned | — | — | — | Not started |
| RB-07 / LR-10 | How is "value of the stolen property" determined (aggregate of items or per item; market, purchase or estimated value)? Are Bandhoo's rules in `legal_engine/amounts.py` acceptable, including treating ambiguous totals as unknown? | S1-1; any case law the QLR relies on | Unassigned | — | — | — | Not started |
| RB-13 / LR-03(b) | For Section 173(3), which theft term governs: 3 years (first conviction) or 1–5 years (repeat), given that the Schedule row shows the repeat term? | S1-1, S1-2 | Unassigned | — | — | — | Not started |
| RB-21 / LR-03(a) | s.303 Explanation 2: is the enacted word "affects" or "effects", and does the difference matter? | S1-1 (second copy) | Unassigned | — | — | — | Not started |
| RB-12 / LR-15 | For mischief causing loss between Rs 1 lakh and Rs 2 lakh, which classification applies given BNS 324(4) "less than one lakh" and Schedule row 324(4) "less than 2 lakh"? Has a corrigendum or amendment resolved it? | S1-1, S1-2, S1-3 | Unassigned | — | — | — | Not started |
| RB-18 / LR-01 | s.115(2): confirm the enacted cross-reference (the current copy reads "section 122"; the corpus reads "section 120") and the Schedule I classification of 115(2). | S1-1, S1-2 | Unassigned | — | — | — | Not started |
| RB-19 / LR-02 | s.117(2) cross-reference and s.117(4) elements ("acting in concert", "or community", "similar"): confirm the enacted wording. Is it correct to tell users that bailability depends on the sub-section when the facts are unclear? | S1-1, S1-2 | Unassigned | — | — | — | Not started |
| RB-14 / LR-05(b) | s.316: are capacity keywords ("employee", "servant", "agent", "banker", "carrier", etc.) an acceptable way to flag 316(3)–(5)? Should the punishment field list all sub-sections? | S1-1, S1-2 | Unassigned | — | — | — | Not started |
| LR-06 | s.318: confirm the classification rows and whether generic "conditional" advice is adequate for cheating complaints. | S1-1, S1-2 | Unassigned | — | — | — | Not started |
| RB-20 / LR-08 | s.351: confirm the enacted wording ("threatens another by any means"; "threatening") and that 351(3) is non-cognizable and bailable despite a 7-year maximum. | S1-1, S1-2 | Unassigned | — | — | — | Not started |
| RB-15 / LR-04(c) | Should Section 134 be offered as an alternative when force is used on a person in an attempted theft (chain snatch, pickpocketing)? | S1-1, S1-2 | Unassigned | — | — | — | Not started |

### 2B. BNSS procedure and *Lalita Kumari*

| IDs | Exact question | Evidence needed | Reviewer | Decision | Notes | Approval date | Status |
|---|---|---|---|---|---|---|---|
| RB-08 / LR-11 | Is Bandhoo's 173(3) paraphrase (`BNSS_173_3_PROCEDURE_TEXT`) faithful, given that it omits "without prejudice to section 175"? Is "discretion" the right characterisation? What does the fourteen-day period govern? Should citizen-facing advice mention 173(3) at all? | S1-2 (173, 175) | Unassigned | — | — | — | Not started |
| RB-08.a | Approve prompt wording that attaches "within a period of fourteen days" to the preliminary enquiry (limb (i)) rather than to DSP permission, adding no other interpretation. | S1-2 | Unassigned | — | — | — | Not started |
| RB-09 / LR-12 | Is "made punishable for three years or more but less than seven years" read by maximum term? How are offences with exactly 3 or exactly 7 years, minimum terms, or different first and repeat terms treated? | S1-2; S1-5 | Unassigned | — | — | — | Not started |
| RB-10 / LR-13 | Is citing BNSS 174(4) at the information-recording stage correct for multi-offence complaints? May a 173(3) enquiry be held when another alleged offence carries 7 years or more? Is a score cut-off an acceptable basis for which offences the advice mentions? | S1-2 | Unassigned | — | — | — | Not started |
| RB-02 / LR-14 | Is the citation "(2014) 2 SCC 1" correct, and is the one-line summary ("mandatory registration of an FIR where information discloses a cognizable offence") accurate and sufficient? | S1-4 | Unassigned | — | — | — | Not started |
| RB-11 / LR-14 | What is the current position on how BNSS 173(3) relates to *Lalita Kumari* (decided under CrPC s.154), including its preliminary-inquiry categories and the fifteen-day guidance in para 111(vii) of the inspected print? Should Bandhoo's caveat change? | S1-2, S1-4, S1-5 | Unassigned | — | — | — | Not started |

### 2C. The 14 hand-entered Schedule I classifications (RB-17 / LR-18)

Registry `VERIFIED_SCHEDULE_I` in `legal_engine/schedule_registry.py`. For each row: confirm cognizable, bailable, court and maximum term against S1-2 and S1-3.

| Section | Rows held by Bandhoo | Evidence needed | Reviewer | Decision | Notes | Approval date | Status |
|---|---|---|---|---|---|---|---|
| 115 | 115(2) | S1-2 | Unassigned | — | — | — | Not started |
| 117 | 117(2), 117(3), 117(4) | S1-2 | Unassigned | — | — | — | Not started |
| 303 | 303(2) main row; value under Rs 5,000 row | S1-2 | Unassigned | — | — | — | Not started |
| 304 | 304(2) | S1-2 | Unassigned | — | — | — | Not started |
| 305 | 305 | S1-2 | Unassigned | — | — | — | Not started |
| 306 | 306 | S1-2 | Unassigned | — | — | — | Not started |
| 309 | 309(4) (single entry; summary mentions 309(5), 309(6)) | S1-2 | Unassigned | — | — | — | Not started |
| 310 | 310(2) (single entry; summary mentions 310(3)–(6)) | S1-2 | Unassigned | — | — | — | Not started |
| 314 | 314 | S1-2 | Unassigned | — | — | — | Not started |
| 316 | 316(2)–(5) | S1-2 | Unassigned | — | — | — | Not started |
| 318 | 318(2)–(4) | S1-2 | Unassigned | — | — | — | Not started |
| 324 | 324(2)–(6) (see RB-12) | S1-2, S1-3 | Unassigned | — | — | — | Not started |
| 351 | 351(2)–(4) | S1-2 | Unassigned | — | — | — | Not started |
| 352 | 352 | S1-2 | Unassigned | — | — | — | Not started |

Related Schedule items (not in the registry; scraped blocks not used for output):

| IDs | Question | Evidence needed | Reviewer | Decision | Notes | Approval date | Status |
|---|---|---|---|---|---|---|---|
| RB-32 / LR-19 | s.87 classification (scraped block says non-cognizable; Gazette copy row says cognizable). Add to the registry or not? | S1-2 | Unassigned | — | — | — | Not started |
| RB-33 / LR-20 | s.90(1)–(2), same question | S1-2 | Unassigned | — | — | — | Not started |
| RB-34 / LR-21 | s.276 (scraped block says bailable; Gazette copy row says non-bailable) | S1-2 | Unassigned | — | — | — | Not started |
| RB-35 / LR-22 | s.354, 355, 357: confirm the rows from the printed Schedule (SC sufficient) | S1-2 | Unassigned | — | — | — | Not started |
| RB-36 / LR-23 | 195 unchecked scraped blocks: verify, discard or replace (PO decision) | S1-2 | Unassigned | — | — | — | Not started |

### 2D. The eight provisional benchmark cases (RB-37–RB-44 / LR-30–LR-37)

Labels are unchanged. Proposed corrections recorded in `label_review` in `benchmark/bns_synthetic_benchmark_50.json` are **not applied**. Two QLRs label independently and the ADJ resolves differences. The decision is the full gold label set: relevant and plausible provisions, contradicted provisions, cognizable, bailable.

| IDs | Case | Exact question | Evidence needed | Reviewer | Decision | Notes | Approval date | Status |
|---|---|---|---|---|---|---|---|---|
| RB-37 / LR-30 | BNS-BM-17 | Two offenders: is s.310 excluded? Does s.311 ("uses any deadly weapon") apply to holding a knife to the throat? Is midnight shop entry trespass or house-breaking? | S1-1 (310(1), 311, 329–331); case law on "uses" | Unassigned | — | — | — | Not started |
| RB-38 / LR-31 | BNS-BM-20 | Bailability of attempted theft (s.62 row: follows the offence attempted)? Is inserting a hand into a pocket "criminal force" under s.134? | S1-1, S1-2 (rows 62, 134, 303(2)) | Unassigned | — | — | — | Not started |
| RB-39 / LR-32 | BNS-BM-21 | Attempted chain snatch: 62 + 304, or 134? Bailability? | S1-1, S1-2 | Unassigned | — | — | — | Not started |
| RB-40 / LR-33 | BNS-BM-22 | Attempt under 303 or 305 (shop as a "building used for the custody of property")? Bailability? | S1-1, S1-2 | Unassigned | — | — | — | Not started |
| RB-41 / LR-34 | BNS-BM-28 | Does s.305 apply to a garage? Which s.331 sub-section applies? | S1-1, S1-2 | Unassigned | — | — | — | Not started |
| RB-42 / LR-35 | BNS-BM-30 | "Purana servant" and s.306; s.305 and s.331; s.115 or s.118(1) for a stick; robbery through hurt caused while carrying away property? | S1-1, S1-2 | Unassigned | — | — | — | Not started |
| RB-43 / LR-36 | BNS-BM-31 | Theft, criminal breach of trust (no entrustment stated) or dishonest misappropriation? Which trespass or house-breaking provisions? | S1-1, S1-2 | Unassigned | — | — | — | Not started |
| RB-44 / LR-37 | BNS-BM-45 | Does s.305 (dwelling) apply? Is s.329 relevant or only plausible when the entry facts are unstated? | S1-1, S1-2 | Unassigned | — | — | — | Not started |

### 2E. Non-penal templates, procedural advice and the Gemini prompt

| IDs | Location | Exact question | Evidence needed | Reviewer | Decision | Notes | Approval date | Status |
|---|---|---|---|---|---|---|---|---|
| RB-23 / LR-17 | `legal_engine/service.py`, `_build_non_penal_response` (citation at the docstring and in the intangible-grievance text) | (a) Confirm "movable property" is defined at BNS s.2(21) (SC sufficient after S1-1). (b) Is "intangible concepts … cannot be the subject of penal theft or robbery" an accurate statement for citizens? | S1-1 | Unassigned | — | — | — | Not started |
| LR-17.a | same function, "forgery of records (Section 336/338)" | What kind of "records" is the sentence meant to cover, and which provisions, if any, should be cited? | S1-1 (ss.336–340 in full) | Unassigned | — | — | — | Not started |
| RB-04.a | same function, consumer-pricing text | Is referring pricing grievances to the Consumer Disputes Redressal Commission appropriate, and must it be limited to the CPA s.2(6)(iv) ground (price above one fixed by law, displayed or agreed)? | S1-6 | Unassigned | — | — | — | Not started |
| RB-04.b | same text, "Legal Metrology Department under the Consumer Protection Act, 2019" | Should a Legal Metrology referral appear at all? If so, under which statute and authority? | S1-7 | Unassigned | — | — | — | Not started |
| RB-06.a | `legal_engine/llm_client.py` `SYSTEM_PROMPT`, theft proviso lines | Approve replacement wording that states both Schedule I rows and the first-conviction requirement without stating that the proviso "applies", and that does not decide RB-06 or RB-07. | S1-1, S1-2 | Unassigned | — | — | — | Not started |
| RB-16.a | `SYSTEM_PROMPT`, Section 173(3) examples | Should "Mischief Sec 324" be removed from the "less than 3 years" examples, or qualified by sub-section (324(5)–(6) carry up to 5 years)? Are the s.103 and s.64 examples accurate? | S1-2, S1-8 | Unassigned | — | — | — | Not started |
| RB-16 / LR-16 | `service.py` templates: `_theft_procedure_note`, `_robbery_procedure_note`, `_cbt_procedure_note`, `_grievous_hurt_procedure_note`, `_mischief_procedure_note`, `_misappropriation_procedure_note`, `_single_offence_procedure`, `_multi_offence_procedure`, `_audit_and_qualify_procedural_recommendation` (vague complaints), `_build_non_penal_response`; the statutory disclaimer in `legal_engine/schemas.py` | For each sentence: is it accurate, appropriately qualified, free of overclaiming, and suitable for citizens? | S1-1, S1-2 | Unassigned | — | — | — | Not started |

### 2F. Corpus discrepancies and potentially incomplete records

Mostly text confirmation (SC sufficient); QLR only where the wording changes an offence element.

| IDs | Records | Exact question | Evidence needed | Reviewer | Decision | Notes | Approval date | Status |
|---|---|---|---|---|---|---|---|---|
| RB-22 / LR-24 | Cross-references in s.71, 89, 148, 199, 264, 341 (differences observed in the single copy) | Confirm the enacted cross-references and approve replacement. | S1-1 | Unassigned | — | — | — | Not started |
| RB-26 / LR-24 | Cross-references in s.2, 29, 30, 99, 113, 122, 136, 155, 159, 167, 186, 200, 211, 212, 237, 240, 249, 265, 339, 342 (automated only) | Error, extraction noise or acceptable? | S1-1 | Unassigned | — | — | — | Not started |
| RB-24 / LR-28 | s.119 title | Approve correction to the Gazette margin heading. | S1-1 | Unassigned | — | — | — | Not started |
| RB-25 | s.304 "moveable"; s.316 illustration "a lakh"; s.318 illustration "diamond" | Correct or accept as immaterial? | S1-1 | Unassigned | — | — | — | Not started |
| RB-05 / LR-25 | 15 corrections applied on 2026-10-20 (s.13, 56, 58, 71, 111, 120, 148, 199, 251, 252, 264, 309, 311, 312, 341) | Confirm each against a second copy. | S1-1 | Unassigned | — | — | — | Not started |
| RB-29 / LR-26 | 13 unverified punishment fields (s.70, 113, 118, 124, 125, 206, 211, 221, 222, 260, 263, 316, 323) | Confirm or replace with enacted wording. | S1-1 | Unassigned | — | — | — | Not started |
| RB-30 / LR-27 | 63 records marked "no punishment clause" by automated check | Spot-check; correct exceptions. | S1-1 | Unassigned | — | — | — | Not started |
| RB-27 / LR-29 | 80 further records `differs_from_gazette_needs_review` (checklist Appendix A.1) | Classify each as error, artefact or acceptable. | S1-1 | Unassigned | — | — | — | Not started |
| RB-28 / LR-29 | 56 records `possibly_incomplete` (checklist Appendix A.2) | Classify each; identify truncation. | S1-1 | Unassigned | — | — | — | Not started |
| RB-31 / LR-07 | s.324 wording differences (likely extraction artefacts) | Confirm immaterial or correct. | S1-1 | Unassigned | — | — | — | Not started |

**Stage 2 exit criterion for each item:** decision, reasoning and authority recorded by two QLRs (or ADJ), or the item formally marked **Provisional (unresolved)** with Bandhoo's uncertainty-preserving behaviour retained. Decisions are copied into the decision fields of `reports/legal_review_checklist.md` by the reviewer or MNT at that time.

---

## Stage 3 — Approved corrections

A correction may start only when its Stage 1 and Stage 2 entries are complete. Each correction gets its own change record using the template in `reports/post_review_change_protocol.md` §3.

### 3.1 Prerequisites per correction

| # | Prerequisite (protocol gate) | Evidence to record |
|---|---|---|
| 1 | Source verified (gate 1) | Stage 1 step ID; source, version and amendment status |
| 2 | Exact passage and provenance (gate 2) | Verbatim passage; extraction notes; for corpus changes, a migration script whose `transcription_check` passes |
| 3 | Approvals (gate 3) | Path A: MNT + SC. Path B/C: QLR 1 + QLR 2 (or ADJ) + MNT, + PO for user-facing changes |
| 4 | Minimal change (gate 4) | One issue per change; no threshold, ranking or label side-effects; corpus changes via a migration with verified backup and atomic write |
| 5 | Regression test (gate 5) | Test name; output showing **fail before** and **pass after** |
| 6 | Offline tests (gate 6) | Targeted tests and full suite with Gemini disabled: counts and warnings; justification for any changed expectation |
| 7 | Benchmark comparison (gate 7) | Before/after fallback reports; case-by-case differences; ablation for corpus text changes; with and without provisional cases; **no relabelling** |
| 8 | Side-effect review (gate 8) | Related provisions, procedural templates, Gemini context lines, schedule metadata, register/checklist entries |
| 9 | Approval, uncertainty, rollback (gate 9) | Names, roles, dates; remaining uncertainty; rollback steps (migration backup path and SHA-256, or file restore from the snapshot per `reports/baseline_and_rollback_audit.md` §7) |
| 10 | Fresh snapshot | New snapshot and manifest **before each implementation batch**, because the 2026-10-20 baseline does not include later reports |

### 3.2 Correction tracker

Columns 1–10 refer to the prerequisites above. "—" means not yet satisfied. Every row is currently **Blocked** (Stage 1/2 not started).

| Plan ID | Correction (from the remediation plan) | Path | Depends on | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P0-1 | Gemini prompt: 173(3) timing attached to the preliminary enquiry (RB-08.a) | B | S1-2; 2B RB-08.a | — | — | — | — | — | — | — | — | — | — | Blocked |
| P0-2 | Gemini prompt: remove settled 303(2) proviso statement (RB-06.a) | B | S1-1, S1-2; 2E RB-06.a | — | — | — | — | — | — | — | — | — | — | Blocked |
| P0-3(a) | "2(22)" → "2(21)" in the non-penal template and docstring; update `tests/test_adversarial_grievance_audit.py` assertion (RB-23) | A | S1-1; 2E RB-23(a) | — | — | — | — | — | — | — | — | — | — | Blocked |
| P0-3(b) | Intangible-property sentence (RB-23(b)) | B | 2E RB-23(b) | — | — | — | — | — | — | — | — | — | — | Blocked |
| P0-4 | Forgery label (LR-17.a) | B | S1-1; 2E LR-17.a | — | — | — | — | — | — | — | — | — | — | Blocked |
| P0-5 | Consumer and Legal Metrology referral (RB-04.a, RB-04.b) | B | S1-6, S1-7; 2E | — | — | — | — | — | — | — | — | — | — | Blocked |
| P1-1 | Corpus text: s.115, 303, 304, 316, 318 (path A); s.117(2), 117(4), 351 (path B) | A/B | S1-1; 2A, 2F | — | — | — | — | — | — | — | — | — | — | Blocked |
| P1-2 | s.324 classification logic (RB-12) | C | S1-1–S1-3; 2A RB-12 | — | — | — | — | — | — | — | — | — | — | Blocked |
| P1-3 | Schedule items s.87, 90, 276, 354, 355, 357 (data marking; registry additions path C) | A/C | S1-2; 2C | — | — | — | — | — | — | — | — | — | — | Blocked |
| P1-4 | Registry rows, advice templates, prompt examples (RB-16, RB-16.a, RB-17) | B/C | S1-2, S1-8; 2C, 2E | — | — | — | — | — | — | — | — | — | — | Blocked |
| P1-5 | Remaining corpus records (RB-22, RB-24–RB-31) | A | S1-1; 2F | — | — | — | — | — | — | — | — | — | — | Blocked |
| C-rules | Any rule decided under RB-06, RB-07, RB-09, RB-10, RB-13, RB-14, RB-15 | C | 2A, 2B decisions | — | — | — | — | — | — | — | — | — | — | Blocked |
| P2-1 | Benchmark labels for the eight provisional cases (via `benchmark/build_dataset.py` with `review_history`) | Label change (independent adjudication) | 2D | — | — | — | — | — | — | — | — | — | — | Blocked |

---

## Stage 4 — Independent evaluation

Follows `reports/independent_evaluation_plan.md`. **The existing 50-case benchmark (`benchmark/bns_synthetic_benchmark_50.json`) is development data.** It was used during development; its "holdout" was previously inspected; it must not be reported as independent test performance.

| Step | IDs | Task | Owner role | Evidence of completion | Assigned | Status |
|---|---|---|---|---|---|---|
| S4-1 | RB-45 | Approve the evaluation plan and **release criteria** (set before any test scoring) | PO, QLR | Signed plan; criteria recorded in the evaluation log | Unassigned | Not started |
| S4-2 | RB-45 | Author new cases to the coverage matrix (authors independent of Bandhoo development); de-identify any real or judgment-derived material | EL, case authors | Case files with coverage tags; de-identification check by a second person | Unassigned | Not started |
| S4-3 | RB-45 | Independent double labelling by two QLRs (blind to Bandhoo outputs and to each other) | QLR 1, QLR 2 | Label files; agreement statistics | Unassigned | Not started |
| S4-4 | RB-45 | Adjudication of disagreements; unresolved cases marked provisional and excluded from headline metrics | ADJ | Adjudication log with rationale | Unassigned | Not started |
| S4-5 | RB-45 | Freeze and hash labels; split into development, validation and **sealed** test sets; check for leakage and near-duplicates | EL | Label hash; split files outside the repository; access log | Unassigned | Not started |
| S4-6 | RB-47 | Implement planned metrics (strict and lenient precision, abstention, per-offence procedural accuracy, serious-error tagging), on development data only | MNT, EL | Tests for the evaluator; metric definitions documented | Unassigned | Not started |
| S4-7 | RB-46 | Run evaluations **by mode, reported separately**: deterministic fallback; cached LLM (cache date, model, prompt hash); genuine live inference (only with PO approval and a quota budget). Mocked outputs are never reported as performance. Live runs that fell back are counted separately. | EL, PO | Mode-labelled reports with `inference_status` counts | Unassigned | Not started |
| S4-8 | RB-45, RB-48 | Final test run once per release candidate; report in the plan's format, **listing every S1 and S2 serious error individually** | EL | Final evaluation report | Unassigned | Not started |
| S4-9 | — | Release assessment against the pre-agreed criteria, open blockers and Stage 2 outcomes | PO, QLR | Recorded decision. Until then Bandhoo stays internal-testing-only. | Unassigned | Not started |

---

## Execution sequence

| Phase | Contents | Starts when | Ends when |
|---|---|---|---|
| **A. Source acquisition and verification** | S1-1 to S1-8 | Now (PO assigns an owner and an SC) | Each source recorded and checked by the SC |
| **B. Qualified legal review** | Stage 2 (2A–2F) | QLRs and ADJ assigned; the Stage 1 evidence for each item recorded | Each item decided or formally marked provisional |
| **C. Approval of narrowly scoped corrections** | Change records for each Stage 3 row | Stage 2 decision recorded (path B/C) or Stage 1 confirmation (path A) | Approvals recorded per protocol gate 3 |
| **D. Implementation with regression tests** | Stage 3 prerequisites 4–10 | Phase C approval for that correction; fresh snapshot taken | Tests, benchmark comparison, side-effect review and rollback recorded |
| **E. Independent evaluation and release assessment** | Stage 4 | S4-1 to S4-5 can run in parallel with phases A–D; S4-7 and S4-8 run on the corrected system | S4-9 decision recorded |

Phases A and E (steps S4-1 to S4-5) can start immediately and in parallel. Phases B–D proceed item by item.

## First actionable task

**S1-1 and S1-2: obtain a second authoritative copy of the BNS and BNSS (including the First Schedule).**

- **Prerequisite:** the PO assigns the person doing it and an SC.
- **How:** use an official host (India Code, the Gazette of India e-Gazette, or the Legislative Department). The India Code PDFs were blocked from this environment on 2026-10-20 (HTTP 403 or an error page), so a person using an ordinary browser, or an approved alternative official source, may be needed.
- **What to record:** for each passage listed in S1-1 and S1-2, use the Stage 1 template.
- **Also start S1-3** (amendments, including Maharashtra) at the same time.

These two steps unblock every path-A transcription item and most Stage 2 questions.

## Evidence currently unavailable

| Evidence | Blocks |
|---|---|
| Second authoritative copy of the BNS and BNSS (India Code blocked during verification) | All path-A corrections; confirmation of every single-copy discrepancy |
| Amendment and corrigendum status after 25 Dec 2023, including Maharashtra | Closure of RB-03; RB-12 |
| Supreme Court copy or SCC report of *Lalita Kumari*; later judgments on BNSS 173(3) | RB-02 closure; RB-11 |
| India Code copy, amendments and rules of the Consumer Protection Act, 2019 | RB-04.a |
| Any source for a Legal Metrology referral | RB-04.b |
| Source check of s.103 and s.64 rows | RB-16.a |
| Named, qualified reviewers | All of Stage 2 onward |
| Independent, lawyer-reviewed test set; recent genuine live results | Stage 4; any performance claim or release decision |

No blocker in `reports/release_blocker_register.md` is changed or closed by this checklist.
