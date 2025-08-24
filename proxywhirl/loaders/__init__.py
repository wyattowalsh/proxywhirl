from .base import BaseLoader
from .clarketm_raw import ClarketmHttpLoader
from .jetkai_proxy_list import JetkaiProxyListLoader
from .monosans import MonosansLoader
from .proxifly import ProxiflyLoader
from .proxyscrape import ProxyScrapeLoader
from .the_speedx import TheSpeedXHttpLoader, TheSpeedXSocksLoader
from .user_provided import UserProvidedLoader
from .vakhov_fresh import VakhovFreshProxyLoader

__all__ = [
    "BaseLoader",
    "TheSpeedXHttpLoader",
    "TheSpeedXSocksLoader",
    "ClarketmHttpLoader",
    "MonosansLoader",
    "ProxyScrapeLoader",
    "UserProvidedLoader",
    # New working loaders
    "ProxiflyLoader",
    "VakhovFreshProxyLoader",
    "JetkaiProxyListLoader",
]
