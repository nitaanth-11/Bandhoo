"""
SQLAlchemy 2.0 ORM Models for Bandhoo Persistent Storage.

Implements all entities specified in K1 / Phase 3:
- Complaints & revisions
- Missing-person reports
- Structured facts & source spans
- Evidence files (metadata + private storage keys)
- Official verification results
- Generated PDF documents and versions
- Email drafts and delivery status
- Audit events (append-only ledger)
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, Float, BigInteger, Boolean, DateTime,
    ForeignKey, JSON
)
from sqlalchemy.orm import relationship

from db.session import Base


def utc_now():
    return datetime.now(timezone.utc)


def generate_uuid():
    return str(uuid.uuid4())


class ComplaintModel(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_number = Column(String(64), unique=True, index=True, nullable=False)
    status = Column(String(32), default="draft", index=True, nullable=False)
    original_narration = Column(Text, nullable=False)
    original_sha256 = Column(String(64), nullable=False)
    clarifications = Column(JSON, default=list)
    complainant_details = Column(JSON, nullable=True)
    
    incident_datetime_raw = Column(String(255), nullable=True)
    incident_datetime_normalized = Column(DateTime, nullable=True)
    incident_location_raw = Column(String(512), nullable=True)
    incident_latitude = Column(Float, nullable=True)
    incident_longitude = Column(Float, nullable=True)
    
    jurisdiction_station = Column(String(128), nullable=True, index=True)
    jurisdiction_status = Column(String(32), nullable=True)
    jurisdiction_distance_m = Column(Float, nullable=True)
    
    review_route = Column(String(64), default="review_status_unavailable", index=True)
    review_reasons = Column(JSON, default=list)
    compiled_record = Column(JSON, nullable=True)
    workflow_version = Column(String(64), default="complaint-compiler-1.0")
    
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    missing_person = relationship("MissingPersonModel", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
    facts = relationship("StructuredFactModel", back_populates="complaint", cascade="all, delete-orphan")
    evidence_files = relationship("EvidenceFileModel", back_populates="complaint", cascade="all, delete-orphan")
    verifications = relationship("VerificationResultModel", back_populates="complaint", cascade="all, delete-orphan")
    documents = relationship("GeneratedDocumentModel", back_populates="complaint", cascade="all, delete-orphan")
    email_drafts = relationship("EmailDraftModel", back_populates="complaint", cascade="all, delete-orphan")
    audit_events = relationship("AuditEventModel", back_populates="complaint", cascade="all, delete-orphan")


class MissingPersonModel(Base):
    __tablename__ = "missing_person_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_id = Column(String(36), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=False, index=True)
    alias = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(32), nullable=True)
    height_cm = Column(Float, nullable=True)
    complexion = Column(String(64), nullable=True)
    identifying_marks = Column(Text, nullable=True)
    clothing_last_seen = Column(Text, nullable=True)
    last_seen_datetime = Column(String(255), nullable=True)
    last_seen_location = Column(String(512), nullable=True)
    relationship_to_complainant = Column(String(128), nullable=True)
    medical_conditions = Column(Text, nullable=True)
    urgency_level = Column(String(32), default="high", nullable=False)
    status = Column(String(32), default="reported", nullable=False)
    
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    complaint = relationship("ComplaintModel", back_populates="missing_person")


class StructuredFactModel(Base):
    __tablename__ = "structured_facts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_id = Column(String(36), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    item_key = Column(String(64), nullable=True)
    kind = Column(String(64), nullable=False, index=True)
    value = Column(Text, nullable=False)
    normalized_value = Column(Text, nullable=True)
    polarity = Column(String(32), default="asserted", nullable=False)
    provenance = Column(String(32), default="complainant_statement", nullable=False)
    verification_status = Column(String(32), default="unverified", nullable=False)
    display_category = Column(String(128), nullable=True)
    extraction_method = Column(String(64), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    complaint = relationship("ComplaintModel", back_populates="facts")
    spans = relationship("FactSourceSpanModel", back_populates="fact", cascade="all, delete-orphan")


class FactSourceSpanModel(Base):
    __tablename__ = "fact_source_spans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    fact_id = Column(String(36), ForeignKey("structured_facts.id", ondelete="CASCADE"), nullable=False, index=True)
    statement_id = Column(String(32), nullable=False)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    quote = Column(Text, nullable=False)

    fact = relationship("StructuredFactModel", back_populates="spans")


class EvidenceFileModel(Base):
    __tablename__ = "evidence_files"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_id = Column(String(36), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String(128), nullable=False)
    sha256_hash = Column(String(64), nullable=False, index=True)
    storage_backend = Column(String(32), default="local_private", nullable=False)
    storage_key = Column(String(512), nullable=False, unique=True)
    custody_status = Column(String(32), default="supplied_not_examined", nullable=False)
    authenticity_status = Column(String(32), default="not_assessed", nullable=False)
    verification_status = Column(String(32), default="unverified", nullable=False)
    uploaded_at = Column(DateTime, default=utc_now, nullable=False)

    complaint = relationship("ComplaintModel", back_populates="evidence_files")


class VerificationResultModel(Base):
    __tablename__ = "verification_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_id = Column(String(36), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type = Column(String(32), nullable=False)
    target_id = Column(String(36), nullable=False)
    verifier_id = Column(String(128), nullable=False)
    verifier_role = Column(String(64), nullable=False)
    authorization_reference = Column(String(255), nullable=False)
    method = Column(String(128), nullable=False)
    result = Column(String(32), nullable=False)
    remarks = Column(Text, nullable=True)
    recorded_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    complaint = relationship("ComplaintModel", back_populates="verifications")


class GeneratedDocumentModel(Base):
    __tablename__ = "generated_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_id = Column(String(36), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type = Column(String(64), nullable=False)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    complaint = relationship("ComplaintModel", back_populates="documents")
    versions = relationship("DocumentVersionModel", back_populates="document", cascade="all, delete-orphan")


class DocumentVersionModel(Base):
    __tablename__ = "document_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("generated_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, default=1, nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    storage_backend = Column(String(32), default="local_private", nullable=False)
    storage_key = Column(String(512), nullable=False, unique=True)
    template_version = Column(String(64), default="pdf-template-1.0")
    metadata_snapshot = Column(JSON, nullable=True)
    generated_at = Column(DateTime, default=utc_now, nullable=False)

    document = relationship("GeneratedDocumentModel", back_populates="versions")


class EmailDraftModel(Base):
    __tablename__ = "email_drafts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_id = Column(String(36), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_email = Column(String(255), nullable=False)
    recipient_name = Column(String(255), nullable=True)
    recipient_type = Column(String(32), default="complainant", nullable=False)
    subject = Column(String(512), nullable=False)
    body_text = Column(Text, nullable=False)
    body_html = Column(Text, nullable=True)
    status = Column(String(32), default="draft_pending_user_confirmation", nullable=False)
    user_confirmed = Column(Boolean, default=False, nullable=False)
    attached_version_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    complaint = relationship("ComplaintModel", back_populates="email_drafts")


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_id = Column(String(36), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=True, index=True)
    entity_type = Column(String(64), nullable=False, index=True)
    entity_id = Column(String(36), nullable=True, index=True)
    action = Column(String(64), nullable=False, index=True)
    actor_type = Column(String(32), default="system_engine", nullable=False)
    actor_id = Column(String(128), default="bandhoo_workflow", nullable=False)
    event_timestamp = Column(DateTime, default=utc_now, nullable=False)
    payload_before = Column(JSON, nullable=True)
    payload_after = Column(JSON, nullable=True)

    complaint = relationship("ComplaintModel", back_populates="audit_events")
