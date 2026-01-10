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

    @pytest.mark.parametrize(
        "url,expected",
        [
            # Valid URLs
            ("http://proxy.example.com:8080", True),
            ("https://proxy.example.com:8080", True),
            ("socks4://proxy.example.com:1080", True),
            ("socks5://proxy.example.com:1080", True),
            ("http://user:pass@proxy.example.com:8080", True),
            # Invalid URLs
            ("http://proxy.example.com", False),  # no port
            ("ftp://proxy.example.com:8080", False),  # wrong scheme
            ("not-a-url", False),  # malformed
            ("", False),  # empty
        ],
        ids=[
            "http_valid",
            "https_valid",
            "socks4_valid",
            "socks5_valid",
            "with_auth_valid",
            "no_port_invalid",
            "wrong_scheme_invalid",
            "malformed_invalid",
            "empty_invalid",
        ],
    )
    def test_is_valid_proxy_url(self, url, expected):
        """Test URL validation with various inputs."""
        assert is_valid_proxy_url(url) is expected


class TestURLParsing:
    """Test URL parsing functions."""

    @pytest.mark.parametrize(
        "url,expected",
        [
            (
                "http://proxy.example.com:8080",
                {
                    "protocol": "http",
                    "host": "proxy.example.com",
                    "port": 8080,
                    "username": None,
                    "password": None,
                },
            ),
            (
                "http://user:pass@proxy.example.com:8080",
                {
                    "protocol": "http",
                    "host": "proxy.example.com",
                    "port": 8080,
                    "username": "user",
                    "password": "pass",
                },
            ),
            (
                "socks5://proxy.example.com:1080",
                {
                    "protocol": "socks5",
                    "host": "proxy.example.com",
                    "port": 1080,
                    "username": None,
                    "password": None,
                },
            ),
            (
                "https://secure.proxy.com:443",
                {
                    "protocol": "https",
                    "host": "secure.proxy.com",
                    "port": 443,
                    "username": None,
                    "password": None,
                },
            ),
        ],
        ids=["simple_http", "with_credentials", "socks5", "https"],
    )
    def test_parse_proxy_url_valid(self, url, expected):
        """Test parsing valid proxy URLs."""
        result = parse_proxy_url(url)
        assert result["protocol"] == expected["protocol"]
        assert result["host"] == expected["host"]
        assert result["port"] == expected["port"]
        assert result["username"] == expected["username"]
        assert result["password"] == expected["password"]

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
        proxy = Proxy(url="http://proxy.example.com:8080", tags={"fast", "us"})  # type: ignore
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
        proxy = create_proxy_from_url("http://proxy.example.com:8080", source=ProxySource.FETCHED)

        assert proxy.source == ProxySource.FETCHED

    def test_create_proxy_from_url_with_tags(self):
        """Test creating proxy with tags."""
        proxy = create_proxy_from_url("http://proxy.example.com:8080", tags={"fast", "us"})

        assert proxy.tags == {"fast", "us"}

    def test_create_proxy_from_invalid_url_raises(self):
        """Test that creating proxy from invalid URL raises ValueError.

        With TASK-301 URL validation, invalid URLs are now rejected at creation time.
        """
        import pytest

        with pytest.raises(ValueError, match="Invalid proxy URL"):
            create_proxy_from_url("not-a-valid-url")


class TestProxyCredentialsModel:
    """Test ProxyCredentials model methods."""

    def test_to_httpx_auth(self):
        """Test conversion to httpx BasicAuth object."""
        import httpx
        from pydantic import SecretStr

        from proxywhirl.models import ProxyCredentials

        creds = ProxyCredentials(username=SecretStr("testuser"), password=SecretStr("testpass"))

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

        creds = ProxyCredentials(username=SecretStr("testuser"), password=SecretStr("testpass"))

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

        config = ProxyConfiguration(timeout=60, max_retries=5, verify_ssl=False, log_level="DEBUG")
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


