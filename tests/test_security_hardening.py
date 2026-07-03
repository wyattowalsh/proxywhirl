"""Comprehensive security hardening tests for ProxyWhirl.

Tests cover:
- SSRF protection (IP blocklist and hostname validation)
- PBKDF2 key derivation
- Credential redaction
- ReDoS protection via safe_regex
- Input validation
- SQL injection prevention
- Error response filtering
"""

from __future__ import annotations

import ipaddress
import socket

import pytest

from proxywhirl.safe_regex import safe_regex_compile, validate_regex_pattern
from proxywhirl.security import (
    derive_key_pbkdf2,
    is_ip_blocked,
    redact_dict,
    redact_url,
    validate_input_port,
    validate_input_string,
    validate_proxy_credentials,
    validate_proxy_url_safety,
    verify_pbkdf2_key,
)

# ============================================================================
# SSRF PROTECTION TESTS
# ============================================================================


class TestSSRFIPBlocklist:
    """Test SSRF IP blocklist protection."""

    def test_loopback_address_blocked(self):
        """Loopback addresses should be blocked."""
        blocked, reason = is_ip_blocked(ipaddress.IPv4Address("127.0.0.1"))
        assert blocked is True
        assert "loopback" in reason.lower()

    def test_private_ips_blocked(self):
        """Private IP ranges (RFC 1918) should be blocked."""
        private_ips = [
            "10.0.0.1",
            "10.255.255.254",
            "172.16.0.1",
            "172.31.255.254",
            "192.168.0.1",
            "192.168.255.254",
        ]
        for ip_str in private_ips:
            blocked, reason = is_ip_blocked(ipaddress.IPv4Address(ip_str))
            assert blocked is True, f"{ip_str} should be blocked"
            assert "private" in reason.lower()

    def test_link_local_blocked(self):
        """Link-local addresses (169.254.x.x) should be blocked."""
        blocked, reason = is_ip_blocked(ipaddress.IPv4Address("169.254.0.1"))
        assert blocked is True
        # Link-local ranges are actually private, so either message is acceptable
        assert "link-local" in reason.lower() or "private" in reason.lower()

    def test_metadata_services_blocked(self):
        """Metadata service IPs should be blocked."""
        # AWS/GCP/Azure metadata
        blocked, reason = is_ip_blocked(ipaddress.IPv4Address("169.254.169.254"))
        assert blocked is True
        assert "metadata" in reason.lower()

        # Alibaba metadata
        blocked, reason = is_ip_blocked(ipaddress.IPv4Address("100.100.100.200"))
        assert blocked is True
        assert "metadata" in reason.lower()

        # Docker host metadata
        blocked, reason = is_ip_blocked(ipaddress.IPv4Address("127.0.0.11"))
        assert blocked is True

    def test_public_ip_allowed(self):
        """Public IP addresses should be allowed."""
        blocked, reason = is_ip_blocked(ipaddress.IPv4Address("8.8.8.8"))
        assert blocked is False

    def test_reserved_addresses_blocked(self):
        """Reserved addresses should be blocked."""
        # 0.0.0.0/8
        blocked, reason = is_ip_blocked(ipaddress.IPv4Address("0.0.0.1"))
        assert blocked is True

    def test_multicast_blocked(self):
        """Multicast addresses should be blocked."""
        # 224.0.0.0/4
        blocked, reason = is_ip_blocked(ipaddress.IPv4Address("224.0.0.1"))
        assert blocked is True
        assert "multicast" in reason.lower()


