"""Datasource polling for automatic proxy source updates.

Implements background polling to periodically fetch proxies from configured
sources without manual intervention.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable

from loguru import logger

from proxywhirl.fetchers import ProxyFetcher


class PollingStrategy(str, Enum):
    """Polling frequency strategy."""

    FIXED = "fixed"  # Fixed interval
    EXPONENTIAL_BACKOFF = "exponential"  # Exponential backoff on failure
    ADAPTIVE = "adaptive"  # Adjust based on change rate


@dataclass
class PollingConfig:
    """Configuration for datasource polling."""

    enabled: bool = True
    interval_seconds: int = 3600  # Poll every hour by default
    strategy: PollingStrategy = PollingStrategy.FIXED
    max_backoff_seconds: int = 86400  # Max 1 day backoff
    backoff_factor: float = 2.0  # For exponential backoff
    timeout_seconds: int = 30  # Request timeout
    failure_threshold: int = 3  # Failures before backoff
    adaptive_min_interval: int = 300  # Min 5 minutes for adaptive
    adaptive_max_interval: int = 86400  # Max 1 day for adaptive
    adaptive_change_rate_threshold: float = 0.1  # 10% change triggers faster poll


@dataclass
class PollingStats:
    """Statistics for a polling task."""

    source_name: str
    last_poll_time: datetime | None = None
    next_poll_time: datetime | None = None
    poll_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    last_error: str | None = None
    proxies_fetched: int = 0
    last_change_rate: float = 0.0


class DatasourcePoller:
    """Manages polling of multiple proxy sources."""

    def __init__(self, config: PollingConfig | None = None):
        """Initialize poller.

        Args:
            config: Polling configuration
        """
        self.config = config or PollingConfig()
        self.stats: dict[str, PollingStats] = {}
        self._tasks: dict[str, asyncio.Task] = {}
        self._running = False
        self._callbacks: list[Callable[[str, list], None]] = []

    def register_source(self, source_name: str) -> None:
        """Register a proxy source for polling.

        Args:
            source_name: Name of the proxy source
        """
        if source_name not in self.stats:
            self.stats[source_name] = PollingStats(source_name=source_name)

    def add_callback(self, callback: Callable[[str, list], None]) -> None:
        """Register callback for when proxies are fetched.

        Callback receives (source_name, proxies) as arguments.

        Args:
            callback: Function to call with fetched proxies
        """
        self._callbacks.append(callback)

    def _calculate_next_poll_time(self, source_name: str, next_interval: int) -> datetime:
        """Calculate when next poll should happen.

        Args:
            source_name: Name of source
            next_interval: Interval in seconds

        Returns:
            Datetime of next poll
        """
        return datetime.now() + timedelta(seconds=next_interval)

    def _get_next_interval(self, source_name: str) -> int:
        """Get next polling interval based on strategy.

        Args:
            source_name: Name of source

        Returns:
            Interval in seconds
        """
        stats = self.stats[source_name]
        base_interval = self.config.interval_seconds

        if self.config.strategy == PollingStrategy.FIXED:
            return base_interval

        if self.config.strategy == PollingStrategy.EXPONENTIAL_BACKOFF:
            if stats.failure_count > self.config.failure_threshold:
                factor = min(
                    self.config.backoff_factor
                    ** (stats.failure_count - self.config.failure_threshold),
                    self.config.max_backoff_seconds / base_interval,
                )
                return min(int(base_interval * factor), self.config.max_backoff_seconds)
            return base_interval

        if self.config.strategy == PollingStrategy.ADAPTIVE:
            change_rate = stats.last_change_rate
            if change_rate > self.config.adaptive_change_rate_threshold:
                # Faster polling for frequently changing sources
                interval = int(base_interval * 0.5)
            else:
                # Slower polling for stable sources
                interval = int(base_interval * 2)

            return max(
                self.config.adaptive_min_interval,
                min(interval, self.config.adaptive_max_interval),
            )

        return base_interval

    async def _poll_source(self, source_name: str, fetcher: ProxyFetcher) -> None:
        """Poll a single source.

        Args:
            source_name: Name of source
            fetcher: ProxyFetcher instance
        """
        stats = self.stats[source_name]
        stats.last_poll_time = datetime.now()
        stats.poll_count += 1

        try:
            # Fetch proxies with timeout
            proxies = await asyncio.wait_for(
                fetcher.fetch_async(source_name),
                timeout=self.config.timeout_seconds,
            )

            stats.success_count += 1
            stats.failure_count = 0
            stats.proxies_fetched = len(proxies)
            stats.last_error = None

            # Trigger callbacks
            for callback in self._callbacks:
                try:
                    callback(source_name, proxies)
                except Exception as e:
                    logger.error(
                        f"Error in polling callback for {source_name}: {e}",
                        exc_info=True,
                    )

            logger.info(f"Polled {source_name}: {len(proxies)} proxies fetched")

        except asyncio.TimeoutError:
            stats.failure_count += 1
            stats.last_error = "Timeout"
            logger.warning(f"Polling {source_name} timed out")

        except Exception as e:
            stats.failure_count += 1
            stats.last_error = str(e)
            logger.error(f"Error polling {source_name}: {e}", exc_info=True)

        # Schedule next poll
        next_interval = self._get_next_interval(source_name)
        stats.next_poll_time = self._calculate_next_poll_time(source_name, next_interval)

    async def start(self, sources: dict[str, ProxyFetcher], run_immediately: bool = False) -> None:
        """Start polling sources.

        Args:
            sources: Dict of {source_name: ProxyFetcher}
            run_immediately: Poll immediately instead of waiting for interval
        """
        if self._running:
            logger.warning("Poller already running")
            return

        if not self.config.enabled:
            logger.info("Polling disabled in configuration")
            return

        self._running = True
        logger.info(f"Starting datasource poller with {len(sources)} sources")

        for source_name, fetcher in sources.items():
            self.register_source(source_name)

            # Poll immediately if requested
            if run_immediately:
                await self._poll_source(source_name, fetcher)
            else:
                stats = self.stats[source_name]
                stats.next_poll_time = self._calculate_next_poll_time(
                    source_name, self.config.interval_seconds
                )

        # Start polling task
        self._polling_task = asyncio.create_task(self._polling_loop(sources))

    async def _polling_loop(self, sources: dict[str, ProxyFetcher]) -> None:
        """Main polling loop.

        Args:
            sources: Dict of {source_name: ProxyFetcher}
        """
        while self._running:
            try:
                now = datetime.now()
                tasks = []

                # Check which sources need polling
                for source_name, fetcher in sources.items():
                    stats = self.stats[source_name]

                    if stats.next_poll_time and stats.next_poll_time <= now:
                        tasks.append(self._poll_source(source_name, fetcher))

                # Run polling tasks concurrently
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                # Sleep before next check
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in polling loop: {e}", exc_info=True)
                await asyncio.sleep(5)

    async def stop(self) -> None:
        """Stop the polling loop."""
        self._running = False

        if hasattr(self, "_polling_task"):
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass

        logger.info("Datasource poller stopped")

    def get_stats(self, source_name: str | None = None) -> dict:
        """Get polling statistics.

        Args:
            source_name: Specific source or None for all

        Returns:
            Statistics dict
        """
        if source_name:
            if source_name not in self.stats:
                return {}
            stats = self.stats[source_name]
            return {
                "source": stats.source_name,
                "last_poll": stats.last_poll_time.isoformat() if stats.last_poll_time else None,
                "next_poll": stats.next_poll_time.isoformat() if stats.next_poll_time else None,
                "poll_count": stats.poll_count,
                "success_count": stats.success_count,
                "failure_count": stats.failure_count,
                "last_error": stats.last_error,
                "proxies_fetched": stats.proxies_fetched,
            }

        return {name: self.get_stats(name) for name in self.stats}
