"""Loader for PubProxy API service."""

from __future__ import annotations

from typing import List

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class PubProxyLoader(BaseLoader):
    """Load proxies from PubProxy API service.

    Provides access to a curated list of public proxies via JSON API.
    Includes detailed proxy information like country, anonymity level, and speed.

    Features:
    - JSON API with structured proxy data
    - Proxy quality metrics (speed, anonymity level)
    - Geographic information (country)
    - Support capabilities (HTTPS, cookies, etc.)
    - Regular updates and validation
    """

    def __init__(self) -> None:
        """Initialize PubProxy loader with API endpoint."""
        super().__init__(
            name="pubproxy",
            description="Curated proxies from PubProxy API service",
        )
        # Fetch more proxies with basic filtering
        self.url = "http://pubproxy.com/api/proxy"
        self.params = {
            "limit": 20,  # Get up to 20 proxies
            "format": "json",
            "type": "http",  # Focus on HTTP proxies
            "level": "elite,anonymous",  # Higher quality proxies
            "speed": "1,2,3,4,5",  # All speed levels
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def load(self) -> DataFrame:
        """Load proxies from PubProxy API.

        Returns:
            DataFrame: Proxy data with host, port, protocol, and metadata columns

        Raises:
            httpx.HTTPError: If the request fails after retries
        """
        rows: List[dict[str, object]] = []

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.url, params=self.params)
                response.raise_for_status()

                data = response.json()

                # Extract proxy list from response
                proxies = data.get("data", [])
                count = data.get("count", 0)

                if not proxies:
                    logger.warning("No proxies returned from PubProxy API")
                    return pd.DataFrame(rows)

                logger.debug(f"PubProxy API returned {count} proxies")

                # Process each proxy
                for proxy in proxies:
                    try:
                        host = str(proxy.get("ip", "")).strip()
                        port = int(str(proxy.get("port", "")))

                        # Validate basic requirements
                        if not host or not (1 <= port <= 65535):
                            continue

                        # Extract additional metadata
                        country = str(proxy.get("country", "")).upper()
                        proxy_level = str(proxy.get("proxy_level", ""))
                        proxy_type = str(proxy.get("type", "http")).lower()
                        speed = str(proxy.get("speed", ""))

                        # Build proxy record
                        proxy_record = {
                            "host": host,
                            "port": port,
                            "protocol": proxy_type,
                        }

                        # Add metadata if available
                        if country:
                            proxy_record["country"] = country
                        if proxy_level:
                            proxy_record["anonymity"] = proxy_level
                        if speed:
                            proxy_record["speed"] = speed

                        rows.append(proxy_record)

                    except (ValueError, TypeError, KeyError) as e:
                        logger.debug(f"Skipping invalid proxy from PubProxy: {e}")
                        continue

                logger.info(f"Loaded {len(rows)} proxies from PubProxy API")

        except httpx.HTTPError as e:
            logger.error(f"HTTP error loading PubProxy proxies: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading PubProxy proxies: {e}")
            raise

        if not rows:
            logger.warning("No valid proxies found in PubProxy API response")

        return pd.DataFrame(rows)
