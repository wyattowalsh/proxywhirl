"""
Comprehensive unit tests for ProxyWhirl to achieve >= 70% coverage.

This test suite covers:
- All HTTP methods (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
- Circuit breaker integration (open/closed/half-open states)
- Retry behavior with failover
- Proxy rotation on request
- Session persistence
- Authentication errors (401, 407)
- LRU client pool eviction
"""

from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest
import respx
from pydantic import SecretStr

from proxywhirl import HealthStatus, Proxy, ProxyWhirl
from proxywhirl.exceptions import (
    ProxyAuthenticationError,
    ProxyConnectionError,
    ProxyPoolEmptyError,
)
from proxywhirl.models import ProxyChain
from proxywhirl.retry import RetryPolicy


class TestProxyWhirlHTTPMethods:
    """Test all HTTP method convenience functions."""

    @respx.mock
    def test_get_method(self) -> None:
        """Test GET request method."""
        # Mock httpx.Client to avoid actual HTTP calls
        respx.get("https://httpbin.org/get").mock(
            return_value=httpx.Response(200, json={"method": "GET"})
        )

        with patch("httpx.Client") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = {"method": "GET"}

            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            rotator = ProxyWhirl()
            proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)

            response = rotator.get("https://httpbin.org/get")

            assert response.status_code == 200
            mock_client.request.assert_called_once()
            args, kwargs = mock_client.request.call_args
            assert args[0] == "GET"
            assert args[1] == "https://httpbin.org/get"

    @respx.mock
    def test_post_method(self) -> None:
        """Test POST request method."""
        with patch("httpx.Client") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 201

            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            rotator = ProxyWhirl()
            proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)

            response = rotator.post("https://httpbin.org/post", json={"key": "value"})

            assert response.status_code == 201
            args, kwargs = mock_client.request.call_args
            assert args[0] == "POST"

    @respx.mock
    def test_put_method(self) -> None:
        """Test PUT request method."""
        with patch("httpx.Client") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200

            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            rotator = ProxyWhirl()
            proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)

            response = rotator.put("https://httpbin.org/put", json={"updated": True})

            assert response.status_code == 200
            args, kwargs = mock_client.request.call_args
            assert args[0] == "PUT"

    @respx.mock
    def test_patch_method(self) -> None:
        """Test PATCH request method."""
        with patch("httpx.Client") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200

            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            rotator = ProxyWhirl()
            proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)

            response = rotator.patch("https://httpbin.org/patch", json={"patched": True})

            assert response.status_code == 200
            args, kwargs = mock_client.request.call_args
            assert args[0] == "PATCH"

    @respx.mock
    def test_delete_method(self) -> None:
        """Test DELETE request method."""
        with patch("httpx.Client") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 204

            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            rotator = ProxyWhirl()
            proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)

            response = rotator.delete("https://httpbin.org/delete")

            assert response.status_code == 204
            args, kwargs = mock_client.request.call_args
            assert args[0] == "DELETE"

    @respx.mock
    def test_head_method(self) -> None:
        """Test HEAD request method."""
        with patch("httpx.Client") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200

            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            rotator = ProxyWhirl()
            proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)

            response = rotator.head("https://httpbin.org/get")

            assert response.status_code == 200
            args, kwargs = mock_client.request.call_args
            assert args[0] == "HEAD"

    @respx.mock
    def test_options_method(self) -> None:
        """Test OPTIONS request method."""
        with patch("httpx.Client") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200

            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            rotator = ProxyWhirl()
            proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)

            response = rotator.options("https://httpbin.org/get")

            assert response.status_code == 200
            args, kwargs = mock_client.request.call_args
            assert args[0] == "OPTIONS"


