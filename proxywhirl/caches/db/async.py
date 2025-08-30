"""proxywhirl/caches/db/async.py -- Asynchronous SQLite cache implementation

Production-ready async SQLite cache implementation featuring:
- True async/await patterns with aiosqlite and SQLAlchemy async engine
- High-concurrency connection pooling with configurable limits
- Automatic connection lifecycle management and health monitoring
- Background cleanup tasks for performance optimization
- Comprehensive metrics and monitoring for production environments

This implementation provides significant performance benefits over sync SQLite
for high-concurrency workloads while maintaining full SQLModel compatibility.
"""

from __future__ import annotations

import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import AsyncGenerator, List, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlmodel import SQLModel, select, text

from .models import ProxyRecord
from proxywhirl.caches.base import (
    BaseProxyCache,
    CacheFilters,
    CacheMetrics,
    DuplicateStrategy,
)
from proxywhirl.caches.config import CacheType
from proxywhirl.models import Proxy

from .base import SQLiteBase


class AsyncSQLiteProxyCache(BaseProxyCache, SQLiteBase):
    """
    Production-ready async SQLite cache with SQLAlchemy async engine.

    Features:
    - True async I/O with aiosqlite
    - Connection pooling with automatic lifecycle management
    - Background maintenance tasks
    - Comprehensive performance monitoring
    - Thread-safe concurrent access patterns
    """

    def __init__(
        self,
        cache_path: Path,
        connection_pool_size: int = 20,
        max_overflow: int = 30,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        enable_wal: bool = True,
        enable_foreign_keys: bool = True,
        create_tables: bool = True,
        duplicate_strategy: Optional[DuplicateStrategy] = None,
        enable_background_cleanup: bool = True,
    ):
        """
        Initialize async SQLite cache with advanced configuration.

        Args:
            cache_path: Path to SQLite database file
            connection_pool_size: Base connection pool size (default: 20)
            max_overflow: Additional connections beyond pool_size (default: 30)
            pool_timeout: Timeout for getting connection from pool (seconds)
            pool_recycle: Connection recycle time (seconds, default: 1 hour)
            enable_wal: Enable Write-Ahead Logging for better concurrency
            enable_foreign_keys: Enable foreign key constraints
            create_tables: Auto-create database tables
            duplicate_strategy: How to handle duplicate proxies
            enable_background_cleanup: Run background maintenance tasks
        """
        if duplicate_strategy is None:
            duplicate_strategy = DuplicateStrategy.UPDATE
        
        BaseProxyCache.__init__(self, CacheType.SQLITE, cache_path, duplicate_strategy)
        SQLiteBase.__init__(self, cache_path, enable_wal)

        # Store async configuration
        self.connection_pool_size = connection_pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.enable_foreign_keys = enable_foreign_keys
        self.create_tables = create_tables
        self.enable_background_cleanup = enable_background_cleanup

        # Track background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()

        # Create async engine with optimized configuration
        self._engine: Optional[AsyncEngine] = None
        self._initialized = False

    async def _get_engine(self) -> AsyncEngine:
        """Get or create the async SQLAlchemy engine with connection pooling."""
        if self._engine is None:
            # Build database URL for aiosqlite
            db_url = f"sqlite+aiosqlite:///{self.cache_path}"

            # Create async engine with connection pooling
            self._engine = create_async_engine(
                db_url,
                pool_size=self.connection_pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                pool_pre_ping=True,  # Verify connections before use
                echo=False,  # Set to True for SQL debugging
                connect_args={
                    "check_same_thread": False,  # Allow multi-threading
                    "timeout": 20,  # Connection timeout
                },
            )

            logger.info(
                f"Created async SQLite engine: {db_url} "
                f"(pool_size={self.connection_pool_size}, max_overflow={self.max_overflow})"
            )

        return self._engine

    async def _initialize_backend(self) -> None:
        """Initialize the async cache and create database tables."""
        if self._initialized:
            return

        engine = await self._get_engine()

        # Create all tables using async engine
        if self.create_tables:
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)

                # Configure SQLite for optimal performance
                if self.enable_wal:
                    await conn.execute(text("PRAGMA journal_mode=WAL"))
                if self.enable_foreign_keys:
                    await conn.execute(text("PRAGMA foreign_keys=ON"))

                # Performance optimizations
                await conn.execute(text("PRAGMA synchronous=NORMAL"))
                await conn.execute(text("PRAGMA cache_size=10000"))
                await conn.execute(text("PRAGMA temp_store=memory"))
                await conn.execute(text("PRAGMA mmap_size=134217728"))  # 128MB mmap

                logger.info("Initialized async SQLite cache with performance optimizations")

        self._initialized = True

        # Start background cleanup tasks
        if self.enable_background_cleanup:
            await self._start_background_tasks()

    async def _cleanup_backend(self) -> None:
        """Clean shutdown of async resources."""
        # Signal background tasks to stop
        self._shutdown_event.set()

        # Cancel and wait for background tasks
        for task in self._background_tasks:
            task.cancel()

        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)

        # Close database engine
        if self._engine:
            await self._engine.dispose()
            self._engine = None

        self._initialized = False
        logger.info("Async SQLite cache shut down cleanly")

    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        cleanup_task = asyncio.create_task(self._cleanup_task())
        metrics_task = asyncio.create_task(self._metrics_collection_task())

        self._background_tasks.extend([cleanup_task, metrics_task])
        logger.info("Started background maintenance tasks")

    async def _cleanup_task(self) -> None:
        """Background task for database maintenance."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Run every hour

                async with self._session() as session:
                    # Clean up old expired proxies (older than 7 days)
                    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
                    result = await session.execute(
                        text("DELETE FROM proxy_records WHERE last_checked < :cutoff"),
                        {"cutoff": cutoff},
                    )
                    await session.commit()

                    if result.rowcount > 0:
                        logger.info(f"Cleaned up {result.rowcount} expired proxy records")

                    # Run SQLite optimization
                    await session.execute(text("PRAGMA optimize"))
                    await session.commit()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _metrics_collection_task(self) -> None:
        """Background task for metrics collection."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # Run every 5 minutes

                # Log connection pool metrics
                engine = await self._get_engine()
                pool = engine.pool
                logger.debug(
                    f"Connection pool stats: "
                    f"size={pool.size()}, checked_in={pool.checkedin()}, "
                    f"checked_out={pool.checkedout()}, overflow={pool.overflow()}"
                )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(60)

    @asynccontextmanager
    async def _session(self) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager for database sessions."""
        if not self._initialized:
            await self._initialize_backend()

        engine = await self._get_engine()
        async with AsyncSession(engine) as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    def _proxy_to_record(self, proxy: Proxy) -> ProxyRecord:
        """Convert Proxy model to ProxyRecord for database storage."""
        return ProxyRecord(
            id=str(uuid.uuid4()),
            protocol=proxy.protocol,
            host=proxy.host,
            port=proxy.port,
            username=proxy.username,
            password=proxy.password,
            country=proxy.country,
            source=proxy.source,
            is_anonymous=proxy.is_anonymous,
            is_https=proxy.is_https,
            is_healthy=proxy.is_healthy,
            response_time_ms=proxy.response_time_ms,
            quality_score=Decimal(str(proxy.quality_score)) if proxy.quality_score else None,
            last_checked=proxy.last_checked or datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    def _record_to_proxy(self, record: ProxyRecord) -> Proxy:
        """Convert ProxyRecord from database to Proxy model."""
        return Proxy(
            protocol=record.protocol,
            host=record.host,
            port=record.port,
            username=record.username,
            password=record.password,
            country=record.country,
            source=record.source,
            is_anonymous=record.is_anonymous,
            is_https=record.is_https,
            is_healthy=record.is_healthy,
            response_time_ms=record.response_time_ms,
            quality_score=float(record.quality_score) if record.quality_score else None,
            last_checked=record.last_checked,
        )

    async def add_proxies(self, proxies: List[Proxy]) -> None:
        """Add multiple proxies to cache with async batch processing."""
        if not proxies:
            return

        async with self._session() as session:
            records_to_add = []

            for proxy in proxies:
                # Check for existing proxy
                stmt = select(ProxyRecord).where(
                    ProxyRecord.host == proxy.host,
                    ProxyRecord.port == proxy.port,
                    ProxyRecord.protocol == proxy.protocol,
                )
                existing = await session.execute(stmt)
                existing_record = existing.scalar_one_or_none()

                if existing_record:
                    if self.duplicate_strategy == DuplicateStrategy.UPDATE:
                        # Update existing record
                        existing_record.is_healthy = proxy.is_healthy
                        existing_record.response_time_ms = proxy.response_time_ms
                        existing_record.quality_score = (
                            Decimal(str(proxy.quality_score)) if proxy.quality_score else None
                        )
                        existing_record.last_checked = proxy.last_checked or datetime.now(
                            timezone.utc
                        )
                        existing_record.updated_at = datetime.now(timezone.utc)
                        session.add(existing_record)
                    # SKIP strategy ignores duplicates
                else:
                    # Add new record
                    records_to_add.append(self._proxy_to_record(proxy))

            # Batch add new records
            if records_to_add:
                session.add_all(records_to_add)

            await session.commit()
            logger.debug(f"Added {len(records_to_add)} new proxies, updated existing duplicates")

    async def get_proxies(self, filters: Optional[CacheFilters] = None) -> List[Proxy]:
        """Retrieve proxies with async filtering and pagination."""
        async with self._session() as session:
            stmt = select(ProxyRecord)

            # Apply filters if provided (simplified version for now)
            if filters:
                # Basic filtering without detailed type checking for now
                try:
                    if hasattr(filters, 'is_healthy') and getattr(filters, 'is_healthy', None) is not None:
                        is_healthy = getattr(filters, 'is_healthy')
                        stmt = stmt.where(ProxyRecord.is_healthy == is_healthy)

                    # Pagination
                    if hasattr(filters, 'limit') and getattr(filters, 'limit', None):
                        stmt = stmt.limit(getattr(filters, 'limit'))
                    if hasattr(filters, 'offset') and getattr(filters, 'offset', None):
                        stmt = stmt.offset(getattr(filters, 'offset'))
                except AttributeError:
                    pass

            # Execute query
            result = await session.execute(stmt)
            records = result.scalars().all()

            # Convert to Proxy objects
            return [self._record_to_proxy(record) for record in records]

    async def update_proxy(self, proxy: Proxy) -> None:
        """Update a single proxy record asynchronously."""
        async with self._session() as session:
            stmt = select(ProxyRecord).where(
                ProxyRecord.host == proxy.host,
                ProxyRecord.port == proxy.port,
                ProxyRecord.protocol == proxy.protocol,
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()

            if record:
                # Update all fields
                record.is_healthy = proxy.is_healthy
                record.response_time_ms = proxy.response_time_ms
                record.quality_score = (
                    Decimal(str(proxy.quality_score)) if proxy.quality_score else None
                )
                record.last_checked = proxy.last_checked or datetime.now(timezone.utc)
                record.updated_at = datetime.now(timezone.utc)

                session.add(record)
                await session.commit()

    async def remove_proxy(self, proxy: Proxy) -> None:
        """Remove a proxy from cache asynchronously."""
        async with self._session() as session:
            stmt = select(ProxyRecord).where(
                ProxyRecord.host == proxy.host,
                ProxyRecord.port == proxy.port,
                ProxyRecord.protocol == proxy.protocol,
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()

            if record:
                await session.delete(record)
                await session.commit()

    async def clear(self) -> None:
        """Clear all proxies from cache asynchronously."""
        async with self._session() as session:
            await session.execute(text("DELETE FROM proxy_records"))
            await session.commit()

    async def get_health_metrics(self) -> CacheMetrics:
        """Collect comprehensive health metrics asynchronously."""
        async with self._session() as session:
            # Total proxy count
            total_result = await session.execute(text("SELECT COUNT(*) FROM proxy_records"))
            total_proxies = total_result.scalar() or 0

            # Healthy proxy count
            healthy_result = await session.execute(
                text("SELECT COUNT(*) FROM proxy_records WHERE is_healthy = 1")
            )
            healthy_proxies = healthy_result.scalar() or 0

            # Average response time
            avg_response_result = await session.execute(
                text("SELECT AVG(response_time_ms) FROM proxy_records WHERE is_healthy = 1")
            )
            avg_response_time = avg_response_result.scalar() or 0.0

            # Cache hit ratio (simplified metric)
            cache_hit_ratio = healthy_proxies / max(total_proxies, 1)

            # Connection pool metrics
            engine = await self._get_engine()
            pool = engine.pool

            return CacheMetrics(
                total_proxies=total_proxies,
                healthy_proxies=healthy_proxies,
                unhealthy_proxies=total_proxies - healthy_proxies,
                avg_response_time=avg_response_time,
                cache_hit_ratio=cache_hit_ratio,
                memory_usage_mb=0,  # Not applicable for SQLite
                connection_pool_active=pool.checkedout(),
                connection_pool_idle=pool.checkedin(),
                last_updated=datetime.now(timezone.utc),
            )

    async def close(self) -> None:
        """Clean shutdown of async resources."""
        await self._cleanup_backend()

    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_backend()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
