"""
Unit tests for SessionManager.

Tests the thread-safe session manager for sticky proxy assignments,
including session creation, retrieval, expiration, cleanup, and concurrent access.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

from proxywhirl.models import Session
from proxywhirl.strategies import SessionManager
from tests.conftest import ProxyFactory


class TestSessionManagerCreation:
    """Tests for session creation functionality."""

    def test_create_session_returns_session_object(self):
        """Test that create_session returns a valid Session object."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()

        # Act
        session = manager.create_session("user-123", proxy)

        # Assert
        assert isinstance(session, Session)
        assert session.session_id == "user-123"
        assert session.proxy_id == str(proxy.id)
        assert session.request_count == 0

    def test_create_session_with_custom_ttl(self):
        """Test that session creation respects custom timeout."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        timeout_seconds = 600  # 10 minutes

        # Act
        session = manager.create_session("user-123", proxy, timeout_seconds=timeout_seconds)

        # Assert
        expected_expiry = session.created_at + timedelta(seconds=timeout_seconds)
        # Allow 1 second tolerance for timing
        assert abs((session.expires_at - expected_expiry).total_seconds()) < 1

    def test_create_session_overwrites_existing_session(self):
        """Test that creating a session with existing ID overwrites it."""
        # Arrange
        manager = SessionManager()
        proxy1 = ProxyFactory.healthy()
        proxy2 = ProxyFactory.healthy()

        # Act
        session1 = manager.create_session("user-123", proxy1)
        session2 = manager.create_session("user-123", proxy2)

        # Assert
        assert session2.proxy_id == str(proxy2.id)
        assert session2.proxy_id != session1.proxy_id
        # Only one session should exist
        assert len(manager.get_all_sessions()) == 1

    def test_create_session_sets_timestamps(self):
        """Test that session creation sets proper timestamps."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        before = datetime.now(timezone.utc)

        # Act
        session = manager.create_session("user-123", proxy)
        after = datetime.now(timezone.utc)

        # Assert
        assert before <= session.created_at <= after
        assert before <= session.last_used_at <= after
        assert session.expires_at > session.created_at


class TestSessionManagerRetrieval:
    """Tests for session retrieval by ID."""

    def test_get_session_returns_existing_session(self):
        """Test that get_session returns an existing active session."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        created_session = manager.create_session("user-123", proxy)

        # Act
        retrieved = manager.get_session("user-123")

        # Assert
        assert retrieved is not None
        assert retrieved.session_id == created_session.session_id
        assert retrieved.proxy_id == created_session.proxy_id

    def test_get_session_returns_none_for_nonexistent(self):
        """Test that get_session returns None for nonexistent session."""
        # Arrange
        manager = SessionManager()

        # Act
        result = manager.get_session("nonexistent-session")

        # Assert
        assert result is None

    def test_get_session_returns_none_for_expired_session(self):
        """Test that get_session returns None for expired sessions."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        # Create session with 1 second TTL
        manager.create_session("user-123", proxy, timeout_seconds=1)

        # Act - Wait for expiration
        time.sleep(1.1)
        result = manager.get_session("user-123")

        # Assert
        assert result is None

    def test_get_session_updates_lru_order(self):
        """Test that getting a session moves it to end of LRU order."""
        # Arrange
        manager = SessionManager(max_sessions=3)
        proxy = ProxyFactory.healthy()

        # Create 3 sessions
        manager.create_session("session-1", proxy)
        manager.create_session("session-2", proxy)
        manager.create_session("session-3", proxy)

        # Access session-1 to move it to end
        manager.get_session("session-1")

        # Create new session - should evict session-2 (now oldest)
        manager.create_session("session-4", proxy)

        # Assert
        assert manager.get_session("session-1") is not None  # Still exists
        assert manager.get_session("session-2") is None  # Evicted
        assert manager.get_session("session-3") is not None
        assert manager.get_session("session-4") is not None


