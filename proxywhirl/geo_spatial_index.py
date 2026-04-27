"""Geographic spatial indexing for efficient geolocation lookups."""

import math
from dataclasses import dataclass


@dataclass
class GeoPoint:
    """Geographic point."""

    latitude: float
    longitude: float
    proxy_url: str


class GeoSpatialIndex:
    """Geographic spatial index for proxy lookups."""

    def __init__(self, grid_size: int = 100):
        self.grid_size = grid_size
        self.grid = {}
        self.points: list[GeoPoint] = []

    def add_point(self, point: GeoPoint) -> None:
        """Add a geographic point."""
        self.points.append(point)

        # Add to grid
        grid_key = self._get_grid_key(point.latitude, point.longitude)
        if grid_key not in self.grid:
            self.grid[grid_key] = []
        self.grid[grid_key].append(point)

    def _get_grid_key(self, latitude: float, longitude: float) -> tuple[int, int]:
        """Get grid key for coordinates."""
        lat_key = int((latitude + 90) / (180 / self.grid_size))
        lon_key = int((longitude + 180) / (360 / self.grid_size))
        return (lat_key, lon_key)

    def find_nearby(
        self, latitude: float, longitude: float, radius_km: float = 100
    ) -> list[GeoPoint]:
        """Find proxies near coordinates."""
        results = []

        for point in self.points:
            distance = self._haversine_distance(
                latitude, longitude, point.latitude, point.longitude
            )

            if distance <= radius_km:
                results.append(point)

        return sorted(
            results,
            key=lambda p: self._haversine_distance(latitude, longitude, p.latitude, p.longitude),
        )

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate haversine distance between two points in km."""
        r = 6371  # Earth radius in km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return r * c
