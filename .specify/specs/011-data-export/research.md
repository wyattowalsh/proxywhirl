# Research: Data Export & Reporting

**Feature**: 011-data-export  
**Date**: 2025-11-02  
**Purpose**: Resolve technical unknowns identified in plan.md Phase 0

## 1. PDF Generation Library Selection

### Decision: **ReportLab**

### Rationale:
- **Mature & Stable**: 20+ years of development, production-proven
- **Python 3.9+ Compatible**: Fully supports target Python versions
- **Feature Complete**: Charts (via reportlab.graphics), tables, images, custom fonts, branding
- **Performance**: Fast rendering for reports (<5s for 50-page PDF)
- **License**: BSD-like (permissive for commercial use)
- **Community**: Extensive documentation, active maintenance

### Alternatives Considered:
- **WeasyPrint**: HTML/CSS to PDF, easier styling but heavier dependencies (cairo, pango), overkill for structured reports
- **matplotlib**: Good for charts but not designed for multi-page reports with tables/text
- **FPDF**: Simpler but lacks advanced features (no reportlab.graphics equivalent)

### Implementation Notes:
- Use `reportlab.platypus` for document flow (tables, paragraphs, page breaks)
- Use `reportlab.graphics.charts` for health trend charts (line, bar, pie)
- Store branding config in settings (logo path, colors, fonts)
- Generate PDFs asynchronously for large reports

---

## 2. Excel Export Strategy

### Decision: **pandas + openpyxl**

### Rationale:
- **pandas Integration**: Already planned dependency for analytics (009-analytics-engine-analysis)
- **DataFrame to Excel**: Single `df.to_excel()` call handles formatting
- **openpyxl Backend**: Supports XLSX, formulas, cell styling, conditional formatting
- **Memory Efficient**: Streaming writer for large datasets
- **Type Preservation**: Maintains numeric, date, boolean types correctly

### Alternatives Considered:
- **xlsxwriter**: Faster but pandas doesn't integrate as seamlessly, more manual formatting
- **pyexcel**: Simpler API but less feature-complete for complex exports
- **Direct openpyxl**: More control but reimplements pandas' data handling logic

### Implementation Notes:
```python
import pandas as pd

# Export analytics data
df = pd.DataFrame(analytics_records)
df.to_excel(
    'export.xlsx',
    index=False,
    engine='openpyxl',
    sheet_name='Analytics'
)

# For multiple sheets (e.g., summary + detailed data)
with pd.ExcelWriter('export.xlsx', engine='openpyxl') as writer:
    summary_df.to_excel(writer, sheet_name='Summary')
    detail_df.to_excel(writer, sheet_name='Details')
```

---

## 3. APScheduler Configuration

### Decision: **BackgroundScheduler**

### Rationale:
- **Thread-Based**: Runs in background thread, no asyncio event loop conflicts
- **Persistent Jobs**: Job stores support (SQLite via SQLAlchemyJobStore)
- **Cron Expressions**: Full cron syntax + interval-based scheduling
- **Timezone Support**: Handles UTC and local timezone scheduling
- **Lightweight**: No external dependencies beyond APScheduler itself

### Alternatives Considered:
- **AsyncIOScheduler**: Requires asyncio event loop management, complicates library-first design
- **Celery**: Overkill, requires message broker (Redis/RabbitMQ), violates simplicity
- **Custom threading.Timer**: No persistence, no cron support, error-prone

### Implementation Notes:
```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
}

scheduler = BackgroundScheduler(jobstores=jobstores)

# Add scheduled export
scheduler.add_job(
    func=execute_export,
    trigger=CronTrigger.from_crontab('0 2 * * *'),  # Daily at 2am
    args=[export_config],
    id='export_analytics_daily',
    replace_existing=True
)

scheduler.start()
```

- Store scheduler state in SQLite (reuse storage.py patterns)
- Graceful shutdown on process exit
- Error handling: Email admin on job failure + retry with exponential backoff

---

## 4. Compression Algorithm

### Decision: **gzip level 6 (default)**

### Rationale:
- **Balance**: Level 6 provides 60-70% compression with <2s overhead per 100MB
- **Compatibility**: Universal support (Python stdlib, all OS)
- **Speed vs Ratio**: Levels 7-9 give <5% more compression but 2-3x slower
- **Memory**: Lower memory footprint than lzma
- **Streaming**: Supports streaming for large files

### Performance Data:
| Level | Compression Ratio | Time (100MB) | Use Case |
|-------|------------------|--------------|----------|
| 1     | ~40-50%          | 0.5s         | Speed priority |
| 6     | ~60-70%          | 1.5s         | **Recommended (default)** |
| 9     | ~65-75%          | 4-5s         | Size priority |

