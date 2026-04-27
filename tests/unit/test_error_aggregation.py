"""Tests for error aggregation and multi-error reporting."""

from __future__ import annotations

import pytest

from proxywhirl.exceptions import (
    CircuitBreakerOpenError,
    MaxRetriesExhaustedError,
    ProxyConnectionError,
    ProxyFetchError,
    ProxyPoolEmptyError,
    ProxyValidationError,
    ProxyWhirlError,
)


class ErrorAggregator:
    """Aggregates multiple errors for batch reporting."""

    def __init__(self) -> None:
        """Initialize error aggregator."""
        self.errors: list[Exception] = []

    def add_error(self, error: Exception) -> None:
        """Add error to collection."""
        self.errors.append(error)

    def get_errors(self) -> list[Exception]:
        """Get all errors."""
        return self.errors.copy()

    def has_errors(self) -> bool:
        """Check if any errors present."""
        return len(self.errors) > 0

    def error_count(self) -> int:
        """Get total error count."""
        return len(self.errors)

    def get_error_types(self) -> dict[str, int]:
        """Get error count by type."""
        type_counts: dict[str, int] = {}
        for error in self.errors:
            error_type = type(error).__name__
            type_counts[error_type] = type_counts.get(error_type, 0) + 1
        return type_counts

    def get_error_messages(self) -> list[str]:
        """Get all error messages."""
        return [str(error) for error in self.errors]

    def clear_errors(self) -> None:
        """Clear all errors."""
        self.errors.clear()

    def filter_errors(self, error_type: type[Exception]) -> list[Exception]:
        """Filter errors by type."""
        return [e for e in self.errors if isinstance(e, error_type)]

    def raise_if_has_errors(self) -> None:
        """Raise MultipleErrors if any errors present."""
        if self.errors:
            raise MultipleErrors(self.errors)


class MultipleErrors(ProxyWhirlError):
    """Exception for aggregating multiple errors."""

    def __init__(self, errors: list[Exception]) -> None:
        """Initialize with list of errors."""
        self.errors = errors
        message = f"Multiple errors occurred ({len(errors)} total):\n"
        for i, error in enumerate(errors, 1):
            message += f"{i}. {type(error).__name__}: {error}\n"
        super().__init__(message)


