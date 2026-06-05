"""Thread pool executor configuration and management.

Configures and manages thread pools for CPU-bound
and I/O-bound proxy operations.
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class ThreadPoolConfig:
    """Configuration for thread pool."""

    pool_name: str
    max_workers: int = 10
    thread_name_prefix: str = "proxywhirl"
    timeout_seconds: int = 30


class ThreadPoolManager:
    """Manages thread pool executors."""

    def __init__(self) -> None:
        """Initialize thread pool manager."""
        self._pools: dict[str, ThreadPoolExecutor] = {}
        logger.debug("ThreadPoolManager initialized")

    def create_pool(self, config: ThreadPoolConfig) -> bool:
        """Create a thread pool.

        Args:
            config: Thread pool configuration

        Returns:
            True if created
        """
        if config.pool_name in self._pools:
            logger.warning(f"Pool already exists: {config.pool_name}")
            return False

        try:
            executor = ThreadPoolExecutor(
                max_workers=config.max_workers,
                thread_name_prefix=config.thread_name_prefix,
            )
            self._pools[config.pool_name] = executor
            logger.info(f"Thread pool created: {config.pool_name} (workers={config.max_workers})")
            return True
        except Exception as e:
            logger.error(f"Failed to create thread pool: {e}")
            return False

    def get_pool(self, pool_name: str) -> ThreadPoolExecutor | None:
        """Get thread pool by name.

        Args:
            pool_name: Pool name

        Returns:
            ThreadPoolExecutor or None
        """
        return self._pools.get(pool_name)

    def submit_task(
        self,
        pool_name: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """Submit task to thread pool.

        Args:
            pool_name: Pool name
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            True if submitted
        """
        pool = self.get_pool(pool_name)
        if not pool:
            logger.error(f"Pool not found: {pool_name}")
            return False

        try:
            pool.submit(func, *args, **kwargs)
            logger.debug(f"Task submitted to pool: {pool_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            return False

    def shutdown_pool(self, pool_name: str, wait: bool = True) -> bool:
        """Shutdown thread pool.

        Args:
            pool_name: Pool name
            wait: Wait for pending tasks

        Returns:
            True if shut down
        """
        pool = self._pools.get(pool_name)
        if not pool:
            return False

        try:
            pool.shutdown(wait=wait)
            del self._pools[pool_name]
            logger.info(f"Thread pool shutdown: {pool_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to shutdown pool: {e}")
            return False

    def shutdown_all(self, wait: bool = True) -> None:
        """Shutdown all thread pools.

        Args:
            wait: Wait for pending tasks
        """
        for pool_name in list(self._pools.keys()):
            self.shutdown_pool(pool_name, wait=wait)
        logger.info("All thread pools shut down")

    def export_metrics(self) -> dict[str, Any]:
        """Export thread pool metrics.

        Returns:
            Dictionary of metrics
        """
        return {
            "total_pools": len(self._pools),
            "pools": {name: {"active": True} for name in self._pools},
        }