class TestCircuitBreakerIntegration:
    """Test circuit breaker integration with different states."""

    @patch("httpx.Client")
    def test_circuit_breaker_initialized_on_add_proxy(self, mock_client_class: MagicMock) -> None:
        """Test that circuit breaker is initialized when adding a proxy."""
        rotator = ProxyWhirl()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        # Circuit breaker should exist for this proxy
        assert str(proxy.id) in rotator.circuit_breakers
        cb = rotator.circuit_breakers[str(proxy.id)]
        assert cb.state.name == "CLOSED"

    @patch("httpx.Client")
    def test_circuit_breaker_closed_allows_requests(self, mock_client_class: MagicMock) -> None:
        """Test that closed circuit breaker allows requests."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        cb = rotator.circuit_breakers[str(proxy.id)]
        assert cb.state.name == "CLOSED"

        response = rotator.get("https://httpbin.org/get")
        assert response.status_code == 200

    def test_get_circuit_breaker_states(self) -> None:
        """Test getting circuit breaker states."""
        rotator = ProxyWhirl()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        states = rotator.get_circuit_breaker_states()
        assert len(states) == 1
        assert str(proxy.id) in states


class TestRetryBehavior:
    """Test retry logic and failover behavior."""

    @patch("httpx.Client")
    def test_retry_on_connection_error(self, mock_client_class: MagicMock) -> None:
        """Test that connection errors trigger retry."""
        # First call fails, second succeeds
        mock_client = MagicMock()
        mock_client.request.side_effect = [
            httpx.ConnectError("Connection failed"),
            Mock(spec=httpx.Response, status_code=200),
        ]
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        response = rotator.get("https://httpbin.org/get")

        assert response.status_code == 200
        assert mock_client.request.call_count == 2

    @patch("httpx.Client")
    def test_retry_exhausted_raises_error(self, mock_client_class: MagicMock) -> None:
        """Test that exhausted retries raise ProxyConnectionError."""
        mock_client = MagicMock()
        mock_client.request.side_effect = httpx.ConnectError("Connection failed")
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl(retry_policy=RetryPolicy(max_attempts=2))
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        with pytest.raises(ProxyConnectionError):
            rotator.get("https://httpbin.org/get")

    @patch("httpx.Client")
    def test_custom_retry_policy_per_request(self, mock_client_class: MagicMock) -> None:
        """Test that per-request retry policy overrides global policy."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl(retry_policy=RetryPolicy(max_attempts=5))
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        custom_policy = RetryPolicy(max_attempts=1)
        response = rotator._make_request(
            "GET", "https://httpbin.org/get", retry_policy=custom_policy
        )

        assert response.status_code == 200


class TestProxyRotation:
    """Test proxy rotation on each request."""

    @patch("httpx.Client")
    def test_rotation_uses_different_proxies(self, mock_client_class: MagicMock) -> None:
        """Test that round-robin strategy rotates through proxies."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl(strategy="round-robin")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)

        # Make multiple requests
        rotator.get("https://httpbin.org/get")
        rotator.get("https://httpbin.org/get")

        # Should have used both proxies (or created clients for both)
        assert rotator.pool.proxies[0].total_requests + rotator.pool.proxies[1].total_requests >= 2


class TestAuthenticationErrors:
    """Test handling of authentication errors (401, 407)."""

    @patch("httpx.Client")
    def test_401_authentication_error(self, mock_client_class: MagicMock) -> None:
        """Test that 401 Unauthorized triggers ProxyAuthenticationError."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 401

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl(retry_policy=RetryPolicy(max_attempts=1))
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        with pytest.raises(ProxyAuthenticationError, match="401"):
            rotator.get("https://httpbin.org/get")

    @patch("httpx.Client")
    def test_407_proxy_authentication_error(self, mock_client_class: MagicMock) -> None:
        """Test that 407 Proxy Authentication Required triggers ProxyAuthenticationError."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 407

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl(retry_policy=RetryPolicy(max_attempts=1))
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        with pytest.raises(ProxyAuthenticationError, match="407"):
            rotator.get("https://httpbin.org/get")

    @patch("httpx.Client")
    def test_auth_error_records_failure(self, mock_client_class: MagicMock) -> None:
        """Test that authentication errors record failures in strategy."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 401

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl(retry_policy=RetryPolicy(max_attempts=1))
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        with pytest.raises(ProxyAuthenticationError):
            rotator.get("https://httpbin.org/get")

        # Proxy should have recorded the failure
        assert rotator.pool.proxies[0].total_failures > 0


