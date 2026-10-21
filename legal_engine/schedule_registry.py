"""
BNSS Schedule I Registry.

Procedural classifications for a subset of BNS offences, transcribed from Part I of the
First Schedule of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 (Act No. 46 of 2023),
as published in the Gazette of India (Extraordinary), Part II, Section 1, 25 December 2023.

Offences whose classification differs between sub-sections are stored as sub-section rows.
When the applicable sub-section cannot be determined from the facts, a field is reported only
if every row agrees on it; otherwise it is left unverified (None).

Includes eligibility checks for preliminary enquiry under Section 173(3) BNSS, which applies to
information relating to a cognizable offence made punishable for three years or more but less
than seven years. Eligibility is computed from the maximum term in each row; an offence whose
maximum term is seven years or more is outside that range.

Sections not in this registry retain an explicit 'unverified_schedule' status in the corpus.
"""

from typing import Dict, Any, Optional, Tuple, List

# Sentinel used for offences punishable with imprisonment for life (or death).
LIFE_IMPRISONMENT_YEARS = 100.0

BNSS_173_3_MIN_YEARS = 3.0
BNSS_173_3_CEILING_YEARS = 7.0

BNSS_173_3_PROCEDURE_TEXT = (
    "Under Section 173(3) BNSS, on receipt of information relating to a cognizable offence made punishable "
    "for three years or more but less than seven years, the officer in charge of the police station may, with "
    "the prior permission of an officer not below the rank of Deputy Superintendent of Police and considering "
    "the nature and gravity of the offence, either (i) conduct a preliminary enquiry to ascertain whether a "
    "prima facie case exists, within a period of fourteen days, or (ii) proceed with investigation when a "
    "prima facie case exists."
)

BNSS_173_3_CAVEAT_TEXT = (
    "This is a discretion available to the police, not a requirement; how Section 173(3) interacts with the "
    "duty to record information under Section 173(1), and with the principles in Lalita Kumari v. Government "
    "of Uttar Pradesh, (2014) 2 SCC 1 (mandatory registration of an FIR where information discloses a cognizable "
    "offence), is the subject of differing judicial and academic views and is not determined by this assessment."
)

BNSS_173_3_RANGE_READING_NOTE = (
    "Range checks use the maximum term prescribed for the offence ('punishable for' read as the maximum term); "
    "offences whose maximum is exactly seven years are treated as outside 'less than seven years', and offences "
    "whose maximum is exactly three years as within 'three years or more'. This reading is pending qualified legal review."
)

# Legal questions this module deliberately does not resolve. Outputs must keep these uncertain.
OPEN_LEGAL_QUESTIONS = {
    "303_proviso_at_registration": (
        "Whether a complaint of theft of property under Rs 5,000 that has been returned or restored may be treated "
        "as non-cognizable at the FIR-registration stage, given that the BNS proviso to Section 303(2) also requires "
        "a first conviction, which is known only after trial. The registry leaves classification unverified."
    ),
    "173_3_punishment_range_reading": BNSS_173_3_RANGE_READING_NOTE,
    "173_3_and_lalita_kumari": (
        "How the Section 173(3) BNSS discretion is reconciled with Lalita Kumari v. Government of Uttar Pradesh, "
        "(2014) 2 SCC 1."
    ),
    "324_value_bands": (
        "The Gazette text of BNSS Schedule I describes Section 324(4) as loss of 'twenty thousand rupees but less than "
        "2 lakh rupees' and Section 324(5) as 'one lakh rupees or upwards', which overlap; the BNS text of Section "
        "324(4) reads 'less than one lakh rupees'. Classification for losses between Rs 1 lakh and Rs 2 lakh is unresolved."
    ),
}

GAZETTE_SOURCE = (
    "Bharatiya Nagarik Suraksha Sanhita, 2023 (Act No. 46 of 2023), First Schedule, Part I "
    "(Gazette of India Extraordinary, 25 December 2023)"
)


def _row(offence, is_cognizable, is_bailable, court, punishment, max_years, min_years=0.0):
    return {
        "offence": offence,
        "is_cognizable": is_cognizable,
        "is_bailable": is_bailable,
        "court_triable_by": court,
        "punishment_summary": punishment,
        "min_punishment_years": min_years,
        "max_punishment_years": max_years,
    }


