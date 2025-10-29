"""
Data models for ProxyWhirl using Pydantic v2.
"""

import asyncio
import threading
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Optional, Protocol, runtime_checkable
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, SecretStr, field_validator, model_validator, ConfigDict
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
# STRATEGY MODELS
# ============================================================================


class StrategyConfig(BaseModel):
    """Configuration for rotation strategies.
    
    This model provides flexible configuration options for all rotation
    strategies, allowing customization of weights, EMA parameters, session
    settings, and geo-targeting constraints.
    """
    
    # Weight configuration for weighted strategies
    weights: Optional[dict[str, float]] = Field(
        default=None,
        description="Proxy weights keyed by proxy ID or URL"
    )
    
    # EMA configuration for performance-based strategies
    ema_alpha: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="EMA smoothing factor (0-1). Higher = more weight to recent values"
    )
    
    # Session configuration for session-based strategies
    session_stickiness_duration_seconds: int = Field(
        default=300,
        ge=0,
        description="How long a session should stick to the same proxy"
    )
    
    # Geo-targeting configuration
    preferred_countries: Optional[list[str]] = Field(
        default=None,
        description="List of ISO 3166-1 alpha-2 country codes (e.g., ['US', 'GB'])"
    )
    preferred_regions: Optional[list[str]] = Field(
        default=None,
        description="List of region names (e.g., ['North America', 'Europe'])"
    )
    
    # Fallback strategy configuration
    fallback_strategy: Optional[str] = Field(
        default="random",
        description="Strategy to use when primary strategy fails or metadata missing"
    )
    
    # Performance thresholds
    max_response_time_ms: Optional[float] = Field(
        default=None,
        description="Maximum acceptable response time in milliseconds"
    )
    min_success_rate: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum acceptable success rate (0-1)"
    )
    
    # Window configuration
    window_duration_seconds: int = Field(
        default=3600,
        ge=60,
        description="Sliding window duration for counter resets (default 1 hour)"
    )
    
    model_config = ConfigDict(extra="forbid")


class SelectionContext(BaseModel):
    """Context information for proxy selection decisions.
    
    This model captures all the contextual information that might be relevant
    for intelligent proxy selection, including session tracking, target URL
    characteristics, and previous attempt history.
    """
    
    # Session tracking
    session_id: Optional[str] = Field(
        default=None,
        description="Unique session identifier for sticky sessions"
    )
    
    # Target information
    target_url: Optional[str] = Field(
        default=None,
        description="The URL being accessed (for domain-based routing)"
    )
    target_country: Optional[str] = Field(
        default=None,
        description="Preferred country for geo-targeting (ISO 3166-1 alpha-2)"
    )
    target_region: Optional[str] = Field(
        default=None,
        description="Preferred region for geo-targeting"
    )
    
    # Request metadata
    request_priority: Optional[int] = Field(
        default=None,
        ge=0,
        le=10,
        description="Priority level (0-10, higher = more important)"
    )
    timeout_ms: Optional[float] = Field(
        default=None,
        description="Request timeout in milliseconds"
    )
    
    # Previous attempts (for retry logic)
    failed_proxy_ids: list[str] = Field(
        default_factory=list,
        description="List of proxy IDs that have failed for this request"
    )
    attempt_number: int = Field(
        default=1,
        ge=1,
        description="Current attempt number (1-indexed)"
    )
    
    # Custom metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for custom selection logic"
    )
    
    model_config = ConfigDict(extra="allow")  # Allow custom fields for extensibility


