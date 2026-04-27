"""Fallback proxy chain support."""

from typing import List, Optional
from dataclasses import dataclass
from proxywhirl.models import Proxy
from loguru import logger


@dataclass
class ProxyChain:
    """Chain of fallback proxies."""
    proxies: List[Proxy]
    name: str
    description: Optional[str] = None
    
    def __iter__(self):
        return iter(self.proxies)
    
    def get_next(self, current_index: int) -> Optional[Proxy]:
        """Get next proxy in chain."""
        if current_index + 1 < len(self.proxies):
            return self.proxies[current_index + 1]
        return None


class FallbackChainManager:
    """Manages fallback proxy chains."""
    
    def __init__(self):
        self.chains: dict[str, ProxyChain] = {}
    
    def register_chain(self, chain: ProxyChain) -> None:
        """Register a fallback chain."""
        self.chains[chain.name] = chain
        logger.info(f"Registered chain '{chain.name}' with {len(chain.proxies)} proxies")
    
    def get_chain(self, name: str) -> Optional[ProxyChain]:
        """Get chain by name."""
        return self.chains.get(name)
    
    def select_with_fallbacks(
        self,
        chain_name: str,
        start_index: int = 0
    ) -> Optional[Proxy]:
        """Select proxy from chain with fallback."""
        chain = self.get_chain(chain_name)
        if not chain or start_index >= len(chain.proxies):
            return None
        return chain.proxies[start_index]
    
    def list_chains(self) -> List[str]:
        """List available chains."""
        return list(self.chains.keys())

