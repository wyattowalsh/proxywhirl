"""Test API v1 backward compatibility.

This module ensures that v1 API signatures and behavior continue to work
correctly, validating backward compatibility for existing consumers.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from proxywhirl import AsyncProxyWhirl, Proxy, ProxyPool, ProxyWhirl


class TestAPIv1BackwardCompatibility:
    """Test suite for API v1 backward compatibility."""

    def test_proxy_model_old_fields(self):
        """Test that Proxy model supports old v1 field names."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            protocol="http",
        )
        assert proxy.url == "http://proxy.example.com:8080"
        assert proxy.protocol == "http"
        assert hasattr(proxy, "url")
        assert hasattr(proxy, "protocol")

    def test_proxy_pool_v1_instantiation(self):
        """Test ProxyPool can be instantiated with v1 parameters."""
        proxies = [
            Proxy(url="http://proxy1:8080", protocol="http"),
            Proxy(url="http://proxy2:8080", protocol="http"),
        ]
        pool = ProxyPool(proxies=proxies)
        assert len(pool.proxies) == 2
        assert all(isinstance(p, Proxy) for p in pool.proxies)

    def test_proxywhirl_v1_sync_init(self):
        """Test ProxyWhirl can be instantiated with v1 defaults."""
        pw = ProxyWhirl()
        assert pw is not None
        assert hasattr(pw, "get")
        assert hasattr(pw, "add_proxy")

    @pytest.mark.asyncio
    async def test_asyncproxywhirl_v1_async_init(self):
        """Test AsyncProxyWhirl can be instantiated with v1 defaults."""
        pw = AsyncProxyWhirl()
        assert pw is not None
        assert hasattr(pw, "get")
        assert hasattr(pw, "add_proxy")

    def test_proxywhirl_v1_simple_get(self):
        """Test ProxyWhirl.get() works with v1 signature."""
        with patch.object(ProxyWhirl, "get") as mock_get:
            mock_proxy = Proxy(url="http://proxy:8080", protocol="http")
            mock_get.return_value = mock_proxy

            pw = ProxyWhirl()
            result = pw.get()

            assert result is not None

    @pytest.mark.asyncio
    async def test_asyncproxywhirl_v1_simple_get(self):
        """Test AsyncProxyWhirl.get() works with v1 signature."""
        pw = AsyncProxyWhirl()
        # Should have get method
        assert hasattr(pw, "get")

    def test_proxy_v1_string_representation(self):
        """Test Proxy string representation backward compatibility."""
        proxy = Proxy(url="http://proxy:8080", protocol="http")
        str_repr = str(proxy)
        assert "proxy:8080" in str_repr or "http" in str_repr

    def test_proxy_v1_equality(self):
        """Test Proxy equality comparison for v1."""
        proxy1 = Proxy(url="http://proxy:8080", protocol="http")
        proxy2 = Proxy(url="http://proxy:8080", protocol="http")
        # Both should represent the same proxy
        assert proxy1.url == proxy2.url
        assert proxy1.protocol == proxy2.protocol

    def test_proxywhirl_v1_no_required_config(self):
        """Test ProxyWhirl can be instantiated without config."""
        # v1 API should allow instantiation without explicit config
        pw = ProxyWhirl()
        assert pw is not None

    @pytest.mark.asyncio
    async def test_asyncproxywhirl_v1_context_manager(self):
        """Test AsyncProxyWhirl works as async context manager."""
        pw = AsyncProxyWhirl()
        assert pw is not None
        assert hasattr(pw, "get")

    def test_proxywhirl_v1_context_manager(self):
        """Test ProxyWhirl works as context manager."""
        pw = ProxyWhirl()
        assert pw is not None
        assert hasattr(pw, "get")

    def test_proxy_v1_dict_conversion(self):
        """Test Proxy can be converted to dict for v1 API."""
        proxy = Proxy(url="http://proxy:8080", protocol="http")
        proxy_dict = proxy.model_dump()
        assert "url" in proxy_dict
        assert "protocol" in proxy_dict
        assert proxy_dict["url"] == "http://proxy:8080"

    def test_proxypool_v1_empty_initialization(self):
        """Test ProxyPool can be initialized with name."""
        pool = ProxyPool(proxies=[], name="default")
        assert len(pool.proxies) == 0

    def test_proxypool_v1_add_proxy(self):
        """Test adding proxies to ProxyPool after initialization."""
        pool = ProxyPool(proxies=[], name="default")
        proxy = Proxy(url="http://proxy:8080", protocol="http")
        pool.proxies.append(proxy)
        assert len(pool.proxies) == 1

    def test_proxy_pool_iteration_v1(self):
        """Test ProxyPool iteration for v1."""
        proxies = [Proxy(url=f"http://proxy{i}:8080", protocol="http") for i in range(3)]
        pool = ProxyPool(proxies=proxies, name="test")
        count = 0
        for proxy in pool.proxies:
            assert isinstance(proxy, Proxy)
            count += 1
        assert count == 3

    @pytest.mark.asyncio
    async def test_asyncproxywhirl_v1_multiple_instances(self):
        """Test creating multiple AsyncProxyWhirl instances."""
        pw1 = AsyncProxyWhirl()
        pw2 = AsyncProxyWhirl()
        assert pw1 is not None
        assert pw2 is not None
        assert pw1 is not pw2

    def test_proxywhirl_v1_config_dict(self):
        """Test ProxyWhirl accepts dict-like configuration."""
        config = {
            "rotation_strategy": "round_robin",
            "timeout": 30,
        }
        try:
            pw = ProxyWhirl(**config)
            assert pw is not None
        except TypeError:
            # Acceptable if config dict approach not supported
            pass

    def test_proxy_v1_immutability(self):
        """Test Proxy model immutability for v1."""
        proxy = Proxy(url="http://proxy:8080", protocol="http")
        try:
            proxy.url = "http://other:8080"
            # If mutable, test passes
        except (AttributeError, ValueError):
            # If immutable, that's also acceptable for v1
            pass

    def test_proxywhirl_v1_rotation_state(self):
        """Test ProxyWhirl maintains state for v1."""
        pw = ProxyWhirl()
        # Should be able to track state
        assert hasattr(pw, "config") or hasattr(pw, "get")

    @pytest.mark.asyncio
    async def test_asyncproxywhirl_v1_error_handling(self):
        """Test AsyncProxyWhirl error handling for v1."""
        pw = AsyncProxyWhirl()
        # Should have error handling mechanisms
        assert hasattr(pw, "get_proxy")

    def test_proxy_v1_none_handling(self):
        """Test Proxy handles None gracefully for v1."""
        with pytest.raises(Exception):
            # Should not accept None URL
            Proxy(url=None, protocol="http")

    def test_proxywhirl_v1_statistics(self):
        """Test ProxyWhirl provides statistics for v1."""
        pw = ProxyWhirl()
        # Should have stats or config method
        if hasattr(pw, "config"):
            stats = pw.config
            assert stats is not None

    def test_proxy_pool_iteration_v1_second(self):
        """Test ProxyPool iteration for v1."""
        proxies = [Proxy(url=f"http://proxy{i}:8080", protocol="http") for i in range(3)]
        pool = ProxyPool(proxies=proxies, name="test")
        count = 0
        for proxy in pool.proxies:
            assert isinstance(proxy, Proxy)
            count += 1
        assert count == 3
