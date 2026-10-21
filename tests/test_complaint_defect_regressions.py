"""
Regression tests for the workflow defects recorded in reports/trust_safety_langgraph_validation.md
(D-2 to D-7, D-9, D-10; D-1 and D-8 are frontend and covered in src/trustSafety.test.js).
Synthetic statements only. No network, no Gemini, no external tracing.
"""

import asyncio
import json
import re
import socket

import pytest

from complaint_engine import build_graph, run_structuring
from complaint_engine import graph as graph_module
from complaint_engine.graph import (
    NODES, REVIEW_UNAVAILABLE, ExternalTracingRefused, ImmutableStatementError, structure_for_api,
)
from complaint_engine.jurisdiction import load_boundaries
from complaint_engine.models import ComplaintStructureRequest, Statement

CLEAN = ("On 14/10/2026 at 9 pm a man took my bag at Dadar Market. I have a photo of him. "
         "My friend saw it. The bag cost Rs 2,000.")
TRACING_VARS = ["LANGSMITH_TRACING", "LANGSMITH_TRACING_V2", "LANGCHAIN_TRACING", "LANGCHAIN_TRACING_V2"]


def boom(state, config):
    raise RuntimeError("simulated failure")


@pytest.fixture
def clean_case(tmp_path):
    """A case that routes to police review when nothing fails (synthetic boundary containing the pin)."""
    ring = [[72.80, 19.00], [72.84, 19.00], [72.84, 19.04], [72.80, 19.04], [72.80, 19.00]]
    p = tmp_path / "b.geojson"
    p.write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": "Synthetic"}, "geometry": {"type": "Polygon", "coordinates": [ring]}}]}))
    load_boundaries.cache_clear()
    request = ComplaintStructureRequest(statement=CLEAN, evidence=[{"evidence_type": "photo"}],
                                        location={"latitude": 19.02, "longitude": 72.82})
    yield request, {"boundary_path": str(p)}
    load_boundaries.cache_clear()


@pytest.fixture
def no_network(monkeypatch):
    attempts = []

    def blocked(*args, **kwargs):
        attempts.append(args)
        raise OSError("network access blocked in tests")
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
    return attempts


@pytest.fixture
def tracing_env(monkeypatch):
    """Clears every tracing switch, and LangSmith's cached view of the environment, before and after."""
    from langsmith import utils as ls_utils
    for var in TRACING_VARS + ["LANGCHAIN_HANDLER", "BANDHOO_ALLOW_EXTERNAL_TRACING"]:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("LANGSMITH_API_KEY", "synthetic-test-value-not-a-key")
    monkeypatch.setenv("LANGSMITH_ENDPOINT", "http://127.0.0.1:9")
    ls_utils.get_env_var.cache_clear()
    yield monkeypatch
    ls_utils.get_env_var.cache_clear()


def _route(state):
    return state["report"]["review"]["route"]


# ── D-2: routing failures never produce "ready for police review" ──

def test_baseline_clean_case_is_ready(clean_case):
    request, cfg = clean_case
    state = run_structuring(request, configurable=cfg)
    assert _route(state) == "ready_for_police_review", state["report"]["review"]["reasons"]


def test_routing_exception_gives_explicit_unavailable_review(clean_case):
    request, cfg = clean_case
    state = run_structuring(request, configurable=cfg, graph=build_graph({"validate_and_route": boom}))
    review = state["report"]["review"]
    assert review is not None
    assert review["route"] == REVIEW_UNAVAILABLE == "review_status_unavailable"
    assert review["validation_passed"] is False
    assert any("Review status unavailable; human review required" in r for r in review["reasons"])
    assert "police_review" not in [l.node for l in state["log"]]


def test_routing_step_with_no_decision_gives_unavailable_review(clean_case):
    request, cfg = clean_case
    state = run_structuring(request, configurable=cfg, graph=build_graph({"validate_and_route": lambda s, c: {}}))
    assert _route(state) == REVIEW_UNAVAILABLE
    assert "police_review" not in [l.node for l in state["log"]]


@pytest.mark.parametrize("bad_review", [
    {"route": "ready_for_police_review", "reasons": [], "validation_passed": True},  # a dict, not a decision
    "ready_for_police_review",
])
def test_routing_step_with_invalid_decision_gives_unavailable_review(clean_case, bad_review):
    request, cfg = clean_case
    state = run_structuring(request, configurable=cfg,
                            graph=build_graph({"validate_and_route": lambda s, c: {"review": bad_review}}))
    assert _route(state) == REVIEW_UNAVAILABLE
    assert "police_review" not in [l.node for l in state["log"]]


