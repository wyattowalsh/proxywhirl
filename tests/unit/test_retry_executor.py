"""
Unit tests for RetryExecutor.
"""

from unittest.mock import Mock

import pytest

from proxywhirl import Proxy
from proxywhirl.circuit_breaker import CircuitBreaker, CircuitBreakerState
from proxywhirl.retry_executor import RetryExecutor
from proxywhirl.retry_metrics import RetryMetrics, RetryOutcome
from proxywhirl.retry_policy import RetryPolicy


class TestIntelligentProxySelection:
    """Test intelligent proxy selection algorithm."""

    def test_excludes_failed_proxy(self):
        """Test that failed proxy is excluded from selection."""
        policy = RetryPolicy()
        circuit_breakers = {}
        metrics = RetryMetrics()

        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")

        circuit_breakers[proxy1.id] = CircuitBreaker(proxy_id=proxy1.id)
        circuit_breakers[proxy2.id] = CircuitBreaker(proxy_id=proxy2.id)

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        # Select proxy when proxy1 failed
        selected = executor.select_retry_proxy([proxy1, proxy2], proxy1)

        assert selected == proxy2
        assert selected.id != proxy1.id

    def test_excludes_open_circuit_breakers(self):
        """Test that proxies with open circuit breakers are excluded."""
        policy = RetryPolicy()
        circuit_breakers = {}
        metrics = RetryMetrics()

        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        proxy3 = Proxy(url="http://proxy3.example.com:8080")

        circuit_breakers[proxy1.id] = CircuitBreaker(proxy_id=proxy1.id)
        circuit_breakers[proxy2.id] = CircuitBreaker(proxy_id=proxy2.id)
        circuit_breakers[proxy3.id] = CircuitBreaker(proxy_id=proxy3.id)

        # Open circuit for proxy2
        for _ in range(5):
            circuit_breakers[proxy2.id].record_failure()

        assert circuit_breakers[proxy2.id].state == CircuitBreakerState.OPEN

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        # Select proxy when proxy1 failed
        selected = executor.select_retry_proxy([proxy1, proxy2, proxy3], proxy1)

        # Should select proxy3 (proxy1 is failed, proxy2 circuit is open)
        assert selected == proxy3

    def test_prioritizes_high_success_rate(self):
        """Test that proxies with higher success rates are prioritized."""
        policy = RetryPolicy()
        circuit_breakers = {}
        metrics = RetryMetrics()

        # Create proxies with different success rates
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy1.total_requests = 100
        proxy1.total_successes = 95  # 95% success rate

        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        proxy2.total_requests = 100
        proxy2.total_successes = 60  # 60% success rate

        failed_proxy = Proxy(url="http://failed.example.com:8080")

        circuit_breakers[proxy1.id] = CircuitBreaker(proxy_id=proxy1.id)
        circuit_breakers[proxy2.id] = CircuitBreaker(proxy_id=proxy2.id)
        circuit_breakers[failed_proxy.id] = CircuitBreaker(proxy_id=failed_proxy.id)

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        # Select proxy
        selected = executor.select_retry_proxy([proxy1, proxy2], failed_proxy)

        # Should select proxy1 (higher success rate)
        assert selected == proxy1

    def test_returns_none_when_no_candidates(self):
        """Test that None is returned when no suitable proxies available."""
        policy = RetryPolicy()
        circuit_breakers = {}
        metrics = RetryMetrics()

        proxy1 = Proxy(url="http://proxy1.example.com:8080")

        circuit_breakers[proxy1.id] = CircuitBreaker(proxy_id=proxy1.id)

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        # Only one proxy available, and it's the failed one
        selected = executor.select_retry_proxy([proxy1], proxy1)

        assert selected is None

    def test_geo_targeting_awareness(self):
        """Test that geo-targeting gives bonus to matching region."""
        policy = RetryPolicy()
        circuit_breakers = {}
        metrics = RetryMetrics()

        # Create proxies with different regions
        proxy_us = Proxy(
            url="http://proxy-us.example.com:8080",
            metadata={"region": "US-EAST"},
        )
        proxy_us.total_requests = 100
        proxy_us.total_successes = 80  # 80% success rate

        proxy_eu = Proxy(
            url="http://proxy-eu.example.com:8080",
            metadata={"region": "EU-WEST"},
        )
        proxy_eu.total_requests = 100
        proxy_eu.total_successes = 85  # 85% success rate (slightly better)

        failed_proxy = Proxy(url="http://failed.example.com:8080")

        circuit_breakers[proxy_us.id] = CircuitBreaker(proxy_id=proxy_us.id)
        circuit_breakers[proxy_eu.id] = CircuitBreaker(proxy_id=proxy_eu.id)
        circuit_breakers[failed_proxy.id] = CircuitBreaker(proxy_id=failed_proxy.id)

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        # Select proxy with US target region
        selected = executor.select_retry_proxy(
            [proxy_us, proxy_eu], failed_proxy, target_region="US-EAST"
        )

        # Should select proxy_us despite lower success rate (10% region bonus)
        assert selected == proxy_us

    def test_score_calculation(self):
        """Test proxy score calculation."""
        policy = RetryPolicy()
        circuit_breakers = {}
        metrics = RetryMetrics()

        proxy = Proxy(url="http://proxy1.example.com:8080")
        proxy.total_requests = 100
        proxy.total_successes = 90  # 90% success rate

        circuit_breakers[proxy.id] = CircuitBreaker(proxy_id=proxy.id)

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        score = executor._calculate_proxy_score(proxy)

        # Base score: (0.7 * 0.9) + (0.3 * 1.0) = 0.63 + 0.3 = 0.93
        # (assuming no latency data, normalized_latency = 0)
        assert score >= 0.9  # Should be high score
