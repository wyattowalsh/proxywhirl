"""Storage backends for persisting proxy pools."""

from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import aiofiles
from cryptography.fernet import Fernet
from loguru import logger
from pydantic import SecretStr
from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from proxywhirl.cache.crypto import CredentialEncryptor
from proxywhirl.models import Proxy

# Prefix for encrypted credentials stored as strings
_ENCRYPTED_PREFIX = "encrypted:"


class ProxyIdentityTable(SQLModel, table=True):
    """Immutable proxy identity table (normalized schema).

    This table stores the core identity of each proxy, with fields that
    rarely change. Geographic and source metadata are stored here.

    Primary Key:
        url: Full proxy URL (e.g., "http://1.2.3.4:8080")

    Indexes:
        - protocol: Fast filtering by protocol type
        - host_port: Unique constraint to prevent duplicates
        - country_code: Geographic filtering
        - source: Source-based queries
    """

    __tablename__: str = "proxy_identities"  # type: ignore[misc]

    url: str = Field(primary_key=True)
    protocol: str = Field(index=True)  # http, https, socks4, socks5
    host: str = Field(index=True)
    port: int
    username: str | None = None
    password: str | None = None  # Encrypted at app level

    # Geographic (immutable per IP)
    country_code: str | None = Field(default=None, index=True)
    country_name: str | None = None
    region: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    asn: int | None = None
    isp_name: str | None = None
    is_residential: bool = False
    is_datacenter: bool = False

    # Source metadata
    source: str = Field(default="fetched", index=True)
    source_url: str | None = None
    discovered_at: datetime = Field(
        default_factory=lambda: datetime.now(__import__("datetime").timezone.utc)
    )
    expires_at: datetime | None = Field(default=None, index=True)


class ValidationResultTable(SQLModel, table=True):
    """Individual validation result table (append-only).

    Stores each validation attempt as an immutable record.
    This enables historical analysis and trend tracking.

    Indexes:
        - proxy_url + validated_at: Fast lookup of recent validations
        - validated_at: Time-range queries
        - is_valid + validated_at: Finding recent valid proxies
    """

    __tablename__: str = "validation_results"  # type: ignore[misc]

    id: int | None = Field(default=None, primary_key=True)
    proxy_url: str = Field(index=True, foreign_key="proxy_identities.url")
    validated_at: datetime = Field(
        default_factory=lambda: datetime.now(__import__("datetime").timezone.utc),
        index=True,
    )
    is_valid: bool
    response_time_ms: float | None = None
    error_type: str | None = None  # timeout, connection_refused, ssl_error, etc.
    error_message: str | None = None


class ProxyStatusTable(SQLModel, table=True):
    """Current computed status table (normalized schema).

    This table maintains the current state of each proxy, computed
    from validation results. It's updated after each validation.

    Primary Key:
        proxy_url: References proxy_identities.url

    Indexes:
        - health_status: Filter by current health
        - last_success_at: Find recently working proxies
        - success_rate_7d: Performance-based sorting
    """

    __tablename__: str = "proxy_statuses"  # type: ignore[misc]

    proxy_url: str = Field(primary_key=True, foreign_key="proxy_identities.url")
    health_status: str = Field(default="unknown", index=True)  # healthy, unhealthy, dead, unknown
    last_success_at: datetime | None = Field(default=None, index=True)
    last_failure_at: datetime | None = None
    last_check_at: datetime | None = Field(default=None, index=True)
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    total_checks: int = 0
    total_successes: int = 0
    avg_response_time_ms: float | None = None
    success_rate_7d: float | None = Field(default=None, index=True)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(__import__("datetime").timezone.utc),
        index=True,
    )


class ProxyAuditTable(SQLModel, table=True):
    """Audit trail for proxy changes.

    Tracks INSERT, UPDATE, and DELETE operations on proxies
    for compliance and debugging purposes.
    """

    __tablename__: str = "proxies_audit"  # type: ignore[misc]

    id: int | None = Field(default=None, primary_key=True)
    proxy_url: str = Field(index=True)
    action: str  # INSERT, UPDATE, DELETE
    old_values: str | None = None  # JSON
    new_values: str | None = None  # JSON
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(__import__("datetime").timezone.utc),
        index=True,
    )


