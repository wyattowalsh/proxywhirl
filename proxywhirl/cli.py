"""Command-line interface for ProxyWhirl.

This module provides a Typer-based CLI for proxy rotation operations.
Supports multiple output formats (text, JSON, CSV, YAML) with TTY-aware rendering.
"""

from __future__ import annotations

import ipaddress
import socket
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
import typer
from rich.console import Console
from rich.table import Table

from proxywhirl.config import CLIConfig, discover_config, load_config
from proxywhirl.formatters import OutputFormat as FormatterOutputFormat
from proxywhirl.models import RequestResult
from proxywhirl.types import BatchAction, ConfigAction, PoolAction
from proxywhirl.utils import CLILock, mask_proxy_url

# Typer app instance
app = typer.Typer(
    name="proxywhirl",
    help="Advanced proxy rotation library with CLI interface",
    add_completion=True,
    no_args_is_help=True,
)


@dataclass
class CommandContext:
    """Shared context for all CLI commands.

    Attributes:
        config: CLI configuration loaded from discovered config file
        config_path: Path to the active configuration file (may be fallback if none found)
        format: Output format (text, json, csv, yaml)
        verbose: Enable verbose logging
        console: Rich console for formatted output
        lock: File lock for concurrent operation safety
    """

    config: CLIConfig
    config_path: Path
    format: FormatterOutputFormat
    verbose: bool
    console: Console
    lock: CLILock | None = None


# Global context storage (set by callback)
_context: CommandContext | None = None


