"""
Email Draft Preparation and Gated Transmission Module (Checkpoint P2.5).

Governing Principles:
1. Prepares formatted email drafts containing complaint summaries and attached PDF metadata.
2. STRICT CONFIRMATION GATE: Requires user review and explicit confirmation before external email transmission.
3. NEVER automatically sends emails. Status remains 'draft_pending_user_confirmation' until explicit user sign-off.
4. Distinguishes draft preparation, user review, screening, verification, and official registration.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EmailAttachmentMetadata(BaseModel):
    file_name: str
    file_size_bytes: int
    sha256_hash: str
    mime_type: str = "application/pdf"
    storage_key: Optional[str] = None


class PreparedEmailDraft(BaseModel):
    draft_id: str
    complaint_number: str
    recipient_email: str
    recipient_type: str  # 'complainant', 'police_nodal', 'legal_aid'
    subject: str
    body_text: str
    body_html: Optional[str] = None
    attachments: List[EmailAttachmentMetadata] = Field(default_factory=list)
    user_confirmation_required: bool = True
    user_confirmed: bool = False
    transmission_status: str = "draft_pending_user_confirmation"
    submission_disclaimer: str = (
        "CONFIRMATION REQUIRED: This is a citizen draft complaint. It has NOT been "
        "transmitted to the police. User review and explicit confirmation are required "
        "prior to any outbound email dispatch."
    )


def prepare_complaint_email_draft(
    compiled_record: dict,
    recipient_email: Optional[str] = None,
    recipient_type: str = "complainant",
    pdf_attachment: Optional[EmailAttachmentMetadata] = None
) -> PreparedEmailDraft:
    """
    Constructs a formal email draft from a compiled complaint record.
    Strictly holds transmission pending user confirmation.
    """
    complaint_no = compiled_record.get("complaint_number", "DRAFT-RECORD")
    complainant = compiled_record.get("complainant") or {}
    report_type = compiled_record.get("report_type", "general_complaint")
    is_missing = report_type == "missing_person_report"
    
    target_email = recipient_email or complainant.get("email") or "not_provided@bandhoo.local"
    target_name = complainant.get("full_name") or "Citizen Complainant"

    if is_missing:
        subject = f"URGENT: Missing Person Citizen Report Draft - Ref {complaint_no}"
    else:
        subject = f"Bandhoo Citizen Complaint Draft - Ref {complaint_no}"

    # Body composition
    body_lines = [
        f"Dear {target_name},",
        "",
        f"This email contains your prepared citizen complaint draft (Reference: {complaint_no}).",
        "",
        "STATUS: DRAFT ONLY (NOT SUBMITTED TO POLICE)",
        "Please note: Bandhoo does not submit complaints directly to the police. This draft has been "
        "compiled from your statements and is ready for your review and submission to the police station.",
        "",
    ]

    if is_missing:
        mp = compiled_record.get("missing_person_details") or {}
        body_lines += [
            "MISSING PERSON DETAILS:",
            f"- Name: {mp.get('full_name')}",
            f"- Age: {mp.get('age')}",
            f"- Last Seen: {mp.get('last_seen_datetime')} at {mp.get('last_seen_location')}",
            "",
            "STATUTORY REMINDER: Under Supreme Court directives (Bachpan Bachao Andolan v. Union of India), "
            "there is NO 48-hour or 24-hour waiting period. Please visit the police station immediately.",
            "",
        ]

    j = compiled_record.get("jurisdiction_assessment") or {}
    if j.get("station"):
        body_lines.append(f"Estimated Jurisdictional Police Station: {j['station']}")
    else:
        body_lines.append("Police Jurisdiction: Requires station confirmation.")

    body_lines += [
        "",
        "Attached Document:",
        f"- {pdf_attachment.file_name} (SHA-256: {pdf_attachment.sha256_hash[:16]}...)" if pdf_attachment else "- PDF generated and ready for download.",
        "",
        "To transmit or print this report, please review the attached document and confirm.",
        "",
        "Regards,",
        "Bandhoo Legal Assistance Engine"
    ]

    attachments_list = [pdf_attachment] if pdf_attachment else []

    import uuid
    return PreparedEmailDraft(
        draft_id=str(uuid.uuid4()),
        complaint_number=complaint_no,
        recipient_email=target_email,
        recipient_type=recipient_type,
        subject=subject,
        body_text="\n".join(body_lines),
        attachments=attachments_list,
        user_confirmation_required=True,
        user_confirmed=False,
        transmission_status="draft_pending_user_confirmation"
    )
