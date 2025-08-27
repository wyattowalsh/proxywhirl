"""proxywhirl/rotator.py -- proxy rotation strategies"""

import asyncio
import hashlib
import random
import time
from bisect import bisect_left
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.models import (
    CircuitState,
    ErrorHandlingPolicy,
    Proxy,
    ProxyStatus,
    RotationStrategy,
    SessionProxy,
    ValidationErrorType,
)

# === Circuit Breaker Components ===


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

    failure_threshold: int = 5  # Consecutive failures to trip breaker
    recovery_timeout: timedelta = timedelta(seconds=60)  # Time before attempting recovery
    success_threshold: int = 3  # Successes needed in half-open to close
    timeout_threshold: timedelta = timedelta(seconds=30)  # Request timeout


@dataclass
class CircuitBreakerState:
    """Internal state tracking for circuit breakers."""

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""


# === ML Feature Engineering ===


@dataclass
class MLFeatures:
    """Feature set for ML-based proxy selection."""

    success_rate: float = 0.0
    avg_response_time: float = 0.0
    total_requests: int = 0
    consecutive_failures: int = 0
    time_since_last_check: float = 0.0
    anonymity_score: float = 0.0
    country_reliability: float = 0.0
    hour_of_day: int = 0
    day_of_week: int = 0


@dataclass
class GeoLocation:
    """Geographic location data for proxy routing."""

    latitude: float
    longitude: float
    country: str
    region: str


# === Metrics Components ===


@dataclass
class RotationMetrics:
    """Performance metrics for rotation operations."""

    selections_total: int = 0
    selections_success: int = 0
    avg_selection_time: float = 0.0
    circuit_breaker_trips: int = 0
    ml_predictions_made: int = 0
    geo_selections: int = 0


# === Prometheus Metrics Setup ===


