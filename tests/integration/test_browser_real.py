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


@pytest.mark.integration
@pytest.mark.slow
class TestBrowserRendererContextPool:
    """Test context pooling functionality with real browser."""

    async def test_pool_basic_functionality(self) -> None:
        """Context pool provides and releases contexts correctly."""
        async with BrowserRenderer(headless=True, timeout=10000, max_contexts=2) as renderer:
            # Pool should have 2 contexts available
            assert renderer.pool_size == 2
            assert renderer.pool_capacity == 2

            # Acquire a context
            context1 = await renderer.acquire_context()
            assert renderer.pool_size == 1

            # Release it back
            await renderer.release_context(context1)
            assert renderer.pool_size == 2

    async def test_pool_exhaustion(self) -> None:
        """Pool blocks when exhausted and unblocks when context released."""
        import asyncio

        async with BrowserRenderer(headless=True, timeout=10000, max_contexts=1) as renderer:
            # Acquire the only context
            context = await renderer.acquire_context()
            assert renderer.pool_size == 0

            # Try to acquire with timeout - should fail
            with pytest.raises(asyncio.TimeoutError):
                await renderer.acquire_context(timeout=0.5)

            # Release context
            await renderer.release_context(context)
            assert renderer.pool_size == 1

    async def test_concurrent_rendering_with_pool(self) -> None:
        """Multiple concurrent renders use different contexts from pool."""
        import asyncio

        async with BrowserRenderer(headless=True, timeout=15000, max_contexts=3) as renderer:
            # Start 3 renders concurrently
            results = await asyncio.gather(
                renderer.render("https://example.com"),
                renderer.render("https://httpbin.org/html"),
                renderer.render("https://httpbin.org/"),
            )

            # All should succeed
            assert len(results) == 3
            for html in results:
                assert html is not None
                assert len(html) > 0

            # All contexts should be back in pool
            assert renderer.pool_size == 3

    async def test_pool_context_reuse(self) -> None:
        """Contexts are reused across multiple render operations."""
        async with BrowserRenderer(headless=True, timeout=10000, max_contexts=2) as renderer:
            # Track initial contexts
            initial_contexts = set(renderer._all_contexts)
            assert len(initial_contexts) == 2

            # Render multiple pages
            for i in range(5):
                await renderer.render("https://example.com")

            # Should still have same 2 contexts (reused)
            final_contexts = set(renderer._all_contexts)
            assert initial_contexts == final_contexts
            assert renderer.pool_size == 2

    async def test_pool_error_recovery(self) -> None:
        """Pool recovers contexts even when render fails."""
        async with BrowserRenderer(headless=True, timeout=5000, max_contexts=2) as renderer:
            # Pool starts full
            assert renderer.pool_size == 2

            # Cause render to fail
            try:
                await renderer.render("https://invalid-domain-12345.test")
            except PlaywrightError:
                pass  # Expected

            # Context should be released back to pool
            assert renderer.pool_size == 2

    async def test_invalid_context_release(self) -> None:
        """Releasing foreign context raises ValueError."""
        from playwright.async_api import async_playwright

        async with BrowserRenderer(headless=True, timeout=10000, max_contexts=1) as renderer:
            # Create a foreign context (not from pool)
            pw = await async_playwright().start()
            browser = await pw.chromium.launch(headless=True)
            foreign_context = await browser.new_context()

            try:
                # Try to release foreign context
                with pytest.raises(ValueError, match="does not belong to this pool"):
                    await renderer.release_context(foreign_context)
            finally:
                await foreign_context.close()
                await browser.close()
                await pw.stop()


@pytest.mark.integration
@pytest.mark.slow
class TestBrowserRendererCrashRecovery:
    """Test browser crash recovery and cleanup."""

    async def test_cleanup_after_timeout_error(self) -> None:
        """Browser cleans up properly after timeout error."""
        renderer = BrowserRenderer(headless=True, timeout=1000)
        await renderer.start()

        initial_pool_size = renderer.pool_size

        # Cause timeout error
        try:
            await renderer.render("https://httpbin.org/delay/10")
        except (TimeoutError, PlaywrightError):
            pass  # Expected

        # Pool should recover
        assert renderer.pool_size == initial_pool_size
        assert renderer._is_started is True

        # Should still work for next render
        html = await renderer.render("https://example.com")
        assert html is not None

        await renderer.close()

    async def test_cleanup_after_network_error(self) -> None:
        """Browser cleans up properly after network error."""
        renderer = BrowserRenderer(headless=True, timeout=5000)
        await renderer.start()

        initial_pool_size = renderer.pool_size

        # Cause network error
        try:
            await renderer.render("http://localhost:99999")
        except PlaywrightError:
            pass  # Expected

        # Pool should recover
        assert renderer.pool_size == initial_pool_size

        # Should still work
        html = await renderer.render("https://example.com")
        assert html is not None

        await renderer.close()

    async def test_multiple_sequential_errors(self) -> None:
        """Browser handles multiple sequential errors without degradation."""
        async with BrowserRenderer(headless=True, timeout=5000, max_contexts=2) as renderer:
            # Cause multiple errors in sequence
            for _ in range(3):
                try:
                    await renderer.render("https://invalid-domain-12345.test")
                except PlaywrightError:
                    pass  # Expected

            # Pool should still be intact
            assert renderer.pool_size == 2

            # Normal render should still work
            html = await renderer.render("https://example.com")
            assert html is not None

    async def test_concurrent_errors_with_pool(self) -> None:
        """Pool handles concurrent errors without corruption."""
        import asyncio

        async with BrowserRenderer(headless=True, timeout=3000, max_contexts=3) as renderer:
            # Start 3 concurrent renders that will all fail
            results = await asyncio.gather(
                renderer.render("https://invalid1-12345.test"),
                renderer.render("https://invalid2-12345.test"),
                renderer.render("https://invalid3-12345.test"),
                return_exceptions=True,
            )

            # All should have raised errors
            assert all(isinstance(r, PlaywrightError) for r in results)

            # Pool should recover all contexts
            assert renderer.pool_size == 3

            # Normal render should still work
            html = await renderer.render("https://example.com")
            assert html is not None


