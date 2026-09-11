"""Shared strategy protocol and state."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol
from uuid import UUID

from proxywhirl.models import (
    Proxy,
    ProxyPool,
    SelectionContext,
)


@dataclass
class ProxyMetrics:
    """Per-proxy mutable metrics maintained by a strategy.

    This class encapsulates performance metrics that a strategy tracks
    for each proxy. By storing these separately from the Proxy model,
    strategies can maintain independent metric state with their own
    configuration (e.g., EMA alpha values).

    Attributes:
        ema_response_time_ms: Exponential moving average of response times
        total_requests: Count of requests made through this proxy
        total_successes: Count of successful requests
        total_failures: Count of failed requests
        last_response_time_ms: Most recent response time
        window_start: Start time of the current sliding window
    """

    ema_response_time_ms: float | None = None
    total_requests: int = 0
    total_successes: int = 0
    total_failures: int = 0
    last_response_time_ms: float | None = None
    window_start: datetime | None = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate for this proxy in this strategy's state."""
        if self.total_requests == 0:
            return 0.0
        return max(0.0, min(1.0, self.total_successes / self.total_requests))

    def update_ema(self, response_time_ms: float, alpha: float) -> None:
        """Update EMA with new response time.

        Args:
            response_time_ms: Response time in milliseconds
            alpha: EMA smoothing factor (0-1)
        """
        if self.ema_response_time_ms is None:
            self.ema_response_time_ms = response_time_ms
        else:
            self.ema_response_time_ms = (
                alpha * response_time_ms + (1 - alpha) * self.ema_response_time_ms
            )
        self.last_response_time_ms = response_time_ms


@dataclass
class StrategyState:
    """Per-strategy mutable state for managing proxy metrics.

    This class separates mutable strategy state from immutable proxy identity.
    Each strategy instance maintains its own StrategyState, which tracks
    per-proxy metrics independently. This allows different strategies to:

    1. Use different EMA alpha values without conflicts
    2. Track proxy performance independently
    3. Maintain consistent metrics across strategy reconfiguration

    The state is keyed by proxy UUID to ensure stable identity even if
    proxy objects are recreated.

    Example:
        >>> state = StrategyState(ema_alpha=0.3)
        >>> state.record_success(proxy.id, response_time_ms=150.0)
        >>> metrics = state.get_metrics(proxy.id)
        >>> print(metrics.ema_response_time_ms)  # 150.0

    Thread Safety:
        Uses threading.Lock to protect all state mutations.

    Attributes:
        ema_alpha: EMA smoothing factor for this strategy's metrics
        window_duration_seconds: Duration of sliding window for counter resets
    """

    ema_alpha: float = 0.2
    window_duration_seconds: int = 3600
    _metrics: dict[UUID, ProxyMetrics] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def get_metrics(self, proxy_id: UUID) -> ProxyMetrics:
        """Get or create metrics for a proxy.

        Args:
            proxy_id: UUID of the proxy

        Returns:
            ProxyMetrics instance for this proxy
        """
        with self._lock:
            if proxy_id not in self._metrics:
                self._metrics[proxy_id] = ProxyMetrics()
            return self._metrics[proxy_id]

    def record_success(self, proxy_id: UUID, response_time_ms: float) -> None:
        """Record a successful request.

        Args:
            proxy_id: UUID of the proxy
            response_time_ms: Response time in milliseconds
        """
        with self._lock:
            metrics = self._metrics.setdefault(proxy_id, ProxyMetrics())
            metrics.total_requests += 1
            metrics.total_successes += 1
            metrics.update_ema(response_time_ms, self.ema_alpha)

    def record_failure(self, proxy_id: UUID) -> None:
        """Record a failed request.

        Args:
            proxy_id: UUID of the proxy
        """
        with self._lock:
            metrics = self._metrics.setdefault(proxy_id, ProxyMetrics())
            metrics.total_requests += 1
            metrics.total_failures += 1

    def get_ema_response_time(self, proxy_id: UUID) -> float | None:
        """Get EMA response time for a proxy.

        Args:
            proxy_id: UUID of the proxy

        Returns:
            EMA response time in ms, or None if no data
        """
        with self._lock:
            if proxy_id not in self._metrics:
                return None
            return self._metrics[proxy_id].ema_response_time_ms

    def get_success_rate(self, proxy_id: UUID) -> float:
        """Get success rate for a proxy.

        Args:
            proxy_id: UUID of the proxy

        Returns:
            Success rate (0.0-1.0), or 0.0 if no data
        """
        with self._lock:
            if proxy_id not in self._metrics:
                return 0.0
            return self._metrics[proxy_id].success_rate

    def get_request_count(self, proxy_id: UUID) -> int:
        """Get total request count for a proxy.

        Args:
            proxy_id: UUID of the proxy

        Returns:
            Total number of requests, or 0 if no data
        """
        with self._lock:
            if proxy_id not in self._metrics:
                return 0
            return self._metrics[proxy_id].total_requests

    def reset_metrics(self, proxy_id: UUID) -> None:
        """Reset metrics for a proxy.

        Args:
            proxy_id: UUID of the proxy
        """
        with self._lock:
            if proxy_id in self._metrics:
                self._metrics[proxy_id] = ProxyMetrics()

    def clear_all(self) -> None:
        """Clear all tracked metrics."""
        with self._lock:
            self._metrics.clear()


class RotationStrategy(Protocol):
    """Protocol defining interface for proxy rotation strategies."""

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        """
        Select a proxy from the pool based on strategy logic.

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

        Returns:
            Selected proxy

        Raises:
            ProxyPoolEmptyError: If no suitable proxy is available
        """
        ...

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record the result of using a proxy.

        Args:
            proxy: The proxy that was used
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        ...
