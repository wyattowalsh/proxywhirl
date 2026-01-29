"""Export functionality for generating web dashboard data.

This module provides functions to export proxy data and statistics
for consumption by the web dashboard.
"""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from loguru import logger

from proxywhirl.geo import batch_geolocate, enrich_proxies_with_geo
from proxywhirl.sources import ALL_HTTP_SOURCES, ALL_SOCKS4_SOURCES, ALL_SOCKS5_SOURCES
from proxywhirl.storage import SQLiteStorage

# Response time distribution bins (ms): (min, max, label)
RESPONSE_TIME_BINS: list[tuple[float, float, str]] = [
    (0, 100, "<100ms"),
    (100, 500, "100-500ms"),
    (500, 1000, "500ms-1s"),
    (1000, 2000, "1-2s"),
    (2000, 5000, "2-5s"),
    (5000, float("inf"), ">5s"),
]

# Continent code to name mapping
CONTINENT_NAMES = {
    "AF": "Africa",
    "AN": "Antarctica",
    "AS": "Asia",
    "EU": "Europe",
    "NA": "North America",
    "OC": "Oceania",
    "SA": "South America",
}


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
    max_age_hours: int = 72,
) -> dict[str, Any]:
    """Generate rich proxy data from database.

    Args:
        storage: SQLiteStorage instance to query
        include_geo: Whether to include country data (slower)
        geo_sample_size: Max IPs to geolocate (rate limited)
        max_age_hours: Only include proxies validated within this time window.
            Default: 72 hours (36 runs at 2h schedule). Set to 0 to include all proxies.

    Returns:
        Dictionary containing proxies with metadata and aggregations
    """
    if max_age_hours > 0:
        proxies_data = await storage.load_validated(max_age_hours)
    else:
        proxies_data = await storage.load()

    proxies = []
    seen_addresses: set[str] = set()  # Track unique IP:port combinations
    protocol_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    country_counts: Counter[str] = Counter()
    port_counts: Counter[int] = Counter()
    continent_counts: Counter[str] = Counter()
    response_times: list[float] = []

    # For source flow (Sankey) data
    source_flow: defaultdict[tuple[str, str, str], int] = defaultdict(int)

    for proxy in proxies_data:
        ip, port = parse_proxy_url(proxy["url"])

        # Deduplicate by IP:port (same proxy may appear with different protocols)
        addr = f"{ip}:{port}"
        if addr in seen_addresses:
            continue
        seen_addresses.add(addr)

        total_checks = proxy.get("total_checks", 0) or 0
        total_successes = proxy.get("total_successes", 0) or 0
        last_success = proxy.get("last_success_at")
        last_failure = proxy.get("last_failure_at")
        discovered_at = proxy.get("discovered_at")
        avg_response = proxy.get("avg_response_time_ms")

        proxy_dict = {
            "ip": ip,
            "port": port,
            "protocol": proxy.get("protocol") or "http",
            "status": proxy.get("health_status", "unknown"),
            "response_time": avg_response,
            "success_rate": (
                round(total_successes / total_checks * 100, 1) if total_checks > 0 else None
            ),
            "total_checks": total_checks,
            "source": proxy.get("source", "fetched"),
            "last_checked": (
                last_success.isoformat()
                if last_success
                else last_failure.isoformat()
                if last_failure
                else None
            ),
            "created_at": discovered_at.isoformat() if discovered_at else None,
            "country": None,
            "country_code": proxy.get("country_code"),
            "continent_code": proxy.get("continent_code"),
        }
        proxies.append(proxy_dict)

        protocol_counts[proxy_dict["protocol"]] += 1
        status_counts[proxy_dict["status"]] += 1
        source_counts[proxy_dict["source"]] += 1
        port_counts[port] += 1

        # Collect response times for statistics
        if avg_response is not None and avg_response > 0:
            response_times.append(avg_response)

    # Add geo data if requested
    if include_geo and proxies:
        ips = [p["ip"] for p in proxies[:geo_sample_size]]
        geo_data = await batch_geolocate(ips, max_batches=50)  # Up to 5000 IPs
        proxies = enrich_proxies_with_geo(proxies, geo_data)

        # Count countries and continents, build source flow
        for p in proxies:
            country_code = p.get("country_code")
            continent_code = p.get("continent_code")
            if country_code:
                country_counts[country_code] += 1
            if continent_code:
                continent_counts[continent_code] += 1

            # Build source flow data (source → protocol → country)
            source = p.get("source", "unknown")
            protocol = p.get("protocol", "http")
            country = country_code or "Unknown"
            source_flow[(source, protocol, country)] += 1

    # Build response time distribution
    response_time_distribution = []
    for bin_min, bin_max, bin_label in RESPONSE_TIME_BINS:
        count = sum(1 for rt in response_times if bin_min <= rt < bin_max)
        response_time_distribution.append(
            {
                "range": bin_label,
                "min": bin_min,
                "max": bin_max if bin_max != float("inf") else None,
                "count": count,
            }
        )

    # Build port distribution (top 15 + others)
    top_ports = port_counts.most_common(15)
    by_port = [{"port": port, "count": count} for port, count in top_ports]
    other_port_count = sum(
        count for port, count in port_counts.items() if port not in dict(top_ports)
    )
    if other_port_count > 0:
        by_port.append({"port": 0, "count": other_port_count, "label": "Other"})

    # Performance statistics
    performance = {}
    if response_times:
        sorted_times = sorted(response_times)
        p95_idx = int(len(sorted_times) * 0.95)
        performance = {
            "avg_ms": round(statistics.mean(response_times), 1),
            "median_ms": round(statistics.median(response_times), 1),
            "p95_ms": round(
                sorted_times[p95_idx] if p95_idx < len(sorted_times) else sorted_times[-1], 1
            ),
            "min_ms": round(min(response_times), 1),
            "max_ms": round(max(response_times), 1),
            "samples": len(response_times),
        }

    # Build source flow for Sankey (limit to top entries)
    source_flow_list = [
        {"source": s, "protocol": p, "country": c, "count": cnt}
        for (s, p, c), cnt in sorted(source_flow.items(), key=lambda x: -x[1])[:200]
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(proxies),
        "proxies": proxies,
        "aggregations": {
            "by_protocol": dict(protocol_counts),
            "by_status": dict(status_counts),
            "by_source": dict(source_counts),
            "by_country": dict(country_counts),
            "by_port": by_port,
            "by_continent": dict(continent_counts),
            "response_time_distribution": response_time_distribution,
            "performance": performance,
            "source_flow": source_flow_list,
        },
    }


