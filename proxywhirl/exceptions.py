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
