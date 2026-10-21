"""
Adversarial Test Suite for Legal Gate Safety and Non-Penal Grievance Auditing.

Verifies the 7 mandatory adversarial scenarios specified in Task 1:
1. Genuine theft or robbery allegation.
2. Figurative commercial complaint.
3. Workplace grievance with insufficient facts.
4. Complaint involving digital or financial interests where another offence may need consideration.
5. Mixed narrative containing a commercial dispute and a separate alleged criminal act.
6. Negated physical violence alongside a distinct positive allegation of force or threat.
7. Physical-risk keywords appearing in irrelevant or hypothetical context.

Explicitly measures False Positives and False Negatives of the non-penal grievance gate separately.
"""

import pytest
from legal_engine.corpus import BNSCorpus
from legal_engine.retrieval import BM25LegalRetriever
from legal_engine.llm_client import GeminiLegalClient
from legal_engine.service import LegalAnalysisService
from legal_engine.schemas import NarrativeInput


@pytest.fixture(scope="module")
def deterministic_service():
    """Initializes a deterministic LegalAnalysisService with LLM explicitly disabled."""
    corpus = BNSCorpus()
    retriever = BM25LegalRetriever(corpus)
    llm_client = GeminiLegalClient(api_key="")
    return LegalAnalysisService(corpus=corpus, retriever=retriever, llm_client=llm_client)


# ── SCENARIO 1: Genuine Theft or Robbery Allegation ──
def test_scenario_1_genuine_theft_robbery(deterministic_service):
    """A genuine theft or robbery allegation must NEVER be suppressed by the grievance gate."""
    narrative = (
        "Two men cornered me in an alley near Kurla station. One man pinned both my arms tightly "
        "against the brick wall, physically restraining me, while the other took my wallet and watch."
    )
    # Gate check
    gate_res = deterministic_service._detect_non_penal_grievance(narrative)
    assert gate_res is None, "Gate must not fire on genuine robbery"

    res = deterministic_service.analyze_complaint(NarrativeInput(narrative=narrative))
    pred_sections = [p.section for p in res.predictions]
    assert len(pred_sections) > 0
    assert 309 in pred_sections or 303 in pred_sections


# ── SCENARIO 2: Figurative Commercial Complaint ──
def test_scenario_2_figurative_commercial_complaint(deterministic_service):
    """Figurative commercial complaint must be classified as preliminary non-penal grievance."""
    narrative = (
        "This restaurant is charging daylight robbery prices for dinner! "
        "They charged Rs 1,200 for a paneer dish and Rs 300 for one roti. The manager was rude."
    )
    gate_res = deterministic_service._detect_non_penal_grievance(narrative)
    assert gate_res is not None
    assert gate_res[0] == "consumer_pricing"

    res = deterministic_service.analyze_complaint(NarrativeInput(narrative=narrative))
    assert len(res.predictions) == 0
    assert "preliminary classification" in res.recommended_action.lower()
    assert "consumer pricing dispute" in res.recommended_action.lower()
    assert "consumer protection act" in res.recommended_action.lower()


# ── SCENARIO 3: Workplace Grievance with Insufficient Facts ──
def test_scenario_3_workplace_grievance_insufficient_facts(deterministic_service):
    """Workplace grievance must cite Section 2(22) movable property distinction and qualify missing facts."""
    narrative = (
        "My manager stole all credit for my marketing presentation in the board meeting and refused my promotion."
    )
    gate_res = deterministic_service._detect_non_penal_grievance(narrative)
    assert gate_res is not None
    assert gate_res[0] == "intangible_metaphor"

    res = deterministic_service.analyze_complaint(NarrativeInput(narrative=narrative))
    assert len(res.predictions) == 0
    action = res.recommended_action
    # Must cite Section 2(22) authoritative BNS text, not repealed or incorrect sections
    assert "2(22)" in action
    assert "preliminary" in action.lower()
    # Must preserve alternative pathways and identify missing facts
    assert len(res.facts_analysis.missing_facts_to_clarify) > 0