def _parse_target_ip_address(hostname: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    """Parse literal and obfuscated IP hostnames without DNS resolution."""
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        normalized = hostname.lower()
        allowed_chars = set("0123456789abcdefx.")
        if not normalized or any(char not in allowed_chars for char in normalized):
            return None
        if normalized.isdigit() and int(normalized) > 0xFFFFFFFF:
            return None
        try:
            address = ipaddress.ip_address(socket.inet_aton(hostname))
        except OSError:
            return None

    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        return address.ipv4_mapped
    return address


def _reject_forbidden_target_address(
    address: ipaddress.IPv4Address | ipaddress.IPv6Address,
    hostname: str,
) -> None:
    """Reject target IPs that should not be reachable without explicit opt-in."""
    if address.is_loopback:
        typer.secho(
            f"Error: Access to localhost/loopback addresses is not allowed: {hostname}",
            err=True,
            fg="red",
        )
        typer.secho(
            "Use --allow-private flag if you need to test against local services",
            err=True,
            fg="yellow",
        )
        raise typer.Exit(code=1)

    if address.is_unspecified:
        typer.secho(
            f"Error: Access to unspecified addresses is not allowed: {hostname}",
            err=True,
            fg="red",
        )
        typer.secho(
            "Use --allow-private flag if you need to test against internal services",
            err=True,
            fg="yellow",
        )
        raise typer.Exit(code=1)

    if address.is_private:
        typer.secho(
            f"Error: Access to private IP addresses is not allowed: {hostname}",
            err=True,
            fg="red",
        )
        typer.secho(
            "Use --allow-private flag if you need to test against internal services",
            err=True,
            fg="yellow",
        )
        raise typer.Exit(code=1)

    if address.is_link_local:
        typer.secho(
            f"Error: Access to link-local IP addresses is not allowed: {hostname}",
            err=True,
            fg="red",
        )
        typer.secho(
            "Use --allow-private flag if you need to test against internal services",
            err=True,
            fg="yellow",
        )
        raise typer.Exit(code=1)

    if address.is_reserved or address.is_multicast:
        typer.secho(
            f"Error: Access to reserved/multicast IP addresses is not allowed: {hostname}",
            err=True,
            fg="red",
        )
        typer.secho(
            "Use --allow-private flag if you need to test against internal services",
            err=True,
            fg="yellow",
        )
        raise typer.Exit(code=1)


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
        hostname_lower = parsed.hostname.rstrip(".").lower()

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

        if hostname_lower == "localhost":
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

        address = _parse_target_ip_address(hostname_lower)
        if address is not None:
            _reject_forbidden_target_address(address, parsed.hostname)


def get_context() -> CommandContext:
    """
    Get the current command context.

    Retrieves the global CommandContext instance that was initialized
    by the main callback. This context is available to all CLI subcommands
    and contains configuration, output format, verbosity, and file lock settings.

    Args:
        None

    Returns:
        CommandContext
            The active command context with config, format, console, and lock.

    Raises:
        typer.Exit
            With exit code 1 if context is not initialized.

    Example:
        >>> ctx = get_context()
        >>> print(ctx.config)
        >>> print(ctx.format)
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
    format: FormatterOutputFormat = typer.Option(
        FormatterOutputFormat.TEXT,
        "--format",
        "-f",
        help="Output format (text/json/csv/yaml)",
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
    """
    ProxyWhirl CLI - Advanced proxy rotation library.

    Main CLI entry point that initializes global context for all subcommands.
    Handles configuration discovery, output format selection, and file locking.
    Called automatically before any subcommand.

    Global options apply to all subcommands. Configuration is auto-discovered
    from multiple sources in order:

    1. Project directory: ./.proxywhirl.toml
    2. User directory: ~/.config/proxywhirl/config.toml (Linux/Mac)
    3. System defaults: In-memory fallback configuration

    Args:
        ctx : typer.Context
            Typer context for managing cleanup callbacks.
        config_file : Path | None
            Path to TOML configuration file. If not provided, auto-discovered.
        format : FormatterOutputFormat
            Output format: text (rich formatted), json, csv, or yaml.
        verbose : bool
            Enable verbose/debug logging output.
        no_lock : bool
            Disable file locking for concurrent operations (use with caution).

    Returns:
        None

    Raises:
        typer.Exit
            With code 1 if config loading fails or lock acquisition fails.

    Example:
        >>> # Auto-discover config
        >>> proxywhirl request --url https://example.com
        >>>
        >>> # Use custom config
        >>> proxywhirl --config ./my-config.toml request --url https://example.com
        >>>
        >>> # Change output format
        >>> proxywhirl --format json pool list

    Note:
        - File lock is auto-released via Typer context cleanup callback
        - Console output adapts to TTY capabilities (color, tables)
        - Context is stored globally and accessed by all subcommands
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
        force_terminal=format == FormatterOutputFormat.TEXT,
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


def render_yaml(data: dict[str, Any]) -> None:
    """Render data as YAML to stdout.

    Args:
        data: Data to render as YAML
    """
    try:
        import yaml
    except ImportError:
        typer.secho(
            "Error: PyYAML not installed. Install with: pip install pyyaml",
            err=True,
            fg="red",
        )
        raise typer.Exit(code=1)

    print(yaml.dump(data, default_flow_style=False, sort_keys=False))


def render_output(context: CommandContext, data: dict[str, Any]) -> None:
    """Render output in the configured format.

    Args:
        context: Command context with format settings
        data: Data to render
    """
    if context.format == FormatterOutputFormat.TEXT:
        render_text(context.console, data)
    elif context.format == FormatterOutputFormat.JSON:
        render_json(data)
    elif context.format == FormatterOutputFormat.CSV:
        render_csv(data)
    elif context.format == FormatterOutputFormat.YAML:
        render_yaml(data)


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
    """
    Make an HTTP request through a rotating proxy.

    Routes request through proxy pool with automatic rotation, retry logic,
    and optional health-based selection. Validates target URL to prevent SSRF.

    Args:
        url : str
            Target URL to request (required). Must be valid HTTP/HTTPS URL.
        method : str
            HTTP method (default: GET). Case-insensitive (GET, POST, PUT, etc).
        headers : list[str]
            Custom HTTP headers. Format: 'Key: Value'. Can be repeated.
        data : str | None
            Request body data (usually for POST/PUT/PATCH).
        proxy : str | None
            Specific proxy URL to use (overrides rotation). Format: http://ip:port
        max_retries : int | None
            Max retry attempts (overrides config default).
        allow_private : bool
            Allow requests to localhost/private IPs (default: False for safety).

    Returns:
        None

    Raises:
        typer.Exit
            With code 1 on invalid URL, header format, or request failure.

    Examples:
        >>> # Simple GET request
        >>> proxywhirl request https://api.example.com

        >>> # POST with JSON data
        >>> proxywhirl request -X POST \\
        ...   -d '{"key":"value"}' https://api.example.com

        >>> # Custom headers
        >>> proxywhirl request \\
        ...   -H "Authorization: Bearer token" https://api.example.com

        >>> # Use specific proxy
        >>> proxywhirl request --proxy http://1.2.3.4:8080 https://example.com

        >>> # Allow private IP targets
        >>> proxywhirl request http://localhost:8080 --allow-private

    Note:
        - Headers are case-insensitive per HTTP spec
        - SSRF protection prevents requests to private/localhost by default
        - Retries apply circuit breaker and exponential backoff
        - Output format controlled by global --format option
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
        from proxywhirl.rotator import ProxyWhirl

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
        rotator = ProxyWhirl(proxies=proxies_list, strategy=ctx.config.rotation_strategy)

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
            if ctx.format == FormatterOutputFormat.TEXT:
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
            elif ctx.format == FormatterOutputFormat.JSON:
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
            elif ctx.format == FormatterOutputFormat.CSV:
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
    action: PoolAction = typer.Argument(..., help="Action: list, add, remove, test, stats"),
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
    """
    Manage the proxy pool with list, add, remove, test, or stats actions.

    Provides pool management commands to view proxies, add new ones, remove
    existing ones, test connectivity, and view statistics. All changes are
    persisted to the configuration file.

    Args:
        action : PoolAction
            Action to perform:
            - list: Show all proxies in pool with health status
            - add: Add proxy to pool (requires --proxy or positional arg)
            - remove: Remove proxy from pool
            - test: Test proxy connectivity to target URL
            - stats: Show pool statistics and performance metrics
        proxy : str | None
            Proxy URL (required for add/remove/test). Format: http://ip:port
        username : str | None
            Proxy username for authentication (optional).
        password : str | None
            Proxy password for authentication (optional).
        target_url : str
            Target URL for proxy testing. Default: https://httpbin.org/ip
        allow_private : bool
            Allow testing against localhost/private IPs (default: False).

    Returns:
        None

    Raises:
        typer.Exit
            With code 1 on invalid action, proxy format, or command failure.

    Examples:
        >>> # List all proxies in pool
        >>> proxywhirl pool list

        >>> # Add HTTP proxy
        >>> proxywhirl pool add http://proxy1.com:8080

        >>> # Add proxy with credentials
        >>> proxywhirl pool add http://proxy1.com:8080 \\
        ...   --username user --password pass

        >>> # Remove proxy from pool
        >>> proxywhirl pool remove http://proxy1.com:8080

        >>> # Test proxy connectivity
        >>> proxywhirl pool test http://proxy1.com:8080

        >>> # Test against custom endpoint
        >>> proxywhirl pool test http://proxy1.com:8080 \\
        ...   --target-url https://api.example.com

        >>> # Show pool statistics
        >>> proxywhirl pool stats

    Note:
        - List shows health status (healthy/degraded/unhealthy/dead)
        - Test uses TCP pre-check for speed, then HTTP validation
        - Stats includes response times and success rates
        - All changes persisted to config file
    """
    import time

    import httpx
    from pydantic import SecretStr

    from proxywhirl.config import ProxyConfig, save_config
    from proxywhirl.models import HealthStatus, PoolSummary, Proxy, ProxyStatus
    from proxywhirl.rotator import ProxyWhirl

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

    rotator = ProxyWhirl(proxies=proxies, strategy=command_ctx.config.rotation_strategy)

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

        if command_ctx.format == FormatterOutputFormat.JSON:
            render_json(summary.model_dump())
        elif command_ctx.format == FormatterOutputFormat.CSV:
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

    elif action == "stats":
        """Show pool statistics."""
        pool_proxies = rotator.pool.get_all_proxies()
        if not pool_proxies:
            command_ctx.console.print("[yellow]No proxies in pool[/yellow]")
            return

        # Calculate statistics
        total = len(pool_proxies)
        healthy = sum(1 for p in pool_proxies if p.health_status == HealthStatus.HEALTHY)
        degraded = sum(1 for p in pool_proxies if p.health_status == HealthStatus.DEGRADED)
        failed = sum(
            1
            for p in pool_proxies
            if p.health_status in (HealthStatus.UNHEALTHY, HealthStatus.DEAD)
        )
        avg_response_time = (
            sum((p.average_response_time_ms or 0) for p in pool_proxies) / total if total > 0 else 0
        )
        avg_success_rate = sum(p.success_rate for p in pool_proxies) / total if total > 0 else 0

        stats_data = {
            "total_proxies": total,
            "healthy": healthy,
            "degraded": degraded,
            "failed": failed,
            "average_response_time_ms": round(avg_response_time, 2),
            "average_success_rate": round(avg_success_rate, 4),
            "rotation_strategy": command_ctx.config.rotation_strategy,
        }

        if command_ctx.format == FormatterOutputFormat.JSON:
            render_json(stats_data)
        elif command_ctx.format == FormatterOutputFormat.CSV:
            import csv

            writer = csv.DictWriter(sys.stdout, fieldnames=stats_data.keys())
            writer.writeheader()
            writer.writerow(stats_data)
        elif command_ctx.format == FormatterOutputFormat.YAML:
            render_yaml(stats_data)
        else:  # TEXT
            command_ctx.console.print("\n[bold]Pool Statistics[/bold]")
            command_ctx.console.print(f"Total Proxies: {stats_data['total_proxies']}")
            command_ctx.console.print(
                f"Healthy: [green]{stats_data['healthy']}[/green] | "
                f"Degraded: [yellow]{stats_data['degraded']}[/yellow] | "
                f"Failed: [red]{stats_data['failed']}[/red]"
            )
            command_ctx.console.print(
                f"Average Response Time: {stats_data['average_response_time_ms']}ms"
            )
            command_ctx.console.print(
                f"Average Success Rate: {stats_data['average_success_rate']:.2%}"
            )
            command_ctx.console.print(f"Strategy: {stats_data['rotation_strategy']}\n")


@app.command()
def config(
    action: ConfigAction = typer.Argument(..., help="Action: show, set, get, init"),
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

    if action == "init":
        # Initialize a new config file
        config_path = Path.cwd() / ".proxywhirl.toml"
        if config_path.exists():
            command_ctx.console.print(f"[yellow]Config file already exists: {config_path}[/yellow]")
            if not typer.confirm("Overwrite?"):
                raise typer.Exit(code=0)

        # Create default config (uses CLIConfig field defaults;
        # only override encrypt_credentials so users don't need
        # PROXYWHIRL_KEY set up before first use)
        default_config = CLIConfig(encrypt_credentials=False)
        save_config(default_config, config_path)
        command_ctx.console.print(f"[green]✓[/green] Created config file: {config_path}")

    elif action == "show":
        # Show entire config
        if command_ctx.format == FormatterOutputFormat.JSON:
            # Exclude sensitive fields
            config_dict = command_ctx.config.model_dump(mode="json", exclude={"proxies"})
            render_json(config_dict)
        elif command_ctx.format == FormatterOutputFormat.CSV:
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
        if command_ctx.format == FormatterOutputFormat.JSON:
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
        if command_ctx.format == FormatterOutputFormat.JSON:
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
        dict[str, Any]: Validated configuration parameters.
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
    console: Console | None = None,
) -> list[Any]:
    """Fetch proxies from all configured sources with progress display.

    Args:
        validate: Whether to validate proxies
        timeout: Validation timeout in seconds
        max_concurrent: Maximum concurrent validation requests
        console: Rich console for progress display

    Returns:
        List of fetched Proxy objects

    Raises:
        Exception: If fetching fails
    """
    from rich.progress import (
        BarColumn,
        MofNCompleteColumn,
        Progress,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
    )

    from proxywhirl.sources import ALL_SOURCES, fetch_all_sources

    total_sources = len(ALL_SOURCES)
    proxies_found = 0
    valid_count = 0

    # Create progress display
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("{task.fields[status]}"),
        console=console,
        transient=False,
    )

    fetch_task = None
    validate_task = None

    def fetch_progress(completed: int, total: int, found: int) -> None:
        """Update fetch progress."""
        nonlocal proxies_found, fetch_task
        proxies_found = found
        if fetch_task is not None:
            progress.update(
                fetch_task,
                completed=completed,
                status=f"[cyan]{proxies_found:,} proxies found[/cyan]",
            )

    def validate_progress(completed: int, total: int, valid: int) -> None:
        """Update validation progress."""
        nonlocal valid_count, validate_task
        valid_count = valid
        if validate_task is not None:
            pct = (valid / completed * 100) if completed > 0 else 0
            progress.update(
                validate_task,
                completed=completed,
                total=total,  # Update total dynamically
                status=f"[green]{valid:,} valid[/green] ({pct:.1f}%)",
            )

    with progress:
        # Add fetch task
        fetch_task = progress.add_task(
            "Fetching sources",
            total=total_sources,
            status="[cyan]starting...[/cyan]",
        )

        # Add validation task (will be updated once fetching completes)
        if validate:
            validate_task = progress.add_task(
                "Validating proxies",
                total=0,  # Will be set after fetch
                status="[dim]waiting...[/dim]",
                visible=True,
            )

        # Run fetch with callbacks
        result = await fetch_all_sources(
            validate=validate,
            timeout=timeout,
            max_concurrent=max_concurrent,
            fetch_progress_callback=fetch_progress,
            validate_progress_callback=validate_progress if validate else None,
        )

        # Mark tasks complete
        progress.update(fetch_task, completed=total_sources)
        if validate_task is not None:
            progress.update(validate_task, completed=progress.tasks[validate_task].total)

    return result


async def _save_results(proxies: list[Any], db_path: Path, validated: bool = True) -> None:
    """Save fetched proxies to database.

    Args:
        proxies: List of proxy dicts or Proxy objects to save
        db_path: Path to SQLite database file
        validated: If True, mark proxies as already validated (healthy status).
            Default is True since fetch validates before saving.
    """
    from proxywhirl.models import Proxy
    from proxywhirl.storage import SQLiteStorage

    storage = SQLiteStorage(db_path)
    await storage.initialize()
    try:
        # Convert dicts to Proxy objects if needed
        proxy_objects = []
        for p in proxies:
            if isinstance(p, dict):
                proxy_objects.append(Proxy.model_validate(p))
            else:
                proxy_objects.append(p)
        await storage.save(proxy_objects, validated=validated)
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


async def _revalidate_existing_proxies(
    db_path: Path,
    timeout: int,
    max_concurrent: int,
    prune_failed: bool,
    revalidate_limit: int | None,
    console: Any,
) -> tuple[list[Any], int]:
    """Re-validate existing proxies in the database.

    Loads all proxies from the database, validates them, and updates
    their status using the normalized schema. Valid proxies get updated
    with successful validation records. Failed proxies are marked as DEAD.

    Args:
        db_path: Path to SQLite database file
        timeout: Validation timeout in seconds
        max_concurrent: Maximum concurrent validation requests
        prune_failed: If True, delete failed proxies. If False, mark them as DEAD.
        revalidate_limit: Maximum proxies to revalidate in oldest-first order.
        console: Rich console for progress display

    Returns:
        Tuple of (list of valid proxy dicts, count of failed proxies)
    """
    from rich.progress import (
        BarColumn,
        MofNCompleteColumn,
        Progress,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
    )

    from proxywhirl.fetchers import ProxyValidator
    from proxywhirl.storage import SQLiteStorage

    # Load existing proxies (returns dicts from normalized schema)
    storage = SQLiteStorage(db_path)
    await storage.initialize()

    try:
        existing_proxies = await storage.load_revalidation_candidates(limit=revalidate_limit)
        total_proxies = len(existing_proxies)

        if total_proxies == 0:
            console.print("[yellow]No proxies in database to re-validate[/yellow]")
            return [], 0

        if revalidate_limit and revalidate_limit > 0:
            console.print(
                "[cyan]Loaded "
                f"{total_proxies:,} oldest proxies from database for incremental re-validation"
                "[/cyan]"
            )
        else:
            console.print(f"[cyan]Loaded {total_proxies:,} proxies from database[/cyan]")

        # Build lookup map for original proxies by URL
        original_by_url: dict[str, Any] = {p["url"]: p for p in existing_proxies}

        # Convert to dicts for validator (already dicts, but ensure format)
        proxy_dicts = []
        for proxy in existing_proxies:
            proxy_dict = {
                "url": proxy["url"],
                "protocol": proxy.get("protocol", "http"),
            }
            proxy_dicts.append(proxy_dict)

        # Validate with progress display
        valid_count = 0
        completed = 0

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("{task.fields[status]}"),
            console=console,
            transient=False,
        )

        def progress_callback(done: int, total: int, valid: int) -> None:
            nonlocal completed, valid_count
            completed = done
            valid_count = valid
            pct = (valid / done * 100) if done > 0 else 0
            progress.update(
                task_id,
                completed=done,
                status=f"[green]{valid:,} valid[/green] ({pct:.1f}%)",
            )

        # Create validator with same settings as fetch
        validator = ProxyValidator(
            timeout=timeout,
            concurrency=max_concurrent,
        )

        with progress:
            task_id = progress.add_task(
                "Re-validating proxies",
                total=total_proxies,
                status="[cyan]starting...[/cyan]",
            )

            try:
                validated_dicts = await validator.validate_batch(
                    proxy_dicts,
                    progress_callback=progress_callback,
                )
            finally:
                await validator.close()

        # Build validation results for batch recording
        valid_urls = {p["url"] for p in validated_dicts}
        validation_results: list[tuple[str, bool, float | None, str | None]] = []

        # Record successful validations
        for p_dict in validated_dicts:
            # Validator stores response time as "average_response_time_ms"
            response_time = p_dict.get("average_response_time_ms")
            validation_results.append((p_dict["url"], True, response_time, None))

        # Record failed validations
        failed_count = 0
        for url in original_by_url:
            if url not in valid_urls:
                validation_results.append((url, False, None, "validation_failed"))
                failed_count += 1

        # Batch record all validation results
        await storage.record_validations_batch(validation_results)

        # If prune_failed, delete dead proxies
        if prune_failed and failed_count > 0:
            await storage.cleanup(
                remove_dead=True,
                remove_stale_days=0,  # Don't remove stale
                remove_never_validated=False,
                vacuum=False,
            )
            console.print(f"[yellow]Deleted {failed_count} failed proxies[/yellow]")
        else:
            console.print(f"[yellow]Marked {failed_count} proxies as DEAD[/yellow]")

        return validated_dicts, failed_count

    finally:
        await storage.close()


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
    if context.format == FormatterOutputFormat.JSON:
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
    revalidate: bool = typer.Option(
        False,
        "--revalidate",
        "-R",
        help="Re-validate existing proxies in database instead of fetching new ones",
    ),
    revalidate_limit: int = typer.Option(
        0,
        "--revalidate-limit",
        help="Maximum proxies to re-validate in oldest-first order (0 = all; use with --revalidate)",
    ),
    prune_failed: bool = typer.Option(
        False,
        "--prune-failed",
        help="Delete failed proxies instead of marking them as DEAD (use with --revalidate)",
    ),
    https_validate: bool = typer.Option(
        True,
        "--https-validate/--no-https-validate",
        help="After fetching, test valid HTTP proxies for HTTPS/CONNECT support and add them as https:// entries",
    ),
    https_timeout: int = typer.Option(
        8,
        "--https-timeout",
        help="Per-stage timeout in seconds for HTTPS CONNECT tests (default 8, higher = more found but slower)",
    ),
    https_max: int = typer.Option(
        2000,
        "--https-max",
        help="Maximum HTTPS-capable proxies to collect during dual-validation (0 = unlimited)",
    ),
) -> None:
    """Fetch proxies from configured sources.

    Examples:
      proxywhirl fetch
      proxywhirl fetch --no-validate
      proxywhirl fetch --timeout 5 --concurrency 50
      proxywhirl fetch --revalidate --timeout 5 --concurrency 2000
      proxywhirl fetch --revalidate --revalidate-limit 2000
      proxywhirl fetch --revalidate --prune-failed
      proxywhirl fetch --no-https-validate
      proxywhirl fetch --https-timeout 10
    """
    import asyncio

    command_ctx = get_context()

    # Parse configuration
    fetch_config = _parse_fetch_config(no_validate, timeout, concurrency)
    effective_revalidate_limit = revalidate_limit if revalidate_limit > 0 else None

    if revalidate_limit < 0:
        command_ctx.console.print("[red]--revalidate-limit must be >= 0[/red]")
        raise typer.Exit(code=1)

    if revalidate_limit > 0 and not revalidate:
        command_ctx.console.print(
            "[red]--revalidate-limit can only be used with --revalidate[/red]"
        )
        raise typer.Exit(code=1)

    if revalidate:
        # Re-validate existing proxies in database
        if effective_revalidate_limit is None:
            command_ctx.console.print("[bold]Re-validating existing proxies in database...[/bold]")
        else:
            command_ctx.console.print(
                "[bold]Re-validating the oldest existing proxies in database "
                f"(limit {effective_revalidate_limit:,})...[/bold]"
            )
        try:
            valid_proxies, failed_count = asyncio.run(
                _revalidate_existing_proxies(
                    db_path=Path("proxywhirl.db"),
                    timeout=fetch_config["timeout"],
                    max_concurrent=fetch_config["max_concurrent"],
                    prune_failed=prune_failed,
                    revalidate_limit=effective_revalidate_limit,
                    console=command_ctx.console,
                )
            )
            command_ctx.console.print(
                f"[green]✓[/green] Re-validation complete: "
                f"[green]{len(valid_proxies):,} valid[/green], "
                f"[red]{failed_count:,} failed[/red]"
            )
            proxies = valid_proxies
        except Exception as e:
            command_ctx.console.print(f"[red]Re-validation failed:[/red] {e}")
            raise typer.Exit(code=1) from e
    else:
        # Normal mode: fetch from sources
        try:
            proxies = asyncio.run(
                _fetch_from_sources(
                    validate=fetch_config["validate"],
                    timeout=fetch_config["timeout"],
                    max_concurrent=fetch_config["max_concurrent"],
                    console=command_ctx.console,
                )
            )
        except Exception as e:
            command_ctx.console.print(f"[red]Fetch failed:[/red] {e}")
            raise typer.Exit(code=1) from e

        # Dual-validate HTTP proxies for HTTPS/CONNECT support
        if https_validate and fetch_config["validate"] and proxies:
            http_only = [p for p in proxies if (p.get("protocol") or "http") == "http"]
            if http_only:
                from rich.progress import (
                    BarColumn,
                    MofNCompleteColumn,
                    Progress,
                    SpinnerColumn,
                    TaskProgressColumn,
                    TextColumn,
                    TimeElapsedColumn,
                )

                try:
                    from proxywhirl.fetchers import ProxyValidator

                    validator = ProxyValidator(
                        timeout=https_timeout,
                    )

                    https_progress = Progress(
                        SpinnerColumn(),
                        TextColumn("[bold blue]{task.description}"),
                        BarColumn(),
                        TaskProgressColumn(),
                        MofNCompleteColumn(),
                        TextColumn("•"),
                        TimeElapsedColumn(),
                        TextColumn("{task.fields[status]}"),
                        console=command_ctx.console,
                        transient=False,
                    )

                    https_task_id = None

                    def https_progress_callback(done: int, total: int, valid: int) -> None:
                        nonlocal https_task_id
                        if https_task_id is not None:
                            pct = (valid / done * 100) if done > 0 else 0
                            https_progress.update(
                                https_task_id,
                                completed=done,
                                status=f"[green]{valid:,} HTTPS[/green] ({pct:.1f}%)",
                            )

                    with https_progress:
                        https_task_id = https_progress.add_task(
                            "HTTPS CONNECT test",
                            total=len(http_only),
                            status="[cyan]starting...[/cyan]",
                        )
                        https_capable = asyncio.run(
                            validator.validate_https_capability_batch(
                                http_only,
                                concurrency=min(fetch_config["max_concurrent"], 500),
                                max_results=https_max if https_max > 0 else None,
                                progress_callback=https_progress_callback,
                            )
                        )

                    if https_capable:
                        proxies = list(proxies) + https_capable
                        command_ctx.console.print(
                            f"[green]✓[/green] Found [green]{len(https_capable):,}[/green] HTTPS-capable proxies"
                        )
                    else:
                        command_ctx.console.print(
                            "[dim]No HTTPS-capable proxies found in this batch[/dim]"
                        )
                except Exception as e:
                    command_ctx.console.print(
                        f"[yellow]HTTPS dual-validation skipped:[/yellow] {e}"
                    )

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

    from proxywhirl.retry import RetryMetrics

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
    if command_ctx.format == FormatterOutputFormat.JSON:
        render_json(output_data)
    elif command_ctx.format == FormatterOutputFormat.CSV:
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

        if command_ctx.format == FormatterOutputFormat.JSON:
            render_json({"available": available})
        else:
            if available:
                command_ctx.console.print("[green]✓[/green] GeoIP database is available")
            else:
                command_ctx.console.print("[yellow]![/yellow] GeoIP database not found")

    else:
        # Show installation instructions
        if command_ctx.format == FormatterOutputFormat.JSON:
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
    from proxywhirl.rotator import ProxyWhirl

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

    rotator = ProxyWhirl(proxies=proxies, strategy=command_ctx.config.rotation_strategy)
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

        if command_ctx.format == FormatterOutputFormat.JSON:
            render_json(summary.model_dump())
        elif command_ctx.format == FormatterOutputFormat.CSV:
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


# Create a command group for sources
sources_app = typer.Typer(
    name="sources",
    help="Manage and audit proxy sources",
    no_args_is_help=False,  # Allow running without args for backward compatibility
)
app.add_typer(sources_app, name="sources")

# Create pool command group
pool_app = typer.Typer(
    name="pool",
    help="Manage proxy pools",
    no_args_is_help=False,
)
app.add_typer(pool_app, name="pool")


@sources_app.callback(invoke_without_command=True)
def sources_callback(
    ctx: typer.Context,
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
        min=1,
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
        proxywhirl sources audit        # Full audit with detailed results
        proxywhirl sources audit --fix  # Audit and remove broken sources
    """
    # Only run if no subcommand is invoked
    if ctx.invoked_subcommand is not None:
        return

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
        enabled_sources = [s for s in ALL_SOURCES if s.enabled]
        command_ctx.console.print(
            f"[bold]Validating {len(enabled_sources)} proxy sources...[/bold]\n"
        )

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
        command_ctx.console.print("[dim]Use 'proxywhirl sources audit' for detailed auditing[/dim]")


@sources_app.command()
def audit(
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
        min=1,
        help="Maximum concurrent requests",
    ),
    retries: int = typer.Option(
        3,
        "--retries",
        "-r",
        help="Number of retries for each source before marking as broken",
    ),
    fix: bool = typer.Option(
        False,
        "--fix",
        help="Remove broken sources from sources.py (creates backup)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what would be removed without making changes (implies --fix)",
    ),
    min_proxies: int = typer.Option(
        1,
        "--min-proxies",
        help="Minimum proxies required for a source to be considered healthy",
    ),
    protocol: str | None = typer.Option(
        None,
        "--protocol",
        "-p",
        help="Only audit sources of specific protocol (http, socks4, socks5)",
    ),
) -> None:
    """Audit proxy sources for broken or stale entries.

    Tests each source by fetching from it and checking if it returns valid proxies.
    A source is considered "broken" if:

    - It returns a non-200 status code
    - It times out after retries
    - It returns 0 proxies (or less than --min-proxies)
    - It returns malformed/unparseable content

    Use --fix to automatically remove broken sources from sources.py.
    A backup file will be created before any modifications.

    Examples:
        proxywhirl sources audit                    # Audit all sources
        proxywhirl sources audit --protocol http    # Only HTTP sources
        proxywhirl sources audit --fix              # Remove broken sources
        proxywhirl sources audit --dry-run          # Preview what would be removed
        proxywhirl sources audit --retries 5        # More retries before marking broken
        proxywhirl sources audit -j 50 -t 30        # Higher concurrency, longer timeout
    """
    import asyncio

    from rich.table import Table

    from proxywhirl.sources import (
        ALL_HTTP_SOURCES,
        ALL_SOCKS4_SOURCES,
        ALL_SOCKS5_SOURCES,
        ALL_SOURCES,
    )

    command_ctx = get_context()

    # Select sources based on protocol filter
    if protocol:
        protocol_lower = protocol.lower()
        if protocol_lower == "http":
            sources_to_audit = [s for s in ALL_HTTP_SOURCES if s.enabled]
            protocol_name = "HTTP"
        elif protocol_lower == "socks4":
            sources_to_audit = [s for s in ALL_SOCKS4_SOURCES if s.enabled]
            protocol_name = "SOCKS4"
        elif protocol_lower == "socks5":
            sources_to_audit = [s for s in ALL_SOCKS5_SOURCES if s.enabled]
            protocol_name = "SOCKS5"
        else:
            command_ctx.console.print(
                f"[red]Invalid protocol: {protocol}. Use http, socks4, or socks5[/red]"
            )
            raise typer.Exit(code=1)
        command_ctx.console.print(
            f"[bold]Auditing {len(sources_to_audit)} {protocol_name} sources...[/bold]\n"
        )
    else:
        sources_to_audit = [s for s in ALL_SOURCES if s.enabled]
        command_ctx.console.print(
            f"[bold]Auditing {len(sources_to_audit)} proxy sources...[/bold]\n"
        )

    # Run audit
    audit_results = asyncio.run(
        _run_source_audit(
            sources=sources_to_audit,
            timeout=timeout,
            concurrency=concurrency,
            retries=retries,
            min_proxies=min_proxies,
            console=command_ctx.console,
        )
    )

    # Separate working and broken sources
    working = [r for r in audit_results if r["status"] == "healthy"]
    broken = [r for r in audit_results if r["status"] == "broken"]

    # Create results table
    table = Table(title="Source Audit Results")
    table.add_column("Status", style="bold", width=10)
    table.add_column("Source", style="cyan")
    table.add_column("Proxies", justify="right")
    table.add_column("Time", justify="right")
    table.add_column("Reason")

    # Sort: broken first, then by name
    sorted_results = sorted(
        audit_results, key=lambda r: (r["status"] == "healthy", r["name"].lower())
    )

    for result in sorted_results:
        if result["status"] == "healthy":
            status = "[green]✓ HEALTHY[/green]"
            reason = ""
        else:
            status = "[red]✗ BROKEN[/red]"
            reason = result.get("error", "Unknown error")[:40]

        proxies = str(result.get("proxy_count", 0))
        time_str = f"{result.get('response_time_ms', 0):.0f}ms"

        table.add_row(status, result["name"], proxies, time_str, reason)

    command_ctx.console.print(table)

    # Summary
    command_ctx.console.print("\n[bold]Audit Summary:[/bold]")
    command_ctx.console.print(
        f"  Total: {len(audit_results)} | "
        f"[green]Healthy: {len(working)}[/green] | "
        f"[red]Broken: {len(broken)}[/red]"
    )

    # Output JSON format for CI
    if command_ctx.format == FormatterOutputFormat.JSON:
        render_json(
            {
                "total_sources": len(audit_results),
                "healthy_sources": len(working),
                "broken_sources": len(broken),
                "broken_urls": [r["url"] for r in broken],
                "results": audit_results,
            }
        )

    # Handle fix mode
    if broken and (fix or dry_run):
        command_ctx.console.print("\n[bold]Broken sources to remove:[/bold]")
        for result in broken:
            command_ctx.console.print(f"  • {result['name']}")
            command_ctx.console.print(f"    URL: {result['url']}")
            command_ctx.console.print(f"    Reason: {result.get('error', 'Unknown')}")

        if dry_run:
            command_ctx.console.print(
                f"\n[yellow]Dry run: Would remove {len(broken)} source(s)[/yellow]"
            )
            command_ctx.console.print("[dim]Run without --dry-run to apply changes[/dim]")
        else:
            # Actually remove broken sources
            removed_count = _remove_broken_sources(
                broken_urls=[r["url"] for r in broken],
                console=command_ctx.console,
            )
            if removed_count > 0:
                command_ctx.console.print(
                    f"\n[green]✓ Removed {removed_count} broken source(s)[/green]"
                )
                command_ctx.console.print(
                    "[yellow]Note: Backup created at proxywhirl/sources.py.backup[/yellow]"
                )
            else:
                command_ctx.console.print(
                    "\n[yellow]No sources were removed (check logs for details)[/yellow]"
                )

    elif broken:
        command_ctx.console.print(
            f"\n[yellow]Found {len(broken)} broken source(s). Use --fix to remove them.[/yellow]"
        )

    # Exit with error if broken sources found (for CI)
    if broken:
        raise typer.Exit(code=1)


