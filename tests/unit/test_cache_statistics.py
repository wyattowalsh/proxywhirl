"""Unit tests for cache statistics tracking.

Tests statistics collection, aggregation, and metrics export to validate
operational monitoring capabilities.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from pydantic import SecretStr

from proxywhirl.cache import CacheManager
from proxywhirl.cache_crypto import CredentialEncryptor
from proxywhirl.cache_models import CacheConfig, CacheEntry, HealthStatus


class TestHitMissTracking:
    """Test hit/miss rate tracking across cache tiers."""

    def test_l1_hit_increments_counter(self, tmp_path: Path) -> None:
        """Test that L1 cache hits increment the L1 hit counter."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)

        # Add entry
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="test_key",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
            health_status=HealthStatus.HEALTHY,
        )
        manager.put(entry.key, entry)

        # Get entry (L1 hit)
        stats_before = manager.get_statistics()
        manager.get(entry.key)
        stats_after = manager.get_statistics()

        assert stats_after.l1_stats.hits == stats_before.l1_stats.hits + 1

    def test_cache_miss_increments_counter(self, tmp_path: Path) -> None:
        """Test that cache misses increment the miss counter."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)

        stats_before = manager.get_statistics()
        manager.get("nonexistent_key")
        stats_after = manager.get_statistics()

        total_misses_before = (
            stats_before.l1_stats.misses
            + stats_before.l2_stats.misses
            + stats_before.l3_stats.misses
        )
        total_misses_after = (
            stats_after.l1_stats.misses + stats_after.l2_stats.misses + stats_after.l3_stats.misses
        )

        assert total_misses_after > total_misses_before


class TestEvictionCounters:
    """Test eviction counters for different eviction reasons."""

    def test_lru_eviction_counter(self, tmp_path: Path) -> None:
        """Test that LRU evictions increment the LRU eviction counter."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l1_config=CacheConfig.model_fields["l1_config"].default.__class__(
                enabled=True, max_entries=2
            ),
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
        now = datetime.now(timezone.utc)

        # Fill L1 to capacity
        for i in range(2):
            entry = CacheEntry(
                key=f"key_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                username=None,
                password=None,
                source="test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
                health_status=HealthStatus.HEALTHY,
            )
            manager.put(entry.key, entry)

        stats_before = manager.get_statistics()

        # Add one more to trigger eviction
        entry = CacheEntry(
            key="key_evict",
            proxy_url="http://proxy_evict.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
            health_status=HealthStatus.HEALTHY,
        )
        manager.put(entry.key, entry)

        stats_after = manager.get_statistics()

        assert stats_after.l1_stats.evictions_lru > stats_before.l1_stats.evictions_lru

    def test_ttl_eviction_counter(self, tmp_path: Path) -> None:
        """Test that TTL-based evictions increment the TTL eviction counter."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
        now = datetime.now(timezone.utc)

        # Add expired entry
        entry = CacheEntry(
            key="expired_key",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now - timedelta(seconds=7200),
            last_accessed=now - timedelta(seconds=7200),
            ttl_seconds=3600,
            expires_at=now - timedelta(seconds=3600),  # Already expired
            health_status=HealthStatus.HEALTHY,
        )
        manager.l1_tier.put(entry.key, entry)

        stats_before = manager.get_statistics()

        # Try to get expired entry (should trigger TTL eviction)
        result = manager.get(entry.key)

        stats_after = manager.get_statistics()

        assert result is None, "Expired entry should not be returned"
        assert stats_after.l1_stats.evictions_ttl > stats_before.l1_stats.evictions_ttl


class TestOverallHitRate:
    """Test overall hit rate calculation."""

    def test_hit_rate_calculation(self, tmp_path: Path) -> None:
        """Test that overall hit rate is calculated correctly."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
        now = datetime.now(timezone.utc)

        # Add entries
        for i in range(5):
            entry = CacheEntry(
                key=f"key_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                username=None,
                password=None,
                source="test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
                health_status=HealthStatus.HEALTHY,
            )
            manager.put(entry.key, entry)

        # Generate hits (5 hits)
        for i in range(5):
            manager.get(f"key_{i}")

        # Generate misses (2 misses)
        manager.get("nonexistent_1")
        manager.get("nonexistent_2")

        stats = manager.get_statistics()

        # Hit rate should be 5/(5+2) = ~0.714
        assert 0.7 <= stats.overall_hit_rate <= 0.72


class TestMetricsExport:
    """Test metrics export format."""

    def test_to_metrics_dict_format(self, tmp_path: Path) -> None:
        """Test that statistics can be exported to metrics dictionary."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)

        stats = manager.get_statistics()
        metrics = stats.model_dump()

        # Verify structure
        assert "l1_stats" in metrics
        assert "l2_stats" in metrics
        assert "l3_stats" in metrics
        assert "promotions" in metrics
        assert "demotions" in metrics
        assert "overall_hit_rate" in metrics

        # Verify nested structure
        assert "hits" in metrics["l1_stats"]
        assert "misses" in metrics["l1_stats"]
        assert "hit_rate" in metrics["l1_stats"]
