"""proxywhirl/cli/commands/reference.py -- Reference Commands

Commands for getting help and reference information.
"""

from typing import Optional
import typer
from typing_extensions import Annotated
from rich.table import Table

from ...models import RotationStrategy
from ..app import app


@app.command(
    "version",
    rich_help_panel="📚 Reference", 
    help="[dim]Show version information and system details[/dim]",
)
def version_info(
    ctx: typer.Context,
    details: Annotated[
        bool,
        typer.Option(
            "--details/--no-details",
            help="[info]Show detailed system information[/info]"
        ),
    ] = False,
) -> None:
    """Show ProxyWhirl version and system information"""
    console = ctx.obj.console
    
    try:
        from ... import __version__
        console.print(f"[success]ProxyWhirl version {__version__}[/success]")
        
        if details:
            import sys
            import platform
            
            table = Table(title="System Information", show_header=True)
            table.add_column("Component", style="cyan")
            table.add_column("Version/Info", style="green") 
            
            table.add_row("Python", f"{sys.version.split()[0]}")
            table.add_row("Platform", platform.platform())
            table.add_row("Architecture", platform.machine())
            
            console.print(table)
            
    except ImportError:
        console.print("[error]❌ Version information not available[/error]")


@app.command(
    "config",
    rich_help_panel="📚 Reference",
    help="[cyan]Show current configuration and environment settings[/cyan]",
)
def show_config(ctx: typer.Context) -> None:
    """Show current configuration and environment settings"""
    console = ctx.obj.console
    
    # Show environment variables
    import os
    env_vars = [
        ("PROXYWHIRL_CACHE_TYPE", "Cache backend type"),
        ("PROXYWHIRL_CACHE_PATH", "Cache file path"),
        ("PROXYWHIRL_ROTATION_STRATEGY", "Default rotation strategy"),
        ("PROXYWHIRL_MAX_FETCH_PROXIES", "Max proxies to fetch"),
        ("PROXYWHIRL_VALIDATE", "Auto-validate setting"),
        ("PROXYWHIRL_LIST_LIMIT", "Default list limit"),
        ("PROXYWHIRL_HEALTHY_ONLY", "Show healthy proxies only"),
    ]
    
    table = Table(title="Environment Configuration", show_header=True)
    table.add_column("Environment Variable", style="cyan")
    table.add_column("Current Value", style="green")
    table.add_column("Description", style="dim")
    
    for var_name, description in env_vars:
        value = os.getenv(var_name, "[dim]not set[/dim]")
        table.add_row(var_name, value, description)
    
    console.print(table)


@app.command(name="strategies", rich_help_panel="📚 Reference")
def list_rotation_strategies() -> None:
    """List all available rotation strategies with descriptions"""
    from rich.console import Console
    console = Console()
    
    table = Table(title="Available Rotation Strategies", show_header=True)
    table.add_column("Strategy", style="cyan bold")
    table.add_column("Description", style="green")
    table.add_column("Use Case", style="dim")
    
    strategies = [
        (RotationStrategy.ROUND_ROBIN, "Cycle through proxies in order", "Balanced load distribution"),
        (RotationStrategy.RANDOM, "Select proxies randomly", "Unpredictable patterns"),
        (RotationStrategy.WEIGHTED, "Weight by response time (faster preferred)", "Performance optimization"),
        (RotationStrategy.HEALTH_BASED, "Use health scores (penalize failures)", "Quality focus"),
        (RotationStrategy.LEAST_USED, "Use least frequently used proxy", "Even usage distribution"),
        # Enhanced strategies (may require async handling)
        (RotationStrategy.ASYNC_ROUND_ROBIN, "Async round-robin with concurrency", "High-throughput async"),
        (RotationStrategy.CIRCUIT_BREAKER, "Circuit breaker pattern", "Fault tolerance"),
        (RotationStrategy.METRICS_AWARE, "ML metrics-based selection", "Adaptive performance"),
        (RotationStrategy.ML_ADAPTIVE, "Machine learning adaptive", "Self-optimizing"),
        (RotationStrategy.CONSISTENT_HASH, "Consistent hashing", "Session affinity"),
        (RotationStrategy.GEO_AWARE, "Geographic proximity", "Regional optimization"),
    ]
    
    for strategy, description, use_case in strategies:
        table.add_row(
            strategy.value,
            description, 
            use_case
        )
    
    console.print(table)
    console.print("\n[dim]Use with --rotation-strategy option:[/dim]")
    console.print("[cyan]proxywhirl get --rotation-strategy random[/cyan]")


@app.command(
    "completion",
    rich_help_panel="📚 Reference",
    help="[dim]Generate shell completion scripts[/dim]",
    hidden=True,  # Hidden from main help but available for users who know about it
)
def generate_completion(
    ctx: typer.Context,
    shell: Annotated[
        str,
        typer.Option(
            help="[info]Shell type: bash, zsh, fish, or powershell[/info]",
        ),
    ] = "bash",
    output: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            "-o",
            help="[accent]Output file path (default: stdout)[/accent]",
        ),
    ] = None,
) -> None:
    """Generate shell completion scripts for proxywhirl CLI"""
    console = ctx.obj.console
    
    if shell not in ["bash", "zsh", "fish", "powershell"]:
        console.print(f"[error]❌ Unsupported shell: {shell}[/error]")
        console.print("[info]💡 Supported shells: bash, zsh, fish, powershell[/info]")
        raise typer.Abort()
    
    # For now, provide installation instructions
    console.print(f"[info]Shell completion for {shell} is not yet implemented[/info]")
    console.print("[dim]This feature will be added in a future release[/dim]")
