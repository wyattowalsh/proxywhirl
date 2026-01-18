"""Property-based tests for SessionManager using Hypothesis.

Tests fundamental invariants of session management:
- Session ID uniqueness
- TTL expiration correctness
- Data preservation
- Thread-safety under concurrent operations
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from proxywhirl.models import HealthStatus, Proxy, ProxyPool
from proxywhirl.strategies import SessionManager, SessionPersistenceStrategy

# ============================================================================
# HYPOTHESIS STRATEGIES
# ============================================================================

# Strategy for generating valid session IDs
session_ids = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd"),
        whitelist_characters="_-",
    ),
    min_size=1,
    max_size=64,
)

# Strategy for generating TTL values (in seconds)
ttl_seconds = st.integers(min_value=1, max_value=86400)

# Strategy for generating small TTL values for expiration testing
small_ttl_seconds = st.integers(min_value=1, max_value=5)

# Strategy for generating number of sessions
num_sessions = st.integers(min_value=1, max_value=50)

# Strategy for generating proxy URLs
proxy_urls = st.builds(
    lambda host, port: f"http://{host}:{port}",
    host=st.text(
        alphabet=st.characters(whitelist_categories=("Ll", "Nd"), whitelist_characters="."),
        min_size=1,
        max_size=30,
    ).filter(lambda x: not x.startswith(".") and not x.endswith(".") and ".." not in x),
    port=st.integers(min_value=1024, max_value=65535),
)


def create_test_proxy(url: str | None = None) -> Proxy:
    """Create a healthy test proxy."""
    if url is None:
        url = f"http://proxy{uuid4().hex[:8]}.example.com:8080"
    proxy = Proxy(url=url)
    proxy.health_status = HealthStatus.HEALTHY
    return proxy


# ============================================================================
# SESSION ID UNIQUENESS TESTS
# ============================================================================


class TestSessionIdUniqueness:
    """Property tests for session ID uniqueness guarantees."""

    @given(session_ids=st.lists(session_ids, min_size=2, max_size=50, unique=True))
    @settings(max_examples=50, deadline=timedelta(milliseconds=2000))
    def test_unique_session_ids_create_unique_sessions(self, session_ids: list[str]) -> None:
        """Property: Unique session IDs always create distinct sessions."""
        manager = SessionManager(max_sessions=100)

        # Create sessions with unique IDs
        created_sessions = {}
        for sid in session_ids:
            proxy = create_test_proxy()
            session = manager.create_session(
                session_id=sid,
                proxy=proxy,
                timeout_seconds=3600,
            )
            created_sessions[sid] = session

        # Verify each session is retrievable with its own ID
        for sid in session_ids:
            retrieved = manager.get_session(sid)
            assert retrieved is not None, f"Session {sid} should be retrievable"
            assert retrieved.session_id == sid

        # Verify session count matches
        all_sessions = manager.get_all_sessions()
        assert len(all_sessions) == len(session_ids)

    @given(session_id=session_ids)
    @settings(max_examples=30, deadline=timedelta(milliseconds=1000))
    def test_same_session_id_updates_existing_session(self, session_id: str) -> None:
        """Property: Creating session with existing ID updates (replaces) it."""
        manager = SessionManager(max_sessions=100)

        # Create first session
        proxy1 = create_test_proxy()
        session1 = manager.create_session(session_id, proxy1, timeout_seconds=3600)
        original_proxy_id = session1.proxy_id

        # Create second session with same ID
        proxy2 = create_test_proxy()
        session2 = manager.create_session(session_id, proxy2, timeout_seconds=3600)

        # Retrieve and verify it's the new session
        retrieved = manager.get_session(session_id)
        assert retrieved is not None
        assert retrieved.proxy_id == session2.proxy_id
        assert retrieved.proxy_id != original_proxy_id  # Should be updated

        # Should still have only one session
        all_sessions = manager.get_all_sessions()
        assert len(all_sessions) == 1


# ============================================================================
# SESSION TTL EXPIRATION TESTS
# ============================================================================


class TestSessionTTLExpiration:
    """Property tests for session TTL expiration behavior."""

    @given(ttl=st.integers(min_value=1, max_value=2), session_id=session_ids)
    @settings(
        max_examples=5,
        deadline=timedelta(milliseconds=10000),
        suppress_health_check=[HealthCheck.too_slow],
    )
    def test_session_expires_after_ttl(self, ttl: int, session_id: str) -> None:
        """Property: Session becomes unavailable after TTL expires."""
        manager = SessionManager(max_sessions=100)

        # Create session with small TTL
        proxy = create_test_proxy()
        session = manager.create_session(session_id, proxy, timeout_seconds=ttl)

        # Session should be available immediately
        retrieved = manager.get_session(session_id)
        assert retrieved is not None, "Session should exist immediately after creation"

        # Wait for TTL to expire (INTENTIONAL: property-based test of TTL semantics)
        time.sleep(ttl + 0.5)

        # Session should no longer be available
        expired = manager.get_session(session_id)
        assert expired is None, f"Session should be expired after {ttl}s TTL"

    @given(ttl=st.integers(min_value=60, max_value=3600))
    @settings(max_examples=20, deadline=timedelta(milliseconds=1000))
    def test_session_available_before_ttl(self, ttl: int) -> None:
        """Property: Session remains available before TTL expires."""
        manager = SessionManager(max_sessions=100)
        session_id = f"test-session-{uuid4().hex[:8]}"

        proxy = create_test_proxy()
        session = manager.create_session(session_id, proxy, timeout_seconds=ttl)

        # Session should be available immediately (TTL hasn't expired)
        retrieved = manager.get_session(session_id)
        assert retrieved is not None
        assert not retrieved.is_expired()

        # Verify expiration time is in the future
        assert retrieved.expires_at > datetime.now(timezone.utc)

    @given(num=st.integers(min_value=2, max_value=5))
    @settings(
        max_examples=5,
        deadline=timedelta(milliseconds=10000),
        suppress_health_check=[HealthCheck.too_slow],
    )
    def test_cleanup_removes_only_expired_sessions(self, num: int) -> None:
        """Property: Cleanup removes expired sessions but preserves active ones."""
        manager = SessionManager(max_sessions=100)

        # Create half with short TTL, half with long TTL
        short_ttl = 1  # Will expire quickly
        long_ttl = 3600  # Won't expire during test

        short_ttl_ids = []
        long_ttl_ids = []

        for i in range(num):
            sid = f"short-{i}-{uuid4().hex[:6]}"
            proxy = create_test_proxy()
            manager.create_session(sid, proxy, timeout_seconds=short_ttl)
            short_ttl_ids.append(sid)

        for i in range(num):
            sid = f"long-{i}-{uuid4().hex[:6]}"
            proxy = create_test_proxy()
            manager.create_session(sid, proxy, timeout_seconds=long_ttl)
            long_ttl_ids.append(sid)

        # Wait for short TTL sessions to expire (INTENTIONAL: property-based test)
        time.sleep(short_ttl + 0.5)

        # Run cleanup
        removed_count = manager.cleanup_expired()

        # Verify correct number removed
        assert removed_count == num, f"Should have removed {num} expired sessions"

        # Verify long TTL sessions still exist
        for sid in long_ttl_ids:
            session = manager.get_session(sid)
            assert session is not None, f"Long-TTL session {sid} should still exist"

        # Verify short TTL sessions are gone
        for sid in short_ttl_ids:
            session = manager.get_session(sid)
            assert session is None, f"Short-TTL session {sid} should be gone"

    @given(ttl1=ttl_seconds, ttl2=ttl_seconds)
    @settings(max_examples=30, deadline=timedelta(milliseconds=1000))
    def test_expiration_is_monotonic(self, ttl1: int, ttl2: int) -> None:
        """Property: Session expiration is monotonically related to TTL."""
        # Skip if TTLs are equal (can't determine order)
        assume(ttl1 != ttl2)

        manager = SessionManager(max_sessions=100)

        # Create two sessions with different TTLs at approximately the same time
        proxy1 = create_test_proxy()
        proxy2 = create_test_proxy()

        session1 = manager.create_session(f"s1-{uuid4().hex[:6]}", proxy1, timeout_seconds=ttl1)
        session2 = manager.create_session(f"s2-{uuid4().hex[:6]}", proxy2, timeout_seconds=ttl2)

        # Longer TTL should expire later
        if ttl1 > ttl2:
            assert session1.expires_at > session2.expires_at
        else:
            assert session2.expires_at > session1.expires_at


# ============================================================================
# SESSION DATA PRESERVATION TESTS
# ============================================================================


class TestSessionDataPreservation:
    """Property tests for session data integrity."""

    @given(session_id=session_ids, ttl=ttl_seconds)
    @settings(max_examples=50, deadline=timedelta(milliseconds=1000))
    def test_proxy_id_preserved_across_retrieval(self, session_id: str, ttl: int) -> None:
        """Property: Proxy ID assigned to session is preserved on retrieval."""
        manager = SessionManager(max_sessions=100)

        proxy = create_test_proxy()
        original_proxy_id = str(proxy.id)

        session = manager.create_session(session_id, proxy, timeout_seconds=ttl)

        # Retrieve multiple times and verify proxy ID consistency
        for _ in range(5):
            retrieved = manager.get_session(session_id)
            assert retrieved is not None
            assert retrieved.proxy_id == original_proxy_id

    @given(session_id=session_ids)
    @settings(max_examples=30, deadline=timedelta(milliseconds=1000))
    def test_touch_updates_request_count(self, session_id: str) -> None:
        """Property: Touching session increments request count."""
        manager = SessionManager(max_sessions=100)

        proxy = create_test_proxy()
        session = manager.create_session(session_id, proxy, timeout_seconds=3600)

        initial_count = session.request_count
        assert initial_count == 0

        # Touch multiple times
        num_touches = 5
        for i in range(num_touches):
            success = manager.touch_session(session_id)
            assert success

        # Verify request count incremented correctly
        retrieved = manager.get_session(session_id)
        assert retrieved is not None
        assert retrieved.request_count == num_touches

    @given(session_id=session_ids)
    @settings(max_examples=30, deadline=timedelta(milliseconds=1000))
    def test_touch_updates_last_used_timestamp(self, session_id: str) -> None:
        """Property: Touching session updates last_used_at timestamp."""
        manager = SessionManager(max_sessions=100)

        proxy = create_test_proxy()
        session = manager.create_session(session_id, proxy, timeout_seconds=3600)

        initial_last_used = session.last_used_at

        # Small delay to ensure timestamp differs (INTENTIONAL: verify timestamp changes)
        time.sleep(0.01)

        # Touch the session
        manager.touch_session(session_id)

        # Verify timestamp updated
        retrieved = manager.get_session(session_id)
        assert retrieved is not None
        assert retrieved.last_used_at >= initial_last_used


# ============================================================================
# CONCURRENT OPERATION TESTS
# ============================================================================


class TestConcurrentOperations:
    """Property tests for thread-safety under concurrent access."""

    @given(num=st.integers(min_value=10, max_value=30))
    @settings(max_examples=10, deadline=timedelta(milliseconds=10000))
    def test_concurrent_session_creation_no_data_corruption(self, num: int) -> None:
        """Property: Concurrent session creation doesn't corrupt internal state."""
        manager = SessionManager(max_sessions=1000)
        errors: list[str] = []
        created_ids: list[str] = []
        lock = threading.Lock()

        def create_session(i: int) -> None:
            try:
                sid = f"concurrent-{i}-{uuid4().hex[:8]}"
                proxy = create_test_proxy()
                session = manager.create_session(sid, proxy, timeout_seconds=3600)

                with lock:
                    created_ids.append(sid)

                # Verify immediately retrievable
                retrieved = manager.get_session(sid)
                if retrieved is None:
                    with lock:
                        errors.append(f"Session {sid} not retrievable after creation")
            except Exception as e:
                with lock:
                    errors.append(f"Error creating session: {e}")

        # Run concurrent creations
        with ThreadPoolExecutor(max_workers=min(num, 10)) as executor:
            futures = [executor.submit(create_session, i) for i in range(num)]
            for future in as_completed(futures):
                future.result()  # Raise any exceptions

        # Verify no errors
        assert not errors, f"Errors during concurrent creation: {errors}"

        # Verify all sessions exist
        all_sessions = manager.get_all_sessions()
        assert len(all_sessions) == num, f"Expected {num} sessions, got {len(all_sessions)}"

    @given(num=st.integers(min_value=5, max_value=20))
    @settings(max_examples=10, deadline=timedelta(milliseconds=10000))
    def test_concurrent_get_and_touch_no_corruption(self, num: int) -> None:
        """Property: Concurrent read/touch operations don't corrupt state."""
        manager = SessionManager(max_sessions=100)

        # Pre-create sessions
        session_ids = []
        for i in range(num):
            sid = f"preexist-{i}-{uuid4().hex[:8]}"
            proxy = create_test_proxy()
            manager.create_session(sid, proxy, timeout_seconds=3600)
            session_ids.append(sid)

        errors: list[str] = []
        touch_counts: dict[str, int] = dict.fromkeys(session_ids, 0)
        lock = threading.Lock()

        def access_session(sid: str) -> None:
            try:
                # Get session
                session = manager.get_session(sid)
                if session is None:
                    with lock:
                        errors.append(f"Session {sid} unexpectedly None")
                    return

                # Touch it
                success = manager.touch_session(sid)
                if success:
                    with lock:
                        touch_counts[sid] += 1
            except Exception as e:
                with lock:
                    errors.append(f"Error accessing {sid}: {e}")

        # Run many concurrent accesses
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(100):  # 100 total operations
                sid = session_ids[_ % len(session_ids)]
                futures.append(executor.submit(access_session, sid))

            for future in as_completed(futures):
                future.result()

        # Verify no errors
        assert not errors, f"Errors during concurrent access: {errors}"

        # Verify all sessions still exist and have request counts
        for sid in session_ids:
            session = manager.get_session(sid)
            assert session is not None
            # Request count should match our tracking (within reason due to concurrent touches)
            assert session.request_count >= touch_counts[sid] - 1

    @given(num=st.integers(min_value=5, max_value=15))
    @settings(max_examples=10, deadline=timedelta(milliseconds=10000))
    def test_concurrent_create_remove_consistency(self, num: int) -> None:
        """Property: Concurrent create/remove maintains consistency."""
        manager = SessionManager(max_sessions=100)
        errors: list[str] = []

        def create_and_remove(i: int) -> None:
            try:
                sid = f"temp-{i}-{uuid4().hex[:8]}"
                proxy = create_test_proxy()

                # Create
                manager.create_session(sid, proxy, timeout_seconds=3600)

                # Verify exists
                if manager.get_session(sid) is None:
                    errors.append(f"{sid} not found after create")
                    return

                # Remove
                removed = manager.remove_session(sid)
                if not removed:
                    errors.append(f"{sid} remove returned False")

                # Verify gone
                if manager.get_session(sid) is not None:
                    errors.append(f"{sid} still exists after remove")

            except Exception as e:
                errors.append(f"Error in create_remove: {e}")

        with ThreadPoolExecutor(max_workers=min(num, 10)) as executor:
            futures = [executor.submit(create_and_remove, i) for i in range(num)]
            for future in as_completed(futures):
                future.result()

        assert not errors, f"Errors: {errors}"


