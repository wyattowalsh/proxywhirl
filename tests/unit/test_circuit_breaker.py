"""
Unit tests for CircuitBreaker.
"""

from unittest.mock import patch

import pytest

from proxywhirl.circuit_breaker import CircuitBreaker, CircuitBreakerState


class TestCircuitBreakerRecordFailure:
    """Test CircuitBreaker.record_failure() method."""

    def test_record_single_failure_stays_closed(self):
        """Test that a single failure keeps circuit breaker CLOSED."""
        cb = CircuitBreaker(proxy_id="test-proxy", failure_threshold=5)

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

        cb.record_failure()

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 1

    def test_record_failures_opens_circuit(self):
        """Test that threshold failures open the circuit."""
        cb = CircuitBreaker(proxy_id="test-proxy", failure_threshold=3)

        # Record 2 failures - should stay closed
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 2

        # Record 3rd failure - should open
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 3

    def test_rolling_window_cleanup(self):
        """Test that old failures are removed from rolling window."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=3,
            window_duration=2.0,  # 2 second window
        )

        # Record 2 failures
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.failure_count == 2

        # Wait for window to expire (mock time + 3 seconds)
        with patch("time.time", return_value=103.0):
            cb.record_failure()  # This should clean up old failures

        # Only the latest failure should count (old ones expired)
        assert cb.failure_count == 1
        assert cb.state == CircuitBreakerState.CLOSED

    def test_failure_in_half_open_reopens_circuit(self):
        """Test that failure in HALF_OPEN state reopens the circuit."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=1.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN

        # Transition to half-open
        with patch("time.time", return_value=101.0):
            cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record failure in half-open state
        with patch("time.time", return_value=101.5):
            cb.record_failure()

        # Should reopen
        assert cb.state == CircuitBreakerState.OPEN


class TestCircuitBreakerRecordSuccess:
    """Test CircuitBreaker.record_success() method."""

    def test_success_in_closed_state_no_change(self):
        """Test that success in CLOSED state doesn't change state."""
        cb = CircuitBreaker(proxy_id="test-proxy")

        assert cb.state == CircuitBreakerState.CLOSED

        cb.record_success()

        assert cb.state == CircuitBreakerState.CLOSED

    def test_success_in_half_open_closes_circuit(self):
        """Test that success in HALF_OPEN state closes the circuit."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=1.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 2

        # Transition to half-open
        with patch("time.time", return_value=101.0):
            cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record success
        cb.record_success()

        # Should close and reset
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert len(cb.failure_window) == 0


class TestCircuitBreakerShouldAttemptRequest:
    """Test CircuitBreaker.should_attempt_request() method."""

    def test_closed_allows_requests(self):
        """Test that CLOSED state allows requests."""
        cb = CircuitBreaker(proxy_id="test-proxy")

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.should_attempt_request() is True

    def test_open_blocks_requests(self):
        """Test that OPEN state blocks requests before timeout."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=10.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN

        # Immediately check - should block
        with patch("time.time", return_value=100.5):
            assert cb.should_attempt_request() is False

        # After 5 seconds (still before timeout) - should block
        with patch("time.time", return_value=105.0):
            assert cb.should_attempt_request() is False

    def test_open_transitions_to_half_open_after_timeout(self):
        """Test that OPEN state transitions to HALF_OPEN after timeout."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=5.0,
        )

        # Open the circuit at time 100
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert cb.next_test_time == 105.0

        # Check at time 105 (timeout elapsed)
        with patch("time.time", return_value=105.0):
            result = cb.should_attempt_request()

        assert result is True
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_half_open_allows_one_request(self):
        """Test that HALF_OPEN state allows exactly one test request.

        When transitioning from OPEN to HALF_OPEN, the first call to
        should_attempt_request() returns True. Subsequent calls return False
        until the test request completes (via record_success or record_failure).
        """
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=1.0,
        )

        # Open and transition to half-open
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        # First call transitions to HALF_OPEN and returns True
        with patch("time.time", return_value=101.0):
            result = cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN
        assert result is True

        # Second call returns False (one test request already pending)
        assert cb.should_attempt_request() is False


class TestCircuitBreakerStateTransitions:
    """Test CircuitBreaker state transition logic."""

    def test_full_lifecycle_closed_to_open_to_half_open_to_closed(self):
        """Test complete circuit breaker lifecycle."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=3,
            window_duration=60.0,
            timeout_duration=10.0,
        )

        # Start CLOSED
        assert cb.state == CircuitBreakerState.CLOSED

        # Record failures to open circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()
            cb.record_failure()

        # Now OPEN
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.next_test_time == 110.0

        # Wait for timeout
        with patch("time.time", return_value=110.0):
            cb.should_attempt_request()

        # Now HALF_OPEN
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record success
        cb.record_success()

        # Now CLOSED
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_half_open_to_open_on_failure(self):
        """Test HALF_OPEN reopens on failure."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=5.0,
        )

        # Open circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        # Transition to half-open
        with patch("time.time", return_value=105.0):
            cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record failure (should reopen)
        with patch("time.time", return_value=105.5):
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        # New timeout should be set
        assert cb.next_test_time == 110.5  # 105.5 + 5.0


class TestCircuitBreakerReset:
    """Test CircuitBreaker.reset() method."""

    def test_reset_from_open_state(self):
        """Test manual reset from OPEN state."""
        cb = CircuitBreaker(proxy_id="test-proxy", failure_threshold=2)

        # Open the circuit
        cb.record_failure()
        cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 2

        # Reset
        cb.reset()

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert len(cb.failure_window) == 0
        assert cb.next_test_time is None

    def test_reset_from_half_open_state(self):
        """Test manual reset from HALF_OPEN state."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=1.0,
        )

        # Open and transition to half-open
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        with patch("time.time", return_value=101.0):
            cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Reset
        cb.reset()

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0


