"""Service metrics and monitoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from loguru import logger


@dataclass
class ServiceMetrics:
    """Service metrics snapshot."""

    uptime_seconds: float = 0.0
    requests_total: int = 0
    requests_success: int = 0
    requests_failed: int = 0
    avg_response_time_ms: float = 0.0
    errors_count: int = 0
    last_error: str | None = None
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        """Get success rate."""
        if self.requests_total == 0:
            return 0.0
        return (self.requests_success / self.requests_total) * 100

    @property
    def error_rate(self) -> float:
        """Get error rate."""
        if self.requests_total == 0:
            return 0.0
        return (self.requests_failed / self.requests_total) * 100


class ServiceHealthChecker:
    """Checks service health."""

    def __init__(
        self,
        min_success_rate: float = 0.95,
        max_error_count: int = 100,
        max_response_time_ms: float = 5000.0,
    ):
        """Initialize health checker.

        Args:
            min_success_rate: Minimum success rate (0-1)
            max_error_count: Maximum error count threshold
            max_response_time_ms: Maximum response time threshold
        """
        self.min_success_rate = min_success_rate
        self.max_error_count = max_error_count
        self.max_response_time_ms = max_response_time_ms

    def is_healthy(self, metrics: ServiceMetrics) -> bool:
        """Check if service is healthy.

        Args:
            metrics: Service metrics

        Returns:
            True if healthy
        """
        success_rate = metrics.success_rate / 100 if metrics.requests_total > 0 else 1.0

        checks = [
            success_rate >= self.min_success_rate,
            metrics.errors_count <= self.max_error_count,
            metrics.avg_response_time_ms <= self.max_response_time_ms,
        ]

        return all(checks)

    def get_health_status(self, metrics: ServiceMetrics) -> dict[str, Any]:
        """Get health status.

        Args:
            metrics: Service metrics

        Returns:
            Health status dict
        """
        is_healthy = self.is_healthy(metrics)
        issues = []

        if metrics.requests_total > 0:
            success_rate = metrics.success_rate / 100
            if success_rate < self.min_success_rate:
                issues.append(f"Success rate {success_rate:.1%} below threshold")

        if metrics.errors_count > self.max_error_count:
            issues.append(f"Error count {metrics.errors_count} exceeds threshold")

        if metrics.avg_response_time_ms > self.max_response_time_ms:
            issues.append(f"Response time {metrics.avg_response_time_ms:.0f}ms exceeds threshold")

        return {
            "is_healthy": is_healthy,
            "status": "healthy" if is_healthy else "unhealthy",
            "issues": issues,
            "metrics": metrics,
        }


class MetricsCollector:
    """Collects service metrics."""

    def __init__(self):
        """Initialize collector."""
        self._metrics = ServiceMetrics()
        self._start_time = datetime.now()

    def record_request(self, success: bool, response_time_ms: float) -> None:
        """Record a request.

        Args:
            success: Whether request succeeded
            response_time_ms: Response time in milliseconds
        """
        self._metrics.requests_total += 1

        if success:
            self._metrics.requests_success += 1
        else:
            self._metrics.requests_failed += 1

        # Update average response time
        if self._metrics.requests_total == 1:
            self._metrics.avg_response_time_ms = response_time_ms
        else:
            # Running average
            old_avg = self._metrics.avg_response_time_ms
            self._metrics.avg_response_time_ms = (
                old_avg * (self._metrics.requests_total - 1) + response_time_ms
            ) / self._metrics.requests_total

    def record_error(self, error_message: str) -> None:
        """Record an error.

        Args:
            error_message: Error message
        """
        self._metrics.errors_count += 1
        self._metrics.last_error = error_message
        logger.warning(f"Error recorded: {error_message}")

    def set_resource_usage(self, memory_mb: float, cpu_percent: float) -> None:
        """Set resource usage metrics.

        Args:
            memory_mb: Memory usage in MB
            cpu_percent: CPU usage as percentage
        """
        self._metrics.memory_usage_mb = memory_mb
        self._metrics.cpu_usage_percent = cpu_percent

    def get_metrics(self) -> ServiceMetrics:
        """Get current metrics.

        Returns:
            Service metrics
        """
        elapsed = (datetime.now() - self._start_time).total_seconds()
        self._metrics.uptime_seconds = elapsed
        return self._metrics

    def reset(self) -> None:
        """Reset metrics."""
        self._metrics = ServiceMetrics()
        self._start_time = datetime.now()
        logger.info("Metrics reset")


class AlertManager:
    """Manages alerts based on metrics."""

    def __init__(self):
        """Initialize alert manager."""
        self._alerts: list[dict[str, Any]] = []
        self._alert_handlers: list[callable] = []

    def add_alert_handler(self, handler: callable) -> None:
        """Add alert handler.

        Args:
            handler: Handler function
        """
        self._alert_handlers.append(handler)

    def check_and_alert(
        self,
        metrics: ServiceMetrics,
        thresholds: dict[str, float] | None = None,
    ) -> None:
        """Check metrics and send alerts.

        Args:
            metrics: Service metrics
            thresholds: Alert thresholds
        """
        thresholds = thresholds or {}

        # Check success rate
        if metrics.requests_total > 0:
            success_rate = metrics.success_rate / 100
            threshold = thresholds.get("success_rate", 0.95)
            if success_rate < threshold:
                self._send_alert(
                    "LOW_SUCCESS_RATE",
                    f"Success rate {success_rate:.1%} below threshold {threshold:.1%}",
                )

        # Check error count
        threshold = thresholds.get("error_count", 100)
        if metrics.errors_count > threshold:
            self._send_alert(
                "HIGH_ERROR_COUNT",
                f"Error count {metrics.errors_count} exceeds threshold {threshold}",
            )

        # Check response time
        threshold = thresholds.get("response_time_ms", 5000)
        if metrics.avg_response_time_ms > threshold:
            self._send_alert(
                "SLOW_RESPONSE",
                f"Response time {metrics.avg_response_time_ms:.0f}ms exceeds threshold {threshold}ms",
            )

    def _send_alert(self, alert_type: str, message: str) -> None:
        """Send alert.

        Args:
            alert_type: Alert type
            message: Alert message
        """
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

        self._alerts.append(alert)

        for handler in self._alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.warning(f"Alert handler error: {e}")

    def get_alerts(self) -> list[dict[str, Any]]:
        """Get all alerts.

        Returns:
            List of alerts
        """
        return self._alerts.copy()

    def clear_alerts(self) -> None:
        """Clear alerts."""
        self._alerts.clear()