class FileStorage:
    """File-based storage backend using JSON with optional encryption.

    Stores proxies in a JSON file with atomic writes to prevent corruption.
    Supports optional Fernet encryption for sensitive credential data.
    All writes are atomic using temp files to ensure data consistency.

    Attributes:
        filepath: Path to the JSON storage file
        encryption_key: Optional Fernet encryption key (bytes)
        _cipher: Fernet cipher instance for encryption/decryption
    """

    def __init__(self, filepath: str | Path, encryption_key: bytes | None = None) -> None:
        """
        Initialize file storage with optional encryption.

        Creates a new file storage instance. If encryption_key is provided,
        all data is encrypted at rest using Fernet symmetric encryption.

        Args:
            filepath : str | Path
                Path to the JSON file for storage. Parent directories are
                created automatically on first save.
            encryption_key : bytes | None
                Optional Fernet encryption key for encrypting credentials.
                If provided, all data is encrypted at rest. To generate:
                `key = Fernet.generate_key()`. Default: None (no encryption).

        Returns:
            None

        Raises:
            cryptography.fernet.InvalidToken
                If encryption_key is invalid Fernet key format.

        Example:
            >>> from cryptography.fernet import Fernet
            >>> key = Fernet.generate_key()
            >>> storage = FileStorage("proxies.json", encryption_key=key)
            >>> # Or without encryption:
            >>> storage = FileStorage("proxies.json")
        """
        self.filepath = Path(filepath)
        self.encryption_key = encryption_key
        self._cipher = Fernet(encryption_key) if encryption_key else None

    async def save(self, proxies: list[Proxy]) -> None:
        """
        Save proxies to JSON file with atomic writes and optional encryption.

        Serializes proxy list to JSON and writes atomically using a temp file.
        Credentials (username/password) are revealed and stored as strings.
        If encryption is configured, the entire JSON is encrypted before writing.

        Args:
            proxies : list[Proxy]
                List of Proxy objects to save.

        Returns:
            None

        Raises:
            OSError
                If file write fails or parent directory cannot be created.

        Example:
            >>> from proxywhirl.models import Proxy
            >>> proxies = [
            ...     Proxy(url="http://1.2.3.4:8080"),
            ...     Proxy(url="http://5.6.7.8:9090", username="user", password="pass"),
            ... ]
            >>> storage = FileStorage("proxies.json")
            >>> await storage.save(proxies)

        Note:
            - Atomic writes prevent corruption on concurrent writes
            - SecretStr credentials are revealed for storage
            - Encryption is applied at the entire file level
            - Parent directories are created automatically
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
        """
        Load proxies from JSON file with optional decryption.

        Reads JSON file, decrypts if encryption is configured, and deserializes
        to Proxy objects. Validates all proxy data during deserialization.

        Args:
            None

        Returns:
            list[Proxy]
                List of Proxy objects loaded from file.

        Raises:
            FileNotFoundError
                If storage file does not exist.
            ValueError
                If JSON is invalid or proxy data fails validation.
            cryptography.fernet.InvalidToken
                If decryption fails (wrong encryption key or corrupted data).

        Example:
            >>> storage = FileStorage("proxies.json")
            >>> proxies = await storage.load()
            >>> for proxy in proxies:
            ...     print(proxy.url)

        Note:
            - Validates all proxy data during deserialization
            - Credentials are loaded as SecretStr (redacted in logs)
            - Empty file raises FileNotFoundError
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
        """
        Clear all proxies from storage by deleting the file.

        Removes the storage file completely. Subsequent loads will fail
        with FileNotFoundError until new data is saved.

        Args:
            None

        Returns:
            None

        Raises:
            OSError
                If file deletion fails.

        Example:
            >>> storage = FileStorage("proxies.json")
            >>> await storage.clear()  # File is deleted
        """
        try:
            if self.filepath.exists():
                self.filepath.unlink()
        except Exception as e:
            raise OSError(f"Failed to clear storage: {e}") from e


