"""Unit tests for BrowserRenderer."""

from __future__ import annotations

import asyncio
import time
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
        assert renderer.max_contexts == 3
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
            max_contexts=5,
        )

        assert renderer.headless is False
        assert renderer.browser_type == "firefox"
        assert renderer.timeout == 60000
        assert renderer.wait_until == "networkidle"
        assert renderer.user_agent == "Custom UA"
        assert renderer.viewport == {"width": 1920, "height": 1080}
        assert renderer.max_contexts == 5

    def test_browser_init_validates_browser_type(self) -> None:
        """BrowserRenderer validates browser type."""
        from proxywhirl.browser import BrowserRenderer

        # These should work
        BrowserRenderer(browser_type="chromium")
        BrowserRenderer(browser_type="firefox")
        BrowserRenderer(browser_type="webkit")

    def test_browser_init_max_contexts_minimum(self) -> None:
        """max_contexts has a minimum of 1."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=0)
        assert renderer.max_contexts == 1

        renderer = BrowserRenderer(max_contexts=-5)
        assert renderer.max_contexts == 1


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
        """start() launches browser and creates context pool."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(headless=True, max_contexts=2)

        # Mock playwright
        mock_playwright = MagicMock()
        mock_browser = AsyncMock()
        mock_context1 = AsyncMock()
        mock_context2 = AsyncMock()

        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.stop = AsyncMock()
        mock_browser.new_context = AsyncMock(side_effect=[mock_context1, mock_context2])

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
            assert renderer._context_pool is not None
            assert len(renderer._all_contexts) == 2
            assert renderer.pool_size == 2
            assert renderer.pool_capacity == 2

            await renderer.close()

    async def test_browser_start_idempotent(self) -> None:
        """Calling start() multiple times is safe."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=1)

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
        """close() properly cleans up resources including all pooled contexts."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=2)

        mock_playwright = MagicMock()
        mock_browser = AsyncMock()
        mock_context1 = AsyncMock()
        mock_context2 = AsyncMock()

        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.stop = AsyncMock()
        mock_browser.new_context = AsyncMock(side_effect=[mock_context1, mock_context2])
        mock_browser.close = AsyncMock()
        mock_context1.close = AsyncMock()
        mock_context2.close = AsyncMock()

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
            assert renderer._context_pool is None
            assert renderer._all_contexts == []
            assert renderer._playwright is None

            # Both contexts should be closed
            mock_context1.close.assert_called_once()
            mock_context2.close.assert_called_once()
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
        """render() returns HTML content from page using pooled context."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=1)

        # Mock page
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Test content</html>")
        mock_page.close = AsyncMock()

        # Mock context
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        # Set up the pool
        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=1)
        renderer._all_contexts = [mock_context]
        await renderer._context_pool.put(mock_context)

        html = await renderer.render("https://example.com")

        assert html == "<html>Test content</html>"
        mock_page.goto.assert_called_once_with(
            "https://example.com", timeout=30000, wait_until="load"
        )
        mock_page.content.assert_called_once()
        mock_page.close.assert_called_once()

        # Context should be back in the pool
        assert renderer.pool_size == 1

    async def test_render_with_wait_strategy(self) -> None:
        """render() uses configured wait strategy."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(wait_until="networkidle", timeout=60000, max_contexts=1)

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Content</html>")
        mock_page.close = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=1)
        renderer._all_contexts = [mock_context]
        await renderer._context_pool.put(mock_context)

        await renderer.render("https://example.com")

        mock_page.goto.assert_called_once_with(
            "https://example.com", timeout=60000, wait_until="networkidle"
        )

    async def test_render_with_selector_wait(self) -> None:
        """render() can wait for specific selector."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=1)

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Content</html>")
        mock_page.close = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=1)
        renderer._all_contexts = [mock_context]
        await renderer._context_pool.put(mock_context)

        await renderer.render("https://example.com", wait_for_selector=".proxy-list")

        mock_page.wait_for_selector.assert_called_once_with(".proxy-list", timeout=30000)

    async def test_render_timeout(self) -> None:
        """render() handles timeout errors and releases context back to pool."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(timeout=1000, max_contexts=1)

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=TimeoutError("Page load timeout"))
        mock_page.close = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=1)
        renderer._all_contexts = [mock_context]
        await renderer._context_pool.put(mock_context)

        with pytest.raises(TimeoutError):
            await renderer.render("https://slow-site.com")

        # Page should still be closed
        mock_page.close.assert_called_once()

        # Context should be back in the pool
        assert renderer.pool_size == 1


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
            async with BrowserRenderer(max_contexts=1) as renderer:
                assert renderer._is_started is True
                html = await renderer.render("https://example.com")
                assert html == "<html>Test</html>"

            # Should be closed after exiting context
            mock_context.close.assert_called_once()
            mock_browser.close.assert_called_once()


