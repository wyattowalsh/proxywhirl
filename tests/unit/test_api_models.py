"""Unit tests for API models validation (api_models.py).

Tests the Pydantic validation logic for API request/response models.
"""

import pytest
from pydantic import HttpUrl, SecretStr, ValidationError

from proxywhirl.api.models import CreateProxyRequest, ProxiedRequest, UpdateConfigRequest


# T016: Unit test for request validation
class TestProxiedRequestValidation:
    """Test ProxiedRequest model validation."""

    def test_proxied_request_valid_url(self):
        """Test ProxiedRequest accepts valid URL."""
        # Arrange & Act
        request = ProxiedRequest(
            url=HttpUrl("https://example.com/api"),
            method="GET",
            headers={"User-Agent": "Test"},
            timeout=30,
        )

        # Assert
        assert str(request.url) == "https://example.com/api"
        assert request.method == "GET"
        assert request.timeout == 30

    def test_proxied_request_invalid_url_format(self):
        """Test ProxiedRequest rejects invalid URL format."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ProxiedRequest(
                url="not-a-valid-url",  # type: ignore[arg-type]
                method="GET",
                timeout=30,
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("url",) for error in errors)

    def test_proxied_request_invalid_http_method(self):
        """Test ProxiedRequest rejects invalid HTTP method."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ProxiedRequest(
                url=HttpUrl("https://example.com"),
                method="INVALID",  # type: ignore[arg-type]
                timeout=30,
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("method",) for error in errors)

    def test_proxied_request_negative_timeout(self):
        """Test ProxiedRequest rejects negative timeout."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ProxiedRequest(
                url=HttpUrl("https://example.com"),
                method="GET",
                timeout=-1,  # type: ignore[arg-type]
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("timeout",) for error in errors)

    def test_proxied_request_zero_timeout(self):
        """Test ProxiedRequest rejects zero timeout."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ProxiedRequest(
                url=HttpUrl("https://example.com"),
                method="GET",
                timeout=0,  # type: ignore[arg-type]
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("timeout",) for error in errors)

    def test_proxied_request_valid_methods(self):
        """Test ProxiedRequest accepts all valid HTTP methods."""
        valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]

        for method in valid_methods:
            # Arrange & Act
            request = ProxiedRequest(
                url=HttpUrl("https://example.com"),
                method=method,  # type: ignore[arg-type]
                timeout=30,
            )

            # Assert
            assert request.method == method

    def test_proxied_request_optional_fields(self):
        """Test ProxiedRequest works with minimal required fields."""
        # Arrange & Act
        request = ProxiedRequest(
            url=HttpUrl("https://example.com"),
            method="GET",
            timeout=30,
        )

        # Assert
        assert request.headers is None or request.headers == {}
        assert request.body is None

    def test_proxied_request_with_body(self):
        """Test ProxiedRequest handles request body."""
        # Arrange & Act
        request = ProxiedRequest(
            url=HttpUrl("https://example.com"),
            method="POST",
            body='{"key": "value"}',
            timeout=30,
        )

        # Assert
        assert request.body == '{"key": "value"}'

    def test_proxied_request_with_headers(self):
        """Test ProxiedRequest handles custom headers."""
        # Arrange
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token123",
            "User-Agent": "ProxyWhirl/1.0",
        }

        # Act
        request = ProxiedRequest(
            url=HttpUrl("https://example.com"),
            method="GET",
            headers=headers,
            timeout=30,
        )

        # Assert
        assert request.headers == headers

    def test_proxied_request_default_timeout(self):
        """Test ProxiedRequest has sensible default timeout."""
        # Arrange & Act
        request = ProxiedRequest(
            url=HttpUrl("https://example.com"),
            method="GET",
            timeout=30,
        )

        # Assert
        assert request.timeout == 30
        assert request.timeout > 0

    # TASK-004: New validation tests

    def test_proxied_request_rejects_ftp_scheme(self):
        """Test ProxiedRequest rejects FTP URLs."""
        with pytest.raises(ValidationError) as exc_info:
            ProxiedRequest(
                url="ftp://example.com/file",  # type: ignore[arg-type]
                method="GET",
                timeout=30,
            )

        errors = exc_info.value.errors()
        assert any("scheme" in str(error).lower() for error in errors)

    def test_proxied_request_rejects_socks5_scheme(self):
        """Test ProxiedRequest rejects SOCKS5 URLs."""
        with pytest.raises(ValidationError) as exc_info:
            ProxiedRequest(
                url="socks5://proxy.example.com:1080",  # type: ignore[arg-type]
                method="GET",
                timeout=30,
            )

        errors = exc_info.value.errors()
        assert any("scheme" in str(error).lower() for error in errors)

    def test_proxied_request_accepts_http_scheme(self):
        """Test ProxiedRequest accepts HTTP URLs."""
        request = ProxiedRequest(
            url=HttpUrl("http://example.com"),
            method="GET",
            timeout=30,
        )
        assert str(request.url).startswith("http://")

    def test_proxied_request_accepts_https_scheme(self):
        """Test ProxiedRequest accepts HTTPS URLs."""
        request = ProxiedRequest(
            url=HttpUrl("https://example.com"),
            method="GET",
            timeout=30,
        )
        assert str(request.url).startswith("https://")

    def test_proxied_request_rejects_url_too_long(self):
        """Test ProxiedRequest rejects URLs longer than 2048 chars."""
        long_url = "https://example.com/" + "a" * 2050
        with pytest.raises(ValidationError) as exc_info:
            ProxiedRequest(
                url=long_url,  # type: ignore[arg-type]
                method="GET",
                timeout=30,
            )

        errors = exc_info.value.errors()
        assert any("2048" in str(error) for error in errors)

    def test_proxied_request_accepts_url_max_length(self):
        """Test ProxiedRequest accepts URL at max length."""
        # Create a URL that's exactly at the limit
        path = "a" * (2048 - len("https://example.com/"))
        url = f"https://example.com/{path}"
        request = ProxiedRequest(
            url=url,  # type: ignore[arg-type]
            method="GET",
            timeout=30,
        )
        assert len(str(request.url)) <= 2048

    def test_proxied_request_rejects_header_name_too_long(self):
        """Test ProxiedRequest rejects header names longer than 256 chars."""
        long_header_name = "X-Custom-" + "a" * 250
        with pytest.raises(ValidationError) as exc_info:
            ProxiedRequest(
                url=HttpUrl("https://example.com"),
                method="GET",
                headers={long_header_name: "value"},
                timeout=30,
            )

        errors = exc_info.value.errors()
        assert any("256" in str(error) for error in errors)

    def test_proxied_request_rejects_header_value_too_long(self):
        """Test ProxiedRequest rejects header values longer than 2048 chars."""
        long_value = "a" * 2050
        with pytest.raises(ValidationError) as exc_info:
            ProxiedRequest(
                url=HttpUrl("https://example.com"),
                method="GET",
                headers={"X-Custom": long_value},
                timeout=30,
            )

        errors = exc_info.value.errors()
        assert any("2048" in str(error) for error in errors)

    def test_proxied_request_rejects_body_too_long(self):
        """Test ProxiedRequest rejects body longer than 1MB."""
        long_body = "a" * (1048576 + 1)  # 1MB + 1
        with pytest.raises(ValidationError) as exc_info:
            ProxiedRequest(
                url=HttpUrl("https://example.com"),
                method="POST",
                body=long_body,
                timeout=30,
            )

        errors = exc_info.value.errors()
        assert any("1mb" in str(error).lower() or "1,048,576" in str(error) for error in errors)

    def test_proxied_request_accepts_body_max_length(self):
        """Test ProxiedRequest accepts body at max length."""
        max_body = "a" * 1048576  # Exactly 1MB
        request = ProxiedRequest(
            url=HttpUrl("https://example.com"),
            method="POST",
            body=max_body,
            timeout=30,
        )
        assert len(request.body) == 1048576


