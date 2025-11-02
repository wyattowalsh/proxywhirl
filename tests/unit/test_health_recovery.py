"""Tests for automatic proxy recovery (US5)."""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from proxywhirl.health import HealthChecker
from proxywhirl.health_models import HealthCheckConfig, HealthStatus


class TestRecoveryCooldown:
    """Tests for exponential backoff calculation (T067)."""

    def test_calculate_recovery_cooldown_exponential(self) -> None:
        """Test that cooldown doubles on each retry."""
        config = HealthCheckConfig(recovery_cooldown_base_seconds=60)
        checker = HealthChecker(config=config)

        # Attempt 0: 60 * 2^0 = 60 seconds
        assert checker._calculate_recovery_cooldown(0) == 60

        # Attempt 1: 60 * 2^1 = 120 seconds
        assert checker._calculate_recovery_cooldown(1) == 120

        # Attempt 2: 60 * 2^2 = 240 seconds
        assert checker._calculate_recovery_cooldown(2) == 240

        # Attempt 3: 60 * 2^3 = 480 seconds
        assert checker._calculate_recovery_cooldown(3) == 480

    def test_calculate_recovery_cooldown_capped(self) -> None:
        """Test that cooldown is capped at maximum."""
        config = HealthCheckConfig(recovery_cooldown_base_seconds=60)
        checker = HealthChecker(config=config)

        # Large attempt number should be capped at 3600 seconds (1 hour)
        cooldown = checker._calculate_recovery_cooldown(20)
        assert cooldown == 3600


class TestRecoveryAttemptTracking:
    """Tests for recovery attempt tracking (T068)."""

    def test_recovery_attempt_increments(self) -> None:
        """Test that recovery_attempt increments on each failure."""
        checker = HealthChecker()
        checker.add_proxy("http://proxy1.example.com:8080", source="test")

        # Schedule recovery
        checker._schedule_recovery("http://proxy1.example.com:8080")
        assert checker._proxies["http://proxy1.example.com:8080"]["recovery_attempt"] == 1

        # Schedule again
        checker._schedule_recovery("http://proxy1.example.com:8080")
        assert checker._proxies["http://proxy1.example.com:8080"]["recovery_attempt"] == 2

    def test_recovery_attempt_resets_on_success(self) -> None:
        """Test that recovery_attempt resets on successful recovery."""
        checker = HealthChecker()
        checker.add_proxy("http://proxy1.example.com:8080", source="test")

        # Set up for recovery
        checker._proxies["http://proxy1.example.com:8080"]["recovery_attempt"] = 3
        checker._proxies["http://proxy1.example.com:8080"][
            "health_status"
        ] = HealthStatus.RECOVERING

        # Mock successful check
        with patch.object(checker, "check_proxy") as mock_check:
            mock_check.return_value = Mock(
                status=HealthStatus.HEALTHY,
                proxy_url="http://proxy1.example.com:8080",
                check_time=datetime.now(timezone.utc),
                check_url="http://www.google.com",
            )

            checker._attempt_recovery("http://proxy1.example.com:8080")

        # Recovery attempt should be reset
        assert checker._proxies["http://proxy1.example.com:8080"]["recovery_attempt"] == 0
        assert (
            checker._proxies["http://proxy1.example.com:8080"]["health_status"]
            == HealthStatus.HEALTHY
        )


class TestMaxRecoveryAttempts:
    """Tests for permanent failure after max retries (T069)."""

    def test_permanent_failure_after_max_attempts(self) -> None:
        """Test that proxy is marked PERMANENTLY_FAILED after max retries."""
        config = HealthCheckConfig(max_recovery_attempts=3)
        checker = HealthChecker(config=config)
        checker.add_proxy("http://proxy1.example.com:8080", source="test")

        # Set recovery attempts to max
        checker._proxies["http://proxy1.example.com:8080"]["recovery_attempt"] = 3

        # Mock failed check
        with patch.object(checker, "check_proxy") as mock_check:
            mock_check.return_value = Mock(
                status=HealthStatus.UNHEALTHY,
                proxy_url="http://proxy1.example.com:8080",
                check_time=datetime.now(timezone.utc),
                check_url="http://www.google.com",
            )

            checker._attempt_recovery("http://proxy1.example.com:8080")

        # Should be permanently failed
        assert (
            checker._proxies["http://proxy1.example.com:8080"]["health_status"]
            == HealthStatus.PERMANENTLY_FAILED
        )


class TestRecoveryCooldownScheduling:
    """Tests for recovery cooldown scheduling (T070)."""

    def test_next_check_time_calculated(self) -> None:
        """Test that next_check_time is calculated correctly."""
        checker = HealthChecker()
        checker.add_proxy("http://proxy1.example.com:8080", source="test")

        before_schedule = datetime.now(timezone.utc)
        checker._schedule_recovery("http://proxy1.example.com:8080")
        after_schedule = datetime.now(timezone.utc)

        next_check = checker._proxies["http://proxy1.example.com:8080"]["next_check_time"]
        assert next_check is not None

        # Should be in the future (at least base cooldown)
        assert next_check > before_schedule
        # But not too far in the future
        assert next_check < after_schedule + timedelta(hours=2)

    def test_recovery_status_set(self) -> None:
        """Test that status is set to RECOVERING when scheduled."""
        checker = HealthChecker()
        checker.add_proxy("http://proxy1.example.com:8080", source="test")

        checker._schedule_recovery("http://proxy1.example.com:8080")

        assert (
            checker._proxies["http://proxy1.example.com:8080"]["health_status"]
            == HealthStatus.RECOVERING
        )
