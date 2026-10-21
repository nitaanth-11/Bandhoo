# BNSS Section 173(3): Triage of New Source Findings

**Prepared:** 2026-10-21 by the Bandhoo maintainer session, for the project owner (PO), the second checker (SC), the source-acquisition owner (SAO), QLR 1, QLR 2 and the adjudicator (ADJ).
**Source:** `reports/section_173_3_source_acquisition_log.md` (the "log"), plus one official cause list obtained this round (§B).
**Status:** triage only.
- No legal determination is made, and no fix is implemented.
- No existing report, blocker status, queue status or source-verification record is changed.
- New register or queue entries are **recommended only** (§E). The PO decides whether to register them.
- No reviewer is appointed, so nothing here is SC-verified.

Bandhoo remains internal-testing-only.

---

## A. *Lalita Kumari v. Govt. of U.P.* (W.P. (Crl.) No. 68 of 2008)

### A.1 What the evidence shows

| Item | Evidence | Status |
|---|---|---|
| **Original judgment, 12 Nov 2013**: direction (vii) | Official Supreme Court copy, `api.sci.gov.in/jonew/judis/40960.pdf` (SHA-256 `358a7336…3a57a6`), and the official report [2013] 14 S.C.R. 713 (Supreme Court asset store; SHA-256 `2dee8917…a1c161c`). Both read at para 111(vii): "…a preliminary inquiry should be made time bound and in any case it should not exceed **7 days**. The fact of such delay and the causes of it must be reflected in the General Diary entry." | Located and verified (provenance). **Not yet SC-checked.** |
| **Reported modification, 5 Mar 2014** | **Official, but from another court:** Delhi High Court, CONT.CAS(C) 582/2023, decided 11 Aug 2026, refers to the "judgment dated 12th November, 2013, and 05th March, 2014, passed by the Supreme Court in the case of Lalita Kumari" and to an inquiry "concluded within 15 days in normal cases, and 06 weeks" in exceptional ones. **Secondary:** news and blog reports (March 2014) that clause (vii) of para 111 was modified from 7 days to 15 days, or six weeks in exceptional cases. | **The Supreme Court's own copy of the 5 Mar 2014 order is not in the evidence set.** The order's existence is corroborated; its wording, date and scope are not verified. |
| Wording relied on in existing reports | The Manupatra print (LK-MPHC, TLS unverified) at 111(vii), and the *Imran Pratapgadhi* quotation at "120.7", read "fifteen days generally and in exceptional cases, by giving adequate reasons, six weeks' time is provided". | This matches the **reported modified** direction, **not** the 2013 text |
| **Paragraph numbering, original** | Official copy and S.C.R.: conclusions are **para 111**, (i)–(viii); the "counter claims" passage is **para 110** | Located and verified |
| **Paragraph numbering, later citations** | *Imran Pratapgadhi* (2025 INSC 410) cites "Paragraph 120" and "120.2"; *Ashish Dave* (2026 INSC 244) cites "119". Both footnote "(2014) 2 SCC 1". | Numbering as used in those judgments (official PDFs) |
| **Paragraph numbering, SCC report** | (2014) 2 SCC 1 | **Inaccessible** (subscription). It is **not verified** that 119/120 is the SCC numbering, or that the SCC text includes the modification. |

### A.2 What is not decided here

This triage does **not** decide:
- whether the 2013 direction remains in force unmodified;
- what the 2014 order says or does;
- whether any *Lalita Kumari* time limit applies to an enquiry under BNSS s.173(3);
- which version or paragraph number Bandhoo or its reports should cite.

### A.3 Records whose wording depends on this

These are listed for the PO; **none is edited**.

| Record | Current text |
|---|---|
| `reports/section_173_3_case_law_review_dossier.md` §5.1, §5.2 | Treats "fifteen days … six weeks" as *Lalita Kumari*'s 111(vii)/120.7. States that the SC numbering "probably follows the SCC report". |
| `reports/section_173_3_legal_review_handoff.md` (L-C questions; dossier QR-C2, QR-C4) | Refers to the fifteen-day / six-week direction |
| `reports/section_173_3_boundary_impact.md` §4 D-6 | Quotes 120.7 (fifteen days / six weeks) |
| `reports/source_verification_matrix.md` §5 (RB-02 summary row); `reports/source_verification_summary.md` §C (RB-11 note) | Cite LK-MPHC para 111(vii), "fifteen days … six weeks" |
| `legal_engine/schedule_registry.py` `BNSS_173_3_CAVEAT_TEXT` | Cites "(2014) 2 SCC 1" with no paragraph number and no time limit. **No code impact unless reviewers change the citation.** |

---

