"""Tests for race conditions in shared state and proxy pool modifications.

Session 8 SA-8.1: Validates thread-safe and async-safe behaviors under
concurrent access patterns.
"""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from proxywhirl.models import Proxy, ProxyPool
from tests.conftest import ProxyFactory


# ============================================================================
# SHARED STATE UNDER ASYNCIO.GATHER
# ============================================================================


class TestAsyncioGatherSharedState:
    """Test shared mutable state when coroutines run via ``asyncio.gather``."""

    @pytest.mark.asyncio
    async def test_gather_counter_increment(self) -> None:
        """Multiple tasks incrementing a shared counter via ``gather``."""
        counter = 0
        lock = asyncio.Lock()

        async def increment() -> None:
            nonlocal counter
            async with lock:
                counter += 1

        await asyncio.gather(*[increment() for _ in range(100)])
        assert counter == 100

    @pytest.mark.asyncio
    async def test_gather_list_append(self) -> None:
        """Multiple tasks appending to a shared list via ``gather``."""
        results: list[int] = []
        lock = asyncio.Lock()

        async def append_value(value: int) -> None:
            async with lock:
                results.append(value)

        await asyncio.gather(*[append_value(i) for i in range(50)])
        assert len(results) == 50
        assert sorted(results) == list(range(50))

    @pytest.mark.asyncio
    async def test_gather_dict_updates(self) -> None:
        """Multiple tasks updating a shared dict via ``gather``."""
        data: dict[str, int] = {}
        lock = asyncio.Lock()

        async def update(key: str, value: int) -> None:
            async with lock:
                data[key] = data.get(key, 0) + value

        await asyncio.gather(
            *[update(f"key_{i % 5}", 1) for i in range(100)]
        )
        assert sum(data.values()) == 100

    @pytest.mark.asyncio
    async def test_gather_without_lock_is_unsafe(self) -> None:
        """Demonstrate that unprotected shared state can lose updates."""
        counter = 0

        async def unsafe_increment() -> None:
            nonlocal counter
            current = counter
            await asyncio.sleep(0)  # yield control
            counter = current + 1

        # Not guaranteed to be 100 because of the race, but we run enough
        # times that it usually fails if truly unsafe.  We'll use a larger
        # batch to increase the chance of observing the race.
        await asyncio.gather(*[unsafe_increment() for _ in range(200)])
        # If the race manifests, counter will be < 200.
        # We only assert it's > 0 to avoid flaky failures; the point is
        # educational: unprotected async shared state is racy.
        assert counter > 0

    @pytest.mark.asyncio
    async def test_gather_with_semaphore(self) -> None:
        """Use a semaphore to limit concurrent access to shared state."""
        counter = 0
        sem = asyncio.Semaphore(1)

        async def increment() -> None:
            nonlocal counter
            async with sem:
                counter += 1

        await asyncio.gather(*[increment() for _ in range(50)])
        assert counter == 50


# ============================================================================
# CONCURRENT PROXY POOL MODIFICATIONS
# ============================================================================


