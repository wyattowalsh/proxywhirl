"""
Internal lazy bootstrap helpers for empty proxy pools.
"""

from __future__ import annotations

import asyncio
import random
import sys
import threading
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from loguru import logger

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    BootstrapConfig,
    Proxy,
    ProxyPool,
    ProxySource,
    ProxySourceConfig,
)
from proxywhirl.sources import ALL_SOURCES, fetch_all_sources
from proxywhirl.utils import create_proxy_from_url

T = TypeVar("T")


def _sample_sources(
    sources: list[ProxySourceConfig] | None,
    sample_size: int,
) -> list[ProxySourceConfig]:
    """Select sources for bootstrap.

    If *sources* is an explicit list, return it as-is.
    Otherwise randomly sample *sample_size* **enabled** sources from ALL_SOURCES
    so each user hits a different subset, distributing load.
    """
    if sources is not None:
        return sources

    enabled = [s for s in ALL_SOURCES if s.enabled]
    if not enabled:
        return []

    k = min(sample_size, len(enabled))
    return random.sample(enabled, k)


def _should_show_progress(show_progress: bool | None) -> bool:
    """Return whether to display Rich progress bars.

    Explicit True/False is respected; None auto-detects a TTY on stderr.
    """
    if show_progress is not None:
        return show_progress
    return sys.stderr.isatty()


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
    config: BootstrapConfig,
) -> tuple[list[Proxy], int]:
    """Fetch and convert bootstrap proxy candidates using *config*.

    Returns:
        Tuple of (candidates, sources_count).
    """
    selected_sources = _sample_sources(config.sources, config.sample_size)
    if not selected_sources:
        return [], 0

    show_progress = _should_show_progress(config.show_progress)

    # Track stats for summary
    total_sources = len(selected_sources)
    proxies_found = 0
    valid_count = 0

    # -- Rich progress callbacks (no-ops when progress is hidden) -----------
    progress_ctx: Any = None
    fetch_task_id: Any = None
    validate_task_id: Any = None

    if show_progress:
        try:
            from rich.console import Console
            from rich.progress import (
                BarColumn,
                MofNCompleteColumn,
                Progress,
                SpinnerColumn,
                TaskProgressColumn,
                TextColumn,
                TimeElapsedColumn,
            )

            console = Console(stderr=True)
            progress_ctx = Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                MofNCompleteColumn(),
                TextColumn("•"),
                TimeElapsedColumn(),
                TextColumn("{task.fields[status]}"),
                console=console,
                transient=True,
            )
        except ImportError:
            pass

    def _fetch_cb(completed: int, total: int, found: int) -> None:
        nonlocal proxies_found
        proxies_found = found
        if progress_ctx is not None and fetch_task_id is not None:
            progress_ctx.update(
                fetch_task_id,
                completed=completed,
                status=f"[cyan]{proxies_found:,} found[/cyan]",
            )

    def _validate_cb(completed: int, total: int, valid: int) -> None:
        nonlocal valid_count
        valid_count = valid
        if progress_ctx is not None and validate_task_id is not None:
            progress_ctx.update(
                validate_task_id,
                completed=completed,
                total=total,
                status=f"[green]{valid:,} valid[/green]",
            )

    start_time = time.monotonic()

    try:
        if progress_ctx is not None:
            progress_ctx.start()
            fetch_task_id = progress_ctx.add_task(
                "Fetching proxies",
                total=total_sources,
                status="[cyan]0 found[/cyan]",
            )
            if config.validate_proxies:
                validate_task_id = progress_ctx.add_task(
                    "Validating proxies",
                    total=0,
                    status="[yellow]waiting[/yellow]",
                )
        fetched = await fetch_all_sources(
            validate=config.validate_proxies,
            timeout=config.timeout,
            max_concurrent=config.max_concurrent,
            sources=selected_sources,
            fetch_progress_callback=_fetch_cb if show_progress else None,
            validate_progress_callback=_validate_cb if show_progress else None,
        )
    finally:
        if progress_ctx is not None:
            progress_ctx.stop()

    elapsed = time.monotonic() - start_time

    candidates = [proxy for proxy in (_coerce_proxy(item) for item in fetched) if proxy is not None]

    # Print a one-line summary to stderr when on a TTY
    if show_progress:
        if config.validate_proxies and valid_count > 0:
            summary = (
                f"Ready: {len(candidates)} proxies "
                f"({proxies_found:,} fetched, {valid_count:,} validated) "
                f"from {total_sources} sources ({elapsed:.1f}s)"
            )
        else:
            summary = (
                f"Ready: {len(candidates)} proxies from {total_sources} sources ({elapsed:.1f}s)"
            )
        # Write directly to stderr to avoid loguru formatting
        try:
            sys.stderr.write(summary + "\n")
            sys.stderr.flush()
        except OSError:
            pass

    # Always log bootstrap result (visible in non-TTY environments)
    logger.info(
        "Bootstrap complete: {} proxies from {} sources ({:.1f}s)",
        len(candidates),
        total_sources,
        elapsed,
    )

    return candidates, total_sources


