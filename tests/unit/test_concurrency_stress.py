"""Concurrency stress tests for ProxyWhirl with 500+ concurrent requests.

Tests race conditions, deadlocks, and resource exhaustion.
Marked with @pytest.mark.stress to skip in CI by default.
"""

import pytest

pytestmark = pytest.mark.slow

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from proxywhirl import AsyncProxyWhirl, ProxyWhirl
from proxywhirl.models import HealthStatus, Proxy, ProxyPool


@pytest.mark.stress
class TestConcurrencyStress:
    """Stress tests for concurrent proxy selection."""

    @pytest.fixture
    def large_pool(self) -> ProxyPool:
        """Create a pool with 50 proxies."""
        pool = ProxyPool(name="stress-pool")
        for i in range(50):
            proxy = Proxy(
                url=f"http://proxy{i:03d}.example.com:{8080 + (i % 100)}",
                health_status=HealthStatus.HEALTHY,
            )
            pool.add_proxy(proxy)
        return pool

    def test_sync_500_concurrent_selections(self, large_pool: ProxyPool) -> None:
        """Test 500 concurrent proxy selections with ThreadPoolExecutor."""
        rotator = ProxyWhirl(pool=large_pool, strategy="round_robin")

        def select_proxy() -> bool:
            """Select a proxy and return success."""
            try:
                proxy = rotator.select()
                return proxy is not None or len(large_pool.get_all_proxies()) == 0
            except Exception:
                return False

        # Run 500 concurrent selections
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(select_proxy) for _ in range(500)]
            results = [f.result() for f in as_completed(futures)]

        # All should succeed
        assert all(results), f"Some selections failed: {sum(results)}/500 succeeded"

    def test_sync_1000_concurrent_selections(self, large_pool: ProxyPool) -> None:
        """Test 1000 concurrent proxy selections."""
        rotator = ProxyWhirl(pool=large_pool, strategy="random")

        def select_proxy() -> bool:
            try:
                proxy = rotator.select()
                return proxy is not None or len(large_pool.get_all_proxies()) == 0
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(select_proxy) for _ in range(1000)]
            results = [f.result() for f in as_completed(futures)]

        assert all(results), f"Some selections failed: {sum(results)}/1000 succeeded"

    def test_sync_concurrent_add_remove_select(self, large_pool: ProxyPool) -> None:
        """Test concurrent add/remove/select operations (detect race conditions)."""
        rotator = ProxyWhirl(pool=large_pool, strategy="weighted")

        def add_proxy() -> bool:
            try:
                proxy = Proxy(url=f"http://temp.example.com:{9000}")
                rotator.pool.add_proxy(proxy)
                return True
            except Exception:
                return False

        def remove_proxy() -> bool:
            try:
                proxies = rotator.pool.get_all_proxies()
                if proxies:
                    rotator.pool.remove_proxy(proxies[0].id)
                return True
            except Exception:
                return False

        def select_proxy() -> bool:
            try:
                rotator.select()
                return True
            except Exception:
                return False

        # Mix operations
        operations = [add_proxy] * 50 + [remove_proxy] * 50 + [select_proxy] * 200

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(op) for op in operations]
            results = [f.result() for f in as_completed(futures)]

        assert all(results), "Some concurrent operations failed"

    def test_sync_stress_multiple_rotators(self) -> None:
        """Test multiple rotators operating concurrently."""
        pools = [ProxyPool(name=f"pool-{i}") for i in range(5)]

        for pool in pools:
            for j in range(20):
                proxy = Proxy(
                    url=f"http://proxy{j}.example.com:{8080 + j}",
                    health_status=HealthStatus.HEALTHY,
                )
                pool.add_proxy(proxy)

        rotators = [ProxyWhirl(pool=pool, strategy="round_robin") for pool in pools]

        def select_from_rotator(rotator: ProxyWhirl) -> bool:
            try:
                rotator.select()
                return True
            except Exception:
                return False

        # Each rotator selects 100 times concurrently
        operations = [(rotator, select_from_rotator) for rotator in rotators for _ in range(100)]

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(op[1], op[0]) for op in operations]
            results = [f.result() for f in as_completed(futures)]

        assert all(results), f"Some operations failed: {sum(results)}/{len(results)} succeeded"

    @pytest.mark.asyncio
    async def test_async_500_concurrent_selections(self, large_pool: ProxyPool) -> None:
        """Test 500 concurrent async selections."""
        rotator = AsyncProxyWhirl(pool=large_pool, strategy="random")

        async def select_proxy() -> bool:
            try:
                proxy = await rotator.select()
                return proxy is not None or len(large_pool.get_all_proxies()) == 0
            except Exception:
                return False

        # Create 500 concurrent tasks
        tasks = [select_proxy() for _ in range(500)]
        results = await asyncio.gather(*tasks)

        assert all(results), f"Some selections failed: {sum(results)}/500 succeeded"

    @pytest.mark.asyncio
    async def test_async_1000_concurrent_selections(self, large_pool: ProxyPool) -> None:
        """Test 1000 concurrent async selections."""
        rotator = AsyncProxyWhirl(pool=large_pool, strategy="least_used")

        async def select_proxy() -> bool:
            try:
                proxy = await rotator.select()
                return proxy is not None or len(large_pool.get_all_proxies()) == 0
            except Exception:
                return False

        tasks = [select_proxy() for _ in range(1000)]
        results = await asyncio.gather(*tasks)

        assert all(results), f"Some selections failed: {sum(results)}/1000 succeeded"

    @pytest.mark.asyncio
    async def test_async_concurrent_operations(self, large_pool: ProxyPool) -> None:
        """Test concurrent async add/select operations."""
        rotator = AsyncProxyWhirl(pool=large_pool, strategy="performance_based")

        async def select_proxy() -> bool:
            try:
                await rotator.select()
                return True
            except Exception:
                return False

        async def mark_request() -> bool:
            try:
                proxy = await rotator.select()
                if proxy:
                    proxy.start_request()
                    proxy.complete_request(success=True, response_time_ms=100.0)
                return True
            except Exception:
                return False

        tasks = [select_proxy() for _ in range(400)] + [mark_request() for _ in range(100)]
        results = await asyncio.gather(*tasks)

        assert all(results), "Some async operations failed"


