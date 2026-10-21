"""
Evaluates the complaint-structuring workflow (complaint_engine) on synthetic cases with gold annotations.

    .venv/bin/python benchmark/structuring/evaluate_structuring.py --out <report.json>

Offline: no Gemini, no network, no external tracing. Synthetic data only. The results describe this
synthetic set; they say nothing about real-world police effectiveness.

ANNOTATION GUIDE (gold in structuring_cases.json, written before the first run)
  people     persons other than the complainant: descriptions ("two men"), relations ("my friend Priya"),
             names. Excludes pronouns and indefinites (he, someone, one of them).
  datetime   each date (absolute or relative) and each time or part of day, separately.
  location   places and landmarks relevant to the incident.
  action     the verb(s) of what others allegedly did ("snatched", "broke into").
  loss       items taken or damaged, and money amounts.
  witness    phrases saying someone saw / was present, or that nobody did.
  evidence   material referred to (photos, screenshots, certificates, CCTV).
  pol        asserted (default) | denied (explicitly negated) | uncertain (hedged, approximate, speculative
             or hearsay).
  missing    expected status per field: not_listed | open | unknown_to_complainant | explicitly_denied |
             not_determined (a list means any of them is acceptable).
  contradictions  fields expected to be flagged (date, time, amount, number_of_persons, identity,
             injury_/weapon_/witness_denied_and_asserted).

METRICS (defined before evaluation)
  Extraction, per category and micro-averaged. Predicted kinds map to categories: person->people,
  datetime->datetime, location->location, alleged_action->action, amount/property->loss,
  witness_reference->witness, evidence_reference->evidence.
    A predicted item is SUPPORTED if a gold item of the same category overlaps it in the same statement
    by at least half of the shorter span, or one text contains the other (case-insensitive, ignoring a
    leading my/the/a/an/his/her/our/mera/meri/mere). A gold item is FOUND if a supported prediction
    matches it. precision = supported / predicted; recall = found / gold.
  Polarity accuracy: share of found gold items whose matching prediction has the same polarity.
  Unsupported-fact rate = (unsupported predictions + overstated predictions) / predictions, where
    overstated = a prediction marked asserted whose gold item is denied or uncertain.
  Integrity counts (must be 0): quotes not verbatim in the statement; items marked verified without a
    police verification event; submission status other than draft-only; contradictions without two
    verbatim quotes, or with dishonesty wording; original statements not preserved verbatim.
  Missing information: per-field status accuracy; "false missing" = reported open when gold is not open;
    "missed missing" = gold open but not reported open.
  Contradictions: precision and recall over (case, field) pairs.
  Language: coverage label matches gold; limited-coverage cases routed to human review.
  Jurisdiction: status and station both equal the expected value; "unsafe" = a station named where the
    expected answer names none. Synthetic boundaries make the expected answers true by construction;
    "real" cases only check safety on the repository's unverified boundary data.
  Draft: a readable draft exists and passes every check (sections present, statement verbatim, every
    extracted detail quoted, checklist present, no claim of FIR registration, submission, verification
    or signature).
"""

import argparse
import json
import os
import re
import sys
import tempfile
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.environ["BANDHOO_SKIP_DOTENV"] = "1"

from complaint_engine import run_structuring  # noqa: E402
from complaint_engine.jurisdiction import assess_point, load_boundaries  # noqa: E402
from complaint_engine.models import ComplaintStructureRequest  # noqa: E402

CATEGORIES = ["people", "datetime", "location", "action", "loss", "witness", "evidence"]
KIND_TO_CATEGORY = {"person": "people", "datetime": "datetime", "location": "location", "alleged_action": "action",
                    "amount": "loss", "property": "loss", "witness_reference": "witness",
                    "evidence_reference": "evidence"}
