# Quickstart: Automated Reporting System

**Feature**: 010-automated-report  
**Date**: 2025-11-02  
**Status**: Complete

## Overview

This quickstart guide demonstrates how to use the automated reporting system to generate on-demand and scheduled reports about proxy pool performance, health, and usage statistics.

---

## Installation

The reporting feature is part of the core `proxywhirl` package. Install with PDF support:

```bash
uv add reportlab>=4.0.0
```

All other dependencies (jinja2, tenacity) are already installed via FastAPI.

---

## Basic Usage (Python API)

### Generate On-Demand Report

```python
from proxywhirl import ProxyRotator, ReportGenerator, SQLiteMetricsCollector
from datetime import datetime, timedelta, timezone

# Initialize proxy rotator with metrics tracking
rotator = ProxyRotator(
    proxies=["http://proxy1.com:8080", "http://proxy2.com:8080"],
    enable_metrics=True  # Required for reporting
)

# Make some requests to generate metrics data
for _ in range(100):
    response = rotator.get("https://api.example.com/data")

# Create metrics collector
metrics_collector = SQLiteMetricsCollector(db_path="./metrics.db")

# Initialize report generator
generator = ReportGenerator(metrics_collector=metrics_collector)

# Generate performance report for last 24 hours
report = generator.generate_report(
    report_type="performance",
    format="json",
    time_range_start=datetime.now(timezone.utc) - timedelta(hours=24),
    time_range_end=datetime.now(timezone.utc)
)

print(f"Report generated: {report.file_path}")
print(f"Generation time: {report.generation_time_ms}ms")
```

---

## Export Formats

### JSON Report

```python
report = generator.generate_report(
    report_type="performance",
    format="json",
    time_range_start=start_time,
    time_range_end=end_time
)

# Output: reports/on-demand/2025-11-02/performance_20251102T093045Z_a1b2c3d4.json
```

**JSON Structure**:
```json
{
  "report_id": "a1b2c3d4-uuid",
  "name": "Performance Report 2025-11-02",
  "generated_at": "2025-11-02T09:30:45Z",
  "time_range": {
    "start": "2025-11-01T09:30:45Z",
    "end": "2025-11-02T09:30:45Z"
  },
  "summary": {
    "total_requests": 15234,
    "total_successes": 14892,
    "total_failures": 342,
    "success_rate": 97.76,
    "avg_response_time_ms": 245.3
  },
  "proxies": [
    {
      "url": "http://proxy1.com:8080",
      "requests": 7621,
      "successes": 7445,
      "failures": 176,
      "success_rate": 97.69,
      "avg_response_time_ms": 238.7
    }
  ],
  "sources": {
    "free-proxy-list": {
      "requests": 5234,
      "success_rate": 96.2
    }
  }
}
```

### CSV Report

```python
report = generator.generate_report(
    report_type="performance",
    format="csv",
    time_range_start=start_time,
    time_range_end=end_time
)

# Output: reports/on-demand/2025-11-02/performance_20251102T093045Z_a1b2c3d4.csv
```

**CSV Structure**:
```csv
proxy_url,requests,successes,failures,success_rate,avg_response_time_ms
http://proxy1.com:8080,7621,7445,176,97.69,238.7
http://proxy2.com:8080,7613,7447,166,97.82,251.9
```

### HTML Report

```python
report = generator.generate_report(
    report_type="performance",
    format="html",
    time_range_start=start_time,
    time_range_end=end_time
)

# Output: reports/on-demand/2025-11-02/performance_20251102T093045Z_a1b2c3d4.html
# Opens in browser with styled tables and basic charts
```

### PDF Report

```python
report = generator.generate_report(
    report_type="performance",
    format="pdf",
    time_range_start=start_time,
    time_range_end=end_time
)

# Output: reports/on-demand/2025-11-02/performance_20251102T093045Z_a1b2c3d4.pdf
# Professional formatted PDF suitable for printing
```

---

## Report Templates

### Create Custom Template

```python
from proxywhirl import ReportTemplate, TemplateManager

# Initialize template manager
template_manager = TemplateManager(template_dir="./templates/user")

# Create custom template
template = ReportTemplate(
    name="daily-performance-summary",
    description="Daily summary focusing on success rates and response times",
    report_type="performance",
    metrics=["requests_total", "success_rate", "avg_response_time", "p95_response_time"],
    filters={
        "sources": ["free-proxy-list", "proxy-scraper"]  # Only include these sources
    },
    thresholds={
        "success_rate": 95.0,      # Highlight if below 95%
        "avg_response_time": 500.0  # Highlight if above 500ms
    },
    output_format="json"
)

# Save template
template_manager.save_template(template)
```

### Use Template

