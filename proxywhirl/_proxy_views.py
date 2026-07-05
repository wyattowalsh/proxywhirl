"""Credential-safe proxy view helpers for adapters."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from proxywhirl.models import HealthStatus, Proxy
from proxywhirl.security import redact_url
from proxywhirl.utils import create_proxy_from_url, public_proxy_url

ProxyStatus = Literal["active", "degraded", "failed"]


class ProxyView(BaseModel):
    """Credential-safe proxy representation shared by API, MCP, and CLI adapters."""

    id: str = Field(description="Proxy UUID")
    url: str = Field(description="Credential-stripped proxy URL")
    protocol: str = Field(description="Proxy protocol")
    status: ProxyStatus = Field(description="Operational status derived from circuit state")
    health: str = Field(description="Proxy health status")
    tags: list[str] = Field(default_factory=list, description="Sorted proxy tags")
    total_requests: int = Field(default=0, ge=0, description="Total initiated requests")
    total_successes: int = Field(default=0, ge=0, description="Total successful requests")
    total_failures: int = Field(default=0, ge=0, description="Total failed requests")
    successful_requests: int = Field(default=0, ge=0, description="Total completed requests")
    failed_requests: int = Field(default=0, ge=0, description="Total failed requests")
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Success ratio")
    avg_latency_ms: int = Field(default=0, ge=0, description="Average latency in milliseconds")
    country_code: str | None = Field(default=None, description="ISO 3166-1 alpha-2 country code")
    source_url: str | None = Field(default=None, description="Source URL that provided the proxy")
    created_at: datetime = Field(description="Proxy creation timestamp")
    updated_at: datetime = Field(description="Proxy update timestamp")

    model_config = ConfigDict(frozen=True, extra="forbid")


class ProxyListQuery(BaseModel):
    """Query DTO for read-only proxy pool listing."""

    offset: int = Field(default=0, ge=0, description="Zero-based result offset")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum results to return")
    protocol: str | None = Field(default=None, description="Filter by proxy protocol")
    country_code: str | None = Field(default=None, description="Filter by country code")
    health: HealthStatus | str | None = Field(default=None, description="Filter by health status")
    status: ProxyStatus | None = Field(default=None, description="Filter by operational status")
    tags: set[str] = Field(default_factory=set, description="Require all tags")

    model_config = ConfigDict(frozen=True, extra="forbid")


class ProxyListResult(BaseModel):
    """Paginated proxy list result."""

    items: list[ProxyView] = Field(description="Current page of proxies")
    total: int = Field(ge=0, description="Total matching proxies before pagination")
    offset: int = Field(ge=0, description="Applied result offset")
    limit: int = Field(ge=1, description="Applied result limit")

    model_config = ConfigDict(frozen=True, extra="forbid")


def list_proxy_result(rotator: Any, query: ProxyListQuery | None = None) -> ProxyListResult:
    """Return a filtered, paginated proxy pool snapshot."""
    query = query or ProxyListQuery()
    filtered = list_proxy_views(rotator, query)
    page = filtered[query.offset : query.offset + query.limit]

    return ProxyListResult(items=page, total=len(filtered), offset=query.offset, limit=query.limit)


def list_proxy_views(rotator: Any, query: ProxyListQuery | None = None) -> list[ProxyView]:
    """Return matching credential-safe proxy views from a rotator."""
    query = query or ProxyListQuery()
    views = [proxy_to_view(rotator, proxy) for proxy in _pool_snapshot(rotator)]
    return [view for view in views if _matches_query(view, query)]


def find_proxy(rotator: Any, proxy_ref: UUID | str) -> Proxy | None:
    """Find a proxy by UUID or URL in a rotator pool."""
    proxy_id = _coerce_uuid(proxy_ref)
    proxy_url = str(proxy_ref)

    for proxy in _pool_snapshot(rotator):
        if proxy_id is not None and proxy.id == proxy_id:
            return proxy
        if _urls_match(proxy.url, proxy_url):
            return proxy
    return None


def find_proxy_view(rotator: Any, proxy_ref: UUID | str) -> ProxyView | None:
    """Find a proxy by UUID or URL, returning a credential-safe view."""
    proxy = find_proxy(rotator, proxy_ref)
    return proxy_to_view(rotator, proxy) if proxy else None


def add_proxy_to_rotator(rotator: Any, proxy: Proxy | str) -> ProxyView:
    """Normalize and add a proxy through a sync rotator."""
    proxy_model = _normalize_proxy(proxy)
    rotator.add_proxy(proxy_model)
    return proxy_to_view(rotator, find_proxy(rotator, proxy_model.id) or proxy_model)


async def add_proxy_to_rotator_async(rotator: Any, proxy: Proxy | str) -> ProxyView:
    """Normalize and add a proxy through an async rotator."""
    proxy_model = _normalize_proxy(proxy)
    await rotator.add_proxy(proxy_model)
    return proxy_to_view(rotator, find_proxy(rotator, proxy_model.id) or proxy_model)


def remove_proxy_from_rotator(rotator: Any, proxy_ref: UUID | str) -> ProxyView | None:
    """Remove a proxy through a sync rotator by UUID or URL."""
    proxy = find_proxy(rotator, proxy_ref)
    if proxy is None:
        return None

    view = proxy_to_view(rotator, proxy)
    rotator.remove_proxy(str(proxy.id))
    return view


async def remove_proxy_from_rotator_async(rotator: Any, proxy_ref: UUID | str) -> ProxyView | None:
    """Remove a proxy through an async rotator by UUID or URL."""
    proxy = find_proxy(rotator, proxy_ref)
    if proxy is None:
        return None

    view = proxy_to_view(rotator, proxy)
    await rotator.remove_proxy(str(proxy.id))
    return view


def select_proxy_view(rotator: Any) -> ProxyView:
    """Select the next proxy from a sync rotator and return its public view."""
    selector = getattr(rotator, "get_proxy", None)
    if selector is None:
        selector = rotator._select_proxy_with_circuit_breaker
    return proxy_to_view(rotator, selector())


async def select_proxy_view_async(rotator: Any) -> ProxyView:
    """Select the next proxy from an async rotator and return its public view."""
    return proxy_to_view(rotator, await rotator.get_proxy())


def proxy_to_view(rotator: Any, proxy: Proxy) -> ProxyView:
    """Return a credential-safe public view for a proxy."""
    circuit_breaker = _circuit_breakers(rotator).get(str(proxy.id))
    health = proxy.health_status.value if proxy.health_status else HealthStatus.UNKNOWN.value
    total_requests = max(proxy.total_requests, proxy.requests_started, proxy.requests_completed)
    successful_requests = max(proxy.total_successes, proxy.requests_completed)

    return ProxyView(
        id=str(proxy.id),
        url=public_proxy_url(str(proxy.url)),
        protocol=proxy.protocol or _protocol_from_url(proxy.url),
        status=_status_for_circuit_breaker(circuit_breaker),
        health=health,
        tags=sorted(proxy.tags),
        total_requests=total_requests,
        total_successes=successful_requests,
        total_failures=proxy.total_failures,
        successful_requests=successful_requests,
        failed_requests=proxy.total_failures,
        success_rate=proxy.success_rate,
        avg_latency_ms=int(proxy.average_response_time_ms or 0),
        country_code=proxy.country_code,
        source_url=redact_url(str(proxy.source_url)) if proxy.source_url is not None else None,
        created_at=proxy.created_at,
        updated_at=proxy.updated_at,
    )


def _pool_snapshot(rotator: Any) -> list[Proxy]:
    return rotator.pool.get_all_proxies()


def _circuit_breakers(rotator: Any) -> dict[str, Any]:
    get_states = getattr(rotator, "get_circuit_breaker_states", None)
    if get_states is None:
        return {}
    return get_states()


def _normalize_proxy(proxy: Proxy | str) -> Proxy:
    if isinstance(proxy, Proxy):
        return proxy
    return create_proxy_from_url(proxy)


def _matches_query(view: ProxyView, query: ProxyListQuery) -> bool:
    if query.protocol and view.protocol != query.protocol:
        return False
    if query.health and view.health != _health_value(query.health):
        return False
    if query.country_code and (view.country_code or "").upper() != query.country_code.upper():
        return False
    if query.status and view.status != query.status:
        return False
    return not query.tags or query.tags.issubset(set(view.tags))


def _status_for_circuit_breaker(circuit_breaker: Any | None) -> ProxyStatus:
    if circuit_breaker is None:
        return "active"

    state = getattr(circuit_breaker, "state", None)
    state_value = getattr(state, "value", state)
    if state_value == "open":
        return "failed"
    if state_value == "half_open":
        return "degraded"
    return "active"


def _protocol_from_url(url: str) -> str:
    return str(url).split("://", 1)[0]


def _coerce_uuid(proxy_ref: UUID | str) -> UUID | None:
    if isinstance(proxy_ref, UUID):
        return proxy_ref
    try:
        return UUID(str(proxy_ref))
    except ValueError:
        return None


def _health_value(health: HealthStatus | str) -> str:
    return health.value if isinstance(health, HealthStatus) else health


def _urls_match(proxy_url: str, proxy_ref: str) -> bool:
    return proxy_url == proxy_ref or public_proxy_url(proxy_url) == proxy_ref
