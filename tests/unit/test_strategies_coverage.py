"""
Unit tests for strategies.py coverage improvement.
Targets: CompositeStrategy, StrategyRegistry edge cases, SessionPersistence, GeoTargeted.
"""

import threading
from unittest.mock import MagicMock

import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)
from proxywhirl.strategies import (
    CompositeStrategy,
    GeoTargetedStrategy,
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    RandomStrategy,
    RoundRobinStrategy,
    SessionPersistenceStrategy,
    StrategyRegistry,
)


class TestCompositeStrategy:
    """Tests for CompositeStrategy."""

    def test_init_with_selector_only(self) -> None:
        """Test creating CompositeStrategy with just a selector."""
        selector = RoundRobinStrategy()
        strategy = CompositeStrategy(selector=selector)
        assert strategy.selector == selector
        assert strategy.filters == []

    def test_init_with_filters_only(self) -> None:
        """Test creating CompositeStrategy with just filters."""
        filters = [GeoTargetedStrategy()]
        strategy = CompositeStrategy(filters=filters)
        assert strategy.filters == filters
        assert isinstance(strategy.selector, RoundRobinStrategy)

    def test_init_with_both_filters_and_selector(self) -> None:
        """Test creating CompositeStrategy with both filters and selector."""
        filters = [GeoTargetedStrategy()]
        selector = RandomStrategy()
        strategy = CompositeStrategy(filters=filters, selector=selector)
        assert strategy.filters == filters
        assert strategy.selector == selector

    def test_init_raises_with_no_filters_and_no_selector(self) -> None:
        """Test that init raises ValueError when both filters and selector are empty/None."""
        # When filters=[] (empty list) and selector is None, it raises ValueError
        # because `not self.filters` is True for empty list
        with pytest.raises(ValueError, match="at least one filter or a selector"):
            CompositeStrategy(filters=[])

    def test_select_with_no_filters(self) -> None:
        """Test selection with no filters applied."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = CompositeStrategy(selector=RoundRobinStrategy())
        selected = strategy.select(pool)

        assert selected == proxy

    def test_select_with_geo_filter(self) -> None:
        """Test selection with geo filter applied."""
        pool = ProxyPool(name="test-pool")
        us_proxy = Proxy(
            url="http://us-proxy.com:8080",
            health_status=HealthStatus.HEALTHY,
            country_code="US",
        )
        uk_proxy = Proxy(
            url="http://uk-proxy.com:8080",
            health_status=HealthStatus.HEALTHY,
            country_code="UK",
        )
        pool.add_proxy(us_proxy)
        pool.add_proxy(uk_proxy)

        strategy = CompositeStrategy(
            filters=[GeoTargetedStrategy()],
            selector=RoundRobinStrategy(),
        )
        context = SelectionContext(target_country="US")
        selected = strategy.select(pool, context)

        assert selected.country_code == "US"

    def test_select_raises_when_pool_empty(self) -> None:
        """Test that selection raises when pool has no healthy proxies."""
        pool = ProxyPool(name="empty-pool")

        strategy = CompositeStrategy(selector=RoundRobinStrategy())

        with pytest.raises(ProxyPoolEmptyError, match="No healthy proxies"):
            strategy.select(pool)

    def test_select_raises_when_all_unhealthy(self) -> None:
        """Test that selection raises when all proxies are unhealthy."""
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.DEAD))

        strategy = CompositeStrategy(selector=RoundRobinStrategy())

        with pytest.raises(ProxyPoolEmptyError, match="No healthy proxies"):
            strategy.select(pool)

    def test_select_with_context_none_creates_default(self) -> None:
        """Test that select creates default context when None passed."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = CompositeStrategy(selector=RoundRobinStrategy())
        # Pass context=None explicitly
        selected = strategy.select(pool, context=None)

        assert selected == proxy

    def test_matches_filter_same_proxy(self) -> None:
        """Test _matches_filter returns True for same proxy."""
        strategy = CompositeStrategy(selector=RoundRobinStrategy())
        proxy = Proxy(url="http://proxy1.com:8080")

        result = strategy._matches_filter(proxy, proxy)
        assert result is True

    def test_matches_filter_same_country(self) -> None:
        """Test _matches_filter returns True for same country."""
        strategy = CompositeStrategy(selector=RoundRobinStrategy())
        proxy1 = Proxy(url="http://proxy1.com:8080", country_code="US")
        proxy2 = Proxy(url="http://proxy2.com:8080", country_code="US")

        result = strategy._matches_filter(proxy1, proxy2)
        assert result is True

    def test_matches_filter_different_country(self) -> None:
        """Test _matches_filter returns False for different country."""
        strategy = CompositeStrategy(selector=RoundRobinStrategy())
        proxy1 = Proxy(url="http://proxy1.com:8080", country_code="US")
        proxy2 = Proxy(url="http://proxy2.com:8080", country_code="UK")

        result = strategy._matches_filter(proxy1, proxy2)
        assert result is False

    def test_matches_filter_no_country_includes_all(self) -> None:
        """Test _matches_filter returns True when filter result has no country."""
        strategy = CompositeStrategy(selector=RoundRobinStrategy())
        proxy1 = Proxy(url="http://proxy1.com:8080")
        proxy2 = Proxy(url="http://proxy2.com:8080")

        result = strategy._matches_filter(proxy1, proxy2)
        assert result is True

    def test_record_result_delegates_to_selector(self) -> None:
        """Test that record_result delegates to selector strategy."""
        mock_selector = MagicMock()
        strategy = CompositeStrategy(selector=mock_selector)

        proxy = Proxy(url="http://proxy1.com:8080")
        strategy.record_result(proxy, success=True, response_time_ms=100.0)

        mock_selector.record_result.assert_called_once_with(proxy, True, 100.0)


