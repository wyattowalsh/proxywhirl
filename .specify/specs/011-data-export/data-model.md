# Data Model: Data Export & Reporting

**Feature**: 011-data-export  
**Date**: 2025-11-02  
**Purpose**: Define data structures for export/import functionality

## Core Entities

### ExportJob

Represents an export request and tracks its execution.

**Fields**:
- `id`: str (UUID) - Unique export job identifier
- `data_type`: str - Type of data being exported (`pool`, `analytics`, `health`, `dashboard`)
- `format`: str - Output format (`csv`, `json`, `excel`, `pdf`)
- `status`: str - Job status (`pending`, `processing`, `completed`, `failed`)
- `created_by_user_id`: str - User who initiated the export
- `created_at`: datetime (UTC) - When job was created
- `completed_at`: datetime | None (UTC) - When job finished
- `time_range_start`: datetime | None (UTC) - Start of data range (for analytics/health)
- `time_range_end`: datetime | None (UTC) - End of data range
- `output_file_path`: str | None - Relative path to exported file
- `file_size_bytes`: int | None - Size of exported file
- `progress_percentage`: int - 0-100 progress indicator
- `compression_enabled`: bool - Whether file is compressed
- `notification_preferences`: dict - `{"in_app": bool, "email": bool, "webhook": str | None}`
- `error_message`: str | None - Error details if status=failed
- `parameters`: dict - Export-specific parameters (columns, filters, etc.)

**Relationships**:
- One-to-many with ExportAuditLog (access tracking)
- Many-to-one with User (creator)
- Optional one-to-one with ExportTemplate (if using template)

**State Transitions**:
```
pending → processing → completed
pending → processing → failed
```

**Validation Rules**:
- `status` must be one of: pending, processing, completed, failed
- `data_type` must be one of: pool, analytics, health, dashboard
- `format` must be one of: csv, json, excel, pdf
- `progress_percentage` must be 0-100
- `time_range_end` must be >= `time_range_start` if both set
- `file_size_bytes` must be > 0 if status=completed

---

### ExportTemplate

Defines reusable export configurations.

**Fields**:
- `id`: str (UUID) - Unique template identifier
- `name`: str - Human-readable template name
- `description`: str | None - Template description
- `data_type`: str - Type of data (`pool`, `analytics`, `health`, `dashboard`)
- `format`: str - Output format
- `default_filters`: dict - Default filter parameters
- `column_selections`: list[str] | None - Which columns to include (for CSV/Excel)
- `compression_enabled`: bool - Default compression setting
- `schedule_settings`: dict | None - Schedule config if used for automated exports
- `destination_path_pattern`: str - Path template (e.g., `exports/{user_id}/{year}/{month}/`)
- `created_by_user_id`: str - Template creator
- `created_at`: datetime (UTC)
- `is_public`: bool - Whether other users can use this template

**Relationships**:
- One-to-many with ExportJob (jobs using this template)
- One-to-many with ScheduledExport (schedules using this template)

**Validation Rules**:
- `name` must be unique per user
- `data_type` and `format` must be valid values
- `destination_path_pattern` must be valid path template

---

### ImportJob

Represents an import request and validation status.

**Fields**:
- `id`: str (UUID) - Unique import job identifier
- `source_file_path`: str - Path to import file
- `file_format`: str - Format of import file (`json`, `csv`)
- `status`: str - Import status (`validating`, `validated`, `importing`, `completed`, `failed`)
- `initiated_by_user_id`: str - User who initiated import
- `initiated_at`: datetime (UTC)
- `completed_at`: datetime | None (UTC)
- `validation_errors`: list[str] - List of validation issues found
- `detected_duplicates`: list[str] - Duplicate proxy URLs found
- `duplicate_resolution_strategy`: str | None - How duplicates were handled (`skip`, `rename`, `merge`)
- `credential_decryption_method`: str - How credentials were decrypted (`master_key`, `user_password`)
- `imported_proxy_count`: int | None - Number of proxies successfully imported
- `error_message`: str | None - Error details if status=failed

