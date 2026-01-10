"""Integration tests for health-based cache invalidation.

Tests the complete health invalidation workflow including:
- Marking proxies unhealthy after failures
- Automatic eviction at failure threshold
- Bulk health-based eviction
- Health status persistence across tiers
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from pydantic import SecretStr

from proxywhirl.cache import CacheManager
from proxywhirl.cache.crypto import CredentialEncryptor
from proxywhirl.cache_models import CacheConfig, CacheEntry, HealthStatus


@pytest.fixture
def temp_cache_dir() -> Path:
    """Create temporary directory for cache files."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def encryption_key() -> str:
    """Generate a valid Fernet encryption key for testing."""
    encryptor = CredentialEncryptor()
    return encryptor.key.decode()


@pytest.fixture
def cache_config(temp_cache_dir: Path, encryption_key: str) -> CacheConfig:
    """Create cache configuration for testing."""
    return CacheConfig(
        encryption_key=SecretStr(encryption_key),
        l2_cache_dir=str(temp_cache_dir),
        l3_database_path=str(temp_cache_dir / "cache.db"),
        health_check_invalidation=True,
        failure_threshold=3,
        enable_background_cleanup=False,  # Disable TTL background cleanup for health tests
    )


def _create_entry(key: str, encryption_key: str) -> CacheEntry:
    """Helper to create a cache entry."""
    now = datetime.now(timezone.utc)
    return CacheEntry(
        key=key,
        proxy_url=f"http://{key}",
        username=SecretStr("testuser"),
        password=SecretStr("testpass123"),
        source="test_source",
        fetch_time=now,
        last_accessed=now,
        ttl_seconds=3600,
        expires_at=now + timedelta(seconds=3600),
        health_status=HealthStatus.HEALTHY,
        failure_count=0,
    )


class TestHealthCheckInvalidation:
    """Integration tests for health check invalidation."""

    def test_proxy_evicted_after_failure_threshold(
        self, cache_config: CacheConfig, encryption_key: str
    ) -> None:
        """Test proxy is evicted from all tiers after reaching failure threshold.

        Scenario:
        1. Add healthy proxy to cache (all tiers)
        2. Mark proxy unhealthy 3 times (failure_threshold=3)
        3. Verify proxy removed from all tiers
        4. Verify cannot retrieve proxy anymore
        """
        manager = CacheManager(cache_config)
        entry = _create_entry("proxy1.example.com:8080", encryption_key)

        # Add to cache
        manager.put(entry.key, entry)
        assert manager.get(entry.key) is not None

        # Mark unhealthy 3 times (should trigger eviction)
        for _ in range(3):
            manager.invalidate_by_health(entry.key)

        # Verify proxy removed from all tiers
        assert manager.get(entry.key) is None

        # Close manager

    def test_failure_count_persists_across_tiers(
        self, cache_config: CacheConfig, encryption_key: str
    ) -> None:
        """Test failure_count is maintained when entry moves between tiers.

        Scenario:
        1. Add entry to L3 (persistent storage)
        2. Mark unhealthy once (failure_count=1)
        3. Retrieve from L3 (promotes to L2, L1)
        4. Mark unhealthy again (failure_count=2)
        5. Verify failure_count accumulated correctly
        """
        manager = CacheManager(cache_config)
        entry = _create_entry("proxy2.example.com:8080", encryption_key)

        # Add to cache
        manager.put(entry.key, entry)

        # Mark unhealthy once
        manager.invalidate_by_health(entry.key)
        retrieved = manager.get(entry.key)
        assert retrieved is not None
        assert retrieved.failure_count == 1
        assert retrieved.health_status == HealthStatus.UNHEALTHY

        # Mark unhealthy again
        manager.invalidate_by_health(entry.key)
        retrieved = manager.get(entry.key)
        assert retrieved is not None
        assert retrieved.failure_count == 2
        assert retrieved.health_status == HealthStatus.UNHEALTHY

        # Close manager

    def test_health_status_persists_across_restart(
        self, cache_config: CacheConfig, encryption_key: str, temp_cache_dir: Path
    ) -> None:
        """Test health_status and failure_count persist across cache manager restart.

        Scenario:
        1. Add entry and mark unhealthy (failure_count=1)
        2. Close manager
        3. Create new manager with same config
        4. Verify health_status and failure_count preserved
        """
        # First manager - add and mark unhealthy
        manager1 = CacheManager(cache_config)
        entry = _create_entry("proxy3.example.com:8080", encryption_key)
        manager1.put(entry.key, entry)
        manager1.invalidate_by_health(entry.key)

        # Second manager - verify persistence
        manager2 = CacheManager(cache_config)
        retrieved = manager2.get(entry.key)
        assert retrieved is not None
        assert retrieved.failure_count == 1
        assert retrieved.health_status == HealthStatus.UNHEALTHY