class SQLiteStorage:
    """SQLite-based storage backend with normalized 3-table schema.

    Uses a normalized schema for efficient storage and querying:
        - proxy_identities: Immutable proxy identity (URL, host, port, geo)
        - proxy_statuses: Current computed status (health, response times)
        - validation_results: Append-only validation history

    Features:
        - Async operations using aiosqlite for non-blocking I/O
        - Normalized schema prevents SQL variable overflow
        - Advanced filtering by health_status, protocol, country
        - Automatic schema creation
        - EMA-based response time tracking
        - Health status state machine (unknown → healthy/unhealthy/dead)

    Example::

        storage = SQLiteStorage("proxies.db")
        await storage.initialize()

        # Add proxies
        await storage.add_proxy(proxy)
        added, skipped = await storage.add_proxies_batch(proxies)

        # Record validation results
        await storage.record_validation(proxy_url, is_valid=True, response_time_ms=150)

        # Query proxies
        healthy = await storage.get_healthy_proxies(max_age_hours=48)
        dead = await storage.get_proxies_by_status("dead")

        # Cleanup and stats
        counts = await storage.cleanup(remove_dead=True, remove_stale_days=7)
        stats = await storage.get_stats()

        await storage.close()
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
            pool_size=10,
        )

        # Slow query logging threshold (milliseconds)
        self._slow_query_threshold_ms: float = 100.0

        # Initialize credential encryptor for secure credential storage
        self._encryptor: CredentialEncryptor | None = None
        self._init_encryptor()

        # Statistics cache (avoid repeated expensive aggregation queries)
        self._stats_cache: dict[str, Any] | None = None
        self._stats_cache_time: datetime | None = None
        self._stats_cache_ttl: timedelta = timedelta(seconds=30)  # Cache for 30 seconds

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

    async def _timed_exec(self, session: AsyncSession, statement: Any) -> Any:
        """Execute a session statement with slow query logging."""
        start = time.monotonic()
        result = await session.exec(statement)
        elapsed_ms = (time.monotonic() - start) * 1000
        if elapsed_ms > self._slow_query_threshold_ms:
            logger.warning(
                f"Slow query ({elapsed_ms:.1f}ms): {str(statement)[:200]}"
            )
        return result

    async def _timed_conn_execute(self, conn: Any, statement: Any) -> Any:
        """Execute a connection statement with slow query logging."""
        start = time.monotonic()
        result = await conn.execute(statement)
        elapsed_ms = (time.monotonic() - start) * 1000
        if elapsed_ms > self._slow_query_threshold_ms:
            logger.warning(
                f"Slow query ({elapsed_ms:.1f}ms): {str(statement)[:200]}"
            )
        return result

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
        """Create normalized database tables if they don't exist.

        Should be called once before any other operations. Creates the normalized
        identity, status, and validation tables. Safe to call multiple times:
        existing tables, including legacy application tables, are preserved.

        Optimizations:
            - Enable WAL mode for concurrent read/write access
            - Enable FOREIGN_KEYS for referential integrity
            - Optimize PRAGMA settings (synchronous, cache_size, temp_store)
            - Create composite and single-column indexes for hot queries

        Raises:
            Exception: If database initialization fails
        """
        from sqlmodel import SQLModel

        async with self.engine.begin() as conn:
            # Enable WAL mode for concurrent reads/writes
            await self._timed_conn_execute(conn, text("PRAGMA journal_mode = WAL"))

            # Enable FOREIGN_KEYS constraint enforcement
            await self._timed_conn_execute(conn, text("PRAGMA foreign_keys = ON"))

            # Optimize synchronous mode: NORMAL balances safety and performance
            await self._timed_conn_execute(conn, text("PRAGMA synchronous = NORMAL"))

            # Increase cache_size to reduce disk I/O (negative = MB)
            await self._timed_conn_execute(conn, text("PRAGMA cache_size = -65536"))  # 64MB cache

            # Use memory for temporary tables (faster)
            await self._timed_conn_execute(conn, text("PRAGMA temp_store = MEMORY"))

            # Create all tables
            await conn.run_sync(SQLModel.metadata.create_all)

            # Create composite and specialized indexes for hot queries
            # Index on (proxy_id, timestamp) for metrics queries
            await self._timed_conn_execute(
                conn,
                text(
                    "CREATE INDEX IF NOT EXISTS idx_validation_proxy_time "
                    "ON validation_results(proxy_url, validated_at)"
                ),
            )

            # Index on cache expiration for TTL cleanup
            # This is for future cache TTL table if implemented

            # Index on health_status for filtering healthy/unhealthy proxies
            await self._timed_conn_execute(
                conn,
                text(
                    "CREATE INDEX IF NOT EXISTS idx_proxy_status_health "
                    "ON proxy_statuses(health_status, last_success_at DESC)"
                ),
            )

            # Index on URL for duplicate detection
            await self._timed_conn_execute(
                conn,
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_proxy_identity_url "
                    "ON proxy_identities(url)"
                ),
            )

            # Index on success_rate_7d for performance-based sorting
            await self._timed_conn_execute(
                conn,
                text(
                    "CREATE INDEX IF NOT EXISTS idx_proxy_status_success_rate "
                    "ON proxy_statuses(success_rate_7d DESC)"
                ),
            )

            # Index on validation results by validity and recency
            await self._timed_conn_execute(
                conn,
                text(
                    "CREATE INDEX IF NOT EXISTS idx_validation_recent_valid "
                    "ON validation_results(is_valid, validated_at DESC)"
                ),
            )

            # Index on last_success_at for finding recently working proxies
            await self._timed_conn_execute(
                conn,
                text(
                    "CREATE INDEX IF NOT EXISTS idx_proxy_status_recent_success "
                    "ON proxy_statuses(last_success_at DESC)"
                ),
            )

            logger.info("Database initialized with WAL mode and optimized indexes")

    async def close(self) -> None:
        """Close database connection and release resources.

        Should be called when done with the storage to properly cleanup
        database connections. Safe to call multiple times.
        """
        await self.engine.dispose()

    async def add_proxy(self, proxy: Proxy) -> bool:
        """Add a new proxy if not exists.

        Args:
            proxy: Proxy model to add

        Returns:
            True if added, False if already exists
        """
        async with AsyncSession(self.engine) as session:
            existing = await session.get(ProxyIdentityTable, proxy.url)
            if existing:
                return False

            # Parse URL for host:port
            parsed = urlparse(proxy.url)

            row = ProxyIdentityTable(
                url=proxy.url,
                protocol=proxy.protocol or "http",
                host=parsed.hostname or "",
                port=parsed.port or 80,
                username=self._encrypt_credential(
                    proxy.username.get_secret_value() if proxy.username else None
                ),
                password=self._encrypt_credential(
                    proxy.password.get_secret_value() if proxy.password else None
                ),
                country_code=proxy.country_code,
                source=proxy.source.value if proxy.source else "fetched",
                source_url=str(proxy.source_url) if proxy.source_url else None,
            )
            session.add(row)

            # Initialize status
            status = ProxyStatusTable(proxy_url=proxy.url)
            session.add(status)

            await session.commit()
            return True

    async def add_proxies_batch(
        self, proxies: list[Proxy], validated: bool = False
    ) -> tuple[int, int]:
        """Add multiple proxies to the normalized schema using true batch operations.

        Args:
            proxies: List of Proxy models to add
            validated: If True, mark proxies as already validated (healthy status,
                last_success_at set). Use this when proxies have passed validation
                before being saved.

        Returns:
            Tuple of (added_count, skipped_count)
        """
        if not proxies:
            return 0, 0

        added = 0
        skipped = 0
        now = datetime.now(timezone.utc)

        async with AsyncSession(self.engine) as session:
            # Batch check existing proxies
            urls = [p.url for p in proxies]
            existing_stmt = select(ProxyIdentityTable.url).where(ProxyIdentityTable.url.in_(urls))
            existing_results = await session.execute(existing_stmt)
            existing_urls = {row[0] for row in existing_results}

            # Separate new and existing
            new_proxies = [p for p in proxies if p.url not in existing_urls]
            skipped = len(proxies) - len(new_proxies)

            if not new_proxies:
                return 0, skipped

            # Deduplicate by URL within the batch to avoid PK collisions
            seen_urls: set[str] = set()
            deduped_proxies: list[Proxy] = []
            for p in new_proxies:
                if p.url not in seen_urls:
                    seen_urls.add(p.url)
                    deduped_proxies.append(p)
            skipped += len(new_proxies) - len(deduped_proxies)
            new_proxies = deduped_proxies

            # Batch insert identities and statuses
            identity_rows = []
            status_rows = []

            for proxy in new_proxies:
                parsed = urlparse(proxy.url)
                identity_rows.append(
                    ProxyIdentityTable(
                        url=proxy.url,
                        protocol=proxy.protocol or "http",
                        host=parsed.hostname or "",
                        port=parsed.port or 80,
                        username=self._encrypt_credential(
                            proxy.username.get_secret_value() if proxy.username else None
                        ),
                        password=self._encrypt_credential(
                            proxy.password.get_secret_value() if proxy.password else None
                        ),
                        source=proxy.source.value if proxy.source else "fetched",
                    )
                )

                # Create status - mark as validated if proxies passed validation
                if validated:
                    status_rows.append(
                        ProxyStatusTable(
                            proxy_url=proxy.url,
                            health_status="healthy",
                            last_success_at=now,
                            last_check_at=now,
                            total_checks=1,
                            total_successes=1,
                            consecutive_successes=1,
                            avg_response_time_ms=proxy.average_response_time_ms,
                        )
                    )
                else:
                    status_rows.append(ProxyStatusTable(proxy_url=proxy.url))

            # Bulk insert
            session.add_all(identity_rows)
            session.add_all(status_rows)
            await session.commit()
            added = len(new_proxies)

        return added, skipped

    async def async_batch_insert_proxies(
        self, proxies: list[Proxy], validated: bool = False
    ) -> tuple[int, int]:
        """Async batch insert proxies with aiosqlite-style semantics.

        This is a thin wrapper around :meth:`add_proxies_batch` that provides
        the ``async_batch_insert_*`` naming convention preferred by some
        async SQLite workflows.

        Args:
            proxies: List of Proxy models to insert
            validated: If True, mark proxies as already validated

        Returns:
            Tuple of (added_count, skipped_count)
        """
        return await self.add_proxies_batch(proxies, validated=validated)

    async def save(self, proxies: list[Proxy], validated: bool = False) -> None:
        """Save proxies to database (adds new, skips existing).

        This is a compatibility wrapper around add_proxies_batch().

        Args:
            proxies: List of proxies to save. Empty list is allowed (no-op).
            validated: If True, mark proxies as already validated (healthy status).
        """
        if not proxies:
            return
        await self.add_proxies_batch(proxies, validated=validated)

    async def delete(self, proxy_url: str) -> bool:
        """Delete a proxy by URL.

        Args:
            proxy_url: URL of the proxy to delete

        Returns:
            True if deleted, False if not found
        """
        async with AsyncSession(self.engine) as session:
            # Delete from status table first
            del_status = delete(ProxyStatusTable).where(ProxyStatusTable.proxy_url == proxy_url)
            await session.exec(del_status)  # type: ignore[arg-type]

            # Delete from identity table
            del_identity = delete(ProxyIdentityTable).where(ProxyIdentityTable.url == proxy_url)
            result = await session.exec(del_identity)  # type: ignore[arg-type]
            await session.commit()

            return result.rowcount > 0 if hasattr(result, "rowcount") else True

    async def clear(self) -> None:
        """Clear all proxies from database."""
        async with AsyncSession(self.engine) as session:
            # Delete all validation results
            await session.exec(delete(ValidationResultTable))  # type: ignore[arg-type]
            # Delete all statuses
            await session.exec(delete(ProxyStatusTable))  # type: ignore[arg-type]
            # Delete all identities
            await session.exec(delete(ProxyIdentityTable))  # type: ignore[arg-type]
            await session.commit()

    async def query(self, **filters: str) -> list[dict[str, Any]]:
        """Query proxies with filtering.

        Args:
            **filters: Filter criteria (source, health_status)

        Returns:
            List of proxy dictionaries matching criteria
        """
        stmt = select(ProxyIdentityTable, ProxyStatusTable).join(
            ProxyStatusTable, ProxyIdentityTable.url == ProxyStatusTable.proxy_url
        )

        if "source" in filters:
            stmt = stmt.where(ProxyIdentityTable.source == filters["source"])
        if "health_status" in filters:
            stmt = stmt.where(ProxyStatusTable.health_status == filters["health_status"])

        async with AsyncSession(self.engine) as session:
            result = await session.exec(stmt)  # type: ignore[arg-type]
            rows = result.all()

            proxies = []
            for identity, status in rows:
                proxies.append(
                    {
                        "url": identity.url,
                        "protocol": identity.protocol,
                        "host": identity.host,
                        "port": identity.port,
                        "username": self._decrypt_credential(identity.username),
                        "password": self._decrypt_credential(identity.password),
                        "country_code": identity.country_code,
                        "source": identity.source,
                        "discovered_at": identity.discovered_at,
                        "health_status": status.health_status,
                        "last_success_at": status.last_success_at,
                        "last_failure_at": status.last_failure_at,
                        "avg_response_time_ms": status.avg_response_time_ms,
                        "total_checks": status.total_checks,
                        "total_successes": status.total_successes,
                    }
                )
            return proxies

    async def record_validation(
        self,
        proxy_url: str,
        is_valid: bool,
        response_time_ms: float | None = None,
        error_type: str | None = None,
        error_message: str | None = None,
    ) -> None:
        """Record a validation result and update proxy status.

        Args:
            proxy_url: URL of the proxy that was validated
            is_valid: Whether the validation succeeded
            response_time_ms: Response time in milliseconds (if successful)
            error_type: Type of error (if failed)
            error_message: Error message (if failed)
        """
        now = datetime.now(timezone.utc)

        async with AsyncSession(self.engine) as session:
            # Insert validation record
            validation = ValidationResultTable(
                proxy_url=proxy_url,
                validated_at=now,
                is_valid=is_valid,
                response_time_ms=response_time_ms,
                error_type=error_type,
                error_message=error_message,
            )
            session.add(validation)

            # Update status
            status = await session.get(ProxyStatusTable, proxy_url)
            if status:
                status.last_check_at = now
                status.total_checks += 1
                status.updated_at = now

                if is_valid:
                    status.last_success_at = now
                    status.total_successes += 1
                    status.consecutive_successes += 1
                    status.consecutive_failures = 0
                    status.health_status = "healthy"

                    # Update avg response time using EMA
                    if response_time_ms is not None:
                        if status.avg_response_time_ms is not None:
                            # EMA with alpha=0.2
                            status.avg_response_time_ms = (
                                0.2 * response_time_ms + 0.8 * status.avg_response_time_ms
                            )
                        else:
                            status.avg_response_time_ms = response_time_ms
                else:
                    status.last_failure_at = now
                    status.consecutive_failures += 1
                    status.consecutive_successes = 0

                    if status.consecutive_failures >= 3:
                        status.health_status = "dead"
                    elif status.consecutive_failures >= 1:
                        status.health_status = "unhealthy"

                session.add(status)

            await session.commit()

    async def record_validations_batch(
        self,
        results: list[tuple[str, bool, float | None, str | None]],
    ) -> int:
        """Record multiple validation results efficiently.

        Args:
            results: List of (proxy_url, is_valid, response_time_ms, error_type) tuples

        Returns:
            Number of validations recorded
        """
        now = datetime.now(timezone.utc)

        async with AsyncSession(self.engine) as session:
            for proxy_url, is_valid, response_time_ms, error_type in results:
                # Insert validation record
                validation = ValidationResultTable(
                    proxy_url=proxy_url,
                    validated_at=now,
                    is_valid=is_valid,
                    response_time_ms=response_time_ms,
                    error_type=error_type,
                )
                session.add(validation)

                # Update status via raw SQL for efficiency
                if is_valid:
                    await session.exec(
                        text("""
                        UPDATE proxy_statuses SET
                            last_check_at = :now,
                            last_success_at = :now,
                            total_checks = total_checks + 1,
                            total_successes = total_successes + 1,
                            consecutive_successes = consecutive_successes + 1,
                            consecutive_failures = 0,
                            health_status = 'healthy',
                            avg_response_time_ms = CASE
                                WHEN avg_response_time_ms IS NULL THEN :response_time
                                ELSE 0.2 * :response_time + 0.8 * avg_response_time_ms
                            END,
                            updated_at = :now
                        WHERE proxy_url = :url
                    """).bindparams(now=now, response_time=response_time_ms, url=proxy_url)
                    )
                else:
                    await session.exec(
                        text("""
                        UPDATE proxy_statuses SET
                            last_check_at = :now,
                            last_failure_at = :now,
                            total_checks = total_checks + 1,
                            consecutive_failures = consecutive_failures + 1,
                            consecutive_successes = 0,
                            health_status = CASE
                                WHEN consecutive_failures >= 2 THEN 'dead'
                                ELSE 'unhealthy'
                            END,
                            updated_at = :now
                        WHERE proxy_url = :url
                    """).bindparams(now=now, url=proxy_url)
                    )

            await session.commit()

        return len(results)

    async def get_healthy_proxies(
        self,
        max_age_hours: int = 48,
        protocol: str | None = None,
        country_code: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get healthy, recently validated proxies.

        Args:
            max_age_hours: Maximum age of last successful validation
            protocol: Filter by protocol (http, https, socks4, socks5)
            country_code: Filter by country code
            limit: Maximum number of proxies to return

        Returns:
            List of proxy dictionaries with identity and status fields
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        stmt = (
            select(ProxyIdentityTable, ProxyStatusTable)
            .join(ProxyStatusTable, ProxyIdentityTable.url == ProxyStatusTable.proxy_url)
            .where(ProxyStatusTable.health_status == "healthy")
            .where(ProxyStatusTable.last_success_at >= cutoff)  # type: ignore[operator]
        )

        if protocol:
            stmt = stmt.where(ProxyIdentityTable.protocol == protocol)
        if country_code:
            stmt = stmt.where(ProxyIdentityTable.country_code == country_code)

        stmt = stmt.order_by(ProxyStatusTable.avg_response_time_ms.asc().nullslast())

        if limit:
            stmt = stmt.limit(limit)

        async with AsyncSession(self.engine) as session:
            result = await session.exec(stmt)  # type: ignore[arg-type]
            rows = result.all()

            proxies = []
            for identity, status in rows:
                proxies.append(
                    {
                        "url": identity.url,
                        "protocol": identity.protocol,
                        "host": identity.host,
                        "port": identity.port,
                        "username": self._decrypt_credential(identity.username),
                        "password": self._decrypt_credential(identity.password),
                        "country_code": identity.country_code,
                        "source": identity.source,
                        "health_status": status.health_status,
                        "last_success_at": status.last_success_at,
                        "avg_response_time_ms": status.avg_response_time_ms,
                        "total_checks": status.total_checks,
                        "total_successes": status.total_successes,
                    }
                )
            return proxies

    async def get_proxies_by_status(
        self,
        health_status: str,
    ) -> list[dict[str, Any]]:
        """Get proxies by health status.

        Args:
            health_status: Filter by health status (healthy, unhealthy, dead, unknown)

        Returns:
            List of proxy dictionaries
        """
        stmt = (
            select(ProxyIdentityTable, ProxyStatusTable)
            .join(ProxyStatusTable, ProxyIdentityTable.url == ProxyStatusTable.proxy_url)
            .where(ProxyStatusTable.health_status == health_status)
        )

        async with AsyncSession(self.engine) as session:
            result = await session.exec(stmt)  # type: ignore[arg-type]
            rows = result.all()

            proxies = []
            for identity, status in rows:
                proxies.append(
                    {
                        "url": identity.url,
                        "protocol": identity.protocol,
                        "host": identity.host,
                        "port": identity.port,
                        "username": self._decrypt_credential(identity.username),
                        "password": self._decrypt_credential(identity.password),
                        "health_status": status.health_status,
                        "last_success_at": status.last_success_at,
                        "total_checks": status.total_checks,
                    }
                )
            return proxies

    async def load(self) -> list[dict[str, Any]]:
        """Load all proxies from the database.

        Returns:
            List of proxy dictionaries with identity and status fields
        """
        stmt = select(ProxyIdentityTable, ProxyStatusTable).join(
            ProxyStatusTable, ProxyIdentityTable.url == ProxyStatusTable.proxy_url
        )

        async with AsyncSession(self.engine) as session:
            result = await self._timed_exec(session, stmt)  # type: ignore[arg-type]
            rows = result.all()

            proxies = []
            for identity, status in rows:
                proxies.append(
                    {
                        "url": identity.url,
                        "protocol": identity.protocol,
                        "host": identity.host,
                        "port": identity.port,
                        "username": self._decrypt_credential(identity.username),
                        "password": self._decrypt_credential(identity.password),
                        "country_code": identity.country_code,
                        "source": identity.source,
                        "discovered_at": identity.discovered_at,
                        "health_status": status.health_status,
                        "last_success_at": status.last_success_at,
                        "last_failure_at": status.last_failure_at,
                        "avg_response_time_ms": status.avg_response_time_ms,
                        "total_checks": status.total_checks,
                        "total_successes": status.total_successes,
                    }
                )
            return proxies

    async def load_revalidation_candidates(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Load proxies for oldest-first revalidation.

        Proxies are ordered to prioritize entries that have never been checked,
        followed by the oldest previously checked proxies. This allows scheduled
        revalidation to progress incrementally across the full inventory while
        remaining deterministic across runs.

        Args:
            limit: Maximum number of proxies to return. ``None`` or values <= 0
                return the full ordered inventory.

        Returns:
            List of proxy dictionaries with identity and status fields.
        """
        stmt = (
            select(ProxyIdentityTable, ProxyStatusTable)
            .join(ProxyStatusTable, ProxyIdentityTable.url == ProxyStatusTable.proxy_url)
            .order_by(
                ProxyStatusTable.last_check_at.is_(None).desc(),
                ProxyStatusTable.last_check_at.asc().nullslast(),
                ProxyStatusTable.updated_at.asc(),
                ProxyIdentityTable.url.asc(),
            )
        )

        if limit is not None and limit > 0:
            stmt = stmt.limit(limit)

        async with AsyncSession(self.engine) as session:
            result = await session.exec(stmt)  # type: ignore[arg-type]
            rows = result.all()

            proxies = []
            for identity, status in rows:
                proxies.append(
                    {
                        "url": identity.url,
                        "protocol": identity.protocol,
                        "host": identity.host,
                        "port": identity.port,
                        "username": self._decrypt_credential(identity.username),
                        "password": self._decrypt_credential(identity.password),
                        "country_code": identity.country_code,
                        "source": identity.source,
                        "discovered_at": identity.discovered_at,
                        "health_status": status.health_status,
                        "last_check_at": status.last_check_at,
                        "last_success_at": status.last_success_at,
                        "last_failure_at": status.last_failure_at,
                        "avg_response_time_ms": status.avg_response_time_ms,
                        "total_checks": status.total_checks,
                        "total_successes": status.total_successes,
                        "updated_at": status.updated_at,
                    }
                )
            return proxies

    async def load_validated(self, max_age_hours: int = 48) -> list[dict[str, Any]]:
        """Load proxies validated within the given time window, excluding dead proxies.

        Args:
            max_age_hours: Maximum age in hours for last_success_at.
                Proxies older than this will be excluded. Default: 48 hours.

        Returns:
            List of proxy dictionaries with recent validations
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        stmt = (
            select(ProxyIdentityTable, ProxyStatusTable)
            .join(ProxyStatusTable, ProxyIdentityTable.url == ProxyStatusTable.proxy_url)
            .where(ProxyStatusTable.last_success_at.isnot(None))  # type: ignore[union-attr]
            .where(ProxyStatusTable.last_success_at >= cutoff)  # type: ignore[operator]
            .where(ProxyStatusTable.health_status == "healthy")
        )

        async with AsyncSession(self.engine) as session:
            result = await session.exec(stmt)  # type: ignore[arg-type]
            rows = result.all()

            proxies = []
            for identity, status in rows:
                proxies.append(
                    {
                        "url": identity.url,
                        "protocol": identity.protocol,
                        "host": identity.host,
                        "port": identity.port,
                        "username": self._decrypt_credential(identity.username),
                        "password": self._decrypt_credential(identity.password),
                        "country_code": identity.country_code,
                        "source": identity.source,
                        "discovered_at": identity.discovered_at,
                        "health_status": status.health_status,
                        "last_success_at": status.last_success_at,
                        "last_failure_at": status.last_failure_at,
                        "avg_response_time_ms": status.avg_response_time_ms,
                        "total_checks": status.total_checks,
                        "total_successes": status.total_successes,
                    }
                )
            return proxies

    async def cleanup(
        self,
        remove_dead: bool = True,
        remove_stale_days: int = 7,
        remove_never_validated: bool = True,
        vacuum: bool = True,
    ) -> dict[str, int]:
        """Clean up stale and dead proxies.

        Args:
            remove_dead: Remove proxies with health_status='dead'
            remove_stale_days: Remove proxies not validated in N days (0 to skip)
            remove_never_validated: Remove proxies that have never been validated
            vacuum: Run VACUUM after cleanup to reclaim space

        Returns:
            dict[str, int]: Counts of removed items by category (dead, stale, never_validated).
        """
        counts: dict[str, int] = {}

        async with AsyncSession(self.engine) as session:
            # Remove dead proxies
            if remove_dead:
                # Get URLs of dead proxies
                dead_stmt = select(ProxyStatusTable.proxy_url).where(
                    ProxyStatusTable.health_status == "dead"
                )
                dead_result = await session.exec(dead_stmt)
                dead_urls = list(dead_result.all())

                if dead_urls:
                    # Delete from validation_results first (FK constraint)
                    del_validation = delete(ValidationResultTable).where(
                        ValidationResultTable.proxy_url.in_(dead_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_validation)  # type: ignore[arg-type]

                    # Delete from status table (FK constraint)
                    del_status = delete(ProxyStatusTable).where(
                        ProxyStatusTable.proxy_url.in_(dead_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_status)  # type: ignore[arg-type]

                    # Delete from proxy_identities
                    del_stmt = delete(ProxyIdentityTable).where(
                        ProxyIdentityTable.url.in_(dead_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_stmt)  # type: ignore[arg-type]
                    counts["dead"] = len(dead_urls)
                else:
                    counts["dead"] = 0

            # Remove stale proxies (not validated recently)
            if remove_stale_days > 0:
                cutoff = datetime.now(timezone.utc) - timedelta(days=remove_stale_days)
                stale_stmt = select(ProxyStatusTable.proxy_url).where(
                    (ProxyStatusTable.last_check_at < cutoff)  # type: ignore[operator]
                    | ProxyStatusTable.last_check_at.is_(None)  # type: ignore[union-attr]
                )
                stale_result = await session.exec(stale_stmt)
                stale_urls = list(stale_result.all())

                if stale_urls:
                    # Delete from validation_results first (FK constraint)
                    del_validation = delete(ValidationResultTable).where(
                        ValidationResultTable.proxy_url.in_(stale_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_validation)  # type: ignore[arg-type]

                    # Delete from status table (FK constraint)
                    del_status = delete(ProxyStatusTable).where(
                        ProxyStatusTable.proxy_url.in_(stale_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_status)  # type: ignore[arg-type]

                    del_stmt = delete(ProxyIdentityTable).where(
                        ProxyIdentityTable.url.in_(stale_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_stmt)  # type: ignore[arg-type]
                    counts["stale"] = len(stale_urls)
                else:
                    counts["stale"] = 0

            # Remove never validated proxies
            if remove_never_validated:
                never_stmt = select(ProxyStatusTable.proxy_url).where(
                    ProxyStatusTable.total_checks == 0
                )
                never_result = await session.exec(never_stmt)
                never_urls = list(never_result.all())

                if never_urls:
                    # Delete from validation_results first (FK constraint)
                    del_validation = delete(ValidationResultTable).where(
                        ValidationResultTable.proxy_url.in_(never_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_validation)  # type: ignore[arg-type]

                    # Delete from status table (FK constraint)
                    del_status = delete(ProxyStatusTable).where(
                        ProxyStatusTable.proxy_url.in_(never_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_status)  # type: ignore[arg-type]

                    del_stmt = delete(ProxyIdentityTable).where(
                        ProxyIdentityTable.url.in_(never_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_stmt)  # type: ignore[arg-type]
                    counts["never_validated"] = len(never_urls)
                else:
                    counts["never_validated"] = 0

            # Clean old validation history (keep 1 day)
            history_cutoff = datetime.now(timezone.utc) - timedelta(days=1)
            del_history = delete(ValidationResultTable).where(
                ValidationResultTable.validated_at < history_cutoff
            )
            result = await session.exec(del_history)  # type: ignore[arg-type]
            counts["old_validations"] = result.rowcount if hasattr(result, "rowcount") else 0

            await session.commit()

        # Vacuum to reclaim space
        if vacuum:
            async with self.engine.begin() as conn:
                await conn.execute(text("VACUUM"))

        return counts

    async def get_stats(self) -> dict[str, Any]:
        """Get database statistics.

        Returns:
            dict[str, Any]: Comprehensive database statistics.
        """
        stats: dict[str, Any] = {}

        async with AsyncSession(self.engine) as session:
            # Total proxies
            result = await self._timed_exec(
                session, text("SELECT COUNT(*) FROM proxy_identities")
            )
            stats["total_proxies"] = result.scalar() or 0

            # By health status
            result = await self._timed_exec(
                session,
                text("""
                SELECT health_status, COUNT(*)
                FROM proxy_statuses
                GROUP BY health_status
            """),
            )
            stats["by_health"] = dict(result.all())

            # By protocol
            result = await self._timed_exec(
                session,
                text("""
                SELECT protocol, COUNT(*)
                FROM proxy_identities
                GROUP BY protocol
            """),
            )
            stats["by_protocol"] = dict(result.all())

            # Validation stats (last 24 hours)
            result = await self._timed_exec(
                session,
                text("""
                SELECT
                    COUNT(*) as total_validations,
                    SUM(CASE WHEN is_valid THEN 1 ELSE 0 END) as successful,
                    AVG(CASE WHEN is_valid THEN response_time_ms END) as avg_response_time
                FROM validation_results
                WHERE validated_at > datetime('now', '-24 hours')
            """),
            )
            row = result.one()
            stats["validations_24h"] = {
                "total": row[0] or 0,
                "successful": row[1] or 0,
                "avg_response_time_ms": row[2],
            }

            # Database file size
            if self.filepath.exists():
                stats["db_size_bytes"] = self.filepath.stat().st_size

        # Cache the stats with TTL
        self._stats_cache = stats
        self._stats_cache_time = datetime.now(timezone.utc)

        return stats

    async def get_stats_cached(self) -> dict[str, Any]:
        """Get cached database statistics with TTL.

        Returns cached stats if available and not expired,
        otherwise queries database and updates cache.

        This avoids expensive aggregation queries on every request.
        Cache is invalidated after 30 seconds.

        Returns:
            dict[str, Any]: Cached database statistics.
        """
        now = datetime.now(timezone.utc)

        # Return cached stats if valid
        if (
            self._stats_cache is not None
            and self._stats_cache_time is not None
            and (now - self._stats_cache_time) < self._stats_cache_ttl
        ):
            return self._stats_cache

        # Cache expired or not populated - fetch fresh stats
        return await self.get_stats()

    async def get_proxies_batch(self, proxy_urls: list[str]) -> dict[str, dict[str, Any]]:
        """Get multiple proxies by URL in a single batch query.

        More efficient than calling get_proxy() in a loop.
        Uses a single JOIN query instead of N queries.

        Args:
            proxy_urls: List of proxy URLs to retrieve

        Returns:
            dict mapping proxy_url to proxy data dict (empty dict if not found)
        """
        if not proxy_urls:
            return {}

        stmt = (
            select(ProxyIdentityTable, ProxyStatusTable)
            .join(ProxyStatusTable, ProxyIdentityTable.url == ProxyStatusTable.proxy_url)
            .where(ProxyIdentityTable.url.in_(proxy_urls))  # type: ignore[attr-defined]
        )

        result_map: dict[str, dict[str, Any]] = {}

        async with AsyncSession(self.engine) as session:
            result = await session.exec(stmt)  # type: ignore[arg-type]
            rows = result.all()

            for identity, status in rows:
                result_map[identity.url] = {
                    "url": identity.url,
                    "protocol": identity.protocol,
                    "host": identity.host,
                    "port": identity.port,
                    "username": self._decrypt_credential(identity.username),
                    "password": self._decrypt_credential(identity.password),
                    "country_code": identity.country_code,
                    "source": identity.source,
                    "health_status": status.health_status,
                    "last_success_at": status.last_success_at,
                    "avg_response_time_ms": status.avg_response_time_ms,
                    "total_checks": status.total_checks,
                    "total_successes": status.total_successes,
                }

        return result_map

    async def get_healthy_proxies_batch(
        self,
        max_age_hours: int = 48,
        protocols: list[str] | None = None,
        country_codes: list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get healthy proxies with optional protocol/country filters.

        More efficient bulk query for filtering by multiple criteria.

        Args:
            max_age_hours: Maximum age of last successful validation
            protocols: Filter by protocol list (http, https, socks4, socks5)
            country_codes: Filter by country code list
            limit: Maximum number of proxies to return

        Returns:
            List of proxy dictionaries
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        stmt = (
            select(ProxyIdentityTable, ProxyStatusTable)
            .join(ProxyStatusTable, ProxyIdentityTable.url == ProxyStatusTable.proxy_url)
            .where(ProxyStatusTable.health_status == "healthy")
            .where(ProxyStatusTable.last_success_at >= cutoff)  # type: ignore[operator]
        )

        if protocols:
            stmt = stmt.where(ProxyIdentityTable.protocol.in_(protocols))  # type: ignore[attr-defined]
        if country_codes:
            stmt = stmt.where(ProxyIdentityTable.country_code.in_(country_codes))  # type: ignore[attr-defined]

        stmt = stmt.order_by(ProxyStatusTable.avg_response_time_ms.asc().nullslast())

        if limit:
            stmt = stmt.limit(limit)

        async with AsyncSession(self.engine) as session:
            result = await session.exec(stmt)  # type: ignore[arg-type]
            rows = result.all()

            proxies = []
            for identity, status in rows:
                proxies.append(
                    {
                        "url": identity.url,
                        "protocol": identity.protocol,
                        "host": identity.host,
                        "port": identity.port,
                        "username": self._decrypt_credential(identity.username),
                        "password": self._decrypt_credential(identity.password),
                        "country_code": identity.country_code,
                        "source": identity.source,
                        "health_status": status.health_status,
                        "last_success_at": status.last_success_at,
                        "avg_response_time_ms": status.avg_response_time_ms,
                        "total_checks": status.total_checks,
                        "total_successes": status.total_successes,
                    }
                )
            return proxies

    async def audit_log_change(
        self,
        proxy_url: str,
        action: str,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
    ) -> None:
        """Log a change to the audit trail.

        Args:
            proxy_url: URL of the proxy that changed
            action: Type of change (INSERT, UPDATE, DELETE)
            old_values: Previous values (for UPDATE/DELETE)
            new_values: New values (for INSERT/UPDATE)
        """
        async with AsyncSession(self.engine) as session:
            audit = ProxyAuditTable(
                proxy_url=proxy_url,
                action=action,
                old_values=json.dumps(old_values) if old_values else None,
                new_values=json.dumps(new_values) if new_values else None,
            )
            session.add(audit)
            await session.commit()


# ============================================================================
# SCHEMA VERSIONING (integrated from schema_versioning.py)
# ============================================================================


class MigrationStatus(str, Enum):
    """Status of a schema migration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class _SchemaVersion:
    """Represents a database schema version."""

    version: int
    description: str
    created_at: datetime
    applied_at: datetime | None = None
    status: MigrationStatus = MigrationStatus.PENDING

    def __repr__(self) -> str:
        return f"v{self.version}: {self.description}"