class TestCreateProxyRequestValidation:
    """Test CreateProxyRequest model validation."""

    def test_create_proxy_accepts_http_scheme(self):
        """Test CreateProxyRequest accepts HTTP proxy URLs."""
        request = CreateProxyRequest(url="http://proxy.example.com:8080")
        assert request.url.startswith("http://")

    def test_create_proxy_accepts_https_scheme(self):
        """Test CreateProxyRequest accepts HTTPS proxy URLs."""
        request = CreateProxyRequest(url="https://proxy.example.com:8080")
        assert request.url.startswith("https://")

    def test_create_proxy_accepts_socks4_scheme(self):
        """Test CreateProxyRequest accepts SOCKS4 proxy URLs."""
        request = CreateProxyRequest(
            url="socks4://proxy.example.com:1080"  # type: ignore[arg-type]
        )
        assert "socks4" in str(request.url).lower()

    def test_create_proxy_accepts_socks5_scheme(self):
        """Test CreateProxyRequest accepts SOCKS5 proxy URLs."""
        request = CreateProxyRequest(
            url="socks5://proxy.example.com:1080"  # type: ignore[arg-type]
        )
        assert "socks5" in str(request.url).lower()

    def test_create_proxy_rejects_ftp_scheme(self):
        """Test CreateProxyRequest rejects FTP URLs."""
        with pytest.raises(ValidationError) as exc_info:
            CreateProxyRequest(
                url="ftp://proxy.example.com:21"  # type: ignore[arg-type]
            )

        errors = exc_info.value.errors()
        assert any("scheme" in str(error).lower() for error in errors)

    def test_create_proxy_rejects_invalid_port(self):
        """Test CreateProxyRequest rejects invalid port numbers."""
        with pytest.raises(ValidationError) as exc_info:
            CreateProxyRequest(
                url="http://proxy.example.com:70000"  # type: ignore[arg-type]
            )

        errors = exc_info.value.errors()
        assert any("port" in str(error).lower() or "65535" in str(error) for error in errors)

    def test_create_proxy_rejects_zero_port(self):
        """Test CreateProxyRequest rejects port 0."""
        with pytest.raises(ValidationError) as exc_info:
            CreateProxyRequest(
                url="http://proxy.example.com:0"  # type: ignore[arg-type]
            )

        errors = exc_info.value.errors()
        assert any("port" in str(error).lower() for error in errors)

    def test_create_proxy_accepts_port_1(self):
        """Test CreateProxyRequest accepts minimum valid port (1)."""
        request = CreateProxyRequest(url="http://proxy.example.com:1")
        assert ":1" in request.url

    def test_create_proxy_accepts_port_65535(self):
        """Test CreateProxyRequest accepts maximum valid port (65535)."""
        request = CreateProxyRequest(url="http://proxy.example.com:65535")
        assert ":65535" in request.url

    def test_create_proxy_rejects_url_too_long(self):
        """Test CreateProxyRequest rejects URLs longer than 2048 chars."""
        long_host = "a" * 2000 + ".example.com"
        long_url = f"http://{long_host}:8080"
        with pytest.raises(ValidationError) as exc_info:
            CreateProxyRequest(
                url=long_url  # type: ignore[arg-type]
            )

        errors = exc_info.value.errors()
        assert any("2048" in str(error) or "256" in str(error) for error in errors)

    def test_create_proxy_rejects_hostname_too_long(self):
        """Test CreateProxyRequest rejects hostnames longer than 256 chars."""
        long_host = "a" * 260
        with pytest.raises(ValidationError) as exc_info:
            CreateProxyRequest(
                url=f"http://{long_host}:8080"  # type: ignore[arg-type]
            )

        errors = exc_info.value.errors()
        assert any("256" in str(error) for error in errors)

    def test_create_proxy_rejects_username_too_long(self):
        """Test CreateProxyRequest rejects usernames longer than 256 chars."""
        long_username = "a" * 260
        with pytest.raises(ValidationError) as exc_info:
            CreateProxyRequest(
                url="http://proxy.example.com:8080",
                username=long_username,
            )

        errors = exc_info.value.errors()
        assert any("256" in str(error) for error in errors)

    def test_create_proxy_accepts_username_max_length(self):
        """Test CreateProxyRequest accepts username at max length."""
        max_username = "a" * 256
        request = CreateProxyRequest(
            url="http://proxy.example.com:8080",
            username=max_username,
        )
        assert len(request.username) == 256

    def test_create_proxy_with_credentials(self):
        """Test CreateProxyRequest handles username and password."""
        request = CreateProxyRequest(
            url="http://proxy.example.com:8080",
            username="user123",
            password=SecretStr("pass456"),
        )
        assert request.username == "user123"
        assert request.password.get_secret_value() == "pass456"


