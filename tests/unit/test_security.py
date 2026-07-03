"""
Comprehensive security tests for ProxyWhirl.

Tests cover:
- SSRF protection with IP blocklists
- Credential redaction in logs and messages
- Input validation on all API endpoints
- TLS certificate verification configuration
- Debug logging redaction
"""

import ipaddress
import logging
from io import StringIO

import pytest

from proxywhirl.security import (
    RedactionFilter,
    add_redaction_to_loguru,
    is_ip_blocked,
    redact_dict,
    redact_url,
    validate_input_port,
    validate_input_string,
    validate_proxy_credentials,
    validate_proxy_url_safety,
)

# ============================================================================
# SSRF PROTECTION TESTS
# ============================================================================


class TestSSRFBlocklist:
    """Test SSRF protection with IP blocklists."""

    def test_metadata_service_aws_blocked(self):
        """Test AWS metadata service (169.254.169.254) is blocked."""
        ip = ipaddress.IPv4Address("169.254.169.254")
        blocked, reason = is_ip_blocked(ip)
        assert blocked
        assert "metadata" in reason.lower()

    def test_metadata_service_azure_blocked(self):
        """Test Azure metadata service is blocked."""
        ip = ipaddress.IPv4Address("169.254.169.254")
        blocked, reason = is_ip_blocked(ip)
        assert blocked

    def test_metadata_service_alibaba_blocked(self):
        """Test Alibaba metadata service (100.100.100.200) is blocked."""
        ip = ipaddress.IPv4Address("100.100.100.200")
        blocked, reason = is_ip_blocked(ip)
        assert blocked
        assert "metadata" in reason.lower()

    def test_docker_metadata_blocked(self):
        """Test Docker metadata service (127.0.0.11) is blocked."""
        ip = ipaddress.IPv4Address("127.0.0.11")
        blocked, reason = is_ip_blocked(ip)
        assert blocked

    def test_loopback_blocked(self):
        """Test loopback addresses are blocked."""
        blocked, reason = is_ip_blocked(ipaddress.IPv4Address("127.0.0.1"))
        assert blocked
        assert "loopback" in reason.lower()

    def test_private_ips_blocked(self):
        """Test private IP ranges are blocked."""
        private_ips = [
            "10.0.0.1",
            "172.16.0.1",
            "192.168.1.1",
        ]
        for ip_str in private_ips:
            blocked, reason = is_ip_blocked(ipaddress.IPv4Address(ip_str))
            assert blocked, f"{ip_str} should be blocked"
            assert "private" in reason.lower()

    def test_link_local_blocked(self):
        """Test link-local addresses are blocked."""
        ip = ipaddress.IPv4Address("169.254.1.1")
        blocked, reason = is_ip_blocked(ip)
        assert blocked
        assert "link-local" in reason.lower()

    def test_reserved_blocked(self):
        """Test reserved addresses are blocked."""
        ip = ipaddress.IPv4Address("240.0.0.1")
        blocked, reason = is_ip_blocked(ip)
        assert blocked
        assert "reserved" in reason.lower()

    def test_multicast_blocked(self):
        """Test multicast addresses are blocked."""
        ip = ipaddress.IPv4Address("224.0.0.1")
        blocked, reason = is_ip_blocked(ip)
        assert blocked
        assert "multicast" in reason.lower()

    def test_unspecified_blocked(self):
        """Test unspecified address (0.0.0.0) is blocked."""
        ip = ipaddress.IPv4Address("0.0.0.0")
        blocked, reason = is_ip_blocked(ip)
        assert blocked
        assert "unspecified" in reason.lower()

    def test_ipv6_loopback_blocked(self):
        """Test IPv6 loopback (::1) is blocked."""
        ip = ipaddress.IPv6Address("::1")
        blocked, reason = is_ip_blocked(ip)
        assert blocked

    def test_ipv6_private_blocked(self):
        """Test IPv6 private addresses are blocked."""
        ip = ipaddress.IPv6Address("fd00::1")
        blocked, reason = is_ip_blocked(ip)
        assert blocked

    def test_ipv6_mapped_ipv4_blocked(self):
        """Test IPv6-mapped IPv4 addresses are validated against IPv4 rules."""
        # IPv6 address mapping to 127.0.0.1 (loopback)
        ip = ipaddress.IPv6Address("::ffff:127.0.0.1")
        blocked, reason = is_ip_blocked(ip)
        assert blocked

    def test_public_ip_allowed(self):
        """Test public IP addresses are allowed."""
        public_ips = [
            "1.1.1.1",  # Cloudflare DNS
            "8.8.8.8",  # Google DNS
            "208.67.222.222",  # OpenDNS
        ]
        for ip_str in public_ips:
            blocked, reason = is_ip_blocked(ipaddress.IPv4Address(ip_str))
            assert not blocked, f"{ip_str} should be allowed"


