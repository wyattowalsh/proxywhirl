"""
Synchronous readers-writer lock implementation for high-concurrency scenarios.

This module provides a threading-based RWLock that allows multiple concurrent
readers while ensuring exclusive access for writers. This is the sync counterpart
to AsyncRWLock in rwlock.py.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager


class SyncRWLock:
    """Synchronous readers-writer lock for high-concurrency scenarios.

    Allows multiple concurrent readers but exclusive writer access.
    Prevents read operations from blocking each other while maintaining
    data consistency for writes.

    Features:
    - Multiple readers can hold the lock simultaneously
    - Writers get exclusive access (no readers or other writers)
    - Writer preference to prevent writer starvation

    Example:
        >>> rwlock = SyncRWLock()
        >>> with rwlock.read_lock():
        ...     # Multiple readers can acquire simultaneously
        ...     value = shared_data.read()
        >>> with rwlock.write_lock():
        ...     # Only one writer at a time
        ...     shared_data.write(new_value)
    """

    def __init__(self) -> None:
        """Initialize the SyncRWLock."""
        self._readers = 0
        self._writers = 0
        self._write_waiters = 0
        self._lock = threading.Lock()
        self._read_ok = threading.Condition(self._lock)
        self._write_ok = threading.Condition(self._lock)

    def acquire_read(self) -> None:
        """Acquire read lock (shared with other readers).

        Blocks if a writer is active or writers are waiting.
        """
        with self._lock:
            # Wait if there's a writer or writers waiting
            while self._writers > 0 or self._write_waiters > 0:
                self._read_ok.wait()
            self._readers += 1

    def release_read(self) -> None:
        """Release read lock.

        Notifies waiting writers if this was the last reader.
        """
        with self._lock:
            self._readers -= 1
            # Wake up waiting writers if we're the last reader
            if self._readers == 0:
                self._write_ok.notify()

    def acquire_write(self) -> None:
        """Acquire write lock (exclusive).

        Blocks until no readers and no other writers hold the lock.
        """
        with self._lock:
            self._write_waiters += 1
            try:
                # Wait until no readers and no writers
                while self._readers > 0 or self._writers > 0:
                    self._write_ok.wait()
                self._writers += 1
            finally:
                self._write_waiters -= 1

    def release_write(self) -> None:
        """Release write lock.

        Notifies both waiting writers and readers.
        """
        with self._lock:
            self._writers -= 1
            # Prefer waiting writers, but also wake readers
            self._write_ok.notify()
            self._read_ok.notify_all()

    @contextmanager
    def read_lock(self) -> Iterator[None]:
        """Context manager for read locks.

        Allows multiple concurrent readers.

        Example:
            >>> with rwlock.read_lock():
            ...     # Multiple threads can read simultaneously
            ...     data = shared_resource.read()
        """
        self.acquire_read()
        try:
            yield
        finally:
            self.release_read()

    @contextmanager
    def write_lock(self) -> Iterator[None]:
        """Context manager for write locks.

        Provides exclusive access - no concurrent readers or writers.

        Example:
            >>> with rwlock.write_lock():
            ...     # Exclusive access guaranteed
            ...     shared_resource.write(new_data)
        """
        self.acquire_write()
        try:
            yield
        finally:
            self.release_write()
