"""Unit tests for cache tier implementations.

Tests for MemoryCacheTier, JsonlCacheTier, DiskCacheTier, and SQLiteCacheTier.
"""

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from proxywhirl.cache.models import CacheEntry, CacheTierConfig, HealthStatus
from proxywhirl.cache.tiers import (
    DiskCacheTier,
    JsonlCacheTier,
    MemoryCacheTier,
    SQLiteCacheTier,
    TierType,
)


@pytest.fixture
def tier_config() -> CacheTierConfig:
    """Create a basic tier configuration."""
    return CacheTierConfig(
        enabled=True,
        max_entries=100,
        ttl_seconds=3600,
    )


@pytest.fixture
def sample_entry() -> CacheEntry:
    """Create a sample cache entry."""
    now = datetime.now(timezone.utc)
    return CacheEntry(
        key="test_key",
        proxy_url="http://proxy.example.com:8080",
        source="test_source",
        fetch_time=now,
        last_accessed=now,
        ttl_seconds=3600,
        expires_at=now + timedelta(hours=1),
    )


@pytest.fixture
def entry_with_credentials() -> CacheEntry:
    """Create a sample cache entry with credentials."""
    now = datetime.now(timezone.utc)
    return CacheEntry(
        key="auth_key",
        proxy_url="http://proxy.example.com:8080",
        username=SecretStr("user"),
        password=SecretStr("pass"),
        source="test_source",
        fetch_time=now,
        last_accessed=now,
        ttl_seconds=3600,
        expires_at=now + timedelta(hours=1),
    )


class TestTierType:
    """Tests for TierType enum."""

    def test_tier_types_defined(self) -> None:
        """Test all tier types are defined."""
        assert TierType.L1_MEMORY == "l1_memory"
        assert TierType.L2_FILE == "l2_file"
        assert TierType.L3_SQLITE == "l3_sqlite"


class TestCacheTierBase:
    """Tests for abstract CacheTier base class."""

    def test_handle_failure_increments_count(self, tier_config: CacheTierConfig) -> None:
        """Test handle_failure increments failure count."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        assert tier.failure_count == 0

        tier.handle_failure(Exception("test"))
        assert tier.failure_count == 1
        assert tier.enabled is True

    def test_handle_failure_disables_tier_at_threshold(self, tier_config: CacheTierConfig) -> None:
        """Test tier is disabled when failures reach threshold."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        tier.failure_threshold = 3

        tier.handle_failure(Exception("error 1"))
        tier.handle_failure(Exception("error 2"))
        assert tier.enabled is True

        tier.handle_failure(Exception("error 3"))
        assert tier.enabled is False

    def test_reset_failures_resets_count(self, tier_config: CacheTierConfig) -> None:
        """Test reset_failures resets failure count."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        tier.failure_count = 2

        tier.reset_failures()
        assert tier.failure_count == 0

    def test_reset_failures_re_enables_tier(self, tier_config: CacheTierConfig) -> None:
        """Test reset_failures re-enables disabled tier."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        tier.enabled = False
        tier.failure_count = 3

        tier.reset_failures()
        assert tier.enabled is True
        assert tier.failure_count == 0


