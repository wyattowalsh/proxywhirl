"""Storage backends for persisting proxy pools."""

from __future__ import annotations

import base64
import json
from datetime import datetime, timedelta, timezone
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
    proxy_url: str = Field(index=True)  # References proxy_identities.url
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

    proxy_url: str = Field(primary_key=True)  # References proxy_identities.url
    health_status: str = Field(default="unknown", index=True)  # healthy, unhealthy, dead, unknown
    last_success_at: datetime | None = Field(default=None, index=True)
    last_failure_at: datetime | None = None
    last_check_at: datetime | None = None
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    total_checks: int = 0
    total_successes: int = 0
    avg_response_time_ms: float | None = None
    success_rate_7d: float | None = Field(default=None, index=True)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(__import__("datetime").timezone.utc)
    )


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

    Example:
        ```python
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
            # Drop legacy 'proxies' table from old schema
            await conn.execute(text("DROP TABLE IF EXISTS proxies"))

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
        """Add multiple proxies to the normalized schema.

        Args:
            proxies: List of Proxy models to add
            validated: If True, mark proxies as already validated (healthy status,
                last_success_at set). Use this when proxies have passed validation
                before being saved.

        Returns:
            Tuple of (added_count, skipped_count)
        """
        added = 0
        skipped = 0
        now = datetime.now(timezone.utc)

        async with AsyncSession(self.engine) as session:
            for proxy in proxies:
                existing = await session.get(ProxyIdentityTable, proxy.url)
                if existing:
                    skipped += 1
                    continue

                parsed = urlparse(proxy.url)

                row = ProxyIdentityTable(
                    url=proxy.url,
                    protocol=proxy.protocol or "http",
                    host=parsed.hostname or "",
                    port=parsed.port or 80,
                    username=proxy.username.get_secret_value() if proxy.username else None,
                    password=proxy.password.get_secret_value() if proxy.password else None,
                    source=proxy.source.value if proxy.source else "fetched",
                )
                session.add(row)

                # Create status - mark as validated if proxies passed validation
                if validated:
                    status = ProxyStatusTable(
                        proxy_url=proxy.url,
                        health_status="healthy",
                        last_success_at=now,
                        last_check_at=now,
                        total_checks=1,
                        total_successes=1,
                        consecutive_successes=1,
                        avg_response_time_ms=proxy.average_response_time_ms,
                    )
                else:
                    status = ProxyStatusTable(proxy_url=proxy.url)
                session.add(status)
                added += 1

            await session.commit()

        return added, skipped

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
                        "username": identity.username,
                        "password": identity.password,
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
                        "username": identity.username,
                        "password": identity.password,
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
                        "username": identity.username,
                        "password": identity.password,
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
            Dictionary with counts of removed items by category
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
                    # Delete from proxy_identities
                    del_stmt = delete(ProxyIdentityTable).where(
                        ProxyIdentityTable.url.in_(dead_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_stmt)  # type: ignore[arg-type]
                    counts["dead"] = len(dead_urls)

                    # Delete from status table
                    del_status = delete(ProxyStatusTable).where(
                        ProxyStatusTable.proxy_url.in_(dead_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_status)  # type: ignore[arg-type]
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
                    del_stmt = delete(ProxyIdentityTable).where(
                        ProxyIdentityTable.url.in_(stale_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_stmt)  # type: ignore[arg-type]

                    del_status = delete(ProxyStatusTable).where(
                        ProxyStatusTable.proxy_url.in_(stale_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_status)  # type: ignore[arg-type]
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
                    del_stmt = delete(ProxyIdentityTable).where(
                        ProxyIdentityTable.url.in_(never_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_stmt)  # type: ignore[arg-type]

                    del_status = delete(ProxyStatusTable).where(
                        ProxyStatusTable.proxy_url.in_(never_urls)  # type: ignore[attr-defined]
                    )
                    await session.exec(del_status)  # type: ignore[arg-type]
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
            Dictionary with comprehensive database statistics
        """
        stats: dict[str, Any] = {}

        async with AsyncSession(self.engine) as session:
            # Total proxies
            result = await session.exec(text("SELECT COUNT(*) FROM proxy_identities"))
            stats["total_proxies"] = result.scalar() or 0

            # By health status
            result = await session.exec(
                text("""
                SELECT health_status, COUNT(*)
                FROM proxy_statuses
                GROUP BY health_status
            """)
            )
            stats["by_health"] = dict(result.all())

            # By protocol
            result = await session.exec(
                text("""
                SELECT protocol, COUNT(*)
                FROM proxy_identities
                GROUP BY protocol
            """)
            )
            stats["by_protocol"] = dict(result.all())

            # Validation stats (last 24 hours)
            result = await session.exec(
                text("""
                SELECT
                    COUNT(*) as total_validations,
                    SUM(CASE WHEN is_valid THEN 1 ELSE 0 END) as successful,
                    AVG(CASE WHEN is_valid THEN response_time_ms END) as avg_response_time
                FROM validation_results
                WHERE validated_at > datetime('now', '-24 hours')
            """)
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

        return stats
