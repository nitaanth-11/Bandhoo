"""
One-off corpus integrity migration for bns_rag_dataset.json (run 2026-10-20).

Usage:
    python reports/apply_corpus_corrections.py <dataset.json> <bns_gazette.txt> <corrections_log.json>

<bns_gazette.txt> is a plain-text extraction (pypdf) of the Gazette of India (Extraordinary) PDF of
the Bharatiya Nyaya Sanhita, 2023 (No. 45 of 2023, 25 December 2023), as hosted by PRS Legislative
Research. It is not stored in this repository.

What it does:
1. Moves each scraped "BNSS Classification" block out of `text` into `scraped_procedural_classification`
   (unverified, secondary source). `text` then holds only statutory text.
2. Applies the hand-transcribed CORRECTIONS below. Every replacement is checked automatically: its
   words must occur, in order and contiguously, in the Gazette text of the same section. A failed
   check aborts the migration.
3. Records per-record verification evidence and replaces the blanket `verified: true` with a value
   derived from that evidence. `verified` is true only when the stored text is consistent with the
   Gazette under the automated check (or was restored from it). This is not legal verification.
4. Writes a corrections log with previous values, replacements, source passages and method.

Refuses to run on a dataset that has already been migrated. Any validation failure exits before
anything is written. Before writing, it takes a timestamped backup in reports/backups/, verifies the
copy byte-for-byte, and then replaces the dataset atomically.
"""

import difflib
import json
import os
import re
import sys
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
from legal_engine.corpus_guard import backup_with_verification  # noqa: E402

CHECKED_ON = "2026-10-20"
SOURCE_DOCUMENT = (
    "The Bharatiya Nyaya Sanhita, 2023 (No. 45 of 2023), Gazette of India Extraordinary, Part II, Section 1, "
    "25 December 2023 (PDF hosted by PRS Legislative Research)"
)
SCRAPED_SOURCE_NOTE = (
    "Scraped from a secondary website together with the statutory text. Not part of the BNS. Not verified "
    "against the BNSS First Schedule unless gazette_check says otherwise. Authoritative procedural metadata "
    "for verified sections is in legal_engine/schedule_registry.py."
)
TRANSCRIPTION_METHOD = (
    "Manual transcription from the Gazette text extraction (line breaks joined, margin notes and page "
    "furniture removed, PDF kerning artefacts repaired), checked automatically as a contiguous word "
    "sequence of the Gazette section."
)

P309 = {
    "309(4)": "shall be punished with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine; and, if the robbery be committed on the highway between sunset and sunrise, the imprisonment may be extended to fourteen years.",
    "309(5)": "shall be punished with rigorous imprisonment for a term which may extend to seven years, and shall also be liable to fine.",
    "309(6)": "shall be punished with imprisonment for life, or with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine.",
}
P111 = {
    "111(2)": "shall,— (a) if such offence has resulted in the death of any person, be punished with death or imprisonment for life, and shall also be liable to fine which shall not be less than ten lakh rupees; (b) in any other case, be punished with imprisonment for a term which shall not be less than five years but which may extend to imprisonment for life, and shall also be liable to fine which shall not be less than five lakh rupees.",
    "111(3)": "shall be punished with imprisonment for a term which shall not be less than five years but which may extend to imprisonment for life, and shall also be liable to fine which shall not be less than five lakh rupees.",
    "111(4)": "shall be punished with imprisonment for a term which shall not be less than five years but which may extend to imprisonment for life, and shall also be liable to fine which shall not be less than five lakh rupees.",
    "111(5)": "shall be punished with imprisonment for a term which shall not be less than three years but which may extend to imprisonment for life, and shall also be liable to fine which shall not be less than five lakh rupees:",
    "111(6)": "shall be punishable with imprisonment for a term which shall not be less than three years but which may extend to imprisonment for life and shall also be liable to fine which shall not be less than two lakh rupees.",
    "111(7)": "shall be punishable with imprisonment for a term which shall not be less than three years but which may extend to imprisonment for ten years and shall also be liable to fine which shall not be less than one lakh rupees.",
}
P120 = {
    "120(1)": "shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
    "120(2)": "shall be punished with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine.",
}
P341 = {
    "341(1)": "shall be punished with imprisonment for life, or with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
    "341(2)": "shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
    "341(3)": "shall be punished with imprisonment of either description for a term which may extend to three years, and shall also be liable to fine.",
}

