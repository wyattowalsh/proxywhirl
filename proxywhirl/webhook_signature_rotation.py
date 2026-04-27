"""Webhook signature key rotation support.

Manages rotating webhook signature keys for
enhanced security and compliance.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from loguru import logger


@dataclass
class SignatureKey:
    """Webhook signature key."""

    key_id: str
    secret: str
    created_at: datetime
    expires_at: datetime | None = None
    is_active: bool = True
    rotated_at: datetime | None = None

    def is_expired(self) -> bool:
        """Check if key is expired.

        Returns:
            True if expired
        """
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at


class SignatureKeyRotationManager:
    """Manages webhook signature key rotation."""

    def __init__(self) -> None:
        """Initialize signature key rotation manager."""
        self._keys: dict[str, SignatureKey] = {}
        self._active_key: str | None = None
        logger.debug("SignatureKeyRotationManager initialized")

    def create_key(
        self,
        key_id: str,
        secret: str,
        expires_in_days: int | None = None,
    ) -> bool:
        """Create a new signature key.

        Args:
            key_id: Key identifier
            secret: Secret value
            expires_in_days: Days until expiration

        Returns:
            True if created
        """
        if key_id in self._keys:
            logger.warning(f"Key already exists: {key_id}")
            return False

        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        key = SignatureKey(
            key_id=key_id,
            secret=secret,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            is_active=True,
        )
        self._keys[key_id] = key

        if self._active_key is None:
            self._active_key = key_id

        logger.info(f"Signature key created: {key_id}")
        return True

    def rotate_key(self, new_key_id: str) -> bool:
        """Rotate to a new signature key.

        Args:
            new_key_id: New key ID

        Returns:
            True if rotated
        """
        if new_key_id not in self._keys:
            logger.error(f"Key not found: {new_key_id}")
            return False

        if self._active_key:
            old_key = self._keys[self._active_key]
            old_key.is_active = False
            old_key.rotated_at = datetime.now(timezone.utc)

        self._active_key = new_key_id
        logger.info(f"Signature key rotated: {new_key_id}")
        return True

    def get_active_key(self) -> SignatureKey | None:
        """Get active signature key.

        Returns:
            Active signature key or None
        """
        if self._active_key is None:
            return None

        key = self._keys.get(self._active_key)
        if key and key.is_expired():
            logger.warning(f"Active key is expired: {self._active_key}")
            return None

        return key

    def get_key(self, key_id: str) -> SignatureKey | None:
        """Get signature key by ID.

        Args:
            key_id: Key ID

        Returns:
            Signature key or None
        """
        return self._keys.get(key_id)

    def get_valid_keys(self) -> list[SignatureKey]:
        """Get all valid (not expired) keys.

        Returns:
            List of valid keys
        """
        return [key for key in self._keys.values() if not key.is_expired()]

    def revoke_key(self, key_id: str) -> bool:
        """Revoke a key.

        Args:
            key_id: Key ID

        Returns:
            True if revoked
        """
        if key_id not in self._keys:
            return False

        key = self._keys[key_id]
        key.is_active = False
        logger.info(f"Signature key revoked: {key_id}")
        return True

    def cleanup_expired_keys(self) -> int:
        """Remove expired keys.

        Returns:
            Number of keys removed
        """
        expired_ids = [kid for kid, key in self._keys.items() if key.is_expired()]

        for kid in expired_ids:
            del self._keys[kid]

        logger.info(f"Cleaned up {len(expired_ids)} expired keys")
        return len(expired_ids)

    def export_metrics(self) -> dict[str, Any]:
        """Export key rotation metrics.

        Returns:
            Dictionary of metrics
        """
        valid_keys = self.get_valid_keys()

        return {
            "total_keys": len(self._keys),
            "active_key": self._active_key,
            "valid_keys": len(valid_keys),
            "expired_keys": len(self._keys) - len(valid_keys),
        }
