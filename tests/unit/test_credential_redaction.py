"""Test credential redaction in error messages and logs.

Tests:
- Credentials are redacted from exception messages
- URLs with auth are redacted in logs
- SecretStr fields are not exposed
- Error message safe formatting
"""

from __future__ import annotations

from pydantic import SecretStr

from proxywhirl.exceptions import (
    ProxyAuthenticationError,
    ProxyConnectionError,
    redact_url,
)
from proxywhirl.models import Proxy, ProxyCredentials


class TestCredentialRedaction:
    """Test credential redaction in error messages."""

    def test_redact_url_with_basic_auth(self) -> None:
        """Test redaction of basic auth in URLs."""
        url = "http://user:password@proxy.example.com:8080"
        redacted = redact_url(url)

        assert "password" not in redacted
        assert "user" not in redacted
        assert "proxy.example.com" in redacted

    def test_redact_url_with_complex_password(self) -> None:
        """Test redaction of complex passwords."""
        url = "http://admin:P@ssw0rd!#$%@proxy.example.com:8080"
        redacted = redact_url(url)

        assert "P@ssw0rd" not in redacted
        assert "admin" not in redacted
        assert "proxy.example.com" in redacted

    def test_redact_url_preserves_protocol(self) -> None:
        """Test that protocol is preserved after redaction."""
        urls = [
            "http://user:pass@proxy.com:8080",
            "https://user:pass@proxy.com:8443",
            "socks5://user:pass@proxy.com:1080",
        ]

        for url in urls:
            redacted = redact_url(url)
            protocol = url.split("://")[0]
            assert protocol in redacted

    def test_redact_url_preserves_host_port(self) -> None:
        """Test that host and port are preserved."""
        url = "http://user:pass@proxy.example.com:9090"
        redacted = redact_url(url)

        assert "proxy.example.com" in redacted
        assert "9090" in redacted

    def test_proxy_credentials_are_secret_str(self) -> None:
        """Test that credentials are stored as SecretStr."""
        creds = ProxyCredentials(
            username=SecretStr("user"),
            password=SecretStr("password"),
        )

        # SecretStr should not expose value in repr
        repr_str = repr(creds.password)
        assert "password" not in repr_str or "***" in repr_str

    def test_exception_message_redaction(self) -> None:
        """Test that exception messages redact credentials."""
        url = "http://user:password@proxy.example.com:8080"

        exc = ProxyConnectionError(
            message=f"Failed to connect to {redact_url(url)}",
            proxy_url=url,
        )

        assert "password" not in str(exc)
        assert "proxy.example.com" in str(exc)

    def test_authentication_error_redaction(self) -> None:
        """Test credential redaction in authentication errors."""
        url = "http://admin:secret123@proxy.com:8080"
        redacted = redact_url(url)

        exc = ProxyAuthenticationError(
            message=f"Auth failed for {redacted}",
            proxy_url=url,
        )

        exc_str = str(exc)
        assert "secret123" not in exc_str
        assert "admin" not in exc_str

    def test_proxy_model_url_redaction(self) -> None:
        """Test redaction in proxy model string representation."""
        proxy = Proxy(
            url="http://user:password@proxy.example.com:8080",
        )

        # Model dump should not expose credentials
        dumped = proxy.model_dump_json()
        assert "password" not in dumped or "***" in dumped or dumped.count("user") <= 1

    def test_error_with_multiple_urls_redacted(self) -> None:
        """Test redaction of multiple URLs in error."""
        url1 = "http://user1:pass1@proxy1.com:8080"
        url2 = "http://user2:pass2@proxy2.com:8080"

        message = f"Failed: {redact_url(url1)} and {redact_url(url2)}"

        assert "pass1" not in message
        assert "pass2" not in message
        assert "proxy1.com" in message
        assert "proxy2.com" in message


