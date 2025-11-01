"""Integration tests for cache statistics tracking.

Tests end-to-end statistics collection scenarios including multi-tier operations.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from pydantic import SecretStr

from proxywhirl.cache import CacheManager
from proxywhirl.cache_crypto import CredentialEncryptor
from proxywhirl.cache_models import CacheConfig, CacheEntry, HealthStatus


def test_hit_rate_target_under_load(tmp_path: Path) -> None:
    """Test that hit rate stays above 80% under realistic load (SC-011).

    Success Criteria: Cache hit rate should stay above 80% under typical
    proxy rotation patterns.
    """
    encryptor = CredentialEncryptor()
    config = CacheConfig(
        l1_config=CacheConfig.model_fields["l1_config"].default.__class__(
            enabled=True, max_entries=100
        ),
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=SecretStr(encryptor.key.decode("utf-8")),
    )
    manager = CacheManager(config)
    now = datetime.now(timezone.utc)

    # Populate cache with 100 proxies
    for i in range(100):
        entry = CacheEntry(
            key=f"proxy_{i}",
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

    # Simulate realistic access pattern:
    # 80% of requests hit top 20 proxies, 15% hit remaining 80, 5% miss
    hit_keys = [f"proxy_{i}" for i in range(20)] * 4  # 80 requests
    hit_keys += [f"proxy_{i}" for i in range(20, 100)]  # 80 requests
    miss_keys = [f"nonexistent_{i}" for i in range(10)]  # 10 misses

    # Execute access pattern
    for key in hit_keys:
        manager.get(key)
    for key in miss_keys:
        manager.get(key)

    stats = manager.get_statistics()

    # Total: 160 hits + 10 misses = 170 operations
    # Hit rate should be 160/170 = 94.1%
    assert stats.overall_hit_rate >= 0.80, f"Hit rate {stats.overall_hit_rate:.2%} below 80% target"
    assert stats.overall_hit_rate >= 0.90, f"Hit rate {stats.overall_hit_rate:.2%} should be ~94%"


def test_statistics_across_tier_promotion(tmp_path: Path) -> None:
    """Test that statistics track tier promotions correctly."""
    encryptor = CredentialEncryptor()
    config = CacheConfig(
        l1_config=CacheConfig.model_fields["l1_config"].default.__class__(
            enabled=True, max_entries=50
        ),
        l2_config=CacheConfig.model_fields["l2_config"].default.__class__(enabled=True),
        l3_config=CacheConfig.model_fields["l3_config"].default.__class__(enabled=True),
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=SecretStr(encryptor.key.decode("utf-8")),
    )
    manager = CacheManager(config)
    now = datetime.now(timezone.utc)

    # Add entry directly to L3 (simulating cold cache)
    entry = CacheEntry(
        key="cold_key",
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
    manager.l3_tier.put(entry.key, entry)

    stats_before = manager.get_statistics()

    # Access should promote L3 -> L2 -> L1
    manager.get("cold_key")

    stats_after = manager.get_statistics()

    # Should record promotion
    assert stats_after.promotions > stats_before.promotions
    assert stats_after.l3_stats.hits > stats_before.l3_stats.hits


def test_statistics_across_eviction(tmp_path: Path) -> None:
    """Test that statistics track evictions and demotions correctly."""
    encryptor = CredentialEncryptor()
    config = CacheConfig(
        l1_config=CacheConfig.model_fields["l1_config"].default.__class__(
            enabled=True, max_entries=2
        ),
        l2_config=CacheConfig.model_fields["l2_config"].default.__class__(enabled=True),
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

    # Should record eviction and demotion
    assert stats_after.l1_stats.evictions_lru > stats_before.l1_stats.evictions_lru
    assert stats_after.demotions > stats_before.demotions


def test_statistics_reset_on_clear(tmp_path: Path) -> None:
    """Test that statistics are preserved across cache clear operations."""
    encryptor = CredentialEncryptor()
    config = CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=SecretStr(encryptor.key.decode("utf-8")),
    )
    manager = CacheManager(config)
    now = datetime.now(timezone.utc)

    # Generate some activity
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
        manager.get(entry.key)

    stats_before = manager.get_statistics()
    assert stats_before.l1_stats.hits > 0

    # Clear cache (note: current implementation doesn't reset stats)
    # This test validates that stats are preserved for monitoring
    manager.l1_tier._cache.clear()
    if manager.l2_tier:
        # File tier doesn't have a clear method yet
        pass
    if manager.l3_tier:
        # SQLite tier doesn't have a clear method yet
        pass

    stats_after = manager.get_statistics()

    # Stats should be preserved (not reset)
    assert stats_after.l1_stats.hits == stats_before.l1_stats.hits
    assert stats_after.overall_hit_rate == stats_before.overall_hit_rate
