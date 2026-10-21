# BNSS Section 173(3): Review Readiness — Reviewer Appointment and Source-Verification Plan

**Prepared:** 2026-10-21 by the Bandhoo maintainer session, for the project owner (PO) and the people the PO appoints.
**Builds on:**
- `reports/section_173_3_legal_review_handoff.md` (the "handoff");
- `reports/section_173_3_case_law_review_dossier.md` (the "dossier");
- `reports/reviewer_assignment_template.md` (the "template");
- `reports/source_verification_matrix.md` §11;
- `reports/legal_review_execution_checklist.md` Stage 1.

**Status:** planning document only. No one has been appointed. No source has been newly obtained. No decision, approval or implementation is recorded here. The template is **not** edited, and its approval block stays blank. Bandhoo remains internal-testing-only.

---

## A. Reviewer appointment

### A.1 The six roles (as defined in the template)

The template's rules (Part 1) apply to every role:
- the PO confirms or amends the proposed qualifications before anyone is appointed;
- qualification evidence means a document the PO has actually seen;
- conflicts are declared before work starts;
- appointment changes are added as new dated entries, never overwritten;
- no personal documents or unnecessary contact details are stored in the repository.

| Role | Proposed minimum qualification (template) | Responsibilities for the s.173(3) review | Independence requirement | Assignment fields to complete (template) |
|---|---|---|---|---|
| **QLR 1**: Qualified Legal Reviewer 1 (§2.1) | Advocate enrolled with an Indian State Bar Council, with criminal-law practice including BNS/BNSS matters; no involvement in Bandhoo development | Answers handoff §4.1 (L-A1 to L-A3, L-B1 to L-B4, L-C1 to L-C4) independently, on the handoff §7 form | Not QLR 2 or the ADJ; no contribution to Bandhoo's code, prompts, corpus or benchmark labels | Name; Bar Council and enrolment (as confirmed by PO); qualification evidence seen by PO (document, date seen); relevant experience (self-declared); independence and conflict declaration; scope assigned; items excluded because of conflict; date appointed; appointee signature and date; PO approval |
| **QLR 2**: Qualified Legal Reviewer 2 (§2.2) | Same as QLR 1, and independent of QLR 1 | Same questions, answered **without** seeing QLR 1's answers | As QLR 1, plus a declaration of independence from QLR 1 | As QLR 1, plus "Independence from QLR 1 (declaration)" |
| **ADJ**: Adjudicator (§2.3) | Senior criminal-law practitioner or academic; not QLR 1 or QLR 2 | Decides any question where QLR 1 and QLR 2 disagree ("Disputed (to ADJ)"). If the ADJ cannot resolve it, nothing changes and Bandhoo keeps its uncertainty-preserving behaviour. | Not QLR 1 or QLR 2; no Bandhoo involvement | Name; position or standing (as confirmed by PO); qualification evidence seen by PO; independence from QLR 1 and QLR 2; independence and conflict declaration; date appointed; appointee signature and date; PO approval |
| **SC**: Second statutory-source checker (§2.4) | A careful reader independent of the change author; text comparison only | Gap G-1: checks the dossier's quotations, page and paragraph references and emphasis against the official PDFs. Also compares any newly obtained source copy (G-2 to G-5) with the project's current copy. Makes **no** legal judgment. | Must not be the author of the change or record being checked. **Note:** the dossier was prepared by the Bandhoo maintainer session, so the SC must be someone other than its author. | Name; relationship to Bandhoo development (declaration); scope assigned; date appointed; appointee signature and date; PO approval |
| **EL**: Evaluation Lead (§2.5) | Not a Bandhoo developer | Gap G-6: designs and runs any approved live Gemini evaluation under `reports/independent_evaluation_plan.md`. Needed for RB-53 closure route (ii) and RB-46. | Not a Bandhoo developer | Name; relevant evaluation experience (self-declared); independence and conflict declaration; **live-evaluation budget approved by PO (amount, date)**; date appointed; appointee signature and date; PO approval |
| **SAO**: Source-acquisition owner (§2.6) | Not set in the checklist; **to be set by the PO**. Template suggestion: able to obtain official or certified copies from India Code, the e-Gazette, the Maharashtra Government Gazette and the Supreme Court. | Gaps G-2 to G-5: obtains official copies and records provenance, version or "as on" date, and SHA-256. Records searches that found nothing, with what was searched and when. | None specified in the template. The PO may add one. | Name; access arrangements (e.g. library, certified-copy request); scope assigned (S1 step IDs); target date; date appointed; appointee signature and date; PO approval |

