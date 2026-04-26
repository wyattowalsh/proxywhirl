"""
LRU cache for httpx.Client instances with automatic eviction.

This module provides a thread-safe pool for reusing HTTP client connections,
improving performance by avoiding repeated connection setup.
"""

from __future__ import annotations

import threading
from collections import OrderedDict

import httpx
from loguru import logger


class LRUClientPool:
    """
    LRU cache for httpx.Client instances with automatic eviction.

    When the pool reaches maxsize, the least recently used client is
    closed and removed to prevent unbounded memory growth.

    Supports dictionary-like access for backward compatibility with tests.
    """

    def __init__(self, maxsize: int = 100) -> None:
        """
        Initialize LRU client pool.

        Args:
            maxsize: Maximum number of clients to cache (default: 100)
        """
        self._clients: OrderedDict[str, httpx.Client] = OrderedDict()
        self._maxsize = maxsize
        self._lock = threading.Lock()

    def get(self, proxy_id: str) -> httpx.Client | None:
        """
        Get a client from the pool, marking it as recently used.

        Args:
            proxy_id: Proxy ID to look up

        Returns:
            Client if found, None otherwise
        """
        with self._lock:
            if proxy_id in self._clients:
                # Move to end (most recently used)
                self._clients.move_to_end(proxy_id)
                return self._clients[proxy_id]
            return None

    def put(self, proxy_id: str, client: httpx.Client) -> None:
        """
        Add a client to the pool, evicting LRU client if at capacity.

        Args:
            proxy_id: Proxy ID to store under
            client: Client instance to store
        """
        with self._lock:
            if proxy_id in self._clients:
                # Already exists, move to end
                self._clients.move_to_end(proxy_id)
            else:
                # Check if we need to evict
                if len(self._clients) >= self._maxsize:
                    # Evict least recently used (first item)
                    lru_proxy_id, lru_client = self._clients.popitem(last=False)
                    try:
                        lru_client.close()
                        logger.debug(
                            "Evicted LRU client from pool",
                            evicted_proxy_id=lru_proxy_id,
                            pool_size=len(self._clients),
                        )
                    except Exception as e:
                        logger.warning(
                            f"Error closing evicted client for proxy {lru_proxy_id}: {e}"
                        )

                # Add new client
                self._clients[proxy_id] = client

    def remove(self, proxy_id: str) -> None:
        """
        Remove and close a client from the pool.

        Args:
            proxy_id: Proxy ID to remove
        """
        with self._lock:
            if proxy_id in self._clients:
                client = self._clients.pop(proxy_id)
                try:
                    client.close()
                    logger.debug("Removed client from pool", proxy_id=proxy_id)
                except Exception as e:
                    logger.warning(f"Error closing client for proxy {proxy_id}: {e}")

    def clear(self) -> None:
        """Close all clients and clear the pool."""
        with self._lock:
            for proxy_id, client in self._clients.items():
                try:
                    client.close()
                    logger.debug("Closed pooled client", proxy_id=proxy_id)
                except Exception as e:
                    logger.warning(f"Error closing client for proxy {proxy_id}: {e}")
            self._clients.clear()

    def __len__(self) -> int:
        """Return number of clients in pool."""
        with self._lock:
            return len(self._clients)

    def __contains__(self, proxy_id: str) -> bool:
        """Check if proxy_id is in pool (supports 'in' operator)."""
        with self._lock:
            return proxy_id in self._clients

    def __getitem__(self, proxy_id: str) -> httpx.Client:
        """Get client by proxy_id (supports dict-like access for tests)."""
        with self._lock:
            return self._clients[proxy_id]

    def __setitem__(self, proxy_id: str, client: httpx.Client) -> None:
        """Set client for proxy_id (supports dict-like access for tests)."""
        self.put(proxy_id, client)

    def __delitem__(self, proxy_id: str) -> None:
        """Delete client for proxy_id (supports dict-like deletion)."""
        self.remove(proxy_id)
