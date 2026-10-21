# Bandhoo Controlled Baseline Refresh & Rollback Validation Report

**Record Identifier:** BR-2026-10-21-01  
**Date:** 2026-10-21  
**Author:** Antigravity / Engineering  
**Scope:** Controlled reconciliation of the production baseline checksum register following deterministic defect fixes (Checkpoint 2) and security/privacy hardening (Checkpoint 5).  
**Status:** VALIDATED & RECONCILED.

---

## 1. Executive Summary

This report establishes the refreshed production baseline for the BNS Prediction Engine ("Bandhoo").

Under the non-negotiable principles established in the release blocker register (`reports/release_blocker_register.md`), production checksums were held strictly immutable until authorized controlled baseline reconciliation. With the successful completion of deterministic defect remediation (Checkpoint 2), the establishment of the independent evaluation protocol (Checkpoint 3), the compilation of the legal/jurisdiction review dossier (Checkpoint 4), and the completion of security and privacy hardening (Checkpoint 5), the baseline hash register (Appendix B) has been formally reconciled.

### Key Validation Outcomes:
1. **Full Test Suite:** 356 of 356 automated tests passing (100% pass rate) across all 15 test modules.
2. **Deterministic Fallback Legal Benchmark:** 50 of 50 cases evaluated, reproducing baseline metrics exactly (Micro Precision: 18.70%, Recall: 56.25%, Macro Precision: 29.61%, Macro Recall: 67.17%). Zero label modifications.
3. **Complaint Structuring Benchmark:** 34 of 34 cases evaluated, 0 integrity violations, 0 unsafe jurisdiction assignments, 100% missing field accuracy.
4. **Frontend Unit & Static Analysis:** 23 of 23 Node test runner unit tests passing; ESLint static analysis clean with 0 errors and 0 warnings.
5. **Blocker Integrity:** All substantive legal, external review, and source verification blockers (RB-01 through RB-53) remain explicitly **OPEN**. No blocker is prematurely marked resolved.

---

## 2. Checksum Reconciliations & Provenance

### 2.1 Core Production File Hash Transition (`main.py`)
`main.py` is the only file from the original 17 baseline files whose hash changed. Its modification history has full provenance:

| Milestone | Git Commit / Stage | SHA-256 (first 16 hex chars) | Full SHA-256 (LF normalized) | Modifications |
|---|---|---|---|---|
| **Original Baseline** | `1ad5bb6` (2026-10-20) | `54ecd10e5097b1ad` | `54ecd10e5097b1adc9e96fca3b0d2eeefbb81e22851ea738ee7e8a939e6a3949` | Baseline API before complaint graph integration |
| **LangGraph / Trust Integration** | `ad50324` (Checkpoint 2) | `ea8b6b43cd54e2f1` | `ea8b6b43cd54e2f190eecba7a9a1d13f99ddc5b527b1406dc574229b0a1d4187` | Added `/api/v1/complaints/structure` route |
| **Hardened Baseline** | `1ee025a` (Checkpoint 5/6) | `d848442f7e7632f5` | `d848442f7e7632f5cdbc73c2a2b6bbe7a242afec1ad408f99aa7fe1c22fc37a2` | Replaced wildcard CORS with origin whitelist (`BANDHOO_CORS_ORIGINS`); added generic 500 error handler |

### 2.2 Preserved Baseline Invariants (100% Identity Preserved)
All 16 remaining baseline files match their original 2026-10-20 hashes exactly:

| File | SHA-256 Hash (LF normalized) | Status |
|---|---|---|
| `legal_engine/__init__.py` | `d313c8e4c45d51df` | Identical |
| `legal_engine/amounts.py` | `35aeeeb80b4d3f3e` | Identical |
| `legal_engine/corpus.py` | `d5be04d2059f2dba` | Identical |
| `legal_engine/corpus_guard.py` | `27eb7bd2613ca296` | Identical |
| `legal_engine/llm_client.py` | `99f7f3fce32cc217` | Identical |
| `legal_engine/retrieval.py` | `6aef165b2df9f75f` | Identical |
| `legal_engine/schedule_registry.py` | `6f0af12b994706d7` | Identical |
| `legal_engine/schemas.py` | `8ce3535987fab323` | Identical |
| `legal_engine/service.py` | `a64d55fe2015f6fe` | Identical |
| `legal_engine/synonyms.py` | `4a8a830fec0ac0b0` | Identical |
| `scrape_bns.py` | `7e5c4440ff0a1d0f` | Identical |
| `benchmark/evaluate_benchmark.py` | `7a23da466d8ca567` | Identical |
| `benchmark/build_dataset.py` | `a736cc4c9be2fd05` | Identical |
| `bns_rag_dataset.json` | `7c7e3322b277e8bd` | Identical |
| `benchmark/bns_synthetic_benchmark_50.json` | `36f2e00dc517fe03` | Identical |
| Pre-migration backup (`reports/backups/bns_rag_dataset.pre_integrity_migration_2026-10-20.json`) | `d053ce3de31ef17d` | Identical, read-only |

