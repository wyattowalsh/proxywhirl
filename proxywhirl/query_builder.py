"""Fluent query builder API for ProxyWhirl proxy selection."""

from __future__ import annotations

from typing import Any

from proxywhirl.models import Proxy, ProxyPool


class ProxyQuery:
    """
    Fluent query builder for selecting proxies with filtering and pagination.

    Usage:
        query = (ProxyQuery()
                 .by_country("US")
                 .by_protocol("HTTP")
                 .with_min_anonymity("elite")
                 .limit(10)
                 .build())
    """

    def __init__(self, pool: ProxyPool | None = None):
        """
        Initialize the query builder.

        Args:
            pool: Optional proxy pool to query (can be set later with set_pool)
        """
        self.pool = pool
        self.filters: dict[str, Any] = {}
        self.sorting: list[tuple[str, str]] = []
        self._limit_value: int | None = None
        self._offset_value: int = 0

    def set_pool(self, pool: ProxyPool) -> ProxyQuery:
        """
        Set the proxy pool to query.

        Args:
            pool: ProxyPool instance

        Returns:
            Self for chaining
        """
        self.pool = pool
        return self

    def by_country(self, country_code: str) -> ProxyQuery:
        """
        Filter by country code.

        Args:
            country_code: ISO 3166-1 alpha-2 country code (e.g., "US", "GB")

        Returns:
            Self for chaining
        """
        self.filters["country"] = country_code
        return self

    def by_protocol(self, protocol: str) -> ProxyQuery:
        """
        Filter by proxy protocol.

        Args:
            protocol: Protocol name (http, https, socks4, socks5)

        Returns:
            Self for chaining
        """
        self.filters["protocol"] = protocol.lower()
        return self

    def by_protocols(self, *protocols: str) -> ProxyQuery:
        """
        Filter by multiple protocols.

        Args:
            *protocols: Multiple protocol names

        Returns:
            Self for chaining
        """
        self.filters["protocols"] = [p.lower() for p in protocols]
        return self

    def with_min_anonymity(self, anonymity: str) -> ProxyQuery:
        """
        Filter by minimum anonymity level.

        Args:
            anonymity: Anonymity level (transparent, anonymous, elite)

        Returns:
            Self for chaining
        """
        self.filters["min_anonymity"] = anonymity.lower()
        return self

    def with_anonymity(self, anonymity: str) -> ProxyQuery:
        """
        Filter by exact anonymity level.

        Args:
            anonymity: Anonymity level (transparent, anonymous, elite)

        Returns:
            Self for chaining
        """
        self.filters["anonymity"] = anonymity.lower()
        return self

    def with_tags(self, *tags: str) -> ProxyQuery:
        """
        Filter by proxy tags.

        Args:
            *tags: Tag strings to match

        Returns:
            Self for chaining
        """
        self.filters["tags"] = list(tags)
        return self

    def with_any_tags(self, *tags: str) -> ProxyQuery:
        """
        Filter by any of the provided tags.

        Args:
            *tags: Tag strings to match (OR logic)

        Returns:
            Self for chaining
        """
        self.filters["any_tags"] = list(tags)
        return self

    def exclude_countries(self, *countries: str) -> ProxyQuery:
        """
        Exclude proxies from specified countries.

        Args:
            *countries: ISO country codes to exclude

        Returns:
            Self for chaining
        """
        self.filters["exclude_countries"] = list(countries)
        return self

    def healthy_only(self) -> ProxyQuery:
        """
        Filter to only healthy proxies.

        Returns:
            Self for chaining
        """
        self.filters["healthy_only"] = True
        return self

    def working_only(self) -> ProxyQuery:
        """
        Filter to only working proxies (exclude dead).

        Returns:
            Self for chaining
        """
        self.filters["working_only"] = True
        return self

    def with_min_success_rate(self, rate: float) -> ProxyQuery:
        """
        Filter by minimum success rate.

        Args:
            rate: Success rate between 0.0 and 1.0

        Returns:
            Self for chaining
        """
        if not 0.0 <= rate <= 1.0:
            msg = f"Success rate must be between 0.0 and 1.0, got {rate}"
            raise ValueError(msg)
        self.filters["min_success_rate"] = rate
        return self

    def with_max_latency_ms(self, latency_ms: float) -> ProxyQuery:
        """
        Filter by maximum latency.

        Args:
            latency_ms: Maximum latency in milliseconds

        Returns:
            Self for chaining
        """
        self.filters["max_latency_ms"] = latency_ms
        return self

    def sort_by(self, field: str, order: str = "asc") -> ProxyQuery:
        """
        Add a sort criterion.

        Args:
            field: Field name to sort by (country, latency, success_rate)
            order: Sort order (asc or desc)

        Returns:
            Self for chaining
        """
        if order.lower() not in ("asc", "desc"):
            msg = f"Sort order must be 'asc' or 'desc', got {order}"
            raise ValueError(msg)
        self.sorting.append((field, order.lower()))
        return self

    def sort_by_latency(self, order: str = "asc") -> ProxyQuery:
        """
        Sort by latency.

        Args:
            order: asc for lowest latency first, desc for highest

        Returns:
            Self for chaining
        """
        return self.sort_by("latency", order)

    def sort_by_success_rate(self, order: str = "desc") -> ProxyQuery:
        """
        Sort by success rate.

        Args:
            order: asc for lowest first, desc for highest

        Returns:
            Self for chaining
        """
        return self.sort_by("success_rate", order)

    def limit(self, count: int) -> ProxyQuery:
        """
        Limit result count.

        Args:
            count: Maximum number of results

        Returns:
            Self for chaining
        """
        if count < 1:
            msg = f"Limit must be >= 1, got {count}"
            raise ValueError(msg)
        self._limit_value = count
        return self

    def offset(self, count: int) -> ProxyQuery:
        """
        Skip first N results.

        Args:
            count: Number of results to skip

        Returns:
            Self for chaining
        """
        if count < 0:
            msg = f"Offset must be >= 0, got {count}"
            raise ValueError(msg)
        self._offset_value = count
        return self

    def first(self) -> Proxy | None:
        """
        Get the first result.

        Returns:
            First Proxy matching filters, or None
        """
        results = self.build()
        return results[0] if results else None

    def count(self) -> int:
        """
        Count matching proxies.

        Returns:
            Number of proxies matching filters
        """
        return len(self.build())

    def exists(self) -> bool:
        """
        Check if any proxy matches filters.

        Returns:
            True if at least one proxy matches
        """
        return self.count() > 0

    def build(self) -> list[Proxy]:
        """
        Execute the query and return matching proxies.

        Returns:
            List of Proxy objects matching all filters

        Raises:
            ValueError: If pool is not set
        """
        if self.pool is None:
            msg = "Pool must be set before building query"
            raise ValueError(msg)

        # Start with all proxies
        proxies = list(self.pool.proxies.values())

        # Apply filters
        for proxy in proxies[:]:
            # Country filter
            if "country" in self.filters:
                if getattr(proxy, "country", None) != self.filters["country"]:
                    proxies.remove(proxy)
                    continue

            # Protocol filter
            if "protocol" in self.filters:
                if getattr(proxy, "protocol", "").lower() != self.filters["protocol"]:
                    proxies.remove(proxy)
                    continue

            # Multiple protocols filter
            if "protocols" in self.filters:
                if getattr(proxy, "protocol", "").lower() not in self.filters["protocols"]:
                    proxies.remove(proxy)
                    continue

            # Anonymity filters
            if "min_anonymity" in self.filters:
                anonymity_levels = {"transparent": 0, "anonymous": 1, "elite": 2}
                proxy_anon = anonymity_levels.get(getattr(proxy, "anonymity", "transparent"), 0)
                min_anon = anonymity_levels.get(self.filters["min_anonymity"], 0)
                if proxy_anon < min_anon:
                    proxies.remove(proxy)
                    continue

            if "anonymity" in self.filters:
                if getattr(proxy, "anonymity", None) != self.filters["anonymity"]:
                    proxies.remove(proxy)
                    continue

            # Tags filter (all tags must match)
            if "tags" in self.filters:
                proxy_tags = set(getattr(proxy, "tags", []))
                filter_tags = set(self.filters["tags"])
                if not filter_tags.issubset(proxy_tags):
                    proxies.remove(proxy)
                    continue

            # Any tags filter (at least one tag must match)
            if "any_tags" in self.filters:
                proxy_tags = set(getattr(proxy, "tags", []))
                filter_tags = set(self.filters["any_tags"])
                if not proxy_tags.intersection(filter_tags):
                    proxies.remove(proxy)
                    continue

            # Exclude countries filter
            if "exclude_countries" in self.filters:
                if getattr(proxy, "country", None) in self.filters["exclude_countries"]:
                    proxies.remove(proxy)
                    continue

            # Health filters
            if self.filters.get("healthy_only"):
                from proxywhirl.models import HealthStatus

                if getattr(proxy, "health_status", None) != HealthStatus.HEALTHY:
                    proxies.remove(proxy)
                    continue

            if self.filters.get("working_only"):
                from proxywhirl.models import HealthStatus

                if getattr(proxy, "health_status", None) == HealthStatus.DEAD:
                    proxies.remove(proxy)
                    continue

            # Success rate filter
            if "min_success_rate" in self.filters:
                success_rate = getattr(proxy, "success_rate", 0.0)
                if success_rate < self.filters["min_success_rate"]:
                    proxies.remove(proxy)
                    continue

            # Latency filter
            if "max_latency_ms" in self.filters:
                latency = getattr(proxy, "latency_ms", float("inf"))
                if latency > self.filters["max_latency_ms"]:
                    proxies.remove(proxy)
                    continue

        # Apply sorting
        for field, order in reversed(self.sorting):
            reverse = order == "desc"
            if field == "latency":
                proxies.sort(
                    key=lambda p: getattr(p, "latency_ms", float("inf")),
                    reverse=reverse,
                )
            elif field == "success_rate":
                proxies.sort(
                    key=lambda p: getattr(p, "success_rate", 0.0),
                    reverse=reverse,
                )
            elif field == "country":
                proxies.sort(
                    key=lambda p: getattr(p, "country", ""),
                    reverse=reverse,
                )

        # Apply offset and limit
        if self._offset_value > 0:
            proxies = proxies[self._offset_value :]

        if self._limit_value is not None:
            proxies = proxies[: self._limit_value]

        return proxies

    def __repr__(self) -> str:
        """Return string representation of query."""
        parts = []
        for key, value in self.filters.items():
            parts.append(f"{key}={value}")
        for field, order in self.sorting:
            parts.append(f"sort_by({field}, {order})")
        if self._limit_value:
            parts.append(f"limit({self._limit_value})")
        if self._offset_value:
            parts.append(f"offset({self._offset_value})")
        return f"ProxyQuery({', '.join(parts)})"
