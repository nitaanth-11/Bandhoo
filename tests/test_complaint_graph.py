"""
Tests for the LangGraph complaint-structuring workflow (complaint_engine).
Synthetic statements only. No network, no Gemini, no external geocoding.
"""

import re

import pytest
from pydantic import ValidationError

from complaint_engine import build_graph, run_structuring
from complaint_engine.extraction import ExtractorUnavailable, extract_deterministic
from complaint_engine.graph import ImmutableStatementError, NODES
from complaint_engine.models import ComplaintStructureRequest, FactItem, SourceSpan, Statement, VerificationEvent

FULL = ("On 14/10/2026 at 9 pm two men snatched my phone near Andheri Station. My friend saw it. "
        "No one was hurt. The phone cost Rs 15,000.")
DISHONESTY_WORDS = re.compile(r"\b(?:lie|lies|lying|liar|false|falsely|dishonest\w*|fabricat\w*|untrue|fake)\b", re.I)


def run(statement=FULL, clarifications=(), evidence=(), location=None, events=None, **cfg):
    req = ComplaintStructureRequest(statement=statement, clarifications=list(clarifications),
                                    evidence=list(evidence), location=location)
    return run_structuring(req, trusted_verification_events=events, configurable=cfg)


def statements_by_id(state):
    return {s["statement_id"]: s for s in state["report"]["complainant_statements"]}


# ── Graph state transitions ──

def test_nodes_run_in_order_and_report_is_built():
    state = run()
    completed = [l.node for l in state["log"] if l.event == "completed"]
    assert completed == ["intake", "extract_facts", "attribute_sources", "detect_missing", "detect_contradictions",
                         "associate_evidence", "assess_jurisdiction", "validate_and_route", "human_review", "build_report"]
    assert state["report"]["header"]["document"].startswith("Structured complaint record")


def test_invalid_input_skips_processing_and_routes_to_human_review():
    state = run(statement="   ")
    completed = [l.node for l in state["log"] if l.event == "completed"]
    assert "extract_facts" not in completed and "assess_jurisdiction" not in completed
    assert state["review"].route == "human_review_required"
    assert any(e.error_type == "EmptyStatement" for e in state["errors"])


def test_clean_case_routes_to_police_review_without_claiming_verification():
    state = run(statement="On 14/10/2026 at 9 pm a man took my bag at Dadar Market. I have a photo of him. My friend saw it. The bag cost Rs 2,000.",
                evidence=[{"evidence_type": "photo", "file_name": "p.jpg"}],
                location={"latitude": 19.0176, "longitude": 72.8562})  # a point used only as synthetic input
    report = state["report"]
    if report["jurisdiction"]["status"] == "inside":
        assert state["review"].route == "ready_for_police_review", state["review"].reasons
    assert report["independently_verified"] == []
    assert "not been submitted" in report["header"]["notice"]


def test_node_failure_is_recorded_and_routed_to_human_review():
    def broken(state, config):
        raise RuntimeError("simulated failure")
    graph = build_graph(node_overrides={"detect_contradictions": broken})
    state = run_structuring(ComplaintStructureRequest(statement=FULL), graph=graph)
    assert any(e.node == "detect_contradictions" and e.error_type == "RuntimeError" for e in state["errors"])
    assert state["review"].route == "human_review_required"
    assert "report" in state  # the run completes and the report is still built


# ── Immutability ──

def test_original_statement_cannot_be_replaced_by_a_node():
    def tamper(state, config):
        return {"original_statement": Statement.create("S1", "original", "a different account")}
    graph = build_graph(node_overrides={"attribute_sources": tamper})
    with pytest.raises(ImmutableStatementError):
        run_structuring(ComplaintStructureRequest(statement=FULL), graph=graph)


def test_statement_model_is_frozen_and_hash_recorded():
    st = Statement.create("S1", "original", "text")
    with pytest.raises(ValidationError):
        st.text = "changed"
    state = run()
    assert state["original_statement"].text == FULL
    assert state["original_sha256"] == state["original_statement"].sha256


# ── Source attribution ──

def test_every_statement_fact_quotes_the_statement_exactly():
    state = run(clarifications=["It was actually at 11 pm."])
    texts = {s.statement_id: s.text for s in [state["original_statement"], *state["clarifications"]]}
    assert state["facts"]
    for f in state["facts"]:
        assert f.spans, f
        for s in f.spans:
            assert texts[s.statement_id][s.start:s.end] == s.quote