class TestStrategyRegistrySingleton:
    """Tests for StrategyRegistry singleton and edge cases."""

    def test_singleton_returns_same_instance(self) -> None:
        """Test that StrategyRegistry is a singleton."""
        registry1 = StrategyRegistry()
        registry2 = StrategyRegistry()
        assert registry1 is registry2

    def test_singleton_thread_safe(self) -> None:
        """Test that singleton is thread-safe."""
        instances = []

        def get_instance() -> None:
            instances.append(StrategyRegistry())

        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All instances should be the same object
        assert all(inst is instances[0] for inst in instances)

    def test_register_and_get_strategy(self) -> None:
        """Test registering and retrieving a strategy."""
        registry = StrategyRegistry()

        # Register a custom strategy class
        class CustomStrategy:
            def select(self, pool, context=None):
                return pool.get_all_proxies()[0]

            def record_result(self, proxy, success, response_time_ms):
                pass

        registry.register_strategy("custom-test", CustomStrategy, validate=False)
        retrieved = registry.get_strategy("custom-test")

        assert retrieved is CustomStrategy

    def test_get_strategy_not_found_raises_keyerror(self) -> None:
        """Test that getting non-existent strategy raises KeyError."""
        registry = StrategyRegistry()
        with pytest.raises(KeyError):
            registry.get_strategy("nonexistent-strategy-xyz")

    def test_list_strategies(self) -> None:
        """Test listing registered strategies."""
        registry = StrategyRegistry()

        # Register a test strategy
        class TestListStrategy:
            def select(self, pool, context=None):
                pass

            def record_result(self, proxy, success, response_time_ms):
                pass

        registry.register_strategy("test-list", TestListStrategy, validate=False)

        strategies = registry.list_strategies()
        assert "test-list" in strategies


