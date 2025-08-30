"""Proxy loaders module."""

from proxywhirl.loaders.base import BaseLoader
from proxywhirl.loaders.clarketm_raw import ClarketmHttpLoader
from proxywhirl.loaders.jetkai_proxy_list import JetkaiProxyListLoader
from proxywhirl.loaders.monosans import MonosansLoader
from proxywhirl.loaders.proxy4parsing import Proxy4ParsingLoader
from proxywhirl.loaders.proxyscrape import ProxyScrapeLoader
from proxywhirl.loaders.pubproxy import PubProxyLoader
from proxywhirl.loaders.sunny_proxy_scraper import SunnyProxyScraperLoader
from proxywhirl.loaders.the_speedx import TheSpeedXHttpLoader, TheSpeedXSocksLoader
from proxywhirl.loaders.user_provided import UserProvidedLoader
from proxywhirl.loaders.vakhov_fresh import VakhovFreshProxyLoader

__all__ = [
    "BaseLoader",
    "ClarketmHttpLoader",
    "JetkaiProxyListLoader",
    "MonosansLoader",
    "Proxy4ParsingLoader",
    "ProxyScrapeLoader",
    "PubProxyLoader",
    "SunnyProxyScraperLoader",
    "TheSpeedXHttpLoader",
    "TheSpeedXSocksLoader",
    "UserProvidedLoader",
    "VakhovFreshProxyLoader",
]
