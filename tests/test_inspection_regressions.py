"""
Regression tests for defects confirmed in the October 2026 inspection:
1. Section 303(2) proviso triggered by ordinary words ("returned home", "first time").
2. Indian currency parsing (lakh, thousands, decimals, multiple amounts, unrelated amounts).
3. Schedule I metadata for Sections 117, 306, 310, 316, 324 (BNSS First Schedule, Gazette text).
4. Section 173(3) BNSS wording and range checks.
5. Section 316 sub-section distinctions.
6. Procedural review across all supported candidates.
7. Section 309 validation (explicit Gemini 0.0, figurative words, multilingual negation).
8. Benchmark provisional-case metadata and with/without-provisional reporting.

Fallback-mode tests use the real BNS corpus; LLM-mode tests use a mocked Gemini client.
"""

import json
import os
import re
from unittest.mock import MagicMock

import pytest

from legal_engine.amounts import assess_stolen_property_value, extract_currency_amounts, format_inr
from legal_engine.corpus import BNSCorpus
from legal_engine.llm_client import GeminiLegalClient
from legal_engine.retrieval import BM25LegalRetriever
from legal_engine.schedule_registry import (
    BNSS_173_3_PROCEDURE_TEXT,
    LIFE_IMPRISONMENT_YEARS,
    check_bnss_173_3_eligibility,
    get_verified_schedule_entry,
    resolve_schedule_classification,
)
from legal_engine.schemas import NarrativeInput
from legal_engine.service import LegalAnalysisService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BENCH_CANDIDATE = os.path.join(BASE_DIR, "datasets", "bns_synthetic_benchmark_50.json")
BENCHMARK_PATH = _BENCH_CANDIDATE if os.path.exists(_BENCH_CANDIDATE) else os.path.join(BASE_DIR, "benchmark", "bns_synthetic_benchmark_50.json")
FALLBACK_REPORT_PATH = os.path.join(BASE_DIR, "benchmark", "evaluation_report_fallback.json")
PROVISIONAL_IDS = ["BNS-BM-17", "BNS-BM-20", "BNS-BM-21", "BNS-BM-22", "BNS-BM-28", "BNS-BM-30", "BNS-BM-31", "BNS-BM-45"]


@pytest.fixture(scope="module")
def corpus():
    return BNSCorpus()


@pytest.fixture(scope="module")
def fallback_service(corpus):
    return LegalAnalysisService(
        corpus=corpus,
        retriever=BM25LegalRetriever(corpus),
        llm_client=MagicMock(is_available=False)
    )


def make_llm_service(corpus, payload):
    client = MagicMock(spec=GeminiLegalClient)
    client.is_available = True
    client.model_name = "mock-gemini"
    client.evaluate_complaint.return_value = payload
    return LegalAnalysisService(corpus=corpus, retriever=BM25LegalRetriever(corpus), llm_client=client)


def sections(res):
    return [p.section for p in res.predictions]


# ── 1. Section 303(2) proviso detection ──

@pytest.mark.parametrize("narrative", [
    "When I returned home I found my phone worth Rs 2,000 had been stolen from my bag.",
    "This is the first time it happened: someone stole my bicycle worth Rs 3,000 from the station.",
    "Someone took my umbrella worth Rs 800 for the first time but returned and restored it immediately.",
    "A neighbour took my bicycle worth Rs 2000 and returned the bicycle to me the next morning. He has no prior record.",
])
def test_theft_proviso_never_inferred_from_complaint(fallback_service, corpus, narrative):
    is_cog, is_bail = fallback_service._determine_schedule_metadata(303, corpus.get_section(303), narrative)
    assert (is_cog, is_bail) == (None, None)


def test_theft_at_or_above_threshold_is_cognizable_even_if_returned(fallback_service, corpus):
    narrative = "Someone stole my laptop worth Rs 65,000 and later returned the laptop to me."
    assert fallback_service._determine_schedule_metadata(303, corpus.get_section(303), narrative) == (True, False)


