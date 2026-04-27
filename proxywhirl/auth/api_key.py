"""
API Key Authentication for ProxyWhirl.

Provides secure API key generation, storage, and validation.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class APIKeyRotation(BaseModel):
    """Configuration for API key rotation."""

    enabled: bool = True
    rotation_interval_days: int = Field(default=90, ge=1)
    grace_period_days: int = Field(default=7, ge=0)

    model_config = ConfigDict(frozen=True)


class APIKey(BaseModel):
    """Secure API key representation."""

    key_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique key identifier")
    key_hash: str = Field(description="Bcrypt hash of the secret key")
    name: str = Field(description="Human-readable key name")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = Field(default=None, description="Optional expiration date")
    last_used_at: datetime | None = Field(default=None)
    is_active: bool = Field(default=True)
    metadata: dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True)


class APIKeyManager:
    """Manager for API key lifecycle."""

    def __init__(self, rotation_config: APIKeyRotation | None = None):
        """Initialize the API key manager.

        Args:
            rotation_config: Configuration for key rotation policy
        """
        self.rotation_config = rotation_config or APIKeyRotation()
        self._keys: dict[str, APIKey] = {}

    def generate_key(
        self,
        name: str,
        expires_in_days: int | None = None,
        metadata: dict[str, str] | None = None,
    ) -> tuple[str, APIKey]:
        """Generate a new API key.

        Args:
            name: Human-readable name for the key
            expires_in_days: Optional expiration time in days
            metadata: Optional metadata to attach to key

        Returns:
            Tuple of (secret_key, APIKey model)
        """
        import bcrypt

        secret = secrets.token_urlsafe(32)
        key_hash = bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()

        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        api_key = APIKey(
            key_hash=key_hash,
            name=name,
            expires_at=expires_at,
            metadata=metadata or {},
        )

        self._keys[api_key.key_id] = api_key
        return secret, api_key

    def validate_key(self, key_id: str, secret: str) -> APIKey | None:
        """Validate an API key against the stored hash.

        Args:
            key_id: The key identifier
            secret: The secret string to validate

        Returns:
            APIKey if valid and active, None otherwise
        """
        import bcrypt

        if key_id not in self._keys:
            return None

        api_key = self._keys[key_id]

        if not api_key.is_active:
            return None

        if api_key.expires_at and datetime.now(timezone.utc) > api_key.expires_at:
            return None

        try:
            if bcrypt.checkpw(secret.encode(), api_key.key_hash.encode()):
                return api_key
        except Exception:
            return None

        return None

    def revoke_key(self, key_id: str) -> bool:
        """Revoke an API key.

        Args:
            key_id: The key identifier

        Returns:
            True if revoked, False if not found
        """
        if key_id in self._keys:
            self._keys[key_id] = self._keys[key_id].model_copy(update={"is_active": False})
            return True
        return False

    def list_keys(self, active_only: bool = True) -> list[APIKey]:
        """List all API keys.

        Args:
            active_only: Only return active keys

        Returns:
            List of APIKey objects
        """
        keys = list(self._keys.values())
        if active_only:
            keys = [k for k in keys if k.is_active]
        return keys
