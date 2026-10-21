"""
Fact extraction with exact source attribution.

Deterministic extractors (regular expressions) run on every statement. Each extracted fact keeps
the exact character span of the complainant's words it came from. An optional LLM extractor can be
injected by trusted server code; its output is accepted only when every quotation is found verbatim
in a statement. Anything else is rejected or, when explicitly labelled as an inference with grounded
basis quotations, kept as an AI inference.
"""

import re
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from complaint_engine.models import FactItem, RejectedItem, SourceSpan, Statement
from legal_engine.amounts import extract_currency_amounts
from legal_engine.service import NEGATION_PATTERNS


class ExtractorUnavailable(Exception):
    """Transient failure of an optional extractor (retried)."""


class InvalidExtractorOutput(Exception):
    """Extractor returned output that does not match the expected structure (not retried)."""


MONTHS = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
MONTH_NUM = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

DATE_PATTERNS = [
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+{MONTHS}(?:,?\s+\d{{4}})?\b",
    rf"\b{MONTHS}\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?\b",
    r"\b(?:yesterday|today|tonight|last night|this morning|this afternoon|this evening|last week|last month)\b",
    r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
]
TIME_PATTERNS = [
    r"\b\d{1,2}(?::\d{2})?\s*(?:[ap]\.m\.|[ap]\.?m)(?![a-z])",  # "10 pm." ends at "pm"; "10 p.m." keeps its dot
    r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b",
    r"\b(?:noon|midnight)\b",
    r"\b(?:morning|afternoon|evening|night)\b",  # part of day; skipped when inside "last night" etc.
]
RELATIONS = (r"neighbou?r|friend|brother|sister|wife|husband|son|daughter|father|mother|employer|boss|landlord|tenant|"
             r"colleague|cousin|uncle|aunt|driver|maid|manager|partner|business\s+partner|co-?worker|relative")
PERSON_PATTERNS = [
    # A relation, optionally followed by a name: "my landlord, Mahesh Jadhav", "his brother Ganesh Jadhav".
    rf"\b(?i:my|his|her|their|our)\s+(?i:{RELATIONS})\b(?:,?[ \t]+(?P<name>[A-Z][a-z]+(?:[ \t]+[A-Z][a-z]+){{0,2}}))?",
    r"\b(?i:a|an|one|two|three|four|five|six|some|several)\s+(?i:unknown\s+)?(?i:man|men|woman|women|boy|boys|girl|girls|person|persons|people|youth|youths|stranger|strangers|individual|individuals)\b",
    r"\b(?i:the)\s+(?i:driver|shopkeeper|shop\s+owner|conductor|security\s+guard|watchman|guard|vendor|accused|thief|thieves|robber|robbers|attacker|attackers|caller|agent)\b",
]
NAMED_PERSON = r"\b(?:named|called|name is|name was)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})"
COUNT_WORDS = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
PLACE_WORDS = r"(?:Road|Rd|Station|Market|Nagar|Street|Lane|Chowk|Mall|Park|Bridge|Bus|Stop|Depot|Gate|Colony|West|East|Junction|Hospital|Signal)"
LOCATION_PATTERNS = [
    rf"\b(?:at|near|outside|inside|opposite|behind|in front of)\s+(?:the\s+)?([A-Z][\w'-]*(?:[ \t]+(?:[A-Z][\w'-]*|{PLACE_WORDS})){{0,5}})",
    r"\b(?:at|near|outside|inside|in front of|to|from|into)\s+((?:my|our|the)\s+(?:home|house|office|shop|building|society|flat|room|school|college|bus stop|market|gate))\b",
    r"\b(?:in|on|inside|aboard)\s+((?:the|a)\s+(?:[a-z]+\s+)?(?:local\s+)?(?:train|bus|taxi|auto|auto-rickshaw|rickshaw|metro|cab))\b",
]
PHONE = r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
VEHICLE = r"\b[A-Z]{2}[\s-]?\d{1,2}[\s-]?[A-Z]{1,3}[\s-]?\d{4}\b"
INJURY = r"\b(?:injur(?:y|ies|ed)|hurt|bleed(?:ing)?|fractur(?:e|ed)|wound(?:ed|s)?|bruis(?:e|es|ed)|stitches)\b"
WEAPON = r"\b(?:knife|knives|gun|pistol|revolver|rod|stick|blade|sword|weapon|weapons|acid)\b"
WITNESS = r"\b(?:witness(?:es|ed)?|saw (?:the|it|this|him|her|them|everything)|was present|were present|was there|were there)\b"
EVIDENCE = (
    r"\b(?:photos?|photographs?|videos?|screenshots?|receipts?|bills?|invoices?|CCTV(?: footage)?|recordings?|"
    r"messages?|chats?|bank statements?|(?:UPI\s+)?transaction\s+(?:ids?|references?|numbers?)|UPI\s+(?:ids?|references?)|"
    r"IMEI(?:\s+number)?|medical (?:report|certificate))\b"
)
EXTRA_DENIALS = [
    r"\bno\s*(?:one|body)\s+(?:saw|was\s+(?:there|present)|witnessed)\b",
    r"\bno\s+witness(?:es)?\b",
    r"\bnothing\s+(?:was\s+)?(?:taken|stolen)\b",
]
DENIAL_RES = [re.compile(p, re.I) for p in NEGATION_PATTERNS + EXTRA_DENIALS]

