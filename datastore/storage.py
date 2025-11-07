import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger
from common.config import settings
from common.utils import ensure_dir, hash_string
from datastore.crypto import get_fernet

BASE_DIR = Path(os.path.expanduser(settings.get("datastore.base_dir", "~/.docufill_ai")))
RECORDS_DIR = BASE_DIR / "records"
PROFILES_DIR = BASE_DIR / "profiles"

ensure_dir(str(RECORDS_DIR))
ensure_dir(str(PROFILES_DIR))

FERNET = get_fernet(settings.get("datastore.encrypt", False))

def _maybe_encrypt(s: str) -> str:
    if FERNET:
        return FERNET.encrypt(s.encode("utf-8")).decode("utf-8")
    return s

def _maybe_decrypt(s: str) -> str:
    if FERNET:
        return FERNET.decrypt(s.encode("utf-8")).decode("utf-8")
    return s

def save_record(record: Dict[str, Any]) -> Path:
    key = hash_string(json.dumps(record, sort_keys=True))
    out = RECORDS_DIR / f"{key}.json"
    raw = json.dumps(record, indent=2)
    buf = _maybe_encrypt(raw)
    out.write_text(buf, encoding="utf-8")
    logger.info("Saved record {}", out)
    return out

def load_record(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    raw = _maybe_decrypt(text)
    return json.loads(raw)

def save_profile(domain: str, profile: Dict[str, Any]) -> Path:
    out = PROFILES_DIR / f"{domain}.json"
    out.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    logger.info("Saved form profile {}", out)
    return out

def load_profile(domain: str) -> Optional[Dict[str, Any]]:
    p = PROFILES_DIR / f"{domain}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

