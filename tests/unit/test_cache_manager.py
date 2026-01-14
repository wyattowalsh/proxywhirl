"""Unit tests for CacheManager orchestration logic.

Tests the CacheManager class that coordinates operations across all three tiers
(L1 memory, L2 JSONL files, L3 SQLite) and handles statistics tracking.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import SecretStr

from proxywhirl.cache import CacheConfig, CacheEntry, CacheManager, HealthStatus


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

    def test_cache_manager_put_get(
        self, cache_config: CacheConfig, sample_entry: CacheEntry
    ) -> None:
        """Test CacheManager put and get orchestration."""
        manager = CacheManager(cache_config)

        # Put entry
        result = manager.put(sample_entry.key, sample_entry)
        assert result is True, "Put should succeed"

        # Get entry
        retrieved = manager.get(sample_entry.key)
        assert retrieved is not None, "Entry should be retrievable"
        assert retrieved.key == sample_entry.key

    def test_cache_manager_delete(
        self, cache_config: CacheConfig, sample_entry: CacheEntry
    ) -> None:
        """Test CacheManager delete across all tiers."""
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
        from proxywhirl.cache import CredentialEncryptor

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
        from proxywhirl.cache import CredentialEncryptor

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
        from proxywhirl.cache import CredentialEncryptor

        encryptor = CredentialEncryptor()
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )

    def test_l3_hit_promotes_to_l1_and_l2(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test that L3 cache hit promotes entry to L1 and L2."""
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

    def test_l2_hit_promotes_to_l1(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test that L2 cache hit promotes entry to L1."""
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

    def test_l1_hit_no_promotion(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test that L1 cache hit does not trigger promotion."""
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
        from proxywhirl.cache import CredentialEncryptor

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
        assert manager.l1_tier.get("entry_0") is not None, (
            "Retrieved entry should be promoted to L1"
        )


class TestAccessTracking:
    """Test access_count and last_accessed tracking.

    T065: Unit test for access_count and last_accessed tracking.
    """

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        from proxywhirl.cache import CredentialEncryptor

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

    def test_last_accessed_updates_on_get(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test that last_accessed timestamp updates on each get."""
        import time

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


class TestTTLManager:
    """Test TTLManager background cleanup."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration with TTL cleanup enabled."""
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            enable_background_cleanup=True,
            cleanup_interval_seconds=5,  # Minimum is 5
        )

    def test_ttl_manager_start_stop(self, cache_config: CacheConfig) -> None:
        """Test TTLManager can be started and stopped."""
        manager = CacheManager(cache_config)
        assert manager.ttl_manager is not None
        assert manager.ttl_manager.enabled is True

        # Stop the TTL manager
        manager.ttl_manager.stop()
        assert manager.ttl_manager.enabled is False

    def test_ttl_manager_start_idempotent(self, cache_config: CacheConfig) -> None:
        """Test that calling start() twice is safe (early return)."""
        manager = CacheManager(cache_config)
        assert manager.ttl_manager is not None

        # Call start again - should not raise
        manager.ttl_manager.start()
        assert manager.ttl_manager.enabled is True

        manager.ttl_manager.stop()

    def test_ttl_manager_stop_idempotent(self, cache_config: CacheConfig) -> None:
        """Test that calling stop() twice is safe (early return)."""
        manager = CacheManager(cache_config)
        assert manager.ttl_manager is not None

        manager.ttl_manager.stop()
        # Call stop again - should not raise
        manager.ttl_manager.stop()
        assert manager.ttl_manager.enabled is False

    def test_ttl_cleanup_removes_expired_entries(self, tmp_path: Path) -> None:
        """Test that TTL cleanup removes expired entries."""

        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            enable_background_cleanup=False,  # Manual cleanup for test
        )
        manager = CacheManager(config)

        # Create expired entry
        now = datetime.now(timezone.utc)
        expired_entry = CacheEntry(
            key="expired_key",
            proxy_url="http://proxy.example.com:8080",
            source="test",
            fetch_time=now - timedelta(hours=2),
            last_accessed=now - timedelta(hours=2),
            ttl_seconds=3600,
            expires_at=now - timedelta(hours=1),  # Already expired
        )
        manager.put(expired_entry.key, expired_entry)

        # Create TTL manager and manually run cleanup
        from proxywhirl.cache.manager import TTLManager

        ttl_manager = TTLManager(manager, cleanup_interval=60)
        removed = ttl_manager._cleanup_expired_entries()
        assert removed >= 1, "Expired entry should be removed"

        # Verify entry is gone
        retrieved = manager.get(expired_entry.key)
        assert retrieved is None


