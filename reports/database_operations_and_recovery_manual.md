# Bandhoo Database Operations and Disaster Recovery Manual

**Target Database:** PostgreSQL 15+ / 16+ (SQLAlchemy 2.0 ORM + Alembic Migrations)  
**Document Classification:** Internal Technical Operations Manual  
**Last Updated:** 2026-10-21  
**Status:** Approved for Production Deployment  

---

## 1. Overview and Architecture

The Bandhoo persistence architecture separates structured relational entities from binary documents and media:
1. **Relational Data (PostgreSQL):** Stores complaints, missing-person records, extracted chronological facts, source attribution spans, evidence metadata, verification decisions, generated document versions, email drafts, and append-only audit events.
2. **Controlled Private File Storage:** Stores binary evidence (audio, photos, CCTV clips, documents) and generated PDF files in a secure directory (`BANDHOO_STORAGE_DIR`) outside the web root. Files are stored atomically, indexed by unique storage keys, and cryptographically verified against SHA-256 hashes recorded in PostgreSQL.

```
                           +---------------------------+
                           |  Bandhoo Application API  |
                           +-------------+-------------+
                                         |
                 +-----------------------+-----------------------+
                 | (Relational metadata)                         | (Binary files)
                 v                                               v
    +-------------------------+                     +-------------------------+
    | PostgreSQL Database     |                     | Controlled Private      |
    | (10 relational tables)  |                     | File Storage            |
    | - complaints            |                     | (BANDHOO_STORAGE_DIR)   |
    | - missing_persons       |                     | - evidence/             |
    | - structured_facts      |                     | - documents/            |
    | - fact_source_spans     |                     | - immutable SHA-256     |
    | - evidence_files (meta) |                     +-------------------------+
    | - verification_results  |
    | - generated_documents   |
    | - document_versions     |
    | - email_drafts          |
    | - audit_events (ledger) |
    +-------------------------+
```

---

## 2. Connection Management & Pooling Safeguards

### 2.1 Configuration
Connection pooling is managed via `db/session.py` with environment variable controls:
```bash
# Connection URI (never hardcode in source code)
DATABASE_URL=postgresql://bandhoo_app:YOUR_DB_PASSWORD@127.0.0.1:5432/bandhoo_prod

# Pool sizing and recycling
DB_POOL_SIZE=10        # Number of permanent connections maintained
DB_MAX_OVERFLOW=20     # Max burst connections above pool size
DB_POOL_TIMEOUT=30     # Timeout (seconds) waiting for an available connection
DB_POOL_RECYCLE=1800   # Connection recycle lifetime (30 minutes)
```

### 2.2 Resiliency Safeguards
- **`pool_pre_ping=True`:** Emits an internal `SELECT 1` ping upon checkout, automatically detecting and discarding dead connections caused by database restarts or network resets.
- **Credential Masking:** All database errors and health checks run through `mask_db_url()`, masking passwords (`user:***@host`) to prevent credentials from ever leaking into application logs or client error responses.
- **Transaction Rollback:** All transactional units executed via `session_scope()` automatically issue `session.rollback()` on exceptions before closing connections.

---

## 3. Schema Management & Migration Runbook

All database schema evolutions are managed strictly through **Alembic**. Direct manual `ALTER TABLE` or `CREATE TABLE` commands in production are strictly prohibited.

### 3.1 Applying Migrations (Upgrade)
```bash
# Check current database revision status
python -m alembic current

# Upgrade to the latest schema revision
python -m alembic upgrade head
```

### 3.2 Rollback Procedures (Downgrade)
Every migration in `migrations/versions/` contains an idempotent `downgrade()` implementation.
```bash
# Roll back exactly one revision
python -m alembic downgrade -1

# Roll back to the original baseline schema
python -m alembic downgrade base
```
*Note: Before applying downgrades in production, a full verified snapshot backup must be executed.*

---

## 4. Backup Strategy

Bandhoo requires two complementary backup streams to achieve data durability:
1. PostgreSQL logical and physical backups.
2. Private file storage file synchronization.

### 4.1 Scheduled Automated Backups
| Backup Type | Frequency | Tool / Method | Retention Policy |
| :--- | :--- | :--- | :--- |
| **Full Logical Dump** | Daily (01:00 UTC) | `pg_dump -Fc` | 30 days daily, 12 months monthly |
| **Write-Ahead Logs (WAL)** | Continuous (< 15 min) | `pg_receivewal` / WAL-E / Barman | 7 days point-in-time recovery window |
| **Private File Storage** | Daily sync | Rclone / AWS S3 Sync with Object Lock | 30 days versioned |

