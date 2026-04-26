"""
Custom exceptions for ProxyWhirl.

All exceptions support additional metadata for debugging and retry logic.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse


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
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    MAX_RETRIES_EXHAUSTED = "MAX_RETRIES_EXHAUSTED"
    CIRCUIT_BREAKER_OPEN = "CIRCUIT_BREAKER_OPEN"
    GEO_LOOKUP_FAILED = "GEO_LOOKUP_FAILED"
    BROWSER_ERROR = "BROWSER_ERROR"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    EVENT_LOOP_CONFLICT = "EVENT_LOOP_CONFLICT"
    SCHEMA_MIGRATION_ERROR = "SCHEMA_MIGRATION_ERROR"


SENSITIVE_QUERY_NAME_PARTS = {
    "auth",
    "authorization",
    "credential",
    "credentials",
    "key",
    "pass",
    "passwd",
    "password",
    "secret",
    "token",
}


def _is_sensitive_query_name(name: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    if normalized in SENSITIVE_QUERY_NAME_PARTS:
        return True
    return any(part in SENSITIVE_QUERY_NAME_PARTS for part in normalized.split("_"))


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
        if parsed.username is not None or parsed.password is not None:
            host_port = parsed.netloc.rsplit("@", 1)[-1]
            redacted_netloc = f"***:***@{host_port}"
            return parsed._replace(netloc=redacted_netloc).geturl()

        # Reconstruct URL without credentials
        if parsed.hostname:
            redacted = f"{parsed.scheme}://{parsed.hostname}"
            if parsed.port:
                redacted += f":{parsed.port}"
            if parsed.path:
                redacted += parsed.path
            if parsed.query:
                # Redact sensitive query parameters
                query_items = [
                    (key, "***" if _is_sensitive_query_name(key) else value)
                    for key, value in parse_qsl(parsed.query, keep_blank_values=True)
                ]
                query = urlencode(query_items).replace("%2A%2A%2A", "***")
                redacted += f"?{query}"
            return redacted
        return url
    except Exception:
        # If parsing fails, try simple regex-based redaction
        return re.sub(r"://[^/@?#]*@", "://***:***@", url)


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
        kwargs.setdefault("retry_recommended", True)
        super().__init__(message, **kwargs)


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
        kwargs.setdefault("retry_recommended", False)
        super().__init__(message, **kwargs)


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


class RateLimitExceededError(ProxyWhirlError):
    """Raised when rate limit is exceeded.

    Actionable guidance:
    - Implement exponential backoff retry strategy
    - Check rate limit headers in response for reset time
    - Consider using a queue to throttle requests
    - Review provider's rate limit documentation
    """

    error_code = ProxyErrorCode.RATE_LIMIT_EXCEEDED

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        reset_at: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with rate limit-specific defaults.

        Args:
            message: Error message
            reset_at: Unix timestamp when rate limit resets
            **kwargs: Additional metadata
        """
        if reset_at is not None:
            message += f" (resets at {reset_at})"
        if "backoff" not in message.lower() and "wait" not in message.lower():
            message += ". Implement exponential backoff before retrying."
        super().__init__(message, retry_recommended=True, **kwargs)
        self.reset_at = reset_at