**Who appoints:** the **project owner** appoints and approves **all six roles** (template Part 1 rule 1; Part 3). The PO's own name is also blank in template Part 3.

Two further roles in `reports/legal_review_execution_checklist.md` (Roles table) are not among the six template roles and are also unassigned:
- **MNT**: the maintainer; technical approval and implementation;
- **PO**: the approval authority for user-facing changes, the live-evaluation budget and release decisions.

The PO should confirm who holds each of these.

### A.2 Appointment checklist (for the PO)

1. Record the PO's own name in template Part 3. Confirm or amend the proposed qualifications in Part 2, and **set** the SAO qualification.
2. Identify candidates for QLR 1, QLR 2 and ADJ: three different people, none involved in Bandhoo development.
3. See each legal reviewer's qualification evidence. Record the document and the date seen; do not store copies.
4. Obtain each appointee's independence and conflict declaration before any work. Record any excluded items.
5. Appoint an SC who did not author the dossier or any record they will check.
6. Appoint an SAO, and record their access arrangements and target dates.
7. Appoint an EL, or record that live evaluation is deferred. If appointing, approve a live-evaluation budget.
8. Assign each person's scope by ID: RB-52/Q-16, RB-53/Q-17, RB-09/RB-10/RB-13 (D-1 to D-3), and the S1 steps in §B.
9. Each appointee signs their entry. The PO signs Part 3 and adds a dated row to the Part 4 assignment log.
10. Tell the MNT that appointments are complete. Stage 2 rows for RB-52 and RB-53 can then be added to the checklists (handoff §7).

### A.3 Completion table (blank; to be completed only by the PO and the appointees)

Tick a column only after the matching entry exists in `reports/reviewer_assignment_template.md`.

| Role | Name recorded in template | Qualification evidence seen by PO | Independence / conflict declared | Scope assigned | Appointee signed | PO approved | Date |
|---|---|---|---|---|---|---|---|
| QLR 1 | ____ | ____ | ____ | ____ | ____ | ____ | ____ |
| QLR 2 | ____ | ____ | ____ | ____ | ____ | ____ | ____ |
| ADJ | ____ | ____ | ____ | ____ | ____ | ____ | ____ |
| SC | ____ | n/a | ____ | ____ | ____ | ____ | ____ |
| EL | ____ | n/a | ____ | ____ | ____ | ____ | ____ |
| SAO | ____ | ____ (if the PO sets a qualification) | ____ | ____ | ____ | ____ | ____ |

**Current state (2026-10-21):** every role is **Pending: not appointed**. PO approval is **not given**.

---

## B. Source-verification plan

### B.1 Status vocabulary

| Status | Meaning |
|---|---|
| **Available, not yet checked** | The project holds the document, but no independent check has been made |
| **Sought, unavailable** | A retrieval attempt failed (access error, blocked host, no response). Says nothing about the content. |
| **Searched, not found** | Specific sources were searched and the item did not appear. **Not proof that it does not exist.** |
| **Not yet sought** | No search made |
| **Not generated** | Evidence that must be produced (e.g. live output), deliberately not created |

### B.2 Gaps, in priority order

Priority reflects what each gap blocks:
- **G-1** gates any reliance on the judgments.
- **G-2** governs whether Bandhoo's "fourteen days" is right for Maharashtra users.
- **G-3** and **G-5** bear on D-1 to D-3.
- **G-4** bears on the caveat and RB-02/RB-11.
- **G-6** is needed only for RB-53 closure route (ii).

#### G-1. Second-checker verification of the judgment quotations (priority 1)

