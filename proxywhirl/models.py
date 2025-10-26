"""
Data models for ProxyWhirl using Pydantic v2.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Optional, Protocol, runtime_checkable
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    import httpx


# ============================================================================
# ENUMS
# ============================================================================


class HealthStatus(str, Enum):
    """Proxy health status states."""

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DEAD = "dead"


class ProxySource(str, Enum):
    """Origin type of proxy."""

    USER = "user"
    FETCHED = "fetched"
    API = "api"
    FILE = "file"


class ProxyFormat(str, Enum):
    """Supported proxy list formats."""

    JSON = "json"
    CSV = "csv"
    TSV = "tsv"
    PLAIN_TEXT = "plain_text"
    HTML_TABLE = "html_table"
    CUSTOM = "custom"


class RenderMode(str, Enum):
    """Page rendering modes for fetching proxy lists."""

    STATIC = "static"
    JAVASCRIPT = "javascript"
    BROWSER = "browser"  # Full browser rendering with Playwright
    AUTO = "auto"


class ValidationLevel(str, Enum):
    """Proxy validation strictness levels.

    BASIC: Format + TCP connectivity validation (fast, ~100ms)
    STANDARD: BASIC + HTTP request test (medium, ~500ms)
    FULL: STANDARD + Anonymity check (comprehensive, ~2s)
    """

    BASIC = "basic"
    STANDARD = "standard"
    FULL = "full"


# ============================================================================
# MODELS
# ============================================================================


class ProxyCredentials(BaseModel):
    """Secure credential storage for proxy authentication."""

    username: SecretStr
    password: SecretStr
    auth_type: Literal["basic", "digest", "bearer"] = "basic"
    additional_headers: dict[str, str] = Field(default_factory=dict)

    def to_httpx_auth(self) -> "httpx.BasicAuth":
        """Convert to httpx BasicAuth object."""
        import httpx

        return httpx.BasicAuth(
            username=self.username.get_secret_value(),
            password=self.password.get_secret_value(),
        )

    def to_dict(self, reveal: bool = False) -> dict[str, Any]:
        """Serialize credentials, optionally revealing secrets."""
        if reveal:
            return {
                "username": self.username.get_secret_value(),
                "password": self.password.get_secret_value(),
                "auth_type": self.auth_type,
                "additional_headers": self.additional_headers,
            }
        return {
            "username": "**********",
            "password": "**********",
            "auth_type": self.auth_type,
            "additional_headers": self.additional_headers,
        }


class Proxy(BaseModel):
    """Represents a single proxy server with connection details and metadata."""

    id: UUID = Field(default_factory=uuid4)
    url: str  # Changed from HttpUrl to allow socks:// URLs
    protocol: Optional[Literal["http", "https", "socks4", "socks5"]] = None
    username: Optional[SecretStr] = None
    password: Optional[SecretStr] = None
    health_status: HealthStatus = HealthStatus.UNKNOWN
    last_success_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    total_requests: int = 0
    total_successes: int = 0
    total_failures: int = 0
    average_response_time_ms: Optional[float] = None
    consecutive_failures: int = 0
    tags: set[str] = Field(default_factory=set)
    source: ProxySource = ProxySource.USER
    source_url: Optional[HttpUrl] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # TTL fields for automatic expiration
    ttl: Optional[int] = None  # Time-to-live in seconds
    expires_at: Optional[datetime] = None  # Explicit expiration timestamp

    @model_validator(mode="after")
    def extract_protocol_from_url(self) -> "Proxy":
        """Extract protocol from URL if not explicitly provided."""
        if self.protocol is None and self.url:
            url_str = str(self.url)
            if url_str.startswith("http://"):
                self.protocol = "http"
            elif url_str.startswith("https://"):
                self.protocol = "https"
            elif url_str.startswith("socks4://"):
                self.protocol = "socks4"
            elif url_str.startswith("socks5://"):
                self.protocol = "socks5"
        return self

    @model_validator(mode="after")
    def validate_credentials(self) -> "Proxy":
        """Ensure username and password are both present or both absent."""
        has_username = self.username is not None
        has_password = self.password is not None
        if has_username != has_password:
            raise ValueError("Both username and password must be provided together")
        return self

    @model_validator(mode="after")
    def set_expiration_from_ttl(self) -> "Proxy":
        """Set expires_at timestamp if ttl is provided."""
        if self.ttl is not None and self.expires_at is None:
            self.expires_at = self.created_at + timedelta(seconds=self.ttl)
        return self

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.total_successes / self.total_requests

    @property
    def is_expired(self) -> bool:
        """Check if proxy has expired based on TTL or explicit expiration time.

        Returns:
            True if proxy has expired, False otherwise. Always False if no TTL/expires_at set.
        """
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_healthy(self) -> bool:
        """Check if proxy is healthy."""
        return self.health_status == HealthStatus.HEALTHY

    @property
    def credentials(self) -> Optional[ProxyCredentials]:
        """Get credentials if present."""
        if self.username and self.password:
            return ProxyCredentials(
                username=self.username,
                password=self.password,
            )
        return None

    def record_success(self, response_time_ms: float) -> None:
        """Record a successful request."""
        self.total_requests += 1
        self.total_successes += 1
        self.consecutive_failures = 0
        self.last_success_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

        # Update average response time
        if self.average_response_time_ms is None:
            self.average_response_time_ms = response_time_ms
        else:
            # Exponential moving average
            alpha = 0.3
            self.average_response_time_ms = (
                alpha * response_time_ms + (1 - alpha) * self.average_response_time_ms
            )

        # Update health status
        if self.health_status in (HealthStatus.UNKNOWN, HealthStatus.DEGRADED):
            self.health_status = HealthStatus.HEALTHY

    def record_failure(self, error: Optional[str] = None) -> None:
        """Record a failed request."""
        self.total_requests += 1
        self.total_failures += 1
        self.consecutive_failures += 1
        self.last_failure_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

        # Update health status based on consecutive failures
        if self.consecutive_failures >= 5:
            self.health_status = HealthStatus.DEAD
        elif self.consecutive_failures >= 3:
            self.health_status = HealthStatus.UNHEALTHY
        elif self.consecutive_failures >= 1:
            self.health_status = HealthStatus.DEGRADED

        # Store error in metadata if provided
        if error:
            if "last_errors" not in self.metadata:
                self.metadata["last_errors"] = []
            self.metadata["last_errors"].append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": error,
                }
            )
            # Keep only last 10 errors
            self.metadata["last_errors"] = self.metadata["last_errors"][-10:]


class ProxyConfiguration(BaseSettings):
    """Global configuration settings for the proxy system."""

    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True
    follow_redirects: bool = True
    pool_connections: int = 10
    pool_max_keepalive: int = 20
    health_check_enabled: bool = True
    health_check_interval_seconds: int = 300
    health_check_url: HttpUrl = Field(default="http://httpbin.org/ip")  # type: ignore
    health_check_timeout: int = 10
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"
    log_redact_credentials: bool = True
    storage_backend: Literal["memory", "sqlite", "file"] = "memory"
    storage_path: Optional[Path] = None

    @field_validator("timeout", "max_retries", "pool_connections")
    @classmethod
    def validate_positive(cls, v: int) -> int:
        """Ensure value is positive."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    @model_validator(mode="after")
    def validate_storage(self) -> "ProxyConfiguration":
        """Validate storage configuration."""
        if self.storage_backend in ("sqlite", "file") and self.storage_path is None:
            raise ValueError(f"storage_path required for {self.storage_backend} backend")
        return self

    model_config = {"frozen": True}


