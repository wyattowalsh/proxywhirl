"""Weighted source selection for proxy fetching."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from loguru import logger


@dataclass
class WeightedSource:
    """A proxy source with weight."""

    name: str
    url: str
    weight: float = 1.0  # Higher weight = higher probability
    success_rate: float = 0.95
    enabled: bool = True

    def get_adjusted_weight(self) -> float:
        """
        Get weight adjusted by success rate.

        Returns:
            Adjusted weight
        """
        return self.weight * self.success_rate


class SourceWeightRegistry:
    """
    Registry for managing weighted sources.

    Selects sources probabilistically based on weights and success rates.
    """

    def __init__(self):
        """Initialize source weight registry."""
        self.sources: dict[str, WeightedSource] = {}
        self.selection_counts: dict[str, int] = {}

    def add_source(
        self,
        name: str,
        url: str,
        weight: float = 1.0,
    ) -> None:
        """
        Add a source to registry.

        Args:
            name: Source name
            url: Source URL
            weight: Source weight (higher = more likely to be selected)
        """
        if weight <= 0:
            raise ValueError(f"Weight must be positive, got {weight}")

        self.sources[name] = WeightedSource(
            name=name,
            url=url,
            weight=weight,
        )
        self.selection_counts[name] = 0

        logger.debug(f"Added weighted source: {name} (weight: {weight})")

    def remove_source(self, name: str) -> None:
        """
        Remove a source from registry.

        Args:
            name: Source name
        """
        if name in self.sources:
            del self.sources[name]
            if name in self.selection_counts:
                del self.selection_counts[name]
            logger.debug(f"Removed source: {name}")

    def set_weight(self, name: str, weight: float) -> None:
        """
        Update source weight.

        Args:
            name: Source name
            weight: New weight
        """
        if name not in self.sources:
            raise KeyError(f"Source not found: {name}")

        if weight <= 0:
            raise ValueError(f"Weight must be positive, got {weight}")

        self.sources[name].weight = weight
        logger.debug(f"Updated weight for {name}: {weight}")

    def set_success_rate(self, name: str, success_rate: float) -> None:
        """
        Update source success rate (affects weight).

        Args:
            name: Source name
            success_rate: Success rate (0.0-1.0)
        """
        if name not in self.sources:
            raise KeyError(f"Source not found: {name}")

        if not 0.0 <= success_rate <= 1.0:
            raise ValueError(f"Success rate must be 0.0-1.0, got {success_rate}")

        self.sources[name].success_rate = success_rate
        logger.debug(f"Updated success rate for {name}: {success_rate:.1%}")

    def enable_source(self, name: str) -> None:
        """
        Enable a source.

        Args:
            name: Source name
        """
        if name in self.sources:
            self.sources[name].enabled = True
            logger.debug(f"Enabled source: {name}")

    def disable_source(self, name: str) -> None:
        """
        Disable a source.

        Args:
            name: Source name
        """
        if name in self.sources:
            self.sources[name].enabled = False
            logger.debug(f"Disabled source: {name}")

    def select_source(self) -> Optional[WeightedSource]:
        """
        Select a source using weighted random selection.

        Returns:
            Selected source or None if no sources available
        """
        enabled_sources = [s for s in self.sources.values() if s.enabled]

        if not enabled_sources:
            logger.warning("No enabled sources available")
            return None

        # Compute adjusted weights
        weights = [s.get_adjusted_weight() for s in enabled_sources]
        total_weight = sum(weights)

        if total_weight <= 0:
            return random.choice(enabled_sources)

        # Weighted random selection
        choice = random.uniform(0, total_weight)
        cumulative = 0.0

        for source, weight in zip(enabled_sources, weights):
            cumulative += weight
            if choice <= cumulative:
                self.selection_counts[source.name] = self.selection_counts.get(source.name, 0) + 1
                return source

        # Fallback (shouldn't reach here)
        return enabled_sources[-1]

    def select_sources(self, count: int) -> list[WeightedSource]:
        """
        Select multiple sources without replacement.

        Args:
            count: Number of sources to select

        Returns:
            List of selected sources
        """
        enabled_sources = [s for s in self.sources.values() if s.enabled]

        if not enabled_sources:
            return []

        # Weighted sampling without replacement
        k = min(count, len(enabled_sources))
        weights = [s.get_adjusted_weight() for s in enabled_sources]

        return random.choices(enabled_sources, weights=weights, k=k)

    def get_source(self, name: str) -> Optional[WeightedSource]:
        """
        Get source by name.

        Args:
            name: Source name

        Returns:
            Source or None
        """
        return self.sources.get(name)

    def get_all_sources(self, enabled_only: bool = False) -> list[WeightedSource]:
        """
        Get all sources.

        Args:
            enabled_only: Only return enabled sources

        Returns:
            List of sources
        """
        if enabled_only:
            return [s for s in self.sources.values() if s.enabled]
        return list(self.sources.values())

    def get_selection_stats(self) -> dict[str, int | float | dict]:  # type: ignore[type-arg]
        """
        Get source selection statistics.

        Returns:
            Dictionary with stats
        """
        total_selections = sum(self.selection_counts.values())

        stats = {}
        for name, count in self.selection_counts.items():
            percent = (count / total_selections * 100) if total_selections > 0 else 0.0
            stats[name] = {
                "selections": count,
                "percentage": percent,
            }

        return {
            "total_selections": total_selections,
            "sources": stats,
        }

    def reset_stats(self) -> None:
        """Reset selection statistics."""
        self.selection_counts = {name: 0 for name in self.sources}
