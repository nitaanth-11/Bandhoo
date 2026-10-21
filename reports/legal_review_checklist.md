# Bandhoo Legal Review Checklist

**Prepared:** 2026-10-20, internal-testing checkpoint. **For:** qualified Indian criminal-law reviewers and the Bandhoo maintainers.

**Status of this document:** every item is **Pending**. Nothing here has been reviewed by a qualified legal professional, and nothing in it is a legal conclusion. Bandhoo is not legally validated and is not production-ready.

## How to use this checklist

1. Work through the items in priority order: **P1** affects the offences and procedural advice Bandhoo produces most often, **P2** affects benchmark labels and less frequent paths, **P3** covers bulk corpus records (Appendix A).
2. For each item, record a status (`Pending`, `Reviewed`, `Disputed` or `Resolved`), your notes, and the final decision with your name and date.
3. Bandhoo maintainers will act on decisions only after they are recorded here. Labels and statutory text are not changed until then.

### Three kinds of content (kept separate throughout)

| Marker | Meaning |
|---|---|
| **[GAZETTE]** | Statutory wording from the official Gazette text, as extracted for this project (provenance below). Treat it as the reference text, subject to the extraction caveats. |
| **[STORED]** | What Bandhoo currently holds in `bns_rag_dataset.json`. Originally scraped from a secondary website; may differ from the Gazette. |
| **[BANDHOO]** | Bandhoo's own interpretation or procedural wording (code in `legal_engine/`). This is what users see; it is not law. |

### Sources and provenance

| Source | Provenance | Limits |
|---|---|---|
| BNS Gazette text | *The Bharatiya Nyaya Sanhita, 2023* (No. 45 of 2023), Gazette of India Extraordinary, 25 Dec 2023. PDF from PRS Legislative Research (`prsindia.org/files/bills_acts/bills_parliament/2023/The Bharatiya Nyaya Sanhita, 2023.pdf`), text extracted with `pypdf`. | Single source; India Code copy could not be downloaded. Extraction can split words ("cau se") and interleave margin headings and footnotes. **Amendments after 25 Dec 2023 were not checked.** The extracted text is not stored in the repository. |
| BNSS Gazette text (incl. First Schedule) | *The Bharatiya Nagarik Suraksha Sanhita, 2023* (No. 46 of 2023), same Gazette date, PRS-hosted PDF, `pypdf` extraction. | As above. Some Schedule I pages extract as separate columns (rows read by position). |
| Stored corpus | `bns_rag_dataset.json`, built by `scrape_bns.py` from `devgan.in` (secondary website), corrected on 2026-10-20 (`reports/corpus_corrections_log_2026-10-20.json`). Per-record evidence in each record's `verification` field. | Not authoritative. Some cross-references match a pre-enactment numbering. |
| Bandhoo procedural registry | `legal_engine/schedule_registry.py` (`VERIFIED_SCHEDULE_I`, line 87), transcribed from the BNSS Gazette Schedule I for 14 sections. | Transcription by the developer, not legal review. |
| Case law | *Lalita Kumari v. Government of Uttar Pradesh* is cited in `schedule_registry.py` lines 39 and 59 as "(2014) 2 SCC 1". | **The citation was added from general knowledge and has not been checked against the judgment in this project.** |
| Not used as legal sources | `bns_finetune_dataset.json`, `bns_scenarios_dataset.json`, `public/bns_rag_dataset.json` | Stale scraper outputs containing known defects. |

### Summary of items

| ID | Item | Type | Priority |
|---|---|---|---|
| LR-01 | BNS 115 voluntarily causing hurt | Statutory text, schedule | P1 |
| LR-02 | BNS 117 grievous hurt | Statutory text, schedule, procedural | P1 |
| LR-03 | BNS 303 theft (text and classification) | Statutory text, schedule | P1 |
| LR-04 | BNS 304 snatching | Statutory text, procedural | P1 |
| LR-05 | BNS 316 criminal breach of trust | Statutory text, interpretation, procedural | P1 |
| LR-06 | BNS 318 cheating | Statutory text, schedule | P1 |
| LR-07 | BNS 324 mischief (text) | Statutory text | P1 |
| LR-08 | BNS 351 criminal intimidation | Statutory text, schedule | P1 |
| LR-09 | BNS 303(2) proviso at FIR registration | Interpretation, procedural | P1 |
| LR-10 | Stolen-property value attribution | Interpretation, procedural | P1 |
| LR-11 | BNSS 173(3) conditions and Bandhoo wording | Procedural | P1 |
| LR-12 | BNSS 173(3) punishment-range reading | Interpretation | P1 |
| LR-13 | Multiple offences: 174(4) deeming and 173(3) | Interpretation, procedural | P1 |
| LR-14 | BNSS 173(3) and *Lalita Kumari* | Interpretation | P1 |
| LR-15 | BNS 324 value bands vs Schedule I | Statutory text, schedule | P1 |
| LR-16 | Procedural advice templates (all user-facing wording) | Procedural | P1 |
| LR-17 | "Section 2(22)" citation in non-penal response | Statutory citation | P1 |
| LR-18 | Registry rows for 14 sections | Schedule | P1 |
| LR-19 | Schedule I: BNS 87 | Schedule | P2 |
| LR-20 | Schedule I: BNS 90 | Schedule | P2 |
| LR-21 | Schedule I: BNS 276 | Schedule | P2 |
| LR-22 | Schedule I: BNS 354, 355, 357 (positional reading) | Schedule | P2 |
| LR-23 | 195 unchecked scraped classification blocks | Schedule | P3 |
| LR-24 | 27 records with differing cross-references | Statutory text | P1 |
| LR-25 | 15 transcribed corrections (2026-10-20) | Statutory text | P1 |
| LR-26 | 13 unverified punishment fields | Statutory text | P2 |
| LR-27 | 67 records marked "no punishment clause" | Statutory text | P2 |
| LR-28 | BNS 119 title | Statutory text | P3 |
| LR-29 | Remaining differing / possibly incomplete records | Statutory text | P3 |
| LR-30 to LR-37 | Eight provisional benchmark cases | Benchmark labelling | P2 |

---

## A. Core offences (P1)

Each item below shows only the **differences** found by an automated ordered word comparison between [STORED] and [GAZETTE]. Many differences are spelling, word order or PDF-extraction artefacts; the reviewer decides which matter. Full stored text is in `bns_rag_dataset.json`; evidence is in each record's `verification.evidence`.

### LR-01 — BNS Section 115 (Voluntarily causing hurt)

| Field | Content |
|---|---|
| Provision | BNS 115(2); BNSS First Schedule row 115(2) |
| Issue type | Statutory text (cross-reference); schedule classification |
| Stored passage | [STORED] "Whoever, except in the case provided for by sub- section (1) of **section 120** voluntarily causes hurt, shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to ten thousand rupees, or with both." |
| Gazette passage | [GAZETTE] "(2) Whoever, except in the case provided for by sub-section (1) of **section 122** voluntarily causes hurt, shall be punished …" |
| Bandhoo behaviour | [BANDHOO] Registry (`schedule_registry.py`): 115(2) non-cognizable, bailable, Any Magistrate, maximum 1 year; Section 173(3) not applicable. Record status `differs_from_gazette_needs_review`; Gemini sees "NOT verified". |
| Legal questions | (a) Confirm the enacted cross-reference is Section 122(1) (hurt on grave and sudden provocation). (b) Confirm the Schedule I classification for 115(2). |
| Evidence to consult | Official BNS text (Gazette / India Code), including any amendment; BNSS First Schedule row 115(2). |
| Needs qualified professional | Yes, for (b) and for confirming no later amendment. |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-02 — BNS Section 117 (Voluntarily causing grievous hurt)

| Field | Content |
|---|---|
| Provision | BNS 117(2), 117(3), 117(4); BNSS First Schedule rows 117(2)–(4) |
| Issue type | Statutory text; schedule classification; procedural advice |
| Stored vs Gazette, 117(2) | [STORED] "Whoever, except in the case provided for by **sub-section (3)**, voluntarily causes grievous hurt …" / [GAZETTE] "(2) Whoever, except in the case provided for by **sub-section (2) of section 122**, voluntarily causes grievous hurt, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine." |
| Stored vs Gazette, 117(4) | [STORED] "When grievous hurt of a person is caused by a group of five or more persons on the ground of his, race, caste, sex, place of birth, language, personal belief or any other ground …" / [GAZETTE] "(4) When a group of five or more persons **acting in concert**, causes grievous hurt to a person on the ground of his race, caste **or community**, sex, place of birth, language, personal belief or any other **similar** ground …" |
| Bandhoo behaviour | [BANDHOO] Registry: cognizable in all rows; bailable under 117(2), non-bailable under 117(3) and 117(4); so `is_bailable` is left unknown unless the sub-section is known. Advice text (`service.py` `_grievous_hurt_procedure_note`, line 669) says Section 173(3) does not apply "on the maximum-term reading" because each row is 7 years or more. |
| Legal questions | (a) Confirm the enacted wording of 117(2) and 117(4). (b) Confirm 117(2) is cognizable and **bailable**. (c) Is it correct to tell users bailability depends on the sub-section when facts are unclear? (d) Is the 173(3) statement correct for a 7-year maximum (see LR-12)? |
| Evidence to consult | Official BNS 117; BNSS First Schedule rows 117(2)–(4). |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-03 — BNS Section 303 (Theft): text and classification

