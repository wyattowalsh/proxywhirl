"""Connect-time DNS pin tests (W1-R4 / fact w1-03).

True pin: outbound connect uses the address from a single preflight resolution.
A second DNS lookup is not a pin; httpx must be given an IP URL.
"""

from __future__ import annotations

import socket
from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import urlsplit

import pytest

from proxywhirl.security import pin_outbound_url


def _getaddrinfo_result(ip: str) -> list[tuple[object, ...]]:
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    return [(family, socket.SOCK_STREAM, 0, "", (ip, 0))]


def _rebinding_getaddrinfo(public_ip: str = "8.8.8.8", rebound_ip: str = "127.0.0.1"):
    """First getaddrinfo call returns ``public_ip``; later calls return ``rebound_ip``."""
    state = {"n": 0}

    def fake_getaddrinfo(*_args: object, **_kwargs: object) -> list[tuple[object, ...]]:
        state["n"] += 1
        if state["n"] == 1:
            return _getaddrinfo_result(public_ip)
        return _getaddrinfo_result(rebound_ip)

    fake_getaddrinfo.state = state  # type: ignore[attr-defined]
    return fake_getaddrinfo


class TestPinOutboundUrl:
    """Unit tests for :func:`pin_outbound_url`."""

    def test_public_ip_literal_pins_without_dns(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def boom(*_args: object, **_kwargs: object) -> list[object]:
            raise AssertionError("getaddrinfo must not run for IP literals")

        monkeypatch.setattr("proxywhirl.security.socket.getaddrinfo", boom)
        pin, reason = pin_outbound_url("http://8.8.8.8:8080/status", purpose="proxy")
        assert reason == ""
        assert pin is not None
        assert pin.ip == "8.8.8.8"
        assert pin.hostname == "8.8.8.8"
        assert urlsplit(pin.pinned_url).hostname == "8.8.8.8"
        assert pin.host_header == "8.8.8.8:8080"
        assert pin.extensions == {"sni_hostname": "8.8.8.8"}

    def test_loopback_ip_pin_fails(self) -> None:
        pin, reason = pin_outbound_url("http://127.0.0.1:8080", purpose="proxy")
        assert pin is None
        assert "loopback" in reason.lower()

    def test_private_ip_pin_fails(self) -> None:
        pin, reason = pin_outbound_url("http://192.168.1.1:8080", purpose="proxy")
        assert pin is None
        assert "private" in reason.lower()

    def test_metadata_ip_pin_fails(self) -> None:
        pin, reason = pin_outbound_url("http://169.254.169.254/latest", purpose="proxy")
        assert pin is None
        assert "metadata" in reason.lower()

    def test_ipv6_literal_is_bracketed_in_pinned_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def boom(*_args: object, **_kwargs: object) -> list[object]:
            raise AssertionError("getaddrinfo must not run for IP literals")

        monkeypatch.setattr("proxywhirl.security.socket.getaddrinfo", boom)
        ipv6 = "2001:4860:4860::8888"
        pin, reason = pin_outbound_url(f"http://[{ipv6}]:8080/path", purpose="proxy")
        assert reason == ""
        assert pin is not None
        assert pin.ip == ipv6
        assert urlsplit(pin.pinned_url).hostname == ipv6
        assert f"[{ipv6}]" in pin.pinned_url

    def test_userinfo_path_query_fragment_preserved(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "proxywhirl.security.socket.getaddrinfo",
            lambda *_args, **_kwargs: _getaddrinfo_result("8.8.8.8"),
        )
        original = "http://user:p%40ss@proxy.example.test:8080/v1?x=1#frag"
        pin, reason = pin_outbound_url(original, purpose="proxy")
        assert pin is not None
        assert reason == ""
        assert pin.ip == "8.8.8.8"
        parsed = urlsplit(pin.pinned_url)
        assert parsed.hostname == "8.8.8.8"
        assert parsed.username == "user"
        assert "user:p%40ss@8.8.8.8:8080" in pin.pinned_url
        assert parsed.path == "/v1"
        assert parsed.query == "x=1"
        assert parsed.fragment == "frag"
        assert parsed.port == 8080

    def test_rebinding_uses_first_resolution_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fake = _rebinding_getaddrinfo()
        monkeypatch.setattr("proxywhirl.security.socket.getaddrinfo", fake)
        pin, reason = pin_outbound_url("http://public.example.test:8080", purpose="proxy")
        assert pin is not None
        assert reason == ""
        assert pin.ip == "8.8.8.8"
        assert urlsplit(pin.pinned_url).hostname == "8.8.8.8"
        assert "127.0.0.1" not in pin.pinned_url

        monkeypatch.setattr(
            "proxywhirl.security.socket.getaddrinfo",
            lambda *_args, **_kwargs: _getaddrinfo_result("127.0.0.1"),
        )
        assert pin.ip == "8.8.8.8"
        assert urlsplit(pin.pinned_url).hostname == "8.8.8.8"

    def test_pin_does_not_reresolve_after_ip_selected(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake = _rebinding_getaddrinfo()
        monkeypatch.setattr("proxywhirl.security.socket.getaddrinfo", fake)
        pin, _reason = pin_outbound_url("https://public.example.test/path", purpose="source")
        assert pin is not None
        lookups_at_pin = fake.state["n"]  # type: ignore[attr-defined]
        _ = (pin.pinned_url, pin.host_header, pin.extensions)
        assert fake.state["n"] == lookups_at_pin  # type: ignore[attr-defined]
        assert pin.host_header == "public.example.test"
        assert pin.extensions == {"sni_hostname": "public.example.test"}

    def test_mixed_records_in_one_lookup_fail_closed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "proxywhirl.security.socket.getaddrinfo",
            lambda *_args, **_kwargs: [
                (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("8.8.8.8", 0)),
                (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 0)),
            ],
        )
        pin, reason = pin_outbound_url("http://public.example.test:8080", purpose="proxy")
        assert pin is None
        assert "loopback" in reason.lower()

    def test_source_purpose_rejects_non_http_scheme(self) -> None:
        pin, reason = pin_outbound_url("file:///etc/passwd", purpose="source")
        assert pin is None
        assert "scheme" in reason.lower()