POLARITY = {"asserted": "asserted", "explicitly_denied": "denied", "uncertain": "uncertain"}
MISSING_FIELDS = ["what_happened", "when", "where", "who", "loss_value", "evidence", "witnesses"]
LEADING = re.compile(r"^(?:my|the|a|an|his|her|our|mera|meri|mere)\s+", re.I)
DISHONESTY = re.compile(r"\b(?:lie|lies|lying|liar|false|falsely|dishonest\w*|fabricat\w*|untrue|fake)\b", re.I)
FORBIDDEN_DRAFT_CLAIMS = [
    re.compile(r"\bFIR\s+(?:No\.?|number|registered)", re.I),
    re.compile(r"\bhas been (?:submitted|registered|verified|received)\b", re.I),
    re.compile(r"\b(?:digitally signed|e-signed|electronically signed)\b", re.I),
    re.compile(r"\b(?:verified|reviewed|approved) by (?:the )?(?:police|officer)\b", re.I),
]
DRAFT_SECTIONS = ["COMPLAINANT'S ACCOUNT", "DETAILS FROM THE ACCOUNT", "MISSING INFORMATION",
                  "POSSIBLE INCONSISTENCIES", "SUPPORTING MATERIAL", "JURISDICTION", "VERIFICATION CHECKLIST"]


def _norm(text):
    return LEADING.sub("", text.strip().lower())


def _locate(gold_item, texts):
    sids = [gold_item["in"]] if "in" in gold_item else list(texts)
    for sid in sids:
        pos = texts[sid].find(gold_item["q"])
        if pos >= 0:
            return sid, pos, pos + len(gold_item["q"])
    raise ValueError(f"gold quote not found: {gold_item['q']}")


def _matches(pred, gold, texts):
    sid, gs, ge = _locate(gold, texts)
    for span in pred["spans"]:
        if span["statement_id"] == sid:
            overlap = min(ge, span["end"]) - max(gs, span["start"])
            if overlap > 0 and overlap >= 0.5 * min(ge - gs, span["end"] - span["start"]):
                return True
    p, g = _norm(pred["value"]), _norm(gold["q"])
    return len(min(p, g, key=len)) >= 3 and (p in g or g in p)


def _ratio(a, b):
    return round(a / b, 4) if b else None


