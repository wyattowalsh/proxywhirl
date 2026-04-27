"""Session affinity implementation for sticky sessions."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger


@dataclass
class SessionAffinity:
    """Session affinity mapping and TTL."""

    client_id: str
    proxy_id: str
    created_at: float = field(default_factory=time.time)
    ttl_seconds: int = 3600
    last_used: float = field(default_factory=time.time)
    request_count: int = 0

    def is_expired(self) -> bool:
        """Check if affinity has expired."""
        return time.time() - self.created_at > self.ttl_seconds

    def touch(self) -> None:
        """Update last used time."""
        self.last_used = time.time()
        self.request_count += 1


class SessionAffinityManager:
    """
    Manage session affinity (sticky sessions).

    Maps client_id -> proxy_id to ensure requests from same client
    use the same proxy for session persistence.
    """

    def __init__(self, default_ttl_seconds: int = 3600):
        """
        Initialize session affinity manager.

        Args:
            default_ttl_seconds: Default TTL for affinities
        """
        self.default_ttl_seconds = default_ttl_seconds
        self.affinities: dict[str, SessionAffinity] = {}

    def set_affinity(
        self, client_id: str, proxy_id: str, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set session affinity for a client.

        Args:
            client_id: Client identifier
            proxy_id: Proxy to bind to this client
            ttl_seconds: Optional custom TTL
        """
        ttl = ttl_seconds or self.default_ttl_seconds
        self.affinities[client_id] = SessionAffinity(
            client_id=client_id,
            proxy_id=proxy_id,
            ttl_seconds=ttl,
        )
        logger.debug(f"Set session affinity: {client_id} -> {proxy_id} (TTL: {ttl}s)")

    def get_affinity(self, client_id: str) -> Optional[str]:
        """
        Get affinity for a client.

        Args:
            client_id: Client identifier

        Returns:
            Proxy ID if affinity exists and not expired, None otherwise
        """
        if client_id not in self.affinities:
            return None

        affinity = self.affinities[client_id]

        if affinity.is_expired():
            del self.affinities[client_id]
            logger.debug(f"Session affinity expired: {client_id}")
            return None

        affinity.touch()
        return affinity.proxy_id

    def has_affinity(self, client_id: str) -> bool:
        """
        Check if client has active affinity.

        Args:
            client_id: Client identifier

        Returns:
            True if active affinity exists
        """
        return self.get_affinity(client_id) is not None

    def remove_affinity(self, client_id: str) -> None:
        """
        Remove affinity for a client.

        Args:
            client_id: Client identifier
        """
        if client_id in self.affinities:
            del self.affinities[client_id]
            logger.debug(f"Removed session affinity: {client_id}")

    def cleanup_expired(self) -> int:
        """
        Remove all expired affinities.

        Returns:
            Number of affinities removed
        """
        expired_clients = [
            client_id for client_id, affinity in self.affinities.items() if affinity.is_expired()
        ]

        for client_id in expired_clients:
            del self.affinities[client_id]

        if expired_clients:
            logger.debug(f"Cleaned up {len(expired_clients)} expired affinities")

        return len(expired_clients)

    def get_stats(self) -> dict[str, int | dict]:
        """
        Get session affinity statistics.

        Returns:
            Dictionary with stats
        """
        active_count = 0
        total_requests = 0

        for affinity in self.affinities.values():
            if not affinity.is_expired():
                active_count += 1
                total_requests += affinity.request_count

        return {
            "active_affinities": active_count,
            "total_affinities": len(self.affinities),
            "total_requests_via_affinity": total_requests,
        }

    def get_affinity_details(self, client_id: str) -> Optional[dict]:
        """
        Get detailed information about a client's affinity.

        Args:
            client_id: Client identifier

        Returns:
            Dictionary with affinity details or None
        """
        if client_id not in self.affinities:
            return None

        affinity = self.affinities[client_id]

        if affinity.is_expired():
            del self.affinities[client_id]
            return None

        return {
            "client_id": affinity.client_id,
            "proxy_id": affinity.proxy_id,
            "created_at": affinity.created_at,
            "last_used": affinity.last_used,
            "request_count": affinity.request_count,
            "ttl_seconds": affinity.ttl_seconds,
            "age_seconds": time.time() - affinity.created_at,
            "seconds_until_expiry": affinity.ttl_seconds - (time.time() - affinity.created_at),
        }
