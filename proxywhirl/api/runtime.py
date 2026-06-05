"""Shared runtime state, dependencies, and metrics for the FastAPI adapter."""

# ruff: noqa: B008

from __future__ import annotations

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

            proxywhirl_circuit_breaker_state.labels(proxy_id=proxy_id).set(state_value)
    except Exception as exc:
        logger.warning(f"Failed to update circuit breaker metrics: {exc}")


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


def verify_api_key(api_key: str | None = Depends(api_key_header)) -> None:
    """Verify API key if authentication is required."""
    api_settings = APISettings()

    if not api_settings.require_auth:
        return

    expected_key = api_settings.api_key.get_secret_value() if api_settings.api_key else None
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication not configured",
        )

    if not api_key or not secrets.compare_digest(api_key, expected_key):
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
