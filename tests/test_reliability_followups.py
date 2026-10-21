"""
Regression tests for follow-up reliability fixes:
1. Section 62 attempt handling never overrides an explicit Gemini score; explicit zero is distinct from a missing score.
2. inference_status and model labels distinguish live inference, unavailable LLM, failed inference and non-invocation.
3. Disputed benchmark cases carry provisional status, structured review records and an audit trail, with labels unchanged.
4. Legal uncertainty (303(2) proviso, 173(3) range reading, Lalita Kumari, 324 bands) is preserved in outputs.

All LLM behaviour is mocked; no live Gemini calls are made.
"""

import json
import os
from unittest.mock import MagicMock

import pytest

from legal_engine.corpus import BNSCorpus
from legal_engine.llm_client import GeminiLegalClient, LLMInferenceError, LLMUnavailableError
from legal_engine.retrieval import BM25LegalRetriever
from legal_engine.schedule_registry import (
    BNSS_173_3_CAVEAT_TEXT,
    OPEN_LEGAL_QUESTIONS,
    check_bnss_173_3_eligibility,
)
from legal_engine.schemas import NarrativeInput
from legal_engine.service import LegalAnalysisService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCHMARK_PATH = os.path.join(BASE_DIR, "benchmark", "bns_synthetic_benchmark_50.json")
DISPUTED_IDS = ["BNS-BM-17", "BNS-BM-20", "BNS-BM-21", "BNS-BM-22", "BNS-BM-28", "BNS-BM-30", "BNS-BM-31", "BNS-BM-45"]

ATTEMPT_NARRATIVE = (
    "A man attempted to steal my wallet from my coat pocket on the bus but I caught his wrist before he could take it."
)


@pytest.fixture(scope="module")
def corpus():
    return BNSCorpus()


def make_service(corpus, payload=None, available=True, side_effect=None):
    client = MagicMock(spec=GeminiLegalClient)
    client.is_available = available
    client.model_name = "mock-gemini"
    if side_effect is not None:
        client.evaluate_complaint.side_effect = side_effect
    else:
        client.evaluate_complaint.return_value = payload or {}
    return LegalAnalysisService(corpus=corpus, retriever=BM25LegalRetriever(corpus), llm_client=client), client


def pred(res, section):
    return next((p for p in res.predictions if p.section == section), None)


# ── 1. Section 62 attempt handling ──

def test_explicit_zero_for_attempt_is_not_overridden(corpus):
    service, _ = make_service(corpus, {"candidate_evaluations": [
        {"section": 62, "applicability_score": 0.0, "reasoning": "Offence was completed, not attempted."},
        {"section": 303, "applicability_score": 0.9, "reasoning": "Theft."},
    ]})
    res = service.analyze_complaint(NarrativeInput(narrative=ATTEMPT_NARRATIVE))
    assert pred(res, 62) is None


def test_explicit_low_attempt_score_is_not_raised(corpus):
    service, _ = make_service(corpus, {"candidate_evaluations": [
        {"section": 62, "applicability_score": 0.3, "reasoning": "Possibly an attempt."},
    ]})
    p = pred(service.analyze_complaint(NarrativeInput(narrative=ATTEMPT_NARRATIVE)), 62)
    assert p is not None and p.lr_prob == pytest.approx(0.3)
    assert p.reasoning == "Possibly an attempt."


@pytest.mark.parametrize("item", [
    {"section": 62, "reasoning": "No score supplied."},
    {"section": 62, "applicability_score": None, "reasoning": "Null score."},
    {"section": 62, "applicability_score": "high", "reasoning": "Non-numeric score."},
])
def test_missing_attempt_score_uses_heuristic_support(corpus, item):
    service, _ = make_service(corpus, {"candidate_evaluations": [item]})
    p = pred(service.analyze_complaint(NarrativeInput(narrative=ATTEMPT_NARRATIVE)), 62)
    # Missing score: heuristic path (retrieval score, raised to 0.8 only if below 0.6), never treated as explicit 0.0
    assert p is not None
    assert p.lr_prob == pytest.approx(max(p.rag_score, 0.8) if p.rag_score < 0.6 else p.rag_score)
    assert p.reasoning.startswith("BNS Section 62 may apply")
    assert any("BNS Section 62" in e for e in p.statutory_elements_supported)


def test_valid_attempt_with_explicit_score_retained(corpus):
    service, _ = make_service(corpus, {"candidate_evaluations": [
        {"section": 62, "applicability_score": 0.9, "reasoning": "Attempted theft interrupted."},
        {"section": 303, "applicability_score": 0.6, "reasoning": "Theft attempted."},
    ]})
    p = pred(service.analyze_complaint(NarrativeInput(narrative=ATTEMPT_NARRATIVE)), 62)
    assert p is not None and p.lr_prob == pytest.approx(0.9)


def test_hindi_attempt_wording_recognised(corpus):
    service, _ = make_service(corpus, {"candidate_evaluations": [{"section": 62, "reasoning": "No score."}]})
    res = service.analyze_complaint(NarrativeInput(
        narrative="बाजार में एक चोर ने मेरी सोने की चेन खींचने का प्रयास किया, लेकिन चेन मेरे हाथ में आ गई।"
    ))
    p = pred(res, 62)
    assert p is not None and p.reasoning.startswith("BNS Section 62 may apply")


@pytest.mark.parametrize("value,expected", [
    (0, 0.0), (0.0, 0.0), ("0", 0.0), (0.45, 0.45), ("0.7", 0.7), (1.5, 1.0), (-0.2, 0.0),
    (None, None), ("high", None), (True, None), (float("nan"), None), ([0.5], None),
])
def test_parse_explicit_score(value, expected):
    assert LegalAnalysisService._parse_explicit_score(value) == expected


