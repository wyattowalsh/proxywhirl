"""Adaptive timeout strategies for proxy operations.

Implements dynamic timeout adjustment based on
network conditions and historical performance.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from loguru import logger


class TimeoutStrategy(str, Enum):
    """Timeout strategy types."""

    FIXED = "fixed"
    LINEAR_BACKOFF = "linear_backoff"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    ADAPTIVE = "adaptive"


@dataclass
class TimeoutConfig:
    """Configuration for timeout handling."""

    strategy: TimeoutStrategy
    base_timeout_ms: int
    min_timeout_ms: int = 100
    max_timeout_ms: int = 30000


class AdaptiveTimeoutManager:
    """Manages adaptive timeout strategies."""

    def __init__(self, config: TimeoutConfig) -> None:
        """Initialize adaptive timeout manager.

        Args:
            config: Timeout configuration
        """
        self.config = config
        self._request_history: list[dict[str, Any]] = []
        self._avg_latency_ms = config.base_timeout_ms
        logger.debug(f"AdaptiveTimeoutManager initialized: {config.strategy.value}")

    def record_request(self, duration_ms: float, success: bool, source: str = "") -> None:
        """Record request for timeout adaptation.

        Args:
            duration_ms: Request duration
            success: Whether request succeeded
            source: Source identifier
        """
        self._request_history.append(
            {
                "duration_ms": duration_ms,
                "success": success,
                "source": source,
            }
        )

        if len(self._request_history) > 100:
            self._request_history.pop(0)

        self._avg_latency_ms = sum(r["duration_ms"] for r in self._request_history) / len(
            self._request_history
        )

    def get_timeout(self, attempt: int = 1, source: str = "") -> int:
        """Get timeout for attempt.

        Args:
            attempt: Attempt number
            source: Source identifier

        Returns:
            Timeout in milliseconds
        """
        if self.config.strategy == TimeoutStrategy.FIXED:
            return self.config.base_timeout_ms

        if self.config.strategy == TimeoutStrategy.LINEAR_BACKOFF:
            timeout = self.config.base_timeout_ms + ((attempt - 1) * 1000)
            return min(timeout, self.config.max_timeout_ms)

        if self.config.strategy == TimeoutStrategy.EXPONENTIAL_BACKOFF:
            timeout = self.config.base_timeout_ms * (2 ** (attempt - 1))
            return min(timeout, self.config.max_timeout_ms)

        if self.config.strategy == TimeoutStrategy.ADAPTIVE:
            timeout = int(self._avg_latency_ms * 2)
            timeout = max(timeout, self.config.min_timeout_ms)
            return min(timeout, self.config.max_timeout_ms)

        return self.config.base_timeout_ms

    def export_metrics(self) -> dict[str, Any]:
        """Export timeout metrics.

        Returns:
            Dictionary of metrics
        """
        if not self._request_history:
            return {
                "strategy": self.config.strategy.value,
                "average_latency_ms": self.config.base_timeout_ms,
                "request_count": 0,
            }

        successful = sum(1 for r in self._request_history if r["success"])

        return {
            "strategy": self.config.strategy.value,
            "average_latency_ms": self._avg_latency_ms,
            "request_count": len(self._request_history),
            "success_rate": (successful / len(self._request_history)) * 100,
        }
