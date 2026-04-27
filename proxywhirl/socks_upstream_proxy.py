"""Upstream SOCKS proxy support for ProxyWhirl.

Allows routing through upstream SOCKS proxies
for enhanced privacy and routing flexibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from loguru import logger


class SOCKSVersion(str, Enum):
    """SOCKS protocol versions."""

    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


@dataclass
class SOCKSConfig:
    """Configuration for SOCKS proxy."""

    host: str
    port: int
    version: SOCKSVersion
    username: str | None = None
    password: str | None = None
    timeout: int = 30
    resolve_host: bool = True

    def validate(self) -> bool:
        """Validate SOCKS configuration.

        Returns:
            True if valid
        """
        if not self.host:
            logger.error("SOCKS host is required")
            return False

        if not 1 <= self.port <= 65535:
            logger.error(f"Invalid SOCKS port: {self.port}")
            return False

        return True

    def to_url(self) -> str:
        """Convert to URL format.

        Returns:
            SOCKS URL string
        """
        auth = ""
        if self.username:
            password = self.password or ""
            auth = f"{self.username}:{password}@"

        return f"{self.version.value}://{auth}{self.host}:{self.port}"


class UpstreamSOCKSProxy:
    """Represents an upstream SOCKS proxy."""

    def __init__(self, config: SOCKSConfig) -> None:
        """Initialize upstream SOCKS proxy.

        Args:
            config: SOCKS configuration
        """
        if not config.validate():
            msg = "Invalid SOCKS configuration"
            raise ValueError(msg)

        self.config = config
        self.is_healthy = True
        self.connection_count = 0
        logger.debug(f"UpstreamSOCKSProxy created: {config.host}:{config.port}")

    def mark_healthy(self) -> None:
        """Mark proxy as healthy."""
        self.is_healthy = True

    def mark_unhealthy(self) -> None:
        """Mark proxy as unhealthy."""
        self.is_healthy = False

    def increment_connection_count(self) -> None:
        """Increment connection counter."""
        self.connection_count += 1

    def export_config(self) -> dict[str, Any]:
        """Export configuration.

        Returns:
            Dictionary of configuration
        """
        return {
            "host": self.config.host,
            "port": self.config.port,
            "version": self.config.version.value,
            "timeout": self.config.timeout,
            "is_healthy": self.is_healthy,
            "connection_count": self.connection_count,
        }


class UpstreamSOCKSProxyManager:
    """Manages upstream SOCKS proxies."""

    def __init__(self) -> None:
        """Initialize upstream SOCKS proxy manager."""
        self._proxies: dict[str, UpstreamSOCKSProxy] = {}
        logger.debug("UpstreamSOCKSProxyManager initialized")

    def register_proxy(self, name: str, config: SOCKSConfig) -> bool:
        """Register an upstream SOCKS proxy.

        Args:
            name: Proxy name/identifier
            config: SOCKS configuration

        Returns:
            True if registered
        """
        if name in self._proxies:
            logger.warning(f"SOCKS proxy already registered: {name}")
            return False

        try:
            proxy = UpstreamSOCKSProxy(config)
            self._proxies[name] = proxy
            logger.info(f"Upstream SOCKS proxy registered: {name}")
            return True
        except ValueError as e:
            logger.error(f"Failed to register SOCKS proxy: {e}")
            return False

    def get_proxy(self, name: str) -> UpstreamSOCKSProxy | None:
        """Get an upstream SOCKS proxy.

        Args:
            name: Proxy name/identifier

        Returns:
            UpstreamSOCKSProxy or None
        """
        return self._proxies.get(name)

    def get_healthy_proxies(self) -> list[UpstreamSOCKSProxy]:
        """Get all healthy upstream SOCKS proxies.

        Returns:
            List of healthy proxies
        """
        return [p for p in self._proxies.values() if p.is_healthy]

    def mark_unhealthy(self, name: str) -> bool:
        """Mark proxy as unhealthy.

        Args:
            name: Proxy name/identifier

        Returns:
            True if marked
        """
        if name in self._proxies:
            self._proxies[name].mark_unhealthy()
            logger.warning(f"Upstream SOCKS proxy marked unhealthy: {name}")
            return True
        return False

    def mark_healthy(self, name: str) -> bool:
        """Mark proxy as healthy.

        Args:
            name: Proxy name/identifier

        Returns:
            True if marked
        """
        if name in self._proxies:
            self._proxies[name].mark_healthy()
            logger.info(f"Upstream SOCKS proxy marked healthy: {name}")
            return True
        return False

    def export_metrics(self) -> dict[str, Any]:
        """Export metrics.

        Returns:
            Dictionary of metrics
        """
        return {
            "total_proxies": len(self._proxies),
            "healthy_proxies": len(self.get_healthy_proxies()),
            "proxies": {
                name: proxy.export_config() for name, proxy in self._proxies.items()
            },
        }
