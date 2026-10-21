"""
LangGraph workflow for complaint structuring.

    intake ─┬─▶ extract_facts ─▶ attribute_sources ─▶ detect_missing ─▶ detect_contradictions
            │       ─▶ associate_evidence ─▶ assess_jurisdiction ─▶ validate_and_route
            └─(invalid input)──────────────────────────────────────▶ validate_and_route
    validate_and_route ─┬─▶ human_review ──┐
                        └─▶ police_review ─┴─▶ build_report ─▶ END

State is held in memory for one run only. There is no checkpointer, no database and no
durable audit trail; the processing log is returned with the result and is not persisted.

A case is shown as ready for police review only when validate_and_route produced a valid, consistent
decision and no step failed. Any other outcome is "review_status_unavailable" or "human_review_required".
External tracing (LangSmith / LangChain) is refused when configured, and disabled inside every run.
"""

import operator
import os
import re
from contextlib import contextmanager
from typing import Annotated, Callable, Dict, List, Optional, Tuple, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from complaint_engine import checks
from complaint_engine.draft import render_draft
from complaint_engine.extraction import (
    ExtractorUnavailable, InvalidExtractorOutput, extract_deterministic, span_is_valid, validate_llm_items,
)
from complaint_engine.jurisdiction import assess_point
from complaint_engine.models import (
    ComplaintStructureRequest, Contradiction, EvidenceItem, FactItem, JurisdictionAssessment, LogEntry,
    MissingInfo, NodeError, RejectedItem, ReviewDecision, Statement, VerificationEvent, sha256_text, utc_now,
)

WORKFLOW_VERSION = "complaint-structuring-0.2"
DEFAULT_LLM_ATTEMPTS = 3

READY = "ready_for_police_review"
REVIEW_UNAVAILABLE = "review_status_unavailable"
REVIEW_UNAVAILABLE_REASON = ("Review status unavailable; human review required (the routing step failed or did not "
                             "produce a valid decision).")
SUBMISSION_STATUS = "draft_only (Bandhoo has no police-submission integration)"
PERSISTENCE = "none (this record is not stored by Bandhoo)"

# Every setting that switches on LangSmith / LangChain tracing (LangSmith reads *_TRACING_V2 and falls back
# to *_TRACING, in both namespaces; LANGCHAIN_HANDLER is the legacy v1 switch).
TRACING_SETTINGS = ("LANGSMITH_TRACING", "LANGSMITH_TRACING_V2", "LANGCHAIN_TRACING", "LANGCHAIN_TRACING_V2",
                    "LANGCHAIN_HANDLER")

HIGH_RISK = re.compile(
    r"\b(?:knife|gun|pistol|weapon|acid|rape|sexual|molest\w*|child|minor|kidnap\w*|abduct\w*|suicide|"
    r"kill\w*|murder\w*|threat\w* to (?:my |our )?life|unconscious|bleeding)\b", re.I)

CATEGORY = {
    "statement": "Complainant's statement",
    "evidence": "Supporting evidence provided (not examined, not verified)",
    "verified": "Independently verified information",
    "unverified": "Unverified claim",
    "missing": "Missing information",
    "inference": "AI-generated inference",
}


class ImmutableStatementError(Exception):
    pass


class ExternalTracingRefused(RuntimeError):
    pass


def keep_original(current: Optional[Statement], update: Optional[Statement]) -> Optional[Statement]:
    """Reducer: the original statement can be set once and never replaced."""
    if current is None:
        return update
    if update is None or update == current:
        return current
    raise ImmutableStatementError("The original complainant statement cannot be changed.")


class ComplaintState(TypedDict, total=False):
    raw_input: ComplaintStructureRequest
    trusted_verification_events: List[VerificationEvent]
    original_statement: Annotated[Optional[Statement], keep_original]
    original_sha256: str
    clarifications: List[Statement]
    input_valid: bool
    language: dict
    facts: List[FactItem]
    rejected_items: Annotated[List[RejectedItem], operator.add]
    missing: List[MissingInfo]
    questions: List[str]
    contradictions: List[Contradiction]
    evidence: List[EvidenceItem]
    accepted_verifications: List[VerificationEvent]
    jurisdiction: JurisdictionAssessment
    review: ReviewDecision
    report: dict
    errors: Annotated[List[NodeError], operator.add]
    log: Annotated[List[LogEntry], operator.add]


