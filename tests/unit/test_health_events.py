"""Tests for health event notifications (US6)."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from proxywhirl.health import HealthChecker
from proxywhirl.health_models import HealthCheckConfig, HealthEvent, HealthStatus


class TestHealthEvent:
    """Tests for HealthEvent model (T081)."""

    def test_health_event_creation(self) -> None:
        """Test creating a HealthEvent."""
        event = HealthEvent(
            event_type="proxy_down",
            proxy_url="http://proxy1.example.com:8080",
            source="premium",
            details={"consecutive_failures": 3},
        )

        assert event.event_type == "proxy_down"
        assert event.proxy_url == "http://proxy1.example.com:8080"
        assert event.source == "premium"
        assert event.details["consecutive_failures"] == 3
        assert event.timestamp is not None

    def test_health_event_severity(self) -> None:
        """Test HealthEvent severity property."""
        proxy_down = HealthEvent(event_type="proxy_down")
        assert proxy_down.severity == "warning"

        proxy_recovered = HealthEvent(event_type="proxy_recovered")
        assert proxy_recovered.severity == "info"

        pool_degraded = HealthEvent(event_type="pool_degraded")
        assert pool_degraded.severity == "critical"

        permanently_failed = HealthEvent(event_type="proxy_permanently_failed")
        assert permanently_failed.severity == "error"


class TestEventCallback:
    """Tests for event callback registration (T082)."""

    def test_callback_called_on_proxy_down(self) -> None:
        """Test that callback is called when proxy goes down."""
        callback = Mock()
        checker = HealthChecker(on_event=callback)
        checker.add_proxy("http://proxy1.example.com:8080", source="test")

        # Simulate failures to trigger proxy_down
        for _ in range(3):
            result = Mock(
                status=HealthStatus.UNHEALTHY,
                proxy_url="http://proxy1.example.com:8080",
                check_time=datetime.now(timezone.utc),
                check_url="http://www.google.com",
                error_message="Connection failed",
            )
            checker._update_health_status("http://proxy1.example.com:8080", result)

        # Callback should have been called - find proxy_down event
        assert callback.called
        proxy_down_events = [
            call[0][0]
            for call in callback.call_args_list
            if call[0][0].event_type == "proxy_down"
        ]
        assert len(proxy_down_events) > 0
        event = proxy_down_events[0]
        assert isinstance(event, HealthEvent)
        assert event.proxy_url == "http://proxy1.example.com:8080"

    def test_callback_called_on_recovery(self) -> None:
        """Test that callback is called when proxy recovers."""
        callback = Mock()
        config = HealthCheckConfig(max_recovery_attempts=5)
        checker = HealthChecker(config=config, on_event=callback)
        checker.add_proxy("http://proxy1.example.com:8080", source="test")

        # Set up proxy as recovering
        checker._proxies["http://proxy1.example.com:8080"]["recovery_attempt"] = 1
        checker._proxies["http://proxy1.example.com:8080"][
            "health_status"
        ] = HealthStatus.RECOVERING

        # Mock successful recovery
        with patch.object(checker, "check_proxy") as mock_check:
            mock_check.return_value = Mock(
                status=HealthStatus.HEALTHY,
                proxy_url="http://proxy1.example.com:8080",
                check_time=datetime.now(timezone.utc),
                check_url="http://www.google.com",
            )

            checker._attempt_recovery("http://proxy1.example.com:8080")

        # Find the recovery event
        recovery_events = [
            call[0][0]
            for call in callback.call_args_list
            if call[0][0].event_type == "proxy_recovered"
        ]
        assert len(recovery_events) > 0
        event = recovery_events[0]
        assert event.proxy_url == "http://proxy1.example.com:8080"

    def test_callback_exception_handled(self) -> None:
        """Test that callback exceptions are caught and logged."""
        def bad_callback(event):
            raise ValueError("Callback error")

        checker = HealthChecker(on_event=bad_callback)
        checker.add_proxy("http://proxy1.example.com:8080", source="test")

        # Should not raise even though callback raises
        checker._emit_event("proxy_down", proxy_url="http://proxy1.example.com:8080")


class TestPoolDegradationEvent:
    """Tests for pool degradation event (T083)."""

    def test_pool_degradation_event_emitted(self) -> None:
        """Test that pool_degraded event is emitted when health drops."""
        callback = Mock()
        checker = HealthChecker(on_event=callback)

        # Add 10 proxies
        for i in range(10):
            checker.add_proxy(f"http://proxy{i}.example.com:8080", source="test")
            checker._proxies[f"http://proxy{i}.example.com:8080"][
                "health_status"
            ] = HealthStatus.HEALTHY

        # Mark 7 as unhealthy (30% healthy = degraded)
        for i in range(7):
            checker._proxies[f"http://proxy{i}.example.com:8080"][
                "health_status"
            ] = HealthStatus.UNHEALTHY

        # Check degradation
        checker._check_pool_degradation()

        # Find pool_degraded event
        degraded_events = [
            call[0][0]
            for call in callback.call_args_list
            if call[0][0].event_type == "pool_degraded"
        ]
        assert len(degraded_events) > 0
        event = degraded_events[0]
        assert event.details["total_proxies"] == 10
        assert event.details["healthy_proxies"] == 3

    def test_no_degradation_event_when_healthy(self) -> None:
        """Test that no event is emitted when pool is healthy."""
        callback = Mock()
        checker = HealthChecker(on_event=callback)

        # Add 10 proxies, all healthy
        for i in range(10):
            checker.add_proxy(f"http://proxy{i}.example.com:8080", source="test")
            checker._proxies[f"http://proxy{i}.example.com:8080"][
                "health_status"
            ] = HealthStatus.HEALTHY

        # Check degradation
        checker._check_pool_degradation()

        # Should not have pool_degraded event
        degraded_events = [
            call[0][0]
            for call in callback.call_args_list
            if call[0][0].event_type == "pool_degraded"
        ]
        assert len(degraded_events) == 0
