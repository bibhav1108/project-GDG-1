import os
from typing import Optional
from cryptography.fernet import Fernet

def get_fernet(enable: bool) -> Optional[Fernet]:
    """
    Returns a Fernet instance if encryption is enabled.
    Generates a new key if none exists in environment.
    """
    if not enable:
        return None

    key = os.environ.get("DOCUFILL_FERNET_KEY")

    # If no key is stored yet, create and cache it in the env
    if not key:
        key = Fernet.generate_key().decode("utf-8")
        os.environ["DOCUFILL_FERNET_KEY"] = key

    # Return a valid Fernet instance
    return Fernet(key.encode("utf-8"))
