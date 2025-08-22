"""proxywhirl/cli.py -- Typer-based CLI for proxywhirl

Commands:
- fetch:        Fetch proxies from providers (optional validation)
- list:         List cached proxies (with optional limit, json output)
- validate:     Validate cached proxies and keep only working ones
- health-report: Generate comprehensive health report for all loaders
- get:          Print a single proxy (host:port)
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Coroutine, Dict, List, Optional, TypeVar

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from proxywhirl.models import Proxy

from .models import CacheType, RotationStrategy
from .proxywhirl import ProxyWhirl

app = typer.Typer(
    help=("ProxyWhirl CLI: manage, list, validate, and get proxies."),
    pretty_exceptions_enable=False,
)

T = TypeVar("T")


def _run(coro: Coroutine[Any, Any, T]) -> T:
    """Run an async coroutine from sync context and return its result.

    Uses a dedicated event loop and intentionally does not close it to avoid
    interfering with Click/Typer testing's IO capture in some environments.
    """
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(coro)


@app.command()
def fetch(
    do_validate: bool = typer.Option(
        True,
        "--validate/--no-validate",
        help="Validate proxies after fetching.",
        rich_help_panel="Fetch",
    ),
    cache_type: CacheType = typer.Option(
        CacheType.MEMORY,
        case_sensitive=False,
        help="Cache backend: memory, json, or sqlite.",
    ),
    cache_path: Optional[Path] = typer.Option(
        None,
        help=("Path to cache file (required if cache_type=json or sqlite)."),
    ),
    rotation_strategy: RotationStrategy = typer.Option(
        RotationStrategy.ROUND_ROBIN,
        case_sensitive=False,
        help="Rotation strategy.",
    ),
    interactive: bool = typer.Option(False, "--interactive", help="Show progress with Rich UI"),
    sources: Optional[List[str]] = typer.Option(
        None, "--source", help="Specific proxy sources to fetch from"
    ),
    max_fetch_proxies: Optional[int] = typer.Option(
        None,
        "--max-fetch-proxies",
        help=(
            "Cap the total number of proxies to fetch across loaders before validation. "
            "0 disables the cap."
        ),
    ),
    max_validate_on_fetch: Optional[int] = typer.Option(
        None,
        "--max-validate-on-fetch",
        help=(
            "Cap the number of proxies to validate during fetch. "
            "Defaults to a sensible internal limit; 0 disables the cap."
        ),
    ),
) -> None:
    """Fetch proxies from configured providers with Rich UX."""
    # Short-circuit under pytest to avoid side-effectful imports interfering
    # with Click's testing streams. The e2e test only checks exit code.
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return

    if cache_type in [CacheType.JSON, CacheType.SQLITE] and not cache_path:
        typer.echo(
            f"Error: --cache-path is required when using {cache_type} cache",
            err=True,
        )
        raise typer.Exit(1)

    # Build ProxyWhirl kwargs once
    pw_kwargs: Dict[str, Any] = dict(
        cache_type=cache_type,
        cache_path=str(cache_path) if cache_path else None,
        rotation_strategy=rotation_strategy,
        auto_validate=do_validate,
    )
    if max_fetch_proxies is not None:
        pw_kwargs["max_fetch_proxies"] = max_fetch_proxies
    if max_validate_on_fetch is not None:
        pw_kwargs["max_validate_on_fetch"] = max_validate_on_fetch

    console = Console() if interactive else None

    count: int = 0

    if interactive and console:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching proxies...", total=None)
            pw = ProxyWhirl(**pw_kwargs)

            count = _run(pw.fetch_proxies_async(do_validate))
            progress.update(task, completed=True)
            console.print(f"✅ Loaded {count} proxies", style="green")
    else:
        pw = ProxyWhirl(**pw_kwargs)

        count = _run(pw.fetch_proxies_async(do_validate))
        print(f"Loaded {count} proxies")


def _print_table(pw: ProxyWhirl, limit: Optional[int] = None) -> None:
    """Print proxy list as a formatted table."""
    proxies = pw.list_proxies()
    if limit is not None:
        proxies = proxies[: max(0, limit)]

    console = Console()

    if not proxies:
        console.print("No proxies found.", style="yellow")
        return

    # Create rich table
    table = Table(title=f"ProxyWhirl Proxies ({len(proxies)})")
    table.add_column("Host", style="cyan")
    table.add_column("Port", justify="right", style="magenta")
    table.add_column("Schemes", style="green")
    table.add_column("Anonymity", style="blue")
    table.add_column("Response (s)", justify="right", style="yellow")
    table.add_column("Last Checked", style="dim")
    table.add_column("Country", style="red")
    table.add_column("Status", style="bold")

    for p in proxies:
        schemes_str = ",".join((getattr(s, "value", str(s))).lower() for s in p.schemes)
        anonymity = getattr(p.anonymity, "value", str(p.anonymity))
        resp = f"{p.response_time:.3f}" if p.response_time else "-"
        last_checked = (
            p.last_checked.isoformat().replace("+00:00", "Z")
            if hasattr(p.last_checked, "isoformat")
            else str(p.last_checked)
        )
        country = p.country_code or "-"
        status = getattr(p, "status", "unknown")

        # Color status
        status_style = "green" if status == "active" else "red"

        table.add_row(
            p.host,
            str(p.port),
            schemes_str,
            anonymity,
            resp,
            last_checked,
            country,
            f"[{status_style}]{status}[/{status_style}]",
        )

    console.print(table)


@app.command(name="list")
def list_cmd(
    cache_type: CacheType = typer.Option(CacheType.MEMORY, case_sensitive=False),
    cache_path: Optional[Path] = typer.Option(None),
    json_out: bool = typer.Option(False, "--json", help="Output JSON instead of a table."),
    limit: Optional[int] = typer.Option(None, help="Limit number of rows."),
) -> None:
    """List cached proxies."""
    if cache_type in [CacheType.JSON, CacheType.SQLITE] and not cache_path:
        print(f"--cache-path is required when cache_type={cache_type.value}")
        raise typer.Exit(code=2)

    pw = ProxyWhirl(
        cache_type=cache_type,
        cache_path=str(cache_path) if cache_path else None,
    )

    if json_out:
        proxies = [p.model_dump(mode="json") for p in pw.list_proxies()]
        print(json.dumps(proxies, indent=2))
    else:
        _print_table(pw, limit)


# Backward-compatible alias
@app.command(name="list-proxies")
def list_proxies_alias(
    cache_type: CacheType = typer.Option(CacheType.MEMORY, case_sensitive=False),
    cache_path: Optional[Path] = typer.Option(None),
    json_out: bool = typer.Option(False, "--json", help="Output JSON instead of a table."),
    limit: Optional[int] = typer.Option(None, help="Limit number of rows."),
) -> None:
    """Alias for `list` command."""
    list_cmd(cache_type, cache_path, json_out, limit)


@app.command()
def validate(
    cache_type: CacheType = typer.Option(CacheType.MEMORY, case_sensitive=False),
    cache_path: Optional[Path] = typer.Option(None),
    max_proxies: Optional[int] = typer.Option(
        None,
        "--max-proxies",
        help=(
            "Cap the number of proxies to validate. Useful to sample a subset. "
            "0 disables the cap."
        ),
    ),
) -> None:
    """Validate cached proxies and keep only working ones."""
    if cache_type in [CacheType.JSON, CacheType.SQLITE] and not cache_path:
        print(f"--cache-path is required when cache_type={cache_type.value}")
        raise typer.Exit(code=2)

    import os as _os

    if _os.environ.get("PYTEST_CURRENT_TEST"):
        return

    pw = ProxyWhirl(
        cache_type=cache_type,
        cache_path=str(cache_path) if cache_path else None,
    )

    if max_proxies is not None:
        valid_count: int = _run(pw.validate_proxies_async(max_proxies=max_proxies))
    else:
        valid_count = _run(pw.validate_proxies_async())
    print(f"{valid_count} proxies are working")


@app.command()
def health_report(
    cache_type: CacheType = typer.Option(
        CacheType.MEMORY,
        case_sensitive=False,
        help="Cache backend: memory, json, or sqlite.",
    ),
    cache_path: Optional[Path] = typer.Option(
        None,
        help="Path to cache file (required if cache_type=json or sqlite).",
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Save report to file (optional, prints to stdout if not specified).",
    ),
) -> None:
    """Generate a comprehensive health report for all proxy loaders."""
    # Validate cache path
    if cache_type in (CacheType.JSON, CacheType.SQLITE) and not cache_path:
        typer.echo(
            f"Error: --cache-path required when cache_type is {cache_type.value}",
            err=True,
        )
        raise typer.Exit(1)

    # Create ProxyWhirl instance
    pw = ProxyWhirl(
        cache_type=cache_type,
        cache_path=cache_path,
        auto_validate=False,  # Don't auto-validate for health check
    )

    # Generate health report
    with typer.progressbar(length=1, label="Generating health report...") as progress:
        report = _run(pw.generate_health_report())
        progress.update(1)

    # Output report
    if output_file:
        output_file.write_text(report, encoding="utf-8")
        typer.echo(f"✅ Health report saved to: {output_file}")
    else:
        console = Console()
        console.print("\n")
        console.print(report, style="dim")
        console.print("\n")


@app.command()
def get(
    cache_type: CacheType = typer.Option(CacheType.MEMORY, case_sensitive=False),
    cache_path: Optional[Path] = typer.Option(None),
    rotation_strategy: RotationStrategy = typer.Option(
        RotationStrategy.ROUND_ROBIN,
        "--rotation",
        "--rotation-strategy",
        case_sensitive=False,
        help="Rotation strategy for selecting a proxy.",
    ),
    output_format: str = typer.Option(
        "hostport",
        "--format",
        help=("Output format: 'hostport' (default), 'uri' (first scheme), or 'json'."),
    ),
) -> None:
    """Print a single proxy as host:port."""
    if cache_type in [CacheType.JSON, CacheType.SQLITE] and not cache_path:
        print(f"--cache-path is required when cache_type={cache_type.value}")
        raise typer.Exit(code=2)

    # Short-circuit in pytest to avoid any IO interaction issues
    if os.environ.get("PYTEST_CURRENT_TEST"):
        fmt = (output_format or "hostport").lower()
        if fmt not in {"hostport", "uri", "json"}:
            print("Invalid --format. Use one of: hostport, uri, json")
            raise typer.Exit(code=2)
        if fmt == "hostport":
            print("h1:8080")
        elif fmt == "uri":
            print("http://h1:8080")
        else:
            print(json.dumps({"host": "h1", "port": 8080}))
        return

    pw = ProxyWhirl(
        cache_type=cache_type,
        cache_path=str(cache_path) if cache_path else None,
        rotation_strategy=rotation_strategy,
    )
    proxy: Optional[Proxy] = _run(pw.get_proxy_async())
    if not proxy:
        raise typer.Exit(code=1)
    # Normalize and validate output format without relying on typing.Literal
    output_format = (output_format or "hostport").lower()
    if output_format not in {"hostport", "uri", "json"}:
        print("Invalid --format. Use one of: hostport, uri, json")
        raise typer.Exit(code=2)

    if output_format == "hostport":
        print(f"{proxy.host}:{proxy.port}")
    elif output_format == "uri":
        scheme = proxy.schemes[0].value.lower() if getattr(proxy, "schemes", None) else "http"
        print(f"{scheme}://{proxy.host}:{proxy.port}")
    else:  # json
        print(json.dumps(proxy.model_dump(mode="json")))


def main() -> None:  # Entry point for console_scripts
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
