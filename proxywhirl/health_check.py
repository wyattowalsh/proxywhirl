"""Health check and monitoring utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from loguru import logger


class HealthStatus(str, Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: HealthStatus
    timestamp: datetime = field(default_factory=datetime.now)
    message: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict."""
        return {
            "name": self.name,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "metrics": self.metrics,
        }


class HealthChecker:
    """Base class for health checks."""

    async def check(self) -> HealthCheckResult:
        """Perform health check.

        Returns:
            Health check result
        """
        raise NotImplementedError


class CompositeHealthChecker:
    """Combines multiple health checks."""

    def __init__(self):
        """Initialize composite checker."""
        self._checkers: dict[str, HealthChecker] = {}
        self._results: list[HealthCheckResult] = []

    def add_checker(self, name: str, checker: HealthChecker) -> None:
        """Add a health checker.

        Args:
            name: Name of checker
            checker: HealthChecker instance
        """
        self._checkers[name] = checker
        logger.debug(f"Added health checker: {name}")

    async def check_all(self) -> list[HealthCheckResult]:
        """Run all health checks.

        Returns:
            List of results
        """
        results = []

        for name, checker in self._checkers.items():
            try:
                result = await checker.check()
                results.append(result)
                self._results.append(result)
            except Exception as e:
                logger.error(f"Health check failed: {name}: {e}")
                result = HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(e),
                )
                results.append(result)
                self._results.append(result)

        return results

    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status.

        Returns:
            Overall health status
        """
        if not self._results:
            return HealthStatus.UNKNOWN

        statuses = {result.status for result in self._results}

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY

        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED

        if HealthStatus.HEALTHY in statuses:
            return HealthStatus.HEALTHY

        return HealthStatus.UNKNOWN

    def get_report(self) -> dict[str, Any]:
        """Get comprehensive health report.

        Returns:
            Health report dict
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self.get_overall_status().value,
            "checks": [result.to_dict() for result in self._results[-20:]],
        }


class SimpleHealthCheck(HealthChecker):
    """Simple health check that runs a callable."""

    def __init__(
        self,
        check_fn: Callable[[], bool],
        name: str = "simple_check",
        metrics_fn: Callable[[], dict[str, Any]] | None = None,
    ):
        """Initialize simple health check.

        Args:
            check_fn: Function returning True for healthy
            name: Check name
            metrics_fn: Optional function returning metrics dict
        """
        self.check_fn = check_fn
        self.name = name
        self.metrics_fn = metrics_fn

    async def check(self) -> HealthCheckResult:
        """Perform health check."""
        try:
            is_healthy = self.check_fn()
            status = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY

            metrics = {}
            if self.metrics_fn:
                metrics = self.metrics_fn()

            return HealthCheckResult(
                name=self.name,
                status=status,
                metrics=metrics,
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
            )


class ThresholdHealthCheck(HealthChecker):
    """Health check based on metric thresholds."""

    def __init__(
        self,
        name: str,
        get_value_fn: Callable[[], float],
        warning_threshold: float,
        critical_threshold: float,
        inverted: bool = False,
    ):
        """Initialize threshold check.

        Args:
            name: Check name
            get_value_fn: Function returning current value
            warning_threshold: Warning level
            critical_threshold: Critical level
            inverted: If True, higher values are worse
        """
        self.name = name
        self.get_value_fn = get_value_fn
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.inverted = inverted

    async def check(self) -> HealthCheckResult:
        """Perform health check."""
        try:
            value = self.get_value_fn()

            if self.inverted:
                is_critical = value > self.critical_threshold
                is_warning = value > self.warning_threshold
            else:
                is_critical = value < self.critical_threshold
                is_warning = value < self.warning_threshold

            if is_critical:
                status = HealthStatus.UNHEALTHY
            elif is_warning:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY

            return HealthCheckResult(
                name=self.name,
                status=status,
                metrics={"current_value": value},
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
            )
