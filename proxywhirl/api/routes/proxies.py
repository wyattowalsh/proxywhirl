"""Proxy endpoints for ProxyWhirl API.

Includes all /api/proxies/* endpoints and the /api/request
proxied request endpoint.
"""

# ruff: noqa: B008

from __future__ import annotations

import asyncio
import hashlib
import time
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from loguru import logger

from proxywhirl._proxy_views import (
    ProxyListQuery,
    ProxyView,
    add_proxy_to_rotator,
    find_proxy_async,
    find_proxy_view_async,
    list_proxy_views_async,
    proxy_to_view,
    remove_proxy_from_rotator,
    select_proxy_view,
)
from proxywhirl.api.models import (
    APIResponse,
    CreateProxyRequest,
    HealthCheckRequest,
    HealthCheckResult,
    PaginatedResponse,
    ProxiedRequest,
    ProxiedResponse,
    ProxyResource,
)
from proxywhirl.api.runtime import (
    clear_proxy_metrics,
    get_rotator,
    get_storage,
    limiter,
    record_rotation,
    revalidate_proxied_target_url,
    validate_proxied_request_url,
    verify_api_key,
)
from proxywhirl.exceptions import (
    ProxyAuthenticationError,
    ProxyConnectionError,
    ProxyPoolEmptyError,
    ProxyWhirlError,
)
from proxywhirl.models import HealthStatus, Proxy
from proxywhirl.rotator import ProxyWhirl
from proxywhirl.security import validate_proxy_url_safety
from proxywhirl.settings import APISettings
from proxywhirl.utils import public_proxy_url

router = APIRouter()

_HOP_BY_HOP_HEADERS = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    }
)


def _sanitize_outbound_headers(headers: dict[str, str] | None) -> dict[str, str]:
    """Remove hop-by-hop headers before forwarding to the target origin."""
    if not headers:
        return {}
    return {key: value for key, value in headers.items() if key.lower() not in _HOP_BY_HOP_HEADERS}


def _truncate_response_body(
    text: str,
    max_bytes: int,
    *,
    upstream_truncated: bool = False,
) -> str:
    """Truncate proxied response bodies to a configured byte limit (UTF-8 safe)."""
    encoded = text.encode("utf-8", errors="replace")
    if len(encoded) <= max_bytes and not upstream_truncated:
        return text
    truncated = encoded[:max_bytes].decode("utf-8", errors="ignore")
    return f"{truncated}\n...[truncated]"


def _get_proxy_id(proxy) -> str:
    """Get stable identifier for a proxy."""
    proxy_id = getattr(proxy, "id", None)
    if proxy_id:
        return str(proxy_id)
    return hashlib.sha256(str(proxy.url).encode()).hexdigest()[:16]


def _proxy_resource(
    proxy: Proxy,
    rotator: ProxyWhirl,
    proxy_id: str | None = None,
) -> ProxyResource:
    """Build the shared public proxy representation."""
    view = proxy_to_view(rotator, proxy)
    if proxy_id is not None and proxy_id != view.id:
        view = view.model_copy(update={"id": proxy_id})
    return _proxy_resource_from_view(view)


def _proxy_resource_from_view(view: ProxyView) -> ProxyResource:
    """Adapt the canonical proxy view to the REST response model."""
    return ProxyResource(
        id=view.id,
        url=view.url,
        protocol=view.protocol,
        status=view.status,
        health=view.health,
        stats={
            "total_requests": view.total_requests,
            "successful_requests": view.successful_requests,
            "failed_requests": view.failed_requests,
            "success_rate": view.success_rate,
            "avg_latency_ms": view.avg_latency_ms,
            "country_code": view.country_code,
        },
        created_at=view.created_at,
        updated_at=view.updated_at,
    )


async def _proxy_views_for_status(
    rotator: ProxyWhirl,
    status_filter: str | None,
) -> list[ProxyView]:
    """Return credential-safe proxy views for API list/stream/export endpoints."""
    if not status_filter:
        return await list_proxy_views_async(rotator)

    status_lower = status_filter.lower()
    if status_lower == "healthy":
        return await list_proxy_views_async(
            rotator,
            ProxyListQuery(health=HealthStatus.HEALTHY),
        )
    if status_lower == "active":
        return [view for view in await list_proxy_views_async(rotator) if view.status != "failed"]
    if status_lower == "unhealthy":
        return [
            view
            for view in await list_proxy_views_async(rotator)
            if view.health != HealthStatus.HEALTHY.value
        ]

    return await list_proxy_views_async(rotator)


