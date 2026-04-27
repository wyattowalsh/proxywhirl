"""Async task queue for TUI refresh operations.

Provides non-blocking task management for TUI refresh operations
to prevent UI freezing during long-running tasks.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Callable

from loguru import logger


@dataclass
class AsyncTask:
    """Represents an async task to execute."""

    name: str
    coro: Any
    priority: int = 0  # Higher priority runs first


class AsyncTaskQueue:
    """Queue for managing async TUI refresh tasks.

    Manages concurrent task execution with priority support
    and prevents UI blocking during refresh operations.

    Example:
        >>> queue = AsyncTaskQueue(max_workers=3)
        >>> await queue.add_task("refresh", some_async_op(), priority=1)
        >>> await queue.process()
    """

    def __init__(self, max_workers: int = 3) -> None:
        """Initialize the task queue.

        Args:
            max_workers: Maximum concurrent tasks
        """
        self.max_workers = max_workers
        self._queue: list[AsyncTask] = []
        self._semaphore = asyncio.Semaphore(max_workers)
        self._running_tasks: set[asyncio.Task[Any]] = set()

    async def add_task(
        self,
        name: str,
        coro: Any,
        priority: int = 0,
    ) -> None:
        """Add a task to the queue.

        Args:
            name: Task name for logging
            coro: Coroutine to execute
            priority: Task priority (higher = first)
        """
        task = AsyncTask(name=name, coro=coro, priority=priority)
        self._queue.append(task)
        self._queue.sort(key=lambda t: -t.priority)  # Sort by priority desc

    async def process(self) -> list[Any]:
        """Process all queued tasks concurrently.

        Returns:
            List of task results
        """
        tasks = [self._process_task(task) for task in self._queue]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        self._queue.clear()
        return results

    async def _process_task(self, task: AsyncTask) -> Any:
        """Process a single task with semaphore control.

        Args:
            task: Task to process

        Returns:
            Task result
        """
        async with self._semaphore:
            try:
                logger.debug(f"Starting async task: {task.name}")
                result = await task.coro
                logger.debug(f"Completed async task: {task.name}")
                return result
            except Exception as e:
                logger.error(f"Task {task.name} failed: {e}")
                raise

    async def cancel_all(self) -> None:
        """Cancel all running tasks."""
        for task in self._running_tasks:
            if not task.done():
                task.cancel()
        self._running_tasks.clear()

    def clear(self) -> None:
        """Clear the queue without processing."""
        self._queue.clear()


class NonBlockingAsyncExecutor:
    """Executor for non-blocking async operations in TUI.

    Prevents UI freezing by running long-duration operations
    asynchronously in the background.

    Example:
        >>> executor = NonBlockingAsyncExecutor()
        >>> executor.submit("refresh_proxies", async_fetch_proxies())
    """

    def __init__(self, max_concurrent: int = 3) -> None:
        """Initialize the executor.

        Args:
            max_concurrent: Maximum concurrent operations
        """
        self.max_concurrent = max_concurrent
        self._queue = AsyncTaskQueue(max_workers=max_concurrent)
        self._callbacks: dict[str, Callable[[Any], None]] = {}

    def submit(
        self,
        name: str,
        coro: Any,
        callback: Callable[[Any], None] | None = None,
        priority: int = 0,
    ) -> None:
        """Submit an async operation.

        Args:
            name: Operation name
            coro: Coroutine to execute
            callback: Optional callback on completion
            priority: Task priority
        """
        if callback:
            self._callbacks[name] = callback

        asyncio.create_task(self._run_with_callback(name, coro))

    async def _run_with_callback(self, name: str, coro: Any) -> Any:
        """Run operation and invoke callback.

        Args:
            name: Operation name
            coro: Coroutine to execute

        Returns:
            Operation result
        """
        try:
            result = await coro
            if name in self._callbacks:
                self._callbacks[name](result)
            return result
        except Exception as e:
            logger.error(f"Operation {name} failed: {e}")
            raise
