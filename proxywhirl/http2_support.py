"""HTTP/2 protocol support for proxies."""

from enum import Enum

import httpx


class HTTPVersion(str, Enum):
    """HTTP protocol versions."""

    HTTP1 = "HTTP/1.1"
    HTTP2 = "HTTP/2"
    HTTP3 = "HTTP/3"


class HTTP2Detector:
    """Detects and manages HTTP/2 support."""

    def __init__(self):
        self.h2_capable_proxies: set = set()
        self.h1_only_proxies: set = set()

    async def check_http2_support(self, proxy_url: str) -> bool:
        """Check if proxy supports HTTP/2."""
        try:
            # Try HTTP/2 with async client
            async with httpx.AsyncClient(proxies=proxy_url, http2=True) as client:
                response = await client.get("https://httpbin.org/get", timeout=10)
                h2_supported = response.http_version == "HTTP/2"

                if h2_supported:
                    self.h2_capable_proxies.add(proxy_url)
                else:
                    self.h1_only_proxies.add(proxy_url)

                return h2_supported
        except Exception:
            self.h1_only_proxies.add(proxy_url)
            return False

    def get_http_version(self, proxy_url: str) -> HTTPVersion:
        """Get HTTP version for proxy."""
        if proxy_url in self.h2_capable_proxies:
            return HTTPVersion.HTTP2
        return HTTPVersion.HTTP1

    def get_h2_capable_proxies(self) -> list:
        """Get list of HTTP/2 capable proxies."""
        return list(self.h2_capable_proxies)
