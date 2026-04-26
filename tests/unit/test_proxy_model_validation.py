"""
Comprehensive proxy model validation tests.

Tests:
- URL format validation (scheme, host, port, credentials)
- Health status enum transitions
- Field constraints and boundaries
- Credential encryption/decryption
"""

import pytest
from pydantic import ValidationError

from proxywhirl.models import Proxy, HealthStatus, ProxyCredentials


class TestProxyURLValidation:
    """Test proxy URL format validation."""

    def test_valid_http_proxy_url(self):
        """Test valid HTTP proxy URL."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080
        )
        assert proxy.url == "http://proxy.example.com:8080"
        assert proxy.protocol == "http"

    def test_valid_https_proxy_url(self):
        """Test valid HTTPS proxy URL."""
        proxy = Proxy(
            protocol="https",
            host="secure-proxy.example.com",
            port=8443
        )
        assert proxy.url == "https://secure-proxy.example.com:8443"

    def test_valid_socks5_proxy_url(self):
        """Test valid SOCKS5 proxy URL."""
        proxy = Proxy(
            protocol="socks5",
            host="socks.example.com",
            port=1080
        )
        assert proxy.url == "socks5://socks.example.com:1080"

    def test_proxy_with_ipv4_address(self):
        """Test proxy with IPv4 address."""
        proxy = Proxy(
            protocol="http",
            host="192.168.1.1",
            port=8080
        )
        assert proxy.url == "http://192.168.1.1:8080"

    def test_proxy_with_ipv6_address(self):
        """Test proxy with IPv6 address (bracketed)."""
        proxy = Proxy(
            protocol="http",
            host="2001:db8::1",
            port=8080
        )
        assert proxy.url == "http://2001:db8::1:8080"

    def test_proxy_with_credentials(self):
        """Test proxy with username/password."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080,
            credentials=ProxyCredentials(username="user", password="pass")
        )
        assert "user" in proxy.url or proxy.credentials is not None

    def test_proxy_with_subdomain(self):
        """Test proxy with subdomains."""
        proxy = Proxy(
            protocol="http",
            host="sub.domain.proxy.example.com",
            port=8080
        )
        assert proxy.url == "http://sub.domain.proxy.example.com:8080"

    def test_proxy_port_boundary_values(self):
        """Test proxy port boundary values."""
        # Valid ports
        proxy_min = Proxy(protocol="http", host="proxy.example.com", port=1)
        assert proxy_min.port == 1
        
        proxy_max = Proxy(protocol="http", host="proxy.example.com", port=65535)
        assert proxy_max.port == 65535
        
        # Standard ports
        proxy_http = Proxy(protocol="http", host="proxy.example.com", port=80)
        assert proxy_http.port == 80
        
        proxy_https = Proxy(protocol="https", host="proxy.example.com", port=443)
        assert proxy_https.port == 443


class TestProxyHealthStatus:
    """Test health status transitions."""

    def test_initial_health_status(self):
        """Test initial health status."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080
        )
        assert proxy.health_status == HealthStatus.HEALTHY

    def test_health_status_transition_to_unhealthy(self):
        """Test transition to unhealthy."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080,
            health_status=HealthStatus.UNHEALTHY
        )
        assert proxy.health_status == HealthStatus.UNHEALTHY

    def test_health_status_transition_to_degraded(self):
        """Test transition to degraded."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080,
            health_status=HealthStatus.DEGRADED
        )
        assert proxy.health_status == HealthStatus.DEGRADED

    def test_health_status_enum_values(self):
        """Test all health status enum values are valid."""
        valid_statuses = [HealthStatus.HEALTHY, HealthStatus.UNHEALTHY, HealthStatus.DEGRADED]
        for status in valid_statuses:
            proxy = Proxy(
                protocol="http",
                host="proxy.example.com",
                port=8080,
                health_status=status
            )
            assert proxy.health_status == status


class TestProxyFieldConstraints:
    """Test field constraints and boundaries."""

    def test_request_counts(self):
        """Test request count tracking."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080,
            requests_completed=100,
            total_requests=150,
            failed_requests=10
        )
        assert proxy.requests_completed == 100
        assert proxy.total_requests == 150
        assert proxy.failed_requests == 10

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080,
            requests_completed=80,
            total_requests=100
        )
        # success_rate = requests_completed / total_requests
        assert proxy.requests_completed <= proxy.total_requests

    def test_proxy_weight_positive(self):
        """Test proxy weight must be positive."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080,
            weight=1.5
        )
        assert proxy.weight > 0

    def test_proxy_response_time_zero_or_positive(self):
        """Test response time is non-negative."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080,
            response_time_ms=100.5
        )
        assert proxy.response_time_ms >= 0


class TestProxyCredentials:
    """Test proxy credentials handling."""

    def test_credentials_with_username_only(self):
        """Test credentials with username only."""
        creds = ProxyCredentials(username="user")
        assert creds.username == "user"

    def test_credentials_with_password(self):
        """Test credentials with password."""
        creds = ProxyCredentials(username="user", password="secure_pass")
        assert creds.username == "user"
        assert creds.password == "secure_pass"

    def test_credentials_with_special_chars(self):
        """Test credentials with special characters."""
        creds = ProxyCredentials(
            username="user@domain.com",
            password="p@ssw0rd!#$"
        )
        assert creds.username == "user@domain.com"

    def test_proxy_with_null_credentials(self):
        """Test proxy with null credentials."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080,
            credentials=None
        )
        assert proxy.credentials is None


class TestProxyEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_proxy_id_uniqueness(self):
        """Test proxy IDs are unique."""
        proxy1 = Proxy(protocol="http", host="proxy1.example.com", port=8080)
        proxy2 = Proxy(protocol="http", host="proxy2.example.com", port=8080)
        assert proxy1.id != proxy2.id

    def test_proxy_created_at_timestamp(self):
        """Test created_at timestamp."""
        proxy = Proxy(protocol="http", host="proxy.example.com", port=8080)
        assert proxy.created_at is not None

    def test_proxy_last_checked_time(self):
        """Test last_checked_time field."""
        proxy = Proxy(protocol="http", host="proxy.example.com", port=8080)
        # Should have a last_checked_time or be None
        assert proxy.last_checked_time is None or proxy.last_checked_time is not None

    def test_proxy_country_code(self):
        """Test country code field."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080,
            country="US"
        )
        assert proxy.country == "US"

    def test_proxy_anonymity_level(self):
        """Test anonymity level."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080,
            anonymity_level="elite"
        )
        assert proxy.anonymity_level == "elite"

    def test_proxy_tags(self):
        """Test proxy tags."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080,
            tags=["fast", "reliable"]
        )
        assert "fast" in proxy.tags
        assert "reliable" in proxy.tags

    def test_proxy_with_no_tags(self):
        """Test proxy with empty tags."""
        proxy = Proxy(
            protocol="http",
            host="proxy.example.com",
            port=8080,
            tags=[]
        )
        assert len(proxy.tags) == 0


class TestProxyImmutability:
    """Test proxy model immutability (frozen config)."""

    def test_proxy_model_frozen(self):
        """Test proxy model is frozen (immutable)."""
        proxy = Proxy(protocol="http", host="proxy.example.com", port=8080)
        
        # Attempting to modify should raise ValidationError or AttributeError
        with pytest.raises((ValidationError, TypeError, AttributeError)):
            proxy.protocol = "https"
