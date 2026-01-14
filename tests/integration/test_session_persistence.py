"""Integration tests for SessionPersistenceStrategy.

Tests the complete session persistence behavior including:
- Multiple concurrent sessions
- Session expiration and cleanup
- Failover when session proxy becomes unhealthy
- SC-005: 99.9% same-proxy guarantee across requests
"""

import time
from threading import Thread
from typing import List

import pytest

from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)
from proxywhirl.strategies import SessionPersistenceStrategy


@pytest.fixture
def proxy_pool() -> ProxyPool:
    """Create a pool with multiple healthy proxies."""
    proxies = [
        Proxy(url="http://proxy1.example.com:8001"),
        Proxy(url="http://proxy2.example.com:8002"),
        Proxy(url="http://proxy3.example.com:8003"),
        Proxy(url="http://proxy4.example.com:8004"),
        Proxy(url="http://proxy5.example.com:8005"),
    ]
    return ProxyPool(name="test_pool", proxies=proxies)


@pytest.fixture
def strategy() -> SessionPersistenceStrategy:
    """Create a SessionPersistenceStrategy instance."""
    return SessionPersistenceStrategy()


def test_multiple_sessions_get_different_proxies(
    strategy: SessionPersistenceStrategy, proxy_pool: ProxyPool
) -> None:
    """Test that different sessions get assigned different proxies."""
    # Create 5 different sessions
    sessions = [f"session_{i}" for i in range(5)]
    assigned_proxies = {}

    for session_id in sessions:
        context = SelectionContext(session_id=session_id)
        proxy = strategy.select(proxy_pool, context)
        assigned_proxies[session_id] = str(proxy.id)

    # All sessions should have proxies assigned
    assert len(assigned_proxies) == 5

    # Proxies should be distributed (not all the same)
    unique_proxies = set(assigned_proxies.values())
    assert len(unique_proxies) >= 2, "Sessions should be distributed across proxies"


def test_sc_005_same_proxy_guarantee(
    strategy: SessionPersistenceStrategy, proxy_pool: ProxyPool
) -> None:
    """Test SC-005: 99.9% same-proxy guarantee across multiple requests.

    Success Criteria:
    - Same proxy returned for same session_id ≥99.9% of the time
    - Test with 1000 requests to get statistical significance
    """
    session_id = "test_session_sc005"
    context = SelectionContext(session_id=session_id)

    # First request establishes the session
    first_proxy = strategy.select(proxy_pool, context)
    first_proxy_id = str(first_proxy.id)

    # Make 999 more requests (total 1000)
    same_proxy_count = 1  # Count the first request
    for _ in range(999):
        proxy = strategy.select(proxy_pool, context)
        if str(proxy.id) == first_proxy_id:
            same_proxy_count += 1

    # Calculate percentage
    percentage = (same_proxy_count / 1000) * 100

    # Should be ≥99.9% (allow up to 1 different proxy out of 1000)
    assert percentage >= 99.9, (
        f"Same-proxy guarantee failed: {percentage:.2f}% "
        f"(expected ≥99.9%, got {same_proxy_count}/1000 same proxy)"
    )


def test_session_persistence_across_time(
    strategy: SessionPersistenceStrategy, proxy_pool: ProxyPool
) -> None:
    """Test that sessions persist across multiple requests over time."""
    session_id = "persistent_session"
    context = SelectionContext(session_id=session_id)

    # First request
    proxy1 = strategy.select(proxy_pool, context)
    proxy1_id = str(proxy1.id)

    # Wait a bit (but less than session timeout)
    time.sleep(0.1)

    # Second request should get same proxy
    proxy2 = strategy.select(proxy_pool, context)
    assert str(proxy2.id) == proxy1_id

    # Wait again
    time.sleep(0.1)

    # Third request should still get same proxy
    proxy3 = strategy.select(proxy_pool, context)
    assert str(proxy3.id) == proxy1_id


def test_session_expiration_creates_new_session(
    strategy: SessionPersistenceStrategy, proxy_pool: ProxyPool
) -> None:
    """Test that expired sessions are replaced with new sessions."""
    # Configure very short timeout
    config = StrategyConfig(session_stickiness_duration_seconds=1)
    strategy.configure(config)

    session_id = "expiring_session"
    context = SelectionContext(session_id=session_id)

    # First request establishes session
    proxy1 = strategy.select(proxy_pool, context)
    proxy1_id = str(proxy1.id)

    # Wait for session to expire
    time.sleep(1.5)

    # Cleanup expired sessions
    cleanup_count = strategy.cleanup_expired_sessions()
    assert cleanup_count >= 1, "Should have cleaned up at least one session"

    # Next request should create new session (might get different proxy)
    proxy2 = strategy.select(proxy_pool, context)
    # We don't assert different proxy since it might randomly select the same one
    # Just verify it returns a valid proxy
    assert proxy2 is not None


