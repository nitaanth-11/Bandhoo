"""
Read-only corpus audit: compares bns_rag_dataset.json against Gazette BNS text and BNSS Schedule I rows.

Usage:
    python reports/corpus_audit.py <bns_rag_dataset.json> <bns_gazette.txt> <bnss_gazette.txt> <repo_root> <out.json>

The two .txt inputs are plain-text extractions of the Gazette of India (Extraordinary) PDFs of the
Bharatiya Nyaya Sanhita, 2023 (Act 45 of 2023) and the Bharatiya Nagarik Suraksha Sanhita, 2023
(Act 46 of 2023), both dated 25 December 2023. They are not stored in this repository.
Similarity scores are a screening signal only: Gazette margin notes and page furniture lower the
score for short sections, and Schedule I rows that wrap across lines are not always parsed.
The script never modifies the corpus.
"""
import difflib
import json
import re
import sys
from collections import Counter

corpus_path, bns_txt, bnss_txt, registry_dir, out_path = sys.argv[1:6]
sys.path.insert(0, registry_dir)
from legal_engine.schedule_registry import VERIFIED_SCHEDULE_I, resolve_schedule_classification  # noqa: E402

corpus = {int(r["section"]): r for r in json.load(open(corpus_path, encoding="utf-8"))}

# ── Gazette BNS: split into sections 1..358 sequentially ──
NOISE = re.compile(r"^(=====PAGE|THE GAZETTE OF INDIA|_{5,}|Sec\. \d|\[PART II|\d{1,3}$)")
lines = [l for l in open(bns_txt, encoding="utf-8").read().splitlines() if not NOISE.match(l.strip())]
gazette, cur, buf = {}, 0, []
for line in lines:
    m = re.match(r"^\s*(\d{1,3})\s*\.\s*", line)
    if m and int(m.group(1)) == cur + 1:
        if cur:
            gazette[cur] = " ".join(buf)
        cur, buf = int(m.group(1)), [line[m.end():]]
    elif cur:
        buf.append(line)
if cur:
    gazette[cur] = " ".join(buf)


def norm_tokens(text):
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"\(\s*\d+\s*\)|\(\s*[a-z]\s*\)|•", " ", text.lower())
    return re.findall(r"[a-z0-9]+", text)


CLASS_BLOCK = re.compile(r"BNSS Classification.*", re.S)

# ── Gazette Schedule I Part I rows: section -> list of (cog, bail) ──
sched_lines = open(bnss_txt, encoding="utf-8").read().splitlines()
start = next(i for i, l in enumerate(sched_lines) if l.strip() == "I.—OFFENCES UNDER THE BHARATIYA NYAYA SANHITA")
end = next(i for i, l in enumerate(sched_lines) if i > start and l.strip().startswith("II.—"))
sched_rows = {}
for l in sched_lines[start:end]:
    m = re.match(r"^(\d{1,3})(\(\s*\d+\s*\))?\s", l)
    if not m or not (1 <= int(m.group(1)) <= 358):
        continue
    cog = "non" if re.search(r"Non-\s*cognizable", l) else ("cog" if "Cognizable" in l else None)
    bail = "non" if re.search(r"Non\s*-\s*bailable", l) else ("bail" if "Bailable" in l else None)
    sec = int(m.group(1))
    sched_rows.setdefault(sec, []).append({"row": l.split()[0] + (m.group(2) or "").replace(" ", ""), "cog": cog, "bail": bail})

results = {}
for sec in range(1, 359):
    rec = corpus[sec]
    text = rec.get("text") or ""
    statutory_part = CLASS_BLOCK.sub("", text)
    g = gazette.get(sec, "")
    ct, gt = norm_tokens(statutory_part), norm_tokens(g)
    sm = difflib.SequenceMatcher(None, ct, gt, autojunk=False)
    ratio = round(sm.ratio(), 3)
    gcount, ccount = Counter(gt), Counter(ct)
    coverage = round(sum(min(n, ccount[w]) for w, n in gcount.items()) / max(1, len(gt)), 3)
    pun = (rec.get("punishment") or "").strip()
    pun_tokens = " ".join(norm_tokens(pun))
    embedded = CLASS_BLOCK.search(text)
    emb_cog = emb_bail = None
    if embedded:
        b = embedded.group(0)
        emb_cog = "non" if re.search(r"Non-cognizable", b, re.I) else ("cog" if re.search(r"Cognizable", b) else None)
        emb_bail = "non" if re.search(r"Non-bailable", b, re.I) else ("bail" if re.search(r"Bailable", b) else None)
    results[sec] = {
        "title": rec.get("title"),
        "verified_flag": rec.get("verified"),
        "source": rec.get("source"),
        "similarity_to_gazette": ratio,
        "gazette_token_coverage": coverage,
        "gazette_has_punishment_clause": bool(re.search(r"shall be punish|punishable with|be punished", g)),
        "punishment_empty": not pun,
        "punishment_in_gazette_text": bool(pun) and pun_tokens in " ".join(gt),
        "punishment_has_penalty_terms": bool(re.search(r"imprisonment|fine|death|community service|punished with", pun, re.I)),
        "in_schedule_i_part_i": sec in sched_rows,
        "schedule_rows": sched_rows.get(sec, []),
        "embedded_classification_block": bool(embedded),
        "embedded_cog": emb_cog,
        "embedded_bail": emb_bail,
        "in_registry": sec in VERIFIED_SCHEDULE_I,
    }

