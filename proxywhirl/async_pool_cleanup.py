"""Async pool cleanup utilities."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Callable

from loguru import logger


@dataclass
class PoolStats:
    """Statistics about a pool."""

    total_items: int = 0
    active_items: int = 0
    idle_items: int = 0
    cleanup_runs: int = 0
    items_removed: int = 0


class AsyncPoolCleaner:
    """
    Async pool cleaner for resource management.

    Periodically cleans up idle or stale items from async pools
    to prevent resource exhaustion.
    """

    def __init__(
        self,
        cleanup_interval: float = 60.0,
        idle_timeout: float = 300.0,
        max_age: float = 3600.0,
    ):
        """
        Initialize async pool cleaner.

        Args:
            cleanup_interval: Cleanup run interval in seconds
            idle_timeout: Maximum idle time before removal in seconds
            max_age: Maximum item age before removal in seconds
        """
        self.cleanup_interval = cleanup_interval
        self.idle_timeout = idle_timeout
        self.max_age = max_age
        self.is_running = False
        self.stats = PoolStats()
        self._cleanup_task: asyncio.Task[None] | None = None

    async def start(self, cleanup_fn: Callable[[], Any]) -> None:
        """
        Start the cleanup loop.

        Args:
            cleanup_fn: Async function to call for cleanup
        """
        if self.is_running:
            logger.warning("Cleanup loop already running")
            return

        self.is_running = True
        self._cleanup_task = asyncio.create_task(
            self._cleanup_loop(cleanup_fn),
        )
        logger.info(f"Started async pool cleaner (interval: {self.cleanup_interval}s)")

    async def stop(self) -> None:
        """Stop the cleanup loop."""
        if not self.is_running:
            return

        self.is_running = False

        if self._cleanup_task:
            self._cleanup_task.cancel()

            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped async pool cleaner")

    async def _cleanup_loop(self, cleanup_fn: Callable[[], Any]) -> None:
        """
        Run the cleanup loop.

        Args:
            cleanup_fn: Async cleanup function
        """
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)

                if self.is_running:
                    await cleanup_fn()
                    self.stats.cleanup_runs += 1

            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    def get_stats(self) -> PoolStats:
        """
        Get cleaner statistics.

        Returns:
            Pool statistics
        """
        return PoolStats(
            total_items=self.stats.total_items,
            active_items=self.stats.active_items,
            idle_items=self.stats.idle_items,
            cleanup_runs=self.stats.cleanup_runs,
            items_removed=self.stats.items_removed,
        )

    def record_item_added(self) -> None:
        """Record an item added to pool."""
        self.stats.total_items += 1

    def record_item_removed(self) -> None:
        """Record an item removed from pool."""
        self.stats.total_items = max(0, self.stats.total_items - 1)
        self.stats.items_removed += 1

    def record_item_active(self) -> None:
        """Record an item becoming active."""
        self.stats.active_items += 1

    def record_item_idle(self) -> None:
        """Record an item becoming idle."""
        self.stats.idle_items = max(0, self.stats.idle_items + 1)


class AsyncResourcePool:
    """
    Generic async resource pool with automatic cleanup.

    Manages a pool of resources with TTL and idle timeout.
    """

    def __init__(
        self,
        factory: Callable[[], Any],
        max_size: int = 10,
        idle_timeout: float = 300.0,
    ):
        """
        Initialize resource pool.

        Args:
            factory: Async factory function to create resources
            max_size: Maximum pool size
            idle_timeout: Idle timeout in seconds
        """
        self.factory = factory
        self.max_size = max_size
        self.idle_timeout = idle_timeout
        self.available: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self.in_use: set[Any] = set()
        self.created_count = 0
        self.destroyed_count = 0
        self.cleaner = AsyncPoolCleaner(idle_timeout=idle_timeout)

    async def acquire(self) -> Any:
        """
        Acquire a resource from the pool.

        Returns:
            Resource instance
        """
        try:
            resource = self.available.get_nowait()
        except asyncio.QueueEmpty:
            if self.created_count < self.max_size:
                resource = await self.factory()
                self.created_count += 1
            else:
                resource = await self.available.get()

        self.in_use.add(resource)
        self.cleaner.record_item_active()
        return resource

    async def release(self, resource: Any) -> None:
        """
        Release a resource back to the pool.

        Args:
            resource: Resource to release
        """
        if resource in self.in_use:
            self.in_use.remove(resource)

        try:
            self.available.put_nowait(resource)
            self.cleaner.record_item_idle()
        except asyncio.QueueFull:
            await self._destroy_resource(resource)

    async def _destroy_resource(self, resource: Any) -> None:
        """
        Destroy a resource.

        Args:
            resource: Resource to destroy
        """
        try:
            if hasattr(resource, "close"):
                if asyncio.iscoroutinefunction(resource.close):
                    await resource.close()
                else:
                    resource.close()

            self.destroyed_count += 1

        except Exception as e:
            logger.error(f"Error destroying resource: {e}")

    async def close(self) -> None:
        """Close the pool and clean up all resources."""
        await self.cleaner.stop()

        while not self.available.empty():
            try:
                resource = self.available.get_nowait()
                await self._destroy_resource(resource)
            except asyncio.QueueEmpty:
                break

        for resource in self.in_use.copy():
            await self._destroy_resource(resource)

        self.in_use.clear()

    def get_stats(self) -> dict[str, int]:
        """
        Get pool statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "created": self.created_count,
            "destroyed": self.destroyed_count,
            "in_use": len(self.in_use),
            "available": self.available.qsize(),
            "cleanup_runs": self.cleaner.stats.cleanup_runs,
        }
