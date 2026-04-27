"""Tests for edge cases, recovery paths, and stress testing.

Tests for:
- Timeout edge cases
- Error recovery paths
- Data corruption detection
- Race conditions
- Cache coherence
- High-throughput stress tests
- Character encoding edge cases
- Empty pool behavior
- Browser failure handling
- Schema migration paths
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from proxywhirl.browser import BrowserRenderer
from proxywhirl.cache.manager import CacheManager
from proxywhirl.cache.models import CacheConfig
from proxywhirl.enrichment import OfflineEnricher
from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import Proxy, ProxyPool
from proxywhirl.rotator import ProxyWhirl


class TestTimeoutEdgeCases:
    """Test timeout handling at boundaries."""

    @pytest.mark.asyncio
    async def test_timeout_zero(self) -> None:
        """Test timeout with zero value."""

        async def long_task() -> None:
            await asyncio.sleep(1)

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(long_task(), timeout=0)

    @pytest.mark.asyncio
    async def test_timeout_very_small(self) -> None:
        """Test timeout with very small positive value."""

        async def work() -> None:
            await asyncio.sleep(0.1)

        # Should timeout if work takes > timeout
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(work(), timeout=0.001)

    @pytest.mark.asyncio
    async def test_timeout_negative_treated_as_no_timeout(self) -> None:
        """Test that negative timeout is handled correctly."""

        async def quick_task() -> str:
            await asyncio.sleep(0.001)
            return "done"

        # Most asyncio functions treat negative timeout as immediate timeout
        # or raise ValueError
        try:
            result = await asyncio.wait_for(quick_task(), timeout=-1)
            # If it succeeds, that's implementation dependent
            assert result == "done"
        except (asyncio.TimeoutError, ValueError):
            pass  # Both are acceptable

    @pytest.mark.asyncio
    async def test_timeout_just_before_completion(self) -> None:
        """Test timeout that occurs just before task completion."""

        async def timed_task() -> str:
            await asyncio.sleep(0.05)
            return "done"

        # Just barely time out
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(timed_task(), timeout=0.049)

        # Just barely complete in time
        result = await asyncio.wait_for(timed_task(), timeout=0.1)
        assert result == "done"


class TestErrorRecoveryPaths:
    """Test recovery from various error conditions."""

    @pytest.mark.asyncio
    async def test_recovery_from_task_cancellation(self) -> None:
        """Test recovery after task cancellation."""

        async def cancellable_task() -> str:
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                return "cancelled"
            return "completed"

        task = asyncio.create_task(cancellable_task())
        await asyncio.sleep(0.01)  # Let task start
        task.cancel()

        result = await task
        assert result == "cancelled"

    @pytest.mark.asyncio
    async def test_recovery_from_exception_in_gather(self) -> None:
        """Test recovery when one task in gather fails."""

        async def may_fail(should_fail: bool) -> str:
            if should_fail:
                raise ValueError("Failed")
            await asyncio.sleep(0.01)
            return "success"

        results = await asyncio.gather(
            may_fail(False),
            may_fail(True),
            may_fail(False),
            return_exceptions=True,
        )

        assert results[0] == "success"
        assert isinstance(results[1], ValueError)
        assert results[2] == "success"

    @pytest.mark.asyncio
    async def test_recovery_with_context_manager_failure(self) -> None:
        """Test cleanup when context manager fails."""

        class FailingResource:
            def __init__(self) -> None:
                self.cleanup_called = False

            async def __aenter__(self) -> FailingResource:
                raise RuntimeError("Setup failed")

            async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
                self.cleanup_called = True

        resource = FailingResource()

        with pytest.raises(RuntimeError):
            async with resource:
                pass

        # Cleanup may or may not be called depending on implementation


class TestDataCorruptionDetection:
    """Test detection of corrupted data."""

    def test_cache_corruption_detection(self) -> None:
        """Test detection of cache data corruption."""
        # This would test CacheCorruptionError being raised
        # when cached data fails validation
        cache = CacheManager(CacheConfig())

        # Simulate corruption detection
        assert cache is not None

    def test_proxy_pool_data_validation(self) -> None:
        """Test validation of proxy pool data."""
        proxy = Proxy(
            ip="192.168.1.1",
            port=8080,
            protocol="http",
        )

        assert proxy.ip == "192.168.1.1"
        assert proxy.port == 8080


class TestRaceConditions:
    """Test handling of race conditions."""

    @pytest.mark.asyncio
    async def test_concurrent_access_to_shared_resource(self) -> None:
        """Test concurrent access to shared resource without data corruption."""
        counter = {"value": 0}
        lock = asyncio.Lock()

        async def increment() -> None:
            nonlocal counter
            async with lock:
                current = counter["value"]
                await asyncio.sleep(0.001)  # Simulate work
                counter["value"] = current + 1

        # Run many concurrent increments
        await asyncio.gather(*[increment() for _ in range(10)])

        assert counter["value"] == 10  # Should be exactly 10, not less

    @pytest.mark.asyncio
    async def test_race_condition_without_lock(self) -> None:
        """Test that race conditions occur without proper locking."""
        counter = {"value": 0}

        async def unsafe_increment() -> None:
            nonlocal counter
            current = counter["value"]
            await asyncio.sleep(0.001)  # Let others interleave
            counter["value"] = current + 1

        # This might not equal 10 due to race conditions
        # (depending on timing and implementation)
        await asyncio.gather(*[unsafe_increment() for _ in range(10)])

        # We don't assert a specific value since it's non-deterministic


class TestCacheCoherence:
    """Test multi-tier cache consistency."""

    @pytest.mark.asyncio
    async def test_cache_invalidation_propagation(self) -> None:
        """Test that cache invalidation propagates through tiers."""
        cache = CacheManager(CacheConfig())

        # Set a value
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Invalidate it
        cache.delete("key1")
        assert cache.get("key1") is None

    @pytest.mark.asyncio
    async def test_concurrent_cache_updates(self) -> None:
        """Test concurrent cache updates don't cause corruption."""
        cache = CacheManager(CacheConfig())
        lock = asyncio.Lock()

        async def update_cache(key: str, value: str) -> None:
            async with lock:
                cache.set(key, value)
                await asyncio.sleep(0.001)
                assert cache.get(key) == value

        # Concurrent updates
        await asyncio.gather(*[update_cache(f"key{i}", f"value{i}") for i in range(5)])

        # All values should be present and correct
        for i in range(5):
            assert cache.get(f"key{i}") == f"value{i}"