@router.post(
    "/api/request",
    response_model=APIResponse[ProxiedResponse],
    tags=["Proxied Requests"],
    summary="Make proxied HTTP request",
)
@limiter.limit("50/minute")
async def make_proxied_request(
    request: Request,
    request_data: ProxiedRequest = Depends(validate_proxied_request_url),
    rotator: ProxyWhirl = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ProxiedResponse]:
    """Make an HTTP request through a rotating proxy.

    This endpoint routes your HTTP request through the proxy pool, automatically
    handling rotation and failover.

    SECURITY: All target URLs are validated to prevent SSRF attacks. The following
    are blocked by default:
    - Localhost and loopback addresses (127.0.0.0/8, ::1)
    - Private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
    - Link-local addresses (169.254.0.0/16)
    - Internal domain names (.local, .internal, .lan, .corp)
    - Non-HTTP/HTTPS schemes (file://, data://, etc.)

    Args:
        request_data: Request details (URL, method, headers, body, timeout) - validated for SSRF
        rotator: ProxyWhirl dependency injection
        api_key: API key verification dependency

    Returns:
        APIResponse with proxied response data

    Raises:
        HTTPException: For various error conditions including SSRF protection
    """
    start_time = time.time()
    record_rotation()
    api_settings = APISettings()
    target_url = str(request_data.url)
    revalidate_proxied_target_url(target_url)

    request_kwargs: dict[str, Any] = {
        "headers": _sanitize_outbound_headers(request_data.headers),
        "timeout": request_data.timeout,
        "follow_redirects": False,
    }
    if request_data.body:
        request_kwargs["content"] = request_data.body.encode()

    try:
        response = await asyncio.to_thread(
            rotator._make_request,
            request_data.method.upper(),
            target_url,
            _response_body_limit_bytes=api_settings.max_proxied_response_bytes,
            **request_kwargs,
        )
    except ProxyPoolEmptyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No proxies available in the pool",
        ) from e
    except ProxyConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="All proxy attempts failed",
        ) from e
    except ProxyAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Proxy authentication failed",
        ) from e
    except ProxyWhirlError as e:
        logger.bind(error_type=type(e).__name__).error("ProxyWhirl error in proxied request")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Proxy service temporarily unavailable",
        ) from e
    except Exception as e:
        logger.bind(error_type=type(e).__name__).error("Unexpected error in proxied request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        ) from e

    elapsed_ms = int((time.time() - start_time) * 1000)
    proxy_used = ""
    if rotator.last_used_proxy is not None:
        proxy_used = public_proxy_url(str(rotator.last_used_proxy.url))

    response_data = ProxiedResponse(
        status_code=response.status_code,
        headers=dict(response.headers),
        body=_truncate_response_body(
            response.text,
            api_settings.max_proxied_response_bytes,
            upstream_truncated=bool(
                getattr(response, "extensions", {}).get(
                    "proxywhirl_response_truncated",
                    False,
                )
            ),
        ),
        proxy_used=proxy_used,
        elapsed_ms=elapsed_ms,
    )
    return APIResponse.success(data=response_data)


@router.get(
    "/api/proxies",
    response_model=APIResponse[PaginatedResponse[ProxyResource]],
    tags=["Pool Management"],
    summary="List all proxies",
)
async def list_proxies(
    page: int = 1,
    page_size: int = 50,
    status_filter: str | None = None,
    rotator: ProxyWhirl = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[PaginatedResponse[ProxyResource]]:
    """List all proxies in the pool with pagination and filtering.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page (max 100)
        status_filter: Filter by health status (optional)
        rotator: ProxyWhirl dependency
        api_key: API key verification

    Returns:
        Paginated list of proxy resources
    """
    # Validate pagination
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")

    all_views = await _proxy_views_for_status(rotator, status_filter)

    # Calculate pagination
    total = len(all_views)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_views = all_views[start_idx:end_idx]

    proxy_resources = [_proxy_resource_from_view(view) for view in page_views]

    # Build paginated response
    paginated = PaginatedResponse[ProxyResource](
        items=proxy_resources,
        total=total,
        page=page,
        page_size=page_size,
        has_next=end_idx < total,
        has_prev=page > 1,
    )

    return APIResponse.success(data=paginated)


@router.get(
    "/api/rotate",
    response_model=APIResponse[ProxyResource],
    tags=["Pool Management"],
    summary="Select next proxy",
)
async def rotate_proxy(
    rotator: ProxyWhirl = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ProxyResource]:
    """Select the next proxy without making an outbound target request."""
    try:
        view = await asyncio.to_thread(select_proxy_view, rotator)
    except ProxyWhirlError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No proxies available in the pool",
        ) from exc

    record_rotation()
    return APIResponse.success(data=_proxy_resource_from_view(view))


async def _stream_proxies_async(
    proxy_views: list[ProxyView],
) -> AsyncIterator[str]:
    """Stream proxies as JSON lines asynchronously.

    Args:
        proxy_views: List of credential-safe proxy views to stream

    Yields:
        JSON-formatted proxy resource lines
    """
    import json

    for view in proxy_views:
        try:
            resource_dict = _proxy_resource_from_view(view).model_dump(mode="json")
            yield json.dumps(resource_dict) + "\n"
        except Exception as exc:
            logger.bind(error_type=type(exc).__name__).warning("Failed to stream proxy")
            continue


@router.get(
    "/api/proxies/stream",
    tags=["Pool Management"],
    summary="Stream all proxies as NDJSON",
)
async def stream_proxies(
    status_filter: str | None = None,
    rotator: ProxyWhirl = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> StreamingResponse:
    """Stream all proxies in NDJSON format (newline-delimited JSON).

    Useful for exporting large proxy lists without buffering entire response.
    Each line is a complete JSON object representing one proxy.

    Args:
        status_filter: Filter by health status (optional)
        rotator: ProxyWhirl dependency
        api_key: API key verification

    Returns:
        StreamingResponse with NDJSON content
    """
    proxy_views = await _proxy_views_for_status(rotator, status_filter)

    return StreamingResponse(
        _stream_proxies_async(proxy_views),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/api/proxies/export",
    tags=["Pool Management"],
    summary="Export all proxies as streaming JSON",
)
async def export_proxies(
    status_filter: str | None = None,
    rotator: ProxyWhirl = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> StreamingResponse:
    """Stream all proxies as newline-delimited JSON (NDJSON).

    This endpoint is functionally equivalent to ``/api/proxies/stream``
    and is provided for discoverability under the ``/export`` path.

    Args:
        status_filter: Filter by health status (optional)
        rotator: ProxyWhirl dependency
        api_key: API key verification

    Returns:
        StreamingResponse with NDJSON content
    """
    proxy_views = await _proxy_views_for_status(rotator, status_filter)

    return StreamingResponse(
        _stream_proxies_async(proxy_views),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/api/proxies",
    response_model=APIResponse[ProxyResource],
    status_code=status.HTTP_201_CREATED,
    tags=["Pool Management"],
    summary="Add new proxy",
)
@limiter.limit("10/minute")
async def add_proxy(
    request: Request,
    proxy_data: CreateProxyRequest,
    rotator: ProxyWhirl = Depends(get_rotator),
    storage=Depends(get_storage),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ProxyResource]:
    """Add a new proxy to the pool.

    Args:
        proxy_data: Proxy URL and optional credentials
        rotator: ProxyWhirl dependency
        api_key: API key verification

    Returns:
        Created proxy resource
    """
    # Check for duplicate (thread-safe snapshot)
    proxy_url_str = str(proxy_data.url)
    if await find_proxy_view_async(rotator, proxy_url_str) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Proxy already exists: {public_proxy_url(proxy_url_str)}",
        )

    # Create proxy
    try:
        from pydantic import SecretStr

        safe, reason = validate_proxy_url_safety(proxy_url_str)
        if not safe:
            raise ValueError(f"Proxy URL blocked by security policy: {reason}")

        new_proxy = Proxy(
            url=proxy_url_str,
            username=SecretStr(proxy_data.username) if proxy_data.username else None,
            password=proxy_data.password,
        )

        view = await asyncio.to_thread(add_proxy_to_rotator, rotator, new_proxy)
        if storage:
            await storage.save([new_proxy])

        return APIResponse.success(data=_proxy_resource_from_view(view))

    except Exception as e:
        logger.bind(error_type=type(e).__name__).error("Error adding proxy")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid proxy configuration",
        ) from e


async def _check_proxy_health(
    proxy,
    test_url: str,
    timeout: float = 10.0,
) -> HealthCheckResult:
    """Check health of a single proxy.

    Args:
        proxy: Proxy instance to check
        test_url: URL to use for health check
        timeout: Request timeout in seconds

    Returns:
        HealthCheckResult with test outcome

    Note:
        Each proxy check creates its own client since httpx requires
        proxy configuration at client instantiation time.
    """
    start_time = time.time()
    try:
        # Create client with proxy configuration
        # Note: httpx requires proxy to be set at client creation time
        async with httpx.AsyncClient(
            proxy=str(proxy.url),
            timeout=timeout,
        ) as client:
            async with client.stream("GET", test_url) as response:
                response_status = response.status_code

        latency_ms = int((time.time() - start_time) * 1000)

        return HealthCheckResult(
            proxy_id=_get_proxy_id(proxy),
            status="working" if response_status == 200 else "failed",
            latency_ms=latency_ms,
            error=None,
            tested_at=datetime.now(timezone.utc),
        )
    except Exception:
        latency_ms = int((time.time() - start_time) * 1000)
        return HealthCheckResult(
            proxy_id=_get_proxy_id(proxy),
            status="failed",
            latency_ms=latency_ms,
            error="Proxy validation failed",
            tested_at=datetime.now(timezone.utc),
        )


@router.post(
    "/api/proxies/health-check",
    response_model=APIResponse[list[HealthCheckResult]],
    tags=["Pool Management"],
    summary="Health check proxies",
)
async def health_check_proxies(
    request_data: HealthCheckRequest,
    rotator: ProxyWhirl = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[list[HealthCheckResult]]:
    """Run health checks on specified proxies.

    Args:
        request_data: Optional list of proxy IDs to check
        rotator: ProxyWhirl dependency
        api_key: API key verification

    Returns:
        List of health check results
    """
    api_settings = APISettings()
    all_proxies = await asyncio.to_thread(rotator.pool.get_all_proxies)
    proxies_to_check = all_proxies
    if request_data.proxy_ids:
        proxies_to_check = [p for p in all_proxies if _get_proxy_id(p) in request_data.proxy_ids]

    if len(proxies_to_check) > api_settings.health_check_max_proxies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Too many proxies requested for health check "
                f"(max {api_settings.health_check_max_proxies})"
            ),
        )

    test_url = "https://httpbin.org/get"
    semaphore = asyncio.Semaphore(api_settings.health_check_concurrency)

    async def _bounded_health_check(proxy) -> HealthCheckResult:
        async with semaphore:
            return await _check_proxy_health(proxy, test_url)

    tasks = [_bounded_health_check(proxy) for proxy in proxies_to_check]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    return APIResponse.success(data=results)


