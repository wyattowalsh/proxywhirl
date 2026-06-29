#!/usr/bin/env python3
"""Minimal synchronous ProxyWhirl example."""

from proxywhirl import Proxy, ProxyWhirl


def main() -> None:
    rotator = ProxyWhirl()
    rotator.add_proxy(Proxy(url="http://127.0.0.1:8080"))
    print(f"Pool size: {rotator.pool.size}")
    print("Add working proxies to the pool before issuing real requests.")


if __name__ == "__main__":
    main()