#!/usr/bin/env python3
"""
Reproducible Evaluation Runner for Bandhoo BNS Legal Classification Benchmark.

Evaluates either:
  1. Deterministic BM25 Fallback (--mode fallback)
  2. Live Gemini LLM inference with local JSON caching (--mode live)

Strict constraints:
  - Never prints API keys or secrets.
  - Never labels fallback outputs as successful Gemini inference.
  - Explicitly separates genuine live responses from cached responses.
  - Reports detailed metrics across legal, procedural, fact-separation, and negation dimensions.
  - Computes exact numerators, denominators, micro/macro averages, and F1 scores.
  - Generates structured error analysis.
"""

import argparse
import datetime
import json
import os
import re
import sys
import time
from typing import Dict, List, Any, Optional, Tuple

# Ensure repository root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

from legal_engine.corpus import BNSCorpus
from legal_engine.retrieval import BM25LegalRetriever
from legal_engine.llm_client import GeminiLegalClient, LLMUnavailableError, LLMInferenceError
from legal_engine.service import LegalAnalysisService
from legal_engine.schemas import NarrativeInput, OffenceClassificationResponse

PROVISIONAL_REVIEW_STATUS = "provisional_pending_legal_review"
EVALUATED_REVIEW_STATUSES = {"verified_authoritative", PROVISIONAL_REVIEW_STATUS}

# Same candidate retrieval parameters as LegalAnalysisService.analyze_complaint.
PRODUCTION_RETRIEVAL_PARAMS = {"min_raw_score": 0.0, "relative_threshold": 0.35, "max_k": 8}