def test_fact_with_mismatched_span_is_rejected():
    def bad_extract(state, config):
        st = state["original_statement"]
        good = extract_deterministic(st)
        forged = FactItem(item_id="X-1", kind="person", value="a woman with a gun",
                          spans=[SourceSpan(statement_id="S1", start=0, end=18, quote="a woman with a gun")],
                          extraction_method="test")
        return {"facts": good + [forged]}
    graph = build_graph(node_overrides={"extract_facts": bad_extract})
    state = run_structuring(ComplaintStructureRequest(statement=FULL), graph=graph)
    assert all(f.item_id != "X-1" for f in state["facts"])
    assert any("does not match" in r.reason for r in state["rejected_items"])


# ── Optional extractor: unsupported facts, AI inferences, retries, invalid output ──

def test_unsupported_llm_fact_rejected_and_grounded_inference_labelled():
    def extractor(statements):
        return [
            {"kind": "person", "value": "two men", "quote": "two men"},
            {"kind": "weapon", "value": "a knife", "quote": "he held a knife"},          # not in the statement
            {"inference": True, "value": "The phone was probably taken for resale", "basis_quotes": ["snatched my phone"]},
            {"inference": True, "value": "The men were known to the complainant", "basis_quotes": ["they were my cousins"]},
        ]
    state = run(llm_extractor=extractor)
    values = [f.value for f in state["facts"]]
    assert "two men" in values
    assert "he held a knife" not in values and "a knife" not in values
    ai = [f for f in state["facts"] if f.provenance == "ai_inference"]
    assert len(ai) == 1 and ai[0].display_category == "AI-generated inference"
    reasons = [r.reason for r in state["rejected_items"]]
    assert any("not found verbatim" in r for r in reasons)
    assert any("inference without verbatim basis" in r for r in reasons)
    assert state["report"]["ai_inferences"][0]["value"].startswith("The phone was probably")
    assert state["review"].route == "human_review_required"


def test_transient_extractor_failures_are_retried():
    calls = {"n": 0}

    def flaky(statements):
        calls["n"] += 1
        if calls["n"] < 3:
            raise ExtractorUnavailable("timeout")
        return [{"kind": "person", "quote": "two men"}]
    state = run(llm_extractor=flaky, llm_max_attempts=3)
    assert calls["n"] == 3
    assert not any(e.error_type == "ExtractorUnavailable" for e in state["errors"])


def test_extractor_exhausting_retries_keeps_deterministic_results():
    def down(statements):
        raise ExtractorUnavailable("down")
    state = run(llm_extractor=down, llm_max_attempts=2)
    assert any(e.error_type == "ExtractorUnavailable" for e in state["errors"])
    assert state["facts"]
    assert state["review"].route == "human_review_required"


def test_invalid_extractor_output_is_an_explicit_error():
    state = run(llm_extractor=lambda statements: {"not": "a list"})
    assert any(e.error_type == "InvalidExtractorOutput" for e in state["errors"])
    assert state["review"].route == "human_review_required"


# ── Missing details ──

def test_missing_core_details_and_questions():
    state = run(statement="Someone took my bag.")
    fields = {m.field: m.status for m in state["missing"]}
    assert fields["what_happened"] == "open" and fields["when"] == "open" and fields["where"] == "open"
    assert fields["loss_value"] == "open"
    assert 0 < len(state["questions"]) <= 5
    for q in state["questions"]:
        assert not re.match(r"^(?:Was|Did he|Did she|Was it)\b", q)  # no leading questions


def test_explicit_denial_and_unknown_are_not_reported_as_missing():
    state = run(statement="Yesterday at 8 pm my wallet was stolen at Kurla Station. Nobody saw it. "
                          "I don't know who took it. I have no receipt.")
    fields = {m.field: m.status for m in state["missing"]}
    assert fields["witnesses"] == "explicitly_denied"
    assert fields["who"] == "unknown_to_complainant"
    assert "when" not in fields


# ── Contradictions ──

def test_contradictions_are_neutral_and_preserve_both_statements():
    state = run(statement="On 14/10/2026 two men took Rs 5,000 from me. No one was hurt.",
                clarifications=["It was on 15/10/2026, three men took Rs 8,000 and my hand was bleeding."])
    fields = {c.field for c in state["contradictions"]}
    assert {"date", "amount", "number_of_persons", "injury_denied_and_asserted"} <= fields
    by_id = {s.statement_id: s.text for s in [state["original_statement"], *state["clarifications"]]}
    for c in state["contradictions"]:
        assert not DISHONESTY_WORDS.search(c.summary)
        assert len(c.spans) == 2
        for s in c.spans:
            assert by_id[s.statement_id][s.start:s.end] == s.quote
    assert state["original_statement"].text.startswith("On 14/10/2026")
    assert state["review"].route == "human_review_required"


