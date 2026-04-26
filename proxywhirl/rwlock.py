"""
Readers-writer locks for high-concurrency scenarios.

This module provides both async and sync RWLock implementations for
allowing multiple concurrent readers but exclusive writer access.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Iterator
from contextlib import asynccontextmanager, contextmanager

from aiorwlock import RWLock as _AioRWLock
from readerwriterlock import rwlock as _rwlock


class AsyncRWLock:
    """Async readers-writer lock for high-concurrency scenarios.

    Allows multiple concurrent readers but exclusive writer access.
    Prevents read operations from blocking each other while maintaining
    data consistency for writes.

    This is a thin wrapper around aiorwlock.RWLock providing a consistent
    interface with method-based context manager access.

    Example:
        >>> rwlock = AsyncRWLock()
        >>> async with rwlock.read_lock():
        ...     # Multiple readers can acquire simultaneously
        ...     value = shared_data.read()
        >>> async with rwlock.write_lock():
        ...     # Only one writer at a time
        ...     shared_data.write(new_value)
    """

    def __init__(self) -> None:
        """Initialize the RWLock."""
        self._lock = _AioRWLock()
        self._state_lock = asyncio.Lock()
        self._readers = 0
        self._writers = 0
        self._write_waiters = 0

    async def acquire_read(self) -> None:
        """Acquire a read lock."""
        await self._lock.reader_lock.acquire()
        async with self._state_lock:
            self._readers += 1

    async def release_read(self) -> None:
        """Release a read lock."""
        try:
            result = self._lock.reader_lock.release()
            if asyncio.iscoroutine(result):
                await result
        except RuntimeError:
            return
        async with self._state_lock:
            if self._readers > 0:
                self._readers -= 1

    async def acquire_write(self) -> None:
        """Acquire a write lock."""
        async with self._state_lock:
            self._write_waiters += 1
        await self._lock.writer_lock.acquire()
        async with self._state_lock:
            self._write_waiters = max(0, self._write_waiters - 1)
            self._writers += 1

    async def release_write(self) -> None:
        """Release a write lock."""
        try:
            result = self._lock.writer_lock.release()
            if asyncio.iscoroutine(result):
                await result
        except RuntimeError:
            return
        async with self._state_lock:
            if self._writers > 0:
                self._writers -= 1

    @asynccontextmanager
    async def read_lock(self):
        """Get read lock async context manager."""
        await self.acquire_read()
        try:
            yield
        finally:
            await self.release_read()

    @asynccontextmanager
    async def write_lock(self):
        """Get write lock async context manager."""
        await self.acquire_write()
        try:
            yield
        finally:
            await self.release_write()


class SyncRWLock:
    """Synchronous readers-writer lock for high-concurrency scenarios.

    Allows multiple concurrent readers but exclusive writer access.
    Prevents read operations from blocking each other while maintaining
    data consistency for writes.

    This is a thin wrapper around readerwriterlock.RWLockFair providing
    a consistent interface with the async version.

    Features:
    - Multiple readers can hold the lock simultaneously
    - Writers get exclusive access (no readers or other writers)
    - Fair scheduling to prevent writer starvation

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
        self._lock = _rwlock.RWLockFair()
        self._state_lock = threading.Lock()
        self._readers = 0
        self._writers = 0
        self._write_waiters = 0

    @contextmanager
    def read_lock(self) -> Iterator[None]:
        """Context manager for read locks.

        Allows multiple concurrent readers.

        Example:
            >>> with rwlock.read_lock():
            ...     # Multiple threads can read simultaneously
            ...     data = shared_resource.read()
        """
        with self._lock.gen_rlock():
            with self._state_lock:
                self._readers += 1
            try:
                yield
            finally:
                with self._state_lock:
                    if self._readers > 0:
                        self._readers -= 1

    @contextmanager
    def write_lock(self) -> Iterator[None]:
        """Context manager for write locks.

        Provides exclusive access - no concurrent readers or writers.

        Example:
            >>> with rwlock.write_lock():
            ...     # Exclusive access guaranteed
            ...     shared_resource.write(new_data)
        """
        with self._state_lock:
            self._write_waiters += 1
        with self._lock.gen_wlock():
            with self._state_lock:
                self._write_waiters = max(0, self._write_waiters - 1)
                self._writers += 1
            try:
                yield
            finally:
                with self._state_lock:
                    if self._writers > 0:
                        self._writers -= 1
