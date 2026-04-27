"""Weighted source selection for proxy routing.

Implements probabilistic source selection based on
performance metrics and configured weights.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class SourceWeight:
    """Represents a weighted proxy source."""

    source_id: str
    weight: float
    success_rate: float = 1.0
    available: bool = True

    def get_effective_weight(self) -> float:
        """Get effective weight considering success rate.

        Returns:
            Effective weight
        """
        if not self.available:
            return 0.0
        return self.weight * self.success_rate


class WeightedSourceSelector:
    """Selects sources based on weights and performance."""

    def __init__(self) -> None:
        """Initialize weighted source selector."""
        self._sources: dict[str, SourceWeight] = {}
        logger.debug("WeightedSourceSelector initialized")

    def register_source(self, source_id: str, weight: float = 1.0) -> bool:
        """Register a weighted source.

        Args:
            source_id: Source identifier
            weight: Weight value

        Returns:
            True if registered
        """
        if weight < 0:
            logger.error(f"Invalid weight: {weight}")
            return False

        if source_id in self._sources:
            logger.warning(f"Source already registered: {source_id}")
            return False

        self._sources[source_id] = SourceWeight(source_id=source_id, weight=weight)
        logger.debug(f"Weighted source registered: {source_id} (weight={weight})")
        return True

    def set_weight(self, source_id: str, weight: float) -> bool:
        """Update source weight.

        Args:
            source_id: Source identifier
            weight: New weight value

        Returns:
            True if updated
        """
        if source_id not in self._sources:
            return False

        if weight < 0:
            logger.error(f"Invalid weight: {weight}")
            return False

        self._sources[source_id].weight = weight
        logger.debug(f"Source weight updated: {source_id} = {weight}")
        return True

    def set_success_rate(self, source_id: str, rate: float) -> bool:
        """Update source success rate.

        Args:
            source_id: Source identifier
            rate: Success rate (0-1)

        Returns:
            True if updated
        """
        if source_id not in self._sources:
            return False

        if not 0 <= rate <= 1:
            logger.error(f"Invalid success rate: {rate}")
            return False

        self._sources[source_id].success_rate = rate
        return True

    def mark_unavailable(self, source_id: str) -> bool:
        """Mark source as unavailable.

        Args:
            source_id: Source identifier

        Returns:
            True if marked
        """
        if source_id in self._sources:
            self._sources[source_id].available = False
            logger.warning(f"Source marked unavailable: {source_id}")
            return True
        return False

    def mark_available(self, source_id: str) -> bool:
        """Mark source as available.

        Args:
            source_id: Source identifier

        Returns:
            True if marked
        """
        if source_id in self._sources:
            self._sources[source_id].available = True
            logger.debug(f"Source marked available: {source_id}")
            return True
        return False

    def select(self) -> str | None:
        """Select a source using weighted random selection.

        Returns:
            Selected source ID or None
        """
        available_sources = [s for s in self._sources.values() if s.available]

        if not available_sources:
            logger.warning("No available sources for selection")
            return None

        weights = [s.get_effective_weight() for s in available_sources]
        total_weight = sum(weights)

        if total_weight == 0:
            logger.warning("All sources have zero weight")
            return random.choice(available_sources).source_id

        selected = random.choices(available_sources, weights=weights, k=1)[0]
        return selected.source_id

    def get_distribution(self) -> dict[str, float]:
        """Get source weight distribution.

        Returns:
            Dictionary of source ID to normalized weight
        """
        available = [s for s in self._sources.values() if s.available]
        if not available:
            return {}

        total = sum(s.weight for s in available)
        if total == 0:
            return {}

        return {s.source_id: s.weight / total for s in available}

    def export_metrics(self) -> dict[str, Any]:
        """Export selector metrics.

        Returns:
            Dictionary of metrics
        """
        return {
            "total_sources": len(self._sources),
            "available_sources": len([s for s in self._sources.values() if s.available]),
            "sources": {
                sid: {
                    "weight": s.weight,
                    "success_rate": s.success_rate,
                    "available": s.available,
                    "effective_weight": s.get_effective_weight(),
                }
                for sid, s in self._sources.items()
            },
        }