**Relationships**:
- One-to-many with ExportAuditLog (import actions logged)
- Many-to-one with User (initiator)

**State Transitions**:
```
validating → validated → importing → completed
validating → failed (validation errors)
validated → failed (import errors)
```

**Validation Rules**:
- `status` must be one of: validating, validated, importing, completed, failed
- `file_format` must be one of: json, csv
- `duplicate_resolution_strategy` must be one of: skip, rename, merge, or null
- `credential_decryption_method` must be one of: master_key, user_password

---

### ExportManifest

Metadata accompanying each export file (embedded in export).

**Fields**:
- `proxywhirl_version`: str - Version that created the export (e.g., `0.2.0`)
- `schema_version`: str - Export schema version (e.g., `1.0`)
- `export_timestamp`: datetime (UTC) - When export was created
- `data_time_range`: dict | None - `{"start": datetime, "end": datetime}` for analytics/health
- `credential_handling_mode`: str - How credentials are included (`full`, `sanitized`, `reference`)
- `compression_algorithm`: str | None - Compression used (`gzip`, or null if uncompressed)
- `compression_level`: int | None - Compression level (1-9 for gzip)
- `data_integrity_checksum`: str - SHA-256 hash of export data
- `total_record_count`: int - Number of records exported
- `export_parameters`: dict - Parameters used for export (filters, columns, etc.)

**Relationships**:
- Embedded in each export file (not a database entity)

**Validation Rules**:
- `schema_version` must follow semver (e.g., `1.0`, `1.1`, `2.0`)
- `credential_handling_mode` must be one of: full, sanitized, reference
- `compression_algorithm` must be one of: gzip, or null
- `compression_level` must be 1-9 if algorithm=gzip
- `data_integrity_checksum` must be valid SHA-256 hash (64 hex chars)

---

### ScheduledExport

Defines automated export schedules.

**Fields**:
- `id`: str (UUID) - Unique schedule identifier
- `template_id`: str - Reference to ExportTemplate
- `name`: str - Human-readable schedule name
- `cron_expression`: str - Cron expression for schedule (e.g., `0 2 * * *`)
- `timezone`: str - Timezone for schedule (e.g., `UTC`, `America/New_York`)
- `enabled`: bool - Whether schedule is active
- `last_execution_time`: datetime | None (UTC) - Last successful execution
- `next_scheduled_time`: datetime | None (UTC) - Next planned execution
- `failure_retry_policy`: dict - `{"max_retries": int, "backoff_seconds": int}`
- `admin_email_list`: list[str] - Emails to notify on failure
- `created_by_user_id`: str - Schedule creator
- `created_at`: datetime (UTC)
- `updated_at`: datetime (UTC)

**Relationships**:
- Many-to-one with ExportTemplate (uses template settings)
- One-to-many with ExportJob (creates jobs when triggered)

**Validation Rules**:
- `cron_expression` must be valid cron syntax
- `timezone` must be valid IANA timezone name
- `admin_email_list` entries must be valid email addresses
- `template_id` must reference existing template

---

### ExportAuditLog

Records all export/import operations and file access.

**Fields**:
- `id`: str (UUID) - Unique log entry identifier
- `operation_type`: str - Type of operation (`export`, `import`, `download`, `delete`)
- `user_id`: str - User who performed operation
- `timestamp`: datetime (UTC) - When operation occurred
- `export_job_id`: str | None - Related export job (if applicable)
- `import_job_id`: str | None - Related import job (if applicable)
- `file_path`: str | None - File involved in operation
- `success`: bool - Whether operation succeeded
- `error_message`: str | None - Error details if failed
- `parameters`: dict - Operation parameters (filters, format, etc.)
- `ip_address`: str | None - User IP address (if available)
- `user_agent`: str | None - User agent (if web request)

**Relationships**:
- Many-to-one with User (actor)
- Many-to-one with ExportJob (optional)
- Many-to-one with ImportJob (optional)

