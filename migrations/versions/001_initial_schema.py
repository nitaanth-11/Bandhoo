"""initial schema for complaints, missing persons, facts, evidence, documents, emails, and audit

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-21 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. complaints table
    op.create_table(
        'complaints',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('complaint_number', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('original_narration', sa.Text(), nullable=False),
        sa.Column('original_sha256', sa.String(length=64), nullable=False),
        sa.Column('clarifications', sa.JSON(), nullable=True),
        sa.Column('complainant_details', sa.JSON(), nullable=True),
        sa.Column('incident_datetime_raw', sa.String(length=255), nullable=True),
        sa.Column('incident_datetime_normalized', sa.DateTime(), nullable=True),
        sa.Column('incident_location_raw', sa.String(length=512), nullable=True),
        sa.Column('incident_latitude', sa.Float(), nullable=True),
        sa.Column('incident_longitude', sa.Float(), nullable=True),
        sa.Column('jurisdiction_station', sa.String(length=128), nullable=True),
        sa.Column('jurisdiction_status', sa.String(length=32), nullable=True),
        sa.Column('jurisdiction_distance_m', sa.Float(), nullable=True),
        sa.Column('review_route', sa.String(length=64), nullable=False, server_default='review_status_unavailable'),
        sa.Column('review_reasons', sa.JSON(), nullable=True),
        sa.Column('compiled_record', sa.JSON(), nullable=True),
        sa.Column('workflow_version', sa.String(length=64), nullable=False, server_default='complaint-compiler-1.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaints_complaint_number'), 'complaints', ['complaint_number'], unique=True)
    op.create_index(op.f('ix_complaints_jurisdiction_station'), 'complaints', ['jurisdiction_station'], unique=False)
    op.create_index(op.f('ix_complaints_review_route'), 'complaints', ['review_route'], unique=False)
    op.create_index(op.f('ix_complaints_status'), 'complaints', ['status'], unique=False)

    # 2. missing_person_reports table
    op.create_table(
        'missing_person_reports',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('complaint_id', sa.String(length=36), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('alias', sa.String(length=255), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=32), nullable=True),
        sa.Column('height_cm', sa.Float(), nullable=True),
        sa.Column('complexion', sa.String(length=64), nullable=True),
        sa.Column('identifying_marks', sa.Text(), nullable=True),
        sa.Column('clothing_last_seen', sa.Text(), nullable=True),
        sa.Column('last_seen_datetime', sa.String(length=255), nullable=True),
        sa.Column('last_seen_location', sa.String(length=512), nullable=True),
        sa.Column('relationship_to_complainant', sa.String(length=128), nullable=True),
        sa.Column('medical_conditions', sa.Text(), nullable=True),
        sa.Column('urgency_level', sa.String(length=32), nullable=False, server_default='high'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='reported'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('complaint_id')
    )
    op.create_index(op.f('ix_missing_person_reports_complaint_id'), 'missing_person_reports', ['complaint_id'], unique=True)
    op.create_index(op.f('ix_missing_person_reports_full_name'), 'missing_person_reports', ['full_name'], unique=False)

    # 3. structured_facts table
    op.create_table(
        'structured_facts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('complaint_id', sa.String(length=36), nullable=False),
        sa.Column('item_key', sa.String(length=64), nullable=True),
        sa.Column('kind', sa.String(length=64), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('normalized_value', sa.Text(), nullable=True),
        sa.Column('polarity', sa.String(length=32), nullable=False, server_default='asserted'),
        sa.Column('provenance', sa.String(length=32), nullable=False, server_default='complainant_statement'),
        sa.Column('verification_status', sa.String(length=32), nullable=False, server_default='unverified'),
        sa.Column('display_category', sa.String(length=128), nullable=True),
        sa.Column('extraction_method', sa.String(length=64), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_structured_facts_complaint_id'), 'structured_facts', ['complaint_id'], unique=False)
    op.create_index(op.f('ix_structured_facts_kind'), 'structured_facts', ['kind'], unique=False)

    # 4. fact_source_spans table
    op.create_table(
        'fact_source_spans',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('fact_id', sa.String(length=36), nullable=False),
        sa.Column('statement_id', sa.String(length=32), nullable=False),
        sa.Column('start_char', sa.Integer(), nullable=False),
        sa.Column('end_char', sa.Integer(), nullable=False),
        sa.Column('quote', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['fact_id'], ['structured_facts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fact_source_spans_fact_id'), 'fact_source_spans', ['fact_id'], unique=False)

    # 5. evidence_files table
    op.create_table(
        'evidence_files',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('complaint_id', sa.String(length=36), nullable=False),
        sa.Column('evidence_type', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('mime_type', sa.String(length=128), nullable=False),
        sa.Column('sha256_hash', sa.String(length=64), nullable=False),
        sa.Column('storage_backend', sa.String(length=32), nullable=False, server_default='local_private'),
        sa.Column('storage_key', sa.String(length=512), nullable=False),
        sa.Column('custody_status', sa.String(length=32), nullable=False, server_default='supplied_not_examined'),
        sa.Column('authenticity_status', sa.String(length=32), nullable=False, server_default='not_assessed'),
        sa.Column('verification_status', sa.String(length=32), nullable=False, server_default='unverified'),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('storage_key')
    )
    op.create_index(op.f('ix_evidence_files_complaint_id'), 'evidence_files', ['complaint_id'], unique=False)
    op.create_index(op.f('ix_evidence_files_sha256_hash'), 'evidence_files', ['sha256_hash'], unique=False)

    # 6. verification_results table
    op.create_table(
        'verification_results',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('complaint_id', sa.String(length=36), nullable=False),
        sa.Column('target_type', sa.String(length=32), nullable=False),
        sa.Column('target_id', sa.String(length=36), nullable=False),
        sa.Column('verifier_id', sa.String(length=128), nullable=False),
        sa.Column('verifier_role', sa.String(length=64), nullable=False),
        sa.Column('authorization_reference', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=128), nullable=False),
        sa.Column('result', sa.String(length=32), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verification_results_complaint_id'), 'verification_results', ['complaint_id'], unique=False)

    # 7. generated_documents table
    op.create_table(
        'generated_documents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('complaint_id', sa.String(length=36), nullable=False),
        sa.Column('document_type', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_generated_documents_complaint_id'), 'generated_documents', ['complaint_id'], unique=False)

    # 8. document_versions table
    op.create_table(
        'document_versions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('sha256_hash', sa.String(length=64), nullable=False),
        sa.Column('storage_backend', sa.String(length=32), nullable=False, server_default='local_private'),
        sa.Column('storage_key', sa.String(length=512), nullable=False),
        sa.Column('template_version', sa.String(length=64), nullable=False, server_default='pdf-template-1.0'),
        sa.Column('metadata_snapshot', sa.JSON(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['generated_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('storage_key')
    )
    op.create_index(op.f('ix_document_versions_document_id'), 'document_versions', ['document_id'], unique=False)

    # 9. email_drafts table
    op.create_table(
        'email_drafts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('complaint_id', sa.String(length=36), nullable=False),
        sa.Column('recipient_email', sa.String(length=255), nullable=False),
        sa.Column('recipient_name', sa.String(length=255), nullable=True),
        sa.Column('recipient_type', sa.String(length=32), nullable=False, server_default='complainant'),
        sa.Column('subject', sa.String(length=512), nullable=False),
        sa.Column('body_text', sa.Text(), nullable=False),
        sa.Column('body_html', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft_pending_user_confirmation'),
        sa.Column('user_confirmed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('attached_version_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_drafts_complaint_id'), 'email_drafts', ['complaint_id'], unique=False)

    # 10. audit_events table
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('complaint_id', sa.String(length=36), nullable=True),
        sa.Column('entity_type', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=True),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('actor_type', sa.String(length=32), nullable=False, server_default='system_engine'),
        sa.Column('actor_id', sa.String(length=128), nullable=False, server_default='bandhoo_workflow'),
        sa.Column('event_timestamp', sa.DateTime(), nullable=False),
        sa.Column('payload_before', sa.JSON(), nullable=True),
        sa.Column('payload_after', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_events_action'), 'audit_events', ['action'], unique=False)
    op.create_index(op.f('ix_audit_events_complaint_id'), 'audit_events', ['complaint_id'], unique=False)
    op.create_index(op.f('ix_audit_events_entity_id'), 'audit_events', ['entity_id'], unique=False)
    op.create_index(op.f('ix_audit_events_entity_type'), 'audit_events', ['entity_type'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table('audit_events')
    op.drop_table('email_drafts')
    op.drop_table('document_versions')
    op.drop_table('generated_documents')
    op.drop_table('verification_results')
    op.drop_table('evidence_files')
    op.drop_table('fact_source_spans')
    op.drop_table('structured_facts')
    op.drop_table('missing_person_reports')
    op.drop_table('complaints')
