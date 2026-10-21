"""
Corpus integrity regression tests (statutory corpus migration of 2026-10-20).

Covers the Section 309 punishment correction, restoration of Sections 111 and 120, sections without a
punishment clause, separation of scraped BNSS classification blocks from statutory text, per-section
verification evidence, the transcription validator used by the migration, and compatibility with the
legacy record format. No LLM calls are made.
"""

import importlib.util
import json
import os
from unittest.mock import MagicMock

import pytest

from legal_engine.corpus import BNSCorpus, split_scraped_classification
from legal_engine.llm_client import GeminiLegalClient
from legal_engine.retrieval import BM25LegalRetriever
from legal_engine.schemas import NarrativeInput, OffenceClassificationResponse
from legal_engine.service import LegalAnalysisService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "bns_rag_dataset.json")
LOG_PATH = os.path.join(BASE_DIR, "reports", "corpus_corrections_log_2026-10-20.json")
TEXT_STATUSES = {"consistent_with_gazette", "restored_from_gazette", "differs_from_gazette_needs_review", "possibly_incomplete"}
PUNISHMENT_STATUSES = {"consistent_with_gazette", "verified_against_gazette", "no_punishment_clause", "unknown", "unverified"}


@pytest.fixture(scope="module")
def corpus():
    return BNSCorpus()


@pytest.fixture(scope="module")
def raw_records():
    with open(DATASET_PATH, encoding="utf-8") as f:
        return {r["section"]: r for r in json.load(f)}


