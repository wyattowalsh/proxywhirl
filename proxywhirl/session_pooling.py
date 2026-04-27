"""Session pooling and reuse management."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger


@dataclass
class PooledSession:
    """A pooled session instance."""

    session_id: str
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    usage_count: int = 0
    max_age_seconds: int = 3600
    idle_timeout_seconds: int = 300

    def is_expired(self) -> bool:
        """Check if session has exceeded max age."""
        return time.time() - self.created_at > self.max_age_seconds

    def is_idle(self) -> bool:
        """Check if session has been idle too long."""
        return time.time() - self.last_used > self.idle_timeout_seconds

    def is_stale(self) -> bool:
        """Check if session is expired or idle."""
        return self.is_expired() or self.is_idle()

    def touch(self) -> None:
        """Update last used time and increment usage count."""
        self.last_used = time.time()
        self.usage_count += 1

    def age_seconds(self) -> float:
        """Get age of session in seconds."""
        return time.time() - self.created_at

    def idle_seconds(self) -> float:
        """Get idle time in seconds."""
        return time.time() - self.last_used


class SessionPool:
    """
    Manage a pool of reusable sessions.

    Allows sessions to be:
    - Created and reused (reduce overhead)
    - Automatically cleaned up (expired/idle)
    - Tracked with metrics
    """

    def __init__(
        self,
        max_pool_size: int = 100,
        max_session_age_seconds: int = 3600,
        idle_timeout_seconds: int = 300,
    ):
        """
        Initialize session pool.

        Args:
            max_pool_size: Maximum sessions in pool
            max_session_age_seconds: Max age before session expires
            idle_timeout_seconds: Idle timeout before session expires
        """
        self.max_pool_size = max_pool_size
        self.max_session_age_seconds = max_session_age_seconds
        self.idle_timeout_seconds = idle_timeout_seconds
        self.sessions: dict[str, PooledSession] = {}
        self.available_sessions: list[str] = []
        self.in_use_sessions: set[str] = set()

    def acquire_session(self, session_id: Optional[str] = None) -> str:
        """
        Acquire a session from the pool.

        Args:
            session_id: Optional specific session ID to acquire

        Returns:
            Session ID
        """
        # Try to reuse existing session
        if session_id and session_id in self.available_sessions:
            if not self.sessions[session_id].is_stale():
                self.available_sessions.remove(session_id)
                self.in_use_sessions.add(session_id)
                self.sessions[session_id].touch()
                logger.debug(f"Reused session: {session_id}")
                return session_id

        # Clean up stale sessions
        self.cleanup_stale()

        # Reuse least-used available session if below limit
        if self.available_sessions:
            reused_id = self.available_sessions.pop(0)
            self.in_use_sessions.add(reused_id)
            self.sessions[reused_id].touch()
            logger.debug(f"Reused session: {reused_id}")
            return reused_id

        # Create new session if pool not full
        if len(self.sessions) < self.max_pool_size:
            new_id = f"sess_{int(time.time() * 1000)}"
            self.sessions[new_id] = PooledSession(
                session_id=new_id,
                max_age_seconds=self.max_session_age_seconds,
                idle_timeout_seconds=self.idle_timeout_seconds,
            )
            self.in_use_sessions.add(new_id)
            logger.debug(f"Created session: {new_id}")
            return new_id

        # Pool full, reuse oldest
        oldest_id = min(
            self.available_sessions,
            key=lambda sid: self.sessions[sid].last_used,
            default=None,
        )
        if oldest_id:
            self.available_sessions.remove(oldest_id)
            self.in_use_sessions.add(oldest_id)
            self.sessions[oldest_id].touch()
            logger.debug(f"Reused (pool full) session: {oldest_id}")
            return oldest_id

        raise RuntimeError("Unable to acquire session")

    def release_session(self, session_id: str) -> None:
        """
        Release a session back to the pool.

        Args:
            session_id: Session ID to release
        """
        if session_id in self.in_use_sessions:
            self.in_use_sessions.remove(session_id)
            if session_id not in self.available_sessions:
                self.available_sessions.append(session_id)
            logger.debug(f"Released session: {session_id}")

    def invalidate_session(self, session_id: str) -> None:
        """
        Invalidate and remove a session.

        Args:
            session_id: Session ID to invalidate
        """
        if session_id in self.sessions:
            del self.sessions[session_id]

        if session_id in self.available_sessions:
            self.available_sessions.remove(session_id)

        if session_id in self.in_use_sessions:
            self.in_use_sessions.remove(session_id)

        logger.debug(f"Invalidated session: {session_id}")

    def cleanup_stale(self) -> int:
        """
        Remove all stale sessions.

        Returns:
            Number of sessions removed
        """
        stale_sessions = [sid for sid, sess in self.sessions.items() if sess.is_stale()]

        for sid in stale_sessions:
            self.invalidate_session(sid)

        if stale_sessions:
            logger.debug(f"Cleaned up {len(stale_sessions)} stale sessions")

        return len(stale_sessions)

    def get_stats(self) -> dict[str, int | float]:
        """
        Get session pool statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "total_sessions": len(self.sessions),
            "available_sessions": len(self.available_sessions),
            "in_use_sessions": len(self.in_use_sessions),
            "pool_utilization_percent": (
                len(self.in_use_sessions) / self.max_pool_size * 100 if self.max_pool_size else 0
            ),
        }

    def get_session_info(self, session_id: str) -> Optional[dict]:
        """
        Get information about a session.

        Args:
            session_id: Session ID

        Returns:
            Dictionary with session info or None
        """
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        return {
            "session_id": session_id,
            "created_at": session.created_at,
            "last_used": session.last_used,
            "age_seconds": session.age_seconds(),
            "idle_seconds": session.idle_seconds(),
            "usage_count": session.usage_count,
            "is_stale": session.is_stale(),
            "in_use": session_id in self.in_use_sessions,
        }
