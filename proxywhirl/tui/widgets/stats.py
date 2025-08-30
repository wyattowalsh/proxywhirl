"""Statistics and progress widgets for the TUI."""

from __future__ import annotations

import time
from typing import Any, List, Optional

from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Label,
    LoadingIndicator,
    ProgressBar,
    Rule,
    Sparkline,
    Static,
)

from ...logger import get_logger

logger = get_logger(__name__)


class ProxyStatsWidget(Static):
    """Advanced widget displaying real-time proxy statistics with rich visualizations."""

    total_proxies: reactive[int] = reactive(0)
    active_proxies: reactive[int] = reactive(0)
    last_updated: reactive[str] = reactive("Never")
    success_rate: reactive[float] = reactive(0.0)
    response_times: reactive[List[float]] = reactive(default=list)
    health_scores: reactive[List[float]] = reactive(default=list)
    throughput_history: reactive[List[float]] = reactive(default=list)

    def compose(self):
        with Vertical():
            yield Static("📊 Proxy Health Dashboard", classes="stats-title")
            yield Rule()

            # Enhanced stats grid with health indicators
            with Vertical(id="stats-content"):
                yield Static("🔄 Loading stats...", id="stats-text")

                # Success rate with health emoji
                with Horizontal():
                    yield Static("🟢", id="health-emoji")
                    yield Label("Success Rate:")
                yield ProgressBar(id="success-rate-bar", show_eta=False)

                # Multi-metric sparklines section
                yield Label("📈 Response Time Trend (ms):")
                yield Sparkline([], id="response-sparkline", classes="sparkline-response")

                yield Label("💓 Health Score Trend:")
                yield Sparkline([], id="health-sparkline", classes="sparkline-health")

                yield Label("⚡ Throughput Trend (/s):")
                yield Sparkline([], id="throughput-sparkline", classes="sparkline-throughput")

                # Real-time metrics bar
                with Horizontal(classes="metrics-row"):
                    yield Static("📊 0ms", id="avg-response")
                    yield Static("💓 0.00", id="current-health") 
                    yield Static("⚡ 0.0/s", id="current-throughput")

            yield Rule()

            # Enhanced status with trend indicators
            with Horizontal(classes="status-row"):
                yield LoadingIndicator(id="loading-indicator")
                yield Static("Ready", id="status-text", classes="status-ready")
                yield Static("", id="trend-indicator")

    def get_health_status_emoji(self, success_rate: float) -> str:
        """Get health status emoji based on success rate"""
        if success_rate >= 0.9:
            return "🟢"  # Excellent
        elif success_rate >= 0.7:
            return "🟡"  # Good
        elif success_rate >= 0.5:
            return "🟠"  # Fair
        else:
            return "🔴"  # Poor

    def get_health_trend_arrow(self, current: float, history: List[float]) -> str:
        """Get trend arrow based on recent health history"""
        if len(history) < 2:
            return ""

        recent_avg = sum(history[-5:]) / min(5, len(history))
        older_avg = (
            sum(history[-10:-5]) / min(5, len(history) - 5) if len(history) > 5 else recent_avg
        )

        if recent_avg > older_avg + 0.05:  # 5% improvement
            return "↗️"
        elif recent_avg < older_avg - 0.05:  # 5% degradation
            return "↘️"
        else:
            return "➡️"  # Stable

    def watch_total_proxies(self, old_total: int, new_total: int) -> None:
        """React to total proxy changes."""
        self.update_stats()

    def watch_active_proxies(self, old_active: int, new_active: int) -> None:
        """React to active proxy changes."""
        self.update_stats()
        self.update_success_rate()

    def watch_last_updated(self, old_updated: str, new_updated: str) -> None:
        """React to last updated changes."""
        self.update_stats()

    def watch_success_rate(self, rate: float) -> None:
        # Update progress bar with color coding
        progress_bar = self.query_one("#success-rate-bar", ProgressBar)
        progress_bar.progress = rate * 100

        # Update health emoji
        health_emoji = self.query_one("#health-emoji", Static)
        health_emoji.update(self.get_health_status_emoji(rate))

        # Update trend indicator
        trend_indicator = self.query_one("#trend-indicator", Static)
        trend_arrow = self.get_health_trend_arrow(rate, list(self.health_scores))
        trend_indicator.update(trend_arrow)

    def watch_response_times(self, times: List[float]) -> None:
        if times:
            sparkline = self.query_one("#response-sparkline", Sparkline)
            # Convert to milliseconds and show last 30 values with enhanced scaling
            ms_times = [t * 1000 for t in times[-30:]]
            sparkline.data = ms_times

            # Update average response time display
            avg_response = self.query_one("#avg-response", Static)
            avg_time = sum(ms_times) / len(ms_times) if ms_times else 0
            avg_response.update(f"📊 {avg_time:.1f}ms")

    def watch_health_scores(self, scores: List[float]) -> None:
        """Update health score sparkline and current display"""
        if scores:
            sparkline = self.query_one("#health-sparkline", Sparkline)
            # Scale health scores (0-1) to better visualization (0-100)
            scaled_scores = [s * 100 for s in scores[-30:]]
            sparkline.data = scaled_scores

            # Update current health score
            current_health = self.query_one("#current-health", Static)
            latest_score = scores[-1] if scores else 0.0
            current_health.update(f"💓 {latest_score:.2f}")

    def watch_throughput_history(self, throughput: List[float]) -> None:
        """Update throughput sparkline and current display"""
        if throughput:
            sparkline = self.query_one("#throughput-sparkline", Sparkline)
            sparkline.data = throughput[-30:]

            # Update current throughput
            current_throughput = self.query_one("#current-throughput", Static)
            latest_throughput = throughput[-1] if throughput else 0.0
            current_throughput.update(f"⚡ {latest_throughput:.1f}/s")

    def update_stats(self) -> None:
        stats_content = self.query_one("#stats-text", Static)
        inactive = max(0, self.total_proxies - self.active_proxies)

        # Enhanced stats with emoji indicators
        health_emoji = self.get_health_status_emoji(self.success_rate)

        content = f"""
📈 Total: [bold blue]{self.total_proxies}[/bold blue]
✅ Active: [bold green]{self.active_proxies}[/bold green] {health_emoji}
❌ Inactive: [bold red]{inactive}[/bold red]
🕒 Updated: [dim]{self.last_updated}[/dim]
        """.strip()
        stats_content.update(content)

    def update_success_rate(self) -> None:
        if self.total_proxies > 0:
            new_rate = self.active_proxies / self.total_proxies
            self.success_rate = new_rate

            # Add to health history for trend analysis
            current_health = list(self.health_scores)
            current_health.append(new_rate)
            self.health_scores = current_health[-50:]  # Keep last 50 measurements
        else:
            self.success_rate = 0.0

    def set_loading(self, loading: bool) -> None:
        """Set loading state with enhanced visual indicators."""
        loading_indicator = self.query_one("#loading-indicator", LoadingIndicator)
        status_text = self.query_one("#status-text", Static)

        if loading:
            loading_indicator.display = True
            status_text.update("Working...")
            status_text.remove_class("status-ready")
            status_text.add_class("status-loading")
        else:
            loading_indicator.display = False
            status_text.update("Ready")
            status_text.remove_class("status-loading")
            status_text.add_class("status-ready")

    def add_response_time(self, time: float) -> None:
        """Add a new response time measurement with enhanced tracking."""
        current_times = list(self.response_times)
        current_times.append(time)
        # Keep only last 50 measurements for better performance
        self.response_times = current_times[-50:]

    def add_health_score(self, score: float) -> None:
        """Add a new health score measurement."""
        current_scores = list(self.health_scores)
        current_scores.append(score)
        self.health_scores = current_scores[-50:]

    def add_throughput_measurement(self, throughput: float) -> None:
        """Add a new throughput measurement."""
        current_throughput = list(self.throughput_history)
        current_throughput.append(throughput)
        self.throughput_history = current_throughput[-50:]

    def update_real_time_metrics(
        self, response_time: Optional[float] = None, health_score: Optional[float] = None, throughput: Optional[float] = None
    ):
        """Batch update multiple metrics for real-time display."""
        if response_time is not None:
            self.add_response_time(response_time)
        if health_score is not None:
            self.add_health_score(health_score)
        if throughput is not None:
            self.add_throughput_measurement(throughput)


