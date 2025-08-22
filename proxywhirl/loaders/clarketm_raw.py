"""Loader for clarketm/proxy-list daily HTTP proxies (raw ip:port lines)."""

from __future__ import annotations

from typing import List

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class ClarketmHttpLoader(BaseLoader):
    """Load HTTP proxies from clarketm/proxy-list (daily/http.txt)."""

    def __init__(self) -> None:
        super().__init__(
            name="clarketm-http",
            description="HTTP proxies from clarketm/proxy-list daily/http.txt",
        )
        self.url = "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def load(self) -> DataFrame:
        try:
            with httpx.Client(timeout=20.0) as client:
                r = client.get(self.url)
                r.raise_for_status()
                lines: List[str] = [ln.strip() for ln in r.text.splitlines() if ln.strip()]

            rows = []
            for ln in lines:
                if ":" not in ln:
                    continue
                host, port_str = ln.split(":", 1)
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
