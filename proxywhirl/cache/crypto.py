"""
Credential encryption utilities for cache storage.

Provides Fernet symmetric encryption for proxy credentials at rest (L2/L3 tiers).
Uses environment variable PROXYWHIRL_CACHE_ENCRYPTION_KEY for key management.
Supports key rotation via MultiFernet with PROXYWHIRL_CACHE_KEY_PREVIOUS.
"""

from __future__ import annotations

import os

from cryptography.fernet import Fernet, MultiFernet
from pydantic import SecretStr

__all__ = [
    "CredentialEncryptor",
    "get_encryption_keys",
    "create_multi_fernet",
    "rotate_key",
]


def get_encryption_keys() -> list[bytes]:
    """Get all valid encryption keys for MultiFernet.

    Returns keys in priority order: current key first, then previous key.
    This allows decryption of data encrypted with either key while
    always encrypting new data with the current (first) key.

    Returns:
        List of Fernet keys as bytes. Always contains at least one key.
        First key is current, subsequent keys are for backward compatibility.

    Raises:
        ValueError: If any key has invalid Fernet format

    Example:
        >>> keys = get_encryption_keys()
        >>> len(keys)  # 1 or 2 depending on env vars
        1
    """
    keys: list[bytes] = []

    # Get current key
    current_key_str = os.environ.get("PROXYWHIRL_CACHE_ENCRYPTION_KEY")
    if current_key_str:
        current_key = (
            current_key_str.encode("utf-8") if isinstance(current_key_str, str) else current_key_str
        )
        try:
            # Validate key format
            Fernet(current_key)
            keys.append(current_key)
        except Exception as e:
            raise ValueError(
                f"Invalid Fernet key format in PROXYWHIRL_CACHE_ENCRYPTION_KEY: {e}. "
                "Key must be 32 url-safe base64-encoded bytes. "
                "Generate a valid key with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            ) from e
    else:
        # No current key, generate one
        keys.append(Fernet.generate_key())

    # Get previous key if exists
    previous_key_str = os.environ.get("PROXYWHIRL_CACHE_KEY_PREVIOUS")
    if previous_key_str:
        previous_key = (
            previous_key_str.encode("utf-8")
            if isinstance(previous_key_str, str)
            else previous_key_str
        )
        try:
            # Validate key format
            Fernet(previous_key)
            # Only add if different from current key
            if previous_key != keys[0]:
                keys.append(previous_key)
        except Exception as e:
            raise ValueError(
                f"Invalid Fernet key format in PROXYWHIRL_CACHE_KEY_PREVIOUS: {e}. "
                "Key must be 32 url-safe base64-encoded bytes. "
                "Generate a valid key with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            ) from e

    return keys


def create_multi_fernet() -> MultiFernet:
    """Create MultiFernet instance with all valid encryption keys.

    MultiFernet tries keys in order for decryption (newest first).
    All new encryptions use the first (current) key.

    Returns:
        MultiFernet instance configured with current and previous keys

    Raises:
        ValueError: If any key has invalid format

    Example:
        >>> mf = create_multi_fernet()
        >>> encrypted = mf.encrypt(b"secret")
        >>> mf.decrypt(encrypted)
        b'secret'
    """
    keys = get_encryption_keys()
    fernets = [Fernet(key) for key in keys]
    return MultiFernet(fernets)


def rotate_key(new_key: str) -> None:
    """Rotate encryption keys by setting new current key.

    This function updates environment variables to perform key rotation:
    - Current key moves to PROXYWHIRL_CACHE_KEY_PREVIOUS
    - New key becomes PROXYWHIRL_CACHE_ENCRYPTION_KEY

    This allows gradual migration: new data uses new key, old data
    can still be decrypted with previous key.

    Args:
        new_key: New Fernet key as base64-encoded string

    Raises:
        ValueError: If new_key has invalid Fernet format

    Example:
        >>> from cryptography.fernet import Fernet
        >>> new_key = Fernet.generate_key().decode()
        >>> rotate_key(new_key)
    """
    # Validate new key format
    try:
        new_key_bytes = new_key.encode("utf-8")
        Fernet(new_key_bytes)
    except Exception as e:
        raise ValueError(
            f"Invalid new key format: {e}. "
            "Key must be 32 url-safe base64-encoded bytes. "
            "Generate a valid key with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        ) from e

    # Move current key to previous
    current_key = os.environ.get("PROXYWHIRL_CACHE_ENCRYPTION_KEY")
    if current_key:
        os.environ["PROXYWHIRL_CACHE_KEY_PREVIOUS"] = current_key

    # Set new key as current
    os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"] = new_key


class CredentialEncryptor:
    """
    Handles encryption/decryption of proxy credentials with key rotation support.

    Uses Fernet symmetric encryption (AES-128-CBC + HMAC) to protect
    credentials stored in L2 (JSONL files) and L3 (SQLite database).
    Supports gradual key rotation via MultiFernet using both current
    and previous keys.

    Example:
        >>> encryptor = CredentialEncryptor()
        >>> encrypted = encryptor.encrypt(SecretStr("mypassword"))
        >>> decrypted = encryptor.decrypt(encrypted)
        >>> decrypted.get_secret_value()
        'mypassword'
    """

    def __init__(self, key: bytes | None = None) -> None:
        """Initialize encryptor with Fernet key or MultiFernet.

        Args:
            key: Optional Fernet key (32 url-safe base64-encoded bytes).
                If None, uses get_encryption_keys() to load current and
                previous keys from environment variables. If no env vars set,
                generates a new key (WARNING: regenerated keys cannot decrypt
                existing cached data).

        Raises:
            ValueError: If provided key is invalid for Fernet
        """
        if key is None:
            # Use MultiFernet with all available keys
            self._cipher = create_multi_fernet()
            # Store the current (first) key for backward compatibility
            keys = get_encryption_keys()
            self.key = keys[0]
        else:
            # Single key provided, use regular Fernet
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
