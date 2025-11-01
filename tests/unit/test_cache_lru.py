"""Unit tests for LRU eviction behavior in cache tiers.

Tests cover:
- T062: LRU eviction from L1 to L2
- LRU ordering and move_to_end behavior
- Capacity enforcement and eviction triggers
"""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import SecretStr

from proxywhirl.cache_models import CacheEntry, CacheTierConfig
from proxywhirl.cache_tiers import MemoryCacheTier, TierType


@pytest.fixture
def tier_config() -> CacheTierConfig:
    """Create tier config with small capacity for testing eviction."""
    return CacheTierConfig(
        enabled=True,
        max_entries=3,  # Small capacity to trigger eviction easily
        eviction_policy="lru",
    )


@pytest.fixture
def memory_tier(tier_config: CacheTierConfig) -> MemoryCacheTier:
    """Create memory cache tier."""
    return MemoryCacheTier(config=tier_config, tier_type=TierType.L1_MEMORY)


def _create_entry(key: str, proxy_url: str) -> CacheEntry:
    """Helper to create cache entry."""
    return CacheEntry(
        key=key,
        proxy_url=proxy_url,
        username=SecretStr("user"),
        password=SecretStr("pass"),
        source="test",
        fetch_time=datetime.now(timezone.utc),
        last_accessed=datetime.now(timezone.utc),
        access_count=0,
        ttl_seconds=3600,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )


class TestLRUEviction:
    """Test LRU eviction from L1 memory tier.
    
    T062: Unit test for LRU eviction from L1 to L2.
    """

    def test_lru_eviction_removes_oldest(self, memory_tier: MemoryCacheTier) -> None:
        """Test that LRU eviction removes the least recently used entry."""
        # Add 3 entries (at capacity)
        entry1 = _create_entry("key1", "http://proxy1.com")
        entry2 = _create_entry("key2", "http://proxy2.com")
        entry3 = _create_entry("key3", "http://proxy3.com")

        memory_tier.put("key1", entry1)
        memory_tier.put("key2", entry2)
        memory_tier.put("key3", entry3)

        assert memory_tier.size() == 3

        # Add 4th entry - should evict key1 (oldest)
        entry4 = _create_entry("key4", "http://proxy4.com")
        memory_tier.put("key4", entry4)

        assert memory_tier.size() == 3
        assert memory_tier.get("key1") is None  # Evicted
        assert memory_tier.get("key2") is not None
        assert memory_tier.get("key3") is not None
        assert memory_tier.get("key4") is not None

    def test_lru_get_refreshes_position(self, memory_tier: MemoryCacheTier) -> None:
        """Test that accessing an entry moves it to the end (most recent)."""
        # Add 3 entries (at capacity)
        entry1 = _create_entry("key1", "http://proxy1.com")
        entry2 = _create_entry("key2", "http://proxy2.com")
        entry3 = _create_entry("key3", "http://proxy3.com")

        memory_tier.put("key1", entry1)
        memory_tier.put("key2", entry2)
        memory_tier.put("key3", entry3)

        # Access key1 to make it most recent
        memory_tier.get("key1")

        # Add 4th entry - should evict key2 (now oldest after key1 was accessed)
        entry4 = _create_entry("key4", "http://proxy4.com")
        memory_tier.put("key4", entry4)

        assert memory_tier.size() == 3
        assert memory_tier.get("key1") is not None  # Still present (was refreshed)
        assert memory_tier.get("key2") is None  # Evicted (oldest)
        assert memory_tier.get("key3") is not None
        assert memory_tier.get("key4") is not None

    def test_lru_put_existing_refreshes_position(self, memory_tier: MemoryCacheTier) -> None:
        """Test that updating an existing entry refreshes its LRU position."""
        # Add 3 entries (at capacity)
        entry1 = _create_entry("key1", "http://proxy1.com")
        entry2 = _create_entry("key2", "http://proxy2.com")
        entry3 = _create_entry("key3", "http://proxy3.com")

        memory_tier.put("key1", entry1)
        memory_tier.put("key2", entry2)
        memory_tier.put("key3", entry3)

        # Update key1 (should move to end)
        updated_entry1 = _create_entry("key1", "http://proxy1-updated.com")
        memory_tier.put("key1", updated_entry1)

        # Add 4th entry - should evict key2 (oldest)
        entry4 = _create_entry("key4", "http://proxy4.com")
        memory_tier.put("key4", entry4)

        assert memory_tier.size() == 3
        assert memory_tier.get("key1") is not None  # Still present (was updated)
        assert memory_tier.get("key2") is None  # Evicted
        assert memory_tier.get("key3") is not None
        assert memory_tier.get("key4") is not None

    def test_lru_eviction_fifo_ordering(self, memory_tier: MemoryCacheTier) -> None:
        """Test that eviction follows FIFO ordering for unaccessed entries."""
        # Add 3 entries in order
        for i in range(1, 4):
            entry = _create_entry(f"key{i}", f"http://proxy{i}.com")
            memory_tier.put(f"key{i}", entry)

        # Add 3 more entries - should evict in FIFO order (key1, key2, key3)
        for i in range(4, 7):
            entry = _create_entry(f"key{i}", f"http://proxy{i}.com")
            memory_tier.put(f"key{i}", entry)

        assert memory_tier.size() == 3
        # Only newest 3 should remain
        assert memory_tier.get("key1") is None
        assert memory_tier.get("key2") is None
        assert memory_tier.get("key3") is None
        assert memory_tier.get("key4") is not None
        assert memory_tier.get("key5") is not None
        assert memory_tier.get("key6") is not None

    def test_lru_no_eviction_under_capacity(self, memory_tier: MemoryCacheTier) -> None:
        """Test that no eviction occurs when under capacity."""
        # Add 2 entries (under capacity of 3)
        entry1 = _create_entry("key1", "http://proxy1.com")
        entry2 = _create_entry("key2", "http://proxy2.com")

        memory_tier.put("key1", entry1)
        memory_tier.put("key2", entry2)

        assert memory_tier.size() == 2
        assert memory_tier.get("key1") is not None
        assert memory_tier.get("key2") is not None

        # Add 3rd entry (at capacity but not over)
        entry3 = _create_entry("key3", "http://proxy3.com")
        memory_tier.put("key3", entry3)

        assert memory_tier.size() == 3
        # All entries still present
        assert memory_tier.get("key1") is not None
        assert memory_tier.get("key2") is not None
        assert memory_tier.get("key3") is not None

    def test_lru_unlimited_capacity(self) -> None:
        """Test that unlimited capacity (None) never evicts."""
        config = CacheTierConfig(
            enabled=True,
            max_entries=None,  # Unlimited
            eviction_policy="lru",
        )
        tier = MemoryCacheTier(config=config, tier_type=TierType.L1_MEMORY)

        # Add many entries
        for i in range(100):
            entry = _create_entry(f"key{i}", f"http://proxy{i}.com")
            tier.put(f"key{i}", entry)

        assert tier.size() == 100
        # All entries still present
        assert tier.get("key0") is not None
        assert tier.get("key50") is not None
        assert tier.get("key99") is not None
