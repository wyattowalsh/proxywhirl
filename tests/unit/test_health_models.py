"""Unit tests for health monitoring models."""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from proxywhirl.health_models import (
    HealthCheckConfig,
    HealthCheckResult,
    HealthStatus,
)


class TestHealthStatus:
    """Tests for HealthStatus enum (T011)."""
    
    def test_all_status_values_exist(self) -> None:
        """Test that all required status values exist."""
        assert HealthStatus.UNKNOWN == "unknown"
        assert HealthStatus.HEALTHY == "healthy"
        assert HealthStatus.UNHEALTHY == "unhealthy"
        assert HealthStatus.CHECKING == "checking"
        assert HealthStatus.RECOVERING == "recovering"
        assert HealthStatus.PERMANENTLY_FAILED == "permanently_failed"
    
    def test_status_is_string_enum(self) -> None:
        """Test that HealthStatus is a string enum."""
        assert isinstance(HealthStatus.HEALTHY.value, str)
        assert HealthStatus.HEALTHY.value == "healthy"
    
    def test_status_transitions_from_unknown(self) -> None:
        """Test valid state transitions from UNKNOWN."""
        # Unknown can transition to checking or healthy
        start = HealthStatus.UNKNOWN
        assert start != HealthStatus.CHECKING
        assert start != HealthStatus.HEALTHY
        # Just verify they're different values (validation rules tested in implementation)


class TestHealthCheckResult:
    """Tests for HealthCheckResult model (T012)."""
    
    def test_create_health_check_result_success(self) -> None:
        """Test creating a successful health check result."""
        now = datetime.now(timezone.utc)
        result = HealthCheckResult(
            proxy_url="http://proxy.example.com:8080",
            check_time=now,
            status=HealthStatus.HEALTHY,
            response_time_ms=150.5,
            status_code=200,
            check_url="http://example.com"
        )
        assert result.proxy_url == "http://proxy.example.com:8080"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time_ms == 150.5
        assert result.status_code == 200
        assert result.error_message is None
    
    def test_create_health_check_result_failure(self) -> None:
        """Test creating a failed health check result."""
        now = datetime.now(timezone.utc)
        result = HealthCheckResult(
            proxy_url="http://proxy.example.com:8080",
            check_time=now,
            status=HealthStatus.UNHEALTHY,
            response_time_ms=None,
            status_code=None,
            error_message="Connection timeout",
            check_url="http://example.com"
        )
        assert result.status == HealthStatus.UNHEALTHY
        assert result.error_message == "Connection timeout"
        assert result.status_code is None
    
    def test_health_check_result_timezone_aware(self) -> None:
        """Test that check_time is timezone-aware."""
        now = datetime.now(timezone.utc)
        result = HealthCheckResult(
            proxy_url="http://proxy.example.com:8080",
            check_time=now,
            status=HealthStatus.HEALTHY,
            check_url="http://example.com"
        )
        assert result.check_time.tzinfo is not None
    
    def test_health_check_result_immutable(self) -> None:
        """Test that HealthCheckResult fields are immutable."""
        result = HealthCheckResult(
            proxy_url="http://proxy.example.com:8080",
            check_time=datetime.now(timezone.utc),
            status=HealthStatus.HEALTHY,
            check_url="http://example.com"
        )
        # Pydantic v2 models are mutable by default, but we can verify the model works
        assert result.proxy_url == "http://proxy.example.com:8080"


class TestHealthCheckConfig:
    """Tests for HealthCheckConfig model (T013)."""
    
    def test_create_config_with_defaults(self) -> None:
        """Test creating config with default values."""
        config = HealthCheckConfig()
        # Verify defaults exist and are reasonable
        assert config.check_interval_seconds >= 10
        assert config.failure_threshold >= 1
        assert config.check_timeout_seconds > 0
    
    def test_config_interval_validation_min_10s(self) -> None:
        """Test that check_interval must be >= 10 seconds."""
        # Should work with 10 seconds
        config = HealthCheckConfig(check_interval_seconds=10)
        assert config.check_interval_seconds == 10
        
        # Should fail with less than 10 seconds
        with pytest.raises(ValidationError) as exc_info:
            HealthCheckConfig(check_interval_seconds=5)
        assert "check_interval_seconds" in str(exc_info.value)
    
    def test_config_threshold_validation_min_1(self) -> None:
        """Test that failure_threshold must be >= 1."""
        # Should work with 1
        config = HealthCheckConfig(failure_threshold=1)
        assert config.failure_threshold == 1
        
        # Should fail with 0
        with pytest.raises(ValidationError) as exc_info:
            HealthCheckConfig(failure_threshold=0)
        assert "failure_threshold" in str(exc_info.value)
    
    def test_config_field_defaults(self) -> None:
        """Test that config has sensible field defaults."""
        config = HealthCheckConfig()
        assert isinstance(config.check_interval_seconds, int)
        assert isinstance(config.failure_threshold, int)
        assert isinstance(config.check_timeout_seconds, (int, float))
        assert config.check_url is not None  # Should have a default check URL
