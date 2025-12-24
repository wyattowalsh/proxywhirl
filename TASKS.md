# ProxyWhirl Task List

> Comprehensive task list for fixing, enhancing, and refactoring proxywhirl.
> Generated from comprehensive audit on 2025-12-24.
> Optimized for Claude Code subagents.

---

## Priority Levels

| Priority | Description | SLA |
|----------|-------------|-----|
| **P0** | Critical - Package broken, cannot import | Immediate |
| **P1** | High - Security issues, major bugs | 1-2 days |
| **P2** | Medium - Code quality, linting | 1 week |
| **P3** | Low - Enhancements, documentation | 2 weeks |

---

## P0: Critical Fixes (Package Broken)

### TASK-001: Fix broken `__init__.py` imports
**Priority:** P0 - CRITICAL
**Type:** Bug Fix
**File:** `proxywhirl/__init__.py`
**Problem:** Package cannot be imported due to 11 missing module references
**Impact:** 100% of users affected - library completely unusable

**Missing modules to remove from imports:**
```
- proxywhirl.analytics_engine (line 8)
- proxywhirl.analytics_models (lines 9-26)
- proxywhirl.cost_analyzer (line 39)
- proxywhirl.failure_analyzer (line 40)
- proxywhirl.pattern_detector (line 41)
- proxywhirl.performance_analyzer (line 42)
- proxywhirl.predictive_analytics (line 43)
- proxywhirl.export_manager (line 64)
- proxywhirl.export_models (lines 65-86)
- proxywhirl.health (line 97)
- proxywhirl.health_models (lines 98-106)
```

**Steps:**
1. Read `proxywhirl/__init__.py`
2. Remove all imports from non-existent modules listed above
3. Remove corresponding entries from `__all__` list (lines 186-210, 218-227, 287-308)
4. Fix duplicate `ExportFormat` import (line 71 duplicates line 16)
5. Run `python -c "import proxywhirl"` to verify fix
6. Run `uv run -- ruff check proxywhirl/__init__.py` to verify no errors

**Acceptance Criteria:**
- [ ] `import proxywhirl` succeeds without errors
- [ ] No `ModuleNotFoundError` exceptions
- [ ] Ruff reports 0 errors for `__init__.py`

---

## P1: Security & High-Priority Fixes

### TASK-002: Restrict default CORS origins
**Priority:** P1
**Type:** Security
**File:** `proxywhirl/api.py`
**Lines:** 189-196

**Problem:** Default CORS allows all origins (`*`)
```python
cors_origins = os.getenv("PROXYWHIRL_CORS_ORIGINS", "*").split(",")
```

**Fix:**
1. Change default to empty list or localhost only
2. Log warning when `*` is used
3. Add documentation about CORS configuration

**Acceptance Criteria:**
- [ ] Default CORS is restrictive (not `*`)
- [ ] Warning logged when wildcard CORS used
- [ ] Documentation updated in README

---

### TASK-003: Fix mutable default argument issues (B008)
**Priority:** P1
**Type:** Bug Prevention
**Files:** Multiple (23 instances)

**Problem:** Function calls in default arguments can cause unexpected behavior

**Steps:**
1. Run `uv run -- ruff check proxywhirl/ --select B008`
2. For each violation, refactor to use `None` default with factory pattern:
   ```python
   # Before
   def func(items: list = []):

   # After
   def func(items: list | None = None):
       if items is None:
           items = []
   ```
3. Verify no regressions with tests

**Acceptance Criteria:**
- [ ] `ruff check --select B008` returns 0 errors
- [ ] All tests pass

---

### TASK-004: Add input validation to API endpoints
**Priority:** P1
**Type:** Security
**File:** `proxywhirl/api.py`

**Problem:** Some API endpoints lack proper input validation

**Endpoints to review:**
- `POST /api/v1/request` - validate URL scheme
- `POST /api/v1/proxies` - validate proxy URL format
- `PUT /api/v1/config` - validate configuration values

**Steps:**
1. Add URL scheme validation (http/https/socks4/socks5 only)
2. Add port range validation (1-65535)
3. Add string length limits to prevent DoS
4. Return proper 400 errors with helpful messages

**Acceptance Criteria:**
- [ ] Invalid URLs return 400 with clear error message
- [ ] Invalid ports return 400
- [ ] Oversized inputs rejected