def test_inconsistent_ready_decision_is_not_accepted(clean_case):
    from complaint_engine.models import ReviewDecision
    request, cfg = clean_case
    forged = ReviewDecision(route="ready_for_police_review", reasons=["Validation failed: x"], validation_passed=False)
    state = run_structuring(request, configurable=cfg,
                            graph=build_graph({"validate_and_route": lambda s, c: {"review": forged}}))
    assert _route(state) != "ready_for_police_review"
    assert "police_review" not in [l.node for l in state["log"]]


# human_review is not on the path of a clean case; its failure is tested separately below.
@pytest.mark.parametrize("node", [n for n in NODES if n not in ("build_report", "human_review")])
def test_no_single_node_failure_is_reported_ready_for_police_review(clean_case, node):
    request, cfg = clean_case
    status, body = structure_for_api(request, configurable=cfg, graph=build_graph({node: boom}))
    assert body["review"]["route"] != "ready_for_police_review"
    assert body["processing_status"] != "complete"


def test_human_review_step_failure_is_not_reported_ready():
    request = ComplaintStructureRequest(statement=CLEAN)  # no location: needs human review
    status, body = structure_for_api(request, graph=build_graph({"human_review": boom}))
    assert any(l["node"] == "human_review" and l["event"] == "failed" for l in body["processing_log"])
    assert body["review"]["route"] == "human_review_required"
    assert body["processing_status"] == "incomplete"


# ── D-3 / D-4 / D-5: failures keep the received statement and are not reported as success ──

def test_intake_exception_preserves_statement_and_is_not_success(clean_case):
    request, cfg = clean_case
    state = run_structuring(request, configurable=cfg, graph=build_graph({"intake": boom}))
    assert state["report"]["processing_status"] == "failed"
    assert state["report"]["received_input"]["statement"] == CLEAN
    status, body = structure_for_api(request, configurable=cfg, graph=build_graph({"intake": boom}))
    assert status == 500
    assert body["processing_status"] == "failed"
    assert body["received_input"]["statement"] == CLEAN
    assert body["review"]["route"] == REVIEW_UNAVAILABLE
    assert body["submission_status"].startswith("draft_only")
    assert any(e["node"] == "intake" for e in body["errors"])


def test_report_build_failure_returns_error_with_statement(clean_case):
    request, cfg = clean_case
    status, body = structure_for_api(request, configurable=cfg, graph=build_graph({"build_report": boom}))
    assert status == 500
    assert body["received_input"]["statement"] == CLEAN
    assert body["review"]["route"] == REVIEW_UNAVAILABLE


def test_statement_replacement_returns_error_with_original_statement(clean_case):
    request, cfg = clean_case

    def tamper(state, config):
        return {"original_statement": Statement.create("S1", "original", "a different account")}
    graph = build_graph({"detect_missing": tamper})
    with pytest.raises(ImmutableStatementError):
        run_structuring(request, configurable=cfg, graph=graph)
    status, body = structure_for_api(request, configurable=cfg, graph=graph)
    assert status == 500
    assert body["received_input"]["statement"] == CLEAN
    assert "a different account" not in json.dumps(body)


def test_mid_workflow_failure_is_marked_incomplete(clean_case):
    request, cfg = clean_case
    status, body = structure_for_api(request, configurable=cfg, graph=build_graph({"detect_contradictions": boom}))
    assert status == 200
    assert body["processing_status"] == "incomplete"
    assert body["review"]["route"] == "human_review_required"


def test_successful_run_is_marked_complete(clean_case):
    request, cfg = clean_case
    status, body = structure_for_api(request, configurable=cfg)
    assert status == 200 and body["processing_status"] == "complete"


