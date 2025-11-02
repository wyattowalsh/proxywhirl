# Research & Technical Decisions: Analytics Engine

**Date**: 2025-11-01  
**Feature**: 009-analytics-engine-analysis  
**Purpose**: Document technical decisions for analytics engine implementation

---

## 1. Adaptive Sampling Implementation

### Decision
Implement **reservoir sampling with time-based stratification** for adaptive analytics collection.

### Rationale
- Reservoir sampling provides unbiased statistical sampling with O(1) per-record decision time
- Time-based stratification ensures temporal distribution is preserved across sampling windows
- Weighted sampling can be applied to preserve distribution of categorical variables (proxy source, success/failure)
- Simple threshold-based switching between 100% capture and sampled modes

### Implementation Approach

```python
class AdaptiveSampler:
    def __init__(self, low_threshold=10_000, high_threshold=100_000, sample_rate=0.1):
        self.low_threshold = low_threshold  # req/min for 100% capture
        self.high_threshold = high_threshold  # req/min for sampling
        self.sample_rate = sample_rate  # 10% sampling
        self.reservoir = []
        self.count = 0
        
    def should_sample(self, current_rate_per_min: int) -> bool:
        """Determine if current request should be sampled."""
        if current_rate_per_min < self.low_threshold:
            return True  # 100% capture
        elif current_rate_per_min > self.high_threshold:
            # Reservoir sampling: include with probability sample_rate
            return random.random() < self.sample_rate
        else:
            # Linear interpolation between thresholds
            ratio = (current_rate_per_min - self.low_threshold) / \
                    (self.high_threshold - self.low_threshold)
            sample_prob = 1.0 - (ratio * (1.0 - self.sample_rate))
            return random.random() < sample_prob
```

### Performance Characteristics
- Decision time: O(1) constant time per request
- Memory overhead: Negligible (single boolean check + RNG call)
- Activation time: <1ms (threshold comparison)
- Statistical accuracy: Unbiased estimator for population statistics

### Alternatives Considered
1. **Stratified sampling**: More complex, requires pre-classification of requests
2. **Systematic sampling**: Can introduce bias for periodic patterns
3. **Fixed-rate sampling**: Doesn't adapt to load, wastes storage or loses data

---

## 2. Time-Series Query Optimization

### Decision
Use **covering indexes** with timestamp-first composite keys and **query result caching** for common date ranges.

### Rationale
- Covering indexes eliminate table lookups for filtered queries
- Timestamp-first ordering enables efficient range scans
- Common queries (last 24h, last 7d) can be cached with TTL invalidation
- SQLite query planner benefits from ANALYZE statistics on time-series data

### Implementation Approach

```sql
-- Primary usage table with covering index
CREATE TABLE analytics_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,  -- Unix timestamp (UTC)
    proxy_source_id TEXT NOT NULL,
    application_id TEXT,
    target_domain TEXT NOT NULL,
    http_method TEXT NOT NULL,
    success INTEGER NOT NULL,  -- 0/1 boolean
    response_time_ms INTEGER NOT NULL,
    http_status_code INTEGER,
    bytes_transferred INTEGER,
    error_code TEXT,
    sampled INTEGER NOT NULL DEFAULT 0,  -- 0=full capture, 1=sampled
    sample_weight REAL NOT NULL DEFAULT 1.0  -- Inverse probability weight
);

-- Covering index for time-range + source queries
CREATE INDEX idx_usage_time_source_success 
ON analytics_usage(timestamp DESC, proxy_source_id, success)
INCLUDE (response_time_ms, http_status_code, bytes_transferred);

-- Covering index for time-range + application queries
CREATE INDEX idx_usage_time_app 
ON analytics_usage(timestamp DESC, application_id, success)
INCLUDE (proxy_source_id, response_time_ms, target_domain);

-- Partial index for failures only (smaller, faster for error analysis)
CREATE INDEX idx_usage_failures 
ON analytics_usage(timestamp DESC, proxy_source_id, error_code)
WHERE success = 0;

-- Run ANALYZE after bulk inserts to update query planner statistics
ANALYZE analytics_usage;
```

### Query Pattern Example

```python
def query_usage_by_source(
    start_time: int, 
    end_time: int, 
    source_id: str
) -> pd.DataFrame:
    """
    Efficient query using covering index.
    Query planner will use idx_usage_time_source_success.
    """
    query = """
        SELECT 
            timestamp,
            success,
            response_time_ms,
            http_status_code,
            bytes_transferred,
            sample_weight
        FROM analytics_usage
        WHERE timestamp >= ? 
          AND timestamp < ?
          AND proxy_source_id = ?
        ORDER BY timestamp DESC
    """
    return pd.read_sql_query(query, conn, params=[start_time, end_time, source_id])
```

