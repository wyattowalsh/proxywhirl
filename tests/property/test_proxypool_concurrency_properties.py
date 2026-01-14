"""Property-based tests for ProxyPool thread-safety using Hypothesis."""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from hypothesis import given, settings
from hypothesis import strategies as st

from proxywhirl.models import HealthStatus, Proxy, ProxyPool


class TestProxyPoolConcurrencyInvariants:
    """Property-based tests verifying ProxyPool thread-safety invariants."""

    @given(
        num_proxies=st.integers(min_value=10, max_value=100),
        num_threads=st.integers(min_value=2, max_value=10),
    )
    @settings(max_examples=20, deadline=5000)
    def test_concurrent_add_preserves_count(self, num_proxies: int, num_threads: int):
        """Property: Concurrent adds should preserve total count (no lost updates)."""
        pool = ProxyPool(name="test-pool", max_pool_size=1000)
        proxies_per_thread = num_proxies // num_threads

        def add_proxies(thread_id: int):
            """Add unique proxies from a thread."""
            for i in range(proxies_per_thread):
                proxy = Proxy(url=f"http://t{thread_id}-p{i}.example.com:8080")
                pool.add_proxy(proxy)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(add_proxies, i) for i in range(num_threads)]
            for f in as_completed(futures):
                f.result()

        # Invariant: All proxies should be added
        expected_count = proxies_per_thread * num_threads
        assert pool.size == expected_count

    @given(
        num_proxies=st.integers(min_value=10, max_value=100),
        num_threads=st.integers(min_value=2, max_value=10),
    )
    @settings(max_examples=20, deadline=5000)
    def test_concurrent_remove_preserves_count(self, num_proxies: int, num_threads: int):
        """Property: Concurrent removes should preserve total count (no double-removes)."""
        pool = ProxyPool(name="test-pool")

        # Add proxies first
        proxy_ids = []
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            pool.add_proxy(proxy)
            proxy_ids.append(proxy.id)

        # Remove proxies concurrently
        def remove_batch(batch_ids):
            """Remove a batch of proxies."""
            for proxy_id in batch_ids:
                pool.remove_proxy(proxy_id)

        # Split proxy IDs among threads
        batch_size = len(proxy_ids) // num_threads
        batches = [proxy_ids[i * batch_size : (i + 1) * batch_size] for i in range(num_threads)]

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(remove_batch, batch) for batch in batches]
            for f in as_completed(futures):
                f.result()

        # Invariant: Pool should have removed all proxies in batches
        remaining = num_proxies - (batch_size * num_threads)
        assert pool.size == remaining

    @given(
        num_operations=st.integers(min_value=20, max_value=100),
    )
    @settings(max_examples=15, deadline=10000)
    def test_concurrent_add_remove_no_negative_count(self, num_operations: int):
        """Property: Pool size should never go negative under concurrent add/remove."""
        pool = ProxyPool(name="test-pool", max_pool_size=1000)
        proxy_ids = []
        lock = threading.Lock()
        size_samples = []

        def add_and_sample():
            """Add proxies and sample size."""
            for i in range(num_operations):
                proxy = Proxy(url=f"http://add{threading.get_ident()}-{i}.example.com:8080")
                pool.add_proxy(proxy)
                with lock:
                    proxy_ids.append(proxy.id)
                    size_samples.append(pool.size)

        def remove_and_sample():
            """Remove proxies as they become available and sample size."""
            removed = 0
            while removed < num_operations // 2:
                with lock:
                    if proxy_ids:
                        proxy_id = proxy_ids.pop(0)
                    else:
                        continue
                pool.remove_proxy(proxy_id)
                removed += 1
                with lock:
                    size_samples.append(pool.size)

        add_thread = threading.Thread(target=add_and_sample)
        remove_thread = threading.Thread(target=remove_and_sample)

        add_thread.start()
        remove_thread.start()

        add_thread.join()
        remove_thread.join()

        # Invariant: Size should never be negative
        assert all(size >= 0 for size in size_samples), f"Negative size found: {min(size_samples)}"

    @given(
        num_proxies=st.integers(min_value=20, max_value=80),
        num_readers=st.integers(min_value=3, max_value=10),
    )
    @settings(max_examples=15, deadline=5000)
    def test_concurrent_reads_return_consistent_snapshots(self, num_proxies: int, num_readers: int):
        """Property: Concurrent reads should return consistent data (no torn reads)."""
        pool = ProxyPool(name="test-pool")

        # Add proxies with known properties
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.total_requests = 10
            proxy.total_successes = 8
            pool.add_proxy(proxy)

        def read_properties():
            """Read various properties atomically."""
            size = pool.size
            total_reqs = pool.total_requests
            success_rate = pool.overall_success_rate
            healthy_count = pool.healthy_count

            # Invariant: Properties should be consistent with each other
            # Total requests should equal size * 10
            assert total_reqs == size * 10, f"Torn read: {total_reqs} != {size} * 10"

            return (size, total_reqs, success_rate, healthy_count)

        # Read concurrently
        with ThreadPoolExecutor(max_workers=num_readers) as executor:
            futures = [executor.submit(read_properties) for _ in range(num_readers * 5)]
            results = [f.result() for f in as_completed(futures)]

        # All reads should return consistent results
        assert all(r[0] == num_proxies for r in results), "Size should be consistent"
        assert all(r[1] == num_proxies * 10 for r in results), "Total requests should be consistent"

    @given(
        num_proxies=st.integers(min_value=10, max_value=50),
        num_filterers=st.integers(min_value=2, max_value=8),
    )
    @settings(max_examples=15, deadline=5000)
    def test_concurrent_filters_return_valid_subsets(self, num_proxies: int, num_filterers: int):
        """Property: Filter results should always be valid subsets of the pool."""
        pool = ProxyPool(name="test-pool")

        # Add proxies with tags
        for i in range(num_proxies):
            tags = {"fast"} if i % 2 == 0 else {"slow"}
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080", tags=tags)
            pool.add_proxy(proxy)

        expected_fast_count = (num_proxies + 1) // 2  # Ceiling division

        def filter_and_validate():
            """Filter and validate results."""
            fast_proxies = pool.filter_by_tags({"fast"})

            # Invariant: Filter results should be a valid subset
            assert len(fast_proxies) <= pool.size, "Filter returned more than pool size"
            assert all(
                "fast" in p.tags for p in fast_proxies
            ), "Filter returned proxies without tag"

            return len(fast_proxies)

        # Filter concurrently
        with ThreadPoolExecutor(max_workers=num_filterers) as executor:
            futures = [executor.submit(filter_and_validate) for _ in range(num_filterers * 3)]
            counts = [f.result() for f in as_completed(futures)]

        # All filters should return the same count
        assert all(
            count == expected_fast_count for count in counts
        ), f"Inconsistent filter counts: {set(counts)}"

    @given(
        num_healthy=st.integers(min_value=10, max_value=50),
        num_unhealthy=st.integers(min_value=10, max_value=50),
    )
    @settings(max_examples=15, deadline=5000)
    def test_health_counts_sum_to_total(self, num_healthy: int, num_unhealthy: int):
        """Property: healthy_count + unhealthy_count should always equal size."""
        pool = ProxyPool(name="test-pool")

        # Add mixed health proxies
        for i in range(num_healthy):
            proxy = Proxy(
                url=f"http://healthy{i}.example.com:8080", health_status=HealthStatus.HEALTHY
            )
            pool.add_proxy(proxy)

        for i in range(num_unhealthy):
            proxy = Proxy(
                url=f"http://unhealthy{i}.example.com:8080", health_status=HealthStatus.DEAD
            )
            pool.add_proxy(proxy)

        def check_invariant():
            """Check that counts sum correctly."""
            size = pool.size
            healthy = pool.healthy_count
            unhealthy = pool.unhealthy_count

            # Invariant: healthy + unhealthy = total
            assert (
                healthy + unhealthy == size
            ), f"Health counts don't sum: {healthy} + {unhealthy} != {size}"

            return (size, healthy, unhealthy)

        # Check concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(check_invariant) for _ in range(20)]
            results = [f.result() for f in as_completed(futures)]

        # All checks should pass (no assertion errors)
        assert len(results) == 20

    @given(
        num_proxies=st.integers(min_value=20, max_value=60),
        num_clearers=st.integers(min_value=2, max_value=5),
    )
    @settings(max_examples=15, deadline=5000)
    def test_clear_unhealthy_idempotent(self, num_proxies: int, num_clearers: int):
        """Property: Multiple concurrent clear_unhealthy calls should be idempotent."""
        pool = ProxyPool(name="test-pool")

        # Add half healthy, half unhealthy
        num_healthy = num_proxies // 2
        num_unhealthy = num_proxies - num_healthy

        for i in range(num_healthy):
            proxy = Proxy(
                url=f"http://healthy{i}.example.com:8080", health_status=HealthStatus.HEALTHY
            )
            pool.add_proxy(proxy)

        for i in range(num_unhealthy):
            proxy = Proxy(
                url=f"http://unhealthy{i}.example.com:8080", health_status=HealthStatus.DEAD
            )
            pool.add_proxy(proxy)

        def clear():
            """Clear unhealthy proxies."""
            return pool.clear_unhealthy()

        # Clear concurrently
        with ThreadPoolExecutor(max_workers=num_clearers) as executor:
            futures = [executor.submit(clear) for _ in range(num_clearers)]
            removed_counts = [f.result() for f in as_completed(futures)]

        # Invariant: Total removed should equal unhealthy count
        assert (
            sum(removed_counts) == num_unhealthy
        ), f"Removed {sum(removed_counts)} != {num_unhealthy}"

        # Invariant: Only healthy proxies should remain
        assert pool.size == num_healthy, f"Pool size {pool.size} != {num_healthy}"
        assert pool.unhealthy_count == 0, "Unhealthy proxies remain after clear"

    @given(
        num_proxies=st.integers(min_value=10, max_value=50),
    )
    @settings(max_examples=15, deadline=5000)
    def test_get_all_proxies_returns_independent_copy(self, num_proxies: int):
        """Property: get_all_proxies should return an independent copy (modifications don't affect pool)."""
        pool = ProxyPool(name="test-pool")

        # Add proxies
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            pool.add_proxy(proxy)

        # Get snapshot
        snapshot = pool.get_all_proxies()

        # Modify snapshot
        snapshot.clear()

        # Invariant: Pool should be unaffected
        assert pool.size == num_proxies, "Pool was affected by snapshot modification"

    @given(
        initial_proxies=st.integers(min_value=5, max_value=30),
        new_proxies=st.integers(min_value=5, max_value=30),
    )
    @settings(max_examples=15, deadline=5000)
    def test_snapshot_isolation_during_modification(self, initial_proxies: int, new_proxies: int):
        """Property: Snapshots should be isolated from concurrent modifications."""
        pool = ProxyPool(name="test-pool", max_pool_size=200)

        # Add initial proxies
        for i in range(initial_proxies):
            proxy = Proxy(url=f"http://initial{i}.example.com:8080")
            pool.add_proxy(proxy)

        barrier = threading.Barrier(2)
        snapshots = []

        def take_snapshot():
            """Take a snapshot."""
            barrier.wait()
            snapshot = pool.get_all_proxies()
            snapshots.append(snapshot)

        def modify_pool():
            """Add more proxies."""
            barrier.wait()
            for i in range(new_proxies):
                proxy = Proxy(url=f"http://new{i}.example.com:8080")
                pool.add_proxy(proxy)

        snapshot_thread = threading.Thread(target=take_snapshot)
        modify_thread = threading.Thread(target=modify_pool)

        snapshot_thread.start()
        modify_thread.start()

        snapshot_thread.join()
        modify_thread.join()

        # Invariant: Snapshot length should be valid (either before or during modification)
        snapshot_len = len(snapshots[0])
        assert (
            initial_proxies <= snapshot_len <= initial_proxies + new_proxies
        ), f"Invalid snapshot length: {snapshot_len}"

    @given(
        num_proxies=st.integers(min_value=10, max_value=50),
        num_duplicates=st.integers(min_value=5, max_value=20),
    )
    @settings(max_examples=15, deadline=5000)
    def test_duplicate_prevention_thread_safe(self, num_proxies: int, num_duplicates: int):
        """Property: Duplicate prevention should work correctly under concurrent access."""
        pool = ProxyPool(name="test-pool", max_pool_size=500)

        # Ensure num_duplicates doesn't exceed num_proxies
        actual_duplicates = min(num_duplicates, num_proxies)

        # Each thread tries to add the same set of proxies
        def add_proxies(thread_id: int):
            """Add proxies (some duplicates)."""
            for i in range(num_proxies):
                # First actual_duplicates are duplicates across all threads
                if i < actual_duplicates:
                    url = f"http://duplicate{i}.example.com:8080"
                else:
                    url = f"http://unique-{thread_id}-{i}.example.com:8080"
                proxy = Proxy(url=url)
                pool.add_proxy(proxy)

        num_threads = 5
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(add_proxies, i) for i in range(num_threads)]
            for f in as_completed(futures):
                f.result()

        # Invariant: Should have exactly actual_duplicates + (num_threads * (num_proxies - actual_duplicates))
        expected_unique = actual_duplicates + (num_threads * (num_proxies - actual_duplicates))
        assert (
            pool.size == expected_unique
        ), f"Duplicate prevention failed: {pool.size} != {expected_unique}"

        # Verify no actual duplicates by URL
        urls = [p.url for p in pool.get_all_proxies()]
        assert len(urls) == len(set(urls)), "Duplicate URLs found in pool"
