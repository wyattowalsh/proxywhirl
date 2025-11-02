# proxywhirl Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-02

## Active Technologies

- Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) (005-caching-mechanisms-storage)
- Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) + httpx (HTTP client with proxy support), threading (background health checks), loguru (structured logging) (006-health-monitoring-continuous)
- Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) (008-metrics-observability-performance)
- Python 3.9+ + pandas>=2.0.0 (data analysis and aggregation) (009-analytics-engine-analysis)
- Python 3.9+ + pandas>=2.0.0, openpyxl>=3.1.0 (Excel export), reportlab>=4.0.0 (PDF generation), apscheduler>=3.10.0 (scheduled exports) (011-data-export)

## Project Structure

```text
proxywhirl/
tests/
.specify/
```

## Commands

uv run pytest tests/
uv run mypy --strict proxywhirl/
uv run ruff check proxywhirl/

## Code Style

Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13): Follow standard conventions
## Recent Changes

- 005-caching-mechanisms-storage: Added Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13)
- 006-health-monitoring-continuous: Added Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) + httpx (HTTP client with proxy support), threading (background health checks), loguru (structured logging)
- 008-metrics-observability-performance: Added Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13)
- 009-analytics-engine-analysis: Added pandas>=2.0.0 for analytics (NEW modules: analytics.py, analytics_models.py)
- 011-data-export: Added pandas, openpyxl, reportlab, apscheduler for data export/import (NEW modules: export.py, import.py, scheduled_export.py, export_models.py)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