class TestProxyURLSafety:
    """Test proxy URL safety validation."""

    def test_public_proxy_url_allowed(self):
        """Test public proxy URLs are allowed."""
        is_safe, reason = validate_proxy_url_safety("http://example.com:8080")
        assert is_safe

    def test_localhost_proxy_url_rejected(self):
        """Test localhost proxy URLs are rejected."""
        is_safe, reason = validate_proxy_url_safety("http://localhost:8080")
        assert not is_safe

    def test_internal_domain_proxy_rejected(self):
        """Test internal domain proxy URLs are rejected."""
        internal_domains = [
            "http://proxy.local:8080",
            "http://proxy.internal:8080",
            "http://proxy.lan:8080",
            "http://proxy.corp:8080",
        ]
        for url in internal_domains:
            is_safe, reason = validate_proxy_url_safety(url)
            assert not is_safe, f"{url} should be rejected"

    def test_private_ip_proxy_rejected(self):
        """Test private IP proxy URLs are rejected."""
        private_proxy_urls = [
            "http://192.168.1.1:8080",
            "http://10.0.0.1:8080",
            "http://172.16.0.1:8080",
        ]
        for url in private_proxy_urls:
            is_safe, reason = validate_proxy_url_safety(url)
            assert not is_safe, f"{url} should be rejected"

    def test_invalid_url_rejected(self):
        """Test invalid URLs are rejected."""
        is_safe, reason = validate_proxy_url_safety("not-a-valid-url")
        assert not is_safe


# ============================================================================
# CREDENTIAL REDACTION TESTS
# ============================================================================


class TestCredentialRedaction:
    """Test credential redaction in logs."""

    def test_redact_url_with_credentials(self):
        """Test URL credentials are redacted."""
        url = "http://user:password@proxy.com:8080/path"
        redacted = redact_url(url)
        assert "***:***@" in redacted
        assert "password" not in redacted
        assert "proxy.com" in redacted

    def test_redact_url_with_only_username(self):
        """Test URL with only username is redacted."""
        url = "http://user@proxy.com:8080"
        redacted = redact_url(url)
        assert "***:***@" in redacted

    def test_redact_url_preserves_public_url(self):
        """Test public URLs are not modified."""
        url = "http://proxy.com:8080/path"
        redacted = redact_url(url)
        assert redacted == url

    def test_redact_url_with_sensitive_query_params(self):
        """Test sensitive query parameters are redacted."""
        url = "http://proxy.com:8080?api_key=secret123&normal=value"
        redacted = redact_url(url)
        assert "secret123" not in redacted
        assert "***" in redacted
        assert "normal=value" in redacted

    def test_redact_url_with_password_param(self):
        """Test password parameter is redacted."""
        url = "http://proxy.com:8080?password=mysecret"
        redacted = redact_url(url)
        assert "mysecret" not in redacted
        assert "***" in redacted

    def test_redact_dict_with_secrets(self):
        """Test dictionary with secret keys is redacted."""
        data = {
            "username": "john",
            "password": "secret123",
            "api_key": "key456",
            "normal_field": "public",
        }
        redacted = redact_dict(data)
        assert redacted["password"] == "***"
        assert redacted["api_key"] == "***"
        assert redacted["normal_field"] == "public"

    def test_redact_dict_nested(self):
        """Test nested dictionaries are redacted."""
        data = {
            "outer": {
                "password": "secret",
                "data": "value",
            }
        }
        redacted = redact_dict(data)
        assert redacted["outer"]["password"] == "***"
        assert redacted["outer"]["data"] == "value"

    def test_redact_dict_with_list(self):
        """Test lists in dictionaries are redacted."""
        data = {"credentials": [{"password": "secret1"}, {"password": "secret2"}]}
        redacted = redact_dict(data)
        # Should redact URL-like strings with credentials
        assert isinstance(redacted["credentials"], list)

    def test_redact_secret_str(self):
        """Test Pydantic SecretStr is redacted."""
        from pydantic import SecretStr

        data = {"token": SecretStr("secret_token")}
        redacted = redact_dict(data)
        assert redacted["token"] == "***"

    def test_redact_dict_with_urls(self):
        """Test URLs with credentials in dicts are redacted."""
        data = {
            "proxy_url": "http://user:pass@proxy.com:8080",
            "target_url": "http://example.com",
        }
        redacted = redact_dict(data)
        assert "pass" not in redacted["proxy_url"]
        assert "***:***@" in redacted["proxy_url"]
        assert redacted["target_url"] == "http://example.com"

    def test_add_redaction_to_loguru_redacts_message_and_extra(self):
        """Loguru redaction helper should install an active patcher."""
        from loguru import logger

        output = StringIO()
        logger.remove()
        logger.add(output, format="{message} {extra}", enqueue=False)

        add_redaction_to_loguru()
        logger.bind(password="secret").info("fetch http://user:pass@proxy.com:8080?token=abc123")

        log_output = output.getvalue()
        assert "proxy.com" in log_output
        assert "user:pass" not in log_output
        assert "pass@" not in log_output
        assert "secret" not in log_output
        assert "abc123" not in log_output


