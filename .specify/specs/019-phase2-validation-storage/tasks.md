# Implementation Tasks: Phase 2 - Validation & Storage

**Feature**: 019-phase2-validation-storage  
**Target**: v0.2.0  
**Status**: Not Started  
**Test-First**: YES (All tests written BEFORE implementation)

## Task Overview

Total Tasks: ~85 tasks across 5 sub-features
Estimated Duration: 5 weeks
Current Progress: 0/85 complete

## Phase 2.1: Multi-Level Validation (T001-T020)

### T001-T005: Validation Level Support
- [ ] T001: Add `ValidationLevel` enum to models.py (BASIC, STANDARD, FULL)
- [ ] T002: Update ProxyValidator.__init__ to accept `level` parameter
- [ ] T003: Write unit test: test_validation_level_basic
- [ ] T004: Write unit test: test_validation_level_standard
- [ ] T005: Write unit test: test_validation_level_full

### T006-T010: TCP Connectivity Validation
- [ ] T006: Write unit test: test_tcp_connect_success
- [ ] T007: Write unit test: test_tcp_connect_timeout
- [ ] T008: Write unit test: test_tcp_connect_refused
- [ ] T009: Implement _validate_tcp_connectivity() method
- [ ] T010: Run tests T006-T008 (verify all pass)

### T011-T015: HTTP Request Validation
- [ ] T011: Write unit test: test_http_request_success
- [ ] T012: Write unit test: test_http_request_timeout
- [ ] T013: Write unit test: test_http_request_invalid_response
- [ ] T014: Implement _validate_http_request() method
- [ ] T015: Run tests T011-T013 (verify all pass)

### T016-T020: Anonymity Detection
- [ ] T016: Write unit test: test_anonymity_transparent
- [ ] T017: Write unit test: test_anonymity_anonymous
- [ ] T018: Write unit test: test_anonymity_elite
- [ ] T019: Implement check_anonymity() method (check IP leakage)
- [ ] T020: Run tests T016-T018 (verify all pass)

### T021-T030: Parallel Validation
- [ ] T021: Write unit test: test_validate_batch_parallel
- [ ] T022: Write unit test: test_validate_batch_concurrency_limit
- [ ] T023: Write unit test: test_validate_batch_partial_failures
- [ ] T024: Write unit test: test_validate_batch_timeout_handling
- [ ] T025: Implement validate_batch() with asyncio.gather
- [ ] T026: Add concurrency semaphore (limit concurrent validations)
- [ ] T027: Run tests T021-T024 (verify all pass)
- [ ] T028: Write performance test: test_validation_performance_100_per_sec
- [ ] T029: Implement optimizations to meet 100+ proxies/sec target
- [ ] T030: Run performance test T028 (verify passes)

---

## Phase 2.2: File Storage (T031-T050)

### T031-T035: Storage Interface
- [ ] T031: Create StorageBackend Protocol in models.py
- [ ] T032: Write unit test: test_storage_protocol_compliance
- [ ] T033: Create FileStorage class skeleton
- [ ] T034: Write unit test: test_file_storage_init
- [ ] T035: Run test T034 (verify passes)

### T036-T045: Save/Load Operations
- [ ] T036: Write unit test: test_file_storage_save_empty_list
- [ ] T037: Write unit test: test_file_storage_save_multiple_proxies
- [ ] T038: Write unit test: test_file_storage_load_from_existing
- [ ] T039: Write unit test: test_file_storage_load_nonexistent_file
- [ ] T040: Write unit test: test_file_storage_save_and_load_roundtrip
- [ ] T041: Implement FileStorage.save() with JSON serialization
- [ ] T042: Implement atomic write (temp file + rename)
- [ ] T043: Implement FileStorage.load() with JSON deserialization
- [ ] T044: Add error handling (file not found, invalid JSON, etc.)
- [ ] T045: Run tests T036-T040 (verify all pass)

### T046-T050: Credential Encryption
- [ ] T046: Write unit test: test_encrypt_decrypt_credentials
- [ ] T047: Write unit test: test_save_with_encryption
- [ ] T048: Write unit test: test_load_with_decryption
- [ ] T049: Implement credential encryption/decryption (Fernet)
- [ ] T050: Run tests T046-T048 (verify all pass)

### T051-T055: File Locking & Concurrency
- [ ] T051: Write unit test: test_concurrent_save_operations
- [ ] T052: Write unit test: test_save_fails_if_locked
- [ ] T053: Implement file locking mechanism
- [ ] T054: Run tests T051-T052 (verify all pass)
- [ ] T055: Integration test: test_file_storage_persistence_across_restarts

---

## Phase 2.3: SQLite Storage (T056-T075)

### T056-T060: Database Schema
- [ ] T056: Define SQLite schema (proxies table)
- [ ] T057: Create SQLiteStorage class skeleton
- [ ] T058: Write unit test: test_sqlite_create_tables
- [ ] T059: Implement table creation in __init__
- [ ] T060: Run test T058 (verify passes)