def generate_stats_from_files(proxy_dir: Path) -> dict[str, Any]:
    """Generate statistics from proxy list files and rich proxy data.

    Args:
        proxy_dir: Path to directory containing proxy list files

    Returns:
        Dictionary containing all dashboard statistics including health,
        performance, validation, geographic, and source ranking data
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

    # Read rich proxy data for aggregations
    rich_path = proxy_dir / "proxies-rich.json"
    rich_data: dict[str, Any] = {}
    if rich_path.exists():
        try:
            with open(rich_path) as f:
                rich_data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to read proxies-rich.json: {e}")

    aggregations = rich_data.get("aggregations", {})

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

    # Use unique count as the primary total (avoids HTTP/HTTPS double-counting)
    unique_count = len(unique_proxies) if unique_proxies else 0

    # Build health stats from status aggregation
    status_agg = aggregations.get("by_status", {})
    health = {
        "healthy": status_agg.get("healthy", 0),
        "unhealthy": status_agg.get("unhealthy", 0),
        "dead": status_agg.get("dead", 0),
        "unknown": status_agg.get("unknown", 0),
    }
    total_validated = health["healthy"] + health["unhealthy"] + health["dead"]

    # Performance stats from aggregations
    perf_agg = aggregations.get("performance", {})
    performance = {
        "avg_response_ms": perf_agg.get("avg_ms"),
        "median_response_ms": perf_agg.get("median_ms"),
        "p95_response_ms": perf_agg.get("p95_ms"),
        "min_response_ms": perf_agg.get("min_ms"),
        "max_response_ms": perf_agg.get("max_ms"),
        "samples": perf_agg.get("samples", 0),
    }

    # Validation stats
    validation = {
        "total_validated": total_validated,
        "success_rate_pct": round(health["healthy"] / total_validated * 100, 1)
        if total_validated > 0
        else 0,
    }

    # Geographic stats
    country_agg = aggregations.get("by_country", {})
    continent_agg = aggregations.get("by_continent", {})
    top_countries = sorted(
        [{"code": k, "count": v} for k, v in country_agg.items()],
        key=lambda x: -x["count"],
    )[:15]
    geographic = {
        "total_countries": len(country_agg),
        "top_countries": top_countries,
        "by_continent": {
            code: {"name": CONTINENT_NAMES.get(code, code), "count": count}
            for code, count in continent_agg.items()
        },
    }

    # Source ranking
    source_agg = aggregations.get("by_source", {})
    top_sources = sorted(
        [{"name": k, "count": v} for k, v in source_agg.items()],
        key=lambda x: -x["count"],
    )[:20]
    sources_ranking = {
        "total_active": len(source_agg),
        "top_sources": top_sources,
    }

    # Include pre-computed aggregations for frontend
    response_time_distribution = aggregations.get("response_time_distribution", [])
    by_port = aggregations.get("by_port", [])
    source_flow = aggregations.get("source_flow", [])

    return {
        "generated_at": metadata.get("generated_at", datetime.now(timezone.utc).isoformat()),
        "sources": {
            "total": metadata.get("total_sources", 0),
        },
        "proxies": {
            "total": unique_count,
            "unique": unique_count,
            "by_protocol": proxy_counts,
        },
        "file_sizes": file_sizes,
        # Enhanced stats sections
        "health": health,
        "performance": performance,
        "validation": validation,
        "geographic": geographic,
        "sources_ranking": sources_ranking,
        # Pre-computed aggregations for charts
        "aggregations": {
            "response_time_distribution": response_time_distribution,
            "by_port": by_port,
            "by_continent": continent_agg,
            "source_flow": source_flow,
        },
    }


async def generate_proxy_lists(
    storage: SQLiteStorage,
    output_dir: Path,
    max_age_hours: int = 72,
) -> dict[str, int]:
    """Generate proxy list text files and metadata.json from database.

    Creates:
        - http.txt, https.txt, socks4.txt, socks5.txt (one proxy per line)
        - all.txt (combined with headers)
        - proxies.json (structured JSON with metadata)
        - metadata.json (counts and timestamp)

    Args:
        storage: SQLiteStorage instance to query
        output_dir: Directory to write output files
        max_age_hours: Only include proxies validated within this time window.
            Default: 72 hours (36 runs at 2h schedule). Set to 0 to include all proxies.

    Returns:
        Dictionary mapping protocol to proxy count
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if max_age_hours > 0:
        proxies_data = await storage.load_validated(max_age_hours)
    else:
        proxies_data = await storage.load()

    # Group proxies by protocol
    proxies_by_protocol: dict[str, set[str]] = {
        "http": set(),
        "https": set(),
        "socks4": set(),
        "socks5": set(),
    }

    for proxy in proxies_data:
        ip, port = parse_proxy_url(proxy["url"])
        if not ip:
            continue

        addr = f"{ip}:{port}"
        protocol = (proxy.get("protocol") or "http").lower()

        if protocol in ("http", "https"):
            proxies_by_protocol["http"].add(addr)
            proxies_by_protocol["https"].add(addr)
        elif protocol == "socks4":
            proxies_by_protocol["socks4"].add(addr)
        elif protocol == "socks5":
            proxies_by_protocol["socks5"].add(addr)

    timestamp = datetime.now(timezone.utc).isoformat()
    total_sources = len(ALL_HTTP_SOURCES) + len(ALL_SOCKS4_SOURCES) + len(ALL_SOCKS5_SOURCES)

    metadata = {
        "generated_at": timestamp,
        "total_sources": total_sources,
        "counts": {protocol: len(proxy_set) for protocol, proxy_set in proxies_by_protocol.items()},
    }

    # Save each protocol in TXT format
    for protocol, proxy_set in proxies_by_protocol.items():
        txt_file = output_dir / f"{protocol}.txt"
        with open(txt_file, "w") as f:
            for proxy_addr in sorted(proxy_set):
                f.write(f"{proxy_addr}\n")
        logger.info(f"Saved {len(proxy_set)} {protocol} proxies to {txt_file}")

    # Save all proxies in one file (skip https since it duplicates http)
    all_txt = output_dir / "all.txt"
    with open(all_txt, "w") as f:
        for protocol in ["http", "socks4", "socks5"]:
            proxy_set = proxies_by_protocol[protocol]
            f.write(f"# {protocol.upper()} Proxies ({len(proxy_set)})\n")
            for proxy_addr in sorted(proxy_set):
                f.write(f"{proxy_addr}\n")
            f.write("\n")
    logger.info(f"Saved all proxies to {all_txt}")

    # Save in JSON format
    json_file = output_dir / "proxies.json"
    json_data = {
        "metadata": metadata,
        "proxies": {
            protocol: sorted(proxy_set) for protocol, proxy_set in proxies_by_protocol.items()
        },
    }
    with open(json_file, "w") as f:
        json.dump(json_data, f, indent=2)
    logger.info(f"Saved JSON to {json_file}")

    # Save metadata
    meta_file = output_dir / "metadata.json"
    with open(meta_file, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata to {meta_file}")

    return {protocol: len(proxy_set) for protocol, proxy_set in proxies_by_protocol.items()}


async def export_for_web(
    db_path: Path,
    output_dir: Path,
    include_stats: bool = True,
    include_rich_proxies: bool = True,
    include_proxy_lists: bool = True,
    max_age_hours: int = 72,
) -> dict[str, Path]:
    """Export data for the web dashboard.

    Args:
        db_path: Path to SQLite database
        output_dir: Directory to write output files
        include_stats: Whether to generate stats.json
        include_rich_proxies: Whether to generate proxies-rich.json
        include_proxy_lists: Whether to generate text files and metadata.json
        max_age_hours: Only include proxies validated within this time window.
            Default: 72 hours (36 runs at 2h schedule). Set to 0 to include all proxies.

    Returns:
        Dictionary mapping output type to file path
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Path] = {}

    # Check if we need database access
    needs_db = (include_proxy_lists or include_rich_proxies) and db_path.exists()

    if needs_db:
        storage = SQLiteStorage(db_path)
        await storage.initialize()

        try:
            # Generate proxy list files first (metadata.json, txt files, proxies.json)
            # This must happen before stats since stats reads from these files
            if include_proxy_lists:
                logger.info("Generating proxy list files from database...")
                counts = await generate_proxy_lists(storage, output_dir, max_age_hours)
                outputs["metadata"] = output_dir / "metadata.json"
                outputs["proxies_json"] = output_dir / "proxies.json"
                logger.info(f"Proxy lists generated: {counts}")

            # Generate rich proxy data (proxies-rich.json)
            if include_rich_proxies:
                logger.info("Generating rich proxy data from database...")
                rich_data = await generate_rich_proxies(storage, max_age_hours=max_age_hours)
                rich_path = output_dir / "proxies-rich.json"
                with open(rich_path, "w") as f:
                    json.dump(rich_data, f)
                outputs["proxies_rich"] = rich_path
                logger.info(f"Rich proxy data saved to {rich_path}")
                logger.info(f"Total rich proxies: {rich_data['total']}")
        finally:
            await storage.close()
    elif include_proxy_lists or include_rich_proxies:
        logger.warning(f"Database not found at {db_path}, skipping database exports")

    # Generate stats from text files (reads metadata.json and txt files)
    if include_stats:
        logger.info("Generating stats.json...")
        stats = generate_stats_from_files(output_dir)
        stats_path = output_dir / "stats.json"
        with open(stats_path, "w") as f:
            json.dump(stats, f, indent=2)
        outputs["stats"] = stats_path
        logger.info(f"Stats saved to {stats_path}")
        logger.info(f"Total proxies: {stats['proxies']['total']}")

    return outputs