| Field | Content |
|---|---|
| Provision | BNS 303(1) Explanations, 303(2); BNSS First Schedule rows 303(2) |
| Issue type | Statutory text; schedule classification |
| Stored vs Gazette | Explanation 2: [STORED] "…the same act which **effects** the severance may be a theft." / [GAZETTE] "…the same act which **affects** the severance may be a theft." Elsewhere [STORED] "inasmuch" vs [GAZETTE] "in as much" (three illustrations; likely formatting only). |
| Punishment | [STORED] and [GAZETTE] agree on 303(2): up to three years, or fine, or both; on second or subsequent conviction rigorous imprisonment of 1 to 5 years and fine; proviso on community service (see LR-09). |
| Schedule I rows | [GAZETTE] "303(2) Theft. … Cognizable. Non-bailable. Any Magistrate." The punishment column of that row reads "Rigorous imprisonment for not be less than 1 year but which may extend to 5 years and fine" (the repeat-conviction term). A second row: "Where value of property is less than 5,000 rupees. Upon return of the value of property or restoration of the stolen property, shall be punished with community service. Non-cognizable. Bailable. Any Magistrate." |
| Bandhoo behaviour | [BANDHOO] Treats 303(2) as cognizable and non-bailable only when the stated value of the taken property is Rs 5,000 or more; otherwise classification is "unknown" (see LR-09). For Section 173(3), it uses a 3-year maximum (first conviction). |
| Legal questions | (a) Is "effects" or "affects" the enacted word, and does it matter? (b) Which punishment term governs Section 173(3) eligibility for theft: 3 years (first conviction) or 5 years (repeat), given the Schedule row shows the repeat term? |
| Evidence to consult | Official BNS 303; BNSS First Schedule 303(2) rows. |
| Needs qualified professional | Yes, for (b) |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-04 — BNS Section 304 (Snatching)

| Field | Content |
|---|---|
| Provision | BNS 304(1)–(2); BNSS First Schedule row 304(2) |
| Issue type | Statutory text (spelling); procedural advice |
| Stored vs Gazette | [STORED] "moveable" / [GAZETTE] "movable" (only difference found). |
| Bandhoo behaviour | [BANDHOO] Registry: 304(2) cognizable, non-bailable, Any Magistrate, maximum 3 years; Section 173(3) treated as **available** (3 years "or more"; see LR-12). Attempted snatching labels in BM-21 (see LR-32). |
| Legal questions | (a) Confirm classification. (b) Is a 3-year maximum within "three years or more but less than seven years"? (c) When force is used on the person, should Section 134 (assault or criminal force in attempt to commit theft of property carried by a person) be offered as an alternative? |
| Evidence to consult | Official BNS 304, 134; BNSS First Schedule rows 304(2), 134. |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-05 — BNS Section 316 (Criminal breach of trust)

| Field | Content |
|---|---|
| Provision | BNS 316(1)–(5); BNSS First Schedule rows 316(2)–(5) |
| Issue type | Statutory text; interpretation; procedural advice |
| Stored vs Gazette | Illustration: [STORED] "remits **a** lakh of rupees" / [GAZETTE] "remits **one** lakh of rupees". Other differences are PDF artefacts ("th e", "fo r", "warehouse keeper co mmits"). |
| Punishment field | [STORED] "shall be punished with imprisonment of either description for a term which may extend to five years, or with fine, or with both." This is only the 316(2) term; status `unverified`. |
| Bandhoo behaviour | [BANDHOO] Registry: all sub-sections cognizable and non-bailable; maximum 5 years under 316(2), 7 under 316(3) and 316(4), life under 316(5). Advice (`_cbt_procedure_note`, line 645) uses keyword patterns (`CBT_CAPACITY_PATTERNS`, line 115: "employee", "servant", "agent", "banker", "carrier", etc.) to say the case "may fall under" 316(3)–(5) and that 173(3) then does not apply; otherwise it says 173(3) is available "if only 316(2) applies". |
| Legal questions | (a) Confirm the Schedule rows. (b) Are the capacity keywords an acceptable way to flag 316(3)–(5) (e.g. is every "agent" or "employee" within 316(4)/(5))? (c) Should the punishment field list all sub-sections? |
| Evidence to consult | Official BNS 316; BNSS First Schedule rows 316(2)–(5). |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-06 — BNS Section 318 (Cheating)

| Field | Content |
|---|---|
| Provision | BNS 318(1)–(4); BNSS First Schedule rows 318(2)–(4) |
| Issue type | Statutory text (illustration); schedule classification |
| Stored vs Gazette | Illustration: [STORED] "pledging as **diamond**" / [GAZETTE] "pledging as **diamonds**". |
| Bandhoo behaviour | [BANDHOO] Registry: 318(2) and 318(3) non-cognizable, bailable; 318(4) cognizable, non-bailable (7 years). Classification is "unknown" unless the sub-section is known; there is no dedicated advice template for cheating. |
| Legal questions | Confirm the classification rows and whether the generic "conditional" advice is adequate for cheating complaints. |
| Evidence to consult | Official BNS 318; BNSS First Schedule rows 318(2)–(4). |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-07 — BNS Section 324 (Mischief): text

| Field | Content |
|---|---|
| Provision | BNS 324(1)–(6) |
| Issue type | Statutory text |
| Stored vs Gazette | Differences are mostly PDF artefacts ("cau se", "belong ing", "intend ing"), plus [STORED] "in to" vs [GAZETTE] "into" and one "cause"/"causes" in an illustration. The value bands match: [STORED] and [GAZETTE] both read 324(4) "twenty thousand rupees and more but less than one lakh rupees" and 324(5) "one lakh rupees or upwards". The Schedule conflict is in LR-15. |
| Legal question | Confirm no substantive wording difference. |
| Evidence to consult | Official BNS 324. |
| Needs qualified professional | No (text comparison), Yes for LR-15 |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-08 — BNS Section 351 (Criminal intimidation)

| Field | Content |
|---|---|
| Provision | BNS 351(1)–(4); BNSS First Schedule rows 351(2)–(4) |
| Issue type | Statutory text; schedule classification |
| Stored vs Gazette | [STORED] "Whoever threatens by any means, another with any injury…" / [GAZETTE] "(1) Whoever threatens another by any means, with any injury…". [STORED] "…the offence of criminal intimidation by **treating** to cause death or grievous hurt…" / [GAZETTE] "…by **threatening** to cause death or grievous hurt…". |
| Bandhoo behaviour | [BANDHOO] Registry: all rows non-cognizable and bailable; maximum 2 years (351(2), 351(4)) or 7 years (351(3)). Advice routes intimidation-only cases to Section 174 BNSS. Robbery validation treats only threats of violence as robbery circumstances (`ROBBERY_THREAT_RE`). |
| Legal questions | (a) Confirm the enacted wording. (b) Confirm 351(3) is non-cognizable and bailable despite a 7-year maximum. |
| Evidence to consult | Official BNS 351; BNSS First Schedule rows 351(2)–(4). |
| Needs qualified professional | Yes, for (b) |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

---

## B. Section 303(2) proviso and property value (P1)

### LR-09 — BNS 303(2) proviso at FIR registration

| Field | Content |
|---|---|
| Provision | BNS 303(2) proviso; BNSS First Schedule second 303(2) row |
| Issue type | Interpretation; procedural advice |
| Statutory wording | [GAZETTE] "Provided that in cases of theft where the value of the stolen property is less than five thousand rupees, and a person is convicted for the first time, shall upon return of the value of property or restoration of the stolen property, shall be punished with community service." [STORED] text and punishment field match. Schedule row: see LR-03. Note the Schedule row does not mention "first conviction". |
| Bandhoo behaviour | [BANDHOO] `_determine_schedule_metadata` (`service.py` line 393): cognizable and non-bailable only if a stated amount of taken property is Rs 5,000 or more; in every other case (below Rs 5,000, unstated, ambiguous, even if return is stated) cognizable and bailable are **unknown**. Advice (`_theft_procedure_note`, line 572) explains both Schedule rows and says first-conviction status "cannot be established from a complaint" and that treating such a complaint as non-cognizable at registration "is unsettled and requires qualified legal review". Return is detected only from explicit statements (`_restoration_stated`, line 438). "First time" in a narrative is never read as a first conviction. |
| Legal questions | (a) At the information/FIR stage, may police treat theft under Rs 5,000 with property returned as non-cognizable, given first conviction is known only after trial? (b) Does the Schedule row apply when the property has not yet been returned? (c) Is "return of the value" by a third party sufficient? (d) Is it correct for Bandhoo to leave classification unknown in all these cases? |
| Evidence to consult | BNS 303(2); BNSS First Schedule; BNSS 173 and 174; any judicial or departmental guidance on the community-service proviso. |
| Needs qualified professional | **Yes** |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-10 — Attributing amounts to stolen property

