"""
Pydantic models for health monitoring.

Defines data structures for health status, check results, events,
and pool statistics.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator

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


class HealthCheckResult(BaseModel):
    """Result of a single health check operation.

    Captures the outcome of checking a proxy's availability,
    including timing, status code, and any error messages.
    """

    proxy_url: str = Field(..., description="Proxy URL that was checked")
    check_time: datetime = Field(..., description="When the check was performed")
    status: HealthStatus = Field(..., description="Result of the health check")
    check_url: str = Field(..., description="URL that was checked through the proxy")
    response_time_ms: Optional[float] = Field(None, description="Response time in milliseconds")
    status_code: Optional[int] = Field(None, description="HTTP status code received")
    error_message: Optional[str] = Field(None, description="Error message if check failed")


class HealthCheckConfig(BaseModel):
    """Configuration for health checking behavior.

    Controls how often checks run, what timeouts to use,
    and what failure thresholds trigger status changes.
    """

    check_interval_seconds: int = Field(
        default=60, ge=10, description="Seconds between health checks (minimum 10)"
    )
    failure_threshold: int = Field(
        default=3, ge=1, description="Consecutive failures before marking unhealthy"
    )
    success_threshold: int = Field(
        default=2, ge=1, description="Consecutive successes before marking healthy"
    )
    check_timeout_seconds: float = Field(
        default=10.0, gt=0, description="Timeout for each health check request"
    )
    check_url: str = Field(
        default="http://www.google.com", description="Target URL to check through proxy"
    )
    expected_status_codes: list[int] = Field(
        default_factory=lambda: [200], description="HTTP status codes considered healthy"
    )
    max_recovery_attempts: int = Field(
        default=5, ge=0, description="Maximum recovery attempts before permanent failure"
    )
    recovery_cooldown_base_seconds: int = Field(
        default=60, gt=0, description="Base cooldown period for recovery (exponential backoff)"
    )
    source_intervals: dict[str, int] = Field(
        default_factory=dict, description="Per-source interval overrides (source name -> seconds)"
    )
    history_retention_hours: int = Field(
        default=24, ge=1, description="How long to keep health check history"
    )

    @field_validator("check_url")
    @classmethod
    def validate_check_url(cls, v: str) -> str:
        """Ensure check_url is a valid http/https URL."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("check_url must be a valid http:// or https:// URL")
        return v


class HealthEvent(BaseModel):
    """A significant health monitoring event."""

    event_type: str  # Placeholder for now
    timestamp: datetime
    proxy_url: Optional[str] = None


class PoolStatus(BaseModel):
    """Aggregate health statistics for the proxy pool."""

    total_proxies: int = 0
    healthy_proxies: int = 0
    unhealthy_proxies: int = 0
    checking_proxies: int = 0
    recovering_proxies: int = 0
    unknown_proxies: int = 0
    by_source: dict[str, "SourceStatus"] = Field(default_factory=dict)

    @property
    def health_percentage(self) -> float:
        """Calculate percentage of healthy proxies."""
        if self.total_proxies == 0:
            return 0.0
        return (self.healthy_proxies / self.total_proxies) * 100.0

    @property
    def is_degraded(self) -> bool:
        """Check if pool health is degraded (less than 50% healthy)."""
        return self.health_percentage < 50.0


class SourceStatus(BaseModel):
    """Health statistics for a specific proxy source."""

    source_name: str
    total_proxies: int = 0
    healthy_proxies: int = 0
    unhealthy_proxies: int = 0
    checking_proxies: int = 0
    recovering_proxies: int = 0
    unknown_proxies: int = 0

    @property
    def health_percentage(self) -> float:
        """Calculate percentage of healthy proxies for this source."""
        if self.total_proxies == 0:
            return 0.0
        return (self.healthy_proxies / self.total_proxies) * 100.0


class ProxyHealthState(BaseModel):
    """Complete health state for a single proxy."""

    proxy_url: str
    health_status: HealthStatus
    last_check: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
