"""Additional tests for utility functions to increase coverage."""

import sys
from io import StringIO

from loguru import logger

from proxywhirl.models import Proxy
from proxywhirl.utils import (
    configure_logging,
    create_proxy_from_url,
    parse_proxy_url,
    validate_proxy_model,
)


class TestConfigureLogging:
    """Tests for configure_logging function."""

    def test_configure_logging_text_format(self):
        """Test configure_logging with text format."""
        logger.remove()
        configure_logging(level="INFO", format_type="text")

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        logger.info("Test message")

        stdout_content = sys.stdout.getvalue()
        sys.stdout = old_stdout

        assert "Test message" in stdout_content

    def test_configure_logging_json_format(self):
        """Test configure_logging with JSON format."""
        logger.remove()
        configure_logging(level="INFO", format_type="json")

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        logger.info("Test JSON message")

        stdout_content = sys.stdout.getvalue()
        sys.stdout = old_stdout

        # JSON logs should contain structured data
        assert "Test JSON message" in stdout_content
        assert '"message"' in stdout_content

    def test_configure_logging_debug_level(self):
        """Test configure_logging with DEBUG level."""
        logger.remove()
        configure_logging(level="DEBUG", format_type="text")

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        logger.debug("Debug message")

        stdout_content = sys.stdout.getvalue()
        sys.stdout = old_stdout

        assert "Debug message" in stdout_content


class TestParseProxyUrl:
    """Tests for parse_proxy_url function."""

    def test_parse_proxy_url_with_basic_auth(self):
        """Test parsing proxy URL with basic authentication."""
        result = parse_proxy_url("http://user:pass@proxy.example.com:8080")

        assert result["protocol"] == "http"
        assert result["host"] == "proxy.example.com"
        assert result["port"] == 8080
        assert result["username"] == "user"
        assert result["password"] == "pass"

    def test_parse_proxy_url_without_auth(self):
        """Test parsing proxy URL without authentication."""
        result = parse_proxy_url("http://proxy.example.com:8080")

        assert result["protocol"] == "http"
        assert result["host"] == "proxy.example.com"
        assert result["port"] == 8080
        assert result["username"] is None
        assert result["password"] is None

    def test_parse_proxy_url_socks5(self):
        """Test parsing SOCKS5 proxy URL."""
        result = parse_proxy_url("socks5://proxy.example.com:1080")

        assert result["protocol"] == "socks5"
        assert result["host"] == "proxy.example.com"
        assert result["port"] == 1080


class TestValidateProxyModel:
    """Tests for validate_proxy_model function."""

    def test_validate_proxy_model_valid(self):
        """Test validating a valid Proxy object."""
        proxy = Proxy(url="http://proxy.example.com:8080")

        # Should return empty list (no errors)
        errors = validate_proxy_model(proxy)
        assert errors == []

    def test_validate_proxy_model_unhealthy(self):
        """Test validating unhealthy proxy still works."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_failure()
        proxy.record_failure()
        proxy.record_failure()

        # Should return empty list (unhealthy is not an error)
        errors = validate_proxy_model(proxy)
        assert errors == []


class TestCreateProxyFromUrl:
    """Tests for create_proxy_from_url function."""

    def test_create_proxy_from_url_basic(self):
        """Test creating proxy from basic URL."""
        proxy = create_proxy_from_url("http://proxy.example.com:8080")

        assert proxy.url == "http://proxy.example.com:8080"
        assert proxy.protocol == "http"
        assert proxy.credentials is None

    def test_create_proxy_from_url_socks5(self):
        """Test creating proxy from SOCKS5 URL."""
        proxy = create_proxy_from_url("socks5://proxy.example.com:1080")

        assert proxy.url == "socks5://proxy.example.com:1080"
        assert proxy.protocol == "socks5"
