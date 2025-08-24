"""Jetkai proxy list loader.

This module provides a loader for fetching proxies from jetkai's tested
proxy list on GitHub. Updated hourly with verified working proxies.

Source: https://github.com/jetkai/proxy-list
"""

from __future__ import annotations

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class JetkaiProxyListLoader(BaseLoader):
    """Load proxies from Jetkai's tested proxy list.

    Fetches from GitHub raw JSON endpoint with verified working proxies
    that are tested against hosting providers every hour.

    Features:
    - 4000+ tested and verified working proxies
    - Updated hourly (24/7)
    - Comprehensive testing against EU/US hosting providers
    - JSON format with geolocation and metadata
    - High reliability (only working proxies included)
    """

    def __init__(self) -> None:
        """Initialize Jetkai loader with GitHub raw endpoint."""
        super().__init__(
            name="JetkaiProxyList",
            description="Tested proxies from Jetkai proxy list (hourly updates)",
        )
        self.url = "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/json/proxies.json"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def load(self) -> DataFrame:
        """Load proxies from Jetkai GitHub repository.

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

                # The JSON format is {protocol: [ip:port strings]}
                proxies = []

                if isinstance(data, dict):
                    for protocol_key, proxy_list in data.items():  # type: ignore
                        if isinstance(proxy_list, list):
                            logger.info(f"Processing {len(proxy_list)} {protocol_key} proxies")

                            for proxy_item in proxy_list:  # type: ignore
                                if isinstance(proxy_item, str) and ":" in proxy_item:
                                    try:
                                        host, port_str = proxy_item.rsplit(":", 1)
                                        port = int(port_str.strip())

                                        # Validate port range
                                        if not (1 <= port <= 65535):
                                            continue

                                        # Normalize protocol
                                        norm_protocol = str(protocol_key).lower().strip()  # type: ignore
                                        if norm_protocol not in [
                                            "http",
                                            "https",
                                            "socks4",
                                            "socks5",
                                        ]:
                                            continue

                                        proxies.append(
                                            {
                                                "host": host.strip(),
                                                "port": port,
                                                "protocol": norm_protocol,
                                                "country": "",  # Not provided in this format
                                            }
                                        )
                                    except (ValueError, IndexError) as e:
                                        logger.debug(f"Invalid proxy format '{proxy_item}': {e}")
                                        continue
                else:
                    logger.error(f"Unexpected JSON format: expected dict, got {type(data)}")
                    return pd.DataFrame()

                if not proxies:
                    logger.warning(f"No valid proxies parsed from {self.name}")
                    return pd.DataFrame()

                df = pd.DataFrame(proxies)
                logger.info(f"Successfully loaded {len(df)} proxies from {self.name}")
                return df

        except Exception as e:
            logger.error(f"Failed to load proxies from {self.name}: {e}")
            raise
