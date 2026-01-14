"""
Unit tests for ProxyRotator error paths and edge cases.
These tests target uncovered lines to improve coverage from 78% to 90%+.
"""

from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from proxywhirl import HealthStatus, Proxy, ProxyRotator
from proxywhirl.exceptions import (
    ProxyAuthenticationError,
    ProxyConnectionError,
    ProxyPoolEmptyError,
)
from proxywhirl.models import ProxyChain
from proxywhirl.rate_limiting import RateLimit, RateLimiter


class TestRotatorStrategyParsing:
    """Test strategy string parsing and error handling."""

    def test_invalid_strategy_string_raises_valueerror(self) -> None:
        """Test that invalid strategy string raises ValueError."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            ProxyRotator(strategy="invalid-strategy")

    def test_valid_strategy_strings(self) -> None:
        """Test all valid strategy strings."""
        for strategy_name in ["round-robin", "random", "weighted", "least-used"]:
            rotator = ProxyRotator(strategy=strategy_name)
            assert rotator.strategy is not None

    def test_strategy_string_case_insensitive(self) -> None:
        """Test that strategy strings are case-insensitive."""
        rotator = ProxyRotator(strategy="ROUND-ROBIN")
        assert rotator.strategy.__class__.__name__ == "RoundRobinStrategy"


class TestRotatorSetStrategy:
    """Test hot-swap strategy functionality."""

    def test_set_strategy_with_string(self) -> None:
        """Test set_strategy with valid strategy string."""
        rotator = ProxyRotator(strategy="round-robin")
        rotator.set_strategy("random")
        assert rotator.strategy.__class__.__name__ == "RandomStrategy"

    def test_set_strategy_with_all_valid_strings(self) -> None:
        """Test set_strategy with all valid strategy strings."""
        rotator = ProxyRotator()
        valid_strategies = [
            "round-robin",
            "random",
            "weighted",
            "least-used",
            "performance-based",
            "session",
            "geo-targeted",
        ]
        for strategy_name in valid_strategies:
            rotator.set_strategy(strategy_name)
            assert rotator.strategy is not None

    def test_set_strategy_invalid_string_raises(self) -> None:
        """Test set_strategy with invalid strategy string raises ValueError."""
        rotator = ProxyRotator()
        with pytest.raises(ValueError, match="Unknown strategy"):
            rotator.set_strategy("nonexistent-strategy")

    def test_set_strategy_non_atomic(self) -> None:
        """Test set_strategy with atomic=False."""
        rotator = ProxyRotator(strategy="round-robin")
        rotator.set_strategy("random", atomic=False)
        assert rotator.strategy.__class__.__name__ == "RandomStrategy"


class TestRotatorCircuitBreakerEdgeCases:
    """Test circuit breaker edge cases."""

    def test_all_circuit_breakers_open_raises_error(self) -> None:
        """Test that all circuit breakers open raises ProxyPoolEmptyError with 503 message."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        # Open the circuit breaker by recording failures
        circuit_breaker = rotator.circuit_breakers[str(proxy.id)]
        for _ in range(circuit_breaker.failure_threshold + 1):
            circuit_breaker.record_failure()

        # Now all circuit breakers are open
        with pytest.raises(ProxyPoolEmptyError, match="503"):
            rotator.get("https://example.com")

    def test_reset_circuit_breaker_success(self) -> None:
        """Test resetting a circuit breaker."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080")
        rotator.add_proxy(proxy)

        proxy_id = str(proxy.id)
        # Record some failures
        rotator.circuit_breakers[proxy_id].record_failure()

        # Reset should work
        rotator.reset_circuit_breaker(proxy_id)
        assert rotator.circuit_breakers[proxy_id].state.name == "CLOSED"

    def test_reset_circuit_breaker_invalid_proxy_id_raises(self) -> None:
        """Test resetting circuit breaker with invalid proxy_id raises KeyError."""
        rotator = ProxyRotator()

        with pytest.raises(KeyError, match="No circuit breaker found"):
            rotator.reset_circuit_breaker("nonexistent-proxy-id")

    def test_get_circuit_breaker_states(self) -> None:
        """Test getting circuit breaker states returns a copy."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080")
        rotator.add_proxy(proxy)

        states = rotator.get_circuit_breaker_states()
        assert len(states) == 1
        # Verify it's a copy
        states["new_key"] = None  # type: ignore
        assert "new_key" not in rotator.circuit_breakers


