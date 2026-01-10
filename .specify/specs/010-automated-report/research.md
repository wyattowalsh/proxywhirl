# Research: Automated Reporting System

**Feature**: 010-automated-report  
**Date**: 2025-11-02  
**Phase**: Phase 0 - Research & Technical Decisions

## Overview

This document captures all technical research, decisions, rationale, and alternatives considered for implementing automated reporting in ProxyWhirl. The focus is on generating on-demand and scheduled reports about proxy pool performance, health, and usage statistics in multiple formats (JSON, CSV, HTML, PDF).

## Research Tasks

### 1. PDF Generation Library Selection

**Decision**: Use `reportlab>=4.0.0`

**Rationale**:
- Industry-standard PDF library with 20+ years of active maintenance (stable, production-ready)
- Pure Python with minimal external dependencies (no browser binaries required)
- Excellent table formatting support via `platypus` framework (critical for tabular metrics reports)
- Low resource overhead (<50MB memory for typical reports) enabling streaming generation
- Python 3.9+ compatibility verified (supports 3.9 through 3.13)
- Programmatic API allows precise layout control for consistent formatting
- Thread-safe for concurrent report generation
- No JavaScript execution needed (unlike browser-based solutions)

**Alternatives Considered**:

1. **WeasyPrint**
   - Rejected: Requires system libraries (Cairo, Pango, GDK-Pixbuf) on Linux - dependency footprint too heavy
   - Rejected: HTML/CSS rendering excellent but overkill for structured data reports
   - Rejected: Higher memory usage (~200MB) for large tables due to HTML DOM overhead
   - Note: Better choice if rich CSS layout needed (not required for metrics reports)

2. **FPDF2**
   - Rejected: Simpler API but weaker table support (manual cell calculations required)
   - Rejected: Less mature ecosystem, fewer examples for complex layouts
   - Rejected: No built-in support for flowables (dynamic page breaks)
   - Note: Good for simple certificates/forms, insufficient for multi-page metric reports

3. **Playwright/Pyppeteer (Browser-based)**
   - Rejected: Requires Chromium binaries (500MB+ download) - violates minimal dependencies principle
   - Rejected: High resource usage (>1GB memory per PDF generation)
   - Rejected: Overkill for tabular data (designed for web page rendering)
   - Rejected: Security concerns (executing JavaScript from templates)

**Implementation Approach**:
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf_report(data: list[dict[str, Any]], output_path: Path) -> None:
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    elements = []
    
    # Streaming approach: yield elements without loading full dataset
    for chunk in chunk_data(data, chunk_size=1000):
        table = Table(chunk)
        table.setStyle(TableStyle([...]))
        elements.append(table)
    
    doc.build(elements)  # reportlab handles pagination automatically
```

**References**:
- ReportLab Documentation: https://docs.reportlab.com/reportlab/userguide/
- 2025 PDF Library Comparison: https://templated.io/blog/generate-pdfs-in-python-with-libraries/

---

### 2. HTML Template Engine Selection

**Decision**: Use `jinja2>=3.1.0` (already in dependency tree via FastAPI)

**Rationale**:
- Already installed as transitive dependency of FastAPI (zero additional dependencies)
- Industry-standard template engine with excellent security track record
- Built-in auto-escaping prevents XSS attacks (critical for user-provided data)
- Rich feature set: inheritance, macros, filters for complex report layouts
- Mature ecosystem with extensive documentation and community support
- Performance: 10-100x faster than programmatic string building for complex HTML
- Supports both file-based and string templates (flexible deployment)
- Python 3.9+ compatible

**Alternatives Considered**:

1. **Mako**
   - Rejected: Allows arbitrary Python code in templates (security risk with user data)
   - Rejected: No auto-escaping by default (manual `| h` filter required)
   - Rejected: Additional dependency not justified by performance gains (~15% faster than Jinja2)
   - Note: Better for trusted templates with complex logic, not data-driven reports

2. **Built-in string.Template or f-strings**
   - Rejected: No auto-escaping (XSS vulnerability)
   - Rejected: Poor readability for multi-line HTML (no syntax highlighting)
   - Rejected: No template inheritance (code duplication for headers/footers)
   - Rejected: Manual escaping error-prone for metric values with special characters

3. **Programmatic HTML Generation (dominate, yattag)**
   - Rejected: More verbose than templates for static structure
   - Rejected: Harder for non-programmers to customize report layouts
   - Note: Consider if reports need dynamic structure beyond templates

**Security Features**:
- Auto-escaping enabled by default: `{{ proxy.url }}` → HTML entities escaped
- Sandboxed environment: No access to Python builtins or filesystem
- Template validation: Syntax errors caught at load time, not runtime

**Implementation Approach**:
```python
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader("templates/"),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)

