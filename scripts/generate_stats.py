"""Generate stats.json and proxies-rich.json for the web dashboard.

This script is a thin wrapper around proxywhirl.exports for use in CI/CD.
For direct usage, prefer: proxywhirl export
"""

import asyncio
from pathlib import Path

from loguru import logger

from proxywhirl.exports import export_for_web


def main() -> None:
    """Main entry point."""
    logger.info("Generating web dashboard data...")

    outputs = asyncio.run(export_for_web(
        db_path=Path("proxywhirl.db"),
        output_dir=Path("docs/proxy-lists"),
        include_stats=True,
        include_rich_proxies=True,
    ))

    for name, path in outputs.items():
        logger.info(f"Exported {name}: {path}")

    logger.info("Export complete!")


if __name__ == "__main__":
    main()
