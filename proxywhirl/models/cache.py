"""proxywhirl/models/cache.py -- Cache configuration models for ProxyWhirl

This module contains configuration models for different cache backends,
providing enterprise-grade features and performance tuning options.

Features:
- Backend-specific configuration models
- Performance and reliability tuning
- Data retention and integrity options
- Unified cache configuration interface
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .enums import CacheType


class JsonCacheConfig(BaseModel):
    """Configuration for enterprise JSON cache features."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    # Enterprise features
    compression: bool = Field(
        default=True,
        description="Enable gzip compression for JSON files (saves ~60-80% disk space)",
    )
    enable_backups: bool = Field(
        default=True, description="Create automatic backups for corruption recovery"
    )
    max_backup_count: int = Field(
        default=5, ge=1, le=50, description="Maximum number of backup files to retain"
    )
    integrity_checks: bool = Field(
        default=True, description="Verify file integrity using checksums and validation"
    )
    retry_attempts: int = Field(
        default=3, ge=1, le=10, description="Number of retry attempts for failed operations"
    )

    # Performance tuning
    atomic_writes: bool = Field(
        default=True, description="Use atomic write operations for data consistency"
    )
    flush_interval_seconds: float = Field(
        default=30.0, ge=1.0, le=300.0, description="Automatic flush interval in seconds"
    )


class SqliteCacheConfig(BaseModel):
    """Configuration for enterprise SQLite cache features."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    # Connection and performance
    connection_pool_size: int = Field(
        default=10, ge=1, le=100, description="Maximum connections in the pool"
    )
    connection_pool_recycle: int = Field(
        default=3600, ge=300, le=86400, description="Connection recycling interval in seconds"
    )
    enable_wal: bool = Field(
        default=True, description="Enable Write-Ahead Logging for better concurrency"
    )

    # Data retention
    health_metrics_retention_days: int = Field(
        default=30, ge=1, le=365, description="Number of days to retain health metrics"
    )
    auto_vacuum: bool = Field(default=True, description="Enable automatic database vacuuming")


class CacheConfiguration(BaseModel):
    """Unified cache configuration for all cache types."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    cache_type: CacheType = Field(
        default=CacheType.JSON, description="Type of cache backend to use"
    )
    cache_path: Optional[str] = Field(
        default=None, description="Custom cache file path (auto-generated if None)"
    )

    # Backend-specific configurations
    json_config: JsonCacheConfig = Field(
        default_factory=JsonCacheConfig, description="Configuration for JSON cache backend"
    )
    sqlite_config: SqliteCacheConfig = Field(
        default_factory=SqliteCacheConfig, description="Configuration for SQLite cache backend"
    )

    @field_validator("cache_path")
    @classmethod
    def validate_cache_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate cache path exists and is writable."""
        if v is None:
            return v
        
        path = Path(v)
        if path.exists() and not path.is_file():
            raise ValueError(f"Cache path must be a file, got directory: {v}")
        
        # Check if parent directory exists and is writable
        parent = path.parent
        if not parent.exists():
            raise ValueError(f"Parent directory does not exist: {parent}")
        if not parent.is_dir():
            raise ValueError(f"Parent path is not a directory: {parent}")
        
        return str(path.resolve())