# ── 2. Inference status and labels ──

def test_status_live_llm(corpus):
    service, _ = make_service(corpus, {"candidate_evaluations": [{"section": 303, "applicability_score": 0.9}]})
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my phone from my bag."))
    assert res.inference_status == "live_llm"
    assert res.model == "Gemini LLM + BM25 Grounded RAG (mock-gemini)"


def test_status_unavailable_llm(corpus):
    service, client = make_service(corpus, available=False)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my phone from my bag."))
    assert res.inference_status == "fallback_llm_unavailable"
    assert res.model == "BM25 Statutory Retrieval Engine (Deterministic Fallback - LLM Inactive)"
    client.evaluate_complaint.assert_not_called()


@pytest.mark.parametrize("error", [
    LLMInferenceError("Gemini API failure: 503 UNAVAILABLE"),
    LLMInferenceError("Malformed LLM JSON output"),
    RuntimeError("unexpected"),
])
def test_status_failed_inference(corpus, error):
    service, client = make_service(corpus, side_effect=error)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my phone from my bag."))
    assert res.inference_status == "fallback_llm_failed"
    assert res.model == "BM25 Statutory Retrieval Engine (Deterministic Fallback - LLM Inference Failed)"
    assert "LLM Inactive" not in res.model
    client.evaluate_complaint.assert_called_once()


def test_status_unavailable_error_raised_during_call(corpus):
    service, _ = make_service(corpus, side_effect=LLMUnavailableError("not configured"))
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my phone from my bag."))
    assert res.inference_status == "fallback_llm_unavailable"


def test_status_not_invoked_without_candidates(corpus):
    service, client = make_service(corpus, {})
    res = service.analyze_complaint(NarrativeInput(narrative="zzqx vvbn qqwe plmk"))
    assert res.inference_status == "fallback_llm_not_invoked"
    assert "LLM Not Invoked" in res.model
    client.evaluate_complaint.assert_not_called()


def test_status_non_penal_gate_and_brief_input(corpus):
    service, client = make_service(corpus, {})
    gate = service.analyze_complaint(NarrativeInput(
        narrative="The multiplex is doing daylight robbery with popcorn prices of Rs 500."
    ))
    assert gate.inference_status == "non_penal_gate"
    brief = service.analyze_complaint(NarrativeInput(narrative="hi"))
    assert brief.inference_status == "input_too_brief"
    client.evaluate_complaint.assert_not_called()


def test_fallback_label_stays_detectable_by_substring(corpus):
    service, _ = make_service(corpus, side_effect=LLMInferenceError("429"))
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my phone from my bag."))
    assert "Fallback" in res.model and res.model.startswith("BM25 Statutory Retrieval Engine")


# ── 3. Disputed benchmark labels ──

@pytest.fixture(scope="module")
def benchmark_cases():
    with open(BENCHMARK_PATH, encoding="utf-8") as f:
        return {c["case_id"]: c for c in json.load(f)}


@pytest.mark.parametrize("cid", DISPUTED_IDS)
def test_disputed_case_review_record(benchmark_cases, cid):
    case = benchmark_cases[cid]
    assert case["review_status"] == "provisional_pending_legal_review"
    review = case["label_review"]
    assert review["resolution"] == "unresolved_pending_qualified_legal_review"
    assert "not a qualified legal review" in review["reviewer"]
    assert review["findings"] and review["sources"]
    for proposal in review["proposed_label_corrections_not_applied"]:
        assert case[proposal["field"]] == proposal["current"]  # proposals are not applied
        assert proposal["proposed"] != proposal["current"]
        assert proposal["basis"]
    history = case["review_history"]
    assert history and all(h["date"] and h["change"] and h["reason"] for h in history)


def test_only_disputed_cases_are_provisional(benchmark_cases):
    provisional = sorted(c for c, v in benchmark_cases.items() if v["review_status"] == "provisional_pending_legal_review")
    assert provisional == DISPUTED_IDS


# ── 4. Legal uncertainty preserved ──

def test_open_legal_questions_registered():
    assert set(OPEN_LEGAL_QUESTIONS) == {
        "303_proviso_at_registration", "173_3_punishment_range_reading", "173_3_and_lalita_kumari", "324_value_bands"
    }


def test_173_3_caveat_names_lalita_kumari():
    assert "Lalita Kumari" in BNSS_173_3_CAVEAT_TEXT and "(2014) 2 SCC 1" in BNSS_173_3_CAVEAT_TEXT


def test_boundary_punishment_terms_flag_interpretation():
    assert "pending qualified legal review" in check_bnss_173_3_eligibility(305)["reason"]          # exactly 7 years
    assert "pending qualified legal review" in check_bnss_173_3_eligibility(304)["reason"]          # exactly 3 years
    assert "pending qualified legal review" not in check_bnss_173_3_eligibility(309)["reason"]      # 10 years: clear


def test_theft_notes_preserve_uncertainty(corpus):
    service, _ = make_service(corpus, available=False)
    below = service._theft_procedure_note("Someone took my umbrella worth Rs 800 and returned the umbrella to me.")
    assert "unsettled" in below and "FIR-registration stage" in below
    above = service._theft_procedure_note("Someone stole my laptop worth Rs 65,000.")
    assert "maximum-term reading" in above and "Lalita Kumari" in above


def test_mischief_note_flags_value_band_overlap(corpus):
    service, _ = make_service(corpus, available=False)
    note = service._mischief_procedure_note()
    assert "324(5)" in note and "overlap" in note and "Unresolved" in note
