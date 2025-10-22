"""
Custom exceptions for ProxyWhirl.
"""


class ProxyWhirlError(Exception):
    """Base exception for all ProxyWhirl errors."""

    pass


class ProxyValidationError(ProxyWhirlError):
    """Raised when proxy URL or configuration is invalid."""

    pass


class ProxyPoolEmptyError(ProxyWhirlError):
    """Raised when attempting to select from an empty proxy pool."""

    pass


class ProxyConnectionError(ProxyWhirlError):
    """Raised when unable to connect through a proxy."""

    pass


class ProxyAuthenticationError(ProxyWhirlError):
    """Raised when proxy authentication fails."""

    pass


class ProxyFetchError(ProxyWhirlError):
    """Raised when fetching proxies from external sources fails."""

    pass


class ProxyStorageError(ProxyWhirlError):
    """Raised when proxy storage operations fail."""

    pass