# ── SCENARIO 4: Complaint Involving Digital or Financial Interests ──
def test_scenario_4_digital_financial_interests(deterministic_service):
    """Complaint involving digital/financial interests must NOT be suppressed by career/intangible language."""
    narrative = (
        "My colleague took credit for my presentation, and also accessed my work station without permission, "
        "deleted database backup files, and embezzled company funds."
    )
    # Must NOT be gated as a mere career grievance because embezzlement and database deletion are alleged
    gate_res = deterministic_service._detect_non_penal_grievance(narrative)
    assert gate_res is None, "Gate must not suppress financial embezzlement or record tampering"

    res = deterministic_service.analyze_complaint(NarrativeInput(narrative=narrative))
    pred_sections = [p.section for p in res.predictions]
    assert len(pred_sections) > 0
    assert 316 in pred_sections or 314 in pred_sections or 303 in pred_sections


# ── SCENARIO 5: Mixed Narrative with Commercial Dispute and Criminal Act ──
def test_scenario_5_mixed_commercial_and_crime(deterministic_service):
    """Mixed narrative with commercial pricing dispute and separate crime must NOT be suppressed."""
    narrative = (
        "The restaurant charged daylight robbery prices for dinner. Outside on the road, "
        "an unknown youth suddenly grabbed and snatched my gold chain from my neck and fled."
    )
    gate_res = deterministic_service._detect_non_penal_grievance(narrative)
    assert gate_res is None, "Gate must not suppress complaint containing affirmative snatching allegation"

    res = deterministic_service.analyze_complaint(NarrativeInput(narrative=narrative))
    pred_sections = [p.section for p in res.predictions]
    assert 304 in pred_sections, "Section 304 (Snatching) must be retrieved and predicted"
    # Figurative 'daylight robbery' must NOT cause Section 309 Robbery to be predicted when no robbery elements exist
    assert 309 not in pred_sections


# ── SCENARIO 6: Negated Violence Alongside Distinct Force or Threat ──
def test_scenario_6_negated_violence_with_positive_threat(deterministic_service):
    """Negated physical violence must NOT erase distinct positive threat of death/injury."""
    narrative = (
        "There was no physical violence and no one was hurt, but he threatened to kill my brother "
        "if I did not hand over my car keys."
    )
    gate_res = deterministic_service._detect_non_penal_grievance(narrative)
    assert gate_res is None

    res = deterministic_service.analyze_complaint(NarrativeInput(narrative=narrative))
    pred_sections = [p.section for p in res.predictions]
    assert len(pred_sections) > 0
    assert 351 in pred_sections, "Section 351 (Criminal Intimidation) must be predicted"


# ── SCENARIO 7: Physical-Risk Keywords in Hypothetical Context ──
def test_scenario_7_physical_risk_in_hypothetical_context(deterministic_service):
    """Physical-risk keywords in purely hypothetical similes must NOT fool gate into predicting violent crime."""
    narrative = (
        "The prices at this cinema are daylight robbery. A guy with a gun could not take my money "
        "faster than this popcorn counter."
    )
    # The 'gun' mention is purely hypothetical; the complaint is purely commercial pricing
    gate_res = deterministic_service._detect_non_penal_grievance(narrative)
    assert gate_res is not None, "Hypothetical gun simile must not prevent gate from identifying commercial pricing grievance"
    assert gate_res[0] == "consumer_pricing"

    res = deterministic_service.analyze_complaint(NarrativeInput(narrative=narrative))
    assert len(res.predictions) == 0
    # Must NOT predict Section 309 (Robbery)
    pred_sections = [p.section for p in res.predictions]
    assert 309 not in pred_sections


