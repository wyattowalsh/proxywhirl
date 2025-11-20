# Implementation Plan: Phase 2 - Validation & Storage

**Feature**: 019-phase2-validation-storage  
**Created**: 2025-10-22  
**Target Release**: v0.2.0  
**Dependencies**: Feature 001 (Core Package) - COMPLETE

## Overview

Phase 2 enhances proxywhirl with production-grade validation, persistent storage, and continuous health monitoring. Building on Phase 1's core rotation and fetching capabilities, Phase 2 enables reliable, long-running proxy management with automated quality control.

## Goals

1. **Multi-Level Validation**: Format, TCP, HTTP, and anonymity validation with configurable levels
2. **Persistent Storage**: File (JSON) and database (SQLite) backends with encryption
3. **Continuous Monitoring**: Background health checks with automatic proxy eviction
4. **Browser Rendering**: JavaScript-enabled fetching for protected proxy sources
5. **Cache Expiration**: TTL-based automatic proxy expiration

## Architecture Decisions

### 1. Validation Strategy

**Decision**: Implement progressive validation levels (BASIC → STANDARD → FULL)

**Rationale**:
- Flexibility: Users choose speed vs. thoroughness
- Performance: Basic validation is fast (<100ms), full validation more comprehensive
- Incremental: Can validate in stages, fail fast on format errors

**Alternatives Considered**:
- All-or-nothing validation: Too rigid, no performance tuning
- Always full validation: Too slow for large batches

### 2. Storage Abstraction

**Decision**: Protocol-based storage interface with File and SQLite implementations

**Rationale**:
- Extensibility: Easy to add Redis, PostgreSQL later
- Testability: Mock storage in tests
- Simplicity: Users pick backend based on needs (File for simple, SQLite for advanced)

**Interface**:
```python
class StorageBackend(Protocol):
    def save(self, proxies: list[Proxy]) -> None: ...
    def load(self) -> list[Proxy]: ...
    def query(self, **filters: Any) -> list[Proxy]: ...
    def delete(self, proxy_url: str) -> None: ...
```

### 3. Health Monitoring

**Decision**: Background asyncio task with configurable intervals

**Rationale**:
- Non-blocking: Doesn't impact request performance
- Async-friendly: Integrates well with async APIs
- Configurable: Interval and failure threshold tunable

**Alternatives Considered**:
- Threading: More complex lifecycle management
- On-demand validation: Doesn't catch failures proactively

### 4. Browser Rendering

**Decision**: Optional Playwright integration (not required for basic usage)

**Rationale**:
- Heavy dependency: Only needed for JS-protected sources
- Flexibility: Users without Playwright can still use other sources
- Clean separation: Rendering is isolated feature

### 5. Encryption

**Decision**: Fernet symmetric encryption for credentials at rest

**Rationale**:
- Simple: Easy to use, well-documented
- Secure: AES-128 with authentication
- Standard: Part of cryptography library (already a dependency)

## Component Design

### 1. ProxyValidator Enhancement

**Current State** (from US5):
- Basic validation exists in ProxyValidator
- Format validation implemented
- Single-threaded validation

**Enhancements**:
```python
class ProxyValidator:
    def __init__(
        self,
        level: ValidationLevel = ValidationLevel.STANDARD,
        concurrency: int = 50,
        timeout: float = 5.0
    ): ...
    
    async def validate(self, proxy_url: str) -> ValidationResult: ...
    async def validate_batch(self, proxies: list[str]) -> list[ValidationResult]: ...
    async def check_anonymity(self, proxy_url: str) -> str: ...  # New
```

**Validation Levels**:
- `BASIC`: Format + TCP (fast, ~100ms)
- `STANDARD`: BASIC + HTTP request (medium, ~500ms)
- `FULL`: STANDARD + Anonymity check (slow, ~2s)

### 2. FileStorage

**New Component**:
```python
class FileStorage:
    def __init__(
        self,
        filepath: str,
        encryption_key: Optional[str] = None,
        pretty: bool = True
    ): ...
    
    def save(self, proxies: list[Proxy]) -> None:
        # Atomic write: temp file + rename
        # Encrypt credentials if key provided
        ...
    
    def load(self) -> list[Proxy]:
        # Load from JSON, decrypt credentials
        ...
```

**Features**:
- Atomic writes (write to `.tmp`, rename)
- Credential encryption (Fernet)
- Pretty JSON (human-readable)
- File locking (prevent concurrent corruption)

### 3. SQLiteStorage

