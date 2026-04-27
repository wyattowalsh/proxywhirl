"""Diversity metrics for proxy pools.

Provides metrics for evaluating IP location diversity and AS (Autonomous System) diversity.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from proxywhirl.models import Proxy


@dataclass
class DiversityMetrics:
    """Metrics measuring proxy pool diversity.

    Attributes:
        country_count: Number of unique countries
        as_count: Number of unique autonomous systems
        city_count: Number of unique cities
        country_distribution: Count of proxies per country
        as_distribution: Count of proxies per AS
        city_distribution: Count of proxies per city
        shannon_entropy: Shannon entropy of country distribution (0-1)
        geographic_spread: Percentage of unique countries vs total proxies
    """

    country_count: int
    as_count: int
    city_count: int
    country_distribution: dict[str, int]
    as_distribution: dict[str, int]
    city_distribution: dict[str, int]
    shannon_entropy: float
    geographic_spread: float


class DiversityAnalyzer:
    """Analyzes diversity metrics for proxy pools."""

    @staticmethod
    def calculate_metrics(proxies: list[Proxy]) -> DiversityMetrics:
        """Calculate diversity metrics for a list of proxies.

        Args:
            proxies: List of proxy objects with geo data

        Returns:
            DiversityMetrics object with computed metrics
        """
        if not proxies:
            return DiversityMetrics(
                country_count=0,
                as_count=0,
                city_count=0,
                country_distribution={},
                as_distribution={},
                city_distribution={},
                shannon_entropy=0.0,
                geographic_spread=0.0,
            )

        countries = []
        asns = []
        cities = []

        for proxy in proxies:
            if hasattr(proxy, "country") and proxy.country:
                countries.append(proxy.country)
            if hasattr(proxy, "asn") and proxy.asn:
                asns.append(proxy.asn)
            if hasattr(proxy, "city") and proxy.city:
                cities.append(proxy.city)

        country_dist = dict(Counter(countries))
        as_dist = dict(Counter(asns))
        city_dist = dict(Counter(cities))

        shannon = DiversityAnalyzer._calculate_shannon_entropy(country_dist, len(proxies))
        geographic_spread = len(country_dist) / len(proxies) * 100 if len(proxies) > 0 else 0

        return DiversityMetrics(
            country_count=len(country_dist),
            as_count=len(as_dist),
            city_count=len(city_dist),
            country_distribution=country_dist,
            as_distribution=as_dist,
            city_distribution=city_dist,
            shannon_entropy=shannon,
            geographic_spread=geographic_spread,
        )

    @staticmethod
    def _calculate_shannon_entropy(distribution: dict[str, int], total: int) -> float:
        """Calculate Shannon entropy for a distribution.

        Higher entropy indicates more uniform distribution.
        Returns normalized entropy 0-1.

        Args:
            distribution: Count distribution dict
            total: Total count

        Returns:
            Normalized Shannon entropy (0-1)
        """
        if not distribution or total == 0:
            return 0.0

        import math

        entropy = 0.0
        for count in distribution.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        # Normalize to 0-1 range
        max_entropy = math.log2(len(distribution)) if len(distribution) > 0 else 1
        return entropy / max_entropy if max_entropy > 0 else 0.0

    @staticmethod
    def get_diversity_score(metrics: DiversityMetrics, total_proxies: int) -> float:
        """Calculate overall diversity score (0-100).

        Combines country diversity, AS diversity, and entropy.

        Args:
            metrics: DiversityMetrics object
            total_proxies: Total number of proxies

        Returns:
            Diversity score 0-100
        """
        if total_proxies == 0:
            return 0.0

        country_score = (metrics.country_count / total_proxies) * 50 if total_proxies > 0 else 0
        as_score = (metrics.as_count / total_proxies) * 30 if total_proxies > 0 else 0
        entropy_score = metrics.shannon_entropy * 20

        return min(100, country_score + as_score + entropy_score)

    @staticmethod
    def get_concentration_warning(metrics: DiversityMetrics, total_proxies: int) -> str | None:
        """Get warning if proxy pool has poor diversity.

        Args:
            metrics: DiversityMetrics object
            total_proxies: Total number of proxies

        Returns:
            Warning message or None if diversity is good
        """
        if total_proxies == 0:
            return "Empty proxy pool"

        if metrics.country_count <= 1:
            return "All proxies from single country"

        if metrics.shannon_entropy < 0.3:
            return "Poor country distribution - proxies clustered in few countries"

        if metrics.as_count <= 1:
            return "All proxies from single AS"

        return None
