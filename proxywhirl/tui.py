"""
Terminal User Interface (TUI) for ProxyWhirl.

Full-featured TUI with proxy sourcing, validation, analytics, health monitoring,
exports, and configuration management.

## Features

- **Overview Tab**: Real-time metrics dashboard and proxy table with color-coded health status
- **Fetch & Validate**: Auto-fetch from 64+ proxy sources with batch validation
- **Export**: Save proxy lists in CSV, JSON, YAML, or plain text formats
- **Test**: Send HTTP requests (GET/POST/PUT/DELETE) through proxies
- **Analytics**: Statistics by protocol, country, and source

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
- F1: Show help

## Architecture

The TUI uses Textual framework with the following components:
- MetricsPanel: Reactive metrics display
- ProxyTable: DataTable with health status indicators
- SourceFetcherPanel: Multi-source proxy fetching
- ExportPanel: Multi-format export functionality
- StrategyPanel: Rotation strategy management
- RequestTesterPanel: HTTP request testing
- AnalyticsPanel: Statistics and insights
- ProxyControlPanel: Manual proxy management
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
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
    TabbedContent,
    TabPane,
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
    """Display real-time metrics."""

    total_proxies = reactive(0)
    active_proxies = reactive(0)
    healthy_proxies = reactive(0)
    degraded_proxies = reactive(0)
    unhealthy_proxies = reactive(0)
    total_requests = reactive(0)
    success_rate = reactive(0.0)
    avg_latency = reactive(0.0)

    def render(self) -> Text:
        """Render metrics display."""
        text = Text()
        text.append("📊 Metrics\n", style="bold cyan")
        text.append("─" * 40 + "\n", style="dim")

        text.append("Proxies: ", style="white")
        text.append(f"{self.total_proxies} total", style="bold")
        text.append(f" | {self.active_proxies} active", style="green")
        text.append(f" | {self.healthy_proxies} healthy\n", style="bold green")

        text.append(f"         {self.degraded_proxies} degraded", style="yellow")
        text.append(f" | {self.unhealthy_proxies} unhealthy\n", style="red")

        text.append("\nRequests: ", style="white")
        text.append(f"{self.total_requests}\n", style="bold")

        text.append("Success Rate: ", style="white")
        text.append(
            f"{self.success_rate:.1f}%\n",
            style="bold green" if self.success_rate > 80 else "bold yellow",
        )

        text.append("Avg Latency: ", style="white")
        text.append(f"{self.avg_latency:.0f}ms\n", style="bold")

        return text


class ProxyTable(DataTable):
    """DataTable widget for displaying proxies."""

    def on_mount(self) -> None:
        """Set up table columns."""
        self.add_column("URL", width=40)
        self.add_column("Protocol", width=10)
        self.add_column("Health", width=12)
        self.add_column("Latency", width=10)
        self.add_column("Success", width=10)
        self.add_column("Failures", width=10)
        self.add_column("Country", width=8)

    def update_proxies(self, proxies: list[Proxy]) -> None:
        """Update table with proxy data."""
        self.clear()

        for proxy in proxies:
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

            # Format latency
            latency_ms = proxy.average_response_time_ms or 0
            latency_text = Text(f"{latency_ms:.0f}ms")
            if latency_ms < 500:
                latency_text.stylize("green")
            elif latency_ms < 2000:
                latency_text.stylize("yellow")
            else:
                latency_text.stylize("red")

            self.add_row(
                str(proxy.url),
                str(proxy.protocol or "http"),
                health_text,
                latency_text,
                str(proxy.total_successes),
                str(proxy.total_failures),
                str(proxy.country_code or "N/A"),
            )


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
                yield Button("Export All", id="export-all-btn", variant="primary")
                yield Button("Export Healthy Only", id="export-healthy-btn", variant="success")

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

            yield Select(
                [
                    ("GET", "GET"),
                    ("POST", "POST"),
                    ("PUT", "PUT"),
                    ("DELETE", "DELETE"),
                ],
                id="test-method",
                value="GET",
            )

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


class ProxyWhirlTUI(App):
    """ProxyWhirl TUI Application."""

    TITLE = "ProxyWhirl - Proxy Rotation TUI"
    CSS_PATH = "tui.tcss"

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+r", "refresh", "Refresh"),
        ("ctrl+f", "fetch", "Fetch Proxies"),
        ("ctrl+e", "export", "Export"),
        ("ctrl+t", "test", "Test Request"),
        ("f1", "help", "Help"),
    ]

    def __init__(self, rotator: ProxyRotator | None = None):
        """Initialize TUI."""
        super().__init__()
        self.rotator = rotator or ProxyRotator()
        self.fetcher: ProxyFetcher | None = None
        self.validator = ProxyValidator()

    def compose(self) -> ComposeResult:
        """Create TUI layout."""
        yield Header()

        with TabbedContent(initial="overview"):
            with TabPane("Overview", id="overview"), Horizontal():
                with Vertical(classes="left-panel"):
                    yield MetricsPanel(id="metrics-panel")
                    yield StrategyPanel()

                with Vertical(classes="right-panel"), VerticalScroll():
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

        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.refresh_all_data()
        self.set_interval(5.0, self.auto_refresh)

    def auto_refresh(self) -> None:
        """Auto-refresh data every 5 seconds."""
        self.refresh_table()
        self.refresh_metrics()

    def refresh_all_data(self) -> None:
        """Refresh all data displays."""
        self.refresh_table()
        self.refresh_metrics()
        self.refresh_analytics()

    def refresh_table(self) -> None:
        """Refresh the proxy table."""
        table = self.query_one("#proxy-table", ProxyTable)
        proxies = self.rotator.pool.get_all_proxies()
        table.update_proxies(proxies)

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

        metrics.total_proxies = total
        metrics.active_proxies = active
        metrics.healthy_proxies = healthy
        metrics.degraded_proxies = degraded
        metrics.unhealthy_proxies = unhealthy
        metrics.total_requests = total_requests
        metrics.success_rate = success_rate
        metrics.avg_latency = avg_latency

    def refresh_analytics(self) -> None:
        """Refresh analytics display."""
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

        # Format output
        text = Text()
        text.append("Protocol Distribution:\n", style="bold cyan")
        for protocol, count in sorted(by_protocol.items()):
            pct = count / total * 100
            text.append(f"  {protocol}: {count} ({pct:.1f}%)\n", style="white")

        text.append("\nTop Countries:\n", style="bold cyan")
        for country, count in sorted(by_country.items(), key=lambda x: x[1], reverse=True)[:10]:
            pct = count / total * 100
            text.append(f"  {country}: {count} ({pct:.1f}%)\n", style="white")

        text.append("\nSources:\n", style="bold cyan")
        for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
            pct = count / total * 100
            text.append(f"  {source}: {count} ({pct:.1f}%)\n", style="white")

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

        # Select sources
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
            self.fetcher = ProxyFetcher(sources=sources[:10])  # Limit to 10 sources for demo
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

        output_static.update(f"🔄 Sending {method} request to {url}...")

        try:
            # Use rotator's request method
            if method == "GET":
                response = self.rotator.get(url)
            elif method == "POST":
                response = self.rotator.post(url, json={})
            elif method == "PUT":
                response = self.rotator.put(url, json={})
            elif method == "DELETE":
                response = self.rotator.delete(url)
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

    def action_help(self) -> None:
        """Show help message."""
        self.notify(
            "ProxyWhirl TUI\n\n"
            "Shortcuts:\n"
            "Ctrl+C - Quit\n"
            "Ctrl+R - Refresh\n"
            "Ctrl+F - Go to Fetch tab\n"
            "Ctrl+E - Go to Export tab\n"
            "Ctrl+T - Go to Test tab\n"
            "F1 - This help\n",
            title="Help",
            timeout=10,
        )


def run_tui(rotator: ProxyRotator | None = None) -> None:
    """Run the TUI application."""
    app = ProxyWhirlTUI(rotator=rotator)
    app.run()
