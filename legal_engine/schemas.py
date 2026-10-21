"""
Pydantic schemas for the BNS legal analysis engine.
Guarantees strict backward compatibility with the existing frontend
while introducing deep, grounded legal reasoning structures.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class NarrativeInput(BaseModel):
    narrative: str = Field(..., description="The user complaint narrative describing the incident.")


class FactExtractionBlock(BaseModel):
    stated_facts: List[str] = Field(
        default_factory=list,
        description="Facts explicitly stated by the complainant without inference."
    )
    inferred_facts: List[str] = Field(
        default_factory=list,
        description="Plausible inferences required to understand the narrative context."
    )
    negated_events: List[str] = Field(
        default_factory=list,
        description="Events explicitly stated NOT to have occurred (e.g., 'no weapons used', 'nobody hurt')."
    )
    missing_facts_to_clarify: List[str] = Field(
        default_factory=list,
        description="Critical missing elements required to confirm applicable legal provisions."
    )


class SectionPredictionItem(BaseModel):
    section: int = Field(..., description="Bharatiya Nyaya Sanhita (BNS), 2023 section number.")
    title: str = Field(..., description="Official statutory title of the BNS section.")
    chapter: str = Field(default="", description="Chapter under BNS, 2023.")
    score: float = Field(..., description="Relevance and legal applicability score between 0.0 and 1.0.")
    rag_score: float = Field(default=0.0, description="Normalized retrieval relevance score.")
    lr_prob: float = Field(default=0.0, description="Reserved for legacy frontend display compatibility.")
    reasoning: str = Field(..., description="Legal reasoning grounded in facts and statutory elements.")
    punishment: str = Field(default="", description="Prescribed statutory punishment clause.")
    statutory_elements_supported: List[str] = Field(
        default_factory=list,
        description="Statutory elements met by complainant's facts."
    )
    unestablished_elements: List[str] = Field(
        default_factory=list,
        description="Statutory elements that remain unproven or require further evidence."
    )
    source_citation: str = Field(
        default="Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023)",
        description="Statutory source reference."
    )
    is_cognizable: Optional[bool] = Field(
        default=None,
        description="Cognizable status under BNSS Schedule I (None if unverified)."
    )
    is_bailable: Optional[bool] = Field(
        default=None,
        description="Bailable status under BNSS Schedule I (None if unverified)."
    )


class OffenceClassificationResponse(BaseModel):
    # Backward-compatible fields expected by React frontend (src/App.jsx)
    predictions: List[SectionPredictionItem] = Field(
        default_factory=list,
        description="Ranked candidate BNS provisions."
    )
    recommended_action: str = Field(
        default="",
        description="Fact-dependent procedural advice under BNSS, 2023 (no blanket false claims)."
    )
    model: str = Field(
        default="BNS-RAG-LLM Grounded Engine v2.0",
        description="Active model and engine identifier."
    )
    standardized_narrative: str = Field(
        default="",
        description="Normalized complaint narrative after slang mapping."
    )
    translations: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Slang or colloquial translations identified."
    )

    # Enhanced structured legal intelligence
    facts_analysis: FactExtractionBlock = Field(
        default_factory=FactExtractionBlock,
        description="Detailed separation of stated facts, inferences, and missing clarifications."
    )
    statutory_disclaimer: str = Field(
        default=(
            "DISCLAIMER: This analysis provides indicative legal provisions based solely on citizen-supplied facts "
            "under the Bharatiya Nyaya Sanhita, 2023. It does not constitute a formal legal opinion or an official "
            "police charge-sheet. Procedural registration is subject to verification by the investigating officer."
        ),
        description="Statutory and regulatory legal disclaimer."
    )
    unverified_exclusions: List[int] = Field(
        default_factory=list,
        description="Section numbers excluded from consideration due to missing or unverified statutory text."
    )
    inference_status: str = Field(
        default="unspecified",
        description=(
            "How this response was produced: 'live_llm' (Gemini inference succeeded), "
            "'fallback_llm_unavailable' (Gemini not configured), 'fallback_llm_failed' (Gemini was called and "
            "failed; deterministic fallback used), 'fallback_llm_not_invoked' (Gemini available but no retrieval "
            "candidates to evaluate), 'non_penal_gate' (non-penal grievance filter; Gemini not called), or "
            "'input_too_brief'. Cached responses are distinguished by the benchmark harness, not the service."
        )
    )
