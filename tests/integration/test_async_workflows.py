"""
Integration tests for async workflows with AsyncProxyRotator.

Tests cover:
- Complete async rotation workflows
- Async request with retry on failure
- Circuit breaker integration
- Concurrent request handling
- Context manager cleanup
- Real HTTP testing with mocked endpoints
"""

import asyncio
from unittest.mock import Mock, patch

import httpx
import pytest
import respx

from proxywhirl import AsyncProxyRotator
from proxywhirl.circuit_breaker import CircuitBreakerState
from proxywhirl.exceptions import (
    ProxyAuthenticationError,
    ProxyConnectionError,
    ProxyPoolEmptyError,
)
from proxywhirl.models import HealthStatus, Proxy
from proxywhirl.retry import BackoffStrategy, RetryPolicy


class TestAsyncRotationWorkflow:
    """Test complete async rotation workflows."""

    async def test_async_rotation_workflow(self):
        """Test complete async rotation workflow."""
        async with AsyncProxyRotator() as rotator:
            # Add proxies
            proxy1 = Proxy(url="http://test-proxy1:8080", protocol="http")
            proxy2 = Proxy(url="http://test-proxy2:8080", protocol="http")

            await rotator.add_proxy(proxy1)
            await rotator.add_proxy(proxy2)

            # Verify proxies were added
            assert rotator.pool.size == 2

            # Get proxy (circuit breakers should allow selection)
            selected = await rotator.get_proxy()
            assert selected is not None
            assert selected.url in ["http://test-proxy1:8080", "http://test-proxy2:8080"]

            # Verify pool stats
            stats = rotator.get_pool_stats()
            assert stats["total_proxies"] == 2
            assert stats["healthy_proxies"] >= 1  # At least one should be healthy/unknown

    async def test_async_proxy_addition_workflow(self):
        """Test async proxy addition workflow."""
        async with AsyncProxyRotator() as rotator:
            # Add proxy from URL string
            await rotator.add_proxy("http://proxy1.example.com:8080")
            assert rotator.pool.size == 1

            # Add proxy from Proxy object
            proxy = Proxy(url="http://proxy2.example.com:8080", protocol="http")
            await rotator.add_proxy(proxy)
            assert rotator.pool.size == 2

            # Verify circuit breakers were created
            assert len(rotator.circuit_breakers) == 2

    async def test_async_proxy_removal_workflow(self):
        """Test async proxy removal workflow."""
        async with AsyncProxyRotator() as rotator:
            # Add proxy
            proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
            await rotator.add_proxy(proxy)
            proxy_id = str(proxy.id)

            assert rotator.pool.size == 1
            assert proxy_id in rotator.circuit_breakers

            # Remove proxy
            await rotator.remove_proxy(proxy_id)

            assert rotator.pool.size == 0
            assert proxy_id not in rotator.circuit_breakers

    async def test_async_statistics_workflow(self):
        """Test async statistics collection workflow."""
        async with AsyncProxyRotator() as rotator:
            # Add proxies from different sources
            proxy1 = Proxy(url="http://proxy1.example.com:8080", protocol="http", source="user")
            proxy2 = Proxy(url="http://proxy2.example.com:8080", protocol="http", source="fetched")

            await rotator.add_proxy(proxy1)
            await rotator.add_proxy(proxy2)

            # Get comprehensive statistics
            stats = rotator.get_statistics()

            assert stats["total_proxies"] == 2
            assert "source_breakdown" in stats
            # Source breakdown should have at least one entry
            assert len(stats["source_breakdown"]) > 0


