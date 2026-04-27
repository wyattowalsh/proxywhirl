"""
Per-proxy custom headers support for advanced HTTP request customization.

Extends custom_headers with per-proxy header configuration, enabling
specialized header requirements on a proxy-by-proxy basis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProxyHeaderConfig:
    """Configuration for per-proxy custom headers."""

    proxy_url: str
    headers: dict[str, str] = field(default_factory=dict)
    override_global: bool = False
    merge_with_global: bool = True
    priority: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "proxy_url": self.proxy_url,
            "headers": self.headers,
            "override_global": self.override_global,
            "merge_with_global": self.merge_with_global,
            "priority": self.priority,
        }


class PerProxyHeaderManager:
    """Manages custom headers on a per-proxy basis."""

    def __init__(self):
        """Initialize headers manager."""
        self.proxy_headers: dict[str, ProxyHeaderConfig] = {}
        self.global_headers: dict[str, str] = {}

    def set_global_header(self, key: str, value: str) -> None:
        """Set a global header applied to all proxies."""
        self.global_headers[key] = value

    def remove_global_header(self, key: str) -> None:
        """Remove a global header."""
        self.global_headers.pop(key, None)

    def register_proxy_headers(
        self,
        proxy_url: str,
        headers: dict[str, str],
        override_global: bool = False,
        priority: int = 0,
    ) -> ProxyHeaderConfig:
        """Register custom headers for a proxy."""
        config = ProxyHeaderConfig(
            proxy_url=proxy_url,
            headers=headers.copy(),
            override_global=override_global,
            priority=priority,
        )
        self.proxy_headers[proxy_url] = config
        return config

    def get_proxy_headers(self, proxy_url: str) -> ProxyHeaderConfig:
        """Get headers for a proxy."""
        if proxy_url not in self.proxy_headers:
            self.proxy_headers[proxy_url] = ProxyHeaderConfig(proxy_url=proxy_url)
        return self.proxy_headers[proxy_url]

    def get_effective_headers(self, proxy_url: str) -> dict[str, str]:
        """Get effective headers combining global and proxy-specific."""
        headers = self.global_headers.copy()

        if proxy_url in self.proxy_headers:
            config = self.proxy_headers[proxy_url]
            if config.override_global:
                headers = config.headers.copy()
            elif config.merge_with_global:
                headers.update(config.headers)

        return headers

    def remove_proxy_headers(self, proxy_url: str) -> None:
        """Remove headers for a proxy."""
        self.proxy_headers.pop(proxy_url, None)

    def get_all_proxy_configs(self) -> dict[str, ProxyHeaderConfig]:
        """Get all proxy header configurations."""
        return self.proxy_headers.copy()

    def apply_headers_to_request(
        self,
        proxy_url: str,
        request_headers: dict[str, str],
    ) -> dict[str, str]:
        """Apply proxy-specific headers to request headers."""
        effective = self.get_effective_headers(proxy_url)
        merged = request_headers.copy()
        merged.update(effective)
        return merged


__all__ = ["PerProxyHeaderManager", "ProxyHeaderConfig"]
