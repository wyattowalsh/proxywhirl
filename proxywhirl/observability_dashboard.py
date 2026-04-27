"""Observability dashboard for metrics and monitoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from loguru import logger


class MetricType(str, Enum):
    """Metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertLevel(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class MetricPoint:
    """Single metric data point."""

    timestamp: datetime
    value: float
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Point dict
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "label": self.label,
        }


@dataclass
class TimeSeries:
    """Time series metric data."""

    name: str
    metric_type: MetricType
    points: list[MetricPoint] = field(default_factory=list)
    tags: dict[str, str] = field(default_factory=dict)
    unit: str = ""

    def add_point(self, value: float, label: str = "") -> None:
        """Add data point.

        Args:
            value: Metric value
            label: Optional label
        """
        point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            label=label,
        )
        self.points.append(point)

    def get_latest(self) -> float | None:
        """Get latest value.

        Returns:
            Latest value or None
        """
        if self.points:
            return self.points[-1].value
        return None

    def get_average(self, minutes: int = 5) -> float | None:
        """Get average over time period.

        Args:
            minutes: Time window in minutes

        Returns:
            Average value or None
        """
        if not self.points:
            return None

        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent = [p.value for p in self.points if p.timestamp >= cutoff]

        return sum(recent) / len(recent) if recent else None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Series dict
        """
        return {
            "name": self.name,
            "type": self.metric_type.value,
            "unit": self.unit,
            "tags": self.tags,
            "points": [p.to_dict() for p in self.points],
        }


@dataclass
class Alert:
    """Dashboard alert."""

    id: str
    message: str
    level: AlertLevel
    metric_name: str
    threshold: float
    current_value: float | None = None
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """Check if alert is active.

        Returns:
            True if active
        """
        return self.resolved_at is None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Alert dict
        """
        return {
            "id": self.id,
            "message": self.message,
            "level": self.level.value,
            "metric": self.metric_name,
            "threshold": self.threshold,
            "current_value": self.current_value,
            "triggered_at": self.triggered_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "is_active": self.is_active,
        }


class DashboardWidget:
    """Single dashboard widget."""

    def __init__(self, id: str, title: str, widget_type: str):
        """Initialize widget.

        Args:
            id: Widget ID
            title: Display title
            widget_type: Type (gauge, graph, number, etc.)
        """
        self.id = id
        self.title = title
        self.widget_type = widget_type
        self.metrics: list[str] = []
        self.refresh_interval = 30

    def add_metric(self, metric_name: str) -> None:
        """Add metric to widget.

        Args:
            metric_name: Metric name
        """
        self.metrics.append(metric_name)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Widget dict
        """
        return {
            "id": self.id,
            "title": self.title,
            "type": self.widget_type,
            "metrics": self.metrics,
            "refresh_interval": self.refresh_interval,
        }


class ObservabilityDashboard:
    """Observability dashboard manager."""

    def __init__(self, name: str):
        """Initialize dashboard.

        Args:
            name: Dashboard name
        """
        self.name = name
        self._metrics: dict[str, TimeSeries] = {}
        self._alerts: dict[str, Alert] = {}
        self._widgets: dict[str, DashboardWidget] = {}
        self._created_at = datetime.now()

    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        unit: str = "",
        tags: dict[str, str] | None = None,
    ) -> TimeSeries:
        """Register metric.

        Args:
            name: Metric name
            metric_type: Type
            unit: Unit
            tags: Optional tags

        Returns:
            TimeSeries object
        """
        series = TimeSeries(
            name=name,
            metric_type=metric_type,
            unit=unit,
            tags=tags or {},
        )
        self._metrics[name] = series
        logger.info(f"Registered metric: {name}")
        return series

    def record_metric(self, name: str, value: float, label: str = "") -> bool:
        """Record metric value.

        Args:
            name: Metric name
            value: Value
            label: Optional label

        Returns:
            True if recorded
        """
        if name not in self._metrics:
            return False

        self._metrics[name].add_point(value, label)
        return True

    def get_metric(self, name: str) -> TimeSeries | None:
        """Get metric.

        Args:
            name: Metric name

        Returns:
            TimeSeries or None
        """
        return self._metrics.get(name)

    def add_alert(self, alert: Alert) -> None:
        """Add alert.

        Args:
            alert: Alert
        """
        self._alerts[alert.id] = alert
        logger.warning(f"Alert triggered: {alert.message}")

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert.

        Args:
            alert_id: Alert ID

        Returns:
            True if resolved
        """
        if alert_id not in self._alerts:
            return False

        self._alerts[alert_id].resolved_at = datetime.now()
        logger.info(f"Alert resolved: {alert_id}")
        return True

    def create_widget(self, widget_id: str, title: str, widget_type: str) -> DashboardWidget:
        """Create widget.

        Args:
            widget_id: Widget ID
            title: Widget title
            widget_type: Widget type

        Returns:
            DashboardWidget
        """
        widget = DashboardWidget(widget_id, title, widget_type)
        self._widgets[widget_id] = widget
        logger.info(f"Created widget: {widget_id}")
        return widget

    def get_active_alerts(self) -> list[Alert]:
        """Get active alerts.

        Returns:
            List of active alerts
        """
        return [a for a in self._alerts.values() if a.is_active]

    def get_dashboard_data(self) -> dict[str, Any]:
        """Get full dashboard data.

        Returns:
            Dashboard data dict
        """
        return {
            "name": self.name,
            "created_at": self._created_at.isoformat(),
            "metrics": {name: series.to_dict() for name, series in self._metrics.items()},
            "alerts": {aid: alert.to_dict() for aid, alert in self._alerts.items()},
            "widgets": {wid: widget.to_dict() for wid, widget in self._widgets.items()},
            "summary": {
                "total_metrics": len(self._metrics),
                "total_alerts": len(self._alerts),
                "active_alerts": len(self.get_active_alerts()),
                "total_widgets": len(self._widgets),
            },
        }

    def get_stats(self) -> dict[str, int]:
        """Get dashboard stats.

        Returns:
            Stats dict
        """
        return {
            "metrics": len(self._metrics),
            "alerts": len(self._alerts),
            "active_alerts": len(self.get_active_alerts()),
            "widgets": len(self._widgets),
        }
