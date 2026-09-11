"""Strategy registry and built-in strategy resolution."""

from __future__ import annotations

import threading
from typing import Literal, TypeAlias

from proxywhirl.strategies.base import RotationStrategy
from proxywhirl.strategies.cost import CostAwareStrategy
from proxywhirl.strategies.geo import GeoTargetedStrategy
from proxywhirl.strategies.least_used import LeastUsedStrategy
from proxywhirl.strategies.performance import PerformanceBasedStrategy
from proxywhirl.strategies.random import RandomStrategy
from proxywhirl.strategies.round_robin import RoundRobinStrategy
from proxywhirl.strategies.session import SessionPersistenceStrategy
from proxywhirl.strategies.weighted import WeightedStrategy


class StrategyRegistry:
    """
    Singleton registry for custom rotation strategies.

    Allows registration and retrieval of custom strategy implementations,
    enabling plugin architecture for ProxyWhirl.

    Example:
        >>> from proxywhirl.strategies import StrategyRegistry
        >>>
        >>> # Create custom strategy
        >>> class MyStrategy:
        ...     def select(self, pool):
        ...         return pool.get_all_proxies()[0]
        ...     def record_result(self, proxy, success, response_time_ms):
        ...         pass
        >>>
        >>> # Register it
        >>> registry = StrategyRegistry()
        >>> registry.register_strategy("my-strategy", MyStrategy)
        >>>
        >>> # Retrieve and use
        >>> strategy_class = registry.get_strategy("my-strategy")
        >>> strategy = strategy_class()

    Thread Safety:
        Thread-safe singleton implementation using double-checked locking.

    Performance:
        Registration: O(1)
        Retrieval: O(1)
        Validation: <1ms per strategy (SC-010)
    """

    _instance: StrategyRegistry | None = None
    _lock = threading.RLock()

    def __init__(self) -> None:
        """Initialize the registry (called once by __new__)."""
        # These are initialized in __new__ for singleton pattern
        if not hasattr(self, "_strategies"):
            self._strategies: dict[str, type] = {}
        if not hasattr(self, "_registry_lock"):
            self._registry_lock = threading.RLock()

    def __new__(cls) -> StrategyRegistry:
        """Ensure singleton pattern with thread-safe double-checked locking."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._strategies = {}
                    instance._registry_lock = threading.RLock()
                    cls._instance = instance
        return cls._instance

    def register_strategy(self, name: str, strategy_class: type, *, validate: bool = True) -> None:
        """
        Register a custom strategy.

        Args:
            name: Unique name for the strategy (e.g., "my-custom-strategy")
            strategy_class: Strategy class implementing RotationStrategy protocol
            validate: If True (default), validates strategy implements required methods

        Raises:
            ValueError: If strategy name already registered (unless re-registering)
            TypeError: If strategy doesn't implement required protocol methods

        Example:
            >>> class FastStrategy:
            ...     def select(self, pool):
            ...         return pool.get_all_proxies()[0]
            ...     def record_result(self, proxy, success, response_time_ms):
            ...         pass
            >>>
            >>> registry = StrategyRegistry()
            >>> registry.register_strategy("fast", FastStrategy)
        """
        import time

        start_time = time.perf_counter()

        if validate:
            self._validate_strategy(strategy_class)

        with self._registry_lock:
            # Allow re-registration (replacement)
            if name in self._strategies:
                from loguru import logger

                logger.warning(
                    f"Replacing existing strategy registration: {name}",
                    old_class=self._strategies[name].__name__,
                    new_class=strategy_class.__name__,
                )

            self._strategies[name] = strategy_class

        load_time = (time.perf_counter() - start_time) * 1000

        from loguru import logger

        logger.info(
            f"Registered strategy: {name} ({strategy_class.__name__}) in {load_time:.2f}ms",
            strategy_name=name,
            strategy_class=strategy_class.__name__,
            load_time_ms=load_time,
        )

        # Validate SC-010: <1 second load time
        if load_time >= 1000.0:
            logger.warning(
                f"Strategy registration exceeded target time: {load_time:.2f}ms (target: <1000ms)",
                strategy_name=name,
                load_time_ms=load_time,
            )

    def get_strategy(self, name: str) -> type:
        """
        Retrieve a registered strategy class.

        Args:
            name: Strategy name used during registration

        Returns:
            Strategy class (not instance - caller must instantiate)

        Raises:
            KeyError: If strategy name not found in registry

        Example:
            >>> registry = StrategyRegistry()
            >>> strategy_class = registry.get_strategy("my-strategy")
            >>> strategy = strategy_class()  # Instantiate
        """
        with self._registry_lock:
            if name not in self._strategies:
                available = ", ".join(self._strategies.keys()) if self._strategies else "none"
                raise KeyError(
                    f"Strategy '{name}' not found in registry. Available strategies: {available}"
                )
            return self._strategies[name]

    def list_strategies(self) -> list[str]:
        """
        List all registered strategy names.

        Returns:
            List of registered strategy names
        """
        with self._registry_lock:
            return list(self._strategies.keys())

    def unregister_strategy(self, name: str) -> None:
        """
        Remove a strategy from the registry.

        Args:
            name: Strategy name to unregister

        Raises:
            KeyError: If strategy name not found
        """
        with self._registry_lock:
            if name not in self._strategies:
                raise KeyError(f"Strategy '{name}' not found in registry")
            del self._strategies[name]

            from loguru import logger

            logger.info(f"Unregistered strategy: {name}", strategy_name=name)

    def _validate_strategy(self, strategy_class: type) -> None:
        """
        Validate that strategy class implements required protocol.

        Args:
            strategy_class: Strategy class to validate

        Raises:
            TypeError: If required methods are missing
        """
        required_methods = ["select", "record_result"]
        missing_methods = []
        non_callable_methods = []

        for method in required_methods:
            if not hasattr(strategy_class, method):
                missing_methods.append(method)
                continue

            if not callable(getattr(strategy_class, method)):
                non_callable_methods.append(method)

        if missing_methods or non_callable_methods:
            details = []
            if missing_methods:
                details.append(f"missing required methods: {', '.join(missing_methods)}")
            if non_callable_methods:
                details.append(f"non-callable required methods: {', '.join(non_callable_methods)}")
            raise TypeError(
                f"Strategy {strategy_class.__name__} {'; '.join(details)}. "
                "Must implement RotationStrategy protocol."
            )

    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton instance (useful for testing).

        Warning:
            This should only be used in tests. Calling this in production
            will clear all registered strategies.
        """
        with cls._lock:
            cls._instance = None


