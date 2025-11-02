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
        self._paused = False  # T094: pause/resume flag
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

                        # Emit proxy_down event
                        self._emit_event(
                            "proxy_down",
                            proxy_url=proxy_url,
                            source=proxy_state.get("source"),
                            details={
                                "consecutive_failures": proxy_state["consecutive_failures"],
                                "last_error": proxy_state.get("last_error"),
                            },
                        )

                        # Invalidate cache if cache manager available
                        if self.cache_manager:
                            try:
                                from proxywhirl.cache import CacheManager

                                cache_key = CacheManager.generate_cache_key(proxy_url)
                                self.cache_manager.invalidate_by_health(cache_key)
                            except Exception as e:
                                logger.error(f"Failed to invalidate cache for {proxy_url}: {e}")

                        # Schedule recovery attempt
                        self._schedule_recovery(proxy_url)

                        # Check if pool is degraded
                        self._check_pool_degradation()

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

        with self._lock:
            if proxy_url not in self._proxies:
                return

            proxy_state = self._proxies[proxy_url]

            # Check if max recovery attempts reached
            if proxy_state["recovery_attempt"] >= self.config.max_recovery_attempts:
                proxy_state["health_status"] = HealthStatus.PERMANENTLY_FAILED
                logger.warning(
                    f"Proxy permanently failed after {proxy_state['recovery_attempt']} recovery attempts: {proxy_url}"
                )

                # Emit permanently_failed event
                self._emit_event(
                    "proxy_permanently_failed",
                    proxy_url=proxy_url,
                    source=proxy_state.get("source"),
                    details={"recovery_attempts": proxy_state["recovery_attempt"]},
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

                # Emit recovery event
                self._emit_event(
                    "proxy_recovered",
                    proxy_url=proxy_url,
                    source=proxy_state.get("source"),
                    details={},
                )
            else:
                # Recovery failed, schedule next attempt
                self._schedule_recovery(proxy_url)

    def _emit_event(
        self,
        event_type: str,
        proxy_url: Optional[str] = None,
        source: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Emit a health monitoring event.

        Args:
            event_type: Type of event (proxy_down, proxy_recovered, pool_degraded)
            proxy_url: Optional proxy URL associated with event
            source: Optional proxy source
            details: Optional additional event details
        """
        from proxywhirl.health_models import HealthEvent

        event = HealthEvent(
            event_type=event_type,
            proxy_url=proxy_url,
            source=source,
            details=details or {},
        )

        # Log event
        logger.log(
            event.severity.upper() if event.severity != "info" else "INFO",
            f"Health event: {event_type} - {proxy_url or 'pool'}",
        )

        # Call event callback if registered
        if self.on_event:
            try:
                self.on_event(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")

    def _check_pool_degradation(self) -> None:
        """Check if pool health is degraded and emit event if so."""
        status = self.get_pool_status()

        if status.is_degraded and status.total_proxies > 0:
            self._emit_event(
                "pool_degraded",
                details={
                    "total_proxies": status.total_proxies,
                    "healthy_proxies": status.healthy_proxies,
                    "health_percentage": status.health_percentage,
                },
            )

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
            sources = {proxy["source"] for proxy in self._proxies.values()}

        # Start a worker for each source
        from proxywhirl.health_worker import HealthWorker

        for source in sources:
            # Get interval for this source (or use default)
            interval = self.config.source_intervals.get(source, self.config.check_interval_seconds)

            worker = HealthWorker(
                source=source,
                check_interval=interval,
                check_func=self._perform_check,  # Pass method reference directly
                proxies=self._proxies,
                lock=self._lock,
                checker=self,  # T094: Pass self for pause flag access
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

    def pause(self) -> None:
        """Pause health monitoring temporarily (T094).

        Workers will skip health checks while paused but continue running.
        Useful for maintenance windows or temporary service disruptions.
        """
        with self._lock:
            if not self._running:
                logger.warning("Cannot pause - health monitoring not running")
                return

            self._paused = True
            logger.info("Health monitoring paused")

    def resume(self) -> None:
        """Resume health monitoring after pause (T095).

        Health checks will resume at the next scheduled interval.
        """
        with self._lock:
            if not self._running:
                logger.warning("Cannot resume - health monitoring not running")
                return

            self._paused = False
            logger.info("Health monitoring resumed")

    def get_health_history(
        self, proxy_url: Optional[str] = None, hours: Optional[int] = None
    ) -> list[HealthCheckResult]:
        """Query health check history from SQLite (T096).

        Args:
            proxy_url: Optional proxy URL to filter by
            hours: Optional hours of history to retrieve (default: config.history_retention_hours)

        Returns:
            List of HealthCheckResult ordered by check_time DESC
        """
        from datetime import datetime, timedelta, timezone

        from proxywhirl.health_models import HealthCheckResult

        if not self.cache_manager:
            logger.warning("Cannot query history - no cache manager configured")
            return []

        try:
            import sqlite3

            from proxywhirl.cache import CacheManager

            # Access the L3 SQLite tier
            if not hasattr(self.cache_manager, "l3_tier"):
                logger.warning("Cannot query history - no L3 SQLite tier available")
                return []

            db_path = self.cache_manager.l3_tier.db_path
            conn = sqlite3.connect(str(db_path))

            # Build query
            hours_back = hours or self.config.history_retention_hours
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)

            if proxy_url:
                # Generate cache key for specific proxy
                cache_key = CacheManager.generate_cache_key(proxy_url)
                cursor = conn.execute(
                    """
                    SELECT proxy_key, check_time, status, response_time_ms,
                           error_message, check_url
                    FROM health_history
                    WHERE proxy_key = ? AND check_time >= ?
                    ORDER BY check_time DESC
                    """,
                    (cache_key, cutoff_time.timestamp()),
                )
            else:
                # All proxies
                cursor = conn.execute(
                    """
                    SELECT proxy_key, check_time, status, response_time_ms,
                           error_message, check_url
                    FROM health_history
                    WHERE check_time >= ?
                    ORDER BY check_time DESC
                    """,
                    (cutoff_time.timestamp(),),
                )

            results = []
            for row in cursor.fetchall():
                # Note: We'd need to reverse-lookup proxy_key to proxy_url
                # For now, use the proxy_key as the URL
                results.append(
                    HealthCheckResult(
                        proxy_url=row[0],  # proxy_key
                        check_time=datetime.fromtimestamp(row[1], tz=timezone.utc),
                        status=HealthStatus(row[2]),
                        response_time_ms=row[3],
                        status_code=None,  # Not stored in history table
                        error_message=row[4],
                        check_url=row[5],
                    )
                )

            conn.close()
            return results

        except Exception as e:
            logger.error(f"Failed to query health history: {e}")
            return []
