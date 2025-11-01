# Implementation Plan: Caching Mechanisms & Storage

**Branch**: `005-caching-mechanisms-storage` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-caching-mechanisms-storage/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a three-tier caching system (in-memory L1, flat file L2, SQLite L3) for persistent proxy storage with TTL-based expiration, health-based invalidation, LRU eviction, credential encryption, and graceful degradation. The cache reduces external proxy fetches by 60%+ while maintaining <1ms memory lookups and <50ms disk lookups. Extends existing `storage.py` infrastructure and integrates with health monitoring for cache invalidation.

## Technical Context

**Language/Version**: Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13)  
**Primary Dependencies**: 
- `pydantic>=2.0.0` (data validation, SecretStr for credentials)
- `cryptography>=41.0.0` (credential encryption at rest - NEW)
- Existing: `httpx`, `tenacity`, `loguru`

**Storage**: 
- L1 (Memory): Python dict with OrderedDict for LRU tracking
- L2 (JSONL Flat File): JSONL files with file locking (fcntl/msvcrt)
- L3 (SQLite): Extends existing `storage.py` with cache tables

**Testing**: pytest with coverage target 85%+, hypothesis for property tests  
**Target Platform**: Cross-platform (Linux, macOS, Windows) - file locking abstraction required  
**Project Type**: Single Python library package (flat architecture per constitution)  
**Performance Goals**: 
- L1 lookups: <1ms (SC-002)
- L2/L3 lookups: <50ms (SC-003)
- Cache warming: 10k proxies in <5s (SC-007)
- Eviction overhead: <10ms (SC-009)

**Constraints**: 
- Memory: ~10MB for L1 (1000 proxies default)
- Storage: <100MB for 10k proxies (SC-010)
- Thread-safe: 100k concurrent ops without corruption (SC-008)
- Credential security: 100% protection (never logged/exposed)

**Scale/Scope**: 
- Default: 1000 proxies (L1), 5000 proxies (L2), unlimited (L3)
- Target hit rate: 80%+ (SC-001)
- Reduce external fetches: 60%+ (SC-004)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Library-First Architecture
- **Status**: PASS
- New cache module (`cache.py` or split into `cache_*.py`) integrates with existing flat package structure
- Usable via direct import: `from proxywhirl.cache import CacheManager`
- No CLI/web dependencies required (though may integrate with existing REST API)
- Full type hints with `py.typed` marker compliance

### ✅ II. Test-First Development
- **Status**: PASS (ENFORCED)
- TDD workflow: Write tests → User approval → Tests fail → Implement
- Target coverage: 85%+ (consistent with 88% existing)
- Property-based tests for LRU eviction, TTL expiration, cache coherence
- Integration tests for all 6 user stories
- 100% coverage for credential security code (constitutional requirement)

### ✅ III. Type Safety & Runtime Validation
- **Status**: PASS
- Full type hints for all cache APIs
- Pydantic models for CacheEntry, CacheConfig, CacheStatistics
- SecretStr for credentials (runtime validation)
- mypy --strict compliance required
- Clear validation errors for corrupted entries, invalid TTL, etc.

### ✅ IV. Independent User Stories
- **Status**: PASS
- All 6 user stories independently testable:
  - US1 (Persist) - test persistence across restarts
  - US2 (TTL) - test expiration in isolation
  - US3 (Health invalidation) - mock health check failures
  - US4 (Multi-tier) - test tier promotion/demotion
  - US5 (Cache warming) - test import from files
  - US6 (Statistics) - test metrics tracking
- No hidden inter-story dependencies

### ✅ V. Performance Standards
- **Status**: PASS (Verified by success criteria)
- L1 selection: <1ms (exceeds <5ms standard)
- Thread-safe with fine-grained locking per tier
- Memory-bounded with LRU eviction
- Concurrent ops: 100k without corruption (exceeds 10k standard)

### ⚠️  VI. Security-First Design
- **Status**: PASS (Enhanced requirements)
- SecretStr for L1 credentials
- Encryption at rest for L2/L3 (cryptography library)
- Never log decrypted credentials (explicit FR-023)
- Validation in tests: 100% credential coverage
- Encryption key from environment variable (FR-024)

### ✅ VII. Simplicity & Flat Architecture
- **Status**: PASS
- Flat module structure: `proxywhirl/cache.py` or split if >500 LOC
- Single responsibility: Caching only, delegates to existing storage.py for SQLite
- Current module count: ~13 → Adding 1-2 cache modules (well under 20 limit)
- No circular dependencies
- Leverages existing infrastructure (storage.py, config.py, models.py)

### 🔍 VIII. Python Package Management (uv)
- **Status**: PASS
- All commands use `uv run` prefix
- New dependency: `uv add cryptography>=41.0.0`
- Test execution: `uv run pytest tests/unit/test_cache.py`
- Type checking: `uv run mypy --strict proxywhirl/cache.py`

### Overall Gate: ✅ PASS
No constitutional violations. Feature aligns with all core principles.

## Project Structure

### Documentation (this feature)

