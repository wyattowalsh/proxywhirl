"""Unit tests for API models validation (api_models.py).

Tests the Pydantic validation logic for API request/response models.
"""

import pytest
from pydantic import HttpUrl, ValidationError

from proxywhirl.api_models import ProxiedRequest


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
