"""
Fetch & validate proxies using bundled assets (offline).

Demonstrates ProxyFetcher parsing text/CSV/HTML and validation.
Run with: uv run python examples/python/40_fetch_and_validate.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Iterable
from unittest.mock import patch

import httpx

CURRENT_DIR = Path(__file__).resolve().parent
EXAMPLES_DIR = CURRENT_DIR.parent
sys.path.append(str(EXAMPLES_DIR))

from _common import asset_path, print_header  # noqa: E402
from proxywhirl import Proxy, ProxySource  # noqa: E402
from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig, ProxyValidator  # noqa: E402
from proxywhirl.models import ProxyFormat, RenderMode, ValidationLevel  # noqa: E402


def _fake_get_factory() -> callable:
    """Return a fake AsyncClient.get that serves bundled assets."""
    html_text = asset_path("sample_proxies.html").read_text()
    csv_text = asset_path("sample_proxies.csv").read_text()
    txt_text = asset_path("sample_proxies.txt").read_text()

    url_map = {
        "https://example.com/proxies.html": html_text,
        "https://example.com/proxies.csv": csv_text,
        "https://example.com/proxies.txt": txt_text,
    }

    async def fake_get(self, url, *args, **kwargs):  # noqa: ANN001
        body = url_map.get(str(url))
        if body is None:
            return httpx.Response(404, request=httpx.Request("GET", url))
        return httpx.Response(200, text=body, request=httpx.Request("GET", url))

    return fake_get


async def main_async() -> None:
    print_header("Fetch & Validate (offline assets)")

    fetcher = ProxyFetcher(
        sources=[
            ProxySourceConfig(
                url="https://example.com/proxies.txt",
                format=ProxyFormat.PLAIN_TEXT,
                render_mode=RenderMode.STATIC,
            ),
            ProxySourceConfig(
                url="https://example.com/proxies.csv",
                format=ProxyFormat.CSV,
                render_mode=RenderMode.STATIC,
            ),
            ProxySourceConfig(
                url="https://example.com/proxies.html",
                format=ProxyFormat.HTML_TABLE,
                render_mode=RenderMode.STATIC,
            ),
        ],
        validator=ProxyValidator(level=ValidationLevel.BASIC, concurrency=4),
    )

    # Align ProxyFormat values with ProxyFetcher parser keys
    fetcher._parsers["plain_text"] = fetcher._parsers.get("text", fetcher._parsers.get("plain_text"))
    fetcher._parsers["html_table"] = fetcher._parsers.get("html", fetcher._parsers.get("html_table"))

    fake_get = _fake_get_factory()
    with patch.object(httpx.AsyncClient, "get", new=fake_get):
        raw_entries = await fetcher.fetch_all(validate=True)

    proxies = [Proxy(url=item["url"], source=ProxySource.FETCHED) for item in raw_entries]
    print(f"Fetched {len(raw_entries)} validated proxies")
    for proxy in proxies:
        print(f"• {proxy.url} (source={proxy.source.value})")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
