# proxywhirl Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-01

## Active Technologies

- Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) (005-caching-mechanisms-storage)
- Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) + httpx (HTTP client with proxy support), threading (background health checks), loguru (structured logging) (006-health-monitoring-continuous)
- Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) (008-metrics-observability-performance)
- Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) + reportlab (PDF generation), jinja2 (HTML templates via FastAPI), threading (scheduling), queue (concurrency), csv/json (stdlib formats) (010-automated-report)

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
- 010-automated-report: Added Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) + reportlab (PDF generation), jinja2 (HTML templates via FastAPI), threading (scheduling), queue (concurrency), csv/json (stdlib formats)tpx (HTTP client with proxy support), threading (background health checks), loguru (structured logging)
- 008-metrics-observability-performance: Added Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
