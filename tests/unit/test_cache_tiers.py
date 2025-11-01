"""Unit tests for cache tier implementations.

Tests the three cache tier implementations:
- MemoryCacheTier (L1): In-memory OrderedDict with LRU
- FileCacheTier (L2): JSONL files with portalocker + encryption
- SQLiteCacheTier (L3): SQLite database with encrypted credentials
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from proxywhirl.cache_models import CacheEntry, CacheTierConfig, HealthStatus
from proxywhirl.cache_tiers import TierType


class TestMemoryCacheTier:
    """Test MemoryCacheTier (L1 in-memory cache with LRU)."""

    @pytest.fixture
    def tier_config(self) -> CacheTierConfig:
        """Fixture for tier configuration."""
        return CacheTierConfig(enabled=True, max_entries=3, eviction_policy="lru")

    @pytest.fixture
    def sample_entry(self) -> CacheEntry:
        """Fixture for a sample cache entry."""
        now = datetime.now(timezone.utc)
        return CacheEntry(
            key="test_key_1",
            proxy_url="http://proxy1.example.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
            health_status=HealthStatus.HEALTHY,
        )

    def test_memory_tier_put_and_get(self, tier_config: CacheTierConfig, sample_entry: CacheEntry) -> None:
        """Test basic put and get operations."""
        # Import here to test that implementation exists
        from proxywhirl.cache_tiers import MemoryCacheTier

        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)

        # Put entry
        result = tier.put(sample_entry.key, sample_entry)
        assert result is True, "Put should succeed"

        # Get entry
        retrieved = tier.get(sample_entry.key)
        assert retrieved is not None, "Entry should be retrievable"
        assert retrieved.key == sample_entry.key
        assert retrieved.proxy_url == sample_entry.proxy_url

    def test_memory_tier_get_nonexistent(self, tier_config: CacheTierConfig) -> None:
        """Test getting non-existent key returns None."""
        from proxywhirl.cache_tiers import MemoryCacheTier

        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        result = tier.get("nonexistent_key")
        assert result is None, "Non-existent key should return None"

    def test_memory_tier_delete(self, tier_config: CacheTierConfig, sample_entry: CacheEntry) -> None:
        """Test delete operation."""
        from proxywhirl.cache_tiers import MemoryCacheTier

        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)

        # Put then delete
        tier.put(sample_entry.key, sample_entry)
        result = tier.delete(sample_entry.key)
        assert result is True, "Delete should succeed"

        # Verify deleted
        retrieved = tier.get(sample_entry.key)
        assert retrieved is None, "Deleted entry should not be retrievable"

    def test_memory_tier_delete_nonexistent(self, tier_config: CacheTierConfig) -> None:
        """Test deleting non-existent key returns False."""
        from proxywhirl.cache_tiers import MemoryCacheTier

        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        result = tier.delete("nonexistent_key")
        assert result is False, "Deleting non-existent key should return False"

    def test_memory_tier_clear(self, tier_config: CacheTierConfig, sample_entry: CacheEntry) -> None:
        """Test clear operation."""
        from proxywhirl.cache_tiers import MemoryCacheTier

        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)

        # Add multiple entries
        for i in range(3):
            entry = CacheEntry(
                key=f"key_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                source="test",
                fetch_time=datetime.now(timezone.utc),
                last_accessed=datetime.now(timezone.utc),
                ttl_seconds=3600,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
            )
            tier.put(f"key_{i}", entry)

        # Clear all
        count = tier.clear()
        assert count == 3, "Clear should return count of removed entries"
        assert tier.size() == 0, "Tier should be empty after clear"

    def test_memory_tier_size(self, tier_config: CacheTierConfig) -> None:
        """Test size tracking."""
        from proxywhirl.cache_tiers import MemoryCacheTier

        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)
        assert tier.size() == 0, "Initial size should be 0"

        # Add entries
        for i in range(2):
            entry = CacheEntry(
                key=f"key_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                source="test",
                fetch_time=datetime.now(timezone.utc),
                last_accessed=datetime.now(timezone.utc),
                ttl_seconds=3600,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
            )
            tier.put(f"key_{i}", entry)

        assert tier.size() == 2, "Size should match entry count"

    def test_memory_tier_keys(self, tier_config: CacheTierConfig) -> None:
        """Test keys listing."""
        from proxywhirl.cache_tiers import MemoryCacheTier

        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)

        # Add entries
        keys_added = ["key_1", "key_2", "key_3"]
        for key in keys_added:
            entry = CacheEntry(
                key=key,
                proxy_url=f"http://proxy.example.com:8080",
                source="test",
                fetch_time=datetime.now(timezone.utc),
                last_accessed=datetime.now(timezone.utc),
                ttl_seconds=3600,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
            )
            tier.put(key, entry)

        keys = tier.keys()
        assert set(keys) == set(keys_added), "Keys should match added entries"

    def test_memory_tier_lru_eviction(self, tier_config: CacheTierConfig) -> None:
        """Test LRU eviction when max_entries exceeded."""
        from proxywhirl.cache_tiers import MemoryCacheTier

        tier = MemoryCacheTier(tier_config, TierType.L1_MEMORY)  # max_entries=3

        # Add 3 entries
        for i in range(3):
            entry = CacheEntry(
                key=f"key_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                source="test",
                fetch_time=datetime.now(timezone.utc),
                last_accessed=datetime.now(timezone.utc),
                ttl_seconds=3600,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
            )
            tier.put(f"key_{i}", entry)

        # Add 4th entry - should evict key_0 (least recently used)
        entry = CacheEntry(
            key="key_3",
            proxy_url="http://proxy3.example.com:8080",
            source="test",
            fetch_time=datetime.now(timezone.utc),
            last_accessed=datetime.now(timezone.utc),
            ttl_seconds=3600,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
        )
        tier.put("key_3", entry)

        # Verify key_0 was evicted
        assert tier.size() == 3, "Size should remain at max_entries"
        assert tier.get("key_0") is None, "Oldest entry should be evicted"
        assert tier.get("key_3") is not None, "New entry should be present"


class TestFileCacheTier:
    """Test FileCacheTier (L2 JSONL file cache with encryption)."""

    @pytest.fixture
    def tier_config(self) -> CacheTierConfig:
        """Fixture for tier configuration."""
        return CacheTierConfig(enabled=True, max_entries=100, eviction_policy="lru")

    @pytest.fixture
    def cache_dir(self, tmp_path: Path) -> Path:
        """Fixture for temporary cache directory."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return cache_dir

    @pytest.fixture
    def sample_entry(self) -> CacheEntry:
        """Fixture for a sample cache entry with credentials."""
        from pydantic import SecretStr

        now = datetime.now(timezone.utc)
        return CacheEntry(
            key="test_key_1",
            proxy_url="http://proxy1.example.com:8080",
            username=SecretStr("testuser"),
            password=SecretStr("testpass"),
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
            health_status=HealthStatus.HEALTHY,
        )

    def test_file_tier_put_and_get(
        self, tier_config: CacheTierConfig, cache_dir: Path, sample_entry: CacheEntry
    ) -> None:
        """Test JSONL file put and get operations."""
        from proxywhirl.cache_tiers import FileCacheTier

        tier = FileCacheTier(tier_config, TierType.L2_FILE, cache_dir=cache_dir)

        # Put entry
        result = tier.put(sample_entry.key, sample_entry)
        assert result is True, "Put should succeed"

        # Get entry
        retrieved = tier.get(sample_entry.key)
        assert retrieved is not None, "Entry should be retrievable"
        assert retrieved.key == sample_entry.key
        assert retrieved.proxy_url == sample_entry.proxy_url
        # Credentials should be encrypted at rest, decrypted on retrieval
        assert retrieved.username is not None
        assert retrieved.username.get_secret_value() == "testuser"

    def test_file_tier_persistence(
        self, tier_config: CacheTierConfig, cache_dir: Path, sample_entry: CacheEntry
    ) -> None:
        """Test persistence across tier instances."""
        from proxywhirl.cache_crypto import CredentialEncryptor
        from proxywhirl.cache_tiers import FileCacheTier

        # Use shared encryptor for both instances
        encryptor = CredentialEncryptor()

        # Create tier, add entry, destroy
        tier1 = FileCacheTier(tier_config, TierType.L2_FILE, cache_dir=cache_dir, encryptor=encryptor)
        tier1.put(sample_entry.key, sample_entry)
        del tier1

        # Create new tier instance, verify entry persists
        tier2 = FileCacheTier(tier_config, TierType.L2_FILE, cache_dir=cache_dir, encryptor=encryptor)
        retrieved = tier2.get(sample_entry.key)
        assert retrieved is not None, "Entry should persist across instances"
        assert retrieved.key == sample_entry.key

    def test_file_tier_delete(
        self, tier_config: CacheTierConfig, cache_dir: Path, sample_entry: CacheEntry
    ) -> None:
        """Test file-based delete operation."""
        from proxywhirl.cache_tiers import FileCacheTier

        tier = FileCacheTier(tier_config, TierType.L2_FILE, cache_dir=cache_dir)

        # Put then delete
        tier.put(sample_entry.key, sample_entry)
        result = tier.delete(sample_entry.key)
        assert result is True, "Delete should succeed"

        # Verify deleted
        retrieved = tier.get(sample_entry.key)
        assert retrieved is None, "Deleted entry should not be retrievable"


