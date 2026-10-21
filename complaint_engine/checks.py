"""
Missing-information, contradiction and evidence checks.

Contradictions are flagged neutrally with both source quotations preserved. They are never treated
as evidence of dishonesty and never resolved automatically.
"""

import re
from typing import Dict, List, Optional, Tuple

from complaint_engine.models import (
    Contradiction, EvidenceItem, EvidenceMetadataInput, FactItem, MissingInfo, NodeError,
    SourceSpan, Statement, VerificationEvent,
)

CORE_FIELDS = ("what_happened", "when", "where")

QUESTIONS = {
    "what_happened": "Please describe what happened, in your own words.",
    "when": "On what date and at about what time did this happen?",
    "where": "Where did this happen? Please give the place or a nearby landmark.",
    "who": "Who was involved? Please describe them if you do not know their names.",
    "loss_value": "What was taken or lost, and what is its approximate value?",
    "medical_attention": "Did anyone receive medical attention? If so, where?",
    "evidence": "Do you have any photos, messages, receipts or other material related to this?",
    "witnesses": "Did anyone else see what happened? If so, how can they be contacted?",
}
WHY = {
    "what_happened": "The police need an account of the events.",
    "when": "Date and time are needed to check the account and records.",
    "where": "The place is needed to confirm jurisdiction and look for evidence.",
    "who": "Descriptions of the people involved help the police identify them.",
    "loss_value": "The items and value of any loss need to be recorded.",
    "medical_attention": "Medical records may support the description of injuries.",
    "evidence": "Supporting material helps the police check the account.",
    "witnesses": "Witnesses may help confirm what happened.",
}
MAX_QUESTIONS = 5

LOSS_WORDS = re.compile(r"\b(?:stole|stolen|steal|took|taken|snatch\w*|grab\w*|robbed|cheat\w*|lost|transferred|paid|fraud|scam\w*|"
                        r"damag\w*|broke|broken|smash\w*|destroy\w*)\b", re.I)
MEDICAL_WORDS = re.compile(r"\b(?:hospital|doctor|clinic|treatment|treated|first aid|medical)\b", re.I)
# "I do not know ..." counts as unknown only for the category its object names. "I do not know the date"
# says nothing about who was involved.
_NOT = r"\b(?:i|we)\s+(?:do\s+not|don't|did\s+not|didn't|cannot|can't|could\s+not|couldn't)\s+"
UNKNOWN_PATTERNS = {
    "who": re.compile(
        _NOT + r"(?:(?:know|tell|say|identify)\s+(?:who|whom|him|her|them|(?:his|her|their)\s+names?|the\s+(?:name|identity)|"
        r"(?:the\s+)?(?:man|men|woman|women|person|persons|people|thief|thieves|accused|culprits?|attackers?|offenders?))|"
        r"recogni[sz]e|see\s+(?:his|her|their)\s+faces?)\b[^.!?]*", re.I),
    "when": re.compile(
        _NOT + r"(?:know|remember|recall|tell|say)\s+(?:when|(?:the\s+)?(?:exact\s+)?(?:time|date|day))\b[^.!?]*", re.I),
    "where": re.compile(
        _NOT + r"(?:know|remember|recall|tell|say)\s+(?:where|the\s+(?:exact\s+)?(?:place|location|address|spot|area)|"
        r"the\s+name\s+of\s+the\s+(?:place|road|street|area|station))\b[^.!?]*", re.I),
    "loss_value": re.compile(
        _NOT + r"(?:know|remember|recall|tell|say)\s+(?:how\s+much|the\s+(?:exact\s+)?(?:value|cost|price|amount)|"
        r"(?:its|their)\s+(?:value|cost|price))\b[^.!?]*", re.I),
}

# Language coverage. The deterministic extractor is written for English, with a few common Hinglish and
# Marathi expressions. For other text, details it cannot find are "not_determined", not missing.
DEVANAGARI = re.compile(r"[\u0900-\u097F]")
ROMANISED_MARKERS = {
    "hai", "hain", "tha", "thi", "mera", "meri", "mere", "mujhe", "maine", "humne", "kal", "aaj", "raat", "shaam",
    "subah", "baje", "aur", "nahi", "nahin", "nhi", "liya", "liye", "gaya", "gayi", "kiya", "diya", "paas", "saamne",
    "wala", "wali", "ke", "ki", "ko", "ne", "se", "mein", "koi", "kisi", "aadmi", "admi", "ladka", "ladke", "chori",
    "cheen", "majha", "mazha", "mala", "kela", "zala", "jhala", "ahe", "hota", "hoti",
}
LIMITED_COVERAGE_NOTE = ("The statement is in a language or script the extractor only partly supports. A person must read "
                         "the original statement; details the extractor could not find are marked 'not determined', not missing.")


