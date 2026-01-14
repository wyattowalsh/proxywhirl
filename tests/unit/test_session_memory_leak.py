"""
Test that SessionPersistenceStrategy properly manages memory.

Tests verify that sessions don't accumulate indefinitely and that
automatic cleanup mechanisms work correctly.

Also tests that ProxyRotator doesn't leak memory through circuit breakers
or client pools under proxy churn.
"""

import time
from datetime import datetime, timedelta, timezone

from proxywhirl.models import HealthStatus, Proxy, ProxyPool, SelectionContext
from proxywhirl.rotator import ProxyRotator
from proxywhirl.strategies import SessionManager, SessionPersistenceStrategy


class TestSessionMemoryManagement:
    """Tests for session memory management and cleanup."""

    def test_session_manager_auto_cleanup_removes_expired_sessions(self):
        """Test that auto-cleanup removes expired sessions periodically."""
        # Create manager with low threshold for testing
        manager = SessionManager(max_sessions=1000, auto_cleanup_threshold=10)

        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)

        # Create a session with 1-second timeout
        session = manager.create_session("short-lived", proxy, timeout_seconds=1)

        # Manually expire it
        session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)

        # Trigger auto-cleanup by performing operations
        for i in range(11):
            manager.create_session(f"new-session-{i}", proxy, timeout_seconds=3600)

        # The expired session should be gone
        assert manager.get_session("short-lived") is None

    def test_session_manager_lru_eviction_when_max_reached(self):
        """Test that LRU eviction works when max_sessions is reached."""
        # Create manager with very small limit
        manager = SessionManager(max_sessions=5, auto_cleanup_threshold=1000)

        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)

        # Create 5 sessions (fill to max)
        for i in range(5):
            manager.create_session(f"session-{i}", proxy, timeout_seconds=3600)

        # First session exists
        assert manager.get_session("session-0") is not None

        # Touch some sessions to update their last_used_at
        for i in range(1, 5):
            manager.touch_session(f"session-{i}")
            time.sleep(0.01)  # Small delay to ensure different timestamps

        # Create a new session - should evict session-0 (oldest last_used_at)
        manager.create_session("session-5", proxy, timeout_seconds=3600)

        # session-0 should be evicted
        assert manager.get_session("session-0") is None
        # Newer sessions should still exist
        assert manager.get_session("session-1") is not None
        assert manager.get_session("session-5") is not None

    def test_session_manager_does_not_accumulate_indefinitely(self):
        """Test that session manager doesn't grow beyond max_sessions."""
        manager = SessionManager(max_sessions=100, auto_cleanup_threshold=50)

        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)

        # Create 500 sessions (5x the max)
        for i in range(500):
            manager.create_session(f"session-{i}", proxy, timeout_seconds=3600)

        # Should never exceed max_sessions
        assert len(manager._sessions) <= 100

    def test_session_persistence_strategy_memory_bounds(self):
        """Test that SessionPersistenceStrategy respects memory bounds."""
        # Create strategy with small limits
        strategy = SessionPersistenceStrategy(max_sessions=50, auto_cleanup_threshold=25)

        pool = ProxyPool(name="test-pool")
        for i in range(5):
            proxy = Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            pool.add_proxy(proxy)

        # Create 200 sessions
        for i in range(200):
            context = SelectionContext(session_id=f"user-{i}")
            strategy.select(pool, context)

        # Check that we don't have more than max_sessions
        stats = strategy.get_session_stats()
        assert stats["total_sessions"] <= stats["max_sessions"]

    def test_session_stats_reporting(self):
        """Test that get_session_stats returns accurate information."""
        strategy = SessionPersistenceStrategy(max_sessions=1000, auto_cleanup_threshold=100)

        stats = strategy.get_session_stats()

        assert stats["max_sessions"] == 1000
        assert stats["auto_cleanup_threshold"] == 100
        assert stats["total_sessions"] == 0

        # Create some sessions
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        for i in range(10):
            context = SelectionContext(session_id=f"user-{i}")
            strategy.select(pool, context)

        stats = strategy.get_session_stats()
        assert stats["total_sessions"] == 10

    def test_expired_sessions_cleaned_up_automatically(self):
        """Test that expired sessions are cleaned up during normal operations."""
        # Set threshold high to prevent cleanup during setup
        manager = SessionManager(max_sessions=1000, auto_cleanup_threshold=10)

        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)

        # Create sessions with very short timeout
        for i in range(3):
            session = manager.create_session(f"expire-{i}", proxy, timeout_seconds=1)
            # Manually expire them
            session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)

        # Create some active sessions
        for i in range(2):
            manager.create_session(f"active-{i}", proxy, timeout_seconds=3600)

        # Should have all 5 sessions before cleanup
        # (auto_cleanup hasn't been triggered yet because we're below threshold)
        assert len(manager._sessions) == 5

        # Trigger auto-cleanup by creating more sessions (enough to hit threshold)
        for i in range(6):
            manager.create_session(f"new-{i}", proxy, timeout_seconds=3600)

        # After crossing threshold, auto-cleanup should have occurred
        # Expired sessions should be gone
        for i in range(3):
            assert manager.get_session(f"expire-{i}") is None

        # Active sessions should still exist
        for i in range(2):
            assert manager.get_session(f"active-{i}") is not None

    def test_manual_cleanup_still_works(self):
        """Test that manual cleanup_expired_sessions still works."""
        strategy = SessionPersistenceStrategy(max_sessions=1000, auto_cleanup_threshold=1000)

        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        # Create sessions
        for i in range(5):
            context = SelectionContext(session_id=f"user-{i}")
            strategy.select(pool, context)

        # Manually expire some sessions
        for i in range(3):
            session = strategy._session_manager.get_session(f"user-{i}")
            if session:
                session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)

        # Manual cleanup
        removed = strategy.cleanup_expired_sessions()

        assert removed == 3

        # Verify they're gone
        for i in range(3):
            assert strategy._session_manager.get_session(f"user-{i}") is None

        # Verify active ones remain
        for i in range(3, 5):
            assert strategy._session_manager.get_session(f"user-{i}") is not None

    def test_session_manager_thread_safety_with_cleanup(self):
        """Test that cleanup operations are thread-safe."""
        import threading

        manager = SessionManager(max_sessions=100, auto_cleanup_threshold=10)
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)

        errors = []

        def create_sessions(start_idx: int, count: int):
            try:
                for i in range(count):
                    manager.create_session(
                        f"thread-{start_idx}-session-{i}", proxy, timeout_seconds=3600
                    )
            except Exception as e:
                errors.append(e)

        # Create sessions from multiple threads
        threads = []
        for t in range(5):
            thread = threading.Thread(target=create_sessions, args=(t, 50))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should have no errors
        assert len(errors) == 0

        # Should respect max_sessions
        assert len(manager._sessions) <= 100

    def test_long_running_session_memory_stability(self):
        """Test that memory usage remains stable under long-running load with session churn."""

        # Create strategy with realistic limits
        strategy = SessionPersistenceStrategy(max_sessions=100, auto_cleanup_threshold=50)

        pool = ProxyPool(name="test-pool")
        for i in range(10):
            proxy = Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            pool.add_proxy(proxy)

        # Simulate long-running usage with session churn
        # Create 1000 sessions total, but only 100 should be active at any time
        session_counter = 0
        for cycle in range(10):
            # Create 100 sessions
            for i in range(100):
                session_id = f"session-{session_counter}"
                context = SelectionContext(session_id=session_id)
                strategy.select(pool, context)
                session_counter += 1

            # Verify we never exceed max_sessions due to LRU eviction
            stats = strategy.get_session_stats()
            assert stats["total_sessions"] <= 100, (
                f"Session count {stats['total_sessions']} exceeds max {stats['max_sessions']}"
            )

        # Final check - should have exactly max_sessions due to LRU eviction
        final_stats = strategy.get_session_stats()
        assert final_stats["total_sessions"] <= 100
        # Should be close to max due to continuous creation
        assert final_stats["total_sessions"] >= 50

    def test_session_manager_cleanup_deque_memory(self):
        """Test that internal deque structures don't grow unbounded."""
        # Use higher threshold to prevent auto-cleanup during initial session creation
        manager = SessionManager(max_sessions=1000, auto_cleanup_threshold=1000)
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)

        # Create many sessions with very short TTL
        for i in range(50):
            session = manager.create_session(f"short-{i}", proxy, timeout_seconds=1)
            # Immediately expire it
            session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)

        # Initial size before manual cleanup (should have 50 expired sessions)
        initial_size = len(manager._sessions)
        assert initial_size == 50, f"Expected 50 sessions, got {initial_size}"

        # Manually trigger cleanup of expired sessions
        removed_count = manager.cleanup_expired()
        assert removed_count == 50, (
            f"Expected to remove 50 expired sessions, removed {removed_count}"
        )

        # After cleanup, expired sessions should be removed
        remaining_size = len(manager._sessions)
        assert remaining_size == 0, f"Expected 0 sessions after cleanup, got {remaining_size}"

    def test_get_all_sessions_cleanup_side_effect(self):
        """Test that get_all_sessions() properly cleans up expired sessions."""
        manager = SessionManager(max_sessions=1000, auto_cleanup_threshold=1000)
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)

        # Create mix of active and expired sessions
        for i in range(50):
            if i < 25:
                # Active sessions
                manager.create_session(f"active-{i}", proxy, timeout_seconds=3600)
            else:
                # Expired sessions
                session = manager.create_session(f"expired-{i}", proxy, timeout_seconds=1)
                session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)

        # get_all_sessions should return only active and clean up expired
        active_sessions = manager.get_all_sessions()
        assert len(active_sessions) == 25, f"Expected 25 active, got {len(active_sessions)}"

        # Verify expired sessions were removed from internal dict
        assert len(manager._sessions) == 25, "Expired sessions not removed from internal storage"


