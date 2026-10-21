"""
Regression tests for the complaint-structuring quality fixes (change record §10).
Each test targets a weakness shown on the development split of benchmark/structuring/structuring_cases.json.
Synthetic statements only. No network, no Gemini.
"""

import json
import os
import re
import subprocess
import sys

from complaint_engine import build_graph, run_structuring
from complaint_engine.models import ComplaintStructureRequest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(statement, *clarifications, **kw):
    return run_structuring(ComplaintStructureRequest(statement=statement, clarifications=list(clarifications), **kw))


def facts(state, kind):
    return [(f.value, f.polarity) for f in state["facts"] if f.kind == kind]


def assert_quotes_exact(state):
    texts = {s.statement_id: s.text for s in [state["original_statement"], *state["clarifications"]]}
    for f in state["facts"]:
        for s in f.spans:
            assert texts[s.statement_id][s.start:s.end] == s.quote


# ── Alleged actions ──

def test_alleged_actions_are_extracted_with_exact_quotes():
    state = run("On 14/10/2026 two men snatched my phone near Andheri Station. One of them pushed me.")
    assert facts(state, "alleged_action") == [("snatched", "asserted"), ("pushed", "asserted")]
    assert_quotes_exact(state)
    assert [a["value"] for a in state["report"]["alleged_actions"]] == ["snatched", "pushed"]


def test_denied_action_is_marked_denied():
    state = run("A man came to my shop and asked for money. He did not hit me.")
    assert ("hit", "explicitly_denied") in facts(state, "alleged_action")


def test_speculative_and_hearsay_allegations_are_uncertain():
    state = run("My neighbour Ramesh must be the one who stole my cycle, because everyone in our building says he steals things.")
    assert facts(state, "alleged_action") == [("stole", "uncertain"), ("steals", "uncertain")]


def test_speculation_about_who_does_not_make_the_date_or_item_uncertain():
    state = run("My neighbour Ramesh must be the one who stole my cycle on 2/10/2026.")
    assert facts(state, "alleged_action") == [("stole", "uncertain")]
    assert facts(state, "datetime") == [("2/10/2026", "asserted")]
    assert facts(state, "property") == [("my cycle", "asserted")]
    assert [p for _, p in facts(state, "event_statement")] == ["uncertain"]


def test_not_knowing_who_did_it_does_not_deny_the_act():
    state = run("My scooter was stolen. I do not know who took it. I did not see him take it. He did not hit me.")
    actions = facts(state, "alleged_action")
    assert ("took", "asserted") in actions and ("hit", "explicitly_denied") in actions
    assert {m.field: m.status for m in state["missing"]}["who"] == "unknown_to_complainant"


def test_complainant_own_actions_and_naming_are_not_alleged_actions():
    state = run("I took a photo of the bike. A man called Ramesh was there.")
    assert facts(state, "alleged_action") == []


def test_hinglish_and_marathi_actions():
    assert ("cheen liya", "asserted") in facts(run("Kal ek ladke ne mera purse cheen liya."), "alleged_action")
    assert ("हिसकावली", "asserted") in facts(run("दोन इसमांनी माझी चेन हिसकावली."), "alleged_action")


# ── Items lost ──

def test_items_lost_are_extracted_in_loss_sentences_only():
    state = run("I called the police from my phone. Later two men took my gold chain and my wallet.")
    assert [v for v, _ in facts(state, "property")] == ["my gold chain", "my wallet"]
    assert [p["value"] for p in state["report"]["items_lost_or_damaged"]] == ["my gold chain", "my wallet"]


def test_damage_counts_as_a_loss_needing_a_value():
    state = run("On 5/10/2026 my landlord broke my door lock at my flat in Kurla.")
    assert ("my door lock", "asserted") in facts(state, "property")
    assert {m.field: m.status for m in state["missing"]}["loss_value"] == "open"


def test_marathi_and_hinglish_items():
    assert any("चेन" in v for v, _ in facts(run("दोन इसमांनी माझी सोन्याची चेन हिसकावली."), "property"))
    assert ("mera purse", "asserted") in facts(run("Kal ek ladke ne mera purse cheen liya."), "property")


# ── People ──

def test_relations_with_names_and_roles():
    state = run("My landlord, Mahesh Jadhav, broke the lock. Then his brother Ganesh Jadhav and the driver left.")
    people = {f.value: f.normalized for f in state["facts"] if f.kind == "person"}
    assert people["My landlord, Mahesh Jadhav"] == "name:Mahesh Jadhav"
    assert people["his brother Ganesh Jadhav"] == "name:Ganesh Jadhav"
    assert "the driver" in people


def test_marathi_relation_is_a_person():
    state = run("माझ्या मित्राने हे पाहिले.")
    assert facts(state, "person") == [("माझ्या मित्राने", "asserted")]


# ── Witnesses, evidence, places, times ──

def test_no_one_was_there_is_a_denied_witness_reference():
    state = run("Last night two men broke into my shop. No one was there at that time.")
    assert ("was there", "explicitly_denied") in facts(state, "witness_reference")
    assert {m.field: m.status for m in state["missing"]}["witnesses"] == "explicitly_denied"


def test_marathi_witness():
    state = run("माझ्या मित्राने हे पाहिले.")
    assert facts(state, "witness_reference") == [("हे पाहिले", "asserted")]


def test_plural_transaction_ids_and_imei_are_evidence():
    state = run("I have screenshots of the chat and the UPI transaction IDs. I also have the box with the IMEI number.")
    values = [v for v, _ in facts(state, "evidence_reference")]
    assert "UPI transaction IDs" in values and "IMEI number" in values