**Validation Rules**:
- `operation_type` must be one of: export, import, download, delete
- Must have either `export_job_id` or `import_job_id` or both null
- `timestamp` must not be in future

---

### User (Extended)

Extension of existing User model to support export functionality.

**New Fields** (if not already present):
- `is_admin`: bool - Whether user has admin privileges
- `notification_preferences`: dict - Default notification settings
- `email`: str - Email for notifications

**Note**: If 003-rest-api includes auth, use its User model. Otherwise, simple model sufficient.

---

## Database Schema (SQLite)

### Table: export_jobs

```sql
CREATE TABLE export_jobs (
    id TEXT PRIMARY KEY,
    data_type TEXT NOT NULL CHECK(data_type IN ('pool', 'analytics', 'health', 'dashboard')),
    format TEXT NOT NULL CHECK(format IN ('csv', 'json', 'excel', 'pdf')),
    status TEXT NOT NULL CHECK(status IN ('pending', 'processing', 'completed', 'failed')),
    created_by_user_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    time_range_start TIMESTAMP,
    time_range_end TIMESTAMP,
    output_file_path TEXT,
    file_size_bytes INTEGER,
    progress_percentage INTEGER NOT NULL DEFAULT 0 CHECK(progress_percentage BETWEEN 0 AND 100),
    compression_enabled BOOLEAN NOT NULL DEFAULT 1,
    notification_preferences TEXT NOT NULL,  -- JSON
    error_message TEXT,
    parameters TEXT NOT NULL  -- JSON
);

CREATE INDEX idx_export_jobs_user ON export_jobs(created_by_user_id);
CREATE INDEX idx_export_jobs_status ON export_jobs(status);
CREATE INDEX idx_export_jobs_created_at ON export_jobs(created_at DESC);
```

### Table: export_templates

```sql
CREATE TABLE export_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    data_type TEXT NOT NULL,
    format TEXT NOT NULL,
    default_filters TEXT NOT NULL,  -- JSON
    column_selections TEXT,  -- JSON array or NULL
    compression_enabled BOOLEAN NOT NULL DEFAULT 1,
    schedule_settings TEXT,  -- JSON or NULL
    destination_path_pattern TEXT NOT NULL,
    created_by_user_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT 0,
    UNIQUE(created_by_user_id, name)
);

CREATE INDEX idx_export_templates_user ON export_templates(created_by_user_id);
CREATE INDEX idx_export_templates_public ON export_templates(is_public) WHERE is_public = 1;
```

### Table: import_jobs

```sql
CREATE TABLE import_jobs (
    id TEXT PRIMARY KEY,
    source_file_path TEXT NOT NULL,
    file_format TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('validating', 'validated', 'importing', 'completed', 'failed')),
    initiated_by_user_id TEXT NOT NULL,
    initiated_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    validation_errors TEXT,  -- JSON array
    detected_duplicates TEXT,  -- JSON array
    duplicate_resolution_strategy TEXT CHECK(duplicate_resolution_strategy IN ('skip', 'rename', 'merge')),
    credential_decryption_method TEXT NOT NULL CHECK(credential_decryption_method IN ('master_key', 'user_password')),
    imported_proxy_count INTEGER,
    error_message TEXT
);

CREATE INDEX idx_import_jobs_user ON import_jobs(initiated_by_user_id);
CREATE INDEX idx_import_jobs_status ON import_jobs(status);
```

### Table: scheduled_exports

```sql
CREATE TABLE scheduled_exports (
    id TEXT PRIMARY KEY,
    template_id TEXT NOT NULL REFERENCES export_templates(id),
    name TEXT NOT NULL,
    cron_expression TEXT NOT NULL,
    timezone TEXT NOT NULL DEFAULT 'UTC',
    enabled BOOLEAN NOT NULL DEFAULT 1,
    last_execution_time TIMESTAMP,
    next_scheduled_time TIMESTAMP,
    failure_retry_policy TEXT NOT NULL,  -- JSON
    admin_email_list TEXT NOT NULL,  -- JSON array
    created_by_user_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_scheduled_exports_enabled ON scheduled_exports(enabled) WHERE enabled = 1;
CREATE INDEX idx_scheduled_exports_next_time ON scheduled_exports(next_scheduled_time);
```

