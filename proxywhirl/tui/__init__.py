"""proxywhirl.tui -- Beautiful, advanced TUI package for ProxyWhirl

A modern, user-friendly terminal interface built with Textual that exposes all
ProxyWhirl functionality through an intuitive dashboard. Features include:
- Real-time proxy management with live updates
- Advanced filtering, sorting, and export capabilities
- Source configuration and health monitoring
- Beautiful, responsive UI with dark/light themes
- Async operation with progress tracking
- Settings management and cache configuration

Usage:
    python -m proxywhirl.tui
    
Package Structure:
    - app: Main TUI application class
    - widgets: Reusable UI components (stats, tables, progress)
    - modals: Modal dialog components (export, settings, health)
    - styles: CSS styling constants
"""

from .app import ProxyWhirlTUI
from .widgets import ProxyDataTable, ProxyStatsWidget

__all__ = ["ProxyWhirlTUI", "ProxyDataTable", "ProxyStatsWidget", "run_tui"]


def run_tui() -> None:
    """Run the ProxyWhirl TUI application."""
    app = ProxyWhirlTUI()
    app.run()
