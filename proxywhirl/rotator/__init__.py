"""
Proxy rotation implementations.

This package provides both synchronous and asynchronous proxy rotators
with automatic failover, circuit breakers, and connection pooling.

Usage:
    Synchronous:
        >>> from proxywhirl.rotator import ProxyWhirl
        >>> rotator = ProxyWhirl(proxies=[...])

    Asynchronous:
        >>> from proxywhirl.rotator import AsyncProxyWhirl
        >>> rotator = AsyncProxyWhirl(proxies=[...])
"""

from proxywhirl.rotator.async_ import AsyncProxyWhirl, LRUAsyncClientPool
from proxywhirl.rotator.base import ProxyRotatorBase
from proxywhirl.rotator.client_pool import LRUClientPool
from proxywhirl.rotator.sync import ProxyWhirl

__all__ = [
    "ProxyWhirl",
    "AsyncProxyWhirl",
    "ProxyRotatorBase",
    "LRUClientPool",
    "LRUAsyncClientPool",
]
