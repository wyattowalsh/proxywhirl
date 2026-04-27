"""Tagging and metadata system for storage.

Enables tagging, filtering, and querying proxies by metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger


@dataclass
class ProxyMetadata:
    """Metadata for proxy."""

    proxy_id: str
    tags: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str | None = None
    updated_at: str | None = None

    def add_tag(self, tag: str) -> bool:
        """Add tag to proxy.

        Args:
            tag: Tag name

        Returns:
            True if added
        """
        if not tag:
            return False

        normalized = tag.lower().strip()
        if normalized in self.tags:
            return False

        self.tags.add(normalized)
        return True

    def remove_tag(self, tag: str) -> bool:
        """Remove tag from proxy.

        Args:
            tag: Tag name

        Returns:
            True if removed
        """
        normalized = tag.lower().strip()
        if normalized in self.tags:
            self.tags.remove(normalized)
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        """Check if proxy has tag.

        Args:
            tag: Tag name

        Returns:
            True if has tag
        """
        normalized = tag.lower().strip()
        return normalized in self.tags

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str) -> Any | None:
        """Get metadata value.

        Args:
            key: Metadata key

        Returns:
            Value or None
        """
        return self.metadata.get(key)


class StorageTagManager:
    """Manages proxy tags and metadata."""

    def __init__(self) -> None:
        """Initialize storage tag manager."""
        self._proxies: dict[str, ProxyMetadata] = {}
        logger.debug("StorageTagManager initialized")

    def register_proxy(self, proxy_id: str) -> bool:
        """Register proxy for tagging.

        Args:
            proxy_id: Proxy ID

        Returns:
            True if registered
        """
        if proxy_id in self._proxies:
            logger.warning(f"Proxy already registered: {proxy_id}")
            return False

        self._proxies[proxy_id] = ProxyMetadata(proxy_id=proxy_id)
        logger.debug(f"Proxy registered for tagging: {proxy_id}")
        return True

    def tag_proxy(self, proxy_id: str, *tags: str) -> bool:
        """Tag a proxy.

        Args:
            proxy_id: Proxy ID
            tags: Tags to add

        Returns:
            True if tagged
        """
        if proxy_id not in self._proxies:
            return False

        metadata = self._proxies[proxy_id]
        for tag in tags:
            metadata.add_tag(tag)

        logger.debug(f"Proxy tagged: {proxy_id} - {tags}")
        return True

    def untag_proxy(self, proxy_id: str, *tags: str) -> bool:
        """Remove tags from proxy.

        Args:
            proxy_id: Proxy ID
            tags: Tags to remove

        Returns:
            True if untagged
        """
        if proxy_id not in self._proxies:
            return False

        metadata = self._proxies[proxy_id]
        for tag in tags:
            metadata.remove_tag(tag)

        logger.debug(f"Proxy untagged: {proxy_id} - {tags}")
        return True

    def get_proxies_by_tag(self, tag: str) -> list[str]:
        """Get all proxies with a specific tag.

        Args:
            tag: Tag name

        Returns:
            List of proxy IDs
        """
        normalized = tag.lower().strip()
        return [pid for pid, meta in self._proxies.items() if normalized in meta.tags]

    def get_proxies_by_tags(self, tags: list[str], match_all: bool = False) -> list[str]:
        """Get proxies matching tags.

        Args:
            tags: List of tags
            match_all: If True, proxy must have all tags

        Returns:
            List of proxy IDs
        """
        if not tags:
            return list(self._proxies.keys())

        normalized_tags = {tag.lower().strip() for tag in tags}
        results = []

        for pid, meta in self._proxies.items():
            if match_all:
                if normalized_tags.issubset(meta.tags):
                    results.append(pid)
            else:
                if meta.tags & normalized_tags:
                    results.append(pid)

        return results

    def set_proxy_metadata(self, proxy_id: str, key: str, value: Any) -> bool:
        """Set metadata on proxy.

        Args:
            proxy_id: Proxy ID
            key: Metadata key
            value: Metadata value

        Returns:
            True if set
        """
        if proxy_id not in self._proxies:
            return False

        self._proxies[proxy_id].set_metadata(key, value)
        logger.debug(f"Metadata set: {proxy_id} - {key}")
        return True

    def export_tags_report(self) -> dict[str, Any]:
        """Export tag statistics report.

        Returns:
            Dictionary with tag statistics
        """
        tag_counts: dict[str, int] = {}

        for metadata in self._proxies.values():
            for tag in metadata.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return {
            "total_proxies": len(self._proxies),
            "total_unique_tags": len(tag_counts),
            "tag_distribution": tag_counts,
        }