class TestAsyncRequestWithRetry:
    """Test async requests with retry logic."""

    @respx.mock
    async def test_async_request_success_on_first_try(self):
        """Test async request succeeds on first attempt."""
        # Mock successful response
        respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(200, json={"origin": "1.2.3.4"})
        )

        async with AsyncProxyRotator() as rotator:
            proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
            await rotator.add_proxy(proxy)

            # Make request
            response = await rotator.get("https://httpbin.org/ip")

            assert response.status_code == 200
            assert response.json()["origin"] == "1.2.3.4"

            # Verify success was recorded
            stats = rotator.get_pool_stats()
            assert stats["total_successes"] == 1

    @respx.mock
    async def test_async_request_retry_on_failure(self):
        """Test async request retries on failure."""
        # Mock: first two attempts fail, third succeeds
        route = respx.get("https://httpbin.org/ip").mock(
            side_effect=[
                httpx.ConnectError("Connection refused"),
                httpx.ConnectError("Connection timeout"),
                httpx.Response(200, json={"origin": "1.2.3.4"}),
            ]
        )

        retry_policy = RetryPolicy(
            max_attempts=3,
            backoff_strategy=BackoffStrategy.FIXED,
            base_delay=0.1,  # Fast retry for tests
        )

        async with AsyncProxyRotator(retry_policy=retry_policy) as rotator:
            proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
            await rotator.add_proxy(proxy)

            # Make request - should retry and eventually succeed
            response = await rotator.get("https://httpbin.org/ip")

            assert response.status_code == 200
            # Route should be called 3 times (2 failures + 1 success)
            assert route.call_count == 3

    async def test_async_request_exhausts_retries(self):
        """Test async request fails after exhausting retries."""
        retry_policy = RetryPolicy(
            max_attempts=2,
            backoff_strategy=BackoffStrategy.FIXED,
            base_delay=0.01,
        )

        async with AsyncProxyRotator(retry_policy=retry_policy) as rotator:
            proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
            await rotator.add_proxy(proxy)

            # Mock request function to always fail
            async def failing_request(*args, **kwargs):
                raise httpx.ConnectError("Connection failed")

            # Patch the client's request method
            with (
                patch.object(httpx.AsyncClient, "request", new=failing_request),
                pytest.raises(ProxyConnectionError),
            ):
                await rotator.get("https://httpbin.org/ip")

            # Verify failures were recorded
            assert rotator.pool.proxies[0].total_failures > 0

    @respx.mock
    async def test_async_request_authentication_error(self):
        """Test async request handles 407 authentication error."""
        # Mock 407 Proxy Authentication Required
        respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(407, text="Proxy Authentication Required")
        )

        async with AsyncProxyRotator() as rotator:
            proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
            await rotator.add_proxy(proxy)

            # Should raise ProxyAuthenticationError
            with pytest.raises(ProxyAuthenticationError) as exc_info:
                await rotator.get("https://httpbin.org/ip")

            assert "authentication required" in str(exc_info.value).lower()


class TestAsyncCircuitBreakerIntegration:
    """Test circuit breaker integration in async workflows."""

    async def test_async_circuit_breaker_triggers_on_failures(self):
        """Test circuit breaker opens after threshold failures."""
        async with AsyncProxyRotator() as rotator:
            proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
            await rotator.add_proxy(proxy)

            proxy_id = str(proxy.id)
            circuit_breaker = rotator.circuit_breakers[proxy_id]

            # Record failures to trigger circuit breaker
            for _ in range(circuit_breaker.failure_threshold):
                circuit_breaker.record_failure()

            # Circuit breaker should be OPEN
            assert circuit_breaker.state == CircuitBreakerState.OPEN

            # Should not attempt request when circuit is open
            assert not circuit_breaker.should_attempt_request()

    async def test_async_circuit_breaker_recovery(self):
        """Test circuit breaker transitions to half-open and recovers."""

        async with AsyncProxyRotator() as rotator:
            proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
            await rotator.add_proxy(proxy)

            proxy_id = str(proxy.id)
            circuit_breaker = rotator.circuit_breakers[proxy_id]

            # Set short timeout for testing
            circuit_breaker.timeout_duration = 0.1

            # Open circuit breaker
            for _ in range(circuit_breaker.failure_threshold):
                circuit_breaker.record_failure()

            assert circuit_breaker.state == CircuitBreakerState.OPEN

            # Wait for timeout to elapse
            await asyncio.sleep(0.2)

            # Should transition to HALF_OPEN
            can_attempt = circuit_breaker.should_attempt_request()
            assert can_attempt
            assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN

            # Record success to close circuit
            circuit_breaker.record_success()
            assert circuit_breaker.state == CircuitBreakerState.CLOSED

    async def test_async_all_circuit_breakers_open_raises_error(self):
        """Test that all open circuit breakers raises ProxyPoolEmptyError."""
        async with AsyncProxyRotator() as rotator:
            # Add multiple proxies
            proxy1 = Proxy(url="http://proxy1.example.com:8080", protocol="http")
            proxy2 = Proxy(url="http://proxy2.example.com:8080", protocol="http")

            await rotator.add_proxy(proxy1)
            await rotator.add_proxy(proxy2)

            # Open all circuit breakers
            for proxy_id in rotator.circuit_breakers:
                cb = rotator.circuit_breakers[proxy_id]
                for _ in range(cb.failure_threshold):
                    cb.record_failure()
                assert cb.state == CircuitBreakerState.OPEN

            # Attempting to get proxy should raise error
            with pytest.raises(ProxyPoolEmptyError) as exc_info:
                await rotator.get_proxy()

            assert "circuit breaker" in str(exc_info.value).lower()

    async def test_async_circuit_breaker_manual_reset(self):
        """Test manual reset of circuit breaker."""
        async with AsyncProxyRotator() as rotator:
            proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
            await rotator.add_proxy(proxy)

            proxy_id = str(proxy.id)
            circuit_breaker = rotator.circuit_breakers[proxy_id]

            # Open circuit breaker
            for _ in range(circuit_breaker.failure_threshold):
                circuit_breaker.record_failure()

            assert circuit_breaker.state == CircuitBreakerState.OPEN

            # Manually reset
            rotator.reset_circuit_breaker(proxy_id)

            assert circuit_breaker.state == CircuitBreakerState.CLOSED
            assert circuit_breaker.failure_count == 0


