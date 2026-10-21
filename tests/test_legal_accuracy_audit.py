"""
Deterministic Regression Test Suite for BNS Legal Accuracy Audit and Pipeline Hardening.
Tests all 7 required scenarios using mocked Gemini clients to avoid API quota consumption:
1. Theft without stated violence
2. Robbery with relevant circumstances
3. Attempt versus completion
4. Unknown property value
5. Potential Section 303(2) proviso
6. Explicit negation
7. Insufficient information
"""

import json
import pytest
from unittest.mock import MagicMock

from legal_engine.corpus import BNSCorpus
from legal_engine.retrieval import BM25LegalRetriever
from legal_engine.llm_client import GeminiLegalClient
from legal_engine.service import LegalAnalysisService
from legal_engine.schemas import NarrativeInput


@pytest.fixture
def test_corpus(tmp_path):
    """Fixture providing verified statutory records for property offences."""
    data = [
        {
            "section": 303,
            "title": "Theft",
            "chapter": "Chapter XVII",
            "text": (
                "Whoever, intending to take dishonestly any movable property out of the possession of any person "
                "without that person’s consent, moves that property in order to such taking, is said to commit theft.\n\n"
                "Whoever commits theft shall be punished with imprisonment of either description for a term which may "
                "extend to three years, or with fine, or with both;\n\n"
                "Provided that in cases of theft where the value of the stolen property is less than five thousand rupees, "
                "and a person is convicted for the first time, shall upon return of the value of property or restoration "
                "of the stolen property, shall be punished with community service."
            ),
            "punishment": "Imprisonment up to three years, or fine, or both. Proviso: community service for first-time theft < Rs 5,000 upon restoration.",
            "keywords": ["theft", "dishonestly", "movable", "property", "pocket", "moves", "consent", "stolen", "stole", "laptop", "car", "pen"],
            "verified": True,
            "source": "Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023)",
            "schedule_i_status": "unverified_schedule"
        },
        {
            "section": 304,
            "title": "Snatching",
            "chapter": "Chapter XVII",
            "text": (
                "Theft is snatching if, in order to commit theft, the offender suddenly or quickly or forcibly "
                "seizes or secures or grabs or takes away from any person or from his possession any moveable property."
            ),
            "punishment": "Imprisonment up to three years, and fine.",
            "keywords": ["snatching", "forcibly", "grabs", "seizes", "quickly", "suddenly"],
            "verified": True,
            "source": "Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023)",
            "schedule_i_status": "unverified_schedule"
        },
        {
            "section": 309,
            "title": "Robbery",
            "chapter": "Chapter XVII",
            "text": (
                "In all robbery there is either theft or extortion. Theft is robbery if, in order to the committing of the theft, "
                "or in committing the theft, or in carrying away property obtained by theft, the offender for that end voluntarily "
                "causes or attempts to cause death or hurt or wrongful restraint, or fear of instant death or hurt or wrongful restraint."
            ),
            "punishment": "Rigorous imprisonment up to ten years, and fine.",
            "keywords": ["robbery", "hurt", "death", "wrongful", "restraint", "instant", "fear", "weapon", "force"],
            "verified": True,
            "source": "Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023)",
            "schedule_i_status": "unverified_schedule"
        },
        {
            "section": 314,
            "title": "Dishonest misappropriation of property",
            "chapter": "Chapter XVII",
            "text": (
                "Whoever dishonestly misappropriates or converts to his own use any movable property, shall be punished "
                "with imprisonment for a term between six months and two years and fine. Finding property or gold ring on road."
            ),
            "punishment": "Imprisonment between six months and two years, and fine.",
            "keywords": ["misappropriates", "converts", "movable", "property", "dishonest", "found", "finds", "ring", "road"],
            "verified": True,
            "source": "Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023)",
            "schedule_i_status": "unverified_schedule"
        },
        {
            "section": 115,
            "title": "Voluntarily causing hurt",
            "chapter": "Chapter VI",
            "text": "Whoever does any act with the intention of thereby causing hurt is said voluntarily to cause hurt.",
            "punishment": "Imprisonment up to one year, or fine.",
            "keywords": ["hurt", "bodily", "pain", "assault"],
            "verified": True,
            "source": "Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023)",
            "schedule_i_status": "unverified_schedule"
        }
    ]
    json_path = tmp_path / "test_rag_corpus.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return BNSCorpus(str(json_path))


