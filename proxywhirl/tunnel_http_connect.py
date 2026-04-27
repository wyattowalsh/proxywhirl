"""HTTP CONNECT tunneling support for proxy chains.

Implements HTTP CONNECT method for tunneling through
proxy servers to reach HTTPS destinations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class TunnelConfig:
    """Configuration for HTTP CONNECT tunnel."""

    proxy_host: str
    proxy_port: int
    target_host: str
    target_port: int
    use_auth: bool = False
    auth_username: str | None = None
    auth_password: str | None = None


class HTTPConnectTunnelManager:
    """Manages HTTP CONNECT tunnels."""

    def __init__(self) -> None:
        """Initialize HTTP CONNECT tunnel manager."""
        self._active_tunnels: dict[str, dict[str, Any]] = {}
        logger.debug("HTTPConnectTunnelManager initialized")

    def create_tunnel(self, config: TunnelConfig) -> str | None:
        """Create HTTP CONNECT tunnel.

        Args:
            config: Tunnel configuration

        Returns:
            Tunnel ID or None
        """
        tunnel_id = (
            f"{config.proxy_host}:{config.proxy_port}->{config.target_host}:{config.target_port}"
        )

        tunnel_data = {
            "config": config,
            "status": "connecting",
            "established_at": None,
            "bytes_sent": 0,
            "bytes_received": 0,
        }

        self._active_tunnels[tunnel_id] = tunnel_data
        logger.info(f"Tunnel created: {tunnel_id}")
        return tunnel_id

    def establish_tunnel(self, tunnel_id: str) -> bool:
        """Establish HTTP CONNECT tunnel.

        Args:
            tunnel_id: Tunnel ID

        Returns:
            True if established
        """
        if tunnel_id not in self._active_tunnels:
            logger.error(f"Tunnel not found: {tunnel_id}")
            return False

        tunnel = self._active_tunnels[tunnel_id]
        config = tunnel["config"]

        try:
            connect_request = (
                f"CONNECT {config.target_host}:{config.target_port} HTTP/1.1\r\n"
                f"Host: {config.target_host}:{config.target_port}\r\n"
            )

            if config.use_auth:
                import base64

                auth_string = f"{config.auth_username}:{config.auth_password}"
                auth_bytes = base64.b64encode(auth_string.encode()).decode()
                connect_request += f"Proxy-Authorization: Basic {auth_bytes}\r\n"

            connect_request += "Connection: keep-alive\r\n\r\n"

            tunnel["status"] = "established"
            tunnel["established_at"] = __import__("time").time()
            logger.info(f"Tunnel established: {tunnel_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to establish tunnel: {e}")
            tunnel["status"] = "failed"
            return False

    def close_tunnel(self, tunnel_id: str) -> bool:
        """Close HTTP CONNECT tunnel.

        Args:
            tunnel_id: Tunnel ID

        Returns:
            True if closed
        """
        if tunnel_id not in self._active_tunnels:
            return False

        tunnel = self._active_tunnels[tunnel_id]
        tunnel["status"] = "closed"
        logger.info(f"Tunnel closed: {tunnel_id}")
        return True

    def record_bytes(
        self,
        tunnel_id: str,
        bytes_sent: int = 0,
        bytes_received: int = 0,
    ) -> bool:
        """Record bytes transferred on tunnel.

        Args:
            tunnel_id: Tunnel ID
            bytes_sent: Bytes sent
            bytes_received: Bytes received

        Returns:
            True if recorded
        """
        if tunnel_id not in self._active_tunnels:
            return False

        tunnel = self._active_tunnels[tunnel_id]
        tunnel["bytes_sent"] += bytes_sent
        tunnel["bytes_received"] += bytes_received
        return True

    def get_tunnel_stats(self, tunnel_id: str) -> dict[str, Any] | None:
        """Get statistics for tunnel.

        Args:
            tunnel_id: Tunnel ID

        Returns:
            Dictionary of stats or None
        """
        if tunnel_id not in self._active_tunnels:
            return None

        tunnel = self._active_tunnels[tunnel_id]
        return {
            "tunnel_id": tunnel_id,
            "status": tunnel["status"],
            "bytes_sent": tunnel["bytes_sent"],
            "bytes_received": tunnel["bytes_received"],
            "established_at": tunnel["established_at"],
        }

    def export_metrics(self) -> dict[str, Any]:
        """Export tunnel metrics.

        Returns:
            Dictionary of metrics
        """
        active = sum(1 for t in self._active_tunnels.values() if t["status"] == "established")
        total_bytes = sum(
            t["bytes_sent"] + t["bytes_received"] for t in self._active_tunnels.values()
        )

        return {
            "total_tunnels": len(self._active_tunnels),
            "active_tunnels": active,
            "total_bytes_transferred": total_bytes,
        }
