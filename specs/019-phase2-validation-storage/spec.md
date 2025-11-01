# Feature Specification: Phase 2 - Validation & Storage

**Feature Branch**: `019-phase2-validation-storage`  
**Created**: 2025-10-22  
**Status**: Draft  
**Phase**: Phase 2 (v0.2.0)  
**Dependencies**: Feature 001 (Core Package) - COMPLETE

## Overview

Phase 2 builds on the core package (US1-US7) by adding robust proxy validation, persistent storage, and continuous health monitoring. This enables production-grade proxy management with reliability, persistence, and automated quality control.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Level Proxy Validation (Priority: P1)

A user fetches proxies from free public sources and needs multi-level validation (format, TCP, HTTP, anonymity) to filter out dead proxies before adding them to the rotation pool.

**Why this priority**: Essential for quality - prevents dead/broken proxies from entering the pool, improving success rates.

**Independent Test**: Can be tested by providing proxies at different quality levels and verifying appropriate validation passes/fails.

**Acceptance Scenarios**:

1. **Given** raw proxy URLs, **When** format validation runs, **Then** only syntactically valid URLs pass (host:port format)
2. **Given** format-valid proxies, **When** TCP validation runs, **Then** only connectable proxies pass (connection test)
3. **Given** TCP-valid proxies, **When** HTTP validation runs, **Then** only HTTP-responsive proxies pass (request test)
4. **Given** HTTP-valid proxies, **When** anonymity check runs, **Then** proxy anonymity level is detected (transparent/anonymous/elite)
5. **Given** validation level config, **When** set to "basic", **Then** only format + TCP validation runs (fast mode)
6. **Given** validation level config, **When** set to "full", **Then** all validation levels run (comprehensive mode)

---

### User Story 2 - Parallel Validation for Performance (Priority: P1)

A system needs to validate 1000+ proxies quickly using parallel validation to meet the <10 second validation requirement for large batches.

**Why this priority**: Performance critical - enables fast proxy validation at scale without blocking operations.

**Independent Test**: Can be tested by validating batches of varying sizes and measuring throughput.

**Acceptance Scenarios**:

1. **Given** 1000 proxies to validate, **When** parallel validation runs with 50 workers, **Then** validation completes in <10 seconds
2. **Given** validation concurrency config, **When** set to 100, **Then** up to 100 proxies are validated simultaneously
3. **Given** parallel validation, **When** some proxies timeout, **Then** other validations continue unaffected
4. **Given** validation results, **When** complete, **Then** success rate and timing stats are reported

---

### User Story 3 - File Persistence (JSON) (Priority: P1)

A user wants to persist fetched proxies to disk (JSON format) so they survive restarts and can be shared across instances.

**Why this priority**: Basic persistence - enables proxy state preservation and reduces re-fetching overhead.

**Independent Test**: Can be tested by saving proxies, restarting system, and loading from disk.

**Acceptance Scenarios**:

1. **Given** proxy pool with proxies, **When** `save_to_file("proxies.json")` is called, **Then** all proxies are written to JSON file atomically
2. **Given** JSON file exists, **When** `load_from_file("proxies.json")` is called, **Then** proxies are loaded into pool
3. **Given** proxies with credentials, **When** saved to file, **Then** credentials are encrypted (never plain text)
4. **Given** concurrent save operations, **When** multiple processes save, **Then** atomic writes prevent corruption
5. **Given** invalid JSON file, **When** load is attempted, **Then** clear error is raised with recovery suggestions

---

### User Story 4 - SQLite Storage Backend (Priority: P2)

An enterprise user needs SQLite storage for transactional proxy management, queryable history, and advanced filtering capabilities.

**Why this priority**: Advanced persistence - enables complex queries, history tracking, and multi-process access.

**Independent Test**: Can be tested by performing CRUD operations and verifying database state.

**Acceptance Scenarios**:

1. **Given** SQLite backend configured, **When** proxies are added, **Then** they are inserted into database with full metadata
2. **Given** database with proxies, **When** queried by source, **Then** filtered results are returned efficiently
3. **Given** proxy health changes, **When** updated in pool, **Then** database is updated transactionally
4. **Given** multiple processes, **When** accessing database, **Then** proper locking prevents conflicts
5. **Given** database schema, **When** migrations needed, **Then** automatic schema migration occurs safely

