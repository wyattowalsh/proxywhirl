"""
Regression test suite for ProxyWhirl.

Tests fixed bugs and edge cases to prevent regressions.
"""

from __future__ import annotations

import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import Proxy, ProxyPool
from proxywhirl.validators import is_valid_proxy_url


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_pool_selection(self):
        """Regression: selecting from empty pool should raise error."""
        pool = ProxyPool()
        with pytest.raises(ProxyPoolEmptyError):
            pool.select()

    def test_invalid_proxy_url_format(self):
        """Regression: invalid proxy URL should fail validation."""
        invalid_urls = [
            "not_a_url",
            "http://",
            "http://host",  # missing port
            "://host:8080",  # missing scheme
            "ftp://host:8080",  # unsupported scheme
        ]
        for url in invalid_urls:
            assert not is_valid_proxy_url(url), f"URL {url} should be invalid"

    def test_proxy_with_none_health_status(self):
        """Regression: None health status should be rejected at the model boundary."""
        with pytest.raises(ValueError):
            Proxy.model_validate({"url": "http://proxy1:8080", "health_status": None})


class TestValidation:
    """Tests for validation logic."""

    def test_proxy_url_with_credentials(self):
        """Regression: proxy URL with credentials should validate."""
        url = "http://user:pass@proxy:8080"
        assert is_valid_proxy_url(url)

    def test_socks_proxy_urls(self):
        """Regression: SOCKS proxy URLs should validate."""
        valid_socks = [
            "socks4://proxy:1080",
            "socks5://proxy:1080",
            "socks5h://proxy:1080",
        ]
        for url in valid_socks:
            assert is_valid_proxy_url(url), f"URL {url} should be valid"

    def test_port_boundary_values(self):
        """Regression: port validation at boundaries."""
        from proxywhirl.validators import is_valid_port

        assert is_valid_port(1)
        assert is_valid_port(65535)
        assert not is_valid_port(0)
        assert not is_valid_port(65536)
        assert not is_valid_port(-1)


class TestConcurrency:
    """Tests for concurrent access patterns."""

    @pytest.mark.asyncio
    async def test_concurrent_pool_access(self):
        """Regression: concurrent pool access should be safe."""
        import asyncio

        pool = ProxyPool()
        for i in range(5):
            proxy = Proxy(url=f"http://proxy{i}:8080")
            pool.add_proxy(proxy)

        async def select_proxy():
            return pool.select()

        tasks = [select_proxy() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # All should succeed (no crashes)
        assert len(results) == 10


class TestDataIntegrity:
    """Tests for data integrity and persistence."""

    def test_pool_size_tracking(self):
        """Regression: pool size should accurately reflect proxies."""
        pool = ProxyPool()
        for i in range(10):
            proxy = Proxy(url=f"http://proxy{i}:8080")
            pool.add_proxy(proxy)

        assert pool.size == 10