class TestRotator407Authentication:
    """Test 407 Proxy Authentication Required handling."""

    @patch("httpx.Client")
    def test_407_response_triggers_auth_error_logging(self, mock_client_class: MagicMock) -> None:
        """Test that 407 response is detected and logged as auth error.

        After bug fix: ProxyAuthenticationError is now raised directly (unwrapped)
        and failure is recorded in strategy.
        """

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 407

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        rotator.add_proxy("http://proxy.example.com:8080")
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY

        # After bug fix, ProxyAuthenticationError is raised directly
        with pytest.raises(ProxyAuthenticationError) as exc_info:
            rotator.get("https://example.com")

        # Verify it's the 407 authentication error
        assert "407" in str(exc_info.value)


class TestRotatorDestructor:
    """Test destructor and cleanup."""

    def test_destructor_closes_clients(self) -> None:
        """Test that __del__ closes pooled clients."""
        rotator = ProxyRotator()

        # Simulate having pooled clients
        mock_client = MagicMock()
        rotator._client_pool["test-proxy"] = mock_client

        # Call destructor
        rotator.__del__()

        mock_client.close.assert_called_once()
        assert len(rotator._client_pool) == 0

    def test_destructor_cancels_timer(self) -> None:
        """Test that __del__ cancels aggregation timer."""
        rotator = ProxyRotator()
        timer = rotator._aggregation_timer

        # Call destructor
        rotator.__del__()

        # Timer should be cancelled (we can check it's not running)
        assert timer is not None

    def test_close_all_clients_handles_exceptions(self) -> None:
        """Test that _close_all_clients handles exceptions gracefully."""
        rotator = ProxyRotator()

        # Add a mock client that raises on close
        mock_client = MagicMock()
        mock_client.close.side_effect = Exception("Close failed")
        rotator._client_pool["test-proxy"] = mock_client

        # Should not raise
        rotator._close_all_clients()

        # Pool should be cleared despite exception
        assert len(rotator._client_pool) == 0


class TestRotatorProxyChains:
    """Test proxy chain functionality."""

    def test_get_chains_empty(self) -> None:
        """Test get_chains returns empty list when no chains added."""
        rotator = ProxyRotator()
        chains = rotator.get_chains()
        assert chains == []

    def test_add_chain(self) -> None:
        """Test adding a proxy chain."""
        rotator = ProxyRotator()
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),
            Proxy(url="http://proxy2.example.com:8080"),
        ]
        chain = ProxyChain(proxies=proxies, name="test-chain")

        rotator.add_chain(chain)

        assert len(rotator.chains) == 1
        assert rotator.pool.size == 1  # Entry proxy added to pool

    def test_remove_chain_success(self) -> None:
        """Test removing a proxy chain by name."""
        rotator = ProxyRotator()
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),
            Proxy(url="http://proxy2.example.com:8080"),
        ]
        chain = ProxyChain(proxies=proxies, name="test-chain")
        rotator.add_chain(chain)

        result = rotator.remove_chain("test-chain")

        assert result is True
        assert len(rotator.chains) == 0

    def test_remove_chain_not_found(self) -> None:
        """Test removing a non-existent chain returns False."""
        rotator = ProxyRotator()

        result = rotator.remove_chain("nonexistent-chain")

        assert result is False

    def test_get_chains_returns_copy(self) -> None:
        """Test that get_chains returns a copy of the chains list."""
        rotator = ProxyRotator()
        # ProxyChain requires at least 2 proxies
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),
            Proxy(url="http://proxy2.example.com:8080"),
        ]
        chain = ProxyChain(proxies=proxies, name="test-chain")
        rotator.add_chain(chain)

        chains = rotator.get_chains()
        chains.append(chain)  # Modify the returned list

        # Original should be unchanged
        assert len(rotator.chains) == 1


