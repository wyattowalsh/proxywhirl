"""Tests for observability layer."""

from __future__ import annotations

import pytest

from proxywhirl.observability import (
    MetricsCollector,
    MetricType,
    ObservabilityContext,
    Span,
    SpanKind,
    SpanStatus,
    Tracer,
)


def test_span_context_creation() -> None:
    """Test creating span context."""
    from proxywhirl.observability import SpanContext

    context = SpanContext()
    assert context.trace_id
    assert context.span_id
    assert context.parent_span_id is None
    assert context.baggage == {}


def test_span_context_baggage() -> None:
    """Test baggage in span context."""
    from proxywhirl.observability import SpanContext

    context = SpanContext()
    context = context.with_baggage("user_id", "123")
    assert context.baggage["user_id"] == "123"


def test_span_creation() -> None:
    """Test creating span."""
    from proxywhirl.observability import SpanContext

    context = SpanContext()
    span = Span(name="test", context=context)

    assert span.name == "test"
    assert span.status == SpanStatus.UNSET
    assert span.duration_ms == 0.0


def test_span_add_event() -> None:
    """Test adding event to span."""
    from proxywhirl.observability import SpanContext

    context = SpanContext()
    span = Span(name="test", context=context)

    span.add_event("event1", {"key": "value"})
    assert len(span.events) == 1
    assert span.events[0]["name"] == "event1"


def test_span_add_attribute() -> None:
    """Test adding attribute to span."""
    from proxywhirl.observability import SpanContext

    context = SpanContext()
    span = Span(name="test", context=context)

    span.add_attribute("key1", "value1")
    assert span.attributes["key1"] == "value1"


def test_span_finish() -> None:
    """Test finishing span."""
    from proxywhirl.observability import SpanContext

    context = SpanContext()
    span = Span(name="test", context=context)

    assert span.end_time is None
    span.finish()
    assert span.end_time is not None
    assert span.status == SpanStatus.OK


def test_span_exception_recording() -> None:
    """Test recording exception in span."""
    from proxywhirl.observability import SpanContext

    context = SpanContext()
    span = Span(name="test", context=context)

    exc = ValueError("test error")
    span.record_exception(exc)

    assert span.status == SpanStatus.ERROR
    assert span.attributes["exception.type"] == "ValueError"
    assert "test error" in span.attributes["exception.message"]


def test_tracer_start_span() -> None:
    """Test starting span with tracer."""
    tracer = Tracer()

    span = tracer.start_span("test", kind=SpanKind.CLIENT)
    assert span.name == "test"
    assert span.kind == SpanKind.CLIENT


def test_tracer_span_recording() -> None:
    """Test recording spans."""
    tracer = Tracer()

    span = tracer.start_span("test")
    span.finish()
    tracer.add_span(span)

    assert len(tracer.get_spans()) == 1


def test_tracer_context_manager() -> None:
    """Test tracer context manager."""
    tracer = Tracer()

    with tracer.trace("operation"):
        assert len(tracer.get_spans()) == 0

    assert len(tracer.get_spans()) == 1
    span = tracer.get_spans()[0]
    assert span.name == "operation"
    assert span.status == SpanStatus.OK


def test_tracer_context_manager_with_error() -> None:
    """Test tracer context manager with exception."""
    tracer = Tracer()

    with pytest.raises(ValueError):
        with tracer.trace("operation"):
            raise ValueError("test error")

    assert len(tracer.get_spans()) == 1
    span = tracer.get_spans()[0]
    assert span.status == SpanStatus.ERROR


@pytest.mark.asyncio
async def test_tracer_async_context_manager() -> None:
    """Test async tracer context manager."""
    tracer = Tracer()

    async with tracer.atrace("async_op"):
        assert len(tracer.get_spans()) == 0

    assert len(tracer.get_spans()) == 1
    span = tracer.get_spans()[0]
    assert span.name == "async_op"


def test_metrics_counter() -> None:
    """Test counter metric."""
    metrics = MetricsCollector()

    metrics.counter("requests", 1.0, description="Request count")
    assert "requests" in metrics._metrics

    metric = metrics.get_metric("requests")
    assert metric.type == MetricType.COUNTER
    assert len(metric.points) == 1


def test_metrics_histogram() -> None:
    """Test histogram metric."""
    metrics = MetricsCollector()

    metrics.histogram(
        "latency",
        150.5,
        description="Request latency",
        unit="ms",
    )

    metric = metrics.get_metric("latency")
    assert metric.type == MetricType.HISTOGRAM
    assert metric.unit == "ms"


def test_metrics_gauge() -> None:
    """Test gauge metric."""
    metrics = MetricsCollector()

    metrics.gauge("pool_size", 10.0, description="Pool size")
    metrics.gauge("pool_size", 15.0, description="Pool size")

    metric = metrics.get_metric("pool_size")
    assert metric.type == MetricType.GAUGE
    assert len(metric.points) == 1
    assert metric.points[0].value == 15.0


def test_metrics_with_labels() -> None:
    """Test metrics with labels."""
    metrics = MetricsCollector()

    metrics.counter(
        "requests",
        1.0,
        labels={"method": "GET", "status": "200"},
    )
    metrics.counter(
        "requests",
        1.0,
        labels={"method": "POST", "status": "201"},
    )

    metric = metrics.get_metric("requests")
    assert len(metric.points) == 2


def test_metrics_list() -> None:
    """Test listing metrics."""
    metrics = MetricsCollector()

    metrics.counter("requests", 1.0)
    metrics.histogram("latency", 100.0)
    metrics.gauge("pool_size", 10.0)

    assert len(metrics.list_metrics()) == 3


def test_metrics_prometheus_export() -> None:
    """Test Prometheus export format."""
    metrics = MetricsCollector()

    metrics.counter("requests", 5.0, description="Request count")
    metrics.gauge("pool_size", 10.0, description="Pool size")

    prometheus = metrics.export_prometheus()
    assert "# HELP requests Request count" in prometheus
    assert "# TYPE requests counter" in prometheus
    assert "requests 5.0" in prometheus
    assert "pool_size 10.0" in prometheus


def test_observability_context() -> None:
    """Test combined observability context."""
    ctx = ObservabilityContext()

    assert ctx.tracer is not None
    assert ctx.metrics is not None
    assert ctx.correlation_id is not None


def test_observability_context_to_dict() -> None:
    """Test exporting observability context."""
    ctx = ObservabilityContext()

    ctx.metrics.counter("test", 1.0)
    span = ctx.tracer.start_span("test")
    span.finish()
    ctx.tracer.add_span(span)

    data = ctx.to_dict()
    assert "correlation_id" in data
    assert "active_trace_id" in data
    assert data["spans_recorded"] == 1
    assert data["metrics_recorded"] == 1


def test_tracer_span_hierarchy() -> None:
    """Test parent-child span relationships."""
    tracer = Tracer()

    with tracer.trace("parent"):
        parent_context = tracer.active_context
        child_span = tracer.start_span("child")

        assert child_span.context.parent_span_id == parent_context.span_id
        assert child_span.context.trace_id == parent_context.trace_id


def test_metrics_clear() -> None:
    """Test clearing metrics."""
    metrics = MetricsCollector()

    metrics.counter("test", 1.0)
    assert len(metrics.list_metrics()) == 1

    metrics.clear()
    assert len(metrics.list_metrics()) == 0