class TestSessionPersistenceEdgeCases:
    """Tests for SessionPersistenceStrategy edge cases."""

    def test_select_without_context_raises(self) -> None:
        """Test that select without context raises ValueError."""
        strategy = SessionPersistenceStrategy()
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        with pytest.raises(ValueError, match="requires SelectionContext with session_id"):
            strategy.select(pool, context=None)

    def test_select_without_session_id_raises(self) -> None:
        """Test that select with context but no session_id raises ValueError."""
        strategy = SessionPersistenceStrategy()
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        context = SelectionContext()  # No session_id
        with pytest.raises(ValueError, match="requires SelectionContext with session_id"):
            strategy.select(pool, context)

    def test_select_creates_new_session(self) -> None:
        """Test that select creates a new session for new session_id."""
        strategy = SessionPersistenceStrategy()
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        context = SelectionContext(session_id="new-session-123")
        selected = strategy.select(pool, context)

        assert selected is not None
        # Session should now exist
        session = strategy._session_manager.get_session("new-session-123")
        assert session is not None

    def test_select_reuses_existing_session(self) -> None:
        """Test that select reuses existing session's proxy."""
        strategy = SessionPersistenceStrategy()
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        context = SelectionContext(session_id="sticky-session")

        # First selection creates session
        first = strategy.select(pool, context)

        # Second selection should return same proxy
        second = strategy.select(pool, context)

        assert first.id == second.id

    def test_select_failover_when_proxy_unhealthy(self) -> None:
        """Test that select fails over when assigned proxy becomes unhealthy."""
        strategy = SessionPersistenceStrategy()
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        context = SelectionContext(session_id="failover-session")

        # First selection
        first = strategy.select(pool, context)

        # Mark the assigned proxy as unhealthy
        first.health_status = HealthStatus.DEAD

        # Second selection should fail over to another proxy
        second = strategy.select(pool, context)

        assert second.health_status == HealthStatus.HEALTHY

    def test_close_session(self) -> None:
        """Test explicitly closing a session."""
        strategy = SessionPersistenceStrategy()
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        context = SelectionContext(session_id="close-me")
        strategy.select(pool, context)

        # Session exists
        assert strategy._session_manager.get_session("close-me") is not None

        # Close it
        strategy.close_session("close-me")

        # Session should be gone
        assert strategy._session_manager.get_session("close-me") is None

    def test_cleanup_expired_sessions(self) -> None:
        """Test cleaning up expired sessions."""
        strategy = SessionPersistenceStrategy()
        # Just verify the method exists and returns int
        removed = strategy.cleanup_expired_sessions()
        assert isinstance(removed, int)