class TestCacheManagerExpiredEntryHandling:
    """Test expired entry handling in get() method."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )

    def test_get_expired_from_l2_returns_none(self, cache_config: CacheConfig) -> None:
        """Test that expired entries in L2 are removed and None returned."""
        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)
        expired_entry = CacheEntry(
            key="expired_l2",
            proxy_url="http://proxy.example.com:8080",
            source="test",
            fetch_time=now - timedelta(hours=2),
            last_accessed=now - timedelta(hours=2),
            ttl_seconds=3600,
            expires_at=now - timedelta(hours=1),  # Already expired
        )

        # Put directly in L2 only
        manager.l2_tier.put(expired_entry.key, expired_entry)

        # Get should return None for expired entry
        retrieved = manager.get(expired_entry.key)
        assert retrieved is None
        # Check TTL eviction was counted
        assert manager.statistics.l2_stats.evictions_ttl >= 1

    def test_get_expired_from_l3_returns_none(self, cache_config: CacheConfig) -> None:
        """Test that expired entries in L3 are removed and None returned."""
        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)
        expired_entry = CacheEntry(
            key="expired_l3",
            proxy_url="http://proxy.example.com:8080",
            source="test",
            fetch_time=now - timedelta(hours=2),
            last_accessed=now - timedelta(hours=2),
            ttl_seconds=3600,
            expires_at=now - timedelta(hours=1),  # Already expired
        )

        # Put directly in L3 only
        manager.l3_tier.put(expired_entry.key, expired_entry)

        # Get should return None for expired entry
        retrieved = manager.get(expired_entry.key)
        assert retrieved is None
        assert manager.statistics.l3_stats.evictions_ttl >= 1


class TestCacheManagerTierExceptionHandling:
    """Test exception handling in put() for L2 and L3 tiers."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )

    def test_put_handles_l2_exception(self, cache_config: CacheConfig) -> None:
        """Test that put handles L2 tier exceptions gracefully."""
        from unittest.mock import patch

        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="l2_error_key",
            proxy_url="http://proxy.example.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )

        # Mock L2 put to raise an exception
        with patch.object(manager.l2_tier, "put", side_effect=Exception("L2 error")):
            result = manager.put(entry.key, entry)
            # Should still succeed because L1/L3 work
            assert result is True

    def test_put_handles_l3_exception(self, cache_config: CacheConfig) -> None:
        """Test that put handles L3 tier exceptions gracefully."""
        from unittest.mock import patch

        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="l3_error_key",
            proxy_url="http://proxy.example.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )

        # Mock L3 put to raise an exception
        with patch.object(manager.l3_tier, "put", side_effect=Exception("L3 error")):
            result = manager.put(entry.key, entry)
            # Should still succeed because L1/L2 work
            assert result is True


class TestCacheManagerClear:
    """Test CacheManager clear() method."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )

    def test_clear_removes_all_entries(self, cache_config: CacheConfig) -> None:
        """Test clear removes entries from all tiers."""
        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)
        for i in range(3):
            entry = CacheEntry(
                key=f"entry_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                source="test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(hours=1),
            )
            manager.put(entry.key, entry)

        # Clear all
        count = manager.clear()
        assert count >= 3

        # Verify all cleared
        assert manager.l1_tier.size() == 0
        assert manager.l2_tier.size() == 0
        assert manager.l3_tier.size() == 0
        assert manager.statistics.l1_stats.current_size == 0
        assert manager.statistics.l2_stats.current_size == 0
        assert manager.statistics.l3_stats.current_size == 0


class TestCacheManagerInvalidateHealth:
    """Test invalidate_by_health edge cases."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            health_check_invalidation=True,
            failure_threshold=3,
        )

    def test_invalidate_nonexistent_key(self, cache_config: CacheConfig) -> None:
        """Test invalidate_by_health with nonexistent key returns early."""
        manager = CacheManager(cache_config)

        # Should not raise error
        manager.invalidate_by_health("nonexistent_key")


class TestCacheManagerL3InitializationFailure:
    """Test L3 tier initialization failure fallback."""

    def test_l3_init_failure_creates_fallback(self, tmp_path: Path) -> None:
        """Test that L3 initialization failure creates disabled fallback tier."""
        from unittest.mock import patch

        from proxywhirl.cache import CacheManager
        from proxywhirl.cache.tiers import SQLiteCacheTier

        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )

        # Mock SQLiteCacheTier init to raise
        with patch.object(SQLiteCacheTier, "__init__", side_effect=Exception("DB init failed")):
            manager = CacheManager(config)
            # L3 should be disabled fallback tier
            assert manager.l3_tier is not None
            assert manager.l3_tier.enabled is False


class TestCacheManagerGenerateCacheKey:
    """Test cache key generation."""

    def test_generate_cache_key_consistent(self) -> None:
        """Test that generate_cache_key returns consistent results."""
        from proxywhirl.cache.manager import CacheManager

        url = "http://proxy.example.com:8080"
        key1 = CacheManager.generate_cache_key(url)
        key2 = CacheManager.generate_cache_key(url)

        assert key1 == key2
        assert len(key1) == 16  # First 16 chars of SHA256 hex

    def test_generate_cache_key_unique_for_different_urls(self) -> None:
        """Test that different URLs generate different keys."""
        from proxywhirl.cache.manager import CacheManager

        key1 = CacheManager.generate_cache_key("http://proxy1.example.com:8080")
        key2 = CacheManager.generate_cache_key("http://proxy2.example.com:8080")

        assert key1 != key2


class TestCacheManagerGetStatistics:
    """Test get_statistics method."""

    def test_get_statistics_returns_copy(self, tmp_path: Path) -> None:
        """Test get_statistics returns a deep copy."""
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )
        manager = CacheManager(config)

        stats = manager.get_statistics()

        # Modifying the copy should not affect original
        stats.l1_stats.hits = 9999
        assert manager.statistics.l1_stats.hits != 9999

    def test_get_statistics_updates_degradation_status(self, tmp_path: Path) -> None:
        """Test that get_statistics updates degradation status."""
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )
        manager = CacheManager(config)

        # Disable L1
        manager.l1_tier.enabled = False

        stats = manager.get_statistics()
        assert stats.l1_degraded is True
        assert stats.l2_degraded is False
        assert stats.l3_degraded is False


class TestCacheManagerDestructor:
    """Test CacheManager cleanup on deletion."""

    def test_destructor_stops_ttl_manager(self, tmp_path: Path) -> None:
        """Test that __del__ stops the TTL manager if running."""
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            enable_background_cleanup=True,
            cleanup_interval_seconds=5,  # Minimum is 5
        )
        manager = CacheManager(config)
        ttl_manager = manager.ttl_manager

        # Explicitly call __del__ (destructor) since del may not immediately trigger it
        manager.__del__()

        # TTL manager should be stopped
        assert ttl_manager.enabled is False


class TestCacheManagerL2Disabled:
    """Test CacheManager behavior when L2 is disabled."""

    def test_l2_disabled_uses_memory_fallback(self, tmp_path: Path) -> None:
        """Test that disabled L2 uses memory fallback tier."""
        from proxywhirl.cache import CacheManager
        from proxywhirl.cache.models import CacheTierConfig

        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )
        # Disable L2
        config.l2_config = CacheTierConfig(enabled=False)

        manager = CacheManager(config)

        # L2 should be a memory tier as fallback
        from proxywhirl.cache.tiers import MemoryCacheTier

        assert isinstance(manager.l2_tier, MemoryCacheTier)


