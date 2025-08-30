"""proxywhirl/caches/db/base.py -- Common database utilities and base classes

Shared utilities and base functionality for SQLite cache implementations.
Contains common imports, utility functions, and base classes used by both
sync and async SQLite implementations.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from loguru import logger

from proxywhirl.models import (
    AnonymityLevel,
    Proxy,
    ProxyScheme,
    ProxyStatus,
)

from .models import ProxyRecord


class SQLiteBase:
    """Base class with common SQLite functionality for both sync/async implementations."""

    def __init__(self, cache_path: Path, enable_wal: bool = True):
        """Initialize base SQLite functionality."""
        self.cache_path = cache_path.with_suffix(".sqlite")
        self.enable_wal = enable_wal

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
        schemes: List[ProxyScheme] = []
        if record.schemes:
            for scheme_str in record.schemes.split(","):
                try:
                    schemes.append(ProxyScheme(scheme_str))
                except ValueError:
                    logger.warning(f"Invalid scheme '{scheme_str}' in proxy record")

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

    def _get_sqlite_pragmas(self) -> List[str]:
        """Get SQLite optimization pragmas."""
        pragmas = [
            "PRAGMA synchronous=NORMAL;",
            "PRAGMA cache_size=10000;",  # 10MB cache
            "PRAGMA temp_store=MEMORY;",
        ]

        if self.enable_wal:
            pragmas.insert(0, "PRAGMA journal_mode=WAL;")

        return pragmas
        return pragmas
