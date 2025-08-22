"""Loader for ProxyScrape public API for free proxies."""

from __future__ import annotations

from typing import List

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class ProxyScrapeLoader(BaseLoader):
    """Load proxies from ProxyScrape API (http, https, socks4, socks5)."""

    def __init__(self) -> None:
        super().__init__(name="proxyscrape", description="ProxyScrape free proxy API")
        # See docs: https://proxyscrape.com/free-proxy-list
        self.base = "https://api.proxyscrape.com/v3/free-proxy-list/get"
        # Single url for tests (override via getattr)
        self.url = f"{self.base}?request=getproxies&proxy_format=ipport"
        # Use 10000 as large limit; API may cap internally
        self.queries = {
            "http": f"{self.base}?request=getproxies&proxy_format=ipport&format=text&protocol=http&limit=10000",  # noqa: E501
            "https": f"{self.base}?request=getproxies&proxy_format=ipport&format=text&protocol=https&limit=10000",  # noqa: E501
            "socks4": f"{self.base}?request=getproxies&proxy_format=ipport&format=text&protocol=socks4&limit=10000",  # noqa: E501
            "socks5": f"{self.base}?request=getproxies&proxy_format=ipport&format=text&protocol=socks5&limit=10000",  # noqa: E501
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def load(self) -> DataFrame:
        rows: List[dict[str, object]] = []
        try:
            with httpx.Client(timeout=20.0) as client:
                for proto, url in self.queries.items():
                    r = client.get(url)
                    r.raise_for_status()
                    for ln in r.text.splitlines():
                        s = ln.strip()
                        if not s or ":" not in s:
                            continue
                        host, port_str = s.split(":", 1)
                        try:
                            port = int(port_str)
                        except ValueError:
                            continue
                        rows.append(
                            {
                                "host": host,
                                "port": port,
                                "protocol": proto,
                            }
                        )

            df = pd.DataFrame(rows)
            logger.info(f"Loaded {len(df)} proxies from {self.name}")
            return df
        except Exception as e:  # pragma: no cover - network variability
            logger.error(f"Error loading proxy source data from {self.name}: {e}")
            raise