@pytest.fixture
def test_retriever(test_corpus):
    return BM25LegalRetriever(test_corpus)


def make_mock_service(test_corpus, test_retriever, llm_response_dict):
    mock_client = MagicMock(spec=GeminiLegalClient)
    mock_client.is_available = True
    mock_client.model_name = "gemini-3.8-flash"
    mock_client.evaluate_complaint.return_value = llm_response_dict
    return LegalAnalysisService(
        corpus=test_corpus,
        retriever=test_retriever,
        llm_client=mock_client
    )


# ── SCENARIO 1: THEFT WITHOUT STATED VIOLENCE ──
def test_scenario_1_theft_without_stated_violence(test_corpus, test_retriever):
    """
    Complaint: 'Someone took my mobile phone out of my pocket without my consent while I was standing at the bus stop. No weapons were used and no one was hurt.'
    Verifies:
    - Primary candidate is Section 303 (Theft).
    - Section 309 (Robbery) is NOT returned as an applicable candidate.
    - Section 314 (Dishonest Misappropriation) is demoted / subordinated to Section 303.
    - Inferred facts contain dishonest intention, not treated as physical stated fact.
    - Missing facts include unverified property value and prior history.
    - Procedural recommendation is qualified and not an unconditional FIR.
    """
    raw_narrative = (
        "Someone took my mobile phone out of my pocket without my consent while I was standing at the bus stop. "
        "No weapons were used and no one was hurt."
    )
    llm_payload = {
        "stated_facts": [
            "Mobile phone removed from complainant's pocket",
            "Complainant did not give consent",
            "Incident occurred at a bus stop"
        ],
        "negated_events": ["No weapons were used", "No one was hurt"],
        "inferred_facts": ["Accused acted with dishonest intention to permanently deprive"],
        "missing_facts_to_clarify": [
            "Monetary value of the mobile phone",
            "Identity of the perpetrator"
        ],
        "recommended_action": "Procedural guidance under BNSS",
        "candidate_evaluations": [
            {
                "section": 303,
                "applicability_score": 0.95,
                "reasoning": "Moving movable property out of possession without consent satisfies theft ingredients.",
                "statutory_elements_supported": ["movable property", "taken out of possession", "without consent"],
                "unestablished_elements": ["property value", "prior history of suspect"]
            },
            {
                "section": 309,
                "applicability_score": 0.25,
                "reasoning": "Robbery requires hurt/violence which is absent.",
                "statutory_elements_supported": ["theft of phone"],
                "unestablished_elements": ["voluntarily causing hurt or fear of instant hurt"]
            },
            {
                "section": 314,
                "applicability_score": 0.30,
                "reasoning": "Alternative property conversion provision.",
                "statutory_elements_supported": ["movable property"],
                "unestablished_elements": ["initial innocent possession subsequently converted"]
            }
        ]
    }

    service = make_mock_service(test_corpus, test_retriever, llm_payload)
    res = service.analyze_complaint(NarrativeInput(narrative=raw_narrative))

    # Verify predictions
    pred_sections = [p.section for p in res.predictions]
    assert 303 in pred_sections
    assert pred_sections[0] == 303  # Primary candidate

    # Section 309 Robbery MUST NOT be in viable predictions because violence is negated
    assert 309 not in pred_sections

    # Section 314 (if included) must be strictly subordinate in score
    sec303_pred = next(p for p in res.predictions if p.section == 303)
    sec314_preds = [p for p in res.predictions if p.section == 314]
    if sec314_preds:
        assert sec303_pred.score > sec314_preds[0].score

    # Verify fact separation
    assert any("dishonest" in f.lower() for f in res.facts_analysis.inferred_facts)
    assert not any("dishonest" in f.lower() for f in res.facts_analysis.stated_facts)
    assert any("no weapons" in n.lower() for n in res.facts_analysis.negated_events)
    assert any("no one was hurt" in n.lower() or "hurt" in n.lower() for n in res.facts_analysis.negated_events)

    # Verify missing facts
    missing_str = " ".join(res.facts_analysis.missing_facts_to_clarify).lower()
    assert "value" in missing_str

    # Verify procedural recommendation is conditional, NOT an unconditional FIR
    action_text = res.recommended_action
    assert "conditional" in action_text.lower() or "depends on" in action_text.lower()
    assert "5,000" in action_text or "5000" in action_text
    assert "proviso" in action_text.lower() or "community service" in action_text.lower()
    assert "174" in action_text  # Mentions NCR / Sec 174 BNSS for proviso


