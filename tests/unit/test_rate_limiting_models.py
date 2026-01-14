"""
Unit tests for rate limiting models.
"""

from datetime import datetime, timezone

import pytest

from proxywhirl.rate_limiting.models import RateLimit, RateLimitEvent


class TestRateLimit:
    """Test RateLimit model."""

    def test_create_basic_rate_limit(self):
        """Test creating a basic rate limit."""
        limit = RateLimit(max_requests=100, time_window=60)

        assert limit.max_requests == 100
        assert limit.time_window == 60
        assert limit.burst_allowance is None

    def test_create_rate_limit_with_burst(self):
        """Test creating a rate limit with burst allowance."""
        limit = RateLimit(max_requests=100, time_window=60, burst_allowance=20)

        assert limit.max_requests == 100
        assert limit.time_window == 60
        assert limit.burst_allowance == 20

    def test_rate_limit_requires_max_requests(self):
        """Test that max_requests is required."""
        with pytest.raises(ValueError):
            RateLimit(time_window=60)  # type: ignore

    def test_rate_limit_requires_time_window(self):
        """Test that time_window is required."""
        with pytest.raises(ValueError):
            RateLimit(max_requests=100)  # type: ignore


class TestRateLimitEvent:
    """Test RateLimitEvent model."""

    def test_create_throttled_event(self):
        """Test creating a throttled event."""
        now = datetime.now(timezone.utc)
        event = RateLimitEvent(
            timestamp=now,
            proxy_id="proxy-123",
            event_type="throttled",
            details={"wait_time": 1.5},
        )

        assert event.timestamp == now
        assert event.proxy_id == "proxy-123"
        assert event.event_type == "throttled"
        assert event.details == {"wait_time": 1.5}

    def test_create_exceeded_event(self):
        """Test creating an exceeded event."""
        now = datetime.now(timezone.utc)
        event = RateLimitEvent(
            timestamp=now,
            proxy_id="proxy-456",
            event_type="exceeded",
            details={"current_count": 101, "max_allowed": 100},
        )

        assert event.event_type == "exceeded"
        assert event.details["current_count"] == 101

    def test_create_adaptive_change_event(self):
        """Test creating an adaptive change event."""
        now = datetime.now(timezone.utc)
        event = RateLimitEvent(
            timestamp=now,
            proxy_id="proxy-789",
            event_type="adaptive_change",
            details={"old_limit": 100, "new_limit": 80, "reason": "429 responses"},
        )

        assert event.event_type == "adaptive_change"
        assert event.details["old_limit"] == 100
        assert event.details["new_limit"] == 80
