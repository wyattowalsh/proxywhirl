"""Tests for custom headers module."""

from proxywhirl.custom_headers import CustomHeadersManager, ProxyHeaders


class TestProxyHeaders:
    """Test proxy headers."""

    def test_to_dict(self):
        """Test converting to dictionary."""
        headers = ProxyHeaders(
            headers={"X-Custom": "value"},
            auth_headers={"Authorization": "Bearer token"},
            user_agent="CustomUA/1.0",
        )

        result = headers.to_dict()
        assert result["X-Custom"] == "value"
        assert result["Authorization"] == "Bearer token"
        assert result["User-Agent"] == "CustomUA/1.0"

    def test_merge(self):
        """Test merging headers."""
        h1 = ProxyHeaders(headers={"X-A": "1"}, user_agent="UA1")
        h2 = ProxyHeaders(headers={"X-B": "2"}, user_agent="UA2")

        merged = h1.merge(h2)
        assert merged.headers == {"X-A": "1", "X-B": "2"}
        assert merged.user_agent == "UA2"

    def test_empty_headers(self):
        """Test empty headers."""
        headers = ProxyHeaders()
        result = headers.to_dict()

        assert result == {}


class TestCustomHeadersManager:
    """Test custom headers manager."""

    def test_set_default_headers(self):
        """Test setting default headers."""
        manager = CustomHeadersManager()
        headers = ProxyHeaders(headers={"X-Default": "value"})

        manager.set_default_headers(headers)
        result = manager.get_headers()

        assert result["X-Default"] == "value"

    def test_set_pool_headers(self):
        """Test setting pool-specific headers."""
        manager = CustomHeadersManager()
        pool_headers = ProxyHeaders(headers={"X-Pool": "value"})

        manager.set_pool_headers("pool1", pool_headers)
        result = manager.get_headers(pool_id="pool1")

        assert result["X-Pool"] == "value"

    def test_set_proxy_headers(self):
        """Test setting proxy-specific headers."""
        manager = CustomHeadersManager()
        proxy_headers = ProxyHeaders(headers={"X-Proxy": "value"})

        manager.set_proxy_headers("http://proxy.com:8080", proxy_headers)
        result = manager.get_headers(proxy_url="http://proxy.com:8080")

        assert result["X-Proxy"] == "value"

    def test_header_precedence(self):
        """Test header precedence: proxy > pool > default."""
        manager = CustomHeadersManager()

        default = ProxyHeaders(headers={"X-Level": "default"})
        pool = ProxyHeaders(headers={"X-Level": "pool"})
        proxy = ProxyHeaders(headers={"X-Level": "proxy"})

        manager.set_default_headers(default)
        manager.set_pool_headers("pool1", pool)
        manager.set_proxy_headers("http://proxy.com:8080", proxy)

        result = manager.get_headers(pool_id="pool1", proxy_url="http://proxy.com:8080")
        assert result["X-Level"] == "proxy"

        result = manager.get_headers(pool_id="pool1")
        assert result["X-Level"] == "pool"

        result = manager.get_headers()
        assert result["X-Level"] == "default"

    def test_remove_pool_headers(self):
        """Test removing pool headers."""
        manager = CustomHeadersManager()
        headers = ProxyHeaders(headers={"X-Pool": "value"})

        manager.set_pool_headers("pool1", headers)
        assert manager.remove_pool_headers("pool1") is True
        assert manager.remove_pool_headers("pool1") is False

    def test_remove_proxy_headers(self):
        """Test removing proxy headers."""
        manager = CustomHeadersManager()
        headers = ProxyHeaders(headers={"X-Proxy": "value"})

        manager.set_proxy_headers("http://proxy.com:8080", headers)
        assert manager.remove_proxy_headers("http://proxy.com:8080") is True
        assert manager.remove_proxy_headers("http://proxy.com:8080") is False
