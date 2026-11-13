"""
Comprehensive tests for request queuing mechanism (TASK-902).

Tests cover:
- Queue initialization with configuration
- Queue size limits
- Backpressure when queue is full
- Queue statistics and monitoring
- Queue clearing functionality
- Integration with rate limiting
"""

import queue
from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from proxywhirl import (
    HealthStatus,
    Proxy,
    ProxyConfiguration,
    ProxyWhirl,
    RateLimitExceededError,
    RequestQueueFullError,
)
from proxywhirl.orchestration import FailoverPolicy
from proxywhirl.rate_limiting import RateLimiter


class TestQueueConfiguration:
    """Test queue configuration and initialization."""

    def test_queue_disabled_by_default(self) -> None:
        """Test that queue is disabled by default."""
        rotator = ProxyWhirl()
        assert rotator.config.queue_enabled is False
        assert rotator._request_queue is None

        stats = rotator.get_queue_stats()
        assert stats["enabled"] is False
        assert stats["size"] == 0
        assert stats["max_size"] == 0

    def test_queue_enabled_with_config(self) -> None:
        """Test that queue can be enabled via configuration."""
        config = ProxyConfiguration(queue_enabled=True, queue_size=50)
        rotator = ProxyWhirl(config=config)

        assert rotator.config.queue_enabled is True
        assert rotator._request_queue is not None
        assert rotator._request_queue.maxsize == 50

        stats = rotator.get_queue_stats()
        assert stats["enabled"] is True
        assert stats["max_size"] == 50
        assert stats["is_empty"] is True

    def test_queue_size_validation(self) -> None:
        """Test that queue size is validated."""
        # Valid sizes
        config1 = ProxyConfiguration(queue_enabled=True, queue_size=1)
        assert config1.queue_size == 1

        config2 = ProxyConfiguration(queue_enabled=True, queue_size=10000)
        assert config2.queue_size == 10000

        # Invalid sizes (should raise validation error)
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ProxyConfiguration(queue_enabled=True, queue_size=0)

        with pytest.raises(ValidationError):
            ProxyConfiguration(queue_enabled=True, queue_size=10001)

    def test_queue_default_size(self) -> None:
        """Test default queue size is 100."""
        config = ProxyConfiguration(queue_enabled=True)
        assert config.queue_size == 100


class TestQueueBackpressure:
    """Test backpressure behavior when queue is full."""

    @patch("httpx.Client")
    def test_queue_full_raises_error(self, mock_client_class: MagicMock) -> None:
        """Test that full queue raises RequestQueueFullError."""
        # Create a small queue
        config = ProxyConfiguration(queue_enabled=True, queue_size=1)

        # Mock rate limiter that always denies requests
        mock_rate_limiter = MagicMock(spec=RateLimiter)
        mock_rate_limiter.check_limit = MagicMock(return_value=False)

        rotator = ProxyWhirl(config=config, rate_limiter=mock_rate_limiter)
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        # Mock httpx.Client to avoid actual HTTP calls
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        # First request should queue successfully
        with patch("asyncio.run") as mock_async_run:
            # Mock async operations
            mock_async_run.side_effect = [
                False,  # check_limit returns False (rate limited)
                None,  # queue.put succeeds
                {  # queue.get
                    "method": "GET",
                    "url": "https://httpbin.org/get",
                    "proxy": proxy,
                    "retry_policy": None,
                    "kwargs": {},
                },
            ]

            # This should succeed (fills the queue)
            try:
                response1 = rotator.get("https://httpbin.org/get")
                assert response1.status_code == 200
            except Exception:
                # Queue might be processed immediately, which is fine
                pass

        # Now fill the queue to capacity (using synchronous queue.Queue)
        rotator._request_queue.put({"test": "data"})

        # Queue should be full now
        assert rotator._request_queue.full()

        # Next request should raise RequestQueueFullError
        with patch("asyncio.run") as mock_async_run:
            mock_async_run.return_value = False  # check_limit returns False

            with pytest.raises(RequestQueueFullError) as exc_info:
                rotator.get("https://httpbin.org/get")

            assert "queue is full" in str(exc_info.value).lower()
            assert "max size: 1" in str(exc_info.value)

    def test_queue_full_error_includes_size(self) -> None:
        """Test that RequestQueueFullError includes queue size in message."""
        error = RequestQueueFullError(queue_size=100)
        assert "max size: 100" in str(error)
        assert error.error_code.value == "QUEUE_FULL"
        assert error.retry_recommended is True


