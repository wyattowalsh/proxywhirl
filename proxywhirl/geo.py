"""IP Geolocation utilities for proxy country lookup.

Uses MaxMind GeoLite2-Country database for fast, offline lookups.
Falls back to ip-api.com batch API if database not available.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import httpx
from loguru import logger

# GeoLite2 database paths to check (in order of preference)
GEOLITE2_PATHS = [
    Path("GeoLite2-Country.mmdb"),
    Path("data/GeoLite2-Country.mmdb"),
    Path(__file__).parent / "data" / "GeoLite2-Country.mmdb",
    Path(__file__).parent.parent / "GeoLite2-Country.mmdb",
    Path.home() / ".local" / "share" / "GeoIP" / "GeoLite2-Country.mmdb",
    Path("/usr/share/GeoIP/GeoLite2-Country.mmdb"),
]


def _find_geolite2_db() -> Path | None:
    """Find GeoLite2 database file."""
    for path in GEOLITE2_PATHS:
        if path.exists():
            return path
    return None


def geolocate_with_database(ips: list[str], db_path: Path) -> dict[str, dict[str, str]]:
    """Geolocate IPs using local GeoLite2 database.

    Args:
        ips: List of IP addresses to lookup
        db_path: Path to GeoLite2-Country.mmdb file

    Returns:
        Dictionary mapping IP to geo info {country, countryCode}
    """
    try:
        import geoip2.database
        import geoip2.errors
    except ImportError:
        logger.warning("geoip2 not installed, skipping database lookup")
        return {}

    results: dict[str, dict[str, str]] = {}
    unique_ips = list(set(ips))

    logger.info(f"Geolocating {len(unique_ips)} IPs using GeoLite2 database...")

    try:
        with geoip2.database.Reader(str(db_path)) as reader:
            for ip in unique_ips:
                try:
                    response = reader.country(ip)
                    results[ip] = {
                        "country": response.country.name or "",
                        "countryCode": response.country.iso_code or "",
                    }
                except geoip2.errors.AddressNotFoundError:
                    # IP not in database (private IP, etc.)
                    pass
                except Exception as e:
                    logger.debug(f"Failed to lookup {ip}: {e}")
    except Exception as e:
        logger.error(f"Failed to open GeoLite2 database: {e}")
        return {}

    logger.info(f"Geolocated {len(results)}/{len(unique_ips)} IPs from database")
    return results


async def geolocate_with_api(
    ips: list[str],
    batch_size: int = 100,
    max_batches: int = 50,
) -> dict[str, dict[str, str]]:
    """Batch geolocate IPs using ip-api.com (fallback).

    Args:
        ips: List of IP addresses to lookup
        batch_size: Number of IPs per batch (max 100 for ip-api.com)
        max_batches: Maximum number of batches to process

    Returns:
        Dictionary mapping IP to geo info {country, countryCode}
    """
    results: dict[str, dict[str, str]] = {}
    unique_ips = list(set(ips))[: batch_size * max_batches]

    if not unique_ips:
        return results

    logger.info(f"Geolocating {len(unique_ips)} IPs via ip-api.com...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(0, len(unique_ips), batch_size):
            batch = unique_ips[i : i + batch_size]

            try:
                response = await client.post(
                    "http://ip-api.com/batch?fields=query,country,countryCode,status",
                    json=batch,
                )
                response.raise_for_status()

                for item in response.json():
                    if item.get("status") == "success":
                        results[item["query"]] = {
                            "country": item.get("country", ""),
                            "countryCode": item.get("countryCode", ""),
                        }

                # Rate limit: 15 requests per minute for free tier
                if i + batch_size < len(unique_ips):
                    await asyncio.sleep(4.5)

            except Exception as e:
                logger.warning(f"Geo API batch {i // batch_size + 1} failed: {e}")
                continue

    logger.info(f"Geolocated {len(results)}/{len(unique_ips)} IPs via API")
    return results


async def batch_geolocate(
    ips: list[str],
    batch_size: int = 100,
    max_batches: int = 50,
    db_path: Path | None = None,
) -> dict[str, dict[str, str]]:
    """Geolocate IPs using best available method.

    Tries in order:
    1. Local GeoLite2 database (fast, no rate limits)
    2. ip-api.com batch API (fallback, rate limited)

    Args:
        ips: List of IP addresses to lookup
        batch_size: Number of IPs per API batch
        max_batches: Maximum API batches to process
        db_path: Optional explicit path to GeoLite2 database

    Returns:
        Dictionary mapping IP to geo info {country, countryCode}
    """
    if not ips:
        return {}

    # Try local database first
    db = db_path or _find_geolite2_db()
    if db:
        logger.info(f"Using GeoLite2 database: {db}")
        return geolocate_with_database(ips, db)

    # Fall back to API
    logger.info("GeoLite2 database not found, falling back to API")
    return await geolocate_with_api(ips, batch_size, max_batches)


def enrich_proxies_with_geo(
    proxies: list[dict[str, Any]],
    geo_data: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    """Add country info to proxy dictionaries.

    Args:
        proxies: List of proxy dictionaries with 'ip' field
        geo_data: Geo lookup results from batch_geolocate

    Returns:
        Proxies with country and country_code fields added
    """
    for proxy in proxies:
        ip = proxy.get("ip", "")
        geo = geo_data.get(ip, {})
        proxy["country"] = geo.get("country")
        proxy["country_code"] = geo.get("countryCode")
    return proxies