# ── SCENARIO 2: ROBBERY WITH RELEVANT CIRCUMSTANCES ──
def test_scenario_2_robbery_with_relevant_circumstances(test_corpus, test_retriever):
    """
    Complaint: 'A man stopped me on the road, held a knife to my neck threatening to kill me if I did not hand over my wallet, and forced me to give it to him.'
    Verifies:
    - Primary candidate is Section 309 (Robbery).
    - Statutory elements supported include threat of instant death/hurt and weapon.
    - Cognizable under Section 173 BNSS.
    """
    narrative = (
        "A man stopped me on the road, held a knife to my neck threatening to kill me if I did not hand over my wallet, "
        "and forced me to give it to him."
    )
    llm_payload = {
        "stated_facts": [
            "Accused held a knife to complainant's neck",
            "Accused threatened to kill complainant",
            "Accused forcibly took complainant's wallet"
        ],
        "negated_events": [],
        "inferred_facts": ["Accused intended to extort/rob under fear of instant death"],
        "missing_facts_to_clarify": ["Value of contents in wallet", "Identity of the accused"],
        "recommended_action": "Register FIR for Robbery under Section 173 BNSS.",
        "candidate_evaluations": [
            {
                "section": 309,
                "applicability_score": 0.95,
                "reasoning": "Taking property by putting complainant in fear of instant death or hurt constitutes Robbery under Section 309 BNS.",
                "statutory_elements_supported": [
                    "taking movable property",
                    "extortion/theft",
                    "fear of instant death or hurt",
                    "use of deadly weapon (knife)"
                ],
                "unestablished_elements": ["identity of suspect"]
            }
        ]
    }

    service = make_mock_service(test_corpus, test_retriever, llm_payload)
    res = service.analyze_complaint(NarrativeInput(narrative=narrative))

    assert len(res.predictions) > 0
    top_pred = res.predictions[0]
    assert top_pred.section == 309
    assert top_pred.title == "Robbery"
    assert top_pred.score > 0.7
    assert any("fear" in el.lower() or "death" in el.lower() or "weapon" in el.lower() for el in top_pred.statutory_elements_supported)
    assert "173" in res.recommended_action
    assert "robbery" in res.recommended_action.lower()


# ── SCENARIO 3: ATTEMPT VERSUS COMPLETION ──
def test_scenario_3_attempt_versus_completion(test_corpus, test_retriever):
    """
    Complaint: 'While walking home, an unknown person tried to snatch my purse from my shoulder, but I held on tightly and shouted for help. He could not take anything and fled empty-handed.'
    Verifies:
    - Attempt recognized; completed taking of property is identified as unestablished.
    - Negations / failure to take property recorded.
    """
    narrative = (
        "While walking home, an unknown person tried to snatch my purse from my shoulder, "
        "but I held on tightly and shouted for help. He could not take anything and fled empty-handed."
    )
    llm_payload = {
        "stated_facts": [
            "Accused tried to grab purse from complainant's shoulder",
            "Complainant resisted and shouted for help",
            "Accused fled empty-handed without obtaining property"
        ],
        "negated_events": ["No property was taken", "Theft was not completed"],
        "inferred_facts": ["Attempt to commit snatching/theft"],
        "missing_facts_to_clarify": ["Identity or description of the accused"],
        "recommended_action": "Record attempt to commit offence under substantive section read with BNS Section 62.",
        "candidate_evaluations": [
            {
                "section": 304,
                "applicability_score": 0.65,
                "reasoning": "Attempted snatching. Physical attempt to seize property was made but completed taking was frustrated.",
                "statutory_elements_supported": ["forcible attempt to grab property"],
                "unestablished_elements": ["completed taking of movable property out of possession"]
            }
        ]
    }

    service = make_mock_service(test_corpus, test_retriever, llm_payload)
    res = service.analyze_complaint(NarrativeInput(narrative=narrative))

    assert len(res.predictions) > 0
    top_pred = res.predictions[0]
    assert top_pred.section in [303, 304]
    assert any("completed" in u.lower() or "taking" in u.lower() for u in top_pred.unestablished_elements)
    assert any("not taken" in n.lower() or "not completed" in n.lower() for n in res.facts_analysis.negated_events)


