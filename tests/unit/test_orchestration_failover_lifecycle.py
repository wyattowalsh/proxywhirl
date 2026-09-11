"""Failover proxy lifecycle: record_result and requests_active (Wave 1 P-B-04/05)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx

from proxywhirl.circuit_breaker import CircuitBreaker
from proxywhirl.models import HealthStatus, Proxy, ProxyPool, SelectionContext
from proxywhirl.orchestration import FailoverPolicy, ProxyRotationContext, RequestOrchestration
from proxywhirl.retry import RetryExecutor, RetryPolicy
from proxywhirl.strategies import RoundRobinStrategy


def _build_failover_orchestrator(
    proxies: list[Proxy],
    *,
    intelligent: bool = True,
) -> RequestOrchestration:
    pool = ProxyPool(name="test", proxies=proxies)
    strategy = RoundRobinStrategy()
    circuit_breakers = {str(p.id): CircuitBreaker(proxy_id=str(p.id)) for p in proxies}
    retry_executor = RetryExecutor(RetryPolicy(max_attempts=1), circuit_breakers, MagicMock())
    return RequestOrchestration(
        failover_policy=FailoverPolicy(
            enabled=True,
            max_proxy_attempts=len(proxies),
            use_intelligent_selection=intelligent,
        ),
        retry_executor=retry_executor,
        strategy=strategy,
        pool=pool,
        circuit_breakers=circuit_breakers,
        select_proxy=lambda ctx=None: strategy.select(pool, ctx),
        get_all_proxies=pool.get_all_proxies,
    )


def test_failover_records_failure_for_intermediate_proxy() -> None:
    """Each exhausted proxy gets strategy.record_result (complete_request)."""
    proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
    proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
    orchestrator = _build_failover_orchestrator([proxy1, proxy2])
    strategy = orchestrator.strategy
    recorded: list[tuple[str, bool]] = []
    original = strategy.record_result

    def spy_record_result(proxy: Proxy, success: bool, response_time_ms: float) -> None:
        recorded.append((str(proxy.id), success))
        original(proxy, success=success, response_time_ms=response_time_ms)

    strategy.record_result = spy_record_result  # type: ignore[method-assign]

    call_count = {"n": 0}

    def request_fn_factory(_proxy: Proxy):
        def request_fn() -> httpx.Response:
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise httpx.ConnectError("first proxy down")
            response = MagicMock(spec=httpx.Response)
            response.status_code = 200
            return response

        return request_fn

    result = orchestrator.execute_sync(
        method="GET",
        url="https://example.com",
        request_fn_factory=request_fn_factory,
    )
    assert result.response.status_code == 200
    failed_ids = {pid for pid, ok in recorded if not ok}
    # First selected proxy is recorded as failure; selection order is strategy-dependent.
    assert failed_ids, "expected at least one intermediate failure record"
    assert failed_ids <= {str(proxy1.id), str(proxy2.id)}


def test_failover_requests_active_zero_after_success() -> None:
    """Multi-proxy failover must not leak requests_active on failed intermediates."""
    proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
    proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
    orchestrator = _build_failover_orchestrator([proxy1, proxy2])
    attempts = {"n": 0}

    def request_fn_factory(_proxy: Proxy):
        def request_fn() -> httpx.Response:
            attempts["n"] += 1
            if attempts["n"] == 1:
                raise httpx.ConnectError("fail once")
            response = MagicMock(spec=httpx.Response)
            response.status_code = 200
            return response

        return request_fn

    result = orchestrator.execute_sync(
        method="GET",
        url="https://example.com",
        request_fn_factory=request_fn_factory,
    )
    assert proxy1.requests_active == 0
    assert proxy2.requests_active == 0


def test_intelligent_failover_starts_request_on_selected_proxy() -> None:
    """select_retry_proxy path must call start_request like strategy.select (P-B-05)."""
    proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
    proxy1.total_requests = 10
    proxy1.total_successes = 10
    proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
    proxy2.total_requests = 10
    proxy2.total_successes = 1
    orchestrator = _build_failover_orchestrator([proxy1, proxy2], intelligent=True)
    rotation_ctx = ProxyRotationContext(
        request_id="r1",
        method="GET",
        url="https://example.com",
        failed_proxy_ids=[str(proxy1.id)],
        selection_context=SelectionContext(),
    )
    proxy2.requests_active = 0
    selected = orchestrator._rotate_proxy(rotation_ctx, proxy1)
    assert selected is not None
    assert selected.id == proxy2.id
    assert proxy2.requests_active == 1


def test_get_available_proxies_uses_is_eligible_not_acquire() -> None:
    """Filtering proxies must not consume half-open probes (P-B-03)."""
    proxy = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
    orchestrator = _build_failover_orchestrator([proxy], intelligent=False)
    cb = orchestrator.circuit_breakers[str(proxy.id)]
    with patch("time.time", return_value=100.0):
        for _ in range(cb.failure_threshold):
            cb.record_failure()
    with patch("time.time", return_value=100.0 + cb.timeout_duration + 1):
        available = orchestrator._get_available_proxies([])
        assert len(available) == 1
        assert cb.state.value == "open"
