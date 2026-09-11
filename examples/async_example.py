#!/usr/bin/env python3
"""Minimal asynchronous ProxyWhirl example.

Bootstrap note
--------------
``AsyncProxyWhirl()`` enables *lazy* auto-bootstrap from built-in ``ALL_SOURCES``
when the pool is empty and you issue a real request.

This demo uses ``bootstrap=False`` and a placeholder proxy so it runs offline.
For the auto-fetch path::

    async with AsyncProxyWhirl() as rotator:
        response = await rotator.get("https://api.example.com/data")
"""

import asyncio

from proxywhirl import AsyncProxyWhirl, Proxy


async def main() -> None:
    # Offline manual-pool demo — no network fetch of public sources.
    async with AsyncProxyWhirl(bootstrap=False) as rotator:
        await rotator.add_proxy(Proxy(url="http://127.0.0.1:8080"))
        print(f"Pool size: {rotator.pool.size}")
        print("Add working proxies to the pool before issuing real requests.")


if __name__ == "__main__":
    asyncio.run(main())
