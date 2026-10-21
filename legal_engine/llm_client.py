"""
LLM Client integration for Google Gemini using google-genai SDK.
Handles prompt construction, structured output enforcement, authentication,
and robust error handling.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("legal_engine.llm_client")


class LLMUnavailableError(Exception):
    """Raised when LLM API credentials are not configured or client cannot initialize."""
    pass


class LLMInferenceError(Exception):
    """Raised when LLM inference fails due to timeout, rate-limiting, or invalid format."""
    pass


SYSTEM_PROMPT = """You are an expert legal assistant specialized in the criminal statutory law of India under the Bharatiya Nyaya Sanhita (BNS), 2023 and procedural law under the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023.

Your primary duty is to analyze a citizen's complaint narrative objectively and evaluate it against the retrieved BNS statutory provisions provided in the context.

STRICT CONSTRAINTS:
1. NEVER invent, fabricate, or hallucinate BNS section numbers. Only evaluate candidate provisions explicitly provided in the retrieved context.
2. NEVER cite repealed Indian Penal Code (IPC) sections. Only reference the BNS, 2023.
3. STRICT FACTUAL SEPARATION:
   - stated_facts: ONLY physical acts, events, and observations explicitly narrated by the complainant. NEVER categorize unobserved mental state (mens rea) or unobserved suspect identity as a stated fact.
   - inferred_facts: Plausible inferences, including criminal intention (animus furandi / dishonest intention inferred from non-consensual taking), motive, or implicit connections.
   - negated_events: Statements explicitly stating that an event, weapon, injury, force, or consequence did NOT occur (e.g. 'no weapons used', 'nobody hurt', 'no physical violence').
   - missing_facts_to_clarify: Critical statutory elements missing from the narrative, specifically:
     * Monetary value of stolen/damaged property.
     * Identity and prior criminal history/conviction record of the accused.
     * Recovery/restoration status of property.
     * Specific force, restraint, or weapons.
4. ELEMENT VALIDATION & APPLICABILITY SCORING:
   - An offence can only be assigned positive applicability_score if its essential statutory elements are supported by stated or plausibly inferred facts.
   - If an essential statutory ingredient is contradicted or explicitly negated by narrative facts, its applicability_score MUST BE 0.0, and the contradicted element must be listed in unestablished_elements.
   - For Robbery (BNS Section 309): Robbery requires theft/extortion accompanied by voluntarily causing or threatening death, hurt, wrongful restraint, or instant fear thereof. If hurt, violence, weapons, or threats are absent or explicitly negated, Section 309 DOES NOT APPLY (applicability_score: 0.0).
   - For Theft (BNS Section 303) vs Dishonest Misappropriation (BNS Section 314): In theft, the initial taking is trespassory and non-consensual from another's possession. Dishonest misappropriation requires property to come into possession non-trespassorily (e.g. found property) and subsequently converted. If property was taken directly from a pocket/bag without consent, Section 303 is the primary provision; Section 314 is only an alternative if initial possession was not theft.
   - For Attempt vs Completed Offence: If the property was not actually taken into the offender's possession (e.g. attempt interrupted), the offence is an attempt under BNS Section 62 read with the relevant substantive section.
5. PROCEDURAL RECOMMENDATIONS (BNSS, 2023):
   - DO NOT generate unconditional recommendations to register an FIR under Section 173(1) BNSS when facts determining cognizability are unverified.
   - SECTION 173(3) BNSS PRELIMINARY ENQUIRY STRICT STATUTORY BOUNDARIES:
     * Applies ONLY to cognizable offences punishable for three years or more but less than seven years.
     * It is discretionary with prior permission from an officer not below the rank of Deputy Superintendent of Police (DSP) within 14 days, or police proceed directly with investigation when a prima facie case exists.
     * NEVER recommend Section 173(3) for vague or ambiguous complaints where no penal offence is established; request factual clarification from the complainant instead.
     * NEVER recommend Section 173(3) for non-cognizable offences (which fall under Section 174 BNSS).
     * NEVER recommend Section 173(3) for offences punishable with less than 3 years (e.g. Hurt Sec 115, Mischief Sec 324, Criminal Intimidation Sec 351).
     * NEVER recommend Section 173(3) for offences punishable with 7 years or more (such as Robbery Sec 309, Murder Sec 103, Dacoity Sec 310, Rape Sec 64), where information is recorded under Section 173(1) BNSS for direct FIR registration.
     * NEVER blindly repeat procedural assertions or Section 173(3) demands found in complainant narratives.
   - For Theft under BNS Section 303: If property value is unstated, explicitly qualify that procedure depends on missing facts:
     * If property value is ₹5,000 or more, or repeat offender: Cognizable and non-bailable under BNSS Schedule I (information recorded under Section 173(1) BNSS for FIR registration).
     * If property value is under ₹5,000, first-time offender, and property restored/returned: Section 303(2) proviso applies (punishable with community service; classified as non-cognizable and bailable under BNSS Schedule I, requiring procedure under Section 174 BNSS).
   - If the sole offence is non-cognizable (e.g. Section 314 alone): Non-cognizable entry under Section 174 BNSS (NCR) and reference to Magistrate.
   - Maintain a clear distinction between citizen reporting, preliminary police inquiry, and formal judicial determination.

