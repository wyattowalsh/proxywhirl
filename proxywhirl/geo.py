"""IP geolocation utilities for proxy country lookup.

Canonical offline geo pipeline
------------------------------
1. ``proxywhirl.geo`` — batch/single country lookup via local GeoLite2-Country
   (``batch_geolocate``, ``enrich_proxies_with_geo``) for exports and dashboards.
2. ``proxywhirl.enrichment.OfflineEnricher`` / ``AsyncOfflineEnricher`` — richer
   offline metadata (GeoLite2-City when present, IP traits, port signatures).

External HTTPS geolocation (ip-api.com) is used only when
``allow_external_api=True`` is passed explicitly to ``batch_geolocate``.
"""

from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
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

# ISO 3166-1 alpha-2 → continent code (aligned with web dashboard mapping)
COUNTRY_TO_CONTINENT: dict[str, str] = {
    "US": "NA",
    "CA": "NA",
    "MX": "NA",
    "BR": "SA",
    "AR": "SA",
    "CL": "SA",
    "CO": "SA",
    "GB": "EU",
    "DE": "EU",
    "FR": "EU",
    "IT": "EU",
    "ES": "EU",
    "NL": "EU",
    "PL": "EU",
    "RU": "EU",
    "UA": "EU",
    "CN": "AS",
    "IN": "AS",
    "JP": "AS",
    "KR": "AS",
    "ID": "AS",
    "TH": "AS",
    "VN": "AS",
    "MY": "AS",
    "SG": "AS",
    "PH": "AS",
    "TR": "AS",
    "SA": "AS",
    "AE": "AS",
    "IL": "AS",
    "PK": "AS",
    "BD": "AS",
    "IR": "AS",
    "HK": "AS",
    "TW": "AS",
    "AU": "OC",
    "NZ": "OC",
    "ZA": "AF",
    "EG": "AF",
    "NG": "AF",
    "KE": "AF",
    "MA": "AF",
}

_DEFAULT_CONTINENT = "AS"
_GEO_CACHE_MAX_SIZE = 10_000
_GEO_CACHE_TTL_SECONDS = 3600.0


class _GeoLookupCache:
    """Bounded TTL cache for geo lookup results."""

    def __init__(
        self,
        max_size: int = _GEO_CACHE_MAX_SIZE,
        ttl_seconds: float = _GEO_CACHE_TTL_SECONDS,
    ) -> None:
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._entries: OrderedDict[str, tuple[dict[str, str], float]] = OrderedDict()

    def get(self, ip: str) -> dict[str, str] | None:
        entry = self._entries.get(ip)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._entries[ip]
            return None
        self._entries.move_to_end(ip)
        return value

    def set(self, ip: str, value: dict[str, str]) -> None:
        if ip in self._entries:
            del self._entries[ip]
        elif len(self._entries) >= self._max_size:
            self._entries.popitem(last=False)
        self._entries[ip] = (value, time.monotonic() + self._ttl_seconds)

    def clear(self) -> None:
        self._entries.clear()


_geo_cache = _GeoLookupCache()


def reset_geo_cache() -> None:
    """Clear the module-level geo cache (primarily for tests)."""
    _geo_cache.clear()


def continent_for_country(country_code: str | None) -> str | None:
    """Map an ISO country code to a continent code."""
    if not country_code:
        return None
    code = country_code.upper()
    return COUNTRY_TO_CONTINENT.get(code, _DEFAULT_CONTINENT)


def _find_geolite2_db() -> Path | None:
    """Find GeoLite2 database file."""
    for path in GEOLITE2_PATHS:
        if path.exists():
            return path
    return None


def _lookup_ip_with_reader(ip: str, reader: Any) -> dict[str, str] | None:
    """Lookup a single IP using an open GeoIP reader."""
    import geoip2.errors

    try:
        response = reader.country(ip)
        country_code = response.country.iso_code or ""
        return {
            "country": response.country.name or "",
            "countryCode": country_code,
            "continentCode": continent_for_country(country_code) or "",
        }
    except geoip2.errors.AddressNotFoundError:
        _geo_cache.set(ip, {})
        return None
    except Exception as e:
        logger.debug(f"Failed to lookup {ip}: {e}")
        return None


def _lookup_single_ip_cached(ip: str, db_path: Path) -> dict[str, str] | None:
    """Lookup a single IP with caching (one reader per call)."""
    cached = _geo_cache.get(ip)
    if cached is not None:
        return cached or None

    try:
        import geoip2.database
    except ImportError:
        return None

    try:
        with geoip2.database.Reader(str(db_path)) as reader:
            result = _lookup_ip_with_reader(ip, reader)
            if result:
                _geo_cache.set(ip, result)
                return result
            return None
    except Exception as e:
        logger.error(f"Failed to open GeoLite2 database: {e}")
        return None


def geolocate_with_database(ips: list[str], db_path: Path) -> dict[str, dict[str, str]]:
    """Geolocate IPs using local GeoLite2 database with caching.

    Uses a single MMDB reader for the whole batch.
    """
    results: dict[str, dict[str, str]] = {}
    unique_ips = list(dict.fromkeys(ips))

    logger.info(f"Geolocating {len(unique_ips)} IPs using GeoLite2 database...")

    try:
        import geoip2.database
    except ImportError:
        logger.warning("geoip2 package not installed; skipping database geolocation")
        return results

    uncached_ips: list[str] = []
    for ip in unique_ips:
        cached = _geo_cache.get(ip)
        if cached is not None:
            if cached:
                results[ip] = cached
        else:
            uncached_ips.append(ip)

    if not uncached_ips:
        logger.info(f"Geolocated {len(results)}/{len(unique_ips)} IPs from database (cache)")
        return results

    try:
        with geoip2.database.Reader(str(db_path)) as reader:
            for ip in uncached_ips:
                result = _lookup_ip_with_reader(ip, reader)
                if result:
                    _geo_cache.set(ip, result)
                    results[ip] = result
    except Exception as e:
        logger.error(f"Failed to open GeoLite2 database: {e}")
        return results

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
    unique_ips = list(dict.fromkeys(ips))[: batch_size * max_batches]

    uncached_ips: list[str] = []
    for ip in unique_ips:
        cached = _geo_cache.get(ip)
        if cached is not None:
            if cached:
                results[ip] = cached
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
                    query = item["query"]
                    if item.get("status") == "success":
                        country_code = item.get("countryCode", "")
                        geo_info = {
                            "country": item.get("country", ""),
                            "countryCode": country_code,
                            "continentCode": continent_for_country(country_code) or "",
                        }
                        results[query] = geo_info
                        _geo_cache.set(query, geo_info)
                    else:
                        _geo_cache.set(query, {})

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
    db = (db_path if db_path is not None and db_path.exists() else None) or _find_geolite2_db()
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
    """Add country and continent info to proxy dictionaries."""
    for proxy in proxies:
        ip = proxy.get("ip", "")
        geo = geo_data.get(ip, {})
        country_code = geo.get("countryCode") or proxy.get("country_code")
        proxy["country"] = geo.get("country") or proxy.get("country")
        proxy["country_code"] = country_code
        continent = geo.get("continentCode") or continent_for_country(country_code)
        if continent:
            proxy["continent_code"] = continent
    return proxies
