"""
Example: Browser Rendering for JavaScript-Heavy Proxy Sites

This example demonstrates how to use ProxyWhirl's BrowserRenderer
to fetch proxies from JavaScript-heavy websites that require a browser
to properly render the content.

Installation:
    pip install 'proxywhirl[js]'
    # or
    pip install playwright
    playwright install chromium
"""

import asyncio

from proxywhirl.browser import BrowserRenderer
from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig
from proxywhirl.models import RenderMode


async def example_basic_browser_rendering():
    """Basic browser rendering example."""
    print("\n=== Example 1: Basic Browser Rendering ===")

    # Create browser renderer with default settings
    async with BrowserRenderer() as renderer:
        # Render a JavaScript-heavy page
        html = await renderer.render("https://example.com/proxies")
        print(f"Rendered {len(html)} bytes of HTML")


async def example_custom_browser_config():
    """Browser rendering with custom configuration."""
    print("\n=== Example 2: Custom Browser Configuration ===")

    # Configure browser settings directly in BrowserRenderer constructor
    async with BrowserRenderer(
        headless=True,  # Run in background (no UI)
        browser_type="chromium",  # or "firefox", "webkit"
        timeout=30000,  # Maximum wait time in milliseconds (30 seconds)
        wait_until="networkidle",  # Wait for network to be idle
    ) as renderer:
        html = await renderer.render("https://example.com/proxies")
        print(f"Rendered with custom config: {len(html)} bytes")


async def example_browser_with_proxy_fetcher():
    """Using BrowserRenderer with ProxyFetcher."""
    print("\n=== Example 3: Browser Rendering with ProxyFetcher ===")

    fetcher = ProxyFetcher()

    # Configure source with browser rendering
    source = ProxySourceConfig(
        url="https://example.com/proxies",
        format="json",
        render_mode=RenderMode.BROWSER,  # Enable browser rendering
    )

    try:
        # Fetch proxies (will automatically use browser rendering)
        proxies = await fetcher.fetch_from_source(source)
        print(f"Fetched {len(proxies)} proxies using browser rendering")

        # Display first proxy
        if proxies:
            print(f"First proxy: {proxies[0]}")
    except Exception as e:
        print(f"Error: {e}")


async def example_mixed_rendering_modes():
    """Mixing static and browser rendering in a single fetcher."""
    print("\n=== Example 4: Mixed Rendering Modes ===")

    fetcher = ProxyFetcher()

    # Define multiple sources with different render modes
    sources = [
        ProxySourceConfig(
            url="https://static-site.com/proxies.json",
            format="json",
            render_mode=RenderMode.STATIC,  # Standard HTTP client
        ),
        ProxySourceConfig(
            url="https://js-heavy-site.com/proxies",
            format="json",
            render_mode=RenderMode.BROWSER,  # Browser rendering
        ),
    ]

    try:
        # Fetch from all sources (ProxyFetcher handles render modes automatically)
        all_proxies = await fetcher.fetch_all(sources)
        print(f"Fetched {len(all_proxies)} total proxies from {len(sources)} sources")

        for i, proxies in enumerate(all_proxies, 1):
            mode = sources[i - 1].render_mode
            print(f"  Source {i} ({mode.value}): {len(proxies)} proxies")
    except Exception as e:
        print(f"Error: {e}")


async def example_error_handling():
    """Handling browser-related errors."""
    print("\n=== Example 5: Error Handling ===")

    fetcher = ProxyFetcher()

    source = ProxySourceConfig(
        url="https://example.com/proxies",
        format="json",
        render_mode=RenderMode.BROWSER,
    )

    try:
        proxies = await fetcher.fetch_from_source(source)
        print(f"Success: {len(proxies)} proxies")
    except ImportError as e:
        # Playwright not installed
        print(f"ImportError: {e}")
        print("Install with: pip install 'proxywhirl[js]'")
    except TimeoutError as e:
        # Browser timeout
        print(f"TimeoutError: {e}")
        print("Consider increasing timeout parameter in BrowserRenderer constructor")
    except RuntimeError as e:
        # Browser crashed
        print(f"RuntimeError: {e}")
        print("Browser may have crashed - check logs")
    except Exception as e:
        # Other errors
        print(f"Unexpected error: {e}")


async def example_performance_tips():
    """Performance optimization tips."""
    print("\n=== Example 6: Performance Tips ===")

    # Tip 1: Reuse BrowserRenderer across multiple renders
    async with BrowserRenderer(
        headless=True,
        timeout=15000,  # Shorter timeout (15 seconds) for faster failure
        wait_until="domcontentloaded",  # Don't wait for all resources
    ) as renderer:
        # Multiple renders reuse the same browser instance
        urls = [
            "https://site1.com/proxies",
            "https://site2.com/proxies",
            "https://site3.com/proxies",
        ]

        for url in urls:
            try:
                html = await renderer.render(url)
                print(f"Rendered {url}: {len(html)} bytes")
            except Exception as e:
                print(f"Failed {url}: {e}")

    # Tip 2: Use STATIC mode for sites that don't need JavaScript
    # (much faster than browser rendering)
    print("\nTip: Use STATIC mode for non-JS sites (10x+ faster)")


async def main():
    """Run all examples."""
    print("ProxyWhirl Browser Rendering Examples")
    print("=" * 50)

    # Note: Most examples will fail without a real proxy source
    # These are demonstration purposes showing the API usage

    await example_basic_browser_rendering()
    await example_custom_browser_config()
    await example_browser_with_proxy_fetcher()
    await example_mixed_rendering_modes()
    await example_error_handling()
    await example_performance_tips()

    print("\n" + "=" * 50)
    print("Examples complete!")
    print("\nNote: These examples use placeholder URLs.")
    print("Replace with real proxy sources for production use.")


if __name__ == "__main__":
    asyncio.run(main())
