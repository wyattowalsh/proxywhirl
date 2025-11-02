# Data Model: Analytics Engine

**Feature**: 009-analytics-engine-analysis  
**Date**: 2025-11-01  
**Purpose**: Define database schema and entity relationships for analytics engine

---

## Overview

The analytics data model consists of 6 core entities capturing usage telemetry, pre-calculated aggregates, cost tracking, retention policies, export jobs, and access audit trails. The schema is optimized for time-series queries with covering indexes and supports adaptive sampling with statistical weighting.

---

## Entity Definitions

### 1. UsageRecord

**Purpose**: Captures detailed telemetry for each proxy request (or sampled subset at high volumes).

**Attributes**:
- `id` (INTEGER PRIMARY KEY): Auto-incrementing unique identifier
- `timestamp` (INTEGER NOT NULL): Unix timestamp in UTC when request was made
- `proxy_source_id` (TEXT NOT NULL): Foreign key to proxy source identifier
- `application_id` (TEXT NULL): Optional identifier for application making the request
- `target_domain` (TEXT NOT NULL): Domain of the target URL
- `http_method` (TEXT NOT NULL): HTTP method (GET, POST, etc.)
- `success` (INTEGER NOT NULL): Boolean (0/1) indicating request success
- `response_time_ms` (INTEGER NOT NULL): Response time in milliseconds
- `http_status_code` (INTEGER NULL): HTTP status code (200, 404, etc.)
- `bytes_transferred` (INTEGER NULL): Total bytes transferred in request+response
- `error_code` (TEXT NULL): Error code if request failed
- `sampled` (INTEGER NOT NULL DEFAULT 0): Boolean (0/1) indicating if record was sampled
- `sample_weight` (REAL NOT NULL DEFAULT 1.0): Inverse probability weight for statistical adjustment

**Validation Rules**:
- `timestamp` must be >= 0 (valid Unix timestamp)
- `success` must be 0 or 1
- `response_time_ms` must be >= 0
- `http_status_code` must be 100-599 if present
- `bytes_transferred` must be >= 0 if present
- `sample_weight` must be > 0 (typically 1.0 for full capture, 10.0 for 10% sampling)

**Indexes**:
```sql
-- Covering index for time-range + source queries
CREATE INDEX idx_usage_time_source_success 
ON analytics_usage(timestamp DESC, proxy_source_id, success);

-- Covering index for time-range + application queries
CREATE INDEX idx_usage_time_app 
ON analytics_usage(timestamp DESC, application_id, success);

-- Partial index for failures (smaller, faster for error analysis)
CREATE INDEX idx_usage_failures 
ON analytics_usage(timestamp DESC, proxy_source_id, error_code)
WHERE success = 0;
```

**Lifecycle**: created → retained (7 days) → aggregated → deleted

---

### 2. AggregateMetric

**Purpose**: Pre-calculated statistics for time buckets to enable fast dashboard queries.

**Two variants**: `analytics_hourly` and `analytics_daily` with identical schema but different time buckets.

**Attributes**:
- `hour_timestamp` / `day_timestamp` (INTEGER PRIMARY KEY): Start of hour/day (Unix timestamp)
- `proxy_source_id` (TEXT NOT NULL): Proxy source identifier
- `application_id` (TEXT NULL): Optional application identifier
- `request_count` (INTEGER NOT NULL): Total requests in bucket (sample-adjusted)
- `success_count` (INTEGER NOT NULL): Successful requests (sample-adjusted)
- `failure_count` (INTEGER NOT NULL): Failed requests (sample-adjusted)
- `avg_response_time_ms` (REAL NOT NULL): Average response time
- `median_response_time_ms` (REAL NOT NULL): Median response time (50th percentile)
- `p95_response_time_ms` (REAL NOT NULL): 95th percentile response time
- `total_bytes_transferred` (INTEGER NOT NULL): Sum of bytes transferred
- `unique_domains_count` (INTEGER NOT NULL): Approximate count of unique domains
- `sample_adjusted` (INTEGER NOT NULL DEFAULT 0): Boolean indicating if includes sampled data

**Validation Rules**:
- `request_count` must be >= 0
- `success_count` + `failure_count` should equal `request_count`
- All response time metrics must be >= 0
- `total_bytes_transferred` must be >= 0
- `unique_domains_count` must be >= 0

**Indexes**:
```sql
CREATE INDEX idx_hourly_time_source 
ON analytics_hourly(hour_timestamp DESC, proxy_source_id);

CREATE INDEX idx_daily_time_source 
ON analytics_daily(day_timestamp DESC, proxy_source_id);
```

