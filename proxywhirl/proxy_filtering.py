"""Advanced proxy filtering and selection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from loguru import logger


class FilterOperator(str, Enum):
    """Filter operators."""

    EQ = "eq"
    NE = "ne"
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    IN = "in"
    CONTAINS = "contains"
    REGEX = "regex"


@dataclass
class FilterRule:
    """Rule for filtering proxies."""

    field: str
    operator: FilterOperator
    value: Any


class ProxyFilter:
    """Filters proxies based on rules."""

    def __init__(self):
        """Initialize filter."""
        self._rules: list[FilterRule] = []
        self._custom_filters: list[Callable] = []

    def add_rule(self, field: str, operator: FilterOperator, value: Any) -> ProxyFilter:
        """Add a filter rule.

        Args:
            field: Proxy field to filter on
            operator: Comparison operator
            value: Value to compare

        Returns:
            Self for chaining
        """
        self._rules.append(FilterRule(field=field, operator=operator, value=value))
        return self

    def add_custom_filter(self, filter_fn: Callable) -> ProxyFilter:
        """Add a custom filter function.

        Args:
            filter_fn: Function that returns bool given a proxy

        Returns:
            Self for chaining
        """
        self._custom_filters.append(filter_fn)
        return self

    def matches(self, proxy: dict[str, Any]) -> bool:
        """Check if proxy matches all rules.

        Args:
            proxy: Proxy dict

        Returns:
            True if matches all rules
        """
        # Check filter rules
        for rule in self._rules:
            if not self._apply_rule(proxy, rule):
                return False

        # Check custom filters
        for filter_fn in self._custom_filters:
            try:
                if not filter_fn(proxy):
                    return False
            except Exception as e:
                logger.warning(f"Custom filter error: {e}")
                return False

        return True

    def _apply_rule(self, proxy: dict[str, Any], rule: FilterRule) -> bool:
        """Apply a single rule.

        Args:
            proxy: Proxy dict
            rule: Filter rule

        Returns:
            True if rule passes
        """
        value = proxy.get(rule.field)

        if rule.operator == FilterOperator.EQ:
            return value == rule.value
        elif rule.operator == FilterOperator.NE:
            return value != rule.value
        elif rule.operator == FilterOperator.GT:
            return value > rule.value
        elif rule.operator == FilterOperator.LT:
            return value < rule.value
        elif rule.operator == FilterOperator.GTE:
            return value >= rule.value
        elif rule.operator == FilterOperator.LTE:
            return value <= rule.value
        elif rule.operator == FilterOperator.IN:
            return value in rule.value
        elif rule.operator == FilterOperator.CONTAINS:
            return rule.value in str(value)
        elif rule.operator == FilterOperator.REGEX:
            import re

            try:
                return bool(re.search(rule.value, str(value)))
            except re.error:
                logger.warning(f"Invalid regex: {rule.value}")
                return False

        return False

    def filter_proxies(self, proxies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter a list of proxies.

        Args:
            proxies: List of proxy dicts

        Returns:
            Filtered proxies
        """
        return [p for p in proxies if self.matches(p)]


class ProxySelector:
    """Selects proxies based on criteria."""

    @staticmethod
    def select_by_country(proxies: list[dict[str, Any]], country: str) -> list[dict[str, Any]]:
        """Select proxies by country.

        Args:
            proxies: List of proxies
            country: Country code (e.g., 'US', 'GB')

        Returns:
            Filtered proxies
        """
        return [p for p in proxies if p.get("country", "").upper() == country.upper()]

    @staticmethod
    def select_by_protocol(proxies: list[dict[str, Any]], protocol: str) -> list[dict[str, Any]]:
        """Select proxies by protocol.

        Args:
            proxies: List of proxies
            protocol: Protocol (http, https, socks4, socks5)

        Returns:
            Filtered proxies
        """
        return [p for p in proxies if p.get("protocol", "").lower() == protocol.lower()]

    @staticmethod
    def select_healthy(proxies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Select only healthy proxies.

        Args:
            proxies: List of proxies

        Returns:
            Healthy proxies
        """
        return [p for p in proxies if p.get("status") == "healthy"]

    @staticmethod
    def select_by_speed(
        proxies: list[dict[str, Any]], min_speed: float | None = None
    ) -> list[dict[str, Any]]:
        """Select proxies by minimum speed.

        Args:
            proxies: List of proxies
            min_speed: Minimum speed in Mbps

        Returns:
            Proxies meeting speed requirement
        """
        if min_speed is None:
            return proxies

        return [p for p in proxies if p.get("speed", 0) >= min_speed]

    @staticmethod
    def select_by_uptime(
        proxies: list[dict[str, Any]], min_uptime: float | None = None
    ) -> list[dict[str, Any]]:
        """Select proxies by minimum uptime.

        Args:
            proxies: List of proxies
            min_uptime: Minimum uptime percentage (0-1)

        Returns:
            Proxies meeting uptime requirement
        """
        if min_uptime is None:
            return proxies

        return [p for p in proxies if p.get("uptime", 1.0) >= min_uptime]

    @staticmethod
    def select_random_sample(
        proxies: list[dict[str, Any]], sample_size: int
    ) -> list[dict[str, Any]]:
        """Select random sample of proxies.

        Args:
            proxies: List of proxies
            sample_size: Sample size

        Returns:
            Random sample
        """
        import random

        return random.sample(proxies, min(sample_size, len(proxies)))


class ProxyGrouping:
    """Groups proxies by criteria."""

    @staticmethod
    def group_by_country(proxies: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Group proxies by country.

        Args:
            proxies: List of proxies

        Returns:
            Dict of country -> proxies
        """
        groups: dict[str, list[dict[str, Any]]] = {}

        for proxy in proxies:
            country = proxy.get("country", "UNKNOWN")
            if country not in groups:
                groups[country] = []
            groups[country].append(proxy)

        return groups

    @staticmethod
    def group_by_protocol(proxies: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Group proxies by protocol.

        Args:
            proxies: List of proxies

        Returns:
            Dict of protocol -> proxies
        """
        groups: dict[str, list[dict[str, Any]]] = {}

        for proxy in proxies:
            protocol = proxy.get("protocol", "unknown").lower()
            if protocol not in groups:
                groups[protocol] = []
            groups[protocol].append(proxy)

        return groups

    @staticmethod
    def group_by_status(proxies: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Group proxies by status.

        Args:
            proxies: List of proxies

        Returns:
            Dict of status -> proxies
        """
        groups: dict[str, list[dict[str, Any]]] = {}

        for proxy in proxies:
            status = proxy.get("status", "unknown")
            if status not in groups:
                groups[status] = []
            groups[status].append(proxy)

        return groups