class TestSQLiteCacheTier:
    """Test SQLiteCacheTier (L3 database cache with encrypted credentials)."""

    @pytest.fixture
    def tier_config(self) -> CacheTierConfig:
        """Fixture for tier configuration."""
        return CacheTierConfig(enabled=True, max_entries=None, eviction_policy="lru")

    @pytest.fixture
    def db_path(self, tmp_path: Path) -> Path:
        """Fixture for temporary database path."""
        return tmp_path / "test_cache.db"

    @pytest.fixture
    def sample_entry(self) -> CacheEntry:
        """Fixture for a sample cache entry with credentials."""
        from pydantic import SecretStr

        now = datetime.now(timezone.utc)
        return CacheEntry(
            key="test_key_1",
            proxy_url="http://proxy1.example.com:8080",
            username=SecretStr("dbuser"),
            password=SecretStr("dbpass"),
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
            health_status=HealthStatus.HEALTHY,
        )

    def test_sqlite_tier_put_and_get(
        self, tier_config: CacheTierConfig, db_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test SQLite put and get operations with encryption."""
        from proxywhirl.cache_tiers import SQLiteCacheTier

        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path=db_path)

        # Put entry
        result = tier.put(sample_entry.key, sample_entry)
        assert result is True, "Put should succeed"

        # Get entry
        retrieved = tier.get(sample_entry.key)
        assert retrieved is not None, "Entry should be retrievable"
        assert retrieved.key == sample_entry.key
        assert retrieved.username is not None
        assert retrieved.username.get_secret_value() == "dbuser"

    def test_sqlite_tier_persistence(
        self, tier_config: CacheTierConfig, db_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test SQLite persistence across connections."""
        from proxywhirl.cache_crypto import CredentialEncryptor
        from proxywhirl.cache_tiers import SQLiteCacheTier

        # Use shared encryptor for both instances
        encryptor = CredentialEncryptor()

        # Create tier, add entry, destroy
        tier1 = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path=db_path, encryptor=encryptor)
        tier1.put(sample_entry.key, sample_entry)
        del tier1

        # Create new tier instance, verify entry persists
        tier2 = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path=db_path, encryptor=encryptor)
        retrieved = tier2.get(sample_entry.key)
        assert retrieved is not None, "Entry should persist in database"
        assert retrieved.key == sample_entry.key

    def test_sqlite_tier_delete(
        self, tier_config: CacheTierConfig, db_path: Path, sample_entry: CacheEntry
    ) -> None:
        """Test SQLite delete operation."""
        from proxywhirl.cache_tiers import SQLiteCacheTier

        tier = SQLiteCacheTier(tier_config, TierType.L3_SQLITE, db_path=db_path)

        # Put then delete
        tier.put(sample_entry.key, sample_entry)
        result = tier.delete(sample_entry.key)
        assert result is True, "Delete should succeed"

        # Verify deleted
        retrieved = tier.get(sample_entry.key)
        assert retrieved is None, "Deleted entry should not be retrievable"