VERIFIED_SCHEDULE_I: Dict[int, Dict[str, Any]] = {
    115: {
        "section": 115,
        "title": "Voluntarily causing hurt",
        "is_conditional": False,
        **_row("Voluntarily causing hurt (Section 115(2))", False, True, "Any Magistrate",
               "Imprisonment up to 1 year, or fine up to Rs 10,000, or both.", 1.0),
    },
    117: {
        "section": 117,
        "title": "Voluntarily causing grievous hurt",
        "is_conditional": True,
        "condition_type": "sub_section",
        "condition_description": (
            "Section 117(2) is cognizable and bailable; Sections 117(3) (permanent disability or persistent "
            "vegetative state) and 117(4) (grievous hurt by a group of five or more persons on specified grounds) "
            "are cognizable and non-bailable, triable by the Court of Session."
        ),
        "sub_sections": {
            "117(2)": _row("Voluntarily causing grievous hurt", True, True, "Any Magistrate",
                           "Imprisonment up to 7 years, and fine.", 7.0),
            "117(3)": _row("Grievous hurt resulting in permanent disability or persistent vegetative state",
                           True, False, "Court of Session",
                           "Rigorous imprisonment not less than 10 years, extendable to imprisonment for life.",
                           LIFE_IMPRISONMENT_YEARS, 10.0),
            "117(4)": _row("Grievous hurt caused by a group of five or more persons on specified grounds",
                           True, False, "Court of Session", "Imprisonment up to 7 years, and fine.", 7.0),
        },
    },
    303: {
        "section": 303,
        "title": "Theft",
        "is_conditional": True,
        "condition_type": "property_value_and_restoration",
        "condition_description": (
            "Section 303(2): cognizable and non-bailable. Schedule I separately classifies theft where the value "
            "of the property is less than Rs 5,000 and the property is returned or its value restored (punishable "
            "with community service) as non-cognizable and bailable; the BNS proviso also requires that the person "
            "is convicted for the first time, which cannot be established from a complaint."
        ),
        "sub_sections": {
            "303(2)": _row("Theft", True, False, "Any Magistrate",
                           "Imprisonment up to 3 years, or fine, or both; on second or subsequent conviction, "
                           "rigorous imprisonment of 1 to 5 years and fine.", 3.0),
            "303(2) proviso": _row("Theft of property valued under Rs 5,000, upon return or restoration",
                                   False, True, "Any Magistrate", "Community service.", 0.0),
        },
    },
    304: {
        "section": 304,
        "title": "Snatching",
        "is_conditional": False,
        **_row("Snatching (Section 304(2))", True, False, "Any Magistrate",
               "Imprisonment up to 3 years, and fine.", 3.0),
    },
    305: {
        "section": 305,
        "title": "Theft in a dwelling house, or means of transportation or place of worship, etc.",
        "is_conditional": False,
        **_row("Theft in a dwelling house, means of transportation or place of worship", True, False,
               "Any Magistrate", "Imprisonment up to 7 years, and fine.", 7.0),
    },
    306: {
        "section": 306,
        "title": "Theft by clerk or servant of property in possession of master",
        "is_conditional": False,
        **_row("Theft by clerk or servant of property in possession of master or employer", True, False,
               "Any Magistrate", "Imprisonment up to 7 years, and fine.", 7.0),
    },
    309: {
        "section": 309,
        "title": "Robbery",
        "is_conditional": False,
        **_row("Robbery (Section 309(4))", True, False, "Magistrate of the first class",
               "Rigorous imprisonment up to 10 years and fine; up to 14 years if committed on a highway between "
               "sunset and sunrise. Attempt (Section 309(5)): rigorous imprisonment up to 7 years and fine. "
               "Causing hurt in committing robbery (Section 309(6)): imprisonment for life, or rigorous "
               "imprisonment up to 10 years, and fine. All rows are cognizable and non-bailable.", 10.0),
    },
    310: {
        "section": 310,
        "title": "Dacoity",
        "is_conditional": False,
        **_row("Dacoity (Section 310(2))", True, False, "Court of Session",
               "Imprisonment for life, or rigorous imprisonment up to 10 years, and fine. Other rows "
               "(Sections 310(3) to 310(6)) are also cognizable, non-bailable and triable by the Court of Session.",
               LIFE_IMPRISONMENT_YEARS, 0.0),
    },
    314: {
        "section": 314,
        "title": "Dishonest misappropriation of property",
        "is_conditional": False,
        **_row("Dishonest misappropriation of movable property", False, True, "Any Magistrate",
               "Imprisonment of not less than 6 months but up to 2 years, and fine.", 2.0, 0.5),
    },
    316: {
        "section": 316,
        "title": "Criminal breach of trust",
        "is_conditional": True,
        "condition_type": "sub_section",
        "condition_description": (
            "All sub-sections are cognizable and non-bailable, but the maximum term differs: 316(2) up to 5 years; "
            "316(3) (carrier, wharfinger or warehouse-keeper) and 316(4) (clerk or servant) up to 7 years; "
            "316(5) (public servant, banker, merchant, factor, broker, attorney or agent) imprisonment for life "
            "or up to 10 years."
        ),
        "sub_sections": {
            "316(2)": _row("Criminal breach of trust", True, False, "Magistrate of the first class",
                           "Imprisonment up to 5 years, or fine, or both.", 5.0),
            "316(3)": _row("Criminal breach of trust by a carrier, wharfinger or warehouse-keeper", True, False,
                           "Magistrate of the first class", "Imprisonment up to 7 years, and fine.", 7.0),
            "316(4)": _row("Criminal breach of trust by a clerk or servant", True, False,
                           "Magistrate of the first class", "Imprisonment up to 7 years, and fine.", 7.0),
            "316(5)": _row("Criminal breach of trust by public servant, banker, merchant or agent", True, False,
                           "Magistrate of the first class",
                           "Imprisonment for life, or imprisonment up to 10 years, and fine.", LIFE_IMPRISONMENT_YEARS),
        },
    },
    318: {
        "section": 318,
        "title": "Cheating",
        "is_conditional": True,
        "condition_type": "sub_section",
        "condition_description": (
            "Section 318(2) cheating and 318(3) cheating a person whose interest the offender is bound to protect "
            "are non-cognizable and bailable; Section 318(4) cheating and dishonestly inducing delivery of property "
            "is cognizable and non-bailable."
        ),
        "sub_sections": {
            "318(2)": _row("Cheating", False, True, "Any Magistrate",
                           "Imprisonment up to 3 years, or fine, or both.", 3.0),
            "318(3)": _row("Cheating a person whose interest the offender was bound to protect", False, True,
                           "Any Magistrate", "Imprisonment up to 5 years, or fine, or both.", 5.0),
            "318(4)": _row("Cheating and dishonestly inducing delivery of property", True, False,
                           "Magistrate of the first class", "Imprisonment up to 7 years, and fine.", 7.0),
        },
    },
    324: {
        "section": 324,
        "title": "Mischief",
        "is_conditional": True,
        "condition_type": "sub_section",
        "condition_description": (
            "Sections 324(2) to 324(4) are non-cognizable and bailable; Sections 324(5) (loss of one lakh rupees "
            "or more) and 324(6) (mischief after preparation for causing death, hurt or wrongful restraint) are "
            "cognizable and bailable. " + OPEN_LEGAL_QUESTIONS["324_value_bands"]
        ),
        "sub_sections": {
            "324(2)": _row("Mischief", False, True, "Any Magistrate",
                           "Imprisonment up to 6 months, or fine, or both.", 0.5),
            "324(3)": _row("Mischief causing loss or damage to property including Government or local authority property",
                           False, True, "Any Magistrate", "Imprisonment up to 1 year, or fine, or both.", 1.0),
            "324(4)": _row("Mischief causing loss or damage of twenty thousand rupees or more", False, True,
                           "Any Magistrate", "Imprisonment up to 2 years, or fine, or both.", 2.0),
            "324(5)": _row("Mischief causing loss or damage of one lakh rupees or more", True, True,
                           "Magistrate of the first class", "Imprisonment up to 5 years, or fine, or both.", 5.0),
            "324(6)": _row("Mischief after preparation for causing death, hurt or wrongful restraint", True, True,
                           "Magistrate of the first class", "Imprisonment up to 5 years, and fine.", 5.0),
        },
    },
    351: {
        "section": 351,
        "title": "Criminal intimidation",
        "is_conditional": True,
        "condition_type": "sub_section",
        "condition_description": (
            "All sub-sections are non-cognizable and bailable; the maximum term is 2 years under 351(2) and 351(4) "
            "and 7 years under 351(3) (threat to cause death or grievous hurt, etc.)."
        ),
        "sub_sections": {
            "351(2)": _row("Criminal intimidation", False, True, "Any Magistrate",
                           "Imprisonment up to 2 years, or fine, or both.", 2.0),
            "351(3)": _row("Criminal intimidation by threat to cause death or grievous hurt, etc.", False, True,
                           "Magistrate of the first class", "Imprisonment up to 7 years, or fine, or both.", 7.0),
            "351(4)": _row("Criminal intimidation by anonymous communication", False, True,
                           "Magistrate of the first class",
                           "Imprisonment up to 2 years, in addition to the punishment under Section 351(1).", 2.0),
        },
    },
    352: {
        "section": 352,
        "title": "Intentional insult with intent to provoke breach of peace",
        "is_conditional": False,
        **_row("Insult intended to provoke breach of the peace", False, True, "Any Magistrate",
               "Imprisonment up to 2 years, or fine, or both.", 2.0),
    },
}

