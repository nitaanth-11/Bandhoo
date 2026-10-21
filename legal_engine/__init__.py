"""
BNS Legal Engine Package
"""

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

__all__ = [
    "BNSCorpus",
    "BM25LegalRetriever",
    "GeminiLegalClient",
    "LegalAnalysisService",
    "LLMUnavailableError",
    "LLMInferenceError",
    "NarrativeInput",
    "OffenceClassificationResponse",
    "SectionPredictionItem",
    "FactExtractionBlock"
]