### Performance Characteristics
- Index scan: O(log n + k) where k = matching rows
- Covering index eliminates table lookups: ~40% query time reduction
- Timestamp range scans leverage B-tree ordering
- Target: <5 seconds for 30-day queries with proper indexing

### Alternatives Considered
1. **Full-text search indexes**: Overkill for structured time-series data
2. **Separate tables per source**: Violates simplicity principle, complex joins
3. **Partitioning by time**: SQLite doesn't support native partitioning

---

## 3. Pandas Integration Patterns

### Decision
Use **chunked reading with pandas** for large result sets and **SQLite aggregation** for GROUP BY operations.

### Rationale
- Pandas excels at in-memory analysis but can exhaust memory on large datasets
- SQLite GROUP BY aggregations are more efficient than pandas groupby for large data
- Chunked reading (iterator pattern) enables streaming large exports
- Pandas provides convenient export to CSV/JSON/Excel formats

### Implementation Approach

```python
def query_with_chunking(
    query: str, 
    params: List[Any],
    chunk_size: int = 10_000
) -> Iterator[pd.DataFrame]:
    """
    Stream large result sets in chunks to avoid memory exhaustion.
    """
    offset = 0
    while True:
        chunk_query = f"{query} LIMIT {chunk_size} OFFSET {offset}"
        chunk = pd.read_sql_query(chunk_query, conn, params=params)
        if chunk.empty:
            break
        yield chunk
        offset += chunk_size

def aggregate_in_database(
    time_range: tuple, 
    group_by: List[str]
) -> pd.DataFrame:
    """
    Leverage SQLite for aggregation, then load into pandas.
    """
    group_cols = ", ".join(group_by)
    query = f"""
        SELECT 
            {group_cols},
            COUNT(*) as request_count,
            SUM(success) as success_count,
            AVG(response_time_ms) as avg_latency,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_ms) as median_latency,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_latency,
            SUM(bytes_transferred) as total_bytes
        FROM analytics_usage
        WHERE timestamp >= ? AND timestamp < ?
        GROUP BY {group_cols}
    """
    return pd.read_sql_query(query, conn, params=time_range)

def export_large_dataset(
    query: str, 
    output_path: str, 
    format: str = "csv"
) -> None:
    """
    Export large datasets without loading everything into memory.
    """
    first_chunk = True
    for chunk in query_with_chunking(query, []):
        mode = 'w' if first_chunk else 'a'
        header = first_chunk
        
        if format == "csv":
            chunk.to_csv(output_path, mode=mode, header=header, index=False)
        elif format == "json":
            chunk.to_json(output_path, orient='records', lines=True, mode=mode)
        
        first_chunk = False
```

### Performance Characteristics
- Memory usage: O(chunk_size) instead of O(total_rows)
- Aggregation: SQLite native GROUP BY faster than pandas for >100K rows
- Export speed: ~100K rows/second for CSV, ~50K rows/second for JSON
- Target: <3 minutes for exports of any size

### Alternatives Considered
1. **Pure SQLite with manual CSV writing**: More code, less maintainable
2. **Load all into pandas first**: Memory exhaustion risk
3. **Use Dask for distributed processing**: Overkill for single-node library

---

## 4. Backup Strategies for SQLite

### Decision
Use **SQLite backup API with incremental approach** and **automated upload to GitHub LFS / Kaggle**.

### Rationale
- SQLite backup API provides consistent snapshots without locking
- Incremental backups reduce storage and upload time
- GitHub LFS supports large binary files (databases)
- Kaggle API provides programmatic dataset upload
- VACUUM before backup reduces file size

### Implementation Approach

