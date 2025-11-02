# Implementation Plan: Analytics Engine & Usage Insights

**Branch**: `009-analytics-engine-analysis` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/009-analytics-engine-analysis/spec.md`

## Summary

The Analytics Engine & Usage Insights feature provides comprehensive analytics capabilities for tracking proxy usage patterns, analyzing source performance, calculating costs and ROI, exporting data for reporting, and managing retention policies. The system captures request-level telemetry, provides query APIs for analysis, implements adaptive sampling for high volumes, and maintains daily backups for disaster recovery.

**Primary Requirements**:
- Capture analytics data for every proxy request (timestamp, source, endpoint, status, response time, HTTP code)
- Query API supporting filtering by time range, source, application, domain, status with <5 second response for 30-day datasets (pagination planned for future enhancement)
- Adaptive sampling (100% below 10K req/min, 10% above 100K req/min with statistical weighting)
- Export capabilities (CSV, JSON, Excel) with configurable fields and date ranges
- Configurable retention policies with automatic aggregation (hourly after 7 days, daily after 30 days)
- Daily automated backups retained for 30 days (stored in GitHub/Kaggle)
- Read-only access for authenticated users, admin-only configuration changes
- <5ms overhead on proxy request execution (p95)

**Technical Approach**:
- Extend existing SQLite storage infrastructure (001-core-python-package)
- Asynchronous analytics collection to avoid blocking proxy operations
- Time-series optimized schema with proper indexing
- Pre-calculated aggregate metrics for common queries
- Integration with structured logging (007-logging-system-structured) for audit trails

## Technical Context

**Language/Version**: Python 3.9+ (target: 3.9, 3.10, 3.11, 3.12, 3.13)  
**Primary Dependencies**: 
- `sqlite3` (built-in) - Analytics database
- `pydantic>=2.0.0` - Data validation and models
- `pandas>=2.0.0` - Data analysis and aggregation (NEW)
- `httpx>=0.25.0` - Async operations (existing)
- `loguru>=0.7.0` - Structured logging (existing)

**Storage**: SQLite database with time-series optimized schema, indexed on (timestamp, proxy_source_id, success_status)  
**Testing**: pytest with property-based tests (hypothesis) for sampling algorithms, >85% coverage target  
**Target Platform**: Cross-platform Python (Linux, macOS, Windows)  
**Project Type**: Single library package (flat architecture per constitution)  
**Performance Goals**: 
- Query response: <5 seconds for 30-day datasets (p95)
- Collection overhead: <5ms on proxy requests (p95)
- Sampling engagement: <100ms detection and activation
- Export generation: <3 minutes for any time range

**Constraints**: 
- Must not add >5ms overhead to proxy operations
- Adaptive sampling must preserve statistical distribution
- Storage growth must remain linear and predictable
- Backup process must not impact query performance

**Scale/Scope**: 
- Support 1M+ requests/day without degradation
- 30-day full resolution data (~1GB per 1M requests)
- Multiple concurrent queries without blocking
- 10GB storage per 1M requests after aggregation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle 1: Library-First Architecture ✅
- Analytics engine implemented as pure Python library in `proxywhirl/analytics.py`
- No CLI or web dependencies required for core functionality
- API consumers can use analytics programmatically

### Principle 2: Test-First Development ✅
- Tests will be written BEFORE implementation (mandatory TDD)
- Property-based tests for sampling algorithms
- Integration tests for query performance
- Unit tests for aggregation logic

### Principle 3: Type Safety ✅
- Full mypy --strict compliance required
- Pydantic models for all analytics entities
- Type hints on all functions and methods

### Principle 4: Independent User Stories ✅
- US1 (Usage Tracking) independently testable
- US2 (Source Performance) independently testable
- US3 (Cost/ROI) independently testable
- US4 (Export) independently testable
- US5 (Retention) independently testable

### Principle 5: Performance Standards ✅
- <5ms collection overhead (p95) - within <1ms proxy selection budget
- Query performance targets explicit (<5 seconds for 30 days)
- Adaptive sampling prevents performance degradation at scale

### Principle 6: Security-First ✅
- No sensitive data in analytics (credentials excluded)
- Read-only access for authenticated users
- Admin-only config changes
- Complete audit trail of data access

### Principle 7: Simplicity ✅
- Single module: `proxywhirl/analytics.py` (within 10 module limit)
- Flat architecture, no sub-packages
- Reuses existing storage infrastructure
- Single responsibility: analytics collection and querying

**Result**: ✅ All constitutional principles satisfied. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/009-analytics-engine-analysis/
├── plan.md              # This file
├── research.md          # Phase 0 output (coming next)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
│   └── analytics-api.yaml
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── spec.md              # Feature specification
```

