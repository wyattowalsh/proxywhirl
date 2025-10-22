"""
Unit tests for Proxy model validation.
"""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from proxywhirl.models import HealthStatus, Proxy


class TestProxyValidation:
    """Test Proxy model validation rules."""

    def test_valid_proxy_url(self):
        """Test proxy creation with valid URL."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.url is not None
        assert proxy.protocol == "http"

    def test_valid_https_proxy(self):
        """Test proxy creation with HTTPS URL."""
        proxy = Proxy(url="https://proxy.example.com:8080")
        assert proxy.protocol == "https"

    def test_valid_socks5_proxy(self):
        """Test proxy creation with SOCKS5 URL."""
        proxy = Proxy(url="socks5://proxy.example.com:1080")
        assert proxy.protocol == "socks5"

    def test_protocol_extracted_from_url(self):
        """Test that protocol is extracted from URL if not provided."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.protocol == "http"

    def test_credentials_both_present(self):
        """Test proxy with both username and password."""
        from pydantic import SecretStr

        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("user"),
            password=SecretStr("pass"),
        )
        assert proxy.username is not None
        assert proxy.password is not None
        assert proxy.credentials is not None

    def test_credentials_both_absent(self):
        """Test proxy without credentials."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.username is None
        assert proxy.password is None
        assert proxy.credentials is None

    def test_credentials_only_username_raises_error(self):
        """Test that providing only username raises ValidationError."""
        from pydantic import SecretStr

        with pytest.raises(ValidationError, match="Both username and password"):
            Proxy(
                url="http://proxy.example.com:8080",
                username=SecretStr("user"),
            )

    def test_credentials_only_password_raises_error(self):
        """Test that providing only password raises ValidationError."""
        from pydantic import SecretStr

        with pytest.raises(ValidationError, match="Both username and password"):
            Proxy(
                url="http://proxy.example.com:8080",
                password=SecretStr("pass"),
            )


class TestProxyHealthStatus:
    """Test Proxy health status transitions."""

    def test_initial_health_status_unknown(self):
        """Test that new proxy has UNKNOWN health status."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.health_status == HealthStatus.UNKNOWN

    def test_record_success_updates_health_to_healthy(self):
        """Test that recording success changes status to HEALTHY."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_success(response_time_ms=100.0)
        assert proxy.health_status == HealthStatus.HEALTHY
        assert proxy.total_successes == 1
        assert proxy.consecutive_failures == 0

    def test_record_success_resets_consecutive_failures(self):
        """Test that success resets consecutive failures counter."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_failure()
        proxy.record_failure()
        assert proxy.consecutive_failures == 2

        proxy.record_success(response_time_ms=100.0)
        assert proxy.consecutive_failures == 0

    def test_one_failure_degrades_health(self):
        """Test that one failure sets status to DEGRADED."""
        proxy = Proxy(
            url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY
        )
        proxy.record_failure()
        assert proxy.health_status == HealthStatus.DEGRADED
        assert proxy.consecutive_failures == 1

    def test_three_failures_unhealthy(self):
        """Test that three consecutive failures set status to UNHEALTHY."""
        proxy = Proxy(
            url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY
        )
        proxy.record_failure()
        proxy.record_failure()
        proxy.record_failure()
        assert proxy.health_status == HealthStatus.UNHEALTHY
        assert proxy.consecutive_failures == 3

    def test_five_failures_dead(self):
        """Test that five consecutive failures set status to DEAD."""
        proxy = Proxy(
            url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY
        )
        for _ in range(5):
            proxy.record_failure()
        assert proxy.health_status == HealthStatus.DEAD
        assert proxy.consecutive_failures == 5


class TestProxyStats:
    """Test Proxy statistics tracking."""

    def test_success_rate_zero_initially(self):
        """Test that success rate is 0 for new proxy."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.success_rate == 0.0

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_success(100.0)
        proxy.record_success(100.0)
        proxy.record_failure()
        # 2 successes / 3 total = 0.666...
        assert abs(proxy.success_rate - 0.6666666666666666) < 0.0001

    def test_average_response_time_single_request(self):
        """Test average response time with single request."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_success(response_time_ms=150.0)
        assert proxy.average_response_time_ms == 150.0

    def test_average_response_time_exponential_moving_average(self):
        """Test that average response time uses exponential moving average."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_success(response_time_ms=100.0)
        proxy.record_success(response_time_ms=200.0)
        # EMA: alpha=0.3, so 0.3*200 + 0.7*100 = 60 + 70 = 130
        assert proxy.average_response_time_ms == 130.0

    def test_last_success_at_updated(self):
        """Test that last_success_at is updated on success."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        before = datetime.now(UTC)
        proxy.record_success(100.0)
        after = datetime.now(UTC)
        assert proxy.last_success_at is not None
        assert before <= proxy.last_success_at <= after

    def test_last_failure_at_updated(self):
        """Test that last_failure_at is updated on failure."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        before = datetime.now(UTC)
        proxy.record_failure()
        after = datetime.now(UTC)
        assert proxy.last_failure_at is not None
        assert before <= proxy.last_failure_at <= after

    def test_failure_error_stored_in_metadata(self):
        """Test that failure errors are stored in metadata."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_failure(error="Connection timeout")
        assert "last_errors" in proxy.metadata
        assert len(proxy.metadata["last_errors"]) == 1
        assert proxy.metadata["last_errors"][0]["error"] == "Connection timeout"

    def test_metadata_keeps_last_10_errors(self):
        """Test that metadata only keeps last 10 errors."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        for i in range(15):
            proxy.record_failure(error=f"Error {i}")
        assert len(proxy.metadata["last_errors"]) == 10
        # Should keep errors 5-14
        assert proxy.metadata["last_errors"][0]["error"] == "Error 5"
        assert proxy.metadata["last_errors"][-1]["error"] == "Error 14"


class TestProxyProperties:
    """Test Proxy computed properties."""

    def test_is_healthy_true_for_healthy_status(self):
        """Test is_healthy returns True for HEALTHY status."""
        proxy = Proxy(
            url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY
        )
        assert proxy.is_healthy is True

    def test_is_healthy_false_for_degraded_status(self):
        """Test is_healthy returns False for DEGRADED status."""
        proxy = Proxy(
            url="http://proxy.example.com:8080", health_status=HealthStatus.DEGRADED
        )
        assert proxy.is_healthy is False

    def test_is_healthy_false_for_unhealthy_status(self):
        """Test is_healthy returns False for UNHEALTHY status."""
        proxy = Proxy(
            url="http://proxy.example.com:8080", health_status=HealthStatus.UNHEALTHY
        )
        assert proxy.is_healthy is False

    def test_is_healthy_false_for_dead_status(self):
        """Test is_healthy returns False for DEAD status."""
        proxy = Proxy(
            url="http://proxy.example.com:8080", health_status=HealthStatus.DEAD
        )
        assert proxy.is_healthy is False

    def test_credentials_property_returns_none_when_no_creds(self):
        """Test credentials property returns None when no credentials."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.credentials is None

    def test_credentials_property_returns_credentials_object(self):
        """Test credentials property returns ProxyCredentials object."""
        from pydantic import SecretStr

        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("user"),
            password=SecretStr("pass"),
        )
        creds = proxy.credentials
        assert creds is not None
        assert creds.username.get_secret_value() == "user"
        assert creds.password.get_secret_value() == "pass"
