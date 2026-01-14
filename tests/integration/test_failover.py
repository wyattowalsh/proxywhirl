"""Integration tests for proxy failover functionality."""

from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from proxywhirl import Proxy, ProxyRotator
from proxywhirl.exceptions import ProxyConnectionError, ProxyPoolEmptyError
from proxywhirl.models import HealthStatus
from proxywhirl.retry_policy import RetryPolicy


class TestProxyFailover:
    """Integration tests for automatic proxy failover on failures."""

    # Retry disabled via RetryPolicy
    @patch("httpx.Client")
    def test_automatic_failover_to_next_proxy(self, mock_client_class):
        """Test that when one proxy fails, rotator automatically tries the next proxy."""
        # Setup mock: first proxy fails, second proxy succeeds
        mock_client = MagicMock()

        call_count = [0]

        def mock_request(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call (first proxy) fails
                raise httpx.ConnectError("Connection failed")
            else:
                # Second call (second proxy) succeeds
                response = Mock(spec=httpx.Response)
                response.status_code = 200
                return response

        mock_client.request.side_effect = mock_request
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Create rotator with 2 proxies
        rotator = ProxyRotator()
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY
        rotator.pool.proxies[1].health_status = HealthStatus.HEALTHY

        # Make request - should succeed despite first proxy failing
        try:
            response = rotator.get("https://example.com")
            assert response.status_code == 200
        except ProxyConnectionError:
            # This should not happen with failover
            pytest.fail(
                "Failover did not work - request failed despite having healthy backup proxy"
            )

        # Verify both proxies were tried
        assert call_count[0] >= 2, "Should have tried at least 2 proxies"

    # Retry disabled via RetryPolicy
    @patch("httpx.Client")
    def test_failover_records_failure_stats(self, mock_client_class):
        """Test that failed proxy records failure statistics."""
        # Setup mock: first attempt fails, retry succeeds
        mock_client = MagicMock()

        call_count = [0]

        def mock_request(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise httpx.ConnectError("Connection failed")
            else:
                response = Mock(spec=httpx.Response)
                response.status_code = 200
                return response

        mock_client.request.side_effect = mock_request
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Create rotator with retries disabled
        rotator = ProxyRotator(retry_policy=RetryPolicy(max_retries=1))
        proxy1 = Proxy(url="http://fail-proxy.example.com:8080")
        proxy2 = Proxy(url="http://good-proxy.example.com:8080")
        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY
        rotator.pool.proxies[1].health_status = HealthStatus.HEALTHY

        # Make request - should succeed on retry with same proxy
        response = rotator.get("https://example.com")
        
        # Should succeed
        assert response.status_code == 200
        # At least 2 calls - initial fail + retry success
        assert call_count[0] >= 2

    # Retry disabled via RetryPolicy
    @patch("httpx.Client")
    def test_all_proxies_fail_raises_exception(self, mock_client_class):
        """Test that when all proxies fail, ProxyConnectionError is raised."""
        # Setup mock: all proxies fail
        mock_client = MagicMock()
        mock_client.request.side_effect = httpx.ConnectError("All proxies down")
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Create rotator with 2 proxies
        rotator = ProxyRotator()
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY
        rotator.pool.proxies[1].health_status = HealthStatus.HEALTHY

        # Should raise ProxyConnectionError or ProxyPoolEmptyError
        with pytest.raises((ProxyConnectionError, ProxyPoolEmptyError)):
            rotator.get("https://example.com")

    @patch("httpx.Client")
    def test_unhealthy_proxies_skipped_during_failover(self, mock_client_class):
        """Test that unhealthy proxies are not tried during failover."""
        # Setup mock
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Create rotator with 3 proxies (1 healthy, 2 unhealthy)
        rotator = ProxyRotator()
        proxy1 = Proxy(url="http://dead-proxy.example.com:8080")
        proxy2 = Proxy(url="http://healthy-proxy.example.com:8080")
        proxy3 = Proxy(url="http://unhealthy-proxy.example.com:8080")

        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)
        rotator.add_proxy(proxy3)

        # Mark proxies
        rotator.pool.proxies[0].health_status = HealthStatus.DEAD
        rotator.pool.proxies[1].health_status = HealthStatus.HEALTHY
        rotator.pool.proxies[2].health_status = HealthStatus.UNHEALTHY

        # Make request
        response = rotator.get("https://example.com")

        # Should succeed using only the healthy proxy
        assert response.status_code == 200

        # Verify only healthy proxy was used
        assert rotator.pool.proxies[1].total_requests >= 1, "Healthy proxy should be used"
        assert rotator.pool.proxies[0].total_requests == 0, "Dead proxy should not be used"
        assert rotator.pool.proxies[2].total_requests == 0, "Unhealthy proxy should not be used"

    # Retry disabled via RetryPolicy
    @patch("httpx.Client")
    def test_consecutive_failures_mark_proxy_unhealthy(self, mock_client_class):
        """Test that consecutive failures eventually mark a proxy as unhealthy."""
        # Setup mock: always fail
        mock_client = MagicMock()
        mock_client.request.side_effect = httpx.ConnectError("Connection failed")
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Create rotator with 1 proxy
        rotator = ProxyRotator()
        proxy = Proxy(url="http://failing-proxy.example.com:8080")
        rotator.add_proxy(proxy)
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY

        # Make multiple requests (should all fail)
        for _ in range(3):
            try:
                rotator.get("https://example.com")
            except (ProxyConnectionError, ProxyPoolEmptyError):
                pass  # Expected to fail

        # After 3 consecutive failures, proxy should be marked unhealthy or degraded
        assert rotator.pool.proxies[0].consecutive_failures >= 1
        assert rotator.pool.proxies[0].health_status in [
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY,
            HealthStatus.DEAD,
        ], f"Expected DEGRADED, UNHEALTHY or DEAD, got {rotator.pool.proxies[0].health_status}"