class ProxySourceConfig(BaseModel):
    """Configuration for a proxy list source."""

    url: HttpUrl
    format: ProxyFormat
    render_mode: RenderMode = RenderMode.AUTO
    parser: Optional[str] = None
    wait_selector: Optional[str] = None
    wait_timeout: int = 30000
    refresh_interval: int = 3600
    enabled: bool = True
    priority: int = 0
    headers: dict[str, str] = Field(default_factory=dict)
    auth: Optional[tuple[str, str]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SourceStats(BaseModel):
    """Statistics for a proxy source."""

    source_url: str
    total_fetched: int = 0
    valid_count: int = 0
    invalid_count: int = 0
    last_fetch_at: Optional[datetime] = None
    last_fetch_duration_ms: Optional[float] = None
    fetch_failure_count: int = 0
    last_error: Optional[str] = None


class ProxyPool(BaseModel):
    """Collection of proxies with management capabilities."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    proxies: list[Proxy] = Field(default_factory=list)
    max_pool_size: int = 100
    auto_remove_dead: bool = False
    dead_proxy_threshold: int = 5
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def size(self) -> int:
        """Get pool size."""
        return len(self.proxies)

    @property
    def healthy_count(self) -> int:
        """Count healthy proxies."""
        return sum(1 for p in self.proxies if p.is_healthy)

    @property
    def unhealthy_count(self) -> int:
        """Count unhealthy proxies."""
        return sum(1 for p in self.proxies if not p.is_healthy)

    @property
    def total_requests(self) -> int:
        """Sum of all proxy requests."""
        return sum(p.total_requests for p in self.proxies)

    @property
    def overall_success_rate(self) -> float:
        """Weighted average success rate."""
        if not self.proxies or self.total_requests == 0:
            return 0.0

        total_successes = sum(p.total_successes for p in self.proxies)
        return total_successes / self.total_requests

    def add_proxy(self, proxy: Proxy) -> None:
        """Add proxy to pool."""
        if self.size >= self.max_pool_size:
            raise ValueError(f"Pool at maximum capacity ({self.max_pool_size})")

        # Check for duplicates
        if any(p.url == proxy.url for p in self.proxies):
            return  # Silently ignore duplicates

        self.proxies.append(proxy)
        self.updated_at = datetime.now(timezone.utc)

    def remove_proxy(self, proxy_id: UUID) -> None:
        """Remove proxy from pool."""
        self.proxies = [p for p in self.proxies if p.id != proxy_id]
        self.updated_at = datetime.now(timezone.utc)

    def get_proxy_by_id(self, proxy_id: UUID) -> Optional[Proxy]:
        """Find proxy by ID."""
        for proxy in self.proxies:
            if proxy.id == proxy_id:
                return proxy
        return None

    def filter_by_tags(self, tags: set[str]) -> list[Proxy]:
        """Get proxies matching all tags."""
        return [p for p in self.proxies if tags.issubset(p.tags)]

    def filter_by_source(self, source: ProxySource) -> list[Proxy]:
        """Get proxies from specific source."""
        return [p for p in self.proxies if p.source == source]

    def get_healthy_proxies(self) -> list[Proxy]:
        """Get all healthy or unknown (not yet tested) proxies, excluding expired ones.

        Returns only proxies that are:
        - Healthy, degraded, or unknown status
        - Not expired (if TTL is set)
        """
        return [
            p
            for p in self.proxies
            if p.health_status
            in (HealthStatus.HEALTHY, HealthStatus.UNKNOWN, HealthStatus.DEGRADED)
            and not p.is_expired  # Filter out expired proxies
        ]

    def clear_unhealthy(self) -> int:
        """Remove all unhealthy proxies, return count removed."""
        initial_count = self.size
        self.proxies = [
            p
            for p in self.proxies
            if p.health_status not in (HealthStatus.DEAD, HealthStatus.UNHEALTHY)
        ]
        self.updated_at = datetime.now(timezone.utc)
        return initial_count - self.size

    def clear_expired(self) -> int:
        """Remove all expired proxies, return count removed.

        Returns:
            Number of expired proxies removed from the pool
        """
        initial_count = self.size
        self.proxies = [p for p in self.proxies if not p.is_expired]
        self.updated_at = datetime.now(timezone.utc)
        return initial_count - self.size

    def get_all_proxies(self) -> list[Proxy]:
        """Get all proxies in the pool."""
        return self.proxies.copy()

    def get_source_breakdown(self) -> dict[str, int]:
        """Get count of proxies by source."""
        breakdown: dict[str, int] = {}
        for proxy in self.proxies:
            source_key = proxy.source.value
            breakdown[source_key] = breakdown.get(source_key, 0) + 1
        return breakdown


# ============================================================================
# STORAGE PROTOCOLS
# ============================================================================


@runtime_checkable
class StorageBackend(Protocol):
    """Protocol for proxy storage backends.

    This defines the interface that all storage backends must implement,
    allowing for file-based, database, or other storage mechanisms.
    """

    async def save(self, proxies: list[Proxy]) -> None:
        """Save proxies to storage.

        Args:
            proxies: List of proxies to save

        Raises:
            IOError: If save operation fails
        """
        ...

    async def load(self) -> list[Proxy]:
        """Load proxies from storage.

        Returns:
            List of proxies loaded from storage

        Raises:
            FileNotFoundError: If storage doesn't exist
            ValueError: If data is corrupted or invalid
        """
        ...

    async def clear(self) -> None:
        """Clear all proxies from storage.

        Raises:
            IOError: If clear operation fails
        """
        ...


# ============================================================================
# HEALTH MONITORING
# ============================================================================


class HealthMonitor:
    """Continuous health monitoring for proxy pools with auto-eviction.

    Runs background health checks at configurable intervals and automatically
    evicts proxies that fail consecutive checks beyond a threshold.

    Example:
        >>> pool = ProxyPool(name="my_pool")
        >>> pool.add_proxy(Proxy(url="http://proxy.com:8080"))
        >>> monitor = HealthMonitor(pool=pool, check_interval=60, failure_threshold=3)
        >>> await monitor.start()  # Start background checks
        >>> # ... proxies are monitored continuously ...
        >>> await monitor.stop()  # Stop monitoring
    """

    def __init__(
        self,
        pool: ProxyPool,
        check_interval: int = 60,
        failure_threshold: int = 3,
    ) -> None:
        """Initialize health monitor.

        Args:
            pool: ProxyPool to monitor
            check_interval: Seconds between health checks (default: 60)
            failure_threshold: Consecutive failures before eviction (default: 3)

        Raises:
            ValueError: If check_interval or failure_threshold <= 0
        """
        if check_interval <= 0:
            raise ValueError("check_interval must be positive")
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")

        self.pool = pool
        self.check_interval = check_interval
        self.failure_threshold = failure_threshold
        self.is_running = False
        self._task: Optional[asyncio.Task[None]] = None
        self._failure_counts: dict[str, int] = {}
        self._start_time: Optional[datetime] = None

    async def start(self) -> None:
        """Start background health monitoring.

        Creates an asyncio task that runs health checks periodically.
        Idempotent - calling multiple times won't create duplicate tasks.
        """
        if self.is_running:
            return  # Already running

        import asyncio

        self.is_running = True
        self._start_time = datetime.now(timezone.utc)
        self._task = asyncio.create_task(self._check_health_loop())

    async def stop(self) -> None:
        """Stop background health monitoring.

        Cancels the background task and waits for graceful shutdown.
        Idempotent - safe to call when not running.
        """
        if not self.is_running:
            return  # Not running

        self.is_running = False

        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass  # Expected when cancelling
            except Exception:
                pass  # Other errors also ignored during shutdown

        self._task = None
        self._start_time = None

    async def _check_health_loop(self) -> None:
        """Main health check loop - runs periodically."""
        import asyncio

        while self.is_running:
            try:
                await self._run_health_checks()
            except Exception:
                # Log error but keep running
                pass

            # Sleep until next check
            await asyncio.sleep(self.check_interval)

    async def _run_health_checks(self) -> None:
        """Run health checks on all proxies in pool."""
        # This will be implemented with actual TCP/HTTP checks
        # For now, just a placeholder
        pass

    def _record_failure(self, proxy: Proxy) -> None:
        """Record a health check failure for a proxy.

        Args:
            proxy: Proxy that failed health check
        """
        url = proxy.url
        self._failure_counts[url] = self._failure_counts.get(url, 0) + 1

        # Check if threshold reached
        if self._failure_counts[url] >= self.failure_threshold:
            self._evict_proxy(proxy)

    def _record_success(self, proxy: Proxy) -> None:
        """Record a successful health check for a proxy.

        Args:
            proxy: Proxy that passed health check
        """
        url = proxy.url
        # Reset failure count on success
        if url in self._failure_counts:
            del self._failure_counts[url]

    def _evict_proxy(self, proxy: Proxy) -> None:
        """Evict a proxy from the pool due to excessive failures.

        Args:
            proxy: Proxy to evict (matched by URL, not identity)
        """
        # Find and remove proxy by URL (handles different proxy instances with same URL)
        proxy_url = proxy.url
        for p in list(self.pool.proxies):
            if p.url == proxy_url:
                self.pool.remove_proxy(p.id)
                break

        # Clean up failure count
        if proxy_url in self._failure_counts:
            del self._failure_counts[proxy_url]

    def get_status(self) -> dict[str, Any]:
        """Get current monitoring status.

        Returns:
            Dict containing:
                - is_running: Whether monitor is active
                - check_interval: Seconds between checks
                - failure_threshold: Failures before eviction
                - total_proxies: Count of proxies in pool
                - healthy_proxies: Count of healthy proxies
                - failure_counts: Dict of proxy URL -> failure count
                - uptime_seconds: Monitor runtime (if running)
        """
        status: dict[str, Any] = {
            "is_running": self.is_running,
            "check_interval": self.check_interval,
            "failure_threshold": self.failure_threshold,
            "total_proxies": self.pool.size,
            "healthy_proxies": len(self.pool.get_healthy_proxies()),
            "failure_counts": self._failure_counts.copy(),
        }

        if self.is_running and self._start_time:
            uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()
            status["uptime_seconds"] = uptime

        return status
