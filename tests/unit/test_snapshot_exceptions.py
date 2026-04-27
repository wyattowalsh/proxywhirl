"""Snapshot tests for exception messages to catch regressions in error formatting.

Uses syrupy for snapshot testing. Snapshots are stored in __snapshots__/ and tracked in git.
"""

from syrupy.assertion import SnapshotAssertion

from proxywhirl.exceptions import (
    CircuitBreakerOpenError,
    MaxRetriesExhaustedError,
    ProxyAuthenticationError,
    ProxyConnectionError,
    ProxyFetchError,
    ProxyPoolEmptyError,
    ProxyStorageError,
    ProxyValidationError,
    ProxyWhirlError,
    RateLimitExceededError,
    redact_url,
)


class TestExceptionMessageSnapshots:
    """Test that exception messages remain consistent (no regressions)."""

    def test_proxy_pool_empty_error_message(self, snapshot: SnapshotAssertion) -> None:
        """Verify ProxyPoolEmptyError message format."""
        exc = ProxyPoolEmptyError("No proxies available in pool")
        assert str(exc) == snapshot

    def test_proxy_validation_error_message(self, snapshot: SnapshotAssertion) -> None:
        """Verify ProxyValidationError message format."""
        exc = ProxyValidationError("Invalid proxy URL format")
        assert str(exc) == snapshot

    def test_proxy_connection_error_message(self, snapshot: SnapshotAssertion) -> None:
        """Verify ProxyConnectionError message format."""
        exc = ProxyConnectionError("Connection timeout", "http://proxy.example.com:8080")
        assert str(exc) == snapshot

    def test_proxy_authentication_error_message(self, snapshot: SnapshotAssertion) -> None:
        """Verify ProxyAuthenticationError message format."""
        exc = ProxyAuthenticationError("Invalid credentials", "proxy.example.com:8080")
        assert str(exc) == snapshot

    def test_proxy_fetch_error_message(self, snapshot: SnapshotAssertion) -> None:
        """Verify ProxyFetchError message format."""
        exc = ProxyFetchError("Failed to fetch proxies from source")
        assert str(exc) == snapshot

    def test_proxy_storage_error_message(self, snapshot: SnapshotAssertion) -> None:
        """Verify ProxyStorageError message format."""
        exc = ProxyStorageError("Database connection failed")
        assert str(exc) == snapshot

    def test_max_retries_exhausted_error_message(self, snapshot: SnapshotAssertion) -> None:
        """Verify MaxRetriesExhaustedError message format."""
        exc = MaxRetriesExhaustedError("Max retries (3) exceeded")
        assert str(exc) == snapshot

    def test_circuit_breaker_open_error_message(self, snapshot: SnapshotAssertion) -> None:
        """Verify CircuitBreakerOpenError message format."""
        exc = CircuitBreakerOpenError("Circuit breaker is open")
        assert str(exc) == snapshot

    def test_rate_limit_exceeded_error_message(self, snapshot: SnapshotAssertion) -> None:
        """Verify RateLimitExceededError message format."""
        exc = RateLimitExceededError("Rate limit exceeded: 100 requests per minute")
        assert str(exc) == snapshot

    def test_exception_str_representation(self, snapshot: SnapshotAssertion) -> None:
        """Verify exception str() representation doesn't change."""
        exc = ProxyWhirlError("Base error message")
        assert str(exc) == snapshot

    def test_exception_repr(self, snapshot: SnapshotAssertion) -> None:
        """Verify exception repr() is consistent."""
        exc = ProxyWhirlError("Base error with repr")
        assert repr(exc) == snapshot

    def test_nested_exception_context(self, snapshot: SnapshotAssertion) -> None:
        """Verify exception with __cause__ is handled correctly."""
        try:
            raise ValueError("Original error")
        except ValueError as original_err:
            try:
                raise ProxyFetchError("Fetch failed") from original_err
            except ProxyFetchError as exc:
                # Capture the formatted exception string
                assert str(exc) == snapshot

    def test_redact_url_snapshot(self, snapshot: SnapshotAssertion) -> None:
        """Verify redacted URL format doesn't change."""
        urls = [
            "http://user:pass@proxy.example.com:8080",
            "https://proxy.example.com:8080",
            "socks5://proxy.example.com:1080",
            "http://proxy.example.com:8080/path?query=value",
        ]
        results = {url: redact_url(url) for url in urls}
        assert results == snapshot


class TestExceptionHierarchy:
    """Test exception inheritance and hierarchy snapshots."""

    def test_exception_mro(self, snapshot: SnapshotAssertion) -> None:
        """Verify method resolution order for exceptions."""
        exc = ProxyConnectionError("test")
        mro = [cls.__name__ for cls in type(exc).__mro__]
        assert mro == snapshot

    def test_all_exception_inheritance(self, snapshot: SnapshotAssertion) -> None:
        """Verify all custom exceptions inherit from ProxyWhirlError."""
        exceptions_to_test = [
            ProxyPoolEmptyError("test"),
            ProxyValidationError("test"),
            ProxyConnectionError("test"),
            ProxyAuthenticationError("test"),
            ProxyFetchError("test"),
            ProxyStorageError("test"),
            MaxRetriesExhaustedError("test"),
            CircuitBreakerOpenError("test"),
            RateLimitExceededError("test"),
        ]

        inheritance_tree = {
            exc.__class__.__name__: isinstance(exc, ProxyWhirlError) for exc in exceptions_to_test
        }
        assert inheritance_tree == snapshot