### Table: export_audit_logs

```sql
CREATE TABLE export_audit_logs (
    id TEXT PRIMARY KEY,
    operation_type TEXT NOT NULL CHECK(operation_type IN ('export', 'import', 'download', 'delete')),
    user_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    export_job_id TEXT REFERENCES export_jobs(id),
    import_job_id TEXT REFERENCES import_jobs(id),
    file_path TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    parameters TEXT,  -- JSON
    ip_address TEXT,
    user_agent TEXT
);

CREATE INDEX idx_audit_logs_user ON export_audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON export_audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_operation ON export_audit_logs(operation_type);
```

---

## File Format Specifications

### Proxy Pool Export (JSON)

```json
{
  "manifest": {
    "proxywhirl_version": "0.2.0",
    "schema_version": "1.0",
    "export_timestamp": "2025-11-02T14:30:00Z",
    "credential_handling_mode": "full",
    "compression_algorithm": "gzip",
    "compression_level": 6,
    "data_integrity_checksum": "sha256:abcd1234...",
    "total_record_count": 10
  },
  "proxies": [
    {
      "url": "http://proxy1.example.com:8080",
      "auth_type": "basic",
      "username": "user1",
      "encrypted_password": "base64encodedencryptedpassword==",
      "health_status": "healthy",
      "last_check_time": "2025-11-02T14:25:00Z",
      "success_rate": 0.95,
      "avg_response_time_ms": 250,
      "metadata": {
        "source": "provider_a",
        "region": "us-east-1"
      }
    }
  ]
}
```

### Analytics Export (CSV)

```csv
timestamp,proxy_source,endpoint,http_method,success,response_time_ms,http_status,bytes_transferred,error_code
2025-11-02T10:00:00Z,proxy1.example.com,api.target.com/users,GET,true,245,200,1024,
2025-11-02T10:00:05Z,proxy2.example.com,api.target.com/posts,GET,false,5000,504,,timeout
```

---

## Relationships Diagram

```
User (existing)
  ├── 1:N ExportJob (created_by)
  ├── 1:N ImportJob (initiated_by)
  ├── 1:N ExportTemplate (created_by)
  ├── 1:N ScheduledExport (created_by)
  └── 1:N ExportAuditLog (user_id)

ExportTemplate
  ├── 1:N ExportJob (optional template reference)
  └── 1:N ScheduledExport (template_id)

ExportJob
  └── 1:N ExportAuditLog (export_job_id)

ImportJob
  └── 1:N ExportAuditLog (import_job_id)

ScheduledExport
  └── 1:N ExportJob (creates when triggered)
```

---

## Data Lifecycle

### Export Lifecycle

1. **Creation**: User/schedule creates ExportJob (status=pending)
2. **Processing**: Worker picks up job, updates progress, status=processing
3. **Completion**: File generated, path + size stored, status=completed
4. **Notification**: Email/webhook/in-app sent based on preferences
5. **Access**: User/admin downloads file (logged in ExportAuditLog)
6. **Expiration**: Cleanup worker deletes file after retention period, updates status

### Import Lifecycle

1. **Initiation**: User uploads file, creates ImportJob (status=validating)
2. **Validation**: Schema + checksum verified, duplicates detected, status=validated or failed
3. **User Confirmation**: User chooses duplicate resolution strategy
4. **Import**: Proxies created/updated, status=importing
5. **Completion**: status=completed, imported_proxy_count set
6. **Audit**: All actions logged in ExportAuditLog

---

**Phase 1 Status**: Data model complete. Next: contracts/ and quickstart.md
