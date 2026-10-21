"""
Regression Test Suite for Retrieval Quality, Metaphor Filtering, Compound Complaints,
and Availability Hardening under BNS, 2023.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from legal_engine.corpus import BNSCorpus
from legal_engine.retrieval import BM25LegalRetriever
from legal_engine.llm_client import GeminiLegalClient, LLMInferenceError
from legal_engine.service import LegalAnalysisService
from legal_engine.schemas import NarrativeInput


@pytest.fixture
def test_corpus():
    return BNSCorpus()


@pytest.fixture
def fallback_service(test_corpus):
    retriever = BM25LegalRetriever(test_corpus)
    mock_llm = MagicMock(spec=GeminiLegalClient)
    mock_llm.is_available = False
    return LegalAnalysisService(corpus=test_corpus, retriever=retriever, llm_client=mock_llm)


# ── TEST 1: Metaphorical robbery language is suppressed ──
def test_metaphorical_robbery_language_suppressed(fallback_service):
    """Metaphorical consumer pricing complaint must NOT trigger Section 309 (Robbery) or 303 (Theft)."""
    complaint = (
        "This restaurant is committing daylight robbery with their prices! "
        "They charged me Rs 1,200 for a simple paneer dish and Rs 300 for one roti. The manager was rude."
    )
    res = fallback_service.analyze_complaint(NarrativeInput(narrative=complaint))
    
    # Must produce 0 penal predictions
    assert len(res.predictions) == 0
    # Must identify consumer pricing dispute in recommended action
    assert "consumer pricing dispute" in res.recommended_action.lower() or "commercial grievance" in res.recommended_action.lower()
    # Sections 303, 304, 309 must NOT be cited
    pred_sections = [p.section for p in res.predictions]
    assert 309 not in pred_sections
    assert 303 not in pred_sections


# ── TEST 2: Genuine robbery allegation is preserved (counterfactual check) ──
def test_genuine_robbery_allegation_preserved(fallback_service):
    """Genuine armed confrontation at commercial venue must NEVER be suppressed by grievance gate."""
    complaint = (
        "Two men armed with a knife cornered me at the supermarket counter, physically restrained me, "
        "and robbed fifty thousand rupees from my bag while threatening to kill me."
    )
    res = fallback_service.analyze_complaint(NarrativeInput(narrative=complaint))
    
    pred_sections = [p.section for p in res.predictions]
    assert len(pred_sections) > 0
    assert 309 in pred_sections  # Robbery must be preserved
    top_pred = res.predictions[0]
    assert top_pred.section == 309
    assert top_pred.score > 0.5


# ── TEST 3: Low-information complaints handled safely ──
def test_low_information_complaint_handled_safely(fallback_service):
    """Vague or low-information input must not produce false penal accusations."""
    complaint = "something happened yesterday"
    res = fallback_service.analyze_complaint(NarrativeInput(narrative=complaint))
    
    # Either empty or expresses uncertainty
    assert len(res.predictions) == 0 or any("clarif" in res.recommended_action.lower() for _ in [1])


# ── TEST 4: Compound complaint retrieves multiple distinct provisions ──
def test_compound_complaint_multi_offence_retrieval(fallback_service):
    """Compound narrative alleging house-trespass and theft must surface both offences."""
    complaint = (
        "A trespasser climbed over my compound wall at 2 AM, broke the padlock of my garage, "
        "and stole power tools worth forty thousand rupees."
    )
    res = fallback_service.analyze_complaint(NarrativeInput(narrative=complaint))
    pred_sections = [p.section for p in res.predictions]
    
    # Must retrieve theft (303) and/or trespass/house-breaking (329/330/331)
    assert 303 in pred_sections
    assert any(s in pred_sections for s in [329, 330, 331])


# ── TEST 5: Negation in one clause and positive evidence in another ──
def test_negation_in_one_clause_positive_in_another(fallback_service):
    """Contrastive negation: 'no violence at first, but then he cornered and threatened me'."""
    complaint = (
        "There was no physical injury at first, but then the suspect cornered me against the wall, "
        "threatened me with instant harm, and took my wallet."
    )
    res = fallback_service.analyze_complaint(NarrativeInput(narrative=complaint))
    pred_sections = [p.section for p in res.predictions]
    
    # Section 309 must be preserved because of the affirmative threat and wrongful restraint
    assert 309 in pred_sections


# ── TEST 6: Candidate selection when BM25 scores are uniformly weak ──
def test_candidate_selection_uniformly_weak_scores(test_corpus):
    """Uniformly weak or out-of-vocabulary query returns empty candidate list."""
    retriever = BM25LegalRetriever(test_corpus)
    # Query with non-legal nonsensical words
    cands = retriever.retrieve("xyzabc qwerty asdfgh foo bar baz", top_k=5)
    assert len(cands) == 0


# ── TEST 7: Preservation of statutory validation after retrieval changes ──
def test_statutory_validation_preservation(fallback_service):
    """Pure non-violent stealth theft must still strictly exclude Section 309 (Robbery)."""
    complaint = (
        "Someone took my phone from my bag while I was waiting at the bus stop. "
        "There were no weapons, no physical violence, and nobody was hurt."
    )
    res = fallback_service.analyze_complaint(NarrativeInput(narrative=complaint))
    pred_sections = [p.section for p in res.predictions]
    
    # Section 303 should be present
    assert 303 in pred_sections
    # Section 309 Robbery MUST be excluded or score 0
    assert 309 not in pred_sections or res.predictions[pred_sections.index(309)].score == 0.0
    # Facts block must be present with separated negations
    assert res.facts_analysis is not None
    assert len(res.facts_analysis.negated_events) > 0


# ── TEST 8: Gemini 503 transient error bounded retry and fallback ──
def test_gemini_503_bounded_retry_and_fallback(test_corpus):
    """Upstream 503 Service Unavailable triggers bounded retry and transparent BM25 fallback."""
    retriever = BM25LegalRetriever(test_corpus)
    mock_genai_client = MagicMock()
    
    # Simulate upstream 503 error
    mock_genai_client.models.generate_content.side_effect = Exception("503 UNAVAILABLE: The service is temporarily overloaded.")
    
    client = GeminiLegalClient(
        api_key="mock_key",
        model_name="gemini-3.8-flash",
        max_retries=1,
        backoff_seconds=0.01  # Fast for test execution
    )
    client._client = mock_genai_client
    
    service = LegalAnalysisService(corpus=test_corpus, retriever=retriever, llm_client=client)
    res = service.analyze_complaint(NarrativeInput(
        narrative="Someone snatched my gold chain forcibly from my neck while I was walking."
    ))
    
    # Must retry once (total 2 attempts)
    assert mock_genai_client.models.generate_content.call_count == 2
    # Must produce transparent fallback response
    assert "Fallback" in res.model
    pred_sections = [p.section for p in res.predictions]
    assert 304 in pred_sections
