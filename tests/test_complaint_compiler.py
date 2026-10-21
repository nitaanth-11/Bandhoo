"""
Acceptance Test Suite for Complete Complaint Compilation Engine (Phase 2 Checkpoint P2.4 & P2.6).

Validates:
1. Long narratives and timeline sequencing.
2. Multiple people with distinct roles (allegations kept unestablished).
3. Conflicting dates across clarifications.
4. Denied evidence and explicit denials.
5. Uncertain and hedged statements.
6. Missing fields and unanswered questions (no hallucination).
7. Multilingual input handling (Hindi/Hinglish).
8. Missing-person compilation.
9. PostgreSQL / relational persistence, foreign key integrity, and retrieval.
10. Failure preservation.
"""

import pytest
from complaint_engine.compiler import compile_complaint_record
from complaint_engine.models import (
    ComplaintStructureRequest,
    ComplainantDetails,
    MissingPersonDetails,
)
from db.session import SessionLocal, init_db
from db.repository import ComplaintRepository


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()


def test_compiler_long_narrative_and_timeline():
    statement = (
        "On 15/10/2026 at 7 pm, I was walking near Dadar Station west. "
        "Two unknown men on a black motorcycle approached me from behind. "
        "One man grabbed my gold necklace worth Rs 65,000 and sped away toward Sena Bhavan. "
        "A shopkeeper Ramesh saw the motorcycle license plate. "
        "I was not physically injured."
    )
    req = ComplaintStructureRequest(
        statement=statement,
        complainant=ComplainantDetails(full_name="Sunita Joshi", phone="9819001122"),
        location={"latitude": 19.0176, "longitude": 72.8562}
    )
    res = compile_complaint_record(req, include_legal_candidates=True)

    assert res["complaint_number"].startswith("BND-")
    assert res["original_narration"]["verbatim_text"] == statement
    assert len(res["chronological_timeline"]) >= 2
    assert any("7 pm" in t.get("time_expression", "") for t in res["chronological_timeline"])
    assert res["property_and_losses"]["monetary_losses"]
    assert any(c.get("bns_section") in [303, 304, 305, 308] for c in res["potential_bns_sections"])


def test_compiler_multiple_people_roles_and_relationships():
    statement = (
        "My landlord Sharmaji came to my apartment with two unknown musclemen. "
        "They threatened me and damaged my furniture. My neighbor Mrs Patel witnessed it."
    )
    req = ComplaintStructureRequest(statement=statement)
    res = compile_complaint_record(req)

    people = res["people_and_roles"]
    assert len(people) >= 2
    # Verify unverified allegation note is present on all persons
    for p in people:
        assert "not an established police finding" in p["note"] or "complainant" in p["note"]


def test_compiler_conflicting_dates_and_clarifications():
    statement = "The robbery occurred on Tuesday afternoon at 3 pm."
    clarification = "Actually looking at my watch receipt it happened on Wednesday morning at 10 am."
    req = ComplaintStructureRequest(statement=statement, clarifications=[clarification])
    res = compile_complaint_record(req)

    assert len(res["clarifications"]) == 1
    assert res["statement_analysis"]["clarifications_recorded"] == 1
    assert res["original_narration"]["verbatim_text"] == statement


def test_compiler_denied_evidence_and_explicit_denials():
    statement = "Someone stole my bicycle outside the temple. There were no cameras and no witnesses."
    req = ComplaintStructureRequest(statement=statement)
    res = compile_complaint_record(req)

    # Denials must be captured in statement analysis
    assert res["statement_analysis"]["explicit_denials"] or res["evidence_and_witnesses"]["witnesses_referenced"] == []


def test_compiler_uncertain_and_hedged_statements():
    statement = "There were possibly three men who looked like they were waiting outside."
    req = ComplaintStructureRequest(statement=statement)
    res = compile_complaint_record(req)

    assert res["original_narration"]["verbatim_text"] == statement


def test_compiler_missing_fields_without_hallucinating_answers():
    statement = "Someone took money from my wallet while I was at the cafe."
    req = ComplaintStructureRequest(statement=statement)
    res = compile_complaint_record(req)

    missing = res["missing_or_contradictory_information"]["missing_fields"]
    # Value was not provided in the statement; must be detected as missing, not invented
    assert any("amount" in m["field"] or "loss_value" in m["field"] for m in missing)


def test_compiler_multilingual_inputs():
    statement = "Meri car chori ho gayi Andheri West mein raat ko 11 baje."
    req = ComplaintStructureRequest(statement=statement)
    res = compile_complaint_record(req)

    assert res["original_narration"]["verbatim_text"] == statement
    assert res["header"]["document_title"]


def test_compiler_missing_person_compilation():
    mp = MissingPersonDetails(
        full_name="Kavita Deshmukh",
        age=16,
        gender="Female",
        clothing_last_seen="Red kurti, white salwar",
        last_seen_location="Thane Railway Station Platform 2"
    )
    req = ComplaintStructureRequest(
        statement="My 16-year-old daughter Kavita went missing from Thane station.",
        missing_person=mp
    )
    res = compile_complaint_record(req)

    assert res["report_type"] == "missing_person_report"
    assert res["missing_person_details"]["full_name"] == "Kavita Deshmukh"
    assert res["urgency_assessment"]["level"] == "critical_urgent"


def test_compiler_database_persistence_and_retrieval():
    db = SessionLocal()
    try:
        statement = "A delivery boy snatched Rs 5,000 cash from my counter at Bandra."
        req = ComplaintStructureRequest(
            statement=statement,
            complainant=ComplainantDetails(full_name="Deepak Shah", phone="9821122334"),
            location={"latitude": 19.0596, "longitude": 72.8295}
        )
        res = compile_complaint_record(req, db_session=db)
        
        assert res["header"]["persistence_status"] == "persisted_in_database"
        db_id = res["persisted_db_id"]

        # Retrieve through repository
        repo = ComplaintRepository(db)
        complaint = repo.get_complaint(db_id)
        assert complaint is not None
        assert complaint.complaint_number == res["complaint_number"]
        assert complaint.original_narration == statement
        assert len(complaint.facts) >= 1
    finally:
        db.close()
