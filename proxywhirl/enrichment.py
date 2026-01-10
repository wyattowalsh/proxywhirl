"""Offline proxy metadata enrichment using local databases.

This module provides 100% offline enrichment of proxy data using:
1. MaxMind GeoLite2 local database (optional, requires download)
2. Python stdlib ipaddress for IP property analysis
3. Port signature analysis

No external API calls - all lookups are local.
"""

from __future__ import annotations

import ipaddress
from pathlib import Path
from typing import Any

from loguru import logger

# Common proxy port signatures
PORT_SIGNATURES: dict[int, str] = {
    # Standard HTTP ports
    80: "http",
    8080: "http-alt",
    8000: "http-alt",
    8888: "http-alt",
    3128: "squid",
    # HTTPS ports
    443: "https",
    8443: "https-alt",
    # SOCKS ports
    1080: "socks",
    1081: "socks-alt",
    9050: "tor",
    9150: "tor-browser",
    # Specialized proxy ports
    3129: "squid-alt",
    8118: "privoxy",
    8123: "polipo",
    9999: "proxy-common",
    # Transparent proxy ports
    3130: "transparent",
    8081: "transparent-alt",
}


class OfflineEnricher:
    """Enrich proxies using local databases only - no API calls."""

    def __init__(self, geoip_path: Path | None = None) -> None:
        """Initialize the enricher.

        Args:
            geoip_path: Path to MaxMind GeoLite2-City.mmdb file.
                       If None, looks in default locations.
        """
        self.geoip_reader: Any = None
        self._init_geoip(geoip_path)

    def _init_geoip(self, geoip_path: Path | None) -> None:
        """Initialize GeoIP reader if database is available."""
        # Check provided path first
        paths_to_check: list[Path] = []

        if geoip_path:
            paths_to_check.append(geoip_path)

        # Default locations
        paths_to_check.extend(
            [
                Path.home() / ".config" / "proxywhirl" / "GeoLite2-City.mmdb",
                Path.home() / ".local" / "share" / "proxywhirl" / "GeoLite2-City.mmdb",
                Path("/usr/share/GeoIP/GeoLite2-City.mmdb"),
                Path("/var/lib/GeoIP/GeoLite2-City.mmdb"),
            ]
        )

        for path in paths_to_check:
            if path.exists():
                try:
                    from geoip2.database import Reader

                    self.geoip_reader = Reader(str(path))
                    logger.info(f"Loaded GeoIP database from {path}")
                    return
                except Exception as e:
                    logger.warning(f"Failed to load GeoIP from {path}: {e}")
                    continue

        logger.info(
            "GeoIP database not found. Run 'proxywhirl setup-geoip' to download. "
            "IP analysis and port signatures will still work."
        )

    def close(self) -> None:
        """Close the GeoIP reader if open."""
        if self.geoip_reader:
            self.geoip_reader.close()
            self.geoip_reader = None

    def enrich(self, ip: str, port: int) -> dict[str, Any]:
        """Enrich a proxy with metadata.

        Args:
            ip: IP address string
            port: Port number

        Returns:
            Dictionary of enrichment fields (all may be None if lookup fails)
        """
        result: dict[str, Any] = {
            # Geo fields (from GeoIP)
            "country": None,
            "country_code": None,
            "city": None,
            "region": None,
            "latitude": None,
            "longitude": None,
            "timezone": None,
            "continent": None,
            "continent_code": None,
            # IP property fields (from stdlib)
            "is_private": None,
            "is_global": None,
            "is_loopback": None,
            "is_reserved": None,
            "ip_version": None,
            # Port analysis
            "port_type": None,
        }

        # 1. GeoIP lookup (if database available)
        result.update(self._geoip_lookup(ip))

        # 2. IP property analysis (stdlib - always works)
        result.update(self._ip_analysis(ip))

        # 3. Port signature analysis
        result["port_type"] = self._port_analysis(port)

        return result

    def _geoip_lookup(self, ip: str) -> dict[str, Any]:
        """Perform GeoIP lookup if database is available."""
        result: dict[str, Any] = {}

        if not self.geoip_reader:
            return result

        try:
            response = self.geoip_reader.city(ip)

            result["country"] = response.country.name
            result["country_code"] = response.country.iso_code
            result["city"] = response.city.name
            result["continent"] = response.continent.name
            result["continent_code"] = response.continent.code

            if response.subdivisions:
                result["region"] = response.subdivisions.most_specific.name

            if response.location:
                result["latitude"] = response.location.latitude
                result["longitude"] = response.location.longitude
                result["timezone"] = response.location.time_zone

        except Exception:
            # IP not found in database or invalid - that's OK
            pass

        return result

    def _ip_analysis(self, ip: str) -> dict[str, Any]:
        """Analyze IP address properties using Python stdlib."""
        result: dict[str, Any] = {}

        try:
            ip_obj = ipaddress.ip_address(ip)

            result["is_private"] = ip_obj.is_private
            result["is_global"] = ip_obj.is_global
            result["is_loopback"] = ip_obj.is_loopback
            result["is_reserved"] = ip_obj.is_reserved
            result["ip_version"] = ip_obj.version

        except ValueError:
            # Invalid IP address - leave as None
            pass

        return result

    def _port_analysis(self, port: int) -> str:
        """Analyze port to determine likely proxy type."""
        return PORT_SIGNATURES.get(port, "other")

    def enrich_batch(
        self,
        proxies: list[dict[str, Any]],
        ip_field: str = "ip",
        port_field: str = "port",
    ) -> list[dict[str, Any]]:
        """Enrich a batch of proxies in place.

        Args:
            proxies: List of proxy dictionaries to enrich
            ip_field: Field name containing IP address
            port_field: Field name containing port

        Returns:
            The same list with enrichment fields added
        """
        for proxy in proxies:
            ip = proxy.get(ip_field, "")
            port = proxy.get(port_field, 0)

            if ip and port:
                enrichment = self.enrich(ip, port)
                proxy.update(enrichment)

        return proxies


def get_default_geoip_path() -> Path:
    """Get the default path for GeoIP database."""
    return Path.home() / ".config" / "proxywhirl" / "GeoLite2-City.mmdb"


def is_geoip_available() -> bool:
    """Check if GeoIP database is available."""
    enricher = OfflineEnricher()
    available = enricher.geoip_reader is not None
    enricher.close()
    return available