@pytest.mark.parametrize("narrative,expected", [
    ("When I returned home I found my phone missing.", False),
    ("I returned from the office and the bike was gone.", False),
    ("He has not returned the phone yet.", False),
    ("He never returned it.", False),
    ("The thief returned the phone to me the next day.", True),
    ("My wallet was returned by the boy's father.", True),
    ("He repaid the full value of the watch.", True),
    ("Usne agle din phone wapas kar diya.", True),
])
def test_restoration_detection_requires_explicit_return_of_property(narrative, expected):
    assert LegalAnalysisService._restoration_stated(narrative) is expected


def test_below_threshold_action_keeps_first_conviction_unverified(fallback_service):
    action = fallback_service._theft_procedure_note(
        "Someone took my umbrella worth Rs 800 and returned the umbrella to me later."
    )
    assert "below ₹5,000" in action
    assert "convicted for the first time" in action
    assert "cannot be established from a complaint" in action
    assert "NON-COGNIZABLE and BAILABLE" in action
    assert "COGNIZABLE and NON-BAILABLE" in action  # both pathways stated


# ── 2. Indian currency parsing ──

@pytest.mark.parametrize("text,value", [
    ("Rs 1.5 lakh", 150000),
    ("₹2,50,000", 250000),
    ("Rs. 4,500/-", 4500),
    ("INR 5000", 5000),
    ("5000 rupees", 5000),
    ("Rs 50k", 50000),
    ("25 thousand rupees", 25000),
    ("Rs 2 crore", 20000000),
    ("Rs 1,234.50", 1234.5),
    ("₹1,00,000", 100000),
    ("15,000 रुपये", 15000),
    ("₹१५,०००", 15000),
    ("80,000 cash", 80000),
    ("worth 3 lakh", 300000),
])
def test_currency_amount_formats(text, value):
    amounts = extract_currency_amounts(text)
    assert len(amounts) == 1
    assert amounts[0].value == pytest.approx(value)


def test_lakh_amount_is_not_read_as_one_rupee():
    a = assess_stolen_property_value("My gold chain worth Rs 1.5 lakh was stolen from my locker.")
    assert a.status == "stated" and a.meets_threshold is True and a.value == 150000


def test_multiple_amounts_any_item_over_threshold():
    a = assess_stolen_property_value("A thief stole Rs 200 cash and my laptop worth Rs 60,000 from my room.")
    assert a.meets_threshold is True
    assert [x.value for x in a.associated_amounts] == [200, 60000]


def test_unrelated_purchase_amount_not_attributed():
    a = assess_stolen_property_value("My phone worth Rs 3,000, which I bought for Rs 25,000 years ago, was stolen.")
    assert a.meets_threshold is False
    assert [x.value for x in a.associated_amounts] == [3000]
    assert [x.value for x in a.unassociated_amounts] == [25000]


def test_amount_in_sentence_without_taking_not_attributed():
    a = assess_stolen_property_value("I paid Rs 10,000 rent this morning. Later someone stole my umbrella.")
    assert a.status == "unstated" and a.meets_threshold is None


def test_small_amounts_summing_over_threshold_are_ambiguous():
    a = assess_stolen_property_value("They stole my wallet worth Rs 3,000 with Rs 2,500 cash inside.")
    assert a.status == "ambiguous" and a.meets_threshold is None


def test_format_inr_uses_indian_grouping():
    assert format_inr(150000) == "1,50,000"
    assert format_inr(5000) == "5,000"


def test_lakh_value_reported_correctly_in_action(fallback_service):
    action = fallback_service._theft_procedure_note("My gold chain worth Rs 1.5 lakh was stolen from my locker.")
    assert "₹1,50,000" in action
    assert "₹1 " not in action


# ── 3. Schedule I metadata (BNSS First Schedule, Gazette text) ──

def test_section_117_bailability_depends_on_sub_section():
    assert resolve_schedule_classification(117, "117(2)")["is_bailable"] is True
    assert resolve_schedule_classification(117, "117(3)")["is_bailable"] is False
    assert resolve_schedule_classification(117, "117(4)")["is_bailable"] is False
    res = resolve_schedule_classification(117)
    assert res["is_cognizable"] is True
    assert res["is_bailable"] is None


