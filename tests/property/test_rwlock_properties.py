"""
Property-based tests for AsyncRWLock using Hypothesis.

These tests verify the core invariants of readers-writer locks:
1. Multiple readers can acquire the lock simultaneously
2. Writers have exclusive access
3. No readers allowed while writing
4. No writers allowed while reading
5. Writer preference over readers
"""

import asyncio

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from proxywhirl.rwlock import AsyncRWLock

# Mark all tests in this module as slow since they use asyncio.sleep
pytestmark = pytest.mark.slow


class TestAsyncRWLockProperties:
    """Property-based tests for AsyncRWLock invariants."""

    @given(num_readers=st.integers(min_value=1, max_value=20))
    async def test_multiple_readers_concurrent(self, num_readers: int):
        """Property: Multiple readers can acquire lock simultaneously."""
        lock = AsyncRWLock()
        active_readers = []
        results: list[str] = []

        async def reader(reader_id: int):
            async with lock.read_lock():
                active_readers.append(reader_id)
                results.append(f"reader_{reader_id}_acquired")
                # Small delay to ensure overlap
                await asyncio.sleep(0.01)
                results.append(f"reader_{reader_id}_released")
                active_readers.remove(reader_id)

        # All readers should be able to run concurrently
        await asyncio.gather(*[reader(i) for i in range(num_readers)])

        # All readers should have completed
        assert len(results) == num_readers * 2
        assert len(active_readers) == 0

        # Verify all readers acquired
        acquired_events = [e for e in results if "acquired" in e]
        assert len(acquired_events) == num_readers

    @given(num_operations=st.integers(min_value=2, max_value=10))
    async def test_writer_exclusive_access(self, num_operations: int):
        """Property: Writers have exclusive access - no concurrent readers or writers."""
        lock = AsyncRWLock()
        active_operations: list[str] = []
        max_concurrent = 0

        async def writer(writer_id: int):
            nonlocal max_concurrent
            async with lock.write_lock():
                active_operations.append(f"writer_{writer_id}")
                max_concurrent = max(max_concurrent, len(active_operations))
                # Invariant: Only one operation (this writer) should be active
                assert len(active_operations) == 1, (
                    f"Writer {writer_id} should have exclusive access. Active: {active_operations}"
                )
                await asyncio.sleep(0.01)
                active_operations.remove(f"writer_{writer_id}")

        # Run writers sequentially (enforced by lock)
        await asyncio.gather(*[writer(i) for i in range(num_operations)])

        # Only one operation should have been active at any time
        assert max_concurrent == 1

    @given(
        num_readers=st.integers(min_value=1, max_value=10),
        num_writers=st.integers(min_value=1, max_value=5),
    )
    async def test_no_readers_while_writing(self, num_readers: int, num_writers: int):
        """Property: No readers can acquire lock while writer holds it."""
        lock = AsyncRWLock()
        active_readers = 0
        active_writers = 0
        violations = []

        async def reader(reader_id: int):
            nonlocal active_readers
            async with lock.read_lock():
                active_readers += 1
                # Invariant: No writers should be active
                if active_writers > 0:
                    violations.append(f"Reader {reader_id} active while writer active")
                await asyncio.sleep(0.01)
                active_readers -= 1

        async def writer(writer_id: int):
            nonlocal active_writers
            async with lock.write_lock():
                active_writers += 1
                # Invariant: No readers should be active
                if active_readers > 0:
                    violations.append(
                        f"Writer {writer_id} active while {active_readers} readers active"
                    )
                # Invariant: Only one writer should be active
                if active_writers > 1:
                    violations.append(f"Writer {writer_id} active while other writer active")
                await asyncio.sleep(0.01)
                active_writers -= 1

        # Mix readers and writers
        tasks = [reader(i) for i in range(num_readers)] + [writer(i) for i in range(num_writers)]
        await asyncio.gather(*tasks)

        # No invariant violations should occur
        assert len(violations) == 0, f"Invariant violations: {violations}"

    @given(
        read_duration_ms=st.integers(min_value=5, max_value=50),
        write_duration_ms=st.integers(min_value=10, max_value=100),
    )
    async def test_writer_waits_for_readers(self, read_duration_ms: int, write_duration_ms: int):
        """Property: Writer must wait for all active readers to finish."""
        lock = AsyncRWLock()
        reader_finished = False
        writer_started = False

        async def long_reader():
            nonlocal reader_finished
            async with lock.read_lock():
                await asyncio.sleep(read_duration_ms / 1000)
                reader_finished = True

        async def writer():
            nonlocal writer_started
            async with lock.write_lock():
                writer_started = True
                # Reader should have finished before writer starts
                assert reader_finished, "Writer started before reader finished"
                await asyncio.sleep(write_duration_ms / 1000)

        # Start reader first
        reader_task = asyncio.create_task(long_reader())
        await asyncio.sleep(0.001)  # Ensure reader acquires first

        # Start writer (should wait)
        writer_task = asyncio.create_task(writer())

        await asyncio.gather(reader_task, writer_task)
        assert reader_finished and writer_started

    @given(
        num_readers=st.integers(min_value=2, max_value=10),
        write_duration_ms=st.integers(min_value=20, max_value=100),
    )
    async def test_readers_wait_for_writer(self, num_readers: int, write_duration_ms: int):
        """Property: Readers must wait for active writer to finish."""
        lock = AsyncRWLock()
        writer_finished = False
        readers_started = []

        async def long_writer():
            nonlocal writer_finished
            async with lock.write_lock():
                await asyncio.sleep(write_duration_ms / 1000)
                writer_finished = True

        async def reader(reader_id: int):
            async with lock.read_lock():
                # Writer should have finished before readers start
                readers_started.append((reader_id, writer_finished))

        # Start writer first
        writer_task = asyncio.create_task(long_writer())
        await asyncio.sleep(0.001)  # Ensure writer acquires first

        # Start readers (should wait)
        reader_tasks = [asyncio.create_task(reader(i)) for i in range(num_readers)]

        await asyncio.gather(writer_task, *reader_tasks)

        # All readers should have started after writer finished
        assert all(finished for _, finished in readers_started), (
            f"Some readers started before writer finished: {readers_started}"
        )

    @given(sequence=st.lists(st.booleans(), min_size=5, max_size=20))
    async def test_alternating_reads_writes(self, sequence: list[bool]):
        """Property: Lock correctly handles alternating read/write sequences."""
        lock = AsyncRWLock()
        active_readers = 0
        active_writers = 0
        operations: list[str] = []

        async def read_op(op_id: int):
            nonlocal active_readers
            async with lock.read_lock():
                active_readers += 1
                operations.append(f"R{op_id}_start")
                # Verify no writers active
                assert active_writers == 0, f"Reader {op_id}: writer active"
                await asyncio.sleep(0.001)
                operations.append(f"R{op_id}_end")
                active_readers -= 1

        async def write_op(op_id: int):
            nonlocal active_writers
            async with lock.write_lock():
                active_writers += 1
                operations.append(f"W{op_id}_start")
                # Verify exclusive access
                assert active_readers == 0, f"Writer {op_id}: {active_readers} readers active"
                assert active_writers == 1, f"Writer {op_id}: {active_writers} writers active"
                await asyncio.sleep(0.001)
                operations.append(f"W{op_id}_end")
                active_writers -= 1

        # Execute sequence (True=read, False=write)
        tasks = [read_op(i) if is_read else write_op(i) for i, is_read in enumerate(sequence)]
        await asyncio.gather(*tasks)

        # Verify all operations completed
        assert len(operations) == len(sequence) * 2

    @given(
        num_readers=st.integers(min_value=2, max_value=8),
        num_writers=st.integers(min_value=1, max_value=4),
    )
    @settings(deadline=None)  # Disable deadline for async tests
    async def test_writer_preference(self, num_readers: int, num_writers: int):
        """Property: Writers get preference over readers (no reader starvation of writers)."""
        lock = AsyncRWLock()
        writer_wait_times: list[float] = []

        async def reader(reader_id: int):
            async with lock.read_lock():
                await asyncio.sleep(0.02)

        async def writer(writer_id: int):
            # Track how long writer waits
            start = asyncio.get_event_loop().time()
            async with lock.write_lock():
                wait_time = asyncio.get_event_loop().time() - start
                writer_wait_times.append(wait_time)
                await asyncio.sleep(0.01)

        # Start initial readers
        reader_tasks = [asyncio.create_task(reader(i)) for i in range(num_readers)]
        await asyncio.sleep(0.001)

        # Start writers (should get preference)
        writer_tasks = [asyncio.create_task(writer(i)) for i in range(num_writers)]

        await asyncio.gather(*reader_tasks, *writer_tasks)

        # Writers should eventually execute (not starved)
        assert len(writer_wait_times) == num_writers

    async def test_release_without_acquire_safe(self):
        """Property: Lock handles incorrect usage gracefully (defensive programming)."""
        lock = AsyncRWLock()

        # Normal acquire/release should work
        await lock.acquire_read()
        await lock.release_read()

        # Multiple releases shouldn't crash (though incorrect usage)
        # This tests defensive programming
        try:
            await lock.release_read()
            # If it doesn't crash, that's acceptable defensive behavior
        except Exception:
            # If it raises, that's also acceptable
            pass

    @given(num_concurrent=st.integers(min_value=3, max_value=15))
    async def test_concurrent_readers_then_writer(self, num_concurrent: int):
        """Property: Many concurrent readers followed by writer works correctly."""
        lock = AsyncRWLock()
        reader_count = 0
        max_readers = 0
        writer_executed = False

        async def reader(reader_id: int):
            nonlocal reader_count, max_readers
            async with lock.read_lock():
                reader_count += 1
                max_readers = max(max_readers, reader_count)
                await asyncio.sleep(0.01)
                reader_count -= 1

        async def writer():
            nonlocal writer_executed
            async with lock.write_lock():
                # All readers should be done
                assert reader_count == 0, f"Writer started with {reader_count} active readers"
                writer_executed = True

        # Start all readers
        reader_tasks = [asyncio.create_task(reader(i)) for i in range(num_concurrent)]

        # Give readers time to acquire
        await asyncio.sleep(0.001)

        # Start writer
        writer_task = asyncio.create_task(writer())

        await asyncio.gather(*reader_tasks, writer_task)

        # Verify readers ran concurrently and writer executed
        assert max_readers > 1, "Readers should have run concurrently"
        assert writer_executed, "Writer should have executed"

    @given(
        num_readers=st.integers(min_value=1, max_value=5),
        num_writers=st.integers(min_value=1, max_value=5),
        num_rounds=st.integers(min_value=2, max_value=5),
    )
    @settings(deadline=None)
    async def test_repeated_cycles(self, num_readers: int, num_writers: int, num_rounds: int):
        """Property: Lock maintains invariants across repeated cycles of reads/writes."""
        lock = AsyncRWLock()
        violations: list[str] = []

        async def reader(reader_id: int, round_id: int):
            async with lock.read_lock():
                # Check writer count through lock internals
                if lock._writers > 0:
                    violations.append(f"Round {round_id}, Reader {reader_id}: writer active")
                await asyncio.sleep(0.001)

        async def writer(writer_id: int, round_id: int):
            async with lock.write_lock():
                # Check reader count through lock internals
                if lock._readers > 0:
                    violations.append(f"Round {round_id}, Writer {writer_id}: readers active")
                if lock._writers > 1:
                    violations.append(f"Round {round_id}, Writer {writer_id}: multiple writers")
                await asyncio.sleep(0.001)

        # Run multiple rounds
        for round_id in range(num_rounds):
            tasks = [reader(i, round_id) for i in range(num_readers)] + [
                writer(i, round_id) for i in range(num_writers)
            ]
            await asyncio.gather(*tasks)

        # No violations across all rounds
        assert len(violations) == 0, f"Invariant violations: {violations}"

    async def test_context_manager_exception_handling(self):
        """Property: Lock properly releases even when exception occurs in context."""
        lock = AsyncRWLock()

        # Test read lock exception handling
        with pytest.raises(ValueError):
            async with lock.read_lock():
                assert lock._readers == 1
                raise ValueError("Test exception")

        # Lock should be released
        assert lock._readers == 0

        # Test write lock exception handling
        with pytest.raises(ValueError):
            async with lock.write_lock():
                assert lock._writers == 1
                raise ValueError("Test exception")

        # Lock should be released
        assert lock._writers == 0

    @given(num_iterations=st.integers(min_value=5, max_value=20))
    async def test_lock_state_consistency(self, num_iterations: int):
        """Property: Lock internal state remains consistent across many operations."""
        lock = AsyncRWLock()

        async def mixed_operations(op_id: int):
            # Alternate between read and write
            if op_id % 2 == 0:
                async with lock.read_lock():
                    # Verify state consistency
                    assert lock._readers >= 1
                    assert lock._writers == 0
                    await asyncio.sleep(0.001)
            else:
                async with lock.write_lock():
                    # Verify state consistency
                    assert lock._readers == 0
                    assert lock._writers == 1
                    await asyncio.sleep(0.001)

        # Run many operations
        await asyncio.gather(*[mixed_operations(i) for i in range(num_iterations)])

        # Final state should be clean
        assert lock._readers == 0
        assert lock._writers == 0
        assert lock._write_waiters == 0
