"""Export functionality for generating web dashboard data.

This module provides functions to export proxy data and statistics
for consumption by the web dashboard.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from loguru import logger

from proxywhirl.geo import batch_geolocate, enrich_proxies_with_geo
from proxywhirl.storage import SQLiteStorage


def parse_proxy_url(url: str) -> tuple[str, int]:
    """Parse proxy URL to extract IP and port.

    Args:
        url: Full proxy URL (e.g., "http://1.2.3.4:8080")

    Returns:
        Tuple of (ip, port)
    """
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        port = parsed.port or 80
        # Validate port range
        if not (0 < port <= 65535):
            port = 80
        return host, port
    except Exception:
        # Handle malformed URLs
        return "", 80


async def generate_rich_proxies(
    storage: SQLiteStorage,
    include_geo: bool = True,
    geo_sample_size: int = 5000,
) -> dict[str, Any]:
    """Generate rich proxy data from database.

    Args:
        storage: SQLiteStorage instance to query
        include_geo: Whether to include country data (slower)
        geo_sample_size: Max IPs to geolocate (rate limited)

    Returns:
        Dictionary containing proxies with metadata and aggregations
    """
    proxies_data = await storage.load()

    proxies = []
    protocol_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    country_counts: Counter[str] = Counter()

    for proxy in proxies_data:
        ip, port = parse_proxy_url(proxy.url)

        proxy_dict = {
            "ip": ip,
            "port": port,
            "protocol": proxy.protocol or "http",
            "status": proxy.health_status.value,
            "response_time": proxy.average_response_time_ms,
            "success_rate": (
                round(proxy.total_successes / proxy.total_requests * 100, 1)
                if proxy.total_requests > 0
                else None
            ),
            "total_checks": proxy.total_requests,
            "source": proxy.source.value,
            "last_checked": (
                proxy.last_success_at.isoformat()
                if proxy.last_success_at
                else proxy.last_failure_at.isoformat()
                if proxy.last_failure_at
                else None
            ),
            "created_at": proxy.created_at.isoformat() if proxy.created_at else None,
            "country": None,
            "country_code": None,
        }
        proxies.append(proxy_dict)

        protocol_counts[proxy_dict["protocol"]] += 1
        status_counts[proxy_dict["status"]] += 1
        source_counts[proxy_dict["source"]] += 1

    # Add geo data if requested
    if include_geo and proxies:
        ips = [p["ip"] for p in proxies[:geo_sample_size]]
        geo_data = await batch_geolocate(ips, max_batches=50)  # Up to 5000 IPs
        proxies = enrich_proxies_with_geo(proxies, geo_data)

        # Count countries
        for p in proxies:
            if p.get("country_code"):
                country_counts[p["country_code"]] += 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(proxies),
        "proxies": proxies,
        "aggregations": {
            "by_protocol": dict(protocol_counts),
            "by_status": dict(status_counts),
            "by_source": dict(source_counts),
            "by_country": dict(country_counts),
        },
    }


def generate_stats_from_files(proxy_dir: Path) -> dict[str, Any]:
    """Generate statistics from proxy list files.

    Args:
        proxy_dir: Path to directory containing proxy list files

    Returns:
        Dictionary containing all dashboard statistics
    """
    # Read existing metadata
    metadata_path = proxy_dir / "metadata.json"
    if not metadata_path.exists():
        logger.warning("metadata.json not found, using empty defaults")
        metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_sources": 0,
            "counts": {},
        }
    else:
        with open(metadata_path) as f:
            metadata = json.load(f)

    # Calculate file sizes
    file_sizes = {}
    files_to_check = [
        "http.txt",
        "https.txt",
        "socks4.txt",
        "socks5.txt",
        "all.txt",
        "proxies.json",
    ]
    for filename in files_to_check:
        path = proxy_dir / filename
        if path.exists():
            file_sizes[filename] = path.stat().st_size

    # Count lines in each protocol file
    proxy_counts = {}
    for protocol in ["http", "https", "socks4", "socks5"]:
        path = proxy_dir / f"{protocol}.txt"
        if path.exists():
            with open(path) as f:
                proxy_counts[protocol] = sum(1 for line in f if line.strip())
        else:
            proxy_counts[protocol] = metadata.get("counts", {}).get(protocol, 0)

    # Calculate unique proxies
    unique_proxies = set()
    for protocol in ["http", "socks4", "socks5"]:
        path = proxy_dir / f"{protocol}.txt"
        if path.exists():
            with open(path) as f:
                for line in f:
                    if line.strip():
                        unique_proxies.add(line.strip())

    return {
        "generated_at": metadata.get("generated_at", datetime.now(timezone.utc).isoformat()),
        "sources": {
            "total": metadata.get("total_sources", 0),
        },
        "proxies": {
            "total": sum(proxy_counts.values()),
            "unique": len(unique_proxies) if unique_proxies else sum(proxy_counts.values()),
            "by_protocol": proxy_counts,
        },
        "file_sizes": file_sizes,
    }


async def export_for_web(
    db_path: Path,
    output_dir: Path,
    include_stats: bool = True,
    include_rich_proxies: bool = True,
) -> dict[str, Path]:
    """Export data for the web dashboard.

    Args:
        db_path: Path to SQLite database
        output_dir: Directory to write output files
        include_stats: Whether to generate stats.json
        include_rich_proxies: Whether to generate proxies-rich.json

    Returns:
        Dictionary mapping output type to file path
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Path] = {}

    # Generate stats from text files
    if include_stats:
        logger.info("Generating stats.json...")
        stats = generate_stats_from_files(output_dir)
        stats_path = output_dir / "stats.json"
        with open(stats_path, "w") as f:
            json.dump(stats, f, indent=2)
        outputs["stats"] = stats_path
        logger.info(f"Stats saved to {stats_path}")
        logger.info(f"Total proxies: {stats['proxies']['total']}")

    # Generate rich proxy data from database
    if include_rich_proxies and db_path.exists():
        logger.info("Generating rich proxy data from database...")
        storage = SQLiteStorage(db_path)
        await storage.initialize()

        try:
            rich_data = await generate_rich_proxies(storage)
            rich_path = output_dir / "proxies-rich.json"
            with open(rich_path, "w") as f:
                json.dump(rich_data, f)
            outputs["proxies_rich"] = rich_path
            logger.info(f"Rich proxy data saved to {rich_path}")
            logger.info(f"Total rich proxies: {rich_data['total']}")
        finally:
            await storage.close()
    elif include_rich_proxies:
        logger.warning(f"Database not found at {db_path}, skipping rich proxy export")

    return outputs