class TestL1EvictionPropagation:
    """Test L1 eviction state propagation to L2/L3 (TASK-602)."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration with small L1 capacity."""
        from proxywhirl.cache import CredentialEncryptor

        encryptor = CredentialEncryptor()
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )

    def test_l1_eviction_marks_entry_as_evicted_in_l2(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that L1 eviction marks entry as evicted (not deleted) in L2."""
        # Override L1 max_entries to trigger eviction
        cache_config.l1_config.max_entries = 2
        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)

        # Add 3 entries (triggers L1 eviction of entry_0)
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

        # entry_0 should be evicted from L1
        assert manager.l1_tier.get("entry_0") is None, "entry_0 should be evicted from L1"

        # entry_0 should still exist in L2 but marked as evicted
        l2_entry = manager.l2_tier.get("entry_0")
        assert l2_entry is not None, "entry_0 should still exist in L2"
        assert l2_entry.evicted_from_l1 is True, "entry_0 should be marked as evicted in L2"

    def test_l1_eviction_marks_entry_as_evicted_in_l3(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that L1 eviction marks entry as evicted (not deleted) in L3."""
        # Override L1 max_entries to trigger eviction
        cache_config.l1_config.max_entries = 2
        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)

        # Add 3 entries (triggers L1 eviction of entry_0)
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

        # entry_0 should be evicted from L1
        assert manager.l1_tier.get("entry_0") is None, "entry_0 should be evicted from L1"

        # entry_0 should still exist in L3 but marked as evicted
        l3_entry = manager.l3_tier.get("entry_0")
        assert l3_entry is not None, "entry_0 should still exist in L3"
        assert l3_entry.evicted_from_l1 is True, "entry_0 should be marked as evicted in L3"

    def test_evicted_entry_can_be_promoted_back_to_l1(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that evicted entry can be promoted back to L1 on access."""
        # Override L1 max_entries to trigger eviction
        cache_config.l1_config.max_entries = 2
        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)

        # Add 3 entries (triggers L1 eviction of entry_0)
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

        # entry_0 should be evicted from L1
        assert manager.l1_tier.get("entry_0") is None

        # Access entry_0 via CacheManager (should promote back to L1)
        retrieved = manager.get("entry_0")
        assert retrieved is not None, "Evicted entry should be retrievable"
        assert retrieved.key == "entry_0"

        # entry_0 should now be back in L1 (promoted)
        l1_entry = manager.l1_tier.get("entry_0")
        assert l1_entry is not None, "entry_0 should be promoted back to L1"

    def test_non_evicted_entries_have_false_flag(
        self, tmp_path: Path, cache_config: CacheConfig
    ) -> None:
        """Test that non-evicted entries have evicted_from_l1=False."""
        manager = CacheManager(cache_config)

        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="test_entry",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
        )

        manager.put(entry.key, entry)

        # Check all tiers have evicted_from_l1=False
        l1_entry = manager.l1_tier.get(entry.key)
        assert l1_entry is not None
        assert l1_entry.evicted_from_l1 is False

        l2_entry = manager.l2_tier.get(entry.key)
        assert l2_entry is not None
        assert l2_entry.evicted_from_l1 is False

        l3_entry = manager.l3_tier.get(entry.key)
        assert l3_entry is not None
        assert l3_entry.evicted_from_l1 is False


class TestCacheWarmingFromFile:
    """Test cache warming from various file formats."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )

    def test_warm_from_json_file(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test cache warming from JSON array file."""
        import json

        manager = CacheManager(cache_config)

        # Create JSON file with proxy data
        json_file = tmp_path / "proxies.json"
        proxy_data = [
            {"proxy_url": "http://proxy1.example.com:8080", "source": "test"},
            {"proxy_url": "http://proxy2.example.com:8080", "source": "test"},
            {"proxy_url": "http://proxy3.example.com:8080", "source": "test"},
        ]
        with open(json_file, "w") as f:
            json.dump(proxy_data, f)

        # Warm cache
        result = manager.warm_from_file(str(json_file))
        assert result["loaded"] == 3
        assert result["skipped"] == 0
        assert result["failed"] == 0

        # Verify entries are in cache
        assert manager.l1_tier.size() == 3

    def test_warm_from_jsonl_file(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test cache warming from JSONL file."""
        import json

        manager = CacheManager(cache_config)

        # Create JSONL file
        jsonl_file = tmp_path / "proxies.jsonl"
        with open(jsonl_file, "w") as f:
            f.write(
                json.dumps({"proxy_url": "http://proxy1.example.com:8080", "source": "test"}) + "\n"
            )
            f.write(
                json.dumps({"proxy_url": "http://proxy2.example.com:8080", "source": "test"}) + "\n"
            )
            f.write(
                json.dumps({"proxy_url": "http://proxy3.example.com:8080", "source": "test"}) + "\n"
            )

        # Warm cache
        result = manager.warm_from_file(str(jsonl_file))
        assert result["loaded"] == 3
        assert result["skipped"] == 0

    def test_warm_from_csv_file(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test cache warming from CSV file."""
        import csv

        manager = CacheManager(cache_config)

        # Create CSV file
        csv_file = tmp_path / "proxies.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["proxy_url", "source"])
            writer.writeheader()
            writer.writerow({"proxy_url": "http://proxy1.example.com:8080", "source": "test"})
            writer.writerow({"proxy_url": "http://proxy2.example.com:8080", "source": "test"})

        # Warm cache
        result = manager.warm_from_file(str(csv_file))
        assert result["loaded"] == 2

    def test_warm_from_nonexistent_file(self, cache_config: CacheConfig) -> None:
        """Test cache warming with nonexistent file."""
        manager = CacheManager(cache_config)

        result = manager.warm_from_file("/nonexistent/file.json")
        assert result["loaded"] == 0
        assert result["failed"] == 1

    def test_warm_with_ttl_override(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test cache warming with TTL override."""
        import json

        manager = CacheManager(cache_config)

        json_file = tmp_path / "proxies.json"
        proxy_data = [{"proxy_url": "http://proxy1.example.com:8080", "source": "test"}]
        with open(json_file, "w") as f:
            json.dump(proxy_data, f)

        # Warm with custom TTL
        result = manager.warm_from_file(str(json_file), ttl_override=7200)
        assert result["loaded"] == 1

        # Verify TTL was set
        key = manager.generate_cache_key("http://proxy1.example.com:8080")
        entry = manager.get(key)
        assert entry is not None
        assert entry.ttl_seconds == 7200

    def test_warm_skips_invalid_entries(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test that invalid entries are skipped during warming."""
        import json

        manager = CacheManager(cache_config)

        json_file = tmp_path / "proxies.json"
        proxy_data = [
            {"proxy_url": "http://proxy1.example.com:8080", "source": "test"},
            {"missing": "proxy_url"},  # Invalid - no proxy_url
            {"proxy_url": "", "source": "test"},  # Invalid - empty proxy_url
        ]
        with open(json_file, "w") as f:
            json.dump(proxy_data, f)

        result = manager.warm_from_file(str(json_file))
        assert result["loaded"] == 1
        assert result["skipped"] == 2

    def test_warm_from_invalid_json(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test cache warming with invalid JSON format."""
        manager = CacheManager(cache_config)

        json_file = tmp_path / "invalid.json"
        with open(json_file, "w") as f:
            f.write("not valid json {")

        result = manager.warm_from_file(str(json_file))
        assert result["loaded"] == 0
        assert result["failed"] >= 1

    def test_warm_from_json_non_array(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test cache warming with JSON object instead of array."""
        import json

        manager = CacheManager(cache_config)

        json_file = tmp_path / "proxies.json"
        with open(json_file, "w") as f:
            json.dump({"proxy_url": "http://proxy1.example.com:8080"}, f)

        result = manager.warm_from_file(str(json_file))
        assert result["loaded"] == 0
        assert result["failed"] == 1

    def test_warm_from_unsupported_format(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test cache warming with unsupported file format."""
        manager = CacheManager(cache_config)

        xml_file = tmp_path / "proxies.xml"
        xml_file.write_text("<proxies></proxies>")

        result = manager.warm_from_file(str(xml_file))
        assert result["loaded"] == 0
        assert result["failed"] == 1


class TestCacheExport:
    """Test cache export functionality."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )

    def test_export_to_file(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test exporting cache entries to a file."""
        import json

        manager = CacheManager(cache_config)

        # Add entries to cache
        now = datetime.now(timezone.utc)
        for i in range(3):
            entry = CacheEntry(
                key=f"export_entry_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                source="test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(hours=1),
            )
            manager.put(entry.key, entry)

        # Export to file
        export_file = tmp_path / "export.jsonl"
        result = manager.export_to_file(str(export_file))
        assert result["exported"] >= 3
        assert result["failed"] == 0

        # Verify file was created
        assert export_file.exists()

        # Verify content
        with open(export_file) as f:
            lines = f.readlines()
            assert len(lines) >= 3
            for line in lines:
                data = json.loads(line.strip())
                assert "proxy_url" in data


class TestCacheConcurrency:
    """Test concurrent access scenarios."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )

    def test_concurrent_put_operations(self, cache_config: CacheConfig) -> None:
        """Test concurrent put operations are thread-safe."""
        import threading

        manager = CacheManager(cache_config)
        now = datetime.now(timezone.utc)

        def put_entry(i: int) -> None:
            entry = CacheEntry(
                key=f"concurrent_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                source="test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(hours=1),
            )
            manager.put(entry.key, entry)

        # Run 10 concurrent puts
        threads = [threading.Thread(target=put_entry, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Verify all entries were added
        assert manager.l1_tier.size() == 10

    def test_concurrent_get_operations(self, cache_config: CacheConfig) -> None:
        """Test concurrent get operations are thread-safe."""
        import threading

        manager = CacheManager(cache_config)

        # Pre-populate cache
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="shared_entry",
            proxy_url="http://proxy.example.com:8080",
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        manager.put(entry.key, entry)

        results = []

        def get_entry() -> None:
            result = manager.get("shared_entry")
            results.append(result)

        # Run 10 concurrent gets
        threads = [threading.Thread(target=get_entry) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All gets should succeed
        assert len(results) == 10
        assert all(r is not None for r in results)


class TestCacheMissScenarios:
    """Test cache miss scenarios across tiers."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )

    def test_complete_cache_miss(self, cache_config: CacheConfig) -> None:
        """Test get on completely missing key (L1/L2/L3 all miss)."""
        manager = CacheManager(cache_config)

        # Get non-existent key
        result = manager.get("nonexistent_key")
        assert result is None

        # Verify miss statistics
        assert manager.statistics.l1_stats.misses >= 1
        assert manager.statistics.l2_stats.misses >= 1
        assert manager.statistics.l3_stats.misses >= 1


class TestCacheWarmingEdgeCases:
    """Test edge cases in cache warming."""

    @pytest.fixture
    def cache_config(self, tmp_path: Path) -> CacheConfig:
        """Fixture for cache configuration."""
        return CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
        )

    def test_warm_with_credentials(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test cache warming with credentials."""
        import json

        manager = CacheManager(cache_config)

        json_file = tmp_path / "proxies.json"
        proxy_data = [
            {
                "proxy_url": "http://proxy1.example.com:8080",
                "source": "test",
                "username": "user1",
                "password": "pass1",
            }
        ]
        with open(json_file, "w") as f:
            json.dump(proxy_data, f)

        result = manager.warm_from_file(str(json_file))
        assert result["loaded"] == 1

        # Verify entry has credentials (encrypted in storage)
        key = manager.generate_cache_key("http://proxy1.example.com:8080")
        entry = manager.get(key)
        assert entry is not None
        assert entry.username is not None
        assert entry.password is not None

    def test_warm_jsonl_with_empty_lines(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test JSONL warming skips empty lines."""
        import json

        manager = CacheManager(cache_config)

        jsonl_file = tmp_path / "proxies.jsonl"
        with open(jsonl_file, "w") as f:
            f.write(
                json.dumps({"proxy_url": "http://proxy1.example.com:8080", "source": "test"}) + "\n"
            )
            f.write("\n")  # Empty line
            f.write("   \n")  # Whitespace only
            f.write(
                json.dumps({"proxy_url": "http://proxy2.example.com:8080", "source": "test"}) + "\n"
            )

        result = manager.warm_from_file(str(jsonl_file))
        assert result["loaded"] == 2  # Should skip empty lines

    def test_warm_jsonl_with_invalid_line(self, tmp_path: Path, cache_config: CacheConfig) -> None:
        """Test JSONL warming handles invalid JSON lines."""
        import json

        manager = CacheManager(cache_config)

        jsonl_file = tmp_path / "proxies.jsonl"
        with open(jsonl_file, "w") as f:
            f.write(
                json.dumps({"proxy_url": "http://proxy1.example.com:8080", "source": "test"}) + "\n"
            )
            f.write("invalid json line\n")
            f.write(
                json.dumps({"proxy_url": "http://proxy2.example.com:8080", "source": "test"}) + "\n"
            )

        result = manager.warm_from_file(str(jsonl_file))
        assert result["loaded"] == 2
        assert result["failed"] == 1
