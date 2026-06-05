"""Health and monitoring endpoints for ProxyWhirl API.

Includes all health, readiness, status, stats, and metrics endpoints.
"""

# ruff: noqa: B008

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, StreamingResponse
from prometheus_client import REGISTRY, generate_latest

from proxywhirl._proxy_views import list_proxy_views
from proxywhirl.api.models import (
    APIResponse,
    HealthResponse,
    MetricsResponse,
    ReadinessResponse,
    StatusResponse,
)
from proxywhirl.api.runtime import (
    get_app_start_time,
    get_config,
    get_last_rotation_time,
    get_rotator,
    get_storage,
    update_prometheus_metrics,
)
from proxywhirl.models import HealthStatus
from proxywhirl.rotator import ProxyWhirl

router = APIRouter()


@router.get(
    "/api/health",
    response_model=APIResponse[HealthResponse],
    tags=["Monitoring"],
    summary="API health check",
)
async def health_check(
    rotator: ProxyWhirl = Depends(get_rotator),
) -> JSONResponse:
    """Check API health status.

    Returns 200 if healthy, 503 if unhealthy.

    Args:
        rotator: ProxyWhirl dependency

    Returns:
        Health status response
    """
    uptime_seconds = int((datetime.now(timezone.utc) - get_app_start_time()).total_seconds())

    # Determine health based on proxy pool (use thread-safe property)
    total_proxies = rotator.pool.size
    if total_proxies == 0:
        health_status = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        # Check actual health of proxies
        healthy_proxies = rotator.pool.healthy_count
        unhealthy_proxies = rotator.pool.unhealthy_count

        if healthy_proxies == 0:
            health_status = "unhealthy"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        elif unhealthy_proxies > healthy_proxies:
            health_status = "degraded"
            status_code = status.HTTP_200_OK
        else:
            health_status = "healthy"
            status_code = status.HTTP_200_OK

    health_response = HealthResponse(
        status=health_status,
        uptime_seconds=uptime_seconds,
        version="1.0.0",
        timestamp=datetime.now(timezone.utc),
    )

    return JSONResponse(
        status_code=status_code,
        content=APIResponse.success(data=health_response).model_dump(mode="json"),
    )


@router.get(
    "/api/ready",
    response_model=APIResponse[ReadinessResponse],
    tags=["Monitoring"],
    summary="API readiness check",
)
async def readiness_check(
    rotator: ProxyWhirl = Depends(get_rotator),
    storage=Depends(get_storage),
) -> JSONResponse:
    """Check if API is ready to serve requests.

    Returns 200 if ready, 503 if not ready.

    Args:
        rotator: ProxyWhirl dependency
        storage: Optional storage dependency

    Returns:
        Readiness status response
    """
    checks = {
        "proxy_pool_initialized": rotator is not None,
        "storage_connected": storage is not None if storage else True,
    }

    ready = all(checks.values())
    status_code = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE

    readiness_response = ReadinessResponse(
        ready=ready,
        checks=checks,
    )

    return JSONResponse(
        status_code=status_code,
        content=APIResponse.success(data=readiness_response).model_dump(mode="json"),
    )


@router.get(
    "/api/status",
    response_model=APIResponse[StatusResponse],
    tags=["Monitoring"],
    summary="Get system status",
)
async def get_status(
    rotator: ProxyWhirl = Depends(get_rotator),
    storage=Depends(get_storage),
    config: dict = Depends(get_config),
) -> APIResponse[StatusResponse]:
    """Get detailed system status including pool stats.

    Args:
        rotator: ProxyWhirl dependency
        storage: Optional storage dependency
        config: Configuration dependency

    Returns:
        System status response
    """
    from proxywhirl.api.models import ProxyPoolStats

    proxy_views = list_proxy_views(rotator)
    total = len(proxy_views)
    failed = sum(1 for view in proxy_views if view.status == "failed")
    healthy = sum(1 for view in proxy_views if view.health == HealthStatus.HEALTHY.value)
    active = total - failed
    healthy_percentage = (healthy / total * 100) if total > 0 else 0.0

    pool_stats = ProxyPoolStats(
        total=total,
        active=active,
        failed=failed,
        healthy_percentage=healthy_percentage,
        last_rotation=get_last_rotation_time(),
    )

    storage_backend = "memory"
    if storage:
        storage_backend = "sqlite"

    status_response = StatusResponse(
        pool_stats=pool_stats,
        rotation_strategy=config.get("rotation_strategy", "round-robin"),
        storage_backend=storage_backend,
        config_source="environment",
    )

    return APIResponse.success(data=status_response)


@router.get(
    "/api/stats",
    response_model=APIResponse[MetricsResponse],
    tags=["Monitoring"],
    summary="Get performance statistics",
)
async def get_stats(
    rotator: ProxyWhirl = Depends(get_rotator),
) -> APIResponse[MetricsResponse]:
    """Get API performance statistics (general aggregate metrics).

    This endpoint provides high-level performance statistics for the API,
    distinct from the detailed Prometheus metrics available at /api/metrics.

    Args:
        rotator: ProxyWhirl dependency

    Returns:
        Performance statistics response

    Note:
        This endpoint provides aggregate metrics. For detailed metrics, use:
        - /api/metrics - Prometheus format metrics
        - /api/metrics/retries - Retry-specific metrics
    """
    from proxywhirl.api.models import ProxyStats

    proxy_views = list_proxy_views(rotator)
    total_requests = sum(view.total_requests for view in proxy_views)
    total_completed = sum(view.successful_requests for view in proxy_views)
    total_failed = sum(view.failed_requests for view in proxy_views)

    # Calculate overall error rate
    error_rate = (total_failed / total_requests * 100) if total_requests > 0 else 0.0

    # Calculate weighted average latency (average_response_time_ms is already in ms)
    total_latency_weighted = sum(
        view.avg_latency_ms * view.successful_requests
        for view in proxy_views
        if view.avg_latency_ms
    )
    avg_latency_ms = total_latency_weighted / total_completed if total_completed > 0 else 0.0

    # Calculate requests per second based on uptime
    uptime_seconds = (datetime.now(timezone.utc) - get_app_start_time()).total_seconds()
    requests_per_second = total_requests / uptime_seconds if uptime_seconds > 0 else 0.0

    # Build per-proxy stats
    proxy_stats_list = []
    for view in proxy_views:
        proxy_stats_list.append(
            ProxyStats(
                proxy_id=view.id,
                requests=view.total_requests,
                successes=view.successful_requests,
                failures=view.failed_requests,
                avg_latency_ms=view.avg_latency_ms,
            )
        )

    metrics_response = MetricsResponse(
        requests_total=total_requests,
        requests_per_second=round(requests_per_second, 2),
        avg_latency_ms=round(avg_latency_ms, 2),
        error_rate=round(error_rate, 2),
        proxy_stats=proxy_stats_list,
    )

    return APIResponse.success(data=metrics_response)


@router.get(
    "/api/metrics",
    tags=["Monitoring"],
    summary="Prometheus metrics endpoint",
    response_class=StreamingResponse,
    include_in_schema=False,
)
async def metrics() -> StreamingResponse:
    """Expose Prometheus metrics in text format."""
    update_prometheus_metrics()
    metrics_output = generate_latest(REGISTRY)

    async def _metrics_stream() -> AsyncIterator[bytes]:
        yield metrics_output

    return StreamingResponse(
        _metrics_stream(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
