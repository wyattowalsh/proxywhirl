"""Web-based monitoring dashboard for ProxyWhirl.

Provides real-time monitoring and metrics visualization
through a web-based dashboard.
"""

from __future__ import annotations

from typing import Any

from loguru import logger


class DashboardWidget:
    """Represents a dashboard widget."""

    def __init__(self, widget_id: str, widget_type: str, title: str) -> None:
        """Initialize dashboard widget.

        Args:
            widget_id: Widget identifier
            widget_type: Type of widget
            title: Widget title
        """
        self.widget_id = widget_id
        self.widget_type = widget_type
        self.title = title
        self.data: dict[str, Any] = {}
        logger.debug(f"Widget created: {widget_id} ({widget_type})")

    def update_data(self, data: dict[str, Any]) -> None:
        """Update widget data.

        Args:
            data: Widget data
        """
        self.data = data

    def to_json(self) -> dict[str, Any]:
        """Convert widget to JSON.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.widget_id,
            "type": self.widget_type,
            "title": self.title,
            "data": self.data,
        }


class DashboardManager:
    """Manages web dashboard."""

    def __init__(self) -> None:
        """Initialize dashboard manager."""
        self._widgets: dict[str, DashboardWidget] = {}
        logger.debug("DashboardManager initialized")

    def add_widget(self, widget_id: str, widget_type: str, title: str) -> bool:
        """Add widget to dashboard.

        Args:
            widget_id: Widget ID
            widget_type: Widget type
            title: Widget title

        Returns:
            True if added
        """
        if widget_id in self._widgets:
            logger.warning(f"Widget already exists: {widget_id}")
            return False

        widget = DashboardWidget(widget_id, widget_type, title)
        self._widgets[widget_id] = widget
        logger.info(f"Widget added: {widget_id}")
        return True

    def update_widget(self, widget_id: str, data: dict[str, Any]) -> bool:
        """Update widget data.

        Args:
            widget_id: Widget ID
            data: Widget data

        Returns:
            True if updated
        """
        if widget_id not in self._widgets:
            logger.error(f"Widget not found: {widget_id}")
            return False

        self._widgets[widget_id].update_data(data)
        logger.debug(f"Widget updated: {widget_id}")
        return True

    def remove_widget(self, widget_id: str) -> bool:
        """Remove widget from dashboard.

        Args:
            widget_id: Widget ID

        Returns:
            True if removed
        """
        if widget_id in self._widgets:
            del self._widgets[widget_id]
            logger.info(f"Widget removed: {widget_id}")
            return True

        return False

    def get_dashboard_html(self) -> str:
        """Get dashboard HTML.

        Returns:
            Dashboard HTML
        """
        widgets_json = (
            "[" + ",".join(str(w.to_json()).replace("'", '"') for w in self._widgets.values()) + "]"
        )

        return f"""<!DOCTYPE html>
<html>
<head>
    <title>ProxyWhirl Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .widget {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; }}
        .widget-title {{ font-weight: bold; }}
    </style>
</head>
<body>
    <h1>ProxyWhirl Monitoring Dashboard</h1>
    <div id="dashboard">
        <!-- Widgets will be rendered here -->
    </div>
    <script>
        const widgets = {widgets_json};
        const dashboard = document.getElementById('dashboard');
        widgets.forEach(w => {{
            const div = document.createElement('div');
            div.className = 'widget';
            div.innerHTML = `<div class="widget-title">${{w.title}}</div><pre>${{JSON.stringify(w.data, null, 2)}}</pre>`;
            dashboard.appendChild(div);
        }});
    </script>
</body>
</html>"""

    def export_metrics(self) -> dict[str, Any]:
        """Export dashboard metrics.

        Returns:
            Dictionary of metrics
        """
        return {
            "total_widgets": len(self._widgets),
            "widgets": {
                wid: {"type": w.widget_type, "title": w.title} for wid, w in self._widgets.items()
            },
        }
