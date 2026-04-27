"""Credentials and secret management."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger

from proxywhirl.utils import decrypt_credentials, encrypt_credentials


@dataclass
class Credential:
    """Single credential entry."""

    name: str
    username: str
    password: str
    extra_fields: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Dict representation
        """
        return {
            "name": self.name,
            "username": self.username,
            "password": self.password,
            "extra_fields": self.extra_fields,
            "description": self.description,
            "tags": self.tags,
        }


class CredentialsManager:
    """Manages credentials securely."""

    def __init__(self):
        """Initialize manager."""
        self._credentials: dict[str, Credential] = {}
        self._encryption_key: str | None = None

    def set_encryption_key(self, key: str) -> None:
        """Set encryption key.

        Args:
            key: Encryption key
        """
        self._encryption_key = key
        logger.info("Encryption key set")

    def add_credential(self, credential: Credential) -> None:
        """Add credential.

        Args:
            credential: Credential to add
        """
        if credential.name in self._credentials:
            logger.warning(f"Overwriting existing credential: {credential.name}")

        self._credentials[credential.name] = credential
        logger.info(f"Added credential: {credential.name}")

    def get_credential(self, name: str) -> Credential | None:
        """Get credential by name.

        Args:
            name: Credential name

        Returns:
            Credential or None
        """
        return self._credentials.get(name)

    def has_credential(self, name: str) -> bool:
        """Check if credential exists.

        Args:
            name: Credential name

        Returns:
            True if exists
        """
        return name in self._credentials

    def remove_credential(self, name: str) -> bool:
        """Remove credential.

        Args:
            name: Credential name

        Returns:
            True if removed
        """
        if name in self._credentials:
            del self._credentials[name]
            logger.info(f"Removed credential: {name}")
            return True

        return False

    def list_credentials(self) -> list[str]:
        """List all credential names.

        Returns:
            List of names
        """
        return list(self._credentials.keys())

    def encrypt_credential(self, name: str) -> str:
        """Encrypt credential.

        Args:
            name: Credential name

        Returns:
            Encrypted string
        """
        credential = self.get_credential(name)
        if not credential:
            raise ValueError(f"Credential not found: {name}")

        if not self._encryption_key:
            raise ValueError("Encryption key not set")

        data = f"{credential.username}:{credential.password}"
        return encrypt_credentials(data, self._encryption_key)

    def decrypt_credential(self, encrypted: str) -> tuple[str, str] | None:
        """Decrypt credential.

        Args:
            encrypted: Encrypted string

        Returns:
            (username, password) tuple or None
        """
        if not self._encryption_key:
            logger.warning("Encryption key not set, cannot decrypt")
            return None

        try:
            decrypted = decrypt_credentials(encrypted, self._encryption_key)
            if ":" not in decrypted:
                return None

            username, password = decrypted.split(":", 1)
            return username, password
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None

    def find_by_tag(self, tag: str) -> list[Credential]:
        """Find credentials by tag.

        Args:
            tag: Tag name

        Returns:
            List of matching credentials
        """
        return [cred for cred in self._credentials.values() if tag in cred.tags]

    def export_credentials(
        self,
        names: list[str] | None = None,
        encrypt: bool = False,
    ) -> dict[str, Any]:
        """Export credentials.

        Args:
            names: Specific names to export (None = all)
            encrypt: Whether to encrypt passwords

        Returns:
            Export dict
        """
        export_data = {}

        cred_names = names or list(self._credentials.keys())

        for name in cred_names:
            credential = self.get_credential(name)
            if not credential:
                continue

            cred_dict = credential.to_dict()

            if encrypt and self._encryption_key:
                password_str = f"{credential.username}:{credential.password}"
                cred_dict["password"] = encrypt_credentials(
                    password_str,
                    self._encryption_key,
                )

            export_data[name] = cred_dict

        return export_data

    def clear(self) -> None:
        """Clear all credentials."""
        self._credentials.clear()
        logger.warning("All credentials cleared")
