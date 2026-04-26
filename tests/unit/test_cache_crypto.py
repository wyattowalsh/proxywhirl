"""Unit tests for credential encryption.

Tests CredentialEncryptor for secure encryption/decryption of proxy credentials.
CRITICAL: 100% coverage required for security code per constitution.
"""

import pytest
from cryptography.fernet import Fernet
from pydantic import SecretStr

from proxywhirl.cache.crypto import (
    CredentialEncryptor,
    create_multi_fernet,
    get_encryption_keys,
    rotate_key,
)


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

    def test_invalid_env_key_raises_descriptive_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test invalid env var key raises ValueError with helpful message (SEC-006)."""
        # Set an invalid key in environment variable
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", "invalid-key-format")

        # Should raise ValueError with helpful message mentioning the env var
        with pytest.raises(
            ValueError,
            match=r"Invalid Fernet key format in PROXYWHIRL_CACHE_ENCRYPTION_KEY.*"
            r"32 url-safe base64-encoded bytes.*"
            r"Generate a valid key",
        ):
            CredentialEncryptor()

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


class TestCacheCryptoModule:
    """Tests for proxywhirl.cache.crypto module.

    This tests the crypto module in the cache subpackage separately.
    """

    def test_credential_encryptor_import(self) -> None:
        """Test CredentialEncryptor can be imported from cache.crypto."""
        from proxywhirl.cache.crypto import CredentialEncryptor as CacheEncryptor

        encryptor = CacheEncryptor()
        assert encryptor is not None

    def test_cache_crypto_roundtrip(self) -> None:
        """Test roundtrip encryption/decryption."""
        from proxywhirl.cache.crypto import CredentialEncryptor as CacheEncryptor

        encryptor = CacheEncryptor()
        original = SecretStr("test_password")

        encrypted = encryptor.encrypt(original)
        decrypted = encryptor.decrypt(encrypted)

        assert decrypted.get_secret_value() == "test_password"

    def test_cache_crypto_empty_secret(self) -> None:
        """Test encrypting empty/None secret."""
        from proxywhirl.cache.crypto import CredentialEncryptor as CacheEncryptor

        encryptor = CacheEncryptor()

        # Empty string
        result = encryptor.encrypt(SecretStr(""))
        assert result == b""

    def test_cache_crypto_empty_decrypt(self) -> None:
        """Test decrypting empty bytes."""
        from proxywhirl.cache.crypto import CredentialEncryptor as CacheEncryptor

        encryptor = CacheEncryptor()
        result = encryptor.decrypt(b"")
        assert result.get_secret_value() == ""

    def test_cache_crypto_invalid_key(self) -> None:
        """Test invalid key raises ValueError."""
        from proxywhirl.cache.crypto import CredentialEncryptor as CacheEncryptor

        with pytest.raises(ValueError, match="Invalid Fernet key"):
            CacheEncryptor(key=b"bad_key")

    def test_cache_crypto_wrong_key_decryption(self) -> None:
        """Test decryption with wrong key fails."""
        from proxywhirl.cache.crypto import CredentialEncryptor as CacheEncryptor

        encryptor1 = CacheEncryptor()
        encryptor2 = CacheEncryptor()  # Different auto-generated key

        encrypted = encryptor1.encrypt(SecretStr("secret"))

        with pytest.raises(ValueError, match="Decryption failed"):
            encryptor2.decrypt(encrypted)

    def test_cache_crypto_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading key from environment variable."""
        from cryptography.fernet import Fernet

        from proxywhirl.cache.crypto import CredentialEncryptor as CacheEncryptor

        test_key = Fernet.generate_key()
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", test_key.decode("utf-8"))

        encryptor = CacheEncryptor()
        assert encryptor.key == test_key

    def test_cache_crypto_generates_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test key generation when no env var."""
        from proxywhirl.cache.crypto import CredentialEncryptor as CacheEncryptor

        monkeypatch.delenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", raising=False)

        encryptor = CacheEncryptor()
        assert encryptor.key is not None
        assert len(encryptor.key) == 44  # Fernet base64 key length

    def test_cache_crypto_none_secret(self) -> None:
        """Test encrypt with None-like secret returns empty bytes."""
        from proxywhirl.cache.crypto import CredentialEncryptor as CacheEncryptor

        encryptor = CacheEncryptor()

        # Test with empty string (line 70 and 74)
        result = encryptor.encrypt(SecretStr(""))
        assert result == b""

    def test_cache_crypto_encrypt_exception(self) -> None:
        """Test encryption exception handling."""
        from unittest.mock import patch

        from proxywhirl.cache.crypto import CredentialEncryptor as CacheEncryptor

        encryptor = CacheEncryptor()

        # Force Fernet.encrypt to raise an exception
        with patch.object(encryptor._cipher, "encrypt", side_effect=Exception("Encrypt error")):
            with pytest.raises(ValueError, match="Encryption failed"):
                encryptor.encrypt(SecretStr("test_value"))


class TestKeyRotation:
    """Test key rotation functionality with MultiFernet."""

    def test_get_encryption_keys_single_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_encryption_keys with only current key."""
        test_key = Fernet.generate_key()
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", test_key.decode())
        monkeypatch.delenv("PROXYWHIRL_CACHE_KEY_PREVIOUS", raising=False)

        keys = get_encryption_keys()
        assert len(keys) == 1
        assert keys[0] == test_key

    def test_get_encryption_keys_two_keys(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_encryption_keys with current and previous keys."""
        current_key = Fernet.generate_key()
        previous_key = Fernet.generate_key()
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", current_key.decode())
        monkeypatch.setenv("PROXYWHIRL_CACHE_KEY_PREVIOUS", previous_key.decode())

        keys = get_encryption_keys()
        assert len(keys) == 2
        assert keys[0] == current_key
        assert keys[1] == previous_key

    def test_get_encryption_keys_generates_if_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_encryption_keys generates key if no env vars set."""
        monkeypatch.delenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", raising=False)
        monkeypatch.delenv("PROXYWHIRL_CACHE_KEY_PREVIOUS", raising=False)

        keys = get_encryption_keys()
        assert len(keys) == 1
        assert len(keys[0]) == 44  # Fernet base64 key length

    def test_get_encryption_keys_invalid_current_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_encryption_keys raises error for invalid current key."""
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", "invalid-key")

        with pytest.raises(
            ValueError,
            match=r"Invalid Fernet key format in PROXYWHIRL_CACHE_ENCRYPTION_KEY",
        ):
            get_encryption_keys()

    def test_get_encryption_keys_invalid_previous_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_encryption_keys raises error for invalid previous key."""
        test_key = Fernet.generate_key()
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", test_key.decode())
        monkeypatch.setenv("PROXYWHIRL_CACHE_KEY_PREVIOUS", "invalid-key")

        with pytest.raises(
            ValueError, match=r"Invalid Fernet key format in PROXYWHIRL_CACHE_KEY_PREVIOUS"
        ):
            get_encryption_keys()

    def test_get_encryption_keys_same_key_deduplicated(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_encryption_keys deduplicates if previous == current."""
        test_key = Fernet.generate_key()
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", test_key.decode())
        monkeypatch.setenv("PROXYWHIRL_CACHE_KEY_PREVIOUS", test_key.decode())

        keys = get_encryption_keys()
        assert len(keys) == 1, "Same key should not be added twice"
        assert keys[0] == test_key

    def test_create_multi_fernet(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test create_multi_fernet creates MultiFernet instance."""
        test_key = Fernet.generate_key()
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", test_key.decode())

        mf = create_multi_fernet()
        # MultiFernet has no direct type check, verify it works
        encrypted = mf.encrypt(b"test")
        decrypted = mf.decrypt(encrypted)
        assert decrypted == b"test"

    def test_create_multi_fernet_two_keys(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test create_multi_fernet with two keys encrypts with first, decrypts with both."""
        current_key = Fernet.generate_key()
        previous_key = Fernet.generate_key()
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", current_key.decode())
        monkeypatch.setenv("PROXYWHIRL_CACHE_KEY_PREVIOUS", previous_key.decode())

        mf = create_multi_fernet()

        # Encrypt with MultiFernet (uses current key)
        encrypted = mf.encrypt(b"test")
        assert mf.decrypt(encrypted) == b"test"

        # Data encrypted with previous key should still decrypt
        previous_fernet = Fernet(previous_key)
        old_encrypted = previous_fernet.encrypt(b"old_data")
        assert mf.decrypt(old_encrypted) == b"old_data"

    def test_rotate_key_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test rotate_key moves current to previous and sets new key."""
        import os

        current_key = Fernet.generate_key().decode()
        new_key = Fernet.generate_key().decode()

        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", current_key)

        rotate_key(new_key)

        assert os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"] == new_key
        assert os.environ["PROXYWHIRL_CACHE_KEY_PREVIOUS"] == current_key

    def test_rotate_key_no_current(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test rotate_key when no current key exists."""
        import os

        monkeypatch.delenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", raising=False)
        monkeypatch.delenv("PROXYWHIRL_CACHE_KEY_PREVIOUS", raising=False)
        new_key = Fernet.generate_key().decode()

        rotate_key(new_key)

        assert os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"] == new_key
        # Previous key should not be set since there was no current key
        assert "PROXYWHIRL_CACHE_KEY_PREVIOUS" not in os.environ

    def test_rotate_key_invalid_key(self) -> None:
        """Test rotate_key raises error for invalid new key."""
        with pytest.raises(ValueError, match=r"Invalid new key format"):
            rotate_key("invalid-key")

    def test_encryptor_uses_multi_fernet(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test CredentialEncryptor uses MultiFernet when no key provided."""
        current_key = Fernet.generate_key()
        previous_key = Fernet.generate_key()
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", current_key.decode())
        monkeypatch.setenv("PROXYWHIRL_CACHE_KEY_PREVIOUS", previous_key.decode())

        encryptor = CredentialEncryptor()

        # Should encrypt with current key
        secret = SecretStr("test_password")
        encrypted = encryptor.encrypt(secret)
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted.get_secret_value() == "test_password"

        # Should decrypt data encrypted with previous key
        previous_fernet = Fernet(previous_key)
        old_encrypted = previous_fernet.encrypt(b"old_password")
        old_decrypted = encryptor.decrypt(old_encrypted)
        assert old_decrypted.get_secret_value() == "old_password"

    def test_encryptor_backward_compatibility(self) -> None:
        """Test CredentialEncryptor with explicit key still uses Fernet."""
        test_key = Fernet.generate_key()
        encryptor = CredentialEncryptor(key=test_key)

        secret = SecretStr("test")
        encrypted = encryptor.encrypt(secret)
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted.get_secret_value() == "test"

    def test_key_rotation_end_to_end(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test full key rotation workflow end-to-end."""
        import os

        # Step 1: Start with one key
        key1 = Fernet.generate_key().decode()
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", key1)
        monkeypatch.delenv("PROXYWHIRL_CACHE_KEY_PREVIOUS", raising=False)

        encryptor1 = CredentialEncryptor()
        secret1 = SecretStr("original_password")
        encrypted1 = encryptor1.encrypt(secret1)

        # Step 2: Rotate to new key
        key2 = Fernet.generate_key().decode()
        rotate_key(key2)

        # Step 3: Create new encryptor with rotated keys
        encryptor2 = CredentialEncryptor()

        # Should decrypt old data (encrypted with key1)
        decrypted1 = encryptor2.decrypt(encrypted1)
        assert decrypted1.get_secret_value() == "original_password"

        # Should encrypt new data with key2
        secret2 = SecretStr("new_password")
        encrypted2 = encryptor2.encrypt(secret2)
        decrypted2 = encryptor2.decrypt(encrypted2)
        assert decrypted2.get_secret_value() == "new_password"

        # Step 4: Verify keys are set correctly
        assert os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"] == key2
        assert os.environ["PROXYWHIRL_CACHE_KEY_PREVIOUS"] == key1
