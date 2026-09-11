"""Unit tests for CredentialsManager SecretStr encrypt/export."""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet
from pydantic import SecretStr

from proxywhirl.credentials_manager import Credential, CredentialsManager
from proxywhirl.utils import decrypt_credentials


@pytest.fixture
def encryption_key() -> str:
    return Fernet.generate_key().decode()


@pytest.fixture
def manager(encryption_key: str) -> CredentialsManager:
    mgr = CredentialsManager()
    mgr.set_encryption_key(encryption_key)
    return mgr


@pytest.fixture
def sample_credential() -> Credential:
    return Credential(
        name="proxy-auth",
        username=SecretStr("alice"),
        password=SecretStr("s3cret-pass"),
        tags=["prod"],
    )


class TestCredentialsManagerEncrypt:
    def test_encrypt_decrypt_roundtrip(
        self,
        manager: CredentialsManager,
        sample_credential: Credential,
        encryption_key: str,
    ) -> None:
        manager.add_credential(sample_credential)

        encrypted = manager.encrypt_credential("proxy-auth")
        assert "alice" not in encrypted
        assert "s3cret-pass" not in encrypted
        assert "*" not in encrypted

        pair = manager.decrypt_credential(encrypted)
        assert pair == ("alice", "s3cret-pass")

        # Also verify via utils against the same key
        assert decrypt_credentials(encrypted, encryption_key) == "alice:s3cret-pass"

    def test_encrypt_uses_secret_values_not_asterisks(
        self,
        manager: CredentialsManager,
        sample_credential: Credential,
    ) -> None:
        """Regression: f\"{SecretStr}\" must not encrypt redacted asterisks."""
        manager.add_credential(sample_credential)

        encrypted = manager.encrypt_credential("proxy-auth")
        username, password = manager.decrypt_credential(encrypted)  # type: ignore[misc]

        assert username == "alice"
        assert password == "s3cret-pass"
        assert "*" not in username
        assert "*" not in password
        # Redacted SecretStr repr would look like this if .get_secret_value() were skipped
        assert username != "**********"
        assert password != "**********"

    def test_encrypt_requires_key(self, sample_credential: Credential) -> None:
        mgr = CredentialsManager()
        mgr.add_credential(sample_credential)
        with pytest.raises(ValueError, match="Encryption key not set"):
            mgr.encrypt_credential("proxy-auth")

    def test_encrypt_missing_credential(self, manager: CredentialsManager) -> None:
        with pytest.raises(ValueError, match="Credential not found"):
            manager.encrypt_credential("missing")


class TestCredentialsManagerExport:
    def test_export_encrypted_uses_secret_values(
        self,
        manager: CredentialsManager,
        sample_credential: Credential,
        encryption_key: str,
    ) -> None:
        manager.add_credential(sample_credential)

        exported = manager.export_credentials(encrypt=True)
        assert "proxy-auth" in exported
        encrypted_password = exported["proxy-auth"]["password"]
        assert isinstance(encrypted_password, str)
        assert "s3cret-pass" not in encrypted_password
        assert "*" not in encrypted_password

        decrypted = decrypt_credentials(encrypted_password, encryption_key)
        assert decrypted == "alice:s3cret-pass"

    def test_export_plaintext_includes_secret_values(
        self,
        manager: CredentialsManager,
        sample_credential: Credential,
    ) -> None:
        manager.add_credential(sample_credential)

        exported = manager.export_credentials(encrypt=False)
        assert exported["proxy-auth"]["username"] == "alice"
        assert exported["proxy-auth"]["password"] == "s3cret-pass"

    def test_to_dict_exposes_secret_values(self, sample_credential: Credential) -> None:
        data = sample_credential.to_dict()
        assert data["username"] == "alice"
        assert data["password"] == "s3cret-pass"
        assert "*" not in data["username"]
        assert "*" not in data["password"]


class TestCredentialsManagerLifecycle:
    def test_add_overwrite_list_and_remove(self, sample_credential: Credential) -> None:
        manager = CredentialsManager()
        manager.add_credential(sample_credential)

        assert manager.has_credential("proxy-auth")
        assert manager.list_credentials() == ["proxy-auth"]
        assert manager.get_credential("proxy-auth") is sample_credential

        replacement = Credential(
            name="proxy-auth",
            username=SecretStr("bob"),
            password=SecretStr("replacement-pass"),
        )
        manager.add_credential(replacement)

        assert manager.get_credential("proxy-auth") is replacement
        assert manager.remove_credential("proxy-auth") is True
        assert manager.remove_credential("proxy-auth") is False
        assert manager.list_credentials() == []

    def test_find_by_tag_and_clear(self, sample_credential: Credential) -> None:
        manager = CredentialsManager()
        other = Credential(
            name="staging-auth",
            username=SecretStr("bob"),
            password=SecretStr("staging-pass"),
            tags=["staging"],
        )
        manager.add_credential(sample_credential)
        manager.add_credential(other)

        assert manager.find_by_tag("prod") == [sample_credential]
        assert manager.find_by_tag("missing") == []

        manager.clear()
        assert manager.list_credentials() == []


class TestCredentialsManagerDecryptionFailures:
    def test_decrypt_without_key_returns_none(self) -> None:
        manager = CredentialsManager()

        assert manager.decrypt_credential("not-an-encrypted-value") is None

    def test_decrypt_rejects_plaintext_without_separator(
        self,
        manager: CredentialsManager,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            "proxywhirl.credentials_manager.decrypt_credentials",
            lambda encrypted, key: "missing-separator",
        )

        assert manager.decrypt_credential("encrypted-value") is None

    def test_decrypt_failure_returns_none(
        self,
        manager: CredentialsManager,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def fail_decryption(encrypted: str, key: str) -> str:
            raise ValueError("invalid ciphertext")

        monkeypatch.setattr(
            "proxywhirl.credentials_manager.decrypt_credentials",
            fail_decryption,
        )

        assert manager.decrypt_credential("encrypted-value") is None


def test_export_filters_unknown_names(
    manager: CredentialsManager,
    sample_credential: Credential,
) -> None:
    manager.add_credential(sample_credential)

    exported = manager.export_credentials(names=["missing", "proxy-auth"])

    assert list(exported) == ["proxy-auth"]