# ── Summaries ──
sims = [r["similarity_to_gazette"] for r in results.values()]
summary = {
    "gazette_sections_parsed": len(gazette),
    "similarity_buckets": {
        ">=0.95": sum(s >= 0.95 for s in sims),
        "0.85-0.95": sum(0.85 <= s < 0.95 for s in sims),
        "0.70-0.85": sum(0.70 <= s < 0.85 for s in sims),
        "<0.70": sum(s < 0.70 for s in sims),
    },
    "low_similarity_sections": sorted((s for s, r in results.items() if r["similarity_to_gazette"] < 0.85),
                                      key=lambda s: results[s]["similarity_to_gazette"]),
    "empty_punishment": [s for s, r in results.items() if r["punishment_empty"]],
}
summary["empty_punishment_with_gazette_punishment_clause"] = [s for s in summary["empty_punishment"] if results[s]["gazette_has_punishment_clause"]]
summary["empty_punishment_in_schedule_i"] = [s for s in summary["empty_punishment"] if results[s]["in_schedule_i_part_i"]]
summary["punishment_without_penalty_terms"] = [s for s, r in results.items() if not r["punishment_empty"] and not r["punishment_has_penalty_terms"]]
summary["punishment_not_found_in_gazette_text"] = [s for s, r in results.items() if not r["punishment_empty"] and not r["punishment_in_gazette_text"]]
summary["embedded_classification_sections"] = sum(r["embedded_classification_block"] for r in results.values())

mismatch = []
for s, r in results.items():
    rows = r["schedule_rows"]
    if not r["embedded_classification_block"] or not rows:
        continue
    row_pairs = {(x["cog"], x["bail"]) for x in rows}
    if (r["embedded_cog"], r["embedded_bail"]) not in row_pairs:
        mismatch.append({"section": s, "embedded": [r["embedded_cog"], r["embedded_bail"]], "schedule_rows": rows})
summary["embedded_vs_gazette_schedule_mismatches"] = mismatch

reg = []
for s, entry in VERIFIED_SCHEDULE_I.items():
    r = results[s]
    res = resolve_schedule_classification(s)
    reg.append({
        "section": s,
        "registry_title": entry["title"],
        "corpus_title": r["title"],
        "titles_match": entry["title"].rstrip(".").lower() == (r["title"] or "").rstrip(".").lower(),
        "registry_cog": res["is_cognizable"], "registry_bail": res["is_bailable"],
        "embedded": [r["embedded_cog"], r["embedded_bail"]],
        "gazette_rows": r["schedule_rows"],
        "corpus_schedule_i_status_field": corpus[s].get("schedule_i_status"),
        "corpus_punishment_head": (corpus[s].get("punishment") or "")[:90],
    })
summary["registry_vs_corpus"] = reg
summary["schedule_i_status_field_values"] = dict(Counter(r.get("schedule_i_status") for r in corpus.values()))
summary["verified_flag_values"] = dict(Counter(str(r.get("verified")) for r in corpus.values()))
summary["source_values"] = dict(Counter(r.get("source") for r in corpus.values()))

json.dump({"summary": summary, "sections": results}, open(out_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
s = summary
print("parsed", s["gazette_sections_parsed"], "buckets", s["similarity_buckets"])
print("low sim", [(x, results[x]["similarity_to_gazette"]) for x in s["low_similarity_sections"]])
print("empty punishment", len(s["empty_punishment"]), "| with gazette punishment clause", len(s["empty_punishment_with_gazette_punishment_clause"]), s["empty_punishment_with_gazette_punishment_clause"])
print("empty & in schedule I", s["empty_punishment_in_schedule_i"])
print("punishment w/o penalty terms", s["punishment_without_penalty_terms"])
print("punishment not in gazette text", len(s["punishment_not_found_in_gazette_text"]), s["punishment_not_found_in_gazette_text"][:30])
print("embedded classification sections", s["embedded_classification_sections"], "mismatches", len(mismatch))
for m in mismatch[:20]:
    print("  ", m)
for r in reg:
    print(" REG", r["section"], r["titles_match"], r["registry_cog"], r["registry_bail"], r["embedded"], [(x["row"], x["cog"], x["bail"]) for x in r["gazette_rows"]])
print(s["schedule_i_status_field_values"], s["verified_flag_values"])
