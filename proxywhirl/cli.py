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
from urllib.parse import urlparse

import httpx
import typer
from rich.console import Console
from rich.table import Table

from proxywhirl.config import CLIConfig, discover_config, load_config
from proxywhirl.models import RequestResult
from proxywhirl.utils import CLILock, mask_proxy_url

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


def validate_target_url(url: str, allow_private: bool = False) -> None:
    """Validate a target URL to prevent SSRF attacks.

    Args:
        url: The URL to validate
        allow_private: If True, allow private/internal IP addresses (default: False)

    Raises:
        typer.Exit: If the URL is invalid or potentially dangerous
    """
    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        typer.secho(f"Error: Invalid URL format: {e}", err=True, fg="red")
        raise typer.Exit(code=1) from e

    # Validate scheme (only http/https allowed for target URLs)
    if parsed.scheme not in ("http", "https"):
        typer.secho(
            f"Error: Invalid URL scheme '{parsed.scheme}'. Only http:// and https:// are allowed.",
            err=True,
            fg="red",
        )
        typer.secho(
            "Rejected schemes: file://, data://, gopher://, ftp://, etc.",
            err=True,
            fg="yellow",
        )
        raise typer.Exit(code=1)

    # Validate hostname exists
    if not parsed.hostname:
        typer.secho("Error: URL must include a valid hostname", err=True, fg="red")
        raise typer.Exit(code=1)

    # Check for localhost/private addresses (SSRF protection)
    if not allow_private:
        hostname_lower = parsed.hostname.lower()

        # Block localhost variations
        localhost_patterns = [
            "localhost",
            "127.",  # 127.0.0.1, etc.
            "0.0.0.0",
            "[::",  # IPv6 localhost variations
            "::1",
        ]

        if any(hostname_lower.startswith(pattern) for pattern in localhost_patterns):
            typer.secho(
                f"Error: Access to localhost/loopback addresses is not allowed: {parsed.hostname}",
                err=True,
                fg="red",
            )
            typer.secho(
                "Use --allow-private flag if you need to test against local services",
                err=True,
                fg="yellow",
            )
            raise typer.Exit(code=1)

        # Block private IP ranges (RFC 1918)
        private_ip_patterns = [
            "10.",  # 10.0.0.0/8
            "172.16.",
            "172.17.",
            "172.18.",
            "172.19.",  # 172.16.0.0/12
            "172.20.",
            "172.21.",
            "172.22.",
            "172.23.",
            "172.24.",
            "172.25.",
            "172.26.",
            "172.27.",
            "172.28.",
            "172.29.",
            "172.30.",
            "172.31.",
            "192.168.",  # 192.168.0.0/16
            "169.254.",  # Link-local
        ]

        if any(hostname_lower.startswith(pattern) for pattern in private_ip_patterns):
            typer.secho(
                f"Error: Access to private IP addresses is not allowed: {parsed.hostname}",
                err=True,
                fg="red",
            )
            typer.secho(
                "Use --allow-private flag if you need to test against internal services",
                err=True,
                fg="yellow",
            )
            raise typer.Exit(code=1)

        # Block internal domain names
        internal_domains = [".local", ".internal", ".lan", ".corp"]
        if any(hostname_lower.endswith(domain) for domain in internal_domains):
            typer.secho(
                f"Error: Access to internal domain names is not allowed: {parsed.hostname}",
                err=True,
                fg="red",
            )
            typer.secho(
                "Use --allow-private flag if you need to test against internal services",
                err=True,
                fg="yellow",
            )
            raise typer.Exit(code=1)


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
        raise typer.Exit(code=1) from e

    # Initialize console with TTY detection
    console = Console(
        force_terminal=format == OutputFormat.TEXT,
        force_interactive=False,
        force_jupyter=False,
    )

    # Initialize lock if enabled
    lock = None
    if not no_lock:
        # Determine lock directory
        if config_file:
            lock_dir = config_file.parent
        else:
            from platformdirs import user_data_dir

            lock_dir = Path(user_data_dir("proxywhirl", "proxywhirl"))
            lock_dir.mkdir(parents=True, exist_ok=True)

        # Acquire lock and ensure cleanup is atomic
        lock = CLILock(config_dir=lock_dir)
        try:
            # Use context manager protocol for safe lock acquisition
            lock.__enter__()
            # Immediately register cleanup callback to ensure lock is ALWAYS released
            # even if the command crashes or raises an exception
            ctx.call_on_close(lambda: lock.__exit__(None, None, None))
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
    allow_private: bool = typer.Option(
        False,
        "--allow-private",
        help="Allow requests to localhost/private IPs (use with caution)",
    ),
) -> None:
    """Make an HTTP request through a rotating proxy.

    Examples:
      proxywhirl request https://api.example.com
      proxywhirl request -X POST -d '{"key":"value"}' https://api.example.com
      proxywhirl request -H "Authorization: Bearer token" https://api.example.com
      proxywhirl request http://localhost:8080 --allow-private
    """
    import time

    ctx = get_context()

    # Validate target URL to prevent SSRF attacks
    validate_target_url(url, allow_private=allow_private)

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
        # Explicit proxy override - use it directly
        proxy_url = proxy
    elif ctx.config.proxies:
        # Use rotator to select proxy based on configured strategy
        from proxywhirl.models import Proxy
        from proxywhirl.rotator import ProxyRotator

        # Convert config proxies to Proxy objects
        proxies_list = [
            Proxy(
                url=p.url,
                username=p.username,
                password=p.password,
            )
            for p in ctx.config.proxies
        ]

        # Create rotator with configured strategy
        rotator = ProxyRotator(proxies=proxies_list, strategy=ctx.config.rotation_strategy)

        # Select proxy using rotation strategy
        try:
            selected_proxy = rotator.strategy.select(rotator.pool)
            proxy_url = selected_proxy.url
        except Exception as e:
            if ctx.verbose:
                typer.secho(f"Proxy selection failed: {e}", err=True, fg="yellow")
            # Fallback to first proxy if selection fails
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
                    # Mask credentials in proxy URL for safe display
                    masked_proxy = mask_proxy_url(result.proxy_used)
                    ctx.console.print(f"[bold]Proxy:[/bold] {masked_proxy}")
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
                    "proxy_used": mask_proxy_url(result.proxy_used) if result.proxy_used else None,
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
                                mask_proxy_url(result.proxy_used) if result.proxy_used else "N/A",
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
    target_url: str = typer.Option(
        "https://httpbin.org/ip",
        "--target-url",
        help="Target URL for proxy testing (http/https only)",
    ),
    allow_private: bool = typer.Option(
        False,
        "--allow-private",
        help="Allow testing against localhost/private IPs (use with caution)",
    ),
) -> None:
    """Manage the proxy pool (list/add/remove/test).

    Examples:
      proxywhirl pool list
      proxywhirl pool add http://proxy1.com:8080
      proxywhirl pool remove http://proxy1.com:8080
      proxywhirl pool test http://proxy1.com:8080
      proxywhirl pool test http://proxy1.com:8080 --target-url https://api.example.com
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
        # List all proxies in pool (thread-safe snapshot)
        pool_proxies = rotator.pool.get_all_proxies()
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
                # Mask proxy URL for safe display
                masked_url = mask_proxy_url(ps.url)
                command_ctx.console.print(
                    f"  [{health_color}]●[/{health_color}] {masked_url} "
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

        # Find proxy by URL (thread-safe snapshot)
        proxy_obj = next((p for p in rotator.pool.get_all_proxies() if p.url == proxy), None)
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

        # Validate target URL to prevent SSRF
        validate_target_url(target_url, allow_private=allow_private)

        # Test proxy with HTTP request
        command_ctx.console.print(f"Testing proxy: {proxy}...")
        command_ctx.console.print(f"Target URL: {target_url}")

        try:
            import time

            start_time = time.time()
            with httpx.Client(
                proxy=proxy,
                timeout=command_ctx.config.timeout,
                verify=command_ctx.config.verify_ssl,
            ) as client:
                response = client.get(target_url)
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
            raise typer.Exit(code=1) from e


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
            raise typer.Exit(code=1) from e


@app.command()
def export(
    output: Path = typer.Option(
        Path("docs/proxy-lists"),
        "--output",
        "-o",
        help="Output directory for exported files",
    ),
    db: Path = typer.Option(
        Path("proxywhirl.db"),
        "--db",
        help="Path to SQLite database",
    ),
    stats_only: bool = typer.Option(
        False,
        "--stats-only",
        help="Only export statistics",
    ),
    proxies_only: bool = typer.Option(
        False,
        "--proxies-only",
        help="Only export proxy list",
    ),
) -> None:
    """Export proxy data and statistics for web dashboard.

    Examples:
      proxywhirl export
      proxywhirl export --output ./exports
      proxywhirl export --stats-only
      proxywhirl export --proxies-only --db custom.db
    """
    import asyncio

    from proxywhirl.exports import export_for_web

    command_ctx = get_context()

    # Determine what to export
    include_stats = not proxies_only
    include_proxies = not stats_only

    # Run async export
    try:
        outputs = asyncio.run(
            export_for_web(
                db_path=db,
                output_dir=output,
                include_stats=include_stats,
                include_rich_proxies=include_proxies,
            )
        )

        # Report results
        if command_ctx.format == OutputFormat.JSON:
            render_json({"exports": {k: str(v) for k, v in outputs.items()}})
        else:
            command_ctx.console.print(f"[green]✓[/green] Export completed to {output}")
            for export_type, path in outputs.items():
                command_ctx.console.print(f"  {export_type}: {path}")

    except Exception as e:
        command_ctx.console.print(f"[red]Export failed:[/red] {e}")
        raise typer.Exit(code=1) from e


def _parse_fetch_config(
    no_validate: bool,
    timeout: int,
    concurrency: int,
) -> dict[str, Any]:
    """Parse and validate fetch configuration parameters.

    Args:
        no_validate: Skip proxy validation
        timeout: Validation timeout in seconds
        concurrency: Concurrent validation requests

    Returns:
        Dict containing validated configuration
    """
    return {
        "validate": not no_validate,
        "timeout": timeout,
        "max_concurrent": concurrency,
    }


async def _fetch_from_sources(
    validate: bool,
    timeout: int,
    max_concurrent: int,
) -> list[Any]:
    """Fetch proxies from all configured sources.

    Args:
        validate: Whether to validate proxies
        timeout: Validation timeout in seconds
        max_concurrent: Maximum concurrent validation requests

    Returns:
        List of fetched Proxy objects

    Raises:
        Exception: If fetching fails
    """
    from proxywhirl.sources import fetch_all_sources

    return await fetch_all_sources(
        validate=validate,
        timeout=timeout,
        max_concurrent=max_concurrent,
    )


async def _save_results(proxies: list[Any], db_path: Path) -> None:
    """Save fetched proxies to database.

    Args:
        proxies: List of Proxy objects to save
        db_path: Path to SQLite database file
    """
    from proxywhirl.storage import SQLiteStorage

    storage = SQLiteStorage(db_path)
    await storage.initialize()
    try:
        for proxy in proxies:
            await storage.save(proxy)
    finally:
        await storage.close()


async def _export_results(db_path: Path, output_dir: Path) -> None:
    """Export proxy data for web dashboard.

    Args:
        db_path: Path to SQLite database file
        output_dir: Output directory for exported files
    """
    from proxywhirl.exports import export_for_web

    await export_for_web(
        db_path=db_path,
        output_dir=output_dir,
    )


def _display_summary(
    context: CommandContext,
    proxies: list[Any],
    no_validate: bool,
) -> None:
    """Display fetch summary to user.

    Args:
        context: Command context with format settings
        proxies: List of fetched Proxy objects
        no_validate: Whether validation was skipped
    """
    if context.format == OutputFormat.JSON:
        render_json(
            {
                "total": len(proxies),
                "validated": not no_validate,
            }
        )
    else:
        context.console.print(f"[green]✓[/green] Fetched {len(proxies)} proxies")


@app.command()
def fetch(
    no_validate: bool = typer.Option(
        False,
        "--no-validate",
        help="Skip proxy validation",
    ),
    no_save_db: bool = typer.Option(
        False,
        "--no-save-db",
        help="Don't save to database",
    ),
    no_export: bool = typer.Option(
        False,
        "--no-export",
        help="Don't export to files",
    ),
    timeout: int = typer.Option(
        10,
        "--timeout",
        help="Validation timeout in seconds",
    ),
    concurrency: int = typer.Option(
        100,
        "--concurrency",
        help="Concurrent validation requests",
    ),
) -> None:
    """Fetch proxies from configured sources.

    Examples:
      proxywhirl fetch
      proxywhirl fetch --no-validate
      proxywhirl fetch --timeout 5 --concurrency 50
    """
    import asyncio

    command_ctx = get_context()

    # Parse configuration
    fetch_config = _parse_fetch_config(no_validate, timeout, concurrency)

    # Run fetch
    command_ctx.console.print("[bold]Fetching proxies...[/bold]")
    try:
        proxies = asyncio.run(
            _fetch_from_sources(
                validate=fetch_config["validate"],
                timeout=fetch_config["timeout"],
                max_concurrent=fetch_config["max_concurrent"],
            )
        )
    except Exception as e:
        command_ctx.console.print(f"[red]Fetch failed:[/red] {e}")
        raise typer.Exit(code=1) from e

    # Display summary
    _display_summary(command_ctx, proxies, no_validate)

    # Save to database if requested
    if not no_save_db:
        command_ctx.console.print("[bold]Saving to database...[/bold]")
        try:
            asyncio.run(_save_results(proxies, Path("proxywhirl.db")))
            command_ctx.console.print("[green]✓[/green] Saved to database")
        except Exception as e:
            command_ctx.console.print(f"[red]Save failed:[/red] {e}")
            raise typer.Exit(code=1) from e

    # Export if requested
    if not no_export:
        command_ctx.console.print("[bold]Exporting...[/bold]")
        try:
            asyncio.run(
                _export_results(
                    db_path=Path("proxywhirl.db"),
                    output_dir=Path("docs/proxy-lists"),
                )
            )
            command_ctx.console.print("[green]✓[/green] Exported to docs/proxy-lists")
        except Exception as e:
            command_ctx.console.print(f"[red]Export failed:[/red] {e}")
            raise typer.Exit(code=1) from e


@app.command()
def stats(
    retry: bool = typer.Option(
        False,
        "--retry",
        help="Show retry metrics",
    ),
    circuit_breaker: bool = typer.Option(
        False,
        "--circuit-breaker",
        help="Show circuit breaker events",
    ),
    hours: int = typer.Option(
        24,
        "--hours",
        "-r",
        help="Time window in hours",
    ),
) -> None:
    """Show proxy pool statistics.

    Examples:
      proxywhirl stats
      proxywhirl stats --retry
      proxywhirl stats --circuit-breaker
      proxywhirl stats --hours 12
    """
    from datetime import datetime, timedelta, timezone

    from proxywhirl.retry_metrics import RetryMetrics

    command_ctx = get_context()

    # If no flags specified, show both
    show_retry = retry or (not retry and not circuit_breaker)
    show_circuit = circuit_breaker or (not retry and not circuit_breaker)

    # Load metrics (would typically come from storage)
    metrics = RetryMetrics()

    # Prepare output data
    output_data: dict[str, Any] = {}

    if show_retry:
        summary = metrics.get_summary()
        output_data["retry"] = {
            "total_requests": summary.get("total_requests", 0),
            "total_retries": summary.get("total_retries", 0),
            "success_rate": summary.get("success_rate", 0.0),
        }

    if show_circuit:
        # Get circuit breaker events (filtering by hours if needed)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        events = [e for e in metrics.circuit_breaker_events if e.timestamp >= cutoff]

        output_data["circuit_breaker"] = {
            "total_events": len(events),
            "events": [
                {
                    "proxy_id": e.proxy_id,
                    "from_state": e.from_state.value,
                    "to_state": e.to_state.value,
                    "timestamp": e.timestamp.isoformat(),
                }
                for e in events[:10]  # Limit to 10 most recent
            ],
        }

    # Render output
    if command_ctx.format == OutputFormat.JSON:
        render_json(output_data)
    elif command_ctx.format == OutputFormat.CSV:
        # For CSV, flatten to table format
        if show_retry and "retry" in output_data:
            data = output_data["retry"]
            render_csv(
                {
                    "table": {
                        "headers": ["metric", "value"],
                        "rows": [[k, str(v)] for k, v in data.items()],
                    }
                }
            )
        elif show_circuit and "circuit_breaker" in output_data:
            events = output_data["circuit_breaker"]["events"]
            if events:
                render_csv(
                    {
                        "table": {
                            "headers": ["proxy_id", "from_state", "to_state", "timestamp"],
                            "rows": [
                                [e["proxy_id"], e["from_state"], e["to_state"], e["timestamp"]]
                                for e in events
                            ],
                        }
                    }
                )
    else:  # TEXT
        command_ctx.console.print("\n[bold]Proxy Pool Statistics[/bold]\n")

        if show_retry and "retry" in output_data:
            command_ctx.console.print("[bold]Retry Metrics[/bold]")
            retry_data = output_data["retry"]
            command_ctx.console.print(f"  Total Requests: {retry_data['total_requests']}")
            command_ctx.console.print(f"  Total Retries: {retry_data['total_retries']}")
            command_ctx.console.print(f"  Success Rate: {retry_data['success_rate']:.1%}\n")

        if show_circuit and "circuit_breaker" in output_data:
            command_ctx.console.print("[bold]Circuit Breaker Events[/bold]")
            cb_data = output_data["circuit_breaker"]
            command_ctx.console.print(f"  Total Events: {cb_data['total_events']}")
            if cb_data["events"]:
                command_ctx.console.print("\n  Recent Events:")
                for event in cb_data["events"]:
                    command_ctx.console.print(
                        f"    {event['proxy_id']}: {event['from_state']} → {event['to_state']}"
                    )
            else:
                command_ctx.console.print(f"  No events in the last {hours} hours")


@app.command(name="setup-geoip")
def setup_geoip(
    check: bool = typer.Option(
        False,
        "--check",
        help="Check if GeoIP database is available",
    ),
) -> None:
    """Setup GeoIP database for proxy geolocation.

    Examples:
      proxywhirl setup-geoip
      proxywhirl setup-geoip --check
    """
    from proxywhirl.enrichment import is_geoip_available

    command_ctx = get_context()

    if check:
        # Check if database is available
        available = is_geoip_available()

        if command_ctx.format == OutputFormat.JSON:
            render_json({"available": available})
        else:
            if available:
                command_ctx.console.print("[green]✓[/green] GeoIP database is available")
            else:
                command_ctx.console.print("[yellow]![/yellow] GeoIP database not found")

    else:
        # Show installation instructions
        if command_ctx.format == OutputFormat.JSON:
            render_json(
                {
                    "instructions": "Download MaxMind GeoLite2 database",
                    "url": "https://dev.maxmind.com/geoip/geolite2-free-geolocation-data",
                }
            )
        else:
            command_ctx.console.print("\n[bold]GeoIP Database Setup[/bold]\n")
            command_ctx.console.print(
                "ProxyWhirl uses MaxMind GeoLite2 for offline IP geolocation.\n"
            )
            command_ctx.console.print("[bold]Instructions:[/bold]")
            command_ctx.console.print("  1. Sign up for a free MaxMind account:")
            command_ctx.console.print(
                "     https://dev.maxmind.com/geoip/geolite2-free-geolocation-data"
            )
            command_ctx.console.print("\n  2. Download GeoLite2-City.mmdb")
            command_ctx.console.print("\n  3. Place the database file in one of these locations:")
            command_ctx.console.print("     - ./GeoLite2-City.mmdb")
            command_ctx.console.print("     - ~/.local/share/proxywhirl/GeoLite2-City.mmdb")
            command_ctx.console.print("     - /usr/share/GeoIP/GeoLite2-City.mmdb")
            command_ctx.console.print("\n  4. Run 'proxywhirl setup-geoip --check' to verify")


@app.command()
def health(
    continuous: bool = typer.Option(False, "--continuous", "-C", help="Run continuously"),
    interval: int | None = typer.Option(None, "--interval", "-i", help="Check interval in seconds"),
    target_url: str | None = typer.Option(
        None, "--target-url", "-t", help="URL to test proxy connectivity against (http/https only)"
    ),
    allow_private: bool = typer.Option(
        False,
        "--allow-private",
        help="Allow testing against localhost/private IPs (use with caution)",
    ),
) -> None:
    """Check health of all proxies in the pool.

    Examples:
      proxywhirl health
      proxywhirl health --continuous --interval 60
      proxywhirl health -C -i 60
      proxywhirl health --target-url https://api.example.com
      proxywhirl health --target-url http://localhost:8080 --allow-private
    """
    import time
    from datetime import datetime, timezone

    import httpx

    from proxywhirl.models import HealthStatus, PoolSummary, Proxy, ProxyStatus
    from proxywhirl.rotator import ProxyRotator

    command_ctx = get_context()

    # Validate target URL if provided
    if target_url:
        validate_target_url(target_url, allow_private=allow_private)

    # Determine the URL to test against
    test_url = target_url if target_url else "https://httpbin.org/ip"

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
        # Use thread-safe snapshot
        for proxy in rotator.pool.get_all_proxies():
            try:
                start_time = time.time()
                with httpx.Client(
                    proxy=proxy.url,
                    timeout=command_ctx.config.timeout,
                    verify=command_ctx.config.verify_ssl,
                ) as client:
                    response = client.get(test_url)

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


@app.command()
def sources(
    validate: bool = typer.Option(
        False,
        "--validate",
        "-v",
        help="Validate all sources and check for stale/broken ones",
    ),
    timeout: float = typer.Option(
        15.0,
        "--timeout",
        "-t",
        help="Timeout per source in seconds",
    ),
    concurrency: int = typer.Option(
        20,
        "--concurrency",
        "-j",
        help="Maximum concurrent requests",
    ),
    fail_on_unhealthy: bool = typer.Option(
        False,
        "--fail-on-unhealthy",
        "-f",
        help="Exit with error code if any sources are unhealthy (for CI)",
    ),
) -> None:
    """List and validate proxy sources.

    By default, lists all configured proxy sources with their URLs.
    Use --validate to check which sources are working and which are stale.

    Examples:
        proxywhirl sources              # List all sources
        proxywhirl sources --validate   # Validate all sources
        proxywhirl sources -v -f        # Validate and fail if any unhealthy (CI mode)
    """
    import asyncio

    from rich.table import Table

    from proxywhirl.sources import (
        ALL_HTTP_SOURCES,
        ALL_SOCKS4_SOURCES,
        ALL_SOCKS5_SOURCES,
        ALL_SOURCES,
    )
    from proxywhirl.sources import (
        validate_sources as validate_sources_async,
    )

    command_ctx = get_context()

    if validate:
        # Validation mode
        command_ctx.console.print(f"[bold]Validating {len(ALL_SOURCES)} proxy sources...[/bold]\n")

        report = asyncio.run(validate_sources_async(timeout=timeout, concurrency=concurrency))

        # Create results table
        table = Table(title="Source Validation Results")
        table.add_column("Status", style="bold", width=8)
        table.add_column("Source", style="cyan")
        table.add_column("Response", justify="right")
        table.add_column("Size", justify="right")
        table.add_column("Time", justify="right")
        table.add_column("Error")

        # Sort: unhealthy first, then by name
        sorted_results = sorted(report.results, key=lambda r: (r.is_healthy, r.name.lower()))

        for result in sorted_results:
            if result.is_healthy:
                status = "[green]✓ OK[/green]"
                error = ""
            else:
                status = "[red]✗ FAIL[/red]"
                error = result.error or (
                    f"HTTP {result.status_code}" if result.status_code else "No response"
                )

            size = f"{result.content_length:,}" if result.content_length else "-"
            time_str = f"{result.response_time_ms:.0f}ms"
            resp = str(result.status_code) if result.status_code else "-"

            table.add_row(status, result.name, resp, size, time_str, error[:30] if error else "")

        command_ctx.console.print(table)

        # Summary
        command_ctx.console.print("\n[bold]Summary:[/bold]")
        command_ctx.console.print(
            f"  Total: {report.total_sources} | "
            f"[green]Healthy: {report.healthy_sources}[/green] | "
            f"[red]Unhealthy: {report.unhealthy_sources}[/red] | "
            f"Time: {report.total_time_ms:.0f}ms"
        )

        if report.unhealthy:
            command_ctx.console.print("\n[bold red]Unhealthy sources:[/bold red]")
            for result in report.unhealthy:
                error_msg = result.error or (
                    f"HTTP {result.status_code}" if result.status_code else "No response"
                )
                command_ctx.console.print(f"  • {result.name}: {error_msg}")

            if fail_on_unhealthy:
                command_ctx.console.print(
                    f"\n[red]Exiting with error: {report.unhealthy_sources} unhealthy source(s)[/red]"
                )
                raise typer.Exit(code=1)
        else:
            command_ctx.console.print("\n[green]All sources are healthy![/green]")

    else:
        # List mode
        command_ctx.console.print("[bold]Configured Proxy Sources[/bold]\n")

        command_ctx.console.print(f"[cyan]HTTP Sources ({len(ALL_HTTP_SOURCES)}):[/cyan]")
        for src in ALL_HTTP_SOURCES:
            url_display = str(src.url)[:80]
            command_ctx.console.print(f"  • {url_display}{'...' if len(str(src.url)) > 80 else ''}")

        command_ctx.console.print(f"\n[cyan]SOCKS4 Sources ({len(ALL_SOCKS4_SOURCES)}):[/cyan]")
        for src in ALL_SOCKS4_SOURCES:
            url_display = str(src.url)[:80]
            command_ctx.console.print(f"  • {url_display}{'...' if len(str(src.url)) > 80 else ''}")

        command_ctx.console.print(f"\n[cyan]SOCKS5 Sources ({len(ALL_SOCKS5_SOURCES)}):[/cyan]")
        for src in ALL_SOCKS5_SOURCES:
            url_display = str(src.url)[:80]
            command_ctx.console.print(f"  • {url_display}{'...' if len(str(src.url)) > 80 else ''}")

        command_ctx.console.print(f"\n[bold]Total: {len(ALL_SOURCES)} sources[/bold]")
        command_ctx.console.print("\n[dim]Use --validate to check source health[/dim]")


if __name__ == "__main__":
    app()
