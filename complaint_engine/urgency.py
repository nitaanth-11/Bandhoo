"""
Urgency and Risk Assessment for Complaints and Missing-Person Reports.

Core Mandate:
- NEVER impose a mandatory 48-hour or 24-hour waiting period for missing persons.
  Per the Supreme Court of India in Bachpan Bachao Andolan v. Union of India (2013) 5 SCC 1,
  and MHA/CCTNS standard operating procedures, any missing person report must be recorded
  immediately. For missing children (under 18), an FIR under Section 137 BNS is mandatory
  without preliminary inquiry.
- Urgent and high-risk cases are routed for immediate human review.
"""

from typing import List, Optional, Tuple
import re

from complaint_engine.models import MissingPersonDetails

HIGH_RISK_KEYWORDS = re.compile(
    r"\b(?:knife|gun|pistol|weapon|acid|rape|sexual|molest\w*|child|minor|kidnap\w*|abduct\w*|suicide|"
    r"kill\w*|murder\w*|threat\w* to (?:my |our )?life|unconscious|bleeding|ransom|hostage|extort\w*|"
    r"traffick\w*|dragged into (?:a |the )?(?:car|van|vehicle)|screaming|forced into|missing child)\b",
    re.I
)

VULNERABLE_KEYWORDS = re.compile(
    r"\b(?:dementia|alzheimer\w*|autis\w*|depress\w*|suicid\w*|disabled|handicapped|mentally challenged|"
    r"unwell|epilep\w*|heart condition|diabetic|insulin|cannot speak|mute|deaf|blind)\b",
    re.I
)

LEGAL_NO_WAITING_PERIOD_NOTICE = (
    "STATUTORY MANDATE: Immediate recording required. Under Supreme Court directives "
    "(Bachpan Bachao Andolan v. Union of India) and MHA Missing Person SOPs, NO 48-HOUR "
    "OR 24-HOUR WAITING PERIOD CAN BE IMPOSED. Police must enter details immediately in "
    "the Station General Diary and initiate search protocols."
)


def assess_urgency(
    text: str,
    missing_person: Optional[MissingPersonDetails] = None,
) -> Tuple[str, List[str], List[str]]:
    """
    Assesses urgency level and returns:
    (urgency_level, urgency_reasons, officer_action_items)
    urgency_level: 'standard', 'high', or 'critical_urgent'
    """
    reasons: List[str] = []
    actions: List[str] = []
    urgency_level = "standard"

    # 1. Missing Person Specific Rules
    if missing_person is not None:
        urgency_level = "high"
        reasons.append("Missing person report: immediate recording required (zero waiting period).")
        actions.append(
            "Enter details immediately in the Station General Diary (GD). "
            "Zero waiting period: NO 48-hour wait permitted."
        )

        # Minor (< 18)
        if missing_person.age is not None and missing_person.age < 18:
            urgency_level = "critical_urgent"
            reasons.append(f"Missing individual is a minor (age {missing_person.age}). Presumption of abduction/trafficking.")
            actions.append("MANDATORY: Register FIR under Section 137 BNS immediately without preliminary inquiry.")
            actions.append("Upload photo and details to TrackChild / CCTNS portal immediately.")
            actions.append("Alert Special Juvenile Police Unit (SJPU) and Child Welfare Officer.")
        elif missing_person.age is not None and missing_person.age >= 65:
            urgency_level = "critical_urgent"
            reasons.append(f"Missing individual is a senior citizen (age {missing_person.age}). High vulnerability.")
            actions.append("Alert senior citizen cell and alert local transport terminals.")

        # Medical vulnerability
        vuln_text = f"{missing_person.medical_conditions_or_vulnerabilities or ''} {text}"
        if VULNERABLE_KEYWORDS.search(vuln_text):
            urgency_level = "critical_urgent"
            reasons.append("Medical vulnerability or mental health condition reported.")
            actions.append("Notify hospitals, clinics, and emergency health centers in the vicinity.")

        # Suspicion of foul play
        concerns = f"{missing_person.known_suspects_or_concerns or ''} {text}"
        if HIGH_RISK_KEYWORDS.search(concerns):
            urgency_level = "critical_urgent"
            reasons.append("Foul play, abduction, or bodily harm concerns indicated.")
            actions.append("Deploy immediate field inquiry team to last seen location.")
            actions.append("Request CCTV preservation along last known route.")
            actions.append("Initiate mobile tower location / CDR preservation if number available.")

        actions.append("Broadcast physical description and photo across police wireless and PCR vans.")
        if missing_person.last_seen_location:
            actions.append(f"Conduct search and inquiries around last seen location: {missing_person.last_seen_location}.")

    # 2. General Narrative Harm Check
    elif HIGH_RISK_KEYWORDS.search(text):
        urgency_level = "critical_urgent"
        reasons.append("The account mentions potentially serious harm, weapons, violence, or life threats.")
        actions.append("Prioritise immediate human officer review and emergency response dispatch.")

    return urgency_level, reasons, actions
