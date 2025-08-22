"""Loader for ProxyNova free proxy lists.

ProxyNova publishes country-specific pages (HTML) with tables. To avoid heavy
HTML parsing dependencies we target the aggregated plain text endpoint if
available; otherwise this loader can be extended later. For now we fetch the
global HTTPS list (fallback) and parse ip:port pairs.

This is a best‑effort public source; availability may fluctuate.
"""

from __future__ import annotations

from typing import List

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class ProxyNovaLoader(BaseLoader):
    """Load proxies from proxynova.com (pattern-matched ip:port scraping)."""

    def __init__(self) -> None:
        super().__init__(
            name="proxynova",
            description=("Free proxies from proxynova.com (scraped simple list)"),
        )
        # Page containing a table of proxies (HTML). We'll regex scan it.
        self.url = "https://www.proxynova.com/proxy-server-list/port-80/"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def load(self) -> DataFrame:  # pragma: no cover - network variability
        rows: List[dict[str, object]] = []
        try:
            with httpx.Client(timeout=20.0) as client:
                r = client.get(self.url)
                r.raise_for_status()
                import re

                pattern = re.compile(r"(\b(?:\d{1,3}\.){3}\d{1,3}):(\d{2,5})")
                from typing import Set, Tuple

                seen: Set[Tuple[str, str]] = set()
                for host, port_str in pattern.findall(r.text):
                    if (host, port_str) in seen:
                        continue
                    seen.add((host, port_str))
                    try:
                        port = int(port_str)
                    except ValueError:
                        continue
                    rows.append({"host": host, "port": port, "protocol": "http"})
            df = pd.DataFrame(rows)
            logger.info(f"Loaded {len(df)} proxies from {self.name}")
            return df
        except Exception as e:  # pragma: no cover - network variability
            logger.error(f"Error loading proxy source data from {self.name}: {e}")
            raise
