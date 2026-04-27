"""Helper functions for exception handling and error context creation."""

from __future__ import annotations

import traceback
from typing import Any

from proxywhirl.exceptions import (
    ProxyConnectionError,
    ProxyErrorCode,
    ProxyWhirlError,
)


def wrap_connection_error(
    e: Exception,
    proxy_url: str | None = None,
    operation: str | None = None,
    retry_recommended: bool = True,
    attempt_count: int | None = None,
) -> ProxyConnectionError:
    """
    Wrap a raw exception into a ProxyConnectionError with context.

    Args:
        e: The original exception to wrap
        proxy_url: The proxy URL that caused the error
        operation: The operation being performed
        retry_recommended: Whether retrying is recommended
        attempt_count: The current attempt number

    Returns:
        ProxyConnectionError with enriched context
    """
    error_msg = str(e) or e.__class__.__name__
    return ProxyConnectionError(
        f"Connection failed: {error_msg}",
        proxy_url=proxy_url,
        error_type=e.__class__.__name__,
        operation=operation,
        retry_recommended=retry_recommended,
        attempt_count=attempt_count,
        original_exception=str(e),
        traceback_str=traceback.format_exc(),
    )


def wrap_timeout_error(
    e: Exception,
    proxy_url: str | None = None,
    timeout_seconds: float | None = None,
    operation: str | None = None,
    attempt_count: int | None = None,
) -> ProxyWhirlError:
    """
    Wrap a timeout exception with context.

    Args:
        e: The original timeout exception
        proxy_url: The proxy URL that timed out
        timeout_seconds: The timeout value in seconds
        operation: The operation being performed
        attempt_count: The current attempt number

    Returns:
        ProxyWhirlError with timeout context
    """
    error_msg = f"Timeout: {str(e) or e.__class__.__name__}"
    if timeout_seconds:
        error_msg += f" (after {timeout_seconds}s)"

    error = ProxyWhirlError(
        error_msg,
        proxy_url=proxy_url,
        error_type="timeout",
        error_code=ProxyErrorCode.TIMEOUT,
        operation=operation,
        retry_recommended=True,
        attempt_count=attempt_count,
        timeout_seconds=timeout_seconds,
        original_exception=str(e),
    )
    return error


def create_error_context(
    error: Exception,
    *,
    proxy_url: str | None = None,
    operation: str | None = None,
    attempt_count: int | None = None,
    additional_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a comprehensive error context dictionary for logging.

    Args:
        error: The exception to contextualize
        proxy_url: The proxy URL involved
        operation: The operation being performed
        attempt_count: The current attempt number
        additional_context: Extra context to include

    Returns:
        Dictionary with error context
    """
    context = {
        "error_type": error.__class__.__name__,
        "error_message": str(error),
        "proxy_url": proxy_url,
        "operation": operation,
        "attempt_count": attempt_count,
        "traceback": traceback.format_exc(),
    }

    if isinstance(error, ProxyWhirlError):
        context["error_code"] = error.error_code.value
        context["retry_recommended"] = error.retry_recommended
        context["recovery_hint"] = error.recovery_hint

    if additional_context:
        context.update(additional_context)

    return context
