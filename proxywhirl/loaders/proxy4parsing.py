"""Loader for proxy4parsing/proxy-list HTTP proxy lists."""

from __future__ import annotations

from typing import List

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class Proxy4ParsingLoader(BaseLoader):
    """Load proxies from proxy4parsing/proxy-list GitHub repository.
    
    Provides HTTP proxies in plain text format (IP:PORT per line).
    Updated regularly with working proxy servers.
    
    Features:
    - HTTP proxy list updated regularly
    - Simple text format for reliable parsing
    - GitHub-hosted for good availability
    - Active maintenance and updates
    """

    def __init__(self) -> None:
        """Initialize Proxy4Parsing loader with HTTP proxy list URL."""
        super().__init__(
            name="proxy4parsing",
            description="HTTP proxies from proxy4parsing/proxy-list repository",
        )
        self.url = "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def load(self) -> DataFrame:
        """Load HTTP proxies from proxy4parsing repository.
        
        Returns:
            DataFrame: Proxy data with host, port, and protocol columns
            
        Raises:
            httpx.HTTPError: If the request fails after retries
        """
        rows: List[dict[str, object]] = []
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.url)
                response.raise_for_status()
                
                # Parse plain text format (IP:PORT per line)
                proxy_count = 0
                for line in response.text.splitlines():
                    line = line.strip()
                    if not line or ":" not in line:
                        continue
                        
                    try:
                        host, port_str = line.split(":", 1)
                        port = int(port_str)
                        
                        # Validate port range
                        if not (1 <= port <= 65535):
                            continue
                            
                        # Validate host (basic check for IP format)
                        if not host or len(host.split(".")) != 4:
                            continue
                            
                        rows.append({
                            "host": host.strip(),
                            "port": port,
                            "protocol": "http",
                        })
                        proxy_count += 1
                        
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Skipping invalid proxy line '{line}': {e}")
                        continue
                
                logger.info(f"Loaded {proxy_count} proxies from proxy4parsing")
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error loading proxy4parsing proxies: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading proxy4parsing proxies: {e}")
            raise

        if not rows:
            logger.warning("No valid proxies found in proxy4parsing response")

        return pd.DataFrame(rows)