OUTPUT FORMAT:
You MUST respond strictly with a valid JSON object matching this schema:
{
  "stated_facts": ["fact 1", "fact 2"],
  "negated_events": ["negation 1"],
  "inferred_facts": ["inference 1"],
  "missing_facts_to_clarify": ["clarification question 1", "clarification question 2"],
  "recommended_action": "Fact-qualified procedural guidance under BNSS, 2023",
  "candidate_evaluations": [
    {
      "section": 303,
      "applicability_score": 0.95,
      "reasoning": "Detailed statutory analysis explaining element satisfaction or legal distinction.",
      "statutory_elements_supported": ["element 1", "element 2"],
      "unestablished_elements": ["element requiring proof"]
    }
  ]
}
"""


class GeminiLegalClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        max_retries: int = 1,
        backoff_seconds: float = 1.5
    ):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        self.max_retries = max(0, max_retries)
        self.backoff_seconds = max(0.0, backoff_seconds)
        self._client: Optional[genai.Client] = None

        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error("Failed to initialize Google GenAI client: %s", type(e).__name__)
                self._client = None

    @property
    def is_available(self) -> bool:
        return self._client is not None

    def _is_transient_error(self, exc: Exception) -> bool:
        """Determines if an error is transient (503 Service Unavailable, 429 Rate Limit, Timeout)."""
        err_msg = str(exc).lower()
        err_type = type(exc).__name__.lower()
        
        # Check standard transient codes and types
        if isinstance(exc, (TimeoutError, ConnectionError)):
            return True
        if any(code in err_msg for code in ["503", "unavailable", "429", "resource_exhausted", "resourceexhausted", "deadline", "timeout"]):
            return True
        if any(code in err_type for code in ["timeout", "servererror", "connection"]):
            return True
        return False

    def evaluate_complaint(
        self,
        narrative: str,
        retrieved_context: str
    ) -> Dict[str, Any]:
        """
        Submits the narrative and retrieved context to Gemini and returns structured legal evaluation.
        Features bounded retry with exponential backoff on transient upstream errors (503, 429, timeout).
        Never logs API keys or sensitive authorization material.
        """
        if not self.is_available:
            raise LLMUnavailableError("Google Gemini API key not configured or client unavailable.")

        user_content = (
            f"=== COMPLAINT NARRATIVE ===\n{narrative}\n\n"
            f"=== RETRIEVED BNS STATUTORY PROVISIONS ===\n{retrieved_context}\n\n"
            f"Please analyze the complaint against the retrieved provisions following all system constraints. Output strictly valid JSON."
        )

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1,
            response_mime_type="application/json"
        )

        attempts = 0
        total_attempts = 1 + self.max_retries

        while attempts < total_attempts:
            attempts += 1
            try:
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=user_content,
                    config=config
                )
                raw_text = response.text if response else None
                if not raw_text or not raw_text.strip():
                    raise LLMInferenceError("Empty model response received from Gemini.")

                result_json = json.loads(raw_text)
                if not isinstance(result_json, dict):
                    raise LLMInferenceError(f"Malformed LLM JSON output: expected JSON object (dict), got {type(result_json).__name__}")
                return result_json

            except (LLMUnavailableError, LLMInferenceError):
                raise
            except json.JSONDecodeError as jde:
                logger.error("Gemini returned invalid JSON: %s", str(jde))
                raise LLMInferenceError(f"Malformed LLM JSON output: {str(jde)}") from jde
            except Exception as e:
                is_transient = self._is_transient_error(e)
                if is_transient and attempts < total_attempts:
                    delay = self.backoff_seconds * (attempts)
                    logger.warning(
                        "Gemini API transient failure (%s: %s). Bounded retry attempt %d/%d in %.1fs...",
                        type(e).__name__,
                        str(e)[:120],
                        attempts,
                        self.max_retries,
                        delay
                    )
                    import time
                    time.sleep(delay)
                    continue

                logger.error("Gemini API error during legal evaluation: %s", type(e).__name__)
                raise LLMInferenceError(f"Gemini API failure: {str(e)}") from e

