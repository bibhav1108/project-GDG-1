# file: ai_extraction/normalize.py
from typing import Dict, Any
from rapidfuzz import process, fuzz
from common.config import settings

# Canonical schema keys (aligned with canonical_schema.json)
CANONICAL_KEYS = [
    "full_name", "father_name", "mother_name", "date_of_birth", "gender", "email", "phone",
    "alternate_contact", "address_line1", "address_line2", "city", "state", "postal_code",
    "country", "university_id", "previous_school", "course_applying_for", "academic_year",
    "fees", "nationality", "religion", "category", "blood_group", "emergency_contact"
]

# Expanded alias map for fuzzy name normalization
ALIASES = {
    # --- Name variants ---
    "name": "full_name",
    "applicant_name": "full_name",
    "student_name": "full_name",
    "candidate_name": "full_name",

    # --- Contact variants ---
    "contact_no": "phone",
    "contact_number": "phone",
    "mobile": "phone",
    "guardian_mobile": "phone",
    "alternate_contact_number": "alternate_contact",
    "alt_contact": "alternate_contact",
    "alternate_mobile": "alternate_contact",

    # --- Email variants ---
    "mail_id": "email",
    "email_address": "email",
    "mail": "email",
    "mailid": "email",

    # --- Address variants ---
    "permanent_address": "address_line1",
    "perm_address": "address_line1",
    "address": "address_line1",
    "alternate_address": "address_line2",
    "alt_address": "address_line2",
    "city_name": "city",
    "town": "city",
    "country_name": "country",

    # --- Postal code variants ---
    "pincode": "postal_code",
    "zip": "postal_code",
    "pin": "postal_code",

    # --- Academic / course ---
    "course_applied_for": "course_applying_for",
    "course_applied": "course_applying_for",
    "course": "course_applying_for",
    "academic_session": "academic_year",
    "session": "academic_year",
    "academic_duration": "academic_year",
    "fee": "fees",
    "fee_amount": "fees",
    "amount": "fees",

    # --- DOB / ID ---
    "dob": "date_of_birth",
    "birth_date": "date_of_birth",
    "d_o_b": "date_of_birth",
    "roll_no": "university_id",
    "student_id": "university_id",
    "univ_id": "university_id",
    "previous_institution": "previous_school",
}


def map_alias(key: str) -> str:
    """Map AI-generated or OCR keys to canonical schema names."""
    k = key.lower().strip()
    if k in ALIASES:
        return ALIASES[k]
    best = process.extractOne(k, CANONICAL_KEYS, scorer=fuzz.QRatio)
    if best and best[1] >= 80:
        return best[0]
    return key


def filter_to_schema(ai_data: Dict[str, Any], schema_fields: list[str]) -> Dict[str, Any]:
    """Filters AI output to only include canonical schema fields."""
    filtered = {}
    for field in schema_fields:
        entry = ai_data.get(field, {})
        if isinstance(entry, dict):
            filtered[field] = {
                "value": entry.get("value", ""),
                "confidence": float(entry.get("confidence", 0.0) or 0.0),
                "rationale": entry.get("rationale", "")
            }
        else:
            filtered[field] = {"value": str(entry), "confidence": 0.0, "rationale": ""}
    return filtered


def normalize_ai_output(ai_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize raw AI dictionary output (from Gemini) into a flat structure
    aligned to canonical schema, resolving aliases and preserving confidence.
    """
    out = {k: "" for k in CANONICAL_KEYS}
    overall_conf = 0.0

    for key, wrap in ai_dict.items():
        mapped = map_alias(key)
        if isinstance(wrap, dict):
            val = wrap.get("value", "")
            conf = float(wrap.get("confidence", 0.0) or 0.0)
        else:
            val = str(wrap) if wrap is not None else ""
            conf = 0.0

        if mapped in out:
            out[mapped] = val
            overall_conf = max(overall_conf, conf)

    out["confidence"] = round(overall_conf, 3)
    out["extraction_method"] = "ocr+ai"
    return out
