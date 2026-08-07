from __future__ import annotations

from cryptography.fernet import Fernet
from loguru import logger


# Fallback key for dev/testing if env var is unconfigured
DEFAULT_FERNET_KEY = b"AxTbdHScaozKcDuDD87m1jplJ6tq1l5o0jsUDXtdLEg="


class CryptoService:
    def __init__(self, key: str | bytes | None = None) -> None:
        if not key:
            self.fernet = Fernet(DEFAULT_FERNET_KEY)
        else:
            if isinstance(key, str):
                key_bytes = key.encode("utf-8")
            else:
                key_bytes = key
            try:
                self.fernet = Fernet(key_bytes)
            except Exception as exc:
                logger.warning(f"Invalid Fernet key provided ({exc}). Using default key.")
                self.fernet = Fernet(DEFAULT_FERNET_KEY)

    def encrypt_token(self, plain_token: str) -> str:
        if not plain_token:
            return ""
        encrypted = self.fernet.encrypt(plain_token.encode("utf-8"))
        return encrypted.decode("utf-8")

    def decrypt_token(self, encrypted_token: str) -> str:
        if not encrypted_token:
            return ""
        try:
            decrypted = self.fernet.decrypt(encrypted_token.encode("utf-8"))
            return decrypted.decode("utf-8")
        except Exception as exc:
            logger.error(f"Failed to decrypt OAuth refresh token: {exc}")
            return ""
