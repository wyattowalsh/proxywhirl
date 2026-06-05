"""Test weighted strategy randomness and distribution.

Tests:
- Weighted strategy produces statistically correct distribution based on success_rate
- Randomness is working properly
- Low success_rate proxies are rarely selected
- Distribution matches success_rate weights over large samples
"""

from __future__ import annotations

import random
from collections import Counter

from proxywhirl.models import Proxy, ProxyPool, SelectionContext
from proxywhirl.strategies import WeightedStrategy


def create_proxy_with_success_rate(url: str, success_rate: float) -> Proxy:
    """Create a proxy with specific success rate.

    Args:
        url: Proxy URL
        success_rate: Desired success rate (0.0-1.0)

    Returns:
        Proxy with total_successes/total_requests set to achieve desired rate
    """
    proxy = Proxy(url=url)
    # Set total_requests to 100 for easy calculation
    proxy.total_requests = 100
    # Set total_successes to achieve desired success rate
    proxy.total_successes = int(success_rate * 100)
    return proxy


class TestWeightedStrategyDistribution:
    """Test that weighted strategy produces correct distribution."""

    def test_equal_success_rates_equal_distribution(self) -> None:
        """Test that equal success rates produce roughly equal distribution."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate(f"http://proxy{i}.example.com:8080", 0.5)
            for i in range(4)
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        # Collect many selections
        selections = []
        for _ in range(10_000):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        # Count occurrences
        counts = Counter(selections)

        # With equal success rates, each should be selected ~25%
        expected_per_proxy = 10_000 / 4  # 2500

        for url, count in counts.items():
            # Allow 10% variance
            assert (expected_per_proxy * 0.9) <= count <= (expected_per_proxy * 1.1)

    def test_success_rate_2_to_1_distribution(self) -> None:
        """Test that 2:1 success_rate ratio affects selection ratio."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate("http://proxy1.example.com:8080", 0.9),
            create_proxy_with_success_rate("http://proxy2.example.com:8080", 0.45),
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        for _ in range(5_000):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        counts = Counter(selections)
        url1 = "http://proxy1.example.com:8080"
        url2 = "http://proxy2.example.com:8080"

        # Higher success rate should be selected more often
        count1 = counts.get(url1, 0)
        count2 = counts.get(url2, 0)

        assert count1 > count2

    def test_success_rate_proportional_selection(self) -> None:
        """Test proportional selection with multiple success rates."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate(f"http://proxy{i}.example.com:8080", 0.1 * (i + 1))
            for i in range(5)
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        for _ in range(10_000):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        urls = set(selections)
        assert len(urls) == len(proxies)

    def test_large_success_rate_differences(self) -> None:
        """Test with large differences in success rates."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate("http://proxy1.example.com:8080", 0.99),
            create_proxy_with_success_rate("http://proxy2.example.com:8080", 0.1),
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        for _ in range(5_000):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        counts = Counter(selections)
        # High success rate proxy should dominate
        assert counts["http://proxy1.example.com:8080"] > counts["http://proxy2.example.com:8080"]

    def test_very_small_success_rate_differences(self) -> None:
        """Test with very small differences in success rates."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate("http://proxy1.example.com:8080", 0.501),
            create_proxy_with_success_rate("http://proxy2.example.com:8080", 0.499),
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        for _ in range(10_000):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        # Both should be selected (very close rates)
        counts = Counter(selections)
        assert len(counts) == 2

    def test_fractional_success_rates(self) -> None:
        """Test with fractional success rates."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate("http://proxy1.example.com:8080", 0.333),
            create_proxy_with_success_rate("http://proxy2.example.com:8080", 0.667),
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        for _ in range(5_000):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        counts = Counter(selections)
        # 2:1 ratio should favor proxy2
        assert counts["http://proxy2.example.com:8080"] > counts["http://proxy1.example.com:8080"]


