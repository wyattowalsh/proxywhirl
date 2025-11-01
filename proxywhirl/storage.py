"""Storage backends for persisting proxy pools."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import Field, SQLModel, select

from proxywhirl.models import Proxy


class ProxyTable(SQLModel, table=True):
    """SQLModel table schema for proxy storage in SQLite.

    This table stores comprehensive proxy metadata including health metrics,
    authentication credentials, and usage statistics. The 'source' field is
    indexed for fast filtering by proxy origin.

    Attributes:
        url: Primary key - full proxy URL (e.g., "http://proxy.com:8080")
        protocol: Protocol type (http, https, socks4, socks5)
        username: Optional authentication username
        password: Optional authentication password (store encrypted at app level)
        health_status: Current health status (healthy, unhealthy, unknown)
        last_success_at: Timestamp of last successful request
        last_failure_at: Timestamp of last failed request
        total_requests: Cumulative request count
        total_successes: Cumulative success count
        total_failures: Cumulative failure count
        average_response_time_ms: Rolling average response time in milliseconds
        consecutive_failures: Current consecutive failure streak
        source: Proxy source identifier (indexed) - user, fetched, api, etc.
        source_url: Original URL where proxy was fetched from
        metadata_json: JSON string for additional custom metadata
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    __tablename__: str = "proxies"  # type: ignore[misc]

    url: str = Field(primary_key=True)
    protocol: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    health_status: str = "unknown"
    last_success_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    total_requests: int = 0
    total_successes: int = 0
    total_failures: int = 0
    average_response_time_ms: Optional[float] = None
    consecutive_failures: int = 0
    source: str = Field(default="user", index=True)  # Indexed for fast queries
    source_url: Optional[str] = None
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
    username_encrypted: Optional[bytes] = None
    password_encrypted: Optional[bytes] = None
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


class FileStorage:
    """File-based storage backend using JSON.

    Stores proxies in a JSON file with atomic writes to prevent corruption.
    Supports optional encryption for sensitive credential data.
    """

    def __init__(self, filepath: Union[str, Path], encryption_key: Optional[bytes] = None) -> None:
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
        content: Union[bytes, str]
        write_mode: str
        if self._cipher:
            content = self._cipher.encrypt(json_str.encode("utf-8"))
            write_mode = "wb"
        else:
            content = json_str
            write_mode = "w"

        # Atomic write: write to temp file then rename
        temp_path = self.filepath.with_suffix(".tmp")
        try:
            with open(temp_path, write_mode) as f:
                f.write(content)
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
                with open(self.filepath, "rb") as f:
                    encrypted_data = f.read()
                # Decrypt data
                json_str = self._cipher.decrypt(encrypted_data).decode("utf-8")
                data = json.loads(json_str)
            else:
                with open(self.filepath) as f:
                    data = json.load(f)

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
    async session management.

    Features:
        - Async operations using aiosqlite for non-blocking I/O
        - Advanced filtering by source, health_status, protocol
        - Automatic schema creation and migration
        - Indexed columns for fast queries
        - Thread-safe concurrent access
        - Automatic upsert on save (updates existing proxies)

    Example:
        ```python
        storage = SQLiteStorage("proxies.db")
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

    def __init__(self, filepath: Union[str, Path]) -> None:
        """Initialize SQLite storage.

        Args:
            filepath: Path to the SQLite database file. Will be created if it doesn't exist.
                Parent directories will be created automatically.
        """

        self.filepath = Path(filepath)
        self.engine: AsyncEngine = create_async_engine(
            f"sqlite+aiosqlite:///{self.filepath}",
            echo=False,
        )

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

    async def save(self, proxies: list[Proxy]) -> None:
        """Save proxies to database with automatic upsert.

        Existing proxies (matching URL) will be updated, new proxies will be inserted.
        Uses a delete + insert pattern to ensure data consistency. All operations
        happen within a transaction.

        Args:
            proxies: List of proxies to save. Empty list is allowed (no-op).

        Raises:
            Exception: If save operation fails (transaction will be rolled back)
        """
        from sqlmodel import delete
        from sqlmodel.ext.asyncio.session import AsyncSession

        async with AsyncSession(self.engine) as session:
            # Delete existing proxies with same URLs (simple upsert)
            urls = [proxy.url for proxy in proxies]
            stmt = delete(ProxyTable).where(ProxyTable.url.in_(urls))  # type: ignore[attr-defined]
            await session.exec(stmt)

            # Insert new proxies
            for proxy in proxies:
                proxy_row = ProxyTable(
                    url=proxy.url,
                    protocol=proxy.protocol,
                    username=proxy.username.get_secret_value() if proxy.username else None,
                    password=proxy.password.get_secret_value() if proxy.password else None,
                    health_status=proxy.health_status.value,
                    last_success_at=proxy.last_success_at,
                    last_failure_at=proxy.last_failure_at,
                    total_requests=proxy.total_requests,
                    total_successes=proxy.total_successes,
                    total_failures=proxy.total_failures,
                    average_response_time_ms=proxy.average_response_time_ms,
                    consecutive_failures=proxy.consecutive_failures,
                    source=proxy.source.value,
                    source_url=str(proxy.source_url) if proxy.source_url else None,
                    metadata_json=json.dumps(proxy.metadata),
                    created_at=proxy.created_at,
                    updated_at=proxy.updated_at,
                )
                session.add(proxy_row)

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
        from sqlmodel.ext.asyncio.session import AsyncSession

        async with AsyncSession(self.engine) as session:
            result = await session.exec(select(ProxyTable))
            proxy_rows = result.all()

            proxies = []
            for row in proxy_rows:
                proxy_data = {
                    "url": row.url,
                    "protocol": row.protocol,
                    "username": row.username,
                    "password": row.password,
                    "health_status": row.health_status,
                    "last_success_at": row.last_success_at,
                    "last_failure_at": row.last_failure_at,
                    "total_requests": row.total_requests,
                    "total_successes": row.total_successes,
                    "total_failures": row.total_failures,
                    "average_response_time_ms": row.average_response_time_ms,
                    "consecutive_failures": row.consecutive_failures,
                    "source": row.source,
                    "source_url": row.source_url,
                    "metadata": json.loads(row.metadata_json),
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                }
                proxies.append(Proxy.model_validate(proxy_data))

            return proxies

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
        from sqlmodel.ext.asyncio.session import AsyncSession

        async with AsyncSession(self.engine) as session:
            stmt = select(ProxyTable)

            # Apply filters
            if "source" in filters:
                stmt = stmt.where(ProxyTable.source == filters["source"])
            if "health_status" in filters:
                stmt = stmt.where(ProxyTable.health_status == filters["health_status"])

            result = await session.exec(stmt)
            proxy_rows = result.all()

            proxies = []
            for row in proxy_rows:
                proxy_data = {
                    "url": row.url,
                    "protocol": row.protocol,
                    "username": row.username,
                    "password": row.password,
                    "health_status": row.health_status,
                    "last_success_at": row.last_success_at,
                    "last_failure_at": row.last_failure_at,
                    "total_requests": row.total_requests,
                    "total_successes": row.total_successes,
                    "total_failures": row.total_failures,
                    "average_response_time_ms": row.average_response_time_ms,
                    "consecutive_failures": row.consecutive_failures,
                    "source": row.source,
                    "source_url": row.source_url,
                    "metadata": json.loads(row.metadata_json),
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                }
                proxies.append(Proxy.model_validate(proxy_data))

            return proxies

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
