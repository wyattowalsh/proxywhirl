"""proxywhirl/cli/app.py -- Main Typer app setup and configuration"""

from __future__ import annotations

import typer

from .callbacks import main_callback

app = typer.Typer(
    help="[bold]ProxyWhirl CLI[/bold]: [italic]Advanced proxy management toolkit[/italic]",
    rich_markup_mode="rich",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    pretty_exceptions_enable=False,
)

# Set the main callback
app.callback()(main_callback)
