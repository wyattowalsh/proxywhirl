"""Integration tests for multi-tier caching strategy.

Tests the complete multi-tier caching behavior including:
- Tier promotion on cache hits (L3→L2→L1)
- Tier demotion on eviction (L1→L2→L3)
- Read-through caching across tiers
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from pydantic import SecretStr

from proxywhirl.cache import CacheManager
from proxywhirl.cache_crypto import CredentialEncryptor
from proxywhirl.cache_models import CacheConfig, CacheEntry, CacheTierConfig, HealthStatus


def test_tier_promotion_on_hit(tmp_path: Path) -> None:
    """Test that cache hits promote entries from lower tiers to L1.

    Scenario:
    1. Store entry in L3 only
    2. Get entry (should be found in L3)
    3. Verify entry is now also in L1 and L2 (promoted)
    """
    encryptor = CredentialEncryptor()
    encryption_key = SecretStr(encryptor.key.decode("utf-8"))

    config = CacheConfig(
        l1_config=CacheTierConfig(enabled=True, max_entries=100),
        l2_config=CacheTierConfig(enabled=True, max_entries=500),
        l3_config=CacheTierConfig(enabled=True, max_entries=None),
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
    )

    manager = CacheManager(config)

    # Create entry
    now = datetime.now(timezone.utc)
    entry = CacheEntry(
        key="promote_test",
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

    # Store only in L3 (bypass L1 and L2)
    manager.l3_tier.put(entry.key, entry)

    # Verify not in L1 or L2 initially
    assert manager.l1_tier.get(entry.key) is None, "Entry should not be in L1 initially"
    assert manager.l2_tier.get(entry.key) is None, "Entry should not be in L2 initially"

    # Get entry through CacheManager (should trigger promotion)
    retrieved = manager.get(entry.key)
    assert retrieved is not None, "Entry should be retrieved from L3"
    assert retrieved.key == entry.key

    # Verify promotion to L1 and L2
    l1_entry = manager.l1_tier.get(entry.key)
    l2_entry = manager.l2_tier.get(entry.key)

    assert l1_entry is not None, "Entry should be promoted to L1"
    assert l2_entry is not None, "Entry should be promoted to L2"


def test_l1_eviction_to_l2(tmp_path: Path) -> None:
    """Test that memory eviction writes entries to disk (L2).

    Scenario:
    1. Fill L1 to capacity
    2. Add one more entry (triggers eviction)
    3. Verify evicted entry is in L2
    """
    encryptor = CredentialEncryptor()
    encryption_key = SecretStr(encryptor.key.decode("utf-8"))

    # Small L1 capacity to trigger eviction quickly
    config = CacheConfig(
        l1_config=CacheTierConfig(enabled=True, max_entries=3),
        l2_config=CacheTierConfig(enabled=True, max_entries=100),
        l3_config=CacheTierConfig(enabled=True, max_entries=None),
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
    )

    manager = CacheManager(config)
    now = datetime.now(timezone.utc)

    # Fill L1 to capacity (3 entries)
    entries = []
    for i in range(3):
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
        entries.append(entry)
        manager.put(entry.key, entry)

    # Verify L1 is at capacity
    assert manager.l1_tier.size() == 3, "L1 should be at capacity"

    # Add one more entry (should trigger eviction of oldest)
    eviction_trigger = CacheEntry(
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
    manager.put(eviction_trigger.key, eviction_trigger)

    # Verify L1 still at capacity (LRU eviction happened)
    assert manager.l1_tier.size() == 3, "L1 should still be at capacity"

    # Verify oldest entry (key_0) was evicted from L1 but exists in L2
    assert manager.l1_tier.get("key_0") is None, "Oldest entry should be evicted from L1"
    l2_entry = manager.l2_tier.get("key_0")
    assert l2_entry is not None, "Evicted entry should be in L2"
    assert l2_entry.key == "key_0"


def test_multi_tier_read_through(tmp_path: Path) -> None:
    """Test complete read-through behavior across all three tiers.

    Scenario:
    1. Store entry only in L3
    2. Clear L1 and L2
    3. Get entry (should read from L3 and promote to L1/L2)
    4. Subsequent gets should hit L1 (fastest tier)
    """
    encryptor = CredentialEncryptor()
    encryption_key = SecretStr(encryptor.key.decode("utf-8"))

    config = CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
    )

    manager = CacheManager(config)
    now = datetime.now(timezone.utc)

    entry = CacheEntry(
        key="readthrough_test",
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

    # Store in all tiers
    manager.put(entry.key, entry)

    # Clear L1 and L2 to simulate cold cache
    manager.l1_tier.clear()
    manager.l2_tier.clear()

    # First get: should read from L3 and promote
    first_get = manager.get(entry.key)
    assert first_get is not None, "Entry should be found in L3"

    # Verify promotion to L1
    assert manager.l1_tier.get(entry.key) is not None, "Entry should be promoted to L1"

    # Second get: should hit L1 (fast path)
    stats_before = manager.get_statistics()
    second_get = manager.get(entry.key)
    stats_after = manager.get_statistics()

    assert second_get is not None, "Entry should still be retrievable"
    # L1 hits should increase
    assert stats_after.l1_stats.hits > stats_before.l1_stats.hits, "L1 hits should increase"
