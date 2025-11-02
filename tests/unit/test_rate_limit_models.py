"""
Unit tests for rate limit Pydantic models.

Tests validation, computed fields, and configuration loading.
"""

import ipaddress
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml
from pydantic import SecretStr, ValidationError

from proxywhirl.rate_limit_models import (
    RateLimitConfig,
    RateLimitMetrics,
    RateLimitResult,
    RateLimitState,
    RateLimitTierConfig,
)


class TestRateLimitTierConfig:
    """Tests for RateLimitTierConfig model."""

    def test_valid_tier_config(self) -> None:
        """Test creating valid tier configuration."""
        tier = RateLimitTierConfig(
            name="free",
            requests_per_window=100,
            window_size_seconds=60,
            description="Free tier",
        )
        assert tier.name == "free"
        assert tier.requests_per_window == 100
        assert tier.window_size_seconds == 60
        assert tier.endpoints == {}

    def test_tier_config_with_endpoints(self) -> None:
        """Test tier configuration with endpoint overrides."""
        tier = RateLimitTierConfig(
            name="premium",
            requests_per_window=1000,
            window_size_seconds=60,
            endpoints={"/api/v1/request": 50, "/api/v1/health": 100},
        )
        assert tier.endpoints["/api/v1/request"] == 50
        assert tier.endpoints["/api/v1/health"] == 100

    def test_tier_name_validation_alphanumeric(self) -> None:
        """Test tier name must be alphanumeric + underscore."""
        with pytest.raises(ValidationError, match="pattern"):
            RateLimitTierConfig(
                name="premium tier",  # Space not allowed
                requests_per_window=100,
                window_size_seconds=60,
            )

    def test_tier_requests_per_window_positive(self) -> None:
        """Test requests_per_window must be positive."""
        with pytest.raises(ValidationError, match="greater than 0"):
            RateLimitTierConfig(
                name="free", requests_per_window=0, window_size_seconds=60
            )

    def test_tier_window_size_range(self) -> None:
        """Test window_size_seconds must be in [1, 3600]."""
        # Too small
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            RateLimitTierConfig(
                name="free", requests_per_window=100, window_size_seconds=0
            )

        # Too large
        with pytest.raises(ValidationError, match="less than or equal to 3600"):
            RateLimitTierConfig(
                name="free", requests_per_window=100, window_size_seconds=3601
            )

    def test_endpoint_path_must_start_with_slash(self) -> None:
        """Test endpoint paths must start with '/'."""
        with pytest.raises(ValidationError, match="must start with"):
            RateLimitTierConfig(
                name="free",
                requests_per_window=100,
                window_size_seconds=60,
                endpoints={"api/v1/request": 50},  # Missing leading '/'
            )

    def test_endpoint_limit_must_be_positive(self) -> None:
        """Test endpoint limits must be positive."""
        with pytest.raises(ValidationError, match="must be positive"):
            RateLimitTierConfig(
                name="free",
                requests_per_window=100,
                window_size_seconds=60,
                endpoints={"/api/v1/request": 0},  # Zero not allowed
            )


class TestRateLimitConfig:
    """Tests for RateLimitConfig model."""

    def test_valid_config(self) -> None:
        """Test creating valid rate limit configuration."""
        config = RateLimitConfig(
            enabled=True,
            default_tier="free",
            tiers=[
                RateLimitTierConfig(
                    name="free", requests_per_window=100, window_size_seconds=60
                )
            ],
        )
        assert config.enabled is True
        assert config.default_tier == "free"
        assert len(config.tiers) == 1

    def test_default_tier_must_exist(self) -> None:
        """Test default_tier must exist in tiers list."""
        with pytest.raises(ValidationError, match="not found in tiers"):
            RateLimitConfig(
                default_tier="nonexistent",
                tiers=[
                    RateLimitTierConfig(
                        name="free", requests_per_window=100, window_size_seconds=60
                    )
                ],
            )

    def test_whitelist_validation_uuid(self) -> None:
        """Test whitelist accepts valid UUIDs."""
        config = RateLimitConfig(
            tiers=[
                RateLimitTierConfig(
                    name="free", requests_per_window=100, window_size_seconds=60
                )
            ],
            whitelist=["550e8400-e29b-41d4-a716-446655440000"],
        )
        assert len(config.whitelist) == 1

    def test_whitelist_validation_ip(self) -> None:
        """Test whitelist accepts valid IP addresses."""
        config = RateLimitConfig(
            tiers=[
                RateLimitTierConfig(
                    name="free", requests_per_window=100, window_size_seconds=60
                )
            ],
            whitelist=["192.168.1.100", "::1"],
        )
        assert len(config.whitelist) == 2

    def test_whitelist_validation_invalid(self) -> None:
        """Test whitelist rejects invalid entries."""
        with pytest.raises(ValidationError, match="Invalid whitelist entry"):
            RateLimitConfig(
                tiers=[
                    RateLimitTierConfig(
                        name="free", requests_per_window=100, window_size_seconds=60
                    )
                ],
                whitelist=["not-a-uuid-or-ip"],
            )

    def test_from_yaml(self) -> None:
        """Test loading configuration from YAML file."""
        yaml_content = """
enabled: true
default_tier: free
tiers:
  - name: free
    requests_per_window: 100
    window_size_seconds: 60
    endpoints:
      /api/v1/request: 50
  - name: premium
    requests_per_window: 1000
    window_size_seconds: 60
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            config_path = Path(f.name)

        try:
            config = RateLimitConfig.from_yaml(config_path)
            assert config.enabled is True
            assert config.default_tier == "free"
            assert len(config.tiers) == 2
            assert config.tiers[0].name == "free"
            assert config.tiers[1].name == "premium"
        finally:
            config_path.unlink()

    def test_from_yaml_file_not_found(self) -> None:
        """Test from_yaml raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            RateLimitConfig.from_yaml("/nonexistent/config.yaml")

    def test_get_tier_config(self) -> None:
        """Test retrieving tier configuration by name."""
        config = RateLimitConfig(
            tiers=[
                RateLimitTierConfig(
                    name="free", requests_per_window=100, window_size_seconds=60
                ),
                RateLimitTierConfig(
                    name="premium", requests_per_window=1000, window_size_seconds=60
                ),
            ]
        )
        free_tier = config.get_tier_config("free")
        assert free_tier is not None
        assert free_tier.name == "free"
        assert free_tier.requests_per_window == 100

        nonexistent = config.get_tier_config("nonexistent")
        assert nonexistent is None