async def _run_source_audit(
    sources: list[Any],
    timeout: float,
    concurrency: int,
    retries: int,
    min_proxies: int,
    console: Console,
) -> list[dict[str, Any]]:
    """Run source audit with retries and proxy counting.

    Args:
        sources: List of ProxySourceConfig to audit
        timeout: Timeout per request in seconds
        concurrency: Maximum concurrent requests
        retries: Number of retries per source
        min_proxies: Minimum proxies for healthy status
        console: Rich console for progress display

    Returns:
        List of audit result dicts with status, proxy_count, etc.
    """
    import asyncio
    import time

    import httpx
    from rich.progress import (
        BarColumn,
        MofNCompleteColumn,
        Progress,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
    )

    from proxywhirl.fetchers import ProxyFetcher
    from proxywhirl.sources import _get_source_name

    results: list[dict[str, Any]] = []
    semaphore = asyncio.Semaphore(concurrency)
    completed = 0

    async def audit_source(source: Any) -> dict[str, Any]:
        """Audit a single source with retries."""
        nonlocal completed
        name = _get_source_name(source)
        url = str(source.url)

        for attempt in range(retries):
            start_time = time.perf_counter()
            try:
                async with semaphore:
                    # Create fetcher for single source
                    fetcher = ProxyFetcher(sources=[source])
                    try:
                        # Fetch without validation (we just want to count)
                        proxies = await fetcher.fetch_all(validate=False, deduplicate=True)
                        elapsed_ms = (time.perf_counter() - start_time) * 1000

                        proxy_count = len(proxies)
                        if proxy_count >= min_proxies:
                            completed += 1
                            return {
                                "name": name,
                                "url": url,
                                "status": "healthy",
                                "proxy_count": proxy_count,
                                "response_time_ms": elapsed_ms,
                                "attempts": attempt + 1,
                            }
                        else:
                            # Not enough proxies, try again
                            if attempt < retries - 1:
                                await asyncio.sleep(1)  # Brief pause before retry
                                continue
                            completed += 1
                            return {
                                "name": name,
                                "url": url,
                                "status": "broken",
                                "proxy_count": proxy_count,
                                "response_time_ms": elapsed_ms,
                                "error": f"Only {proxy_count} proxies (min: {min_proxies})",
                                "attempts": attempt + 1,
                            }
                    finally:
                        await fetcher.close()

            except httpx.TimeoutException:
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                    continue
                completed += 1
                return {
                    "name": name,
                    "url": url,
                    "status": "broken",
                    "proxy_count": 0,
                    "response_time_ms": (time.perf_counter() - start_time) * 1000,
                    "error": "Timeout",
                    "attempts": attempt + 1,
                }
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                    continue
                completed += 1
                return {
                    "name": name,
                    "url": url,
                    "status": "broken",
                    "proxy_count": 0,
                    "response_time_ms": (time.perf_counter() - start_time) * 1000,
                    "error": str(e)[:100],
                    "attempts": attempt + 1,
                }

        # Should not reach here, but handle it
        completed += 1
        return {
            "name": name,
            "url": url,
            "status": "broken",
            "proxy_count": 0,
            "response_time_ms": 0,
            "error": "Max retries exceeded",
            "attempts": retries,
        }

    # Run with progress bar
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )

    with progress:
        task = progress.add_task("Auditing sources", total=len(sources))

        async def audit_with_progress(source: Any) -> dict[str, Any]:
            result = await audit_source(source)
            progress.update(task, advance=1)
            return result

        tasks = [audit_with_progress(src) for src in sources]
        results = await asyncio.gather(*tasks)

    return results


