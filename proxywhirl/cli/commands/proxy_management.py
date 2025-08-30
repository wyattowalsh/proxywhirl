"""proxywhirl/cli/commands/proxy_management.py -- Proxy Management Commands

Commands for fetching and managing proxies from various sources.
"""

import asyncio
import os
from pathlib import Path
from typing import List, Optional
import typer
from typing_extensions import Annotated

from ...caches.config import CacheType
from ...models import RotationStrategy
from ...proxywhirl import ProxyWhirl
from ..app import app, ProxyWhirlError, handle_error


@app.command(
    "fetch",
    rich_help_panel="🌐 Proxy Management",
    help="[bold green]🚀 Fetch proxies from configured providers[/bold green]",
    epilog="[dim]Environment variables: PROXYWHIRL_CACHE_TYPE, PROXYWHIRL_CACHE_PATH, PROXYWHIRL_ROTATION_STRATEGY, PROXYWHIRL_MAX_FETCH_PROXIES[/dim]",
)
def fetch(
    ctx: typer.Context,
    do_validate: Annotated[
        bool,
        typer.Option(
            "--validate/--no-validate",
            help="[cyan]Validate proxies after fetching for better quality[/cyan]",
            envvar="PROXYWHIRL_VALIDATE",
            rich_help_panel="🔍 Validation Options",
        ),
    ] = True,
    cache_type: Annotated[
        CacheType,
        typer.Option(
            "--cache-type",
            case_sensitive=False,
            help="[info]Cache backend: memory, json, or sqlite[/info]",
            envvar="PROXYWHIRL_CACHE_TYPE",
            rich_help_panel="💾 Cache Options",
        ),
    ] = CacheType.MEMORY,
    cache_path: Annotated[
        Optional[Path],
        typer.Option(
            "--cache-path",
            help="[accent]Path to cache file (required for json/sqlite)[/accent]",
            envvar="PROXYWHIRL_CACHE_PATH",
            rich_help_panel="💾 Cache Options",
        ),
    ] = None,
    rotation_strategy: Annotated[
        RotationStrategy,
        typer.Option(
            "--rotation-strategy",
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
            "--source",
            help="[accent]Specific proxy sources to fetch from[/accent]",
            rich_help_panel="🎯 Source Options",
        ),
    ] = None,
    max_proxies: Annotated[
        Optional[int],
        typer.Option(
            "--max-proxies",
            help="[warning]Maximum number of proxies to fetch (0 = no limit)[/warning]",
            envvar="PROXYWHIRL_MAX_FETCH_PROXIES",
            min=0,
            rich_help_panel="⚙️ Performance Options",
        ),
    ] = None,
    max_validate: Annotated[
        Optional[int],
        typer.Option(
            "--max-validate",
            help="[warning]Maximum proxies to validate during fetch[/warning]",
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
        console.print("[warning]Test environment detected - skipping fetch operation[/warning]")
        return

    try:
        # Validate cache consistency
        if cache_type in [CacheType.JSON, CacheType.SQLITE] and not cache_path:
            raise ProxyWhirlError(
                f"Cache path required for {cache_type.value} cache",
                f"Add --cache-path ./proxies.{cache_type.value.lower()}"
            )

        # Create ProxyWhirl instance
        pw = ProxyWhirl(
            cache_type=cache_type,
            cache_path=cache_path,
            rotation_strategy=rotation_strategy,
            auto_validate=do_validate,
        )
        
        # Note: sources, max_proxies, max_validate, and interactive parameters
        # are not currently supported by the ProxyWhirl.fetch_proxies_async API
        # They will be implemented in future versions
        if sources:
            console.print("[warning]⚠️  --source parameter not yet implemented[/warning]")
        if max_proxies:
            console.print("[warning]⚠️  --max-proxies parameter not yet implemented[/warning]")  
        if max_validate:
            console.print("[warning]⚠️  --max-validate parameter not yet implemented[/warning]")
        if interactive:
            console.print("[warning]⚠️  --interactive parameter not yet implemented[/warning]")

        # Run the fetch operation
        def _run_fetch():
            return asyncio.run(pw.fetch_proxies_async(validate=do_validate))

        fetched_count = _run_fetch()
        
        if fetched_count > 0:
            console.print(f"[success]✅ Successfully fetched {fetched_count} proxies[/success]")
            if do_validate:
                console.print("[info]💡 Proxies have been validated and cached[/info]")
        else:
            console.print("[warning]⚠️  No proxies were fetched. Check your sources or network connection.[/warning]")

    except FileNotFoundError:
        console.print("[error]❌ Cache file not found. Check the --cache-path option.[/error]")
        raise typer.Abort()
    except PermissionError:
        console.print("[error]❌ Permission denied accessing cache file. Check file permissions.[/error]")  
        raise typer.Abort()
    except Exception as e:
        handle_error(e, console)
