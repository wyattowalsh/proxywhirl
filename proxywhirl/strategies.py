"""
Rotation strategies for proxy selection.
"""

import random
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Protocol, runtime_checkable

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyPool,
    SelectionContext,
    Session,
    StrategyConfig,
)


class StrategyRegistry:
    """
    Singleton registry for custom rotation strategies.

    Allows registration and retrieval of custom strategy implementations,
    enabling plugin architecture for ProxyWhirl.

    Example:
        >>> from proxywhirl.strategies import StrategyRegistry
        >>>
        >>> # Create custom strategy
        >>> class MyStrategy:
        ...     def select(self, pool):
        ...         return pool.get_all_proxies()[0]
        ...     def record_result(self, proxy, success, response_time_ms):
        ...         pass
        >>>
        >>> # Register it
        >>> registry = StrategyRegistry()
        >>> registry.register_strategy("my-strategy", MyStrategy)
        >>>
        >>> # Retrieve and use
        >>> strategy_class = registry.get_strategy("my-strategy")
        >>> strategy = strategy_class()

    Thread Safety:
        Thread-safe singleton implementation using double-checked locking.

    Performance:
        Registration: O(1)
        Retrieval: O(1)
        Validation: <1ms per strategy (SC-010)
    """

    _instance: Optional["StrategyRegistry"] = None
    _lock = threading.RLock()

    def __init__(self) -> None:
        """Initialize the registry (called once by __new__)."""
        # These are initialized in __new__ for singleton pattern
        if not hasattr(self, "_strategies"):
            self._strategies: dict[str, type] = {}
        if not hasattr(self, "_registry_lock"):
            self._registry_lock = threading.RLock()

    def __new__(cls) -> "StrategyRegistry":
        """Ensure singleton pattern with thread-safe double-checked locking."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._strategies = {}
                    instance._registry_lock = threading.RLock()
                    cls._instance = instance
        return cls._instance

    def register_strategy(self, name: str, strategy_class: type, *, validate: bool = True) -> None:
        """
        Register a custom strategy.

        Args:
            name: Unique name for the strategy (e.g., "my-custom-strategy")
            strategy_class: Strategy class implementing RotationStrategy protocol
            validate: If True (default), validates strategy implements required methods

        Raises:
            ValueError: If strategy name already registered (unless re-registering)
            TypeError: If strategy doesn't implement required protocol methods

        Example:
            >>> class FastStrategy:
            ...     def select(self, pool):
            ...         return pool.get_all_proxies()[0]
            ...     def record_result(self, proxy, success, response_time_ms):
            ...         pass
            >>>
            >>> registry = StrategyRegistry()
            >>> registry.register_strategy("fast", FastStrategy)
        """
        import time

        start_time = time.perf_counter()

        if validate:
            self._validate_strategy(strategy_class)

        with self._registry_lock:
            # Allow re-registration (replacement)
            if name in self._strategies:
                from loguru import logger

                logger.warning(
                    f"Replacing existing strategy registration: {name}",
                    old_class=self._strategies[name].__name__,
                    new_class=strategy_class.__name__,
                )

            self._strategies[name] = strategy_class

        load_time = (time.perf_counter() - start_time) * 1000

        from loguru import logger

        logger.info(
            f"Registered strategy: {name} ({strategy_class.__name__}) in {load_time:.2f}ms",
            strategy_name=name,
            strategy_class=strategy_class.__name__,
            load_time_ms=load_time,
        )

        # Validate SC-010: <1 second load time
        if load_time >= 1000.0:
            logger.warning(
                f"Strategy registration exceeded target time: {load_time:.2f}ms (target: <1000ms)",
                strategy_name=name,
                load_time_ms=load_time,
            )

    def get_strategy(self, name: str) -> type:
        """
        Retrieve a registered strategy class.

        Args:
            name: Strategy name used during registration

        Returns:
            Strategy class (not instance - caller must instantiate)

        Raises:
            KeyError: If strategy name not found in registry

        Example:
            >>> registry = StrategyRegistry()
            >>> strategy_class = registry.get_strategy("my-strategy")
            >>> strategy = strategy_class()  # Instantiate
        """
        with self._registry_lock:
            if name not in self._strategies:
                available = ", ".join(self._strategies.keys()) if self._strategies else "none"
                raise KeyError(
                    f"Strategy '{name}' not found in registry. Available strategies: {available}"
                )
            return self._strategies[name]

    def list_strategies(self) -> list[str]:
        """
        List all registered strategy names.

        Returns:
            List of registered strategy names
        """
        with self._registry_lock:
            return list(self._strategies.keys())

    def unregister_strategy(self, name: str) -> None:
        """
        Remove a strategy from the registry.

        Args:
            name: Strategy name to unregister

        Raises:
            KeyError: If strategy name not found
        """
        with self._registry_lock:
            if name not in self._strategies:
                raise KeyError(f"Strategy '{name}' not found in registry")
            del self._strategies[name]

            from loguru import logger

            logger.info(f"Unregistered strategy: {name}", strategy_name=name)

    def _validate_strategy(self, strategy_class: type) -> None:
        """
        Validate that strategy class implements required protocol.

        Args:
            strategy_class: Strategy class to validate

        Raises:
            TypeError: If required methods are missing
        """
        required_methods = ["select", "record_result"]
        missing_methods = []

        for method in required_methods:
            if not hasattr(strategy_class, method):
                missing_methods.append(method)

        if missing_methods:
            raise TypeError(
                f"Strategy {strategy_class.__name__} missing required methods: "
                f"{', '.join(missing_methods)}. "
                f"Must implement RotationStrategy protocol."
            )

    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton instance (useful for testing).

        Warning:
            This should only be used in tests. Calling this in production
            will clear all registered strategies.
        """
        with cls._lock:
            cls._instance = None


