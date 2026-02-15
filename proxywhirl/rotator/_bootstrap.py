"""
Internal lazy bootstrap helpers for empty proxy pools.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from loguru import logger

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import Proxy, ProxyPool, ProxySource, ProxySourceConfig
from proxywhirl.sources import ALL_SOURCES, fetch_all_sources
from proxywhirl.utils import create_proxy_from_url


def _coerce_proxy(proxy_data: dict[str, Any]) -> Proxy | None:
    """Convert fetched proxy payload to Proxy model."""
    proxy_url = proxy_data.get("url")
    if not isinstance(proxy_url, str) or not proxy_url:
        return None

    try:
        return create_proxy_from_url(proxy_url, source=ProxySource.FETCHED)
    except ValueError:
        return None


async def _fetch_bootstrap_candidates(
    *,
    validate: bool = True,
    timeout: int = 10,
    max_concurrent: int = 100,
    max_proxies: int | None = None,
    sources: list[ProxySourceConfig] | None = None,
) -> list[Proxy]:
    """Fetch and convert bootstrap proxy candidates from built-in sources."""
    fetched = await fetch_all_sources(
        validate=validate,
        timeout=timeout,
        max_concurrent=max_concurrent,
        sources=sources if sources is not None else ALL_SOURCES,
    )
    if max_proxies is not None:
        fetched = fetched[:max_proxies]

    candidates = [proxy for proxy in (_coerce_proxy(item) for item in fetched) if proxy is not None]
    return candidates


def _raise_bootstrap_empty_error() -> None:
    """Raise a clear pool-empty bootstrap error."""
    raise ProxyPoolEmptyError(
        "Lazy auto-fetch bootstrap yielded zero proxies from built-in public sources"
    )


async def bootstrap_pool_if_empty_async(
    *,
    pool: ProxyPool,
    add_proxy: Callable[[Proxy], Awaitable[None]],
    validate: bool = True,
    timeout: int = 10,
    max_concurrent: int = 100,
    max_proxies: int | None = None,
    sources: list[ProxySourceConfig] | None = None,
) -> int:
    """
    Populate an empty pool by fetching from built-in sources.

    Returns:
        Number of proxies added to the pool.
    """
    if pool.size > 0:
        return 0

    candidates = await _fetch_bootstrap_candidates(
        validate=validate,
        timeout=timeout,
        max_concurrent=max_concurrent,
        max_proxies=max_proxies,
        sources=sources,
    )
    if not candidates:
        _raise_bootstrap_empty_error()

    added = 0
    for proxy in candidates:
        try:
            await add_proxy(proxy)
            added += 1
        except Exception as exc:
            logger.debug("Skipping bootstrap proxy during async pool load", error=str(exc))

    if added == 0:
        _raise_bootstrap_empty_error()

    return added


def bootstrap_pool_if_empty_sync(
    *,
    pool: ProxyPool,
    add_proxy: Callable[[Proxy], None],
    validate: bool = True,
    timeout: int = 10,
    max_concurrent: int = 100,
    max_proxies: int | None = None,
    sources: list[ProxySourceConfig] | None = None,
) -> int:
    """
    Synchronous wrapper for bootstrap_pool_if_empty_async.

    Returns:
        Number of proxies added to the pool.
    """
    if pool.size > 0:
        return 0

    candidates = asyncio.run(
        _fetch_bootstrap_candidates(
            validate=validate,
            timeout=timeout,
            max_concurrent=max_concurrent,
            max_proxies=max_proxies,
            sources=sources,
        )
    )
    if not candidates:
        _raise_bootstrap_empty_error()

    added = 0
    for proxy in candidates:
        try:
            add_proxy(proxy)
            added += 1
        except Exception as exc:
            logger.debug("Skipping bootstrap proxy during sync pool load", error=str(exc))

    if added == 0:
        _raise_bootstrap_empty_error()

    return added
