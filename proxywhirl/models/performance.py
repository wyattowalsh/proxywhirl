"""proxywhirl/models/performance.py -- Performance metrics and error tracking models

This module contains models for tracking proxy performance, error states,
and reliability metrics with industry-standard indicators and patterns.

Features:
- Enhanced performance metrics with percentiles
- Error state tracking and cooldown management
- Lightweight dataclasses for high-performance scenarios
- Industry-standard reliability indicators
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, computed_field

from .enums import ErrorHandlingPolicy, ValidationErrorType
from .types import ResponseTimeSeconds, SuccessRate, UptimePercentage


@dataclass(frozen=True, slots=True)
class CoreProxy:
    """Lightweight, immutable proxy representation for high-performance scenarios."""
    host: str
    port: int
    scheme: str
    
    @property
    def url(self) -> str:
        """Generate proxy URL."""
        return f"{self.scheme}://{self.host}:{self.port}"


@dataclass(frozen=True, slots=True)
class ErrorEvent:
    """Immutable error event record for performance tracking."""
    timestamp: datetime
    error_type: ValidationErrorType
    error_message: Optional[str] = None
    http_status: Optional[int] = None


class ProxyErrorState(BaseModel):
    """Tracks error state and history for a proxy."""

    # Current error state
    consecutive_failures: int = 0
    last_error_type: Optional[ValidationErrorType] = None
    last_error_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None

    # Error history (limited to last 10 for memory efficiency)
    error_history: List[ErrorEvent] = Field(default_factory=list)

    # Cooldown state
    is_in_cooldown: bool = False
    cooldown_until: Optional[datetime] = None
    cooldown_policy: Optional[ErrorHandlingPolicy] = None

    # Failure pattern analysis
    failure_rate_1h: float = 0.0  # Failures per hour in last hour
    failure_rate_24h: float = 0.0  # Failures per hour in last 24h

    def add_error(
        self,
        error_type: ValidationErrorType,
        error_message: Optional[str] = None,
        http_status: Optional[int] = None,
    ) -> None:
        """Add an error event and update state."""
        now = datetime.now(timezone.utc)
        
        # Update consecutive failures
        self.consecutive_failures += 1
        self.last_error_type = error_type
        self.last_error_time = now
        
        # Add to error history (keep only last 10)
        error_event = ErrorEvent(
            timestamp=now,
            error_type=error_type,
            error_message=error_message,
            http_status=http_status,
        )
        self.error_history.append(error_event)
        if len(self.error_history) > 10:
            self.error_history.pop(0)
        
        # Update failure rates (simplified calculation)
        self._update_failure_rates()

    def add_success(self) -> None:
        """Record a successful operation."""
        self.consecutive_failures = 0
        self.last_success_time = datetime.now(timezone.utc)
        self.last_error_type = None

    def is_available(self) -> bool:
        """Check if proxy is available (not in cooldown)."""
        if not self.is_in_cooldown:
            return True
        
        if self.cooldown_until is None:
            return True
            
        return datetime.now(timezone.utc) >= self.cooldown_until

    def set_cooldown(self, policy: ErrorHandlingPolicy, duration_seconds: int) -> None:
        """Set proxy in cooldown state."""
        self.is_in_cooldown = True
        self.cooldown_policy = policy
        self.cooldown_until = datetime.now(timezone.utc).replace(
            microsecond=0
        ) + timedelta(seconds=duration_seconds)

    def clear_cooldown(self) -> None:
        """Clear cooldown state."""
        self.is_in_cooldown = False
        self.cooldown_until = None
        self.cooldown_policy = None

    def _update_failure_rates(self) -> None:
        """Update failure rates based on error history."""
        if not self.error_history:
            self.failure_rate_1h = 0.0
            self.failure_rate_24h = 0.0
            return
        
        now = datetime.now(timezone.utc)
        
        # Count errors in last hour
        errors_1h = sum(
            1 for error in self.error_history
            if (now - error.timestamp).total_seconds() <= 3600
        )
        self.failure_rate_1h = errors_1h
        
        # Count errors in last 24 hours
        errors_24h = sum(
            1 for error in self.error_history
            if (now - error.timestamp).total_seconds() <= 86400
        )
        self.failure_rate_24h = errors_24h / 24.0  # Per hour average


class ProxyCredentials(BaseModel):
    """Authentication credentials for proxy access."""

    username: str
    password: str
    auth_type: str = "basic"  # basic, ntlm, etc.


class ProxyPerformanceMetrics(BaseModel):
    """Enhanced performance and reliability metrics with industry-standard indicators."""

    # Basic request statistics
    success_count: int = 0
    failure_count: int = 0
    total_requests: int = 0

    # Response time metrics (enhanced with percentiles)
    avg_response_time: Optional[ResponseTimeSeconds] = None
    min_response_time: Optional[ResponseTimeSeconds] = None
    max_response_time: Optional[ResponseTimeSeconds] = None
    p50_response_time: Optional[ResponseTimeSeconds] = Field(
        None, description="50th percentile (median) response time"
    )
    p95_response_time: Optional[ResponseTimeSeconds] = Field(
        None, description="95th percentile response time"
    )
    p99_response_time: Optional[ResponseTimeSeconds] = Field(
        None, description="99th percentile response time"
    )

    # Uptime and availability
    uptime_percentage: Optional[UptimePercentage] = None

    # Failure tracking (industry standard)
    consecutive_failures: int = Field(0, description="Consecutive failures since last success")
    max_consecutive_failures: int = Field(0, description="Maximum consecutive failures recorded")

    # Health check metrics
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    health_check_interval: int = Field(30, description="Health check interval in seconds")

    # Connection-specific metrics
    connection_success_rate: Optional[SuccessRate] = Field(
        None, description="TCP connection establishment success rate"
    )
    dns_resolution_time: Optional[ResponseTimeSeconds] = Field(
        None, description="Average DNS resolution time"
    )
    ssl_handshake_time: Optional[ResponseTimeSeconds] = Field(
        None, description="Average SSL handshake time"
    )

    # Bandwidth and throughput
    bytes_transferred: int = Field(0, description="Total bytes transferred through proxy")
    avg_bandwidth_mbps: Optional[float] = Field(
        None, ge=0.0, description="Average bandwidth in Mbps"
    )

    @computed_field
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return round(self.success_count / self.total_requests, 4)

    @computed_field
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        if self.total_requests == 0:
            return 0.0
        return round(self.failure_count / self.total_requests, 4)

    @computed_field
    @property
    def reliability_score(self) -> float:
        """Calculate reliability score (0.0-1.0) based on multiple factors."""
        if self.total_requests == 0:
            return 0.0
        
        # Base score from success rate
        base_score = self.success_rate
        
        # Consecutive failures penalty
        if self.consecutive_failures > 0:
            penalty = min(0.3, self.consecutive_failures * 0.05)
            base_score = max(0.0, base_score - penalty)
        
        # Uptime bonus
        if self.uptime_percentage is not None and self.uptime_percentage > 95.0:
            base_score = min(1.0, base_score * 1.05)
        
        return round(base_score, 4)

    @computed_field
    @property
    def performance_score(self) -> float:
        """Calculate performance score (0.0-1.0) based on response times."""
        if self.avg_response_time is None:
            return 0.0
        
        # Score based on average response time (lower is better)
        if self.avg_response_time <= 0.5:
            return 1.0
        elif self.avg_response_time <= 1.0:
            return 0.9
        elif self.avg_response_time <= 2.0:
            return 0.7
        elif self.avg_response_time <= 5.0:
            return 0.5
        else:
            return 0.2

    @computed_field
    @property
    def is_healthy(self) -> bool:
        """Determine if proxy is considered healthy."""
        return (
            self.success_rate >= 0.8 and
            self.consecutive_failures < 3 and
            (self.avg_response_time is None or self.avg_response_time < 10.0)
        )

    @computed_field
    @property
    def health_grade(self) -> str:
        """Get letter grade for overall health."""
        if not self.is_healthy:
            return "F"
        
        score = (self.reliability_score + self.performance_score) / 2
        
        if score >= 0.95:
            return "A+"
        elif score >= 0.90:
            return "A"
        elif score >= 0.85:
            return "A-"
        elif score >= 0.80:
            return "B+"
        elif score >= 0.75:
            return "B"
        elif score >= 0.70:
            return "B-"
        elif score >= 0.65:
            return "C+"
        elif score >= 0.60:
            return "C"
        elif score >= 0.55:
            return "C-"
        elif score >= 0.50:
            return "D"
        else:
            return "F"


class ProxyCapabilities(BaseModel):
    """Proxy feature support information."""

    supports_https: bool = True
    supports_connect_method: bool = True
    supports_udp: bool = False
    max_concurrent_connections: Optional[int] = None
    bandwidth_limit_mbps: Optional[float] = None
    protocol_versions: List[str] = Field(default_factory=list)
