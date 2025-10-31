"""Unit tests for model validators and properties."""

from datetime import datetime, timedelta, timezone

import pytest

from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyConfiguration,
    ProxyCredentials,
)


class TestProxyValidators:
    """Test Proxy model validators."""

    def test_extract_protocol_from_http_url(self):
        """Test protocol extraction from http:// URL."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.protocol == "http"

    def test_extract_protocol_from_https_url(self):
        """Test protocol extraction from https:// URL."""
        proxy = Proxy(url="https://proxy.example.com:8443")
        assert proxy.protocol == "https"

    def test_extract_protocol_from_socks4_url(self):
        """Test protocol extraction from socks4:// URL."""
        proxy = Proxy(url="socks4://proxy.example.com:1080")
        assert proxy.protocol == "socks4"

    def test_extract_protocol_from_socks5_url(self):
        """Test protocol extraction from socks5:// URL."""
        proxy = Proxy(url="socks5://proxy.example.com:1080")
        assert proxy.protocol == "socks5"

    def test_explicit_protocol_not_overridden(self):
        """Test that explicit protocol is not overridden."""
        proxy = Proxy(url="http://proxy.example.com:8080", protocol="https")
        assert proxy.protocol == "https"

    def test_validate_credentials_both_present(self):
        """Test credentials validation with both username and password."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username="user",
            password="pass",
        )
        assert proxy.username == "user"
        assert proxy.password == "pass"

    def test_validate_credentials_both_absent(self):
        """Test credentials validation with neither username nor password."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.username is None
        assert proxy.password is None

    def test_validate_credentials_only_username_raises_error(self):
        """Test that username without password raises error."""
        with pytest.raises(
            ValueError, match="Both username and password must be provided together"
        ):
            Proxy(
                url="http://proxy.example.com:8080",
                username="user",
            )

    def test_validate_credentials_only_password_raises_error(self):
        """Test that password without username raises error."""
        with pytest.raises(
            ValueError, match="Both username and password must be provided together"
        ):
            Proxy(
                url="http://proxy.example.com:8080",
                password="pass",
            )

    def test_set_expiration_from_ttl(self):
        """Test that expires_at is set from ttl."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            ttl=3600,  # 1 hour
        )
        expected_expiration = proxy.created_at + timedelta(seconds=3600)
        assert proxy.expires_at == expected_expiration

    def test_set_expiration_ttl_none(self):
        """Test that expires_at is None when ttl is None."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.expires_at is None

    def test_explicit_expires_at_not_overridden(self):
        """Test that explicit expires_at is not overridden by ttl."""
        explicit_expiration = datetime.now(timezone.utc) + timedelta(hours=2)
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            ttl=3600,  # 1 hour
            expires_at=explicit_expiration,
        )
        assert proxy.expires_at == explicit_expiration


class TestProxyProperties:
    """Test Proxy model properties."""

    def test_success_rate_zero_requests(self):
        """Test success rate with zero requests."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.success_rate == 0.0

    def test_success_rate_all_successes(self):
        """Test success rate with all successes."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            total_requests=10,
            total_successes=10,
        )
        assert proxy.success_rate == 1.0

    def test_success_rate_partial_successes(self):
        """Test success rate with partial successes."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            total_requests=10,
            total_successes=7,
        )
        assert proxy.success_rate == 0.7

    def test_success_rate_no_successes(self):
        """Test success rate with no successes."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            total_requests=10,
            total_successes=0,
        )
        assert proxy.success_rate == 0.0

    def test_is_expired_no_expiration(self):
        """Test is_expired with no expiration set."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert not proxy.is_expired

    def test_is_expired_future_expiration(self):
        """Test is_expired with future expiration."""
        future_expiration = datetime.now(timezone.utc) + timedelta(hours=1)
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            expires_at=future_expiration,
        )
        assert not proxy.is_expired

    def test_is_expired_past_expiration(self):
        """Test is_expired with past expiration."""
        past_expiration = datetime.now(timezone.utc) - timedelta(hours=1)
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            expires_at=past_expiration,
        )
        assert proxy.is_expired

    def test_is_healthy_true(self):
        """Test is_healthy property when status is HEALTHY."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            health_status=HealthStatus.HEALTHY,
        )
        assert proxy.is_healthy

    def test_is_healthy_false_unhealthy(self):
        """Test is_healthy property when status is UNHEALTHY."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            health_status=HealthStatus.UNHEALTHY,
        )
        assert not proxy.is_healthy

    def test_is_healthy_false_degraded(self):
        """Test is_healthy property when status is DEGRADED."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            health_status=HealthStatus.DEGRADED,
        )
        assert not proxy.is_healthy

    def test_credentials_property_with_auth(self):
        """Test credentials property with authentication."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username="user",
            password="pass",
        )
        creds = proxy.credentials
        assert creds is not None
        assert creds.username == "user"
        assert creds.password == "pass"

    def test_credentials_property_without_auth(self):
        """Test credentials property without authentication."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.credentials is None


