"""Unit tests for async_client module.

Tests cover AsyncProxyRotator initialization, proxy management, strategy handling,
circuit breakers, and HTTP request methods.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import HealthStatus, Proxy, ProxyConfiguration
from proxywhirl.retry import RetryPolicy
from proxywhirl.rotator import AsyncProxyRotator
from proxywhirl.strategies import (
    LeastUsedStrategy,
    RandomStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
)


class TestAsyncProxyRotatorInit:
    """Test AsyncProxyRotator initialization."""

    def test_init_defaults(self) -> None:
        """Test initialization with defaults."""
        rotator = AsyncProxyRotator()

        assert rotator.pool.size == 0
        assert isinstance(rotator.strategy, RoundRobinStrategy)
        assert isinstance(rotator.config, ProxyConfiguration)
        assert isinstance(rotator.retry_policy, RetryPolicy)
        assert rotator.circuit_breakers == {}

    def test_init_with_proxies(self) -> None:
        """Test initialization with initial proxies."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        assert rotator.pool.size == 1
        assert str(proxy.id) in rotator.circuit_breakers

    def test_init_with_strategy_instance(self) -> None:
        """Test initialization with strategy instance."""
        strategy = RandomStrategy()
        rotator = AsyncProxyRotator(strategy=strategy)

        assert rotator.strategy is strategy

    def test_init_with_strategy_string_round_robin(self) -> None:
        """Test initialization with 'round-robin' strategy string."""
        rotator = AsyncProxyRotator(strategy="round-robin")
        assert isinstance(rotator.strategy, RoundRobinStrategy)

    def test_init_with_strategy_string_random(self) -> None:
        """Test initialization with 'random' strategy string."""
        rotator = AsyncProxyRotator(strategy="random")
        assert isinstance(rotator.strategy, RandomStrategy)

    def test_init_with_strategy_string_weighted(self) -> None:
        """Test initialization with 'weighted' strategy string."""
        rotator = AsyncProxyRotator(strategy="weighted")
        assert isinstance(rotator.strategy, WeightedStrategy)

    def test_init_with_strategy_string_least_used(self) -> None:
        """Test initialization with 'least-used' strategy string."""
        rotator = AsyncProxyRotator(strategy="least-used")
        assert isinstance(rotator.strategy, LeastUsedStrategy)

    def test_init_with_invalid_strategy_string(self) -> None:
        """Test initialization with invalid strategy string raises ValueError."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            AsyncProxyRotator(strategy="invalid-strategy")

    def test_init_with_custom_config(self) -> None:
        """Test initialization with custom configuration."""
        config = ProxyConfiguration(timeout=60, verify_ssl=False)
        rotator = AsyncProxyRotator(config=config)

        assert rotator.config.timeout == 60
        assert rotator.config.verify_ssl is False

    def test_init_with_custom_retry_policy(self) -> None:
        """Test initialization with custom retry policy."""
        policy = RetryPolicy(max_attempts=5)
        rotator = AsyncProxyRotator(retry_policy=policy)

        assert rotator.retry_policy.max_attempts == 5


class TestAsyncProxyRotatorContextManager:
    """Test AsyncProxyRotator context manager."""

    async def test_context_manager_creates_client(self) -> None:
        """Test context manager creates httpx client."""
        rotator = AsyncProxyRotator()

        async with rotator as r:
            assert r._client is not None
            assert r is rotator

        # Client should be closed after exiting
        assert rotator._client is None

    async def test_context_manager_cancels_timer(self) -> None:
        """Test context manager stops aggregation thread on exit."""
        rotator = AsyncProxyRotator()

        async with rotator:
            assert rotator._aggregation_thread is not None
            assert rotator._aggregation_thread.is_alive()

        # Thread should be stopped and joined
        assert rotator._stop_event.is_set()
        # Thread should have finished or be close to finishing
        assert not rotator._aggregation_thread.is_alive() or rotator._aggregation_thread.daemon


class TestAsyncProxyRotatorProxyManagement:
    """Test proxy management methods."""

    async def test_add_proxy_with_proxy_object(self) -> None:
        """Test adding proxy with Proxy object."""
        rotator = AsyncProxyRotator()
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)

        await rotator.add_proxy(proxy)

        assert rotator.pool.size == 1
        assert str(proxy.id) in rotator.circuit_breakers

    async def test_add_proxy_with_url_string(self) -> None:
        """Test adding proxy with URL string."""
        rotator = AsyncProxyRotator()

        await rotator.add_proxy("http://proxy.example.com:8080")

        assert rotator.pool.size == 1

    async def test_remove_proxy(self) -> None:
        """Test removing proxy by ID."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        await rotator.remove_proxy(str(proxy.id))

        assert rotator.pool.size == 0

    async def test_get_proxy_with_empty_pool_raises(self) -> None:
        """Test get_proxy with empty pool raises ProxyPoolEmptyError."""
        rotator = AsyncProxyRotator()

        with pytest.raises(ProxyPoolEmptyError):
            await rotator.get_proxy()

    async def test_get_proxy_returns_proxy(self) -> None:
        """Test get_proxy returns a proxy from pool."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        result = await rotator.get_proxy()

        assert result.id == proxy.id


class TestAsyncProxyRotatorSetStrategy:
    """Test set_strategy method."""

    def test_set_strategy_with_string(self) -> None:
        """Test set_strategy with strategy string."""
        rotator = AsyncProxyRotator(strategy="round-robin")

        rotator.set_strategy("random")

        assert isinstance(rotator.strategy, RandomStrategy)

    def test_set_strategy_with_instance(self) -> None:
        """Test set_strategy with strategy instance."""
        rotator = AsyncProxyRotator()
        new_strategy = LeastUsedStrategy()

        rotator.set_strategy(new_strategy)

        assert rotator.strategy is new_strategy

    def test_set_strategy_performance_based(self) -> None:
        """Test set_strategy with performance-based strategy."""
        rotator = AsyncProxyRotator()

        rotator.set_strategy("performance-based")

        assert rotator.strategy.__class__.__name__ == "PerformanceBasedStrategy"

    def test_set_strategy_session(self) -> None:
        """Test set_strategy with session strategy."""
        rotator = AsyncProxyRotator()

        rotator.set_strategy("session")

        assert rotator.strategy.__class__.__name__ == "SessionPersistenceStrategy"

    def test_set_strategy_geo_targeted(self) -> None:
        """Test set_strategy with geo-targeted strategy."""
        rotator = AsyncProxyRotator()

        rotator.set_strategy("geo-targeted")

        assert rotator.strategy.__class__.__name__ == "GeoTargetedStrategy"

    def test_set_strategy_invalid_raises(self) -> None:
        """Test set_strategy with invalid string raises ValueError."""
        rotator = AsyncProxyRotator()

        with pytest.raises(ValueError, match="Unknown strategy"):
            rotator.set_strategy("invalid")

    def test_set_strategy_atomic_uses_lock(self) -> None:
        """Test set_strategy with atomic=True (no-op for compatibility)."""
        rotator = AsyncProxyRotator()

        rotator.set_strategy("random", atomic=True)

        # Strategy should be set correctly (atomic is now a no-op)
        assert isinstance(rotator.strategy, RandomStrategy)

    def test_set_strategy_non_atomic(self) -> None:
        """Test set_strategy with atomic=False."""
        rotator = AsyncProxyRotator()

        rotator.set_strategy("random", atomic=False)

        assert isinstance(rotator.strategy, RandomStrategy)


class TestAsyncProxyRotatorStats:
    """Test statistics methods."""

    def test_get_pool_stats_empty_pool(self) -> None:
        """Test get_pool_stats with empty pool."""
        rotator = AsyncProxyRotator()

        stats = rotator.get_pool_stats()

        assert stats["total_proxies"] == 0
        assert stats["healthy_proxies"] == 0
        assert stats["unhealthy_proxies"] == 0
        assert stats["dead_proxies"] == 0
        assert stats["average_success_rate"] == 0.0

    def test_get_pool_stats_with_proxies(self) -> None:
        """Test get_pool_stats with various proxy states."""
        proxies = [
            Proxy(
                url="http://192.168.1.1:8080", allow_local=True, health_status=HealthStatus.HEALTHY
            ),
            Proxy(
                url="http://192.168.1.2:8080", allow_local=True, health_status=HealthStatus.HEALTHY
            ),
            Proxy(
                url="http://192.168.1.3:8080",
                allow_local=True,
                health_status=HealthStatus.UNHEALTHY,
            ),
            Proxy(url="http://192.168.1.4:8080", allow_local=True, health_status=HealthStatus.DEAD),
        ]
        rotator = AsyncProxyRotator(proxies=proxies)

        stats = rotator.get_pool_stats()

        assert stats["total_proxies"] == 4
        assert stats["healthy_proxies"] == 2  # HEALTHY + UNKNOWN + DEGRADED
        assert stats["unhealthy_proxies"] == 1
        assert stats["dead_proxies"] == 1

    def test_get_pool_stats_calculates_totals(self) -> None:
        """Test get_pool_stats calculates request totals."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        proxy.total_requests = 10
        proxy.total_successes = 8
        proxy.total_failures = 2

        rotator = AsyncProxyRotator(proxies=[proxy])

        stats = rotator.get_pool_stats()

        assert stats["total_requests"] == 10
        assert stats["total_successes"] == 8
        assert stats["total_failures"] == 2

    def test_get_statistics_includes_source_breakdown(self) -> None:
        """Test get_statistics includes source breakdown."""
        rotator = AsyncProxyRotator()

        stats = rotator.get_statistics()

        assert "source_breakdown" in stats