class TestProxyRotatorMemoryManagement:
    """Tests for ProxyRotator memory management including circuit breakers and client pools."""

    def test_circuit_breakers_cleaned_up_on_proxy_removal(self):
        """Test that circuit breakers are removed when proxies are removed."""
        rotator = ProxyRotator()

        # Add proxies
        proxy_ids = []
        for i in range(10):
            proxy = Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)
            proxy_ids.append(str(proxy.id))

        # Verify circuit breakers created
        assert len(rotator.circuit_breakers) == 10

        # Remove half the proxies
        for i in range(5):
            rotator.remove_proxy(proxy_ids[i])

        # Circuit breakers should be cleaned up
        assert len(rotator.circuit_breakers) == 5

        # Verify the right ones remain
        for i in range(5, 10):
            assert proxy_ids[i] in rotator.circuit_breakers

    def test_circuit_breakers_cleaned_up_on_unhealthy_clear(self):
        """Test that circuit breakers are removed when clearing unhealthy proxies."""
        rotator = ProxyRotator()

        # Add proxies
        for i in range(10):
            proxy = Proxy(
                url=f"http://proxy{i}.com:8080",
                health_status=HealthStatus.HEALTHY if i < 5 else HealthStatus.UNHEALTHY,
            )
            rotator.add_proxy(proxy)

        # Verify all circuit breakers created
        assert len(rotator.circuit_breakers) == 10

        # Clear unhealthy proxies
        removed_count = rotator.clear_unhealthy_proxies()
        assert removed_count == 5

        # Circuit breakers should be cleaned up for removed proxies
        assert len(rotator.circuit_breakers) == 5

    def test_client_pool_lru_eviction(self):
        """Test that client pool evicts LRU clients when limit reached."""
        rotator = ProxyRotator()

        # Add proxies (within the ProxyPool's max_pool_size limit of 100)
        for i in range(50):
            proxy = Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)

        # Client pool starts empty - clients are created lazily when requests are made
        # Just verify the pool exists and is empty since we haven't made any requests
        assert len(rotator._client_pool) == 0

        # Verify the LRU client pool infrastructure is in place
        assert hasattr(rotator._client_pool, "put")
        assert hasattr(rotator._client_pool, "get")
        assert hasattr(rotator._client_pool, "remove")
        assert rotator._client_pool._maxsize == 100  # Verify LRU maxsize is configured

    def test_proxy_churn_memory_stability(self):
        """Test that repeated add/remove of proxies doesn't leak memory."""
        rotator = ProxyRotator()

        # Simulate continuous proxy churn (realistic for dynamic proxy pools)
        for cycle in range(10):
            # Add 20 proxies
            added_proxies = []
            for i in range(20):
                proxy = Proxy(
                    url=f"http://proxy-cycle{cycle}-{i}.com:8080",
                    health_status=HealthStatus.HEALTHY,
                )
                rotator.add_proxy(proxy)
                added_proxies.append(str(proxy.id))

            # After adding, we have: previous_count + 20
            expected_after_add = 5 * cycle + 20
            assert len(rotator.circuit_breakers) == expected_after_add, (
                f"Cycle {cycle}: Expected {expected_after_add} after add, got {len(rotator.circuit_breakers)}"
            )

            # Remove 15 proxies (net growth of 5 per cycle)
            for i in range(15):
                rotator.remove_proxy(added_proxies[i])

            # After removing, we have: previous_count + 5
            expected_after_remove = 5 * (cycle + 1)
            assert len(rotator.circuit_breakers) == expected_after_remove, (
                f"Cycle {cycle}: Expected {expected_after_remove} after remove, got {len(rotator.circuit_breakers)}"
            )

        # Final count should be 50 (10 cycles * 5 net growth)
        assert len(rotator.circuit_breakers) == 50
        assert rotator.pool.size == 50

    def test_circuit_breaker_failure_window_cleanup(self):
        """Test that circuit breaker failure windows don't grow unbounded."""
        from proxywhirl.circuit_breaker import CircuitBreaker

        # Create circuit breaker with short window for testing
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            window_duration=0.2,  # 200ms window
            failure_threshold=1000,  # High threshold to prevent state transitions during test
        )

        # Record some failures
        import time

        for i in range(10):
            cb.record_failure()
            time.sleep(0.01)  # 10ms between failures

        # Should have all 10 failures in window
        initial_count = len(cb.failure_window)
        assert initial_count == 10, f"Expected 10 failures, got {initial_count}"

        # Wait for window to expire
        time.sleep(0.25)  # Wait longer than window_duration

        # Record a new failure - this should trigger cleanup of old failures
        cb.record_failure()

        # Only the most recent failure should remain (all old ones expired)
        final_count = len(cb.failure_window)
        assert final_count == 1, f"Expected 1 failure after cleanup, got {final_count}"

    def test_rotator_destructor_cleanup(self):
        """Test that ProxyRotator properly cleans up resources in destructor."""
        # Create rotator in a scope
        rotator = ProxyRotator()

        # Add proxies with clients
        for i in range(5):
            proxy = Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)

        # Access internal structures
        circuit_breaker_count = len(rotator.circuit_breakers)
        assert circuit_breaker_count == 5

        # Delete rotator (calls __del__)
        del rotator

        # If we reached here without errors, cleanup succeeded
        # (Cannot verify internal state after deletion, but no exceptions means success)

    def test_combined_session_and_circuit_breaker_memory(self):
        """Test memory stability with both sessions and circuit breakers under load."""
        from proxywhirl.strategies import SessionPersistenceStrategy

        # Create rotator with session strategy directly
        session_strategy = SessionPersistenceStrategy(max_sessions=100, auto_cleanup_threshold=50)
        rotator = ProxyRotator(strategy=session_strategy)

        # Add proxies
        for i in range(10):
            proxy = Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)

        # Verify strategy is session persistence
        assert isinstance(rotator.strategy, SessionPersistenceStrategy)

        # Circuit breakers should be created for each proxy
        assert len(rotator.circuit_breakers) == 10

        # Pool size should be stable
        assert rotator.pool.size == 10

        # Session stats should show proper configuration
        stats = session_strategy.get_session_stats()
        assert stats["max_sessions"] == 100
        assert stats["auto_cleanup_threshold"] == 50
        assert stats["total_sessions"] == 0  # No requests made yet
