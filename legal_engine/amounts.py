"""
Indian currency amount extraction and stolen-property value assessment.

Supports amounts written with currency markers (Rs, Rs., INR, ₹, rupees, रुपये),
Indian and international digit grouping (1,00,000 / 100,000), decimals, Devanagari
digits, and scale words (k, thousand, hazar, हजार, lakh, lac, लाख, crore, करोड़).

An amount is only attributed to stolen property when the sentence describing it
also describes a taking, and the amount is not introduced by an unrelated
transaction (price paid, rent, fee, salary, bribe, etc.). Ambiguous totals are
reported as unknown rather than guessed.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional

PROVISO_VALUE_THRESHOLD = 5000

_DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

_SCALES = {
    "k": 1_000,
    "thousand": 1_000,
    "hazar": 1_000,
    "hazaar": 1_000,
    "हजार": 1_000,
    "हज़ार": 1_000,
    "lakh": 100_000,
    "lakhs": 100_000,
    "lac": 100_000,
    "lacs": 100_000,
    "लाख": 100_000,
    "crore": 10_000_000,
    "crores": 10_000_000,
    "करोड़": 10_000_000,
    "करोड": 10_000_000,
}

_NUM = r"(?P<num>\d{1,3}(?:,\d{2,3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
_SCALE = r"(?:\s*(?P<scale>k|thousand|hazaa?r|हज़?ार|lakhs?|lacs?|लाख|crores?|करोड़?)(?![a-z]))?"
_PREFIX_CUR = r"(?:rs\.?|inr|₹|rupees?)"
_SUFFIX_CUR = r"(?:rs\.?|inr|rupees?|rupaye|rupaiye|rupay|रुपये|रुपए|रुपया|cash)"
_VALUE_CUE = r"(?:worth|valued\s+at|value\s+of|costing|kimat|keemat|कीमत)"

_AMOUNT_PATTERNS = [
    re.compile(_PREFIX_CUR + r"\s*" + _NUM + _SCALE, re.I),
    re.compile(_NUM + _SCALE + r"\s*(?:/-\s*)?" + _SUFFIX_CUR + r"(?![a-z])", re.I),
    re.compile(_VALUE_CUE + r"\s+(?:about\s+|around\s+|approx\.?\s+|approximately\s+|nearly\s+)?" + _NUM + _SCALE, re.I),
]

# Words in a sentence indicating that property was taken.
TAKING_RE = re.compile(
    r"(?:\b(?:stole|stolen|steal|stealing|theft|thief|thieves|took|taken|take\s+away|snatch\w*|pick-?pocket\w*|"
    r"picked\s+my\s+pocket|robbed|robbery|looted|loot\s+liya|swiped|pilfered|missing|disappeared|"
    r"chori|chura\w*|uthaa?\s*le|le\s+gaya|le\s+gayi|nikal\s+liya|misappropriat\w*|embezzl\w*|"
    r"disposed\s+of|sold\s+it)\b|चोरी|चुरा|छीन|लूट|ले\s+गया|ले\s+गई|अपहृत|गायब)",
    re.I,
)

# Words shortly before an amount showing it belongs to a different transaction.
_UNRELATED_WORDS = {
    "paid", "pay", "paying", "bought", "buy", "purchased", "purchase", "spent", "spend", "rent",
    "fee", "fees", "fine", "salary", "loan", "bribe", "demanded", "charged", "charge", "owe", "owed",
    "priced", "deposit", "reward", "emi", "for",
}
_VALUE_CUE_WORDS = {"worth", "valued", "value", "costing", "kimat", "keemat", "कीमत", "containing", "contained", "with"}
_CONTEXT_WINDOW_WORDS = 4

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?;।])\s+|\n+")


@dataclass
class CurrencyAmount:
    value: float
    text: str
    start: int
    end: int


@dataclass
class PropertyValueAssessment:
    """Outcome of attributing stated amounts to stolen property."""
    status: str  # "stated" | "ambiguous" | "unstated"
    value: Optional[float] = None
    meets_threshold: Optional[bool] = None
    associated_amounts: List[CurrencyAmount] = field(default_factory=list)
    unassociated_amounts: List[CurrencyAmount] = field(default_factory=list)
    note: str = ""


def _parse_number(num: str, scale: Optional[str]) -> Optional[float]:
    try:
        value = float(num.replace(",", ""))
    except ValueError:
        return None
    if scale:
        value *= _SCALES.get(scale.lower(), _SCALES.get(scale, 1))
    return value


def extract_currency_amounts(text: str) -> List[CurrencyAmount]:
    """Returns all currency amounts in text, ordered by position, without overlaps."""
    if not text:
        return []
    normalized = text.translate(_DEVANAGARI_DIGITS)
    found: List[CurrencyAmount] = []
    for pattern in _AMOUNT_PATTERNS:
        for m in pattern.finditer(normalized):
            if any(m.start() < a.end and a.start < m.end() for a in found):
                continue
            value = _parse_number(m.group("num"), m.group("scale"))
            if value is None:
                continue
            found.append(CurrencyAmount(value=value, text=m.group(0).strip(), start=m.start(), end=m.end()))
    found.sort(key=lambda a: a.start)
    return found


def _introduced_by_unrelated_transaction(preceding: str) -> bool:
    words = re.findall(r"[^\W\d_]+", preceding.lower())[-_CONTEXT_WINDOW_WORDS:]
    for word in reversed(words):
        if word in _VALUE_CUE_WORDS:
            return False
        if word in _UNRELATED_WORDS:
            return True
    return False


def _sentence_spans(text: str):
    start = 0
    for m in _SENTENCE_SPLIT_RE.finditer(text):
        yield start, m.start()
        start = m.end()
    yield start, len(text)


def assess_stolen_property_value(text: str) -> PropertyValueAssessment:
    """
    Attributes stated amounts to stolen property and evaluates the Rs 5,000
    threshold used by the Section 303(2) BNS proviso.

    - Any single attributed amount >= Rs 5,000 establishes the threshold is met.
    - A single attributed amount, or several whose sum is below Rs 5,000, is below the threshold.
    - Several small amounts whose sum reaches Rs 5,000 are reported as ambiguous, because the
      items may overlap (e.g. a wallet and the cash inside it).
    """
    amounts = extract_currency_amounts(text)
    if not amounts:
        return PropertyValueAssessment(status="unstated", note="No monetary amount stated.")

    normalized = text.translate(_DEVANAGARI_DIGITS)
    associated: List[CurrencyAmount] = []
    unassociated: List[CurrencyAmount] = []
    for s_start, s_end in _sentence_spans(normalized):
        sentence = normalized[s_start:s_end]
        has_taking = bool(TAKING_RE.search(sentence))
        for amt in amounts:
            if not (s_start <= amt.start < s_end):
                continue
            preceding = normalized[s_start:amt.start]
            if has_taking and not _introduced_by_unrelated_transaction(preceding):
                associated.append(amt)
            else:
                unassociated.append(amt)

    if not associated:
        return PropertyValueAssessment(
            status="unstated",
            unassociated_amounts=unassociated,
            note="Stated amounts are not attributable to the taken property.",
        )

    largest = max(a.value for a in associated)
    total = sum(a.value for a in associated)
    if largest >= PROVISO_VALUE_THRESHOLD:
        return PropertyValueAssessment(
            status="stated", value=largest, meets_threshold=True,
            associated_amounts=associated, unassociated_amounts=unassociated,
            note="At least one item of taken property is valued at Rs 5,000 or more.",
        )
    if total < PROVISO_VALUE_THRESHOLD:
        return PropertyValueAssessment(
            status="stated", value=total, meets_threshold=False,
            associated_amounts=associated, unassociated_amounts=unassociated,
            note="Stated value of taken property is below Rs 5,000.",
        )
    return PropertyValueAssessment(
        status="ambiguous", value=None, meets_threshold=None,
        associated_amounts=associated, unassociated_amounts=unassociated,
        note="Several amounts are stated whose relationship (separate items or overlapping) is unclear.",
    )


def format_inr(value: float) -> str:
    """Formats a rupee value with Indian digit grouping (e.g. 150000 -> '1,50,000')."""
    whole = int(round(value))
    s = str(whole)
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return ",".join(groups + [tail])
