"""Proxy loaders module."""

from proxywhirl.loaders.base import BaseLoader
from proxywhirl.loaders.clarketm import ClarketmLoader
from proxywhirl.loaders.jetkai_proxy_list import JetkaiProxyListLoader
from proxywhirl.loaders.monosans import MonosansLoader
from proxywhirl.loaders.proxy4parsing import Proxy4ParsingLoader
from proxywhirl.loaders.proxy_scrape import ProxyScrapeLoader
from proxywhirl.loaders.pubproxy import PubProxyLoader
from proxywhirl.loaders.sunny_proxy_scraper import SunnyProxyScraperLoader
from proxywhirl.loaders.thespeedx import TheSpeedXLoader
from proxywhirl.loaders.user_provided import UserProvidedLoader
from proxywhirl.loaders.vakhov_fresh import VakhovFreshLoader

__all__ = [
    "BaseLoader",
    "ClarketmLoader",
    "JetkaiProxyListLoader",
    "MonosansLoader",
    "Proxy4ParsingLoader",
    "ProxyScrapeLoader",
    "PubProxyLoader",
    "SunnyProxyScraperLoader",
    "TheSpeedXLoader",
    "UserProvidedLoader",
    "VakhovFreshLoader",
]
