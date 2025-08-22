"""Loader for monosans/proxy-list plain text proxy lists."""

from __future__ import annotations

from typing import List

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class MonosansLoader(BaseLoader):
    """Load proxies from monosans/proxy-list.

    Tests expect a single `.url` attribute and the ability to parse either
    JSON (with a `proxies` array) or plain text (ip:port per line). We'll use
    a consolidated endpoint in tests via mocking; real world uses per-protocol
    files, but we keep compatibility by exposing a single `url` as the main
    fetch target and falling back as needed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="monosans",
            description="Proxies from monosans/proxy-list (plain text)",
        )
        # Default to HTTP list (tests patch httpx.Client, don't hit network)
        self.url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def load(self) -> DataFrame:
        rows: List[dict[str, object]] = []
        try:
            with httpx.Client(timeout=20.0) as client:
                r = client.get(self.url)
                r.raise_for_status()
                # Prefer JSON if available
                try:
                    data = r.json()
                    items = data.get("proxies", []) if isinstance(data, dict) else []
                    for item in items:
                        try:
                            host = str(item.get("ip"))
                            port = int(str(item.get("port")))
                            proto = str(item.get("protocol", "http")).lower()
                        except (TypeError, ValueError, KeyError):
                            continue
                        if host and 1 <= port <= 65535:
                            rows.append(
                                {
                                    "host": host,
                                    "port": port,
                                    "protocol": proto,
                                }
                            )
                except (ValueError, KeyError):
                    # Fallback to text parsing (ip:port per line)
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
                                "protocol": "http",
                            }
                        )

            df = pd.DataFrame(rows)
            logger.info(f"Loaded {len(df)} proxies from {self.name}")
            return df
        except Exception as e:  # pragma: no cover - network variability
            logger.error(f"Error loading proxy source data from {self.name}: {e}")
            raise