def evaluate_case(case):
    req = ComplaintStructureRequest(statement=case["statement"], clarifications=case["clarifications"],
                                    evidence=case["evidence"])
    state = run_structuring(req)
    report = state["report"]
    texts = {"S1": case["statement"], **{f"S{n}": t for n, t in enumerate(case["clarifications"], 2)}}
    gold = case["gold"]
    facts = [f.model_dump() for f in state.get("facts") or [] if f.provenance == "complainant_statement"]
    out = {"id": case["id"], "split": case["split"], "group": case["group"], "categories": {}, "integrity": {}}

    unsupported = overstated = predicted_total = 0
    pol_ok = pol_n = 0
    for cat in CATEGORIES:
        preds = [f for f in facts if KIND_TO_CATEGORY.get(f["kind"]) == cat]
        golds = gold[cat]
        supported = [p for p in preds if any(_matches(p, g, texts) for g in golds)]
        found, pol_details = 0, []
        for g in golds:
            m = next((p for p in preds if _matches(p, g, texts)), None)
            if m:
                found += 1
                gp, pp = g.get("pol", "asserted"), POLARITY[m["polarity"]]
                pol_n += 1
                pol_ok += gp == pp
                if gp != pp:
                    pol_details.append({"gold": g["q"], "expected": gp, "predicted": pp})
        for p in supported:
            g = next(g for g in golds if _matches(p, g, texts))
            if p["polarity"] == "asserted" and g.get("pol", "asserted") != "asserted":
                overstated += 1
        unsupported += len(preds) - len(supported)
        predicted_total += len(preds)
        out["categories"][cat] = {
            "gold": len(golds), "predicted": len(preds), "supported": len(supported), "found": found,
            "missed": [g["q"] for g in golds if not any(_matches(p, g, texts) for p in preds)],
            "unsupported": [p["value"] for p in preds if p not in supported],
            "polarity_errors": pol_details,
        }
    out["polarity"] = {"correct": pol_ok, "assessed": pol_n}
    out["unsupported"] = {"unsupported": unsupported, "overstated": overstated, "predicted": predicted_total}

    # Integrity
    bad_quotes = sum(1 for f in state.get("facts") or [] for s in f.spans
                     if texts.get(s.statement_id, "")[s.start:s.end] != s.quote)
    verified = len(report.get("independently_verified") or [])
    contradictions = report.get("contradictions") or []
    bad_contradictions = sum(1 for c in contradictions
                             if len(c["spans"]) != 2 or DISHONESTY.search(c["summary"])
                             or any(texts.get(s["statement_id"], "")[s["start"]:s["end"]] != s["quote"] for s in c["spans"]))
    preserved = [s["text"] for s in report.get("complainant_statements") or []] == list(texts.values())
    out["integrity"] = {
        "non_verbatim_quotes": bad_quotes,
        "unbacked_verification_claims": verified,
        "non_draft_submission_status": 0 if str(report.get("submission_status", "")).startswith("draft_only") else 1,
        "invalid_contradictions": bad_contradictions,
        "statements_not_preserved": 0 if preserved else 1,
    }

    # Missing information
    predicted_missing = {m["field"]: m["status"] for m in report.get("missing_information") or []}
    fields = {}
    for field in MISSING_FIELDS:
        expected = gold["missing"][field]
        expected = expected if isinstance(expected, list) else [expected]
        got = predicted_missing.get(field, "not_listed")
        fields[field] = {"expected": expected, "predicted": got, "correct": got in expected,
                         "false_missing": got == "open" and "open" not in expected,
                         "missed_missing": "open" in expected and got != "open"}
    out["missing"] = fields

    # Contradictions
    pred_fields = sorted({c["field"] for c in contradictions})
    out["contradictions"] = {"expected": sorted(gold["contradictions"]), "predicted": pred_fields}

    # Language and routing
    coverage = (report.get("language_coverage") or {}).get("coverage", "not_reported")
    route = (report.get("review") or {}).get("route")
    out["language"] = {"expected": gold["coverage"], "predicted": coverage, "route": route,
                       "correct": coverage == gold["coverage"] and (gold["coverage"] != "limited" or route == "human_review_required")}

    # Draft
    draft = report.get("draft_text")
    checks = {}
    if isinstance(draft, str) and draft.strip():
        checks["sections_present"] = all(h in draft for h in DRAFT_SECTIONS)
        checks["statements_verbatim"] = all(t in draft for t in texts.values())
        checks["details_quoted"] = all(f"“{f['value']}”" in draft for f in facts
                                       if KIND_TO_CATEGORY.get(f["kind"]) and f["polarity"] != "explicitly_denied")
        checks["checklist_present"] = all(item in draft for item in report.get("verification_checklist_for_officer") or [])
        checks["no_forbidden_claims"] = not any(r.search(draft) for r in FORBIDDEN_DRAFT_CLAIMS)
    out["draft"] = {"present": bool(checks), "checks": checks, "passed": bool(checks) and all(checks.values())}
    return out


def evaluate_jurisdiction(data):
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        synthetic = os.path.join(tmp, "synthetic.geojson")
        with open(synthetic, "w") as fh:
            json.dump(data["synthetic_boundaries"], fh)
        paths = {"synthetic": synthetic, "missing_file": os.path.join(tmp, "absent.geojson"), "real": None}
        for case in data["jurisdiction_cases"]:
            load_boundaries.cache_clear()
            loc = case["location"] or {}
            kwargs = {"path": paths[case["boundaries"]]} if paths[case["boundaries"]] else {}
            r = assess_point(loc.get("latitude"), loc.get("longitude"), **kwargs)
            exp = case["expected"]
            results.append({"id": case["id"], "boundaries": case["boundaries"], "expected": exp,
                            "predicted": {"status": r.status, "station": r.station},
                            "correct": r.status == exp["status"] and r.station == exp["station"],
                            "unsafe": exp["station"] is None and r.station is not None})
    load_boundaries.cache_clear()
    return results