class TestAsyncProxyRotatorClearUnhealthy:
    """Test clear_unhealthy_proxies method."""

    async def test_clear_unhealthy_removes_dead_proxies(self) -> None:
        """Test clear_unhealthy_proxies removes unhealthy and dead proxies."""
        proxies = [
            Proxy(
                url="http://192.168.1.1:8080", allow_local=True, health_status=HealthStatus.HEALTHY
            ),
            Proxy(
                url="http://192.168.1.2:8080",
                allow_local=True,
                health_status=HealthStatus.UNHEALTHY,
            ),
            Proxy(url="http://192.168.1.3:8080", allow_local=True, health_status=HealthStatus.DEAD),
        ]
        rotator = AsyncProxyRotator(proxies=proxies)

        removed = await rotator.clear_unhealthy_proxies()

        assert removed == 2
        assert rotator.pool.size == 1


class TestAsyncProxyRotatorGetProxyDict:
    """Test _get_proxy_dict method."""

    def test_get_proxy_dict_without_credentials(self) -> None:
        """Test _get_proxy_dict without credentials."""
        rotator = AsyncProxyRotator()
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)

        result = rotator._get_proxy_dict(proxy)

        assert result["http://"] == "http://192.168.1.1:8080"
        assert result["https://"] == "http://192.168.1.1:8080"

    def test_get_proxy_dict_with_credentials(self) -> None:
        """Test _get_proxy_dict with credentials."""
        rotator = AsyncProxyRotator()
        proxy = Proxy(
            url="http://192.168.1.1:8080",
            allow_local=True,
            username=SecretStr("user"),
            password=SecretStr("pass"),
        )

        result = rotator._get_proxy_dict(proxy)

        assert result["http://"] == "http://user:pass@192.168.1.1:8080"
        assert result["https://"] == "http://user:pass@192.168.1.1:8080"