# A few common Hinglish (romanised Hindi) and Marathi expressions. Deliberately narrow: each pattern needs a
# clear marker (a number word before a person noun, a postposition after a place noun, "baje"/"वाजता" after an
# hour). Times given this way have no am/pm, so they are not normalised and never compared.
DEV = "\u0900-\u097F"
MR_MONTHS = {"जानेवारी": 1, "फेब्रुवारी": 2, "मार्च": 3, "एप्रिल": 4, "मे": 5, "जून": 6, "जुलै": 7, "ऑगस्ट": 8,
             "सप्टेंबर": 9, "ऑक्टोबर": 10, "नोव्हेंबर": 11, "डिसेंबर": 12}
MR_DATE = rf"(?<![\d{DEV}])(\d{{1,2}})\s+({'|'.join(MR_MONTHS)})(?![{DEV}])(?:,?\s+(\d{{4}})(?!\d))?"
INDIC_DATE_PATTERNS = [
    MR_DATE,
    r"\b(?:kal|aaj|parso|parson)(?:\s+(?:raat|shaam|subah|dopahar))?\b",
    rf"(?<![{DEV}])(?:काल|आज|परवा)(?:\s+(?:रात्री|सकाळी|संध्याकाळी|दुपारी))?(?![{DEV}])",
]
INDIC_TIME_PATTERNS = [
    r"\b\d{1,2}(?::\d{2})?\s*baje\b",
    rf"(?<![\d{DEV}])\d{{1,2}}\s*वाजता(?![{DEV}])",
]
INDIC_COUNT = {"ek": 1, "do": 2, "teen": 3, "char": 4, "chaar": 4, "paanch": 5,
               "एक": 1, "दोन": 2, "तीन": 3, "चार": 4, "पाच": 5}
