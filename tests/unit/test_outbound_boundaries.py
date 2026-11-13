"""Focused regressions for outbound fetch, validation, and browser boundaries."""

from __future__ import annotations

import asyncio
import socket
from unittest.mock import AsyncMock, MagicMock, call, patch

import httpx
import pytest

from proxywhirl.browser import BrowserRenderer
from proxywhirl.exceptions import ProxyFetchError
from proxywhirl.fetchers import (
    CSVParser,
    JSONParser,
    PlainTextParser,
    ProxyFetcher,
    ProxySourceConfig,
    ProxyValidator,
)
from proxywhirl.fetchers.parsers import GeonodeParser


def _public_getaddrinfo(host: str, *args: object, **kwargs: object) -> list[tuple[object, ...]]:
    """Pin helper for tests: resolve example hosts to a documentation IPv4."""
    del args, kwargs
    if str(host).startswith("127.") or str(host) in {"localhost", "::1"}:
        return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 0))]
    return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("8.8.8.8", 0))]


async def _ready_renderer(page: AsyncMock) -> BrowserRenderer:
    """Return a renderer with one mocked context ready for use."""
    renderer = BrowserRenderer(max_contexts=1)
    context = AsyncMock()
    context.new_page = AsyncMock(return_value=page)
    renderer._is_started = True
    renderer._context_pool = asyncio.Queue(maxsize=1)
    renderer._all_contexts = [context]
    await renderer._context_pool.put(context)
    return renderer


class TestValidatorClientBoundaries:
    """Ensure proxy-specific transports and cleanup remain isolated."""

    async def test_socks_clients_are_partitioned_by_exact_credentialed_url(self) -> None:
        """Different SOCKS URLs or credentials must never share a transport."""
        validator = ProxyValidator()
        first_client = AsyncMock()
        second_client = AsyncMock()
        transport = MagicMock()

        with (
            patch("proxywhirl.fetchers.validator.SOCKS_AVAILABLE", True),
            patch("proxywhirl.fetchers.validator.AsyncProxyTransport") as transport_type,
            patch.object(
                httpx,
                "AsyncClient",
                side_effect=[first_client, second_client],
            ),
        ):
            transport_type.from_url.side_effect = [transport, MagicMock()]
            first = await validator._get_socks_client("socks5://alice:first@proxy.example.com:1080")
            first_again = await validator._get_socks_client(
                "socks5://alice:first@proxy.example.com:1080"
            )
            second = await validator._get_socks_client(
                "socks5://alice:second@proxy.example.com:1080"
            )

        assert first is first_client
        assert first_again is first_client
        assert second is second_client
        assert transport_type.from_url.call_args_list == [
            call("socks5://alice:first@proxy.example.com:1080"),
            call("socks5://alice:second@proxy.example.com:1080"),
        ]
        assert all("alice" not in key for key in validator._socks_clients)

        await validator.close()
        first_client.aclose.assert_awaited_once()
        second_client.aclose.assert_awaited_once()

    async def test_socks_client_cache_evicts_and_closes_least_recently_used(self) -> None:
        """The credential-partitioned SOCKS cache must stay bounded."""
        validator = ProxyValidator()
        validator._max_socks_clients = 2
        clients = [AsyncMock(), AsyncMock(), AsyncMock()]

        with (
            patch("proxywhirl.fetchers.validator.SOCKS_AVAILABLE", True),
            patch("proxywhirl.fetchers.validator.AsyncProxyTransport") as transport_type,
            patch.object(httpx, "AsyncClient", side_effect=clients),
        ):
            transport_type.from_url.side_effect = [MagicMock(), MagicMock(), MagicMock()]
            first = await validator._get_socks_client("socks5://alice:a@one.example:1080")
            second = await validator._get_socks_client("socks5://alice:b@two.example:1080")
            assert await validator._get_socks_client("socks5://alice:a@one.example:1080") is first
            third = await validator._get_socks_client("socks5://alice:c@three.example:1080")

        assert len(validator._socks_clients) == 2
        assert validator._socks_client is third
        second.aclose.assert_awaited_once()
        first.aclose.assert_not_awaited()
        third.aclose.assert_not_awaited()

        await validator.close()
        first.aclose.assert_awaited_once()
        second.aclose.assert_awaited_once()
        third.aclose.assert_awaited_once()

    async def test_validator_close_finishes_all_clients_before_propagating_cancellation(
        self,
    ) -> None:
        """One cancelled close must not prevent other clients from closing."""
        validator = ProxyValidator()
        direct_client = AsyncMock()
        socks_client = AsyncMock()
        direct_client.aclose.side_effect = asyncio.CancelledError()
        validator._client = direct_client
        validator._socks_client = socks_client

        with pytest.raises(asyncio.CancelledError):
            await validator.close()

        direct_client.aclose.assert_awaited_once()
        socks_client.aclose.assert_awaited_once()
        assert validator._client is None
        assert validator._socks_client is None

    async def test_fetcher_close_always_closes_validator_after_client_failure(self) -> None:
        """Fetcher cleanup must not strand validator clients after a close error."""
        validator = MagicMock()
        validator.close = AsyncMock()
        fetcher = ProxyFetcher(validator=validator)
        client = AsyncMock()
        client.aclose.side_effect = RuntimeError("client close failed")
        fetcher._client = client

        with pytest.raises(RuntimeError, match="client close failed"):
            await fetcher.close()

        client.aclose.assert_awaited_once()
        validator.close.assert_awaited_once()
        assert fetcher._client is None

    async def test_fetcher_close_cancels_refresh_before_releasing_clients(self) -> None:
        """Closing a fetcher cannot leave its background refresh task running."""
        validator = MagicMock()
        validator.close = AsyncMock()
        fetcher = ProxyFetcher(validator=validator)
        refresh_started = asyncio.Event()

        async def refresh() -> None:
            refresh_started.set()
            await asyncio.Event().wait()

        refresh_task = asyncio.create_task(refresh())
        fetcher._refresh_task = refresh_task
        await refresh_started.wait()

        await fetcher.close()

        assert refresh_task.cancelled()
        assert fetcher._refresh_task is None
        validator.close.assert_awaited_once()


