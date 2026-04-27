"""Full-text search over proxy metadata."""

from __future__ import annotations

from proxywhirl.models import Proxy, ProxyPool


class ProxySearch:
    """
    Full-text search over proxy metadata.

    Supports filtering by country, protocol, anonymity, tags, and metadata fields.
    """

    def __init__(self, pool: ProxyPool):
        """
        Initialize proxy search.

        Args:
            pool: ProxyPool to search
        """
        self.pool = pool

    def search_by_text(self, query: str) -> list[Proxy]:
        """
        Search proxies by text query.

        Searches in country, protocol, tags, and URL.

        Args:
            query: Search query string

        Returns:
            List of matching proxies
        """
        query_lower = query.lower()
        results = []

        for proxy in self.pool.proxies.values():
            # Search in URL
            if query_lower in proxy.url.lower():
                results.append(proxy)
                continue

            # Search in country
            if hasattr(proxy, "country") and proxy.country and query_lower in proxy.country.lower():
                results.append(proxy)
                continue

            # Search in protocol
            if query_lower in proxy.protocol.lower():
                results.append(proxy)
                continue

            # Search in tags
            if (
                hasattr(proxy, "tags")
                and proxy.tags
                and any(query_lower in tag.lower() for tag in proxy.tags)
            ):
                results.append(proxy)
                continue

        return results

    def search_by_country(self, country_code: str) -> list[Proxy]:
        """
        Search proxies by country code.

        Args:
            country_code: ISO country code (e.g., 'US')

        Returns:
            List of proxies in the specified country
        """
        results = []
        for proxy in self.pool.proxies.values():
            if hasattr(proxy, "country") and proxy.country == country_code:
                results.append(proxy)
        return results

    def search_by_protocol(self, protocol: str) -> list[Proxy]:
        """
        Search proxies by protocol.

        Args:
            protocol: Protocol name (http, https, socks5, etc.)

        Returns:
            List of proxies with the specified protocol
        """
        protocol_lower = protocol.lower()
        return [
            proxy
            for proxy in self.pool.proxies.values()
            if proxy.protocol.lower() == protocol_lower
        ]

    def search_by_anonymity(self, anonymity: str) -> list[Proxy]:
        """
        Search proxies by anonymity level.

        Args:
            anonymity: Anonymity level (transparent, anonymous, elite)

        Returns:
            List of proxies with specified anonymity
        """
        results = []
        for proxy in self.pool.proxies.values():
            if hasattr(proxy, "anonymity") and proxy.anonymity == anonymity:
                results.append(proxy)
        return results

    def search_by_tags(self, *tags: str, match_all: bool = False) -> list[Proxy]:
        """
        Search proxies by tags.

        Args:
            *tags: Tag strings to search for
            match_all: If True, proxy must have all tags; if False, any tag

        Returns:
            List of matching proxies
        """
        results = []
        search_tags = set(tags)

        for proxy in self.pool.proxies.values():
            if not hasattr(proxy, "tags"):
                continue

            proxy_tags = set(proxy.tags) if proxy.tags else set()

            if match_all:
                if search_tags.issubset(proxy_tags):
                    results.append(proxy)
            else:
                if proxy_tags & search_tags:  # Intersection
                    results.append(proxy)

        return results

    def search_by_metadata(self, **criteria) -> list[Proxy]:
        """
        Search proxies by arbitrary metadata.

        Args:
            **criteria: Field=value criteria to match

        Returns:
            List of matching proxies
        """
        results = []

        for proxy in self.pool.proxies.values():
            match = True
            for field, value in criteria.items():
                if not hasattr(proxy, field) or getattr(proxy, field) != value:
                    match = False
                    break
            if match:
                results.append(proxy)

        return results

    def search_by_region(self, region: str) -> list[Proxy]:
        """
        Search proxies by region (if available).

        Args:
            region: Region name

        Returns:
            List of proxies in the region
        """
        region_lower = region.lower()
        results = []

        for proxy in self.pool.proxies.values():
            if hasattr(proxy, "region") and proxy.region and region_lower in proxy.region.lower():
                results.append(proxy)

        return results

    def search_by_isp(self, isp: str) -> list[Proxy]:
        """
        Search proxies by ISP.

        Args:
            isp: ISP name

        Returns:
            List of proxies from the ISP
        """
        isp_lower = isp.lower()
        results = []

        for proxy in self.pool.proxies.values():
            if hasattr(proxy, "isp") and proxy.isp and isp_lower in proxy.isp.lower():
                results.append(proxy)

        return results

    def faceted_search(self, query: str) -> dict[str, list[Proxy]]:
        """
        Perform faceted search grouping results by type.

        Args:
            query: Search query

        Returns:
            Dictionary with results grouped by category
        """
        return {
            "by_text": self.search_by_text(query),
            "by_country": self.search_by_country(query),
            "by_protocol": self.search_by_protocol(query),
        }

    def combined_search(
        self,
        text: str | None = None,
        country: str | None = None,
        protocol: str | None = None,
        anonymity: str | None = None,
        tags: list[str] | None = None,
    ) -> list[Proxy]:
        """
        Perform combined search with multiple criteria.

        All specified criteria must match (AND logic).

        Args:
            text: Text query
            country: Country code
            protocol: Protocol name
            anonymity: Anonymity level
            tags: List of tags

        Returns:
            List of proxies matching all criteria
        """
        # Start with all proxies
        results = list(self.pool.proxies.values())

        if text:
            text_results = set(self.search_by_text(text))
            results = [p for p in results if p in text_results]

        if country:
            country_results = set(self.search_by_country(country))
            results = [p for p in results if p in country_results]

        if protocol:
            protocol_results = set(self.search_by_protocol(protocol))
            results = [p for p in results if p in protocol_results]

        if anonymity:
            anonymity_results = set(self.search_by_anonymity(anonymity))
            results = [p for p in results if p in anonymity_results]

        if tags:
            tag_results = set(self.search_by_tags(*tags, match_all=False))
            results = [p for p in results if p in tag_results]

        return results