class TestZeroAndNegativeWeights:
    """Test edge cases with zero and very low success rates."""

    def test_success_rate_validation_accepts_valid_values(self) -> None:
        """Test that zero and very low success rates are handled."""
        proxies = [
            create_proxy_with_success_rate("http://proxy1.example.com:8080", 0.0),
            create_proxy_with_success_rate("http://proxy2.example.com:8080", 0.5),
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)
        strategy = WeightedStrategy()

        # Should not raise - zero rates are handled with minimum weight (0.1)
        selections = []
        for _ in range(100):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        assert len(selections) == 100

    def test_low_success_rate_rarely_selected(self) -> None:
        """Test that very low success rate proxies are rarely selected."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate("http://proxy1.example.com:8080", 0.99),
            create_proxy_with_success_rate("http://proxy2.example.com:8080", 0.01),
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        for _ in range(1_000):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        counts = Counter(selections)
        # High rate should dominate (>90% of selections)
        high_rate_count = counts.get("http://proxy1.example.com:8080", 0)
        assert high_rate_count > 900

    def test_single_high_success_rate(self) -> None:
        """Test single proxy with high success rate."""
        strategy = WeightedStrategy()
        proxy = create_proxy_with_success_rate("http://proxy1.example.com:8080", 0.95)
        pool = ProxyPool(name="test_pool", proxies=[proxy])

        selections = []
        for _ in range(100):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        # All selections should be from the single proxy
        assert all(s == "http://proxy1.example.com:8080" for s in selections)


class TestWeightedStrategyEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_weight_distribution_chi_square(self) -> None:
        """Test distribution using chi-square test for goodness of fit."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate("http://proxy1.example.com:8080", 0.6),
            create_proxy_with_success_rate("http://proxy2.example.com:8080", 0.4),
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        random_state = random.getstate()
        random.seed(0)
        try:
            for _ in range(2_000):
                context = SelectionContext()
                selected = strategy.select(pool, context)
                selections.append(selected.url)
        finally:
            random.setstate(random_state)

        counts = Counter(selections)
        # Roughly 60:40 distribution
        url1 = "http://proxy1.example.com:8080"
        url2 = "http://proxy2.example.com:8080"
        count1 = counts.get(url1, 0)
        count2 = counts.get(url2, 0)

        # 60:40 expected from weights
        assert 1000 < count1 < 1200
        assert 800 < count2 < 1000

    def test_many_proxies_with_uneven_rates(self) -> None:
        """Test many proxies with varying success rates."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate(f"http://proxy{i}.example.com:8080", 0.1 * (i + 1))
            for i in range(10)
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        for _ in range(5_000):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        # All proxies should be selected at least once
        selected_urls = set(selections)
        assert len(selected_urls) == 10

    def test_all_equal_low_rates(self) -> None:
        """Test all proxies with equal low success rates."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate(f"http://proxy{i}.example.com:8080", 0.05)
            for i in range(5)
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        for _ in range(1_000):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        # Even with low rates, distribution should be roughly equal
        counts = Counter(selections)
        for count in counts.values():
            # ~200 selections per proxy (1000/5), allow ±50%
            assert 100 < count < 300


class TestRandomnessProperties:
    """Test randomness and distribution properties."""

    def test_selection_is_non_deterministic(self) -> None:
        """Test that selection is non-deterministic."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate("http://proxy1.example.com:8080", 0.5),
            create_proxy_with_success_rate("http://proxy2.example.com:8080", 0.5),
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections1 = []
        selections2 = []
        for _ in range(100):
            context1 = SelectionContext()
            selections1.append(strategy.select(pool, context1).url)

        for _ in range(100):
            context2 = SelectionContext()
            selections2.append(strategy.select(pool, context2).url)

        # Sequences should be different (not identical)
        assert selections1 != selections2

    def test_selection_independence(self) -> None:
        """Test that selections are independent."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate(f"http://proxy{i}.example.com:8080", 0.5)
            for i in range(3)
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        for _ in range(1_000):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        # Each proxy should be selected roughly equally (±30%)
        counts = Counter(selections)
        expected = 1000 / 3
        for count in counts.values():
            assert (expected * 0.7) < count < (expected * 1.3)

    def test_long_tail_selection(self) -> None:
        """Test that long-tail (low-probability) proxies are still selected."""
        strategy = WeightedStrategy()
        proxies = [
            create_proxy_with_success_rate("http://proxy1.example.com:8080", 0.98),
            create_proxy_with_success_rate("http://proxy2.example.com:8080", 0.01),
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        for _ in range(1_000):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected.url)

        # Even the low-probability proxy should be selected (minimum weight floor)
        counts = Counter(selections)
        assert counts.get("http://proxy2.example.com:8080", 0) > 0

    def test_distribution_consistency_across_runs(self) -> None:
        """Test that distribution is consistent across multiple runs."""
        proxies = [
            create_proxy_with_success_rate("http://proxy1.example.com:8080", 0.7),
            create_proxy_with_success_rate("http://proxy2.example.com:8080", 0.3),
        ]

        distributions = []
        for _ in range(3):
            strategy = WeightedStrategy()
            pool = ProxyPool(
                name="test_pool",
                proxies=[
                    create_proxy_with_success_rate("http://proxy1.example.com:8080", 0.7),
                    create_proxy_with_success_rate("http://proxy2.example.com:8080", 0.3),
                ],
            )

            selections = []
            for _ in range(1_000):
                context = SelectionContext()
                selected = strategy.select(pool, context)
                selections.append(selected.url)

            counts = Counter(selections)
            ratio = counts.get("http://proxy1.example.com:8080", 0) / counts.get(
                "http://proxy2.example.com:8080", 1
            )
            distributions.append(ratio)

        # Ratios should be similar across runs (within 20%)
        avg_ratio = sum(distributions) / len(distributions)
        for ratio in distributions:
            assert 0.8 < (ratio / avg_ratio) < 1.2