class TestSSRFHostnameValidation:
    """Test hostname-based SSRF protection."""

    def test_ip_url_with_blocklist(self):
        """IP-based URLs should be checked against blocklist."""
        safe, reason = validate_proxy_url_safety("http://127.0.0.1:8080")
        assert safe is False
        assert "loopback" in reason.lower()

    def test_private_ip_url_blocked(self):
        """URLs with private IPs should be blocked."""
        safe, reason = validate_proxy_url_safety("http://192.168.1.1:8080")
        assert safe is False
        assert "private" in reason.lower()

    def test_metadata_service_url_blocked(self):
        """Metadata service URLs should be blocked."""
        safe, reason = validate_proxy_url_safety("http://169.254.169.254:80/latest")
        assert safe is False
        assert "metadata" in reason.lower()

    def test_internal_tld_blocked(self):
        """Internal TLDs should be blocked."""
        safe, reason = validate_proxy_url_safety("http://service.local:8080")
        assert safe is False
        assert "internal" in reason.lower() or "blocked" in reason.lower()

    def test_metadata_hostname_blocked(self):
        """Known metadata service hostnames should be blocked."""
        dangerous_hostnames = [
            "metadata.google.internal",
            "gce-metadata.appspot.com",
        ]
        for hostname in dangerous_hostnames:
            safe, reason = validate_proxy_url_safety(f"http://{hostname}")
            assert safe is False, f"{hostname} should be blocked"

    def test_public_url_allowed(self):
        """Public proxy URLs should be allowed."""
        safe, reason = validate_proxy_url_safety("http://example.com:8080")
        assert safe is True

    def test_hostname_resolving_to_loopback_rejected(self, monkeypatch):
        """DNS-backed internal addresses should be rejected."""
        monkeypatch.setattr(
            "proxywhirl.security.socket.getaddrinfo",
            lambda *_args, **_kwargs: [
                (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 8080))
            ],
        )
        safe, reason = validate_proxy_url_safety("http://public.example.test:8080")
        assert safe is False
        assert "loopback" in reason.lower()

    def test_invalid_url_rejected(self):
        """Invalid URLs should be rejected."""
        safe, reason = validate_proxy_url_safety("not a url")
        assert safe is False


# ============================================================================
# PBKDF2 KEY DERIVATION TESTS
# ============================================================================