| Field | Content |
|---|---|
| Current status | **Available, not yet checked.** Both PDFs were retrieved from `api.sci.gov.in` with TLS verified, and twice gave identical SHA-256 values (dossier §1). Quotations were transcribed from `pypdf` text extraction. The emphasis marked by the Court is not visible in that extraction. |
| Question to resolve | Does each quotation in dossier §3.3, §4.3 and §5.1 match the official PDF word for word, with the stated PDF page and paragraph? Which words did the Court emphasise in the passages marked "[Emphasis supplied]" / "(emphasis added)"? |
| Preferred source | The official PDFs: *Imran Pratapgadhi*, 2025 INSC 410 (SHA-256 `896f08f97519248a7f004350d43b72ffc296144e817c0be8b0365bd28f0d5a58`), and *Ashish Dave*, 2026 INSC 244 (SHA-256 `3350c58215253837483fbe01397717b841f08cbb25ac2d5cbfb31edaff81bc0b`), at the URLs in dossier §1 |
| Acceptable alternatives | A certified copy from the Supreme Court Registry. The SCC report (2026) 1 SCC 721 for *Imran Pratapgadhi* (paragraph numbering may differ; record which is used). |
| Verification method | (1) Download again and confirm the SHA-256. (2) Open in a PDF viewer, not a text extractor. (3) Compare each quotation; record every difference, including punctuation, and the emphasised words. (4) Confirm page and paragraph numbers. (5) Record the result against the dossier section, without legal comment. |
| Responsible | **SC**. QLR 1 and QLR 2 rely on the result. |
| Blocks | Reliance on SC-IP / SC-AD for L-C1 to L-C4 (D-1 to D-3). Does not block the statutory-text questions for Changes A and B. |

#### G-2. Maharashtra enactment and commencement evidence (priority 1)

| Field | Content |
|---|---|
| Current status | **Searched, not found** in the sources checked. Enactment status is **UNKNOWN**. Maharashtra L.C. Bill VI of 2026 was passed by the Legislative Council on 24 Mar 2026, and L.C. Bill XVII of 2026 on 8 Jul 2026 (each would substitute "six weeks" for "fourteen days" in s.173(3)(i)). The Bombay High Court library's Maharashtra Acts I–LIII of 2026 (the latest first published 13 Aug 2026) contained no BNSS amendment Act (checklist S1-3). No Assembly passage, assent, Act number, Gazette publication or commencement was found. The **official records themselves were not obtained**. Neither bill is treated as law. |
| Question to resolve | Was either bill enacted? If so: the Maharashtra Act number; the date and form of assent (whether the Governor's or the President's is legally required is for the QLR); the date of Gazette publication; the commencement date or notification; and which bill text was enacted. If not: the status as on the date checked, with the source. |
| Preferred source | The Maharashtra Government Gazette publication of any such Act and any commencement notification; the Law and Judiciary Department, Government of Maharashtra; and Maharashtra Legislature Secretariat records of passage by both Houses |
| Acceptable alternatives | A certified copy from the Law and Judiciary Department. India Code's state-legislation section, if accessible and showing an "as on" date. The Bombay High Court library mirror is acceptable for **locating** an Act; confirm against the Gazette. News reports and PRS bill pages are **leads only**. |
| Verification method | The SAO records each source searched, the date and the result, including "not found". The SC compares any Act text with the bill clauses (L.C. VI clause 6; L.C. XVII clause 7). The QLR decides the legal effect and the assent route. **No conclusion on enactment is recorded without an official document.** |
| Responsible | **SAO** (acquisition); **SC** (comparison); **QLR** (effect) |
| Blocks | Q-01 Step 2. It also informs whether Change B's "fourteen days" needs a Maharashtra caveat (handoff L-B questions; QR-B4). |

#### G-3. Second official BNSS copy, including the First Schedule (priority 2)

| Field | Content |
|---|---|
| Current status | **Sought, unavailable.** India Code returned an error page or HTTP 403 on 2026-10-20 and 2026-10-21. The project holds one PRS-hosted Gazette copy. There are partial official-host reproductions of s.173: quoted in full in SC-IP p.18 and SC-AD pp.14–15, and s.173(3)(i) in the Maharashtra L.C. Bill VI extract. These are quotations, not copies of the Act (checklist S1-2). Central amendments and corrigenda after 25 Dec 2023: **searched, not found** (S1-3); this is not proof that none exist. The BNS punishment terms used in the boundary analysis (ss.57, 308(2), 318(4), 351(2)) also rest on one PRS copy (S1-1). |
| Question to resolve | Is the text of BNSS ss.173(1)–(4), 174 and 175 the same in an official current copy? Are the Schedule I rows for 117, 305, 306, 308(2), 316, 318 and 351 the same? Has any central amendment or corrigendum changed them since 25 Dec 2023? |
| Preferred source | India Code (current text with "as on" date). The Gazette of India e-Gazette (original Act No. 46 of 2023, and any amending Act or corrigendum). Ministry of Law and Justice, Legislative Department. |
| Acceptable alternatives | A certified copy. **Commercial bare-act editions and secondary websites are not acceptable as a second authoritative copy.** |
| Verification method | The SAO records the source, version or "as on" date, and SHA-256. The SC compares the listed provisions and rows with the PRS copy and records differences. Any difference is referred to the QLR, never corrected directly. |
| Responsible | **SAO**, **SC** |
| Blocks | Closure of RB-03. Confidence in L-B1 and L-C1. Not strictly required to answer L-A1 to L-A3. |