@runtime_checkable
class RotationStrategy(Protocol):
    """Protocol defining interface for proxy rotation strategies."""

    def select(self, pool: ProxyPool, context: Optional[SelectionContext] = None) -> Proxy:
        """
        Select a proxy from the pool based on strategy logic.

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

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
            healthy_proxies = [p for p in healthy_proxies if str(p.id) not in failed_ids]

            if not healthy_proxies:
                raise ProxyPoolEmptyError(
                    "No healthy proxies available after filtering failed proxies"
                )

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

    Thread Safety: Uses Python's random module which is thread-safe
    via GIL-protected random number generation. No additional locking required.
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
            healthy_proxies = [p for p in healthy_proxies if str(p.id) not in failed_ids]

            if not healthy_proxies:
                raise ProxyPoolEmptyError(
                    "No healthy proxies available after filtering failed proxies"
                )

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
    Weighted proxy selection strategy with SelectionContext support.

    Selects proxies based on custom weights or success rates. When custom weights
    are provided via StrategyConfig, they take precedence. Otherwise, weights are
    derived from success_rate. Uses weighted random selection to favor
    higher-performing proxies while still giving all proxies a chance.

    Supports:
    - Custom weights via StrategyConfig.weights (proxy URL -> weight mapping)
    - Fallback to success_rate-based weights
    - Minimum weight (0.1) to ensure all proxies have selection chance
    - SelectionContext for filtering (e.g., failed_proxy_ids)

    Thread Safety: Uses Python's random.choices() which is thread-safe
    via GIL-protected random number generation. No additional locking required.
    """

    def __init__(self) -> None:
        """Initialize weighted strategy."""
        self.config: Optional[StrategyConfig] = None

    def select(self, pool: ProxyPool, context: Optional[SelectionContext] = None) -> Proxy:
        """
        Select a proxy weighted by custom weights or success rate.

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

        Returns:
            Weighted-random selected healthy proxy

        Raises:
            ProxyPoolEmptyError: If no healthy proxies are available
        """
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available in pool")

        # Filter out failed proxies if context provided
        if context and context.failed_proxy_ids:
            failed_ids = set(context.failed_proxy_ids)
            healthy_proxies = [p for p in healthy_proxies if str(p.id) not in failed_ids]

            if not healthy_proxies:
                raise ProxyPoolEmptyError(
                    "No healthy proxies available after filtering failed proxies"
                )

        # Calculate weights
        if self.config and self.config.weights:
            # Use custom weights from config
            weights = []
            for proxy in healthy_proxies:
                custom_weight = self.config.weights.get(proxy.url, None)
                if custom_weight is not None and custom_weight > 0:
                    weights.append(custom_weight)
                else:
                    # Fallback to success rate or minimum weight
                    weights.append(max(proxy.success_rate, 0.1))
        else:
            # Use success rates as weights
            # Add small base weight (0.1) to give all proxies a chance
            weights = [max(proxy.success_rate, 0.1) for proxy in healthy_proxies]

        # Handle edge case: all weights are zero/negative (shouldn't happen with max(0.1))
        if all(w <= 0 for w in weights):
            # Fallback to uniform weights
            weights = [1.0] * len(weights)

        # Use random.choices for weighted selection
        selected = random.choices(healthy_proxies, weights=weights, k=1)[0]

        # Update proxy metadata to track request start
        selected.start_request()

        return selected

    def configure(self, config: StrategyConfig) -> None:
        """
        Configure the strategy with custom settings.

        Args:
            config: Strategy configuration object with optional custom weights
        """
        self.config = config

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """
        Validate that pool has required metadata for weighted selection.

        Weighted strategy can work with success_rate (always available) or custom weights.

        Args:
            pool: The proxy pool to validate

        Returns:
            Always True as success_rate is always available
        """
        return True

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record the result of using a proxy.

        Updates proxy statistics based on request outcome.

        Args:
            proxy: The proxy that was used
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        # Use complete_request for proper tracking
        proxy.complete_request(success=success, response_time_ms=response_time_ms)


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
            healthy_proxies = [p for p in healthy_proxies if str(p.id) not in failed_ids]

            if not healthy_proxies:
                raise ProxyPoolEmptyError(
                    "No healthy proxies available after filtering failed proxies"
                )

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