### 2.3 Added Baseline Components
The following modules introduced in the complaint structuring workflow and security hardening are now indexed in the refreshed baseline:

| File | SHA-256 (first 16 hex chars) | Full SHA-256 | Description |
|---|---|---|---|
| `requirements-lock.txt` | `e893b3d0c94a3245` | `e893b3d0c94a3245037ae615170d10a905a9601d8e0fc6cfb33bc9e65e6d60a5` | Exact pinned Python dependency lockfile |
| `complaint_engine/__init__.py` | `bf18be70cd69f606` | `bf18be70cd69f606ca198dbd71d34c2ab96a575a7bcf1fbdb82a931a7428f522` | Package initializer |
| `complaint_engine/checks.py` | `56427e31a405edd9` | `56427e31a405edd9ebaa000494df9da182b8a786fec7c0be5d40cb4d3d8a1f73` | Contradiction, loss, and unsupported claim checks |
| `complaint_engine/draft.py` | `6e4bda6ecc23ba29` | `6e4bda6ecc23ba29d6727c7c34d4223f03b290ae5e5d36e2f42a7747805d762e` | Verbatim narrative drafting & section mapping |
| `complaint_engine/extraction.py` | `fd3f7ec9eff770e7` | `fd3f7ec9eff770e7045b4cbb233f0099fe6bc12036495bebeebc69ebf522c09d` | Fact extraction & edge-case regex rules |
| `complaint_engine/graph.py` | `18798991921aaa61` | `18798991921aaa610842db18544f8ae45a1f68fa5ca3f938b8ca819074b6e512` | LangGraph workflow state machine |
| `complaint_engine/jurisdiction.py` | `94576e146bd1b6b2` | `94576e146bd1b6b245a165b4c4fae3b33da003d19e0787a07c14a601aa0d6bc9` | Boundary containment and buffer checks |
| `complaint_engine/models.py` | `adf946d8cf835faf` | `adf946d8cf835fafa85418b763ecaa8a5f8e56994a32ec696515b60882e37989` | Pydantic state models & display categories |
| `src/App.jsx` | `ce4187a92edd397c` | `ce4187a92edd397c7e5a07c7c10b75965f577ba699f8481ffec1be9e7a96a323` | Hardened frontend with `API_BASE_URL` and ESLint fixes |

---

## 3. Comprehensive Verification Results

### 3.1 Full Pytest Suite (356 Tests)
Command executed: `python -m pytest tests/`  
Execution time: 46.10s  
Result: **356 passed, 0 failed, 0 warnings**

| Test Module | Tests | Result | Description |
|---|---|---|---|
| `test_adversarial_grievance_audit.py` | 10 | PASS | Grievance adversarial attack tests |
| `test_benchmark_metric_identities.py` | 5 | PASS | Benchmark evaluation metric mathematical identities |
| `test_complaint_defect_regressions.py` | 63 | PASS | Checkpoint 2 regression tests for all 8 extraction defects |
| `test_complaint_graph.py` | 26 | PASS | LangGraph complaint workflow states, review gates, and fallbacks |
| `test_corpus_guard.py` | 12 | PASS | Corpus protection, scraper guard, and read-only backup integrity |
| `test_corpus_integrity.py` | 28 | PASS | Integrity checks on BNS corpus text and section mappings |
| `test_frontend_trust_safety.py` | 1 | PASS | Frontend trust & safety contract verification |
| `test_gemini_pipeline.py` | 17 | PASS | Deterministic mocked LLM pipeline error handling |
| `test_inspection_regressions.py` | 72 | PASS | Historical defect inspection regression suite |
| `test_jurisdiction_and_api.py` | 12 | PASS | True centroid calculation, 100m buffer, and API contracts |
| `test_legal_accuracy_audit.py` | 11 | PASS | Legal accuracy across statutory cross-references |
| `test_legal_engine.py` | 13 | PASS | Legal engine amounts, synonyms, and schemas |
| `test_procedural_law_audit.py` | 10 | PASS | Procedural law audit checks |
| `test_reliability_followups.py` | 42 | PASS | Reliability, concurrency, and timeout handling |
| `test_retrieval_and_quality.py` | 8 | PASS | BM25 retrieval accuracy and ranking stability |
| `test_structuring_quality.py` | 26 | PASS | Structuring quality, polarity, and verbatim extraction |
| **Total** | **356** | **PASS** | **100% Pass Rate** |

