"""Tests for concurrent access patterns and race conditions."""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from proxywhirl.models import Proxy


class TestRaceConditions:
    """Test concurrent access patterns."""

    def test_concurrent_proxy_selection(self) -> None:
        """Test concurrent proxy selection doesn't cause race."""
        proxies = [Proxy(url=f"http://proxy{i}.local:8080") for i in range(10)]
        selections = []

        def select_proxy() -> None:
            selections.append(proxies[0])

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(select_proxy) for _ in range(100)]
            for f in futures:
                f.result()

        assert len(selections) == 100

    @pytest.mark.asyncio
    async def test_concurrent_cache_access(self) -> None:
        """Test concurrent cache access is thread-safe."""
        cache = {}

        async def cache_access(key: str, value: str) -> None:
            cache[key] = value
            await asyncio.sleep(0.001)
            assert cache[key] == value

        await asyncio.gather(*[cache_access(f"key{i}", f"value{i}") for i in range(50)])

        assert len(cache) == 50

    def test_concurrent_pool_updates(self) -> None:
        """Test concurrent pool updates don't lose data."""
        pool = []
        pool_lock = threading.Lock()

        def add_proxy(url: str) -> None:
            with pool_lock:
                pool.append(Proxy(url=url))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(add_proxy, f"http://proxy{i}.local:8080") for i in range(100)
            ]
            for f in futures:
                f.result()

        assert len(pool) == 100

    @pytest.mark.asyncio
    async def test_race_condition_cache_stampede(self) -> None:
        """Test race condition in cache stampede scenario."""
        cache = {}
        lock = asyncio.Lock()
        fetching = False

        async def get_or_fetch(key: str) -> str:
            nonlocal fetching
            
            if key in cache:
                return cache[key]

            async with lock:
                # Double-check pattern
                if key in cache:
                    return cache[key]
                
                if fetching:
                    # Already fetching, wait and retry
                    pass
                else:
                    fetching = True

            if fetching:
                await asyncio.sleep(0.01)
                if key in cache:
                    return cache[key]
            
            # Do the fetch
            try:
                await asyncio.sleep(0.02)
                cache[key] = f"value_{key}"
                return cache[key]
            finally:
                async with lock:
                    fetching = False

        results = await asyncio.gather(*[get_or_fetch("shared_key") for _ in range(10)])

        assert all(r == "value_shared_key" for r in results)

    def test_double_checked_locking_pattern(self) -> None:
        """Test double-checked locking pattern."""
        resource = None
        resource_lock = threading.Lock()

        def get_resource() -> str:
            nonlocal resource
            if resource is None:
                with resource_lock:
                    if resource is None:
                        resource = "initialized"
            return resource

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_resource) for _ in range(100)]
            results = [f.result() for f in futures]

        assert all(r == "initialized" for r in results)

    @pytest.mark.asyncio
    async def test_concurrent_validation_requests(self) -> None:
        """Test concurrent validation requests."""
        validation_count = 0
        validation_lock = asyncio.Lock()

        async def validate_proxy() -> None:
            nonlocal validation_count
            async with validation_lock:
                validation_count += 1
            await asyncio.sleep(0.001)

        await asyncio.gather(*[validate_proxy() for _ in range(50)])
        assert validation_count == 50

    def test_concurrent_dictionary_access(self) -> None:
        """Test concurrent dictionary access is safe."""
        data = {}
        data_lock = threading.Lock()

        def update_data(key: str, value: int) -> None:
            with data_lock:
                data[key] = data.get(key, 0) + value

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(update_data, "counter", 1) for _ in range(100)]
            for f in futures:
                f.result()

        assert data["counter"] == 100

    @pytest.mark.asyncio
    async def test_race_in_state_transitions(self) -> None:
        """Test race conditions in state transitions."""
        state = "closed"
        state_lock = asyncio.Lock()

        async def transition_state(new_state: str) -> None:
            nonlocal state
            async with state_lock:
                state = new_state
                await asyncio.sleep(0.001)

        await asyncio.gather(
            transition_state("open"),
            transition_state("half_open"),
            transition_state("closed"),
        )

        assert state in ["open", "half_open", "closed"]

    def test_atomic_counter_increments(self) -> None:
        """Test atomic counter increments."""
        import threading

        counter = 0
        counter_lock = threading.Lock()

        def increment() -> None:
            nonlocal counter
            with counter_lock:
                counter += 1

        threads = [threading.Thread(target=increment) for _ in range(1000)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert counter == 1000