class PerformanceBasedStrategy:
    """
    Performance-based proxy selection using EMA response times.

    Selects proxies using weighted random selection based on inverse EMA
    response times - faster proxies (lower EMA) get higher weights.
    This adaptively favors better-performing proxies while still giving
    all proxies a chance to be selected.

    Thread Safety: Uses Python's random.choices() which is thread-safe
    via GIL-protected random number generation. No additional locking required.
    """

    def __init__(self) -> None:
        """Initialize performance-based strategy."""
        self.config: Optional[StrategyConfig] = None

    def select(self, pool: ProxyPool, context: Optional[SelectionContext] = None) -> Proxy:
        """
        Select a proxy weighted by inverse EMA response time.

        Faster proxies (lower EMA) receive higher weights for selection.

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

        Returns:
            Performance-weighted selected healthy proxy with EMA data

        Raises:
            ProxyPoolEmptyError: If no healthy proxies with EMA data are available
        """
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available in pool")

        # Filter proxies with EMA data
        proxies_with_ema = [
            p
            for p in healthy_proxies
            if p.ema_response_time_ms is not None and p.ema_response_time_ms > 0
        ]

        if not proxies_with_ema:
            raise ProxyPoolEmptyError(
                "No proxies with EMA data available. "
                "Proxies need historical performance data for performance-based selection."
            )

        # Filter out failed proxies if context provided
        if context and context.failed_proxy_ids:
            failed_ids = set(context.failed_proxy_ids)
            proxies_with_ema = [p for p in proxies_with_ema if str(p.id) not in failed_ids]

            if not proxies_with_ema:
                raise ProxyPoolEmptyError(
                    "No healthy proxies with EMA data available after filtering failed proxies"
                )

        # Calculate inverse weights (lower EMA = higher weight)
        # Use 1/ema_response_time as the weight
        weights = [
            1.0 / p.ema_response_time_ms  # type: ignore[operator]
            for p in proxies_with_ema
        ]

        # Use random.choices for weighted selection
        selected = random.choices(proxies_with_ema, weights=weights, k=1)[0]

        # Track request start
        selected.start_request()

        return selected

    def configure(self, config: StrategyConfig) -> None:
        """Configure the strategy with custom settings."""
        self.config = config

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """
        Validate that proxies have EMA data for performance-based selection.

        Returns:
            True if at least one proxy has EMA data, False otherwise
        """
        healthy_proxies = pool.get_healthy_proxies()
        return any(
            p.ema_response_time_ms is not None and p.ema_response_time_ms > 0
            for p in healthy_proxies
        )

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record the result of using a proxy.

        The EMA is automatically updated by proxy.complete_request() using
        the proxy's configured ema_alpha value.

        Args:
            proxy: The proxy that was used
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        # Complete the request (handles EMA update internally)
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

    def __init__(self) -> None:
        """Initialize session persistence strategy."""
        self._session_manager = SessionManager()
        self._fallback_strategy: RotationStrategy = RoundRobinStrategy()
        self._session_timeout_seconds: int = 3600  # 1 hour default

    def configure(self, config: "StrategyConfig") -> None:
        """
        Configure session persistence parameters.

        Args:
            config: Strategy configuration with session_stickiness_duration_seconds
        """
        # Use session_stickiness_duration_seconds from config
        if config.session_stickiness_duration_seconds is not None:
            self._session_timeout_seconds = config.session_stickiness_duration_seconds

        # Optionally configure fallback strategy
        if hasattr(config, "fallback_strategy") and config.fallback_strategy:
            # In a real implementation, you'd instantiate the strategy from name
            pass

    def validate_metadata(self, pool: "ProxyPool") -> bool:
        """
        Validate that pool has necessary metadata for strategy.

        Session persistence doesn't require specific proxy metadata.

        Args:
            pool: The proxy pool to validate

        Returns:
            Always True - session persistence works with any pool
        """
        return True

    def select(self, pool: "ProxyPool", context: Optional["SelectionContext"] = None) -> "Proxy":
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

        # Check for existing session
        session = self._session_manager.get_session(session_id)

        if session is not None:
            # Session exists - try to use assigned proxy
            try:
                # Convert proxy_id from string to UUID
                from uuid import UUID

                proxy_uuid = UUID(session.proxy_id)
                assigned_proxy = pool.get_proxy_by_id(proxy_uuid)

                # Check if proxy is still healthy or untested (UNKNOWN is acceptable)
                if assigned_proxy is not None and assigned_proxy.health_status in (
                    HealthStatus.HEALTHY,
                    HealthStatus.UNKNOWN,
                ):
                    # Update session last_used
                    self._session_manager.touch_session(session_id)
                    # Mark proxy as in-use
                    assigned_proxy.start_request()
                    return assigned_proxy
                # Proxy unhealthy - need to failover (fall through to new selection)
            except Exception:
                # Error retrieving proxy - fall through to new selection
                pass

        # No valid session or failover needed - select new proxy
        healthy_proxies = pool.get_healthy_proxies()

        # Filter out failed proxies from context
        if context and context.failed_proxy_ids:
            failed_ids = set(context.failed_proxy_ids)
            healthy_proxies = [p for p in healthy_proxies if str(p.id) not in failed_ids]

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

        # Mark proxy as in-use
        new_proxy.start_request()

        return new_proxy

    def record_result(self, proxy: "Proxy", success: bool, response_time_ms: float) -> None:
        """
        Record the result of a request through a proxy.

        Updates proxy completion statistics via Proxy.complete_request().

        Args:
            proxy: The proxy that handled the request
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        proxy.complete_request(success=success, response_time_ms=response_time_ms)

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


class GeoTargetedStrategy:
    """
    Geo-targeted proxy selection strategy.

    Filters proxies based on geographical location (country or region) specified
    in the SelectionContext. Supports fallback to any proxy when no matches found.

    Features:
    - Country-based filtering (ISO 3166-1 alpha-2 codes)
    - Region-based filtering (custom region names)
    - Country takes precedence over region when both specified
    - Configurable fallback behavior
    - Secondary strategy for selection from filtered proxies

    Thread Safety:
        Stateless per-request operations, thread-safe.

    Success Criteria:
        SC-006: 100% correct region selection when available

    Performance:
        O(n) filtering + O(1) or O(n) secondary selection
    """

    def __init__(self) -> None:
        """Initialize geo-targeted strategy."""
        self._fallback_enabled: bool = True
        self._secondary_strategy: RotationStrategy = RoundRobinStrategy()

    def configure(self, config: "StrategyConfig") -> None:
        """
        Configure geo-targeting parameters.

        Args:
            config: Strategy configuration with geo settings
        """
        if config.geo_fallback_enabled is not None:
            self._fallback_enabled = config.geo_fallback_enabled

        # Configure secondary strategy based on name
        if config.geo_secondary_strategy:
            strategy_name = config.geo_secondary_strategy.lower()
            if strategy_name == "round_robin":
                self._secondary_strategy = RoundRobinStrategy()
            elif strategy_name == "random":
                self._secondary_strategy = RandomStrategy()
            elif strategy_name == "least_used":
                self._secondary_strategy = LeastUsedStrategy()
            # Default to round_robin if unknown

    def validate_metadata(self, pool: "ProxyPool") -> bool:
        """
        Validate that pool has geo metadata.

        Geo-targeting is optional, so always returns True.
        Proxies without geo data will simply not match geo filters.

        Args:
            pool: The proxy pool to validate

        Returns:
            Always True - geo data is optional
        """
        return True

    def select(self, pool: "ProxyPool", context: Optional["SelectionContext"] = None) -> "Proxy":
        """
        Select a proxy based on geographical targeting.

        Selection logic:
        1. If context has target_country: filter by country (exact match)
        2. Else if context has target_region: filter by region (exact match)
        3. If no target specified: use all healthy proxies
        4. Apply context.failed_proxy_ids filtering
        5. If filtered list empty and fallback enabled: use all healthy proxies
        6. If filtered list empty and fallback disabled: raise error
        7. Apply secondary strategy to filtered proxies

        Args:
            pool: The proxy pool to select from
            context: Selection context with target_country or target_region

        Returns:
            Proxy matching geo criteria (or any proxy if fallback enabled)

        Raises:
            ProxyPoolEmptyError: If no proxies match criteria and fallback disabled
        """
        # Start with all healthy proxies
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available")

        # Determine target location from context
        target_country = context.target_country if context else None
        target_region = context.target_region if context else None

        # Filter by geography
        if target_country:
            # Country takes precedence - exact match
            filtered_proxies = [
                p
                for p in healthy_proxies
                if p.country_code and p.country_code.upper() == target_country.upper()
            ]
            target_location = target_country
        elif target_region:
            # Region filtering - exact match
            filtered_proxies = [
                p for p in healthy_proxies if p.region and p.region.upper() == target_region.upper()
            ]
            target_location = target_region
        else:
            # No geo targeting - use all healthy proxies
            filtered_proxies = healthy_proxies
            target_location = None

        # Filter out previously failed proxies from context
        if context and context.failed_proxy_ids:
            failed_ids = set(context.failed_proxy_ids)
            filtered_proxies = [p for p in filtered_proxies if str(p.id) not in failed_ids]

        # Handle empty filtered list
        if not filtered_proxies:
            if self._fallback_enabled:
                # Fallback to any healthy proxy (excluding failed)
                if context and context.failed_proxy_ids:
                    failed_ids = set(context.failed_proxy_ids)
                    filtered_proxies = [p for p in healthy_proxies if str(p.id) not in failed_ids]
                else:
                    filtered_proxies = healthy_proxies

                if not filtered_proxies:
                    raise ProxyPoolEmptyError("No healthy proxies available after filtering")
            else:
                # No fallback - raise error with clear message
                location_str = (
                    f"country={target_location}" if target_country else f"region={target_location}"
                )
                raise ProxyPoolEmptyError(
                    f"No proxies available for target location: {location_str}"
                )

        # Create temp pool and apply secondary strategy
        temp_pool = ProxyPool(name="geo_filtered", proxies=filtered_proxies)
        selected_proxy = self._secondary_strategy.select(temp_pool)

        # Mark proxy as in-use
        selected_proxy.start_request()

        return selected_proxy

    def record_result(self, proxy: "Proxy", success: bool, response_time_ms: float) -> None:
        """
        Record the result of a request through a proxy.

        Updates proxy completion statistics via Proxy.complete_request().

        Args:
            proxy: The proxy that handled the request
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        proxy.complete_request(success=success, response_time_ms=response_time_ms)