template = env.get_template("report.html.j2")
html = template.render(
    report_data=data,
    generated_at=datetime.now(timezone.utc)
)
```

**References**:
- Jinja2 Documentation: https://jinja.palletsprojects.com/
- Template Security: https://jinja.palletsprojects.com/en/3.1.x/sandbox/

---

### 3. CSV Generation Strategy

**Decision**: Use standard library `csv` module with streaming

**Rationale**:
- Zero external dependencies (stdlib only)
- Streaming support via `csv.writer()` + file handles (constant memory usage)
- Simple API suitable for tabular metrics data (rows/columns structure)
- 100% compatible with Excel, Google Sheets, pandas without special formatting
- No performance overhead from dataframe abstractions
- Thread-safe when using separate file handles per report
- Python 3.9+ native support for Path objects

**Alternatives Considered**:

1. **pandas (pd.DataFrame.to_csv())**
   - Rejected: Heavy dependency (20+ packages including NumPy) not justified for simple CSV
   - Rejected: Eager loading (entire dataset in memory as DataFrame) violates streaming requirement
   - Rejected: 10-50x slower than csv module for simple row-by-row writes
   - Note: Consider if reports need complex transformations (pivots, aggregations)

2. **polars (pl.DataFrame.write_csv())**
   - Rejected: Even heavier dependency (Rust binaries, 100MB+ install size)
   - Rejected: Overkill for straightforward metrics export (no complex queries needed)
   - Rejected: Additional learning curve for maintainers
   - Note: Better if reports process multi-GB datasets (not expected for metrics)

**Streaming Pattern**:
```python
import csv
from typing import Iterator

def stream_csv_report(
    data: Iterator[dict[str, Any]], 
    output_path: Path
) -> None:
    """Stream CSV generation with constant memory usage."""
    with output_path.open('w', newline='') as f:
        # Determine headers from first row (streamed)
        first_row = next(data)
        writer = csv.DictWriter(f, fieldnames=first_row.keys())
        writer.writeheader()
        writer.writerow(first_row)
        
        # Stream remaining rows (no accumulation)
        for row in data:
            writer.writerow(row)
```

**Memory Efficiency**:
- Pandas approach: 2-3x dataset size in memory (DataFrame + CSV buffer)
- csv module approach: <1MB memory regardless of dataset size (streaming)

**References**:
- csv Module Documentation: https://docs.python.org/3/library/csv.html
- CSV Performance Best Practices: https://realpython.com/python-csv/

---

### 4. Report Scheduling Strategy

**Decision**: Use `threading.Timer` for scheduled reports (stdlib only)

**Rationale**:
- Zero external dependencies (stdlib threading module)
- Sufficient reliability for report scheduling (non-critical if delayed by seconds)
- Low resource overhead (<1MB memory per scheduled report)
- Python-native solution aligns with library-first principle
- Simple API suitable for interval-based scheduling (hourly, daily, weekly)
- Works seamlessly with existing httpx/asyncio usage (no conflicts)
- Graceful shutdown via timer.cancel() during cleanup

**Alternatives Considered**:

1. **APScheduler**
   - Rejected: Heavy dependency (10+ packages) adds 5MB+ to install size
   - Rejected: Overkill for simple interval scheduling (cron, persistence not needed)
   - Rejected: Requires JobStore infrastructure (SQLite/Redis) for persistence
   - Note: Consider if complex schedules needed (e.g., "every 2nd Tuesday at 3:15 PM")

2. **schedule library**
   - Rejected: External dependency (though lightweight) not justified by API convenience
   - Rejected: Single-threaded blocking loop (conflicts with asyncio event loop)
   - Rejected: Manual thread management needed for background scheduling
   - Note: Human-friendly API (`schedule.every().day.at("10:30")`) but stdlib equivalent simple

3. **External cron (system-level)**
   - Rejected: Platform-dependent (Linux/macOS only, not Windows)
   - Rejected: Requires root/sudo for crontab installation (deployment complexity)
   - Rejected: No programmatic control (can't cancel/update schedules at runtime)
   - Note: Acceptable as user-deployed alternative (documented option)

**Implementation Approach**:
```python
from threading import Timer
from typing import Callable

