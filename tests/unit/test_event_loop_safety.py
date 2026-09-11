"""Event-loop safety contracts for thread-locked pool and async rate limiter.

Wave 2 Team H: ProxyPool async helpers, AsyncRateLimiter loop-bound locks,
and regression coverage that async paths do not hold thread locks on the
event-loop thread.
"""

from __future__ import annotations

import asyncio
import threading
import warnings
from collections.abc import Iterator
from unittest.mock import patch

import pytest

from proxywhirl.models import Proxy, ProxyPool
from proxywhirl.rate_limiting import AsyncRateLimiter, RateLimit


@pytest.fixture(autouse=True)
def _reset_pool_loop_warning_flag() -> Iterator[None]:
    """Allow per-test observation of the once-per-process pool warning."""
    import proxywhirl.models.core as models_core

    models_core._PROXY_POOL_EVENT_LOOP_LOCK_WARNED = False
    yield
    models_core._PROXY_POOL_EVENT_LOOP_LOCK_WARNED = False


class TestProxyPoolAsyncHelpers:
    """ProxyPool a* helpers offload RLock work via asyncio.to_thread."""

    async def test_aget_all_proxies_returns_snapshot(self) -> None:
        pool = ProxyPool(name="async-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")
        await pool.aadd_proxy(proxy)

        snapshot = await pool.aget_all_proxies()
        assert len(snapshot) == 1
        assert snapshot[0].url == proxy.url
        assert await pool.asize() == 1

    async def test_async_helper_does_not_hold_lock_on_event_loop_thread(self) -> None:
        """While aget_all_proxies runs, work executes off the event-loop thread."""
        pool = ProxyPool(name="async-pool")
        await pool.aadd_proxy(Proxy(url="http://proxy.example.com:8080"))

        held_on_loop_thread: list[bool] = []
        loop_thread_id = threading.get_ident()
        real_get_all = ProxyPool.get_all_proxies

        def instrumented_get_all(self: ProxyPool) -> list[Proxy]:
            held_on_loop_thread.append(threading.get_ident() == loop_thread_id)
            return real_get_all(self)

        with patch.object(ProxyPool, "get_all_proxies", instrumented_get_all):
            result = await pool.aget_all_proxies()

        assert len(result) == 1
        assert held_on_loop_thread == [False]

    async def test_sync_pool_method_warns_under_running_loop(self) -> None:
        pool = ProxyPool(name="warn-pool")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _ = pool.size
        messages = [str(w.message) for w in caught if issubclass(w.category, RuntimeWarning)]
        assert any("threading.RLock" in msg for msg in messages)


class TestAsyncRateLimiterLoopBinding:
    """AsyncRateLimiter must rebind asyncio.Lock when the event loop changes."""

    async def test_lock_bound_to_running_loop(self) -> None:
        limiter = AsyncRateLimiter()
        lock = limiter._get_lock()
        assert limiter._loop is asyncio.get_running_loop()
        assert await limiter.check_limit("proxy-1") is True
        assert limiter._get_lock() is lock

    def test_lock_recreated_for_new_event_loop(self) -> None:
        limiter = AsyncRateLimiter(global_limit=RateLimit(max_requests=10, time_window=60))

        async def use_limiter() -> asyncio.Lock:
            return limiter._get_lock()

        loop1 = asyncio.new_event_loop()
        try:
            lock1 = loop1.run_until_complete(use_limiter())
        finally:
            loop1.close()

        loop2 = asyncio.new_event_loop()
        try:
            lock2 = loop2.run_until_complete(use_limiter())
        finally:
            loop2.close()

        assert lock1 is not lock2
        assert limiter._loop is None or limiter._loop is loop2


class TestSelectOffloadContract:
    """Rotator base async selection uses to_thread (no thread lock on loop)."""

    async def test_aselect_runs_select_off_loop_thread(self) -> None:
        from proxywhirl.models import HealthStatus
        from proxywhirl.retry import RetryPolicy
        from proxywhirl.rotator.base import ProxyRotatorBase
        from proxywhirl.strategies import RoundRobinStrategy

        pool = ProxyPool(
            name="select-pool",
            proxies=[
                Proxy(
                    url="http://proxy1.example.com:8080",
                    health_status=HealthStatus.HEALTHY,
                )
            ],
        )
        rotator = ProxyRotatorBase()
        rotator._init_common(pool, RoundRobinStrategy(), config=None, retry_policy=RetryPolicy())
        rotator._init_circuit_breakers_for_proxies(await pool.aget_all_proxies())

        loop_thread_id = threading.get_ident()
        ran_on_loop: list[bool] = []
        real_select = rotator._select_proxy_with_circuit_breaker

        def instrumented_select(context=None):
            ran_on_loop.append(threading.get_ident() == loop_thread_id)
            return real_select(context)

        with patch.object(
            rotator,
            "_select_proxy_with_circuit_breaker",
            side_effect=instrumented_select,
        ):
            proxy = await rotator._aselect_proxy_with_circuit_breaker()

        assert proxy.url == "http://proxy1.example.com:8080"
        assert ran_on_loop == [False]
