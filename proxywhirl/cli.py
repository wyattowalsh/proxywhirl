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

import click
import httpx
import typer
from rich.console import Console
from rich.table import Table
from typer.core import TyperGroup

from proxywhirl.config import CLIConfig, discover_config, load_config
from proxywhirl.formatters import OutputFormat as FormatterOutputFormat
from proxywhirl.models import RequestResult
from proxywhirl.types import ConfigAction, PoolAction
from proxywhirl.utils import CLILock, mask_proxy_url, public_proxy_url

# Typer app instance
app = typer.Typer(
    name="proxywhirl",
    help="Advanced proxy rotation library with CLI interface",
    add_completion=True,
    no_args_is_help=True,
)


class _InvalidActionGroup(TyperGroup):
    """Click group that prints 'Invalid action' for unknown subcommands."""

    def get_command(self, ctx, cmd_name):
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return rv
        click.echo("Invalid action")
        ctx.exit(1)


pool_app = typer.Typer(
    cls=_InvalidActionGroup,
    name="pool",
    help="Manage the proxy pool",
)

config_app = typer.Typer(
    cls=_InvalidActionGroup,
    name="config",
    help="Manage CLI configuration",
)


def _proxy_reference_matches(stored_url: str, requested_url: str) -> bool:
    """Match proxy URLs by exact URL or credential-stripped public URL."""
    return stored_url == requested_url or public_proxy_url(stored_url) == requested_url


def _safe_config_value(value: Any) -> Any:
    """Return a display-safe representation of a CLI config value."""
    from pydantic import BaseModel, SecretStr

    if isinstance(value, SecretStr):
        return "***"
    if isinstance(value, BaseModel):
        return _safe_config_value(value.model_dump(mode="json"))
    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in value.items():
            key_lower = str(key).lower()
            if key_lower == "url" and isinstance(item, str):
                safe[str(key)] = public_proxy_url(item)
            elif key_lower in {"username", "password"}:
                safe[str(key)] = "***" if item else None
            else:
                safe[str(key)] = _safe_config_value(item)
        return safe
    if isinstance(value, list):
        return [_safe_config_value(item) for item in value]
    if isinstance(value, str) and "://" in value and "@" in value:
        return public_proxy_url(value)
    return value


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
        else:
            try:
                resolved_addresses = socket.getaddrinfo(
                    parsed.hostname,
                    None,
                    socket.AF_UNSPEC,
                    socket.SOCK_STREAM,
                )
            except socket.gaierror as e:
                typer.secho(
                    f"Error: Cannot resolve hostname: {parsed.hostname}", err=True, fg="red"
                )
                raise typer.Exit(code=1) from e

            checked_addresses: set[ipaddress.IPv4Address | ipaddress.IPv6Address] = set()
            for address_info in resolved_addresses:
                try:
                    resolved_address = ipaddress.ip_address(address_info[4][0])
                except ValueError:
                    typer.secho(
                        f"Error: Cannot validate resolved address for: {parsed.hostname}",
                        err=True,
                        fg="red",
                    )
                    raise typer.Exit(code=1)
                if (
                    isinstance(resolved_address, ipaddress.IPv6Address)
                    and resolved_address.ipv4_mapped
                ):
                    resolved_address = resolved_address.ipv4_mapped
                if resolved_address in checked_addresses:
                    continue
                checked_addresses.add(resolved_address)
                _reject_forbidden_target_address(resolved_address, parsed.hostname)


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
                url=public_proxy_url(str(p.url)),
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
        rotator.add_proxy(new_proxy)

        # Save updated config
        command_ctx.config.proxies.append(
            ProxyConfig(
                url=proxy,
                username=SecretStr(username) if username else None,
                password=SecretStr(password) if password else None,
            )
        )
        save_config(command_ctx.config, command_ctx.config_path)

        command_ctx.console.print(f"[green]✓[/green] Added proxy: {public_proxy_url(proxy)}")

    elif action == "remove":
        if not proxy:
            command_ctx.console.print("[red]Proxy URL required for 'remove' action[/red]")
            raise typer.Exit(code=1)

        # Find proxy by exact URL or by the credential-stripped URL shown by list/export commands.
        proxy_obj = next(
            (
                p
                for p in rotator.pool.get_all_proxies()
                if _proxy_reference_matches(str(p.url), proxy)
            ),
            None,
        )
        if not proxy_obj:
            command_ctx.console.print(
                f"[red]Error:[/red] Proxy not found: {public_proxy_url(proxy)}"
            )
            raise typer.Exit(code=1)

        # Remove proxy through the rotator so circuit breakers and clients are cleaned up.
        rotator.remove_proxy(str(proxy_obj.id))

        # Save updated config
        command_ctx.config.proxies = [
            p for p in command_ctx.config.proxies if not _proxy_reference_matches(p.url, proxy)
        ]
        save_config(command_ctx.config, command_ctx.config_path)

        command_ctx.console.print(f"[green]✓[/green] Removed proxy: {public_proxy_url(proxy)}")

    elif action == "test":
        if not proxy:
            command_ctx.console.print("[red]Proxy URL required for 'test' action[/red]")
            raise typer.Exit(code=1)

        # Validate target URL to prevent SSRF
        validate_target_url(target_url, allow_private=allow_private)

        # Test proxy with HTTP request
        command_ctx.console.print(f"Testing proxy: {public_proxy_url(proxy)}...")
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
            command_ctx.console.print(f"[red]✗[/red] Proxy test failed: {mask_proxy_url(str(e))}")
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

        value_obj = _safe_config_value(getattr(command_ctx.config, key))
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


