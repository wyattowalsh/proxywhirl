"""Table widgets for displaying proxy data."""

from __future__ import annotations

from typing import Any

from textual.binding import Binding
from textual.message import Message
from textual.widgets import DataTable

from ...models import Proxy


class ProxyDataTable(DataTable):
    """Enhanced DataTable with proxy-specific functionality."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("d", "delete_selected", "Delete Selected"),
        Binding("v", "validate_selected", "Validate Selected"),
        Binding("e", "export_selected", "Export Selected"),
    ]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.show_header = True
        self._setup_columns()

    def _setup_columns(self) -> None:
        """Setup table columns with proper formatting."""
        self.add_columns("Status", "IP", "Port", "Type", "Country", "Speed", "Last Check")

    def add_proxy_row(self, proxy: Any) -> None:
        """Add a proxy row with formatted data."""
        # Handle both dict and Proxy object
        if hasattr(proxy, "__dict__"):
            proxy_dict = proxy.__dict__ if hasattr(proxy, "__dict__") else proxy
        else:
            proxy_dict = proxy

        status = "🟢" if proxy_dict.get("is_valid") else "🔴"
        speed_ms = proxy_dict.get("response_time", 0)
        speed_display = f"{speed_ms:.0f}ms" if speed_ms else "N/A"

        self.add_row(
            status,
            str(proxy_dict.get("ip", "")),
            str(proxy_dict.get("port", "")),
            str(proxy_dict.get("type", "")).upper(),
            str(proxy_dict.get("country", "Unknown")),
            speed_display,
            str(proxy_dict.get("last_check", "Never")),
            key=str(proxy_dict.get("id", id(proxy))),
        )

    def get_selected_proxy_data(self) -> dict[str, Any] | None:
        """Get data for currently selected proxy."""
        if self.cursor_row >= 0:
            row_key = self.get_row_at(self.cursor_row)
            return {"row_key": row_key, "row_index": self.cursor_row}
        return None

    async def action_refresh(self) -> None:
        """Refresh table data."""
        self.post_message(ProxyDataTable.Refresh())

    async def action_delete_selected(self) -> None:
        """Delete selected proxy."""
        selected = self.get_selected_proxy_data()
        if selected:
            self.post_message(ProxyDataTable.DeleteProxy(selected))

    async def action_validate_selected(self) -> None:
        """Validate selected proxy."""
        selected = self.get_selected_proxy_data()
        if selected:
            self.post_message(ProxyDataTable.ValidateProxy(selected))

    async def action_export_selected(self) -> None:
        """Export selected proxies."""
        self.post_message(ProxyDataTable.ExportSelected())

    class Refresh(Message):
        """Refresh table message."""

    class DeleteProxy(Message):
        """Delete proxy message."""

        def __init__(self, proxy_data: dict[str, Any]) -> None:
            super().__init__()
            self.proxy_data = proxy_data

    class ValidateProxy(Message):
        """Validate proxy message."""

        def __init__(self, proxy_data: dict[str, Any]) -> None:
            super().__init__()
            self.proxy_data = proxy_data

    class ExportSelected(Message):
        """Export selected message."""


class ProxyTableWidget(DataTable):
    """Enhanced DataTable for displaying proxy information with rich formatting."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.show_header = True

    def setup_columns(self) -> None:
        """Setup table columns for proxy display."""
        self.add_columns(
            "🌐 Host",
            "🔌 Port",
            "🔗 Schemes",
            "🌍 Country",
            "🎭 Anonymity",
            "⚡ Response",
            "📶 Status",
            "🕒 Last Checked",
        )

    def add_proxy_row(self, proxy: Proxy) -> None:
        """Add a single proxy row to the table with rich formatting."""
        schemes_str = ",".join(
            s.value.lower() if hasattr(s, "value") else str(s).lower() for s in proxy.schemes
        )

        # Format response time with color coding
        if proxy.response_time:
            if proxy.response_time < 1.0:
                response_time = f"[green]{proxy.response_time:.3f}s[/green]"
            elif proxy.response_time < 3.0:
                response_time = f"[yellow]{proxy.response_time:.3f}s[/yellow]"
            else:
                response_time = f"[red]{proxy.response_time:.3f}s[/red]"
        else:
            response_time = "[dim]-[/dim]"

        last_checked = (
            proxy.last_checked.strftime("%H:%M:%S") if proxy.last_checked else "[dim]-[/dim]"
        )

        # Enhanced status with color and icons
        proxy_status = getattr(proxy, "status", "unknown")
        if proxy_status == "active":
            status = "[green]🟢 Active[/green]"
        elif proxy_status == "inactive":
            status = "[red]🔴 Inactive[/red]"
        else:
            status = "[yellow]🟡 Unknown[/yellow]"

        # Enhance country display
        country_display = (
            f"[bold]{proxy.country_code}[/bold]" if proxy.country_code else "[dim]-[/dim]"
        )

        # Enhance anonymity display
        anonymity_value = (
            proxy.anonymity.value if hasattr(proxy.anonymity, "value") else str(proxy.anonymity)
        )
        if anonymity_value.lower() in ["elite", "high"]:
            anonymity_display = f"[green]🛡️ {anonymity_value}[/green]"
        elif anonymity_value.lower() in ["anonymous", "medium"]:
            anonymity_display = f"[yellow]🔒 {anonymity_value}[/yellow]"
        else:
            anonymity_display = f"[red]👁️ {anonymity_value}[/red]"

        self.add_row(
            proxy.host,
            str(proxy.port),
            f"[blue]{schemes_str}[/blue]",
            country_display,
            anonymity_display,
            response_time,
            status,
            last_checked,
        )