| Field | Content |
|---|---|
| Provision | BNS 303(2) proviso (Rs 5,000 threshold) |
| Issue type | Interpretation; procedural advice |
| Bandhoo behaviour | [BANDHOO] `assess_stolen_property_value` (`amounts.py` line 138): counts an amount only if it is in a sentence describing a taking and is not introduced by words such as "paid", "bought", "rent", "loan", "fee" (`_UNRELATED_WORDS`, line 62). Any single item worth Rs 5,000 or more meets the threshold; several small amounts summing to Rs 5,000 or more are "ambiguous" (classification unknown); one amount below Rs 5,000 is "below threshold". Lakh, crore, "k", "thousand" and Devanagari digits are parsed; Hindi number words are not. |
| Legal questions | (a) Is "value of the stolen property" the aggregate of all items taken in one incident? (b) Which value applies: purchase price, market value at the time of theft, or the complainant's estimate? (c) Is treating ambiguous totals as unknown acceptable? |
| Evidence to consult | BNS 303(2); judicial guidance on valuation of stolen property. |
| Needs qualified professional | **Yes** |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

---

## C. BNSS Section 173(3), Section 174(4) and *Lalita Kumari* (P1)

### LR-11 — Section 173(3) conditions and Bandhoo's wording

| Field | Content |
|---|---|
| Provision | BNSS 173(3) |
| Issue type | Procedural advice |
| Statutory wording | [GAZETTE] "(3) Without prejudice to the provisions contained in section 175, on receipt of information relating to the commission of any cognizable offence, which is made punishable for three years or more but less than seven years, the officer in charge of the police station may with the prior permission from an officer not below the rank of Deputy Superintendent of Police, considering the nature and gravity of the offence,— (i) proceed to conduct preliminary enquiry to ascertain whether there exists a prima facie case for proceeding in the matter within a period of fourteen days; or (ii) proceed with investigation when there exists a prima facie case." |
| Bandhoo wording | [BANDHOO] `BNSS_173_3_PROCEDURE_TEXT` (`schedule_registry.py` line 28): paraphrase covering cognizability, the 3-to-under-7-year range, prior DSP permission, the nature and gravity of the offence, a preliminary enquiry "within a period of fourteen days", or investigation where a prima facie case exists. `BNSS_173_3_CAVEAT_TEXT` (line 37) calls it a discretion, not a requirement. Bandhoo rejects user or model claims that 173(3) applies to non-cognizable offences, to offences of 7 years or more, or to vague complaints. |
| Legal questions | (a) Is the paraphrase faithful (including "without prejudice to section 175")? (b) Is it right to describe 173(3) as a police discretion? (c) Does the 14-day period govern completion of the enquiry or something else? (d) Should Bandhoo mention 173(3) at all in citizen-facing advice? |
| Evidence to consult | BNSS 173(1)–(4), 175; any MHA or State guidance on preliminary enquiry. |
| Needs qualified professional | **Yes** |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-12 — Reading of "punishable for three years or more but less than seven years"

| Field | Content |
|---|---|
| Provision | BNSS 173(3) |
| Issue type | Interpretation |
| Bandhoo behaviour | [BANDHOO] `check_bnss_173_3_eligibility` (line 363) uses the **maximum** term in each Schedule row. A maximum of exactly 7 years is treated as outside the range (e.g. BNS 117(2), 305, 306, 316(3), 316(4), 318(4)). A maximum of exactly 3 years is treated as inside it (e.g. 303(2) first conviction, 304(2)). Both boundary cases carry the label "interpretation pending qualified legal review" (`BNSS_173_3_RANGE_READING_NOTE`, line 44). |
| Legal question | Is "made punishable for" read by reference to the maximum term? How should offences with a minimum term, or with different first and repeat-conviction terms, be treated? |
| Evidence to consult | BNSS 173(3); judicial or academic commentary on the provision. |
| Needs qualified professional | **Yes** |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-13 — Several offences in one complaint

| Field | Content |
|---|---|
| Provision | BNSS 174(4); 173(1); 173(3) |
| Issue type | Interpretation; procedural advice |
| Statutory wording | [GAZETTE] 174(4): "Where a case relates to two or more offences of which at least one is cognizable, the case shall be deemed to be a cognizable case, notwithstanding that the other offences are non-cognizable." |
| Bandhoo behaviour | [BANDHOO] `_multi_offence_procedure` (`service.py` line 808) reviews every candidate scoring 0.5 or more (`PROCEDURAL_SUPPORT_SCORE_FLOOR`, line 131). If any candidate is cognizable, it says information is recorded under 173(1) "if that offence is made out" and cites 174(4). It assesses 173(3) "offence by offence". |
| Legal questions | (a) Is citing 174(4) at the information-recording stage correct? (b) When one offence is within the 173(3) range and another is 7 years or more, may a preliminary enquiry be held at all? (c) Is a score cut-off an acceptable basis for which offences are mentioned in advice? |
| Evidence to consult | BNSS 173, 174. |
| Needs qualified professional | **Yes** |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-14 — Section 173(3) and *Lalita Kumari*

| Field | Content |
|---|---|
| Provision | BNSS 173(1), 173(3); *Lalita Kumari v. Government of Uttar Pradesh* |
| Issue type | Interpretation |
| Bandhoo wording | [BANDHOO] `BNSS_173_3_CAVEAT_TEXT`: "…how Section 173(3) interacts with the duty to record information under Section 173(1), and with the principles in Lalita Kumari v. Government of Uttar Pradesh, (2014) 2 SCC 1 (mandatory registration of an FIR where information discloses a cognizable offence), is the subject of differing judicial and academic views and is not determined by this assessment." |
| Source status | **The citation and the one-line summary of the judgment were written from general knowledge and have not been checked against the judgment.** No judgment text is held in the project. Secondary commentary seen during development (SCC Online blog, January 2026) discusses tension between 173(3) and the judgment but was not relied on as authority. |
| Legal questions | (a) Is the citation correct? (b) Is the summary accurate? (c) What is the current position on how 173(3) relates to the judgment, including any later decisions? (d) Should citizen-facing advice mention it? |
| Evidence to consult | The judgment itself; any later Supreme Court or High Court decisions on 173(3). |
| Needs qualified professional | **Yes** |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

---

## D. Section 324 value bands (P1)

### LR-15 — BNS 324(4)/(5) bands vs BNSS Schedule I

| Field | Content |
|---|---|
| Provision | BNS 324(4), 324(5); BNSS First Schedule rows 324(4), 324(5) |
| Issue type | Statutory text; schedule classification |
| Statutory wording | [GAZETTE, BNS] 324(4): "…loss or damage to the amount of twenty thousand rupees and more but less than **one lakh** rupees shall be punished with imprisonment … which may extend to two years, or with fine, or with both." 324(5): "…one lakh rupees or upwards … may extend to five years, or with fine, or with both." [GAZETTE, BNSS Schedule] row 324(4): "Mischief causing loss or damage to the amount of twenty thousand rupees but less than **2 lakh** rupees. … Non-cognizable. Bailable. Any Magistrate." Row 324(5): "…one lakh rupees or upwards. … Cognizable. Bailable. Magistrate of the first class." |
| Bandhoo behaviour | [BANDHOO] Registry: cognizability unknown for 324 unless the sub-section is known (324(2)–(4) non-cognizable; 324(5)–(6) cognizable); all bailable. Advice (`_mischief_procedure_note`, line 678) states the band conflict as unresolved. |
| Legal questions | (a) For loss between Rs 1 lakh and Rs 2 lakh, which classification applies? (b) Has the Schedule entry been corrected or amended? |
| Evidence to consult | BNS 324; BNSS First Schedule; any corrigendum or amendment. |
| Needs qualified professional | **Yes** |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

---

## E. Procedural advice templates and citations (P1)

### LR-16 — All user-facing procedural wording

| Field | Content |
|---|---|
| Provision | Various BNS / BNSS |
| Issue type | Procedural advice |
| Bandhoo behaviour | [BANDHOO] Fixed templates in `legal_engine/service.py`: vague complaint (`_audit_and_qualify_procedural_recommendation`, line 516); theft (line 572); robbery (line 629: cognizable, non-bailable, 173(1); 173(3) inapplicable because 309(4) carries up to 10 years, 14 on a highway at night); criminal breach of trust (line 645); grievous hurt (line 669); mischief (line 678); dishonest misappropriation (line 687: non-cognizable, bailable, Section 174 procedure); single and multiple offences (lines 739, 808); non-penal grievance responses (line 1000, including "Consumer Disputes Redressal Commission or Legal Metrology Department under the Consumer Protection Act, 2019"). Every response carries a disclaimer (`schemas.py`, `statutory_disclaimer`). |
| Legal questions | For each template: is every statement accurate, appropriately qualified, and suitable for a citizen audience? Are any statements overclaiming (e.g. "information is to be recorded as an FIR")? Is the consumer-forum referral accurate? |
| Evidence to consult | BNSS 173, 174, 175; BNS sections cited; Consumer Protection Act, 2019. |
| Needs qualified professional | **Yes** |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-17 — "Section 2(22)" citation for movable property

