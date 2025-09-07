"""proxywhirl/cli/commands/data_display.py -- Data display commands"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer
from rich.table import Table
from typing_extensions import Annotated

from ...caches import CacheType
from ...models import Proxy
from ...proxywhirl import ProxyWhirl
from ..app import app
from ..state import ProxyWhirlError
from ..utils import handle_error


@app.command(name="list", rich_help_panel="📋 Data Display")
def list_proxies(
    ctx: typer.Context,
    list_cache_type: Annotated[
        CacheType,
        typer.Option(
            CacheType.MEMORY,
            case_sensitive=False,
            help="[info]Cache backend to read from[/info]",
            rich_help_panel="💾 Cache Options",
        ),
    ] = CacheType.MEMORY,
    cache_path: Annotated[
        Optional[Path],
        typer.Option(
            None,
            help="[accent]Path to cache file (required for json/sqlite)[/accent]",
            rich_help_panel="💾 Cache Options",
        ),
    ] = None,
    json_out: Annotated[
        bool,
        typer.Option(
            "--json/--no-json",
            help="[info]Output JSON instead of a beautiful table[/info]",
            rich_help_panel="📤 Output Options",
        ),
    ] = False,
    limit: Annotated[
        Optional[int],
        typer.Option(
            None,
            "--limit",
            "-l",
            help="[cyan]Limit number of rows displayed[/cyan]",
            min=1,
            rich_help_panel="📤 Output Options",
        ),
    ] = None,
    healthy_only: Annotated[
        bool,
        typer.Option(
            True,  # Default to healthy only for better user experience
            "--healthy-only/--include-unhealthy",
            help="[success]🟢 Only show healthy proxies (default: True for cleaner output)[/success]",
            rich_help_panel="✅ Quality Filters",
        ),
    ] = True,
) -> None:
    """[bold]📋 List cached proxies with beautiful formatting[/bold]

    Display your proxy cache in a beautifully formatted table with status indicators,
    performance metrics, and helpful summaries. Supports JSON output for scripting.
    """
    console = ctx.obj.console

    try:
        if list_cache_type in [CacheType.JSON, CacheType.SQLITE] and not cache_path:
            handle_error(
                ProxyWhirlError(
                    f"Cache path required for {list_cache_type.value} cache",
                    f"Add: --cache-path ./proxies.{list_cache_type.value.lower()}",
                ),
                console,
            )

        pw = ProxyWhirl(
            cache_type=list_cache_type,
            cache_path=str(cache_path) if cache_path else None,
        )

        # Get all proxies and filter them
        all_proxies = pw.list_proxies()

        # Apply healthy filter if requested
        if healthy_only:
            filtered_proxies = [
                p for p in all_proxies if getattr(p, "status", "unknown") == "active"
            ]

            # Inform user about filtering
            total_count = len(all_proxies)
            healthy_count = len(filtered_proxies)
            unhealthy_count = total_count - healthy_count

            if not ctx.obj.quiet and total_count > 0:
                console.print(
                    f"[info]🟢 Showing {healthy_count} healthy proxies (filtered out {unhealthy_count} unhealthy)[/info]"
                )
                if unhealthy_count > 0:
                    console.print(
                        f"[dim]💡 Use --include-unhealthy to see all {total_count} proxies[/dim]"
                    )
        else:
            filtered_proxies = all_proxies

        if json_out:
            proxies_data = [p.model_dump(mode="json") for p in filtered_proxies]
            import json
            print(json.dumps(proxies_data, indent=2))
        else:
            _print_table_filtered(filtered_proxies, console, limit, healthy_only)

    except Exception as e:
        handle_error(e, console)


@app.command(name="ls", rich_help_panel="📋 Data Display", hidden=True)
def list_proxies_alias(ctx: typer.Context) -> None:
    """[dim]Alias for `list` command[/dim]"""
    # Forward to the main list command with basic options
    list_proxies(ctx)


def _print_table(pw: ProxyWhirl, console, limit: Optional[int] = None) -> None:
    """Print proxy list as a beautifully formatted Rich table."""
    proxies = pw.list_proxies()
    if limit is not None:
        proxies = proxies[:limit]

    if not proxies:
        console.print("[warning]🔍 No proxies found in cache. Use 'proxywhirl fetch' to load some![/warning]")
        return

    # Enhanced Rich table with better styling and information density
    table = Table(
        title=f"[proxy]ProxyWhirl Proxy Cache[/proxy] [dim]({len(proxies)} proxies)[/dim]",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
        row_styles=["none", "dim"],
    )

    table.add_column("Host", style="cyan", no_wrap=True)
    table.add_column("Port", justify="right", style="magenta", width=6)
    table.add_column("Schemes", style="green", width=12)
    table.add_column("Anonymity", style="blue", width=10)
    table.add_column("Response (s)", justify="right", style="yellow", width=12)
    table.add_column("Last Checked", style="dim", width=12)
    table.add_column("Country", style="red", width=8, justify="center")
    table.add_column("Status", style="bold", width=8, justify="center")

    for p in proxies:
        # Enhanced data display with fallbacks
        schemes = ", ".join(p.schemes) if p.schemes else "unknown"
        anonymity = getattr(p, "anonymity_level", "unknown")
        response_time = f"{p.response_time:.2f}" if p.response_time else "N/A"
        last_checked = getattr(p, "last_validated", "Never")
        country = getattr(p, "country_code", "??") or "??"
        status_color = "green" if getattr(p, "status", "unknown") == "active" else "red"
        status_icon = "✅" if getattr(p, "status", "unknown") == "active" else "❌"

        table.add_row(
            p.host,
            str(p.port),
            schemes,
            anonymity,
            response_time,
            str(last_checked)[:12],  # Truncate if too long
            country,
            f"[{status_color}]{status_icon}[/{status_color}]",
        )

    console.print(table)

    # Add helpful summary information with enhanced health status
    active_count = sum(1 for p in proxies if getattr(p, "status", None) == "active")
    if active_count > 0:
        success_rate = active_count / len(proxies)
        health_emoji = "🟢" if success_rate > 0.8 else "🟡" if success_rate > 0.5 else "🔴"
        console.print(
            f"[success]📊 Health: {active_count}/{len(proxies)} active ({success_rate:.1%}) {health_emoji}[/success]"
        )
    else:
        console.print("[warning]🔴 No active proxies found. Consider running validation.[/warning]")


def _print_table_filtered(
    proxies: List[Proxy], console, limit: Optional[int] = None, healthy_only: bool = False
) -> None:
    """Print filtered proxy list as a beautifully formatted Rich table."""
    if limit is not None:
        proxies = proxies[:limit]

    if not proxies:
        if healthy_only:
            console.print(
                "[warning]🔍 No healthy proxies found. Use --include-unhealthy to see all proxies or fetch more.[/warning]"
            )
        else:
            console.print("[warning]🔍 No proxies found in cache. Use 'proxywhirl fetch' to load some![/warning]")
        return

    # Enhanced Rich table with health indicators
    filter_info = " (healthy only)" if healthy_only else ""
    table = Table(
        title=f"[proxy]ProxyWhirl Proxy Cache[/proxy] [dim]({len(proxies)} proxies{filter_info})[/dim]",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
        row_styles=["none", "dim"],
    )

    table.add_column("Host", style="cyan", no_wrap=True)
    table.add_column("Port", justify="right", style="magenta", width=6)
    table.add_column("Schemes", style="green", width=12)
    table.add_column("Anonymity", style="blue", width=10)
    table.add_column("Response (s)", justify="right", style="yellow", width=12)
    table.add_column("Last Checked", style="dim", width=12)
    table.add_column("Country", style="red", width=8, justify="center")
    table.add_column("Status", style="bold", width=8, justify="center")

    for p in proxies:
        # Enhanced data display with fallbacks
        schemes = ", ".join(p.schemes) if p.schemes else "unknown"
        anonymity = getattr(p, "anonymity_level", "unknown")
        response_time = f"{p.response_time:.2f}" if p.response_time else "N/A"
        last_checked = getattr(p, "last_validated", "Never")
        country = getattr(p, "country_code", "??") or "??"
        status_color = "green" if getattr(p, "status", "unknown") == "active" else "red"
        status_icon = "✅" if getattr(p, "status", "unknown") == "active" else "❌"

        table.add_row(
            p.host,
            str(p.port),
            schemes,
            anonymity,
            response_time,
            str(last_checked)[:12],  # Truncate if too long
            country,
            f"[{status_color}]{status_icon}[/{status_color}]",
        )

    console.print(table)

    # Enhanced summary with health metrics
    active_count = sum(1 for p in proxies if getattr(p, "status", None) == "active")
    if active_count > 0:
        success_rate = active_count / len(proxies)
        health_emoji = "🟢" if success_rate > 0.8 else "🟡" if success_rate > 0.5 else "🔴"
        console.print(
            f"[success]📊 Health: {active_count}/{len(proxies)} active ({success_rate:.1%}) {health_emoji}[/success]"
        )
    else:
        console.print("[warning]🔴 No active proxies found. Consider running validation.[/warning]")
