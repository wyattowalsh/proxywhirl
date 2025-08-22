"""
proxywhirl/loaders/base.py -- base class for all proxy source data loaders
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set

import httpx
from loguru import logger
from pandas import DataFrame
from pydantic import BaseModel, Field
from tenacity import AsyncRetrying, RetryError, stop_after_attempt, wait_exponential


class LoaderConfig(BaseModel):
    """Configuration for proxy loader behavior."""

    timeout: float = Field(default=30.0, ge=1.0, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, ge=0.1, description="Base delay between retries")
    max_retry_delay: float = Field(default=60.0, ge=1.0, description="Maximum retry delay")
    rate_limit_calls: int = Field(default=10, ge=1, description="Rate limit: calls per period")
    rate_limit_period: float = Field(
        default=60.0, ge=1.0, description="Rate limit period in seconds"
    )
    enable_caching: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=300, ge=60, description="Cache TTL in seconds")
    user_agent: str = Field(
        default="ProxyWhirl/1.0 (+https://github.com/wyattowalsh/proxywhirl)",
        description="User agent string",
    )
    headers: Dict[str, str] = Field(default_factory=dict, description="Additional HTTP headers")


class LoaderCapabilities(BaseModel):
    """Metadata about loader capabilities and requirements."""

    schemes: Set[str] = Field(default_factory=set, description="Supported proxy schemes")
    countries: Optional[Set[str]] = Field(None, description="Available countries (if filterable)")
    anonymity_levels: Set[str] = Field(
        default_factory=set, description="Supported anonymity levels"
    )
    requires_auth: bool = Field(default=False, description="Requires authentication")
    rate_limited: bool = Field(default=True, description="Source has rate limiting")
    max_concurrent: int = Field(default=1, ge=1, description="Maximum concurrent requests")
    expected_count: Optional[int] = Field(None, description="Typical proxy count returned")
    supports_filtering: bool = Field(default=False, description="Supports query filtering")
    data_freshness: Optional[str] = Field(None, description="How often data is updated")


class LoaderHealthStatus(BaseModel):
    """Health and operational status of a loader."""

    is_operational: bool = Field(default=True, description="Is loader currently operational")
    last_success: Optional[datetime] = Field(None, description="Last successful load time")
    last_failure: Optional[datetime] = Field(None, description="Last failure time")
    consecutive_failures: int = Field(default=0, ge=0, description="Consecutive failure count")
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0, description="Success rate (0-1)")
    avg_response_time: Optional[float] = Field(None, description="Average response time")
    total_requests: int = Field(default=0, ge=0, description="Total requests made")
    total_successes: int = Field(default=0, ge=0, description="Total successful requests")
    total_failures: int = Field(default=0, ge=0, description="Total failed requests")
    error_message: Optional[str] = Field(None, description="Last error message")


class BaseLoader(ABC):
    """Base class for all proxy source data loaders with advanced capabilities."""

    def __init__(
        self,
        name: str,
        description: str,
        config: Optional[LoaderConfig] = None,
        capabilities: Optional[LoaderCapabilities] = None,
    ):
        self.name = name
        self.description = description
        self.config = config or LoaderConfig()
        self.capabilities = capabilities or LoaderCapabilities()
        self.health = LoaderHealthStatus()

        # Rate limiting state
        self._last_requests: List[datetime] = []
        self._client: Optional[httpx.AsyncClient] = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"{self.__class__.__name__}(name={self.name!r})"

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_client()

    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized."""
        if self._client is None or self._client.is_closed:
            headers = {
                "User-Agent": self.config.user_agent,
                **self.config.headers,
            }
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                headers=headers,
            )

    async def _close_client(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _respect_rate_limit(self) -> None:
        """Enforce rate limiting."""
        now = datetime.now(timezone.utc)

        # Clean old requests outside the window
        cutoff = now - timedelta(seconds=self.config.rate_limit_period)
        self._last_requests = [req for req in self._last_requests if req > cutoff]

        # Check if we're within limits
        if len(self._last_requests) >= self.config.rate_limit_calls:
            sleep_time = (
                self.config.rate_limit_period - (now - self._last_requests[0]).total_seconds()
            )
            if sleep_time > 0:
                logger.debug(f"Rate limiting {self.name}: sleeping {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)

        # Record this request
        self._last_requests.append(now)

    async def _update_health_success(self, response_time: float) -> None:
        """Update health metrics after successful operation."""
        self.health.is_operational = True
        self.health.last_success = datetime.now(timezone.utc)
        self.health.consecutive_failures = 0
        self.health.total_requests += 1
        self.health.total_successes += 1

        # Update success rate
        self.health.success_rate = self.health.total_successes / self.health.total_requests

        # Update average response time
        if self.health.avg_response_time is None:
            self.health.avg_response_time = response_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.health.avg_response_time = (
                alpha * response_time + (1 - alpha) * self.health.avg_response_time
            )

    async def _update_health_failure(self, error: Exception) -> None:
        """Update health metrics after failed operation."""
        self.health.last_failure = datetime.now(timezone.utc)
        self.health.consecutive_failures += 1
        self.health.total_requests += 1
        self.health.total_failures += 1
        self.health.error_message = str(error)

        # Mark as non-operational after 3 consecutive failures
        if self.health.consecutive_failures >= 3:
            self.health.is_operational = False

        # Update success rate
        self.health.success_rate = (
            self.health.total_successes / self.health.total_requests
            if self.health.total_requests > 0
            else 0.0
        )

    @abstractmethod
    def load(self) -> DataFrame:
        """Load proxy source data synchronously."""

    async def load_async(self) -> DataFrame:
        """Load proxy source data asynchronously.

        Default implementation runs the synchronous load() method in a
        thread pool. Subclasses can override for true async loading.
        """
        import concurrent.futures

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.load)

    async def load_with_retry(self) -> DataFrame:
        """Load with built-in retry logic and health tracking."""
        if not self.health.is_operational:
            raise RuntimeError(f"Loader {self.name} is not operational")

        await self._ensure_client()
        await self._respect_rate_limit()

        start_time = datetime.now(timezone.utc)

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(self.config.max_retries + 1),
                wait=wait_exponential(
                    multiplier=self.config.retry_delay, max=self.config.max_retry_delay
                ),
            ):
                with attempt:
                    df = await self.load_async()

                    # Track successful completion
                    end_time = datetime.now(timezone.utc)
                    response_time = (end_time - start_time).total_seconds()
                    await self._update_health_success(response_time)

                    logger.info(
                        f"Loaded {len(df)} proxies from {self.name} in {response_time:.2f}s"
                    )
                    return df

        except RetryError as e:
            await self._update_health_failure(e)
            logger.error(
                f"Failed to load from {self.name} after {self.config.max_retries} retries: {e}"
            )
            raise
        except (RuntimeError, OSError, ValueError, ConnectionError) as e:
            await self._update_health_failure(e)
            logger.error(f"Error loading from {self.name}: {e}")
            raise

    def get_health_status(self) -> LoaderHealthStatus:
        """Get current health status."""
        return self.health.model_copy()

    def is_healthy(self) -> bool:
        """Quick health check."""
        return self.health.is_operational and self.health.success_rate > 0.5

    def get_capabilities(self) -> LoaderCapabilities:
        """Get loader capabilities."""
        return self.capabilities.model_copy()

    def configure(self, **kwargs: Any) -> None:
        """Update configuration dynamically."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")

    async def test_connection(self) -> bool:
        """Test if the loader can connect to its data source."""
        try:
            async with self:
                df = await self.load_async()
                return len(df) > 0
        except (RuntimeError, OSError, ValueError) as e:
            logger.debug(f"Connection test failed for {self.name}: {e}")
            return False