**New Component**:
```python
class SQLiteStorage:
    def __init__(
        self,
        db_path: str,
        encryption_key: Optional[str] = None
    ): ...
    
    def save(self, proxies: list[Proxy]) -> None: ...
    def load(self) -> list[Proxy]: ...
    def query(self, **filters: Any) -> list[Proxy]: ...
    def delete(self, proxy_url: str) -> None: ...
```

**Schema**:
```sql
CREATE TABLE proxies (
    url TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    health_status TEXT NOT NULL,
    username TEXT,  -- Encrypted
    password TEXT,  -- Encrypted
    total_requests INTEGER DEFAULT 0,
    total_successes INTEGER DEFAULT 0,
    total_failures INTEGER DEFAULT 0,
    avg_response_time REAL,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_source ON proxies(source);
CREATE INDEX idx_health ON proxies(health_status);
```

### 4. HealthMonitor

**New Component**:
```python
class HealthMonitor:
    def __init__(
        self,
        pool: ProxyPool,
        interval: int = 300,  # 5 minutes
        failure_threshold: int = 3,
        validator: Optional[ProxyValidator] = None
    ): ...
    
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    def get_status(self) -> dict[str, Any]: ...
```

**Behavior**:
- Runs health checks on all proxies every `interval` seconds
- Tracks consecutive failures per proxy
- Auto-removes proxies exceeding `failure_threshold`
- Provides status API (last check, next check, failure counts)

### 5. BrowserRenderer

**New Component** (optional dependency):
```python
class BrowserRenderer:
    def __init__(
        self,
        headless: bool = True,
        timeout: float = 30.0,
        wait_for: str = "networkidle"
    ): ...
    
    async def render(self, url: str) -> str:
        # Returns rendered HTML
        ...
```

**Integration** with ProxyFetcher:
```python
fetcher = ProxyFetcher(
    sources=[source],
    render_mode=RenderMode.BROWSER,  # Uses BrowserRenderer
    browser_config={"headless": True, "timeout": 30}
)
```

## Data Flow

### Validation Flow
```
Raw Proxy URLs
    ↓
Format Validation (quick, fails fast)
    ↓
TCP Connectivity (parallel, 50 concurrent)
    ↓
HTTP Request Test (parallel, 50 concurrent)
    ↓
Anonymity Check (optional, parallel)
    ↓
ValidationResult (success/failure + metadata)
```

### Storage Flow
```
ProxyPool.proxies
    ↓
Storage.save()
    ↓
Serialize to JSON/SQL
    ↓
Encrypt credentials (if key provided)
    ↓
Write atomically (file) or transactionally (SQLite)
    ↓
Disk

Load path:
Disk
    ↓
Read JSON/SQL
    ↓
Decrypt credentials
    ↓
Deserialize to Proxy objects
    ↓
ProxyPool.proxies
```

### Health Monitoring Flow
```
Start Monitor
    ↓
Schedule Background Task (asyncio)
    ↓
Every {interval} seconds:
    ├── Get all proxies from pool
    ├── Validate each proxy (parallel)
    ├── Track failures per proxy
    ├── Remove proxies > failure_threshold
    └── Log results
```

## Testing Strategy

### Unit Tests
- `test_validation_levels.py` - Each validation level independently
- `test_file_storage.py` - Save/load/encryption
- `test_sqlite_storage.py` - CRUD operations
- `test_health_monitor.py` - Scheduler, failure tracking
- `test_browser_renderer.py` - Mocked Playwright

### Integration Tests
- `test_validation_workflow.py` - End-to-end validation
- `test_storage_persistence.py` - Save + restart + load
- `test_health_monitoring_integration.py` - Monitor with real proxies
- `test_mixed_storage.py` - Switch between File and SQLite

### Performance Tests
- `test_validation_performance.py` - 100+ proxies/sec benchmark
- `test_storage_performance.py` - Save/load 1000 proxies
- `test_concurrent_validation.py` - Parallel validation scaling

### Property-Based Tests
- Storage round-trip: `save(proxies) → load() == proxies`
- Validation consistency: Same proxy, same result
- Encryption: `decrypt(encrypt(data)) == data`

## Implementation Phases

### Phase 2.1 - Multi-Level Validation (Week 1)

**Tasks**:
1. Add `ValidationLevel` enum to models.py
2. Enhance ProxyValidator with level support
3. Implement TCP connectivity check
4. Implement HTTP request check
5. Implement anonymity detection
6. Add parallel validation with asyncio
7. Add validation benchmarks (target: 100+ proxies/sec)

**Deliverables**:
- Enhanced ProxyValidator class
- ValidationResult model with detailed metadata
- Validation benchmarks passing
- Tests: 20+ unit tests, 5+ integration tests