def test_section_306_triable_by_any_magistrate():
    assert get_verified_schedule_entry(306)["court_triable_by"] == "Any Magistrate"


def test_section_310_has_no_minimum_term_and_is_sessions_triable():
    entry = get_verified_schedule_entry(310)
    assert entry["min_punishment_years"] == 0.0
    assert entry["max_punishment_years"] == LIFE_IMPRISONMENT_YEARS
    assert entry["court_triable_by"] == "Court of Session"


def test_section_316_sub_sections():
    rows = get_verified_schedule_entry(316)["sub_sections"]
    assert {k: v["max_punishment_years"] for k, v in rows.items()} == {
        "316(2)": 5.0, "316(3)": 7.0, "316(4)": 7.0, "316(5)": LIFE_IMPRISONMENT_YEARS
    }
    assert all(v["is_cognizable"] is True and v["is_bailable"] is False for v in rows.values())
    res = resolve_schedule_classification(316)
    assert (res["is_cognizable"], res["is_bailable"], res["max_punishment_years"]) == (True, False, None)


def test_section_324_cognizability_depends_on_sub_section():
    assert resolve_schedule_classification(324, "324(5)")["is_cognizable"] is True
    assert resolve_schedule_classification(324, "324(2)")["is_cognizable"] is False
    assert resolve_schedule_classification(324)["is_cognizable"] is None
    assert resolve_schedule_classification(324)["is_bailable"] is True


def test_fallback_117_prediction_reports_unverified_bailability(fallback_service):
    res = fallback_service.analyze_complaint(NarrativeInput(
        narrative="My neighbour fractured my arm with an iron rod during an argument, it is grievous hurt."
    ))
    pred = next(p for p in res.predictions if p.section == 117)
    assert pred.is_cognizable is True
    assert pred.is_bailable is None


# ── 4. Section 173(3) wording and range checks ──

def test_173_3_text_matches_statutory_conditions():
    text = BNSS_173_3_PROCEDURE_TEXT
    assert "three years or more but less than seven years" in text
    assert "prior permission" in text and "Deputy Superintendent of Police" in text
    assert "preliminary enquiry" in text and "fourteen days" in text
    assert "proceed with investigation when a prima facie case exists" in text


@pytest.mark.parametrize("sec,kwargs,eligible", [
    (304, {}, True),                               # 3 years
    (303, {"is_cognizable": True}, True),          # 3 years (5 on repeat conviction)
    (316, {"sub_section": "316(2)"}, True),        # 5 years
    (316, {"sub_section": "316(4)"}, False),       # 7 years
    (316, {"sub_section": "316(5)"}, False),       # life
    (117, {"sub_section": "117(2)"}, False),       # 7 years
    (305, {}, False),                              # 7 years
    (309, {}, False),                              # 10 years
    (115, {}, False),                              # non-cognizable, 1 year
    (351, {}, False),                              # non-cognizable
])
def test_173_3_eligibility_by_maximum_term(sec, kwargs, eligible):
    assert check_bnss_173_3_eligibility(sec, **kwargs)["eligible"] is eligible


def test_theft_action_does_not_misstate_173_3(fallback_service):
    action = fallback_service._theft_procedure_note("Someone stole my laptop worth Rs 65,000 from my car.")
    assert "punishable up to 3 years" not in action
    assert "three years or more but less than seven years" in action
    assert not re.search(r"permission[^.]{0,40}within 14 days", action)
    unstated = fallback_service._theft_procedure_note("Someone stole my laptop from my car.")
    assert not re.search(r"permission[^.]{0,40}within 14 days", unstated)


# ── 5. Section 316 sub-sections ──