@pytest.fixture(scope="module")
def migration():
    spec = importlib.util.spec_from_file_location("apply_corpus_corrections",
                                                  os.path.join(BASE_DIR, "reports", "apply_corpus_corrections.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ── Section 309 punishment ──

def test_section_309_punishment_is_statutory_punishment(corpus):
    sec = corpus.get_section(309)
    p = sec["punishment"]
    assert "Z is put in fear" not in p and "punishable as such" not in p
    assert "rigorous imprisonment for a term which may extend to ten years" in p
    assert "may be extended to fourteen years" in p
    assert "Section 309(5): shall be punished with rigorous imprisonment for a term which may extend to seven years" in p
    assert [x["sub_section"] for x in sec["punishment_provisions"]] == ["309(4)", "309(5)", "309(6)"]
    assert sec["punishment_status"] == "verified_against_gazette"


def test_section_309_context_presents_corrected_punishment(corpus):
    ctx = corpus.format_for_llm_context([309])
    assert "- Punishment: Section 309(4): shall be punished with rigorous imprisonment" in ctx


# ── Sections 111 and 120 completeness ──

def test_section_111_restored(corpus):
    sec = corpus.get_section(111)
    text = sec["text"]
    assert text.startswith("(1) Any continuing unlawful activity")
    for marker in ("(2) Whoever commits organised crime", "(3) Whoever abets", "(4) Any person who is a member",
                   "(5) Whoever, intentionally, harbours", "(6) Whoever possesses any property", "(7) If any person on behalf"):
        assert marker in text
    assert "“proceeds of any organised crime” means" not in text
    assert sec["text_status"] == "restored_from_gazette" and sec["verified"] is True
    assert [x["sub_section"] for x in sec["punishment_provisions"]] == [f"111({i})" for i in range(2, 8)]


def test_section_120_restored(corpus):
    sec = corpus.get_section(120)
    text = sec["text"]
    assert text.startswith("(1) Whoever voluntarily causes hurt for the purpose of extorting")
    assert "(2) Whoever voluntarily causes grievous hurt for any purpose referred to in sub-section (1)" in text
    assert "Illustrations." in text
    assert sec["punishment"].startswith("Section 120(1): shall be punished")
    assert sec["text_status"] == "restored_from_gazette"


def test_section_264_punishment_filled(corpus):
    p = corpus.get_section(264)["punishment"]
    assert "if he does so intentionally" in p and "if he does so negligently" in p


# ── Genuine absence of punishment clauses ──

@pytest.mark.parametrize("sec_num", [2, 4, 32, 54])
def test_sections_without_punishment_clause(corpus, raw_records, sec_num):
    sec = corpus.get_section(sec_num)
    assert sec["punishment"] == ""
    assert sec["punishment_status"] == "no_punishment_clause"
    assert raw_records[sec_num]["verification"]["punishment_method"] == "manual_review"
    ctx = corpus.format_for_llm_context([sec_num])
    assert "No punishment clause in this section" in ctx
    assert "As prescribed by court" not in ctx


def test_no_section_left_with_unexplained_empty_punishment(raw_records):
    for sec, r in raw_records.items():
        if not r["punishment"]:
            assert r["punishment_status"] in {"no_punishment_clause", "unknown"}, sec


# ── Separation of scraped BNSS classification from BNS text ──

def test_no_statutory_text_contains_scraped_classification(raw_records, corpus):
    assert not any("BNSS Classification" in r["text"] for r in raw_records.values())
    assert not any("BNSS Classification" in s["text"] for s in corpus.all_sections())
    assert sum(1 for r in raw_records.values() if r["scraped_procedural_classification"]) == 201


def test_llm_context_excludes_scraped_classification(corpus):
    ctx = corpus.format_for_llm_context([87, 90, 276, 305, 97])
    assert "BNSS Classification" not in ctx
    assert "Triable by" not in ctx and "Non-cognizable" not in ctx
    assert "Official Text" not in ctx and "- Statutory Text:" in ctx


def test_scraped_blocks_preserved_and_marked(raw_records):
    for sec in (87, 90, 276):
        block = raw_records[sec]["scraped_procedural_classification"]
        assert block["status"] == "unverified_secondary_source"
        assert block["gazette_check"] == "conflicts_with_gazette_schedule_i"
        assert block["text"].startswith("BNSS Classification")
    for sec in (354, 355, 357):
        assert raw_records[sec]["scraped_procedural_classification"]["gazette_check"] == "consistent_manual_positional_reading"


def test_scraped_classification_not_used_as_procedural_metadata(corpus):
    service = LegalAnalysisService(corpus=corpus, retriever=BM25LegalRetriever(corpus),
                                   llm_client=MagicMock(is_available=False))
    # Section 87 has a scraped (and wrong) classification but no verified registry entry.
    assert service._determine_schedule_metadata(87, corpus.get_section(87), "x") == (None, None)


def test_bm25_document_keeps_legacy_wording_for_retrieval_parity(corpus):
    doc = corpus.get_document_text(97)
    assert "BNSS Classification" in doc
    assert corpus.get_section(97)["text"] in doc


# ── Section-level verification status ──

def test_every_record_has_verification_evidence(raw_records):
    for sec, r in raw_records.items():
        v = r["verification"]
        assert v["text_status"] in TEXT_STATUSES, sec
        assert r["punishment_status"] in PUNISHMENT_STATUSES, sec
        assert v["checked_on"] == "2026-10-20" and "Gazette" in v["source_document"]
        assert v["legal_review"] == "not performed"
        assert {"corpus_only_numbers", "gazette_token_coverage", "ordered_comparison_problems_sample"} <= set(v["evidence"])
        assert r["verified"] is (v["text_status"] in {"consistent_with_gazette", "restored_from_gazette"}), sec


def test_no_blanket_verification(raw_records):
    flags = [r["verified"] for r in raw_records.values()]
    assert any(flags) and not all(flags)


def test_cross_reference_difference_recorded_and_flagged_to_llm(raw_records, corpus):
    v = raw_records[115]["verification"]
    assert v["text_status"] == "differs_from_gazette_needs_review"
    assert v["evidence"]["cross_reference_numbers_differ"] is True
    assert "120" in v["evidence"]["corpus_only_numbers"]
    assert "NOT verified" in corpus.format_for_llm_context([115])


def test_corrections_log_matches_corpus(raw_records):
    with open(LOG_PATH, encoding="utf-8") as f:
        log = json.load(f)
    entries = [e for e in log["entries"] if e["method"] == "manual_transcription_automated_check"]
    assert {e["section"] for e in entries} == {2, 4, 13, 32, 56, 58, 71, 111, 120, 148, 199, 251, 252, 264, 309, 311, 312, 341}
    for e in entries:
        assert raw_records[e["section"]][e["field"]] == e["new_value"]
        assert e["previous_value"] != e["new_value"] and "Gazette" in e["source"]


# ── Transcription validator: incomplete, altered, reordered text ──

GAZ = "whoever commits robbery shall be punished with rigorous imprisonment for a term which may extend to ten years".split()
HEADINGS = [["robbery"], ["dacoity"]]


def test_validator_accepts_exact_transcription(migration):
    ok, omitted, problems = migration.transcription_check(GAZ, " ".join(GAZ[3:]), HEADINGS)
    assert ok and not omitted and not problems


@pytest.mark.parametrize("bad,kind", [
    ("shall be punished with simple imprisonment for a term which may extend to ten years", "replace"),     # altered word
    ("shall not be punished with rigorous imprisonment for a term which may extend to ten years", "delete"),  # added word
    ("shall be punished with rigorous imprisonment for a term which may extend to years ten", None),         # reordered
    ("shall be punished with imprisonment for a term which may extend to ten years", "missing"),             # word left out
])
def test_validator_rejects_altered_added_reordered_or_incomplete(migration, bad, kind):
    ok, _, problems = migration.transcription_check(GAZ, bad, HEADINGS)
    assert not ok
    if kind:
        assert any(p.startswith(kind) for p in problems)


def test_validator_tolerates_only_margin_headings(migration):
    gazette = "whoever commits robbery shall be punished robbery dacoity with rigorous imprisonment".split()
    ok, omitted, _ = migration.transcription_check(gazette, "shall be punished with rigorous imprisonment", HEADINGS)
    assert ok and omitted == ["robbery dacoity"]
    gazette_noise = "whoever commits robbery shall be punished robbery death with rigorous imprisonment".split()
    ok, _, problems = migration.transcription_check(gazette_noise, "shall be punished with rigorous imprisonment", HEADINGS)
    assert not ok and problems[0].startswith("missing")


# ── Backward compatibility with legacy records ──

@pytest.fixture
def legacy_corpus(tmp_path):
    data = [
        {"section": 303, "title": "Theft", "chapter": "Chapter XVII",
         "text": "Whoever, intending to take dishonestly any movable property out of the possession of any person "
                 "without that person's consent, moves that property in order to such taking, is said to commit theft.\n\n"
                 "BNSS Classification\n\n• Cognizable\n\n• Non-bailable",
         "punishment": "shall be punished with imprisonment of either description for a term which may extend to three years.",
         "keywords": ["theft", "stole", "phone"], "verified": True,
         "source": "Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023)", "schedule_i_status": "unverified_schedule"},
        {"section": 2, "title": "Definitions", "chapter": "Chapter I",
         "text": "In this Sanhita, unless the context otherwise requires, the following words have meanings.",
         "punishment": "", "keywords": ["definitions"], "verified": True,
         "source": "Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023)"},
    ] + [
        # Unrelated filler records: BM25 term weights are zero in a two-document corpus.
        {"section": n, "title": title, "chapter": "Chapter VI", "text": text, "punishment": "",
         "keywords": [title.lower()], "verified": True}
        for n, title, text in (
            (115, "Voluntarily causing hurt", "Whoever does any act with the intention of thereby causing hurt to any person."),
            (351, "Criminal intimidation", "Whoever threatens another with any injury to his person, reputation or property."),
            (324, "Mischief", "Whoever with intent to cause wrongful loss causes the destruction of any property."),
        )
    ]
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return BNSCorpus(str(path))


def test_legacy_records_load_with_separated_text(legacy_corpus):
    sec = legacy_corpus.get_section(303)
    assert "BNSS Classification" not in sec["text"]
    assert sec["scraped_procedural_classification"]["gazette_check"] == "not_checked_against_gazette"
    assert sec["text_status"] == "unverified" and sec["punishment_status"] == "unverified"
    assert legacy_corpus.get_section(2)["scraped_procedural_classification"] is None
    ctx = legacy_corpus.format_for_llm_context([303, 2])
    assert "BNSS Classification" not in ctx
    assert "NOT verified against the Gazette text" in ctx
    assert "Not available in the corpus. Do not infer a punishment." in ctx


def test_legacy_corpus_works_end_to_end(legacy_corpus):
    service = LegalAnalysisService(corpus=legacy_corpus, retriever=BM25LegalRetriever(legacy_corpus),
                                   llm_client=MagicMock(spec=GeminiLegalClient, is_available=False))
    res = service.analyze_complaint(NarrativeInput(narrative="Someone stole my phone from my bag."))
    assert isinstance(res, OffenceClassificationResponse)
    assert [p.section for p in res.predictions] == [303]
    OffenceClassificationResponse.model_validate(res.model_dump())


def test_split_helper():
    assert split_scraped_classification("Statute text.\n\nBNSS Classification\n• Cognizable") == ("Statute text.", "BNSS Classification\n• Cognizable")
    assert split_scraped_classification("Statute text only.") == ("Statute text only.", None)