def _raise_bootstrap_empty_error(
    *,
    sources_count: int = 0,
    sources_were_explicit: bool = False,
) -> None:
    """Raise a context-aware pool-empty bootstrap error."""
    if sources_count == 0 and sources_were_explicit:
        msg = (
            "No proxy sources configured. Use sources=None for built-in "
            "defaults, or provide a non-empty list of ProxySourceConfig."
        )
    else:
        msg = (
            f"Bootstrap fetched 0 usable proxies from {sources_count} sources. "
            "Sources may be temporarily unavailable \u2014 try again (random sampling "
            "hits different sources each time), increase sample_size, or provide "
            "working sources explicitly."
        )
    raise ProxyPoolEmptyError(msg)


def _run_async_from_sync(coro_factory: Callable[[], Awaitable[T]]) -> T:
    """
    Run an async callable from synchronous code, including active-loop environments.

    When called from environments that already have an event loop running
    (e.g. Jupyter/Colab), this executes the coroutine in a short-lived worker thread
    to avoid ``asyncio.run() cannot be called from a running event loop``.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro_factory())

    result: list[T] = []
    errors: list[BaseException] = []

    def _runner() -> None:
        try:
            result.append(asyncio.run(coro_factory()))
        except BaseException as exc:  # pragma: no cover - surfaced in caller
            errors.append(exc)

    thread = threading.Thread(target=_runner, daemon=True, name="proxywhirl-bootstrap-runner")
    thread.start()
    thread.join()

    if errors:
        raise errors[0]
    if not result:
        raise RuntimeError("Bootstrap runner exited without returning a result")
    return result[0]


async def bootstrap_pool_if_empty_async(
    *,
    pool: ProxyPool,
    add_proxy: Callable[[Proxy], Awaitable[None]],
    config: BootstrapConfig | None = None,
    # Legacy keyword args (used when config is None)
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

    if config is not None and not config.enabled:
        return 0

    if config is None:
        config = BootstrapConfig(
            sources=sources,
            sample_size=10,
            validate_proxies=validate,
            timeout=timeout,
            max_concurrent=max_concurrent,
        )

    sources_were_explicit = config.sources is not None

    candidates, sources_count = await _fetch_bootstrap_candidates(config=config)

    # Apply max_proxies limit (from config or legacy kwarg)
    effective_max = config.max_proxies if config.max_proxies is not None else max_proxies
    if effective_max is not None:
        candidates = candidates[:effective_max]

    if not candidates:
        _raise_bootstrap_empty_error(
            sources_count=sources_count,
            sources_were_explicit=sources_were_explicit,
        )

    added = 0
    for proxy in candidates:
        try:
            await add_proxy(proxy)
            added += 1
        except Exception as exc:
            logger.debug("Skipping bootstrap proxy during async pool load", error=str(exc))

    if added == 0:
        _raise_bootstrap_empty_error(
            sources_count=sources_count,
            sources_were_explicit=sources_were_explicit,
        )

    return added


def bootstrap_pool_if_empty_sync(
    *,
    pool: ProxyPool,
    add_proxy: Callable[[Proxy], None],
    config: BootstrapConfig | None = None,
    # Legacy keyword args (used when config is None)
    validate: bool = True,
    timeout: int = 10,
    max_concurrent: int = 100,
    max_proxies: int | None = None,
    sources: list[ProxySourceConfig] | None = None,
) -> int:
    """
    Synchronous wrapper that populates an empty pool from built-in sources.

    Returns:
        Number of proxies added to the pool.
    """
    if pool.size > 0:
        return 0

    if config is not None and not config.enabled:
        return 0

    if config is None:
        config = BootstrapConfig(
            sources=sources,
            sample_size=10,
            validate_proxies=validate,
            timeout=timeout,
            max_concurrent=max_concurrent,
        )

    sources_were_explicit = config.sources is not None

    candidates, sources_count = _run_async_from_sync(
        lambda: _fetch_bootstrap_candidates(config=config)
    )

    # Apply max_proxies limit (from config or legacy kwarg)
    effective_max = config.max_proxies if config.max_proxies is not None else max_proxies
    if effective_max is not None:
        candidates = candidates[:effective_max]

    if not candidates:
        _raise_bootstrap_empty_error(
            sources_count=sources_count,
            sources_were_explicit=sources_were_explicit,
        )

    added = 0
    for proxy in candidates:
        try:
            add_proxy(proxy)
            added += 1
        except Exception as exc:
            logger.debug("Skipping bootstrap proxy during sync pool load", error=str(exc))

    if added == 0:
        _raise_bootstrap_empty_error(
            sources_count=sources_count,
            sources_were_explicit=sources_were_explicit,
        )

    return added