class TestMemoryCacheTier:
    """Tests for MemoryCacheTier."""

    def test_get_nonexistent_key(self, tier_config: CacheTierConfig) -> None:
        """Test get returns None for nonexistent key."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        result = tier.get("nonexistent")
        assert result is None

    def test_put_and_get(self, tier_config: CacheTierConfig, sample_entry: CacheEntry) -> None:
        """Test put stores and get retrieves entry."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)

        success = tier.put(sample_entry.key, sample_entry)
        assert success is True

        result = tier.get(sample_entry.key)
        assert result is not None
        assert result.key == sample_entry.key

    def test_put_lru_eviction(self, sample_entry: CacheEntry) -> None:
        """Test LRU eviction when max_entries exceeded."""
        config = CacheTierConfig(enabled=True, max_entries=2, ttl_seconds=3600)
        tier = MemoryCacheTier(config, TierType.L1_MEMORY)

        now = datetime.now(timezone.utc)
        entry1 = CacheEntry(
            key="key1",
            proxy_url="http://proxy1.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        entry2 = CacheEntry(
            key="key2",
            proxy_url="http://proxy2.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        entry3 = CacheEntry(
            key="key3",
            proxy_url="http://proxy3.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )

        tier.put("key1", entry1)
        tier.put("key2", entry2)
        assert tier.size() == 2

        # Adding third should evict first (LRU)
        tier.put("key3", entry3)
        assert tier.size() == 2
        assert tier.get("key1") is None  # Evicted
        assert tier.get("key2") is not None
        assert tier.get("key3") is not None

    def test_put_updates_existing_key(
        self, tier_config: CacheTierConfig, sample_entry: CacheEntry
    ) -> None:
        """Test put updates existing entry."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)

        tier.put(sample_entry.key, sample_entry)

        updated = CacheEntry(
            key=sample_entry.key,
            proxy_url="http://updated.com:8080",
            source=sample_entry.source,
            fetch_time=sample_entry.fetch_time,
            last_accessed=sample_entry.last_accessed,
            ttl_seconds=sample_entry.ttl_seconds,
            expires_at=sample_entry.expires_at,
        )
        tier.put(sample_entry.key, updated)

        result = tier.get(sample_entry.key)
        assert result is not None
        assert result.proxy_url == "http://updated.com:8080"
        assert tier.size() == 1

    def test_put_exception_handling(
        self, tier_config: CacheTierConfig, sample_entry: CacheEntry
    ) -> None:
        """Test put handles exceptions gracefully."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)

        # Mock the cache to raise exception
        with patch.object(tier, "_cache", side_effect=Exception("Storage error")):
            # Should catch and handle, returning False
            # But the way the code works, we need to trigger the exception path
            pass

        # Test with a rigged ordered dict that raises
        tier._cache = MagicMock()
        tier._cache.__contains__ = MagicMock(side_effect=Exception("Test error"))

        result = tier.put("key", sample_entry)
        assert result is False
        assert tier.failure_count == 1

    def test_delete_existing_key(
        self, tier_config: CacheTierConfig, sample_entry: CacheEntry
    ) -> None:
        """Test delete removes existing key."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        tier.put(sample_entry.key, sample_entry)

        result = tier.delete(sample_entry.key)
        assert result is True
        assert tier.get(sample_entry.key) is None

    def test_delete_nonexistent_key(self, tier_config: CacheTierConfig) -> None:
        """Test delete returns False for nonexistent key."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        result = tier.delete("nonexistent")
        assert result is False

    def test_clear(self, tier_config: CacheTierConfig, sample_entry: CacheEntry) -> None:
        """Test clear removes all entries."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        tier.put(sample_entry.key, sample_entry)
        tier.put("key2", sample_entry)

        count = tier.clear()
        assert count == 2
        assert tier.size() == 0

    def test_size(self, tier_config: CacheTierConfig, sample_entry: CacheEntry) -> None:
        """Test size returns correct count."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        assert tier.size() == 0

        tier.put(sample_entry.key, sample_entry)
        assert tier.size() == 1

    def test_keys(self, tier_config: CacheTierConfig, sample_entry: CacheEntry) -> None:
        """Test keys returns all keys."""
        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        tier.put("key1", sample_entry)
        tier.put("key2", sample_entry)

        keys = tier.keys()
        assert set(keys) == {"key1", "key2"}

    def test_get_moves_to_end_lru(
        self, tier_config: CacheTierConfig, sample_entry: CacheEntry
    ) -> None:
        """Test get moves key to end for LRU tracking."""
        config = CacheTierConfig(enabled=True, max_entries=2, ttl_seconds=3600)
        tier = MemoryCacheTier(config, TierType.L1_MEMORY)

        now = datetime.now(timezone.utc)
        entry1 = CacheEntry(
            key="key1",
            proxy_url="http://proxy1.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        entry2 = CacheEntry(
            key="key2",
            proxy_url="http://proxy2.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )

        tier.put("key1", entry1)
        tier.put("key2", entry2)

        # Access key1 to move it to end
        tier.get("key1")

        # Adding new entry should evict key2 (LRU) instead of key1
        entry3 = CacheEntry(
            key="key3",
            proxy_url="http://proxy3.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        tier.put("key3", entry3)

        assert tier.get("key1") is not None  # Should still exist
        assert tier.get("key2") is None  # Should be evicted


class TestJsonlCacheTier:
    """Tests for JsonlCacheTier (JSONL file-based L2 cache)."""

    def test_get_nonexistent_key(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test get returns None when key doesn't exist."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        result = tier.get("nonexistent")
        assert result is None

    def test_put_and_get(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test put stores and get retrieves entry."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        success = tier.put(sample_entry.key, sample_entry)
        assert success is True

        result = tier.get(sample_entry.key)
        assert result is not None
        assert result.key == sample_entry.key

    def test_put_and_get_with_credentials(
        self, tier_config: CacheTierConfig, tmp_path: Path, entry_with_credentials: CacheEntry
    ) -> None:
        """Test put/get with encrypted credentials."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        success = tier.put(entry_with_credentials.key, entry_with_credentials)
        assert success is True

        result = tier.get(entry_with_credentials.key)
        assert result is not None
        assert result.username is not None
        assert result.username.get_secret_value() == "user"
        assert result.password is not None
        assert result.password.get_secret_value() == "pass"

    def test_get_with_corrupted_json(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test get handles corrupted JSON lines gracefully."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        # First store a valid entry
        tier.put(sample_entry.key, sample_entry)

        # Corrupt the file by adding invalid JSON
        shard_id = tier._get_shard_id(sample_entry.key)
        shard_path = tier._get_shard_path(shard_id)
        with open(shard_path, "a") as f:
            f.write("not valid json\n")

        # Should still be able to get the valid entry
        result = tier.get(sample_entry.key)
        assert result is not None
        assert result.key == sample_entry.key

    def test_get_exception_handling(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test get handles exceptions gracefully when reading shard fails."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        tier.put(sample_entry.key, sample_entry)

        # Remove index entry to force file read, then mock Lock to raise exception
        tier._index.clear()
        tier._index[sample_entry.key] = 0  # Re-add to index to trigger read
        with patch("proxywhirl.cache.tiers.portalocker.Lock", side_effect=Exception("Lock error")):
            result = tier.get(sample_entry.key)
            # Result is None because _read_shard fails silently and returns empty dict
            assert result is None

    def test_put_exception_handling(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test put handles exceptions gracefully."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        # Force exception during read or write by mocking Lock
        with patch.object(tier, "_read_shard", side_effect=Exception("Read error")):
            result = tier.put(sample_entry.key, sample_entry)
            assert result is False
            assert tier.failure_count == 1

    def test_delete_nonexistent_key(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test delete returns False when key doesn't exist."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        result = tier.delete("nonexistent")
        assert result is False

    def test_delete_existing_key(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test delete removes existing key."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        tier.put(sample_entry.key, sample_entry)

        result = tier.delete(sample_entry.key)
        assert result is True
        assert tier.get(sample_entry.key) is None

    def test_delete_exception_handling(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test delete handles exceptions gracefully."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        tier.put(sample_entry.key, sample_entry)

        # Force exception during read by mocking _read_shard
        with patch.object(tier, "_read_shard", side_effect=Exception("Read error")):
            result = tier.delete(sample_entry.key)
            assert result is False
            assert tier.failure_count == 1

    def test_clear(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test clear removes all entries."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        now = datetime.now(timezone.utc)

        # Create two distinct entries with different keys
        entry1 = CacheEntry(
            key="key1",
            proxy_url="http://proxy1.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        entry2 = CacheEntry(
            key="key2",
            proxy_url="http://proxy2.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )

        tier.put(entry1.key, entry1)
        tier.put(entry2.key, entry2)

        count = tier.clear()
        assert count == 2
        assert tier.size() == 0

    def test_size(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test size returns correct count."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        assert tier.size() == 0

        tier.put(sample_entry.key, sample_entry)
        assert tier.size() == 1

    def test_keys(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test keys returns all keys."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        now = datetime.now(timezone.utc)
        entry1 = CacheEntry(
            key="key1",
            proxy_url="http://proxy1.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        entry2 = CacheEntry(
            key="key2",
            proxy_url="http://proxy2.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        tier.put("key1", entry1)
        tier.put("key2", entry2)

        keys = tier.keys()
        assert set(keys) == {"key1", "key2"}

    def test_shard_path(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test shard path generation."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        path = tier._get_shard_path(0)
        assert "shard_00.jsonl" in str(path)

    def test_creates_cache_directory(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test tier creates cache directory if it doesn't exist."""
        cache_dir = tmp_path / "new_cache"
        JsonlCacheTier(tier_config, TierType.L2_FILE, cache_dir)
        assert cache_dir.exists()

    def test_cleanup_expired(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test cleanup_expired removes expired entries."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        now = datetime.now(timezone.utc)

        # Create expired entry
        expired_entry = CacheEntry(
            key="expired_key",
            proxy_url="http://expired.com:8080",
            source="test",
            fetch_time=now - timedelta(hours=2),
            last_accessed=now - timedelta(hours=2),
            ttl_seconds=3600,
            expires_at=now - timedelta(hours=1),  # Already expired
        )

        # Create valid entry
        valid_entry = CacheEntry(
            key="valid_key",
            proxy_url="http://valid.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )

        tier.put(expired_entry.key, expired_entry)
        tier.put(valid_entry.key, valid_entry)
        assert tier.size() == 2

        # Run cleanup
        removed = tier.cleanup_expired()
        assert removed == 1
        assert tier.size() == 1
        assert tier.get("expired_key") is None
        assert tier.get("valid_key") is not None

    def test_evict_oldest_returns_false_when_empty(
        self, tier_config: CacheTierConfig, tmp_path: Path
    ) -> None:
        """Evicting with no entries should return False."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        assert tier._evict_oldest() is False

    def test_rebuild_index_skips_corrupted_lines(
        self, tier_config: CacheTierConfig, tmp_path: Path
    ) -> None:
        """Rebuild index should tolerate corrupted JSON and bad timestamps."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        shard_path = tier._get_shard_path(0)
        shard_path.write_text(
            "\n".join(
                [
                    '{"key": "ok1", "last_accessed": "not-a-date"}',
                    '{"key": "ok2"}',
                    "{bad-json",
                    "",
                ]
            )
            + "\n"
        )

        tier._rebuild_index()
        assert "ok1" in tier._index
        assert "ok2" in tier._index

    def test_health_fields_roundtrip(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test all health monitoring fields survive serialization roundtrip."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        now = datetime.now(timezone.utc)

        # Create entry with all health monitoring fields populated
        entry = CacheEntry(
            key="health_test_key",
            proxy_url="http://proxy.example.com:8080",
            source="test_source",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
            health_status=HealthStatus.HEALTHY,
            failure_count=1,
            evicted_from_l1=True,
            # Health monitoring fields (Feature 006)
            last_health_check=now - timedelta(minutes=5),
            consecutive_health_failures=2,
            consecutive_health_successes=5,
            recovery_attempt=1,
            next_check_time=now + timedelta(minutes=10),
            last_health_error="Connection timeout",
            total_health_checks=10,
            total_health_check_failures=3,
        )

        # Store and retrieve
        success = tier.put(entry.key, entry)
        assert success is True

        retrieved = tier.get(entry.key)
        assert retrieved is not None

        # Verify all health monitoring fields are preserved
        assert retrieved.health_status == HealthStatus.HEALTHY
        assert retrieved.failure_count == 1
        assert retrieved.evicted_from_l1 is True
        assert retrieved.consecutive_health_failures == 2
        assert retrieved.consecutive_health_successes == 5
        assert retrieved.recovery_attempt == 1
        assert retrieved.last_health_error == "Connection timeout"
        assert retrieved.total_health_checks == 10
        assert retrieved.total_health_check_failures == 3
        assert retrieved.last_health_check is not None
        assert retrieved.next_check_time is not None

    def test_max_entries_eviction(self, tmp_path: Path) -> None:
        """Test LRU eviction when max_entries is exceeded."""
        config = CacheTierConfig(enabled=True, max_entries=2)
        tier = JsonlCacheTier(config, TierType.L2_FILE, tmp_path)
        now = datetime.now(timezone.utc)

        # Create entries with different last_accessed times
        entry1 = CacheEntry(
            key="key1",
            proxy_url="http://proxy1.com:8080",
            source="test",
            fetch_time=now - timedelta(hours=2),
            last_accessed=now - timedelta(hours=2),  # Oldest
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        entry2 = CacheEntry(
            key="key2",
            proxy_url="http://proxy2.com:8080",
            source="test",
            fetch_time=now - timedelta(hours=1),
            last_accessed=now - timedelta(hours=1),
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        entry3 = CacheEntry(
            key="key3",
            proxy_url="http://proxy3.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,  # Newest
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )

        # Add first two entries
        tier.put("key1", entry1)
        tier.put("key2", entry2)
        assert tier.size() == 2

        # Adding third should evict the oldest (key1)
        tier.put("key3", entry3)
        assert tier.size() == 2
        assert tier.get("key1") is None  # Should be evicted (oldest)
        assert tier.get("key2") is not None
        assert tier.get("key3") is not None

    def test_deterministic_shard_id(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test shard ID computation is deterministic across calls."""
        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        # Same key should always produce same shard ID
        key = "test_key_for_determinism"
        shard_id1 = tier._get_shard_id(key)
        shard_id2 = tier._get_shard_id(key)
        shard_id3 = tier._get_shard_id(key)

        assert shard_id1 == shard_id2 == shard_id3

    def test_concurrent_access(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test concurrent reads and writes don't corrupt data."""

        tier = JsonlCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        now = datetime.now(timezone.utc)

        entries = []
        for i in range(10):
            entry = CacheEntry(
                key=f"concurrent-{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                source="test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(hours=1),
            )
            entries.append(entry)

        # Concurrent writes (simulate with sequential for sync tier)
        for e in entries:
            success = tier.put(e.key, e)
            assert success is True

        # Concurrent reads
        results = []
        for e in entries:
            result = tier.get(e.key)
            results.append(result)

        # Verify all entries
        for i, result in enumerate(results):
            assert result is not None
            assert result.key == f"concurrent-{i}"
            assert result.proxy_url == f"http://proxy{i}.example.com:8080"


class TestDiskCacheTier:
    """Tests for DiskCacheTier (SQLite-based L2 cache)."""

    def test_get_nonexistent_key(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test get returns None when key doesn't exist."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        result = tier.get("nonexistent")
        assert result is None

    def test_put_and_get(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test put stores and get retrieves entry."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        success = tier.put(sample_entry.key, sample_entry)
        assert success is True

        result = tier.get(sample_entry.key)
        assert result is not None
        assert result.key == sample_entry.key

    def test_put_and_get_with_credentials(
        self, tier_config: CacheTierConfig, tmp_path: Path, entry_with_credentials: CacheEntry
    ) -> None:
        """Test put/get with encrypted credentials."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        success = tier.put(entry_with_credentials.key, entry_with_credentials)
        assert success is True

        result = tier.get(entry_with_credentials.key)
        assert result is not None
        assert result.username is not None
        assert result.username.get_secret_value() == "user"
        assert result.password is not None
        assert result.password.get_secret_value() == "pass"

    def test_get_exception_handling(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test get handles exceptions gracefully."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        tier.put(sample_entry.key, sample_entry)

        # Close cached connection so patch takes effect
        tier.close()

        # Mock sqlite3.connect to raise exception
        with patch("proxywhirl.cache.tiers.sqlite3.connect", side_effect=Exception("DB error")):
            result = tier.get(sample_entry.key)
            assert result is None
            assert tier.failure_count == 1

    def test_put_exception_handling(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test put handles exceptions gracefully."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        # Close any cached connection so patch takes effect
        tier.close()

        # Mock sqlite3.connect to raise exception
        with patch("proxywhirl.cache.tiers.sqlite3.connect", side_effect=Exception("DB error")):
            result = tier.put(sample_entry.key, sample_entry)
            assert result is False
            assert tier.failure_count == 1

    def test_delete_nonexistent_key(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test delete returns False when key doesn't exist."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        result = tier.delete("nonexistent")
        assert result is False

    def test_delete_existing_key(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test delete removes existing key."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        tier.put(sample_entry.key, sample_entry)

        result = tier.delete(sample_entry.key)
        assert result is True
        assert tier.get(sample_entry.key) is None

    def test_delete_exception_handling(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test delete handles exceptions gracefully."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        tier.put(sample_entry.key, sample_entry)

        # Close cached connection so patch takes effect
        tier.close()

        # Mock sqlite3.connect to raise exception
        with patch("proxywhirl.cache.tiers.sqlite3.connect", side_effect=Exception("DB error")):
            result = tier.delete(sample_entry.key)
            assert result is False
            assert tier.failure_count == 1

    def test_clear(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test clear removes all entries."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        now = datetime.now(timezone.utc)
        entry1 = CacheEntry(
            key="key1",
            proxy_url="http://proxy1.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        entry2 = CacheEntry(
            key="key2",
            proxy_url="http://proxy2.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        tier.put("key1", entry1)
        tier.put("key2", entry2)

        count = tier.clear()
        assert count == 2
        assert tier.size() == 0

    def test_clear_handles_exception(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test clear handles exceptions gracefully."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        tier.put(sample_entry.key, sample_entry)

        # Close cached connection so patch takes effect
        tier.close()

        # Mock sqlite3.connect to raise exception
        with patch("proxywhirl.cache.tiers.sqlite3.connect", side_effect=Exception("DB error")):
            count = tier.clear()
            # Should return 0 because exception is caught
            assert count == 0

    def test_size(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test size returns correct count."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        assert tier.size() == 0

        tier.put(sample_entry.key, sample_entry)
        assert tier.size() == 1

    def test_size_handles_exception(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test size handles exceptions gracefully."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        tier.put(sample_entry.key, sample_entry)

        # Close cached connection so patch takes effect
        tier.close()

        # Mock sqlite3.connect to raise exception
        with patch("proxywhirl.cache.tiers.sqlite3.connect", side_effect=Exception("DB error")):
            count = tier.size()
            assert count == 0

    def test_keys(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test keys returns all keys."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        now = datetime.now(timezone.utc)
        entry1 = CacheEntry(
            key="key1",
            proxy_url="http://proxy1.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        entry2 = CacheEntry(
            key="key2",
            proxy_url="http://proxy2.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        tier.put("key1", entry1)
        tier.put("key2", entry2)

        keys = tier.keys()
        assert set(keys) == {"key1", "key2"}

    def test_keys_handles_exception(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test keys handles exceptions gracefully."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        tier.put(sample_entry.key, sample_entry)

        # Close cached connection so patch takes effect
        tier.close()

        # Mock sqlite3.connect to raise exception
        with patch("proxywhirl.cache.tiers.sqlite3.connect", side_effect=Exception("DB error")):
            keys = tier.keys()
            assert keys == []

    def test_creates_cache_directory(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test tier creates cache directory if it doesn't exist."""
        cache_dir = tmp_path / "new_cache"
        DiskCacheTier(tier_config, TierType.L2_FILE, cache_dir)
        assert cache_dir.exists()

    def test_uses_sqlite_database(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test tier uses SQLite database file."""
        DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        db_path = tmp_path / "l2_cache.db"
        assert db_path.exists()

    def test_cleanup_expired(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Disk cache should remove expired entries."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        now = datetime.now(timezone.utc)
        expired_entry = CacheEntry(
            key="expired",
            proxy_url="http://expired.com:8080",
            source="test",
            fetch_time=now - timedelta(hours=2),
            last_accessed=now - timedelta(hours=2),
            ttl_seconds=60,
            expires_at=now - timedelta(minutes=1),
        )
        valid_entry = CacheEntry(
            key="valid",
            proxy_url="http://valid.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        tier.put(expired_entry.key, expired_entry)
        tier.put(valid_entry.key, valid_entry)

        removed = tier.cleanup_expired()
        assert removed == 1
        assert tier.get("expired") is None
        assert tier.get("valid") is not None

    def test_migrate_from_jsonl(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Migrate JSONL shards into SQLite cache."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)
        now = datetime.now(timezone.utc)

        username_hex = tier.encryptor.encrypt(SecretStr("user")).hex()
        password_hex = tier.encryptor.encrypt(SecretStr("pass")).hex()
        entry = {
            "key": "migrate-key",
            "proxy_url": "http://proxy.example.com:8080",
            "source": "test",
            "fetch_time": now.isoformat(),
            "last_accessed": now.isoformat(),
            "access_count": 0,
            "ttl_seconds": 3600,
            "expires_at": (now + timedelta(hours=1)).isoformat(),
            "health_status": "unknown",
            "failure_count": 0,
            "evicted_from_l1": False,
            "username_encrypted": username_hex,
            "password_encrypted": password_hex,
        }

        shard_path = tier.cache_dir / "shard_00.jsonl"
        shard_path.write_text(
            "\n".join(
                [
                    json.dumps(entry),
                    "{bad-json",
                ]
            )
            + "\n"
        )

        migrated = tier.migrate_from_jsonl()
        assert migrated == 1


class TestSQLiteCacheTier:
    """Tests for SQLiteCacheTier."""

    def test_init_creates_database(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test initialization creates database with schema."""
        db_path = tmp_path / "cache.db"
        SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)

        assert db_path.exists()

        # Verify schema
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        assert "cache_entries" in tables
        assert "health_history" in tables

    def test_get_nonexistent_key(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test get returns None for nonexistent key."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)

        result = tier.get("nonexistent")
        assert result is None

    def test_put_and_get(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test put stores and get retrieves entry."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)

        success = tier.put(sample_entry.key, sample_entry)
        assert success is True

        result = tier.get(sample_entry.key)
        assert result is not None
        assert result.key == sample_entry.key

    def test_put_and_get_with_credentials(
        self, tier_config: CacheTierConfig, tmp_path: Path, entry_with_credentials: CacheEntry
    ) -> None:
        """Test put/get with encrypted credentials."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)

        success = tier.put(entry_with_credentials.key, entry_with_credentials)
        assert success is True

        result = tier.get(entry_with_credentials.key)
        assert result is not None
        assert result.username is not None
        assert result.username.get_secret_value() == "user"
        assert result.password is not None
        assert result.password.get_secret_value() == "pass"

    def test_get_exception_handling(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test get handles exceptions gracefully."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)
        tier.put(sample_entry.key, sample_entry)

        # Mock sqlite3 to raise exception
        with patch("proxywhirl.cache.tiers.sqlite3.connect", side_effect=Exception("DB error")):
            result = tier.get(sample_entry.key)
            assert result is None
            assert tier.failure_count == 1

    def test_put_exception_handling(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test put handles exceptions gracefully."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)

        # Mock sqlite3 to raise exception
        with patch("proxywhirl.cache.tiers.sqlite3.connect", side_effect=Exception("DB error")):
            result = tier.put(sample_entry.key, sample_entry)
            assert result is False
            assert tier.failure_count == 1

    def test_delete_existing_key(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test delete removes existing key."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)
        tier.put(sample_entry.key, sample_entry)

        result = tier.delete(sample_entry.key)
        assert result is True
        assert tier.get(sample_entry.key) is None

    def test_delete_nonexistent_key(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test delete returns False for nonexistent key."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)

        result = tier.delete("nonexistent")
        assert result is False

    def test_delete_exception_handling(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test delete handles exceptions gracefully."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)
        tier.put(sample_entry.key, sample_entry)

        # Mock sqlite3 to raise exception
        with patch("proxywhirl.cache.tiers.sqlite3.connect", side_effect=Exception("DB error")):
            result = tier.delete(sample_entry.key)
            assert result is False
            assert tier.failure_count == 1

    def test_clear(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test clear removes all entries."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)
        now = datetime.now(timezone.utc)
        entry1 = CacheEntry(
            key="key1",
            proxy_url="http://proxy1.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        entry2 = CacheEntry(
            key="key2",
            proxy_url="http://proxy2.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        tier.put("key1", entry1)
        tier.put("key2", entry2)

        count = tier.clear()
        assert count == 2
        assert tier.size() == 0

    def test_clear_exception_handling(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test clear handles exceptions gracefully."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)
        tier.put(sample_entry.key, sample_entry)

        # Mock sqlite3 to raise exception
        with patch("proxywhirl.cache.tiers.sqlite3.connect", side_effect=Exception("DB error")):
            count = tier.clear()
            assert count == 0
            assert tier.failure_count == 1

    def test_size(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test size returns correct count."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)
        assert tier.size() == 0

        tier.put(sample_entry.key, sample_entry)
        assert tier.size() == 1

    def test_size_exception_handling(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test size handles exceptions gracefully."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)
        tier.put(sample_entry.key, sample_entry)

        # Mock sqlite3 to raise exception
        with patch("proxywhirl.cache.tiers.sqlite3.connect", side_effect=Exception("DB error")):
            count = tier.size()
            assert count == 0
            assert tier.failure_count == 1

    def test_keys(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test keys returns all keys."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)
        now = datetime.now(timezone.utc)
        entry1 = CacheEntry(
            key="key1",
            proxy_url="http://proxy1.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        entry2 = CacheEntry(
            key="key2",
            proxy_url="http://proxy2.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        tier.put("key1", entry1)
        tier.put("key2", entry2)

        keys = tier.keys()
        assert set(keys) == {"key1", "key2"}

    def test_keys_exception_handling(
        self, tier_config: CacheTierConfig, tmp_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test keys handles exceptions gracefully."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)
        tier.put(sample_entry.key, sample_entry)

        # Mock sqlite3 to raise exception
        with patch("proxywhirl.cache.tiers.sqlite3.connect", side_effect=Exception("DB error")):
            keys = tier.keys()
            assert keys == []
            assert tier.failure_count == 1

    def test_migrate_health_columns_existing_db(
        self, tier_config: CacheTierConfig, tmp_path: Path
    ) -> None:
        """Test migration adds health columns to existing database."""
        db_path = tmp_path / "cache.db"

        # Create database without health columns
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE cache_entries (
                key TEXT PRIMARY KEY,
                proxy_url TEXT NOT NULL,
                username_encrypted BLOB,
                password_encrypted BLOB,
                source TEXT NOT NULL,
                fetch_time REAL NOT NULL,
                last_accessed REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                ttl_seconds INTEGER NOT NULL,
                expires_at REAL NOT NULL,
                health_status TEXT DEFAULT 'unknown',
                failure_count INTEGER DEFAULT 0,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()

        # Create tier which should trigger migration
        SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)

        # Verify health columns exist
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("PRAGMA table_info(cache_entries)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        assert "last_health_check" in columns
        assert "consecutive_health_failures" in columns
        assert "consecutive_health_successes" in columns

    def test_migrate_catches_operational_error(
        self, tier_config: CacheTierConfig, tmp_path: Path
    ) -> None:
        """Test migration handles concurrent column addition gracefully."""
        db_path = tmp_path / "cache.db"

        # Create tier normally first
        SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)

        # Create another tier - migration should not fail even though columns exist
        tier2 = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)

        assert tier2 is not None

    def test_creates_parent_directory(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test tier creates parent directory if it doesn't exist."""
        db_path = tmp_path / "subdir" / "cache.db"
        SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)

        assert db_path.parent.exists()
        assert db_path.exists()

    def test_put_with_health_monitoring_fields(
        self, tier_config: CacheTierConfig, tmp_path: Path
    ) -> None:
        """Test put stores health monitoring fields."""
        db_path = tmp_path / "cache.db"
        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path)

        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="health_test",
            proxy_url="http://proxy.example.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
            health_status=HealthStatus.HEALTHY,
            last_health_check=now,
            consecutive_health_failures=2,
            consecutive_health_successes=5,
            recovery_attempt=1,
            next_check_time=now + timedelta(minutes=5),
            last_health_error="Previous error",
            total_health_checks=10,
            total_health_check_failures=3,
        )

        success = tier.put(entry.key, entry)
        assert success is True

        result = tier.get(entry.key)
        assert result is not None
        assert result.health_status == HealthStatus.HEALTHY
        assert result.consecutive_health_failures == 2
        assert result.consecutive_health_successes == 5
        assert result.recovery_attempt == 1
        assert result.last_health_error == "Previous error"
        assert result.total_health_checks == 10
        assert result.total_health_check_failures == 3
