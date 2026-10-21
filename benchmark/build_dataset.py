"""
Benchmark Dataset Generator for Bharatiya Nyaya Sanhita (BNS), 2023.
Creates a controlled, version-controlled 50-case benchmark covering diverse fictional complaints
across English, Hindi, and Hinglish with authoritative reference labels and statutory rationales.
"""

import json
import os
from typing import List, Dict, Any

BENCHMARK_CASES: List[Dict[str, Any]] = [
    # ── CATEGORY 1: DIRECT THEFT (CASES 01-05) ──
    {
        "case_id": "BNS-BM-01",
        "category": "direct_theft",
        "language": "English",
        "narrative": (
            "Yesterday evening around 7 PM, while I was waiting for train at Dadar platform 3, "
            "someone took my leather wallet from my rear trousers pocket without my consent or knowledge. "
            "The wallet contained Rs 4,500 in cash and my PAN card."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Movable property (leather wallet, cash, PAN card)",
            "Taken out of complainant's possession without consent",
            "Dishonest moving in order to taking"
        ],
        "unestablished_elements": [
            "Identity of the perpetrator",
            "Prior conviction record of the perpetrator"
        ],
        "contradicted_elements": [
            "Voluntarily causing hurt, death, or wrongful restraint",
            "Fear of instant hurt or restraint",
            "Display or use of weapons"
        ],
        "material_missing_facts": [
            "Whether the perpetrator has prior convictions under Section 303",
            "Whether the stolen property will be returned/restored"
        ],
        "expected_uncertainty": (
            "Procedural route is conditional under Section 303(2) proviso because property value is Rs 4,500 (< Rs 5,000). "
            "If first-time offender and restored, punishment is community service (non-cognizable / bailable under BNSS Schedule I); "
            "otherwise cognizable and non-bailable."
        ),
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "Constitutes theft under Section 303(1) BNS. Section 309 Robbery is contradicted because no confrontation, "
            "restraint, violence, or threat occurred. BNSS Schedule I procedural status is conditional on accused's prior record "
            "and property restoration under the Section 303(2) proviso."
        ),
        "source_reference": "BNS, 2023 Sec 303; BNSS, 2023 First Schedule Part I (Entry for Section 303)",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-02",
        "category": "direct_theft",
        "language": "English",
        "narrative": (
            "I parked my bicycle worth Rs 12,000 outside Bandra station west with a wire lock. "
            "When I returned an hour later, the lock was cut and the bicycle was missing. No one confronted me."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Movable property (bicycle valued at Rs 12,000)",
            "Moved out of owner's possession without consent by cutting wire lock"
        ],
        "unestablished_elements": ["Identity of suspect"],
        "contradicted_elements": ["Confrontation, hurt, weapons, threat of harm"],
        "material_missing_facts": ["Suspect identity", "CCTV footage availability"],
        "expected_uncertainty": "Offence is clear; investigative certainty on suspect identity required.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Stolen property exceeds ₹5,000 threshold, placing it squarely under general theft (Section 303(2) BNS). "
            "Classified as Cognizable and Non-bailable under BNSS Schedule I Part I. Recorded under Section 173 BNSS."
        ),
        "source_reference": "BNS, 2023 Sec 303(2); BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-03",
        "category": "direct_theft",
        "language": "Hindi",
        "narrative": (
            "कल दोपहर को जब मैं बांद्रा लोकल ट्रेन में चढ़ा, तब किसी ने मेरी जेब से मेरा वीवो मोबाइल फोन चुपके से निकाल लिया। "
            "मुझे कोई चोट नहीं लगी और न ही किसी ने कोई धमकी दी। फोन की कीमत लगभग 15,000 रुपये है।"
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "चल संपत्ति (15,000 रुपये मूल्य का वीवो मोबाइल फोन)",
            "सहमति के बिना जेब से बेईमानी से निकालना"
        ],
        "unestablished_elements": ["आरोपी की पहचान"],
        "contradicted_elements": ["चोट, धमकी, हथियार या हिंसा (धारा 309 लूट का पूर्ण खंडन)"],
        "material_missing_facts": ["संदिग्ध व्यक्ति की पहचान"],
        "expected_uncertainty": "अपराध स्पष्ट है; धारा 303(2) बीएनएस के तहत संज्ञेय।",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "बीएनएस धारा 303(2) के तहत चोरी का अपराध। मूल्य 5,000 रुपये से अधिक है, अतः बीएनएसएस अनुसूची I के अनुसार "
            "यह संज्ञेय (Cognizable) और गैर-जमानती (Non-bailable) है।"
        ),
        "source_reference": "BNS, 2023 Sec 303(2); BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-04",
        "category": "direct_theft",
        "language": "Hinglish",
        "narrative": (
            "Mera laptop bag office desk se chori ho gaya jab main lunch ke liye gaya tha. "
            "Bag mein laptop tha worth 65000 rupees. Koi ladai ya confrontation nahi hui, bas chupke se utha ke le gaya koi."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Movable property (laptop worth Rs 65,000)",
            "Taken dishonestly from desk without consent"
        ],
        "unestablished_elements": ["Accused identity"],
        "contradicted_elements": ["Ladai, confrontation, force, hurt (Robbery contradicted)"],
        "material_missing_facts": ["CCTV footage of office area"],
        "expected_uncertainty": "Offence established; suspect unknown.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Theft under BNS Section 303(2). Property value > Rs 5,000 establishes cognizable, non-bailable classification under BNSS Schedule I."
        ),
        "source_reference": "BNS, 2023 Sec 303(2); BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-05",
        "category": "direct_theft",
        "language": "English",
        "narrative": (
            "A stranger stealthily removed an unstitched silk saree bundle from my shop counter in Crawford Market "
            "while I was attending another customer. Total value is Rs 3,200. No threats or force were used."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Movable property (saree bundle valued at Rs 3,200)",
            "Moved without owner's consent"
        ],
        "unestablished_elements": ["Identity and criminal history of suspect"],
        "contradicted_elements": ["Threats, force, hurt, weapons"],
        "material_missing_facts": [
            "Whether suspect has prior conviction under Section 303",
            "Whether property will be restored upon apprehension"
        ],
        "expected_uncertainty": (
            "Value < Rs 5,000 makes procedural classification conditional under Section 303(2) proviso."
        ),
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "Theft under Section 303(1). Section 309 Robbery is contradicted. Schedule I status is conditional (None) pending "
            "factual verification of prior convictions and property restoration."
        ),
        "source_reference": "BNS, 2023 Sec 303; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },

    # ── CATEGORY 2: FOUND PROPERTY CONVERTED (CASES 06-09) ──
    {
        "case_id": "BNS-BM-06",
        "category": "found_property",
        "language": "English",
        "narrative": (
            "I lost my gold ring inscribed with my initials 'RK' on Linking Road. The next day, a local fruit vendor told me "
            "he found the ring on the road, saw my inscription, but immediately took it to a jeweler and sold it for cash instead of returning it."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [314],
        "plausible_alternatives": [303],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Property found on public road (came into possession non-trespassorily)",
            "Finder knew means of discovering owner ('RK' initials)",
            "Dishonest misappropriation / conversion to own use by selling to jeweler"
        ],
        "unestablished_elements": ["Direct trespassory taking from complainant's body/pocket"],
        "contradicted_elements": ["Force, restraint, hurt, confrontation"],
        "material_missing_facts": ["Jeweler's receipt / confirmation of sale"],
        "expected_uncertainty": (
            "Must be distinguished from direct theft (Section 303). Governed by Section 314 Explanation 2."
        ),
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": False,
        "expected_bailable": True,
        "legal_rationale": (
            "Dishonest misappropriation of property under BNS Section 314. Under Section 314 Explanation 2, a finder who converts "
            "property knowing the owner commits criminal misappropriation, not theft. Under BNSS Schedule I Part I, Section 314 is "
            "NON-COGNIZABLE and BAILABLE (procedure under Section 174 BNSS)."
        ),
        "source_reference": "BNS, 2023 Sec 314; BNSS, 2023 First Schedule Part I (Entry for Section 314)",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-07",
        "category": "found_property",
        "language": "Hindi",
        "narrative": (
            "सड़क पर गिरा हुआ एक पर्स मिला जिसमें मालिक का आधार कार्ड और 5000 रुपये थे। "
            "उस व्यक्ति ने आधार कार्ड देखकर भी मालिक को नहीं लौटाया और सारे पैसे अपने निजी खर्च में उड़ा दिए।"
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [314],
        "plausible_alternatives": [303],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "सड़क पर मिली संपत्ति (बिना चोरी के कब्जे में आना)",
            "मालिक की पहचान का ज्ञान (आधार कार्ड)",
            "बेईमानी से निजी उपयोग में संपत्ति का संपरिवर्तन (Conversion)"
        ],
        "unestablished_elements": ["चोरी के माध्यम से कब्जा लेना"],
        "contradicted_elements": ["बल, हिंसा या धमकी"],
        "material_missing_facts": ["खर्च किए गए पैसों की बरामदगी"],
        "expected_uncertainty": "सीधी चोरी (धारा 303) के बजाय आपराधिक दुर्विनियोग (धारा 314)।",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": False,
        "expected_bailable": True,
        "legal_rationale": (
            "बीएनएस धारा 314 (संपत्ति का बेईमानी से दुर्विनियोग)। बीएनएसएस अनुसूची I के अनुसार यह अपराध "
            "असंज्ञेय (Non-cognizable) और जमानती (Bailable) है। पुलिस धारा 174 बीएनएसएस के तहत एनसीआर दर्ज करेगी।"
        ),
        "source_reference": "BNS, 2023 Sec 314; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-08",
        "category": "found_property",
        "language": "Hinglish",
        "narrative": (
            "Ek courier delivery boy ka parcel bag road pe gir gaya tha. Auto driver ne bag uthaya, parcel khole aur branded sports shoes "
            "apne paas rakh liye aur baki saman fek diya. Koi theft direct nahi thi, sadak pe gira hua mila tha."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [314],
        "plausible_alternatives": [303],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Lost property picked from road",
            "Dishonest appropriation to own use"
        ],
        "unestablished_elements": ["Original taking from person's possession"],
        "contradicted_elements": ["Force, violence, threat"],
        "material_missing_facts": ["Value of shoes and courier records"],
        "expected_uncertainty": "Offence is misappropriation under Section 314, non-cognizable under BNSS.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": False,
        "expected_bailable": True,
        "legal_rationale": (
            "BNS Section 314 applies to dishonest misappropriation of found property. Non-cognizable and Bailable under BNSS Schedule I."
        ),
        "source_reference": "BNS, 2023 Sec 314; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-09",
        "category": "found_property",
        "language": "English",
        "narrative": (
            "A suitcase was left unattended on a bench at Marine Drive promenade. An unidentified man picked up the suitcase, "
            "waited around for five minutes, and then walked away with it. We do not know if he intended to find the owner or convert it."
        ),
        "classification_type": "B",
        "relevant_candidate_sections": [314],
        "plausible_alternatives": [303],
        "contradicted_sections": [309],
        "explicitly_supported_elements": ["Movable property picked from public bench"],
        "unestablished_elements": [
            "Dishonest intention at the time of taking",
            "Subsequent conversion or attempt to discover owner"
        ],
        "contradicted_elements": ["Violence, confrontation, robbery"],
        "material_missing_facts": [
            "Whether the finder made reasonable efforts to trace the owner",
            "Whether the contents were appropriated or handed to police"
        ],
        "expected_uncertainty": (
            "Cannot definitively classify until subsequent conduct establishes whether conversion was dishonest (Section 314) or innocent finder."
        ),
        "expected_attempt": False,
        "verified_schedule_applicable": False,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "Under Section 314 Explanation 2, merely taking lost property into custody is not an offence; "
            "dishonest misappropriation only occurs upon subsequent conversion without reasonable attempt to find owner."
        ),
        "source_reference": "BNS, 2023 Sec 314 Explanation 2",
        "review_status": "verified_authoritative"
    },

    # ── CATEGORY 3: SNATCHING (CASES 10-13) ──
    {
        "case_id": "BNS-BM-10",
        "category": "snatching",
        "language": "English",
        "narrative": (
            "While I was walking along Juhu Tara Road, two men on a black motorcycle suddenly drove past from behind "
            "and forcibly snatched my gold chain from around my neck before speeding away. I did not fall and was not injured."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [304],
        "plausible_alternatives": [303],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Sudden, quick or forcible seizure of movable property from person (BNS Section 304)",
            "Taking away from possession on motorcycle"
        ],
        "unestablished_elements": ["Accused identity"],
        "contradicted_elements": [
            "Voluntarily causing hurt or fear of instant death/hurt/restraint (Robbery Section 309)"
        ],
        "material_missing_facts": ["Vehicle registration number", "Chain weight and value"],
        "expected_uncertainty": "Snatching is specifically defined under Section 304 BNS; does not escalate to Robbery since no hurt was caused.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "BNS Section 304 creates an independent offence for Snatching (sudden, quick or forcible seizure). "
            "Classified as COGNIZABLE and NON-BAILABLE under BNSS Schedule I Part I."
        ),
        "source_reference": "BNS, 2023 Sec 304; BNSS, 2023 First Schedule Part I (Entry for Section 304)",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-11",
        "category": "snatching",
        "language": "Hindi",
        "narrative": (
            "जब मैं अंधेरी ईस्ट में पैदल चल रही थी, तभी पीछे से एक बाइक सवार तेजी से आया और मेरे हाथ से झपट्टा मारकर मेरा पर्स छीनकर भाग गया।"
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [304],
        "plausible_alternatives": [303],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "अचानक या तेजी से झपट्टा मारकर संपत्ति छीनना (धारा 304 झपटमारी)"
        ],
        "unestablished_elements": ["आरोपी का विवरण"],
        "contradicted_elements": ["चोट पहुंचाना या जान से मारने की धमकी"],
        "material_missing_facts": ["पर्स में मौजूद नकदी और सामान का मूल्य"],
        "expected_uncertainty": "धारा 304 बीएनएस के तहत झपटमारी।",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "बीएनएस धारा 304 के तहत झपटमारी (Snatching)। बीएनएसएस अनुसूची I के अनुसार संज्ञेय (Cognizable) और गैर-जमानती (Non-bailable)।"
        ),
        "source_reference": "BNS, 2023 Sec 304; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-12",
        "category": "snatching",
        "language": "Hinglish",
        "narrative": (
            "Main footpath pe chal raha tha phone pe baat karte hue. Ek ladka achanak daudte hue aaya aur mere haath se phone snatch karke galli mein bhaag gaya. "
            "Maine pakadne ki koshish ki par wo tezi se nikal gaya."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [304],
        "plausible_alternatives": [303],
        "contradicted_sections": [309],
        "explicitly_supported_elements": ["Quick or sudden seizure of phone from victim's hand"],
        "unestablished_elements": ["Identity of runner"],
        "contradicted_elements": ["Weapons, injury, intimidation"],
        "material_missing_facts": ["IMEI number of phone"],
        "expected_uncertainty": "Snatching under Section 304 BNS.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "BNS Section 304 specifically penalizes sudden or quick seizure of property from person. Cognizable and Non-bailable under BNSS Schedule I."
        ),
        "source_reference": "BNS, 2023 Sec 304; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-13",
        "category": "snatching",
        "language": "English",
        "narrative": (
            "A man grabbed my shopping bag while walking past me in a crowded bazaar. It was so fast that I do not know if he snatched it "
            "by quick seizure or if my grip slipped as he brushed past."
        ),
        "classification_type": "B",
        "relevant_candidate_sections": [304],
        "plausible_alternatives": [303],
        "contradicted_sections": [309],
        "explicitly_supported_elements": ["Bag taken in crowded market"],
        "unestablished_elements": ["Whether taking was sudden/forcible snatching (Sec 304) or stealth theft (Sec 303)"],
        "contradicted_elements": ["Weapons, hurt, threats"],
        "material_missing_facts": ["Eyewitness statements", "Contents of bag"],
        "expected_uncertainty": "Factual ambiguity between Snatching (Section 304) and Simple Theft (Section 303).",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Snatching requires affirmative sudden or forcible seizure; if taking was merely stealthy pickpocketing, Section 303 applies. "
            "Both are cognizable and non-bailable."
        ),
        "source_reference": "BNS, 2023 Sec 304, Sec 303",
        "review_status": "verified_authoritative"
    },

    # ── CATEGORY 4: ROBBERY STATUTORY CIRCUMSTANCES (CASES 14-19) ──
    {
        "case_id": "BNS-BM-14",
        "category": "robbery_statutory_circumstances",
        "language": "English",
        "narrative": (
            "Two men cornered me in an alley near Kurla station. One man pinned both my arms tightly against the brick wall, "
            "physically restraining me so I could not move, while the other reached into my pockets and took my wallet and watch. "
            "No weapons were produced and they did not hit me."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [309],
        "plausible_alternatives": [303],
        "contradicted_sections": [],
        "explicitly_supported_elements": [
            "Voluntary causing of wrongful restraint in order to the committing of theft (BNS Section 309)",
            "Theft of movable property (wallet and watch)"
        ],
        "unestablished_elements": ["Suspects' identities"],
        "contradicted_elements": ["Weapons used", "Actual physical blows or bodily injury caused"],
        "material_missing_facts": ["Value of wallet and watch"],
        "expected_uncertainty": (
            "Robbery is established despite absence of weapons or injury because wrongful restraint satisfies the statutory alternative of Section 309."
        ),
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Under BNS Section 309, theft is robbery if the offender for that end voluntarily causes or attempts to cause death, hurt, "
            "OR wrongful restraint. Physical pinning of arms constitutes wrongful restraint under Section 126 BNS, making the theft robbery. "
            "Absence of weapons or injuries does NOT negate Section 309. Cognizable and Non-bailable under BNSS Schedule I Part I."
        ),
        "source_reference": "BNS, 2023 Sec 309; BNSS, 2023 First Schedule Part I (Entry for Section 309)",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-15",
        "category": "robbery_statutory_circumstances",
        "language": "English",
        "narrative": (
            "A man blocked my path near Sion railway bridge, clenched his fist right in front of my face, and aggressively shouted: "
            "'Hand over your phone right now or I will smash your jaw and break your teeth.' Terrified of instant hurt, I surrendered my iPhone 14. "
            "No weapon was shown and he did not actually hit me."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [309],
        "plausible_alternatives": [303],
        "contradicted_sections": [],
        "explicitly_supported_elements": [
            "Voluntarily causing fear of instant hurt in order to committing theft (BNS Section 309)",
            "Extortion/theft of mobile phone under instant threat"
        ],
        "unestablished_elements": ["Suspect identity"],
        "contradicted_elements": ["Actual injury caused", "Display of weapon"],
        "material_missing_facts": ["Phone IMEI"],
        "expected_uncertainty": "Statutory condition of fear of instant hurt is established on narrative face.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Under BNS Section 309, putting the victim in fear of instant hurt satisfies the definition of robbery. "
            "Absence of a physical weapon or completed blow does not exclude robbery when the threat of instant violence is direct and immediate. "
            "Cognizable and Non-bailable under BNSS Schedule I."
        ),
        "source_reference": "BNS, 2023 Sec 309; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-16",
        "category": "robbery_statutory_circumstances",
        "language": "English",
        "narrative": (
            "While I was walking home in Chembur, a man grabbed my wrist to steal my gold bracelet. When I resisted, he punched me hard "
            "in the face, causing a bloody lip and severe bruising, and tore the bracelet off before running."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [309, 115],
        "plausible_alternatives": [],
        "contradicted_sections": [],
        "explicitly_supported_elements": [
            "Voluntarily causing hurt in committing theft (BNS Section 309 and Section 115)",
            "Theft of gold bracelet"
        ],
        "unestablished_elements": ["Perpetrator identity"],
        "contradicted_elements": [],
        "material_missing_facts": ["Medical MLC report", "Value of bracelet"],
        "expected_uncertainty": "Clear robbery accompanied by actual bodily hurt.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Theft accompanied by voluntarily causing hurt is robbery under BNS Section 309. Also attracts Section 115(2) (voluntarily causing hurt). "
            "Cognizable and Non-bailable under BNSS Schedule I."
        ),
        "source_reference": "BNS, 2023 Sec 309, Sec 115; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-17",
        "category": "robbery_statutory_circumstances",
        "language": "English",
        "narrative": (
            "Two masked men entered my chemist shop at midnight. One held a large knife against my throat and threatened to kill me "
            "if I screamed, while the other looted Rs 40,000 from the cash register."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [309, 310, 311],
        "plausible_alternatives": [],
        "contradicted_sections": [],
        "explicitly_supported_elements": [
            "Use of deadly weapon (knife) in committing robbery",
            "Fear of instant death voluntarily caused",
            "Theft of cash Rs 40,000"
        ],
        "unestablished_elements": ["Masked perpetrators' identities"],
        "contradicted_elements": [],
        "material_missing_facts": ["CCTV footage"],
        "expected_uncertainty": "Aggravated robbery with deadly weapon (Section 311 BNS).",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Robbery under Section 309 aggravated by attempt to cause death or grievous hurt with deadly weapon under Section 311 BNS. "
            "Cognizable and Non-bailable under BNSS Schedule I."
        ),
        "source_reference": "BNS, 2023 Sec 309, Sec 311; BNSS, 2023 First Schedule Part I",
        "review_status": "provisional_pending_legal_review",
        "label_review_notes": "Label lists Section 310 (dacoity), but BNS Section 310(1) requires five or more persons conjointly committing robbery; the narrative describes two offenders. Section 311 depends on whether holding a knife to the throat is 'uses any deadly weapon', which requires judicial interpretation.",
        "label_review": {'reviewed_on': '2026-10-20',
         'reviewer': 'Automated statutory cross-check against BNS text and BNSS First Schedule (not a qualified '
                     'legal review)',
         'sources': ['BNSS, 2023 First Schedule, Part I (Gazette of India Extraordinary, 25 Dec 2023)',
                     'BNS, 2023 section text as held in bns_rag_dataset.json'],
         'findings': ['Section 309 supported: theft accompanied by fear of instant death (knife to throat, threat to '
                      'kill).',
                      'Section 310 inconsistent with facts: BNS Section 310(1) requires five or more persons; two '
                      'are described.',
                      "Section 311 ('uses any deadly weapon') turns on case law on whether brandishing amounts to "
                      'use; not verified here.',
                      'Possible house-trespass or house-breaking depends on whether the shop was open at midnight; '
                      'not stated.',
                      'expected_cognizable=True / expected_bailable=False consistent with Sections 309(4) and 311 '
                      'rows.'],
         'proposed_label_corrections_not_applied': [{'field': 'relevant_candidate_sections',
                                                     'current': [309, 310, 311],
                                                     'proposed': [309, 311],
                                                     'basis': 'BNS Section 310(1): five or more persons.'},
                                                    {'field': 'contradicted_sections',
                                                     'current': [],
                                                     'proposed': [310],
                                                     'basis': 'BNS Section 310(1): five or more persons.'}],
         'resolution': 'unresolved_pending_qualified_legal_review'},
        "review_history": [{'date': '2026-10-20',
          'change': 'review_status: verified_authoritative -> provisional_pending_legal_review',
          'reason': 'Specific statutory label concerns identified in inspection round 2.'},
         {'date': '2026-10-20',
          'change': 'label_review record added; labels unchanged',
          'reason': 'Case-by-case review against statutory text in round 3.'}]
    },
    {
        "case_id": "BNS-BM-18",
        "category": "robbery_statutory_circumstances",
        "language": "Hindi",
        "narrative": (
            "रात को 10 बजे दो अज्ञात युवकों ने मुझे सुनसान गली में घेर लिया। एक ने मेरी दोनों बाहें पीछे से कसकर पकड़ लीं ताकि मैं हिल न सकूं "
            "और दूसरे ने मेरी जेब से 8000 रुपये निकाल लिए। उनके पास कोई हथियार नहीं था और न ही उन्होंने मुझे मारा।"
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [309],
        "plausible_alternatives": [303],
        "contradicted_sections": [],
        "explicitly_supported_elements": [
            "चोरी करने के उद्देश्य से सदोष अवरोध (Wrongful restraint) कारित करना (धारा 309 बीएनएस)"
        ],
        "unestablished_elements": ["आरोपियों की पहचान"],
        "contradicted_elements": ["हथियार का प्रयोग", "मारपीट या शारीरिक चोट"],
        "material_missing_facts": ["आरोपियों का हुलिया"],
        "expected_uncertainty": "बिना हथियार या चोट के भी सदोष अवरोध के कारण लूट का अपराध सिद्ध होता है।",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "बीएनएस धारा 309 के तहत चोरी लूट है यदि चोरी करने के लिए सदोष अवरोध कारित किया जाए। हथियार या चोट न होने पर भी "
            "सदोष अवरोध के कारण यह संज्ञेय और गैर-जमानती लूट (Robbery) है।"
        ),
        "source_reference": "BNS, 2023 Sec 309; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-19",
        "category": "robbery_statutory_circumstances",
        "language": "Hinglish",
        "narrative": (
            "Kal raat ko auto se utarte waqt driver aur uske dost ne mujhe gher liya. Ek bande ne collar pakad ke wall pe daba diya "
            "aur bola 'chupchaap purse nikaal warna jaan se maar dunga'. Darr ke maare maine purse de diya jisme 10000 cash tha."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [309],
        "plausible_alternatives": [303],
        "contradicted_sections": [],
        "explicitly_supported_elements": [
            "Wrongful restraint and putting in fear of instant death/harm to commit theft",
            "Theft of Rs 10,000 cash"
        ],
        "unestablished_elements": ["Auto registration number"],
        "contradicted_elements": [],
        "material_missing_facts": ["Auto rickshaw number"],
        "expected_uncertainty": "Robbery under BNS Section 309.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Restraint plus immediate threat of death satisfies Section 309 BNS robbery. Cognizable and Non-bailable under BNSS Schedule I."
        ),
        "source_reference": "BNS, 2023 Sec 309; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },

    # ── CATEGORY 5: ATTEMPTED OFFENCES (CASES 20-23) ──
    {
        "case_id": "BNS-BM-20",
        "category": "attempted_offence",
        "language": "English",
        "narrative": (
            "While boarding a crowded BEST bus at Churchgate, I felt someone's hand sliding inside my front coat pocket where my wallet was kept. "
            "I immediately grabbed the person's wrist before he could grasp or remove the wallet. The wallet never left my pocket."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [62, 303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Act done towards the commission of theft (hand inserted into pocket)",
            "Interrupted before moving or taking property"
        ],
        "unestablished_elements": ["Completed taking out of possession (completed theft negated)"],
        "contradicted_elements": ["Weapons, force, completed injury, robbery"],
        "material_missing_facts": ["Suspect identity"],
        "expected_uncertainty": (
            "Must be charged as attempt under Section 62 read with Section 303, not completed theft."
        ),
        "expected_attempt": True,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": True,
        "legal_rationale": (
            "Attempt to commit theft under BNS Section 62 read with Section 303. Under BNSS Schedule I Part I, attempt to commit an offence "
            "punishable with imprisonment is cognizable if the primary offence is cognizable, and bailable if the primary offence is bailable or as specified."
        ),
        "source_reference": "BNS, 2023 Sec 62, Sec 303; BNSS, 2023 First Schedule Part I",
        "review_status": "provisional_pending_legal_review",
        "label_review_notes": 'expected_bailable=True conflicts with the BNSS First Schedule entry for Section 62, under which bailability follows the offence attempted; theft under Section 303(2) is non-bailable. It would fit only if Section 134 (criminal force in attempting theft of property carried by a person; cognizable, bailable) were the intended offence, which is not labelled.',
        "label_review": {'reviewed_on': '2026-10-20',
         'reviewer': 'Automated statutory cross-check against BNS text and BNSS First Schedule (not a qualified '
                     'legal review)',
         'sources': ['BNSS, 2023 First Schedule, Part I (Gazette of India Extraordinary, 25 Dec 2023)',
                     'BNS, 2023 section text as held in bns_rag_dataset.json'],
         'findings': ['Sections 62 + 303 consistent with the facts (hand in pocket, wallet never removed).',
                      'Schedule I, Section 62: bailability follows the offence attempted; Section 303(2) main row is '
                      'non-bailable.',
                      'The Section 303(2) community-service row presupposes return or restoration of taken property '
                      'and a value under Rs 5,000; neither fits an attempt where nothing was taken and value is '
                      'unstated.',
                      "Section 134 (cognizable, bailable) may apply if inserting a hand into the complainant's "
                      'pocket is criminal force to the person; requires review.'],
         'proposed_label_corrections_not_applied': [{'field': 'expected_bailable',
                                                     'current': True,
                                                     'proposed': False,
                                                     'basis': 'Schedule I Section 62 row read with Section 303(2) '
                                                              'row (non-bailable).'},
                                                    {'field': 'plausible_alternatives',
                                                     'current': [],
                                                     'proposed': [134],
                                                     'basis': 'BNS Section 134; Schedule I row: cognizable, '
                                                              'bailable.'}],
         'resolution': 'unresolved_pending_qualified_legal_review'},
        "review_history": [{'date': '2026-10-20',
          'change': 'review_status: verified_authoritative -> provisional_pending_legal_review',
          'reason': 'Bailability label conflicts with labelled sections; unresolved in round 3.'},
         {'date': '2026-10-20',
          'change': 'label_review record added; labels unchanged',
          'reason': 'Case-by-case review against statutory text in round 3.'}]
    },
    {
        "case_id": "BNS-BM-21",
        "category": "attempted_offence",
        "language": "Hindi",
        "narrative": (
            "बाजार में एक चोर ने मेरी सोने की चेन खींचने का प्रयास किया, लेकिन चेन मेरे हाथ में आ गई और टूटी नहीं। "
            "लोगों के चिल्लाने पर वह बिना कुछ लिए भाग गया।"
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [62, 304],
        "plausible_alternatives": [303],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "झपटमारी का प्रयास (Attempt to commit snatching)"
        ],
        "unestablished_elements": ["संपत्ति का कब्जा छिनना (अपराध अपूर्ण रहा)"],
        "contradicted_elements": ["चोट लगना या जानलेवा हमला"],
        "material_missing_facts": ["भागने वाले व्यक्ति का विवरण"],
        "expected_uncertainty": "अपूर्ण अपराध: धारा 62 सहपठित धारा 304 बीएनएस।",
        "expected_attempt": True,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": True,
        "legal_rationale": (
            "बीएनएस धारा 62 सहपठित धारा 304 (झपटमारी का प्रयत्न)। चूंकि संपत्ति कब्जे से नहीं हटी, अतः पूर्ण अपराध नहीं बना।"
        ),
        "source_reference": "BNS, 2023 Sec 62, Sec 304; BNSS, 2023 First Schedule Part I",
        "review_status": "provisional_pending_legal_review",
        "label_review_notes": 'expected_bailable=True conflicts with the BNSS First Schedule entry for Section 62, under which bailability follows the offence attempted; snatching under Section 304(2) is non-bailable. Pulling a chain the complainant is wearing may also fall under Section 134 (cognizable, bailable), which is not labelled.',
        "label_review": {'reviewed_on': '2026-10-20',
         'reviewer': 'Automated statutory cross-check against BNS text and BNSS First Schedule (not a qualified '
                     'legal review)',
         'sources': ['BNSS, 2023 First Schedule, Part I (Gazette of India Extraordinary, 25 Dec 2023)',
                     'BNS, 2023 section text as held in bns_rag_dataset.json'],
         'findings': ['Sections 62 + 304 consistent with the facts (chain pulled, remained with complainant).',
                      'Schedule I, Section 62 row read with Section 304(2) row: cognizable, non-bailable.',
                      'Section 134 (criminal force in attempting theft of property worn by a person) is a strong '
                      'unlabelled candidate; cognizable, bailable.'],
         'proposed_label_corrections_not_applied': [{'field': 'expected_bailable',
                                                     'current': True,
                                                     'proposed': False,
                                                     'basis': 'Schedule I Section 62 row read with Section 304(2) '
                                                              'row (non-bailable).'},
                                                    {'field': 'plausible_alternatives',
                                                     'current': [303],
                                                     'proposed': [303, 134],
                                                     'basis': 'BNS Section 134.'}],
         'resolution': 'unresolved_pending_qualified_legal_review'},
        "review_history": [{'date': '2026-10-20',
          'change': 'review_status: verified_authoritative -> provisional_pending_legal_review',
          'reason': 'Bailability label conflicts with labelled sections; unresolved in round 3.'},
         {'date': '2026-10-20',
          'change': 'label_review record added; labels unchanged',
          'reason': 'Case-by-case review against statutory text in round 3.'}]
    },
    {
        "case_id": "BNS-BM-22",
        "category": "attempted_offence",
        "language": "Hinglish",
        "narrative": (
            "Ek ladka meri dukan ke drawer se cash nikalne ki koshish kar raha tha, par jaise hi maine awaz lagayi wo dar ke mare "
            "hath khali chhod kar bhag gaya. Ek bhi rupya chori nahi ho paya."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [62, 303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": ["Act done towards committing theft from cash drawer"],
        "unestablished_elements": ["Completed taking of property"],
        "contradicted_elements": ["Violence, robbery"],
        "material_missing_facts": ["Suspect identification from market CCTV"],
        "expected_uncertainty": "Attempted theft under Section 62 read with Section 303.",
        "expected_attempt": True,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": True,
        "legal_rationale": (
            "Attempt to commit theft under BNS Section 62 read with Section 303. Moving of property was interrupted."
        ),
        "source_reference": "BNS, 2023 Sec 62, Sec 303; BNSS, 2023 First Schedule Part I",
        "review_status": "provisional_pending_legal_review",
        "label_review_notes": 'expected_bailable=True conflicts with the BNSS First Schedule entry for Section 62, under which bailability follows the offence attempted; theft under Section 303(2) is non-bailable. An attempt at theft from a shop drawer may instead be an attempt under Section 305 (building used for the custody of property), also non-bailable.',
        "label_review": {'reviewed_on': '2026-10-20',
         'reviewer': 'Automated statutory cross-check against BNS text and BNSS First Schedule (not a qualified '
                     'legal review)',
         'sources': ['BNSS, 2023 First Schedule, Part I (Gazette of India Extraordinary, 25 Dec 2023)',
                     'BNS, 2023 section text as held in bns_rag_dataset.json'],
         'findings': ['Sections 62 + 303 consistent with the facts (attempt to take cash interrupted; nothing '
                      'taken).',
                      "A shop may be a 'building used for the custody of property' under BNS Section 305(a); whether "
                      'the attempt is under Section 305 requires review.',
                      'Schedule I, Section 62 row: bailability follows the offence attempted; Sections 303(2) and '
                      '305 rows are non-bailable.'],
         'proposed_label_corrections_not_applied': [{'field': 'expected_bailable',
                                                     'current': True,
                                                     'proposed': False,
                                                     'basis': 'Schedule I Section 62 row read with Section '
                                                              '303(2)/305 rows (non-bailable).'},
                                                    {'field': 'plausible_alternatives',
                                                     'current': [],
                                                     'proposed': [305],
                                                     'basis': 'BNS Section 305(a).'}],
         'resolution': 'unresolved_pending_qualified_legal_review'},
        "review_history": [{'date': '2026-10-20',
          'change': 'review_status: verified_authoritative -> provisional_pending_legal_review',
          'reason': 'Bailability label conflicts with labelled sections; unresolved in round 3.'},
         {'date': '2026-10-20',
          'change': 'label_review record added; labels unchanged',
          'reason': 'Case-by-case review against statutory text in round 3.'}]
    },
    {
        "case_id": "BNS-BM-23",
        "category": "attempted_offence",
        "language": "English",
        "narrative": (
            "A man attempted to break open the latch of our apartment door with a crowbar at 3 AM. Our dog barked loudly, "
            "alerting us, and the man fled down the staircase before gaining entry into the house."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [62, 329, 331],
        "plausible_alternatives": [],
        "contradicted_sections": [303],
        "explicitly_supported_elements": [
            "Attempt to commit house-breaking by night (BNS Section 62 read with Section 331)"
        ],
        "unestablished_elements": ["Entry into house", "Theft of property"],
        "contradicted_elements": ["Completed theft (no property moved)"],
        "material_missing_facts": ["Crowbar recovery", "Fingerprint evidence"],
        "expected_uncertainty": "Attempted house-breaking by night; theft not committed.",
        "expected_attempt": True,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Attempt to commit house-breaking by night under BNS Section 62 read with Section 331. Cognizable under BNSS Schedule I."
        ),
        "source_reference": "BNS, 2023 Sec 62, Sec 331; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },

    # ── CATEGORY 6: EXPLICIT NEGATION (CASES 24-27) ──
    {
        "case_id": "BNS-BM-24",
        "category": "explicit_negation",
        "language": "English",
        "narrative": (
            "My office backpack was taken from the back seat of my unlocked car in Malad while I was buying water. "
            "I state categorically that no weapons were used, no force was used, no restraint occurred, and nobody was hurt or threatened in any way. "
            "The bag contained documents and a tablet worth Rs 22,000."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Movable property worth Rs 22,000 taken dishonestly without consent"
        ],
        "unestablished_elements": ["Perpetrator identity"],
        "contradicted_elements": [
            "Weapons, force, restraint, hurt, threat of instant harm (Section 309 Robbery strictly contradicted)"
        ],
        "material_missing_facts": ["Dashcam footage"],
        "expected_uncertainty": "Robbery must be strictly excluded with 0 applicability score.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Simple theft under Section 303(2) BNS. Section 309 (Robbery) is legally contradicted by explicit negative facts "
            "negating all statutory alternative ingredients. Cognizable and Non-bailable under BNSS Schedule I."
        ),
        "source_reference": "BNS, 2023 Sec 303(2); BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-25",
        "category": "explicit_negation",
        "language": "Hindi",
        "narrative": (
            "मेरी दुकान के गल्ले से 15,000 रुपये चोरी हो गए। मैं स्पष्ट रूप से कहता हूं कि किसी भी हथियार का उपयोग नहीं किया गया था, "
            "कोई हिंसा नहीं हुई, किसी को चोट नहीं आई और किसी को कोई धमकी नहीं दी गई।"
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": ["दुकान के गल्ले से 15,000 रुपये की चोरी"],
        "unestablished_elements": ["चोर की पहचान"],
        "contradicted_elements": ["हथियार, हिंसा, चोट और धमकी (लूट धारा 309 का स्पष्ट खंडन)"],
        "material_missing_facts": ["दुकान का सीसीटीवी फुटेज"],
        "expected_uncertainty": "धारा 309 पूरी तरह से बाहर होनी चाहिए।",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "बीएनएस धारा 303(2) के तहत चोरी। धारा 309 का पूर्ण बहिष्कार क्योंकि हिंसा/धमकी का स्पष्ट खंडन किया गया है। "
            "बीएनएसएस अनुसूची I के तहत संज्ञेय और गैर-जमानती।"
        ),
        "source_reference": "BNS, 2023 Sec 303(2); BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-26",
        "category": "explicit_negation",
        "language": "Hinglish",
        "narrative": (
            "Mera mobile car ke dashboard se gayab ho gaya. Na koi weapon tha, na kisi ne force use kiya, "
            "na koi chot aayi, aur na hi koi threat diya gaya tha. Simple stealth chori hai Rs 35,000 ke phone ki."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": ["Stealth theft of Rs 35,000 mobile phone"],
        "unestablished_elements": ["Suspect identity"],
        "contradicted_elements": ["Weapon, force, chot (hurt), threat (Robbery strictly negated)"],
        "material_missing_facts": ["IMEI number"],
        "expected_uncertainty": "Robbery Section 309 must have 0 score.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Theft under Section 303(2) BNS. Section 309 contradicted by explicit facts. Cognizable and Non-bailable under BNSS Schedule I."
        ),
        "source_reference": "BNS, 2023 Sec 303(2); BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-27",
        "category": "explicit_negation",
        "language": "English",
        "narrative": (
            "An umbrella and rain jacket worth Rs 1,400 were taken from the porch rack outside my ground floor flat. "
            "No one was threatened, no force or restraint was exerted, and no weapons were involved. "
            "The property was returned this morning by the neighbor's teenage son who confessed it was his first time."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Theft of property valued at Rs 1,400 (< Rs 5,000)",
            "First-time offender admission",
            "Property returned/restored"
        ],
        "unestablished_elements": ["Formal verification of lack of prior convictions"],
        "contradicted_elements": ["Threat, force, restraint, weapons (Robbery negated)"],
        "material_missing_facts": ["Police record check of accused"],
        "expected_uncertainty": (
            "Section 303(2) proviso squarely applies if verified first-time, leading to Non-cognizable, Bailable classification."
        ),
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": False,
        "expected_bailable": True,
        "legal_rationale": (
            "Theft under Section 303(1). Because property value < Rs 5,000, property was restored, and offender is first-time, "
            "the proviso to Section 303(2) BNS applies (community service punishment). Under BNSS Schedule I Part I, this specific proviso "
            "is NON-COGNIZABLE and BAILABLE (procedure under Section 174 BNSS)."
        ),
        "source_reference": "BNS, 2023 Sec 303(2) proviso; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },

    # ── CATEGORY 7: COMPOUND OFFENCES (CASES 28-31) ──
    {
        "case_id": "BNS-BM-28",
        "category": "compound_offence",
        "language": "English",
        "narrative": (
            "A trespasser climbed over my compound wall at 2 AM, broke the padlock of my garage, "
            "and stole power tools worth Rs 18,000."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303, 329, 331],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "House-trespass / house-breaking by night (BNS Section 329, 331)",
            "Theft of movable property valued at Rs 18,000 (Section 303(2))"
        ],
        "unestablished_elements": ["Identity of intruder"],
        "contradicted_elements": ["Violence against person, robbery"],
        "material_missing_facts": ["Tool serial numbers", "Fingerprint recovery from padlock"],
        "expected_uncertainty": "Compound offence requiring multiple sections (trespass + theft).",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Compound offence comprising house-breaking by night under Section 331(4) BNS and theft under Section 303(2) BNS. "
            "Cognizable and Non-bailable under BNSS Schedule I."
        ),
        "source_reference": "BNS, 2023 Sec 303, Sec 329, Sec 331; BNSS, 2023 First Schedule Part I",
        "review_status": "provisional_pending_legal_review",
        "label_review_notes": 'Section 305 (theft in a building used for the custody of property) is not listed as relevant or plausible, and the applicable sub-section of Section 331 is unstated.',
        "label_review": {'reviewed_on': '2026-10-20',
         'reviewer': 'Automated statutory cross-check against BNS text and BNSS First Schedule (not a qualified '
                     'legal review)',
         'sources': ['BNSS, 2023 First Schedule, Part I (Gazette of India Extraordinary, 25 Dec 2023)',
                     'BNS, 2023 section text as held in bns_rag_dataset.json'],
         'findings': ['Section 303 supported; value Rs 18,000 (Section 303(2) main row: cognizable, non-bailable).',
                      'A garage used to store tools is a building used for the custody of property: Section 305(a) '
                      'is the more specific theft provision and is unlabelled.',
                      'Scaling the compound wall and breaking the padlock at 2 AM to commit theft fits '
                      'house-breaking by night under Section 331(4) (cognizable, non-bailable).',
                      'Section 329 house-trespass is a lesser included description of the entry.'],
         'proposed_label_corrections_not_applied': [{'field': 'relevant_candidate_sections',
                                                     'current': [303, 329, 331],
                                                     'proposed': [303, 305, 329, 331],
                                                     'basis': 'BNS Section 305(a).'}],
         'resolution': 'unresolved_pending_qualified_legal_review'},
        "review_history": [{'date': '2026-10-20',
          'change': 'review_status: verified_authoritative -> provisional_pending_legal_review',
          'reason': 'Specific statutory label concerns identified in inspection round 2.'},
         {'date': '2026-10-20',
          'change': 'label_review record added; labels unchanged',
          'reason': 'Case-by-case review against statutory text in round 3.'}]
    },
    {
        "case_id": "BNS-BM-29",
        "category": "compound_offence",
        "language": "Hindi",
        "narrative": (
            "पड़ोसी ने अवैध रूप से मेरे घर के अहाते में घुसकर मुझे गालियां दीं, थप्पड़ मारा और मेरा मोबाइल जमीन पर पटक कर तोड़ दिया।"
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [115, 329, 351, 352],
        "plausible_alternatives": [],
        "contradicted_sections": [303, 309],
        "explicitly_supported_elements": [
            "घर में अनधिकार प्रवेश (Criminal trespass Section 329)",
            "स्वेच्छया उपहति कारित करना (Voluntarily causing hurt Section 115)",
            "अपमान और संपत्ति का नुकसान/रिष्टि (Mischief / Insult Section 351, 352)"
        ],
        "unestablished_elements": ["चोरी करने का आशय"],
        "contradicted_elements": ["चोरी या लूट (संपत्ति ले जाई नहीं गई, बल्कि तोड़ी गई)"],
        "material_missing_facts": ["टूटे हुए फोन की कीमत", "मेडिकल चोट पर्ची"],
        "expected_uncertainty": "चोरी (धारा 303) नहीं बनती; उपहति, अतिचार और रिष्टि का संयुक्त अपराध है।",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": False,
        "expected_bailable": True,
        "legal_rationale": (
            "धारा 115 (साधारण उपहति) असंज्ञेय/जमानती है; धारा 329 (आपराधिक अतिचार) असंज्ञेय/जमानती है; "
            "धारा 352 (शांति भंग करने के आशय से अपमान) असंज्ञेय/जमानती है। बीएनएसएस धारा 174 के तहत एनसीआर प्रक्रिया।"
        ),
        "source_reference": "BNS, 2023 Sec 115, Sec 329, Sec 352; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-30",
        "category": "compound_offence",
        "language": "Hinglish",
        "narrative": (
            "Ghar ka purana servant bina permission flat mein ghusa duplicate key se, bedroom almirah khol ke 80,000 cash chori kiya "
            "aur jab society watchman ne roka toh watchman ko danda maar kar ghayal kar diya."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303, 309, 115, 329],
        "plausible_alternatives": [],
        "contradicted_sections": [],
        "explicitly_supported_elements": [
            "House-trespass with duplicate key",
            "Theft of Rs 80,000 from almirah",
            "Voluntarily causing hurt in carrying away stolen property (Robbery BNS Section 309)"
        ],
        "unestablished_elements": ["Servant current whereabouts"],
        "contradicted_elements": [],
        "material_missing_facts": ["Watchman medical report"],
        "expected_uncertainty": "Theft converted into robbery because hurt was caused while carrying away stolen property.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Under BNS Section 309, theft is robbery if in carrying away stolen property the offender voluntarily causes hurt. "
            "Hitting the watchman with a stick transforms the theft into robbery. Cognizable and Non-bailable under BNSS Schedule I."
        ),
        "source_reference": "BNS, 2023 Sec 309, Sec 115, Sec 329; BNSS, 2023 First Schedule Part I",
        "review_status": "provisional_pending_legal_review",
        "label_review_notes": 'Section 306 (theft by servant) and Section 305 are not listed; hurt with a stick (Section 115 vs Section 118) and entry using a duplicate key (Sections 330/331) require review.',
        "label_review": {'reviewed_on': '2026-10-20',
         'reviewer': 'Automated statutory cross-check against BNS text and BNSS First Schedule (not a qualified '
                     'legal review)',
         'sources': ['BNSS, 2023 First Schedule, Part I (Gazette of India Extraordinary, 25 Dec 2023)',
                     'BNS, 2023 section text as held in bns_rag_dataset.json'],
         'findings': ["'Purana servant' is ambiguous (former or long-serving); Section 306 applies only if the "
                      'person was a clerk or servant at the time of the theft.',
                      'Theft from a bedroom almirah in a flat falls within Section 305(a) (building used as a human '
                      'dwelling).',
                      'Entering by opening a lock with a duplicate key may be house-breaking under Section 330; time '
                      'of entry not stated (Section 331 sub-section unknown).',
                      'Hurt caused to the watchman while carrying away the property supports Section 309; Section '
                      '309(6) covers causing hurt in committing robbery.',
                      "Whether a 'danda' is an instrument likely to cause death (Section 118(1)) rather than simple "
                      'hurt (Section 115) is a factual question.'],
         'proposed_label_corrections_not_applied': [{'field': 'plausible_alternatives',
                                                     'current': [],
                                                     'proposed': [305, 306, 118, 331],
                                                     'basis': 'BNS Sections 305(a), 306, 118(1), 330/331.'}],
         'resolution': 'unresolved_pending_qualified_legal_review'},
        "review_history": [{'date': '2026-10-20',
          'change': 'review_status: verified_authoritative -> provisional_pending_legal_review',
          'reason': 'Specific statutory label concerns identified in inspection round 2.'},
         {'date': '2026-10-20',
          'change': 'label_review record added; labels unchanged',
          'reason': 'Case-by-case review against statutory text in round 3.'}]
    },
    {
        "case_id": "BNS-BM-31",
        "category": "compound_offence",
        "language": "English",
        "narrative": (
            "A tenant whose lease expired 3 months ago refused to vacate, broke the padlock of the owner's locked storage room "
            "inside the premises, and disposed of the owner's antique furniture worth Rs 50,000."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303, 316, 329],
        "plausible_alternatives": [314],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Breaking lock of private storage room (criminal trespass)",
            "Disposing of landlord's furniture (theft / criminal breach of trust)"
        ],
        "unestablished_elements": ["Exact terms of expired tenancy agreement"],
        "contradicted_elements": ["Physical violence, armed robbery"],
        "material_missing_facts": ["Tenancy agreement and eviction notices"],
        "expected_uncertainty": "Intersection of criminal breach of trust (Section 316) and theft (Section 303).",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Breaking open locked storage room not covered by lease and removing furniture constitutes theft under Section 303(2) BNS "
            "and criminal trespass under Section 329 BNS. Cognizable and Non-bailable."
        ),
        "source_reference": "BNS, 2023 Sec 303, Sec 316, Sec 329; BNSS, 2023 First Schedule Part I",
        "review_status": "provisional_pending_legal_review",
        "label_review_notes": 'Section 316 is labelled relevant although the narrative does not state entrustment of the furniture; the legal rationale itself analyses theft and criminal trespass.',
        "label_review": {'reviewed_on': '2026-10-20',
         'reviewer': 'Automated statutory cross-check against BNS text and BNSS First Schedule (not a qualified '
                     'legal review)',
         'sources': ['BNSS, 2023 First Schedule, Part I (Gazette of India Extraordinary, 25 Dec 2023)',
                     'BNS, 2023 section text as held in bns_rag_dataset.json'],
         'findings': ["Section 316 requires entrustment or dominion over the property; furniture in the owner's "
                      'separately locked storage room was not stated to be entrusted to the tenant.',
                      "Section 303 supported (furniture moved out of the owner's possession and disposed of; value "
                      'Rs 50,000).',
                      'Breaking the padlock of a room used to store property may be house-breaking (Sections '
                      '330/331) and theft in a building used for the custody of property (Section 305(a)).',
                      'Section 329 (tenant remaining after expiry of lease with intent to commit an offence) '
                      'supported on the stated facts.'],
         'proposed_label_corrections_not_applied': [{'field': 'relevant_candidate_sections',
                                                     'current': [303, 316, 329],
                                                     'proposed': [303, 329],
                                                     'basis': 'No entrustment stated (BNS Section 316(1)).'},
                                                    {'field': 'plausible_alternatives',
                                                     'current': [314],
                                                     'proposed': [314, 316, 305, 331],
                                                     'basis': 'BNS Sections 305(a), 316, 330/331.'}],
         'resolution': 'unresolved_pending_qualified_legal_review'},
        "review_history": [{'date': '2026-10-20',
          'change': 'review_status: verified_authoritative -> provisional_pending_legal_review',
          'reason': 'Specific statutory label concerns identified in inspection round 2.'},
         {'date': '2026-10-20',
          'change': 'label_review record added; labels unchanged',
          'reason': 'Case-by-case review against statutory text in round 3.'}]
    },

    # ── CATEGORY 8: AMBIGUOUS COMPLAINTS (CASES 32-35) ──
    {
        "case_id": "BNS-BM-32",
        "category": "ambiguous_complaint",
        "language": "English",
        "narrative": (
            "I gave my business partner Rs 2,00,000 as investment capital for our joint restaurant venture. "
            "He neither opened the restaurant nor returned the money upon demand, claiming the project faced licensing difficulties."
        ),
        "classification_type": "B",
        "relevant_candidate_sections": [316, 318],
        "plausible_alternatives": [],
        "contradicted_sections": [303, 309],
        "explicitly_supported_elements": ["Entrustment of money for business venture"],
        "unestablished_elements": [
            "Dishonest intention ab initio (Cheating Section 318)",
            "Dishonest misappropriation vs genuine commercial business loss (Section 316)"
        ],
        "contradicted_elements": ["Theft from possession, robbery, physical force"],
        "material_missing_facts": [
            "Partnership agreement terms",
            "Bank accounts showing whether funds were diverted or spent on licensing"
        ],
        "expected_uncertainty": (
            "Cannot determine whether this is a civil commercial dispute or criminal breach of trust (Section 316) / cheating (Section 318). "
            "Requires investigative verification under Section 173(3) BNSS."
        ),
        "expected_attempt": False,
        "verified_schedule_applicable": False,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "Breach of contract does not automatically constitute a penal offence unless dishonest intention existed at inception (Section 318) "
            "or property was dishonestly converted (Section 316). Procedural registration depends on preliminary enquiry."
        ),
        "source_reference": "BNS, 2023 Sec 316, Sec 318; BNSS, 2023 Sec 173(3)",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-33",
        "category": "ambiguous_complaint",
        "language": "Hindi",
        "narrative": (
            "मैंने अपने दोस्त को एक हफ्ते के लिए अपनी कार दी थी। अब एक महीना हो गया है, "
            "वह कार वापस नहीं कर रहा है और बहाने बना रहा है कि कार गैराज में रिपेयर हो रही है।"
        ),
        "classification_type": "B",
        "relevant_candidate_sections": [316],
        "plausible_alternatives": [314, 303],
        "contradicted_sections": [309],
        "explicitly_supported_elements": ["कार का संन्यास (Entrustment of car to friend)"],
        "unestablished_elements": ["बेईमानी से संपरिवर्तन (Dishonest conversion) बनाम वास्तविक देरी"],
        "contradicted_elements": ["चोरी या लूट (कब्जा स्वेच्छा से दिया गया था)"],
        "material_missing_facts": ["गैराज का बिल या पुष्टि कि कार बेची गई है या नहीं"],
        "expected_uncertainty": "अमानत में खयानत (धारा 316) अथवा सिविल विवाद की अनिश्चितता।",
        "expected_attempt": False,
        "verified_schedule_applicable": False,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "कब्जा सहमति से दिया गया था, इसलिए धारा 303 चोरी नहीं बनती। धारा 316 (आपराधिक विश्वासघात) तभी बनेगा जब कार का "
            "बेईमानी से दुरुपयोग साबित हो। धारा 173(3) बीएनएसएस के तहत प्रारंभिक जांच अपेक्षित है।"
        ),
        "source_reference": "BNS, 2023 Sec 316; BNSS, 2023 Sec 173(3)",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-34",
        "category": "ambiguous_complaint",
        "language": "Hinglish",
        "narrative": (
            "Society builder ne possession dene ka promise kiya tha December 2024 tak aur hum sab se 10-10 lakh extra le liye amenities ke naam pe. "
            "Abhi tak building incomplete hai aur builder bol raha hai construction cost badh gaya."
        ),
        "classification_type": "B",
        "relevant_candidate_sections": [318],
        "plausible_alternatives": [],
        "contradicted_sections": [303, 309],
        "explicitly_supported_elements": ["Payment of money under builder-buyer agreement"],
        "unestablished_elements": ["Fraudulent/dishonest inducement at the inception (Cheating Section 318)"],
        "contradicted_elements": ["Physical theft, robbery"],
        "material_missing_facts": ["RERA registration and agreement terms"],
        "expected_uncertainty": "Consumer/civil contractual dispute vs criminal cheating.",
        "expected_attempt": False,
        "verified_schedule_applicable": False,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "Commercial contractual delay requires preliminary enquiry under Section 173(3) BNSS before registering penal cheating case under Section 318 BNS."
        ),
        "source_reference": "BNS, 2023 Sec 318; BNSS, 2023 Sec 173(3)",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-35",
        "category": "ambiguous_complaint",
        "language": "English",
        "narrative": (
            "My estranged brother took our deceased father's vintage wristwatch from the ancestral house locker, "
            "claiming our father verbally gifted it to him before passing away, which our mother disputes."
        ),
        "classification_type": "B",
        "relevant_candidate_sections": [303, 314],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": ["Taking of wristwatch from ancestral locker"],
        "unestablished_elements": [
            "Dishonest intention vs bona fide claim of right (gift assertion)"
        ],
        "contradicted_elements": ["Robbery, force, weapons"],
        "material_missing_facts": ["Will or testamentary records", "Mother's statement"],
        "expected_uncertainty": (
            "Bona fide claim of right excludes theft under Section 303 BNS; civil succession dispute likely."
        ),
        "expected_attempt": False,
        "verified_schedule_applicable": False,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "If property is taken under a bona fide belief of entitlement (gift by father), dishonest intention is absent. "
            "Cannot establish theft under Section 303 BNS without verifying title."
        ),
        "source_reference": "BNS, 2023 Sec 303; Supreme Court precedent on bona fide claim of right",
        "review_status": "verified_authoritative"
    },

    # ── CATEGORY 9: MISSING MATERIAL FACTS (CASES 36-39) ──
    {
        "case_id": "BNS-BM-36",
        "category": "missing_material_facts",
        "language": "English",
        "narrative": (
            "Someone stole my handbag from a restaurant chair in Colaba while I was washing my hands. "
            "The bag contained personal cosmetics, a notebook, and some cash."
        ),
        "classification_type": "B",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Theft of movable handbag out of possession without consent"
        ],
        "unestablished_elements": ["Perpetrator identity"],
        "contradicted_elements": ["Violence, force, weapons"],
        "material_missing_facts": [
            "Monetary value of the handbag and cash",
            "Whether value is less than Rs 5,000",
            "Identity and prior conviction history of suspect"
        ],
        "expected_uncertainty": (
            "Procedural classification under BNSS Schedule I is completely unknown / conditional: "
            "if value < Rs 5,000 with first-time restoration, Non-cognizable (NCR under Sec 174 BNSS); "
            "if value >= Rs 5,000, Cognizable (FIR under Sec 173 BNSS). Explicit None must be returned."
        ),
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "Section 303(1) theft is established, but procedural status cannot be determined because property value is unstated. "
            "Engine must explicitly express uncertainty and return None for cognizable/bailable fields."
        ),
        "source_reference": "BNS, 2023 Sec 303(2); BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-37",
        "category": "missing_material_facts",
        "language": "Hindi",
        "narrative": (
            "मेरी साइकिल सोसाइटी कंपाउंड से चोरी हो गई है। चोर का पता नहीं है और न ही कोई चश्मदीद गवाह है।"
        ),
        "classification_type": "B",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": ["साइकिल की चोरी"],
        "unestablished_elements": ["चोर की पहचान"],
        "contradicted_elements": ["हिंसा या लूट"],
        "material_missing_facts": [
            "साइकिल की अनुमानित कीमत (मूल्य 5000 रुपये से कम है या अधिक)",
            "आरोपी का पूर्व आपराधिक इतिहास"
        ],
        "expected_uncertainty": "कीमत अज्ञात होने के कारण संज्ञेयता का निर्धारण नहीं किया जा सकता।",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "बीएनएस धारा 303। मूल्य अज्ञात होने से धारा 303(2) का सामान्य खंड या परंतु (proviso) लागू होगा, यह अनिर्णीत है। "
            "अतः प्रक्रियात्मक स्थिति अनिर्धारित (None) रहेगी।"
        ),
        "source_reference": "BNS, 2023 Sec 303(2); BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-38",
        "category": "missing_material_facts",
        "language": "Hinglish",
        "narrative": (
            "Station ke bahar se meri leather jacket chori ho gayi. Koi confrontation nahi hua, bas gayab ho gayi."
        ),
        "classification_type": "B",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": ["Theft of leather jacket"],
        "unestablished_elements": ["Suspect identity"],
        "contradicted_elements": ["Confrontation, robbery"],
        "material_missing_facts": ["Value of jacket", "Prior record of accused"],
        "expected_uncertainty": "Value unstated; procedural classification conditional.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "BNS Section 303 theft. Absence of value prevents determining if general clause or proviso applies."
        ),
        "source_reference": "BNS, 2023 Sec 303; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-39",
        "category": "missing_material_facts",
        "language": "English",
        "narrative": (
            "A wristwatch was taken from my hotel room locker. The lock was opened with a master key. Value of watch is not specified."
        ),
        "classification_type": "B",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [316],
        "contradicted_sections": [309],
        "explicitly_supported_elements": ["Wristwatch removed from hotel room locker"],
        "unestablished_elements": ["Staff entrustment vs external intruder"],
        "contradicted_elements": ["Robbery, force, weapons"],
        "material_missing_facts": ["Watch value", "Hotel staff key log"],
        "expected_uncertainty": "Unknown value and entrustment status require clarification.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "Theft under Section 303 or breach of trust under Section 316. Value missing."
        ),
        "source_reference": "BNS, 2023 Sec 303, Sec 316",
        "review_status": "verified_authoritative"
    },

    # ── CATEGORY 10: MISLEADING KEYWORDS (CASES 40-43) ──
    {
        "case_id": "BNS-BM-40",
        "category": "misleading_keywords",
        "language": "English",
        "narrative": (
            "The supermarket charged me Rs 600 for imported mangoes which were labeled Rs 300 on the rack. "
            "I feel completely robbed and cheated by their daylight robbery pricing policy."
        ),
        "classification_type": "C",
        "relevant_candidate_sections": [],
        "plausible_alternatives": [],
        "contradicted_sections": [303, 309, 318],
        "explicitly_supported_elements": [],
        "unestablished_elements": ["All statutory elements of Robbery, Theft, or Penal Cheating"],
        "contradicted_elements": [
            "Penal offence of Robbery (Section 309) or Theft (Section 303) — purely metaphorical consumer pricing grievance"
        ],
        "material_missing_facts": ["Consumer forum complaint"],
        "expected_uncertainty": (
            "Keyword 'robbed'/'robbery' is colloquial hyperbole. No criminal offence under BNS. Must NOT return Section 309."
        ),
        "expected_attempt": False,
        "verified_schedule_applicable": False,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "Metaphorical colloquial grievance ('daylight robbery') regarding retail pricing. Does not satisfy any element of BNS Section 309 or Section 303. "
            "Engine must reject keyword-driven hallucination of robbery."
        ),
        "source_reference": "Consumer Protection Act, 2019 (Civil remedy; no BNS offence)",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-41",
        "category": "misleading_keywords",
        "language": "Hindi",
        "narrative": (
            "उस दुकानदार ने मुझे बातों में उलझाकर मेरा बहुत सारा कीमती समय लूट लिया और मुझे कोई सामान भी पसंद नहीं आया।"
        ),
        "classification_type": "C",
        "relevant_candidate_sections": [],
        "plausible_alternatives": [],
        "contradicted_sections": [303, 309],
        "explicitly_supported_elements": [],
        "unestablished_elements": ["चोरी या लूट के तत्व"],
        "contradicted_elements": ["चल संपत्ति की चोरी या सदोष अवरोध/उपहति (लाक्षणिक प्रयोग 'समय लूट लिया')"],
        "material_missing_facts": ["कोई आपराधिक कृत्य नहीं"],
        "expected_uncertainty": "लाक्षणिक मुहावरा (समय लूटना); कोई दांडिक अपराध नहीं।",
        "expected_attempt": False,
        "verified_schedule_applicable": False,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "यह केवल मुहावरेदार अभिव्यक्ति है। बीएनएस की धारा 309 (लूट) के तत्व पूर्णतः अनुपस्थित हैं।"
        ),
        "source_reference": "Non-penal narrative; BNS Sections inapplicable",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-42",
        "category": "misleading_keywords",
        "language": "Hinglish",
        "narrative": (
            "Bhai movie theater waale popcorn ka 500 rupya le rahe hain, yeh toh openly public ko loot rahe hain, "
            "police ko inpe robbery ka case darj karna chahiye."
        ),
        "classification_type": "C",
        "relevant_candidate_sections": [],
        "plausible_alternatives": [],
        "contradicted_sections": [303, 309],
        "explicitly_supported_elements": [],
        "unestablished_elements": ["Penal ingredients of BNS Section 309"],
        "contradicted_elements": ["Theft, extortion, violence, weapons"],
        "material_missing_facts": ["None (non-criminal complaint)"],
        "expected_uncertainty": "Non-penal commercial grievance; keyword 'loot' / 'robbery' must not trigger Section 309.",
        "expected_attempt": False,
        "verified_schedule_applicable": False,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "Colloquial slang 'public ko loot rahe hain'. No penal offence under BNS."
        ),
        "source_reference": "Non-penal narrative",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-43",
        "category": "misleading_keywords",
        "language": "English",
        "narrative": (
            "My colleague snatched the promotion from under my nose by taking credit for my presentation in the board meeting."
        ),
        "classification_type": "C",
        "relevant_candidate_sections": [],
        "plausible_alternatives": [],
        "contradicted_sections": [304, 303, 309],
        "explicitly_supported_elements": [],
        "unestablished_elements": ["Physical movable property", "Sudden or forcible seizure from person"],
        "contradicted_elements": ["Penal snatching under BNS Section 304"],
        "material_missing_facts": ["Corporate internal HR grievance"],
        "expected_uncertainty": "Corporate metaphor; must not be classified under Section 304 Snatching.",
        "expected_attempt": False,
        "verified_schedule_applicable": False,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "Metaphorical corporate complaint. BNS Section 304 requires movable physical property taken from a person."
        ),
        "source_reference": "Non-penal narrative",
        "review_status": "verified_authoritative"
    },

    # ── CATEGORY 11: PARAPHRASED NARRATIVES (CASES 44-47) ──
    {
        "case_id": "BNS-BM-44",
        "category": "paraphrased_narrative",
        "language": "English",
        "narrative": (
            "Deprived of my portable computing terminal through surreptitious removal from my vehicle's rear compartment "
            "during my brief absence at the fuel depot. Valuation amounts to approximately thirty-two thousand rupees without any overt intimidation or corporeal harm."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Dishonest taking of movable property (computing terminal / laptop valued at Rs 32,000) out of vehicle"
        ],
        "unestablished_elements": ["Perpetrator identity"],
        "contradicted_elements": ["Intimidation, corporeal harm, weapons"],
        "material_missing_facts": ["Serial number of terminal"],
        "expected_uncertainty": "Formal legalistic phrasing describes simple theft over Rs 5,000.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Theft under Section 303(2) BNS. Intimidation and harm explicitly negated, excluding Section 309. Cognizable and Non-bailable."
        ),
        "source_reference": "BNS, 2023 Sec 303(2); BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-45",
        "category": "paraphrased_narrative",
        "language": "Hindi",
        "narrative": (
            "मेरी अनुपस्थिति में किसी अज्ञात व्यक्ति द्वारा मेरे शयनकक्ष की अलमारी से पच्चीस हजार रुपये की नकद राशि "
            "अपहृत कर ली गई है, बिना किसी हिंसा अथवा विवशता के।"
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303, 329],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "शयनकक्ष से 25,000 रुपये नकद की चोरी",
            "गृह अतिचार (House-trespass)"
        ],
        "unestablished_elements": ["अज्ञात व्यक्ति की पहचान"],
        "contradicted_elements": ["हिंसा या विवशता"],
        "material_missing_facts": ["प्रवेश का माध्यम (ताला तोड़ा या खुली खिड़की)"],
        "expected_uncertainty": "शुद्ध चोरी और गृह-अतिचार। लूट का खंडन।",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "बीएनएस धारा 303(2) (चोरी) तथा धारा 329 (अतिचार)। संज्ञेय और गैर-जमानती।"
        ),
        "source_reference": "BNS, 2023 Sec 303(2), Sec 329; BNSS, 2023 First Schedule Part I",
        "review_status": "provisional_pending_legal_review",
        "label_review_notes": 'Section 305 (theft in a dwelling house) is not listed, and Section 329 assumes entry facts that the narrative does not state.',
        "label_review": {'reviewed_on': '2026-10-20',
         'reviewer': 'Automated statutory cross-check against BNS text and BNSS First Schedule (not a qualified '
                     'legal review)',
         'sources': ['BNSS, 2023 First Schedule, Part I (Gazette of India Extraordinary, 25 Dec 2023)',
                     'BNS, 2023 section text as held in bns_rag_dataset.json'],
         'findings': ['Theft of Rs 25,000 cash from a bedroom almirah falls within Section 305(a) (building used as '
                      'a human dwelling); unlabelled.',
                      'Section 329 requires unlawful entry or remaining; the narrative does not say how the unknown '
                      'person entered (lawful visitors are possible).',
                      'Section 309 correctly contradicted (no violence or coercion).'],
         'proposed_label_corrections_not_applied': [{'field': 'relevant_candidate_sections',
                                                     'current': [303, 329],
                                                     'proposed': [303, 305],
                                                     'basis': 'BNS Section 305(a).'},
                                                    {'field': 'plausible_alternatives',
                                                     'current': [],
                                                     'proposed': [329],
                                                     'basis': 'Entry facts not stated (BNS Section 329).'}],
         'resolution': 'unresolved_pending_qualified_legal_review'},
        "review_history": [{'date': '2026-10-20',
          'change': 'review_status: verified_authoritative -> provisional_pending_legal_review',
          'reason': 'Specific statutory label concerns identified in inspection round 2.'},
         {'date': '2026-10-20',
          'change': 'label_review record added; labels unchanged',
          'reason': 'Case-by-case review against statutory text in round 3.'}]
    },
    {
        "case_id": "BNS-BM-46",
        "category": "paraphrased_narrative",
        "language": "Hinglish",
        "narrative": (
            "Chalti local mein se kisi smart chor ne pocket se purse khiska diya, koi pata bhi nahi chala, "
            "jab platform pe utra tab dekha jeb khali thi. Total 7000 rupaye the andar."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [303],
        "plausible_alternatives": [],
        "contradicted_sections": [309],
        "explicitly_supported_elements": ["Pickpocketing of Rs 7,000 purse from pocket"],
        "unestablished_elements": ["Perpetrator identity"],
        "contradicted_elements": ["Violence, confrontation"],
        "material_missing_facts": ["Exact train coach"],
        "expected_uncertainty": "Simple theft > Rs 5,000.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Stealth pickpocketing is theft under BNS Section 303(2). Property value > Rs 5,000: Cognizable and Non-bailable."
        ),
        "source_reference": "BNS, 2023 Sec 303(2); BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-47",
        "category": "paraphrased_narrative",
        "language": "English",
        "narrative": (
            "An unknown assailant abruptly and forcibly tore a platinum necklace from a pedestrian's throat "
            "whilst astride a pillion, subsequently accelerating into oncoming traffic."
        ),
        "classification_type": "A",
        "relevant_candidate_sections": [304],
        "plausible_alternatives": [303],
        "contradicted_sections": [309],
        "explicitly_supported_elements": [
            "Sudden and forcible tearing away of necklace from person (Snatching Section 304 BNS)"
        ],
        "unestablished_elements": ["Assailant and motorcycle details"],
        "contradicted_elements": [],
        "material_missing_facts": ["Value of platinum necklace"],
        "expected_uncertainty": "Snatching under Section 304 BNS.",
        "expected_attempt": False,
        "verified_schedule_applicable": True,
        "expected_cognizable": True,
        "expected_bailable": False,
        "legal_rationale": (
            "Abrupt and forcible tearing from throat constitutes Snatching under Section 304 BNS. Cognizable and Non-bailable."
        ),
        "source_reference": "BNS, 2023 Sec 304; BNSS, 2023 First Schedule Part I",
        "review_status": "verified_authoritative"
    },

    # ── CATEGORY 12: INSUFFICIENT INFORMATION (CASES 48-50) ──
    {
        "case_id": "BNS-BM-48",
        "category": "insufficient_information",
        "language": "English",
        "narrative": (
            "Bad thing happened near railway gate yesterday night. Please take action immediately."
        ),
        "classification_type": "D",
        "relevant_candidate_sections": [],
        "plausible_alternatives": [],
        "contradicted_sections": [],
        "explicitly_supported_elements": [],
        "unestablished_elements": ["All statutory elements"],
        "contradicted_elements": [],
        "material_missing_facts": [
            "Nature of the incident",
            "Offence alleged",
            "Property or person affected",
            "Date, time, and specific location"
        ],
        "expected_uncertainty": (
            "Completely insufficient information. Engine must report ambiguity / narrative too brief and avoid confident classification."
        ),
        "expected_attempt": False,
        "verified_schedule_applicable": False,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "Does not articulate facts supporting any cognizable or non-cognizable statutory offence under the BNS, 2023."
        ),
        "source_reference": "BNSS, 2023 Sec 173 (Insufficient information for FIR registration)",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-49",
        "category": "insufficient_information",
        "language": "Hindi",
        "narrative": (
            "कुछ लोग गड़बड़ कर रहे हैं, पुलिस तुरंत आकर जांच करे।"
        ),
        "classification_type": "D",
        "relevant_candidate_sections": [],
        "plausible_alternatives": [],
        "contradicted_sections": [],
        "explicitly_supported_elements": [],
        "unestablished_elements": ["सभी विधिक तत्व"],
        "contradicted_elements": [],
        "material_missing_facts": ["विशिष्ट घटना, स्थान, आरोपी का विवरण, अपराध की प्रकृति"],
        "expected_uncertainty": "तथ्यों के अभाव में किसी भी धारा में वर्गीकरण संभव नहीं।",
        "expected_attempt": False,
        "verified_schedule_applicable": False,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "अति संक्षिप्त और अस्पष्ट शिकायत जिसमें किसी संज्ञेय अपराध के तत्व नहीं हैं।"
        ),
        "source_reference": "BNSS, 2023 Sec 173",
        "review_status": "verified_authoritative"
    },
    {
        "case_id": "BNS-BM-50",
        "category": "insufficient_information",
        "language": "Hinglish",
        "narrative": (
            "Mera bohot bada nuksan ho gaya hai kal sham ko, please FIR likho aur mujhe justice dilao."
        ),
        "classification_type": "D",
        "relevant_candidate_sections": [],
        "plausible_alternatives": [],
        "contradicted_sections": [],
        "explicitly_supported_elements": [],
        "unestablished_elements": ["All statutory elements"],
        "contradicted_elements": [],
        "material_missing_facts": [
            "Type of loss (commercial, civil, accident, or criminal)",
            "Specific criminal act",
            "Property or person involved"
        ],
        "expected_uncertainty": "Insufficient facts to ground any BNS penal section.",
        "expected_attempt": False,
        "verified_schedule_applicable": False,
        "expected_cognizable": None,
        "expected_bailable": None,
        "legal_rationale": (
            "Bare allegation of loss without describing criminal acts or mens rea cannot justify any BNS section."
        ),
        "source_reference": "BNSS, 2023 Sec 173",
        "review_status": "verified_authoritative"
    }
]


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(base_dir, "bns_synthetic_benchmark_50.json")

    print(f"Generating benchmark with {len(BENCHMARK_CASES)} cases...")

    # Validation checks
    assert len(BENCHMARK_CASES) == 50, f"Expected 50 cases, got {len(BENCHMARK_CASES)}"

    ids = set()
    categories = {}
    languages = {}
    types = {}

    for c in BENCHMARK_CASES:
        cid = c["case_id"]
        assert cid not in ids, f"Duplicate ID: {cid}"
        ids.add(cid)

        cat = c["category"]
        categories[cat] = categories.get(cat, 0) + 1

        lang = c["language"]
        languages[lang] = languages.get(lang, 0) + 1

        ctype = c["classification_type"]
        types[ctype] = types.get(ctype, 0) + 1

        # Check required fields
        required_fields = [
            "case_id", "category", "language", "narrative", "classification_type",
            "relevant_candidate_sections", "plausible_alternatives", "contradicted_sections",
            "explicitly_supported_elements", "unestablished_elements", "contradicted_elements",
            "material_missing_facts", "expected_uncertainty", "expected_attempt",
            "verified_schedule_applicable", "expected_cognizable", "expected_bailable",
            "legal_rationale", "source_reference", "review_status"
        ]
        for f in required_fields:
            assert f in c, f"Missing field '{f}' in case {cid}"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(BENCHMARK_CASES, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {out_path} ({os.path.getsize(out_path)} bytes)")
    print(f"Categories ({len(categories)}): {categories}")
    print(f"Languages ({len(languages)}): {languages}")
    print(f"Classification Types ({len(types)}): {types}")


if __name__ == "__main__":
    main()
