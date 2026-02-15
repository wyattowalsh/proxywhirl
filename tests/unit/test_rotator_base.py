"""
Unit tests for ProxyRotatorBase shared functionality.

Tests verify the base class methods used by both ProxyWhirl and AsyncProxyWhirl.
"""

import pytest
from pydantic import SecretStr

from proxywhirl.circuit_breaker import CircuitBreakerState
from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import HealthStatus, Proxy, ProxyPool
from proxywhirl.retry import RetryPolicy
from proxywhirl.rotator import ProxyRotatorBase
from proxywhirl.strategies import RoundRobinStrategy


class ConcreteRotator(ProxyRotatorBase):
    """Concrete implementation of ProxyRotatorBase for testing."""

    def __init__(self, proxies: list[Proxy] | None = None):
        pool = ProxyPool(name="test-pool", proxies=proxies or [])
        strategy = RoundRobinStrategy()
        retry_policy = RetryPolicy()
        self._init_common(pool, strategy, None, retry_policy)
        if proxies:
            self._init_circuit_breakers_for_proxies(proxies)


class TestProxyRotatorBaseInit:
    """Test ProxyRotatorBase initialization."""

    def test_init_common_sets_attributes(self):
        """Test that _init_common sets all expected attributes."""
        proxy = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator = ConcreteRotator(proxies=[proxy])

        assert rotator.pool is not None
        assert rotator.strategy is not None
        assert rotator.retry_policy is not None
        assert rotator.retry_metrics is not None
        assert rotator.circuit_breakers is not None

    def test_init_circuit_breakers_for_proxies(self):
        """Test that circuit breakers are initialized for all proxies."""
        proxies = [
            Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY),
            Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY),
            Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.HEALTHY),
        ]
        rotator = ConcreteRotator(proxies=proxies)

        assert len(rotator.circuit_breakers) == 3
        for proxy in proxies:
            assert str(proxy.id) in rotator.circuit_breakers
            assert rotator.circuit_breakers[str(proxy.id)].state == CircuitBreakerState.CLOSED


class TestGetProxyDict:
    """Test _get_proxy_dict method."""

    def test_basic_proxy_url(self):
        """Test conversion of basic proxy URL."""
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator = ConcreteRotator(proxies=[proxy])

        result = rotator._get_proxy_dict(proxy)

        assert result["http://"] == "http://proxy.example.com:8080"
        assert result["https://"] == "http://proxy.example.com:8080"

    def test_proxy_with_credentials(self):
        """Test conversion of proxy with username and password."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("user"),
            password=SecretStr("pass"),
            health_status=HealthStatus.HEALTHY,
        )
        rotator = ConcreteRotator(proxies=[proxy])

        result = rotator._get_proxy_dict(proxy)

        assert result["http://"] == "http://user:pass@proxy.example.com:8080"
        assert result["https://"] == "http://user:pass@proxy.example.com:8080"


class TestShouldUseCircuitBreaker:
    """Test _should_use_circuit_breaker method."""

    def test_returns_true_when_circuit_closed(self):
        """Test that closed circuit breaker allows requests."""
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator = ConcreteRotator(proxies=[proxy])

        assert rotator._should_use_circuit_breaker(proxy) is True

    def test_returns_false_when_circuit_open(self):
        """Test that open circuit breaker blocks requests."""
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator = ConcreteRotator(proxies=[proxy])

        # Open the circuit breaker
        cb = rotator.circuit_breakers[str(proxy.id)]
        for _ in range(cb.failure_threshold):
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert rotator._should_use_circuit_breaker(proxy) is False

    def test_returns_true_when_no_circuit_breaker(self):
        """Test that missing circuit breaker allows requests."""
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator = ConcreteRotator(proxies=[])  # No proxies, so no circuit breakers

        assert rotator._should_use_circuit_breaker(proxy) is True


class TestSelectProxyWithCircuitBreaker:
    """Test _select_proxy_with_circuit_breaker method."""

    def test_selects_from_available_proxies(self):
        """Test that selection respects circuit breaker states."""
        proxies = [
            Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY),
            Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY),
        ]
        rotator = ConcreteRotator(proxies=proxies)

        selected = rotator._select_proxy_with_circuit_breaker()
        assert selected in proxies

    def test_skips_proxies_with_open_circuit(self):
        """Test that proxies with open circuits are skipped."""
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator = ConcreteRotator(proxies=[proxy1, proxy2])

        # Open circuit for proxy1
        cb = rotator.circuit_breakers[str(proxy1.id)]
        for _ in range(cb.failure_threshold):
            cb.record_failure()

        # Should only select proxy2
        for _ in range(5):
            selected = rotator._select_proxy_with_circuit_breaker()
            assert selected.id == proxy2.id

    def test_raises_when_all_circuits_open(self):
        """Test that error is raised when all circuit breakers are open."""
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator = ConcreteRotator(proxies=[proxy])

        # Open the circuit
        cb = rotator.circuit_breakers[str(proxy.id)]
        for _ in range(cb.failure_threshold):
            cb.record_failure()

        with pytest.raises(ProxyPoolEmptyError, match="503 Service Temporarily Unavailable"):
            rotator._select_proxy_with_circuit_breaker()


class TestAddProxyCommon:
    """Test _add_proxy_common method."""

    def test_adds_proxy_and_circuit_breaker(self):
        """Test that adding proxy also creates circuit breaker."""
        rotator = ConcreteRotator(proxies=[])
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)

        rotator._add_proxy_common(proxy)

        assert proxy in rotator.pool.get_all_proxies()
        assert str(proxy.id) in rotator.circuit_breakers
        assert rotator.circuit_breakers[str(proxy.id)].state == CircuitBreakerState.CLOSED


class TestRemoveProxyCommon:
    """Test _remove_proxy_common method."""

    def test_removes_circuit_breaker(self):
        """Test that removing proxy also removes circuit breaker."""
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator = ConcreteRotator(proxies=[proxy])

        assert str(proxy.id) in rotator.circuit_breakers

        rotator._remove_proxy_common(str(proxy.id))

        assert str(proxy.id) not in rotator.circuit_breakers

    def test_handles_missing_circuit_breaker(self):
        """Test that removing non-existent circuit breaker doesn't raise."""
        rotator = ConcreteRotator(proxies=[])

        # Should not raise
        rotator._remove_proxy_common("non-existent-id")


