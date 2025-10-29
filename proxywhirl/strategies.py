"""
Rotation strategies for proxy selection.
"""

import random
import threading
from datetime import datetime, timedelta, timezone
from typing import Optional, Protocol, runtime_checkable

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import Proxy, ProxyPool, Session, SelectionContext, StrategyConfig


@runtime_checkable
class RotationStrategy(Protocol):
    """Protocol defining interface for proxy rotation strategies."""

    def select(self, pool: ProxyPool) -> Proxy:
        """
        Select a proxy from the pool based on strategy logic.

        Args:
            pool: The proxy pool to select from

        Returns:
            Selected proxy

        Raises:
            ProxyPoolEmptyError: If no suitable proxy is available
        """
        ...

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record the result of using a proxy.

        Args:
            proxy: The proxy that was used
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        ...


class RoundRobinStrategy:
    """
    Round-robin proxy selection strategy with SelectionContext support.

    Selects proxies in sequential order, wrapping around to the first
    proxy after reaching the end of the list. Only selects healthy proxies.
    Supports filtering based on SelectionContext (e.g., failed_proxy_ids).
    """

    def __init__(self) -> None:
        """Initialize round-robin strategy."""
        self._current_index: int = 0
        self.config: Optional[StrategyConfig] = None

    def select(self, pool: ProxyPool, context: Optional[SelectionContext] = None) -> Proxy:
        """
        Select next proxy in round-robin order.

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

        Returns:
            Next healthy proxy in rotation

        Raises:
            ProxyPoolEmptyError: If no healthy proxies are available
        """
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available in pool")

        # Filter out failed proxies if context provided
        if context and context.failed_proxy_ids:
            failed_ids = set(context.failed_proxy_ids)
            healthy_proxies = [
                p for p in healthy_proxies
                if str(p.id) not in failed_ids
            ]
            
            if not healthy_proxies:
                raise ProxyPoolEmptyError("No healthy proxies available after filtering failed proxies")

        # Select proxy at current index (with wraparound)
        proxy = healthy_proxies[self._current_index % len(healthy_proxies)]

        # Increment index for next selection
        self._current_index = (self._current_index + 1) % len(healthy_proxies)

        # Update proxy metadata to track request start
        proxy.start_request()

        return proxy

    def configure(self, config: StrategyConfig) -> None:
        """
        Configure the strategy with custom settings.

        Args:
            config: Strategy configuration object
        """
        self.config = config

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """
        Validate that pool has required metadata for this strategy.

        Round-robin doesn't require any special metadata, so always returns True.

        Args:
            pool: The proxy pool to validate

        Returns:
            Always True for round-robin
        """
        return True

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record the result of using a proxy.

        Updates proxy statistics based on request outcome and completes the request tracking.

        Args:
            proxy: The proxy that was used
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        # Use complete_request which handles both metrics update and success/failure recording
        proxy.complete_request(success=success, response_time_ms=response_time_ms)


class RandomStrategy:
    """
    Random proxy selection strategy with SelectionContext support.

    Randomly selects a proxy from the pool of healthy proxies.
    Provides unpredictable rotation for scenarios where sequential
    patterns should be avoided.
    """

    def __init__(self) -> None:
        """Initialize random strategy."""
        self.config: Optional[StrategyConfig] = None

    def select(self, pool: ProxyPool, context: Optional[SelectionContext] = None) -> Proxy:
        """
        Select a random healthy proxy.

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

        Returns:
            Randomly selected healthy proxy

        Raises:
            ProxyPoolEmptyError: If no healthy proxies are available
        """
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available in pool")

        # Filter out failed proxies if context provided
        if context and context.failed_proxy_ids:
            failed_ids = set(context.failed_proxy_ids)
            healthy_proxies = [
                p for p in healthy_proxies
                if str(p.id) not in failed_ids
            ]
            
            if not healthy_proxies:
                raise ProxyPoolEmptyError("No healthy proxies available after filtering failed proxies")

        proxy = random.choice(healthy_proxies)
        
        # Update proxy metadata to track request start
        proxy.start_request()
        
        return proxy

    def configure(self, config: StrategyConfig) -> None:
        """Configure the strategy with custom settings."""
        self.config = config

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """Random selection doesn't require metadata validation."""
        return True

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """Record the result of using a proxy."""
        proxy.complete_request(success=success, response_time_ms=response_time_ms)


class WeightedStrategy:
    """
    Weighted proxy selection strategy.

    Selects proxies based on their success rates, giving preference
    to proxies with higher success rates. Uses weighted random selection
    where weights are derived from success_rate.
    """

    def select(self, pool: ProxyPool) -> Proxy:
        """
        Select a proxy weighted by success rate.

        Args:
            pool: The proxy pool to select from

        Returns:
            Weighted-random selected healthy proxy

        Raises:
            ProxyPoolEmptyError: If no healthy proxies are available
        """
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available in pool")

        # Calculate weights based on success rates
        # Add small base weight to give all proxies a chance
        weights = [max(proxy.success_rate, 0.1) for proxy in healthy_proxies]

        # Use random.choices for weighted selection
        selected = random.choices(healthy_proxies, weights=weights, k=1)[0]
        return selected

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """Record the result of using a proxy."""
        if success:
            proxy.record_success(response_time_ms)
        else:
            proxy.record_failure()


class LeastUsedStrategy:
    """
    Least-used proxy selection strategy with SelectionContext support.

    Selects the proxy with the fewest started requests, helping to
    balance load across all available proxies. Uses requests_started
    counter to determine least-used proxy.
    """

    def __init__(self) -> None:
        """Initialize least-used strategy."""
        self.config: Optional[StrategyConfig] = None

    def select(self, pool: ProxyPool, context: Optional[SelectionContext] = None) -> Proxy:
        """
        Select the least-used healthy proxy.

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

        Returns:
            Healthy proxy with fewest started requests

        Raises:
            ProxyPoolEmptyError: If no healthy proxies are available
        """
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available in pool")

        # Filter out failed proxies if context provided
        if context and context.failed_proxy_ids:
            failed_ids = set(context.failed_proxy_ids)
            healthy_proxies = [
                p for p in healthy_proxies
                if str(p.id) not in failed_ids
            ]
            
            if not healthy_proxies:
                raise ProxyPoolEmptyError("No healthy proxies available after filtering failed proxies")

        # Select proxy with minimum requests_started (new comprehensive tracking)
        proxy = min(healthy_proxies, key=lambda p: p.requests_started)
        
        # Update proxy metadata to track request start
        proxy.start_request()
        
        return proxy

    def configure(self, config: StrategyConfig) -> None:
        """Configure the strategy with custom settings."""
        self.config = config

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """
        Validate that proxies have request tracking metadata.

        Args:
            pool: The proxy pool to validate

        Returns:
            True if all proxies have requests_started field
        """
        # All Proxy objects now have requests_started field by default
        return True

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """Record the result of using a proxy."""
        proxy.complete_request(success=success, response_time_ms=response_time_ms)


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================


class SessionManager:
    """Thread-safe session manager for sticky proxy assignments.
    
    Manages the mapping between session IDs and their assigned proxies,
    with automatic expiration and cleanup. All operations are thread-safe.
    """
    
    def __init__(self) -> None:
        """Initialize the session manager."""
        self._sessions: dict[str, Session] = {}
        self._lock = threading.RLock()
    
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
    
    def get_session(self, session_id: str) -> Optional[Session]:
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
            expired_ids = [
                sid for sid, session in self._sessions.items()
                if session.is_expired()
            ]
            
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