## B. Pending Supreme Court matter: *Azad Singh Kataria v. Union of India*, W.P.(Crl.) No. 461/2024

### B.1 What the official records establish

All records below are from the Supreme Court's own host, TLS verified.

| Date | Record | Content (as printed) |
|---|---|---|
| 22-11-2024 | Record of Proceedings, Court No. 3, Item 9, Section PIL-W, "(FOR ADMISSION)". Coram: Surya Kant J., Ujjal Bhuyan J. `api.sci.gov.in/supremecourt/2024/48206/48206_2024_3_9_57398_Order_22-Nov-2024.pdf`, SHA-256 `e416496a41be6c54ba5bf5d4a6367aa0827a777c47a4322ef49cddd8c6346fbf` | "List on 02.12.2024." |
| 03-12-2025 | Record of Proceedings, Court No. 1, Item 21, PIL-W. Coram: CJI, Ujjal Bhuyan J., N. Kotiswar Singh J. Annotation: "[ONLY W.P. (C) NO. 39/2025 IS LISTED UNDER THIS ITEM]". SHA-256 `9b0c9048…588f` | "List on 11.12.2025 along with all the connected matters." |
| 27-02-2026 | Record of Proceedings, Court No. 1, Item 31. Coram: CJI, Joymalya Bagchi J. Connected matters: W.P.(C) 625/2024; W.P.(Crl.) 444/2024, 57/2025, 40/2025, 39/2025; Diary No. 57373/2024. Pending IAs include interim relief (16331/2025, 26124/2025) and a stay application (17495/2025). SHA-256 `234ea6c7…0d27d` | "List on 15.05.2026." |
| **15-05-2026 (latest official record found)** | Daily cause list, Chief Justice's Court, `api.sci.gov.in/jonew/cl/2026-05-15/M_J_1.pdf`, SHA-256 `a593d23332bb2ec70ae43be74b9103bef17591801168a27882215b8b598e8c8f` | Under "PUBLIC INTEREST LITIGATIONS": "113 W.P.(Crl.) No. 461/2024 PIL-W AZAD SINGH KATARIA … Versus UNION OF INDIA", with "Connected W.P.(C) No. 625/2024 … MANNARGUDI BAR ASSOCIATION … Versus UNION OF INDIA AND ORS. FOR ADMISSION". |

**Not found:**
- any order dated 15-05-2026 or later: two web searches on the case's order path, and a search of 2026 cause lists, found nothing;
- the petition and its prayers;
- any order saying that notice was issued, which provisions are challenged, or what interim relief (if any) was granted.

**The official records establish only:**
- the case exists, in the PIL-W section, "for admission";
- the connected matters listed above;
- the benches and listing dates above;
- that it was listed on 15 May 2026.

**They do not establish** which provisions are challenged, or the matter's current status after 15 May 2026.

### B.2 What secondary reporting says (not relied on)

- LiveLaw (updated 28 Feb 2026) reports: "One of the provisions under challenge was Section 173 of the BNSS".
- Search summaries of LiveLaw and Bar & Bench coverage also mention BNS s.152, and BNSS ss.43(3), 107, 223 and 356 in the connected Mannargudi Bar Association petition.

**These descriptions are unverified.** The petition's scope must not be inferred from them.

---

## C. Maharashtra legislation

### C.1 BNSS amendment bills (six weeks in s.173(3)(i))

| Item | Status |
|---|---|
| L.C. Bill No. VI of 2026 (clause 6) and L.C. Bill No. XVII of 2026 (clause 7) | Passed by the Legislative Council on 24 Mar and 8 Jul 2026 respectively. Bill XVII was published in the Maharashtra Gazette (Part VIII, Ext. 81, 3 Jul 2026). |
| Enactment | **UNKNOWN.** The official Maharashtra e-Gazette (Parts IV and VIII, 1 Jan to 21 Oct 2026) shows **no** BNSS amendment Act or Ordinance; the latest Act listed is No. LIV of 2026 (6 Oct 2026). Assembly passage, assent and commencement are not shown in any record found. **Not law.** |

### C.2 BNS amendment bill (ss.72 and 75)

| Item | Status |
|---|---|
| L.A. Bill No. XXX of 2026, "Bharatiya Nyaya Sanhita (Maharashtra Amendment) Act, 2026" | The Legislature Secretariat copy is headed "(As passed by the Legislative Assembly on the 25th March, 2026.)" and "(As passed by the Legislative Council on the 25th March, 2026.)" (SHA-256 `3afa7dac…5c16`). Bill published in the Gazette, Part VIII, Ext. No. 41, 25 Mar 2026. |
| Content (bill text, not law) | Clause 2: insert "or section 124" in s.72(1). Clause 3: add clauses (v)–(viii) to s.75(1), and reference them in s.75(2). |
| Enactment | **No verified enactment evidence.** No Act was found in the Gazette Parts IV and VIII searches up to 21 Oct 2026, and no 2026 Act text in the Bombay High Court mirror mentions the "Nyaya Sanhita". **Status UNKNOWN; not law. Corpus text is unchanged.** |

