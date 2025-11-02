# Data Model: Automated Reporting System

**Feature**: 010-automated-report  
**Date**: 2025-11-02  
**Status**: Complete

## Overview

This document defines all data entities, relationships, validation rules, and state transitions for the automated reporting system. All models use Pydantic v2 for runtime validation and are fully type-hinted for mypy --strict compliance.

---

## Core Entities

### 1. Report

Represents a generated report with metadata and content.

**Fields**:
- `id`: `str` - UUID v4 identifier (generated on creation)
- `name`: `str` - Human-readable report name (e.g., "Performance Report 2025-11-02")
- `report_type`: `Literal["performance", "health", "aggregate", "custom"]` - Report category
- `format`: `Literal["json", "csv", "html", "pdf"]` - Output format
- `generated_at`: `datetime` - Timestamp when report was generated (UTC)
- `time_range_start`: `datetime` - Start of data time range (UTC)
- `time_range_end`: `datetime` - End of data time range (UTC)
- `parameters`: `Dict[str, Any]` - Generation parameters (filters, options, etc.)
- `file_path`: `Path | None` - Path to generated report file (None if in-memory only)
- `file_size_bytes`: `int | None` - Size of generated file in bytes
- `generation_time_ms`: `int` - Time taken to generate report in milliseconds
- `status`: `Literal["generating", "completed", "failed"]` - Generation status
- `error_message`: `str | None` - Error message if generation failed

**Validation Rules**:
- `id` must be valid UUID v4 format
- `name` must be 1-200 characters
- `time_range_end` must be after `time_range_start`
- `time_range_end` must not be in future
- `generated_at` must be in UTC timezone
- `file_size_bytes` must be positive if present
- `generation_time_ms` must be non-negative

**State Transitions**:
```
[New] -> generating -> completed
                   \-> failed
```

**Relationships**:
- May reference one `ReportTemplate` (if generated from template)
- Tracked by one `ReportHistory` entry
- Contains aggregated data from multiple `ReportMetric` instances

**Example**:
```python
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Dict, Any
import uuid

class Report(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(min_length=1, max_length=200)
    report_type: Literal["performance", "health", "aggregate", "custom"]
    format: Literal["json", "csv", "html", "pdf"]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    time_range_start: datetime
    time_range_end: datetime
    parameters: Dict[str, Any] = Field(default_factory=dict)
    file_path: Path | None = None
    file_size_bytes: int | None = Field(None, gt=0)
    generation_time_ms: int = Field(ge=0)
    status: Literal["generating", "completed", "failed"] = "generating"
    error_message: str | None = None
    
    @property
    def duration_days(self) -> float:
        """Calculate time range duration in days."""
        return (self.time_range_end - self.time_range_start).total_seconds() / 86400
```

---

### 2. ReportTemplate

Represents a customizable report structure defining metrics, filters, and formatting.

**Fields**:
- `id`: `str` - UUID v4 identifier
- `name`: `str` - Unique template name (slug format: lowercase, hyphens)
- `description`: `str` - Human-readable template description
- `report_type`: `Literal["performance", "health", "aggregate", "custom"]` - Base report type
- `metrics`: `List[str]` - Metric names to include (validated against available metrics)
- `filters`: `Dict[str, Any]` - Filter criteria (proxy URLs, sources, tags, etc.)
- `thresholds`: `Dict[str, float]` - Threshold values for highlighting (e.g., {"success_rate": 95.0})
- `output_format`: `Literal["json", "csv", "html", "pdf"]` - Default output format
- `created_at`: `datetime` - Template creation timestamp (UTC)
- `updated_at`: `datetime` - Last update timestamp (UTC)
- `created_by`: `str | None` - User identifier (if applicable)
- `is_system`: `bool` - True for built-in templates, False for user-created

**Validation Rules**:
- `name` must match pattern: `^[a-z0-9-]+$` (slug format)
- `name` must be 3-50 characters
- `description` must be 10-500 characters
- `metrics` list must not be empty
- Each metric name must exist in available metrics registry
- `thresholds` keys must match metric names in `metrics` list
- `is_system` templates cannot be modified or deleted

**Relationships**:
- Used to generate multiple `Report` instances
- References `MetricDefinition` entries via `metrics` list

