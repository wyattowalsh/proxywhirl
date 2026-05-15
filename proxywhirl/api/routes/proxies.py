"""Proxy endpoints for ProxyWhirl API.

Includes all /api/proxies/* endpoints and the /api/request
proxied request endpoint.
"""

# ruff: noqa: B008

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from loguru import logger

import proxywhirl.api.core as _api_core
from proxywhirl.api.core import (
    _get_proxy_id,
    get_rotator,
    get_storage,
    limiter,
    validate_proxied_request_url,
    verify_api_key,
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
from proxywhirl.exceptions import ProxyWhirlError
from proxywhirl.models import Proxy
from proxywhirl.rotator import ProxyWhirl

router = APIRouter()


def _public_proxy_url(proxy_url: str) -> str:
    """Return a proxy URL without userinfo credentials."""
    parsed = urlsplit(proxy_url)
    netloc = parsed.netloc.rsplit("@", 1)[-1]
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))


def _proxy_resource(
    proxy: Proxy,
    rotator: ProxyWhirl,
    proxy_id: str | None = None,
) -> ProxyResource:
    """Build the shared public proxy representation."""
    resource_id = proxy_id or _get_proxy_id(proxy)
    circuit_breaker = rotator.get_circuit_breaker_states().get(resource_id)

    if circuit_breaker and circuit_breaker.state.value == "open":
        proxy_status = "failed"
    elif circuit_breaker and circuit_breaker.state.value == "half_open":
        proxy_status = "degraded"
    else:
        proxy_status = "active"

    health_value = proxy.health_status.value if proxy.health_status else "unknown"

    return ProxyResource(
        id=resource_id,
        url=_public_proxy_url(str(proxy.url)),
        protocol=proxy.protocol or "http",
        status=proxy_status,
        health=health_value,
        stats={
            "total_requests": proxy.requests_started,
            "successful_requests": proxy.requests_completed,
            "failed_requests": proxy.total_failures,
            "avg_latency_ms": int(proxy.average_response_time_ms or 0),
        },
        created_at=proxy.created_at,
        updated_at=proxy.updated_at,
    )


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
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # Get next proxy from rotator using strategy
            proxy = rotator.strategy.select(rotator.pool)
            if not proxy:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No proxies available in the pool",
                )

            # Track last rotation time
            _api_core._last_rotation_time = datetime.now(timezone.utc)

            # Build proxy URL for httpx
            proxy_url = str(proxy.url)

            # Make the HTTP request through the proxy
            async with httpx.AsyncClient(proxy=proxy_url) as client:
                response = await client.request(
                    method=request_data.method,
                    url=str(request_data.url),
                    headers=request_data.headers,
                    content=request_data.body.encode() if request_data.body else None,
                    timeout=request_data.timeout,
                )

            elapsed_ms = int((time.time() - start_time) * 1000)

            # Build successful response
            response_data = ProxiedResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text,
                proxy_used=_public_proxy_url(proxy_url),
                elapsed_ms=elapsed_ms,
            )

            return APIResponse.success(data=response_data)

        except (httpx.ProxyError, httpx.ConnectError, httpx.TimeoutException) as e:
            # Proxy-related error, try next proxy
            logger.warning(f"Proxy attempt {attempt + 1} failed: {e}")
            continue

        except ProxyWhirlError as e:
            # Handle ProxyWhirl-specific errors
            logger.error(f"ProxyWhirl error in proxied request: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Proxy service temporarily unavailable",
            ) from e

        except Exception as e:
            logger.error(f"Unexpected error in proxied request: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred",
            ) from e

    # All retries exhausted
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"All {max_retries} proxy attempts failed",
    )


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

    # Get all proxies (thread-safe snapshot)
    all_proxies = rotator.pool.get_all_proxies()

    # Apply status filter if provided
    if status_filter:
        status_lower = status_filter.lower()
        if status_lower == "healthy":
            all_proxies = [p for p in all_proxies if p.is_healthy]
        elif status_lower == "unhealthy":
            all_proxies = [p for p in all_proxies if not p.is_healthy]
        elif status_lower == "active":
            # Active means proxy is available (not in a failed circuit breaker state)
            circuit_breakers = rotator.get_circuit_breaker_states()
            all_proxies = [
                p
                for p in all_proxies
                if _get_proxy_id(p) not in circuit_breakers
                or circuit_breakers[_get_proxy_id(p)].state.value != "open"
            ]

    # Calculate pagination
    total = len(all_proxies)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_proxies = all_proxies[start_idx:end_idx]

    proxy_resources = [_proxy_resource(proxy, rotator) for proxy in page_proxies]

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
        proxy = rotator.strategy.select(rotator.pool)
    except ProxyWhirlError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No proxies available in the pool",
        ) from exc

    if not proxy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No proxies available in the pool",
        )

    _api_core._last_rotation_time = datetime.now(timezone.utc)
    return APIResponse.success(data=_proxy_resource(proxy, rotator))