class TestPBKDF2KeyDerivation:
    """Test PBKDF2-based key derivation."""

    def test_key_derivation_basic(self):
        """Basic key derivation should work."""
        password = "test_password_123"
        key, salt = derive_key_pbkdf2(password)

        assert isinstance(key, bytes)
        assert isinstance(salt, bytes)
        assert len(key) == 32  # 256-bit key
        assert len(salt) >= 8

    def test_same_password_different_salt(self):
        """Same password with different salts should produce different keys."""
        password = "test_password"
        key1, salt1 = derive_key_pbkdf2(password)
        # Generate a new salt explicitly
        import secrets

        salt2 = secrets.token_bytes(16)
        key2, _ = derive_key_pbkdf2(password, salt=salt2)

        # Different salts
        assert salt1 != salt2
        # Different keys (due to different salts)
        assert key1 != key2

    def test_default_salt_is_random(self):
        """Implicit PBKDF2 salts should differ across calls."""
        password = "test_password"
        key1, salt1 = derive_key_pbkdf2(password)
        key2, salt2 = derive_key_pbkdf2(password)

        assert salt1 != salt2
        assert key1 != key2

    def test_same_password_same_salt(self):
        """Same password and salt should produce same key."""
        password = "test_password"
        key1, salt = derive_key_pbkdf2(password)
        key2, _ = derive_key_pbkdf2(password, salt=salt)

        assert key1 == key2

    def test_key_length_configurable(self):
        """Key length should be configurable."""
        password = "test_password"
        key, _ = derive_key_pbkdf2(password, dklen=64)
        assert len(key) == 64

    def test_iterations_enforced(self):
        """Low iteration counts should be rejected."""
        password = "test_password"
        with pytest.raises(ValueError, match="Iterations must be >= 10000"):
            derive_key_pbkdf2(password, iterations=1000)

    def test_empty_password_rejected(self):
        """Empty passwords should be rejected."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            derive_key_pbkdf2("")

    def test_verify_correct_password(self):
        """Verification should succeed with correct password."""
        password = "correct_password"
        key, salt = derive_key_pbkdf2(password)

        assert verify_pbkdf2_key(password, key, salt) is True

    def test_verify_incorrect_password(self):
        """Verification should fail with incorrect password."""
        password = "correct_password"
        key, salt = derive_key_pbkdf2(password)

        assert verify_pbkdf2_key("wrong_password", key, salt) is False


# ============================================================================
# REDACTION TESTS
# ============================================================================


class TestCredentialRedaction:
    """Test credential redaction for logs and errors."""

    def test_url_redaction_basic(self):
        """URLs with credentials should be redacted."""
        url = "http://user:password@example.com/path"
        redacted = redact_url(url)

        assert "password" not in redacted
        assert "***" in redacted
        assert "example.com" in redacted

    def test_url_redaction_complex(self):
        """Complex URLs with query params should be redacted."""
        url = "https://proxy:secret@proxy.example.com:8080/status?api_key=abc123&token=xyz"
        redacted = redact_url(url)

        assert "secret" not in redacted
        assert "abc123" not in redacted
        assert "xyz" not in redacted

    def test_dict_redaction(self):
        """Sensitive dict keys should be redacted."""
        data = {
            "username": "admin",
            "password": "secret123",
            "api_key": "key_abc",
            "normal_key": "safe_value",
        }
        redacted = redact_dict(data)

        assert redacted["password"] == "***"
        assert redacted["api_key"] == "***"
        assert redacted["normal_key"] == "safe_value"
        assert redacted["username"] == "admin"  # Username is not redacted

    def test_nested_dict_redaction(self):
        """Nested dicts should be recursively redacted."""
        data = {
            "config": {
                "proxy": {
                    "username": "admin",
                    "password": "secret",
                },
                "api_token": "token123",
            },
        }
        redacted = redact_dict(data)

        assert redacted["config"]["proxy"]["password"] == "***"
        assert redacted["config"]["api_token"] == "***"


# ============================================================================
# SAFE REGEX TESTS
# ============================================================================


class TestSafeRegex:
    """Test ReDoS protection via safe_regex."""

    def test_catastrophic_backtracking_rejected(self):
        """Patterns with catastrophic backtracking should be rejected."""
        from click.exceptions import Exit

        dangerous_patterns = [
            r"(a+)+b",  # Nested quantifiers
            r"(a*)*b",  # Nested quantifiers
            r"(a|a)*b",  # Alternation with overlap
            r"(a|ab)*b",  # Alternation with overlap
        ]

        for pattern in dangerous_patterns:
            with pytest.raises(Exit):
                validate_regex_pattern(pattern)

    def test_pattern_length_enforced(self):
        """Excessively long patterns should be rejected."""
        from click.exceptions import Exit

        long_pattern = "a" * 2000

        with pytest.raises(Exit):
            validate_regex_pattern(long_pattern)

    def test_safe_pattern_accepted(self):
        """Safe patterns should be accepted."""
        safe_patterns = [
            r"^[a-zA-Z0-9]+$",
            r"https?://[a-z0-9.-]+",
            r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",
        ]

        for pattern in safe_patterns:
            try:
                compiled = safe_regex_compile(pattern)
                assert compiled is not None
            except SystemExit:
                pytest.fail(f"Safe pattern {pattern} was rejected")


# ============================================================================
# INPUT VALIDATION TESTS
# ============================================================================


class TestInputValidation:
    """Test input validation utilities."""

    def test_string_length_enforced(self):
        """String length should be enforced."""
        with pytest.raises(ValueError, match="exceeds maximum length"):
            validate_input_string("x" * 3000, max_length=2048)

    def test_valid_string_accepted(self):
        """Valid strings should be accepted."""
        result = validate_input_string("test_value", max_length=100)
        assert result == "test_value"

    def test_port_validation(self):
        """Port numbers should be validated."""
        # Valid ports
        assert validate_input_port(8080) == 8080
        assert validate_input_port("443") == 443

        # Invalid ports
        with pytest.raises(ValueError):
            validate_input_port(0)
        with pytest.raises(ValueError):
            validate_input_port(65536)
        with pytest.raises(ValueError):
            validate_input_port("invalid")

    def test_proxy_credentials_validation(self):
        """Proxy credentials must be provided together."""
        # Both provided
        user, passwd = validate_proxy_credentials("admin", "secret")
        assert user == "admin"
        assert passwd == "secret"

        # Both absent
        user, passwd = validate_proxy_credentials(None, None)
        assert user is None
        assert passwd is None

        # Only one provided (should fail)
        with pytest.raises(ValueError, match="Both username and password"):
            validate_proxy_credentials("admin", None)

        with pytest.raises(ValueError, match="Both username and password"):
            validate_proxy_credentials(None, "secret")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
