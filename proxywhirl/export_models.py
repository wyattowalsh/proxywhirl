"""
Data models for ProxyWhirl export functionality using Pydantic v2.

This module provides comprehensive models for exporting proxy data, metrics,
logs, and configurations in various formats with filtering, compression, and
validation capabilities.
"""

import gzip
import json
import zipfile
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# ENUMS
# ============================================================================


class ExportFormat(str, Enum):
    """Supported export output formats."""

    CSV       = "csv"
    JSON      = "json"
    JSONL     = "jsonl"
    YAML      = "yaml"
    TEXT      = "text"
    MARKDOWN  = "markdown"


class ExportType(str, Enum):
    """Types of data that can be exported."""

    PROXIES        = "proxies"
    METRICS        = "metrics"
    LOGS           = "logs"
    CONFIGURATION  = "configuration"
    HEALTH_STATUS  = "health_status"
    CACHE_DATA     = "cache_data"


class ExportStatus(str, Enum):
    """Export job execution status."""

    PENDING    = "pending"
    RUNNING    = "running"
    COMPLETED  = "completed"
    FAILED     = "failed"
    CANCELLED  = "cancelled"


class CompressionType(str, Enum):
    """Supported compression types for exports."""

    NONE  = "none"
    GZIP  = "gzip"
    ZIP   = "zip"


class ExportDestinationType(str, Enum):
    """Supported export destination types."""

    LOCAL_FILE  = "local_file"
    MEMORY      = "memory"
    S3          = "s3"
    HTTP        = "http"


# ============================================================================
# FILTER MODELS
# ============================================================================


class ProxyExportFilter(BaseModel):
    """Filter criteria for proxy exports."""

    model_config = ConfigDict(extra="forbid")

    # Status filters
    health_status: Optional[list[str]]    = Field(None, description="Filter by health status")
    source: Optional[list[str]]           = Field(None, description="Filter by proxy source")
    protocol: Optional[list[str]]         = Field(None, description="Filter by protocol (http, socks4, socks5)")
    
    # Performance filters
    min_success_rate: Optional[float]     = Field(None, ge=0.0, le=1.0, description="Minimum success rate (0.0-1.0)")
    max_response_time_ms: Optional[float] = Field(None, gt=0, description="Maximum average response time in ms")
    min_requests: Optional[int]           = Field(None, ge=0, description="Minimum total requests")
    
    # Time filters
    created_after: Optional[datetime]     = Field(None, description="Filter proxies created after this time")
    created_before: Optional[datetime]    = Field(None, description="Filter proxies created before this time")
    last_success_after: Optional[datetime] = Field(None, description="Filter proxies with success after this time")
    
    # Field selection
    include_fields: Optional[list[str]]   = Field(None, description="Specific fields to include in export")
    exclude_fields: Optional[list[str]]   = Field(None, description="Specific fields to exclude from export")