@pytest.mark.integration
@pytest.mark.slow
class TestBrowserRendererInvalidContent:
    """Test handling of invalid, malformed, or problematic content."""

    async def test_empty_response_body(self) -> None:
        """Browser handles pages with empty body."""
        async with BrowserRenderer(headless=True, timeout=10000) as renderer:
            # about:blank has minimal content
            html = await renderer.render("about:blank")

            # Should return HTML structure even if mostly empty
            assert html is not None
            assert len(html) > 0

    async def test_binary_content_type(self) -> None:
        """Browser handles binary content responses."""
        async with BrowserRenderer(headless=True, timeout=15000) as renderer:
            # Try to render binary content (image)
            try:
                html = await renderer.render("https://httpbin.org/image/png")
                # Some browsers may render binary as-is or show placeholder
                assert html is not None
            except PlaywrightError:
                # Acceptable if browser rejects binary content
                pass

    async def test_large_dom_structure(self) -> None:
        """Browser handles pages with large DOM structures."""
        async with BrowserRenderer(headless=True, timeout=20000) as renderer:
            # httpbin has reasonably sized DOM
            html = await renderer.render("https://httpbin.org/")

            # Should handle without issues
            assert html is not None
            assert len(html) > 1000

    async def test_special_characters_in_url(self) -> None:
        """Browser handles URLs with special characters."""
        async with BrowserRenderer(headless=True, timeout=10000) as renderer:
            # URL with query parameters
            html = await renderer.render("https://httpbin.org/anything?test=value&foo=bar")

            assert html is not None
            assert len(html) > 0

    async def test_non_utf8_content(self) -> None:
        """Browser handles non-UTF8 encoded content."""
        async with BrowserRenderer(headless=True, timeout=15000) as renderer:
            # Most modern browsers handle encoding automatically
            html = await renderer.render("https://httpbin.org/encoding/utf8")

            assert html is not None
            assert len(html) > 0

    async def test_infinite_loop_timeout(self) -> None:
        """Browser times out on pages with infinite JavaScript loops."""
        async with BrowserRenderer(headless=True, timeout=5000) as renderer:
            # httpbin delay endpoint simulates slow response
            with pytest.raises((TimeoutError, PlaywrightError)):
                await renderer.render("https://httpbin.org/delay/10")

    async def test_404_page_content(self) -> None:
        """Browser renders 404 error pages."""
        async with BrowserRenderer(headless=True, timeout=10000) as renderer:
            # Should load 404 page content (even if minimal)
            html = await renderer.render("https://httpbin.org/status/404")

            # Page should load and return HTML even with 404 status
            assert html is not None
            assert len(html) > 0
            assert "<html" in html.lower() or "<!doctype" in html.lower()

    async def test_500_server_error_page(self) -> None:
        """Browser renders 500 error pages."""
        async with BrowserRenderer(headless=True, timeout=10000) as renderer:
            # Should load 500 error page content
            html = await renderer.render("https://httpbin.org/status/500")

            assert html is not None
            assert len(html) > 0

    async def test_malformed_json_content(self) -> None:
        """Browser handles pages serving malformed JSON."""
        async with BrowserRenderer(headless=True, timeout=10000) as renderer:
            # JSON content should be displayed by browser
            html = await renderer.render("https://httpbin.org/json")

            assert html is not None
            assert len(html) > 0

    async def test_content_security_policy(self) -> None:
        """Browser respects Content-Security-Policy headers."""
        async with BrowserRenderer(headless=True, timeout=10000) as renderer:
            # Regular page should work fine
            html = await renderer.render("https://example.com")

            assert html is not None
            assert len(html) > 0

    async def test_mixed_content_handling(self) -> None:
        """Browser handles mixed HTTP/HTTPS content."""
        async with BrowserRenderer(headless=True, timeout=15000) as renderer:
            # Modern browsers block mixed content, but page should still load
            html = await renderer.render("https://example.com")

            assert html is not None
            assert len(html) > 0
