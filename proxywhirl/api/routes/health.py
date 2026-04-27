"""Health and monitoring endpoints for ProxyWhirl API.

Includes all health, readiness, status, stats, and metrics endpoints.
"""

# ruff: noqa: B008

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response, StreamingResponse
from prometheus_client import REGISTRY, generate_latest

from proxywhirl.api.core import (
    _app_start_time,
    _get_proxy_id,
    _last_rotation_time,
    get_config,
    get_rotator,
    get_storage,
    update_prometheus_metrics,
    verify_api_key,
)
from proxywhirl.api.models import (
    APIResponse,
    HealthResponse,
    MetricsResponse,
    ReadinessResponse,
    StatusResponse,
)
from proxywhirl.rotator import ProxyWhirl

router = APIRouter()


@router.get(
    "/api/v1/health",
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
    uptime_seconds = int((datetime.now(timezone.utc) - _app_start_time).total_seconds())

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
    "/api/v1/ready",
    response_model=APIResponse[ReadinessResponse],
    tags=["Monitoring"],
    summary="API readiness check",
)
async def readiness_check(
    rotator: ProxyWhirl = Depends(get_rotator),
    storage = Depends(get_storage),
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
    "/api/v1/status",
    response_model=APIResponse[StatusResponse],
    tags=["Monitoring"],
    summary="Get system status",
)
async def get_status(
    rotator: ProxyWhirl = Depends(get_rotator),
    storage = Depends(get_storage),
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

    # Use thread-safe property
    total = rotator.pool.size
    # Calculate active/failed based on circuit breaker states and health checks
    circuit_breakers = rotator.get_circuit_breaker_states()
    failed = sum(1 for cb in circuit_breakers.values() if cb.state.value == "OPEN")
    healthy = rotator.pool.healthy_count
    active = total - failed
    healthy_percentage = (healthy / total * 100) if total > 0 else 0.0

    pool_stats = ProxyPoolStats(
        total=total,
        active=active,
        failed=failed,
        healthy_percentage=healthy_percentage,
        last_rotation=_last_rotation_time,
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
    "/api/v1/stats",
    response_model=APIResponse[MetricsResponse],
    tags=["Monitoring"],
    summary="Get performance statistics",
)
async def get_stats(
    rotator: ProxyWhirl = Depends(get_rotator),
) -> APIResponse[MetricsResponse]:
    """Get API performance statistics (general aggregate metrics).

    This endpoint provides high-level performance statistics for the API,
    distinct from the detailed Prometheus metrics available at /metrics.

    Args:
        rotator: ProxyWhirl dependency

    Returns:
        Performance statistics response

    Note:
        This endpoint provides aggregate metrics. For detailed metrics, use:
        - /metrics - Prometheus format metrics
        - /api/v1/metrics/retries - Retry-specific metrics
        - /metrics/retry - Comprehensive retry metrics with JSON/Prometheus format
    """
    from proxywhirl.api.models import ProxyStats

    # Calculate aggregate metrics from all proxies (thread-safe snapshot)
    all_proxies = rotator.pool.get_all_proxies()
    total_requests = sum(p.requests_started for p in all_proxies)
    total_completed = sum(p.requests_completed for p in all_proxies)
    total_failed = sum(p.total_failures for p in all_proxies)

    # Calculate overall error rate
    error_rate = (total_failed / total_requests * 100) if total_requests > 0 else 0.0

    # Calculate weighted average latency (average_response_time_ms is already in ms)
    total_latency_weighted = sum(
        (p.average_response_time_ms or 0) * p.requests_completed
        for p in all_proxies
        if p.average_response_time_ms
    )
    avg_latency_ms = total_latency_weighted / total_completed if total_completed > 0 else 0.0

    # Calculate requests per second based on uptime
    uptime_seconds = (datetime.now(timezone.utc) - _app_start_time).total_seconds()
    requests_per_second = total_requests / uptime_seconds if uptime_seconds > 0 else 0.0

    # Build per-proxy stats
    proxy_stats_list = []
    for proxy in all_proxies:
        proxy_stats_list.append(
            ProxyStats(
                proxy_id=_get_proxy_id(proxy),
                requests=proxy.requests_started,
                successes=proxy.requests_completed,
                failures=proxy.total_failures,
                avg_latency_ms=int(proxy.average_response_time_ms or 0),
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
    "/metrics",
    tags=["Monitoring"],
    summary="Prometheus metrics endpoint",
    response_class=StreamingResponse,
    include_in_schema=False,
)
async def metrics() -> StreamingResponse:
    """Expose Prometheus metrics in text format.

    This endpoint returns metrics in Prometheus exposition format, including:
    - proxywhirl_requests_total: Total HTTP requests by endpoint, method, and status
    - proxywhirl_request_duration_seconds: Request duration histogram
    - proxywhirl_proxies_total: Total proxies in pool
    - proxywhirl_proxies_healthy: Number of healthy proxies
    - proxywhirl_circuit_breaker_state: Circuit breaker states (0=closed, 1=open, 2=half-open)

    Returns:
        Prometheus metrics in text format as a streaming response
    """
    # Update proxy pool and circuit breaker metrics before returning
    update_prometheus_metrics()

    # Generate Prometheus text format
    metrics_output = generate_latest(REGISTRY)

    async def _metrics_stream() -> AsyncIterator[bytes]:
        yield metrics_output

    return StreamingResponse(
        _metrics_stream(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@router.get(
    "/metrics/retry",
    tags=["Monitoring"],
    summary="Get retry statistics with optional Prometheus format",
)
async def get_retry_metrics_endpoint(
    format: str | None = None,
    hours: int = 24,
    api_key: None = Depends(verify_api_key),
) -> Response:
    """Get retry statistics in JSON or Prometheus format.

    This endpoint provides comprehensive retry metrics including:
    - Total retry attempts
    - Success rate by attempt number
    - Time-series data (hourly aggregates)
    - Per-proxy statistics

    Args:
        format: Output format ('prometheus' for Prometheus text format, default: JSON)
        hours: Number of hours of data to include (default: 24)
        api_key: API key verification

    Returns:
        Retry metrics in requested format
    """
    import proxywhirl.api.core as _api_core

    if not _api_core._rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _api_core._rotator.get_retry_metrics()

    # Get all metrics data
    summary = metrics.get_summary()
    timeseries_data = metrics.get_timeseries(hours=hours)
    stats_by_proxy = metrics.get_by_proxy(hours=hours)

    # Prometheus format
    if format and format.lower() == "prometheus":
        lines = []

        # Total retries
        lines.append("# HELP proxywhirl_retry_total Total number of retry attempts")
        lines.append("# TYPE proxywhirl_retry_total counter")
        lines.append(f"proxywhirl_retry_total {summary['total_retries']}")
        lines.append("")

        # Success by attempt
        lines.append(
            "# HELP proxywhirl_retry_success_by_attempt Successful requests by attempt number"
        )
        lines.append("# TYPE proxywhirl_retry_success_by_attempt gauge")
        for attempt_num, count in summary["success_by_attempt"].items():
            lines.append(f'proxywhirl_retry_success_by_attempt{{attempt="{attempt_num}"}} {count}')
        lines.append("")

        # Circuit breaker events count
        lines.append(
            "# HELP proxywhirl_circuit_breaker_events_total Total circuit breaker state changes"
        )
        lines.append("# TYPE proxywhirl_circuit_breaker_events_total counter")
        lines.append(
            f"proxywhirl_circuit_breaker_events_total {summary['circuit_breaker_events_count']}"
        )
        lines.append("")

        # Per-proxy metrics
        lines.append("# HELP proxywhirl_retry_proxy_attempts Total retry attempts per proxy")
        lines.append("# TYPE proxywhirl_retry_proxy_attempts gauge")
        for proxy_id, stats in stats_by_proxy.items():
            # Escape proxy_id for Prometheus label
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_retry_proxy_attempts{{proxy_id="{safe_proxy_id}"}} {stats["total_attempts"]}'
            )
        lines.append("")

        lines.append("# HELP proxywhirl_retry_proxy_success Total successful requests per proxy")
        lines.append("# TYPE proxywhirl_retry_proxy_success gauge")
        for proxy_id, stats in stats_by_proxy.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_retry_proxy_success{{proxy_id="{safe_proxy_id}"}} {stats["success_count"]}'
            )
        lines.append("")

        lines.append("# HELP proxywhirl_retry_proxy_failure Total failed requests per proxy")
        lines.append("# TYPE proxywhirl_retry_proxy_failure gauge")
        for proxy_id, stats in stats_by_proxy.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_retry_proxy_failure{{proxy_id="{safe_proxy_id}"}} {stats["failure_count"]}'
            )
        lines.append("")

        lines.append(
            "# HELP proxywhirl_retry_proxy_avg_latency Average latency per proxy in seconds"
        )
        lines.append("# TYPE proxywhirl_retry_proxy_avg_latency gauge")
        for proxy_id, stats in stats_by_proxy.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_retry_proxy_avg_latency{{proxy_id="{safe_proxy_id}"}} {stats["avg_latency"]:.6f}'
            )
        lines.append("")

        prometheus_output = "\n".join(lines)
        return Response(
            content=prometheus_output,
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    # JSON format (default)

    # Build comprehensive response
    response_data = {
        "summary": {
            "total_retries": summary["total_retries"],
            "success_by_attempt": {str(k): v for k, v in summary["success_by_attempt"].items()},
            "circuit_breaker_events_count": summary["circuit_breaker_events_count"],
            "retention_hours": summary["retention_hours"],
        },
        "timeseries": [
            {
                "timestamp": point["timestamp"],
                "total_requests": point["total_requests"],
                "total_retries": point["total_retries"],
                "success_rate": point["success_rate"],
                "avg_latency": point["avg_latency"],
            }
            for point in timeseries_data
        ],
        "by_proxy": {
            proxy_id: {
                "proxy_id": stats["proxy_id"],
                "total_attempts": stats["total_attempts"],
                "success_count": stats["success_count"],
                "failure_count": stats["failure_count"],
                "avg_latency": stats["avg_latency"],
                "circuit_breaker_opens": stats["circuit_breaker_opens"],
            }
            for proxy_id, stats in stats_by_proxy.items()
        },
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=APIResponse.success(data=response_data).model_dump(mode="json"),
    )


@router.get(
    "/metrics/circuit-breaker",
    tags=["Monitoring"],
    summary="Get circuit breaker states with optional Prometheus format",
)
async def get_circuit_breaker_metrics_endpoint(
    format: str | None = None,
    hours: int = 24,
    api_key: None = Depends(verify_api_key),
) -> Response:
    """Get circuit breaker states and events in JSON or Prometheus format.

    This endpoint provides circuit breaker information including:
    - Current state of all circuit breakers
    - State change events (history)
    - Failure counts and thresholds

    Args:
        format: Output format ('prometheus' for Prometheus text format, default: JSON)
        hours: Number of hours of event history to include (default: 24)
        api_key: API key verification

    Returns:
        Circuit breaker metrics in requested format
    """
    import proxywhirl.api.core as _api_core

    if not _api_core._rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    # Get circuit breaker states
    circuit_breakers = _api_core._rotator.get_circuit_breaker_states()

    # Get circuit breaker events
    metrics = _api_core._rotator.get_retry_metrics()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    events = [event for event in metrics.circuit_breaker_events if event.timestamp >= cutoff]

    # Prometheus format
    if format and format.lower() == "prometheus":
        lines = []

        # Circuit breaker state
        lines.append(
            "# HELP proxywhirl_circuit_breaker_state Circuit breaker state (0=closed, 1=open, 2=half_open)"
        )
        lines.append("# TYPE proxywhirl_circuit_breaker_state gauge")
        for proxy_id, cb in circuit_breakers.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            # Map state to numeric value
            state_value = 0
            if cb.state.value == "open":
                state_value = 1
            elif cb.state.value == "half_open":
                state_value = 2
            lines.append(
                f'proxywhirl_circuit_breaker_state{{proxy_id="{safe_proxy_id}"}} {state_value}'
            )
        lines.append("")

        # Failure count
        lines.append(
            "# HELP proxywhirl_circuit_breaker_failure_count Current failure count within window"
        )
        lines.append("# TYPE proxywhirl_circuit_breaker_failure_count gauge")
        for proxy_id, cb in circuit_breakers.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_circuit_breaker_failure_count{{proxy_id="{safe_proxy_id}"}} {cb.failure_count}'
            )
        lines.append("")

        # Failure threshold
        lines.append(
            "# HELP proxywhirl_circuit_breaker_failure_threshold Failure threshold before opening"
        )
        lines.append("# TYPE proxywhirl_circuit_breaker_failure_threshold gauge")
        for proxy_id, cb in circuit_breakers.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_circuit_breaker_failure_threshold{{proxy_id="{safe_proxy_id}"}} {cb.failure_threshold}'
            )
        lines.append("")

        # State change events count
        lines.append(
            "# HELP proxywhirl_circuit_breaker_state_changes_total Total state changes in time window"
        )
        lines.append("# TYPE proxywhirl_circuit_breaker_state_changes_total counter")
        lines.append(f"proxywhirl_circuit_breaker_state_changes_total {len(events)}")
        lines.append("")

        # Count of opens per proxy
        from collections import defaultdict

        opens_by_proxy: dict[str, int] = defaultdict(int)
        for event in events:
            if event.to_state.value == "open":
                opens_by_proxy[event.proxy_id] += 1

        lines.append(
            "# HELP proxywhirl_circuit_breaker_opens_total Total circuit breaker opens per proxy"
        )
        lines.append("# TYPE proxywhirl_circuit_breaker_opens_total counter")
        for proxy_id, count in opens_by_proxy.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_circuit_breaker_opens_total{{proxy_id="{safe_proxy_id}"}} {count}'
            )
        lines.append("")

        prometheus_output = "\n".join(lines)
        return Response(
            content=prometheus_output,
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    # JSON format (default)
    from proxywhirl.api.models import CircuitBreakerEventResponse, CircuitBreakerResponse

    # Build circuit breaker states response
    states = []
    for proxy_id, cb in circuit_breakers.items():
        states.append(
            CircuitBreakerResponse(
                proxy_id=proxy_id,
                state=cb.state.value,
                failure_count=cb.failure_count,
                failure_threshold=cb.failure_threshold,
                window_duration=cb.window_duration,
                timeout_duration=cb.timeout_duration,
                next_test_time=datetime.fromtimestamp(cb.next_test_time, timezone.utc)
                if cb.next_test_time
                else None,
                last_state_change=cb.last_state_change,
            )
        )

    # Build events response
    event_responses = [
        CircuitBreakerEventResponse(
            proxy_id=event.proxy_id,
            from_state=event.from_state.value,
            to_state=event.to_state.value,
            timestamp=event.timestamp,
            failure_count=event.failure_count,
        )
        for event in events
    ]

    response_data = {
        "states": [state.model_dump(mode="json") for state in states],
        "events": [event.model_dump(mode="json") for event in event_responses],
        "total_events": len(event_responses),
        "hours": hours,
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=APIResponse.success(data=response_data).model_dump(mode="json"),
    )