**Example**:
```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import List, Dict, Any, Literal
import re

class ReportTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(min_length=3, max_length=50, pattern=r"^[a-z0-9-]+$")
    description: str = Field(min_length=10, max_length=500)
    report_type: Literal["performance", "health", "aggregate", "custom"]
    metrics: List[str] = Field(min_length=1)
    filters: Dict[str, Any] = Field(default_factory=dict)
    thresholds: Dict[str, float] = Field(default_factory=dict)
    output_format: Literal["json", "csv", "html", "pdf"] = "json"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str | None = None
    is_system: bool = False
    
    @field_validator("thresholds")
    @classmethod
    def validate_thresholds_match_metrics(cls, v, info):
        """Ensure all threshold keys exist in metrics list."""
        if "metrics" in info.data:
            metrics_set = set(info.data["metrics"])
            invalid_keys = set(v.keys()) - metrics_set
            if invalid_keys:
                raise ValueError(f"Threshold keys not in metrics: {invalid_keys}")
        return v
```

---

### 3. ReportSchedule

Represents an automated report generation schedule.

**Fields**:
- `id`: `str` - UUID v4 identifier
- `name`: `str` - Schedule name (e.g., "Daily Performance Report")
- `description`: `str` - Schedule description
- `template_id`: `str` - Reference to ReportTemplate UUID
- `cron_expression`: `str` - Cron format schedule (e.g., "0 9 * * *" for daily 9 AM)
- `time_range_spec`: `Literal["last_hour", "last_24h", "last_7d", "last_30d", "yesterday"]` - Data range
- `output_directory`: `Path` - Directory where reports will be saved
- `enabled`: `bool` - Whether schedule is active
- `created_at`: `datetime` - Schedule creation timestamp (UTC)
- `last_run_at`: `datetime | None` - Last successful execution timestamp (UTC)
- `next_run_at`: `datetime | None` - Calculated next execution timestamp (UTC)
- `run_count`: `int` - Total number of successful executions
- `failure_count`: `int` - Number of consecutive failures
- `max_retries`: `int` - Maximum retry attempts on failure (default 3)
- `retry_delay_seconds`: `int` - Delay between retries (default 300 = 5 minutes)

**Validation Rules**:
- `cron_expression` must be valid cron syntax (5 fields: minute hour day month weekday)
- `output_directory` must be writable
- `max_retries` must be 0-10
- `retry_delay_seconds` must be 60-3600 (1 minute to 1 hour)
- `failure_count` resets to 0 after successful run
- Schedule disabled automatically if `failure_count >= max_retries`

**State Transitions**:
```
[Created] -> enabled=True -> [Active] -> (schedule fires) -> [Executing]
                                                          \-> [Failed] (retry)
                                                          \-> [Completed] -> [Active]
          -> enabled=False -> [Inactive]
```

**Relationships**:
- References one `ReportTemplate` (must exist)
- Generates multiple `Report` instances over time
- Creates `ReportHistory` entries for each execution

**Example**:
```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
import croniter

class ReportSchedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(max_length=500)
    template_id: str  # UUID reference
    cron_expression: str = Field(example="0 9 * * *")
    time_range_spec: Literal["last_hour", "last_24h", "last_7d", "last_30d", "yesterday"]
    output_directory: Path
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    run_count: int = Field(default=0, ge=0)
    failure_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: int = Field(default=300, ge=60, le=3600)
    
    @field_validator("cron_expression")
    @classmethod
    def validate_cron(cls, v):
        """Validate cron expression syntax."""
        try:
            croniter.croniter(v)
        except (ValueError, KeyError):
            raise ValueError(f"Invalid cron expression: {v}")
        return v
    
    def calculate_next_run(self) -> datetime:
        """Calculate next execution time from current time."""
        base = datetime.now(timezone.utc)
        cron = croniter.croniter(self.cron_expression, base)
        return cron.get_next(datetime)
```

---

### 4. ReportHistory

Represents historical record of report generation attempts.

**Fields**:
- `id`: `str` - UUID v4 identifier
- `report_id`: `str` - Reference to Report UUID
- `schedule_id`: `str | None` - Reference to ReportSchedule UUID (if scheduled)
- `started_at`: `datetime` - Generation start timestamp (UTC)
- `completed_at`: `datetime | None` - Generation completion timestamp (UTC)
- `status`: `Literal["generating", "completed", "failed"]` - Final status
- `error_message`: `str | None` - Error message if failed
- `retry_attempt`: `int` - Retry attempt number (0 for first attempt)
- `retention_expires_at`: `datetime` - Timestamp when history entry should be deleted

**Validation Rules**:
- `completed_at` must be after `started_at` if present
- `retention_expires_at` must be in future
- `retry_attempt` must be non-negative

**Relationships**:
- References one `Report` (must exist)
- May reference one `ReportSchedule` (if scheduled generation)

