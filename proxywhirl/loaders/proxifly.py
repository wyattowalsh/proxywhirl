"""Proxifly free proxy list loader.

This module provides a loader for fetching proxies from proxifly's CDN-hosted
free proxy list service. Updated every 5 minutes with 2000+ proxies.

Source: https://github.com/proxifly/free-proxy-list
"""

from __future__ import annotations

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class ProxiflyLoader(BaseLoader):
    """Load proxies from Proxifly's free proxy list.

    Fetches from CDN-hosted JSON endpoint with comprehensive proxy data
    including IP, port, protocols, country, and anonymity levels.

    Features:
    - 2000+ proxies updated every 5 minutes
    - CDN delivery for fast access
    - Multiple protocol support (HTTP, HTTPS, SOCKS4, SOCKS5)
    - Country and anonymity information
    - JSON format with structured data
    """

    def __init__(self) -> None:
        """Initialize Proxifly loader with CDN endpoint."""
        super().__init__(
            name="Proxifly", description="Proxies from Proxifly CDN-hosted free proxy list"
        )
        self.url = (
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def load(self) -> DataFrame:
        """Load proxies from Proxifly CDN endpoint.

        Returns:
            DataFrame with columns: host, port, protocol, country

        Raises:
            Exception: If fetching or parsing fails after retries
        """
        logger.info(f"Fetching proxies from {self.name}")

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.url, headers={"User-Agent": "ProxyWhirl/1.0"})
                response.raise_for_status()
                data = response.json()

                if not data:
                    logger.warning(f"No data received from {self.name}")
                    return pd.DataFrame()

                logger.info(f"Received {len(data)} proxies from {self.name}")

                # Parse JSON data into DataFrame
                proxies = []
                for item in data:
                    try:
                        # Extract basic proxy info
                        host = item.get("ip", "").strip()
                        port = item.get("port")
                        country = item.get("country", "").upper()

                        # Skip invalid entries
                        if not host or not port:
                            continue

                        # Convert port to integer
                        try:
                            port = int(port)
                            if not (1 <= port <= 65535):
                                continue
                        except (ValueError, TypeError):
                            continue

                        # Extract supported protocols
                        protocols = item.get("protocols", [])
                        if not protocols:
                            # Default to HTTP if no protocols specified
                            protocols = ["http"]

                        # Create entry for each supported protocol
                        for protocol in protocols:
                            scheme = protocol.lower().strip()
                            if scheme in ["http", "https", "socks4", "socks5"]:
                                proxies.append(
                                    {
                                        "host": host,
                                        "port": port,
                                        "protocol": scheme,
                                        "country": country[:2] if country else "",
                                    }
                                )

                    except Exception as e:
                        logger.debug(f"Error parsing proxy entry: {e}")
                        continue

                if not proxies:
                    logger.warning(f"No valid proxies parsed from {self.name}")
                    return pd.DataFrame()

                df = pd.DataFrame(proxies)
                logger.info(f"Successfully loaded {len(df)} proxies from {self.name}")
                return df

        except Exception as e:
            logger.error(f"Failed to load proxies from {self.name}: {e}")
            raise
