"""proxywhirl/cli/commands/interactive.py -- Interactive mode commands"""

from __future__ import annotations

import typer

from ..app import app


@app.command(name="tui", rich_help_panel="🖥️ Interactive Mode")
def run_tui(ctx: typer.Context) -> None:
    """[bold]🖥️ Launch interactive terminal UI[/bold]
    
    Start the beautiful ProxyWhirl TUI for managing proxies interactively.
    """
    console = ctx.obj.console
    
    try:
        from ...tui import run_tui
        console.print("[info]🚀 Launching ProxyWhirl TUI...[/info]")
        run_tui()
    except ImportError as e:
        console.print(f"[error]❌ TUI not available: {e}[/error]")
        console.print("[warning]💡 Try: pip install 'proxywhirl[tui]'[/warning]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[error]❌ Failed to launch TUI: {e}[/error]")
        raise typer.Exit(1)
