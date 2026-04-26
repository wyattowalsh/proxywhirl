"""
Type aliases for common callback signatures and string literals in ProxyWhirl.

This module defines standardized callback type aliases to ensure consistency
across the codebase and improve IDE support. It also includes Literal types
for common string constants (actions, log levels, etc.).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Literal, TypeAlias

import httpx

from proxywhirl.cache.models import CacheEntry
from proxywhirl.models import Proxy, ProxyPool, Session

# ============================================================================
# STRING LITERAL TYPES
# ============================================================================

PoolAction: TypeAlias = Literal["list", "add", "remove", "test", "stats"]
"""Pool management actions in CLI."""

ConfigAction: TypeAlias = Literal["show", "get", "set", "init"]
"""Configuration management actions in CLI."""

BatchAction: TypeAlias = Literal["add", "remove", "update"]
"""Batch operation actions in CLI."""

ProxywhirlAction: TypeAlias = Literal[
    "list",
    "rotate",
    "status",
    "recommend",
    "health",
    "reset_cb",
    "add",
    "remove",
    "fetch",
    "validate",
    "set_strategy",
]
"""MCP proxywhirl tool actions."""

LogLevel: TypeAlias = Literal["info", "debug", "warning", "error"]
"""Standard logging levels."""

CacheFormat: TypeAlias = Literal["json", "jsonl", "csv"]
"""Cache export formats."""

Protocol: TypeAlias = Literal["http", "https", "socks4", "socks5"]
"""Proxy protocol types."""

ProxyProtocol: TypeAlias = Literal["http", "https", "socks4", "socks5"]
"""Proxy protocol literal type."""

ProxyType: TypeAlias = Literal["free", "semi-paid", "premium"]
"""Proxy pricing tier types."""

PerformanceLevel: TypeAlias = Literal["high", "medium", "low"]
"""Performance recommendation levels."""

ValidationLevel: TypeAlias = Literal["basic", "standard", "full"]
"""Proxy validation strictness levels."""

# ============================================================================
# HTTP REQUEST CALLBACKS
# ============================================================================

HttpRequestCallback: TypeAlias = Callable[[], httpx.Response]
"""Synchronous HTTP request callback that returns a response."""

AsyncHttpRequestCallback: TypeAlias = Callable[[], Awaitable[httpx.Response]]
"""Asynchronous HTTP request callback that returns a response."""

# ============================================================================
# CACHE CALLBACKS
# ============================================================================

CacheEvictionCallback: TypeAlias = Callable[[str, CacheEntry], None]
"""Cache eviction callback: (key, entry) -> None"""

CacheHitCallback: TypeAlias = Callable[[str, CacheEntry], None]
"""Cache hit callback: (key, entry) -> None"""

CacheMissCallback: TypeAlias = Callable[[str], None]
"""Cache miss callback: (key) -> None"""

# ============================================================================
# PROXY MANAGEMENT CALLBACKS
# ============================================================================

ProxyAddCallback: TypeAlias = Callable[[Proxy], Awaitable[None]]
"""Async callback for adding a proxy: (proxy) -> None"""

ProxyRemoveCallback: TypeAlias = Callable[[str], Awaitable[None]]
"""Async callback for removing a proxy: (proxy_id) -> None"""

ProxyValidationCallback: TypeAlias = Callable[[Proxy], Awaitable[bool]]
"""Async proxy validation callback: (proxy) -> is_valid"""

ProxySelectionCallback: TypeAlias = Callable[[ProxyPool], Proxy]
"""Proxy selection callback: (pool) -> selected_proxy"""

# ============================================================================
# HEALTH CHECK CALLBACKS
# ============================================================================

HealthCheckCallback: TypeAlias = Callable[[Proxy], Awaitable[bool]]
"""Health check callback: (proxy) -> is_healthy"""

HealthStatusChangeCallback: TypeAlias = Callable[[Proxy, str, str], Awaitable[None]]
"""Health status change callback: (proxy, old_status, new_status) -> None"""

# ============================================================================
# SESSION CALLBACKS
# ============================================================================

SessionCreateCallback: TypeAlias = Callable[[Session], Awaitable[None]]
"""Session creation callback: (session) -> None"""

SessionCloseCallback: TypeAlias = Callable[[str], Awaitable[None]]
"""Session closure callback: (session_id) -> None"""

# Legacy aliases for backward compatibility
SessionCallback: TypeAlias = SessionCreateCallback
SessionEvictionCallback: TypeAlias = SessionCloseCallback

# ============================================================================
# ERROR AND RETRY CALLBACKS
# ============================================================================

ErrorCallback: TypeAlias = Callable[[Exception], Awaitable[None]]
"""Error handler callback: (exception) -> None"""

RetryCallback: TypeAlias = Callable[[int, Exception], Awaitable[None]]
"""Retry callback: (attempt_number, exception) -> None"""

ErrorHandlerCallback: TypeAlias = ErrorCallback

# ============================================================================
# LOGGING AND MONITORING CALLBACKS
# ============================================================================

LogCallback: TypeAlias = Callable[[str, str], None]
"""Logging callback: (level, message) -> None"""

MetricsCallback: TypeAlias = Callable[[str, float], None]
"""Metrics callback: (metric_name, value) -> None"""

LoggingCallback: TypeAlias = LogCallback

# ============================================================================
# MCP/MIDDLEWARE CALLBACKS
# ============================================================================

MiddlewareNextCallback: TypeAlias = Callable[[object], Awaitable[object]]
"""Middleware next callback: (context) -> result"""

ToolCallCallback: TypeAlias = Callable[[str, dict[str, object]], Awaitable[object]]
"""Tool call callback: (tool_name, args) -> result"""

MCPMiddlewareCallback: TypeAlias = MiddlewareNextCallback
