"""IP Geolocation utilities for proxy country lookup.

Uses MaxMind GeoLite2-Country database for fast, offline lookups.
External API lookup is available only when explicitly enabled.
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


# Cache for single IP lookups
_geo_cache: dict[str, dict[str, str]] = {}


def _lookup_single_ip_cached(ip: str, db_path: Path) -> dict[str, str] | None:
    """Lookup a single IP with caching.

    Args:
        ip: IP address to lookup
        db_path: Path to GeoLite2-Country.mmdb file

    Returns:
        dict with country and countryCode, or None if not found
    """
    if ip in _geo_cache:
        return _geo_cache[ip]

    try:
        import geoip2.database
        import geoip2.errors
    except ImportError:
        return None

    try:
        with geoip2.database.Reader(str(db_path)) as reader:
            try:
                response = reader.country(ip)
                result = {
                    "country": response.country.name or "",
                    "countryCode": response.country.iso_code or "",
                }
                _geo_cache[ip] = result
                return result
            except geoip2.errors.AddressNotFoundError:
                # IP not in database, cache the miss
                _geo_cache[ip] = {}
                return None
            except Exception as e:
                logger.debug(f"Failed to lookup {ip}: {e}")
                return None
    except Exception as e:
        logger.error(f"Failed to open GeoLite2 database: {e}")
        return None


def geolocate_with_database(ips: list[str], db_path: Path) -> dict[str, dict[str, str]]:
    """Geolocate IPs using local GeoLite2 database with caching.

    Args:
        ips: List of IP addresses to lookup
        db_path: Path to GeoLite2-Country.mmdb file

    Returns:
        dict[str, dict[str, str]]: Mapping of IP to geo info with country and countryCode keys.
    """
    results: dict[str, dict[str, str]] = {}
    unique_ips = list(set(ips))

    logger.info(f"Geolocating {len(unique_ips)} IPs using GeoLite2 database...")

    for ip in unique_ips:
        result = _lookup_single_ip_cached(ip, db_path)
        if result:
            results[ip] = result

    logger.info(f"Geolocated {len(results)}/{len(unique_ips)} IPs from database")
    return results


async def geolocate_with_api(
    ips: list[str],
    batch_size: int = 100,
    max_batches: int = 50,
) -> dict[str, dict[str, str]]:
    """Batch geolocate IPs using ip-api.com with caching.

    Args:
        ips: List of IP addresses to lookup
        batch_size: Number of IPs per batch (max 100 for ip-api.com)
        max_batches: Maximum number of batches to process

    Returns:
        dict[str, dict[str, str]]: Mapping of IP to geo info with country and countryCode keys.
    """
    results: dict[str, dict[str, str]] = {}
    unique_ips = list(set(ips))[: batch_size * max_batches]

    # First check cache
    uncached_ips = []
    for ip in unique_ips:
        if ip in _geo_cache and _geo_cache[ip]:
            results[ip] = _geo_cache[ip]
        else:
            uncached_ips.append(ip)

    if not uncached_ips:
        return results

    logger.info(f"Geolocating {len(uncached_ips)} IPs via ip-api.com (cached {len(results)})...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(0, len(uncached_ips), batch_size):
            batch = uncached_ips[i : i + batch_size]

            try:
                response = await client.post(
                    "https://ip-api.com/batch?fields=query,country,countryCode,status",
                    json=batch,
                )
                response.raise_for_status()

                for item in response.json():
                    if item.get("status") == "success":
                        geo_info = {
                            "country": item.get("country", ""),
                            "countryCode": item.get("countryCode", ""),
                        }
                        results[item["query"]] = geo_info
                        _geo_cache[item["query"]] = geo_info
                    else:
                        # Cache misses
                        _geo_cache[item["query"]] = {}

                # Rate limit: 15 requests per minute for free tier
                if i + batch_size < len(uncached_ips):
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
    allow_external_api: bool = False,
) -> dict[str, dict[str, str]]:
    """Geolocate IPs using best available method.

    Tries in order:
    1. Local GeoLite2 database (fast, no rate limits)
    2. External HTTPS API, only when explicitly enabled

    Args:
        ips: List of IP addresses to lookup
        batch_size: Number of IPs per API batch
        max_batches: Maximum API batches to process
        db_path: Optional explicit path to GeoLite2 database
        allow_external_api: Whether to send IPs to the external lookup API

    Returns:
        dict[str, dict[str, str]]: Mapping of IP to geo info with country and countryCode keys.
    """
    if not ips:
        return {}

    # Try local database first
    db = db_path or _find_geolite2_db()
    if db:
        logger.info(f"Using GeoLite2 database: {db}")
        return geolocate_with_database(ips, db)

    if not allow_external_api:
        logger.info("GeoLite2 database not found; external geo lookup disabled")
        return {}

    logger.info("GeoLite2 database not found, using external geo API")
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