### C.3 Official records needed (both bills)

None of the three bills' extracted texts contains a commencement sub-clause; clause 1 gives the short title only. **When such an Act would take effect is a legal question for the QLR.** The evidence needed is:

1. **Assembly passage** (L.C. Bills VI and XVII): a Legislature Secretariat record, i.e. the bill "as passed by both Houses", the proceedings, or a certified status.
2. **Assent:** whether the Governor assented, or the bill was reserved for the President's consideration (arts. 200–201; whether reservation was required is a QLR question), and the date. Sources: the Law and Judiciary Department; the Legislature Secretariat; for reserved bills, the record of the President's decision.
3. **Act number and Gazette publication:** the Maharashtra Government Gazette, Part IV (Marathi) and Part VIII (English translation). An Act's header carries the line "First published, after having received the assent of the Governor [or President] in the 'Maharashtra Government Gazette', on …", as in Maharashtra Act No. LIII of 2026.
4. **Commencement:** any commencement notification in the Gazette, or, if none, the facts the QLR needs (publication date) to determine commencement.
5. **Enacted text:** for the SC to compare with the bill clauses.

---

## D. Decision register

Roles are those in `reports/reviewer_assignment_template.md`. **All roles are unfilled.** Every decision below is blank and unapproved.

| ID | Finding | Evidence available | Evidence missing | Question for QLR 1 / QLR 2 (ADJ on disagreement) | Responsible | Blocks | Next action → closure evidence |
|---|---|---|---|---|---|---|---|
| **T-1** | *Lalita Kumari* direction (vii): the 2013 text says 7 days; the reported 2014 modification says 15 days / six weeks | Official 2013 judgment and S.C.R. (A.1); official Delhi High Court order referring to the 5 Mar 2014 order; secondary reports | The Supreme Court's own copy of the 5 Mar 2014 order; an SC check of both texts | Which text of direction (vii) is the operative *Lalita Kumari* direction to cite: the 2013 text, the modified direction, or both with explanation? Does either bear on BNSS s.173(3)? (This builds on QR-C2.) | **SC** (verify first); **SAO** (obtain the order); **QLR 1, QLR 2, ADJ** | Any citation of *Lalita Kumari* time limits in reports, the caveat or the handoff (QR-C2, D-6). **Does not block** Changes A or B, which do not cite *Lalita Kumari*. | SAO obtains the order from the Supreme Court → SC compares → QLR decision recorded on the handoff §7 form. **Closure:** official order text plus a signed SC comparison plus a QLR decision |
| **T-2** | *Lalita Kumari* paragraph numbering: official 110/111; later judgments cite 119/120 with (2014) 2 SCC 1 | Official copy and S.C.R. (110/111); SC-IP and SC-AD PDFs (119/120) | The SCC report; an SC check | Which paragraph references should Bandhoo's records use: the official 111, SCC numbering (once verified), or both, stated explicitly? | **SAO** (SCC report); **SC**; **QLR** | Citation wording only (RB-02; QR-C4) | SAO obtains (2014) 2 SCC 1 → SC maps the paragraph numbers → QLR decides. **Closure:** a mapping table signed by the SC, plus a QLR decision |
| **T-3** | *Kataria* W.P.(Crl.) 461/2024, pending; s.173 reportedly challenged | Official orders 22-11-2024, 03-12-2025, 27-02-2026; cause list 15-05-2026 (B.1) | The petition and prayers; any order on or after 15-05-2026; current status | (a) Does the pendency of this matter affect how Bandhoo should describe s.173(3)? (b) Should any s.173(3) decision (D-1 to D-3, Change B) pause until its current status is known? (c) Does any interim order (if one exists) matter? | **SAO** (status, petition, orders); **QLR 1, QLR 2, ADJ** | Potentially D-1 to D-3, Change B and the caveat wording (QLR to decide). Release: recommended as a **release-gating check**, since a ruling on s.173 could change the law Bandhoo describes. | SAO obtains the case status and the orders after 27-02-2026 from the Supreme Court portal, plus the petition copy → QLR records a decision on pause or no pause. **Closure:** a dated official status record plus a QLR decision |
| **T-4** | Maharashtra BNSS amendment (six weeks) | Bills VI and XVII (Council passage); Gazette search showing no Act up to 21 Oct 2026 | Assembly passage, assent, Act number, publication, commencement (C.3) | Once evidence exists: the legal effect in Maharashtra, and the date of effect; whether Bandhoo's "fourteen days" needs a Maharashtra qualification (QR-B4) | **SAO**; **SC**; **QLR**; **PO** (wording approval) | Q-01 Step 2. Informs Change B review (QR-B4) but does not block Change B, which keeps "fourteen days". Release for Maharashtra users: recommended as a release-gating check. | SAO obtains the C.3 records, or a written status from the Law and Judiciary Department → SC compares the text → QLR decides. **Closure:** official Gazette Act and commencement evidence, or an official written status, plus a QLR decision |
| **T-5** | Maharashtra BNS amendment (ss.72, 75) | L.A. Bill XXX "as passed" by both Houses (25 Mar 2026); Gazette bill publication; no Act found | Assent, Act number, publication, commencement (C.3) | Once evidence exists: the effect on BNS ss.72 and 75 as applied in Maharashtra, and whether Bandhoo's corpus or advice needs a jurisdiction note | **SAO**; **SC**; **QLR**; **PO** | Not the s.173(3) review. Release: corpus accuracy for Maharashtra (RB-03). Corpus text is not to change until enactment is verified (path A/B per the protocol). | As T-4. **Closure:** official Act and commencement evidence plus an SC text comparison plus a QLR decision on the corpus |

