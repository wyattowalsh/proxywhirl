"""HTTP connection pooling and management."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from loguru import logger


@dataclass
class ConnectionPoolStats:
    """Statistics for a connection pool."""

    created: int = 0
    active: int = 0
    idle: int = 0
    total_requests: int = 0
    total_errors: int = 0
    peak_connections: int = 0
    avg_response_time_ms: float = 0.0


class ConnectionPool:
    """Manages HTTP connections."""

    def __init__(
        self,
        pool_size: int = 10,
        max_idle_time_seconds: int = 300,
        timeout_seconds: int = 30,
    ):
        """Initialize connection pool.

        Args:
            pool_size: Maximum pool size
            max_idle_time_seconds: Maximum idle time before closing
            timeout_seconds: Connection timeout
        """
        self.pool_size = pool_size
        self.max_idle_time_seconds = max_idle_time_seconds
        self.timeout_seconds = timeout_seconds

        self._connections: dict[str, Any] = {}
        self._last_used: dict[str, datetime] = {}
        self._stats = ConnectionPoolStats()

    def get_connection(self, key: str) -> Any | None:
        """Get a connection from the pool.

        Args:
            key: Connection key (host, proxy, etc.)

        Returns:
            Connection or None
        """
        if key in self._connections:
            conn = self._connections[key]
            self._last_used[key] = datetime.now()
            self._stats.active += 1
            self._stats.total_requests += 1
            return conn

        return None

    def add_connection(self, key: str, connection: Any) -> None:
        """Add a connection to the pool.

        Args:
            key: Connection key
            connection: Connection object
        """
        if len(self._connections) >= self.pool_size:
            # Remove oldest idle connection
            oldest_key = min(
                self._last_used.keys(),
                key=lambda k: self._last_used[k],
            )
            del self._connections[oldest_key]
            del self._last_used[oldest_key]
            logger.debug(f"Removed old connection: {oldest_key}")

        self._connections[key] = connection
        self._last_used[key] = datetime.now()
        self._stats.created += 1
        self._stats.peak_connections = max(
            self._stats.peak_connections,
            len(self._connections),
        )

    def release_connection(self, key: str) -> None:
        """Release a connection back to the pool.

        Args:
            key: Connection key
        """
        if key in self._connections:
            self._last_used[key] = datetime.now()
            self._stats.active = max(0, self._stats.active - 1)
            self._stats.idle += 1

    def cleanup_idle(self) -> int:
        """Clean up idle connections.

        Returns:
            Number of connections removed
        """
        now = datetime.now()
        expired_keys = [
            key
            for key, last_used in self._last_used.items()
            if (now - last_used).total_seconds() > self.max_idle_time_seconds
        ]

        for key in expired_keys:
            del self._connections[key]
            del self._last_used[key]

        logger.debug(f"Cleaned up {len(expired_keys)} idle connections")
        return len(expired_keys)

    def close_all(self) -> None:
        """Close all connections."""
        self._connections.clear()
        self._last_used.clear()
        logger.info("Closed all connections in pool")

    def get_statistics(self) -> ConnectionPoolStats:
        """Get pool statistics.

        Returns:
            Pool statistics
        """
        stats = self._stats
        stats.idle = len(self._connections) - stats.active
        return stats

    def record_error(self) -> None:
        """Record an error in the pool."""
        self._stats.total_errors += 1


class ConnectionPoolManager:
    """Manages multiple connection pools."""

    def __init__(self):
        """Initialize manager."""
        self._pools: dict[str, ConnectionPool] = {}

    def create_pool(
        self,
        name: str,
        pool_size: int = 10,
        max_idle_time_seconds: int = 300,
    ) -> ConnectionPool:
        """Create a new connection pool.

        Args:
            name: Pool name
            pool_size: Maximum pool size
            max_idle_time_seconds: Max idle time

        Returns:
            Created ConnectionPool
        """
        pool = ConnectionPool(
            pool_size=pool_size,
            max_idle_time_seconds=max_idle_time_seconds,
        )
        self._pools[name] = pool
        logger.info(f"Created connection pool: {name}")
        return pool

    def get_pool(self, name: str) -> ConnectionPool | None:
        """Get a connection pool.

        Args:
            name: Pool name

        Returns:
            ConnectionPool or None
        """
        return self._pools.get(name)

    def cleanup_all(self) -> dict[str, int]:
        """Clean up all idle connections across pools.

        Returns:
            Dict of pool name to cleanup count
        """
        results = {}
        for name, pool in self._pools.items():
            results[name] = pool.cleanup_idle()

        return results

    def close_all(self) -> None:
        """Close all pools."""
        for pool in self._pools.values():
            pool.close_all()
        logger.info("Closed all connection pools")

    def get_all_statistics(self) -> dict[str, ConnectionPoolStats]:
        """Get statistics for all pools.

        Returns:
            Dict of pool name to statistics
        """
        return {name: pool.get_statistics() for name, pool in self._pools.items()}
