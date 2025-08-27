"""proxywhirl/caches/sqlite.py -- Enterprise SQLite cache with SQLModel integration

Production-ready SQLite cache implementation featuring:
- Advanced SQLModel ORM with relationship mapping
- Connection pooling for optimal performance
- Comprehensive health metrics and analytics
- Time-series data tracking with efficient queries
- Geographic and source analysis capabilities
"""

from __future__ import annotations

import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlmodel import Session, SQLModel, create_engine, select, text

from proxywhirl.cache_models import (
    ProxyRecord,
)
from proxywhirl.caches.base import (
    BaseProxyCache,
    CacheFilters,
    CacheMetrics,
    DuplicateStrategy,
)
from proxywhirl.models import CacheType, Proxy


class SQLiteProxyCache(BaseProxyCache):
    """Enterprise SQLite cache with full SQLModel ORM integration."""

    def __init__(
        self,
        cache_path: Path,
        connection_pool_size: int = 5,
        connection_pool_recycle: int = 3600,
        enable_wal: bool = True,
        create_tables: bool = True,
        duplicate_strategy: Optional[DuplicateStrategy] = None,
    ):
        if duplicate_strategy is None:
            duplicate_strategy = DuplicateStrategy.UPDATE
        super().__init__(CacheType.SQLITE, cache_path, duplicate_strategy)

        # Store configuration
        self.connection_pool_size = connection_pool_size
        self.connection_pool_recycle = connection_pool_recycle
        self.enable_wal = enable_wal

        # Database configuration
        self.cache_path = cache_path.with_suffix(".sqlite")

        # Connection string with optimizations
        connect_args = {"check_same_thread": False}
        if enable_wal:
            connect_args = {"check_same_thread": False}  # Remove isolation_level for now

        # Create engine with connection pooling
        self.engine = create_engine(
            f"sqlite:///{self.cache_path}",
            pool_size=connection_pool_size,
            pool_recycle=connection_pool_recycle,
            connect_args=connect_args,
            echo=False,  # Set to True for SQL debugging
        )

        # Initialize database schema
        if create_tables:
            self._create_tables()

        self._initialized = True
        logger.info(f"SQLite cache initialized: {self.cache_path}")

    def _create_tables(self) -> None:
        """Create all database tables from SQLModel metadata."""
        try:
            SQLModel.metadata.create_all(self.engine)

            # Enable WAL mode and other optimizations using raw connection
            with self.engine.begin() as connection:
                connection.exec_driver_sql("PRAGMA journal_mode=WAL;")
                connection.exec_driver_sql("PRAGMA synchronous=NORMAL;")
                connection.exec_driver_sql("PRAGMA cache_size=10000;")  # 10MB cache
                connection.exec_driver_sql("PRAGMA temp_store=MEMORY;")

        except Exception as e:
            logger.error(f"Failed to create SQLite tables: {e}")
            raise

    async def add_proxies(self, proxies: List[Proxy]) -> None:
        """Add proxies with intelligent upsert and relationship handling."""
        if not proxies:
            return

        try:
            with Session(self.engine) as session:
                added_count = 0
                updated_count = 0

                for proxy in proxies:
                    # Check for existing record
                    existing = session.exec(
                        select(ProxyRecord).where(
                            ProxyRecord.host == proxy.host, ProxyRecord.port == proxy.port
                        )
                    ).first()

                    if existing:
                        # Update existing record
                        self._update_proxy_record(existing, proxy)
                        updated_count += 1
                    else:
                        # Create new record
                        proxy_record = self._create_proxy_record(proxy)
                        session.add(proxy_record)
                        added_count += 1

                session.commit()
                logger.info(f"SQLite cache: added {added_count}, updated {updated_count} proxies")

        except Exception as e:
            logger.error(f"Failed to add proxies to SQLite cache: {e}")
            raise

    async def get_proxies(self, filters: Optional[CacheFilters] = None) -> List[Proxy]:
        """Get proxies with advanced filtering capabilities."""
        try:
            with Session(self.engine) as session:
                query = select(ProxyRecord)

                # Apply filters
                if filters:
                    if filters.healthy_only:
                        # Assuming health is tracked via recent metrics
                        query = query.where(ProxyRecord.status == "active")

                    # Basic filtering - avoiding complex .in_() for now
                    if filters.country_codes and len(filters.country_codes) == 1:
                        query = query.where(ProxyRecord.country_code == filters.country_codes[0])

                    if filters.sources and len(filters.sources) == 1:
                        query = query.where(ProxyRecord.source == filters.sources[0])

                    if filters.limit:
                        query = query.limit(filters.limit)

                    if filters.offset:
                        query = query.offset(filters.offset)

                records = session.exec(query).all()
                return [self._record_to_proxy(record) for record in records]

        except Exception as e:
            logger.error(f"Failed to get proxies from SQLite cache: {e}")
            return []

    async def update_proxy(self, proxy: Proxy) -> None:
        """Update a specific proxy record."""
        try:
            with Session(self.engine) as session:
                existing = session.exec(
                    select(ProxyRecord).where(
                        ProxyRecord.host == proxy.host, ProxyRecord.port == proxy.port
                    )
                ).first()

                if existing:
                    self._update_proxy_record(existing, proxy)
                    session.add(existing)
                    session.commit()
                    logger.debug(f"Updated proxy {proxy.host}:{proxy.port}")

        except Exception as e:
            logger.error(f"Failed to update proxy in SQLite cache: {e}")
            raise

    async def remove_proxy(self, proxy: Proxy) -> None:
        """Remove a proxy and its related data."""
        try:
            with Session(self.engine) as session:
                record = session.exec(
                    select(ProxyRecord).where(
                        ProxyRecord.host == proxy.host, ProxyRecord.port == proxy.port
                    )
                ).first()

                if record:
                    session.delete(record)  # Cascade deletes handle relationships
                    session.commit()
                    logger.debug(f"Removed proxy {proxy.host}:{proxy.port}")

        except Exception as e:
            logger.error(f"Failed to remove proxy from SQLite cache: {e}")
            raise

    async def clear(self) -> None:
        """Clear all data from the cache."""
        try:
            with Session(self.engine) as session:
                # Delete all records using SQLModel ORM
                records = session.exec(select(ProxyRecord)).all()
                for record in records:
                    session.delete(record)
                session.commit()
                logger.info("SQLite cache cleared")

        except Exception as e:
            logger.error(f"Failed to clear SQLite cache: {e}")
            raise

    async def get_health_metrics(self) -> CacheMetrics:
        """Get comprehensive cache health metrics with enhanced analytics."""
        try:
            with Session(self.engine) as session:
                # Get basic counts using SQLModel queries
                total_proxies = len(session.exec(select(ProxyRecord)).all())
                healthy_records = session.exec(
                    select(ProxyRecord).where(ProxyRecord.status == "active")
                ).all()
                healthy_proxies = len(healthy_records)

                # Enhanced metrics using geographic analytics
                enhanced_metrics = CacheMetrics(
                    total_proxies=total_proxies,
                    healthy_proxies=healthy_proxies,
                    unhealthy_proxies=total_proxies - healthy_proxies,
                    last_updated=datetime.now(timezone.utc),
                    success_rate=healthy_proxies / total_proxies if total_proxies > 0 else 0.0,
                )

                # Get geographic and source analytics if available
                try:
                    geo_analytics = await self.get_geographic_analytics()
                    if geo_analytics:
                        # Extract geographic distribution
                        enhanced_metrics.geographic_distribution = {
                            item["country_code"]: item["total_proxies"]
                            for item in geo_analytics.get("geographic", [])
                        }

                        # Extract source reliability
                        enhanced_metrics.source_reliability = {
                            item["source"]: item["avg_quality"]
                            for item in geo_analytics.get("source_reliability", [])
                        }

                        # Calculate quality distribution
                        quality_ranges = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
                        for item in geo_analytics.get("geographic", []):
                            high_quality = item.get("high_quality_proxies", 0)
                            total_prox = item.get("total_proxies", 0)
                            if total_prox > 0:
                                ratio = high_quality / total_prox
                                if ratio >= 0.8:
                                    quality_ranges["high"] += total_prox
                                elif ratio >= 0.5:
                                    quality_ranges["medium"] += total_prox
                                else:
                                    quality_ranges["low"] += total_prox
                            else:
                                quality_ranges["unknown"] += total_prox
                        enhanced_metrics.quality_distribution = quality_ranges

                except Exception as analytics_error:
                    logger.debug(f"Analytics calculation failed: {analytics_error}")

                # Get performance trends for response times
                try:
                    trends = await self.get_performance_trends(hours=1)  # Last hour only
                    recent_data = trends.get("hourly_trends", [])
                    if recent_data:
                        latest = recent_data[0]
                        enhanced_metrics.avg_response_time = latest.get("avg_response_time")

                except Exception as trends_error:
                    logger.debug(f"Trends calculation failed: {trends_error}")

                # Database file size
                try:
                    if self.cache_path.exists():
                        file_size = self.cache_path.stat().st_size / (1024 * 1024)  # MB
                        enhanced_metrics.disk_usage_mb = file_size
                except Exception:
                    pass

                return enhanced_metrics

        except Exception as e:
            logger.error(f"Failed to get health metrics from SQLite cache: {e}")
            return CacheMetrics()

    async def get_connection_metrics(self) -> Dict[str, Any]:
        """Get database connection pool metrics."""
        try:
            # SQLAlchemy connection pool stats
            pool = self.engine.pool
            return {
                "active_connections": getattr(pool, "checkedout", 0),
                "idle_connections": getattr(pool, "checkedin", 0),
                "total_connections": getattr(pool, "size", 0),
                "overflow_connections": getattr(pool, "checked_out", 0),
                "pool_size": self.connection_pool_size,
            }
        except Exception as e:
            logger.debug(f"Connection metrics failed: {e}")
            return {
                "active_connections": 0,
                "idle_connections": 0,
                "total_connections": 0,
                "overflow_connections": 0,
                "pool_size": self.connection_pool_size,
            }

    def _create_proxy_record(self, proxy: Proxy) -> ProxyRecord:
        """Convert Proxy model to ProxyRecord for database storage."""
        return ProxyRecord(
            id=uuid.uuid4(),
            host=proxy.host,
            port=proxy.port,
            ip=str(proxy.ip),  # Convert IP to string
            schemes=",".join([s.value for s in proxy.schemes]),
            country_code=proxy.country_code,
            country=proxy.country,
            source=proxy.source,
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            last_checked=datetime.now(timezone.utc),
            proxy_metadata="{}",
            target_health="{}",
            # Required fields with defaults
            city=getattr(proxy, "city", None),
            region=getattr(proxy, "region", None),
            isp=getattr(proxy, "isp", None),
            organization=getattr(proxy, "organization", None),
            quality_score=getattr(proxy, "quality_score", None),
            blacklist_reason=None,
            credentials=None,
            capabilities=None,
        )

    def _update_proxy_record(self, record: ProxyRecord, proxy: Proxy) -> None:
        """Update existing ProxyRecord with data from Proxy."""
        record.host = proxy.host
        record.port = proxy.port
        record.ip = str(proxy.ip)  # Convert IP to string
        record.schemes = ",".join([s.value for s in proxy.schemes])
        record.country_code = proxy.country_code
        record.country = proxy.country
        record.source = proxy.source
        record.updated_at = datetime.now(timezone.utc)
        record.last_checked = datetime.now(timezone.utc)

    def _record_to_proxy(self, record: ProxyRecord) -> Proxy:
        """Convert ProxyRecord back to Proxy model."""
        from proxywhirl.models import AnonymityLevel, ProxyScheme, ProxyStatus

        schemes: List[ProxyScheme] = []
        if record.schemes:
            for scheme_str in record.schemes.split(","):
                try:
                    schemes.append(ProxyScheme(scheme_str.strip()))
                except ValueError:
                    logger.warning(f"Unknown proxy scheme: {scheme_str}")

        return Proxy(
            host=record.host,
            port=record.port,
            ip=record.ip,
            schemes=schemes,
            country_code=record.country_code,
            country=record.country,
            source=record.source,
            # Optional fields with proper defaults
            credentials=None,
            metrics=None,
            capabilities=None,
            city=record.city,
            region=record.region,
            isp=record.isp,
            organization=record.organization,
            anonymity=AnonymityLevel.UNKNOWN,
            last_checked=record.last_checked or datetime.now(timezone.utc),
            response_time=None,
            metadata={},
            status=ProxyStatus.ACTIVE if record.status == "active" else ProxyStatus.INACTIVE,
            quality_score=float(record.quality_score) if record.quality_score else None,
            blacklist_reason=record.blacklist_reason,
        )

    # === Enhanced Analytics Methods ===

    async def get_geographic_analytics(self) -> Dict[str, Dict[str, int]]:
        """Get geographic distribution analytics using composite indexes."""
        try:
            with Session(self.engine) as session:
                # Country distribution with quality metrics
                country_stats = session.exec(
                    text(
                        """
                        SELECT 
                            country_code,
                            country,
                            COUNT(*) as total_proxies,
                            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_proxies,
                            AVG(quality_score) as avg_quality,
                            COUNT(CASE WHEN quality_score > 0.8 THEN 1 END) as high_quality_proxies
                        FROM proxy_records 
                        WHERE country_code IS NOT NULL 
                        GROUP BY country_code, country 
                        ORDER BY total_proxies DESC
                    """
                    )
                ).fetchall()

                # Source reliability analytics
                source_stats = session.exec(
                    text(
                        """
                        SELECT 
                            source,
                            COUNT(*) as total_proxies,
                            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_proxies,
                            AVG(quality_score) as avg_quality,
                            COUNT(CASE WHEN updated_at > datetime('now', '-1 hour') THEN 1 END) as recent_updates
                        FROM proxy_records 
                        WHERE source IS NOT NULL 
                        GROUP BY source 
                        ORDER BY avg_quality DESC NULLS LAST
                    """
                    )
                ).fetchall()

                return {
                    "geographic": [
                        {
                            "country_code": row.country_code,
                            "country": row.country,
                            "total_proxies": row.total_proxies,
                            "active_proxies": row.active_proxies,
                            "avg_quality": float(row.avg_quality) if row.avg_quality else 0.0,
                            "high_quality_proxies": row.high_quality_proxies,
                        }
                        for row in country_stats
                    ],
                    "source_reliability": [
                        {
                            "source": row.source,
                            "total_proxies": row.total_proxies,
                            "active_proxies": row.active_proxies,
                            "avg_quality": float(row.avg_quality) if row.avg_quality else 0.0,
                            "recent_updates": row.recent_updates,
                        }
                        for row in source_stats
                    ],
                }
        except Exception as e:
            logger.error(f"Geographic analytics failed: {e}")
            return {"geographic": [], "source_reliability": []}

    async def get_performance_trends(
        self, proxy_id: Optional[uuid.UUID] = None, hours: int = 24
    ) -> Dict[str, List[Dict]]:
        """Get performance trends using time-series indexes."""
        try:
            with Session(self.engine) as session:
                # Build query with optional proxy filter
                base_query = """
                    SELECT 
                        datetime(timestamp) as time_bucket,
                        AVG(response_time) as avg_response_time,
                        AVG(success_rate) as avg_success_rate,
                        COUNT(*) as measurements,
                        COUNT(CASE WHEN status_code = 200 THEN 1 END) as successful_checks
                    FROM health_metrics 
                    WHERE timestamp > datetime('now', '-{} hours')
                """.format(
                    hours
                )

                if proxy_id:
                    base_query += f" AND proxy_record_id = '{proxy_id}'"

                base_query += """
                    GROUP BY datetime(timestamp, 'start of hour')
                    ORDER BY time_bucket DESC
                    LIMIT 168  -- One week of hourly data max
                """

                trends = session.exec(text(base_query)).fetchall()

                return {
                    "hourly_trends": [
                        {
                            "timestamp": row.time_bucket,
                            "avg_response_time": (
                                float(row.avg_response_time) if row.avg_response_time else None
                            ),
                            "avg_success_rate": (
                                float(row.avg_success_rate) if row.avg_success_rate else None
                            ),
                            "measurements": row.measurements,
                            "successful_checks": row.successful_checks,
                        }
                        for row in trends
                    ]
                }
        except Exception as e:
            logger.error(f"Performance trends failed: {e}")
            return {"hourly_trends": []}

    async def record_health_metric(
        self,
        proxy_id: uuid.UUID,
        response_time: Optional[float] = None,
        success_rate: Optional[float] = None,
        target_url: Optional[str] = None,
        status_code: Optional[int] = None,
        check_type: str = "http",
    ) -> None:
        """Record health metrics for time-series analysis."""
        try:
            from proxywhirl.cache_models import HealthMetric

            with Session(self.engine) as session:
                health_metric = HealthMetric(
                    proxy_record_id=proxy_id,
                    timestamp=datetime.now(timezone.utc),
                    response_time=Decimal(str(response_time)) if response_time else None,
                    success_rate=Decimal(str(success_rate)) if success_rate else None,
                    target_url=target_url,
                    status_code=status_code,
                    check_type=check_type,
                )
                session.add(health_metric)
                session.commit()
        except Exception as e:
            logger.error(f"Failed to record health metric: {e}")

    async def cleanup_old_metrics(self, days_to_keep: int = 30) -> int:
        """Clean up old health metrics to manage database size."""
        try:
            with Session(self.engine) as session:
                cutoff_date = datetime.now(timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) - timedelta(days=days_to_keep)

                result = session.exec(
                    text("DELETE FROM health_metrics WHERE timestamp < :cutoff"),
                    {"cutoff": cutoff_date},
                )

                deleted_count = result.rowcount or 0
                session.commit()
                logger.info(f"Cleaned up {deleted_count} old health metrics")
                return deleted_count
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0