INDIC_RELATION_PATTERNS = [
    r"\b(?:mera|mere|meri)\s+(?:bhai|dost|behen|behan|pati|patni|beta|beti|papa|maa|padosi|saathi)\b",
    rf"(?<![{DEV}])(?:माझ्या|माझा|माझी|माझे)\s+(?:मित्राने|मित्रांनी|मित्र|मैत्रिणीने|मैत्रीण|भावाने|भाऊ|बहिणीने|बहीण|पत्नीने|"
    rf"पत्नी|पतीने|पती|वडिलांनी|वडील|आईने|आई|मुलाने|मुलगा|मुलीने|मुलगी|शेजाऱ्याने|शेजारी|सहकाऱ्याने|सहकारी)(?![{DEV}])",
]
INDIC_WITNESS_PATTERNS = [
    r"\b(?:(?:sab|ye|yeh|woh|wo)\s+)?dekha\b",
    rf"(?<![{DEV}])(?:(?:हे|ते|सगळे|सर्व)\s+)?(?:पाहिले|पाहिलं|बघितले|बघितलं)(?![{DEV}])",
]
INDIC_PERSON_PATTERNS = [
    r"\b(?:ek|do|teen|char|chaar|paanch)\s+(?:aadmi|aadmiyon|admi|ladke|ladkon|ladko|log|logon|aurat|aurton|auraton|"
    r"mahila|mahilaon|chor)\b",
    rf"(?<![{DEV}])(?:एक|दोन|तीन|चार|पाच)\s+(?:माणूस|माणसे|माणसं|माणसांनी|माणसाने|मुलगा|मुले|मुलं|मुलांनी|मुलाने|इसम|इसमांनी|"
    rf"इसमाने|व्यक्ती|व्यक्तींनी|व्यक्तीने|महिला|महिलांनी|महिलेने|बायका|चोर|चोरांनी|चोराने)(?![{DEV}])",
]
HINGLISH_ACTION = (r"(?:cheen\s+(?:liya|li|le|kar)|chura\s+(?:liya|li|le)|chori\s+(?:kar\s+)?(?:li|liya|ki)|maar(?:a|i|pit\s+ki)|"
                   r"dhakka\s+(?:diya|de\s+diya|maara)|dhamki\s+(?:di|diya|dee)|le\s+(?:gaya|gaye|gayi))")
# Alleged actions: what others are said to have done. Not after "I"/"we" (the complainant's own acts);
# "called" not when it introduces a name ("a man called Ramesh"); "asked" only for money.
ACTION_PATTERNS = [
    r"(?<!\bI )(?<!\bwe )(?<!\bWe )\b(?:snatch(?:ed|es|ing)?|st(?:ole|olen|eals?|ealing)|took|taken|robbed|grabbed|pickpocketed|"
    r"hit|beat(?:en)?|push(?:ed)?|slapped|punched|kicked|attacked|assaulted|stabbed|threaten(?:ed|ing)?|abused|"
    r"harass(?:ed|ing)|molested|cheated|defrauded|scammed|promis(?:ed|ing)|pretend(?:ed|ing)|offer(?:ed|ing)|demanded|"
    r"extorted|damaged|smashed|broke(?:n)?(?:\s+into)?|drove\s+away|ran\s+away|fled)\b",
    r"(?<!\bI )(?<!\bwe )(?<!\bWe )\bcalled\b(?!\s+[A-Z])",
    r"\basked\b(?=\s+(?:me\s+)?for\s+(?:money|cash|payment|a\s+bribe))",
    rf"\b{HINGLISH_ACTION}\b",
    rf"(?<![{DEV}])(?:हिसकाव(?:ली|ला|ले)|चोर(?:ले|ली|ला)|चोरून\s+नेल(?:ा|ी|े)|मार(?:ले|ली|हाण\s+केली)|धक्का\s+दिला|"
    rf"धमकी\s+दिली|फसव(?:ले|ली|णूक\s+केली))(?![{DEV}])",
]
# Items lost or damaged. Extracted only next to a loss or damage verb: after an active verb ("took my bag and
# my wallet"), before a passive one ("my scooter was stolen"), or before a Hinglish/Marathi verb (verb-final order).
_ITEM_NOUNS = (r"phone|mobile|smartphone|bag|handbag|purse|wallet|chain|necklace|ring|earrings?|bangles?|jewell?ery|"
               r"watch|laptop|tablet|cash|money|scooter|bike|motorcycle|bicycle|cycle|car|documents?|passport|"
               r"(?:ID|Aadhaar|PAN|ATM|debit|credit)\s+card|lock|SIM(?:\s+card)?")
