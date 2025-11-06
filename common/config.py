import json
import os
from pathlib import Path
import yaml

class Settings:
    def __init__(self, path: str = "config/settings.yaml"):
        self._raw = {}
        with open(path, "r", encoding="utf-8") as f:
            self._raw = yaml.safe_load(f)
        # Allow env overrides
        enc_env = os.getenv("DOCUFILL_ENCRYPTION")
        if enc_env is not None:
            try:
                self._raw["datastore"]["encrypt"] = bool(int(enc_env))
            except Exception:
                pass

    def get(self, dotted: str, default=None):
        cur = self._raw
        for part in dotted.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return default
        return cur

    def as_json(self):
        return json.dumps(self._raw, indent=2)

settings = Settings()
