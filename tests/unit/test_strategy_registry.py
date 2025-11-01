"""
Tests for StrategyRegistry singleton and plugin system.

Covers:
- Singleton pattern implementation
- Strategy registration and retrieval
- Validation of strategy protocol compliance
- Thread-safe operations
- Error handling
"""

import threading
from typing import Optional

import pytest

from proxywhirl.models import Proxy, ProxyPool, SelectionContext
from proxywhirl.strategies import StrategyRegistry


class TestStrategyRegistry:
    """Test StrategyRegistry singleton and basic operations."""

    def setup_method(self):
        """Reset registry before each test."""
        StrategyRegistry.reset()

    def test_singleton_pattern(self):
        """Test that StrategyRegistry is a true singleton."""
        registry1 = StrategyRegistry()
        registry2 = StrategyRegistry()
        assert registry1 is registry2

    def test_singleton_thread_safe(self):
        """Test singleton creation is thread-safe."""
        instances = []

        def create_instance():
            instances.append(StrategyRegistry())

        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All instances should be the same object
        assert all(inst is instances[0] for inst in instances)

    def test_register_valid_strategy(self):
        """Test registering a valid strategy."""

        class ValidStrategy:
            def select(
                self, pool: ProxyPool, context: Optional[SelectionContext] = None
            ) -> Proxy:
                return pool.get_all_proxies()[0]

            def record_result(
                self, proxy: Proxy, success: bool, response_time_ms: float
            ) -> None:
                pass

        registry = StrategyRegistry()
        registry.register_strategy("valid", ValidStrategy)

        assert "valid" in registry.list_strategies()

    def test_register_strategy_without_validation(self):
        """Test registering strategy without validation."""

        class IncompleteStrategy:
            def select(self, pool: ProxyPool) -> Proxy:
                return pool.get_all_proxies()[0]
            # Missing record_result method

        registry = StrategyRegistry()
        # Should succeed when validation is disabled
        registry.register_strategy("incomplete", IncompleteStrategy, validate=False)
        assert "incomplete" in registry.list_strategies()

    def test_register_invalid_strategy_missing_select(self):
        """Test registering strategy missing select method fails."""

        class MissingSelect:
            def record_result(
                self, proxy: Proxy, success: bool, response_time_ms: float
            ) -> None:
                pass

        registry = StrategyRegistry()
        with pytest.raises(TypeError, match="missing required methods: select"):
            registry.register_strategy("invalid", MissingSelect)

    def test_register_invalid_strategy_missing_record_result(self):
        """Test registering strategy missing record_result method fails."""

        class MissingRecordResult:
            def select(self, pool: ProxyPool) -> Proxy:
                return pool.get_all_proxies()[0]

        registry = StrategyRegistry()
        with pytest.raises(TypeError, match="missing required methods: record_result"):
            registry.register_strategy("invalid", MissingRecordResult)

    def test_register_strategy_replacement(self):
        """Test that re-registering a strategy replaces the old one."""

        class StrategyV1:
            version = 1

            def select(self, pool: ProxyPool) -> Proxy:
                return pool.get_all_proxies()[0]

            def record_result(
                self, proxy: Proxy, success: bool, response_time_ms: float
            ) -> None:
                pass

        class StrategyV2:
            version = 2

            def select(self, pool: ProxyPool) -> Proxy:
                return pool.get_all_proxies()[0]

            def record_result(
                self, proxy: Proxy, success: bool, response_time_ms: float
            ) -> None:
                pass

        registry = StrategyRegistry()
        registry.register_strategy("test", StrategyV1, validate=False)
        registry.register_strategy("test", StrategyV2, validate=False)

        retrieved_class = registry.get_strategy("test")
        assert retrieved_class.version == 2  # Should be the newer version

    def test_get_strategy(self):
        """Test retrieving a registered strategy."""

        class TestStrategy:
            def select(self, pool: ProxyPool) -> Proxy:
                return pool.get_all_proxies()[0]

            def record_result(
                self, proxy: Proxy, success: bool, response_time_ms: float
            ) -> None:
                pass

        registry = StrategyRegistry()
        registry.register_strategy("test", TestStrategy, validate=False)

        retrieved = registry.get_strategy("test")
        assert retrieved is TestStrategy

    def test_get_nonexistent_strategy(self):
        """Test retrieving non-existent strategy raises KeyError."""
        registry = StrategyRegistry()
        with pytest.raises(KeyError, match="Strategy 'nonexistent' not found"):
            registry.get_strategy("nonexistent")

    def test_list_strategies_empty(self):
        """Test listing strategies when registry is empty."""
        registry = StrategyRegistry()
        assert registry.list_strategies() == []

    def test_list_strategies_multiple(self):
        """Test listing multiple registered strategies."""

        class Strategy1:
            def select(self, pool: ProxyPool) -> Proxy:
                return pool.get_all_proxies()[0]

            def record_result(
                self, proxy: Proxy, success: bool, response_time_ms: float
            ) -> None:
                pass

        class Strategy2:
            def select(self, pool: ProxyPool) -> Proxy:
                return pool.get_all_proxies()[0]

            def record_result(
                self, proxy: Proxy, success: bool, response_time_ms: float
            ) -> None:
                pass

        registry = StrategyRegistry()
        registry.register_strategy("strat1", Strategy1, validate=False)
        registry.register_strategy("strat2", Strategy2, validate=False)

        strategies = registry.list_strategies()
        assert "strat1" in strategies
        assert "strat2" in strategies
        assert len(strategies) == 2

    def test_unregister_strategy(self):
        """Test unregistering a strategy."""

        class TestStrategy:
            def select(self, pool: ProxyPool) -> Proxy:
                return pool.get_all_proxies()[0]

            def record_result(
                self, proxy: Proxy, success: bool, response_time_ms: float
            ) -> None:
                pass

        registry = StrategyRegistry()
        registry.register_strategy("test", TestStrategy, validate=False)
        assert "test" in registry.list_strategies()

        registry.unregister_strategy("test")
        assert "test" not in registry.list_strategies()

    def test_unregister_nonexistent_strategy(self):
        """Test unregistering non-existent strategy raises KeyError."""
        registry = StrategyRegistry()
        with pytest.raises(KeyError, match="Strategy 'nonexistent' not found"):
            registry.unregister_strategy("nonexistent")

    def test_registry_thread_safe_operations(self):
        """Test that registry operations are thread-safe."""

        class TestStrategy:
            def select(self, pool: ProxyPool) -> Proxy:
                return pool.get_all_proxies()[0]

            def record_result(
                self, proxy: Proxy, success: bool, response_time_ms: float
            ) -> None:
                pass

        registry = StrategyRegistry()
        errors = []

        def register_many():
            try:
                for i in range(10):
                    registry.register_strategy(
                        f"strat{threading.current_thread().name}_{i}",
                        TestStrategy,
                        validate=False,
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=register_many, name=f"T{i}") for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have 50 strategies registered (5 threads * 10 registrations each)
        assert len(registry.list_strategies()) == 50
        assert len(errors) == 0

    def test_validate_strategy_with_missing_methods(self):
        """Test _validate_strategy method with invalid strategy."""

        class InvalidStrategy:
            pass

        registry = StrategyRegistry()
        with pytest.raises(
            TypeError, match="missing required methods: select, record_result"
        ):
            registry._validate_strategy(InvalidStrategy)

    def test_reset_registry(self):
        """Test resetting the registry."""

        class TestStrategy:
            def select(self, pool: ProxyPool) -> Proxy:
                return pool.get_all_proxies()[0]

            def record_result(
                self, proxy: Proxy, success: bool, response_time_ms: float
            ) -> None:
                pass

        registry = StrategyRegistry()
        registry.register_strategy("test", TestStrategy, validate=False)
        assert len(registry.list_strategies()) > 0

        StrategyRegistry.reset()

        # After reset, should get a new instance with empty registry
        new_registry = StrategyRegistry()
        assert len(new_registry.list_strategies()) == 0
