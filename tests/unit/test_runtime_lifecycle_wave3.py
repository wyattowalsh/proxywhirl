"""Regression tests for request lifecycle and rotator resource ownership."""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from proxywhirl.exceptions import ProxyConnectionError, RateLimitExceededError
from proxywhirl.models import HealthStatus, Proxy, ProxyPool, SelectionContext
from proxywhirl.orchestration import FailoverPolicy
from proxywhirl.rate_limiting import SyncRateLimiter
from proxywhirl.retry import RetryPolicy
from proxywhirl.rotator.async_ import AsyncProxyWhirl
from proxywhirl.rotator.sync import ProxyWhirl
from proxywhirl.strategies.composite import CompositeStrategy


def _healthy_proxy(host: str = "proxy.example.com") -> Proxy:
    return Proxy(url=f"http://{host}:8080", health_status=HealthStatus.HEALTHY)


def _response() -> httpx.Response:
    request = httpx.Request("GET", "https://example.com")
    return httpx.Response(200, request=request)


def test_failure_accounting_is_not_gated_by_historical_failures() -> None:
    proxy = _healthy_proxy()
    proxy.total_requests = 7
    proxy.total_failures = 7
    rotator = ProxyWhirl(
        proxies=[proxy],
        retry_policy=RetryPolicy(max_attempts=1),
        bootstrap=False,
    )
    client = MagicMock(spec=httpx.Client)
    client.request.side_effect = httpx.ConnectError(
        "proxy down",
        request=httpx.Request("GET", "https://example.com"),
    )
    rotator._get_or_create_client = MagicMock(return_value=client)  # type: ignore[method-assign]

    with pytest.raises(ProxyConnectionError):
        rotator.get("https://example.com")

    assert proxy.requests_started == 1
    assert proxy.requests_completed == 1
    assert proxy.requests_active == 0
    assert proxy.total_failures == 8
    rotator.close()


def test_rate_limit_rejection_settles_selected_proxy() -> None:
    proxy = _healthy_proxy()
    limiter = MagicMock(spec=SyncRateLimiter)
    limiter.check_limit.return_value = False
    rotator = ProxyWhirl(proxies=[proxy], rate_limiter=limiter, bootstrap=False)

    with pytest.raises(RateLimitExceededError):
        rotator.get("https://example.com")

    assert proxy.requests_started == 1
    assert proxy.requests_completed == 1
    assert proxy.requests_active == 0
    assert proxy.total_failures == 1
    rotator.close()


def test_failover_settles_each_selected_proxy_once() -> None:
    proxies = [_healthy_proxy("proxy1.example.com"), _healthy_proxy("proxy2.example.com")]
    rotator = ProxyWhirl(
        proxies=proxies,
        retry_policy=RetryPolicy(max_attempts=1),
        failover_policy=FailoverPolicy(
            enabled=True,
            max_proxy_attempts=2,
            use_intelligent_selection=False,
        ),
        bootstrap=False,
    )
    failed_client = MagicMock(spec=httpx.Client)
    failed_client.request.side_effect = httpx.ConnectError(
        "first proxy down",
        request=httpx.Request("GET", "https://example.com"),
    )
    successful_client = MagicMock(spec=httpx.Client)
    successful_client.request.return_value = _response()
    clients = iter((failed_client, successful_client))
    rotator._get_or_create_client = MagicMock(  # type: ignore[method-assign]
        side_effect=lambda _proxy, _proxy_dict: next(clients)
    )

    response = rotator.get("https://example.com")

    assert response.status_code == 200
    assert sorted(proxy.requests_started for proxy in proxies) == [1, 1]
    assert sorted(proxy.requests_completed for proxy in proxies) == [1, 1]
    assert sorted(proxy.requests_active for proxy in proxies) == [0, 0]
    assert sum(proxy.total_failures for proxy in proxies) == 1
    assert sum(proxy.total_successes for proxy in proxies) == 1
    rotator.close()


@pytest.mark.asyncio
async def test_async_cancellation_settles_selected_proxy() -> None:
    proxy = _healthy_proxy()
    rotator = AsyncProxyWhirl(
        proxies=[proxy],
        retry_policy=RetryPolicy(max_attempts=1),
        bootstrap=False,
    )
    request_started = asyncio.Event()

    async def blocked_request(*_args: object, **_kwargs: object) -> httpx.Response:
        request_started.set()
        await asyncio.Event().wait()
        raise AssertionError("unreachable")

    client = MagicMock(spec=httpx.AsyncClient)
    client.request = AsyncMock(side_effect=blocked_request)
    client.aclose = AsyncMock()
    rotator._get_or_create_client = AsyncMock(return_value=client)  # type: ignore[method-assign]

    request_task = asyncio.create_task(rotator.get("https://example.com"))
    await request_started.wait()
    request_task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await request_task

    assert proxy.requests_started == 1
    assert proxy.requests_completed == 1
    assert proxy.requests_active == 0
    assert proxy.total_failures == 1
    await rotator.aclose()


@pytest.mark.asyncio
async def test_async_cancellation_during_offloaded_selection_settles_proxy() -> None:
    proxy = _healthy_proxy()
    rotator = AsyncProxyWhirl(proxies=[proxy], bootstrap=False)
    entered = threading.Event()
    release = threading.Event()
    select_proxy = rotator.orchestrator.select_proxy

    def blocked_selection(context: SelectionContext | None = None) -> Proxy:
        entered.set()
        assert release.wait(timeout=5)
        return select_proxy(context)

    rotator.orchestrator.select_proxy = blocked_selection
    request_task = asyncio.create_task(rotator.get("https://example.com"))
    assert await asyncio.to_thread(entered.wait, 5)
    request_task.cancel()
    release.set()
    with pytest.raises(asyncio.CancelledError):
        await request_task

    assert proxy.requests_started == 1
    assert proxy.requests_completed == 1
    assert proxy.requests_active == 0
    assert proxy.total_failures == 1
    await rotator.aclose()


