"""
Custom exceptions for ProxyWhirl.

All exceptions support additional metadata for debugging and retry logic.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Any
from urllib.parse import urlparse


class ProxyErrorCode(str, Enum):
    """Error codes for programmatic error handling."""

    PROXY_POOL_EMPTY = "PROXY_POOL_EMPTY"
    PROXY_VALIDATION_FAILED = "PROXY_VALIDATION_FAILED"
    PROXY_CONNECTION_FAILED = "PROXY_CONNECTION_FAILED"
    PROXY_AUTH_FAILED = "PROXY_AUTH_FAILED"
    PROXY_FETCH_FAILED = "PROXY_FETCH_FAILED"
    PROXY_STORAGE_FAILED = "PROXY_STORAGE_FAILED"
    CACHE_CORRUPTED = "CACHE_CORRUPTED"
    CACHE_STORAGE_FAILED = "CACHE_STORAGE_FAILED"
    CACHE_VALIDATION_FAILED = "CACHE_VALIDATION_FAILED"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
    QUEUE_FULL = "QUEUE_FULL"


def redact_url(url: str) -> str:
    """
    Redact sensitive information from a URL.

    Removes username and password while preserving scheme, host, port, and path.

    Args:
        url: URL to redact

    Returns:
        Redacted URL string
    """
    try:
        parsed = urlparse(url)
        # Reconstruct URL without credentials
        if parsed.hostname:
            redacted = f"{parsed.scheme}://{parsed.hostname}"
            if parsed.port:
                redacted += f":{parsed.port}"
            if parsed.path:
                redacted += parsed.path
            if parsed.query:
                # Redact sensitive query parameters
                query = parsed.query
                query = re.sub(
                    r"(password|token|key|secret|auth)=[^&]*",
                    r"\1=***",
                    query,
                    flags=re.IGNORECASE,
                )
                redacted += f"?{query}"
            return redacted
        return url
    except Exception:
        # If parsing fails, try simple regex-based redaction
        return re.sub(r"://[^:]+:[^@]+@", "://***:***@", url)


class ProxyWhirlError(Exception):
    """Base exception for all ProxyWhirl errors."""

    # Default error code for the exception class
    error_code: ProxyErrorCode = ProxyErrorCode.NETWORK_ERROR

    def __init__(
        self,
        message: str,
        *,
        proxy_url: str | None = None,
        error_type: str | None = None,
        error_code: ProxyErrorCode | None = None,
        retry_recommended: bool = False,
        attempt_count: int | None = None,
        **metadata: Any,
    ) -> None:
        """
        Initialize exception with optional metadata.

        Args:
            message: Human-readable error message
            proxy_url: URL of the proxy that caused the error (will be redacted)
            error_type: Type of error (e.g., "timeout", "invalid_credentials")
            error_code: Programmatic error code for handling
            retry_recommended: Whether retrying the operation is recommended
            attempt_count: Number of attempts made before this error
            **metadata: Additional error-specific metadata
        """
        # Redact proxy URL if provided
        redacted_url = redact_url(proxy_url) if proxy_url else None

        # Build enhanced message with context
        enhanced_message = message
        if redacted_url:
            enhanced_message += f" (proxy: {redacted_url})"
        if attempt_count is not None:
            enhanced_message += f" [attempt {attempt_count}]"

        super().__init__(enhanced_message)

        self.proxy_url = redacted_url
        self.error_type = error_type
        self.error_code = error_code or self.__class__.error_code
        self.retry_recommended = retry_recommended
        self.attempt_count = attempt_count
        self.metadata = metadata

    def to_dict(self) -> dict[str, Any]:
        """
        Convert exception to dictionary for logging/serialization.

        Returns:
            Dictionary representation of the error
        """
        return {
            "error_code": self.error_code.value,
            "message": str(self),
            "proxy_url": self.proxy_url,
            "error_type": self.error_type,
            "retry_recommended": self.retry_recommended,
            "attempt_count": self.attempt_count,
            **self.metadata,
        }


class ProxyValidationError(ProxyWhirlError):
    """Raised when proxy URL or configuration is invalid.

    Actionable guidance:
    - Verify the proxy URL format (e.g., http://host:port)
    - Check that the protocol is supported (http, https, socks5)
    - Ensure credentials are properly encoded
    """

    error_code = ProxyErrorCode.PROXY_VALIDATION_FAILED

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize with validation-specific defaults."""
        if "suggestion" not in message:
            message += ". Check proxy URL format and protocol."
        super().__init__(message, retry_recommended=False, **kwargs)


class ProxyPoolEmptyError(ProxyWhirlError):
    """Raised when attempting to select from an empty proxy pool.

    Actionable guidance:
    - Add proxies to the pool using add_proxy() or auto-fetch
    - Check if proxies were filtered out by health checks
    - Verify proxy sources are reachable
    """

    error_code = ProxyErrorCode.PROXY_POOL_EMPTY

    def __init__(self, message: str = "No proxies available in the pool", **kwargs: Any) -> None:
        """Initialize with pool-empty-specific defaults."""
        if "add proxies" not in message.lower():
            message += ". Add proxies using add_proxy() or enable auto-fetch."
        super().__init__(message, retry_recommended=False, **kwargs)


class ProxyConnectionError(ProxyWhirlError):
    """Raised when unable to connect through a proxy.

    Actionable guidance:
    - Verify proxy is reachable and not blocked
    - Check network connectivity
    - Ensure proxy supports the target protocol
    - Try increasing timeout value
    """

    error_code = ProxyErrorCode.PROXY_CONNECTION_FAILED

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize with connection-specific defaults."""
        if "timeout" in message.lower():
            kwargs.setdefault("error_code", ProxyErrorCode.TIMEOUT)
        super().__init__(message, retry_recommended=True, **kwargs)


class ProxyAuthenticationError(ProxyWhirlError):
    """Raised when proxy authentication fails.

    Actionable guidance:
    - Verify username and password are correct
    - Check if proxy requires specific auth method
    - Ensure credentials are not expired
    - Contact proxy provider if credentials should be valid
    """

    error_code = ProxyErrorCode.PROXY_AUTH_FAILED

    def __init__(self, message: str = "Proxy authentication failed", **kwargs: Any) -> None:
        """Initialize with auth-specific defaults."""
        if "verify credentials" not in message.lower():
            message += ". Verify username and password are correct."
        super().__init__(message, retry_recommended=False, **kwargs)


class ProxyFetchError(ProxyWhirlError):
    """Raised when fetching proxies from external sources fails.

    Actionable guidance:
    - Verify the source URL is accessible
    - Check API credentials if required
    - Ensure the response format matches expectations
    - Review rate limits with the provider
    """

    error_code = ProxyErrorCode.PROXY_FETCH_FAILED

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize with fetch-specific defaults."""
        super().__init__(message, retry_recommended=True, **kwargs)


class ProxyStorageError(ProxyWhirlError):
    """Raised when proxy storage operations fail.

    Actionable guidance:
    - Check file system permissions
    - Verify disk space is available
    - Ensure storage path is writable
    - Check database connection if using external storage
    """

    error_code = ProxyErrorCode.PROXY_STORAGE_FAILED

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize with storage-specific defaults."""
        if "permissions" not in message.lower() and "disk space" not in message.lower():
            message += ". Check file permissions and disk space."
        super().__init__(message, retry_recommended=False, **kwargs)


class CacheCorruptionError(ProxyWhirlError):
    """Raised when cache data is corrupted and cannot be recovered.

    Actionable guidance:
    - Clear the cache and reinitialize
    - Check for disk errors or corruption
    - Verify cache format version compatibility
    """

    error_code = ProxyErrorCode.CACHE_CORRUPTED

    def __init__(self, message: str = "Cache data is corrupted", **kwargs: Any) -> None:
        """Initialize with cache corruption-specific defaults."""
        if "clear cache" not in message.lower():
            message += ". Clear the cache to recover."
        super().__init__(message, retry_recommended=False, **kwargs)


class CacheStorageError(ProxyWhirlError):
    """Raised when cache storage backend is unavailable.

    Actionable guidance:
    - Verify cache backend (Redis, Memcached) is running
    - Check network connectivity to cache server
    - Ensure cache credentials are valid
    - Review cache server logs for errors
    """

    error_code = ProxyErrorCode.CACHE_STORAGE_FAILED

    def __init__(self, message: str = "Cache storage backend unavailable", **kwargs: Any) -> None:
        """Initialize with cache storage-specific defaults."""
        super().__init__(message, retry_recommended=True, **kwargs)


class CacheValidationError(ValueError, ProxyWhirlError):
    """Raised when cache entry fails validation.

    Actionable guidance:
    - Check cache entry format
    - Verify data types match schema
    - Ensure required fields are present
    """

    error_code = ProxyErrorCode.CACHE_VALIDATION_FAILED

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize with cache validation-specific defaults."""
        super().__init__(message, retry_recommended=False, **kwargs)


class RequestQueueFullError(ProxyWhirlError):
    """Raised when the request queue is full and cannot accept more requests.

    Actionable guidance:
    - Wait for pending requests to complete
    - Increase queue_size in configuration
    - Reduce request rate to avoid overloading the queue
    - Consider implementing request batching or throttling
    """

    error_code = ProxyErrorCode.QUEUE_FULL

    def __init__(
        self, message: str = "Request queue is full", queue_size: int | None = None, **kwargs: Any
    ) -> None:
        """Initialize with queue-specific defaults."""
        if queue_size is not None:
            message += f" (max size: {queue_size})"
        if "wait" not in message.lower() and "reduce" not in message.lower():
            message += ". Wait for requests to complete or increase queue_size."
        super().__init__(message, retry_recommended=True, **kwargs)