class BenchmarkEvaluator:
    def __init__(
        self,
        benchmark_path: str,
        mode: str = "fallback",
        cache_dir: Optional[str] = None,
        limit: Optional[int] = None
    ):
        self.benchmark_path = benchmark_path
        self.mode = mode.lower()
        if self.mode not in ("fallback", "live"):
            raise ValueError(f"Invalid mode '{mode}'. Choose 'fallback' or 'live'.")

        self.cache_dir = cache_dir or os.path.join(BASE_DIR, "benchmark", "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.limit = limit

        self.corpus = BNSCorpus()
        self.retriever = BM25LegalRetriever(self.corpus)

        self._last_call_source = None
        self._current_case_id_holder = {"case_id": None}

        # Setup LLM client according to mode
        if self.mode == "live":
            # Real client loaded from environment (never print secrets)
            self.llm_client = GeminiLegalClient()
            if not self.llm_client.is_available:
                print("[WARNING] GEMINI_API_KEY not configured or client unavailable. Live mode may fall back.")
            self.model_identifier = f"Google Gemini API ({self.llm_client.model_name})"
        else:
            # Explicitly disabled client for deterministic fallback
            self.llm_client = GeminiLegalClient(api_key="")
            self.llm_client._client = None
            self.model_identifier = "Deterministic BM25 Fallback"

        # Intercept LLM calls for caching and provenance tracking in live mode
        self._wrap_client_with_cache()
        self.service = LegalAnalysisService(
            corpus=self.corpus,
            retriever=self.retriever,
            llm_client=self.llm_client
        )

    def _wrap_client_with_cache(self):
        """Wraps evaluate_complaint to use local JSON cache in live mode and track call provenance."""
        if self.mode != "live":
            return

        original_evaluate = self.llm_client.evaluate_complaint

        def cached_evaluate(narrative: str, context_str: str) -> Dict[str, Any]:
            cid = self._current_case_id_holder["case_id"]
            if not cid:
                self._last_call_source = "genuine_live"
                return original_evaluate(narrative, context_str)

            cache_file = os.path.join(self.cache_dir, f"{cid}.json")
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cached_data = json.load(f)
                    self._last_call_source = "cached_live"
                    return cached_data
                except Exception as e:
                    print(f"[{cid}] Cache read error: {e}, falling back to live API")

            # Call live Gemini API with conservative rate limiting
            time.sleep(1.0)
            self._last_call_source = "genuine_live"
            result = original_evaluate(narrative, context_str)
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"[{cid}] Warning: Failed to write cache: {e}")

            return result

        self.llm_client.evaluate_complaint = cached_evaluate

    def run_evaluation(self) -> Dict[str, Any]:
        with open(self.benchmark_path, "r", encoding="utf-8") as f:
            all_cases = json.load(f)

        if self.limit:
            all_cases = all_cases[:self.limit]

        evaluation_date = datetime.datetime.now(datetime.timezone.utc).isoformat()
        results: List[Dict[str, Any]] = []
        excluded_cases: List[Dict[str, str]] = []
        errors: List[Dict[str, Any]] = []

        # Metric accumulators
        total_predictions_count = 0
        true_positives = 0
        false_positives = 0
        total_relevant_sections = 0
        relevant_sections_retrieved = 0

        contradicted_cases_count = 0
        contradicted_false_positives = 0

        attempt_cases_count = 0
        attempt_correct_count = 0

        negation_cases_count = 0
        negation_success_count = 0

        misleading_keyword_cases_count = 0
        misleading_success_count = 0

        fact_separation_cases_count = 0
        fact_separation_success_count = 0

        uncertainty_cases_count = 0
        uncertainty_success_count = 0

        schedule_eval_count = 0
        schedule_correct_count = 0

        failed_requests_count = 0
        malformed_outputs_count = 0

        genuine_live_success_count = 0
        cached_live_count = 0
        fallback_activations_count = 0

        print(f"\n=======================================================")
        print(f"  RUNNING BNS CLASSIFICATION BENCHMARK EVALUATION")
        print(f"  Mode: {self.mode.upper()} | Model: {self.model_identifier}")
        print(f"  Cases: {len(all_cases)} | Path: {self.benchmark_path}")
        print(f"=======================================================\n")

        for idx, case in enumerate(all_cases, 1):
            cid = case["case_id"]
            if case.get("review_status") not in EVALUATED_REVIEW_STATUSES:
                excluded_cases.append({
                    "case_id": cid,
                    "reason": f"Review status is '{case.get('review_status')}', not an evaluated status."
                })
                continue

            if self.mode == "live":
                self._current_case_id_holder["case_id"] = cid

            narrative = case["narrative"]
            expected_sections = set(case.get("relevant_candidate_sections", []))
            plausible_sections = set(case.get("plausible_alternatives", []))
            contradicted_sections = set(case.get("contradicted_sections", []))
            classification_type = case.get("classification_type", "A")

            t0 = time.time()
            self._last_call_source = None
            try:
                res = self.service.analyze_complaint(NarrativeInput(narrative=narrative))
                elapsed = time.time() - t0
            except Exception as e:
                elapsed = time.time() - t0
                failed_requests_count += 1
                actual_mode = "error"
                print(f"[{cid}] FAILED: {e}")
                errors.append({
                    "case_id": cid,
                    "expected_behavior": f"Execution of sections {list(expected_sections)}",
                    "actual_behavior": f"Exception raised: {str(e)}",
                    "error_category": "pipeline_exception",
                    "likely_root_cause": str(e),
                    "suggested_general_correction": "Inspect input validation and error handling."
                })
                continue

            # Verify that fallback is never mislabeled as live Gemini
            inference_status = getattr(res, "inference_status", "unspecified")
            is_fallback = inference_status.startswith("fallback") or "Fallback" in (res.model or "")
            if self.mode == "live":
                if is_fallback:
                    actual_mode = "fallback_on_llm_failure" if inference_status == "fallback_llm_failed" else inference_status
                    fallback_activations_count += 1
                elif getattr(self, "_last_call_source", None) == "cached_live":
                    actual_mode = "cached_live"
                    cached_live_count += 1
                else:
                    actual_mode = "genuine_live"
                    genuine_live_success_count += 1
            else:
                actual_mode = "deterministic_fallback"

            predicted_sections = [p.section for p in res.predictions]
            pred_scores = {p.section: p.score for p in res.predictions}

            # ── 1. Section Precision & Recall ──
            # Valid positives include relevant sections AND plausible alternatives
            acceptable_target_pool = expected_sections.union(plausible_sections)

            case_tp = 0
            case_fp = 0
            for sec in predicted_sections:
                if sec in acceptable_target_pool:
                    case_tp += 1
                else:
                    case_fp += 1

            true_positives += case_tp
            false_positives += case_fp
            total_predictions_count += len(predicted_sections)

            # Recall measures recovery of strictly relevant ground-truth sections
            case_relevant_found = 0
            for sec in expected_sections:
                total_relevant_sections += 1
                if sec in predicted_sections:
                    relevant_sections_retrieved += 1
                    case_relevant_found += 1

            case_prec = round(case_tp / len(predicted_sections), 4) if predicted_sections else (1.0 if not expected_sections else 0.0)
            case_rec = round(case_relevant_found / len(expected_sections), 4) if expected_sections else 1.0
            case_f1 = round(2 * case_prec * case_rec / (case_prec + case_rec), 4) if (case_prec + case_rec) > 0 else 0.0

            # ── 2. Contradiction Violation Check ──
            case_contradicted_fp = False
            if contradicted_sections:
                contradicted_cases_count += 1
                for csec in contradicted_sections:
                    if csec in predicted_sections and pred_scores.get(csec, 0.0) > 0.0:
                        contradicted_false_positives += 1
                        case_contradicted_fp = True
                        errors.append({
                            "case_id": cid,
                            "expected_behavior": f"Section {csec} must be excluded/zeroed due to explicit contradiction",
                            "actual_behavior": f"Section {csec} returned with score {pred_scores.get(csec)}",
                            "error_category": "validation_miss",
                            "likely_root_cause": "Element contradiction filter did not suppress section.",
                            "suggested_general_correction": "Refine statutory contradiction rules in _validate_candidate_elements."
                        })

            # ── 3. Attempt Handling Check ──
            is_attempt_case = case.get("expected_attempt", False)
            attempt_ok = True
            if is_attempt_case:
                attempt_cases_count += 1
                has_attempt_flag = (
                    62 in predicted_sections
                    or any("attempt" in p.reasoning.lower() for p in res.predictions)
                    or "attempt" in res.recommended_action.lower()
                    or any("attempt" in s.lower() for s in (res.facts_analysis.stated_facts if res.facts_analysis else []))
                )
                if has_attempt_flag:
                    attempt_correct_count += 1
                else:
                    attempt_ok = False
                    errors.append({
                        "case_id": cid,
                        "expected_behavior": "Attempted offence (Section 62) identified",
                        "actual_behavior": "Treated as completed offence or Section 62 omitted",
                        "error_category": "model_reasoning_gap",
                        "likely_root_cause": "Interrupted execution not tagged as Section 62 attempt.",
                        "suggested_general_correction": "Add attempt detection hook in retrieval/reasoning pipeline."
                    })

            # ── 4. Explicit Negation Handling Check ──
            if case.get("category") == "explicit_negation":
                negation_cases_count += 1
                # Must exclude Section 309
                if 309 not in predicted_sections or pred_scores.get(309, 0) == 0.0:
                    negation_success_count += 1
                else:
                    errors.append({
                        "case_id": cid,
                        "expected_behavior": "Section 309 strictly excluded after explicit negation of force/weapons",
                        "actual_behavior": f"Section 309 predicted with score {pred_scores.get(309)}",
                        "error_category": "validation_miss",
                        "likely_root_cause": "Negation pattern failed to suppress Section 309 candidate.",
                        "suggested_general_correction": "Ensure clean_text strips all negated clauses before element evaluation."
                    })

            # ── 5. Misleading Keywords Immunity Check ──
            if case.get("category") == "misleading_keywords":
                misleading_keyword_cases_count += 1
                # Must NOT return penal sections 303, 304, 309 for non-penal metaphorical complaints
                penal_hits = [s for s in (303, 304, 309) if s in predicted_sections and pred_scores.get(s, 0) > 0.35]
                if not penal_hits:
                    misleading_success_count += 1
                else:
                    errors.append({
                        "case_id": cid,
                        "expected_behavior": "Non-penal / metaphorical grievance rejected; no theft/robbery/snatching predicted",
                        "actual_behavior": f"Predicted penal sections: {penal_hits}",
                        "error_category": "retrieval_failure",
                        "likely_root_cause": "Colloquial metaphor triggered BM25 keyword matching.",
                        "suggested_general_correction": "Add intent filter for consumer pricing and corporate non-penal grievances."
                    })

            # ── 6. Fact/Inference Separation Check ──
            fact_separation_cases_count += 1
            has_facts_block = res.facts_analysis is not None
            has_separation = False
            if has_facts_block:
                stated = res.facts_analysis.stated_facts or []
                inferred = res.facts_analysis.inferred_facts or []
                if stated or inferred:
                    overlap = set(stated).intersection(set(inferred))
                    has_separation = len(overlap) == 0

            if has_separation:
                fact_separation_success_count += 1

            # ── 7. Uncertainty & Missing Facts Handling ──
            if classification_type in ("B", "D"):
                uncertainty_cases_count += 1
                rec_action = res.recommended_action or ""
                missing = res.facts_analysis.missing_facts_to_clarify if res.facts_analysis else []
                # Engine must express uncertainty via qualification, NCR mention, missing facts, or brief note
                expresses_uncertainty = (
                    len(missing) > 0
                    or "conditional" in rec_action.lower()
                    or "unverified" in rec_action.lower()
                    or "clarif" in rec_action.lower()
                    or "preliminary enquiry" in rec_action.lower()
                    or "preliminary classification" in rec_action.lower()
                    or "preliminary analysis" in rec_action.lower()
                    or "too brief" in rec_action.lower()
                    or "ncr" in rec_action.lower()
                    or "magistrate" in rec_action.lower()
                )
                if expresses_uncertainty:
                    uncertainty_success_count += 1
                else:
                    errors.append({
                        "case_id": cid,
                        "expected_behavior": "Appropriate expression of legal uncertainty / missing material facts",
                        "actual_behavior": "Unconditional procedural recommendation produced without qualifying missing facts",
                        "error_category": "model_reasoning_gap",
                        "likely_root_cause": "Engine failed to flag conditional nature of narrative.",
                        "suggested_general_correction": "Ensure missing property values or civil disputes qualify the action text."
                    })

            # ── 8. Procedural Recommendation Correctness (Verified metadata only) ──
            schedule_eval_match = True
            schedule_evaluated = False
            if case.get("verified_schedule_applicable") and case.get("expected_cognizable") is not None:
                schedule_evaluated = True
                schedule_eval_count += 1
                exp_cog = case["expected_cognizable"]
                exp_bail = case["expected_bailable"]

                if res.predictions:
                    top_pred = res.predictions[0]
                    act_cog = top_pred.is_cognizable
                    act_bail = top_pred.is_bailable
                    if act_cog == exp_cog and act_bail == exp_bail:
                        schedule_correct_count += 1
                    else:
                        schedule_eval_match = False
                        errors.append({
                            "case_id": cid,
                            "expected_behavior": f"Procedural metadata: Cognizable={exp_cog}, Bailable={exp_bail}",
                            "actual_behavior": f"Top section {top_pred.section} returned Cognizable={act_cog}, Bailable={act_bail}",
                            "error_category": "procedural_metadata_mismatch",
                            "likely_root_cause": "Schedule I resolution logic produced differing classification.",
                            "suggested_general_correction": "Check schedule_registry.py and conditionality handling in _determine_schedule_metadata."
                        })
                else:
                    schedule_eval_match = False

            # ── 9. Pure Retrieval Candidate Evaluation (at k=3, 5, 8, 10) ──
            trans_query, _ = self.service.translate_synonyms(narrative)
            raw_retrieved = self.retriever.retrieve(trans_query, top_k=10)
            raw_sec_nums = [s for s, _ in raw_retrieved]

            cand_hits_3 = len(expected_sections.intersection(raw_sec_nums[:3]))
            cand_hits_5 = len(expected_sections.intersection(raw_sec_nums[:5]))
            cand_hits_8 = len(expected_sections.intersection(raw_sec_nums[:8]))
            cand_hits_10 = len(expected_sections.intersection(raw_sec_nums[:10]))

            # Candidate pool actually used by the service (clause-level retrieval, max 8)
            prod_retrieved = self.retriever.retrieve_clause_level(trans_query, **PRODUCTION_RETRIEVAL_PARAMS)
            prod_sec_nums = [s for s, _ in prod_retrieved]
            prod_cand_hits = len(expected_sections.intersection(prod_sec_nums))

            cand_tp_3 = len(acceptable_target_pool.intersection(raw_sec_nums[:3]))
            cand_tp_5 = len(acceptable_target_pool.intersection(raw_sec_nums[:5]))
            cand_tp_8 = len(acceptable_target_pool.intersection(raw_sec_nums[:8]))
            cand_tp_10 = len(acceptable_target_pool.intersection(raw_sec_nums[:10]))

            # ── 10. Non-Penal Grievance Gate Evaluation ──
            is_ground_truth_non_penal = (len(expected_sections) == 0)
            is_gate_fired = (
                len(predicted_sections) == 0
                and (
                    "preliminary" in (res.recommended_action or "").lower()
                    or "pricing" in (res.recommended_action or "").lower()
                    or "grievance" in (res.recommended_action or "").lower()
                    or "too brief" in (res.recommended_action or "").lower()
                )
            )
            gate_fp = (not is_ground_truth_non_penal and is_gate_fired)
            gate_fn = (is_ground_truth_non_penal and not is_gate_fired)

            # Check for low recall errors
            if case_rec < 0.5 and expected_sections:
                errors.append({
                    "case_id": cid,
                    "expected_behavior": f"Predict sections {list(expected_sections)}",
                    "actual_behavior": f"Predicted {predicted_sections}",
                    "error_category": "retrieval_failure" if not any(s in raw_sec_nums for s in expected_sections) else "model_reasoning_gap",
                    "likely_root_cause": "Target section was not retrieved by BM25 or pruned by model reasoning.",
                    "suggested_general_correction": "Examine vocabulary alignment and synonyms for Hindi/Hinglish."
                })

            status_str = "OK" if (case_prec >= 0.5 and case_rec >= 0.5 and not case_contradicted_fp) else "REVIEW"
            print(f"[{cid}] Type {classification_type} | Mode: {actual_mode:<16} | Prec: {case_prec:.2f} | Rec: {case_rec:.2f} | Status: {status_str} ({elapsed:.2f}s)")

            results.append({
                "case_id": cid,
                "review_status": case.get("review_status"),
                "is_provisional": case.get("review_status") == PROVISIONAL_REVIEW_STATUS,
                "has_label_review_notes": bool(case.get("label_review_notes")),
                "category": case["category"],
                "language": case["language"],
                "classification_type": classification_type,
                "expected_sections": list(expected_sections),
                "plausible_sections": list(plausible_sections),
                "contradicted_sections": list(contradicted_sections),
                "predicted_sections": predicted_sections,
                "pred_scores": pred_scores,
                "raw_retrieved_sections": raw_sec_nums,
                "precision": case_prec,
                "recall": case_rec,
                "f1": case_f1,
                "tp": case_tp,
                "fp": case_fp,
                "total_pred": len(predicted_sections),
                "expected_count": len(expected_sections),
                "relevant_found": case_relevant_found,
                "contradicted_fp": case_contradicted_fp,
                "attempt_ok": attempt_ok,
                "schedule_match": schedule_eval_match,
                "schedule_evaluated": schedule_evaluated,
                "production_candidates": prod_sec_nums,
                "production_cand_hits": prod_cand_hits,
                "cand_hits_3": cand_hits_3,
                "cand_hits_5": cand_hits_5,
                "cand_hits_8": cand_hits_8,
                "cand_hits_10": cand_hits_10,
                "cand_tp_3": cand_tp_3,
                "cand_tp_5": cand_tp_5,
                "cand_tp_8": cand_tp_8,
                "cand_tp_10": cand_tp_10,
                "raw_cand_count": len(raw_sec_nums),
                "is_ground_truth_non_penal": is_ground_truth_non_penal,
                "is_gate_fired": is_gate_fired,
                "gate_fp": gate_fp,
                "gate_fn": gate_fn,
                "elapsed_sec": round(elapsed, 3),
                "actual_mode": actual_mode,
                "inference_status": "cached_llm_response" if actual_mode == "cached_live" else inference_status,
                "is_fallback": is_fallback
            })

        # Load splits if available
        splits_file = os.path.join(BASE_DIR, "benchmark", "dataset_splits.json")
        dev_ids = set()
        holdout_ids = set()
        if os.path.exists(splits_file):
            with open(splits_file, "r", encoding="utf-8") as f:
                s_data = json.load(f)
                dev_ids = set(s_data.get("dev_ids", []))
                holdout_ids = set(s_data.get("holdout_ids", []))

        def compute_group_metrics(case_list: List[Dict[str, Any]]) -> Dict[str, Any]:
            if not case_list:
                return {}
            tot_pred = sum(c["total_pred"] for c in case_list)
            tp_sum = sum(c["tp"] for c in case_list)
            fp_sum = sum(c["fp"] for c in case_list)
            exp_sum = sum(c["expected_count"] for c in case_list)
            rel_found_sum = sum(c["relevant_found"] for c in case_list)

            # Micro-averaged metrics
            micro_prec = round(tp_sum / tot_pred, 4) if tot_pred > 0 else 0.0
            micro_rec = round(rel_found_sum / exp_sum, 4) if exp_sum > 0 else 0.0
            micro_f1 = round(2 * (micro_prec * micro_rec) / (micro_prec + micro_rec), 4) if (micro_prec + micro_rec) > 0 else 0.0

            # Macro-averaged metrics
            macro_prec = round(sum(c["precision"] for c in case_list) / len(case_list), 4) if case_list else 0.0
            macro_rec = round(sum(c["recall"] for c in case_list) / len(case_list), 4) if case_list else 0.0
            macro_f1 = round(sum(c["f1"] for c in case_list) / len(case_list), 4) if case_list else 0.0

            # Retrieval Recall@k & Candidate Precision@k
            r_hits_3 = sum(c["cand_hits_3"] for c in case_list)
            r_hits_5 = sum(c["cand_hits_5"] for c in case_list)
            r_hits_8 = sum(c["cand_hits_8"] for c in case_list)
            r_hits_10 = sum(c["cand_hits_10"] for c in case_list)

            cand_tp_3_sum = sum(c["cand_tp_3"] for c in case_list)
            cand_tp_5_sum = sum(c["cand_tp_5"] for c in case_list)
            cand_tp_8_sum = sum(c["cand_tp_8"] for c in case_list)
            cand_tp_10_sum = sum(c.get("cand_tp_10", 0) for c in case_list)

            # Actual candidates returned by dynamic retriever up to cutoff k
            cand_total_3 = sum(min(3, c["raw_cand_count"]) for c in case_list)
            cand_total_5 = sum(min(5, c["raw_cand_count"]) for c in case_list)
            cand_total_8 = sum(min(8, c["raw_cand_count"]) for c in case_list)
            cand_total_10 = sum(min(10, c["raw_cand_count"]) for c in case_list)

            # Fixed-slot theoretical capacity (k * N_cases)
            fixed_cand_total_3 = 3 * len(case_list)
            fixed_cand_total_5 = 5 * len(case_list)
            fixed_cand_total_8 = 8 * len(case_list)
            fixed_cand_total_10 = 10 * len(case_list)

            contra_cases = [c for c in case_list if len(c["contradicted_sections"]) > 0]
            contra_fp_count = sum(1 for c in contra_cases if c["contradicted_fp"])

            # Grievance gate counts in this group
            penal_cases_count = sum(1 for c in case_list if not c["is_ground_truth_non_penal"])
            non_penal_cases_count = sum(1 for c in case_list if c["is_ground_truth_non_penal"])
            gate_fp_cases = [c["case_id"] for c in case_list if c["gate_fp"]]
            gate_fn_cases = [c["case_id"] for c in case_list if c["gate_fn"]]
            gate_fp_count = len(gate_fp_cases)
            gate_fn_count = len(gate_fn_cases)

            # Type C pure non-penal grievance cases (misleading keywords / figurative / commercial)
            type_c_cases = [c for c in case_list if c["category"] == "misleading_keywords"]
            type_c_fn_cases = [c["case_id"] for c in type_c_cases if c["gate_fn"]]
            type_c_fn_rate = round(len(type_c_fn_cases) / len(type_c_cases), 4) if type_c_cases else 0.0

            gate_fp_rate = round(gate_fp_count / penal_cases_count, 4) if penal_cases_count > 0 else 0.0
            gate_fn_rate = round(gate_fn_count / non_penal_cases_count, 4) if non_penal_cases_count > 0 else 0.0

            prod_hits = sum(c["production_cand_hits"] for c in case_list)
            prod_cand_total = sum(len(c["production_candidates"]) for c in case_list)
            sched_cases = [c for c in case_list if c["schedule_evaluated"]]
            sched_correct = sum(1 for c in sched_cases if c["schedule_match"])

            return {
                "case_count": len(case_list),
                "counts_and_denominators": {
                    "production_candidate_hits": prod_hits,
                    "production_candidates_returned": prod_cand_total,
                    "schedule_evaluated_cases": len(sched_cases),
                    "schedule_correct_cases": sched_correct,
                    "total_predictions": tot_pred,
                    "true_positives": tp_sum,
                    "false_positives": fp_sum,
                    "ground_truth_relevant_sections": exp_sum,
                    "relevant_sections_retrieved_in_final": rel_found_sum,
                    "retrieval_hits_at_3": r_hits_3,
                    "retrieval_hits_at_5": r_hits_5,
                    "retrieval_hits_at_8": r_hits_8,
                    "retrieval_hits_at_10": r_hits_10,
                    "candidate_tp_at_3": cand_tp_3_sum,
                    "candidate_total_at_3": cand_total_3,
                    "fixed_slot_candidate_total_at_3": fixed_cand_total_3,
                    "candidate_tp_at_5": cand_tp_5_sum,
                    "candidate_total_at_5": cand_total_5,
                    "fixed_slot_candidate_total_at_5": fixed_cand_total_5,
                    "candidate_tp_at_8": cand_tp_8_sum,
                    "candidate_total_at_8": cand_total_8,
                    "fixed_slot_candidate_total_at_8": fixed_cand_total_8,
                    "candidate_tp_at_10": cand_tp_10_sum,
                    "candidate_total_at_10": cand_total_10,
                    "fixed_slot_candidate_total_at_10": fixed_cand_total_10,
                    "cases_with_contradictions": len(contra_cases),
                    "contradicted_false_positive_cases": contra_fp_count,
                    "penal_cases_for_gate": penal_cases_count,
                    "gate_false_positives": gate_fp_count,
                    "gate_false_positive_case_ids": gate_fp_cases,
                    "non_penal_cases_for_gate": non_penal_cases_count,
                    "gate_false_negatives": gate_fn_count,
                    "gate_false_negative_case_ids": gate_fn_cases,
                    "type_c_non_penal_cases": len(type_c_cases),
                    "type_c_false_negatives": len(type_c_fn_cases),
                    "type_c_false_negative_case_ids": type_c_fn_cases
                },
                "retrieval_recall_at_3": round(r_hits_3 / exp_sum, 4) if exp_sum > 0 else 0.0,
                "retrieval_recall_at_5": round(r_hits_5 / exp_sum, 4) if exp_sum > 0 else 0.0,
                "retrieval_recall_at_8": round(r_hits_8 / exp_sum, 4) if exp_sum > 0 else 0.0,
                "retrieval_recall_at_10": round(r_hits_10 / exp_sum, 4) if exp_sum > 0 else 0.0,
                "production_candidate_recall": round(prod_hits / exp_sum, 4) if exp_sum > 0 else 0.0,
                "procedural_correctness_rate_verified_only": round(sched_correct / len(sched_cases), 4) if sched_cases else 0.0,
                "candidate_precision_at_3": round(cand_tp_3_sum / cand_total_3, 4) if cand_total_3 > 0 else 0.0,
                "candidate_precision_at_5": round(cand_tp_5_sum / cand_total_5, 4) if cand_total_5 > 0 else 0.0,
                "candidate_precision_at_8": round(cand_tp_8_sum / cand_total_8, 4) if cand_total_8 > 0 else 0.0,
                "candidate_precision_at_10": round(cand_tp_10_sum / cand_total_10, 4) if cand_total_10 > 0 else 0.0,
                "candidate_precision_fixed_k_n_at_3": round(cand_tp_3_sum / fixed_cand_total_3, 4) if fixed_cand_total_3 > 0 else 0.0,
                "candidate_precision_fixed_k_n_at_5": round(cand_tp_5_sum / fixed_cand_total_5, 4) if fixed_cand_total_5 > 0 else 0.0,
                "candidate_precision_fixed_k_n_at_8": round(cand_tp_8_sum / fixed_cand_total_8, 4) if fixed_cand_total_8 > 0 else 0.0,
                "candidate_precision_fixed_k_n_at_10": round(cand_tp_10_sum / fixed_cand_total_10, 4) if fixed_cand_total_10 > 0 else 0.0,
                "final_prediction_precision_micro": micro_prec,
                "final_prediction_recall_micro": micro_rec,
                "final_prediction_f1_micro": micro_f1,
                "final_prediction_precision_macro": macro_prec,
                "final_prediction_recall_macro": macro_rec,
                "final_prediction_f1_macro": macro_f1,
                # Backward-compatible fields
                "final_prediction_precision": micro_prec,
                "final_prediction_recall": micro_rec,
                "final_prediction_f1": micro_f1,
                "unsupported_section_rate": round(fp_sum / tot_pred, 4) if tot_pred > 0 else 0.0,
                "contradicted_fp_rate": round(contra_fp_count / len(contra_cases), 4) if contra_cases else 0.0,
                "gate_false_positive_rate": gate_fp_rate,
                "gate_false_negative_rate": gate_fn_rate,
                "type_c_gate_false_negative_rate": type_c_fn_rate
            }

        overall_metrics = compute_group_metrics(results)
        non_provisional_cases = [c for c in results if not c["is_provisional"]]
        provisional_cases = [c for c in results if c["is_provisional"]]
        overall_excl_provisional_metrics = compute_group_metrics(non_provisional_cases)
        provisional_only_metrics = compute_group_metrics(provisional_cases)
        dev_cases = [c for c in results if c["case_id"] in dev_ids]
        holdout_cases = [c for c in results if c["case_id"] in holdout_ids]

        dev_metrics = compute_group_metrics(dev_cases)
        holdout_metrics = compute_group_metrics(holdout_cases)

        # Breakdown by language
        by_language = {}
        for lang in ("English", "Hindi", "Hinglish"):
            l_cases = [c for c in results if c["language"] == lang]
            by_language[lang] = compute_group_metrics(l_cases)

        # Automated verification of metric identities and reconciliation sums across partitions
        self._verify_metric_identities(
            overall_metrics, dev_metrics, holdout_metrics, by_language,
            overall_excl_provisional_metrics, provisional_only_metrics
        )

        # Breakdown by key scenarios
        compound_cases = [c for c in results if c["category"] == "compound_offence"]
        compound_metrics = compute_group_metrics(compound_cases)
        compound_exp = sum(c["expected_count"] for c in compound_cases)
        compound_found = sum(c["relevant_found"] for c in compound_cases)
        compound_section_recall = round(compound_found / compound_exp, 4) if compound_exp > 0 else 0.0
        compound_complete_cases = sum(1 for c in compound_cases if c["relevant_found"] == c["expected_count"] and c["expected_count"] > 0)
        compound_case_completion_rate = round(compound_complete_cases / len(compound_cases), 4) if compound_cases else 0.0

        misleading_cases = [c for c in results if c["category"] == "misleading_keywords"]
        misleading_metrics = compute_group_metrics(misleading_cases)

        attempt_correctness_rate = round(attempt_correct_count / attempt_cases_count, 4) if attempt_cases_count > 0 else 1.0
        negation_immunity_rate = round(negation_success_count / negation_cases_count, 4) if negation_cases_count > 0 else 1.0
        misleading_immunity_rate = round(misleading_success_count / misleading_keyword_cases_count, 4) if misleading_keyword_cases_count > 0 else 1.0
        fact_separation_rate = round(fact_separation_success_count / fact_separation_cases_count, 4) if fact_separation_cases_count > 0 else 0.0
        uncertainty_handling_rate = round(uncertainty_success_count / uncertainty_cases_count, 4) if uncertainty_cases_count > 0 else 1.0
        procedural_correctness_rate = round(schedule_correct_count / schedule_eval_count, 4) if schedule_eval_count > 0 else 0.0

        # Disaggregated live metrics
        live_cases_genuine = [c for c in results if c.get("actual_mode") == "genuine_live"]
        live_cases_cached = [c for c in results if c.get("actual_mode") == "cached_live"]
        live_fallback_cases = [c for c in results if c.get("actual_mode", "").startswith("fallback")]

        genuine_live_metrics = compute_group_metrics(live_cases_genuine)
        cached_live_metrics = compute_group_metrics(live_cases_cached)

        # Non-penal grievance gate totals across entire evaluated set
        total_penal = sum(1 for c in results if not c["is_ground_truth_non_penal"])
        total_non_penal = sum(1 for c in results if c["is_ground_truth_non_penal"])
        all_gate_fp_cases = [c["case_id"] for c in results if c["gate_fp"]]
        all_gate_fn_cases = [c["case_id"] for c in results if c["gate_fn"]]
        total_gate_fp = len(all_gate_fp_cases)
        total_gate_fn = len(all_gate_fn_cases)
        gate_fp_rate_overall = round(total_gate_fp / total_penal, 4) if total_penal > 0 else 0.0
        gate_fn_rate_overall = round(total_gate_fn / total_non_penal, 4) if total_non_penal > 0 else 0.0

        report = {
            "metadata": {
                "benchmark_version": "1.1",
                "evaluation_date_utc": evaluation_date,
                "evaluation_mode": self.mode,
                "model_identifier": self.model_identifier,
                "total_cases_evaluated": len(results),
                "total_cases_excluded": len(excluded_cases),
                "cases_attempted": len(results),
                "successful_genuine_live_responses": genuine_live_success_count,
                "cached_responses_used": cached_live_count,
                "fallback_activations": fallback_activations_count,
                "failed_requests": failed_requests_count,
                "malformed_outputs": malformed_outputs_count,
                "inference_status_counts": {
                    status: sum(1 for c in results if c["inference_status"] == status)
                    for status in sorted({c["inference_status"] for c in results})
                },
                "held_out_inspection_status": "previously_inspected",
                "provisional_ground_truth_cases": [c["case_id"] for c in provisional_cases],
                "cases_with_label_review_notes": [c["case_id"] for c in results if c["has_label_review_notes"]],
                "provisional_labels_note": (
                    "Cases with review_status 'provisional_pending_legal_review' have statutory labels pending qualified "
                    "legal review. Their labels are unchanged. 'overall_metrics' includes them; "
                    "'overall_metrics_excluding_provisional' excludes them."
                ),
                "review_status_note": (
                    "'verified_authoritative' is the original status assigned when the synthetic benchmark was built. "
                    "No case has a documented review by a qualified legal professional; see label_review_notes in the "
                    "benchmark file for documented label concerns."
                ),
                "service_limitations_and_notes": (
                    "Deterministic BM25 fallback is fully reproducible offline. "
                    "Google Gemini Live API mode is subject to upstream 503 high-demand / quota limits; "
                    "fallbacks are recorded separately and never counted as live responses."
                )
            },
            "excluded_cases": excluded_cases,
            "overall_metrics": overall_metrics,
            "overall_metrics_excluding_provisional": overall_excl_provisional_metrics,
            "provisional_cases_only_metrics": provisional_only_metrics,
            "split_metrics": {
                "development_set_35": dev_metrics,
                "held_out_set_15_previously_inspected": holdout_metrics
            },
            "by_language": by_language,
            "scenario_special_metrics": {
                "compound_offences": compound_metrics,
                "compound_section_recall": compound_section_recall,
                "compound_section_recall_ratio": f"{compound_found}/{compound_exp}",
                "compound_case_completion_rate": compound_case_completion_rate,
                "compound_case_completion_ratio": f"{compound_complete_cases}/{len(compound_cases)}",
                "misleading_keywords": misleading_metrics,
                "attempt_handling_correctness_rate": attempt_correctness_rate,
                "explicit_negation_immunity_rate": negation_immunity_rate,
                "misleading_keyword_immunity_rate": misleading_immunity_rate,
                "fact_inference_separation_rate": fact_separation_rate,
                "uncertainty_and_missing_fact_rate": uncertainty_handling_rate,
                "procedural_correctness_rate_verified_only": procedural_correctness_rate,
                "non_penal_grievance_gate": {
                    "total_penal_cases": total_penal,
                    "gate_false_positives": total_gate_fp,
                    "gate_false_positive_rate": gate_fp_rate_overall,
                    "gate_false_positive_ratio": f"{total_gate_fp}/{total_penal}",
                    "gate_false_positive_case_ids": all_gate_fp_cases,
                    "type_c_total_cases": overall_metrics.get("counts_and_denominators", {}).get("type_c_non_penal_cases", 0),
                    "type_c_gate_false_negatives": overall_metrics.get("counts_and_denominators", {}).get("type_c_false_negatives", 0),
                    "type_c_gate_false_negative_rate": overall_metrics.get("type_c_gate_false_negative_rate", 0.0),
                    "type_c_gate_false_negative_ratio": f"{overall_metrics.get('counts_and_denominators', {}).get('type_c_false_negatives', 0)}/{overall_metrics.get('counts_and_denominators', {}).get('type_c_non_penal_cases', 0)}",
                    "type_c_gate_false_negative_case_ids": overall_metrics.get("counts_and_denominators", {}).get("type_c_false_negative_case_ids", []),
                    "total_non_penal_cases_all_zero_sec": total_non_penal,
                    "gate_false_negatives": total_gate_fn,
                    "gate_false_negative_rate": gate_fn_rate_overall,
                    "gate_false_negative_ratio": f"{total_gate_fn}/{total_non_penal}",
                    "gate_false_negative_case_ids": all_gate_fn_cases
                }
            },
            "live_mode_disaggregation": {
                "genuine_live_cases_count": len(live_cases_genuine),
                "genuine_live_metrics": genuine_live_metrics,
                "cached_live_cases_count": len(live_cases_cached),
                "cached_live_metrics": cached_live_metrics,
                "fallback_activations_count": len(live_fallback_cases)
            },
            "metric_definitions_and_limitations": {
                "retrieval_recall_at_k": {
                    "formula": "sum(cand_hits_k) / sum(expected_count)",
                    "numerator": "Ground-truth relevant sections in the first k results of BM25LegalRetriever.retrieve(translated narrative, top_k=10)",
                    "denominator": "Total ground-truth relevant sections across cases in split",
                    "averaging": "Micro-averaged across section instances",
                    "unit": "relevant section instances",
                    "limitations": (
                        "Diagnostic of single-pass global BM25 only. It is NOT the candidate pool used by the service, which "
                        "uses retrieve_clause_level(max_k=8) and never passes more than 8 candidates to validation, so "
                        "Recall@10 is not achievable recall for the deployed pipeline. The relative threshold (0.35) means "
                        "fewer than k candidates may be returned. See production_candidate_recall."
                    )
                },
                "production_candidate_recall": {
                    "formula": "sum(production_cand_hits) / sum(expected_count)",
                    "numerator": "Ground-truth relevant sections in retrieve_clause_level(translated narrative, min_raw_score=0.0, relative_threshold=0.35, max_k=8), the same call the service makes",
                    "denominator": "Total ground-truth relevant sections across cases in split",
                    "averaging": "Micro-averaged across section instances",
                    "unit": "relevant section instances",
                    "limitations": "Upper bound on final recall in fallback mode only when the non-penal gate does not fire."
                },
                "candidate_precision_at_k_dynamic": {
                    "formula": "sum(cand_tp_k) / sum(min(k, raw_cand_count))",
                    "numerator": "Retrieved candidates in top-k belonging to relevant or plausible target pool",
                    "denominator": "Total candidates actually returned by dynamic retriever up to cutoff k",
                    "averaging": "Micro-averaged across returned candidate instances",
                    "unit": "candidate section instances"
                },
                "candidate_precision_at_k_fixed": {
                    "formula": "sum(cand_tp_k) / (k * total_cases)",
                    "numerator": "Retrieved candidates in top-k belonging to relevant or plausible target pool",
                    "denominator": "Theoretical fixed slot capacity (k * total_cases)",
                    "averaging": "Micro-averaged across theoretical candidate slots",
                    "unit": "candidate section instances"
                },
                "final_prediction_precision_micro": {
                    "formula": "sum(tp) / sum(total_pred)",
                    "numerator": "Predicted sections belonging to relevant OR plausible candidate pool",
                    "denominator": "Total sections predicted by engine across all cases",
                    "averaging": "Micro-averaged across all prediction instances",
                    "unit": "predicted section instances",
                    "limitations": "Lenient: plausible alternatives count as correct for precision but not for recall."
                },
                "final_prediction_recall_micro": {
                    "formula": "sum(relevant_found) / sum(expected_count)",
                    "numerator": "Ground-truth relevant sections successfully present in engine predictions",
                    "denominator": "Total ground-truth relevant sections across cases",
                    "averaging": "Micro-averaged across relevant section instances",
                    "unit": "relevant section instances",
                    "limitations": "Strict: only relevant_candidate_sections count; plausible alternatives are not credited."
                },
                "final_prediction_f1_micro": {
                    "formula": "2 * (Precision * Recall) / (Precision + Recall)",
                    "averaging": "Harmonic mean of micro-precision and micro-recall",
                    "unit": "harmonic mean"
                },
                "macro_metrics": {
                    "formula": "sum(case_metric) / total_cases",
                    "averaging": "Macro-averaged equally across all cases regardless of prediction count",
                    "empty_handling": "If expected is empty and predicted is empty, case precision=1.0, recall=1.0, F1=1.0. If predicted non-empty on empty expected, precision=0.0, recall=1.0, F1=0.0.",
                    "unit": "case-level mean"
                },
                "unsupported_section_rate": {
                    "formula": "sum(fp) / sum(total_pred) = 1 - final_prediction_precision_micro",
                    "numerator": "Predicted sections not in relevant or plausible label pools",
                    "denominator": "Total sections predicted across all cases",
                    "unit": "predicted section instances",
                    "limitations": (
                        "Not an independent metric: it is the complement of micro precision. 'Unsupported' means absent "
                        "from the benchmark labels, not legally unsupported by the facts."
                    )
                },
                "contradicted_fp_rate": {
                    "formula": "cases_with_contradicted_fp / cases_with_contradicted_sections",
                    "numerator": "Cases where an explicitly contradicted section appeared with score > 0",
                    "denominator": "Cases with at least one explicitly contradicted section defined in benchmark (most list Section 309)",
                    "unit": "cases"
                },
                "compound_offence_section_recall": {
                    "formula": "sum(relevant_found_in_compound) / sum(expected_in_compound)",
                    "numerator": "Relevant sections identified across compound multi-offence cases",
                    "denominator": "Total ground-truth relevant sections across evaluated compound cases",
                    "unit": "relevant section instances"
                },
                "compound_case_completion_rate": {
                    "formula": "cases_with_all_compound_sections_found / total_compound_cases",
                    "numerator": "Compound offence cases where 100% of expected sections were recovered",
                    "denominator": "Total evaluated compound offence cases",
                    "unit": "cases"
                },
                "non_penal_grievance_gate_fpr": {
                    "formula": "gate_false_positives / total_penal_cases",
                    "numerator": "Genuine penal complaints incorrectly suppressed by grievance gate",
                    "denominator": "Evaluated cases with at least one relevant section",
                    "unit": "cases"
                },
                "non_penal_grievance_gate_fnr_type_c": {
                    "formula": "type_c_false_negatives / total_type_c_cases",
                    "numerator": "Type C non-penal complaints (pricing/career metaphors) where gate failed to activate",
                    "denominator": "Evaluated misleading_keywords cases",
                    "unit": "cases"
                },
                "non_penal_grievance_gate_fnr_all_zero_sec": {
                    "formula": "gate_false_negatives / total_zero_sec_cases",
                    "numerator": "Zero-section cases (Type C grievances + Type D vague reports) where gate failed to activate",
                    "denominator": "Evaluated cases with zero expected sections",
                    "unit": "cases"
                },
                "procedural_correctness_rate_verified_only": {
                    "formula": "correct_schedule_metadata_cases / schedule_evaluated_cases",
                    "numerator": "Cases where the TOP-RANKED prediction's (is_cognizable, is_bailable) equals the labelled pair",
                    "denominator": "Cases with verified_schedule_applicable=true and a non-null expected_cognizable label",
                    "unit": "cases",
                    "limitations": (
                        "Only the top prediction is compared, so a correct classification on a lower-ranked offence scores "
                        "as a miss. Labels are synthetic; some attempt-case bailability labels carry documented concerns "
                        "(see cases_with_label_review_notes)."
                    )
                }
            },
            "case_results": results,
            "error_analysis": errors
        }

        self._print_terminal_report(report)
        return report

    def _print_terminal_report(self, report: Dict[str, Any]):
        o = report["overall_metrics"]
        cnts = o.get("counts_and_denominators", {})
        s = report["split_metrics"]
        langs = report["by_language"]
        scen = report["scenario_special_metrics"]
        meta = report["metadata"]

        print("\n" + "=" * 70)
        print("         BNS BENCHMARK AGGREGATE EVALUATION REPORT")
        print("=" * 70)
        print(f" Model Identifier      : {meta['model_identifier']}")
        print(f" Evaluation Mode       : {meta['evaluation_mode']}")
        print(f" Total Cases Evaluated : {meta['total_cases_evaluated']} (Dev: {s['development_set_35'].get('case_count', 0)}, Holdout: {s['held_out_set_15_previously_inspected'].get('case_count', 0)})")
        print(f" Genuine Live Calls    : {meta.get('successful_genuine_live_responses', 0)}")
        print(f" Cached Live Responses : {meta.get('cached_responses_used', 0)}")
        print(f" Fallback Activations  : {meta.get('fallback_activations', 0)}")
        print(f" Failed Requests       : {meta['failed_requests']}")
        print("-" * 70)
        print(" [1] PURE RETRIEVAL RECALL & CANDIDATE PRECISION (BEFORE PRUNING):")
        print(f"     Retrieval Recall@3                 : {o.get('retrieval_recall_at_3', 0.0) * 100:.2f}% ({cnts.get('retrieval_hits_at_3', 0)}/{cnts.get('ground_truth_relevant_sections', 0)})")
        print(f"     Retrieval Recall@5                 : {o.get('retrieval_recall_at_5', 0.0) * 100:.2f}% ({cnts.get('retrieval_hits_at_5', 0)}/{cnts.get('ground_truth_relevant_sections', 0)})")
        print(f"     Retrieval Recall@8                 : {o.get('retrieval_recall_at_8', 0.0) * 100:.2f}% ({cnts.get('retrieval_hits_at_8', 0)}/{cnts.get('ground_truth_relevant_sections', 0)})")
        print(f"     Retrieval Recall@10                : {o.get('retrieval_recall_at_10', 0.0) * 100:.2f}% ({cnts.get('retrieval_hits_at_10', 0)}/{cnts.get('ground_truth_relevant_sections', 0)})")
        print(f"     Candidate Precision@3  (dynamic)   : {o.get('candidate_precision_at_3', 0.0) * 100:.2f}% ({cnts.get('candidate_tp_at_3', 0)}/{cnts.get('candidate_total_at_3', 0)}) [fixed 3*N: {o.get('candidate_precision_fixed_k_n_at_3', 0.0) * 100:.2f}% ({cnts.get('candidate_tp_at_3', 0)}/{cnts.get('fixed_slot_candidate_total_at_3', 0)})]")
        print(f"     Candidate Precision@5  (dynamic)   : {o.get('candidate_precision_at_5', 0.0) * 100:.2f}% ({cnts.get('candidate_tp_at_5', 0)}/{cnts.get('candidate_total_at_5', 0)}) [fixed 5*N: {o.get('candidate_precision_fixed_k_n_at_5', 0.0) * 100:.2f}% ({cnts.get('candidate_tp_at_5', 0)}/{cnts.get('fixed_slot_candidate_total_at_5', 0)})]")
        print(f"     Candidate Precision@8  (dynamic)   : {o.get('candidate_precision_at_8', 0.0) * 100:.2f}% ({cnts.get('candidate_tp_at_8', 0)}/{cnts.get('candidate_total_at_8', 0)}) [fixed 8*N: {o.get('candidate_precision_fixed_k_n_at_8', 0.0) * 100:.2f}% ({cnts.get('candidate_tp_at_8', 0)}/{cnts.get('fixed_slot_candidate_total_at_8', 0)})]")
        print(f"     Candidate Precision@10 (dynamic)   : {o.get('candidate_precision_at_10', 0.0) * 100:.2f}% ({cnts.get('candidate_tp_at_10', 0)}/{cnts.get('candidate_total_at_10', 0)}) [fixed 10*N: {o.get('candidate_precision_fixed_k_n_at_10', 0.0) * 100:.2f}% ({cnts.get('candidate_tp_at_10', 0)}/{cnts.get('fixed_slot_candidate_total_at_10', 0)})]")
        print("-" * 70)
        print(" [2] FINAL PREDICTION PERFORMANCE (AFTER VALIDATION/FILTERING):")
        print(f"     Final Precision (Micro)            : {o.get('final_prediction_precision_micro', 0.0) * 100:.2f}% ({cnts.get('true_positives', 0)}/{cnts.get('total_predictions', 0)})")
        print(f"     Final Recall (Micro)               : {o.get('final_prediction_recall_micro', 0.0) * 100:.2f}% ({cnts.get('relevant_sections_retrieved_in_final', 0)}/{cnts.get('ground_truth_relevant_sections', 0)})")
        print(f"     Final F1 (Micro)                   : {o.get('final_prediction_f1_micro', 0.0):.4f}")
        print(f"     Final Precision (Macro)            : {o.get('final_prediction_precision_macro', 0.0) * 100:.2f}%")
        print(f"     Final Recall (Macro)               : {o.get('final_prediction_recall_macro', 0.0) * 100:.2f}%")
        print(f"     Final F1 (Macro)                   : {o.get('final_prediction_f1_macro', 0.0):.4f}")
        print(f"     Unsupported Section Rate           : {o.get('unsupported_section_rate', 0.0) * 100:.2f}% ({cnts.get('false_positives', 0)}/{cnts.get('total_predictions', 0)})")
        print(f"     Contradicted Section False-Pos Rate: {o.get('contradicted_fp_rate', 0.0) * 100:.2f}% ({cnts.get('contradicted_false_positive_cases', 0)}/{cnts.get('cases_with_contradictions', 0)})")
        print(f"     Production Candidate Recall (k<=8) : {o.get('production_candidate_recall', 0.0) * 100:.2f}% ({cnts.get('production_candidate_hits', 0)}/{cnts.get('ground_truth_relevant_sections', 0)})")
        print("     *Unsupported rate = 1 - micro precision. Recall@k uses single-pass retrieve(), not the service's candidate pool.")
        print("-" * 70)
        x = report.get("overall_metrics_excluding_provisional", {})
        xc = x.get("counts_and_denominators", {})
        print(f" [2b] EXCLUDING PROVISIONAL CASES ({x.get('case_count', 0)} cases; provisional: {meta.get('provisional_ground_truth_cases', [])}):")
        print(f"     Final Precision (Micro)            : {x.get('final_prediction_precision_micro', 0.0) * 100:.2f}% ({xc.get('true_positives', 0)}/{xc.get('total_predictions', 0)})")
        print(f"     Final Recall (Micro)               : {x.get('final_prediction_recall_micro', 0.0) * 100:.2f}% ({xc.get('relevant_sections_retrieved_in_final', 0)}/{xc.get('ground_truth_relevant_sections', 0)})")
        print(f"     Final F1 (Micro)                   : {x.get('final_prediction_f1_micro', 0.0):.4f}")
        print(f"     Retrieval Recall@10                : {x.get('retrieval_recall_at_10', 0.0) * 100:.2f}% ({xc.get('retrieval_hits_at_10', 0)}/{xc.get('ground_truth_relevant_sections', 0)})")
        print(f"     Unsupported Section Rate           : {x.get('unsupported_section_rate', 0.0) * 100:.2f}% ({xc.get('false_positives', 0)}/{xc.get('total_predictions', 0)})")
        print(f"     Procedural Correctness (Verified)  : {x.get('procedural_correctness_rate_verified_only', 0.0) * 100:.2f}% ({xc.get('schedule_correct_cases', 0)}/{xc.get('schedule_evaluated_cases', 0)})")
        print("-" * 70)
        print(" [3] SPLIT COMPARISON (DEV vs PREVIOUSLY INSPECTED HOLDOUT):")
        dev = s.get("development_set_35", {})
        hld = s.get("held_out_set_15_previously_inspected", {})
        dev_c = dev.get("counts_and_denominators", {})
        hld_c = hld.get("counts_and_denominators", {})
        print(f"     Dev Set (35 cases)       - Recall: {dev.get('final_prediction_recall_micro', 0.0)*100:.2f}% ({dev_c.get('relevant_sections_retrieved_in_final',0)}/{dev_c.get('ground_truth_relevant_sections',0)}) | Prec: {dev.get('final_prediction_precision_micro', 0.0)*100:.2f}% | F1: {dev.get('final_prediction_f1_micro', 0.0):.4f}")
        print(f"     Holdout Set (15 cases)*  - Recall: {hld.get('final_prediction_recall_micro', 0.0)*100:.2f}% ({hld_c.get('relevant_sections_retrieved_in_final',0)}/{hld_c.get('ground_truth_relevant_sections',0)}) | Prec: {hld.get('final_prediction_precision_micro', 0.0)*100:.2f}% | F1: {hld.get('final_prediction_f1_micro', 0.0):.4f}")
        print("     *Note: Holdout set was previously inspected in prior evaluation reports.")
        print("-" * 70)
        print(" [4] BREAKDOWN BY LANGUAGE:")
        for lang_name, ldata in langs.items():
            lc = ldata.get("counts_and_denominators", {})
            print(f"     {lang_name:<10} ({ldata.get('case_count', 0)} cases) - Recall: {ldata.get('final_prediction_recall_micro', 0.0)*100:.2f}% ({lc.get('relevant_sections_retrieved_in_final',0)}/{lc.get('ground_truth_relevant_sections',0)}) | Prec: {ldata.get('final_prediction_precision_micro', 0.0)*100:.2f}% | F1: {ldata.get('final_prediction_f1_micro', 0.0):.4f}")
        print("-" * 70)
        print(" [5] SCENARIO-SPECIFIC EVALUATIONS:")
        comp = scen.get("compound_offences", {})
        gate = scen.get("non_penal_grievance_gate", {})
        print(f"     Compound Section Recall (Micro)    : {scen.get('compound_section_recall', 0.0) * 100:.2f}% ({scen.get('compound_section_recall_ratio', 'N/A')})")
        print(f"     Compound Case Completion (All-Req) : {scen.get('compound_case_completion_rate', 0.0) * 100:.2f}% ({scen.get('compound_case_completion_ratio', 'N/A')})")
        print(f"     Grievance Gate False-Positive Rate : {gate.get('gate_false_positive_rate', 0.0) * 100:.2f}% ({gate.get('gate_false_positive_ratio', 'N/A')}) IDs: {gate.get('gate_false_positive_case_ids', [])}")
        print(f"     Gate FNR (Type C Non-Penal)        : {gate.get('type_c_gate_false_negative_rate', 0.0) * 100:.2f}% ({gate.get('type_c_gate_false_negative_ratio', 'N/A')}) IDs: {gate.get('type_c_gate_false_negative_case_ids', [])}")
        print(f"     Gate FNR (All Zero-Sec: Type C+D)  : {gate.get('gate_false_negative_rate', 0.0) * 100:.2f}% ({gate.get('gate_false_negative_ratio', 'N/A')}) IDs: {gate.get('gate_false_negative_case_ids', [])}")
        print(f"     Misleading Keywords Immunity       : {scen.get('misleading_keyword_immunity_rate', 0.0) * 100:.2f}%")
        print(f"     Explicit Negation Immunity         : {scen.get('explicit_negation_immunity_rate', 0.0) * 100:.2f}%")
        print(f"     Attempt Handling Correctness       : {scen.get('attempt_handling_correctness_rate', 0.0) * 100:.2f}%")
        print(f"     Fact vs Inference Separation       : {scen.get('fact_inference_separation_rate', 0.0) * 100:.2f}%")
        print(f"     Missing Fact / Uncertainty Handling: {scen.get('uncertainty_and_missing_fact_rate', 0.0) * 100:.2f}%")
        print(f"     Procedural Correctness (Verified)  : {scen.get('procedural_correctness_rate_verified_only', 0.0) * 100:.2f}% ({cnts.get('schedule_correct_cases', 0)}/{cnts.get('schedule_evaluated_cases', 0)}, top prediction only)")
        print("=" * 70)
        print(f" Total Material Errors Identified      : {len(report['error_analysis'])}")
        print("=" * 70 + "\n")

    def _verify_metric_identities(
        self,
        overall: Dict[str, Any],
        dev: Dict[str, Any],
        holdout: Dict[str, Any],
        by_language: Dict[str, Dict[str, Any]],
        excl_provisional: Optional[Dict[str, Any]] = None,
        provisional_only: Optional[Dict[str, Any]] = None
    ):
        """
        Automated verification of metric identities and reconciliation sums across all partitions.
        Ensures arithmetic integrity and prevents regression in reporting formulas.
        """
        partitions = [("Overall", overall), ("Dev", dev), ("Holdout", holdout),
                      ("ExclProvisional", excl_provisional or {}), ("ProvisionalOnly", provisional_only or {})]
        for lang, l_data in by_language.items():
            partitions.append((f"Lang_{lang}", l_data))

        for name, p in partitions:
            if not p:
                continue
            cnts = p["counts_and_denominators"]
            # 1. Identity: TP + FP == Total Predictions
            assert cnts["true_positives"] + cnts["false_positives"] == cnts["total_predictions"], (
                f"[{name}] Identity violation: TP ({cnts['true_positives']}) + FP ({cnts['false_positives']}) != Total Preds ({cnts['total_predictions']})"
            )

            # 2. Micro Precision == TP / Total Predictions
            if cnts["total_predictions"] > 0:
                exp_micro_prec = round(cnts["true_positives"] / cnts["total_predictions"], 4)
                assert abs(p["final_prediction_precision_micro"] - exp_micro_prec) <= 0.0001, (
                    f"[{name}] Micro Precision mismatch: {p['final_prediction_precision_micro']} vs {exp_micro_prec}"
                )

            # 3. Micro Recall == Relevant Recovered / Ground Truth Relevant Sections
            if cnts["ground_truth_relevant_sections"] > 0:
                exp_micro_rec = round(cnts["relevant_sections_retrieved_in_final"] / cnts["ground_truth_relevant_sections"], 4)
                assert abs(p["final_prediction_recall_micro"] - exp_micro_rec) <= 0.0001, (
                    f"[{name}] Micro Recall mismatch: {p['final_prediction_recall_micro']} vs {exp_micro_rec}"
                )

            # 4. Micro F1 follows from Micro Precision and Micro Recall
            pval = p["final_prediction_precision_micro"]
            rval = p["final_prediction_recall_micro"]
            if (pval + rval) > 0:
                exp_micro_f1 = round(2 * pval * rval / (pval + rval), 4)
                assert abs(p["final_prediction_f1_micro"] - exp_micro_f1) <= 0.0001, (
                    f"[{name}] Micro F1 mismatch: {p['final_prediction_f1_micro']} vs {exp_micro_f1}"
                )

            # 5. Unsupported Section Rate uses documented denominator (FP / Total Preds)
            if cnts["total_predictions"] > 0:
                exp_unsup = round(cnts["false_positives"] / cnts["total_predictions"], 4)
                assert abs(p["unsupported_section_rate"] - exp_unsup) <= 0.0001, (
                    f"[{name}] Unsupported Section Rate mismatch: {p['unsupported_section_rate']} vs {exp_unsup}"
                )
                assert abs((p["final_prediction_precision_micro"] + p["unsupported_section_rate"]) - 1.0) <= 0.0001, (
                    f"[{name}] Precision ({p['final_prediction_precision_micro']}) + Unsupported Rate ({p['unsupported_section_rate']}) != 1.0"
                )

            # 6. Dynamic candidate precision uses actual returned candidates
            for k in (3, 5, 8, 10):
                ret_denom = cnts[f"candidate_total_at_{k}"]
                if ret_denom > 0:
                    exp_dyn = round(cnts[f"candidate_tp_at_{k}"] / ret_denom, 4)
                    assert abs(p[f"candidate_precision_at_{k}"] - exp_dyn) <= 0.0001, (
                        f"[{name}] Dynamic Prec@{k} mismatch: {p[f'candidate_precision_at_{k}']} vs {exp_dyn}"
                    )

            # 7. Fixed-slot candidate precision uses K * N
            for k in (3, 5, 8, 10):
                fixed_denom = cnts[f"fixed_slot_candidate_total_at_{k}"]
                assert fixed_denom == k * p["case_count"]
                if fixed_denom > 0:
                    exp_fixed = round(cnts[f"candidate_tp_at_{k}"] / fixed_denom, 4)
                    assert abs(p[f"candidate_precision_fixed_k_n_at_{k}"] - exp_fixed) <= 0.0001, (
                        f"[{name}] Fixed Prec@{k} mismatch: {p[f'candidate_precision_fixed_k_n_at_{k}']} vs {exp_fixed}"
                    )

        # 8. Reconcile Split Totals (Overall == Dev + Holdout)
        if dev and holdout:
            o_cnt = overall["counts_and_denominators"]
            d_cnt = dev["counts_and_denominators"]
            h_cnt = holdout["counts_and_denominators"]
            for field in [
                "total_predictions", "true_positives", "false_positives",
                "ground_truth_relevant_sections", "relevant_sections_retrieved_in_final",
                "retrieval_hits_at_3", "retrieval_hits_at_5", "retrieval_hits_at_8", "retrieval_hits_at_10",
                "candidate_tp_at_3", "candidate_total_at_3", "candidate_tp_at_5", "candidate_total_at_5",
                "candidate_tp_at_8", "candidate_total_at_8", "candidate_tp_at_10", "candidate_total_at_10"
            ]:
                assert o_cnt[field] == d_cnt[field] + h_cnt[field], (
                    f"Overall {field} ({o_cnt[field]}) != Dev ({d_cnt[field]}) + Holdout ({h_cnt[field]})"
                )

        # 8b. Reconcile provisional partition (Overall == Excluding Provisional + Provisional Only)
        if excl_provisional:
            o_cnt = overall["counts_and_denominators"]
            x_cnt = excl_provisional["counts_and_denominators"]
            p_cnt = (provisional_only or {}).get("counts_and_denominators", {})
            for field in [
                "total_predictions", "true_positives", "false_positives",
                "ground_truth_relevant_sections", "relevant_sections_retrieved_in_final",
                "retrieval_hits_at_10", "production_candidate_hits",
                "schedule_evaluated_cases", "schedule_correct_cases"
            ]:
                assert o_cnt[field] == x_cnt[field] + p_cnt.get(field, 0), (
                    f"Overall {field} ({o_cnt[field]}) != Excl. provisional ({x_cnt[field]}) + Provisional ({p_cnt.get(field, 0)})"
                )

        # 9. Reconcile Language Totals (Overall == English + Hindi + Hinglish)
        if len(by_language) == 3:
            o_cnt = overall["counts_and_denominators"]
            sum_by_lang = {
                field: sum(by_language[lang]["counts_and_denominators"][field] for lang in by_language)
                for field in [
                    "total_predictions", "true_positives", "false_positives",
                    "ground_truth_relevant_sections", "relevant_sections_retrieved_in_final",
                    "retrieval_hits_at_3", "retrieval_hits_at_5", "retrieval_hits_at_8", "retrieval_hits_at_10",
                    "candidate_tp_at_3", "candidate_total_at_3", "candidate_tp_at_5", "candidate_total_at_5",
                    "candidate_tp_at_8", "candidate_total_at_8", "candidate_tp_at_10", "candidate_total_at_10"
                ]
            }
            for field, l_sum in sum_by_lang.items():
                assert o_cnt[field] == l_sum, (
                    f"Overall {field} ({o_cnt[field]}) != Language Sum ({l_sum})"
                )