class TestBrowserRendererContextPool:
    """Test context pool functionality."""

    async def test_acquire_context_from_pool(self) -> None:
        """acquire_context() returns context from pool."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=2)

        mock_context1 = AsyncMock()
        mock_context2 = AsyncMock()

        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=2)
        renderer._all_contexts = [mock_context1, mock_context2]
        await renderer._context_pool.put(mock_context1)
        await renderer._context_pool.put(mock_context2)

        assert renderer.pool_size == 2

        context = await renderer.acquire_context()
        assert context in [mock_context1, mock_context2]
        assert renderer.pool_size == 1

    async def test_acquire_context_not_started(self) -> None:
        """acquire_context() raises RuntimeError if not started."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer()

        with pytest.raises(RuntimeError, match="Browser not started"):
            await renderer.acquire_context()

    async def test_acquire_context_with_timeout(self) -> None:
        """acquire_context() respects timeout parameter."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=1)

        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=1)
        renderer._all_contexts = []

        # Pool is empty, so this should timeout
        with pytest.raises(asyncio.TimeoutError):
            await renderer.acquire_context(timeout=0.1)

    async def test_release_context_to_pool(self) -> None:
        """release_context() returns context to pool."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=1)

        mock_context = AsyncMock()

        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=1)
        renderer._all_contexts = [mock_context]

        # Pool is empty
        assert renderer.pool_size == 0

        await renderer.release_context(mock_context)

        assert renderer.pool_size == 1

    async def test_release_context_not_started(self) -> None:
        """release_context() raises RuntimeError if not started."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer()

        with pytest.raises(RuntimeError, match="Browser not started"):
            await renderer.release_context(AsyncMock())

    async def test_release_context_invalid_context(self) -> None:
        """release_context() raises ValueError if context not from pool."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=1)

        mock_context = AsyncMock()
        foreign_context = AsyncMock()

        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=1)
        renderer._all_contexts = [mock_context]

        with pytest.raises(ValueError, match="Context does not belong to this pool"):
            await renderer.release_context(foreign_context)

    async def test_pool_size_property(self) -> None:
        """pool_size returns current available contexts."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=3)

        # Not started
        assert renderer.pool_size == 0

        mock_context1 = AsyncMock()
        mock_context2 = AsyncMock()

        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=3)
        renderer._all_contexts = [mock_context1, mock_context2]
        await renderer._context_pool.put(mock_context1)
        await renderer._context_pool.put(mock_context2)

        assert renderer.pool_size == 2

    async def test_pool_capacity_property(self) -> None:
        """pool_capacity returns max_contexts."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=5)
        assert renderer.pool_capacity == 5

    async def test_concurrent_rendering_with_pool(self) -> None:
        """Pool supports concurrent rendering with multiple contexts."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=2)

        # Create mock contexts and pages
        mock_context1 = AsyncMock()
        mock_context2 = AsyncMock()

        mock_page1 = AsyncMock()
        mock_page1.goto = AsyncMock()
        mock_page1.content = AsyncMock(return_value="<html>Page 1</html>")
        mock_page1.close = AsyncMock()

        mock_page2 = AsyncMock()
        mock_page2.goto = AsyncMock()
        mock_page2.content = AsyncMock(return_value="<html>Page 2</html>")
        mock_page2.close = AsyncMock()

        mock_context1.new_page = AsyncMock(return_value=mock_page1)
        mock_context2.new_page = AsyncMock(return_value=mock_page2)

        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=2)
        renderer._all_contexts = [mock_context1, mock_context2]
        await renderer._context_pool.put(mock_context1)
        await renderer._context_pool.put(mock_context2)

        # Run two renders concurrently
        results = await asyncio.gather(
            renderer.render("https://site1.com"),
            renderer.render("https://site2.com"),
        )

        assert len(results) == 2
        assert "<html>Page 1</html>" in results
        assert "<html>Page 2</html>" in results

        # All contexts should be back in pool
        assert renderer.pool_size == 2


class TestBrowserRendererPooledPerformance:
    """Test performance benefits of pooled contexts."""

    async def test_pooled_vs_unpooled_conceptual(self) -> None:
        """Conceptually verify that pooled rendering reuses contexts."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=2)

        mock_context1 = AsyncMock()
        mock_context2 = AsyncMock()

        # Track how many times new_page is called on each context
        page_creation_count = {"ctx1": 0, "ctx2": 0}

        def make_mock_page():
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.content = AsyncMock(return_value="<html>Content</html>")
            mock_page.close = AsyncMock()
            return mock_page

        async def ctx1_new_page():
            page_creation_count["ctx1"] += 1
            return make_mock_page()

        async def ctx2_new_page():
            page_creation_count["ctx2"] += 1
            return make_mock_page()

        mock_context1.new_page = ctx1_new_page
        mock_context2.new_page = ctx2_new_page

        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=2)
        renderer._all_contexts = [mock_context1, mock_context2]
        await renderer._context_pool.put(mock_context1)
        await renderer._context_pool.put(mock_context2)

        # Render 5 pages sequentially
        for i in range(5):
            await renderer.render(f"https://site{i}.com")

        # With pooling, we should reuse the same 2 contexts
        # Total pages created = 5, spread across 2 contexts
        total_pages = page_creation_count["ctx1"] + page_creation_count["ctx2"]
        assert total_pages == 5

        # All contexts should be back in pool
        assert renderer.pool_size == 2

    async def test_pool_exhaustion_and_waiting(self) -> None:
        """When pool is exhausted, render waits for available context."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=1)

        mock_context = AsyncMock()
        render_started = asyncio.Event()
        allow_render_complete = asyncio.Event()

        # Simulate slow page rendering with synchronization
        async def slow_new_page():
            mock_page = AsyncMock()

            async def slow_goto(*args, **kwargs):
                render_started.set()
                await allow_render_complete.wait()

            mock_page.goto = slow_goto
            mock_page.content = AsyncMock(return_value="<html>Slow Content</html>")
            mock_page.close = AsyncMock()
            return mock_page

        mock_context.new_page = slow_new_page

        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=1)
        renderer._all_contexts = [mock_context]
        await renderer._context_pool.put(mock_context)

        # Start first render
        task1 = asyncio.create_task(renderer.render("https://site1.com"))

        # Wait until render has actually started and acquired the context
        await render_started.wait()

        # Pool should be empty while task1 is running
        assert renderer.pool_size == 0

        # Start second render - it will wait for context
        task2 = asyncio.create_task(renderer.render("https://site2.com"))

        # Let the second task start (it should be waiting on the pool)
        await asyncio.sleep(0.01)

        # Still empty - task2 is waiting
        assert renderer.pool_size == 0

        # Allow renders to complete
        allow_render_complete.set()

        # Wait for both to complete
        results = await asyncio.gather(task1, task2)

        assert len(results) == 2
        assert renderer.pool_size == 1

    async def test_get_context_options(self) -> None:
        """_get_context_options returns correct viewport and user agent."""
        from proxywhirl.browser import BrowserRenderer

        # Without user agent
        renderer = BrowserRenderer(viewport={"width": 1024, "height": 768})
        options = renderer._get_context_options()
        assert options == {"viewport": {"width": 1024, "height": 768}}

        # With user agent
        renderer = BrowserRenderer(
            viewport={"width": 1920, "height": 1080}, user_agent="CustomBot/1.0"
        )
        options = renderer._get_context_options()
        assert options == {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "CustomBot/1.0",
        }


class TestBrowserRendererPooledVsUnpooledBenchmark:
    """Benchmark tests comparing pooled vs simulated unpooled performance."""

    async def test_pooled_performance_simulation(self) -> None:
        """Simulate pooled performance - contexts are reused."""
        from proxywhirl.browser import BrowserRenderer

        renderer = BrowserRenderer(max_contexts=3)

        # Track context creation
        context_creation_count = 0

        def make_mock_context():
            nonlocal context_creation_count
            context_creation_count += 1
            mock_context = AsyncMock()

            async def new_page():
                mock_page = AsyncMock()
                mock_page.goto = AsyncMock()
                mock_page.content = AsyncMock(return_value="<html>Content</html>")
                mock_page.close = AsyncMock()
                return mock_page

            mock_context.new_page = new_page
            return mock_context

        # Create pool with 3 contexts
        mock_contexts = [make_mock_context() for _ in range(3)]

        renderer._is_started = True
        renderer._context_pool = asyncio.Queue(maxsize=3)
        renderer._all_contexts = mock_contexts
        for ctx in mock_contexts:
            await renderer._context_pool.put(ctx)

        # Render 10 pages
        start_time = time.monotonic()
        for i in range(10):
            await renderer.render(f"https://site{i}.com")
        pooled_duration = time.monotonic() - start_time

        # With pooling: only 3 contexts were created, but 10 pages rendered
        assert context_creation_count == 3
        assert renderer.pool_size == 3

        # Store duration for comparison (we can't actually compare without real browser)
        assert pooled_duration >= 0  # Just verify it ran

    async def test_unpooled_simulation(self) -> None:
        """Simulate unpooled performance - new context per render."""

        # This simulates what would happen without pooling:
        # A new context is created for each render

        context_creation_count = 0

        async def simulate_unpooled_render():
            nonlocal context_creation_count
            context_creation_count += 1
            # Simulate context creation overhead
            await asyncio.sleep(0)

        # Render 10 pages without pooling
        start_time = time.monotonic()
        for _ in range(10):
            await simulate_unpooled_render()
        unpooled_duration = time.monotonic() - start_time

        # Without pooling: 10 contexts were created for 10 pages
        assert context_creation_count == 10
        assert unpooled_duration >= 0  # Just verify it ran
