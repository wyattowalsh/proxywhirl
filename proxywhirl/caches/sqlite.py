"""proxywhirl/caches/sqlite.py -- Enterprise SQLite cache with SQLModel ORM

Production-grade SQLite cache leveraging SQLModel for:
- Rich relational data modeling with health metrics
- Advanced query capabilities with filters and analytics
- Connection pooling and transaction management
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from loguru import logger
from sqlalchemy import text
from sqlmodel import Field, SQLModel, create_engine, select

from proxywhirl.caches.base import BaseProxyCache, CacheFilters, CacheMetrics
from proxywhirl.models import CacheType, Proxy, ProxyStatus


class ProxyRecord(SQLModel, table=True):
    """Enhanced proxy record with metadata and health tracking."""

    __tablename__ = "proxy_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    host: str = Field(index=True, max_length=255)
    port: int = Field(index=True)
    schemes: str = Field(default="http")
    status: str = Field(default="unknown", index=True)
    response_time: Optional[float] = Field(default=None, index=True)
    quality_score: Optional[float] = Field(default=None, index=True)
    success_rate: Optional[float] = Field(default=None, index=True)
    anonymity: Optional[str] = Field(default=None, index=True)
    country_code: Optional[str] = Field(default=None, index=True, max_length=3)
    source: Optional[str] = Field(default=None, index=True, max_length=100)
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    last_checked: Optional[datetime] = Field(default=None, index=True)
    check_count: int = Field(default=0)
    failure_count: int = Field(default=0)


class SQLiteProxyCache(BaseProxyCache):
    """Enterprise SQLite cache with SQLModel ORM."""

    def __init__(self, db_path: str | Path = "proxies.db"):
        super().__init__(CacheType.SQLITE, str(db_path))
        self.db_path = Path(db_path)
        self._setup_engine()

    def _setup_engine(self) -> None:
        """Setup SQLAlchemy engine with SQLite optimizations."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        sqlite_url = f"sqlite:///{self.db_path}"
        self.engine = create_engine(sqlite_url, echo=False)

        # Create tables
        SQLModel.metadata.create_all(self.engine)
        logger.debug(f"SQLite cache initialized at {self.db_path}")

    def _proxy_to_record(self, proxy: Proxy) -> ProxyRecord:
        """Convert Proxy to ProxyRecord."""
        return ProxyRecord(
            host=proxy.host,
            port=proxy.port,
            schemes=json.dumps([s.value if hasattr(s, "value") else str(s) for s in proxy.schemes]),
            status=proxy.status.value if hasattr(proxy.status, "value") else str(proxy.status),
            response_time=proxy.response_time,
            quality_score=getattr(proxy, "quality_score", None),
            success_rate=getattr(proxy, "success_rate", None),
            anonymity=(
                proxy.anonymity.value if hasattr(proxy.anonymity, "value") else str(proxy.anonymity)
            ),
            country_code=getattr(proxy, "country_code", None),
            source=getattr(proxy, "source", None),
            last_checked=proxy.last_checked if hasattr(proxy, "last_checked") else None,
        )

    def _record_to_proxy(self, record: ProxyRecord) -> Proxy:
        """Convert ProxyRecord to Proxy."""
        from proxywhirl.models import AnonymityLevel, Scheme

        # Parse schemes
        try:
            schemes_data = json.loads(record.schemes)
            schemes = [Scheme(s) for s in schemes_data]
        except (json.JSONDecodeError, ValueError, TypeError):
            schemes = [Scheme.HTTP]
        
        # Parse anonymity
        try:
            anonymity = (
                AnonymityLevel(record.anonymity) if record.anonymity else AnonymityLevel.UNKNOWN
            )
        except (ValueError, TypeError):
            anonymity = AnonymityLevel.UNKNOWN
        
        # Parse status
        try:
            status = ProxyStatus(record.status)
        except (ValueError, TypeError):
            status = ProxyStatus.UNKNOWN        return Proxy(
            host=record.host,
            port=record.port,
            schemes=schemes,
            anonymity=anonymity,
            response_time=record.response_time,
            source=record.source,
            status=status,
        )

    async def add_proxies(self, proxies: List[Proxy]) -> None:
        """Add proxies with upsert logic."""
        if not proxies:
            return

        from sqlmodel import Session

        with Session(self.engine) as session:
            for proxy in proxies:
                # Check if proxy exists
                stmt = select(ProxyRecord).where(
                    ProxyRecord.host == proxy.host, ProxyRecord.port == proxy.port
                )
                existing = session.exec(stmt).first()

                if existing:
                    # Update existing
                    existing.last_seen = datetime.now(timezone.utc)
                    existing.status = (
                        proxy.status.value if hasattr(proxy.status, "value") else str(proxy.status)
                    )
                    existing.response_time = proxy.response_time
                    session.add(existing)
                else:
                    # Add new
                    record = self._proxy_to_record(proxy)
                    session.add(record)

            session.commit()

    async def get_proxies(self, filters: Optional[CacheFilters] = None) -> List[Proxy]:
        """Get proxies with filtering."""
        from sqlmodel import Session

        with Session(self.engine) as session:
            stmt = select(ProxyRecord)

            # Apply filters
            if filters:
                if filters.countries:
                    stmt = stmt.where(ProxyRecord.country_code.in_(filters.countries))
                if filters.healthy_only:
                    stmt = stmt.where(ProxyRecord.status == "active")

            records = session.exec(stmt).all()
            return [self._record_to_proxy(record) for record in records]

    async def update_proxy(self, proxy: Proxy) -> None:
        """Update proxy."""
        from sqlmodel import Session

        with Session(self.engine) as session:
            stmt = select(ProxyRecord).where(
                ProxyRecord.host == proxy.host, ProxyRecord.port == proxy.port
            )
            existing = session.exec(stmt).first()

            if existing:
                existing.status = (
                    proxy.status.value if hasattr(proxy.status, "value") else str(proxy.status)
                )
                existing.response_time = proxy.response_time
                existing.last_seen = datetime.now(timezone.utc)
                existing.check_count += 1
                session.add(existing)
                session.commit()

    async def remove_proxy(self, proxy: Proxy) -> None:
        """Remove proxy."""
        from sqlmodel import Session

        with Session(self.engine) as session:
            stmt = select(ProxyRecord).where(
                ProxyRecord.host == proxy.host, ProxyRecord.port == proxy.port
            )
            record = session.exec(stmt).first()
            if record:
                session.delete(record)
                session.commit()

    async def clear(self) -> None:
        """Clear all data."""
        from sqlmodel import Session

        with Session(self.engine) as session:
            session.exec(text("DELETE FROM proxy_records"))
            session.commit()

    async def get_health_metrics(self) -> CacheMetrics:
        """Get health metrics."""
        from sqlmodel import Session

        with Session(self.engine) as session:
            total_count = session.exec(select(ProxyRecord)).fetchall()
            total_proxies = len(total_count) if total_count else 0

            active_count = session.exec(
                select(ProxyRecord).where(ProxyRecord.status == "active")
            ).fetchall()
            active_proxies = len(active_count) if active_count else 0

            return CacheMetrics(
                total_proxies=total_proxies,
                active_proxies=active_proxies,
                success_rate=active_proxies / total_proxies if total_proxies > 0 else 0.0,
                average_response_time=None,
                last_updated=datetime.now(timezone.utc),
                health_distribution={},
                top_countries={},
                cache_type=self.cache_type.value,
                cache_path=str(self.cache_path) if self.cache_path else None,
            )

    async def _update_cache_metrics(self) -> None:
        """Update internal metrics."""
        self._metrics = await self.get_health_metrics()
