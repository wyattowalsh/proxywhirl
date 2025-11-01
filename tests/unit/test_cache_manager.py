"""Unit tests for CacheManager orchestration logic.

Tests the CacheManager class that coordinates operations across all three tiers
(L1 memory, L2 JSONL files, L3 SQLite) and handles statistics tracking.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import SecretStr

from proxywhirl.cache_models import CacheConfig, CacheEntry, HealthStatus


class TestCacheManager:
    """Test CacheManager multi-tier orchestration."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            default_ttl_seconds=3600,
        )

    @pytest.fixture
    def sample_entry(self) -> CacheEntry:
        """Fixture for a sample cache entry."""
        now = datetime.now(timezone.utc)
        return CacheEntry(
            key="test_key",
            proxy_url="http://proxy.example.com:8080",
            username=SecretStr("user"),
            password=SecretStr("pass"),
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
            health_status=HealthStatus.HEALTHY,
        )

    def test_cache_manager_put_get(self, cache_config: CacheConfig, sample_entry: CacheEntry) -> None:
        """Test CacheManager put and get orchestration."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)

        # Put entry
        result = manager.put(sample_entry.key, sample_entry)
        assert result is True, "Put should succeed"

        # Get entry
        retrieved = manager.get(sample_entry.key)
        assert retrieved is not None, "Entry should be retrievable"
        assert retrieved.key == sample_entry.key

    def test_cache_manager_delete(self, cache_config: CacheConfig, sample_entry: CacheEntry) -> None:
        """Test CacheManager delete across all tiers."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)

        # Put then delete
        manager.put(sample_entry.key, sample_entry)
        result = manager.delete(sample_entry.key)
        assert result is True, "Delete should succeed"

        # Verify deleted
        retrieved = manager.get(sample_entry.key)
        assert retrieved is None, "Deleted entry should not be retrievable"

    def test_cache_manager_multi_tier_lookup(
        self, cache_config: CacheConfig, sample_entry: CacheEntry
    ) -> None:
        """Test that CacheManager checks L1 -> L2 -> L3 in order."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)

        # Put entry (should go to all tiers)
        manager.put(sample_entry.key, sample_entry)

        # Clear L1 only
        manager.l1_tier.clear()

        # Get should still succeed from L2/L3
        retrieved = manager.get(sample_entry.key)
        assert retrieved is not None, "Entry should be found in L2/L3"


class TestCacheLogging:
    """Test cache operation logging and credential redaction."""

    def test_cache_put_logged_with_redaction(self, tmp_path: Path) -> None:
        """Test that cache put operations are logged with credentials redacted."""
        import io
        import sys

        from loguru import logger

        from proxywhirl.cache import CacheManager
        from proxywhirl.cache_models import CacheConfig

        # Capture logs to a string buffer
        log_buffer = io.StringIO()
        # Remove default handler and add our custom one
        logger.remove()
        logger.add(log_buffer, format="{message}", level="DEBUG")

        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )
        manager = CacheManager(config)

        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="test",
            proxy_url="http://proxy.example.com:8080",
            username=SecretStr("secret_user"),
            password=SecretStr("secret_pass"),
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
        )

        manager.put("test", entry)

        # Get log output
        log_output = log_buffer.getvalue()

        # Re-add default stderr handler for subsequent tests
        logger.add(sys.stderr, format="{message}", level="DEBUG")

        # Verify logging occurred
        assert "cache" in log_output.lower(), f"Cache operation should be logged. Got: {log_output}"

        # Verify credentials are NOT in logs
        assert "secret_user" not in log_output, "Username should not appear in logs"
        assert "secret_pass" not in log_output, "Password should not appear in logs"
        assert "***" in log_output, "Credentials should be redacted with ***"


class TestHealthInvalidation:
    """Test health-based cache invalidation."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration with health checking enabled."""
        from proxywhirl.cache_crypto import CredentialEncryptor

        encryptor = CredentialEncryptor()
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
            health_check_invalidation=True,
            failure_threshold=3,
        )

    def test_invalidate_by_health_increments_failure_count(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that invalidate_by_health increments failure_count."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)

        # Create healthy entry
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="test_proxy",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
            health_status=HealthStatus.HEALTHY,
            failure_count=0,
        )

        manager.put(entry.key, entry)

        # Mark as unhealthy (failure)
        manager.invalidate_by_health(entry.key)

        # Retrieve and check failure count
        retrieved = manager.get(entry.key)
        assert retrieved is not None, "Entry should still exist after one failure"
        assert retrieved.failure_count == 1, "Failure count should be incremented"
        assert retrieved.health_status == HealthStatus.UNHEALTHY


class TestFailureThreshold:
    """Test proxy removal when failure threshold is reached."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration with low failure threshold."""
        from proxywhirl.cache_crypto import CredentialEncryptor

        encryptor = CredentialEncryptor()
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
            health_check_invalidation=True,
            failure_threshold=3,
        )

    def test_proxy_removed_when_failure_threshold_reached(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that proxy is removed after reaching failure threshold."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)

        # Create entry
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="failing_proxy",
            proxy_url="http://bad-proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
            health_status=HealthStatus.HEALTHY,
            failure_count=0,
        )

        manager.put(entry.key, entry)

        # Trigger failures up to threshold
        for i in range(3):
            manager.invalidate_by_health(entry.key)

        # Proxy should be removed
        retrieved = manager.get(entry.key)
        assert retrieved is None, "Proxy should be removed after reaching failure threshold"