---

## E. Recommendations and change control

1. **Verify before relying.** The SC should check T-1 (direction (vii) in the 2013 copy, the S.C.R., the Manupatra print and the SC-IP/SC-AD quotations) and T-2 (numbering) **before** the QLRs use any *Lalita Kumari* passage. Add this to the SC's G-1 scope (log G-1, step 6).
2. **QLR decisions requested:** T-1 and T-2 (which version and which paragraph references to cite); T-3 (effect of *Kataria* and whether to pause); T-4 and T-5 only once evidence exists.
3. **Separate gates (unchanged):**

   | Item | Affected by T-1 to T-5? |
   |---|---|
   | Change A (RB-52 / Q-16) | No. It concerns missing registry data, not the case law. |
   | Change B (Q-01 Step 1 / Q-17 Step 1) and the RB-53 route | Possibly by T-3 (QLR to decide). T-4 informs QR-B4. |
   | D-1 to D-3 (RB-09, RB-10, RB-13) | Possibly by T-3 (QLR to decide) |
   | Q-01 Step 2 (Maharashtra) | Blocked by T-4 |
   | *Lalita Kumari* caveat and citation wording (RB-02, RB-11) | T-1, T-2 |

4. **Recommended register and queue entries.** These are **not** added; the PO approves or declines each.

   | Proposed ID | Type | Proposed text | Status if registered |
   |---|---|---|---|
   | RB-02.a | Register, class M / I | *Lalita Kumari* 2013 direction (vii) "7 days" versus the reported 5 Mar 2014 modification ("15 days / six weeks"); official numbering 110/111 versus the 119/120 cited later; Supreme Court copy of the 2014 order and the SCC report not obtained. Closure: T-1 and T-2 closure evidence. | Open |
   | RB-54 | Register, class M | Pending Supreme Court matter, *Azad Singh Kataria v. Union of India*, W.P.(Crl.) 461/2024; official orders to 27-02-2026 and listing on 15-05-2026; scope and current status unverified. Closure: official current status, plus a QLR decision on its effect and on any pause. | Open |
   | RB-03.a | Register, class M | Maharashtra L.A. Bill XXX of 2026 (BNS ss.72, 75) passed by both Houses on 25-03-2026; enactment unverified. Closure: T-5 closure evidence. | Open |
   | (RB-03, existing) | Register | Record the 2026-10-21 Gazette search result for L.C. Bills VI and XVII as a dated addendum; status stays UNKNOWN | Open (unchanged) |
   | Q-18 | Queue | "*Lalita Kumari* citation and caveat wording." Only after the T-1/T-2 QLR decisions. Location: `BNSS_173_3_CAVEAT_TEXT` and the report texts in A.3. Path B. | Blocked |
   | — | Queue | **No entry recommended** for T-3, T-4 or T-5 until evidence exists. There is no correction to queue yet. | — |
   | — | Matrix and summary | Dated addenda recording G-BNSS/G-BNS Gazette provenance (log G-3) and the T-1/T-2 facts, after SC verification | — |

5. **Unchanged by this triage:**
   - every RB entry remains **Open** and every Q entry **Blocked**;
   - no source-verification record, dossier, handoff, readiness plan or log is edited;
   - no corpus, code, prompt, test, label or threshold is changed.