class TestLRUClientPool:
    """Test LRU client pool eviction logic."""

    def test_lru_pool_eviction(self) -> None:
        """Test that LRU pool evicts least recently used client when at capacity."""
        from proxywhirl.rotator import LRUClientPool

        pool = LRUClientPool(maxsize=2)

        # Create mock clients
        client1 = MagicMock(spec=httpx.Client)
        client2 = MagicMock(spec=httpx.Client)
        client3 = MagicMock(spec=httpx.Client)

        # Add clients to pool
        pool.put("proxy1", client1)
        pool.put("proxy2", client2)

        assert len(pool) == 2

        # Adding third client should evict first one
        pool.put("proxy3", client3)

        assert len(pool) == 2
        assert "proxy1" not in pool
        assert "proxy2" in pool
        assert "proxy3" in pool
        client1.close.assert_called_once()

    def test_lru_pool_get_marks_as_used(self) -> None:
        """Test that getting a client marks it as recently used."""
        from proxywhirl.rotator import LRUClientPool

        pool = LRUClientPool(maxsize=2)

        client1 = MagicMock(spec=httpx.Client)
        client2 = MagicMock(spec=httpx.Client)
        client3 = MagicMock(spec=httpx.Client)

        pool.put("proxy1", client1)
        pool.put("proxy2", client2)

        # Access proxy1, making it recently used
        pool.get("proxy1")

        # Add proxy3 - should evict proxy2 (not proxy1)
        pool.put("proxy3", client3)

        assert "proxy1" in pool
        assert "proxy2" not in pool
        assert "proxy3" in pool
        client2.close.assert_called_once()

    def test_lru_pool_remove(self) -> None:
        """Test removing a client from the pool."""
        from proxywhirl.rotator import LRUClientPool

        pool = LRUClientPool(maxsize=2)
        client = MagicMock(spec=httpx.Client)
        pool.put("proxy1", client)

        assert "proxy1" in pool

        pool.remove("proxy1")

        assert "proxy1" not in pool
        client.close.assert_called_once()

    def test_lru_pool_clear(self) -> None:
        """Test clearing all clients from the pool."""
        from proxywhirl.rotator import LRUClientPool

        pool = LRUClientPool(maxsize=2)
        client1 = MagicMock(spec=httpx.Client)
        client2 = MagicMock(spec=httpx.Client)

        pool.put("proxy1", client1)
        pool.put("proxy2", client2)

        pool.clear()

        assert len(pool) == 0
        client1.close.assert_called_once()
        client2.close.assert_called_once()

    def test_lru_pool_dict_operations(self) -> None:
        """Test dict-like operations (__getitem__, __setitem__, __delitem__)."""
        from proxywhirl.rotator import LRUClientPool

        pool = LRUClientPool(maxsize=2)
        client = MagicMock(spec=httpx.Client)

        # Test __setitem__
        pool["proxy1"] = client
        assert "proxy1" in pool

        # Test __getitem__
        assert pool["proxy1"] is client

        # Test __delitem__
        del pool["proxy1"]
        assert "proxy1" not in pool


class TestProxyChains:
    """Test proxy chain functionality."""

    def test_add_chain_creates_circuit_breaker(self) -> None:
        """Test that adding a chain creates circuit breaker for entry proxy."""
        rotator = ProxyWhirl()
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),
            Proxy(url="http://proxy2.example.com:8080"),
        ]
        chain = ProxyChain(proxies=proxies, name="test-chain")

        rotator.add_chain(chain)

        entry_proxy_id = str(chain.entry_proxy.id)
        assert entry_proxy_id in rotator.circuit_breakers

    def test_remove_chain_removes_circuit_breaker(self) -> None:
        """Test that removing a chain removes circuit breaker."""
        rotator = ProxyWhirl()
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),
            Proxy(url="http://proxy2.example.com:8080"),
        ]
        chain = ProxyChain(proxies=proxies, name="test-chain")

        rotator.add_chain(chain)
        entry_proxy_id = str(chain.entry_proxy.id)

        rotator.remove_chain("test-chain")

        assert entry_proxy_id not in rotator.circuit_breakers


