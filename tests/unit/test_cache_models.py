"""Unit tests for cache models (health status, enums, validation).

Tests the health status infrastructure including:
- HealthStatus enum values
- CacheEntry health_status field
- failure_count tracking
- is_healthy property
"""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import SecretStr, ValidationError

from proxywhirl.cache_models import (
    CacheConfig,
    CacheEntry,
    CacheStatistics,
    CacheTierConfig,
    HealthStatus,
    TierStatistics,
)


@pytest.fixture
def sample_entry() -> CacheEntry:
    """Create a sample cache entry for testing."""
    now = datetime.now(timezone.utc)
    return CacheEntry(
        key="proxy.example.com:8080",
        proxy_url="http://proxy.example.com:8080",
        username=SecretStr("testuser"),
        password=SecretStr("testpass123"),
        source="test_source",
        fetch_time=now,
        last_accessed=now,
        ttl_seconds=3600,
        expires_at=now + timedelta(seconds=3600),
    )


def _create_entry(health_status: HealthStatus = HealthStatus.UNKNOWN) -> CacheEntry:
    """Helper to create cache entry with specific health status."""
    now = datetime.now(timezone.utc)
    return CacheEntry(
        key="proxy.example.com:8080",
        proxy_url="http://proxy.example.com:8080",
        username=SecretStr("testuser"),
        password=SecretStr("testpass123"),
        source="test_source",
        fetch_time=now,
        last_accessed=now,
        ttl_seconds=3600,
        expires_at=now + timedelta(seconds=3600),
        health_status=health_status,
    )


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_health_status_values(self) -> None:
        """Test HealthStatus enum has all expected values."""
        assert HealthStatus.HEALTHY == "healthy"
        assert HealthStatus.UNHEALTHY == "unhealthy"
        assert HealthStatus.UNKNOWN == "unknown"

    def test_health_status_from_string(self) -> None:
        """Test HealthStatus can be created from string values."""
        assert HealthStatus("healthy") == HealthStatus.HEALTHY
        assert HealthStatus("unhealthy") == HealthStatus.UNHEALTHY
        assert HealthStatus("unknown") == HealthStatus.UNKNOWN

    def test_health_status_invalid_value(self) -> None:
        """Test HealthStatus rejects invalid values."""
        with pytest.raises(ValueError):
            HealthStatus("invalid")


