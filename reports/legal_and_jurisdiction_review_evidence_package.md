# Bandhoo Legal and Jurisdiction Review Evidence Package

**Document Identifier:** EVIDENCE-PACK-2026-V1  
**Status:** Completed / Awaiting Authorised Reviewer Decision  
**Checkpoint:** Checkpoint 4 — Legal and Jurisdiction Review  
**Audience:** Qualified Legal Reviewers (QLR 1, QLR 2), Legal Adjudicator (ADJ), Project Owners (PO), Evaluation Lead (EL), and Maintainers (MNT).

---

> [!WARNING]
> **No legal determinations are made within this package.**
> In strict accordance with the project rules, unresolved statutory interpretations and boundary legal provenance questions are compiled with neutral primary-source evidence for qualified reviewers. **All associated release blockers (RB-02, RB-03, RB-06, RB-07, RB-08, RB-08.a, RB-09, RB-10, RB-11, RB-12, RB-13, RB-14, RB-15, RB-16) remain OPEN.**

---

# PART A: Legal Evidence Package — BNSS Section 173(3) & State Amendments

## 1. Statutory Architecture & Context

### 1.1 Central Statutory Text: BNSS Section 173(3)
Source: *The Gazette of India Extraordinary*, 25 December 2023 (Act No. 46 of 2023), Single authoritative PRS copy (G-BNSS):

> **Section 173(3):**
> *"Without prejudice to the provisions contained in section 175, on receipt of information relating to the commission of any cognizable offence, which is made punishable for three years or more but less than seven years, the officer in charge of the police station may with the prior permission from an officer not below the rank of Deputy Superintendent of Police, considering the nature and gravity of the offence,—*  
> *(i) proceed to conduct preliminary enquiry to ascertain whether there exists a prima facie case for proceeding in the matter within a period of fourteen days; or*  
> *(ii) proceed with investigation when there exists a prima facie case."*

### 1.2 Surrounding Procedural Mandates
* **BNSS s.173(1)**: General rule governing information in cognizable cases. Every information disclosing a cognizable offence shall be reduced to writing and recorded (mandatory FIR registration).
* **BNSS s.174(1)–(2)**: Non-cognizable cases. Substance entered in the station diary (NCR); informant referred to the Magistrate; no police investigation without a Magistrate's order.
* **BNSS s.174(4)**: Multi-offence rule. *"Where a case relates to two or more offences of which at least one is cognizable, the case shall be deemed to be a cognizable case, notwithstanding that the other offences are non-cognizable."*
* **BNSS s.175**: Power of Magistrates to inquire into offences and supervise police action, explicitly preserved by the opening clause of 173(3).

---

## 2. Supreme Court Case-Law Dossier

Bandhoo has retrieved and verified three official Supreme Court authorities bearing on preliminary enquiries and Section 173(3):

| Citation | Case & Coram | Date & Host | Verified SHA-256 | Key Legal Finding / Ratio |
| :--- | :--- | :--- | :--- | :--- |
| **2025 INSC 410** | *Imran Pratapgadhi v. State of Gujarat*<br/>Abhay S. Oka and Ujjal Bhuyan, JJ.<br/>Crl. A. No. 1545 of 2025 | 28 March 2025<br/>`api.sci.gov.in` (TLS verified) | `896f08f97519248a...` | **Para 42.1–42.3**: Held that where an offence carries imprisonment of 7 years or more (e.g. BNS s.57 / 308(2)), **Section 173(3) has no application**. Direct registration of FIR under Section 173(1) is mandatory. Section 173(3) enquiry is strictly restricted to offences with punishment $\ge 3$ years and $< 7$ years. |
| **2026 INSC 244** | *Ashish Dave v. State of Rajasthan*<br/>Vikram Nath and Sandeep Mehta, JJ.<br/>Crl. A. aris. SLP (Crl) 19369/2025 | 27 February 2026<br/>`api.sci.gov.in` (TLS verified) | `3350c58215253837...` | Cites *Imran Pratapgadhi* with approval ((2026) 1 SCC 721). Reaffirms that Section 173(3) is an exception to mandatory FIR registration and cannot be invoked beyond its explicit statutory bounds. |
| **[2013] 14 S.C.R. 713**<br/>((2014) 2 SCC 1) | *Lalita Kumari v. Govt. of U.P. & Ors.*<br/>P. Sathasivam, CJI, Chauhan, Desai, Gogoi, Bobde, JJ. | 12 November 2013<br/>`cdnbbsr.s3waas.gov.in` | `2dee8917c4dd55d6...` | **Para 120 (111 in Manupatra)**: Registration of FIR mandatory under Section 154 CrPC if cognizable offence disclosed. Preliminary inquiry permitted only in defined categories (matrimonial, commercial, medical negligence, corruption, delay) with general 15-day limit. |

---

## 3. Unresolved Legal Questions for Qualified Reviewers

The following questions are submitted to QLR 1, QLR 2, and ADJ without developer predetermination:

| Question ID | Blocker / Checklist Ref | Statutory Element at Issue | Bandhoo's Current Working Assumption (Pending Review) | Questions for QLR Decision |
| :--- | :--- | :--- | :--- | :--- |
| **QR-A** | **RB-09** / LR-12 | "punishable for three years or more but less than seven years" | Reads the boundary by **maximum term**. Offences with a maximum of exactly 7 years (e.g. BNS 117(2), 305, 306, 316(3)–(4), 318(4)) are treated as **outside** 173(3). | Does "less than seven years" exclude offences whose maximum is exactly 7 years? How are offences with minimum terms (e.g. "not less than 1 year") or alternative terms treated? |
| **QR-B** | **RB-08.a** / Q-01 | "within a period of fourteen days" | Attaches the 14-day limit to the **preliminary enquiry** (limb i), not to obtaining DSP permission. | Does "within a period of fourteen days" govern the completion of the enquiry, DSP permission, or both? |
| **QR-C** | **RB-10** / LR-13 | Multi-offence complaints & BNSS 174(4) | If one offence carries $<7$ years and another carries $\ge 7$ years, 173(3) is treated as inapplicable to the case. | May an officer conduct a 173(3) preliminary enquiry on a 3–7 year offence if an accompanying alleged offence carries $\ge 7$ years? |
| **QR-D** | **RB-11** / LR-14 | BNSS 173(3) vs *Lalita Kumari* | Engine notes both; does not assert that 173(3) supersedes *Lalita Kumari* exceptions. | Does BNSS 173(3) codify and exhaust preliminary inquiries, or do the non-statutory *Lalita Kumari* categories (e.g. medical negligence, commercial disputes) survive alongside it? |
| **QR-E** | **RB-06** / LR-09 | BNS s.303(2) theft proviso below ₹5,000 | Engine leaves classification **unknown** because "convicted for the first time" cannot be known at FIR stage. | May theft of property under ₹5,000 with restored property be treated as non-cognizable at intake stage before trial? |
| **QR-F** | **RB-12** / LR-15 | BNS s.324(4) vs Schedule I row | Mismatch: Section text says "less than one lakh", Schedule row says "less than 2 lakh". | For mischief between ₹1 lakh and ₹2 lakh, which classification governs: cognizable (per text) or non-cognizable (per Schedule)? |

---

## 4. Maharashtra State Amendments Review

### 4.1 Primary Source Documents Inspected
1. **Maharashtra L.C. Bill No. VI of 2026**: Passed by Legislative Council on 24 March 2026 (Clause 6).
2. **Maharashtra L.C. Bill No. XVII of 2026**: Passed by Legislative Council on 8 July 2026 (`mls.org.in`, Clause 7).

### 4.2 Proposed Amendment Text
Both bills propose amending BNSS Section 173(3)(i) for Maharashtra by substituting **"six weeks"** for **"fourteen days"**.

### 4.3 Enactment & Legal Status: UNVERIFIED / UNKNOWN
* **Zero Evidence of Enactment**: Exhaustive review of the Maharashtra Government Gazette and Bombay High Court Library (Acts Nos. I–LIII of 2026) revealed **no enacted BNSS amendment Act**.
* **Constitutional Requirement**: Under Article 254(2) of the Constitution of India, a state amendment to a central criminal procedural statute requires Presidential assent to prevail over central law. No Presidential assent notification has been located.
* **Engine Decision**: The bills **cannot be treated as current law**. Bandhoo continues to apply the central 14-day statutory text, while recording that Maharashtra amendment enactment status remains unestablished.

---

# PART B: Jurisdiction & Spatial Evidence Package

## 5. Boundary Dataset Provenance, CRS & Licensing

### 5.1 Dataset Metadata & Provenance
* **File Path**: `mumbai_police_jurisdictions.geojson`
* **File Size**: 422,516 bytes (SHA-256: `a1718b3bbcd38d9de550b9f184b18df81dcfef01d4c539d7f3425c888c27a8f3`)
* **Feature Count**: 91 police station jurisdiction polygons.
* **Provenance**: **Unverified**. The dataset does not embed metadata specifying the official surveying agency (e.g. Mumbai Police Commissionerate vs Municipal Corporation of Greater Mumbai), date of delimitation, or revision gazette.
* **Licensing**: **Undocumented**. No explicit Open Government Data (OGD) license or public domain declaration is embedded. Public distribution requires administrative confirmation.

### 5.2 Coordinate Reference System (CRS) & Projection Mathematics
* **Native CRS**: WGS 84 (EPSG:4326), RFC 7946 GeoJSON specification, formatted in `[longitude, latitude]` order.
* **Distance Projection**: Local equirectangular planar approximation calibrated for Mumbai's latitude ($\approx 19.0^\circ$ N):
  $$kx = 111320.0 \times \cos(\text{radians}(\text{lat})) \approx 105,247\text{ m per degree longitude}$$
  $$ky = 110540.0\text{ m per degree latitude}$$