# ── SCENARIO 4: UNKNOWN PROPERTY VALUE ──
def test_scenario_4_unknown_property_value(test_corpus, test_retriever):
    """
    Complaint: 'Someone took my vintage pen from my office desk while I stepped away. Nobody saw who took it.'
    Verifies:
    - Section 303 (Theft) candidate.
    - Missing facts explicitly highlight unknown property value.
    - Procedural recommendation explicitly avoids unconditional FIR, stating conditional paths under Section 303(2) BNS.
    """
    narrative = "Someone took my vintage pen from my office desk while I stepped away. Nobody saw who took it."
    llm_payload = {
        "stated_facts": [
            "Vintage pen taken from complainant's office desk",
            "Complainant was away from desk",
            "No witnesses observed the taking"
        ],
        "negated_events": [],
        "inferred_facts": ["Dishonest intention inferred from removal without consent"],
        "missing_facts_to_clarify": [
            "Value of the vintage pen",
            "Suspect identity"
        ],
        "recommended_action": "",
        "candidate_evaluations": [
            {
                "section": 303,
                "applicability_score": 0.90,
                "reasoning": "Movable property moved out of possession without consent.",
                "statutory_elements_supported": ["movable property", "taken out of possession", "without consent"],
                "unestablished_elements": ["monetary value of pen", "identity of suspect"]
            }
        ]
    }

    service = make_mock_service(test_corpus, test_retriever, llm_payload)
    res = service.analyze_complaint(NarrativeInput(narrative=narrative))

    # Missing facts must contain property value
    missing_all = " ".join(res.facts_analysis.missing_facts_to_clarify).lower()
    assert "value" in missing_all

    # Procedural guidance must be conditional, acknowledging the < Rs 5,000 threshold
    action = res.recommended_action
    assert "5,000" in action or "5000" in action
    assert "conditional" in action.lower() or "depends on" in action.lower()
    assert "174" in action  # BNSS 174 non-cognizable path referenced


# ── SCENARIO 5: POTENTIAL SECTION 303(2) PROVISO ──
def test_scenario_5_potential_section_303_2_proviso(test_corpus, test_retriever):
    """
    Complaint: 'A neighbor teenager took an old bicycle worth Rs 2000 from my porch without asking. He has no prior criminal record, admitted his mistake, and returned the bicycle to me the next morning.'
    Verifies:
    - Facts relevant to Section 303(2) proviso: value < Rs 5,000, first-time offender, property returned.
    - Identifies community service and non-cognizable status under BNSS Schedule I.
    - Procedural recommendation directs to Section 174 BNSS (NCR / Magistrate), NOT unconditional Section 173 FIR.
    """
    narrative = (
        "A neighbor teenager took an old bicycle worth Rs 2000 from my porch without asking. "
        "He has no prior criminal record, admitted his mistake, and returned the bicycle to me the next morning."
    )
    llm_payload = {
        "stated_facts": [
            "Bicycle worth Rs 2,000 taken from porch without asking",
            "Accused has no prior criminal record",
            "Accused returned the bicycle next morning"
        ],
        "negated_events": ["No prior criminal history"],
        "inferred_facts": ["Initial taking was without consent"],
        "missing_facts_to_clarify": [],
        "recommended_action": "Qualifying circumstances under Section 303(2) proviso.",
        "candidate_evaluations": [
            {
                "section": 303,
                "applicability_score": 0.85,
                "reasoning": "Theft of bicycle under Rs 5,000 with first-time offender restoration engages the Section 303(2) proviso.",
                "statutory_elements_supported": ["movable property", "taken without consent", "value under Rs 5,000", "property restored"],
                "unestablished_elements": []
            }
        ]
    }

    service = make_mock_service(test_corpus, test_retriever, llm_payload)
    res = service.analyze_complaint(NarrativeInput(narrative=narrative))

    action = res.recommended_action
    assert "proviso" in action.lower() or "community service" in action.lower()
    assert "non-cognizable" in action.lower()
    assert "174" in action  # Requires Section 174 BNSS NCR procedure
    assert "bailable" in action.lower()


