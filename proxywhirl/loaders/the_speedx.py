"""Loaders for TheSpeedX proxy lists (HTTP and SOCKS).

This module groups all TheSpeedX source loaders together to keep one module
per external source, as opposed to splitting by protocol.
"""

from __future__ import annotations

from typing import Dict, List

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class TheSpeedXHttpLoader(BaseLoader):
    """Load HTTP proxies from TheSpeedX GitHub repository."""

    def __init__(self) -> None:
        super().__init__(
            name="the-speedx-http",
            description="HTTP proxies from TheSpeedX/PROXY-List http.txt",
        )
        self.url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"

    async def load_async(self) -> DataFrame:
        """Load HTTP proxies asynchronously using BaseLoader's client management."""
        await self._ensure_client()
        try:
            assert self._client is not None
            r = await self._client.get(self.url)
            r.raise_for_status()
            lines: List[str] = [ln.strip() for ln in r.text.splitlines() if ln.strip()]

            rows: List[dict] = []
            for ln in lines:
                if ":" not in ln:
                    continue
                host, port_str = ln.split(":", 1)
                try:
                    port = int(port_str)
                except ValueError:
                    continue
                rows.append({"host": host, "port": port, "protocol": "http"})

            # Create DataFrame with proper columns even if empty
            if rows:
                df = pd.DataFrame(rows)
            else:
                df = pd.DataFrame(columns=["host", "port", "protocol"])
            logger.info(f"Loaded {len(df)} proxies from {self.name}")
            return df
        except Exception as e:  # pragma: no cover - network variability
            logger.error(f"Error loading proxy source data from {self.name}: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def load(self) -> DataFrame:
        """Load HTTP proxies synchronously (fallback for sync usage)."""
        try:
            with httpx.Client(timeout=20.0) as client:
                r = client.get(self.url)
                r.raise_for_status()
                lines: List[str] = [ln.strip() for ln in r.text.splitlines() if ln.strip()]

            rows: List[dict] = []
            for ln in lines:
                if ":" not in ln:
                    continue
                host, port_str = ln.split(":", 1)
                try:
                    port = int(port_str)
                except ValueError:
                    continue
                rows.append({"host": host, "port": port, "protocol": "http"})

            # Create DataFrame with proper columns even if empty
            if rows:
                df = pd.DataFrame(rows)
            else:
                df = pd.DataFrame(columns=["host", "port", "protocol"])
            logger.info(f"Loaded {len(df)} proxies from {self.name}")
            return df
        except Exception as e:  # pragma: no cover - network variability
            logger.error(f"Error loading proxy source data from {self.name}: {e}")
            raise


class TheSpeedXSocksLoader(BaseLoader):
    """Load SOCKS proxies from TheSpeedX socks4.txt and socks5.txt."""

    def __init__(self) -> None:
        super().__init__(
            name="the-speedx-socks",
            description="SOCKS proxies from TheSpeedX/PROXY-List socks4/5.txt",
        )
        self.urls = [
            ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt"),
            ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"),
        ]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def load(self) -> DataFrame:
        rows: List[Dict[str, object]] = []
        try:
            with httpx.Client(timeout=20.0) as client:
                for url in self.urls:
                    r = client.get(url)
                    r.raise_for_status()
                    proto = "socks5" if url.endswith("socks5.txt") else "socks4"
                    lines: List[str] = [ln.strip() for ln in r.text.splitlines() if ln.strip()]
                    for ln in lines:
                        if ":" not in ln:
                            continue
                        host, port_str = ln.split(":", 1)
                        try:
                            port = int(port_str)
                        except ValueError:
                            continue
                        rows.append({"host": host, "port": port, "protocol": proto})

            # Create DataFrame with proper columns even if empty
            if rows:
                df = pd.DataFrame(rows)
            else:
                df = pd.DataFrame(columns=["host", "port", "protocol"])
            logger.info(f"Loaded {len(df)} proxies from {self.name}")
            return df
        except Exception as e:  # pragma: no cover - network variability
            logger.error(f"Error loading proxy source data from {self.name}: {e}")
            raise