```python
# Generate report using template
report = generator.generate_from_template(
    template_name="daily-performance-summary",
    time_range_start=start_time,
    time_range_end=end_time
)

# Template filters and thresholds automatically applied
```

---

## Scheduled Reports

### Create Daily Report Schedule

```python
from proxywhirl import ReportSchedule, ScheduleManager

# Initialize schedule manager
schedule_manager = ScheduleManager(db_path="./schedules.db")

# Create daily schedule (runs at 9 AM UTC)
schedule = ReportSchedule(
    name="Daily Performance Report",
    description="Automated daily report summarizing yesterday's performance",
    template_id="daily-performance-summary",  # Use custom template
    cron_expression="0 9 * * *",  # Daily at 9 AM
    time_range_spec="yesterday",  # Yesterday's data
    output_directory="./reports/scheduled/daily",
    enabled=True,
    max_retries=3,
    retry_delay_seconds=300  # 5 minutes between retries
)

# Save and activate schedule
schedule_manager.create_schedule(schedule)

# Schedule will automatically generate reports at 9 AM UTC each day
```

### Other Schedule Examples

```python
# Hourly report (every hour on the hour)
hourly_schedule = ReportSchedule(
    name="Hourly Health Check",
    cron_expression="0 * * * *",
    time_range_spec="last_hour",
    ...
)

# Weekly report (Mondays at 8 AM)
weekly_schedule = ReportSchedule(
    name="Weekly Summary",
    cron_expression="0 8 * * 1",
    time_range_spec="last_7d",
    ...
)

# End of month report (1st of each month at midnight)
monthly_schedule = ReportSchedule(
    name="Monthly Report",
    cron_expression="0 0 1 * *",
    time_range_spec="last_30d",
    ...
)
```

---

## REST API Usage

### Generate Report via API

```bash
curl -X POST http://localhost:8000/api/v1/reports/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "report_type": "performance",
    "format": "json",
    "time_range_start": "2025-11-01T00:00:00Z",
    "time_range_end": "2025-11-02T00:00:00Z"
  }'

# Response:
# {
#   "report_id": "a1b2c3d4-uuid",
#   "status": "generating",
#   "estimated_completion_seconds": 5,
#   "status_url": "/api/v1/reports/a1b2c3d4-uuid/status",
#   "download_url": "/api/v1/reports/a1b2c3d4-uuid/download"
# }
```

### Check Report Status

```bash
curl -X GET http://localhost:8000/api/v1/reports/a1b2c3d4-uuid/status \
  -H "X-API-Key: your-api-key"

# Response:
# {
#   "report_id": "a1b2c3d4-uuid",
#   "status": "completed",
#   "generation_time_ms": 3245,
#   "download_url": "/api/v1/reports/a1b2c3d4-uuid/download"
# }
```

### Download Report

```bash
curl -X GET http://localhost:8000/api/v1/reports/a1b2c3d4-uuid/download \
  -H "X-API-Key: your-api-key" \
  -o report.json
```

---

## CLI Usage

```bash
# Generate on-demand report
uv run proxywhirl report generate \
  --type performance \
  --format json \
  --start "2025-11-01T00:00:00Z" \
  --end "2025-11-02T00:00:00Z" \
  --output ./reports/

# Create template
uv run proxywhirl report template create \
  --name daily-summary \
  --type performance \
  --metrics requests_total,success_rate,avg_response_time \
  --format json

# Schedule daily report
uv run proxywhirl report schedule create \
  --name "Daily Report" \
  --template daily-summary \
  --cron "0 9 * * *" \
  --time-range yesterday \
  --output ./reports/scheduled/

# List all reports
uv run proxywhirl report list --status completed --limit 10

# List schedules
uv run proxywhirl report schedule list
```

---

## Advanced Usage

### Custom Filters

```python
# Filter by specific proxy URLs
report = generator.generate_report(
    report_type="performance",
    format="json",
    time_range_start=start_time,
    time_range_end=end_time,
    filters={
        "proxy_urls": ["http://proxy1.com:8080", "http://proxy3.com:8080"]
    }
)

# Filter by source
report = generator.generate_report(
    report_type="performance",
    format="json",
    time_range_start=start_time,
    time_range_end=end_time,
    filters={
        "sources": ["free-proxy-list"]
    }
)
```

### Streaming Large Reports

```python
# For very large datasets (1M+ metrics), use streaming
from proxywhirl import stream_report_data

# Stream metrics incrementally (constant memory usage)
metrics_stream = stream_report_data(
    collector=metrics_collector,
    start_time=start_time,
    end_time=end_time,
    chunk_size=1000  # Process 1000 metrics at a time
)

# Generate CSV with streaming
with open("large_report.csv", "w") as f:
    generate_csv_stream(metrics_stream, f)

# Memory usage: <100MB regardless of dataset size
```

### Concurrent Report Generation

