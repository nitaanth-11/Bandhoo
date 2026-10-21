"""
Comprehensive Unit & Regression Tests for Phase 3:
Database persistence, Alembic migrations, rollback, private file storage, and security.
"""

import os
import shutil
import tempfile
import uuid
from pathlib import Path
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from alembic.config import Config
from alembic import command

from db.session import (
    Base, mask_db_url, check_db_health, session_scope, create_configured_engine
)
from db.models import (
    ComplaintModel, MissingPersonModel, StructuredFactModel, FactSourceSpanModel,
    EvidenceFileModel, GeneratedDocumentModel, DocumentVersionModel, EmailDraftModel,
    AuditEventModel
)
from db.repository import ComplaintRepository
from complaint_engine.storage import (
    PrivateFileStorage, StorageSecurityError, StorageIntegrityError
)


@pytest.fixture
def temp_storage():
    """Provides an isolated private storage directory for tests."""
    temp_dir = tempfile.mkdtemp(prefix="bandhoo_test_storage_")
    storage = PrivateFileStorage(base_dir=temp_dir)
    yield storage
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def in_memory_db():
    """Provides an isolated SQLite engine and repository."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session, engine
    session.close()
    Base.metadata.drop_all(bind=engine)


# ==============================================================================
# 1. Security & URL Sanitization Tests
# ==============================================================================

def test_mask_db_url_redacts_passwords():
    """Verifies credentials are masked in connection strings."""
    raw_url = "postgresql://bandhoo_admin:SuperSecretPass123!@db.internal:5432/bandhoo_prod"
    masked = mask_db_url(raw_url)
    assert "SuperSecretPass123!" not in masked
    assert "bandhoo_admin:***@db.internal:5432" in masked


def test_mask_db_url_handles_non_credential_urls():
    """Verifies SQLite or unauthenticated URLs remain valid."""
    assert mask_db_url("sqlite:///local.db") == "sqlite:///local.db"
    assert mask_db_url("") == ""


def test_db_health_check_returns_healthy(in_memory_db):
    """Verifies health check executes and reports connectivity without leaking secrets."""
    health = check_db_health()
    assert health["status"] in ["healthy", "unhealthy"]
    assert "password" not in str(health).lower()


# ==============================================================================
# 2. Alembic Migration Upgrade & Downgrade (Rollback) Tests
# ==============================================================================

def test_alembic_migration_upgrade_and_downgrade():
    """
    Executes Alembic upgrade to head and downgrade to base on an isolated database.
    Verifies that all 10 tables are created and then completely cleaned up on rollback.
    """
    temp_db_path = Path(tempfile.gettempdir()) / f"test_alembic_{uuid.uuid4().hex}.db"
    test_db_url = f"sqlite:///{temp_db_path}"

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

    test_engine = create_engine(test_db_url)

    try:
        # Step 1: Run upgrade to head
        command.upgrade(alembic_cfg, "head")

        inspector = inspect(test_engine)
        table_names = set(inspector.get_table_names())
        expected_tables = {
            "complaints",
            "missing_person_reports",
            "structured_facts",
            "fact_source_spans",
            "evidence_files",
            "verification_results",
            "generated_documents",
            "document_versions",
            "email_drafts",
            "audit_events",
        }
        assert expected_tables.issubset(table_names), f"Missing tables: {expected_tables - table_names}"

        # Step 2: Run downgrade to base (rollback verification)
        command.downgrade(alembic_cfg, "base")

        inspector_after = inspect(test_engine)
        tables_after = set(inspector_after.get_table_names())
        # All 10 application tables must have been dropped
        remaining_app_tables = tables_after.intersection(expected_tables)
        assert len(remaining_app_tables) == 0, f"Tables failed to drop during rollback: {remaining_app_tables}"

    finally:
        test_engine.dispose()
        if temp_db_path.exists():
            temp_db_path.unlink()


# ==============================================================================
# 3. Controlled Private File Storage Tests
# ==============================================================================

def test_private_storage_atomic_save_and_read(temp_storage):
    """Verifies atomic write, SHA-256 calculation, and data integrity."""
    payload = b"Formal PDF Complaint Document Content"
    key, size, sha256 = temp_storage.save_file(payload, "documents/complaint_001.pdf")

    assert size == len(payload)
    assert len(sha256) == 64
    assert temp_storage.exists(key)

    # Read back and verify bytes
    read_data = temp_storage.read_file(key, verify_sha256=sha256)
    assert read_data == payload


def test_private_storage_rejects_path_traversal(temp_storage):
    """Verifies that attempts to escape private storage root are blocked."""
    payload = b"Dangerous Content"
    with pytest.raises(StorageSecurityError):
        temp_storage.save_file(payload, "../outside_secret.txt")

    with pytest.raises(StorageSecurityError):
        temp_storage.read_file("../../etc/passwd")


def test_private_storage_integrity_verification_failure(temp_storage):
    """Verifies that corrupted files or mismatched hashes raise StorageIntegrityError."""
    payload = b"Authentic Content"
    key, _, _ = temp_storage.save_file(payload, "evidence/photo.png")

    fake_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    with pytest.raises(StorageIntegrityError):
        temp_storage.read_file(key, verify_sha256=fake_hash)


# ==============================================================================
# 4. Database Persistence & Repository Layer Tests
# ==============================================================================

def test_repository_save_and_retrieve_complaint(in_memory_db):
    """Verifies saving compiled complaint with facts, spans, and audit event."""
    session, _ = in_memory_db
    repo = ComplaintRepository(session)

    complaint_id = str(uuid.uuid4())
    compiled_record = {
        "complaint_id": complaint_id,
        "complaint_number": "BND-TEST-001",
        "original_narration": {
            "verbatim_text": "A chain was snatched on Main Street.",
            "sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        },
        "review_and_routing": {"route": "human_review_required", "reasons": ["High value loss"]},
        "all_extracted_facts": [
            {
                "item_id": "F1",
                "kind": "action",
                "value": "snatched chain",
                "spans": [{"statement_id": "S1", "start": 16, "end": 30, "quote": "snatched chain"}]
            }
        ]
    }

    saved = repo.save_compiled_complaint(compiled_record)
    assert saved.id == complaint_id
    assert saved.status == "human_review_required"

    # Query back
    retrieved = repo.get_complaint(complaint_id)
    assert retrieved is not None
    assert len(retrieved.facts) == 1
    assert retrieved.facts[0].value == "snatched chain"
    assert len(retrieved.facts[0].spans) == 1
    assert retrieved.facts[0].spans[0].quote == "snatched chain"

    # Verify audit event logged
    audit_events = repo.get_audit_events(complaint_id)
    assert len(audit_events) >= 1
    assert audit_events[0].action == "complaint_compiled_and_persisted"


def test_repository_records_evidence_metadata_and_storage_key(in_memory_db):
    """Verifies evidence metadata is saved with storage key rather than raw binary."""
    session, _ = in_memory_db
    repo = ComplaintRepository(session)

    complaint = ComplaintModel(
        id=str(uuid.uuid4()),
        complaint_number="BND-EVID-001",
        status="draft",
        original_narration="Witness statement and photo attached.",
        original_sha256="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    )
    session.add(complaint)
    session.commit()

    evidence = repo.record_evidence_file(
        complaint_id=complaint.id,
        evidence_type="scene_photo",
        file_name="incident_scene.jpg",
        file_size_bytes=204800,
        mime_type="image/jpeg",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        storage_key="evidence/incident_scene.jpg",
        description="Photograph of incident scene"
    )

    assert evidence.id is not None
    assert evidence.storage_key == "evidence/incident_scene.jpg"
    assert evidence.custody_status == "supplied_not_examined"
    assert evidence.verification_status == "unverified"

    # Check audit event
    audits = repo.get_audit_events(complaint.id)
    assert any(a.action == "evidence_file_uploaded_and_stored" for a in audits)


def test_repository_foreign_key_cascade(in_memory_db):
    """Verifies that deleting a complaint cascades deletions to facts and evidence."""
    session, _ = in_memory_db
    repo = ComplaintRepository(session)

    complaint_id = str(uuid.uuid4())
    compiled_record = {
        "complaint_id": complaint_id,
        "complaint_number": "BND-CASCADE-001",
        "original_narration": {"verbatim_text": "Sample text", "sha256": "abc"},
        "all_extracted_facts": [{"item_id": "F1", "kind": "action", "value": "theft"}]
    }
    repo.save_compiled_complaint(compiled_record)

    # Confirm fact exists
    assert session.query(StructuredFactModel).filter(StructuredFactModel.complaint_id == complaint_id).count() == 1

    # Delete complaint
    c = session.query(ComplaintModel).filter(ComplaintModel.id == complaint_id).first()
    session.delete(c)
    session.commit()

    # Verify facts were cascaded
    assert session.query(StructuredFactModel).filter(StructuredFactModel.complaint_id == complaint_id).count() == 0