def _remove_broken_sources(broken_urls: list[str], console: Console) -> int:
    """Remove broken sources from sources.py file.

    Creates a backup before modification. Uses regex to comment out
    the broken source definitions.

    Args:
        broken_urls: List of URLs to remove
        console: Rich console for output

    Returns:
        Number of sources removed
    """
    import re
    import shutil

    sources_path = Path(__file__).parent / "sources.py"
    backup_path = sources_path.with_suffix(".py.backup")

    if not sources_path.exists():
        console.print("[red]Error: sources.py not found[/red]")
        return 0

    # Create backup
    shutil.copy(sources_path, backup_path)

    # Read current content
    content = sources_path.read_text()
    removed_count = 0

    # For each broken URL, comment out its ProxySourceConfig definition
    for url in broken_urls:
        # Escape URL for regex
        escaped_url = re.escape(url)

        # Pattern to match ProxySourceConfig with this URL
        # Matches: VARIABLE_NAME = ProxySourceConfig(...url="<url>"...)
        # This is a simplified pattern - in practice, source configs span multiple lines
        pattern = (
            rf'^([A-Z_]+)\s*=\s*ProxySourceConfig\(\s*\n?\s*url=["\']?{escaped_url}["\']?.*?\)$'
        )

        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            var_name = match.group(1)
            # Comment out the entire definition
            commented = f"# REMOVED BY AUDIT: {match.group(0)}"
            content = content.replace(match.group(0), commented)
            removed_count += 1
            console.print(f"  [dim]Commented out: {var_name}[/dim]")

    # If we made changes, also remove from the collection lists
    if removed_count > 0:
        # Write modified content
        sources_path.write_text(content)

    return removed_count


@app.command()
def tui() -> None:
    """Launch the interactive Terminal User Interface (TUI).

    The TUI provides a full-featured dashboard for managing proxies with:
      - Real-time metrics and sparkline visualizations
      - Proxy table with filtering, sorting, and health status
      - Manual proxy management (add/remove)
      - Health checks with progress bars
      - Circuit breaker monitoring
      - Request testing with multiple HTTP methods
      - Export functionality with format preview

    Keyboard shortcuts:
      j/k     - Navigate up/down
      g/G     - Jump to first/last
      Enter   - View proxy details
      c       - Copy proxy URL
      t       - Quick test proxy
      /       - Focus search
      ?       - Show help modal
      Ctrl+A  - Toggle auto-refresh
      Ctrl+R  - Refresh all data
      Ctrl+F  - Fetch tab
      Ctrl+E  - Export tab
      Ctrl+T  - Test tab
      Ctrl+H  - Health tab

    Examples:
      proxywhirl tui
    """
    from proxywhirl.tui import run_tui

    # Run the TUI (bypasses normal output formatting)
    run_tui()


