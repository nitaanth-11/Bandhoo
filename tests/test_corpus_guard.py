"""
Safeguards against silently overwriting the reviewed corpus, and downstream handling of the
per-record verification fields across every corpus record. No network, scraper run or LLM call.
"""

import ast
import hashlib
import importlib.util
import json
import os
import re
import shutil

import pytest

from legal_engine.corpus import BNSCorpus
from legal_engine.corpus_guard import (
    PROTECTED_CORPUS_FILES,
    CorpusOverwriteError,
    assert_safe_scraper_output,
    backup_with_verification,
    is_migrated_corpus,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(BASE_DIR, "bns_rag_dataset.json")
BACKUP = os.path.join(BASE_DIR, "reports", "backups", "bns_rag_dataset.pre_integrity_migration_2026-10-20.json")
BACKUP_SHA256 = "d053ce3de31ef17d985b03251e9178d38b3ed70144dc2abe7802c1f873783807"


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ── Backup integrity ──

def test_pre_migration_backup_intact_and_read_only():
    assert sha256(BACKUP) == BACKUP_SHA256
    assert not os.access(BACKUP, os.W_OK)
    with open(BACKUP, encoding="utf-8") as f:
        records = json.load(f)
    assert len(records) == 358 and not any("verification" in r for r in records)


# ── Scraper output guard ──

@pytest.mark.parametrize("path", PROTECTED_CORPUS_FILES)
def test_guard_refuses_live_corpus_files(path):
    with pytest.raises(CorpusOverwriteError):
        assert_safe_scraper_output(path)


def test_guard_refuses_any_migrated_corpus(tmp_path):
    copy = tmp_path / "elsewhere.json"
    shutil.copy(DATASET, copy)
    assert is_migrated_corpus(str(copy))
    with pytest.raises(CorpusOverwriteError):
        assert_safe_scraper_output(str(copy))


def test_guard_allows_staging_and_legacy_files(tmp_path):
    assert_safe_scraper_output(str(tmp_path / "scraper_staging" / "bns_rag_dataset.json"))
    legacy = tmp_path / "legacy.json"
    shutil.copy(BACKUP, legacy)
    assert not is_migrated_corpus(str(legacy))
    assert_safe_scraper_output(str(legacy))


def test_backup_with_verification(tmp_path):
    src = tmp_path / "data.json"
    src.write_text('[{"section": 1}]', encoding="utf-8")
    backup = backup_with_verification(str(src), str(tmp_path / "backups"))
    assert sha256(backup) == sha256(src) and backup != str(src)


def test_scraper_writes_only_through_guard_to_staging():
    source = open(os.path.join(BASE_DIR, "scrape_bns.py"), encoding="utf-8").read()
    assert 'OUTPUT_DIR = os.path.join(REPO_DIR, "scraper_staging")' in source
    assert '"public"' not in source
    tree = ast.parse(source)
    lines = source.splitlines()
    writes = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "open"
              and any(isinstance(a, ast.Constant) and a.value == "w" for a in n.args)]
    assert len(writes) == 3
    for call in writes:
        assert "assert_safe_scraper_output" in lines[call.lineno - 2], f"unguarded write at line {call.lineno}"


# ── Migration script cannot silently overwrite ──

@pytest.fixture(scope="module")
def migration():
    spec = importlib.util.spec_from_file_location("apply_corpus_corrections",
                                                  os.path.join(BASE_DIR, "reports", "apply_corpus_corrections.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_refuses_migrated_dataset(migration, tmp_path):
    copy = tmp_path / "corpus.json"
    shutil.copy(DATASET, copy)
    before = sha256(copy)
    with pytest.raises(SystemExit, match="already migrated"):
        migration.main(str(copy), str(tmp_path / "missing_gazette.txt"), str(tmp_path / "log.json"))
    assert sha256(copy) == before


def test_migration_validation_failure_writes_nothing(migration, tmp_path):
    copy = tmp_path / "corpus.json"
    shutil.copy(BACKUP, copy)
    os.chmod(copy, 0o644)
    before = sha256(copy)
    bad_gazette = tmp_path / "gazette.txt"
    bad_gazette.write_text("1. Not the Gazette.\n", encoding="utf-8")
    backups_dir = os.path.join(BASE_DIR, "reports", "backups")
    backups_before = set(os.listdir(backups_dir))
    with pytest.raises(AssertionError, match="358 Gazette sections"):
        migration.main(str(copy), str(bad_gazette), str(tmp_path / "log.json"))
    assert sha256(copy) == before
    assert not (tmp_path / "log.json").exists()
    assert set(os.listdir(backups_dir)) == backups_before


# ── Downstream handling across all records ──

@pytest.fixture(scope="module")
def corpus():
    return BNSCorpus()


def test_every_llm_context_block_is_clean_and_labelled(corpus):
    for sec in corpus.all_sections():
        ctx = corpus.format_for_llm_context([sec["section"]])
        assert "BNSS Classification" not in ctx
        assert "As prescribed" not in ctx
        verification_line = re.search(r"- Text Verification: (.*)", ctx).group(1)
        if sec["verified"]:
            assert not verification_line.startswith("NOT verified"), sec["section"]
        else:
            assert verification_line.startswith("NOT verified"), sec["section"]


def test_missing_punishment_never_replaced_with_text(corpus):
    for sec in corpus.all_sections():
        if not sec["punishment"]:
            ctx = corpus.format_for_llm_context([sec["section"]])
            line = re.search(r"- Punishment: (.*)", ctx).group(1)
            assert line in (
                "No punishment clause in this section (definition, exception or general provision).",
                "Not available in the corpus. Do not infer a punishment.",
            ), sec["section"]


def test_bm25_documents_unchanged_by_field_separation(corpus):
    """Every BM25 document contains the statutory text and, where present, the legacy scraped wording."""
    for sec in corpus.all_sections():
        doc = corpus.get_document_text(sec["section"])
        assert sec["text"] in doc
        scraped = sec["scraped_procedural_classification"]
        if scraped:
            assert scraped["text"] in doc