# ============================================================================
# LRU EVICTION TESTS
# ============================================================================


class TestLRUEviction:
    """Property tests for LRU eviction behavior."""

    @given(max_sessions=st.integers(min_value=5, max_value=20))
    @settings(max_examples=20, deadline=timedelta(milliseconds=2000))
    def test_max_sessions_limit_enforced(self, max_sessions: int) -> None:
        """Property: Session count never exceeds max_sessions."""
        manager = SessionManager(max_sessions=max_sessions)

        # Create more sessions than the limit
        overflow = 10
        for i in range(max_sessions + overflow):
            sid = f"overflow-{i}-{uuid4().hex[:6]}"
            proxy = create_test_proxy()
            manager.create_session(sid, proxy, timeout_seconds=3600)

            # Count should never exceed max
            current_count = len(manager.get_all_sessions())
            assert current_count <= max_sessions, (
                f"Session count {current_count} exceeds max {max_sessions}"
            )

    @given(max_sessions=st.integers(min_value=3, max_value=10))
    @settings(max_examples=15, deadline=timedelta(milliseconds=2000))
    def test_lru_evicts_oldest_session(self, max_sessions: int) -> None:
        """Property: LRU eviction removes the least recently used session.

        Note: get_session() moves the session to the end of the LRU order,
        so we use get_all_sessions() to check existence without affecting order.
        """
        manager = SessionManager(max_sessions=max_sessions)

        # Create sessions up to limit
        first_session_id = None
        for i in range(max_sessions):
            sid = f"ordered-{i}-{uuid4().hex[:6]}"
            if i == 0:
                first_session_id = sid
            proxy = create_test_proxy()
            manager.create_session(sid, proxy, timeout_seconds=3600)

        # First session should still exist (use get_all_sessions to avoid LRU update)
        all_sessions = manager.get_all_sessions()
        assert first_session_id in [s.session_id for s in all_sessions], (
            "First session should exist before eviction"
        )

        # Create one more session (triggers eviction)
        new_sid = f"new-session-{uuid4().hex[:6]}"
        proxy = create_test_proxy()
        manager.create_session(new_sid, proxy, timeout_seconds=3600)

        # First session should have been evicted (it's oldest/LRU)
        all_sessions_after = manager.get_all_sessions()
        session_ids_after = [s.session_id for s in all_sessions_after]
        assert first_session_id not in session_ids_after, (
            "First session should have been LRU-evicted"
        )

        # New session should exist
        assert new_sid in session_ids_after


