"""proxywhirl/loaders/fresh_proxy_list.py -- loader for Fresh Proxy List.

From https://github.com/vakhov/fresh-proxy-list
"""

import httpx
import pandas as pd
from loguru import logger
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.loaders.base import BaseLoader


class FreshProxyListLoader(BaseLoader):
    """Loader for fresh-proxy-list.com"""

    def __init__(self):
        super().__init__(
            name="fresh-proxy-list",
            description="Loader for fresh-proxy-list from freshproxylist.com",
        )
        self.url = "https://www.freshproxylist.com/"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=15),
    )
    def load(self) -> DataFrame:
        """Load proxy source data"""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.url)
                response.raise_for_status()
                data = response.json()

            df = pd.DataFrame(data)
            logger.info(f"Loaded {len(df)} proxies from {self.name}")
            return df

        except Exception as e:
            logger.error(f"Error loading proxy source data from {self.name}: {e}")
            raise e