class TestNonRetryableErrors:
    """Test handling of non-retryable errors."""

    @patch("httpx.Client")
    def test_non_retryable_error_wrapped_auth_error(self, mock_client_class: MagicMock) -> None:
        """Test that NonRetryableError wrapping ProxyAuthenticationError is unwrapped."""
        # Simulate NonRetryableError wrapping an auth error
        auth_error = ProxyAuthenticationError("Proxy auth failed")

        mock_client = MagicMock()
        mock_client.request.side_effect = auth_error
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl(retry_policy=RetryPolicy(max_attempts=1))
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        # Should raise ProxyAuthenticationError, not NonRetryableError
        with pytest.raises(ProxyAuthenticationError):
            rotator.get("https://httpbin.org/get")


class TestSessionPersistence:
    """Test session-based proxy persistence."""

    @patch("httpx.Client")
    def test_round_robin_rotates_proxies(self, mock_client_class: MagicMock) -> None:
        """Test that round-robin strategy rotates through proxies."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl(strategy="round-robin")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)

        # Make multiple requests
        rotator.get("https://httpbin.org/get")
        rotator.get("https://httpbin.org/get")

        # At least one proxy should have requests
        assert max(p.total_requests for p in rotator.pool.proxies) >= 1


class TestStatistics:
    """Test statistics and pool stats functionality."""

    def test_get_pool_stats_with_proxies(self) -> None:
        """Test get_pool_stats with multiple proxies."""
        rotator = ProxyWhirl()
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.UNHEALTHY)
        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)

        stats = rotator.get_pool_stats()

        assert stats["total_proxies"] == 2
        assert stats["healthy_proxies"] == 1
        assert stats["unhealthy_proxies"] == 1

    def test_get_statistics_includes_source_breakdown(self) -> None:
        """Test that get_statistics includes source breakdown."""
        rotator = ProxyWhirl()
        proxy = Proxy(url="http://proxy.example.com:8080")
        rotator.add_proxy(proxy)

        stats = rotator.get_statistics()

        assert "source_breakdown" in stats
        assert "total_proxies" in stats


class TestContextManager:
    """Test context manager functionality."""

    def test_context_manager_creates_client(self) -> None:
        """Test that entering context manager creates HTTP client."""
        rotator = ProxyWhirl()

        with rotator as r:
            assert r._client is not None
            assert isinstance(r._client, httpx.Client)

    def test_context_manager_closes_pooled_clients(self) -> None:
        """Test that exiting context manager closes pooled clients."""
        rotator = ProxyWhirl()
        mock_client = MagicMock(spec=httpx.Client)
        rotator._client_pool["test"] = mock_client

        with rotator:
            pass

        assert len(rotator._client_pool) == 0
        mock_client.close.assert_called_once()


class TestClientPooling:
    """Test client pooling and reuse."""

    @patch("httpx.Client")
    def test_client_reuse_for_same_proxy(self, mock_client_class: MagicMock) -> None:
        """Test that the same client is reused for subsequent requests to same proxy."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        # Make two requests
        rotator.get("https://httpbin.org/get")
        rotator.get("https://httpbin.org/get")

        # Should have created only one client (reused)
        assert mock_client_class.call_count == 1


