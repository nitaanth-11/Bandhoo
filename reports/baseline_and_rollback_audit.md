# Bandhoo Baseline Snapshot and Rollback Audit

**Prepared:** 2026-10-20. **Status:** baseline snapshot created and verified. Bandhoo remains internal-testing-only; this audit concerns recoverability only, not legal validity.

## 1. Starting state (inspected before acting)

| Check | Result |
|---|---|
| Previous baseline task | **Had not run.** `reports/baseline_and_rollback_audit.md` did not exist; no snapshot directory, tag, stash or extra branch existed. |
| Git | One commit (`1ad5bb6 The initial phase`) on `master`. 6 tracked files modified (`.gitignore`, `bns_rag_dataset.json`, `main.py`, `public/bns_rag_dataset.json`, `scrape_bns.py`, `src/App.jsx`). Untracked: `benchmark/`, `legal_engine/`, `reports/`, `tests/`, `pytest.ini`, `requirements.txt`. The remote URL contains no embedded credentials. |
| Ignore rules | `.gitignore` excludes `.env`, `.env.*` (except `.env.example`), `node_modules`, `dist`, Python caches, virtual environments and `scraper_staging/`. |
| Secret-like files | `.env` only (name checked; **contents not read**). |
| Disk | 682 GiB free; project 95 MB, of which `node_modules` is 87 MB and `.git` 400 KB. |
| Checksum register | `reports/release_blocker_register.md` Appendix B: 17 baseline hashes, all matching before the snapshot was taken. |

No commit, reset, clean, deletion or overwrite was performed in the original project.

## 2. Snapshot

| Item | Value |
|---|---|
| Snapshot root | `/Users/tanaya/Desktop/Bandhoo_snapshots/bandhoo_baseline_20261020T210347/` (outside the repository; timestamp is local system time) |
| Project copy | `…/bandhoo_baseline_20261020T210347/project/`: 105 files, 6.7 MB |
| SHA-256 manifest | `…/bandhoo_baseline_20261020T210347/MANIFEST.sha256`: 105 entries, `shasum -c` format, paths relative to `project/`. SHA-256 of the manifest itself: `5125ea461052efb0b0d38b437f0da22f02e4d1f110d67e0cdab0fcd9b779b2c1` |
| Permissions record | `…/PERMISSIONS.txt`: octal mode of each file in the original (87 × 644, 14 × 755, 4 × 444). SHA-256: `0ab600432d4c8738f6b6c4d8dcf7b78505f6aeb0872becf02b9872c0c86b032a` |
| Comparison record | `…/COMPARISON_SUMMARY.json`. SHA-256: `6a6cf7c340797393843cd5a514eee08e1f9ba0d6e02d298a25e15082232d1849` |
| Copy method | `rsync -a` (preserves timestamps and modes) from `/Users/tanaya/Desktop/Bandhoo/` |
| Protection | Snapshot made read-only (`chmod -R a-w`) after verification. The root directory was briefly made writable once, to add `PERMISSIONS.txt`; the project copy was not changed, and it still matched the manifest 105/105 afterwards. |

### 2.1 Included

All tracked and untracked project files, including:
- the uncommitted changes to `main.py` and `src/App.jsx`;
- `.git/` (full history and index);
- `legal_engine/`, `tests/`, `benchmark/`, `reports/` (including the read-only corpus backup `reports/backups/bns_rag_dataset.pre_integrity_migration_2026-10-20.json`);
- `public/`, `src/`;
- the data files (`bns_rag_dataset.json`, `bns_finetune_dataset.json`, `bns_scenarios_dataset.json`, GeoJSON/KML, police-station data);
- `package.json` and `package-lock.json`, `requirements.txt`, `pytest.ini`, `.gitignore`.

### 2.2 Excluded (4,371 original files; every omission explained)

