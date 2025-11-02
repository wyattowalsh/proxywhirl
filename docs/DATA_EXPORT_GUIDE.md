# Data Export Guide

ProxyWhirl provides comprehensive data export functionality for extracting proxy lists, metrics, logs, and configuration data in multiple formats.

## Overview

The export system supports:

- **Multiple Data Types**: Proxies, metrics, logs, configuration, health status, cache data
- **Multiple Formats**: CSV, JSON, JSONL, YAML, text, Markdown
- **Compression**: GZIP and ZIP compression
- **Filtering**: Advanced filtering by health status, source, performance metrics, time ranges
- **Destinations**: Local files, in-memory, S3 (planned), HTTP (planned)
- **History & Audit**: Complete export history tracking
- **Progress Tracking**: Real-time export progress monitoring

## Quick Start

### Python API

```python
from proxywhirl import (
    ExportManager,
    ExportConfig,
    ExportType,
    ExportFormat,
    LocalFileDestination,
    ProxyPool,
)

# Create proxy pool
pool = ProxyPool(name="my-pool", proxies=[...])

# Create export manager
export_manager = ExportManager(proxy_pool=pool)

# Configure and execute export
config = ExportConfig(
    export_type=ExportType.PROXIES,
    export_format=ExportFormat.CSV,
    destination=LocalFileDestination(
        file_path="exports/proxies.csv",
        overwrite=True,
    ),
)

result = export_manager.export(config)
print(f"Exported {result.records_exported} proxies to {result.destination_path}")
```

### REST API

```bash
# Export proxies to CSV
curl -X POST http://localhost:8000/api/v1/exports \
  -H "Content-Type: application/json" \
  -d '{
    "export_type": "proxies",
    "export_format": "csv",
    "destination_type": "local_file",
    "file_path": "exports/proxies.csv",
    "overwrite": true
  }'

# Get export history
curl http://localhost:8000/api/v1/exports/history
```

## Export Types

### 1. Proxy List Export

Export your complete proxy pool with optional filtering and field selection.

```python
from proxywhirl import ProxyExportFilter

config = ExportConfig(
    export_type=ExportType.PROXIES,
    export_format=ExportFormat.JSON,
    destination=LocalFileDestination(file_path="proxies.json"),
    proxy_filter=ProxyExportFilter(
        health_status=["healthy"],
        min_success_rate=0.8,
        protocol=["http", "https"],
        include_fields=["url", "health_status", "success_rate"],
    ),
)
```

### 2. Metrics Export

Export system metrics with time range filtering.

```python
from datetime import datetime, timedelta, timezone
from proxywhirl import MetricsExportFilter

config = ExportConfig(
    export_type=ExportType.METRICS,
    export_format=ExportFormat.JSON,
    destination=LocalFileDestination(file_path="metrics.json"),
    metrics_filter=MetricsExportFilter(
        start_time=datetime.now(timezone.utc) - timedelta(hours=24),
        end_time=datetime.now(timezone.utc),
        metric_names=["requests_total", "response_time"],
    ),
)
```

### 3. Log Export

Export application logs with filtering by level, component, and content.

```python
from proxywhirl import LogExportFilter

config = ExportConfig(
    export_type=ExportType.LOGS,
    export_format=ExportFormat.JSONL,
    destination=LocalFileDestination(file_path="logs.jsonl"),
    log_filter=LogExportFilter(
        log_levels=["ERROR", "CRITICAL"],
        search_text="connection failed",
        max_entries=1000,
    ),
)
```

### 4. Configuration Export

Export system configuration with optional secret redaction.

```python
from proxywhirl import ConfigurationExportFilter

config = ExportConfig(
    export_type=ExportType.CONFIGURATION,
    export_format=ExportFormat.YAML,
    destination=LocalFileDestination(file_path="config.yaml"),
    config_filter=ConfigurationExportFilter(
        redact_secrets=True,
        include_sections=["proxy_pool", "rotation_strategy"],
    ),
)
```

### 5. Health Status Export

Export detailed health status for all proxies.

```python
config = ExportConfig(
    export_type=ExportType.HEALTH_STATUS,
    export_format=ExportFormat.JSON,
    destination=LocalFileDestination(file_path="health_report.json"),
)
```

## Export Formats

### CSV

Ideal for spreadsheet analysis and database imports.

```python
config = ExportConfig(
    export_type=ExportType.PROXIES,
    export_format=ExportFormat.CSV,
    destination=LocalFileDestination(file_path="proxies.csv"),
)
```

**Output Example:**
```csv
url,protocol,health_status,total_requests,success_rate
http://proxy1.example.com:8080,http,healthy,100,0.95
http://proxy2.example.com:8080,http,degraded,50,0.80
```

### JSON

Structured data format with optional pretty-printing.

```python
config = ExportConfig(
    export_type=ExportType.PROXIES,
    export_format=ExportFormat.JSON,
    destination=LocalFileDestination(file_path="proxies.json"),
    pretty_print=True,
)
```

**Output Example:**
```json
[
  {
    "url": "http://proxy1.example.com:8080",
    "protocol": "http",
    "health_status": "healthy",
    "success_rate": 0.95
  }
]
```

### JSONL (JSON Lines)

Streaming-friendly format with one JSON object per line.

```python
config = ExportConfig(
    export_type=ExportType.PROXIES,
    export_format=ExportFormat.JSONL,
    destination=LocalFileDestination(file_path="proxies.jsonl"),
)
```

### YAML

Human-readable format ideal for configuration files.

```python
config = ExportConfig(
    export_type=ExportType.PROXIES,
    export_format=ExportFormat.YAML,
    destination=LocalFileDestination(file_path="proxies.yaml"),
)
```

### Markdown

Formatted tables for documentation and reports.