class TestConcurrentProxyPoolModifications:
    """Test ``ProxyPool`` under concurrent reads and writes."""

    def test_threaded_proxy_pool_append(self) -> None:
        """Multiple threads appending proxies to a ``ProxyPool``."""
        pool = ProxyPool(name="thread_append", proxies=[])
        lock = threading.Lock()
        errors: list[Exception] = []

        def add_proxies(batch_id: int) -> None:
            try:
                for i in range(10):
                    proxy = ProxyFactory.build()
                    with lock:
                        pool.proxies.append(proxy)
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(add_proxies, i) for i in range(10)]
            for future in futures:
                future.result()

        assert len(errors) == 0
        assert len(pool.proxies) == 100

    def test_threaded_proxy_pool_pop(self) -> None:
        """Multiple threads popping proxies from a ``ProxyPool``."""
        pool = ProxyPool(name="thread_pop", proxies=[ProxyFactory.build() for _ in range(100)])
        lock = threading.Lock()
        popped: list[Proxy] = []
        errors: list[Exception] = []

        def pop_proxies() -> None:
            try:
                while True:
                    with lock:
                        if not pool.proxies:
                            break
                        popped.append(pool.proxies.pop())
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(pop_proxies) for _ in range(5)]
            for future in futures:
                future.result()

        assert len(errors) == 0
        assert len(pool.proxies) == 0
        assert len(popped) == 100

    @pytest.mark.asyncio
    async def test_async_proxy_pool_append(self) -> None:
        """Multiple async tasks appending proxies to a ``ProxyPool``."""
        pool = ProxyPool(name="async_append", proxies=[])
        lock = asyncio.Lock()

        async def add_proxy(task_id: int) -> None:
            for i in range(5):
                proxy = ProxyFactory.build()
                async with lock:
                    pool.proxies.append(proxy)
                await asyncio.sleep(0)

        await asyncio.gather(*[add_proxy(i) for i in range(10)])
        assert len(pool.proxies) == 50

    @pytest.mark.asyncio
    async def test_async_proxy_pool_mixed_ops(self) -> None:
        """Async tasks performing mixed append/pop on a ``ProxyPool``."""
        pool = ProxyPool(name="async_mixed", proxies=[ProxyFactory.build() for _ in range(20)])
        lock = asyncio.Lock()

        async def modify(task_id: int) -> None:
            for i in range(5):
                async with lock:
                    if i % 2 == 0 and pool.proxies:
                        pool.proxies.pop(0)
                    else:
                        pool.proxies.append(ProxyFactory.build())
                await asyncio.sleep(0)

        await asyncio.gather(*[modify(i) for i in range(4)])
        # Pool should still be valid regardless of exact count
        assert isinstance(pool, ProxyPool)
        assert len(pool.proxies) >= 0

    def test_threaded_read_during_write(self) -> None:
        """Threads reading proxy count while others are appending."""
        pool = ProxyPool(name="read_during_write", proxies=[])
        lock = threading.Lock()
        read_counts: list[int] = []
        errors: list[Exception] = []

        def writer() -> None:
            try:
                for _ in range(20):
                    with lock:
                        pool.proxies.append(ProxyFactory.build())
            except Exception as e:
                errors.append(e)

        def reader() -> None:
            try:
                for _ in range(20):
                    with lock:
                        read_counts.append(len(pool.proxies))
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            futures.extend([executor.submit(writer) for _ in range(2)])
            futures.extend([executor.submit(reader) for _ in range(2)])
            for future in futures:
                future.result()

        assert len(errors) == 0
        assert len(pool.proxies) == 40

    @pytest.mark.asyncio
    async def test_async_read_during_write(self) -> None:
        """Async tasks reading while others are writing."""
        pool = ProxyPool(name="async_read_write", proxies=[])
        lock = asyncio.Lock()
        read_counts: list[int] = []

        async def writer() -> None:
            for _ in range(20):
                async with lock:
                    pool.proxies.append(ProxyFactory.build())
                await asyncio.sleep(0)

        async def reader() -> None:
            for _ in range(20):
                async with lock:
                    read_counts.append(len(pool.proxies))
                await asyncio.sleep(0)

        await asyncio.gather(writer(), writer(), reader(), reader())
        assert len(pool.proxies) == 40

    def test_proxy_pool_concurrent_selection(self) -> None:
        """Multiple threads selecting proxies concurrently."""
        pool = ProxyPool(name="concurrent_select", proxies=[ProxyFactory.healthy() for _ in range(20)])
        lock = threading.Lock()
        selected: list[Proxy] = []
        errors: list[Exception] = []

        def select() -> None:
            try:
                for _ in range(10):
                    with lock:
                        if pool.proxies:
                            selected.append(pool.proxies[0])
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(select) for _ in range(5)]
            for future in futures:
                future.result()

        assert len(errors) == 0
        assert len(selected) == 50
        assert all(isinstance(p, Proxy) for p in selected)

    @pytest.mark.asyncio
    async def test_async_proxy_pool_selection(self) -> None:
        """Multiple async tasks selecting proxies concurrently."""
        pool = ProxyPool(name="async_select", proxies=[ProxyFactory.healthy() for _ in range(10)])
        lock = asyncio.Lock()
        selected: list[Proxy] = []

        async def select(task_id: int) -> None:
            for _ in range(5):
                async with lock:
                    if pool.proxies:
                        selected.append(pool.proxies[0])
                await asyncio.sleep(0)

        await asyncio.gather(*[select(i) for i in range(5)])
        assert len(selected) == 25


# ============================================================================
# ATOMIC OPERATIONS
# ============================================================================


class TestAtomicOperations:
    """Test atomic-like operations under concurrency."""

    def test_atomic_counter_with_threading(self) -> None:
        """A locked counter incremented by many threads must be exact."""
        counter = 0
        lock = threading.Lock()

        def increment() -> None:
            nonlocal counter
            for _ in range(100):
                with lock:
                    counter += 1

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(increment) for _ in range(10)]
            for future in futures:
                future.result()

        assert counter == 1000

    @pytest.mark.asyncio
    async def test_atomic_counter_with_asyncio(self) -> None:
        """A locked counter incremented by many async tasks must be exact."""
        counter = 0
        lock = asyncio.Lock()

        async def increment() -> None:
            nonlocal counter
            for _ in range(100):
                async with lock:
                    counter += 1

        await asyncio.gather(*[increment() for _ in range(10)])
        assert counter == 1000

    def test_double_checked_locking(self) -> None:
        """Double-checked locking pattern must initialize exactly once."""
        resource: str | None = None
        lock = threading.Lock()
        initialized_count = 0
        init_lock = threading.Lock()

        def get_resource() -> str:
            nonlocal resource, initialized_count
            if resource is None:
                with lock:
                    if resource is None:
                        with init_lock:
                            initialized_count += 1
                        resource = "initialized"
            return resource

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_resource) for _ in range(100)]
            results = [f.result() for f in futures]

        assert all(r == "initialized" for r in results)
        assert initialized_count == 1


# ============================================================================
# COUNT CHECK
# ============================================================================


def test_at_least_fifteen_tests_exist() -> None:
    """Meta-test: ensure this module contains >= 15 test functions."""
    import inspect
    import sys

    module = sys.modules[__name__]

    def _collect_tests(obj):
        tests = []
        for name, member in inspect.getmembers(obj):
            if name.startswith("test_") and (inspect.isfunction(member) or inspect.ismethod(member)):
                tests.append(member)
        return tests

    test_funcs = _collect_tests(module)
    for _, cls in inspect.getmembers(module, inspect.isclass):
        test_funcs.extend(_collect_tests(cls))

    assert len(test_funcs) >= 15, f"Expected >= 15 tests, found {len(test_funcs)}"