def test_cbt_by_employee_does_not_offer_173_3(fallback_service):
    note = fallback_service._cbt_procedure_note(
        "My shop employee was entrusted with Rs 5 lakh of company cash and dishonestly took it for himself."
    )
    assert "316(4)" in note
    assert "Section 173(3) BNSS does not apply" in note
    assert "permissible" not in note.lower()


def test_cbt_without_capacity_facts_is_conditional(fallback_service):
    note = fallback_service._cbt_procedure_note("My business partner was entrusted with funds and spent them on himself.")
    assert "If only Section 316(2) applies" in note
    assert "requires verification" in note


# ── 6. Procedural review across supported candidates ──

def test_procedure_considers_theft_not_only_top_ranked_intimidation(fallback_service):
    res = fallback_service.analyze_complaint(NarrativeInput(
        narrative="He took my phone from my pocket and later threatened to sue me if I complained."
    ))
    assert res.predictions[0].section == 351
    action = res.recommended_action
    assert "Sec 303 (Theft)" in action
    assert "different procedural routes" in action
    assert "procedural route cannot be determined" in action


def test_mixed_cognizable_candidates_cite_174_4(corpus):
    payload = {
        "stated_facts": ["Laptop worth Rs 60,000 taken", "Accused abused complainant"],
        "candidate_evaluations": [
            {"section": 303, "applicability_score": 0.9, "reasoning": "Theft."},
            {"section": 352, "applicability_score": 0.8, "reasoning": "Intentional insult."},
        ],
    }
    service = make_llm_service(corpus, payload)
    res = service.analyze_complaint(NarrativeInput(
        narrative="A man stole my laptop worth Rs 60,000 and insulted me loudly to provoke a fight."
    ))
    assert {303, 352} <= set(sections(res))
    action = res.recommended_action
    assert "Section 174(4)" in action
    assert "Sec 352" in action and "Sec 303" in action


# ── 7. Section 309 robbery validation ──

def test_explicit_gemini_zero_for_robbery_is_not_overridden(corpus):
    payload = {
        "candidate_evaluations": [
            {"section": 309, "applicability_score": 0.0, "reasoning": "Threat was made after the taking."},
            {"section": 303, "applicability_score": 0.9, "reasoning": "Theft."},
        ]
    }
    service = make_llm_service(corpus, payload)
    res = service.analyze_complaint(NarrativeInput(
        narrative="He took my wallet from my desk. Next week he threatened to kill me and pointed a knife at me."
    ))
    assert 309 not in sections(res)


def test_explicit_gemini_low_score_is_not_raised_by_trigger_words(corpus):
    payload = {"candidate_evaluations": [{"section": 309, "applicability_score": 0.3, "reasoning": "Uncertain nexus."}]}
    service = make_llm_service(corpus, payload)
    res = service.analyze_complaint(NarrativeInput(
        narrative="He threatened to kill me and took my wallet."
    ))
    pred = next(p for p in res.predictions if p.section == 309)
    assert pred.lr_prob == pytest.approx(0.3)


@pytest.mark.parametrize("narrative", [
    "My feelings were hurt when the man took my wallet from my desk drawer.",
    "He took my phone from my pocket and later threatened to sue me if I complained.",
    "Someone stole my handbag from a restaurant chair in Colaba while I was washing my hands. The bag contained personal cosmetics, a notebook, and some cash.",
    "My knife set was stolen from my kitchen while I was away.",
])
def test_fallback_robbery_requires_stated_elements(fallback_service, narrative):
    assert 309 not in sections(fallback_service.analyze_complaint(NarrativeInput(narrative=narrative)))


@pytest.mark.parametrize("narrative", [
    "Two masked men entered my chemist shop at midnight. One held a large knife against my throat and threatened to kill me if I screamed, while the other looted Rs 40,000 from the cash register.",
    "Kal raat ko auto se utarte waqt driver aur uske dost ne mujhe gher liya. Ek bande ne collar pakad ke wall pe daba diya aur bola 'chupchaap purse nikaal warna jaan se maar dunga'. Darr ke maare maine purse de diya jisme 10000 cash tha.",
])
def test_fallback_preserves_threat_based_robbery(fallback_service, narrative):
    assert 309 in sections(fallback_service.analyze_complaint(NarrativeInput(narrative=narrative)))


