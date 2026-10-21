"""
Repository persistence layer for Bandhoo complaints and audit records.
"""

import uuid
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from db.models import (
    ComplaintModel, MissingPersonModel, StructuredFactModel, FactSourceSpanModel,
    EvidenceFileModel, GeneratedDocumentModel, DocumentVersionModel, EmailDraftModel,
    AuditEventModel
)


class ComplaintRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_compiled_complaint(self, compiled_record: dict) -> ComplaintModel:
        """
        Atomically saves or updates a compiled complaint record, its facts,
        source spans, missing-person details, and audit log.
        """
        complaint_id = compiled_record.get("complaint_id") or str(uuid.uuid4())
        complaint_number = compiled_record.get("complaint_number") or f"BND-{uuid.uuid4().hex[:8].upper()}"
        
        # Check if already exists
        complaint = self.db.query(ComplaintModel).filter(ComplaintModel.id == complaint_id).first()
        is_new = complaint is None
        
        if is_new:
            complaint = ComplaintModel(id=complaint_id, complaint_number=complaint_number)
            self.db.add(complaint)

        # Populate header & core attributes
        orig = compiled_record.get("original_narration") or {}
        complaint.original_narration = orig.get("verbatim_text", "")
        complaint.original_sha256 = orig.get("sha256", "")
        complaint.clarifications = compiled_record.get("clarifications") or []
        complaint.complainant_details = compiled_record.get("complainant")
        complaint.status = compiled_record.get("review_and_routing", {}).get("route", "draft")
        complaint.review_route = compiled_record.get("review_and_routing", {}).get("route", "review_status_unavailable")
        complaint.review_reasons = compiled_record.get("review_and_routing", {}).get("reasons", [])
        
        # Jurisdiction
        j = compiled_record.get("jurisdiction_assessment") or {}
        complaint.jurisdiction_station = j.get("station")
        complaint.jurisdiction_status = j.get("status")
        complaint.jurisdiction_distance_m = j.get("distance_to_boundary_m")
        
        # Entire compiled JSON snapshot
        complaint.compiled_record = compiled_record
        complaint.workflow_version = compiled_record.get("header", {}).get("workflow_version", "complaint-compiler-1.0")
        
        # Flush to establish foreign key
        self.db.flush()

        # Missing Person details
        mp_data = compiled_record.get("missing_person_details")
        if mp_data:
            mp_record = self.db.query(MissingPersonModel).filter(MissingPersonModel.complaint_id == complaint.id).first()
            if not mp_record:
                mp_record = MissingPersonModel(complaint_id=complaint.id)
                self.db.add(mp_record)
            mp_record.full_name = mp_data.get("full_name", "")
            mp_record.alias = mp_data.get("alias")
            mp_record.age = mp_data.get("age")
            mp_record.gender = mp_data.get("gender")
            mp_record.height_cm = mp_data.get("height_cm")
            mp_record.complexion = mp_data.get("complexion")
            mp_record.identifying_marks = mp_data.get("identifying_marks")
            mp_record.clothing_last_seen = mp_data.get("clothing_last_seen")
            mp_record.last_seen_datetime = mp_data.get("last_seen_datetime")
            mp_record.last_seen_location = mp_data.get("last_seen_location")
            mp_record.relationship_to_complainant = mp_data.get("relationship_to_complainant")
            mp_record.medical_conditions = mp_data.get("medical_conditions_or_vulnerabilities")
            mp_record.urgency_level = compiled_record.get("urgency_assessment", {}).get("level", "high")

        # Clear existing facts on update for idempotence
        self.db.query(StructuredFactModel).filter(StructuredFactModel.complaint_id == complaint.id).delete()
        self.db.flush()

        # Add Facts & Source Spans
        for raw_fact in compiled_record.get("all_extracted_facts") or []:
            fact_id = str(uuid.uuid4())
            fact_item = StructuredFactModel(
                id=fact_id,
                complaint_id=complaint.id,
                item_key=raw_fact.get("item_id"),
                kind=raw_fact.get("kind", "other"),
                value=raw_fact.get("value", ""),
                normalized_value=raw_fact.get("normalized"),
                polarity=raw_fact.get("polarity", "asserted"),
                provenance=raw_fact.get("provenance", "complainant_statement"),
                verification_status=raw_fact.get("verification_status", "unverified"),
                display_category=raw_fact.get("display_category"),
                extraction_method=raw_fact.get("extraction_method"),
                note=raw_fact.get("note", "")
            )
            self.db.add(fact_item)
            self.db.flush()

            for s in raw_fact.get("spans") or []:
                span = FactSourceSpanModel(
                    fact_id=fact_item.id,
                    statement_id=s.get("statement_id", "S1"),
                    start_char=s.get("start", 0),
                    end_char=s.get("end", 0),
                    quote=s.get("quote", "")
                )
                self.db.add(span)

        # Audit Event
        audit = AuditEventModel(
            complaint_id=complaint.id,
            entity_type="complaint",
            entity_id=complaint.id,
            action="complaint_compiled_and_persisted" if is_new else "complaint_revision_saved",
            actor_type="system_engine",
            actor_id="bandhoo_compiler_v1",
            payload_after={"status": complaint.status, "facts_count": len(compiled_record.get("all_extracted_facts") or [])}
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(complaint)
        return complaint

    def get_complaint(self, complaint_id_or_number: str) -> Optional[ComplaintModel]:
        return self.db.query(ComplaintModel).filter(
            (ComplaintModel.id == complaint_id_or_number) |
            (ComplaintModel.complaint_number == complaint_id_or_number)
        ).first()

    def record_document_version(
        self,
        complaint_id: str,
        document_type: str,
        title: str,
        storage_key: str,
        file_size_bytes: int,
        sha256_hash: str,
        metadata_snapshot: Optional[dict] = None
    ) -> DocumentVersionModel:
        """Stores metadata for a generated PDF document without storing raw binary in DB."""
        doc = self.db.query(GeneratedDocumentModel).filter(
            GeneratedDocumentModel.complaint_id == complaint_id,
            GeneratedDocumentModel.document_type == document_type
        ).first()

        if not doc:
            doc = GeneratedDocumentModel(
                complaint_id=complaint_id,
                document_type=document_type,
                title=title
            )
            self.db.add(doc)
            self.db.flush()

        existing_versions = self.db.query(DocumentVersionModel).filter(
            DocumentVersionModel.document_id == doc.id
        ).count()

        version = DocumentVersionModel(
            document_id=doc.id,
            version_number=existing_versions + 1,
            file_size_bytes=file_size_bytes,
            sha256_hash=sha256_hash,
            storage_key=storage_key,
            metadata_snapshot=metadata_snapshot
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def save_email_draft(
        self,
        complaint_id: str,
        recipient_email: str,
        subject: str,
        body_text: str,
        attached_version_id: Optional[str] = None
    ) -> EmailDraftModel:
        """Stores a prepared email draft awaiting user confirmation."""
        draft = EmailDraftModel(
            complaint_id=complaint_id,
            recipient_email=recipient_email,
            subject=subject,
            body_text=body_text,
            attached_version_id=attached_version_id,
            status="draft_pending_user_confirmation",
            user_confirmed=False
        )
        self.db.add(draft)
        self.db.commit()
        self.db.refresh(draft)
        return draft

    def record_evidence_file(
        self,
        complaint_id: str,
        evidence_type: str,
        file_name: str,
        file_size_bytes: int,
        mime_type: str,
        sha256_hash: str,
        storage_key: str,
        description: Optional[str] = None
    ) -> EvidenceFileModel:
        """Stores evidence file metadata and private storage key."""
        evidence = EvidenceFileModel(
            complaint_id=complaint_id,
            evidence_type=evidence_type,
            description=description,
            file_name=file_name,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            sha256_hash=sha256_hash,
            storage_key=storage_key,
            custody_status="supplied_not_examined",
            authenticity_status="not_assessed",
            verification_status="unverified"
        )
        self.db.add(evidence)
        
        audit = AuditEventModel(
            complaint_id=complaint_id,
            entity_type="evidence_file",
            entity_id=evidence.id,
            action="evidence_file_uploaded_and_stored",
            actor_type="user_or_system",
            actor_id="bandhoo_evidence_ingest",
            payload_after={"storage_key": storage_key, "sha256": sha256_hash, "file_name": file_name}
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def get_audit_events(self, complaint_id: str) -> List[AuditEventModel]:
        """Retrieves append-only audit trail for a complaint."""
        return self.db.query(AuditEventModel).filter(
            AuditEventModel.complaint_id == complaint_id
        ).order_by(AuditEventModel.event_timestamp.asc()).all()