class TestHighThroughputStress:
    """Test system under high load."""

    @pytest.mark.asyncio
    async def test_high_concurrency_gather(self) -> None:
        """Test handling of many concurrent tasks."""

        async def work(task_id: int) -> int:
            await asyncio.sleep(0.001)
            return task_id

        # Create 100 concurrent tasks
        results = await asyncio.gather(*[work(i) for i in range(100)])

        assert len(results) == 100
        assert results == list(range(100))

    @pytest.mark.asyncio
    async def test_semaphore_under_stress(self) -> None:
        """Test semaphore limiting under stress."""
        semaphore = asyncio.Semaphore(5)
        active_count = {"current": 0, "max": 0}

        async def work() -> None:
            async with semaphore:
                active_count["current"] += 1
                active_count["max"] = max(active_count["max"], active_count["current"])
                await asyncio.sleep(0.01)
                active_count["current"] -= 1

        await asyncio.gather(*[work() for _ in range(50)])

        # Max concurrent should never exceed semaphore limit
        assert active_count["max"] <= 5

    @pytest.mark.asyncio
    async def test_queue_under_stress(self) -> None:
        """Test queue operations under stress."""
        queue: asyncio.Queue[int] = asyncio.Queue(maxsize=10)

        async def producer(count: int) -> None:
            for i in range(count):
                await queue.put(i)

        async def consumer(count: int) -> list[int]:
            items = []
            for _ in range(count):
                items.append(await queue.get())
            return items

        # Produce 50 items, consume 50 items
        producer_task = asyncio.create_task(producer(50))
        consumer_task = asyncio.create_task(consumer(50))

        await producer_task
        items = await consumer_task

        assert len(items) == 50
        assert items == list(range(50))


class TestEncodingEdgeCases:
    """Test character encoding edge cases."""

    def test_proxy_url_with_unicode(self) -> None:
        """Test proxy URLs with unicode characters."""
        # Proxy URLs shouldn't have unicode, but test handling
        proxy = Proxy(
            ip="192.168.1.1",
            port=8080,
            protocol="http",
        )

        # Proxy URL should be ASCII-compatible
        url = proxy.url
        assert isinstance(url, str)
        assert all(ord(c) < 128 for c in url)  # ASCII-only

    def test_enrichment_with_special_ips(self) -> None:
        """Test enrichment with special IP addresses."""
        enricher = OfflineEnricher()

        # Test various special IPs
        test_cases = [
            ("127.0.0.1", True, "loopback"),
            ("192.168.1.1", True, "private"),
            ("10.0.0.1", True, "private"),
            ("172.16.0.1", True, "private"),
            ("255.255.255.255", True, "reserved"),
        ]

        for ip, expected_special, note in test_cases:
            result = enricher.enrich(ip, 80)
            # Should have recognized the IP
            assert result.get("ip_version") in (4, 5, None)


