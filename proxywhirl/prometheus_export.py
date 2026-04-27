"""Prometheus metrics export and scraping endpoint.

Provides:
- Prometheus-compatible metrics endpoint
- Custom metric registration and export
- Metrics scraping for monitoring systems
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from loguru import logger


class MetricType(str, Enum):
    """Prometheus metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Single metric data point."""

    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE
    help_text: str = ""


@dataclass
class PrometheusRegistry:
    """Prometheus metrics registry."""

    metrics: dict[str, list[Metric]] = field(default_factory=lambda: defaultdict(list))
    _lock: Any = field(default=None)

    def register_counter(
        self,
        name: str,
        value: float = 0,
        help_text: str = "",
        labels: dict[str, str] | None = None,
    ) -> None:
        """Register a counter metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            help_text=help_text,
            labels=labels or {},
        )
        self.metrics[name].append(metric)

    def register_gauge(
        self,
        name: str,
        value: float = 0,
        help_text: str = "",
        labels: dict[str, str] | None = None,
    ) -> None:
        """Register a gauge metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            help_text=help_text,
            labels=labels or {},
        )
        self.metrics[name].append(metric)

    def record_counter(
        self,
        name: str,
        value: float = 1,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a counter increment."""
        if labels:
            f"{name}_{hash(frozenset(labels.items()))}"

        found = False
        for metric in self.metrics[name]:
            if metric.labels == (labels or {}):
                metric.value += value
                metric.timestamp = time.time()
                found = True
                break

        if not found:
            metric = Metric(
                name=name,
                value=value,
                metric_type=MetricType.COUNTER,
                labels=labels or {},
            )
            self.metrics[name].append(metric)

    def record_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a gauge value."""
        found = False
        for metric in self.metrics[name]:
            if metric.labels == (labels or {}):
                metric.value = value
                metric.timestamp = time.time()
                found = True
                break

        if not found:
            metric = Metric(
                name=name,
                value=value,
                metric_type=MetricType.GAUGE,
                labels=labels or {},
            )
            self.metrics[name].append(metric)

    def get_metrics(self) -> dict[str, list[Metric]]:
        """Get all registered metrics."""
        return dict(self.metrics)

    def clear(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()

    def to_prometheus_format(self) -> str:
        """Export metrics in Prometheus text format."""
        output = []

        for name, metric_list in sorted(self.metrics.items()):
            if not metric_list:
                continue

            # Add metric help text from first metric
            help_text = metric_list[0].help_text
            if help_text:
                output.append(f"# HELP {name} {help_text}")

            # Add metric type from first metric
            metric_type = metric_list[0].metric_type.value
            output.append(f"# TYPE {name} {metric_type}")

            # Add all metric values
            for metric in metric_list:
                if metric.labels:
                    label_str = ",".join([f'{k}="{v}"' for k, v in sorted(metric.labels.items())])
                    output.append(
                        f"{name}{{{label_str}}} {metric.value} {int(metric.timestamp * 1000)}"
                    )
                else:
                    output.append(f"{name} {metric.value} {int(metric.timestamp * 1000)}")

        return "\n".join(output) + "\n"


# Global registry instance
_global_registry: PrometheusRegistry | None = None


def get_registry() -> PrometheusRegistry:
    """Get or create global Prometheus registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = PrometheusRegistry()
    return _global_registry


def export_metrics() -> str:
    """Export all metrics in Prometheus format."""
    registry = get_registry()
    return registry.to_prometheus_format()


def register_default_metrics() -> None:
    """Register default proxywhirl metrics."""
    registry = get_registry()

    # Proxy pool metrics
    registry.register_gauge(
        "proxywhirl_pool_total_proxies",
        help_text="Total number of proxies in pool",
    )
    registry.register_gauge(
        "proxywhirl_pool_healthy_proxies",
        help_text="Number of healthy proxies in pool",
    )
    registry.register_gauge(
        "proxywhirl_pool_degraded_proxies",
        help_text="Number of degraded proxies in pool",
    )

    # Request metrics
    registry.register_counter(
        "proxywhirl_requests_total",
        help_text="Total number of requests processed",
    )
    registry.register_counter(
        "proxywhirl_requests_failed_total",
        help_text="Total number of failed requests",
    )
    registry.register_gauge(
        "proxywhirl_request_duration_ms",
        help_text="Request duration in milliseconds",
    )

    # Rotation metrics
    registry.register_counter(
        "proxywhirl_rotations_total",
        help_text="Total number of proxy rotations",
    )
    registry.register_gauge(
        "proxywhirl_current_proxy_index",
        help_text="Current proxy selection index",
    )

    # Error metrics
    registry.register_counter(
        "proxywhirl_errors_total",
        help_text="Total number of errors",
    )
    registry.register_gauge(
        "proxywhirl_circuit_breaker_state",
        help_text="Circuit breaker state (0=closed, 1=open, 2=half_open)",
    )

    logger.info("Registered default Prometheus metrics")
