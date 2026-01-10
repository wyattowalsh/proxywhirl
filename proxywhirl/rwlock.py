"""
Async readers-writer lock implementation for high-concurrency scenarios.
"""

from __future__ import annotations

import asyncio


class AsyncRWLock:
    """Async readers-writer lock for high-concurrency scenarios.

    Allows multiple concurrent readers but exclusive writer access.
    Prevents read operations from blocking each other while maintaining
    data consistency for writes.

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
        self._readers = 0
        self._writers = 0
        self._write_waiters = 0
        self._lock = asyncio.Lock()
        self._read_ok = asyncio.Condition(self._lock)
        self._write_ok = asyncio.Condition(self._lock)

    async def acquire_read(self) -> None:
        """Acquire read lock (shared with other readers)."""
        async with self._lock:
            # Wait if there's a writer or writers waiting
            while self._writers > 0 or self._write_waiters > 0:
                await self._read_ok.wait()
            self._readers += 1

    async def release_read(self) -> None:
        """Release read lock."""
        async with self._lock:
            self._readers -= 1
            # Wake up waiting writers if we're the last reader
            if self._readers == 0:
                self._write_ok.notify()

    async def acquire_write(self) -> None:
        """Acquire write lock (exclusive)."""
        async with self._lock:
            self._write_waiters += 1
            try:
                # Wait until no readers and no writers
                while self._readers > 0 or self._writers > 0:
                    await self._write_ok.wait()
                self._writers += 1
            finally:
                self._write_waiters -= 1

    async def release_write(self) -> None:
        """Release write lock."""
        async with self._lock:
            self._writers -= 1
            # Prefer waiting writers, but also wake readers
            self._write_ok.notify()
            self._read_ok.notify_all()

    class ReadContext:
        """Context manager for read locks."""

        def __init__(self, lock: AsyncRWLock) -> None:
            self.lock = lock

        async def __aenter__(self) -> None:
            await self.lock.acquire_read()

        async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
            await self.lock.release_read()

    class WriteContext:
        """Context manager for write locks."""

        def __init__(self, lock: AsyncRWLock) -> None:
            self.lock = lock

        async def __aenter__(self) -> None:
            await self.lock.acquire_write()

        async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
            await self.lock.release_write()

    def read_lock(self) -> AsyncRWLock.ReadContext:
        """Get read lock context manager."""
        return AsyncRWLock.ReadContext(self)

    def write_lock(self) -> AsyncRWLock.WriteContext:
        """Get write lock context manager."""
        return AsyncRWLock.WriteContext(self)