class CompositeStrategy:
    """
    Composite strategy that applies filtering and selection strategies in sequence.

    This strategy implements the filter + select pattern:
    1. Filter strategies narrow down the proxy pool based on criteria (e.g., geography)
    2. Selector strategy chooses the best proxy from the filtered set

    Example:
        >>> # Filter by geography, then select by performance
        >>> from proxywhirl.strategies import CompositeStrategy, GeoTargetedStrategy, PerformanceBasedStrategy
        >>> strategy = CompositeStrategy(
        ...     filters=[GeoTargetedStrategy()],
        ...     selector=PerformanceBasedStrategy()
        ... )
        >>> proxy = strategy.select(pool, SelectionContext(target_country="US"))

    Thread Safety:
        Thread-safe if all component strategies are thread-safe.

    Performance:
        Selection time is sum of filter and selector times.
        Target: <5ms total (SC-007).
    """

    def __init__(
        self,
        filters: Optional[list["RotationStrategy"]] = None,
        selector: Optional["RotationStrategy"] = None,
    ):
        """
        Initialize composite strategy.

        Args:
            filters: List of filtering strategies to apply sequentially
            selector: Final selection strategy to choose from filtered pool

        Raises:
            ValueError: If both filters and selector are None
        """

        self.filters = filters or []
        self.selector = selector or RoundRobinStrategy()

        if not self.filters and selector is None:
            raise ValueError("CompositeStrategy requires at least one filter or a selector")

    def select(self, pool: "ProxyPool", context: Optional["SelectionContext"] = None) -> "Proxy":
        """
        Select a proxy by applying filters then selector.

        Process:
        1. Start with full pool of healthy proxies
        2. Apply each filter strategy sequentially
        3. Apply selector strategy to filtered set
        4. Return selected proxy

        Args:
            pool: The proxy pool to select from
            context: Request context with filtering criteria

        Returns:
            Selected proxy from filtered pool

        Raises:
            ProxyPoolEmptyError: If filters eliminate all proxies

        Performance:
            Target: <5ms total including all filters and selector (SC-007)
        """
        from proxywhirl.exceptions import ProxyPoolEmptyError

        if context is None:
            from proxywhirl.models import SelectionContext

            context = SelectionContext()

        # Start with healthy proxies only
        filtered_proxies = [p for p in pool.get_all_proxies() if p.is_healthy]

        if not filtered_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available")

        # Apply filters sequentially
        for filter_strategy in self.filters:
            # Create temporary pool with filtered proxies
            temp_pool = pool.__class__(name=f"{pool.name}-filtered")
            for proxy in filtered_proxies:
                temp_pool.add_proxy(proxy)

            # Apply filter
            try:
                selected = filter_strategy.select(temp_pool, context)
                # If filter returned one proxy, use it to filter the set
                # For geo-filtering, this means only proxies matching criteria remain
                filtered_proxies = [
                    p for p in filtered_proxies if self._matches_filter(p, selected)
                ]
            except ProxyPoolEmptyError:
                # Filter eliminated all proxies
                raise ProxyPoolEmptyError(
                    f"Filter {filter_strategy.__class__.__name__} eliminated all proxies"
                )

            if not filtered_proxies:
                raise ProxyPoolEmptyError("All proxies filtered out")

        # Apply selector to filtered pool
        final_pool = pool.__class__(name=f"{pool.name}-final")
        for proxy in filtered_proxies:
            final_pool.add_proxy(proxy)

        return self.selector.select(final_pool, context)

    def _matches_filter(self, proxy: "Proxy", filter_result: "Proxy") -> bool:
        """
        Check if proxy matches filter criteria based on filter result.

        For now, we use a simple heuristic: if the filter strategy selected a proxy,
        we check if it shares key attributes (country, region) with other proxies.

        Args:
            proxy: Proxy to check
            filter_result: Proxy returned by filter strategy

        Returns:
            True if proxy matches filter criteria
        """
        # If same proxy, definitely matches
        if proxy.id == filter_result.id:
            return True

        # Check geo-location match
        if hasattr(filter_result, "country_code") and filter_result.country_code:
            return getattr(proxy, "country_code", None) == filter_result.country_code

        # If no specific criteria, include all
        return True

    def record_result(self, proxy: "Proxy", success: bool, response_time_ms: float) -> None:
        """
        Record result by delegating to selector strategy.

        Args:
            proxy: The proxy that handled the request
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        # Delegate to selector for result recording
        self.selector.record_result(proxy, success, response_time_ms)

        # Also update filters if they track results
        for filter_strategy in self.filters:
            if hasattr(filter_strategy, "record_result"):
                filter_strategy.record_result(proxy, success, response_time_ms)

    def configure(self, config: "StrategyConfig") -> None:
        """
        Configure all component strategies.

        Args:
            config: Strategy configuration to apply
        """
        for filter_strategy in self.filters:
            if hasattr(filter_strategy, "configure"):
                filter_strategy.configure(config)

        if hasattr(self.selector, "configure"):
            self.selector.configure(config)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "CompositeStrategy":
        """
        Create CompositeStrategy from configuration dictionary.

        Args:
            config: Configuration dict with keys:
                - filters: List of filter strategy names or instances
                - selector: Selector strategy name or instance

        Returns:
            Configured CompositeStrategy instance

        Example:
            >>> config = {
            ...     "filters": ["geo-targeted"],
            ...     "selector": "performance-based"
            ... }
            >>> strategy = CompositeStrategy.from_config(config)

        Raises:
            ValueError: If config is invalid
        """
        filters_config = config.get("filters", [])
        selector_config = config.get("selector", "round-robin")

        # Convert filter names to instances
        filters = []
        for f in filters_config:
            if isinstance(f, str):
                # Will be implemented with StrategyRegistry in T070
                filters.append(cls._strategy_from_name(f))
            else:
                filters.append(f)

        # Convert selector name to instance
        if isinstance(selector_config, str):
            selector = cls._strategy_from_name(selector_config)
        else:
            selector = selector_config

        return cls(filters=filters, selector=selector)

    @staticmethod
    def _strategy_from_name(name: str) -> "RotationStrategy":
        """
        Convert strategy name to strategy instance.

        Args:
            name: Strategy name (e.g., "round-robin", "performance-based")

        Returns:
            Strategy instance

        Raises:
            ValueError: If strategy name not recognized
        """
        # Simple mapping for now - will use StrategyRegistry in T070
        strategy_map: dict[str, type[RotationStrategy]] = {
            "round-robin": RoundRobinStrategy,
            "random": RandomStrategy,
            "least-used": LeastUsedStrategy,
            "performance-based": PerformanceBasedStrategy,
            "session": SessionPersistenceStrategy,
            "geo-targeted": GeoTargetedStrategy,
        }

        strategy_class = strategy_map.get(name)
        if strategy_class is None:
            raise ValueError(f"Unknown strategy name: {name}")

        return strategy_class()