**Example**:
```python
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta

class ReportHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_id: str  # UUID reference
    schedule_id: str | None = None  # UUID reference if scheduled
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    status: Literal["generating", "completed", "failed"] = "generating"
    error_message: str | None = None
    retry_attempt: int = Field(default=0, ge=0)
    retention_expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=30)
    )
```

---

### 5. ReportMetric

Represents a single metric data point for inclusion in reports.

**Fields**:
- `name`: `str` - Metric name (e.g., "proxy_requests_total", "success_rate")
- `value`: `float | int | str` - Metric value
- `timestamp`: `datetime` - Measurement timestamp (UTC)
- `proxy_url`: `str | None` - Associated proxy URL (redacted)
- `source`: `str | None` - Proxy source identifier
- `labels`: `Dict[str, str]` - Additional dimensional labels (tags, categories)

**Validation Rules**:
- `name` must match pattern: `^[a-z_][a-z0-9_]*$` (snake_case)
- `proxy_url` must be redacted format if present (no credentials)
- `timestamp` must be in UTC timezone

**Example**:
```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Dict, Union

class ReportMetric(BaseModel):
    name: str = Field(pattern=r"^[a-z_][a-z0-9_]*$")
    value: Union[float, int, str]
    timestamp: datetime
    proxy_url: str | None = None
    source: str | None = None
    labels: Dict[str, str] = Field(default_factory=dict)
    
    @field_validator("proxy_url")
    @classmethod
    def validate_redacted_url(cls, v):
        """Ensure proxy URL is redacted (no credentials)."""
        if v and (":" in v.split("//")[1].split("@")[0] if "@" in v else False):
            raise ValueError("Proxy URL must be redacted (no credentials)")
        return v
```

---

### 6. MetricsDataStore

Abstract interface for accessing metrics data (decouples from 008-metrics implementation).

**Interface Methods**:
- `get_proxy_metrics(start_time, end_time, proxy_filter=None) -> Iterator[ReportMetric]`
- `get_aggregate_stats(start_time, end_time) -> Dict[str, Any]`
- `get_source_breakdown(start_time, end_time) -> Dict[str, Dict[str, Any]]`
- `get_available_metrics() -> List[str]`
- `validate_metric_name(name: str) -> bool`

**Implementations**:
- `SQLiteMetricsCollector` - Queries 008-metrics SQLite database
- `InMemoryMetricsCollector` - Uses ProxyRotator internal state (for testing)
- `MockMetricsCollector` - Returns fake data (for unit tests)

**Example**:
```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterator, Dict, Any, List

class MetricsDataStore(ABC):
    """Abstract interface for metrics data access."""
    
    @abstractmethod
    def get_proxy_metrics(
        self,
        start_time: datetime,
        end_time: datetime,
        proxy_filter: List[str] | None = None
    ) -> Iterator[ReportMetric]:
        """Retrieve proxy metrics for time range (streaming)."""
        pass
    
    @abstractmethod
    def get_aggregate_stats(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get aggregate statistics (totals, averages, percentiles)."""
        pass
    
    @abstractmethod
    def get_available_metrics(self) -> List[str]:
        """List all available metric names."""
        pass
```

---

## Entity Relationships Diagram

```
ReportTemplate (1) --generates--> (*) Report
ReportSchedule (1) --uses--> (1) ReportTemplate
ReportSchedule (1) --generates--> (*) Report
Report (1) --tracked-by--> (1) ReportHistory
ReportHistory (*) --belongs-to--> (1) ReportSchedule [optional]
Report (*) --aggregates--> (*) ReportMetric
MetricsDataStore --provides--> (*) ReportMetric
```

---

## File Storage Schema

### Report Files

**Naming Convention**: `{report_type}_{timestamp}_{id}.{format}`  
**Example**: `performance_20251102T093045Z_a1b2c3d4.json`

**Directory Structure**:
```
reports/
├── on-demand/          # User-requested reports
│   ├── 2025-11-02/
│   │   ├── performance_20251102T093045Z_a1b2c3d4.json
│   │   └── health_20251102T140532Z_e5f6g7h8.pdf
│   └── 2025-11-03/
└── scheduled/          # Automated scheduled reports
    ├── daily-performance/
    │   ├── 2025-11-02.json
    │   └── 2025-11-03.json
    └── weekly-health/
        └── 2025-W44.pdf
```

### Template Files

**Naming Convention**: `{template_name}.json`  
**Example**: `daily-performance-summary.json`

**Directory Structure**:
```
templates/
├── system/             # Built-in templates (read-only)
│   ├── basic-performance.json
│   ├── detailed-health.json
│   └── aggregate-stats.json
└── user/               # User-created templates (read-write)
    ├── custom-dashboard.json
    └── compliance-report.json
```

