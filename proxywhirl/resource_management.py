"""Resource management and pooling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from loguru import logger

T = TypeVar("T")


@dataclass
class ResourceStats:
    """Resource statistics."""

    total_created: int = 0
    total_destroyed: int = 0
    currently_allocated: int = 0
    peak_allocated: int = 0
    failed_creations: int = 0
    failed_destructions: int = 0


class ResourcePool(Generic[T]):
    """Generic resource pool."""

    def __init__(
        self,
        factory: callable,
        min_size: int = 5,
        max_size: int = 20,
        timeout: float = 30.0,
    ):
        """Initialize pool.

        Args:
            factory: Resource factory function
            min_size: Minimum pool size
            max_size: Maximum pool size
            timeout: Acquisition timeout
        """
        self.factory = factory
        self.min_size = min_size
        self.max_size = max_size
        self.timeout = timeout
        self._available: list[T] = []
        self._in_use: set[int] = set()
        self._stats = ResourceStats()

    def acquire(self) -> T:
        """Acquire resource from pool.

        Returns:
            Resource
        """
        if self._available:
            resource = self._available.pop()
        else:
            if self._stats.currently_allocated >= self.max_size:
                raise RuntimeError("Resource pool exhausted")

            try:
                resource = self.factory()
                self._stats.total_created += 1
            except Exception as e:
                self._stats.failed_creations += 1
                logger.error(f"Failed to create resource: {e}")
                raise

        self._in_use.add(id(resource))
        self._stats.currently_allocated += 1
        self._stats.peak_allocated = max(
            self._stats.peak_allocated,
            self._stats.currently_allocated,
        )

        return resource

    def release(self, resource: T) -> None:
        """Release resource back to pool.

        Args:
            resource: Resource to release
        """
        rid = id(resource)
        if rid in self._in_use:
            self._in_use.remove(rid)
            self._available.append(resource)
            self._stats.currently_allocated -= 1

    def drain(self) -> None:
        """Drain all resources."""
        for resource in self._available:
            try:
                if hasattr(resource, "close"):
                    resource.close()
                self._stats.total_destroyed += 1
            except Exception as e:
                self._stats.failed_destructions += 1
                logger.warning(f"Failed to close resource: {e}")

        self._available.clear()
        self._in_use.clear()
        logger.info("Resource pool drained")

    def get_stats(self) -> ResourceStats:
        """Get pool statistics.

        Returns:
            Stats
        """
        return self._stats


@dataclass
class ResourceQuota:
    """Resource quota tracking."""

    max_memory_mb: float = 1024.0
    max_cpu_percent: float = 80.0
    max_connections: int = 100
    max_open_files: int = 1000

    current_memory_mb: float = 0.0
    current_cpu_percent: float = 0.0
    current_connections: int = 0
    current_open_files: int = 0

    def can_allocate(self, memory_mb: float) -> bool:
        """Check if can allocate memory.

        Args:
            memory_mb: Memory to allocate

        Returns:
            True if can allocate
        """
        return self.current_memory_mb + memory_mb <= self.max_memory_mb

    def allocate_memory(self, memory_mb: float) -> bool:
        """Allocate memory.

        Args:
            memory_mb: Memory to allocate

        Returns:
            True if allocated
        """
        if self.can_allocate(memory_mb):
            self.current_memory_mb += memory_mb
            return True

        return False

    def release_memory(self, memory_mb: float) -> None:
        """Release memory.

        Args:
            memory_mb: Memory to release
        """
        self.current_memory_mb = max(0, self.current_memory_mb - memory_mb)

    def can_create_connection(self) -> bool:
        """Check if can create connection.

        Returns:
            True if can create
        """
        return self.current_connections < self.max_connections

    def create_connection(self) -> bool:
        """Create connection.

        Returns:
            True if created
        """
        if self.can_create_connection():
            self.current_connections += 1
            return True

        return False

    def close_connection(self) -> None:
        """Close connection."""
        self.current_connections = max(0, self.current_connections - 1)

    def get_utilization(self) -> dict[str, float]:
        """Get resource utilization.

        Returns:
            Utilization percentages
        """
        return {
            "memory_percent": (self.current_memory_mb / self.max_memory_mb) * 100,
            "cpu_percent": self.current_cpu_percent,
            "connection_percent": (self.current_connections / self.max_connections) * 100,
            "file_descriptor_percent": (self.current_open_files / self.max_open_files) * 100,
        }

    def is_quota_exceeded(self) -> bool:
        """Check if quota exceeded.

        Returns:
            True if exceeded
        """
        utilization = self.get_utilization()
        return any(util > 100 for util in utilization.values())


class ResourceMonitor:
    """Monitors resource usage."""

    def __init__(self):
        """Initialize monitor."""
        self._quota = ResourceQuota()
        self._alerts: list[dict[str, Any]] = []

    def update_metrics(
        self,
        memory_mb: float | None = None,
        cpu_percent: float | None = None,
        connections: int | None = None,
        open_files: int | None = None,
    ) -> None:
        """Update resource metrics.

        Args:
            memory_mb: Memory usage
            cpu_percent: CPU usage
            connections: Active connections
            open_files: Open files
        """
        if memory_mb is not None:
            self._quota.current_memory_mb = memory_mb

        if cpu_percent is not None:
            self._quota.current_cpu_percent = cpu_percent

        if connections is not None:
            self._quota.current_connections = connections

        if open_files is not None:
            self._quota.current_open_files = open_files

        self._check_thresholds()

    def _check_thresholds(self) -> None:
        """Check resource thresholds."""
        utilization = self._quota.get_utilization()

        if utilization["memory_percent"] > 80:
            self._alert("HIGH_MEMORY", f"Memory usage {utilization['memory_percent']:.1f}%")

        if utilization["cpu_percent"] > self._quota.max_cpu_percent:
            self._alert("HIGH_CPU", f"CPU usage {utilization['cpu_percent']:.1f}%")

        if utilization["connection_percent"] > 80:
            self._alert(
                "HIGH_CONNECTIONS",
                f"Connections {self._quota.current_connections}/{self._quota.max_connections}",
            )

    def _alert(self, alert_type: str, message: str) -> None:
        """Create alert.

        Args:
            alert_type: Alert type
            message: Alert message
        """
        alert = {"type": alert_type, "message": message}
        self._alerts.append(alert)
        logger.warning(f"Alert: {alert_type} - {message}")

    def get_alerts(self) -> list[dict[str, str]]:
        """Get all alerts.

        Returns:
            List of alerts
        """
        return self._alerts.copy()

    def clear_alerts(self) -> None:
        """Clear alerts."""
        self._alerts.clear()

    def get_status(self) -> dict[str, Any]:
        """Get resource status.

        Returns:
            Status dict
        """
        return {
            "utilization": self._quota.get_utilization(),
            "quota_exceeded": self._quota.is_quota_exceeded(),
            "alerts": self._alerts,
        }