---

### User Story 5 - Continuous Health Monitoring (Priority: P2)

Operations team needs background health monitoring that continuously validates proxies without blocking requests, automatically removing failed proxies.

**Why this priority**: Automated quality control - maintains pool health without manual intervention.

**Independent Test**: Can be tested by starting monitoring, introducing proxy failures, and verifying automatic eviction.

**Acceptance Scenarios**:

1. **Given** health monitoring enabled, **When** background checker runs, **Then** all proxies are validated every N minutes (configurable)
2. **Given** proxy fails health check, **When** failure threshold reached (e.g., 3 consecutive), **Then** proxy is auto-removed from pool
3. **Given** monitoring interval config, **When** set to 5 minutes, **Then** health checks run every 5 minutes
4. **Given** monitoring running, **When** new proxy is added, **Then** it is included in next health check cycle
5. **Given** monitoring stats, **When** accessed via API, **Then** check history and failure reasons are available

---

### User Story 6 - JavaScript Rendering Support (Priority: P3)

A user needs to fetch proxies from websites that require JavaScript execution (e.g., Cloudflare-protected sites) using Playwright for browser automation.

**Why this priority**: Advanced fetching - enables access to JS-protected proxy sources that plain HTTP can't reach.

**Independent Test**: Can be tested by fetching from a JS-required site and verifying proxy extraction.

**Acceptance Scenarios**:

1. **Given** proxy source requires JS, **When** fetch with `render_mode="browser"`, **Then** Playwright renders page and extracts proxies
2. **Given** browser rendering, **When** page loads, **Then** waits for dynamic content to load before extraction
3. **Given** headless browser config, **When** rendering, **Then** browser runs in headless mode (no GUI)
4. **Given** rendering timeout, **When** page takes too long, **Then** timeout error is raised with partial results
5. **Given** rendering failures, **When** browser can't start, **Then** graceful fallback to non-JS fetch (if possible)

---

### User Story 7 - TTL-Based Cache Expiration (Priority: P3)

A user wants cached proxies to automatically expire after a configurable TTL (Time To Live) to ensure only fresh proxies are used.

**Why this priority**: Quality maintenance - prevents stale proxy usage over time.

**Independent Test**: Can be tested by setting short TTL and verifying auto-expiration.

**Acceptance Scenarios**:

1. **Given** proxies cached with 1-hour TTL, **When** 1 hour elapses, **Then** proxies are marked as expired
2. **Given** expired proxy accessed, **When** requested, **Then** proxy is re-validated before use
3. **Given** TTL config updated, **When** reload, **Then** new TTL applies to future proxies
4. **Given** storage backend, **When** saving, **Then** TTL timestamps are persisted correctly

---

## Functional Requirements

### FR-001: Validation Levels
- Support `BASIC` (format + TCP), `STANDARD` (+ HTTP), `FULL` (+ anonymity) validation levels
- Configurable via `ValidationLevel` enum
- Default: STANDARD

### FR-002: Validation Performance
- Parallel validation with configurable concurrency (default: 50 workers)
- Target: 100+ proxies/second for STANDARD validation
- Timeout per proxy: 5 seconds (configurable)

### FR-003: File Storage
- JSON format with atomic writes (write to temp, rename)
- Automatic credential encryption using cryptography.fernet
- Pretty-printed JSON for human readability
- File locking for concurrent access prevention

### FR-004: SQLite Storage
- Schema: proxies table (url, source, health, stats, created_at, updated_at)
- Indexes on: url (unique), source, health_status
- Automatic migrations using Alembic or custom migration system
- WAL mode for better concurrency

### FR-005: Health Monitoring
- Background thread/task for continuous monitoring
- Configurable check interval (default: 5 minutes)
- Configurable failure threshold (default: 3 consecutive failures)
- Graceful shutdown and resource cleanup

### FR-006: Browser Rendering
- Playwright integration for JS-required sites
- Headless mode by default
- Configurable wait strategies (network idle, DOM ready)
- Optional: Stealth mode to avoid detection