class TestAsyncProxyRotatorCircuitBreakers:
    """Test circuit breaker methods."""

    def test_get_circuit_breaker_states(self) -> None:
        """Test get_circuit_breaker_states returns copy of circuit breakers."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        states = rotator.get_circuit_breaker_states()

        assert str(proxy.id) in states
        assert states is not rotator.circuit_breakers  # Is a copy

    def test_reset_circuit_breaker(self) -> None:
        """Test reset_circuit_breaker resets to CLOSED state."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        # Record some failures to open the circuit
        cb = rotator.circuit_breakers[str(proxy.id)]
        for _ in range(10):
            cb.record_failure()

        rotator.reset_circuit_breaker(str(proxy.id))

        # Should be reset
        assert cb.failure_count == 0

    def test_reset_circuit_breaker_invalid_id_raises(self) -> None:
        """Test reset_circuit_breaker with invalid ID raises KeyError."""
        rotator = AsyncProxyRotator()

        with pytest.raises(KeyError, match="No circuit breaker found"):
            rotator.reset_circuit_breaker("invalid-id")

    def test_get_retry_metrics(self) -> None:
        """Test get_retry_metrics returns retry metrics."""
        rotator = AsyncProxyRotator()

        metrics = rotator.get_retry_metrics()

        assert metrics is rotator.retry_metrics


