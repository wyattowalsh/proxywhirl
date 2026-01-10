"""
Unit tests for ProxyPool model.
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import uuid4

import pytest

from proxywhirl.models import HealthStatus, Proxy, ProxyPool, ProxySource


class TestProxyPoolBasics:
    """Test basic ProxyPool functionality."""

    def test_empty_pool_initialization(self):
        """Test creating an empty pool."""
        pool = ProxyPool(name="test-pool")
        assert pool.size == 0
        assert pool.healthy_count == 0
        assert pool.unhealthy_count == 0

    def test_pool_with_initial_proxies(self):
        """Test creating pool with initial proxies."""
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),  # type: ignore
            Proxy(url="http://proxy2.example.com:8080"),  # type: ignore
        ]
        pool = ProxyPool(name="test-pool", proxies=proxies)
        assert pool.size == 2

    def test_add_proxy(self):
        """Test adding proxy to pool."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        pool.add_proxy(proxy)
        assert pool.size == 1

    def test_add_duplicate_proxy_ignored(self):
        """Test that adding duplicate proxy is silently ignored."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        proxy2 = Proxy(url="http://proxy.example.com:8080")  # type: ignore

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        # Should only have one proxy
        assert pool.size == 1

    def test_add_proxy_exceeds_max_pool_size_raises_error(self):
        """Test that exceeding max_pool_size raises ValueError."""
        pool = ProxyPool(name="test-pool", max_pool_size=2)
        pool.add_proxy(Proxy(url="http://proxy1.example.com:8080"))  # type: ignore
        pool.add_proxy(Proxy(url="http://proxy2.example.com:8080"))  # type: ignore

        with pytest.raises(ValueError, match="maximum capacity"):
            pool.add_proxy(Proxy(url="http://proxy3.example.com:8080"))  # type: ignore

    def test_remove_proxy(self):
        """Test removing proxy from pool."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        pool.add_proxy(proxy)
        assert pool.size == 1

        pool.remove_proxy(proxy.id)
        assert pool.size == 0

    def test_remove_nonexistent_proxy_no_error(self):
        """Test that removing non-existent proxy doesn't raise error."""
        pool = ProxyPool(name="test-pool")
        fake_id = uuid4()
        pool.remove_proxy(fake_id)  # Should not raise
        assert pool.size == 0

    def test_get_proxy_by_id(self):
        """Test getting proxy by ID."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        pool.add_proxy(proxy)

        found = pool.get_proxy_by_id(proxy.id)
        assert found is not None
        assert found.id == proxy.id

    def test_get_proxy_by_id_not_found(self):
        """Test getting non-existent proxy by ID returns None."""
        pool = ProxyPool(name="test-pool")
        fake_id = uuid4()
        found = pool.get_proxy_by_id(fake_id)
        assert found is None


class TestProxyPoolFiltering:
    """Test ProxyPool filtering methods."""

    def test_filter_by_tags_single_tag(self):
        """Test filtering by single tag."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", tags={"fast", "us"})  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", tags={"slow", "eu"})  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        results = pool.filter_by_tags({"fast"})
        assert len(results) == 1
        assert results[0].id == proxy1.id

    def test_filter_by_tags_multiple_tags(self):
        """Test filtering by multiple tags (AND logic)."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", tags={"fast", "us"})  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", tags={"fast"})  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        results = pool.filter_by_tags({"fast", "us"})
        assert len(results) == 1
        assert results[0].id == proxy1.id

    def test_filter_by_tags_no_matches(self):
        """Test filtering by tags with no matches."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080", tags={"slow"})  # type: ignore
        pool.add_proxy(proxy)

        results = pool.filter_by_tags({"fast"})
        assert len(results) == 0

    def test_filter_by_source(self):
        """Test filtering by proxy source."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", source=ProxySource.USER)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", source=ProxySource.FETCHED)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        results = pool.filter_by_source(ProxySource.USER)
        assert len(results) == 1
        assert results[0].id == proxy1.id

    def test_get_healthy_proxies(self):
        """Test getting only healthy proxies."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.DEAD)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        results = pool.get_healthy_proxies()
        assert len(results) == 1
        assert results[0].id == proxy1.id

    def test_get_healthy_proxies_empty(self):
        """Test getting healthy proxies from pool with none."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.DEAD)  # type: ignore
        pool.add_proxy(proxy)

        results = pool.get_healthy_proxies()
        assert len(results) == 0


class TestProxyPoolClearUnhealthy:
    """Test ProxyPool clear_unhealthy method."""

    def test_clear_unhealthy_removes_dead_proxies(self):
        """Test that clear_unhealthy removes DEAD proxies."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.DEAD)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        removed_count = pool.clear_unhealthy()
        assert removed_count == 1
        assert pool.size == 1
        assert pool.proxies[0].id == proxy1.id

    def test_clear_unhealthy_removes_unhealthy_proxies(self):
        """Test that clear_unhealthy removes UNHEALTHY proxies."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.UNHEALTHY)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        removed_count = pool.clear_unhealthy()
        assert removed_count == 1
        assert pool.size == 1

    def test_clear_unhealthy_keeps_degraded_proxies(self):
        """Test that clear_unhealthy keeps DEGRADED proxies."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.DEGRADED)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.DEAD)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        removed_count = pool.clear_unhealthy()
        assert removed_count == 1
        assert pool.size == 1
        assert pool.proxies[0].health_status == HealthStatus.DEGRADED

    def test_clear_unhealthy_returns_zero_when_all_healthy(self):
        """Test that clear_unhealthy returns 0 when all proxies are healthy."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        pool.add_proxy(proxy)

        removed_count = pool.clear_unhealthy()
        assert removed_count == 0
        assert pool.size == 1


class TestProxyPoolStats:
    """Test ProxyPool statistics properties."""

    def test_healthy_count(self):
        """Test healthy proxy count."""
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(
            Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        )  # type: ignore
        pool.add_proxy(
            Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
        )  # type: ignore
        pool.add_proxy(Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.DEAD))  # type: ignore

        assert pool.healthy_count == 2

    def test_unhealthy_count(self):
        """Test unhealthy proxy count."""
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(
            Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        )  # type: ignore
        pool.add_proxy(Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.DEAD))  # type: ignore
        pool.add_proxy(
            Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.DEGRADED)
        )  # type: ignore

        assert pool.unhealthy_count == 2

    def test_total_requests(self):
        """Test total requests across all proxies."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080")  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080")  # type: ignore
        proxy1.record_success(100.0)
        proxy1.record_success(100.0)
        proxy2.record_success(100.0)

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        assert pool.total_requests == 3

    def test_overall_success_rate(self):
        """Test overall success rate calculation."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080")  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080")  # type: ignore

        # proxy1: 2 successes, 0 failures
        proxy1.record_success(100.0)
        proxy1.record_success(100.0)

        # proxy2: 1 success, 1 failure
        proxy2.record_success(100.0)
        proxy2.record_failure()

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        # 3 successes / 4 total = 0.75
        assert pool.overall_success_rate == 0.75

    def test_overall_success_rate_empty_pool(self):
        """Test overall success rate for empty pool."""
        pool = ProxyPool(name="test-pool")
        assert pool.overall_success_rate == 0.0


class TestProxyPoolThreadSafety:
    """Test ProxyPool thread-safety under concurrent access."""

    def test_concurrent_add_proxy(self):
        """Test that concurrent add_proxy operations are thread-safe."""
        pool = ProxyPool(name="test-pool", max_pool_size=1000)
        num_threads = 10
        proxies_per_thread = 10

        def add_proxies(thread_id: int) -> int:
            """Add proxies from a thread."""
            count = 0
            for i in range(proxies_per_thread):
                proxy = Proxy(url=f"http://proxy-{thread_id}-{i}.example.com:8080")  # type: ignore
                pool.add_proxy(proxy)
                count += 1
            return count

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(add_proxies, i) for i in range(num_threads)]
            results = [f.result() for f in as_completed(futures)]

        # All proxies should be added successfully
        assert sum(results) == num_threads * proxies_per_thread
        assert pool.size == num_threads * proxies_per_thread

    def test_concurrent_remove_proxy(self):
        """Test that concurrent remove_proxy operations are thread-safe."""
        pool = ProxyPool(name="test-pool")
        num_proxies = 100

        # Add proxies first
        proxy_ids = []
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")  # type: ignore
            pool.add_proxy(proxy)
            proxy_ids.append(proxy.id)

        assert pool.size == num_proxies

        # Remove proxies concurrently
        def remove_proxy(proxy_id):
            pool.remove_proxy(proxy_id)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(remove_proxy, pid) for pid in proxy_ids]
            for f in as_completed(futures):
                f.result()

        # All proxies should be removed
        assert pool.size == 0

    def test_concurrent_add_and_remove(self):
        """Test concurrent add and remove operations."""
        pool = ProxyPool(name="test-pool", max_pool_size=1000)
        num_operations = 100
        barrier = threading.Barrier(2)  # Synchronize start of both threads

        proxy_ids = []
        lock = threading.Lock()

        def add_proxies():
            """Add proxies continuously."""
            barrier.wait()  # Wait for both threads to be ready
            for i in range(num_operations):
                proxy = Proxy(url=f"http://add-proxy{i}.example.com:8080")  # type: ignore
                pool.add_proxy(proxy)
                with lock:
                    proxy_ids.append(proxy.id)

        def remove_proxies():
            """Remove proxies as they become available."""
            barrier.wait()  # Wait for both threads to be ready
            removed = 0
            while removed < num_operations:
                with lock:
                    if proxy_ids:
                        proxy_id = proxy_ids.pop(0)
                    else:
                        continue
                pool.remove_proxy(proxy_id)
                removed += 1

        add_thread = threading.Thread(target=add_proxies)
        remove_thread = threading.Thread(target=remove_proxies)

        add_thread.start()
        remove_thread.start()

        add_thread.join()
        remove_thread.join()

        # Pool should be empty (all added proxies were removed)
        assert pool.size == 0

    def test_concurrent_get_proxy_by_id(self):
        """Test that concurrent get_proxy_by_id operations are thread-safe."""
        pool = ProxyPool(name="test-pool")
        num_proxies = 50

        # Add proxies
        proxy_ids = []
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")  # type: ignore
            pool.add_proxy(proxy)
            proxy_ids.append(proxy.id)

        def get_proxy(proxy_id):
            """Get proxy by ID."""
            return pool.get_proxy_by_id(proxy_id)

        # Read proxies concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_proxy, pid) for pid in proxy_ids]
            results = [f.result() for f in as_completed(futures)]

        # All proxies should be found
        assert all(r is not None for r in results)
        assert len(results) == num_proxies

    def test_concurrent_filter_operations(self):
        """Test concurrent filter_by_tags and filter_by_source operations."""
        pool = ProxyPool(name="test-pool")

        # Add proxies with different tags and sources
        for i in range(50):
            tags = {"fast"} if i % 2 == 0 else {"slow"}
            source = ProxySource.USER if i % 3 == 0 else ProxySource.FETCHED
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080", tags=tags, source=source)  # type: ignore
            pool.add_proxy(proxy)

        def filter_by_tags():
            """Filter by tags."""
            return pool.filter_by_tags({"fast"})

        def filter_by_source():
            """Filter by source."""
            return pool.filter_by_source(ProxySource.USER)

        # Run filters concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            tag_futures = [executor.submit(filter_by_tags) for _ in range(20)]
            source_futures = [executor.submit(filter_by_source) for _ in range(20)]

            tag_results = [f.result() for f in as_completed(tag_futures)]
            source_results = [f.result() for f in as_completed(source_futures)]

        # All results should be consistent
        assert all(len(r) == 25 for r in tag_results)  # 25 "fast" proxies
        assert all(len(r) == 17 for r in source_results)  # 17 USER proxies (0, 3, 6, ..., 48)

    def test_concurrent_property_access(self):
        """Test concurrent access to computed properties."""
        pool = ProxyPool(name="test-pool")

        # Add proxies with different health statuses
        for i in range(100):
            status = HealthStatus.HEALTHY if i % 2 == 0 else HealthStatus.DEAD
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080", health_status=status)  # type: ignore
            proxy.total_requests = 10
            proxy.total_successes = 8
            pool.add_proxy(proxy)

        def access_properties():
            """Access various properties."""
            return {
                "size": pool.size,
                "healthy_count": pool.healthy_count,
                "unhealthy_count": pool.unhealthy_count,
                "total_requests": pool.total_requests,
                "success_rate": pool.overall_success_rate,
            }

        # Access properties concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(access_properties) for _ in range(50)]
            results = [f.result() for f in as_completed(futures)]

        # All results should be identical
        expected = results[0]
        assert all(r == expected for r in results)

    def test_concurrent_get_healthy_proxies(self):
        """Test concurrent get_healthy_proxies calls."""
        pool = ProxyPool(name="test-pool")

        # Add mixed health status proxies
        for i in range(100):
            status = HealthStatus.HEALTHY if i < 60 else HealthStatus.DEAD
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080", health_status=status)  # type: ignore
            pool.add_proxy(proxy)

        def get_healthy():
            """Get healthy proxies."""
            return pool.get_healthy_proxies()

        # Get healthy proxies concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_healthy) for _ in range(50)]
            results = [f.result() for f in as_completed(futures)]

        # All results should have the same count
        assert all(len(r) == 60 for r in results)

    def test_concurrent_clear_unhealthy(self):
        """Test concurrent clear_unhealthy calls."""
        pool = ProxyPool(name="test-pool")

        # Add mixed health status proxies
        for i in range(100):
            status = HealthStatus.HEALTHY if i < 60 else HealthStatus.DEAD
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080", health_status=status)  # type: ignore
            pool.add_proxy(proxy)

        assert pool.size == 100

        def clear():
            """Clear unhealthy proxies."""
            return pool.clear_unhealthy()

        # Clear concurrently from multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(clear) for _ in range(5)]
            results = [f.result() for f in as_completed(futures)]

        # Total removed should equal 40 (only counted once per proxy)
        # Some threads may return 0 if they run after the first clear
        assert sum(results) == 40
        assert pool.size == 60  # Only healthy proxies remain

    def test_concurrent_get_all_proxies_returns_snapshot(self):
        """Test that get_all_proxies returns a consistent snapshot."""
        pool = ProxyPool(name="test-pool", max_pool_size=200)

        # Add initial proxies
        for i in range(50):
            proxy = Proxy(url=f"http://initial{i}.example.com:8080")  # type: ignore
            pool.add_proxy(proxy)

        snapshots = []
        barrier = threading.Barrier(2)

        def get_snapshot():
            """Get a snapshot of all proxies."""
            barrier.wait()
            return pool.get_all_proxies()

        def modify_pool():
            """Modify the pool while snapshots are being taken."""
            barrier.wait()
            for i in range(50):
                proxy = Proxy(url=f"http://new{i}.example.com:8080")  # type: ignore
                pool.add_proxy(proxy)

        snapshot_thread = threading.Thread(target=lambda: snapshots.append(get_snapshot()))
        modify_thread = threading.Thread(target=modify_pool)

        snapshot_thread.start()
        modify_thread.start()

        snapshot_thread.join()
        modify_thread.join()

        # The snapshot should not be affected by modifications
        # It should contain exactly the proxies that were in the pool when snapshot was taken
        snapshot = snapshots[0]
        assert isinstance(snapshot, list)
        # Snapshot length should be between 50 and 100 depending on timing
        assert 50 <= len(snapshot) <= 100

    def test_concurrent_get_source_breakdown(self):
        """Test concurrent get_source_breakdown calls."""
        pool = ProxyPool(name="test-pool")

        # Add proxies with different sources
        for i in range(90):
            if i % 3 == 0:
                source = ProxySource.USER
            elif i % 3 == 1:
                source = ProxySource.FETCHED
            else:
                source = ProxySource.API
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080", source=source)  # type: ignore
            pool.add_proxy(proxy)

        def get_breakdown():
            """Get source breakdown."""
            return pool.get_source_breakdown()

        # Get breakdown concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_breakdown) for _ in range(50)]
            results = [f.result() for f in as_completed(futures)]

        # All results should be identical
        expected = {"user": 30, "fetched": 30, "api": 30}
        assert all(r == expected for r in results)

    def test_no_race_condition_on_duplicate_check(self):
        """Test that duplicate checking doesn't have race conditions."""
        pool = ProxyPool(name="test-pool", max_pool_size=200)
        num_threads = 10

        # All threads try to add the same proxy URLs
        def add_duplicates(thread_id: int):
            """Try to add duplicate proxies."""
            for i in range(10):
                # Each thread tries to add the same 10 proxy URLs
                proxy = Proxy(url=f"http://proxy{i}.example.com:8080")  # type: ignore
                pool.add_proxy(proxy)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(add_duplicates, i) for i in range(num_threads)]
            for f in as_completed(futures):
                f.result()

        # Should only have 10 unique proxies despite 100 add attempts
        assert pool.size == 10
