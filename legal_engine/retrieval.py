"""
Modular Retrieval Service for BNS Legal Provisions.
Implements BM25Okapi retrieval with clean tokenization, candidate shortlisting,
and hybrid scoring readiness.
"""

import re
from typing import List, Dict, Tuple, Any, Optional
from rank_bm25 import BM25Okapi
from legal_engine.corpus import BNSCorpus


def tokenize_legal_text(text: str) -> List[str]:
    """Simple alphanumeric tokenizer tailored for English, Hindi-transliterated and legal terms."""
    if not text:
        return []
    # Lowercase and split on non-alphanumeric characters, keep words >= 2 chars
    tokens = re.findall(r'\b[a-zA-Z0-9_\-]{2,}\b', text.lower())
    return tokens


class BM25LegalRetriever:
    """Retrieval engine using BM25Okapi over verified statutory documents."""

    def __init__(self, corpus: BNSCorpus):
        self.corpus = corpus
        self.section_numbers: List[int] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25: Optional[BM25Okapi] = None
        self._build_index()

    def _build_index(self):
        self.section_numbers = []
        self.tokenized_corpus = []

        for sec in self.corpus.all_sections():
            doc_str = self.corpus.get_document_text(sec["section"])
            tokens = tokenize_legal_text(doc_str)
            if tokens:
                self.section_numbers.append(sec["section"])
                self.tokenized_corpus.append(tokens)

        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        min_raw_score: float = 0.0,
        relative_threshold: float = 0.35,
        max_candidates: Optional[int] = None
    ) -> List[Tuple[int, float]]:
        """
        Retrieves relevant BNS sections for the given query using dynamic thresholding.
        Returns a list of tuples: (section_number, normalized_score).
        
        Dynamic candidate selection rules:
        - Drops candidates with zero or negative raw BM25 score (or below min_raw_score if specified).
        - Avoids fixed top-k padding: prunes candidates whose score ratio relative to the
          top candidate drops below relative_threshold, preventing irrelevant tail candidates.
        - Guarantees the primary candidate if raw score meets min_raw_score.
        - Explicitly treats normalized scores as lexical relevance rankings, NOT calibrated probabilities.
        """
        if not self.bm25 or not query:
            return []

        tokens = tokenize_legal_text(query)
        if not tokens:
            return []

        raw_scores = self.bm25.get_scores(tokens)
        
        # Pair section numbers with raw BM25 scores
        scored_pairs = list(zip(self.section_numbers, raw_scores))
        
        # Sort descending by BM25 score
        scored_pairs.sort(key=lambda x: x[1], reverse=True)

        effective_floor = max(min_raw_score, 0.0001)
        if not scored_pairs or scored_pairs[0][1] < effective_floor:
            return []

        max_score = scored_pairs[0][1]
        effective_limit = min(top_k, max_candidates) if max_candidates else top_k

        normalized_results: List[Tuple[int, float]] = []
        for snum, raw_score in scored_pairs:
            if raw_score < effective_floor:
                break
            # Retain if meets relative score threshold or is the guaranteed top candidate
            if (raw_score / max_score) >= relative_threshold or len(normalized_results) < 1:
                norm = round(min(raw_score / max_score, 1.0), 4)
                normalized_results.append((snum, norm))
                if len(normalized_results) >= effective_limit:
                    break

        return normalized_results


    def retrieve_clause_level(
        self,
        text: str,
        min_raw_score: float = 2.5,
        relative_threshold: float = 0.35,
        max_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Retrieves candidates across the global narrative and individual action clauses.
        Prevents a dominant primary offence from drowning out secondary provisions
        in compound, multi-action complaints.
        """
        if not text or not self.bm25:
            return []

        # 1. Global retrieval across the full complaint
        global_candidates = self.retrieve(
            text,
            top_k=max_k,
            min_raw_score=min_raw_score,
            relative_threshold=relative_threshold,
            max_candidates=max_k
        )
        candidate_scores: Dict[int, float] = {snum: score for snum, score in global_candidates}

        # 2. Segment narrative into clauses/sentences
        delims = r'(?:[.!?;:\n]+|,\s*(?:and|aur|lekin|while|also)\s+|\b(?:and\s+then|after\s+that|aur\s+phir|aur\s+jab|aur\s+uske\s+baad|before\s+leaving|in\s+addition|subsequently)\b)'
        parts = re.split(delims, text, flags=re.IGNORECASE)
        clauses = [p.strip() for p in parts if len(p.strip().split()) >= 3]

        # 3. Clause-level retrieval to surface secondary provisions
        if len(clauses) > 1:
            for cl in clauses:
                cl_candidates = self.retrieve(
                    cl,
                    top_k=3,
                    min_raw_score=min_raw_score,
                    relative_threshold=0.50,
                    max_candidates=3
                )
                for snum, score in cl_candidates:
                    # Merge uniquely by maximum normalized relevance
                    candidate_scores[snum] = max(candidate_scores.get(snum, 0.0), score)

        # Sort merged candidates descending by score and cap at max_k
        merged_sorted = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        return merged_sorted[:max_k]

