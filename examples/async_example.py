#!/usr/bin/env python3
"""Minimal asynchronous ProxyWhirl example."""

import asyncio

from proxywhirl import AsyncProxyWhirl, Proxy


async def main() -> None:
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy(Proxy(url="http://127.0.0.1:8080"))
        print(f"Pool size: {rotator.pool.size}")
        print("Add working proxies to the pool before issuing real requests.")


if __name__ == "__main__":
    asyncio.run(main())