| Field | Content |
|---|---|
| Provision | BNS 2 (definitions); BNS 303 |
| Issue type | Statutory citation (confirmed discrepancy) |
| Bandhoo wording | [BANDHOO] Non-penal response (`service.py` line 1035): "Under Section 303 read with Section **2(22)** of the BNS, 2023, penal offences against property strictly apply to corporeal movable property…" |
| Gazette | [GAZETTE] "**(21)** "movable property" includes property of every description, except land and things attached to the earth or permanently fastened to anything which is attached to the earth." |
| Legal questions | (a) Confirm the clause number is 2(21) and approve the correction. (b) Is the statement that intangible things "cannot be the subject of penal theft" accurate as phrased? |
| Evidence to consult | BNS 2(21), 303. |
| Needs qualified professional | (a) No, confirmation is sufficient; (b) Yes |
| Review status | Pending (code not yet changed) |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-18 — Registry rows for 14 sections

| Field | Content |
|---|---|
| Provision | BNSS First Schedule rows for BNS 115, 117, 303, 304, 305, 306, 309, 310, 314, 316, 318, 324, 351, 352 |
| Issue type | Schedule classification |
| Bandhoo behaviour | [BANDHOO] `VERIFIED_SCHEDULE_I` (`schedule_registry.py` line 87): cognizable, bailable, court and maximum term per row, transcribed by the developer from the Gazette Schedule. These values drive `is_cognizable`, `is_bailable` and the 173(3) checks. Notable values: 117(2) bailable; 306 Any Magistrate; 310 Court of Session; 309 rows all cognizable and non-bailable; 314 non-cognizable and bailable; 352 non-cognizable and bailable. |
| Legal question | Confirm every row against the official Schedule, including any amendment. |
| Evidence to consult | BNSS First Schedule, Part I. |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

---

## F. Schedule I conflicts in scraped classification blocks (P2–P3)

These blocks were scraped with the statutory text, moved out of it on 2026-10-20, and are **never** shown to Gemini or used for procedural output. They remain in `scraped_procedural_classification` and in the search index wording.

### LR-19 — BNS Section 87

| Field | Content |
|---|---|
| Provision | BNS 87 (Kidnapping, abducting or inducing woman to compel her marriage, etc.) |
| Issue type | Schedule classification |
| Stored block | [STORED] "BNSS Classification • Imprisonment for 10 years and fine • **Non-cognizable** • Non-bailable • Triable by Court of Session" |
| Gazette | [GAZETTE] Schedule row 87: "Imprisonment for 10 years and fine. **Cognizable.** Non-bailable. Court of Session." |
| Bandhoo behaviour | [BANDHOO] Section 87 is not in the registry, so classification is reported as unknown. |
| Legal question | Confirm the classification; decide whether to add the section to the registry. |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-20 — BNS Section 90

| Field | Content |
|---|---|
| Provision | BNS 90(1), 90(2) (Death caused by act done with intent to cause miscarriage) |
| Issue type | Schedule classification |
| Stored block | [STORED] "BNSS Classification • 90(1) – Imprisonment for 10 years and fine. • 90(2) – Imprisonment for life, or as above. • **Non-cognizable** • Non-bailable • Triable by Court of Session" |
| Gazette | [GAZETTE] Rows 90(1) and 90(2): "**Cognizable.** Non-bailable. Court of Session." |
| Bandhoo behaviour | Not in registry; classification unknown. |
| Legal question | Confirm the classification. |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-21 — BNS Section 276

| Field | Content |
|---|---|
| Provision | BNS 276 (Adulteration of drugs) |
| Issue type | Schedule classification |
| Stored block | [STORED] "BNSS Classification • Imprisonment for 1 year, or fine of 5,000 rupees, or both. • Non-cognizable • **Bailable** • Triable by Any Magistrate." |
| Gazette | [GAZETTE] Row 276: "Imprisonment for 1 year, or fine of 5,000 rupees, or both. Non-cognizable. **Non-bailable.** Any Magistrate." |
| Bandhoo behaviour | Not in registry; classification unknown. |
| Legal question | Confirm the classification. |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-22 — BNS Sections 354, 355, 357 (positional reading)

| Field | Content |
|---|---|
| Provision | BNS 354, 355, 357 |
| Issue type | Schedule classification |
| Stored blocks | [STORED] all three: Non-cognizable, Bailable, Any Magistrate. |
| Gazette | The extracted Schedule pages separate the columns, so each row was matched to its classification **by position**. On that reading all three are Non-cognizable, Bailable, Any Magistrate. Lower confidence. |
| Legal question | Confirm the three rows from the printed Schedule. |
| Needs qualified professional | No (reading the printed page is sufficient) |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-23 — 195 unchecked scraped classification blocks

| Field | Content |
|---|---|
| Provision | BNSS First Schedule (all other rows) |
| Issue type | Schedule classification |
| Bandhoo behaviour | [BANDHOO] Blocks retained with `gazette_check: not_checked_against_gazette`. Not used for procedural output; their words remain in the BM25 search index for retrieval parity. |
| Legal question | Decide whether to verify these against the Schedule, discard them, or replace them with registry entries. |
| Needs qualified professional | No for verification; yes for any classification later added to the registry |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

---

## G. Corpus records (P1–P3)

### LR-24 — 27 records with differing cross-references

Automated ordered comparison; the pairs are "stored → Gazette". Some pairs come from footnote Act years in the Gazette extraction (e.g. 113, 167) and are probably noise. Several show an offset of two, consistent with pre-enactment numbering. Gemini sees these records as "NOT verified".

| Section | Title (stored) | Number differences (stored → Gazette) | Status | Notes / decision |
|---|---|---|---|---|
| 2 | Definitions | 10/46/47/48/51/53 → 9/49/50/52; 113/114/117 → 119/120/123; list of 13 sections → 127/222/230/…/263; 306 → 308; 324 → 330 | Pending | |
| 29 | Exclusion of acts which are offences independently of harm caused | 21/22 → 25/26; 23 → 27 | Pending | |
| 30 | Act done in good faith for benefit of a person without consent | 21/22 → 26/27 | Pending | |
| 71 | Punishment for repeat offenders | 67 → 70 | Pending | |
| 89 | Causing miscarriage without woman's consent | 86 → 88 | Pending | |
| 99 | Buying child for purposes of prostitution, etc | 96 → 98 | Pending | |
| 113 | Terrorist act | 1967, 2 (Act-year references; likely footnote noise) | Pending | |
| 115 | Voluntarily causing hurt | 120 → 122 (see LR-01) | Pending | |
| 122 | Voluntarily causing hurt or grievous hurt on provocation | 99 → 101 | Pending | |
| 136 | Assault or criminal force on grave provocation | 129 → 131 | Pending | |
| 148 | Conspiracy to commit offences punishable by section 147 | 145 → 147 | Pending | |
| 155 | Receiving property taken by war or depredation… | 151 → 153; 152 → 154 | Pending | |
| 159 | Abetting mutiny, or attempting to seduce a soldier… | 165 → (no number) | Pending | |
| 167 | Persons subject to certain Acts | 1950/1934 (Act years; likely footnote noise) | Pending | |
| 186 | Prohibition of fictitious stamps | 176 → 178; 179 → 181; 181 → 183; 183 → 185 | Pending | |
| 199 | Public servant disobeying direction under law | 174 → 173 (BNSS reference); 73 → 74; 122 → 77/79/124/143; 141/142 → 144 | Pending | |
| 200 | Punishment for non-treatment of victim | 449 → 397 (BNSS reference) | Pending | |
| 211 | Omission to give notice or information to public servant… | 447 → 394 (BNSS reference) | Pending | |
| 212 | Furnishing false information | 209 → 211; 303 → 309; list → 103/105/307 | Pending | |
| 237 | Using as true such declaration knowing it to be false | 234 → 236 | Pending | |
| 240 | Giving false information respecting an offence committed | 236 → 238; 237 → 239; list → 103/105/307 | Pending | |
| 249 | Harbouring offender | list → 103/105/307 | Pending | |
| 264 | Omission to apprehend, or sufferance of escape… | 257 → 259; 258 → 260; 259 → 261 | Pending | |
| 265 | Resistance or obstruction to lawful apprehension… | 260 → 262; 261 → 263 | Pending | |
| 339 | Having possession of document described in section 337 or 338… | 335 → 337; 336 → 338 | Pending | |
| 341 | Making or possessing counterfeit seal… | 336 → 338 | Pending | |
| 342 | Counterfeiting device or mark used for authenticating documents… | 336 → 338 | Pending | |

- **Issue type:** statutory text.
- **Legal question:** confirm the enacted cross-references and approve replacement of the stored text from the official source.
- **Needs qualified professional:** no for confirming the text; yes if any difference reflects an amendment.

### LR-25 — The 15 corrections made on 2026-10-20

| Field | Content |
|---|---|
| Provision | BNS 13, 56, 58, 71, 111 (text and punishment), 120 (text and punishment), 148, 199, 251, 252, 264, 309, 311, 312, 341 (punishment fields) |
| Issue type | Statutory text |
| Bandhoo behaviour | [BANDHOO] Replacements were hand-transcribed from the Gazette extraction. Each was machine-checked to contain the Gazette words in the same order with no substitutions; skipped Gazette words were only margin headings. Full before and after values: `reports/corpus_corrections_log_2026-10-20.json`. Sub-section labels such as "Section 309(4):" are added metadata, not statute. |
| Legal question | Confirm each replacement against the official text and any amendment. |
| Evidence to consult | Official BNS text; the corrections log. |
| Needs qualified professional | No for text confirmation |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-26 — 13 unverified punishment fields