def _span_for(match: re.Match, st: Statement) -> SourceSpan:
    return SourceSpan(statement_id=st.statement_id, start=match.start(), end=match.end(), quote=match.group(0))


def language_profile(statements: List[Statement]) -> dict:
    """Returns {"coverage": "full" | "limited", "detected": ..., "note": ...} for the statements together."""
    detected = "latin_script_english"
    for st in statements:
        letters = [c for c in st.text if c.isalpha()]
        if letters and sum(1 for c in letters if DEVANAGARI.match(c)) / len(letters) >= 0.2:
            detected = "devanagari_script"
            break
        if len(ROMANISED_MARKERS & {w.lower() for w in re.findall(r"[A-Za-z]+", st.text)}) >= 3:
            detected = "romanised_hindi_or_marathi"
    limited = detected != "latin_script_english"
    return {"coverage": "limited" if limited else "full", "detected": detected,
            "note": LIMITED_COVERAGE_NOTE if limited else ""}


def detect_missing(facts: List[FactItem], statements: List[Statement], evidence_supplied: bool,
                   location_supplied: bool, coverage: str = "full") -> List[MissingInfo]:
    asserted = [f for f in facts if f.provenance == "complainant_statement" and f.polarity != "explicitly_denied"]
    kinds = {f.kind for f in asserted}
    text = " ".join(s.text for s in statements)
    out: List[MissingInfo] = []
    # With limited language coverage, "not found" means "not read", so it is never reported as missing.
    not_found = "not_determined" if coverage == "limited" else "open"

    def unknown(field: str) -> Optional[MissingInfo]:
        for st in statements:
            m = UNKNOWN_PATTERNS[field].search(st.text) if field in UNKNOWN_PATTERNS else None
            if m:
                return MissingInfo(field=field, why_needed=WHY[field], status="unknown_to_complainant", source_spans=[_span_for(m, st)])
        return None

    def absent(field: str) -> MissingInfo:
        return unknown(field) or MissingInfo(field=field, why_needed=WHY[field], status=not_found)

    if len(re.findall(r"\w+", text)) < 8:
        out.append(MissingInfo(field="what_happened", why_needed=WHY["what_happened"]))
    def core(field: str, found: bool) -> None:
        # An explicit "I don't know the exact place" is recorded even when a partial detail ("on the bus") was given.
        entry = absent(field) if not found else unknown(field)
        if entry:
            out.append(entry)

    core("when", "datetime" in kinds)
    core("where", "location" in kinds or location_supplied)
    core("who", "person" in kinds)

    nothing_taken = [f for f in facts if f.kind == "denial" and re.search(r"nothing", f.value, re.I)]
    if nothing_taken:
        out.append(MissingInfo(field="loss_value", why_needed=WHY["loss_value"], status="explicitly_denied",
                               source_spans=nothing_taken[0].spans))
    elif "amount" not in kinds and (LOSS_WORDS.search(text) or coverage == "limited"):
        out.append(absent("loss_value"))

    if "injury" in kinds and not MEDICAL_WORDS.search(text):
        out.append(MissingInfo(field="medical_attention", why_needed=WHY["medical_attention"]))

    evidence_denials = [f for f in facts if f.kind == "evidence_reference" and f.polarity == "explicitly_denied"]
    if "evidence_reference" not in kinds and not evidence_supplied:
        out.append(MissingInfo(field="evidence", why_needed=WHY["evidence"], status="explicitly_denied",
                               source_spans=evidence_denials[0].spans) if evidence_denials
                   else MissingInfo(field="evidence", why_needed=WHY["evidence"], status=not_found))

    witness_denials = [f for f in facts if f.kind == "denial" and re.search(r"saw|witness|present|there", f.value, re.I)]
    if witness_denials:
        out.append(MissingInfo(field="witnesses", why_needed=WHY["witnesses"], status="explicitly_denied",
                               source_spans=witness_denials[0].spans))
    elif "witness_reference" not in kinds:
        out.append(MissingInfo(field="witnesses", why_needed=WHY["witnesses"], status=not_found))
    return out


