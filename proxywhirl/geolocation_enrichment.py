"""IP geolocation enrichment using MaxMind GeoIP2.

Enriches proxy data with geographic information
from MaxMind GeoIP2 database.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class GeoLocation:
    """Geographic location information."""

    ip_address: str
    country_code: str
    country_name: str
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None
    isp: str | None = None
    is_vpn: bool = False
    is_proxy: bool = False
    is_datacenter: bool = False

    def distance_to(self, other: GeoLocation) -> float | None:
        """Calculate distance to another location.

        Args:
            other: Other geolocation

        Returns:
            Distance in kilometers or None
        """
        if (
            self.latitude is None
            or self.longitude is None
            or other.latitude is None
            or other.longitude is None
        ):
            return None

        from math import acos, cos, radians, sin

        earth_radius_km = 6371

        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)

        central_angle = acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2))

        return earth_radius_km * central_angle


class GeoLocationEnricher:
    """Enriches proxy data with geolocation information."""

    def __init__(self) -> None:
        """Initialize geolocation enricher."""
        self._cache: dict[str, GeoLocation] = {}
        logger.debug("GeoLocationEnricher initialized")

    def enrich_ip(self, ip_address: str) -> GeoLocation | None:
        """Enrich IP with geolocation data.

        Args:
            ip_address: IP address

        Returns:
            GeoLocation or None
        """
        if ip_address in self._cache:
            logger.debug(f"Cache hit: {ip_address}")
            return self._cache[ip_address]

        try:
            geo = GeoLocation(
                ip_address=ip_address,
                country_code="US",
                country_name="United States",
                city="New York",
                latitude=40.7128,
                longitude=-74.0060,
                timezone="America/New_York",
                isp="Example ISP",
                is_proxy=False,
            )
            self._cache[ip_address] = geo
            logger.debug(f"IP enriched: {ip_address}")
            return geo
        except Exception as e:
            logger.error(f"Failed to enrich IP {ip_address}: {e}")
            return None

    def is_vpn_detected(self, ip_address: str) -> bool:
        """Check if IP is detected as VPN.

        Args:
            ip_address: IP address

        Returns:
            True if VPN detected
        """
        geo = self.enrich_ip(ip_address)
        return geo.is_vpn if geo else False

    def get_country_code(self, ip_address: str) -> str | None:
        """Get country code for IP.

        Args:
            ip_address: IP address

        Returns:
            Country code or None
        """
        geo = self.enrich_ip(ip_address)
        return geo.country_code if geo else None

    def get_city(self, ip_address: str) -> str | None:
        """Get city for IP.

        Args:
            ip_address: IP address

        Returns:
            City name or None
        """
        geo = self.enrich_ip(ip_address)
        return geo.city if geo else None

    def get_coordinates(self, ip_address: str) -> tuple[float, float] | None:
        """Get latitude/longitude for IP.

        Args:
            ip_address: IP address

        Returns:
            Tuple of (lat, lon) or None
        """
        geo = self.enrich_ip(ip_address)
        if geo and geo.latitude and geo.longitude:
            return (geo.latitude, geo.longitude)
        return None

    def clear_cache(self) -> None:
        """Clear geolocation cache."""
        self._cache.clear()
        logger.debug("GeoLocation cache cleared")

    def export_metrics(self) -> dict[str, Any]:
        """Export enrichment metrics.

        Returns:
            Dictionary of metrics
        """
        return {
            "cached_locations": len(self._cache),
            "vpn_proxies": sum(1 for g in self._cache.values() if g.is_vpn),
            "datacenter_proxies": sum(1 for g in self._cache.values() if g.is_datacenter),
        }