def test_concurrent_sessions_thread_safety(
    strategy: SessionPersistenceStrategy, proxy_pool: ProxyPool
) -> None:
    """Test that multiple threads can safely use different sessions."""
    results: List[str] = []
    errors: List[Exception] = []

    def make_requests(session_id: str) -> None:
        try:
            context = SelectionContext(session_id=session_id)
            # Make 10 requests per thread
            proxy_ids = set()
            for _ in range(10):
                proxy = strategy.select(proxy_pool, context)
                proxy_ids.add(str(proxy.id))

            # Each session should use exactly 1 proxy (same proxy every time)
            results.append(f"{session_id}:{len(proxy_ids)}")
        except Exception as e:
            errors.append(e)

    # Create 10 threads with different sessions
    threads = []
    for i in range(10):
        thread = Thread(target=make_requests, args=(f"thread_session_{i}",))
        threads.append(thread)
        thread.start()

    # Wait for all threads
    for thread in threads:
        thread.join()

    # Check for errors
    assert len(errors) == 0, f"Errors occurred: {errors}"

    # Each session should have used exactly 1 proxy
    assert len(results) == 10
    for result in results:
        session_id, proxy_count = result.split(":")
        assert (
            proxy_count == "1"
        ), f"Session {session_id} used {proxy_count} different proxies, expected 1"


def test_failover_when_session_proxy_becomes_unhealthy(
    strategy: SessionPersistenceStrategy, proxy_pool: ProxyPool
) -> None:
    """Test automatic failover when a session's proxy becomes unhealthy."""
    session_id = "failover_session"
    context = SelectionContext(session_id=session_id)

    # Establish session with first proxy
    proxy1 = strategy.select(proxy_pool, context)
    proxy1_id = str(proxy1.id)

    # Verify we get same proxy on next request
    proxy2 = strategy.select(proxy_pool, context)
    assert str(proxy2.id) == proxy1_id

    # Mark the session's proxy as unhealthy
    for proxy in proxy_pool.proxies:
        if str(proxy.id) == proxy1_id:
            proxy.health_status = HealthStatus.UNHEALTHY
            break

    # Next request should automatically failover to different proxy
    proxy3 = strategy.select(proxy_pool, context)
    assert str(proxy3.id) != proxy1_id, "Should failover to different proxy"
    assert proxy3.health_status != HealthStatus.UNHEALTHY, "New proxy should not be unhealthy"

    # Subsequent requests should stick to the new proxy
    proxy4 = strategy.select(proxy_pool, context)
    assert str(proxy4.id) == str(proxy3.id), "Should stick to new proxy after failover"


def test_session_closes_properly(
    strategy: SessionPersistenceStrategy, proxy_pool: ProxyPool
) -> None:
    """Test that explicit session closure works correctly."""
    session_id = "closeable_session"
    context = SelectionContext(session_id=session_id)

    # Establish session
    proxy1 = strategy.select(proxy_pool, context)
    proxy1_id = str(proxy1.id)

    # Verify session exists
    proxy2 = strategy.select(proxy_pool, context)
    assert str(proxy2.id) == proxy1_id

    # Close session explicitly
    strategy.close_session(session_id)

    # Next request should create new session (might get different proxy)
    proxy3 = strategy.select(proxy_pool, context)
    assert proxy3 is not None  # Should get a valid proxy


def test_high_load_session_persistence(
    strategy: SessionPersistenceStrategy, proxy_pool: ProxyPool
) -> None:
    """Test session persistence under high load (100 sessions, 50 requests each)."""
    session_count = 100
    requests_per_session = 50

    # Track proxy consistency per session
    session_proxies = {}

    for session_num in range(session_count):
        session_id = f"load_session_{session_num}"
        context = SelectionContext(session_id=session_id)

        proxy_ids = set()
        for _ in range(requests_per_session):
            proxy = strategy.select(proxy_pool, context)
            proxy_ids.add(str(proxy.id))

        # Each session should use exactly 1 proxy
        session_proxies[session_id] = len(proxy_ids)

    # Verify all sessions used exactly 1 proxy
    for session_id, proxy_count in session_proxies.items():
        assert proxy_count == 1, f"Session {session_id} used {proxy_count} proxies, expected 1"

    # Total requests: 100 sessions * 50 requests = 5000
    # All should have been consistent
    total_requests = session_count * requests_per_session
    assert total_requests == 5000


def test_session_with_proxy_metadata_updates(
    strategy: SessionPersistenceStrategy, proxy_pool: ProxyPool
) -> None:
    """Test that proxy metadata is updated correctly during session persistence."""
    session_id = "metadata_session"
    context = SelectionContext(session_id=session_id)

    # First request
    proxy1 = strategy.select(proxy_pool, context)
    initial_request_count = proxy1.total_requests

    # Record a successful result
    strategy.record_result(proxy1, success=True, response_time_ms=100.0)

    # Verify metadata updated
    assert proxy1.total_requests == initial_request_count + 1

    # Make another request - should get same proxy
    proxy2 = strategy.select(proxy_pool, context)
    assert str(proxy2.id) == str(proxy1.id)

    # Verify request count increased
    assert proxy2.total_requests > initial_request_count
