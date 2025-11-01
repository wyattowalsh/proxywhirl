"""Property-based tests for cache using Hypothesis.

Tests invariants and edge cases through generative testing to discover
unexpected behaviors.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import SecretStr

from proxywhirl.cache import CacheManager
from proxywhirl.cache_crypto import CredentialEncryptor
from proxywhirl.cache_models import CacheConfig, CacheEntry, HealthStatus

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


class TestCacheInvariants:
    """Test fundamental cache invariants using property-based testing."""

    @given(key=cache_keys, proxy_url=proxy_urls, ttl=ttl_seconds)
    @settings(max_examples=50, deadline=timedelta(milliseconds=1000))
    def test_put_get_roundtrip(
        self, tmp_path: Path, key: str, proxy_url: str, ttl: int
    ) -> None:
        """Property: What you put in, you should get back (within TTL)."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
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
    @settings(max_examples=20, deadline=timedelta(milliseconds=2000))
    def test_multiple_entries_isolation(self, tmp_path: Path, keys: list[str]) -> None:
        """Property: Multiple entries should not interfere with each other."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
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
    @settings(max_examples=50, deadline=timedelta(milliseconds=500))
    def test_get_nonexistent_returns_none(self, tmp_path: Path, key: str) -> None:
        """Property: Getting non-existent key always returns None."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)

        result = manager.get(key)
        assert result is None, f"Non-existent key {key} should return None"

    @given(key=cache_keys, proxy_url=proxy_urls)
    @settings(max_examples=50, deadline=timedelta(milliseconds=1000))
    def test_update_overwrites(self, tmp_path: Path, key: str, proxy_url: str) -> None:
        """Property: Putting same key twice should overwrite with new value."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
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

    @given(num_entries=st.integers(min_value=1, max_value=100))
    @settings(max_examples=20, deadline=timedelta(milliseconds=2000))
    def test_hits_plus_misses_equals_total_requests(
        self, tmp_path: Path, num_entries: int
    ) -> None:
        """Property: Total hits + misses should equal number of get operations."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
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
        for i in range(num_entries * 2):
            manager.get(f"key_{i}")

        stats = manager.get_statistics()
        total_hits = stats.l1_stats.hits + stats.l2_stats.hits + stats.l3_stats.hits
        total_misses = stats.l1_stats.misses + stats.l2_stats.misses + stats.l3_stats.misses

        # Total operations should be num_entries * 2
        assert (
            total_hits + total_misses == num_entries * 2
        ), f"Hits ({total_hits}) + Misses ({total_misses}) != Total ops ({num_entries * 2})"

    @given(num_evictions=st.integers(min_value=1, max_value=10))
    @settings(max_examples=10, deadline=timedelta(milliseconds=2000))
    def test_eviction_count_matches_capacity_overflow(
        self, tmp_path: Path, num_evictions: int
    ) -> None:
        """Property: Number of evictions should match capacity overflows."""
        encryptor = CredentialEncryptor()
        capacity = 5
        config = CacheConfig(
            l1_config=CacheConfig.model_fields["l1_config"].default.__class__(
                enabled=True, max_entries=capacity
            ),
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
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


@pytest.fixture(autouse=True)
def _setup_tmp_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Make tmp_path available to hypothesis tests."""
    monkeypatch.setattr(
        "tests.property.test_cache_properties.tmp_path_fixture", tmp_path, raising=False
    )