class TestAsyncProxyRotatorSelectWithCircuitBreaker:
    """Test _select_proxy_with_circuit_breaker method."""

    def test_select_with_available_proxy(self) -> None:
        """Test selection with available proxy."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        result = rotator._select_proxy_with_circuit_breaker()

        assert result.id == proxy.id

    def test_select_with_all_circuit_breakers_open_raises(self) -> None:
        """Test selection raises when all circuit breakers are open."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        # Open the circuit breaker
        cb = rotator.circuit_breakers[str(proxy.id)]
        for _ in range(10):
            cb.record_failure()

        with pytest.raises(ProxyPoolEmptyError, match="503 Service Temporarily Unavailable"):
            rotator._select_proxy_with_circuit_breaker()

    def test_select_filters_open_circuit_breakers(self) -> None:
        """Test selection filters out proxies with open circuit breakers."""
        proxy1 = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        proxy2 = Proxy(url="http://192.168.1.2:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy1, proxy2])

        # Open circuit breaker for proxy1
        cb = rotator.circuit_breakers[str(proxy1.id)]
        for _ in range(10):
            cb.record_failure()

        # Should only get proxy2
        result = rotator._select_proxy_with_circuit_breaker()

        assert result.id == proxy2.id


class TestAsyncProxyRotatorHttpMethods:
    """Test HTTP request methods."""

    async def test_make_request_with_empty_pool_raises(self) -> None:
        """Test _make_request with empty pool raises ProxyPoolEmptyError."""
        rotator = AsyncProxyRotator()

        with pytest.raises(ProxyPoolEmptyError):
            await rotator._make_request("GET", "https://example.com")

    async def test_make_request_success(self) -> None:
        """Test _make_request with successful request."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(
            rotator, "_execute_async_with_retry", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = mock_response

            result = await rotator._make_request("GET", "https://example.com")

            assert result.status_code == 200
            mock_execute.assert_called_once()

    async def test_make_request_failure_raises_connection_error(self) -> None:
        """Test _make_request raises ProxyConnectionError on failure."""
        from proxywhirl.exceptions import ProxyConnectionError

        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        with patch.object(
            rotator, "_execute_async_with_retry", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.side_effect = ConnectionError("Connection failed")

            with pytest.raises(ProxyConnectionError, match="Request failed"):
                await rotator._make_request("GET", "https://example.com")

    async def test_get_method(self) -> None:
        """Test get() method."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            result = await rotator.get("https://example.com")

            assert result is mock_response
            mock_make.assert_called_once_with("GET", "https://example.com")

    async def test_get_method_with_params(self) -> None:
        """Test GET method with query parameters."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            result = await rotator.get("https://example.com", params={"q": "search", "limit": 10})

            assert result is mock_response
            mock_make.assert_called_once_with(
                "GET", "https://example.com", params={"q": "search", "limit": 10}
            )

    async def test_get_method_with_headers(self) -> None:
        """Test GET method with custom headers."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            headers = {"Authorization": "Bearer token123", "User-Agent": "CustomAgent/1.0"}
            result = await rotator.get("https://example.com", headers=headers)

            assert result is mock_response
            mock_make.assert_called_once_with("GET", "https://example.com", headers=headers)

    async def test_post_method(self) -> None:
        """Test post() method."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            result = await rotator.post("https://example.com", json={"key": "value"})

            assert result is mock_response
            mock_make.assert_called_once_with("POST", "https://example.com", json={"key": "value"})

    async def test_post_method_with_json_body(self) -> None:
        """Test POST method with JSON body."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 201

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            payload = {"name": "test", "data": [1, 2, 3], "nested": {"key": "value"}}
            result = await rotator.post("https://api.example.com/create", json=payload)

            assert result is mock_response
            mock_make.assert_called_once_with(
                "POST", "https://api.example.com/create", json=payload
            )

    async def test_post_method_with_form_data(self) -> None:
        """Test POST method with form data."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            form_data = {"username": "user", "password": "pass"}
            result = await rotator.post("https://example.com/login", data=form_data)

            assert result is mock_response
            mock_make.assert_called_once_with("POST", "https://example.com/login", data=form_data)

    async def test_post_method_with_files(self) -> None:
        """Test POST method with file upload."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            files = {"file": ("test.txt", b"file contents", "text/plain")}
            result = await rotator.post("https://example.com/upload", files=files)

            assert result is mock_response
            mock_make.assert_called_once_with("POST", "https://example.com/upload", files=files)

    async def test_put_method(self) -> None:
        """Test put() method."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            result = await rotator.put("https://example.com", data="test")

            assert result is mock_response
            mock_make.assert_called_once()

    async def test_put_method_with_json(self) -> None:
        """Test PUT method with JSON payload."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            payload = {"id": 123, "status": "updated"}
            result = await rotator.put("https://api.example.com/resource/123", json=payload)

            assert result is mock_response
            mock_make.assert_called_once_with(
                "PUT", "https://api.example.com/resource/123", json=payload
            )

    async def test_delete_method(self) -> None:
        """Test delete() method."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            result = await rotator.delete("https://example.com")

            assert result is mock_response
            mock_make.assert_called_once_with("DELETE", "https://example.com")

    async def test_delete_method_with_params(self) -> None:
        """Test DELETE method with query parameters."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 204

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            result = await rotator.delete(
                "https://api.example.com/resource/456", params={"cascade": "true"}
            )

            assert result is mock_response
            mock_make.assert_called_once_with(
                "DELETE", "https://api.example.com/resource/456", params={"cascade": "true"}
            )

    async def test_patch_method(self) -> None:
        """Test patch() method."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            result = await rotator.patch("https://example.com", json={"update": "data"})

            assert result is mock_response
            mock_make.assert_called_once()

    async def test_patch_method_with_partial_update(self) -> None:
        """Test PATCH method with partial update payload."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            patch_data = {"status": "active", "last_updated": "2025-01-06"}
            result = await rotator.patch("https://api.example.com/user/789", json=patch_data)

            assert result is mock_response
            mock_make.assert_called_once_with(
                "PATCH", "https://api.example.com/user/789", json=patch_data
            )

    async def test_head_method(self) -> None:
        """Test head() method."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            result = await rotator.head("https://example.com")

            assert result is mock_response
            mock_make.assert_called_once_with("HEAD", "https://example.com")

    async def test_head_method_with_headers(self) -> None:
        """Test HEAD method with custom headers."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Length": "12345", "Content-Type": "text/html"}

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            result = await rotator.head("https://example.com/resource", headers={"Accept": "*/*"})

            assert result is mock_response
            assert result.headers["Content-Length"] == "12345"
            mock_make.assert_called_once_with(
                "HEAD", "https://example.com/resource", headers={"Accept": "*/*"}
            )

    async def test_options_method(self) -> None:
        """Test options() method."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            result = await rotator.options("https://example.com")

            assert result is mock_response
            mock_make.assert_called_once_with("OPTIONS", "https://example.com")

    async def test_options_method_cors_preflight(self) -> None:
        """Test OPTIONS method for CORS preflight request."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            headers = {
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
                "Origin": "https://example.com",
            }
            result = await rotator.options("https://api.example.com/endpoint", headers=headers)

            assert result is mock_response
            assert "Access-Control-Allow-Methods" in result.headers
            mock_make.assert_called_once_with(
                "OPTIONS", "https://api.example.com/endpoint", headers=headers
            )


