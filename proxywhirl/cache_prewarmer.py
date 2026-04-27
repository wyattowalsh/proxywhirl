"""Cache prewarming utilities for loading cache on startup.

Features:
- Multi-strategy cache population
- Background prewarming
- Progress tracking
- Error handling and retry
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Callable

from loguru import logger


@dataclass
class PreheatStrategy:
    """Strategy for prewarming cache."""

    name: str
    description: str
    priority: int = 0  # Higher = higher priority


@dataclass
class PreheatProgress:
    """Progress tracking for cache prewarming."""

    total_items: int
    loaded_items: int = 0
    failed_items: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None

    @property
    def elapsed_seconds(self) -> float:
        """Elapsed time in seconds."""
        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def success_rate(self) -> float:
        """Percentage of items loaded successfully."""
        if self.total_items == 0:
            return 0.0

        return (self.loaded_items / self.total_items) * 100

    @property
    def is_complete(self) -> bool:
        """Whether prewarming is complete."""
        return self.loaded_items + self.failed_items >= self.total_items

    def mark_complete(self) -> None:
        """Mark prewarming as complete."""
        self.end_time = time.time()


class PrewarmSource(ABC):
    """Abstract base for cache prewarming sources."""

    @abstractmethod
    async def fetch_items(self) -> AsyncIterator[tuple[str, Any]]:
        """Fetch items to preload into cache.

        Yields:
            (key, value) tuples
        """

    @property
    @abstractmethod
    def strategy(self) -> PreheatStrategy:
        """Get prewarming strategy metadata."""


class ProxyListPrewarmSource(PrewarmSource):
    """Prewarming source for proxy lists."""

    def __init__(
        self,
        fetcher: Callable[[], Any],
        category: str = "default",
    ):
        """Initialize proxy list prewarming source.

        Args:
            fetcher: Async callable that returns proxy list
            category: Category of proxies (e.g., 'http', 'socks5')
        """
        self.fetcher = fetcher
        self.category = category

    async def fetch_items(self) -> AsyncIterator[tuple[str, Any]]:
        """Fetch proxies and yield as cache items."""
        try:
            proxies = await self.fetcher()

            for idx, proxy in enumerate(proxies):
                key = f"proxy:{self.category}:{idx}"
                yield (key, proxy)

        except Exception as e:
            logger.error(
                "Error fetching proxies for prewarming",
                category=self.category,
                error=e,
            )

    @property
    def strategy(self) -> PreheatStrategy:
        """Get strategy metadata."""
        return PreheatStrategy(
            name=f"proxy-list-{self.category}",
            description=f"Preload {self.category} proxies into cache",
            priority=10,
        )


class GeolocationCachePrewarmSource(PrewarmSource):
    """Prewarming source for geolocation data."""

    def __init__(
        self,
        fetcher: Callable[[list[str]], Any],
        ips: list[str],
    ):
        """Initialize geolocation prewarming source.

        Args:
            fetcher: Async callable that returns geolocation data
            ips: List of IPs to preload geo data for
        """
        self.fetcher = fetcher
        self.ips = ips

    async def fetch_items(self) -> AsyncIterator[tuple[str, Any]]:
        """Fetch geolocation data and yield as cache items."""
        try:
            geo_data = await self.fetcher(self.ips)

            for ip, data in geo_data.items():
                key = f"geo:{ip}"
                yield (key, data)

        except Exception as e:
            logger.error(
                "Error fetching geolocation data for prewarming",
                error=e,
            )

    @property
    def strategy(self) -> PreheatStrategy:
        """Get strategy metadata."""
        return PreheatStrategy(
            name="geolocation-cache",
            description="Preload geolocation data into cache",
            priority=5,
        )


class StaticDataPrewarmSource(PrewarmSource):
    """Prewarming source for static data."""

    def __init__(
        self,
        data: dict[str, Any],
        prefix: str = "static",
    ):
        """Initialize static data prewarming source.

        Args:
            data: Dictionary of static data to preload
            prefix: Key prefix for cached items
        """
        self.data = data
        self.prefix = prefix

    async def fetch_items(self) -> AsyncIterator[tuple[str, Any]]:
        """Yield static data items."""
        for key, value in self.data.items():
            cache_key = f"{self.prefix}:{key}"
            yield (cache_key, value)

    @property
    def strategy(self) -> PreheatStrategy:
        """Get strategy metadata."""
        return PreheatStrategy(
            name="static-data",
            description="Preload static configuration data",
            priority=20,  # Highest priority
        )


class CachePrewarmer:
    """Manages cache prewarming on startup."""

    def __init__(
        self,
        cache_set: Callable[[str, Any], Any],
        max_concurrent: int = 10,
    ):
        """Initialize cache prewarmer.

        Args:
            cache_set: Async callable to set cache value (key, value)
            max_concurrent: Maximum concurrent cache set operations
        """
        self.cache_set = cache_set
        self.max_concurrent = max_concurrent
        self.sources: list[PrewarmSource] = []
        self.progress: PreheatProgress | None = None

    def add_source(self, source: PrewarmSource) -> None:
        """Add a prewarming source.

        Args:
            source: PrewarmSource instance
        """
        self.sources.append(source)
        self.sources.sort(key=lambda s: s.strategy.priority, reverse=True)

    async def preheat(
        self,
        on_progress: Callable[[PreheatProgress], None] | None = None,
    ) -> PreheatProgress:
        """Execute cache prewarming.

        Args:
            on_progress: Optional callback for progress updates

        Returns:
            Prewarming progress details
        """
        # Count total items
        total_items = 0
        all_items = []

        for source in self.sources:
            async for key, value in source.fetch_items():
                all_items.append((key, value))
                total_items += 1

        self.progress = PreheatProgress(total_items=total_items)

        # Load items concurrently
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def load_item(key: str, value: Any) -> None:
            """Load single item with concurrency limit."""
            async with semaphore:
                try:
                    await self.cache_set(key, value)
                    self.progress.loaded_items += 1

                    if on_progress:
                        on_progress(self.progress)

                except Exception as e:
                    self.progress.failed_items += 1
                    logger.error(
                        "Error prewarming cache item",
                        key=key,
                        error=e,
                    )

                    if on_progress:
                        on_progress(self.progress)

        # Load all items
        tasks = [load_item(key, value) for key, value in all_items]
        await asyncio.gather(*tasks)

        self.progress.mark_complete()

        logger.info(
            "Cache prewarming complete",
            loaded=self.progress.loaded_items,
            failed=self.progress.failed_items,
            elapsed_seconds=self.progress.elapsed_seconds,
        )

        return self.progress

    async def preheat_background(
        self,
        on_progress: Callable[[PreheatProgress], None] | None = None,
    ) -> asyncio.Task:
        """Execute cache prewarming in background task.

        Args:
            on_progress: Optional callback for progress updates

        Returns:
            Asyncio Task for prewarming
        """

        async def _run():
            return await self.preheat(on_progress)

        return asyncio.create_task(_run())

    def get_progress(self) -> PreheatProgress | None:
        """Get current prewarming progress."""
        return self.progress

    def get_sources_summary(self) -> dict[str, Any]:
        """Get summary of prewarming sources."""
        return {
            "count": len(self.sources),
            "sources": [
                {
                    "name": source.strategy.name,
                    "description": source.strategy.description,
                    "priority": source.strategy.priority,
                }
                for source in self.sources
            ],
        }
