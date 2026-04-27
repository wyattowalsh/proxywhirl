"""Adaptive health checking based on performance metrics."""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
from loguru import logger


@dataclass
class PerformanceMetric:
    """Performance metric for adaptive health checks."""

    response_time_ms: float
    success: bool
    timestamp: datetime


class AdaptiveHealthChecker:
    """Adaptive health checking with performance tracking."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics: deque = deque(maxlen=window_size)
        self.failure_threshold = 0.3
        self.latency_threshold_ms = 5000

    def record_metric(self, response_time_ms: float, success: bool) -> None:
        """Record a performance metric."""
        self.metrics.append(
            PerformanceMetric(
                response_time_ms=response_time_ms, success=success, timestamp=datetime.now()
            )
        )

    def get_failure_rate(self) -> float:
        """Calculate failure rate."""
        if not self.metrics:
            return 0.0
        failures = sum(1 for m in self.metrics if not m.success)
        return failures / len(self.metrics)

    def get_avg_latency(self) -> float:
        """Calculate average latency."""
        if not self.metrics:
            return 0.0
        return sum(m.response_time_ms for m in self.metrics) / len(self.metrics)

    def get_p95_latency(self) -> float:
        """Calculate 95th percentile latency."""
        if not self.metrics:
            return 0.0
        sorted_times = sorted([m.response_time_ms for m in self.metrics])
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[idx] if idx < len(sorted_times) else sorted_times[-1]

    def is_healthy(self) -> bool:
        """Determine if proxy is healthy based on adaptive thresholds."""
        if not self.metrics:
            return True

        failure_rate = self.get_failure_rate()
        p95_latency = self.get_p95_latency()

        return failure_rate <= self.failure_threshold and p95_latency <= self.latency_threshold_ms

    def adjust_thresholds(self) -> None:
        """Dynamically adjust thresholds based on recent performance."""
        if len(self.metrics) < 50:
            return

        avg_latency = self.get_avg_latency()
        self.latency_threshold_ms = avg_latency * 2