PROPERTY_PATTERNS = [
    rf"\b(?:my|our|his|her|the)\s+(?:[a-z]+\s+)?(?:{_ITEM_NOUNS})\b",
    r"\b(?:cash|money|jewell?ery|valuables)\b",
    r"\b(?:mera|meri|mere)\s+(?:[a-z]+\s+)?(?:phone|mobile|purse|bag|wallet|chain|ghadi|paise|laptop|cycle|bike|gaadi)\b",
    rf"(?<![{DEV}])(?:माझी|माझा|माझे)\s+(?:सोन्याची\s+)?(?:चेन|पाकीट|फोन|मोबाईल|पर्स|बॅग|अंगठी|घड्याळ|गाडी|सायकल|पैसे)(?![{DEV}])",
]
LOSS_ACTIVE = re.compile(r"\b(?:snatched|stole|took|grabbed|robbed|paid|transferred|lost|damaged|broke|smashed|destroyed|"
                         r"pickpocketed)\W+(?:\w+\W+){0,6}$", re.I)
LOSS_PASSIVE = re.compile(r"\W*(?:\w+\W+){0,5}?(?:was|were|got|has\s+been|have\s+been)\s+(?:\w+\s+)?"
                          r"(?:stolen|taken|snatched|lost|damaged|broken|grabbed|robbed|destroyed)\b", re.I)
LOSS_VERB_FINAL = re.compile(rf"\W*(?:\S+\s+){{0,2}}?(?:{HINGLISH_ACTION}|हिसकाव|चोर|नेल)", re.I)

HINGLISH_PLACE_WORDS = r"(?:station|market|road|naka|chowk|bazaar|bazar|nagar|stop|signal|bridge|pul|mandir|masjid|hospital|school|college|gate|colony)"
INDIC_LOCATION_PATTERNS = [
    # "Dadar station ke paas" -> "Dadar station" (must start with a capitalised name)
    rf"\b([A-Z][\w'-]*(?:[ \t]+(?:[A-Z][\w'-]*|{HINGLISH_PLACE_WORDS})){{0,4}})[ \t]+(?:ke|ki)[ \t]+"
    r"(?:paas|pass|saamne|samne|bahar|baahar|andar|peeche|piche)\b",
    # "दादर स्टेशनजवळ" -> "दादर स्टेशन" (a name followed by a place noun, then a postposition or a break)
    rf"(?<![{DEV}])((?!(?:मी|माझ्या|माझा|माझी|आम्ही|आमच्या|तो|ती|ते|एका|त्या|या)[ \t])[{DEV}]+[ \t]+"
    rf"(?:स्टेशन|मार्केट|रोड|बाजार|चौक|नाका|पूल|सिग्नल|हॉस्पिटल|गेट|नगर|मंदिर|शाळा|कॉलेज))"
    rf"(?=जवळ|समोर|बाहेर|मध्ये|वर|च्या|ला|[ \t.,।]|$)",
]
NEG_CUE = re.compile(r"\b(?:no|not|never|nobody|nothing|didn't|did not|wasn't|weren't|without)\b(?:\W+\w+){0,3}\W*$", re.I)
# "I do not know who took it" / "I did not see him take it" say nothing against the act itself.
EPISTEMIC_NEG = re.compile(r"\b(?:do|did|does|am|was|could|can)(?:\s+not|n't)\s+(?:know|remember|recall|see|notice|sure)\b"
                           r"(?:\W+\w+){0,3}\W*$", re.I)
# "around/about ..." hedges only the item right after it; "I think/maybe ..." hedges the rest of the sentence.
HEDGE_CUE = re.compile(r"\b(?:around|about|approximately|approx\.?|roughly|nearly)\W*$", re.I)
SENTENCE_HEDGE_CUE = re.compile(r"\b(?:maybe|probably|perhaps|i think|i believe|not sure)\b", re.I)
# Speculation ("must be the one who stole") and hearsay ("everyone says he steals") qualify who did what, so they
# make alleged actions uncertain, not the date or the item lost in the same sentence.
ATTRIBUTION_CUE = re.compile(
    r"\b(?:must\s+(?:be|have)|i\s+suspect|seems?\s+(?:like|that)|"
    r"(?:everyone|everybody|people|they|neighbou?rs)\b[^.!?]{0,40}?\bsays?|i\s+(?:have\s+)?heard|someone\s+told\s+me|"
    r"according\s+to|rumou?r)\b", re.I)


