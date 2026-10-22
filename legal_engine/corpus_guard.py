"""
Write safeguards for the statutory corpus.

The backend corpus (bns_rag_dataset.json) carries reviewed corrections and per-record verification
evidence (see reports/corpus_integrity_audit.md). These helpers stop tools from silently replacing it:
- assert_safe_scraper_output refuses scraper writes to the live corpus files or to any migrated corpus.
- backup_with_verification copies a file and confirms the copy is byte-identical before any rewrite.
"""

import datetime
import hashlib
import json
import os
import shutil

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTECTED_CORPUS_FILES = (
    os.path.join(REPO_ROOT, "datasets", "bns_rag_dataset.json"),
    os.path.join(REPO_ROOT, "bns_rag_dataset.json"),
    os.path.join(REPO_ROOT, "public", "bns_rag_dataset.json"),
)
WORKFLOW_DOC = "reports/CORPUS_UPDATE_WORKFLOW.md"


class CorpusOverwriteError(RuntimeError):
    """Raised when a write would replace the reviewed corpus without the documented workflow."""


def is_migrated_corpus(path: str) -> bool:
    """True if path is a corpus JSON file whose records carry per-record verification evidence."""
    if not os.path.isfile(path):
        return False
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError):
        return False
    return isinstance(data, list) and any(isinstance(r, dict) and "verification" in r for r in data)


def assert_safe_scraper_output(path: str) -> None:
    """Raises CorpusOverwriteError if a scraper write to path could replace the reviewed corpus."""
    target = os.path.realpath(path)
    if target in {os.path.realpath(p) for p in PROTECTED_CORPUS_FILES}:
        raise CorpusOverwriteError(
            f"Refusing to write scraped output to {path}: it is a live corpus file. Write to a staging "
            f"directory and follow {WORKFLOW_DOC}."
        )
    if is_migrated_corpus(target):
        raise CorpusOverwriteError(
            f"Refusing to overwrite {path}: it is a migrated corpus with verification evidence. "
            f"Follow {WORKFLOW_DOC}."
        )


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def backup_with_verification(path: str, backup_dir: str) -> str:
    """Copies path into backup_dir with a timestamp, verifies the copy byte-for-byte and returns its path."""
    os.makedirs(backup_dir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f")
    base, ext = os.path.splitext(os.path.basename(path))
    backup_path = os.path.join(backup_dir, f"{base}.backup_{stamp}{ext}")
    shutil.copy2(path, backup_path)
    if _sha256(backup_path) != _sha256(path):
        raise CorpusOverwriteError(f"Backup verification failed for {path}; nothing was written.")
    return backup_path