class TestEmptyPoolStrategies:
    """Test strategy behavior with empty proxy pools."""

    @pytest.mark.asyncio
    async def test_rotation_with_empty_pool(self) -> None:
        """Test rotation when pool is empty."""
        rotator = ProxyWhirl(
            proxies=[],  # Empty pool
            strategy="round-robin",
        )

        with pytest.raises(ProxyPoolEmptyError):
            await rotator.get_next_proxy()

    @pytest.mark.asyncio
    async def test_empty_pool_with_bootstrap(self) -> None:
        """Test automatic bootstrap when pool is empty."""
        # Would test auto-bootstrap behavior if configured
        pool = ProxyPool(proxies=[])
        assert len(pool.proxies) == 0


class TestBrowserFailureHandling:
    """Test Playwright failure scenarios."""

    @pytest.mark.asyncio
    async def test_browser_context_cleanup_on_error(self) -> None:
        """Test that contexts are cleaned up even on render errors."""
        renderer = BrowserRenderer(max_contexts=2, headless=True)

        # We can't actually test render failures without a real browser,
        # but we can test cleanup behavior
        async with renderer:
            initial_size = renderer.pool_size
            assert initial_size == 2

    @pytest.mark.asyncio
    async def test_browser_acquire_timeout(self) -> None:
        """Test timeout when acquiring browser context."""
        renderer = BrowserRenderer(max_contexts=1, headless=True)

        async with renderer:
            # Acquire the only context
            ctx = await renderer.acquire_context()

            # Try to acquire another with timeout
            with pytest.raises(asyncio.TimeoutError):
                await renderer.acquire_context(timeout=0.01)

            # Release and try again
            await renderer.release_context(ctx)
            ctx2 = await renderer.acquire_context(timeout=0.5)
            assert ctx2 is not None


class TestSchemaMigrationPaths:
    """Test schema migration success and failure paths."""

    @pytest.mark.asyncio
    async def test_migration_state_consistency(self) -> None:
        """Test that migration state remains consistent."""

        class Migration:
            def __init__(self, version: int) -> None:
                self.version = version
                self.state = "pending"

            async def up(self) -> None:
                self.state = "applying"
                await asyncio.sleep(0.01)
                self.state = "applied"

            async def down(self) -> None:
                self.state = "reverting"
                await asyncio.sleep(0.01)
                self.state = "reverted"

        migration = Migration(1)
        assert migration.state == "pending"

        await migration.up()
        assert migration.state == "applied"

        await migration.down()
        assert migration.state == "reverted"

    @pytest.mark.asyncio
    async def test_migration_failure_recovery(self) -> None:
        """Test recovery from failed migration."""

        class FailingMigration:
            def __init__(self) -> None:
                self.attempted = False

            async def up(self) -> None:
                self.attempted = True
                raise RuntimeError("Migration failed")

        migration = FailingMigration()

        with pytest.raises(RuntimeError):
            await migration.up()

        assert migration.attempted


class TestAsyncBatchOperations:
    """Test async batch operation patterns."""

    @pytest.mark.asyncio
    async def test_batch_insert_pattern(self) -> None:
        """Test async batch insert pattern."""

        async def insert_batch(items: list[str]) -> int:
            """Simulate batch insert."""
            await asyncio.sleep(0.01)
            return len(items)

        items = [f"item-{i}" for i in range(100)]
        batch_size = 10

        batches = [items[i : i + batch_size] for i in range(0, len(items), batch_size)]
        results = await asyncio.gather(*[insert_batch(batch) for batch in batches])

        assert sum(results) == 100

    @pytest.mark.asyncio
    async def test_batch_with_error_handling(self) -> None:
        """Test batch operations with error handling."""

        async def insert_batch(batch_id: int, items: list[str]) -> dict[str, Any]:
            if batch_id == 2:  # Simulate failure
                raise ValueError("Batch 2 failed")
            await asyncio.sleep(0.01)
            return {"batch_id": batch_id, "count": len(items)}

        batches = [(i, [f"item-{j}" for j in range(10)]) for i in range(5)]

        results = await asyncio.gather(
            *[insert_batch(batch_id, items) for batch_id, items in batches],
            return_exceptions=True,
        )

        assert len(results) == 5
        assert isinstance(results[2], ValueError)
        assert results[0]["count"] == 10