TEXT_111 = (
    "(1) Any continuing unlawful activity including kidnapping, robbery, vehicle theft, extortion, land grabbing, contract killing, "
    "economic offence, cyber-crimes, trafficking of persons, drugs, weapons or illicit goods or services, human trafficking for "
    "prostitution or ransom, by any person or a group of persons acting in concert, singly or jointly, either as a member of an "
    "organised crime syndicate or on behalf of such syndicate, by use of violence, threat of violence, intimidation, coercion, or by "
    "any other unlawful means to obtain direct or indirect material benefit including a financial benefit, shall constitute organised crime.\n\n"
    "Explanation.—For the purposes of this sub-section,—\n\n"
    "(i) “organised crime syndicate” means a group of two or more persons who, acting either singly or jointly, as a syndicate or gang "
    "indulge in any continuing unlawful activity;\n\n"
    "(ii) “continuing unlawful activity” means an activity prohibited by law which is a cognizable offence punishable with imprisonment "
    "of three years or more, undertaken by any person, either singly or jointly, as a member of an organised crime syndicate or on behalf "
    "of such syndicate in respect of which more than one charge-sheets have been filed before a competent Court within the preceding "
    "period of ten years and that Court has taken cognizance of such offence, and includes economic offence;\n\n"
    "(iii) “economic offence” includes criminal breach of trust, forgery, counterfeiting of currency-notes, bank-notes and Government "
    "stamps, hawala transaction, mass-marketing fraud or running any scheme to defraud several persons or doing any act in any manner "
    "with a view to defraud any bank or financial institution or any other institution or organisation for obtaining monetary benefits "
    "in any form.\n\n"
    "(2) Whoever commits organised crime shall,—\n\n"
    "(a) if such offence has resulted in the death of any person, be punished with death or imprisonment for life, and shall also be "
    "liable to fine which shall not be less than ten lakh rupees;\n\n"
    "(b) in any other case, be punished with imprisonment for a term which shall not be less than five years but which may extend to "
    "imprisonment for life, and shall also be liable to fine which shall not be less than five lakh rupees.\n\n"
    "(3) Whoever abets, attempts, conspires or knowingly facilitates the commission of an organised crime, or otherwise engages in any "
    "act preparatory to an organised crime, shall be punished with imprisonment for a term which shall not be less than five years but "
    "which may extend to imprisonment for life, and shall also be liable to fine which shall not be less than five lakh rupees.\n\n"
    "(4) Any person who is a member of an organised crime syndicate shall be punished with imprisonment for a term which shall not be "
    "less than five years but which may extend to imprisonment for life, and shall also be liable to fine which shall not be less than "
    "five lakh rupees.\n\n"
    "(5) Whoever, intentionally, harbours or conceals any person who has committed the offence of an organised crime shall be punished "
    "with imprisonment for a term which shall not be less than three years but which may extend to imprisonment for life, and shall also "
    "be liable to fine which shall not be less than five lakh rupees:\n\n"
    "Provided that this sub-section shall not apply to any case in which the harbour or concealment is by the spouse of the offender.\n\n"
    "(6) Whoever possesses any property derived or obtained from the commission of an organised crime or proceeds of any organised crime "
    "or which has been acquired through the organised crime, shall be punishable with imprisonment for a term which shall not be less "
    "than three years but which may extend to imprisonment for life and shall also be liable to fine which shall not be less than two "
    "lakh rupees.\n\n"
    "(7) If any person on behalf of a member of an organised crime syndicate is, or at any time has been in possession of movable or "
    "immovable property which he cannot satisfactorily account for, shall be punishable with imprisonment for a term which shall not be "
    "less than three years but which may extend to imprisonment for ten years and shall also be liable to fine which shall not be less "
    "than one lakh rupees."
)

TEXT_120 = (
    "(1) Whoever voluntarily causes hurt for the purpose of extorting from the sufferer or from any person interested in the sufferer, "
    "any confession or any information which may lead to the detection of an offence or misconduct, or for the purpose of constraining "
    "the sufferer or any person interested in the sufferer to restore or to cause the restoration of any property or valuable security "
    "or to satisfy any claim or demand, or to give information which may lead to the restoration of any property or valuable security, "
    "shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.\n\n"
    "Illustrations.\n\n"
    "(a) A, a police officer, tortures Z in order to induce Z to confess that he committed a crime. A is guilty of an offence under this section.\n\n"
    "(b) A, a police officer, tortures B to induce him to point out where certain stolen property is deposited. A is guilty of an offence "
    "under this section.\n\n"
    "(c) A, a revenue officer, tortures Z in order to compel him to pay certain arrears of revenue due from Z. A is guilty of an offence "
    "under this section.\n\n"
    "(2) Whoever voluntarily causes grievous hurt for any purpose referred to in sub-section (1), shall be punished with imprisonment of "
    "either description for a term which may extend to ten years, and shall also be liable to fine."
)