### T061-T070: CRUD Operations
- [ ] T061: Write unit test: test_sqlite_save_single_proxy
- [ ] T062: Write unit test: test_sqlite_save_multiple_proxies
- [ ] T063: Write unit test: test_sqlite_load_all_proxies
- [ ] T064: Write unit test: test_sqlite_query_by_source
- [ ] T065: Write unit test: test_sqlite_query_by_health_status
- [ ] T066: Write unit test: test_sqlite_delete_proxy
- [ ] T067: Implement SQLiteStorage.save() with SQLAlchemy
- [ ] T068: Implement SQLiteStorage.load()
- [ ] T069: Implement SQLiteStorage.query(**filters)
- [ ] T070: Implement SQLiteStorage.delete(proxy_url)

### T071-T075: Performance & Reliability
- [ ] T071: Write unit test: test_sqlite_transaction_rollback
- [ ] T072: Write unit test: test_sqlite_concurrent_access
- [ ] T073: Add connection pooling and WAL mode
- [ ] T074: Add indexes (source, health_status)
- [ ] T075: Performance test: test_sqlite_query_speed_under_50ms

---

## Phase 2.4: Health Monitoring (T076-T090)

### T076-T080: Monitor Setup
- [ ] T076: Create HealthMonitor class skeleton
- [ ] T077: Write unit test: test_monitor_init_with_defaults
- [ ] T078: Write unit test: test_monitor_init_with_custom_config
- [ ] T079: Implement __init__ with configurable interval/threshold
- [ ] T080: Run tests T077-T078 (verify all pass)

### T081-T085: Background Task Scheduler
- [ ] T081: Write unit test: test_monitor_start_schedules_task
- [ ] T082: Write unit test: test_monitor_stop_cancels_task
- [ ] T083: Write unit test: test_monitor_checks_run_periodically
- [ ] T084: Implement start() with asyncio.create_task
- [ ] T085: Implement stop() with graceful task cancellation

### T086-T090: Failure Tracking & Eviction
- [ ] T086: Write unit test: test_monitor_tracks_consecutive_failures
- [ ] T087: Write unit test: test_monitor_evicts_after_threshold
- [ ] T088: Write unit test: test_monitor_resets_failures_on_success
- [ ] T089: Implement failure tracking per proxy
- [ ] T090: Implement auto-eviction logic

### T091-T095: Status API & Integration
- [ ] T091: Write unit test: test_monitor_get_status
- [ ] T092: Implement get_status() API
- [ ] T093: Integration test: test_monitor_with_real_proxies
- [ ] T094: Integration test: test_monitor_evicts_dead_proxies
- [ ] T095: Performance test: test_monitor_cpu_overhead_under_5_percent

---

## Phase 2.5: Browser Rendering (T096-T110)

### T096-T100: Browser Setup
- [ ] T096: Add Playwright to optional dependencies
- [ ] T097: Create BrowserRenderer class skeleton
- [ ] T098: Write unit test: test_browser_init_headless
- [ ] T099: Write unit test: test_browser_init_with_options
- [ ] T100: Implement __init__ with Playwright configuration

### T101-T105: Page Rendering
- [ ] T101: Write unit test: test_browser_render_simple_page (mocked)
- [ ] T102: Write unit test: test_browser_render_with_wait_strategy (mocked)
- [ ] T103: Write unit test: test_browser_render_timeout (mocked)
- [ ] T104: Implement render() method with Playwright
- [ ] T105: Add wait strategies (load, networkidle, domcontentloaded)

### T106-T110: Integration with ProxyFetcher
- [ ] T106: Add RenderMode.BROWSER to models.py
- [ ] T107: Write integration test: test_fetcher_with_browser_mode
- [ ] T108: Update ProxyFetcher to use BrowserRenderer when mode=BROWSER
- [ ] T109: Add error handling (browser crash, timeout)
- [ ] T110: Integration test: test_browser_fetching_from_js_site (if available)

---

## Phase 2.6: TTL Cache Expiration (T111-T120)

### T111-T115: TTL Tracking
- [ ] T111: Add `ttl` and `expires_at` fields to Proxy model
- [ ] T112: Write unit test: test_proxy_is_expired
- [ ] T113: Write unit test: test_proxy_not_expired
- [ ] T114: Implement is_expired() property on Proxy
- [ ] T115: Run tests T112-T113 (verify all pass)

### T116-T120: TTL Enforcement
- [ ] T116: Write unit test: test_pool_filters_expired_proxies
- [ ] T117: Write unit test: test_rotator_skips_expired_proxies
- [ ] T118: Update ProxyPool to filter expired proxies in get_healthy_proxies()
- [ ] T119: Update rotation strategies to skip expired proxies
- [ ] T120: Integration test: test_ttl_expiration_workflow