**Lifecycle**: 
- Hourly: calculated daily → retained (30 days) → deleted
- Daily: calculated weekly → retained (365 days) → deleted

---

### 3. CostRecord

**Purpose**: Associates cost data with proxy sources for ROI analysis.

**Attributes**:
- `id` (INTEGER PRIMARY KEY): Auto-incrementing unique identifier
- `proxy_source_id` (TEXT NOT NULL): Proxy source identifier
- `billing_period_start` (INTEGER NOT NULL): Start of billing period (Unix timestamp)
- `billing_period_end` (INTEGER NOT NULL): End of billing period (Unix timestamp)
- `cost_per_request` (REAL NULL): Cost per individual request (if applicable)
- `subscription_cost` (REAL NULL): Fixed subscription cost for period
- `data_transfer_cost` (REAL NULL): Variable cost based on bytes transferred
- `currency` (TEXT NOT NULL DEFAULT 'USD'): Currency code (ISO 4217)
- `cost_model` (TEXT NOT NULL): Cost model type ('per_request', 'subscription', 'data_transfer', 'hybrid')
- `notes` (TEXT NULL): Optional notes about cost calculation

**Validation Rules**:
- `billing_period_end` must be > `billing_period_start`
- At least one cost field (`cost_per_request`, `subscription_cost`, or `data_transfer_cost`) must be non-null
- All cost fields must be >= 0 if present
- `currency` must be valid ISO 4217 code
- `cost_model` must be one of the allowed values

**Indexes**:
```sql
CREATE INDEX idx_cost_source_period 
ON analytics_cost(proxy_source_id, billing_period_start);
```

**Lifecycle**: created → retained (indefinitely or per compliance requirements) → archived

---

### 4. RetentionPolicy

**Purpose**: Configuration for how long different types of analytics data are retained.

**Attributes**:
- `id` (INTEGER PRIMARY KEY): Policy identifier (typically singleton with id=1)
- `raw_data_retention_days` (INTEGER NOT NULL DEFAULT 7): Days to retain full-resolution usage records
- `hourly_aggregate_retention_days` (INTEGER NOT NULL DEFAULT 30): Days to retain hourly rollups
- `daily_aggregate_retention_days` (INTEGER NOT NULL DEFAULT 365): Days to retain daily rollups
- `backup_retention_days` (INTEGER NOT NULL DEFAULT 30): Days to retain database backups
- `immutable_until` (INTEGER NULL): Unix timestamp before which data cannot be deleted (compliance)
- `auto_aggregation_enabled` (INTEGER NOT NULL DEFAULT 1): Boolean to enable/disable scheduled aggregation
- `auto_backup_enabled` (INTEGER NOT NULL DEFAULT 1): Boolean to enable/disable automated backups
- `created_at` (INTEGER NOT NULL): Unix timestamp when policy was created
- `updated_at` (INTEGER NOT NULL): Unix timestamp of last policy update
- `updated_by` (TEXT NULL): User/admin who last updated the policy

**Validation Rules**:
- All retention_days fields must be > 0
- `daily_aggregate_retention_days` should be >= `hourly_aggregate_retention_days`
- `hourly_aggregate_retention_days` should be >= `raw_data_retention_days`
- `immutable_until` must be >= current time if set (prevents backdating)
- `auto_*` fields must be 0 or 1

**No indexes needed** (single-row table, always full scan)

**Lifecycle**: created → updated (admin only) → never deleted

---

### 5. ExportJob

**Purpose**: Tracks analytics data export requests for async processing and audit trails.

**Attributes**:
- `id` (TEXT PRIMARY KEY): UUID for the export job
- `user_id` (TEXT NOT NULL): Identifier of user who requested export
- `created_at` (INTEGER NOT NULL): Unix timestamp when job was created
- `time_range_start` (INTEGER NOT NULL): Start of requested time range
- `time_range_end` (INTEGER NOT NULL): End of requested time range
- `format` (TEXT NOT NULL): Export format ('csv', 'json', 'excel', 'pdf_report')
- `fields` (TEXT NOT NULL): JSON array of field names to include
- `filters` (TEXT NULL): JSON object of additional filters applied
- `status` (TEXT NOT NULL): Job status ('queued', 'processing', 'completed', 'failed')
- `progress_percent` (INTEGER DEFAULT 0): Progress indicator (0-100)
- `file_path` (TEXT NULL): Path to generated export file (when completed)
- `file_size_bytes` (INTEGER NULL): Size of exported file
- `row_count` (INTEGER NULL): Number of rows exported
- `error_message` (TEXT NULL): Error details if status='failed'
- `completed_at` (INTEGER NULL): Unix timestamp when job finished