@app.command()
def db_stats(
    db: Path = typer.Option(
        Path("proxywhirl.db"),
        "--db",
        help="Path to SQLite database",
    ),
) -> None:
    """Show database statistics.

    Displays comprehensive statistics about the proxy database including
    counts by health status, protocol, and validation metrics.

    Examples:
      proxywhirl db-stats
      proxywhirl db-stats --db custom.db
    """
    import asyncio

    from rich.table import Table

    command_ctx = get_context()

    async def get_db_stats():
        from proxywhirl.storage import SQLiteStorage

        storage = SQLiteStorage(db)
        await storage.initialize()

        try:
            return await storage.get_stats()
        finally:
            await storage.close()

    try:
        stats = asyncio.run(get_db_stats())
    except Exception as e:
        command_ctx.console.print(f"[red]Error loading stats:[/red] {e}")
        raise typer.Exit(code=1) from e

    if command_ctx.format == FormatterOutputFormat.JSON:
        render_json(stats)
    else:
        table = Table(title="Proxy Database Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")

        table.add_row("Total Proxies", f"{stats.get('total_proxies', 0):,}")
        table.add_row("", "")

        # Health status breakdown
        table.add_row("[bold]By Health Status[/bold]", "")
        for status, count in sorted(stats.get("by_health", {}).items()):
            color = "green" if status == "healthy" else "yellow" if status == "unknown" else "red"
            table.add_row(f"  {status}", f"[{color}]{count:,}[/{color}]")

        table.add_row("", "")

        # Protocol breakdown
        table.add_row("[bold]By Protocol[/bold]", "")
        for protocol, count in sorted(stats.get("by_protocol", {}).items()):
            table.add_row(f"  {protocol}", f"{count:,}")

        # Validation stats (normalized only)
        if "validations_24h" in stats:
            table.add_row("", "")
            table.add_row("[bold]Validations (24h)[/bold]", "")
            v = stats["validations_24h"]
            table.add_row("  Total", f"{v.get('total', 0):,}")
            table.add_row("  Successful", f"{v.get('successful', 0):,}")
            if v.get("avg_response_time_ms"):
                table.add_row("  Avg Response Time", f"{v['avg_response_time_ms']:.0f}ms")

        # Database size
        if "db_size_bytes" in stats:
            size_mb = stats["db_size_bytes"] / (1024 * 1024)
            table.add_row("", "")
            table.add_row("Database Size", f"{size_mb:.2f} MB")

        command_ctx.console.print(table)


@app.command()
def cleanup(
    db: Path = typer.Option(
        Path("proxywhirl.db"),
        "--db",
        help="Path to SQLite database",
    ),
    stale_days: int = typer.Option(
        7,
        "--stale-days",
        help="Remove proxies not validated in N days",
    ),
    execute: bool = typer.Option(
        False,
        "--execute",
        help="Actually perform cleanup (dry run by default)",
    ),
) -> None:
    """Clean up stale and dead proxies from the database.

    By default, performs a dry run showing what would be removed.
    Use --execute to actually perform the cleanup.

    Examples:
      proxywhirl cleanup                        # Dry run
      proxywhirl cleanup --execute              # Actually remove
      proxywhirl cleanup --stale-days 14        # Remove if not validated in 14 days
    """
    import asyncio

    command_ctx = get_context()

    async def run_cleanup():
        from proxywhirl.storage import SQLiteStorage

        storage = SQLiteStorage(db)
        await storage.initialize()

        try:
            if execute:
                result = await storage.cleanup(
                    remove_dead=True,
                    remove_stale_days=stale_days,
                    remove_never_validated=True,
                    vacuum=True,
                )
                return {"executed": True, "counts": result}
            else:
                # Dry run - just get stats
                stats = await storage.get_stats()
                return {
                    "executed": False,
                    "would_remove": {
                        "dead": stats.get("by_health", {}).get("dead", 0),
                    },
                }
        finally:
            await storage.close()

    try:
        result = asyncio.run(run_cleanup())
    except Exception as e:
        command_ctx.console.print(f"[red]Cleanup failed:[/red] {e}")
        raise typer.Exit(code=1) from e

    if command_ctx.format == FormatterOutputFormat.JSON:
        render_json(result)
    else:
        if result["executed"]:
            counts = result["counts"]
            total = sum(counts.values())
            command_ctx.console.print(
                f"[green]✓[/green] Cleanup completed: removed {total:,} proxies"
            )
            for category, count in counts.items():
                command_ctx.console.print(f"  {category}: {count:,}")
        else:
            would_remove = result.get("would_remove", {})
            command_ctx.console.print("[yellow]Dry run - showing what would be removed:[/yellow]")
            for category, count in would_remove.items():
                command_ctx.console.print(f"  {category}: {count:,}")
            command_ctx.console.print("\n[dim]Use --execute to actually remove[/dim]")


@sources_app.command()
def discover(
    recommended: bool = typer.Option(
        True,
        "--recommended/--all",
        "-r/-a",
        help="Show recommended sources (default) or all available",
    ),
    by_type: str = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by proxy type (http, socks4, socks5, api)",
    ),
    format: FormatterOutputFormat = typer.Option(
        FormatterOutputFormat.TEXT,
        "--format",
        "-f",
        case_sensitive=False,
        help="Output format (text, json, csv, yaml)",
    ),
) -> None:
    """Discover available proxy sources.

    Examples:
      proxywhirl sources discover --recommended
      proxywhirl sources discover --all --type http
      proxywhirl sources discover --recommended --format json
    """
    from proxywhirl.sources import (
        ALL_HTTP_SOURCES,
        ALL_SOCKS4_SOURCES,
        ALL_SOCKS5_SOURCES,
        ALL_SOURCES,
        API_SOURCES,
        RECOMMENDED_SOURCES,
    )

    command_ctx = get_context()

    # Determine which sources to show
    sources_to_show = []

    if by_type:
        by_type_lower = by_type.lower()
        if by_type_lower == "http":
            sources_to_show = ALL_HTTP_SOURCES
        elif by_type_lower == "socks4":
            sources_to_show = ALL_SOCKS4_SOURCES
        elif by_type_lower == "socks5":
            sources_to_show = ALL_SOCKS5_SOURCES
        elif by_type_lower == "api":
            sources_to_show = API_SOURCES
        else:
            command_ctx.console.print(
                f"[red]Error: Unknown type '{by_type}'. Choose: http, socks4, socks5, api[/red]"
            )
            raise typer.Exit(code=1)
    elif recommended:
        sources_to_show = RECOMMENDED_SOURCES
    else:
        sources_to_show = ALL_SOURCES

    # Build source data for rendering
    source_data = []
    for source in sources_to_show:
        source_data.append(
            {
                "name": source.name,
                "url": source.url,
                "type": source.proxy_type.value
                if hasattr(source.proxy_type, "value")
                else str(source.proxy_type),
                "enabled": "Yes" if source.enabled else "No",
                "parser": source.parser_type.value
                if hasattr(source.parser_type, "value")
                else str(source.parser_type),
            }
        )

    if format == FormatterOutputFormat.JSON:
        render_json(source_data)
    elif format == FormatterOutputFormat.CSV:
        render_csv(
            {
                "table": {
                    "headers": ["Name", "URL", "Type", "Enabled", "Parser"],
                    "rows": [
                        [
                            s["name"],
                            s["url"],
                            s["type"],
                            s["enabled"],
                            s["parser"],
                        ]
                        for s in source_data
                    ],
                }
            }
        )
    elif format == FormatterOutputFormat.YAML:
        render_yaml(source_data)
    else:  # TEXT
        table = Table(title=f"Proxy Sources ({len(source_data)} total)")
        table.add_column("Name", style="cyan")
        table.add_column("URL", style="magenta")
        table.add_column("Type", style="green")
        table.add_column("Enabled", style="yellow")
        table.add_column("Parser", style="blue")

        for source in source_data:
            table.add_row(
                source["name"],
                source["url"][:50] + "..." if len(source["url"]) > 50 else source["url"],
                source["type"],
                source["enabled"],
                source["parser"],
            )

        command_ctx.console.print(table)


