"""Browser-based rendering for JavaScript-heavy proxy sources using Playwright."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Literal

from loguru import logger

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext, Page


class BrowserRenderer:
    """Browser-based page renderer using Playwright for JavaScript execution.

    Renders pages that require full browser JavaScript execution, useful for
    proxy sources that use client-side rendering or dynamic content loading.

    Supports context pooling for improved performance when rendering multiple
    pages concurrently. Pooled contexts are reused instead of being created
    fresh for each render operation.

    Example:
        >>> renderer = BrowserRenderer(headless=True)
        >>> await renderer.start()
        >>> html = await renderer.render("https://example.com/proxies")
        >>> await renderer.close()

        Or use as context manager:
        >>> async with BrowserRenderer() as renderer:
        ...     html = await renderer.render("https://example.com/proxies")

        Pooled mode for concurrent rendering:
        >>> async with BrowserRenderer(max_contexts=5) as renderer:
        ...     results = await asyncio.gather(
        ...         renderer.render("https://site1.com"),
        ...         renderer.render("https://site2.com"),
        ...         renderer.render("https://site3.com"),
        ...     )
    """

    def __init__(
        self,
        headless: bool = True,
        browser_type: Literal["chromium", "firefox", "webkit"] = "chromium",
        timeout: int = 30000,
        wait_until: Literal["load", "domcontentloaded", "networkidle"] = "load",
        user_agent: str | None = None,
        viewport: dict[str, int] | None = None,
        max_contexts: int = 3,
    ) -> None:
        """Initialize browser renderer.

        Args:
            headless: Run browser in headless mode (default: True)
            browser_type: Browser engine to use (default: chromium)
            timeout: Page load timeout in milliseconds (default: 30000)
            wait_until: When to consider navigation complete (default: load)
            user_agent: Custom user agent string (optional)
            viewport: Custom viewport size, e.g. {"width": 1280, "height": 720}
            max_contexts: Maximum number of pooled browser contexts (default: 3).
                         Higher values allow more concurrent rendering but use more memory.
        """
        self.headless = headless
        self.browser_type = browser_type
        self.timeout = timeout
        self.wait_until = wait_until
        self.user_agent = user_agent
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.max_contexts = max(1, max_contexts)

        self._playwright: Any | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None  # Legacy single context (deprecated)
        self._is_started = False

        # Context pool for concurrent rendering
        self._context_pool: asyncio.Queue[BrowserContext] | None = None
        self._all_contexts: list[BrowserContext] = []
        self._pool_lock: asyncio.Lock | None = None

    async def start(self) -> None:
        """Start the browser instance and initialize the context pool.

        Initializes Playwright, launches the browser, and pre-creates browser
        contexts for the pool. Idempotent - safe to call multiple times.

        Raises:
            ImportError: If playwright is not installed
            RuntimeError: If browser fails to start
        """
        if self._is_started:
            return  # Already started

        try:
            from playwright.async_api import async_playwright
        except ImportError as e:
            raise ImportError(
                "Playwright is required for browser rendering. "
                "Install with: pip install 'proxywhirl[browser]' or pip install playwright"
            ) from e

        # Start playwright
        self._playwright = await async_playwright().start()

        # Launch browser
        browser_launcher = getattr(self._playwright, self.browser_type)
        self._browser = await browser_launcher.launch(headless=self.headless)

        # Initialize pool infrastructure
        self._context_pool = asyncio.Queue(maxsize=self.max_contexts)
        self._all_contexts = []
        self._pool_lock = asyncio.Lock()

        # Pre-create contexts for the pool
        context_options = self._get_context_options()
        for i in range(self.max_contexts):
            context = await self._browser.new_context(**context_options)
            self._all_contexts.append(context)
            await self._context_pool.put(context)
            logger.debug(f"Created browser context {i + 1}/{self.max_contexts} for pool")

        # Keep legacy single context for backwards compatibility
        self._context = self._all_contexts[0] if self._all_contexts else None
        self._is_started = True
        logger.info(f"BrowserRenderer started with {self.max_contexts} pooled contexts")

    def _get_context_options(self) -> dict[str, Any]:
        """Get context creation options.

        Returns:
            Dictionary of options for browser.new_context()
        """
        options: dict[str, Any] = {"viewport": self.viewport}
        if self.user_agent:
            options["user_agent"] = self.user_agent
        return options

    async def close(self) -> None:
        """Close the browser instance and all pooled contexts.

        Closes all browser contexts in the pool and the browser itself.
        Safe to call multiple times.
        """
        if not self._is_started:
            return

        # Close all pooled contexts
        for context in self._all_contexts:
            try:
                await context.close()
            except Exception as e:
                logger.warning(f"Error closing browser context: {e}")

        self._all_contexts = []
        self._context_pool = None
        self._pool_lock = None
        self._context = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

        self._is_started = False
        logger.debug("BrowserRenderer closed and all contexts cleaned up")

    async def acquire_context(self, timeout: float | None = None) -> BrowserContext:
        """Acquire a browser context from the pool.

        Blocks until a context is available. For concurrent rendering, use this
        with release_context() to manage context lifecycle manually.

        Args:
            timeout: Maximum time to wait for a context (seconds). None means wait forever.

        Returns:
            A browser context from the pool

        Raises:
            RuntimeError: If browser is not started
            asyncio.TimeoutError: If timeout expires before a context is available
        """
        if not self._is_started or self._context_pool is None:
            raise RuntimeError("Browser not started. Call start() or use as context manager.")

        if timeout is not None:
            return await asyncio.wait_for(self._context_pool.get(), timeout=timeout)
        return await self._context_pool.get()

    async def release_context(self, context: BrowserContext) -> None:
        """Release a browser context back to the pool.

        Returns a previously acquired context to the pool for reuse.

        Args:
            context: The browser context to release

        Raises:
            RuntimeError: If browser is not started
            ValueError: If context is not from this pool
        """
        if not self._is_started or self._context_pool is None:
            raise RuntimeError("Browser not started or already closed.")

        if context not in self._all_contexts:
            raise ValueError("Context does not belong to this pool")

        await self._context_pool.put(context)
        logger.debug("Browser context released back to pool")

    @property
    def pool_size(self) -> int:
        """Number of contexts currently available in the pool."""
        if self._context_pool is None:
            return 0
        return self._context_pool.qsize()

    @property
    def pool_capacity(self) -> int:
        """Total capacity of the context pool."""
        return self.max_contexts

    async def render(
        self,
        url: str,
        wait_for_selector: str | None = None,
        wait_for_timeout: int | None = None,
    ) -> str:
        """Render a page and return its HTML content.

        Uses the context pool for concurrent-safe rendering. Acquires a context
        from the pool, renders the page, and releases the context back.

        Args:
            url: URL to render
            wait_for_selector: Optional CSS selector to wait for before returning
            wait_for_timeout: Optional additional wait time in milliseconds

        Returns:
            Rendered HTML content as string

        Raises:
            RuntimeError: If browser is not started
            TimeoutError: If page load times out
        """
        if not self._is_started or self._context_pool is None:
            raise RuntimeError("Browser not started. Call start() or use as context manager.")

        # Acquire context from pool
        context = await self.acquire_context()
        page: Page | None = None

        try:
            page = await context.new_page()

            # Navigate to page
            await page.goto(url, timeout=self.timeout, wait_until=self.wait_until)

            # Wait for selector if provided
            if wait_for_selector:
                await page.wait_for_selector(wait_for_selector, timeout=self.timeout)

            # Additional wait if provided
            if wait_for_timeout:
                await page.wait_for_timeout(wait_for_timeout)

            # Get rendered HTML
            html: str = await page.content()
            return html

        finally:
            # Always close the page
            if page:
                await page.close()
            # Always release context back to pool
            await self.release_context(context)

    async def __aenter__(self) -> BrowserRenderer:
        """Context manager entry - starts the browser."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - closes the browser."""
        await self.close()
