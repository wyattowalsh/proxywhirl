"""proxywhirl/cli/utils.py -- Utility functions and helpers for CLI"""

from __future__ import annotations

import asyncio
import types
from typing import Any, Coroutine, Optional, TypeVar

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from ..caches import CacheType
from .state import ProxyWhirlError

T = TypeVar("T")

__all__ = [
    "handle_error", 
    "_run",
    "EnhancedProgressContext",
    "get_health_status_emoji",
    "get_health_trend_arrow",
    "validate_cache_consistency",
]


def handle_error(error: Exception, console: Console) -> None:
    """Centralized error handling with Typer best practices and Rich formatting.
    
    Uses appropriate Typer exception types for better CLI integration.
    """
    if isinstance(error, ProxyWhirlError):
        console.print(
            Panel(
                f"[error]❌ {error.message}[/error]"
                + (
                    f"\n[warning]💡 Suggestion: {error.suggestion}[/warning]"
                    if error.suggestion
                    else ""
                ),
                title="ProxyWhirl Error",
                border_style="red",
            )
        )
        # Use typer.Abort for consistent error handling
        raise typer.Abort()
    elif isinstance(error, (FileNotFoundError, PermissionError)):
        # Use typer.BadParameter for parameter-related errors
        raise typer.BadParameter(str(error))
    else:
        console.print(f"[error]❌ Unexpected error: {error}[/error]")
        raise typer.Abort()


def _run(coro: Coroutine[Any, Any, T]) -> T:
    """Async wrapper for Typer commands.
    
    Note: This wrapper is necessary because Typer doesn't have native async support yet.
    See: https://github.com/fastapi/typer/issues/950
    
    Once Typer adds native async support, this wrapper can be removed and commands
    can be declared with async def directly.
    
    Uses a dedicated event loop and intentionally does not close it to avoid
    interfering with Click/Typer testing's IO capture in some environments.
    """
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(coro)


class EnhancedProgressContext:
    """Enhanced progress context with ETA, throughput, and health indicators"""

    def __init__(self, console: Console, description: str, total: Optional[int] = None):
        self.console = console
        self.description = description
        self.total = total
        self.progress: Optional[Progress] = None
        self.task_id = None
        self.start_time: Optional[float] = None
        self.current_count = 0

    def __enter__(self):
        import time

        self.start_time = time.time()

        # Create progress with enhanced columns
        if self.total:
            # For determinate progress with ETA
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=None),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=self.console,
                transient=False,
            )
        else:
            # For indeterminate progress with elapsed time only
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=self.console,
                transient=False,
            )

        self.progress.__enter__()

        self.task_id = self.progress.add_task(f"[cyan]{self.description}...", total=self.total)
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[types.TracebackType],
    ) -> None:
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, completed=True)
            self.progress.__exit__(exc_type, exc_val, exc_tb)

    def update(
        self,
        count: Optional[int] = None,
        description: Optional[str] = None,
        health_status: str = "🟢",
    ):
        """Update progress with optional health indicator"""
        if not self.progress or self.task_id is None:
            return

        update_kwargs = {}

        if count is not None:
            self.current_count = count
            update_kwargs["completed"] = count

        if description:
            # Add health status emoji to description
            update_kwargs["description"] = f"[cyan]{description} {health_status}[/cyan]"
        elif count is not None and self.total and self.start_time:
            # Calculate throughput for progress updates
            import time

            elapsed = time.time() - self.start_time
            throughput = count / elapsed if elapsed > 0 else 0
            update_kwargs["description"] = (
                f"[cyan]{self.description} {health_status} ({throughput:.1f}/s)[/cyan]"
            )

        self.progress.update(self.task_id, **update_kwargs)

    def complete_with_stats(self, final_count: int, success_rate: Optional[float] = None):
        """Complete progress with final statistics"""
        if not self.progress or self.task_id is None or self.start_time is None:
            return

        import time

        elapsed = time.time() - self.start_time
        throughput = final_count / elapsed if elapsed > 0 else 0

        if success_rate is not None:
            health_emoji = "🟢" if success_rate > 0.8 else "🟡" if success_rate > 0.5 else "🔴"
            description = f"[cyan]✅ Complete: {final_count} items ({success_rate:.1%} success) @ {throughput:.1f}/s {health_emoji}[/cyan]"
        else:
            description = f"[cyan]✅ Complete: {final_count} items @ {throughput:.1f}/s 🟢[/cyan]"

        self.progress.update(self.task_id, description=description, completed=True)


def get_health_status_emoji(success_rate: float) -> str:
    """Get health status emoji based on success rate"""
    if success_rate >= 0.9:
        return "🟢"  # Excellent
    elif success_rate >= 0.7:
        return "🟡"  # Good
    elif success_rate >= 0.5:
        return "🟠"  # Fair
    else:
        return "🔴"  # Poor


def get_health_trend_arrow(current: float, previous: Optional[float] = None) -> str:
    """Get trend arrow for health metrics"""
    if previous is None:
        return ""

    if current > previous + 0.05:  # 5% improvement threshold
        return "↗️"
    elif current < previous - 0.05:  # 5% degradation threshold
        return "↘️"
    else:
        return "➡️"  # Stable


def validate_cache_consistency(ctx: typer.Context, param: typer.CallbackParam, value: Any) -> Any:
    """Callback to ensure cache_type and cache_path are consistent.
    
    Uses proper Typer callback pattern with Context and CallbackParam support.
    Includes resilient_parsing check for shell completion compatibility.
    """
    # Handle shell completion without validation
    if ctx.resilient_parsing:
        return value
        
    if not value:
        return value

    # Access other parameters through context
    # Try different parameter names depending on the command
    cache_type = (
        ctx.params.get("cache_type")  # For older commands
        or ctx.params.get("fetch_cache_type")  # For fetch command
        or ctx.params.get("get_cache_type")  # For get command
        or ctx.params.get("health_cache_type")  # For health command
        or CacheType.MEMORY
    )

    cache_path = (
        ctx.params.get("cache_path")  # For older commands
        or ctx.params.get("fetch_cache_path")  # For fetch command
        or ctx.params.get("get_cache_path")  # For get command
        or ctx.params.get("health_cache_path")  # For health command
    )

    if cache_type in [CacheType.JSON, CacheType.SQLITE] and not cache_path:
        raise typer.BadParameter(
            f"--cache-path is required when using {cache_type.value} cache. "
            f"Provide a path like: --cache-path ./proxies.{cache_type.value.lower()}"
        )
    return value