@pytest.mark.stress
class TestConcurrencyEdgeCases:
    """Edge case tests for concurrent access patterns."""

    def test_concurrent_pool_mutation(self) -> None:
        """Test rapid pool mutations don't cause crashes."""
        pool = ProxyPool(name="mutation-pool")
        rotator = ProxyWhirl(pool=pool, strategy="round_robin")

        def mutate_pool() -> bool:
            try:
                # Add
                for i in range(10):
                    pool.add_proxy(Proxy(url=f"http://temp{i}.example.com:8080"))

                # Remove all
                for proxy in pool.get_all_proxies():
                    pool.remove_proxy(proxy.id)

                return True
            except Exception:
                return False

        def use_pool() -> bool:
            try:
                rotator.select()
                return True
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(mutate_pool) for _ in range(20)] + [
                executor.submit(use_pool) for _ in range(100)
            ]
            results = [f.result() for f in as_completed(futures)]

        assert all(results), "Pool mutation test failed"

    def test_concurrent_health_status_updates(self) -> None:
        """Test concurrent health status updates don't race."""
        pool = ProxyPool(name="health-pool")
        proxies = [
            Proxy(url=f"http://proxy{i}.example.com:8080", health_status=HealthStatus.HEALTHY)
            for i in range(20)
        ]

        for proxy in proxies:
            pool.add_proxy(proxy)

        def update_health() -> bool:
            try:
                for proxy in pool.get_all_proxies():
                    proxy.health_status = HealthStatus.UNHEALTHY
                    proxy.health_status = HealthStatus.HEALTHY
                return True
            except Exception:
                return False

        def select_proxy() -> bool:
            try:
                rotator = ProxyWhirl(pool=pool, strategy="random")
                rotator.select()
                return True
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(update_health) for _ in range(50)] + [
                executor.submit(select_proxy) for _ in range(100)
            ]
            results = [f.result() for f in as_completed(futures)]

        assert all(results), "Health status update test failed"