# Deprecated - kept for backward compatibility
@router.post(
    "/api/proxies/test",
    response_model=APIResponse[list[HealthCheckResult]],
    tags=["Pool Management"],
    summary="Health check proxies (deprecated)",
    deprecated=True,
)
async def health_check_proxies_deprecated(
    request_data: HealthCheckRequest,
    rotator: ProxyWhirl = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[list[HealthCheckResult]]:
    """Run health checks on specified proxies.

    **DEPRECATED:** Use `/api/proxies/health-check` instead.
    This endpoint is kept for backward compatibility and will be removed in a future version.

    Args:
        request_data: Optional list of proxy IDs to check
        rotator: ProxyWhirl dependency
        api_key: API key verification

    Returns:
        List of health check results
    """
    logger.warning(
        "Deprecated endpoint used: POST /api/proxies/test. "
        "Please migrate to /api/proxies/health-check"
    )
    return await health_check_proxies(request_data, rotator, api_key)


@router.get(
    "/api/proxies/{proxy_id}",
    response_model=APIResponse[ProxyResource],
    tags=["Pool Management"],
    summary="Get proxy by ID",
)
async def get_proxy(
    proxy_id: str,
    rotator: ProxyWhirl = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ProxyResource]:
    """Get details of a specific proxy.

    Args:
        proxy_id: Proxy identifier
        rotator: ProxyWhirl dependency
        api_key: API key verification

    Returns:
        Proxy resource
    """
    # Find proxy by ID (thread-safe snapshot)
    view = await find_proxy_view_async(rotator, proxy_id)
    if view is not None:
        if proxy_id != view.id:
            view = view.model_copy(update={"id": proxy_id})
        return APIResponse.success(data=_proxy_resource_from_view(view))

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Proxy not found: {proxy_id}",
    )


@router.delete(
    "/api/proxies/{proxy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Pool Management"],
    summary="Delete proxy",
)
async def delete_proxy(
    proxy_id: str,
    rotator: ProxyWhirl = Depends(get_rotator),
    storage=Depends(get_storage),
    api_key: None = Depends(verify_api_key),
) -> None:
    """Remove a proxy from the pool.

    Args:
        proxy_id: Proxy identifier
        rotator: ProxyWhirl dependency
        storage: Optional storage dependency
        api_key: API key verification
    """
    stored_proxy = await find_proxy_async(rotator, proxy_id)
    removed = await asyncio.to_thread(remove_proxy_from_rotator, rotator, proxy_id)
    if removed is not None:
        # Persist if storage configured
        if storage:
            storage_url = str(stored_proxy.url) if stored_proxy is not None else str(removed.url)
            await storage.delete(storage_url)
        # Drop per-proxy Prometheus series so proxy-id labels cannot grow unbounded.
        metric_source = stored_proxy if stored_proxy is not None else removed
        stable_id = _get_proxy_id(metric_source)
        clear_proxy_metrics(stable_id)
        if proxy_id != stable_id:
            clear_proxy_metrics(proxy_id)
        return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Proxy not found: {proxy_id}",
    )