class MetricsExportFilter(BaseModel):
    """Filter criteria for metrics exports."""

    model_config = ConfigDict(extra="forbid")

    # Time range (required for metrics)
    start_time: datetime                  = Field(description="Start time for metrics export")
    end_time: datetime                    = Field(description="End time for metrics export")
    
    # Metric selection
    metric_names: Optional[list[str]]     = Field(None, description="Specific metrics to export")
    
    # Aggregation
    aggregation_interval: Optional[str]   = Field(None, description="Aggregation interval (1m, 5m, 1h, 1d)")
    
    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, v: datetime, info: Any) -> datetime:
        """Ensure end_time is after start_time."""
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class LogExportFilter(BaseModel):
    """Filter criteria for log exports."""

    model_config = ConfigDict(extra="forbid")

    # Time range
    start_time: Optional[datetime]      = Field(None, description="Start time for log export")
    end_time: Optional[datetime]        = Field(None, description="End time for log export")
    
    # Log level filters
    log_levels: Optional[list[str]]     = Field(None, description="Filter by log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    
    # Component filters
    components: Optional[list[str]]     = Field(None, description="Filter by component/module names")
    
    # Content filters
    search_text: Optional[str]          = Field(None, description="Search for specific text in logs")
    exclude_text: Optional[str]         = Field(None, description="Exclude logs containing this text")
    
    # Limit
    max_entries: Optional[int]          = Field(None, gt=0, description="Maximum number of log entries to export")


class ConfigurationExportFilter(BaseModel):
    """Filter criteria for configuration exports."""

    model_config = ConfigDict(extra="forbid")

    # Section selection
    include_sections: Optional[list[str]] = Field(None, description="Specific config sections to include")
    exclude_sections: Optional[list[str]] = Field(None, description="Specific config sections to exclude")
    
    # Security
    redact_secrets: bool                  = Field(True, description="Redact sensitive values (passwords, API keys)")
    include_defaults: bool                = Field(False, description="Include default configuration values")


# ============================================================================
# DESTINATION MODELS
# ============================================================================


class LocalFileDestination(BaseModel):
    """Local file system export destination."""

    model_config = ConfigDict(extra="forbid")

    type: Literal[ExportDestinationType.LOCAL_FILE] = ExportDestinationType.LOCAL_FILE
    file_path: Path                                  = Field(description="Absolute or relative file path")
    overwrite: bool                                  = Field(False, description="Overwrite existing file")
    create_directories: bool                         = Field(True, description="Create parent directories if needed")


class MemoryDestination(BaseModel):
    """In-memory export destination (returns data directly)."""

    model_config = ConfigDict(extra="forbid")

    type: Literal[ExportDestinationType.MEMORY] = ExportDestinationType.MEMORY


class S3Destination(BaseModel):
    """AWS S3 export destination."""

    model_config = ConfigDict(extra="forbid")

    type: Literal[ExportDestinationType.S3] = ExportDestinationType.S3
    bucket: str                              = Field(description="S3 bucket name")
    key: str                                 = Field(description="S3 object key (path)")
    region: Optional[str]                    = Field(None, description="AWS region")
    access_key_id: Optional[str]             = Field(None, description="AWS access key ID")
    secret_access_key: Optional[str]         = Field(None, description="AWS secret access key")


class HTTPDestination(BaseModel):
    """HTTP/HTTPS export destination (POST upload)."""

    model_config = ConfigDict(extra="forbid")

    type: Literal[ExportDestinationType.HTTP] = ExportDestinationType.HTTP
    url: str                                   = Field(description="HTTP endpoint URL")
    method: str                                = Field("POST", description="HTTP method")
    headers: Optional[dict[str, str]]          = Field(None, description="HTTP headers")
    auth_token: Optional[str]                  = Field(None, description="Bearer token for authentication")


# Union type for all destination types
ExportDestination = Union[LocalFileDestination, MemoryDestination, S3Destination, HTTPDestination]


# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================


class ExportConfig(BaseModel):
    """Configuration for export operations."""

    model_config = ConfigDict(extra="forbid")

    # Export type and format
    export_type: ExportType            = Field(description="Type of data to export")
    export_format: ExportFormat        = Field(description="Output format")
    
    # Destination
    destination: ExportDestination     = Field(description="Export destination configuration")
    
    # Compression
    compression: CompressionType       = Field(CompressionType.NONE, description="Compression type")
    
    # Filters (type-specific)
    proxy_filter: Optional[ProxyExportFilter]          = Field(None, description="Filters for proxy exports")
    metrics_filter: Optional[MetricsExportFilter]      = Field(None, description="Filters for metrics exports")
    log_filter: Optional[LogExportFilter]              = Field(None, description="Filters for log exports")
    config_filter: Optional[ConfigurationExportFilter] = Field(None, description="Filters for config exports")
    
    # Options
    pretty_print: bool                 = Field(True, description="Pretty-print JSON/YAML output")
    include_metadata: bool             = Field(True, description="Include export metadata header")
    validate_before_export: bool       = Field(True, description="Validate data before exporting")
    streaming: bool                    = Field(False, description="Use streaming for large exports")
    chunk_size: int                    = Field(1000, gt=0, description="Chunk size for streaming exports")


# ============================================================================
# EXPORT JOB MODELS
# ============================================================================


class ExportMetadata(BaseModel):
    """Metadata about an export operation."""

    model_config = ConfigDict(extra="forbid")

    export_id: UUID                    = Field(default_factory=uuid4, description="Unique export ID")
    export_type: ExportType            = Field(description="Type of data exported")
    export_format: ExportFormat        = Field(description="Output format used")
    created_at: datetime               = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str]          = Field(None, description="User/system that created export")
    proxywhirl_version: str            = Field("1.0.0", description="ProxyWhirl version")
    total_records: Optional[int]       = Field(None, description="Total number of records exported")
    file_size_bytes: Optional[int]     = Field(None, description="Export file size in bytes")
    compression_used: CompressionType  = Field(CompressionType.NONE)
    filters_applied: Optional[dict[str, Any]] = Field(None, description="Filters that were applied")


