"""Storage backends for persisting proxy pools."""

from __future__ import annotations

import base64
import json
from datetime import date as Date  # noqa: N812
from datetime import datetime
from pathlib import Path
from uuid import UUID

import aiofiles
import sqlalchemy as sa
from cryptography.fernet import Fernet
from loguru import logger
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import Field, SQLModel, select

from proxywhirl.cache.crypto import CredentialEncryptor
from proxywhirl.models import Proxy

# Prefix for encrypted credentials stored as strings
_ENCRYPTED_PREFIX = "encrypted:"


class ProxyTable(SQLModel, table=True):
    """SQLModel table schema for proxy storage in SQLite.

    This table stores comprehensive proxy metadata including health metrics,
    authentication credentials, usage statistics, and analytics. Multiple fields
    are indexed for fast querying by geographic location, health status, and source.

    Primary Key:
        url: Full proxy URL (e.g., "http://proxy.com:8080")

    Secondary Keys:
        id: UUID for proxy identification

    Core Fields:
        protocol: Protocol type (http, https, socks4, socks5)
        username: Optional authentication username
        password: Optional authentication password (store encrypted at app level)

    Health Status:
        health_status: Current health status (healthy, unhealthy, degraded, dead, unknown)
        last_success_at: Timestamp of last successful request
        last_failure_at: Timestamp of last failed request
        last_health_check: Timestamp of last health check
        last_health_error: Last health check error message
        total_checks: Total health checks performed
        total_health_failures: Total health check failures
        consecutive_successes: Consecutive successful health checks
        consecutive_failures: Current consecutive failure streak
        recovery_attempt: Current recovery attempt count
        next_check_time: Scheduled next health check
        last_recovered_at: Timestamp of last recovery from unhealthy state
        revival_attempts: Number of recovery attempts made
        health_status_transitions_json: JSON string tracking status transitions

    Request Tracking:
        requests_started: Total requests initiated
        requests_completed: Total requests finished (success or failure)
        requests_active: Currently in-flight requests
        total_requests: Cumulative request count (legacy)
        total_successes: Cumulative success count
        total_failures: Cumulative failure count

    Response Time Metrics:
        average_response_time_ms: Rolling average response time in milliseconds
        ema_response_time_ms: Exponential moving average response time
        ema_alpha: EMA smoothing factor
        response_time_p50_ms: 50th percentile response time
        response_time_p95_ms: 95th percentile response time
        response_time_p99_ms: 99th percentile response time
        min_response_time_ms: Minimum response time observed
        max_response_time_ms: Maximum response time observed
        response_time_stddev_ms: Response time standard deviation
        response_samples_count: Number of response time samples collected

    Error Tracking:
        error_types_json: JSON dict mapping error type to count
        last_error_type: Most recent error type
        last_error_message: Most recent error message
        last_error_at: Timestamp of last error
        timeout_count: Number of timeout errors
        connection_refused_count: Number of connection refused errors
        ssl_error_count: Number of SSL/TLS errors
        http_4xx_count: Number of HTTP 4xx client errors
        http_5xx_count: Number of HTTP 5xx server errors

    Geographic Information:
        country_code: ISO 3166-1 alpha-2 country code (indexed)
        country_name: Full country name
        region: Region/state within country
        city: City location
        isp_name: Internet Service Provider name
        asn: Autonomous System Number
        is_residential: Whether proxy is residential IP
        is_datacenter: Whether proxy is datacenter IP
        is_vpn: Whether proxy is VPN service
        is_tor: Whether proxy is Tor exit node
        latitude: Geographic latitude
        longitude: Geographic longitude

    Protocol Support:
        http_version: HTTP version supported (e.g., "1.1", "2.0")
        tls_version: TLS version supported (e.g., "1.2", "1.3")
        supports_https: Whether HTTPS is supported
        supports_connect: Whether HTTP CONNECT method is supported
        supports_http2: Whether HTTP/2 is supported

    Source Metadata:
        source: Proxy source identifier (indexed) - user, fetched, api, etc.
        source_url: Original URL where proxy was fetched from
        source_name: Human-readable source name
        fetch_timestamp: When proxy was fetched
        fetch_duration_ms: Time taken to fetch proxy
        last_validation_time: Last time proxy was validated
        validation_method: Method used for validation

    Sliding Window:
        window_start: Start time of current sliding window
        window_duration_seconds: Window duration in seconds

    Tags & TTL:
        tags_json: JSON array of proxy tags
        ttl: Time-to-live in seconds
        expires_at: Explicit expiration timestamp

    Metadata:
        metadata_json: JSON string for additional custom metadata
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    __tablename__: str = "proxies"  # type: ignore[misc]

    # Primary and Secondary Keys
    url: str = Field(primary_key=True)
    id: str | None = None  # UUID stored as string

    # Core Fields
    protocol: str | None = None
    username: str | None = None
    password: str | None = None

    # Health Status
    health_status: str = "unknown"
    last_success_at: datetime | None = None
    last_failure_at: datetime | None = None
    last_health_check: datetime | None = None
    last_health_error: str | None = None
    total_checks: int = 0
    total_health_failures: int = 0
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    recovery_attempt: int = 0
    next_check_time: datetime | None = None
    last_recovered_at: datetime | None = None
    revival_attempts: int = 0
    health_status_transitions_json: str | None = None

    # Request Tracking
    requests_started: int = 0
    requests_completed: int = 0
    requests_active: int = 0
    total_requests: int = 0
    total_successes: int = 0
    total_failures: int = 0

    # Response Time Metrics
    average_response_time_ms: float | None = None
    ema_response_time_ms: float | None = None
    ema_alpha: float = 0.2
    response_time_p50_ms: float | None = None
    response_time_p95_ms: float | None = None
    response_time_p99_ms: float | None = None
    min_response_time_ms: float | None = None
    max_response_time_ms: float | None = None
    response_time_stddev_ms: float | None = None
    response_samples_count: int = 0

    # Error Tracking
    error_types_json: str | None = None
    last_error_type: str | None = None
    last_error_message: str | None = None
    last_error_at: datetime | None = None
    timeout_count: int = 0
    connection_refused_count: int = 0
    ssl_error_count: int = 0
    http_4xx_count: int = 0
    http_5xx_count: int = 0

    # Geographic Information (country_code indexed for fast geo-filtering)
    country_code: str | None = Field(default=None, index=True)
    country_name: str | None = None
    region: str | None = None
    city: str | None = None
    isp_name: str | None = None
    asn: int | None = None
    is_residential: bool | None = None
    is_datacenter: bool | None = None
    is_vpn: bool | None = None
    is_tor: bool | None = None
    latitude: float | None = None
    longitude: float | None = None

    # Protocol Support
    http_version: str | None = None
    tls_version: str | None = None
    supports_https: bool | None = None
    supports_connect: bool | None = None
    supports_http2: bool | None = None

    # Source Metadata (source indexed for fast source-based queries)
    source: str = Field(default="user", index=True)
    source_url: str | None = None
    source_name: str | None = None
    fetch_timestamp: datetime | None = None
    fetch_duration_ms: float | None = None
    last_validation_time: datetime | None = None
    validation_method: str | None = None

    # Sliding Window
    window_start: datetime | None = None
    window_duration_seconds: int = 3600

    # Tags & TTL
    tags_json: str | None = None
    ttl: int | None = None
    expires_at: datetime | None = None

    # Metadata
    metadata_json: str = "{}"
    created_at: datetime
    updated_at: datetime


class CacheEntryTable(SQLModel, table=True):
    """SQLModel table schema for L3 cache storage.

    This table stores cached proxy entries with TTL, health status, and
    encryption support for credentials. Used by the three-tier caching
    system (L1 memory, L2 JSONL files, L3 SQLite).

    Attributes:
        key: Primary key - URL-safe hash of proxy URL
        proxy_url: Full proxy URL (scheme://host:port)
        username_encrypted: Encrypted username (BLOB), None if no auth
        password_encrypted: Encrypted password (BLOB), None if no auth
        source: Proxy source identifier (indexed)
        fetch_time: Unix timestamp when proxy was fetched
        last_accessed: Unix timestamp of last cache access (indexed)
        access_count: Number of cache hits
        ttl_seconds: Time-to-live duration in seconds
        expires_at: Unix timestamp of expiration (indexed)
        health_status: Current health status: healthy, unhealthy, unknown (indexed)
        failure_count: Consecutive failures for health tracking
        created_at: Unix timestamp of record creation
        updated_at: Unix timestamp of last update
    """

    __tablename__: str = "cache_entries"  # type: ignore[misc]

    key: str = Field(primary_key=True)
    proxy_url: str
    username_encrypted: bytes | None = None
    password_encrypted: bytes | None = None
    source: str = Field(index=True)
    fetch_time: float
    last_accessed: float = Field(index=True)
    access_count: int = 0
    ttl_seconds: int
    expires_at: float = Field(index=True)
    health_status: str = Field(default="unknown", index=True)
    failure_count: int = 0
    created_at: float
    updated_at: float


class CircuitBreakerStateTable(SQLModel, table=True):
    """SQLModel table schema for circuit breaker state persistence.

    This table stores circuit breaker state across restarts to prevent
    immediately retrying failed proxies.

    Attributes:
        proxy_id: Primary key - unique identifier for the proxy
        state: Current circuit breaker state (closed, open, half_open)
        failure_count: Current failure count within the rolling window
        failure_window_json: JSON array of failure timestamps
        next_test_time: Unix timestamp when circuit can transition to half-open
        last_state_change: Timestamp of last state transition
        failure_threshold: Configured failure threshold
        window_duration: Configured window duration in seconds
        timeout_duration: Configured timeout duration in seconds
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    __tablename__: str = "circuit_breaker_states"  # type: ignore[misc]

    proxy_id: str = Field(primary_key=True)
    state: str = Field(index=True)  # closed, open, half_open
    failure_count: int = 0
    failure_window_json: str = "[]"  # JSON array of timestamps
    next_test_time: float | None = None
    last_state_change: datetime
    failure_threshold: int = 5
    window_duration: float = 60.0
    timeout_duration: float = 30.0
    created_at: datetime
    updated_at: datetime


class DailyStatsTable(SQLModel, table=True):
    """SQLModel table schema for daily analytics statistics.

    This table stores aggregated daily metrics for monitoring proxy pool
    performance over time. One record per day with cumulative statistics.

    Attributes:
        stat_date: Primary key - date of the statistics (YYYY-MM-DD)
        total_requests: Total number of requests made on this day
        total_successes: Number of successful requests on this day
        total_failures: Number of failed requests on this day
        avg_response_time_ms: Average response time in milliseconds for this day
    """

    model_config = {"arbitrary_types_allowed": True}

    __tablename__: str = "daily_stats"  # type: ignore[misc]

    stat_date: Date = Field(sa_column=sa.Column("date", sa.Date, primary_key=True))  # type: ignore[valid-type]
    total_requests: int = Field(default=0)
    total_successes: int = Field(default=0)
    total_failures: int = Field(default=0)
    avg_response_time_ms: float = Field(default=0.0)


class RequestLogTable(SQLModel, table=True):
    """SQLModel table schema for detailed request logging.

    This table stores individual request logs for detailed analytics and debugging.
    Each record represents a single HTTP request made through a proxy.

    Attributes:
        id: Primary key - auto-incrementing request log ID
        timestamp: When the request was made (indexed for time-range queries)
        proxy_url: Full URL of the proxy used (indexed for proxy-specific queries)
        target_url: Target URL that was requested
        response_time_ms: Response time in milliseconds
        status_code: HTTP status code (None if request failed before receiving response)
        success: Whether the request succeeded
        error: Error message if request failed (None if successful)
    """

    __tablename__: str = "request_logs"  # type: ignore[misc]

    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(index=True)
    proxy_url: str = Field(index=True)
    target_url: str
    response_time_ms: float
    status_code: int | None = None
    success: bool
    error: str | None = None


class FileStorage:
    """File-based storage backend using JSON.

    Stores proxies in a JSON file with atomic writes to prevent corruption.
    Supports optional encryption for sensitive credential data.
    """

    def __init__(self, filepath: str | Path, encryption_key: bytes | None = None) -> None:
        """Initialize file storage.

        Args:
            filepath: Path to the JSON file for storage
            encryption_key: Optional Fernet encryption key for encrypting credentials.
                If provided, all data will be encrypted at rest.
        """
        self.filepath = Path(filepath)
        self.encryption_key = encryption_key
        self._cipher = Fernet(encryption_key) if encryption_key else None

    async def save(self, proxies: list[Proxy]) -> None:
        """Save proxies to JSON file.

        Args:
            proxies: List of proxies to save

        Raises:
            IOError: If save operation fails
        """
        # Ensure parent directory exists
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        # Serialize proxies - use model_dump with context to reveal secrets for storage
        data = []
        for proxy in proxies:
            proxy_dict = proxy.model_dump(mode="json")
            # Reveal SecretStr values for storage
            if proxy.username:
                proxy_dict["username"] = proxy.username.get_secret_value()
            if proxy.password:
                proxy_dict["password"] = proxy.password.get_secret_value()
            data.append(proxy_dict)

        json_str = json.dumps(data, indent=2)

        # Encrypt if cipher is configured
        content: bytes | str
        write_mode: str
        if self._cipher:
            content = self._cipher.encrypt(json_str.encode("utf-8"))
            write_mode = "wb"
        else:
            content = json_str
            write_mode = "w"

        # Atomic write: write to temp file then rename
        # Use unique temp file to avoid race conditions in concurrent saves
        import uuid

        temp_path = self.filepath.with_suffix(f".tmp.{uuid.uuid4().hex[:8]}")
        try:
            async with aiofiles.open(temp_path, write_mode) as f:
                await f.write(content)
                # Ensure file is flushed to disk before renaming
                await f.flush()
            # File is now closed and flushed, safe to rename
            temp_path.replace(self.filepath)
        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise OSError(f"Failed to save proxies: {e}") from e

    async def load(self) -> list[Proxy]:
        """Load proxies from JSON file.

        Returns:
            List of proxies loaded from file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid or data is corrupted
            cryptography.fernet.InvalidToken: If decryption fails (wrong key)
        """
        from cryptography.fernet import InvalidToken

        if not self.filepath.exists():
            raise FileNotFoundError(f"Storage file not found: {self.filepath}")

        try:
            # Read file content
            if self._cipher:
                async with aiofiles.open(self.filepath, "rb") as f:
                    encrypted_data = await f.read()
                # Decrypt data
                json_str = self._cipher.decrypt(encrypted_data).decode("utf-8")
                data = json.loads(json_str)
            else:
                async with aiofiles.open(self.filepath) as f:
                    content = await f.read()
                    data = json.loads(content)

            # Deserialize to Proxy objects
            proxies = [Proxy.model_validate(item) for item in data]
            return proxies
        except InvalidToken:
            # Re-raise InvalidToken without wrapping it
            raise
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in storage file: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to load proxies: {e}") from e

    async def clear(self) -> None:
        """Clear all proxies from storage by deleting the file.

        Raises:
            IOError: If clear operation fails
        """
        try:
            if self.filepath.exists():
                self.filepath.unlink()
        except Exception as e:
            raise OSError(f"Failed to clear storage: {e}") from e


class SQLiteStorage:
    """SQLite-based storage backend with advanced query capabilities.

    Provides high-performance async proxy storage using SQLite with SQLModel ORM.
    Supports complex queries, automatic upserts, and concurrent access through
    async session management with configurable connection pooling.

    Features:
        - Async operations using aiosqlite for non-blocking I/O
        - Configurable connection pooling for concurrent access
        - Advanced filtering by source, health_status, protocol
        - Automatic schema creation and migration
        - Indexed columns for fast queries
        - Thread-safe concurrent access
        - Automatic upsert on save (updates existing proxies)

    Example:
        ```python
        # Default async driver (recommended)
        storage = SQLiteStorage("proxies.db", use_async_driver=True, pool_size=10)
        await storage.initialize()

        # Configuration option for future compatibility
        storage = SQLiteStorage("proxies.db", use_async_driver=False)
        await storage.initialize()

        # Save proxies
        await storage.save([proxy1, proxy2])

        # Query by source
        user_proxies = await storage.query(source="user")

        # Load all
        all_proxies = await storage.load()

        await storage.close()
        ```
    """

    def __init__(
        self,
        filepath: str | Path,
        use_async_driver: bool = True,
        pool_size: int = 5,
        pool_max_overflow: int = 10,
        pool_timeout: float = 30.0,
        pool_recycle: int = 3600,
    ) -> None:
        """Initialize SQLite storage with connection pooling.

        Args:
            filepath: Path to the SQLite database file. Will be created if it doesn't exist.
                Parent directories will be created automatically.
            use_async_driver: Whether to use async aiosqlite driver (True, recommended) for
                true non-blocking async I/O. When False, uses a compatibility mode that may
                fall back to sync operations. Default is True for best async performance.
                Note: Current implementation requires aiosqlite; this option is reserved for
                future compatibility enhancements.
            pool_size: Size of the connection pool (max concurrent connections). Default: 5
            pool_max_overflow: Max overflow connections beyond pool_size. Default: 10
            pool_timeout: Timeout in seconds when getting connection from pool. Default: 30.0
            pool_recycle: Recycle connections after N seconds (-1 to disable). Default: 3600
        """

        self.filepath = Path(filepath)
        self.use_async_driver = use_async_driver
        self.pool_size = pool_size
        self.pool_max_overflow = pool_max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle

        # Current implementation uses aiosqlite for async operations
        # use_async_driver parameter is provided for configuration compatibility
        # and future enhancements but currently always uses async driver
        db_url = f"sqlite+aiosqlite:///{self.filepath}"

        # Note: SQLite with aiosqlite uses StaticPool by default which doesn't support
        # pool_size, max_overflow, pool_timeout parameters. These are stored as instance
        # attributes for API compatibility and future enhancement with other backends.
        self.engine: AsyncEngine = create_async_engine(
            db_url,
            echo=False,
        )

        # Initialize credential encryptor for secure credential storage
        self._encryptor: CredentialEncryptor | None = None
        self._init_encryptor()

    def _init_encryptor(self) -> None:
        """Initialize the credential encryptor.

        Creates a CredentialEncryptor using environment-based keys.
        Logs a warning if encryption is not configured (credentials will be stored unencrypted).
        """
        try:
            self._encryptor = CredentialEncryptor()
            logger.debug("Credential encryption initialized for SQLite storage")
        except Exception as e:
            logger.warning(
                f"Credential encryption not available, storing credentials unencrypted: {e}"
            )
            self._encryptor = None

    def _encrypt_credential(self, value: str | None) -> str | None:
        """Encrypt a credential value for storage.

        Args:
            value: Plaintext credential value (or None)

        Returns:
            Encrypted credential as prefixed base64 string, or None if input is None.
            If encryption is not configured, returns plaintext value.
        """
        if value is None:
            return None

        if self._encryptor is None:
            # Encryption not configured, store plaintext (with warning logged at init)
            return value

        try:
            encrypted_bytes = self._encryptor.encrypt(SecretStr(value))
            if not encrypted_bytes:
                return None
            # Encode as base64 string with prefix for storage in TEXT column
            encoded = base64.b64encode(encrypted_bytes).decode("utf-8")
            return f"{_ENCRYPTED_PREFIX}{encoded}"
        except Exception as e:
            logger.error(f"Failed to encrypt credential, storing unencrypted: {e}")
            return value

    def _decrypt_credential(self, value: str | None) -> str | None:
        """Decrypt a credential value from storage.

        Args:
            value: Stored credential value (encrypted with prefix or plaintext legacy)

        Returns:
            Decrypted plaintext credential, or None if input is None.
            Handles legacy unencrypted values gracefully.
        """
        if value is None:
            return None

        # Check if value is encrypted (has prefix)
        if not value.startswith(_ENCRYPTED_PREFIX):
            # Legacy plaintext value - return as-is
            logger.debug("Found legacy unencrypted credential in storage")
            return value

        if self._encryptor is None:
            logger.error(
                "Cannot decrypt credential: encryptor not configured. "
                "Set PROXYWHIRL_CACHE_ENCRYPTION_KEY environment variable."
            )
            return None

        try:
            # Remove prefix and decode base64
            encoded = value[len(_ENCRYPTED_PREFIX) :]
            encrypted_bytes = base64.b64decode(encoded)
            # Decrypt
            decrypted = self._encryptor.decrypt(encrypted_bytes)
            return decrypted.get_secret_value() if decrypted else None
        except Exception as e:
            logger.error(f"Failed to decrypt credential: {e}")
            return None

    async def initialize(self) -> None:
        """Create database tables if they don't exist.

        Should be called once before any other operations. Creates the 'proxies'
        table with all necessary columns and indexes. Safe to call multiple times -
        existing tables won't be affected.

        Raises:
            Exception: If database initialization fails
        """
        from sqlmodel import SQLModel

        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def close(self) -> None:
        """Close database connection and release resources.

        Should be called when done with the storage to properly cleanup
        database connections. Safe to call multiple times.
        """
        await self.engine.dispose()

    def _proxy_to_table(self, proxy: Proxy) -> ProxyTable:
        """Convert a Proxy model to ProxyTable for storage.

        This helper method encapsulates the conversion logic to keep the save method clean.

        Args:
            proxy: Proxy model instance to convert

        Returns:
            ProxyTable instance ready for database insertion
        """
        # Serialize tags to JSON
        tags_json = json.dumps(list(proxy.tags)) if proxy.tags else None

        # Serialize error_types from metadata if present
        error_types_json = None
        if "error_types" in proxy.metadata:
            error_types_json = json.dumps(proxy.metadata["error_types"])

        # Serialize health_status_transitions from metadata if present
        health_status_transitions_json = None
        if "health_status_transitions" in proxy.metadata:
            health_status_transitions_json = json.dumps(proxy.metadata["health_status_transitions"])

        # Encrypt credentials before storage
        username_raw = proxy.username.get_secret_value() if proxy.username else None
        password_raw = proxy.password.get_secret_value() if proxy.password else None

        return ProxyTable(
            # Primary and Secondary Keys
            url=proxy.url,
            id=str(proxy.id),
            # Core Fields
            protocol=proxy.protocol,
            username=self._encrypt_credential(username_raw),
            password=self._encrypt_credential(password_raw),
            # Health Status
            health_status=proxy.health_status.value,
            last_success_at=proxy.last_success_at,
            last_failure_at=proxy.last_failure_at,
            last_health_check=proxy.last_health_check,
            last_health_error=proxy.last_health_error,
            total_checks=proxy.total_checks,
            total_health_failures=proxy.total_health_failures,
            consecutive_successes=proxy.consecutive_successes,
            consecutive_failures=proxy.consecutive_failures,
            recovery_attempt=proxy.recovery_attempt,
            next_check_time=proxy.next_check_time,
            last_recovered_at=proxy.metadata.get("last_recovered_at"),
            revival_attempts=proxy.metadata.get("revival_attempts", 0),
            health_status_transitions_json=health_status_transitions_json,
            # Request Tracking
            requests_started=proxy.requests_started,
            requests_completed=proxy.requests_completed,
            requests_active=proxy.requests_active,
            total_requests=proxy.total_requests,
            total_successes=proxy.total_successes,
            total_failures=proxy.total_failures,
            # Response Time Metrics
            average_response_time_ms=proxy.average_response_time_ms,
            ema_response_time_ms=proxy.ema_response_time_ms,
            ema_alpha=proxy.ema_alpha,
            response_time_p50_ms=proxy.metadata.get("response_time_p50_ms"),
            response_time_p95_ms=proxy.metadata.get("response_time_p95_ms"),
            response_time_p99_ms=proxy.metadata.get("response_time_p99_ms"),
            min_response_time_ms=proxy.metadata.get("min_response_time_ms"),
            max_response_time_ms=proxy.metadata.get("max_response_time_ms"),
            response_time_stddev_ms=proxy.metadata.get("response_time_stddev_ms"),
            response_samples_count=proxy.metadata.get("response_samples_count", 0),
            # Error Tracking
            error_types_json=error_types_json,
            last_error_type=proxy.metadata.get("last_error_type"),
            last_error_message=proxy.metadata.get("last_error_message"),
            last_error_at=proxy.metadata.get("last_error_at"),
            timeout_count=proxy.metadata.get("timeout_count", 0),
            connection_refused_count=proxy.metadata.get("connection_refused_count", 0),
            ssl_error_count=proxy.metadata.get("ssl_error_count", 0),
            http_4xx_count=proxy.metadata.get("http_4xx_count", 0),
            http_5xx_count=proxy.metadata.get("http_5xx_count", 0),
            # Sliding Window
            window_start=proxy.window_start,
            window_duration_seconds=proxy.window_duration_seconds,
            # Geographic
            country_code=proxy.country_code,
            country_name=proxy.metadata.get("country_name"),
            region=proxy.region,
            city=proxy.metadata.get("city"),
            isp_name=proxy.metadata.get("isp_name"),
            asn=proxy.metadata.get("asn"),
            is_residential=proxy.metadata.get("is_residential"),
            is_datacenter=proxy.metadata.get("is_datacenter"),
            is_vpn=proxy.metadata.get("is_vpn"),
            is_tor=proxy.metadata.get("is_tor"),
            latitude=proxy.metadata.get("latitude"),
            longitude=proxy.metadata.get("longitude"),
            # Protocol Support
            http_version=proxy.metadata.get("http_version"),
            tls_version=proxy.metadata.get("tls_version"),
            supports_https=proxy.metadata.get("supports_https"),
            supports_connect=proxy.metadata.get("supports_connect"),
            supports_http2=proxy.metadata.get("supports_http2"),
            # Source Metadata
            source=proxy.source.value,
            source_url=str(proxy.source_url) if proxy.source_url else None,
            source_name=proxy.metadata.get("source_name"),
            fetch_timestamp=proxy.metadata.get("fetch_timestamp"),
            fetch_duration_ms=proxy.metadata.get("fetch_duration_ms"),
            last_validation_time=proxy.metadata.get("last_validation_time"),
            validation_method=proxy.metadata.get("validation_method"),
            # Tags & TTL
            tags_json=tags_json,
            ttl=proxy.ttl,
            expires_at=proxy.expires_at,
            # Metadata
            metadata_json=json.dumps(proxy.metadata),
            created_at=proxy.created_at,
            updated_at=proxy.updated_at,
        )

    async def save(self, proxies: list[Proxy]) -> None:
        """Save proxies to database with automatic upsert.

        Existing proxies (matching URL) will be updated, new proxies will be inserted.
        Uses a delete + insert pattern with batch operations for optimal performance.
        All operations happen within a transaction.

        Performance: Uses batch DELETE and INSERT operations for significantly improved
        performance with large proxy pools.

        Args:
            proxies: List of proxies to save. Empty list is allowed (no-op).

        Raises:
            Exception: If save operation fails (transaction will be rolled back)
        """
        from sqlmodel import delete
        from sqlmodel.ext.asyncio.session import AsyncSession

        if not proxies:
            # No-op for empty list
            return

        async with AsyncSession(self.engine) as session:
            # Batch delete existing proxies with same URLs (simple upsert)
            urls = [proxy.url for proxy in proxies]
            stmt = delete(ProxyTable).where(ProxyTable.url.in_(urls))  # type: ignore[attr-defined]
            await session.exec(stmt)

            # Batch insert all new proxies using add_all
            proxy_rows = [self._proxy_to_table(proxy) for proxy in proxies]
            session.add_all(proxy_rows)

            await session.commit()

    async def load(self) -> list[Proxy]:
        """Load all proxies from database.

        Retrieves all proxy records and converts them to Proxy objects.
        Returns an empty list if no proxies are stored.

        Returns:
            List of all proxies in the database (may be empty)

        Raises:
            Exception: If load operation fails
        """
        stmt = select(ProxyTable)
        proxy_rows = await self._execute_query(stmt)
        return self._process_results(proxy_rows)

    def _build_filters(self, **filters: str) -> list[sa.ColumnElement[bool]]:
        """Build SQLAlchemy filter conditions from keyword arguments.

        Args:
            **filters: Filter criteria (source, health_status, etc.)

        Returns:
            List of SQLAlchemy filter conditions
        """
        conditions: list[sa.ColumnElement[bool]] = []

        if "source" in filters:
            conditions.append(ProxyTable.source == filters["source"])  # type: ignore[arg-type]
        if "health_status" in filters:
            conditions.append(ProxyTable.health_status == filters["health_status"])  # type: ignore[arg-type]

        return conditions

    def _build_query(self, filters: list[sa.ColumnElement[bool]]) -> sa.Select[tuple[ProxyTable]]:
        """Construct the SELECT statement with filters.

        Args:
            filters: List of SQLAlchemy filter conditions

        Returns:
            SQLAlchemy SELECT statement
        """
        stmt = select(ProxyTable)
        for condition in filters:
            stmt = stmt.where(condition)
        return stmt

    async def _execute_query(self, stmt: sa.Select[tuple[ProxyTable]]) -> list[ProxyTable]:
        """Execute the query asynchronously.

        Args:
            stmt: SQLAlchemy SELECT statement

        Returns:
            List of ProxyTable rows
        """
        from sqlmodel.ext.asyncio.session import AsyncSession

        async with AsyncSession(self.engine) as session:
            result = await session.exec(stmt)  # type: ignore[arg-type]
            return result.all()

    def _restore_health_metadata(self, row: ProxyTable, metadata: dict[str, object]) -> None:
        """Restore health status fields from ProxyTable into metadata.

        Args:
            row: Database row
            metadata: Metadata dictionary to update (modified in-place)
        """
        if row.last_recovered_at:
            metadata["last_recovered_at"] = row.last_recovered_at
        if row.revival_attempts:
            metadata["revival_attempts"] = row.revival_attempts
        if row.health_status_transitions_json:
            metadata["health_status_transitions"] = json.loads(row.health_status_transitions_json)

    def _restore_response_time_metadata(self, row: ProxyTable, metadata: dict[str, object]) -> None:
        """Restore response time metrics from ProxyTable into metadata.

        Args:
            row: Database row
            metadata: Metadata dictionary to update (modified in-place)
        """
        if row.response_time_p50_ms is not None:
            metadata["response_time_p50_ms"] = row.response_time_p50_ms
        if row.response_time_p95_ms is not None:
            metadata["response_time_p95_ms"] = row.response_time_p95_ms
        if row.response_time_p99_ms is not None:
            metadata["response_time_p99_ms"] = row.response_time_p99_ms
        if row.min_response_time_ms is not None:
            metadata["min_response_time_ms"] = row.min_response_time_ms
        if row.max_response_time_ms is not None:
            metadata["max_response_time_ms"] = row.max_response_time_ms
        if row.response_time_stddev_ms is not None:
            metadata["response_time_stddev_ms"] = row.response_time_stddev_ms
        if row.response_samples_count:
            metadata["response_samples_count"] = row.response_samples_count

    def _restore_error_metadata(self, row: ProxyTable, metadata: dict[str, object]) -> None:
        """Restore error tracking fields from ProxyTable into metadata.

        Args:
            row: Database row
            metadata: Metadata dictionary to update (modified in-place)
        """
        if row.error_types_json:
            metadata["error_types"] = json.loads(row.error_types_json)
        if row.last_error_type:
            metadata["last_error_type"] = row.last_error_type
        if row.last_error_message:
            metadata["last_error_message"] = row.last_error_message
        if row.last_error_at:
            metadata["last_error_at"] = row.last_error_at
        if row.timeout_count:
            metadata["timeout_count"] = row.timeout_count
        if row.connection_refused_count:
            metadata["connection_refused_count"] = row.connection_refused_count
        if row.ssl_error_count:
            metadata["ssl_error_count"] = row.ssl_error_count
        if row.http_4xx_count:
            metadata["http_4xx_count"] = row.http_4xx_count
        if row.http_5xx_count:
            metadata["http_5xx_count"] = row.http_5xx_count

    def _restore_location_info(self, row: ProxyTable, metadata: dict[str, object]) -> None:
        """Restore location information from ProxyTable into metadata.

        Args:
            row: Database row
            metadata: Metadata dictionary to update (modified in-place)
        """
        if row.country_name:
            metadata["country_name"] = row.country_name
        if row.city:
            metadata["city"] = row.city
        if row.isp_name:
            metadata["isp_name"] = row.isp_name
        if row.asn is not None:
            metadata["asn"] = row.asn

    def _restore_ip_classification(self, row: ProxyTable, metadata: dict[str, object]) -> None:
        """Restore IP classification flags from ProxyTable into metadata.

        Args:
            row: Database row
            metadata: Metadata dictionary to update (modified in-place)
        """
        if row.is_residential is not None:
            metadata["is_residential"] = row.is_residential
        if row.is_datacenter is not None:
            metadata["is_datacenter"] = row.is_datacenter
        if row.is_vpn is not None:
            metadata["is_vpn"] = row.is_vpn
        if row.is_tor is not None:
            metadata["is_tor"] = row.is_tor

    def _restore_coordinates(self, row: ProxyTable, metadata: dict[str, object]) -> None:
        """Restore geographic coordinates from ProxyTable into metadata.

        Args:
            row: Database row
            metadata: Metadata dictionary to update (modified in-place)
        """
        if row.latitude is not None:
            metadata["latitude"] = row.latitude
        if row.longitude is not None:
            metadata["longitude"] = row.longitude

    def _restore_geographic_metadata(self, row: ProxyTable, metadata: dict[str, object]) -> None:
        """Restore geographic fields from ProxyTable into metadata.

        This method coordinates restoration of all geographic information including
        location details, IP classification, and coordinates.

        Args:
            row: Database row
            metadata: Metadata dictionary to update (modified in-place)
        """
        self._restore_location_info(row, metadata)
        self._restore_ip_classification(row, metadata)
        self._restore_coordinates(row, metadata)

    def _restore_protocol_metadata(self, row: ProxyTable, metadata: dict[str, object]) -> None:
        """Restore protocol support fields from ProxyTable into metadata.

        Args:
            row: Database row
            metadata: Metadata dictionary to update (modified in-place)
        """
        if row.http_version:
            metadata["http_version"] = row.http_version
        if row.tls_version:
            metadata["tls_version"] = row.tls_version
        if row.supports_https is not None:
            metadata["supports_https"] = row.supports_https
        if row.supports_connect is not None:
            metadata["supports_connect"] = row.supports_connect
        if row.supports_http2 is not None:
            metadata["supports_http2"] = row.supports_http2

    def _restore_source_metadata(self, row: ProxyTable, metadata: dict[str, object]) -> None:
        """Restore source metadata fields from ProxyTable into metadata.

        Args:
            row: Database row
            metadata: Metadata dictionary to update (modified in-place)
        """
        if row.source_name:
            metadata["source_name"] = row.source_name
        if row.fetch_timestamp:
            metadata["fetch_timestamp"] = row.fetch_timestamp
        if row.fetch_duration_ms is not None:
            metadata["fetch_duration_ms"] = row.fetch_duration_ms
        if row.last_validation_time:
            metadata["last_validation_time"] = row.last_validation_time
        if row.validation_method:
            metadata["validation_method"] = row.validation_method

    def _enrich_metadata(self, row: ProxyTable, metadata: dict[str, object]) -> None:
        """Enrich metadata with all fields from ProxyTable.

        This method coordinates the restoration of all metadata categories.

        Args:
            row: Database row
            metadata: Metadata dictionary to update (modified in-place)
        """
        self._restore_health_metadata(row, metadata)
        self._restore_response_time_metadata(row, metadata)
        self._restore_error_metadata(row, metadata)
        self._restore_geographic_metadata(row, metadata)
        self._restore_protocol_metadata(row, metadata)
        self._restore_source_metadata(row, metadata)

    def _build_proxy_data(
        self, row: ProxyTable, tags: set[str], metadata: dict[str, object]
    ) -> dict[str, object]:
        """Build proxy data dictionary from database row.

        Args:
            row: Database row
            tags: Deserialized tags set
            metadata: Enriched metadata dictionary

        Returns:
            Dictionary ready for Proxy.model_validate
        """
        return {
            # Primary and Secondary Keys
            "id": row.id if row.id else None,
            "url": row.url,
            # Core Fields
            "protocol": row.protocol,
            "username": self._decrypt_credential(row.username),
            "password": self._decrypt_credential(row.password),
            # Health Status
            "health_status": row.health_status,
            "last_success_at": row.last_success_at,
            "last_failure_at": row.last_failure_at,
            "last_health_check": row.last_health_check,
            "last_health_error": row.last_health_error,
            "total_checks": row.total_checks,
            "total_health_failures": row.total_health_failures,
            "consecutive_successes": row.consecutive_successes,
            "consecutive_failures": row.consecutive_failures,
            "recovery_attempt": row.recovery_attempt,
            "next_check_time": row.next_check_time,
            # Request Tracking
            "requests_started": row.requests_started,
            "requests_completed": row.requests_completed,
            "requests_active": row.requests_active,
            "total_requests": row.total_requests,
            "total_successes": row.total_successes,
            "total_failures": row.total_failures,
            # Response Time Metrics
            "average_response_time_ms": row.average_response_time_ms,
            "ema_response_time_ms": row.ema_response_time_ms,
            "ema_alpha": row.ema_alpha,
            # Sliding Window
            "window_start": row.window_start,
            "window_duration_seconds": row.window_duration_seconds,
            # Geographic
            "country_code": row.country_code,
            "region": row.region,
            # Source Metadata
            "source": row.source,
            "source_url": row.source_url,
            # Tags & TTL
            "tags": tags,
            "ttl": row.ttl,
            "expires_at": row.expires_at,
            # Metadata (now enriched with all ProxyTable fields)
            "metadata": metadata,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    def _validate_row_id(self, row: ProxyTable) -> str | None:
        """Validate that row.id is a valid UUID string.

        Args:
            row: Database row to validate

        Returns:
            Valid UUID string or None if invalid/missing

        Note:
            Logs warnings for invalid IDs to help identify data integrity issues.
        """
        if row.id is None:
            logger.warning(f"Proxy row has no ID (url={row.url}). A new UUID will be generated.")
            return None

        try:
            # Validate UUID format by parsing it
            UUID(row.id)
            return row.id
        except (ValueError, TypeError) as e:
            logger.error(
                f"Invalid UUID format in database row (id={row.id!r}, url={row.url}): {e}. "
                "A new UUID will be generated."
            )
            return None

    def _convert_row_to_proxy(self, row: ProxyTable) -> Proxy:
        """Convert a single ProxyTable row to Proxy object.

        Args:
            row: Database row to convert

        Returns:
            Proxy object
        """
        # Validate row ID before conversion
        validated_id = self._validate_row_id(row)

        # Deserialize tags from JSON
        tags = set(json.loads(row.tags_json)) if row.tags_json else set()

        # Deserialize and enrich metadata
        metadata: dict[str, object] = json.loads(row.metadata_json)
        self._enrich_metadata(row, metadata)

        # Build proxy data and validate
        proxy_data = self._build_proxy_data(row, tags, metadata)
        # Override the id with validated value if valid; if None, Pydantic will use default_factory
        if validated_id is not None:
            proxy_data["id"] = validated_id
        else:
            # Remove id from proxy_data to allow Pydantic's default_factory=uuid4 to generate a new UUID
            proxy_data.pop("id", None)
        return Proxy.model_validate(proxy_data)

    def _process_results(self, rows: list[ProxyTable]) -> list[Proxy]:
        """Convert ProxyTable rows to Proxy objects.

        Args:
            rows: List of ProxyTable rows from database

        Returns:
            List of Proxy objects
        """
        return [self._convert_row_to_proxy(row) for row in rows]

    async def query(self, **filters: str) -> list[Proxy]:
        """Query proxies with advanced filtering capabilities.

        Supports filtering by any indexed field. Multiple filters are combined
        with AND logic. Returns an empty list if no proxies match.

        Supported filters:
            - source: Filter by proxy source (e.g., "user", "fetched", "api")
            - health_status: Filter by health status (e.g., "healthy", "unhealthy")

        Args:
            **filters: Keyword arguments for filter criteria.
                Example: query(source="user", health_status="healthy")

        Returns:
            List of proxies matching all filter criteria (may be empty)

        Raises:
            Exception: If query operation fails
        """
        filter_conditions = self._build_filters(**filters)
        stmt = self._build_query(filter_conditions)
        proxy_rows = await self._execute_query(stmt)
        return self._process_results(proxy_rows)

    async def delete(self, proxy_url: str) -> None:
        """Delete a proxy by URL.

        Args:
            proxy_url: URL of the proxy to delete
        """
        from sqlmodel import delete
        from sqlmodel.ext.asyncio.session import AsyncSession

        async with AsyncSession(self.engine) as session:
            stmt = delete(ProxyTable).where(ProxyTable.url == proxy_url)  # type: ignore[arg-type]
            await session.exec(stmt)
            await session.commit()

    async def clear(self) -> None:
        """Clear all proxies from database."""
        from sqlmodel import delete
        from sqlmodel.ext.asyncio.session import AsyncSession

        async with AsyncSession(self.engine) as session:
            stmt = delete(ProxyTable)
            await session.exec(stmt)
            await session.commit()

    async def load_validated(self, max_age_hours: int = 48) -> list[Proxy]:
        """Load only proxies that were validated within the given time window.

        This method filters out stale proxies that haven't been successfully
        validated recently. Essential for exports to ensure only working
        proxies are included.

        Args:
            max_age_hours: Maximum age in hours for last_success_at.
                Proxies older than this will be excluded. Default: 48 hours.

        Returns:
            List of proxies with recent last_success_at timestamps
        """
        from datetime import timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        stmt = select(ProxyTable).where(
            ProxyTable.last_success_at.isnot(None),  # type: ignore[union-attr]
            ProxyTable.last_success_at >= cutoff,  # type: ignore[operator]
        )
        proxy_rows = await self._execute_query(stmt)
        return self._process_results(proxy_rows)
