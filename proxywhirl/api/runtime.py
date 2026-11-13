"""Shared runtime state, dependencies, and metrics for the FastAPI adapter."""

# ruff: noqa: B008

from __future__ import annotations

import asyncio
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader
from loguru import logger
from prometheus_client import Counter, Gauge, Histogram
from slowapi import Limiter

from proxywhirl.api.models import ProxiedRequest
from proxywhirl.rotator import ProxyWhirl
from proxywhirl.settings import APISettings
from proxywhirl.storage import SQLiteStorage
from proxywhirl.utils import validate_target_url_safe

_rotator: ProxyWhirl | None = None
_storage: SQLiteStorage | None = None
_config: dict[str, Any] = {}
_app_start_time = datetime.now(timezone.utc)
_last_rotation_time: datetime | None = None


def set_rotator(rotator: ProxyWhirl | None) -> None:
    """Set the process-global API rotator instance."""
    global _rotator
    _rotator = rotator


def get_current_rotator() -> ProxyWhirl | None:
    """Return the process-global API rotator without raising."""
    return _rotator


def get_rotator() -> ProxyWhirl:
    """Get the singleton ProxyWhirl instance."""
    if _rotator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ProxyWhirl not initialized",
        )
    return _rotator


def set_storage(storage: SQLiteStorage | None) -> None:
    """Set the optional process-global API storage instance."""
    global _storage
    _storage = storage


def get_storage() -> SQLiteStorage | None:
    """Get the optional SQLiteStorage instance."""
    return _storage


def set_config(config: dict[str, Any]) -> None:
    """Replace the current API runtime configuration."""
    global _config
    _config = config


def get_config() -> dict[str, Any]:
    """Get current API configuration."""
    return _config


def reset_api_state() -> None:
    """Reset API runtime state for tests and fresh app lifecycles."""
    global _app_start_time, _last_rotation_time
    set_rotator(None)
    set_storage(None)
    set_config({})
    _app_start_time = datetime.now(timezone.utc)
    _last_rotation_time = None
    _tracked_proxy_ids.clear()


def get_app_start_time() -> datetime:
    """Return API process start time."""
    return _app_start_time


def get_last_rotation_time() -> datetime | None:
    """Return the most recent proxy rotation timestamp."""
    return _last_rotation_time


def record_rotation(now: datetime | None = None) -> datetime:
    """Record and return the current proxy rotation timestamp."""
    global _last_rotation_time
    _last_rotation_time = now or datetime.now(timezone.utc)
    return _last_rotation_time


def _get_proxy_id(proxy: Any) -> str:
    """Get stable identifier for a proxy."""
    proxy_id = getattr(proxy, "id", None)
    if proxy_id:
        return str(proxy_id)
    return hashlib.sha256(str(proxy.url).encode()).hexdigest()[:16]


MAX_TRACKED_PROXY_IDS = 512
_OVERFLOW_PROXY_ID = "_other"
_tracked_proxy_ids: set[str] = set()


def _bounded_proxy_id(proxy_id: str) -> str:
    """Bound per-proxy Prometheus labels; overflow collapses to ``_other``."""
    if proxy_id in _tracked_proxy_ids:
        return proxy_id
    if len(_tracked_proxy_ids) < MAX_TRACKED_PROXY_IDS:
        _tracked_proxy_ids.add(proxy_id)
        return proxy_id
    return _OVERFLOW_PROXY_ID


def clear_proxy_metrics(proxy_id: str) -> None:
    """Drop a proxy's metric series when it is deleted from the pool."""
    _tracked_proxy_ids.discard(proxy_id)
    try:
        proxywhirl_circuit_breaker_state.remove(proxy_id)
    except KeyError:
        pass


UNMATCHED_ENDPOINT_LABEL = "unmatched"
_METRIC_METHODS = frozenset({"DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"})
OTHER_METHOD_LABEL = "OTHER"


def metric_method_label(method: str) -> str:
    """Collapse non-standard methods so public routes cannot mint series."""
    normalized = method.upper()
    if normalized in _METRIC_METHODS:
        return normalized
    return OTHER_METHOD_LABEL


def metric_endpoint_label(request: Request) -> str:
    """Return a low-cardinality endpoint label for Prometheus.

    Matched FastAPI/Starlette routes use the path template (e.g.
    ``/api/proxies/{proxy_id}``). Requests without a template — including
    unique ``/api/<uuid>`` 404s — collapse to a single ``unmatched`` label
    so raw paths cannot explode series cardinality.
    """
    route = request.scope.get("route")
    template = getattr(route, "path", None)
    if isinstance(template, str) and template:
        return template
    return UNMATCHED_ENDPOINT_LABEL


proxywhirl_requests_total = Counter(
    "proxywhirl_requests_total",
    "Total number of HTTP requests",
    ["endpoint", "method", "status"],
)

proxywhirl_request_duration_seconds = Histogram(
    "proxywhirl_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint", "method"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
)

proxywhirl_proxies_total = Gauge(
    "proxywhirl_proxies_total",
    "Total number of proxies in the pool",
)