class MaxRetriesExhaustedError(ProxyWhirlError):
    """Raised when maximum retry attempts are exhausted.

    Actionable guidance:
    - Check operation logs for failure patterns
    - Verify proxy/network connectivity
    - Review timeout and retry configuration
    - Consider manual retry with longer delays
    """

    error_code = ProxyErrorCode.MAX_RETRIES_EXHAUSTED

    def __init__(
        self,
        message: str = "Maximum retries exhausted",
        max_attempts: int | None = None,
        last_error: Exception | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with retry exhaustion-specific context.

        Args:
            message: Error message
            max_attempts: Number of attempts made
            last_error: The final exception that triggered this error
            **kwargs: Additional metadata
        """
        if max_attempts is not None:
            message += f" (attempted {max_attempts} times)"
        if "check logs" not in message.lower():
            message += ". Review operation logs for failure patterns."
        kwargs.setdefault("error_type", "exhausted_retries")
        super().__init__(message, retry_recommended=False, **kwargs)
        self.max_attempts = max_attempts
        self.last_error = last_error


class CircuitBreakerOpenError(ProxyWhirlError):
    """Raised when circuit breaker is in open state.

    Actionable guidance:
    - Wait for circuit breaker cooldown period to complete
    - Monitor service health to know when to retry
    - Consider manual reset if service is confirmed healthy
    - Implement fallback strategy or timeout
    """

    error_code = ProxyErrorCode.CIRCUIT_BREAKER_OPEN

    def __init__(
        self,
        message: str = "Circuit breaker is open",
        reopens_at: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with circuit breaker context.

        Args:
            message: Error message
            reopens_at: Unix timestamp when circuit may reopen
            **kwargs: Additional metadata
        """
        if reopens_at is not None:
            message += f" (reopens at {reopens_at})"
        if "wait" not in message.lower():
            message += ". Wait for cooldown period before retrying."
        super().__init__(message, retry_recommended=True, **kwargs)
        self.reopens_at = reopens_at


class ProxyConnectionContextError(ProxyConnectionError):
    """ProxyConnectionError with additional context information.

    Extends ProxyConnectionError to include source, target, and phase context
    for debugging connection failures.
    """

    def __init__(
        self,
        message: str,
        *,
        source: str | None = None,
        target: str | None = None,
        phase: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with connection context.

        Args:
            message: Error message
            source: Source proxy address
            target: Target server being accessed
            phase: Phase of connection (connect, auth, request, etc.)
            **kwargs: Additional metadata
        """
        enhanced_msg = message
        if phase:
            enhanced_msg += f" (phase: {phase})"
        if source:
            enhanced_msg += f" (source: {source})"
        if target:
            enhanced_msg += f" (target: {target})"

        super().__init__(enhanced_msg, **kwargs)
        self.source = source
        self.target = target
        self.phase = phase


class CacheTierError(ProxyWhirlError):
    """Cache exception with tier information."""

    def __init__(
        self,
        message: str,
        *,
        tier_name: str | None = None,
        tier_level: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with cache tier context.

        Args:
            message: Error message
            tier_name: Name of the cache tier (L1, L2, etc.)
            tier_level: Numeric tier level
            **kwargs: Additional metadata
        """
        enhanced_msg = message
        if tier_name:
            enhanced_msg += f" (tier: {tier_name})"
        if tier_level is not None:
            enhanced_msg += f" (level: {tier_level})"

        super().__init__(enhanced_msg, **kwargs)
        self.tier_name = tier_name
        self.tier_level = tier_level


class ProxyValidationPathError(ProxyValidationError):
    """ProxyValidationError with field path information."""

    def __init__(
        self,
        message: str,
        *,
        field_path: str | None = None,
        expected_type: str | None = None,
        received_value: Any = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with validation path context.

        Args:
            message: Error message
            field_path: Dot-notation path to invalid field (e.g., 'proxy.url')
            expected_type: Expected data type
            received_value: The value that failed validation
            **kwargs: Additional metadata
        """
        enhanced_msg = message
        if field_path:
            enhanced_msg += f" (field: {field_path})"
        if expected_type:
            enhanced_msg += f" (expected: {expected_type})"

        super().__init__(enhanced_msg, **kwargs)
        self.field_path = field_path
        self.expected_type = expected_type
        self.received_value = received_value


class GeoIPLookupError(ProxyWhirlError):
    """Raised when geolocation lookup fails.

    Actionable guidance:
    - Verify GeoIP database is loaded and accessible
    - Check IP address format is valid
    - Ensure GeoIP service/database is up to date
    - Consider fallback to generic location info
    """

    error_code = ProxyErrorCode.GEO_LOOKUP_FAILED

    def __init__(
        self,
        message: str = "GeoIP lookup failed",
        ip_address: str | None = None,
        lookup_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with geolocation context.

        Args:
            message: Error message
            ip_address: IP that failed lookup (redacted if sensitive)
            lookup_type: Type of lookup (country, city, isp, etc.)
            **kwargs: Additional metadata
        """
        enhanced_msg = message
        if lookup_type:
            enhanced_msg += f" (type: {lookup_type})"
        if ip_address and not ip_address.startswith("***"):
            enhanced_msg += f" (IP: {ip_address})"

        if "check database" not in message.lower():
            enhanced_msg += ". Verify GeoIP database is available."

        super().__init__(enhanced_msg, **kwargs)
        self.ip_address = ip_address
        self.lookup_type = lookup_type


class BrowserRenderError(ProxyWhirlError):
    """Raised when browser rendering fails (Playwright).

    Actionable guidance:
    - Verify Playwright browsers are installed
    - Check system resources (memory, disk)
    - Ensure target URL is accessible
    - Review Playwright timeout settings
    - Check for JavaScript errors on target page
    """

    error_code = ProxyErrorCode.BROWSER_ERROR

    def __init__(
        self,
        message: str = "Browser rendering failed",
        browser_type: str | None = None,
        target_url: str | None = None,
        timeout_ms: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with browser context.

        Args:
            message: Error message
            browser_type: Type of browser (chromium, firefox, webkit)
            target_url: URL being rendered (redacted if sensitive)
            timeout_ms: Timeout value in milliseconds
            **kwargs: Additional metadata
        """
        enhanced_msg = message
        if browser_type:
            enhanced_msg += f" (browser: {browser_type})"
        if timeout_ms:
            enhanced_msg += f" (timeout: {timeout_ms}ms)"
        if target_url:
            redacted = redact_url(target_url)
            enhanced_msg += f" (URL: {redacted})"

        if "playwright" not in message.lower():
            enhanced_msg += ". Verify Playwright browsers are installed."

        super().__init__(enhanced_msg, **kwargs)
        self.browser_type = browser_type
        self.target_url = target_url
        self.timeout_ms = timeout_ms


class ProxySourceUnavailableError(ProxyFetchError):
    """Raised when a proxy source is temporarily or permanently unavailable.

    Actionable guidance:
    - Check source status page for known issues
    - Verify network connectivity to source
    - Try alternative proxy sources
    - Contact provider if source is permanently unavailable
    """

    error_code = ProxyErrorCode.SOURCE_UNAVAILABLE

    def __init__(
        self,
        message: str,
        source_name: str | None = None,
        is_permanent: bool = False,
        alternative_sources: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with source unavailability context.

        Args:
            message: Error message
            source_name: Name of unavailable source
            is_permanent: Whether unavailability is permanent
            alternative_sources: List of alternative sources to try
            **kwargs: Additional metadata
        """
        enhanced_msg = message
        if source_name:
            enhanced_msg += f" (source: {source_name})"
        if is_permanent:
            enhanced_msg += " [PERMANENT]"

        if alternative_sources:
            alt_str = ", ".join(alternative_sources[:3])
            enhanced_msg += f" Try: {alt_str}"

        super().__init__(enhanced_msg, **kwargs)
        self.source_name = source_name
        self.is_permanent = is_permanent
        self.alternative_sources = alternative_sources or []


class EventLoopConflictError(ProxyWhirlError):
    """Raised when there's a conflict between async/sync event loops.

    Actionable guidance:
    - Use AsyncProxyWhirl in async context (asyncio, web frameworks)
    - Use ProxyWhirl in sync context (scripts, CLI)
    - Avoid mixing async and sync proxy usage in same thread
    - Check if you're running async code in a sync function
    """

    error_code = ProxyErrorCode.EVENT_LOOP_CONFLICT

    def __init__(
        self,
        message: str = "Event loop conflict",
        current_context: str | None = None,
        expected_context: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with event loop context.

        Args:
            message: Error message
            current_context: Current execution context (sync/async)
            expected_context: Expected execution context
            **kwargs: Additional metadata
        """
        enhanced_msg = message
        if current_context:
            enhanced_msg += f" (current: {current_context})"
        if expected_context:
            enhanced_msg += f" (expected: {expected_context})"

        if "sync" not in message.lower() and "async" not in message.lower():
            enhanced_msg += ". Use ProxyWhirl for sync, AsyncProxyWhirl for async."

        super().__init__(enhanced_msg, **kwargs)
        self.current_context = current_context
        self.expected_context = expected_context


class SchemaMigrationError(ProxyStorageError):
    """Raised when database schema migration fails.

    Actionable guidance:
    - Backup database before retry
    - Check database logs for migration errors
    - Verify database connectivity and permissions
    - Consider manual migration if automated fails
    - Review schema version compatibility
    """

    error_code = ProxyErrorCode.SCHEMA_MIGRATION_ERROR

    def __init__(
        self,
        message: str = "Database schema migration failed",
        from_version: str | None = None,
        to_version: str | None = None,
        recovery_steps: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with migration context.

        Args:
            message: Error message
            from_version: Source schema version
            to_version: Target schema version
            recovery_steps: Suggested recovery steps
            **kwargs: Additional metadata
        """
        enhanced_msg = message
        if from_version and to_version:
            enhanced_msg += f" ({from_version} → {to_version})"
        if "backup" not in message.lower():
            enhanced_msg += " Backup database before retry."

        super().__init__(enhanced_msg, **kwargs)
        self.from_version = from_version
        self.to_version = to_version
        self.recovery_steps = recovery_steps or [
            "1. Backup the database",
            "2. Check database logs for errors",
            "3. Verify database permissions",
            "4. Retry migration manually",
        ]


class TimeoutError(ProxyWhirlError):
    """Raised when operation exceeds timeout.

    Actionable guidance:
    - Check if target is responsive
    - Increase timeout value if appropriate
    - Verify network connectivity
    - Consider async operations for better concurrency
    """

    error_code = ProxyErrorCode.TIMEOUT

    def __init__(
        self,
        message: str,
        timeout_seconds: float | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with timeout context.

        Args:
            message: Error message
            timeout_seconds: Timeout duration in seconds
            operation: Description of timed-out operation
            **kwargs: Additional metadata
        """
        enhanced_msg = message
        if timeout_seconds is not None:
            enhanced_msg += f" (timeout: {timeout_seconds}s)"
        if operation:
            enhanced_msg += f" (operation: {operation})"

        if "increase timeout" not in message.lower():
            enhanced_msg += " Increase timeout or verify target responsiveness."

        super().__init__(enhanced_msg, retry_recommended=True, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class StorageRecoveryError(ProxyStorageError):
    """Raised when storage recovery fails.

    Includes recovery strategies and diagnostic information.
    """

    def __init__(
        self,
        message: str,
        storage_type: str | None = None,
        recovery_strategy: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with recovery context.

        Args:
            message: Error message
            storage_type: Type of storage (sqlite, filesystem, etc.)
            recovery_strategy: Suggested recovery approach
            **kwargs: Additional metadata
        """
        enhanced_msg = message
        if storage_type:
            enhanced_msg += f" (storage: {storage_type})"
        if recovery_strategy:
            enhanced_msg += f" Recovery: {recovery_strategy}"

        super().__init__(enhanced_msg, **kwargs)
        self.storage_type = storage_type
        self.recovery_strategy = recovery_strategy