---

## Phase 2.7: Documentation & Polish (T121-T135)

### T121-T125: Code Documentation
- [ ] T121: Add docstrings to all new classes (ValidationLevel, FileStorage, etc.)
- [ ] T122: Add docstrings to all new methods
- [ ] T123: Add inline comments for complex logic
- [ ] T124: Update __init__.py exports for new classes
- [ ] T125: Update __all__ list with new exports

### T126-T130: User Documentation
- [ ] T126: Create examples/validation_example.py
- [ ] T127: Create examples/file_storage_example.py
- [ ] T128: Create examples/sqlite_storage_example.py
- [ ] T129: Create examples/health_monitoring_example.py
- [ ] T130: Create examples/browser_rendering_example.py

### T131-T135: Quality Gates & Release
- [ ] T131: Run full test suite (all 385+ tests)
- [ ] T132: Run mypy --strict proxywhirl/ (verify 0 errors)
- [ ] T133: Run ruff check proxywhirl/ (verify all passing)
- [ ] T134: Generate coverage report (verify 85%+ coverage)
- [ ] T135: Update README.md with Phase 2 features and examples

---

## Testing Checkpoints

### Checkpoint 1: After Phase 2.1 (Validation)
- Run: `uv run pytest tests/unit/test_validation*.py -v`
- Expected: 20+ tests passing
- Run: `uv run pytest tests/benchmarks/test_validation_performance.py`
- Expected: 100+ proxies/sec benchmark passing

### Checkpoint 2: After Phase 2.2 (File Storage)
- Run: `uv run pytest tests/unit/test_file_storage.py -v`
- Expected: 15+ tests passing
- Run: `uv run pytest tests/integration/test_storage_persistence.py`
- Expected: Round-trip persistence tests passing

### Checkpoint 3: After Phase 2.3 (SQLite Storage)
- Run: `uv run pytest tests/unit/test_sqlite_storage.py -v`
- Expected: 20+ tests passing
- Run: `uv run pytest tests/benchmarks/test_storage_performance.py`
- Expected: Query speed <50ms benchmark passing

### Checkpoint 4: After Phase 2.4 (Health Monitoring)
- Run: `uv run pytest tests/unit/test_health_monitor.py -v`
- Expected: 15+ tests passing
- Run: `uv run pytest tests/integration/test_health_monitoring.py`
- Expected: Auto-eviction integration tests passing

### Checkpoint 5: After Phase 2.5 (Browser Rendering)
- Run: `uv run pytest tests/unit/test_browser_renderer.py -v`
- Expected: 10+ tests passing (mocked)
- Run: `uv run pytest tests/integration/test_browser_fetching.py` (if Playwright available)
- Expected: Real browser tests passing (optional)

### Final Checkpoint: Phase 2 Complete
- Run: `uv run pytest tests/ -q`
- Expected: 385+ tests passing (300 from Phase 1 + 85 from Phase 2)
- Run: `uv run pytest tests/ --cov=proxywhirl`
- Expected: 85%+ coverage
- Run quality gates: mypy, ruff
- Expected: All passing

---

## Dependencies

### New Required Dependencies
```toml
# Already in pyproject.toml (for Phase 1):
# - httpx
# - pydantic
# - cryptography
# - loguru

# No new required dependencies
```

### New Optional Dependencies
```toml
[project.optional-dependencies]
storage = [
    "sqlalchemy>=2.0.0",
]
browser = [
    "playwright>=1.40.0",
]
```

---

## Success Criteria

- [ ] All 85 Phase 2 tasks complete
- [ ] All 385+ tests passing (100%)
- [ ] Coverage maintained at 85%+
- [ ] mypy --strict: 0 errors
- [ ] ruff: all checks passing
- [ ] Performance benchmarks passing:
  - Validation: 100+ proxies/sec
  - File save: <500ms for 1000 proxies
  - SQLite query: <50ms
  - Health monitoring: <5% CPU
- [ ] Documentation complete:
  - All classes/methods documented
  - 5+ working examples
  - README updated
- [ ] Constitution compliance maintained

---

## Notes

- **Test-First**: All tests must be written BEFORE implementation
- **Quality Gates**: mypy and ruff must pass after each checkpoint
- **Performance**: Run benchmarks after each performance-critical feature
- **Documentation**: Update docs as features are completed, not at the end
- **Constitution**: Follow all 7 principles from `.specify/memory/constitution.md`

---

## Timeline Estimate

- Week 1 (T001-T030): Multi-Level Validation - 20 hours
- Week 2 (T031-T055): File Storage - 20 hours
- Week 3 (T056-T075): SQLite Storage - 20 hours
- Week 4 (T076-T095): Health Monitoring - 16 hours
- Week 5 (T096-T135): Browser Rendering + Documentation - 24 hours

**Total**: ~100 hours (5 weeks @ 20 hours/week)
