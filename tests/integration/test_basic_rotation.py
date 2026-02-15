"""Integration tests for basic proxy rotation functionality."""

from unittest.mock import MagicMock, Mock, patch

import httpx

from proxywhirl import Proxy, ProxyWhirl
from proxywhirl.models import HealthStatus


class TestBasicRotation:
    """Integration tests for basic round-robin proxy rotation."""

    @patch("httpx.Client")
    def test_round_robin_rotation_with_three_proxies(self, mock_client_class):
        """Test that 10 requests cycle through 3 proxies in round-robin fashion."""
        # Setup mock HTTP client
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.text = "Success"

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Create rotator with 3 proxies
        rotator = ProxyWhirl()
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        proxy3 = Proxy(url="http://proxy3.example.com:8080")

        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)
        rotator.add_proxy(proxy3)

        # Mark all as healthy
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY
        rotator.pool.proxies[1].health_status = HealthStatus.HEALTHY
        rotator.pool.proxies[2].health_status = HealthStatus.HEALTHY

        # Make 10 requests (3 full cycles + 1)
        for _ in range(10):
            rotator.get("https://example.com")

        # Verify each proxy was used fairly
        # With 10 requests and 3 proxies: 2 proxies get 3 requests, 1 proxy gets 4 requests
        request_counts = [p.total_requests for p in rotator.pool.proxies]
        request_counts.sort()

        assert request_counts == [
            3,
            3,
            4,
        ], f"Expected fair distribution [3, 3, 4], got {request_counts}"

        # Verify all proxies were successful
        for proxy in rotator.pool.proxies:
            assert proxy.total_successes == proxy.total_requests
            assert proxy.total_failures == 0

    @patch("httpx.Client")
    def test_all_proxies_get_traffic(self, mock_client_class):
        """Test that over multiple requests, all proxies receive traffic."""
        # Setup mock
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Create rotator with 5 proxies
        rotator = ProxyWhirl()
        for i in range(5):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            rotator.add_proxy(proxy)
            rotator.pool.proxies[i].health_status = HealthStatus.HEALTHY

        # Make 20 requests
        for _ in range(20):
            rotator.get("https://example.com")

        # Verify all proxies received requests (check success counts)
        for i, proxy in enumerate(rotator.pool.proxies):
            assert proxy.total_requests == 4, (
                f"Proxy {i} should have handled 4 requests (20 total / 5 proxies), "
                f"but handled {proxy.total_requests}"
            )
            assert proxy.total_successes == 4, (
                f"Proxy {i} should have 4 successes, got {proxy.total_successes}"
            )

    @patch("httpx.Client")
    def test_single_proxy_no_rotation(self, mock_client_class):
        """Test that with a single proxy, all requests use that proxy."""
        # Setup mock
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Create rotator with 1 proxy
        rotator = ProxyWhirl()
        proxy = Proxy(url="http://single-proxy.example.com:8080")
        rotator.add_proxy(proxy)
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY

        # Make 10 requests
        for _ in range(10):
            rotator.get("https://example.com")

        # Verify single proxy handled all requests
        assert rotator.pool.proxies[0].total_requests == 10
        assert rotator.pool.proxies[0].total_successes == 10

    @patch("httpx.Client")
    def test_rotation_preserves_order_across_methods(self, mock_client_class):
        """Test that rotation order is consistent across different HTTP methods."""
        # Setup mock
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Create rotator with 3 proxies
        rotator = ProxyWhirl()
        for i in range(3):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            rotator.add_proxy(proxy)
            rotator.pool.proxies[i].health_status = HealthStatus.HEALTHY

        # Track proxy usage
        proxy_urls = []

        # Make requests with different HTTP methods
        for method in [rotator.get, rotator.post, rotator.put]:
            current_proxy = rotator.strategy.select(rotator.pool)
            if current_proxy:
                proxy_urls.append(current_proxy.url)
            method("https://example.com")

        # Should cycle through proxies regardless of HTTP method
        assert len(proxy_urls) == 3
        assert len(set(proxy_urls)) == 3, "All 3 proxies should be used"

    @patch("httpx.Client")
    def test_dynamic_proxy_addition_during_rotation(self, mock_client_class):
        """Test that adding proxies mid-rotation works correctly."""
        # Setup mock
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Create rotator with 2 proxies
        rotator = ProxyWhirl()
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY
        rotator.pool.proxies[1].health_status = HealthStatus.HEALTHY

        # Make 5 requests
        for _ in range(5):
            rotator.get("https://example.com")

        # Add a third proxy
        proxy3 = Proxy(url="http://proxy3.example.com:8080")
        rotator.add_proxy(proxy3)
        rotator.pool.proxies[2].health_status = HealthStatus.HEALTHY

        # Make 6 more requests (2 full cycles with 3 proxies)
        for _ in range(6):
            rotator.get("https://example.com")

        # Verify all proxies were used
        # First 2 proxies: 5 requests (2.5 each) + 6 requests (2 each) = 4-5 requests each
        # Third proxy: 2 requests
        assert rotator.pool.proxies[0].total_requests >= 4
        assert rotator.pool.proxies[1].total_requests >= 4
        assert rotator.pool.proxies[2].total_requests == 2