@pytest.mark.parametrize("narrative", [
    "मेरी दुकान के गल्ले से 15,000 रुपये चोरी हो गए। मैं स्पष्ट रूप से कहता हूं कि किसी भी हथियार का उपयोग नहीं किया गया था, कोई हिंसा नहीं हुई, किसी को चोट नहीं आई और किसी को कोई धमकी नहीं दी गई।",
    "Mere bag se 3000 rupaye chori ho gaye, koi hathiyar nahi tha aur kisi ko chot nahi aayi, bina kisi maarpeet ke.",
])
def test_multilingual_negation_excludes_robbery(fallback_service, narrative):
    res = fallback_service.analyze_complaint(NarrativeInput(narrative=narrative))
    assert 309 not in sections(res)
    assert len(res.facts_analysis.negated_events) >= 2


# ── 8. Benchmark metadata and reporting ──

@pytest.fixture(scope="module")
def benchmark_cases():
    with open(BENCHMARK_PATH, encoding="utf-8") as f:
        return {c["case_id"]: c for c in json.load(f)}


def test_disputed_cases_marked_provisional_in_dataset(benchmark_cases):
    provisional = sorted(cid for cid, c in benchmark_cases.items()
                         if c["review_status"] == "provisional_pending_legal_review")
    assert provisional == PROVISIONAL_IDS
    assert all(benchmark_cases[cid].get("label_review_notes") for cid in PROVISIONAL_IDS)


def test_label_concerns_documented_without_changing_labels(benchmark_cases):
    for cid in ("BNS-BM-20", "BNS-BM-21", "BNS-BM-22"):
        case = benchmark_cases[cid]
        assert case["expected_bailable"] is True  # label intentionally unchanged
        assert "Section 62" in case["label_review_notes"]
    assert 310 in benchmark_cases["BNS-BM-17"]["relevant_candidate_sections"]


def test_dataset_builder_matches_published_benchmark(benchmark_cases):
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_dataset", os.path.join(BASE_DIR, "benchmark", "build_dataset.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert {c["case_id"]: c for c in module.BENCHMARK_CASES} == benchmark_cases


def test_fallback_report_includes_with_and_without_provisional_metrics():
    with open(FALLBACK_REPORT_PATH, encoding="utf-8") as f:
        report = json.load(f)
    overall = report["overall_metrics"]
    excl = report["overall_metrics_excluding_provisional"]
    prov = report["provisional_cases_only_metrics"]
    assert overall["case_count"] == 50 and excl["case_count"] == 42 and prov["case_count"] == 8
    assert sorted(report["metadata"]["provisional_ground_truth_cases"]) == PROVISIONAL_IDS
    for field in ("total_predictions", "true_positives", "ground_truth_relevant_sections",
                  "relevant_sections_retrieved_in_final", "schedule_evaluated_cases", "schedule_correct_cases"):
        assert overall["counts_and_denominators"][field] == (
            excl["counts_and_denominators"][field] + prov["counts_and_denominators"][field]
        )
    for part in (overall, excl):
        assert abs(part["unsupported_section_rate"] + part["final_prediction_precision_micro"] - 1.0) <= 0.0001
    scen = report["scenario_special_metrics"]
    assert scen["procedural_correctness_rate_verified_only"] == overall["procedural_correctness_rate_verified_only"]


def test_metric_definitions_disclose_recall_at_k_and_unsupported_rate():
    with open(FALLBACK_REPORT_PATH, encoding="utf-8") as f:
        defs = json.load(f)["metric_definitions_and_limitations"]
    assert "retrieve_clause_level" in defs["retrieval_recall_at_k"]["limitations"]
    assert "1 - final_prediction_precision_micro" in defs["unsupported_section_rate"]["formula"]
    assert "production_candidate_recall" in defs
    assert "TOP-RANKED" in defs["procedural_correctness_rate_verified_only"]["numerator"]