---

## Database Schema (SQLite via SQLModel)

### Table: report_history

```sql
CREATE TABLE report_history (
    id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL,
    schedule_id TEXT,
    started_at TEXT NOT NULL,  -- ISO 8601 UTC
    completed_at TEXT,         -- ISO 8601 UTC
    status TEXT NOT NULL CHECK(status IN ('generating', 'completed', 'failed')),
    error_message TEXT,
    retry_attempt INTEGER NOT NULL DEFAULT 0,
    retention_expires_at TEXT NOT NULL,  -- ISO 8601 UTC
    FOREIGN KEY (schedule_id) REFERENCES report_schedules(id) ON DELETE CASCADE
);

CREATE INDEX idx_report_history_retention ON report_history(retention_expires_at);
CREATE INDEX idx_report_history_schedule ON report_history(schedule_id);
```

### Table: report_schedules

```sql
CREATE TABLE report_schedules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    template_id TEXT NOT NULL,
    cron_expression TEXT NOT NULL,
    time_range_spec TEXT NOT NULL CHECK(time_range_spec IN ('last_hour', 'last_24h', 'last_7d', 'last_30d', 'yesterday')),
    output_directory TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,  -- SQLite boolean
    created_at TEXT NOT NULL,
    last_run_at TEXT,
    next_run_at TEXT,
    run_count INTEGER NOT NULL DEFAULT 0,
    failure_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    retry_delay_seconds INTEGER NOT NULL DEFAULT 300
);

CREATE INDEX idx_report_schedules_enabled ON report_schedules(enabled);
CREATE INDEX idx_report_schedules_next_run ON report_schedules(next_run_at) WHERE enabled = 1;
```

---

## Validation Rules Summary

| Entity | Key Validations |
|--------|----------------|
| Report | UUID format, time range consistency, status transitions |
| ReportTemplate | Slug name format, non-empty metrics, metric existence check, system template protection |
| ReportSchedule | Valid cron syntax, writable output directory, retry limits |
| ReportHistory | Time ordering, future retention date |
| ReportMetric | Snake_case name, redacted proxy URLs, UTC timestamps |

---

## State Machine: Report Generation

```
┌─────────────┐
│  New Report │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ Generating  │────>│  Completed  │ (success)
└──────┬──────┘     └─────────────┘
       │
       └────────────>┌─────────────┐
                     │   Failed    │ (error)
                     └─────────────┘
```

**Transitions**:
- `New -> Generating`: Report generation starts
- `Generating -> Completed`: Generation succeeds, file written
- `Generating -> Failed`: Exception raised during generation

---

## Memory Efficiency: Streaming Architecture

All report generation uses **generator-based streaming** to maintain constant memory usage:

```python
def stream_report_data(
    collector: MetricsDataStore,
    start_time: datetime,
    end_time: datetime,
    chunk_size: int = 1000
) -> Iterator[ReportMetric]:
    """Stream metrics data in chunks."""
    offset = 0
    while True:
        chunk = collector.get_metrics_chunk(start_time, end_time, offset, chunk_size)
        if not chunk:
            break
        for metric in chunk:
            yield metric  # One metric at a time
        offset += chunk_size

# CSV generation example
def generate_csv(metrics_stream: Iterator[ReportMetric], output_file):
    import csv
    writer = csv.DictWriter(output_file, fieldnames=['name', 'value', 'timestamp'])
    writer.writeheader()
    for metric in metrics_stream:  # Processes one at a time
        writer.writerow({'name': metric.name, 'value': metric.value, 'timestamp': metric.timestamp})
```

**Memory Guarantee**: <100MB regardless of dataset size (1M+ metrics)

---

## Security Considerations

1. **Credential Protection**: All proxy URLs stored in redacted format (no username/password)
2. **Path Validation**: Output paths validated to prevent directory traversal attacks
3. **Template Injection**: Jinja2 autoescaping prevents XSS in HTML reports
4. **File Permissions**: Report files created with 0600 (owner read/write only)
5. **SQL Injection**: Parameterized queries only, no string concatenation

---

## Type Safety

All models fully type-hinted for mypy --strict compliance:

```python
from typing import Iterator, Dict, Any, List, Literal, Union
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field

# All entities inherit from BaseModel
# All methods have complete type signatures
# All fields have explicit types (no Any except Dict values)
```

**Mypy Validation**: `mypy --strict proxywhirl/report_models.py` must pass with 0 errors.
