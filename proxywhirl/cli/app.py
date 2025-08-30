"""proxywhirl/cli/app.py -- Main Typer app setup and configuration"""

from __future__ import annotations

import typer
from rich.theme import Theme

from .callbacks import main_callback

# Enhanced ProxyWhirl theme for better UX
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

app = typer.Typer(
    help="[bold]ProxyWhirl CLI[/bold]: [italic]Advanced proxy management toolkit[/italic]",
    rich_markup_mode="rich",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    pretty_exceptions_enable=False,
)

# Set the main callback
app.callback()(main_callback)
