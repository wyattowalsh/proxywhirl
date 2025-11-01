"""
Contextual logging utilities for ProxyWhirl.

This module provides context binding helpers that attach metadata (request IDs,
proxy URLs, strategy names) to log entries for correlation and debugging.
"""

import contextvars
from typing import Any, Optional
from uuid import uuid4

from loguru import logger


# Context variables for request-scoped metadata
_request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
_operation_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "operation", default=None
)
_proxy_url_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "proxy_url", default=None
)
_strategy_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "strategy", default=None
)
_source_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "source", default=None
)
_user_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "user_id", default=None
)


def generate_request_id() -> str:
    """
    Generate a unique request ID.

    Returns:
        UUID string for request correlation
    """
    return str(uuid4())


def set_request_id(request_id: Optional[str] = None) -> str:
    """
    Set the request ID for the current context.

    Args:
        request_id: Request ID to set (generates new one if None)

    Returns:
        The request ID that was set
    """
    if request_id is None:
        request_id = generate_request_id()
    _request_id_var.set(request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """
    Get the current request ID.

    Returns:
        Current request ID or None
    """
    return _request_id_var.get()


def set_operation(operation: str) -> None:
    """
    Set the operation type for the current context.

    Args:
        operation: Operation identifier (e.g., "proxy_selection", "health_check")
    """
    _operation_var.set(operation)


def get_operation() -> Optional[str]:
    """
    Get the current operation type.

    Returns:
        Current operation or None
    """
    return _operation_var.get()


def set_proxy_url(proxy_url: str) -> None:
    """
    Set the proxy URL for the current context.

    Args:
        proxy_url: Proxy URL being used
    """
    _proxy_url_var.set(proxy_url)


def get_proxy_url() -> Optional[str]:
    """
    Get the current proxy URL.

    Returns:
        Current proxy URL or None
    """
    return _proxy_url_var.get()


def set_strategy(strategy: str) -> None:
    """
    Set the rotation strategy for the current context.

    Args:
        strategy: Strategy name (e.g., "round_robin", "weighted")
    """
    _strategy_var.set(strategy)


def get_strategy() -> Optional[str]:
    """
    Get the current rotation strategy.

    Returns:
        Current strategy or None
    """
    return _strategy_var.get()


def set_source(source: str) -> None:
    """
    Set the proxy source for the current context.

    Args:
        source: Source identifier (e.g., "free_proxy_list", "premium_provider")
    """
    _source_var.set(source)


def get_source() -> Optional[str]:
    """
    Get the current proxy source.

    Returns:
        Current source or None
    """
    return _source_var.get()


def set_user_id(user_id: str) -> None:
    """
    Set the user ID for the current context.

    Args:
        user_id: User identifier for multi-tenant scenarios
    """
    _user_id_var.set(user_id)


def get_user_id() -> Optional[str]:
    """
    Get the current user ID.

    Returns:
        Current user ID or None
    """
    return _user_id_var.get()


def get_context() -> dict[str, Any]:
    """
    Get all current context values as a dictionary.

    Returns:
        Dictionary of context values (excluding None values)
    """
    context: dict[str, Any] = {}
    
    request_id = get_request_id()
    if request_id is not None:
        context["request_id"] = request_id
    
    operation = get_operation()
    if operation is not None:
        context["operation"] = operation
    
    proxy_url = get_proxy_url()
    if proxy_url is not None:
        context["proxy_url"] = proxy_url
    
    strategy = get_strategy()
    if strategy is not None:
        context["strategy"] = strategy
    
    source = get_source()
    if source is not None:
        context["source"] = source
    
    user_id = get_user_id()
    if user_id is not None:
        context["user_id"] = user_id
    
    return context


def clear_context() -> None:
    """
    Clear all context variables.

    Useful for cleanup after request completion or in test teardown.
    """
    _request_id_var.set(None)
    _operation_var.set(None)
    _proxy_url_var.set(None)
    _strategy_var.set(None)
    _source_var.set(None)
    _user_id_var.set(None)


def log_with_context(level: str, message: str, **extra: Any) -> None:
    """
    Log a message with current context automatically included.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Log message
        **extra: Additional fields to include
    """
    # Merge context with extra fields
    context = get_context()
    merged = {**context, **extra}
    
    # Use loguru's bind to attach context
    log_func = getattr(logger.bind(**merged), level.lower())
    log_func(message)


class LogContext:
    """
    Context manager for scoped logging context.

    Example:
        >>> with LogContext(operation="proxy_selection", strategy="weighted"):
        ...     logger.info("Selecting proxy")
        ...     # Logs will include operation and strategy
    """

    def __init__(
        self,
        request_id: Optional[str] = None,
        operation: Optional[str] = None,
        proxy_url: Optional[str] = None,
        strategy: Optional[str] = None,
        source: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Initialize logging context.

        Args:
            request_id: Request ID (generates new one if None)
            operation: Operation type
            proxy_url: Proxy URL
            strategy: Strategy name
            source: Source identifier
            user_id: User identifier
        """
        self.request_id = request_id
        self.operation = operation
        self.proxy_url = proxy_url
        self.strategy = strategy
        self.source = source
        self.user_id = user_id
        
        # Store previous values for restoration
        self._prev_request_id: Optional[str] = None
        self._prev_operation: Optional[str] = None
        self._prev_proxy_url: Optional[str] = None
        self._prev_strategy: Optional[str] = None
        self._prev_source: Optional[str] = None
        self._prev_user_id: Optional[str] = None

    def __enter__(self) -> "LogContext":
        """Enter context and set variables."""
        # Save previous values
        self._prev_request_id = get_request_id()
        self._prev_operation = get_operation()
        self._prev_proxy_url = get_proxy_url()
        self._prev_strategy = get_strategy()
        self._prev_source = get_source()
        self._prev_user_id = get_user_id()
        
        # Set new values
        if self.request_id is not None:
            set_request_id(self.request_id)
        elif self._prev_request_id is None:
            # Generate new request ID if none exists
            set_request_id()
        
        if self.operation is not None:
            set_operation(self.operation)
        
        if self.proxy_url is not None:
            set_proxy_url(self.proxy_url)
        
        if self.strategy is not None:
            set_strategy(self.strategy)
        
        if self.source is not None:
            set_source(self.source)
        
        if self.user_id is not None:
            set_user_id(self.user_id)
        
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context and restore previous variables."""
        # Restore previous values
        _request_id_var.set(self._prev_request_id)
        _operation_var.set(self._prev_operation)
        _proxy_url_var.set(self._prev_proxy_url)
        _strategy_var.set(self._prev_strategy)
        _source_var.set(self._prev_source)
        _user_id_var.set(self._prev_user_id)


def bind_context(**context: Any) -> Any:
    """
    Bind context values to loguru for current scope.

    Args:
        **context: Context key-value pairs

    Returns:
        Loguru logger with bound context

    Example:
        >>> log = bind_context(request_id="req-123", operation="test")
        >>> log.info("Message with context")
    """
    # Get current context and merge with provided
    current = get_context()
    merged = {**current, **context}
    return logger.bind(**merged)
