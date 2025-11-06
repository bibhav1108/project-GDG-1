# file: parsing/validators.py
import re
from typing import Tuple
from dateutil import parser as dateparser

# ------------------------------
# Regex patterns for validation
# ------------------------------
EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE = re.compile(r"^\+?[0-9 ()-]{7,}$")
PINCODE = re.compile(r"^[0-9]{5,6}$")
NUMERIC = re.compile(r"^[0-9]+(\.[0-9]+)?$")
GENDER = re.compile(r"^(male|female|other|m|f|o)$", re.IGNORECASE)
NAME = re.compile(r"^[A-Za-z .'-]{2,}$")

# ------------------------------
# Core validation functions
# ------------------------------

def validate_email(s: str) -> Tuple[bool, float]:
    """Validate email addresses."""
    ok = bool(s and EMAIL.match(s.strip()))
    return ok, 0.98 if ok else 0.0


def validate_phone(s: str) -> Tuple[bool, float]:
    """Validate phone numbers (10+ digits)."""
    if not s:
        return False, 0.0
    digits = re.sub(r"\D", "", s)
    ok = len(digits) >= 10
    return ok, 0.95 if ok else 0.0


def validate_postal(s: str) -> Tuple[bool, float]:
    """Validate postal codes (5–6 digits)."""
    ok = bool(s and PINCODE.match(s.strip()))
    return ok, 0.9 if ok else 0.0


def parse_date(s: str) -> Tuple[str, float]:
    """Try parsing flexible date formats."""
    if not s:
        return "", 0.0
    try:
        dt = dateparser.parse(s, dayfirst=True, fuzzy=True)
        return dt.strftime("%Y-%m-%d"), 0.9
    except Exception:
        return "", 0.0


def validate_name(s: str) -> Tuple[bool, float]:
    """Validate person name fields."""
    ok = bool(s and NAME.match(s.strip()))
    return ok, 0.9 if ok else 0.0


def validate_gender(s: str) -> Tuple[bool, float]:
    """Validate gender (male/female/other)."""
    ok = bool(s and GENDER.match(s.strip().lower()))
    return ok, 0.95 if ok else 0.0


def validate_numeric(s: str) -> Tuple[bool, float]:
    """Validate numeric fields like fees or IDs."""
    ok = bool(s and NUMERIC.match(s.strip()))
    return ok, 0.9 if ok else 0.0


def validate_text(s: str) -> Tuple[bool, float]:
    """Generic fallback for non-empty text fields."""
    ok = bool(s and len(s.strip()) > 1)
    return ok, 0.8 if ok else 0.0


# ------------------------------
# Central dispatcher
# ------------------------------

def validate_field(field: str, value: str) -> Tuple[bool, float]:
    """
    Unified validation entry point.
    Returns (is_valid, confidence) for a given field name and value.
    """
    if not value:
        return False, 0.0

    field = field.lower().strip()
    if "email" in field:
        return validate_email(value)
    if any(k in field for k in ["phone", "contact", "mobile"]):
        return validate_phone(value)
    if any(k in field for k in ["postal", "pincode", "zip"]):
        return validate_postal(value)
    if "date" in field or "dob" in field:
        parsed, conf = parse_date(value)
        return bool(parsed), conf
    if any(k in field for k in ["gender", "sex"]):
        return validate_gender(value)
    if any(k in field for k in ["fees", "amount", "id", "year"]):
        return validate_numeric(value)
    if any(k in field for k in ["name", "father", "mother"]):
        return validate_name(value)
    if any(k in field for k in ["address", "city", "state", "country", "course", "school", "religion", "category", "nationality", "blood"]):
        return validate_text(value)

    # Default fallback
    return validate_text(value)