# ── SCENARIO 6: EXPLICIT NEGATION ──
def test_scenario_6_explicit_negation(test_corpus, test_retriever):
    """
    Complaint: 'My bag went missing from my car seat. No weapons were used, no force was used, and no one was hurt or threatened.'
    Verifies:
    - Captures all negative assertions in negated_events.
    - Robbery Section 309 is strictly excluded or assigned 0.0 applicability.
    - Supported elements do not claim force, hurt, or weapons.
    """
    narrative = "My bag went missing from my car seat. No weapons were used, no force was used, and no one was hurt or threatened."
    llm_payload = {
        "stated_facts": ["Bag missing from car seat"],
        "negated_events": ["No weapons were used", "No force was used", "No one was hurt or threatened"],
        "inferred_facts": [],
        "missing_facts_to_clarify": ["Value of bag", "Did someone break into the car?"],
        "recommended_action": "",
        "candidate_evaluations": [
            {
                "section": 303,
                "applicability_score": 0.85,
                "reasoning": "Movable property moved out of car seat without consent.",
                "statutory_elements_supported": ["movable property"],
                "unestablished_elements": ["perpetrator identity", "taking out of possession"]
            },
            {
                "section": 309,
                "applicability_score": 0.40,
                "reasoning": "Robbery candidate.",
                "statutory_elements_supported": [],
                "unestablished_elements": ["hurt, violence, force, weapons"]
            }
        ]
    }

    service = make_mock_service(test_corpus, test_retriever, llm_payload)
    res = service.analyze_complaint(NarrativeInput(narrative=narrative))

    # Robbery Section 309 must be completely excluded from predictions
    pred_sections = [p.section for p in res.predictions]
    assert 309 not in pred_sections

    # Negated events must contain weapons, force, hurt
    neg_text = " ".join(res.facts_analysis.negated_events).lower()
    assert "weapon" in neg_text
    assert "force" in neg_text
    assert "hurt" in neg_text or "threatened" in neg_text


# ── SCENARIO 7: INSUFFICIENT INFORMATION ──
def test_scenario_7_insufficient_information(test_corpus, test_retriever):
    """
    Complaint: 'Something strange happened near Dadar station yesterday evening.'
    Verifies:
    - Factual narrative is too ambiguous to identify specific penal offences.
    - Empty or inconclusive predictions.
    - Procedural recommendation states insufficient facts and advises preliminary inquiry.
    """
    narrative = "Something strange happened near Dadar station yesterday evening."
    llm_payload = {
        "stated_facts": ["Unspecified event occurred near Dadar station yesterday evening"],
        "negated_events": [],
        "inferred_facts": [],
        "missing_facts_to_clarify": [
            "What specific acts occurred?",
            "Was any property stolen, person injured, or law broken?"
        ],
        "recommended_action": "Insufficient facts to establish any penal offence.",
        "candidate_evaluations": []
    }

    service = make_mock_service(test_corpus, test_retriever, llm_payload)
    res = service.analyze_complaint(NarrativeInput(narrative=narrative))

    assert len(res.predictions) == 0
    assert "insufficient" in res.recommended_action.lower() or "preliminary inquiry" in res.recommended_action.lower()


