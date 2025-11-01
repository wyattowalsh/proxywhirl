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
    HealthStatus,
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