def _statements(state: ComplaintState) -> List[Statement]:
    original = state.get("original_statement")
    return ([original] if original else []) + list(state.get("clarifications") or [])


def _configurable(config: Optional[RunnableConfig]) -> dict:
    return (config or {}).get("configurable", {}) if isinstance(config, dict) else {}


# ── Nodes ──

def intake(state: ComplaintState, config: RunnableConfig) -> dict:
    req = state["raw_input"]
    text = req.statement if isinstance(req.statement, str) else ""
    if not text.strip():
        return {"input_valid": False, "errors": [NodeError(node="intake", error_type="EmptyStatement",
                                                             message="The complainant statement is empty.")]}
    original = Statement.create("S1", "original", text)
    clarifications = [Statement.create(f"S{i}", "clarification", c)
                      for i, c in enumerate([c for c in req.clarifications if isinstance(c, str) and c.strip()], 2)]
    return {"original_statement": original, "original_sha256": original.sha256, "clarifications": clarifications,
            "input_valid": True, "language": checks.language_profile([original] + clarifications)}


def extract_facts(state: ComplaintState, config: RunnableConfig) -> dict:
    statements = _statements(state)
    facts: List[FactItem] = []
    for st in statements:
        facts.extend(extract_deterministic(st))
    out: Dict = {"facts": facts}
    cfg = _configurable(config)
    extractor: Optional[Callable] = cfg.get("llm_extractor")
    if extractor is None:
        return out
    attempts = int(cfg.get("llm_max_attempts", DEFAULT_LLM_ATTEMPTS))
    log, errors = [], []
    for attempt in range(1, attempts + 1):
        try:
            raw = extractor([s.model_dump() for s in statements])
            accepted, rejected = validate_llm_items(raw, statements, cfg.get("llm_name", "llm"))
            out["facts"] = facts + accepted
            out["rejected_items"] = rejected
            log.append(LogEntry(node="extract_facts", event=f"optional extractor succeeded on attempt {attempt}"))
            break
        except ExtractorUnavailable as exc:
            log.append(LogEntry(node="extract_facts", event=f"optional extractor attempt {attempt} failed: {exc}"))
            if attempt == attempts:
                errors.append(NodeError(node="extract_facts", error_type="ExtractorUnavailable",
                                        message=f"Optional extractor failed after {attempts} attempts; deterministic results only."))
        except InvalidExtractorOutput as exc:
            errors.append(NodeError(node="extract_facts", error_type="InvalidExtractorOutput", message=str(exc)))
            break
    out["log"] = log
    out["errors"] = errors
    return out


def attribute_sources(state: ComplaintState, config: RunnableConfig) -> dict:
    """Keeps only facts whose every span matches the statement text exactly; labels display categories."""
    by_id = {s.statement_id: s for s in _statements(state)}
    kept, rejected = [], []
    for f in state.get("facts") or []:
        if f.spans and all(span_is_valid(s, by_id) for s in f.spans):
            f = f.model_copy(update={"display_category": CATEGORY["inference" if f.provenance == "ai_inference" else "unverified"]})
            kept.append(f)
        else:
            rejected.append(RejectedItem(proposed=f.value[:200], reason="source span does not match the statement text",
                                         source=f.extraction_method))
    return {"facts": kept, "rejected_items": rejected}


def detect_missing(state: ComplaintState, config: RunnableConfig) -> dict:
    req = state["raw_input"]
    missing = checks.detect_missing(state.get("facts") or [], _statements(state),
                                    evidence_supplied=bool(req.evidence), location_supplied=req.location is not None,
                                    coverage=(state.get("language") or {}).get("coverage", "full"))
    return {"missing": missing, "questions": checks.questions_for(missing)}


