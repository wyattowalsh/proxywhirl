"""proxywhirl/cli/commands/proxy_access.py -- Proxy Access Commands

Commands for getting and accessing cached proxies.
"""

import asyncio
from pathlib import Path
from typing import Optional
import typer
from typing_extensions import Annotated

from ...caches.config import CacheType
from ...models import RotationStrategy
from ...proxywhirl import ProxyWhirl
from ..app import app, handle_error


@app.command(rich_help_panel="🎯 Proxy Access")
def get(
    ctx: typer.Context,
    get_cache_type: Annotated[
        CacheType,
        typer.Option(
            CacheType.MEMORY,
            case_sensitive=False,
            help="[info]Cache backend to read from[/info]",
            rich_help_panel="💾 Cache Options",
        ),
    ] = CacheType.MEMORY,
    get_cache_path: Annotated[
        Optional[Path],
        typer.Option(
            None, help="[accent]Path to cache file[/accent]", rich_help_panel="💾 Cache Options"
        ),
    ] = None,
    rotation_strategy: Annotated[
        RotationStrategy,
        typer.Option(
            RotationStrategy.ROUND_ROBIN,
            "--rotation",
            "--rotation-strategy",
            case_sensitive=False,
            help="[info]Strategy for selecting proxy (use 'proxywhirl strategies' for all options)[/info]",
            rich_help_panel="🔄 Selection Options",
        ),
    ] = RotationStrategy.ROUND_ROBIN,
    output_format: Annotated[
        str,
        typer.Option(
            "hostport",
            "--format",
            "-f",
            help="[cyan]Output format: hostport, uri, or json[/cyan]",
            rich_help_panel="📤 Output Options",
        ),
    ] = "hostport",
    show_details: Annotated[
        bool,
        typer.Option(
            "--details/--no-details",
            "-d",
            help="[info]Show detailed proxy information[/info]",
            rich_help_panel="📤 Output Options",
        ),
    ] = False,
) -> None:
    """Get a proxy using the specified rotation strategy.
    
    Retrieves a single proxy from the cache using the configured rotation strategy.
    If the cache is empty, will automatically attempt to fetch proxies.
    """
    console = ctx.obj.console
    
    try:
        # Validate cache consistency
        if get_cache_type in [CacheType.JSON, CacheType.SQLITE] and not get_cache_path:
            console.print(f"[error]❌ Cache path required for {get_cache_type.value} cache[/error]")
            console.print(f"[info]💡 Add --cache-path ./proxies.{get_cache_type.value.lower()}[/info]")
            raise typer.Abort()

        # Create ProxyWhirl instance
        pw = ProxyWhirl(
            cache_type=get_cache_type,
            cache_path=get_cache_path,
            rotation_strategy=rotation_strategy,
            auto_validate=False,  # Don't auto-validate when getting a proxy
        )

        # Get proxy using async method
        def _run_get():
            return asyncio.run(pw.get_proxy_async())

        proxy = _run_get()

        if proxy is None:
            console.print("[warning]⚠️  No proxies available. Try running:[/warning]")
            console.print("[cyan]proxywhirl fetch[/cyan]")
            raise typer.Exit(1)

        # Format output based on requested format
        if output_format == "hostport":
            output = f"{proxy.host}:{proxy.port}"
        elif output_format == "uri":
            scheme = proxy.schemes[0].value if proxy.schemes else "http"
            output = f"{scheme}://{proxy.host}:{proxy.port}"
        elif output_format == "json":
            import json
            proxy_dict = {
                "host": proxy.host,
                "port": proxy.port,
                "schemes": [s.value for s in proxy.schemes],
            }
            if hasattr(proxy, "anonymity"):
                proxy_dict["anonymity"] = proxy.anonymity.value
            if hasattr(proxy, "country_code"):
                proxy_dict["country_code"] = proxy.country_code
            if hasattr(proxy, "response_time") and proxy.response_time:
                proxy_dict["response_time"] = proxy.response_time
            output = json.dumps(proxy_dict)
        else:
            console.print(f"[error]❌ Unknown format: {output_format}[/error]")
            console.print("[info]💡 Supported formats: hostport, uri, json[/info]")
            raise typer.Abort()

        if show_details and output_format != "json":
            # Show detailed information
            console.print(f"[proxy]Selected Proxy:[/proxy] [cyan]{proxy.host}:{proxy.port}[/cyan]")
            console.print(f"[dim]Strategy:[/dim] {rotation_strategy.value}")
            if hasattr(proxy, "schemes"):
                schemes_str = ", ".join(s.value for s in proxy.schemes)
                console.print(f"[dim]Schemes:[/dim] {schemes_str}")
            if hasattr(proxy, "country_code") and proxy.country_code:
                console.print(f"[dim]Country:[/dim] {proxy.country_code}")
            if hasattr(proxy, "response_time") and proxy.response_time:
                console.print(f"[dim]Response Time:[/dim] {proxy.response_time:.3f}s")
        else:
            # Just output the formatted result
            print(output)

    except Exception as e:
        handle_error(e, console)
