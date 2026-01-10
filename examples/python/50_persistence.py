"""
Persistence demos: JSON and SQLite storage backends.

Uses temporary paths to stay side-effect free.
Run with: uv run python examples/python/50_persistence.py
"""

from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
EXAMPLES_DIR = CURRENT_DIR.parent
sys.path.append(str(EXAMPLES_DIR))

from _common import print_header  # noqa: E402
from proxywhirl import HealthStatus, Proxy, ProxySource  # noqa: E402
from proxywhirl.storage import FileStorage, SQLiteStorage  # noqa: E402


async def json_storage_demo() -> None:
    print_header("FileStorage (encrypted JSON)")
    proxies = [
        Proxy(url="http://proxy-store-1.local:9000", source=ProxySource.USER),
        Proxy(url="http://proxy-store-2.local:9000", source=ProxySource.FETCHED),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "proxies.json"
        storage = FileStorage(storage_path)
        await storage.save(proxies)
        restored = await storage.load()
        print(f"Stored {len(restored)} proxies at {storage_path}")
        for proxy in restored:
            print(f"• {proxy.url} (source={proxy.source.value})")


async def sqlite_storage_demo() -> None:
    print_header("SQLiteStorage")
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "proxies.db"
        storage = SQLiteStorage(db_path)
        await storage.initialize()

        proxies = [
            Proxy(
                url="http://proxy-db-1.local:9000",
                source=ProxySource.USER,
                health_status=HealthStatus.HEALTHY,
            ),
            Proxy(
                url="http://proxy-db-2.local:9000",
                source=ProxySource.FETCHED,
                health_status=HealthStatus.DEGRADED,
            ),
        ]

        await storage.save(proxies)
        all_proxies = await storage.load()
        healthy_only = await storage.query(health_status=HealthStatus.HEALTHY.value)

        print(f"Database '{db_path.name}' contains {len(all_proxies)} proxies")
        print("Healthy query result:", [p.url for p in healthy_only])

        await storage.close()


async def main_async() -> None:
    await json_storage_demo()
    await sqlite_storage_demo()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