### 3.2 BNS Legal Benchmark Evaluation (50 Cases)
Command executed: `python benchmark/evaluate_benchmark.py --mode fallback`  
Result: **100% Deterministic Reproducibility**
- **Evaluation Mode:** Deterministic BM25 Fallback
- **Micro Precision:** 18.70% (43/230)
- **Micro Recall:** 56.25% (36/64)
- **Micro F1:** 0.2807
- **Macro Precision:** 29.61%
- **Macro Recall:** 67.17%
- **Macro F1:** 0.3496
- **Contradicted Section False-Positive Rate:** 0.00% (0/40)
- **Misleading Keywords Immunity:** 100.00%
- **Explicit Negation Immunity:** 100.00%
- **Fact vs Inference Separation:** 100.00%

### 3.3 Structuring Evaluation (34 Cases)
Command executed: `python benchmark/structuring/evaluate_structuring.py`  
Result: **100% Integrity Across All Splits**
- **Overall Cases:** 34 (20 Dev, 14 Heldout)
- **Micro Precision:** 0.9702 (220/235)
- **Micro Recall:** 0.9955 (219/220)
- **Polarity Accuracy:** 100.00% (219/219)
- **Missing Field Accuracy:** 100.00% (238/238 fields, 0 false missing)
- **Contradiction Recall:** 1.00 (missed: 0)
- **Draft Preservation:** 34/34 passed
- **Integrity Violations:** 0 non-verbatim quotes, 0 unbacked verification claims, 0 non-draft submission statuses, 0 invalid contradictions
- **Jurisdiction Safety:** 11/11 correct, 0 unsafe assignments

### 3.4 Frontend Unit Tests & Static Analysis
Commands executed:
- `npm run lint` -> **PASS (0 errors, 0 warnings)**
- `node --test src/trustSafety.test.js` -> **PASS (23 tests passed, 0 failures)**

---

## 4. Rollback Snapshot & Procedure

### 4.1 Git Milestone Tags
The complete history of checkpoints is preserved in signed git tags:
1. `pre_checkpoint2_baseline`: Commit `281cfba` (Baseline before defect fixes).
2. `checkpoint2_complete`: Commit `ad50324` (Deterministic defect fixes).
3. `checkpoint3_ready`: Commit `a4ecb1e` (Independent evaluation protocol).
4. `checkpoint4_ready`: Commit `211627a` (Legal and jurisdiction review evidence package).
5. `checkpoint5_ready`: Commit `1ee025a` (Security, privacy, and dependency hardening).
6. `checkpoint6_baseline_refreshed`: *(Current commit)* (Appendix B baseline reconciled).

### 4.2 Rollback Procedure
To roll back any component or the full repository to any milestone:
```bash
# To rollback to the pre-checkpoint2 baseline:
git checkout pre_checkpoint2_baseline

# To rollback to the Checkpoint 5 state:
git checkout checkpoint5_ready

# Verify working tree checksums match the recorded snapshot:
python -c "
import hashlib
for path, expected in [('main.py', '54ecd10e5097b1ad')]:
    with open(path, 'rb') as f:
        assert hashlib.sha256(f.read().replace(b'\r\n', b'\n')).hexdigest()[:16] == expected
"
```

### 4.3 Pre-Migration Backup Protection
The pre-migration backup (`reports/backups/bns_rag_dataset.pre_integrity_migration_2026-10-20.json`) remains strictly protected:
- SHA-256: `d053ce3de31ef17d985b03251e9178d38b3ed70144dc2abe7802c1f873783807`
- File System Permissions: Read-only (`-r--r--r--` / Windows `FILE_ATTRIBUTE_READONLY`)
- Protected by automated test `tests/test_corpus_guard.py::test_pre_migration_backup_intact_and_read_only`

---

## 5. Blocker Register Governance

The reconciliation of the baseline checksums does **not** close any substantive legal blockers. The release blocker register (`reports/release_blocker_register.md`) maintains all 53 blockers in **OPEN** status:
- **RB-01 to RB-05 (Sources & Provenance):** OPEN pending primary Gazette copies and official police boundary licenses.
- **RB-06 to RB-11 (Statutory Interpretations):** OPEN pending qualified legal reviewer sign-off on Section 173(3) and theft provisions.
- **RB-45 & RB-46 (Evaluation Independence):** OPEN pending execution of the independent evaluation protocol by external third parties.

**Baseline Refresh BR-2026-10-21-01 is complete, verified, and operational.**