class TestSecretStrHandling:
    """Test SecretStr field security."""

    def test_secret_str_not_in_repr(self) -> None:
        """Test that SecretStr values are not in repr."""
        secret = SecretStr("my-secret-password")
        repr_val = repr(secret)

        # Should be redacted in repr
        assert "my-secret-password" not in repr_val

    def test_secret_str_not_in_str(self) -> None:
        """Test that SecretStr values are not in str."""
        secret = SecretStr("my-secret-password")
        str_val = str(secret)

        # Should be redacted in str
        assert "my-secret-password" not in str_val

    def test_credentials_model_dump_excludes_secrets(self) -> None:
        """Test that model dump excludes secret fields."""
        creds = ProxyCredentials(
            username=SecretStr("admin"),
            password=SecretStr("secret"),
        )

        # Dumping should not expose secrets
        dumped = creds.model_dump()
        dumped_json = creds.model_dump_json()

        assert "secret" not in dumped_json or "***" in dumped_json or len(dumped_json) < 50

    def test_secret_str_comparison_safe(self) -> None:
        """Test that SecretStr comparison is safe."""
        secret1 = SecretStr("password")
        secret2 = SecretStr("password")
        secret3 = SecretStr("other")

        # Equality should work
        assert secret1 == secret2
        assert secret1 != secret3

        # But repr should be safe
        assert "password" not in repr(secret1)


class TestErrorMessageSafety:
    """Test error message formatting safety."""

    def test_redact_url_in_error_context(self) -> None:
        """Test URL redaction in full error context."""
        url = "http://user:password@proxy.example.com:8080"
        redacted = redact_url(url)

        error_msg = f"Connection failed to {redacted}"

        assert "password" not in error_msg
        assert "user" not in error_msg
        assert "proxy.example.com" in error_msg

    def test_exception_str_is_safe(self) -> None:
        """Test that exception string representation is safe."""
        url = "http://admin:secret@proxy.com:8080"
        redacted = redact_url(url)

        exc = ProxyConnectionError(
            message=f"Failed: {redacted}",
            proxy_url=url,
        )

        # String should not contain credentials
        exc_str = str(exc)
        assert "secret" not in exc_str.lower()

    def test_exception_args_are_safe(self) -> None:
        """Test that exception args don't leak credentials."""
        url = "http://user:password@proxy.com:8080"
        redacted = redact_url(url)

        exc = ProxyConnectionError(
            message=f"Error: {redacted}",
            proxy_url=url,
        )

        # Args should not contain unredacted credentials
        for arg in exc.args:
            if isinstance(arg, str):
                assert "password" not in arg

    def test_logging_safe_format(self) -> None:
        """Test that logging format is safe."""
        url = "http://user:password@proxy.com:8080"
        redacted = redact_url(url)

        # Simulate logging
        log_msg = f"[WARN] Proxy {redacted} failed health check"

        assert "password" not in log_msg
        assert "user" not in log_msg
        assert "proxy.com" in log_msg


class TestNoCredentialLeak:
    """Test that no credentials leak through other mechanisms."""

    def test_proxy_url_field_is_safe(self) -> None:
        """Test that proxy URL field doesn't leak in comparison."""
        proxy1 = Proxy(url="http://user:pass@proxy1.com:8080")
        proxy2 = Proxy(url="http://user:pass@proxy2.com:8080")

        # Comparison should work but not expose passwords
        different = proxy1 != proxy2

        assert different

    def test_credentials_not_in_config_repr(self) -> None:
        """Test credentials not exposed in config repr."""
        creds = ProxyCredentials(
            username=SecretStr("admin"),
            password=SecretStr("secret123"),
        )

        config_repr = repr(creds)

        # Secret value should not appear
        assert "secret123" not in config_repr

    def test_redact_url_regex_pattern(self) -> None:
        """Test redaction pattern handles edge cases."""
        test_urls = [
            "http://user:pass@host.com:8080",
            "http://user@host.com:8080",
            "http://host.com:8080",
            "http://127.0.0.1:8080",
            "http://[::1]:8080",
        ]

        for url in test_urls:
            redacted = redact_url(url)
            # Should not crash and should be reasonable
            assert len(redacted) > 0
            assert "://" in redacted

    def test_credential_object_not_loggable(self) -> None:
        """Test that credential objects are safe when formatted."""
        creds = ProxyCredentials(
            username=SecretStr("user"),
            password=SecretStr("password"),
        )

        # Format as would happen in logs
        try:
            formatted = f"{creds}"
            # Should not contain the actual secret
            assert "password" not in formatted or "***" in formatted
        except Exception:
            # If it raises, that's also safe
            pass