### Alternatives Considered:
- **lzma (xz)**: Better compression (75-80%) but 5-10x slower, not worth for exports
- **bz2**: Similar to gzip but 2x slower, no significant advantage
- **zstd**: Fast and efficient but requires external dependency, Python 3.11+ only

### Implementation Notes:
```python
import gzip

# Compress export
with gzip.open('export.csv.gz', 'wb', compresslevel=6) as f:
    f.write(csv_data.encode('utf-8'))

# User can disable compression
if not export_job.compression_enabled:
    write_file('export.csv', csv_data)
```

- File extension: `.csv.gz`, `.json.gz` (manifest indicates compression)
- Decompress automatically on import if needed
- Allow user to specify compression level in advanced settings (default 6)

---

## 5. Notification Infrastructure

### Decision: **SMTP for email + httpx for webhooks**

### Rationale:
- **Email (SMTP)**:
  - Python stdlib `smtplib` + `email.mime` (no extra dependencies)
  - Configure SMTP server in settings (host, port, credentials)
  - Support TLS/SSL for security
  - HTML templates for branded notifications
  
- **Webhooks (httpx)**:
  - Already a dependency (httpx for proxy requests)
  - POST JSON payload to configured webhook URL
  - Retry with exponential backoff on failure
  - Timeout handling (5s default)

- **In-App Notifications**:
  - Store in SQLite notifications table
  - Poll via API endpoint or WebSocket (if 003-rest-api includes it)
  - Mark as read/unread, expiry after 30 days

### Alternatives Considered:
- **SendGrid/AWS SES**: External service dependency, adds cost, complicates setup
- **Celery + RabbitMQ**: Overkill for notifications, violates simplicity
- **Task queue**: Custom queue adds complexity, SMTP async sufficient

### Implementation Notes:

**Email Configuration**:
```python
from pydantic_settings import BaseSettings

class NotificationSettings(BaseSettings):
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: SecretStr
    smtp_password: SecretStr
    smtp_use_tls: bool = True
    from_email: str = "noreply@proxywhirl.com"
```

**Send Email**:
```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_notification(to: str, subject: str, body_html: str):
    msg = MIMEMultipart('alternative')
    msg['From'] = settings.from_email
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body_html, 'html'))
    
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        if settings.smtp_use_tls:
            server.starttls()
        server.login(
            settings.smtp_username.get_secret_value(),
            settings.smtp_password.get_secret_value()
        )
        server.send_message(msg)
```

**Webhook**:
```python
import httpx

async def send_webhook_notification(url: str, payload: dict):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Webhook failed: {e}")
            # Retry logic with exponential backoff
```

---

## 6. Access Control Integration

### Decision: **Simple user_id + is_admin model stored in export jobs**

### Rationale:
- **Minimal Complexity**: No separate auth system, reuse existing user context
- **Storage**: ExportJob tracks `created_by_user_id`
- **Check Logic**: `can_access(export_job, current_user)` function checks `creator or is_admin`
- **Audit Trail**: All access attempts logged in ExportAuditLog

### Implementation Notes:
```python
def can_access_export(export_job: ExportJob, user: User) -> bool:
    """Check if user can access export file."""
    if user.is_admin:
        return True
    if export_job.created_by_user_id == user.id:
        return True
    return False

def get_export_file(export_id: str, current_user: User) -> bytes:
    export_job = storage.get_export_job(export_id)
    if not can_access_export(export_job, current_user):
        raise PermissionError(f"User {current_user.id} cannot access export {export_id}")
    
    # Log access attempt
    audit_log = ExportAuditLog(
        operation_type="download",
        user_id=current_user.id,
        export_job_id=export_id,
        timestamp=datetime.now(timezone.utc)
    )
    storage.log_export_access(audit_log)
    
    return read_export_file(export_job.output_file_path)
```

### User Model Extension:
```python
from pydantic import BaseModel

class User(BaseModel):
    id: str
    email: str
    is_admin: bool = False
```

- If 003-rest-api includes auth, integrate with its user model
- Otherwise, simple User class sufficient for library-first usage
- API endpoints check user context from request authentication

---

## 7. File Storage Management

### Decision: **Hierarchical directory structure with retention policy worker**

### Directory Structure:
```
exports/
├── {user_id}/
│   ├── {year}/
│   │   ├── {month}/
│   │   │   ├── pool_20251102_120530_user123.json.gz
│   │   │   ├── analytics_20251102_140230_user123.csv.gz
│   │   │   └── health_20251102_160045_user123.pdf
│   │   └── ...
│   └── ...
└── .retention_marker  # Tracks last cleanup run
```

### Rationale:
- **Organization**: User-based isolation, date-based browsing
- **Performance**: Avoid single directory with thousands of files
- **Cleanup**: Date-based directories simplify retention policy (delete old months)
- **Portability**: Relative paths in manifest, absolute paths in DB