### Source Code (repository root)

```text
proxywhirl/              # Flat package (existing)
├── __init__.py          # Public API exports (update with analytics exports)
├── analytics.py         # NEW: Analytics engine implementation
├── analytics_models.py  # NEW: Pydantic models for analytics entities
├── storage.py           # EXTEND: Add analytics schema and queries
├── rotator.py           # MODIFY: Add analytics collection hooks
├── models.py            # Existing core models
├── config.py            # EXTEND: Add analytics configuration
└── py.typed             # PEP 561 type marker

tests/
├── unit/
│   ├── test_analytics.py           # NEW: Analytics core logic tests
│   ├── test_analytics_sampling.py  # NEW: Sampling algorithm tests
│   ├── test_analytics_queries.py   # NEW: Query API tests
│   └── test_analytics_export.py    # NEW: Export functionality tests
├── integration/
│   ├── test_analytics_integration.py  # NEW: End-to-end analytics tests
│   └── test_analytics_performance.py  # NEW: Performance benchmarks
└── property/
    └── test_analytics_sampling_properties.py  # NEW: Hypothesis property tests
```

**Structure Decision**: Single library package with flat architecture per constitutional principle #7. Analytics functionality added as two new modules (`analytics.py`, `analytics_models.py`) within the existing `proxywhirl/` package, keeping total module count under the 10 module limit. This maintains simplicity while providing comprehensive analytics capabilities.

## Complexity Tracking

> No constitutional violations - this table is not required.

---

## Phase 0: Research & Technical Decisions

The following research tasks must be completed to resolve all technical unknowns before design phase:

### Research Tasks

1. **Adaptive Sampling Implementation**
   - Research weighted random sampling algorithms for time-series data
   - Investigate reservoir sampling vs stratified sampling approaches
   - Determine statistical weighting formulas to preserve distribution characteristics
   - Benchmark sampling overhead to ensure <100ms activation time

2. **Time-Series Query Optimization**
   - Research SQLite indexing strategies for time-series queries
   - Investigate query plan optimization for date range filters
   - Evaluate partial index strategies for success/failure status
   - Research SQLite ANALYZE command usage for query optimization

3. **Pandas Integration Patterns**
   - Research pandas integration with SQLite for efficient aggregation
   - Investigate chunked reading strategies for large datasets
   - Evaluate pandas vs pure SQLite for aggregation performance
   - Research memory-efficient export patterns for large result sets

4. **Backup Strategies for SQLite**
   - Research SQLite backup API vs file copy approaches
   - Investigate incremental backup strategies
   - Evaluate VACUUM and ANALYZE integration with backup schedules
   - Research GitHub LFS vs Kaggle API for automated backup storage

5. **Aggregation Strategies**
   - Research time-bucket aggregation patterns in SQLite
   - Investigate materialized view alternatives in SQLite
   - Evaluate trigger-based vs scheduled aggregation approaches
   - Research rollup table design patterns for multiple granularities

### Deliverable

A `research.md` file documenting:
- **Decision**: Chosen approach for each research area
- **Rationale**: Why this approach was selected
- **Alternatives Considered**: What other options were evaluated
- **Implementation Guidance**: Key patterns and best practices
- **Performance Implications**: Expected impact on targets

---

## Phase 1: Design & Contracts