# ── SCENARIO 8: ROBBERY BY WRONGFUL RESTRAINT WITHOUT WEAPONS OR INJURY ──
def test_scenario_8_robbery_by_wrongful_restraint_without_weapons_or_injury(test_corpus, test_retriever):
    """
    Complaint: 'Two men blocked my path, pinned my arms against a wall, and took my wallet out of my pocket. No weapons were used and nobody was hurt.'
    Verifies:
    - BNS Section 309 includes statutory alternative of wrongful restraint.
    - Section 309 is NOT excluded merely because weapons and completed injury are absent.
    - Supported elements identify wrongful restraint.
    - Classified as cognizable and non-bailable under verified BNSS Schedule I metadata.
    """
    narrative = (
        "Two men blocked my path, pinned my arms against a wall, and took my wallet out of my pocket. "
        "No weapons were used and nobody was hurt."
    )
    llm_payload = {
        "stated_facts": [
            "Two men blocked complainant's path and pinned complainant's arms against a wall",
            "Wallet removed from complainant's pocket without consent"
        ],
        "negated_events": ["No weapons were used", "Nobody was hurt"],
        "inferred_facts": ["Offenders acted conjointly with common intention"],
        "missing_facts_to_clarify": ["Value of wallet contents", "Identity of the two men"],
        "recommended_action": "Register FIR for Robbery under Section 173 BNSS.",
        "candidate_evaluations": [
            {
                "section": 309,
                "applicability_score": 0.90,
                "reasoning": "Theft accompanied by wrongful restraint (blocking and pinning against a wall) satisfies Robbery under BNS Section 309.",
                "statutory_elements_supported": ["taking movable property", "wrongful restraint to commit theft"],
                "unestablished_elements": ["identity of suspects"]
            }
        ]
    }

    service = make_mock_service(test_corpus, test_retriever, llm_payload)
    res = service.analyze_complaint(NarrativeInput(narrative=narrative))

    # Section 309 MUST be supported, NOT excluded!
    pred_sections = [p.section for p in res.predictions]
    assert 309 in pred_sections
    top_pred = res.predictions[0]
    assert top_pred.section == 309
    assert top_pred.score > 0.6
    assert any("restraint" in el.lower() for el in top_pred.statutory_elements_supported)

    # Schedule I metadata verification
    assert top_pred.is_cognizable is True
    assert top_pred.is_bailable is False


# ── SCENARIO 9: BNSS SCHEDULE I METADATA VERIFICATION ──
def test_scenario_9_schedule_i_metadata_verification(test_corpus, test_retriever):
    """
    Verifies reconciliation of Schedule I metadata:
    - Unconditional verified sections (309, 304, 314) have verified booleans.
    - Conditional section (303) derives booleans when value is verified.
    - Unknown property value preserves None.
    """
    # 1. Section 314 (Dishonest Misappropriation): Verified Non-cognizable (False), Bailable (True)
    service = make_mock_service(test_corpus, test_retriever, {
        "stated_facts": ["Found gold ring on the high road, knew the owner from inscription, but sold it."],
        "negated_events": [],
        "inferred_facts": [],
        "missing_facts_to_clarify": [],
        "recommended_action": "Record NCR under Section 174 BNSS.",
        "candidate_evaluations": [
            {"section": 314, "applicability_score": 0.85, "reasoning": "Misappropriation of found property."}
        ]
    })
    res_314 = service.analyze_complaint(NarrativeInput(narrative="Found gold ring on road, sold it."))
    pred_314 = next(p for p in res_314.predictions if p.section == 314)
    assert pred_314.is_cognizable is False
    assert pred_314.is_bailable is True

    # 2. Section 303 with verified value >= Rs 5,000: Verified Cognizable (True), Non-bailable (False)
    service_high = make_mock_service(test_corpus, test_retriever, {
        "stated_facts": ["Laptop worth Rs 50000 stolen from car."],
        "negated_events": [],
        "inferred_facts": [],
        "missing_facts_to_clarify": [],
        "recommended_action": "Action",
        "candidate_evaluations": [
            {"section": 303, "applicability_score": 0.90, "reasoning": "Theft."}
        ]
    })
    res_high = service_high.analyze_complaint(NarrativeInput(narrative="Someone stole my laptop worth Rs 50000."))
    pred_high = next(p for p in res_high.predictions if p.section == 303)
    assert pred_high.is_cognizable is True
    assert pred_high.is_bailable is False

    # 3. Section 303 with unknown value: Preserves explicit None
    service_unk = make_mock_service(test_corpus, test_retriever, {
        "stated_facts": ["Pen stolen from desk."],
        "negated_events": [],
        "inferred_facts": [],
        "missing_facts_to_clarify": ["Value of pen"],
        "recommended_action": "Action",
        "candidate_evaluations": [
            {"section": 303, "applicability_score": 0.80, "reasoning": "Theft."}
        ]
    })
    res_unk = service_unk.analyze_complaint(NarrativeInput(narrative="Someone took my pen from my desk."))
    pred_unk = next(p for p in res_unk.predictions if p.section == 303)
    assert pred_unk.is_cognizable is None
    assert pred_unk.is_bailable is None


