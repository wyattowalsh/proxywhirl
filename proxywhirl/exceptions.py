"""
Custom exceptions for ProxyWhirl.

All exceptions support additional metadata for debugging and retry logic.
"""

from typing import Any, Optional


class ProxyWhirlError(Exception):
    """Base exception for all ProxyWhirl errors."""

    def __init__(
        self,
        message: str,
        *,
        proxy_url: Optional[str] = None,
        error_type: Optional[str] = None,
        retry_recommended: bool = False,
        **metadata: Any,
    ) -> None:
        """
        Initialize exception with optional metadata.

        Args:
            message: Human-readable error message
            proxy_url: URL of the proxy that caused the error (without credentials)
            error_type: Type of error (e.g., "timeout", "invalid_credentials")
            retry_recommended: Whether retrying the operation is recommended
            **metadata: Additional error-specific metadata
        """
        super().__init__(message)
        self.proxy_url = proxy_url
        self.error_type = error_type
        self.retry_recommended = retry_recommended
        self.metadata = metadata


class ProxyValidationError(ProxyWhirlError):
    """Raised when proxy URL or configuration is invalid."""


class ProxyPoolEmptyError(ProxyWhirlError):
    """Raised when attempting to select from an empty proxy pool."""


class ProxyConnectionError(ProxyWhirlError):
    """Raised when unable to connect through a proxy."""


class ProxyAuthenticationError(ProxyWhirlError):
    """Raised when proxy authentication fails."""


class ProxyFetchError(ProxyWhirlError):
    """Raised when fetching proxies from external sources fails."""


class ProxyStorageError(ProxyWhirlError):
    """Raised when proxy storage operations fail."""


class CacheCorruptionError(ProxyWhirlError):
    """Raised when cache data is corrupted and cannot be recovered."""


class CacheStorageError(ProxyWhirlError):
    """Raised when cache storage backend is unavailable."""


class CacheValidationError(ValueError, ProxyWhirlError):
    """Raised when cache entry fails validation."""


class RateLimitExceeded(ProxyWhirlError):
    """
    Raised when rate limit is exceeded.

    Used for HTTP 429 Too Many Requests responses with Retry-After header.
    """

    def __init__(
        self,
        message: str,
        *,
        limit: int,
        current_count: int,
        window_size_seconds: int,
        retry_after_seconds: int,
        tier: str,
        endpoint: str,
        identifier: str,
        **metadata: Any,
    ) -> None:
        """
        Initialize rate limit exception.

        Args:
            message: Human-readable error message
            limit: Maximum requests allowed in window
            current_count: Current request count in window
            window_size_seconds: Window size in seconds
            retry_after_seconds: Seconds until rate limit resets
            tier: User's rate limit tier
            endpoint: API endpoint that was rate limited
            identifier: User ID or IP address
            **metadata: Additional error-specific metadata
        """
        super().__init__(
            message,
            error_type="rate_limit_exceeded",
            retry_recommended=True,
            limit=limit,
            current_count=current_count,
            window_size_seconds=window_size_seconds,
            retry_after_seconds=retry_after_seconds,
            tier=tier,
            endpoint=endpoint,
            identifier=identifier,
            **metadata,
        )
        self.limit = limit
        self.current_count = current_count
        self.window_size_seconds = window_size_seconds
        self.retry_after_seconds = retry_after_seconds
        self.tier = tier
        self.endpoint = endpoint
        self.identifier = identifier