class TestLoggingUtilities:
    """Test logging configuration and redaction utilities."""

    def test_configure_logging_text_format(self):
        """Test configuring text-format logging."""
        from proxywhirl.utils import configure_logging

        # Should not raise
        configure_logging(level="INFO", format_type="text", redact_credentials=True)

    def test_configure_logging_json_format(self):
        """Test configuring JSON-format logging."""
        from proxywhirl.utils import configure_logging

        # Should not raise
        configure_logging(level="DEBUG", format_type="json", redact_credentials=False)

    def test_redact_sensitive_data_passwords(self):
        """Test that passwords and usernames are redacted from log data."""
        from proxywhirl.utils import _redact_sensitive_data

        data = {"username": "user", "password": "secret123", "url": "http://example.com"}
        redacted = _redact_sensitive_data(data)

        # Both username and password are in the sensitive key list
        assert redacted["username"] == "***"
        assert redacted["password"] == "***"
        assert redacted["url"] == "http://example.com"

    def test_redact_sensitive_data_api_keys(self):
        """Test that API keys are redacted."""
        from proxywhirl.utils import _redact_sensitive_data

        data = {"api_key": "key123", "secret_token": "token456", "public_data": "visible"}
        redacted = _redact_sensitive_data(data)

        # Sensitive keys are redacted with "***"
        assert redacted["api_key"] == "***"
        assert redacted["secret_token"] == "***"
        assert redacted["public_data"] == "visible"

    def test_redact_sensitive_data_nested(self):
        """Test redaction works recursively in nested structures."""
        from proxywhirl.utils import _redact_sensitive_data

        data = {
            "level1": {"password": "secret", "safe": "value"},
            "level2": ["normal", {"credential": "hidden"}],
        }
        redacted = _redact_sensitive_data(data)

        # Sensitive keys are redacted with "***" at all nesting levels
        assert redacted["level1"]["password"] == "***"
        assert redacted["level1"]["safe"] == "value"
        assert redacted["level2"][1]["credential"] == "***"

    def test_redact_url_credentials_with_auth(self):
        """Test that URL credentials are redacted."""
        from proxywhirl.utils import _redact_url_credentials

        url = "http://user:password@proxy.example.com:8080/path"
        redacted = _redact_url_credentials(url)

        assert "user" not in redacted
        assert "password" not in redacted
        # Credentials are replaced with ***:***
        assert "***:***@" in redacted
        assert "proxy.example.com" in redacted

    def test_redact_url_credentials_without_auth(self):
        """Test that URLs without credentials pass through unchanged."""
        from proxywhirl.utils import _redact_url_credentials

        url = "http://proxy.example.com:8080/path"
        redacted = _redact_url_credentials(url)

        assert redacted == url