proxywhirl_proxies_healthy = Gauge(
    "proxywhirl_proxies_healthy",
    "Number of healthy proxies in the pool",
)

proxywhirl_circuit_breaker_state = Gauge(
    "proxywhirl_circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 2=half-open)",
    ["proxy_id"],
)


def update_prometheus_metrics() -> None:
    """Update Prometheus metrics for proxy pool and circuit breakers."""
    rotator = get_current_rotator()
    if not rotator:
        return

    proxywhirl_proxies_total.set(rotator.pool.size)
    proxywhirl_proxies_healthy.set(rotator.pool.healthy_count)

    try:
        circuit_breakers = rotator.get_circuit_breaker_states()
        for proxy_id, circuit_breaker in circuit_breakers.items():
            state_value = 0
            if circuit_breaker.state.value == "open":
                state_value = 1
            elif circuit_breaker.state.value == "half_open":
                state_value = 2

            proxywhirl_circuit_breaker_state.labels(proxy_id=_bounded_proxy_id(str(proxy_id))).set(
                state_value
            )
    except Exception as exc:
        logger.bind(error_type=type(exc).__name__).warning(
            "Failed to update circuit breaker metrics"
        )


async def update_prometheus_metrics_async() -> None:
    """Update Prometheus metrics without taking pool locks on the event loop."""
    rotator = get_current_rotator()
    if not rotator:
        return

    total, healthy, circuit_breakers = await asyncio.to_thread(
        lambda: (
            rotator.pool.size,
            rotator.pool.healthy_count,
            rotator.get_circuit_breaker_states(),
        )
    )
    proxywhirl_proxies_total.set(total)
    proxywhirl_proxies_healthy.set(healthy)

    try:
        for proxy_id, circuit_breaker in circuit_breakers.items():
            state_value = 0
            if circuit_breaker.state.value == "open":
                state_value = 1
            elif circuit_breaker.state.value == "half_open":
                state_value = 2

            proxywhirl_circuit_breaker_state.labels(proxy_id=_bounded_proxy_id(str(proxy_id))).set(
                state_value
            )
    except Exception as exc:
        logger.bind(error_type=type(exc).__name__).warning(
            "Failed to update circuit breaker metrics"
        )


def get_rate_limit_key(request: Request) -> str:
    """Extract a spoof-resistant rate limit key from the request."""
    api_key = request.headers.get("X-API-Key")
    if api_key:
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return f"apikey:{key_hash}"

    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"


limiter = Limiter(key_func=get_rate_limit_key, default_limits=[APISettings().rate_limit])
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Fail-closed public allowlist: every /api/* route requires a key unless listed here.
# Prometheus /api/metrics may still be public via PROXYWHIRL_PUBLIC_METRICS
# (middleware short-circuit), independent of this set.
PUBLIC_API_PATHS: frozenset[str] = frozenset(
    {
        "/api/health",
        "/api/ready",
    }
)
# Retained for tests/docs that still name the old force-auth surface.
FORCE_AUTH_EXACT_ROUTES: frozenset[tuple[str, str]] = frozenset()
FORCE_AUTH_PREFIX_ROUTES: frozenset[tuple[str, str]] = frozenset()


def secure_compare_digest(provided: str | None, expected: str) -> bool:
    """Constant-time comparison that rejects length mismatches without raising."""
    if not provided or not expected:
        return False
    if len(provided) != len(expected):
        return False
    return secrets.compare_digest(provided, expected)


def request_requires_api_key(method: str, path: str, *, require_auth: bool) -> bool:
    """Return True when the route must present a valid API key.

    ``/api/*`` is fail-closed: every API route requires a key unless it is on
    :data:`PUBLIC_API_PATHS`. Non-API routes (e.g. ``/protected`` in tests)
    require a key only when ``require_auth`` is true.
    """
    del method  # method is part of the public signature for middleware callers
    if path in PUBLIC_API_PATHS:
        return False
    if path.startswith("/api/"):
        return True
    return require_auth


def verify_api_key(
    request: Request,
    api_key: str | None = Depends(api_key_header),
) -> None:
    """Verify API key when global or per-route force-auth policy applies."""
    api_settings = APISettings()
    path = request.url.path

    if not request_requires_api_key(request.method, path, require_auth=api_settings.require_auth):
        return

    expected_key = api_settings.api_key.get_secret_value() if api_settings.api_key else None
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication not configured",
        )

    if not secure_compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


def validate_proxied_request_url(request_data: ProxiedRequest) -> ProxiedRequest:
    """Validate target URL for SSRF protection before proxying."""
    try:
        validate_target_url_safe(str(request_data.url), allow_private=False)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is blocked by security policy (SSRF protection)",
        )
    return request_data


def revalidate_proxied_target_url(url: str) -> None:
    """Re-run SSRF validation immediately before an outbound proxied request (DNS rebinding)."""
    try:
        validate_target_url_safe(url, allow_private=False)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is blocked by security policy (SSRF protection)",
        )
