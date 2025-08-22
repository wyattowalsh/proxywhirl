from .base import BaseLoader
from .clarketm_raw import ClarketmHttpLoader
from .fresh_proxy_list import FreshProxyListLoader
from .monosans import MonosansLoader
from .openproxyspace import OpenProxySpaceLoader
from .proxynova import ProxyNovaLoader
from .proxyscrape import ProxyScrapeLoader
from .the_speedx import TheSpeedXHttpLoader, TheSpeedXSocksLoader
from .user_provided import UserProvidedLoader

__all__ = [
    "BaseLoader",
    "FreshProxyListLoader",
    "TheSpeedXHttpLoader",
    "TheSpeedXSocksLoader",
    "ClarketmHttpLoader",
    "MonosansLoader",
    "ProxyScrapeLoader",
    "UserProvidedLoader",
    "ProxyNovaLoader",
    "OpenProxySpaceLoader",
]
