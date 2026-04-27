"""Predictive proxy selection using machine learning.

Uses historical performance data to predict which proxy will perform
best for the next request, improving success rates and latency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from loguru import logger

from proxywhirl.models import Proxy, SelectionContext


@dataclass
class ProxyMetrics:
    """Historical metrics for a proxy."""

    proxy_url: str
    success_rate: float = 0.5
    avg_latency: float = 0.0
    failure_count: int = 0
    success_count: int = 0
    last_used: datetime | None = None
    performance_score: float = 0.5
    request_count: int = 0
    failures_by_type: dict[str, int] = field(default_factory=dict)

    def update_success(self, latency: float) -> None:
        """Record successful request."""
        self.success_count += 1
        self.request_count += 1
        self.avg_latency = (
            self.avg_latency * (self.success_count - 1) + latency
        ) / self.success_count
        self.last_used = datetime.now()
        self._update_score()

    def update_failure(self, failure_type: str = "general") -> None:
        """Record failed request."""
        self.failure_count += 1
        self.request_count += 1
        self.failures_by_type[failure_type] = self.failures_by_type.get(failure_type, 0) + 1
        self._update_score()

    def _update_score(self) -> None:
        """Recalculate performance score."""
        if self.request_count == 0:
            self.performance_score = 0.5
            return

        self.success_rate = self.success_count / self.request_count
        # Score = success_rate (0.5x) + latency factor (0.5x)
        latency_factor = max(0, 1 - (self.avg_latency / 10.0))  # Normalized
        self.performance_score = (self.success_rate * 0.5) + (latency_factor * 0.5)


class PredictiveSelector:
    """Predicts best proxy for next request using ML."""

    def __init__(self) -> None:
        """Initialize predictor."""
        self.metrics: dict[str, ProxyMetrics] = {}
        self.prediction_history: list[dict[str, Any]] = []
        self.min_samples = 5  # Minimum samples before making predictions

    def record_request(
        self,
        proxy_url: str,
        success: bool,
        latency: float = 0.0,
        failure_type: str = "general",
    ) -> None:
        """Record request outcome for learning.

        Args:
            proxy_url: Proxy URL
            success: Whether request succeeded
            latency: Request latency in seconds
            failure_type: Type of failure if unsuccessful
        """
        if proxy_url not in self.metrics:
            self.metrics[proxy_url] = ProxyMetrics(proxy_url)

        metrics = self.metrics[proxy_url]
        if success:
            metrics.update_success(latency)
        else:
            metrics.update_failure(failure_type)

        logger.debug(
            f"Recorded request for {proxy_url}: "
            f"success={success}, latency={latency:.2f}s, score={metrics.performance_score:.2f}"
        )

    def predict_best_proxy(
        self,
        proxies: list[Proxy],
        context: SelectionContext | None = None,
    ) -> Proxy | None:
        """Predict which proxy should be used next.

        Args:
            proxies: Available proxies to choose from
            context: Optional context for prediction

        Returns:
            Predicted best proxy or None
        """
        if not proxies:
            return None

        # Filter proxies we have metrics for
        candidates = []
        for proxy in proxies:
            if proxy.url in self.metrics:
                metrics = self.metrics[proxy.url]
                if metrics.request_count >= self.min_samples:
                    candidates.append((proxy, metrics))

        if not candidates:
            # Not enough data, use random
            logger.debug("Not enough training data, returning random proxy")
            return proxies[0] if proxies else None

        # Select proxy with highest performance score
        best_proxy, best_metrics = max(candidates, key=lambda x: x[1].performance_score)

        self.prediction_history.append(
            {
                "timestamp": datetime.now(),
                "predicted_proxy": best_proxy.url,
                "score": best_metrics.performance_score,
                "context": context.model_dump() if context else None,
            }
        )

        logger.debug(
            f"Predicted best proxy: {best_proxy.url} (score: {best_metrics.performance_score:.2f})"
        )
        return best_proxy

    def get_proxy_ranking(self, proxies: list[Proxy]) -> list[tuple[Proxy, float]]:
        """Get ranking of proxies by predicted performance.

        Args:
            proxies: Proxies to rank

        Returns:
            List of (proxy, score) tuples sorted by score
        """
        ranking = []
        for proxy in proxies:
            if proxy.url in self.metrics:
                metrics = self.metrics[proxy.url]
                ranking.append((proxy, metrics.performance_score))
            else:
                ranking.append((proxy, 0.5))  # Default score

        return sorted(ranking, key=lambda x: x[1], reverse=True)

    def reset_metrics(self, proxy_url: str | None = None) -> None:
        """Reset metrics for proxy(s).

        Args:
            proxy_url: If provided, reset only this proxy; else reset all
        """
        if proxy_url:
            if proxy_url in self.metrics:
                del self.metrics[proxy_url]
                logger.debug(f"Reset metrics for {proxy_url}")
        else:
            self.metrics.clear()
            logger.debug("Reset all proxy metrics")

    def get_metrics(self, proxy_url: str) -> ProxyMetrics | None:
        """Get metrics for a proxy."""
        return self.metrics.get(proxy_url)

    def get_prediction_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent prediction history."""
        return self.prediction_history[-limit:]

    def export_metrics(self) -> dict[str, Any]:
        """Export all metrics as dictionary."""
        return {
            url: {
                "success_rate": metrics.success_rate,
                "avg_latency": metrics.avg_latency,
                "failure_count": metrics.failure_count,
                "success_count": metrics.success_count,
                "performance_score": metrics.performance_score,
                "request_count": metrics.request_count,
            }
            for url, metrics in self.metrics.items()
        }


_predictor: PredictiveSelector | None = None


def get_predictor() -> PredictiveSelector:
    """Get global predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = PredictiveSelector()
    return _predictor
