"""Authentication utilities for the canonical ProxyWhirl REST API."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict


class WebhookSignature(BaseModel):
    """Immutable webhook signature metadata."""

    model_config = ConfigDict(frozen=True)

    signature: str
    timestamp: str
    nonce: str


class WebhookSigner:
    """Sign and verify webhook payloads using HMAC-SHA256."""

    def __init__(self, secret: str) -> None:
        self._secret = secret.encode()

    @staticmethod
    def generate_nonce() -> str:
        """Generate a unique 32-character hex nonce."""
        return secrets.token_hex(16)

    def sign_payload(self, payload: bytes, timestamp: str, nonce: str) -> str:
        """Sign payload and return a 64-character SHA256 hex digest."""
        data = payload + timestamp.encode() + nonce.encode()
        return hmac.new(self._secret, data, hashlib.sha256).hexdigest()

    def verify_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: str,
        nonce: str,
        tolerance_seconds: int = 300,
    ) -> bool:
        """Verify a payload signature and timestamp tolerance."""
        expected = self.sign_payload(payload, timestamp, nonce)
        if not hmac.compare_digest(expected, signature):
            return False

        try:
            signed_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            return False

        if signed_at.tzinfo is None:
            signed_at = signed_at.replace(tzinfo=timezone.utc)

        age = (datetime.now(timezone.utc) - signed_at.astimezone(timezone.utc)).total_seconds()
        if age > tolerance_seconds:
            raise ValueError("timestamp too old")

        return True


class APIKeyAuth(BaseModel):
    """API key authentication record."""

    key_id: str
    key_secret: str
    name: str
    requests_per_minute: int = 100
    requests_per_hour: int = 10000
    expires_at: datetime | None = None
    is_active: bool = True

    @property
    def is_expired(self) -> bool:
        """Return whether the API key has expired."""
        if self.expires_at is None:
            return False
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at.astimezone(timezone.utc) < datetime.now(timezone.utc)


def create_api_key(name: str) -> tuple[str, str]:
    """Create a new API key pair."""
    key_id = secrets.token_urlsafe(16)
    key_secret = secrets.token_urlsafe(32)
    return key_id, key_secret
