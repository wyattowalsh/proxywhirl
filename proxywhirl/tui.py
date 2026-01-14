"""
Terminal User Interface (TUI) for ProxyWhirl.

Full-featured TUI with proxy sourcing, validation, analytics, health monitoring,
exports, and configuration management.

## Features

- **Overview Tab**: Real-time metrics dashboard and proxy table with color-coded health status
- **Fetch & Validate**: Auto-fetch from 64+ proxy sources with batch validation
- **Export**: Save proxy lists in CSV, JSON, YAML, or plain text formats
- **Test**: Send HTTP requests (GET/POST/PUT/DELETE/HEAD/PATCH/OPTIONS) through proxies
- **Analytics**: Statistics by protocol, country, and source
- **Health Tab**: Circuit breaker status and health check controls

## Usage

Launch via CLI:
    $ proxywhirl tui

Or programmatically:
    >>> from proxywhirl import ProxyRotator, run_tui
    >>> rotator = ProxyRotator()
    >>> run_tui(rotator=rotator)

## Keyboard Shortcuts

- Ctrl+C: Quit
- Ctrl+R: Refresh all data
- Ctrl+F: Go to Fetch & Validate tab
- Ctrl+E: Go to Export tab
- Ctrl+T: Go to Test tab
- Delete: Delete selected proxy
- Enter: View proxy details
- F1: Show help

## Architecture

The TUI uses Textual framework with the following components:
- MetricsPanel: Reactive metrics display
- RetryMetricsPanel: Retry statistics display
- ProxyTable: DataTable with health status indicators, filtering, and sorting
- FilterPanel: Search and filter controls
- SourceFetcherPanel: Multi-source proxy fetching
- ExportPanel: Multi-format export functionality
- StrategyPanel: Rotation strategy management
- RequestTesterPanel: HTTP request testing with custom headers/body
- AnalyticsPanel: Statistics and insights
- ProxyControlPanel: Manual proxy management
- HealthCheckPanel: Batch health checking with progress
- CircuitBreakerPanel: Circuit breaker status display
- ProxyDetailsScreen: Modal for detailed proxy information
- ConfirmDeleteScreen: Deletion confirmation dialog
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen, ScreenResultType
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    Select,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)

from proxywhirl.exceptions import ProxyFetchError
from proxywhirl.fetchers import ProxyFetcher, ProxyValidator
from proxywhirl.models import HealthStatus, Proxy
from proxywhirl.rotator import ProxyRotator
from proxywhirl.sources import (
    ALL_HTTP_SOURCES,
    ALL_SOCKS4_SOURCES,
    ALL_SOCKS5_SOURCES,
    ALL_SOURCES,
    RECOMMENDED_SOURCES,
)
from proxywhirl.strategies import (
    GeoTargetedStrategy,
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    RandomStrategy,
    RoundRobinStrategy,
    SessionPersistenceStrategy,
    WeightedStrategy,
)
from proxywhirl.utils import validate_target_url_safe


class MetricsPanel(Static):
    """Display real-time metrics with sparkline visualization."""

    total_proxies = reactive(0)
    active_proxies = reactive(0)
    healthy_proxies = reactive(0)
    degraded_proxies = reactive(0)
    unhealthy_proxies = reactive(0)
    total_requests = reactive(0)
    success_rate = reactive(0.0)
    avg_latency = reactive(0.0)
    prev_latency = reactive(0.0)  # For trend indicator
    prev_success_rate = reactive(0.0)  # For trend indicator

    # History for sparklines
    _latency_history: list[float] = []
    _success_history: list[float] = []

    def _sparkline(self, values: list[float], width: int = 10) -> str:
        """Generate a simple ASCII sparkline."""
        if not values:
            return "─" * width
        # Sparkline characters: ▁▂▃▄▅▆▇█
        chars = "▁▂▃▄▅▆▇█"
        min_val = min(values) if values else 0
        max_val = max(values) if values else 1
        range_val = max_val - min_val if max_val > min_val else 1

        # Take last 'width' values
        recent = values[-width:]
        result = ""
        for v in recent:
            idx = int((v - min_val) / range_val * (len(chars) - 1))
            idx = max(0, min(len(chars) - 1, idx))
            result += chars[idx]
        # Pad if needed
        return result.ljust(width, "─")

    def _trend_indicator(self, current: float, previous: float) -> tuple[str, str]:
        """Get trend indicator arrow and style."""
        diff = current - previous
        if abs(diff) < 0.5:
            return "→", "dim"
        elif diff > 0:
            return "↑", "green" if current > previous else "red"
        else:
            return "↓", "red" if current < previous else "green"

    def render(self) -> Text:
        """Render metrics display with sparklines and trends."""
        text = Text()
        text.append("📊 Metrics\n", style="bold cyan")
        text.append("─" * 40 + "\n", style="dim")

        # Proxy counts with visual bar
        text.append("Proxies: ", style="white")
        text.append(f"{self.total_proxies} total", style="bold")
        text.append(f" | {self.active_proxies} active\n", style="green")

        # Health status bar
        if self.total_proxies > 0:
            bar_width = 30
            h_width = int(self.healthy_proxies / self.total_proxies * bar_width)
            d_width = int(self.degraded_proxies / self.total_proxies * bar_width)
            u_width = bar_width - h_width - d_width
            text.append("  [", style="dim")
            text.append("█" * h_width, style="green")
            text.append("█" * d_width, style="yellow")
            text.append("█" * u_width, style="red")
            text.append("] ", style="dim")
            text.append(f"{self.healthy_proxies}✓ ", style="green")
            text.append(f"{self.degraded_proxies}⚠ ", style="yellow")
            text.append(f"{self.unhealthy_proxies}✗\n", style="red")

        text.append("\nRequests: ", style="white")
        text.append(f"{self.total_requests:,}\n", style="bold")

        # Success rate with trend
        text.append("Success Rate: ", style="white")
        rate_style = "bold green" if self.success_rate > 80 else "bold yellow"
        text.append(f"{self.success_rate:.1f}%", style=rate_style)

        trend_arrow, trend_style = self._trend_indicator(self.success_rate, self.prev_success_rate)
        text.append(f" {trend_arrow} ", style=trend_style)

        # Sparkline for success rate
        text.append(self._sparkline(self._success_history), style="cyan")
        text.append("\n")

        # Latency with trend
        text.append("Avg Latency: ", style="white")
        latency_style = (
            "green" if self.avg_latency < 500 else "yellow" if self.avg_latency < 2000 else "red"
        )
        text.append(f"{self.avg_latency:.0f}ms", style=f"bold {latency_style}")

        # For latency, up is bad (inverted trend)
        trend_arrow, _ = self._trend_indicator(self.avg_latency, self.prev_latency)
        trend_style = "red" if trend_arrow == "↑" else "green" if trend_arrow == "↓" else "dim"
        text.append(f" {trend_arrow} ", style=trend_style)

        # Sparkline for latency
        text.append(self._sparkline(self._latency_history), style="cyan")
        text.append("\n")

        return text

    def update_history(self, latency: float, success_rate: float) -> None:
        """Update metric history for sparklines."""
        self._latency_history.append(latency)
        self._success_history.append(success_rate)
        # Keep last 20 values
        if len(self._latency_history) > 20:
            self._latency_history = self._latency_history[-20:]
        if len(self._success_history) > 20:
            self._success_history = self._success_history[-20:]


class ProxyTable(DataTable):
    """DataTable widget for displaying proxies with row selection and sorting."""

    # Store proxy references for selection
    _proxy_map: dict[str, Proxy]

    # Sorting state
    sort_column: str | None = None
    sort_ascending: bool = True

    # Filter state
    filter_text: str = ""
    filter_protocol: str = "all"
    filter_health: str = "all"
    filter_country: str = "all"
    filter_favorites_only: bool = False

    # Favorites tracking
    _favorites: set[str]

    def __init__(self, *args, **kwargs) -> None:
        """Initialize with row cursor for selection."""
        super().__init__(*args, cursor_type="row", **kwargs)
        self._proxy_map = {}
        self._favorites = set()

    def on_mount(self) -> None:
        """Set up table columns."""
        self.add_column("★", width=3, key="favorite")
        self.add_column("URL", width=38, key="url")
        self.add_column("Protocol", width=10, key="protocol")
        self.add_column("Health", width=12, key="health")
        self.add_column("Latency", width=14, key="latency")
        self.add_column("Success", width=8, key="success")
        self.add_column("Failures", width=8, key="failures")
        self.add_column("Country", width=8, key="country")

    def get_selected_proxy(self) -> Proxy | None:
        """Get the currently selected proxy."""
        if self.cursor_row is not None and self.row_count > 0:
            try:
                row_key = self.get_row_at(self.cursor_row)
                if row_key and str(row_key.value) in self._proxy_map:
                    return self._proxy_map[str(row_key.value)]
            except Exception:
                pass
        return None

    def update_proxies(
        self,
        proxies: list[Proxy],
        filter_text: str = "",
        filter_protocol: str = "all",
        filter_health: str = "all",
        filter_country: str = "all",
        filter_favorites_only: bool = False,
    ) -> None:
        """Update table with proxy data, applying filters and sorting."""
        self.clear()
        self._proxy_map.clear()

        # Store filter state
        self.filter_text = filter_text
        self.filter_protocol = filter_protocol
        self.filter_health = filter_health
        self.filter_country = filter_country
        self.filter_favorites_only = filter_favorites_only

        # Apply filters
        filtered = self._filter_proxies(proxies)

        # Apply sorting
        sorted_proxies = self._sort_proxies(filtered)

        for proxy in sorted_proxies:
            # Store proxy reference using URL as key
            proxy_key = str(proxy.url)
            self._proxy_map[proxy_key] = proxy

            # Color-code protocol
            protocol = str(proxy.protocol or "http")
            protocol_text = Text(protocol.upper())
            protocol_colors = {
                "http": "cyan",
                "https": "green",
                "socks4": "magenta",
                "socks5": "blue",
            }
            protocol_text.stylize(f"bold {protocol_colors.get(protocol, 'white')}")

            # Color-code health status
            health_text = Text(proxy.health_status.value.upper())
            if proxy.health_status == HealthStatus.HEALTHY:
                health_text.stylize("bold green")
            elif proxy.health_status == HealthStatus.DEGRADED:
                health_text.stylize("bold yellow")
            elif proxy.health_status == HealthStatus.UNHEALTHY:
                health_text.stylize("bold orange1")
            elif proxy.health_status == HealthStatus.DEAD:
                health_text.stylize("bold red")
            else:
                health_text.stylize("dim")

            # Format latency with signal bars
            latency_ms = proxy.average_response_time_ms or 0
            if latency_ms == 0:
                signal = "░░░░"
                signal_style = "dim"
            elif latency_ms < 200:
                signal = "████"
                signal_style = "bold green"
            elif latency_ms < 500:
                signal = "███░"
                signal_style = "green"
            elif latency_ms < 1000:
                signal = "██░░"
                signal_style = "yellow"
            elif latency_ms < 2000:
                signal = "█░░░"
                signal_style = "orange1"
            else:
                signal = "▒░░░"
                signal_style = "red"

            latency_text = Text(f"{signal} {latency_ms:.0f}ms")
            latency_text.stylize(signal_style)

            # Format success/failure counts with color
            successes_text = Text(str(proxy.total_successes))
            failures_text = Text(str(proxy.total_failures))
            if proxy.total_successes > 0:
                successes_text.stylize("green")
            if proxy.total_failures > 0:
                failures_text.stylize("red")

            # Favorite indicator
            is_favorite = proxy_key in self._favorites
            fav_text = Text("★" if is_favorite else "☆")
            fav_text.stylize("bold yellow" if is_favorite else "dim")

            self.add_row(
                fav_text,
                str(proxy.url),
                protocol_text,
                health_text,
                latency_text,
                successes_text,
                failures_text,
                str(proxy.country_code or "N/A"),
                key=proxy_key,
            )

    def toggle_favorite(self, proxy_url: str) -> bool:
        """Toggle favorite status for a proxy. Returns new favorite state."""
        if proxy_url in self._favorites:
            self._favorites.discard(proxy_url)
            return False
        else:
            self._favorites.add(proxy_url)
            return True

    def _filter_proxies(self, proxies: list[Proxy]) -> list[Proxy]:
        """Apply filters to proxy list."""
        result = proxies

        # Text filter (URL search)
        if self.filter_text:
            search = self.filter_text.lower()
            result = [p for p in result if search in str(p.url).lower()]

        # Protocol filter
        if self.filter_protocol != "all":
            result = [p for p in result if (p.protocol or "http") == self.filter_protocol]

        # Health filter
        if self.filter_health != "all":
            result = [p for p in result if p.health_status.value == self.filter_health]

        # Country filter
        if self.filter_country != "all":
            result = [p for p in result if (p.country_code or "N/A") == self.filter_country]

        # Favorites filter
        if self.filter_favorites_only:
            result = [p for p in result if str(p.url) in self._favorites]

        return result

    def _sort_proxies(self, proxies: list[Proxy]) -> list[Proxy]:
        """Sort proxies by current sort column."""
        if not self.sort_column:
            # Default: favorites first, then by health
            return sorted(
                proxies,
                key=lambda p: (0 if str(p.url) in self._favorites else 1, p.health_status.value),
            )

        # Define sort key functions
        sort_keys = {
            "favorite": lambda p: 0 if str(p.url) in self._favorites else 1,
            "url": lambda p: str(p.url).lower(),
            "protocol": lambda p: (p.protocol or "http").lower(),
            "health": lambda p: p.health_status.value,
            "latency": lambda p: p.average_response_time_ms or 0,
            "success": lambda p: p.total_successes,
            "failures": lambda p: p.total_failures,
            "country": lambda p: (p.country_code or "ZZZ").lower(),
        }

        key_fn = sort_keys.get(self.sort_column)
        if key_fn:
            return sorted(proxies, key=key_fn, reverse=not self.sort_ascending)
        return proxies

    def set_sort(self, column: str) -> None:
        """Set sort column, toggling direction if same column."""
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True


class SourceFetcherPanel(Static):
    """Panel for fetching proxies from sources."""

    def compose(self) -> ComposeResult:
        """Create source fetcher UI."""
        with Vertical(id="fetch-container"):
            yield Label("🌐 Fetch Proxies from Sources", classes="panel-title")

            yield Select(
                [
                    ("All Sources (64+)", "all"),
                    ("Recommended Only", "recommended"),
                    ("HTTP Sources", "http"),
                    ("SOCKS4 Sources", "socks4"),
                    ("SOCKS5 Sources", "socks5"),
                ],
                id="source-select",
                prompt="Select proxy sources",
            )

            with Horizontal(classes="button-row"):
                yield Button("Fetch Proxies", id="fetch-btn", variant="primary")
                yield Button("Validate All", id="validate-all-btn", variant="success")

            yield Label("", id="fetch-status")


class ExportPanel(Static):
    """Panel for exporting proxy lists."""

    def compose(self) -> ComposeResult:
        """Create export UI."""
        with Vertical(id="export-container"):
            yield Label("💾 Export Proxy List", classes="panel-title")

            yield Input(
                placeholder="Export file path (e.g., proxies.csv)",
                id="export-path",
            )

            yield Select(
                [
                    ("CSV Format", "csv"),
                    ("JSON Format", "json"),
                    ("Text Format (one per line)", "text"),
                    ("YAML Format", "yaml"),
                ],
                id="export-format",
                prompt="Select export format",
            )

            with Horizontal(classes="button-row"):
                yield Button("Preview", id="preview-export-btn", variant="default")
                yield Button("Export All", id="export-all-btn", variant="primary")
                yield Button("Healthy Only", id="export-healthy-btn", variant="success")

            yield Label("", id="export-status")


class StrategyPanel(Static):
    """Panel for managing rotation strategies."""

    def compose(self) -> ComposeResult:
        """Create strategy management UI."""
        with Vertical(id="strategy-container"):
            yield Label("🎯 Rotation Strategy", classes="panel-title")

            yield Select(
                [
                    ("Round Robin", "round-robin"),
                    ("Random", "random"),
                    ("Weighted", "weighted"),
                    ("Least Used", "least-used"),
                    ("Performance Based", "performance"),
                    ("Geo Targeted", "geo"),
                    ("Session Persistence", "session"),
                ],
                id="strategy-select",
                prompt="Select rotation strategy",
            )

            yield Button("Apply Strategy", id="apply-strategy-btn", variant="primary")
            yield Label("", id="strategy-status")


class RequestTesterPanel(Static):
    """Panel for testing proxy requests."""

    def compose(self) -> ComposeResult:
        """Create request tester UI."""
        with Vertical(id="request-container"):
            yield Label("🚀 Test Proxy Request", classes="panel-title")

            yield Input(
                placeholder="URL to test (e.g., https://httpbin.org/ip)",
                id="test-url",
                value="https://httpbin.org/ip",
            )

            with Horizontal(classes="button-row"):
                yield Select(
                    [
                        ("GET", "GET"),
                        ("POST", "POST"),
                        ("PUT", "PUT"),
                        ("DELETE", "DELETE"),
                        ("HEAD", "HEAD"),
                        ("PATCH", "PATCH"),
                        ("OPTIONS", "OPTIONS"),
                    ],
                    id="test-method",
                    value="GET",
                )

                yield Input(
                    placeholder='Headers (JSON: {"Auth": "Bearer token"})',
                    id="test-headers",
                )

            yield Label("Request Body (for POST/PUT/PATCH):", classes="input-label")
            yield TextArea(id="test-body", language="json")

            yield Button("Send Request", id="send-request-btn", variant="primary")

            with VerticalScroll(id="response-scroll"):
                yield Static("", id="response-output")


class AnalyticsPanel(Static):
    """Panel for analytics and statistics."""

    def compose(self) -> ComposeResult:
        """Create analytics UI."""
        with Vertical(id="analytics-container"):
            yield Label("📈 Analytics & Statistics", classes="panel-title")

            yield Static("", id="analytics-content")

            yield Button("Refresh Analytics", id="refresh-analytics-btn", variant="primary")


class ProxyControlPanel(Static):
    """Panel for manually adding and removing proxies."""

    def compose(self) -> ComposeResult:
        """Create proxy control UI."""
        with Vertical(id="control-container"):
            yield Label("🎛️ Proxy Management", classes="panel-title")

            yield Input(
                placeholder="Proxy URL or paste multiple (one per line)",
                id="add-proxy-url",
            )

            with Horizontal(classes="button-row"):
                yield Input(
                    placeholder="Username (optional)",
                    id="add-proxy-username",
                    password=False,
                )
                yield Input(
                    placeholder="Password (optional)",
                    id="add-proxy-password",
                    password=True,
                )

            with Horizontal(classes="button-row"):
                yield Button("Add Proxy", id="add-proxy-btn", variant="primary")
                yield Button("Remove Selected", id="remove-proxy-btn", variant="error")

            with Horizontal(classes="button-row"):
                yield Button("Clear All", id="clear-all-btn", variant="warning")
                yield Button("Test All", id="test-all-btn", variant="success")

            yield Label("", id="control-status")


class StatusBar(Static):
    """Status bar showing current app state and quick stats."""

    proxy_count = reactive(0)
    healthy_count = reactive(0)
    auto_refresh = reactive(True)
    current_strategy = reactive("round-robin")
    last_action = reactive("")

    def render(self) -> Text:
        """Render status bar."""
        text = Text()

        # Auto-refresh indicator
        if self.auto_refresh:
            text.append(" 🔄 ", style="green")
        else:
            text.append(" ⏸️ ", style="yellow")

        # Quick stats
        text.append(f" {self.proxy_count} proxies ", style="bold white")
        text.append("|", style="dim")
        text.append(f" {self.healthy_count}✓ ", style="green")
        text.append("|", style="dim")
        text.append(f" {self.current_strategy} ", style="cyan")
        text.append("|", style="dim")

        # Last action (if any)
        if self.last_action:
            text.append(f" {self.last_action} ", style="yellow")
            text.append("|", style="dim")

        # Keyboard hints
        text.append(" ? help ", style="dim")
        text.append("f fav ", style="dim")
        text.append("t test ", style="dim")
        text.append("c copy ", style="dim")

        return text


class FilterPanel(Static):
    """Panel for filtering the proxy table."""

    def compose(self) -> ComposeResult:
        """Create filter UI."""
        with Horizontal(id="filter-container"):
            yield Input(
                placeholder="🔍 Search URL...",
                id="filter-search",
            )

            yield Select(
                [
                    ("All Protocols", "all"),
                    ("HTTP", "http"),
                    ("HTTPS", "https"),
                    ("SOCKS4", "socks4"),
                    ("SOCKS5", "socks5"),
                ],
                id="filter-protocol",
                value="all",
            )

            yield Select(
                [
                    ("All Health", "all"),
                    ("Healthy", "healthy"),
                    ("Degraded", "degraded"),
                    ("Unhealthy", "unhealthy"),
                    ("Dead", "dead"),
                    ("Unknown", "unknown"),
                ],
                id="filter-health",
                value="all",
            )

            yield Select(
                [("All Countries", "all")],
                id="filter-country",
                value="all",
            )

            yield Checkbox("★ Favorites only", id="filter-favorites")


class RetryMetricsPanel(Static):
    """Panel for displaying retry metrics."""

    total_retries = reactive(0)
    successful_retries = reactive(0)
    failed_retries = reactive(0)

    def render(self) -> Text:
        """Render retry metrics display."""
        text = Text()
        text.append("🔄 Retry Metrics\n", style="bold cyan")
        text.append("─" * 30 + "\n", style="dim")

        text.append("Total Retries: ", style="white")
        text.append(f"{self.total_retries}\n", style="bold")

        text.append("Successful: ", style="white")
        text.append(f"{self.successful_retries}\n", style="bold green")

        text.append("Failed: ", style="white")
        text.append(f"{self.failed_retries}\n", style="bold red")

        if self.total_retries > 0:
            rate = self.successful_retries / self.total_retries * 100
            text.append("Success Rate: ", style="white")
            text.append(
                f"{rate:.1f}%\n",
                style="bold green" if rate > 50 else "bold yellow",
            )

        return text


class CircuitBreakerPanel(Static):
    """Panel for displaying circuit breaker states."""

    def compose(self) -> ComposeResult:
        """Create circuit breaker UI."""
        with Vertical(id="circuit-breaker-container"):
            yield Label("⚡ Circuit Breakers", classes="panel-title")
            yield Static("", id="circuit-breaker-content")
            yield Button("Reset All", id="reset-all-cb-btn", variant="warning")


class HealthCheckPanel(Static):
    """Panel for running health checks."""

    def compose(self) -> ComposeResult:
        """Create health check UI."""
        with Vertical(id="health-check-container"):
            yield Label("🏥 Health Check", classes="panel-title")

            yield ProgressBar(id="health-progress", show_eta=False)

            with Horizontal(classes="button-row"):
                yield Button("Run Health Check", id="health-check-btn", variant="primary")
                yield Button("Cancel", id="cancel-health-btn", variant="error")

            yield Label("", id="health-status")


class ProxyDetailsScreen(ModalScreen):
    """Modal screen showing detailed proxy information."""

    BINDINGS = [
        ("escape", "dismiss", "Close"),
    ]

    def __init__(self, proxy: Proxy, *args, **kwargs) -> None:
        """Initialize with proxy data."""
        super().__init__(*args, **kwargs)
        self.proxy = proxy

    def compose(self) -> ComposeResult:
        """Create modal content."""
        with Vertical(id="details-modal"):
            yield Label("📋 Proxy Details", classes="panel-title")

            details = Text()
            details.append("URL: ", style="bold cyan")
            details.append(f"{self.proxy.url}\n\n", style="white")

            details.append("Protocol: ", style="bold cyan")
            details.append(f"{self.proxy.protocol or 'http'}\n", style="white")

            details.append("Health Status: ", style="bold cyan")
            health_style = {
                HealthStatus.HEALTHY: "bold green",
                HealthStatus.DEGRADED: "bold yellow",
                HealthStatus.UNHEALTHY: "bold orange1",
                HealthStatus.DEAD: "bold red",
            }.get(self.proxy.health_status, "dim")
            details.append(f"{self.proxy.health_status.value}\n", style=health_style)

            details.append("\nPerformance:\n", style="bold cyan")
            details.append(
                f"  Latency: {self.proxy.average_response_time_ms or 0:.0f}ms\n",
                style="white",
            )
            details.append(f"  Successes: {self.proxy.total_successes}\n", style="green")
            details.append(f"  Failures: {self.proxy.total_failures}\n", style="red")

            if self.proxy.total_successes + self.proxy.total_failures > 0:
                success_rate = (
                    self.proxy.total_successes
                    / (self.proxy.total_successes + self.proxy.total_failures)
                    * 100
                )
                details.append(f"  Success Rate: {success_rate:.1f}%\n", style="white")

            details.append("\nMetadata:\n", style="bold cyan")
            details.append(f"  Country: {self.proxy.country_code or 'Unknown'}\n", style="white")
            details.append(f"  Source: {self.proxy.source.value}\n", style="white")

            if self.proxy.last_used_at:
                details.append(
                    f"  Last Used: {self.proxy.last_used_at.isoformat()}\n",
                    style="white",
                )

            if self.proxy.last_checked_at:
                details.append(
                    f"  Last Checked: {self.proxy.last_checked_at.isoformat()}\n",
                    style="white",
                )

            yield Static(details, id="details-content")

            with Horizontal(classes="button-row"):
                yield Button("Copy URL", id="copy-url-btn", variant="success")
                yield Button("Test Proxy", id="test-detail-proxy-btn", variant="primary")
                yield Button("Close", id="close-details-btn", variant="default")

    async def action_dismiss(self, result: ScreenResultType | None = None) -> None:
        """Dismiss the modal."""
        self.dismiss(result)

    @on(Button.Pressed, "#copy-url-btn")
    def copy_url_to_clipboard(self) -> None:
        """Copy proxy URL to clipboard."""
        try:
            import pyperclip

            pyperclip.copy(str(self.proxy.url))
            self.app.notify(f"Copied: {str(self.proxy.url)[:40]}...", severity="information")
        except ImportError:
            self.app.notify("pyperclip not installed", severity="warning")
        except Exception as e:
            self.app.notify(f"Copy failed: {e}", severity="error")


class ConfirmDeleteScreen(ModalScreen):
    """Modal screen for confirming proxy deletion."""

    BINDINGS = [
        ("escape", "dismiss", "Cancel"),
        ("enter", "confirm", "Confirm"),
    ]

    def __init__(self, proxy_url: str, *args, **kwargs) -> None:
        """Initialize with proxy URL to delete."""
        super().__init__(*args, **kwargs)
        self.proxy_url = proxy_url

    def compose(self) -> ComposeResult:
        """Create confirmation dialog."""
        with Vertical(id="confirm-modal"):
            yield Label("⚠️ Confirm Deletion", classes="panel-title")
            yield Static(
                f"Are you sure you want to remove this proxy?\n\n{self.proxy_url}",
                id="confirm-message",
            )

            with Horizontal(classes="button-row"):
                yield Button("Delete", id="confirm-delete-btn", variant="error")
                yield Button("Cancel", id="cancel-delete-btn", variant="default")

    async def action_dismiss(self, result: ScreenResultType | None = None) -> None:
        """Cancel and close modal."""
        self.dismiss(result)

    def action_confirm(self) -> None:
        """Confirm deletion."""
        self.dismiss(True)


class HelpScreen(ModalScreen):
    """Modal screen showing comprehensive help information."""

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("enter", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        """Create help modal content."""
        with Vertical(id="help-modal"):
            yield Label("🎯 ProxyWhirl TUI Help", classes="panel-title")

            with VerticalScroll(id="help-scroll"):
                yield Static(self._get_help_content(), id="help-content")

            with Horizontal(classes="button-row"):
                yield Button("Close [Esc]", id="close-help-btn", variant="primary")

    def _get_help_content(self) -> Text:
        """Generate formatted help content."""
        text = Text()

        # Navigation section
        text.append("⌨️  NAVIGATION\n", style="bold cyan")
        text.append("─" * 50 + "\n", style="dim")
        text.append("  j / ↓      ", style="bold white")
        text.append("Move down\n", style="white")
        text.append("  k / ↑      ", style="bold white")
        text.append("Move up\n", style="white")
        text.append("  g          ", style="bold white")
        text.append("Jump to first row\n", style="white")
        text.append("  G          ", style="bold white")
        text.append("Jump to last row\n", style="white")
        text.append("  /          ", style="bold white")
        text.append("Focus search box\n", style="white")
        text.append("\n")

        # Actions section
        text.append("🎬  ACTIONS\n", style="bold cyan")
        text.append("─" * 50 + "\n", style="dim")
        text.append("  Enter      ", style="bold white")
        text.append("View proxy details\n", style="white")
        text.append("  c          ", style="bold white")
        text.append("Copy proxy URL to clipboard\n", style="white")
        text.append("  f          ", style="bold white")
        text.append("Toggle favorite ★/☆\n", style="white")
        text.append("  Delete     ", style="bold white")
        text.append("Remove selected proxy\n", style="white")
        text.append("  Ctrl+R     ", style="bold white")
        text.append("Refresh all data\n", style="white")
        text.append("  Ctrl+A     ", style="bold white")
        text.append("Toggle auto-refresh\n", style="white")
        text.append("  Ctrl+D     ", style="bold white")
        text.append("Delete all unhealthy proxies\n", style="white")
        text.append("  t          ", style="bold white")
        text.append("Quick test selected proxy\n", style="white")
        text.append("\n")

        # Tabs section
        text.append("📑  TABS\n", style="bold cyan")
        text.append("─" * 50 + "\n", style="dim")
        text.append("  1-6        ", style="bold white")
        text.append("Switch to tab by number\n", style="white")
        text.append("  Ctrl+F     ", style="bold white")
        text.append("Fetch & Validate tab\n", style="white")
        text.append("  Ctrl+E     ", style="bold white")
        text.append("Export tab\n", style="white")
        text.append("  Ctrl+T     ", style="bold white")
        text.append("Test Request tab\n", style="white")
        text.append("  Ctrl+H     ", style="bold white")
        text.append("Health tab\n", style="white")
        text.append("  Ctrl+S     ", style="bold white")
        text.append("Analytics tab\n", style="white")
        text.append("\n")

        # Import/Export section
        text.append("📥  IMPORT/EXPORT\n", style="bold cyan")
        text.append("─" * 50 + "\n", style="dim")
        text.append("  Ctrl+I     ", style="bold white")
        text.append("Import proxies from clipboard\n", style="white")
        text.append("  Ctrl+E     ", style="bold white")
        text.append("Go to export tab\n", style="white")
        text.append("\n")

        # Table section
        text.append("📊  TABLE FEATURES\n", style="bold cyan")
        text.append("─" * 50 + "\n", style="dim")
        text.append("  • Click column headers to sort\n", style="white")
        text.append("  • Use filters to narrow results\n", style="white")
        text.append("  • Health status: ", style="white")
        text.append("●", style="green")
        text.append(" healthy  ", style="dim")
        text.append("●", style="yellow")
        text.append(" degraded  ", style="dim")
        text.append("●", style="red")
        text.append(" unhealthy\n", style="dim")
        text.append("\n")

        # Help section
        text.append("❓  HELP\n", style="bold cyan")
        text.append("─" * 50 + "\n", style="dim")
        text.append("  ?          ", style="bold white")
        text.append("Show this help modal\n", style="white")
        text.append("  F1         ", style="bold white")
        text.append("Quick help notification\n", style="white")
        text.append("  Ctrl+C     ", style="bold white")
        text.append("Quit application\n", style="white")

        return text

    async def action_dismiss(self, result: ScreenResultType | None = None) -> None:
        """Close the help modal."""
        self.dismiss(result)

    @on(Button.Pressed, "#close-help-btn")
    def close_help(self) -> None:
        """Close help modal."""
        self.app.pop_screen()


class ProxyWhirlTUI(App):
    """ProxyWhirl TUI Application."""

    TITLE = "🌀 ProxyWhirl"
    SUB_TITLE = "Intelligent Proxy Rotation"
    CSS_PATH = "tui.tcss"

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+r", "refresh", "Refresh"),
        ("ctrl+f", "fetch", "Fetch Proxies"),
        ("ctrl+e", "export", "Export"),
        ("ctrl+t", "test", "Test Request"),
        ("ctrl+h", "health", "Health Tab"),
        ("ctrl+s", "analytics", "Analytics"),
        ("ctrl+a", "toggle_auto_refresh", "Toggle Auto"),
        ("ctrl+d", "delete_unhealthy", "Delete Unhealthy"),
        ("ctrl+i", "import_proxies", "Import Proxies"),
        ("delete", "delete_proxy", "Delete Proxy"),
        ("enter", "view_details", "View Details"),
        ("c", "copy_url", "Copy URL"),
        ("t", "quick_test", "Quick Test"),
        ("f", "toggle_favorite", "Toggle Favorite"),
        ("j", "cursor_down", "Next Row"),
        ("k", "cursor_up", "Previous Row"),
        ("g", "cursor_top", "First Row"),
        ("G", "cursor_bottom", "Last Row"),
        ("1", "tab_1", "Tab 1"),
        ("2", "tab_2", "Tab 2"),
        ("3", "tab_3", "Tab 3"),
        ("4", "tab_4", "Tab 4"),
        ("5", "tab_5", "Tab 5"),
        ("6", "tab_6", "Tab 6"),
        ("?", "show_help_modal", "Help Modal"),
        ("/", "focus_search", "Search"),
        ("f1", "help", "Help"),
    ]

    # Filter state
    _filter_text: str = ""
    _filter_protocol: str = "all"
    _filter_health: str = "all"
    _filter_country: str = "all"
    _filter_favorites_only: bool = False

    # Health check cancellation flag
    _health_check_cancelled: bool = False

    # Auto-refresh state
    _auto_refresh_enabled: bool = True
    _auto_refresh_timer = None

    # Theme state
    dark_mode: bool = True

    # Start time for uptime tracking
    _app_start_time: datetime | None = None

    def __init__(self, rotator: ProxyRotator | None = None):
        """Initialize TUI."""
        super().__init__()
        self.rotator = rotator or ProxyRotator()
        self.fetcher: ProxyFetcher | None = None
        self.validator = ProxyValidator()
        self._app_start_time = datetime.now()

    def compose(self) -> ComposeResult:
        """Create TUI layout."""
        yield Header()

        with TabbedContent(initial="overview"):
            with TabPane("Overview", id="overview"), Horizontal():
                with Vertical(classes="left-panel"):
                    yield MetricsPanel(id="metrics-panel")
                    yield RetryMetricsPanel(id="retry-metrics-panel")
                    yield StrategyPanel()
                    yield ProxyControlPanel()

                with Vertical(classes="right-panel"):
                    yield FilterPanel()
                    with VerticalScroll():
                        yield ProxyTable(id="proxy-table")

            with TabPane("Fetch & Validate", id="fetch"), Horizontal():
                yield SourceFetcherPanel()
                with VerticalScroll():
                    yield Static("", id="fetch-results")

            with TabPane("Export", id="export"), Horizontal():
                yield ExportPanel()
                with VerticalScroll():
                    yield Static("", id="export-preview")

            with TabPane("Test", id="test"):
                yield RequestTesterPanel()

            with TabPane("Analytics", id="analytics"):
                yield AnalyticsPanel()

            with TabPane("Health", id="health"), Horizontal():
                with Vertical(classes="left-panel"):
                    yield HealthCheckPanel()
                with Vertical(classes="right-panel"):
                    yield CircuitBreakerPanel()

        yield StatusBar(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.refresh_all_data()
        self.set_interval(5.0, self.auto_refresh)
        self._populate_country_filter()

    def _populate_country_filter(self) -> None:
        """Populate country filter with available countries.

        Note: Textual Select doesn't support dynamic option updates easily,
        so this is a placeholder for future implementation.
        """
        try:
            _ = self.query_one("#filter-country", Select)
            proxies = self.rotator.pool.get_all_proxies()
            _ = sorted({p.country_code or "N/A" for p in proxies})
            # Dynamic population would require recreating the Select widget
        except Exception:
            pass

    def auto_refresh(self) -> None:
        """Auto-refresh data every 5 seconds (if enabled)."""
        if not self._auto_refresh_enabled:
            return

        self.refresh_table()
        self.refresh_metrics()
        self.refresh_retry_metrics()
        self.refresh_circuit_breakers()
        self.refresh_status_bar()

    def refresh_all_data(self) -> None:
        """Refresh all data displays."""
        self.refresh_table()
        self.refresh_metrics()
        self.refresh_retry_metrics()
        self.refresh_analytics()
        self.refresh_circuit_breakers()
        self.refresh_status_bar()

    def refresh_status_bar(self) -> None:
        """Refresh the status bar."""
        try:
            status_bar = self.query_one("#status-bar", StatusBar)
            proxies = self.rotator.pool.get_all_proxies()

            status_bar.proxy_count = len(proxies)
            status_bar.healthy_count = sum(
                1 for p in proxies if p.health_status == HealthStatus.HEALTHY
            )
            status_bar.auto_refresh = self._auto_refresh_enabled
            status_bar.current_strategy = self.rotator.strategy.__class__.__name__.replace(
                "Strategy", ""
            ).lower()
        except Exception:
            pass

    def refresh_table(self) -> None:
        """Refresh the proxy table with current filters."""
        table = self.query_one("#proxy-table", ProxyTable)
        proxies = self.rotator.pool.get_all_proxies()
        table.update_proxies(
            proxies,
            filter_text=self._filter_text,
            filter_protocol=self._filter_protocol,
            filter_health=self._filter_health,
            filter_country=self._filter_country,
            filter_favorites_only=self._filter_favorites_only,
        )

    def refresh_metrics(self) -> None:
        """Refresh metrics panel."""
        metrics = self.query_one("#metrics-panel", MetricsPanel)

        proxies = self.rotator.pool.get_all_proxies()
        total = len(proxies)
        healthy = sum(1 for p in proxies if p.health_status == HealthStatus.HEALTHY)
        degraded = sum(1 for p in proxies if p.health_status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for p in proxies if p.health_status == HealthStatus.UNHEALTHY)
        active = healthy + degraded

        total_success = sum(p.total_successes for p in proxies)
        total_failures = sum(p.total_failures for p in proxies)
        total_requests = total_success + total_failures

        success_rate = (total_success / total_requests * 100) if total_requests > 0 else 0.0

        latencies = [
            p.average_response_time_ms
            for p in proxies
            if p.average_response_time_ms is not None and p.average_response_time_ms > 0
        ]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        # Store previous values for trend indicators
        metrics.prev_latency = metrics.avg_latency
        metrics.prev_success_rate = metrics.success_rate

        metrics.total_proxies = total
        metrics.active_proxies = active
        metrics.healthy_proxies = healthy
        metrics.degraded_proxies = degraded
        metrics.unhealthy_proxies = unhealthy
        metrics.total_requests = total_requests
        metrics.success_rate = success_rate
        metrics.avg_latency = avg_latency

        # Update history for sparklines
        metrics.update_history(avg_latency, success_rate)

    def refresh_analytics(self) -> None:
        """Refresh analytics display with histogram."""
        analytics_content = self.query_one("#analytics-content", Static)

        proxies = self.rotator.pool.get_all_proxies()
        if not proxies:
            analytics_content.update("No proxies available for analytics.")
            return

        # Calculate statistics
        total = len(proxies)
        by_protocol = {}
        by_country = {}
        by_source = {}
        latencies = []

        for proxy in proxies:
            # Protocol stats
            protocol = proxy.protocol or "http"
            by_protocol[protocol] = by_protocol.get(protocol, 0) + 1

            # Country stats
            country = proxy.country_code or "Unknown"
            by_country[country] = by_country.get(country, 0) + 1

            # Source stats
            source = proxy.source.value
            by_source[source] = by_source.get(source, 0) + 1

            # Latency for histogram
            if proxy.average_response_time_ms and proxy.average_response_time_ms > 0:
                latencies.append(proxy.average_response_time_ms)

        # Format output
        text = Text()

        # Latency histogram
        if latencies:
            text.append("⏱️  Response Time Distribution\n", style="bold cyan")
            text.append("─" * 40 + "\n", style="dim")

            # Create histogram buckets
            buckets = [
                (0, 100, "< 100ms"),
                (100, 500, "100-500ms"),
                (500, 1000, "500ms-1s"),
                (1000, 2000, "1-2s"),
                (2000, 5000, "2-5s"),
                (5000, float("inf"), "> 5s"),
            ]

            max_count = 0
            bucket_counts = []
            for low, high, label in buckets:
                count = sum(1 for lat in latencies if low <= lat < high)
                bucket_counts.append((label, count))
                max_count = max(max_count, count)

            # Draw histogram bars
            bar_width = 20
            for label, count in bucket_counts:
                bar_len = int(count / max_count * bar_width) if max_count > 0 else 0

                # Color based on latency (green=fast, red=slow)
                if "< 100" in label or "100-500" in label:
                    style = "green"
                elif "500ms" in label or "1-2s" in label:
                    style = "yellow"
                else:
                    style = "red"

                text.append(f"  {label:>10} ", style="white")
                text.append("█" * bar_len, style=style)
                text.append("░" * (bar_width - bar_len), style="dim")
                text.append(f" {count}\n", style="white")

            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            text.append(f"\n  Avg: {avg_latency:.0f}ms | ", style="dim")
            text.append(f"Min: {min_latency:.0f}ms | ", style="green")
            text.append(f"Max: {max_latency:.0f}ms\n", style="red")
            text.append("\n")

        # Protocol distribution
        text.append("📡 Protocol Distribution\n", style="bold cyan")
        text.append("─" * 40 + "\n", style="dim")
        for protocol, count in sorted(by_protocol.items()):
            pct = count / total * 100
            bar_len = int(pct / 100 * 20)
            text.append(f"  {protocol:>8}: ", style="white")
            text.append("█" * bar_len, style="cyan")
            text.append(f" {count} ({pct:.0f}%)\n", style="white")

        # Top countries
        text.append("\n🌍 Top Countries\n", style="bold cyan")
        text.append("─" * 40 + "\n", style="dim")
        for country, count in sorted(by_country.items(), key=lambda x: x[1], reverse=True)[:8]:
            pct = count / total * 100
            text.append(f"  {country:>8}: {count:>4} ({pct:.1f}%)\n", style="white")

        # Health summary
        healthy = sum(1 for p in proxies if p.health_status == HealthStatus.HEALTHY)
        degraded = sum(1 for p in proxies if p.health_status == HealthStatus.DEGRADED)
        unhealthy = sum(
            1 for p in proxies if p.health_status in (HealthStatus.UNHEALTHY, HealthStatus.DEAD)
        )

        text.append("\n💚 Health Summary\n", style="bold cyan")
        text.append("─" * 40 + "\n", style="dim")
        text.append(f"  Healthy:   {healthy:>4} ", style="green")
        text.append("█" * int(healthy / total * 20) if total > 0 else "", style="green")
        text.append("\n")
        text.append(f"  Degraded:  {degraded:>4} ", style="yellow")
        text.append("█" * int(degraded / total * 20) if total > 0 else "", style="yellow")
        text.append("\n")
        text.append(f"  Unhealthy: {unhealthy:>4} ", style="red")
        text.append("█" * int(unhealthy / total * 20) if total > 0 else "", style="red")
        text.append("\n")

        analytics_content.update(text)

    @on(Button.Pressed, "#fetch-btn")
    def fetch_proxies(self) -> None:
        """Fetch proxies from selected sources."""
        self.fetch_proxies_async()

    @work(exclusive=True)
    async def fetch_proxies_async(self) -> None:
        """Async worker to fetch proxies."""
        status_label = self.query_one("#fetch-status", Label)
        status_label.update("🔄 Fetching proxies...")

        source_select = self.query_one("#source-select", Select)
        source_type = str(source_select.value)

        # Select sources based on type
        if source_type == "all":
            sources = ALL_SOURCES
        elif source_type == "recommended":
            sources = RECOMMENDED_SOURCES
        elif source_type == "http":
            sources = ALL_HTTP_SOURCES
        elif source_type == "socks4":
            sources = ALL_SOCKS4_SOURCES
        elif source_type == "socks5":
            sources = ALL_SOCKS5_SOURCES
        else:
            sources = RECOMMENDED_SOURCES

        try:
            status_label.update(f"🔄 Fetching from {len(sources)} sources...")
            self.fetcher = ProxyFetcher(sources=sources)
            proxies_data = await self.fetcher.fetch_all(validate=False)

            # Add to rotator
            count = 0
            for proxy_dict in proxies_data:
                try:
                    proxy_url = proxy_dict.get("url")
                    if proxy_url:
                        self.rotator.add_proxy(proxy_url)
                        count += 1
                except Exception:
                    continue

            status_label.update(f"✅ Fetched {count} proxies")
            self.refresh_all_data()

        except ProxyFetchError as e:
            status_label.update(f"❌ Fetch failed: {e}")
        except Exception as e:
            status_label.update(f"❌ Error: {e}")

    @on(Button.Pressed, "#validate-all-btn")
    def validate_all_proxies(self) -> None:
        """Validate all proxies."""
        self.validate_proxies_async()

    @work(exclusive=True)
    async def validate_proxies_async(self) -> None:
        """Async worker to validate proxies."""
        status_label = self.query_one("#fetch-status", Label)
        status_label.update("🔄 Validating proxies...")

        proxies = self.rotator.pool.get_all_proxies()
        if not proxies:
            status_label.update("❌ No proxies to validate")
            return

        try:
            proxy_dicts = [{"url": str(p.url)} for p in proxies]
            valid_proxies = await self.validator.validate_batch(proxy_dicts)

            valid_count = len([p for p in valid_proxies if p.get("valid", False)])
            status_label.update(f"✅ Validation complete: {valid_count}/{len(proxies)} valid")

        except Exception as e:
            status_label.update(f"❌ Validation failed: {e}")

    @on(Button.Pressed, "#preview-export-btn")
    def preview_export(self) -> None:
        """Show preview of export format."""
        export_format_select = self.query_one("#export-format", Select)
        preview_output = self.query_one("#export-preview", Static)

        format_type = str(export_format_select.value)
        proxies = self.rotator.pool.get_all_proxies()[:5]  # Preview first 5

        if not proxies:
            preview_output.update("No proxies available for preview.")
            return

        text = Text()
        text.append(f"📋 Preview ({format_type.upper()} format)\n", style="bold cyan")
        text.append("─" * 40 + "\n\n", style="dim")

        if format_type == "csv":
            text.append("url,protocol,health,latency_ms,country\n", style="bold white")
            for p in proxies:
                text.append(
                    f"{p.url},{p.protocol or 'http'},{p.health_status.value},"
                    f"{p.average_response_time_ms or 0:.0f},{p.country_code or 'N/A'}\n",
                    style="white",
                )
        elif format_type == "json":
            import json as json_mod

            preview_data = [
                {
                    "url": str(p.url),
                    "protocol": p.protocol or "http",
                    "health": p.health_status.value,
                    "latency_ms": p.average_response_time_ms or 0,
                    "country": p.country_code or "N/A",
                }
                for p in proxies
            ]
            text.append(json_mod.dumps(preview_data, indent=2), style="white")
        elif format_type == "text":
            for p in proxies:
                text.append(f"{p.url}\n", style="white")
        elif format_type == "yaml":
            for p in proxies:
                text.append(f"- url: {p.url}\n", style="white")
                text.append(f"  protocol: {p.protocol or 'http'}\n", style="dim")
                text.append(f"  health: {p.health_status.value}\n", style="dim")

        if len(self.rotator.pool.get_all_proxies()) > 5:
            text.append(
                f"\n... and {len(self.rotator.pool.get_all_proxies()) - 5} more\n", style="dim"
            )

        preview_output.update(text)

    @on(Button.Pressed, "#export-all-btn")
    def export_all_proxies(self) -> None:
        """Export all proxies."""
        self.export_proxies(healthy_only=False)

    @on(Button.Pressed, "#export-healthy-btn")
    def export_healthy_proxies(self) -> None:
        """Export only healthy proxies."""
        self.export_proxies(healthy_only=True)

    def export_proxies(self, healthy_only: bool = False) -> None:
        """Export proxies to file."""
        export_path_input = self.query_one("#export-path", Input)
        export_format_select = self.query_one("#export-format", Select)
        status_label = self.query_one("#export-status", Label)

        file_path = export_path_input.value
        if not file_path:
            status_label.update("❌ Please enter a file path")
            return

        format_type = str(export_format_select.value)

        # Filter proxies
        proxies = self.rotator.pool.get_all_proxies()
        if healthy_only:
            proxies = [p for p in proxies if p.health_status == HealthStatus.HEALTHY]

        if not proxies:
            status_label.update("❌ No proxies to export")
            return

        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            if format_type == "csv":
                self._export_csv(path, proxies)
            elif format_type == "json":
                self._export_json(path, proxies)
            elif format_type == "text":
                self._export_text(path, proxies)
            elif format_type == "yaml":
                self._export_yaml(path, proxies)

            status_label.update(f"✅ Exported {len(proxies)} proxies to {file_path}")

        except Exception as e:
            status_label.update(f"❌ Export failed: {e}")

    def _export_csv(self, path: Path, proxies: list[Proxy]) -> None:
        """Export to CSV format."""
        import io

        from proxywhirl.utils import atomic_write

        # Write to string buffer first
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["URL", "Protocol", "Health", "Latency", "Successes", "Failures", "Country"]
        )
        for proxy in proxies:
            writer.writerow(
                [
                    str(proxy.url),
                    proxy.protocol or "http",
                    proxy.health_status.value,
                    proxy.average_response_time_ms or 0,
                    proxy.total_successes,
                    proxy.total_failures,
                    proxy.country_code or "N/A",
                ]
            )

        # Write atomically
        atomic_write(path, output.getvalue())

    def _export_json(self, path: Path, proxies: list[Proxy]) -> None:
        """Export to JSON format."""
        from proxywhirl.utils import atomic_write_json

        data = {
            "export_date": datetime.now().isoformat(),
            "total_proxies": len(proxies),
            "proxies": [
                {
                    "url": str(p.url),
                    "protocol": p.protocol or "http",
                    "health_status": p.health_status.value,
                    "latency_ms": p.average_response_time_ms,
                    "successes": p.total_successes,
                    "failures": p.total_failures,
                    "country": p.country_code,
                }
                for p in proxies
            ],
        }
        # Write atomically
        atomic_write_json(path, data, indent=2)

    def _export_text(self, path: Path, proxies: list[Proxy]) -> None:
        """Export to text format (one URL per line)."""
        from proxywhirl.utils import atomic_write

        # Build content first
        content = "\n".join(str(proxy.url) for proxy in proxies) + "\n"

        # Write atomically
        atomic_write(path, content)

    def _export_yaml(self, path: Path, proxies: list[Proxy]) -> None:
        """Export to YAML format."""
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML export")

        from proxywhirl.utils import atomic_write

        data = {
            "export_date": datetime.now().isoformat(),
            "total_proxies": len(proxies),
            "proxies": [
                {
                    "url": str(p.url),
                    "protocol": p.protocol or "http",
                    "health_status": p.health_status.value,
                    "latency_ms": p.average_response_time_ms,
                    "successes": p.total_successes,
                    "failures": p.total_failures,
                    "country": p.country_code,
                }
                for p in proxies
            ],
        }

        # Serialize to string first
        yaml_content = yaml.dump(data, default_flow_style=False)

        # Write atomically
        atomic_write(path, yaml_content)

    @on(Button.Pressed, "#apply-strategy-btn")
    def apply_strategy(self) -> None:
        """Apply selected rotation strategy."""
        strategy_select = self.query_one("#strategy-select", Select)
        status_label = self.query_one("#strategy-status", Label)

        strategy_type = str(strategy_select.value)

        try:
            if strategy_type == "round-robin":
                self.rotator.strategy = RoundRobinStrategy()
            elif strategy_type == "random":
                self.rotator.strategy = RandomStrategy()
            elif strategy_type == "weighted":
                self.rotator.strategy = WeightedStrategy()
            elif strategy_type == "least-used":
                self.rotator.strategy = LeastUsedStrategy()
            elif strategy_type == "performance":
                self.rotator.strategy = PerformanceBasedStrategy()
            elif strategy_type == "geo":
                self.rotator.strategy = GeoTargetedStrategy()
            elif strategy_type == "session":
                self.rotator.strategy = SessionPersistenceStrategy()

            status_label.update(f"✅ Applied {strategy_type} strategy")

        except Exception as e:
            status_label.update(f"❌ Failed to apply strategy: {e}")

    def _validate_request_url(self, url: str) -> None:
        """Validate URL to prevent SSRF attacks.

        Args:
            url: The URL to validate

        Raises:
            ValueError: If the URL is invalid or potentially dangerous
        """
        validate_target_url_safe(url)

    @on(Button.Pressed, "#send-request-btn")
    def send_request(self) -> None:
        """Send test request through proxy."""
        self.send_request_async()

    @work(exclusive=True)
    async def send_request_async(self) -> None:
        """Async worker to send test request."""
        url_input = self.query_one("#test-url", Input)
        method_select = self.query_one("#test-method", Select)
        headers_input = self.query_one("#test-headers", Input)
        body_textarea = self.query_one("#test-body", TextArea)
        output_static = self.query_one("#response-output", Static)

        url = url_input.value
        method = str(method_select.value)

        if not url:
            output_static.update("❌ Please enter a URL")
            return

        # Validate URL to prevent SSRF attacks
        try:
            self._validate_request_url(url)
        except ValueError as e:
            output_static.update(f"❌ Invalid URL: {e}")
            self.notify(str(e), severity="error", timeout=5)
            return

        # Parse custom headers
        custom_headers = {}
        if headers_input.value.strip():
            try:
                custom_headers = json.loads(headers_input.value)
                if not isinstance(custom_headers, dict):
                    raise ValueError("Headers must be a JSON object")
            except (json.JSONDecodeError, ValueError) as e:
                output_static.update(f"❌ Invalid headers JSON: {e}")
                return

        # Parse request body
        request_body = None
        body_text = body_textarea.text.strip()
        if body_text and method in ("POST", "PUT", "PATCH"):
            try:
                request_body = json.loads(body_text)
            except json.JSONDecodeError:
                # Use as raw text if not valid JSON
                request_body = body_text

        output_static.update(f"🔄 Sending {method} request to {url}...")

        try:
            # Build request kwargs
            kwargs: dict = {}
            if custom_headers:
                kwargs["headers"] = custom_headers
            if request_body is not None:
                if isinstance(request_body, dict):
                    kwargs["json"] = request_body
                else:
                    kwargs["content"] = request_body

            # Use rotator's request method
            if method == "GET":
                response = self.rotator.get(url, **kwargs)
            elif method == "POST":
                if "json" not in kwargs and "content" not in kwargs:
                    kwargs["json"] = {}
                response = self.rotator.post(url, **kwargs)
            elif method == "PUT":
                if "json" not in kwargs and "content" not in kwargs:
                    kwargs["json"] = {}
                response = self.rotator.put(url, **kwargs)
            elif method == "DELETE":
                response = self.rotator.delete(url, **kwargs)
            elif method == "HEAD":
                response = self.rotator.head(url, **kwargs)
            elif method == "PATCH":
                if "json" not in kwargs and "content" not in kwargs:
                    kwargs["json"] = {}
                response = self.rotator.patch(url, **kwargs)
            elif method == "OPTIONS":
                response = self.rotator.options(url, **kwargs)
            else:
                output_static.update(f"❌ Unsupported method: {method}")
                return

            # Format response
            result_text = Text()
            result_text.append(f"✅ {method} {url}\n", style="bold green")
            result_text.append(f"Status: {response.status_code}\n", style="cyan")
            result_text.append(
                f"Response Time: {response.elapsed.total_seconds():.2f}s\n", style="yellow"
            )
            result_text.append("\nResponse Body:\n", style="bold")

            try:
                json_data = response.json()
                result_text.append(json.dumps(json_data, indent=2), style="white")
            except Exception:
                result_text.append(response.text[:1000], style="white")

            output_static.update(result_text)
            self.refresh_all_data()

        except Exception as e:
            output_static.update(f"❌ Request failed: {e}")

    @on(Button.Pressed, "#refresh-analytics-btn")
    def refresh_analytics_button(self) -> None:
        """Refresh analytics on button click."""
        self.refresh_analytics()

    def action_refresh(self) -> None:
        """Refresh all data."""
        self.refresh_all_data()

    def action_fetch(self) -> None:
        """Focus fetch tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "fetch"

    def action_export(self) -> None:
        """Focus export tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "export"

    def action_test(self) -> None:
        """Focus test tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "test"

    def action_health(self) -> None:
        """Focus health tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "health"

    def action_analytics(self) -> None:
        """Focus analytics tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "analytics"
        self.refresh_analytics()

    def action_delete_unhealthy(self) -> None:
        """Delete all unhealthy/dead proxies."""
        proxies = self.rotator.pool.get_all_proxies()
        unhealthy = [
            p for p in proxies if p.health_status in (HealthStatus.UNHEALTHY, HealthStatus.DEAD)
        ]

        if not unhealthy:
            self.notify("No unhealthy proxies to delete", severity="information")
            return

        # Remove all unhealthy proxies
        removed = 0
        for proxy in unhealthy:
            try:
                self.rotator.remove_proxy(str(proxy.url))
                removed += 1
            except Exception:
                pass

        self.notify(f"🗑️ Removed {removed} unhealthy proxies", severity="information")
        self.refresh_all_data()

    def action_copy_url(self) -> None:
        """Copy selected proxy URL to clipboard."""
        table = self.query_one("#proxy-table", ProxyTable)
        proxy = table.get_selected_proxy()

        if proxy:
            try:
                import pyperclip

                pyperclip.copy(str(proxy.url))
                self.notify(f"Copied: {str(proxy.url)[:40]}...", severity="information")
            except ImportError:
                self.notify("pyperclip not installed", severity="warning")
            except Exception as e:
                self.notify(f"Copy failed: {e}", severity="error")
        else:
            self.notify("No proxy selected", severity="warning")

    def action_cursor_down(self) -> None:
        """Move cursor down in proxy table (vim j key)."""
        try:
            table = self.query_one("#proxy-table", ProxyTable)
            if table.row_count > 0:
                table.action_cursor_down()
        except Exception:
            pass

    def action_cursor_up(self) -> None:
        """Move cursor up in proxy table (vim k key)."""
        try:
            table = self.query_one("#proxy-table", ProxyTable)
            if table.row_count > 0:
                table.action_cursor_up()
        except Exception:
            pass

    def action_cursor_top(self) -> None:
        """Move cursor to first row (vim g key)."""
        try:
            table = self.query_one("#proxy-table", ProxyTable)
            if table.row_count > 0:
                table.move_cursor(row=0)
        except Exception:
            pass

    def action_cursor_bottom(self) -> None:
        """Move cursor to last row (vim G key)."""
        try:
            table = self.query_one("#proxy-table", ProxyTable)
            if table.row_count > 0:
                table.move_cursor(row=table.row_count - 1)
        except Exception:
            pass

    def action_help(self) -> None:
        """Show help message."""
        self.notify(
            "ProxyWhirl TUI\n\n"
            "Navigation:\n"
            "j/k - Move down/up\n"
            "g/G - First/Last row\n"
            "Enter - View details\n"
            "c - Copy URL\n"
            "Delete - Remove proxy\n\n"
            "Tabs:\n"
            "Ctrl+F - Fetch tab\n"
            "Ctrl+E - Export tab\n"
            "Ctrl+T - Test tab\n"
            "Ctrl+H - Health tab\n"
            "Ctrl+R - Refresh\n"
            "? - Full help\n",
            title="Help",
            timeout=10,
        )

    def action_show_help_modal(self) -> None:
        """Show the comprehensive help modal."""
        self.push_screen(HelpScreen())

    def action_focus_search(self) -> None:
        """Focus the search input box."""
        try:
            search_input = self.query_one("#filter-search", Input)
            search_input.focus()
        except Exception:
            pass

    def action_toggle_auto_refresh(self) -> None:
        """Toggle auto-refresh on/off."""
        self._auto_refresh_enabled = not self._auto_refresh_enabled
        self.refresh_status_bar()

        if self._auto_refresh_enabled:
            self.notify("🔄 Auto-refresh enabled", severity="information")
        else:
            self.notify("⏸️ Auto-refresh paused", severity="warning")

    def action_quick_test(self) -> None:
        """Quick test selected proxy with httpbin."""
        table = self.query_one("#proxy-table", ProxyTable)
        proxy = table.get_selected_proxy()

        if not proxy:
            self.notify("No proxy selected", severity="warning")
            return

        self.notify(f"🧪 Testing {str(proxy.url)[:30]}...", severity="information")
        self.quick_test_proxy_async(proxy)

    @work(exclusive=True)
    async def quick_test_proxy_async(self, proxy: Proxy) -> None:
        """Async worker for quick proxy test."""
        try:
            # Test against httpbin
            response = self.rotator.get(
                "https://httpbin.org/ip",
                timeout=10,
            )

            if response.status_code == 200:
                self.notify(
                    f"✅ Proxy works! ({response.elapsed.total_seconds():.1f}s)",
                    severity="information",
                    timeout=5,
                )
                proxy.record_success(response.elapsed.total_seconds() * 1000)
            else:
                self.notify(
                    f"⚠️ Proxy returned {response.status_code}",
                    severity="warning",
                    timeout=5,
                )
                proxy.record_failure()

            self.refresh_table()
            self.refresh_metrics()

        except Exception as e:
            self.notify(f"❌ Test failed: {e}", severity="error", timeout=5)
            proxy.record_failure()
            self.refresh_table()

    # =========================================================================
    # Tab Navigation (1-6 keys)
    # =========================================================================

    def action_tab_1(self) -> None:
        """Switch to tab 1 (Overview)."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "overview"

    def action_tab_2(self) -> None:
        """Switch to tab 2 (Fetch)."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "fetch"

    def action_tab_3(self) -> None:
        """Switch to tab 3 (Export)."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "export"

    def action_tab_4(self) -> None:
        """Switch to tab 4 (Test)."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "test"

    def action_tab_5(self) -> None:
        """Switch to tab 5 (Analytics)."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "analytics"

    def action_tab_6(self) -> None:
        """Switch to tab 6 (Health)."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "health"

    # =========================================================================
    # Import Proxies
    # =========================================================================

    def action_import_proxies(self) -> None:
        """Import proxies from clipboard or show import dialog."""
        try:
            import pyperclip

            clipboard = pyperclip.paste()
            if clipboard:
                # Try to parse proxies from clipboard
                lines = clipboard.strip().split("\n")
                added = 0
                for line in lines:
                    line = line.strip()
                    if line and (":" in line or line.startswith("http")):
                        try:
                            # Add protocol if missing
                            if not line.startswith(("http://", "https://", "socks")):
                                line = f"http://{line}"
                            self.rotator.add_proxy(line)
                            added += 1
                        except Exception:
                            continue

                if added > 0:
                    self.notify(
                        f"📥 Imported {added} proxies from clipboard", severity="information"
                    )
                    self.refresh_all_data()
                else:
                    self.notify("No valid proxies found in clipboard", severity="warning")
            else:
                self.notify("Clipboard is empty", severity="warning")
        except ImportError:
            self.notify("pyperclip not installed", severity="warning")
        except Exception as e:
            self.notify(f"Import failed: {e}", severity="error")

    # =========================================================================
    # New Enhancement Handlers
    # =========================================================================

    def refresh_retry_metrics(self) -> None:
        """Refresh retry metrics panel."""
        try:
            retry_panel = self.query_one("#retry-metrics-panel", RetryMetricsPanel)
            metrics = self.rotator.get_retry_metrics()

            retry_panel.total_retries = metrics.total_retries
            retry_panel.successful_retries = metrics.successful_retries
            retry_panel.failed_retries = metrics.failed_retries
        except Exception:
            pass  # Panel may not exist or metrics unavailable

    def refresh_circuit_breakers(self) -> None:
        """Refresh circuit breaker status display."""
        try:
            cb_content = self.query_one("#circuit-breaker-content", Static)
            states = self.rotator.get_circuit_breaker_states()

            if not states:
                cb_content.update("No circuit breakers active.")
                return

            text = Text()
            for proxy_id, cb in states.items():
                # Get state name
                state_name = cb.state.name if hasattr(cb, "state") else "UNKNOWN"

                # Color-code state
                if state_name == "CLOSED":
                    style = "bold green"
                    icon = "✅"
                elif state_name == "OPEN":
                    style = "bold red"
                    icon = "🔴"
                elif state_name == "HALF_OPEN":
                    style = "bold yellow"
                    icon = "🟡"
                else:
                    style = "dim"
                    icon = "❓"

                # Truncate proxy ID for display
                display_id = proxy_id[:30] + "..." if len(proxy_id) > 30 else proxy_id

                text.append(f"{icon} ", style=style)
                text.append(f"{display_id}: ", style="white")
                text.append(f"{state_name}\n", style=style)

            cb_content.update(text)
        except Exception:
            pass  # Panel may not exist or feature unavailable

    @on(Button.Pressed, "#add-proxy-btn")
    def add_proxy(self) -> None:
        """Add a proxy manually. Supports multiple proxies separated by newlines."""
        url_input = self.query_one("#add-proxy-url", Input)
        username_input = self.query_one("#add-proxy-username", Input)
        password_input = self.query_one("#add-proxy-password", Input)
        status_label = self.query_one("#control-status", Label)

        raw_input = url_input.value.strip()
        if not raw_input:
            status_label.update("❌ Please enter a proxy URL")
            return

        # Support multiple URLs separated by newlines, commas, or spaces
        urls = []
        for line in raw_input.replace(",", "\n").replace(" ", "\n").split("\n"):
            url = line.strip()
            if url:
                urls.append(url)

        if not urls:
            status_label.update("❌ No valid URLs found")
            return

        try:
            username = username_input.value.strip()
            password = password_input.value.strip()

            added = 0
            for url in urls:
                # Validate URL format (basic check)
                if not url.startswith(("http://", "https://", "socks4://", "socks5://")):
                    url = f"http://{url}"

                # Add credentials if provided
                if username and password:
                    from urllib.parse import urlparse, urlunparse

                    parsed = urlparse(url)
                    netloc = f"{username}:{password}@{parsed.hostname}"
                    if parsed.port:
                        netloc += f":{parsed.port}"
                    url = urlunparse(parsed._replace(netloc=netloc))

                try:
                    self.rotator.add_proxy(url)
                    added += 1
                except Exception:
                    pass

            if added == 1:
                status_label.update(f"✅ Added proxy: {urls[0][:40]}...")
            else:
                status_label.update(f"✅ Added {added} proxies")

            # Clear inputs
            url_input.value = ""
            username_input.value = ""
            password_input.value = ""

            self.refresh_all_data()

        except Exception as e:
            status_label.update(f"❌ Failed to add proxy: {e}")

    @on(Button.Pressed, "#remove-proxy-btn")
    def remove_selected_proxy(self) -> None:
        """Remove the selected proxy from the pool."""
        table = self.query_one("#proxy-table", ProxyTable)
        proxy = table.get_selected_proxy()

        if not proxy:
            self.notify("No proxy selected", severity="warning")
            return

        # Show confirmation dialog
        self.push_screen(
            ConfirmDeleteScreen(str(proxy.url)),
            self._handle_delete_confirmation,
        )

    def _handle_delete_confirmation(self, confirmed: bool | None) -> None:
        """Handle delete confirmation result."""
        if confirmed:
            table = self.query_one("#proxy-table", ProxyTable)
            proxy = table.get_selected_proxy()

            if proxy:
                try:
                    self.rotator.remove_proxy(str(proxy.url))
                    self.notify(f"Removed proxy: {str(proxy.url)[:40]}...", severity="information")
                    self.refresh_all_data()
                except Exception as e:
                    self.notify(f"Failed to remove: {e}", severity="error")

    @on(Button.Pressed, "#clear-all-btn")
    def clear_all_proxies(self) -> None:
        """Clear all proxies from the pool."""
        proxies = self.rotator.pool.get_all_proxies()
        if not proxies:
            self.notify("No proxies to clear", severity="information")
            return

        count = len(proxies)
        for proxy in proxies:
            try:
                self.rotator.remove_proxy(str(proxy.url))
            except Exception:
                pass

        self.notify(f"🗑️ Cleared {count} proxies", severity="information")
        self.refresh_all_data()

    @on(Button.Pressed, "#test-all-btn")
    def test_all_proxies(self) -> None:
        """Test all healthy proxies."""
        self.test_all_proxies_async()

    @work(exclusive=True)
    async def test_all_proxies_async(self) -> None:
        """Async worker to test all proxies."""
        proxies = self.rotator.pool.get_all_proxies()
        healthy = [p for p in proxies if p.health_status == HealthStatus.HEALTHY]

        if not healthy:
            self.notify("No healthy proxies to test", severity="warning")
            return

        self.notify(f"🧪 Testing {len(healthy)} healthy proxies...", severity="information")

        passed = 0
        failed = 0

        for proxy in healthy:
            try:
                response = self.rotator.get(
                    "https://httpbin.org/ip",
                    timeout=10,
                )
                if response.status_code == 200:
                    proxy.record_success(response.elapsed.total_seconds() * 1000)
                    passed += 1
                else:
                    proxy.record_failure()
                    failed += 1
            except Exception:
                proxy.record_failure()
                failed += 1

        self.notify(f"✅ {passed} passed, ❌ {failed} failed", severity="information")
        self.refresh_all_data()

    def action_delete_proxy(self) -> None:
        """Delete key action to remove selected proxy."""
        self.remove_selected_proxy()

    def action_toggle_favorite(self) -> None:
        """Toggle favorite status for selected proxy."""
        table = self.query_one("#proxy-table", ProxyTable)
        proxy = table.get_selected_proxy()

        if proxy:
            is_fav = table.toggle_favorite(str(proxy.url))
            if is_fav:
                self.notify("★ Added to favorites", severity="information")
            else:
                self.notify("☆ Removed from favorites", severity="information")
            self.refresh_table()
        else:
            self.notify("No proxy selected", severity="warning")

    def action_view_details(self) -> None:
        """Enter key action to view proxy details."""
        table = self.query_one("#proxy-table", ProxyTable)
        proxy = table.get_selected_proxy()

        if proxy:
            self.push_screen(ProxyDetailsScreen(proxy))
        else:
            self.notify("No proxy selected", severity="warning")

    @on(Button.Pressed, "#close-details-btn")
    def close_details(self) -> None:
        """Close details modal."""
        self.pop_screen()

    @on(Button.Pressed, "#confirm-delete-btn")
    def confirm_delete(self) -> None:
        """Confirm proxy deletion."""
        screen = self.screen
        if isinstance(screen, ConfirmDeleteScreen):
            screen.dismiss(True)

    @on(Button.Pressed, "#cancel-delete-btn")
    def cancel_delete(self) -> None:
        """Cancel proxy deletion."""
        self.pop_screen()

    # Filter handlers
    @on(Input.Changed, "#filter-search")
    def filter_search_changed(self, event: Input.Changed) -> None:
        """Handle search filter change."""
        self._filter_text = event.value
        self.refresh_table()

    @on(Select.Changed, "#filter-protocol")
    def filter_protocol_changed(self, event: Select.Changed) -> None:
        """Handle protocol filter change."""
        self._filter_protocol = str(event.value)
        self.refresh_table()

    @on(Select.Changed, "#filter-health")
    def filter_health_changed(self, event: Select.Changed) -> None:
        """Handle health filter change."""
        self._filter_health = str(event.value)
        self.refresh_table()

    @on(Select.Changed, "#filter-country")
    def filter_country_changed(self, event: Select.Changed) -> None:
        """Handle country filter change."""
        self._filter_country = str(event.value)
        self.refresh_table()

    @on(Checkbox.Changed, "#filter-favorites")
    def filter_favorites_changed(self, event: Checkbox.Changed) -> None:
        """Handle favorites filter change."""
        self._filter_favorites_only = event.value
        self.refresh_table()

    # Column sorting handler
    @on(DataTable.HeaderSelected)
    def sort_column(self, event: DataTable.HeaderSelected) -> None:
        """Handle column header click for sorting."""
        table = self.query_one("#proxy-table", ProxyTable)
        if event.column_key:
            table.set_sort(str(event.column_key.value))
            self.refresh_table()

    # Health check handlers
    @on(Button.Pressed, "#health-check-btn")
    def run_health_check(self) -> None:
        """Run health check on all proxies."""
        self._health_check_cancelled = False
        self.health_check_async()

    @on(Button.Pressed, "#cancel-health-btn")
    def cancel_health_check(self) -> None:
        """Cancel ongoing health check."""
        self._health_check_cancelled = True
        try:
            status_label = self.query_one("#health-status", Label)
            status_label.update("⚠️ Health check cancelled")
        except Exception:
            pass

    @work(exclusive=True)
    async def health_check_async(self) -> None:
        """Async worker to run health checks."""
        status_label = self.query_one("#health-status", Label)
        progress_bar = self.query_one("#health-progress", ProgressBar)

        proxies = self.rotator.pool.get_all_proxies()
        if not proxies:
            status_label.update("❌ No proxies to check")
            return

        total = len(proxies)
        healthy = 0
        degraded = 0
        unhealthy = 0
        dead = 0

        status_label.update(f"🔄 Checking {total} proxies...")
        progress_bar.update(total=total, progress=0)

        for i, proxy in enumerate(proxies):
            if self._health_check_cancelled:
                break

            try:
                # Validate proxy
                proxy_dicts = [{"url": str(proxy.url)}]
                results = await self.validator.validate_batch(proxy_dicts)

                if results and results[0].get("valid", False):
                    # Update health in pool
                    proxy.record_success(results[0].get("latency_ms", 100))
                    healthy += 1
                else:
                    proxy.record_failure()
                    if proxy.health_status == HealthStatus.DEAD:
                        dead += 1
                    elif proxy.health_status == HealthStatus.UNHEALTHY:
                        unhealthy += 1
                    else:
                        degraded += 1

            except Exception:
                proxy.record_failure()
                unhealthy += 1

            progress_bar.update(progress=i + 1)

        if not self._health_check_cancelled:
            status_label.update(
                f"✅ Check complete: {healthy} healthy, {degraded} degraded, "
                f"{unhealthy} unhealthy, {dead} dead"
            )
        self.refresh_all_data()

    @on(Button.Pressed, "#reset-all-cb-btn")
    def reset_all_circuit_breakers(self) -> None:
        """Reset all circuit breakers."""
        try:
            states = self.rotator.get_circuit_breaker_states()
            for proxy_id in states:
                self.rotator.reset_circuit_breaker(proxy_id)

            self.notify("All circuit breakers reset", severity="information")
            self.refresh_circuit_breakers()
        except Exception as e:
            self.notify(f"Failed to reset: {e}", severity="error")

    @on(Button.Pressed, "#test-detail-proxy-btn")
    def test_proxy_from_details(self) -> None:
        """Test proxy from details modal."""
        screen = self.screen
        if isinstance(screen, ProxyDetailsScreen):
            proxy = screen.proxy
            # Set the test URL input and switch to test tab
            self.pop_screen()

            try:
                url_input = self.query_one("#test-url", Input)
                url_input.value = "https://httpbin.org/ip"

                tabs = self.query_one(TabbedContent)
                tabs.active = "test"

                self.notify(f"Testing proxy: {str(proxy.url)[:40]}...", severity="information")
            except Exception:
                pass


def run_tui(rotator: ProxyRotator | None = None) -> None:
    """Run the TUI application."""
    app = ProxyWhirlTUI(rotator=rotator)
    app.run()