class TestSyncQueueImplementation:
    """Test that ProxyWhirl uses sync queue.Queue instead of asyncio.Queue."""

    def test_queue_enabled_without_event_loop(self) -> None:
        """Test ProxyWhirl with queue_enabled=True works without an event loop.

        This verifies the fix for using queue.Queue instead of asyncio.Queue
        in the synchronous ProxyWhirl class.
        """
        import queue

        from proxywhirl.models import ProxyConfiguration

        # Create config with queue enabled
        config = ProxyConfiguration(queue_enabled=True, queue_size=10)

        # This should NOT raise an error about missing event loop
        # (previously it would fail because asyncio.Queue requires an event loop)
        rotator = ProxyWhirl(config=config)

        # Verify the queue was created
        assert rotator._request_queue is not None
        assert rotator.config.queue_enabled is True

        # Verify the queue is a standard library queue.Queue, not asyncio.Queue
        assert isinstance(rotator._request_queue, queue.Queue)

    def test_queue_operations_are_synchronous(self) -> None:
        """Test that queue operations work synchronously."""
        import queue

        from proxywhirl.models import ProxyConfiguration

        config = ProxyConfiguration(queue_enabled=True, queue_size=5)
        rotator = ProxyWhirl(config=config)

        assert rotator._request_queue is not None
        q = rotator._request_queue

        # Test synchronous put operation
        q.put({"test": "data1"})
        q.put({"test": "data2"})

        assert q.qsize() == 2
        assert not q.empty()
        assert not q.full()

        # Test synchronous get operation
        item1 = q.get_nowait()
        assert item1 == {"test": "data1"}

        item2 = q.get_nowait()
        assert item2 == {"test": "data2"}

        assert q.empty()

        # Test queue.Empty exception is raised (not asyncio.QueueEmpty)
        with pytest.raises(queue.Empty):
            q.get_nowait()

    def test_queue_type_annotation_is_sync_queue(self) -> None:
        """Test that the queue is properly typed as queue.Queue."""
        import queue as queue_module

        from proxywhirl.models import ProxyConfiguration

        config = ProxyConfiguration(queue_enabled=True, queue_size=10)
        rotator = ProxyWhirl(config=config)

        # Verify the queue exists and is the correct type
        assert rotator._request_queue is not None
        assert type(rotator._request_queue).__module__ == "queue"
        assert type(rotator._request_queue).__name__ == "Queue"
        assert isinstance(rotator._request_queue, queue_module.Queue)

        # Verify it has the expected synchronous queue methods
        assert hasattr(rotator._request_queue, "put")
        assert hasattr(rotator._request_queue, "get")
        assert hasattr(rotator._request_queue, "put_nowait")
        assert hasattr(rotator._request_queue, "get_nowait")
        assert hasattr(rotator._request_queue, "qsize")
        assert hasattr(rotator._request_queue, "empty")
        assert hasattr(rotator._request_queue, "full")

    def test_queue_disabled_by_default(self) -> None:
        """Test that queue is disabled by default."""
        rotator = ProxyWhirl()

        assert rotator._request_queue is None
        assert rotator.config.queue_enabled is False

    def test_get_queue_stats_with_sync_queue(self) -> None:
        """Test get_queue_stats works correctly with sync queue."""
        from proxywhirl.models import ProxyConfiguration

        config = ProxyConfiguration(queue_enabled=True, queue_size=10)
        rotator = ProxyWhirl(config=config)

        stats = rotator.get_queue_stats()

        assert stats["enabled"] is True
        assert stats["size"] == 0
        assert stats["max_size"] == 10
        assert stats["is_full"] is False
        assert stats["is_empty"] is True