---

## P2: Linting & Code Quality

### TASK-005: Fix unused imports (F401)
**Priority:** P2
**Type:** Code Quality
**Files:** Multiple (14 instances)

**Steps:**
1. Run `uv run -- ruff check proxywhirl/ --select F401`
2. Remove each unused import
3. Verify no functionality broken

**Acceptance Criteria:**
- [ ] `ruff check --select F401` returns 0 errors

---

### TASK-006: Fix undefined names (F821)
**Priority:** P2
**Type:** Bug Fix
**Files:** Multiple (7 instances)

**Steps:**
1. Run `uv run -- ruff check proxywhirl/ --select F821`
2. For each undefined name:
   - Add missing import, OR
   - Fix typo in name, OR
   - Remove dead code referencing it
3. Test affected functionality

**Acceptance Criteria:**
- [ ] `ruff check --select F821` returns 0 errors
- [ ] No runtime `NameError` exceptions

---

### TASK-007: Fix whitespace issues (W293)
**Priority:** P2
**Type:** Code Style
**Files:** Multiple (49 instances)

**Steps:**
1. Run `uv run -- ruff check proxywhirl/ --select W293 --fix`
2. Verify changes look correct
3. Commit with message "style: Remove trailing whitespace"

**Acceptance Criteria:**
- [ ] `ruff check --select W293` returns 0 errors

---

### TASK-008: Fix deprecated annotations (UP006, UP035, UP045)
**Priority:** P2
**Type:** Code Modernization
**Files:** Multiple (39 instances total)

**Steps:**
1. Run `uv run -- ruff check proxywhirl/ --select UP006,UP035,UP045 --fix`
2. Replace `List[X]` with `list[X]`
3. Replace `Optional[X]` with `X | None`
4. Update imports from `typing` to use built-in types

**Acceptance Criteria:**
- [ ] `ruff check --select UP` returns 0 errors
- [ ] Code uses modern Python 3.9+ type syntax

---

### TASK-009: Organize imports (I001)
**Priority:** P2
**Type:** Code Style
**File:** `proxywhirl/__init__.py`

**Steps:**
1. Run `uv run -- ruff check proxywhirl/__init__.py --select I001 --fix`
2. Verify import order is correct (stdlib, third-party, local)

**Acceptance Criteria:**
- [ ] `ruff check --select I001` returns 0 errors

---

### TASK-010: Fix unused variables (F841)
**Priority:** P2
**Type:** Code Quality
**Files:** Multiple (2 instances)

**Steps:**
1. Run `uv run -- ruff check proxywhirl/ --select F841`
2. Remove or use each unused variable
3. Prefix intentionally unused with `_`

**Acceptance Criteria:**
- [ ] `ruff check --select F841` returns 0 errors

---

## P2: Implement Missing Modules (Choose One Path)

> **Decision Required:** Either implement the missing modules OR remove references.
> Path A is faster, Path B adds planned functionality.

### TASK-011A: Remove missing module references (Fast Path)
**Priority:** P2
**Type:** Cleanup
**Estimated Time:** 1 hour

**Modules to NOT implement (remove all references):**
- `analytics_engine`, `analytics_models`
- `health`, `health_models`
- `export_manager`, `export_models`
- `cost_analyzer`, `failure_analyzer`
- `pattern_detector`, `performance_analyzer`
- `predictive_analytics`

**Steps:**
1. Complete TASK-001 first
2. Search codebase for any remaining references
3. Remove from `api.py` (export endpoints lines 1009-1289)
4. Update README to remove references to unimplemented features
5. Update version to indicate breaking change if needed

---

### TASK-011B: Implement analytics_engine module
**Priority:** P2
**Type:** New Feature
**Spec:** `specs/009-analytics-engine-analysis/spec.md`
**Estimated Time:** 2-3 days

**Steps:**
1. Read spec at `specs/009-analytics-engine-analysis/spec.md`
2. Read data model at `specs/009-analytics-engine-analysis/data-model.md`
3. Create `proxywhirl/analytics_engine.py`
4. Create `proxywhirl/analytics_models.py`
5. Implement classes referenced in `__init__.py`:
   - `AnalyticsEngine`
   - `AnalysisConfig`, `AnalysisReport`, `AnalysisType`
   - `AnalyticsQuery`, `ProxyPerformanceMetrics`
   - `PerformanceScore`, `UsagePattern`, `FailureCluster`
   - `Prediction`, `Recommendation`, `RecommendationPriority`
   - `Anomaly`, `AnomalyType`, `TimeSeriesData`, `TrendDirection`
