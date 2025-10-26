"""Browser-based rendering for JavaScript-heavy proxy sources using Playwright."""

from typing import TYPE_CHECKING, Any, Literal, Optional

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext, Page  # type: ignore[import-not-found]


class BrowserRenderer:
    """Browser-based page renderer using Playwright for JavaScript execution.

    Renders pages that require full browser JavaScript execution, useful for
    proxy sources that use client-side rendering or dynamic content loading.

    Example:
        >>> renderer = BrowserRenderer(headless=True)
        >>> await renderer.start()
        >>> html = await renderer.render("https://example.com/proxies")
        >>> await renderer.close()

        Or use as context manager:
        >>> async with BrowserRenderer() as renderer:
        ...     html = await renderer.render("https://example.com/proxies")
    """

    def __init__(
        self,
        headless: bool = True,
        browser_type: Literal["chromium", "firefox", "webkit"] = "chromium",
        timeout: int = 30000,
        wait_until: Literal["load", "domcontentloaded", "networkidle"] = "load",
        user_agent: Optional[str] = None,
        viewport: Optional[dict[str, int]] = None,
    ) -> None:
        """Initialize browser renderer.

        Args:
            headless: Run browser in headless mode (default: True)
            browser_type: Browser engine to use (default: chromium)
            timeout: Page load timeout in milliseconds (default: 30000)
            wait_until: When to consider navigation complete (default: load)
            user_agent: Custom user agent string (optional)
            viewport: Custom viewport size, e.g. {"width": 1280, "height": 720}
        """
        self.headless = headless
        self.browser_type = browser_type
        self.timeout = timeout
        self.wait_until = wait_until
        self.user_agent = user_agent
        self.viewport = viewport or {"width": 1280, "height": 720}

        self._playwright: Optional[Any] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._is_started = False

    async def start(self) -> None:
        """Start the browser instance.

        Initializes Playwright and launches the browser. Idempotent - safe to call
        multiple times.

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

        # Create context
        context_options: dict[str, Any] = {"viewport": self.viewport}
        if self.user_agent:
            context_options["user_agent"] = self.user_agent

        self._context = await self._browser.new_context(**context_options)
        self._is_started = True

    async def close(self) -> None:
        """Close the browser instance.

        Closes the browser context and browser. Safe to call multiple times.
        """
        if not self._is_started:
            return

        if self._context:
            await self._context.close()
            self._context = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

        self._is_started = False

    async def render(
        self,
        url: str,
        wait_for_selector: Optional[str] = None,
        wait_for_timeout: Optional[int] = None,
    ) -> str:
        """Render a page and return its HTML content.

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
        if not self._is_started or not self._context:
            raise RuntimeError(
                "Browser not started. Call start() or use as context manager."
            )

        page: Page = await self._context.new_page()

        try:
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
            await page.close()

    async def __aenter__(self) -> "BrowserRenderer":
        """Context manager entry - starts the browser."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - closes the browser."""
        await self.close()
