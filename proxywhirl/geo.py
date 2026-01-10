"""IP Geolocation utilities for proxy country lookup.

Uses ip-api.com batch API for efficient lookups (100 IPs per request).
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
from loguru import logger


async def batch_geolocate(
    ips: list[str],
    batch_size: int = 100,
    max_batches: int = 50,  # Limit to 5000 IPs by default
) -> dict[str, dict[str, str]]:
    """Batch geolocate IPs using ip-api.com.

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

    logger.info(f"Geolocating {len(unique_ips)} unique IPs...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(0, len(unique_ips), batch_size):
            batch = unique_ips[i : i + batch_size]

            try:
                # ip-api.com batch endpoint
                response = await client.post(
                    "https://ip-api.com/batch?fields=query,country,countryCode,status",
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
                    await asyncio.sleep(4.5)  # ~13 requests/minute to be safe

            except Exception as e:
                logger.warning(f"Geo batch {i // batch_size + 1} failed: {e}")
                continue

            if (i // batch_size + 1) % 10 == 0:
                logger.info(
                    f"Geo progress: {min(i + batch_size, len(unique_ips))}/{len(unique_ips)} IPs"
                )

    logger.info(f"Geolocated {len(results)}/{len(unique_ips)} IPs")
    return results


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
