"""
Core Legal Analysis Service.
Coordinates synonym mapping, BM25 retrieval, Gemini LLM reasoning,
local corpus verification, and deterministic fallback handling.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

from legal_engine.corpus import BNSCorpus
from legal_engine.retrieval import BM25LegalRetriever
from legal_engine.llm_client import GeminiLegalClient, LLMUnavailableError, LLMInferenceError
from legal_engine.schemas import (
    NarrativeInput,
    OffenceClassificationResponse,
    SectionPredictionItem,
    FactExtractionBlock
)

from legal_engine.synonyms import DEFAULT_SYNONYM_MAP
from legal_engine.amounts import TAKING_RE, assess_stolen_property_value, format_inr
from legal_engine.schedule_registry import (
    BNSS_173_3_CAVEAT_TEXT,
    BNSS_173_3_PROCEDURE_TEXT,
    OPEN_LEGAL_QUESTIONS,
    check_bnss_173_3_eligibility,
    resolve_schedule_classification
)

logger = logging.getLogger("legal_engine.service")

# Hindi and Hinglish negations of violence, weapons, injury or threats.
# Devanagari patterns avoid \b because vowel signs are not word characters in Python's re.
MULTILINGUAL_VIOLENCE_NEGATION_PATTERNS = [
    r'(?:कोई|किसी)\s+(?:भी\s+|को\s+)?(?:\S+\s+)??(?:हथियार|हिंसा|चोट|धमकी|मारपीट|ज़बरदस्ती|जबरदस्ती|बल)(?:\s+\S+){0,5}?\s+नहीं',
    r'बिना\s+(?:किसी\s+)?(?:\S+\s+)??(?:हथियार|हिंसा|चोट|धमकी|मारपीट|ज़बरदस्ती|जबरदस्ती|बल|विवशता)',
    r'\b(?:koi|kisi|kisi\s+ko|na)\s+(?:bhi\s+)?(?:\w+\s+)??(?:hathiyaa?r|weapon|maar\s*peet|maarpeet|marpeet|hinsa|chot|dhamki|zabardasti|force|violence)\b(?:\s+\w+){0,4}?\s+(?:nahi|nahin|nhi|nai)\b',
    r'\bbina\s+(?:kisi\s+)?(?:\w+\s+)??(?:hathiyaa?r|weapon|maar\s*peet|maarpeet|marpeet|hinsa|chot|dhamki|zabardasti|force|violence)\b',
]

# Regex patterns for common negative assertions in complaints
NEGATION_PATTERNS = [
    r'\bno\s+(?:theft|violence|injury|hurt|weapon|weapons|loss|damage|force|harm)\b',
    r'\bnobody\s+(?:was\s+)?(?:hurt|injured|killed|attacked|threatened)\b',
    r'\bnot\s+(?:injured|hurt|stolen|harmed|attacked|threatened|armed)\b',
    r'\bwithout\s+(?:any\s+)?(?:violence|weapon|weapons|harm|injury|force)\b',
    r'\bdid\s+not\s+(?:steal|hit|beat|attack|threaten|hurt)\b',
    r'\bno\s+one\s+(?:was\s+)?(?:hurt|injured|threatened|restrained|attacked)(?:\s+or\s+(?:hurt|injured|threatened|restrained|attacked))*\b',
    r'\bno\s+weapons?\s+(?:were\s+)?(?:used|involved|present)\b',
    r'\bno\s+(?:force|threat|threats|fear)(?:\s+(?:was|were)\s+used)?\b',
] + MULTILINGUAL_VIOLENCE_NEGATION_PATTERNS

# Figurative uses of "hurt" that do not describe bodily hurt.
FIGURATIVE_HURT_PATTERNS = [
    r'\b(?:feelings?|sentiments?|ego|pride|heart|reputation|image)\s+(?:(?:was|were|got|has\s+been|have\s+been)\s+)?(?:badly\s+|deeply\s+|really\s+|very\s+)?hurt\b',
    r'\bhurt\s+(?:my|his|her|our|their)\s+(?:feelings?|sentiments?|ego|pride|heart|reputation)\b',
]

# Statutory alternatives under BNS Section 309: hurt, wrongful restraint, or fear of instant
# death, hurt or wrongful restraint. Patterns require bodily or violent context.
ROBBERY_RESTRAINT_RE = re.compile(
    r'\b(?:restrain|restrained|restraint|pinned|pinning|held\s+(?:me\s+)?down|holding\s+(?:me\s+)?down|cornered|trapped|'
    r'blocked\s+(?:my\s+)?(?:way|path)|grabbed\s+(?:me|my\s+(?:arm|collar|hand|neck))|tied\s+(?:me\s+)?up|'
    r'prevented\s+(?:me|him|her)\s+from\s+(?:moving|leaving)|locked\s+(?:me\s+)?up|surrounded\s+me)\b',
    re.I
)
ROBBERY_THREAT_RE = re.compile(
    r'(?:\b(?:threaten(?:ed|ing|s)?|warned)\s+(?:me\s+|him\s+|her\s+|us\s+|them\s+)?(?:that\s+(?:he|she|they)\s+would\s+|to\s+)?'
    r'(?:kill|murder|shoot|stab|slit|slash|cut|hurt|harm|injure|beat|hit|break|attack|burn|throw\s+acid)\b|'
    r'\bthreats?\s+(?:to|of)\s+(?:kill|murder|death|shoot|stab|hurt|harm|injur\w*|beat|violence)\b|'
    r'\b(?:at\s+(?:gun|knife)\s*-?\s*point|gunpoint|knifepoint)\b|'
    r'\b(?:pointed|aimed|held|pressed|put|placed|brandished|waved|showed|displayed|drew|pulled\s+out|took\s+out)\s+'
    r'(?:a\s+|an\s+|his\s+|the\s+|their\s+)?(?:\w+\s+){0,2}?(?:knife|gun|pistol|revolver|blade|dagger|sword|firearm|weapon|chaa?ku|talwar|iron\s+rod)\b|'
    r'\bor\s+(?:else\s+)?(?:i|we|he|they)\s*(?:\'ll|\s+will|\s+would)\s+(?:kill|shoot|stab|hurt|beat|hit|harm)\b|'
    r'\b(?:jaan\s+se\s+maar\w*|maar\s+(?:dal|daal)\w*|goli\s+maar\w*|chaa?ku\s+(?:dikha|laga|rakh)\w*|talwar\s+dikha\w*|maar\w*\s+(?:ki|ka)\s+dhamki)|'
    r'(?:जान\s+से\s+मार|मार\s+डाल|गोली\s+मार|चाकू\s+(?:दिखा|लगा|रख)|तलवार\s+दिखा|पिस्तौल\s+(?:दिखा|तान)|बंदूक\s+(?:दिखा|तान)|मारने\s+की\s+धमकी))',
    re.I
)
ROBBERY_HURT_RE = re.compile(
    r'(?:\b(?:hit|punched|slapped|kicked|struck|beat|stabbed|slashed|choked|strangled|pushed|shoved|knocked|attacked|assaulted)\s+'
    r'(?:me|him|her|us|them|my|his|our|their|the\s+\w+)\b|'
    r'\b(?:beaten|bleeding|wounded|injured|injury|injuries|fractured?|bruised|bruises)\b|'
    r'\b(?:hurt|harmed)\s+(?:me|him|her|us|them|my\s+(?:arm|hand|leg|head|face|neck|back|shoulder|eye|body))\b|'
    r'\b(?:was|were|got|been)\s+(?:badly\s+|seriously\s+)?hurt\b|'
    r'\b(?:maar\s*(?:kar|ke|diya|di|peet\w*)|maara|pitai|pitaai|peeta|peet\s+diya|ghayal|zakhmi|'
    r'chot\s+(?:lagi|aayi|pahunch\w*)|danda\s+maar\w*|thappad\s+maar\w*|chaa?ku\s+maar\w*|ghoo?nsa\s+maar\w*)\b|'
    r'(?:मार\s*(?:कर|के|दिया|पीट)|मारा|पीटा|पिटाई|घायल|ज़ख्मी|जख्मी|चोट\s+(?:लगी|आई|पहुंचा)|डंडा\s+मार|थप्पड़\s+मार|चाकू\s+मार))',
    re.I
)
ROBBERY_ARMED_RE = re.compile(
    r'(?:\barmed\b|\bwith\s+(?:a|an)\s+(?:\w+\s+)?(?:knife|gun|pistol|revolver|blade|dagger|sword|firearm|weapon|iron\s+rod|chaa?ku|talwar)\b|'
    r'\bchaa?ku\s+(?:le\s*ke|leke|ke\s+saath)|हथियारबंद|हथियारों\s+से\s+लैस)',
    re.I
)
EXTORTION_TAKING_RE = re.compile(
    r'(?:\b(?:hand(?:ed)?\s+over|forced\s+(?:me|him|her)\s+to\s+(?:give|hand)|made\s+(?:me|him|her)\s+(?:give|hand)|'
    r'nikaa?l\w*|chh?ee?n\s+li\w*|le\s+li(?:ya|ye|)|de\s+di(?:ya|ye|)|dena\s+pada)\b|'
    r'छीन|ले\s+लिया|दे\s+दिया|देना\s+पड़ा)',
    re.I
)

# Explicit statements that the taken property, or its value, was given back.
RESTORATION_PATTERNS = [
    r'(?<!\bI )(?<!\bwe )\b(?:returned|restored|gave\s+back|handed\s+back|brought\s+back|give\s+back)\s+'
    r'(?:it|them|the\s+\w+|my\s+\w+|our\s+\w+|all\s+(?:the\s+)?\w+|everything)\b(?!\s+(?:home|house))',
    r'\b(?:it|they|the\s+\w+|my\s+\w+)\s+(?:was|were|has\s+been|have\s+been)\s+(?:returned|restored|given\s+back|handed\s+back)\b',
    r'\b(?:paid|repaid|returned|restored)\s+(?:back\s+)?(?:me\s+)?(?:the\s+)?(?:full\s+)?(?:value|amount|money|cost)\b',
    r'\b(?:wapas|vapas|waapas)\s+(?:kar|de|lauta)\s*(?:diya|di|diye)\b|\blauta\s+(?:diya|di|diye)\b',
    r'(?:वापस\s+(?:कर|दे|लौटा)\s*(?:दिया|दी|दिए)|लौटा\s+(?:दिया|दी|दिए))',
]
RESTORATION_NEGATION_RE = re.compile(r"(?:\bnot|\bnever|n't|\bnahi|\bnahin|नहीं)\s*(?:\w+\s+){0,2}$", re.I)

# Capacity indicators that may bring criminal breach of trust within an aggravated sub-section.
CBT_CAPACITY_PATTERNS = {
    "316(3)": r'\b(?:carrier|transporter|transport\s+company|courier|logistics|wharfinger|warehouse(?:-keeper|\s+keeper)?)\b',
    "316(4)": r'(?:\b(?:employee|employed|servant|clerk|staff|worker|accountant|cashier|naukar|munim)\b|कर्मचारी|नौकर)',
    "316(5)": r'\b(?:banker|bank\s+manager|public\s+servant|government\s+(?:officer|official|servant)|merchant|broker|agent|attorney|factor|dalal)\b',
}

# Model labels for deterministic fallback responses. "LLM Inactive" is kept for the unconfigured case
# for compatibility; the structured inference_status field is authoritative.
FALLBACK_STATUS_LABELS = {
    "fallback_llm_unavailable": "LLM Inactive",
    "fallback_llm_failed": "LLM Inference Failed",
    "fallback_llm_not_invoked": "LLM Not Invoked: No Retrieval Candidates",
}

# Procedural review considers candidates whose validated score reaches this floor. It affects only the
# procedural recommendation text, not which provisions are predicted or how they are ranked.
PROCEDURAL_SUPPORT_SCORE_FLOOR = 0.5


class LegalAnalysisService:
    def __init__(
        self,
        corpus: Optional[BNSCorpus] = None,
        retriever: Optional[BM25LegalRetriever] = None,
        llm_client: Optional[GeminiLegalClient] = None,
        synonym_map: Optional[Dict[str, str]] = None
    ):
        self.corpus = corpus or BNSCorpus()
        self.retriever = retriever or BM25LegalRetriever(self.corpus)
        self.llm_client = llm_client or GeminiLegalClient()
        self.synonym_map = synonym_map if synonym_map is not None else DEFAULT_SYNONYM_MAP

    def translate_synonyms(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Translates colloquial synonyms to standard legal terms across English, Hindi, and Hinglish."""
        if not text or not self.synonym_map:
            return text or "", []

        translations = []
        standardized_text = text
        sorted_syns = sorted(self.synonym_map.keys(), key=len, reverse=True)

        for syn in sorted_syns:
            # Boundary-aware pattern supporting ASCII and Unicode/Devanagari scripts
            pattern = r'(?:(?<=[\s\b.,!?;:\'\"()\[\]])|^)' + re.escape(syn) + r'(?=(?:[\s\b.,!?;:\'\"()\[\]]|$))'
            if re.search(pattern, standardized_text, re.IGNORECASE):
                std_term = self.synonym_map[syn]
                translations.append({
                    "synonym": syn,
                    "standard_term": std_term
                })
                standardized_text = re.sub(pattern, std_term, standardized_text, flags=re.IGNORECASE)

        return standardized_text, translations

    def detect_negations(self, text: str) -> List[str]:
        """Identifies explicit negative statements within the text."""
        detected = []
        for pat in NEGATION_PATTERNS:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                detected.append(m.strip())
        return list(set(detected))

    def _validate_candidate_elements(
        self,
        sec_num: int,
        sec_data: Dict[str, Any],
        app_score: float,
        rag_score: float,
        reasoning: str,
        supported_elements: List[str],
        unestablished_elements: List[str],
        negations: List[str],
        raw_narrative: str,
        is_explicit_score: bool = True
    ) -> Tuple[float, float, str, List[str], List[str]]:
        """
        Validates statutory elements against stated negations and narrative facts.
        Evaluates statutory alternatives under BNS Section 309 (death, hurt, wrongful restraint,
        or fear of instant death, hurt, or wrongful restraint) so that robbery is not excluded
        merely because weapons or completed injury are absent if restraint or threats occurred.
        """
        combined_text = f"{raw_narrative} {' '.join(negations)}".lower()

        # Strip negated assertions so negative mentions like "no weapons were used", "no one was hurt",
        # "nobody was threatened" do not trigger affirmative robbery circumstances.
        # Use bounded patterns so contrastive clauses (e.g. "no violence, but he threatened me") preserve positive evidence.
        clean_text = raw_narrative
        for n in negations:
            clean_text = clean_text.replace(n, " ")
        for pat in NEGATION_PATTERNS:
            clean_text = re.sub(pat, " ", clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(
            r'\b(?:no|neither|without|did\s+not\s+have|never\s+used)\s+(?:any\s+)?(?:\w+\s+){0,3}?(?:weapon|weapons|violence|force|injury|injuries|harm|threat|threats)(?:\s+(?:was|were)\s+(?:used|involved|present|produced))?\b',
            ' ', clean_text, flags=re.IGNORECASE
        )
        clean_text = re.sub(
            r'\b(?:no\s+(?:one|body|person)|nobody)\s+(?:was\s+)?(?:ever\s+)?(?:hurt|injured|threatened|restrained|harmed)(?:\s+or\s+(?:hurt|injured|threatened|restrained|harmed))*\b',
            ' ', clean_text, flags=re.IGNORECASE
        )

        # Strip figurative pricing and metaphorical robbery expressions so slang does not trigger Section 309
        clean_text = re.sub(
            r'\b(?:daylight\s+robbery|loot\s+rahe|loot\s+macha|khule\s*aam\s*loot|खुलेआम\s*लूट|लूट\s*मचा)\b',
            ' ', clean_text, flags=re.IGNORECASE
        )

        # Strip hypothetical comparisons, similes, and figurative expressions involving weapons or bodily harm
        clean_text = re.sub(
            r'\b(?:faster|quicker|worse|more)\s+than\s+(?:a\s+|an\s+)?(?:\w+\s+){0,3}?(?:gun|knife|weapon|robber|thief)\b',
            ' ', clean_text, flags=re.IGNORECASE
        )
        clean_text = re.sub(
            r'\b(?:like|as\s+if)\s+(?:a\s+|an\s+)?(?:\w+\s+){0,3}?(?:gun|knife|weapon|robber|hit|punch|slap)\b',
            ' ', clean_text, flags=re.IGNORECASE
        )
        clean_text = re.sub(
            r'\b(?:felt|feels)\s+like\s+(?:a\s+|an\s+)?(?:\w+\s+){0,3}?(?:punch|hit|slap|shot|robbed)\b',
            ' ', clean_text, flags=re.IGNORECASE
        )
        clean_text = re.sub(
            r'\b(?:an?\s+)?(?:guy|man|person|someone|armed\s+robber|robber)\s+with\s+(?:a\s+)?(?:gun|knife|weapon|pistol)\s+(?:could|can|would|might)(?:\s+not|\s*n\'t)?\b',
            ' ', clean_text, flags=re.IGNORECASE
        )
        clean_text = re.sub(
            r'\bwould\s+rather\s+(?:be\s+)?(?:hit|shot|punched|robbed|killed)\b',
            ' ', clean_text, flags=re.IGNORECASE
        )
        clean_text = re.sub(
            r'\beven\s+(?:a\s+|an\s+)?(?:guy|man|person|robber)\s+with\s+(?:a\s+)?(?:gun|knife|weapon)\b',
            ' ', clean_text, flags=re.IGNORECASE
        )

        for pat in FIGURATIVE_HURT_PATTERNS:
            clean_text = re.sub(pat, ' ', clean_text, flags=re.IGNORECASE)

        # Check for affirmative Robbery circumstances under BNS Section 309:
        # Statutory alternatives: death, hurt, wrongful restraint, or fear of instant death, hurt, or wrongful restraint.
        has_restraint = bool(ROBBERY_RESTRAINT_RE.search(clean_text))
        has_threat = bool(ROBBERY_THREAT_RE.search(clean_text))
        has_hurt = bool(ROBBERY_HURT_RE.search(clean_text))
        has_weapon = bool(ROBBERY_ARMED_RE.search(clean_text))

        robbery_circumstances_present = has_restraint or has_threat or has_hurt or has_weapon

        # Non-confrontational sneak/pocket/unattended theft indicators:
        non_confrontational_theft = bool(re.search(
            r'\b(?:pocket|drawer|desk|bus\s+stop|unattended|while\s+i\s+was\s+(?:standing|walking|away|asleep)|behind\s+my\s+back)\b',
            raw_narrative, re.I
        ))
        is_commercial_or_figurative = bool(re.search(
            r'\b(?:daylight\s+robbery|prices?|overpriced|expensive|mrp|popcorn|ticket|promotion|credit|presentation)\b',
            raw_narrative, re.I
        ))
        explicit_non_violence = any(
            re.search(r'\b(?:no|without|not)\s+(?:any\s+)?(?:weapon|weapons|violence|hurt|injury|force|harm|threat)', n, re.I)
            for n in negations
        ) or bool(re.search(r'\b(?:no weapons?|no one was hurt|nobody was hurt|no violence|without weapons?|without violence|no force)\b', raw_narrative, re.I)) \
          or any(re.search(pat, raw_narrative, re.I) for pat in MULTILINGUAL_VIOLENCE_NEGATION_PATTERNS)

        is_contradicted = False

        # ── Section 309: Robbery ──
        if sec_num == 309:
            # Robbery is supported only if a statutory alternative (hurt, restraint, or fear of instant death,
            # hurt or restraint) is stated. An explicit Gemini score is never raised by keyword matches; in
            # deterministic mode Section 309 is retained only when such circumstances and a taking are stated.
            has_taking = bool(TAKING_RE.search(raw_narrative) or EXTORTION_TAKING_RE.search(raw_narrative))
            heuristic_support = robbery_circumstances_present and has_taking
            if robbery_circumstances_present and (is_explicit_score or heuristic_support):
                if has_restraint and not any("restraint" in s.lower() for s in supported_elements):
                    supported_elements.append("wrongful restraint stated in connection with the taking (BNS Section 309)")
                if has_threat and not any("threat" in s.lower() or "fear" in s.lower() for s in supported_elements):
                    supported_elements.append("threat or fear of instant death or hurt stated (BNS Section 309)")
                if has_hurt and not any("hurt" in s.lower() for s in supported_elements):
                    supported_elements.append("hurt stated in connection with the taking (BNS Section 309)")
                if has_weapon and not any("weapon" in s.lower() for s in supported_elements):
                    supported_elements.append("offender armed with or displaying a weapon (BNS Section 309)")
                if not is_explicit_score:
                    if app_score < 0.5:
                        app_score = 0.85
                    reasoning = (
                        "BNS Section 309 (Robbery) may apply: the narrative states a taking together with statutory "
                        f"circumstances ({', '.join(supported_elements)}). Whether the hurt, restraint or fear was "
                        "caused for the purpose of committing or carrying away the theft requires verification."
                    )
                if not any("nexus" in u.lower() for u in unestablished_elements):
                    unestablished_elements.append(
                        "Nexus between the violence, restraint or threat and the taking (BNS Section 309) is not verified."
                    )
            elif is_explicit_score and not (explicit_non_violence or non_confrontational_theft or is_commercial_or_figurative):
                # Gemini's applicability judgement stands; it is only lowered on contradiction.
                pass
            elif not is_explicit_score and not (explicit_non_violence or non_confrontational_theft or is_commercial_or_figurative):
                is_contradicted = True
                app_score = 0.0
                unestablished_elements.append(
                    "Not supported: the narrative does not state hurt, wrongful restraint, or fear of instant death, "
                    "hurt or wrongful restraint in connection with a taking (alternative essential ingredients of "
                    "Robbery under BNS Section 309)."
                )
                reasoning = (
                    "BNS Section 309 (Robbery) is not supported by the stated facts: deterministic validation found no "
                    "statement of hurt, wrongful restraint or instant threat accompanying a theft or extortion."
                )
            else:
                is_contradicted = True
                app_score = 0.0
                supported_elements = [
                    el for el in supported_elements
                    if not re.search(r'\b(violence|hurt|injury|weapon|force|threat|restraint)\b', el, re.I)
                ]
                contradiction_note = (
                    "Contradicted by complaint facts: narrative describes non-confrontational theft with no hurt, "
                    "no wrongful restraint, and no fear of instant harm (essential alternative statutory ingredients of Robbery under BNS Section 309)."
                )
                if not any("contradicted" in u.lower() for u in unestablished_elements):
                    unestablished_elements.append(contradiction_note)
                reasoning = (
                    "BNS Section 309 (Robbery) requires theft or extortion accompanied by voluntarily causing or "
                    "threatening death, hurt, or wrongful restraint. Here, no force, restraint, or threat occurred "
                    "('no weapons used / no one hurt'), legally negating the essential aggravating elements of Robbery."
                )

        # ── Section 304: Snatching ──
        # Snatching requires suddenly, quickly, or forcibly seizing or grabbing property.
        elif sec_num == 304:
            if explicit_non_violence and ("pocket" in combined_text or "bus stop" in combined_text):
                # Pickpocketing without sudden or forcible snatching
                if not any("sudden" in u.lower() or "forcibl" in u.lower() for u in unestablished_elements):
                    unestablished_elements.append(
                        "Snatching requires sudden, quick, or forcible seizure; stealthy pickpocketing falls primarily under simple theft (Section 303)."
                    )

        # ── Section 314: Dishonest Misappropriation ──
        # Requires property to come into possession non-trespassorily and subsequently converted.
        elif sec_num == 314:
            if "pocket" in combined_text or "without my consent" in combined_text:
                if not any("trespass" in u.lower() or "possession" in u.lower() for u in unestablished_elements):
                    unestablished_elements.append(
                        "Requires property to have come into possession without initial trespassory theft (e.g. finding lost property); "
                        "narrative indicates direct non-consensual taking from complainant's pocket."
                    )
                # Demote applicability relative to primary theft
                if app_score > 0.35:
                    app_score = 0.25

        # ── Section 62: Attempt to commit offences ──
        elif sec_num == 62:
            has_attempt = bool(re.search(
                r'(?:\b(?:attempt|attempted|attempting|trying\s+to|tried\s+to|koshish|prayas|interrupted|foiled|stopped\s+before|caught\s+before)\b|प्रयास|प्रयत्न|कोशिश)',
                raw_narrative, re.I
            ))
            if has_attempt:
                if not any("attempt" in s.lower() for s in supported_elements):
                    supported_elements.append("Act towards the commission of the offence (BNS Section 62)")
                # An explicit Gemini score (including 0.0) is never raised by keyword matches.
                if not is_explicit_score:
                    if app_score < 0.6:
                        app_score = 0.8
                    reasoning = (
                        "BNS Section 62 may apply: the narrative describes an attempt in which an act was done towards "
                        "the commission of the offence, but the substantive offence was interrupted or foiled before completion."
                    )
            else:
                if app_score > 0.4:
                    app_score = 0.2


        # ── Strict Scoring Decoupling: BM25 must NOT inflate contradicted sections ──
        if is_contradicted or (is_explicit_score and app_score <= 0.0):
            final_score = 0.0
            app_score = 0.0
        else:
            final_score = round(0.7 * app_score + 0.3 * min(rag_score, 1.0), 4)

        return app_score, final_score, reasoning, supported_elements, unestablished_elements

    def _determine_schedule_metadata(
        self,
        sec_num: int,
        sec_data: Dict[str, Any],
        raw_narrative: str
    ) -> Tuple[Optional[bool], Optional[bool]]:
        """
        Determines verified cognizable and bailable status under BNSS Schedule I.
        Returns a field as bool only when every applicable Schedule I row agrees on it,
        otherwise None (conditional or unverified).

        Theft (Section 303) is resolved to the main Section 303(2) row only when the taken property
        is stated to be worth Rs 5,000 or more. Below that value the Schedule I classification depends
        on restoration of the property and, under the BNS proviso, on a first conviction, which cannot
        be established from a complaint, so both fields remain None.
        """
        if not sec_data.get("schedule_i_entry"):
            return None, None

        if sec_num == 303:
            if assess_stolen_property_value(raw_narrative).meets_threshold is not True:
                return None, None
            resolved = resolve_schedule_classification(303, "303(2)")
        else:
            resolved = resolve_schedule_classification(sec_num)

        return resolved["is_cognizable"], resolved["is_bailable"]

    @staticmethod
    def _parse_explicit_score(value: Any) -> Optional[float]:
        """
        Returns an explicitly supplied applicability score clamped to [0.0, 1.0], or None when the
        score is missing, null, boolean or non-numeric. An explicit 0.0 is returned as 0.0, not None.
        """
        if value is None or isinstance(value, bool):
            return None
        try:
            score = float(value)
        except (ValueError, TypeError):
            return None
        if score != score or score in (float("inf"), float("-inf")):
            return None
        return min(max(score, 0.0), 1.0)

    @staticmethod
    def _restoration_stated(text: str) -> bool:
        """True only if the narrative explicitly states that taken property or its value was given back."""
        for pat in RESTORATION_PATTERNS:
            for m in re.finditer(pat, text, re.I):
                if not RESTORATION_NEGATION_RE.search(text[max(0, m.start() - 30):m.start()]):
                    return True
        return False

    @staticmethod
    def _possible_cbt_sub_sections(text: str) -> List[str]:
        """Returns aggravated Section 316 sub-sections suggested by the capacity in which property was entrusted."""
        return [sub for sub, pat in CBT_CAPACITY_PATTERNS.items() if re.search(pat, text, re.I)]

    def _enrich_facts_block(
        self,
        stated_facts: List[str],
        inferred_facts: List[str],
        negations: List[str],
        missing_facts: List[str],
        candidate_sections: List[int],
        raw_narrative: str
    ) -> FactExtractionBlock:
        """Separates stated facts from legal inferences and ensures missing statutory facts are recorded."""
        enriched_stated = []
        enriched_inferred = list(inferred_facts)
        enriched_missing = list(missing_facts)

        for fact in stated_facts:
            # Move mental state / mens rea out of stated physical facts into inferred facts
            if re.search(r'\b(?:dishonest|intent|intention|mens rea|animus)\b', fact, re.I):
                if fact not in enriched_inferred:
                    enriched_inferred.append(fact)
            else:
                enriched_stated.append(fact)

        # If theft is considered, ensure animus furandi is noted as an inference if taking is non-consensual
        if 303 in candidate_sections:
            if not any("dishonest" in inf.lower() for inf in enriched_inferred):
                enriched_inferred.append(
                    "Dishonest intention (animus furandi) is inferred from the non-consensual removal of property from possession."
                )

            # Check if property value is specified in narrative
            value_assessment = assess_stolen_property_value(raw_narrative)
            if value_assessment.status != "stated":
                if value_assessment.status == "ambiguous":
                    val_q = "Total value of the stolen property is unclear from the amounts stated (critical to determine whether the Section 303(2) proviso for theft under ₹5,000 can apply)."
                else:
                    val_q = "Monetary value of stolen property is not specified (critical to determine whether the Section 303(2) proviso for theft under ₹5,000 applies)."
                if not any("value" in m.lower() for m in enriched_missing):
                    enriched_missing.append(val_q)

            rec_q = "Status of property recovery or restoration is unverified (Section 303(2) proviso requires return of property or payment of value)."
            if not any("restor" in m.lower() or "recover" in m.lower() for m in enriched_missing):
                enriched_missing.append(rec_q)

            prior_q = "Prior criminal conviction record of the accused is unverified (Section 303(2) proviso applies only to first-time convictions)."
            if not any("prior" in m.lower() or "conviction" in m.lower() for m in enriched_missing):
                enriched_missing.append(prior_q)

        # If candidate sections are empty or no stated facts, record essential missing facts
        if not candidate_sections or not enriched_stated:
            for q in [
                "Specific details of what incident or unlawful act occurred.",
                "Date, time, and precise location of the incident.",
                "Identity or description of suspects or persons involved.",
                "Whether any property was taken or damaged, or if physical force, injury, or threat occurred."
            ]:
                if not any(q.split()[0].lower() in m.lower() for m in enriched_missing):
                    enriched_missing.append(q)

        return FactExtractionBlock(
            stated_facts=enriched_stated,
            inferred_facts=enriched_inferred,
            negated_events=negations,
            missing_facts_to_clarify=enriched_missing
        )

    def _audit_and_qualify_procedural_recommendation(
        self,
        predictions: List[SectionPredictionItem],
        facts_block: FactExtractionBlock,
        raw_narrative: str,
        raw_action: str
    ) -> str:
        """
        Audits procedural recommendations against BNSS Schedule I rules and material facts.

        1. Vague complaints lacking penal allegations require factual clarification from the complainant;
           they never warrant a preliminary enquiry under Section 173(3) BNSS or formal police action.
        2. Section 173(3) BNSS covers information relating to a COGNIZABLE offence made punishable for
           THREE YEARS OR MORE BUT LESS THAN SEVEN YEARS. With prior permission of an officer not below the
           rank of DSP, the officer in charge may conduct a preliminary enquiry (within fourteen days) or
           proceed with investigation when a prima facie case exists.
        3. Offences punishable with seven years or more, and non-cognizable offences (Section 174 BNSS),
           fall outside Section 173(3).
        4. Every sufficiently supported candidate is reviewed, not only the top-ranked one. Where candidates
           imply different procedural routes, the recommendation preserves that uncertainty; under
           Section 174(4) BNSS a case relating to several offences of which at least one is cognizable is
           deemed a cognizable case.
        5. User-supplied legal claims or model assertions (e.g. demanding Section 173(3) or an unconditional
           FIR) are audited against verified statutory conditions and overridden where inaccurate.
        """
        # Check if user narrative or raw action attempted to invoke Section 173(3)
        narrative_cites_173_3 = bool(re.search(r'\b173\s*\(\s*3\s*\)', raw_narrative, re.I))
        action_cites_173_3 = bool(raw_action and re.search(r'\b173\s*\(\s*3\s*\)', raw_action, re.I))
        cites_173_3 = narrative_cites_173_3 or action_cites_173_3

        # ── Case: Inconclusive / Vague / No positive penal predictions ──
        if not predictions or predictions[0].score <= 0.0:
            rec = (
                "Preliminary assessment: Insufficient factual allegations to disclose or establish any penal offence "
                "under the Bharatiya Nyaya Sanhita, 2023. Formal procedural steps under the BNSS, 2023 (such as an FIR "
                "under Section 173 or NCR entry under Section 174) cannot be initiated on an ambiguous narrative. "
                "Factual clarification from the complainant is required regarding specific acts, affected persons or property, "
                "date, time, location, and whether any force, injury, or unlawful taking occurred."
            )
            if cites_173_3:
                rec += (
                    " Note: Preliminary enquiry under Section 173(3) BNSS is legally inapplicable to vague complaints lacking "
                    "prima facie allegations of a cognizable offence; Section 173(3) requires information relating to "
                    "a cognizable offence made punishable for three years or more but less than seven years."
                )
            return rec

        top_pred = predictions[0]
        supported = [p for p in predictions if p.score >= PROCEDURAL_SUPPORT_SCORE_FLOOR]
        if top_pred not in supported:
            supported.insert(0, top_pred)

        if len(supported) == 1:
            return self._single_offence_procedure(top_pred, predictions, raw_narrative, raw_action, cites_173_3)
        return self._multi_offence_procedure(supported, raw_narrative, cites_173_3)

    def _theft_procedure_note(self, raw_narrative: str) -> str:
        """Fact-qualified Schedule I classification for theft under BNS Section 303."""
        assessment = assess_stolen_property_value(raw_narrative)
        proviso_pathway = (
            "Schedule I of the BNSS classifies theft where the value of the property is less than ₹5,000 and the "
            "property is returned or its value restored (punishable with community service) as NON-COGNIZABLE and "
            "BAILABLE, with procedure under Section 174 BNSS. The proviso to Section 303(2) BNS additionally requires "
            "that the person is convicted for the first time, which cannot be established from a complaint. Whether such a "
            "complaint may be treated as non-cognizable at the FIR-registration stage is unsettled and requires qualified legal review."
        )
        main_pathway = (
            "Otherwise, theft under Section 303(2) BNS is COGNIZABLE and NON-BAILABLE under BNSS Schedule I and the "
            "information is recorded under Section 173(1) BNSS."
        )
        range_note = (
            "Theft under Section 303(2) is punishable with imprisonment up to three years (one to five years on a "
            "second or subsequent conviction), within the range of Section 173(3) BNSS on the maximum-term reading of "
            f"'punishable for' (pending qualified legal review). {BNSS_173_3_PROCEDURE_TEXT} "
            f"{BNSS_173_3_CAVEAT_TEXT}"
        )

        if assessment.meets_threshold is True:
            return (
                f"Theft under BNS Section 303(2): the stated value of the taken property (at least ₹{format_inr(assessment.value)}) "
                "is ₹5,000 or more, so the community-service proviso cannot apply. Classified as COGNIZABLE and NON-BAILABLE "
                "under Schedule I of the BNSS, 2023; information is recorded under Section 173(1) BNSS for FIR registration. "
                f"{range_note} Investigative verification of suspect identity and property recovery is advised."
            )

        restoration = (
            " The complaint states that the property or its value was returned; prior-conviction status remains unverified."
            if self._restoration_stated(raw_narrative) else
            " Restoration of the property and the accused's prior-conviction record are unverified."
        )
        if assessment.meets_threshold is False:
            return (
                f"The stated value of the taken property is ₹{format_inr(assessment.value)} (below ₹5,000). Procedural "
                "classification under BNSS Schedule I is conditional on facts that cannot be established from the complaint:\n"
                f"1. {proviso_pathway}\n"
                f"2. {main_pathway}\n"
                f"{restoration.strip()} Investigative verification is required before formal procedural determination."
            )

        value_note = (
            "Several amounts are stated and their attribution to the taken property is unclear"
            if assessment.status == "ambiguous" else "The value of the taken property is not stated"
        )
        return (
            "Procedural course under the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 is conditional on unverified material facts "
            f"(property value, property restoration, and prior conviction record). {value_note}.\n"
            "1. If the stolen property value is ₹5,000 or more, or the proviso otherwise does not apply, the offence under "
            "Section 303(2) BNS is cognizable and non-bailable under BNSS Schedule I (information recorded under Section 173(1) BNSS "
            "for FIR registration).\n"
            f"2. {proviso_pathway}\n"
            "Investigative verification of property value and suspect history is required before formal procedural determination."
        )

    def _robbery_procedure_note(self, cites_173_3: bool) -> str:
        rec = (
            "The narrative alleges facts that, if verified, may constitute Robbery under BNS Section 309 (theft or extortion "
            "accompanied by causing or attempting to cause death, hurt or wrongful restraint, or fear of instant death, hurt "
            "or wrongful restraint). Robbery is classified as COGNIZABLE and NON-BAILABLE under Schedule I of the BNSS, 2023; "
            "information is to be recorded as an FIR under Section 173(1) BNSS."
        )
        if cites_173_3:
            rec += (
                " Note: BNSS Section 173(3) preliminary enquiry is legally INAPPLICABLE to Robbery because Section 309(4) carries "
                "rigorous imprisonment up to 10 years (up to 14 years on a highway between sunset and sunrise), which exceeds "
                "the 7-year ceiling ('less than seven years') specified in Section 173(3). Information is recorded under "
                "Section 173(1) BNSS without a Section 173(3) preliminary enquiry."
            )
        return rec

    def _cbt_procedure_note(self, raw_narrative: str) -> str:
        possible = self._possible_cbt_sub_sections(raw_narrative)
        rec = (
            "Criminal breach of trust under BNS Section 316 is classified as COGNIZABLE and NON-BAILABLE under Schedule I of "
            "the BNSS, 2023 in every sub-section, and information is recorded under Section 173(1) BNSS. The applicable "
            "sub-section depends on the capacity in which the property was entrusted: Section 316(2) is punishable with up to "
            "5 years; Section 316(3) (carrier, wharfinger or warehouse-keeper) and Section 316(4) (clerk or servant) with up to "
            "7 years; Section 316(5) (public servant, banker, merchant, factor, broker, attorney or agent) with imprisonment for "
            "life or up to 10 years."
        )
        if possible:
            rec += (
                f" The complaint suggests entrustment in a capacity that may fall under Section {' or Section '.join(possible)}; "
                "if so, the maximum term is seven years or more and, on the maximum-term reading of 'punishable for' (pending "
                "qualified legal review), Section 173(3) BNSS does not apply. The capacity of entrustment requires verification."
            )
        else:
            rec += (
                " If only Section 316(2) applies, the offence falls within the range of Section 173(3) BNSS. "
                f"{BNSS_173_3_PROCEDURE_TEXT} {BNSS_173_3_CAVEAT_TEXT} The capacity in which the property was entrusted "
                "requires verification before this is determined."
            )
        return rec

    def _grievous_hurt_procedure_note(self) -> str:
        return (
            "Voluntarily causing grievous hurt under BNS Section 117 is classified as COGNIZABLE under Schedule I of the BNSS, 2023; "
            "it is BAILABLE under Section 117(2) but NON-BAILABLE under Section 117(3) (permanent disability or persistent "
            "vegetative state) and Section 117(4) (grievous hurt by a group of five or more persons on specified grounds). "
            "Information is recorded under Section 173(1) BNSS. Each sub-section is punishable with seven years or more, so on "
            "the maximum-term reading of 'punishable for' (pending qualified legal review) Section 173(3) BNSS does not apply."
        )

    def _mischief_procedure_note(self) -> str:
        return (
            "Mischief under BNS Section 324 is BAILABLE in every sub-section of BNSS Schedule I, but cognizability depends on "
            "the sub-section: Sections 324(2) to 324(4) are NON-COGNIZABLE (Section 174 BNSS), while Sections 324(5) and "
            "324(6) are COGNIZABLE (Section 173(1) BNSS). The amount of loss or damage and any preparation for causing "
            "death, hurt or wrongful restraint require verification. Unresolved: "
            f"{OPEN_LEGAL_QUESTIONS['324_value_bands']}"
        )

    def _misappropriation_procedure_note(self, cites_173_3: bool) -> str:
        rec = (
            "Dishonest misappropriation of property under BNS Section 314 is classified as NON-COGNIZABLE and BAILABLE under Schedule I of the BNSS, 2023. "
            "Under Section 174 BNSS, the substance of the information is entered in the book prescribed by the State Government "
            "(commonly the NCR register) and the informant referred to the Magistrate; police cannot investigate without an order "
            "from the Magistrate (Section 174(2) BNSS)."
        )
        if cites_173_3:
            rec += " Note: Section 173(3) BNSS applies only to cognizable offences and is inapplicable to non-cognizable offences."
        return rec

    def _section_procedure_note(self, pred: SectionPredictionItem, raw_narrative: str, cites_173_3: bool) -> Optional[str]:
        """Section-specific procedural note, or None when only the general classification applies."""
        if pred.section == 303:
            return self._theft_procedure_note(raw_narrative)
        if pred.section == 309:
            return self._robbery_procedure_note(cites_173_3)
        if pred.section == 316:
            return self._cbt_procedure_note(raw_narrative)
        if pred.section == 117:
            return self._grievous_hurt_procedure_note()
        if pred.section == 324:
            return self._mischief_procedure_note()
        return None

    @staticmethod
    def _classification_label(pred: SectionPredictionItem) -> str:
        has_entry = resolve_schedule_classification(pred.section)["verified"]
        if pred.is_cognizable is None:
            if has_entry:
                return "classification under BNSS Schedule I is conditional on material facts or sub-section"
            return "classification not verified in this registry"
        cog = "COGNIZABLE" if pred.is_cognizable else "NON-COGNIZABLE"
        if pred.is_bailable is None:
            bail = "bailability depends on the sub-section"
        else:
            bail = "BAILABLE" if pred.is_bailable else "NON-BAILABLE"
        return f"{cog}, {bail} under BNSS Schedule I"

    def _audit_173_3_claims(self, preds: List[SectionPredictionItem]) -> str:
        notes = []
        for p in preds:
            elig = check_bnss_173_3_eligibility(p.section, p.is_cognizable)
            if elig["eligible"]:
                notes.append(f"Section {p.section}: within the Section 173(3) range")
            else:
                notes.append(f"Section {p.section}: {elig['reason']}")
        return (
            "Section 173(3) BNSS is assessed offence by offence: " + " | ".join(notes) +
            f" {BNSS_173_3_PROCEDURE_TEXT} {BNSS_173_3_CAVEAT_TEXT}"
        )

    def _single_offence_procedure(
        self,
        top_pred: SectionPredictionItem,
        predictions: List[SectionPredictionItem],
        raw_narrative: str,
        raw_action: str,
        cites_173_3: bool
    ) -> str:
        """Procedural recommendation when only one candidate is sufficiently supported."""
        note = self._section_procedure_note(top_pred, raw_narrative, cites_173_3)
        if note:
            return note

        # ── Case: Section 314 (Dishonest Misappropriation alone) ──
        if top_pred.section == 314 and len([p for p in predictions if p.score > 0.3]) == 1:
            return self._misappropriation_procedure_note(cites_173_3)

        action_cites_173_3 = bool(raw_action and re.search(r'\b173\s*\(\s*3\s*\)', raw_action, re.I))

        # ── Audit and Sanitize raw_action (if provided from LLM or external source) ──
        if raw_action and len(raw_action) > 20 and not raw_action.startswith("Prima facie"):
            # If raw_action or narrative asserted Section 173(3), verify eligibility
            if cites_173_3:
                elig_info = check_bnss_173_3_eligibility(top_pred.section, top_pred.is_cognizable)
                if not elig_info.get("eligible"):
                    max_p = elig_info.get("max_punishment")
                    if elig_info.get("conditional"):
                        return (
                            f"Correction of procedural advice: Section 173(3) BNSS applicability to Section {top_pred.section} "
                            f"({top_pred.title}) cannot be confirmed. {elig_info['reason']} {BNSS_173_3_CAVEAT_TEXT}"
                        )
                    if elig_info.get("is_cognizable") is False:
                        reason = "the offence is classified as non-cognizable under BNSS Schedule I"
                        correct_proc = "Procedure is governed by Section 174 BNSS (NCR and Magistrate referral)."
                    elif max_p is not None and max_p >= 7.0:
                        reason = ("its maximum punishment is seven years or more, outside the 'less than seven years' range of "
                                  "Section 173(3) on the maximum-term reading (pending qualified legal review)")
                        correct_proc = "Information must be recorded under Section 173(1) BNSS for FIR registration without Section 173(3) preliminary enquiry."
                    else:
                        reason = elig_info.get("reason", "statutory conditions are not satisfied")
                        correct_proc = "Procedure depends on verified Schedule I classification of the offence."

                    return (
                        f"Correction of procedural advice: Section 173(3) BNSS preliminary enquiry is legally INAPPLICABLE to "
                        f"Section {top_pred.section} ({top_pred.title}) because {reason}. {correct_proc}"
                    )
                elif not action_cites_173_3 or not re.search(r'deputy\s+superintendent|\bdsp\b', raw_action, re.I) \
                        or not re.search(r'fourteen|14', raw_action):
                    raw_action += f" (Statutory note: {BNSS_173_3_PROCEDURE_TEXT} {BNSS_173_3_CAVEAT_TEXT})"
            return raw_action

        # ── General qualified fallback ──
        top_cited = ", ".join(f"Sec {p.section} ({p.title})" for p in predictions[:2])
        is_cog = top_pred.is_cognizable
        if is_cog is True:
            proc_note = "Classified as COGNIZABLE under BNSS Schedule I; information recorded under Section 173(1) BNSS for FIR registration."
        elif is_cog is False:
            proc_note = "Classified as NON-COGNIZABLE under BNSS Schedule I; procedure under Section 174 BNSS (NCR and Magistrate referral)."
        else:
            proc_note = "Procedural classification under BNSS Schedule I is conditional on verification of material facts."

        rec = (
            f"Preliminary analysis identified potential application of {top_cited}. "
            f"{proc_note} Procedural registration under BNSS, 2023 is subject to investigative verification of material facts by the investigating officer."
        )
        if cites_173_3:
            rec += " " + self._audit_173_3_claims([top_pred])
        return rec

    def _multi_offence_procedure(
        self,
        supported: List[SectionPredictionItem],
        raw_narrative: str,
        cites_173_3: bool
    ) -> str:
        """Procedural review across several sufficiently supported candidate offences."""
        listing = "; ".join(
            f"Sec {p.section} ({p.title}): {self._classification_label(p)}" for p in supported
        )
        cognizable = [p for p in supported if p.is_cognizable is True]
        non_cognizable = [p for p in supported if p.is_cognizable is False]
        unknown = [p for p in supported if p.is_cognizable is None]

        def _names(preds):
            return ", ".join(f"Sec {p.section} ({p.title})" for p in preds)

        if cognizable:
            route = (
                f"At least one candidate offence ({_names(cognizable)}) is classified as cognizable. If that offence is made out "
                "on the facts, information is recorded under Section 173(1) BNSS; under Section 174(4) BNSS, a case relating to "
                "two or more offences of which at least one is cognizable is deemed to be a cognizable case."
            )
            if non_cognizable or unknown:
                route += (
                    " If it is not made out, the procedural route depends on the remaining candidates "
                    f"({_names(non_cognizable + unknown)})."
                )
            route += (
                " Where Section 173(3) BNSS is mentioned below, it is assessed offence by offence; on the maximum-term reading "
                "(pending qualified legal review) it does not apply to an offence whose maximum term is seven years or more."
            )
        elif non_cognizable and not unknown:
            route = (
                f"All supported candidate offences ({_names(non_cognizable)}) are classified as non-cognizable; procedure is "
                "governed by Section 174 BNSS (entry of the substance of the information and referral of the informant to the "
                "Magistrate; no investigation without a Magistrate's order)."
            )
        elif non_cognizable:
            route = (
                f"The candidates imply different procedural routes: {_names(non_cognizable)} is non-cognizable (Section 174 BNSS), "
                f"while the classification of {_names(unknown)} is conditional or unverified and could require recording under "
                "Section 173(1) BNSS. The procedural route cannot be determined until the material facts are verified."
            )
        else:
            route = (
                f"The procedural classification of {_names(unknown)} is conditional on material facts or not verified; the "
                "procedural route cannot be determined until those facts are verified."
            )

        parts = [f"Procedural review across supported candidate provisions — {listing}.", route]
        for p in supported:
            note = self._section_procedure_note(p, raw_narrative, cites_173_3)
            if note:
                parts.append(f"[Sec {p.section}] {note}")
        if cites_173_3:
            parts.append(self._audit_173_3_claims(supported))
        parts.append(
            "Procedural registration under BNSS, 2023 is subject to investigative verification of material facts by the investigating officer."
        )
        return "\n".join(parts)

    def _detect_non_penal_grievance(self, text: str) -> Optional[Tuple[str, str]]:
        """
        Distinguishes non-penal consumer pricing disputes, workplace grievances, and
        figurative expressions from genuine offences under the Bharatiya Nyaya Sanhita, 2023.
        
        Strict safety principles:
        1. Distinction is treated as a preliminary classification, not a definitive legal conclusion.
        2. Never suppresses complaints where affirmative penal allegations are present:
           - Actual physical violence, bodily harm, or real weapons
           - Tangible movable property taking (theft, snatching, house-breaking, trespass)
           - Financial, digital, or document crimes (forgery, breach of trust, cheating, embezzlement)
           - Unlawful restraint, extortion, or criminal intimidation
        3. Ignores physical keywords appearing in purely hypothetical, simile, or negated contexts
           (e.g., 'could not take money faster than a guy with a gun', 'felt like a punch in the gut').
        """
        if not text:
            return None

        # Clean text of hypothetical/simile comparisons before checking for affirmative crimes
        hypothetical_patterns = [
            r'\b(?:faster|quicker|worse|more)\s+than\s+(?:a\s+|an\s+)?(?:\w+\s+){0,3}?(?:gun|knife|weapon|robber|thief)\b',
            r'\b(?:like|as\s+if)\s+(?:a\s+|an\s+)?(?:\w+\s+){0,3}?(?:gun|knife|weapon|robber|hit|punch|slap)\b',
            r'\b(?:felt|feels)\s+like\s+(?:a\s+|an\s+)?(?:\w+\s+){0,3}?(?:punch|hit|slap|shot|robbed)\b',
            r'\b(?:an?\s+)?(?:guy|man|person|someone|armed\s+robber|robber)\s+with\s+(?:a\s+)?(?:gun|knife|weapon|pistol)\s+(?:could|can|would|might)(?:\s+not|\s*n\'t)?\b',
            r'\bwould\s+rather\s+(?:be\s+)?(?:hit|shot|punched|robbed|killed)\b',
            r'\beven\s+(?:a\s+|an\s+)?(?:guy|man|person|robber)\s+with\s+(?:a\s+)?(?:gun|knife|weapon)\b',
        ]
        audit_text = text
        for pat in hypothetical_patterns:
            audit_text = re.sub(pat, " ", audit_text, flags=re.IGNORECASE)

        # Check for explicit negations of violence/weapons
        audit_clean = audit_text
        for pat in NEGATION_PATTERNS:
            audit_clean = re.sub(pat, " ", audit_clean, flags=re.IGNORECASE)

        # Clean metaphorical/intangible occurrences of snatching/cheating before checking affirmative crimes
        # e.g., 'snatched the promotion/credit', 'feel cheated by ... pricing/prices/policy'
        audit_crime = audit_clean
        audit_crime = re.sub(
            r'\b(?:snatch|snatched|snatching)\s+(?:away\s+)?(?:all\s+)?(?:my\s+|our\s+|the\s+)?(?:promotion|credit|idea|thunder|spotlight|show|limelight|heart|happiness|peace|sleep|joy|reputation|opportunity|appraisal|time|sanity)\b',
            ' ',
            audit_crime,
            flags=re.I
        )
        audit_crime = re.sub(
            r'\b(?:feel|feels|feeling)\s+(?:completely\s+|totally\s+)?(?:robbed|cheated)\s+(?:and\s+(?:robbed|cheated)\s+)?(?:by|at)\b',
            ' ',
            audit_crime,
            flags=re.I
        )
        audit_crime = re.sub(
            r'\b(?:robbed\s+and\s+cheated|cheated\s+and\s+robbed)\s+by\s+(?:their|the)?\s*(?:daylight\s+robbery\s+)?(?:pricing|prices|bill|policy)\b',
            ' ',
            audit_crime,
            flags=re.I
        )

        # ── 1. Check for Affirmative Penal Allegations ──
        # If any of these are present, DO NOT gate out the complaint; preserve statutory pathways.

        # A. Actual physical crime or weapon indicators (not in hypothetical/negated context)
        affirmative_violence = bool(re.search(
            r'\b(?:gun|guns|knife|knives|weapon|weapons|pistol|chaku|talwar|blade|iron\s+rod|'
            r'revolver|dagger|firearm|hit|punched|slapped|kicked|struck|bleeding|fracture|'
            r'injured|injury|assaulted|cornered|pinned|tied\s+up|held\s+down|held\s+hostage|'
            r'choked|strangled|stabbed)\b',
            audit_crime, re.I
        ))

        # B. Affirmative threat of violence / criminal intimidation / extortion
        affirmative_threat = bool(re.search(
            r'\b(?:threatened\s+to\s+(?:kill|murder|shoot|stab|harm|break|beat)|'
            r'death\s+threat|demanded\s+extortion|demanded\s+ransom|blackmail)\b',
            audit_crime, re.I
        ))

        # C. Property crime (theft of tangible movable property, snatching, trespass, burglary)
        affirmative_property_crime = bool(re.search(
            r'\b(?:snatch|snatched|snatching|pickpocket|picked\s+my\s+pocket|'
            r'broke\s+open|forced\s+entry|broke\s+in|trespass|burglary|break-in|padlock|'
            r'(?:stole|stolen|chori|chura|loot\s+liya)\s+(?:my\s+|the\s+)?(?:wallet|purse|phone|watch|cash|money|rupees|jewellery|gold|chain|laptop|car|bike|cycle|bicycle|bag|backpack|goods|items|clothes|tools))\b',
            audit_crime, re.I
        ))

        # D. White-collar / Financial / Digital / Breach of Trust / Forgery offences
        affirmative_financial_digital = bool(re.search(
            r'\b(?:forged|forgery|counterfeit|fake\s+notes|fake\s+currency|fake\s+tickets?|'
            r'embezzl|misappropriat|cheated|cheating|fraud|defraud|breach\s+of\s+trust|'
            r'unauthorized\s+transfer|diverted\s+funds|hacked|tampered|deleted\s+(?:records|data|access|database))\b',
            audit_crime, re.I
        ))

        has_affirmative_crime = (
            affirmative_violence
            or affirmative_threat
            or affirmative_property_crime
            or affirmative_financial_digital
        )

        if has_affirmative_crime:
            # Preserve statutory pathways for criminal evaluation
            return None

        # ── 2. Check for Figurative Intangible Complaints ──
        intangible_patterns = [
            r'\b(?:stole|stealing|swiped|robbed|snatched)\s+(?:away\s+)?(?:all\s+)?(?:my\s+|our\s+|the\s+)?(?:promotion|credit|idea|thunder|spotlight|show|limelight|heart|happiness|peace|sleep|joy|reputation|opportunity|appraisal|time|sanity)\b',
            r'\brobbed\s+(?:me|us|him|her)\s+of\s+(?:all\s+)?(?:my\s+|our\s+|his\s+|her\s+)?(?:peace|peace\s+of\s+mind|happiness|joy|sleep|reputation|youth|dignity|sanity|time)\b',
            r'(?:कीमती\s+)?(?:समय|वक्त|चैन|नींद|शांति|सुख|दिल)\s*(?:लूट|चुरा|छीन)',
            r'(?:लूट|चुरा|छीन)\s*(?:लिया)?\s*.*?(?:समय|वक्त|चैन|नींद|शांति|सुख|दिल)',
            r'\b(?:samay|waqt|time|sukoon|chain|neend|shanti|dil)\s+(?:loot|chura|chin)\b',
            r'\b(?:loot|chura|chin)\s+liya\s+.*?(?:samay|waqt|time|sukoon|chain|neend|shanti|dil)\b'
        ]
        for pat in intangible_patterns:
            m = re.search(pat, text, re.I)
            if m:
                return ("intangible_metaphor", m.group(0))

        # ── 3. Check for Commercial Pricing / Consumer Disputes ──
        pricing_patterns = [
            r'\b(?:daylight\s+robbery|looting|robbery|loot\s+rahe|loot\s+macha|khule\s*aam\s*loot|खुलेआम\s*लूट|लूट\s*मचा)\b.*?\b(?:prices?|pricing|bill|billing|charged|charging|mrp|overpriced|expensive|rate|rates|menu|rupya\s+le\s+rahe|rupaye\s+le\s+rahe|ticket|popcorn|carry\s+bag)\b',
            r'\b(?:prices?|pricing|bill|billing|charged|charging|mrp|overpriced|expensive|rate|rates|menu|rupya\s+le\s+rahe|rupaye\s+le\s+rahe|ticket|popcorn|carry\s+bag)\b.*?\b(?:daylight\s+robbery|looting|robbery|loot\s+rahe|loot\s+macha|khule\s*aam\s*loot|खुलेआम\s*लूट|लूट\s*मचा)\b'
        ]
        for pat in pricing_patterns:
            m = re.search(pat, text, re.I)
            if m:
                return ("consumer_pricing", m.group(0))

        return None

    def _build_non_penal_response(
        self,
        raw_narrative: str,
        standard_narrative: str,
        translations: List[Dict[str, str]],
        grievance_type: str,
        matched_snippet: str
    ) -> OffenceClassificationResponse:
        """
        Constructs an appropriately qualified preliminary response when figurative language,
        consumer pricing disputes, or career grievances without penal elements are detected.
        
        Strict adherence to BNS principles:
        1. Presents the determination as a preliminary assessment, not a definitive legal conclusion.
        2. Correctly cites Section 303 read with Section 2(22) of BNS, 2023 for movable property.
        3. Identifies missing facts and explicitly preserves alternative statutory pathways
           (e.g., fraud, forgery, breach of trust, criminal intimidation) if unstated facts exist.
        """
        if grievance_type == "consumer_pricing":
            action = (
                f"Preliminary classification: The narrative appears to describe a consumer pricing dispute or "
                f"commercial grievance ('{matched_snippet}') rather than a cognizable penal offence under the "
                "Bharatiya Nyaya Sanhita, 2023. Penal property offences such as Theft (Section 303) or Robbery "
                "(Section 309) require dishonest, non-consensual taking of corporeal movable property or criminal force. "
                "This assessment is preliminary based on citizen-provided narrative facts. If the dispute involved unstated "
                "penal acts—such as physical assault, criminal intimidation (Section 351), or cheating (Section 318)—"
                "further material facts must be stated to evaluate those statutory pathways. For retail overcharging or "
                "pricing grievances without criminal acts, recourse lies before the Consumer Disputes Redressal Commission "
                "or Legal Metrology Department under the Consumer Protection Act, 2019."
            )
            fact_desc = f"Preliminary consumer pricing dispute or overcharging grievance ('{matched_snippet}')"
        else:
            action = (
                f"Preliminary classification: The narrative describes a figurative expression or workplace/career "
                f"grievance ('{matched_snippet}') rather than an actionable penal offence under the Bharatiya Nyaya "
                "Sanhita, 2023. Under Section 303 read with Section 2(22) of the BNS, 2023, penal offences against "
                "property strictly apply to corporeal movable property; intangible concepts (e.g., promotions, work credit, "
                "or professional reputation) cannot be the subject of penal theft or robbery. This is a preliminary assessment, "
                "not a definitive judicial finding. If the incident involved distinct unstated offences—such as criminal breach "
                "of trust (Section 316), cheating (Section 318), forgery of records (Section 336/338), or criminal intimidation "
                "(Section 351)—those specific facts must be provided for evaluation. In the absence of criminal acts, recourse "
                "lies through internal grievance mechanisms, labor forums, or civil litigation."
            )
            fact_desc = f"Preliminary figurative or non-corporeal career grievance ('{matched_snippet}')"

        facts_block = FactExtractionBlock(
            stated_facts=[fact_desc],
            inferred_facts=[
                "Preliminary assessment: Allegations regarding pricing or career recognition do not prima facie establish elements of penal property offences under BNS, 2023.",
                "Non-penal classification is preliminary and subject to verification of whether unstated criminal acts occurred."
            ],
            negated_events=["No corporeal theft, weapon, physical restraint, or criminal force reported"],
            missing_facts_to_clarify=[
                "Confirm whether any tangible movable property was taken without consent.",
                "Confirm whether any physical force, violence, bodily harm, or threat was employed.",
                "Confirm whether distinct financial fraud, cheating, criminal breach of trust, or electronic record forgery occurred."
            ]
        )

        model_suffix = "(Deterministic Fallback - LLM Inactive)" if not self.llm_client.is_available else "(Non-Penal Grievance Filter)"

        return OffenceClassificationResponse(
            predictions=[],
            recommended_action=action,
            model=f"BM25 Statutory Retrieval Engine {model_suffix}",
            standardized_narrative=standard_narrative,
            translations=translations,
            facts_analysis=facts_block,
            unverified_exclusions=self.corpus.excluded_sections,
            inference_status="non_penal_gate"
        )

    def analyze_complaint(self, data: NarrativeInput) -> OffenceClassificationResponse:
        """Complete pipeline: Translation -> BM25 Retrieval -> LLM / Fallback -> Verified Contract."""
        raw_narrative = (data.narrative or "").strip()

        # Handle empty or trivial inputs
        if len(raw_narrative) < 5:
            return OffenceClassificationResponse(
                predictions=[],
                recommended_action="Narrative too brief. Please describe the incident in greater detail.",
                model="N/A",
                standardized_narrative=raw_narrative,
                translations=[],
                facts_analysis=FactExtractionBlock(),
                unverified_exclusions=self.corpus.excluded_sections,
                inference_status="input_too_brief"
            )

        # Handle input length cap to prevent DoS / buffer issues
        if len(raw_narrative) > 8000:
            raw_narrative = raw_narrative[:8000]

        # Step 1: Synonym translation
        standard_narrative, translations = self.translate_synonyms(raw_narrative)

        # Step 2: Non-penal / Metaphorical grievance gate
        non_penal_match = self._detect_non_penal_grievance(raw_narrative)
        if non_penal_match:
            grievance_type, matched_snippet = non_penal_match
            return self._build_non_penal_response(
                raw_narrative=raw_narrative,
                standard_narrative=standard_narrative,
                translations=translations,
                grievance_type=grievance_type,
                matched_snippet=matched_snippet
            )

        # Step 3: Dynamic BM25 candidate retrieval with clause-level multi-action awareness
        retrieved_candidates = self.retriever.retrieve_clause_level(
            standard_narrative,
            min_raw_score=0.0,
            relative_threshold=0.35,
            max_k=8
        )
        retrieved_sec_nums = [snum for snum, _ in retrieved_candidates]
        retrieval_score_map = {snum: score for snum, score in retrieved_candidates}

        negations = self.detect_negations(raw_narrative)

        # Step 4: Attempt LLM reasoning if available
        if not self.llm_client.is_available:
            fallback_status = "fallback_llm_unavailable"
        elif not retrieved_sec_nums:
            fallback_status = "fallback_llm_not_invoked"
        else:
            fallback_status = "fallback_llm_failed"
            try:
                context_str = self.corpus.format_for_llm_context(retrieved_sec_nums)
                llm_output = self.llm_client.evaluate_complaint(raw_narrative, context_str)
                return self._build_llm_response(
                    raw_narrative=raw_narrative,
                    standard_narrative=standard_narrative,
                    translations=translations,
                    retrieval_score_map=retrieval_score_map,
                    llm_output=llm_output,
                    negations=negations
                )
            except LLMUnavailableError as e:
                fallback_status = "fallback_llm_unavailable"
                logger.warning("LLM unavailable, switching to transparent BM25 fallback: %s", str(e))
            except LLMInferenceError as e:
                logger.warning("LLM evaluation failed, switching to transparent BM25 fallback: %s", str(e))
            except Exception as e:
                logger.warning("Unexpected error during LLM response processing, switching to transparent BM25 fallback: %s", str(e))

        # Step 5: Transparent Rule-based BM25 Fallback (when no LLM key or LLM error)
        return self._build_fallback_response(
            raw_narrative=raw_narrative,
            standard_narrative=standard_narrative,
            translations=translations,
            retrieved_candidates=retrieved_candidates,
            negations=negations,
            fallback_status=fallback_status
        )

    def _build_llm_response(
        self,
        raw_narrative: str,
        standard_narrative: str,
        translations: List[Dict[str, str]],
        retrieval_score_map: Dict[int, float],
        llm_output: Dict[str, Any],
        negations: List[str]
    ) -> OffenceClassificationResponse:
        """Parses, verifies, validates statutory elements, and packages Gemini LLM structured output."""
        stated_facts = llm_output.get("stated_facts", [])
        if not isinstance(stated_facts, list):
            stated_facts = []
        inferred_facts = llm_output.get("inferred_facts", [])
        if not isinstance(inferred_facts, list):
            inferred_facts = []
        raw_negations = llm_output.get("negated_events", [])
        if not isinstance(raw_negations, list):
            raw_negations = []
        llm_negations = list(set(raw_negations + negations))
        missing_facts = llm_output.get("missing_facts_to_clarify", [])
        if not isinstance(missing_facts, list):
            missing_facts = []
        raw_action = llm_output.get("recommended_action", "")
        if not isinstance(raw_action, str):
            raw_action = str(raw_action or "")

        predictions: List[SectionPredictionItem] = []
        raw_evaluations = llm_output.get("candidate_evaluations", [])
        if not isinstance(raw_evaluations, list):
            raw_evaluations = []

        candidate_sec_nums = []

        for item in raw_evaluations:
            if not isinstance(item, dict):
                continue
            try:
                sec_num = int(item.get("section", 0))
            except (ValueError, TypeError):
                continue

            # Verify section exists in verified local BNS corpus
            sec_data = self.corpus.get_section(sec_num)
            if not sec_data:
                # REJECT fabricated or hallucinated section numbers
                logger.warning("Rejected unverified/hallucinated section cited by LLM: %s", sec_num)
                continue

            candidate_sec_nums.append(sec_num)

            rag_score = retrieval_score_map.get(sec_num, 0.0)
            explicit_score = self._parse_explicit_score(item.get("applicability_score"))
            is_explicit_score = explicit_score is not None
            if is_explicit_score:
                raw_app_score = explicit_score
            else:
                if "applicability_score" in item:
                    logger.warning("Ignoring non-numeric applicability_score for section %s; treating as missing.", sec_num)
                raw_app_score = rag_score if rag_score > 0 else 0.5

            reasoning = item.get("reasoning", "")
            if not reasoning:
                reasoning = f"Evaluated under BNS Section {sec_num} ({sec_data['title']})."

            supported_elements = item.get("statutory_elements_supported", [])
            if not isinstance(supported_elements, list):
                supported_elements = []

            unestablished_elements = item.get("unestablished_elements", [])
            if not isinstance(unestablished_elements, list):
                unestablished_elements = []

            # ── Run Statutory Element & Contradiction Validation ──
            validated_app_score, final_score, reasoning, supported_elements, unestablished_elements = (
                self._validate_candidate_elements(
                    sec_num=sec_num,
                    sec_data=sec_data,
                    app_score=raw_app_score,
                    rag_score=rag_score,
                    reasoning=reasoning,
                    supported_elements=supported_elements,
                    unestablished_elements=unestablished_elements,
                    negations=llm_negations,
                    raw_narrative=raw_narrative,
                    is_explicit_score=is_explicit_score
                )
            )

            # Do not present contradicted or non-applicable sections as viable candidates
            if final_score <= 0.0:
                logger.info("Excluded or zeroed section %s due to statutory contradiction or 0 applicability.", sec_num)
                continue

            is_cog, is_bail = self._determine_schedule_metadata(sec_num, sec_data, raw_narrative)

            predictions.append(SectionPredictionItem(
                section=sec_num,
                title=sec_data["title"],
                chapter=sec_data["chapter"],
                score=final_score,
                rag_score=rag_score,
                lr_prob=round(validated_app_score, 4),
                reasoning=reasoning,
                punishment=sec_data.get("punishment", ""),
                statutory_elements_supported=supported_elements,
                unestablished_elements=unestablished_elements,
                source_citation=sec_data.get("source", "Bharatiya Nyaya Sanhita, 2023"),
                is_cognizable=is_cog,
                is_bailable=is_bail
            ))

        # Sort descending by score
        predictions.sort(key=lambda x: x.score, reverse=True)
        predictions = predictions[:8]

        # Enrich facts block (separation of facts vs inferences, missing statutory items)
        facts_block = self._enrich_facts_block(
            stated_facts=stated_facts,
            inferred_facts=inferred_facts,
            negations=llm_negations,
            missing_facts=missing_facts,
            candidate_sections=candidate_sec_nums,
            raw_narrative=raw_narrative
        )

        # Audit and qualify procedural recommendations under BNSS, 2023
        recommended_action = self._audit_and_qualify_procedural_recommendation(
            predictions=predictions,
            facts_block=facts_block,
            raw_narrative=raw_narrative,
            raw_action=raw_action
        )

        model_name = getattr(self.llm_client, "model_name", None) or "unspecified model"
        return OffenceClassificationResponse(
            predictions=predictions,
            recommended_action=recommended_action,
            model=f"Gemini LLM + BM25 Grounded RAG ({model_name})",
            standardized_narrative=standard_narrative,
            translations=translations,
            facts_analysis=facts_block,
            unverified_exclusions=self.corpus.excluded_sections,
            inference_status="live_llm"
        )

    def _build_fallback_response(
        self,
        raw_narrative: str,
        standard_narrative: str,
        translations: List[Dict[str, str]],
        retrieved_candidates: List[Tuple[int, float]],
        negations: List[str],
        fallback_status: str = "fallback_llm_unavailable"
    ) -> OffenceClassificationResponse:
        """Deterministic, transparent BM25 fallback when the LLM is unavailable, failed, or not invoked."""
        predictions: List[SectionPredictionItem] = []
        words_in_narrative = set(re.findall(r'\b[a-zA-Z]{3,}\b', standard_narrative.lower()))

        candidate_sec_nums = []

        for sec_num, norm_score in retrieved_candidates:
            sec_data = self.corpus.get_section(sec_num)
            if not sec_data:
                continue

            candidate_sec_nums.append(sec_num)
            sec_keywords = set(k.lower() for k in sec_data.get("keywords", []))
            overlap = words_in_narrative & sec_keywords
            # Require at least one verified keyword overlap in fallback mode
            if not overlap:
                continue

            reasoning = (
                f"Section {sec_data['section']} of BNS, 2023 deals with \"{sec_data['title']}\" "
                f"under {sec_data.get('chapter', 'the relevant chapter')}."
            )
            if overlap:
                reasoning += f" Matched keywords: [{', '.join(sorted(overlap))}]."
            if sec_data.get("text"):
                first_sent = sec_data["text"].split(".")[0].strip() + "."
                reasoning += f" Statutory scope: \"{first_sent[:180]}\""

            supported = list(overlap)
            unestablished = ["Requires human officer inquiry to verify specific intent and evidentiary elements."]

            # Validate elements against negations in fallback mode as well
            validated_app, final_score, reasoning, supported, unestablished = (
                self._validate_candidate_elements(
                    sec_num=sec_num,
                    sec_data=sec_data,
                    app_score=norm_score,
                    rag_score=norm_score,
                    reasoning=reasoning,
                    supported_elements=supported,
                    unestablished_elements=unestablished,
                    negations=negations,
                    raw_narrative=raw_narrative,
                    is_explicit_score=False
                )
            )

            if final_score <= 0.0:
                continue

            is_cog, is_bail = self._determine_schedule_metadata(sec_num, sec_data, raw_narrative)

            predictions.append(SectionPredictionItem(
                section=sec_num,
                title=sec_data["title"],
                chapter=sec_data["chapter"],
                score=final_score,
                rag_score=norm_score,
                lr_prob=0.0,
                reasoning=reasoning,
                punishment=sec_data.get("punishment", ""),
                statutory_elements_supported=supported,
                unestablished_elements=unestablished,
                source_citation=sec_data.get("source", "Bharatiya Nyaya Sanhita, 2023"),
                is_cognizable=is_cog,
                is_bailable=is_bail
            ))

        # Sort descending by score
        predictions.sort(key=lambda x: x.score, reverse=True)

        stated_facts = [s.strip() for s in raw_narrative.split(".") if len(s.strip()) > 8][:4]

        facts_block = self._enrich_facts_block(
            stated_facts=stated_facts,
            inferred_facts=[],
            negations=negations,
            missing_facts=[
                "Confirm whether any weapon or bodily force was employed.",
                "Verify specific time, location, and property identifiers."
            ],
            candidate_sections=candidate_sec_nums,
            raw_narrative=raw_narrative
        )

        recommended_action = self._audit_and_qualify_procedural_recommendation(
            predictions=predictions,
            facts_block=facts_block,
            raw_narrative=raw_narrative,
            raw_action=""
        )

        return OffenceClassificationResponse(
            predictions=predictions,
            recommended_action=recommended_action,
            model=f"BM25 Statutory Retrieval Engine (Deterministic Fallback - {FALLBACK_STATUS_LABELS[fallback_status]})",
            standardized_narrative=standard_narrative,
            translations=translations,
            facts_analysis=facts_block,
            unverified_exclusions=self.corpus.excluded_sections,
            inference_status=fallback_status
        )
