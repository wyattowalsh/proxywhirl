"""Session persistence strategy."""

from __future__ import annotations

import threading
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from uuid import UUID

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyPool,
    SelectionContext,
    Session,
    StrategyConfig,
)
from proxywhirl.strategies.base import RotationStrategy
from proxywhirl.strategies.round_robin import RoundRobinStrategy


class SessionManager:
    """Thread-safe session manager for sticky proxy assignments.

    Manages the mapping between session IDs and their assigned proxies,
    with automatic expiration and cleanup. All operations are thread-safe.

    Features:
    - Automatic TTL-based expiration
    - LRU eviction when max_sessions limit is reached
    - Periodic cleanup of expired sessions
    """

    def __init__(self, max_sessions: int = 10000, auto_cleanup_threshold: int = 100) -> None:
        """Initialize the session manager.

        Args:
            max_sessions: Maximum number of active sessions (default: 10000)
            auto_cleanup_threshold: Trigger cleanup after this many operations (default: 100)
        """
        self._sessions: OrderedDict[str, Session] = OrderedDict()
        self._lock = threading.RLock()
        self._max_sessions = max_sessions
        self._auto_cleanup_threshold = auto_cleanup_threshold
        self._operation_counter = 0

    def create_session(
        self,
        session_id: str,
        proxy: Proxy,
        timeout_seconds: int = 300,
    ) -> Session:
        """Create or update a session assignment.

        Args:
            session_id: Unique identifier for the session
            proxy: Proxy to assign to this session
            timeout_seconds: Session TTL in seconds (default 5 minutes)

        Returns:
            The created/updated Session object
        """
        with self._lock:
            # Auto-cleanup check
            self._maybe_auto_cleanup()

            # Check if we need to evict old sessions (LRU)
            if len(self._sessions) >= self._max_sessions:
                self._evict_lru_session()

            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(seconds=timeout_seconds)

            session = Session(
                session_id=session_id,
                proxy_id=str(proxy.id),
                created_at=now,
                expires_at=expires_at,
                last_used_at=now,
                request_count=0,
            )

            self._sessions[session_id] = session
            return session

    def get_session(self, session_id: str) -> Session | None:
        """Get an active session by ID.

        Args:
            session_id: The session ID to look up

        Returns:
            Session object if found and not expired, None otherwise
        """
        with self._lock:
            session = self._sessions.get(session_id)

            if session is None:
                return None

            # Check if expired
            if session.is_expired():
                del self._sessions[session_id]
                return None

            # Mark as recently used (move to end of OrderedDict)
            self._sessions.move_to_end(session_id)

            return session

    def touch_session(self, session_id: str) -> bool:
        """Update session last_used_at and increment request_count.

        Args:
            session_id: The session ID to touch

        Returns:
            True if session was touched, False if not found or expired
        """
        with self._lock:
            session = self.get_session(session_id)

            if session is None:
                return False

            session.touch()
            return True

    def remove_session(self, session_id: str) -> bool:
        """Remove a session from the manager.

        Args:
            session_id: The session ID to remove

        Returns:
            True if session was removed, False if not found
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def cleanup_expired(self) -> int:
        """Remove all expired sessions.

        Returns:
            Number of expired sessions removed
        """
        with self._lock:
            expired_ids = [sid for sid, session in self._sessions.items() if session.is_expired()]

            for sid in expired_ids:
                del self._sessions[sid]

            return len(expired_ids)

    def get_all_sessions(self) -> list[Session]:
        """Get all active (non-expired) sessions.

        Returns:
            List of active Session objects
        """
        with self._lock:
            # Filter out expired sessions
            active = []
            expired_ids = []

            for sid, session in self._sessions.items():
                if session.is_expired():
                    expired_ids.append(sid)
                else:
                    active.append(session)

            # Clean up expired
            for sid in expired_ids:
                del self._sessions[sid]

            return active

    def clear_all(self) -> None:
        """Remove all sessions."""
        with self._lock:
            self._sessions.clear()

    def _maybe_auto_cleanup(self) -> None:
        """Perform automatic cleanup if threshold is reached.

        This is called periodically to clean up expired sessions without
        requiring manual intervention. Thread-safe (assumes caller holds lock).
        """
        self._operation_counter += 1

        if self._operation_counter >= self._auto_cleanup_threshold:
            self._operation_counter = 0
            # Clean up expired sessions
            expired_count = self._cleanup_expired_unsafe()
            if expired_count > 0:
                from loguru import logger

                logger.debug(
                    f"Auto-cleanup removed {expired_count} expired sessions",
                    expired_count=expired_count,
                    total_sessions=len(self._sessions),
                )

    def _cleanup_expired_unsafe(self) -> int:
        """Internal cleanup method (assumes caller holds lock).

        Returns:
            Number of expired sessions removed
        """
        expired_ids = [sid for sid, session in self._sessions.items() if session.is_expired()]

        for sid in expired_ids:
            del self._sessions[sid]

        return len(expired_ids)

    def _evict_lru_session(self) -> None:
        """Evict the least recently used session (LRU eviction) in O(1) time.

        This is called when max_sessions limit is reached. Removes the session
        at the front of the OrderedDict (oldest/least recently used).
        Thread-safe (assumes caller holds lock).
        """
        if not self._sessions:
            return

        # Remove oldest (first) item in O(1) time
        lru_session_id, _ = self._sessions.popitem(last=False)

        from loguru import logger

        logger.debug(
            f"LRU eviction removed session {lru_session_id}",
            evicted_session_id=lru_session_id,
            total_sessions=len(self._sessions),
        )


class SessionPersistenceStrategy:
    """
    Session persistence strategy (sticky sessions).

    Maintains consistent proxy assignment for a given session ID across multiple
    requests. Ensures that all requests within a session use the same proxy unless
    the proxy becomes unavailable.

    Features:
    - Session-to-proxy binding with configurable TTL
    - Automatic failover when assigned proxy becomes unhealthy
    - Thread-safe session management
    - Session expiration and cleanup

    Thread Safety:
        Uses SessionManager which has internal locking for thread-safe operations.

    Success Criteria:
        SC-005: 99.9% same-proxy guarantee for session requests

    Performance:
        O(1) session lookup, <1ms overhead for session management
    """

    def __init__(self, max_sessions: int = 10000, auto_cleanup_threshold: int = 100) -> None:
        """Initialize session persistence strategy.

        Args:
            max_sessions: Maximum number of active sessions before LRU eviction (default: 10000)
            auto_cleanup_threshold: Number of operations between auto-cleanups (default: 100)
        """
        self._session_manager = SessionManager(
            max_sessions=max_sessions, auto_cleanup_threshold=auto_cleanup_threshold
        )
        self._fallback_strategy: RotationStrategy = RoundRobinStrategy()
        self._session_timeout_seconds: int = 3600  # 1 hour default
        self.config: StrategyConfig | None = None

    def configure(self, config: StrategyConfig) -> None:
        """
        Configure session persistence parameters.

        Args:
            config: Strategy configuration with session_stickiness_duration_seconds
        """
        # Store config for later use
        self.config = config

        # Use session_stickiness_duration_seconds from config
        if config.session_stickiness_duration_seconds is not None:
            self._session_timeout_seconds = config.session_stickiness_duration_seconds

        # Optionally configure fallback strategy
        if hasattr(config, "fallback_strategy") and config.fallback_strategy:
            from proxywhirl.strategies.registry import resolve_builtin_strategy

            self._fallback_strategy = resolve_builtin_strategy(config.fallback_strategy)

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """
        Validate that pool has necessary metadata for strategy.

        Session persistence doesn't require specific proxy metadata.

        Args:
            pool: The proxy pool to validate

        Returns:
            Always True - session persistence works with any pool
        """
        return True

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        """
        Select a proxy with session persistence.

        If session_id exists and proxy is healthy, returns same proxy.
        If session_id is new or assigned proxy is unhealthy, assigns new proxy.

        Args:
            pool: The proxy pool to select from
            context: Selection context with session_id (required)

        Returns:
            Healthy proxy assigned to the session

        Raises:
            ValueError: If context is None or session_id is missing
            ProxyPoolEmptyError: If no healthy proxies available
        """
        if context is None or context.session_id is None:
            raise ValueError("SessionPersistenceStrategy requires SelectionContext with session_id")

        session_id = context.session_id
        failed_proxy_ids = set(context.failed_proxy_ids)

        # Check for existing session and attempt to reuse with single lookup
        session = self._session_manager.get_session(session_id)

        if session is not None:
            # Session exists - try to use assigned proxy when the persisted ID is valid.
            try:
                proxy_uuid = UUID(session.proxy_id)
            except (ValueError, TypeError, AttributeError):
                proxy_uuid = None

            if proxy_uuid is not None:
                assigned_proxy = pool.get_proxy_by_id(proxy_uuid)

                # Check if proxy is still healthy or untested (UNKNOWN is acceptable)
                if (
                    assigned_proxy is not None
                    and assigned_proxy.health_status
                    in (
                        HealthStatus.HEALTHY,
                        HealthStatus.UNKNOWN,
                        HealthStatus.DEGRADED,
                    )
                    and str(assigned_proxy.id) not in failed_proxy_ids
                ):
                    # Update session last_used with cached session object
                    # (single lookup, session touch happens exactly once)
                    session.touch()
                    # Mark proxy as in-use
                    assigned_proxy.start_request()
                    return assigned_proxy
                # Proxy unhealthy - need to failover (fall through to new selection)

        # No valid session or failover needed - select new proxy
        healthy_proxies = pool.get_healthy_proxies()

        # Filter out failed proxies from context
        if failed_proxy_ids:
            healthy_proxies = [p for p in healthy_proxies if str(p.id) not in failed_proxy_ids]

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available for session")

        # Use fallback strategy to select new proxy from filtered list
        # Create temp pool with only healthy proxies
        temp_pool = ProxyPool(name="temp", proxies=healthy_proxies)
        new_proxy = self._fallback_strategy.select(temp_pool)

        # Create or update session with new proxy
        self._session_manager.create_session(
            session_id=session_id, proxy=new_proxy, timeout_seconds=self._session_timeout_seconds
        )

        return new_proxy

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record the result of a request through a proxy.

        Updates proxy completion statistics via Proxy.complete_request().

        Args:
            proxy: The proxy that handled the request
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        # Pass strategy's alpha to avoid mutating proxy state
        alpha = (
            self.config.ema_alpha if hasattr(self, "config") and self.config is not None else None
        )
        proxy.complete_request(success=success, response_time_ms=response_time_ms, alpha=alpha)

    def close_session(self, session_id: str) -> None:
        """
        Explicitly close a session.

        Args:
            session_id: The session ID to close
        """
        self._session_manager.remove_session(session_id)

    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions.

        Returns:
            Number of sessions removed
        """
        return self._session_manager.cleanup_expired()

    def get_session_stats(self) -> dict[str, int]:
        """
        Get session statistics.

        Returns:
            dict[str, int]: Session statistics including total_sessions, max_sessions,
            and auto_cleanup_threshold.
        """
        return {
            "total_sessions": len(self._session_manager._sessions),
            "max_sessions": self._session_manager._max_sessions,
            "auto_cleanup_threshold": self._session_manager._auto_cleanup_threshold,
        }