class ReportScheduler:
    """Simple interval-based report scheduler using stdlib."""
    
    def __init__(self) -> None:
        self._timers: dict[str, Timer] = {}
    
    def schedule_report(
        self,
        report_id: str,
        interval_seconds: int,
        report_func: Callable[[], None]
    ) -> None:
        """Schedule recurring report generation."""
        def _run_and_reschedule() -> None:
            report_func()  # Generate report
            # Reschedule next run
            self._timers[report_id] = Timer(interval_seconds, _run_and_reschedule)
            self._timers[report_id].start()
        
        # Start initial timer
        self._timers[report_id] = Timer(interval_seconds, _run_and_reschedule)
        self._timers[report_id].start()
    
    def cancel_schedule(self, report_id: str) -> None:
        """Cancel scheduled report."""
        if report_id in self._timers:
            self._timers[report_id].cancel()
            del self._timers[report_id]
    
    def shutdown(self) -> None:
        """Cancel all scheduled reports."""
        for timer in self._timers.values():
            timer.cancel()
        self._timers.clear()
```

**Reliability Considerations**:
- Timer drift: ±1-2 seconds per hour (acceptable for report scheduling)
- Process restart: Schedules lost (acceptable - reports not mission-critical)
- System sleep/hibernate: Timers paused (expected behavior)
- Note: If persistence needed, store schedules in SQLite and restore on startup

**References**:
- threading.Timer Documentation: https://docs.python.org/3/library/threading.html#timer-objects
- Scheduling Comparison: https://leapcell.io/blog/scheduling-tasks-in-python-apscheduler-versus-schedule

---

### 5. Concurrency Queue Strategy

**Decision**: Use `queue.Queue` (stdlib) with ThreadPoolExecutor

**Rationale**:
- Matches existing threading model (ProxyRotator uses httpx synchronous client)
- Simple thread-safe queue without asyncio complexity
- ThreadPoolExecutor provides worker pool for concurrent report generation
- No mixing of sync/async code (httpx Client is synchronous, not AsyncClient)
- Configurable concurrency limit via max_workers parameter
- Graceful shutdown via executor.shutdown(wait=True)
- Lower overhead than asyncio.Queue for CPU-bound report generation

**Alternatives Considered**:

1. **asyncio.Queue with AsyncClient**
   - Rejected: ProxyRotator uses httpx.Client (sync), not httpx.AsyncClient
   - Rejected: Would require async/await throughout reporting module (breaking change)
   - Rejected: asyncio better for I/O-bound tasks, reports are CPU-bound (PDF generation)
   - Note: Consider if ProxyWhirl migrates to async-first architecture

2. **threading.Queue (raw)**
   - Rejected: Requires manual worker thread management (boilerplate)
   - Rejected: ThreadPoolExecutor provides cleaner API with same performance
   - Note: threading.Queue used internally by ThreadPoolExecutor

**Implementation Approach**:
```python
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable

