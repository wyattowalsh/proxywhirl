"""proxywhirl/cli/commands/data_display.py -- Data Display Commands

Commands for listing and displaying cached proxy data.
"""

import json
from pathlib import Path
from typing import List, Optional
import typer
from typing_extensions import Annotated
from rich.console import Console  
from rich.table import Table

from ...caches.config import CacheType
from ...models import Proxy
from ...proxywhirl import ProxyWhirl
from ..app import app, handle_error


def _print_table_filtered(
    proxies: List[Proxy], console: Console, limit: Optional[int] = None, healthy_only: bool = False
) -> None:
    """Print filtered proxy list as a beautifully formatted Rich table."""
    if limit is not None:
        proxies = proxies[: max(0, limit)]

    if not proxies:
        if healthy_only:
            console.print(
                "[warning]No healthy proxies found in cache.[/warning]\n\n"
                "[info]💡 Try:[/info] [accent]proxywhirl fetch --validate[/accent]"
            )
        else:
            console.print(
                "[warning]No proxies found in cache.[/warning]\n\n"
                "[info]💡 Try running:[/info] [accent]proxywhirl fetch[/accent]"
            )
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
        schemes_str = ",".join((getattr(s, "value", str(s))).lower() for s in p.schemes)
        anonymity = (
            getattr(p.anonymity, "value", str(p.anonymity))
            if hasattr(p, "anonymity")
            else "unknown"
        )
        resp = f"{p.response_time:.3f}" if hasattr(p, "response_time") and p.response_time else "-"
        last_checked = (
            p.last_checked.strftime("%m-%d %H:%M")
            if hasattr(p, "last_checked") and hasattr(p.last_checked, "strftime")
            else "never"
        )
        country = getattr(p, "country_code", "-") or "-"
        status = getattr(p, "status", "unknown")

        # Enhanced color-coded status with more emojis for better health visualization
        if status == "active":
            status_display = "[success]🟢 active[/success]"
        elif status == "inactive":
            status_display = "[error]🔴 inactive[/error]"
        elif status == "timeout":
            status_display = "[warning]🟡 timeout[/warning]"
        elif status == "testing":
            status_display = "[info]🔵 testing[/info]"
        else:
            status_display = "[dim]❓ unknown[/dim]"

        table.add_row(
            p.host,
            str(p.port),
            schemes_str,
            anonymity,
            resp,
            last_checked,
            country,
            status_display,
        )

    console.print(table)

    # Enhanced summary with health metrics
    active_count = sum(1 for p in proxies if getattr(p, "status", None) == "active")
    if active_count > 0:
        success_rate = active_count / len(proxies)
        health_emoji = "🟢" if success_rate > 0.8 else "🟡" if success_rate > 0.5 else "🔴"
        trend_arrow = "↗️" if success_rate > 0.7 else "↘️" if success_rate < 0.3 else "➡️"
        console.print(
            f"[success]{health_emoji} {active_count} of {len(proxies)} proxies are currently active ({success_rate:.1%}) {trend_arrow}[/success]"
        )
    else:
        console.print("[warning]🔴 No active proxies found. Consider running validation.[/warning]")


@app.command(
    "list", 
    rich_help_panel="📋 Data Display",
    help="[bold]📋 List cached proxies with beautiful formatting[/bold]",
    epilog="[dim]Use --json for programmatic access or --healthy-only to filter quality proxies[/dim]",
)
def list_proxies(
    ctx: typer.Context,
    cache_type: Annotated[
        CacheType,
        typer.Option(
            "--cache-type",
            case_sensitive=False,
            help="[info]Cache backend to read from[/info]",
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
    json_output: Annotated[
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
            "--limit",
            "-l",
            help="[cyan]Limit number of rows displayed[/cyan]",
            envvar="PROXYWHIRL_LIST_LIMIT",
            min=1,
            rich_help_panel="📤 Output Options",
        ),
    ] = None,
    healthy_only: Annotated[
        bool,
        typer.Option(
            "--healthy-only/--include-unhealthy",
            help="[success]🟢 Only show healthy proxies (default: True for cleaner output)[/success]",
            envvar="PROXYWHIRL_HEALTHY_ONLY",
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
        # Validate cache consistency
        if cache_type in [CacheType.JSON, CacheType.SQLITE] and not cache_path:
            console.print("[error]❌ Cache path required for {cache_type.value} cache[/error]")
            console.print(f"[info]💡 Add --cache-path ./proxies.{cache_type.value.lower()}[/info]")
            raise typer.Abort()

        # Create ProxyWhirl instance
        pw = ProxyWhirl(
            cache_type=cache_type,
            cache_path=cache_path,
            auto_validate=False,  # Don't auto-validate when just listing
        )

        proxies = pw.list_proxies()

        # Apply healthy filter if requested
        if healthy_only:
            proxies = [p for p in proxies if getattr(p, "status", "unknown") == "active"]

        if json_output:
            # JSON output for programmatic access
            proxy_dicts = []
            for p in proxies[:limit] if limit else proxies:
                proxy_dict = {
                    "host": p.host,
                    "port": p.port,
                    "schemes": [getattr(s, "value", str(s)) for s in p.schemes],
                }
                if hasattr(p, "anonymity"):
                    proxy_dict["anonymity"] = getattr(p.anonymity, "value", str(p.anonymity))
                if hasattr(p, "response_time") and p.response_time:
                    proxy_dict["response_time"] = p.response_time
                if hasattr(p, "country_code"):
                    proxy_dict["country_code"] = p.country_code
                if hasattr(p, "status"):
                    proxy_dict["status"] = p.status
                proxy_dicts.append(proxy_dict)

            print(json.dumps(proxy_dicts, indent=2))
        else:
            # Table output with Rich formatting
            _print_table_filtered(proxies, console, limit, healthy_only)

    except FileNotFoundError:
        console.print("[error]❌ Cache file not found. Check the --cache-path option.[/error]")
        raise typer.Abort()
    except Exception as e:
        handle_error(e, console)


# Alias commands for better UX  
@app.command(name="ls", rich_help_panel="📋 Data Display", hidden=True)
def ls_alias(
    ctx: typer.Context,
    cache_type: Annotated[
        CacheType,
        typer.Option(
            CacheType.MEMORY, case_sensitive=False, help="[info]Cache backend to read from[/info]"
        ),
    ] = CacheType.MEMORY,
    cache_path: Annotated[
        Optional[Path], typer.Option(None, help="[accent]Path to cache file[/accent]")
    ] = None,
    json_out: Annotated[
        bool, typer.Option("--json", help="[info]Output JSON instead of table[/info]")
    ] = False,
    limit: Annotated[
        Optional[int],
        typer.Option(None, "--limit", "-l", help="[cyan]Limit number of rows[/cyan]", min=1),
    ] = None,
    healthy_only: Annotated[
        bool,
        typer.Option(
            True,
            "--healthy-only/--include-unhealthy", 
            help="[success]Only show healthy proxies[/success]"
        ),
    ] = True,
) -> None:
    """[dim]Alias for `list` command[/dim]"""
    # Call the main list command
    list_proxies(ctx, cache_type, cache_path, json_out, limit, healthy_only)