for _sec, _entry in VERIFIED_SCHEDULE_I.items():
    _entry.setdefault("statutory_source", GAZETTE_SOURCE)
    _entry.setdefault("verified", True)


def get_verified_schedule_entry(sec_num: int) -> Optional[Dict[str, Any]]:
    """Returns verified Schedule I entry if transcribed from the Gazette, else None."""
    return VERIFIED_SCHEDULE_I.get(int(sec_num))


def _applicable_rows(entry: Dict[str, Any], sub_section: Optional[str]) -> List[Tuple[str, Dict[str, Any]]]:
    rows = entry.get("sub_sections")
    if not rows:
        return [(str(entry["section"]), entry)]
    if sub_section and sub_section in rows:
        return [(sub_section, rows[sub_section])]
    return list(rows.items())


def _common(rows: List[Tuple[str, Dict[str, Any]]], key: str):
    values = {row[key] for _, row in rows}
    return values.pop() if len(values) == 1 else None


def resolve_schedule_classification(sec_num: int, sub_section: Optional[str] = None) -> Dict[str, Any]:
    """
    Resolves Schedule I classification for a section, optionally for a known sub-section.
    Fields on which the applicable rows disagree are returned as None (unverified).
    """
    entry = get_verified_schedule_entry(sec_num)
    if not entry:
        return {"verified": False, "sub_section": None, "determined": False,
                "is_cognizable": None, "is_bailable": None,
                "min_punishment_years": None, "max_punishment_years": None, "rows": []}
    rows = _applicable_rows(entry, sub_section)
    return {
        "verified": True,
        "sub_section": rows[0][0] if len(rows) == 1 else None,
        "determined": len(rows) == 1,
        "is_cognizable": _common(rows, "is_cognizable"),
        "is_bailable": _common(rows, "is_bailable"),
        "min_punishment_years": _common(rows, "min_punishment_years"),
        "max_punishment_years": _common(rows, "max_punishment_years"),
        "rows": rows,
    }