*Prerequisites: research.md completed*

### 1. Data Model Design (`data-model.md`)

Extract entities from spec and design database schema:

**Core Entities**:
- `UsageRecord` - Individual request telemetry
- `AggregateMetric` - Pre-calculated statistics per time bucket
- `CostRecord` - Cost data association with sources
- `RetentionPolicy` - Retention configuration
- `ExportJob` - Export request tracking

**Schema Design**:
- Time-series optimized tables with proper indexing
- Foreign key relationships to existing proxy_sources table
- Timestamp columns using UTC (INTEGER for Unix timestamp)
- Indexes on query filter columns (timestamp, source_id, status)

**State Transitions**:
- UsageRecord: created → retained → aggregated → archived/deleted
- ExportJob: queued → processing → completed/failed
- AggregateMetric: calculated → retained → archived/deleted

### 2. API Contracts (`contracts/analytics-api.yaml`)

Generate programmatic API contracts from functional requirements:

**Query API**:
- `query_usage(time_range, filters, group_by, metrics) -> DataFrame`
- `compare_periods(period1, period2, dimensions) -> ComparisonResult`
- `get_source_performance(source_id, time_range) -> PerformanceMetrics`
- `calculate_costs(time_range, cost_model) -> CostReport`

**Export API**:
- `export_analytics(time_range, format, fields) -> ExportJob`
- `get_export_status(job_id) -> ExportStatus`
- `download_export(job_id) -> bytes`

**Configuration API** (admin-only):
- `set_retention_policy(policy: RetentionPolicy) -> None`
- `get_retention_policy() -> RetentionPolicy`
- `set_sampling_thresholds(low, high, rate) -> None`
- `trigger_aggregation(time_range) -> AggregationJob`

**Audit API**:
- `get_access_log(time_range, user_filter) -> List[AccessEvent]`

### 3. Quick Start Guide (`quickstart.md`)

Provide working examples for each user story:

```python
# US1: Track Usage Patterns
from proxywhirl import ProxyRotator, AnalyticsEngine

rotator = ProxyRotator()
analytics = AnalyticsEngine(rotator)

# Usage is automatically tracked
response = rotator.request("https://example.com")

# Query usage patterns
usage = analytics.query_usage(
    time_range="24h",
    group_by="proxy_source"
)
print(usage.summary())

# US2: Analyze Source Performance
perf = analytics.get_source_performance(
    source_id="free-proxy-list",
    time_range="7d"
)
print(f"Success rate: {perf.success_rate}%")

# US3: Cost/ROI Analysis
costs = analytics.calculate_costs(
    time_range="30d",
    cost_model=CostModel.PER_REQUEST
)
print(f"Total spend: ${costs.total}")

# US4: Export Analytics
job = analytics.export_analytics(
    time_range="90d",
    format="csv",
    fields=["timestamp", "source", "success", "latency"]
)
analytics.download_export(job.id, "analytics.csv")

# US5: Configure Retention (admin)
analytics.set_retention_policy(
    RetentionPolicy(
        raw_data_days=7,
        hourly_aggregates_days=30,
        daily_aggregates_days=365
    )
)
```

### 4. Agent Context Update

Run `.specify/scripts/bash/update-agent-context.sh copilot` to add:
- New technology: `pandas>=2.0.0` for data analysis
- New modules: `analytics.py`, `analytics_models.py`
- New test files in tests/unit/, tests/integration/, tests/property/

---

## Next Steps

After Phase 1 completion, run `/speckit.tasks` to generate task decomposition in `tasks.md`. This will break down implementation into test-first phases with detailed acceptance criteria.

**Phase 1 Deliverables**:
- ✅ `research.md` - Technical decisions documented
- ✅ `data-model.md` - Database schema and entity design
- ✅ `contracts/analytics-api.yaml` - API contracts
- ✅ `quickstart.md` - Working examples
- ✅ Agent context updated with new dependencies

**Constitution Re-Check**: After Phase 1 design, verify all principles still satisfied (expected: ✅ pass).
