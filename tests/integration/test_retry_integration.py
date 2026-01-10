"""
Integration tests for retry execution.
"""

from unittest.mock import Mock, patch

import httpx
import pytest

from proxywhirl import Proxy, ProxyRotator, RetryPolicy
from proxywhirl.circuit_breaker import CircuitBreakerState
from proxywhirl.exceptions import ProxyConnectionError


class TestRetryExecution:
    """Integration tests for retry execution."""

    def test_retry_with_intermittent_failures(self):
        """Test retry succeeds after intermittent failures."""
        rotator = ProxyRotator(
            proxies=[
                Proxy(url="http://proxy1.example.com:8080"),
                Proxy(url="http://proxy2.example.com:8080"),
            ],
            retry_policy=RetryPolicy(max_attempts=3),
        )

        attempt_count = 0

        def mock_request(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 3:
                # First 2 attempts fail
                raise httpx.ConnectError("Connection failed")
            else:
                # Third attempt succeeds
                response = Mock(spec=httpx.Response)
                response.status_code = 200
                response.json.return_value = {"success": True}
                return response

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client.request = mock_request
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            # Should succeed after retries
            response = rotator.get("https://httpbin.org/ip")

        assert response.status_code == 200
        assert attempt_count == 3  # Took 3 attempts

    def test_max_attempts_enforcement(self):
        """Test that retries stop after max_attempts."""
        rotator = ProxyRotator(
            proxies=[Proxy(url="http://proxy1.example.com:8080")],
            retry_policy=RetryPolicy(max_attempts=3),
        )

        attempt_count = 0

        def mock_request(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            raise httpx.ConnectError("Connection failed")

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client.request = mock_request
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            # Should fail after max attempts
            with pytest.raises(ProxyConnectionError):
                rotator.get("https://httpbin.org/ip")

        # Should have tried exactly max_attempts times
        assert attempt_count == 3

    def test_retry_respects_status_codes(self):
        """Test that only configured status codes trigger retries."""
        rotator = ProxyRotator(
            proxies=[Proxy(url="http://proxy1.example.com:8080")],
            retry_policy=RetryPolicy(
                max_attempts=3,
                retry_status_codes=[502, 503],  # Only retry these
            ),
        )

        attempt_count = 0

        def mock_request(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1

            response = Mock(spec=httpx.Response)
            response.status_code = 504  # Not in retry list
            return response

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client.request = mock_request
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            # Should NOT retry on 504 (not in list)
            response = rotator.get("https://httpbin.org/ip")

        assert response.status_code == 504
        assert attempt_count == 1  # No retries

    def test_timeout_enforcement(self):
        """Test that total timeout is enforced."""
        rotator = ProxyRotator(
            proxies=[Proxy(url="http://proxy1.example.com:8080")],
            retry_policy=RetryPolicy(
                max_attempts=10,
                base_delay=2.0,
                timeout=3.0,  # Total timeout 3 seconds
            ),
        )

        def mock_request(*args, **kwargs):
            raise httpx.ConnectError("Connection failed")

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client.request = mock_request
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            # Should fail due to timeout, not max attempts
            with pytest.raises(ProxyConnectionError):
                rotator.get("https://httpbin.org/ip")

    def test_per_request_policy_override(self):
        """Test per-request retry policy override."""
        rotator = ProxyRotator(
            proxies=[Proxy(url="http://proxy1.example.com:8080")],
            retry_policy=RetryPolicy(max_attempts=5),  # Global: 5 attempts
        )

        attempt_count = 0

        def mock_request(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            raise httpx.ConnectError("Connection failed")

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client.request = mock_request
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            # Override with 2 attempts for this request
            per_request_policy = RetryPolicy(max_attempts=2)

            with pytest.raises(ProxyConnectionError):
                rotator._make_request(
                    "GET",
                    "https://httpbin.org/ip",
                    retry_policy=per_request_policy,
                )

        # Should use per-request policy (2 attempts)
        assert attempt_count == 2


class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker with retry logic."""

    def test_circuit_breaker_prevents_cascading_failures(self):
        """Test that circuit breaker excludes failing proxies."""
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")

        rotator = ProxyRotator(
            proxies=[proxy1, proxy2],
            retry_policy=RetryPolicy(max_attempts=1),  # Don't retry
        )

        # Manually open circuit breaker for proxy1
        cb1 = rotator.circuit_breakers[str(proxy1.id)]
        for _ in range(5):  # Threshold is 5
            cb1.record_failure()

        assert cb1.state == CircuitBreakerState.OPEN

        # Circuit breaker for proxy2 should be closed
        cb2 = rotator.circuit_breakers[str(proxy2.id)]
        assert cb2.state == CircuitBreakerState.CLOSED

        # Request should only try proxy2 (proxy1 circuit is open)
        def mock_request(*args, **kwargs):
            response = Mock(spec=httpx.Response)
            response.status_code = 200
            return response

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client.request = mock_request
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            response = rotator.get("https://httpbin.org/ip")

        assert response.status_code == 200

    def test_all_circuit_breakers_open_returns_503(self):
        """Test widespread failure detection (FR-019)."""
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")

        rotator = ProxyRotator(
            proxies=[proxy1, proxy2],
        )

        # Open both circuit breakers
        for proxy in [proxy1, proxy2]:
            cb = rotator.circuit_breakers[str(proxy.id)]
            for _ in range(5):
                cb.record_failure()
            assert cb.state == CircuitBreakerState.OPEN

        # Should fail immediately with descriptive error
        with pytest.raises(Exception, match="503|Service Temporarily Unavailable"):
            rotator.get("https://httpbin.org/ip")

    def test_half_open_health_check(self):
        """Test half-open state recovery."""
        proxy = Proxy(url="http://proxy1.example.com:8080")

        rotator = ProxyRotator(proxies=[proxy])

        # Open circuit breaker
        cb = rotator.circuit_breakers[str(proxy.id)]
        with patch("time.time", return_value=100.0):
            for _ in range(5):
                cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN

        # Wait for timeout - keep time patch active for entire test request
        # Don't call should_attempt_request() directly - it consumes the
        # one allowed test request slot in HALF_OPEN state
        with patch("time.time", return_value=130.0):  # 30 seconds later
            # Verify we've waited past the timeout
            assert cb.next_test_time is not None
            assert cb.next_test_time <= 130.0

            # Successful request should transition to HALF_OPEN then CLOSED
            def mock_request(*args, **kwargs):
                response = Mock(spec=httpx.Response)
                response.status_code = 200
                return response

            with patch("httpx.Client") as mock_client_class:
                mock_client = Mock()
                mock_client.request = mock_request
                mock_client.__enter__ = Mock(return_value=mock_client)
                mock_client.__exit__ = Mock(return_value=False)
                mock_client_class.return_value = mock_client

                response = rotator.get("https://httpbin.org/ip")

            assert response.status_code == 200
            assert cb.state == CircuitBreakerState.CLOSED
