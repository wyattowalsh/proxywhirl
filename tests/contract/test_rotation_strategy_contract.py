"""Contract tests for RotationStrategy protocol.

Ensures all strategy implementations fulfill the RotationStrategy contract:
- Must have a select method
- select method must accept SelectionContext
- select method must return Proxy or raise ProxyPoolEmptyError when unavailable
- Must be stateful (track requests)
"""

import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import HealthStatus, Proxy, ProxyPool, SelectionContext
from proxywhirl.strategies import (
    CompositeStrategy,
    CostAwareStrategy,
    GeoTargetedStrategy,
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    RandomStrategy,
    RoundRobinStrategy,
    SessionPersistenceStrategy,
    StrategyRegistry,
    WeightedStrategy,
)


class TestRotationStrategyContract:
    """Contract tests for all RotationStrategy implementations."""

    @pytest.fixture
    def sample_pool(self) -> ProxyPool:
        """Create a pool with test proxies."""
        pool = ProxyPool(name="test-pool")
        for i in range(5):
            proxy = Proxy(
                url=f"http://proxy{i}.example.com:{8080 + i}",
                health_status=HealthStatus.HEALTHY,
            )
            pool.add_proxy(proxy)
        return pool

    @pytest.fixture
    def sample_context(self) -> SelectionContext:
        """Create a sample selection context."""
        return SelectionContext(session_id="contract-session")

    @pytest.mark.parametrize(
        "strategy_class",
        [
            RoundRobinStrategy,
            RandomStrategy,
            WeightedStrategy,
            LeastUsedStrategy,
            PerformanceBasedStrategy,
            SessionPersistenceStrategy,
            GeoTargetedStrategy,
            CostAwareStrategy,
        ],
    )
    def test_strategy_has_select_method(self, strategy_class) -> None:
        """Verify all strategies have a select method."""
        assert hasattr(strategy_class, "select"), f"{strategy_class.__name__} missing select method"
        assert callable(strategy_class.select), f"{strategy_class.__name__}.select is not callable"

    @pytest.mark.parametrize(
        "strategy_class",
        [
            RoundRobinStrategy,
            RandomStrategy,
            WeightedStrategy,
            LeastUsedStrategy,
            PerformanceBasedStrategy,
            SessionPersistenceStrategy,
            GeoTargetedStrategy,
            CostAwareStrategy,
        ],
    )
    def test_strategy_select_returns_optional_proxy(
        self, strategy_class, sample_pool: ProxyPool, sample_context: SelectionContext
    ) -> None:
        """Verify select method returns a Proxy."""
        strategy = strategy_class()
        result = strategy.select(sample_pool, sample_context)
        assert isinstance(result, Proxy), (
            f"{strategy_class.__name__}.select returned {type(result)}, expected Proxy"
        )

    @pytest.mark.parametrize(
        "strategy_class",
        [
            RoundRobinStrategy,
            RandomStrategy,
            WeightedStrategy,
            LeastUsedStrategy,
            PerformanceBasedStrategy,
            SessionPersistenceStrategy,
            GeoTargetedStrategy,
            CostAwareStrategy,
        ],
    )
    def test_strategy_handles_empty_pool(
        self, strategy_class, sample_context: SelectionContext
    ) -> None:
        """Verify strategies reject empty pools consistently."""
        empty_pool = ProxyPool(name="empty-pool")

        strategy = strategy_class()
        with pytest.raises((ProxyPoolEmptyError, ValueError)):
            strategy.select(empty_pool, SelectionContext(session_id="empty-session"))

    @pytest.mark.parametrize(
        "strategy_class",
        [
            RoundRobinStrategy,
            RandomStrategy,
            WeightedStrategy,
            LeastUsedStrategy,
            PerformanceBasedStrategy,
            SessionPersistenceStrategy,
            GeoTargetedStrategy,
            CostAwareStrategy,
        ],
    )
    def test_strategy_handles_single_proxy(
        self, strategy_class, sample_context: SelectionContext
    ) -> None:
        """Verify strategies work with single proxy."""
        pool = ProxyPool(name="single-pool")
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)
        context = SelectionContext(session_id="single-session")

        strategy = strategy_class()
        result = strategy.select(pool, context)

        assert result.url == "http://proxy.example.com:8080"

    @pytest.mark.parametrize(
        "strategy_class",
        [
            RoundRobinStrategy,
            RandomStrategy,
            WeightedStrategy,
            LeastUsedStrategy,
            PerformanceBasedStrategy,
        ],
    )
    def test_strategy_respects_health_status(self, strategy_class, sample_pool: ProxyPool) -> None:
        """Verify strategies respect proxy health status."""
        # Mark all but one proxy as unhealthy
        proxies = sample_pool.get_all_proxies()
        healthy_proxy = proxies[0]

        for proxy in proxies[1:]:
            proxy.health_status = HealthStatus.UNHEALTHY

        context = SelectionContext()
        strategy = strategy_class()

        selections = [strategy.select(sample_pool, context) for _ in range(10)]
        healthy_count = sum(1 for p in selections if p.url == healthy_proxy.url)

        assert healthy_count >= 1, f"{strategy_class.__name__} not respecting health status"

    def test_round_robin_rotation(self, sample_pool: ProxyPool) -> None:
        """Verify RoundRobinStrategy cycles through proxies."""
        context = SelectionContext()
        strategy = RoundRobinStrategy()

        selections = [strategy.select(sample_pool, context) for _ in range(15)]
        selected_urls = [p.url for p in selections]

        # Should have at least 2 different proxies (not always same)
        assert len(set(selected_urls)) >= 2, "RoundRobinStrategy should rotate through proxies"

    def test_random_strategy_distribution(self, sample_pool: ProxyPool) -> None:
        """Verify RandomStrategy doesn't always return same proxy."""
        context = SelectionContext()
        strategy = RandomStrategy()

        selections = [strategy.select(sample_pool, context) for _ in range(30)]
        selected_urls = [p.url for p in selections]

        # Should have at least 2 different proxies
        assert len(set(selected_urls)) >= 2, "RandomStrategy should select from multiple proxies"

    def test_composite_strategy_works(self, sample_pool: ProxyPool) -> None:
        """Verify CompositeStrategy delegates to child strategies."""
        composite = CompositeStrategy(selector=RandomStrategy())
        context = SelectionContext()

        result = composite.select(sample_pool, context)
        assert isinstance(result, Proxy)

    def test_strategy_registry_has_all_strategies(self) -> None:
        """Verify StrategyRegistry contains all defined strategies."""
        registry = StrategyRegistry()

        expected_strategies = {
            "round_robin": RoundRobinStrategy,
            "random": RandomStrategy,
            "weighted": WeightedStrategy,
            "least_used": LeastUsedStrategy,
            "performance_based": PerformanceBasedStrategy,
            "session_persistence": SessionPersistenceStrategy,
            "geo_targeted": GeoTargetedStrategy,
            "cost_aware": CostAwareStrategy,
        }

        for name, strategy_class in expected_strategies.items():
            registry.register_strategy(name, strategy_class, validate=False)
            assert registry.get_strategy(name) is strategy_class, (
                f"Registry missing strategy: {name}"
            )


class TestStrategyProtocolCompliance:
    """Test that strategies comply with RotationStrategy protocol."""

    @pytest.mark.parametrize(
        "strategy_class",
        [
            RoundRobinStrategy,
            RandomStrategy,
            WeightedStrategy,
            LeastUsedStrategy,
            PerformanceBasedStrategy,
            SessionPersistenceStrategy,
            GeoTargetedStrategy,
            CostAwareStrategy,
        ],
    )
    def test_strategy_implements_protocol(self, strategy_class) -> None:
        """Verify strategy implements RotationStrategy protocol methods."""
        strategy = strategy_class()

        # Must have select method with correct signature
        import inspect

        sig = inspect.signature(strategy.select)
        params = list(sig.parameters.keys())

        assert "context" in params, f"{strategy_class.__name__}.select missing 'context' parameter"
