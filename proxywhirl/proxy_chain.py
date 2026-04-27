"""Proxy chaining - route requests through multiple proxies for anonymity layers.

Allows chaining proxies where response from proxy A becomes request through proxy B.
"""

from dataclasses import dataclass
from typing import Any, Optional

from loguru import logger

from proxywhirl.models import Proxy, ProxyPool


@dataclass
class ProxyChainNode:
    """A single proxy in the chain."""

    proxy: Proxy
    position: int
    error_count: int = 0
    success_count: int = 0


class ProxyChain:
    """Chain of proxies for layered anonymity."""

    def __init__(self, chain_id: Optional[str] = None) -> None:
        """Initialize proxy chain."""
        self.chain_id = chain_id or self._generate_id()
        self.nodes: list[ProxyChainNode] = []
        self._current_index = 0

    @staticmethod
    def _generate_id() -> str:
        """Generate unique chain ID."""
        import uuid

        return f"chain_{uuid.uuid4().hex[:8]}"

    def add_proxy(self, proxy: Proxy) -> None:
        """Add proxy to chain."""
        position = len(self.nodes)
        node = ProxyChainNode(proxy=proxy, position=position)
        self.nodes.append(node)
        logger.debug(f"Added proxy to chain {self.chain_id}: {proxy.url} (position {position})")

    def remove_proxy(self, proxy_id: str) -> bool:
        """Remove proxy from chain by ID."""
        for i, node in enumerate(self.nodes):
            if node.proxy.id == proxy_id:
                self.nodes.pop(i)
                # Reindex positions
                for j, n in enumerate(self.nodes):
                    n.position = j
                logger.debug(f"Removed proxy from chain {self.chain_id}: {proxy_id}")
                return True
        return False

    def get_chain_urls(self) -> list[str]:
        """Get all proxy URLs in order."""
        return [node.proxy.url for node in self.nodes]

    def get_current_proxy(self) -> Optional[Proxy]:
        """Get the current proxy in the chain."""
        if self._current_index < len(self.nodes):
            return self.nodes[self._current_index].proxy
        return None

    def get_next_proxy(self) -> Optional[Proxy]:
        """Get the next proxy in the chain."""
        self._current_index += 1
        return self.get_current_proxy()

    def reset(self) -> None:
        """Reset to first proxy in chain."""
        self._current_index = 0

    def mark_success(self) -> None:
        """Mark current proxy as successful."""
        if 0 <= self._current_index < len(self.nodes):
            self.nodes[self._current_index].success_count += 1

    def mark_error(self) -> None:
        """Mark current proxy as failed."""
        if 0 <= self._current_index < len(self.nodes):
            self.nodes[self._current_index].error_count += 1

    def is_complete(self) -> bool:
        """Check if chain traversal is complete."""
        return self._current_index >= len(self.nodes)

    def is_empty(self) -> bool:
        """Check if chain is empty."""
        return len(self.nodes) == 0

    def get_chain_stats(self) -> dict[str, Any]:
        """Get statistics for the chain."""
        if not self.nodes:
            return {"chain_id": self.chain_id, "length": 0}

        total_success = sum(node.success_count for node in self.nodes)
        total_errors = sum(node.error_count for node in self.nodes)
        total_requests = total_success + total_errors

        return {
            "chain_id": self.chain_id,
            "length": len(self.nodes),
            "total_requests": total_requests,
            "total_success": total_success,
            "total_errors": total_errors,
            "success_rate": (total_success / total_requests if total_requests > 0 else 0.0),
            "nodes": [
                {
                    "position": node.position,
                    "proxy_url": node.proxy.url,
                    "success": node.success_count,
                    "errors": node.error_count,
                }
                for node in self.nodes
            ],
        }


class ProxyChainManager:
    """Manager for multiple proxy chains."""

    def __init__(self) -> None:
        """Initialize chain manager."""
        self.chains: dict[str, ProxyChain] = {}

    def create_chain(self, chain_id: Optional[str] = None) -> ProxyChain:
        """Create a new proxy chain."""
        chain = ProxyChain(chain_id=chain_id)
        self.chains[chain.chain_id] = chain
        logger.debug(f"Created proxy chain: {chain.chain_id}")
        return chain

    def get_chain(self, chain_id: str) -> Optional[ProxyChain]:
        """Get chain by ID."""
        return self.chains.get(chain_id)

    def delete_chain(self, chain_id: str) -> bool:
        """Delete a chain."""
        if chain_id in self.chains:
            del self.chains[chain_id]
            logger.debug(f"Deleted proxy chain: {chain_id}")
            return True
        return False

    def add_proxy_to_chain(self, chain_id: str, proxy: Proxy) -> bool:
        """Add proxy to existing chain."""
        chain = self.get_chain(chain_id)
        if chain:
            chain.add_proxy(proxy)
            return True
        return False

    def create_chain_from_pool(
        self,
        pool: ProxyPool,
        chain_length: int = 3,
        exclude_unhealthy: bool = True,
    ) -> Optional[ProxyChain]:
        """Create a chain from pool proxies."""
        proxies = pool.get_all_proxies()

        if exclude_unhealthy:
            from proxywhirl.models import HealthStatus

            proxies = [p for p in proxies if p.health_status != HealthStatus.UNHEALTHY]

        if len(proxies) < chain_length:
            logger.warning(
                f"Not enough proxies for chain of length {chain_length}. Found {len(proxies)}"
            )
            return None

        # Create chain with first N proxies
        chain = self.create_chain()
        for proxy in proxies[:chain_length]:
            chain.add_proxy(proxy)

        return chain

    def list_chains(self) -> list[str]:
        """List all chain IDs."""
        return list(self.chains.keys())

    def get_all_chains_stats(self) -> dict[str, Any]:
        """Get statistics for all chains."""
        return {chain_id: chain.get_chain_stats() for chain_id, chain in self.chains.items()}


# Utility functions for working with chains


def create_chain_from_urls(urls: list[str]) -> ProxyChain:
    """Create a proxy chain from list of proxy URLs."""
    chain = ProxyChain()

    for url in urls:
        proxy = Proxy(url=url)
        chain.add_proxy(proxy)

    return chain


def rotate_chain_order(chain: ProxyChain) -> None:
    """Rotate proxy order in chain (move first to end)."""
    if chain.nodes:
        first_node = chain.nodes.pop(0)
        chain.nodes.append(first_node)

        # Reindex positions
        for i, node in enumerate(chain.nodes):
            node.position = i

        logger.debug(f"Rotated chain order: {chain.chain_id}")


def shuffle_chain_order(chain: ProxyChain) -> None:
    """Shuffle proxy order in chain."""
    import random

    random.shuffle(chain.nodes)

    # Reindex positions
    for i, node in enumerate(chain.nodes):
        node.position = i

    logger.debug(f"Shuffled chain order: {chain.chain_id}")


def merge_chains(chain1: ProxyChain, chain2: ProxyChain) -> ProxyChain:
    """Merge two chains into a new chain."""
    merged = ProxyChain()

    for node in chain1.nodes + chain2.nodes:
        merged.add_proxy(node.proxy)

    return merged