### Phase 2.2 - File Storage (Week 2)

**Tasks**:
1. Create FileStorage class with Protocol interface
2. Implement JSON serialization (Proxy → dict)
3. Add atomic write mechanism (temp file + rename)
4. Implement credential encryption (Fernet)
5. Add file locking (prevent concurrent writes)
6. Error handling and recovery (corrupted file, missing key)

**Deliverables**:
- FileStorage class with save/load methods
- Encryption utilities
- Tests: 15+ unit tests, 5+ integration tests

### Phase 2.3 - SQLite Storage (Week 3)

**Tasks**:
1. Define SQLite schema (proxies table)
2. Implement SQLiteStorage class with SQLAlchemy
3. Add query builder (filter by source, health, etc.)
4. Implement credential encryption for database
5. Add connection pooling and transactions
6. Performance optimization (indexes, batching)

**Deliverables**:
- SQLiteStorage class with full CRUD
- Migration system (schema versioning)
- Tests: 20+ unit tests, 5+ integration tests

### Phase 2.4 - Health Monitoring (Week 4)

**Tasks**:
1. Create HealthMonitor class
2. Implement background task scheduler (asyncio)
3. Add failure tracking per proxy
4. Implement auto-eviction logic
5. Add monitoring status API
6. Graceful shutdown and cleanup

**Deliverables**:
- HealthMonitor class with start/stop
- Status API (last check, failures, etc.)
- Tests: 15+ unit tests, 5+ integration tests

### Phase 2.5 - Browser Rendering (Week 5)

**Tasks**:
1. Add Playwright as optional dependency
2. Create BrowserRenderer class
3. Implement page rendering with wait strategies
4. Integrate with ProxyFetcher (RenderMode.BROWSER)
5. Error handling (browser crash, timeout)
6. Documentation and examples

**Deliverables**:
- BrowserRenderer class (optional)
- RenderMode enum enhancement
- Tests: 10+ unit tests (mocked), 3+ integration tests (if Playwright available)

## Dependencies

### New Dependencies
```toml
[project.optional-dependencies]
storage = [
    "sqlalchemy>=2.0.0",
    "alembic>=1.12.0",
]
browser = [
    "playwright>=1.40.0",
]
```

### Existing Dependencies
- httpx - HTTP validation
- pydantic - Data models
- cryptography - Already present (for encryption)
- loguru - Logging

## Configuration

### Environment Variables
```bash
PROXY_ENCRYPTION_KEY=<fernet-key>  # For credential encryption
PROXY_STORAGE_PATH=proxies.json    # File storage path
PROXY_DB_PATH=proxies.db           # SQLite path
PROXY_HEALTH_INTERVAL=300          # Health check interval (seconds)
PROXY_FAILURE_THRESHOLD=3          # Failures before eviction
```

### Code Configuration
```python
from proxywhirl import (
    ProxyRotator, 
    ValidationLevel, 
    FileStorage,
    HealthMonitor
)

rotator = ProxyRotator(
    validation_level=ValidationLevel.FULL,
    validation_concurrency=50,
    storage=FileStorage(
        filepath="proxies.json",
        encryption_key=os.environ.get("PROXY_ENCRYPTION_KEY")
    )
)

# Optional: Start health monitoring
monitor = HealthMonitor(
    pool=rotator.pool,
    interval=300,
    failure_threshold=3
)
await monitor.start()
```

## Success Criteria

- [ ] Validation: 100+ proxies/second (STANDARD level)
- [ ] Storage: 0 data corruption incidents in testing
- [ ] Health Monitoring: <5% CPU overhead
- [ ] Test Coverage: 85%+ overall
- [ ] Quality Gates: mypy --strict, ruff passing
- [ ] Documentation: All APIs documented with examples
- [ ] Performance: File save <500ms for 1000 proxies
- [ ] Performance: SQLite query <50ms for filtered queries

## Risk Mitigation

### Risk 1: Playwright Heavy Dependency
**Mitigation**: Make optional, provide clear docs on when needed

### Risk 2: Encryption Key Management
**Mitigation**: Support multiple key sources (env var, file, KMS), clear docs

### Risk 3: Database Corruption
**Mitigation**: WAL mode, backups, recovery procedures documented

### Risk 4: Health Monitoring Overhead
**Mitigation**: Configurable intervals, ability to disable, profiling

## Future Enhancements (Phase 3+)

- Redis caching backend
- PostgreSQL storage
- Real-time monitoring dashboard
- Advanced anonymity checks (DNS leaks, WebRTC)
- Proxy scoring and ranking
- Distributed health monitoring
