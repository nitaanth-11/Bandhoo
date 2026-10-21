"""
Deterministic Mocked Test Suite for Gemini LLM Pipeline.
Covers all edge cases and failure modes specified in Task 3:
1. Successful structured model response
2. Empty model response
3. Invalid JSON
4. Missing required fields
5. Invalid section identifiers
6. Fabricated source citations
7. Provider timeout
8. Rate-limit response (HTTP 429)
9. Authentication failure (HTTP 401/403 and missing key)
10. Invalid structured output (JSON array, primitive string, non-dict elements)
11. Incorrect model configuration
12. Explicit fallback behaviour
13. Strict separation of States A, B, and C
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from legal_engine.corpus import BNSCorpus
from legal_engine.retrieval import BM25LegalRetriever
from legal_engine.llm_client import GeminiLegalClient, LLMUnavailableError, LLMInferenceError
from legal_engine.service import LegalAnalysisService
from legal_engine.schemas import (
    NarrativeInput,
    OffenceClassificationResponse,
    SectionPredictionItem,
    FactExtractionBlock
)


@pytest.fixture
def mock_corpus(tmp_path):
    """Fixture providing a verified mini-corpus with specific test sections."""
    sample_data = [
        {
            "section": 303,
            "title": "Theft",
            "chapter": "Chapter XVII",
            "text": "Whoever, intending to take dishonestly any moveable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft.",
            "punishment": "Imprisonment of either description up to three years, or with fine, or with both.",
            "keywords": ["theft", "dishonestly", "moveable", "property", "pocket"],
            "verified": True,
            "source": "Bharatiya Nyaya Sanhita, 2023"
        },
        {
            "section": 304,
            "title": "Snatching",
            "chapter": "Chapter XVII",
            "text": "Theft is snatching if, in order to commit theft, the offender suddenly or quickly or forcibly seizes or secures or grabs or takes away from any person any moveable property.",
            "punishment": "Imprisonment for a term which may extend to three years, and shall also be liable to fine.",
            "keywords": ["snatching", "forcibly", "grabs", "seizes"],
            "verified": True,
            "source": "Bharatiya Nyaya Sanhita, 2023"
        },
        {
            "section": 115,
            "title": "Voluntarily causing hurt",
            "chapter": "Chapter VI",
            "text": "Whoever does any act with the intention of thereby causing hurt to any person, or with the knowledge that he is likely thereby to cause hurt to any person, and does thereby cause hurt to any person, is said voluntarily to cause hurt.",
            "punishment": "Imprisonment of either description up to one year, or fine.",
            "keywords": ["hurt", "assault", "pain", "beating"],
            "verified": True,
            "source": "Bharatiya Nyaya Sanhita, 2023"
        }
    ]
    json_file = tmp_path / "mock_corpus.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)
    return BNSCorpus(str(json_file))


@pytest.fixture
def retriever(mock_corpus):
    return BM25LegalRetriever(mock_corpus)


# ── TEST 1: Successful Structured Model Response (State A) ──
def test_successful_structured_model_response(mock_corpus, retriever):
    """Verify genuine LLM success correctly populates contract and model identifier."""
    client = GeminiLegalClient(api_key="mock_test_key", model_name="gemini-2.5-flash")
    mock_genai_client = MagicMock()
    client._client = mock_genai_client

    valid_payload = {
        "stated_facts": ["Mobile phone removed from complainant's pocket", "Occurred at bus stop"],
        "negated_events": ["No physical force or violence was used"],
        "inferred_facts": ["Accused moved the property dishonestly"],
        "missing_facts_to_clarify": ["Confirm if anyone witnessed the accused taking the phone"],
        "recommended_action": "Register complaint for theft under Section 303 of BNS, 2023.",
        "candidate_evaluations": [
            {
                "section": 303,
                "applicability_score": 0.95,
                "reasoning": "Moving moveable property dishonestly out of possession without consent constitutes theft.",
                "statutory_elements_supported": ["dishonest intention", "moveable property", "without consent"],
                "unestablished_elements": []
            }
        ]
    }
    mock_response = MagicMock()
    mock_response.text = json.dumps(valid_payload)
    mock_genai_client.models.generate_content.return_value = mock_response

    # 1. Direct client evaluation test (State A inference succeeds)
    direct_eval = client.evaluate_complaint("Narrative text", "Context text")
    assert direct_eval == valid_payload

    # 2. Service level integration test
    service = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=client)
    res = service.analyze_complaint(NarrativeInput(
        narrative="Someone took my mobile phone out of my pocket without my consent while I was at the bus stop. No violence was used."
    ))

    # Strict assertion: Must identify as genuine Gemini LLM inference, NOT fallback
    assert res.model == "Gemini LLM + BM25 Grounded RAG (gemini-2.5-flash)"
    assert "Deterministic Fallback" not in res.model
    assert len(res.predictions) == 1
    assert res.predictions[0].section == 303
    assert res.predictions[0].title == "Theft"
    assert res.predictions[0].score > 0.6
    assert "No physical force or violence was used" in res.facts_analysis.negated_events
    assert res.facts_analysis.stated_facts == ["Mobile phone removed from complainant's pocket", "Occurred at bus stop"]


# ── TEST 2: Empty Model Response (State C & State B) ──
@pytest.mark.parametrize("empty_text", ["", "   ", None])
def test_empty_model_response(mock_corpus, retriever, empty_text):
    """Empty response from provider must raise LLMInferenceError and trigger fallback."""
    client = GeminiLegalClient(api_key="mock_test_key", model_name="gemini-2.5-flash")
    mock_genai_client = MagicMock()
    client._client = mock_genai_client

    mock_resp = MagicMock()
    mock_resp.text = empty_text
    mock_genai_client.models.generate_content.return_value = mock_resp

    # State C: Direct inference must raise explicit error, never return empty success
    with pytest.raises(LLMInferenceError, match="Empty model response"):
        client.evaluate_complaint("narrative", "context")

    # State B: Service must transparently fall back to deterministic retrieval
    service = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=client)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my phone from my pocket"))
    assert res.model == "BM25 Statutory Retrieval Engine (Deterministic Fallback - LLM Inference Failed)"
    assert res.inference_status == "fallback_llm_failed"
    assert "Gemini LLM" not in res.model
    assert len(res.predictions) > 0


# ── TEST 3: Invalid JSON Output (State C & State B) ──
def test_invalid_json_handling(mock_corpus, retriever):
    """Malformed non-JSON output must raise LLMInferenceError and trigger fallback."""
    client = GeminiLegalClient(api_key="mock_test_key", model_name="gemini-2.5-flash")
    mock_genai_client = MagicMock()
    client._client = mock_genai_client

    mock_resp = MagicMock()
    mock_resp.text = "Here is your analysis: { 'section': 303, unclosed json..."
    mock_genai_client.models.generate_content.return_value = mock_resp

    # State C: Direct client call raises explicit error
    with pytest.raises(LLMInferenceError, match="Malformed LLM JSON output"):
        client.evaluate_complaint("narrative", "context")

    # State B: Service switches to fallback
    service = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=client)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my purse in the market"))
    assert res.model == "BM25 Statutory Retrieval Engine (Deterministic Fallback - LLM Inference Failed)"
    assert res.inference_status == "fallback_llm_failed"
    assert len(res.predictions) > 0


# ── TEST 4: Missing Required Fields ──
def test_missing_required_fields_handling(mock_corpus, retriever):
    """LLM returns valid JSON but omits optional or internal fields; service defaults cleanly."""
    client = GeminiLegalClient(api_key="mock_test_key", model_name="gemini-2.5-flash")
    mock_genai_client = MagicMock()
    client._client = mock_genai_client

    # Minimal payload missing stated_facts, negated_events, reasoning, etc.
    sparse_payload = {
        "candidate_evaluations": [
            {"section": 303}
        ]
    }
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(sparse_payload)
    mock_genai_client.models.generate_content.return_value = mock_resp

    service = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=client)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone took my phone dishonestly"))

    assert res.model.startswith("Gemini LLM")
    assert len(res.predictions) == 1
    assert res.predictions[0].section == 303
    assert res.predictions[0].title == "Theft"
    assert res.predictions[0].reasoning  # Provided default
    assert isinstance(res.facts_analysis.stated_facts, list)
    assert isinstance(res.facts_analysis.missing_facts_to_clarify, list)


# ── TEST 5: Invalid Section Identifiers Rejection ──
def test_invalid_section_identifiers_rejection(mock_corpus, retriever):
    """Sections that do not exist in the verified BNS corpus must be filtered out."""
    client = GeminiLegalClient(api_key="mock_test_key", model_name="gemini-2.5-flash")
    mock_genai_client = MagicMock()
    client._client = mock_genai_client

    payload = {
        "candidate_evaluations": [
            {"section": 9999, "applicability_score": 0.99, "reasoning": "Hallucinated section"},
            {"section": 420, "applicability_score": 0.90, "reasoning": "Repealed IPC section"},
            {"section": "invalid_string", "applicability_score": 0.50},
            {"section": 303, "applicability_score": 0.85, "reasoning": "Valid theft section"}
        ]
    }
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(payload)
    mock_genai_client.models.generate_content.return_value = mock_resp

    service = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=client)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone took my property dishonestly"))

    pred_sections = [p.section for p in res.predictions]
    assert 9999 not in pred_sections
    assert 420 not in pred_sections
    assert 303 in pred_sections
    assert len(pred_sections) == 1


# ── TEST 6: Fabricated Source Citations Override ──
def test_fabricated_source_citations_overridden(mock_corpus, retriever):
    """Statutory citations must always come from the verified corpus, ignoring LLM attempts to fabricate."""
    client = GeminiLegalClient(api_key="mock_test_key", model_name="gemini-2.5-flash")
    mock_genai_client = MagicMock()
    client._client = mock_genai_client

    payload = {
        "candidate_evaluations": [
            {
                "section": 303,
                "applicability_score": 0.85,
                "reasoning": "Grounded reasoning",
                "source_citation": "Fabricated Custom Act 2099"  # Attemped fabrication
            }
        ]
    }
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(payload)
    mock_genai_client.models.generate_content.return_value = mock_resp

    service = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=client)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone took my phone dishonestly"))

    assert res.predictions[0].source_citation == "Bharatiya Nyaya Sanhita, 2023"
    assert "Fabricated" not in res.predictions[0].source_citation


# ── TEST 7: Provider Timeout ──
def test_provider_timeout_handling(mock_corpus, retriever):
    """Timeout from provider raises LLMInferenceError and activates fallback."""
    client = GeminiLegalClient(api_key="mock_test_key", model_name="gemini-2.5-flash")
    mock_genai_client = MagicMock()
    client._client = mock_genai_client
    mock_genai_client.models.generate_content.side_effect = TimeoutError("Deadline exceeded after 30000ms")

    # State C
    with pytest.raises(LLMInferenceError, match="Gemini API failure"):
        client.evaluate_complaint("narrative", "context")

    # State B
    service = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=client)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone snatched my gold chain forcibly"))
    assert res.model == "BM25 Statutory Retrieval Engine (Deterministic Fallback - LLM Inference Failed)"
    assert res.inference_status == "fallback_llm_failed"
    assert len(res.predictions) > 0


# ── TEST 8: Rate-Limit Response (HTTP 429) ──
def test_rate_limit_handling(mock_corpus, retriever):
    """Rate limit (429) from provider raises LLMInferenceError and activates fallback."""
    client = GeminiLegalClient(api_key="mock_test_key", model_name="gemini-2.5-flash")
    mock_genai_client = MagicMock()
    client._client = mock_genai_client
    mock_genai_client.models.generate_content.side_effect = Exception("429 ResourceExhausted: Quota exceeded")

    # State C
    with pytest.raises(LLMInferenceError, match="429 ResourceExhausted"):
        client.evaluate_complaint("narrative", "context")

    # State B
    service = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=client)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone took my bag forcibly"))
    assert res.model == "BM25 Statutory Retrieval Engine (Deterministic Fallback - LLM Inference Failed)"
    assert res.inference_status == "fallback_llm_failed"


# ── TEST 9: Authentication Failure ──
def test_authentication_failure(mock_corpus, retriever):
    """Unconfigured credentials or 401/403 provider responses."""
    # Sub-case 9a: No API key provided (isolated from ambient environment)
    with patch.dict("os.environ", {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
        unconfigured_client = GeminiLegalClient(api_key=None)
        assert not unconfigured_client.is_available
        with pytest.raises(LLMUnavailableError, match="API key not configured"):
            unconfigured_client.evaluate_complaint("narrative", "context")

    # Sub-case 9b: Invalid API key rejected by API (HTTP 401/403)
    auth_client = GeminiLegalClient(api_key="invalid_key")
    mock_genai_client = MagicMock()
    auth_client._client = mock_genai_client
    mock_genai_client.models.generate_content.side_effect = Exception("401 Invalid API Key")

    with pytest.raises(LLMInferenceError, match="401 Invalid API Key"):
        auth_client.evaluate_complaint("narrative", "context")

    # Sub-case 9c: Service engages fallback cleanly
    service = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=auth_client)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my laptop"))
    assert res.model == "BM25 Statutory Retrieval Engine (Deterministic Fallback - LLM Inference Failed)"
    assert res.inference_status == "fallback_llm_failed"


# ── TEST 10: Invalid Structured Output (JSON Array / Non-dict) ──
@pytest.mark.parametrize("invalid_raw", [
    json.dumps([{"section": 303}]),  # Top-level array instead of object
    json.dumps("Plain text string response"),  # Primitive string
    json.dumps(12345),  # Primitive number
])
def test_invalid_structured_output_types(mock_corpus, retriever, invalid_raw):
    """Model returning valid JSON that is not a JSON object must raise LLMInferenceError."""
    client = GeminiLegalClient(api_key="mock_test_key", model_name="gemini-2.5-flash")
    mock_genai_client = MagicMock()
    client._client = mock_genai_client

    mock_resp = MagicMock()
    mock_resp.text = invalid_raw
    mock_genai_client.models.generate_content.return_value = mock_resp

    # State C: Direct inference must reject non-dict output
    with pytest.raises(LLMInferenceError, match="expected JSON object"):
        client.evaluate_complaint("narrative", "context")

    # State B: Service switches to fallback
    service = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=client)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my watch"))
    assert res.model == "BM25 Statutory Retrieval Engine (Deterministic Fallback - LLM Inference Failed)"
    assert res.inference_status == "fallback_llm_failed"


# ── TEST 11: Incorrect Model Configuration ──
def test_incorrect_model_configuration(mock_corpus, retriever):
    """Specifying an unknown or unsupported model identifier."""
    client = GeminiLegalClient(api_key="mock_test_key", model_name="unsupported-gemini-v999")
    mock_genai_client = MagicMock()
    client._client = mock_genai_client
    mock_genai_client.models.generate_content.side_effect = Exception("404 Model unsupported-gemini-v999 not found")

    with pytest.raises(LLMInferenceError, match="404 Model unsupported-gemini-v999 not found"):
        client.evaluate_complaint("narrative", "context")

    service = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=client)
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my watch"))
    assert res.model == "BM25 Statutory Retrieval Engine (Deterministic Fallback - LLM Inference Failed)"
    assert res.inference_status == "fallback_llm_failed"


# ── TEST 12: Explicit Fallback Behaviour ──
def test_explicit_fallback_behaviour(mock_corpus, retriever):
    """Deterministic fallback must strictly produce verified BM25 rankings and transparent model tag."""
    mock_inactive_client = MagicMock(spec=GeminiLegalClient)
    mock_inactive_client.is_available = False

    service = LegalAnalysisService(
        corpus=mock_corpus,
        retriever=retriever,
        llm_client=mock_inactive_client,
        synonym_map={"stole": "theft"}
    )
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my mobile phone without any injury"))

    # Must accurately flag the fallback engine
    assert res.model == "BM25 Statutory Retrieval Engine (Deterministic Fallback - LLM Inactive)"
    assert res.inference_status == "fallback_llm_unavailable"
    assert "Gemini LLM" not in res.model

    # Must contain BM25 predictions
    assert len(res.predictions) > 0
    top_pred = res.predictions[0]
    assert top_pred.section in [303, 304]
    assert top_pred.source_citation == "Bharatiya Nyaya Sanhita, 2023"

    # Must extract negations and heuristic facts
    assert any("injury" in n for n in res.facts_analysis.negated_events)
    assert len(res.facts_analysis.stated_facts) > 0
    assert len(res.facts_analysis.missing_facts_to_clarify) > 0


# ── TEST 13: Strict Three-State Separation Guarantee ──
def test_three_state_separation_guarantee(mock_corpus, retriever):
    """
    Guarantees strict separation between:
    State A: Successful Gemini inference (model tag Gemini LLM ...)
    State B: Successful deterministic fallback (model tag BM25 Statutory Retrieval Engine ...)
    State C: Failed inference with explicit error (LLMInferenceError / LLMUnavailableError raised directly)
    """
    # Verify State C
    client_c = GeminiLegalClient(api_key="key")
    mock_g = MagicMock()
    client_c._client = mock_g
    mock_g.models.generate_content.side_effect = RuntimeError("Provider internal error")
    with pytest.raises(LLMInferenceError):
        client_c.evaluate_complaint("narrative", "context")

    # Verify State B
    service_b = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=client_c)
    res_b = service_b.analyze_complaint(NarrativeInput(narrative="Someone took my phone dishonestly"))
    assert res_b.model.startswith("BM25 Statutory Retrieval Engine")
    assert not res_b.model.startswith("Gemini LLM")

    # Verify State A
    client_a = GeminiLegalClient(api_key="key", model_name="gemini-2.5-flash")
    mock_ga = MagicMock()
    client_a._client = mock_ga
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "stated_facts": ["phone taken"],
        "candidate_evaluations": [{"section": 303, "applicability_score": 0.9}]
    })
    mock_ga.models.generate_content.return_value = mock_resp
    service_a = LegalAnalysisService(corpus=mock_corpus, retriever=retriever, llm_client=client_a)
    res_a = service_a.analyze_complaint(NarrativeInput(narrative="Someone took my phone dishonestly"))
    assert res_a.model.startswith("Gemini LLM")
    assert not res_a.model.startswith("BM25 Statutory Retrieval Engine")
