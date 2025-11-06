from typing import Dict, Any
from rapidfuzz import process, fuzz
from common.config import settings

CANONICAL_KEYS = [
    "full_name","email","phone","address_line1","address_line2","city","state","postal_code",
    "country","dob","id_number","source_file","page","confidence","extraction_method"
]

ALIASES = {
    "mail_id": "email",
    "e-mail": "email",
    "guardian_mobile": "phone",
    "mobile": "phone",
    "pin": "postal_code",
    "zip": "postal_code",
    "roll_no": "id_number",
}

def map_alias(key: str) -> str:
    k = key.lower().strip()
    if k in ALIASES:
        return ALIASES[k]
    # Fuzzy fallback
    best = process.extractOne(k, CANONICAL_KEYS, scorer=fuzz.QRatio)
    if best and best[1] >= 80:
        return best[0]
    return key

def normalize_ai_output(ai_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    ai_dict is expected as:
      { field: { "value": str, "confidence": float, "rationale": str }, ... }
    This returns a flat dict aligned to canonical keys and attaches method+confidence.
    """
    out = {k: "" for k in CANONICAL_KEYS}
    for key, wrap in ai_dict.items():
        mapped = map_alias(key)
        if isinstance(wrap, dict):
            val = wrap.get("value", "")
            conf = float(wrap.get("confidence", 0.0) or 0.0)
        else:
            val = str(wrap) if wrap is not None else ""
            conf = 0.0
        out[mapped] = val
        # store overall confidence and method if empty
        if "confidence" not in out or not out["confidence"]:
            out["confidence"] = conf
    out["extraction_method"] = out.get("extraction_method") or "ocr+ai"
    # keep source_file/page if present in ai output
    return out
