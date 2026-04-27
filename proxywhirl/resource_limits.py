"""Resource limit controls for ProxyWhirl."""

from __future__ import annotations

import os
import psutil
from dataclasses import dataclass
from typing import Optional

from loguru import logger


@dataclass
class ResourceLimits:
    """Configuration for resource limits."""

    max_memory_mb: float = 512.0
    max_open_connections: int = 1000
    max_cache_size_mb: float = 100.0
    max_log_file_size_mb: float = 100.0
    max_log_files: int = 10
    warn_threshold: float = 0.8  # Warn at 80% usage


class ResourceLimiter:
    """
    Monitor and enforce resource limits.

    Tracks:
    - Memory usage
    - Open connections
    - Cache size
    - Log file size
    """

    def __init__(self, limits: Optional[ResourceLimits] = None):
        """
        Initialize resource limiter.

        Args:
            limits: ResourceLimits configuration
        """
        self.limits = limits or ResourceLimits()
        self.process = psutil.Process(os.getpid())
        self.open_connections = 0
        self.cache_size_bytes = 0

    def get_memory_usage_mb(self) -> float:
        """
        Get current memory usage in MB.

        Returns:
            Memory usage in megabytes
        """
        try:
            return self.process.memory_info().rss / (1024 * 1024)
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return 0.0

    def get_memory_usage_percent(self) -> float:
        """
        Get memory usage as percentage of limit.

        Returns:
            Percentage of memory limit used (0-100)
        """
        usage_mb = self.get_memory_usage_mb()
        return (usage_mb / self.limits.max_memory_mb) * 100

    def check_memory_limit(self) -> tuple[bool, str]:
        """
        Check if memory limit is exceeded.

        Returns:
            Tuple of (is_ok, message)
        """
        usage_mb = self.get_memory_usage_mb()
        usage_percent = self.get_memory_usage_percent()

        if usage_mb > self.limits.max_memory_mb:
            return False, f"Memory limit exceeded: {usage_mb:.1f}MB / {self.limits.max_memory_mb:.1f}MB"

        if usage_percent > (self.limits.warn_threshold * 100):
            return True, f"Memory usage high: {usage_percent:.1f}% of limit"

        return True, f"Memory OK: {usage_mb:.1f}MB / {self.limits.max_memory_mb:.1f}MB"

    def record_connection_open(self) -> bool:
        """
        Record opening of a connection.

        Returns:
            True if connection allowed, False if limit exceeded
        """
        if self.open_connections >= self.limits.max_open_connections:
            logger.warning(
                f"Connection limit exceeded: {self.open_connections}/"
                f"{self.limits.max_open_connections}"
            )
            return False

        self.open_connections += 1
        return True

    def record_connection_close(self) -> None:
        """Record closing of a connection."""
        if self.open_connections > 0:
            self.open_connections -= 1

    def check_connection_limit(self) -> tuple[bool, str]:
        """
        Check connection limit status.

        Returns:
            Tuple of (is_ok, message)
        """
        percent = (self.open_connections / self.limits.max_open_connections) * 100

        if self.open_connections >= self.limits.max_open_connections:
            return False, f"Connection limit exceeded: {self.open_connections}/{self.limits.max_open_connections}"

        if percent > (self.limits.warn_threshold * 100):
            return True, f"Connection usage high: {percent:.1f}%"

        return True, f"Connections OK: {self.open_connections}/{self.limits.max_open_connections}"

    def record_cache_size(self, size_bytes: int) -> bool:
        """
        Record cache size.

        Args:
            size_bytes: Cache size in bytes

        Returns:
            True if within limit, False if exceeded
        """
        max_bytes = self.limits.max_cache_size_mb * 1024 * 1024
        self.cache_size_bytes = size_bytes

        if size_bytes > max_bytes:
            logger.warning(
                f"Cache size limit exceeded: {size_bytes / (1024 * 1024):.1f}MB / "
                f"{self.limits.max_cache_size_mb:.1f}MB"
            )
            return False

        return True

    def check_cache_size_limit(self) -> tuple[bool, str]:
        """
        Check cache size limit.

        Returns:
            Tuple of (is_ok, message)
        """
        max_bytes = self.limits.max_cache_size_mb * 1024 * 1024
        cache_mb = self.cache_size_bytes / (1024 * 1024)
        percent = (self.cache_size_bytes / max_bytes) * 100

        if self.cache_size_bytes > max_bytes:
            return False, f"Cache size limit exceeded: {cache_mb:.1f}MB / {self.limits.max_cache_size_mb:.1f}MB"

        if percent > (self.limits.warn_threshold * 100):
            return True, f"Cache usage high: {percent:.1f}%"

        return True, f"Cache OK: {cache_mb:.1f}MB / {self.limits.max_cache_size_mb:.1f}MB"

    def get_resource_status(self) -> dict[str, dict[str, str | float | bool]]:
        """
        Get comprehensive resource status.

        Returns:
            Dictionary with status for all resources
        """
        mem_ok, mem_msg = self.check_memory_limit()
        conn_ok, conn_msg = self.check_connection_limit()
        cache_ok, cache_msg = self.check_cache_size_limit()

        return {
            "memory": {
                "ok": mem_ok,
                "message": mem_msg,
                "usage_mb": self.get_memory_usage_mb(),
                "usage_percent": self.get_memory_usage_percent(),
            },
            "connections": {
                "ok": conn_ok,
                "message": conn_msg,
                "open": self.open_connections,
                "limit": self.limits.max_open_connections,
            },
            "cache": {
                "ok": cache_ok,
                "message": cache_msg,
                "size_mb": self.cache_size_bytes / (1024 * 1024),
                "limit_mb": self.limits.max_cache_size_mb,
            },
        }

    def enforce_limits(self) -> list[str]:
        """
        Enforce all limits and return list of violations.

        Returns:
            List of limit violation messages
        """
        violations = []

        mem_ok, msg = self.check_memory_limit()
        if not mem_ok:
            violations.append(msg)

        conn_ok, msg = self.check_connection_limit()
        if not conn_ok:
            violations.append(msg)

        cache_ok, msg = self.check_cache_size_limit()
        if not cache_ok:
            violations.append(msg)

        return violations

    def get_free_memory_mb(self) -> float:
        """
        Get available memory.

        Returns:
            Available memory in megabytes before hitting limit
        """
        usage_mb = self.get_memory_usage_mb()
        return max(0.0, self.limits.max_memory_mb - usage_mb)

    def get_free_connections(self) -> int:
        """
        Get available connection slots.

        Returns:
            Number of connections that can still be opened
        """
        return max(0, self.limits.max_open_connections - self.open_connections)

    def get_free_cache_mb(self) -> float:
        """
        Get available cache space.

        Returns:
            Available cache space in megabytes
        """
        max_bytes = self.limits.max_cache_size_mb * 1024 * 1024
        return max(0.0, (max_bytes - self.cache_size_bytes) / (1024 * 1024))