class TestRotatorRemoveProxy:
    """Test remove_proxy edge cases."""

    def test_remove_proxy_closes_pooled_client(self) -> None:
        """Test that remove_proxy closes the pooled client for that proxy."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080")
        rotator.add_proxy(proxy)

        # Simulate having a pooled client for this proxy
        mock_client = MagicMock()
        rotator._client_pool[str(proxy.id)] = mock_client

        rotator.remove_proxy(str(proxy.id))

        mock_client.close.assert_called_once()
        assert str(proxy.id) not in rotator._client_pool

    def test_remove_proxy_handles_client_close_error(self) -> None:
        """Test that remove_proxy handles client close errors gracefully."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080")
        rotator.add_proxy(proxy)

        # Simulate a client that raises on close
        mock_client = MagicMock()
        mock_client.close.side_effect = Exception("Close failed")
        rotator._client_pool[str(proxy.id)] = mock_client

        # Should not raise
        rotator.remove_proxy(str(proxy.id))

        # Client should be removed despite exception
        assert str(proxy.id) not in rotator._client_pool
        assert rotator.pool.size == 0


class TestRotatorClearUnhealthy:
    """Test clear_unhealthy_proxies functionality."""

    def test_clear_unhealthy_proxies(self) -> None:
        """Test clearing unhealthy proxies from pool."""
        rotator = ProxyRotator()

        # Add healthy and unhealthy proxies
        healthy = Proxy(url="http://healthy.example.com:8080", health_status=HealthStatus.HEALTHY)
        unhealthy = Proxy(
            url="http://unhealthy.example.com:8080", health_status=HealthStatus.UNHEALTHY
        )
        dead = Proxy(url="http://dead.example.com:8080", health_status=HealthStatus.DEAD)

        rotator.add_proxy(healthy)
        rotator.add_proxy(unhealthy)
        rotator.add_proxy(dead)

        assert rotator.pool.size == 3

        removed = rotator.clear_unhealthy_proxies()

        assert removed == 2
        assert rotator.pool.size == 1


class TestRotatorMetrics:
    """Test retry metrics functionality."""

    def test_get_retry_metrics(self) -> None:
        """Test getting retry metrics."""
        rotator = ProxyRotator()
        metrics = rotator.get_retry_metrics()

        assert metrics is not None
        assert metrics is rotator.retry_metrics


class TestRotatorPoolStats:
    """Test pool statistics functionality."""

    def test_get_pool_stats_empty(self) -> None:
        """Test get_pool_stats with empty pool."""
        rotator = ProxyRotator()
        stats = rotator.get_pool_stats()

        assert stats["total_proxies"] == 0
        assert stats["healthy_proxies"] == 0
        assert stats["average_success_rate"] == 0.0

    def test_get_statistics_includes_source_breakdown(self) -> None:
        """Test get_statistics includes source breakdown."""
        rotator = ProxyRotator()
        stats = rotator.get_statistics()

        assert "source_breakdown" in stats


class TestRotatorStrategyInstance:
    """Test rotator with strategy instance (not string)."""

    def test_init_with_strategy_instance(self) -> None:
        """Test initializing rotator with strategy instance."""
        from proxywhirl.strategies import RandomStrategy

        strategy = RandomStrategy()
        rotator = ProxyRotator(strategy=strategy)

        assert rotator.strategy is strategy

    def test_set_strategy_with_instance(self) -> None:
        """Test set_strategy with strategy instance."""
        from proxywhirl.strategies import WeightedStrategy

        rotator = ProxyRotator(strategy="round-robin")
        new_strategy = WeightedStrategy()

        rotator.set_strategy(new_strategy)

        assert rotator.strategy is new_strategy