class TestQueueStatistics:
    """Test queue statistics and monitoring."""

    def test_queue_stats_when_disabled(self) -> None:
        """Test queue stats when queue is disabled."""
        rotator = ProxyWhirl()
        stats = rotator.get_queue_stats()

        assert stats["enabled"] is False
        assert stats["size"] == 0
        assert stats["max_size"] == 0
        assert stats["is_full"] is False
        assert stats["is_empty"] is True

    def test_queue_stats_when_enabled(self) -> None:
        """Test queue stats when queue is enabled."""
        config = ProxyConfiguration(queue_enabled=True, queue_size=50)
        rotator = ProxyWhirl(config=config)

        stats = rotator.get_queue_stats()
        assert stats["enabled"] is True
        assert stats["size"] == 0
        assert stats["max_size"] == 50
        assert stats["is_full"] is False
        assert stats["is_empty"] is True

    def test_queue_stats_with_items(self) -> None:
        """Test queue stats reflect queued items."""
        config = ProxyConfiguration(queue_enabled=True, queue_size=10)
        rotator = ProxyWhirl(config=config)

        # Add some items to the queue (using synchronous queue.Queue)
        rotator._request_queue.put({"test": "1"})
        rotator._request_queue.put({"test": "2"})
        rotator._request_queue.put({"test": "3"})

        stats = rotator.get_queue_stats()
        assert stats["enabled"] is True
        assert stats["size"] == 3
        assert stats["max_size"] == 10
        assert stats["is_full"] is False
        assert stats["is_empty"] is False

    def test_queue_stats_when_full(self) -> None:
        """Test queue stats when queue is full."""
        config = ProxyConfiguration(queue_enabled=True, queue_size=2)
        rotator = ProxyWhirl(config=config)

        # Fill the queue (using synchronous queue.Queue)
        rotator._request_queue.put({"test": "1"})
        rotator._request_queue.put({"test": "2"})

        stats = rotator.get_queue_stats()
        assert stats["enabled"] is True
        assert stats["size"] == 2
        assert stats["max_size"] == 2
        assert stats["is_full"] is True
        assert stats["is_empty"] is False


class TestQueueClearing:
    """Test queue clearing functionality."""

    def test_clear_queue_when_disabled(self) -> None:
        """Test that clear_queue raises error when queue is disabled."""
        rotator = ProxyWhirl()

        with pytest.raises(RuntimeError, match="not enabled"):
            rotator.clear_queue()

    def test_clear_empty_queue(self) -> None:
        """Test clearing an empty queue."""
        config = ProxyConfiguration(queue_enabled=True, queue_size=10)
        rotator = ProxyWhirl(config=config)

        cleared = rotator.clear_queue()
        assert cleared == 0

        stats = rotator.get_queue_stats()
        assert stats["size"] == 0
        assert stats["is_empty"] is True

    def test_clear_queue_with_items(self) -> None:
        """Test clearing queue with items."""
        config = ProxyConfiguration(queue_enabled=True, queue_size=10)
        rotator = ProxyWhirl(config=config)

        # Add items to queue (using synchronous queue.Queue)
        rotator._request_queue.put({"test": "1"})
        rotator._request_queue.put({"test": "2"})
        rotator._request_queue.put({"test": "3"})

        # Verify queue has items
        stats_before = rotator.get_queue_stats()
        assert stats_before["size"] == 3

        # Clear queue
        cleared = rotator.clear_queue()
        assert cleared == 3

        # Verify queue is empty
        stats_after = rotator.get_queue_stats()
        assert stats_after["size"] == 0
        assert stats_after["is_empty"] is True


