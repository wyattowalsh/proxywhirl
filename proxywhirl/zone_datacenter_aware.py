"""Datacenter-aware proxy routing.

Routes requests to proxies in specific datacenters
based on geographic location and performance metrics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class DatacenterInfo:
    """Information about a datacenter."""

    datacenter_id: str
    name: str
    region: str
    country_code: str
    latitude: float
    longitude: float
    available_proxies: int = 0


class DatacenterAwareRouter:
    """Routes requests based on datacenter awareness."""

    def __init__(self) -> None:
        """Initialize datacenter-aware router."""
        self._datacenters: dict[str, DatacenterInfo] = {}
        self._proxy_to_datacenter: dict[str, str] = {}
        logger.debug("DatacenterAwareRouter initialized")

    def register_datacenter(self, info: DatacenterInfo) -> bool:
        """Register a datacenter.

        Args:
            info: Datacenter information

        Returns:
            True if registered
        """
        if info.datacenter_id in self._datacenters:
            logger.warning(f"Datacenter already registered: {info.datacenter_id}")
            return False

        self._datacenters[info.datacenter_id] = info
        logger.info(f"Datacenter registered: {info.datacenter_id} ({info.name})")
        return True

    def assign_proxy_to_datacenter(self, proxy_id: str, datacenter_id: str) -> bool:
        """Assign proxy to datacenter.

        Args:
            proxy_id: Proxy ID
            datacenter_id: Datacenter ID

        Returns:
            True if assigned
        """
        if datacenter_id not in self._datacenters:
            logger.error(f"Datacenter not found: {datacenter_id}")
            return False

        if proxy_id in self._proxy_to_datacenter:
            old_dc = self._proxy_to_datacenter[proxy_id]
            self._datacenters[old_dc].available_proxies -= 1

        self._proxy_to_datacenter[proxy_id] = datacenter_id
        self._datacenters[datacenter_id].available_proxies += 1
        logger.debug(f"Proxy assigned: {proxy_id} -> {datacenter_id}")
        return True

    def get_proxies_by_datacenter(self, datacenter_id: str) -> list[str]:
        """Get proxies in a datacenter.

        Args:
            datacenter_id: Datacenter ID

        Returns:
            List of proxy IDs
        """
        return [pid for pid, dc_id in self._proxy_to_datacenter.items() if dc_id == datacenter_id]

    def get_proxies_by_region(self, region: str) -> list[str]:
        """Get proxies in a region.

        Args:
            region: Region name

        Returns:
            List of proxy IDs
        """
        result = []
        for dc_id, dc_info in self._datacenters.items():
            if dc_info.region == region:
                result.extend(self.get_proxies_by_datacenter(dc_id))
        return result

    def get_closest_datacenter(self, latitude: float, longitude: float) -> str | None:
        """Get closest datacenter by distance.

        Args:
            latitude: User latitude
            longitude: User longitude

        Returns:
            Datacenter ID or None
        """
        from math import acos, cos, radians, sin

        min_distance = float("inf")
        closest_dc = None

        for dc_id, dc_info in self._datacenters.items():
            if dc_info.available_proxies == 0:
                continue

            lat1, lon1 = radians(latitude), radians(longitude)
            lat2, lon2 = radians(dc_info.latitude), radians(dc_info.longitude)

            central_angle = acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2))
            distance = 6371 * central_angle

            if distance < min_distance:
                min_distance = distance
                closest_dc = dc_id

        return closest_dc

    def export_metrics(self) -> dict[str, Any]:
        """Export datacenter routing metrics.

        Returns:
            Dictionary of metrics
        """
        total_proxies = len(self._proxy_to_datacenter)
        proxies_by_dc = {}

        for dc_id, dc_info in self._datacenters.items():
            proxies_by_dc[dc_id] = {
                "name": dc_info.name,
                "region": dc_info.region,
                "available_proxies": dc_info.available_proxies,
            }

        return {
            "total_datacenters": len(self._datacenters),
            "total_proxies": total_proxies,
            "datacenters": proxies_by_dc,
        }
