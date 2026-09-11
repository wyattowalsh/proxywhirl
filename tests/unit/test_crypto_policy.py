"""Unit tests for durable crypto key policy (no ephemeral Fernet keys)."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest


class TestEncryptionKeyPolicy:
    def test_get_encryption_keys_requires_env(self) -> None:
        from proxywhirl.cache.crypto import get_encryption_keys

        env = {
            k: v
            for k, v in os.environ.items()
            if k
            not in {
                "PROXYWHIRL_CACHE_ENCRYPTION_KEY",
                "PROXYWHIRL_CACHE_KEY_PREVIOUS",
                "PROXYWHIRL_ENCRYPTION_KEY",
            }
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="PROXYWHIRL_CACHE_ENCRYPTION_KEY"):
                get_encryption_keys()

    def test_credential_encryptor_requires_configured_key(self) -> None:
        from proxywhirl.cache.crypto import CredentialEncryptor

        env = {
            k: v
            for k, v in os.environ.items()
            if k
            not in {
                "PROXYWHIRL_CACHE_ENCRYPTION_KEY",
                "PROXYWHIRL_CACHE_KEY_PREVIOUS",
                "PROXYWHIRL_ENCRYPTION_KEY",
            }
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="PROXYWHIRL_CACHE_ENCRYPTION_KEY"):
                CredentialEncryptor()

    def test_deprecated_encryption_key_alias(self) -> None:
        """PROXYWHIRL_ENCRYPTION_KEY is accepted when canonical cache key is absent."""
        from cryptography.fernet import Fernet

        from proxywhirl.cache.crypto import CredentialEncryptor, get_encryption_keys

        alias_key = Fernet.generate_key().decode()
        env = {
            k: v
            for k, v in os.environ.items()
            if k
            not in {
                "PROXYWHIRL_CACHE_ENCRYPTION_KEY",
                "PROXYWHIRL_CACHE_KEY_PREVIOUS",
                "PROXYWHIRL_ENCRYPTION_KEY",
            }
        }
        env["PROXYWHIRL_ENCRYPTION_KEY"] = alias_key
        with patch.dict(os.environ, env, clear=True):
            keys = get_encryption_keys()
            assert keys[0] == alias_key.encode("utf-8")
            encryptor = CredentialEncryptor()
            assert encryptor.key == alias_key.encode("utf-8")

    def test_encryptor_with_explicit_key_roundtrip(self) -> None:
        from cryptography.fernet import Fernet
        from pydantic import SecretStr

        from proxywhirl.cache.crypto import CredentialEncryptor

        key = Fernet.generate_key()
        encryptor = CredentialEncryptor(key=key)
        token = encryptor.encrypt(SecretStr("s3cret"))
        assert encryptor.decrypt(token).get_secret_value() == "s3cret"
