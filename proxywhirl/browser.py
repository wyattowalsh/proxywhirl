"""Browser-based rendering for JavaScript-heavy proxy sources using Playwright.

This module provides asynchronous page rendering via Playwright, optimized for
fetching proxies from JavaScript-heavy sources that require full browser execution.

Key Features:
    - Playwright-based async rendering (Chromium, Firefox, WebKit)
    - Context pooling for concurrent rendering without browser spawn overhead
    - Automatic page cleanup and resource management
    - Configurable timeout, wait strategies, and viewport settings
    - Custom user agent support for scraper-friendly rendering

Architecture:
    The BrowserRenderer uses a pool of pre-created browser contexts instead of
    creating a new context per render. This reduces overhead and allows true
    concurrent rendering. Contexts are managed via asyncio.Queue.

Performance Characteristics:
    - Single context (default): ~50-100ms per page
    - Pooled contexts: 10-50ms per page with concurrency
    - Memory: ~50MB per context (adjust max_contexts accordingly)
    - CPU: ~1-2 cores per browser instance

Security:
    - Contexts run in separate browser tabs (isolated by default)
    - No data leakage between contexts
    - Recommended: Run with headless=True in production

Use Cases:
    1. Fetching from JS-rendered proxy lists (e.g., free proxy sites)
    2. Handling AJAX-loaded content and infinite scroll
    3. Executing JavaScript that generates proxy lists
    4. Web scraping with modern JavaScript frameworks (React, Vue, Angular)

Not Recommended For:
    - Simple HTML pages (use httpx instead)
    - Sensitive data (browser overhead not worth it)
    - Extreme scale (100+ concurrent contexts)
    - Tight latency budgets (<100ms per page)

Examples:
    >>> # Basic usage
    >>> renderer = BrowserRenderer(headless=True)
    >>> await renderer.start()
    >>> try:
    ...     html = await renderer.render("https://example.com")
    ... finally:
    ...     await renderer.close()

    >>> # With context manager
    >>> async with BrowserRenderer(max_contexts=5) as renderer:
    ...     html = await renderer.render("https://example.com")

    >>> # Wait for dynamic content
    >>> async with BrowserRenderer() as renderer:
    ...     html = await renderer.render(
    ...         "https://example.com/proxies",
    ...         wait_for_selector=".proxy-list",
    ...         wait_for_timeout=2000
    ...     )

    >>> # Concurrent rendering
    >>> async with BrowserRenderer(max_contexts=5) as renderer:
    ...     urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
    ...     results = await asyncio.gather(*[renderer.render(url) for url in urls])

    >>> # Manual context management for fine-grained control
    >>> renderer = BrowserRenderer(max_contexts=10)
    >>> await renderer.start()
    >>> context = await renderer.acquire_context(timeout=5.0)
    >>> page = await context.new_page()
    >>> await page.goto("https://example.com")
    >>> content = await page.content()
    >>> await page.close()
    >>> await renderer.release_context(context)
    >>> await renderer.close()
"""

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
        extra_args: list[str] | None = None,
    ) -> None:
        """Initialize browser renderer with pooled context management.

        Creates a BrowserRenderer instance that will manage a pool of browser contexts
        for concurrent page rendering. The browser itself is not started until start()
        or the async context manager is entered.

        Args:
            headless: Run browser in headless mode without GUI.
                Default: True. Set to False for debugging (shows browser window).
            browser_type: Browser engine to use.
                Default: "chromium" (fastest, recommended).
                Other options: "firefox" (more stable), "webkit" (Safari-like).
            timeout: Page load timeout in milliseconds.
                Default: 30000 (30 seconds). Applies to goto(), wait_for_selector(), etc.
                Raises TimeoutError if exceeded.
            wait_until: When to consider page navigation complete.
                Default: "load" for full page load. Other options are
                "domcontentloaded" for faster DOM readiness and "networkidle"
                for slower, more reliable network quiescence.
            user_agent: Custom user agent string to send in HTTP headers.
                Default: None (uses Playwright default).
                Tip: Use modern user agents to avoid being blocked by scrapers.
                Example: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            viewport: Custom viewport size as dict with "width" and "height".
                Default: {"width": 1280, "height": 720} for desktop. Use
                {"width": 375, "height": 667} for mobile, {"width": 1920,
                "height": 1080} for larger displays, or None for the default.
            max_contexts: Maximum number of pooled browser contexts.
                Default: 3 for light use. Use 5-10 for moderate concurrency
                and 20+ only for high-throughput scenarios with enough memory.
                Memory impact is approximately 50-100MB per context.
            extra_args: Additional command-line arguments for the browser.
                Dangerous arguments (e.g., --no-sandbox, --remote-debugging-port)
                are rejected to prevent security risks.

        Raises:
            ValueError: If max_contexts < 1 (automatically adjusted to 1)
            ValueError: If extra_args contains dangerous browser flags

        Examples:
            >>> # Default configuration (recommended)
            >>> renderer = BrowserRenderer()

            >>> # Faster loading (trade reliability for speed)
            >>> renderer = BrowserRenderer(wait_until="domcontentloaded")

            >>> # High concurrency
            >>> renderer = BrowserRenderer(max_contexts=10)

            >>> # Custom user agent (appears as real browser to servers)
            >>> renderer = BrowserRenderer(user_agent="Mozilla/5.0 (iPhone...)")

            >>> # Mobile viewport
            >>> renderer = BrowserRenderer(viewport={"width": 375, "height": 667})

            >>> # Firefox browser (more stable with some JS-heavy sites)
            >>> renderer = BrowserRenderer(browser_type="firefox")
        """
        self.headless = headless
        self.browser_type = browser_type
        self.timeout = timeout
        self.wait_until = wait_until
        self.user_agent = user_agent
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.max_contexts = max(1, max_contexts)
        self.extra_args = self._validate_browser_args(extra_args or [])

        self._playwright: Any | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None  # Legacy single context (deprecated)
        self._is_started = False

        # Context pool for concurrent rendering
        self._context_pool: asyncio.Queue[BrowserContext] | None = None
        self._all_contexts: list[BrowserContext] = []
        self._pool_lock: asyncio.Lock | None = None

    @staticmethod
    def _validate_browser_args(args: list[str]) -> list[str]:
        """Validate browser command-line arguments for security.

        Rejects dangerous flags that could compromise sandboxing or
        expose remote debugging interfaces.

        Args:
            args: List of command-line argument strings

        Returns:
            Validated argument list

        Raises:
            ValueError: If a dangerous argument is detected
        """
        dangerous = {
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--remote-debugging-port",
            "--remote-debugging-address",
            "--disable-web-security",
            "--disable-features=IsolateOrigins",
            "--disable-site-isolation-trials",
        }
        for arg in args:
            base = arg.split("=", 1)[0].lower()
            if base in dangerous or base.startswith("--remote-debugging"):
                raise ValueError(f"Dangerous browser argument rejected: {arg}")
        return args

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
        launch_options: dict[str, Any] = {"headless": self.headless}
        if self.extra_args:
            launch_options["args"] = self.extra_args
        self._browser = await browser_launcher.launch(**launch_options)

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
        """Render a page and return its fully-loaded HTML content.

        Fetches a URL through the browser, waits for page load and any specified
        selectors, and returns the complete rendered HTML. Uses pooled contexts
        for concurrent-safe rendering. Each call acquires a context, performs
        rendering, and returns the context to the pool.

        Args:
            url: Full HTTP(S) URL to render.
                Example: "https://free-proxy-list.net/"
            wait_for_selector: Optional CSS selector to wait for before returning.
                After page load completes, the renderer will wait for this selector
                to appear in the DOM before returning. Useful for pages with AJAX
                content or lazy loading.
                Example: ".proxy-row" (wait for proxy table rows)
                Default: None (return after page load only)
            wait_for_timeout: Optional additional wait time in milliseconds AFTER
                wait_for_selector (if provided). Useful for waiting for animations
                or additional network activity to complete.
                Default: None (no additional wait)
                Example: 2000 (wait 2 seconds after selector appears)

        Returns:
            str: Complete rendered HTML as a string, including all JavaScript-
            executed content, inline styles, and dynamically loaded elements.
            Content is taken after page_load + selector wait + timeout wait.

        Raises:
            RuntimeError: If browser is not started (call start() or use context manager)
            TimeoutError: If page load exceeds timeout (from __init__)
            asyncio.TimeoutError: If wait_for_selector exceeds timeout (from __init__)
            Exception: Other page loading errors (network, invalid URL, etc.)

        Examples:
            >>> async with BrowserRenderer() as renderer:
            ...     # Simple page render
            ...     html = await renderer.render("https://example.com")

            >>> async with BrowserRenderer() as renderer:
            ...     # Wait for dynamic content to load
            ...     html = await renderer.render(
            ...         "https://free-proxy-list.net/",
            ...         wait_for_selector="table.table tbody tr"
            ...     )

            >>> async with BrowserRenderer() as renderer:
            ...     # Wait for selector + additional animation time
            ...     html = await renderer.render(
            ...         "https://proxylists.io/",
            ...         wait_for_selector=".proxy-item",
            ...         wait_for_timeout=1000  # Wait 1s after list loads
            ...     )

            >>> async with BrowserRenderer(max_contexts=5) as renderer:
            ...     # Concurrent rendering
            ...     urls = ["https://site1.com", "https://site2.com"]
            ...     results = await asyncio.gather(
            ...         *[renderer.render(url) for url in urls]
            ...     )

        Performance Notes:
            - Typical render time: 50-500ms (depends on page complexity)
            - Pooled rendering: 10-50ms overhead per concurrent request
            - Memory: ~50MB per pooled context
            - Network: Full page load including all resources

        Selector Tips:
            - Use specific selectors to wait for key content: ".proxy-list", "#table", "body"
            - Avoid selectors that appear early (e.g., page header)
            - Test selectors in browser console: document.querySelector("...")
            - Use xpath for complex selections: "//table[@id='proxies']/tbody/tr"

        Proxy Extraction Pattern:
            >>> async with BrowserRenderer(wait_until="networkidle") as renderer:
            ...     html = await renderer.render(
            ...         "https://example-proxy-site.com/",
            ...         wait_for_selector="table.proxy-table tbody tr",
            ...         wait_for_timeout=2000
            ...     )
            ...     # Parse html with BeautifulSoup, lxml, etc.
            ...     from bs4 import BeautifulSoup
            ...     soup = BeautifulSoup(html, "html.parser")
            ...     proxies = [tr.text.strip() for tr in soup.select("table tbody tr")]
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