def test_api_endpoint_returns_error_response_on_intake_failure(monkeypatch):
    monkeypatch.setenv("BANDHOO_SKIP_DOTENV", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    import main
    monkeypatch.setattr(graph_module, "_DEFAULT_GRAPH", build_graph({"intake": boom}))
    out = asyncio.run(main.structure_complaint(ComplaintStructureRequest(statement=CLEAN)))
    assert out.status_code == 500
    body = json.loads(out.body)
    assert body["received_input"]["statement"] == CLEAN
    assert body["review"]["route"] == REVIEW_UNAVAILABLE


# ── D-6: "I do not know ..." is attributed only to the matching category ──

def _missing(statement):
    return {m.field: m.status for m in run_structuring(ComplaintStructureRequest(statement=statement))["missing"]}


def test_unknown_date_does_not_imply_unknown_identity():
    m = _missing("Someone took my bag at Dadar Market. I do not know the date.")
    assert m["when"] == "unknown_to_complainant"
    assert m["who"] == "open"


def test_unknown_identity_does_not_imply_unknown_date():
    m = _missing("Someone took my bag at Dadar Market. I don't know who took it.")
    assert m["who"] == "unknown_to_complainant"
    assert m["when"] == "open"


def test_unknown_place_is_recorded_for_place_only():
    m = _missing("Yesterday someone took my bag on the bus. I don't know the exact place.")
    assert m["where"] == "unknown_to_complainant"
    assert m["who"] == "open"


def test_unknown_value_is_recorded_for_loss_only():
    m = _missing("On 14/10/2026 a man took my bag at Dadar Market. I do not know the value of the bag.")
    assert m["loss_value"] == "unknown_to_complainant"
    assert "who" not in m and "when" not in m


def test_unrelated_dont_know_marks_nothing_unknown():
    m = _missing("Someone took my bag at Dadar Market. I don't know what happened after that.")
    assert "unknown_to_complainant" not in m.values()


# ── D-7: conflicting dates without a year ──

def _contradictions(statement, *clarifications):
    state = run_structuring(ComplaintStructureRequest(statement=statement, clarifications=list(clarifications)))
    return state, [c for c in state["contradictions"] if c.field == "date"]


def test_yearless_dates_that_differ_are_flagged_with_both_quotes():
    state, dates = _contradictions("On 14 October two men took my bag.", "It was on 15 October.")
    assert len(dates) == 1
    by_id = {s.statement_id: s.text for s in [state["original_statement"], *state["clarifications"]]}
    quotes = [s.quote for s in dates[0].spans]
    assert quotes == ["14 October", "15 October"]
    for s in dates[0].spans:
        assert by_id[s.statement_id][s.start:s.end] == s.quote
    assert re.search(r"\b(?:19|20)\d{2}\b", dates[0].summary) is None  # no year is inferred
    assert all("????" in f.normalized for f in state["facts"] if f.kind == "datetime" and f.normalized and not f.normalized.startswith("T"))
    assert state["review"].route == "human_review_required"


def test_month_first_and_day_first_yearless_dates_are_compared():
    _, dates = _contradictions("On October 14 a man took my phone.", "It happened on 15 October.")
    assert len(dates) == 1


def test_same_yearless_date_is_not_a_conflict():
    _, dates = _contradictions("On 14 October two men took my bag.", "Yes, it was 14 October.")
    assert dates == []


def test_full_and_yearless_date_with_same_day_is_not_resolved_or_flagged():
    _, dates = _contradictions("On 14/10/2026 two men took my bag.", "It was 14 October.")
    assert dates == []


def test_full_and_yearless_date_with_different_day_is_flagged():
    _, dates = _contradictions("On 14/10/2026 two men took my bag.", "It was 15 October.")
    assert len(dates) == 1


# ── D-9: Hinglish and Marathi ──

HINGLISH = "Kal raat 9 baje do aadmi ne Dadar station ke paas mera phone cheen liya. Koi chot nahi aayi."
MARATHI = "काल रात्री ९ वाजता दोन माणसांनी दादर स्टेशनजवळ माझा फोन हिसकावला."


def _facts(state, kind):
    return [f for f in state["facts"] if f.kind == kind]


def _assert_quotes_exact(state):
    by_id = {s.statement_id: s.text for s in [state["original_statement"], *state["clarifications"]]}
    for f in state["facts"]:
        for s in f.spans:
            assert by_id[s.statement_id][s.start:s.end] == s.quote


def test_hinglish_common_expressions_are_extracted_with_exact_quotes():
    state = run_structuring(ComplaintStructureRequest(statement=HINGLISH))
    _assert_quotes_exact(state)
    assert [f.value for f in _facts(state, "location")] == ["Dadar station"]
    assert "9 baje" in [f.value for f in _facts(state, "datetime")]
    assert [(f.value, f.normalized) for f in _facts(state, "person")] == [("do aadmi", "count:2")]


def test_marathi_common_expressions_are_extracted_with_exact_quotes():
    state = run_structuring(ComplaintStructureRequest(statement=MARATHI))
    _assert_quotes_exact(state)
    assert [f.value for f in _facts(state, "location")] == ["दादर स्टेशन"]
    assert "९ वाजता" in [f.value for f in _facts(state, "datetime")]
    assert [(f.value, f.normalized) for f in _facts(state, "person")] == [("दोन माणसांनी", "count:2")]


@pytest.mark.parametrize("statement", [HINGLISH, MARATHI])
def test_limited_language_support_routes_to_human_review_without_claiming_missing(statement):
    state = run_structuring(ComplaintStructureRequest(statement=statement))
    report = state["report"]
    assert report["language_coverage"]["coverage"] == "limited"
    assert state["review"].route == "human_review_required"
    assert any("language" in r.lower() for r in state["review"].reasons)
    assert report["complainant_statements"][0]["text"] == statement
    statuses = {m.field: m.status for m in state["missing"]}
    assert "open" not in statuses.values(), statuses
    assert report["questions_for_complainant"] == []


def test_hinglish_without_a_place_does_not_invent_one():
    state = run_structuring(ComplaintStructureRequest(statement="Kal shaam ko kisi ne mera purse le liya aur bhaag gaya."))
    assert _facts(state, "location") == []
    assert {m.field: m.status for m in state["missing"]}["where"] == "not_determined"


def test_marathi_yearless_dates_that_differ_are_flagged():
    _, dates = _contradictions("१४ ऑक्टोबर रोजी माझा फोन चोरीला गेला.", "तो दिवस १५ ऑक्टोबर होता.")
    assert len(dates) == 1
    assert [s.quote for s in dates[0].spans] == ["१४ ऑक्टोबर", "१५ ऑक्टोबर"]


def test_english_statement_keeps_full_coverage():
    state = run_structuring(ComplaintStructureRequest(statement=CLEAN))
    assert state["report"]["language_coverage"]["coverage"] == "full"
    assert not any("language" in r.lower() for r in state["review"].reasons)


# ── D-10: external tracing ──

@pytest.mark.parametrize("var", TRACING_VARS)
@pytest.mark.parametrize("value", ["true", "True"])
def test_each_tracing_setting_is_refused_without_network(tracing_env, no_network, var, value):
    tracing_env.setenv(var, value)
    with pytest.raises(ExternalTracingRefused):
        build_graph()
    with pytest.raises(ExternalTracingRefused):
        run_structuring(ComplaintStructureRequest(statement=CLEAN))
    status, body = structure_for_api(ComplaintStructureRequest(statement=CLEAN))
    assert status == 503
    assert body["received_input"]["statement"] == CLEAN
    assert body["review"]["route"] == REVIEW_UNAVAILABLE
    assert var in body["errors"][0]["message"]
    assert no_network == []


@pytest.mark.parametrize("value", ["", "false", "0"])
def test_disabled_tracing_values_are_not_refused(tracing_env, no_network, value):
    for var in TRACING_VARS:
        tracing_env.setenv(var, value)
    state = run_structuring(ComplaintStructureRequest(statement=CLEAN))
    assert state["report"]["processing_status"] == "complete"
    assert no_network == []


def test_tracing_check_runs_on_every_request_not_only_at_build(tracing_env, no_network):
    run_structuring(ComplaintStructureRequest(statement=CLEAN))  # builds and caches the default graph
    tracing_env.setenv("LANGSMITH_TRACING_V2", "true")
    with pytest.raises(ExternalTracingRefused):
        run_structuring(ComplaintStructureRequest(statement=CLEAN))


def _record_tracer_construction(monkeypatch):
    from langchain_core.tracers import langchain as lc_tracers
    created = []

    def fake_init(self, *args, **kwargs):
        created.append(kwargs)
        raise RuntimeError("tracer construction recorded by test")
    monkeypatch.setattr(lc_tracers.LangChainTracer, "__init__", fake_init)
    return created


def test_tracing_is_disabled_inside_the_workflow_even_if_the_setting_check_is_bypassed(tracing_env, no_network):
    """Defence in depth: the run itself disables LangSmith tracing, independent of the settings check."""
    from langsmith.utils import tracing_is_enabled
    tracing_env.setenv("LANGSMITH_TRACING_V2", "true")
    assert tracing_is_enabled() is True  # precondition: LangSmith would trace this process
    tracing_env.setattr(graph_module, "external_tracing_settings", lambda: [])
    created = _record_tracer_construction(tracing_env)
    graph = build_graph()

    # Control: invoking the compiled graph directly would construct a LangSmith tracer.
    graph.invoke({"raw_input": ComplaintStructureRequest(statement=CLEAN), "trusted_verification_events": []})
    assert created, "control failed: the tracer probe did not detect tracing"
    created.clear()

    state = run_structuring(ComplaintStructureRequest(statement=CLEAN), graph=graph)
    assert state["report"]["processing_status"] == "complete"
    assert created == []
    assert no_network == []


def test_workflow_and_api_make_no_network_calls(tracing_env, no_network):
    tracing_env.setenv("BANDHOO_SKIP_DOTENV", "1")
    tracing_env.setenv("GEMINI_API_KEY", "")
    tracing_env.setenv("GOOGLE_API_KEY", "")
    import main
    request = ComplaintStructureRequest(statement=HINGLISH, clarifications=["It was on 15 October."],
                                        evidence=[{"evidence_type": "photo"}],
                                        location={"latitude": 19.02, "longitude": 72.84})
    report = asyncio.run(main.structure_complaint(request))
    assert report["processing_status"] in ("complete", "incomplete")
    assert report["header"]["extraction_mode"] == "deterministic"
    assert no_network == []