| Field | Content |
|---|---|
| Provision | BNS 70, 113, 118, 124, 125, 206, 211, 221, 222, 260, 263, 316, 323 |
| Issue type | Statutory text |
| Bandhoo behaviour | [BANDHOO] The `punishment` field was not found as a continuous passage in the Gazette section (`punishment_status: unverified`). Causes include paraphrase (118 starts "Imprisonment of either description up to three years…") and single-limb extraction of multi-limb punishments (316). The field is returned to API clients and shown to Gemini. |
| Legal question | For each, confirm or replace with the enacted punishment wording. |
| Needs qualified professional | No for text |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-27 — 67 records marked "no punishment clause"

| Field | Content |
|---|---|
| Provision | 67 BNS sections with an empty punishment field |
| Issue type | Statutory text |
| Bandhoo behaviour | [BANDHOO] Sections 2, 4, 32 and 54 were reviewed manually. The other 63 were classified by an automated check for phrases such as "shall be punished" in the Gazette section. Gemini is told "No punishment clause in this section"; no punishment is invented. |
| Legal question | Spot-check that none of the 63 contains a punishment. |
| Needs qualified professional | No |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-28 — BNS Section 119 title

| Field | Content |
|---|---|
| Provision | BNS 119 |
| Issue type | Statutory text (title) |
| Stored vs Gazette | [STORED] title "…to extort property, or to constrain to an illegal **to an** act" / [GAZETTE] margin heading "…to extort property, or to constrain to an illegal act." |
| Legal question | Approve correction of the title. |
| Needs qualified professional | No |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

### LR-29 — Remaining differing and possibly incomplete records

| Field | Content |
|---|---|
| Provision | 80 further records marked `differs_from_gazette_needs_review` and 56 marked `possibly_incomplete` (Appendix A) |
| Issue type | Statutory text |
| Note | These statuses come from an automated comparison and **do not mean the records are legally wrong**. Many differences are formatting or extraction artefacts; some "possibly incomplete" records only reflect margin headings (Section 97 was checked manually and its operative text matches). |
| Legal question | Review each record; record the outcome in Appendix A. |
| Needs qualified professional | No for text comparison |
| Review status | Pending |
| Reviewer notes | |
| Final decision (reviewer, date) | |

---

## H. Provisional benchmark cases (P2)

Labels below are **unchanged** and must stay unchanged until a decision is recorded here. "Proposed" corrections come from an automated statutory cross-check (`label_review` in `benchmark/bns_synthetic_benchmark_50.json`) and have **not** been applied.

### LR-30 — BNS-BM-17 (English, robbery)

| Field | Content |
|---|---|
| Narrative | "Two masked men entered my chemist shop at midnight. One held a large knife against my throat and threatened to kill me if I screamed, while the other looted Rs 40,000 from the cash register." |
| Current labels | Relevant [309, 310, 311]; plausible []; contradicted []; cognizable true, bailable false |
| Concern | Section 310(1) dacoity requires five or more persons; two are described. Section 311 turns on whether holding a knife to the throat is "uses any deadly weapon". |
| Proposed (not applied) | Relevant [309, 311]; contradicted [310] |
| Legal questions | Is 310 excluded? Does 311 apply on these facts? Is shop entry at midnight trespass or house-breaking? |
| Issue type | Benchmark labelling |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final labels (reviewer, date) | |

### LR-31 — BNS-BM-20 (English, attempted theft)

| Field | Content |
|---|---|
| Narrative | "While boarding a crowded BEST bus at Churchgate, I felt someone's hand sliding inside my front coat pocket where my wallet was kept. I immediately grabbed the person's wrist before he could grasp or remove the wallet. The wallet never left my pocket." |
| Current labels | Relevant [62, 303]; plausible []; contradicted [309]; cognizable true, **bailable true** |
| Concern | The Schedule I row for Section 62 makes bailability follow the offence attempted; 303(2) is non-bailable. "Bailable" fits only Section 134, which is not labelled. |
| Proposed (not applied) | Bailable false; plausible [134] |
| Legal questions | Correct bailability for attempted theft here? Is inserting a hand into the pocket "criminal force" under Section 134? |
| Issue type | Benchmark labelling |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final labels (reviewer, date) | |

### LR-32 — BNS-BM-21 (Hindi, attempted chain snatching)

| Field | Content |
|---|---|
| Narrative | "बाजार में एक चोर ने मेरी सोने की चेन खींचने का प्रयास किया, लेकिन चेन मेरे हाथ में आ गई और टूटी नहीं। लोगों के चिल्लाने पर वह बिना कुछ लिए भाग गया।" |
| Current labels | Relevant [62, 304]; plausible [303]; contradicted [309]; cognizable true, **bailable true** |
| Concern | Section 62 read with 304(2) gives non-bailable. Section 134 is a strong unlabelled candidate (cognizable, bailable). |
| Proposed (not applied) | Bailable false; plausible [303, 134] |
| Legal questions | Correct offence(s) and bailability for an attempted chain snatch with force? |
| Issue type | Benchmark labelling |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final labels (reviewer, date) | |

### LR-33 — BNS-BM-22 (Hinglish, attempted theft from shop drawer)

| Field | Content |
|---|---|
| Narrative | "Ek ladka meri dukan ke drawer se cash nikalne ki koshish kar raha tha, par jaise hi maine awaz lagayi wo dar ke mare hath khali chhod kar bhag gaya. Ek bhi rupya chori nahi ho paya." |
| Current labels | Relevant [62, 303]; plausible []; contradicted [309]; cognizable true, **bailable true** |
| Concern | Bailability follows the offence attempted (303(2) and 305 non-bailable). A shop may be a "building used for the custody of property" (Section 305). |
| Proposed (not applied) | Bailable false; plausible [305] |
| Legal questions | Is this an attempt under 303 or 305? Correct bailability? |
| Issue type | Benchmark labelling |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final labels (reviewer, date) | |

### LR-34 — BNS-BM-28 (English, garage break-in)

| Field | Content |
|---|---|
| Narrative | "A trespasser climbed over my compound wall at 2 AM, broke the padlock of my garage, and stole power tools worth Rs 18,000." |
| Current labels | Relevant [303, 329, 331]; plausible []; contradicted [309]; cognizable true, bailable false |
| Concern | Section 305 (theft in a building used for the custody of property) is unlabelled; the 331 sub-section is unstated. |
| Proposed (not applied) | Relevant [303, 305, 329, 331] |
| Legal questions | Does 305 apply to a garage? Which 331 sub-section applies? |
| Issue type | Benchmark labelling |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final labels (reviewer, date) | |

### LR-35 — BNS-BM-30 (Hinglish, servant theft and hurt to watchman)

| Field | Content |
|---|---|
| Narrative | "Ghar ka purana servant bina permission flat mein ghusa duplicate key se, bedroom almirah khol ke 80,000 cash chori kiya aur jab society watchman ne roka toh watchman ko danda maar kar ghayal kar diya." |
| Current labels | Relevant [303, 309, 115, 329]; plausible []; contradicted []; cognizable true, bailable false |
| Concern | "Purana servant" may mean former or long-serving (affects Section 306). Sections 305 and 331 are unlabelled. Hurt with a stick: Section 115 or 118(1)? |
| Proposed (not applied) | Plausible [305, 306, 118, 331] |
| Legal questions | Which provisions apply? Is causing hurt while carrying away the property robbery under 309? |
| Issue type | Benchmark labelling |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final labels (reviewer, date) | |

### LR-36 — BNS-BM-31 (English, tenant disposes of owner's furniture)

| Field | Content |
|---|---|
| Narrative | "A tenant whose lease expired 3 months ago refused to vacate, broke the padlock of the owner's locked storage room inside the premises, and disposed of the owner's antique furniture worth Rs 50,000." |
| Current labels | Relevant [303, 316, 329]; plausible [314]; contradicted [309]; cognizable true, bailable false |
| Concern | No entrustment is stated, so Section 316 is doubtful. Since the 2026-10-20 corpus correction, Bandhoo's top fallback prediction is 314 rather than 316 (a near-tie), which accounts for the procedural-correctness change from 12/32 to 11/32. |
| Proposed (not applied) | Relevant [303, 329]; plausible [314, 316, 305, 331] |
| Legal questions | Theft, criminal breach of trust or dishonest misappropriation? Which trespass or house-breaking provisions apply? |
| Issue type | Benchmark labelling |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final labels (reviewer, date) | |

### LR-37 — BNS-BM-45 (Hindi, cash taken from bedroom almirah)

| Field | Content |
|---|---|
| Narrative | "मेरी अनुपस्थिति में किसी अज्ञात व्यक्ति द्वारा मेरे शयनकक्ष की अलमारी से पच्चीस हजार रुपये की नकद राशि अपहृत कर ली गई है, बिना किसी हिंसा अथवा विवशता के।" |
| Current labels | Relevant [303, 329]; plausible []; contradicted [309]; cognizable true, bailable false |
| Concern | Section 305 (theft in a dwelling house) is unlabelled; Section 329 assumes entry facts that are not stated. |
| Proposed (not applied) | Relevant [303, 305]; plausible [329] |
| Legal questions | Does 305 apply? Is 329 relevant or only plausible? |
| Issue type | Benchmark labelling |
| Needs qualified professional | Yes |
| Review status | Pending |
| Reviewer notes | |
| Final labels (reviewer, date) | |

