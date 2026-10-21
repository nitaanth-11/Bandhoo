# Bandhoo Source Verification Summary

**Prepared:** 2026-10-20. **Companion to:** `reports/source_verification_matrix.md`, which has the full passages, IDs and closure criteria.

**Bandhoo remains internal-testing-only.** Nothing in this summary is a legal verification.

## Read this first: three different things

| Term | Meaning |
|---|---|
| **Textual match** | Bandhoo's stored text or claim agrees with one inspected copy of a source. It does **not** make the claim legally correct: the copy may be outdated or amended, and the claim may be applied wrongly. |
| **Textual discrepancy** | Bandhoo's text differs from the inspected copy. It is **not** proof of a legal error: the copy itself may contain a printing or extraction fault, or Bandhoo may be quoting a different version. |
| **Legally incorrect statement** | Can only be established by a qualified Indian criminal-law reviewer, ideally against more than one authoritative source. **No item has reached that stage.** |

## Sources actually inspected (2026-10-20)

1. **BNS 2023 (No. 45 of 2023)**, Gazette of India Extraordinary, 25 Dec 2023: PRS-hosted PDF, extracted with `pypdf`.
2. **BNSS 2023 (No. 46 of 2023)** including the First Schedule, same date: PRS-hosted PDF.
3. **Consumer Protection Act, 2019 (No. 35 of 2019)**, [9th August, 2019]: PRS-hosted PDF.
4. **Lalita Kumari v. Govt. of U.P. and Ors.**, WP (Crl.) 68 of 2008, decided 12.11.2013: a Manupatra print (MANU/SC/1166/2013) hosted on the Madhya Pradesh High Court website. Its TLS certificate could not be verified, so it was downloaded with verification disabled.

**Not obtained:**
- India Code copies of the BNS, BNSS and CPA (HTTP 403 or error page);
- the Supreme Court's own copy and the SCC report of *Lalita Kumari*;
- any amendment record after 25 Dec 2023;
- any source for the "Legal Metrology Department" referral.

Bandhoo's own corpus was not used as authority for anything.

## A. Text directly checked against the single available copy

### A.1 Matches (textual match only)