### FR-007: Cache Expiration
- Per-proxy TTL tracking
- Lazy expiration (check on access)
- Optional: Active expiration (background cleanup)
- TTL inheritance from source config

---

## Non-Functional Requirements

### NFR-001: Performance
- Validation: 100+ proxies/second (STANDARD level)
- File save: <500ms for 1000 proxies
- SQLite query: <50ms for filtered queries
- Health monitoring: <5% CPU overhead

### NFR-002: Reliability
- Atomic file writes (no corruption on crash)
- Database transactions (ACID guarantees)
- Graceful degradation (continue on partial failures)
- Error recovery (retry, fallback)

### NFR-003: Security
- Credentials encrypted at rest (never plain text)
- Secure key management (environment variable, key file)
- No credentials in logs or error messages (continued from US7)

### NFR-004: Scalability
- Support 10,000+ proxies in pool
- Efficient queries for large datasets
- Memory-efficient validation (streaming, batching)

### NFR-005: Maintainability
- Clear error messages with troubleshooting hints
- Comprehensive logging (validation results, storage ops)
- Type-safe APIs (mypy --strict compliance)
- Well-documented configuration options

---

## Technical Architecture

### Components

1. **ProxyValidator** (already implemented in US5)
   - Enhance with multi-level validation
   - Add parallel validation support
   - Add anonymity detection

2. **FileStorage** (new)
   - JSON serialization/deserialization
   - Atomic writes with temp files
   - Credential encryption/decryption
   - File locking

3. **SQLiteStorage** (new)
   - SQLAlchemy models
   - Query builder methods
   - Migration system
   - Connection pooling

4. **HealthMonitor** (new)
   - Background thread/asyncio task
   - Validation scheduler
   - Failure tracking
   - Auto-eviction logic

5. **BrowserRenderer** (new)
   - Playwright wrapper
   - Page rendering
   - Wait strategies
   - Content extraction

### Data Models

```python
class ValidationLevel(str, Enum):
    BASIC = "basic"      # Format + TCP
    STANDARD = "standard"  # + HTTP
    FULL = "full"        # + Anonymity

class StorageBackend(Protocol):
    def save(self, proxies: list[Proxy]) -> None: ...
    def load(self) -> list[Proxy]: ...
    def query(self, **filters: Any) -> list[Proxy]: ...
    def delete(self, proxy_url: str) -> None: ...

class HealthCheckResult(BaseModel):
    proxy_url: str
    timestamp: datetime
    success: bool
    response_time_ms: Optional[int]
    error: Optional[str]
```

---

## API Contracts

### Validation API

```python
from proxywhirl import ProxyValidator, ValidationLevel

validator = ProxyValidator(
    level=ValidationLevel.FULL,
    concurrency=50,
    timeout=5.0
)

# Validate single proxy
result = await validator.validate("http://proxy.example.com:8080")

# Validate batch
proxies = [...]
results = await validator.validate_batch(proxies)  # Returns list[ValidationResult]

# Check anonymity
level = await validator.check_anonymity("http://proxy.example.com:8080")
# Returns: "transparent", "anonymous", or "elite"
```

### Storage API

```python
from proxywhirl import FileStorage, SQLiteStorage

# File storage
storage = FileStorage(filepath="proxies.json", encryption_key="...")
storage.save(rotator.pool.proxies)
proxies = storage.load()

# SQLite storage
storage = SQLiteStorage(db_path="proxies.db")
storage.save(rotator.pool.proxies)
proxies = storage.query(source="FETCHED", health_status="HEALTHY")
storage.delete("http://dead-proxy.com:8080")
```

### Health Monitoring API

```python
from proxywhirl import HealthMonitor

monitor = HealthMonitor(
    pool=rotator.pool,
    interval=300,  # 5 minutes
    failure_threshold=3
)

# Start monitoring
await monitor.start()

# Get status
status = monitor.get_status()
# Returns: {last_check: datetime, next_check: datetime, failures: dict}

# Stop monitoring
await monitor.stop()
```

### Browser Rendering API

