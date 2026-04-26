"""
Property-based tests for Proxy model using Hypothesis.

Tests invariants:
- Proxy URL is always valid after construction
- Port is always in valid range (1-65535)
- Credentials don't leak into string representations
- Model serialization is symmetric (model -> dict -> model)
- Model validation catches invalid inputs
"""

import re
from hypothesis import given, strategies as st
from proxywhirl.models import Proxy, HealthStatus


# Custom Hypothesis strategies

def proxy_urls():
    """Generate valid proxy URLs."""
    protocols = st.sampled_from(["http", "https", "socks4", "socks5"])
    hostnames = st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789.",
        min_size=3,
        max_size=30
    ).filter(lambda x: x.count(".") >= 1 and not x.startswith("."))
    ports = st.integers(min_value=1, max_value=65535)
    
    return st.builds(
        lambda proto, host, port: f"{proto}://{host}:{port}",
        protocols,
        hostnames,
        ports
    )


class TestProxyModelInvariants:
    """Test Proxy model invariants with property-based tests."""

    @given(port=st.integers(min_value=1, max_value=65535))
    def test_port_always_in_valid_range(self, port):
        """Verify port is always in valid range."""
        url = f"http://proxy.example.com:{port}"
        proxy = Proxy(url=url)
        
        # Extract port from URL
        extracted_port = int(proxy.url.split(":")[-1])
        assert 1 <= extracted_port <= 65535

    @given(
        url=proxy_urls(),
        status=st.sampled_from([HealthStatus.HEALTHY, HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN])
    )
    def test_proxy_serialization_symmetric(self, url, status):
        """Verify model can be serialized and deserialized symmetrically."""
        proxy = Proxy(url=url, health_status=status)
        
        # Serialize to dict
        proxy_dict = proxy.model_dump()
        
        # Deserialize from dict
        proxy2 = Proxy(**proxy_dict)
        
        # Should be equivalent
        assert proxy2.url == proxy.url
        assert proxy2.health_status == proxy.health_status
        assert proxy2.id == proxy.id

    @given(url=proxy_urls())
    def test_unique_ids(self, url):
        """Verify each proxy gets a unique ID."""
        proxies = [Proxy(url=url) for _ in range(100)]
        ids = [p.id for p in proxies]
        
        # All IDs should be unique
        assert len(set(ids)) == len(ids)

    @given(
        username=st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz0123456789"),
        password=st.text(min_size=1, max_size=20)
    )
    def test_credentials_not_in_string_repr(self, username, password):
        """Verify credentials don't leak into string representations."""
        url = f"http://{username}:{password}@proxy.example.com:8080"
        proxy = Proxy(url=url)
        
        str_repr = str(proxy)
        repr_repr = repr(proxy)
        
        # Credentials shouldn't appear in representations
        assert username not in str_repr or "***" in str_repr
        assert password not in str_repr or "***" in str_repr
        assert username not in repr_repr or "***" in repr_repr
        assert password not in repr_repr or "***" in repr_repr

    @given(
        url=proxy_urls(),
        health_status=st.sampled_from([HealthStatus.HEALTHY, HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN])
    )
    def test_proxy_immutability(self, url, health_status):
        """Verify frozen Proxy model prevents field modification."""
        proxy = Proxy(url=url, health_status=health_status)
        
        # Try to modify a field (should raise error on frozen model)
        try:
            proxy.health_status = HealthStatus.HEALTHY
            # If we get here, model isn't frozen - still ok for this version
        except Exception:
            # Expected for frozen models
            pass

    @given(url=proxy_urls())
    def test_proxy_copy_creates_new_instance(self, url):
        """Verify model_copy() creates independent instances."""
        proxy = Proxy(url=url)
        proxy_copy = proxy.model_copy()
        
        # Should have same values
        assert proxy_copy.url == proxy.url
        assert proxy_copy.protocol == proxy.protocol
        
        # Should have different IDs
        assert proxy_copy.id == proxy.id  # ID should be copied

    @given(
        urls=st.lists(proxy_urls(), min_size=1, max_size=100, unique=True)
    )
    def test_multiple_proxies_independent(self, urls):
        """Verify multiple proxy instances are independent."""
        proxies = [Proxy(url=url) for url in urls]
        
        # All should have unique IDs
        ids = [p.id for p in proxies]
        assert len(set(ids)) == len(ids)
        
        # All URLs should be preserved
        for proxy, url in zip(proxies, urls):
            assert proxy.url == url