class TestErrorAggregation:
    """Test error aggregation functionality."""

    def test_add_single_error(self) -> None:
        """Test adding single error."""
        aggregator = ErrorAggregator()
        error = ProxyConnectionError("Connection failed")
        aggregator.add_error(error)

        assert aggregator.error_count() == 1
        assert aggregator.has_errors() is True
        assert aggregator.get_errors() == [error]

    def test_add_multiple_errors(self) -> None:
        """Test adding multiple errors."""
        aggregator = ErrorAggregator()
        error1 = ProxyConnectionError("Connection 1 failed")
        error2 = ProxyValidationError("Validation failed")
        error3 = ProxyFetchError("Fetch failed")

        aggregator.add_error(error1)
        aggregator.add_error(error2)
        aggregator.add_error(error3)

        assert aggregator.error_count() == 3
        assert aggregator.has_errors() is True

    def test_get_errors_returns_copy(self) -> None:
        """Test get_errors returns a copy."""
        aggregator = ErrorAggregator()
        error = ProxyPoolEmptyError("Pool empty")
        aggregator.add_error(error)

        errors1 = aggregator.get_errors()
        errors2 = aggregator.get_errors()

        assert errors1 == errors2
        assert errors1 is not errors2

    def test_error_count_accuracy(self) -> None:
        """Test error count is accurate."""
        aggregator = ErrorAggregator()
        for i in range(5):
            aggregator.add_error(ProxyConnectionError(f"Error {i}"))

        assert aggregator.error_count() == 5

    def test_get_error_types(self) -> None:
        """Test grouping errors by type."""
        aggregator = ErrorAggregator()
        aggregator.add_error(ProxyConnectionError("Conn 1"))
        aggregator.add_error(ProxyConnectionError("Conn 2"))
        aggregator.add_error(ProxyValidationError("Validation"))
        aggregator.add_error(ProxyFetchError("Fetch"))

        types = aggregator.get_error_types()

        assert types["ProxyConnectionError"] == 2
        assert types["ProxyValidationError"] == 1
        assert types["ProxyFetchError"] == 1

    def test_get_error_messages(self) -> None:
        """Test getting error messages."""
        aggregator = ErrorAggregator()
        msg1 = "Connection failed"
        msg2_base = "Validation failed"

        aggregator.add_error(ProxyConnectionError(msg1))
        aggregator.add_error(ProxyValidationError(msg2_base))

        messages = aggregator.get_error_messages()

        assert len(messages) == 2
        assert msg1 in messages
        assert any(msg2_base in msg for msg in messages)

    def test_clear_errors(self) -> None:
        """Test clearing all errors."""
        aggregator = ErrorAggregator()
        aggregator.add_error(ProxyConnectionError("Error 1"))
        aggregator.add_error(ProxyConnectionError("Error 2"))

        assert aggregator.has_errors() is True
        aggregator.clear_errors()
        assert aggregator.has_errors() is False
        assert aggregator.error_count() == 0

    def test_filter_errors_by_type(self) -> None:
        """Test filtering errors by type."""
        aggregator = ErrorAggregator()
        aggregator.add_error(ProxyConnectionError("Conn 1"))
        aggregator.add_error(ProxyConnectionError("Conn 2"))
        aggregator.add_error(ProxyValidationError("Validation"))
        aggregator.add_error(ProxyFetchError("Fetch"))

        conn_errors = aggregator.filter_errors(ProxyConnectionError)

        assert len(conn_errors) == 2
        assert all(isinstance(e, ProxyConnectionError) for e in conn_errors)

    def test_filter_errors_returns_empty(self) -> None:
        """Test filtering returns empty list when no matches."""
        aggregator = ErrorAggregator()
        aggregator.add_error(ProxyConnectionError("Conn"))
        aggregator.add_error(ProxyValidationError("Validation"))

        fetch_errors = aggregator.filter_errors(ProxyFetchError)

        assert fetch_errors == []

    def test_raise_if_has_errors_empty(self) -> None:
        """Test no error raised when aggregator is empty."""
        aggregator = ErrorAggregator()
        # Should not raise
        aggregator.raise_if_has_errors()

    def test_raise_if_has_errors_with_errors(self) -> None:
        """Test MultipleErrors raised when errors present."""
        aggregator = ErrorAggregator()
        aggregator.add_error(ProxyConnectionError("Error 1"))
        aggregator.add_error(ProxyValidationError("Error 2"))

        with pytest.raises(MultipleErrors) as exc_info:
            aggregator.raise_if_has_errors()

        assert len(exc_info.value.errors) == 2

    def test_multiple_errors_exception(self) -> None:
        """Test MultipleErrors exception behavior."""
        error1 = ProxyConnectionError("Connection failed")
        error2 = ProxyValidationError("Validation failed")
        errors = [error1, error2]

        exc = MultipleErrors(errors)

        assert exc.errors == errors
        assert "2 total" in str(exc)
        assert "ProxyConnectionError" in str(exc)
        assert "ProxyValidationError" in str(exc)

    def test_multiple_errors_with_various_types(self) -> None:
        """Test MultipleErrors with different error types."""
        errors = [
            ProxyPoolEmptyError("Pool empty"),
            CircuitBreakerOpenError("Circuit open"),
            MaxRetriesExhaustedError("Max retries"),
        ]

        exc = MultipleErrors(errors)

        assert len(exc.errors) == 3
        assert all(isinstance(e, ProxyWhirlError) for e in exc.errors)

    def test_multiple_errors_message_format(self) -> None:
        """Test MultipleErrors message formatting."""
        errors = [
            ProxyConnectionError("First error"),
            ProxyValidationError("Second error"),
        ]

        exc = MultipleErrors(errors)
        message = str(exc)

        assert "Multiple errors occurred (2 total)" in message
        assert "1. ProxyConnectionError: First error" in message
        assert "2. ProxyValidationError: Second error" in message

    def test_error_aggregator_context_manager(self) -> None:
        """Test error aggregator as context manager."""

        class ErrorCollector:
            def __init__(self) -> None:
                self.aggregator = ErrorAggregator()

            def __enter__(self) -> ErrorCollector:
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore
                if exc_type is not None and exc_val is not None:
                    self.aggregator.add_error(exc_val)
                return False

        collector = ErrorCollector()
        try:
            with collector:
                raise ProxyConnectionError("Test error")
        except ProxyConnectionError:
            pass

        assert collector.aggregator.error_count() == 1

    def test_aggregator_preserves_error_metadata(self) -> None:
        """Test aggregator preserves error metadata."""
        error = ProxyConnectionError("Connection failed")
        error.metadata = {"attempt": 3, "timeout": 30}  # type: ignore

        aggregator = ErrorAggregator()
        aggregator.add_error(error)

        retrieved_error = aggregator.get_errors()[0]
        assert hasattr(retrieved_error, "metadata")
        assert retrieved_error.metadata == {"attempt": 3, "timeout": 30}  # type: ignore