# ── SCENARIO 10: NEGATED VIOLENCE WITH SEPARATE QUALIFYING THREAT ──
def test_scenario_10_negated_violence_with_qualifying_threat(test_corpus, test_retriever):
    """
    Complaint: 'There was no physical violence and no weapon was used, but the man cornered me and threatened to break my teeth if I did not hand over my wallet.'
    Verifies:
    - Negation of 'physical violence' and 'weapon' does NOT erase positive evidence of 'cornered' (wrongful restraint) and 'threatened' (fear of instant hurt).
    - Section 309 Robbery is retained and supported.
    - Supported elements identify wrongful restraint and threat of instant hurt.
    - Procedural classification is Cognizable (True) and Non-bailable (False) under BNSS Schedule I.
    """
    narrative = (
        "There was no physical violence and no weapon was used, but the man cornered me and threatened to break my teeth "
        "if I did not hand over my wallet."
    )
    llm_payload = {
        "stated_facts": [
            "Man cornered the complainant",
            "Man demanded wallet with verbal threat to break teeth",
            "Complainant handed over wallet"
        ],
        "negated_events": ["No physical violence occurred", "No weapon was used"],
        "inferred_facts": ["Theft accompanied by fear of instant hurt and wrongful restraint"],
        "missing_facts_to_clarify": ["Value of wallet", "Suspect identity"],
        "recommended_action": "FIR under Section 173 BNSS.",
        "candidate_evaluations": [
            {
                "section": 309,
                "applicability_score": 0.85,
                "reasoning": "Theft accompanied by fear of instant hurt and wrongful restraint.",
                "statutory_elements_supported": [],
                "unestablished_elements": ["perpetrator identity"]
            },
            {
                "section": 303,
                "applicability_score": 0.60,
                "reasoning": "Underlying theft of wallet.",
                "statutory_elements_supported": ["movable property"],
                "unestablished_elements": []
            }
        ]
    }

    service = make_mock_service(test_corpus, test_retriever, llm_payload)
    res = service.analyze_complaint(NarrativeInput(narrative=narrative))

    pred_sections = [p.section for p in res.predictions]
    assert 309 in pred_sections

    pred_309 = next(p for p in res.predictions if p.section == 309)
    assert pred_309.score > 0.5
    assert pred_309.is_cognizable is True
    assert pred_309.is_bailable is False

    # Positive evidence of threat / restraint must be preserved
    supp_text = " ".join(pred_309.statutory_elements_supported).lower()
    assert "restraint" in supp_text or "threat" in supp_text or "fear" in supp_text
    # Negated items must NOT be claimed as supported
    assert "weapon" not in supp_text


# ── SCENARIO 11: BM25 CANNOT OVERRIDE STATUTORY CONTRADICTION ──
def test_scenario_11_bm25_cannot_override_statutory_contradiction(test_corpus, test_retriever):
    """
    Verifies that high BM25 lexical similarity cannot override explicit statutory contradiction.
    When complaint explicitly negates all aggravating circumstances of Robbery,
    Section 309 must be zeroed out and excluded from predictions even if BM25 score is high.
    """
    narrative = "My pen was taken from my desk while I was at lunch. No one threatened me, no one hurt me, and no force was used."
    # Simulate an LLM attempting to assign positive score to 309
    llm_payload = {
        "stated_facts": ["Pen missing from desk"],
        "negated_events": ["No one threatened me", "No one hurt me", "No force was used"],
        "inferred_facts": [],
        "missing_facts_to_clarify": ["Value of pen"],
        "recommended_action": "Preliminary enquiry",
        "candidate_evaluations": [
            {
                "section": 309,
                "applicability_score": 0.45,
                "reasoning": "Robbery candidate based on stolen property.",
                "statutory_elements_supported": [],
                "unestablished_elements": []
            },
            {
                "section": 303,
                "applicability_score": 0.85,
                "reasoning": "Theft of movable property without consent.",
                "statutory_elements_supported": ["movable property"],
                "unestablished_elements": []
            }
        ]
    }

    service = make_mock_service(test_corpus, test_retriever, llm_payload)
    res = service.analyze_complaint(NarrativeInput(narrative=narrative))

    pred_sections = [p.section for p in res.predictions]
    # Section 309 must be completely excluded
    assert 309 not in pred_sections
    assert 303 in pred_sections

