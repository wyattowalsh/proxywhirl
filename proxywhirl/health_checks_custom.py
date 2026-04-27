"""Custom health check endpoints."""

from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class HealthStatus(str, Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: HealthStatus
    message: Optional[str] = None
    last_checked: datetime = None
    response_time_ms: float = 0.0


class CustomHealthCheckManager:
    """Manages custom health checks."""

    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.results: Dict[str, HealthCheckResult] = {}

    def register_check(self, name: str, check_func: Callable) -> None:
        """Register a custom health check."""
        self.checks[name] = check_func

    async def run_check(self, name: str) -> Optional[HealthCheckResult]:
        """Run a specific health check."""
        check_func = self.checks.get(name)
        if not check_func:
            return None

        try:
            import time

            start = time.time()
            result = await check_func() if hasattr(check_func, "__await__") else check_func()
            elapsed = (time.time() - start) * 1000

            health_result = HealthCheckResult(
                name=name,
                status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                response_time_ms=elapsed,
                last_checked=datetime.now(),
            )
            self.results[name] = health_result
            return health_result
        except Exception as e:
            result = HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
                last_checked=datetime.now(),
            )
            self.results[name] = result
            return result

    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all health checks."""
        for name in self.checks:
            await self.run_check(name)
        return self.results

    def get_overall_status(self) -> HealthStatus:
        """Get overall health status."""
        if not self.results:
            return HealthStatus.HEALTHY

        statuses = [r.status for r in self.results.values()]
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY
