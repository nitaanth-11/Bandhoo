"""
Readable complaint draft rendered from a structured report (graph.build_report).

The draft only re-presents the report: every detail is the complainant's own words in quotation marks,
with the statement it came from. It states that it is a draft, not an FIR, not submitted and not verified.
"""

from typing import List

REVIEW_LABELS = {
    "ready_for_police_review": "Ready for police review (not submitted; not yet reviewed by police)",
    "human_review_required": "Needs human review",
}
REVIEW_UNAVAILABLE_LABEL = "Review status unavailable; human review required"
DETAIL_SECTIONS = [
    ("People mentioned", "persons"),
    ("Dates and times", "dates_and_times"),
    ("Places", "locations"),
    ("Alleged actions", "alleged_actions"),
    ("Items lost or damaged", "items_lost_or_damaged"),
    ("Amounts", "losses"),
    ("Injuries mentioned", "injuries"),
    ("Weapons mentioned", "weapons_mentioned"),
    ("Vehicles", "vehicles"),
    ("Contact details mentioned", "contact_details_mentioned"),
    ("Witnesses mentioned", "witness_references"),
    ("Evidence mentioned in the account", "evidence_references_in_statement"),
]
MISSING_LABELS = {
    "open": "not provided",
    "unknown_to_complainant": "complainant says they do not know",
    "explicitly_denied": "stated as not applicable by the complainant",
    "not_determined": "could not be determined automatically; a person must read the statement",
}


def _quote(item: dict) -> str:
    marks = {"explicitly_denied": " [denied]", "uncertain": " [uncertain]"}.get(item.get("polarity"), "")
    sources = ", ".join(s["statement_id"] for s in item.get("spans") or [])
    return f"“{item['value']}”{marks} ({sources})"


def render_draft(report: dict) -> str:
    review = report.get("review") or {}
    lines: List[str] = [
        "COMPLAINT DRAFT – STRUCTURED RECORD (NOT AN FIR)",
        "Status: Draft only. Not submitted to the police. Not stored by Bandhoo. No information in it is verified "
        "unless listed under independently verified information.",
        f"Review status: {REVIEW_LABELS.get(review.get('route'), REVIEW_UNAVAILABLE_LABEL)}",
        f"Prepared: {report['header']['generated_at']} (workflow {report['header']['workflow_version']}, "
        f"{report['header']['extraction_mode']} extraction; processing {report.get('processing_status')})",
    ]
    coverage = report.get("language_coverage") or {}
    if coverage.get("coverage") == "limited":
        lines.append(f"Language: {coverage.get('note')}")

    complainant = report.get("complainant_details")
    if complainant:
        lines += [
            "",
            "COMPLAINANT DETAILS",
            f"Name: {complainant.get('full_name')}",
            f"Phone: {complainant.get('phone') or 'Not provided'}",
            f"Email: {complainant.get('email') or 'Not provided'}",
            f"Address: {complainant.get('address') or 'Not provided'}",
        ]

    mp = report.get("missing_person_details")
    if mp:
        age_str = f"{mp.get('age')}" if mp.get('age') is not None else "Not stated"
        minor_tag = " [MINOR - Mandatory Section 137 BNS Registration Required]" if mp.get('age') is not None and mp.get('age') < 18 else ""
        lines += [
            "",
            "MISSING PERSON DETAILS (IMMEDIATE ACTION REQUIRED - ZERO WAITING PERIOD APPLIES)",
            f"Full Name: {mp.get('full_name')}",
            f"Age: {age_str}{minor_tag}",
            f"Gender: {mp.get('gender') or 'Not stated'}",
            f"Last Seen: {mp.get('last_seen_datetime') or 'Not stated'} at {mp.get('last_seen_location') or 'Not stated'}",
            f"Physical Description: {mp.get('complexion') or 'complexion not stated'}, height {mp.get('height_cm') or 'unknown'} cm, marks: {mp.get('identifying_marks') or 'none stated'}",
            f"Clothing Last Seen: {mp.get('clothing_last_seen') or 'Not stated'}",
            f"Relationship to Complainant: {mp.get('relationship_to_complainant') or 'Not stated'}",
            f"Medical Vulnerabilities: {mp.get('medical_conditions_or_vulnerabilities') or 'None stated'}",
            "Statutory Notice: Under Supreme Court directives (Bachpan Bachao Andolan v. UOI), NO 48-hour or 24-hour waiting period is applicable. Record immediately.",
        ]

    lines += ["", "1. COMPLAINANT'S ACCOUNT (verbatim, as received)"]
    statements = report.get("complainant_statements") or []
    for s in statements:
        lines.append(f"{s['statement_id']} ({s['kind']}): {s['text']}")
    if not statements and report.get("received_input"):
        lines.append(f"Received, not processed: {report['received_input']['statement']}")

    lines += ["", "2. DETAILS FROM THE ACCOUNT (complainant's words; not verified)"]
    for label, key in DETAIL_SECTIONS:
        items = report.get(key) or []
        lines.append(f"{label}: " + ("; ".join(_quote(i) for i in items) if items else "none identified"))
    verified = report.get("independently_verified") or []
    lines.append("Independently verified information: " +
                 ("; ".join(f"{v.get('item_id') or v.get('evidence_id')} (police verification record)" for v in verified)
                  if verified else "none"))
    inferences = report.get("ai_inferences") or []
    lines.append("AI-generated inferences (not facts; require verification): " +
                 ("; ".join(_quote(i) for i in inferences) if inferences else "none"))

    lines += ["", "3. MISSING INFORMATION"]
    missing = report.get("missing_information") or []
    for m in missing:
        quote = f" (“{m['source_spans'][0]['quote']}”)" if m.get("source_spans") else ""
        lines.append(f"- {m['field'].replace('_', ' ')}: {MISSING_LABELS.get(m['status'], m['status'])}{quote}")
    if not missing:
        lines.append("- none identified")
    for q in report.get("questions_for_complainant") or []:
        lines.append(f"  Question for the complainant: {q}")

    lines += ["", "4. POSSIBLE INCONSISTENCIES (for clarification; both statements are preserved above)"]
    contradictions = report.get("contradictions") or []
    lines += [f"- {c['summary']}" for c in contradictions] or ["- none identified"]

    lines += ["", "5. SUPPORTING MATERIAL (supplied by the complainant)"]
    verified_ids = {v.get("evidence_id") for v in verified}
    evidence = report.get("supporting_evidence_provided") or []
    lines += [f"- {e['evidence_id']} ({e['evidence_type']}): " +
              ("verified by police record" if e["evidence_id"] in verified_ids else "supplied, not examined, not verified")
              for e in evidence] or ["- none supplied"]

    lines += ["", "6. JURISDICTION"]
    j = report.get("jurisdiction") or {}
    if j.get("status") == "inside" and j.get("station"):
        lines.append(f"- Map-based estimate: {j['station']} (boundary data unverified; police to confirm)")
    else:
        lines.append(f"- Police jurisdiction requires confirmation (map check: {j.get('status', 'not assessed')}).")

    lines += ["", "7. VERIFICATION CHECKLIST (for the receiving officer)"]
    lines += [f"- [ ] {item}" for item in report.get("verification_checklist_for_officer") or []]

    lines += ["", "8. FOR POLICE USE ONLY (to be completed by the receiving officer)",
              "Received by: ____________________  Date and time: ____________________",
              "Reference: ____________________  Action taken: ____________________"]
    return "\n".join(lines)
