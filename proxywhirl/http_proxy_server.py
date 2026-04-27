"""HTTP proxy source listing and serving."""

from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger


@dataclass
class ProxyListConfig:
    """Configuration for proxy list serving."""

    format: str = "text"  # text, json, csv, m3u8
    host: str = "0.0.0.0"
    port: int = 8080
    auth_enabled: bool = False
    auth_token: str | None = None
    max_age_minutes: int = 60
    cors_enabled: bool = True
    allowed_origins: list[str] = field(default_factory=lambda: ["*"])


class ProxyListServer:
    """
    Simple HTTP proxy list server.

    Serves proxy lists via HTTP in various formats:
    - Plain text (one per line)
    - JSON
    - CSV
    - M3U8 (for media player compatibility)
    """

    def __init__(self, config: ProxyListConfig):
        """
        Initialize proxy list server.

        Args:
            config: Server configuration
        """
        self.config = config
        self.proxies: list[str] = []
        self.is_running = False
        self.requests_count = 0

    def add_proxies(self, proxies: list[str]) -> None:
        """
        Add proxies to serve.

        Args:
            proxies: List of proxy URLs
        """
        self.proxies.extend(proxies)
        logger.info(f"Added {len(proxies)} proxies to serve")

    def set_proxies(self, proxies: list[str]) -> None:
        """
        Replace proxy list.

        Args:
            proxies: List of proxy URLs
        """
        self.proxies = proxies.copy()
        logger.info(f"Set {len(proxies)} proxies for serving")

    def remove_proxy(self, proxy_url: str) -> bool:
        """
        Remove a proxy from list.

        Args:
            proxy_url: Proxy URL to remove

        Returns:
            True if removed
        """
        if proxy_url in self.proxies:
            self.proxies.remove(proxy_url)
            return True

        return False

    def get_proxies_text(self) -> str:
        """
        Get proxies in plain text format.

        Returns:
            Plain text proxy list
        """
        return "\n".join(self.proxies)

    def get_proxies_json(self) -> dict:
        """
        Get proxies in JSON format.

        Returns:
            Dictionary with proxies
        """
        return {
            "count": len(self.proxies),
            "proxies": self.proxies,
        }

    def get_proxies_csv(self) -> str:
        """
        Get proxies in CSV format.

        Returns:
            CSV-formatted proxy list
        """
        lines = ["proxy_url"]
        lines.extend([f'"{p}"' for p in self.proxies])
        return "\n".join(lines)

    def get_proxies_m3u8(self) -> str:
        """
        Get proxies in M3U8 format.

        Returns:
            M3U8-formatted proxy list
        """
        lines = ["#EXTM3U"]
        for i, proxy in enumerate(self.proxies, 1):
            lines.append(f"#EXTINF:0,Proxy {i}")
            lines.append(proxy)

        return "\n".join(lines)

    def format_response(self, format_type: str | None = None) -> str | dict:
        """
        Format proxies for response.

        Args:
            format_type: Format type (overrides config)

        Returns:
            Formatted proxy list
        """
        fmt = format_type or self.config.format

        if fmt == "json":
            return self.get_proxies_json()

        elif fmt == "csv":
            return self.get_proxies_csv()

        elif fmt == "m3u8":
            return self.get_proxies_m3u8()

        else:
            return self.get_proxies_text()

    def validate_auth(self, token: str | None) -> bool:
        """
        Validate authentication token.

        Args:
            token: Auth token

        Returns:
            True if valid
        """
        if not self.config.auth_enabled:
            return True

        if self.config.auth_token is None:
            return True

        return token == self.config.auth_token

    def add_request(self) -> None:
        """Record a request."""
        self.requests_count += 1

    def get_stats(self) -> dict[str, int]:
        """
        Get server statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "running": int(self.is_running),
            "proxy_count": len(self.proxies),
            "total_requests": self.requests_count,
        }

    def start(self) -> None:
        """Start the server."""
        self.is_running = True
        logger.info(f"Proxy list server started on {self.config.host}:{self.config.port}")

    def stop(self) -> None:
        """Stop the server."""
        self.is_running = False
        logger.info("Proxy list server stopped")

    def get_endpoint_urls(self) -> dict[str, str]:
        """
        Get available endpoint URLs.

        Returns:
            Dictionary of endpoint URLs
        """
        base_url = f"http://{self.config.host}:{self.config.port}"

        return {
            "text": f"{base_url}/proxies",
            "json": f"{base_url}/proxies?format=json",
            "csv": f"{base_url}/proxies?format=csv",
            "m3u8": f"{base_url}/proxies?format=m3u8",
        }
