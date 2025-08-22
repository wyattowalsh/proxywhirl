"""Loader for openproxy.space aggregated proxy list.

The service exposes protocol‑segmented plain text lists (ip:port). We query a
small subset (http, socks4, socks5) to avoid overly large downloads.
"""

from __future__ import annotations

from typing import Dict, List

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class OpenProxySpaceLoader(BaseLoader):
    """Load proxies from openproxy.space plain text endpoints."""

    def __init__(self) -> None:
        super().__init__(
            name="openproxyspace",
            description="OpenProxySpace plain text proxies",
        )
        base = "https://openproxy.space/list"
        # Only first page per protocol to limit volume; can be extended.
        self.urls: Dict[str, str] = {
            "http": f"{base}/http",
            "socks4": f"{base}/socks4",
            "socks5": f"{base}/socks5",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def load(self) -> DataFrame:  # pragma: no cover - network variability
        rows: List[dict[str, object]] = []
        try:
            with httpx.Client(timeout=20.0) as client:
                for proto, url in self.urls.items():
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
                        rows.append({"host": host, "port": port, "protocol": proto})
            df = pd.DataFrame(rows)
            logger.info(f"Loaded {len(df)} proxies from {self.name}")
            return df
        except Exception as e:  # pragma: no cover - network variability
            logger.error(f"Error loading proxy source data from {self.name}: {e}")
            raise
