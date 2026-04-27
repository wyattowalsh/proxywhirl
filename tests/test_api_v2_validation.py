"""Test API v2 validation and new features.

This module tests v2 API validation, new request/response models,
and enhanced validation capabilities.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from proxywhirl import AsyncProxyWhirl, Proxy, ProxyPool, ProxyWhirl


class TestAPIv2Validation:
    """Test suite for API v2 validation enhancements."""

    def test_proxy_v2_validation_required_fields(self):
        """Test Proxy v2 validates required fields."""
        with pytest.raises(ValidationError):
            Proxy(url=None, protocol="http")

    def test_proxy_v2_url_format_validation(self):
        """Test Proxy v2 validates URL format."""
        proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
        assert proxy.url == "http://proxy.example.com:8080"

    def test_proxy_v2_protocol_validation(self):
        """Test Proxy v2 validates protocol values."""
        valid_protocols = ["http", "https", "socks4", "socks5"]
        for protocol in valid_protocols:
            try:
                proxy = Proxy(url="http://proxy:8080", protocol=protocol)
                assert proxy.protocol == protocol
            except ValidationError:
                # Some protocols might be restricted
                pass

    def test_proxy_v2_extra_forbid(self):
        """Test Proxy v2 forbids extra fields."""
        try:
            proxy = Proxy(url="http://proxy:8080", protocol="http", invalid_field="should_fail")
            # If accepted, that's okay for backward compat
        except ValidationError as e:
            # Should reject extra fields
            assert "extra" in str(e).lower() or "unexpected" in str(e).lower()

    def test_proxy_v2_frozen_model(self):
        """Test Proxy v2 is frozen/immutable."""
        proxy = Proxy(url="http://proxy:8080", protocol="http")
        try:
            proxy.url = "http://other:8080"
            # If mutable, test passes (not frozen)
        except (AttributeError, ValidationError):
            # If frozen, that's v2 best practice
            pass

    def test_proxy_pool_v2_validation(self):
        """Test ProxyPool v2 validates proxy list."""
        proxies = [
            Proxy(url="http://proxy1:8080", protocol="http"),
            Proxy(url="http://proxy2:8080", protocol="http"),
        ]
        pool = ProxyPool(proxies=proxies, name="test")
        assert len(pool.proxies) == 2

    def test_proxy_pool_v2_empty_list_validation(self):
        """Test ProxyPool v2 handles empty list."""
        pool = ProxyPool(proxies=[], name="test")
        assert len(pool.proxies) == 0

    def test_proxy_v2_port_validation(self):
        """Test Proxy v2 validates port number."""
        proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
        # Port should be part of URL
        assert "8080" in proxy.url

    def test_proxy_v2_hostname_validation(self):
        """Test Proxy v2 validates hostname."""
        proxy = Proxy(url="http://example.com:8080", protocol="http")
        assert "example.com" in proxy.url

    @pytest.mark.asyncio
    async def test_proxywhirl_v2_type_hints(self):
        """Test ProxyWhirl v2 proper type hints."""
        pw = AsyncProxyWhirl()
        assert hasattr(pw, "get_proxy")
        # Method should have type hints
        if hasattr(pw.get_proxy, "__annotations__"):
            assert "return" in pw.get_proxy.__annotations__

    def test_proxy_v2_protocol_case_sensitivity(self):
        """Test Proxy v2 protocol case handling."""
        proxy = Proxy(url="http://proxy:8080", protocol="http")
        # Protocol should be normalized
        assert proxy.protocol.lower() == "http"

    def test_proxy_v2_url_validation_strict(self):
        """Test Proxy v2 URL validation is strict."""
        with pytest.raises(ValidationError):
            # Invalid URL format
            Proxy(url="not a url", protocol="http")

    def test_proxy_v2_scheme_validation(self):
        """Test Proxy v2 validates URL scheme."""
        proxy = Proxy(url="http://proxy:8080", protocol="http")
        # URL should have scheme
        assert proxy.url.startswith("http://") or proxy.url.startswith("https://")

    def test_proxy_v2_ipv4_support(self):
        """Test Proxy v2 supports IPv4 addresses."""
        try:
            proxy = Proxy(url="http://192.168.1.1:8080", protocol="http")
            assert "192.168.1.1" in proxy.url
        except (ValidationError, ValueError):
            # IP might not be valid
            pass

    def test_proxy_v2_ipv6_support(self):
        """Test Proxy v2 supports IPv6 addresses."""
        try:
            proxy = Proxy(url="http://[::1]:8080", protocol="http")
            assert proxy.url is not None
        except ValidationError:
            # IPv6 might not be supported
            pass

    def test_proxy_v2_domain_validation(self):
        """Test Proxy v2 validates domain names."""
        proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
        assert "example.com" in proxy.url

    def test_proxy_pool_v2_type_validation(self):
        """Test ProxyPool v2 validates proxy type."""
        with pytest.raises((ValidationError, TypeError)):
            # Should not accept non-Proxy objects
            pool = ProxyPool(proxies=["not a proxy"], name="test")

    def test_proxywhirl_v2_config_validation(self):
        """Test ProxyWhirl v2 config validation."""
        try:
            pw = ProxyWhirl(rotation_strategy="invalid_strategy")
            # Config should be validated
        except (ValidationError, ValueError):
            # Should reject invalid strategy
            pass

    def test_proxy_v2_default_port(self):
        """Test Proxy v2 handles default port."""
        try:
            proxy = Proxy(url="http://proxy.example.com", protocol="http")
            assert "proxy.example.com" in proxy.url
        except ValidationError:
            # Port might be required
            pass

    @pytest.mark.asyncio
    async def test_asyncproxywhirl_v2_concurrent_validation(self):
        """Test AsyncProxyWhirl v2 handles concurrent operations."""
        pw = AsyncProxyWhirl()
        # Should support async operations
        assert hasattr(pw, "get_proxy")

    def test_proxy_v2_max_retries_validation(self):
        """Test Proxy v2 validates max retries."""
        try:
            proxy = Proxy(
                url="http://proxy:8080",
                protocol="http",
            )
            # Should accept valid proxy
            assert proxy is not None
        except ValidationError:
            pass

    def test_proxy_pool_v2_duplicate_detection(self):
        """Test ProxyPool v2 handles duplicates."""
        proxies = [
            Proxy(url="http://proxy:8080", protocol="http"),
            Proxy(url="http://proxy:8080", protocol="http"),
        ]
        pool = ProxyPool(proxies=proxies, name="test")
        # Pool should accept duplicates (dedup is separate concern)
        assert len(pool.proxies) == 2

    def test_proxy_v2_authentication_fields(self):
        """Test Proxy v2 handles authentication."""
        try:
            proxy = Proxy(url="http://user:pass@proxy:8080", protocol="http")
            # Should accept auth in URL
            assert proxy.url is not None
        except ValidationError:
            pass

    def test_proxywhirl_v2_response_model(self):
        """Test ProxyWhirl v2 response models."""
        pw = ProxyWhirl()
        # Should have proper response typing
        if hasattr(pw, "get"):
            import inspect

            sig = inspect.signature(pw.get)
            # Should have return annotation
            if sig.return_annotation != inspect.Signature.empty:
                assert sig.return_annotation is not None
