# ProxyWhirl Database Schema Design

## Overview

ProxyWhirl uses SQLModel (Pydantic + SQLAlchemy) for ORM and stores proxy data in SQLite. This guide documents the complete schema, relationships, and design patterns.

## Core Tables

### ProxyTable
Main proxy records with connection metadata and performance statistics.

```python
class ProxyTable(SQLModel, table=True):
    """Core proxy data model in database."""
    
    __tablename__ = "proxies"
    
    # Identifiers
    id: int = Field(primary_key=True)
    proxy_url: str = Field(unique=True, index=True)
    
    # Proxy Details
    protocol: str  # http, https, socks5
    host: str
    port: int
    username: str | None
    password: str | None  # encrypted
    
    # Status & Health
    is_active: bool = True
    health_status: str  # HEALTHY, SUSPICIOUS, DEAD
    last_health_check: datetime
    consecutive_failures: int = 0
    
    # Performance
    avg_response_time_ms: float | None
    bandwidth_mbps: float | None
    geolocation: str | None
    
    # Metadata
    source: str  # where proxy came from
    added_date: datetime
    last_used: datetime | None
    tags: str | None  # JSON array of tags
    custom_headers: str | None  # JSON
    
    # Relationships
    sessions: list["SessionTable"] = Relationship(back_populates="proxy")
    performance_logs: list["PerformanceLogTable"] = Relationship(back_populates="proxy")
```

### SessionTable
HTTP/HTTPS sessions using specific proxies for request tracking.

```python
class SessionTable(SQLModel, table=True):
    """Track sessions and their proxy usage."""
    
    __tablename__ = "sessions"
    
    id: int = Field(primary_key=True)
    session_id: str = Field(unique=True, index=True)
    proxy_id: int = Field(foreign_key="proxies.id", index=True)
    
    # Session Info
    created_at: datetime
    last_active: datetime
    request_count: int = 0
    error_count: int = 0
    
    # Custom Data
    headers: str | None  # JSON
    cookies: str | None  # JSON
    
    # Relationships
    proxy: ProxyTable = Relationship(back_populates="sessions")
    requests: list["RequestLogTable"] = Relationship(back_populates="session")
```

### PerformanceLogTable
Time-series performance metrics for analytics and optimization.

```python
class PerformanceLogTable(SQLModel, table=True):
    """Performance metrics history."""
    
    __tablename__ = "performance_logs"
    
    id: int = Field(primary_key=True)
    proxy_id: int = Field(foreign_key="proxies.id", index=True)
    timestamp: datetime = Field(index=True)
    
    # Metrics
    response_time_ms: float
    status_code: int
    bytes_sent: int
    bytes_received: int
    
    # Request Info
    target_host: str
    error_message: str | None
    
    proxy: ProxyTable = Relationship(back_populates="performance_logs")
```

### CacheTable
Multi-tier cache storage for proxy queries and DNS.

```python
class CacheTable(SQLModel, table=True):
    """Cache entries for fast lookup."""
    
    __tablename__ = "cache_entries"
    
    id: int = Field(primary_key=True)
    key: str = Field(unique=True, index=True)
    tier: str  # L1 (memory), L2 (redis), L3 (disk)
    value: str  # JSON encoded
    expires_at: datetime = Field(index=True)
    created_at: datetime
    hit_count: int = 0
```

## Query Optimization Patterns

### Get Healthy Proxies by Country
```sql
SELECT p.* FROM proxies p
WHERE p.is_active = 1
  AND p.health_status = 'HEALTHY'
  AND p.geolocation LIKE '%Country%'
ORDER BY p.avg_response_time_ms ASC
LIMIT 10;
```

### Proxy Rotation Statistics
```sql
SELECT 
    p.id,
    p.proxy_url,
    COUNT(s.id) as session_count,
    SUM(s.request_count) as total_requests,
    AVG(pl.response_time_ms) as avg_response_time
FROM proxies p
LEFT JOIN sessions s ON p.id = s.proxy_id
LEFT JOIN performance_logs pl ON p.id = pl.proxy_id
WHERE pl.timestamp > datetime('now', '-1 day')
GROUP BY p.id
ORDER BY total_requests DESC;
```

### Health Check Candidates
```sql
SELECT p.id, p.proxy_url, p.last_health_check
FROM proxies p
WHERE p.is_active = 1
  AND (p.last_health_check IS NULL 
       OR p.last_health_check < datetime('now', '-30 minutes'))
ORDER BY p.last_health_check ASC
LIMIT 20;
```

## Indexes for Performance

```sql
CREATE INDEX idx_proxy_status ON proxies(is_active, health_status);
CREATE INDEX idx_proxy_geolocation ON proxies(geolocation);
CREATE INDEX idx_session_proxy ON sessions(proxy_id);
CREATE INDEX idx_perf_log_timestamp ON performance_logs(timestamp);
CREATE INDEX idx_perf_log_proxy ON performance_logs(proxy_id, timestamp);
CREATE INDEX idx_cache_expires ON cache_entries(expires_at);
```

## Data Lifecycle

### Proxy Lifecycle
1. **Creation**: Fetched from source, validated
2. **Active**: In rotation pool, health checked
3. **Suspicious**: High failure rate detected
4. **Dead**: Consecutive failures threshold exceeded
5. **Archived**: Moved to historical table after 30 days

### Session Lifecycle
1. **Created**: When rotator initializes
2. **Active**: Used for proxied requests
3. **Stale**: No requests for 24+ hours
4. **Closed**: Session cleanup

### Performance Log Retention
- Last 7 days: Detailed metrics
- 8-30 days: Hourly aggregates
- 31+ days: Daily aggregates

## Backup & Recovery

### Backup Strategy
```bash
sqlite3 proxywhirl.db ".backup backup.db"
```

### Recovery
```bash
sqlite3 proxywhirl.db ".restore backup.db"
```

### Migration to PostgreSQL
See MIGRATION_GUIDE_V2.md for production deployments.