def get_punishment_range_years(sec_num: int, sub_section: Optional[str] = None) -> Tuple[Optional[float], Optional[float]]:
    """Returns (min, max) punishment years for a verified section, or None where sub-sections differ."""
    res = resolve_schedule_classification(sec_num, sub_section)
    return res["min_punishment_years"], res["max_punishment_years"]


def _format_years(years: float) -> str:
    if years >= LIFE_IMPRISONMENT_YEARS:
        return "imprisonment for life"
    if years < 1.0:
        return f"{int(round(years * 12))} months"
    return f"{years:g} years"


def _row_173_3_status(label: str, row: Dict[str, Any]) -> Tuple[bool, str]:
    max_years = row["max_punishment_years"]
    if row["is_cognizable"] is False:
        return False, f"{label} is classified as NON-COGNIZABLE under BNSS Schedule I"
    if max_years == BNSS_173_3_CEILING_YEARS:
        return False, (
            f"{label} is punishable with up to {_format_years(max_years)}; on the maximum-term reading this is "
            "outside the 'less than seven years' range of Section 173(3) (interpretation pending qualified legal review)"
        )
    if max_years > BNSS_173_3_CEILING_YEARS:
        return False, (
            f"{label} is punishable with up to {_format_years(max_years)}, which exceeds the "
            "'less than seven years' range of Section 173(3)"
        )
    if max_years < BNSS_173_3_MIN_YEARS:
        return False, (
            f"{label} is punishable with up to {_format_years(max_years)}, which is below the "
            "'three years or more' range of Section 173(3)"
        )
    boundary = " on the maximum-term reading (interpretation pending qualified legal review)" \
        if max_years == BNSS_173_3_MIN_YEARS else ""
    return True, (
        f"{label} is cognizable and punishable with up to {_format_years(max_years)}, within the "
        f"'three years or more but less than seven years' range of Section 173(3){boundary}"
    )


