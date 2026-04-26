"""
Custom headers support for proxies in ProxyWhirl.

Allows attaching custom HTTP headers to proxies for specialized use cases.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProxyHeaders(BaseModel):
    """Custom headers for proxy requests."""

    headers: dict[str, str] = Field(default_factory=dict, description="Custom HTTP headers")
    auth_headers: dict[str, str] = Field(default_factory=dict, description="Authentication headers")
    user_agent: Optional[str] = Field(default=None, description="Custom User-Agent header")

    model_config = ConfigDict(frozen=True)

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary of all headers.

        Returns:
            Combined dictionary of all headers
        """
        all_headers = dict(self.headers)
        all_headers.update(self.auth_headers)

        if self.user_agent:
            all_headers["User-Agent"] = self.user_agent

        return all_headers

    def merge(self, other: ProxyHeaders) -> ProxyHeaders:
        """Merge with another ProxyHeaders object.

        Args:
            other: ProxyHeaders to merge

        Returns:
            New ProxyHeaders with merged values
        """
        merged_headers = {**self.headers, **other.headers}
        merged_auth = {**self.auth_headers, **other.auth_headers}
        merged_ua = other.user_agent or self.user_agent

        return ProxyHeaders(
            headers=merged_headers,
            auth_headers=merged_auth,
            user_agent=merged_ua,
        )


class CustomHeadersManager:
    """Manager for custom proxy headers."""

    def __init__(self):
        """Initialize the headers manager."""
        self._default_headers = ProxyHeaders()
        self._pool_headers: dict[str, ProxyHeaders] = {}
        self._proxy_headers: dict[str, ProxyHeaders] = {}

    def set_default_headers(self, headers: ProxyHeaders) -> None:
        """Set default headers for all proxies.

        Args:
            headers: ProxyHeaders to use as default
        """
        self._default_headers = headers

    def set_pool_headers(self, pool_id: str, headers: ProxyHeaders) -> None:
        """Set custom headers for a specific pool.

        Args:
            pool_id: Pool identifier
            headers: ProxyHeaders for the pool
        """
        self._pool_headers[pool_id] = headers

    def set_proxy_headers(self, proxy_url: str, headers: ProxyHeaders) -> None:
        """Set custom headers for a specific proxy.

        Args:
            proxy_url: Proxy URL
            headers: ProxyHeaders for the proxy
        """
        self._proxy_headers[proxy_url] = headers

    def get_headers(
        self,
        pool_id: Optional[str] = None,
        proxy_url: Optional[str] = None,
    ) -> dict[str, str]:
        """Get combined headers for a proxy.

        Args:
            pool_id: Optional pool identifier
            proxy_url: Optional proxy URL

        Returns:
            Combined dictionary of headers
        """
        headers = self._default_headers

        if pool_id and pool_id in self._pool_headers:
            headers = headers.merge(self._pool_headers[pool_id])

        if proxy_url and proxy_url in self._proxy_headers:
            headers = headers.merge(self._proxy_headers[proxy_url])

        return headers.to_dict()

    def remove_pool_headers(self, pool_id: str) -> bool:
        """Remove custom headers for a pool.

        Args:
            pool_id: Pool identifier

        Returns:
            True if removed, False if not found
        """
        if pool_id in self._pool_headers:
            del self._pool_headers[pool_id]
            return True
        return False

    def remove_proxy_headers(self, proxy_url: str) -> bool:
        """Remove custom headers for a proxy.

        Args:
            proxy_url: Proxy URL

        Returns:
            True if removed, False if not found
        """
        if proxy_url in self._proxy_headers:
            del self._proxy_headers[proxy_url]
            return True
        return False
