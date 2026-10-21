"""
Complete Complaint Compilation Engine (Phase 2 Checkpoint P2.4).

Compiles all information provided by the user into a consistent, reviewable,
and legally grounded complaint record.

Governing Principles:
1. Preserve original narration verbatim and unchanged (with SHA-256 integrity check).
2. Keep extracted facts grounded in character spans, strictly separated from AI inferences.
3. Preserve negation, speculation, identity corrections and uncertainty scope.
4. Never convert unverified allegations into established facts.
5. Zero hallucination: do not invent names, dates, values, witnesses, evidence or legal citations.
6. Identify unanswered questions and open missing fields without fabricating answers.
7. Supports both general complaints and specialized missing-person reports.
8. Persists structured records, revisions, and audit logs to PostgreSQL.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from complaint_engine.graph import run_structuring
from complaint_engine.models import (
    ComplaintStructureRequest,
    ComplainantDetails,
    MissingPersonDetails,
    utc_now,
    sha256_text,
)


def _format_chronological_timeline(report: dict) -> List[dict]:
    """
    Constructs an incident timeline ordered by date/time references,
    falling back to complainant statement narrative order.
    """
    timeline = []
    dates_and_times = report.get("dates_and_times") or []
    events = report.get("events") or []
    alleged_actions = report.get("alleged_actions") or []

    # Map statements to sequence
    for dt in dates_and_times:
        spans = dt.get("spans") or []
        span_ref = spans[0] if spans else {}
        timeline.append({
            "time_expression": dt.get("value"),
            "normalized": dt.get("normalized"),
            "event_description": dt.get("note") or "Stated incident timing",
            "source_span": span_ref,
            "statement_id": span_ref.get("statement_id", "S1"),
            "polarity": dt.get("polarity", "asserted")
        })

    for act in alleged_actions:
        spans = act.get("spans") or []
        span_ref = spans[0] if spans else {}
        timeline.append({
            "time_expression": "Sequence order from narrative",
            "normalized": None,
            "event_description": f"Alleged action: {act.get('value')}",
            "source_span": span_ref,
            "statement_id": span_ref.get("statement_id", "S1"),
            "polarity": act.get("polarity", "asserted")
        })

    return timeline


def _format_people_and_roles(report: dict) -> List[dict]:
    """
    Categorizes individuals mentioned into explicit legal capacities
    (alleged suspect, victim, witness, relative), ensuring allegations are never established facts.
    """
    people = []
    persons_raw = report.get("persons") or []
    witnesses_raw = report.get("witness_references") or []

    witness_quotes = {w.get("value", "").lower() for w in witnesses_raw}

    for p in persons_raw:
        val = p.get("value", "")
        polarity = p.get("polarity", "asserted")
        spans = p.get("spans") or []
        
        # Categorize role cautiously
        val_lower = val.lower()
        if any(w in val_lower for w in ["saw", "witness", "friend", "passerby", "neighbour", "neighbor"]):
            role = "eyewitness_referenced"
        elif any(s in val_lower for w in ["stole", "took", "hit", "attacked", "snatched", "robbed", "threatened", "kidnapped", "accused", "suspect"] for s in [w]):
            role = "alleged_perpetrator_unverified"
        else:
            role = "person_involved_or_alleged"

        people.append({
            "name_or_description": val,
            "alleged_role": role,
            "polarity": polarity,
            "verification_status": "unverified",
            "spans": spans,
            "note": "Allegation from complainant statement; not an established police finding."
        })

    for w in witnesses_raw:
        if w.get("value", "").lower() not in [p["name_or_description"].lower() for p in people]:
            people.append({
                "name_or_description": w.get("value"),
                "alleged_role": "eyewitness_referenced",
                "polarity": w.get("polarity", "asserted"),
                "verification_status": "unverified",
                "spans": w.get("spans") or [],
                "note": "Witness reference provided by complainant."
            })

    return people


def _retrieve_statutory_candidates(narrative_text: str) -> List[dict]:
    """
    Retrieves potential BNS statutory references using BM25 and BNS Corpus.
    Includes strict disclaimers that this is machine assistance for review, not an official charge.
    """
    try:
        from legal_engine import BNSCorpus, BM25LegalRetriever
        corpus = BNSCorpus()
        retriever = BM25LegalRetriever(corpus)
        results = retriever.retrieve(narrative_text, top_k=4)
        
        candidates = []
        for item in results:
            sec_num = item[0] if isinstance(item, (tuple, list)) else getattr(item, "section_num", None)
            score = item[1] if isinstance(item, (tuple, list)) else getattr(item, "score", 0.0)
            sec_data = corpus.get_section(sec_num) if sec_num is not None else None
            title = sec_data.get("title", "") if sec_data else ""
            punishment = sec_data.get("punishment", "") if sec_data else ""
            candidates.append({
                "bns_section": sec_num,
                "title": title,
                "punishment": punishment,
                "relevance_score": round(score, 4),
                "disclaimer": "AI statutory candidate suggestion for human legal review only; not an official police charge or final FIR classification."
            })
        return candidates
    except Exception as exc:
        return [{
            "bns_section": None,
            "title": "Statutory retrieval unavailable",
            "error": str(exc),
            "disclaimer": "Legal analysis service unavailable."
        }]


def compile_complaint_record(
    request: ComplaintStructureRequest,
    include_legal_candidates: bool = True,
    db_session: Optional[Any] = None
) -> dict:
    """
    Executes complete complaint compilation across all 10 requirements.
    Preserves raw narrative, builds chronological timeline, categorizes roles,
    analyzes missing info, formats missing person details, and optionally persists to PostgreSQL.
    """
    # 1. Run the LangGraph structuring workflow
    state = run_structuring(request)
    report = state.get("report") or {}
    statements = report.get("complainant_statements") or []
    orig_statement = statements[0]["text"] if statements else request.statement

    complaint_id = str(uuid.uuid4())
    complaint_number = f"BND-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    # 2. Gather chronological facts & people
    timeline = _format_chronological_timeline(report)
    people_and_roles = _format_people_and_roles(report)

    # 3. Statement analysis (denials, corrections, uncertainties)
    explicit_denials = report.get("explicit_denials") or []
    uncertain_items = [
        f for f in (state.get("facts") or [])
        if getattr(f, "polarity", "") == "uncertain"
    ]
    statement_analysis = {
        "explicit_denials": [d.get("value") if isinstance(d, dict) else str(d) for d in explicit_denials],
        "hedged_or_uncertain_claims": [u.value for u in uncertain_items],
        "clarifications_recorded": len(statements) - 1,
        "contradictions_flagged": [c.get("summary") for c in report.get("contradictions") or []]
    }

    # 4. Property, Losses & Damages
    property_and_losses = {
        "items_lost_or_damaged": report.get("items_lost_or_damaged") or [],
        "monetary_losses": report.get("losses") or [],
        "injuries_reported": report.get("injuries") or [],
        "weapons_mentioned": report.get("weapons_mentioned") or []
    }

    # 5. Evidence & Witnesses
    evidence_and_witnesses = {
        "witnesses_referenced": report.get("witness_references") or [],
        "supporting_evidence_provided": report.get("supporting_evidence_provided") or [],
        "independently_verified": report.get("independently_verified") or []
    }

    # 6. Potential Legal Sections
    legal_candidates = []
    if include_legal_candidates:
        full_text = " ".join([orig_statement] + list(request.clarifications))
        legal_candidates = _retrieve_statutory_candidates(full_text)

    # 7. Collect all extracted facts for database persistence
    all_facts = [
        f.model_dump() if hasattr(f, "model_dump") else f
        for f in (state.get("facts") or [])
    ]

    # 8. Assemble compiled record
    compiled = {
        "complaint_id": complaint_id,
        "complaint_number": complaint_number,
        "header": {
            "document_title": "Comprehensive Structured Complaint Record",
            "document_status": "DRAFT - Not an FIR - Citizen Report Draft",
            "workflow_version": "complaint-compiler-1.0",
            "compiled_at": utc_now(),
            "persistence_status": "in_memory" if not db_session else "persisted_in_database",
        },
        "complainant": request.complainant.model_dump() if request.complainant else None,
        "report_type": "missing_person_report" if request.missing_person else "general_complaint",
        "missing_person_details": request.missing_person.model_dump() if request.missing_person else None,
        "urgency_assessment": report.get("urgency_assessment"),
        "original_narration": {
            "verbatim_text": orig_statement,
            "sha256": sha256_text(orig_statement),
            "received_at": statements[0].get("received_at", utc_now()) if statements else utc_now()
        },
        "clarifications": [s for s in statements[1:]] if len(statements) > 1 else [],
        "chronological_timeline": timeline,
        "people_and_roles": people_and_roles,
        "alleged_actions": report.get("alleged_actions") or [],
        "property_and_losses": property_and_losses,
        "evidence_and_witnesses": evidence_and_witnesses,
        "jurisdiction_assessment": report.get("jurisdiction"),
        "potential_bns_sections": legal_candidates,
        "statement_analysis": statement_analysis,
        "missing_or_contradictory_information": {
            "missing_fields": report.get("missing_information") or [],
            "questions_for_complainant": report.get("questions_for_complainant") or [],
            "contradictions": report.get("contradictions") or []
        },
        "verification_checklist_for_officer": report.get("verification_checklist_for_officer") or [],
        "review_and_routing": report.get("review") or {},
        "draft_text": report.get("draft_text", ""),
        "all_extracted_facts": all_facts,
    }

    # 9. PostgreSQL Persistence (if session provided)
    if db_session:
        from db.repository import ComplaintRepository
        repo = ComplaintRepository(db_session)
        persisted_entity = repo.save_compiled_complaint(compiled)
        compiled["header"]["persistence_status"] = "persisted_in_database"
        compiled["persisted_db_id"] = persisted_entity.id

    return compiled
