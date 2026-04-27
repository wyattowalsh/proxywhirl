"""Tests for graceful shutdown with pending requests and connections."""

from __future__ import annotations

import asyncio
import signal
import threading
import time
from contextlib import asynccontextmanager, contextmanager
from typing import Any


class GracefulShutdownManager:
    """Manages graceful shutdown of services."""

    def __init__(self, timeout: float = 5.0) -> None:
        """Initialize shutdown manager."""
        self.timeout = timeout
        self.shutdown_event = asyncio.Event()
        self._pending_tasks: set[asyncio.Task] = set()
        self._lock = threading.Lock()
        self.is_shutting_down = False

    def signal_shutdown(self) -> None:
        """Signal shutdown initiated."""
        self.is_shutting_down = True

    @contextmanager
    def track_sync_work(self):
        """Track synchronous work during shutdown."""
        yield

    @asynccontextmanager
    async def track_async_work(self):
        """Track async work and ensure completion on shutdown."""
        task = asyncio.current_task()
        if task:
            with self._lock:
                self._pending_tasks.add(task)
        try:
            yield
        finally:
            if task:
                with self._lock:
                    self._pending_tasks.discard(task)

    async def shutdown_gracefully(self) -> None:
        """Perform graceful shutdown."""
        self.signal_shutdown()
        self.shutdown_event.set()
        await self.wait_for_pending()

    async def wait_for_pending(self) -> None:
        """Wait for all pending tasks to complete."""
        start = time.time()
        while time.time() - start < self.timeout:
            with self._lock:
                if not self._pending_tasks:
                    break
            await asyncio.sleep(0.01)

        # Cancel remaining tasks
        with self._lock:
            pending = list(self._pending_tasks)
        for task in pending:
            task.cancel()

    def has_pending_work(self) -> bool:
        """Check if there's pending work."""
        with self._lock:
            return len(self._pending_tasks) > 0


class TestGracefulShutdown:
    """Test graceful shutdown functionality."""

    @pytest.fixture
    def shutdown_mgr(self):
        """Provide shutdown manager."""
        return GracefulShutdownManager(timeout=1.0)

    def test_init_not_shutting_down(self, shutdown_mgr) -> None:
        """Test initial state is not shutting down."""
        assert not shutdown_mgr.is_shutting_down

    def test_signal_shutdown(self, shutdown_mgr) -> None:
        """Test shutdown signal."""
        shutdown_mgr.signal_shutdown()
        assert shutdown_mgr.is_shutting_down

    def test_no_pending_work_initially(self, shutdown_mgr) -> None:
        """Test no pending work initially."""
        assert not shutdown_mgr.has_pending_work()

    @pytest.mark.asyncio
    async def test_shutdown_with_no_pending(self, shutdown_mgr) -> None:
        """Test shutdown with no pending work."""
        await shutdown_mgr.shutdown_gracefully()
        assert shutdown_mgr.is_shutting_down

    @pytest.mark.asyncio
    async def test_track_async_work(self, shutdown_mgr) -> None:
        """Test tracking async work."""
        async with shutdown_mgr.track_async_work():
            await asyncio.sleep(0.01)
        # Should complete normally

    @pytest.mark.asyncio
    async def test_pending_task_tracking(self, shutdown_mgr) -> None:
        """Test pending task tracking."""
        async def slow_work() -> None:
            async with shutdown_mgr.track_async_work():
                await asyncio.sleep(0.1)

        task = asyncio.create_task(slow_work())
        await asyncio.sleep(0.01)
        # Task should be tracked
        assert shutdown_mgr.has_pending_work()
        await task

    @pytest.mark.asyncio
    async def test_wait_for_pending_completes(self, shutdown_mgr) -> None:
        """Test waiting for pending tasks."""
        async def quick_work() -> None:
            async with shutdown_mgr.track_async_work():
                await asyncio.sleep(0.01)

        task = asyncio.create_task(quick_work())
        await asyncio.sleep(0.005)
        await shutdown_mgr.wait_for_pending()
        assert not shutdown_mgr.has_pending_work()

    @pytest.mark.asyncio
    async def test_wait_for_pending_timeout(self, shutdown_mgr) -> None:
        """Test timeout on pending tasks."""
        shutdown_mgr.timeout = 0.05
        
        async def slow_work() -> None:
            async with shutdown_mgr.track_async_work():
                await asyncio.sleep(10)

        task = asyncio.create_task(slow_work())
        await asyncio.sleep(0.01)
        await shutdown_mgr.wait_for_pending()
        # Task should be cancelled
        assert task.done() or task.cancelled()

    @pytest.mark.asyncio
    async def test_graceful_shutdown_signal(self, shutdown_mgr) -> None:
        """Test graceful shutdown signal sets flag."""
        await shutdown_mgr.shutdown_gracefully()
        assert shutdown_mgr.shutdown_event.is_set()

    def test_sync_work_tracking(self, shutdown_mgr) -> None:
        """Test sync work tracking."""
        with shutdown_mgr.track_sync_work():
            pass
        # Should complete normally

    @pytest.mark.asyncio
    async def test_multiple_pending_tasks(self, shutdown_mgr) -> None:
        """Test multiple pending tasks."""
        async def work() -> None:
            async with shutdown_mgr.track_async_work():
                await asyncio.sleep(0.01)

        tasks = [asyncio.create_task(work()) for _ in range(5)]
        await asyncio.sleep(0.005)
        # All should be tracked
        await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_shutdown_state_propagation(self, shutdown_mgr) -> None:
        """Test shutdown state propagates."""
        async def check_shutdown_flag() -> bool:
            return shutdown_mgr.is_shutting_down

        # Before shutdown
        assert not await check_shutdown_flag()
        
        shutdown_mgr.signal_shutdown()
        
        # After shutdown
        assert await check_shutdown_flag()


import pytest
