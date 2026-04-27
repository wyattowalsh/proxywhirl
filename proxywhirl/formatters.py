"""Output formatters for CLI commands.

Provides JSON, YAML, CSV, and text formatting for proxy data.
"""

from __future__ import annotations

import csv
import json
from enum import Enum
from io import StringIO
from typing import Any

import yaml

from proxywhirl.models import Proxy


class OutputFormat(str, Enum):
    """Supported output formats."""

    TEXT = "text"
    JSON = "json"
    CSV = "csv"
    YAML = "yaml"


def format_proxies(
    proxies: list[Proxy],
    format: OutputFormat = OutputFormat.TEXT,
) -> str:
    """Format a list of proxies in the specified format.

    Args:
        proxies: List of Proxy objects to format
        format: Output format (text/json/csv/yaml)

    Returns:
        Formatted proxy data as string
    """
    if format == OutputFormat.JSON:
        return _format_json(proxies)
    elif format == OutputFormat.YAML:
        return _format_yaml(proxies)
    elif format == OutputFormat.CSV:
        return _format_csv(proxies)
    else:
        return _format_text(proxies)


def format_stats(
    stats: dict[str, Any],
    format: OutputFormat = OutputFormat.TEXT,
) -> str:
    """Format statistics in the specified format.

    Args:
        stats: Dictionary of statistics
        format: Output format

    Returns:
        Formatted stats as string
    """
    if format == OutputFormat.JSON:
        return json.dumps(stats, indent=2)
    elif format == OutputFormat.YAML:
        return yaml.dump(stats, default_flow_style=False)
    elif format == OutputFormat.CSV:
        output = StringIO()
        writer = csv.writer(output)
        for key, value in stats.items():
            writer.writerow([key, value])
        return output.getvalue()
    else:
        return "\n".join(f"{k}: {v}" for k, v in stats.items())


def _format_text(proxies: list[Proxy]) -> str:
    """Format proxies as plain text table."""
    if not proxies:
        return "No proxies found"

    lines = []
    lines.append(f"{'Proxy':<30} {'Status':<12} {'Country':<15}")
    lines.append("-" * 57)

    for proxy in proxies:
        status = (
            proxy.health_status.name
            if hasattr(proxy, "health_status") and proxy.health_status
            else "UNKNOWN"
        )
        country = getattr(proxy, "country", "Unknown")
        lines.append(f"{proxy.proxy_string:<30} {status:<12} {country:<15}")

    return "\n".join(lines)


def _format_json(proxies: list[Proxy]) -> str:
    """Format proxies as JSON."""
    data = [
        {
            "proxy": proxy.proxy_string,
            "host": proxy.host,
            "port": proxy.port,
            "protocol": proxy.protocol,
            "status": (
                proxy.health_status.name
                if hasattr(proxy, "health_status") and proxy.health_status
                else None
            ),
            "country": getattr(proxy, "country", None),
        }
        for proxy in proxies
    ]
    return json.dumps(data, indent=2)


def _format_yaml(proxies: list[Proxy]) -> str:
    """Format proxies as YAML."""
    data = [
        {
            "proxy": proxy.proxy_string,
            "host": proxy.host,
            "port": proxy.port,
            "protocol": proxy.protocol,
            "status": (
                proxy.health_status.name
                if hasattr(proxy, "health_status") and proxy.health_status
                else None
            ),
            "country": getattr(proxy, "country", None),
        }
        for proxy in proxies
    ]
    return yaml.dump(data, default_flow_style=False)


def _format_csv(proxies: list[Proxy]) -> str:
    """Format proxies as CSV."""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["proxy", "host", "port", "protocol", "status", "country"])

    for proxy in proxies:
        status = (
            proxy.health_status.name
            if hasattr(proxy, "health_status") and proxy.health_status
            else None
        )
        writer.writerow(
            [
                proxy.proxy_string,
                proxy.host,
                proxy.port,
                proxy.protocol,
                status,
                getattr(proxy, "country", None),
            ]
        )

    return output.getvalue()