### 4.2 Executing a Full Logical Backup
```bash
# Execute compressed custom-format pg_dump
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/backups/bandhoo/postgres"
mkdir -p "$BACKUP_DIR"

pg_dump -h 127.0.0.1 -U bandhoo_app -d bandhoo_prod -Fc -f "$BACKUP_DIR/bandhoo_backup_${TIMESTAMP}.dump"

# Compute SHA-256 checksum of backup artifact
sha256sum "$BACKUP_DIR/bandhoo_backup_${TIMESTAMP}.dump" > "$BACKUP_DIR/bandhoo_backup_${TIMESTAMP}.dump.sha256"

# Encrypt backup archive with GPG/AES-256
gpg --symmetric --cipher-algo AES256 "$BACKUP_DIR/bandhoo_backup_${TIMESTAMP}.dump"
```

### 4.3 Backing Up Private File Storage
```bash
STORAGE_DIR="./private_storage"
STORAGE_BACKUP_DIR="/var/backups/bandhoo/storage"
mkdir -p "$STORAGE_BACKUP_DIR"

# Archive private files with SHA-256 integrity manifest
tar -czf "$STORAGE_BACKUP_DIR/storage_backup_${TIMESTAMP}.tar.gz" -C "$STORAGE_DIR" .
sha256sum "$STORAGE_BACKUP_DIR/storage_backup_${TIMESTAMP}.tar.gz" > "$STORAGE_BACKUP_DIR/storage_backup_${TIMESTAMP}.tar.gz.sha256"
```

---

## 5. Point-in-Time Recovery (PITR) & Restore Runbook

### 5.1 Full Logical Restore Procedure
```bash
# 1. Stop application server to terminate active sessions
systemctl stop bandhoo-api

# 2. Re-create target database if recovering from corruption
dropdb -h 127.0.0.1 -U postgres bandhoo_prod
createdb -h 127.0.0.1 -U postgres -O bandhoo_app bandhoo_prod

# 3. Restore from verified compressed dump
pg_restore -h 127.0.0.1 -U bandhoo_app -d bandhoo_prod -v "$BACKUP_DIR/bandhoo_backup_${TIMESTAMP}.dump"

# 4. Verify table integrity and row counts
python -m alembic current
python -c "from db.session import check_db_health; print(check_db_health())"

# 5. Restore private storage files if required
tar -xzf "$STORAGE_BACKUP_DIR/storage_backup_${TIMESTAMP}.tar.gz" -C "$STORAGE_DIR"

# 6. Restart application server
systemctl start bandhoo-api
```

### 5.2 Point-In-Time Recovery (WAL Archiving)
To recover to an exact timestamp (e.g., prior to an accidental administrative deletion):
1. Stop PostgreSQL service.
2. Restore base physical backup to PostgreSQL data directory (`$PGDATA`).
3. Place `recovery.signal` file in `$PGDATA`.
4. Configure `postgresql.conf`:
   ```ini
   restore_command = 'cp /var/backups/bandhoo/wal_archive/%f %p'
   recovery_target_time = '2026-10-21 11:45:00 UTC'
   recovery_target_action = 'promote'
   ```
5. Start PostgreSQL service and verify logs confirm recovery target reached and promoted.

---

## 6. Disaster Recovery Metrics (RPO & RTO)

- **Recovery Point Objective (RPO):** < 15 minutes (ensured by continuous WAL archiving).
- **Recovery Time Objective (RTO):** < 30 minutes (ensured by scripted restore procedures).

---

## 7. Security, Privacy and Audit Governance

1. **Verbatim Narration Integrity:** Every complaint stores `original_sha256`. Narration text is cryptographically unalterable.
2. **Append-Only Audit Ledger:** The `audit_events` table records every lifecycle transition, evidence ingestion, revision save, and document generation with timestamps, actor IDs, and differential payloads.
3. **No PII in Application Logs:** Application endpoints log only request paths, sanitized station names, and complaint UUIDs. Personal complainant names, phone numbers, and full narrative texts are strictly prohibited from log aggregators.
4. **Controlled Private Storage Security:** `PrivateFileStorage` rejects all directory traversal attempts (`..`, absolute paths) and re-verifies SHA-256 hashes on read operations.
