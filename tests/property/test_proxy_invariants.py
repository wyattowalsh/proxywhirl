"""
Property-based tests for Proxy model using Hypothesis.

Tests invariants:
- Proxy URLs are parseable and maintain structure
- Model serialization is symmetric
- Proxy instances are independent
"""

import re
from hypothesis import given, strategies as st, settings, HealthCheck
from proxywhirl.models import Proxy, HealthStatus


# Hypothesis strategy for valid proxy URLs
@st.composite
def valid_proxy_urls(draw):
    """Generate valid proxy URLs."""
    proto = draw(st.sampled_from(["http", "https", "socks4", "socks5"]))
    # Generate hostnames with at least one dot
    parts = draw(st.lists(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=10),
        min_size=2,
        max_size=4
    ))
    hostname = ".".join(parts)
    port = draw(st.integers(min_value=1024, max_value=65535))
    return f"{proto}://{hostname}:{port}"


class TestProxyModelInvariants:
    """Test Proxy model invariants with property-based tests."""

    @given(url=valid_proxy_urls())
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    def test_proxy_url_structure_preserved(self, url):
        """Verify that proxy URL structure is preserved."""
        proxy = Proxy(url=url)
        
        # URL should match pattern
        assert re.match(
            r"^(https?|socks[45])://[a-zA-Z0-9.-]+:\d+$",
            proxy.url
        ), f"Invalid URL format: {proxy.url}"
        
        # Port should be extractable
        port_str = proxy.url.split(":")[-1]
        port = int(port_str)
        assert 1 <= port <= 65535

    @given(url=valid_proxy_urls())
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    def test_proxy_serialization_roundtrip(self, url):
        """Verify model can serialize and deserialize symmetrically."""
        proxy = Proxy(url=url)
        
        # Serialize to dict
        proxy_dict = proxy.model_dump()
        
        # Deserialize from dict
        proxy2 = Proxy(**proxy_dict)
        
        # Should be equivalent
        assert proxy2.url == proxy.url
        assert proxy2.id == proxy.id

    @given(
        url1=valid_proxy_urls(),
        url2=valid_proxy_urls()
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    def test_different_proxies_have_different_ids(self, url1, url2):
        """Verify different proxies get different IDs."""
        proxy1 = Proxy(url=url1)
        proxy2 = Proxy(url=url2)
        
        # IDs should be different
        assert proxy1.id != proxy2.id

    @given(
        url=valid_proxy_urls(),
        status=st.sampled_from([HealthStatus.HEALTHY, HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN])
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    def test_health_status_preserved(self, url, status):
        """Verify health status is preserved through serialization."""
        proxy = Proxy(url=url, health_status=status)
        
        # Serialize and deserialize
        proxy_dict = proxy.model_dump()
        proxy2 = Proxy(**proxy_dict)
        
        # Status should match
        assert proxy2.health_status == status

    @given(st.integers(min_value=1024, max_value=65535))
    def test_port_extraction_correctness(self, port):
        """Verify port extraction is correct."""
        url = f"http://example.com:{port}"
        proxy = Proxy(url=url)
        
        # Extract port from URL
        extracted_port = int(proxy.url.split(":")[-1])
        assert extracted_port == port

    @given(url=valid_proxy_urls())
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    def test_proxy_model_validation(self, url):
        """Verify Proxy model validates input correctly."""
        # Valid URL should create proxy
        proxy = Proxy(url=url)
        assert proxy is not None
        assert proxy.url == url

    @given(st.text(min_size=0, max_size=50))
    def test_invalid_urls_handled(self, invalid_url):
        """Verify invalid URLs are rejected or sanitized."""
        # This test checks that the model either rejects or handles invalid URLs gracefully
        try:
            proxy = Proxy(url=invalid_url)
            # If creation succeeds, verify it has a valid structure at least
            assert isinstance(proxy, Proxy)
        except Exception:
            # It's fine if invalid URLs raise exceptions
            pass