def sentence_spans(text: str) -> List[Tuple[int, int]]:
    spans = []
    for m in re.finditer(r"[^.!?।\n]+[.!?।]?", text):
        s, e = m.start(), m.end()
        while s < e and text[s].isspace():
            s += 1
        while e > s and text[e - 1].isspace():
            e -= 1
        if e - s >= 3:
            spans.append((s, e))
    return spans


def _sentence_of(spans: List[Tuple[int, int]], pos: int) -> Tuple[int, int]:
    for s, e in spans:
        if s <= pos < e:
            return s, e
    return 0, 0


def _polarity(text: str, start: int, end: int, sentences: List[Tuple[int, int]], kind: str = "") -> str:
    s, _ = _sentence_of(sentences, start)
    before = text[s:start]
    if NEG_CUE.search(before) and not EPISTEMIC_NEG.search(before):
        return "explicitly_denied"
    for r in DENIAL_RES:  # item lies inside a denial phrase, e.g. "no weapon was used"
        m = r.search(text, s, end + 40)
        if m and m.start() <= start and m.end() >= end:
            return "explicitly_denied"
    if HEDGE_CUE.search(before) or SENTENCE_HEDGE_CUE.search(before):
        return "uncertain"
    if kind == "alleged_action" and ATTRIBUTION_CUE.search(before):
        return "uncertain"
    return "asserted"


def _normalize_date(raw: str) -> Optional[str]:
    m = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", raw)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = y + 2000 if y < 100 else y
        return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= d <= 31 and 1 <= mo <= 12 else None
    m = re.fullmatch(rf"(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTHS})(?:,?\s+(\d{{4}}))?", raw, re.I)
    if m:
        y = m.group(3) or "????"
        return f"{y}-{MONTH_NUM[m.group(2)[:3].lower()]:02d}-{int(m.group(1)):02d}"
    m = re.fullmatch(rf"({MONTHS})\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,?\s+(\d{{4}}))?", raw, re.I)
    if m:
        y = m.group(3) or "????"
        return f"{y}-{MONTH_NUM[m.group(1)[:3].lower()]:02d}-{int(m.group(2)):02d}"
    m = re.fullmatch(MR_DATE, raw)
    if m:  # Marathi month name; Devanagari digits are read by int()
        y = f"{int(m.group(3)):04d}" if m.group(3) else "????"
        return f"{y}-{MR_MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}"
    return None  # relative expressions ("yesterday", "kal") are not normalised


def _normalize_time(raw: str) -> Optional[str]:
    r = raw.lower().replace(".", "").replace(" ", "")
    if r == "noon":
        return "12:00"
    if r == "midnight":
        return "00:00"
    m = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?(am|pm)?", r)
    if not m:
        return None
    h, mi, ap = int(m.group(1)), int(m.group(2) or 0), m.group(3)
    if ap == "pm" and h < 12:
        h += 12
    if ap == "am" and h == 12:
        h = 0
    return f"{h:02d}:{mi:02d}" if h < 24 and mi < 60 else None