def labelled(provisions):
    # "Section 309(4): ..." labels are added metadata, not statutory text.
    return " ".join(f"Section {sub}: {text}" for sub, text in provisions.items())


# Each correction: field -> new value, plus punishment_status and the defect it fixes.
CORRECTIONS = {
    309: {"defect": "Punishment field held the end of Illustration (d) instead of the punishment clauses.",
          "punishment": labelled(P309), "punishment_provisions": P309},
    311: {"defect": "Punishment field held a garbled fragment.",
          "punishment": "the imprisonment with which such offender shall be punished shall not be less than seven years."},
    312: {"defect": "Punishment field held a garbled fragment.",
          "punishment": "the imprisonment with which such offender shall be punished shall not be less than seven years."},
    264: {"defect": "Punishment field was empty although the section prescribes punishment.",
          "punishment": "shall be punished— (a) if he does so intentionally, with imprisonment of either description for a term which may "
                        "extend to three years, or with fine, or with both; and (b) if he does so negligently, with simple imprisonment for "
                        "a term which may extend to two years, or with fine, or with both."},
    111: {"defect": "Stored text held only an Explanation ('proceeds of any organised crime') that does not appear in the Gazette "
                    "text; the operative provision and punishments were missing.",
          "text": TEXT_111, "punishment": labelled(P111), "punishment_provisions": P111},
    120: {"defect": "Stored text began at the Illustrations; sub-sections (1) and (2) were missing. Punishment field empty.",
          "text": TEXT_120, "punishment": labelled(P120), "punishment_provisions": P120},
    13: {"defect": "Punishment field began with part of the offence description.",
         "punishment": "shall be subject for every such subsequent offence to imprisonment for life, or to imprisonment of either "
                       "description for a term which may extend to ten years."},
    56: {"defect": "Punishment field began with part of the offence description and omitted the public-servant limb.",
         "punishment": "be punished with imprisonment of any description provided for that offence for a term which may extend to "
                       "one-fourth part of the longest term provided for that offence; or with such fine as is provided for that offence, "
                       "or with both; and if the abettor or the person abetted is a public servant, whose duty it is to prevent the "
                       "commission of such offence, the abettor shall be punished with imprisonment of any description provided for that "
                       "offence, for a term which may extend to one-half of the longest term provided for that offence, or with such fine "
                       "as is provided for the offence, or with both."},
    58: {"defect": "Punishment field began with part of the offence description.",
         "punishment": "shall,— (a) if that offence be committed, be punished with imprisonment of either description for a term which may "
                       "extend to seven years; or (b) if the offence be not committed, with imprisonment of either description, for a term "
                       "which may extend to three years, and shall also be liable to fine."},
    71: {"defect": "Punishment field began with part of the offence description, citing sections that differ from the Gazette (67 instead of 70).",
         "punishment": "shall be punished with imprisonment for life which shall mean imprisonment for the remainder of that person’s "
                       "natural life, or with death."},
    148: {"defect": "Punishment field began with part of the offence description, citing section 145 instead of 147.",
          "punishment": "shall be punished with imprisonment for life, or with imprisonment of either description which may extend to "
                        "ten years, and shall also be liable to fine."},
    199: {"defect": "Punishment field began with part of the offence description, citing a list of sections that differs from the Gazette.",
          "punishment": "shall be punished with rigorous imprisonment for a term which shall not be less than six months but which may "
                        "extend to two years, and shall also be liable to fine."},
    251: {"defect": "Punishment field began with part of the offence description.",
          "punishment": "shall,— (a) if the offence is punishable with death, be punished with imprisonment of either description for a "
                        "term which may extend to seven years, and shall also be liable to fine; (b) if the offence is punishable with "
                        "imprisonment for life or with imprisonment which may extend to ten years, be punished with imprisonment of either "
                        "description for a term which may extend to three years, and shall also be liable to fine; (c) if the offence is "
                        "punishable with imprisonment not extending to ten years, be punished with imprisonment of the description provided "
                        "for the offence for a term which may extend to one-fourth part of the longest term of imprisonment provided for "
                        "the offence, or with fine, or with both."},
    252: {"defect": "Punishment field began with part of the offence description.",
          "punishment": "shall, unless he uses all means in his power to cause the offender to be apprehended and convicted of the offence, "
                        "be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both."},
    341: {"defect": "Punishment field began with part of the offence description (citing section 336 instead of 338) and covered only sub-section (1).",
          "punishment": labelled(P341), "punishment_provisions": P341},
    # Sections with no punishment clause of their own (manually reviewed against the Gazette).
    2: {"defect": "Punishment field held part of the definitions; the section prescribes no punishment.", "punishment": "",
        "punishment_status": "no_punishment_clause"},
    4: {"defect": "Punishment field held the general list of punishments; the section prescribes no punishment for an offence.",
        "punishment": "", "punishment_status": "no_punishment_clause"},
    32: {"defect": "Punishment field held part of a general exception; the section prescribes no punishment.", "punishment": "",
         "punishment_status": "no_punishment_clause"},
    54: {"defect": None, "punishment_status": "no_punishment_clause",
         "note": "Deeming provision ('shall be deemed to have committed such act or offence'); empty punishment field is correct."},
}

