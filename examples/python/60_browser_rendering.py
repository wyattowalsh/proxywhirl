"""
Browser rendering examples for JavaScript-heavy proxy sources.

These samples are defensive: they check for Playwright, use reachable URLs,
and keep output concise. Install extras first:

    uv pip install "proxywhirl[js]"
    playwright install chromium

Run with:
    uv run python examples/python/60_browser_rendering.py
"""

from __future__ import annotations

import asyncio

from proxywhirl.fetchers import ProxyFetcher
from proxywhirl.models import ProxyFormat, ProxySourceConfig, RenderMode

BrowserTools = tuple[type]  # BrowserRenderer only


def load_browser_tools() -> BrowserTools | None:
    """Lazy-import browser dependencies so the script degrades gracefully."""
    try:
        from proxywhirl.browser import BrowserRenderer
    except ImportError:
        print("Playwright is not installed. Install with `uv pip install \"proxywhirl[js]\"`.")
        print("Then run `playwright install chromium` once to download a browser.")
        return None
    return (BrowserRenderer,)


async def basic_render(browser_renderer: type) -> None:
    print("\n=== Example 1: Basic browser render ===")
    async with browser_renderer() as renderer:
        html = await renderer.render("https://httpbin.org/html")
        print(f"Fetched {len(html)} bytes of HTML")


async def custom_config_example(
    browser_renderer: type,
) -> None:
    print("\n=== Example 2: Custom browser configuration ===")
    async with browser_renderer(
        headless=True,
        browser_type="chromium",
        timeout=20000,  # milliseconds
        wait_until="networkidle",
    ) as renderer:
        html = await renderer.render("https://httpbin.org/delay/1")
        print(f"Rendered with custom config, length={len(html)} bytes")


async def fetcher_with_browser(
    browser_renderer: type,
) -> None:
    print("\n=== Example 3: ProxyFetcher + browser render ===")
    fetcher = ProxyFetcher()
    fetcher._parsers["html_table"] = fetcher._parsers.get("html", fetcher._parsers.get("html_table"))
    source = ProxySourceConfig(
        url="https://httpbin.org/html",
        format=ProxyFormat.HTML_TABLE,
        render_mode=RenderMode.BROWSER,
    )
    try:
        proxies = await fetcher.fetch_from_source(source)
        print(f"Fetched {len(proxies)} proxy entries using browser mode")
    except Exception as exc:  # noqa: BLE001
        print(f"Fetch failed (expected if the page has no table data): {exc}")
        print("Swap the URL with a real JS-heavy proxy catalog in production.")


async def mixed_rendering_example(
    browser_renderer: type,
) -> None:
    print("\n=== Example 4: Mixing static and browser sources ===")
    sources = [
        ProxySourceConfig(
            url="https://example.com/proxies.json",
            format=ProxyFormat.JSON,
            render_mode=RenderMode.STATIC,
        ),
        ProxySourceConfig(
            url="https://example.com/js-proxies",
            format=ProxyFormat.HTML_TABLE,
            render_mode=RenderMode.BROWSER,
        ),
    ]
    for idx, source in enumerate(sources, start=1):
        print(f"Source {idx}: {source.url} ({source.render_mode.value})")
    print("ProxyFetcher will open the browser only for the JS-heavy source.")


async def run_examples(tools: BrowserTools) -> None:
    (browser_renderer,) = tools
    for example in (
        basic_render,
        custom_config_example,
        fetcher_with_browser,
        mixed_rendering_example,
    ):
        try:
            await example(browser_renderer)
        except Exception as exc:  # noqa: BLE001
            print(f"Example {example.__name__} skipped due to error: {exc}")


def main() -> None:
    tools = load_browser_tools()
    if not tools:
        return
    asyncio.run(run_examples(tools))


if __name__ == "__main__":
    main()
