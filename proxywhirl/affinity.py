"""Proxy affinity/stickiness - return same proxy for multiple requests in a session.

Ensures a user/session gets the same proxy for consistent behavior.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from loguru import logger

from proxywhirl.models import Proxy, ProxyPool


@dataclass
class AffinitySession:
    """Session with proxy affinity."""

    session_id: str
    assigned_proxy_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_used_at: datetime = field(default_factory=datetime.now)
    request_count: int = 0
    ttl_seconds: Optional[int] = None

    def is_expired(self) -> bool:
        """Check if session has expired."""
        if self.ttl_seconds is None:
            return False

        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expiry_time

    def mark_used(self) -> None:
        """Mark session as recently used."""
        self.last_used_at = datetime.now()
        self.request_count += 1


class ProxyAffinityManager:
    """Manages proxy affinity/stickiness for sessions."""

    def __init__(self, default_ttl: Optional[int] = 3600) -> None:
        """Initialize affinity manager.

        Args:
            default_ttl: Default session TTL in seconds (None = no expiry)
        """
        self.default_ttl = default_ttl
        self.sessions: dict[str, AffinitySession] = {}
        self.proxy_pool: Optional[ProxyPool] = None

    def set_proxy_pool(self, pool: ProxyPool) -> None:
        """Set the proxy pool for affinity selection."""
        self.proxy_pool = pool

    def create_session(
        self,
        session_id: str,
        proxy_id: str,
        ttl_seconds: Optional[int] = None,
    ) -> AffinitySession:
        """Create new affinity session."""
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl

        session = AffinitySession(
            session_id=session_id,
            assigned_proxy_id=proxy_id,
            ttl_seconds=ttl,
        )
        self.sessions[session_id] = session
        logger.debug(f"Created affinity session: {session_id} -> {proxy_id}")

        return session

    def get_proxy_for_session(self, session_id: str) -> Optional[Proxy]:
        """Get assigned proxy for session."""
        session = self.sessions.get(session_id)

        if not session:
            return None

        if session.is_expired():
            logger.debug(f"Affinity session expired: {session_id}")
            del self.sessions[session_id]
            return None

        session.mark_used()

        if not self.proxy_pool:
            logger.warning("No proxy pool set for affinity manager")
            return None

        # Find proxy by ID
        proxy = self.proxy_pool.get_proxy(session.assigned_proxy_id)
        return proxy

    def assign_proxy_to_session(
        self,
        session_id: str,
        proxy: Proxy,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Assign proxy to session."""
        self.create_session(session_id, proxy.id, ttl_seconds=ttl_seconds)

    def remove_session(self, session_id: str) -> bool:
        """Remove affinity session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.debug(f"Removed affinity session: {session_id}")
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """Remove all expired sessions."""
        expired_ids = [sid for sid, session in self.sessions.items() if session.is_expired()]

        for sid in expired_ids:
            del self.sessions[sid]

        if expired_ids:
            logger.debug(f"Cleaned up {len(expired_ids)} expired sessions")

        return len(expired_ids)

    def get_session_info(self, session_id: str) -> Optional[dict]:
        """Get information about a session."""
        session = self.sessions.get(session_id)

        if not session:
            return None

        return {
            "session_id": session.session_id,
            "proxy_id": session.assigned_proxy_id,
            "created_at": session.created_at.isoformat(),
            "last_used_at": session.last_used_at.isoformat(),
            "request_count": session.request_count,
            "ttl_seconds": session.ttl_seconds,
            "is_expired": session.is_expired(),
        }

    def list_sessions(self) -> dict[str, dict]:
        """List all active sessions."""
        self.cleanup_expired_sessions()

        return {
            sid: {
                "proxy_id": session.assigned_proxy_id,
                "request_count": session.request_count,
                "last_used": session.last_used_at.isoformat(),
            }
            for sid, session in self.sessions.items()
        }

    def get_session_stats(self) -> dict:
        """Get overall affinity statistics."""
        self.cleanup_expired_sessions()

        total_sessions = len(self.sessions)
        total_requests = sum(s.request_count for s in self.sessions.values())

        return {
            "total_sessions": total_sessions,
            "total_requests": total_requests,
            "avg_requests_per_session": (
                total_requests / total_sessions if total_sessions > 0 else 0
            ),
        }


class StickySessionRouter:
    """Route requests to proxy with session stickiness."""

    def __init__(self, pool: ProxyPool) -> None:
        """Initialize sticky router."""
        self.pool = pool
        self.affinity = ProxyAffinityManager()
        self.affinity.set_proxy_pool(pool)

    def get_proxy_for_request(
        self,
        session_id: str,
        fallback_strategy: str = "round_robin",
    ) -> Optional[Proxy]:
        """Get proxy for request with sticky routing."""
        # Check if session has assigned proxy
        proxy = self.affinity.get_proxy_for_session(session_id)
        if proxy:
            return proxy

        # No affinity session, create new one with next proxy
        from proxywhirl.strategies import StrategyRegistry

        strategy = StrategyRegistry().get(fallback_strategy)
        if not strategy:
            logger.error(f"Unknown strategy: {fallback_strategy}")
            return None

        from proxywhirl.models import SelectionContext

        context = SelectionContext(pool=self.pool)
        next_proxy = strategy.select(context)

        if next_proxy:
            self.affinity.assign_proxy_to_session(session_id, next_proxy)
            return next_proxy

        return None

    def reset_session(self, session_id: str) -> None:
        """Reset/clear session affinity."""
        self.affinity.remove_session(session_id)


class ConsistentHashRouter:
    """Route requests using consistent hashing for stable proxy selection."""

    def __init__(self, pool: ProxyPool) -> None:
        """Initialize consistent hash router."""
        self.pool = pool
        self._build_hash_ring()

    def _build_hash_ring(self) -> None:
        """Build consistent hash ring from proxies."""
        self.hash_ring: dict[str, Proxy] = {}
        self.sorted_hashes: list = []

        for proxy in self.pool.get_all_proxies():
            # Create multiple virtual nodes for better distribution
            for i in range(3):
                virtual_key = f"{proxy.id}:{i}"
                hash_value = self._hash(virtual_key)
                self.hash_ring[hash_value] = proxy
                self.sorted_hashes.append(hash_value)

        self.sorted_hashes.sort()

    @staticmethod
    def _hash(key: str) -> int:
        """Hash a key using SHA-256."""
        return int(hashlib.sha256(key.encode()).hexdigest(), 16)

    def get_proxy_for_request(self, request_id: str) -> Optional[Proxy]:
        """Get proxy for request using consistent hashing."""
        if not self.sorted_hashes:
            return None

        request_hash = self._hash(request_id)

        # Find first hash >= request_hash (wraps around if needed)
        for hash_value in self.sorted_hashes:
            if hash_value >= request_hash:
                return self.hash_ring[hash_value]

        # Wrap around to first
        return self.hash_ring[self.sorted_hashes[0]]

    def rebalance(self) -> None:
        """Rebuild hash ring after pool changes."""
        self._build_hash_ring()
        logger.debug("Rebalanced consistent hash ring")
