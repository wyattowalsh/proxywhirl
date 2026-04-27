"""Proxy priority levels for preferring paid/premium proxies.

Implements priority-based proxy selection that prefers premium
proxies over free ones while handling fallbacks gracefully.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from loguru import logger

from proxywhirl.models import Proxy


class ProxyPriority(str, Enum):
    """Proxy priority levels."""

    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    STANDARD = "standard"
    FREE = "free"


PRIORITY_SCORES = {
    ProxyPriority.ENTERPRISE: 1000,
    ProxyPriority.PREMIUM: 500,
    ProxyPriority.STANDARD: 100,
    ProxyPriority.FREE: 1,
}


class PrioritySelector:
    """Selects proxies based on priority levels."""

    def __init__(self, strict_priority: bool = False) -> None:
        """Initialize priority selector.

        Args:
            strict_priority: If True, never select lower priority if higher available
        """
        self.strict_priority = strict_priority
        self.proxy_priorities: dict[str, ProxyPriority] = {}

    def set_priority(self, proxy_url: str, priority: ProxyPriority) -> None:
        """Set priority for a proxy.

        Args:
            proxy_url: Proxy URL
            priority: ProxyPriority level
        """
        self.proxy_priorities[proxy_url] = priority
        logger.debug(f"Set priority for {proxy_url}: {priority.value}")

    def get_priority(self, proxy_url: str) -> ProxyPriority:
        """Get priority for a proxy.

        Args:
            proxy_url: Proxy URL

        Returns:
            ProxyPriority (defaults to STANDARD)
        """
        return self.proxy_priorities.get(proxy_url, ProxyPriority.STANDARD)

    def select_by_priority(self, proxies: list[Proxy]) -> Proxy | None:
        """Select proxy with highest priority.

        Args:
            proxies: List of proxies

        Returns:
            Selected proxy or None
        """
        if not proxies:
            return None

        # Sort by priority
        sorted_proxies = sorted(
            proxies,
            key=lambda p: PRIORITY_SCORES.get(self.get_priority(p.url), 0),
            reverse=True,
        )

        if self.strict_priority:
            # Return highest priority only
            best = sorted_proxies[0]
            logger.debug(
                f"Selected highest priority proxy: {best.url} ({self.get_priority(best.url).value})"
            )
            return best
        else:
            # Can use lower priority if needed
            for proxy in sorted_proxies:
                if proxy.status == "active":
                    logger.debug(
                        f"Selected active proxy: {proxy.url} ({self.get_priority(proxy.url).value})"
                    )
                    return proxy

            # Fallback to first if none active
            return sorted_proxies[0]

    def get_priority_ranking(self, proxies: list[Proxy]) -> list[tuple[Proxy, ProxyPriority]]:
        """Get proxies ranked by priority.

        Args:
            proxies: List of proxies

        Returns:
            List of (proxy, priority) tuples sorted by priority
        """
        ranking = [(p, self.get_priority(p.url)) for p in proxies]
        return sorted(ranking, key=lambda x: PRIORITY_SCORES.get(x[1], 0), reverse=True)

    def filter_by_priority(self, proxies: list[Proxy], min_priority: ProxyPriority) -> list[Proxy]:
        """Filter proxies by minimum priority.

        Args:
            proxies: List of proxies
            min_priority: Minimum acceptable priority

        Returns:
            Filtered list of proxies
        """
        min_score = PRIORITY_SCORES.get(min_priority, 0)
        return [p for p in proxies if PRIORITY_SCORES.get(self.get_priority(p.url), 0) >= min_score]

    def get_priority_stats(self, proxies: list[Proxy]) -> dict[str, Any]:
        """Get priority distribution statistics.

        Args:
            proxies: List of proxies

        Returns:
            Dict with statistics
        """
        stats: dict[str, int] = {}
        for proxy in proxies:
            priority = self.get_priority(proxy.url).value
            stats[priority] = stats.get(priority, 0) + 1

        return {
            "total": len(proxies),
            "distribution": stats,
        }

    def bulk_set_priority(self, proxies: list[Proxy], priority: ProxyPriority) -> None:
        """Set same priority for multiple proxies.

        Args:
            proxies: List of proxies
            priority: Priority to set
        """
        for proxy in proxies:
            self.set_priority(proxy.url, priority)
        logger.info(f"Set priority {priority.value} for {len(proxies)} proxies")


_selector: PrioritySelector | None = None


def get_priority_selector() -> PrioritySelector:
    """Get global priority selector instance."""
    global _selector
    if _selector is None:
        _selector = PrioritySelector()
    return _selector
