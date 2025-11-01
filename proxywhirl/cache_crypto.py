"""
Credential encryption utilities for cache storage.

Provides Fernet symmetric encryption for proxy credentials at rest (L2/L3 tiers).
Uses environment variable PROXYWHIRL_CACHE_ENCRYPTION_KEY for key management.
"""

import os
from typing import Optional

from cryptography.fernet import Fernet
from pydantic import SecretStr

__all__ = [
    "CredentialEncryptor",
]


class CredentialEncryptor:
    """
    Handles encryption/decryption of proxy credentials.

    Uses Fernet symmetric encryption (AES-128-CBC + HMAC) to protect
    credentials stored in L2 (JSONL files) and L3 (SQLite database).

    Example:
        >>> encryptor = CredentialEncryptor()
        >>> encrypted = encryptor.encrypt(SecretStr("mypassword"))
        >>> decrypted = encryptor.decrypt(encrypted)
        >>> decrypted.get_secret_value()
        'mypassword'
    """

    def __init__(self, key: Optional[bytes] = None) -> None:
        """Initialize encryptor with Fernet key.

        Args:
            key: Optional Fernet key (32 url-safe base64-encoded bytes).
                If None, reads from PROXYWHIRL_CACHE_ENCRYPTION_KEY env var.
                If env var not set, generates a new key (WARNING: regenerated keys
                cannot decrypt existing cached data).

        Raises:
            ValueError: If provided key is invalid for Fernet
        """
        if key is None:
            # Try environment variable first
            env_key = os.environ.get("PROXYWHIRL_CACHE_ENCRYPTION_KEY")
            key = env_key.encode("utf-8") if env_key else Fernet.generate_key()

        try:
            self._cipher = Fernet(key)
            self.key = key
        except Exception as e:
            raise ValueError(f"Invalid Fernet key: {e}") from e

    def encrypt(self, secret: SecretStr) -> bytes:
        """Encrypt a SecretStr to bytes.

        Args:
            secret: SecretStr containing plaintext to encrypt

        Returns:
            Encrypted bytes suitable for storage in BLOB fields

        Raises:
            ValueError: If encryption fails
        """
        if not secret:
            return b""

        plaintext = secret.get_secret_value()
        if not plaintext:
            return b""

        try:
            return self._cipher.encrypt(plaintext.encode("utf-8"))
        except Exception as e:
            raise ValueError(f"Encryption failed: {e}") from e

    def decrypt(self, encrypted: bytes) -> SecretStr:
        """Decrypt encrypted bytes back to SecretStr.

        Args:
            encrypted: Encrypted bytes from storage

        Returns:
            SecretStr containing decrypted plaintext (never logs value)

        Raises:
            ValueError: If decryption fails (wrong key, corrupted data)
        """
        if not encrypted:
            return SecretStr("")

        try:
            plaintext_bytes = self._cipher.decrypt(encrypted)
            plaintext = plaintext_bytes.decode("utf-8")
            return SecretStr(plaintext)
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}") from e