def test_denied_evidence_is_explicitly_denied_not_missing():
    state = run("Two unknown men stole cash from my shop at Kandivali. I do not have any CCTV footage.")
    assert ("CCTV footage", "explicitly_denied") in facts(state, "evidence_reference")
    assert {m.field: m.status for m in state["missing"]}["evidence"] == "explicitly_denied"


def test_places_after_to_and_on_public_transport():
    state = run("A man came to my shop in Malad. Later a woman took my wallet in the crowded train.")
    assert [v for v, _ in facts(state, "location")] == ["my shop", "the crowded train"]
    assert "where" not in {m.field for m in state["missing"]}


def test_time_at_sentence_end_does_not_include_the_full_stop():
    state = run("It happened at 10 pm. He left at 10 p.m. sharp.")
    assert [v for v, _ in facts(state, "datetime")] == ["10 pm", "10 p.m."]


def test_explicit_unknown_is_kept_when_a_partial_detail_is_given():
    state = run("Yesterday a man took my bag on the bus. I don't know the exact place. I don't know who he was.")
    m = {x.field: x.status for x in state["missing"]}
    assert m["where"] == "unknown_to_complainant" and m["who"] == "unknown_to_complainant"
    assert "when" not in m


def test_parts_of_day_are_time_references():
    state = run("On 12 October two men took my bag.", "It happened in the evening.")
    assert ("evening", "asserted") in facts(state, "datetime")


# ── Identity contradictions ──

def test_corrected_name_is_flagged_neutrally_with_both_quotes():
    state = run("On 5/10/2026 my landlord, Mahesh Jadhav, broke my door lock.",
                "The person who broke the lock was his brother Ganesh Jadhav, not Mahesh.")
    ids = [c for c in state["contradictions"] if c.field == "identity"]
    assert len(ids) == 1
    assert [s.quote for s in ids[0].spans] == ["my landlord, Mahesh Jadhav", "his brother Ganesh Jadhav"]
    assert not re.search(r"\b(?:lie|false|dishonest|fake)\w*", ids[0].summary, re.I)
    assert state["review"].route == "human_review_required"


def test_a_new_name_without_a_correction_is_not_a_contradiction():
    state = run("On 5/10/2026 my landlord, Mahesh Jadhav, broke my door lock.",
                "His brother Ganesh Jadhav was also there.")
    assert [c for c in state["contradictions"] if c.field == "identity"] == []


# ── Readable draft ──

DRAFT_SECTIONS = ["COMPLAINANT'S ACCOUNT", "DETAILS FROM THE ACCOUNT", "MISSING INFORMATION",
                  "POSSIBLE INCONSISTENCIES", "SUPPORTING MATERIAL", "JURISDICTION", "VERIFICATION CHECKLIST"]
FORBIDDEN = re.compile(r"FIR\s+(?:No\.?|number|registered)|has been (?:submitted|registered|verified|received)|"
                       r"digitally signed|e-signed|(?:verified|reviewed|approved) by (?:the )?(?:police|officer)", re.I)


def test_draft_text_is_standardised_and_quotes_every_detail():
    statement = ("On 14/10/2026 at about 9:30 pm two men snatched my phone near Andheri Station. "
                 "My friend Priya saw it. I was not injured.")
    state = run(statement, "It was closer to 11 pm.", evidence=[{"evidence_type": "photo"}])
    draft = state["report"]["draft_text"]
    for heading in DRAFT_SECTIONS:
        assert heading in draft
    assert statement in draft and "It was closer to 11 pm." in draft
    for f in state["facts"]:
        if f.kind not in ("event_statement", "denial"):
            assert f"“{f.value}”" in draft, f.value
    for item in state["report"]["verification_checklist_for_officer"]:
        assert item in draft
    assert "NOT AN FIR" in draft and "Not submitted to the police" in draft
    assert "Independently verified information: none" in draft
    assert not FORBIDDEN.search(draft)


def test_draft_marks_denied_and_uncertain_details():
    draft = run("I think it was around 10 pm. A man asked for money. He did not hit me.")["report"]["draft_text"]
    assert "“10 pm” [uncertain]" in draft
    assert "“hit” [denied]" in draft


def test_failed_run_draft_makes_no_claims():
    def boom(state, config):
        raise RuntimeError("simulated failure")
    state = run_structuring(ComplaintStructureRequest(statement="Someone stole my bag at Dadar Market."),
                            graph=build_graph({"detect_missing": boom}))
    draft = state["report"]["draft_text"]
    assert "Someone stole my bag at Dadar Market." in draft
    assert not FORBIDDEN.search(draft)
    assert "Review status: Needs human review" in draft


# ── Evaluation harness: integrity invariants (not accuracy thresholds) ──

def test_evaluation_harness_integrity_invariants(tmp_path):
    out = tmp_path / "eval.json"
    env = {**os.environ, "GEMINI_API_KEY": "", "GOOGLE_API_KEY": "", "BANDHOO_SKIP_DOTENV": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    subprocess.run([sys.executable, "-B", os.path.join(ROOT, "benchmark", "structuring", "evaluate_structuring.py"),
                    "--out", str(out)], check=True, capture_output=True, env=env, cwd=ROOT, timeout=300)
    result = json.loads(out.read_text(encoding="utf-8"))
    assert set(result["summary"]["all"]["integrity"].values()) == {0}
    assert result["jurisdiction"]["unsafe"] == 0
    assert result["summary"]["all"]["draft"]["passed"] == result["summary"]["all"]["draft"]["cases"]
