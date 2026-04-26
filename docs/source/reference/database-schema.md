---
title: Database Schema
---

# Database Schema Reference

## Overview

ProxyWhirl uses SQLModel (SQLAlchemy ORM) with SQLite for persistent proxy storage. The schema is managed via Alembic migrations.

## Schema Diagram

```
┌─────────────────┐          ┌──────────────────┐
│   ProxyTable    │ 1───────* │  ProxyMetrics    │
├─────────────────┤          ├──────────────────┤
│ id (PK)         │          │ id (PK)          │
│ url             │          │ proxy_id (FK)    │
│ protocol        │          │ latency_ms       │
│ host            │          │ success_rate     │
│ port            │          │ last_checked     │
│ country         │          │ updated_at       │
│ is_active       │          └──────────────────┘
│ created_at      │
│ updated_at      │
│ metadata        │
└─────────────────┘

┌──────────────────┐          ┌─────────────────┐
│  HealthMonitor   │ 1───────* │  CircuitBreaker │
├──────────────────┤          ├─────────────────┤
│ id (PK)          │          │ id (PK)         │
│ proxy_id (FK)    │          │ proxy_id (FK)   │
│ status           │          │ state           │
│ last_failure     │          │ failure_count   │
│ check_interval   │          │ last_failure    │
│ recovery_time    │          │ recovery_time   │
└──────────────────┘          └─────────────────┘
```

## Tables

### ProxyTable

Stores proxy server information and metadata.

```sql
CREATE TABLE proxy (
    id                  TEXT PRIMARY KEY,
    url                 TEXT NOT NULL UNIQUE,
    protocol            TEXT NOT NULL,  -- http, https, socks4, socks5
    host                TEXT NOT NULL,
    port                INTEGER NOT NULL,
    country             TEXT,            -- ISO 3166-1 alpha-2
    username            TEXT,
    password_encrypted  BYTEA,
    source              TEXT,            -- proxy source URL or name
    is_active           BOOLEAN DEFAULT TRUE,
    response_time_ms    FLOAT DEFAULT NULL,
    success_rate        FLOAT DEFAULT NULL,
    last_validated      DATETIME,
    validation_errors   INTEGER DEFAULT 0,
    cost_per_request    FLOAT DEFAULT NULL,
    concurrent_limit    INTEGER DEFAULT NULL,
    timeout_seconds     FLOAT DEFAULT 30,
    metadata            TEXT,            -- JSON string
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_proxy_protocol ON proxy(protocol);
CREATE INDEX idx_proxy_country ON proxy(country);
CREATE INDEX idx_proxy_is_active ON proxy(is_active);
CREATE INDEX idx_proxy_source ON proxy(source);
CREATE UNIQUE INDEX idx_proxy_url ON proxy(url);
```

### HealthMonitor

Tracks proxy health status and recovery metrics.

```sql
CREATE TABLE health_monitor (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    proxy_id        TEXT NOT NULL UNIQUE,
    status          TEXT DEFAULT 'HEALTHY',  -- HEALTHY, DEGRADED, UNHEALTHY
    failure_count   INTEGER DEFAULT 0,
    success_count   INTEGER DEFAULT 0,
    last_failure    DATETIME,
    last_success    DATETIME,
    check_interval  INTEGER DEFAULT 300,    -- seconds
    recovery_time   INTEGER DEFAULT 3600,   -- seconds
    metadata        TEXT,                   -- JSON
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proxy_id) REFERENCES proxy(id) ON DELETE CASCADE
);

CREATE INDEX idx_health_status ON health_monitor(status);
CREATE INDEX idx_health_proxy ON health_monitor(proxy_id);
```

### CircuitBreaker

Maintains circuit breaker state per proxy.

```sql
CREATE TABLE circuit_breaker (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    proxy_id        TEXT NOT NULL UNIQUE,
    state           TEXT DEFAULT 'CLOSED',  -- CLOSED, OPEN, HALF_OPEN
    failure_count   INTEGER DEFAULT 0,
    success_count   INTEGER DEFAULT 0,
    last_failure    DATETIME,
    last_reset      DATETIME,
    open_until      DATETIME,               -- auto-recovery time
    failure_threshold INTEGER DEFAULT 5,
    success_threshold INTEGER DEFAULT 2,
    recovery_timeout INTEGER DEFAULT 30,   -- seconds
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proxy_id) REFERENCES proxy(id) ON DELETE CASCADE
);

CREATE INDEX idx_cb_state ON circuit_breaker(state);
CREATE INDEX idx_cb_proxy ON circuit_breaker(proxy_id);
```

### ProxyMetrics

Historical metrics for performance tracking.