def test_no_contradiction_for_a_single_consistent_account():
    state = run(statement="On 14/10/2026 at 9 pm a man took my bag at Dadar Market. The bag cost Rs 2,000.")
    assert state["contradictions"] == []


# ── Evidence and verification ──

EV = [{"evidence_type": "photo", "description": "photo of the bag", "file_name": "bag.jpg", "sha256": "ab" * 32}]


def test_uploaded_evidence_alone_is_never_verified():
    state = run(evidence=EV)
    ev = state["evidence"][0]
    assert (ev.custody_status, ev.authenticity_status, ev.verification_status) == ("supplied_not_examined", "not_assessed", "unverified")
    assert state["report"]["independently_verified"] == []


def _event(**kw):
    base = dict(event_id="VE-1", target_id="EV-1", verifier_id="officer-test", verifier_role="police_officer",
                authorization_reference="AUTH-TEST", method="inspected original", result="consistent",
                recorded_at="2026-10-21T00:00:00Z")
    base.update(kw)
    return VerificationEvent(**base)


@pytest.mark.parametrize("bad", [dict(verifier_role="complainant"), dict(authorization_reference=" "),
                                 dict(method=""), dict(target_id="EV-99")])
def test_unauthorised_or_incomplete_verification_events_are_rejected(bad):
    state = run(evidence=EV, events=[_event(**bad)])
    assert state["evidence"][0].verification_status == "unverified"
    assert any(e.error_type == "RejectedVerificationEvent" for e in state["errors"])


def test_authorised_verification_event_marks_only_its_target():
    state = run(evidence=EV + [{"evidence_type": "receipt"}], events=[_event()])
    ev1, ev2 = state["evidence"]
    assert ev1.verification_status == "independently_verified" and ev1.custody_status == "examined_by_police"
    assert ev2.verification_status == "unverified"
    assert state["review"].validation_passed


def test_api_request_cannot_carry_verification_events():
    with pytest.raises(ValidationError):
        ComplaintStructureRequest(statement=FULL, trusted_verification_events=[{"target_id": "EV-1"}])
    with pytest.raises(ValidationError):
        ComplaintStructureRequest(statement=FULL, evidence=[{"evidence_type": "photo", "verification_status": "independently_verified"}])


def test_validation_catches_a_status_set_without_an_event():
    def forge(state, config):
        facts = [f.model_copy(update={"verification_status": "independently_verified"}) for f in state["facts"][:1]]
        return {"facts": facts + state["facts"][1:]}
    graph = build_graph(node_overrides={"assess_jurisdiction": forge})
    state = run_structuring(ComplaintStructureRequest(statement=FULL), graph=graph)
    assert state["review"].validation_passed is False
    assert state["review"].route == "human_review_required"


def test_all_expected_nodes_present():
    assert set(NODES) >= {"intake", "extract_facts", "attribute_sources", "detect_missing", "detect_contradictions",
                          "associate_evidence", "assess_jurisdiction", "validate_and_route", "build_report"}


def test_police_review_route_with_synthetic_boundaries(tmp_path):
    import json
    from complaint_engine.jurisdiction import load_boundaries
    ring = [[72.80, 19.00], [72.84, 19.00], [72.84, 19.04], [72.80, 19.04], [72.80, 19.00]]
    p = tmp_path / "b.geojson"
    p.write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": "Synthetic"}, "geometry": {"type": "Polygon", "coordinates": [ring]}}]}))
    load_boundaries.cache_clear()
    common = dict(statement="On 14/10/2026 at 9 pm a man took my bag at Dadar Market. I have a photo of him. "
                            "My friend saw it. The bag cost Rs 2,000.",
                  evidence=[{"evidence_type": "photo"}], boundary_path=str(p))
    inside = run(location={"latitude": 19.02, "longitude": 72.82}, **common)
    assert inside["jurisdiction"].station == "Synthetic"
    assert inside["review"].route == "ready_for_police_review", inside["review"].reasons
    completed = [l.node for l in inside["log"] if l.event == "completed"]
    assert "police_review" in completed and "human_review" not in completed
    outside = run(location={"latitude": 18.90, "longitude": 72.70}, **common)
    assert outside["jurisdiction"].station is None
    assert outside["review"].route == "human_review_required"
    assert "Police jurisdiction requires confirmation." in outside["review"].reasons
