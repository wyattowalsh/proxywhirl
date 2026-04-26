"""Tests for character encoding edge cases in proxy handling."""

from __future__ import annotations

import pytest

from proxywhirl.models import Proxy


class TestEncodingEdgeCases:
    """Test character encoding edge cases."""

    def test_ascii_proxy_url(self) -> None:
        """Test ASCII-only proxy URL."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.url == "http://proxy.example.com:8080"

    def test_ipv4_proxy_url(self) -> None:
        """Test IPv4 proxy URL with numbers."""
        proxy = Proxy(url="http://192.168.1.1:3128", allow_local=True)
        assert proxy.url == "http://192.168.1.1:3128"

    def test_proxy_url_with_port_numbers(self) -> None:
        """Test proxy URL with standard and non-standard ports."""
        proxy1 = Proxy(url="http://proxy.example.com:80")
        proxy2 = Proxy(url="http://proxy.example.com:8080")
        proxy3 = Proxy(url="http://proxy.example.com:9999")

        assert proxy1.url == "http://proxy.example.com:80"
        assert proxy2.url == "http://proxy.example.com:8080"
        assert proxy3.url == "http://proxy.example.com:9999"

    def test_proxy_url_with_credentials(self) -> None:
        """Test proxy URL with username and password."""
        proxy = Proxy(
            url="http://user:pass@proxy.example.com:8080",
            credentials={"username": "user", "password": "pass"},
        )
        assert "user" in proxy.url

    def test_socks_proxy_url_encoding(self) -> None:
        """Test SOCKS proxy URL encoding."""
        proxy = Proxy(url="socks5://proxy.example.com:1080")
        assert proxy.url == "socks5://proxy.example.com:1080"

    def test_https_proxy_url(self) -> None:
        """Test HTTPS proxy URL."""
        proxy = Proxy(url="https://proxy.example.com:443")
        assert proxy.url == "https://proxy.example.com:443"

    def test_long_domain_name(self) -> None:
        """Test very long domain name."""
        long_domain = "very-long-proxy-server-name-with-many-parts.subdomain.example.com"
        proxy = Proxy(url=f"http://{long_domain}:8080")
        assert long_domain in proxy.url

    def test_domain_with_hyphens(self) -> None:
        """Test domain with hyphens."""
        proxy = Proxy(url="http://my-proxy-server.example-domain.com:8080")
        assert proxy.url == "http://my-proxy-server.example-domain.com:8080"

    def test_numeric_domain(self) -> None:
        """Test domain starting with numbers."""
        proxy = Proxy(url="http://1proxy.example.com:8080")
        assert proxy.url == "http://1proxy.example.com:8080"

    def test_proxy_model_string_representation(self) -> None:
        """Test proxy model can be converted to string."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        str_repr = str(proxy)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    def test_proxy_url_normalization(self) -> None:
        """Test proxy URL is properly normalized."""
        # URL should be normalized
        proxy = Proxy(url="http://example.com:8080")
        assert proxy.url.startswith("http://")

    def test_proxy_with_special_port_number(self) -> None:
        """Test proxy with edge case port numbers."""
        # Port 0 is technically valid but unusual
        # Port 65535 is the max
        proxy_max = Proxy(url="http://proxy.example.com:65535")
        assert proxy_max.url == "http://proxy.example.com:65535"

    def test_multiple_proxies_encoding_consistency(self) -> None:
        """Test multiple proxies maintain encoding consistency."""
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),
            Proxy(url="http://proxy2.example.com:8080"),
            Proxy(url="http://proxy3.example.com:8080"),
        ]

        urls = [p.url for p in proxies]
        assert all(isinstance(url, str) for url in urls)
        assert len(urls) == 3
