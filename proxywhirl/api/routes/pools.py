"""Configuration, retry, and circuit breaker endpoints for ProxyWhirl API.

Includes all /api/config/*, /api/retry/*, /api/circuit-breakers/*,
and /api/metrics/* endpoints.
"""

# ruff: noqa: B008

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger

import proxywhirl.api.core as _api_core
from proxywhirl.api.core import (
    get_config,
    get_rotator,
    limiter,
    verify_api_key,
)
from proxywhirl.api.models import (
    APIResponse,
    CircuitBreakerEventResponse,
    CircuitBreakerResponse,
    ConfigurationSettings,
    ProxyRetryStatsResponse,
    RetryMetricsResponse,
    RetryPolicyRequest,
    RetryPolicyResponse,
    TimeSeriesResponse,
    UpdateConfigRequest,
)
from proxywhirl.rotator import ProxyWhirl

router = APIRouter()


@router.get(
    "/api/config",
    response_model=APIResponse[ConfigurationSettings],
    tags=["Configuration"],
    summary="Get current configuration",
)
async def get_configuration(
    config: dict = Depends(get_config),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ConfigurationSettings]:
    """Get current API configuration.

    Args:
        config: Configuration dependency
        api_key: API key verification

    Returns:
        Current configuration settings
    """
    from proxywhirl.api.models import RateLimitConfig

    config_settings = ConfigurationSettings(
        rotation_strategy=config.get("rotation_strategy", "round-robin"),
        timeout=config.get("timeout", 30),
        max_retries=config.get("max_retries", 3),
        rate_limits=RateLimitConfig(**config.get("rate_limits", {})),
        auth_enabled=config.get("auth_enabled", False),
        cors_origins=config.get("cors_origins", ["*"]),
    )

    return APIResponse.success(data=config_settings)


@router.put(
    "/api/config",
    response_model=APIResponse[ConfigurationSettings],
    tags=["Configuration"],
    summary="Update configuration",
)
@limiter.limit("5/minute")
async def update_configuration(
    request: Request,
    update_data: UpdateConfigRequest,
    config: dict = Depends(get_config),
    rotator: ProxyWhirl = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ConfigurationSettings]:
    """Update API configuration at runtime.

    Args:
        update_data: Configuration updates (partial)
        config: Configuration dependency
        rotator: ProxyWhirl dependency
        api_key: API key verification

    Returns:
        Updated configuration settings
    """
    from proxywhirl.api.models import RateLimitConfig

    # Apply updates
    if update_data.rotation_strategy is not None:
        config["rotation_strategy"] = update_data.rotation_strategy
        # Update rotator strategy dynamically using hot-swap
        try:
            rotator.set_strategy(update_data.rotation_strategy, atomic=True)
            logger.info(f"Rotation strategy updated to: {update_data.rotation_strategy}")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid rotation strategy: {str(e)}",
            ) from e

    if update_data.timeout is not None:
        config["timeout"] = update_data.timeout

    if update_data.max_retries is not None:
        config["max_retries"] = update_data.max_retries

    if update_data.rate_limits is not None:
        config["rate_limits"] = update_data.rate_limits.model_dump()

    if update_data.cors_origins is not None:
        config["cors_origins"] = update_data.cors_origins

    # Return updated config
    config_settings = ConfigurationSettings(
        rotation_strategy=config.get("rotation_strategy", "round-robin"),
        timeout=config.get("timeout", 30),
        max_retries=config.get("max_retries", 3),
        rate_limits=RateLimitConfig(**config.get("rate_limits", {})),
        auth_enabled=config.get("auth_enabled", False),
        cors_origins=config.get("cors_origins", ["*"]),
    )

    return APIResponse.success(data=config_settings)


@router.get(
    "/api/retry/policy",
    response_model=APIResponse[RetryPolicyResponse],
    tags=["Retry & Failover"],
    summary="Get global retry policy",
)
async def get_retry_policy(
    api_key: None = Depends(verify_api_key),
) -> APIResponse[RetryPolicyResponse]:
    """Get the current global retry policy configuration.

    Returns:
        Current retry policy settings
    """
    from proxywhirl.api.models import RetryPolicyResponse

    if not _api_core._rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    policy = _api_core._rotator.retry_policy

    response = RetryPolicyResponse(
        max_attempts=policy.max_attempts,
        backoff_strategy=policy.backoff_strategy.value,
        base_delay=policy.base_delay,
        multiplier=policy.multiplier,
        max_backoff_delay=policy.max_backoff_delay,
        jitter=policy.jitter,
        retry_status_codes=policy.retry_status_codes,
        timeout=policy.timeout,
        retry_non_idempotent=policy.retry_non_idempotent,
    )

    return APIResponse.success(data=response)