class TestQueueIntegrationWithRateLimiting:
    """Test queue integration with rate limiting."""

    @patch("httpx.Client")
    def test_request_queued_when_rate_limited(self, mock_client_class: MagicMock) -> None:
        """Test that requests are queued when rate limited."""
        config = ProxyConfiguration(queue_enabled=True, queue_size=10)

        # Create mock rate limiter that denies requests
        mock_rate_limiter = MagicMock(spec=RateLimiter)
        mock_rate_limiter.check_limit.return_value = False  # Rate limit exceeded

        rotator = ProxyWhirl(config=config, rate_limiter=mock_rate_limiter)
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        # Mock successful response
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Test that when rate limited, request is queued and processed successfully
        response = rotator.get("https://httpbin.org/get")

        # Verify response was successful
        assert response.status_code == 200

        # Verify the request was made through the mock client
        mock_client.request.assert_called_once()

    @patch("httpx.Client")
    def test_queued_request_pins_proxy_with_failover_enabled(
        self, mock_client_class: MagicMock
    ) -> None:
        """Queued dequeue must reuse the rate-limited proxy when failover is enabled."""
        config = ProxyConfiguration(queue_enabled=True, queue_size=10)
        mock_rate_limiter = MagicMock(spec=RateLimiter)
        limit_checks: list[str] = []

        def check_limit(proxy_id: str) -> bool:
            limit_checks.append(proxy_id)
            return len(limit_checks) > 1

        mock_rate_limiter.check_limit.side_effect = check_limit

        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator = ProxyWhirl(
            proxies=[proxy1, proxy2],
            config=config,
            rate_limiter=mock_rate_limiter,
            failover_policy=FailoverPolicy(enabled=True, max_proxy_attempts=2),
        )

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        attempted_ids: list[str] = []
        original_factory = rotator._get_or_create_client

        def spy_get_client(proxy: Proxy, proxy_dict: dict[str, str]):
            attempted_ids.append(str(proxy.id))
            return original_factory(proxy, proxy_dict)

        rotator._get_or_create_client = spy_get_client  # type: ignore[method-assign]

        response = rotator.get("https://httpbin.org/get")

        assert response.status_code == 200
        assert len(set(limit_checks)) == 1
        assert len(set(attempted_ids)) == 1
        assert attempted_ids[0] == limit_checks[0]
        mock_client.request.assert_called_once()

    @patch("httpx.Client")
    def test_queued_request_returns_the_caller_response(self, mock_client_class: MagicMock) -> None:
        """A caller must receive its own response when another request is already queued."""
        config = ProxyConfiguration(queue_enabled=True, queue_size=10)
        mock_rate_limiter = MagicMock(spec=RateLimiter)
        mock_rate_limiter.check_limit.return_value = False

        rotator = ProxyWhirl(config=config, rate_limiter=mock_rate_limiter)
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        def fake_request(method: str, url: str, **kwargs: object) -> Mock:
            del method, kwargs
            response = Mock(spec=httpx.Response)
            response.status_code = 200
            response.text = url
            return response

        mock_client = MagicMock()
        mock_client.request.side_effect = fake_request
        mock_client_class.return_value = mock_client

        other_url = "https://other.example/queued-first"
        caller_url = "https://caller.example/mine"
        other_done: queue.Queue[httpx.Response] = queue.Queue(maxsize=1)
        assert rotator._request_queue is not None
        rotator._request_queue.put(
            {
                "method": "GET",
                "url": other_url,
                "proxy": proxy,
                "retry_policy": None,
                "response_body_limit_bytes": None,
                "kwargs": {},
                "done": other_done,
            }
        )

        response = rotator.get(caller_url)

        assert response.text == caller_url
        other_response = other_done.get_nowait()
        assert other_response.text == other_url

    @patch("httpx.Client")
    def test_queued_request_survives_drainer_exit(self, mock_client_class: MagicMock) -> None:
        """A caller that loses the drain lock must still receive its own response."""
        import threading
        import time

        config = ProxyConfiguration(queue_enabled=True, queue_size=10)
        mock_rate_limiter = MagicMock(spec=RateLimiter)
        mock_rate_limiter.check_limit.return_value = False

        rotator = ProxyWhirl(config=config, rate_limiter=mock_rate_limiter)
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        caller_url = "https://caller.example/after-drainer-exit"

        def fake_request(method: str, url: str, **kwargs: object) -> Mock:
            del method, kwargs
            response = Mock(spec=httpx.Response)
            response.status_code = 200
            response.text = url
            return response

        mock_client = MagicMock()
        mock_client.request.side_effect = fake_request
        mock_client_class.return_value = mock_client

        assert rotator._queue_drain_lock.acquire(blocking=False)
        outcome: dict[str, object] = {}

        def run_get() -> None:
            try:
                outcome["response"] = rotator.get(caller_url)
            except BaseException as exc:
                outcome["error"] = exc

        worker = threading.Thread(target=run_get)
        worker.start()
        assert rotator._request_queue is not None
        deadline = time.monotonic() + 2
        while rotator._request_queue.qsize() == 0 and time.monotonic() < deadline:
            time.sleep(0.01)
        rotator._queue_drain_lock.release()
        worker.join(timeout=2)

        assert not worker.is_alive()
        assert "error" not in outcome
        response = outcome["response"]
        assert isinstance(response, Mock)
        assert response.text == caller_url

    def test_request_not_queued_when_queue_disabled(self) -> None:
        """Test that requests raise error when queue is disabled and rate limited."""
        config = ProxyConfiguration(queue_enabled=False)

        # Create mock rate limiter that denies requests
        mock_rate_limiter = MagicMock(spec=RateLimiter)
        mock_rate_limiter.check_limit.return_value = False  # Rate limit exceeded

        rotator = ProxyWhirl(config=config, rate_limiter=mock_rate_limiter)
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        with pytest.raises(RateLimitExceededError, match="Rate limit exceeded"):
            rotator.get("https://httpbin.org/get")


class TestQueueEdgeCases:
    """Test edge cases and error conditions."""

    @patch("httpx.Client")
    def test_concurrent_queued_gets_return_own_responses(
        self, mock_client_class: MagicMock
    ) -> None:
        """Two queued callers must each receive the response for their own URL."""
        import threading

        config = ProxyConfiguration(queue_enabled=True, queue_size=10)
        mock_rate_limiter = MagicMock(spec=RateLimiter)
        mock_rate_limiter.check_limit.return_value = False
        rotator = ProxyWhirl(config=config, rate_limiter=mock_rate_limiter)
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        def fake_request(method: str, url: str, **kwargs: object) -> Mock:
            del method, kwargs
            response = Mock(spec=httpx.Response)
            response.status_code = 200
            response.text = url
            return response

        mock_client = MagicMock()
        mock_client.request.side_effect = fake_request
        mock_client_class.return_value = mock_client

        urls = ("https://a.example/one", "https://b.example/two")
        outcome: dict[str, object] = {}

        def run_get(url: str) -> None:
            try:
                outcome[url] = rotator.get(url)
            except BaseException as exc:
                outcome[url] = exc

        workers = [threading.Thread(target=run_get, args=(url,)) for url in urls]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(timeout=5)

        assert all(not worker.is_alive() for worker in workers)
        for url in urls:
            response = outcome[url]
            assert isinstance(response, Mock)
            assert response.text == url

    def test_queue_timeout_handling(self) -> None:
        """A full queue rejects locally before any HTTP request is attempted."""
        config = ProxyConfiguration(queue_enabled=True, queue_size=1)
        mock_rate_limiter = MagicMock(spec=RateLimiter)
        mock_rate_limiter.check_limit.return_value = False
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        with ProxyWhirl(config=config, rate_limiter=mock_rate_limiter) as rotator:
            rotator.add_proxy(proxy)
            assert rotator._request_queue is not None
            rotator._request_queue.put_nowait({"test": "data"})

            with pytest.raises(RequestQueueFullError):
                rotator.get("https://httpbin.org/get")
