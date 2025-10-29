"""
Integration tests for rotation strategies.

These tests validate strategies with realistic proxy pools and request simulations,
verifying they meet acceptance criteria from user stories.
"""

import time
from collections import Counter

import pytest

from proxywhirl.models import (
    Proxy,
    ProxyPool,
    HealthStatus,
    SelectionContext,
    StrategyConfig,
)
from proxywhirl.strategies import RoundRobinStrategy, RandomStrategy, LeastUsedStrategy


class TestRoundRobinIntegration:
    """Integration tests for RoundRobinStrategy (US1)."""

    def test_round_robin_with_realistic_proxy_pool(self):
        """
        Integration test: Round-robin with realistic proxy pool.
        
        Validates SC-001: Perfect distribution (±1 request variance).
        """
        # Arrange - Create pool with 5 proxies (some with existing usage)
        pool = ProxyPool(name="production-pool", max_pool_size=10)
        
        proxies = [
            Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY),
            Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY),
            Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.HEALTHY),
            Proxy(url="http://proxy4.example.com:8080", health_status=HealthStatus.DEGRADED),  # Still usable
            Proxy(url="http://proxy5.example.com:8080", health_status=HealthStatus.HEALTHY),
        ]
        
        for proxy in proxies:
            pool.add_proxy(proxy)
        
        strategy = RoundRobinStrategy()
        config = StrategyConfig(window_duration_seconds=3600)
        strategy.configure(config)
        
        # Act - Simulate 100 requests
        num_requests = 100
        selections = []
        
        for _ in range(num_requests):
            context = SelectionContext()
            proxy = strategy.select(pool, context)
            selections.append(proxy)
            
            # Simulate request completion
            success = True
            response_time_ms = 150.0
            strategy.record_result(proxy, success, response_time_ms)
        
        # Assert - Verify SC-001: Perfect distribution (±1 variance)
        selection_counts = Counter(p.url for p in selections)
        
        expected_per_proxy = num_requests / len(proxies)
        for url, count in selection_counts.items():
            variance = abs(count - expected_per_proxy)
            assert variance <= 1, (
                f"Proxy {url} has variance {variance} (count: {count}, "
                f"expected: {expected_per_proxy}). All counts: {selection_counts}"
            )
        
        # Verify all proxies were selected
        assert len(selection_counts) == len(proxies)
        
        # Verify metadata tracking
        all_proxies = pool.get_all_proxies()
        for proxy in all_proxies:
            assert proxy.requests_completed > 0, f"Proxy {proxy.url} never completed requests"
            assert proxy.requests_active == 0, f"Proxy {proxy.url} has active requests"
            assert proxy.total_requests > 0, f"Proxy {proxy.url} has no tracked requests"

    def test_round_robin_with_dynamic_pool_changes(self):
        """
        Integration test: Round-robin adapts to pool changes.
        
        Proxies can be added/removed, unhealthy proxies excluded dynamically.
        """
        # Arrange
        pool = ProxyPool(name="dynamic-pool")
        
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)
        
        strategy = RoundRobinStrategy()
        context = SelectionContext()
        
        # Act & Assert - Phase 1: Two proxies alternate
        selections1 = [strategy.select(pool, context) for _ in range(4)]
        urls1 = [p.url for p in selections1]
        assert urls1 == [
            "http://proxy1.com:8080",
            "http://proxy2.com:8080",
            "http://proxy1.com:8080",
            "http://proxy2.com:8080",
        ]
        
        # Phase 2: Add third proxy
        proxy3 = Proxy(url="http://proxy3.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy3)
        
        selections2 = [strategy.select(pool, context) for _ in range(6)]
        urls2 = [p.url for p in selections2]
        # Should cycle through all 3 proxies
        assert set(urls2) == {
            "http://proxy1.com:8080",
            "http://proxy2.com:8080",
            "http://proxy3.com:8080",
        }
        
        # Phase 3: Mark proxy2 as dead
        proxy2.health_status = HealthStatus.DEAD
        
        selections3 = [strategy.select(pool, context) for _ in range(4)]
        urls3 = [p.url for p in selections3]
        # Should skip proxy2, only use proxy1 and proxy3
        assert "http://proxy2.com:8080" not in urls3
        assert set(urls3) == {"http://proxy1.com:8080", "http://proxy3.com:8080"}

    def test_round_robin_with_failed_proxy_context(self):
        """
        Integration test: Round-robin respects failed_proxy_ids in context.
        
        For retry scenarios, previously failed proxies are excluded.
        """
        # Arrange
        pool = ProxyPool(name="retry-pool")
        
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy3 = Proxy(url="http://proxy3.com:8080", health_status=HealthStatus.HEALTHY)
        
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)
        pool.add_proxy(proxy3)
        
        strategy = RoundRobinStrategy()
        
        # Act - First attempt fails with proxy1
        context1 = SelectionContext(failed_proxy_ids=[])
        selected1 = strategy.select(pool, context1)
        
        # Simulate failure
        strategy.record_result(selected1, success=False, response_time_ms=5000.0)
        
        # Retry with proxy1 marked as failed
        context2 = SelectionContext(failed_proxy_ids=[str(selected1.id)])
        selected2 = strategy.select(pool, context2)
        
        # Assert - Should not select the same proxy
        assert selected2.id != selected1.id
        assert selected2.url in ["http://proxy2.com:8080", "http://proxy3.com:8080"]


