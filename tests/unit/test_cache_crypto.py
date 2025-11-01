"""Unit tests for credential encryption.

Tests CredentialEncryptor for secure encryption/decryption of proxy credentials.
CRITICAL: 100% coverage required for security code per constitution.
"""

import os

import pytest
from pydantic import SecretStr

from proxywhirl.cache_crypto import CredentialEncryptor


class TestCredentialEncryptor:
    """Test Fernet-based credential encryption."""

    def test_encrypt_decrypt_roundtrip(self) -> None:
        """Test encryption and decryption roundtrip."""
        encryptor = CredentialEncryptor()
        original = SecretStr("my_secret_password")

        # Encrypt
        encrypted = encryptor.encrypt(original)
        assert isinstance(encrypted, bytes), "Encrypted should be bytes"
        assert b"my_secret_password" not in encrypted, "Plaintext should not be in encrypted"

        # Decrypt
        decrypted = encryptor.decrypt(encrypted)
        assert isinstance(decrypted, SecretStr), "Decrypted should be SecretStr"
        assert decrypted.get_secret_value() == "my_secret_password"

    def test_encrypt_empty_string(self) -> None:
        """Test encrypting empty string returns empty bytes."""
        encryptor = CredentialEncryptor()
        encrypted = encryptor.encrypt(SecretStr(""))
        assert encrypted == b"", "Empty string should encrypt to empty bytes"

    def test_decrypt_empty_bytes(self) -> None:
        """Test decrypting empty bytes returns empty SecretStr."""
        encryptor = CredentialEncryptor()
        decrypted = encryptor.decrypt(b"")
        assert decrypted.get_secret_value() == "", "Empty bytes should decrypt to empty string"

    def test_encryptor_from_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test encryptor loads key from environment variable."""
        from cryptography.fernet import Fernet

        # Generate a valid key
        test_key = Fernet.generate_key()
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", test_key.decode("utf-8"))

        encryptor = CredentialEncryptor()
        assert encryptor.key == test_key, "Should load key from env var"

    def test_encryptor_generates_key_if_no_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test encryptor generates key if env var not set."""
        monkeypatch.delenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", raising=False)

        encryptor = CredentialEncryptor()
        assert encryptor.key is not None, "Should generate key"
        assert len(encryptor.key) == 44, "Fernet key should be 44 bytes (base64 encoded)"

    def test_invalid_key_raises_error(self) -> None:
        """Test invalid Fernet key raises ValueError."""
        with pytest.raises(ValueError, match="Invalid Fernet key"):
            CredentialEncryptor(key=b"invalid_key")

    def test_decrypt_with_wrong_key_raises_error(self) -> None:
        """Test decrypting with wrong key raises ValueError."""
        encryptor1 = CredentialEncryptor()
        encryptor2 = CredentialEncryptor()  # Different key

        encrypted = encryptor1.encrypt(SecretStr("secret"))

        with pytest.raises(ValueError, match="Decryption failed"):
            encryptor2.decrypt(encrypted)


class TestCredentialRedaction:
    """Test that credentials are never exposed in logs.

    CRITICAL: 100% coverage required for security code.
    """

    def test_secret_str_not_logged(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test SecretStr never appears in log output."""
        import logging

        caplog.set_level(logging.DEBUG)

        secret = SecretStr("super_secret_password")

        # Log the secret (should be automatically redacted by Pydantic)
        logging.debug(f"Secret value: {secret}")

        # Verify plaintext not in logs
        log_text = " ".join(record.message for record in caplog.records)
        assert "super_secret_password" not in log_text, "Plaintext should not be in logs"
        assert "**" in log_text, "Secret should be redacted with asterisks"

    def test_encrypted_credentials_not_in_logs(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that encrypted credentials are not logged."""
        import logging

        caplog.set_level(logging.DEBUG)

        encryptor = CredentialEncryptor()
        secret = SecretStr("password123")
        encrypted = encryptor.encrypt(secret)

        # Log encrypted value
        logging.debug(f"Encrypted: {encrypted}")

        # Verify password not in logs
        log_text = " ".join(record.message for record in caplog.records)
        assert "password123" not in log_text, "Plaintext password should never be logged"
