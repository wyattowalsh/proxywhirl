"""OpenTelemetry Jaeger tracing integration."""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime


try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False


@dataclass
class TraceConfig:
    """Jaeger tracing configuration."""
    agent_host: str = "localhost"
    agent_port: int = 6831
    service_name: str = "proxywhirl"
    sampler_rate: float = 1.0


class JaegerTracingManager:
    """Manages Jaeger tracing integration."""
    
    def __init__(self, config: TraceConfig):
        self.config = config
        self.tracer = None
        
        if TELEMETRY_AVAILABLE:
            self._init_tracer()
    
    def _init_tracer(self):
        """Initialize Jaeger tracer."""
        jaeger_exporter = JaegerExporter(
            agent_host_name=self.config.agent_host,
            agent_port=self.config.agent_port,
        )
        trace.set_tracer_provider(TracerProvider())
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        self.tracer = trace.get_tracer(__name__)
    
    def start_span(self, name: str, **attributes):
        """Start a new tracing span."""
        if not self.tracer:
            return None
        
        span = self.tracer.start_span(name)
        for key, value in attributes.items():
            span.set_attribute(key, value)
        return span
    
    def record_proxy_request(self, proxy_url: str, status_code: int, latency_ms: float):
        """Record a proxy request span."""
        if not self.tracer:
            return
        
        with self.tracer.start_as_current_span("proxy_request") as span:
            span.set_attribute("proxy_url", proxy_url)
            span.set_attribute("status_code", status_code)
            span.set_attribute("latency_ms", latency_ms)