```text
specs/005-caching-mechanisms-storage/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (already exists)
├── research.md          # Phase 0 output (created next)
├── data-model.md        # Phase 1 output (created next)
├── quickstart.md        # Phase 1 output (created next)
├── contracts/           # Phase 1 output (created next)
│   └── cache-api.json   # Internal API contract for CacheManager
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
proxywhirl/              # Flat package structure (constitution VII)
├── __init__.py          # Public API exports
├── cache.py             # NEW: CacheManager, CacheTier interface
├── cache_tiers.py       # NEW: MemoryCacheTier, FileCacheTier, SQLiteCacheTier implementations
├── cache_models.py      # NEW: CacheEntry, CacheConfig, CacheStatistics (Pydantic)
├── cache_crypto.py      # NEW: Credential encryption/decryption utilities
├── storage.py           # EXISTING: Extend with cache table schema
├── models.py            # EXISTING: May add cache-related models
├── config.py            # EXISTING: Add cache configuration settings
├── exceptions.py        # EXISTING: Add cache-specific exceptions
└── ...                  # Other existing modules

tests/
├── unit/
│   ├── test_cache_manager.py        # NEW: CacheManager unit tests
│   ├── test_cache_tiers.py          # NEW: Individual tier tests
│   ├── test_cache_lru.py            # NEW: LRU eviction tests
│   ├── test_cache_ttl.py            # NEW: TTL expiration tests
│   ├── test_cache_crypto.py         # NEW: Credential encryption tests (100% coverage)
│   └── test_cache_statistics.py     # NEW: Metrics tracking tests
├── integration/
│   ├── test_cache_persistence.py    # NEW: Restart persistence tests (US1)
│   ├── test_cache_health.py         # NEW: Health invalidation tests (US3)
│   ├── test_cache_warming.py        # NEW: Cache warming tests (US5)
│   └── test_cache_multi_tier.py     # NEW: Tier promotion/demotion (US4)
├── property/
│   └── test_cache_properties.py     # NEW: Hypothesis tests for invariants
└── benchmarks/
    └── test_cache_performance.py    # NEW: Performance validation (SC-002, SC-003, SC-007, SC-009)
```

**Structure Decision**: Single project with flat module structure. Cache feature adds 4 new modules (`cache.py`, `cache_tiers.py`, `cache_models.py`, `cache_crypto.py`) to the existing `proxywhirl/` package, staying well under the 20-module constitutional limit. Extends existing `storage.py` for SQLite tier rather than duplicating database logic.

## Complexity Tracking

> **No violations requiring justification**

This feature maintains constitutional simplicity:

- Flat module structure preserved
- Single responsibility per module (cache management)
- No new architectural patterns introduced
- Leverages existing infrastructure (storage, config, models)
- Module count: 13 existing + 4 new = 17 total (under 20 limit)

---

## Phase 0: Research Complete ✅

**Status**: Complete  
**Output**: [research.md](./research.md)

**Key Decisions Made**:

1. **Credential Encryption**: Fernet (symmetric encryption) from `cryptography` library
2. **File Locking**: `portalocker` library for cross-platform compatibility
3. **LRU Implementation**: Python stdlib `OrderedDict` with O(1) operations
4. **TTL Strategy**: Hybrid lazy expiration + background cleanup
5. **Tier Promotion**: Read-through caching with automatic tier optimization
6. **Statistics**: Atomic counters with periodic aggregation
7. **Graceful Degradation**: Try-except with tier skip flag + health tracking

**New Dependencies**:

```bash
uv add cryptography>=41.0.0
uv add portalocker>=2.8.0
```

---

## Phase 1: Design & Contracts Complete ✅

**Status**: Complete  
**Outputs**:

- [data-model.md](./data-model.md) - Entity schemas and relationships
- [contracts/cache-api.json](./contracts/cache-api.json) - Internal API contract
- [quickstart.md](./quickstart.md) - Usage examples and integration guide

**Key Entities Defined**:

1. **CacheEntry**: Proxy + metadata with TTL, health status, access tracking
2. **CacheConfig**: Tier configuration, TTL settings, encryption, paths
3. **CacheStatistics**: Hit rates, eviction counts, degradation status
4. **CacheTier**: Abstract interface with MemoryCacheTier, FileCacheTier, SQLiteCacheTier

**Database Schema**: SQLite table `cache_entries` with indexes for TTL/LRU queries

**File Format**: JSONL (one entry per line) with sharding by key prefix

**Agent Context**: Updated `.github/copilot-instructions.md` with Python 3.9+ targeting

---

## Phase 2: Task Breakdown (Next Command)

**Status**: Pending - requires `/speckit.tasks` command

This plan document is now complete. Next step: Generate `tasks.md` with test-first implementation phases.

**Ready for**: `/speckit.tasks`

---

## Constitution Re-Check Post-Design ✅

All constitutional principles verified after design phase:

- ✅ Library-first architecture maintained
- ✅ TDD workflow enforced (tests written before implementation)
- ✅ Full type safety with Pydantic models
- ✅ Independent user stories (all 6 testable in isolation)
- ✅ Performance targets achievable (<1ms L1, <50ms L2/L3)
- ✅ Security enhanced (credential encryption, SecretStr, env key management)
- ✅ Flat module structure preserved (4 new modules, total 17)
- ✅ `uv run` commands enforced

**Overall Gate**: ✅ PASS - No violations, ready for implementation