class TestProxyConfigurationValidators:
    """Test ProxyConfiguration model validators."""

    def test_validate_positive_timeout(self):
        """Test timeout must be positive."""
        with pytest.raises(ValueError, match="Value must be positive"):
            ProxyConfiguration(timeout=0)

    def test_validate_positive_max_retries(self):
        """Test max_retries must be positive."""
        with pytest.raises(ValueError, match="Value must be positive"):
            ProxyConfiguration(max_retries=0)

    def test_validate_positive_pool_connections(self):
        """Test pool_connections must be positive."""
        with pytest.raises(ValueError, match="Value must be positive"):
            ProxyConfiguration(pool_connections=0)

    def test_validate_negative_timeout(self):
        """Test negative timeout raises error."""
        with pytest.raises(ValueError, match="Value must be positive"):
            ProxyConfiguration(timeout=-1)

    def test_validate_negative_max_retries(self):
        """Test negative max_retries raises error."""
        with pytest.raises(ValueError, match="Value must be positive"):
            ProxyConfiguration(max_retries=-1)

    def test_validate_negative_pool_connections(self):
        """Test negative pool_connections raises error."""
        with pytest.raises(ValueError, match="Value must be positive"):
            ProxyConfiguration(pool_connections=-1)

    def test_validate_storage_sqlite_without_path(self):
        """Test sqlite backend requires storage_path."""
        with pytest.raises(ValueError, match="storage_path required for sqlite backend"):
            ProxyConfiguration(storage_backend="sqlite")

    def test_validate_storage_file_without_path(self):
        """Test file backend requires storage_path."""
        with pytest.raises(ValueError, match="storage_path required for file backend"):
            ProxyConfiguration(storage_backend="file")

    def test_validate_storage_memory_no_path_required(self):
        """Test memory backend doesn't require storage_path."""
        config = ProxyConfiguration(storage_backend="memory")
        assert config.storage_path is None

    def test_validate_storage_sqlite_with_path(self):
        """Test sqlite backend with storage_path."""
        from pathlib import Path

        config = ProxyConfiguration(
            storage_backend="sqlite",
            storage_path=Path("/tmp/proxies.db"),
        )
        assert config.storage_path == Path("/tmp/proxies.db")


class TestProxyCredentialsRedaction:
    """Test ProxyCredentials password redaction."""

    def test_password_redacted_in_repr(self):
        """Test that password is redacted in repr."""
        creds = ProxyCredentials(username="user", password="secret123")
        repr_str = repr(creds)
        assert "secret123" not in repr_str
        assert "***" in repr_str or "SecretStr" in repr_str

    def test_password_redacted_in_str(self):
        """Test that password is redacted in str."""
        creds = ProxyCredentials(username="user", password="secret123")
        str_rep = str(creds)
        assert "secret123" not in str_rep
        assert "***" in str_rep or "SecretStr" in str_rep

    def test_password_value_accessible(self):
        """Test that password value is still accessible."""
        creds = ProxyCredentials(username="user", password="secret123")
        assert creds.password.get_secret_value() == "secret123"


class TestProxyRecordMethods:
    """Test Proxy record methods."""

    def test_record_success_updates_counts(self):
        """Test recording success updates counts."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_success(100.0)

        assert proxy.total_requests == 1
        assert proxy.total_successes == 1

    def test_record_failure_updates_counts(self):
        """Test recording failure updates counts."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_failure()

        assert proxy.total_requests == 1
        assert proxy.total_successes == 0

    def test_start_request_increments_counter(self):
        """Test starting request increments counter."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.start_request()

        assert proxy.requests_started == 1
        assert proxy.concurrent_requests == 1

    def test_complete_request_decrements_concurrent(self):
        """Test completing request decrements concurrent counter."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.start_request()
        proxy.complete_request()

        assert proxy.requests_started == 1
        assert proxy.concurrent_requests == 0

    def test_multiple_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        proxy = Proxy(url="http://proxy.example.com:8080")

        proxy.start_request()
        proxy.start_request()
        proxy.start_request()

        assert proxy.requests_started == 3
        assert proxy.concurrent_requests == 3

        proxy.complete_request()
        assert proxy.concurrent_requests == 2