class TestCircuitBreakerThreadSafety:
    """Test CircuitBreaker thread safety."""

    def test_concurrent_failure_recording(self):
        """Test that concurrent failure recording is thread-safe."""
        import threading

        cb = CircuitBreaker(proxy_id="test-proxy", failure_threshold=100)

        def record_failures():
            for _ in range(10):
                cb.record_failure()

        # Create 10 threads, each recording 10 failures
        threads = [threading.Thread(target=record_failures) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have exactly 100 failures
        assert cb.failure_count == 100

    def test_concurrent_state_transitions(self):
        """Test concurrent state transitions don't cause race conditions."""
        import threading

        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=5,
            timeout_duration=1.0,
        )

        results = []

        def record_and_check():
            with patch("time.time", return_value=100.0):
                cb.record_failure()
                results.append(cb.state)

        # Create multiple threads recording failures
        threads = [threading.Thread(target=record_and_check) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Circuit should be open (threshold is 5, we recorded 10 failures)
        assert cb.state == CircuitBreakerState.OPEN


class TestCircuitBreakerPersistence:
    """Test CircuitBreaker state persistence."""

    @pytest.fixture
    async def temp_storage(self):
        """Create temporary SQLite storage for testing."""
        import tempfile
        from pathlib import Path

        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()
            yield storage
            await storage.close()

    async def test_save_state_disabled_by_default(self, temp_storage):
        """Test that state persistence is disabled by default."""
        cb = CircuitBreaker(proxy_id="test-proxy")
        cb.set_storage(temp_storage)

        # Should not persist (persist_state=False by default)
        await cb.save_state()

        # Verify no state saved
        cb2 = CircuitBreaker(proxy_id="test-proxy")
        cb2.set_storage(temp_storage)
        loaded = await cb2.load_state()
        assert loaded is False

    async def test_save_and_load_closed_state(self):
        """Test saving and loading CLOSED state."""
        from proxywhirl.storage import SQLiteStorage

        storage = SQLiteStorage(":memory:")
        await storage.initialize()

        # Create circuit breaker with persistence enabled
        cb = CircuitBreaker(proxy_id="test-proxy", persist_state=True)
        cb.set_storage(storage)

        # Save state
        await cb.save_state()

        # Load in new instance
        cb2 = CircuitBreaker(proxy_id="test-proxy", persist_state=True)
        cb2.set_storage(storage)
        loaded = await cb2.load_state()

        assert loaded is True
        assert cb2.state == CircuitBreakerState.CLOSED
        assert cb2.failure_count == 0
        assert len(cb2.failure_window) == 0

        await storage.close()

    async def test_save_and_load_open_state(self):
        """Test saving and loading OPEN state with failure history."""
        from proxywhirl.storage import SQLiteStorage

        storage = SQLiteStorage(":memory:")
        await storage.initialize()

        # Create and open circuit breaker
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            persist_state=True,
            failure_threshold=3,
            window_duration=60.0,
            timeout_duration=30.0,
        )
        cb.set_storage(storage)

        # Record failures to open circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 3
        assert cb.next_test_time == 130.0

        # Save state
        await cb.save_state()

        # Load in new instance
        cb2 = CircuitBreaker(proxy_id="test-proxy", persist_state=True)
        cb2.set_storage(storage)
        loaded = await cb2.load_state()

        assert loaded is True
        assert cb2.state == CircuitBreakerState.OPEN
        assert cb2.failure_count == 3
        assert len(cb2.failure_window) == 3
        assert cb2.next_test_time == 130.0
        assert cb2.failure_threshold == 3
        assert cb2.window_duration == 60.0
        assert cb2.timeout_duration == 30.0

        await storage.close()

    async def test_save_and_load_half_open_state(self):
        """Test saving and loading HALF_OPEN state."""
        from proxywhirl.storage import SQLiteStorage

        storage = SQLiteStorage(":memory:")
        await storage.initialize()

        # Create circuit breaker
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            persist_state=True,
            failure_threshold=2,
            timeout_duration=5.0,
        )
        cb.set_storage(storage)

        # Open circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN

        # Transition to half-open
        with patch("time.time", return_value=105.0):
            cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Save state
        await cb.save_state()

        # Load in new instance
        cb2 = CircuitBreaker(proxy_id="test-proxy", persist_state=True)
        cb2.set_storage(storage)
        loaded = await cb2.load_state()

        assert loaded is True
        assert cb2.state == CircuitBreakerState.HALF_OPEN

        await storage.close()

    async def test_persistence_across_restarts(self):
        """Test that state persists across simulated restarts."""
        import tempfile
        from pathlib import Path

        from proxywhirl.storage import SQLiteStorage

        # Use a temporary file for storage
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"

            # First "run" - open circuit and persist
            storage1 = SQLiteStorage(db_path)
            await storage1.initialize()

            cb1 = CircuitBreaker(
                proxy_id="proxy-1",
                persist_state=True,
                failure_threshold=3,
            )
            cb1.set_storage(storage1)

            # Open the circuit
            with patch("time.time", return_value=100.0):
                cb1.record_failure()
                cb1.record_failure()
                cb1.record_failure()

            assert cb1.state == CircuitBreakerState.OPEN
            await cb1.save_state()
            await storage1.close()

            # Second "run" - restore state after restart
            storage2 = SQLiteStorage(db_path)
            await storage2.initialize()

            cb2 = CircuitBreaker(proxy_id="proxy-1", persist_state=True)
            cb2.set_storage(storage2)
            loaded = await cb2.load_state()

            assert loaded is True
            assert cb2.state == CircuitBreakerState.OPEN
            assert cb2.failure_count == 3

            # Circuit should still be open immediately after restart
            with patch("time.time", return_value=100.5):
                assert cb2.should_attempt_request() is False

            await storage2.close()

    async def test_create_with_storage_factory(self):
        """Test create_with_storage factory method."""
        from proxywhirl.models import CircuitBreakerConfig
        from proxywhirl.storage import SQLiteStorage

        storage = SQLiteStorage(":memory:")
        await storage.initialize()

        # Create circuit breaker with config
        config = CircuitBreakerConfig(
            persist_state=True,
            failure_threshold=10,
            window_duration=120.0,
            timeout_duration=60.0,
        )

        cb = await CircuitBreaker.create_with_storage(
            proxy_id="test-proxy",
            storage=storage,
            config=config,
        )

        assert cb.proxy_id == "test-proxy"
        assert cb.persist_state is True
        assert cb.failure_threshold == 10
        assert cb.window_duration == 120.0
        assert cb.timeout_duration == 60.0

        await storage.close()

    async def test_create_with_storage_restores_state(self):
        """Test create_with_storage restores existing state."""
        from proxywhirl.models import CircuitBreakerConfig
        from proxywhirl.storage import SQLiteStorage

        storage = SQLiteStorage(":memory:")
        await storage.initialize()

        # Create and persist an open circuit
        cb1 = CircuitBreaker(
            proxy_id="test-proxy",
            persist_state=True,
            failure_threshold=2,
        )
        cb1.set_storage(storage)

        with patch("time.time", return_value=100.0):
            cb1.record_failure()
            cb1.record_failure()

        await cb1.save_state()

        # Create new instance using factory - should restore state
        config = CircuitBreakerConfig(persist_state=True)
        cb2 = await CircuitBreaker.create_with_storage(
            proxy_id="test-proxy",
            storage=storage,
            config=config,
        )

        assert cb2.state == CircuitBreakerState.OPEN
        assert cb2.failure_count == 2

        await storage.close()

    async def test_delete_state(self):
        """Test deleting persisted state."""
        from proxywhirl.storage import SQLiteStorage

        storage = SQLiteStorage(":memory:")
        await storage.initialize()

        # Create and persist state
        cb = CircuitBreaker(proxy_id="test-proxy", persist_state=True)
        cb.set_storage(storage)

        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        await cb.save_state()

        # Delete state
        await cb.delete_state()

        # Verify state is gone
        cb2 = CircuitBreaker(proxy_id="test-proxy", persist_state=True)
        cb2.set_storage(storage)
        loaded = await cb2.load_state()
        assert loaded is False

        await storage.close()

    async def test_multiple_proxies_independent_state(self):
        """Test that different proxies maintain independent state."""
        from proxywhirl.storage import SQLiteStorage

        storage = SQLiteStorage(":memory:")
        await storage.initialize()

        # Create two circuit breakers
        cb1 = CircuitBreaker(proxy_id="proxy-1", persist_state=True, failure_threshold=2)
        cb1.set_storage(storage)

        cb2 = CircuitBreaker(proxy_id="proxy-2", persist_state=True, failure_threshold=2)
        cb2.set_storage(storage)

        # Open first circuit
        with patch("time.time", return_value=100.0):
            cb1.record_failure()
            cb1.record_failure()

        await cb1.save_state()
        await cb2.save_state()

        # Load states
        cb1_new = CircuitBreaker(proxy_id="proxy-1", persist_state=True)
        cb1_new.set_storage(storage)
        await cb1_new.load_state()

        cb2_new = CircuitBreaker(proxy_id="proxy-2", persist_state=True)
        cb2_new.set_storage(storage)
        await cb2_new.load_state()

        # First should be open, second should be closed
        assert cb1_new.state == CircuitBreakerState.OPEN
        assert cb2_new.state == CircuitBreakerState.CLOSED

        await storage.close()

    @pytest.mark.skip(
        reason="SQLite :memory: with aiosqlite uses separate db per connection; requires file-based db for proper testing"
    )
    async def test_auto_persist_on_state_transition(self):
        """Test that state is automatically persisted on transitions."""
        import asyncio

        from proxywhirl.storage import SQLiteStorage

        storage = SQLiteStorage(":memory:")
        await storage.initialize()

        # Create circuit breaker with auto-persistence
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            persist_state=True,
            failure_threshold=2,
        )
        cb.set_storage(storage)

        # Record failures (should auto-persist)
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        # Give async task time to complete
        await asyncio.sleep(0.1)

        # Verify state was persisted
        cb2 = CircuitBreaker(proxy_id="test-proxy", persist_state=True)
        cb2.set_storage(storage)
        loaded = await cb2.load_state()

        assert loaded is True
        assert cb2.state == CircuitBreakerState.OPEN

        await storage.close()


