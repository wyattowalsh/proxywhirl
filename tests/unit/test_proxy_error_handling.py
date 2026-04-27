"""Tests for proxy error handling and edge cases."""

import pytest
from pydantic import ValidationError

from proxywhirl.models import Proxy


class TestProxyURLErrors:
    """Test proxy URL validation errors."""

    def test_invalid_url_no_scheme(self):
        """Test URL without scheme raises error."""
        with pytest.raises(ValidationError) as exc_info:
            Proxy(url="proxy.example.com:8080")
        assert "scheme" in str(exc_info.value).lower()

    def test_invalid_url_unsupported_scheme(self):
        """Test unsupported proxy scheme raises error."""
        with pytest.raises(ValidationError) as exc_info:
            Proxy(url="ftp://proxy.example.com:8080")
        assert "scheme" in str(exc_info.value).lower()

    def test_invalid_url_missing_host(self):
        """Test URL without host."""
        with pytest.raises(ValidationError):
            Proxy(url="http://:8080")

    def test_empty_url(self):
        """Test empty URL raises error."""
        with pytest.raises(ValidationError):
            Proxy(url="")

    def test_url_with_spaces(self):
        """Test URL with spaces."""
        with pytest.raises(ValidationError):
            Proxy(url="http://proxy example.com:8080")


class TestProxyCredentialErrors:
    """Test credential validation errors."""

    def test_username_without_password(self):
        """Test username without password raises error."""
        with pytest.raises(ValidationError) as exc_info:
            Proxy(url="http://proxy.example.com:8080", username="user")
        assert "password" in str(exc_info.value).lower()

    def test_password_without_username(self):
        """Test password without username raises error."""
        with pytest.raises(ValidationError) as exc_info:
            Proxy(url="http://proxy.example.com:8080", password="pass")
        assert "username" in str(exc_info.value).lower()

    def test_empty_username(self):
        """Test empty username with password is allowed (validated at runtime)."""
        # Empty username doesn't raise validation error, but is semantically wrong
        proxy = Proxy(url="http://proxy.example.com:8080", username="", password="pass")
        assert proxy.username is not None

    def test_empty_password(self):
        """Test empty password with username is allowed (validated at runtime)."""
        # Empty password doesn't raise validation error, but is semantically wrong
        proxy = Proxy(url="http://proxy.example.com:8080", username="user", password="")
        assert proxy.password is not None


class TestProxyPrivateIPErrors:
    """Test private IP address restrictions."""

    def test_private_ipv4_not_allowed_by_default(self):
        """Test private IPv4 not allowed without allow_local."""
        with pytest.raises(ValidationError) as exc_info:
            Proxy(url="http://192.168.1.1:8080")
        assert "private" in str(exc_info.value).lower() or "local" in str(exc_info.value).lower()

    def test_localhost_not_allowed_by_default(self):
        """Test localhost not allowed by default."""
        with pytest.raises(ValidationError) as exc_info:
            Proxy(url="http://localhost:8080")
        assert "private" in str(exc_info.value).lower() or "local" in str(exc_info.value).lower()

    def test_127_0_0_1_not_allowed_by_default(self):
        """Test 127.0.0.1 not allowed by default."""
        with pytest.raises(ValidationError):
            Proxy(url="http://127.0.0.1:8080")

    def test_private_ipv6_not_allowed_by_default(self):
        """Test private IPv6 not allowed by default."""
        with pytest.raises(ValidationError):
            Proxy(url="http://[::1]:8080")  # IPv6 loopback

    def test_private_ipv4_allowed_with_flag(self):
        """Test private IPv4 allowed with allow_local=True."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        assert proxy.allow_local is True

    def test_localhost_allowed_with_flag(self):
        """Test localhost allowed with allow_local=True."""
        proxy = Proxy(url="http://localhost:8080", allow_local=True)
        assert proxy.allow_local is True


class TestProxyFieldTypeErrors:
    """Test field type validation."""

    def test_invalid_country_code_type(self):
        """Test invalid country code type."""
        # Should still accept string
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            country_code="INVALID_CODE",  # Length is fine, just a string
        )
        assert proxy.country_code == "INVALID_CODE"

    def test_invalid_ttl_negative(self):
        """Test negative TTL values."""
        # Pydantic should accept any int, but semantically negative TTL is invalid
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            ttl=-1,  # Negative TTL
        )
        # Should be stored but it's semantically wrong
        assert proxy.ttl == -1

    def test_cost_per_request_negative_rejected(self):
        """Test negative cost per request is rejected."""
        with pytest.raises(ValidationError):
            Proxy(url="http://proxy.example.com:8080", cost_per_request=-0.5)

    def test_invalid_health_status_type(self):
        """Test invalid health status type."""
        with pytest.raises(ValidationError):
            Proxy(url="http://proxy.example.com:8080", health_status="INVALID_STATUS")


class TestProxyRequestCountErrors:
    """Test request count validation."""

    def test_negative_requests_completed(self):
        """Test negative request counts are rejected."""
        # Request counts must be non-negative
        with pytest.raises(ValidationError):
            Proxy(
                url="http://proxy.example.com:8080",
                requests_completed=-5,  # Negative
            )

    def test_completed_exceeds_total(self):
        """Test completed requests exceeding total."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            total_requests=100,
            requests_completed=150,  # More than total
        )
        # Model allows this, but it's logically inconsistent
        assert proxy.requests_completed > proxy.total_requests

    def test_negative_total_requests(self):
        """Test negative total requests are rejected."""
        with pytest.raises(ValidationError):
            Proxy(url="http://proxy.example.com:8080", total_requests=-10)


class TestProxyModelEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_proxy_with_extremely_long_host(self):
        """Test proxy with very long hostname."""
        long_host = "sub." * 100 + "example.com"
        # This might be invalid DNS but let's see if pydantic accepts it
        try:
            proxy = Proxy(url=f"http://{long_host}:8080")
            assert proxy.url is not None
        except ValidationError:
            # If rejected, that's also fine
            pass

    def test_proxy_with_unicode_in_url(self):
        """Test proxy URL with unicode characters."""
        with pytest.raises(ValidationError):
            Proxy(url="http://プロキシ.example.com:8080")

    def test_proxy_with_special_chars_in_host(self):
        """Test proxy with special characters in hostname."""
        with pytest.raises(ValidationError):
            Proxy(url="http://proxy-!@#$%.example.com:8080")

    def test_proxy_port_out_of_range(self):
        """Test proxy with port > 65535."""
        with pytest.raises(ValidationError):
            Proxy(url="http://proxy.example.com:65536")

    def test_proxy_port_zero(self):
        """Test proxy with port 0."""
        with pytest.raises(ValidationError):
            Proxy(url="http://proxy.example.com:0")

    def test_proxy_with_query_string_in_url(self):
        """Test proxy URL with query string (should be rejected)."""
        with pytest.raises(ValidationError):
            Proxy(url="http://proxy.example.com:8080?timeout=30")

    def test_proxy_with_fragment_in_url(self):
        """Test proxy URL with fragment."""
        with pytest.raises(ValidationError):
            Proxy(url="http://proxy.example.com:8080#section")

    def test_proxy_with_path_in_url(self):
        """Test proxy URL with path (should be rejected)."""
        with pytest.raises(ValidationError):
            Proxy(url="http://proxy.example.com:8080/path/to/proxy")


class TestProxyConsecutiveCounters:
    """Test consecutive failure and success counters."""

    def test_consecutive_failures_max_value(self):
        """Test very high consecutive failure count."""
        proxy = Proxy(url="http://proxy.example.com:8080", consecutive_failures=999999)
        assert proxy.consecutive_failures == 999999

    def test_consecutive_successes_max_value(self):
        """Test very high consecutive success count."""
        proxy = Proxy(url="http://proxy.example.com:8080", consecutive_successes=999999)
        assert proxy.consecutive_successes == 999999

    def test_both_consecutive_counters(self):
        """Test both consecutive counters simultaneously."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            consecutive_failures=10,
            consecutive_successes=50,  # Logically impossible but allowed
        )
        assert proxy.consecutive_failures == 10
        assert proxy.consecutive_successes == 50


class TestProxyResponseTimeFields:
    """Test response time field validation."""

    def test_negative_response_time(self):
        """Test negative response time is rejected."""
        # Response times must be non-negative
        with pytest.raises(ValidationError):
            Proxy(url="http://proxy.example.com:8080", average_response_time_ms=-100.0)

    def test_zero_response_time(self):
        """Test zero response time."""
        proxy = Proxy(url="http://proxy.example.com:8080", average_response_time_ms=0.0)
        assert proxy.average_response_time_ms == 0.0

    def test_very_high_response_time(self):
        """Test very high response time."""
        proxy = Proxy(url="http://proxy.example.com:8080", average_response_time_ms=999999999.99)
        assert proxy.average_response_time_ms > 0
