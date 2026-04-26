"""
Retry metrics collection and aggregation.

Thread Safety:
    RetryMetrics uses threading.Lock for thread-safe operation in synchronous contexts.
    When used in async contexts (e.g., FastAPI endpoints), methods that acquire locks
    should be called using asyncio.to_thread() to prevent blocking the event loop.

Usage:
    Sync context (RetryExecutor, aggregation thread):
        metrics.record_attempt(attempt)
        metrics.aggregate_hourly()

    Async context (FastAPI endpoints):
        summary = await asyncio.to_thread(metrics.get_summary)
        timeseries = await asyncio.to_thread(metrics.get_timeseries, hours=24)
"""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from enum import Enum
from threading import Lock
from typing import Any

from pydantic import BaseModel, Field, PrivateAttr

from proxywhirl.circuit_breaker import CircuitBreakerState


class RetryOutcome(str, Enum):
    """Outcome of a retry attempt."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CIRCUIT_OPEN = "circuit_open"


class RetryAttempt(BaseModel):
    """Record of a single retry attempt."""

    request_id: str
    attempt_number: int = Field(ge=0)
    proxy_id: str
    timestamp: datetime
    outcome: RetryOutcome
    status_code: int | None = None
    delay_before: float = Field(ge=0)
    latency: float = Field(ge=0)
    error_message: str | None = None


class CircuitBreakerEvent(BaseModel):
    """Circuit breaker state change event."""

    proxy_id: str
    from_state: CircuitBreakerState
    to_state: CircuitBreakerState
    timestamp: datetime
    failure_count: int


class HourlyAggregate(BaseModel):
    """Hourly aggregated metrics."""

    hour: datetime  # Truncated to hour
    total_requests: int = 0
    total_retries: int = 0
    success_by_attempt: dict[int, int] = Field(default_factory=dict)
    failure_by_reason: dict[str, int] = Field(default_factory=dict)
    avg_latency: float = 0.0


class RetryMetrics(BaseModel):
    """Aggregated retry metrics collection."""

    # Current period (last hour, raw data)
    current_attempts: deque[RetryAttempt] = Field(default_factory=deque)

    # Historical data (last 24 hours, aggregated)
    hourly_aggregates: dict[datetime, HourlyAggregate] = Field(default_factory=dict)

    # Circuit breaker events
    circuit_breaker_events: list[CircuitBreakerEvent] = Field(default_factory=list)

    # Configuration
    retention_hours: int = Field(default=24)
    max_current_attempts: int = Field(default=10000)

    # Runtime (not serialized)
    _lock: Lock = PrivateAttr(default_factory=Lock)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        """Initialize with maxlen-bounded deque."""
        super().__init__(**data)
        # Replace unbounded deque with maxlen-bounded one
        max_attempts = data.get("max_current_attempts", 10000)
        self.current_attempts = deque(self.current_attempts, maxlen=max_attempts)

    def record_attempt(self, attempt: RetryAttempt) -> None:
        """Record a retry attempt."""
        with self._lock:
            self.current_attempts.append(attempt)
            # Auto-evicts oldest item when maxlen is reached

    def record_circuit_breaker_event(self, event: CircuitBreakerEvent) -> None:
        """Record circuit breaker state change."""
        with self._lock:
            self.circuit_breaker_events.append(event)

            # Keep last 1000 events
            if len(self.circuit_breaker_events) > 1000:
                self.circuit_breaker_events = self.circuit_breaker_events[-1000:]

    def aggregate_hourly(self) -> None:
        """Aggregate current_attempts into hourly summaries."""
        with self._lock:
            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(hours=self.retention_hours)

            # Group attempts by hour
            attempts_by_hour: dict[datetime, list[RetryAttempt]] = defaultdict(list)
            for attempt in self.current_attempts:
                if attempt.timestamp >= cutoff:
                    hour = attempt.timestamp.replace(minute=0, second=0, microsecond=0)
                    attempts_by_hour[hour].append(attempt)

            # Create/update hourly aggregates
            for hour, attempts in attempts_by_hour.items():
                if hour not in self.hourly_aggregates:
                    self.hourly_aggregates[hour] = HourlyAggregate(hour=hour)

                agg = self.hourly_aggregates[hour]
                agg.total_requests += len({a.request_id for a in attempts})
                agg.total_retries += len(attempts)

                for attempt in attempts:
                    if attempt.outcome == RetryOutcome.SUCCESS:
                        agg.success_by_attempt[attempt.attempt_number] = (
                            agg.success_by_attempt.get(attempt.attempt_number, 0) + 1
                        )
                    else:
                        reason = attempt.error_message or attempt.outcome.value
                        agg.failure_by_reason[reason] = agg.failure_by_reason.get(reason, 0) + 1

            # Remove old aggregates
            self.hourly_aggregates = {
                h: agg for h, agg in self.hourly_aggregates.items() if h >= cutoff
            }

    def get_summary(self) -> dict[str, Any]:
        """Get metrics summary for API response."""
        with self._lock:
            total_retries = len(self.current_attempts) + sum(
                agg.total_retries for agg in self.hourly_aggregates.values()
            )

            success_by_attempt: dict[int, int] = defaultdict(int)
            for agg in self.hourly_aggregates.values():
                for attempt_num, count in agg.success_by_attempt.items():
                    success_by_attempt[attempt_num] += count

            return {
                "total_retries": total_retries,
                "success_by_attempt": dict(success_by_attempt),
                "circuit_breaker_events_count": len(self.circuit_breaker_events),
                "retention_hours": self.retention_hours,
            }

    def get_timeseries(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get time-series data for the specified hours."""
        with self._lock:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

            data_points = []
            for hour, agg in sorted(self.hourly_aggregates.items()):
                if hour >= cutoff:
                    success_count = sum(agg.success_by_attempt.values())
                    total_attempts = agg.total_retries
                    success_rate = success_count / total_attempts if total_attempts > 0 else 0.0

                    data_points.append(
                        {
                            "timestamp": hour.isoformat(),
                            "total_requests": agg.total_requests,
                            "total_retries": agg.total_retries,
                            "success_rate": success_rate,
                            "avg_latency": agg.avg_latency,
                        }
                    )

            return data_points

    def get_by_proxy(self, hours: int = 24) -> dict[str, dict[str, Any]]:
        """Get per-proxy retry statistics."""
        with self._lock:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            proxy_stats: dict[str, dict[str, Any]] = defaultdict(
                lambda: {
                    "total_attempts": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "total_latency": 0.0,
                    "circuit_breaker_opens": 0,
                }
            )

            # Aggregate from current attempts
            for attempt in self.current_attempts:
                if attempt.timestamp >= cutoff:
                    stats = proxy_stats[attempt.proxy_id]
                    stats["total_attempts"] += 1
                    stats["total_latency"] += attempt.latency

                    if attempt.outcome == RetryOutcome.SUCCESS:
                        stats["success_count"] += 1
                    else:
                        stats["failure_count"] += 1

            # Count circuit breaker opens
            for event in self.circuit_breaker_events:
                if event.timestamp >= cutoff and event.to_state == CircuitBreakerState.OPEN:
                    proxy_stats[event.proxy_id]["circuit_breaker_opens"] += 1

            # Calculate average latency
            result = {}
            for proxy_id, stats in proxy_stats.items():
                avg_latency = (
                    stats["total_latency"] / stats["total_attempts"]
                    if stats["total_attempts"] > 0
                    else 0.0
                )
                result[proxy_id] = {
                    "proxy_id": proxy_id,
                    "total_attempts": stats["total_attempts"],
                    "success_count": stats["success_count"],
                    "failure_count": stats["failure_count"],
                    "avg_latency": avg_latency,
                    "circuit_breaker_opens": stats["circuit_breaker_opens"],
                }

            return result