class TestUpdateConfigRequestValidation:
    """Test UpdateConfigRequest model validation."""

    def test_update_config_accepts_round_robin_strategy(self):
        """Test UpdateConfigRequest accepts 'round-robin' strategy."""
        request = UpdateConfigRequest(rotation_strategy="round-robin")
        assert request.rotation_strategy == "round-robin"

    def test_update_config_accepts_random_strategy(self):
        """Test UpdateConfigRequest accepts 'random' strategy."""
        request = UpdateConfigRequest(rotation_strategy="random")
        assert request.rotation_strategy == "random"

    def test_update_config_accepts_weighted_strategy(self):
        """Test UpdateConfigRequest accepts 'weighted' strategy."""
        request = UpdateConfigRequest(rotation_strategy="weighted")
        assert request.rotation_strategy == "weighted"

    def test_update_config_accepts_least_used_strategy(self):
        """Test UpdateConfigRequest accepts 'least-used' strategy."""
        request = UpdateConfigRequest(rotation_strategy="least-used")
        assert request.rotation_strategy == "least-used"

    def test_update_config_rejects_invalid_strategy(self):
        """Test UpdateConfigRequest rejects invalid rotation strategies."""
        with pytest.raises(ValidationError) as exc_info:
            UpdateConfigRequest(rotation_strategy="invalid-strategy")

        errors = exc_info.value.errors()
        assert any("strategy" in str(error).lower() for error in errors)

    def test_update_config_rejects_strategy_too_long(self):
        """Test UpdateConfigRequest rejects strategy names longer than 64 chars."""
        long_strategy = "a" * 70
        with pytest.raises(ValidationError) as exc_info:
            UpdateConfigRequest(rotation_strategy=long_strategy)

        errors = exc_info.value.errors()
        assert any("64" in str(error) for error in errors)

    def test_update_config_rejects_cors_origin_too_long(self):
        """Test UpdateConfigRequest rejects CORS origins longer than 256 chars."""
        long_origin = "https://" + "a" * 250 + ".example.com"
        with pytest.raises(ValidationError) as exc_info:
            UpdateConfigRequest(cors_origins=[long_origin])

        errors = exc_info.value.errors()
        assert any("256" in str(error) for error in errors)

    def test_update_config_accepts_cors_origin_max_length(self):
        """Test UpdateConfigRequest accepts CORS origin at max length."""
        max_origin = "https://" + "a" * (256 - len("https://"))
        request = UpdateConfigRequest(cors_origins=[max_origin])
        assert len(request.cors_origins[0]) <= 256

    def test_update_config_accepts_multiple_cors_origins(self):
        """Test UpdateConfigRequest accepts multiple CORS origins."""
        origins = ["http://localhost:3000", "https://example.com", "*"]
        request = UpdateConfigRequest(cors_origins=origins)
        assert request.cors_origins == origins

    def test_update_config_partial_update(self):
        """Test UpdateConfigRequest allows partial updates."""
        request = UpdateConfigRequest(timeout=60)
        assert request.timeout == 60
        assert request.rotation_strategy is None
        assert request.max_retries is None
