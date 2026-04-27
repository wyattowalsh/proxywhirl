"""Proxy pool optimization and tuning."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class OptimizationStrategy(str, Enum):
    """Pool optimization strategies."""

    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    COST = "cost"
    BALANCED = "balanced"


@dataclass
class PoolOptimizationResult:
    """Result of pool optimization."""

    strategy: OptimizationStrategy
    current_size: int
    recommended_size: int
    proxies_to_add: int
    proxies_to_remove: int
    confidence: float
    reason: str


class PoolOptimizer:
    """Optimizes proxy pool configuration."""

    def __init__(self, strategy: OptimizationStrategy = OptimizationStrategy.BALANCED):
        """Initialize optimizer.

        Args:
            strategy: Optimization strategy
        """
        self.strategy = strategy
        self._history: list[dict[str, Any]] = []

    def analyze_pool_health(
        self,
        pool_size: int,
        healthy_count: int,
        degraded_count: int,
        request_volume: int,
        error_rate: float,
    ) -> dict[str, Any]:
        """Analyze pool health metrics.

        Args:
            pool_size: Total proxies in pool
            healthy_count: Number of healthy proxies
            degraded_count: Number of degraded proxies
            request_volume: Recent request volume
            error_rate: Error rate (0-1)

        Returns:
            Health analysis dict
        """
        health_score = 0.0

        # Calculate availability percentage
        available = healthy_count + (degraded_count * 0.5)
        availability = available / pool_size if pool_size > 0 else 0.0

        # Calculate efficiency
        efficiency = 1.0 - error_rate
        throughput = request_volume

        # Weighted score
        health_score = (
            (availability * 0.4) + (efficiency * 0.35) + (min(throughput / 1000, 1.0) * 0.25)
        )

        return {
            "health_score": health_score,
            "availability": availability,
            "efficiency": efficiency,
            "throughput": throughput,
            "error_rate": error_rate,
        }

    def recommend_pool_size(
        self,
        current_size: int,
        health_analysis: dict[str, Any],
        request_volume: int,
        sla_requirements: dict[str, Any] | None = None,
    ) -> PoolOptimizationResult:
        """Recommend optimal pool size.

        Args:
            current_size: Current pool size
            health_analysis: Health analysis result
            request_volume: Request volume per minute
            sla_requirements: SLA requirements (min_availability, max_latency, etc.)

        Returns:
            Optimization recommendation
        """
        sla_requirements = sla_requirements or {
            "min_availability": 0.95,
            "max_error_rate": 0.05,
        }

        recommended_size = current_size
        proxies_to_add = 0
        proxies_to_remove = 0
        confidence = 0.0
        reason = ""

        health_score = health_analysis.get("health_score", 0.0)
        availability = health_analysis.get("availability", 0.0)
        error_rate = health_analysis.get("error_rate", 0.0)

        min_availability = sla_requirements.get("min_availability", 0.95)
        max_error_rate = sla_requirements.get("max_error_rate", 0.05)

        if self.strategy == OptimizationStrategy.PERFORMANCE:
            # Prioritize redundancy and speed
            if availability < min_availability:
                recommended_size = int(current_size * 1.3)
                proxies_to_add = recommended_size - current_size
                confidence = 0.85
                reason = "Insufficient availability for SLA"
            elif health_score > 0.8:
                recommended_size = max(int(current_size * 0.9), 3)
                proxies_to_remove = current_size - recommended_size
                confidence = 0.7
                reason = "Pool health excellent; can reduce size"
            else:
                confidence = 0.6
                reason = "Pool health adequate; maintaining current size"

        elif self.strategy == OptimizationStrategy.AVAILABILITY:
            # Maximize reliability
            if availability < 0.99:
                recommended_size = int(current_size * 1.5)
                proxies_to_add = recommended_size - current_size
                confidence = 0.9
                reason = "Adding proxies for high availability"
            else:
                confidence = 0.8
                reason = "Target availability achieved"

        elif self.strategy == OptimizationStrategy.COST:
            # Minimize pool size
            if error_rate <= max_error_rate and availability >= min_availability:
                recommended_size = max(int(current_size * 0.7), 2)
                proxies_to_remove = current_size - recommended_size
                confidence = 0.75
                reason = "SLA met; reducing costs"
            else:
                confidence = 0.5
                reason = "Cannot reduce without violating SLA"

        else:  # BALANCED
            # Balance all factors
            if availability < min_availability:
                recommended_size = int(current_size * 1.2)
                proxies_to_add = recommended_size - current_size
                confidence = 0.8
                reason = "Adding proxies to meet availability SLA"
            elif health_score > 0.85 and current_size > 5:
                recommended_size = max(int(current_size * 0.95), 3)
                proxies_to_remove = current_size - recommended_size
                confidence = 0.7
                reason = "Pool healthy; slight optimization"
            else:
                confidence = 0.75
                reason = "Balanced approach; maintaining size"

        return PoolOptimizationResult(
            strategy=self.strategy,
            current_size=current_size,
            recommended_size=recommended_size,
            proxies_to_add=proxies_to_add,
            proxies_to_remove=proxies_to_remove,
            confidence=confidence,
            reason=reason,
        )

    def detect_degradation_pattern(
        self,
        health_scores: list[float],
        window_size: int = 10,
    ) -> dict[str, Any]:
        """Detect degradation patterns in health scores.

        Args:
            health_scores: Recent health scores
            window_size: Lookback window size

        Returns:
            Pattern analysis dict
        """
        if len(health_scores) < 2:
            return {"degradation_detected": False, "reason": "Insufficient data"}

        recent = health_scores[-window_size:] if len(health_scores) > window_size else health_scores
        trend = (recent[-1] - recent[0]) / len(recent) if len(recent) > 0 else 0.0

        degrading = trend < -0.01  # Degrading if average loss > 1% per window
        critical = recent[-1] < 0.5  # Critical if current score < 50%

        return {
            "degradation_detected": degrading,
            "critical": critical,
            "trend": trend,
            "current_score": recent[-1] if recent else 0.0,
            "avg_score": sum(recent) / len(recent) if recent else 0.0,
        }

    def get_optimization_history(self) -> list[dict[str, Any]]:
        """Get optimization history.

        Returns:
            List of optimization events
        """
        return self._history.copy()