class Session(BaseModel):
    """Session tracking for sticky proxy assignments.
    
    This model maintains the relationship between a session and its assigned
    proxy, with TTL support and usage tracking.
    """
    
    session_id: str = Field(
        description="Unique session identifier"
    )
    proxy_id: str = Field(
        description="ID of the proxy assigned to this session"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the session was created"
    )
    expires_at: datetime = Field(
        description="When the session expires (TTL)"
    )
    last_used_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last time this session was used"
    )
    request_count: int = Field(
        default=0,
        ge=0,
        description="Number of requests made in this session"
    )
    
    def is_expired(self) -> bool:
        """Check if the session has expired.
        
        Returns:
            True if current time >= expires_at
        """
        return datetime.now(timezone.utc) >= self.expires_at
    
    def touch(self) -> None:
        """Update last_used_at timestamp and increment request_count."""
        self.last_used_at = datetime.now(timezone.utc)
        self.request_count += 1
    
    model_config = ConfigDict(extra="forbid")


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
    # Enhanced request tracking (Phase 2: Intelligent Rotation Strategies)
    requests_started: int = 0  # Total requests initiated
    requests_completed: int = 0  # Total requests finished (success or failure)
    requests_active: int = 0  # Currently in-flight requests
    total_requests: int = 0  # Legacy field, kept for backwards compatibility
    total_successes: int = 0
    total_failures: int = 0
    average_response_time_ms: Optional[float] = None
    # EMA (Exponential Moving Average) tracking for performance-based strategies
    ema_response_time_ms: Optional[float] = None  # Current EMA value
    ema_alpha: float = 0.2  # Smoothing factor (configurable, 0 < alpha < 1)
    # Sliding window for counter staleness prevention
    window_start: Optional[datetime] = None  # Start time of current window
    window_duration_seconds: int = 3600  # Window duration (default 1 hour)
    # Geo-location for geo-targeted strategies
    country_code: Optional[str] = None  # ISO 3166-1 alpha-2 code (e.g., "US", "GB")
    region: Optional[str] = None  # Region/state within country (optional)
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

    def start_request(self) -> None:
        """Mark a request as started (for tracking in-flight requests).
        
        This should be called when a request is about to be made through this proxy.
        Increments both requests_started and requests_active counters.
        """
        self.requests_started += 1
        self.requests_active += 1
        self.updated_at = datetime.now(timezone.utc)
        
        # Initialize window if not set
        if self.window_start is None:
            self.window_start = datetime.now(timezone.utc)

    def complete_request(self, success: bool, response_time_ms: float) -> None:
        """Mark a request as complete and update metrics.
        
        Args:
            success: Whether the request was successful
            response_time_ms: Response time in milliseconds
            
        This method decrements requests_active, increments requests_completed,
        updates EMA response time, and delegates to record_success/record_failure.
        """
        # Decrement active count
        if self.requests_active > 0:
            self.requests_active -= 1
        
        # Increment completed count
        self.requests_completed += 1
        
        # Update EMA response time
        if self.ema_response_time_ms is None:
            self.ema_response_time_ms = response_time_ms
        else:
            # EMA formula: EMA_new = alpha * value + (1 - alpha) * EMA_old
            self.ema_response_time_ms = (
                self.ema_alpha * response_time_ms
                + (1 - self.ema_alpha) * self.ema_response_time_ms
            )
        
        # Delegate to existing success/failure recording
        if success:
            self.record_success(response_time_ms)
        else:
            self.record_failure()

    def reset_window(self) -> None:
        """Reset the sliding window counters.
        
        This is called when the window duration has elapsed, preventing
        counter staleness and unbounded memory growth.
        """
        now = datetime.now(timezone.utc)
        self.window_start = now
        self.requests_started = 0
        self.requests_completed = 0
        # Note: Don't reset requests_active as those are truly active
        self.updated_at = now

    def is_window_expired(self) -> bool:
        """Check if the current sliding window has expired.
        
        Returns:
            True if window duration has elapsed since window_start
        """
        if self.window_start is None:
            return False
        
        now = datetime.now(timezone.utc)
        elapsed = (now - self.window_start).total_seconds()
        return elapsed >= self.window_duration_seconds


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
    """Collection of proxies with management capabilities.
    
    Thread-safe proxy pool with RLock protection for concurrent access.
    All mutating operations are automatically protected by a reentrant lock.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    name: str
    proxies: list[Proxy] = Field(default_factory=list)
    max_pool_size: int = 100
    auto_remove_dead: bool = False
    dead_proxy_threshold: int = 5
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __init__(self, **data: Any) -> None:
        """Initialize ProxyPool with thread lock."""
        super().__init__(**data)
        # Use object.__setattr__ to bypass Pydantic's field validation
        object.__setattr__(self, '_lock', threading.RLock())

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
        """Add proxy to pool (thread-safe)."""
        with self._lock:
            if self.size >= self.max_pool_size:
                raise ValueError(f"Pool at maximum capacity ({self.max_pool_size})")

            # Check for duplicates
            if any(p.url == proxy.url for p in self.proxies):
                return  # Silently ignore duplicates

            self.proxies.append(proxy)
            self.updated_at = datetime.now(timezone.utc)

    def remove_proxy(self, proxy_id: UUID) -> None:
        """Remove proxy from pool (thread-safe)."""
        with self._lock:
            self.proxies = [p for p in self.proxies if p.id != proxy_id]
            self.updated_at = datetime.now(timezone.utc)

    def get_proxy_by_id(self, proxy_id: UUID) -> Optional[Proxy]:
        """Find proxy by ID (thread-safe)."""
        with self._lock:
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
        """Get all healthy or unknown (not yet tested) proxies, excluding expired ones (thread-safe).

        Returns only proxies that are:
        - Healthy, degraded, or unknown status
        - Not expired (if TTL is set)
        """
        with self._lock:
            return [
                p
                for p in self.proxies
                if p.health_status
                in (HealthStatus.HEALTHY, HealthStatus.UNKNOWN, HealthStatus.DEGRADED)
                and not p.is_expired  # Filter out expired proxies
            ]

    def clear_unhealthy(self) -> int:
        """Remove all unhealthy proxies, return count removed (thread-safe)."""
        with self._lock:
            initial_count = self.size
            self.proxies = [
                p
                for p in self.proxies
                if p.health_status not in (HealthStatus.DEAD, HealthStatus.UNHEALTHY)
            ]
            self.updated_at = datetime.now(timezone.utc)
            return initial_count - self.size

    def clear_expired(self) -> int:
        """Remove all expired proxies, return count removed (thread-safe).

        Returns:
            Number of expired proxies removed from the pool
        """
        with self._lock:
            initial_count = self.size
            self.proxies = [p for p in self.proxies if not p.is_expired]
            self.updated_at = datetime.now(timezone.utc)
            return initial_count - self.size

    def get_all_proxies(self) -> list[Proxy]:
        """Get all proxies in the pool (thread-safe)."""
        with self._lock:
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


# ============================================================================
# CLI MODELS
# ============================================================================


class RequestResult(BaseModel):
    """Result of HTTP request made through proxy."""

    url: str
    method: str  # GET, POST, PUT, DELETE, etc.
    status_code: int
    elapsed_ms: float
    proxy_used: str  # URL of proxy that succeeded
    attempts: int  # Number of retries before success
    headers: dict[str, str]  # Response headers
    body: Optional[str] = None  # Response body (truncated if large)
    error: Optional[str] = None  # Error message if failed
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def is_success(self) -> bool:
        """Check if request was successful."""
        return 200 <= self.status_code < 300


class ProxyStatus(BaseModel):
    """Status of a single proxy in the pool."""

    url: str
    health: str  # "healthy", "degraded", "failed", "unknown"
    last_check: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    success_rate: float = 0.0  # 0.0-1.0
    total_requests: int = 0
    failed_requests: int = 0
    is_active: bool = True


class PoolSummary(BaseModel):
    """Summary of entire proxy pool."""

    total_proxies: int
    healthy: int
    degraded: int
    failed: int
    rotation_strategy: str
    current_index: int  # For round-robin
    proxies: list[ProxyStatus]