class _Builder:
    def __init__(self, statement: Statement):
        self.st = statement
        self.text = statement.text
        self.sentences = sentence_spans(self.text)
        self.items: List[FactItem] = []
        self.taken: set = set()

    def add(self, kind, start, end, method, normalized=None, polarity=None, note=""):
        key = (kind, start, end)
        if key in self.taken or end <= start:
            return
        # Skip a match that lies inside one already extracted for the same kind ("10:30" inside "10:30 pm").
        if any(k == kind and s <= start and end <= e for k, s, e in self.taken):
            return
        self.taken.add(key)
        quote = self.text[start:end]
        self.items.append(FactItem(
            item_id=f"{self.st.statement_id}-F{len(self.items) + 1}",
            kind=kind,
            value=quote,
            spans=[SourceSpan(statement_id=self.st.statement_id, start=start, end=end, quote=quote)],
            polarity=polarity or _polarity(self.text, start, end, self.sentences, kind),
            extraction_method=method,
            normalized=normalized,
            note=note,
        ))

    def regex(self, kind, patterns: Iterable[str], method: str, group: int = 0,
              normalizer: Optional[Callable] = None, flags: int = re.I):
        for p in patterns:
            for m in re.finditer(p, self.text, flags):
                s, e = m.span(group)
                self.add(kind, s, e, method, normalized=normalizer(self.text[s:e]) if normalizer else None)


def extract_deterministic(statement: Statement) -> List[FactItem]:
    b = _Builder(statement)
    for s, e in b.sentences:
        sent = b.text[s:e]
        denied = any(r.search(sent) for r in DENIAL_RES)
        hedged = bool(SENTENCE_HEDGE_CUE.search(sent) or ATTRIBUTION_CUE.search(sent))
        b.add("event_statement", s, e, "rule:sentence",
              polarity="explicitly_denied" if denied else ("uncertain" if hedged else "asserted"))
    b.regex("datetime", DATE_PATTERNS, "rule:date", normalizer=_normalize_date)
    b.regex("datetime", TIME_PATTERNS, "rule:time", normalizer=lambda r: "T" + (_normalize_time(r) or "?"))
    b.regex("datetime", INDIC_DATE_PATTERNS, "rule:date_hi_mr", normalizer=_normalize_date)
    b.regex("datetime", INDIC_TIME_PATTERNS, "rule:time_hi_mr", normalizer=lambda r: "T?")
    for p in PERSON_PATTERNS:
        for m in re.finditer(p, b.text):
            first = m.group(0).split()[0].lower()
            name = m.groupdict().get("name")
            b.add("person", m.start(), m.end(), "rule:person",
                  normalized=f"name:{name}" if name else
                  f"count:{COUNT_WORDS[first]}" if first in COUNT_WORDS and first not in ("a", "an") else None)
    b.regex("person", INDIC_RELATION_PATTERNS, "rule:person_hi_mr")
    for p in INDIC_PERSON_PATTERNS:
        for m in re.finditer(p, b.text, re.I):
            b.add("person", m.start(), m.end(), "rule:person_hi_mr", normalized=f"count:{INDIC_COUNT[m.group(0).split()[0].lower()]}")
    b.regex("person", [NAMED_PERSON], "rule:named_person", group=1, flags=0, normalizer=lambda r: f"name:{r}")
    b.regex("location", [LOCATION_PATTERNS[0]], "rule:location", group=1, flags=0)
    b.regex("location", LOCATION_PATTERNS[1:], "rule:location", group=1)
    b.regex("location", [INDIC_LOCATION_PATTERNS[0]], "rule:location_hi", group=1, flags=0)
    b.regex("location", [INDIC_LOCATION_PATTERNS[1]], "rule:location_mr", group=1)
    for a in extract_currency_amounts(b.text):
        b.add("amount", a.start, a.end, "rule:amount", normalized=f"{a.value:.2f}")
    b.regex("phone", [PHONE], "rule:phone", normalizer=lambda r: re.sub(r"\D", "", r)[-10:])
    b.regex("vehicle", [VEHICLE], "rule:vehicle", normalizer=lambda r: re.sub(r"[\s-]", "", r).upper(), flags=0)
    b.regex("injury", [INJURY], "rule:injury")
    b.regex("weapon", [WEAPON], "rule:weapon")
    b.regex("witness_reference", [WITNESS], "rule:witness")
    b.regex("witness_reference", INDIC_WITNESS_PATTERNS, "rule:witness_hi_mr")
    b.regex("alleged_action", ACTION_PATTERNS[:3], "rule:action", flags=0)
    b.regex("alleged_action", ACTION_PATTERNS[3:], "rule:action_hi_mr")
    for p in PROPERTY_PATTERNS:
        for m in re.finditer(p, b.text, re.I):
            s, _ = _sentence_of(b.sentences, m.start())
            if LOSS_ACTIVE.search(b.text[s:m.start()]) or LOSS_PASSIVE.match(b.text, m.end()) \
                    or LOSS_VERB_FINAL.match(b.text, m.end()):
                b.add("property", m.start(), m.end(), "rule:property")
    b.regex("evidence_reference", [EVIDENCE], "rule:evidence")
    for r in DENIAL_RES:
        for m in r.finditer(b.text):
            b.add("denial", m.start(), m.end(), "rule:denial", polarity="explicitly_denied")
    return b.items