class Migration:
    """Represents a database migration."""

    def __init__(
        self,
        version: int,
        description: str,
        up_script: str,
        down_script: str | None = None,
    ) -> None:
        """Initialize migration."""
        self.version = version
        self.description = description
        self.up_script = up_script
        self.down_script = down_script or f"-- Rollback for v{version}"
        self.created_at = datetime.now(timezone.utc)

    def validate(self) -> bool:
        """Validate migration."""
        if not self.version or self.version < 1:
            logger.error(f"Invalid version: {self.version}")
            return False
        if not self.description:
            logger.error("Migration missing description")
            return False
        if not self.up_script:
            logger.error("Migration missing up script")
            return False
        return True


class SchemaVersioningManager:
    """Manages database schema versioning and migrations."""

    def __init__(self) -> None:
        """Initialize schema versioning manager."""
        self._versions: dict[int, _SchemaVersion] = {}
        self._migrations: dict[int, Migration] = {}
        self._current_version = 0
        logger.debug("SchemaVersioningManager initialized")

    def register_migration(self, migration: Migration) -> bool:
        """Register a migration."""
        if not migration.validate():
            return False
        if migration.version in self._migrations:
            logger.warning(f"Migration v{migration.version} already registered")
            return False
        self._migrations[migration.version] = migration
        logger.debug(f"Migration registered: {migration}")
        return True

    def apply_migration(self, version: int) -> bool:
        """Apply a migration."""
        if version not in self._migrations:
            logger.error(f"Migration v{version} not found")
            return False
        migration = self._migrations[version]
        schema_version = _SchemaVersion(
            version=version,
            description=migration.description,
            created_at=migration.created_at,
            applied_at=datetime.now(timezone.utc),
            status=MigrationStatus.COMPLETED,
        )
        self._versions[version] = schema_version
        self._current_version = version
        logger.info(f"Migration applied: {schema_version}")
        return True

    def rollback_migration(self, version: int) -> bool:
        """Rollback a migration."""
        if version not in self._versions:
            logger.error(f"Migration v{version} not found")
            return False
        if version not in self._migrations:
            logger.error(f"Migration script v{version} not found")
            return False
        schema_version = self._versions[version]
        schema_version.status = MigrationStatus.ROLLED_BACK
        self._current_version = version - 1
        logger.info(f"Migration rolled back: v{version}")
        return True

    def get_current_version(self) -> int:
        """Get current schema version."""
        return self._current_version

    def get_migration(self, version: int) -> Migration | None:
        """Get a migration."""
        return self._migrations.get(version)

    def get_pending_migrations(self) -> list[Migration]:
        """Get pending migrations."""
        pending = []
        for version in sorted(self._migrations.keys()):
            if version > self._current_version:
                pending.append(self._migrations[version])
        return pending

    def get_applied_migrations(self) -> list[_SchemaVersion]:
        """Get applied migrations."""
        return [v for v in sorted(self._versions.values(), key=lambda x: x.version)]

    def export_status(self) -> dict[str, Any]:
        """Export migration status."""
        return {
            "current_version": self._current_version,
            "total_migrations": len(self._migrations),
            "applied_migrations": len(self._versions),
            "pending_migrations": len(self.get_pending_migrations()),
            "applied": [
                {
                    "version": v.version,
                    "description": v.description,
                    "applied_at": v.applied_at.isoformat() if v.applied_at else None,
                }
                for v in self.get_applied_migrations()
            ],
        }