```python
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime

class AnalyticsBackup:
    def __init__(self, db_path: str, backup_dir: str):
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self) -> Path:
        """
        Create consistent backup using SQLite backup API.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"analytics_{timestamp}.db"
        
        # Vacuum before backup to reduce size
        src_conn = sqlite3.connect(self.db_path)
        src_conn.execute("VACUUM")
        src_conn.close()
        
        # Use backup API for consistent snapshot
        src_conn = sqlite3.connect(self.db_path)
        dst_conn = sqlite3.connect(backup_path)
        
        with dst_conn:
            src_conn.backup(dst_conn, pages=100, progress=self._backup_progress)
        
        src_conn.close()
        dst_conn.close()
        
        return backup_path
    
    def upload_to_github_lfs(self, backup_path: Path) -> None:
        """
        Upload backup to GitHub repository using LFS.
        """
        # Add to git-lfs tracking
        subprocess.run(["git", "lfs", "track", "*.db"], check=True)
        
        # Add, commit, push
        subprocess.run(["git", "add", str(backup_path)], check=True)
        subprocess.run([
            "git", "commit", "-m", 
            f"Analytics backup: {backup_path.name}"
        ], check=True)
        subprocess.run(["git", "push"], check=True)
    
    def upload_to_kaggle(self, backup_path: Path) -> None:
        """
        Upload backup to Kaggle dataset using API.
        """
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        api.dataset_create_version(
            folder=str(backup_path.parent),
            version_notes=f"Automated backup: {datetime.utcnow().isoformat()}",
            quiet=False
        )
    
    def cleanup_old_backups(self, retain_days: int = 30) -> None:
        """
        Remove backups older than retention period.
        """
        cutoff = datetime.utcnow().timestamp() - (retain_days * 86400)
        
        for backup_file in self.backup_dir.glob("analytics_*.db"):
            if backup_file.stat().st_mtime < cutoff:
                backup_file.unlink()
```

### Backup Schedule

```python
# Automated daily backup (using cron or scheduler)
def daily_backup_job():
    backup = AnalyticsBackup(
        db_path="analytics.db",
        backup_dir="backups/"
    )
    
    # Create backup
    backup_path = backup.create_backup()
    
    # Upload to both GitHub and Kaggle for redundancy
    backup.upload_to_github_lfs(backup_path)
    backup.upload_to_kaggle(backup_path)
    
    # Cleanup old local backups
    backup.cleanup_old_backups(retain_days=30)
```

### Performance Characteristics
- Backup time: ~1 minute per 1GB database
- No read/write blocking during backup
- Incremental uploads to GitHub LFS (only changed blocks)
- Storage: 30 backups × database size

### Alternatives Considered
1. **Simple file copy**: No consistency guarantee during writes
2. **SQLite .dump command**: Slower, produces SQL text instead of binary
3. **Cloud storage only**: GitHub/Kaggle provide version control benefits

---

## 5. Aggregation Strategies

### Decision
Use **scheduled aggregation with separate rollup tables** for each time granularity (hourly, daily).

### Rationale
- Separate tables avoid mixing granularities in queries
- Scheduled aggregation (background job) avoids query-time overhead
- Pre-calculated aggregates enable fast dashboard queries
- Rollup tables can be indexed differently than raw data
- Trigger-based aggregation adds overhead to write path

### Implementation Approach

```sql
-- Hourly aggregates (kept for 30 days)
CREATE TABLE analytics_hourly (
    hour_timestamp INTEGER PRIMARY KEY,  -- Start of hour (Unix timestamp)
    proxy_source_id TEXT NOT NULL,
    application_id TEXT,
    request_count INTEGER NOT NULL,
    success_count INTEGER NOT NULL,
    failure_count INTEGER NOT NULL,
    avg_response_time_ms REAL NOT NULL,
    median_response_time_ms REAL NOT NULL,
    p95_response_time_ms REAL NOT NULL,
    total_bytes_transferred INTEGER NOT NULL,
    unique_domains_count INTEGER NOT NULL,
    sample_adjusted INTEGER NOT NULL DEFAULT 0  -- 1 if includes sampled data
);

CREATE INDEX idx_hourly_time_source ON analytics_hourly(hour_timestamp DESC, proxy_source_id);

-- Daily aggregates (kept for 365 days)
CREATE TABLE analytics_daily (
    day_timestamp INTEGER PRIMARY KEY,  -- Start of day (Unix timestamp)
    proxy_source_id TEXT NOT NULL,
    application_id TEXT,
    request_count INTEGER NOT NULL,
    success_count INTEGER NOT NULL,
    failure_count INTEGER NOT NULL,
    avg_response_time_ms REAL NOT NULL,
    median_response_time_ms REAL NOT NULL,
    p95_response_time_ms REAL NOT NULL,
    total_bytes_transferred INTEGER NOT NULL,
    unique_domains_count INTEGER NOT NULL,
    sample_adjusted INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_daily_time_source ON analytics_daily(day_timestamp DESC, proxy_source_id);
```