@router.put(
    "/api/retry/policy",
    response_model=APIResponse[RetryPolicyResponse],
    tags=["Retry & Failover"],
    summary="Update global retry policy",
)
async def update_retry_policy(
    policy_request: RetryPolicyRequest,
    api_key: None = Depends(verify_api_key),
) -> APIResponse[RetryPolicyResponse]:
    """Update the global retry policy configuration.

    Args:
        policy_request: New retry policy settings

    Returns:
        Updated retry policy
    """
    from proxywhirl.api.models import RetryPolicyResponse
    from proxywhirl.retry import BackoffStrategy, RetryPolicy

    if not _api_core._rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    # Build new policy from request (only update provided fields)
    current_policy = _api_core._rotator.retry_policy

    policy_dict = current_policy.model_dump()

    if policy_request.max_attempts is not None:
        policy_dict["max_attempts"] = policy_request.max_attempts

    if policy_request.backoff_strategy is not None:
        policy_dict["backoff_strategy"] = BackoffStrategy(policy_request.backoff_strategy)

    if policy_request.base_delay is not None:
        policy_dict["base_delay"] = policy_request.base_delay

    if policy_request.multiplier is not None:
        policy_dict["multiplier"] = policy_request.multiplier

    if policy_request.max_backoff_delay is not None:
        policy_dict["max_backoff_delay"] = policy_request.max_backoff_delay

    if policy_request.jitter is not None:
        policy_dict["jitter"] = policy_request.jitter

    if policy_request.retry_status_codes is not None:
        policy_dict["retry_status_codes"] = policy_request.retry_status_codes

    if policy_request.timeout is not None:
        policy_dict["timeout"] = policy_request.timeout

    if policy_request.retry_non_idempotent is not None:
        policy_dict["retry_non_idempotent"] = policy_request.retry_non_idempotent

    # Create new policy
    try:
        new_policy = RetryPolicy(**policy_dict)
        _api_core._rotator.retry_policy = new_policy
        _api_core._rotator.retry_executor.retry_policy = new_policy

        response = RetryPolicyResponse(
            max_attempts=new_policy.max_attempts,
            backoff_strategy=new_policy.backoff_strategy.value,
            base_delay=new_policy.base_delay,
            multiplier=new_policy.multiplier,
            max_backoff_delay=new_policy.max_backoff_delay,
            jitter=new_policy.jitter,
            retry_status_codes=new_policy.retry_status_codes,
            timeout=new_policy.timeout,
            retry_non_idempotent=new_policy.retry_non_idempotent,
        )

        return APIResponse.success(data=response)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid policy configuration: {e}",
        ) from e