async def _stream_proxies_async(
    all_proxies: list,
    rotator: ProxyWhirl,
) -> AsyncIterator[str]:
    """Stream proxies as JSON lines asynchronously.

    Args:
        all_proxies: List of all proxies to stream
        rotator: ProxyWhirl rotator instance for circuit breaker state

    Yields:
        JSON-formatted proxy resource lines
    """
    import json

    for proxy in all_proxies:
        try:
            resource_dict = _proxy_resource(proxy, rotator).model_dump(mode="json")
            yield json.dumps(resource_dict) + "\n"
        except Exception as e:
            logger.warning(f"Failed to stream proxy: {e}")
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
    # Get all proxies (thread-safe snapshot)
    all_proxies = rotator.pool.get_all_proxies()

    # Apply status filter if provided
    if status_filter:
        status_lower = status_filter.lower()
        if status_lower == "healthy":
            all_proxies = [p for p in all_proxies if p.is_healthy]
        elif status_lower == "unhealthy":
            all_proxies = [p for p in all_proxies if not p.is_healthy]
        elif status_lower == "active":
            # Active means proxy is available (not in a failed circuit breaker state)
            circuit_breakers = rotator.get_circuit_breaker_states()
            all_proxies = [
                p
                for p in all_proxies
                if _get_proxy_id(p) not in circuit_breakers
                or circuit_breakers[_get_proxy_id(p)].state.value != "open"
            ]

    return StreamingResponse(
        _stream_proxies_async(all_proxies, rotator),
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
    # Reuse the stream_proxies implementation
    all_proxies = rotator.pool.get_all_proxies()

    if status_filter:
        status_lower = status_filter.lower()
        if status_lower == "healthy":
            all_proxies = [p for p in all_proxies if p.is_healthy]
        elif status_lower == "unhealthy":
            all_proxies = [p for p in all_proxies if not p.is_healthy]
        elif status_lower == "active":
            circuit_breakers = rotator.get_circuit_breaker_states()
            all_proxies = [
                p
                for p in all_proxies
                if _get_proxy_id(p) not in circuit_breakers
                or circuit_breakers[_get_proxy_id(p)].state.value != "open"
            ]

    return StreamingResponse(
        _stream_proxies_async(all_proxies, rotator),
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
    for existing_proxy in rotator.pool.get_all_proxies():
        if str(existing_proxy.url) == proxy_url_str:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Proxy already exists: {proxy_url_str}",
            )

    # Create proxy
    try:
        from pydantic import SecretStr

        new_proxy = Proxy(
            url=proxy_url_str,
            username=SecretStr(proxy_data.username) if proxy_data.username else None,
            password=proxy_data.password,
        )

        # Add to rotator
        rotator.add_proxy(new_proxy)

        return APIResponse.success(data=_proxy_resource(new_proxy, rotator))

    except Exception as e:
        logger.error(f"Error adding proxy: {e}", exc_info=True)
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
            response = await client.get(test_url)

        latency_ms = int((time.time() - start_time) * 1000)

        return HealthCheckResult(
            proxy_id=_get_proxy_id(proxy),
            status="working" if response.status_code == 200 else "failed",
            latency_ms=latency_ms,
            error=None,
            tested_at=datetime.now(timezone.utc),
        )
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return HealthCheckResult(
            proxy_id=_get_proxy_id(proxy),
            status="failed",
            latency_ms=latency_ms,
            error=str(e),
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
    # Determine which proxies to check (thread-safe snapshot)
    all_proxies = rotator.pool.get_all_proxies()
    proxies_to_check = all_proxies
    if request_data.proxy_ids:
        proxies_to_check = [p for p in all_proxies if _get_proxy_id(p) in request_data.proxy_ids]

    test_url = "https://httpbin.org/get"

    # Run health checks concurrently
    # Note: Each proxy check creates its own client since httpx requires
    # proxy configuration at client instantiation time (not per-request)
    tasks = [_check_proxy_health(proxy, test_url) for proxy in proxies_to_check]
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
    for proxy in rotator.pool.get_all_proxies():
        if _get_proxy_id(proxy) == proxy_id:
            return APIResponse.success(data=_proxy_resource(proxy, rotator, proxy_id))

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
    # Find and remove proxy (thread-safe)
    # First find the proxy by ID
    target_proxy = None
    for proxy in rotator.pool.get_all_proxies():
        if _get_proxy_id(proxy) == proxy_id:
            target_proxy = proxy
            break

    if target_proxy:
        # Use thread-safe remove method
        rotator.pool.remove_proxy(target_proxy.id)

        # Persist if storage configured
        if storage:
            await storage.save(rotator.pool.get_all_proxies())

        return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Proxy not found: {proxy_id}",
    )
