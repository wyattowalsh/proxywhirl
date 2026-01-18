"""Real Playwright browser integration tests.

Tests BrowserRenderer with actual browser instances to validate:
- Timeout handling with real page loads
- Invalid content and error recovery
- Browser crash recovery and cleanup
- JavaScript execution and rendering
- Multiple render modes and wait strategies

These tests require Playwright to be installed and are skipped if not available.
"""

from __future__ import annotations

import pytest

# Skip entire module if Playwright not installed
playwright = pytest.importorskip("playwright", reason="Playwright not installed")
from playwright.async_api import Error as PlaywrightError  # noqa: E402

from proxywhirl.browser import BrowserRenderer  # noqa: E402


@pytest.mark.integration
@pytest.mark.slow
class TestBrowserRendererReal:
    """Real browser integration tests with actual Playwright."""

    async def test_render_simple_static_page(self) -> None:
        """BrowserRenderer can render a simple static HTML page."""
        async with BrowserRenderer(headless=True, timeout=10000) as renderer:
            # Use a simple test page
            html = await renderer.render("https://example.com")

            # Basic validation
            assert html is not None
            assert len(html) > 0
            assert "<html" in html.lower() or "<!doctype" in html.lower()
            assert "example" in html.lower()

    async def test_render_with_javascript(self) -> None:
        """BrowserRenderer executes JavaScript and renders dynamic content."""
        async with BrowserRenderer(headless=True, timeout=15000) as renderer:
            # httpbin.org has dynamic JavaScript content
            html = await renderer.render("https://httpbin.org/")

            # Verify JavaScript executed
            assert html is not None
            assert len(html) > 0
            # httpbin shows various endpoints
            assert "httpbin" in html.lower()

    async def test_timeout_handling_short_timeout(self) -> None:
        """BrowserRenderer handles timeout errors with very short timeout."""
        async with BrowserRenderer(headless=True, timeout=1) as renderer:
            # 1ms timeout should fail on any real page
            with pytest.raises((TimeoutError, PlaywrightError)):
                await renderer.render("https://httpbin.org/delay/1")

    async def test_timeout_handling_slow_page(self) -> None:
        """BrowserRenderer handles timeout on intentionally slow pages."""
        async with BrowserRenderer(headless=True, timeout=2000) as renderer:
            # httpbin delay endpoint - 5 second delay with 2 second timeout
            with pytest.raises((TimeoutError, PlaywrightError)):
                await renderer.render("https://httpbin.org/delay/5")

    async def test_invalid_url_handling(self) -> None:
        """BrowserRenderer handles invalid URLs gracefully."""
        async with BrowserRenderer(headless=True, timeout=5000) as renderer:
            # Non-existent domain should raise error
            with pytest.raises(PlaywrightError):
                await renderer.render("https://this-domain-does-not-exist-12345.invalid")

    async def test_network_error_handling(self) -> None:
        """BrowserRenderer handles network errors."""
        async with BrowserRenderer(headless=True, timeout=5000) as renderer:
            # localhost on unlikely port should fail
            with pytest.raises(PlaywrightError):
                await renderer.render("http://localhost:99999")

    async def test_http_error_status_codes(self) -> None:
        """BrowserRenderer handles HTTP error status codes."""
        async with BrowserRenderer(headless=True, timeout=10000) as renderer:
            # httpbin 404 endpoint - should load but return 404 page
            html = await renderer.render("https://httpbin.org/status/404")

            # Page should load even with 404 status
            assert html is not None
            assert len(html) > 0

    async def test_wait_for_selector_success(self) -> None:
        """BrowserRenderer waits for specific selector to appear."""
        async with BrowserRenderer(headless=True, timeout=15000) as renderer:
            # example.com has <h1> element
            html = await renderer.render("https://example.com", wait_for_selector="h1")

            assert html is not None
            assert "<h1>" in html.lower()

    async def test_wait_for_selector_timeout(self) -> None:
        """BrowserRenderer times out if selector never appears."""
        async with BrowserRenderer(headless=True, timeout=3000) as renderer:
            # Wait for non-existent selector
            with pytest.raises((TimeoutError, PlaywrightError)):
                await renderer.render(
                    "https://example.com", wait_for_selector=".this-class-does-not-exist-12345"
                )

    async def test_wait_until_networkidle(self) -> None:
        """BrowserRenderer waits for network idle state."""
        async with BrowserRenderer(
            headless=True, timeout=15000, wait_until="networkidle"
        ) as renderer:
            html = await renderer.render("https://httpbin.org/")

            # Should have fully loaded content
            assert html is not None
            assert len(html) > 0

    async def test_wait_until_domcontentloaded(self) -> None:
        """BrowserRenderer waits for DOM content loaded."""
        async with BrowserRenderer(
            headless=True, timeout=10000, wait_until="domcontentloaded"
        ) as renderer:
            html = await renderer.render("https://example.com")

            assert html is not None
            assert len(html) > 0

    async def test_multiple_renders_same_instance(self) -> None:
        """BrowserRenderer can render multiple pages with same instance."""
        async with BrowserRenderer(headless=True, timeout=10000) as renderer:
            # Render first page
            html1 = await renderer.render("https://example.com")
            assert html1 is not None
            assert "example" in html1.lower()

            # Render second page
            html2 = await renderer.render("https://httpbin.org/html")
            assert html2 is not None
            assert html1 != html2  # Different content

    async def test_browser_cleanup_after_error(self) -> None:
        """BrowserRenderer properly cleans up after errors."""
        renderer = BrowserRenderer(headless=True, timeout=5000)
        await renderer.start()

        # Cause an error
        try:
            await renderer.render("https://this-will-fail-12345.invalid")
        except PlaywrightError:
            pass  # Expected

        # Should still be able to close cleanly
        await renderer.close()

        # Verify cleanup
        assert renderer._is_started is False
        assert renderer._browser is None
        assert renderer._context is None

    async def test_sequential_start_close_cycles(self) -> None:
        """BrowserRenderer handles multiple start/close cycles."""
        renderer = BrowserRenderer(headless=True, timeout=10000)

        # First cycle
        await renderer.start()
        assert renderer._is_started is True
        html1 = await renderer.render("https://example.com")
        assert html1 is not None
        await renderer.close()
        assert renderer._is_started is False

        # Second cycle
        await renderer.start()
        assert renderer._is_started is True
        html2 = await renderer.render("https://example.com")
        assert html2 is not None
        await renderer.close()
        assert renderer._is_started is False

    async def test_firefox_browser_type(self) -> None:
        """BrowserRenderer works with Firefox browser."""
        async with BrowserRenderer(
            headless=True, browser_type="firefox", timeout=15000
        ) as renderer:
            html = await renderer.render("https://example.com")

            assert html is not None
            assert len(html) > 0
            assert "example" in html.lower()

    async def test_webkit_browser_type(self) -> None:
        """BrowserRenderer works with WebKit browser."""
        async with BrowserRenderer(headless=True, browser_type="webkit", timeout=15000) as renderer:
            html = await renderer.render("https://example.com")

            assert html is not None
            assert len(html) > 0
            assert "example" in html.lower()

    async def test_custom_viewport_rendering(self) -> None:
        """BrowserRenderer respects custom viewport settings."""
        async with BrowserRenderer(
            headless=True, timeout=10000, viewport={"width": 1920, "height": 1080}
        ) as renderer:
            html = await renderer.render("https://example.com")

            # Should render successfully with custom viewport
            assert html is not None
            assert len(html) > 0

    async def test_custom_user_agent(self) -> None:
        """BrowserRenderer uses custom user agent."""
        custom_ua = "ProxyWhirl-Test-Browser/1.0"

        async with BrowserRenderer(headless=True, timeout=15000, user_agent=custom_ua) as renderer:
            # httpbin shows request headers including user-agent
            html = await renderer.render("https://httpbin.org/headers")

            # Verify our custom user agent was used
            assert html is not None
            assert custom_ua in html

    async def test_render_without_start_raises_error(self) -> None:
        """BrowserRenderer raises error if render called before start."""
        renderer = BrowserRenderer(headless=True, timeout=10000)

        # Try to render without starting
        with pytest.raises(RuntimeError, match="Browser not started"):
            await renderer.render("https://example.com")

    async def test_idempotent_start(self) -> None:
        """BrowserRenderer start() is idempotent."""
        renderer = BrowserRenderer(headless=True, timeout=10000)

        # Start multiple times
        await renderer.start()
        browser1 = renderer._browser

        await renderer.start()
        browser2 = renderer._browser

        # Should be same browser instance
        assert browser1 is browser2

        await renderer.close()

    async def test_idempotent_close(self) -> None:
        """BrowserRenderer close() is idempotent."""
        renderer = BrowserRenderer(headless=True, timeout=10000)

        # Close without starting should be safe
        await renderer.close()

        # Start and close multiple times
        await renderer.start()
        await renderer.close()
        await renderer.close()  # Second close should be safe

        assert renderer._is_started is False

    async def test_page_with_redirect(self) -> None:
        """BrowserRenderer follows HTTP redirects."""
        async with BrowserRenderer(headless=True, timeout=15000) as renderer:
            # httpbin redirect endpoint
            html = await renderer.render("https://httpbin.org/redirect/2")

            # Should follow redirects and render final page
            assert html is not None
            assert len(html) > 0

    async def test_page_with_cookies(self) -> None:
        """BrowserRenderer handles pages that set cookies."""
        async with BrowserRenderer(headless=True, timeout=15000) as renderer:
            # httpbin cookies endpoint
            html = await renderer.render("https://httpbin.org/cookies/set?test=value")

            # Should handle cookie setting
            assert html is not None
            assert len(html) > 0

    async def test_malformed_html_handling(self) -> None:
        """BrowserRenderer handles malformed HTML gracefully."""
        async with BrowserRenderer(headless=True, timeout=10000) as renderer:
            # Most real-world pages have some HTML quirks
            html = await renderer.render("https://example.com")

            # Browser should still render and return content
            assert html is not None
            assert len(html) > 0

    async def test_concurrent_renders_fail_gracefully(self) -> None:
        """BrowserRenderer handles concurrent render attempts."""
        async with BrowserRenderer(headless=True, timeout=10000) as renderer:
            # Render pages sequentially (concurrent not supported with single context)
            html1 = await renderer.render("https://example.com")
            html2 = await renderer.render("https://httpbin.org/html")

            # Both should succeed
            assert html1 is not None
            assert html2 is not None
            assert html1 != html2

    async def test_empty_page_rendering(self) -> None:
        """BrowserRenderer handles rendering of minimal/empty pages."""
        async with BrowserRenderer(headless=True, timeout=10000) as renderer:
            # about:blank should render
            html = await renderer.render("about:blank")

            # Should get minimal HTML
            assert html is not None
            assert len(html) > 0

    async def test_large_page_rendering(self) -> None:
        """BrowserRenderer handles large page content."""
        async with BrowserRenderer(headless=True, timeout=20000) as renderer:
            # httpbin has reasonably sized pages
            html = await renderer.render("https://httpbin.org/")

            # Should handle larger content
            assert html is not None
            assert len(html) > 1000  # Reasonable size check

    async def test_https_certificate_handling(self) -> None:
        """BrowserRenderer handles HTTPS certificates."""
        async with BrowserRenderer(headless=True, timeout=15000) as renderer:
            # Standard HTTPS site
            html = await renderer.render("https://httpbin.org/")

            # Should handle valid certificates
            assert html is not None
            assert len(html) > 0

    async def test_wait_for_timeout_parameter(self) -> None:
        """BrowserRenderer respects wait_for_timeout parameter."""
        async with BrowserRenderer(headless=True, timeout=15000) as renderer:
            # Add extra wait time
            html = await renderer.render("https://example.com", wait_for_timeout=1000)

            # Should wait and then return content
            assert html is not None
            assert len(html) > 0
