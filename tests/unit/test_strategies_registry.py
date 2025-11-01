"""Unit tests for StrategyRegistry in proxywhirl.strategies."""

import pytest

from proxywhirl.strategies import StrategyRegistry


class DummyValidStrategy:
    def select(self, _pool):
        return None

    def record_result(self, _proxy, _success, _response_time_ms):
        pass


class DummyMissingSelect:
    def record_result(self, _proxy, _success, _response_time_ms):
        pass


class DummyMissingRecord:
    def select(self, _pool):
        return None


def test_singleton_behavior_reset():
    r1 = StrategyRegistry()
    r2 = StrategyRegistry()
    assert r1 is r2

    # Reset should replace the singleton instance
    StrategyRegistry.reset()
    r3 = StrategyRegistry()
    assert r3 is not r1


def test_register_get_list_unregister_and_replacement(caplog):
    registry = StrategyRegistry()
    registry.reset()

    # Initially empty
    assert registry.list_strategies() == []

    # Register a strategy
    registry.register_strategy("dummy", DummyValidStrategy)
    assert "dummy" in registry.list_strategies()

    # Get returns the registered class
    cls = registry.get_strategy("dummy")
    assert cls is DummyValidStrategy

    # Re-register same name with replacement should warn but succeed
    with caplog.at_level("WARNING"):
        registry.register_strategy("dummy", DummyValidStrategy)
    assert "dummy" in registry.list_strategies()

    # Unregister removes it
    registry.unregister_strategy("dummy")
    assert "dummy" not in registry.list_strategies()

    # Unregistering missing raises KeyError
    with pytest.raises(KeyError):
        registry.unregister_strategy("nonexistent")


def test_get_strategy_missing_raises_keyerror():
    registry = StrategyRegistry()
    registry.reset()

    with pytest.raises(KeyError):
        registry.get_strategy("does-not-exist")


def test_validate_strategy_accepts_valid_class():
    registry = StrategyRegistry()
    registry.reset()

    # Should not raise for valid strategy when registering with validation
    registry.register_strategy("valid", DummyValidStrategy, validate=True)
    # cleanup
    registry.unregister_strategy("valid")


def test_validate_strategy_missing_methods_raises():
    registry = StrategyRegistry()
    registry.reset()

    with pytest.raises(TypeError):
        registry.register_strategy("bad1", DummyMissingSelect, validate=True)

    with pytest.raises(TypeError):
        registry.register_strategy("bad2", DummyMissingRecord, validate=True)