class TestTierPromotion:
    """Test tier promotion on cache hits.

    T063: Unit test for tier promotion on cache hit (L3→L2→L1).
    """

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        from proxywhirl.cache_crypto import CredentialEncryptor

        encryptor = CredentialEncryptor()
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )

    def test_l3_hit_promotes_to_l1_and_l2(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that L3 cache hit promotes entry to L1 and L2."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)

        # Create entry
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="l3_entry",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
        )

        # Put only in L3
        manager.l3_tier.put(entry.key, entry)

        # Get should find in L3 and promote to L1, L2
        retrieved = manager.get(entry.key)
        assert retrieved is not None, "Entry should be found in L3"

        # Verify promotion to L1 and L2
        assert manager.l1_tier.get(entry.key) is not None, "Entry should be promoted to L1"
        assert manager.l2_tier.get(entry.key) is not None, "Entry should be promoted to L2"

        # Check promotion statistics
        assert manager.statistics.promotions == 2, "Should record 2 promotions (to L1 and L2)"

    def test_l2_hit_promotes_to_l1(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that L2 cache hit promotes entry to L1."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)

        # Create entry
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="l2_entry",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
        )

        # Put only in L2
        manager.l2_tier.put(entry.key, entry)

        # Get should find in L2 and promote to L1
        retrieved = manager.get(entry.key)
        assert retrieved is not None, "Entry should be found in L2"

        # Verify promotion to L1
        assert manager.l1_tier.get(entry.key) is not None, "Entry should be promoted to L1"

        # Check promotion statistics
        assert manager.statistics.promotions == 1, "Should record 1 promotion (to L1)"

    def test_l1_hit_no_promotion(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that L1 cache hit does not trigger promotion."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)

        # Create entry
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="l1_entry",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
        )

        # Put in all tiers
        manager.put(entry.key, entry)

        # Reset statistics
        manager.statistics.promotions = 0

        # Get from L1 should not promote
        retrieved = manager.get(entry.key)
        assert retrieved is not None, "Entry should be found in L1"

        # Check no promotion occurred
        assert manager.statistics.promotions == 0, "L1 hit should not trigger promotion"


class TestTierDemotion:
    """Test tier demotion on L1 eviction.

    T064: Unit test for tier demotion on L1 eviction (L1→L2→L3).
    """

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration with small L1 capacity."""
        from proxywhirl.cache_crypto import CredentialEncryptor

        encryptor = CredentialEncryptor()
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )

    def test_l1_eviction_preserves_in_l2_l3(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that LRU eviction from L1 doesn't remove from L2/L3."""
        from proxywhirl.cache import CacheManager

        # Override L1 max_entries to trigger eviction
        cache_config.l1_config.max_entries = 2
        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)

        # Add 2 entries (at L1 capacity)
        for i in range(2):
            entry = CacheEntry(
                key=f"entry_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                username=None,
                password=None,
                source="test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
            )
            manager.put(f"entry_{i}", entry)

        # Add 3rd entry - should evict entry_0 from L1
        entry3 = CacheEntry(
            key="entry_2",
            proxy_url="http://proxy2.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
        )
        manager.put("entry_2", entry3)

        # entry_0 should be evicted from L1
        assert manager.l1_tier.get("entry_0") is None, "entry_0 should be evicted from L1"

        # But still exist in L2 and L3
        assert manager.l2_tier.get("entry_0") is not None, "entry_0 should still exist in L2"
        assert manager.l3_tier.get("entry_0") is not None, "entry_0 should still exist in L3"

    def test_evicted_entry_retrievable_from_lower_tiers(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that evicted L1 entry is still retrievable via CacheManager."""
        from proxywhirl.cache import CacheManager

        # Override L1 max_entries
        cache_config.l1_config.max_entries = 2
        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)

        # Add 3 entries (triggers L1 eviction)
        for i in range(3):
            entry = CacheEntry(
                key=f"entry_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                username=None,
                password=None,
                source="test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
            )
            manager.put(f"entry_{i}", entry)

        # entry_0 should be evicted from L1 but retrievable from L2/L3
        retrieved = manager.get("entry_0")
        assert retrieved is not None, "Evicted entry should be retrievable from lower tiers"
        assert retrieved.key == "entry_0"

        # And should be promoted back to L1
        assert manager.l1_tier.get("entry_0") is not None, "Retrieved entry should be promoted to L1"


class TestAccessTracking:
    """Test access_count and last_accessed tracking.

    T065: Unit test for access_count and last_accessed tracking.
    """

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        from proxywhirl.cache_crypto import CredentialEncryptor

        encryptor = CredentialEncryptor()
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )

    def test_access_count_increments_on_get(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that access_count increments on each get."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="tracked_entry",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            access_count=0,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
        )

        manager.put(entry.key, entry)

        # Access multiple times
        for i in range(5):
            retrieved = manager.get(entry.key)
            assert retrieved is not None
            assert retrieved.access_count == i + 1, f"Access count should be {i + 1}"

    def test_last_accessed_updates_on_get(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that last_accessed timestamp updates on each get."""
        import time

        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="tracked_entry",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            access_count=0,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
        )

        manager.put(entry.key, entry)
        initial_access_time = entry.last_accessed

        # Wait briefly and access again
        time.sleep(0.1)
        retrieved = manager.get(entry.key)
        assert retrieved is not None
        assert retrieved.last_accessed > initial_access_time, "last_accessed should be updated"

    def test_access_count_zero_on_new_entry(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that new entries start with access_count of 0."""
        from proxywhirl.cache import CacheManager

        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="new_entry",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            access_count=0,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
        )

        manager.put(entry.key, entry)

        # First get should show access_count = 1
        retrieved = manager.get(entry.key)
        assert retrieved is not None
        assert retrieved.access_count == 1, "First access should show count of 1"

