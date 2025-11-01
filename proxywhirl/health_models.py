"""
Pydantic models for health monitoring.

Defines data structures for health status, check results, events,
and pool statistics.
"""

from enum import Enum
from typing import Any

__all__ = [
    "HealthStatus",
    "HealthCheckResult",
    "HealthCheckConfig",
    "HealthEvent",
    "PoolStatus",
    "SourceStatus",
    "ProxyHealthState",
]


class HealthStatus(str, Enum):
    """Proxy health status states."""
    
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    CHECKING = "checking"
    RECOVERING = "recovering"
    PERMANENTLY_FAILED = "permanently_failed"
