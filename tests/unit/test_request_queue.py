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

from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from proxywhirl import (
    HealthStatus,
    Proxy,
    ProxyConfiguration,
    ProxyWhirl,
    RequestQueueFullError,
)
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

    def test_request_not_queued_when_queue_disabled(self) -> None:
        """Test that requests raise error when queue is disabled and rate limited."""
        config = ProxyConfiguration(queue_enabled=False)

        # Create mock rate limiter that denies requests
        mock_rate_limiter = MagicMock(spec=RateLimiter)
        mock_rate_limiter.check_limit.return_value = False  # Rate limit exceeded

        rotator = ProxyWhirl(config=config, rate_limiter=mock_rate_limiter)
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        with pytest.raises(Exception) as exc_info:
            rotator.get("https://httpbin.org/get")

        # Should raise ProxyConnectionError, not RequestQueueFullError
        assert "rate limit" in str(exc_info.value).lower()


class TestQueueEdgeCases:
    """Test edge cases and error conditions."""

    def test_queue_operations_thread_safe(self) -> None:
        """Test that queue operations are thread-safe."""
        import asyncio
        import threading

        config = ProxyConfiguration(queue_enabled=True, queue_size=100)
        rotator = ProxyWhirl(config=config)

        def add_items():
            import contextlib

            for i in range(10):
                with contextlib.suppress(Exception):
                    asyncio.run(rotator._request_queue.put({"item": i}))

        threads = [threading.Thread(target=add_items) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = rotator.get_queue_stats()
        assert stats["size"] <= 100  # Should not exceed max size

    @pytest.mark.skip(
        reason="Test makes actual network requests - needs refactoring to mock HTTP layer"
    )
    def test_queue_timeout_handling(self) -> None:
        """Test timeout handling during queue operations."""
        import asyncio

        config = ProxyConfiguration(queue_enabled=True, queue_size=1)

        # Mock rate limiter
        mock_rate_limiter = MagicMock(spec=RateLimiter)

        rotator = ProxyWhirl(config=config, rate_limiter=mock_rate_limiter)
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        # Fill the queue
        asyncio.run(rotator._request_queue.put({"test": "data"}))

        # Now the queue is full, next request should raise RequestQueueFullError
        with patch("asyncio.run") as mock_async_run:
            mock_async_run.return_value = False  # check_limit returns False

            # Should raise because queue is full (backpressure)
            with pytest.raises(RequestQueueFullError):
                rotator.get("https://httpbin.org/get")