class TestBulkHealthEviction:
    """Integration tests for bulk health-based eviction."""

    def test_multiple_proxies_evicted_at_threshold(
        self, cache_config: CacheConfig, encryption_key: str
    ) -> None:
        """Test multiple proxies can be independently evicted based on health.

        Scenario:
        1. Add 5 proxies to cache
        2. Mark 3 proxies unhealthy (reach threshold)
        3. Verify only unhealthy proxies removed
        4. Verify healthy proxies remain
        """
        manager = CacheManager(cache_config)

        # Add 5 proxies
        entries = [_create_entry(f"proxy{i}.example.com:8080", encryption_key) for i in range(1, 6)]
        for entry in entries:
            manager.put(entry.key, entry)

        # Mark first 3 proxies unhealthy (reach threshold)
        for entry in entries[:3]:
            for _ in range(3):
                manager.invalidate_by_health(entry.key)

        # Verify unhealthy proxies removed
        for entry in entries[:3]:
            assert manager.get(entry.key) is None

        # Verify healthy proxies remain
        for entry in entries[3:]:
            retrieved = manager.get(entry.key)
            assert retrieved is not None
            assert retrieved.health_status == HealthStatus.HEALTHY
            assert retrieved.failure_count == 0

        # Close manager

    def test_health_invalidation_disabled(
        self, cache_config: CacheConfig, encryption_key: str
    ) -> None:
        """Test health invalidation can be disabled via config.

        Scenario:
        1. Configure cache with health_check_invalidation=False
        2. Add proxy and mark unhealthy many times
        3. Verify proxy NOT evicted (config disables invalidation)
        """
        # Disable health invalidation
        cache_config.health_check_invalidation = False
        manager = CacheManager(cache_config)

        entry = _create_entry("proxy6.example.com:8080", encryption_key)
        manager.put(entry.key, entry)

        # Mark unhealthy 10 times (way above threshold)
        for _ in range(10):
            manager.invalidate_by_health(entry.key)

        # Verify proxy NOT removed (invalidation disabled)
        retrieved = manager.get(entry.key)
        assert retrieved is not None
        # Note: failure_count still increments, just no eviction
        assert retrieved.failure_count == 10
        assert retrieved.health_status == HealthStatus.UNHEALTHY

        # Close manager

    def test_custom_failure_threshold(self, cache_config: CacheConfig, encryption_key: str) -> None:
        """Test custom failure threshold is respected.

        Scenario:
        1. Configure cache with failure_threshold=5
        2. Add proxy and mark unhealthy 4 times
        3. Verify proxy still present (below threshold)
        4. Mark unhealthy 5th time
        5. Verify proxy removed (reached threshold)
        """
        # Set higher threshold
        cache_config.failure_threshold = 5
        manager = CacheManager(cache_config)

        entry = _create_entry("proxy7.example.com:8080", encryption_key)
        manager.put(entry.key, entry)

        # Mark unhealthy 4 times (below threshold)
        for _ in range(4):
            manager.invalidate_by_health(entry.key)

        retrieved = manager.get(entry.key)
        assert retrieved is not None
        assert retrieved.failure_count == 4

        # 5th time reaches threshold
        manager.invalidate_by_health(entry.key)
        assert manager.get(entry.key) is None

        # Close manager