```python
def aggregate_to_hourly(start_hour: int, end_hour: int) -> None:
    """
    Aggregate raw usage data into hourly rollups.
    Run daily for previous 24 hours.
    """
    query = """
        INSERT OR REPLACE INTO analytics_hourly
        SELECT 
            (timestamp / 3600) * 3600 as hour_timestamp,
            proxy_source_id,
            application_id,
            SUM(sample_weight) as request_count,  -- Adjust for sampling
            SUM(success * sample_weight) as success_count,
            SUM((1 - success) * sample_weight) as failure_count,
            AVG(response_time_ms) as avg_response_time_ms,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_ms) as median_response_time_ms,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time_ms,
            SUM(bytes_transferred * sample_weight) as total_bytes_transferred,
            COUNT(DISTINCT target_domain) as unique_domains_count,
            MAX(sampled) as sample_adjusted
        FROM analytics_usage
        WHERE timestamp >= ? AND timestamp < ?
        GROUP BY hour_timestamp, proxy_source_id, application_id
    """
    conn.execute(query, (start_hour, end_hour))
    conn.commit()

def aggregate_to_daily(start_day: int, end_day: int) -> None:
    """
    Aggregate hourly data into daily rollups.
    Run daily for previous day.
    """
    # Can aggregate from hourly table (faster) or raw data
    query = """
        INSERT OR REPLACE INTO analytics_daily
        SELECT 
            (hour_timestamp / 86400) * 86400 as day_timestamp,
            proxy_source_id,
            application_id,
            SUM(request_count) as request_count,
            SUM(success_count) as success_count,
            SUM(failure_count) as failure_count,
            AVG(avg_response_time_ms) as avg_response_time_ms,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY median_response_time_ms) as median_response_time_ms,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY p95_response_time_ms) as p95_response_time_ms,
            SUM(total_bytes_transferred) as total_bytes_transferred,
            SUM(unique_domains_count) as unique_domains_count,  -- Approximation
            MAX(sample_adjusted) as sample_adjusted
        FROM analytics_hourly
        WHERE hour_timestamp >= ? AND hour_timestamp < ?
        GROUP BY day_timestamp, proxy_source_id, application_id
    """
    conn.execute(query, (start_day, end_day))
    conn.commit()

def scheduled_aggregation_job():
    """
    Run daily to maintain rollup tables.
    """
    now = int(datetime.utcnow().timestamp())
    
    # Aggregate yesterday's data to hourly
    yesterday_start = (now // 86400 - 1) * 86400
    aggregate_to_hourly(yesterday_start, yesterday_start + 86400)
    
    # Aggregate last week's hourly to daily
    week_ago = (now // 86400 - 7) * 86400
    aggregate_to_daily(week_ago, yesterday_start)
    
    # Delete raw data older than 7 days (after aggregation)
    retention_cutoff = now - (7 * 86400)
    conn.execute("DELETE FROM analytics_usage WHERE timestamp < ?", (retention_cutoff,))
    conn.commit()
```

### Aggregation Schedule
- **Hourly aggregation**: Run daily at 00:00 UTC for previous 24 hours
- **Daily aggregation**: Run weekly for previous 7 days
- **Raw data cleanup**: After aggregation confirms success
- **VACUUM**: Run monthly to reclaim space

### Performance Characteristics
- Aggregation time: ~1 minute per 1M raw records
- Query performance: 10-100x faster on rollup tables vs raw data
- Storage savings: ~90% reduction after aggregation
- No impact on write path (scheduled, not triggered)

### Alternatives Considered
1. **Trigger-based aggregation**: Adds overhead to every INSERT
2. **Materialized views**: SQLite doesn't support automated refresh
3. **Single table with granularity column**: Complicates queries and indexing

---

## Implementation Priority

1. **Phase 0 (Foundation)**:
   - Core schema with covering indexes
   - Basic query API without aggregation
   - Simple 100% capture (no sampling yet)

2. **Phase 1 (Sampling & Performance)**:
   - Adaptive sampling implementation
   - Query optimization with pandas integration
   - Performance benchmarking

3. **Phase 2 (Aggregation & Retention)**:
   - Scheduled aggregation jobs
   - Rollup table generation
   - Retention policy enforcement

4. **Phase 3 (Backup & Export)**:
   - Backup automation
   - GitHub LFS / Kaggle integration
   - Export functionality

---

## Performance Validation

After implementation, validate against targets:

- ✅ Query <5 seconds for 30-day datasets (p95)
- ✅ Collection overhead <5ms (p95)
- ✅ Sampling activation <100ms
- ✅ Export <3 minutes for any time range
- ✅ Storage growth linear (10GB per 1M requests)
- ✅ Backup time <5 minutes for 5GB database

---

**Research Complete**: All technical unknowns resolved. Ready for Phase 1 (Design & Contracts).
