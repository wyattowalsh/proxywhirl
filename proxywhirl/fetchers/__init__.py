"""Proxy fetching, parsing, and validation (package facade)."""

from __future__ import annotations

from proxywhirl.fetchers.fetcher import (
    ProxyFetcher,
    _is_retryable_http_error,
    _wait_with_retry_after,
)
from proxywhirl.fetchers.parsers import (
    CSVParser,
    GeonodeParser,
    HTMLTableParser,
    JSONParser,
    PlainTextParser,
    deduplicate_proxies,
    normalize_parsed_proxy_rows,
)
from proxywhirl.fetchers.shared import (
    DEFAULT_ANONYMITY_TEST_URL,
    FETCH_MAX_RESPONSE_BYTES,
    HTML_PARSE_MAX_BYTES,
    HTML_PARSE_MAX_ROWS,
    PERIODIC_REFRESH_MAX_CONSECUTIVE_ERRORS,
    SOCKS_AVAILABLE,
    AsyncProxyTransport,
)
from proxywhirl.fetchers.validator import ProxyValidator, ValidationResult
from proxywhirl.models import ProxySourceConfig, RenderMode
from proxywhirl.security import validate_proxy_url_safety
from proxywhirl.utils import parse_proxy_url

__all__ = [
    "AsyncProxyTransport",
    "CSVParser",
    "DEFAULT_ANONYMITY_TEST_URL",
    "FETCH_MAX_RESPONSE_BYTES",
    "GeonodeParser",
    "HTMLTableParser",
    "HTML_PARSE_MAX_BYTES",
    "HTML_PARSE_MAX_ROWS",
    "JSONParser",
    "PERIODIC_REFRESH_MAX_CONSECUTIVE_ERRORS",
    "PlainTextParser",
    "ProxyFetcher",
    "ProxySourceConfig",
    "ProxyValidator",
    "RenderMode",
    "SOCKS_AVAILABLE",
    "ValidationResult",
    "_is_retryable_http_error",
    "_wait_with_retry_after",
    "deduplicate_proxies",
    "normalize_parsed_proxy_rows",
    "parse_proxy_url",
    "validate_proxy_url_safety",
]
