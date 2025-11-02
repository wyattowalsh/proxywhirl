# Quickstart: Data Export & Reporting

**Feature**: 011-data-export  
**Audience**: Developers using proxywhirl  
**Prerequisites**: proxywhirl core package installed (001-core-python-package)

## Installation

```bash
uv add proxywhirl[export]  # Includes pandas, openpyxl, reportlab, apscheduler
```

Or if already using proxywhirl:

```bash
uv add pandas openpyxl reportlab apscheduler
```

## Basic Usage

### 1. Export Proxy Pool Configuration

```python
from proxywhirl import ProxyRotator, ExportManager
from proxywhirl.export_models import ExportJob

# Set up proxy pool
rotator = ProxyRotator(proxies=[
    "http://proxy1.example.com:8080",
    "http://user:pass@proxy2.example.com:8080"
])

# Create export manager
export_mgr = ExportManager()

# Export pool to JSON (with encrypted credentials)
export_job = export_mgr.export_pool(
    format="json",
    credential_mode="full",  # Options: full, sanitized, reference
    compression_enabled=True,
    output_path="backups/pool_backup.json.gz"
)

print(f"Export complete: {export_job.output_file_path}")
print(f"File size: {export_job.file_size_bytes} bytes")
```

### 2. Import Proxy Pool Configuration

```python
from proxywhirl import ImportManager

import_mgr = ImportManager()

# Import from backup file
import_job = import_mgr.import_pool(
    file_path="backups/pool_backup.json.gz",
    credential_decryption_key="your-master-key-or-password",  # Master key or user password
    duplicate_strategy="skip"  # Options: skip, rename, merge
)

if import_job.status == "completed":
    print(f"Imported {import_job.imported_proxy_count} proxies")
else:
    print(f"Import failed: {import_job.error_message}")
```

### 3. Export Analytics Data

```python
from datetime import datetime, timedelta, timezone

# Export last 7 days of analytics to CSV
end_date = datetime.now(timezone.utc)
start_date = end_date - timedelta(days=7)

export_job = export_mgr.export_analytics(
    format="csv",  # Options: csv, json, excel
    time_range_start=start_date,
    time_range_end=end_date,
    columns=["timestamp", "proxy_source", "endpoint", "success", "response_time_ms"],
    compression_enabled=True,
    output_path="analytics/weekly_report.csv.gz"
)

# Check export status
if export_job.status == "completed":
    print(f"Analytics exported: {export_job.output_file_path}")
```

### 4. Export Health Check Reports (PDF)

```python
# Generate health report for all proxies
export_job = export_mgr.export_health_report(
    format="pdf",
    time_range_days=7,
    output_path="reports/health_report.pdf"
)

print(f"PDF report generated: {export_job.output_file_path}")
```

### 5. Schedule Automated Exports

```python
from proxywhirl import ScheduledExportManager
from proxywhirl.export_models import ExportTemplate

# Create export template
template = ExportTemplate(
    name="Daily Analytics Backup",
    data_type="analytics",
    format="csv",
    default_filters={"min_response_time_ms": 0},
    compression_enabled=True,
    destination_path_pattern="backups/analytics/{year}/{month}/"
)

# Schedule daily export at 2am UTC
scheduler = ScheduledExportManager()
schedule = scheduler.schedule_export(
    template=template,
    cron_expression="0 2 * * *",  # Daily at 2am
    timezone="UTC",
    admin_email_list=["admin@example.com"]
)

# Start scheduler
scheduler.start()
print(f"Scheduled export: {schedule.name}")
print(f"Next run: {schedule.next_scheduled_time}")
```

## Async Export (Large Datasets)

For exports that may take time (>1 minute):

```python
import asyncio

async def export_large_dataset():
    # Exports >10MB are automatically async
    export_job = export_mgr.export_analytics(
        format="excel",
        time_range_start=start_date,
        time_range_end=end_date,
        notification_preferences={
            "in_app": True,
            "email": True,
            "webhook": "https://your-webhook.com/notify"
        }
    )
    
    # Poll for completion
    while export_job.status in ["pending", "processing"]:
        await asyncio.sleep(5)
        export_job = export_mgr.get_export_status(export_job.id)
        print(f"Progress: {export_job.progress_percentage}%")
    
    if export_job.status == "completed":
        # Download file
        file_bytes = export_mgr.download_export(export_job.id)
        with open("large_export.xlsx", "wb") as f:
            f.write(file_bytes)

asyncio.run(export_large_dataset())
```

## Notifications

### Configure Email Notifications

```python
from proxywhirl.config import NotificationSettings

# Configure SMTP settings
settings = NotificationSettings(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_username="your-email@gmail.com",
    smtp_password="your-app-password",  # Use SecretStr
    smtp_use_tls=True,
    from_email="noreply@proxywhirl.com"
)

# Enable email notifications for exports
export_job = export_mgr.export_pool(
    format="json",
    notification_preferences={
        "email": True,  # Send email when complete
        "in_app": True
    }
)
```

### Webhook Notifications

