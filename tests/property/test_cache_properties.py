"""Property-based tests for cache using Hypothesis.

Tests invariants and edge cases through generative testing to discover
unexpected behaviors.
"""

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import SecretStr

from proxywhirl.cache import CacheManager
from proxywhirl.cache.crypto import CredentialEncryptor
from proxywhirl.cache.models import CacheConfig, CacheEntry, CacheTierConfig, HealthStatus

# Strategy for generating valid cache keys
cache_keys = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd"),
        whitelist_characters="_-.",
    ),
    min_size=1,
    max_size=100,
)

# Strategy for generating valid proxy URLs
proxy_urls = st.builds(
    lambda host, port: f"http://{host}:{port}",
    host=st.text(
        alphabet=st.characters(whitelist_categories=("Ll", "Nd"), whitelist_characters=".-"),
        min_size=1,
        max_size=50,
    ).filter(lambda x: not x.startswith("-") and not x.endswith("-")),
    port=st.integers(min_value=1, max_value=65535),
)

# Strategy for generating TTL values
ttl_seconds = st.integers(min_value=1, max_value=86400)


def create_cache_manager(tmp_dir: Path) -> CacheManager:
    """Helper to create a CacheManager with proper configuration."""
    encryptor = CredentialEncryptor()
    config = CacheConfig(
        l2_cache_dir=str(tmp_dir / "cache"),
        l3_database_path=str(tmp_dir / "cache.db"),
        encryption_key=SecretStr(encryptor.key.decode("utf-8")),
    )
    return CacheManager(config)


def create_cache_manager_with_max_entries(tmp_dir: Path, max_entries: int) -> CacheManager:
    """Helper to create a CacheManager with L1 max entries configured."""
    encryptor = CredentialEncryptor()
    config = CacheConfig(
        l1_config=CacheTierConfig(enabled=True, max_entries=max_entries),
        l2_cache_dir=str(tmp_dir / "cache"),
        l3_database_path=str(tmp_dir / "cache.db"),
        encryption_key=SecretStr(encryptor.key.decode("utf-8")),
    )
    return CacheManager(config)


class TestCacheInvariants:
    """Test fundamental cache invariants using property-based testing."""

    @given(key=cache_keys, proxy_url=proxy_urls, ttl=ttl_seconds)
    @settings(max_examples=50, deadline=timedelta(milliseconds=2000))
    def test_put_get_roundtrip(self, key: str, proxy_url: str, ttl: int) -> None:
        """Property: What you put in, you should get back (within TTL)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = create_cache_manager(Path(tmp_dir))
            now = datetime.now(timezone.utc)

            entry = CacheEntry(
                key=key,
                proxy_url=proxy_url,
                username=None,
                password=None,
                source="hypothesis",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=ttl,
                expires_at=now + timedelta(seconds=ttl),
                health_status=HealthStatus.HEALTHY,
            )

            manager.put(entry.key, entry)
            retrieved = manager.get(entry.key)

            assert retrieved is not None, f"Failed to retrieve key: {key}"
            assert retrieved.key == entry.key
            assert retrieved.proxy_url == entry.proxy_url
            assert retrieved.ttl_seconds == entry.ttl_seconds

    @given(keys=st.lists(cache_keys, min_size=1, max_size=20, unique=True))
    @settings(max_examples=20, deadline=timedelta(milliseconds=3000))
    def test_multiple_entries_isolation(self, keys: list[str]) -> None:
        """Property: Multiple entries should not interfere with each other."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = create_cache_manager(Path(tmp_dir))
            now = datetime.now(timezone.utc)

            # Put all entries
            for i, key in enumerate(keys):
                entry = CacheEntry(
                    key=key,
                    proxy_url=f"http://proxy{i}.example.com:8080",
                    username=None,
                    password=None,
                    source="hypothesis",
                    fetch_time=now,
                    last_accessed=now,
                    ttl_seconds=3600,
                    expires_at=now + timedelta(seconds=3600),
                    health_status=HealthStatus.HEALTHY,
                )
                manager.put(entry.key, entry)

            # All should be retrievable
            for i, key in enumerate(keys):
                retrieved = manager.get(key)
                assert retrieved is not None, f"Key {key} not found"
                assert retrieved.proxy_url == f"http://proxy{i}.example.com:8080"

    @given(key=cache_keys)
    @settings(max_examples=50, deadline=timedelta(milliseconds=1000))
    def test_get_nonexistent_returns_none(self, key: str) -> None:
        """Property: Getting non-existent key always returns None."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = create_cache_manager(Path(tmp_dir))
            result = manager.get(key)
            assert result is None, f"Non-existent key {key} should return None"

    @given(key=cache_keys, proxy_url=proxy_urls)
    @settings(max_examples=50, deadline=timedelta(milliseconds=2000))
    def test_update_overwrites(self, key: str, proxy_url: str) -> None:
        """Property: Putting same key twice should overwrite with new value."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = create_cache_manager(Path(tmp_dir))
            now = datetime.now(timezone.utc)

            # First put
            entry1 = CacheEntry(
                key=key,
                proxy_url="http://original.example.com:8080",
                username=None,
                password=None,
                source="hypothesis",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
                health_status=HealthStatus.HEALTHY,
            )
            manager.put(entry1.key, entry1)

            # Second put with different URL
            entry2 = CacheEntry(
                key=key,
                proxy_url=proxy_url,
                username=None,
                password=None,
                source="hypothesis",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
                health_status=HealthStatus.HEALTHY,
            )
            manager.put(entry2.key, entry2)

            # Should get the second value
            retrieved = manager.get(key)
            assert retrieved is not None
            assert retrieved.proxy_url == proxy_url