```python
from concurrent.futures import ThreadPoolExecutor

# Generate multiple reports concurrently (max 3 concurrent)
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = []
    
    for report_type in ["performance", "health", "aggregate"]:
        future = executor.submit(
            generator.generate_report,
            report_type=report_type,
            format="json",
            time_range_start=start_time,
            time_range_end=end_time
        )
        futures.append(future)
    
    # Wait for all reports to complete
    reports = [f.result() for f in futures]
```

---

## Configuration

### Environment Variables

```bash
# Report output directory
export PROXYWHIRL_REPORT_DIR="./reports"

# Template directory
export PROXYWHIRL_TEMPLATE_DIR="./templates"

# Report retention period (days)
export PROXYWHIRL_REPORT_RETENTION_DAYS=30

# Maximum concurrent reports
export PROXYWHIRL_MAX_CONCURRENT_REPORTS=3

# Metrics database path
export PROXYWHIRL_METRICS_DB="./metrics.db"
```

### Configuration File (pyproject.toml)

```toml
[tool.proxywhirl.reporting]
output_directory = "./reports"
template_directory = "./templates"
retention_days = 30
max_concurrent_reports = 3
chunk_size = 1000  # Streaming chunk size
```

---

## Testing

### Unit Test Example

```python
import pytest
from proxywhirl import ReportGenerator, MockMetricsCollector

def test_generate_performance_report():
    # Use mock collector for testing
    collector = MockMetricsCollector()
    generator = ReportGenerator(metrics_collector=collector)
    
    report = generator.generate_report(
        report_type="performance",
        format="json",
        time_range_start=start_time,
        time_range_end=end_time
    )
    
    assert report.status == "completed"
    assert report.file_path.exists()
    assert report.generation_time_ms > 0
```

---

## Common Patterns

### Daily Report with Email (Scheduled)

```python
# Schedule daily report with custom post-processing
def email_report_callback(report: Report):
    """Send report via email after generation."""
    send_email(
        to="team@example.com",
        subject=f"Daily Performance Report - {report.generated_at.date()}",
        attachment=report.file_path
    )

schedule = ReportSchedule(
    name="Daily Report with Email",
    cron_expression="0 9 * * *",
    time_range_spec="yesterday",
    ...
)

# Register callback
schedule_manager.add_completion_callback(schedule.id, email_report_callback)
```

### Real-time Report Generation

```python
# Generate report immediately after request batch
async def process_request_batch():
    # Make 1000 requests
    for _ in range(1000):
        await rotator.async_get("https://api.example.com")
    
    # Generate immediate report
    report = generator.generate_report(
        report_type="performance",
        format="json",
        time_range_start=datetime.now(timezone.utc) - timedelta(minutes=5),
        time_range_end=datetime.now(timezone.utc)
    )
    
    return report
```

---

## Troubleshooting

### Report Generation Fails

```python
try:
    report = generator.generate_report(...)
except ReportGenerationError as e:
    print(f"Generation failed: {e}")
    print(f"Error details: {e.details}")
```

**Common Issues**:
- **Insufficient data**: No metrics data for specified time range
  - Solution: Check time range, ensure metrics collection is enabled
- **Invalid template**: Referenced metric doesn't exist
  - Solution: Validate template against available metrics
- **Disk space**: Output directory full
  - Solution: Clean old reports, check retention settings

### Slow Report Generation

- **Large time ranges**: Reduce time range or use streaming
- **Too many metrics**: Filter to specific proxies/sources
- **Disk I/O**: Use SSD for report output directory

### Memory Usage High

- **Not streaming**: Ensure using streaming for large datasets
- **Chunk size too large**: Reduce `chunk_size` parameter (default 1000)

---

## Best Practices

1. **Use streaming** for datasets >10,000 metrics
2. **Set retention period** to automatically clean old reports (default 30 days)
3. **Limit concurrent reports** to 3 to prevent resource exhaustion
4. **Use templates** for consistent recurring reports
5. **Schedule reports during low traffic** hours (e.g., 2-4 AM)
6. **Monitor schedule failures** and adjust retry settings
7. **Validate templates** before creating schedules
8. **Use filters** to reduce report size for targeted analysis

---

## Next Steps

- See [data-model.md](data-model.md) for complete entity definitions
- See [api-contracts.md](contracts/api-contracts.md) for REST API details
- See [research.md](research.md) for technical decisions and rationale
- See [tasks.md](tasks.md) for implementation checklist (once generated)

---

## Examples Repository

Full working examples available at:
```
examples/
├── basic_reporting.py           # Simple on-demand report generation
├── scheduled_reports.py         # Automated scheduled reports
├── custom_templates.py          # Creating and using custom templates
├── streaming_large_reports.py   # Memory-efficient large dataset handling
└── rest_api_client.py          # REST API usage examples
```