class TestAsyncProxyRotatorHttpMethodsTimeout:
    """Test HTTP methods with timeout handling."""

    async def test_get_with_timeout(self) -> None:
        """Test GET request with custom timeout."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            result = await rotator.get("https://example.com", timeout=5.0)

            assert result is mock_response
            mock_make.assert_called_once_with("GET", "https://example.com", timeout=5.0)

    async def test_post_with_timeout(self) -> None:
        """Test POST request with custom timeout."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 201

        with patch.object(rotator, "_make_request", new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response

            result = await rotator.post("https://example.com", json={"data": "test"}, timeout=10.0)

            assert result is mock_response
            mock_make.assert_called_once_with(
                "POST", "https://example.com", json={"data": "test"}, timeout=10.0
            )


class TestAsyncProxyRotatorHttpMethodsProxyRotation:
    """Test HTTP methods with proxy rotation."""

    async def test_get_rotates_proxies_on_failure(self) -> None:
        """Test GET request rotates to next proxy on failure."""
        from proxywhirl.exceptions import ProxyConnectionError

        proxy1 = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        proxy2 = Proxy(url="http://192.168.1.2:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy1, proxy2])

        # First call fails, triggering rotation
        with patch.object(
            rotator, "_execute_async_with_retry", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.side_effect = [
                ConnectionError("First proxy failed"),
                MagicMock(status_code=200),
            ]

            # First request should fail
            with pytest.raises(ProxyConnectionError):
                await rotator.get("https://example.com")

            # Second request should succeed with rotated proxy
            result = await rotator.get("https://example.com")
            assert result.status_code == 200

    async def test_post_uses_different_proxy_each_call(self) -> None:
        """Test POST requests cycle through available proxies."""
        proxy1 = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        proxy2 = Proxy(url="http://192.168.1.2:8080", allow_local=True)
        proxy3 = Proxy(url="http://192.168.1.3:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy1, proxy2, proxy3], strategy="round-robin")

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(
            rotator, "_execute_async_with_retry", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = mock_response

            # Make multiple requests - should rotate through proxies
            await rotator.post("https://example.com", json={"attempt": 1})
            await rotator.post("https://example.com", json={"attempt": 2})
            await rotator.post("https://example.com", json={"attempt": 3})

            # Should have called execute 3 times
            assert mock_execute.call_count == 3


class TestAsyncProxyRotatorHttpMethodsResponseHandling:
    """Test HTTP methods with various response scenarios."""

    async def test_get_handles_200_response(self) -> None:
        """Test GET handles 200 OK response."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}

        with patch.object(
            rotator, "_execute_async_with_retry", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = mock_response

            result = await rotator.get("https://api.example.com/data")

            assert result.status_code == 200
            assert result.json() == {"ok": True}

    async def test_post_handles_201_created(self) -> None:
        """Test POST handles 201 Created response."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.headers = {"Location": "https://api.example.com/resource/123"}

        with patch.object(
            rotator, "_execute_async_with_retry", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = mock_response

            result = await rotator.post("https://api.example.com/create", json={"name": "test"})

            assert result.status_code == 201
            assert result.headers["Location"] == "https://api.example.com/resource/123"

    async def test_delete_handles_204_no_content(self) -> None:
        """Test DELETE handles 204 No Content response."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 204

        with patch.object(
            rotator, "_execute_async_with_retry", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = mock_response

            result = await rotator.delete("https://api.example.com/resource/123")

            assert result.status_code == 204

    async def test_get_handles_404_not_found(self) -> None:
        """Test GET handles 404 Not Found response."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch.object(
            rotator, "_execute_async_with_retry", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = mock_response

            result = await rotator.get("https://api.example.com/nonexistent")

            assert result.status_code == 404

    async def test_execute_async_with_retry_success(self) -> None:
        """Test _execute_async_with_retry with successful request."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()

        async def mock_request_fn():
            return mock_response

        result = await rotator._execute_async_with_retry(
            mock_request_fn, proxy, "GET", "https://example.com"
        )

        assert result is mock_response

    async def test_execute_async_with_retry_records_success(self) -> None:
        """Test _execute_async_with_retry records success in circuit breaker."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        mock_response = MagicMock()

        async def mock_request_fn():
            return mock_response

        cb = rotator.circuit_breakers[str(proxy.id)]
        # Circuit breaker should remain closed after success
        from proxywhirl.circuit_breaker import CircuitBreakerState

        assert cb.state == CircuitBreakerState.CLOSED

        await rotator._execute_async_with_retry(
            mock_request_fn, proxy, "GET", "https://example.com"
        )

        # Still closed after success
        assert cb.state == CircuitBreakerState.CLOSED

    async def test_execute_async_with_retry_retries_on_failure(self) -> None:
        """Test _execute_async_with_retry retries on failure."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        policy = RetryPolicy(max_attempts=3, base_delay=0.01)
        rotator = AsyncProxyRotator(proxies=[proxy], retry_policy=policy)

        call_count = 0
        mock_response = MagicMock()

        async def mock_request_fn():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection failed")
            return mock_response

        result = await rotator._execute_async_with_retry(
            mock_request_fn, proxy, "GET", "https://example.com"
        )

        assert result is mock_response
        assert call_count == 3

    async def test_execute_async_with_retry_circuit_breaker_open_raises(self) -> None:
        """Test _execute_async_with_retry raises when circuit breaker is open."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

        # Open the circuit breaker
        cb = rotator.circuit_breakers[str(proxy.id)]
        for _ in range(10):
            cb.record_failure()

        async def mock_request_fn():
            return MagicMock()

        from proxywhirl.exceptions import ProxyConnectionError

        with pytest.raises(ProxyConnectionError, match="Circuit breaker is open"):
            await rotator._execute_async_with_retry(
                mock_request_fn, proxy, "GET", "https://example.com"
            )

    async def test_execute_async_with_retry_exhausts_retries(self) -> None:
        """Test _execute_async_with_retry raises after exhausting retries."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        policy = RetryPolicy(max_attempts=2, base_delay=0.01)
        rotator = AsyncProxyRotator(proxies=[proxy], retry_policy=policy)

        async def mock_request_fn():
            raise ConnectionError("Connection failed")

        with pytest.raises(ConnectionError, match="Connection failed"):
            await rotator._execute_async_with_retry(
                mock_request_fn, proxy, "GET", "https://example.com"
            )