### Retention Policy Worker:
```python
from pathlib import Path
from datetime import datetime, timedelta, timezone

def cleanup_old_exports(retention_days: int = 30):
    """Delete export files older than retention_days."""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
    exports_dir = Path("exports")
    
    for user_dir in exports_dir.iterdir():
        if not user_dir.is_dir():
            continue
        for year_dir in user_dir.iterdir():
            for month_dir in year_dir.iterdir():
                for export_file in month_dir.glob("*"):
                    if export_file.stat().st_mtime < cutoff_date.timestamp():
                        export_file.unlink()
                        logger.info(f"Deleted expired export: {export_file}")
                        
                        # Update DB status
                        storage.mark_export_deleted(export_file.name)
```

### Scheduled Cleanup:
- Run daily via APScheduler (2am UTC)
- Configurable retention period in settings
- Log deleted files for audit
- Update ExportJob status to "expired"

---

## 8. Import Validation Patterns

### Decision: **Pydantic models for schema validation + JSON Schema for version checking**

### Rationale:
- **Type Safety**: Pydantic validates types, required fields, constraints
- **Schema Versioning**: JSON Schema stored in manifest, checked on import
- **Error Messages**: Pydantic provides helpful validation errors
- **Consistency**: Reuses existing Pydantic infrastructure (001-core-python-package)

### Implementation:
```python
from pydantic import BaseModel, Field, validator
from typing import List
import json

class ExportManifestV1(BaseModel):
    """Schema for export manifest version 1."""
    proxywhirl_version: str
    schema_version: str = "1.0"
    export_timestamp: datetime
    credential_mode: str = Field(..., regex="^(full|sanitized|reference)$")
    compression_algorithm: str = "gzip"
    data_integrity_checksum: str
    
class ProxyExportV1(BaseModel):
    """Schema for exported proxy."""
    url: str
    auth_type: str
    username: str | None = None
    encrypted_password: str | None = None  # Base64 encoded
    health_status: str
    metadata: dict = {}
    
class PoolExportV1(BaseModel):
    """Top-level schema for pool export."""
    manifest: ExportManifestV1
    proxies: List[ProxyExportV1]
    
def validate_import_file(file_path: Path) -> PoolExportV1:
    """Validate import file structure and schema."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    try:
        pool_export = PoolExportV1(**data)
    except ValidationError as e:
        raise ImportValidationError(
            f"Invalid export file format: {e.errors()}"
        )
    
    # Check schema version compatibility
    if pool_export.manifest.schema_version != "1.0":
        raise ImportValidationError(
            f"Unsupported schema version: {pool_export.manifest.schema_version}"
        )
    
    # Verify checksum
    calculated_checksum = compute_checksum(pool_export.proxies)
    if calculated_checksum != pool_export.manifest.data_integrity_checksum:
        raise ImportValidationError("Checksum mismatch - file may be corrupted")
    
    return pool_export
```

### Schema Versioning Strategy:
- **V1.0**: Initial export format
- **V1.1+**: Add optional fields (backward compatible)
- **V2.0**: Breaking changes (provide migration tool)
- Manifest stores schema version for forward compatibility

### Duplicate Detection:
```python
def detect_duplicates(proxies: List[ProxyExportV1], existing_proxies: List[Proxy]) -> List[str]:
    """Return list of duplicate proxy URLs."""
    existing_urls = {p.url for p in existing_proxies}
    import_urls = {p.url for p in proxies}
    return list(existing_urls & import_urls)

def resolve_duplicates(duplicates: List[str], strategy: str):
    """Handle duplicate proxies based on strategy (skip/rename/merge)."""
    if strategy == "skip":
        return [p for p in proxies if p.url not in duplicates]
    elif strategy == "rename":
        # Append suffix to duplicates
        pass
    elif strategy == "merge":
        # Update existing with import data
        pass
```

---

## Summary of Decisions

| Area | Decision | Key Dependencies |
|------|----------|------------------|
| PDF Generation | ReportLab | `reportlab>=4.0.0` |
| Excel Export | pandas + openpyxl | `pandas>=2.0.0`, `openpyxl>=3.1.0` |
| Scheduling | BackgroundScheduler | `apscheduler>=3.10.0` |
| Compression | gzip level 6 | Python stdlib |
| Email | SMTP (stdlib) | `smtplib` + config |
| Webhooks | httpx | `httpx>=0.25.0` (existing) |
| Access Control | User ID + is_admin | Simple model |
| File Storage | User/date hierarchy | Local filesystem |
| Import Validation | Pydantic + checksums | `pydantic>=2.0.0` (existing) |

**All unknowns resolved**. Ready for Phase 1 (data-model.md, contracts, quickstart.md).
