"""proxywhirl/cache_models.py -- Enhanced SQLModel database models for SQLite cache backend

This module provides rich relational database models for the SQLite cache backend,
leveraging SQLModel's advanced features while keeping JSON/memory backends simple.

Key Features:
- UUID primary keys for distributed systems
- Proper foreign key relationships with cascade behaviors
- Decimal precision for performance metrics
- Timezone-aware timestamps
- Health history and performance trend tracking
- Enhanced querying capabilities with indexes
- Rich metadata storage and categorization
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlmodel import (
    Field,
    Relationship,
    SQLModel,
)

from proxywhirl.models import AnonymityLevel, ProxyStatus

# === Core SQLModel Table Models ===


class ProxyRecord(SQLModel, table=True):
    """
    Core proxy record in the enhanced SQLite cache.

    Features:
    - UUID primary key for distributed systems
    - Rich metadata storage beyond basic proxy info
    - Proper indexes for common query patterns
    - Timezone-aware timestamps
    """

    __tablename__ = "proxy_records"

    # Primary identification
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Core proxy information with proper indexing
    host: str = Field(index=True, max_length=253)
    port: int = Field(index=True, ge=1, le=65535)
    ip: str = Field(index=True, max_length=45)  # IPv6 compatible
    schemes: str = Field(description="JSON-serialized list of supported schemes")

    # Geographic and network information with indexes
    country_code: Optional[str] = Field(None, index=True, max_length=2)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    isp: Optional[str] = Field(None, max_length=200)
    organization: Optional[str] = Field(None, max_length=200)

    # Status and quality tracking with indexes
    status: str = Field(default=ProxyStatus.ACTIVE, index=True, max_length=20)
    anonymity: str = Field(default=AnonymityLevel.UNKNOWN, index=True, max_length=20)
    source: Optional[str] = Field(None, index=True, max_length=100)

    # Timestamps (timezone-aware)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    last_checked: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

    # Quality and error tracking
    quality_score: Optional[Decimal] = Field(None, decimal_places=3, max_digits=4)
    blacklist_reason: Optional[str] = Field(None, max_length=500)

    # JSON fields for complex data
    credentials: Optional[str] = Field(None, description="JSON-serialized credentials")
    capabilities: Optional[str] = Field(None, description="JSON-serialized capabilities")
    metadata: str = Field(default="{}", description="JSON-serialized metadata")
    target_health: str = Field(default="{}", description="JSON-serialized target health status")

    # Relationships
    health_metrics: List[HealthMetric] = Relationship(
        back_populates="proxy_record",
        cascade_delete=True,
    )
    performance_history: List[PerformanceHistory] = Relationship(
        back_populates="proxy_record",
        cascade_delete=True,
    )
    proxy_tags: List[ProxyTagLink] = Relationship(
        back_populates="proxy_record",
        cascade_delete=True,
    )


class HealthMetric(SQLModel, table=True):
    """
    Time-series health tracking for proxies.

    Features:
    - Efficient time-series storage
    - Proper foreign key relationships
    - Decimal precision for metrics
    - Configurable data retention
    """

    __tablename__ = "health_metrics"

    # Primary key and relationships
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    proxy_record_id: uuid.UUID = Field(foreign_key="proxy_records.id", index=True)
    proxy_record: Optional[ProxyRecord] = Relationship(back_populates="health_metrics")

    # Time-series data with proper indexing
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

    # Health metrics with decimal precision
    response_time: Optional[Decimal] = Field(None, decimal_places=6, max_digits=10)
    success_rate: Optional[Decimal] = Field(None, decimal_places=4, max_digits=5)
    uptime_percentage: Optional[Decimal] = Field(None, decimal_places=4, max_digits=5)

    # Health check context
    target_url: Optional[str] = Field(None, index=True, max_length=500)
    check_type: str = Field(index=True, max_length=50)
    status_code: Optional[int] = Field(None, index=True)
    error_message: Optional[str] = Field(None, max_length=1000)

    # Additional metrics
    bytes_transferred: Optional[int] = Field(None, ge=0)
    connection_time: Optional[Decimal] = Field(None, decimal_places=6, max_digits=10)

    class Config:
        # Enable foreign key constraint checking
        arbitrary_types_allowed = True


class PerformanceHistory(SQLModel, table=True):
    """
    Historical performance metrics for trend analysis.

    Features:
    - Aggregated performance data
    - Time-window based metrics
    - Statistical calculations
    - Trend analysis support
    """

    __tablename__ = "performance_history"

    # Primary key and relationships
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    proxy_record_id: uuid.UUID = Field(foreign_key="proxy_records.id", index=True)
    proxy_record: Optional[ProxyRecord] = Relationship(back_populates="performance_history")

    # Time window definition
    window_start: datetime = Field(index=True)
    window_end: datetime = Field(index=True)
    window_type: str = Field(index=True, max_length=20)  # hourly, daily, weekly

    # Aggregated performance metrics (decimal precision)
    avg_response_time: Optional[Decimal] = Field(None, decimal_places=6, max_digits=10)
    min_response_time: Optional[Decimal] = Field(None, decimal_places=6, max_digits=10)
    max_response_time: Optional[Decimal] = Field(None, decimal_places=6, max_digits=10)
    p95_response_time: Optional[Decimal] = Field(None, decimal_places=6, max_digits=10)

    # Success and failure metrics
    total_requests: int = Field(default=0, ge=0)
    successful_requests: int = Field(default=0, ge=0)
    failed_requests: int = Field(default=0, ge=0)
    success_rate: Optional[Decimal] = Field(None, decimal_places=4, max_digits=5)

    # Throughput metrics
    requests_per_minute: Optional[Decimal] = Field(None, decimal_places=2, max_digits=10)
    total_bytes: Optional[int] = Field(None, ge=0)
    average_bytes_per_request: Optional[Decimal] = Field(None, decimal_places=2, max_digits=12)

    # Quality scoring
    quality_score: Optional[Decimal] = Field(None, decimal_places=3, max_digits=4)


class Tag(SQLModel, table=True):
    """
    Categorization tags for proxy organization.

    Features:
    - Hierarchical tag system
    - Color coding for UI
    - Description and metadata
    - Usage statistics
    """

    __tablename__ = "tags"

    # Primary identification
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)

    # Hierarchical organization
    parent_tag_id: Optional[uuid.UUID] = Field(None, foreign_key="tags.id")
    parent_tag: Optional[Tag] = Relationship(
        back_populates="child_tags",
        sa_relationship_kwargs={"remote_side": "Tag.id"},
    )
    child_tags: List[Tag] = Relationship(back_populates="parent_tag")

    # Display and metadata
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, max_length=7)  # Hex color code
    icon: Optional[str] = Field(None, max_length=50)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    proxy_tags: List[ProxyTagLink] = Relationship(back_populates="tag")


class ProxyTagLink(SQLModel, table=True):
    """
    Many-to-many relationship between proxies and tags.

    Features:
    - Additional link metadata
    - Automatic timestamping
    - Weight/priority scoring
    """

    __tablename__ = "proxy_tag_links"

    # Composite primary key
    proxy_record_id: uuid.UUID = Field(foreign_key="proxy_records.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)

    # Relationships
    proxy_record: Optional[ProxyRecord] = Relationship(back_populates="proxy_tags")
    tag: Optional[Tag] = Relationship(back_populates="proxy_tags")

    # Link metadata
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_by: Optional[str] = Field(None, max_length=100)  # System or user identifier
    weight: Optional[Decimal] = Field(None, decimal_places=3, max_digits=4)  # 0.0-1.0
    is_auto_assigned: bool = Field(default=True)


class CacheMetadata(SQLModel, table=True):
    """
    Cache configuration and statistics.

    Features:
    - Cache performance metrics
    - Configuration storage
    - Maintenance tracking
    - Usage statistics
    """

    __tablename__ = "cache_metadata"

    # Primary key (singleton pattern)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Cache statistics
    total_proxies: int = Field(default=0, ge=0)
    active_proxies: int = Field(default=0, ge=0)
    healthy_proxies: int = Field(default=0, ge=0)

    # Performance metrics
    cache_hit_rate: Optional[Decimal] = Field(None, decimal_places=4, max_digits=5)
    avg_query_time: Optional[Decimal] = Field(None, decimal_places=6, max_digits=10)

    # Maintenance tracking
    last_cleanup: Optional[datetime] = Field(None)
    last_health_check: Optional[datetime] = Field(None)
    last_performance_analysis: Optional[datetime] = Field(None)

    # Configuration (JSON-serialized)
    configuration: str = Field(default="{}", description="JSON-serialized cache configuration")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Database schema version for migrations
    schema_version: str = Field(default="1.0.0", max_length=20)


# === Utility Functions ===


def get_table_models() -> List[type[SQLModel]]:
    """
    Get all SQLModel table classes for database creation.

    Returns:
        List of SQLModel table classes in dependency order
    """
    return [
        Tag,
        ProxyRecord,
        HealthMetric,
        PerformanceHistory,
        ProxyTagLink,
        CacheMetadata,
    ]


def get_foreign_key_relationships() -> dict[str, List[str]]:
    """
    Get foreign key relationship mapping for understanding dependencies.

    Returns:
        Dictionary mapping table names to their foreign key dependencies
    """
    return {
        "proxy_records": [],
        "tags": ["tags"],  # Self-referential for hierarchical tags
        "health_metrics": ["proxy_records"],
        "performance_history": ["proxy_records"],
        "proxy_tag_links": ["proxy_records", "tags"],
        "cache_metadata": [],
    }