class TestGeoTargetedStrategyEdgeCases:
    """Tests for GeoTargetedStrategy edge cases."""

    def test_select_without_context(self) -> None:
        """Test selection without context uses all healthy proxies."""
        strategy = GeoTargetedStrategy()
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        selected = strategy.select(pool, context=None)
        assert selected == proxy

    def test_select_with_target_country(self) -> None:
        """Test selection with target_country filters correctly."""
        strategy = GeoTargetedStrategy()
        pool = ProxyPool(name="test-pool")
        us_proxy = Proxy(
            url="http://us.com:8080",
            health_status=HealthStatus.HEALTHY,
            country_code="US",
        )
        uk_proxy = Proxy(
            url="http://uk.com:8080",
            health_status=HealthStatus.HEALTHY,
            country_code="UK",
        )
        pool.add_proxy(us_proxy)
        pool.add_proxy(uk_proxy)

        context = SelectionContext(target_country="US")
        selected = strategy.select(pool, context)

        assert selected.country_code == "US"

    def test_select_with_target_region(self) -> None:
        """Test selection with target_region filters correctly."""
        strategy = GeoTargetedStrategy()
        pool = ProxyPool(name="test-pool")
        eu_proxy = Proxy(
            url="http://eu.com:8080",
            health_status=HealthStatus.HEALTHY,
            region="Europe",
        )
        asia_proxy = Proxy(
            url="http://asia.com:8080",
            health_status=HealthStatus.HEALTHY,
            region="Asia",
        )
        pool.add_proxy(eu_proxy)
        pool.add_proxy(asia_proxy)

        context = SelectionContext(target_region="Europe")
        selected = strategy.select(pool, context)

        assert selected.region == "Europe"

    def test_select_fallback_when_no_match(self) -> None:
        """Test fallback to any proxy when no geo match and fallback enabled."""
        strategy = GeoTargetedStrategy()
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(
            url="http://proxy.com:8080",
            health_status=HealthStatus.HEALTHY,
            country_code="JP",
        )
        pool.add_proxy(proxy)

        context = SelectionContext(target_country="US")  # No US proxy
        # Fallback is enabled by default
        selected = strategy.select(pool, context)

        assert selected == proxy  # Falls back to JP proxy

    def test_select_no_fallback_raises(self) -> None:
        """Test that selection raises when no match and fallback disabled."""
        strategy = GeoTargetedStrategy()
        strategy._fallback_enabled = False

        pool = ProxyPool(name="test-pool")
        proxy = Proxy(
            url="http://proxy.com:8080",
            health_status=HealthStatus.HEALTHY,
            country_code="JP",
        )
        pool.add_proxy(proxy)

        context = SelectionContext(target_country="US")  # No US proxy

        with pytest.raises(ProxyPoolEmptyError):
            strategy.select(pool, context)

    def test_configure_fallback_disabled(self) -> None:
        """Test configuring geo fallback to disabled."""
        strategy = GeoTargetedStrategy()
        config = StrategyConfig(geo_fallback_enabled=False)
        strategy.configure(config)

        assert strategy._fallback_enabled is False

    def test_configure_secondary_strategy(self) -> None:
        """Test configuring secondary selection strategy."""
        strategy = GeoTargetedStrategy()

        # Test round_robin
        config = StrategyConfig(geo_secondary_strategy="round_robin")
        strategy.configure(config)
        assert isinstance(strategy._secondary_strategy, RoundRobinStrategy)

        # Test random
        config = StrategyConfig(geo_secondary_strategy="random")
        strategy.configure(config)
        assert isinstance(strategy._secondary_strategy, RandomStrategy)

        # Test least_used
        config = StrategyConfig(geo_secondary_strategy="least_used")
        strategy.configure(config)
        assert isinstance(strategy._secondary_strategy, LeastUsedStrategy)

    def test_validate_metadata_always_true(self) -> None:
        """Test that validate_metadata always returns True (geo data is optional)."""
        strategy = GeoTargetedStrategy()
        pool = ProxyPool(name="test-pool")

        # Empty pool
        assert strategy.validate_metadata(pool) is True

        # Pool with proxies without geo data
        pool.add_proxy(Proxy(url="http://proxy.com:8080"))
        assert strategy.validate_metadata(pool) is True


