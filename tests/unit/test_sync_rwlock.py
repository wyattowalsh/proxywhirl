"""
Unit tests for SyncRWLock (synchronous readers-writer lock).

Tests verify that the SyncRWLock provides:
1. Multiple concurrent readers
2. Exclusive writer access
3. Writer preference (no writer starvation)
4. Thread safety
"""

import threading
import time

from proxywhirl.rwlock import SyncRWLock


class TestSyncRWLockBasicOperations:
    """Test basic SyncRWLock operations."""

    def test_read_lock_context_manager(self):
        """Test read lock as context manager."""
        lock = SyncRWLock()
        entered = False

        with lock.read_lock():
            entered = True

        assert entered

    def test_write_lock_context_manager(self):
        """Test write lock as context manager."""
        lock = SyncRWLock()
        entered = False

        with lock.write_lock():
            entered = True

        assert entered

    def test_nested_read_locks(self):
        """Test that multiple read locks can be held."""
        lock = SyncRWLock()
        results = []

        def reader(n):
            with lock.read_lock():
                results.append(f"enter-{n}")
                time.sleep(0.01)
                results.append(f"exit-{n}")

        t1 = threading.Thread(target=reader, args=(1,))
        t2 = threading.Thread(target=reader, args=(2,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Both should have entered (concurrent reads allowed)
        assert "enter-1" in results
        assert "enter-2" in results


class TestSyncRWLockConcurrentReaders:
    """Test that multiple readers can hold the lock simultaneously."""

    def test_multiple_concurrent_readers(self):
        """Test that multiple threads can read concurrently."""
        lock = SyncRWLock()
        concurrent_count = []
        count_lock = threading.Lock()
        active_readers = 0

        def reader():
            nonlocal active_readers
            with lock.read_lock():
                with count_lock:
                    active_readers += 1
                    concurrent_count.append(active_readers)
                time.sleep(0.05)  # Hold lock briefly
                with count_lock:
                    active_readers -= 1

        threads = [threading.Thread(target=reader) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have had multiple concurrent readers
        assert max(concurrent_count) > 1


class TestSyncRWLockExclusiveWriter:
    """Test that writers get exclusive access."""

    def test_writer_excludes_readers(self):
        """Test that writer blocks readers."""
        lock = SyncRWLock()
        write_started = threading.Event()
        reader_waited = False

        def writer():
            with lock.write_lock():
                write_started.set()
                time.sleep(0.1)  # Hold write lock

        def reader():
            nonlocal reader_waited
            write_started.wait()  # Wait for writer to start
            start = time.time()
            with lock.read_lock():
                elapsed = time.time() - start
                # Should have waited for writer to release
                if elapsed >= 0.05:
                    reader_waited = True

        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)

        writer_thread.start()
        reader_thread.start()

        writer_thread.join()
        reader_thread.join()

        assert reader_waited

    def test_writer_excludes_other_writers(self):
        """Test that only one writer at a time."""
        lock = SyncRWLock()
        concurrent_writers = []
        count_lock = threading.Lock()
        active_writers = 0

        def writer():
            nonlocal active_writers
            with lock.write_lock():
                with count_lock:
                    active_writers += 1
                    concurrent_writers.append(active_writers)
                time.sleep(0.02)
                with count_lock:
                    active_writers -= 1

        threads = [threading.Thread(target=writer) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should never have more than 1 writer
        assert max(concurrent_writers) == 1


class TestSyncRWLockWriterPreference:
    """Test that writers don't starve (writer preference)."""

    def test_waiting_writer_blocks_new_readers(self):
        """Test that when writer is waiting, new readers block."""
        lock = SyncRWLock()
        reader1_started = threading.Event()
        writer_waiting = threading.Event()
        reader2_order = []

        def reader1():
            with lock.read_lock():
                reader1_started.set()
                writer_waiting.wait()  # Wait until writer is waiting
                time.sleep(0.1)  # Hold lock

        def writer():
            reader1_started.wait()  # Wait for reader1 to start
            writer_waiting.set()
            with lock.write_lock():
                reader2_order.append("writer")

        def reader2():
            writer_waiting.wait()
            time.sleep(0.01)  # Small delay to ensure writer starts waiting first
            with lock.read_lock():
                reader2_order.append("reader2")

        t1 = threading.Thread(target=reader1)
        t2 = threading.Thread(target=writer)
        t3 = threading.Thread(target=reader2)

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

        # Writer should complete before reader2 (writer preference)
        assert reader2_order == ["writer", "reader2"]


class TestSyncRWLockThreadSafety:
    """Test thread safety under high concurrency."""

    def test_concurrent_mixed_operations(self):
        """Test mixed read/write operations don't corrupt state."""
        lock = SyncRWLock()
        shared_value = 0
        errors = []

        def reader():
            try:
                for _ in range(100):
                    with lock.read_lock():
                        _ = shared_value  # Read operation
            except Exception as e:
                errors.append(e)

        def writer():
            nonlocal shared_value
            try:
                for _ in range(50):
                    with lock.write_lock():
                        shared_value += 1  # Write operation
            except Exception as e:
                errors.append(e)

        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=reader))
            threads.append(threading.Thread(target=writer))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert shared_value == 5 * 50  # 5 writers × 50 increments each
