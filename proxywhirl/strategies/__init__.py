"""
Rotation strategies package for proxy selection.

This package provides various strategies for selecting proxies from a pool:

- RoundRobinStrategy: Sequential rotation through proxies
- RandomStrategy: Random proxy selection
- WeightedStrategy: Selection weighted by success rate or custom weights
- LeastUsedStrategy: Selects least-used proxy (min-heap based)
- PerformanceBasedStrategy: Selection based on EMA response times
- SessionPersistenceStrategy: Maintains session affinity
- GeoTargetedStrategy: Location-based selection
- CostAwareStrategy: Selection considering proxy costs
- CompositeStrategy: Combines multiple strategies

Usage:
    from proxywhirl.strategies import RoundRobinStrategy, StrategyRegistry

    strategy = RoundRobinStrategy()
    proxy = strategy.select(pool)
"""

from proxywhirl.strategies.core import (
    CompositeStrategy,
    CostAwareStrategy,
    GeoTargetedStrategy,
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    RandomStrategy,
    RotationStrategy,
    RoundRobinStrategy,
    SessionManager,
    SessionPersistenceStrategy,
    StrategyRegistry,
    WeightedStrategy,
)

__all__ = [
    # Protocol
    "RotationStrategy",
    # Registry
    "StrategyRegistry",
    # Simple strategies
    "RoundRobinStrategy",
    "RandomStrategy",
    # Weighted strategies
    "WeightedStrategy",
    "LeastUsedStrategy",
    # Performance strategies
    "PerformanceBasedStrategy",
    # Session strategies
    "SessionManager",
    "SessionPersistenceStrategy",
    # Advanced strategies
    "GeoTargetedStrategy",
    "CostAwareStrategy",
    "CompositeStrategy",
]