| Rule | Files | Reason | How to recover |
|---|---|---|---|
| `.env`, `.env.*` | 1 | Secrets; never read or copied. | Recreate from the secure source used originally. Not needed for offline tests. |
| `node_modules/` | 4,338 | Generated frontend dependencies (87 MB). | `npm ci` using the snapshot's `package-lock.json` (not tested in this audit). |
| `__pycache__/`, `*.pyc` | 27 | Python bytecode caches. | Regenerated automatically. **Note:** `__pycache__/kml_loader.cpython-312.pyc` is tracked in git and was excluded by this rule (see §6). |
| `.pytest_cache/` | 5 | Test cache. | Regenerated automatically. |
| `.DS_Store`, `scraper_staging/` | 0 present | OS metadata; unreviewed scraper output. | — |

## 3. Integrity verification

| Check | Result |
|---|---|
| Snapshot files vs original (SHA-256, every manifest entry) | **105/105 identical**; 0 mismatches; 0 manifest files missing from the original. |
| Original files not in snapshot | 4,371, all matched by the exclusion rules above; **0 unexplained omissions**. |
| Register Appendix B baseline hashes (17 files: all production code, corpus, benchmark labels, pre-migration backup) | All present in the snapshot with matching hashes. |

## 4. Restoration verification

| Step | Result |
|---|---|
| Restore attempt 1 (scratch: `…/scratchpad/restore_test`) | Manifest 105/105 OK; 17/17 register hashes OK. The test suite ran **227 passed, 1 failed** (`tests/test_corpus_guard.py::test_pre_migration_backup_intact_and_read_only`). **Cause:** the restore procedure made every file writable (`chmod -R u+w`), so the read-only backup lost its read-only mode. No content was wrong. This led to recording original permissions (`PERMISSIONS.txt`). |
| Restore attempt 2 (clean scratch: `…/scratchpad/restore_test2`) using the procedure in §7.1 | Manifest **105/105 OK**; permissions **105/105 match** `PERMISSIONS.txt`. |
| Git metadata in restored copy | `git fsck` exit status 0, no errors; `git log` shows `1ad5bb6`. `git status` differed only by the excluded tracked file `__pycache__/kml_loader.cpython-312.pyc` (shown as deleted). After `git checkout -- __pycache__/kml_loader.cpython-312.pyc` in the scratch copy, the recovered file was byte-identical to the original and `git status` matched the original exactly. |
| Import isolation | In the restored copy, `legal_engine` was imported from the restored directory, not from the original project. |

The scratch restores live in the session scratchpad (`/private/tmp/claude-501/…/scratchpad/`) and are temporary. The snapshot under `/Users/tanaya/Desktop/Bandhoo_snapshots/` is the durable copy.

## 5. Offline tests in the restored copy

| Item | Result |
|---|---|
| Command | `GEMINI_API_KEY="" GOOGLE_API_KEY="" python3.14 -m pytest -q -p no:cacheprovider --rootdir=<restored copy>` |
| Collected | 228 tests |
| Result (restore attempt 2) | **228 passed, 1 warning** (upstream Google GenAI SDK deprecation) |
| Live calls | None. No `.env` exists in the restored copy; Gemini keys blank; LLM behaviour is mocked in tests. |
| Environment | System Python 3.14 (`/usr/local/bin/python3.14`) with already-installed packages. The original environment was not modified. |

## 6. Discrepancies, limitations and risks

1. **Tracked bytecode file excluded.** `__pycache__/kml_loader.cpython-312.pyc` is committed in git but was excluded by the cache rule. It is recoverable from the commit (verified). It is a generated file with no effect on the backend.
2. **This audit document is not in the snapshot.** It was written after the snapshot. Restoring the snapshot over the project would not include it unless it is preserved separately.
3. **Same physical disk.** The snapshot is on the same machine and disk as the project. It does not protect against disk loss or theft. An off-machine copy (with the manifest) is recommended.
4. **Not a git commit.** Git history was deliberately not altered; the snapshot is a filesystem copy. A commit or tag remains a decision for the project owner.
5. **Dependencies not snapshotted.** The Python environment (system site-packages) and `node_modules` are not captured. Restores rely on installed packages or `requirements.txt` / `package-lock.json`; frontend reinstall and build were not tested.
6. **`.env` not captured.** Must be recreated from its secure source for any live Gemini use.
7. **Read-only protection is advisory.** Anyone with account access can change permissions. Integrity should be re-checked against `MANIFEST.sha256` (and the manifest against its hash recorded above) before any restore.
8. **Tests cover offline behaviour only.** They do not validate live Gemini behaviour or legal correctness.

