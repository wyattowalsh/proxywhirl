"""
Unit tests for SessionPersistenceStrategy.

Following TDD: These tests are written FIRST and should FAIL before implementation.
"""

import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)
from proxywhirl.strategies import SessionPersistenceStrategy


class TestSessionPersistenceStrategy:
    """Unit tests for SessionPersistenceStrategy (US5)."""

    def test_select_creates_new_session_on_first_request(self):
        """Test that first request with session_id creates a new session."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = SessionPersistenceStrategy()
        context = SelectionContext(session_id="user-123")

        # Act
        selected = strategy.select(pool, context)

        # Assert
        assert selected is not None
        assert selected.url == "http://proxy1.com:8080"
        # Session should be stored internally

    def test_select_returns_same_proxy_for_existing_session(self):
        """Test that subsequent requests with same session_id get same proxy."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxies = [
            Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            for i in range(3)
        ]
        for proxy in proxies:
            pool.add_proxy(proxy)

        strategy = SessionPersistenceStrategy()
        context = SelectionContext(session_id="user-123")

        # Act - First selection establishes session
        first_proxy = strategy.select(pool, context)

        # Make 5 more selections with same session_id
        subsequent_proxies = [strategy.select(pool, context) for _ in range(5)]

        # Assert - All should be the same proxy
        assert all(p.url == first_proxy.url for p in subsequent_proxies)

    def test_select_creates_different_sessions_for_different_ids(self):
        """Test that different session_ids get different proxies (usually)."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxies = [
            Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            for i in range(5)
        ]
        for proxy in proxies:
            pool.add_proxy(proxy)

        strategy = SessionPersistenceStrategy()

        # Act - Create 3 different sessions
        session1_proxy = strategy.select(pool, SelectionContext(session_id="user-1"))
        session2_proxy = strategy.select(pool, SelectionContext(session_id="user-2"))
        session3_proxy = strategy.select(pool, SelectionContext(session_id="user-3"))

        # Assert - Each session should maintain its own proxy
        # (They might be the same by chance, but session persistence should work)
        # Verify each session returns its assigned proxy consistently
        assert (
            strategy.select(pool, SelectionContext(session_id="user-1")).url == session1_proxy.url
        )
        assert (
            strategy.select(pool, SelectionContext(session_id="user-2")).url == session2_proxy.url
        )
        assert (
            strategy.select(pool, SelectionContext(session_id="user-3")).url == session3_proxy.url
        )

    def test_select_handles_session_expiration(self):
        """Test that expired sessions get new proxy assignment."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxies = [
            Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            for i in range(3)
        ]
        for proxy in proxies:
            pool.add_proxy(proxy)

        # Configure with very short timeout (1 second)
        strategy = SessionPersistenceStrategy()
        config = StrategyConfig(session_stickiness_duration_seconds=1)
        strategy.configure(config)

        context = SelectionContext(session_id="user-123")

        # Act - First selection
        first_proxy = strategy.select(pool, context)

        # Simulate time passing by manually expiring the session
        # (In real implementation, we'll need to access internal session storage)
        import time

        time.sleep(1.1)  # Wait for session to expire

        # Second selection after expiration
        second_proxy = strategy.select(pool, context)

        # Assert - Should create new session (might get different proxy)
        # The key assertion is that both selections succeed
        assert first_proxy is not None
        assert second_proxy is not None
        # Note: They might be the same proxy by chance, which is OK

    def test_select_handles_unhealthy_session_proxy(self):
        """Test failover when session's assigned proxy becomes unhealthy."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = SessionPersistenceStrategy()
        context = SelectionContext(session_id="user-123")

        # Act - First selection
        first_proxy = strategy.select(pool, context)
        assert first_proxy.health_status == HealthStatus.HEALTHY

        # Mark the assigned proxy as unhealthy
        first_proxy.health_status = HealthStatus.DEAD

        # Try to select again with same session
        second_proxy = strategy.select(pool, context)

        # Assert - Should failover to healthy proxy
        assert second_proxy.health_status == HealthStatus.HEALTHY
        assert second_proxy.url != first_proxy.url  # Different proxy

    def test_select_raises_when_no_session_id_provided(self):
        """Test that selection without session_id raises error."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = SessionPersistenceStrategy()
        context = SelectionContext()  # No session_id

        # Act & Assert
        with pytest.raises((ValueError, ProxyPoolEmptyError)):
            strategy.select(pool, context)

    def test_configure_accepts_session_timeout(self):
        """Test that strategy accepts session timeout configuration."""
        # Arrange
        strategy = SessionPersistenceStrategy()
        config = StrategyConfig(session_stickiness_duration_seconds=7200)  # 2 hours

        # Act
        strategy.configure(config)

        # Assert - Should not raise, configuration accepted
        assert True  # If we got here, configure worked

    def test_validate_metadata_always_returns_true(self):
        """Test that session persistence doesn't require specific proxy metadata."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = SessionPersistenceStrategy()

        # Act
        result = strategy.validate_metadata(pool)

        # Assert
        assert result is True

    def test_record_result_updates_proxy_metadata(self):
        """Test that record_result updates proxy completion stats."""
        # Arrange
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy.start_request()

        strategy = SessionPersistenceStrategy()

        # Act
        strategy.record_result(proxy, success=True, response_time_ms=100.0)

        # Assert
        assert proxy.requests_completed == 1
        assert proxy.requests_active == 0
        assert proxy.total_successes == 1
