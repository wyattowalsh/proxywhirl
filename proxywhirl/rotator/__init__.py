"""
Proxy rotation implementations.

This package provides both synchronous and asynchronous proxy rotators
with automatic failover, circuit breakers, and connection pooling.

Usage:
    Synchronous:
        >>> from proxywhirl.rotator import ProxyRotator
        >>> rotator = ProxyRotator(proxies=[...])

    Asynchronous:
        >>> from proxywhirl.rotator import AsyncProxyRotator
        >>> rotator = AsyncProxyRotator(proxies=[...])
"""

from proxywhirl.rotator.async_ import AsyncProxyRotator, LRUAsyncClientPool
from proxywhirl.rotator.base import ProxyRotatorBase
from proxywhirl.rotator.client_pool import LRUClientPool
from proxywhirl.rotator.sync import ProxyRotator

__all__ = [
    "ProxyRotator",
    "AsyncProxyRotator",
    "ProxyRotatorBase",
    "LRUClientPool",
    "LRUAsyncClientPool",
]