# Scraped classification checks against the BNSS First Schedule (Gazette, 25 Dec 2023), reviewed manually.
SCRAPED_CLASSIFICATION_CHECKS = {
    87: ("conflicts_with_gazette_schedule_i", "Gazette: Cognizable, Non-bailable, Court of Session. Scraped block: Non-cognizable."),
    90: ("conflicts_with_gazette_schedule_i", "Gazette: 90(1) and 90(2) Cognizable, Non-bailable, Court of Session. Scraped block: Non-cognizable."),
    276: ("conflicts_with_gazette_schedule_i", "Gazette: Non-cognizable, Non-bailable, Any Magistrate. Scraped block: Bailable."),
    354: ("consistent_manual_positional_reading", "Gazette columns read by row position: Non-cognizable, Bailable, Any Magistrate."),
    355: ("consistent_manual_positional_reading", "Gazette columns read by row position: Non-cognizable, Bailable, Any Magistrate."),
    357: ("consistent_manual_positional_reading", "Gazette columns read by row position: Non-cognizable, Bailable, Any Magistrate."),
}

# Gazette margin headings whose corpus title differs from the Gazette, reviewed manually against the
# extracted Gazette page. Only these exact headings are added to the corpus titles for the margin check.
# (The corpus title of section 119 reads "... to constrain to an illegal to an act"; left unchanged.)
REVIEWED_MARGIN_HEADINGS = [
    "Voluntarily causing hurt or grievous hurt to extort property, or to constrain to an illegal act.",  # section 119
]

NOISE = re.compile(r"^(=====PAGE|THE GAZETTE OF INDIA|_{5,}|Sec\. \d|\[PART II|\d{1,3}$)", re.I)
CLASS_BLOCK = re.compile(r"\n*\s*BNSS Classification.*", re.S)
PUNISHMENT_CLAUSE = re.compile(r"shall be punish|punishable with|be punished with", re.I)


def load_gazette(path):
    lines = [l.rstrip() for l in open(path, encoding="utf-8").read().splitlines() if not NOISE.match(l.strip())]
    out, cur, buf = {}, 0, []
    for line in lines:
        m = re.match(r"^\s*(\d{1,3})\s*\.\s*", line)
        if m and int(m.group(1)) == cur + 1:
            if cur:
                out[cur] = "\n".join(buf)
            cur, buf = int(m.group(1)), [line[m.end():]]
        elif cur:
            buf.append(line)
    out[cur] = "\n".join(buf)
    assert len(out) == 358, f"Expected 358 Gazette sections, parsed {len(out)}"
    return out


def tokens(text):
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    text = re.sub(r"\(\s*\d+\s*\)|\(\s*[a-z]{1,4}\s*\)|•", " ", text.lower())
    return re.findall(r"[a-z]+|\d+", text)


def contains_sequence(haystack, needle):
    n = len(needle)
    return n > 0 and any(haystack[i:i + n] == needle for i in range(len(haystack) - n + 1))


def is_margin_heading_run(run, heading_token_lists):
    """True if the run of Gazette words splits exactly into one or more section titles (margin headings)."""
    reachable = {0}
    for start in range(len(run)):
        if start not in reachable:
            continue
        for heading in heading_token_lists:
            if run[start:start + len(heading)] == heading:
                reachable.add(start + len(heading))
    return len(run) in reachable


