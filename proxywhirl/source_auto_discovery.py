"""Auto-discovery system for new proxy sources.

Automatically discovers and integrates new proxy sources
through configuration scanning, API discovery, and plugins.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from loguru import logger


class DiscoveryMethod(str, Enum):
    """Methods for discovering proxy sources."""

    CONFIGURATION = "configuration"
    API = "api"
    PLUGIN = "plugin"
    WEB_SCAN = "web_scan"


@dataclass
class DiscoveredSource:
    """Represents a discovered proxy source."""

    name: str
    url: str
    method: DiscoveryMethod
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified: bool = False
    proxy_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"{self.name} ({self.method.value})"


class SourceDiscoveryEngine:
    """Engine for discovering new proxy sources."""

    def __init__(self) -> None:
        """Initialize source discovery engine."""
        self._sources: dict[str, DiscoveredSource] = {}
        self._discovery_handlers: dict[str, list[Callable]] = {}
        logger.debug("SourceDiscoveryEngine initialized")

    def register_discovery_handler(self, method: DiscoveryMethod, handler: Callable) -> None:
        """Register a discovery handler.

        Args:
            method: Discovery method
            handler: Callable to discover sources
        """
        method_name = method.value
        if method_name not in self._discovery_handlers:
            self._discovery_handlers[method_name] = []
        self._discovery_handlers[method_name].append(handler)
        logger.debug(f"Discovery handler registered: {method_name}")

    def discover_sources(self, method: DiscoveryMethod) -> list[DiscoveredSource]:
        """Discover sources using a specific method.

        Args:
            method: Discovery method

        Returns:
            List of discovered sources
        """
        method_name = method.value
        discovered = []

        if method_name not in self._discovery_handlers:
            logger.warning(f"No handlers registered for method: {method_name}")
            return discovered

        for handler in self._discovery_handlers[method_name]:
            try:
                sources = handler()
                discovered.extend(sources)
                logger.debug(f"Handler found {len(sources)} sources: {method_name}")
            except Exception as e:
                logger.error(f"Discovery handler failed: {method_name} - {e}")

        return discovered

    def register_source(self, source: DiscoveredSource) -> bool:
        """Register a discovered source.

        Args:
            source: Discovered source

        Returns:
            True if registered
        """
        if source.name in self._sources:
            logger.warning(f"Source already registered: {source.name}")
            return False

        self._sources[source.name] = source
        logger.info(f"Source registered: {source}")
        return True

    def get_source(self, name: str) -> DiscoveredSource | None:
        """Get a discovered source.

        Args:
            name: Source name

        Returns:
            DiscoveredSource or None
        """
        return self._sources.get(name)

    def verify_source(self, name: str, proxy_count: int = 0) -> bool:
        """Mark a source as verified.

        Args:
            name: Source name
            proxy_count: Number of proxies found

        Returns:
            True if verified
        """
        if name not in self._sources:
            return False

        source = self._sources[name]
        source.verified = True
        source.proxy_count = proxy_count
        logger.info(f"Source verified: {name} ({proxy_count} proxies)")
        return True

    def get_verified_sources(self) -> list[DiscoveredSource]:
        """Get all verified sources.

        Returns:
            List of verified sources
        """
        return [s for s in self._sources.values() if s.verified]

    def get_unverified_sources(self) -> list[DiscoveredSource]:
        """Get all unverified sources.

        Returns:
            List of unverified sources
        """
        return [s for s in self._sources.values() if not s.verified]

    def export_metrics(self) -> dict[str, Any]:
        """Export discovery metrics.

        Returns:
            Dictionary of metrics
        """
        return {
            "total_sources": len(self._sources),
            "verified_sources": len(self.get_verified_sources()),
            "unverified_sources": len(self.get_unverified_sources()),
            "total_proxies": sum(s.proxy_count for s in self._sources.values()),
            "sources_by_method": {
                method: len([s for s in self._sources.values() if s.method.value == method])
                for method in DiscoveryMethod
            },
        }
