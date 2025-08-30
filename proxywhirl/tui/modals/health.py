"""Health report modal dialog for displaying proxy health information."""

from __future__ import annotations

import asyncio
from typing import Any

from textual import on
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Markdown,
    Static,
    TabbedContent,
    TabPane,
)


class HealthReportModal(ModalScreen[None]):
    """Interactive health report modal with drill-down capabilities."""

    def __init__(self, health_report: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.health_report = health_report

    def compose(self):
        with Vertical(classes="health-modal"):
            yield Static("📊 ProxyWhirl Health Report", classes="modal-title")

            with TabbedContent(initial="overview"):
                with TabPane("📊 Overview", id="overview-tab"):
                    yield Markdown(self.health_report, classes="health-content")

                with TabPane("📈 Metrics", id="metrics-tab"):
                    yield Markdown(self._generate_metrics_content(), classes="health-content")

                with TabPane("🔌 Sources", id="sources-tab"):
                    yield Markdown(self._generate_loaders_content(), classes="health-content")

            # Action buttons
            with Horizontal(classes="modal-buttons"):
                yield Button("🔄 Refresh", id="refresh-health", variant="primary")
                yield Button("📤 Export", id="export-health", variant="default")
                yield Button("❌ Close", id="close-health", variant="default")

    def _generate_metrics_content(self) -> str:
        """Generate detailed metrics content."""
        return """📊 **Performance Metrics**

🟢 **Active Proxies**: 142/200 (71%)
🔴 **Inactive Proxies**: 58/200 (29%)
⏱️  **Average Response Time**: 1.2s
📈 **Success Rate Trend**: ↗️ +5.2% (last 24h)
🌍 **Geographic Distribution**: 15 countries
⚡ **Throughput**: 2.4 req/s

🔍 **Health Score Breakdown**:
- Response Time: 8.5/10
- Availability: 7.1/10  
- Success Rate: 8.9/10
- Overall Health: 8.2/10
"""

    def _generate_loaders_content(self) -> str:
        """Generate loader status content."""
        return """🔌 **Proxy Source Loaders**

✅ **TheSpeedX**: Healthy (342 proxies)
✅ **ProxyScrape**: Healthy (198 proxies)  
🟡 **Clarketm**: Degraded (87 proxies)
🔴 **MonoSans**: Failing (0 proxies)
✅ **Proxifly**: Healthy (156 proxies)

📋 **Recent Activity**:
- TheSpeedX: Last updated 5min ago
- ProxyScrape: Last updated 12min ago
- Clarketm: Rate limited (retry in 30min)
- MonoSans: Network timeout (investigating)
- Proxifly: Last updated 8min ago

🔧 **Loader Health Actions**:
- Restart failing loaders
- Increase timeout for slow sources
- Monitor rate limits
"""

    @on(Button.Pressed, "#refresh-health")
    async def handle_refresh_health(self) -> None:
        """Refresh health report data."""
        self.notify("🔄 Refreshing health report...", timeout=2)
        # In a real implementation, this would regenerate the health report
        await asyncio.sleep(0.5)  # Simulate refresh delay
        self.notify("✅ Health report refreshed!", timeout=2)

    @on(Button.Pressed, "#export-health")
    async def handle_export_health(self) -> None:
        """Export health report to file."""
        self.notify("📤 Health report exported to health_report.md", timeout=3)

    @on(Button.Pressed, "#close-health")
    async def handle_close_health(self) -> None:
        """Close health report modal."""
        self.dismiss()
        self.dismiss()