class TestFetcherRedirectBoundaries:
    """Ensure each static redirect is checked before another request is sent."""

    async def test_static_fetch_aborts_unsafe_redirect_before_request(self) -> None:
        """A public source cannot redirect the HTTP client to a loopback target."""
        source = ProxySourceConfig(
            url="https://public.example/proxies",
            format="json",
        )
        fetcher = ProxyFetcher()
        redirect = MagicMock()
        redirect.status_code = 302
        redirect.headers = {"Location": "http://127.0.0.1/admin"}
        response_context = AsyncMock()
        response_context.__aenter__.return_value = redirect
        client = MagicMock()
        client.stream.return_value = response_context

        def safety(url: str) -> tuple[bool, str]:
            if url.startswith("http://127.0.0.1"):
                return False, "Loopback address blocked"
            return True, ""

        with (
            patch.object(fetcher, "_get_client", new=AsyncMock(return_value=client)),
            patch(
                "proxywhirl.fetchers.fetcher.validate_source_url_safety",
                side_effect=safety,
            ) as validate,
            patch("proxywhirl.security.socket.getaddrinfo", _public_getaddrinfo),
            pytest.raises(ProxyFetchError, match="redirect blocked.*Loopback"),
        ):
            await fetcher.fetch_from_source(source)

        assert any(
            awaited.args[0] == "http://127.0.0.1/admin" for awaited in validate.call_args_list
        )
        client.stream.assert_called_once()

    async def test_static_fetch_revalidates_safe_redirect_and_strips_cross_origin_auth(
        self,
    ) -> None:
        """A safe cross-origin hop is fetched only after validation without source auth."""
        source = ProxySourceConfig(
            url="https://public.example/proxies",
            format="json",
            auth=("source-user", "source-password"),
            headers={"Authorization": "Bearer source-secret", "Accept": "application/json"},
        )
        fetcher = ProxyFetcher()
        redirect = MagicMock()
        redirect.status_code = 302
        redirect.headers = {"Location": "https://cdn.example/proxies.json"}
        success = MagicMock()
        success.status_code = 200
        success.headers = {}
        success.encoding = "utf-8"
        success.raise_for_status = MagicMock()

        async def body_chunks(*_args: object, **_kwargs: object):
            yield b'[{"host":"203.0.113.10","port":8080}]'

        success.aiter_bytes = body_chunks
        redirect_context = AsyncMock()
        redirect_context.__aenter__.return_value = redirect
        success_context = AsyncMock()
        success_context.__aenter__.return_value = success
        client = MagicMock()
        client.stream.side_effect = [redirect_context, success_context]

        with (
            patch.object(fetcher, "_get_client", new=AsyncMock(return_value=client)),
            patch(
                "proxywhirl.fetchers.fetcher.validate_source_url_safety",
                return_value=(True, ""),
            ) as validate,
            patch("proxywhirl.security.socket.getaddrinfo", _public_getaddrinfo),
        ):
            result = await fetcher.fetch_from_source(source)

        assert result == [
            {
                "host": "203.0.113.10",
                "port": 8080,
                "url": "http://203.0.113.10:8080",
                "protocol": "http",
            }
        ]
        assert any(
            awaited.args[0] == "https://cdn.example/proxies.json"
            for awaited in validate.call_args_list
        )
        first_request, second_request = client.stream.call_args_list
        assert first_request.kwargs["auth"] == ("source-user", "source-password")
        assert first_request.kwargs["headers"]["Authorization"] == "Bearer source-secret"
        assert first_request.kwargs["headers"]["Host"] == "public.example"
        assert second_request.kwargs["auth"] is None
        assert second_request.kwargs["headers"]["Accept"] == "application/json"
        assert "Authorization" not in second_request.kwargs["headers"]
        assert second_request.kwargs["headers"]["Host"] == "cdn.example"