class TestFetcherConnectsToPinnedIp:
    """Fetcher must stream the pinned IP URL, not the hostname."""

    @pytest.mark.asyncio
    async def test_stream_uses_pinned_ip_and_preserves_host(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from proxywhirl.fetchers.fetcher import ProxyFetcher

        fake = _rebinding_getaddrinfo()
        monkeypatch.setattr("proxywhirl.security.socket.getaddrinfo", fake)
        monkeypatch.setattr(
            "proxywhirl.fetchers.fetcher.validate_source_url_safety",
            lambda _url: (True, ""),
        )

        async def _aiter_bytes(chunk_size: int = 65536) -> AsyncIterator[bytes]:
            yield b"ok"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.encoding = "utf-8"
        mock_response.raise_for_status = MagicMock()
        mock_response.aiter_bytes = _aiter_bytes
        stream_cm = AsyncMock()
        stream_cm.__aenter__.return_value = mock_response
        stream_cm.__aexit__.return_value = None
        client = MagicMock()
        client.stream = MagicMock(return_value=stream_cm)

        fetcher = ProxyFetcher()
        body = await fetcher._fetch_static_content(
            client,
            "https://public.example.test/proxies",
            headers={"Accept": "text/plain"},
            auth=None,
        )
        assert body == "ok"
        args, kwargs = client.stream.call_args
        assert args[0] == "GET"
        streamed_url = args[1]
        assert urlsplit(streamed_url).hostname == "8.8.8.8"
        assert "127.0.0.1" not in streamed_url
        assert "public.example.test" not in streamed_url
        assert kwargs["headers"]["Host"] == "public.example.test"
        assert kwargs["headers"]["Accept"] == "text/plain"
        assert kwargs["extensions"]["sni_hostname"] == "public.example.test"


class TestSourceValidationConnectsToPinnedIp:
    """Source-list validation must stream the pinned IP, not the hostname."""

    @pytest.mark.asyncio
    async def test_validation_stream_uses_pinned_ip(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from proxywhirl.models import ProxyFormat, ProxySourceConfig
        from proxywhirl.sources import _fetch_validation_content

        fake = _rebinding_getaddrinfo()
        monkeypatch.setattr("proxywhirl.security.socket.getaddrinfo", fake)
        monkeypatch.setattr(
            "proxywhirl.sources.validate_source_url_safety",
            lambda _url: (True, ""),
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.url = "http://8.8.8.8/list"
        mock_response.encoding = "utf-8"
        mock_response.aiter_bytes = MagicMock()
        stream_cm = AsyncMock()
        stream_cm.__aenter__.return_value = mock_response
        stream_cm.__aexit__.return_value = None
        client = MagicMock()
        client.stream = MagicMock(return_value=stream_cm)

        async def _empty_read(*_args: object, **_kwargs: object) -> tuple[str, int, None]:
            return "", 0, None

        monkeypatch.setattr("proxywhirl.sources._read_validation_content", _empty_read)
        monkeypatch.setattr(
            "proxywhirl.sources._count_parseable_proxies",
            lambda *_args, **_kwargs: 0,
        )

        source = ProxySourceConfig(
            url="https://public.example.test/list",
            format=ProxyFormat.PLAIN_TEXT,
        )
        await _fetch_validation_content(source, timeout=1.0, client=client)
        streamed_url = client.stream.call_args.args[1]
        assert urlsplit(streamed_url).hostname == "8.8.8.8"
        assert "public.example.test" not in streamed_url
        assert client.stream.call_args.kwargs["headers"]["Host"] == "public.example.test"
        assert client.stream.call_args.kwargs["extensions"]["sni_hostname"] == "public.example.test"


class TestValidatorConnectsToPinnedIp:
    """Validator TCP and HTTP clients must target the pinned IP."""

    @pytest.mark.asyncio
    async def test_validate_opens_and_proxies_pinned_ip(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from proxywhirl.fetchers.validator import ProxyValidator

        fake = _rebinding_getaddrinfo()
        monkeypatch.setattr("proxywhirl.security.socket.getaddrinfo", fake)
        monkeypatch.setattr(
            "proxywhirl.fetchers.validate_proxy_url_safety",
            lambda _url, *args, **kwargs: (True, ""),
        )

        mock_writer = AsyncMock()
        mock_writer.close = MagicMock()
        mock_writer.wait_closed = AsyncMock()
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with (
            patch(
                "asyncio.open_connection",
                new=AsyncMock(return_value=(AsyncMock(), mock_writer)),
            ) as mock_open,
            patch("httpx.AsyncClient", return_value=mock_client) as mock_client_cls,
        ):
            validator = ProxyValidator()
            result = await validator.validate({"url": "http://public.example.test:8080"})

        assert result.is_valid is True
        mock_open.assert_awaited()
        opened_host = mock_open.await_args.args[0]
        opened_port = mock_open.await_args.args[1]
        assert opened_host == "8.8.8.8"
        assert opened_port == 8080
        proxy_kw = mock_client_cls.call_args.kwargs["proxy"]
        assert urlsplit(proxy_kw).hostname == "8.8.8.8"
        assert "127.0.0.1" not in proxy_kw
        assert "public.example.test" not in proxy_kw