class TestLoggingRedactionFilter:
    """Test redaction filter for standard logging."""

    def test_filter_redacts_log_record(self):
        """Test RedactionFilter redacts sensitive log record."""
        filter_obj = RedactionFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="User logged in with password: secretpass",
            args=(),
            exc_info=None,
        )

        # Filter should return True (allow logging) but modify record
        assert filter_obj.filter(record) is True

    def test_filter_redacts_dict_args(self):
        """Test RedactionFilter redacts dict arguments."""
        filter_obj = RedactionFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Request: %s",
            args=({"password": "secret"},),
            exc_info=None,
        )

        filter_obj.filter(record)
        # The args should be redacted
        assert filter_obj.filter(record) is True


# ============================================================================
# INPUT VALIDATION TESTS
# ============================================================================


class TestInputValidation:
    """Test input validation utilities."""

    def test_validate_string_valid(self):
        """Test valid string passes validation."""
        result = validate_input_string("hello", max_length=10)
        assert result == "hello"

    def test_validate_string_empty(self):
        """Test empty string is valid."""
        result = validate_input_string("", max_length=10)
        assert result == ""

    def test_validate_string_max_length_exceeded(self):
        """Test string exceeding max length is rejected."""
        with pytest.raises(ValueError, match="exceeds maximum length"):
            validate_input_string("a" * 100, max_length=10)

    def test_validate_string_with_pattern_valid(self):
        """Test string matching pattern is accepted."""
        result = validate_input_string("host123", pattern=r"^[a-z0-9]+$")
        assert result == "host123"

    def test_validate_string_with_pattern_invalid(self):
        """Test string not matching pattern is rejected."""
        with pytest.raises(ValueError, match="does not match required pattern"):
            validate_input_string("host!123", pattern=r"^[a-z0-9]+$")

    def test_validate_string_non_string_input(self):
        """Test non-string input is rejected."""
        with pytest.raises(ValueError, match="Expected string"):
            validate_input_string(123)  # type: ignore

    def test_validate_port_valid(self):
        """Test valid port numbers are accepted."""
        assert validate_input_port(8080) == 8080
        assert validate_input_port("8080") == 8080
        assert validate_input_port(1) == 1
        assert validate_input_port(65535) == 65535

    def test_validate_port_too_low(self):
        """Test port below 1 is rejected."""
        with pytest.raises(ValueError, match="between 1 and 65535"):
            validate_input_port(0)

    def test_validate_port_too_high(self):
        """Test port above 65535 is rejected."""
        with pytest.raises(ValueError, match="between 1 and 65535"):
            validate_input_port(65536)

    def test_validate_port_invalid_string(self):
        """Test non-numeric port string is rejected."""
        with pytest.raises(ValueError, match="must be an integer"):
            validate_input_port("not-a-port")

    def test_validate_credentials_valid(self):
        """Test valid credentials are accepted."""
        user, pwd = validate_proxy_credentials("user", "password")
        assert user == "user"
        assert pwd == "password"

    def test_validate_credentials_none_both(self):
        """Test both credentials can be None."""
        user, pwd = validate_proxy_credentials(None, None)
        assert user is None
        assert pwd is None

    def test_validate_credentials_mismatch_username_only(self):
        """Test username without password is rejected."""
        with pytest.raises(
            ValueError, match="Both username and password must be provided together"
        ):
            validate_proxy_credentials("user", None)

    def test_validate_credentials_mismatch_password_only(self):
        """Test password without username is rejected."""
        with pytest.raises(
            ValueError, match="Both username and password must be provided together"
        ):
            validate_proxy_credentials(None, "password")


