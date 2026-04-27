"""Async fetch timeout context managers for ProxyWhirl.

Provides configurable timeout handling for async HTTP operations
with proper cleanup and error handling.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any

from loguru import logger


class AsyncFetchTimeout:
    """Context manager for async fetch operations with timeout.

    Handles timeout management for async HTTP requests with automatic
    cancellation and cleanup on timeout.

    Example:
        >>> async with AsyncFetchTimeout(timeout=30) as fetcher:
        ...     response = await fetcher.fetch(url)
    """

    def __init__(self, timeout: float = 30.0) -> None:
        """Initialize the timeout manager.

        Args:
            timeout: Timeout in seconds
        """
        self.timeout = timeout
        self._task: asyncio.Task[Any] | None = None

    async def __aenter__(self) -> AsyncFetchTimeout:
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context and cancel any pending tasks."""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                logger.debug("Async fetch task cancelled")

    async def fetch(self, coro: Any) -> Any:
        """Execute coroutine with timeout.

        Args:
            coro: Coroutine to execute

        Returns:
            Result from the coroutine

        Raises:
            asyncio.TimeoutError: If timeout exceeded
        """
        try:
            return await asyncio.wait_for(coro, timeout=self.timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Fetch operation timed out after {self.timeout}s")
            raise


@asynccontextmanager
async def async_fetch_with_timeout(
    timeout: float = 30.0,
) -> Any:
    """Async context manager for fetch operations with timeout.

    Args:
        timeout: Timeout in seconds

    Yields:
        AsyncFetchTimeout instance

    Example:
        >>> async with async_fetch_with_timeout(timeout=60) as fetcher:
        ...     result = await fetcher.fetch(some_async_operation())
    """
    timeout_mgr = AsyncFetchTimeout(timeout=timeout)
    async with timeout_mgr:
        yield timeout_mgr


class AsyncFetchBatch:
    """Batch executor for async fetch operations with timeout.

    Manages multiple concurrent fetch operations with per-operation
    timeout handling.

    Example:
        >>> batch = AsyncFetchBatch(timeout=30, max_concurrent=10)
        >>> results = await batch.fetch_urls(urls)
    """

    def __init__(self, timeout: float = 30.0, max_concurrent: int = 10) -> None:
        """Initialize batch executor.

        Args:
            timeout: Per-operation timeout in seconds
            max_concurrent: Maximum concurrent operations
        """
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_timeout(self, coro: Any) -> Any:
        """Fetch with timeout and semaphore control.

        Args:
            coro: Coroutine to execute

        Returns:
            Result from coroutine
        """
        async with self._semaphore:
            try:
                return await asyncio.wait_for(coro, timeout=self.timeout)
            except asyncio.TimeoutError:
                logger.warning(f"Fetch timed out after {self.timeout}s")
                raise

    async def fetch_all(self, coros: list[Any]) -> list[Any]:
        """Execute multiple fetch operations with timeout.

        Args:
            coros: List of coroutines

        Returns:
            List of results (may contain exceptions if return_exceptions=True)
        """
        tasks = [self.fetch_with_timeout(coro) for coro in coros]
        return await asyncio.gather(*tasks, return_exceptions=True)
