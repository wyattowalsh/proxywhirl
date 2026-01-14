"""
Integration tests for configurable retry policies.
"""

from unittest.mock import Mock, patch

import httpx
import pytest

from proxywhirl import Proxy, ProxyRotator, RetryPolicy
from proxywhirl.exceptions import ProxyConnectionError
from proxywhirl.retry import BackoffStrategy


class TestPerRequestPolicyOverride:
    """Integration tests for per-request policy override."""

    def test_per_request_override_precedence(self):
        """Test that per-request policy takes precedence over global."""
        # Global policy: 5 attempts
        global_policy = RetryPolicy(max_attempts=5)

        rotator = ProxyRotator(
            proxies=[Proxy(url="http://proxy1.example.com:8080")],
            retry_policy=global_policy,
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


class TestRetryNonIdempotent:
    """Integration tests for non-idempotent request handling."""

    def test_post_skips_retry_by_default(self):
        """Test that POST requests skip retries by default."""
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

            with pytest.raises(ProxyConnectionError):
                rotator.post("https://httpbin.org/post", json={"data": "test"})

        # Should NOT retry POST (only 1 attempt)
        assert attempt_count == 1

    def test_post_retries_when_explicitly_enabled(self):
        """Test that POST retries when retry_non_idempotent=True."""
        policy = RetryPolicy(max_attempts=3, retry_non_idempotent=True)

        rotator = ProxyRotator(
            proxies=[Proxy(url="http://proxy1.example.com:8080")],
            retry_policy=policy,
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

            with pytest.raises(ProxyConnectionError):
                rotator.post("https://httpbin.org/post", json={"data": "test"})

        # Should retry POST (3 attempts)
        assert attempt_count == 3

    def test_get_always_retries(self):
        """Test that GET requests always retry (idempotent)."""
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

            with pytest.raises(ProxyConnectionError):
                rotator.get("https://httpbin.org/get")

        # Should retry GET (3 attempts)
        assert attempt_count == 3


class TestCustomStatusCodes:
    """Integration tests for custom retry status codes."""

    def test_only_configured_codes_trigger_retry(self):
        """Test that only configured status codes trigger retries."""
        policy = RetryPolicy(
            max_attempts=3,
            retry_status_codes=[502, 503],  # Only retry these
        )

        rotator = ProxyRotator(
            proxies=[Proxy(url="http://proxy1.example.com:8080")],
            retry_policy=policy,
        )

        attempt_count = 0

        def mock_request(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1

            response = Mock(spec=httpx.Response)
            response.status_code = 504  # NOT in retry list
            return response

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client.request = mock_request
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            # Should NOT retry on 504
            response = rotator.get("https://httpbin.org/status/504")

        assert response.status_code == 504
        assert attempt_count == 1  # No retries

    def test_configured_codes_do_trigger_retry(self):
        """Test that configured codes do trigger retries."""
        policy = RetryPolicy(
            max_attempts=3,
            retry_status_codes=[502, 503, 504],
        )

        rotator = ProxyRotator(
            proxies=[Proxy(url="http://proxy1.example.com:8080")],
            retry_policy=policy,
        )

        attempt_count = 0

        def mock_request(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 3:
                response = Mock(spec=httpx.Response)
                response.status_code = 503  # In retry list
                return response
            else:
                # Success on 3rd attempt
                response = Mock(spec=httpx.Response)
                response.status_code = 200
                return response

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client.request = mock_request
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            response = rotator.get("https://httpbin.org/status/503")

        assert response.status_code == 200
        assert attempt_count == 3  # Retried twice


class TestBackoffStrategyVariants:
    """Integration tests for different backoff strategies."""

    def test_exponential_backoff(self):
        """Test exponential backoff timing."""
        policy = RetryPolicy(
            max_attempts=4,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=1.0,
            multiplier=2.0,
            jitter=False,
        )

        rotator = ProxyRotator(
            proxies=[Proxy(url="http://proxy1.example.com:8080")],
            retry_policy=policy,
        )

        delays = []

        def mock_request(*args, **kwargs):
            raise httpx.ConnectError("Connection failed")

        def mock_sleep(delay):
            delays.append(delay)

        with patch("httpx.Client") as mock_client_class, patch("time.sleep", mock_sleep):
            mock_client = Mock()
            mock_client.request = mock_request
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            with pytest.raises(ProxyConnectionError):
                rotator.get("https://httpbin.org/get")

        # Should have exponential delays: 1, 2, 4
        assert len(delays) >= 2
        assert delays[0] == pytest.approx(1.0, abs=0.1)
        assert delays[1] == pytest.approx(2.0, abs=0.1)

    def test_linear_backoff(self):
        """Test linear backoff timing."""
        policy = RetryPolicy(
            max_attempts=4,
            backoff_strategy=BackoffStrategy.LINEAR,
            base_delay=2.0,
            jitter=False,
        )

        rotator = ProxyRotator(
            proxies=[Proxy(url="http://proxy1.example.com:8080")],
            retry_policy=policy,
        )

        delays = []

        def mock_request(*args, **kwargs):
            raise httpx.ConnectError("Connection failed")

        def mock_sleep(delay):
            delays.append(delay)

        with patch("httpx.Client") as mock_client_class, patch("time.sleep", mock_sleep):
            mock_client = Mock()
            mock_client.request = mock_request
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            with pytest.raises(ProxyConnectionError):
                rotator.get("https://httpbin.org/get")

        # Should have linear delays: 2, 4, 6
        assert len(delays) >= 2
        assert delays[0] == pytest.approx(2.0, abs=0.1)
        assert delays[1] == pytest.approx(4.0, abs=0.1)

    def test_fixed_backoff(self):
        """Test fixed backoff timing."""
        policy = RetryPolicy(
            max_attempts=4,
            backoff_strategy=BackoffStrategy.FIXED,
            base_delay=3.0,
            jitter=False,
        )

        rotator = ProxyRotator(
            proxies=[Proxy(url="http://proxy1.example.com:8080")],
            retry_policy=policy,
        )

        delays = []

        def mock_request(*args, **kwargs):
            raise httpx.ConnectError("Connection failed")

        def mock_sleep(delay):
            delays.append(delay)

        with patch("httpx.Client") as mock_client_class, patch("time.sleep", mock_sleep):
            mock_client = Mock()
            mock_client.request = mock_request
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            with pytest.raises(ProxyConnectionError):
                rotator.get("https://httpbin.org/get")

        # Should have fixed delays: 3, 3, 3
        assert all(d == pytest.approx(3.0, abs=0.1) for d in delays)
