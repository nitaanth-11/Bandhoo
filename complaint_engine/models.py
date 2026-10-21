"""
Typed records for the complaint-structuring workflow.

Design rules enforced here and in the graph's validation node:
- A complainant statement is immutable once received (frozen model, SHA-256 recorded).
- Every fact derived from a statement cites at least one exact source span.
- Provenance (where an item came from) and verification status (whether anyone checked it)
  are separate fields. Only an accepted police verification event can make an item
  "independently verified"; supplying a file never does.
"""

import hashlib
from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Statement(BaseModel):
    """A complainant statement, stored verbatim and never edited."""
    model_config = ConfigDict(frozen=True)

    statement_id: str
    kind: Literal["original", "clarification"]
    text: str
    received_at: str
    sha256: str

    @classmethod
    def create(cls, statement_id: str, kind: str, text: str) -> "Statement":
        return cls(statement_id=statement_id, kind=kind, text=text, received_at=utc_now(), sha256=sha256_text(text))


class SourceSpan(BaseModel):
    model_config = ConfigDict(frozen=True)

    statement_id: str
    start: int
    end: int
    quote: str


FactKind = Literal[
    "event_statement", "datetime", "location", "person", "amount", "phone", "vehicle", "alleged_action", "property",
    "injury", "weapon", "witness_reference", "evidence_reference", "denial", "other",
]
Provenance = Literal["complainant_statement", "ai_inference"]
VerificationStatus = Literal["unverified", "independently_verified", "verification_inconsistent", "could_not_verify"]
Polarity = Literal["asserted", "explicitly_denied", "uncertain"]


class FactItem(BaseModel):
    item_id: str
    kind: FactKind
    value: str
    spans: List[SourceSpan] = Field(default_factory=list)
    provenance: Provenance = "complainant_statement"
    verification_status: VerificationStatus = "unverified"
    polarity: Polarity = "asserted"
    extraction_method: str
    # Derived, machine-normalised value used only for comparisons (e.g. "2026-10-14", "21:30").
    normalized: Optional[str] = None
    note: str = ""
    display_category: str = ""


class RejectedItem(BaseModel):
    """An extractor output that could not be grounded in the complainant's words."""
    proposed: str
    reason: str
    source: str


class EvidenceItem(BaseModel):
    """Supplied material (metadata only). Supplying it proves nothing about authenticity."""
    evidence_id: str
    evidence_type: str
    description: str = ""
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    sha256: Optional[str] = None
    custody_status: Literal["supplied_not_examined", "examined_by_police"] = "supplied_not_examined"
    authenticity_status: Literal["not_assessed", "assessed_by_police"] = "not_assessed"
    verification_status: VerificationStatus = "unverified"
    linked_item_ids: List[str] = Field(default_factory=list)


class VerificationEvent(BaseModel):
    """
    A verification recorded by an authorised police officer. The public API never accepts these:
    there is no authentication system yet, so they can only be passed in by trusted server code.
    """
    model_config = ConfigDict(frozen=True)

    event_id: str
    target_id: str
    verifier_id: str
    verifier_role: str
    authorization_reference: str
    method: str
    result: Literal["consistent", "inconsistent", "could_not_verify"]
    recorded_at: str


class MissingInfo(BaseModel):
    field: str
    why_needed: str
    # not_determined: the extractor could not read this from the statement (e.g. limited language support);
    # the statement may contain it, so it is not reported as missing.
    status: Literal["open", "explicitly_denied", "unknown_to_complainant", "not_determined"] = "open"
    source_spans: List[SourceSpan] = Field(default_factory=list)


class Contradiction(BaseModel):
    contradiction_id: str
    field: str
    summary: str
    spans: List[SourceSpan]
    status: Literal["open"] = "open"
    detector: str


class JurisdictionAssessment(BaseModel):
    status: Literal["inside", "near_boundary", "outside_all", "multiple", "no_location", "data_unavailable"]
    station: Optional[str] = None
    distance_to_boundary_m: Optional[float] = None
    method: str = "polygon_containment"
    message: str = ""
    boundary_data: dict = Field(default_factory=dict)


class NodeError(BaseModel):
    node: str
    error_type: str
    message: str


class LogEntry(BaseModel):
    node: str
    event: str
    at: str = Field(default_factory=utc_now)


class ReviewDecision(BaseModel):
    # review_status_unavailable: the routing step failed or gave no valid decision; human review is required.
    route: Literal["human_review_required", "ready_for_police_review", "review_status_unavailable"]
    reasons: List[str] = Field(default_factory=list)
    validation_passed: bool


# ── API input models (extra fields forbidden so callers cannot inject verification events) ──

class LocationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    latitude: float
    longitude: float
    source: Literal["map_pin", "device_gps", "unknown"] = "unknown"
    accuracy_m: Optional[float] = None


class EvidenceMetadataInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evidence_type: str
    description: str = ""
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    sha256: Optional[str] = None


class ComplaintStructureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    statement: str = Field(..., description="The complainant's original account, verbatim.")
    clarifications: List[str] = Field(default_factory=list, description="Later clarifications, verbatim, in order.")
    evidence: List[EvidenceMetadataInput] = Field(default_factory=list)
    location: Optional[LocationInput] = None