def check_bnss_173_3_eligibility(
    sec_num: int,
    is_cognizable: Optional[bool] = None,
    sub_section: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates whether information about an offence falls within Section 173(3) BNSS:
    1. The offence must be COGNIZABLE.
    2. It must be made punishable for THREE YEARS OR MORE BUT LESS THAN SEVEN YEARS (maximum term).
    3. A preliminary enquiry requires PRIOR PERMISSION from an officer not below the rank of DSP.
    4. The preliminary enquiry is to ascertain a prima facie case within FOURTEEN DAYS; alternatively the
       officer may proceed with investigation when a prima facie case exists.

    `is_cognizable` narrows conditional entries to rows with that classification (e.g. theft once the
    value is known). `sub_section` selects a specific row. Returns conditional=True when the applicable
    rows lead to different outcomes.
    """
    entry = get_verified_schedule_entry(sec_num)
    if not entry:
        return {
            "eligible": False,
            "conditional": False,
            "reason": (
                f"BNS Section {sec_num} does not have a verified BNSS Schedule I entry in this registry. "
                "Section 173(3) BNSS applicability cannot be affirmed without verified statutory classification."
            ),
            "max_punishment": None,
            "is_cognizable": None
        }

    rows = _applicable_rows(entry, sub_section)
    if is_cognizable is not None and len(rows) > 1:
        narrowed = [(label, row) for label, row in rows if row["is_cognizable"] == is_cognizable]
        rows = narrowed or rows

    statuses = [(label, row, *_row_173_3_status(f"Section {label}", row)) for label, row in rows]
    eligible_flags = {flag for _, _, flag, _ in statuses}
    cog = _common(rows, "is_cognizable")
    max_p = _common(rows, "max_punishment_years")
    title = entry["title"]

    if eligible_flags == {True}:
        return {
            "eligible": True,
            "conditional": False,
            "reason": f"{statuses[0][3]} ({title}). {BNSS_173_3_PROCEDURE_TEXT} {BNSS_173_3_CAVEAT_TEXT}",
            "max_punishment": max_p,
            "is_cognizable": True
        }
    if eligible_flags == {False}:
        if cog is False:
            reason = (
                f"BNS Section {sec_num} ({title}) is classified as NON-COGNIZABLE under BNSS Schedule I. "
                "Section 173(3) BNSS applies only to cognizable offences; procedure is governed by Section 174 BNSS."
            )
        else:
            reason = "; ".join(r for _, _, _, r in statuses) + f" ({title})."
        return {
            "eligible": False,
            "conditional": False,
            "reason": reason,
            "max_punishment": max_p,
            "is_cognizable": cog
        }
    return {
        "eligible": False,
        "conditional": True,
        "reason": (
            f"Section 173(3) BNSS applicability to BNS Section {sec_num} ({title}) depends on the applicable "
            "sub-section or material facts: " + "; ".join(r for _, _, _, r in statuses) + "."
        ),
        "max_punishment": max_p,
        "is_cognizable": cog
    }