6. Write unit tests
7. Verify import works

---

### TASK-011C: Implement health monitoring module
**Priority:** P2
**Type:** New Feature
**Spec:** `specs/006-health-monitoring-continuous/spec.md`
**Estimated Time:** 1-2 days

**Steps:**
1. Read spec at `specs/006-health-monitoring-continuous/spec.md`
2. Create `proxywhirl/health.py`
3. Create `proxywhirl/health_models.py`
4. Implement classes:
   - `HealthChecker`
   - `HealthCheckConfig`, `HealthCheckResult`
   - `HealthEvent`, `PoolStatus`, `SourceStatus`
   - `ProxyHealthState`
5. Write unit tests

---

### TASK-011D: Implement export module
**Priority:** P2
**Type:** New Feature
**Spec:** `specs/011-data-export/spec.md`
**Estimated Time:** 2-3 days

**Steps:**
1. Read spec at `specs/011-data-export/spec.md`
2. Create `proxywhirl/export_manager.py`
3. Create `proxywhirl/export_models.py`
4. Implement classes referenced in `__init__.py`
5. Wire up API endpoints in `api.py` (already stubbed)
6. Write unit tests

---

## P2: Test Fixes

### TASK-012: Fix test imports after TASK-001
**Priority:** P2
**Type:** Test Fix
**Files:** `tests/**/*.py`

**Problem:** Tests fail to import due to broken `__init__.py`

**Steps:**
1. Complete TASK-001 first
2. Run `uv run -- pytest --co -q` to collect tests
3. Fix any remaining import errors in test files
4. Verify all tests can be collected

**Acceptance Criteria:**
- [ ] `pytest --co` succeeds without errors
- [ ] All 93 test files can be imported

---

### TASK-013: Run full test suite and fix failures
**Priority:** P2
**Type:** Test Fix
**Files:** `tests/**/*.py`

**Steps:**
1. Complete TASK-012 first
2. Run `uv run -- pytest -x` to find first failure
3. Fix each failing test
4. Run full suite `uv run -- pytest`
5. Ensure >80% coverage maintained

**Acceptance Criteria:**
- [ ] All tests pass
- [ ] Coverage >= 80%

---

## P2: Type Checking

### TASK-014: Fix mypy strict mode errors
**Priority:** P2
**Type:** Type Safety
**Files:** `proxywhirl/**/*.py`

**Steps:**
1. Run `uv run -- mypy proxywhirl/`
2. Fix each type error:
   - Add missing type annotations
   - Fix incompatible types
   - Add proper Optional handling
3. Ensure mypy passes in strict mode

**Acceptance Criteria:**
- [ ] `mypy proxywhirl/` returns 0 errors
- [ ] All functions have type annotations

---

## P3: Documentation & Enhancements

### TASK-015: Update README for current state
**Priority:** P3
**Type:** Documentation
**File:** `README.md`

**Steps:**
1. Remove references to unimplemented features
2. Update installation instructions
3. Verify all code examples work
4. Update feature status table
5. Add troubleshooting section

**Acceptance Criteria:**
- [ ] All code examples in README are runnable
- [ ] No references to missing features

---

### TASK-016: Add CONTRIBUTING.md
**Priority:** P3
**Type:** Documentation
**File:** `CONTRIBUTING.md`

**Steps:**
1. Create contributing guide with:
   - Development setup instructions
   - Code style guidelines
   - Testing requirements
   - PR process

---

### TASK-017: Add pre-commit hooks
**Priority:** P3
**Type:** DX Enhancement
**File:** `.pre-commit-config.yaml`

**Steps:**
1. Create `.pre-commit-config.yaml` with:
   - ruff (linting + formatting)
   - mypy (type checking)
   - pytest (run tests)
2. Add instructions to README

---

### TASK-018: Add GitHub Actions CI
**Priority:** P3
**Type:** DevOps
**File:** `.github/workflows/ci.yml`