#### G-4. Official *Lalita Kumari* judgment and SCC report (priority 3)

| Field | Content |
|---|---|
| Current status | **Sought, unavailable** from an official host. No Supreme Court-hosted PDF was found. The project holds a Manupatra print hosted on mphc.gov.in (TLS **not** verified) and the quotations in SC-IP para 22 (para 120) and SC-AD para 22 (para 119). The SCC volume (2014) 2 SCC 1 was not inspected. A neutral citation "2013 INSC 748" and "[2013] 14 S.C.R. 713" were seen only in a search-result description, which is a lead (S1-4). |
| Question to resolve | Confirm the citation and the coram. Which numbering is authoritative: SCC 119/120 or the print's 110/111? Is the text of the conclusions (120.1–120.8) the same as in the official copy? |
| Preferred source | The Supreme Court of India's official judgment record for W.P. (Crl.) No. 68 of 2008, decided 12.11.2013, and the SCC report (2014) 2 SCC 1 |
| Acceptable alternatives | A certified copy from the Supreme Court Registry. The Supreme Court Reports (S.C.R.) from an official publisher, once its citation is confirmed. |
| Verification method | The SAO obtains it; the SC compares it with LK-MPHC and with the quotations in SC-IP and SC-AD (dossier §5.1); the QLR uses the confirmed numbering |
| Responsible | **SAO**, **SC**; QLR for use |
| Blocks | RB-02 and RB-11 (caveat wording). Peripheral to Changes A, B and C. |

#### G-5. High Court (and any further Supreme Court) decisions on BNSS s.173(3) (priority 2)

| Field | Content |
|---|---|
| Current status | **Not yet sought** (S1-5). Only the two Supreme Court decisions were obtained. |
| Question to resolve | Has any court analysed: (a) whether "less than seven years" includes a maximum of exactly seven years; (b) per-offence or per-case application where several offences are alleged; (c) the fourteen-day period and DSP permission; (d) vague complaints? Has any decision considered the different treatment of seven-year offences in SC-IP para 28 and SC-AD para 25? |
| Preferred source | Official court websites: Bombay High Court judgments; other High Courts as relevant; the Supreme Court's website; and the eCourts judgments service |
| Acceptable alternatives | Recognised law reports (e.g. SCC, Cri LJ, Bom LR), used by the QLR to **identify** decisions. Each relied-on decision should then be obtained from an official source. Blogs and news summaries are leads only. |
| Verification method | The QLRs define the search (they decide relevance). The SAO obtains official copies with SHA-256. The SC checks the quotations. Each QLR records which decisions were considered on the handoff §7 form. |
| Responsible | **QLR 1 and QLR 2** (search scope and relevance), **SAO**, **SC** |
| Blocks | D-1 to D-3 (handoff L-C1 to L-C3, especially L-C2) |

#### G-6. Live Gemini output (priority 3; needed only for RB-53 route (ii))

| Field | Content |
|---|---|
| Current status | **Not generated.** This was deliberate: no live call has been made in any recent round. The only live report (5 cases) is stale (RB-46). Probe results used **simulated** Gemini text and show only what the code does with such text. |
| Question to resolve | How often does genuine Gemini output contain the line-59 timing wording, or describe enquiry timing without "173(3)" (RB-53 routes (a) and (b))? After any approved Change B, does it still occur? |
| Preferred source | An approved live evaluation under `reports/independent_evaluation_plan.md`: a PO-approved budget, mode-separated reporting (genuine live versus cached versus mocked), and the outputs retained for review |
| Acceptable alternatives | **None for live behaviour.** Cached and mocked outputs are not evidence of current Gemini behaviour. |
| Verification method | The EL defines the cases and the measure (e.g. occurrences of a "permission … within 14/fourteen days" pattern, and uncited enquiry-timing text). The MNT runs the evaluation only after PO approval. QLR 1 and QLR 2 review the flagged outputs. |
| Responsible | **EL**, with **PO** approval and budget; MNT executes; QLR reviews |
| Blocks | RB-53 closure route (ii) only. Route (i), a separately approved check fix, does not need it. |

