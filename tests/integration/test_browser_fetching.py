"""Integration tests for browser-based proxy fetching."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig
from proxywhirl.models import RenderMode


class TestBrowserFetching:
    """Test ProxyFetcher with browser rendering mode."""

    async def test_fetcher_with_browser_mode(self) -> None:
        """ProxyFetcher uses BrowserRenderer when render_mode=BROWSER."""
        # Create source with BROWSER render mode
        source = ProxySourceConfig(
            url="https://example.com/proxies",
            format="json",
            render_mode=RenderMode.BROWSER,
        )

        fetcher = ProxyFetcher(sources=[source])

        # Mock the browser renderer - return JSON array directly
        mock_html = '[{"host": "1.2.3.4", "port": 8080}]'

        # Mock BrowserRenderer
        mock_renderer = AsyncMock()
        mock_renderer.render = AsyncMock(return_value=mock_html)
        mock_renderer.__aenter__ = AsyncMock(return_value=mock_renderer)
        mock_renderer.__aexit__ = AsyncMock(return_value=None)

        # Mock the browser module
        mock_browser_module = MagicMock()
        mock_browser_module.BrowserRenderer = MagicMock(return_value=mock_renderer)

        with patch.dict("sys.modules", {"proxywhirl.browser": mock_browser_module}):
            proxies = await fetcher.fetch_from_source(source)

            # Verify browser was used
            mock_renderer.render.assert_called_once_with(source.url)

            # Verify proxies were parsed
            assert len(proxies) == 1
            assert proxies[0]["host"] == "1.2.3.4"

    async def test_fetcher_static_mode_no_browser(self) -> None:
        """ProxyFetcher uses HTTP client when render_mode=STATIC."""
        import respx
        from httpx import Response

        source = ProxySourceConfig(
            url="https://example.com/proxies",
            format="json",
            render_mode=RenderMode.STATIC,
        )

        fetcher = ProxyFetcher(sources=[source])

        # Mock HTTP response - return JSON array
        mock_json = '[{"host": "5.6.7.8", "port": 3128}]'

        with respx.mock:
            respx.get(source.url).mock(return_value=Response(200, text=mock_json))

            proxies = await fetcher.fetch_from_source(source)

            # Verify proxies were parsed
            assert len(proxies) == 1
            assert proxies[0]["host"] == "5.6.7.8"

    async def test_browser_mode_import_error(self) -> None:
        """ProxyFetcher raises helpful error if Playwright not installed."""
        from proxywhirl.exceptions import ProxyFetchError

        source = ProxySourceConfig(
            url="https://example.com/proxies",
            format="json",
            render_mode=RenderMode.BROWSER,
        )

        fetcher = ProxyFetcher(sources=[source])

        # Mock BrowserRenderer import to fail
        with patch.dict("sys.modules", {"proxywhirl.browser": None}):
            with patch("builtins.__import__", side_effect=ImportError("No module")):
                with pytest.raises(ProxyFetchError, match="Browser rendering requires Playwright"):
                    await fetcher.fetch_from_source(source)

    async def test_browser_timeout_handling(self) -> None:
        """ProxyFetcher handles browser timeout errors gracefully."""
        from proxywhirl.exceptions import ProxyFetchError

        source = ProxySourceConfig(
            url="https://slow-site.com/proxies",
            format="json",
            render_mode=RenderMode.BROWSER,
        )

        fetcher = ProxyFetcher(sources=[source])

        # Mock browser to raise timeout
        mock_renderer = AsyncMock()
        mock_renderer.render = AsyncMock(side_effect=TimeoutError("Page load timeout"))
        mock_renderer.__aenter__ = AsyncMock(return_value=mock_renderer)
        mock_renderer.__aexit__ = AsyncMock(return_value=None)

        # Mock the browser module
        mock_browser_module = MagicMock()
        mock_browser_module.BrowserRenderer = MagicMock(return_value=mock_renderer)

        with patch.dict("sys.modules", {"proxywhirl.browser": mock_browser_module}):
            with pytest.raises(ProxyFetchError, match="Browser timeout"):
                await fetcher.fetch_from_source(source)

    async def test_browser_runtime_error_handling(self) -> None:
        """ProxyFetcher handles browser runtime errors gracefully."""
        from proxywhirl.exceptions import ProxyFetchError

        source = ProxySourceConfig(
            url="https://broken-site.com/proxies",
            format="json",
            render_mode=RenderMode.BROWSER,
        )

        fetcher = ProxyFetcher(sources=[source])

        # Mock browser to raise runtime error
        mock_renderer = AsyncMock()
        mock_renderer.render = AsyncMock(side_effect=RuntimeError("Browser crashed"))
        mock_renderer.__aenter__ = AsyncMock(return_value=mock_renderer)
        mock_renderer.__aexit__ = AsyncMock(return_value=None)

        # Mock the browser module
        mock_browser_module = MagicMock()
        mock_browser_module.BrowserRenderer = MagicMock(return_value=mock_renderer)

        with patch.dict("sys.modules", {"proxywhirl.browser": mock_browser_module}):
            with pytest.raises(ProxyFetchError, match="Browser error"):
                await fetcher.fetch_from_source(source)

    async def test_fetch_all_with_mixed_render_modes(self) -> None:
        """ProxyFetcher handles sources with different render modes."""
        import respx
        from httpx import Response

        # Mix of STATIC and BROWSER sources
        source_static = ProxySourceConfig(
            url="https://static-site.com/proxies",
            format="json",
            render_mode=RenderMode.STATIC,
        )
        source_browser = ProxySourceConfig(
            url="https://js-site.com/proxies",
            format="json",
            render_mode=RenderMode.BROWSER,
        )

        fetcher = ProxyFetcher(sources=[source_static, source_browser], validator=None)

        # Mock HTTP response for static source
        mock_static_json = '[{"url": "http://1.2.3.4:8080"}]'

        # Mock browser response
        mock_browser_html = '[{"url": "http://5.6.7.8:3128"}]'
        mock_renderer = AsyncMock()
        mock_renderer.render = AsyncMock(return_value=mock_browser_html)
        mock_renderer.__aenter__ = AsyncMock(return_value=mock_renderer)
        mock_renderer.__aexit__ = AsyncMock(return_value=None)

        with respx.mock:
            respx.get(source_static.url).mock(return_value=Response(200, text=mock_static_json))

            # Mock the browser module
            mock_browser_module = MagicMock()
            mock_browser_module.BrowserRenderer = MagicMock(return_value=mock_renderer)

            with patch.dict("sys.modules", {"proxywhirl.browser": mock_browser_module}):
                proxies = await fetcher.fetch_all(validate=False, deduplicate=False)

                # Should get proxies from both sources
                assert len(proxies) == 2
                urls = {p["url"] for p in proxies}
                assert "http://1.2.3.4:8080" in urls
                assert "http://5.6.7.8:3128" in urls