def transcription_check(gazette_tokens, replacement, heading_token_lists):
    """
    Checks a transcription against the Gazette section. Returns (ok, omitted_runs, problems).

    Fails when the transcription contains a word that is altered, added or out of order relative to the
    Gazette ('replace'/'delete' opcodes), or when a Gazette word run inside the transcribed span was left
    out and is not entirely made of section titles (margin headings). Accepted margin-heading runs are
    returned in omitted_runs for the corrections log.
    """
    a = tokens(replacement)
    if not a:
        return False, [], ["empty transcription"]
    ops = difflib.SequenceMatcher(None, a, gazette_tokens, autojunk=False).get_opcodes()
    problems, omitted = [], []
    for op, i1, i2, j1, j2 in ops:
        if op in ("replace", "delete"):
            problems.append(f"{op}: transcription {a[i1:i2]} vs Gazette {gazette_tokens[j1:j2]}")
        elif op == "insert" and 0 < i1 < len(a):
            run = gazette_tokens[j1:j2]
            if is_margin_heading_run(run, heading_token_lists):
                omitted.append(" ".join(run))
            else:
                problems.append(f"missing Gazette words not transcribed: {run}")
    return not problems, omitted, problems


def main(dataset_path, gazette_path, log_path):
    records = json.loads(open(dataset_path, encoding="utf-8").read())
    if any("verification" in r for r in records):
        sys.exit("Dataset already migrated; refusing to run again.")
    by_sec = {int(r["section"]): r for r in records}

    vocab = set()
    for r in records:
        vocab.update(tokens(CLASS_BLOCK.sub("", r.get("text") or "")))
    vocab.update(tokens(TEXT_111 + " " + TEXT_120))

    def repair(text):
        def join(m):
            word = (m.group(1) + m.group(2)).lower()
            return m.group(1) + m.group(2) if word in vocab and m.group(2).lower() not in vocab else m.group(0)
        text = re.sub(r"\b([A-Z]) ([a-z]{2,})", join, text)

        # PDF artefact: a trailing "s" split from its word (e.g. "Illustration s"), joined only if the result is a corpus word.
        def join_s(m):
            return m.group(1) + "s" if (m.group(1) + "s").lower() in vocab else m.group(0)
        return re.sub(r"\b([A-Za-z]{3,}) s\b", join_s, text)

    gazette = {s: repair(t) for s, t in load_gazette(gazette_path).items()}
    gaz_tokens = {s: tokens(t) for s, t in gazette.items()}
    # Gazette margin headings are section titles; only these may be skipped inside a transcription.
    heading_tokens = [t for t in (tokens(r.get("title") or "") for r in records) if t]
    heading_tokens += [tokens(h) for h in REVIEWED_MARGIN_HEADINGS]
    log = []

    # 1. Separate scraped classification blocks from statutory text.
    for sec, rec in by_sec.items():
        text = rec.get("text") or ""
        m = CLASS_BLOCK.search(text)
        if m:
            block = m.group(0).strip()
            rec["text"] = text[:m.start()].rstrip()
            status, note = SCRAPED_CLASSIFICATION_CHECKS.get(sec, ("not_checked_against_gazette", ""))
            rec["scraped_procedural_classification"] = {
                "text": block, "status": "unverified_secondary_source", "gazette_check": status,
                "gazette_check_note": note, "source_note": SCRAPED_SOURCE_NOTE,
            }
            log.append({"section": sec, "sub_section": None, "field": "text",
                        "change": "scraped 'BNSS Classification' block moved to scraped_procedural_classification",
                        "previous_value_excerpt": block[:200], "new_value": "(removed from text; preserved separately)",
                        "source": "n/a (separation of non-statutory content)", "method": "automated", "checked_on": CHECKED_ON})
        else:
            rec["scraped_procedural_classification"] = None

    # 2. Apply verified corrections.
    for sec, corr in CORRECTIONS.items():
        rec = by_sec[sec]
        for field in ("text", "punishment"):
            if field not in corr:
                continue
            new = corr[field]
            omitted = []
            if new:
                parts = corr["punishment_provisions"].values() if field == "punishment" and "punishment_provisions" in corr else [new]
                for part in parts:
                    ok, runs, problems = transcription_check(gaz_tokens[sec], part, heading_tokens)
                    if not ok:
                        sys.exit(f"Validation failed for section {sec} {field}: {problems}")
                    omitted.extend(runs)
            old = rec.get(field, "")
            if old == new:
                continue
            rec[field] = new
            log.append({"section": sec,
                        "sub_section": list(corr["punishment_provisions"]) if field == "punishment" and "punishment_provisions" in corr else None,
                        "field": field, "change": corr["defect"], "previous_value": old, "new_value": new,
                        "source": SOURCE_DOCUMENT, "source_passage": f"BNS, 2023, section {sec}",
                        "method": "manual_transcription_automated_check", "method_detail": TRANSCRIPTION_METHOD,
                        "gazette_words_not_transcribed": omitted,
                        "checked_on": CHECKED_ON})
        if "punishment_provisions" in corr:
            rec["punishment_provisions"] = [{"sub_section": k, "text": v} for k, v in corr["punishment_provisions"].items()]

    # 3. Per-record verification evidence.
    for sec, rec in by_sec.items():
        corr = CORRECTIONS.get(sec, {})
        ct, gt = tokens(rec["text"]), gaz_tokens[sec]
        extra, missing = Counter(ct) - Counter(gt), Counter(gt) - Counter(ct)
        coverage = round(1 - sum(missing.values()) / max(1, len(gt)), 3)
        extra_numbers = sorted({t for t in extra if t.isdigit()}, key=int)
        # Ordered comparison: altered, added or reordered words are 'replace'/'delete' opcodes;
        # interior Gazette words left out (other than margin headings) mean the text is incomplete.
        _, _, problems = transcription_check(gt, rec["text"], heading_tokens)
        altered = [p for p in problems if not p.startswith("missing")]
        if "text" in corr:
            text_status, method = "restored_from_gazette", "manual_transcription_automated_check"
        elif altered or extra_numbers:
            text_status, method = "differs_from_gazette_needs_review", "automated_ordered_comparison"
        elif problems or coverage < 0.90:
            text_status, method = "possibly_incomplete", "automated_ordered_comparison"
        else:
            text_status, method = "consistent_with_gazette", "automated_ordered_comparison"

        punishment = rec.get("punishment") or ""
        if corr.get("punishment_status"):
            p_status = corr["punishment_status"]
        elif corr.get("punishment"):
            p_status = "verified_against_gazette"
        elif not punishment:
            p_status = "unknown" if PUNISHMENT_CLAUSE.search(gazette[sec]) else "no_punishment_clause"
        elif contains_sequence(gt, tokens(punishment)):
            p_status = "consistent_with_gazette"
        else:
            p_status = "unverified"
        rec["punishment_status"] = p_status

        rec["verified"] = text_status in ("consistent_with_gazette", "restored_from_gazette")
        rec["verification"] = {
            "text_status": text_status,
            "punishment_status": p_status,
            "method": method,
            "punishment_method": "manual_review" if corr else "automated_pattern_check",
            "source_document": SOURCE_DOCUMENT,
            "checked_on": CHECKED_ON,
            "evidence": {
                "corpus_only_token_count": sum(extra.values()),
                "corpus_only_tokens_sample": sorted(extra.elements())[:15],
                "corpus_only_numbers": extra_numbers,
                "gazette_token_coverage": coverage,
                "ordered_comparison_problems_sample": problems[:3],
                "cross_reference_numbers_differ": bool(extra_numbers),
            },
            "note": corr.get("note", ""),
            "legal_review": "not performed",
        }
        if text_status == "restored_from_gazette":
            rec["source"] = SOURCE_DOCUMENT

    # All validation has passed. Take a verified backup, then replace the dataset atomically.
    backup_path = backup_with_verification(dataset_path, os.path.join(REPO_ROOT, "reports", "backups"))
    print("verified backup:", backup_path)
    tmp_path = dataset_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(records, indent=2, ensure_ascii=False))
    os.replace(tmp_path, dataset_path)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({"checked_on": CHECKED_ON, "source_document": SOURCE_DOCUMENT, "entries": log}, f, indent=2, ensure_ascii=False)

    print("text_status:", dict(Counter(r["verification"]["text_status"] for r in records)))
    print("punishment_status:", dict(Counter(r["punishment_status"] for r in records)))
    print("verified=true:", sum(r["verified"] for r in records), "| scraped blocks moved:",
          sum(1 for r in records if r["scraped_procedural_classification"]), "| log entries:", len(log))


if __name__ == "__main__":
    main(*sys.argv[1:4])
