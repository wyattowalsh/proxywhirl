"""proxywhirl/caches/db/sync.py -- Synchronous SQLite cache implementation

Synchronous SQLite cache implementation using SQLModel ORM for traditional
blocking I/O patterns. Provides enterprise-grade features with connection
pooling and comprehensive error handling.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlmodel import Session, SQLModel, create_engine, select

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


class SQLiteProxyCache(BaseProxyCache, SQLiteBase):
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
        
        BaseProxyCache.__init__(self, CacheType.SQLITE, cache_path, duplicate_strategy)
        SQLiteBase.__init__(self, cache_path, enable_wal)

        # Store configuration
        self.connection_pool_size = connection_pool_size
        self.connection_pool_recycle = connection_pool_recycle
        self.create_tables = create_tables
        self._initialized = False

    async def _initialize_backend(self) -> None:
        """Backend-specific initialization logic."""
        if self._initialized:
            return

        # Connection string with optimizations
        connect_args = {"check_same_thread": False}

        # Create engine with connection pooling
        self.engine = create_engine(
            f"sqlite:///{self.cache_path}",
            pool_size=self.connection_pool_size,
            pool_recycle=self.connection_pool_recycle,
            connect_args=connect_args,
            echo=False,  # Set to True for SQL debugging
        )

        # Initialize database schema
        if self.create_tables:
            self._create_tables()
        self._initialized = True
        logger.info(f"SQLite cache initialized: {self.cache_path}")

    async def _cleanup_backend(self) -> None:
        """Backend-specific cleanup logic."""
        try:
            if hasattr(self, 'engine'):
                self.engine.dispose()
        except Exception as e:
            logger.warning(f"Failed to properly dispose SQLite engine: {e}")

    def _create_tables(self) -> None:
        """Create all database tables from SQLModel metadata."""
        try:
            SQLModel.metadata.create_all(self.engine)

            # Enable WAL mode and other optimizations using raw connection
            with self.engine.begin() as connection:
                for pragma in self._get_sqlite_pragmas():
                    connection.exec_driver_sql(pragma)

            logger.info("SQLite tables created and optimized")

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
                    # Check for existing proxy
                    existing = session.exec(
                        select(ProxyRecord).where(
                            ProxyRecord.host == proxy.host,
                            ProxyRecord.port == proxy.port
                        )
                    ).first()

                    if existing:
                        if self.duplicate_strategy == DuplicateStrategy.UPDATE:
                            # Update existing record
                            self._update_proxy_record(existing, proxy)
                            session.add(existing)
                            updated_count += 1
                        # SKIP strategy ignores duplicates
                    else:
                        # Add new record
                        new_record = self._create_proxy_record(proxy)
                        session.add(new_record)
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

                # Apply basic filters - simplified for now to avoid type errors
                if filters:
                    # Status filter (healthy/unhealthy proxies)
                    try:
                        if hasattr(filters, 'is_healthy') and getattr(filters, 'is_healthy', None) is not None:
                            is_healthy = getattr(filters, 'is_healthy')
                            status_filter = "active" if is_healthy else "inactive"
                            query = query.where(ProxyRecord.status == status_filter)
                    except AttributeError:
                        pass
                    
                    # Pagination
                    try:
                        if hasattr(filters, 'limit') and getattr(filters, 'limit', None):
                            query = query.limit(getattr(filters, 'limit'))
                        if hasattr(filters, 'offset') and getattr(filters, 'offset', None):
                            query = query.offset(getattr(filters, 'offset'))
                    except AttributeError:
                        pass

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
                        ProxyRecord.host == proxy.host,
                        ProxyRecord.port == proxy.port
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
                        ProxyRecord.host == proxy.host,
                        ProxyRecord.port == proxy.port
                    )
                ).first()

                if record:
                    session.delete(record)
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

                # Calculate average response time for healthy proxies
                avg_response_time = 0.0
                if healthy_records:
                    response_times = [
                        float(r.quality_score) for r in healthy_records 
                        if r.quality_score is not None
                    ]
                    if response_times:
                        avg_response_time = sum(response_times) / len(response_times)

                # Enhanced metrics
                enhanced_metrics = CacheMetrics(
                    total_proxies=total_proxies,
                    healthy_proxies=healthy_proxies,
                    unhealthy_proxies=total_proxies - healthy_proxies,
                    last_updated=datetime.now(timezone.utc),
                    cache_hit_ratio=healthy_proxies / total_proxies if total_proxies > 0 else 0.0,
                    avg_response_time=avg_response_time,
                )

                return enhanced_metrics

        except Exception as e:
            logger.error(f"Failed to get health metrics from SQLite cache: {e}")
            return CacheMetrics(
                total_proxies=0,
                healthy_proxies=0,
                unhealthy_proxies=0,
                last_updated=datetime.now(timezone.utc),
            )

    async def get_connection_metrics(self) -> Dict[str, Any]:
        """Get database connection pool metrics."""
        try:
            # SQLAlchemy connection pool stats
            if hasattr(self, 'engine'):
                pool = self.engine.pool
                return {
                    "active_connections": getattr(pool, "checkedout", lambda: 0)(),
                    "idle_connections": getattr(pool, "checkedin", lambda: 0)(),
                    "total_connections": getattr(pool, "size", lambda: 0)(),
                    "pool_size": self.connection_pool_size,
                }
        except Exception as e:
            logger.debug(f"Connection metrics failed: {e}")
        
        return {
            "active_connections": 0,
            "idle_connections": 0,
            "total_connections": 0,
            "pool_size": self.connection_pool_size,
        }

    async def cleanup_old_metrics(self, days_to_keep: int = 30) -> int:
        """Clean up old health metrics to manage database size."""
        try:
            # For now, just return 0 as we don't have separate health metrics table
            # This could be enhanced to clean up old proxy records
            logger.debug("Cleanup old metrics called - no action taken (placeholder)")
            return 0
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0