**Validation Rules**:
- `time_range_end` must be > `time_range_start`
- `format` must be one of allowed values
- `status` must be one of allowed values
- `progress_percent` must be 0-100
- `file_path` required if status='completed'
- `error_message` required if status='failed'

**Indexes**:
```sql
CREATE INDEX idx_export_user_created 
ON analytics_export(user_id, created_at DESC);

CREATE INDEX idx_export_status 
ON analytics_export(status, created_at DESC);
```

**State Transitions**:
- queued → processing → completed
- queued → processing → failed
- No transitions backward or from terminal states (completed/failed)

**Lifecycle**: created → processing → completed/failed → retained (90 days) → deleted

---

### 6. AccessAuditLog

**Purpose**: Records all access to analytics data for security and compliance auditing.

**Attributes**:
- `id` (INTEGER PRIMARY KEY): Auto-incrementing unique identifier
- `timestamp` (INTEGER NOT NULL): Unix timestamp of access event
- `user_id` (TEXT NOT NULL): Identifier of user accessing analytics
- `action` (TEXT NOT NULL): Action performed ('query', 'export', 'config_change', 'backup')
- `resource` (TEXT NULL): Specific resource accessed (e.g., table name, export job ID)
- `time_range_start` (INTEGER NULL): Start of time range for queries
- `time_range_end` (INTEGER NULL): End of time range for queries
- `filters_applied` (TEXT NULL): JSON object of filters used in query
- `ip_address` (TEXT NULL): IP address of client
- `user_agent` (TEXT NULL): User agent string
- `result_count` (INTEGER NULL): Number of rows returned/exported
- `execution_time_ms` (INTEGER NULL): Query execution time
- `success` (INTEGER NOT NULL): Boolean indicating if action succeeded

**Validation Rules**:
- `action` must be one of allowed values
- `success` must be 0 or 1
- `execution_time_ms` must be >= 0 if present
- `result_count` must be >= 0 if present

**Indexes**:
```sql
CREATE INDEX idx_audit_timestamp 
ON analytics_audit(timestamp DESC);

CREATE INDEX idx_audit_user 
ON analytics_audit(user_id, timestamp DESC);

CREATE INDEX idx_audit_action 
ON analytics_audit(action, timestamp DESC);
```

**Lifecycle**: created → retained (per compliance requirements, typically 365+ days) → archived

---

## Entity Relationships

```
┌─────────────────┐
│  UsageRecord    │──┐
│  (raw data)     │  │ aggregated_from
└─────────────────┘  │
                     ├──> ┌──────────────────┐
                     │    │ AggregateMetric  │
┌─────────────────┐  │    │ (hourly/daily)   │
│  CostRecord     │──┘    └──────────────────┘
└─────────────────┘
        │
        └─references─> [proxy_source_id] <─┐
                                            │
┌─────────────────┐                        │
│ RetentionPolicy │──governs──> ┌──────────┴───────┐
│  (config)       │              │   UsageRecord    │
└─────────────────┘              │ AggregateMetric  │
                                 │  CostRecord      │
┌─────────────────┐              └──────────────────┘
│   ExportJob     │──exports──>
└─────────────────┘
        │
        └─logged_in─> ┌──────────────────┐
                      │ AccessAuditLog   │
                      └──────────────────┘
```

**Relationship Details**:
1. **UsageRecord → AggregateMetric**: Many-to-one (many raw records aggregate into one metric)
2. **CostRecord → proxy_source_id**: Many-to-one (multiple billing periods per source)
3. **RetentionPolicy → Data Tables**: One-to-many (single policy governs all tables)
4. **ExportJob → UsageRecord**: Many-to-many (one export includes many records)
5. **All operations → AccessAuditLog**: One-to-one (each action generates one audit entry)

---

## Pydantic Models