class TestEncryptionUtilities:
    """Test encryption utility functions (optional cryptography dependency)."""

    def test_generate_encryption_key(self):
        """Test generating Fernet encryption key."""
        try:
            from proxywhirl.utils import generate_encryption_key

            key = generate_encryption_key()
            assert isinstance(key, str)
            assert len(key) > 20  # Fernet keys are base64-encoded, should be fairly long
        except ImportError:
            pytest.skip("cryptography package not installed")

    def test_encrypt_credentials_basic(self):
        """Test encrypting credentials."""
        try:
            from proxywhirl.utils import encrypt_credentials, generate_encryption_key

            key = generate_encryption_key()
            plaintext = "my-secret-password"

            encrypted = encrypt_credentials(plaintext, key)
            assert encrypted != plaintext
            assert isinstance(encrypted, str)
        except ImportError:
            pytest.skip("cryptography package not installed")

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encrypt/decrypt roundtrip preserves data."""
        try:
            from proxywhirl.utils import (
                decrypt_credentials,
                encrypt_credentials,
                generate_encryption_key,
            )

            key = generate_encryption_key()
            plaintext = "test-password-123"

            encrypted = encrypt_credentials(plaintext, key)
            decrypted = decrypt_credentials(encrypted, key)

            assert decrypted == plaintext
        except ImportError:
            pytest.skip("cryptography package not installed")

    def test_decrypt_with_wrong_key_fails(self):
        """Test that decryption with wrong key raises error."""
        try:
            from cryptography.fernet import InvalidToken

            from proxywhirl.utils import (
                decrypt_credentials,
                encrypt_credentials,
                generate_encryption_key,
            )

            key1 = generate_encryption_key()
            key2 = generate_encryption_key()

            encrypted = encrypt_credentials("secret", key1)

            with pytest.raises(InvalidToken):
                decrypt_credentials(encrypted, key2)
        except ImportError:
            pytest.skip("cryptography package not installed")

    def test_encrypt_without_explicit_key(self):
        """Test that encryption can generate key if none provided."""
        try:
            from proxywhirl.utils import encrypt_credentials

            # Should not raise even without explicit key
            encrypted = encrypt_credentials("test-data")
            assert isinstance(encrypted, str)
        except ImportError:
            pytest.skip("cryptography package not installed")


class TestAtomicWrite:
    """Test atomic file write operations."""

    def test_atomic_write_creates_file(self, tmp_path):
        """Test that atomic_write creates a new file."""
        from proxywhirl.utils import atomic_write

        file_path = tmp_path / "test.txt"
        content = "Hello, World!"

        atomic_write(file_path, content)

        assert file_path.exists()
        assert file_path.read_text() == content

    def test_atomic_write_overwrites_existing_file(self, tmp_path):
        """Test that atomic_write correctly overwrites existing files."""
        from proxywhirl.utils import atomic_write

        file_path = tmp_path / "test.txt"
        file_path.write_text("Original content")

        new_content = "New content"
        atomic_write(file_path, new_content)

        assert file_path.read_text() == new_content

    def test_atomic_write_no_temp_files_left(self, tmp_path):
        """Test that no temporary files are left after atomic_write."""
        from proxywhirl.utils import atomic_write

        file_path = tmp_path / "test.txt"
        atomic_write(file_path, "Test content")

        # Check that no .tmp.* files remain in the directory
        temp_files = list(tmp_path.glob("*.tmp.*"))
        assert len(temp_files) == 0

    def test_atomic_write_fsync_called(self, tmp_path):
        """Test that fsync is called to ensure data is on disk."""
        from unittest.mock import patch

        from proxywhirl.utils import atomic_write

        file_path = tmp_path / "test.txt"

        with patch("os.fsync") as mock_fsync:
            atomic_write(file_path, "Test content")
            # fsync should be called once
            assert mock_fsync.call_count == 1

    def test_atomic_write_cleans_up_on_error(self, tmp_path):
        """Test that temporary file is cleaned up on error."""
        from unittest.mock import patch

        from proxywhirl.utils import atomic_write

        file_path = tmp_path / "test.txt"

        # Mock os.fsync to raise an error
        with patch("os.fsync", side_effect=OSError("Disk full")), pytest.raises(OSError):
            atomic_write(file_path, "Test content")

        # No temp files should remain
        temp_files = list(tmp_path.glob("*.tmp.*"))
        assert len(temp_files) == 0

    def test_atomic_write_preserves_original_on_error(self, tmp_path):
        """Test that original file is preserved on write error."""
        from unittest.mock import patch

        from proxywhirl.utils import atomic_write

        file_path = tmp_path / "test.txt"
        original_content = "Original content"
        file_path.write_text(original_content)

        # Mock os.fsync to raise an error
        with patch("os.fsync", side_effect=OSError("Disk full")), pytest.raises(OSError):
            atomic_write(file_path, "New content")

        # Original file should remain unchanged
        assert file_path.read_text() == original_content

    def test_atomic_write_custom_encoding(self, tmp_path):
        """Test atomic_write with custom encoding."""
        from proxywhirl.utils import atomic_write

        file_path = tmp_path / "test.txt"
        content = "Test with ümläuts and émojis 🚀"

        atomic_write(file_path, content, encoding="utf-8")

        assert file_path.read_text(encoding="utf-8") == content

    def test_atomic_write_large_content(self, tmp_path):
        """Test atomic_write with large content."""
        from proxywhirl.utils import atomic_write

        file_path = tmp_path / "large.txt"
        # Create a large string (1MB)
        content = "x" * (1024 * 1024)

        atomic_write(file_path, content)

        assert file_path.read_text() == content
        assert len(file_path.read_text()) == 1024 * 1024

    def test_atomic_write_json_helper(self, tmp_path):
        """Test atomic_write_json helper function."""
        import json

        from proxywhirl.utils import atomic_write_json

        file_path = tmp_path / "test.json"
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        atomic_write_json(file_path, data)

        assert file_path.exists()
        loaded_data = json.loads(file_path.read_text())
        assert loaded_data == data

    def test_atomic_write_json_with_formatting(self, tmp_path):
        """Test atomic_write_json with custom JSON formatting."""
        import json

        from proxywhirl.utils import atomic_write_json

        file_path = tmp_path / "formatted.json"
        data = {"key": "value", "nested": {"a": 1, "b": 2}}

        atomic_write_json(file_path, data, indent=2)

        content = file_path.read_text()
        assert "  " in content  # Should have indentation
        loaded_data = json.loads(content)
        assert loaded_data == data
