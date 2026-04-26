"""
Comprehensive proxy model validation tests.

Tests:
- URL format validation (scheme, host, port, credentials)
- Health status enum transitions
- Field constraints and boundaries
- Credential handling
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from proxywhirl.models import Proxy, HealthStatus, ProxyCredentials, ProxySource


class TestProxyURLValidation:
    """Test proxy URL format validation."""

    def test_valid_http_proxy_url(self):
        """Test valid HTTP proxy URL."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.url == "http://proxy.example.com:8080"

    def test_valid_https_proxy_url(self):
        """Test valid HTTPS proxy URL."""
        proxy = Proxy(url="https://secure-proxy.example.com:8443")
        assert proxy.url == "https://secure-proxy.example.com:8443"

    def test_valid_socks5_proxy_url(self):
        """Test valid SOCKS5 proxy URL."""
        proxy = Proxy(url="socks5://socks.example.com:1080")
        assert proxy.url == "socks5://socks.example.com:1080"

    def test_valid_socks4_proxy_url(self):
        """Test valid SOCKS4 proxy URL."""
        proxy = Proxy(url="socks4://socks.example.com:1080")
        assert proxy.url == "socks4://socks.example.com:1080"

    def test_proxy_with_ipv4_address(self):
        """Test proxy with IPv4 address (allow_local for private IPs)."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        assert "192.168.1.1" in proxy.url

    def test_proxy_with_ipv6_address(self):
        """Test proxy with IPv6 address (allow_local for private IPs)."""
        proxy = Proxy(url="http://[2001:db8::1]:8080", allow_local=True)
        assert proxy.url == "http://[2001:db8::1]:8080"

    def test_proxy_with_credentials_in_url(self):
        """Test proxy with credentials in URL."""
        proxy = Proxy(url="http://user:password@proxy.example.com:8080")
        assert "proxy.example.com" in proxy.url

    def test_proxy_with_subdomain(self):
        """Test proxy with subdomains."""
        proxy = Proxy(url="http://sub.domain.proxy.example.com:8080")
        assert "sub.domain.proxy.example.com" in proxy.url

    def test_invalid_proxy_url_no_scheme(self):
        """Test invalid proxy URL without scheme raises error."""
        with pytest.raises(ValidationError):
            Proxy(url="proxy.example.com:8080")

    def test_invalid_proxy_scheme(self):
        """Test invalid proxy scheme raises error."""
        with pytest.raises(ValidationError):
            Proxy(url="ftp://proxy.example.com:8080")

    def test_proxy_standard_http_port(self):
        """Test standard HTTP port (80)."""
        proxy = Proxy(url="http://proxy.example.com:80")
        assert ":80" in proxy.url

    def test_proxy_standard_https_port(self):
        """Test standard HTTPS port (443)."""
        proxy = Proxy(url="https://proxy.example.com:443")
        assert ":443" in proxy.url


class TestProxyHealthStatus:
    """Test health status field."""

    def test_initial_health_status_unknown(self):
        """Test initial health status is UNKNOWN."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.health_status == HealthStatus.UNKNOWN

    def test_health_status_healthy(self):
        """Test setting health status to HEALTHY."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            health_status=HealthStatus.HEALTHY
        )
        assert proxy.health_status == HealthStatus.HEALTHY

    def test_health_status_unhealthy(self):
        """Test setting health status to UNHEALTHY."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            health_status=HealthStatus.UNHEALTHY
        )
        assert proxy.health_status == HealthStatus.UNHEALTHY

    def test_health_status_degraded(self):
        """Test setting health status to DEGRADED."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            health_status=HealthStatus.DEGRADED
        )
        assert proxy.health_status == HealthStatus.DEGRADED

    def test_all_health_status_values(self):
        """Test all health status enum values."""
        for status in HealthStatus:
            proxy = Proxy(
                url="http://proxy.example.com:8080",
                health_status=status
            )
            assert proxy.health_status == status


class TestProxyFieldConstraints:
    """Test field constraints and boundaries."""

    def test_request_counts_zero(self):
        """Test initial request counts are zero."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.requests_completed == 0
        assert proxy.total_requests == 0
        assert proxy.total_successes == 0
        assert proxy.total_failures == 0

    def test_request_counts_positive(self):
        """Test request counts can be positive."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            requests_completed=100,
            total_requests=150,
            total_successes=80,
            total_failures=20
        )
        assert proxy.requests_completed == 100
        assert proxy.total_requests == 150
        assert proxy.total_successes == 80
        assert proxy.total_failures == 20

    def test_consecutive_failures_tracking(self):
        """Test consecutive failures tracking."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            consecutive_failures=5
        )
        assert proxy.consecutive_failures == 5

    def test_consecutive_successes_tracking(self):
        """Test consecutive successes tracking."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            consecutive_successes=10
        )
        assert proxy.consecutive_successes == 10

    def test_response_time_tracking(self):
        """Test response time tracking."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            average_response_time_ms=150.5,
            latency_ms=175.0
        )
        assert proxy.average_response_time_ms == 150.5
        assert proxy.latency_ms == 175.0

    def test_cost_per_request_non_negative(self):
        """Test cost per request must be non-negative."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            cost_per_request=0.05
        )
        assert proxy.cost_per_request == 0.05

    def test_cost_per_request_zero_free(self):
        """Test cost of zero is free."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            cost_per_request=0.0
        )
        assert proxy.cost_per_request == 0.0


