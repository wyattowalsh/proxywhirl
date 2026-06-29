"""Integration tests for proxy failover functionality."""

from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from proxywhirl import Proxy, ProxyWhirl
from proxywhirl.exceptions import ProxyConnectionError, ProxyPoolEmptyError
from proxywhirl.models import HealthStatus
from proxywhirl.orchestration import FailoverPolicy
from proxywhirl.retry import RetryPolicy


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

        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        rotator = ProxyWhirl(
            proxies=[proxy1, proxy2],
            failover_policy=FailoverPolicy(enabled=True, max_proxy_attempts=2),
            retry_policy=RetryPolicy(max_attempts=1),
        )
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY
        rotator.pool.proxies[1].health_status = HealthStatus.HEALTHY

        attempted_ids: list[str] = []
        original_factory = rotator._get_or_create_client

        def spy_get_client(proxy: Proxy, proxy_dict: dict[str, str]):
            attempted_ids.append(str(proxy.id))
            return original_factory(proxy, proxy_dict)

        rotator._get_or_create_client = spy_get_client  # type: ignore[method-assign]

        response = rotator.get("https://example.com")
        assert response.status_code == 200
        assert len(set(attempted_ids)) >= 2, "Failover should try multiple distinct proxy IDs"

    # Retry disabled via RetryPolicy
    @patch("httpx.Client")
    def test_inner_retry_succeeds_on_same_proxy(self, mock_client_class):
        """Inner RetryExecutor retry succeeds on the initially selected proxy.

        FailoverPolicy is disabled by default, so this does not rotate to proxy2.
        """
        mock_client = MagicMock()

        call_count = [0]

        def mock_request(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise httpx.ConnectError("Connection failed")
            response = Mock(spec=httpx.Response)
            response.status_code = 200
            return response

        mock_client.request.side_effect = mock_request
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl(retry_policy=RetryPolicy(max_retries=1))
        proxy1 = Proxy(url="http://fail-proxy.example.com:8080")
        proxy2 = Proxy(url="http://good-proxy.example.com:8080")
        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY
        rotator.pool.proxies[1].health_status = HealthStatus.HEALTHY

        attempted_ids: list[str] = []
        original_factory = rotator._get_or_create_client

        def spy_get_client(proxy: Proxy, proxy_dict: dict[str, str]):
            attempted_ids.append(str(proxy.id))
            return original_factory(proxy, proxy_dict)

        rotator._get_or_create_client = spy_get_client  # type: ignore[method-assign]

        response = rotator.get("https://example.com")

        assert response.status_code == 200
        assert call_count[0] >= 2
        assert len(set(attempted_ids)) == 1

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
        rotator = ProxyWhirl()
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
        rotator = ProxyWhirl()
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
        rotator = ProxyWhirl()
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