def detect_contradictions(state: ComplaintState, config: RunnableConfig) -> dict:
    return {"contradictions": checks.detect_contradictions(state.get("facts") or [], _statements(state))}


def associate_evidence(state: ComplaintState, config: RunnableConfig) -> dict:
    facts = state.get("facts") or []
    evidence = checks.associate_evidence(state["raw_input"].evidence, facts)
    facts, evidence, accepted, errors = checks.apply_verification_events(
        list(state.get("trusted_verification_events") or []), facts, evidence)
    for f in facts:
        if f.verification_status == "independently_verified":
            f.display_category = CATEGORY["verified"]
    return {"facts": facts, "evidence": evidence, "accepted_verifications": accepted, "errors": errors}


def assess_jurisdiction(state: ComplaintState, config: RunnableConfig) -> dict:
    loc = state["raw_input"].location
    path = _configurable(config).get("boundary_path")
    kwargs = {"path": path} if path else {}
    if loc is None:
        return {"jurisdiction": assess_point(None, None, **kwargs)}
    return {"jurisdiction": assess_point(loc.latitude, loc.longitude, **kwargs)}


def validate_and_route(state: ComplaintState, config: RunnableConfig) -> dict:
    failures, reasons = [], []
    original = state.get("original_statement")
    if not state.get("input_valid"):
        reasons.append("The statement could not be processed (empty or invalid input).")
    if original is not None and sha256_text(original.text) != state.get("original_sha256"):
        failures.append("original statement changed during processing")
    by_id = {s.statement_id: s for s in _statements(state)}
    verified_targets = {v.target_id for v in state.get("accepted_verifications") or []}
    for f in state.get("facts") or []:
        if not f.spans or not all(span_is_valid(s, by_id) for s in f.spans):
            failures.append(f"{f.item_id}: missing or invalid source span")
        if f.provenance == "ai_inference" and f.display_category != CATEGORY["inference"]:
            failures.append(f"{f.item_id}: AI inference not labelled as such")
        if f.verification_status == "independently_verified" and f.item_id not in verified_targets:
            failures.append(f"{f.item_id}: marked verified without an accepted verification event")
    for e in state.get("evidence") or []:
        if e.verification_status != "unverified" and e.evidence_id not in verified_targets:
            failures.append(f"{e.evidence_id}: evidence status changed without an accepted verification event")
        if e.authenticity_status != "not_assessed" and e.evidence_id not in verified_targets:
            failures.append(f"{e.evidence_id}: authenticity changed without an accepted verification event")

    if failures:
        reasons.append("Validation failed: " + "; ".join(failures))
    if state.get("errors"):
        reasons.append("Processing errors: " + "; ".join(f"{e.node}: {e.error_type}" for e in state["errors"]))
    if state.get("contradictions"):
        reasons.append(f"{len(state['contradictions'])} possible inconsistency(ies) need clarification.")
    j = state.get("jurisdiction")
    if j is None or j.status != "inside":
        reasons.append("Police jurisdiction requires confirmation.")
    open_core = [m.field for m in state.get("missing") or [] if m.status == "open" and m.field in checks.CORE_FIELDS]
    if open_core:
        reasons.append("Core information missing: " + ", ".join(open_core) + ".")
    if state.get("rejected_items"):
        reasons.append(f"{len(state['rejected_items'])} extracted item(s) could not be grounded in the statement and were rejected.")
    if any(HIGH_RISK.search(s.text) for s in _statements(state)):
        reasons.append("The account mentions potentially serious harm; prioritise human review.")
    if (state.get("language") or {}).get("coverage") == "limited":
        reasons.append(checks.LIMITED_COVERAGE_NOTE)

    route = "human_review_required" if reasons else READY
    return {"review": ReviewDecision(route=route, reasons=reasons, validation_passed=not failures)}


def _is_ready(state: ComplaintState) -> bool:
    """Ready only for a real, consistent decision from validate_and_route and a run with no errors."""
    review = state.get("review")
    return (isinstance(review, ReviewDecision) and review.route == READY and review.validation_passed
            and not review.reasons and not state.get("errors"))


