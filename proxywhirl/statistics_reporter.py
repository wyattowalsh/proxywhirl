"""Statistics collection and reporting."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MetricType(str, Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """A metric value."""

    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    tags: dict[str, str] = field(default_factory=dict)
    unit: str | None = None


class StatisticsCollector:
    """Collects statistics and metrics."""

    def __init__(self):
        """Initialize collector."""
        self._metrics: dict[str, list[Metric]] = {}
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}

    def increment_counter(
        self, name: str, value: int = 1, tags: dict[str, str] | None = None
    ) -> None:
        """Increment a counter.

        Args:
            name: Metric name
            value: Value to add
            tags: Optional tags
        """
        self._counters[name] = self._counters.get(name, 0) + value

        metric = Metric(
            name=name,
            value=float(value),
            metric_type=MetricType.COUNTER,
            tags=tags or {},
        )
        self._record_metric(metric)

    def set_gauge(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Set a gauge value.

        Args:
            name: Metric name
            value: Value
            tags: Optional tags
        """
        self._gauges[name] = value

        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            tags=tags or {},
        )
        self._record_metric(metric)

    def record_histogram(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Record a histogram value.

        Args:
            name: Metric name
            value: Value
            tags: Optional tags
        """
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            tags=tags or {},
        )
        self._record_metric(metric)

    def record_timer(
        self, name: str, duration_ms: float, tags: dict[str, str] | None = None
    ) -> None:
        """Record a timer value.

        Args:
            name: Metric name
            duration_ms: Duration in milliseconds
            tags: Optional tags
        """
        metric = Metric(
            name=name,
            value=duration_ms,
            metric_type=MetricType.TIMER,
            tags=tags or {},
            unit="ms",
        )
        self._record_metric(metric)

    def _record_metric(self, metric: Metric) -> None:
        """Record a metric."""
        if metric.name not in self._metrics:
            self._metrics[metric.name] = []
        self._metrics[metric.name].append(metric)

    def get_counter(self, name: str) -> int:
        """Get counter value.

        Args:
            name: Counter name

        Returns:
            Counter value
        """
        return self._counters.get(name, 0)

    def get_gauge(self, name: str) -> float | None:
        """Get gauge value.

        Args:
            name: Gauge name

        Returns:
            Gauge value or None
        """
        return self._gauges.get(name)

    def get_metrics(self, name: str | None = None) -> list[Metric]:
        """Get metrics.

        Args:
            name: Optional filter by name

        Returns:
            List of metrics
        """
        if name:
            return self._metrics.get(name, [])
        return [m for metrics in self._metrics.values() for m in metrics]

    def clear(self) -> None:
        """Clear all metrics."""
        self._metrics.clear()
        self._counters.clear()
        self._gauges.clear()


@dataclass
class StatisticsReport:
    """Report of statistics."""

    title: str
    timestamp: datetime = field(default_factory=datetime.now)
    metrics: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)


class StatisticsReporter:
    """Generates statistics reports."""

    def __init__(self, collector: StatisticsCollector):
        """Initialize reporter.

        Args:
            collector: StatisticsCollector instance
        """
        self.collector = collector

    def generate_report(self, title: str) -> StatisticsReport:
        """Generate a statistics report.

        Args:
            title: Report title

        Returns:
            StatisticsReport
        """
        metrics = {}
        summary = {}

        for metric_name, metric_values in self.collector._metrics.items():
            if not metric_values:
                continue

            values = [m.value for m in metric_values]

            metrics[metric_name] = {
                "count": len(values),
                "sum": sum(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "type": metric_values[0].metric_type.value,
            }

        # Build summary
        summary["total_metrics"] = len(metrics)
        summary["counters"] = len(self.collector._counters)
        summary["gauges"] = len(self.collector._gauges)

        return StatisticsReport(
            title=title,
            metrics=metrics,
            summary=summary,
        )

    def export_json(self, report: StatisticsReport) -> str:
        """Export report to JSON.

        Args:
            report: StatisticsReport

        Returns:
            JSON string
        """
        return json.dumps(
            {
                "title": report.title,
                "timestamp": report.timestamp.isoformat(),
                "metrics": report.metrics,
                "summary": report.summary,
            },
            indent=2,
        )

    def export_markdown(self, report: StatisticsReport) -> str:
        """Export report to Markdown.

        Args:
            report: StatisticsReport

        Returns:
            Markdown string
        """
        lines = [f"# {report.title}", ""]
        lines.append(f"*Generated: {report.timestamp.isoformat()}*")
        lines.append("")

        # Summary section
        lines.append("## Summary")
        for key, value in report.summary.items():
            lines.append(f"- **{key}**: {value}")
        lines.append("")

        # Metrics section
        lines.append("## Metrics")
        if report.metrics:
            lines.append("| Metric | Count | Sum | Avg | Min | Max | Type |")
            lines.append("|--------|-------|-----|-----|-----|-----|------|")

            for name, stats in sorted(report.metrics.items()):
                lines.append(
                    f"| {name} | {stats['count']} | {stats['sum']:.2f} | "
                    f"{stats['avg']:.2f} | {stats['min']:.2f} | {stats['max']:.2f} | "
                    f"{stats['type']} |"
                )

        return "\n".join(lines)
