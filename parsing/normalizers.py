import re
from typing import Dict
from common.utils import normalize_whitespace

def title_case_name(s: str) -> str:
    s = normalize_whitespace(s)
    return s.title()

def normalize_phone(s: str) -> str:
    if not s:
        return s
    digits = re.sub(r"\D", "", s)
    # Attempt E.164 for India by default if 10 digits
    if len(digits) == 10:
        return "+91" + digits
    if not digits.startswith("+" ) and digits:
        return "+" + digits
    return digits

def split_address(full: str) -> Dict[str, str]:
    full = normalize_whitespace(full or "")
    parts = [p.strip() for p in re.split(r"[,\n]", full) if p.strip()]
    addr1 = parts[0] if parts else ""
    addr2 = parts[1] if len(parts) > 1 else ""
    return {"address_line1": addr1, "address_line2": addr2}
