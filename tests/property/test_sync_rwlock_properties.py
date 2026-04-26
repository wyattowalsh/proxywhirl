"""
Property-based tests for SyncRWLock using Hypothesis.

These tests verify the core invariants of readers-writer locks:
1. Multiple readers can acquire the lock simultaneously
2. Writers have exclusive access
3. No readers allowed while writing
4. No writers allowed while reading
5. Writer preference over readers
6. No deadlocks under contention
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from proxywhirl.rwlock import SyncRWLock

# Mark all tests in this module as slow since they use time.sleep for lock testing
pytestmark = pytest.mark.slow


class TestSyncRWLockConcurrentReads:
    """Property tests for concurrent read access."""

    @given(num_readers=st.integers(min_value=2, max_value=20))
    @settings(deadline=None, max_examples=50)
    def test_concurrent_reads_dont_block_each_other(self, num_readers: int):
        """Property: Concurrent reads don't block each other.

        Multiple readers should be able to hold the lock simultaneously,
        demonstrating that read operations can proceed in parallel.
        """
        lock = SyncRWLock()
        active_readers: list[int] = []
        max_concurrent = 0
        lock_for_list = threading.Lock()
        results: list[str] = []

        def reader(reader_id: int) -> None:
            nonlocal max_concurrent
            with lock.read_lock():
                with lock_for_list:
                    active_readers.append(reader_id)
                    current_count = len(active_readers)
                    if current_count > max_concurrent:
                        max_concurrent = current_count
                    results.append(f"reader_{reader_id}_acquired")

                # Hold the lock briefly to ensure overlap
                time.sleep(0.01)

                with lock_for_list:
                    results.append(f"reader_{reader_id}_released")
                    active_readers.remove(reader_id)

        # Run all readers concurrently
        with ThreadPoolExecutor(max_workers=num_readers) as executor:
            futures = [executor.submit(reader, i) for i in range(num_readers)]
            for future in as_completed(futures):
                future.result()  # Raise any exceptions

        # All readers should have completed
        assert len(results) == num_readers * 2
        assert len(active_readers) == 0

        # Verify concurrent reads occurred (at least 2 readers were active at once)
        # Note: With small num_readers or fast execution, this might not always happen
        if num_readers >= 4:
            assert max_concurrent >= 2, (
                f"Expected at least 2 concurrent readers with {num_readers} readers, "
                f"got max_concurrent={max_concurrent}"
            )

        # Verify all readers acquired
        acquired_events = [e for e in results if "acquired" in e]
        assert len(acquired_events) == num_readers


class TestSyncRWLockWriteBlocking:
    """Property tests for write blocking behavior."""

    @given(num_operations=st.integers(min_value=2, max_value=10))
    @settings(deadline=None, max_examples=50)
    def test_write_blocks_all_reads(self, num_operations: int):
        """Property: Writers have exclusive access - no concurrent readers or writers.

        When a writer holds the lock, no other thread (reader or writer)
        should be able to acquire it.
        """
        lock = SyncRWLock()
        active_operations: list[str] = []
        lock_for_list = threading.Lock()
        violations: list[str] = []

        def writer(writer_id: int) -> None:
            with lock.write_lock():
                with lock_for_list:
                    active_operations.append(f"writer_{writer_id}")
                    # Invariant: Only one operation (this writer) should be active
                    if len(active_operations) != 1:
                        violations.append(
                            f"Writer {writer_id} should have exclusive access. "
                            f"Active: {active_operations.copy()}"
                        )

                time.sleep(0.01)

                with lock_for_list:
                    active_operations.remove(f"writer_{writer_id}")

        # Run writers concurrently (lock should serialize them)
        with ThreadPoolExecutor(max_workers=num_operations) as executor:
            futures = [executor.submit(writer, i) for i in range(num_operations)]
            for future in as_completed(futures):
                future.result()

        # No violations should have occurred
        assert len(violations) == 0, f"Violations: {violations}"

    @given(
        num_readers=st.integers(min_value=2, max_value=8),
        num_writers=st.integers(min_value=1, max_value=4),
    )
    @settings(deadline=None, max_examples=50)
    def test_no_readers_while_writing(self, num_readers: int, num_writers: int):
        """Property: No readers can acquire lock while writer holds it."""
        lock = SyncRWLock()
        active_readers = 0
        active_writers = 0
        count_lock = threading.Lock()
        violations: list[str] = []

        def reader(reader_id: int) -> None:
            nonlocal active_readers
            with lock.read_lock():
                with count_lock:
                    active_readers += 1
                    # Invariant: No writers should be active
                    if active_writers > 0:
                        violations.append(f"Reader {reader_id} active while writer active")

                time.sleep(0.005)

                with count_lock:
                    active_readers -= 1

        def writer(writer_id: int) -> None:
            nonlocal active_writers
            with lock.write_lock():
                with count_lock:
                    active_writers += 1
                    # Invariant: No readers should be active
                    if active_readers > 0:
                        violations.append(
                            f"Writer {writer_id} active while {active_readers} readers active"
                        )
                    # Invariant: Only one writer should be active
                    if active_writers > 1:
                        violations.append(f"Writer {writer_id} active while other writer active")

                time.sleep(0.01)

                with count_lock:
                    active_writers -= 1

        # Mix readers and writers
        with ThreadPoolExecutor(max_workers=num_readers + num_writers) as executor:
            futures = [executor.submit(reader, i) for i in range(num_readers)]
            futures.extend([executor.submit(writer, i) for i in range(num_writers)])
            for future in as_completed(futures):
                future.result()

        # No invariant violations should occur
        assert len(violations) == 0, f"Invariant violations: {violations}"


class TestSyncRWLockDeadlockFree:
    """Property tests for deadlock prevention."""

    @given(
        num_readers=st.integers(min_value=2, max_value=10),
        num_writers=st.integers(min_value=1, max_value=5),
        num_rounds=st.integers(min_value=2, max_value=5),
    )
    @settings(deadline=None, max_examples=30)
    def test_no_deadlocks_under_contention(
        self, num_readers: int, num_writers: int, num_rounds: int
    ):
        """Property: No deadlocks occur under high contention.

        With many readers and writers competing for the lock across
        multiple rounds, the system should always make progress
        (no thread should be stuck indefinitely).
        """
        lock = SyncRWLock()
        completed_operations = []
        operations_lock = threading.Lock()
        timeout_seconds = 10.0  # Generous timeout to detect deadlocks

        def reader(reader_id: int, round_id: int) -> None:
            with lock.read_lock():
                time.sleep(0.001)
                with operations_lock:
                    completed_operations.append(f"R{round_id}_{reader_id}")

        def writer(writer_id: int, round_id: int) -> None:
            with lock.write_lock():
                time.sleep(0.002)
                with operations_lock:
                    completed_operations.append(f"W{round_id}_{writer_id}")

        start_time = time.time()
        total_operations = 0

        # Run multiple rounds
        for round_id in range(num_rounds):
            with ThreadPoolExecutor(max_workers=num_readers + num_writers) as executor:
                futures = [executor.submit(reader, i, round_id) for i in range(num_readers)]
                futures.extend([executor.submit(writer, i, round_id) for i in range(num_writers)])

                for future in as_completed(futures, timeout=timeout_seconds):
                    future.result()
                    total_operations += 1

                    # Check for timeout (potential deadlock)
                    elapsed = time.time() - start_time
                    if elapsed > timeout_seconds:
                        pytest.fail(
                            f"Potential deadlock detected: {total_operations} operations "
                            f"completed in {elapsed:.2f}s"
                        )

        # All operations should have completed
        expected_operations = num_rounds * (num_readers + num_writers)
        assert len(completed_operations) == expected_operations, (
            f"Expected {expected_operations} operations, got {len(completed_operations)}"
        )

    @given(sequence=st.lists(st.booleans(), min_size=5, max_size=20))
    @settings(deadline=None, max_examples=50)
    def test_alternating_reads_writes_no_deadlock(self, sequence: list[bool]):
        """Property: Alternating read/write sequences complete without deadlock."""
        lock = SyncRWLock()
        active_readers = 0
        active_writers = 0
        count_lock = threading.Lock()
        operations: list[str] = []
        violations: list[str] = []

        def read_op(op_id: int) -> None:
            nonlocal active_readers
            with lock.read_lock():
                with count_lock:
                    active_readers += 1
                    operations.append(f"R{op_id}_start")
                    # Verify no writers active
                    if active_writers > 0:
                        violations.append(f"Reader {op_id}: writer active")

                time.sleep(0.001)

                with count_lock:
                    operations.append(f"R{op_id}_end")
                    active_readers -= 1

        def write_op(op_id: int) -> None:
            nonlocal active_writers
            with lock.write_lock():
                with count_lock:
                    active_writers += 1
                    operations.append(f"W{op_id}_start")
                    # Verify exclusive access
                    if active_readers > 0:
                        violations.append(f"Writer {op_id}: {active_readers} readers active")
                    if active_writers > 1:
                        violations.append(f"Writer {op_id}: {active_writers} writers active")

                time.sleep(0.001)

                with count_lock:
                    operations.append(f"W{op_id}_end")
                    active_writers -= 1

        # Execute sequence (True=read, False=write)
        with ThreadPoolExecutor(max_workers=len(sequence)) as executor:
            futures = [
                executor.submit(read_op if is_read else write_op, i)
                for i, is_read in enumerate(sequence)
            ]
            for future in as_completed(futures, timeout=30.0):
                future.result()

        # Verify all operations completed
        assert len(operations) == len(sequence) * 2
        assert len(violations) == 0, f"Violations: {violations}"


class TestSyncRWLockInvariants:
    """Property tests for internal state invariants."""

    @given(num_iterations=st.integers(min_value=5, max_value=20))
    @settings(deadline=None, max_examples=50)
    def test_lock_state_consistency(self, num_iterations: int):
        """Property: Lock internal state remains consistent across many operations."""
        lock = SyncRWLock()
        violations: list[str] = []
        violations_lock = threading.Lock()

        def mixed_operations(op_id: int) -> None:
            # Alternate between read and write
            if op_id % 2 == 0:
                with lock.read_lock():
                    # Verify state consistency
                    if lock._readers < 1:
                        with violations_lock:
                            violations.append(f"Op {op_id}: readers={lock._readers} (expected >=1)")
                    if lock._writers != 0:
                        with violations_lock:
                            violations.append(f"Op {op_id}: writers={lock._writers} (expected 0)")
                    time.sleep(0.001)
            else:
                with lock.write_lock():
                    # Verify state consistency
                    if lock._readers != 0:
                        with violations_lock:
                            violations.append(
                                f"Op {op_id}: readers={lock._readers} (expected 0 for writer)"
                            )
                    if lock._writers != 1:
                        with violations_lock:
                            violations.append(f"Op {op_id}: writers={lock._writers} (expected 1)")
                    time.sleep(0.001)

        # Run many operations
        with ThreadPoolExecutor(max_workers=num_iterations) as executor:
            futures = [executor.submit(mixed_operations, i) for i in range(num_iterations)]
            for future in as_completed(futures):
                future.result()

        # Final state should be clean
        assert lock._readers == 0, f"Final readers count: {lock._readers}"
        assert lock._writers == 0, f"Final writers count: {lock._writers}"
        assert lock._write_waiters == 0, f"Final write waiters: {lock._write_waiters}"
        assert len(violations) == 0, f"State violations: {violations}"

    def test_context_manager_exception_handling(self):
        """Property: Lock properly releases even when exception occurs in context."""
        lock = SyncRWLock()

        # Test read lock exception handling
        with pytest.raises(ValueError), lock.read_lock():
            assert lock._readers == 1
            raise ValueError("Test exception")

        # Lock should be released
        assert lock._readers == 0

        # Test write lock exception handling
        with pytest.raises(ValueError), lock.write_lock():
            assert lock._writers == 1
            raise ValueError("Test exception")

        # Lock should be released
        assert lock._writers == 0


class TestSyncRWLockWriterPreference:
    """Property tests for writer preference behavior."""

    @given(
        num_readers=st.integers(min_value=3, max_value=8),
        num_writers=st.integers(min_value=1, max_value=3),
    )
    @settings(deadline=None, max_examples=30)
    def test_writer_not_starved_by_readers(self, num_readers: int, num_writers: int):
        """Property: Writers eventually get access even with many readers.

        This tests that writers are not starved by a continuous stream of readers.
        """
        lock = SyncRWLock()
        writer_completed: list[float] = []
        writer_lock = threading.Lock()

        def reader(reader_id: int) -> None:
            with lock.read_lock():
                time.sleep(0.02)  # Hold read lock briefly

        def writer(writer_id: int) -> None:
            start = time.time()
            with lock.write_lock():
                elapsed = time.time() - start
                with writer_lock:
                    writer_completed.append(elapsed)
                time.sleep(0.01)

        # Start readers first
        with ThreadPoolExecutor(max_workers=num_readers + num_writers) as executor:
            reader_futures = [executor.submit(reader, i) for i in range(num_readers)]
            time.sleep(0.005)  # Let readers start

            # Start writers (should eventually complete despite readers)
            writer_futures = [executor.submit(writer, i) for i in range(num_writers)]

            # Wait for all to complete with timeout
            for future in as_completed(reader_futures + writer_futures, timeout=30.0):
                future.result()

        # All writers should have completed
        assert len(writer_completed) == num_writers, (
            f"Expected {num_writers} writers to complete, got {len(writer_completed)}"
        )

    def test_writer_waits_for_readers_to_finish(self):
        """Property: Writer must wait for all active readers to finish."""
        lock = SyncRWLock()
        reader_finished = threading.Event()
        writer_started = threading.Event()
        reader_was_finished_when_writer_started = None

        def long_reader() -> None:
            with lock.read_lock():
                time.sleep(0.05)
                reader_finished.set()

        def writer() -> None:
            nonlocal reader_was_finished_when_writer_started
            with lock.write_lock():
                reader_was_finished_when_writer_started = reader_finished.is_set()
                writer_started.set()
                time.sleep(0.01)

        # Start reader first
        reader_thread = threading.Thread(target=long_reader)
        reader_thread.start()
        time.sleep(0.01)  # Ensure reader acquires first

        # Start writer (should wait)
        writer_thread = threading.Thread(target=writer)
        writer_thread.start()

        reader_thread.join(timeout=5.0)
        writer_thread.join(timeout=5.0)

        assert reader_finished.is_set(), "Reader should have finished"
        assert writer_started.is_set(), "Writer should have started"
        assert reader_was_finished_when_writer_started, (
            "Reader should have been finished when writer started"
        )

    def test_readers_wait_for_writer_to_finish(self):
        """Property: Readers must wait for active writer to finish."""
        lock = SyncRWLock()
        writer_finished = threading.Event()
        readers_started: list[tuple[int, bool]] = []
        readers_lock = threading.Lock()

        def long_writer() -> None:
            with lock.write_lock():
                time.sleep(0.05)
                writer_finished.set()

        def reader(reader_id: int) -> None:
            with lock.read_lock(), readers_lock:
                readers_started.append((reader_id, writer_finished.is_set()))

        # Start writer first
        writer_thread = threading.Thread(target=long_writer)
        writer_thread.start()
        time.sleep(0.01)  # Ensure writer acquires first

        # Start readers (should wait)
        num_readers = 5
        reader_threads = [threading.Thread(target=reader, args=(i,)) for i in range(num_readers)]
        for t in reader_threads:
            t.start()

        writer_thread.join(timeout=5.0)
        for t in reader_threads:
            t.join(timeout=5.0)

        # All readers should have started after writer finished
        assert len(readers_started) == num_readers
        assert all(finished for _, finished in readers_started), (
            f"Some readers started before writer finished: {readers_started}"
        )
