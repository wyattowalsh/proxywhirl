"""Rotation strategies for ProxyWhirl (package facade)."""

from __future__ import annotations

from proxywhirl.strategies.base import ProxyMetrics, RotationStrategy, StrategyState
from proxywhirl.strategies.composite import CompositeStrategy
from proxywhirl.strategies.cost import CostAwareStrategy
from proxywhirl.strategies.geo import GeoTargetedStrategy
from proxywhirl.strategies.least_used import LeastUsedStrategy
from proxywhirl.strategies.performance import PerformanceBasedStrategy
from proxywhirl.strategies.random import RandomStrategy
from proxywhirl.strategies.registry import (
    BUILTIN_STRATEGY_CLASSES,
    BuiltinStrategyName,
    StrategyRegistry,
    resolve_builtin_strategy,
)
from proxywhirl.strategies.round_robin import RoundRobinStrategy
from proxywhirl.strategies.session import SessionManager, SessionPersistenceStrategy
from proxywhirl.strategies.weighted import WeightedStrategy

__all__ = [
    "BUILTIN_STRATEGY_CLASSES",
    "BuiltinStrategyName",
    "CompositeStrategy",
    "CostAwareStrategy",
    "GeoTargetedStrategy",
    "LeastUsedStrategy",
    "PerformanceBasedStrategy",
    "ProxyMetrics",
    "RandomStrategy",
    "RotationStrategy",
    "RoundRobinStrategy",
    "SessionManager",
    "SessionPersistenceStrategy",
    "StrategyRegistry",
    "StrategyState",
    "WeightedStrategy",
    "resolve_builtin_strategy",
]
