"""Vakhov fresh proxy list loader.

This module provides a loader for fetching proxies from vakhov's GitHub Pages
hosted fresh proxy list service. Updated every 5-20 minutes.

Source: https://github.com/vakhov/fresh-proxy-list
"""

from __future__ import annotations

from typing import List

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class VakhovFreshProxyLoader(BaseLoader):
    """Load proxies from Vakhov's fresh proxy list.

    Fetches from GitHub Pages hosted endpoints with protocol-specific
    proxy lists updated every 5-20 minutes.

    Features:
    - 500+ proxies updated every 5-20 minutes
    - GitHub Pages hosting for reliability
    - Protocol-specific endpoints
    - Simple IP:Port format
    """

    def __init__(self) -> None:
        """Initialize Vakhov loader with GitHub Pages endpoints."""
        super().__init__(
            name="VakhovFresh", description="Proxies from Vakhov fresh proxy list (GitHub Pages)"
        )
        # Multiple endpoints for different protocols
        self.urls = {
            "http": "https://vakhov.github.io/fresh-proxy-list/http.txt",
            "https": "https://vakhov.github.io/fresh-proxy-list/https.txt",
            "socks4": "https://vakhov.github.io/fresh-proxy-list/socks4.txt",
            "socks5": "https://vakhov.github.io/fresh-proxy-list/socks5.txt",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def load(self) -> DataFrame:
        """Load proxies from Vakhov GitHub Pages endpoints.

        Returns:
            DataFrame with columns: host, port, protocol

        Raises:
            Exception: If fetching or parsing fails after retries
        """
        logger.info(f"Fetching proxies from {self.name}")

        all_proxies = []

        try:
            with httpx.Client(timeout=20.0) as client:
                for protocol, url in self.urls.items():
                    try:
                        logger.debug(f"Fetching {protocol} proxies from {url}")
                        response = client.get(url, headers={"User-Agent": "ProxyWhirl/1.0"})
                        response.raise_for_status()

                        # Parse text format (IP:Port per line)
                        lines: List[str] = [
                            line.strip() for line in response.text.splitlines() if line.strip()
                        ]

                        protocol_proxies = []
                        for line in lines:
                            if ":" not in line:
                                continue

                            try:
                                host, port_str = line.split(":", 1)
                                host = host.strip()
                                port = int(port_str.strip())

                                # Validate port range
                                if not (1 <= port <= 65535):
                                    continue

                                # Validate host is not empty
                                if not host:
                                    continue

                                protocol_proxies.append(
                                    {"host": host, "port": port, "protocol": protocol}
                                )

                            except (ValueError, IndexError) as e:
                                logger.debug(f"Error parsing line '{line}': {e}")
                                continue

                        logger.info(f"Loaded {len(protocol_proxies)} {protocol} proxies")
                        all_proxies.extend(protocol_proxies)

                    except Exception as e:
                        logger.warning(f"Failed to load {protocol} proxies: {e}")
                        continue  # Try other protocols even if one fails

                if not all_proxies:
                    logger.warning(f"No valid proxies parsed from {self.name}")
                    return pd.DataFrame()

                df = pd.DataFrame(all_proxies)
                logger.info(f"Successfully loaded {len(df)} total proxies from {self.name}")
                return df

        except Exception as e:
            logger.error(f"Failed to load proxies from {self.name}: {e}")
            raise
