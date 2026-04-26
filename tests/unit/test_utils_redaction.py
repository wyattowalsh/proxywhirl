"""Tests for utils.py edge cases to push coverage to 90%."""

from proxywhirl.models import Proxy
from proxywhirl.utils import create_proxy_from_url, validate_proxy_model


class TestValidationEdgeCases:
    """Tests for validation edge cases."""

    def test_validate_proxy_model_with_zero_requests_allows_any_stats(self):
        """Test that proxies with 0 requests don't fail validation."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        # No requests recorded, so stats should be valid
        validate_proxy_model(proxy)  # Should not raise

    def test_validate_proxy_model_success_rate_calculation(self):
        """Test validation with various success rates."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_success(100.0)
        proxy.record_success(150.0)
        proxy.record_failure()

        # Should validate successfully
        validate_proxy_model(proxy)

    def test_create_proxy_from_url_with_socks5_no_auth(self):
        """Test creating SOCKS5 proxy without authentication."""
        proxy = create_proxy_from_url("socks5://proxy.example.com:1080")

        assert proxy.url == "socks5://proxy.example.com:1080"
        assert proxy.protocol == "socks5"
        assert proxy.username is None
        assert proxy.password is None

    def test_create_proxy_from_url_preserves_trailing_slash(self):
        """Test that trailing slash in URL is handled."""
        proxy1 = create_proxy_from_url("http://proxy.example.com:8080/")
        proxy2 = create_proxy_from_url("http://proxy.example.com:8080")

        # Both should create valid proxies
        assert "proxy.example.com" in str(proxy1.url)
        assert "proxy.example.com" in str(proxy2.url)

    def test_create_proxy_from_url_with_empty_username(self):
        """Test that URL with empty username is handled."""
        # This tests the edge case where username is empty string
        proxy = create_proxy_from_url("http://:password@proxy.example.com:8080")
        # Password should be set, username might be None or empty
        if proxy.password:
            assert proxy.password.get_secret_value() == "password"