def questions_for(missing: List[MissingInfo]) -> List[str]:
    order = ["what_happened", "when", "where", "who", "loss_value", "medical_attention", "evidence", "witnesses"]
    open_fields = [m.field for m in missing if m.status == "open"]
    return [QUESTIONS[f] for f in order if f in open_fields][:MAX_QUESTIONS]


def _distinct(facts: List[FactItem], kind: str, prefix: str = "") -> Dict[str, FactItem]:
    seen: Dict[str, FactItem] = {}
    for f in facts:
        if f.kind == kind and f.normalized and f.polarity != "explicitly_denied" and f.normalized.startswith(prefix):
            if "?" not in f.normalized:
                seen.setdefault(f.normalized, f)
    return seen


DATE_NORMALIZED = re.compile(r"(?:\d{4}|\?{4})-\d{2}-\d{2}")


def _minutes(t: str) -> int:
    h, m = t.lstrip("T").split(":")
    return int(h) * 60 + int(m)


# A later statement that corrects an earlier one ("actually", "sorry", "not Mahesh").
CORRECTION_CUE = re.compile(r"\b(?i:actually|sorry|correction|mistake|wrong(?:ly)?)\b|\bnot\s+[A-Z][a-z]+")


def detect_contradictions(facts: List[FactItem], statements: Optional[List[Statement]] = None) -> List[Contradiction]:
    out: List[Contradiction] = []

    def add(field: str, label: str, a: FactItem, b: FactItem, detector: str):
        out.append(Contradiction(
            contradiction_id=f"C-{len(out) + 1}",
            field=field,
            summary=(f"The account mentions different {label}: “{a.spans[0].quote}” ({a.spans[0].statement_id}) "
                     f"and “{b.spans[0].quote}” ({b.spans[0].statement_id}). Clarification requested; "
                     f"both statements are preserved."),
            spans=[a.spans[0], b.spans[0]],
            detector=detector,
        ))

    # Dates. A date given without a year ("????-10-14") is compared on day and month only; no year is
    # assumed, so "14 October" and 14/10/2026 do not conflict, but "14 October" and "15 October" do.
    dates = [f for f in facts if f.kind == "datetime" and f.polarity != "explicitly_denied" and f.normalized
             and DATE_NORMALIZED.fullmatch(f.normalized)]
    pair = next(((a, b) for i, a in enumerate(dates) for b in dates[i + 1:]
                 if a.normalized != b.normalized
                 and ("????" not in a.normalized + b.normalized or a.normalized[5:] != b.normalized[5:])), None)
    if pair:
        yearless = "????" in pair[0].normalized + pair[1].normalized
        add("date", "dates (no year was given; none is assumed)" if yearless else "dates", *pair, "rule:distinct_dates")

    times = list(_distinct(facts, "datetime", "T").items())
    for i in range(len(times)):
        for j in range(i + 1, len(times)):
            if abs(_minutes(times[i][0]) - _minutes(times[j][0])) >= 60:
                add("time", "times", times[i][1], times[j][1], "rule:distinct_times")
                break
        else:
            continue
        break

    amounts = list(_distinct(facts, "amount").values())
    if len(amounts) > 1:
        add("amount", "amounts (please clarify whether they refer to the same loss)", amounts[0], amounts[1], "rule:distinct_amounts")

    counts = list(_distinct(facts, "person", "count:").values())
    if len(counts) > 1:
        add("number_of_persons", "numbers of people", counts[0], counts[1], "rule:distinct_person_counts")

    # Names: a correcting statement that gives a different name from an earlier statement. A new name
    # without a correction may be another person and is not flagged.
    named = [f for f in facts if f.kind == "person" and (f.normalized or "").startswith("name:")
             and f.polarity != "explicitly_denied"]
    correcting = {st.statement_id for st in statements or [] if st.kind == "clarification" and CORRECTION_CUE.search(st.text)}
    order = [st.statement_id for st in statements or []]
    pair = next(((a, b) for b in named if b.spans[0].statement_id in correcting
                 for a in named if order.index(a.spans[0].statement_id) < order.index(b.spans[0].statement_id)
                 and a.normalized != b.normalized), None) if order else None
    if pair:
        add("identity", "names (please clarify whether they refer to the same person)", *pair, "rule:corrected_name")

    vehicles = list(_distinct(facts, "vehicle").values())
    if len(vehicles) > 1:
        add("vehicle", "vehicle numbers", vehicles[0], vehicles[1], "rule:distinct_vehicles")

    # A denial in one place and an assertion of the same thing elsewhere.
    denials = [f for f in facts if f.kind == "denial"]
    categories = {
        "injury": (r"hurt|injur|harm|bleed", "injury"),
        "weapon": (r"weapon|knife|gun|rod|stick|acid", "weapon"),
        "witness": (r"saw|witness|present|there", "witness_reference"),
    }
    for field, (pattern, kind) in categories.items():
        d = next((f for f in denials if re.search(pattern, f.value, re.I)), None)
        a = next((f for f in facts if f.kind == kind and f.polarity == "asserted"), None)
        if d and a:
            add(f"{field}_denied_and_asserted", f"statements about {field}", d, a, "rule:denial_vs_assertion")
    return out


