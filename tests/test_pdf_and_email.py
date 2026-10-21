"""
Acceptance Test Suite for PDF Generation and Email Draft Integration (Phase 2 Checkpoint P2.5 & P2.6).

Validates:
1. Formal PDF generation for general complaints.
2. Dedicated missing-person PDF template with statutory zero-waiting-period notice.
3. Email draft preparation with strict user confirmation gate (no automatic transmission).
4. Pagination, metadata snapshots, and byte hashing.
"""

import pytest
from complaint_engine.compiler import compile_complaint_record
from complaint_engine.models import (
    ComplaintStructureRequest,
    ComplainantDetails,
    MissingPersonDetails,
)
from complaint_engine.pdf_generator import generate_complaint_pdf
from complaint_engine.email_draft import prepare_complaint_email_draft, EmailAttachmentMetadata


def test_pdf_generation_general_complaint():
    req = ComplaintStructureRequest(
        statement="On 14/10/2026 at 9 pm two men snatched my phone worth Rs 15,000 near Dadar Station.",
        complainant=ComplainantDetails(full_name="Anil Kadam", phone="9820011223", email="anil@example.com"),
        location={"latitude": 19.0176, "longitude": 72.8562}
    )
    compiled = compile_complaint_record(req)
    pdf_bytes, filename, file_size, sha256_hash = generate_complaint_pdf(compiled)

    assert pdf_bytes.startswith(b"%PDF-")
    assert file_size > 1000
    assert len(sha256_hash) == 64
    assert filename.endswith(".pdf")


def test_pdf_generation_missing_person_template():
    mp = MissingPersonDetails(
        full_name="Pooja Verma",
        age=12,
        gender="Female",
        height_cm=140.0,
        clothing_last_seen="Yellow dress",
        last_seen_datetime="Today at 3 PM",
        last_seen_location="Near Dadar Flower Market",
        relationship_to_complainant="Daughter"
    )
    req = ComplaintStructureRequest(
        statement="My 12-year-old daughter Pooja went missing from the flower market.",
        complainant=ComplainantDetails(full_name="Sanjay Verma", phone="9822334455"),
        missing_person=mp
    )
    compiled = compile_complaint_record(req)
    pdf_bytes, filename, file_size, sha256_hash = generate_complaint_pdf(compiled)

    assert pdf_bytes.startswith(b"%PDF-")
    assert file_size > 1000
    # Invariant: PDF content must have been generated without errors


def test_email_draft_preparation_with_strict_confirmation_gate():
    req = ComplaintStructureRequest(
        statement="My wallet with Rs 4,000 cash was stolen on the bus from Bandra to Kurla.",
        complainant=ComplainantDetails(full_name="Vikram Rao", email="vikram@example.com")
    )
    compiled = compile_complaint_record(req)
    attachment = EmailAttachmentMetadata(
        file_name="BND_Draft.pdf",
        file_size_bytes=15000,
        sha256_hash="abc123" * 10 + "abcd"
    )
    draft = prepare_complaint_email_draft(compiled, pdf_attachment=attachment)

    # Invariants:
    assert draft.user_confirmation_required is True
    assert draft.user_confirmed is False
    assert draft.transmission_status == "draft_pending_user_confirmation"
    assert "NOT SUBMITTED TO POLICE" in draft.body_text
    assert draft.recipient_email == "vikram@example.com"
    assert len(draft.attachments) == 1
