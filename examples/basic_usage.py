#!/usr/bin/env python3
"""Minimal synchronous ProxyWhirl example.

Bootstrap note
--------------
``ProxyWhirl()`` enables *lazy* auto-bootstrap from built-in ``ALL_SOURCES`` when
the pool is empty and you issue a real request (``.get`` / ``.get_proxy``).

This demo uses ``bootstrap=False`` and a placeholder proxy so it runs offline
without hitting public sources. For the auto-fetch path::

    rotator = ProxyWhirl()  # default bootstrap
    response = rotator.get("https://api.example.com/data")
"""

from proxywhirl import Proxy, ProxyWhirl


def main() -> None:
    # Offline manual-pool demo — no network fetch of public sources.
    rotator = ProxyWhirl(bootstrap=False)
    rotator.add_proxy(Proxy(url="http://127.0.0.1:8080"))
    print(f"Pool size: {rotator.pool.size}")
    print("Add working proxies to the pool before issuing real requests.")


if __name__ == "__main__":
    main()