EVIDENCE_TYPE_WORDS = {
    "photo": r"photo", "video": r"video|cctv|recording", "screenshot": r"screenshot", "receipt": r"receipt|bill|invoice",
    "message": r"message|chat", "bank": r"bank|transaction|upi", "medical": r"medical",
}


def associate_evidence(inputs: List[EvidenceMetadataInput], facts: List[FactItem]) -> List[EvidenceItem]:
    items: List[EvidenceItem] = []
    refs = [f for f in facts if f.kind == "evidence_reference" and f.polarity != "explicitly_denied"]
    for n, ev in enumerate(inputs, 1):
        words = " ".join([ev.evidence_type, ev.description or "", ev.file_name or ""]).lower()
        linked = []
        for key, pattern in EVIDENCE_TYPE_WORDS.items():
            if re.search(pattern, words):
                linked += [f.item_id for f in refs if re.search(pattern, f.value, re.I) and f.item_id not in linked]
        items.append(EvidenceItem(
            evidence_id=f"EV-{n}", evidence_type=ev.evidence_type, description=ev.description,
            file_name=ev.file_name, file_size_bytes=ev.file_size_bytes, sha256=ev.sha256, linked_item_ids=linked,
        ))
    return items


AUTHORISED_VERIFIER_ROLES = {"police_officer"}
RESULT_STATUS = {"consistent": "independently_verified", "inconsistent": "verification_inconsistent",
                 "could_not_verify": "could_not_verify"}


def apply_verification_events(events: List[VerificationEvent], facts: List[FactItem], evidence: List[EvidenceItem]
                              ) -> Tuple[List[FactItem], List[EvidenceItem], List[VerificationEvent], List[NodeError]]:
    """Accept only events from an authorised police role with an authorisation reference and a stated method."""
    facts = [f.model_copy() for f in facts]
    evidence = [e.model_copy() for e in evidence]
    by_id = {f.item_id: f for f in facts}
    ev_by_id = {e.evidence_id: e for e in evidence}
    accepted: List[VerificationEvent] = []
    errors: List[NodeError] = []
    for ev in events:
        problems = []
        if ev.verifier_role not in AUTHORISED_VERIFIER_ROLES:
            problems.append("verifier role is not an authorised police role")
        if not ev.authorization_reference.strip():
            problems.append("missing authorisation reference")
        if not ev.method.strip():
            problems.append("missing verification method")
        if ev.target_id not in by_id and ev.target_id not in ev_by_id:
            problems.append("unknown target")
        if problems:
            errors.append(NodeError(node="associate_evidence", error_type="RejectedVerificationEvent",
                                    message=f"{ev.event_id}: " + "; ".join(problems)))
            continue
        status = RESULT_STATUS[ev.result]
        if ev.target_id in by_id:
            by_id[ev.target_id].verification_status = status
        else:
            item = ev_by_id[ev.target_id]
            item.verification_status = status
            item.custody_status = "examined_by_police"
            item.authenticity_status = "assessed_by_police"
        accepted.append(ev)
    return facts, evidence, accepted, errors
