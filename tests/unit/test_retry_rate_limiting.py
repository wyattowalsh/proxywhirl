"""
Unit tests for retry logic helper functions.

Tests cover:
- T094: _is_retryable_http_error helper function
- T095: _wait_with_retry_after helper function with Retry-After parsing
- T096: Exponential backoff with jitter
- T097: Retry-After header capping at 60 seconds
"""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
from tenacity import Future, RetryCallState

from proxywhirl.fetchers import (
    _is_retryable_http_error,
    _wait_with_retry_after,
)


class TestRetryHelperFunctions:
    """Test retry helper functions."""

    def test_is_retryable_http_error_for_retryable_codes(self) -> None:
        """Test _is_retryable_http_error returns True for retryable status codes."""
        for status_code in [429, 503, 502, 504]:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            error = httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)
            assert _is_retryable_http_error(error) is True, (
                f"Expected {status_code} to be retryable"
            )

    def test_is_retryable_http_error_for_non_retryable_codes(self) -> None:
        """Test _is_retryable_http_error returns False for non-retryable status codes."""
        for status_code in [400, 401, 403, 404, 500]:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            error = httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)
            assert _is_retryable_http_error(error) is False, (
                f"Expected {status_code} to NOT be retryable"
            )

    def test_is_retryable_http_error_for_non_http_errors(self) -> None:
        """Test _is_retryable_http_error returns False for non-HTTP errors."""
        assert _is_retryable_http_error(ValueError("Not HTTP error")) is False
        assert _is_retryable_http_error(httpx.TimeoutException("Timeout")) is False

    def test_wait_with_retry_after_header(self) -> None:
        """Test _wait_with_retry_after parses Retry-After header."""
        mock_response = MagicMock()
        mock_response.headers = {"Retry-After": "5"}
        error = httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)

        retry_state = RetryCallState(retry_object=None, fn=None, args=(), kwargs={})
        retry_state.outcome = Future(1)
        retry_state.outcome.set_exception(error)
        retry_state.attempt_number = 1

        wait_time = _wait_with_retry_after(retry_state)
        assert wait_time == 5.0

    def test_wait_with_retry_after_caps_at_60_seconds(self) -> None:
        """Test _wait_with_retry_after caps Retry-After at 60 seconds."""
        mock_response = MagicMock()
        mock_response.headers = {"Retry-After": "120"}
        error = httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)

        retry_state = RetryCallState(retry_object=None, fn=None, args=(), kwargs={})
        retry_state.outcome = Future(1)
        retry_state.outcome.set_exception(error)
        retry_state.attempt_number = 1

        wait_time = _wait_with_retry_after(retry_state)
        assert wait_time == 60.0

    def test_wait_with_exponential_backoff_no_header(self) -> None:
        """Test _wait_with_retry_after uses exponential backoff without header."""
        mock_response = MagicMock()
        mock_response.headers = {}
        error = httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)

        retry_state = RetryCallState(retry_object=None, fn=None, args=(), kwargs={})
        retry_state.outcome = Future(3)
        retry_state.outcome.set_exception(error)
        retry_state.attempt_number = 3

        wait_time = _wait_with_retry_after(retry_state)
        # Should be 2^3 = 8 + jitter (0-25%)
        assert 8.0 <= wait_time <= 10.0

    def test_wait_with_exponential_backoff_caps_at_60(self) -> None:
        """Test exponential backoff caps at 60 seconds for high attempt numbers."""
        mock_response = MagicMock()
        mock_response.headers = {}
        error = httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)

        retry_state = RetryCallState(retry_object=None, fn=None, args=(), kwargs={})
        retry_state.outcome = Future(10)
        retry_state.outcome.set_exception(error)
        retry_state.attempt_number = 10  # 2^10 = 1024, should cap at 60

        wait_time = _wait_with_retry_after(retry_state)
        assert 60.0 <= wait_time <= 75.0  # 60 + max 25% jitter

    def test_wait_with_invalid_retry_after_falls_back(self) -> None:
        """Test invalid Retry-After falls back to exponential backoff."""
        mock_response = MagicMock()
        mock_response.headers = {"Retry-After": "invalid"}
        error = httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)

        retry_state = RetryCallState(retry_object=None, fn=None, args=(), kwargs={})
        retry_state.outcome = Future(1)
        retry_state.outcome.set_exception(error)
        retry_state.attempt_number = 1

        wait_time = _wait_with_retry_after(retry_state)
        # Should fall back to exponential backoff (2^1 = 2 + jitter)
        assert 2.0 <= wait_time <= 2.5