class TestCacheEntryHealthFields:
    """Tests for CacheEntry health-related fields."""

    def test_default_health_status(self, sample_entry: CacheEntry) -> None:
        """Test CacheEntry defaults to UNKNOWN health status."""
        assert sample_entry.health_status == HealthStatus.UNKNOWN

    def test_default_failure_count(self, sample_entry: CacheEntry) -> None:
        """Test CacheEntry defaults to 0 failure count."""
        assert sample_entry.failure_count == 0

    def test_set_health_status_healthy(self) -> None:
        """Test setting health_status to HEALTHY."""
        entry = _create_entry(health_status=HealthStatus.HEALTHY)
        assert entry.health_status == HealthStatus.HEALTHY

    def test_set_health_status_unhealthy(self) -> None:
        """Test setting health_status to UNHEALTHY."""
        entry = _create_entry(health_status=HealthStatus.UNHEALTHY)
        assert entry.health_status == HealthStatus.UNHEALTHY

    def test_increment_failure_count(self, sample_entry: CacheEntry) -> None:
        """Test incrementing failure_count."""
        assert sample_entry.failure_count == 0

        # Create new entry with incremented count (Pydantic models are immutable)
        updated = sample_entry.model_copy(update={"failure_count": 1})
        assert updated.failure_count == 1

        updated = updated.model_copy(update={"failure_count": 2})
        assert updated.failure_count == 2

    def test_failure_count_validation_negative(self) -> None:
        """Test failure_count validation rejects negative values."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError):
            CacheEntry(
                key="proxy.example.com:8080",
                proxy_url="http://proxy.example.com:8080",
                username=SecretStr("testuser"),
                password=SecretStr("testpass123"),
                source="test_source",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
                failure_count=-1,
            )

    def test_is_healthy_property_when_healthy(self) -> None:
        """Test is_healthy property returns True when health_status is HEALTHY."""
        entry = _create_entry(health_status=HealthStatus.HEALTHY)
        assert entry.is_healthy is True

    def test_is_healthy_property_when_unhealthy(self) -> None:
        """Test is_healthy property returns False when health_status is UNHEALTHY."""
        entry = _create_entry(health_status=HealthStatus.UNHEALTHY)
        assert entry.is_healthy is False

    def test_is_healthy_property_when_unknown(self, sample_entry: CacheEntry) -> None:
        """Test is_healthy property returns False when health_status is UNKNOWN."""
        assert sample_entry.health_status == HealthStatus.UNKNOWN
        assert sample_entry.is_healthy is False


class TestCacheConfigHealthSettings:
    """Tests for CacheConfig health-related settings."""

    def test_default_health_check_invalidation(self) -> None:
        """Test default health_check_invalidation is True."""
        config = CacheConfig(encryption_key=SecretStr("test_key_32_chars_long_______"))
        assert config.health_check_invalidation is True

    def test_default_failure_threshold(self) -> None:
        """Test default failure_threshold is 3."""
        config = CacheConfig(encryption_key=SecretStr("test_key_32_chars_long_______"))
        assert config.failure_threshold == 3

    def test_custom_failure_threshold(self) -> None:
        """Test setting custom failure_threshold."""
        config = CacheConfig(
            encryption_key=SecretStr("test_key_32_chars_long_______"), failure_threshold=5
        )
        assert config.failure_threshold == 5

    def test_disable_health_check_invalidation(self) -> None:
        """Test disabling health_check_invalidation."""
        config = CacheConfig(
            encryption_key=SecretStr("test_key_32_chars_long_______"),
            health_check_invalidation=False,
        )
        assert config.health_check_invalidation is False

    def test_failure_threshold_validation(self) -> None:
        """Test failure_threshold must be >= 1."""
        with pytest.raises(ValidationError):
            CacheConfig(
                encryption_key=SecretStr("test_key_32_chars_long_______"), failure_threshold=0
            )

        with pytest.raises(ValidationError):
            CacheConfig(
                encryption_key=SecretStr("test_key_32_chars_long_______"), failure_threshold=-1
            )


class TestCacheTierConfig:
    """Tests for CacheTierConfig model."""

    def test_default_values(self) -> None:
        """Test CacheTierConfig default values."""
        config = CacheTierConfig()
        assert config.enabled is True
        assert config.max_entries is None
        assert config.eviction_policy == "lru"

    def test_valid_eviction_policies(self) -> None:
        """Test all valid eviction policies are accepted."""
        for policy in ["lru", "lfu", "fifo"]:
            config = CacheTierConfig(eviction_policy=policy)
            assert config.eviction_policy == policy

    def test_invalid_eviction_policy_raises(self) -> None:
        """Test invalid eviction policy raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid eviction policy"):
            CacheTierConfig(eviction_policy="invalid_policy")

    def test_custom_max_entries(self) -> None:
        """Test setting custom max_entries."""
        config = CacheTierConfig(max_entries=5000)
        assert config.max_entries == 5000

    def test_disabled_tier(self) -> None:
        """Test disabling a tier."""
        config = CacheTierConfig(enabled=False)
        assert config.enabled is False