```sql
CREATE TABLE proxy_metrics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    proxy_id        TEXT NOT NULL,
    latency_ms      FLOAT,
    bandwidth_kbps  FLOAT,
    success_count   INTEGER DEFAULT 0,
    failure_count   INTEGER DEFAULT 0,
    error_type      TEXT,                -- connection, timeout, validation, auth
    response_code   INTEGER,
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proxy_id) REFERENCES proxy(id) ON DELETE CASCADE
);

CREATE INDEX idx_metrics_proxy ON proxy_metrics(proxy_id);
CREATE INDEX idx_metrics_timestamp ON proxy_metrics(timestamp);
CREATE INDEX idx_metrics_latency ON proxy_metrics(latency_ms);
```

### Cache Tables (L2)

Optional SQLite-backed cache for L2 tier.

```sql
CREATE TABLE cache_entry (
    key             TEXT PRIMARY KEY,
    value           BYTEA NOT NULL,
    expires_at      DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cache_expires ON cache_entry(expires_at);
```

## Migrations

Alembic manages schema evolution. Run migrations with:

```bash
# Apply pending migrations
alembic upgrade head

# Generate new migration (after model changes)
alembic revision --autogenerate -m "description"

# Downgrade one revision
alembic downgrade -1
```

### Migration Files

```
alembic/versions/
├── 001_initial_schema.py         -- ProxyTable, HealthMonitor, CircuitBreaker
├── 002_add_metrics.py             -- ProxyMetrics table
├── 003_add_cache_tables.py        -- Cache L2 support
└── ...
```

## Data Types

| Type | SQLite | Python | Example |
|------|--------|--------|---------|
| TEXT | TEXT | str | "192.168.1.1" |
| INTEGER | INTEGER | int | 8080 |
| FLOAT | REAL | float | 125.45 |
| BOOLEAN | INTEGER (0/1) | bool | True → 1 |
| DATETIME | TEXT (ISO8601) | datetime | "2025-04-26T08:00:00" |
| BYTEA | BLOB | bytes | b'\x01\x02...' |
| JSON | TEXT | str | '{"key": "value"}' |

## Common Queries

### Find All Active Proxies by Country

```sql
SELECT id, host, port, protocol FROM proxy 
WHERE is_active = 1 AND country = 'US'
ORDER BY response_time_ms ASC;
```

### Get Healthy Proxies with Recent Success

```sql
SELECT p.* FROM proxy p
JOIN health_monitor h ON p.id = h.proxy_id
WHERE h.status = 'HEALTHY' 
  AND h.last_success > datetime('now', '-1 hour')
ORDER BY p.response_time_ms ASC
LIMIT 10;
```

### Circuit Breaker State Summary

```sql
SELECT state, COUNT(*) as count FROM circuit_breaker
GROUP BY state;

-- Output:
-- CLOSED    | 850
-- HALF_OPEN | 15
-- OPEN      | 35
```

### Performance Metrics by Proxy

```sql
SELECT 
    proxy_id,
    AVG(latency_ms) as avg_latency,
    MIN(latency_ms) as min_latency,
    MAX(latency_ms) as max_latency,
    COUNT(*) as request_count
FROM proxy_metrics
WHERE timestamp > datetime('now', '-24 hours')
GROUP BY proxy_id
ORDER BY avg_latency ASC;
```

## Backup & Recovery

### Database Backup

```bash
# SQLite backup (single file)
cp proxywhirl.db proxywhirl.db.backup.$(date +%Y%m%d)

# Or with sqlite3 CLI
sqlite3 proxywhirl.db ".backup proxywhirl.db.backup"
```

### Recovery

```bash
# Restore from backup
cp proxywhirl.db.backup.20250426 proxywhirl.db

# Verify integrity
sqlite3 proxywhirl.db "PRAGMA integrity_check;"
```

## Performance Optimization

### Enable WAL Mode

```python
import sqlite3
conn = sqlite3.connect("proxywhirl.db")
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
```

### Index Strategy

- **Search Columns**: `protocol`, `country`, `source`, `is_active`
- **Filter Columns**: All columns in WHERE clauses
- **Sort Columns**: `response_time_ms`, `created_at`

### Vacuum & Analyze

```bash
# Reclaim space after deletes
sqlite3 proxywhirl.db "VACUUM;"

# Update query planner statistics
sqlite3 proxywhirl.db "ANALYZE;"
```

## Configuration

Set database path via environment:

```bash
export PROXYWHIRL_STORAGE_PATH="file:proxywhirl.db?mode=rwc&cache=shared"
```

Or in code:

```python
from proxywhirl import DataStorageConfig

config = DataStorageConfig(
    storage_path="proxywhirl.db",
    enable_backups=True,
    backup_dir="backups/",
    max_db_size_mb=1000
)
```

See also: [Storage & Persistence](../concepts/storage.md), [Migrations](./migrations.md)