def summarise(cases):
    s = {"cases": len(cases), "extraction": {}, "integrity": defaultdict(int)}
    tot = defaultdict(int)
    for cat in CATEGORIES:
        g = sum(c["categories"][cat]["gold"] for c in cases)
        p = sum(c["categories"][cat]["predicted"] for c in cases)
        sup = sum(c["categories"][cat]["supported"] for c in cases)
        f = sum(c["categories"][cat]["found"] for c in cases)
        s["extraction"][cat] = {"gold": g, "predicted": p, "precision": _ratio(sup, p), "recall": _ratio(f, g)}
        tot["g"] += g; tot["p"] += p; tot["s"] += sup; tot["f"] += f
    s["extraction"]["micro"] = {"gold": tot["g"], "predicted": tot["p"], "precision": _ratio(tot["s"], tot["p"]),
                                "recall": _ratio(tot["f"], tot["g"])}
    pol_ok = sum(c["polarity"]["correct"] for c in cases)
    pol_n = sum(c["polarity"]["assessed"] for c in cases)
    s["polarity_accuracy"] = {"correct": pol_ok, "assessed": pol_n, "accuracy": _ratio(pol_ok, pol_n)}
    uns = sum(c["unsupported"]["unsupported"] for c in cases)
    over = sum(c["unsupported"]["overstated"] for c in cases)
    pred = sum(c["unsupported"]["predicted"] for c in cases)
    s["unsupported_fact_rate"] = {"unsupported": uns, "overstated": over, "predicted": pred,
                                  "rate": _ratio(uns + over, pred)}
    for c in cases:
        for k, v in c["integrity"].items():
            s["integrity"][k] += v
    s["integrity"] = dict(s["integrity"])
    fields = [f for c in cases for f in c["missing"].values()]
    s["missing_information"] = {"fields": len(fields), "accuracy": _ratio(sum(f["correct"] for f in fields), len(fields)),
                                "false_missing": sum(f["false_missing"] for f in fields),
                                "missed_missing": sum(f["missed_missing"] for f in fields)}
    exp = {(c["id"], f) for c in cases for f in c["contradictions"]["expected"]}
    got = {(c["id"], f) for c in cases for f in c["contradictions"]["predicted"]}
    s["contradictions"] = {"expected": len(exp), "predicted": len(got), "correct": len(exp & got),
                           "precision": _ratio(len(exp & got), len(got)), "recall": _ratio(len(exp & got), len(exp)),
                           "missed": sorted(f"{a}:{b}" for a, b in exp - got),
                           "spurious": sorted(f"{a}:{b}" for a, b in got - exp)}
    s["language"] = {"correct": sum(c["language"]["correct"] for c in cases), "cases": len(cases)}
    s["draft"] = {"passed": sum(c["draft"]["passed"] for c in cases), "cases": len(cases)}
    return s


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--cases", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "structuring_cases.json"))
    parser.add_argument("--out", default=None, help="write the full JSON report here")
    args = parser.parse_args()
    with open(args.cases, encoding="utf-8") as fh:
        data = json.load(fh)
    load_boundaries.cache_clear()
    cases = [evaluate_case(c) for c in data["cases"]]
    jur = evaluate_jurisdiction(data)
    result = {
        "note": "Synthetic cases only; results do not measure real-world police effectiveness.",
        "summary": {split: summarise([c for c in cases if split == "all" or c["split"] == split])
                    for split in ("dev", "heldout", "all")},
        "jurisdiction": {"correct": sum(r["correct"] for r in jur), "cases": len(jur),
                         "unsafe": sum(r["unsafe"] for r in jur), "results": jur},
        "cases": cases,
    }
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=1)
    for split in ("dev", "heldout", "all"):
        s = result["summary"][split]
        e = s["extraction"]
        print(f"[{split}] {s['cases']} cases")
        for cat in CATEGORIES + ["micro"]:
            print(f"   {cat:10s} P={e[cat]['precision']} R={e[cat]['recall']} (gold {e[cat]['gold']}, predicted {e[cat]['predicted']})")
        print(f"   polarity {s['polarity_accuracy']}  unsupported {s['unsupported_fact_rate']}")
        print(f"   missing {s['missing_information']}")
        print(f"   contradictions P={s['contradictions']['precision']} R={s['contradictions']['recall']} "
              f"missed={s['contradictions']['missed']} spurious={s['contradictions']['spurious']}")
        print(f"   language {s['language']}  draft {s['draft']}  integrity {s['integrity']}")
    print(f"[jurisdiction] correct {result['jurisdiction']['correct']}/{result['jurisdiction']['cases']}, unsafe {result['jurisdiction']['unsafe']}")


if __name__ == "__main__":
    main()
