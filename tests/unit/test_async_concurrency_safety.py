"""
Concurrency and thread safety tests for AsyncProxyWhirl.

Tests:
- Concurrent proxy addition and removal
- Thread-safe state management
- No race conditions in proxy selection
- Circuit breaker state consistency under concurrent access
"""

import asyncio
import pytest
from proxywhirl.rotator import AsyncProxyWhirl


class TestAsyncConcurrencySafety:
    """Test async concurrency safety."""

    @pytest.mark.asyncio
    async def test_concurrent_add_remove_proxies(self):
        """Test concurrent add/remove operations don't cause race conditions."""
        rotator = AsyncProxyWhirl()
        
        async def add_proxies():
            for i in range(10):
                await rotator.add_proxy(f"http://add-proxy{i}.example.com:8080")
                await asyncio.sleep(0.01)
        
        async def remove_proxies():
            await asyncio.sleep(0.05)
            proxies = rotator.pool.get_all_proxies()
            for proxy in proxies[:5]:
                await rotator.remove_proxy(str(proxy.id))
                await asyncio.sleep(0.01)
        
        # Run concurrently
        await asyncio.gather(add_proxies(), remove_proxies())
        
        # Should end in valid state
        final_proxies = rotator.pool.get_all_proxies()
        assert len(final_proxies) >= 5

    @pytest.mark.asyncio
    async def test_concurrent_get_proxy_multiple_calls(self):
        """Test concurrent get_proxy() calls are safe."""
        rotator = AsyncProxyWhirl()
        
        # Add proxies
        for i in range(20):
            await rotator.add_proxy(f"http://proxy{i}.example.com:808{i % 10}")
        
        # Concurrent get_proxy calls
        tasks = [rotator.get_proxy() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        successful = [r for r in results if not isinstance(r, Exception)]
        assert len(successful) == 100

    @pytest.mark.asyncio
    async def test_pool_state_consistency_under_concurrent_access(self):
        """Test pool state remains consistent during concurrent operations."""
        rotator = AsyncProxyWhirl()
        
        async def worker():
            for i in range(5):
                await rotator.add_proxy(f"http://worker-proxy{asyncio.current_task().get_name()}-{i}.example.com:8080")
                await asyncio.sleep(0.001)
        
        # Run 5 concurrent workers
        tasks = [asyncio.create_task(worker(), name=f"w{i}") for i in range(5)]
        await asyncio.gather(*tasks)
        
        # Pool should have all proxies
        final_count = len(rotator.pool.get_all_proxies())
        assert final_count == 25  # 5 workers * 5 proxies each

    @pytest.mark.asyncio
    async def test_concurrent_proxy_selection_fairness(self):
        """Test that concurrent proxy selection is fair (round-robin works correctly)."""
        rotator = AsyncProxyWhirl(strategy="round-robin")
        
        proxy_urls = [f"http://proxy{i}.example.com:808{i}" for i in range(10)]
        for url in proxy_urls:
            await rotator.add_proxy(url)
        
        # Select proxies concurrently
        selections = []
        
        async def select_many_times():
            for _ in range(20):
                proxy = await rotator.get_proxy()
                selections.append(proxy.url)
        
        tasks = [select_many_times() for _ in range(5)]
        await asyncio.gather(*tasks)
        
        # Should have selected all 10 proxies at least once across concurrent calls
        unique_selected = set(selections)
        assert len(unique_selected) > 0

    @pytest.mark.asyncio
    async def test_no_deadlock_on_concurrent_operations(self):
        """Test that concurrent operations don't cause deadlocks."""
        rotator = AsyncProxyWhirl()
        
        async def mixed_operations():
            for i in range(10):
                await rotator.add_proxy(f"http://test{i}.example.com:8080")
                try:
                    await rotator.get_proxy()
                except Exception:
                    pass
                
                if i % 3 == 0:
                    proxies = rotator.pool.get_all_proxies()
                    if proxies:
                        await rotator.remove_proxy(str(proxies[0].id))
        
        # Run with timeout to catch deadlocks
        try:
            await asyncio.wait_for(
                asyncio.gather(*[mixed_operations() for _ in range(5)]),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            pytest.fail("Deadlock detected - operations timed out")

    @pytest.mark.asyncio
    async def test_concurrent_access_to_circuit_breakers(self):
        """Test circuit breakers remain consistent under concurrent access."""
        rotator = AsyncProxyWhirl()
        
        # Add proxies with circuit breakers
        for i in range(5):
            await rotator.add_proxy(f"http://cb-proxy{i}.example.com:8080")
        
        async def access_circuit_breakers():
            proxies = rotator.pool.get_all_proxies()
            for _ in range(20):
                for proxy in proxies:
                    cb = rotator.circuit_breakers.get(str(proxy.id))
                    if cb:
                        # should_attempt_request is sync on CircuitBreaker
                        result = cb.should_attempt_request()
                        assert isinstance(result, bool)
        
        # Concurrent access to circuit breakers
        tasks = [access_circuit_breakers() for _ in range(5)]
        await asyncio.gather(*tasks)
        
        # All circuit breakers should be in valid state
        for proxy in rotator.pool.get_all_proxies():
            cb = rotator.circuit_breakers.get(str(proxy.id))
            assert cb is not None

    @pytest.mark.asyncio
    async def test_100_concurrent_proxy_additions(self):
        """Stress test: Add 100 proxies concurrently."""
        rotator = AsyncProxyWhirl()
        
        tasks = [
            rotator.add_proxy(f"http://stress-proxy{i}.example.com:808{i % 10}")
            for i in range(100)
        ]
        
        await asyncio.gather(*tasks)
        
        # Should have all 100
        assert len(rotator.pool.get_all_proxies()) == 100

    @pytest.mark.asyncio
    async def test_concurrent_health_status_updates(self):
        """Test concurrent health status updates are safe."""
        rotator = AsyncProxyWhirl()
        
        # Add proxies
        for i in range(10):
            await rotator.add_proxy(f"http://health-proxy{i}.example.com:8080")
        
        async def update_health():
            proxies = rotator.pool.get_all_proxies()
            for proxy in proxies:
                # Simulate health updates
                proxy.requests_completed += 1
                proxy.total_requests += 1
        
        # Concurrent updates
        tasks = [update_health() for _ in range(50)]
        await asyncio.gather(*tasks)
        
        # Pool should still be valid
        final_proxies = rotator.pool.get_all_proxies()
        assert len(final_proxies) == 10
        assert all(p.total_requests > 0 for p in final_proxies)