class TestTierStatistics:
    """Tests for TierStatistics model."""

    def test_default_values(self) -> None:
        """Test TierStatistics default values."""
        stats = TierStatistics()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.current_size == 0

    def test_hit_rate_with_hits(self) -> None:
        """Test hit_rate computation with hits."""
        stats = TierStatistics(hits=80, misses=20)
        assert stats.hit_rate == 0.8

    def test_hit_rate_with_no_requests(self) -> None:
        """Test hit_rate returns 0.0 when no requests."""
        stats = TierStatistics(hits=0, misses=0)
        assert stats.hit_rate == 0.0

    def test_hit_rate_all_hits(self) -> None:
        """Test hit_rate returns 1.0 when all hits."""
        stats = TierStatistics(hits=100, misses=0)
        assert stats.hit_rate == 1.0

    def test_hit_rate_all_misses(self) -> None:
        """Test hit_rate returns 0.0 when all misses."""
        stats = TierStatistics(hits=0, misses=100)
        assert stats.hit_rate == 0.0

    def test_total_evictions(self) -> None:
        """Test total_evictions computed field."""
        stats = TierStatistics(
            evictions_lru=10,
            evictions_ttl=5,
            evictions_health=3,
            evictions_corruption=2,
        )
        assert stats.total_evictions == 20

    def test_total_evictions_zero(self) -> None:
        """Test total_evictions returns 0 when no evictions."""
        stats = TierStatistics()
        assert stats.total_evictions == 0


class TestCacheStatistics:
    """Tests for CacheStatistics model."""

    def test_default_values(self) -> None:
        """Test CacheStatistics default values."""
        stats = CacheStatistics()
        assert stats.promotions == 0
        assert stats.demotions == 0
        assert stats.l1_degraded is False
        assert stats.l2_degraded is False
        assert stats.l3_degraded is False

    def test_overall_hit_rate_with_hits(self) -> None:
        """Test overall_hit_rate computed across all tiers.

        Note: Uses max() of tier misses to avoid triple-counting since
        each miss cascades through all tiers.
        """
        stats = CacheStatistics(
            l1_stats=TierStatistics(hits=50, misses=10),
            l2_stats=TierStatistics(hits=30, misses=5),
            l3_stats=TierStatistics(hits=20, misses=5),
        )
        # Total hits: 100, Max misses: 10 (L1), Total requests: 110
        # Hit rate: 100/110 = 0.909...
        expected = 100 / 110
        assert abs(stats.overall_hit_rate - expected) < 0.001

    def test_overall_hit_rate_no_requests(self) -> None:
        """Test overall_hit_rate returns 0.0 when no requests."""
        stats = CacheStatistics()
        assert stats.overall_hit_rate == 0.0

    def test_total_size(self) -> None:
        """Test total_size computed across all tiers."""
        stats = CacheStatistics(
            l1_stats=TierStatistics(current_size=100),
            l2_stats=TierStatistics(current_size=500),
            l3_stats=TierStatistics(current_size=1000),
        )
        assert stats.total_size == 1600

    def test_total_size_zero(self) -> None:
        """Test total_size returns 0 when empty."""
        stats = CacheStatistics()
        assert stats.total_size == 0

    def test_to_metrics_dict(self) -> None:
        """Test to_metrics_dict returns correct format."""
        stats = CacheStatistics(
            l1_stats=TierStatistics(hits=80, misses=20, current_size=100),
            l2_stats=TierStatistics(hits=40, misses=10, current_size=500),
            l3_stats=TierStatistics(hits=20, misses=5, current_size=1000),
            promotions=15,
            demotions=5,
        )
        metrics = stats.to_metrics_dict()

        assert "cache.l1.hit_rate" in metrics
        assert "cache.l2.hit_rate" in metrics
        assert "cache.l3.hit_rate" in metrics
        assert "cache.overall.hit_rate" in metrics
        assert "cache.total_size" in metrics
        assert "cache.promotions" in metrics
        assert "cache.demotions" in metrics
        assert "cache.l1.size" in metrics
        assert "cache.l2.size" in metrics
        assert "cache.l3.size" in metrics

        assert metrics["cache.l1.hit_rate"] == 0.8
        assert metrics["cache.promotions"] == 15.0
        assert metrics["cache.demotions"] == 5.0
        assert metrics["cache.total_size"] == 1600.0