```python
config = ExportConfig(
    export_type=ExportType.PROXIES,
    export_format=ExportFormat.MARKDOWN,
    destination=LocalFileDestination(file_path="proxies.md"),
)
```

## Compression

Reduce export file sizes with built-in compression.

### GZIP Compression

```python
from proxywhirl import CompressionType

config = ExportConfig(
    export_type=ExportType.PROXIES,
    export_format=ExportFormat.JSON,
    destination=LocalFileDestination(file_path="proxies.json.gz"),
    compression=CompressionType.GZIP,
)
```

### ZIP Compression

```python
config = ExportConfig(
    export_type=ExportType.PROXIES,
    export_format=ExportFormat.JSON,
    destination=LocalFileDestination(file_path="proxies.zip"),
    compression=CompressionType.ZIP,
)
```

## Advanced Filtering

### Filter by Health Status

```python
proxy_filter = ProxyExportFilter(
    health_status=["healthy", "degraded"]
)
```

### Filter by Success Rate

```python
proxy_filter = ProxyExportFilter(
    min_success_rate=0.9  # Only proxies with 90%+ success rate
)
```

### Filter by Protocol

```python
proxy_filter = ProxyExportFilter(
    protocol=["http", "https"]  # Exclude SOCKS proxies
)
```

### Filter by Time Range

```python
from datetime import datetime, timedelta, timezone

proxy_filter = ProxyExportFilter(
    created_after=datetime.now(timezone.utc) - timedelta(days=7),
    last_success_after=datetime.now(timezone.utc) - timedelta(hours=1),
)
```

### Field Selection

```python
# Include only specific fields
proxy_filter = ProxyExportFilter(
    include_fields=["url", "health_status", "success_rate"]
)

# Exclude specific fields
proxy_filter = ProxyExportFilter(
    exclude_fields=["credentials", "metadata"]
)
```

## Export History

Track and query export operations.

```python
# Get recent export history
history = export_manager.get_export_history(limit=10)

for entry in history:
    print(f"{entry.export_type} -> {entry.export_format}: "
          f"{entry.records_exported} records ({entry.status})")
```

### Via REST API

```bash
# Get export history
curl http://localhost:8000/api/v1/exports/history?limit=10

# Get specific export status
curl http://localhost:8000/api/v1/exports/{job_id}
```

## Export Destinations

### Local File

```python
from proxywhirl import LocalFileDestination

destination = LocalFileDestination(
    file_path="exports/proxies.csv",
    overwrite=True,
    create_directories=True,
)
```

### Memory (In-Memory)

Return data directly without writing to disk.

```python
from proxywhirl import MemoryDestination

destination = MemoryDestination()

# Result will contain data in result.data
result = export_manager.export(config)
data = result.data
```

## Error Handling

```python
from proxywhirl.export_manager import ExportError

try:
    result = export_manager.export(config)
    if result.success:
        print(f"Export successful: {result.records_exported} records")
    else:
        print(f"Export failed: {result.error}")
except ExportError as e:
    print(f"Export error: {e}")
```

## Best Practices

### 1. Use Appropriate Formats

- **CSV**: Best for tabular data and spreadsheet analysis
- **JSON**: Best for programmatic consumption
- **JSONL**: Best for streaming and large datasets
- **YAML**: Best for human-readable configuration
- **Markdown**: Best for documentation and reports

### 2. Apply Filters

Filter data before export to reduce file sizes and processing time:

```python
# Export only healthy proxies from the last 24 hours
proxy_filter = ProxyExportFilter(
    health_status=["healthy"],
    created_after=datetime.now(timezone.utc) - timedelta(days=1),
    min_success_rate=0.8,
)
```

### 3. Use Compression

For large exports, always enable compression:

```python
config = ExportConfig(
    export_type=ExportType.PROXIES,
    export_format=ExportFormat.JSON,
    destination=LocalFileDestination(file_path="proxies.json.gz"),
    compression=CompressionType.GZIP,
)
```

### 4. Redact Sensitive Data

When exporting configurations, always redact secrets:

```python
config_filter = ConfigurationExportFilter(
    redact_secrets=True
)
```

### 5. Monitor Export History

Regularly review export history for auditing and troubleshooting:

```python
history = export_manager.get_export_history(limit=100)
failed_exports = [e for e in history if e.status == "failed"]
```

## REST API Reference

### Create Export

**POST** `/api/v1/exports`

```json
{
  "export_type": "proxies",
  "export_format": "csv",
  "destination_type": "local_file",
  "file_path": "exports/proxies.csv",
  "compression": "gzip",
  "health_status": ["healthy"],
  "min_success_rate": 0.8,
  "pretty_print": true,
  "include_metadata": true
}
```

### Get Export Status

**GET** `/api/v1/exports/{job_id}`

Returns current status and progress of an export job.

### Get Export History

**GET** `/api/v1/exports/history?limit=100`

Returns list of recent export operations with their status and results.

## Examples

See `examples/data_export_example.py` for comprehensive usage examples.

## Limitations

- S3 and HTTP destinations are planned for future releases
- Large exports (>1M records) may take several minutes
- Concurrent exports are limited to prevent resource exhaustion

## Troubleshooting

### Export Fails with "No proxy pool configured"

Ensure you initialize ExportManager with a proxy pool:

```python
export_manager = ExportManager(proxy_pool=pool)
```

### File Already Exists Error

Set `overwrite=True` in your destination:

```python
destination = LocalFileDestination(
    file_path="proxies.csv",
    overwrite=True,
)
```

### Permission Denied Error

Ensure the export destination directory is writable and the user has appropriate permissions.

## See Also

- [API Documentation](./rest-api.md)
- [Examples](../examples/)
- [Export Models Reference](../reference/export-models.md)