try:
    from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

    # Create mock classes for when prometheus is not available
    class CollectorRegistry:
        def __init__(self):
            pass

    class Counter:
        def __init__(self, *args, **kwargs):
            pass

        def inc(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

    class Gauge:
        def __init__(self, *args, **kwargs):
            pass

        def set(self, *args, **kwargs):
            pass

        def inc(self, *args, **kwargs):
            pass

        def dec(self, *args, **kwargs):
            pass

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass

        def observe(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self


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
        # Enhanced strategies require async handling in proxywhirl.py
        elif self.strategy in [
            RotationStrategy.ASYNC_ROUND_ROBIN,
            RotationStrategy.CIRCUIT_BREAKER,
            RotationStrategy.METRICS_AWARE,
            RotationStrategy.ML_ADAPTIVE,
            RotationStrategy.CONSISTENT_HASH,
            RotationStrategy.GEO_AWARE,
        ]:
            # Fallback to round robin for sync calls
            chosen = self._round_robin(available)
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

    def create_session_proxy(self, session_id: str, proxy: Proxy, target_id: Optional[str] = None) -> SessionProxy:
        """Create a session proxy mapping."""
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.default_session_ttl)
        session_proxy = SessionProxy(
            session_id=session_id,
            proxy=proxy,
            expires_at=expires_at,
            target_id=target_id
        )
        self._sessions[session_id] = session_proxy
        return session_proxy


# === Enhanced Async Rotator Base Class ===


class AsyncProxyRotator(ProxyRotator):
    """Async-first proxy rotator with enhanced capabilities."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = RotationMetrics()
        self._async_lock = asyncio.Lock()

    async def get_proxy_async(self, proxies: List[Proxy]) -> Optional[Proxy]:
        """Non-blocking proxy selection with concurrent health checks."""
        start_time = time.time()

        try:
            if not proxies:
                return None

            # Parallel availability checking
            async with self._async_lock:
                available_checks = await asyncio.gather(
                    *[self._check_availability_async(p) for p in proxies], return_exceptions=True
                )

            available = [
                p
                for p, check in zip(proxies, available_checks)
                if check and not isinstance(check, Exception)
            ]

            if not available:
                # Emergency fallback with best available
                available = sorted(
                    proxies,
                    key=lambda p: (
                        p.error_state.cooldown_until or datetime.min.replace(tzinfo=timezone.utc)
                    ),
                )[:5]

            # Strategy-specific async selection
            proxy = await self._select_async(available)

            # Update metrics
            self.metrics.selections_total += 1
            if proxy:
                self.metrics.selections_success += 1
                # Track usage
                key = f"{proxy.host}:{proxy.port}"
                self._use_counts[key] = self._use_counts.get(key, 0) + 1

            return proxy

        except Exception as e:
            logger.error(f"Async proxy selection failed: {e}")
            return None
        finally:
            selection_time = time.time() - start_time
            # Update running average
            total = self.metrics.selections_total
            if total > 0:
                self.metrics.avg_selection_time = (
                    self.metrics.avg_selection_time * (total - 1) + selection_time
                ) / total

    async def _check_availability_async(self, proxy: Proxy) -> bool:
        """Async availability check for proxy."""
        return proxy.error_state.is_available() and proxy.status != ProxyStatus.BLACKLISTED

    async def _select_async(self, proxies: List[Proxy]) -> Optional[Proxy]:
        """Async strategy dispatch."""
        if self.strategy == RotationStrategy.ASYNC_ROUND_ROBIN:
            return await self._async_round_robin(proxies)
        elif self.strategy == RotationStrategy.WEIGHTED:
            return await self._async_weighted_selection(proxies)
        elif self.strategy == RotationStrategy.HEALTH_BASED:
            return await self._async_health_based_selection(proxies)
        else:
            # Fallback to sync methods for basic strategies
            return self.get_proxy(proxies)

    async def _async_round_robin(self, proxies: List[Proxy]) -> Optional[Proxy]:
        """Async round-robin selection."""
        if not proxies:
            return None
        proxy = proxies[self._current_index % len(proxies)]
        self._current_index += 1
        return proxy

    async def _async_weighted_selection(self, proxies: List[Proxy]) -> Optional[Proxy]:
        """Async weighted selection based on response time."""
        if not proxies:
            return None

        weights: List[float] = []
        for proxy in proxies:
            if proxy.response_time and proxy.response_time > 0:
                weight = 1.0 / proxy.response_time
            else:
                weight = 1.0
            weights.append(weight)

        # Use asyncio-friendly random selection
        await asyncio.sleep(0)  # Yield control
        return random.choices(proxies, weights=weights)[0]

    async def _async_health_based_selection(self, proxies: List[Proxy]) -> Optional[Proxy]:
        """Async health-based selection."""
        if not proxies:
            return None

        healthy_proxies: List[Tuple[Proxy, float]] = []
        for proxy in proxies:
            key = f"{proxy.host}:{proxy.port}"
            health_score = self._health_scores.get(key, 0.5)
            if health_score > 0.3:
                healthy_proxies.append((proxy, health_score))

        if not healthy_proxies:
            return random.choice(proxies)

        proxies_list, scores = zip(*healthy_proxies)
        await asyncio.sleep(0)  # Yield control
        return random.choices(list(proxies_list), weights=list(scores))[0]


# === Metrics Rotator ===


class MetricsRotator(AsyncProxyRotator):
    """Proxy rotator with Prometheus metrics collection."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create instance-specific registry to avoid conflicts
        self._registry = CollectorRegistry()
        
        # Initialize Prometheus metrics with unique names per instance
        instance_id = id(self)
        self.selection_duration = Histogram(
            f"proxy_selection_duration_seconds_{instance_id}",
            "Time spent selecting proxy",
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
            registry=self._registry,
        )

        self.selection_total = Counter(
            f"proxy_selections_total_{instance_id}", 
            "Total proxy selections", 
            ["strategy", "status"],
            registry=self._registry,
        )

        self.available_proxies = Gauge(
            f"available_proxies_count_{instance_id}", 
            "Number of available proxies",
            registry=self._registry,
        )

        self.session_count = Gauge(
            f"active_sessions_count_{instance_id}", 
            "Number of active sessions",
            registry=self._registry,
        )

        self.circuit_breaker_state = Gauge(
            f"circuit_breaker_state_{instance_id}",
            "Circuit breaker state (0=closed, 1=open, 2=half_open)",
            ["proxy"],
            registry=self._registry,
        )

    async def get_proxy_async(self, proxies: List[Proxy]) -> Optional[Proxy]:
        """Get proxy with metrics collection."""
        start_time = time.time()

        try:
            proxy = await super().get_proxy_async(proxies)
            status = "success" if proxy else "no_proxy_available"

            # Update available proxies gauge
            available_count = len([p for p in proxies if p.error_state.is_available()])
            self.available_proxies.set(available_count)

            return proxy

        except Exception:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            self.selection_duration.observe(duration)
            self.selection_total.labels(strategy=self.strategy.value, status=status).inc()

    def update_session_count(self, count: int):
        """Update active session count metric."""
        self.session_count.set(count)

    def update_circuit_breaker_state(self, proxy_key: str, state: CircuitState):
        """Update circuit breaker state metric."""
        state_value = {CircuitState.CLOSED: 0, CircuitState.OPEN: 1, CircuitState.HALF_OPEN: 2}.get(
            state, 0
        )

        self.circuit_breaker_state.labels(proxy=proxy_key).set(state_value)


# === Circuit Breaker Rotator ===


class CircuitBreakerRotator(AsyncProxyRotator):
    """Proxy rotator with advanced circuit breaker protection."""

    def __init__(self, *args, circuit_config: Optional[CircuitBreakerConfig] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.circuit_config = circuit_config or CircuitBreakerConfig()
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}

    async def get_proxy_with_circuit_breaker(self, proxies: List[Proxy]) -> Optional[Proxy]:
        """Get proxy with circuit breaker protection."""
        proxy = await self.get_proxy_async(proxies)
        if not proxy:
            return None

        key = f"{proxy.host}:{proxy.port}"
        breaker_state = self.circuit_breakers.get(key, CircuitBreakerState())
        self.circuit_breakers[key] = breaker_state

        # Check circuit breaker state
        if breaker_state.state == CircuitState.OPEN:
            if self._should_attempt_reset(breaker_state):
                breaker_state.state = CircuitState.HALF_OPEN
                breaker_state.success_count = 0
                logger.info(f"Circuit breaker for {key} moved to HALF_OPEN")
            else:
                # Find alternative proxy
                alternative_proxies = [p for p in proxies if f"{p.host}:{p.port}" != key]
                if alternative_proxies:
                    return await self.get_proxy_async(alternative_proxies)
                raise CircuitBreakerError(f"Circuit breaker open for {proxy}")

        return proxy

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def execute_with_circuit_breaker(self, proxy: Proxy, operation, *args, **kwargs) -> Any:
        """Execute operation with circuit breaker protection."""
        key = f"{proxy.host}:{proxy.port}"
        breaker_state = self.circuit_breakers.get(key, CircuitBreakerState())
        self.circuit_breakers[key] = breaker_state

        if breaker_state.state == CircuitState.OPEN:
            if not self._should_attempt_reset(breaker_state):
                raise CircuitBreakerError(f"Circuit breaker open for {proxy}")

        try:
            # Execute the operation
            result = await operation(*args, **kwargs)
            self._on_success(breaker_state)
            return result

        except Exception as e:
            self._on_failure(breaker_state)
            raise

    def _should_attempt_reset(self, breaker_state: CircuitBreakerState) -> bool:
        """Check if circuit breaker should attempt reset."""
        if breaker_state.last_failure_time is None:
            return True
        return (
            datetime.now(timezone.utc) - breaker_state.last_failure_time
            > self.circuit_config.recovery_timeout
        )

    def _on_success(self, breaker_state: CircuitBreakerState):
        """Handle successful operation."""
        breaker_state.last_success_time = datetime.now(timezone.utc)

        if breaker_state.state == CircuitState.HALF_OPEN:
            breaker_state.success_count += 1
            if breaker_state.success_count >= self.circuit_config.success_threshold:
                breaker_state.state = CircuitState.CLOSED
                breaker_state.failure_count = 0
                logger.info("Circuit breaker moved to CLOSED")
        elif breaker_state.state == CircuitState.CLOSED:
            breaker_state.failure_count = 0

    def _on_failure(self, breaker_state: CircuitBreakerState):
        """Handle failed operation."""
        breaker_state.last_failure_time = datetime.now(timezone.utc)
        breaker_state.failure_count += 1

        if (
            breaker_state.state == CircuitState.CLOSED
            and breaker_state.failure_count >= self.circuit_config.failure_threshold
        ):
            breaker_state.state = CircuitState.OPEN
            self.metrics.circuit_breaker_trips += 1
            logger.warning("Circuit breaker tripped to OPEN state")

        elif breaker_state.state == CircuitState.HALF_OPEN:
            breaker_state.state = CircuitState.OPEN
            logger.warning("Circuit breaker moved back to OPEN from HALF_OPEN")


# === Consistent Hash Rotator ===


class ConsistentHashRing:
    """Consistent hashing implementation for proxy session stickiness."""

    def __init__(self, replicas: int = 150):
        self.replicas = replicas
        self.ring: List[Tuple[int, Proxy]] = []
        self.proxy_map: Dict[str, Proxy] = {}

    def add_proxy(self, proxy: Proxy):
        """Add proxy to the hash ring."""
        key = f"{proxy.host}:{proxy.port}"
        self.proxy_map[key] = proxy

        for i in range(self.replicas):
            replica_key = f"{key}:{i}"
            hash_value = int(hashlib.md5(replica_key.encode()).hexdigest(), 16)
            self.ring.append((hash_value, proxy))

        self.ring.sort()

    def get_proxy(self, session_id: str) -> Optional[Proxy]:
        """Get proxy for session using consistent hashing."""
        if not self.ring:
            return None

        hash_value = int(hashlib.md5(session_id.encode()).hexdigest(), 16)
        idx = bisect_left([h for h, _ in self.ring], hash_value)

        if idx == len(self.ring):
            idx = 0

        return self.ring[idx][1]

    def remove_proxy(self, proxy: Proxy):
        """Remove proxy from hash ring."""
        key = f"{proxy.host}:{proxy.port}"
        if key in self.proxy_map:
            del self.proxy_map[key]
            self.ring = [(h, p) for h, p in self.ring if f"{p.host}:{p.port}" != key]


class ConsistentHashRotator(AsyncProxyRotator):
    """Proxy rotator with consistent hashing for session stickiness."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hash_ring = ConsistentHashRing()
        self._ring_dirty = True

    async def get_proxy_for_session_ch(
        self, session_id: str, proxies: List[Proxy]
    ) -> Optional[Proxy]:
        """Get proxy using consistent hashing for better stickiness."""
        await self._update_hash_ring(proxies)
        return self.hash_ring.get_proxy(session_id)

    async def get_proxy_for_session_async(
        self, session_id: str, proxies: List[Proxy]
    ) -> Optional[Proxy]:
        """Alias for get_proxy_for_session_ch for compatibility."""
        return await self.get_proxy_for_session_ch(session_id, proxies)

    async def _update_hash_ring(self, proxies: List[Proxy]):
        """Update hash ring with available proxies."""
        if not self._ring_dirty:
            return

        self.hash_ring = ConsistentHashRing()
        for proxy in proxies:
            if proxy.error_state.is_available():
                self.hash_ring.add_proxy(proxy)

        self._ring_dirty = False


# === Geographic Aware Rotator ===


class GeoAwareRotator(AsyncProxyRotator):
    """Geographic and latency-aware proxy rotator."""

    def __init__(
        self,
        *args,
        preferred_regions: Optional[List[str]] = None,
        geo_cache_ttl: int = 3600,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.preferred_regions = preferred_regions or []
        self.location_cache: Dict[str, GeoLocation] = {}
        self.geo_cache_ttl = geo_cache_ttl
        self._cache_timestamps: Dict[str, datetime] = {}

    async def select_by_geography(
        self,
        proxies: List[Proxy],
        target_location: Optional[Tuple[float, float]] = None,
    ) -> Optional[Proxy]:
        """Select proxy based on geographic proximity and regional preferences."""
        if not proxies:
            return None

        self.metrics.geo_selections += 1

        # Filter by preferred regions first
        if self.preferred_regions:
            regional_proxies = [p for p in proxies if p.country_code in self.preferred_regions]
            if regional_proxies:
                proxies = regional_proxies

        # If target location provided, sort by distance
        if target_location:
            proxy_distances = []
            for proxy in proxies:
                try:
                    proxy_location = await self._get_proxy_location(proxy)
                    if proxy_location:
                        distance = self._calculate_distance(
                            target_location,
                            (proxy_location.latitude, proxy_location.longitude),
                        )
                        proxy_distances.append((distance, proxy))
                except Exception:
                    proxy_distances.append((float("inf"), proxy))

            # Sort by distance and select from closest 20%
            proxy_distances.sort()
            closest_count = max(1, len(proxy_distances) // 5)
            closest_proxies = [p for _, p in proxy_distances[:closest_count]]

            # Performance-weighted selection among closest
            return max(
                closest_proxies,
                key=lambda p: p.success_rate * (1.0 / (p.avg_response_time or 1.0)),
            )

        return await self.get_proxy_async(proxies)

    async def _get_proxy_location(self, proxy: Proxy) -> Optional[GeoLocation]:
        """Get proxy geographic location with caching."""
        cache_key = f"{proxy.host}:{proxy.port}"

        # Check cache validity
        if cache_key in self.location_cache:
            timestamp = self._cache_timestamps.get(cache_key)
            if timestamp and (datetime.now(timezone.utc) - timestamp).seconds < self.geo_cache_ttl:
                return self.location_cache[cache_key]

        try:
            # Use IP geolocation service
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"http://ipapi.co/{proxy.host}/json/") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        location = GeoLocation(
                            latitude=float(data.get("latitude", 0)),
                            longitude=float(data.get("longitude", 0)),
                            country=data.get("country_code", ""),
                            region=data.get("region", ""),
                        )
                        self.location_cache[cache_key] = location
                        self._cache_timestamps[cache_key] = datetime.now(timezone.utc)
                        return location
        except Exception as e:
            logger.debug(f"Failed to get location for {proxy.host}: {e}")
            return None

    def _calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates using Haversine formula."""
        from math import asin, cos, radians, sin, sqrt

        lat1, lon1 = radians(loc1[0]), radians(loc1[1])
        lat2, lon2 = radians(loc2[0]), radians(loc2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 6371 * 2 * asin(sqrt(a))  # Earth radius in km


# === ML Adaptive Rotator (Simplified) ===


class AdaptiveMLRotator(AsyncProxyRotator):
    """Machine Learning-based proxy selection with continuous learning."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.training_data: List[Dict[str, Any]] = []
        self.model_trained = False
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

    async def select_proxy_ml(
        self, proxies: List[Proxy], context: Optional[Dict] = None
    ) -> Optional[Proxy]:
        """ML-based proxy selection with context awareness."""
        if not proxies:
            return None

        self.metrics.ml_predictions_made += 1

        if not self.model_trained or len(self.training_data) < 50:
            # Fallback to weighted selection while collecting data
            return await self._async_weighted_selection(proxies)

        try:
            # Score each proxy based on historical performance
            proxy_scores = []
            for proxy in proxies:
                score = self._calculate_ml_score(proxy, context)
                proxy_scores.append((score, proxy))

            # Select from top performers with some randomization
            proxy_scores.sort(reverse=True, key=lambda x: x[0])

            # Use epsilon-greedy strategy (90% exploit, 10% explore)
            if random.random() < 0.9:
                # Exploit: Select from top 30%
                top_count = max(1, len(proxy_scores) // 3)
                top_proxies = [proxy for _, proxy in proxy_scores[:top_count]]
                return random.choice(top_proxies)
            else:
                # Explore: Random selection for learning
                return random.choice(proxies)

        except Exception as e:
            logger.error(f"ML selection failed: {e}")
            return await self._async_weighted_selection(proxies)

    def _calculate_ml_score(self, proxy: Proxy, context: Optional[Dict] = None) -> float:
        """Calculate ML-based score for proxy selection."""
        key = f"{proxy.host}:{proxy.port}"
        history = self.performance_history[key]

        if len(history) < 5:
            return proxy.success_rate * 0.5  # Low confidence for new proxies

        # Calculate features
        recent_requests = list(history)[-20:]  # Last 20 requests
        success_rate = sum(1 for req in recent_requests if req.get("success", False)) / len(
            recent_requests
        )
        avg_response_time = sum(req.get("response_time", 1.0) for req in recent_requests) / len(
            recent_requests
        )

        # Simple scoring algorithm (can be replaced with actual ML model)
        score = success_rate * 0.6  # 60% weight on success rate
        score += (1.0 / max(0.1, avg_response_time)) * 0.3  # 30% weight on speed
        score += (1.0 - proxy.error_state.failure_count / 10.0) * 0.1  # 10% on reliability

        return score

    def update_training_data(
        self,
        proxy: Proxy,
        success: bool,
        response_time: float,
        context: Optional[Dict] = None,
    ):
        """Update training data with request outcomes."""
        key = f"{proxy.host}:{proxy.port}"
        self.performance_history[key].append(
            {
                "success": success,
                "response_time": response_time,
                "timestamp": time.time(),
                "context": context or {},
            }
        )

        # Retrain periodically (simplified)
        if len(self.training_data) % 100 == 0:
            self._retrain_model()

    def _retrain_model(self):
        """Simplified model retraining."""
        # In a real implementation, this would use scikit-learn
        # For now, just mark as trained
        self.model_trained = True
        logger.info("ML model retrained with latest data")
