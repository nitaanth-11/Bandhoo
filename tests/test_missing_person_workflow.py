"""
Unit tests for Missing-Person Reporting and Urgency Assessment Workflow (Phase 2 Checkpoint P2.1).

Key Invariants:
1. NEVER impose a mandatory 48-hour or 24-hour waiting period.
2. Minor missing persons (< 18) are critical_urgent; mandatory FIR under Section 137 BNS.
3. Vulnerable individuals (medical condition, elderly, foul play concerns) trigger immediate actions.
4. Clean existing complaint workflows without missing persons are 100% backward-compatible.
"""

import pytest
from complaint_engine import run_structuring
from complaint_engine.models import (
    ComplaintStructureRequest,
    ComplainantDetails,
    MissingPersonDetails,
)
from complaint_engine.urgency import assess_urgency, LEGAL_NO_WAITING_PERIOD_NOTICE


def test_missing_child_is_critical_urgent_and_requires_immediate_fir():
    mp = MissingPersonDetails(
        full_name="Aarav Sharma",
        age=9,
        gender="Male",
        height_cm=130.0,
        clothing_last_seen="Blue school uniform, black shoes",
        last_seen_datetime="2026-10-21 at 2 PM",
        last_seen_location="Outside Holy Cross High School, Kurla",
        relationship_to_complainant="Son",
    )
    req = ComplaintStructureRequest(
        statement="My 9-year-old son Aarav did not return home from school this afternoon. We checked everywhere.",
        complainant=ComplainantDetails(full_name="Ramesh Sharma", phone="9820011223"),
        missing_person=mp,
        location={"latitude": 19.0657, "longitude": 72.8794},
    )
    state = run_structuring(req)
    report = state["report"]

    assert report["review"]["route"] == "human_review_required"
    assert report["urgency_assessment"]["level"] == "critical_urgent"
    assert any("minor (age 9)" in r for r in report["urgency_assessment"]["reasons"])
    assert any("Section 137 BNS" in act for act in report["verification_checklist_for_officer"])
    assert "ZERO WAITING PERIOD" in report["draft_text"]
    assert "Section 137 BNS" in report["draft_text"]


def test_no_mandatory_waiting_period_ever_imposed_for_adult():
    # Adult missing for only 3 hours: police must NOT turn complainant away with a 48h wait rule
    mp = MissingPersonDetails(
        full_name="Pooja Verma",
        age=24,
        gender="Female",
        last_seen_datetime="Today at 10 AM (3 hours ago)",
        last_seen_location="Near Dadar Flower Market",
        relationship_to_complainant="Sister",
    )
    req = ComplaintStructureRequest(
        statement="My sister Pooja went to Dadar flower market 3 hours ago and her phone is switched off.",
        missing_person=mp,
    )
    state = run_structuring(req)
    report = state["report"]

    assert report["review"]["route"] == "human_review_required"
    assert report["urgency_assessment"]["level"] == "high"
    # Verify statutory notice is present
    assert "NO 48-HOUR OR 24-HOUR WAITING PERIOD CAN BE IMPOSED" in report["urgency_assessment"]["legal_mandate"]
    assert any("Zero waiting period: NO 48-hour wait permitted" in act for act in report["verification_checklist_for_officer"])


def test_vulnerable_missing_person_with_dementia():
    mp = MissingPersonDetails(
        full_name="Kishore Kulkarni",
        age=72,
        gender="Male",
        medical_conditions_or_vulnerabilities="Severe Alzheimer's dementia, diabetic, needs daily medication",
        last_seen_datetime="Yesterday evening",
        last_seen_location="Vile Parle East",
    )
    req = ComplaintStructureRequest(
        statement="My grandfather who has dementia walked out of the house yesterday evening and has not returned.",
        missing_person=mp,
    )
    state = run_structuring(req)
    report = state["report"]

    assert report["urgency_assessment"]["level"] == "critical_urgent"
    assert any("senior citizen" in r for r in report["urgency_assessment"]["reasons"])
    assert any("Medical vulnerability" in r for r in report["urgency_assessment"]["reasons"])
    assert any("hospitals, clinics" in act for act in report["verification_checklist_for_officer"])


def test_foul_play_and_abduction_concerns():
    mp = MissingPersonDetails(
        full_name="Rahul Nair",
        age=28,
        known_suspects_or_concerns="Was threatened by moneylenders; witnesses saw him forced into a white van",
        last_seen_location="Andheri Link Road",
    )
    req = ComplaintStructureRequest(
        statement="Rahul was kidnapped by men in a white van on Link Road after being threatened.",
        missing_person=mp,
    )
    state = run_structuring(req)
    report = state["report"]

    assert report["urgency_assessment"]["level"] == "critical_urgent"
    assert any("Foul play, abduction" in r for r in report["urgency_assessment"]["reasons"])
    assert any("CCTV preservation" in act for act in report["verification_checklist_for_officer"])
    assert any("mobile tower location" in act for act in report["verification_checklist_for_officer"])


def test_standard_complaint_without_missing_person_preserves_clean_behavior():
    req = ComplaintStructureRequest(
        statement="On 14/10/2026 at 9 pm a man took my bag at Dadar Market. I have a photo of him. My friend saw it. The bag cost Rs 2,000.",
        evidence=[{"evidence_type": "photo", "file_name": "p.jpg"}],
        location={"latitude": 19.0176, "longitude": 72.8562},
    )
    state = run_structuring(req)
    report = state["report"]

    # When inside jurisdiction and clean, routes to ready_for_police_review
    assert "missing_person_details" not in report
    assert "urgency_assessment" not in report
    if report["jurisdiction"]["status"] == "inside":
        assert report["review"]["route"] == "ready_for_police_review"
