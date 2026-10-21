"""
Comprehensive Automated Test Suite for BNS Legal Engine.
Tests all 13 critical requirements specified in Phase 7.
All tests use deterministic mocks and local fixtures, requiring NO live API credentials.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from legal_engine.corpus import BNSCorpus
from legal_engine.retrieval import BM25LegalRetriever, tokenize_legal_text
from legal_engine.llm_client import GeminiLegalClient, LLMUnavailableError, LLMInferenceError
from legal_engine.service import LegalAnalysisService
from legal_engine.schemas import (
    NarrativeInput,
    OffenceClassificationResponse,
    SectionPredictionItem,
    FactExtractionBlock
)


@pytest.fixture
def sample_corpus(tmp_path):
    """Fixture creating an isolated, controlled corpus for testing."""
    sample_data = [
        {
            "section": 303,
            "title": "Theft",
            "chapter": "Chapter XVII",
            "text": "Whoever, intending to take dishonestly any moveable property out of the possession of any person without that person’s consent, moves that property in order to such taking, is said to commit theft.",
            "punishment": "Imprisonment of either description up to three years, or with fine, or with both.",
            "keywords": ["dishonestly", "moveable", "property", "theft", "steals"],
            "verified": True,
            "source": "Bharatiya Nyaya Sanhita, 2023"
        },
        {
            "section": 304,
            "title": "Snatching",
            "chapter": "Chapter XVII",
            "text": "Theft is snatching if, in order to commit theft, the offender suddenly or quickly or forcibly seizes or secures or grabs or takes away from any person any moveable property.",
            "punishment": "Imprisonment for a term which may extend to three years, and shall also be liable to fine.",
            "keywords": ["snatching", "forcibly", "grabs", "seizes", "theft"],
            "verified": True,
            "source": "Bharatiya Nyaya Sanhita, 2023"
        },
        {
            "section": 115,
            "title": "Voluntarily causing hurt",
            "chapter": "Chapter VI",
            "text": "Whoever does any act with the intention of thereby causing hurt to any person, or with the knowledge that he is likely thereby to cause hurt to any person, and does thereby cause hurt to any person, is said voluntarily to cause hurt.",
            "punishment": "Imprisonment of either description for a term which may extend to one year, or with fine which may extend to ten thousand rupees, or with both.",
            "keywords": ["hurt", "bodily", "pain", "assault", "voluntarily"],
            "verified": True,
            "source": "Bharatiya Nyaya Sanhita, 2023"
        },
        {
            "section": 999,
            "title": "Incomplete Test Section",
            "chapter": "Chapter X",
            "text": "",  # Empty text to test exclusion
            "punishment": "",
            "keywords": ["empty"],
            "verified": False,
            "source": "Unverified Test"
        }
    ]
    json_file = tmp_path / "test_bns_corpus.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)
    return BNSCorpus(str(json_file))


@pytest.fixture
def legal_service(sample_corpus):
    retriever = BM25LegalRetriever(sample_corpus)
    mock_llm = MagicMock(spec=GeminiLegalClient)
    mock_llm.is_available = False  # Default to fallback mode
    syn_map = {
        "stole": "theft",
        "chori": "theft",
        "maarpeet": "assault hurt"
    }
    return LegalAnalysisService(
        corpus=sample_corpus,
        retriever=retriever,
        llm_client=mock_llm,
        synonym_map=syn_map
    )


# ── TEST 1: Legal record loading and validation ──
def test_legal_record_loading(sample_corpus):
    assert sample_corpus.has_section(303)
    assert sample_corpus.has_section(304)
    sec = sample_corpus.get_section(303)
    assert sec["title"] == "Theft"
    assert "dishonestly" in sec["text"]
    assert sec["verified"] is True


# ── TEST 2: Retrieval ranking and exclusion of incomplete records ──
def test_retrieval_and_exclusion(sample_corpus):
    # Section 999 with empty text must be excluded from corpus
    assert not sample_corpus.has_section(999)
    assert 999 in sample_corpus.excluded_sections

    retriever = BM25LegalRetriever(sample_corpus)
    results = retriever.retrieve("Someone snatched my phone forcibly", top_k=2)
    assert len(results) > 0
    top_sec, score = results[0]
    assert top_sec == 304  # Snatching
    assert score > 0.0


# ── TEST 3: Negation handling ──
def test_negation_handling(legal_service):
    query = "Nobody was hurt. There was no theft. It was just a minor disagreement."
    negations = legal_service.detect_negations(query)
    assert len(negations) >= 2
    assert any("no theft" in n.lower() for n in negations)
    assert any("nobody was hurt" in n.lower() or "hurt" in n.lower() for n in negations)

    res = legal_service.analyze_complaint(NarrativeInput(narrative=query))
    assert res.facts_analysis.negated_events


# ── TEST 4: Attempt versus completed offences ──
def test_attempt_handling(sample_corpus):
    mock_llm = MagicMock(spec=GeminiLegalClient)
    mock_llm.is_available = True
    mock_llm.model_name = "gemini-2.5-flash"
    mock_llm.evaluate_complaint.return_value = {
        "stated_facts": ["Accused tried to grab phone", "Complainant resisted", "Phone was not taken"],
        "negated_events": ["No property was stolen"],
        "inferred_facts": ["Attempt to commit theft/snatching"],
        "missing_facts_to_clarify": ["Was any weapon shown during the attempt?"],
        "recommended_action": "Record attempt to commit theft/snatching under Section 304 read with attempt provisions.",
        "candidate_evaluations": [
            {
                "section": 304,
                "applicability_score": 0.65,
                "reasoning": "Attempted snatching. Physical force used to seize property, but completed theft was frustrated.",
                "statutory_elements_supported": ["forcible grab"],
                "unestablished_elements": ["completed taking of moveable property"]
            }
        ]
    }
    retriever = BM25LegalRetriever(sample_corpus)
    service = LegalAnalysisService(corpus=sample_corpus, retriever=retriever, llm_client=mock_llm)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone tried to snatch my phone but failed and fled."))
    
    assert res.predictions
    assert res.predictions[0].section == 304
    assert "Attempted snatching" in res.predictions[0].reasoning
    assert "No property was stolen" in res.facts_analysis.negated_events


# ── TEST 5: Compound complaints ──
def test_compound_complaints(sample_corpus):
    mock_llm = MagicMock(spec=GeminiLegalClient)
    mock_llm.is_available = True
    mock_llm.model_name = "gemini-2.5-flash"
    mock_llm.evaluate_complaint.return_value = {
        "stated_facts": ["Accused punched victim causing bleeding", "Accused snatched wallet"],
        "negated_events": [],
        "inferred_facts": [],
        "missing_facts_to_clarify": [],
        "recommended_action": "Register FIR for compound offences of Hurt and Snatching under Section 173 BNSS.",
        "candidate_evaluations": [
            {"section": 304, "applicability_score": 0.9, "reasoning": "Snatching of wallet."},
            {"section": 115, "applicability_score": 0.85, "reasoning": "Voluntarily causing hurt."}
        ]
    }
    retriever = BM25LegalRetriever(sample_corpus)
    service = LegalAnalysisService(corpus=sample_corpus, retriever=retriever, llm_client=mock_llm)
    res = service.analyze_complaint(NarrativeInput(narrative="He punched me in the face causing hurt and snatched my wallet."))
    
    sec_nums = [p.section for p in res.predictions]
    assert 304 in sec_nums
    assert 115 in sec_nums


# ── TEST 6: Hindi and Hinglish narratives ──
def test_hindi_hinglish_translation(legal_service):
    text = "Chor ne mera bag chori kiya aur maarpeet ki"
    std, trans = legal_service.translate_synonyms(text)
    assert "theft" in std.lower()
    assert "assault hurt" in std.lower()
    assert len(trans) >= 2


# ── TEST 7: Empty or irrelevant narratives ──
def test_empty_or_trivial_narratives(legal_service):
    res = legal_service.analyze_complaint(NarrativeInput(narrative="hi"))
    assert len(res.predictions) == 0
    assert "too brief" in res.recommended_action.lower()


# ── TEST 8: Missing facts and uncertain conclusions ──
def test_missing_facts_detection(legal_service):
    res = legal_service.analyze_complaint(NarrativeInput(narrative="Someone took my property yesterday."))
    assert res.facts_analysis.missing_facts_to_clarify
    assert len(res.facts_analysis.missing_facts_to_clarify) > 0


# ── TEST 9 & 10: Rejection of invalid section numbers and fabricated citations ──
def test_invalid_section_rejection(sample_corpus):
    mock_llm = MagicMock(spec=GeminiLegalClient)
    mock_llm.is_available = True
    mock_llm.model_name = "gemini-2.5-flash"
    # LLM hallucinates non-existent section 4200 and fabricated IPC 420
    mock_llm.evaluate_complaint.return_value = {
        "stated_facts": ["Theft alleged"],
        "negated_events": [],
        "inferred_facts": [],
        "missing_facts_to_clarify": [],
        "recommended_action": "Action",
        "candidate_evaluations": [
            {"section": 4200, "applicability_score": 0.99, "reasoning": "Hallucinated Section"},
            {"section": 420, "applicability_score": 0.95, "reasoning": "IPC section (not in BNS)"},
            {"section": 303, "applicability_score": 0.8, "reasoning": "Valid theft section"}
        ]
    }
    retriever = BM25LegalRetriever(sample_corpus)
    service = LegalAnalysisService(corpus=sample_corpus, retriever=retriever, llm_client=mock_llm)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone dishonestly took my moveable property without consent"))

    pred_sections = [p.section for p in res.predictions]
    assert 4200 not in pred_sections
    assert 420 not in pred_sections
    assert 303 in pred_sections


# ── TEST 10: Fabricated source identifiers and citations ──
def test_fabricated_source_citations(sample_corpus):
    mock_llm = MagicMock(spec=GeminiLegalClient)
    mock_llm.is_available = True
    mock_llm.model_name = "gemini-2.5-flash"
    mock_llm.evaluate_complaint.return_value = {
        "stated_facts": ["Theft alleged"],
        "negated_events": [],
        "inferred_facts": [],
        "missing_facts_to_clarify": [],
        "recommended_action": "Action",
        "candidate_evaluations": [
            {"section": 303, "applicability_score": 0.8, "reasoning": "Valid theft section"}
        ]
    }
    retriever = BM25LegalRetriever(sample_corpus)
    service = LegalAnalysisService(
        corpus=sample_corpus,
        retriever=retriever,
        llm_client=mock_llm,
        synonym_map={"stole": "theft"}
    )
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my phone"))

    # The cited source must match the verified corpus source, not an invented text
    sec303_pred = next(p for p in res.predictions if p.section == 303)
    assert sec303_pred.source_citation == "Bharatiya Nyaya Sanhita, 2023"



# ── TEST 11: Invalid LLM Output (Malformed JSON or Schema Error) ──
def test_malformed_llm_output_handling(sample_corpus):
    mock_llm = MagicMock(spec=GeminiLegalClient)
    mock_llm.is_available = True
    mock_llm.evaluate_complaint.side_effect = LLMInferenceError("Malformed LLM JSON output: Unterminated string")
    
    retriever = BM25LegalRetriever(sample_corpus)
    service = LegalAnalysisService(corpus=sample_corpus, retriever=retriever, llm_client=mock_llm)
    
    # Must NOT crash or raise exception; must gracefully engage deterministic fallback
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my gold ring from my drawer"))
    assert res is not None
    assert "Fallback" in res.model
    assert len(res.predictions) > 0


# ── TEST 12: Provider timeout and unavailable API ──
def test_llm_unavailable_fallback(sample_corpus):
    mock_llm = MagicMock(spec=GeminiLegalClient)
    mock_llm.is_available = False
    
    retriever = BM25LegalRetriever(sample_corpus)
    service = LegalAnalysisService(corpus=sample_corpus, retriever=retriever, llm_client=mock_llm)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my purse in the market"))
    
    assert res is not None
    assert "Fallback" in res.model
    assert "LLM Inactive" in res.model
    assert res.predictions[0].section in [303, 304]


# ── TEST 13: Backward compatibility with existing endpoint contract ──
def test_backward_compatibility_contract(legal_service):
    res = legal_service.analyze_complaint(NarrativeInput(narrative="A thief stole my mobile phone while I was walking"))
    res_dict = res.model_dump()
    
    # Required top-level legacy keys
    for key in ["predictions", "recommended_action", "model", "standardized_narrative", "translations"]:
        assert key in res_dict, f"Missing required top-level key: {key}"
        
    # Required keys on each prediction object for React frontend rendering
    assert len(res_dict["predictions"]) > 0
    first_pred = res_dict["predictions"][0]
    for pkey in ["section", "title", "chapter", "score", "rag_score", "lr_prob", "reasoning", "punishment"]:
        assert pkey in first_pred, f"Missing required prediction key: {pkey}"
    
    # Enhanced structured fields present
    assert "facts_analysis" in res_dict
    assert "statutory_disclaimer" in res_dict
