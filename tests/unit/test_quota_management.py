"""Tests for quota management system."""

from datetime import datetime, timedelta, timezone

from proxywhirl.quota_management import (
    QuotaConfig,
    QuotaLimit,
    QuotaManager,
    QuotaPeriod,
    QuotaType,
    QuotaUsage,
)


class TestQuotaLimit:
    """Test QuotaLimit dataclass."""

    def test_is_exceeded(self):
        """Test quota exceeded check."""
        limit = QuotaLimit(limit=100, period=QuotaPeriod.DAILY, enforce=True)
        assert not limit.is_exceeded(50)
        assert not limit.is_exceeded(99)
        assert limit.is_exceeded(101)

    def test_is_exceeded_not_enforced(self):
        """Test that non-enforced limits don't trigger exceeded."""
        limit = QuotaLimit(limit=100, period=QuotaPeriod.DAILY, enforce=False)
        assert not limit.is_exceeded(500)

    def test_warning_level(self):
        """Test warning threshold check."""
        limit = QuotaLimit(limit=100, period=QuotaPeriod.DAILY, warning_threshold=0.8)
        assert not limit.warning_level(79)
        assert limit.warning_level(80)
        assert limit.warning_level(90)


class TestQuotaUsage:
    """Test QuotaUsage dataclass."""

    def test_increment(self):
        """Test usage increment."""
        usage = QuotaUsage(quota_type=QuotaType.REQUESTS, limit=100)
        assert usage.current_usage == 0
        usage.increment()
        assert usage.current_usage == 1
        usage.increment(5)
        assert usage.current_usage == 6

    def test_percentage_used(self):
        """Test percentage calculation."""
        usage = QuotaUsage(quota_type=QuotaType.REQUESTS, limit=100)
        usage.current_usage = 0
        assert usage.percentage_used() == 0.0
        usage.current_usage = 50
        assert usage.percentage_used() == 50.0
        usage.current_usage = 100
        assert usage.percentage_used() == 100.0

    def test_should_reset_hourly(self):
        """Test reset detection for hourly quota."""
        usage = QuotaUsage(
            quota_type=QuotaType.REQUESTS,
            limit=100,
            period=QuotaPeriod.HOURLY,
        )
        assert not usage.should_reset()
        usage.last_reset = datetime.now(timezone.utc) - timedelta(hours=2)
        assert usage.should_reset()

    def test_should_reset_daily(self):
        """Test reset detection for daily quota."""
        usage = QuotaUsage(
            quota_type=QuotaType.REQUESTS,
            limit=100,
            period=QuotaPeriod.DAILY,
        )
        assert not usage.should_reset()
        usage.last_reset = datetime.now(timezone.utc) - timedelta(days=2)
        assert usage.should_reset()

    def test_reset(self):
        """Test usage reset."""
        usage = QuotaUsage(quota_type=QuotaType.REQUESTS, limit=100)
        usage.current_usage = 50
        old_reset_time = usage.last_reset
        usage.reset()
        assert usage.current_usage == 0
        assert usage.last_reset > old_reset_time


class TestQuotaManager:
    """Test QuotaManager."""

    def test_register_quota(self):
        """Test quota registration."""
        manager = QuotaManager()
        config = QuotaConfig(
            quota_type=QuotaType.REQUESTS,
            limit=100,
            period=QuotaPeriod.DAILY,
        )
        manager.register_quota("user1", config)
        usage = manager.get_usage("user1", QuotaType.REQUESTS)
        assert usage is not None
        assert usage.limit == 100

    def test_consume_quota_success(self):
        """Test successful quota consumption."""
        manager = QuotaManager()
        config = QuotaConfig(
            quota_type=QuotaType.REQUESTS,
            limit=100,
            period=QuotaPeriod.DAILY,
        )
        manager.register_quota("user1", config)
        assert manager.consume_quota("user1", QuotaType.REQUESTS, 50)
        usage = manager.get_usage("user1", QuotaType.REQUESTS)
        assert usage.current_usage == 50

    def test_consume_quota_exceeded(self):
        """Test quota exceeded on consumption."""
        manager = QuotaManager()
        config = QuotaConfig(
            quota_type=QuotaType.REQUESTS,
            limit=100,
            period=QuotaPeriod.DAILY,
            enforce=True,
        )
        manager.register_quota("user1", config)
        manager.consume_quota("user1", QuotaType.REQUESTS, 100)
        assert not manager.consume_quota("user1", QuotaType.REQUESTS, 1)

    def test_consume_quota_not_registered(self):
        """Test consumption for unregistered entity."""
        manager = QuotaManager()
        assert not manager.consume_quota("user1", QuotaType.REQUESTS)

    def test_reset_quota(self):
        """Test manual quota reset."""
        manager = QuotaManager()
        config = QuotaConfig(
            quota_type=QuotaType.REQUESTS,
            limit=100,
            period=QuotaPeriod.DAILY,
        )
        manager.register_quota("user1", config)
        manager.consume_quota("user1", QuotaType.REQUESTS, 50)
        assert manager.reset_quota("user1", QuotaType.REQUESTS)
        usage = manager.get_usage("user1", QuotaType.REQUESTS)
        assert usage.current_usage == 0

    def test_set_limit(self):
        """Test updating quota limits."""
        manager = QuotaManager()
        manager.set_limit(QuotaType.REQUESTS, 200, QuotaPeriod.HOURLY)
        assert manager._limits[QuotaType.REQUESTS].limit == 200

    def test_export_metrics(self):
        """Test metrics export."""
        manager = QuotaManager()
        config = QuotaConfig(
            quota_type=QuotaType.REQUESTS,
            limit=100,
            period=QuotaPeriod.DAILY,
        )
        manager.register_quota("user1", config)
        manager.consume_quota("user1", QuotaType.REQUESTS, 25)
        metrics = manager.export_metrics("user1")
        assert "requests" in metrics
        assert metrics["requests"]["current_usage"] == 25
        assert metrics["requests"]["percentage_used"] == 25.0

    def test_get_all_usage(self):
        """Test getting all usage for an entity."""
        manager = QuotaManager()
        config1 = QuotaConfig(
            quota_type=QuotaType.REQUESTS,
            limit=100,
            period=QuotaPeriod.DAILY,
        )
        config2 = QuotaConfig(
            quota_type=QuotaType.BANDWIDTH,
            limit=1000,
            period=QuotaPeriod.DAILY,
        )
        manager.register_quota("user1", config1)
        manager.register_quota("user1", config2)
        all_usage = manager.get_all_usage("user1")
        assert len(all_usage) == 2
        assert QuotaType.REQUESTS in all_usage
        assert QuotaType.BANDWIDTH in all_usage