@pool_app.command("list")
def _pool_list() -> None:
    pool("list")


@pool_app.command("add")
def _pool_add(
    proxy: str = typer.Argument(..., help="Proxy URL"),
    username: str | None = typer.Option(None, "--username", "-u", help="Proxy username"),
    password: str | None = typer.Option(None, "--password", "-p", help="Proxy password"),
) -> None:
    pool("add", proxy=proxy, username=username, password=password)


@pool_app.command("remove")
def _pool_remove(
    proxy: str = typer.Argument(..., help="Proxy URL"),
) -> None:
    pool("remove", proxy=proxy)


@pool_app.command("test")
def _pool_test(
    proxy: str = typer.Argument(..., help="Proxy URL"),
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
    pool("test", proxy=proxy, target_url=target_url, allow_private=allow_private)


@pool_app.command("stats")
def _pool_stats() -> None:
    pool("stats")


@config_app.command("init")
def _config_init() -> None:
    config("init")


@config_app.command("show")
def _config_show() -> None:
    config("show")


@config_app.command("get")
def _config_get(
    key: str = typer.Argument(..., help="Config key"),
) -> None:
    config("get", key=key)


@config_app.command("set")
def _config_set(
    key: str = typer.Argument(..., help="Config key"),
    value: str = typer.Argument(..., help="Config value"),
) -> None:
    config("set", key=key, value=value)


app.add_typer(pool_app, name="pool")
app.add_typer(config_app, name="config")


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
def sources(
    validate: bool = typer.Option(
        False,
        "--validate",
        "-v",
        help="Validate configured proxy sources",
    ),
    timeout: float = typer.Option(
        15.0,
        "--timeout",
        "-t",
        min=0.1,
        help="Timeout per source in seconds",
    ),
    concurrency: int = typer.Option(
        20,
        "--concurrency",
        "-j",
        min=1,
        help="Maximum concurrent source validations",
    ),
    fail_on_unhealthy: bool = typer.Option(
        False,
        "--fail-on-unhealthy",
        "-f",
        help="Exit non-zero if any enabled source is unhealthy",
    ),
) -> None:
    """List and validate configured proxy sources."""
    from proxywhirl.sources import ALL_SOURCES, validate_sources_sync

    command_ctx = get_context()
    enabled_sources = [source for source in ALL_SOURCES if source.enabled]

    if not validate:
        table = Table(title="Proxy Sources")
        table.add_column("URL", style="cyan")
        table.add_column("Format")
        table.add_column("Protocol")
        table.add_column("Mode")

        for source in enabled_sources:
            source_format = getattr(source.format, "value", source.format)
            protocol = getattr(source.protocol, "value", source.protocol)
            render_mode = getattr(source.render_mode, "value", source.render_mode)
            table.add_row(str(source.url), str(source_format), str(protocol), str(render_mode))

        command_ctx.console.print(table)
        command_ctx.console.print(f"{len(enabled_sources)}/{len(ALL_SOURCES)} sources enabled")
        return

    command_ctx.console.print(f"[bold]Validating {len(enabled_sources)} proxy sources...[/bold]")
    report = validate_sources_sync(timeout=timeout, concurrency=concurrency)

    table = Table(title="Source Validation Results")
    table.add_column("Status", style="bold")
    table.add_column("Source", style="cyan")
    table.add_column("HTTP", justify="right")
    table.add_column("Proxy Data", justify="right")
    table.add_column("Bytes", justify="right")
    table.add_column("Time", justify="right")
    table.add_column("Error")

    for result in sorted(report.results, key=lambda item: (item.is_healthy, item.name.lower())):
        status_text = "[green]healthy[/green]" if result.is_healthy else "[red]unhealthy[/red]"
        status_code = str(result.status_code) if result.status_code is not None else "-"
        error = result.error or ""
        table.add_row(
            status_text,
            result.name,
            status_code,
            "yes" if result.has_proxies else "no",
            str(result.content_length),
            f"{result.response_time_ms:.0f}ms",
            error,
        )

    command_ctx.console.print(table)
    command_ctx.console.print(
        f"{report.healthy_sources}/{report.total_sources} sources healthy "
        f"({report.unhealthy_sources} unhealthy)"
    )

    if fail_on_unhealthy and not report.all_healthy:
        raise typer.Exit(code=1)


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
      proxywhirl validate-proxy http://proxy.example.com:8080
      proxywhirl validate-proxy http://proxy.example.com:8080 --target https://httpbin.org/status/200
      proxywhirl validate-proxy socks5://proxy.example.com:1080 --timeout 5
      proxywhirl --format json validate-proxy http://proxy.example.com:8080
    """
    command_ctx = get_context()

    try:
        # Parse proxy URL
        parsed = urlparse(proxy_url)
        if not parsed.scheme or not parsed.hostname:
            command_ctx.console.print(f"[red]Invalid proxy URL: {proxy_url}[/red]")
            raise typer.Exit(code=1)

        proxy_string = f"{parsed.scheme}://{parsed.netloc}"
        display_proxy = public_proxy_url(proxy_string)

        # Test proxy
        try:
            import time

            start_time = time.time()
            response = httpx.get(
                target_url, proxy=proxy_string, timeout=timeout, follow_redirects=True
            )
            elapsed_ms = (time.time() - start_time) * 1000

            result = {
                "proxy": display_proxy,
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
                "proxy": display_proxy,
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
                "proxy": display_proxy,
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
      proxywhirl import-proxies proxies.json
      proxywhirl import-proxies proxies.csv --format csv
      proxywhirl import-proxies proxies.txt --format text --pool backup
      proxywhirl --format json import-proxies data.json --no-dedup
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

        from proxywhirl.config import ProxyConfig, save_config
        from proxywhirl.models import Proxy

        imported = 0
        failed = 0
        errors = []
        existing_proxy_urls = {proxy_config.url for proxy_config in command_ctx.config.proxies}

        for proxy_str in proxies:
            try:
                Proxy(url=proxy_str)
                if proxy_str in existing_proxy_urls:
                    continue
                command_ctx.config.proxies.append(ProxyConfig(url=proxy_str))
                existing_proxy_urls.add(proxy_str)
                imported += 1
            except Exception as e:
                failed += 1
                errors.append({"proxy": proxy_str, "error": str(e)})

        save_config(command_ctx.config, command_ctx.config_path)

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

    except typer.Exit:
        raise
    except Exception as e:
        command_ctx.console.print(f"[red]Error importing proxies: {e}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