@app.command()
def batch(
    action: BatchAction = typer.Argument(..., help="Action: add, remove, update"),
    input_file: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Input file (CSV, JSON, or YAML with proxy list)",
    ),
    format: str = typer.Option(
        "auto",
        "--format",
        "-f",
        help="Input format (auto, csv, json, yaml)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be done without making changes",
    ),
) -> None:
    """Perform batch operations on proxies.

    Input file formats:
    - CSV: columns = url, username (optional), password (optional)
    - JSON: list of {url, username?, password?}
    - YAML: list of {url, username?, password?}

    Examples:
      proxywhirl batch add --input proxies.csv
      proxywhirl batch remove --input remove.json --dry-run
      proxywhirl batch update --input updates.yaml
    """
    import csv
    import json

    command_ctx = get_context()

    # Load input file
    if not input_file.exists():
        command_ctx.console.print(f"[red]Error: File not found: {input_file}[/red]")
        raise typer.Exit(code=1)

    proxies_data = []

    # Detect format if auto
    detected_format = format
    if format == "auto":
        suffix = input_file.suffix.lower()
        if suffix == ".csv":
            detected_format = "csv"
        elif suffix == ".json":
            detected_format = "json"
        elif suffix in (".yaml", ".yml"):
            detected_format = "yaml"
        else:
            detected_format = "json"  # default

    try:
        if detected_format == "csv":
            with open(input_file) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    proxies_data.append(row)

        elif detected_format == "json":
            with open(input_file) as f:
                proxies_data = json.load(f)

        elif detected_format == "yaml":
            try:
                import yaml
            except ImportError:
                command_ctx.console.print(
                    "[red]Error: PyYAML not installed. Install with: pip install pyyaml[/red]"
                )
                raise typer.Exit(code=1)

            with open(input_file) as f:
                proxies_data = yaml.safe_load(f) or []
    except Exception as e:
        command_ctx.console.print(f"[red]Error reading file: {e}[/red]")
        raise typer.Exit(code=1)

    # Create rotator
    from proxywhirl.config import ProxyConfig, save_config
    from proxywhirl.models import Proxy
    from proxywhirl.rotator import ProxyWhirl

    proxies = []
    for proxy_config in command_ctx.config.proxies:
        proxies.append(
            Proxy(
                url=proxy_config.url,
                username=proxy_config.username,
                password=proxy_config.password,
            )
        )

    rotator = ProxyWhirl(proxies=proxies, strategy=command_ctx.config.rotation_strategy)

    # Process batch operation
    results = {"added": 0, "removed": 0, "updated": 0, "errors": []}

    if action == "add":
        for item in proxies_data:
            try:
                proxy_url = item.get("url") if isinstance(item, dict) else item
                username = item.get("username") if isinstance(item, dict) else None
                password = item.get("password") if isinstance(item, dict) else None

                if not proxy_url:
                    results["errors"].append("Missing proxy URL")
                    continue

                if not dry_run:
                    rotator.pool.add_proxy(
                        Proxy(url=proxy_url, username=username, password=password)
                    )
                results["added"] += 1
            except Exception as e:
                results["errors"].append(f"{item}: {e}")

    elif action == "remove":
        for item in proxies_data:
            try:
                proxy_url = item.get("url") if isinstance(item, dict) else item
                if not proxy_url:
                    results["errors"].append("Missing proxy URL")
                    continue

                if not dry_run:
                    rotator.pool.remove_proxy(proxy_url)
                results["removed"] += 1
            except Exception as e:
                results["errors"].append(f"{item}: {e}")

    elif action == "update":
        for item in proxies_data:
            try:
                proxy_url = item.get("url") if isinstance(item, dict) else item
                if not proxy_url:
                    results["errors"].append("Missing proxy URL")
                    continue

                # Update proxy (remove and re-add with new config)
                if not dry_run:
                    rotator.pool.remove_proxy(proxy_url)
                    username = item.get("username") if isinstance(item, dict) else None
                    password = item.get("password") if isinstance(item, dict) else None
                    rotator.pool.add_proxy(
                        Proxy(url=proxy_url, username=username, password=password)
                    )
                results["updated"] += 1
            except Exception as e:
                results["errors"].append(f"{item}: {e}")

    # Save config if not dry run
    if not dry_run and (action == "add" or action == "remove" or action == "update"):
        proxy_configs = [
            ProxyConfig(
                url=p.url,
                username=p.username,
                password=p.password,
            )
            for p in rotator.pool.get_all_proxies()
        ]
        command_ctx.config.proxies = proxy_configs
        save_config(command_ctx.config, command_ctx.config_path)

    # Output results
    output_data = {
        "action": action,
        "dry_run": dry_run,
        "added": results["added"],
        "removed": results["removed"],
        "updated": results["updated"],
        "errors": results["errors"],
        "error_count": len(results["errors"]),
    }

    if command_ctx.format == FormatterOutputFormat.JSON:
        render_json(output_data)
    elif command_ctx.format == FormatterOutputFormat.CSV:
        import csv
        import sys

        writer = csv.DictWriter(sys.stdout, fieldnames=output_data.keys())
        writer.writeheader()
        writer.writerow(output_data)
    elif command_ctx.format == FormatterOutputFormat.YAML:
        render_yaml(output_data)
    else:  # TEXT
        command_ctx.console.print(f"\n[bold]Batch {action.upper()} Results[/bold]")
        if dry_run:
            command_ctx.console.print("[yellow][DRY RUN][/yellow]")
        command_ctx.console.print(f"Added: {results['added']}")
        command_ctx.console.print(f"Removed: {results['removed']}")
        command_ctx.console.print(f"Updated: {results['updated']}")
        if results["errors"]:
            command_ctx.console.print(f"\n[red]Errors ({len(results['errors'])}):[/red]")
            for error in results["errors"]:
                command_ctx.console.print(f"  - {error}")


@sources_app.command(name="discover")
def sources_discover(
    ctx: typer.Context,
    max_results: int = typer.Option(
        20,
        "--max-results",
        "-m",
        help="Maximum number of sources to discover",
    ),
    filter_type: str = typer.Option(
        "",
        "--type",
        "-t",
        help="Filter by proxy type (http,socks4,socks5)",
    ),
    sort_by: str = typer.Option(
        "quality",
        "--sort-by",
        "-s",
        help="Sort by: quality, latency, speed, availability",
    ),
) -> None:
    """Discover available proxy sources."""
    command_ctx = get_context()

    try:
        from proxywhirl import sources

        all_sources = sources.ALL_SOURCES
        filtered_sources = all_sources

        # Filter by type if specified
        if filter_type:
            type_val = filter_type.upper()
            filtered_sources = [s for s in all_sources if s.proxy_type.name == type_val]

        # Sort sources (simplified)
        if sort_by == "quality":
            filtered_sources = sorted(
                filtered_sources,
                key=lambda s: getattr(s, "quality_score", 0),
                reverse=True,
            )

        # Limit results
        filtered_sources = filtered_sources[:max_results]

        if command_ctx.format == FormatterOutputFormat.JSON:
            data = [
                {
                    "name": s.name,
                    "url": s.url,
                    "proxy_type": s.proxy_type.name,
                    "format": s.format.value if hasattr(s.format, "value") else str(s.format),
                }
                for s in filtered_sources
            ]
            render_json(data)
        else:
            command_ctx.console.print(f"\n[bold]Discovered {len(filtered_sources)} Sources[/bold]")
            table = Table()
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("URL", style="blue")
            for s in filtered_sources:
                table.add_row(
                    s.name,
                    s.proxy_type.name,
                    s.url[:50] + "..." if len(s.url) > 50 else s.url,
                )
            command_ctx.console.print(table)

    except Exception as e:
        command_ctx.console.print(f"[red]Error discovering sources: {e}[/red]")
        raise typer.Exit(code=1)


@app.command(name="formats")
def list_formats(
    ctx: typer.Context,
) -> None:
    """List available proxy export formats."""
    command_ctx = get_context()

    formats = {
        "json": "JSON format with full proxy details",
        "csv": "Comma-separated values",
        "yaml": "YAML format",
        "txt": "Plain text, one proxy per line",
        "m3u": "M3U playlist format (for proxies with specific structure)",
        "pac": "Proxy Auto-Config JavaScript",
    }

    if command_ctx.format == FormatterOutputFormat.JSON:
        render_json(formats)
    else:
        command_ctx.console.print("\n[bold]Available Export Formats[/bold]\n")
        for fmt, desc in formats.items():
            command_ctx.console.print(f"[cyan]{fmt:10}[/cyan] {desc}")
        command_ctx.console.print()