def _find_quote(quote: str, statements: List[Statement], statement_id: Optional[str]) -> Optional[SourceSpan]:
    if not isinstance(quote, str) or not quote.strip():
        return None
    for st in statements:
        if statement_id and st.statement_id != statement_id:
            continue
        i = st.text.find(quote)
        if i >= 0:
            return SourceSpan(statement_id=st.statement_id, start=i, end=i + len(quote), quote=quote)
    return None


ALLOWED_KINDS = {"event_statement", "datetime", "location", "person", "amount", "phone", "vehicle", "alleged_action", "property",
                 "injury", "weapon", "witness_reference", "evidence_reference", "denial", "other"}


def validate_llm_items(raw, statements: List[Statement], model_name: str = "llm") -> Tuple[List[FactItem], List[RejectedItem]]:
    """Ground LLM-proposed items in the statements. Returns (accepted items, rejected items)."""
    if not isinstance(raw, list):
        raise InvalidExtractorOutput(f"expected a list of items, got {type(raw).__name__}")
    accepted: List[FactItem] = []
    rejected: List[RejectedItem] = []
    for n, item in enumerate(raw, 1):
        if not isinstance(item, dict):
            rejected.append(RejectedItem(proposed=str(item)[:200], reason="item is not an object", source=model_name))
            continue
        label = str(item.get("value") or item.get("quote") or "")[:300]
        if item.get("inference"):
            basis = item.get("basis_quotes") or []
            spans = [_find_quote(q, statements, item.get("statement_id")) for q in basis] if isinstance(basis, list) else []
            if not spans or any(s is None for s in spans):
                rejected.append(RejectedItem(proposed=label, reason="inference without verbatim basis quotations", source=model_name))
                continue
            accepted.append(FactItem(
                item_id=f"AI-{n}", kind="other", value=label, spans=spans, provenance="ai_inference",
                extraction_method=f"llm:{model_name}", note="AI-generated inference; requires verification.",
            ))
            continue
        span = _find_quote(item.get("quote"), statements, item.get("statement_id"))
        if span is None:
            rejected.append(RejectedItem(proposed=label, reason="quotation not found verbatim in any statement", source=model_name))
            continue
        kind = item.get("kind") if item.get("kind") in ALLOWED_KINDS else "other"
        st = next(s for s in statements if s.statement_id == span.statement_id)
        accepted.append(FactItem(
            item_id=f"LLM-{n}", kind=kind, value=span.quote, spans=[span],
            polarity=_polarity(st.text, span.start, span.end, sentence_spans(st.text), kind),
            extraction_method=f"llm:{model_name}",
            note=f"model label: {str(item.get('value'))[:120]}" if item.get("value") and item.get("value") != span.quote else "",
        ))
    return accepted, rejected


def span_is_valid(span: SourceSpan, statements_by_id: Dict[str, Statement]) -> bool:
    st = statements_by_id.get(span.statement_id)
    return bool(st) and 0 <= span.start < span.end <= len(st.text) and st.text[span.start:span.end] == span.quote
