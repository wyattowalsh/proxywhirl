"""Monitoring and observability integration."""

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""

    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_logging: bool = True
    metrics_interval_seconds: int = 60
    trace_sample_rate: float = 0.1


class MonitoringIntegration:
    """Integrates monitoring components."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.start_time = datetime.now()
        self.metrics = {}

    def record_event(self, event_type: str, **attributes) -> None:
        """Record a monitoring event."""
        event = {"type": event_type, "timestamp": datetime.now().isoformat(), **attributes}

        if event_type not in self.metrics:
            self.metrics[event_type] = []

        self.metrics[event_type].append(event)

    def get_uptime_seconds(self) -> float:
        """Get service uptime."""
        return (datetime.now() - self.start_time).total_seconds()

    def get_metrics_summary(self) -> Dict:
        """Get monitoring metrics summary."""
        summary = {
            "uptime_seconds": self.get_uptime_seconds(),
            "events_count": sum(len(v) for v in self.metrics.values()),
            "event_types": list(self.metrics.keys()),
        }
        return summary

    def export_metrics(self) -> Dict:
        """Export metrics for external systems."""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_metrics_summary(),
            "events": self.metrics,
        }
