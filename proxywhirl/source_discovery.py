"""Auto-discovery of proxy sources from GitHub and other repositories."""

from __future__ import annotations

import re
from dataclasses import dataclass

from loguru import logger


@dataclass
class DiscoveredSource:
    """A discovered proxy source."""

    name: str
    url: str
    source_type: str  # "github", "http", "rss", etc.
    format: str  # "json", "csv", "plaintext", "html", etc.
    repository: str | None = None
    last_discovered: float = 0.0
    reliability_score: float = 0.5  # 0.0-1.0


class SourceDiscovery:
    """
    Auto-discover proxy sources from GitHub and web repositories.

    Can scan GitHub for proxy lists, RSS feeds, and other sources.
    """

    GITHUB_PROXY_LIST_PATTERNS = [
        r"proxy[_-]list",
        r"free[_-]proxy",
        r"proxy[_-]server",
        r"proxy[_-]crawler",
        r"http[_-]proxy",
    ]

    RSS_PROXY_FEED_PATTERNS = [
        r"proxy.*feed",
        r"feed.*proxy",
        r"proxy.*rss",
        r"rss.*proxy",
    ]

    def __init__(self):
        """Initialize source discovery."""
        self.discovered_sources: dict[str, DiscoveredSource] = {}
        self.scanned_repositories: set[str] = set()

    def discover_from_github(
        self,
        query: str = "proxy",
        language: str | None = None,
    ) -> list[DiscoveredSource]:
        """
        Discover proxy sources from GitHub.

        Args:
            query: Search query
            language: Optional language filter (e.g., "python")

        Returns:
            List of discovered sources
        """
        discovered = []

        # Simulate GitHub API search (in real implementation, use github API)
        logger.info(f"Searching GitHub for proxy sources: {query}")

        # In a real implementation, would call GitHub API here
        # For now, return empty list (implementation would fetch actual results)
        # This is a stub showing the interface

        return discovered

    def discover_from_github_topic(
        self,
        topic: str = "proxy-list",
    ) -> list[DiscoveredSource]:
        """
        Discover proxy sources from GitHub topics.

        Args:
            topic: GitHub topic to search

        Returns:
            List of discovered sources
        """
        logger.info(f"Searching GitHub topic: {topic}")

        # Stub for real GitHub API call
        return []

    def discover_from_raw_files(
        self,
        repository: str,
        patterns: list[str] | None = None,
    ) -> list[DiscoveredSource]:
        """
        Discover proxy list files in a repository.

        Args:
            repository: GitHub repository (user/repo)
            patterns: Optional file patterns to search for

        Returns:
            List of discovered sources
        """
        if patterns is None:
            patterns = self.GITHUB_PROXY_LIST_PATTERNS

        discovered = []

        logger.info(f"Scanning {repository} for proxy lists")

        # Look for common proxy list files
        common_filenames = [
            "proxies.txt",
            "proxy_list.txt",
            "proxies.json",
            "proxy_list.json",
            "proxies.csv",
            "proxy_list.csv",
            "README.md",
            "PROXIES.md",
        ]

        # In real implementation, would use GitHub API to search files
        for filename in common_filenames:
            raw_url = f"https://raw.githubusercontent.com/{repository}/main/{filename}"
            source = DiscoveredSource(
                name=f"{repository}/{filename}",
                url=raw_url,
                source_type="github",
                format=self._infer_format(filename),
                repository=repository,
            )
            discovered.append(source)

        return discovered

    def discover_from_rss(
        self,
        feed_url: str,
    ) -> list[DiscoveredSource]:
        """
        Discover proxy sources from RSS feed.

        Args:
            feed_url: RSS feed URL

        Returns:
            List of discovered sources
        """
        logger.info(f"Scanning RSS feed: {feed_url}")

        # In real implementation, would fetch and parse RSS feed
        return []

    def validate_source(self, source: DiscoveredSource) -> bool:
        """
        Validate that a discovered source is accessible.

        Args:
            source: Source to validate

        Returns:
            True if source is accessible and valid
        """
        logger.debug(f"Validating source: {source.name}")

        # In real implementation, would attempt to fetch and parse source
        # For now, stub implementation
        return True

    def register_source(self, source: DiscoveredSource) -> None:
        """
        Register a discovered source.

        Args:
            source: Source to register
        """
        self.discovered_sources[source.name] = source
        logger.info(f"Registered discovered source: {source.name}")

    def get_discovered_sources(
        self,
        min_reliability: float = 0.5,
    ) -> list[DiscoveredSource]:
        """
        Get all discovered sources above reliability threshold.

        Args:
            min_reliability: Minimum reliability score

        Returns:
            List of sources
        """
        return [
            s for s in self.discovered_sources.values() if s.reliability_score >= min_reliability
        ]

    def _infer_format(self, filename: str) -> str:
        """
        Infer format from filename.

        Args:
            filename: Filename to infer from

        Returns:
            Format string
        """
        if filename.endswith(".json"):
            return "json"
        elif filename.endswith(".csv"):
            return "csv"
        elif filename.endswith(".md") or filename.endswith(".txt"):
            return "plaintext"
        elif filename.endswith(".html"):
            return "html"
        else:
            return "unknown"

    def _extract_urls(self, content: str) -> list[str]:
        """
        Extract URLs from content.

        Args:
            content: Content to extract from

        Returns:
            List of URLs found
        """
        url_pattern = r"https?://[^\s]+"
        return re.findall(url_pattern, content)

    def get_discovery_stats(self) -> dict[str, int | dict]:  # type: ignore[type-arg]
        """
        Get discovery statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "total_discovered": len(self.discovered_sources),
            "repositories_scanned": len(self.scanned_repositories),
            "by_source_type": {
                source_type: sum(
                    1 for s in self.discovered_sources.values() if s.source_type == source_type
                )
                for source_type in {s.source_type for s in self.discovered_sources.values()}
            },
        }
