"""
Loader that accepts a user-provided list of proxies (dicts) and returns a
DataFrame. Optionally validates minimal schema.
"""

from __future__ import annotations

from typing import Iterable, Mapping

import pandas as pd
from pandas import DataFrame

from proxywhirl.loaders.base import BaseLoader


class UserProvidedLoader(BaseLoader):
    """Wrap a user-provided iterable of proxy dicts to feed ProxyWhirl."""

    def __init__(self, proxies: Iterable[Mapping[str, object]], name: str = "user") -> None:
        super().__init__(name=name, description="User-provided proxies")
        self._proxies = list(proxies)

    def load(self) -> DataFrame:
        # Minimal normalization happens downstream in ProxyWhirl.fetch_proxies
        return pd.DataFrame(self._proxies)