```python
# Configure webhook for completion notifications
export_job = export_mgr.export_analytics(
    format="csv",
    time_range_start=start_date,
    time_range_end=end_date,
    notification_preferences={
        "webhook": "https://your-app.com/webhooks/export-complete"
    }
)

# Webhook will receive POST with JSON payload:
# {
#   "export_id": "uuid",
#   "status": "completed",
#   "file_size_bytes": 12345,
#   "download_url": "https://..."
# }
```

## Access Control

Only the user who created an export (or admins) can download it:

```python
from proxywhirl.models import User

# Assume user authentication handled elsewhere
current_user = User(id="user123", is_admin=False)

# Try to download export
try:
    file_bytes = export_mgr.download_export(
        export_id="some-export-id",
        current_user=current_user
    )
except PermissionError:
    print("You don't have permission to access this export")
```

## Compression

Compression is enabled by default (gzip level 6):

```python
# Disable compression for a specific export
export_job = export_mgr.export_pool(
    format="json",
    compression_enabled=False  # Output will be .json instead of .json.gz
)

# Or configure default compression level
from proxywhirl.config import ExportSettings

settings = ExportSettings(
    default_compression_level=9  # Maximum compression (slower)
)
```

## Error Handling

```python
from proxywhirl.exceptions import ExportError, ImportValidationError

try:
    export_job = export_mgr.export_analytics(
        format="csv",
        time_range_start=start_date,
        time_range_end=end_date
    )
except ExportError as e:
    print(f"Export failed: {e}")
    print(f"Details: {e.details}")

try:
    import_job = import_mgr.import_pool(
        file_path="invalid_file.json",
        credential_decryption_key="wrong-key"
    )
except ImportValidationError as e:
    print(f"Import validation failed: {e.validation_errors}")
```

## REST API Usage (if 003-rest-api installed)

### Create Export via API

```bash
curl -X POST http://localhost:8000/api/v1/exports \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "data_type": "analytics",
    "format": "csv",
    "time_range_start": "2025-11-01T00:00:00Z",
    "time_range_end": "2025-11-02T00:00:00Z",
    "compression_enabled": true,
    "notification_preferences": {
      "email": true
    }
  }'
```

Response:
```json
{
  "id": "uuid-here",
  "status": "pending",
  "progress_percentage": 0,
  "created_at": "2025-11-02T14:30:00Z"
}
```

### Check Export Status

```bash
curl http://localhost:8000/api/v1/exports/uuid-here \
  -H "X-API-Key: your-api-key"
```

Response includes status, progress, and download availability for programmatic polling:
```json
{
  "id": "uuid-here",
  "status": "completed",
  "progress_percentage": 100,
  "output_file_path": "exports/user123/2025/11/analytics_20251102_143000_user123.csv.gz",
  "file_size_bytes": 1024000,
  "created_at": "2025-11-02T14:30:00Z",
  "completed_at": "2025-11-02T14:30:45Z"
}
```

### Download Export

```bash
curl http://localhost:8000/api/v1/exports/uuid-here/download \
  -H "X-API-Key: your-api-key" \
  -O -J  # Save with original filename
```

### Import via API

```bash
curl -X POST http://localhost:8000/api/v1/imports \
  -H "X-API-Key: your-api-key" \
  -F "file=@pool_backup.json.gz" \
  -F "credential_decryption_key=your-master-key-or-password" \
  -F "duplicate_strategy=skip"
```

## Advanced Features

### Custom Export Templates

```python
from proxywhirl.export_models import ExportTemplate

# Create reusable template
template = ExportTemplate(
    name="Weekly Performance Report",
    description="Analytics with >90% success rate",
    data_type="analytics",
    format="excel",
    default_filters={
        "min_success_rate": 0.9,
        "time_range_days": 7
    },
    column_selections=[
        "timestamp",
        "proxy_source",
        "success_rate",
        "avg_response_time_ms"
    ],
    compression_enabled=True,
    destination_path_pattern="reports/{year}/week_{week}/"
)

# Save template
export_mgr.save_template(template)

# Use template for export
export_job = export_mgr.export_from_template(
    template_id=template.id,
    additional_params={"time_range_days": 14}  # Override default
)
```

### Audit Trail

All export/import operations are logged:

```python
# Get audit logs for a user
logs = export_mgr.get_audit_logs(
    user_id="user123",
    operation_type="export",
    start_date=start_date,
    end_date=end_date
)

for log in logs:
    print(f"{log.timestamp}: {log.operation_type} - {log.file_path}")
```

## Performance Tips

1. **Use compression** for large exports (reduces size by 60%+)
2. **Limit date ranges** for analytics exports to avoid timeouts
3. **Use column selection** to export only needed fields
4. **Schedule exports** during off-peak hours (2am UTC default)
5. **Monitor disk space** for export destination directory

## Next Steps

- See [data-model.md](./data-model.md) for complete data structures
- See [contracts/export-api.yaml](./contracts/export-api.yaml) for REST API reference
- See [plan.md](./plan.md) for implementation details