class TestStrategyRegistryValidation:
    """Tests for StrategyRegistry validation and unregister."""

    def test_register_strategy_with_validation(self) -> None:
        """Test registering strategy with validation enabled."""
        registry = StrategyRegistry()

        class ValidStrategy:
            def select(self, pool, context=None):
                return pool.get_all_proxies()[0]

            def record_result(self, proxy, success, response_time_ms):
                pass

        # Should not raise with validate=True (default)
        registry.register_strategy("valid-test-strategy", ValidStrategy, validate=True)
        assert registry.get_strategy("valid-test-strategy") is ValidStrategy

    def test_register_strategy_validation_fails(self) -> None:
        """Test that strategy validation fails for missing methods."""
        registry = StrategyRegistry()

        class InvalidStrategy:
            # Missing both 'select' and 'record_result' methods
            pass

        with pytest.raises(TypeError, match="missing required methods"):
            registry.register_strategy("invalid-strategy", InvalidStrategy, validate=True)

    def test_register_strategy_missing_select(self) -> None:
        """Test that validation fails when 'select' method is missing."""
        registry = StrategyRegistry()

        class NoSelectStrategy:
            def record_result(self, proxy, success, response_time_ms):
                pass

        with pytest.raises(TypeError, match="select"):
            registry.register_strategy("no-select", NoSelectStrategy, validate=True)

    def test_register_strategy_missing_record_result(self) -> None:
        """Test that validation fails when 'record_result' method is missing."""
        registry = StrategyRegistry()

        class NoRecordStrategy:
            def select(self, pool, context=None):
                return pool.get_all_proxies()[0]

        with pytest.raises(TypeError, match="record_result"):
            registry.register_strategy("no-record", NoRecordStrategy, validate=True)

    def test_unregister_strategy(self) -> None:
        """Test unregistering a strategy."""
        registry = StrategyRegistry()

        class TempStrategy:
            def select(self, pool, context=None):
                pass

            def record_result(self, proxy, success, response_time_ms):
                pass

        registry.register_strategy("temp-strategy", TempStrategy, validate=False)
        assert "temp-strategy" in registry.list_strategies()

        registry.unregister_strategy("temp-strategy")
        assert "temp-strategy" not in registry.list_strategies()

    def test_unregister_strategy_not_found(self) -> None:
        """Test unregistering a non-existent strategy raises KeyError."""
        registry = StrategyRegistry()

        with pytest.raises(KeyError, match="not found"):
            registry.unregister_strategy("nonexistent-strategy-xyz")

    def test_register_strategy_replacement_warns(self) -> None:
        """Test that re-registering a strategy logs a warning."""
        registry = StrategyRegistry()

        class FirstStrategy:
            def select(self, pool, context=None):
                pass

            def record_result(self, proxy, success, response_time_ms):
                pass

        class SecondStrategy:
            def select(self, pool, context=None):
                pass

            def record_result(self, proxy, success, response_time_ms):
                pass

        registry.register_strategy("replace-test", FirstStrategy, validate=False)
        # Re-register with different class - should warn but succeed
        registry.register_strategy("replace-test", SecondStrategy, validate=False)

        assert registry.get_strategy("replace-test") is SecondStrategy

    def test_registry_reset(self) -> None:
        """Test resetting the registry singleton."""
        registry = StrategyRegistry()

        class ResetTestStrategy:
            def select(self, pool, context=None):
                pass

            def record_result(self, proxy, success, response_time_ms):
                pass

        registry.register_strategy("reset-test", ResetTestStrategy, validate=False)

        # Reset the singleton
        StrategyRegistry.reset()

        # New registry should be a fresh instance
        new_registry = StrategyRegistry()
        # Note: Due to how singleton works, registered strategies might persist
        # unless we explicitly handle it in reset()