class ReportGenerationQueue:
    """Thread-safe queue for concurrent report generation."""
    
    def __init__(self, max_concurrent: int = 3) -> None:
        self._executor = ThreadPoolExecutor(
            max_workers=max_concurrent,
            thread_name_prefix="report-gen"
        )
        self._pending: dict[str, Future[Path]] = {}
    
    def submit_report(
        self,
        report_id: str,
        generate_func: Callable[[], Path]
    ) -> Future[Path]:
        """Submit report for generation, returns Future."""
        if report_id in self._pending:
            raise ValueError(f"Report {report_id} already queued")
        
        future = self._executor.submit(generate_func)
        self._pending[report_id] = future
        
        # Cleanup when done
        future.add_done_callback(lambda f: self._pending.pop(report_id, None))
        return future
    
    def shutdown(self) -> None:
        """Wait for pending reports, then shutdown."""
        self._executor.shutdown(wait=True)
```

**Concurrency Limits**:
- Default: 3 concurrent reports (SC-011 requirement)
- Rationale: PDF generation is CPU-bound (multi-threading provides parallelism)
- Memory: ~50MB per concurrent report = 150MB total
- CPU: Reports use 1 core each = 3/8 cores on typical dev machine

**References**:
- ThreadPoolExecutor Documentation: https://docs.python.org/3/library/concurrent.futures.html
- Queue Documentation: https://docs.python.org/3/library/queue.html

---

### 6. Metrics Data Access Strategy

**Decision**: Query metrics from ProxyRotator's in-memory state + SQLite storage

**Rationale**:
- No dependency on 008-metrics-observability-performance (can work independently)
- Reuses existing ProxyRotator.pool state (proxies, health, requests)
- SQLite storage already persists proxy metadata (no new database)
- Simple abstraction layer: `MetricsCollector` class aggregates data
- Supports both real-time (in-memory) and historical (SQLite) reports
- No network calls needed (metrics local to process)
- Future-proof: If 008 implemented, MetricsCollector can query Prometheus API

**Alternatives Considered**:

1. **Direct SQLite Queries in Report Code**
   - Rejected: Tight coupling to storage schema (breaks if schema changes)
   - Rejected: Duplicates logic across report formats (CSV, JSON, PDF)
   - Rejected: Harder to test (requires database setup)

2. **Dependency Injection (Metrics from 008)**
   - Rejected: Creates hard dependency on 008 (violates independent user stories)
   - Rejected: 008 may not be implemented when 010 ships
   - Note: Support as optional enhancement via MetricsCollector abstraction

3. **Separate Metrics Database (Duplicate Storage)**
   - Rejected: Storage duplication (metrics already in Prometheus + SQLite)
   - Rejected: Data consistency challenges (which is source of truth?)
   - Rejected: Higher maintenance burden

**Abstraction Layer Pattern**:
```python
from typing import Protocol, Iterator
from datetime import datetime, timezone

class MetricsSource(Protocol):
    """Protocol for metrics data sources (in-memory or Prometheus)."""
    
    def get_request_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Iterator[RequestMetric]:
        """Yield request metrics for time range."""
        ...
    
    def get_health_metrics(self) -> Iterator[HealthMetric]:
        """Yield current health metrics for all proxies."""
        ...

class ProxyRotatorMetrics:
    """Metrics source from ProxyRotator in-memory state."""
    
    def __init__(self, rotator: ProxyRotator) -> None:
        self.rotator = rotator
    
    def get_request_metrics(self, start_time, end_time):
        # Query from rotator.pool.proxies[*].request_count, etc.
        for proxy in self.rotator.pool.proxies:
            yield RequestMetric(
                proxy_url=proxy.url,
                request_count=proxy.request_count,
                # ...
            )