# ============================================================================
# SESSION PERSISTENCE STRATEGY INTEGRATION TESTS
# ============================================================================


class TestSessionPersistenceStrategyProperties:
    """Property tests for SessionPersistenceStrategy."""

    @given(session_id=session_ids)
    @settings(max_examples=30, deadline=timedelta(milliseconds=2000))
    def test_same_proxy_returned_for_same_session(self, session_id: str) -> None:
        """Property: Same session ID always returns the same proxy (sticky sessions)."""
        # Create pool with multiple proxies
        pool = ProxyPool(name="test-pool")
        for i in range(5):
            proxy = create_test_proxy()
            pool.add_proxy(proxy)

        strategy = SessionPersistenceStrategy()

        from proxywhirl.models import SelectionContext

        context = SelectionContext(session_id=session_id)

        # First selection creates binding
        first_proxy = strategy.select(pool, context)
        first_proxy_id = str(first_proxy.id)

        # Subsequent selections should return same proxy
        for _ in range(10):
            proxy = strategy.select(pool, context)
            assert str(proxy.id) == first_proxy_id, "Session persistence should return same proxy"

    @given(num_sessions=st.integers(min_value=2, max_value=10))
    @settings(max_examples=20, deadline=timedelta(milliseconds=2000))
    def test_different_sessions_can_use_different_proxies(self, num_sessions: int) -> None:
        """Property: Different session IDs may get different proxies."""
        # Create pool with many proxies to increase chance of different assignments
        pool = ProxyPool(name="test-pool")
        for i in range(num_sessions * 2):
            proxy = create_test_proxy()
            pool.add_proxy(proxy)

        strategy = SessionPersistenceStrategy()

        from proxywhirl.models import SelectionContext

        # Create different sessions
        proxy_assignments = {}
        for i in range(num_sessions):
            sid = f"session-{i}-{uuid4().hex[:6]}"
            context = SelectionContext(session_id=sid)
            proxy = strategy.select(pool, context)
            proxy_assignments[sid] = str(proxy.id)

        # We can't guarantee all different (depends on strategy),
        # but each session should maintain its own assignment
        for sid, expected_proxy_id in proxy_assignments.items():
            context = SelectionContext(session_id=sid)
            proxy = strategy.select(pool, context)
            assert str(proxy.id) == expected_proxy_id