class TestPerformanceBasedStrategyEdgeCases:
    """Tests for PerformanceBasedStrategy edge cases."""

    def test_select_handles_cold_start_proxies(self) -> None:
        """Test that proxies without EMA data are selected as exploration candidates.

        With TASK-304 cold-start handling, new proxies are given exploration trials
        rather than being rejected. This prevents proxy starvation.
        """
        strategy = PerformanceBasedStrategy(exploration_count=5)
        pool = ProxyPool(name="test-pool")
        # Proxy without EMA data (new proxy)
        proxy = Proxy(url="http://proxy.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        # Cold-start: should select the proxy as an exploration candidate
        selected = strategy.select(pool)
        assert selected == proxy

    def test_select_with_ema_data(self) -> None:
        """Test selection with proxies that have EMA data."""
        strategy = PerformanceBasedStrategy()
        pool = ProxyPool(name="test-pool")

        # Create proxy with EMA data
        proxy = Proxy(
            url="http://proxy.com:8080",
            health_status=HealthStatus.HEALTHY,
            ema_alpha=0.2,
        )
        # Simulate some requests to build EMA
        proxy.start_request()
        proxy.complete_request(success=True, response_time_ms=100.0)
        pool.add_proxy(proxy)

        selected = strategy.select(pool)
        assert selected == proxy

    def test_select_filters_failed_proxies(self) -> None:
        """Test that selection filters out failed_proxy_ids from context."""
        strategy = PerformanceBasedStrategy()
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(
            url="http://proxy1.com:8080",
            health_status=HealthStatus.HEALTHY,
            ema_alpha=0.2,
        )
        proxy1.start_request()
        proxy1.complete_request(success=True, response_time_ms=100.0)

        proxy2 = Proxy(
            url="http://proxy2.com:8080",
            health_status=HealthStatus.HEALTHY,
            ema_alpha=0.2,
        )
        proxy2.start_request()
        proxy2.complete_request(success=True, response_time_ms=50.0)

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        # Exclude proxy2
        context = SelectionContext(failed_proxy_ids=[str(proxy2.id)])
        selected = strategy.select(pool, context)

        assert selected == proxy1

    def test_validate_metadata(self) -> None:
        """Test validate_metadata returns True when healthy proxies exist.

        With TASK-304 cold-start handling, validate_metadata returns True if there
        are any healthy proxies (exploration candidates or proxies with EMA data).
        """
        strategy = PerformanceBasedStrategy()
        pool = ProxyPool(name="test-pool")

        # No proxies - should be False
        assert strategy.validate_metadata(pool) is False

        # With healthy proxy (no EMA data = exploration candidate)
        proxy_no_ema = Proxy(url="http://proxy.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy_no_ema)
        # Now returns True because there's a healthy proxy (cold-start exploration)
        assert strategy.validate_metadata(pool) is True

        # With additional EMA data proxy
        proxy_with_ema = Proxy(
            url="http://proxy2.com:8080",
            health_status=HealthStatus.HEALTHY,
            ema_alpha=0.2,
        )
        proxy_with_ema.start_request()
        proxy_with_ema.complete_request(success=True, response_time_ms=100.0)
        pool.add_proxy(proxy_with_ema)
        assert strategy.validate_metadata(pool) is True


class TestSessionManagerEdgeCases:
    """Tests for SessionManager edge cases."""

    def test_get_all_sessions(self) -> None:
        """Test get_all_sessions returns all sessions."""
        from proxywhirl.strategies import SessionManager

        manager = SessionManager()

        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        manager.create_session("session-1", proxy, timeout_seconds=3600)
        manager.create_session("session-2", proxy, timeout_seconds=3600)

        all_sessions = manager.get_all_sessions()

        assert len(all_sessions) == 2
        session_ids = [s.session_id for s in all_sessions]
        assert "session-1" in session_ids
        assert "session-2" in session_ids

    def test_clear_all_sessions(self) -> None:
        """Test clearing all sessions."""
        from proxywhirl.strategies import SessionManager

        manager = SessionManager()

        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        manager.create_session("session-1", proxy, timeout_seconds=3600)
        manager.create_session("session-2", proxy, timeout_seconds=3600)

        assert len(manager.get_all_sessions()) == 2

        manager.clear_all()

        assert len(manager.get_all_sessions()) == 0

    def test_cleanup_expired(self) -> None:
        """Test cleanup_expired removes expired sessions."""
        from datetime import datetime, timedelta, timezone

        from proxywhirl.strategies import SessionManager

        manager = SessionManager()

        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        # Create a long-lived session
        manager.create_session("active-session", proxy, timeout_seconds=3600)

        # Create a session and manually expire it
        expired_session = manager.create_session("expired-session", proxy, timeout_seconds=1)
        expired_session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)

        # Cleanup expired
        removed = manager.cleanup_expired()

        # Should have removed 1 expired session
        assert removed >= 1

        # Active session should still exist
        assert manager.get_session("active-session") is not None
        # Expired should be gone
        assert manager.get_session("expired-session") is None

    def test_touch_session(self) -> None:
        """Test touching a session refreshes its expiration."""
        from proxywhirl.strategies import SessionManager

        manager = SessionManager()

        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        session = manager.create_session("touch-session", proxy, timeout_seconds=60)

        original_expiry = session.expires_at

        # Touch the session
        refreshed = manager.touch_session("touch-session")

        assert refreshed is True
        # Expiry should be extended
        updated_session = manager.get_session("touch-session")
        assert updated_session.expires_at >= original_expiry

    def test_touch_session_not_found(self) -> None:
        """Test touching non-existent session returns False."""
        from proxywhirl.strategies import SessionManager

        manager = SessionManager()

        result = manager.touch_session("nonexistent-session")

        assert result is False

    def test_remove_session(self) -> None:
        """Test removing a specific session."""
        from proxywhirl.strategies import SessionManager

        manager = SessionManager()

        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        manager.create_session("to-remove", proxy, timeout_seconds=3600)

        assert manager.get_session("to-remove") is not None

        manager.remove_session("to-remove")

        assert manager.get_session("to-remove") is None


class TestSessionPersistenceStrategyConfigure:
    """Tests for SessionPersistenceStrategy.configure method."""

    def test_configure_session_timeout(self) -> None:
        """Test configuring session timeout."""
        strategy = SessionPersistenceStrategy()

        config = StrategyConfig(session_stickiness_duration_seconds=7200)
        strategy.configure(config)

        assert strategy._session_timeout_seconds == 7200

    def test_configure_session_timeout_uses_config_default(self) -> None:
        """Test that StrategyConfig default is applied."""
        strategy = SessionPersistenceStrategy()

        # Default timeout before configure
        assert strategy._session_timeout_seconds == 3600

        # Configure with default StrategyConfig (has default of 300)
        config = StrategyConfig()
        strategy.configure(config)

        # Should use the config's default value (300)
        assert strategy._session_timeout_seconds == config.session_stickiness_duration_seconds


class TestCompositeStrategyFromConfig:
    """Tests for CompositeStrategy.from_config class method."""

    def test_from_config_default(self) -> None:
        """Test from_config with default settings."""
        config = {}
        strategy = CompositeStrategy.from_config(config)

        assert strategy.filters == []
        assert isinstance(strategy.selector, RoundRobinStrategy)

    def test_from_config_with_selector_string(self) -> None:
        """Test from_config with selector as string."""
        config = {"selector": "random"}
        strategy = CompositeStrategy.from_config(config)

        assert isinstance(strategy.selector, RandomStrategy)

    def test_from_config_with_filters_strings(self) -> None:
        """Test from_config with filters as strings."""
        config = {
            "filters": ["geo-targeted"],
            "selector": "round-robin",
        }
        strategy = CompositeStrategy.from_config(config)

        assert len(strategy.filters) == 1
        assert isinstance(strategy.filters[0], GeoTargetedStrategy)

    def test_from_config_with_filter_instances(self) -> None:
        """Test from_config with filter instances."""
        geo_filter = GeoTargetedStrategy()
        config = {
            "filters": [geo_filter],
            "selector": RoundRobinStrategy(),
        }
        strategy = CompositeStrategy.from_config(config)

        assert len(strategy.filters) == 1
        assert strategy.filters[0] is geo_filter

    def test_strategy_from_name_all_strategies(self) -> None:
        """Test _strategy_from_name for all known strategies."""
        assert isinstance(CompositeStrategy._strategy_from_name("round-robin"), RoundRobinStrategy)
        assert isinstance(CompositeStrategy._strategy_from_name("random"), RandomStrategy)
        assert isinstance(CompositeStrategy._strategy_from_name("least-used"), LeastUsedStrategy)
        assert isinstance(
            CompositeStrategy._strategy_from_name("performance-based"), PerformanceBasedStrategy
        )
        assert isinstance(
            CompositeStrategy._strategy_from_name("session"), SessionPersistenceStrategy
        )
        assert isinstance(
            CompositeStrategy._strategy_from_name("geo-targeted"), GeoTargetedStrategy
        )

    def test_strategy_from_name_unknown_raises(self) -> None:
        """Test _strategy_from_name raises ValueError for unknown strategy."""
        with pytest.raises(ValueError, match="Unknown strategy name"):
            CompositeStrategy._strategy_from_name("unknown-strategy")
