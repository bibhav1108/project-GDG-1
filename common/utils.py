import hashlib
import os
import re
from pathlib import Path

MASK_TOKEN = "•"

def safe_basename(path: str) -> str:
    return os.path.basename(path).replace("\\", "/")

def mask_value(value: str, left: int = 3, right: int = 2) -> str:
    if not value:
        return value
    s = str(value)
    if len(s) <= left + right:
        return MASK_TOKEN * len(s)
    return s[:left] + MASK_TOKEN * (len(s) - left - right) + s[-right:]

def hash_string(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]

def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()
