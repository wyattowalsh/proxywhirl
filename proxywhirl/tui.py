"""proxywhirl/tui.py -- Beautiful, advanced TUI for ProxyWhirl

This module has been refactored into a proper package structure:
- proxywhirl.tui.app: Main TUI application class
- proxywhirl.tui.widgets: Reusable UI components
- proxywhirl.tui.modals: Modal dialog components  
- proxywhirl.tui.styles: CSS styling constants

Usage:
    python -m proxywhirl.tui
"""

# Import the run_tui function from the TUI package
from .tui import run_tui

__all__ = ["run_tui"]

if __name__ == "__main__":
    run_tui()
