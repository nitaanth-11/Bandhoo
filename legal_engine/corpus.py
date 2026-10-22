"""
Legal Corpus Management for Bharatiya Nyaya Sanhita, 2023.
Loads, validates, and provides access to cleaned statutory text.
"""

import json
import os
import re
from typing import Dict, List, Optional, Any, Tuple


from legal_engine.schedule_registry import get_verified_schedule_entry

# Scraped procedural metadata that older records appended to the statutory text. It is not part of the BNS.
SCRAPED_CLASSIFICATION_RE = re.compile(r"\n*\s*BNSS Classification.*", re.S)

TEXT_STATUS_LABELS = {
    "consistent_with_gazette": "consistent with the Gazette text (automated check; not a legal review)",
    "restored_from_gazette": "restored from the Gazette text (automated check of transcription; not a legal review)",
    "differs_from_gazette_needs_review": "NOT verified: wording differs from the Gazette text in places; treat wording and section cross-references with caution",
    "possibly_incomplete": "NOT verified: may be incomplete compared with the Gazette text",
}
PUNISHMENT_FALLBACK_LABELS = {
    "no_punishment_clause": "No punishment clause in this section (definition, exception or general provision).",
    "unknown": "Not available in the corpus. Do not infer a punishment.",
}


def split_scraped_classification(text: str) -> Tuple[str, Optional[str]]:
    """Splits legacy text into (statutory text, scraped classification block or None)."""
    m = SCRAPED_CLASSIFICATION_RE.search(text or "")
    if not m:
        return (text or "").strip(), None
    return text[:m.start()].strip(), m.group(0).strip()


class BNSCorpus:
    def __init__(self, dataset_path: Optional[str] = None):
        if dataset_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            for candidate in [
                os.path.join(base_dir, "datasets", "bns_rag_dataset.json"),
                os.path.join(base_dir, "bns_rag_dataset.json"),
            ]:
                if os.path.exists(candidate):
                    dataset_path = candidate
                    break
            else:
                dataset_path = os.path.join(base_dir, "datasets", "bns_rag_dataset.json")

        self.dataset_path = dataset_path
        self.sections_by_num: Dict[int, Dict[str, Any]] = {}
        self.excluded_sections: List[int] = []
        self._load_and_validate()

    def _load_and_validate(self):
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"BNS statutory dataset not found at: {self.dataset_path}")

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for record in data:
            sec_num = record.get("section")
            # Statutory text only: any scraped classification block (legacy records) is held separately.
            text, legacy_block = split_scraped_classification(record.get("text") or "")
            scraped = record.get("scraped_procedural_classification")
            if scraped is None and legacy_block:
                scraped = {"text": legacy_block, "status": "unverified_secondary_source",
                           "gazette_check": "not_checked_against_gazette"}
            verification = record.get("verification") or {}
            verified = record.get("verified", False)

            # Exclude incomplete records from definitive legal reasoning
            if not text or len(text) < 15:
                self.excluded_sections.append(sec_num)
                continue

            sec_int = int(sec_num)
            verified_sched = get_verified_schedule_entry(sec_int)
            sched_status = "verified_schedule" if verified_sched else record.get("schedule_i_status", "unverified_schedule")

            self.sections_by_num[sec_int] = {
                "section": sec_int,
                "title": record.get("title", f"Section {sec_int}"),
                "chapter": record.get("chapter", ""),
                "text": text,
                "punishment": record.get("punishment", ""),
                "punishment_status": record.get("punishment_status") or verification.get("punishment_status") or "unverified",
                "punishment_provisions": record.get("punishment_provisions") or [],
                "keywords": record.get("keywords", []),
                "verified": verified,
                "text_status": verification.get("text_status") or "unverified",
                "verification": verification,
                "scraped_procedural_classification": scraped,
                "source": record.get("source", "Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023)"),
                "schedule_i_status": sched_status,
                "schedule_i_entry": verified_sched
            }

    def get_section(self, sec_num: int) -> Optional[Dict[str, Any]]:
        return self.sections_by_num.get(sec_num)

    def has_section(self, sec_num: int) -> bool:
        return sec_num in self.sections_by_num

    def all_sections(self) -> List[Dict[str, Any]]:
        return list(self.sections_by_num.values())

    def get_document_text(self, sec_num: int) -> str:
        sec = self.get_section(sec_num)
        if not sec:
            return ""
        keywords_str = " ".join(sec.get("keywords", []))
        # The BM25 index keeps the legacy scraped classification wording so that separating it from the
        # statutory text does not change retrieval. It is never presented as statutory text.
        scraped = sec.get("scraped_procedural_classification") or {}
        legacy = f" {scraped['text']}" if scraped.get("text") else ""
        return f"{sec['title']} {keywords_str} {sec['text']}{legacy}"

    def format_for_llm_context(self, sec_nums: List[int], max_text_chars: int = 1200) -> str:
        """Format a list of retrieved sections as high-density context for the LLM."""
        context_blocks = []
        for snum in sec_nums:
            sec = self.get_section(snum)
            if not sec:
                continue
            text = sec["text"]
            if len(text) > max_text_chars:
                text = text[:max_text_chars] + "... [Statutory text continued in official gazette]"
            
            punishment = sec.get("punishment") or PUNISHMENT_FALLBACK_LABELS.get(
                sec.get("punishment_status"), PUNISHMENT_FALLBACK_LABELS["unknown"]
            )
            text_status = TEXT_STATUS_LABELS.get(
                sec.get("text_status"), "NOT verified against the Gazette text"
            )
            # Only statutory text is presented; scraped procedural classifications are deliberately excluded.
            block = (
                f"### BNS Section {sec['section']}: {sec['title']}\n"
                f"- Chapter: {sec.get('chapter', 'N/A')}\n"
                f"- Statutory Text: {text}\n"
                f"- Text Verification: {text_status}\n"
                f"- Punishment: {punishment}\n"
                f"- Source Citation: {sec.get('source')}\n"
            )
            context_blocks.append(block)
        return "\n".join(context_blocks)
