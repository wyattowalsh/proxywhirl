"""Comprehensive observability layer with spans, metrics, and logs.

Provides:
- Distributed tracing with span context
- Metrics collection (counters, histograms, gauges)
- Structured logging with correlation IDs
- OpenTelemetry integration
"""

from __future__ import annotations

import time
import traceback
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

from loguru import logger


class SpanKind(str, Enum):
    """OpenTelemetry span kinds."""

    INTERNAL = "INTERNAL"
    SERVER = "SERVER"
    CLIENT = "CLIENT"
    PRODUCER = "PRODUCER"
    CONSUMER = "CONSUMER"


class SpanStatus(str, Enum):
    """Span status."""

    UNSET = "UNSET"
    OK = "OK"
    ERROR = "ERROR"


@dataclass
class SpanContext:
    """Context for distributed tracing."""

    trace_id: str = field(default_factory=lambda: uuid4().hex)
    span_id: str = field(default_factory=lambda: uuid4().hex)
    parent_span_id: str | None = None
    baggage: dict[str, str] = field(default_factory=dict)

    def with_baggage(self, key: str, value: str) -> SpanContext:
        """Add baggage item."""
        self.baggage[key] = value
        return self


@dataclass
class Span:
    """Represents a trace span."""

    name: str
    context: SpanContext
    kind: SpanKind = SpanKind.INTERNAL
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    status: SpanStatus = SpanStatus.UNSET
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    error: Exception | None = None

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Add event to span."""
        self.events.append(
            {
                "name": name,
                "timestamp": time.time(),
                "attributes": attributes or {},
            }
        )

    def add_attribute(self, key: str, value: Any) -> None:
        """Add attribute to span."""
        self.attributes[key] = value

    def record_exception(self, exc: Exception) -> None:
        """Record exception in span."""
        self.error = exc
        self.status = SpanStatus.ERROR
        self.attributes["exception.type"] = type(exc).__name__
        self.attributes["exception.message"] = str(exc)
        self.attributes["exception.stacktrace"] = traceback.format_exc()

    def finish(self) -> None:
        """Mark span as finished."""
        self.end_time = time.time()
        if self.status == SpanStatus.UNSET:
            self.status = SpanStatus.OK

    @property
    def duration_ms(self) -> float:
        """Get span duration in milliseconds."""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000


class Tracer:
    """Distributed tracer."""

    def __init__(self) -> None:
        """Initialize tracer."""
        self._spans: list[Span] = []
        self._active_context: SpanContext | None = None

    @property
    def active_context(self) -> SpanContext:
        """Get active span context."""
        if self._active_context is None:
            self._active_context = SpanContext()
        return self._active_context

    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: dict[str, Any] | None = None,
    ) -> Span:
        """Start a new span.

        Args:
            name: Span name
            kind: Span kind
            attributes: Initial attributes

        Returns:
            New span
        """
        # Create child context
        parent_context = self.active_context
        context = SpanContext(
            trace_id=parent_context.trace_id,
            parent_span_id=parent_context.span_id,
        )
        context.baggage = parent_context.baggage.copy()

        span = Span(
            name=name,
            context=context,
            kind=kind,
            attributes=attributes or {},
        )

        return span

    def add_span(self, span: Span) -> None:
        """Record a completed span."""
        self._spans.append(span)
        logger.debug(
            "Span recorded",
            name=span.name,
            duration_ms=span.duration_ms,
            status=span.status.value,
            trace_id=span.context.trace_id,
        )

    def get_spans(self, trace_id: str | None = None) -> list[Span]:
        """Get recorded spans.

        Args:
            trace_id: Filter by trace ID (None = all)

        Returns:
            List of spans
        """
        if trace_id is None:
            return self._spans
        return [s for s in self._spans if s.context.trace_id == trace_id]

    def clear_spans(self) -> None:
        """Clear recorded spans."""
        self._spans.clear()

    @contextmanager
    def trace(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: dict[str, Any] | None = None,
    ) -> Iterator[Span]:
        """Context manager for tracing.

        Args:
            name: Span name
            kind: Span kind
            attributes: Initial attributes

        Yields:
            Span object
        """
        span = self.start_span(name, kind, attributes)
        old_context = self._active_context
        self._active_context = span.context

        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            raise
        finally:
            span.finish()
            self.add_span(span)
            self._active_context = old_context

    @asynccontextmanager
    async def atrace(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: dict[str, Any] | None = None,
    ) -> AsyncIterator[Span]:
        """Async context manager for tracing.

        Args:
            name: Span name
            kind: Span kind
            attributes: Initial attributes

        Yields:
            Span object
        """
        span = self.start_span(name, kind, attributes)
        old_context = self._active_context
        self._active_context = span.context

        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            raise
        finally:
            span.finish()
            self.add_span(span)
            self._active_context = old_context


class MetricType(str, Enum):
    """Metric types."""

    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"


@dataclass
class MetricPoint:
    """Individual metric data point."""

    timestamp: float = field(default_factory=time.time)
    value: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class Metric:
    """Metric with collected data points."""

    name: str
    type: MetricType
    description: str
    unit: str = ""
    points: list[MetricPoint] = field(default_factory=list)


class MetricsCollector:
    """Collects and aggregates metrics."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self._metrics: dict[str, Metric] = {}

    def counter(
        self,
        name: str,
        value: float = 1.0,
        description: str = "",
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record counter metric.

        Args:
            name: Metric name
            value: Increment value
            description: Metric description
            labels: Metric labels
        """
        if name not in self._metrics:
            self._metrics[name] = Metric(
                name=name,
                type=MetricType.COUNTER,
                description=description,
            )

        metric = self._metrics[name]
        point = MetricPoint(value=value, labels=labels or {})
        metric.points.append(point)

        logger.debug("Counter recorded", metric=name, value=value, labels=labels)

    def histogram(
        self,
        name: str,
        value: float,
        description: str = "",
        labels: dict[str, str] | None = None,
        unit: str = "",
    ) -> None:
        """Record histogram metric.

        Args:
            name: Metric name
            value: Observed value
            description: Metric description
            labels: Metric labels
            unit: Unit of measurement
        """
        if name not in self._metrics:
            self._metrics[name] = Metric(
                name=name,
                type=MetricType.HISTOGRAM,
                description=description,
                unit=unit,
            )

        metric = self._metrics[name]
        point = MetricPoint(value=value, labels=labels or {})
        metric.points.append(point)

    def gauge(
        self,
        name: str,
        value: float,
        description: str = "",
        labels: dict[str, str] | None = None,
        unit: str = "",
    ) -> None:
        """Record gauge metric.

        Args:
            name: Metric name
            value: Current value
            description: Metric description
            labels: Metric labels
            unit: Unit of measurement
        """
        if name not in self._metrics:
            self._metrics[name] = Metric(
                name=name,
                type=MetricType.GAUGE,
                description=description,
                unit=unit,
            )

        metric = self._metrics[name]
        # For gauges, replace last value with same labels
        existing = None
        for point in reversed(metric.points):
            if point.labels == (labels or {}):
                existing = point
                break

        if existing:
            existing.value = value
        else:
            point = MetricPoint(value=value, labels=labels or {})
            metric.points.append(point)

    def get_metric(self, name: str) -> Metric | None:
        """Get metric by name.

        Args:
            name: Metric name

        Returns:
            Metric or None
        """
        return self._metrics.get(name)

    def list_metrics(self) -> list[Metric]:
        """List all collected metrics.

        Returns:
            List of metrics
        """
        return list(self._metrics.values())

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format.

        Returns:
            Prometheus text format
        """
        lines = []

        for metric in self._metrics.values():
            lines.append(f"# HELP {metric.name} {metric.description}")
            lines.append(f"# TYPE {metric.name} {metric.type.value}")

            for point in metric.points:
                labels_str = ""
                if point.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in point.labels.items()]
                    labels_str = "{" + ",".join(label_pairs) + "}"

                lines.append(f"{metric.name}{labels_str} {point.value}")

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all metrics."""
        self._metrics.clear()


class ObservabilityContext:
    """Combined observability context (tracing + metrics)."""

    def __init__(self) -> None:
        """Initialize observability context."""
        self.tracer = Tracer()
        self.metrics = MetricsCollector()
        self.correlation_id = uuid4().hex

    def to_dict(self) -> dict[str, Any]:
        """Export context as dictionary.

        Returns:
            Context dictionary
        """
        return {
            "correlation_id": self.correlation_id,
            "active_trace_id": self.tracer.active_context.trace_id,
            "spans_recorded": len(self.tracer.get_spans()),
            "metrics_recorded": len(self.metrics.list_metrics()),
        }


# Global observability instance
_observability: ObservabilityContext | None = None


def get_observability() -> ObservabilityContext:
    """Get or create global observability context."""
    global _observability
    if _observability is None:
        _observability = ObservabilityContext()
    return _observability


def reset_observability() -> None:
    """Reset global observability context (for testing)."""
    global _observability
    _observability = None


__all__ = [
    "SpanKind",
    "SpanStatus",
    "SpanContext",
    "Span",
    "Tracer",
    "MetricType",
    "MetricPoint",
    "Metric",
    "MetricsCollector",
    "ObservabilityContext",
    "get_observability",
    "reset_observability",
]
