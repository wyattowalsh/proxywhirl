"""DNS over HTTPS (DoH) support for secure DNS resolution.

Provides:
- DoH client implementation
- Cloudflare and Google DoH resolvers
- Caching and fallback mechanisms
"""

from __future__ import annotations

import ipaddress
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from loguru import logger


@dataclass
class DNSRecord:
    """DNS A/AAAA record."""

    hostname: str
    ip_address: str
    record_type: str  # "A" or "AAAA"
    ttl: int = 3600
    timestamp: float = field(default_factory=time.time)

    @property
    def age_seconds(self) -> float:
        """Age in seconds."""
        return time.time() - self.timestamp

    @property
    def is_expired(self) -> bool:
        """Check if TTL expired."""
        return self.age_seconds > self.ttl


class DoHResolver:
    """DNS over HTTPS resolver."""

    # Public DoH endpoints
    CLOUDFLARE_DOH = "https://cloudflare-dns.com/dns-query"
    GOOGLE_DOH = "https://dns.google/dns-query"
    QUAD9_DOH = "https://dns.quad9.net/dns-query"

    def __init__(
        self,
        endpoint: str = CLOUDFLARE_DOH,
        cache_ttl: int = 3600,
        timeout: float = 10.0,
    ):
        """Initialize DoH resolver.

        Args:
            endpoint: DoH endpoint URL
            cache_ttl: Cache TTL in seconds
            timeout: Request timeout
        """
        self.endpoint = endpoint
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.cache: dict[str, list[DNSRecord]] = {}
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> DoHResolver:
        """Async context manager entry."""
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    async def resolve(self, hostname: str) -> list[str]:
        """Resolve hostname to IP addresses via DoH.

        Args:
            hostname: Hostname to resolve

        Returns:
            List of IP addresses

        Raises:
            RuntimeError: If resolution fails
        """
        # Check cache
        if hostname in self.cache:
            records = [r for r in self.cache[hostname] if not r.is_expired]
            if records:
                logger.debug(f"Resolved {hostname} from cache: {[r.ip_address for r in records]}")
                return [r.ip_address for r in records]

        if not self.client:
            self.client = httpx.AsyncClient(timeout=self.timeout)

        try:
            # Query both A and AAAA records
            results = []

            for record_type in ["A", "AAAA"]:
                try:
                    response = await self.client.get(
                        self.endpoint,
                        params={
                            "name": hostname,
                            "type": record_type,
                            "cd": "false",
                        },
                        headers={
                            "Accept": "application/dns-json",
                        },
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if "Answer" in data:
                            for answer in data["Answer"]:
                                ip = answer.get("data")
                                if ip and self._is_valid_ip(ip):
                                    record = DNSRecord(
                                        hostname=hostname,
                                        ip_address=ip,
                                        record_type=record_type,
                                        ttl=answer.get("TTL", self.cache_ttl),
                                    )
                                    results.append(record)

                except Exception as e:
                    logger.warning(f"DoH query failed for {record_type} {hostname}: {e}")

            if results:
                self.cache[hostname] = results
                ips = [r.ip_address for r in results]
                logger.info(f"Resolved {hostname} via DoH: {ips}")
                return ips

            raise RuntimeError(f"Could not resolve {hostname} via DoH")

        except Exception as e:
            logger.error(f"DoH resolution failed for {hostname}: {e}")
            raise

    @staticmethod
    def _is_valid_ip(ip_str: str) -> bool:
        """Check if string is valid IP address."""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False

    def clear_cache(self) -> None:
        """Clear DNS cache."""
        self.cache.clear()
        logger.debug("Cleared DoH resolver cache")

    async def get_stats(self) -> dict[str, Any]:
        """Get resolver statistics."""
        total_records = sum(len(records) for records in self.cache.values())
        valid_records = sum(
            1 for records in self.cache.values() for r in records if not r.is_expired
        )

        return {
            "endpoint": self.endpoint,
            "cached_hosts": len(self.cache),
            "total_records": total_records,
            "valid_records": valid_records,
            "expired_records": total_records - valid_records,
        }
