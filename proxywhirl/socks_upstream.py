"""SOCKS upstream proxy chaining support."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from loguru import logger


@dataclass
class SOCKSUpstream:
    """SOCKS upstream proxy configuration."""

    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    socks_version: int = 5  # 4 or 5

    def url(self) -> str:
        """Get upstream proxy URL."""
        version_str = f"socks{self.socks_version}"
        if self.username:
            return f"{version_str}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{version_str}://{self.host}:{self.port}"

    def is_valid(self) -> bool:
        """Check if upstream configuration is valid."""
        if not self.host or self.port <= 0 or self.port > 65535:
            return False

        if self.socks_version not in (4, 5):
            return False

        if self.username and not self.password:
            return False

        return True


class SOCKSChain:
    """
    Manage SOCKS proxy chaining.

    Allows chaining proxies together:
    client -> upstream SOCKS -> final SOCKS proxy
    """

    def __init__(self):
        """Initialize SOCKS chain."""
        self.chain: list[SOCKSUpstream] = []

    def add_upstream(
        self,
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        socks_version: int = 5,
    ) -> None:
        """
        Add upstream proxy to chain.

        Args:
            host: Upstream proxy host
            port: Upstream proxy port
            username: Optional authentication username
            password: Optional authentication password
            socks_version: SOCKS protocol version (4 or 5)
        """
        upstream = SOCKSUpstream(
            host=host,
            port=port,
            username=username,
            password=password,
            socks_version=socks_version,
        )

        if not upstream.is_valid():
            raise ValueError(f"Invalid upstream configuration: {upstream}")

        self.chain.append(upstream)
        logger.debug(
            f"Added upstream to SOCKS chain: "
            f"{upstream.host}:{upstream.port} (SOCKS{upstream.socks_version})"
        )

    def remove_upstream(self, index: int) -> None:
        """
        Remove upstream at index.

        Args:
            index: Index of upstream to remove
        """
        if 0 <= index < len(self.chain):
            removed = self.chain.pop(index)
            logger.debug(f"Removed upstream: {removed.host}:{removed.port}")

    def get_chain(self) -> list[SOCKSUpstream]:
        """
        Get the proxy chain.

        Returns:
            List of upstream proxies in order
        """
        return self.chain.copy()

    def has_upstream(self) -> bool:
        """
        Check if chain has any upstream proxies.

        Returns:
            True if chain is not empty
        """
        return len(self.chain) > 0

    def get_upstream_urls(self) -> list[str]:
        """
        Get upstream proxy URLs.

        Returns:
            List of SOCKS URLs
        """
        return [upstream.url() for upstream in self.chain]

    def validate_chain(self) -> bool:
        """
        Validate entire chain.

        Returns:
            True if all upstreams are valid
        """
        return all(upstream.is_valid() for upstream in self.chain)

    def clear_chain(self) -> None:
        """Clear all upstreams from chain."""
        self.chain.clear()
        logger.debug("Cleared SOCKS chain")


class SOCKSProxyConfig:
    """
    Configuration for SOCKS proxy with optional chaining.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        socks_version: int = 5,
    ):
        """
        Initialize SOCKS proxy config.

        Args:
            host: SOCKS proxy host
            port: SOCKS proxy port
            username: Optional authentication username
            password: Optional authentication password
            socks_version: SOCKS protocol version
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.socks_version = socks_version
        self.upstream_chain = SOCKSChain()

    def add_upstream(
        self,
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        socks_version: int = 5,
    ) -> None:
        """
        Add upstream proxy to chain.

        Args:
            host: Upstream proxy host
            port: Upstream proxy port
            username: Optional authentication username
            password: Optional authentication password
            socks_version: SOCKS protocol version
        """
        self.upstream_chain.add_upstream(
            host=host,
            port=port,
            username=username,
            password=password,
            socks_version=socks_version,
        )

    def get_proxy_url(self) -> str:
        """
        Get SOCKS proxy URL.

        Returns:
            SOCKS proxy URL
        """
        version_str = f"socks{self.socks_version}"
        if self.username:
            return f"{version_str}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{version_str}://{self.host}:{self.port}"

    def get_full_chain(self) -> list[str]:
        """
        Get full chain including this proxy and upstreams.

        Returns:
            List of proxy URLs
        """
        chain = self.upstream_chain.get_upstream_urls()
        chain.append(self.get_proxy_url())
        return chain

    def is_chained(self) -> bool:
        """
        Check if proxy has upstream chain.

        Returns:
            True if upstream chain exists
        """
        return self.upstream_chain.has_upstream()

    def validate(self) -> bool:
        """
        Validate entire configuration.

        Returns:
            True if configuration is valid
        """
        if self.port <= 0 or self.port > 65535:
            return False

        if self.socks_version not in (4, 5):
            return False

        if self.username and not self.password:
            return False

        return self.upstream_chain.validate_chain()

    def to_dict(self) -> dict:
        """
        Export configuration as dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password if self.password else None,
            "socks_version": self.socks_version,
            "has_upstream_chain": self.is_chained(),
            "upstream_chain": self.upstream_chain.get_upstream_urls(),
            "full_chain": self.get_full_chain(),
        }