class TestParserInputBoundaries:
    """Reject oversized parser inputs before allocating parsed structures."""

    @pytest.mark.parametrize(
        "parser_type",
        [
            JSONParser,
            CSVParser,
            PlainTextParser,
            GeonodeParser,
        ],
    )
    def test_parser_rejects_oversized_input(self, parser_type: type[object]) -> None:
        """All externally fed parsers enforce their byte cap before parsing."""
        parser = parser_type(max_bytes=32)
        with pytest.raises(ProxyFetchError, match="exceeds.*32.*bytes"):
            parser.parse("x" * 33)

    def test_json_size_check_runs_before_json_decode(self) -> None:
        """Oversized JSON is rejected without invoking the allocating decoder."""
        parser = JSONParser(max_bytes=8)

        with patch("proxywhirl.fetchers.parsers.json.loads") as loads:
            with pytest.raises(ProxyFetchError, match="exceeds.*8.*bytes"):
                parser.parse("[" + " " * 8 + "]")

        loads.assert_not_called()


class TestBrowserOutboundBoundaries:
    """Guard browser navigation, bounded output, and cancellation cleanup."""

    async def test_redirect_hops_are_revalidated_before_browser_navigation(self) -> None:
        """An unsafe redirect hop is aborted before the browser requests it."""
        page = AsyncMock()
        page.close = AsyncMock()
        safe_route = MagicMock()
        safe_route.continue_ = AsyncMock()
        safe_route.abort = AsyncMock()
        blocked_route = MagicMock()
        blocked_route.continue_ = AsyncMock()
        blocked_route.abort = AsyncMock()
        safe_request = MagicMock()
        safe_request.url = "https://public.example/proxies"
        safe_request.is_navigation_request.return_value = True
        blocked_request = MagicMock()
        blocked_request.url = "http://127.0.0.1/admin"
        blocked_request.is_navigation_request.return_value = True

        async def navigate(*_args: object, **_kwargs: object) -> None:
            route_handler = page.route.await_args.args[1]
            await route_handler(safe_route, safe_request)
            await route_handler(blocked_route, blocked_request)
            raise RuntimeError("navigation aborted")

        page.goto = AsyncMock(side_effect=navigate)
        renderer = await _ready_renderer(page)

        with patch(
            "proxywhirl.browser.validate_source_url_safety",
            side_effect=[(True, ""), (False, "Loopback address blocked")],
        ) as validate:
            with pytest.raises(ValueError, match="SSRF protection.*Loopback"):
                await renderer.render("https://public.example/proxies")

        assert validate.call_args_list == [
            call("https://public.example/proxies"),
            call("http://127.0.0.1/admin"),
        ]
        safe_route.continue_.assert_awaited_once()
        safe_route.abort.assert_not_awaited()
        blocked_route.abort.assert_awaited_once()
        blocked_route.continue_.assert_not_awaited()
        page.close.assert_awaited_once()
        assert renderer.pool_size == 1

    async def test_bounded_render_does_not_materialize_unbounded_page_content(self) -> None:
        """A content cap uses an in-page bounded serializer, not page.content()."""
        page = AsyncMock()
        page.goto = AsyncMock()
        page.content = AsyncMock(side_effect=AssertionError("unbounded content requested"))
        page.evaluate = AsyncMock(return_value="<html>bounded</html>")
        page.close = AsyncMock()
        renderer = await _ready_renderer(page)

        html = await renderer.render(
            "https://public.example/proxies",
            max_content_bytes=64,
        )

        assert html == "<html>bounded</html>"
        page.content.assert_not_awaited()
        page.evaluate.assert_awaited_once()
        assert page.evaluate.await_args.args[1] == 64
        assert renderer.pool_size == 1

    async def test_page_close_cancellation_still_releases_context(self) -> None:
        """A cancelled page close must not leak the acquired pooled context."""
        page = AsyncMock()
        page.goto = AsyncMock()
        page.content = AsyncMock(return_value="<html>done</html>")
        page.close = AsyncMock(side_effect=asyncio.CancelledError())
        renderer = await _ready_renderer(page)

        with pytest.raises(asyncio.CancelledError):
            await renderer.render("https://public.example/proxies")

        page.close.assert_awaited_once()
        assert renderer.pool_size == 1

    async def test_close_finishes_all_resources_before_propagating_cancellation(self) -> None:
        """A cancelled context close does not strand other browser resources."""
        renderer = BrowserRenderer(max_contexts=2)
        first_context = AsyncMock()
        second_context = AsyncMock()
        browser = AsyncMock()
        playwright = AsyncMock()
        first_context.close.side_effect = asyncio.CancelledError()
        renderer._is_started = True
        renderer._all_contexts = [first_context, second_context]
        renderer._context = first_context
        renderer._browser = browser
        renderer._playwright = playwright
        renderer._context_pool = asyncio.Queue(maxsize=2)

        with pytest.raises(asyncio.CancelledError):
            await renderer.close()

        first_context.close.assert_awaited_once()
        second_context.close.assert_awaited_once()
        browser.close.assert_awaited_once()
        playwright.stop.assert_awaited_once()
        assert renderer._is_started is False
        assert renderer._all_contexts == []
        assert renderer._browser is None
        assert renderer._playwright is None

    async def test_start_cancellation_closes_partially_created_resources(self) -> None:
        """Cancellation during pool creation closes prior contexts and browser clients."""
        renderer = BrowserRenderer(max_contexts=2)
        playwright = MagicMock()
        browser = AsyncMock()
        first_context = AsyncMock()
        playwright.chromium.launch = AsyncMock(return_value=browser)
        playwright.stop = AsyncMock()
        browser.new_context = AsyncMock(side_effect=[first_context, asyncio.CancelledError()])
        browser.close = AsyncMock()
        first_context.close = AsyncMock()
        playwright_manager = MagicMock()
        playwright_manager.start = AsyncMock(return_value=playwright)
        playwright_module = MagicMock()
        playwright_module.async_playwright.return_value = playwright_manager

        with (
            patch.dict("sys.modules", {"playwright.async_api": playwright_module}),
            pytest.raises(asyncio.CancelledError),
        ):
            await renderer.start()

        first_context.close.assert_awaited_once()
        browser.close.assert_awaited_once()
        playwright.stop.assert_awaited_once()
        assert renderer._is_started is False
        assert renderer._all_contexts == []
        assert renderer._browser is None
        assert renderer._playwright is None