@router.get(
    "/api/circuit-breakers",
    response_model=APIResponse[list[CircuitBreakerResponse]],
    tags=["Retry & Failover"],
    summary="List all circuit breaker states",
)
async def list_circuit_breakers(
    api_key: None = Depends(verify_api_key),
) -> APIResponse[list[CircuitBreakerResponse]]:
    """Get circuit breaker states for all proxies.

    Returns:
        List of circuit breaker states
    """
    from proxywhirl.api.models import CircuitBreakerResponse

    if not _api_core._rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    circuit_breakers = _api_core._rotator.get_circuit_breaker_states()

    responses = []
    for proxy_id, cb in circuit_breakers.items():
        responses.append(
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

    return APIResponse.success(data=responses)


@router.get(
    "/api/metrics/circuit-breakers",
    response_model=APIResponse[list[CircuitBreakerEventResponse]],
    tags=["Retry & Failover"],
    summary="Get circuit breaker metrics",
)
async def get_circuit_breaker_metrics(
    hours: int = 24,
    api_key: None = Depends(verify_api_key),
) -> APIResponse[list[CircuitBreakerEventResponse]]:
    """Get circuit breaker state change events.

    Args:
        hours: Number of hours to retrieve (default: 24)

    Returns:
        List of circuit breaker events
    """
    from proxywhirl.api.models import CircuitBreakerEventResponse

    if not _api_core._rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _api_core._rotator.get_retry_metrics()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    events = [
        CircuitBreakerEventResponse(
            proxy_id=event.proxy_id,
            from_state=event.from_state.value,
            to_state=event.to_state.value,
            timestamp=event.timestamp,
            failure_count=event.failure_count,
        )
        for event in metrics.circuit_breaker_events
        if event.timestamp >= cutoff
    ]

    return APIResponse.success(data=events)


@router.get(
    "/api/circuit-breakers/{proxy_id}",
    response_model=APIResponse[CircuitBreakerResponse],
    tags=["Retry & Failover"],
    summary="Get circuit breaker state for specific proxy",
)
async def get_circuit_breaker(
    proxy_id: str,
    api_key: None = Depends(verify_api_key),
) -> APIResponse[CircuitBreakerResponse]:
    """Get circuit breaker state for a specific proxy.

    Args:
        proxy_id: Proxy ID to get circuit breaker for

    Returns:
        Circuit breaker state
    """
    from proxywhirl.api.models import CircuitBreakerResponse

    if not _api_core._rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    circuit_breakers = _api_core._rotator.get_circuit_breaker_states()

    if proxy_id not in circuit_breakers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Circuit breaker not found for proxy: {proxy_id}",
        )

    cb = circuit_breakers[proxy_id]

    response = CircuitBreakerResponse(
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

    return APIResponse.success(data=response)


@router.post(
    "/api/circuit-breakers/{proxy_id}/reset",
    response_model=APIResponse[CircuitBreakerResponse],
    tags=["Retry & Failover"],
    summary="Manually reset circuit breaker",
)
@limiter.limit("10/minute")
async def reset_circuit_breaker(
    request: Request,
    proxy_id: str,
    api_key: None = Depends(verify_api_key),
) -> APIResponse[CircuitBreakerResponse]:
    """Manually reset a circuit breaker to CLOSED state.

    Args:
        proxy_id: Proxy ID whose circuit breaker to reset

    Returns:
        Updated circuit breaker state
    """
    from proxywhirl.api.models import CircuitBreakerResponse

    if not _api_core._rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    try:
        _api_core._rotator.reset_circuit_breaker(proxy_id)

        # Get updated state
        circuit_breakers = _api_core._rotator.get_circuit_breaker_states()
        cb = circuit_breakers[proxy_id]

        response = CircuitBreakerResponse(
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

        return APIResponse.success(data=response)

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Circuit breaker not found for proxy: {proxy_id}",
        )


@router.get(
    "/api/metrics/retries",
    response_model=APIResponse[RetryMetricsResponse],
    tags=["Retry & Failover"],
    summary="Get retry metrics summary",
)
async def get_retry_metrics(
    api_key: None = Depends(verify_api_key),
) -> APIResponse[RetryMetricsResponse]:
    """Get aggregated retry metrics.

    Returns:
        Retry metrics summary
    """
    from proxywhirl.api.models import RetryMetricsResponse

    if not _api_core._rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _api_core._rotator.get_retry_metrics()
    # Use asyncio.to_thread to avoid blocking event loop with threading.Lock
    summary = await asyncio.to_thread(metrics.get_summary)

    response = RetryMetricsResponse(
        total_retries=summary["total_retries"],
        success_by_attempt={str(k): v for k, v in summary["success_by_attempt"].items()},
        circuit_breaker_events_count=summary["circuit_breaker_events_count"],
        retention_hours=summary["retention_hours"],
    )

    return APIResponse.success(data=response)


@router.get(
    "/api/metrics/retries/timeseries",
    response_model=APIResponse[TimeSeriesResponse],
    tags=["Retry & Failover"],
    summary="Get time-series retry data",
)
async def get_retry_timeseries(
    hours: int = 24,
    api_key: None = Depends(verify_api_key),
) -> APIResponse[TimeSeriesResponse]:
    """Get hourly retry metrics for the specified time range.

    Args:
        hours: Number of hours to retrieve (default: 24)

    Returns:
        Time-series retry data
    """
    from proxywhirl.api.models import TimeSeriesDataPoint, TimeSeriesResponse

    if not _api_core._rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _api_core._rotator.get_retry_metrics()
    # Use asyncio.to_thread to avoid blocking event loop with threading.Lock
    timeseries_data = await asyncio.to_thread(metrics.get_timeseries, hours=hours)

    data_points = [
        TimeSeriesDataPoint(
            timestamp=datetime.fromisoformat(point["timestamp"]),
            total_requests=point["total_requests"],
            total_retries=point["total_retries"],
            success_rate=point["success_rate"],
            avg_latency=point["avg_latency"],
        )
        for point in timeseries_data
    ]

    response = TimeSeriesResponse(data_points=data_points)

    return APIResponse.success(data=response)


@router.get(
    "/api/metrics/retries/by-proxy",
    response_model=APIResponse[ProxyRetryStatsResponse],
    tags=["Retry & Failover"],
    summary="Get per-proxy retry statistics",
)
async def get_retry_stats_by_proxy(
    hours: int = 24,
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ProxyRetryStatsResponse]:
    """Get retry statistics grouped by proxy.

    Args:
        hours: Number of hours to analyze (default: 24)

    Returns:
        Per-proxy retry statistics
    """
    from proxywhirl.api.models import ProxyRetryStats, ProxyRetryStatsResponse

    if not _api_core._rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _api_core._rotator.get_retry_metrics()
    # Use asyncio.to_thread to avoid blocking event loop with threading.Lock
    stats_by_proxy = await asyncio.to_thread(metrics.get_by_proxy, hours=hours)

    proxies = {proxy_id: ProxyRetryStats(**stats) for proxy_id, stats in stats_by_proxy.items()}

    response = ProxyRetryStatsResponse(proxies=proxies)

    return APIResponse.success(data=response.model_dump(mode="json"))