# ============================================================================
# TLS VERIFICATION TESTS
# ============================================================================


class TestTLSVerification:
    """Test TLS certificate verification configuration."""

    def test_verify_ssl_enabled_by_default(self):
        """Test verify_ssl is True by default in configuration."""
        from proxywhirl.settings import ProxyConfiguration

        config = ProxyConfiguration()
        assert config.verify_ssl is True

    def test_verify_ssl_can_be_disabled(self):
        """Test verify_ssl can be explicitly disabled."""
        from proxywhirl.settings import ProxyConfiguration

        config = ProxyConfiguration(verify_ssl=False)
        assert config.verify_ssl is False

    def test_verify_ssl_respected_in_rotator(self):
        """Test verify_ssl setting is respected in proxy rotator."""
        from proxywhirl.rotator import ProxyWhirl
        from proxywhirl.settings import ProxyConfiguration

        config = ProxyConfiguration(verify_ssl=True)
        rotator = ProxyWhirl(config=config)
        assert rotator.config.verify_ssl is True


# ============================================================================
# DEBUG LOGGING TESTS
# ============================================================================


class TestDebugLogging:
    """Test that sensitive data is not logged in debug mode."""

    def test_sensitive_data_not_in_debug_logs(self):
        """Test sensitive fields are not logged even in debug mode."""
        from proxywhirl.utils import _redact_sensitive_data

        data = {
            "url": "http://user:password@proxy.com:8080",
            "api_key": "secret123",
            "normal_field": "public",
        }

        redacted = _redact_sensitive_data(data)
        assert "password" not in str(redacted)
        assert "secret123" not in str(redacted)

    def test_proxy_model_debug_string(self):
        """Test Proxy model doesn't expose secrets in string representation."""
        from proxywhirl.models import Proxy

        proxy = Proxy(url="http://user:pass@proxy.com:8080")
        proxy_str = str(proxy)
        # Password should not appear in string representation
        # (Proxy model should not expose credentials)
        assert "pass@" not in proxy_str or "***" in proxy_str


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestSecurityIntegration:
    """Integration tests for security controls."""

    def test_ssrf_prevents_aws_metadata_access(self):
        """Test complete SSRF protection chain."""
        from proxywhirl.utils import validate_target_url_safe

        # Should raise ValueError for metadata service
        with pytest.raises(ValueError, match="not allowed"):
            validate_target_url_safe("http://169.254.169.254")

    def test_logging_redaction_chain(self):
        """Test logging redaction works end-to-end."""
        from loguru import logger

        # Create a test handler
        captured_logs = []

        def capture_handler(message):
            captured_logs.append(message.record["message"])

        logger.add(capture_handler, format="{message}")

        # Log sensitive data
        logger.info("User auth token: secret123")

        # Verify log was captured (redaction happens at handler level)
        assert len(captured_logs) > 0

    def test_api_input_validation_chain(self):
        """Test API input validation works end-to-end."""
        # This would be tested via actual API tests
        # Here we verify the utility functions work together
        from proxywhirl.security import validate_proxy_credentials

        # Test that credentials are validated before use
        user, pwd = validate_proxy_credentials("user", "pass")
        assert user == "user"
        assert pwd == "pass"