class TestGetCircuitBreakerStates:
    """Test get_circuit_breaker_states method."""

    def test_returns_copy_of_circuit_breakers(self):
        """Test that get_circuit_breaker_states returns a copy."""
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator = ConcreteRotator(proxies=[proxy])

        states = rotator.get_circuit_breaker_states()

        assert str(proxy.id) in states
        assert states is not rotator.circuit_breakers

    def test_returns_empty_dict_when_no_proxies(self):
        """Test with no proxies."""
        rotator = ConcreteRotator(proxies=[])

        states = rotator.get_circuit_breaker_states()

        assert states == {}


class TestResetCircuitBreaker:
    """Test reset_circuit_breaker method."""

    def test_resets_circuit_breaker(self):
        """Test that reset_circuit_breaker resets to CLOSED state."""
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator = ConcreteRotator(proxies=[proxy])

        # Open the circuit breaker
        cb = rotator.circuit_breakers[str(proxy.id)]
        for _ in range(10):
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN

        rotator.reset_circuit_breaker(str(proxy.id))

        assert cb.state == CircuitBreakerState.CLOSED

    def test_raises_key_error_for_unknown_proxy(self):
        """Test that KeyError is raised for unknown proxy_id."""
        rotator = ConcreteRotator(proxies=[])

        with pytest.raises(KeyError, match="No circuit breaker found"):
            rotator.reset_circuit_breaker("unknown-id")


class TestGetRetryMetrics:
    """Test get_retry_metrics method."""

    def test_returns_retry_metrics(self):
        """Test that get_retry_metrics returns the metrics instance."""
        rotator = ConcreteRotator(proxies=[])

        metrics = rotator.get_retry_metrics()

        assert metrics is rotator.retry_metrics


class TestGetPoolStats:
    """Test get_pool_stats method."""

    def test_returns_correct_stats(self):
        """Test that get_pool_stats returns correct statistics."""
        proxy1 = Proxy(
            url="http://proxy1.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            total_requests=10,
            total_successes=8,
            total_failures=2,
        )
        proxy2 = Proxy(
            url="http://proxy2.example.com:8080",
            health_status=HealthStatus.UNHEALTHY,
            total_requests=5,
            total_successes=2,
            total_failures=3,
        )
        rotator = ConcreteRotator(proxies=[proxy1, proxy2])

        stats = rotator.get_pool_stats()

        assert stats["total_proxies"] == 2
        assert stats["healthy_proxies"] == 1
        assert stats["unhealthy_proxies"] == 1
        assert stats["dead_proxies"] == 0
        assert stats["total_requests"] == 15
        assert stats["total_successes"] == 10
        assert stats["total_failures"] == 5

    def test_handles_empty_pool(self):
        """Test get_pool_stats with no proxies."""
        rotator = ConcreteRotator(proxies=[])

        stats = rotator.get_pool_stats()

        assert stats["total_proxies"] == 0
        assert stats["average_success_rate"] == 0.0


class TestGetStatistics:
    """Test get_statistics method."""

    def test_includes_source_breakdown(self):
        """Test that get_statistics includes source_breakdown."""
        from proxywhirl.models import ProxySource

        proxy1 = Proxy(
            url="http://proxy1.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            source=ProxySource.USER,
        )
        proxy2 = Proxy(
            url="http://proxy2.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            source=ProxySource.FETCHED,
        )
        rotator = ConcreteRotator(proxies=[proxy1, proxy2])

        stats = rotator.get_statistics()

        assert "source_breakdown" in stats
        assert stats["source_breakdown"]["user"] == 1
        assert stats["source_breakdown"]["fetched"] == 1
