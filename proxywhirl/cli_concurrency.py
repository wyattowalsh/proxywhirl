"""Concurrent command execution utilities for the CLI.

Provides utilities for parallelizing independent CLI commands
and operations to improve performance in batch scenarios.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, TypeVar

from loguru import logger

T = TypeVar("T")


class CLICommandBatch:
    """Executor for parallel CLI commands.

    Allows multiple independent CLI operations to run concurrently,
    with proper error handling and aggregation of results.

    Example:
        >>> batch = CLICommandBatch(max_concurrent=5)
        >>> results = await batch.execute_commands([
        ...     (validate_proxy, ("proxy1", "127.0.0.1:8080")),
        ...     (validate_proxy, ("proxy2", "127.0.0.1:8081")),
        ... ])
    """

    def __init__(self, max_concurrent: int = 10) -> None:
        """Initialize the batch executor.

        Args:
            max_concurrent: Maximum number of concurrent commands
        """
        self.max_concurrent = max_concurrent
        self._semaphore: asyncio.Semaphore | None = None

    async def execute_commands(
        self,
        commands: list[tuple[Callable[..., Any], tuple[Any, ...]]],
    ) -> list[Any]:
        """Execute multiple commands concurrently.

        Args:
            commands: List of (callable, args_tuple) pairs

        Returns:
            List of results in the same order as input commands
        """
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        tasks = [self._run_command(func, args) for func, args in commands]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def _run_command(self, func: Callable[..., Any], args: tuple[Any, ...]) -> Any:
        """Run a single command with semaphore control.

        Args:
            func: Callable to execute
            args: Arguments for the callable

        Returns:
            Result from the callable
        """
        async with self._semaphore:  # type: ignore
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args)
                return func(*args)
            except Exception as e:
                logger.error(f"Command failed: {e}")
                raise


async def run_concurrent_operations(
    operations: list[tuple[Callable[..., Any], tuple[Any, ...]]],
    max_concurrent: int = 10,
) -> list[Any]:
    """Convenience function to run operations concurrently.

    Args:
        operations: List of (callable, args_tuple) pairs
        max_concurrent: Maximum concurrent operations

    Returns:
        List of results
    """
    batch = CLICommandBatch(max_concurrent=max_concurrent)
    return await batch.execute_commands(operations)
