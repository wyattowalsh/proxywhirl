"""OpenTelemetry metrics export."""

from typing import Optional
from dataclasses import dataclass


try:
    from opentelemetry import metrics
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.sdk.metrics import MeterProvider

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False


@dataclass
class MetricsConfig:
    """OpenTelemetry metrics configuration."""

    service_name: str = "proxywhirl"
    enable_prometheus: bool = True
    prometheus_port: int = 8000


class OpenTelemetryMetrics:
    """OpenTelemetry metrics collection."""

    def __init__(self, config: MetricsConfig):
        self.config = config
        self.meter = None
        self.counters = {}
        self.histograms = {}

        if METRICS_AVAILABLE:
            self._init_metrics()

    def _init_metrics(self):
        """Initialize OpenTelemetry metrics."""
        if self.config.enable_prometheus:
            reader = PrometheusMetricReader()
            provider = MeterProvider(metric_readers=[reader])
            metrics.set_meter_provider(provider)

        self.meter = metrics.get_meter(__name__)

    def create_counter(self, name: str, description: str) -> None:
        """Create a counter metric."""
        if not self.meter:
            return
        self.counters[name] = self.meter.create_counter(name, description=description)

    def create_histogram(self, name: str, description: str, unit: str = "ms") -> None:
        """Create a histogram metric."""
        if not self.meter:
            return
        self.histograms[name] = self.meter.create_histogram(
            name, description=description, unit=unit
        )

    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter."""
        if name in self.counters:
            self.counters[name].add(value)

    def record_histogram(self, name: str, value: float) -> None:
        """Record a histogram value."""
        if name in self.histograms:
            self.histograms[name].record(value)