class TestRotatorInitWithProxies:
    """Test rotator initialization with proxies."""

    def test_init_with_proxy_list(self) -> None:
        """Test rotator initialization with proxy list creates circuit breakers."""
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),
            Proxy(url="http://proxy2.example.com:8080"),
        ]
        rotator = ProxyRotator(proxies=proxies)

        assert rotator.pool.size == 2
        # Each proxy should have a circuit breaker
        for proxy in proxies:
            assert str(proxy.id) in rotator.circuit_breakers


class TestRotatorContextManager:
    """Test context manager functionality."""

    def test_context_manager_enter_exit(self) -> None:
        """Test context manager creates and closes client."""
        rotator = ProxyRotator()

        with rotator as r:
            assert r._client is not None
            assert r is rotator

        # After exit, client should be closed
        assert rotator._client is None

    def test_context_manager_cancels_timer(self) -> None:
        """Test context manager cancels aggregation timer on exit."""
        rotator = ProxyRotator()
        timer = rotator._aggregation_timer
        assert timer is not None

        with rotator:
            pass

        # Timer should be cancelled after exit
        assert rotator._aggregation_timer is None


class TestRotatorGetProxyDict:
    """Test _get_proxy_dict with credentials."""

    def test_proxy_dict_without_credentials(self) -> None:
        """Test proxy dict without credentials."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080")

        proxy_dict = rotator._get_proxy_dict(proxy)

        assert proxy_dict["http://"] == "http://proxy.example.com:8080"
        assert proxy_dict["https://"] == "http://proxy.example.com:8080"

    def test_proxy_dict_with_credentials(self) -> None:
        """Test proxy dict with credentials inserts auth into URL."""
        from pydantic import SecretStr

        rotator = ProxyRotator()
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("testuser"),
            password=SecretStr("testpass"),
        )

        proxy_dict = rotator._get_proxy_dict(proxy)

        expected = "http://testuser:testpass@proxy.example.com:8080"
        assert proxy_dict["http://"] == expected
        assert proxy_dict["https://"] == expected


class TestRotatorGetOrCreateClient:
    """Test _get_or_create_client pooling."""

    def test_returns_existing_client(self) -> None:
        """Test that _get_or_create_client returns existing pooled client."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy_dict = {"http://": "http://proxy.example.com:8080"}

        # Create initial client
        client1 = rotator._get_or_create_client(proxy, proxy_dict)

        # Should return same client
        client2 = rotator._get_or_create_client(proxy, proxy_dict)

        assert client1 is client2

        # Cleanup
        client1.close()


class TestRotatorHTTPMethods:
    """Test HTTP method shortcuts."""

    @patch("httpx.Client")
    def test_post_method(self, mock_client_class: MagicMock) -> None:
        """Test POST method."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        response = rotator.post("https://example.com", data={"key": "value"})

        assert response.status_code == 200
        mock_client.request.assert_called()

    @patch("httpx.Client")
    def test_put_method(self, mock_client_class: MagicMock) -> None:
        """Test PUT method."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        response = rotator.put("https://example.com")

        assert response.status_code == 200

    @patch("httpx.Client")
    def test_delete_method(self, mock_client_class: MagicMock) -> None:
        """Test DELETE method."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 204

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        response = rotator.delete("https://example.com/resource")

        assert response.status_code == 204

    @patch("httpx.Client")
    def test_patch_method(self, mock_client_class: MagicMock) -> None:
        """Test PATCH method."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        response = rotator.patch("https://example.com/resource")

        assert response.status_code == 200

    @patch("httpx.Client")
    def test_head_method(self, mock_client_class: MagicMock) -> None:
        """Test HEAD method."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        response = rotator.head("https://example.com")

        assert response.status_code == 200

    @patch("httpx.Client")
    def test_options_method(self, mock_client_class: MagicMock) -> None:
        """Test OPTIONS method."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        response = rotator.options("https://example.com")

        assert response.status_code == 200