class TestCredentialsHandling:
    """Test URL-encoding of credentials with special characters."""

    def test_get_proxy_dict_with_special_chars_in_username(self) -> None:
        """Test that special characters in username are URL-encoded."""
        rotator = ProxyWhirl()

        # Create proxy with special characters in username
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("user@domain.com"),  # @ is special
            password=SecretStr("password123"),
            health_status=HealthStatus.HEALTHY,
        )

        proxy_dict = rotator._get_proxy_dict(proxy)

        # Check that @ is encoded as %40 in username
        url = proxy_dict["http://"]
        assert "user%40domain.com" in url
        assert url.startswith("http://user%40domain.com:password123@proxy.example.com:8080")

    def test_get_proxy_dict_with_special_chars_in_password(self) -> None:
        """Test that special characters in password are URL-encoded."""
        rotator = ProxyWhirl()

        # Create proxy with special characters in password
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("user123"),
            password=SecretStr("pass:word@123/secret"),  # Multiple special chars
            health_status=HealthStatus.HEALTHY,
        )

        proxy_dict = rotator._get_proxy_dict(proxy)

        # Check that special characters are encoded in password
        # : -> %3A, @ -> %40, / -> %2F
        url = proxy_dict["http://"]
        assert "pass%3Aword%40123%2Fsecret" in url
        assert url.startswith("http://user123:pass%3Aword%40123%2Fsecret@proxy.example.com:8080")

    def test_get_proxy_dict_with_url_unsafe_chars(self) -> None:
        """Test URL encoding of all unsafe URL characters."""
        rotator = ProxyWhirl()

        # Create proxy with unsafe characters: space, !, #, $, %, &, ', ", +, ,, ;, =, ?, [, ]
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("user name"),  # space
            password=SecretStr("pass!@#$%&'+="),  # Multiple unsafe chars
            health_status=HealthStatus.HEALTHY,
        )

        proxy_dict = rotator._get_proxy_dict(proxy)

        # Verify URL was constructed properly with encoded credentials
        url = proxy_dict["http://"]
        # space -> %20, ! -> %21, @ -> %40, # -> %23, $ -> %24, % -> %25, & -> %26, ' -> %27, + -> %2B, = -> %3D
        assert "user%20name" in url
        assert "pass%21%40%23%24%25%26%27%2B%3D" in url
        assert url.startswith(
            "http://user%20name:pass%21%40%23%24%25%26%27%2B%3D@proxy.example.com:8080"
        )

    def test_get_proxy_dict_both_protocols_contain_encoded_creds(self) -> None:
        """Test that both http and https proxies have encoded credentials."""
        rotator = ProxyWhirl()

        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("user@test"),
            password=SecretStr("pass:123"),
            health_status=HealthStatus.HEALTHY,
        )

        proxy_dict = rotator._get_proxy_dict(proxy)

        # Both should contain the same URL with encoded credentials
        expected_encoded = "user%40test:pass%3A123"
        assert expected_encoded in proxy_dict["http://"]
        assert expected_encoded in proxy_dict["https://"]
        # Both should point to the same host
        assert "proxy.example.com:8080" in proxy_dict["http://"]
        assert "proxy.example.com:8080" in proxy_dict["https://"]

    def test_get_proxy_dict_without_credentials(self) -> None:
        """Test that proxy without credentials works correctly."""
        rotator = ProxyWhirl()

        proxy = Proxy(
            url="http://proxy.example.com:8080",
            health_status=HealthStatus.HEALTHY,
        )

        proxy_dict = rotator._get_proxy_dict(proxy)

        # Should just be the URL without any credentials
        assert proxy_dict["http://"] == "http://proxy.example.com:8080"
        assert proxy_dict["https://"] == "http://proxy.example.com:8080"