## 7. Rollback instructions

Always verify before and after. Never delete the current project in place; move it aside instead.

```bash
SNAP=/Users/tanaya/Desktop/Bandhoo_snapshots/bandhoo_baseline_20261020T210347
```

### 7.1 Restore into a new directory (recommended; non-destructive)

```bash
# 0. Verify the manifest itself, then the snapshot
shasum -a 256 "$SNAP/MANIFEST.sha256"      # expect 5125ea461052efb0b0d38b437f0da22f02e4d1f110d67e0cdab0fcd9b779b2c1
(cd "$SNAP/project" && shasum -a 256 -c ../MANIFEST.sha256 | grep -vc ': OK$')   # expect 0

# 1. Copy
DEST=/Users/tanaya/Desktop/Bandhoo_restored        # must not exist yet
mkdir "$DEST" && rsync -a "$SNAP/project/" "$DEST/"

# 2. Re-apply original permissions (directories writable, files as recorded)
find "$DEST" -type d -exec chmod u+w {} +
while IFS= read -r line; do chmod "${line%%  *}" "$DEST/${line#*  }"; done < "$SNAP/PERMISSIONS.txt"

# 3. Verify the restored copy
(cd "$DEST" && shasum -a 256 -c "$SNAP/MANIFEST.sha256" | grep -vc ': OK$')      # expect 0

# 4. Optional: restore the tracked bytecode file and confirm git state
(cd "$DEST" && git checkout -- __pycache__/kml_loader.cpython-312.pyc && git fsck && git status --short)

# 5. Recreate excluded items as needed
#    - .env: from its secure source (never from logs or reports)
#    - node_modules: (cd "$DEST" && npm ci)

# 6. Offline tests (no Gemini)
(cd "$DEST" && GEMINI_API_KEY="" GOOGLE_API_KEY="" python3.14 -m pytest -q -p no:cacheprovider)   # expect 228 passed
```

### 7.2 Replace the working project (only on an explicit owner decision)

```bash
# Move the current project aside; do not delete it
mv /Users/tanaya/Desktop/Bandhoo /Users/tanaya/Desktop/Bandhoo_pre_rollback_$(date +%Y%m%dT%H%M%S)
# Restore with §7.1, using DEST=/Users/tanaya/Desktop/Bandhoo
# Then copy back items the snapshot does not contain, from the moved-aside directory:
#   .env, node_modules (or run npm ci), and any reports written after 2026-10-20T21:03
#   (including reports/baseline_and_rollback_audit.md)
```

### 7.3 Restore a single file

```bash
F=legal_engine/service.py                         # example
grep "  $F\$" "$SNAP/MANIFEST.sha256"              # expected hash
cp "$SNAP/project/$F" "/Users/tanaya/Desktop/Bandhoo/$F"
chmod "$(grep "  $F\$" "$SNAP/PERMISSIONS.txt" | cut -d' ' -f1)" "/Users/tanaya/Desktop/Bandhoo/$F"
shasum -a 256 "/Users/tanaya/Desktop/Bandhoo/$F"  # must equal the manifest hash
```

After any rollback, re-run the offline test suite and the fallback benchmark (`python benchmark/evaluate_benchmark.py --mode fallback`), and compare the results with `benchmark/evaluation_report_fallback.json` from the snapshot.

## 8. Original working tree after this task

- All 105 manifest files in the original still match the manifest (105/105).
- The 17 register baseline hashes are unchanged.
- The pre-migration backup is still read-only.
- No other file was created or modified, apart from this document.
- No `.env` read, no Gemini call, no scraper run.
