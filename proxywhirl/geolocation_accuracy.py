"""Enhanced geolocation accuracy support."""

from dataclasses import dataclass

import httpx
from loguru import logger


@dataclass
class GeolocationData:
    """Detailed geolocation information."""

    ip: str
    country: str
    country_code: str
    region: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    isp: str | None = None
    asn: str | None = None
    accuracy: float = 0.0


class GeolocationEnricher:
    """Enriches proxy data with accurate geolocation."""

    def __init__(self):
        self.cache: dict[str, GeolocationData] = {}
        self.providers = [
            "https://ipapi.co/{ip}/json/",
            "https://ip-api.com/json/{ip}",
        ]

    async def enrich_proxy(self, ip: str) -> GeolocationData | None:
        """Enrich proxy with geolocation data."""
        if ip in self.cache:
            return self.cache[ip]

        for provider_url in self.providers:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(provider_url.format(ip=ip), timeout=10)
                    data = response.json()

                    geo_data = GeolocationData(
                        ip=ip,
                        country=data.get("country_name", data.get("country")),
                        country_code=data.get("country_code"),
                        region=data.get("region"),
                        city=data.get("city"),
                        latitude=data.get("latitude"),
                        longitude=data.get("longitude"),
                        isp=data.get("org"),
                        asn=data.get("asn"),
                        accuracy=0.95,
                    )
                    self.cache[ip] = geo_data
                    return geo_data
            except Exception as e:
                logger.debug(f"Geolocation provider error: {e}")
                continue

        logger.warning(f"Could not enrich geolocation for {ip}")
        return None

    def batch_enrich(self, ips: list[str]) -> dict[str, GeolocationData | None]:
        """Batch enrich multiple IPs."""
        return {ip: self.cache.get(ip) for ip in ips}
