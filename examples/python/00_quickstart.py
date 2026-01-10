"""
Quickstart: create a proxy pool, rotate through it, and make a mocked request.

Everything runs offline via httpx.MockTransport.
Run with: uv run python examples/python/00_quickstart.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

import httpx
from unittest.mock import patch

CURRENT_DIR = Path(__file__).resolve().parent
EXAMPLES_DIR = CURRENT_DIR.parent
sys.path.append(str(EXAMPLES_DIR))

from _common import demo_pool, print_header  # noqa: E402
from proxywhirl import ProxyRotator  # noqa: E402


def main() -> None:
    print_header("ProxyWhirl Quickstart")

    pool = demo_pool(name="quickstart")
    rotator = ProxyRotator(proxies=[p.model_copy(deep=True) for p in pool.get_all_proxies()])

    # Track selections so the mock handler can echo which proxy was used.
    selection_order: List[str] = []
    original_select = rotator.strategy.select

    def select_with_tracking(pool, context=None):
        proxy = original_select(pool, context=context)
        selection_order.append(proxy.url)
        return proxy

    rotator.strategy.select = select_with_tracking  # type: ignore[attr-defined]

    def handler(request: httpx.Request) -> httpx.Response:
        current_proxy = selection_order[-1] if selection_order else "unknown"
        payload = {
            "requested_url": str(request.url),
            "proxy_used": current_proxy,
        }
        return httpx.Response(200, json=payload, request=request)

    _original_client = httpx.Client

    def client_factory(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return _original_client(*args, **kwargs)

    with patch("httpx.Client", client_factory):
        response = rotator.get("https://httpbin.org/ip").json()

    rotator.strategy.select = original_select

    print("Rotation order:", " -> ".join(selection_order))
    print("Sample response:", response)
    print("Pool stats:", rotator.get_pool_stats())


if __name__ == "__main__":
    main()
