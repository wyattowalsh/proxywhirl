"""
Webhook request signing and verification for ProxyWhirl.

Provides HMAC-SHA256 signing for webhook requests.
"""

from __future__ import annotations

import hashlib
import hmac

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class WebhookSigner(BaseModel):
    """Signer for webhook requests using HMAC-SHA256."""

    secret: SecretStr = Field(description="Secret key for signing")
    algorithm: str = Field(default="sha256", description="HMAC algorithm")

    model_config = ConfigDict(frozen=True)

    def sign(self, payload: bytes) -> str:
        """Sign a payload.

        Args:
            payload: Raw bytes to sign

        Returns:
            Hex-encoded HMAC signature
        """
        secret = self.secret.get_secret_value()
        if isinstance(secret, str):
            secret = secret.encode()

        signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        return signature

    def sign_json(self, json_str: str) -> str:
        """Sign a JSON string.

        Args:
            json_str: JSON string to sign

        Returns:
            Hex-encoded HMAC signature
        """
        return self.sign(json_str.encode("utf-8"))


class WebhookVerifier(BaseModel):
    """Verifier for signed webhook requests."""

    secret: SecretStr = Field(description="Secret key for verification")
    algorithm: str = Field(default="sha256", description="HMAC algorithm")
    timestamp_tolerance_seconds: int = Field(
        default=300, description="Tolerance for timestamp validation"
    )

    model_config = ConfigDict(frozen=True)

    def verify(self, payload: bytes, signature: str) -> bool:
        """Verify a payload signature.

        Args:
            payload: Raw bytes that were signed
            signature: Hex-encoded signature to verify

        Returns:
            True if signature is valid
        """
        secret = self.secret.get_secret_value()
        if isinstance(secret, str):
            secret = secret.encode()

        expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def verify_json(self, json_str: str, signature: str) -> bool:
        """Verify a JSON string signature.

        Args:
            json_str: JSON string that was signed
            signature: Hex-encoded signature to verify

        Returns:
            True if signature is valid
        """
        return self.verify(json_str.encode("utf-8"), signature)

    def verify_request(
        self,
        payload: bytes,
        signature: str,
        timestamp: str | None = None,
    ) -> tuple[bool, str | None]:
        """Verify a complete webhook request with optional timestamp validation.

        Args:
            payload: Raw request body bytes
            signature: Signature from webhook header
            timestamp: Optional timestamp from webhook header

        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        if not self.verify(payload, signature):
            return False, "Invalid signature"

        if timestamp:
            import time

            try:
                ts = int(timestamp)
                current_time = int(time.time())
                if abs(current_time - ts) > self.timestamp_tolerance_seconds:
                    return (
                        False,
                        f"Timestamp too old (tolerance: {self.timestamp_tolerance_seconds}s)",
                    )
            except (ValueError, TypeError):
                return False, "Invalid timestamp format"

        return True, None
