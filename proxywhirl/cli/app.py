"""proxywhirl/cli/app.py -- Main Typer app configuration and setup

Main CLI application with context management, themes, and global configuration.
"""

from __future__ import annotations
import traceback
from pathlib import Path
from typing import Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
import typer
from typing_extensions import Annotated

from ..config import ProxyWhirlSettings
from ..caches.config import CacheType

# ProxyWhirl theme for better UX
PROXYWHIRL_THEME = Theme(
    {
        "proxy": "cyan bold",
        "success": "green bold",
        "warning": "yellow bold",
        "error": "red bold",
        "info": "blue",
        "accent": "magenta",
        "dim": "dim white",
    }
)


class ProxyWhirlState:
    """Shared state across CLI commands for better context management"""

    def __init__(self):
        self.console = Console(theme=PROXYWHIRL_THEME)
        self.debug = False
        self.quiet = False
        self.cache_type = CacheType.MEMORY
        self.cache_path: Optional[Path] = None
        self.config: Optional[ProxyWhirlSettings] = None

    def load_config_file(self, config_path: Optional[Path]) -> None:
        """Load configuration from file."""
        try:
            if config_path and config_path.exists():
                self.config = ProxyWhirlSettings.from_yaml(config_path)
                if self.debug:
                    self.console.print(f"[success]✅ Loaded config from {config_path}[/success]")
        except Exception as e:
            raise ProxyWhirlError(
                f"Failed to load config from {config_path}: {e}",
                "Check the YAML syntax and file permissions"
            )

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with fallback to default."""
        if self.config is None:
            return default
        return getattr(self.config, key, default)


class ProxyWhirlError(Exception):
    """Custom exception with Rich formatting support"""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)


def handle_error(error: Exception, console: Console) -> None:
    """Enhanced centralized error handling with Typer best practices and Rich formatting."""
    if isinstance(error, ProxyWhirlError):
        console.print(
            Panel(
                f"[error]❌ {error.message}[/error]"
                + (
                    f"\n[warning]💡 Suggestion: {error.suggestion}[/warning]"
                    if error.suggestion
                    else ""
                ),
                title="ProxyWhirl Error",
                border_style="red",
            )
        )
        raise typer.Abort()
    elif isinstance(error, (FileNotFoundError, PermissionError)):
        file_msg = str(error)
        console.print(
            Panel(
                f"[error]❌ File System Error[/error]\n[dim]{file_msg}[/dim]",
                title="File Access Problem", 
                border_style="red",
            )
        )
        if isinstance(error, PermissionError):
            console.print("[info]💡 Try running with sudo or check file permissions[/info]")
        else:
            console.print("[info]💡 Check if the file path exists and is accessible[/info]")
        raise typer.Abort()
    elif isinstance(error, KeyboardInterrupt):
        console.print("\n[warning]⚠️  Operation cancelled by user[/warning]")
        raise typer.Abort()
    elif isinstance(error, ConnectionError):
        console.print(
            Panel(
                "[error]❌ Network Connection Error[/error]\n"
                "[dim]Unable to connect to proxy sources or validation targets[/dim]",
                title="Network Problem",
                border_style="red", 
            )
        )
        console.print("[info]💡 Check your internet connection and firewall settings[/info]")
        raise typer.Abort()
    else:
        # Generic error with stack trace for debugging
        console.print(
            Panel(
                f"[error]❌ Unexpected Error: {type(error).__name__}[/error]\n"
                f"[dim]{str(error)}[/dim]",
                title="Internal Error",
                border_style="red",
            )
        )
        console.print("[info]💡 This might be a bug. Please report it with the following details:[/info]")
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Abort()


# Main Typer app configuration
app = typer.Typer(
    help="[bold]ProxyWhirl CLI[/bold]: [italic]Advanced proxy management toolkit[/italic] 🌐",
    rich_markup_mode="rich",
    no_args_is_help=True,
    context_settings={
        "help_option_names": ["-h", "--help"],
        "max_content_width": 120,
        "terminal_width": None,
    },
    pretty_exceptions_enable=False,
    add_completion=True,
    epilog="""
[dim]Examples:[/dim]
  [cyan]proxywhirl fetch --validate --interactive[/cyan]     # Fetch & validate with progress
  [cyan]proxywhirl list --healthy-only --limit 10[/cyan]     # Show top 10 healthy proxies
  [cyan]proxywhirl export --format json --healthy-only[/cyan] # Export healthy proxies as JSON
  [cyan]proxywhirl get --rotation-strategy random[/cyan]      # Get random proxy
  [cyan]proxywhirl tui[/cyan]                                # Launch interactive TUI
  
[dim]Environment Variables:[/dim]
  [yellow]PROXYWHIRL_CACHE_TYPE[/yellow], [yellow]PROXYWHIRL_CACHE_PATH[/yellow], [yellow]PROXYWHIRL_VALIDATE[/yellow]
    """,
)


@app.callback()
def main_callback(
    ctx: typer.Context,
    config: Annotated[
        Optional[Path],
        typer.Option(
            None,
            "--config",
            "-c",
            help="[accent]Path to YAML configuration file[/accent]",
            exists=False,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ] = None,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="[info]Enable verbose output[/info]")
    ] = False,
    quiet: Annotated[
        bool, typer.Option("--quiet", "-q", help="[dim]Suppress non-essential output[/dim]")
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version/--no-version",
            help="[dim]Show version and exit[/dim]",
        ),
    ] = False,
) -> None:
    """[bold]ProxyWhirl[/bold] - [italic]Advanced proxy management toolkit[/italic]

    A modern, high-performance proxy management system with intelligent rotation,
    validation, and rich reporting capabilities. Supports YAML configuration files
    for streamlined workflow management.
    """
    if version:
        from .. import __version__
        console = Console(theme=PROXYWHIRL_THEME)
        console.print(f"[success]ProxyWhirl version {__version__}[/success]")
        raise typer.Exit()
        
    if verbose and quiet:
        console = Console(theme=PROXYWHIRL_THEME)
        console.print("[error]❌ Cannot use both --verbose and --quiet options[/error]")
        raise typer.Abort()

    # Initialize context-based state instead of global state
    state = ProxyWhirlState()
    state.debug = verbose
    state.quiet = quiet
    
    # Load configuration file if provided
    try:
        state.load_config_file(config)
    except ProxyWhirlError as e:
        handle_error(e, state.console)

    # Provide feedback for verbose mode
    if verbose:
        state.console.print("[info]🔧 Verbose mode enabled[/info]")

    if quiet:
        state.console.quiet = True
        
    # Make state available to all commands via context
    ctx.obj = state


# Import commands to register them with the app
from . import commands

def main() -> None:
    """Main entry point for the CLI application."""
    app()


# For backwards compatibility
cli = app


if __name__ == "__main__":
    app()