class TestProxyCredentials:
    """Test proxy credentials handling."""

    def test_credentials_with_username(self):
        """Test credentials with username field (requires password too)."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username="myuser",
            password="mypass"
        )
        assert proxy.username is not None

    def test_credentials_with_password(self):
        """Test credentials with password field (requires username too)."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username="myuser",
            password="mypass"
        )
        assert proxy.password is not None

    def test_credentials_both_username_and_password(self):
        """Test credentials with both username and password."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username="user@domain.com",
            password="p@ssw0rd!#$"
        )
        assert proxy.username is not None
        assert proxy.password is not None

    def test_proxy_without_credentials(self):
        """Test proxy without credentials."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=None,
            password=None
        )
        assert proxy.username is None
        assert proxy.password is None


class TestProxyGeoLocation:
    """Test geolocation fields."""

    def test_proxy_country_code(self):
        """Test country code field."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            country_code="US"
        )
        assert proxy.country_code == "US"

    def test_proxy_region(self):
        """Test region field."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            region="California"
        )
        assert proxy.region == "California"

    def test_proxy_country_and_region(self):
        """Test country code and region together."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            country_code="GB",
            region="England"
        )
        assert proxy.country_code == "GB"
        assert proxy.region == "England"


class TestProxyMetadata:
    """Test metadata and tags."""

    def test_proxy_tags(self):
        """Test proxy tags."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            tags={"fast", "reliable"}
        )
        assert "fast" in proxy.tags
        assert "reliable" in proxy.tags

    def test_proxy_empty_tags(self):
        """Test proxy with empty tags."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert len(proxy.tags) == 0

    def test_proxy_metadata(self):
        """Test proxy metadata field."""
        meta = {"tier": "premium", "region": "EU"}
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            metadata=meta
        )
        assert proxy.metadata["tier"] == "premium"
        assert proxy.metadata["region"] == "EU"

    def test_proxy_source(self):
        """Test proxy source field."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            source=ProxySource.USER
        )
        assert proxy.source == ProxySource.USER


class TestProxyEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_proxy_id_uniqueness(self):
        """Test proxy IDs are unique."""
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        assert proxy1.id != proxy2.id

    def test_proxy_created_at_timestamp(self):
        """Test created_at timestamp."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.created_at is not None
        assert isinstance(proxy.created_at, datetime)

    def test_proxy_updated_at_timestamp(self):
        """Test updated_at timestamp."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.updated_at is not None
        assert isinstance(proxy.updated_at, datetime)

    def test_proxy_ttl_field(self):
        """Test TTL field."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            ttl=3600
        )
        assert proxy.ttl == 3600

    def test_proxy_active_requests(self):
        """Test active requests counter."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            requests_active=5
        )
        assert proxy.requests_active == 5

    def test_proxy_last_success_at(self):
        """Test last success timestamp."""
        now = datetime.now()
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            last_success_at=now
        )
        assert proxy.last_success_at == now

    def test_proxy_allow_local_flag(self):
        """Test allow_local flag."""
        proxy_allow = Proxy(
            url="http://localhost:8080",
            allow_local=True
        )
        assert proxy_allow.allow_local is True
        
        proxy_deny = Proxy(
            url="http://proxy.example.com:8080",
            allow_local=False
        )
        assert proxy_deny.allow_local is False