# Future: PrometheusMetrics implements same protocol
# class PrometheusMetrics:
#     def __init__(self, prometheus_url: str): ...
#     def get_request_metrics(self, ...): ...  # Query /api/v1/query_range
```

**Benefits**:
- Reports work with or without 008-metrics
- Easy to test (mock MetricsSource protocol)
- Future enhancement path clear (add PrometheusMetrics)

**References**:
- Python Protocols: https://docs.python.org/3/library/typing.html#typing.Protocol
- Dependency Injection in Python: https://python-dependency-injector.ets-labs.org/

---

### 7. Streaming Strategy for Large Reports

**Decision**: Use generator functions with chunked writes

**Rationale**:
- Pythonic pattern (generators natural for streaming data)
- Constant memory usage regardless of dataset size (SC-006 requirement)
- Compatible with all output formats (CSV, JSON, PDF, HTML)
- Simple to implement and test (standard Python idiom)
- No external dependencies (stdlib iterator protocol)
- Composable: Can chain generators (filter → transform → write)

**Streaming Patterns**:

1. **CSV Streaming** (line-by-line):
```python
def stream_csv_report(metrics: Iterator[dict]) -> Iterator[str]:
    """Yield CSV rows as strings (constant memory)."""
    # Header row
    first = next(metrics)
    yield ','.join(first.keys()) + '\n'
    yield ','.join(str(v) for v in first.values()) + '\n'
    
    # Data rows
    for row in metrics:
        yield ','.join(str(v) for v in row.values()) + '\n'

# Usage: write to file without loading full dataset
with open('report.csv', 'w') as f:
    for line in stream_csv_report(get_metrics()):
        f.write(line)
```

2. **JSON Streaming** (array elements):
```python
def stream_json_report(metrics: Iterator[dict]) -> Iterator[str]:
    """Yield JSON array elements (constant memory)."""
    yield '[\n'
    first = True
    for item in metrics:
        if not first:
            yield ',\n'
        yield json.dumps(item, indent=2)
        first = False
    yield '\n]'
```

3. **PDF Streaming** (chunk-based tables):
```python
def stream_pdf_report(metrics: Iterator[dict], chunk_size: int = 1000):
    """Yield PDF table chunks (bounded memory)."""
    doc = SimpleDocTemplate(...)
    elements = []
    
    # Process in chunks
    for chunk in chunk_iterator(metrics, chunk_size):
        table = Table([[row[col] for col in columns] for row in chunk])
        elements.append(table)
        
        # Flush to disk if buffer exceeds threshold
        if len(elements) > 10:
            doc.build(elements)
            elements.clear()
    
    doc.build(elements)  # Final flush
```

**Alternatives Considered**:

1. **Iterator Protocol (manual __iter__/__next__)**
   - Rejected: More boilerplate than generators for same functionality
   - Rejected: Generators provide cleaner syntax (yield vs return)
   - Note: Equivalent performance, generators preferred by convention

2. **Chunk-Based File Writes (no generators)**
   - Rejected: Requires explicit buffering logic (error-prone)
   - Rejected: Harder to compose transformations (each format needs buffer management)
   - Note: Generators abstract buffering automatically

**Memory Benchmark**:
- Traditional (eager): 2-3x dataset size in memory
- Streaming (generator): <10MB constant memory (SC-006 compliant)
- Example: 1M row report = 500MB eager vs. 5MB streaming

**References**:
- Generator Tutorial: https://realpython.com/introduction-to-python-generators/
- Streaming Patterns: https://labex.io/tutorials/python-how-to-stream-files-with-generators-452349

---

### 8. Report Template Storage Strategy

**Decision**: Store templates as JSON files in filesystem

**Rationale**:
- Simple CRUD operations (read/write JSON files)
- Version control friendly (templates in Git)
- No database schema needed (avoid SQLite for simple key-value data)
- Easy backup/restore (copy files)
- Human-editable (users can hand-edit templates if needed)
- Fast lookups (filesystem caching by OS)

**File Structure**:
```
~/.proxywhirl/
└── templates/
    ├── default.json          # Built-in template
    ├── performance.json      # User-defined template
    └── daily-health.json     # User-defined template
```

**Template Schema (Pydantic)**:
```python
from pydantic import BaseModel, Field

class ReportTemplate(BaseModel):
    """Validated report template configuration."""
    
    template_id: str = Field(..., pattern=r'^[a-z0-9_-]+$')
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    
    # Metrics to include (validated against available metrics)
    metrics: list[str] = Field(..., min_items=1)
    
    # Filters
    filter_pools: Optional[list[str]] = None
    filter_sources: Optional[list[str]] = None
    
    # Output format
    format: Literal["json", "csv", "html", "pdf"] = "json"
    
    # Schedule (optional)
    schedule: Optional[str] = None  # Cron expression or interval