---

## Sign-off

| Role | Name | Date | Items covered | Signature |
|---|---|---|---|---|
| Reviewer 1 (qualified Indian criminal-law professional) | | | | |
| Reviewer 2 | | | | |
| Adjudicator (for disputed items) | | | | |
| Bandhoo maintainer (implementation of decisions) | | | | |


---

## Appendix A — Records needing individual text review (P3)

Generated from `bns_rag_dataset.json` (`verification` field). The "First automated difference" column is the first item of `evidence.ordered_comparison_problems_sample` and may be an extraction artefact. Records already covered by LR-01 to LR-08 (core offences) or LR-24 (cross-references) are marked in the Item column.

### A.1 Differs from Gazette, needs review (107 records)

| Section | Title (stored) | Item | Punishment status | First automated difference | Review status | Notes / decision |
|---|---|---|---|---|---|---|
| 1 | Short title, commencement and application | — | no_punishment_clause | delete: transcription ['preamble', 'an', 'act', 'to', 'consolidate', 'and', 'amend', 'the', 'provisions', 'relating', 'to', 'offences', 'and', 'for', … | Pending | |
| 2 | Definitions | LR-24 | no_punishment_clause | missing Gazette words not transcribed: ['denotes'] | Pending | |
| 3 | General Explanations | — | no_punishment_clause | missing Gazette words not transcribed: ['general', 'explanations', '21', 'of', '2000'] | Pending | |
| 4 | Punishments | — | no_punishment_clause | delete: transcription ['life', 'that', 'is', 'to', 'say', 'imprisonment', 'for', 'remainder', 'of', 'a', 'person', 's', 'natural'] vs Gazette [] | Pending | |
| 5 | Commutation of sentence | — | no_punishment_clause | replace: transcription ['explanations'] vs Gazette ['explanation'] | Pending | |
| 8 | Amount of fine, liability in default of payment of fine, etc | — | consistent_with_gazette | delete: transcription ['for', 'any', 'term', 'not', 'exceeding'] vs Gazette [] | Pending | |
| 9 | Limit of punishment of offence made up of several offences | — | consistent_with_gazette | replace: transcription ['where'] vs Gazette ['limit', 'of', 'punishment', 'of', 'offence', 'made', 'up', 'of', 'several', 'offences'] | Pending | |
| 13 | Enhanced punishment for certain offences after previous conviction | — | verified_against_gazette | replace: transcription ['chapters'] vs Gazette ['chapter'] | Pending | |
| 22 | Act of a person of unsound mind | — | no_punishment_clause | replace: transcription ['mental', 'illness'] vs Gazette ['unsoundness', 'of', 'mind'] | Pending | |
| 23 | Act of a person incapable of judgment by reason of intoxication caused | — | no_punishment_clause | replace: transcription ['unless'] vs Gazette ['provided'] | Pending | |
| 27 | Act done in good faith for benefit of child or person with unsound min | — | no_punishment_clause | missing Gazette words not transcribed: ['person'] | Pending | |
| 28 | Consent known to be given under fear or misconception | — | no_punishment_clause | replace: transcription ['mental', 'illness'] vs Gazette ['unsoundness', 'of', 'mind'] | Pending | |
| 29 | Exclusion of acts which are offences independently of harm caused | LR-24 | no_punishment_clause | replace: transcription ['21', '22'] vs Gazette ['25', '26'] | Pending | |
| 30 | Act done in good faith for benefit of a person without consent | LR-24 | no_punishment_clause | missing Gazette words not transcribed: ['this'] | Pending | |
| 36 | Right of private defence against the act of a person with unsound mind | — | no_punishment_clause | replace: transcription ['mental', 'illness'] vs Gazette ['unsoundness', 'of', 'mind'] | Pending | |
| 39 | When such right extends to causing any harm other than death | — | no_punishment_clause | replace: transcription ['specfied'] vs Gazette ['specified'] | Pending | |
| 41 | When the right of private defence of property extends to causing death | — | no_punishment_clause | replace: transcription ['sun', 'set'] vs Gazette ['sunset'] | Pending | |
| 43 | Commencement and continuance of the right of private defence of proper | — | no_punishment_clause | replace: transcription ['sun', 'rise'] vs Gazette ['sunrise'] | Pending | |
| 46 | Abettor | — | consistent_with_gazette | replace: transcription ['with', 'mental', 'illness'] vs Gazette ['of', 'unsound', 'mind'] | Pending | |
| 56 | Abetment of offence punishable with imprisonment | — | verified_against_gazette | replace: transcription ['by'] vs Gazette ['under'] | Pending | |
| 58 | Concealing design to commit offence punishable with death or imprisonm | — | verified_against_gazette | delete: transcription ['illegal'] vs Gazette [] | Pending | |
| 59 | Public servant concealing design to commit offence which it is his dut | — | consistent_with_gazette | delete: transcription ['illegal'] vs Gazette [] | Pending | |
| 63 | Rape | — | no_punishment_clause | replace: transcription ['mental', 'illness'] vs Gazette ['unsoundness', 'of', 'mind'] | Pending | |
| 64 | Punishment for rape | — | consistent_with_gazette | missing Gazette words not transcribed: ['rape', 'rape', 'punishment', 'for'] | Pending | |
| 68 | Sexual intercourse by a person in authority | — | consistent_with_gazette | replace: transcription ['meaning'] vs Gazette ['meanings'] | Pending | |
| 69 | Sexual intercourse by employing deceitful means etc | — | consistent_with_gazette | missing Gazette words not transcribed: ['to'] | Pending | |
| 71 | Punishment for repeat offenders | LR-24 | verified_against_gazette | replace: transcription ['67'] vs Gazette ['70'] | Pending | |
| 72 | Disclosure of identity of the victim of certain offences, etc | — | consistent_with_gazette | replace: transcription ['minor'] vs Gazette ['a', 'child'] | Pending | |
| 74 | Assault or criminal force to woman with intent to outrage her modesty | — | consistent_with_gazette | replace: transcription ['there', 'by'] vs Gazette ['thereby'] | Pending | |
| 75 | Sexual harassment | — | consistent_with_gazette | replace: transcription ['act'] vs Gazette ['acts'] | Pending | |
| 77 | Voyeurism | — | consistent_with_gazette | replace: transcription ['purpose'] vs Gazette ['purposes'] | Pending | |
| 89 | Causing miscarriage without woman’s consent | LR-24 | consistent_with_gazette | replace: transcription ['86'] vs Gazette ['88'] | Pending | |
| 96 | Procuration of child | — | consistent_with_gazette | delete: transcription ['below', 'the', 'age', 'of', 'eighteen', 'years'] vs Gazette [] | Pending | |
| 98 | Selling child for purposes of prostitution, etc | — | consistent_with_gazette | missing Gazette words not transcribed: ['any'] | Pending | |
| 99 | Buying child for purposes of prostitution, etc | LR-24 | consistent_with_gazette | delete: transcription ['below', 'the', 'age', 'of', 'eighteen', 'years'] vs Gazette [] | Pending | |
| 101 | Murder | — | no_punishment_clause | replace: transcription ['person', 'under', 'eighteen', 'years', 'of', 'age'] vs Gazette ['child'] | Pending | |
| 103 | Punishment for murder | — | consistent_with_gazette | missing Gazette words not transcribed: ['similar'] | Pending | |
| 107 | Abetment of suicide of child or person of unsound mind | — | consistent_with_gazette | replace: transcription ['person', 'under', 'eighteen', 'years', 'of', 'age'] vs Gazette ['child'] | Pending | |
| 109 | Attempt to murder | — | consistent_with_gazette | missing Gazette words not transcribed: ['culpable', 'homicide', 'by', 'causing', 'death', 'of', 'person', 'other', 'than', 'person', 'whose', 'death',… | Pending | |
| 112 | Petty organised crime | — | consistent_with_gazette | replace: transcription ['crime', 'that', 'causes', 'general', 'feelings'] vs Gazette ['act'] | Pending | |
| 113 | Terrorist act | LR-24 | unverified | replace: transcription ['a', 'person', 'is', 'said', 'to', 'have', 'committed', 'a', 'terrorist', 'act', 'if', 'he', 'commits'] vs Gazette ['whoever',… | Pending | |
| 115 | Voluntarily causing hurt | LR-01–08 | consistent_with_gazette | replace: transcription ['120'] vs Gazette ['122'] | Pending | |
| 117 | Voluntarily causing grievous hurt | LR-01–08 | consistent_with_gazette | replace: transcription ['whoever', 'except', 'in', 'the', 'case', 'provided', 'for', 'by', 'sub', 'section'] vs Gazette ['hurt'] | Pending | |
| 119 | Voluntarily causing hurt or grievous hurt to extort property, or to co | — | consistent_with_gazette | replace: transcription ['subsection'] vs Gazette ['sub', 'section'] | Pending | |
| 122 | Voluntarily causing hurt or grievous hurt on provocation | LR-24 | consistent_with_gazette | missing Gazette words not transcribed: ['grievous'] | Pending | |
| 125 | Act endangering life or personal safety of others | — | unverified | delete: transcription ['the'] vs Gazette [] | Pending | |
| 129 | Criminal force | — | no_punishment_clause | replace: transcription ['throw'] vs Gazette ['throws'] | Pending | |
| 136 | Assault or criminal force on grave provocation | LR-24 | consistent_with_gazette | replace: transcription ['129'] vs Gazette ['131', 'of', 'kidnapping', 'abduction', 'slavery', 'and', 'forced', 'labour'] | Pending | |
| 137 | Kidnapping | — | consistent_with_gazette | delete: transcription ['below', 'the', 'age', 'of', 'eighteen', 'years'] vs Gazette [] | Pending | |
| 139 | Kidnapping or maiming a child for purposes of begging | — | consistent_with_gazette | delete: transcription ['below', 'the', 'age', 'of', 'eighteen', 'years'] vs Gazette [] | Pending | |
| 143 | Trafficking of person | — | consistent_with_gazette | replace: transcription ['practicing'] vs Gazette ['practising'] | Pending | |
| 144 | Exploitation of a trafficked person | — | consistent_with_gazette | delete: transcription ['below', 'the', 'age', 'of', 'eighteen', 'years'] vs Gazette [] | Pending | |
| 148 | Conspiracy to commit offences punishable by section 147 | LR-24 | verified_against_gazette | replace: transcription ['145'] vs Gazette ['147'] | Pending | |
| 155 | Receiving property taken by war or depredation mentioned in sections 1 | LR-24 | consistent_with_gazette | replace: transcription ['151'] vs Gazette ['153'] | Pending | |
| 159 | Abetting mutiny, or attempting to seduce a soldier, sailor or airman f | LR-24 | consistent_with_gazette | delete: transcription ['subject', 'to', 'the', 'acts', 'referred', 'to', 'in', 'section', '165'] vs Gazette [] | Pending | |
| 167 | Persons subject to certain Acts | LR-24 | consistent_with_gazette | delete: transcription ['army', 'act', '1950', 'the', 'indian', 'navy', 'discipline', 'act', '1934', 'or', 'the'] vs Gazette [] | Pending | |
| 178 | Counterfeiting coin, government stamps, currency-notes or bank-notes | — | consistent_with_gazette | missing Gazette words not transcribed: ['as'] | Pending | |
| 179 | Using as genuine, forged or counterfeit coin, Government stamp, curren | — | consistent_with_gazette | missing Gazette words not transcribed: ['imports', 'or', 'exports', 'or'] | Pending | |
| 180 | Possession of forged or counterfeit coin, Government stamp, currency-n | — | consistent_with_gazette | delete: transcription ['issued', 'by', 'government', 'for', 'the', 'purpose', 'of', 'revenue'] vs Gazette [] | Pending | |
| 186 | Prohibition of fictitious stamps | LR-24 | consistent_with_gazette | replace: transcription ['176'] vs Gazette ['178'] | Pending | |
| 195 | Assaulting or obstructing public servant when suppressing riot, etc | — | consistent_with_gazette | missing Gazette words not transcribed: ['as', 'such', 'public', 'servant'] | Pending | |
| 196 | Promoting enmity between different groups on ground of religion, race, | — | consistent_with_gazette | replace: transcription ['racials'] vs Gazette ['racial'] | Pending | |
| 199 | Public servant disobeying direction under law | LR-24 | verified_against_gazette | replace: transcription ['174'] vs Gazette ['173'] | Pending | |
| 200 | Punishment for non-treatment of victim | LR-24 | consistent_with_gazette | replace: transcription ['449'] vs Gazette ['397'] | Pending | |
| 209 | Non-appearance in response to a proclamation under section 84 of Bhara | — | consistent_with_gazette | replace: transcription ['bhartiya'] vs Gazette ['bharatiya'] | Pending | |
| 211 | Omission to give notice or information to public servant by person leg | LR-24 | unverified | replace: transcription ['447'] vs Gazette ['394'] | Pending | |
| 212 | Furnishing false information | LR-24 | consistent_with_gazette | missing Gazette words not transcribed: ['a', 'wealthy', 'merchant'] | Pending | |
| 217 | False information, with intent to cause public servant to use his lawf | — | consistent_with_gazette | replace: transcription ['servan'] vs Gazette ['servant'] | Pending | |
| 223 | Disobedience to order duly promulgated by public servant | — | consistent_with_gazette | replace: transcription ['persons'] vs Gazette ['person'] | Pending | |
| 227 | Giving false evidence | — | no_punishment_clause | missing Gazette words not transcribed: ['threat', 'of', 'injury', 'to', 'public', 'servant', 'threat', 'of', 'injury', 'to', 'induce', 'person', 'to',… | Pending | |
| 228 | Fabricating false evidence | — | no_punishment_clause | replace: transcription ['puts'] vs Gazette ['p', 'uts'] | Pending | |
| 230 | Giving or fabricating false evidence with intent to procure conviction | — | consistent_with_gazette | missing Gazette words not transcribed: ['to'] | Pending | |
| 232 | Threatening any person to give false evidence | — | consistent_with_gazette | delete: transcription ['an'] vs Gazette [] | Pending | |
| 237 | Using as true such declaration knowing it to be false | LR-24 | consistent_with_gazette | replace: transcription ['234'] vs Gazette ['236'] | Pending | |
| 240 | Giving false information respecting an offence committed | LR-24 | consistent_with_gazette | replace: transcription ['236'] vs Gazette ['238'] | Pending | |
| 244 | Fraudulent claim to property to prevent its seizure as forfeited or in | — | consistent_with_gazette | replace: transcription ['practices'] vs Gazette ['practises'] | Pending | |
| 249 | Harbouring offender | LR-24 | consistent_with_gazette | replace: transcription ['97', '99', '172', '173', '174', '175', '301', '304', '305', '306', '320', '325'] vs Gazette ['103', '105', '307', 'sub', 'sec… | Pending | |
| 253 | Harbouring offender who has escaped from custody or whose apprehension | — | consistent_with_gazette | replace: transcription ['provision', 'does'] vs Gazette ['provisions', 'of', 'this', 'section', 'do'] | Pending | |
| 254 | Penalty for harbouring robbers or dacoits | — | consistent_with_gazette | missing Gazette words not transcribed: ['the', 'provisions', 'of'] | Pending | |
| 264 | Omission to apprehend, or sufferance of escape, on part of public serv | LR-24 | verified_against_gazette | replace: transcription ['257'] vs Gazette ['259'] | Pending | |
| 265 | Resistance or obstruction to lawful apprehension or escape or rescue i | LR-24 | consistent_with_gazette | replace: transcription ['260'] vs Gazette ['262'] | Pending | |
| 268 | Personation of an assessor | — | consistent_with_gazette | replace: transcription ['on'] vs Gazette ['as'] | Pending | |
| 269 | Failure by person released on bail or bond to appear in court | — | consistent_with_gazette | missing Gazette words not transcribed: ['bond'] | Pending | |
| 272 | Malignant act likely to spread infection of disease dangerous to life | — | consistent_with_gazette | replace: transcription ['the'] vs Gazette ['to'] | Pending | |
| 294 | Sale, etc., of obscene books, etc | — | consistent_with_gazette | replace: transcription ['more'] vs Gazette ['mo', 're'] | Pending | |
| 295 | Sale, etc., of obscene objects to child | — | consistent_with_gazette | replace: transcription ['below', 'the', 'age', 'of', 'eighteen', 'years'] vs Gazette ['any'] | Pending | |
| 301 | Trespassing on burial places, etc | — | consistent_with_gazette | replace: transcription ['sepulture'] vs Gazette ['sepulchre'] | Pending | |
| 303 | Theft | LR-01–08 | consistent_with_gazette | replace: transcription ['effects'] vs Gazette ['affects'] | Pending | |
| 304 | Snatching | LR-01–08 | consistent_with_gazette | replace: transcription ['moveable'] vs Gazette ['movable'] | Pending | |
| 308 | Extortion | — | consistent_with_gazette | replace: transcription ['sings'] vs Gazette ['signs'] | Pending | |
| 316 | Criminal breach of trust | LR-01–08 | unverified | missing Gazette words not transcribed: ['dishonest', 'misappropriation', 'of', 'property', 'possessed', 'by', 'deceased', 'person', 'at', 'the', 'time… | Pending | |
| 317 | Stolen property | — | consistent_with_gazette | replace: transcription ['property'] vs Gazette ['propert', 'y'] | Pending | |
| 318 | Cheating | LR-01–08 | consistent_with_gazette | replace: transcription ['diamond'] vs Gazette ['diamonds'] | Pending | |
| 321 | Dishonestly or fraudulently preventing debt being available for credit | — | consistent_with_gazette | replace: transcription ['debt'] vs Gazette ['debts'] | Pending | |
| 323 | Dishonest or fraudulent removal or concealment of property | — | unverified | replace: transcription ['description'] vs Gazette ['d', 'escription'] | Pending | |
| 324 | Mischief | LR-01–08 | consistent_with_gazette | replace: transcription ['cause'] vs Gazette ['cau', 'se'] | Pending | |
| 330 | House-trespass and house-breaking | — | no_punishment_clause | replace: transcription ['housetrespass'] vs Gazette ['house', 'trespass'] | Pending | |
| 335 | Making a false document | — | no_punishment_clause | replace: transcription ['mental', 'illness'] vs Gazette ['unsoundness', 'of', 'mind'] | Pending | |
| 338 | Forgery of valuable security, will, etc | — | consistent_with_gazette | replace: transcription ['acquaintance'] vs Gazette ['acquittance'] | Pending | |
| 339 | Having possession of document described in section 337 or 338, knowing | LR-24 | consistent_with_gazette | replace: transcription ['335'] vs Gazette ['337'] | Pending | |
| 341 | Making or possessing counterfeit seal, etc., with intent to commit for | LR-24 | verified_against_gazette | replace: transcription ['336'] vs Gazette ['338'] | Pending | |
| 342 | Counterfeiting device or mark used for authenticating documents descri | LR-24 | consistent_with_gazette | replace: transcription ['336', 'of', 'this', 'sanhita'] vs Gazette ['338'] | Pending | |
| 349 | Selling goods marked with a counterfeit property mark | — | consistent_with_gazette | replace: transcription ['prove'] vs Gazette ['proves'] | Pending | |
| 351 | Criminal intimidation | LR-01–08 | consistent_with_gazette | missing Gazette words not transcribed: ['another'] | Pending | |
| 353 | Statements conducing to public mischief | — | consistent_with_gazette | replace: transcription ['tranquility'] vs Gazette ['tranquillity'] | Pending | |
| 356 | Defamation | — | consistent_with_gazette | replace: transcription ['say'] vs Gazette ['says'] | Pending | |
| 357 | Breach of contract to attend on and supply wants of helpless person | — | consistent_with_gazette | replace: transcription ['mental', 'illness'] vs Gazette ['unsoundness', 'of', 'mind'] | Pending | |

### A.2 Possibly incomplete (56 records)

| Section | Title (stored) | Item | Punishment status | First automated difference | Review status | Notes / decision |
|---|---|---|---|---|---|---|
| 14 | Act done by a person bound, or by mistake of fact believing himself bo | — | no_punishment_clause | missing Gazette words not transcribed: ['punishment', 'of', 'person', 'guilty', 'of', 'one', 'of', 'several', 'offences', 'judgment', 'stating', 'that… | Pending | |
| 19 | Act likely to cause harm, but done without criminal intent, and to pre | — | no_punishment_clause | (coverage below 90%; no ordered difference) | Pending | |
| 21 | Act of a child above seven and under twelve of immature understanding | — | no_punishment_clause | missing Gazette words not transcribed: ['years', 'of', 'age'] | Pending | |
| 32 | Act to which a person compelled by threats | — | no_punishment_clause | missing Gazette words not transcribed: ['that'] | Pending | |
| 35 | Right of private defence of the body and of property | — | no_punishment_clause | missing Gazette words not transcribed: ['communication', 'made', 'in', 'good', 'faith', 'act', 'to', 'which', 'a', 'person', 'is', 'compelled', 'by', … | Pending | |
| 38 | When the right of private defence of the body extends to causing death | — | no_punishment_clause | missing Gazette words not transcribed: ['right', 'of', 'private', 'defence', 'against', 'act', 'of', 'a', 'person', 'of', 'unsound', 'mind', 'etc', 'a… | Pending | |
| 44 | Right of private defence against deadly assault when there is risk of  | — | no_punishment_clause | missing Gazette words not transcribed: ['when', 'such', 'right', 'extends', 'to', 'causing', 'any', 'harm', 'other', 'than', 'death', 'commencement', … | Pending | |
| 48 | Abetment outside India for offence in India | — | no_punishment_clause | (coverage below 90%; no ordered difference) | Pending | |
| 52 | Abettor when liable to cumulative punishment for act abetted and for a | — | no_punishment_clause | missing Gazette words not transcribed: ['punishment', 'of', 'abetment', 'if', 'act', 'abetted', 'is', 'committed', 'in', 'consequence', 'and', 'where'… | Pending | |
| 55 | Abetment of offence punishable with death or imprisonment for life | — | consistent_with_gazette | missing Gazette words not transcribed: ['and'] | Pending | |
| 61 | Criminal conspiracy | — | consistent_with_gazette | missing Gazette words not transcribed: ['with', 'the', 'common', 'object'] | Pending | |
| 62 | Punishment for attempting to commit offences punishable with imprisonm | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 65 | Punishment for rape in certain cases | — | consistent_with_gazette | missing Gazette words not transcribed: ['sub'] | Pending | |
| 70 | Gang rape | — | unverified | missing Gazette words not transcribed: ['imprisonment', 'for'] | Pending | |
| 82 | Marrying again during lifetime of husband or wife | — | consistent_with_gazette | missing Gazette words not transcribed: ['stalking', 'word', 'gesture', 'or', 'act', 'intended', 'to', 'insult', 'modesty', 'of', 'a', 'woman', 'dowry'… | Pending | |
| 88 | Causing miscarriage | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 97 | Kidnapping or abducting child under ten years with intent to steal fro | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 100 | Culpable homicide | — | no_punishment_clause | missing Gazette words not transcribed: ['1'] | Pending | |
| 124 | Voluntarily causing grievous hurt by use of acid, etc | — | unverified | missing Gazette words not transcribed: ['sub'] | Pending | |
| 131 | Punishment for assault or criminal force otherwise than on grave provo | — | consistent_with_gazette | missing Gazette words not transcribed: ['1'] | Pending | |
| 135 | Assault or criminal force in attempt wrongfully to confine a person | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 146 | Unlawful compulsory labour | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 153 | Waging war against Government of any foreign State at peace with the G | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 161 | Abetment of assault by soldier, sailor or airman on his superior offic | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 170 | Bribery | — | no_punishment_clause | missing Gazette words not transcribed: ['abetment', 'of', 'such', 'assault', 'if', 'assault', 'committed', 'abetment', 'of', 'desertion', 'of', 'soldi… | Pending | |
| 175 | False statement in connection with an election | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 177 | Failure to keep election accounts | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 181 | Making or possessing instruments or materials for forging or counterfe | — | consistent_with_gazette | missing Gazette words not transcribed: ['or'] | Pending | |
| 188 | Unlawfully taking coining instrument from mint | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 192 | Wantonly giving provocation with intent to cause riot- if rioting be c | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 198 | Public servant disobeying law, with intent to cause injury to any pers | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 205 | Wearing garb or carrying token used by public servant with fraudulent  | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 206 | Absconding to avoid service of summons or other proceeding | — | unverified | missing Gazette words not transcribed: ['be'] | Pending | |
| 221 | Obstructing public servant in discharge of public functions | — | unverified | missing Gazette words not transcribed: ['and'] | Pending | |
| 222 | Omission to assist public servant when bound by law to give assistance | — | unverified | missing Gazette words not transcribed: ['and'] | Pending | |
| 226 | Attempt to commit suicide to compel or restraint exercise of lawful po | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 229 | Punishment for false evidence | — | consistent_with_gazette | missing Gazette words not transcribed: ['stage'] | Pending | |
| 239 | Intentional omission to give information of offence by person bound to | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 245 | Fraudulently suffering decree for sum not due | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 251 | Offering gift or restoration of property in consideration of screening | — | verified_against_gazette | missing Gazette words not transcribed: ['shall'] | Pending | |
| 252 | Taking gift to help to recover stolen property, etc | — | verified_against_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 255 | Public servant disobeying direction of law with intent to save person  | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 260 | Intentional omission to apprehend on the part of public servant bound  | — | unverified | missing Gazette words not transcribed: ['public', 'servant', 'framing', 'incorrect', 'record', 'or', 'writing', 'with', 'intent', 'to', 'save', 'perso… | Pending | |
| 263 | Resistance or obstruction to lawful apprehension of another person | — | unverified | missing Gazette words not transcribed: ['or'] | Pending | |
| 270 | Public nuisance | — | no_punishment_clause | (coverage below 90%; no ordered difference) | Pending | |
| 281 | Rash driving or riding on a public way | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 290 | Negligent conduct with respect to pulling down, repairing or construct | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 300 | Disturbing religious assembly | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 302 | Uttering words, etc., with deliberate intent to wound religious feelin | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 312 | Attempt to commit robbery or dacoity when armed with deadly weapon | — | verified_against_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 313 | Punishment for belonging to gang of robbers, etc | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 322 | Dishonest or fraudulent execution of deed of transfer containing false | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 327 | Mischief with intent to destroy or make unsafe a rail, aircraft, decke | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 336 | Forgery | — | consistent_with_gazette | missing Gazette words not transcribed: ['forgery', '21', 'of', '2000'] | Pending | |
| 345 | Property mark | — | consistent_with_gazette | (coverage below 90%; no ordered difference) | Pending | |
| 358 | Repeal and savings | — | no_punishment_clause | (coverage below 90%; no ordered difference) | Pending | |

