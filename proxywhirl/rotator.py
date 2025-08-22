"""proxywhirl/rotator.py -- proxy rotation strategies"""

import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from proxywhirl.models import (
    ErrorHandlingPolicy,
    Proxy,
    ProxyStatus,
    RotationStrategy,
    ValidationErrorType,
)


class ProxyRotator:
    """Handle proxy rotation strategies with health tracking and cooldowns."""

    # Attribute type declarations for strict typing
    _health_scores: dict[str, float]
    _use_counts: dict[str, int]
    _cooldowns: dict[str, datetime]
    _cooldown_period: timedelta

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
    ):
        # Validate strategy input early; tests expect errors for invalid values
        if not isinstance(strategy, RotationStrategy):
            raise ValueError("Invalid rotation strategy")
        self.strategy = strategy
        self._current_index = 0
        # Internal tracking
        self._health_scores = {}
        self._use_counts = {}
        self._cooldowns = {}
        self._cooldown_period = timedelta(seconds=15)

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

        # Update proxy response time if provided
        if response_time is not None:
            proxy.response_time = response_time
            proxy.last_checked = datetime.now(timezone.utc)
