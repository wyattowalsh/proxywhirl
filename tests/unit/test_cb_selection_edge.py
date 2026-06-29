"""Edge-case tests for circuit-breaker-aware proxy selection."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import httpx
import pytest

from proxywhirl import Proxy, ProxyWhirl
from proxywhirl.circuit_breaker import CircuitBreaker
from proxywhirl.exceptions import ProxyConnectionError
from proxywhirl.models import HealthStatus, ProxyPool
from proxywhirl.orchestration import FailoverPolicy, RequestOrchestration
from proxywhirl.retry import RetryExecutor, RetryPolicy
from proxywhirl.strategies import RoundRobinStrategy


def test_proxy_without_circuit_breaker_is_selectable() -> None:
    """Proxies missing a circuit breaker entry must still be eligible for selection."""
    proxy = Proxy(url="http://no-cb.example.com:8080", health_status=HealthStatus.HEALTHY)
    rotator = ProxyWhirl(proxies=[proxy])

    # Simulate a proxy added without CB initialization
    rotator.circuit_breakers.pop(str(proxy.id), None)

    selected = rotator._select_proxy_with_circuit_breaker()
    assert selected.id == proxy.id


def _build_orchestrator(*, failover_enabled: bool = False) -> tuple[RequestOrchestration, Proxy]:
    proxy = Proxy(url="http://proxy.example.com:8080", allow_local=True)
    pool = ProxyPool(name="test", proxies=[proxy])
    strategy = RoundRobinStrategy()
    circuit_breakers = {str(proxy.id): CircuitBreaker(proxy_id=str(proxy.id))}
    retry_executor = RetryExecutor(RetryPolicy(max_attempts=1), circuit_breakers, MagicMock())

    def select_proxy(_context=None) -> Proxy:
        return strategy.select(pool, _context)

    orchestrator = RequestOrchestration(
        failover_policy=FailoverPolicy(enabled=failover_enabled),
        retry_executor=retry_executor,
        strategy=strategy,
        pool=pool,
        circuit_breakers=circuit_breakers,
        select_proxy=select_proxy,
        get_all_proxies=pool.get_all_proxies,
    )
    return orchestrator, proxy


def test_on_proxy_selected_invoked_for_sync_request() -> None:
    """Selection callback runs once per sync orchestration."""
    orchestrator, proxy = _build_orchestrator()
    selected: list[Proxy] = []

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200

    result = orchestrator.execute_sync(
        method="GET",
        url="https://example.com",
        request_fn_factory=lambda _proxy: lambda: mock_response,
        on_proxy_selected=selected.append,
    )

    assert result.proxy.id == proxy.id
    assert len(selected) == 1
    assert selected[0].id == proxy.id


@pytest.mark.asyncio
async def test_on_proxy_selected_invoked_for_async_request() -> None:
    """Selection callback runs once per async orchestration."""
    orchestrator, proxy = _build_orchestrator()
    selected: list[Proxy] = []

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200

    async def request_fn() -> httpx.Response:
        return mock_response

    result = await orchestrator.execute_async(
        method="GET",
        url="https://example.com",
        request_fn_factory=lambda _proxy: request_fn,
        on_proxy_selected=selected.append,
    )

    assert result.proxy.id == proxy.id
    assert len(selected) == 1
    assert selected[0].id == proxy.id


def test_on_proxy_selected_invoked_for_failover_rounds() -> None:
    """Failover orchestration invokes callback for each selected proxy."""
    orchestrator, _proxy = _build_orchestrator(failover_enabled=True)
    selected: list[Proxy] = []
    call_count = 0

    def request_fn_factory(_proxy: Proxy):
        nonlocal call_count
        call_count += 1

        def request_fn() -> httpx.Response:
            raise httpx.ConnectError("boom")

        return request_fn

    with pytest.raises(ProxyConnectionError):
        orchestrator.execute_sync(
            method="GET",
            url="https://example.com",
            request_fn_factory=request_fn_factory,
            on_proxy_selected=selected.append,
        )

    assert call_count >= 1
    assert len(selected) == call_count


def test_pinned_proxy_skips_reselection() -> None:
    """Pinned proxy bypasses strategy selection for queued or rate-limited retries."""
    proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
    proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
    pool = ProxyPool(name="test", proxies=[proxy1, proxy2])
    strategy = RoundRobinStrategy()
    circuit_breakers = {
        str(proxy1.id): CircuitBreaker(proxy_id=str(proxy1.id)),
        str(proxy2.id): CircuitBreaker(proxy_id=str(proxy2.id)),
    }
    retry_executor = RetryExecutor(RetryPolicy(max_attempts=1), circuit_breakers, MagicMock())
    orchestrator = RequestOrchestration(
        failover_policy=FailoverPolicy(enabled=False),
        retry_executor=retry_executor,
        strategy=strategy,
        pool=pool,
        circuit_breakers=circuit_breakers,
        select_proxy=lambda _context=None: strategy.select(pool, _context),
        get_all_proxies=pool.get_all_proxies,
    )

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200

    result = orchestrator.execute_sync(
        method="GET",
        url="https://example.com",
        request_fn_factory=lambda _proxy: lambda: mock_response,
        pinned_proxy=proxy2,
    )

    assert result.proxy.id == proxy2.id


def test_max_failover_rounds_uses_available_proxies() -> None:
    """Default failover cap counts eligible proxies, not raw pool size."""
    now = datetime.now(timezone.utc)
    proxies = [
        Proxy(url="http://p1.example.com:8080", health_status=HealthStatus.HEALTHY),
        Proxy(
            url="http://p2.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            expires_at=now - timedelta(seconds=1),
        ),
        Proxy(url="http://p3.example.com:8080", health_status=HealthStatus.HEALTHY),
    ]
    pool = ProxyPool(name="test", proxies=proxies)
    strategy = RoundRobinStrategy()
    circuit_breakers = {str(proxy.id): CircuitBreaker(proxy_id=str(proxy.id)) for proxy in proxies}
    retry_executor = RetryExecutor(RetryPolicy(max_attempts=1), circuit_breakers, MagicMock())
    orchestrator = RequestOrchestration(
        failover_policy=FailoverPolicy(enabled=True),
        retry_executor=retry_executor,
        strategy=strategy,
        pool=pool,
        circuit_breakers=circuit_breakers,
        select_proxy=lambda _context=None: strategy.select(pool, _context),
        get_all_proxies=pool.get_all_proxies,
    )

    assert orchestrator._max_failover_rounds() == 2


def test_failover_reports_pool_exhaustion_after_single_failure() -> None:
    """Single-proxy failover should report exhaustion with failed attempt context."""
    orchestrator, _proxy = _build_orchestrator(failover_enabled=True)

    def request_fn_factory(_proxy: Proxy):
        def request_fn() -> httpx.Response:
            raise httpx.ConnectError("boom")

        return request_fn

    with pytest.raises(
        ProxyConnectionError, match="failover round|failed attempt|No additional proxies"
    ):
        orchestrator.execute_sync(
            method="GET",
            url="https://example.com",
            request_fn_factory=request_fn_factory,
        )


def test_selection_excludes_failed_proxy_ids() -> None:
    """Failed proxy IDs in selection context are skipped during selection."""
    from proxywhirl.models import SelectionContext

    proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
    proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
    rotator = ProxyWhirl(proxies=[proxy1, proxy2])

    context = SelectionContext(failed_proxy_ids=[str(proxy1.id)])
    selected = rotator._select_proxy_with_circuit_breaker(context)

    assert selected.id == proxy2.id


def test_selection_uses_pool_proxies_when_get_all_missing() -> None:
    """Pools without get_all_proxies fall back to the proxies attribute."""
    proxy = Proxy(url="http://fallback.example.com:8080", health_status=HealthStatus.HEALTHY)
    rotator = ProxyWhirl(proxies=[proxy])

    class _PoolWithoutSnapshot:
        def __init__(self, proxies: list[Proxy]) -> None:
            self.proxies = proxies

    rotator.pool = _PoolWithoutSnapshot([proxy])  # type: ignore[assignment]

    selected = rotator._select_proxy_with_circuit_breaker()
    assert selected.id == proxy.id


def test_lru_client_pool_evicts_when_full() -> None:
    """LRU client pool evicts the oldest entry when max size is reached."""
    from unittest.mock import Mock

    from proxywhirl.rotator.client_pool import LRUClientPool

    pool = LRUClientPool(maxsize=1)
    old_client = Mock()
    pool.put("proxy-old", old_client)
    pool.put("proxy-new", Mock())

    old_client.close.assert_called_once()
    assert pool.get("proxy-old") is None
    assert pool.get("proxy-new") is not None


def test_lru_client_pool_refreshes_existing_entry() -> None:
    """Re-inserting an existing proxy moves it to the MRU position without eviction."""
    from unittest.mock import Mock

    from proxywhirl.rotator.client_pool import LRUClientPool

    pool = LRUClientPool(maxsize=2)
    first = Mock(name="first")
    second = Mock(name="second")
    pool.put("proxy-a", first)
    pool.put("proxy-b", second)

    refreshed = Mock(name="refreshed")
    pool.put("proxy-a", refreshed)

    # Existing entries are refreshed in-place (MRU bump only)
    assert pool.get("proxy-a") is first
    assert pool.get("proxy-b") is second
    second.close.assert_not_called()


def test_lru_client_pool_logs_close_errors_on_eviction() -> None:
    """Eviction tolerates client close failures without crashing."""
    from unittest.mock import Mock

    from proxywhirl.rotator.client_pool import LRUClientPool

    pool = LRUClientPool(maxsize=1)
    failing_client = Mock()
    failing_client.close.side_effect = RuntimeError("close failed")

    pool.put("proxy-old", failing_client)
    pool.put("proxy-new", Mock())

    failing_client.close.assert_called_once()
    assert pool.get("proxy-old") is None
    assert pool.get("proxy-new") is not None