class TestCircuitBreakerHalfOpenRaceCondition:
    """Test CircuitBreaker HALF_OPEN state race condition prevention."""

    def test_only_one_request_allowed_in_half_open_state(self):
        """Test that only one request is allowed when in HALF_OPEN state.

        This verifies that the _half_open_pending flag prevents multiple
        concurrent test requests.
        """
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=5.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN

        # Transition to HALF_OPEN
        with patch("time.time", return_value=105.0):
            first_result = cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN
        assert first_result is True

        # Second request should be blocked (pending flag is set)
        second_result = cb.should_attempt_request()
        assert second_result is False

        # Third request should also be blocked
        third_result = cb.should_attempt_request()
        assert third_result is False

    def test_concurrent_threads_blocked_when_one_is_testing(self):
        """Test that concurrent threads are blocked when one is testing.

        Multiple threads trying to get a request slot in HALF_OPEN state
        should result in exactly one True and the rest False.
        """
        import threading

        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=5.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN

        results = []
        barrier = threading.Barrier(10)

        def attempt_request():
            barrier.wait()  # Synchronize all threads to start at the same time
            with patch("time.time", return_value=105.0):
                result = cb.should_attempt_request()
                results.append(result)

        # Create 10 threads that will all try to get a request slot
        threads = [threading.Thread(target=attempt_request) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Exactly one thread should have gotten True
        assert results.count(True) == 1
        assert results.count(False) == 9
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_half_open_pending_flag_resets_on_success(self):
        """Test that _half_open_pending flag resets when recording success.

        After a successful test request, the circuit should close and
        allow all subsequent requests.
        """
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=5.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        # Transition to HALF_OPEN
        with patch("time.time", return_value=105.0):
            assert cb.should_attempt_request() is True

        assert cb.state == CircuitBreakerState.HALF_OPEN
        assert cb._half_open_pending is True

        # Second request blocked
        assert cb.should_attempt_request() is False

        # Record success - should reset flag and close circuit
        cb.record_success()

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb._half_open_pending is False

        # Now requests should be allowed again
        assert cb.should_attempt_request() is True
        assert cb.should_attempt_request() is True

    def test_half_open_pending_flag_resets_on_failure(self):
        """Test that _half_open_pending flag resets when recording failure.

        After a failed test request, the circuit should reopen and
        the pending flag should be reset.
        """
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=5.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        # Transition to HALF_OPEN
        with patch("time.time", return_value=105.0):
            assert cb.should_attempt_request() is True

        assert cb.state == CircuitBreakerState.HALF_OPEN
        assert cb._half_open_pending is True

        # Second request blocked
        assert cb.should_attempt_request() is False

        # Record failure - should reset flag and reopen circuit
        with patch("time.time", return_value=105.5):
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert cb._half_open_pending is False

        # Now requests should be blocked (circuit is open)
        with patch("time.time", return_value=106.0):
            assert cb.should_attempt_request() is False

    def test_half_open_pending_flag_resets_on_state_transition(self):
        """Test that _half_open_pending flag resets on any state transition.

        Covers the reset() method which transitions back to CLOSED.
        """
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=5.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        # Transition to HALF_OPEN
        with patch("time.time", return_value=105.0):
            assert cb.should_attempt_request() is True

        assert cb.state == CircuitBreakerState.HALF_OPEN
        assert cb._half_open_pending is True

        # Manual reset should clear the flag
        cb.reset()

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb._half_open_pending is False

        # Requests should be allowed
        assert cb.should_attempt_request() is True
