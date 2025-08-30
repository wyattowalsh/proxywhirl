"""proxywhirl/cli/commands/reference.py -- Reference commands"""

from __future__ import annotations

import typer
from rich.panel import Panel
from rich.text import Text

from ..app import app


@app.command(name="strategies", rich_help_panel="📚 Reference")
def show_strategies(ctx: typer.Context) -> None:
    """[bold]🔄 Show available rotation strategies[/bold]
    
    Display all rotation strategies with descriptions and use cases.
    """
    console = ctx.obj.console
    
    strategies_info = [
        ("round_robin", "🔄 Round Robin", "Fair rotation through all proxies"),
        ("weighted", "⚖️  Weighted", "Prioritize faster/healthier proxies"),
        ("random", "🎲 Random", "Random selection for unpredictability"),
        ("least_used", "📊 Least Used", "Use proxies with lowest usage count"),
        ("response_time", "⚡ Response Time", "Prioritize fastest responding proxies"),
    ]
    
    strategy_text = Text()
    for key, name, description in strategies_info:
        strategy_text.append(f"{name}\n", style="bold cyan")
        strategy_text.append(f"  Key: {key}\n", style="dim")
        strategy_text.append(f"  {description}\n\n", style="white")
    
    console.print(
        Panel(
            strategy_text.rstrip(),
            title="[bold magenta]ProxyWhirl Rotation Strategies[/bold magenta]",
            border_style="blue",
        )
    )
    
    console.print("\n[info]💡 Use with: --rotation-strategy <strategy_key>[/info]")