```python
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

class UsageRecord(BaseModel):
    """Individual proxy request telemetry."""
    id: Optional[int] = None
    timestamp: int = Field(..., ge=0)
    proxy_source_id: str
    application_id: Optional[str] = None
    target_domain: str
    http_method: str
    success: bool
    response_time_ms: int = Field(..., ge=0)
    http_status_code: Optional[int] = Field(None, ge=100, le=599)
    bytes_transferred: Optional[int] = Field(None, ge=0)
    error_code: Optional[str] = None
    sampled: bool = False
    sample_weight: float = Field(1.0, gt=0.0)
    
    @field_validator('http_method')
    @classmethod
    def validate_http_method(cls, v: str) -> str:
        allowed = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'}
        if v.upper() not in allowed:
            raise ValueError(f'Invalid HTTP method: {v}')
        return v.upper()

class AggregateMetric(BaseModel):
    """Pre-calculated statistics for a time bucket."""
    timestamp: int = Field(..., ge=0)  # hour_timestamp or day_timestamp
    proxy_source_id: str
    application_id: Optional[str] = None
    request_count: int = Field(..., ge=0)
    success_count: int = Field(..., ge=0)
    failure_count: int = Field(..., ge=0)
    avg_response_time_ms: float = Field(..., ge=0.0)
    median_response_time_ms: float = Field(..., ge=0.0)
    p95_response_time_ms: float = Field(..., ge=0.0)
    total_bytes_transferred: int = Field(..., ge=0)
    unique_domains_count: int = Field(..., ge=0)
    sample_adjusted: bool = False

class CostModel(str, Enum):
    """Cost calculation methodology."""
    PER_REQUEST = "per_request"
    SUBSCRIPTION = "subscription"
    DATA_TRANSFER = "data_transfer"
    HYBRID = "hybrid"

class CostRecord(BaseModel):
    """Cost data for a proxy source billing period."""
    id: Optional[int] = None
    proxy_source_id: str
    billing_period_start: int = Field(..., ge=0)
    billing_period_end: int = Field(..., ge=0)
    cost_per_request: Optional[float] = Field(None, ge=0.0)
    subscription_cost: Optional[float] = Field(None, ge=0.0)
    data_transfer_cost: Optional[float] = Field(None, ge=0.0)
    currency: str = Field(default="USD", pattern=r'^[A-Z]{3}$')
    cost_model: CostModel
    notes: Optional[str] = None
    
    @field_validator('billing_period_end')
    @classmethod
    def validate_period(cls, v: int, info) -> int:
        if 'billing_period_start' in info.data and v <= info.data['billing_period_start']:
            raise ValueError('billing_period_end must be after billing_period_start')
        return v

class RetentionPolicy(BaseModel):
    """Configuration for data retention."""
    id: int = 1  # Singleton
    raw_data_retention_days: int = Field(7, gt=0)
    hourly_aggregate_retention_days: int = Field(30, gt=0)
    daily_aggregate_retention_days: int = Field(365, gt=0)
    backup_retention_days: int = Field(30, gt=0)
    immutable_until: Optional[int] = Field(None, ge=0)
    auto_aggregation_enabled: bool = True
    auto_backup_enabled: bool = True
    created_at: int
    updated_at: int
    updated_by: Optional[str] = None

class ExportFormat(str, Enum):
    """Supported export formats."""
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    PDF_REPORT = "pdf_report"

class ExportStatus(str, Enum):
    """Export job lifecycle states."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ExportJob(BaseModel):
    """Analytics data export request."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    created_at: int
    time_range_start: int = Field(..., ge=0)
    time_range_end: int = Field(..., ge=0)
    format: ExportFormat
    fields: List[str]
    filters: Optional[Dict[str, Any]] = None
    status: ExportStatus = ExportStatus.QUEUED
    progress_percent: int = Field(0, ge=0, le=100)
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = Field(None, ge=0)
    row_count: Optional[int] = Field(None, ge=0)
    error_message: Optional[str] = None
    completed_at: Optional[int] = None

class AuditAction(str, Enum):
    """Types of audited actions."""
    QUERY = "query"
    EXPORT = "export"
    CONFIG_CHANGE = "config_change"
    BACKUP = "backup"

class AccessAuditLog(BaseModel):
    """Audit trail for analytics access."""
    id: Optional[int] = None
    timestamp: int = Field(..., ge=0)
    user_id: str
    action: AuditAction
    resource: Optional[str] = None
    time_range_start: Optional[int] = Field(None, ge=0)
    time_range_end: Optional[int] = Field(None, ge=0)
    filters_applied: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    result_count: Optional[int] = Field(None, ge=0)
    execution_time_ms: Optional[int] = Field(None, ge=0)
    success: bool
```

---

## Schema Migration Strategy

**Initial Schema** (v1.0.0):
- All 6 entities with indexes
- Retention policy with sensible defaults
- Sample data for testing

**Future Extensions** (considerations for later versions):
- Partitioning by month for `analytics_usage` (if SQLite adds support)
- Additional indexes based on query patterns
- Materialized views for common aggregations (if performance demands)
- Archive table for historical data beyond retention period

**Backward Compatibility**:
- New columns added with DEFAULT values
- Old columns marked as deprecated before removal
- Schema version tracked in metadata table

---

**Data Model Complete**: Ready for contract generation (Phase 1, Step 2).
