"""Output formatters for CLI commands.

Provides JSON, YAML, CSV, and text formatting for proxy data.
"""

from __future__ import annotations

import csv
import json
from enum import Enum
from io import StringIO
from typing import Any
from urllib.parse import urlparse

import yaml

from proxywhirl.models import Proxy
from proxywhirl.utils import public_proxy_url


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
        row = _proxy_output_row(proxy)
        lines.append(f"{row['proxy']:<30} {row['status']:<12} {row['country']:<15}")

    return "\n".join(lines)


def _format_json(proxies: list[Proxy]) -> str:
    """Format proxies as JSON."""
    data = [_proxy_output_row(proxy) for proxy in proxies]
    return json.dumps(data, indent=2)


def _format_yaml(proxies: list[Proxy]) -> str:
    """Format proxies as YAML."""
    data = [_proxy_output_row(proxy) for proxy in proxies]
    return yaml.dump(data, default_flow_style=False)


def _format_csv(proxies: list[Proxy]) -> str:
    """Format proxies as CSV."""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["proxy", "host", "port", "protocol", "status", "country"])

    for proxy in proxies:
        row = _proxy_output_row(proxy)
        writer.writerow(
            [
                row["proxy"],
                row["host"],
                row["port"],
                row["protocol"],
                row["status"],
                row["country"],
            ]
        )

    return output.getvalue()


def _proxy_output_row(proxy: Proxy) -> dict[str, Any]:
    """Return a formatter-safe proxy row for current Proxy models."""
    safe_url = public_proxy_url(str(proxy.url))
    parsed = urlparse(safe_url)
    metadata = getattr(proxy, "metadata", {}) or {}
    country = (
        getattr(proxy, "country_code", None)
        or metadata.get("country_code")
        or metadata.get("country")
        or "Unknown"
    )
    status = proxy.health_status.name if getattr(proxy, "health_status", None) else "UNKNOWN"
    return {
        "proxy": safe_url,
        "host": parsed.hostname,
        "port": parsed.port,
        "protocol": proxy.protocol,
        "status": status,
        "country": country,
    }