class TestAsyncConcurrentRequests:
    """Test concurrent request handling."""

    @respx.mock
    async def test_async_concurrent_requests_succeed(self):
        """Test multiple concurrent requests through rotator."""
        # Mock successful responses
        respx.get(url__regex=r"https://httpbin.org/.*").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        async with AsyncProxyRotator() as rotator:
            # Add multiple proxies
            for i in range(3):
                proxy = Proxy(url=f"http://proxy{i}.example.com:8080", protocol="http")
                await rotator.add_proxy(proxy)

            # Make concurrent requests
            tasks = [rotator.get(f"https://httpbin.org/get?id={i}") for i in range(10)]

            responses = await asyncio.gather(*tasks)

            # All requests should succeed
            assert len(responses) == 10
            assert all(r.status_code == 200 for r in responses)

            # Verify stats
            stats = rotator.get_pool_stats()
            assert stats["total_successes"] == 10

    @respx.mock
    async def test_async_concurrent_requests_with_mixed_results(self):
        """Test concurrent requests with some failures."""
        # Mock mixed responses (some succeed, some fail)
        call_count = 0

        def response_callback(request):
            nonlocal call_count
            call_count += 1
            # First 3 succeed, rest fail
            if call_count <= 3:
                return httpx.Response(200, json={"success": True})
            else:
                raise httpx.ConnectError("Connection failed")

        respx.get(url__regex=r"https://httpbin.org/.*").mock(side_effect=response_callback)

        retry_policy = RetryPolicy(max_attempts=1)  # No retries for faster test

        async with AsyncProxyRotator(retry_policy=retry_policy) as rotator:
            proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
            await rotator.add_proxy(proxy)

            # Make concurrent requests
            tasks = [rotator.get(f"https://httpbin.org/get?id={i}") for i in range(5)]

            # Use gather with return_exceptions to handle failures
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count successes and failures
            successes = sum(1 for r in results if isinstance(r, httpx.Response))
            failures = sum(1 for r in results if isinstance(r, Exception))

            assert successes == 3
            assert failures == 2

    async def test_async_concurrent_requests_stress_test(self):
        """Stress test with many concurrent requests."""
        async with AsyncProxyRotator() as rotator:
            # Add proxies
            for i in range(5):
                proxy = Proxy(url=f"http://proxy{i}.example.com:8080", protocol="http")
                await rotator.add_proxy(proxy)

            # Mock all requests to succeed quickly
            async def mock_request(*args, **kwargs):
                await asyncio.sleep(0.001)  # Simulate network delay
                return Mock(status_code=200, json=lambda: {"success": True})

            with patch.object(httpx.AsyncClient, "request", new=mock_request):
                # Make many concurrent requests
                tasks = [rotator.get(f"https://example.com/endpoint{i}") for i in range(100)]

                responses = await asyncio.gather(*tasks, return_exceptions=True)

                # All should succeed
                assert len(responses) == 100
                successes = sum(1 for r in responses if not isinstance(r, Exception))
                assert successes == 100