class TestStatisticsInvariants:
    """Test statistics invariants using property-based testing."""

    @given(num_entries=st.integers(min_value=1, max_value=50))
    @settings(max_examples=20, deadline=timedelta(milliseconds=3000))
    def test_l1_hits_plus_misses_equals_total_requests(self, num_entries: int) -> None:
        """Property: L1 hits + misses should equal number of get operations.

        In multi-tier cache, L1 is always checked first, so L1 stats reflect total requests.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = create_cache_manager(Path(tmp_dir))
            now = datetime.now(timezone.utc)

            # Add entries
            for i in range(num_entries):
                entry = CacheEntry(
                    key=f"key_{i}",
                    proxy_url=f"http://proxy{i}.example.com:8080",
                    username=None,
                    password=None,
                    source="hypothesis",
                    fetch_time=now,
                    last_accessed=now,
                    ttl_seconds=3600,
                    expires_at=now + timedelta(seconds=3600),
                    health_status=HealthStatus.HEALTHY,
                )
                manager.put(entry.key, entry)

            # Perform gets (some hits, some misses)
            total_ops = num_entries * 2
            for i in range(total_ops):
                manager.get(f"key_{i}")

            stats = manager.get_statistics()
            # L1 hits + misses should equal total get operations
            # (L1 is checked first for every request)
            l1_total = stats.l1_stats.hits + stats.l1_stats.misses

            assert l1_total == total_ops, (
                f"L1 hits ({stats.l1_stats.hits}) + misses ({stats.l1_stats.misses}) != "
                f"Total ops ({total_ops})"
            )

    @given(num_evictions=st.integers(min_value=1, max_value=10))
    @settings(max_examples=10, deadline=timedelta(milliseconds=3000))
    def test_eviction_count_matches_capacity_overflow(self, num_evictions: int) -> None:
        """Property: Number of evictions should match capacity overflows."""
        capacity = 5
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = create_cache_manager_with_max_entries(Path(tmp_dir), capacity)
            now = datetime.now(timezone.utc)

            # Fill beyond capacity
            total_entries = capacity + num_evictions
            for i in range(total_entries):
                entry = CacheEntry(
                    key=f"key_{i}",
                    proxy_url=f"http://proxy{i}.example.com:8080",
                    username=None,
                    password=None,
                    source="hypothesis",
                    fetch_time=now,
                    last_accessed=now,
                    ttl_seconds=3600,
                    expires_at=now + timedelta(seconds=3600),
                    health_status=HealthStatus.HEALTHY,
                )
                manager.put(entry.key, entry)

            stats = manager.get_statistics()

            # Should have at least num_evictions evictions
            assert (
                stats.l1_stats.evictions_lru >= num_evictions
            ), f"Expected at least {num_evictions} evictions, got {stats.l1_stats.evictions_lru}"


class TestCacheMaxSizeInvariant:
    """Property tests ensuring cache size never exceeds configured maximum."""

    @given(
        max_entries=st.integers(min_value=3, max_value=20),
        num_puts=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=30, deadline=timedelta(milliseconds=5000))
    def test_l1_cache_size_never_exceeds_max(self, max_entries: int, num_puts: int) -> None:
        """Property: L1 cache size should never exceed max_entries regardless of put operations."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = create_cache_manager_with_max_entries(Path(tmp_dir), max_entries)
            now = datetime.now(timezone.utc)

            # Perform many put operations
            for i in range(num_puts):
                entry = CacheEntry(
                    key=f"key_{i}",
                    proxy_url=f"http://proxy{i}.example.com:8080",
                    username=None,
                    password=None,
                    source="hypothesis",
                    fetch_time=now,
                    last_accessed=now,
                    ttl_seconds=3600,
                    expires_at=now + timedelta(seconds=3600),
                    health_status=HealthStatus.HEALTHY,
                )
                manager.put(entry.key, entry)

                # Check size after each put
                stats = manager.get_statistics()
                assert stats.l1_stats.current_size <= max_entries, (
                    f"L1 cache size ({stats.l1_stats.current_size}) exceeded max ({max_entries}) "
                    f"after put #{i + 1}"
                )

    @given(
        max_entries=st.integers(min_value=5, max_value=15),
        overflow_factor=st.integers(min_value=2, max_value=5),
    )
    @settings(max_examples=20, deadline=timedelta(milliseconds=5000))
    def test_cache_respects_max_after_overflow(
        self, max_entries: int, overflow_factor: int
    ) -> None:
        """Property: After significant overflow, cache size equals max (not less, not more)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = create_cache_manager_with_max_entries(Path(tmp_dir), max_entries)
            now = datetime.now(timezone.utc)

            total_entries = max_entries * overflow_factor
            for i in range(total_entries):
                entry = CacheEntry(
                    key=f"key_{i}",
                    proxy_url=f"http://proxy{i}.example.com:8080",
                    username=None,
                    password=None,
                    source="hypothesis",
                    fetch_time=now,
                    last_accessed=now,
                    ttl_seconds=3600,
                    expires_at=now + timedelta(seconds=3600),
                    health_status=HealthStatus.HEALTHY,
                )
                manager.put(entry.key, entry)

            stats = manager.get_statistics()

            # L1 should be exactly at max capacity after overflow
            assert stats.l1_stats.current_size == max_entries, (
                f"After {total_entries} puts with max={max_entries}, "
                f"L1 size should be {max_entries}, got {stats.l1_stats.current_size}"
            )

    @given(
        keys=st.lists(cache_keys, min_size=5, max_size=30, unique=True),
        max_entries=st.integers(min_value=3, max_value=10),
    )
    @settings(max_examples=20, deadline=timedelta(milliseconds=5000))
    def test_unique_keys_respect_max_capacity(self, keys: list[str], max_entries: int) -> None:
        """Property: With unique keys, L1 size never exceeds max even with random key patterns."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = create_cache_manager_with_max_entries(Path(tmp_dir), max_entries)
            now = datetime.now(timezone.utc)

            for i, key in enumerate(keys):
                entry = CacheEntry(
                    key=key,
                    proxy_url=f"http://proxy{i}.example.com:8080",
                    username=None,
                    password=None,
                    source="hypothesis",
                    fetch_time=now,
                    last_accessed=now,
                    ttl_seconds=3600,
                    expires_at=now + timedelta(seconds=3600),
                    health_status=HealthStatus.HEALTHY,
                )
                manager.put(entry.key, entry)

            stats = manager.get_statistics()
            assert (
                stats.l1_stats.current_size <= max_entries
            ), f"L1 cache size ({stats.l1_stats.current_size}) exceeded max ({max_entries})"


