"""Command-line interface for ProxyWhirl.

This module provides a Typer-based CLI for proxy rotation operations.
Supports multiple output formats (text, JSON, CSV) with TTY-aware rendering.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import httpx
import typer
from rich.console import Console
from rich.table import Table

from proxywhirl.config import CLIConfig, discover_config, load_config
from proxywhirl.models import RequestResult
from proxywhirl.utils import CLILock

# Typer app instance
app = typer.Typer(
    name="proxywhirl",
    help="Advanced proxy rotation library with CLI interface",
    add_completion=True,
    no_args_is_help=True,
)


class OutputFormat(str, Enum):
    """Supported output formats for CLI commands."""

    TEXT = "text"
    JSON = "json"
    CSV = "csv"


@dataclass
class CommandContext:
    """Shared context for all CLI commands.

    Attributes:
        config: CLI configuration loaded from discovered config file
        config_path: Path to the active configuration file (may be fallback if none found)
        format: Output format (text, json, csv)
        verbose: Enable verbose logging
        console: Rich console for formatted output
        lock: File lock for concurrent operation safety
    """

    config: CLIConfig
    config_path: Path
    format: OutputFormat
    verbose: bool
    console: Console
    lock: CLILock | None = None


# Global context storage (set by callback)
_context: CommandContext | None = None


def get_context() -> CommandContext:
    """Get the current command context.

    Returns:
        CommandContext: The active command context

    Raises:
        typer.Exit: If context is not initialized
    """
    if _context is None:
        typer.secho("Error: Command context not initialized", err=True, fg="red")
        raise typer.Exit(code=1)
    return _context


@app.callback()
def main(
    ctx: typer.Context,
    config_file: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file (TOML). Auto-discovered if not provided.",
        exists=True,
        dir_okay=False,
        resolve_path=True,
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.TEXT,
        "--format",
        "-f",
        help="Output format (text/json/csv)",
        case_sensitive=False,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
    no_lock: bool = typer.Option(
        False,
        "--no-lock",
        help="Disable file locking (use with caution)",
    ),
) -> None:
    """ProxyWhirl CLI - Advanced proxy rotation library.

    Global options apply to all subcommands.
    Configuration is auto-discovered from:
      1. Project directory: ./.proxywhirl.toml
      2. User directory: ~/.config/proxywhirl/config.toml (Linux/Mac)
      3. Defaults: In-memory configuration
    """
    global _context

    # Discover config file if not provided
    if config_file is None:
        config_file = discover_config()

    # Load configuration (defaults if no file found)
    try:
        config = load_config(config_file)
    except Exception as e:
        typer.secho(f"Error loading config: {e}", err=True, fg="red")
        raise typer.Exit(code=1)

    # Initialize console with TTY detection
    console = Console(
        force_terminal=format == OutputFormat.TEXT,
        force_interactive=False,
        force_jupyter=False,
    )

    # Initialize lock if enabled
    lock = None
    if not no_lock:
        # Use config dir or fallback to temp dir
        if config_file:
            lock_dir = config_file.parent
        else:
            from platformdirs import user_data_dir

            lock_dir = Path(user_data_dir("proxywhirl", "proxywhirl"))
            lock_dir.mkdir(parents=True, exist_ok=True)

        lock = CLILock(config_dir=lock_dir)
        try:
            lock.__enter__()
        except typer.Exit:
            # Lock acquisition failed (already handled by CLILock)
            raise

    # Store context globally
    _context = CommandContext(
        config=config,
        config_path=config_file or Path.cwd() / ".proxywhirl.toml",  # Fallback path
        format=format,
        verbose=verbose,
        console=console,
        lock=lock,
    )

    # Ensure lock cleanup on exit
    if lock is not None:
        ctx.call_on_close(lambda: lock.__exit__(None, None, None))


def render_text(console: Console, data: dict[str, Any]) -> None:
    """Render data as formatted text using Rich.

    Args:
        console: Rich console instance
        data: Data to render (must have 'message' or table structure)
    """
    if "message" in data:
        console.print(data["message"])
    elif "table" in data:
        table = Table(title=data.get("title"))
        for header in data["table"]["headers"]:
            table.add_column(str(header))
        for row in data["table"]["rows"]:
            table.add_row(*[str(cell) for cell in row])
        console.print(table)
    else:
        console.print(data)


def render_json(data: dict[str, Any]) -> None:
    """Render data as JSON to stdout.

    Args:
        data: Data to render as JSON
    """
    import json

    print(json.dumps(data, indent=2))


def render_csv(data: dict[str, Any]) -> None:
    """Render data as CSV to stdout.

    Args:
        data: Data to render (must have 'table' structure with headers/rows)
    """
    import csv

    if "table" not in data:
        typer.secho("Error: CSV format requires table data", err=True, fg="red")
        raise typer.Exit(code=1)

    writer = csv.writer(sys.stdout)
    writer.writerow(data["table"]["headers"])
    writer.writerows(data["table"]["rows"])


def render_output(context: CommandContext, data: dict[str, Any]) -> None:
    """Render output in the configured format.

    Args:
        context: Command context with format settings
        data: Data to render
    """
    if context.format == OutputFormat.TEXT:
        render_text(context.console, data)
    elif context.format == OutputFormat.JSON:
        render_json(data)
    elif context.format == OutputFormat.CSV:
        render_csv(data)


# ============================================================================
# Commands
# ============================================================================


@app.command()
def request(
    url: str = typer.Argument(..., help="Target URL to request"),
    method: str = typer.Option("GET", "--method", "-X", help="HTTP method (GET/POST/etc)"),
    headers: list[str] = typer.Option(
        None, "--header", "-H", help="Custom headers (format: 'Key: Value')"
    ),
    data: str | None = typer.Option(None, "--data", "-d", help="Request body data"),
    proxy: str | None = typer.Option(
        None, "--proxy", "-p", help="Specific proxy URL (overrides rotation)"
    ),
    max_retries: int | None = typer.Option(
        None, "--retries", help="Max retry attempts (overrides config)"
    ),
) -> None:
    """Make an HTTP request through a rotating proxy.

    Examples:
      proxywhirl request https://api.example.com
      proxywhirl request -X POST -d '{"key":"value"}' https://api.example.com
      proxywhirl request -H "Authorization: Bearer token" https://api.example.com
    """
    import time

    ctx = get_context()

    # Parse headers
    header_dict: dict[str, str] = {}
    if headers:
        for header in headers:
            if ":" not in header:
                typer.secho(f"Invalid header format: {header}", err=True, fg="red")
                typer.secho("Use format: 'Key: Value'", err=True, fg="yellow")
                raise typer.Exit(code=1)
            key, value = header.split(":", 1)
            header_dict[key.strip()] = value.strip()

    # Get proxy to use
    proxy_url: str | None = None
    if proxy:
        proxy_url = proxy
    elif ctx.config.proxies:
        # Use first proxy from config for now (TODO: implement rotation)
        proxy_url = ctx.config.proxies[0].url

    # Determine retries
    retries = max_retries if max_retries is not None else ctx.config.max_retries

    # Make request with retries
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            start_time = time.time()

            # Create httpx client with proxy
            with httpx.Client(
                proxy=proxy_url,
                timeout=ctx.config.timeout,
                follow_redirects=ctx.config.follow_redirects,
                verify=ctx.config.verify_ssl,
            ) as client:
                # Make request
                response = client.request(method=method, url=url, headers=header_dict, content=data)

            elapsed_ms = (time.time() - start_time) * 1000

            # Create result
            result = RequestResult(
                url=url,
                method=method,
                status_code=response.status_code,
                elapsed_ms=elapsed_ms,
                proxy_used=proxy_url or "direct",
                attempts=attempt + 1,
                headers=dict(response.headers),
                body=response.text[:1000],  # Truncate to 1000 chars
            )

            # Render output based on format
            if ctx.format == OutputFormat.TEXT:
                # Human-readable output
                status_color = "green" if result.is_success() else "red"
                ctx.console.print(
                    f"[bold]Status:[/bold] [{status_color}]{result.status_code}[/{status_color}]"
                )
                ctx.console.print(f"[bold]URL:[/bold] {result.url}")
                ctx.console.print(f"[bold]Time:[/bold] {result.elapsed_ms:.0f}ms")
                if result.proxy_used and result.proxy_used != "direct":
                    ctx.console.print(f"[bold]Proxy:[/bold] {result.proxy_used}")
                ctx.console.print(f"[bold]Attempts:[/bold] {result.attempts}")
                if result.body:
                    ctx.console.print("\n[bold]Response:[/bold]")
                    ctx.console.print(result.body)
            elif ctx.format == OutputFormat.JSON:
                output: dict[str, Any] = {
                    "status_code": result.status_code,
                    "url": result.url,
                    "method": result.method,
                    "elapsed_ms": result.elapsed_ms,
                    "proxy_used": result.proxy_used,
                    "attempts": result.attempts,
                    "body": result.body,
                }
                render_json(output)
            elif ctx.format == OutputFormat.CSV:
                output_csv: dict[str, Any] = {
                    "table": {
                        "headers": ["Status", "URL", "Time(ms)", "Proxy", "Attempts"],
                        "rows": [
                            [
                                str(result.status_code),
                                result.url,
                                f"{result.elapsed_ms:.0f}",
                                result.proxy_used or "N/A",
                                str(result.attempts),
                            ]
                        ],
                    }
                }
                render_csv(output_csv)

            # Exit successfully
            return

        except Exception as e:
            last_error = e
            if ctx.verbose:
                typer.secho(
                    f"Attempt {attempt + 1}/{retries + 1} failed: {e}",
                    err=True,
                    fg="yellow",
                )
            if attempt < retries:
                time.sleep(1)  # Wait before retry

    # All retries exhausted
    typer.secho(f"Request failed after {retries + 1} attempts", err=True, fg="red")
    if last_error:
        typer.secho(f"Last error: {last_error}", err=True, fg="red")
    raise typer.Exit(code=1)


@app.command()
def pool(
    action: str = typer.Argument(..., help="Action: list, add, remove, test"),
    proxy: str | None = typer.Argument(None, help="Proxy URL (for add/remove/test actions)"),
    username: str | None = typer.Option(None, "--username", "-u", help="Proxy username"),
    password: str | None = typer.Option(None, "--password", "-p", help="Proxy password"),
) -> None:
    """Manage the proxy pool (list/add/remove/test).

    Examples:
      proxywhirl pool list
      proxywhirl pool add http://proxy1.com:8080
      proxywhirl pool remove http://proxy1.com:8080
      proxywhirl pool test http://proxy1.com:8080
    """
    import time

    import httpx
    from pydantic import SecretStr

    from proxywhirl.config import ProxyConfig, save_config
    from proxywhirl.models import HealthStatus, PoolSummary, Proxy, ProxyStatus
    from proxywhirl.rotator import ProxyRotator

    command_ctx = get_context()

    # Validate action
    valid_actions = ["list", "add", "remove", "test"]
    if action not in valid_actions:
        command_ctx.console.print(
            f"[red]Invalid action '{action}'. Valid actions: {', '.join(valid_actions)}[/red]"
        )
        raise typer.Exit(code=1)

    # Create rotator from config
    proxies = []
    for proxy_config in command_ctx.config.proxies:
        proxies.append(
            Proxy(
                url=proxy_config.url,
                username=proxy_config.username,
                password=proxy_config.password,
            )
        )

    rotator = ProxyRotator(proxies=proxies, strategy=command_ctx.config.rotation_strategy)

    if action == "list":
        # List all proxies in pool
        pool_proxies = rotator.pool.proxies
        if not pool_proxies:
            command_ctx.console.print("[yellow]No proxies in pool[/yellow]")
            return

        proxy_statuses = [
            ProxyStatus(
                url=p.url,
                health=p.health_status,
                response_time_ms=p.average_response_time_ms or 0,
                success_rate=p.success_rate,
            )
            for p in pool_proxies
        ]

        summary = PoolSummary(
            total_proxies=len(pool_proxies),
            healthy=sum(1 for p in pool_proxies if p.health_status == HealthStatus.HEALTHY),
            degraded=sum(1 for p in pool_proxies if p.health_status == HealthStatus.DEGRADED),
            failed=sum(
                1
                for p in pool_proxies
                if p.health_status in (HealthStatus.UNHEALTHY, HealthStatus.DEAD)
            ),
            rotation_strategy=command_ctx.config.rotation_strategy,
            current_index=0,  # Not tracked in rotator yet
            proxies=proxy_statuses,
        )

        if command_ctx.format == OutputFormat.JSON:
            render_json(summary.model_dump())
        elif command_ctx.format == OutputFormat.CSV:
            # For CSV, output each proxy as a row
            import csv
            import sys

            writer = csv.DictWriter(
                sys.stdout, fieldnames=["url", "health", "response_time_ms", "success_rate"]
            )
            writer.writeheader()
            writer.writerows([ps.model_dump() for ps in proxy_statuses])
        else:  # TEXT
            command_ctx.console.print("\n[bold]Proxy Pool Summary[/bold]")
            command_ctx.console.print(f"Total Proxies: {summary.total_proxies}")
            command_ctx.console.print(
                f"Healthy: [green]{summary.healthy}[/green] | "
                f"Degraded: [yellow]{summary.degraded}[/yellow] | "
                f"Failed: [red]{summary.failed}[/red]"
            )
            command_ctx.console.print(f"Strategy: {summary.rotation_strategy}\n")

            for ps in proxy_statuses:
                health_color = (
                    "green"
                    if ps.health == HealthStatus.HEALTHY
                    else "yellow"
                    if ps.health == HealthStatus.DEGRADED
                    else "red"
                )
                command_ctx.console.print(
                    f"  [{health_color}]●[/{health_color}] {ps.url} "
                    f"({ps.response_time_ms:.0f}ms, {ps.success_rate * 100:.0f}% success)"
                )

    elif action == "add":
        if not proxy:
            command_ctx.console.print("[red]Proxy URL required for 'add' action[/red]")
            raise typer.Exit(code=1)

        # Add proxy to pool
        new_proxy = Proxy(
            url=proxy,
            username=SecretStr(username) if username else None,
            password=SecretStr(password) if password else None,
        )
        rotator.pool.add_proxy(new_proxy)

        # Save updated config
        command_ctx.config.proxies.append(
            ProxyConfig(
                url=proxy,
                username=SecretStr(username) if username else None,
                password=SecretStr(password) if password else None,
            )
        )
        save_config(command_ctx.config, command_ctx.config_path)

        command_ctx.console.print(f"[green]✓[/green] Added proxy: {proxy}")

    elif action == "remove":
        if not proxy:
            command_ctx.console.print("[red]Proxy URL required for 'remove' action[/red]")
            raise typer.Exit(code=1)

        # Find proxy by URL
        proxy_obj = next((p for p in rotator.pool.proxies if p.url == proxy), None)
        if not proxy_obj:
            command_ctx.console.print(f"[red]Error:[/red] Proxy not found: {proxy}")
            raise typer.Exit(code=1)

        # Remove proxy from pool
        rotator.pool.remove_proxy(proxy_obj.id)

        # Save updated config
        command_ctx.config.proxies = [p for p in command_ctx.config.proxies if p.url != proxy]
        save_config(command_ctx.config, command_ctx.config_path)

        command_ctx.console.print(f"[green]✓[/green] Removed proxy: {proxy}")

    elif action == "test":
        if not proxy:
            command_ctx.console.print("[red]Proxy URL required for 'test' action[/red]")
            raise typer.Exit(code=1)

        # Test proxy with HTTP request
        command_ctx.console.print(f"Testing proxy: {proxy}...")

        try:
            import time

            start_time = time.time()
            with httpx.Client(
                proxy=proxy,
                timeout=command_ctx.config.timeout,
                verify=command_ctx.config.verify_ssl,
            ) as client:
                response = client.get("https://httpbin.org/ip")
            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                command_ctx.console.print(f"[green]✓[/green] Proxy is working ({elapsed_ms:.0f}ms)")
                if command_ctx.verbose:
                    command_ctx.console.print(f"Response: {response.text}")
            else:
                command_ctx.console.print(
                    f"[yellow]![/yellow] Proxy returned status {response.status_code}"
                )
        except Exception as e:
            command_ctx.console.print(f"[red]✗[/red] Proxy test failed: {e}")
            raise typer.Exit(code=1)


@app.command()
def config(
    action: str = typer.Argument(..., help="Action: show, set, get, init"),
    key: str | None = typer.Argument(None, help="Config key (for get/set)"),
    value: str | None = typer.Argument(None, help="Config value (for set)"),
) -> None:
    """Manage CLI configuration (show/get/set/init).

    Examples:
      proxywhirl config show
      proxywhirl config get rotation_strategy
      proxywhirl config set rotation_strategy random
      proxywhirl config init
    """
    from pathlib import Path

    from proxywhirl.config import CLIConfig, save_config

    command_ctx = get_context()

    # Validate action
    valid_actions = ["show", "get", "set", "init"]
    if action not in valid_actions:
        command_ctx.console.print(
            f"[red]Invalid action '{action}'. Valid actions: {', '.join(valid_actions)}[/red]"
        )
        raise typer.Exit(code=1)

    if action == "init":
        # Initialize a new config file
        config_path = Path.cwd() / ".proxywhirl.toml"
        if config_path.exists():
            command_ctx.console.print(f"[yellow]Config file already exists: {config_path}[/yellow]")
            if not typer.confirm("Overwrite?"):
                raise typer.Exit(code=0)

        # Create default config
        default_config = CLIConfig(
            proxies=[],
            proxy_file=None,
            rotation_strategy="round_robin",
            health_check_interval=300,
            timeout=30,
            max_retries=3,
            follow_redirects=True,
            verify_ssl=True,
            default_format="text",
            color=True,
            verbose=False,
            storage_backend="memory",
            storage_path=None,
            encrypt_credentials=False,
            encryption_key_env="PROXYWHIRL_KEY",
        )
        save_config(default_config, config_path)
        command_ctx.console.print(f"[green]✓[/green] Created config file: {config_path}")

    elif action == "show":
        # Show entire config
        if command_ctx.format == OutputFormat.JSON:
            # Exclude sensitive fields
            config_dict = command_ctx.config.model_dump(mode="json", exclude={"proxies"})
            render_json(config_dict)
        elif command_ctx.format == OutputFormat.CSV:
            # CSV format - show as key-value pairs
            import csv
            import sys

            config_dict = command_ctx.config.model_dump(mode="json", exclude={"proxies"})
            writer = csv.writer(sys.stdout)
            writer.writerow(["key", "value"])
            for k, v in config_dict.items():
                writer.writerow([k, v])
        else:  # TEXT
            command_ctx.console.print("\n[bold]Configuration[/bold]")
            command_ctx.console.print(f"Config file: {command_ctx.config_path}\n")

            # Show non-sensitive settings
            command_ctx.console.print(f"rotation_strategy: {command_ctx.config.rotation_strategy}")
            command_ctx.console.print(
                f"health_check_interval: {command_ctx.config.health_check_interval}s"
            )
            command_ctx.console.print(f"timeout: {command_ctx.config.timeout}s")
            command_ctx.console.print(f"max_retries: {command_ctx.config.max_retries}")
            command_ctx.console.print(f"follow_redirects: {command_ctx.config.follow_redirects}")
            command_ctx.console.print(f"verify_ssl: {command_ctx.config.verify_ssl}")
            command_ctx.console.print(f"default_format: {command_ctx.config.default_format}")
            command_ctx.console.print(f"color: {command_ctx.config.color}")
            command_ctx.console.print(f"verbose: {command_ctx.config.verbose}")
            command_ctx.console.print(f"storage_backend: {command_ctx.config.storage_backend}")
            command_ctx.console.print(f"storage_path: {command_ctx.config.storage_path}")

    elif action == "get":
        if not key:
            command_ctx.console.print("[red]Key required for 'get' action[/red]")
            raise typer.Exit(code=1)

        # Get specific config value
        if not hasattr(command_ctx.config, key):
            command_ctx.console.print(f"[red]Unknown config key: {key}[/red]")
            raise typer.Exit(code=1)

        value_obj = getattr(command_ctx.config, key)
        if command_ctx.format == OutputFormat.JSON:
            render_json({key: value_obj})
        else:
            command_ctx.console.print(str(value_obj))

    elif action == "set":
        if not key or not value:
            command_ctx.console.print("[red]Key and value required for 'set' action[/red]")
            raise typer.Exit(code=1)

        # Set config value
        if not hasattr(command_ctx.config, key):
            command_ctx.console.print(f"[red]Unknown config key: {key}[/red]")
            raise typer.Exit(code=1)

        # Convert value to appropriate type
        old_value = getattr(command_ctx.config, key)
        try:
            new_value: bool | int | float | str
            if isinstance(old_value, bool):
                new_value = value.lower() in ("true", "1", "yes", "on")
            elif isinstance(old_value, int):
                new_value = int(value)
            elif isinstance(old_value, float):
                new_value = float(value)
            else:
                new_value = value

            setattr(command_ctx.config, key, new_value)
            save_config(command_ctx.config, command_ctx.config_path)
            command_ctx.console.print(f"[green]✓[/green] Set {key} = {new_value}")
        except ValueError as e:
            command_ctx.console.print(f"[red]Invalid value for {key}: {e}[/red]")
            raise typer.Exit(code=1)


@app.command()
def health(
    continuous: bool = typer.Option(False, "--continuous", "-c", help="Run continuously"),
    interval: int | None = typer.Option(None, "--interval", "-i", help="Check interval in seconds"),
) -> None:
    """Check health of all proxies in the pool.

    Examples:
      proxywhirl health
      proxywhirl health --continuous --interval 60
    """
    import time
    from datetime import datetime, timezone

    import httpx

    from proxywhirl.models import HealthStatus, PoolSummary, Proxy, ProxyStatus
    from proxywhirl.rotator import ProxyRotator

    command_ctx = get_context()

    # Create rotator from config
    proxies = []
    for proxy_config in command_ctx.config.proxies:
        proxies.append(
            Proxy(
                url=proxy_config.url,
                username=proxy_config.username,
                password=proxy_config.password,
            )
        )

    if not proxies:
        command_ctx.console.print("[yellow]No proxies configured[/yellow]")
        command_ctx.console.print("Add proxies using: proxywhirl pool add <URL>")
        raise typer.Exit(code=0)

    rotator = ProxyRotator(proxies=proxies, strategy=command_ctx.config.rotation_strategy)
    check_interval = interval if interval is not None else command_ctx.config.health_check_interval

    def check_health() -> list[ProxyStatus]:
        """Check health of all proxies."""
        results = []
        for proxy in rotator.pool.proxies:
            try:
                start_time = time.time()
                with httpx.Client(
                    proxy=proxy.url,
                    timeout=command_ctx.config.timeout,
                    verify=command_ctx.config.verify_ssl,
                ) as client:
                    response = client.get("https://httpbin.org/ip")

                elapsed_ms = (time.time() - start_time) * 1000
                is_healthy = response.status_code == 200

                # Update proxy health
                proxy.health_status = HealthStatus.HEALTHY if is_healthy else HealthStatus.DEGRADED
                if is_healthy:
                    proxy.last_success_at = datetime.now(timezone.utc)
                    proxy.total_successes += 1
                    proxy.consecutive_failures = 0
                else:
                    proxy.last_failure_at = datetime.now(timezone.utc)
                    proxy.total_failures += 1
                    proxy.consecutive_failures += 1

                proxy.total_requests += 1
                proxy.average_response_time_ms = elapsed_ms

                results.append(
                    ProxyStatus(
                        url=proxy.url,
                        health=proxy.health_status,
                        response_time_ms=elapsed_ms,
                        success_rate=proxy.success_rate,
                    )
                )

                if command_ctx.verbose:
                    command_ctx.console.print(
                        f"✓ {proxy.url}: {response.status_code} ({elapsed_ms:.0f}ms)"
                    )

            except Exception as e:
                # Mark as unhealthy
                proxy.health_status = HealthStatus.UNHEALTHY
                proxy.last_failure_at = datetime.now(timezone.utc)
                proxy.total_failures += 1
                proxy.total_requests += 1
                proxy.consecutive_failures += 1

                results.append(
                    ProxyStatus(
                        url=proxy.url,
                        health=HealthStatus.UNHEALTHY,
                        response_time_ms=0,
                        success_rate=proxy.success_rate,
                    )
                )

                if command_ctx.verbose:
                    command_ctx.console.print(f"✗ {proxy.url}: {e}")

        return results

    # Single check mode
    if not continuous:
        command_ctx.console.print("\n[bold]Checking proxy health...[/bold]\n")
        results = check_health()

        # Display results
        summary = PoolSummary(
            total_proxies=len(results),
            healthy=sum(1 for r in results if r.health == HealthStatus.HEALTHY),
            degraded=sum(1 for r in results if r.health == HealthStatus.DEGRADED),
            failed=sum(
                1 for r in results if r.health in (HealthStatus.UNHEALTHY, HealthStatus.DEAD)
            ),
            rotation_strategy=command_ctx.config.rotation_strategy,
            current_index=0,
            proxies=results,
        )

        if command_ctx.format == OutputFormat.JSON:
            render_json(summary.model_dump())
        elif command_ctx.format == OutputFormat.CSV:
            import csv
            import sys

            writer = csv.DictWriter(
                sys.stdout, fieldnames=["url", "health", "response_time_ms", "success_rate"]
            )
            writer.writeheader()
            writer.writerows([r.model_dump() for r in results])
        else:  # TEXT
            command_ctx.console.print("[bold]Health Check Results[/bold]")
            command_ctx.console.print(
                f"Healthy: [green]{summary.healthy}[/green] | "
                f"Degraded: [yellow]{summary.degraded}[/yellow] | "
                f"Failed: [red]{summary.failed}[/red]\n"
            )

            for r in results:
                health_color = (
                    "green"
                    if r.health == HealthStatus.HEALTHY
                    else "yellow"
                    if r.health == HealthStatus.DEGRADED
                    else "red"
                )
                command_ctx.console.print(
                    f"  [{health_color}]●[/{health_color}] {r.url} "
                    f"({r.response_time_ms:.0f}ms, {r.success_rate * 100:.0f}% success)"
                )

    # Continuous monitoring mode
    else:
        command_ctx.console.print(
            f"\n[bold]Continuous health monitoring (interval: {check_interval}s)[/bold]"
        )
        command_ctx.console.print("Press Ctrl+C to stop\n")

        try:
            iteration = 0
            while True:
                iteration += 1
                command_ctx.console.print(f"\n[dim]Check #{iteration}[/dim]")
                results = check_health()

                # Display brief summary
                healthy = sum(1 for r in results if r.health == HealthStatus.HEALTHY)
                degraded = sum(1 for r in results if r.health == HealthStatus.DEGRADED)
                failed = sum(
                    1 for r in results if r.health in (HealthStatus.UNHEALTHY, HealthStatus.DEAD)
                )

                command_ctx.console.print(
                    f"Status: [green]{healthy} healthy[/green] | "
                    f"[yellow]{degraded} degraded[/yellow] | "
                    f"[red]{failed} failed[/red]"
                )

                time.sleep(check_interval)

        except KeyboardInterrupt:
            command_ctx.console.print("\n[yellow]Monitoring stopped[/yellow]")
            raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