class TestAsyncContextManagerCleanup:
    """Test proper cleanup on context manager exit."""

    async def test_async_context_manager_cleanup(self):
        """Test proper cleanup on context manager exit."""
        rotator = AsyncProxyRotator()

        # Add proxies
        await rotator.add_proxy("http://proxy1.example.com:8080")
        await rotator.add_proxy("http://proxy2.example.com:8080")

        # Enter context manager
        async with rotator:
            # Client should be created
            assert rotator._client is not None

            # Make a request to populate client pool
            async def mock_request(*args, **kwargs):
                return Mock(status_code=200)

            with patch.object(httpx.AsyncClient, "request", new=mock_request):
                await rotator.get("https://example.com")

        # After exit, client should be None
        assert rotator._client is None

        # Client pool should be empty (all clients closed)
        assert len(rotator._client_pool) == 0

    async def test_async_context_manager_cleanup_on_exception(self):
        """Test cleanup happens even when exception occurs."""
        rotator = AsyncProxyRotator()

        try:
            async with rotator:
                # Client should be created
                assert rotator._client is not None

                # Raise exception
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Cleanup should still happen
        assert rotator._client is None

    async def test_async_aggregation_thread_cleanup(self):
        """Test that aggregation thread is stopped on cleanup."""
        rotator = AsyncProxyRotator()

        # Thread should be running
        assert rotator._aggregation_thread.is_alive()

        async with rotator:
            pass

        # Wait a bit for thread to stop
        await asyncio.sleep(0.1)

        # Thread should be stopped (or at least stopping)
        # Note: Thread may still be alive briefly after context exit
        # so we check the stop event instead
        assert rotator._stop_event.is_set()

    async def test_async_client_pool_cleanup(self):
        """Test that all clients in pool are closed on cleanup."""
        async with AsyncProxyRotator() as rotator:
            # Add proxies
            for i in range(3):
                await rotator.add_proxy(f"http://proxy{i}.example.com:8080")

            # Create clients by making requests
            async def mock_request(*args, **kwargs):
                return Mock(status_code=200)

            with patch.object(httpx.AsyncClient, "request", new=mock_request):
                # Make requests to create clients for each proxy
                for _ in range(3):
                    await rotator.get("https://example.com")

            # Clients should be in pool
            assert len(rotator._client_pool) > 0

        # After exit, pool should be empty
        assert len(rotator._client_pool) == 0


class TestAsyncHTTPMethods:
    """Test all async HTTP methods."""

    @respx.mock
    async def test_async_all_http_methods(self):
        """Test all HTTP methods work correctly."""
        # Mock all methods
        respx.get("https://httpbin.org/get").mock(
            return_value=httpx.Response(200, json={"method": "GET"})
        )
        respx.post("https://httpbin.org/post").mock(
            return_value=httpx.Response(201, json={"method": "POST"})
        )
        respx.put("https://httpbin.org/put").mock(
            return_value=httpx.Response(200, json={"method": "PUT"})
        )
        respx.delete("https://httpbin.org/delete").mock(return_value=httpx.Response(204, text=""))
        respx.patch("https://httpbin.org/patch").mock(
            return_value=httpx.Response(200, json={"method": "PATCH"})
        )
        respx.head("https://httpbin.org/head").mock(return_value=httpx.Response(200, text=""))
        respx.route(method="OPTIONS").mock(return_value=httpx.Response(200, text=""))

        async with AsyncProxyRotator() as rotator:
            proxy = Proxy(url="http://proxy.example.com:8080", protocol="http")
            await rotator.add_proxy(proxy)

            # Test all methods
            response_get = await rotator.get("https://httpbin.org/get")
            assert response_get.status_code == 200

            response_post = await rotator.post("https://httpbin.org/post", json={"key": "value"})
            assert response_post.status_code == 201

            response_put = await rotator.put("https://httpbin.org/put", json={"key": "value"})
            assert response_put.status_code == 200

            response_delete = await rotator.delete("https://httpbin.org/delete")
            assert response_delete.status_code == 204

            response_patch = await rotator.patch("https://httpbin.org/patch", json={"key": "value"})
            assert response_patch.status_code == 200

            response_head = await rotator.head("https://httpbin.org/head")
            assert response_head.status_code == 200

            response_options = await rotator.options("https://httpbin.org/options")
            assert response_options.status_code == 200

            # Verify all requests were counted
            stats = rotator.get_pool_stats()
            assert stats["total_successes"] == 7