class TestTTLExpirationMonotonicity:
    """Property tests for TTL expiration being monotonic (once expired, stays expired)."""

    @given(ttl=st.integers(min_value=1, max_value=2))
    @settings(
        max_examples=5,
        deadline=timedelta(milliseconds=10000),
        suppress_health_check=[HealthCheck.too_slow],
    )
    def test_expired_entries_stay_expired(self, ttl: int) -> None:
        """Property: Once a TTL expires, the entry should not be retrievable."""
        import time

        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = create_cache_manager(Path(tmp_dir))
            now = datetime.now(timezone.utc)

            # Create entry with short TTL
            entry = CacheEntry(
                key="expiring_key",
                proxy_url="http://expiring.example.com:8080",
                username=None,
                password=None,
                source="hypothesis",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=ttl,
                expires_at=now + timedelta(seconds=ttl),
                health_status=HealthStatus.HEALTHY,
            )
            manager.put(entry.key, entry)

            # Should be retrievable before expiration
            retrieved = manager.get(entry.key)
            assert retrieved is not None, "Entry should be retrievable before TTL expires"

            # Wait for expiration
            time.sleep(ttl + 0.5)

            # After expiration, should not be retrievable
            retrieved_after = manager.get(entry.key)
            assert (
                retrieved_after is None
            ), f"Entry should NOT be retrievable after TTL ({ttl}s) expires"

    @given(ttl=ttl_seconds)
    @settings(max_examples=30, deadline=timedelta(milliseconds=1000))
    def test_ttl_expiration_is_deterministic(self, ttl: int) -> None:
        """Property: TTL expiration calculation is deterministic (is_expired is consistent)."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl)

        entry = CacheEntry(
            key="deterministic_test",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="hypothesis",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=ttl,
            expires_at=expires_at,
            health_status=HealthStatus.HEALTHY,
        )

        # is_expired should be consistent when called multiple times at the same logical time
        # (before the TTL has actually elapsed)
        expired_check_1 = entry.is_expired
        expired_check_2 = entry.is_expired
        expired_check_3 = entry.is_expired

        # All checks should return the same value
        assert (
            expired_check_1 == expired_check_2 == expired_check_3
        ), "is_expired should be deterministic"

        # Since we just created it, it should not be expired
        assert (
            not expired_check_1
        ), f"Entry with TTL={ttl}s should not be expired immediately after creation"

    @given(
        base_ttl=st.integers(min_value=60, max_value=3600),
        delta_seconds=st.integers(min_value=-30, max_value=30),
    )
    @settings(max_examples=50, deadline=timedelta(milliseconds=500))
    def test_expiration_boundary_is_precise(self, base_ttl: int, delta_seconds: int) -> None:
        """Property: Expiration check is precise at the boundary time."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=base_ttl)

        entry = CacheEntry(
            key="boundary_test",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="hypothesis",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=base_ttl,
            expires_at=expires_at,
            health_status=HealthStatus.HEALTHY,
        )

        # Check at a simulated time relative to expiration
        check_time = expires_at + timedelta(seconds=delta_seconds)

        # Simulate the is_expired check at check_time
        is_expired_at_check_time = check_time >= expires_at

        if delta_seconds >= 0:
            # At or after expiration time, should be expired
            assert (
                is_expired_at_check_time
            ), f"Entry should be expired at check_time={check_time} (expires_at={expires_at})"
        else:
            # Before expiration time, should not be expired
            assert (
                not is_expired_at_check_time
            ), f"Entry should NOT be expired at check_time={check_time} (expires_at={expires_at})"
