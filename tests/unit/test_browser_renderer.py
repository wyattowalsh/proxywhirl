"""Unit tests for BrowserRenderer."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestBrowserRendererInit:
    """Test BrowserRenderer initialization."""

    def test_browser_init_headless(self) -> None:
        """BrowserRenderer initializes with headless mode by default."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer()

        assert renderer.headless is True
        assert renderer.browser_type == "chromium"
        assert renderer.timeout == 30000
        assert renderer.wait_until == "load"
        assert renderer.user_agent is None
        assert renderer.viewport == {"width": 1280, "height": 720}
        assert renderer._is_started is False

    def test_browser_init_with_options(self) -> None:
        """BrowserRenderer accepts custom configuration."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(
            headless=False,
            browser_type="firefox",
            timeout=60000,
            wait_until="networkidle",
            user_agent="Custom UA",
            viewport={"width": 1920, "height": 1080},
        )

        assert renderer.headless is False
        assert renderer.browser_type == "firefox"
        assert renderer.timeout == 60000
        assert renderer.wait_until == "networkidle"
        assert renderer.user_agent == "Custom UA"
        assert renderer.viewport == {"width": 1920, "height": 1080}

    def test_browser_init_validates_browser_type(self) -> None:
        """BrowserRenderer validates browser type."""
        from proxywhirl.browser import BrowserRenderer

        # These should work
        BrowserRenderer(browser_type="chromium")
        BrowserRenderer(browser_type="firefox")
        BrowserRenderer(browser_type="webkit")


class TestBrowserRendererLifecycle:
    """Test browser lifecycle management."""

    async def test_browser_start_requires_playwright(self) -> None:
        """start() raises ImportError if playwright not installed."""
        from unittest.mock import patch

        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer()

        # Use builtins.__import__ to simulate ImportError when importing playwright
        original_import = (
            __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__
        )

        def mock_import(name, *args, **kwargs):
            if name == "playwright.async_api":
                raise ImportError("No module named 'playwright'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            with pytest.raises(ImportError, match="Playwright is required for browser rendering"):
                await renderer.start()

    async def test_browser_start_launches_browser(self) -> None:
        """start() launches browser and creates context."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(headless=True)

        # Mock playwright
        mock_playwright = MagicMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()

        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.stop = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        # Mock the async_playwright function - it returns a context manager
        # that has an async .start() method
        mock_playwright_cm = MagicMock()
        mock_playwright_cm.start = AsyncMock(return_value=mock_playwright)

        def mock_async_playwright():
            return mock_playwright_cm

        mock_module = MagicMock()
        mock_module.async_playwright = mock_async_playwright

        with patch.dict("sys.modules", {"playwright.async_api": mock_module}):
            await renderer.start()

            assert renderer._is_started is True
            assert renderer._playwright is not None
            assert renderer._browser is not None
            assert renderer._context is not None

            await renderer.close()

    async def test_browser_start_idempotent(self) -> None:
        """Calling start() multiple times is safe."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer()

        mock_playwright = MagicMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()

        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.stop = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        # Mock the async_playwright function - it returns a context manager
        # that has an async .start() method
        mock_playwright_cm = MagicMock()
        mock_playwright_cm.start = AsyncMock(return_value=mock_playwright)

        def mock_async_playwright():
            return mock_playwright_cm

        mock_module = MagicMock()
        mock_module.async_playwright = mock_async_playwright

        with patch.dict("sys.modules", {"playwright.async_api": mock_module}):
            await renderer.start()
            first_browser = renderer._browser

            await renderer.start()  # Second call
            second_browser = renderer._browser

            assert first_browser == second_browser  # Same instance

            await renderer.close()

    async def test_browser_close_cleans_up(self) -> None:
        """close() properly cleans up resources."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer()

        mock_playwright = MagicMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()

        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.stop = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()
        mock_context.close = AsyncMock()

        # Mock the async_playwright function - it returns a context manager
        # that has an async .start() method
        mock_playwright_cm = MagicMock()
        mock_playwright_cm.start = AsyncMock(return_value=mock_playwright)

        def mock_async_playwright():
            return mock_playwright_cm

        mock_module = MagicMock()
        mock_module.async_playwright = mock_async_playwright

        with patch.dict("sys.modules", {"playwright.async_api": mock_module}):
            await renderer.start()
            await renderer.close()

            assert renderer._is_started is False
            assert renderer._browser is None
            assert renderer._context is None
            assert renderer._playwright is None

            mock_context.close.assert_called_once()
            mock_browser.close.assert_called_once()
            mock_playwright.stop.assert_called_once()

    async def test_browser_close_idempotent(self) -> None:
        """Calling close() when not started is safe."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer()

        # Should not raise
        await renderer.close()
        await renderer.close()


class TestBrowserRendererRender:
    """Test page rendering."""

    async def test_render_requires_started_browser(self) -> None:
        """render() raises RuntimeError if browser not started."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer()

        with pytest.raises(RuntimeError, match="Browser not started"):
            await renderer.render("https://example.com")

    async def test_render_simple_page(self) -> None:
        """render() returns HTML content from page."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer()

        # Mock page
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Test content</html>")
        mock_page.close = AsyncMock()

        # Mock context
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        renderer._is_started = True
        renderer._context = mock_context

        html = await renderer.render("https://example.com")

        assert html == "<html>Test content</html>"
        mock_page.goto.assert_called_once_with(
            "https://example.com", timeout=30000, wait_until="load"
        )
        mock_page.content.assert_called_once()
        mock_page.close.assert_called_once()

    async def test_render_with_wait_strategy(self) -> None:
        """render() uses configured wait strategy."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(wait_until="networkidle", timeout=60000)

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Content</html>")
        mock_page.close = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        renderer._is_started = True
        renderer._context = mock_context

        await renderer.render("https://example.com")

        mock_page.goto.assert_called_once_with(
            "https://example.com", timeout=60000, wait_until="networkidle"
        )

    async def test_render_with_selector_wait(self) -> None:
        """render() can wait for specific selector."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer()

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Content</html>")
        mock_page.close = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        renderer._is_started = True
        renderer._context = mock_context

        await renderer.render("https://example.com", wait_for_selector=".proxy-list")

        mock_page.wait_for_selector.assert_called_once_with(".proxy-list", timeout=30000)

    async def test_render_timeout(self) -> None:
        """render() handles timeout errors."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(timeout=1000)

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=TimeoutError("Page load timeout"))
        mock_page.close = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        renderer._is_started = True
        renderer._context = mock_context

        with pytest.raises(TimeoutError):
            await renderer.render("https://slow-site.com")

        # Page should still be closed
        mock_page.close.assert_called_once()


class TestBrowserRendererContextManager:
    """Test context manager protocol."""

    async def test_context_manager_starts_and_stops(self) -> None:
        """Context manager automatically starts and stops browser."""
        from proxywhirl.browser import BrowserRenderer

        mock_playwright = MagicMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.stop = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()
        mock_context.close = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Test</html>")
        mock_page.close = AsyncMock()

        # Mock the async_playwright function - it returns a context manager
        # that has an async .start() method
        mock_playwright_cm = MagicMock()
        mock_playwright_cm.start = AsyncMock(return_value=mock_playwright)

        def mock_async_playwright():
            return mock_playwright_cm

        mock_module = MagicMock()
        mock_module.async_playwright = mock_async_playwright

        with patch.dict("sys.modules", {"playwright.async_api": mock_module}):
            async with BrowserRenderer() as renderer:
                assert renderer._is_started is True
                html = await renderer.render("https://example.com")
                assert html == "<html>Test</html>"

            # Should be closed after exiting context
            mock_context.close.assert_called_once()
            mock_browser.close.assert_called_once()
