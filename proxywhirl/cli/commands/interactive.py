"""proxywhirl/cli/commands/interactive.py -- Interactive Commands

Commands for launching interactive interfaces.
"""

from ..app import app


@app.command(rich_help_panel="🖥️ Interactive Mode")
def tui() -> None:
    """Launch the ProxyWhirl TUI (Terminal User Interface)"""
    try:
        from ...tui import main as tui_main
        tui_main()
    except ImportError:
        from rich.console import Console
        console = Console()
        console.print("[error]❌ TUI module not available[/error]")
        console.print("[info]💡 The TUI may not be fully implemented yet[/info]")
    except Exception as e:
        from rich.console import Console
        console = Console()
        console.print(f"[error]❌ Failed to start TUI: {e}[/error]")


@app.command(name="interactive", rich_help_panel="🖥️ Interactive Mode")
def interactive() -> None:
    """Launch interactive mode (alias for tui)"""
    tui()