**Steps:**
1. Create CI workflow with:
   - Matrix testing (Python 3.9-3.13)
   - Linting (ruff)
   - Type checking (mypy)
   - Tests with coverage
   - Build verification
2. Add status badge to README

---

### TASK-019: Improve error messages
**Priority:** P3
**Type:** UX Enhancement
**Files:** `proxywhirl/exceptions.py`, `proxywhirl/rotator.py`

**Steps:**
1. Review all exception messages
2. Add actionable guidance to errors
3. Include relevant context (proxy URL, attempt count)
4. Add error codes for programmatic handling

---

### TASK-020: Add request logging middleware
**Priority:** P3
**Type:** Observability
**File:** `proxywhirl/api.py`

**Steps:**
1. Add request/response logging middleware
2. Log request duration, status code, endpoint
3. Redact sensitive data (passwords, tokens)
4. Use structured JSON logging

---

### TASK-021: Add Prometheus metrics endpoint
**Priority:** P3
**Type:** Observability
**Spec:** `specs/008-metrics-observability-performance/spec.md`
**File:** `proxywhirl/api.py`

**Steps:**
1. Add `prometheus_client` dependency
2. Create `/metrics` endpoint
3. Track:
   - Request count by endpoint
   - Request duration histogram
   - Proxy health gauge
   - Circuit breaker states
4. Add Grafana dashboard JSON

---

### TASK-022: Add Docker support
**Priority:** P3
**Type:** DevOps
**Files:** `Dockerfile`, `docker-compose.yml`

**Steps:**
1. Create optimized multi-stage Dockerfile
2. Create docker-compose.yml for local development
3. Add health check
4. Document container usage

---

### TASK-023: Add async API client
**Priority:** P3
**Type:** Feature
**File:** `proxywhirl/async_client.py`

**Steps:**
1. Create `AsyncProxyRotator` class
2. Mirror sync API with async methods
3. Use `httpx.AsyncClient`
4. Add async context manager support
5. Write tests

---

### TASK-024: Performance optimization - connection pooling
**Priority:** P3
**Type:** Performance
**File:** `proxywhirl/rotator.py`

**Steps:**
1. Implement connection pooling per proxy
2. Reuse connections within TTL
3. Add pool size configuration
4. Benchmark improvement

---

### TASK-025: Add proxy chain support
**Priority:** P3
**Type:** Feature
**File:** `proxywhirl/models.py`, `proxywhirl/rotator.py`

**Steps:**
1. Add `ProxyChain` model
2. Support chaining multiple proxies
3. Add chain-aware routing
4. Write tests

---

## Execution Order

### Phase 1: Make Package Usable (Day 1)
1. TASK-001 (Critical - fix imports)
2. TASK-005, TASK-006, TASK-007 (Quick linting fixes)
3. TASK-012 (Fix test imports)

### Phase 2: Stabilize (Days 2-3)
4. TASK-002, TASK-003, TASK-004 (Security)
5. TASK-008, TASK-009, TASK-010 (Code quality)
6. TASK-013 (Fix all tests)
7. TASK-014 (Type checking)

### Phase 3: Choose Feature Path (Days 4-7)
8. TASK-011A (Remove missing modules) OR
   TASK-011B/C/D (Implement missing modules)

### Phase 4: Polish (Week 2+)
9. TASK-015 through TASK-025 (Documentation & enhancements)

---

## Quick Commands Reference

```bash
# Verify package imports
python -c "import proxywhirl; print(proxywhirl.__version__)"

# Run all linting
uv run -- ruff check proxywhirl/

# Auto-fix linting issues
uv run -- ruff check proxywhirl/ --fix

# Run type checking
uv run -- mypy proxywhirl/

# Run tests
uv run -- pytest

# Run tests with coverage
uv run -- pytest --cov=proxywhirl --cov-report=html

# Format code
uv run -- ruff format proxywhirl/
```

---

## Notes for Subagents

1. **Always read the file before editing** - Use `Read` tool first
2. **Run tests after changes** - Verify no regressions
3. **Commit incrementally** - One task per commit
4. **Use descriptive commit messages** - Follow conventional commits
5. **Check ruff after edits** - Ensure no new errors introduced
6. **Reference this file** - Update task status as you complete items

---

*Last updated: 2025-12-24*