class TestSessionManagerExpiration:
    """Tests for session expiration/TTL behavior."""

    def test_session_is_expired_after_ttl(self):
        """Test that session becomes expired after TTL passes."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()

        # Create session with 1 second TTL
        session = manager.create_session("user-123", proxy, timeout_seconds=1)
        assert not session.is_expired()

        # Act - Wait for expiration
        time.sleep(1.1)

        # Assert
        assert session.is_expired()

    def test_expired_sessions_removed_on_get(self):
        """Test that expired sessions are cleaned up when accessed."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        manager.create_session("user-123", proxy, timeout_seconds=1)

        # Act - Wait for expiration then access
        time.sleep(1.1)
        _ = manager.get_session("user-123")

        # Assert - Session should be removed from internal storage
        all_sessions = manager.get_all_sessions()
        assert len(all_sessions) == 0


class TestSessionManagerCleanup:
    """Tests for session cleanup functionality."""

    def test_cleanup_expired_removes_all_expired_sessions(self):
        """Test that cleanup_expired removes all expired sessions."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()

        # Create sessions with short TTL
        manager.create_session("session-1", proxy, timeout_seconds=1)
        manager.create_session("session-2", proxy, timeout_seconds=1)
        manager.create_session("session-3", proxy, timeout_seconds=300)  # Not expired

        # Wait for first two to expire
        time.sleep(1.1)

        # Act
        removed_count = manager.cleanup_expired()

        # Assert
        assert removed_count == 2
        assert manager.get_session("session-1") is None
        assert manager.get_session("session-2") is None
        assert manager.get_session("session-3") is not None

    def test_cleanup_expired_returns_zero_when_no_expired(self):
        """Test that cleanup returns 0 when no sessions are expired."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        manager.create_session("session-1", proxy, timeout_seconds=300)
        manager.create_session("session-2", proxy, timeout_seconds=300)

        # Act
        removed_count = manager.cleanup_expired()

        # Assert
        assert removed_count == 0

    def test_auto_cleanup_triggers_after_threshold(self):
        """Test that auto-cleanup triggers after operation threshold."""
        # Arrange - Low threshold for testing
        manager = SessionManager(auto_cleanup_threshold=3)
        proxy = ProxyFactory.healthy()

        # Create an expired session
        manager.create_session("expired-session", proxy, timeout_seconds=0)
        time.sleep(0.1)  # Ensure it's expired

        # Act - Create sessions to trigger auto-cleanup
        manager.create_session("session-1", proxy, timeout_seconds=300)
        manager.create_session("session-2", proxy, timeout_seconds=300)
        manager.create_session("session-3", proxy, timeout_seconds=300)

        # Assert - Expired session should be cleaned up
        all_sessions = manager.get_all_sessions()
        session_ids = [s.session_id for s in all_sessions]
        assert "expired-session" not in session_ids

    def test_clear_all_removes_all_sessions(self):
        """Test that clear_all removes all sessions."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        manager.create_session("session-1", proxy)
        manager.create_session("session-2", proxy)
        manager.create_session("session-3", proxy)

        # Act
        manager.clear_all()

        # Assert
        assert len(manager.get_all_sessions()) == 0


class TestSessionManagerConcurrency:
    """Tests for concurrent session access (thread safety)."""

    def test_concurrent_session_creation(self):
        """Test that concurrent session creation is thread-safe."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        num_threads = 50
        results = []

        def create_session(session_id: str):
            session = manager.create_session(session_id, proxy)
            return session.session_id

        # Act
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_session, f"session-{i}") for i in range(num_threads)]
            for future in as_completed(futures):
                results.append(future.result())

        # Assert
        assert len(results) == num_threads
        all_sessions = manager.get_all_sessions()
        assert len(all_sessions) == num_threads

    def test_concurrent_get_and_create(self):
        """Test concurrent get and create operations."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        num_operations = 100
        errors = []

        def worker(operation_id: int):
            try:
                session_id = f"session-{operation_id % 10}"  # Reuse 10 session IDs
                if operation_id % 2 == 0:
                    manager.create_session(session_id, proxy)
                else:
                    manager.get_session(session_id)
            except Exception as e:
                errors.append(e)

        # Act
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_operations)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Assert - No errors should occur
        assert len(errors) == 0

    def test_concurrent_cleanup(self):
        """Test that concurrent cleanup operations don't cause issues."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()

        # Create some sessions
        for i in range(20):
            manager.create_session(f"session-{i}", proxy, timeout_seconds=1)

        time.sleep(1.1)  # Let them expire

        errors = []

        def cleanup_worker():
            try:
                manager.cleanup_expired()
            except Exception as e:
                errors.append(e)

        # Act - Run cleanup concurrently
        threads = [threading.Thread(target=cleanup_worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Assert
        assert len(errors) == 0

    def test_concurrent_touch_session(self):
        """Test concurrent touch operations on same session."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        manager.create_session("shared-session", proxy)

        def touch_worker():
            for _ in range(100):
                manager.touch_session("shared-session")

        # Act
        threads = [threading.Thread(target=touch_worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Assert - Session should still exist and have been touched many times
        session = manager.get_session("shared-session")
        assert session is not None
        assert session.request_count == 500  # 5 threads * 100 touches


class TestSessionManagerUpdate:
    """Tests for session update operations."""

    def test_touch_session_updates_last_used(self):
        """Test that touch_session updates last_used_at timestamp."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        session = manager.create_session("user-123", proxy)
        original_last_used = session.last_used_at

        # Small delay to ensure different timestamp
        time.sleep(0.1)

        # Act
        result = manager.touch_session("user-123")

        # Assert
        assert result is True
        updated_session = manager.get_session("user-123")
        assert updated_session.last_used_at > original_last_used

    def test_touch_session_increments_request_count(self):
        """Test that touch_session increments request_count."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        manager.create_session("user-123", proxy)

        # Act
        manager.touch_session("user-123")
        manager.touch_session("user-123")
        manager.touch_session("user-123")

        # Assert
        session = manager.get_session("user-123")
        assert session.request_count == 3

    def test_touch_session_returns_false_for_nonexistent(self):
        """Test that touch returns False for nonexistent session."""
        # Arrange
        manager = SessionManager()

        # Act
        result = manager.touch_session("nonexistent")

        # Assert
        assert result is False

    def test_touch_session_returns_false_for_expired(self):
        """Test that touch returns False for expired session."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        manager.create_session("user-123", proxy, timeout_seconds=1)

        # Wait for expiration
        time.sleep(1.1)

        # Act
        result = manager.touch_session("user-123")

        # Assert
        assert result is False


class TestSessionManagerDeletion:
    """Tests for session deletion."""

    def test_remove_session_returns_true_for_existing(self):
        """Test that remove_session returns True for existing session."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        manager.create_session("user-123", proxy)

        # Act
        result = manager.remove_session("user-123")

        # Assert
        assert result is True
        assert manager.get_session("user-123") is None

    def test_remove_session_returns_false_for_nonexistent(self):
        """Test that remove_session returns False for nonexistent session."""
        # Arrange
        manager = SessionManager()

        # Act
        result = manager.remove_session("nonexistent")

        # Assert
        assert result is False

    def test_remove_session_deletes_correct_session(self):
        """Test that remove only deletes the specified session."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        manager.create_session("session-1", proxy)
        manager.create_session("session-2", proxy)
        manager.create_session("session-3", proxy)

        # Act
        manager.remove_session("session-2")

        # Assert
        assert manager.get_session("session-1") is not None
        assert manager.get_session("session-2") is None
        assert manager.get_session("session-3") is not None


class TestSessionManagerLRUEviction:
    """Tests for LRU eviction when max_sessions is reached."""

    def test_lru_eviction_when_max_sessions_reached(self):
        """Test that oldest session is evicted when max reached."""
        # Arrange
        manager = SessionManager(max_sessions=3)
        proxy = ProxyFactory.healthy()

        # Create 3 sessions (at capacity)
        manager.create_session("session-1", proxy)
        manager.create_session("session-2", proxy)
        manager.create_session("session-3", proxy)

        # Act - Create 4th session (should evict session-1)
        manager.create_session("session-4", proxy)

        # Assert
        assert manager.get_session("session-1") is None  # Evicted
        assert manager.get_session("session-2") is not None
        assert manager.get_session("session-3") is not None
        assert manager.get_session("session-4") is not None

    def test_lru_eviction_respects_access_order(self):
        """Test that LRU eviction respects access order, not creation order."""
        # Arrange
        manager = SessionManager(max_sessions=3)
        proxy = ProxyFactory.healthy()

        # Create 3 sessions
        manager.create_session("session-1", proxy)
        manager.create_session("session-2", proxy)
        manager.create_session("session-3", proxy)

        # Access session-1 to make it most recently used
        manager.get_session("session-1")

        # Act - Create 4th session (should evict session-2, the LRU)
        manager.create_session("session-4", proxy)

        # Assert
        assert manager.get_session("session-1") is not None  # Recently accessed
        assert manager.get_session("session-2") is None  # Evicted (LRU)
        assert manager.get_session("session-3") is not None
        assert manager.get_session("session-4") is not None

    def test_max_sessions_limit_enforced(self):
        """Test that session count never exceeds max_sessions."""
        # Arrange
        max_sessions = 5
        manager = SessionManager(max_sessions=max_sessions)
        proxy = ProxyFactory.healthy()

        # Act - Create more sessions than limit
        for i in range(20):
            manager.create_session(f"session-{i}", proxy)

        # Assert
        all_sessions = manager.get_all_sessions()
        assert len(all_sessions) <= max_sessions


class TestSessionManagerEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_get_all_sessions_filters_expired(self):
        """Test that get_all_sessions filters out expired sessions."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()

        manager.create_session("active-1", proxy, timeout_seconds=300)
        manager.create_session("expired-1", proxy, timeout_seconds=1)
        manager.create_session("active-2", proxy, timeout_seconds=300)

        # Wait for expiration
        time.sleep(1.1)

        # Act
        all_sessions = manager.get_all_sessions()

        # Assert
        session_ids = [s.session_id for s in all_sessions]
        assert "active-1" in session_ids
        assert "active-2" in session_ids
        assert "expired-1" not in session_ids

    def test_session_manager_with_zero_max_sessions(self):
        """Test behavior with max_sessions=0 (edge case)."""
        # Arrange - This is an unusual configuration
        manager = SessionManager(max_sessions=1)
        proxy = ProxyFactory.healthy()

        # Act
        manager.create_session("session-1", proxy)
        manager.create_session("session-2", proxy)

        # Assert - Only latest session should exist
        all_sessions = manager.get_all_sessions()
        assert len(all_sessions) == 1
        assert all_sessions[0].session_id == "session-2"

    def test_session_with_very_long_ttl(self):
        """Test session with very long TTL."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        one_year_seconds = 365 * 24 * 60 * 60

        # Act
        session = manager.create_session("long-lived", proxy, timeout_seconds=one_year_seconds)

        # Assert
        assert not session.is_expired()
        expected_expiry = session.created_at + timedelta(seconds=one_year_seconds)
        assert abs((session.expires_at - expected_expiry).total_seconds()) < 1

    def test_empty_session_id(self):
        """Test that empty session ID is handled correctly."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()

        # Act
        session = manager.create_session("", proxy)

        # Assert - Empty string is a valid session ID
        assert session.session_id == ""
        assert manager.get_session("") is not None

    def test_unicode_session_id(self):
        """Test that unicode session IDs work correctly."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()
        unicode_id = "user-\u4e2d\u6587-\u65e5\u672c\u8a9e-\ud83d\ude80"

        # Act
        session = manager.create_session(unicode_id, proxy)

        # Assert
        assert session.session_id == unicode_id
        assert manager.get_session(unicode_id) is not None

    def test_session_proxy_id_stored_as_string(self):
        """Test that proxy ID is stored as string regardless of proxy.id type."""
        # Arrange
        manager = SessionManager()
        proxy = ProxyFactory.healthy()

        # Act
        session = manager.create_session("user-123", proxy)

        # Assert
        assert isinstance(session.proxy_id, str)
        assert session.proxy_id == str(proxy.id)