BuiltinStrategyName: TypeAlias = Literal[
    "round-robin",
    "round_robin",
    "random",
    "weighted",
    "least-used",
    "least_used",
    "performance-based",
    "performance_based",
    "session",
    "session-persistence",
    "session_persistence",
    "geo-targeted",
    "geo_targeted",
    "cost-aware",
    "cost_aware",
]


BUILTIN_STRATEGY_CLASSES: dict[BuiltinStrategyName, type[RotationStrategy]] = {
    "round-robin": RoundRobinStrategy,
    "round_robin": RoundRobinStrategy,
    "random": RandomStrategy,
    "weighted": WeightedStrategy,
    "least-used": LeastUsedStrategy,
    "least_used": LeastUsedStrategy,
    "performance-based": PerformanceBasedStrategy,
    "performance_based": PerformanceBasedStrategy,
    "session": SessionPersistenceStrategy,
    "session-persistence": SessionPersistenceStrategy,
    "session_persistence": SessionPersistenceStrategy,
    "geo-targeted": GeoTargetedStrategy,
    "geo_targeted": GeoTargetedStrategy,
    "cost-aware": CostAwareStrategy,
    "cost_aware": CostAwareStrategy,
}


def resolve_builtin_strategy(name: BuiltinStrategyName) -> RotationStrategy:
    """Resolve a built-in strategy name or alias to a new strategy instance."""
    strategy_class = BUILTIN_STRATEGY_CLASSES.get(name.lower())
    if strategy_class is None:
        valid_options = ", ".join(BUILTIN_STRATEGY_CLASSES)
        raise ValueError(f"Unknown strategy name: {name}. Valid options: {valid_options}")

    return strategy_class()
