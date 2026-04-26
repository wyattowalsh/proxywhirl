"""HTTP/SOCKS tunnel multiplexing for concurrent proxy connections.

Provides:
- Connection pooling and reuse
- Multiplexed tunnel management
- Load balancing across tunnels
- Connection health monitoring
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

import httpx
from loguru import logger


class TunnelState(str, Enum):
    """Tunnel connection state."""

    IDLE = "idle"
    ACTIVE = "active"
    STALE = "stale"
    CLOSED = "closed"


@dataclass
class TunnelMetrics:
    """Metrics for a tunnel connection."""

    requests_total: int = 0
    requests_success: int = 0
    requests_failed: int = 0
    bytes_transferred: int = 0
    last_used_at: float = field(default_factory=time.time)
    created_at: float = field(default_factory=time.time)

    @property
    def success_rate(self) -> float:
        """Success rate percentage."""
        if self.requests_total == 0:
            return 100.0
        return (self.requests_success / self.requests_total) * 100

    @property
    def age_seconds(self) -> float:
        """Age in seconds."""
        return time.time() - self.created_at

    @property
    def idle_time_seconds(self) -> float:
        """Idle time in seconds."""
        return time.time() - self.last_used_at


class ProxyTunnel:
    """Single proxy tunnel connection."""

    def __init__(
        self,
        proxy_url: str,
        max_requests: int = 1000,
        max_age_seconds: int = 3600,
    ):
        """Initialize proxy tunnel.

        Args:
            proxy_url: Proxy URL
            max_requests: Max requests before rotation
            max_age_seconds: Max tunnel age in seconds
        """
        self.tunnel_id = uuid4().hex[:12]
        self.proxy_url = proxy_url
        self.max_requests = max_requests
        self.max_age_seconds = max_age_seconds
        self.client: httpx.AsyncClient | None = None
        self.state = TunnelState.IDLE
        self.metrics = TunnelMetrics()
        self.lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize HTTP client."""
        if not self.client:
            self.client = httpx.AsyncClient(
                proxy=self.proxy_url,
                timeout=30.0,
                follow_redirects=True,
            )
            self.state = TunnelState.ACTIVE
            logger.debug(f"Initialized tunnel {self.tunnel_id} to {self.proxy_url}")

    async def close(self) -> None:
        """Close tunnel and cleanup."""
        if self.client:
            await self.client.aclose()
            self.client = None
        self.state = TunnelState.CLOSED
        logger.debug(f"Closed tunnel {self.tunnel_id}")

    async def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make request through tunnel.

        Args:
            method: HTTP method
            url: Target URL
            **kwargs: Additional httpx parameters

        Returns:
            Response object

        Raises:
            RuntimeError: If tunnel is closed or unusable
        """
        async with self.lock:
            if self.state == TunnelState.CLOSED:
                raise RuntimeError(f"Tunnel {self.tunnel_id} is closed")

            # Check if tunnel should be rotated
            if self._should_rotate():
                logger.info(f"Rotating tunnel {self.tunnel_id} (age/requests)")
                raise RuntimeError(f"Tunnel {self.tunnel_id} needs rotation")

            if not self.client:
                await self.initialize()

            self.state = TunnelState.ACTIVE
            self.metrics.last_used_at = time.time()

        try:
            response = await self.client.request(method, url, **kwargs)
            self.metrics.requests_total += 1
            self.metrics.requests_success += 1
            self.metrics.bytes_transferred += len(response.content)
            return response

        except Exception as e:
            self.metrics.requests_total += 1
            self.metrics.requests_failed += 1
            logger.warning(f"Tunnel {self.tunnel_id} request failed: {e}")
            self.state = TunnelState.STALE
            raise

    def _should_rotate(self) -> bool:
        """Check if tunnel should be rotated."""
        if self.metrics.requests_total >= self.max_requests:
            return True
        if self.metrics.age_seconds > self.max_age_seconds:
            return True
        if self.state == TunnelState.STALE:
            return True
        return False

    def get_stats(self) -> dict[str, Any]:
        """Get tunnel statistics."""
        return {
            "tunnel_id": self.tunnel_id,
            "proxy_url": self.proxy_url,
            "state": self.state.value,
            "requests_total": self.metrics.requests_total,
            "requests_success": self.metrics.requests_success,
            "requests_failed": self.metrics.requests_failed,
            "success_rate": self.metrics.success_rate,
            "bytes_transferred": self.metrics.bytes_transferred,
            "age_seconds": self.metrics.age_seconds,
            "idle_seconds": self.metrics.idle_time_seconds,
        }


class TunnelMultiplexer:
    """Manages multiple proxy tunnels with load balancing."""

    def __init__(
        self,
        proxy_urls: list[str],
        pool_size: int = 5,
        max_requests_per_tunnel: int = 1000,
    ):
        """Initialize tunnel multiplexer.

        Args:
            proxy_urls: List of proxy URLs
            pool_size: Number of tunnels per proxy
            max_requests_per_tunnel: Max requests before tunnel rotation
        """
        self.proxy_urls = proxy_urls
        self.pool_size = pool_size
        self.tunnels: dict[str, deque[ProxyTunnel]] = {url: deque() for url in proxy_urls}
        self.tunnel_index = 0
        self.lock = asyncio.Lock()
        self.closed = False

        # Initialize tunnel pools
        for url in proxy_urls:
            for _ in range(pool_size):
                tunnel = ProxyTunnel(
                    url,
                    max_requests=max_requests_per_tunnel,
                )
                self.tunnels[url].append(tunnel)

        logger.info(
            f"Initialized TunnelMultiplexer with {len(proxy_urls)} proxies, pool_size={pool_size}"
        )

    async def close(self) -> None:
        """Close all tunnels."""
        async with self.lock:
            for tunnel_pool in self.tunnels.values():
                for tunnel in tunnel_pool:
                    await tunnel.close()
            self.closed = True
            logger.info("Closed all tunnels")

    async def get_tunnel(self) -> ProxyTunnel:
        """Get next available tunnel with load balancing.

        Returns:
            Tunnel object

        Raises:
            RuntimeError: If no tunnels available
        """
        if self.closed:
            raise RuntimeError("Multiplexer is closed")

        async with self.lock:
            # Round-robin through proxies
            self.tunnel_index = (self.tunnel_index + 1) % len(self.proxy_urls)
            proxy_url = self.proxy_urls[self.tunnel_index]
            tunnel_pool = self.tunnels[proxy_url]

            if not tunnel_pool:
                raise RuntimeError(f"No tunnels available for {proxy_url}")

            tunnel = tunnel_pool.popleft()
            tunnel_pool.append(tunnel)

            if not tunnel.client:
                await tunnel.initialize()

            return tunnel

    async def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make multiplexed request through best available tunnel."""
        tunnel = await self.get_tunnel()
        return await tunnel.request(method, url, **kwargs)

    async def get_stats(self) -> dict[str, Any]:
        """Get multiplexer statistics."""
        stats = {
            "proxy_urls": len(self.proxy_urls),
            "pool_size": self.pool_size,
            "total_tunnels": sum(len(pool) for pool in self.tunnels.values()),
            "tunnels_by_proxy": {},
        }

        for proxy_url, tunnel_pool in self.tunnels.items():
            stats["tunnels_by_proxy"][proxy_url] = [tunnel.get_stats() for tunnel in tunnel_pool]

        return stats