class TestAsyncStrategySwapping:
    """Test hot-swapping strategies in async context."""

    async def test_async_hot_swap_strategy(self):
        """Test strategy can be swapped during runtime."""
        async with AsyncProxyRotator(strategy="round-robin") as rotator:
            # Add proxies
            for i in range(3):
                await rotator.add_proxy(f"http://proxy{i}.example.com:8080")

            # Initial strategy
            assert rotator.strategy.__class__.__name__ == "RoundRobinStrategy"

            # Hot-swap to random strategy
            rotator.set_strategy("random")

            assert rotator.strategy.__class__.__name__ == "RandomStrategy"

            # Verify selection still works
            proxy = await rotator.get_proxy()
            assert proxy is not None

    async def test_async_strategy_swap_performance(self):
        """Test strategy swap completes quickly (<100ms)."""
        import time

        async with AsyncProxyRotator(strategy="round-robin") as rotator:
            # Add proxies
            for i in range(10):
                await rotator.add_proxy(f"http://proxy{i}.example.com:8080")

            # Measure swap time
            start = time.perf_counter()
            rotator.set_strategy("weighted")
            elapsed_ms = (time.perf_counter() - start) * 1000

            # Should complete in <100ms (SC-009)
            assert elapsed_ms < 100


class TestAsyncUnhealthyProxyCleanup:
    """Test cleanup of unhealthy proxies in async context."""

    async def test_async_clear_unhealthy_proxies(self):
        """Test clearing unhealthy proxies."""
        async with AsyncProxyRotator() as rotator:
            # Add healthy and unhealthy proxies
            healthy = Proxy(url="http://healthy.example.com:8080", protocol="http")
            healthy.health_status = HealthStatus.HEALTHY

            unhealthy = Proxy(url="http://unhealthy.example.com:8080", protocol="http")
            unhealthy.health_status = HealthStatus.UNHEALTHY

            dead = Proxy(url="http://dead.example.com:8080", protocol="http")
            dead.health_status = HealthStatus.DEAD

            await rotator.add_proxy(healthy)
            await rotator.add_proxy(unhealthy)
            await rotator.add_proxy(dead)

            assert rotator.pool.size == 3

            # Clear unhealthy
            removed_count = await rotator.clear_unhealthy_proxies()

            assert removed_count == 2  # unhealthy + dead
            assert rotator.pool.size == 1

            # Only healthy proxy should remain
            remaining_proxy = rotator.pool.proxies[0]
            assert remaining_proxy.health_status == HealthStatus.HEALTHY

    async def test_async_clear_unhealthy_removes_circuit_breakers(self):
        """Test that clearing unhealthy proxies also removes circuit breakers."""
        async with AsyncProxyRotator() as rotator:
            # Add unhealthy proxy
            unhealthy = Proxy(url="http://unhealthy.example.com:8080", protocol="http")
            unhealthy.health_status = HealthStatus.DEAD

            await rotator.add_proxy(unhealthy)
            proxy_id = str(unhealthy.id)

            # Verify circuit breaker exists
            assert proxy_id in rotator.circuit_breakers

            # Clear unhealthy
            await rotator.clear_unhealthy_proxies()

            # Circuit breaker should be removed
            assert proxy_id not in rotator.circuit_breakers