class _BlockingFilter:
    def __init__(self, entered: threading.Event, release: threading.Event) -> None:
        self.entered = entered
        self.release = release

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        del context
        candidate = pool.get_all_proxies()[0]
        self.entered.set()
        assert self.release.wait(timeout=5)
        candidate.start_request()
        return candidate

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        del proxy, success, response_time_ms


class _NonMutatingSelector:
    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        del context
        return pool.get_all_proxies()[0]

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        del proxy, success, response_time_ms


def test_composite_filter_probe_does_not_restore_over_live_counter_updates() -> None:
    proxy = _healthy_proxy()
    pool = ProxyPool(name="live", proxies=[proxy])
    entered = threading.Event()
    release = threading.Event()
    composite = CompositeStrategy(
        filters=[_BlockingFilter(entered, release)],  # type: ignore[list-item]
        selector=_NonMutatingSelector(),  # type: ignore[arg-type]
    )

    with ThreadPoolExecutor(max_workers=1) as executor:
        selection = executor.submit(composite.select, pool, SelectionContext())
        assert entered.wait(timeout=5)
        proxy.start_request()
        release.set()
        assert selection.result(timeout=5).id == proxy.id

    assert proxy.requests_started == 1
    assert proxy.requests_active == 1


def test_sync_same_key_client_race_returns_one_canonical_client() -> None:
    proxy = _healthy_proxy()
    rotator = ProxyWhirl(proxies=[proxy], bootstrap=False)
    barrier = threading.Barrier(2)
    constructed = [MagicMock(spec=httpx.Client), MagicMock(spec=httpx.Client)]
    pending = list(constructed)
    created_lock = threading.Lock()

    def make_client(**_kwargs: object) -> httpx.Client:
        with created_lock:
            client = pending.pop()
        barrier.wait(timeout=5)
        return client

    with patch("proxywhirl.rotator.sync.httpx.Client", side_effect=make_client):
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(
                    rotator._get_or_create_client, proxy, rotator._get_proxy_dict(proxy)
                )
                for _ in range(2)
            ]
            clients = [future.result(timeout=5) for future in futures]

    assert clients[0] is clients[1]
    # Exactly one of the two constructed clients is canonical; the other is closed.
    canonical = clients[0]
    duplicate = next(client for client in constructed if client is not canonical)
    duplicate.close.assert_called_once_with()
    rotator.close()


@pytest.mark.asyncio
async def test_async_same_key_client_race_returns_one_canonical_client() -> None:
    proxy = _healthy_proxy()
    rotator = AsyncProxyWhirl(proxies=[proxy], bootstrap=False)
    original_get = rotator._client_pool.get
    both_read = asyncio.Event()
    read_count = 0

    async def synchronized_get(proxy_id: str) -> httpx.AsyncClient | None:
        nonlocal read_count
        result = await original_get(proxy_id)
        read_count += 1
        if read_count == 2:
            both_read.set()
        await both_read.wait()
        return result

    rotator._client_pool.get = synchronized_get  # type: ignore[method-assign]
    constructed = [MagicMock(spec=httpx.AsyncClient), MagicMock(spec=httpx.AsyncClient)]
    for client in constructed:
        client.aclose = AsyncMock()

    with patch("proxywhirl.rotator.async_.httpx.AsyncClient", side_effect=constructed):
        clients = await asyncio.gather(
            rotator._get_or_create_client(proxy, rotator._get_proxy_dict(proxy)),
            rotator._get_or_create_client(proxy, rotator._get_proxy_dict(proxy)),
        )

    assert clients[0] is clients[1]
    duplicate = next(client for client in constructed if client is not clients[0])
    duplicate.aclose.assert_awaited_once()
    await rotator.aclose()


def test_sync_constructor_is_passive_and_close_is_idempotent() -> None:
    with patch.object(ProxyWhirl, "_start_aggregation_timer") as start_timer:
        rotator = ProxyWhirl(bootstrap=False)
        start_timer.assert_not_called()
        rotator.__enter__()
        start_timer.assert_called_once_with()

    client = rotator._client
    assert client is not None
    rotator.close()
    rotator.close()
    assert rotator._client is None
    assert client.is_closed

    partial = ProxyWhirl.__new__(ProxyWhirl)
    partial.close()


@pytest.mark.asyncio
async def test_async_aclose_finishes_pool_cleanup_when_cancelled() -> None:
    rotator = AsyncProxyWhirl(bootstrap=False)
    close_started = asyncio.Event()

    async def block_close() -> None:
        close_started.set()
        await asyncio.Event().wait()

    main_client = MagicMock(spec=httpx.AsyncClient)
    main_client.aclose = AsyncMock(side_effect=block_close)
    pooled_client = MagicMock(spec=httpx.AsyncClient)
    pooled_client.aclose = AsyncMock()
    rotator._client = main_client
    await rotator._client_pool.put("pooled", pooled_client)

    close_task = asyncio.create_task(rotator.aclose())
    await close_started.wait()
    close_task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await close_task

    pooled_client.aclose.assert_awaited_once()
    assert rotator._client is None
    assert len(rotator._client_pool) == 0
    assert rotator._stop_event.is_set()
    await rotator.aclose()

    partial = AsyncProxyWhirl.__new__(AsyncProxyWhirl)
    await partial.aclose()
