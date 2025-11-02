"""
Health monitoring for proxy pool.

Provides continuous health checking of proxies using background threads,
automatic failure detection, and recovery mechanisms.
"""

import threading
from datetime import datetime, timezone
from typing import Any, Callable, Optional
from urllib.parse import urlparse

import httpx
from loguru import logger

from proxywhirl.health_models import (
    HealthCheckConfig,
    HealthCheckResult,
    HealthStatus,
)

__all__ = ["HealthChecker"]


class HealthChecker:
    """
    Manages health monitoring of proxy pool with background checks.

    Performs periodic HTTP HEAD requests to verify proxy availability,
    tracks health status, and provides real-time pool statistics.
    """

    def __init__(
        self,
        config: Optional[HealthCheckConfig] = None,
        cache_manager: Optional[Any] = None,
        on_event: Optional[Callable[[Any], None]] = None,
    ) -> None:
        """Initialize health checker.

        Args:
            config: Health check configuration (uses defaults if None)
            cache_manager: Optional CacheManager for persistence
            on_event: Optional callback for health events
        """
        self.config = config or HealthCheckConfig()
        self.cache_manager = cache_manager
        self.on_event = on_event
        self._running = False
        self._proxies: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()

        logger.info(
            "HealthChecker initialized with config: check_interval={}s, failure_threshold={}",
            self.config.check_interval_seconds,
            self.config.failure_threshold,
        )

    def add_proxy(self, proxy_url: str, source: str = "unknown") -> None:
        """Register a proxy for health monitoring.

        Args:
            proxy_url: Full proxy URL (http://host:port)
            source: Source identifier for the proxy

        Raises:
            ValueError: If proxy_url is invalid
        """
        # Validate URL format
        try:
            parsed = urlparse(proxy_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid proxy URL: {proxy_url}")
        except Exception as e:
            raise ValueError(f"Invalid proxy URL: {proxy_url}") from e

        with self._lock:
            if proxy_url in self._proxies:
                logger.debug(f"Proxy already registered, updating: {proxy_url}")
            else:
                logger.debug(f"Registering proxy for health monitoring: {proxy_url}")

            self._proxies[proxy_url] = {
                "source": source,
                "health_status": HealthStatus.UNKNOWN,
                "consecutive_failures": 0,
                "consecutive_successes": 0,
                "total_checks": 0,
                "total_failures": 0,
                "last_check_time": None,
                "last_error": None,
                "recovery_attempt": 0,
                "next_check_time": None,
            }

    def remove_proxy(self, proxy_url: str) -> bool:
        """Remove a proxy from health monitoring.

        Args:
            proxy_url: Proxy URL to remove

        Returns:
            True if proxy was removed, False if it wasn't registered
        """
        with self._lock:
            if proxy_url in self._proxies:
                del self._proxies[proxy_url]
                logger.debug(f"Removed proxy from health monitoring: {proxy_url}")
                return True
            return False

    def check_proxy(self, proxy_url: str) -> HealthCheckResult:
        """Perform a health check on a proxy.

        Args:
            proxy_url: Proxy URL to check

        Returns:
            HealthCheckResult with check outcome
        """
        check_time = datetime.now(timezone.utc)
        check_url = self.config.check_url

        try:
            # Perform HTTP HEAD request through proxy
            # Note: httpx uses 'proxy' parameter, not 'proxies'
            with httpx.Client(
                proxy=proxy_url,
                timeout=self.config.check_timeout_seconds,
            ) as client:
                response = client.head(check_url)

                # Calculate response time
                response_time_ms = response.elapsed.total_seconds() * 1000

                # Check if status code is acceptable
                if response.status_code in self.config.expected_status_codes:
                    return HealthCheckResult(
                        proxy_url=proxy_url,
                        check_time=check_time,
                        status=HealthStatus.HEALTHY,
                        response_time_ms=response_time_ms,
                        status_code=response.status_code,
                        check_url=check_url,
                    )
                else:
                    return HealthCheckResult(
                        proxy_url=proxy_url,
                        check_time=check_time,
                        status=HealthStatus.UNHEALTHY,
                        response_time_ms=response_time_ms,
                        status_code=response.status_code,
                        error_message=f"Unexpected status code: {response.status_code}",
                        check_url=check_url,
                    )

        except httpx.TimeoutException as e:
            return HealthCheckResult(
                proxy_url=proxy_url,
                check_time=check_time,
                status=HealthStatus.UNHEALTHY,
                error_message=f"Request timeout: {str(e)}",
                check_url=check_url,
            )
        except Exception as e:
            return HealthCheckResult(
                proxy_url=proxy_url,
                check_time=check_time,
                status=HealthStatus.UNHEALTHY,
                error_message=f"Check failed: {str(e)}",
                check_url=check_url,
            )

    def _update_health_status(self, proxy_url: str, result: HealthCheckResult) -> None:
        """Update proxy health status based on check result.

        Args:
            proxy_url: Proxy URL being updated
            result: Health check result
        """
        with self._lock:
            if proxy_url not in self._proxies:
                logger.warning(f"Cannot update health for unregistered proxy: {proxy_url}")
                return

            proxy_state = self._proxies[proxy_url]
            proxy_state["last_check_time"] = result.check_time
            proxy_state["total_checks"] += 1

            if result.status == HealthStatus.HEALTHY:
                # Success - reset failure count, increment success count
                proxy_state["consecutive_failures"] = 0
                proxy_state["consecutive_successes"] += 1
                proxy_state["last_error"] = None

                # Check if we should mark as healthy
                if (
                    proxy_state["consecutive_successes"] >= self.config.success_threshold
                    or proxy_state["health_status"] == HealthStatus.UNKNOWN
                ):
                    proxy_state["health_status"] = HealthStatus.HEALTHY
                    logger.info(f"Proxy marked healthy: {proxy_url}")

            else:
                # Failure - reset success count, increment failure count
                proxy_state["consecutive_successes"] = 0
                proxy_state["consecutive_failures"] += 1
                proxy_state["total_failures"] += 1
                proxy_state["last_error"] = result.error_message

                # Check if we should mark as unhealthy
                if proxy_state["consecutive_failures"] >= self.config.failure_threshold:
                    old_status = proxy_state["health_status"]
                    proxy_state["health_status"] = HealthStatus.UNHEALTHY

                    if old_status != HealthStatus.UNHEALTHY:
                        logger.warning(
                            f"Proxy marked unhealthy: {proxy_url}, "
                            f"failures={proxy_state['consecutive_failures']}"
                        )

                        # Invalidate cache if cache manager available
                        if self.cache_manager:
                            try:
                                from proxywhirl.cache import CacheManager

                                cache_key = CacheManager.generate_cache_key(proxy_url)
                                self.cache_manager.invalidate_by_health(cache_key)
                            except Exception as e:
                                logger.error(
                                    f"Failed to invalidate cache for {proxy_url}: {e}"
                                )

                        # Schedule recovery attempt
                        self._schedule_recovery(proxy_url)

    def _schedule_recovery(self, proxy_url: str) -> None:
        """Schedule a recovery attempt for an unhealthy proxy.

        Args:
            proxy_url: Proxy URL to schedule recovery for
        """
        from datetime import datetime, timedelta, timezone

        with self._lock:
            if proxy_url not in self._proxies:
                return

            proxy_state = self._proxies[proxy_url]

            # Calculate exponential backoff cooldown
            attempt = proxy_state.get("recovery_attempt", 0)
            cooldown = self._calculate_recovery_cooldown(attempt)

            # Schedule next check
            proxy_state["next_check_time"] = datetime.now(timezone.utc) + timedelta(
                seconds=cooldown
            )
            proxy_state["health_status"] = HealthStatus.RECOVERING
            proxy_state["recovery_attempt"] = attempt + 1

            logger.info(
                f"Scheduled recovery for {proxy_url} in {cooldown}s (attempt {attempt + 1})"
            )

    def _calculate_recovery_cooldown(self, attempt: int) -> int:
        """Calculate exponential backoff cooldown for recovery attempts.

        Args:
            attempt: Current recovery attempt number (0-based)

        Returns:
            Cooldown period in seconds
        """
        # Exponential backoff: base * 2^attempt
        base = self.config.recovery_cooldown_base_seconds
        cooldown = base * (2**attempt)

        # Cap at a reasonable maximum (e.g., 1 hour)
        max_cooldown = 3600
        return min(cooldown, max_cooldown)

    def _attempt_recovery(self, proxy_url: str) -> None:
        """Attempt to recover an unhealthy proxy.

        Args:
            proxy_url: Proxy URL to attempt recovery on
        """
        from datetime import datetime, timezone

        with self._lock:
            if proxy_url not in self._proxies:
                return

            proxy_state = self._proxies[proxy_url]

            # Check if max recovery attempts reached
            if (
                proxy_state["recovery_attempt"]
                >= self.config.max_recovery_attempts
            ):
                proxy_state["health_status"] = HealthStatus.PERMANENTLY_FAILED
                logger.warning(
                    f"Proxy permanently failed after {proxy_state['recovery_attempt']} recovery attempts: {proxy_url}"
                )
                return

            # Perform health check
            proxy_state["health_status"] = HealthStatus.CHECKING

        # Release lock before check to avoid blocking
        result = self.check_proxy(proxy_url)

        with self._lock:
            if proxy_url not in self._proxies:
                return

            proxy_state = self._proxies[proxy_url]

            if result.status == HealthStatus.HEALTHY:
                # Recovery successful!
                proxy_state["health_status"] = HealthStatus.HEALTHY
                proxy_state["recovery_attempt"] = 0
                proxy_state["consecutive_failures"] = 0
                proxy_state["consecutive_successes"] = 1
                proxy_state["next_check_time"] = None
                logger.info(f"Proxy recovered successfully: {proxy_url}")
            else:
                # Recovery failed, schedule next attempt
                self._schedule_recovery(proxy_url)

    def start(self) -> None:
        """Start health monitoring with background workers.

        Creates one worker thread per unique proxy source.
        """
        if self._running:
            logger.warning("Health monitoring already running")
            return

        self._running = True
        self._workers: dict[str, Any] = {}

        # Get unique sources
        with self._lock:
            sources = set(proxy["source"] for proxy in self._proxies.values())

        # Start a worker for each source
        from proxywhirl.health_worker import HealthWorker

        for source in sources:
            # Get interval for this source (or use default)
            interval = self.config.source_intervals.get(
                source, self.config.check_interval_seconds
            )

            worker = HealthWorker(
                source=source,
                check_interval=interval,
                check_func=self._perform_check,  # Pass method reference directly
                proxies=self._proxies,
                lock=self._lock,
            )
            worker.start()
            self._workers[source] = worker

        logger.info(f"Health monitoring started with {len(self._workers)} workers")

    def stop(self, timeout: float = 5.0) -> None:
        """Stop health monitoring and cleanup workers.

        Args:
            timeout: Maximum seconds to wait for each worker to stop
        """
        if not self._running:
            return

        logger.info("Stopping health monitoring")
        self._running = False

        # Stop all workers
        for source, worker in self._workers.items():
            worker.stop(timeout=timeout)

        self._workers.clear()
        logger.info("Health monitoring stopped")

    def _perform_check(self, proxy_url: str) -> Any:
        """Perform health check and update status.

        Args:
            proxy_url: Proxy URL to check

        Returns:
            HealthCheckResult
        """
        result = self.check_proxy(proxy_url)
        self._update_health_status(proxy_url, result)
        return result

    def get_pool_status(self) -> "PoolStatus":
        """Get real-time health statistics for the entire proxy pool.

        Returns:
            PoolStatus with current health metrics
        """
        from proxywhirl.health_models import PoolStatus, SourceStatus

        with self._lock:
            # Count by status
            status_counts: dict[str, int] = {
                "total": 0,
                "healthy": 0,
                "unhealthy": 0,
                "checking": 0,
                "recovering": 0,
                "unknown": 0,
            }

            # Count by source
            by_source: dict[str, dict[str, int]] = {}

            for proxy_url, state in self._proxies.items():
                status_counts["total"] += 1
                source = state.get("source", "unknown")

                # Initialize source if not seen
                if source not in by_source:
                    by_source[source] = {
                        "total": 0,
                        "healthy": 0,
                        "unhealthy": 0,
                        "checking": 0,
                        "recovering": 0,
                        "unknown": 0,
                    }

                by_source[source]["total"] += 1

                # Count by health status
                health_status = state.get("health_status", HealthStatus.UNKNOWN)
                if health_status == HealthStatus.HEALTHY:
                    status_counts["healthy"] += 1
                    by_source[source]["healthy"] += 1
                elif health_status == HealthStatus.UNHEALTHY:
                    status_counts["unhealthy"] += 1
                    by_source[source]["unhealthy"] += 1
                elif health_status == HealthStatus.CHECKING:
                    status_counts["checking"] += 1
                    by_source[source]["checking"] += 1
                elif health_status == HealthStatus.RECOVERING:
                    status_counts["recovering"] += 1
                    by_source[source]["recovering"] += 1
                else:  # UNKNOWN or PERMANENTLY_FAILED
                    status_counts["unknown"] += 1
                    by_source[source]["unknown"] += 1

            # Create SourceStatus objects
            source_statuses = {
                source: SourceStatus(
                    source_name=source,
                    total_proxies=counts["total"],
                    healthy_proxies=counts["healthy"],
                    unhealthy_proxies=counts["unhealthy"],
                    checking_proxies=counts["checking"],
                    recovering_proxies=counts["recovering"],
                    unknown_proxies=counts["unknown"],
                )
                for source, counts in by_source.items()
            }

            return PoolStatus(
                total_proxies=status_counts["total"],
                healthy_proxies=status_counts["healthy"],
                unhealthy_proxies=status_counts["unhealthy"],
                checking_proxies=status_counts["checking"],
                recovering_proxies=status_counts["recovering"],
                unknown_proxies=status_counts["unknown"],
                by_source=source_statuses,
            )

    def get_proxy_status(self, proxy_url: str) -> Optional["ProxyHealthState"]:
        """Get health state for a specific proxy.

        Args:
            proxy_url: Proxy URL to query

        Returns:
            ProxyHealthState if proxy is registered, None otherwise
        """
        from proxywhirl.health_models import ProxyHealthState

        with self._lock:
            if proxy_url not in self._proxies:
                return None

            state = self._proxies[proxy_url]
            return ProxyHealthState(
                proxy_url=proxy_url,
                health_status=state.get("health_status", HealthStatus.UNKNOWN),
                last_check=state.get("last_check_time"),
                consecutive_failures=state.get("consecutive_failures", 0),
                consecutive_successes=state.get("consecutive_successes", 0),
            )