```python
from proxywhirl import ProxyFetcher, RenderMode

fetcher = ProxyFetcher(
    sources=[source],
    render_mode=RenderMode.BROWSER,  # Use Playwright
    wait_for="networkidle",  # Wait strategy
    timeout=30.0
)

proxies = await fetcher.fetch_all()
```

---

## Testing Strategy

### Unit Tests
- Validation logic (each level independently)
- Storage operations (save/load/query)
- Encryption/decryption
- Health check scheduler
- Browser rendering mocks

### Integration Tests
- End-to-end validation workflow
- Storage persistence across restarts
- Health monitoring with real proxies
- Browser rendering with live sites (if available)

### Performance Tests
- Validation throughput (100+ proxies/sec)
- Storage I/O benchmarks
- Concurrent access tests
- Memory profiling

### Property-Based Tests
- Storage round-trip (save + load = original)
- Validation consistency (same proxy, same result)
- Health monitoring invariants

---

## Implementation Plan

### Phase 2.1 - Multi-Level Validation (Week 1)
- [ ] Enhance ProxyValidator with ValidationLevel support
- [ ] Implement TCP connectivity check
- [ ] Implement HTTP request check
- [ ] Implement anonymity detection
- [ ] Add parallel validation with asyncio
- [ ] Add validation benchmarks

### Phase 2.2 - File Storage (Week 2)
- [ ] Implement FileStorage class
- [ ] Add JSON serialization with atomic writes
- [ ] Implement credential encryption
- [ ] Add file locking mechanism
- [ ] Add error handling and recovery
- [ ] Write comprehensive tests

### Phase 2.3 - SQLite Storage (Week 3)
- [ ] Define SQLite schema
- [ ] Implement SQLiteStorage class with SQLAlchemy
- [ ] Add query builder methods
- [ ] Implement migration system
- [ ] Add connection pooling
- [ ] Performance optimization

### Phase 2.4 - Health Monitoring (Week 4)
- [ ] Implement HealthMonitor class
- [ ] Add background thread scheduler
- [ ] Implement failure tracking
- [ ] Add auto-eviction logic
- [ ] Add monitoring API
- [ ] Integration tests

### Phase 2.5 - Browser Rendering (Week 5)
- [ ] Integrate Playwright
- [ ] Implement page rendering
- [ ] Add wait strategies
- [ ] Error handling and retries
- [ ] Optional: Stealth mode
- [ ] Documentation

---

## Success Metrics

- **Validation Performance**: 100+ proxies/second (STANDARD level)
- **Storage Reliability**: 0 data corruption incidents
- **Health Monitoring**: <5% CPU overhead
- **Test Coverage**: 85%+ overall
- **Quality Gates**: mypy --strict, ruff passing
- **Documentation**: All APIs documented with examples

---

## Dependencies

### New Python Packages
- `playwright>=1.40.0` - Browser automation (optional)
- `sqlalchemy>=2.0.0` - Database ORM (optional)
- `alembic>=1.12.0` - Database migrations (optional)

### Existing Packages (already in use)
- `httpx` - HTTP validation
- `pydantic` - Data validation
- `cryptography` - Credential encryption
- `loguru` - Logging

---

## Configuration

```python
from proxywhirl import ProxyRotator, ValidationLevel, FileStorage

rotator = ProxyRotator(
    validation_level=ValidationLevel.FULL,
    validation_concurrency=50,
    storage=FileStorage(
        filepath="proxies.json",
        encryption_key=os.environ["PROXY_ENCRYPTION_KEY"]
    ),
    health_monitoring=True,
    health_check_interval=300,  # 5 minutes
    failure_threshold=3
)
```

---

## Future Enhancements (Phase 3+)

- Redis caching backend
- Distributed storage (multi-node)
- Real-time health monitoring dashboard
- Advanced anonymity verification (DNS leaks, WebRTC)
- Proxy scoring/ranking system
- Automatic source discovery

---

## References

- US5: Proxy Fetching (basic validation implemented)
- US6: Mixed Sources (source tagging)
- US7: Advanced Error Handling (error metadata)
- Feature 005: Caching Mechanisms (original storage spec)
- Feature 006: Health Monitoring (original monitoring spec)