class TestRateLimitState:
    """Tests for RateLimitState model."""

    def test_valid_state(self) -> None:
        """Test creating valid rate limit state."""
        now = datetime.now(timezone.utc)
        reset_at = now + timedelta(seconds=60)
        state = RateLimitState(
            key="ratelimit:user123:/api/v1/request",
            identifier="550e8400-e29b-41d4-a716-446655440000",
            endpoint="/api/v1/request",
            tier="free",
            current_count=42,
            limit=100,
            window_start_ms=int(now.timestamp() * 1000),
            window_size_seconds=60,
            reset_at=reset_at,
        )
        assert state.identifier == "550e8400-e29b-41d4-a716-446655440000"
        assert state.current_count == 42
        assert state.limit == 100

    def test_computed_remaining(self) -> None:
        """Test computed 'remaining' property."""
        now = datetime.now(timezone.utc)
        state = RateLimitState(
            key="ratelimit:user123:/test",
            identifier="550e8400-e29b-41d4-a716-446655440000",
            endpoint="/test",
            tier="free",
            current_count=42,
            limit=100,
            window_start_ms=int(now.timestamp() * 1000),
            window_size_seconds=60,
            reset_at=now + timedelta(seconds=60),
        )
        assert state.remaining == 58  # 100 - 42

    def test_computed_is_exceeded(self) -> None:
        """Test computed 'is_exceeded' property."""
        now = datetime.now(timezone.utc)
        # Not exceeded
        state = RateLimitState(
            key="ratelimit:user123:/test",
            identifier="550e8400-e29b-41d4-a716-446655440000",
            endpoint="/test",
            tier="free",
            current_count=99,
            limit=100,
            window_start_ms=int(now.timestamp() * 1000),
            window_size_seconds=60,
            reset_at=now + timedelta(seconds=60),
        )
        assert state.is_exceeded is False

        # Exactly at limit (exceeded)
        state.current_count = 100
        assert state.is_exceeded is True

    def test_computed_retry_after_seconds(self) -> None:
        """Test computed 'retry_after_seconds' property."""
        now = datetime.now(timezone.utc)
        reset_at = now + timedelta(seconds=30)
        state = RateLimitState(
            key="ratelimit:user123:/test",
            identifier="550e8400-e29b-41d4-a716-446655440000",
            endpoint="/test",
            tier="free",
            current_count=100,
            limit=100,
            window_start_ms=int(now.timestamp() * 1000),
            window_size_seconds=60,
            reset_at=reset_at,
        )
        # Should be approximately 30 seconds
        assert 28 <= state.retry_after_seconds <= 30

    def test_identifier_validation_uuid(self) -> None:
        """Test identifier accepts valid UUID."""
        now = datetime.now(timezone.utc)
        state = RateLimitState(
            key="ratelimit:user123:/test",
            identifier="550e8400-e29b-41d4-a716-446655440000",
            endpoint="/test",
            tier="free",
            current_count=0,
            limit=100,
            window_start_ms=int(now.timestamp() * 1000),
            window_size_seconds=60,
            reset_at=now + timedelta(seconds=60),
        )
        assert state.identifier == "550e8400-e29b-41d4-a716-446655440000"

    def test_identifier_validation_ip(self) -> None:
        """Test identifier accepts valid IP address."""
        now = datetime.now(timezone.utc)
        state = RateLimitState(
            key="ratelimit:192.168.1.100:/test",
            identifier="192.168.1.100",
            endpoint="/test",
            tier="free",
            current_count=0,
            limit=100,
            window_start_ms=int(now.timestamp() * 1000),
            window_size_seconds=60,
            reset_at=now + timedelta(seconds=60),
        )
        assert state.identifier == "192.168.1.100"

    def test_identifier_validation_invalid(self) -> None:
        """Test identifier rejects invalid values."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError, match="Invalid identifier"):
            RateLimitState(
                key="ratelimit:invalid:/test",
                identifier="not-a-uuid-or-ip",
                endpoint="/test",
                tier="free",
                current_count=0,
                limit=100,
                window_start_ms=int(now.timestamp() * 1000),
                window_size_seconds=60,
                reset_at=now + timedelta(seconds=60),
            )

    def test_endpoint_validation(self) -> None:
        """Test endpoint must start with '/'."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError, match="must start with"):
            RateLimitState(
                key="ratelimit:user123:test",
                identifier="550e8400-e29b-41d4-a716-446655440000",
                endpoint="test",  # Missing '/'
                tier="free",
                current_count=0,
                limit=100,
                window_start_ms=int(now.timestamp() * 1000),
                window_size_seconds=60,
                reset_at=now + timedelta(seconds=60),
            )


