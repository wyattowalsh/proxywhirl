#!/usr/bin/env python3
"""
Health check script for ProxyWhirl loaders.
This script tests all available loaders and generates health reports.
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from proxywhirl.loaders import (
    ClarketmHttpLoader,
    JetkaiProxyListLoader,
    MonosansLoader,
    ProxiflyLoader,
    ProxyScrapeLoader,
    TheSpeedXHttpLoader,
    TheSpeedXSocksLoader,
    VakhovFreshProxyLoader,
)
from proxywhirl.loaders.base import BaseLoader

# Configure loguru for script logging
logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")


class LoaderHealthChecker:
    """Health checker for ProxyWhirl loaders."""

    def __init__(self):
        self.loaders = [
            TheSpeedXHttpLoader(),
            TheSpeedXSocksLoader(),
            ClarketmHttpLoader(),
            MonosansLoader(),
            ProxyScrapeLoader(),
            ProxiflyLoader(),
            VakhovFreshProxyLoader(),
            JetkaiProxyListLoader(),
        ]

    async def test_loader(self, loader) -> Dict[str, Any]:
        """Test a single loader and return health metrics."""
        logger.info(f"Testing loader: {loader.name}")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Test connection
            can_connect = await loader.test_connection()
            
            # Try to load a small sample
            if can_connect:
                async with loader:
                    df = await asyncio.wait_for(loader.load_async(), timeout=30.0)
                    proxy_count = len(df)
            else:
                proxy_count = 0
                
        except asyncio.TimeoutError:
            can_connect = False
            proxy_count = 0
            logger.warning(f"Timeout testing {loader.name}")
        except Exception as e:
            can_connect = False
            proxy_count = 0
            logger.warning(f"Error testing {loader.name}: {e}")
        
        end_time = datetime.now(timezone.utc)
        response_time = (end_time - start_time).total_seconds()
        
        # Get loader health status
        health = loader.get_health_status()
        
        return {
            "name": loader.name,
            "description": loader.description,
            "status": "✅ Operational" if can_connect else "❌ Failed",
            "can_connect": can_connect,
            "proxy_count": proxy_count,
            "response_time": round(response_time, 2),
            "success_rate": round(health.success_rate * 100, 1),
            "last_tested": datetime.now(timezone.utc).isoformat(),
            "capabilities": {
                "schemes": list(loader.capabilities.schemes) if loader.capabilities.schemes else [],
                "supports_filtering": loader.capabilities.supports_filtering,
                "requires_auth": loader.capabilities.requires_auth,
            }
        }

    async def run_health_check(self) -> Dict[str, Any]:
        """Run health check on all loaders."""
        logger.info(f"Starting health check for {len(self.loaders)} loaders")
        
        # Test all loaders concurrently with timeout
        tasks = [self.test_loader(loader) for loader in self.loaders]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        loader_results = []
        operational_count = 0
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Failed to test loader: {result}")
                continue
            
            loader_results.append(result)
            if result["can_connect"]:
                operational_count += 1
        
        # Calculate overall stats
        total_loaders = len(loader_results)
        operational_percentage = (operational_count / total_loaders * 100) if total_loaders > 0 else 0
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_loaders": total_loaders,
                "operational": operational_count,
                "failed": total_loaders - operational_count,
                "operational_percentage": round(operational_percentage, 1)
            },
            "loaders": sorted(loader_results, key=lambda x: x["name"])
        }

    def generate_markdown_table(self, health_data: Dict[str, Any]) -> str:
        """Generate markdown table from health data."""
        summary = health_data["summary"]
        loaders = health_data["loaders"]
        
        # Header with summary
        markdown = f"""## 📊 Loader Health Status

**Last Updated:** {datetime.fromisoformat(health_data['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M UTC')}

**Summary:** {summary['operational']}/{summary['total_loaders']} loaders operational ({summary['operational_percentage']}%)

| Loader | Status | Proxies | Response Time | Success Rate | Schemes |
|--------|--------|---------|---------------|--------------|---------|
"""
        
        # Add each loader row
        for loader in loaders:
            schemes = ', '.join(loader['capabilities']['schemes'][:3])  # Limit to 3 schemes
            if len(loader['capabilities']['schemes']) > 3:
                schemes += '...'
            
            markdown += f"| {loader['name']} | {loader['status']} | {loader['proxy_count']} | {loader['response_time']}s | {loader['success_rate']}% | {schemes} |\n"
        
        return markdown

    def generate_compact_badge(self, health_data: Dict[str, Any]) -> str:
        """Generate a compact status badge."""
        summary = health_data["summary"]
        operational = summary["operational"]
        total = summary["total_loaders"]
        percentage = summary["operational_percentage"]
        
        if percentage >= 80:
            status = "🟢 Excellent"
        elif percentage >= 60:
            status = "🟡 Good"
        elif percentage >= 40:
            status = "🟠 Fair"
        else:
            status = "🔴 Poor"
        
        return f"**Loader Health:** {status} ({operational}/{total} operational)"


async def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # Output JSON for GitHub Actions
        checker = LoaderHealthChecker()
        health_data = await checker.run_health_check()
        print(json.dumps(health_data, indent=2))
    else:
        # Output markdown table
        checker = LoaderHealthChecker()
        health_data = await checker.run_health_check()
        print(checker.generate_markdown_table(health_data))


if __name__ == "__main__":
    asyncio.run(main())