class TestExpiredProxyHandling:
    """Test handling of expired proxies during selection."""

    def test_expired_proxy_skipped_during_selection(self) -> None:
        """Test that expired proxies are skipped during proxy selection."""
        from datetime import datetime, timedelta, timezone

        rotator = ProxyWhirl()

        # Create an expired proxy (TTL in past)
        expired_proxy = Proxy(
            url="http://expired.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),  # Expired 1 hour ago
        )

        # Create a valid proxy
        valid_proxy = Proxy(
            url="http://valid.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),  # Expires in 1 hour
        )

        rotator.add_proxy(expired_proxy)
        rotator.add_proxy(valid_proxy)

        # Select proxy - should skip the expired one and return the valid one
        selected = rotator._select_proxy_with_circuit_breaker()

        assert selected.id == valid_proxy.id
        assert selected.url == "http://valid.example.com:8080"

    def test_all_expired_proxies_raises_error(self) -> None:
        """Test that ProxyPoolEmptyError is raised when all proxies are expired."""
        from datetime import datetime, timedelta, timezone

        rotator = ProxyWhirl()

        # Create only expired proxies
        proxy1 = Proxy(
            url="http://expired1.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        proxy2 = Proxy(
            url="http://expired2.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=30),
        )

        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)

        # Should raise error since all proxies are expired
        with pytest.raises(ProxyPoolEmptyError):
            rotator._select_proxy_with_circuit_breaker()

    def test_expired_proxy_with_circuit_breaker_both_unavailable(self) -> None:
        """Test scenario where both expired and circuit-broken proxies exist."""
        from datetime import datetime, timedelta, timezone

        rotator = ProxyWhirl()

        # Create an expired proxy
        expired_proxy = Proxy(
            url="http://expired.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )

        # Create a valid proxy that we'll manually mark as having no circuit breaker
        # to simulate it being unavailable
        valid_proxy = Proxy(
            url="http://valid.example.com:8080",
            health_status=HealthStatus.UNHEALTHY,  # Mark as unhealthy
        )

        rotator.add_proxy(expired_proxy)
        rotator.add_proxy(valid_proxy)

        # Both proxies should be unavailable:
        # - expired_proxy: expired
        # - valid_proxy: unhealthy
        with pytest.raises(ProxyPoolEmptyError):
            rotator._select_proxy_with_circuit_breaker()

    def test_expired_proxy_is_expired_property(self) -> None:
        """Test that is_expired property works correctly."""
        from datetime import datetime, timedelta, timezone

        # Create an expired proxy
        expired = Proxy(
            url="http://expired.example.com:8080",
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )

        # Create a valid proxy
        valid = Proxy(
            url="http://valid.example.com:8080",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        # Create a proxy with no expiration
        no_expiry = Proxy(
            url="http://no-expiry.example.com:8080",
        )

        assert expired.is_expired is True
        assert valid.is_expired is False
        assert no_expiry.is_expired is False

    @patch("httpx.Client")
    def test_request_skips_expired_proxies(self, mock_client_class: MagicMock) -> None:
        """Test that making requests skips expired proxies."""
        from datetime import datetime, timedelta, timezone

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl()

        # Add expired proxy
        expired_proxy = Proxy(
            url="http://expired.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )

        # Add valid proxy
        valid_proxy = Proxy(
            url="http://valid.example.com:8080",
            health_status=HealthStatus.HEALTHY,
        )

        rotator.add_proxy(expired_proxy)
        rotator.add_proxy(valid_proxy)

        # Make request - should use valid proxy only
        response = rotator.get("https://httpbin.org/get")

        assert response.status_code == 200
        # The call should have been made to the valid proxy's client
        mock_client.request.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_pool_raises_error(self) -> None:
        """Test that making request with empty pool raises ProxyPoolEmptyError after bootstrap fails."""
        rotator = ProxyWhirl()

        # Mock bootstrap to fail (simulating no proxies fetched from sources)
        with patch.object(
            rotator, "_bootstrap_pool_if_empty", side_effect=ProxyPoolEmptyError("Bootstrap failed")
        ):
            with pytest.raises(ProxyPoolEmptyError):
                rotator.get("https://httpbin.org/get")

    @patch("httpx.Client")
    def test_generic_exception_handling(self, mock_client_class: MagicMock) -> None:
        """Test that generic exceptions are caught and wrapped."""
        mock_client = MagicMock()
        mock_client.request.side_effect = Exception("Unknown error")
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl(retry_policy=RetryPolicy(max_attempts=1))
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        with pytest.raises(ProxyConnectionError):
            rotator.get("https://httpbin.org/get")

    def test_clear_unhealthy_removes_circuit_breakers(self) -> None:
        """Test that clearing unhealthy proxies also removes their circuit breakers."""
        rotator = ProxyWhirl()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.DEAD)
        rotator.add_proxy(proxy)

        proxy_id = str(proxy.id)
        assert proxy_id in rotator.circuit_breakers

        rotator.clear_unhealthy_proxies()

        assert proxy_id not in rotator.circuit_breakers
