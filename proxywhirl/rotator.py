"""proxywhirl/rotator.py -- proxy rotation strategies"""

import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from proxywhirl.models import (
    ErrorHandlingPolicy,
    Proxy,
    ProxyStatus,
    RotationStrategy,
    SessionProxy,
    ValidationErrorType,
)


class ProxyRotator:
    """Handle proxy rotation strategies with health tracking and cooldowns."""

    # Attribute type declarations for strict typing
    _health_scores: dict[str, float]
    _use_counts: dict[str, int]
    _cooldowns: dict[str, datetime]
    _cooldown_period: timedelta
    _sessions: Dict[str, SessionProxy]  # Session ID -> SessionProxy mapping

    # Error handling policy to cooldown duration mapping (seconds)
    ERROR_POLICY_DURATIONS = {
        ErrorHandlingPolicy.COOLDOWN_SHORT: 15,  # 15 seconds for minor issues
        ErrorHandlingPolicy.COOLDOWN_MEDIUM: 300,  # 5 minutes for rate limiting
        ErrorHandlingPolicy.COOLDOWN_LONG: 1800,  # 30 minutes for severe issues
    }

    # Error type to handling policy mapping
    ERROR_TYPE_POLICIES = {
        ValidationErrorType.TIMEOUT: ErrorHandlingPolicy.COOLDOWN_SHORT,
        ValidationErrorType.CONNECTION_ERROR: ErrorHandlingPolicy.REMOVE_IMMEDIATELY,
        ValidationErrorType.AUTHENTICATION_ERROR: ErrorHandlingPolicy.REMOVE_IMMEDIATELY,
        ValidationErrorType.PROXY_ERROR: ErrorHandlingPolicy.REMOVE_IMMEDIATELY,
        ValidationErrorType.HTTP_ERROR: ErrorHandlingPolicy.COOLDOWN_SHORT,
        ValidationErrorType.SSL_ERROR: ErrorHandlingPolicy.COOLDOWN_MEDIUM,
        ValidationErrorType.RATE_LIMITED: ErrorHandlingPolicy.COOLDOWN_MEDIUM,
        ValidationErrorType.CIRCUIT_BREAKER_OPEN: ErrorHandlingPolicy.COOLDOWN_LONG,
        ValidationErrorType.UNKNOWN: ErrorHandlingPolicy.COOLDOWN_SHORT,
    }

    def __init__(
        self,
        strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN,
        default_session_ttl: int = 1800,  # 30 minutes default
    ):
        # Validate strategy input early; tests expect errors for invalid values
        if not isinstance(strategy, RotationStrategy):
            raise ValueError("Invalid rotation strategy")
        self.strategy = strategy
        self.default_session_ttl = default_session_ttl
        self._current_index = 0
        # Internal tracking
        self._health_scores = {}
        self._use_counts = {}
        self._cooldowns = {}
        self._cooldown_period = timedelta(seconds=15)
        # Session management
        self._sessions: Dict[str, SessionProxy] = {}

    def get_proxy(self, proxies: List[Proxy]) -> Optional[Proxy]:
        """Get next proxy based on rotation strategy."""
        if not proxies:
            return None

        # Filter out proxies that are not available (in cooldown or blacklisted)
        available: List[Proxy] = []
        for p in proxies:
            # Use the new error state availability check
            if p.error_state.is_available() and p.status != ProxyStatus.BLACKLISTED:
                available.append(p)

        # If no proxies are available, allow emergency access to best ones
        if not available:
            # Find proxies with shortest remaining cooldown
            available = sorted(
                proxies,
                key=lambda p: p.error_state.cooldown_until
                or datetime.min.replace(tzinfo=timezone.utc),
            )[:5]
            if not available:
                available = proxies

        if self.strategy == RotationStrategy.ROUND_ROBIN:
            chosen = self._round_robin(available)
        elif self.strategy == RotationStrategy.RANDOM:
            chosen = self._random_selection(available)
        elif self.strategy == RotationStrategy.WEIGHTED:
            chosen = self._weighted_selection(available)
        elif self.strategy == RotationStrategy.HEALTH_BASED:
            chosen = self._health_based_selection(available)
        elif self.strategy == RotationStrategy.LEAST_USED:
            chosen = self._least_used_selection(available)
        else:
            chosen = self._round_robin(available)

        # Track usage
        if chosen:
            key = f"{chosen.host}:{chosen.port}"
            self._use_counts[key] = self._use_counts.get(key, 0) + 1
        return chosen

    def _round_robin(self, proxies: List[Proxy]) -> Proxy:
        """Round robin selection."""
        proxy = proxies[self._current_index % len(proxies)]
        self._current_index += 1
        return proxy

    def _random_selection(self, proxies: List[Proxy]) -> Proxy:
        """Random selection."""
        return random.choice(proxies)

    def _weighted_selection(self, proxies: List[Proxy]) -> Proxy:
        """Weighted selection based on response time."""
        # Weight by inverse response time (faster = higher weight)
        weights: List[float] = []
        for proxy in proxies:
            if proxy.response_time and proxy.response_time > 0:
                weight = 1.0 / proxy.response_time
            else:
                weight = 1.0  # Default weight for unknown response times
            weights.append(weight)
        return random.choices(proxies, weights=weights)[0]

    def _health_based_selection(self, proxies: List[Proxy]) -> Proxy:
        """Health-based selection."""
        # Filter out unhealthy proxies and prefer healthy ones
        healthy_proxies: List[tuple[Proxy, float]] = []
        for proxy in proxies:
            key = f"{proxy.host}:{proxy.port}"
            health_score = self._health_scores.get(key, 0.5)
            # Consider proxies with health score > 0.3 as usable
            if health_score > 0.3:
                healthy_proxies.append((proxy, health_score))
        if not healthy_proxies:
            # Fallback to random if no healthy proxies
            return self._random_selection(proxies)
        # Weight by health score
        proxies_list, scores = zip(*healthy_proxies)
        return random.choices(list(proxies_list), weights=list(scores))[0]

    def _least_used_selection(self, proxies: List[Proxy]) -> Proxy:
        """
        Pick proxy with the fewest selections so far; tie-break by
        response_time then random.
        """
        if not proxies:
            return self._random_selection(proxies)
        # Build list with counts
        scored: List[tuple[int, float, float, Proxy]] = []
        for p in proxies:
            key = f"{p.host}:{p.port}"
            cnt = self._use_counts.get(key, 0)
            rt = p.response_time if p.response_time is not None else float("inf")
            scored.append((cnt, rt, random.random(), p))
        scored.sort(key=lambda x: (x[0], x[1], x[2]))
        return scored[0][3]

    def update_health_score(
        self,
        proxy: Proxy,
        success: bool,
        response_time: Optional[float] = None,
        error_type: Optional[ValidationErrorType] = None,
        error_message: Optional[str] = None,
        http_status: Optional[int] = None,
    ) -> None:
        """Update health score for a proxy with enhanced error handling."""
        key = f"{proxy.host}:{proxy.port}"
        current_score = self._health_scores.get(key, 0.5)

        if success:
            # Record success in error state
            proxy.error_state.add_success()

            # Increase health score for successful requests
            new_score = min(1.0, current_score + 0.1)

            # Clear any cooldown on success
            proxy.error_state.clear_cooldown()

        else:
            # Record error in error state
            if error_type:
                proxy.error_state.add_error(error_type, error_message, http_status)

            # Decrease score for failed requests
            new_score = max(0.0, current_score - 0.2)

            # Apply differentiated cooldown based on error type
            if error_type and error_type in self.ERROR_TYPE_POLICIES:
                policy = self.ERROR_TYPE_POLICIES[error_type]

                if policy == ErrorHandlingPolicy.REMOVE_IMMEDIATELY:
                    # Mark for removal (caller should handle this)
                    proxy.status = ProxyStatus.INACTIVE
                elif policy == ErrorHandlingPolicy.BLACKLIST:
                    # Permanently blacklist
                    proxy.status = ProxyStatus.BLACKLISTED
                    proxy.blacklist_reason = f"Blacklisted due to {error_type.value}"
                elif policy in self.ERROR_POLICY_DURATIONS:
                    # Apply cooldown based on policy
                    duration = self.ERROR_POLICY_DURATIONS[policy]
                    proxy.error_state.set_cooldown(policy, duration)

        self._health_scores[key] = new_score

    # === Session Management Methods ===

    def get_proxy_for_session(
        self,
        session_id: str,
        proxies: List[Proxy],
        target_id: Optional[str] = None,
        custom_ttl: Optional[int] = None,
    ) -> Optional[Proxy]:
        """
        Get a proxy for a specific session with stickiness.

        If the session already has a healthy proxy assigned, returns that proxy.
        Otherwise, assigns a new proxy using the configured rotation strategy.

        Parameters
        ----------
        session_id : str
            Unique identifier for the session.
        proxies : List[Proxy]
            Available proxies to choose from.
        target_id : str, optional
            Target ID for target-specific session management.
        custom_ttl : int, optional
            Custom TTL in seconds for this session. Uses default_session_ttl if None.

        Returns
        -------
        Proxy or None
            Assigned proxy for the session or None if no proxies available.

        Notes
        -----
        - Sessions are automatically cleaned up when expired
        - Unhealthy proxy assignments are replaced with new selections
        - Integrates with existing rotation strategies and error handling
        """
        if not proxies:
            return None

        # Clean up expired sessions first
        self._cleanup_expired_sessions()

        # Check if session exists and is still valid
        if session_id in self._sessions:
            session_proxy = self._sessions[session_id]

            # Verify session hasn't expired and proxy is still healthy
            if not session_proxy.should_reassign:
                # Ensure the assigned proxy is still in the available proxy list
                proxy_key = f"{session_proxy.proxy.host}:{session_proxy.proxy.port}"
                available_keys = {f"{p.host}:{p.port}" for p in proxies}

                if proxy_key in available_keys:
                    # Update usage tracking
                    self._use_counts[proxy_key] = self._use_counts.get(proxy_key, 0) + 1
                    return session_proxy.proxy
                else:
                    # Proxy no longer available, need to reassign
                    del self._sessions[session_id]

        # Need to assign a new proxy for this session
        new_proxy = self.get_proxy(proxies)
        if new_proxy is None:
            return None

        # Create session mapping with TTL
        ttl_seconds = custom_ttl or self.default_session_ttl
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

        session_proxy = SessionProxy(
            session_id=session_id, proxy=new_proxy, expires_at=expires_at, target_id=target_id
        )

        self._sessions[session_id] = session_proxy
        return new_proxy

    def extend_session_ttl(self, session_id: str, additional_seconds: int) -> bool:
        """
        Extend TTL for an existing session.

        Parameters
        ----------
        session_id : str
            Session identifier to extend.
        additional_seconds : int
            Seconds to add to current expiration time.

        Returns
        -------
        bool
            True if session was found and extended, False otherwise.
        """
        if session_id in self._sessions:
            self._sessions[session_id].extend_ttl(additional_seconds)
            return True
        return False

    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a specific session, forcing reassignment on next request.

        Parameters
        ----------
        session_id : str
            Session identifier to invalidate.

        Returns
        -------
        bool
            True if session was found and removed, False otherwise.
        """
        return self._sessions.pop(session_id, None) is not None

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific session.

        Parameters
        ----------
        session_id : str
            Session identifier to query.

        Returns
        -------
        dict or None
            Session information or None if session doesn't exist.
        """
        if session_id not in self._sessions:
            return None

        session = self._sessions[session_id]
        return {
            "session_id": session.session_id,
            "proxy": f"{session.proxy.host}:{session.proxy.port}",
            "assigned_at": session.assigned_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "ttl_remaining": session.ttl_remaining,
            "target_id": session.target_id,
            "is_proxy_healthy": session.is_proxy_healthy,
            "should_reassign": session.should_reassign,
        }

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Get information about all active sessions.

        Returns
        -------
        List[dict]
            List of session information dictionaries.
        """
        self._cleanup_expired_sessions()
        return [
            info
            for info in (self.get_session_info(sid) for sid in self._sessions.keys())
            if info is not None
        ]

    def _cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions from storage.

        Returns
        -------
        int
            Number of sessions cleaned up.
        """
        expired_sessions = [
            session_id for session_id, session in self._sessions.items() if session.is_expired
        ]

        for session_id in expired_sessions:
            del self._sessions[session_id]

        return len(expired_sessions)

    def clear_all_sessions(self) -> int:
        """
        Clear all session mappings.

        Returns
        -------
        int
            Number of sessions cleared.
        """
        count = len(self._sessions)
        self._sessions.clear()
        return count
