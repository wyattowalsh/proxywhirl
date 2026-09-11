"""Shared constants and optional SOCKS transport for fetchers."""

from __future__ import annotations

from loguru import logger

FETCH_MAX_RESPONSE_BYTES = 256_000


HTML_PARSE_MAX_BYTES = 2_000_000


HTML_PARSE_MAX_ROWS = 10_000


DEFAULT_ANONYMITY_TEST_URL = "https://httpbin.org/anything"


PERIODIC_REFRESH_MAX_CONSECUTIVE_ERRORS = 3


try:
    from httpx_socks import AsyncProxyTransport

    SOCKS_AVAILABLE = True
except ImportError:
    AsyncProxyTransport = None  # type: ignore[misc, assignment]
    SOCKS_AVAILABLE = False
    logger.debug(
        "httpx-socks not installed. SOCKS4/SOCKS5 proxy validation will not work. "
        "Install with: uv sync or add httpx-socks to your dependencies"
    )
