import os
from typing import Optional
from cryptography.fernet import Fernet

def get_fernet(enable: bool) -> Optional[Fernet]:
    if not enable:
        return None
    key = os.environ.get("DOCUFILL_FERNET_KEY")
    if not key:
        key = Fernet.generate_key().decode("utf-8")
        # Persist key to user env for future sessions (simple approach)
        os.environ["DOCUFILL_FERNET_KEY"] = key
    return Fernet(key.encode("utf-8"))