class EnhancedProgressWidget(Static):
    """Progress widget with ETA and throughput metrics."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.start_time: Optional[float] = None
        self.completed_items = 0
        self.total_items = 0

    def start_progress(self, total: int, operation: str) -> None:
        """Start progress tracking."""
        self.start_time = time.time()
        self.total_items = total
        self.completed_items = 0
        self.update(f"⏳ Starting {operation}...")

    def update_progress(self, completed: int, current_item: str = "") -> None:
        """Update progress with ETA calculation."""
        if not self.start_time:
            return

        self.completed_items = completed
        elapsed = time.time() - self.start_time

        if completed > 0:
            rate = completed / elapsed
            remaining = self.total_items - completed
            eta = remaining / rate if rate > 0 else 0

            percentage = (completed / self.total_items) * 100

            self.update(
                f"⚡ {completed}/{self.total_items} ({percentage:.1f}%) "
                f"| Rate: {rate:.1f}/s | ETA: {eta:.0f}s"
                f"{f' | {current_item}' if current_item else ''}"
            )
        else:
            self.update(f"⏳ {completed}/{self.total_items}")

    def complete_progress(self, message: str = "✅ Complete!") -> None:
        """Mark progress as complete."""
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.update(f"{message} (took {elapsed:.1f}s)")
            self.update(f"{message} (took {elapsed:.1f}s)")