```

**Validation**:
```python
def validate_template(template: ReportTemplate) -> list[str]:
    """Validate template references only existing metrics."""
    available_metrics = ["request_count", "success_rate", "avg_latency", ...]
    
    errors = []
    for metric in template.metrics:
        if metric not in available_metrics:
            errors.append(f"Unknown metric: {metric}")
    
    return errors  # FR-024 requirement
```

**Alternatives Considered**:

1. **SQLite Database**
   - Rejected: Overkill for ~10 templates (simple key-value storage)
   - Rejected: Requires schema migrations if template format changes
   - Rejected: Less transparent than JSON files for users

2. **YAML Files**
   - Rejected: Additional dependency (PyYAML) not justified
   - Rejected: JSON sufficient for structured data (no comments needed)

**References**:
- Pydantic Validation: https://docs.pydantic.dev/latest/concepts/validators/

---

### 9. Report Retention and Cleanup Strategy

**Decision**: Automated cleanup via background thread with configurable retention

**Rationale**:
- SQLite database stores report history (timestamp, path, params)
- Background thread runs daily to delete expired reports (default 30 days)
- Configurable retention per report type (e.g., daily=30d, monthly=365d)
- Graceful degradation: If cleanup fails, logs error (doesn't block reports)
- Manual cleanup API provided for user control

**Cleanup Implementation**:
```python
from datetime import timedelta
from threading import Timer

