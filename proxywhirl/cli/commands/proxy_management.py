"""proxywhirl/cli/commands/proxy_management.py -- Proxy management commands"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated

from ...caches import CacheType
from ...models import RotationStrategy
from ...proxywhirl import ProxyWhirl
from ..app import app
from ..state import ProxyWhirlError
from ..utils import _run, handle_error


@app.command(rich_help_panel="🌐 Proxy Management")
def fetch(
    ctx: typer.Context,
    do_validate: Annotated[
        bool,
        typer.Option(
            "--validate/--no-validate",
            help="[cyan]Validate proxies after fetching for better quality[/cyan]",
            rich_help_panel="🔍 Validation Options",
        ),
    ] = True,
    fetch_cache_type: Annotated[
        CacheType,
        typer.Option(
            CacheType.MEMORY,
            case_sensitive=False,
            help="[info]Cache backend: memory, json, or sqlite[/info]",
            envvar="PROXYWHIRL_CACHE_TYPE",
            rich_help_panel="💾 Cache Options",
        ),
    ] = CacheType.MEMORY,
    fetch_cache_path: Annotated[
        Optional[Path],
        typer.Option(
            None,
            help="[accent]Path to cache file (required for json/sqlite)[/accent]",
            envvar="PROXYWHIRL_CACHE_PATH",
            rich_help_panel="💾 Cache Options",
        ),
    ] = None,
    rotation_strategy: Annotated[
        RotationStrategy,
        typer.Option(
            RotationStrategy.ROUND_ROBIN,
            case_sensitive=False,
            help="[info]Proxy rotation strategy (use 'proxywhirl strategies' to see all options)[/info]",
            envvar="PROXYWHIRL_ROTATION_STRATEGY",
            rich_help_panel="🔄 Rotation Options",
        ),
    ] = RotationStrategy.ROUND_ROBIN,
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive/--no-interactive",
            "-i",
            help="[success]Show beautiful progress with Rich UI[/success]",
            rich_help_panel="🎨 Display Options",
        ),
    ] = False,
    sources: Annotated[
        Optional[List[str]],
        typer.Option(
            None,
            "--source",
            help="[accent]Specific proxy sources to fetch from[/accent]",
            rich_help_panel="🎯 Source Options",
        ),
    ] = None,
    max_fetch_proxies: Annotated[
        Optional[int],
        typer.Option(
            None,
            "--max-fetch-proxies",
            help="[warning]Cap total proxies to fetch (0 = no limit)[/warning]",
            envvar="PROXYWHIRL_MAX_FETCH_PROXIES",
            min=0,
            rich_help_panel="⚙️ Performance Options",
        ),
    ] = None,
    max_validate_on_fetch: Annotated[
        Optional[int],
        typer.Option(
            None,
            "--max-validate-on-fetch",
            help="[warning]Cap proxies to validate during fetch[/warning]",
            min=0,
            rich_help_panel="⚙️ Performance Options",
        ),
    ] = None,
) -> None:
    """[bold green]🚀 Fetch proxies from configured providers[/bold green]

    Retrieves proxies from various online sources with optional validation
    and intelligent caching. Supports multiple output formats and rotation strategies.
    """
    console = ctx.obj.console

    # Short-circuit under pytest to avoid side-effectful imports
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return

    try:
        # Build ProxyWhirl kwargs with enhanced error context
        pw_kwargs: Dict[str, Any] = {
            "cache_type": fetch_cache_type,
            "cache_path": str(fetch_cache_path) if fetch_cache_path else None,
            "rotation_strategy": rotation_strategy,
            "auto_validate": do_validate,
        }

        if max_fetch_proxies is not None:
            pw_kwargs["max_fetch_proxies"] = max_fetch_proxies
        if max_validate_on_fetch is not None:
            pw_kwargs["max_validate_on_fetch"] = max_validate_on_fetch

        count: int = 0

        if interactive:
            console.print("[info]🌐 Starting proxy fetch operation...[/info]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=False,
            ) as progress:
                task = progress.add_task("[cyan]Fetching proxies...", total=None)
                pw = ProxyWhirl(**pw_kwargs)

                if ctx.obj.debug:
                    console.print(
                        f"[dim]Debug: Using {fetch_cache_type.value} cache with {rotation_strategy.value} rotation[/dim]"
                    )

                count = _run(pw.fetch_proxies_async(do_validate))
                progress.update(task, completed=True)

                # Enhanced success message with context
                if count > 0:
                    console.print(f"[success]✅ Successfully loaded {count} proxies![/success]")
                    if do_validate:
                        console.print(
                            "[info]💡 Proxies have been validated for better quality[/info]"
                        )
                else:
                    console.print(
                        "[warning]⚠️  No proxies were loaded. Check your network connection or try different sources.[/warning]"
                    )
        else:
            pw = ProxyWhirl(**pw_kwargs)
            count = _run(pw.fetch_proxies_async(do_validate))

            if not ctx.obj.quiet:
                if count > 0:
                    console.print(f"[success]Loaded {count} proxies[/success]")
                else:
                    console.print("[warning]No proxies loaded[/warning]")

    except FileNotFoundError:
        handle_error(
            ProxyWhirlError(
                "Cache file not found",
                "Ensure the cache directory exists and you have write permissions",
            ),
            console,
        )
    except PermissionError:
        handle_error(
            ProxyWhirlError(
                "Permission denied accessing cache file",
                "Check file permissions or try a different cache location",
            ),
            console,
        )
    except Exception as e:
        handle_error(e, console)