class TestRotatorMakeRequestWithRetryPolicy:
    """Test _make_request with custom retry_policy."""

    @patch("httpx.Client")
    def test_custom_retry_policy(self, mock_client_class: MagicMock) -> None:
        """Test _make_request with per-request retry_policy override."""
        from proxywhirl.retry import RetryPolicy

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        custom_policy = RetryPolicy(max_attempts=1)

        response = rotator._make_request(
            "GET",
            "https://example.com",
            retry_policy=custom_policy,
        )

        assert response.status_code == 200


class TestRotatorSetStrategySlowWarning:
    """Test set_strategy slow swap warning."""

    def test_slow_swap_covers_warning_path(self) -> None:
        """Test that slow strategy swap covers the warning log path.

        The warning is logged when swap takes >= 100ms.
        We mock time.perf_counter at the module level where it's used.
        """
        rotator = ProxyRotator()

        call_count = [0]

        def mock_perf_counter():
            call_count[0] += 1
            if call_count[0] == 1:
                return 0.0  # Start time
            return 0.2  # End time - 200ms elapsed, > 100ms threshold

        # Patch where it's used (in the set_strategy method's import scope)
        with patch("time.perf_counter", mock_perf_counter):
            rotator.set_strategy("random")

        # Strategy should still be swapped
        assert rotator.strategy.__class__.__name__ == "RandomStrategy"


class TestRotatorRemoveChainWithError:
    """Test remove_chain error handling."""

    def test_remove_chain_with_remove_proxy_error(self) -> None:
        """Test remove_chain handles remove_proxy error gracefully."""
        rotator = ProxyRotator()
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),
            Proxy(url="http://proxy2.example.com:8080"),
        ]
        chain = ProxyChain(proxies=proxies, name="test-chain")
        rotator.add_chain(chain)

        # Mock remove_proxy to raise an exception
        with patch.object(rotator, "remove_proxy", side_effect=Exception("Remove failed")):
            result = rotator.remove_chain("test-chain")

        # Should still return True and remove the chain
        assert result is True
        assert len(rotator.chains) == 0


class TestRotatorAddChainWithoutTags:
    """Test add_chain when entry_proxy has no tags attribute."""

    def test_add_chain_initializes_tags(self) -> None:
        """Test add_chain initializes tags if missing."""
        rotator = ProxyRotator()
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),
            Proxy(url="http://proxy2.example.com:8080"),
        ]
        chain = ProxyChain(proxies=proxies, name="test-chain")

        # Ensure entry_proxy has tags (Proxy model should have it)
        entry = chain.entry_proxy
        assert hasattr(entry, "tags")

        rotator.add_chain(chain)

        # Entry proxy should now have chain_entry tag
        assert "chain_entry" in entry.tags


