"""
Unit tests for utility functions.
"""

import pytest

from proxywhirl.models import HealthStatus, Proxy, ProxySource
from proxywhirl.utils import (
    create_proxy_from_url,
    is_valid_proxy_url,
    parse_proxy_url,
    proxy_to_dict,
    validate_proxy_model,
)


class TestURLValidation:
    """Test URL validation functions."""

    def test_valid_http_proxy_url(self):
        """Test validation of valid HTTP proxy URL."""
        assert is_valid_proxy_url("http://proxy.example.com:8080") is True

    def test_valid_https_proxy_url(self):
        """Test validation of valid HTTPS proxy URL."""
        assert is_valid_proxy_url("https://proxy.example.com:8080") is True

    def test_valid_socks4_proxy_url(self):
        """Test validation of valid SOCKS4 proxy URL."""
        assert is_valid_proxy_url("socks4://proxy.example.com:1080") is True

    def test_valid_socks5_proxy_url(self):
        """Test validation of valid SOCKS5 proxy URL."""
        assert is_valid_proxy_url("socks5://proxy.example.com:1080") is True

    def test_valid_proxy_url_with_auth(self):
        """Test validation of proxy URL with authentication."""
        assert is_valid_proxy_url("http://user:pass@proxy.example.com:8080") is True

    def test_invalid_proxy_url_no_port(self):
        """Test validation fails for URL without port."""
        assert is_valid_proxy_url("http://proxy.example.com") is False

    def test_invalid_proxy_url_wrong_scheme(self):
        """Test validation fails for invalid scheme."""
        assert is_valid_proxy_url("ftp://proxy.example.com:8080") is False

    def test_invalid_proxy_url_malformed(self):
        """Test validation fails for malformed URL."""
        assert is_valid_proxy_url("not-a-url") is False


class TestURLParsing:
    """Test URL parsing functions."""

    def test_parse_simple_http_url(self):
        """Test parsing simple HTTP proxy URL."""
        result = parse_proxy_url("http://proxy.example.com:8080")
        assert result["protocol"] == "http"
        assert result["host"] == "proxy.example.com"
        assert result["port"] == 8080
        assert result["username"] is None
        assert result["password"] is None

    def test_parse_url_with_credentials(self):
        """Test parsing proxy URL with credentials."""
        result = parse_proxy_url("http://user:pass@proxy.example.com:8080")
        assert result["protocol"] == "http"
        assert result["host"] == "proxy.example.com"
        assert result["port"] == 8080
        assert result["username"] == "user"
        assert result["password"] == "pass"

    def test_parse_socks5_url(self):
        """Test parsing SOCKS5 proxy URL."""
        result = parse_proxy_url("socks5://proxy.example.com:1080")
        assert result["protocol"] == "socks5"
        assert result["host"] == "proxy.example.com"
        assert result["port"] == 1080

    def test_parse_invalid_url_raises_error(self):
        """Test that parsing invalid URL raises ValueError."""
        with pytest.raises(ValueError, match="Invalid proxy URL"):
            parse_proxy_url("not-a-valid-url")


class TestProxyValidation:
    """Test proxy model validation functions."""

    def test_validate_valid_proxy(self):
        """Test validation of valid proxy returns empty error list."""
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        errors = validate_proxy_model(proxy)
        assert len(errors) == 0

    def test_validate_proxy_with_credentials(self):
        """Test validation of proxy with credentials."""
        from pydantic import SecretStr

        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("user"),
            password=SecretStr("pass"),
        )  # type: ignore
        errors = validate_proxy_model(proxy)
        assert len(errors) == 0

    def test_validate_proxy_inconsistent_stats(self):
        """Test validation detects inconsistent statistics."""
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        proxy.total_requests = 5
        proxy.total_successes = 3
        proxy.total_failures = 4  # 3 + 4 > 5, inconsistent!

        errors = validate_proxy_model(proxy)
        assert len(errors) > 0
        assert "Inconsistent stats" in errors[0]

    def test_validate_proxy_negative_consecutive_failures(self):
        """Test validation detects negative consecutive failures."""
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        proxy.consecutive_failures = -1

        errors = validate_proxy_model(proxy)
        assert len(errors) > 0
        assert "consecutive_failures" in errors[0]


class TestProxyDictConversion:
    """Test proxy to dictionary conversion."""

    def test_proxy_to_dict_basic(self):
        """Test basic proxy to dict conversion."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            source=ProxySource.USER,
        )  # type: ignore
        result = proxy_to_dict(proxy)

        assert result["url"] == "http://proxy.example.com:8080"
        assert result["protocol"] == "http"
        assert result["health_status"] == "healthy"
        assert result["source"] == "user"
        assert "stats" in result

    def test_proxy_to_dict_with_tags(self):
        """Test proxy to dict includes tags."""
        proxy = Proxy(
            url="http://proxy.example.com:8080", tags={"fast", "us"}
        )  # type: ignore
        result = proxy_to_dict(proxy)

        assert "tags" in result
        assert set(result["tags"]) == {"fast", "us"}

    def test_proxy_to_dict_without_stats(self):
        """Test proxy to dict without stats."""
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        result = proxy_to_dict(proxy, include_stats=False)

        assert "stats" not in result
        assert "url" in result

    def test_proxy_to_dict_with_stats(self):
        """Test proxy to dict includes detailed stats."""
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        proxy.record_success(100.0)
        proxy.record_failure()

        result = proxy_to_dict(proxy, include_stats=True)

        assert result["stats"]["total_requests"] == 2
        assert result["stats"]["total_successes"] == 1
        assert result["stats"]["total_failures"] == 1
        assert result["stats"]["success_rate"] == 0.5


class TestCreateProxyFromURL:
    """Test creating proxy from URL string."""

    def test_create_proxy_from_simple_url(self):
        """Test creating proxy from simple URL."""
        proxy = create_proxy_from_url("http://proxy.example.com:8080")

        assert proxy.url == "http://proxy.example.com:8080"
        assert proxy.protocol == "http"
        assert proxy.source == ProxySource.USER

    def test_create_proxy_from_url_with_source(self):
        """Test creating proxy with specific source."""
        proxy = create_proxy_from_url(
            "http://proxy.example.com:8080", source=ProxySource.FETCHED
        )

        assert proxy.source == ProxySource.FETCHED

    def test_create_proxy_from_url_with_tags(self):
        """Test creating proxy with tags."""
        proxy = create_proxy_from_url(
            "http://proxy.example.com:8080", tags={"fast", "us"}
        )

        assert proxy.tags == {"fast", "us"}

    def test_create_proxy_from_invalid_url_accepts_any_string(self):
        """Test that creating proxy accepts any string (validation happens separately)."""
        # Since we allow any string for url field, invalid URLs get accepted by Pydantic
        # Validation logic can check them separately with validate_proxy_model
        proxy = create_proxy_from_url("not-a-valid-url")
        assert proxy.url == "not-a-valid-url"


class TestProxyCredentialsModel:
    """Test ProxyCredentials model methods."""

    def test_to_httpx_auth(self):
        """Test conversion to httpx BasicAuth object."""
        import httpx
        from pydantic import SecretStr

        from proxywhirl.models import ProxyCredentials

        creds = ProxyCredentials(
            username=SecretStr("testuser"), password=SecretStr("testpass")
        )

        auth = creds.to_httpx_auth()
        assert isinstance(auth, httpx.BasicAuth)
        # httpx.BasicAuth stores username/password internally, we verify the type is correct

    def test_to_dict_revealed(self):
        """Test to_dict with reveal=True."""
        from pydantic import SecretStr

        from proxywhirl.models import ProxyCredentials

        creds = ProxyCredentials(
            username=SecretStr("testuser"),
            password=SecretStr("testpass"),
            auth_type="basic",
            additional_headers={"X-Custom": "value"},
        )

        result = creds.to_dict(reveal=True)
        assert result["username"] == "testuser"
        assert result["password"] == "testpass"
        assert result["auth_type"] == "basic"
        assert result["additional_headers"] == {"X-Custom": "value"}

    def test_to_dict_redacted(self):
        """Test to_dict with reveal=False (default)."""
        from pydantic import SecretStr

        from proxywhirl.models import ProxyCredentials

        creds = ProxyCredentials(
            username=SecretStr("testuser"), password=SecretStr("testpass")
        )

        result = creds.to_dict(reveal=False)
        assert result["username"] == "**********"
        assert result["password"] == "**********"


class TestProxyConfiguration:
    """Test ProxyConfiguration model validation."""

    def test_valid_configuration(self):
        """Test creating valid configuration."""
        from proxywhirl.models import ProxyConfiguration

        config = ProxyConfiguration()
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.verify_ssl is True

    def test_configuration_with_custom_values(self):
        """Test configuration with custom values."""
        from proxywhirl.models import ProxyConfiguration

        config = ProxyConfiguration(
            timeout=60, max_retries=5, verify_ssl=False, log_level="DEBUG"
        )
        assert config.timeout == 60
        assert config.max_retries == 5
        assert config.verify_ssl is False
        assert config.log_level == "DEBUG"

    def test_configuration_negative_timeout_raises_error(self):
        """Test that negative timeout raises validation error."""
        from pydantic import ValidationError

        from proxywhirl.models import ProxyConfiguration

        with pytest.raises(ValidationError, match="positive"):
            ProxyConfiguration(timeout=-1)

    def test_configuration_storage_backend_requires_path(self):
        """Test that sqlite/file storage requires path."""
        from pydantic import ValidationError

        from proxywhirl.models import ProxyConfiguration

        with pytest.raises(ValidationError, match="storage_path required"):
            ProxyConfiguration(storage_backend="sqlite")
