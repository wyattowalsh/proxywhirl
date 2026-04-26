"""Request signing and authentication for proxy interactions.

Supports:
- HMAC-SHA256 signing for request integrity
- OAuth2 bearer tokens
- API key authentication
- Custom authentication headers
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any
from urllib.parse import urlencode

from loguru import logger


class SignatureAlgorithm(str, Enum):
    """Supported signature algorithms."""

    HMAC_SHA256 = "hmac-sha256"
    HMAC_SHA512 = "hmac-sha512"
    RSA_SHA256 = "rsa-sha256"


@dataclass
class SignatureConfig:
    """Configuration for request signing."""

    algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256
    secret_key: str = ""
    include_timestamp: bool = True
    timestamp_tolerance: int = 300  # 5 minutes
    include_nonce: bool = False


class RequestSigner:
    """Sign HTTP requests for integrity and authenticity verification."""

    def __init__(self, config: SignatureConfig):
        """Initialize request signer.

        Args:
            config: Signature configuration
        """
        self.config = config
        self.nonce_cache: set[str] = set()

    def sign_request(
        self,
        method: str,
        url: str,
        body: bytes | str | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """Sign an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            body: Optional request body
            headers: Optional existing headers

        Returns:
            Dictionary with signature headers to add to request
        """
        if headers is None:
            headers = {}

        signature_headers = dict(headers)
        timestamp = str(int(time.time()))

        # Build signature string
        sig_string = self._build_signature_string(
            method,
            url,
            body,
            signature_headers,
            timestamp,
        )

        # Generate signature
        signature = self._generate_signature(sig_string)

        # Add signature headers
        signature_headers["X-Signature"] = signature
        signature_headers["X-Signature-Algorithm"] = self.config.algorithm.value

        if self.config.include_timestamp:
            signature_headers["X-Timestamp"] = timestamp

        if self.config.include_nonce:
            nonce = self._generate_nonce()
            signature_headers["X-Nonce"] = nonce

        return signature_headers

    def verify_request(
        self,
        method: str,
        url: str,
        body: bytes | str | None = None,
        headers: dict[str, str] | None = None,
    ) -> bool:
        """Verify a request signature.

        Args:
            method: HTTP method
            url: Request URL
            body: Request body
            headers: Request headers

        Returns:
            True if signature is valid, False otherwise
        """
        if headers is None:
            headers = {}

        signature = headers.get("X-Signature")
        if not signature:
            logger.warning("Request missing X-Signature header")
            return False

        timestamp = headers.get("X-Timestamp")
        if self.config.include_timestamp and timestamp:
            try:
                ts = int(timestamp)
                now = int(time.time())
                if abs(now - ts) > self.config.timestamp_tolerance:
                    logger.warning("Request timestamp outside tolerance window")
                    return False
            except ValueError:
                logger.warning("Invalid timestamp format")
                return False

        nonce = headers.get("X-Nonce")
        if self.config.include_nonce and nonce:
            if nonce in self.nonce_cache:
                logger.warning("Request nonce replay detected")
                return False
            self.nonce_cache.add(nonce)

        # Rebuild signature
        sig_string = self._build_signature_string(
            method,
            url,
            body,
            headers,
            timestamp or "",
        )
        expected_signature = self._generate_signature(sig_string)

        # Constant-time comparison
        return hmac.compare_digest(signature, expected_signature)

    def _build_signature_string(
        self,
        method: str,
        url: str,
        body: bytes | str | None,
        headers: dict[str, str],
        timestamp: str,
    ) -> str:
        """Build signature string from request components.

        Args:
            method: HTTP method
            url: Request URL
            body: Request body
            headers: Request headers
            timestamp: Request timestamp

        Returns:
            Signature string
        """
        parts = [
            method.upper(),
            url,
        ]

        if body:
            if isinstance(body, bytes):
                body = body.decode("utf-8")
            parts.append(body)

        if self.config.include_timestamp and timestamp:
            parts.append(timestamp)

        return "\n".join(parts)

    def _generate_signature(self, message: str) -> str:
        """Generate HMAC signature.

        Args:
            message: Message to sign

        Returns:
            Hex-encoded signature
        """
        if self.config.algorithm == SignatureAlgorithm.HMAC_SHA256:
            signature = hmac.new(
                self.config.secret_key.encode(),
                message.encode(),
                hashlib.sha256,
            ).hexdigest()
        elif self.config.algorithm == SignatureAlgorithm.HMAC_SHA512:
            signature = hmac.new(
                self.config.secret_key.encode(),
                message.encode(),
                hashlib.sha512,
            ).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {self.config.algorithm}")

        return signature

    @staticmethod
    def _generate_nonce() -> str:
        """Generate a random nonce.

        Returns:
            Random nonce string
        """
        import secrets

        return secrets.token_urlsafe(32)


class APIKeyAuthenticator:
    """Authenticate requests using API keys."""

    def __init__(
        self,
        api_key: str,
        key_header: str = "X-API-Key",
    ):
        """Initialize API key authenticator.

        Args:
            api_key: API key value
            key_header: Header name for API key
        """
        self.api_key = api_key
        self.key_header = key_header

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers.

        Returns:
            Dictionary with auth headers
        """
        return {
            self.key_header: self.api_key,
        }

    def verify_request(self, headers: dict[str, str]) -> bool:
        """Verify request authentication.

        Args:
            headers: Request headers

        Returns:
            True if API key is valid
        """
        provided_key = headers.get(self.key_header)
        return provided_key == self.api_key


class BearerTokenAuthenticator:
    """Authenticate requests using bearer tokens."""

    def __init__(self, token: str):
        """Initialize bearer token authenticator.

        Args:
            token: Bearer token value
        """
        self.token = token

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers.

        Returns:
            Dictionary with auth headers
        """
        return {
            "Authorization": f"Bearer {self.token}",
        }

    def verify_request(self, headers: dict[str, str]) -> bool:
        """Verify request authentication.

        Args:
            headers: Request headers

        Returns:
            True if bearer token is valid
        """
        auth_header = headers.get("Authorization", "")
        try:
            scheme, credentials = auth_header.split(" ", 1)
            return scheme.lower() == "bearer" and credentials == self.token
        except ValueError:
            return False
