"""proxywhirl/cli/callbacks.py -- Typer callback functions"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from .state import ProxyWhirlState


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
    
    A modern, high-performance proxy management system for rotating proxies.
    """
    if version:
        from .. import __version__

        print(f"ProxyWhirl version {__version__}")
        raise typer.Exit()

    # Create and configure CLI state
    state = ProxyWhirlState()
    state.debug = verbose
    state.quiet = quiet
    
    # Load configuration if provided
    if config:
        state.load_config_file(config)
    
    # Make state available to all commands via context
    ctx.obj = state