class ExportProgress(BaseModel):
    """Progress tracking for export operations."""

    model_config = ConfigDict(extra="forbid")

    total_records: int                 = Field(0, description="Total records to export")
    processed_records: int             = Field(0, description="Records processed so far")
    failed_records: int                = Field(0, description="Records that failed validation/export")
    current_phase: str                 = Field("initializing", description="Current export phase")
    started_at: Optional[datetime]     = Field(None)
    estimated_completion: Optional[datetime] = Field(None)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_records == 0:
            return 0.0
        return (self.processed_records / self.total_records) * 100.0


class ExportJob(BaseModel):
    """Complete export job with configuration, status, and results."""

    model_config = ConfigDict(extra="forbid")

    # Identity
    job_id: UUID                       = Field(default_factory=uuid4, description="Unique job ID")
    
    # Configuration
    config: ExportConfig               = Field(description="Export configuration")
    
    # Status
    status: ExportStatus               = Field(ExportStatus.PENDING, description="Current job status")
    
    # Progress
    progress: ExportProgress           = Field(default_factory=ExportProgress)
    
    # Timestamps
    created_at: datetime               = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime]     = Field(None)
    completed_at: Optional[datetime]   = Field(None)
    
    # Results
    result_path: Optional[str]         = Field(None, description="Path to exported file (if local)")
    result_data: Optional[Any]         = Field(None, description="Exported data (if memory destination)")
    error_message: Optional[str]       = Field(None, description="Error message if failed")
    
    # Metadata
    metadata: Optional[ExportMetadata] = Field(None, description="Export metadata")
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate export duration in seconds."""
        if not self.started_at:
            return None
        end_time = self.completed_at or datetime.now(timezone.utc)
        return (end_time - self.started_at).total_seconds()


# ============================================================================
# EXPORT RESULT MODELS
# ============================================================================


class ExportResult(BaseModel):
    """Result of an export operation."""

    model_config = ConfigDict(extra="forbid")

    success: bool                      = Field(description="Whether export succeeded")
    job_id: UUID                       = Field(description="Export job ID")
    export_type: ExportType            = Field(description="Type of data exported")
    export_format: ExportFormat        = Field(description="Output format")
    
    # Results
    destination_path: Optional[str]    = Field(None, description="Path where data was exported")
    data: Optional[Any]                = Field(None, description="Exported data (for memory destination)")
    records_exported: int              = Field(0, description="Number of records exported")
    file_size_bytes: Optional[int]     = Field(None, description="Size of exported file")
    
    # Timing
    duration_seconds: float            = Field(description="Export duration")
    
    # Metadata
    metadata: Optional[ExportMetadata] = Field(None, description="Export metadata")
    
    # Error info
    error: Optional[str]               = Field(None, description="Error message if failed")


class ExportHistoryEntry(BaseModel):
    """Historical record of an export operation."""

    model_config = ConfigDict(extra="forbid")

    job_id: UUID                       = Field(description="Export job ID")
    export_type: ExportType            = Field(description="Type of data exported")
    export_format: ExportFormat        = Field(description="Output format")
    status: ExportStatus               = Field(description="Final status")
    created_at: datetime               = Field(description="When export was created")
    completed_at: Optional[datetime]   = Field(None, description="When export completed")
    duration_seconds: Optional[float]  = Field(None, description="Export duration")
    records_exported: int              = Field(0, description="Number of records exported")
    file_size_bytes: Optional[int]     = Field(None, description="Size of exported file")
    destination_path: Optional[str]    = Field(None, description="Export destination")
    error: Optional[str]               = Field(None, description="Error message if failed")
