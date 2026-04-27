"""Advanced logging utilities and formatters."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from loguru import logger


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Structured log entry."""

    level: LogLevel
    message: str
    timestamp: str
    module: str
    function: str
    line: int
    extra: dict[str, Any]


class StructuredLogger:
    """Provides structured logging."""

    @staticmethod
    def log_event(
        level: LogLevel,
        message: str,
        module: str = "",
        function: str = "",
        line: int = 0,
        **extra: Any,
    ) -> None:
        """Log a structured event.

        Args:
            level: Log level
            message: Log message
            module: Module name
            function: Function name
            line: Line number
            **extra: Extra fields
        """
        context = {
            "module": module,
            "function": function,
            "line": line,
            **extra,
        }

        if level == LogLevel.DEBUG:
            logger.debug(message, **context)
        elif level == LogLevel.INFO:
            logger.info(message, **context)
        elif level == LogLevel.WARNING:
            logger.warning(message, **context)
        elif level == LogLevel.ERROR:
            logger.error(message, **context)
        elif level == LogLevel.CRITICAL:
            logger.critical(message, **context)

    @staticmethod
    def log_performance(
        operation: str,
        duration_ms: float,
        status: str = "success",
        **metadata: Any,
    ) -> None:
        """Log performance metrics.

        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            status: Operation status
            **metadata: Additional metadata
        """
        logger.info(
            f"Performance: {operation} completed in {duration_ms:.2f}ms",
            operation=operation,
            duration_ms=duration_ms,
            status=status,
            **metadata,
        )

    @staticmethod
    def log_request(
        method: str,
        url: str,
        status_code: int | None = None,
        duration_ms: float | None = None,
        **metadata: Any,
    ) -> None:
        """Log HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            status_code: Response status code
            duration_ms: Request duration
            **metadata: Additional metadata
        """
        message = f"{method} {url}"
        if status_code:
            message += f" -> {status_code}"

        logger.info(
            message,
            method=method,
            url=url,
            status_code=status_code,
            duration_ms=duration_ms,
            **metadata,
        )

    @staticmethod
    def log_error_with_context(
        error: Exception,
        operation: str = "",
        **context: Any,
    ) -> None:
        """Log error with context.

        Args:
            error: Exception
            operation: Operation being performed
            **context: Error context
        """
        logger.error(
            f"Error in {operation}: {error}",
            error_type=type(error).__name__,
            error_message=str(error),
            operation=operation,
            **context,
        )


class LogAggregator:
    """Aggregates logs for analysis."""

    def __init__(self):
        """Initialize aggregator."""
        self._logs: list[LogEntry] = []
        self._stats: dict[str, int] = {}

    def add_log(self, entry: LogEntry) -> None:
        """Add log entry.

        Args:
            entry: Log entry
        """
        self._logs.append(entry)

        level_key = f"{entry.level.value}_count"
        self._stats[level_key] = self._stats.get(level_key, 0) + 1

    def get_summary(self) -> dict[str, Any]:
        """Get log summary.

        Returns:
            Summary dict
        """
        return {
            "total_logs": len(self._logs),
            "by_level": self._stats,
            "earliest": self._logs[0].timestamp if self._logs else None,
            "latest": self._logs[-1].timestamp if self._logs else None,
        }

    def filter_by_level(self, level: LogLevel) -> list[LogEntry]:
        """Filter logs by level.

        Args:
            level: Log level

        Returns:
            Filtered logs
        """
        return [log for log in self._logs if log.level == level]

    def filter_by_module(self, module: str) -> list[LogEntry]:
        """Filter logs by module.

        Args:
            module: Module name

        Returns:
            Filtered logs
        """
        return [log for log in self._logs if module in log.module]

    def export_json(self) -> str:
        """Export logs as JSON.

        Returns:
            JSON string
        """
        return json.dumps(
            [
                {
                    "level": entry.level.value,
                    "message": entry.message,
                    "timestamp": entry.timestamp,
                    "module": entry.module,
                    "function": entry.function,
                    "line": entry.line,
                    "extra": entry.extra,
                }
                for entry in self._logs
            ],
            indent=2,
        )

    def clear(self) -> None:
        """Clear all logs."""
        self._logs.clear()
        self._stats.clear()


class PerformanceMonitor:
    """Monitors performance metrics."""

    def __init__(self):
        """Initialize monitor."""
        self._metrics: dict[str, list[float]] = {}

    def record_metric(self, name: str, value: float) -> None:
        """Record a metric.

        Args:
            name: Metric name
            value: Metric value
        """
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(value)

    def get_metric_stats(self, name: str) -> dict[str, float] | None:
        """Get statistics for a metric.

        Args:
            name: Metric name

        Returns:
            Statistics dict or None
        """
        values = self._metrics.get(name, [])
        if not values:
            return None

        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    def get_all_stats(self) -> dict[str, dict[str, float]]:
        """Get all metric statistics.

        Returns:
            Dict of metric name to stats
        """
        result = {}
        for name in self._metrics:
            stats = self.get_metric_stats(name)
            if stats:
                result[name] = stats

        return result