def effective_review(state: ComplaintState) -> ReviewDecision:
    """The decision to report. Never ready unless _is_ready; a missing or invalid decision is 'unavailable'."""
    review = state.get("review")
    if _is_ready(state):
        return review
    if isinstance(review, ReviewDecision) and review.route == "human_review_required":
        return review
    return ReviewDecision(route=REVIEW_UNAVAILABLE, reasons=[REVIEW_UNAVAILABLE_REASON], validation_passed=False)


def human_review(state: ComplaintState, config: RunnableConfig) -> dict:
    review = effective_review(state)
    event = ("review status unavailable; routed to human review" if review.route == REVIEW_UNAVAILABLE
             else "routed to human review; nothing is decided automatically")
    return {"review": review, "log": [LogEntry(node="human_review", event=event)]}


def police_review(state: ComplaintState, config: RunnableConfig) -> dict:
    return {"log": [LogEntry(node="police_review", event="routed for police review; nothing has been verified")]}


def build_report(state: ComplaintState, config: RunnableConfig) -> dict:
    facts = state.get("facts") or []
    statement_facts = [f for f in facts if f.provenance == "complainant_statement"]

    position = {st.statement_id: n for n, st in enumerate(_statements(state))}

    def _with_category(item_dict: dict, f: FactItem) -> dict:
        if not item_dict.get("display_category"):
            item_dict["display_category"] = (
                CATEGORY["verified"] if f.verification_status == "independently_verified"
                else CATEGORY["inference" if f.provenance == "ai_inference" else "unverified"]
            )
        return item_dict

    def by_kind(*kinds):  # in the order the complainant said them
        items = [f for f in statement_facts if f.kind in kinds]
        items.sort(key=lambda f: (position.get(f.spans[0].statement_id, 0), f.spans[0].start) if f.spans else (0, 0))
        return [_with_category(f.model_dump(), f) for f in items]

    j = state.get("jurisdiction")
    errors = state.get("errors") or []
    if state.get("original_statement") is None and state.get("input_valid") is not False:
        processing_status = "failed"  # intake did not complete: the statement was received but not processed
    elif state.get("input_valid") is False:
        processing_status = "invalid_input"
    else:
        processing_status = "incomplete" if errors else "complete"
    checklist = []
    for e in state.get("evidence") or []:
        checklist.append(f"Examine {e.evidence_id} ({e.evidence_type}); supplied, not examined, authenticity not assessed.")
    for f in statement_facts:
        if f.kind == "witness_reference" and f.polarity == "asserted":
            checklist.append(f"Contact the witness referred to in “{f.value}” ({f.item_id}).")
    checklist.append("Confirm the police jurisdiction." if not j or j.status != "inside"
                     else f"Confirm the map-based jurisdiction estimate ({j.station}).")
    for c in state.get("contradictions") or []:
        checklist.append(f"Clarify {c.contradiction_id} with the complainant.")

    report = {
        "header": {
            "document": "Structured complaint record (draft, not an FIR)",
            "notice": ("Prepared from the complainant's account. Nothing in this record has been verified unless "
                       "marked as independently verified by an authorised police officer. It has not been submitted to the police."),
            "workflow_version": WORKFLOW_VERSION,
            "generated_at": utc_now(),
            "extraction_mode": "deterministic" if not _configurable(config).get("llm_extractor") else "deterministic + grounded optional extractor",
        },
        "processing_status": processing_status,
        "categories": CATEGORY,
        "complainant_statements": [s.model_dump() for s in _statements(state)],
        "language_coverage": state.get("language") or {"coverage": "not_assessed"},
        "chronology_note": "Events are listed in the order the complainant gave them; no order is inferred.",
        "events": by_kind("event_statement"),
        "dates_and_times": by_kind("datetime"),
        "persons": by_kind("person"),
        "locations": by_kind("location"),
        "alleged_actions": by_kind("alleged_action"),
        "items_lost_or_damaged": by_kind("property"),
        "losses": by_kind("amount"),
        "injuries": by_kind("injury"),
        "weapons_mentioned": by_kind("weapon"),
        "contact_details_mentioned": by_kind("phone"),
        "vehicles": by_kind("vehicle"),
        "witness_references": by_kind("witness_reference"),
        "evidence_references_in_statement": by_kind("evidence_reference"),
        "explicit_denials": by_kind("denial"),
        "supporting_evidence_provided": [e.model_dump() for e in state.get("evidence") or []],
        "independently_verified": [_with_category(f.model_dump(), f) for f in facts if f.verification_status == "independently_verified"]
        + [e.model_dump() for e in state.get("evidence") or [] if e.verification_status == "independently_verified"],
        "missing_information": [m.model_dump() for m in state.get("missing") or []],
        "questions_for_complainant": list(state.get("questions") or []),
        "contradictions": [c.model_dump() for c in state.get("contradictions") or []],
        "ai_inferences": [_with_category(f.model_dump(), f) for f in facts if f.provenance == "ai_inference"],
        "rejected_items": [r.model_dump() for r in state.get("rejected_items") or []],
        "jurisdiction": j.model_dump() if j else None,
        "legal_provisions": "Not included. Legal classification is a separate, machine-generated service and is not part of this record.",
        "verification_checklist_for_officer": checklist,
        "review": effective_review(state).model_dump(),
        "submission_status": SUBMISSION_STATUS,
        "persistence": PERSISTENCE,
        "errors": [e.model_dump() for e in errors],
        "processing_log": [l.model_dump() for l in state.get("log") or []],
    }
    if processing_status == "failed":
        report["received_input"] = _received_input(state["raw_input"])
    report["draft_text"] = render_draft(report)
    return {"report": report}