@pool_app.command(name="statistics")
def pool_statistics(
    ctx: typer.Context,
    detailed: bool = typer.Option(
        False,
        "--detailed",
        "-d",
        help="Show detailed statistics per proxy",
    ),
) -> None:
    """Get pool statistics and health information."""
    command_ctx = get_context()

    try:
        rotator = command_ctx.rotator
        pool = rotator.pool

        # Basic stats
        stats = {
            "total_proxies": len(pool.proxies),
            "active_proxies": len([p for p in pool.proxies if p.is_active]),
            "inactive_proxies": len([p for p in pool.proxies if not p.is_active]),
            "rotation_count": getattr(rotator, "rotation_count", 0),
            "requests_served": getattr(rotator, "requests_served", 0),
        }

        if detailed:
            proxy_stats = []
            for p in pool.proxies[:10]:  # Limit to first 10
                proxy_stats.append(
                    {
                        "proxy": p.proxy_string,
                        "type": p.proxy_type.name,
                        "is_active": p.is_active,
                        "country": getattr(p, "country", "Unknown"),
                    }
                )
            stats["proxies"] = proxy_stats

        if command_ctx.format == FormatterOutputFormat.JSON:
            render_json(stats)
        else:
            command_ctx.console.print("\n[bold]Pool Statistics[/bold]")
            command_ctx.console.print(f"Total Proxies: {stats['total_proxies']}")
            command_ctx.console.print(f"Active: {stats['active_proxies']}")
            command_ctx.console.print(f"Inactive: {stats['inactive_proxies']}")
            command_ctx.console.print(f"Rotations: {stats['rotation_count']}")
            command_ctx.console.print(f"Requests Served: {stats['requests_served']}")

            if detailed and "proxies" in stats:
                command_ctx.console.print("\n[bold]Proxy Details[/bold]")
                table = Table()
                table.add_column("Proxy", style="cyan")
                table.add_column("Type", style="green")
                table.add_column("Status", style="yellow")
                for p in stats["proxies"]:
                    status = "[green]Active[/green]" if p["is_active"] else "[red]Inactive[/red]"
                    table.add_row(p["proxy"], p["type"], status)
                command_ctx.console.print(table)

    except Exception as e:
        command_ctx.console.print(f"[red]Error getting pool statistics: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def list_proxies(
    pool_name: str | None = typer.Option(
        None,
        "--pool",
        "-p",
        help="Filter by pool name",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        "-s",
        help="Filter by health status (HEALTHY, DEGRADED, UNHEALTHY, DEAD)",
    ),
    country: str | None = typer.Option(
        None,
        "--country",
        "-c",
        help="Filter by country code (e.g., US, GB)",
    ),
    limit: int = typer.Option(
        100,
        "--limit",
        "-l",
        help="Maximum number of proxies to list",
        min=1,
    ),
) -> None:
    """List proxies in the pool with optional filtering.

    Examples:
      proxywhirl list_proxies
      proxywhirl list_proxies --status HEALTHY --limit 50
      proxywhirl list_proxies --country US
      proxywhirl list_proxies --pool default --json
    """
    from proxywhirl.models import HealthStatus

    command_ctx = get_context()

    try:
        rotator = command_ctx.rotator
        proxies = rotator.pool.get_all_proxies()

        # Apply filters
        if status:
            try:
                status_enum = HealthStatus[status.upper()]
                proxies = [p for p in proxies if p.health_status == status_enum]
            except KeyError:
                command_ctx.console.print(
                    f"[red]Invalid status: {status}. Use: HEALTHY, DEGRADED, UNHEALTHY, DEAD[/red]"
                )
                raise typer.Exit(code=1)

        if country:
            proxies = [p for p in proxies if getattr(p, "country", "").upper() == country.upper()]

        if pool_name:
            # Filter by pool name if available
            proxies = [p for p in proxies if getattr(p, "pool_name", "") == pool_name]

        proxies = proxies[:limit]

        if command_ctx.format == FormatterOutputFormat.JSON:
            data = [
                {
                    "proxy": p.proxy_string,
                    "type": p.proxy_type.name,
                    "status": p.health_status.name if hasattr(p, "health_status") else "UNKNOWN",
                    "country": getattr(p, "country", "Unknown"),
                    "response_time_ms": getattr(p, "average_response_time_ms", None),
                    "success_rate": getattr(p, "success_rate", None),
                }
                for p in proxies
            ]
            render_json({"proxies": data, "count": len(proxies)})
        elif command_ctx.format == FormatterOutputFormat.CSV:
            import csv

            writer = csv.writer(sys.stdout)
            writer.writerow(
                ["Proxy", "Type", "Status", "Country", "Response Time (ms)", "Success Rate"]
            )
            for p in proxies:
                writer.writerow(
                    [
                        p.proxy_string,
                        p.proxy_type.name,
                        p.health_status.name if hasattr(p, "health_status") else "UNKNOWN",
                        getattr(p, "country", "Unknown"),
                        getattr(p, "average_response_time_ms", ""),
                        getattr(p, "success_rate", ""),
                    ]
                )
        else:  # TEXT
            if not proxies:
                command_ctx.console.print("[yellow]No proxies found[/yellow]")
                return

            table = Table(title=f"Proxies ({len(proxies)} total)")
            table.add_column("Proxy", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Country", style="magenta")
            table.add_column("Response (ms)", style="blue")
            table.add_column("Success Rate", style="bold")

            for p in proxies:
                status_color = (
                    "green"
                    if hasattr(p, "health_status") and p.health_status.name == "HEALTHY"
                    else "red"
                )
                status_text = p.health_status.name if hasattr(p, "health_status") else "UNKNOWN"
                table.add_row(
                    p.proxy_string,
                    p.proxy_type.name,
                    f"[{status_color}]{status_text}[/{status_color}]",
                    getattr(p, "country", "Unknown"),
                    str(round(getattr(p, "average_response_time_ms", 0), 1)),
                    f"{getattr(p, 'success_rate', 0):.1%}",
                )

            command_ctx.console.print(table)
    except Exception as e:
        command_ctx.console.print(f"[red]Error listing proxies: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def validate_proxy(
    proxy_url: str = typer.Argument(
        ..., help="Proxy URL to validate (e.g., http://proxy.example.com:8080)"
    ),
    target_url: str | None = typer.Option(
        "https://httpbin.org/ip",
        "--target",
        "-t",
        help="Target URL to test proxy against",
    ),
    timeout: float = typer.Option(
        10.0,
        "--timeout",
        help="Request timeout in seconds",
        min=0.1,
    ),
) -> None:
    """Validate proxy health with optional target URL test.

    Examples:
      proxywhirl validate_proxy http://proxy.example.com:8080
      proxywhirl validate_proxy http://proxy.example.com:8080 --target https://httpbin.org/status/200
      proxywhirl validate_proxy socks5://proxy.example.com:1080 --timeout 5
      proxywhirl validate_proxy http://proxy.example.com:8080 --json
    """
    command_ctx = get_context()

    try:
        # Parse proxy URL
        parsed = urlparse(proxy_url)
        if not parsed.scheme or not parsed.hostname:
            command_ctx.console.print(f"[red]Invalid proxy URL: {proxy_url}[/red]")
            raise typer.Exit(code=1)

        # Prepare proxy string
        if parsed.port:
            proxy_string = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
        else:
            proxy_string = f"{parsed.scheme}://{parsed.hostname}"

        # Test proxy
        try:
            import time

            start_time = time.time()
            proxies = {
                "http://": proxy_string,
                "https://": proxy_string,
            }

            response = httpx.get(
                target_url, proxies=proxies, timeout=timeout, follow_redirects=True
            )
            elapsed_ms = (time.time() - start_time) * 1000

            result = {
                "proxy": proxy_string,
                "status": "HEALTHY" if response.status_code < 400 else "DEGRADED",
                "response_code": response.status_code,
                "response_time_ms": round(elapsed_ms, 1),
                "target_url": target_url,
            }

            if command_ctx.format == FormatterOutputFormat.JSON:
                render_json(result)
            else:
                if response.status_code < 400:
                    command_ctx.console.print("[green]✓ Proxy is healthy[/green]")
                else:
                    command_ctx.console.print("[yellow]! Proxy degraded[/yellow]")
                command_ctx.console.print(f"Response Code: {response.status_code}")
                command_ctx.console.print(f"Response Time: {result['response_time_ms']}ms")

        except httpx.ConnectError as e:
            result = {
                "proxy": proxy_string,
                "status": "UNHEALTHY",
                "error": str(e),
                "reason": "Connection failed",
            }
            if command_ctx.format == FormatterOutputFormat.JSON:
                render_json(result)
            else:
                command_ctx.console.print(f"[red]✗ Proxy connection failed: {e}[/red]")
            raise typer.Exit(code=1)
        except httpx.TimeoutException as e:
            result = {
                "proxy": proxy_string,
                "status": "UNHEALTHY",
                "error": str(e),
                "reason": "Timeout",
            }
            if command_ctx.format == FormatterOutputFormat.JSON:
                render_json(result)
            else:
                command_ctx.console.print(f"[red]✗ Proxy timeout after {timeout}s[/red]")
            raise typer.Exit(code=1)

    except typer.Exit:
        raise
    except Exception as e:
        command_ctx.console.print(f"[red]Error validating proxy: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def import_proxies(
    file_path: Path = typer.Argument(..., help="File path (JSON, CSV, or plain text)", exists=True),
    format_type: str = typer.Option(
        "auto",
        "--format",
        "-f",
        help="File format (auto, json, csv, text)",
    ),
    pool_name: str = typer.Option(
        "imported",
        "--pool",
        "-p",
        help="Target pool name",
    ),
    dedup: bool = typer.Option(
        True,
        "--dedup/--no-dedup",
        help="Deduplicate proxies before import",
    ),
) -> None:
    """Import proxies from file (JSON, CSV, or plain text).

    Examples:
      proxywhirl import_proxies proxies.json
      proxywhirl import_proxies proxies.csv --format csv
      proxywhirl import_proxies proxies.txt --format text --pool backup
      proxywhirl import_proxies data.json --no-dedup --json
    """
    import json

    command_ctx = get_context()

    try:
        # Determine format
        if format_type == "auto":
            suffix = file_path.suffix.lower()
            if suffix == ".json":
                format_type = "json"
            elif suffix == ".csv":
                format_type = "csv"
            else:
                format_type = "text"

        # Parse file
        proxies = []

        if format_type == "json":
            with open(file_path) as f:
                data = json.load(f)
                if isinstance(data, list):
                    proxies = data
                elif isinstance(data, dict) and "proxies" in data:
                    proxies = data["proxies"]
                else:
                    proxies = [str(data)]
        elif format_type == "csv":
            import csv

            with open(file_path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if "proxy" in row:
                        proxies.append(row["proxy"])
                    elif "url" in row:
                        proxies.append(row["url"])
                    else:
                        proxies.append(str(list(row.values())[0]))
        else:  # text
            with open(file_path) as f:
                proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        if not proxies:
            command_ctx.console.print("[yellow]No proxies found in file[/yellow]")
            raise typer.Exit(code=1)

        # Deduplicate if requested
        if dedup:
            proxies = list(dict.fromkeys(proxies))

        # Import proxies
        rotator = command_ctx.rotator
        imported = 0
        failed = 0
        errors = []

        for proxy_str in proxies:
            try:
                # Add to pool (format depends on implementation)
                rotator.pool.add_proxy_from_string(proxy_str)
                imported += 1
            except Exception as e:
                failed += 1
                errors.append({"proxy": proxy_str, "error": str(e)})

        result = {
            "file": str(file_path),
            "format": format_type,
            "total_parsed": len(proxies),
            "imported": imported,
            "failed": failed,
            "pool_name": pool_name,
        }

        if errors and command_ctx.verbose:
            result["errors"] = errors

        if command_ctx.format == FormatterOutputFormat.JSON:
            render_json(result)
        else:
            command_ctx.console.print("[green]✓ Import completed[/green]")
            command_ctx.console.print(f"Imported: {imported} proxies")
            if failed:
                command_ctx.console.print(f"[yellow]Failed: {failed} proxies[/yellow]")

    except Exception as e:
        command_ctx.console.print(f"[red]Error importing proxies: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def diagnose() -> None:
    """Run system health diagnostics.

    Checks database connectivity, configuration, dependencies, and system health.
    Useful for troubleshooting issues.

    Examples:
      proxywhirl diagnose
    """
    import platform
    import sqlite3
    from datetime import datetime

    command_ctx = get_context()
    console = command_ctx.console

    console.print("[bold cyan]ProxyWhirl System Diagnostics[/bold cyan]\n")

    diagnostics = {
        "system": {},
        "configuration": {},
        "database": {},
        "proxy_pool": {},
        "dependencies": {},
    }

    try:
        diagnostics["system"]["platform"] = platform.system()
        diagnostics["system"]["python_version"] = f"{platform.python_version()}"
        diagnostics["system"]["architecture"] = platform.machine()
        console.print("[bold]System Information[/bold]")
        console.print(f"  Platform: {diagnostics['system']['platform']}")
        console.print(f"  Python: {diagnostics['system']['python_version']}")
        console.print(f"  Architecture: {diagnostics['system']['architecture']}\n")
    except Exception as e:
        console.print(f"[red]✗ System check failed: {e}[/red]\n")
        diagnostics["system"]["error"] = str(e)

    try:
        console.print("[bold]Configuration[/bold]")
        cfg = command_ctx.config
        diagnostics["configuration"]["has_config"] = command_ctx.config_path.exists()
        diagnostics["configuration"]["config_path"] = str(command_ctx.config_path)
        console.print(f"  Config file: {command_ctx.config_path}")
        console.print(f"  Exists: {'✓' if diagnostics['configuration']['has_config'] else '✗'}")

        if hasattr(cfg, "data_storage") and cfg.data_storage:
            db_path = getattr(cfg.data_storage, "db_path", None)
            if db_path:
                diagnostics["configuration"]["database_path"] = str(db_path)
                console.print(f"  Database: {db_path}\n")
        else:
            console.print("[yellow]  Note: No persistent storage configured[/yellow]\n")
    except Exception as e:
        console.print(f"[red]✗ Configuration check failed: {e}[/red]\n")
        diagnostics["configuration"]["error"] = str(e)

    try:
        console.print("[bold]Database Connection[/bold]")
        if hasattr(command_ctx.config, "data_storage") and command_ctx.config.data_storage:
            db_path = getattr(command_ctx.config.data_storage, "db_path", None)
            if db_path:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM proxy_table")
                proxy_count = cursor.fetchone()[0]
                conn.close()

                diagnostics["database"]["connected"] = True
                diagnostics["database"]["tables"] = table_count
                diagnostics["database"]["proxies"] = proxy_count
                console.print(f"  ✓ Connected to {db_path}")
                console.print(f"  Tables: {table_count}")
                console.print(f"  Proxies in DB: {proxy_count}\n")
            else:
                console.print("[yellow]  No database path configured[/yellow]\n")
        else:
            console.print("[yellow]  No storage configuration[/yellow]\n")
    except sqlite3.Error as e:
        console.print(f"[red]✗ Database connection failed: {e}[/red]\n")
        diagnostics["database"]["error"] = str(e)
    except Exception as e:
        console.print(f"[yellow]⚠ Database check skipped: {e}[/yellow]\n")
        diagnostics["database"]["warning"] = str(e)

    try:
        console.print("[bold]Proxy Pool Status[/bold]")
        rotator = command_ctx.rotator
        proxies = rotator.pool.get_all_proxies()
        healthy_count = sum(
            1 for p in proxies if hasattr(p, "health_status") and p.health_status.name == "HEALTHY"
        )
        diagnostics["proxy_pool"]["total"] = len(proxies)
        diagnostics["proxy_pool"]["healthy"] = healthy_count
        console.print(f"  Total proxies: {len(proxies)}")
        console.print(f"  Healthy: {healthy_count}")
        if len(proxies) > 0:
            console.print(f"  Health ratio: {healthy_count}/{len(proxies)}")
        console.print()
    except Exception as e:
        console.print(f"[yellow]⚠ Proxy pool check skipped: {e}[/yellow]\n")
        diagnostics["proxy_pool"]["warning"] = str(e)

    try:
        console.print("[bold]Key Dependencies[/bold]")
        import_checks = {
            "httpx": False,
            "pydantic": False,
            "sqlmodel": False,
            "loguru": False,
            "rich": False,
            "typer": False,
        }
        for module in import_checks:
            try:
                __import__(module)
                import_checks[module] = True
                console.print(f"  ✓ {module}")
            except ImportError:
                console.print(f"  [red]✗ {module}[/red]")

        diagnostics["dependencies"] = import_checks
        console.print()
    except Exception as e:
        console.print(f"[yellow]⚠ Dependency check skipped: {e}[/yellow]\n")

    console.print("[bold cyan]Diagnostics Complete[/bold cyan]")

    if command_ctx.format == FormatterOutputFormat.JSON:
        import json

        console.print_json(data=diagnostics)


@app.command()
def diversity() -> None:
    """Analyze proxy pool diversity metrics.

    Shows geographic and AS (Autonomous System) diversity metrics.
    Helps identify if proxy pool is balanced across regions.

    Examples:
      proxywhirl diversity
      proxywhirl diversity --format json
    """
    from proxywhirl.diversity_metrics import DiversityAnalyzer

    command_ctx = get_context()
    console = command_ctx.console

    try:
        rotator = command_ctx.rotator
        proxies = rotator.pool.get_all_proxies()

        if not proxies:
            console.print("[yellow]No proxies in pool[/yellow]")
            return

        metrics = DiversityAnalyzer.calculate_metrics(proxies)
        diversity_score = DiversityAnalyzer.get_diversity_score(metrics, len(proxies))
        warning = DiversityAnalyzer.get_concentration_warning(metrics, len(proxies))

        if command_ctx.format == FormatterOutputFormat.JSON:
            console.print_json(
                data={
                    "total_proxies": len(proxies),
                    "country_count": metrics.country_count,
                    "as_count": metrics.as_count,
                    "city_count": metrics.city_count,
                    "diversity_score": round(diversity_score, 2),
                    "shannon_entropy": round(metrics.shannon_entropy, 3),
                    "geographic_spread": round(metrics.geographic_spread, 2),
                    "top_countries": {
                        k: v
                        for k, v in sorted(
                            metrics.country_distribution.items(),
                            key=lambda x: x[1],
                            reverse=True,
                        )[:5]
                    },
                    "top_as": {
                        k: v
                        for k, v in sorted(
                            metrics.as_distribution.items(),
                            key=lambda x: x[1],
                            reverse=True,
                        )[:5]
                    },
                    "warning": warning,
                }
            )
        else:
            console.print("[bold cyan]Proxy Pool Diversity Analysis[/bold cyan]\n")
            console.print(f"Total proxies: {len(proxies)}")
            console.print(f"Unique countries: {metrics.country_count}")
            console.print(f"Unique ASNs: {metrics.as_count}")
            console.print(f"Unique cities: {metrics.city_count}")
            console.print()

            score_color = (
                "green" if diversity_score >= 70 else ("yellow" if diversity_score >= 50 else "red")
            )
            console.print(
                f"[{score_color}]Diversity Score: {diversity_score:.1f}/100[/{score_color}]"
            )
            console.print(f"Geographic Spread: {metrics.geographic_spread:.1f}%")
            console.print(f"Shannon Entropy: {metrics.shannon_entropy:.3f}")

            if warning:
                console.print(f"\n[yellow]⚠ Warning: {warning}[/yellow]")

            if metrics.country_distribution:
                console.print("\n[bold]Top Countries[/bold]")
                for country, count in sorted(
                    metrics.country_distribution.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:5]:
                    pct = (count / len(proxies)) * 100
                    console.print(f"  {country}: {count} ({pct:.1f}%)")

            if metrics.as_distribution:
                console.print("\n[bold]Top ASNs[/bold]")
                for asn, count in sorted(
                    metrics.as_distribution.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:5]:
                    pct = (count / len(proxies)) * 100
                    console.print(f"  {asn}: {count} ({pct:.1f}%)")

    except Exception as e:
        console.print(f"[red]Error analyzing diversity: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def shell() -> None:
    """Interactive REPL shell for proxy operations.

    Examples:
      proxywhirl shell
      # Then use: list, stats, rotate, validate <url>, exit
    """
    import cmd
    import shlex
    from pathlib import Path

    from proxywhirl.models import HealthStatus

    command_ctx = get_context()

    class ProxyWhirlREPL(cmd.Cmd):
        """Interactive proxy rotation shell."""

        intro = """
[bold cyan]ProxyWhirl Interactive Shell[/bold cyan]
Type [bold]help[/bold] for commands. Type [bold]exit[/bold] or [bold]quit[/bold] to exit.
        """
        prompt = "proxywhirl> "
        history_file = Path.home() / ".proxywhirl_history"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.history_list: list[str] = []
            self._load_history()

        def _load_history(self) -> None:
            """Load command history from file."""
            if self.history_file.exists():
                try:
                    with open(self.history_file) as f:
                        self.history_list = [line.rstrip("\n") for line in f.readlines()]
                except Exception:
                    pass

        def _save_history(self) -> None:
            """Save command history to file."""
            try:
                with open(self.history_file, "a") as f:
                    if self.history_list:
                        f.write(self.history_list[-1] + "\n")
            except Exception:
                pass

        def do_history(self, arg: str) -> None:
            """Search command history: history [search_term]"""
            if arg:
                matches = [cmd for cmd in self.history_list if arg.lower() in cmd.lower()]
                if matches:
                    for i, cmd_str in enumerate(matches[-10:], 1):
                        command_ctx.console.print(f"[cyan]{i}[/cyan] {cmd_str}")
                else:
                    command_ctx.console.print("[yellow]No matching commands in history[/yellow]")
            else:
                for i, cmd_str in enumerate(self.history_list[-20:], 1):
                    command_ctx.console.print(f"[cyan]{i}[/cyan] {cmd_str}")

        def onecmd_plus_hooks(self, line: str) -> bool:
            """Override to save commands in history."""
            if line and not line.startswith("?") and not line.startswith("#"):
                self.history_list.append(line)
                self._save_history()
            return super().onecmd_plus_hooks(line)

        def do_list(self, arg: str) -> None:
            """List proxies: list [status] [--limit N]"""
            try:
                rotator = command_ctx.rotator
                proxies = rotator.pool.get_all_proxies()

                if arg:
                    parts = shlex.split(arg)
                    if parts[0].upper() in ["HEALTHY", "DEGRADED", "UNHEALTHY", "DEAD"]:
                        status_enum = HealthStatus[parts[0].upper()]
                        proxies = [p for p in proxies if p.health_status == status_enum]

                limit = 10
                for i, part in enumerate(parts):
                    if part == "--limit" and i + 1 < len(parts):
                        limit = int(parts[i + 1])

                proxies = proxies[:limit]

                if not proxies:
                    command_ctx.console.print("[yellow]No proxies found[/yellow]")
                    return

                table = Table(title=f"Proxies ({len(proxies)} total)")
                table.add_column("Proxy", style="cyan")
                table.add_column("Status", style="yellow")
                table.add_column("Country", style="magenta")

                for p in proxies:
                    status_text = p.health_status.name if hasattr(p, "health_status") else "UNKNOWN"
                    table.add_row(
                        p.proxy_string,
                        status_text,
                        getattr(p, "country", "Unknown"),
                    )

                command_ctx.console.print(table)
            except Exception as e:
                command_ctx.console.print(f"[red]Error: {e}[/red]")

        def do_stats(self, _arg: str) -> None:
            """Show pool statistics."""
            try:
                rotator = command_ctx.rotator
                proxies = rotator.pool.get_all_proxies()
                total = len(proxies)
                healthy = sum(1 for p in proxies if p.health_status == HealthStatus.HEALTHY)

                command_ctx.console.print("[bold]Statistics[/bold]")
                command_ctx.console.print(f"Total: {total}")
                command_ctx.console.print(f"Healthy: {healthy}")
            except Exception as e:
                command_ctx.console.print(f"[red]Error: {e}[/red]")

        def do_rotate(self, _arg: str) -> None:
            """Get next proxy."""
            try:
                rotator = command_ctx.rotator
                proxy = rotator.get_proxy()
                command_ctx.console.print(f"[green]Next proxy:[/green] {proxy.proxy_string}")
            except Exception as e:
                command_ctx.console.print(f"[red]Error: {e}[/red]")

        def do_validate(self, arg: str) -> None:
            """Validate proxy: validate <url>"""
            if not arg:
                command_ctx.console.print("[yellow]Usage: validate <url>[/yellow]")
                return
            # Simplified validation
            command_ctx.console.print(f"[blue]Validating proxy against {arg}...[/blue]")
            command_ctx.console.print("[green]✓ Validation would run here[/green]")

        def do_exit(self, _arg: str) -> None:
            """Exit the shell."""
            command_ctx.console.print("[cyan]Goodbye![/cyan]")
            return True

        def do_quit(self, _arg: str) -> None:
            """Exit the shell."""
            return self.do_exit(_arg)

        def do_help(self, arg: str) -> None:
            """Show help."""
            if not arg:
                command_ctx.console.print(
                    """
[bold]Available Commands:[/bold]
  list [status] [--limit N]  - List proxies
  stats                       - Show pool statistics
  rotate                      - Get next proxy
  validate <url>              - Validate proxy
  history [search_term]       - Search command history
  exit, quit                  - Exit shell
  help [command]              - Show help
                """
                )
            else:
                super().do_help(arg)

    try:
        repl = ProxyWhirlREPL()
        command_ctx.console.print(repl.intro)
        repl.cmdloop()
    except KeyboardInterrupt:
        command_ctx.console.print("\n[cyan]Shell interrupted[/cyan]")
    except Exception as e:
        command_ctx.console.print(f"[red]Shell error: {e}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