class AsyncSQLiteProxyCache(BaseProxyCache):
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
        if duplicate_strategy is None:
            duplicate_strategy = DuplicateStrategy.UPDATE
        super().__init__(CacheType.SQLITE, cache_path, duplicate_strategy)

        # Store configuration
        self.connection_pool_size = connection_pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.enable_wal = enable_wal
        self.enable_foreign_keys = enable_foreign_keys
        self.enable_background_cleanup = enable_background_cleanup

        # Database configuration
        self.cache_path = cache_path.with_suffix(".sqlite")
        self._engine: Optional[AsyncEngine] = None
        self._background_tasks: List[asyncio.Task] = []
        self._initialized = False

    async def _get_engine(self) -> AsyncEngine:
        """Get or create the async database engine."""
        if self._engine is None:
            # Create async connection string
            connection_string = f"sqlite+aiosqlite:///{self.cache_path}"

            # Create async engine with optimized connection pool
            self._engine = create_async_engine(
                connection_string,
                pool_size=self.connection_pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                echo=False,  # Set to True for SQL debugging
                future=True,
            )

            logger.info(f"Async SQLite engine created: {self.cache_path}")

        return self._engine

    async def _initialize(self) -> None:
        """Initialize the async database and create tables."""
        if self._initialized:
            return

        try:
            engine = await self._get_engine()

            # Create all tables
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)

                # Enable WAL mode and other optimizations
                if self.enable_wal:
                    await conn.execute(text("PRAGMA journal_mode=WAL"))

                if self.enable_foreign_keys:
                    await conn.execute(text("PRAGMA foreign_keys=ON"))

                # Performance optimizations
                await conn.execute(text("PRAGMA synchronous=NORMAL"))
                await conn.execute(text("PRAGMA cache_size=10000"))  # 10MB cache
                await conn.execute(text("PRAGMA temp_store=MEMORY"))
                await conn.execute(text("PRAGMA mmap_size=268435456"))  # 256MB mmap

            # Start background maintenance tasks
            if self.enable_background_cleanup:
                await self._start_background_tasks()

            self._initialized = True
            logger.info(f"Async SQLite cache initialized: {self.cache_path}")

        except Exception as e:
            logger.error(f"Failed to initialize async SQLite cache: {e}")
            raise

    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        try:
            # Cleanup task - runs every hour
            cleanup_task = asyncio.create_task(self._cleanup_task())
            self._background_tasks.append(cleanup_task)

            # Metrics collection task - runs every 5 minutes
            metrics_task = asyncio.create_task(self._metrics_collection_task())
            self._background_tasks.append(metrics_task)

            logger.info("Background tasks started for async SQLite cache")
        except Exception as e:
            logger.error(f"Failed to start background tasks: {e}")

    async def _cleanup_task(self) -> None:
        """Background task for periodic cleanup."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self.cleanup_old_metrics(days_to_keep=30)
                logger.debug("Background cleanup completed")
            except asyncio.CancelledError:
                logger.info("Cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Background cleanup failed: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error

    async def _metrics_collection_task(self) -> None:
        """Background task for metrics collection."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                metrics = await self.get_health_metrics()
                logger.debug(f"Collected metrics: {metrics.total_proxies} proxies")
            except asyncio.CancelledError:
                logger.info("Metrics collection task cancelled")
                break
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
                await asyncio.sleep(300)  # Continue on error

    @asynccontextmanager
    async def _get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session with proper error handling."""
        if not self._initialized:
            await self._initialize()

        engine = await self._get_engine()
        async with AsyncSession(engine) as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def _proxy_to_record(self, proxy: Proxy) -> ProxyRecord:
        """Convert Proxy model to ProxyRecord for database storage."""
        return ProxyRecord(
            id=proxy.id or uuid.uuid4(),
            host=proxy.host,
            port=proxy.port,
            protocol=proxy.protocol,
            anonymity_level=proxy.anonymity_level,
            country_code=proxy.country_code or "UNKNOWN",
            source=proxy.source or "manual",
            is_working=proxy.is_working,
            response_time=proxy.response_time,
            last_checked=proxy.last_checked or datetime.now(timezone.utc),
            created_at=proxy.created_at or datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            status="active" if proxy.is_working else "inactive",
            success_rate=Decimal("0.0"),
            total_checks=0,
            consecutive_failures=0,
        )

    def _record_to_proxy(self, record: ProxyRecord) -> Proxy:
        """Convert ProxyRecord from database to Proxy model."""
        return Proxy(
            id=record.id,
            host=record.host,
            port=record.port,
            protocol=record.protocol,
            anonymity_level=record.anonymity_level,
            country_code=record.country_code if record.country_code != "UNKNOWN" else None,
            source=record.source if record.source != "manual" else None,
            is_working=record.is_working,
            response_time=record.response_time,
            last_checked=record.last_checked,
            created_at=record.created_at,
        )

    async def add_proxies(self, proxies: List[Proxy]) -> None:
        """Add proxies with intelligent upsert and relationship handling."""
        if not proxies:
            return

        try:
            async with self._get_session() as session:
                added_count = 0
                updated_count = 0

                for proxy in proxies:
                    # Check for existing record
                    result = await session.execute(
                        select(ProxyRecord).where(
                            ProxyRecord.host == proxy.host, ProxyRecord.port == proxy.port
                        )
                    )
                    existing = result.scalar_one_or_none()

                    if existing:
                        # Update existing record
                        if proxy.is_working is not None:
                            existing.is_working = proxy.is_working
                        if proxy.response_time is not None:
                            existing.response_time = proxy.response_time
                        existing.last_checked = proxy.last_checked or datetime.now(timezone.utc)
                        existing.updated_at = datetime.now(timezone.utc)
                        updated_count += 1
                    else:
                        # Create new record
                        proxy_record = self._proxy_to_record(proxy)
                        session.add(proxy_record)
                        added_count += 1

                logger.info(
                    f"Async SQLite cache: added {added_count}, updated {updated_count} proxies"
                )

        except Exception as e:
            logger.error(f"Failed to add proxies to async SQLite cache: {e}")
            raise

    async def get_proxies(self, filters: Optional[CacheFilters] = None) -> List[Proxy]:
        """Get proxies with advanced filtering capabilities."""
        try:
            async with self._get_session() as session:
                query = select(ProxyRecord)

                # Apply filters
                if filters:
                    if filters.healthy_only:
                        query = query.where(ProxyRecord.is_working)

                    if filters.country_codes and len(filters.country_codes) == 1:
                        query = query.where(ProxyRecord.country_code == filters.country_codes[0])

                    if filters.sources and len(filters.sources) == 1:
                        query = query.where(ProxyRecord.source == filters.sources[0])

                    if filters.limit:
                        query = query.limit(filters.limit)

                result = await session.execute(query)
                records = result.scalars().all()

                return [self._record_to_proxy(record) for record in records]

        except Exception as e:
            logger.error(f"Failed to get proxies from async SQLite cache: {e}")
            return []

    async def update_proxy(self, proxy: Proxy) -> None:
        """Update a specific proxy record."""
        try:
            async with self._get_session() as session:
                result = await session.execute(
                    select(ProxyRecord).where(
                        ProxyRecord.host == proxy.host, ProxyRecord.port == proxy.port
                    )
                )
                existing = result.scalar_one_or_none()

                if existing:
                    # Update the existing record
                    if proxy.is_working is not None:
                        existing.is_working = proxy.is_working
                    if proxy.response_time is not None:
                        existing.response_time = proxy.response_time
                    if proxy.anonymity_level is not None:
                        existing.anonymity_level = proxy.anonymity_level
                    if proxy.country_code is not None:
                        existing.country_code = proxy.country_code

                    existing.last_checked = proxy.last_checked or datetime.now(timezone.utc)
                    existing.updated_at = datetime.now(timezone.utc)

                    logger.debug(f"Updated proxy: {proxy.host}:{proxy.port}")
                else:
                    logger.warning(f"Proxy not found for update: {proxy.host}:{proxy.port}")

        except Exception as e:
            logger.error(f"Failed to update proxy in async SQLite cache: {e}")
            raise

    async def remove_proxy(self, proxy: Proxy) -> None:
        """Remove a specific proxy record."""
        try:
            async with self._get_session() as session:
                result = await session.execute(
                    select(ProxyRecord).where(
                        ProxyRecord.host == proxy.host, ProxyRecord.port == proxy.port
                    )
                )
                existing = result.scalar_one_or_none()

                if existing:
                    await session.delete(existing)
                    logger.debug(f"Removed proxy: {proxy.host}:{proxy.port}")
                else:
                    logger.warning(f"Proxy not found for removal: {proxy.host}:{proxy.port}")

        except Exception as e:
            logger.error(f"Failed to remove proxy from async SQLite cache: {e}")
            raise

    async def clear(self) -> None:
        """Clear all proxy records from the cache."""
        try:
            async with self._get_session() as session:
                await session.execute(text("DELETE FROM proxy_records"))
                logger.info("Async SQLite cache cleared")

        except Exception as e:
            logger.error(f"Failed to clear async SQLite cache: {e}")
            raise

    async def get_health_metrics(self) -> CacheMetrics:
        """Get comprehensive health metrics for the cache."""
        try:
            async with self._get_session() as session:
                # Get basic counts
                total_result = await session.execute(
                    select(text("COUNT(*) as count FROM proxy_records"))
                )
                total_count = total_result.scalar() or 0

                healthy_result = await session.execute(
                    select(text("COUNT(*) as count FROM proxy_records WHERE is_working = 1"))
                )
                healthy_count = healthy_result.scalar() or 0

                return CacheMetrics(
                    total_proxies=int(total_count),
                    healthy_proxies=int(healthy_count),
                    unhealthy_proxies=int(total_count - healthy_count),
                    geographic_distribution={},
                    source_reliability={},
                    average_response_time=0.0,
                    cache_hit_ratio=1.0,
                    last_updated=datetime.now(timezone.utc),
                )

        except Exception as e:
            logger.error(f"Failed to get health metrics from async SQLite cache: {e}")
            return CacheMetrics(
                total_proxies=0,
                healthy_proxies=0,
                unhealthy_proxies=0,
                geographic_distribution={},
                source_reliability={},
                average_response_time=0.0,
                cache_hit_ratio=0.0,
                last_updated=datetime.now(timezone.utc),
            )

    async def cleanup_old_metrics(self, days_to_keep: int = 30) -> int:
        """Clean up old health metrics to maintain performance."""
        try:
            async with self._get_session() as session:
                cutoff_date = datetime.now(timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) - timedelta(days=days_to_keep)

                result = await session.execute(
                    text("DELETE FROM health_metrics WHERE timestamp < :cutoff"),
                    {"cutoff": cutoff_date},
                )

                deleted_count = result.rowcount or 0
                logger.info(f"Cleaned up {deleted_count} old health metrics (async)")
                return deleted_count
        except Exception as e:
            logger.error(f"Async cleanup failed: {e}")
            return 0

    async def close(self) -> None:
        """Close the async cache and cleanup resources."""
        try:
            # Cancel background tasks
            for task in self._background_tasks:
                task.cancel()

            if self._background_tasks:
                await asyncio.gather(*self._background_tasks, return_exceptions=True)

            # Close engine
            if self._engine:
                await self._engine.dispose()
                self._engine = None

            self._initialized = False
            logger.info("Async SQLite cache closed successfully")
        except Exception as e:
            logger.error(f"Failed to close async SQLite cache: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