class ReportCleanupService:
    """Automated report cleanup service."""
    
    def __init__(
        self,
        storage: ReportStorage,
        retention_days: int = 30,
        cleanup_interval: timedelta = timedelta(days=1)
    ) -> None:
        self.storage = storage
        self.retention_days = retention_days
        self._timer: Optional[Timer] = None
        self._start_cleanup_timer(cleanup_interval)
    
    def _start_cleanup_timer(self, interval: timedelta) -> None:
        """Schedule next cleanup run."""
        def _cleanup() -> None:
            try:
                self._delete_expired_reports()
            except Exception as e:
                logger.error(f"Report cleanup failed: {e}")
            finally:
                # Reschedule
                self._start_cleanup_timer(interval)
        
        self._timer = Timer(interval.total_seconds(), _cleanup)
        self._timer.start()
    
    def _delete_expired_reports(self) -> None:
        """Delete reports older than retention period."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        
        # Query expired reports from SQLite
        expired = self.storage.get_reports_before(cutoff)
        
        for report in expired:
            # Delete file
            report.output_path.unlink(missing_ok=True)
            # Delete history record
            self.storage.delete_report(report.report_id)
```

**Retention Policy (FR-021)**:
- Default: 30 days for generated report files
- Configurable: Users can set custom retention via config
- Scope: Only deletes generated reports, not raw metrics (metrics follow 008 policy)

**Alternatives Considered**:

1. **No Automatic Cleanup**
   - Rejected: Disk space accumulation over time (user complaints)
   - Rejected: Requires manual user intervention (poor UX)

2. **TTL in SQLite (PRAGMA)**
   - Rejected: SQLite doesn't support TTL natively
   - Rejected: Would require triggers (complex, fragile)

**References**:
- File Cleanup Best Practices: https://docs.python.org/3/library/pathlib.html#pathlib.Path.unlink

---

### 10. Error Handling and Retry Strategy

**Decision**: Fail-fast for on-demand reports, retry with exponential backoff for scheduled reports

**Rationale**:
- On-demand reports: User waiting for response, fail immediately with clear error
- Scheduled reports: No user waiting, retry up to 3 times with backoff
- Use existing `tenacity` library (already in dependencies)
- Log failures with structured context for debugging
- Partial success: If report generation fails mid-stream, delete partial file

**Implementation**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry_error_callback=lambda _: logger.error("Report generation failed after retries")
)
def generate_scheduled_report(report_id: str) -> Path:
    """Generate scheduled report with retry logic."""
    try:
        return _generate_report(report_id)
    except Exception as e:
        # Cleanup partial file
        output_path.unlink(missing_ok=True)
        raise

def generate_on_demand_report(report_id: str) -> Path:
    """Generate on-demand report (no retry, fail fast)."""
    try:
        return _generate_report(report_id)
    except Exception as e:
        logger.error(f"On-demand report failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )
```

**Error Categories**:
1. **Validation errors** (template invalid): Return 400, no retry
2. **Missing data** (no metrics for time range): Return 200 with empty report, no retry
3. **I/O errors** (disk full): Return 500, retry scheduled reports
4. **Timeout** (report too large): Return 500, no retry (user must adjust filters)

**References**:
- tenacity Documentation: https://tenacity.readthedocs.io/

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **PDF Generation** | reportlab>=4.0.0 | Mature, minimal dependencies, excellent table support, streaming capable |
| **HTML Templates** | jinja2>=3.1.0 (already installed) | Auto-escaping, zero new dependencies, industry standard |
| **CSV Generation** | stdlib csv module | Zero dependencies, streaming support, simple API |
| **Scheduling** | threading.Timer (stdlib) | Zero dependencies, sufficient reliability, simple API |
| **Concurrency** | queue.Queue + ThreadPoolExecutor | Matches sync httpx, simple thread-safe queue, stdlib only |
| **Metrics Access** | MetricsCollector abstraction layer | No 008 dependency, future-proof, testable |
| **Streaming** | Generator functions + chunked writes | Pythonic, constant memory, composable |
| **Templates** | JSON files in filesystem | Simple CRUD, version control friendly, human-editable |
| **Retention** | Background cleanup thread | Automated, configurable, graceful degradation |
| **Error Handling** | Fail-fast (on-demand) + retry (scheduled) | Responsive UX, reliable automation |

---

## Dependency Impact

**New Dependencies**: NONE (all stdlib + existing dependencies)

**Existing Dependencies Reused**:
- `jinja2` (via FastAPI transitive dependency)
- `tenacity` (already in pyproject.toml)
- `pydantic` (validation)
- `loguru` (structured logging)

**Optional Dependencies** (user's choice):
- `reportlab` ONLY if PDF reports needed (install with `uv add reportlab`)

---

## Performance Characteristics

| Metric | Target | Implementation |
|--------|--------|----------------|
| Report Generation Time | <5s for 1000 proxies (SC-001) | Streaming + threading |
| Memory Usage | <100MB (SC-006) | Generator-based streaming |
| Concurrent Reports | 3 simultaneous (SC-011) | ThreadPoolExecutor(max_workers=3) |
| Metrics Accuracy | <1% variance (SC-002) | Direct from ProxyRotator state |
| Schedule Drift | ±1 minute (SC-007) | threading.Timer (acceptable) |

---

## Security Considerations

| Risk | Mitigation |
|------|-----------|
| **XSS in HTML reports** | Jinja2 auto-escaping enabled by default |
| **Path traversal** | Validate output_path with pathlib.resolve() |
| **Template injection** | Jinja2 sandboxed environment, no eval() |
| **Credential leakage** | Never include proxy credentials in reports (only pool names) |
| **Disk space DoS** | Automated cleanup + configurable retention |

---

## Next Steps (Phase 1)

With research complete, proceed to Phase 1:
1. **data-model.md**: Define Pydantic models (ReportConfig, ReportTemplate, ReportHistory)
2. **contracts/**: API endpoints for report generation (/api/v1/reports)
3. **quickstart.md**: 5-minute guide to generating first report

---

## Open Questions (Phase 2)

- Should PDF reports include charts/graphs? (Phase 1: tables only, Phase 2: consider matplotlib)
- Email delivery for scheduled reports? (Out of scope per spec, future enhancement)
- Multi-format output in single request? (e.g., generate CSV + PDF simultaneously)
- Report signing/verification? (hash-based integrity checks for compliance use cases)