### B.3 Gaps that cannot be resolved without an appointed owner or authoritative access

**All six.** None can be resolved by the maintainer session alone.

| Gap | Blocked on |
|---|---|
| G-1 | An appointed SC independent of the dossier's author |
| G-2 | An SAO with access to the Maharashtra Government Gazette or Law and Judiciary Department records. The mirror search cannot settle enactment status. |
| G-3 | Access to India Code or the e-Gazette (blocked from this environment), or a certified copy; plus an SC |
| G-4 | Access to the Supreme Court's official record or the SCC volume; plus an SC |
| G-5 | QLRs to define relevance, and access to official judgment sources |
| G-6 | An EL, a PO-approved budget and live-evaluation approval |

---

## C. Review sequence

### C.1 Order (applies to each change separately)

1. **Appoint reviewers** (§A): PO.
2. **Verify sources independently** (§B): SC for G-1 before the QLRs rely on the judgments; SAO and SC for G-2 to G-5 as each becomes available.
3. **Make independent legal decisions:** QLR 1 and QLR 2 answer the handoff §4.1 questions separately, on the handoff §7 form.
4. **Adjudicate disagreements:** the ADJ. If unresolved, no change is made.
5. **Approve implementation:** the MNT gives technical approval of the exact change; the PO approves any user-facing change. Recorded in a change record (`reports/post_review_change_protocol.md` §3).
6. **Implement only approved changes:** one issue per change, after a fresh snapshot and manifest.
7. **Run checks:**
   - acceptance tests that fail before and pass after (gate 5);
   - regression tests: full offline suite with Gemini disabled (gate 6);
   - benchmark comparison with `--out` to a scratch path, case by case, with no relabelling (gate 7);
   - side-effect review (gate 8);
   - rollback record (gate 9).

**Scratch dry runs are not implementation validation.** The dry runs in `reports/section_173_3_remediation_proposal.md` §5 were run on copies outside the repository, before any approval. They show feasibility only. Step 7 must be done again, and recorded, on the approved implementation.

### C.2 Separate gates per change

| Change | Legal questions (handoff §4.1) | Source prerequisites | Implementation approval | May proceed independently of |
|---|---|---|---|---|
| **A** (RB-52 / Q-16) | L-A1 to L-A3 | None beyond the registry. G-1 is not required. | MNT + PO | B, RB-53 check fix, C, Maharashtra |
| **B** (Q-01 Step 1 / Q-17 Step 1) | L-B1 to L-B3 | Statutory text: PRS copy plus official-host quotations. G-3 recommended. G-2 status to be noted by reviewers (QR-B4). | MNT + PO | A, C. Must **not** introduce "six weeks". |
| **RB-53 closure** (check fix or route (ii)) | L-B4 | Route (ii) requires G-6 | Separate proposal and approval (route (i)), or a QLR + PO decision plus live evidence (route (ii)) | A, C |
| **C** (D-1 to D-3, L-C4; RB-09, RB-10, RB-13) | L-C1 to L-C4 | G-1 required. G-5 and G-3 strongly recommended. | Only after decisions; then one coordinated change (proposal §C.3) | A, B |
| **Maharashtra** (Q-01 Step 2) | QR-B4 (after evidence) | G-2: official enactment **and** commencement evidence | QLR + PO, after G-2 | — |

### C.3 Status (unchanged by this document)

| Item | Register | Queue |
|---|---|---|
| RB-52 | Open | Q-16 Blocked |
| RB-53 | Open | Q-17 Blocked |
| RB-08, RB-08.a | Open | Q-01 Blocked (Steps 1 and 2) |
| RB-09, RB-10, RB-13 | Open | No implementation entry. Decision only. |
| RB-03 | Open | Q-01 Blocked (Maharashtra status recorded under RB-03) |
| RB-02, RB-11 | Open | No queue entry |
| RB-46 | Open | Q-15 Blocked |

All blockers remain **Open**, and all correction-queue entries remain **Blocked**.