def _received_input(request: ComplaintStructureRequest) -> dict:
    text = request.statement if isinstance(request.statement, str) else ""
    return {"statement": text, "clarifications": list(request.clarifications), "sha256": sha256_text(text),
            "note": "Received verbatim and not processed."}


NODES = {
    "intake": intake,
    "extract_facts": extract_facts,
    "attribute_sources": attribute_sources,
    "detect_missing": detect_missing,
    "detect_contradictions": detect_contradictions,
    "associate_evidence": associate_evidence,
    "assess_jurisdiction": assess_jurisdiction,
    "validate_and_route": validate_and_route,
    "human_review": human_review,
    "police_review": police_review,
    "build_report": build_report,
}


def _guard(name: str, fn: Callable) -> Callable:
    """Converts an unexpected node exception into a recorded error so the case goes to human review."""
    def node(state: ComplaintState, config: RunnableConfig) -> dict:
        try:
            out = dict(fn(state, config) or {})
        except ImmutableStatementError:
            raise
        except Exception as exc:  # noqa: BLE001 - every failure is recorded and routed to review
            return {"errors": [NodeError(node=name, error_type=type(exc).__name__, message=str(exc)[:300])],
                    "log": [LogEntry(node=name, event="failed")]}
        out["log"] = list(out.get("log") or []) + [LogEntry(node=name, event="completed")]
        return out
    node.__name__ = name
    return node


def _after_intake(state: ComplaintState) -> str:
    return "extract_facts" if state.get("input_valid") else "validate_and_route"


def _after_validation(state: ComplaintState) -> str:
    return "police_review" if _is_ready(state) else "human_review"


def external_tracing_settings() -> List[str]:
    """Names of the tracing settings that are switched on (any value other than empty, false, 0, no or off)."""
    return [v for v in TRACING_SETTINGS if os.environ.get(v, "").strip().lower() not in ("", "false", "0", "no", "off")]


def _tracing_allowed() -> bool:
    return os.environ.get("BANDHOO_ALLOW_EXTERNAL_TRACING") == "1"


def _refuse_external_tracing() -> None:
    enabled = external_tracing_settings()
    if enabled and not _tracing_allowed():
        raise ExternalTracingRefused(f"External tracing is configured ({', '.join(enabled)}). Complaint data must not "
                                     "be sent to a tracing service without an approved policy.")