def main():
    parser = argparse.ArgumentParser(description="Evaluate Bandhoo against BNS Benchmark")
    parser.add_argument(
        "--benchmark",
        default=os.path.join(BASE_DIR, "datasets", "bns_synthetic_benchmark_50.json") if os.path.exists(os.path.join(BASE_DIR, "datasets", "bns_synthetic_benchmark_50.json")) else os.path.join(BASE_DIR, "benchmark", "bns_synthetic_benchmark_50.json"),
        help="Path to benchmark JSON"
    )
    parser.add_argument(
        "--mode",
        choices=["fallback", "live"],
        default="fallback",
        help="Evaluation mode ('fallback' or 'live')"
    )
    parser.add_argument(
        "--cache-dir",
        default=os.path.join(BASE_DIR, "benchmark", "cache"),
        help="Directory to store cached LLM responses"
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output report JSON path"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of cases to evaluate"
    )
    args = parser.parse_args()

    evaluator = BenchmarkEvaluator(
        benchmark_path=args.benchmark,
        mode=args.mode,
        cache_dir=args.cache_dir,
        limit=args.limit
    )
    report = evaluator.run_evaluation()

    out_path = args.out or os.path.join(
        BASE_DIR, "benchmark", f"evaluation_report_{args.mode}.json"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Saved complete evaluation report to: {out_path}\n")


if __name__ == "__main__":
    main()
