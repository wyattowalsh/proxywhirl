"""Weighted health-based proxy routing.

Routes more traffic to healthier proxies based on health scores and
reduces traffic to degraded proxies in a dynamic manner.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from proxywhirl.models import Proxy


class HealthWeightedRouter:
    """Routes requests based on proxy health scores."""

    def __init__(self, enable_adaptive: bool = True) -> None:
        """Initialize health-weighted router.

        Args:
            enable_adaptive: Enable adaptive weight adjustment
        """
        self.enable_adaptive = enable_adaptive
        self.weights: dict[str, float] = {}
        self.health_scores: dict[str, float] = {}

    def calculate_weights(self, proxies: list[Proxy]) -> dict[str, float]:
        """Calculate routing weights based on proxy health.

        Args:
            proxies: List of proxies

        Returns:
            Dict mapping proxy URL to weight (0-1)
        """
        if not proxies:
            return {}

        weights = {}
        total_health = 0.0

        # Calculate health scores
        for proxy in proxies:
            score = self._calculate_health_score(proxy)
            self.health_scores[proxy.url] = score
            total_health += score

        if total_health == 0:
            # All proxies equally degraded, distribute evenly
            weight = 1.0 / len(proxies)
            for proxy in proxies:
                weights[proxy.url] = weight
        else:
            # Distribute weights proportional to health
            for proxy in proxies:
                score = self.health_scores[proxy.url]
                weights[proxy.url] = score / total_health

        self.weights = weights
        return weights

    def select_proxy_by_weight(self, proxies: list[Proxy]) -> Proxy | None:
        """Select proxy weighted by health.

        Args:
            proxies: List of proxies

        Returns:
            Selected proxy or None
        """
        if not proxies:
            return None

        weights = self.calculate_weights(proxies)
        if not weights:
            return proxies[0]

        # Select using weighted random
        import random

        total = sum(weights.values())
        choice = random.uniform(0, total)
        current = 0

        for proxy in proxies:
            current += weights.get(proxy.url, 0)
            if choice <= current:
                logger.debug(
                    f"Selected proxy {proxy.url} (weight: {weights.get(proxy.url, 0):.2f})"
                )
                return proxy

        return proxies[-1]  # Fallback

    def _calculate_health_score(self, proxy: Proxy) -> float:
        """Calculate health score for a proxy (0-1).

        Args:
            proxy: Proxy to score

        Returns:
            Health score 0-1 (1.0 = fully healthy)
        """
        score = 0.5  # Default baseline

        # Factor in status
        if proxy.status == "active":
            score = 0.9
        elif proxy.status == "degraded":
            score = 0.5
        elif proxy.status == "inactive":
            score = 0.1

        # Factor in failure count
        if proxy.failure_count > 0:
            failure_ratio = proxy.failure_count / max(1, proxy.failure_count + proxy.success_count)
            score *= max(0, 1 - failure_ratio)

        # Factor in success rate
        if proxy.success_count > 0:
            success_rate = proxy.success_count / (proxy.success_count + proxy.failure_count)
            score = (score * 0.5) + (success_rate * 0.5)

        return max(0, min(1, score))  # Clamp to 0-1

    def get_health_stats(self) -> dict[str, Any]:
        """Get health statistics.

        Returns:
            Dict with health information
        """
        return {
            "health_scores": self.health_scores.copy(),
            "weights": self.weights.copy(),
            "avg_health": (
                sum(self.health_scores.values()) / len(self.health_scores)
                if self.health_scores
                else 0.0
            ),
        }


_router: HealthWeightedRouter | None = None


def get_health_weighted_router() -> HealthWeightedRouter:
    """Get global health-weighted router instance."""
    global _router
    if _router is None:
        _router = HealthWeightedRouter()
    return _router