@contextmanager
def _external_tracing_disabled():
    """Turns LangSmith / LangChain tracing off for the run, whatever the environment says."""
    if _tracing_allowed():
        yield
        return
    from langchain_core.tracers.context import tracing_v2_callback_var
    from langsmith.run_helpers import tracing_context
    token = tracing_v2_callback_var.set(None)
    try:
        with tracing_context(enabled=False):
            yield
    finally:
        tracing_v2_callback_var.reset(token)


def build_graph(node_overrides: Optional[Dict[str, Callable]] = None):
    """Compiles the workflow. `node_overrides` replaces node functions (used by tests for fault injection)."""
    _refuse_external_tracing()
    nodes = {**NODES, **(node_overrides or {})}
    g = StateGraph(ComplaintState)
    for name, fn in nodes.items():
        g.add_node(name, _guard(name, fn))
    g.add_edge(START, "intake")
    g.add_conditional_edges("intake", _after_intake, {"extract_facts": "extract_facts", "validate_and_route": "validate_and_route"})
    for a, b in [("extract_facts", "attribute_sources"), ("attribute_sources", "detect_missing"),
                 ("detect_missing", "detect_contradictions"), ("detect_contradictions", "associate_evidence"),
                 ("associate_evidence", "assess_jurisdiction"), ("assess_jurisdiction", "validate_and_route")]:
        g.add_edge(a, b)
    g.add_conditional_edges("validate_and_route", _after_validation, {"human_review": "human_review", "police_review": "police_review"})
    g.add_edge("human_review", "build_report")
    g.add_edge("police_review", "build_report")
    g.add_edge("build_report", END)
    return g.compile()


_DEFAULT_GRAPH = None


def run_structuring(request: ComplaintStructureRequest, trusted_verification_events: Optional[List[VerificationEvent]] = None,
                    configurable: Optional[dict] = None, graph=None) -> dict:
    """Runs the workflow and returns the final state. Verification events must come from trusted server code."""
    global _DEFAULT_GRAPH
    _refuse_external_tracing()  # checked on every run, not only when the graph is first built
    if graph is None:
        if _DEFAULT_GRAPH is None:
            _DEFAULT_GRAPH = build_graph()
        graph = _DEFAULT_GRAPH
    initial = {"raw_input": request, "trusted_verification_events": list(trusted_verification_events or [])}
    with _external_tracing_disabled():
        return graph.invoke(initial, config={"configurable": dict(configurable or {})})


def _failure_body(request: ComplaintStructureRequest, errors: List[NodeError]) -> dict:
    return {
        "processing_status": "failed",
        "message": ("The statement was received but could not be structured. Nothing was stored, verified or "
                    "submitted. A person must review the statement below."),
        "received_input": _received_input(request),
        "review": ReviewDecision(route=REVIEW_UNAVAILABLE, reasons=[REVIEW_UNAVAILABLE_REASON],
                                 validation_passed=False).model_dump(),
        "submission_status": SUBMISSION_STATUS,
        "persistence": PERSISTENCE,
        "errors": [e.model_dump() for e in errors],
    }


def structure_for_api(request: ComplaintStructureRequest, configurable: Optional[dict] = None,
                      graph=None) -> Tuple[int, dict]:
    """(HTTP status, body) for the API. A run that could not structure the statement is an error response
    that returns the received statement verbatim, never a partial success."""
    try:
        state = run_structuring(request, configurable=configurable, graph=graph)
    except ExternalTracingRefused as exc:
        return 503, _failure_body(request, [NodeError(node="tracing_guard", error_type="ExternalTracingRefused", message=str(exc))])
    except ImmutableStatementError as exc:
        return 500, _failure_body(request, [NodeError(node="workflow", error_type="ImmutableStatementError", message=str(exc))])
    report = state.get("report")
    if not report or report.get("processing_status") == "failed":
        return 500, _failure_body(request, list(state.get("errors") or []))
    return 200, report
