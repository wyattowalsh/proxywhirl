#!/usr/bin/env python3
"""
proxywhirl Loader Health Check Script

This script verifies the health of all loaders using the health reporting functionality
of the proxywhirl package. It tests each loader's connectivity and functionality.

Author: proxywhirl SWE Dev Agent
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from proxywhirl import ProxyWhirl, configure_rich_logging, get_logger
from proxywhirl.caches import CacheType
from proxywhirl.models.enums import RotationStrategy

# Configure rich logging for better output
configure_rich_logging()
logger = get_logger(__name__)

console = Console()


async def test_all_loaders():
    """Test the health of all proxywhirl loaders."""
    rprint("\n[bold cyan]🔍 proxywhirl Loader Health Check[/bold cyan]")
    rprint("[dim]Testing connectivity and functionality of all proxy loaders...[/dim]\n")

    try:
        # Initialize ProxyWhirl with minimal configuration for testing
        settings = ProxyWhirlSettings()
        
        proxy_whirl = ProxyWhirl(
            settings=settings,
            cache_type=CacheType.MEMORY,  # Use memory cache for testing
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
            auto_validate=False,  # Disable validation for faster testing
            max_proxies=10,  # Limit for testing
            enable_all_loaders=True,  # Enable all available loaders
        )

        # Generate comprehensive health report
        console.print("[yellow]🏥 Generating health report...[/yellow]")
        health_report = await proxy_whirl.generate_health_report()
        
        # Display the health report
        console.print(Panel(
            health_report,
            title="[bold green]📋 ProxyWhirl Health Report[/bold green]",
            border_style="green",
            expand=True
        ))

        # Save report to file with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_file = project_root / f"loader_health_report_{timestamp}.md"
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(health_report)
        
        console.print(f"\n[green]✅ Health report saved to: {report_file}[/green]")

        # Additional detailed loader testing
        console.print("\n[yellow]🔧 Performing detailed loader tests...[/yellow]")
        
        loader_results = []
        if proxy_whirl.loaders:
            for loader in proxy_whirl.loaders:
                console.print(f"[dim]Testing {loader.name}...[/dim]")
                try:
                    # Test connection
                    can_connect = await loader.test_connection()
                    
                    # Get loader capabilities
                    capabilities = loader.get_capabilities()
                    
                    loader_results.append({
                        "name": loader.name,
                        "description": loader.description,
                        "can_connect": can_connect,
                        "schemes": list(capabilities.schemes) if capabilities.schemes else [],
                        "requires_auth": capabilities.requires_auth,
                        "rate_limited": capabilities.rate_limited,
                        "expected_count": capabilities.expected_count,
                        "supports_filtering": capabilities.supports_filtering,
                    })
                    
                except Exception as e:
                    logger.error(f"Error testing loader {loader.name}: {e}")
                    loader_results.append({
                        "name": loader.name,
                        "description": loader.description,
                        "can_connect": False,
                        "error": str(e),
                        "schemes": [],
                        "requires_auth": False,
                        "rate_limited": False,
                        "expected_count": None,
                        "supports_filtering": False,
                    })

            # Create detailed results table
            table = Table(title="📊 Detailed Loader Test Results", show_header=True, header_style="bold blue")
            table.add_column("Loader", style="cyan", no_wrap=True)
            table.add_column("Status", justify="center", style="bold")
            table.add_column("Schemes", style="dim")
            table.add_column("Auth Required", justify="center")
            table.add_column("Rate Limited", justify="center") 
            table.add_column("Expected Count", justify="right")
            table.add_column("Description", style="dim")

            for result in loader_results:
                status = "✅ Working" if result["can_connect"] else "❌ Failed"
                status_style = "green" if result["can_connect"] else "red"
                
                schemes_str = ", ".join(result["schemes"][:3])  # Limit display
                if len(result["schemes"]) > 3:
                    schemes_str += "..."
                
                auth_icon = "🔐" if result["requires_auth"] else "🔓"
                rate_icon = "⏱️" if result["rate_limited"] else "🚀"
                expected = str(result["expected_count"]) if result["expected_count"] else "N/A"
                
                table.add_row(
                    result["name"],
                    f"[{status_style}]{status}[/{status_style}]",
                    schemes_str or "N/A",
                    auth_icon,
                    rate_icon,
                    expected,
                    result["description"][:50] + "..." if len(result["description"]) > 50 else result["description"]
                )

            console.print(table)

            # Summary statistics
            working_count = sum(1 for r in loader_results if r["can_connect"])
            total_count = len(loader_results)
            success_rate = (working_count / total_count * 100) if total_count > 0 else 0

            console.print(f"\n[bold green]📈 Summary Statistics:[/bold green]")
            console.print(f"  • Total Loaders: {total_count}")
            console.print(f"  • Working: {working_count}")
            console.print(f"  • Failed: {total_count - working_count}")
            console.print(f"  • Success Rate: {success_rate:.1f}%")

            if working_count < total_count:
                console.print(f"\n[bold yellow]⚠️  Warning: {total_count - working_count} loaders are not working properly.[/bold yellow]")
                console.print("[dim]Check network connectivity and loader configurations.[/dim]")
            else:
                console.print(f"\n[bold green]🎉 All loaders are working properly![/bold green]")

        else:
            console.print("[red]❌ No loaders found![/red]")

        return True

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        console.print(f"[red]❌ Health check failed: {e}[/red]")
        return False


def main():
    """Main entry point."""
    try:
        result = asyncio.run(test_all_loaders())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Health check interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]💥 Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