class TestRateLimitResult:
    """Tests for RateLimitResult model."""

    def test_valid_allowed_result(self) -> None:
        """Test creating valid allowed result."""
        now = datetime.now(timezone.utc)
        state = RateLimitState(
            key="ratelimit:user123:/test",
            identifier="550e8400-e29b-41d4-a716-446655440000",
            endpoint="/test",
            tier="free",
            current_count=42,
            limit=100,
            window_start_ms=int(now.timestamp() * 1000),
            window_size_seconds=60,
            reset_at=now + timedelta(seconds=60),
        )
        result = RateLimitResult(allowed=True, state=state)
        assert result.allowed is True
        assert result.reason is None

    def test_valid_denied_result(self) -> None:
        """Test creating valid denied result."""
        now = datetime.now(timezone.utc)
        state = RateLimitState(
            key="ratelimit:user123:/test",
            identifier="550e8400-e29b-41d4-a716-446655440000",
            endpoint="/test",
            tier="free",
            current_count=100,
            limit=100,
            window_start_ms=int(now.timestamp() * 1000),
            window_size_seconds=60,
            reset_at=now + timedelta(seconds=60),
        )
        result = RateLimitResult(allowed=False, state=state, reason="rate_limit_exceeded")
        assert result.allowed is False
        assert result.reason == "rate_limit_exceeded"

    def test_reason_required_when_denied(self) -> None:
        """Test reason is required when allowed=False."""
        now = datetime.now(timezone.utc)
        state = RateLimitState(
            key="ratelimit:user123:/test",
            identifier="550e8400-e29b-41d4-a716-446655440000",
            endpoint="/test",
            tier="free",
            current_count=100,
            limit=100,
            window_start_ms=int(now.timestamp() * 1000),
            window_size_seconds=60,
            reset_at=now + timedelta(seconds=60),
        )
        with pytest.raises(ValidationError, match="reason required"):
            RateLimitResult(allowed=False, state=state)  # Missing reason


class TestRateLimitMetrics:
    """Tests for RateLimitMetrics model."""

    def test_valid_metrics(self) -> None:
        """Test creating valid metrics."""
        metrics = RateLimitMetrics(
            total_requests=1000,
            throttled_requests=50,
            allowed_requests=950,
            by_tier={"free": 30, "premium": 20},
            by_endpoint={"/api/v1/request": 40, "/api/v1/pool": 10},
            avg_check_latency_ms=2.5,
            p95_check_latency_ms=4.8,
            redis_errors=0,
        )
        assert metrics.total_requests == 1000
        assert metrics.throttled_requests == 50
        assert metrics.allowed_requests == 950

    def test_totals_validation(self) -> None:
        """Test throttled + allowed must equal total."""
        with pytest.raises(ValidationError, match="must equal total"):
            RateLimitMetrics(
                total_requests=1000,
                throttled_requests=50,
                allowed_requests=900,  # 50 + 900 != 1000
                avg_check_latency_ms=2.5,
                p95_check_latency_ms=4.8,
                redis_errors=0,
            )

    def test_non_negative_counts(self) -> None:
        """Test all counts must be non-negative."""
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            RateLimitMetrics(
                total_requests=-1,
                throttled_requests=0,
                allowed_requests=-1,
                avg_check_latency_ms=2.5,
                p95_check_latency_ms=4.8,
                redis_errors=0,
            )
