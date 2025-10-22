"""Integration tests for runtime proxy pool updates."""

import httpx
import pytest
import respx

from proxywhirl import Proxy, ProxyRotator
from proxywhirl.models import HealthStatus


class TestRuntimeProxyUpdates:
    """Test adding and removing proxies during active rotation."""

    @respx.mock
    def test_add_proxy_during_active_rotation(self):
        """Test that newly added proxies are immediately available for rotation."""
        # Start with one proxy
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        rotator = ProxyRotator(proxies=[proxy1])

        # Mark as healthy so it can be selected
        proxy1.health_status = HealthStatus.HEALTHY

        # Mock successful responses
        respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(200, json={"origin": "1.2.3.4"})
        )

        # Make first request (uses proxy1)
        response1 = rotator.get("https://httpbin.org/ip")
        assert response1.status_code == 200
        assert proxy1.total_requests == 1

        # Add a second proxy mid-rotation
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        proxy2.health_status = HealthStatus.HEALTHY
        rotator.add_proxy(proxy2)

        # Verify pool now has 2 proxies
        assert rotator.pool.size == 2

        # Make another request (round-robin will continue from proxy1)
        response2 = rotator.get("https://httpbin.org/ip")
        assert response2.status_code == 200

        # Make more requests to ensure both proxies are used in rotation
        for _ in range(6):
            rotator.get("https://httpbin.org/ip")

        # Both proxies should have been used multiple times now
        assert proxy1.total_requests >= 3
        assert proxy2.total_requests >= 3

    @respx.mock
    def test_remove_proxy_during_active_rotation(self):
        """Test that removed proxies are no longer used for requests."""
        # Start with two proxies
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        rotator = ProxyRotator(proxies=[proxy1, proxy2])

        proxy1.health_status = HealthStatus.HEALTHY
        proxy2.health_status = HealthStatus.HEALTHY

        # Mock successful responses
        respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(200, json={"origin": "1.2.3.4"})
        )

        # Make some requests
        rotator.get("https://httpbin.org/ip")
        rotator.get("https://httpbin.org/ip")

        # Both proxies should have been used
        assert proxy1.total_requests == 1
        assert proxy2.total_requests == 1

        # Remove proxy1
        rotator.remove_proxy(str(proxy1.id))

        # Verify pool now has only 1 proxy
        assert rotator.pool.size == 1
        assert proxy2 in rotator.pool.proxies
        assert proxy1 not in rotator.pool.proxies

        # Make more requests - only proxy2 should be used
        proxy2_requests_before = proxy2.total_requests
        for _ in range(5):
            rotator.get("https://httpbin.org/ip")

        # Proxy1 shouldn't have any new requests
        assert proxy1.total_requests == 1
        # Proxy2 should have all the new requests
        assert proxy2.total_requests == proxy2_requests_before + 5

    @respx.mock
    def test_add_remove_multiple_proxies_runtime(self):
        """Test adding and removing multiple proxies during rotation."""
        # Start with two proxies
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        rotator = ProxyRotator(proxies=[proxy1, proxy2])

        proxy1.health_status = HealthStatus.HEALTHY
        proxy2.health_status = HealthStatus.HEALTHY

        # Mock responses
        respx.get("https://httpbin.org/test").mock(
            return_value=httpx.Response(200, text="success")
        )

        # Initial state: 2 proxies
        assert rotator.pool.size == 2

        # Make some requests
        for _ in range(4):
            rotator.get("https://httpbin.org/test")

        # Add two more proxies
        proxy3 = Proxy(url="http://proxy3.example.com:8080")
        proxy4 = Proxy(url="http://proxy4.example.com:8080")
        proxy3.health_status = HealthStatus.HEALTHY
        proxy4.health_status = HealthStatus.HEALTHY

        rotator.add_proxy(proxy3)
        rotator.add_proxy(proxy4)

        # Now should have 4 proxies
        assert rotator.pool.size == 4

        # Make requests with all 4
        for _ in range(8):
            rotator.get("https://httpbin.org/test")

        # All proxies should have been used
        assert proxy1.total_requests >= 1
        assert proxy2.total_requests >= 1
        assert proxy3.total_requests >= 1
        assert proxy4.total_requests >= 1

        # Remove two proxies
        rotator.remove_proxy(str(proxy1.id))
        rotator.remove_proxy(str(proxy3.id))

        # Should be back to 2 proxies
        assert rotator.pool.size == 2
        assert proxy2 in rotator.pool.proxies
        assert proxy4 in rotator.pool.proxies

    @respx.mock
    def test_pool_remains_functional_after_updates(self):
        """Test that pool continues to function correctly after adds/removes."""
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        rotator = ProxyRotator(proxies=[proxy1])
        proxy1.health_status = HealthStatus.HEALTHY

        respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(200, json={"origin": "1.2.3.4"})
        )

        # Perform multiple add/remove cycles
        for i in range(3):
            # Add proxies
            new_proxy = Proxy(url=f"http://proxy{i+2}.example.com:8080")
            new_proxy.health_status = HealthStatus.HEALTHY
            rotator.add_proxy(new_proxy)

            # Make requests
            for _ in range(2):
                response = rotator.get("https://httpbin.org/ip")
                assert response.status_code == 200

            # Remove the newly added proxy
            rotator.remove_proxy(str(new_proxy.id))

        # Pool should still work with original proxy
        assert rotator.pool.size == 1
        response = rotator.get("https://httpbin.org/ip")
        assert response.status_code == 200

    @respx.mock
    def test_empty_pool_after_removing_all_proxies(self):
        """Test behavior when all proxies are removed."""
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        rotator = ProxyRotator(proxies=[proxy1, proxy2])

        proxy1.health_status = HealthStatus.HEALTHY
        proxy2.health_status = HealthStatus.HEALTHY

        # Remove all proxies
        rotator.remove_proxy(str(proxy1.id))
        rotator.remove_proxy(str(proxy2.id))

        # Pool should be empty
        assert rotator.pool.size == 0

        # Trying to make a request should raise an error
        from proxywhirl.exceptions import ProxyPoolEmptyError

        with pytest.raises(ProxyPoolEmptyError):
            rotator.get("https://httpbin.org/ip")
