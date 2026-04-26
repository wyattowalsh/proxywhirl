"""API v2 authentication, webhook signing, and per-key rate limiting.

Provides:
- API key authentication with per-key rate limits
- HMAC-SHA256 webhook signing/verification
- Key rotation support
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class APIKeyAuth(BaseModel):
    """API key with rate limiting configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key_id: str = Field(description="Unique key identifier")
    key_secret: str = Field(description="Secret key (hashed in database)")
    name: str = Field(description="Human-readable key name")
    requests_per_minute: int = Field(default=60, ge=1, le=10000)
    requests_per_hour: int = Field(default=3600, ge=1, le=1000000)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    scopes: list[str] = Field(
        default_factory=list,
        description="API scopes this key has access to",
    )


class RateLimitKey(BaseModel):
    """Rate limit tracking for an API key."""

    model_config = ConfigDict(frozen=False)

    key_id: str
    minute_requests: int = 0
    hour_requests: int = 0
    last_minute_reset: float = Field(default_factory=time.time)
    last_hour_reset: float = Field(default_factory=time.time)

    def is_minute_limit_exceeded(self, limit: int) -> bool:
        """Check if minute rate limit is exceeded."""
        now = time.time()
        if now - self.last_minute_reset >= 60:
            return False
        return self.minute_requests >= limit

    def is_hour_limit_exceeded(self, limit: int) -> bool:
        """Check if hour rate limit is exceeded."""
        now = time.time()
        if now - self.last_hour_reset >= 3600:
            return False
        return self.hour_requests >= limit


class WebhookSignature(BaseModel):
    """HMAC-SHA256 signature for webhook verification."""

    model_config = ConfigDict(frozen=True)

    signature: str = Field(description="HMAC-SHA256 signature (hex)")
    timestamp: str = Field(description="ISO 8601 timestamp")
    nonce: str = Field(description="One-time nonce for replay prevention")


class WebhookSigner:
    """Sign and verify webhook requests using HMAC-SHA256."""

    def __init__(self, webhook_secret: Optional[str] = None):
        """Initialize webhook signer.

        Args:
            webhook_secret: Secret key for signing. If not provided,
                          uses PROXYWHIRL_WEBHOOK_SECRET env var.
        """
        self.secret = webhook_secret or os.getenv("PROXYWHIRL_WEBHOOK_SECRET", "").encode()
        if not self.secret:
            raise ValueError("Webhook secret not configured")

    @staticmethod
    def generate_nonce() -> str:
        """Generate a random nonce."""
        return secrets.token_hex(16)

    def sign_payload(self, payload: bytes, timestamp: str, nonce: str) -> str:
        """Sign webhook payload.

        Args:
            payload: Raw request body
            timestamp: ISO 8601 timestamp
            nonce: One-time nonce

        Returns:
            HMAC-SHA256 signature in hex format
        """
        message = f"{timestamp}.{nonce}.{payload.decode()}".encode()
        if isinstance(self.secret, str):
            self.secret = self.secret.encode()
        return hmac.new(self.secret, message, hashlib.sha256).hexdigest()

    def verify_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: str,
        nonce: str,
        tolerance_seconds: int = 300,
    ) -> bool:
        """Verify webhook signature.

        Args:
            payload: Raw request body
            signature: Signature to verify
            timestamp: ISO 8601 timestamp
            nonce: One-time nonce
            tolerance_seconds: Max age of timestamp (default 5 min)

        Returns:
            True if signature is valid and timestamp is recent

        Raises:
            ValueError: If timestamp is too old
        """
        # Verify timestamp freshness
        request_time = datetime.fromisoformat(timestamp)
        now = datetime.now(timezone.utc)
        age = (now - request_time.replace(tzinfo=timezone.utc)).total_seconds()

        if age > tolerance_seconds:
            raise ValueError(f"Webhook timestamp too old: {age:.0f}s")

        # Verify signature
        expected_signature = self.sign_payload(payload, timestamp, nonce)
        return hmac.compare_digest(signature, expected_signature)


class KeyRotationPolicy(BaseModel):
    """Policy for API key rotation."""

    model_config = ConfigDict(frozen=True)

    rotation_days: int = Field(default=90, ge=1)
    warn_before_days: int = Field(default=7, ge=1)
    keep_previous_keys: int = Field(default=2, description="Number of old keys to keep")


def create_api_key(
    name: str,
    requests_per_minute: int = 60,
    requests_per_hour: int = 3600,
    expires_in_days: Optional[int] = None,
) -> tuple[str, str]:
    """Create a new API key.

    Args:
        name: Human-readable key name
        requests_per_minute: Requests allowed per minute
        requests_per_hour: Requests allowed per hour
        expires_in_days: Days until key expires (None = no expiry)

    Returns:
        Tuple of (key_id, key_secret)
    """
    key_id = f"pk_{secrets.token_hex(8)}"
    key_secret = secrets.token_urlsafe(32)

    expires_at = None
    if expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

    return key_id, key_secret