# ── SEPARATE MEASUREMENT: False Positives and False Negatives of the Grievance Gate ──
def test_grievance_gate_fp_and_fn_rates(deterministic_service):
    """
    Evaluates false positives and false negatives of the non-penal grievance gate independently.
    
    Definition:
      - Penal cases (Condition Negative): Complaint alleges a criminal offence.
      - Non-penal cases (Condition Positive): Complaint is a civil pricing dispute or figurative metaphor.
      - Gate False Positive: Gate fired on a penal case (suppressed a real crime).
      - Gate False Negative: Gate failed on a non-penal case (passed non-penal case to penal engine).
    """
    # 5 penal cases (must NOT be gated)
    penal_cases = [
        "Two men cornered me in an alley, pinned my arms against the wall, and took my wallet.",
        "A thief snatched my mobile phone while I was walking on Linking Road.",
        "My colleague took credit for my code, deleted database backup files, and embezzled company funds.",
        "The restaurant charged daylight robbery prices, and outside a thief snatched my gold chain.",
        "There was no physical injury, but he threatened to kill my brother if I did not hand over my keys."
    ]

    # 4 non-penal cases (MUST be gated)
    non_penal_cases = [
        "This restaurant is charging daylight robbery prices for dinner! 1200 for paneer!",
        "My manager stole all credit for my marketing presentation in the board meeting.",
        "उस दुकानदार ने मुझे बातों में उलझाकर मेरा बहुत सारा कीमती समय लूट लिया।",
        "The prices at this cinema are daylight robbery. A guy with a gun could not take my money faster than this popcorn counter."
    ]

    gate_false_positives = 0
    for text in penal_cases:
        if deterministic_service._detect_non_penal_grievance(text) is not None:
            gate_false_positives += 1

    gate_false_negatives = 0
    for text in non_penal_cases:
        if deterministic_service._detect_non_penal_grievance(text) is None:
            gate_false_negatives += 1

    # Exact counts and denominators
    penal_count = len(penal_cases)
    non_penal_count = len(non_penal_cases)
    fp_rate = gate_false_positives / penal_count
    fn_rate = gate_false_negatives / non_penal_count

    assert gate_false_positives == 0, f"Gate False Positives: {gate_false_positives}/{penal_count} ({fp_rate*100:.1f}%)"
    assert gate_false_negatives == 0, f"Gate False Negatives: {gate_false_negatives}/{non_penal_count} ({fn_rate*100:.1f}%)"


# ── REGRESSION TESTS: Verified Non-Penal Gate Defects (BNS-BM-40 & BNS-BM-43) ──
def test_regression_pricing_feel_cheated_bns_bm_40(deterministic_service):
    """
    Regression test for BNS-BM-40:
    Colloquial 'feel completely robbed and cheated by daylight robbery pricing policy'
    must be gated as consumer pricing and not misidentified as criminal cheating or robbery.
    """
    narrative = (
        "The supermarket charged me Rs 600 for imported mangoes which were labeled Rs 300 on the rack. "
        "I feel completely robbed and cheated by their daylight robbery pricing policy."
    )
    gate_res = deterministic_service._detect_non_penal_grievance(narrative)
    assert gate_res is not None, "Gate must catch consumer pricing with 'feel robbed and cheated'"
    assert gate_res[0] == "consumer_pricing"

    res = deterministic_service.analyze_complaint(NarrativeInput(narrative=narrative))
    assert len(res.predictions) == 0
    assert "consumer pricing dispute" in res.recommended_action.lower()


def test_regression_promotion_snatching_bns_bm_43(deterministic_service):
    """
    Regression test for BNS-BM-43:
    'snatched the promotion from under my nose' must be gated as an intangible career
    metaphor and not misidentified as physical snatching of corporeal property (BNS 304).
    """
    narrative = (
        "My colleague snatched the promotion from under my nose by taking credit for my presentation in the board meeting."
    )
    gate_res = deterministic_service._detect_non_penal_grievance(narrative)
    assert gate_res is not None, "Gate must catch figurative promotion snatching"
    assert gate_res[0] == "intangible_metaphor"

    res = deterministic_service.analyze_complaint(NarrativeInput(narrative=narrative))
    assert len(res.predictions) == 0
    assert 304 not in [p.section for p in res.predictions]
    assert "workplace" in res.recommended_action.lower() or "career" in res.recommended_action.lower()