* **Geometric Distortion**: Over the 40 km north-south extent of Mumbai, error from planar equirectangular distance approximation compared to geodesic Vincenty distance is $<0.15\%$, well within consumer GPS noise tolerance.

---

## 6. The 100-Metre Buffer Threshold: Technical Justification & Validation

### 6.1 Urban Consumer GPS Accuracy Profile
* Under ideal open-sky conditions, mobile GPS accuracy is 5–15 metres.
* In Mumbai’s dense high-rise urban street canyons (e.g. Fort, Dadar, Lower Parel, Andheri), multipath reflection and building signal blockage degrade real-world mobile GPS accuracy to **30–80 metres**.
* IP and cellular-tower positioning fallbacks exhibit location errors between **150 and 800 metres**.

### 6.2 Empirical Topology Audit of the GeoJSON Dataset
An automated spatial topology audit of `mumbai_police_jurisdictions.geojson` was executed:
* **Holes**: 0 interior rings.
* **Pairwise Bounding Box Overlaps**: 279 pairs share overlapping bounding rectangles.
* **Boundary Segment Overlaps**: **170 boundary segment intersections/containments** exist where vertex coordinates of one station fall strictly inside the boundary of a neighbouring station (e.g. Cuffe Parade & Marine Drive: 10 overlapping vertices; Cuffe Parade & Colaba: 35 overlapping vertices; Nirmal Nagar & Kherwadi: 3 overlapping vertices).

```
                      +-------------------+
                      |   Station A       |
                      |          * (Point inside A, but 45m from border)
       - - - - - - - -|- - - - - - - - - -|- - - - - - 100m Buffer Zone
                      |                   |  --> Triggers "near_boundary"
       ===============+===================+=============== Border Line
                      |                   |  --> Ambiguity / Overlap Zone
       - - - - - - - -|- - - - - - - - - -|- - - - - -
                      |   Station B       |
                      +-------------------+
```

### 6.3 Safety Rationale for the 100-Metre Threshold
1. **Zero False Certainty**: A point within 100 metres of a border edge is at acute risk of being misassigned due to ordinary GPS jitter or polygon boundary discretization errors.
2. **Safe Failure Mode**: In all such cases, `assess_point()` outputs `status: "near_boundary"` with message:
   `"Police jurisdiction requires confirmation."`
   This prevents the engine from erroneously misdirecting a citizen to the wrong police station.

---

## 7. Polygon Containment & Ambiguity Handling

### 7.1 Point-in-Polygon Algorithm
Implemented in `complaint_engine/jurisdiction.py` via ray-casting (`_point_in_ring`) using Green's theorem for centroids and local equirectangular segment projection for distance calculation.

### 7.2 Exhaustive Status Taxonomy

| Status Code | Spatial Condition | Engine Behavior & Output | User-Facing Message |
| :--- | :--- | :--- | :--- |
| `inside` | Point strictly within exactly one polygon and $\text{distance} \ge 100$ m. | Returns `station: "<Name>"` and `distance_to_boundary_m`. | *"Map-based estimate from boundary data whose source is unverified; police to confirm."* |
| `near_boundary` | Point within exactly one polygon, but $\text{distance} < 100$ m. | Sets `station: None`. Routes to human/police review. | *"Police jurisdiction requires confirmation."* |
| `multiple` | Point lies inside two or more overlapping polygons. | Sets `station: None`. Overlap flagged in review log. | *"Police jurisdiction requires confirmation."* |
| `outside_all` | Point is outside all 91 Mumbai station polygons. | Sets `station: None`. | *"Police jurisdiction requires confirmation."* |
| `no_location` | Coordinates null, missing, or non-finite. | Sets `station: None`. | *"Police jurisdiction requires confirmation."* |
| `data_unavailable` | File read error or corrupted GeoJSON. | Sets `station: None`. System error logged. | *"Police jurisdiction requires confirmation."* |

---

## 8. Summary of Open Blockers Associated with Checkpoint 4

The following release blockers are maintained in **OPEN** status pending formal qualified review:

- **RB-02**: *Lalita Kumari* summary text and Supreme Court report citation review.
- **RB-03**: Acquisition and verification of second authoritative copy of BNS/BNSS.
- **RB-06**: BNS Section 303(2) theft proviso below ₹5,000 application at intake.
- **RB-07**: Property valuation rules under Section 303(2).
- **RB-08**: BNSS 173(3) procedure text and characterization of police discretion.
- **RB-08.a**: Attaching 14-day limit to preliminary enquiry in system prompt.
- **RB-09**: Range interpretation of "three years or more but less than seven years".
- **RB-10**: Application of BNSS 174(4) multi-offence rule at information stage.
- **RB-11**: Relationship between BNSS 173(3) and *Lalita Kumari* categories.
- **RB-12**: Resolution of BNS 324(4) vs First Schedule valuation mismatch.
- **RB-13**: First-conviction vs repeat-conviction theft term for 173(3) checks.
- **RB-16**: Procedural recommendation template accuracy and citizen suitability.

---
*End of Evidence Package Document EVIDENCE-PACK-2026-V1*
