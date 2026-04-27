"""Tagging system for proxy metadata."""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger


@dataclass
class Tag:
    """A tag for proxy metadata."""

    name: str
    category: str | None = None
    description: str | None = None
    color: str = "#808080"

    def __hash__(self) -> int:
        """Hash by name for set operations."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Compare by name."""
        if isinstance(other, Tag):
            return self.name == other.name
        return False


class TagManager:
    """
    Manage tags for proxy metadata.

    Supports tagging proxies with categories like:
    - "datacenter", "residential", "vpn"
    - "fast", "reliable", "cheap"
    - "geo-us", "geo-eu", "geo-asia"
    """

    # Predefined tag categories
    PROXY_TYPE_TAGS = {
        "datacenter": Tag("datacenter", "type", "Datacenter IP", "#FF6B6B"),
        "residential": Tag("residential", "type", "Residential IP", "#4ECDC4"),
        "vpn": Tag("vpn", "type", "VPN service", "#45B7D1"),
        "mobile": Tag("mobile", "type", "Mobile IP", "#96CEB4"),
    }

    QUALITY_TAGS = {
        "fast": Tag("fast", "quality", "Low latency", "#2ECC71"),
        "reliable": Tag("reliable", "quality", "High uptime", "#27AE60"),
        "cheap": Tag("cheap", "quality", "Low cost", "#F39C12"),
        "stable": Tag("stable", "quality", "Consistent performance", "#3498DB"),
    }

    GEO_TAGS = {
        "geo-us": Tag("geo-us", "geo", "United States", "#FF6B6B"),
        "geo-eu": Tag("geo-eu", "geo", "European Union", "#4ECDC4"),
        "geo-asia": Tag("geo-asia", "geo", "Asia Pacific", "#45B7D1"),
        "geo-other": Tag("geo-other", "geo", "Other regions", "#95A5A6"),
    }

    def __init__(self):
        """Initialize tag manager."""
        self.tags: dict[str, Tag] = {}
        self.proxy_tags: dict[str, set[str]] = {}  # proxy_id -> set of tag names

        # Add predefined tags
        for tag in [
            *self.PROXY_TYPE_TAGS.values(),
            *self.QUALITY_TAGS.values(),
            *self.GEO_TAGS.values(),
        ]:
            self.register_tag(tag)

    def register_tag(self, tag: Tag) -> None:
        """
        Register a tag.

        Args:
            tag: Tag to register
        """
        self.tags[tag.name] = tag
        logger.debug(f"Registered tag: {tag.name}")

    def unregister_tag(self, tag_name: str) -> None:
        """
        Unregister a tag.

        Args:
            tag_name: Tag name to unregister
        """
        if tag_name in self.tags:
            del self.tags[tag_name]
            # Remove from all proxies
            for tags in self.proxy_tags.values():
                tags.discard(tag_name)
            logger.debug(f"Unregistered tag: {tag_name}")

    def tag_proxy(self, proxy_id: str, *tag_names: str) -> None:
        """
        Add tags to a proxy.

        Args:
            proxy_id: Proxy identifier
            *tag_names: Tag names to add
        """
        if proxy_id not in self.proxy_tags:
            self.proxy_tags[proxy_id] = set()

        for tag_name in tag_names:
            if tag_name not in self.tags:
                logger.warning(f"Tag not registered: {tag_name}")
                continue

            self.proxy_tags[proxy_id].add(tag_name)

        logger.debug(f"Tagged proxy {proxy_id}: {', '.join(tag_names)}")

    def untag_proxy(self, proxy_id: str, *tag_names: str) -> None:
        """
        Remove tags from a proxy.

        Args:
            proxy_id: Proxy identifier
            *tag_names: Tag names to remove
        """
        if proxy_id in self.proxy_tags:
            for tag_name in tag_names:
                self.proxy_tags[proxy_id].discard(tag_name)

            logger.debug(f"Untagged proxy {proxy_id}: {', '.join(tag_names)}")

    def get_proxy_tags(self, proxy_id: str) -> set[str]:
        """
        Get tags for a proxy.

        Args:
            proxy_id: Proxy identifier

        Returns:
            Set of tag names
        """
        return self.proxy_tags.get(proxy_id, set()).copy()

    def has_tag(self, proxy_id: str, tag_name: str) -> bool:
        """
        Check if proxy has a tag.

        Args:
            proxy_id: Proxy identifier
            tag_name: Tag name

        Returns:
            True if proxy has tag
        """
        return tag_name in self.proxy_tags.get(proxy_id, set())

    def find_proxies_by_tag(self, tag_name: str) -> list[str]:
        """
        Find all proxies with a tag.

        Args:
            tag_name: Tag name

        Returns:
            List of proxy IDs
        """
        return [proxy_id for proxy_id, tags in self.proxy_tags.items() if tag_name in tags]

    def find_proxies_by_tags(
        self,
        *tag_names: str,
        match_all: bool = False,
    ) -> list[str]:
        """
        Find proxies by multiple tags.

        Args:
            *tag_names: Tag names to search for
            match_all: If True, proxy must have all tags; if False, any tag

        Returns:
            List of proxy IDs
        """
        search_tags = set(tag_names)

        results = []
        for proxy_id, tags in self.proxy_tags.items():
            if match_all:
                if search_tags.issubset(tags):
                    results.append(proxy_id)
            else:
                if tags & search_tags:  # Intersection
                    results.append(proxy_id)

        return results

    def get_tag_stats(self) -> dict[str, int]:
        """
        Get tag statistics.

        Returns:
            Dictionary with stats
        """
        stats = {}
        for tag_name in self.tags:
            count = len(self.find_proxies_by_tag(tag_name))
            stats[tag_name] = count

        return stats

    def remove_proxy(self, proxy_id: str) -> None:
        """
        Remove all tags for a proxy.

        Args:
            proxy_id: Proxy identifier
        """
        if proxy_id in self.proxy_tags:
            del self.proxy_tags[proxy_id]
