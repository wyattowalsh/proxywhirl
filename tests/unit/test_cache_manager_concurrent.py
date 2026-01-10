"""Unit tests for concurrent cache operations (TASK-202).

Tests thread-safety of CacheManager to verify race condition fixes for:
- L1 eviction while L2/L3 writes are in progress
- Concurrent cache operations not corrupting state
- TTL cleanup not racing with cache operations
"""

import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import SecretStr

from proxywhirl.cache_models import CacheConfig, CacheEntry


class TestConcurrentCacheAccess:
    """Test concurrent cache operations to verify race condition fixes (TASK-202)."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        from proxywhirl.cache.crypto import CredentialEncryptor

        encryptor = CredentialEncryptor()
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
            enable_background_cleanup=False,  # Disable for controlled testing
        )

    def test_concurrent_put_operations(self, cache_config: CacheConfig) -> None:
        """Test that concurrent put operations don't corrupt cache state."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)
        now = datetime.now(timezone.utc)
        num_threads = 10
        entries_per_thread = 20
        errors = []

        def put_entries(thread_id: int) -> None:
            """Put multiple entries from a single thread."""
            try:
                for i in range(entries_per_thread):
                    key = f"thread_{thread_id}_entry_{i}"
                    entry = CacheEntry(
                        key=key,
                        proxy_url=f"http://proxy-{thread_id}-{i}.example.com:8080",
                        source="concurrent_test",
                        fetch_time=now,
                        last_accessed=now,
                        ttl_seconds=3600,
                        expires_at=now + timedelta(seconds=3600),
                    )
                    result = manager.put(key, entry)
                    if not result:
                        errors.append(f"Thread {thread_id}: put failed for {key}")
            except Exception as e:
                errors.append(f"Thread {thread_id}: exception {e}")

        # Start threads
        threads = []
        for tid in range(num_threads):
            t = threading.Thread(target=put_entries, args=(tid,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Verify no errors
        assert len(errors) == 0, f"Errors during concurrent puts: {errors}"

        # Verify all entries are present
        expected_count = num_threads * entries_per_thread
        l1_size = manager.l1_tier.size()
        l2_size = manager.l2_tier.size()
        l3_size = manager.l3_tier.size()

        # At least one tier should have all entries (L3 should have everything)
        assert l3_size == expected_count, f"Expected {expected_count} entries in L3, got {l3_size}"

    def test_concurrent_get_and_put(self, cache_config: CacheConfig) -> None:
        """Test concurrent get and put operations don't cause corruption."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)
        now = datetime.now(timezone.utc)
        num_keys = 50
        errors = []
        stop_flag = threading.Event()

        # Pre-populate cache
        for i in range(num_keys):
            key = f"entry_{i}"
            entry = CacheEntry(
                key=key,
                proxy_url=f"http://proxy-{i}.example.com:8080",
                source="concurrent_test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
            )
            manager.put(key, entry)

        def reader_thread() -> None:
            """Continuously read entries."""
            try:
                while not stop_flag.is_set():
                    for i in range(num_keys):
                        key = f"entry_{i}"
                        result = manager.get(key)
                        if result is None:
                            errors.append(f"Reader: entry {key} unexpectedly None")
            except Exception as e:
                errors.append(f"Reader: exception {e}")

        def writer_thread() -> None:
            """Continuously update entries."""
            try:
                counter = 0
                while not stop_flag.is_set():
                    for i in range(num_keys):
                        key = f"entry_{i}"
                        entry = CacheEntry(
                            key=key,
                            proxy_url=f"http://proxy-{i}-updated-{counter}.example.com:8080",
                            source="concurrent_test",
                            fetch_time=now,
                            last_accessed=now,
                            ttl_seconds=3600,
                            expires_at=now + timedelta(seconds=3600),
                        )
                        result = manager.put(key, entry)
                        if not result:
                            errors.append(f"Writer: put failed for {key}")
                    counter += 1
            except Exception as e:
                errors.append(f"Writer: exception {e}")

        # Start reader and writer threads
        readers = [threading.Thread(target=reader_thread) for _ in range(3)]
        writers = [threading.Thread(target=writer_thread) for _ in range(2)]

        for t in readers + writers:
            t.start()

        # Run for 1 second
        time.sleep(1.0)
        stop_flag.set()

        # Wait for all threads
        for t in readers + writers:
            t.join(timeout=2.0)

        # Verify no errors
        assert len(errors) == 0, f"Errors during concurrent get/put: {errors}"

    def test_concurrent_eviction_and_promotion(self, cache_config: CacheConfig) -> None:
        """Test L1 eviction while L2/L3 writes are in progress (core race condition)."""
        from proxywhirl.cache import CacheManager

        # Small L1 to trigger evictions
        cache_config.l1_config.max_entries = 10
        manager = CacheManager(cache_config)
        now = datetime.now(timezone.utc)
        errors = []
        num_entries = 100

        def add_entries_to_trigger_eviction() -> None:
            """Add many entries to trigger L1 eviction."""
            try:
                for i in range(num_entries):
                    key = f"eviction_test_{i}"
                    entry = CacheEntry(
                        key=key,
                        proxy_url=f"http://proxy-{i}.example.com:8080",
                        source="eviction_test",
                        fetch_time=now,
                        last_accessed=now,
                        ttl_seconds=3600,
                        expires_at=now + timedelta(seconds=3600),
                    )
                    result = manager.put(key, entry)
                    if not result:
                        errors.append(f"Put failed for {key}")
            except Exception as e:
                errors.append(f"Exception during eviction: {e}")

        def read_and_promote() -> None:
            """Read entries to trigger promotion from L2/L3 to L1."""
            try:
                for i in range(0, num_entries, 5):  # Sample every 5th entry
                    key = f"eviction_test_{i}"
                    result = manager.get(key)
                    # Entry might not exist yet if writer hasn't added it
                    # So we don't check for None here
            except Exception as e:
                errors.append(f"Exception during promotion: {e}")

        # Run eviction and promotion concurrently
        t1 = threading.Thread(target=add_entries_to_trigger_eviction)
        t2 = threading.Thread(target=read_and_promote)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # Verify no errors
        assert len(errors) == 0, f"Errors during concurrent eviction/promotion: {errors}"

        # Verify L1 is at capacity
        assert manager.l1_tier.size() <= cache_config.l1_config.max_entries

        # Verify all entries are in L2/L3 (even if evicted from L1)
        l3_size = manager.l3_tier.size()
        assert l3_size == num_entries, f"Expected {num_entries} in L3, got {l3_size}"

    def test_concurrent_delete_and_get(self, cache_config: CacheConfig) -> None:
        """Test concurrent delete and get operations."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)
        now = datetime.now(timezone.utc)
        num_keys = 50
        errors = []

        # Pre-populate
        for i in range(num_keys):
            key = f"delete_test_{i}"
            entry = CacheEntry(
                key=key,
                proxy_url=f"http://proxy-{i}.example.com:8080",
                source="delete_test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
            )
            manager.put(key, entry)

        def deleter() -> None:
            """Delete all entries."""
            try:
                for i in range(num_keys):
                    key = f"delete_test_{i}"
                    manager.delete(key)
            except Exception as e:
                errors.append(f"Deleter: exception {e}")

        def reader() -> None:
            """Try to read entries (may get None after deletion)."""
            try:
                for i in range(num_keys):
                    key = f"delete_test_{i}"
                    manager.get(key)  # May return None, that's ok
            except Exception as e:
                errors.append(f"Reader: exception {e}")

        # Run concurrently
        t1 = threading.Thread(target=deleter)
        t2 = threading.Thread(target=reader)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # Verify no errors
        assert len(errors) == 0, f"Errors during concurrent delete/get: {errors}"

        # Verify all deleted
        for i in range(num_keys):
            key = f"delete_test_{i}"
            result = manager.get(key)
            assert result is None, f"Entry {key} should be deleted"

    def test_concurrent_ttl_cleanup(self, cache_config: CacheConfig) -> None:
        """Test TTL cleanup doesn't race with cache operations."""
        from proxywhirl.cache import CacheManager
        from proxywhirl.cache.manager import TTLManager

        manager = CacheManager(cache_config)
        ttl_manager = TTLManager(manager, cleanup_interval=60)
        now = datetime.now(timezone.utc)
        errors = []
        stop_flag = threading.Event()

        # Add mix of expired and valid entries
        for i in range(50):
            key = f"ttl_test_{i}"
            if i % 2 == 0:
                # Expired
                entry = CacheEntry(
                    key=key,
                    proxy_url=f"http://proxy-{i}.example.com:8080",
                    source="ttl_test",
                    fetch_time=now - timedelta(hours=2),
                    last_accessed=now - timedelta(hours=2),
                    ttl_seconds=3600,
                    expires_at=now - timedelta(hours=1),
                )
            else:
                # Valid
                entry = CacheEntry(
                    key=key,
                    proxy_url=f"http://proxy-{i}.example.com:8080",
                    source="ttl_test",
                    fetch_time=now,
                    last_accessed=now,
                    ttl_seconds=3600,
                    expires_at=now + timedelta(hours=1),
                )
            manager.put(key, entry)

        def cleanup_worker() -> None:
            """Run TTL cleanup."""
            try:
                while not stop_flag.is_set():
                    ttl_manager._cleanup_expired_entries()
                    time.sleep(0.01)
            except Exception as e:
                errors.append(f"Cleanup: exception {e}")

        def cache_worker() -> None:
            """Perform cache operations."""
            try:
                counter = 0
                while not stop_flag.is_set():
                    # Mix of operations
                    key = f"ttl_test_{counter % 50}"
                    manager.get(key)
                    if counter % 3 == 0:
                        # Add new entry
                        new_entry = CacheEntry(
                            key=f"new_{counter}",
                            proxy_url=f"http://new-{counter}.example.com:8080",
                            source="ttl_test",
                            fetch_time=now,
                            last_accessed=now,
                            ttl_seconds=3600,
                            expires_at=now + timedelta(hours=1),
                        )
                        manager.put(f"new_{counter}", new_entry)
                    counter += 1
            except Exception as e:
                errors.append(f"Cache worker: exception {e}")

        # Start concurrent operations
        cleanup_thread = threading.Thread(target=cleanup_worker)
        workers = [threading.Thread(target=cache_worker) for _ in range(3)]

        cleanup_thread.start()
        for w in workers:
            w.start()

        # Run for 0.5 seconds
        time.sleep(0.5)
        stop_flag.set()

        # Wait for all threads
        cleanup_thread.join(timeout=2.0)
        for w in workers:
            w.join(timeout=2.0)

        # Verify no errors
        assert len(errors) == 0, f"Errors during concurrent TTL cleanup: {errors}"

    def test_lock_is_reentrant(self, cache_config: CacheConfig) -> None:
        """Test that the lock is reentrant (RLock) for nested operations."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)
        now = datetime.now(timezone.utc)

        # This should not deadlock due to nested lock acquisition
        entry = CacheEntry(
            key="test_key",
            proxy_url="http://proxy.example.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
        )

        # put() calls clear() internally in some paths, both use lock
        manager.put("test_key", entry)
        # get() may call delete() for expired entries, both use lock
        result = manager.get("test_key")
        assert result is not None

    def test_concurrent_invalidate_by_health(self, cache_config: CacheConfig) -> None:
        """Test concurrent health invalidation operations."""
        from proxywhirl.cache import CacheManager

        cache_config.health_check_invalidation = True
        cache_config.failure_threshold = 5

        manager = CacheManager(cache_config)
        now = datetime.now(timezone.utc)
        num_keys = 20
        errors = []

        # Pre-populate
        for i in range(num_keys):
            key = f"health_test_{i}"
            entry = CacheEntry(
                key=key,
                proxy_url=f"http://proxy-{i}.example.com:8080",
                source="health_test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
            )
            manager.put(key, entry)

        def invalidate_worker(key_offset: int) -> None:
            """Invalidate entries by health."""
            try:
                for i in range(10):  # Exceed failure threshold
                    for j in range(num_keys):
                        key = f"health_test_{j}"
                        manager.invalidate_by_health(key)
            except Exception as e:
                errors.append(f"Worker {key_offset}: exception {e}")

        # Run multiple workers concurrently
        threads = [threading.Thread(target=invalidate_worker, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Verify no errors
        assert len(errors) == 0, f"Errors during concurrent health invalidation: {errors}"

        # All entries should be evicted (exceeded failure threshold)
        for i in range(num_keys):
            key = f"health_test_{i}"
            result = manager.get(key)
            assert result is None, f"Entry {key} should be evicted after health failures"
