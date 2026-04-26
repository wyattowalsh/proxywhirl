"""Adaptive proxy selection based on request context and performance metrics.

Provides:
- Context-aware proxy selection
- Performance-based scoring
- Dynamic proxy ranking
- Adaptive strategy switching
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from loguru import logger


class SelectionContext(str, Enum):
    """Proxy selection context."""

    STANDARD = "standard"
    HIGH_PRIORITY = "high_priority"
    LOW_LATENCY = "low_latency"
    HIGH_BANDWIDTH = "high_bandwidth"
    GEO_SPECIFIC = "geo_specific"
    ANONYMOUS = "anonymous"


@dataclass
class ProxyScore:
    """Score for proxy selection."""

    proxy_id: str
    overall_score: float = 0.0
    latency_score: float = 0.0  # 0-100, lower latency = higher score
    success_rate_score: float = 0.0  # 0-100
    bandwidth_score: float = 0.0  # 0-100
    freshness_score: float = 0.0  # 0-100, penalize old proxies
    anonymity_score: float = 0.0  # 0-100
    geo_score: float = 0.0  # 0-100, match to target region
    timestamps: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "proxy_id": self.proxy_id,
            "overall_score": round(self.overall_score, 2),
            "latency_score": round(self.latency_score, 2),
            "success_rate_score": round(self.success_rate_score, 2),
            "bandwidth_score": round(self.bandwidth_score, 2),
            "freshness_score": round(self.freshness_score, 2),
            "anonymity_score": round(self.anonymity_score, 2),
            "geo_score": round(self.geo_score, 2),
        }


class AdaptiveSelector:
    """Adaptive proxy selection engine."""

    def __init__(self, window_size: int = 100):
        """Initialize adaptive selector.

        Args:
            window_size: Number of requests to consider for scoring
        """
        self.window_size = window_size
        self.proxy_scores: dict[str, ProxyScore] = {}
        self.context_weights = {
            SelectionContext.STANDARD: {
                "latency": 0.25,
                "success_rate": 0.5,
                "bandwidth": 0.15,
                "freshness": 0.1,
                "anonymity": 0.0,
                "geo": 0.0,
            },
            SelectionContext.LOW_LATENCY: {
                "latency": 0.6,
                "success_rate": 0.2,
                "bandwidth": 0.1,
                "freshness": 0.1,
                "anonymity": 0.0,
                "geo": 0.0,
            },
            SelectionContext.HIGH_BANDWIDTH: {
                "latency": 0.1,
                "success_rate": 0.3,
                "bandwidth": 0.5,
                "freshness": 0.1,
                "anonymity": 0.0,
                "geo": 0.0,
            },
            SelectionContext.ANONYMOUS: {
                "latency": 0.2,
                "success_rate": 0.3,
                "bandwidth": 0.1,
                "freshness": 0.1,
                "anonymity": 0.3,
                "geo": 0.0,
            },
            SelectionContext.GEO_SPECIFIC: {
                "latency": 0.1,
                "success_rate": 0.3,
                "bandwidth": 0.15,
                "freshness": 0.1,
                "anonymity": 0.15,
                "geo": 0.2,
            },
        }

    def register_proxy(self, proxy_id: str) -> None:
        """Register proxy for scoring.

        Args:
            proxy_id: Proxy identifier
        """
        if proxy_id not in self.proxy_scores:
            self.proxy_scores[proxy_id] = ProxyScore(proxy_id=proxy_id)
            logger.debug(f"Registered proxy {proxy_id} for adaptive scoring")

    def update_metrics(
        self,
        proxy_id: str,
        latency_ms: float,
        success: bool,
        bytes_transferred: int = 0,
        anonymity_level: str = "low",
        target_country: str | None = None,
        proxy_country: str | None = None,
    ) -> None:
        """Update proxy metrics.

        Args:
            proxy_id: Proxy identifier
            latency_ms: Request latency in milliseconds
            success: Whether request was successful
            bytes_transferred: Bytes transferred in request
            anonymity_level: Anonymity level (low/medium/high)
            target_country: Target country code
            proxy_country: Proxy country code
        """
        if proxy_id not in self.proxy_scores:
            self.register_proxy(proxy_id)

        score = self.proxy_scores[proxy_id]
        score.timestamps.append(time.time())

        # Keep sliding window
        if len(score.timestamps) > self.window_size:
            score.timestamps.pop(0)

        # Update individual scores
        score.latency_score = max(0, 100 - (latency_ms / 10))  # 100ms = 0 score
        score.success_rate_score = self._calculate_success_rate_score(proxy_id)
        score.bandwidth_score = min(100, (bytes_transferred / 1000000) * 10)  # 100MB = 100 score
        score.freshness_score = self._calculate_freshness_score(proxy_id)
        score.anonymity_score = self._get_anonymity_score(anonymity_level)

        if target_country and proxy_country:
            score.geo_score = 100 if target_country == proxy_country else 50
        else:
            score.geo_score = 50

        logger.debug(f"Updated metrics for {proxy_id}: latency={latency_ms}ms, success={success}")

    def _calculate_success_rate_score(self, proxy_id: str) -> float:
        """Calculate success rate score from timestamp history."""
        score = self.proxy_scores[proxy_id]
        if not score.timestamps or len(score.timestamps) < 5:
            return 50.0
        # Simplistic: assume longer window = more successful
        return min(100, (len(score.timestamps) / 10) * 100)

    def _calculate_freshness_score(self, proxy_id: str) -> float:
        """Calculate freshness score (penalize stale proxies)."""
        score = self.proxy_scores[proxy_id]
        if not score.timestamps:
            return 0.0
        age_seconds = time.time() - score.timestamps[-1]
        if age_seconds > 3600:  # 1 hour
            return max(0, 100 - (age_seconds / 36) if age_seconds < 3600 else 0)
        return 100.0

    @staticmethod
    def _get_anonymity_score(anonymity_level: str) -> float:
        """Get anonymity score."""
        scores = {
            "low": 33.0,
            "medium": 66.0,
            "high": 100.0,
            "elite": 100.0,
        }
        return scores.get(anonymity_level.lower(), 0.0)

    def select_proxy(
        self,
        candidate_proxies: list[str],
        context: SelectionContext = SelectionContext.STANDARD,
    ) -> str | None:
        """Select best proxy for context.

        Args:
            candidate_proxies: List of proxy IDs to choose from
            context: Selection context

        Returns:
            Selected proxy ID or None
        """
        if not candidate_proxies:
            return None

        weights = self.context_weights.get(context, self.context_weights[SelectionContext.STANDARD])

        best_proxy = None
        best_score = -1

        for proxy_id in candidate_proxies:
            if proxy_id not in self.proxy_scores:
                self.register_proxy(proxy_id)

            score_obj = self.proxy_scores[proxy_id]

            # Calculate weighted overall score
            overall = (
                (score_obj.latency_score * weights["latency"])
                + (score_obj.success_rate_score * weights["success_rate"])
                + (score_obj.bandwidth_score * weights["bandwidth"])
                + (score_obj.freshness_score * weights["freshness"])
                + (score_obj.anonymity_score * weights["anonymity"])
                + (score_obj.geo_score * weights["geo"])
            )

            score_obj.overall_score = overall

            if overall > best_score:
                best_score = overall
                best_proxy = proxy_id

        if best_proxy:
            logger.debug(
                f"Selected proxy {best_proxy} (score={best_score:.1f}) for {context.value}"
            )

        return best_proxy

    def get_top_proxies(
        self,
        count: int = 5,
        context: SelectionContext = SelectionContext.STANDARD,
    ) -> list[tuple[str, float]]:
        """Get top N proxies ranked by score.

        Args:
            count: Number of proxies to return
            context: Selection context

        Returns:
            List of (proxy_id, score) tuples
        """
        ranked = sorted(
            self.proxy_scores.values(),
            key=lambda s: s.overall_score,
            reverse=True,
        )

        return [(s.proxy_id, s.overall_score) for s in ranked[:count]]

    def get_stats(self) -> dict[str, Any]:
        """Get selector statistics."""
        return {
            "registered_proxies": len(self.proxy_scores),
            "window_size": self.window_size,
            "proxy_scores": {pid: score.to_dict() for pid, score in self.proxy_scores.items()},
        }