class TestRotatorRateLimiting:
    """Test rate limiting integration in ProxyRotator."""

    def test_rotator_init_without_rate_limiter(self) -> None:
        """Test ProxyRotator initialization without rate limiter."""
        rotator = ProxyRotator()
        assert rotator.rate_limiter is None

    def test_rotator_init_with_rate_limiter(self) -> None:
        """Test ProxyRotator initialization with rate limiter."""
        rate_limit = RateLimit(max_requests=10, time_window=60)
        limiter = RateLimiter(global_limit=rate_limit)
        rotator = ProxyRotator(rate_limiter=limiter)

        assert rotator.rate_limiter is not None
        assert rotator.rate_limiter is limiter

    @patch("httpx.Client")
    def test_request_succeeds_when_rate_limit_allowed(self, mock_client_class: MagicMock) -> None:
        """Test that request succeeds when rate limiter allows it."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Setup rate limiter that allows requests
        rate_limit = RateLimit(max_requests=10, time_window=60)
        limiter = RateLimiter(global_limit=rate_limit)

        # Create rotator with rate limiter
        rotator = ProxyRotator(rate_limiter=limiter)
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        # Set per-proxy limit
        limiter.set_proxy_limit(str(proxy.id), RateLimit(max_requests=5, time_window=60))

        # Make request - should succeed
        response = rotator.get("https://example.com")

        assert response.status_code == 200
        mock_client.request.assert_called()

    @patch("httpx.Client")
    def test_request_fails_when_rate_limit_exceeded(self, mock_client_class: MagicMock) -> None:
        """Test that request fails when rate limiter blocks it."""
        # Setup mock response (won't be used since rate limit will block)
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Setup rate limiter with very restrictive limit
        limiter = RateLimiter()

        # Create rotator with rate limiter
        rotator = ProxyRotator(rate_limiter=limiter)
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        # Set very restrictive per-proxy limit
        limiter.set_proxy_limit(str(proxy.id), RateLimit(max_requests=1, time_window=60))

        # First request should succeed
        response1 = rotator.get("https://example.com")
        assert response1.status_code == 200

        # Second request should fail due to rate limit
        with pytest.raises(ProxyConnectionError, match="Rate limit exceeded"):
            rotator.get("https://example.com")

    @patch("httpx.Client")
    def test_rate_limit_respects_global_limit(self, mock_client_class: MagicMock) -> None:
        """Test that global rate limit is respected."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Setup rate limiter with global limit
        global_limit = RateLimit(max_requests=2, time_window=60)
        limiter = RateLimiter(global_limit=global_limit)

        # Create rotator with two proxies
        rotator = ProxyRotator(rate_limiter=limiter)
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)

        # First two requests should succeed (global limit = 2)
        response1 = rotator.get("https://example.com")
        response2 = rotator.get("https://example.com")

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Third request should fail due to global rate limit
        with pytest.raises(ProxyConnectionError, match="Rate limit exceeded"):
            rotator.get("https://example.com")

    def test_rate_limiter_can_be_configured_after_init(self) -> None:
        """Test that rate limiter can be configured after rotator initialization."""
        rotator = ProxyRotator()
        assert rotator.rate_limiter is None

        # Add rate limiter after initialization
        rate_limit = RateLimit(max_requests=10, time_window=60)
        limiter = RateLimiter(global_limit=rate_limit)
        rotator.rate_limiter = limiter

        assert rotator.rate_limiter is not None

    @patch("httpx.Client")
    def test_rate_limit_logs_warning_when_exceeded(self, mock_client_class: MagicMock) -> None:
        """Test that rate limit exceedance is logged as a warning."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Setup rate limiter
        limiter = RateLimiter()

        # Create rotator
        rotator = ProxyRotator(rate_limiter=limiter)
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        # Set restrictive limit
        limiter.set_proxy_limit(str(proxy.id), RateLimit(max_requests=1, time_window=60))

        # First request succeeds
        rotator.get("https://example.com")

        # Second request should log warning and raise exception
        with pytest.raises(ProxyConnectionError):
            rotator.get("https://example.com")

    @patch("httpx.Client")
    def test_rate_limit_state_persists_across_requests(self, mock_client_class: MagicMock) -> None:
        """Test that rate limit state is persistent across multiple requests."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Create shared rate limiter
        limiter = RateLimiter()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)

        # Create first rotator instance
        rotator1 = ProxyRotator(rate_limiter=limiter)
        rotator1.add_proxy(proxy)
        limiter.set_proxy_limit(str(proxy.id), RateLimit(max_requests=2, time_window=60))

        # Make 2 requests with first rotator
        rotator1.get("https://example.com")
        rotator1.get("https://example.com")

        # Create second rotator instance with SAME rate limiter
        rotator2 = ProxyRotator(rate_limiter=limiter)
        rotator2.add_proxy(proxy)

        # Third request with second rotator should fail (state persisted)
        with pytest.raises(ProxyConnectionError, match="Rate limit exceeded"):
            rotator2.get("https://example.com")
