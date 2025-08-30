"""Loader for sunny9577/proxy-scraper JSON proxy lists."""

from __future__ import annotations

from typing import List

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class SunnyProxyScraperLoader(BaseLoader):
    """Load proxies from sunny9577/proxy-scraper GitHub repository.

    Provides structured JSON proxy data with comprehensive metadata including
    country, anonymity level, and supported protocols.

    Features:
    - JSON format with rich metadata
    - Country and region information
    - Anonymity level classification (Elite, Transparent)
    - Protocol support information
    - Regular updates via automated scraping
    """

    def __init__(self) -> None:
        """Initialize SunnyProxyScraper loader with JSON proxy list URL."""
        super().__init__(
            name="sunny-proxy-scraper",
            description="Structured proxies from sunny9577/proxy-scraper repository",
        )
        self.url = "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.json"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def load(self) -> DataFrame:
        """Load proxies from sunny9577/proxy-scraper repository.

        Returns:
            DataFrame: Proxy data with host, port, protocol, and metadata columns

        Raises:
            httpx.HTTPError: If the request fails after retries
        """
        rows: List[dict[str, object]] = []

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.url)
                response.raise_for_status()

                data = response.json()

                if not isinstance(data, list):
                    logger.error("Expected JSON array from sunny9577/proxy-scraper")
                    return pd.DataFrame(rows)

                # Process each proxy
                for proxy in data:
                    try:
                        host = str(proxy.get("ip", "")).strip()
                        port = int(str(proxy.get("port", "")))

                        # Validate basic requirements
                        if not host or not (1 <= port <= 65535):
                            continue

                        # Extract metadata
                        country = str(proxy.get("country", "")).strip()
                        anonymity = str(proxy.get("anonymity", "")).strip()
                        proxy_type = str(proxy.get("type", "")).strip()

                        # Determine protocol from type field
                        protocol = "http"
                        if proxy_type.lower() in ["http/https", "https"]:
                            protocol = "https"
                        elif proxy_type.lower() in ["socks4"]:
                            protocol = "socks4"
                        elif proxy_type.lower() in ["socks5"]:
                            protocol = "socks5"

                        # Build proxy record
                        proxy_record = {
                            "host": host,
                            "port": port,
                            "protocol": protocol,
                        }

                        # Add metadata if available
                        if country:
                            proxy_record["country"] = country
                        if anonymity:
                            proxy_record["anonymity"] = anonymity.lower()
                        if proxy_type:
                            proxy_record["type"] = proxy_type

                        rows.append(proxy_record)

                    except (ValueError, TypeError, KeyError) as e:
                        logger.debug(f"Skipping invalid proxy from sunny9577: {e}")
                        continue

                logger.info(f"Loaded {len(rows)} proxies from sunny9577/proxy-scraper")

        except httpx.HTTPError as e:
            logger.error(f"HTTP error loading sunny9577/proxy-scraper proxies: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading sunny9577/proxy-scraper proxies: {e}")
            raise

        if not rows:
            logger.warning("No valid proxies found in sunny9577/proxy-scraper response")

        return pd.DataFrame(rows)