class TestRandomIntegration:
    """Integration tests for RandomStrategy."""

    def test_random_with_realistic_pool(self):
        """
        Integration test: Random strategy with realistic proxy pool.
        """
        # Arrange
        pool = ProxyPool(name="random-pool")
        
        for i in range(10):
            pool.add_proxy(
                Proxy(
                    url=f"http://proxy{i}.example.com:8080",
                    health_status=HealthStatus.HEALTHY
                )
            )
        
        strategy = RandomStrategy()
        context = SelectionContext()
        
        # Act - Make 100 selections
        selections = [strategy.select(pool, context) for _ in range(100)]
        
        # Assert - All proxies should be selected at least once (high probability)
        selected_urls = {p.url for p in selections}
        all_urls = {p.url for p in pool.get_all_proxies()}
        
        # With 100 selections and 10 proxies, probability of missing one is very low
        assert len(selected_urls) >= 8, (
            f"Too few proxies selected: {len(selected_urls)}/10"
        )


class TestLeastUsedIntegration:
    """Integration tests for LeastUsedStrategy."""

    def test_least_used_achieves_perfect_load_balancing(self):
        """
        Integration test: Least-used achieves near-perfect load balancing.
        
        Validates that requests are distributed evenly across proxies.
        """
        # Arrange
        pool = ProxyPool(name="balanced-pool")
        
        num_proxies = 5
        for i in range(num_proxies):
            pool.add_proxy(
                Proxy(
                    url=f"http://proxy{i}.com:8080",
                    health_status=HealthStatus.HEALTHY
                )
            )
        
        strategy = LeastUsedStrategy()
        context = SelectionContext()
        
        # Act - Make 50 selections
        for _ in range(50):
            proxy = strategy.select(pool, context)
            # Simulate request completion
            strategy.record_result(proxy, success=True, response_time_ms=100.0)
        
        # Assert - Check load distribution
        all_proxies = pool.get_all_proxies()
        request_counts = [p.requests_completed for p in all_proxies]
        
        min_count = min(request_counts)
        max_count = max(request_counts)
        
        # With least-used, variance should be at most 1
        assert max_count - min_count <= 1, (
            f"Load imbalance detected. Min: {min_count}, Max: {max_count}. "
            f"Distribution: {request_counts}"
        )

    def test_least_used_with_pre_existing_load(self):
        """
        Integration test: Least-used rebalances pool with pre-existing load.
        """
        # Arrange - Create pool with uneven existing load
        pool = ProxyPool(name="uneven-pool")
        
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.requests_started = 50  # Heavily used
        proxy1.requests_completed = 50
        
        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.requests_started = 30  # Moderately used
        proxy2.requests_completed = 30
        
        proxy3 = Proxy(url="http://proxy3.com:8080", health_status=HealthStatus.HEALTHY)
        proxy3.requests_started = 5  # Lightly used
        proxy3.requests_completed = 5
        
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)
        pool.add_proxy(proxy3)
        
        strategy = LeastUsedStrategy()
        context = SelectionContext()
        
        # Act - Make 45 selections (should favor proxy3, then proxy2)
        selections = []
        for _ in range(45):
            proxy = strategy.select(pool, context)
            selections.append(proxy)
            strategy.record_result(proxy, success=True, response_time_ms=100.0)
        
        # Assert - Most selections should be proxy3 initially, then balanced
        final_counts = [p.requests_completed for p in pool.get_all_proxies()]
        
        # After rebalancing, all proxies should be closer together
        min_final = min(final_counts)
        max_final = max(final_counts)
        
        # Variance should be significantly reduced
        assert max_final - min_final <= 20, (
            f"Load not properly rebalanced. Final distribution: {final_counts}"
        )


class TestStrategyPerformance:
    """Integration tests for strategy performance requirements."""

    def test_strategy_selection_performance(self):
        """
        Integration test: Strategy selection meets <5ms overhead (SC-007).
        """
        # Arrange
        pool = ProxyPool(name="perf-pool")
        
        for i in range(100):
            pool.add_proxy(
                Proxy(
                    url=f"http://proxy{i}.com:8080",
                    health_status=HealthStatus.HEALTHY
                )
            )
        
        strategies = [
            RoundRobinStrategy(),
            RandomStrategy(),
            LeastUsedStrategy(),
        ]
        
        context = SelectionContext()
        
        # Act & Assert - Test each strategy
        for strategy in strategies:
            start_time = time.perf_counter()
            
            # Make 1000 selections
            for _ in range(1000):
                strategy.select(pool, context)
            
            end_time = time.perf_counter()
            elapsed_ms = (end_time - start_time) * 1000
            avg_ms_per_selection = elapsed_ms / 1000
            
            # Assert - Average selection time should be < 5ms (SC-007)
            assert avg_ms_per_selection < 5.0, (
                f"{strategy.__class__.__name__} exceeds 5ms overhead: "
                f"{avg_ms_per_selection:.2f}ms per selection"
            )