| ID | Item |
|---|---|
| LR-03 / LR-09 | BNS 303(2) punishment and proviso wording; BNSS Schedule rows for 303(2), including the "less than 5,000 rupees … community service … Non-cognizable. Bailable." row. |
| RB-08 / LR-11 | Elements of Bandhoo's Section 173(3) paraphrase: cognizable; three years or more but less than seven; prior DSP permission; nature and gravity; preliminary enquiry within fourteen days, or investigation. **Not reproduced:** "without prejudice to the provisions contained in section 175". |
| RB-10 / LR-13 | BNSS 174(4) deeming text. |
| LR-16 | BNSS 174(1)–(2) as used in templates ("NCR register" is Bandhoo's informal label). |
| RB-02 / LR-14 | The citation "(2014) 2 SCC 1" appears in the equivalent-citation list of the Manupatra print. Bandhoo's one-line summary matches para 111(i) of that print: "Registration of FIR is mandatory under Section 154 of the Code, if the information discloses commission of a cognizable offence and no preliminary inquiry is permissible in such a situation." **The SCC report itself was not inspected.** |
| RB-17 / LR-18 | Registry classification rows for the 14 sections (developer transcription). |
| LR-16 | Robbery template punishment figures (309(4): 10 years; 14 on a highway between sunset and sunrise); Section 314 classification. |
| RB-37 to RB-44 | Statutory statements relied on in the provisional-case label reviews: s.310(1) five or more persons; s.311 "uses any deadly weapon"; s.62 Schedule row (bailability follows the offence attempted); s.134 and its row (cognizable, bailable); s.305(a); s.306; s.316(1) entrustment. |
| RB-04.a | Consumer Protection Act, 2019 establishes District, State and National Consumer Disputes Redressal Commissions (ss.28, 42, 53). Section 2(6)(iv) covers complaints of charging more than a price fixed by law, displayed, or agreed. |
| RB-05 / LR-25 | The 15 corpus corrections of 2026-10-20 (machine-checked transcription). |
| RB-30 / LR-27 | Sections 2, 4, 32 and 54 contain no punishment clause. |

### A.2 Discrepancies observed (textual; not proof of legal error)

| ID | Stored or claimed | Inspected copy |
|---|---|---|
| RB-23 / LR-17 | Template cites "Section 2(22)" for movable property | "(21) "movable property"…"; (22) is "number". |
| RB-18 / LR-01 | s.115(2) "section 120" | "section 122". |
| RB-19 / LR-02 | s.117(2) "sub-section (3)"; s.117(4) omits "acting in concert", "or community", "similar" | "sub-section (2) of section 122"; the omitted words are present. |
| RB-20 / LR-08 | s.351 "treating"; "threatens by any means, another" | "threatening"; "threatens another by any means". |
| RB-21 / LR-03 | s.303 Explanation 2 "effects the severance" | "affects the severance". |
| RB-12 / LR-15 | BNS 324(4) "less than one lakh" | BNSS Schedule row 324(4) "less than 2 lakh" (both within the inspected material; they conflict with each other). |
| RB-22 / LR-24 | Cross-references in s.71, 89, 148, 199, 264, 341 | Different section numbers in the inspected copy (offsets consistent with pre-enactment numbering). |
| RB-24 / LR-28 | s.119 title "illegal to an act" | Margin heading "illegal act". |
| RB-25 | s.304 "moveable"; s.316 illustration "a lakh"; s.318 illustration "diamond" | "movable"; "one lakh"; "diamonds". |
| RB-32, RB-33, RB-34 | Scraped classification blocks: s.87 and s.90 non-cognizable; s.276 bailable | Schedule rows: s.87 and s.90 cognizable; s.276 non-bailable. These blocks are not used for Bandhoo output. |
| RB-08.a **(new)** | Gemini system prompt: DSP permission "within 14 days" | The fourteen days attaches to the preliminary enquiry. |
| RB-04.b **(new)** | Template: "Legal Metrology Department under the Consumer Protection Act, 2019" | No mention of Legal Metrology in the inspected CPA copy. |
| LR-17.a **(new)** | Template labels Sections 336/338 "forgery of records" | 336(1) is forgery generally (false documents or electronic records); 338 concerns valuable securities, wills, etc. |

## B. Suspected differences (automated comparison only)

| ID | Item |
|---|---|
| RB-26 / LR-24 | Cross-reference differences in s.2, 29, 30, 99, 122, 136, 155, 159, 186, 200, 211, 212, 237, 240, 249, 265, 339, 342 (s.113 and s.167 probably footnote noise). |
| RB-27 / LR-29 | 80 further records marked `differs_from_gazette_needs_review` (many likely formatting or extraction artefacts). |
| RB-28 / LR-29 | 56 records marked `possibly_incomplete` (some only margin-heading effects; s.97 confirmed to match manually). |
| RB-29 / LR-26 | 13 punishment fields not found verbatim (s.70, 113, 118, 124, 125, 206, 211, 221, 222, 260, 263, 316, 323). |
| RB-31 / LR-07 | s.324 wording differences, mostly extraction artefacts. |
| RB-30 / LR-27 | 63 "no punishment clause" records classified by pattern check. |
| RB-35 / LR-22 | s.354, 355, 357 Schedule rows: agree only by positional reading of column-split pages. |
| RB-36 / LR-23 | 195 scraped classification blocks never compared (source comparison not done). |

## C. Legal interpretations that remain unresolved

| ID | Question |
|---|---|
| RB-06 / LR-09 | Section 303(2) proviso at FIR registration (first conviction unknowable from a complaint). |
| RB-06.a **(new)** | The Gemini system prompt states the proviso as settled, contrary to Bandhoo's service logic. |
| RB-07 / LR-10 | How "value of the stolen property" is determined. |
| RB-13 / LR-03(b) | Which theft term (3 years or 1–5 years) governs Section 173(3). |
| RB-09 / LR-12 | "Punishable for three years or more but less than seven years" by maximum term; the 3-year and 7-year boundaries. |
| RB-10 / LR-13 | Using 174(4) and 173(3) when several offences are alleged. |
| RB-11 / LR-14 | Relationship between BNSS 173(3) and *Lalita Kumari*. Note: the judgment concerns CrPC s.154. Its para 111(vi)–(vii) lists categories for preliminary inquiry and a time limit ("should not exceed fifteen days generally … six weeks" in exceptional cases), while BNSS 173(3) refers to "fourteen days". |
| RB-12 / LR-15 | Classification of mischief losses between Rs 1 lakh and Rs 2 lakh. |
| RB-14, RB-15 | Sub-section heuristics (117, 316) and the Section 134 alternative. |
| RB-04.a | Whether referring pricing grievances to Consumer Commissions is appropriate advice (the Act covers overcharging in the s.2(6)(iv) sense, not high prices generally). |
| LR-17.a | Correct sections for "forgery of records". |
| RB-37 to RB-44 | Gold labels for the eight provisional benchmark cases. |
| RB-16 / LR-16 | Adequacy of every procedural template and prompt statement for citizen-facing use. |

## D. Sources unavailable or not checked

| ID | Gap |
|---|---|
| RB-03 | Second authoritative copy (India Code or eGazette) of the BNS and BNSS: blocked (HTTP 403 or error page). |
| RB-03 | Amendments to the BNS or BNSS after 25 Dec 2023: **unknown** (one search found only state and private member's bills, not inspected). |
| RB-02 | Supreme Court copy and SCC report of *Lalita Kumari*; the inspected copy is a third-party print with unverified TLS. |
| RB-04.b | Any source for a "Legal Metrology Department" referral. |
| — | India Code copy of the Consumer Protection Act, 2019; amendments, rules and notifications under it. |
| RB-11 | Later judgments interpreting BNSS 173(3). |

## E. Items blocked pending qualified legal review

These cannot be closed by source matching alone:

| Group | IDs |
|---|---|
| Procedural advice | RB-06 (and RB-06.a), RB-07, RB-08, RB-09, RB-10, RB-11, RB-12, RB-13, RB-14, RB-15, RB-16, RB-17 |
| User-facing citations and referrals | RB-23 (the legal statement about intangible property), RB-04.a, RB-04.b, LR-17.a |
| Statutory-text discrepancies where wording affects elements | RB-18, RB-19, RB-20, RB-21 (once a second copy confirms the text) |
| Benchmark labels | RB-37 to RB-44 |
| Schedule classifications, before any registry extension | RB-32 to RB-34 |

Path-A transcription items (RB-22, RB-24, RB-25, RB-26 to RB-31, RB-35) need a second source copy and a second checker, but not a QLR, unless the wording changes an offence element (`reports/post_review_change_protocol.md`).

## F. RB-01 closure assessment

**RB-01 closure condition** (blocker register): "Both files exist, and every entry has a source and status."

| Check | Result |
|---|---|
| `reports/source_verification_matrix.md` exists | Yes (created 2026-10-20). |
| `reports/source_verification_summary.md` exists | Yes (this file). |
| Every matrix entry has a source and a status | Verified by a script on 2026-10-20 (see the completion report). |
| Contents checked | **Pending maintainer review.** As instructed, the RB-01 status in `release_blocker_register.md` was **not** changed; the register was not modified. |

Closing RB-01 means only that the source-verification **record** exists. Every substantive legal question remains open until the required reviewers approve it.

## G. Addendum — 2026-10-21 (source acquisition only)

Sections A–F above are unchanged. Details are in `source_verification_matrix.md` §11 and `legal_review_execution_checklist.md` (Stage 1 acquisition record, second pass). Nothing below is a legal verification, and no blocker was closed.

| Topic | What changed | What did not |
|---|---|---|
| **Maharashtra BNSS s.173(3) amendment** | L.C. Bills VI and XVII of 2026 (each "six weeks" for "fourteen days" in 173(3)(i)) were passed by the Legislative Council on 24 March and 8 July 2026. Maharashtra Acts I–LIII of 2026 in the Bombay High Court library include no BNSS amendment Act. | **Enactment status UNKNOWN.** No assent, Act number, publication or commencement found. Neither bill is treated as law. |
| **Later Supreme Court decisions on 173(3)** | Obtained from the Supreme Court's own host: *Imran Pratapgadhi v. State of Gujarat*, 2025 INSC 410 (28 Mar 2025), and *Ashish Dave v. State of Rajasthan*, 2026 INSC 244 (27 Feb 2026). Both discuss 173(3) and *Lalita Kumari*. | The relationship (RB-11) is still **unresolved** pending the QLR. High Court decisions not sought. |
| ***Lalita Kumari*** | Its conclusions (numbered "paragraph 120", not 111 as in the Manupatra print) are quoted in 2025 INSC 410. | Official copy of the judgment and the SCC report: **still not obtained**. |
| **Legal Metrology** | The Legal Metrology Act, 2009 was inspected as enacted (PRS). | Rules and the current consolidated text were not obtained. |
| **BNS/BNSS second copy; CPA current copy** | — | **Still not obtained** (India Code blocked). Secondary hosts not used. |
