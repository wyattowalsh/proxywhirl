# Data Model: Health Monitoring

**Feature**: 006-health-monitoring-continuous  
**Date**: 2025-11-01

## Overview

Data structures for continuous proxy health monitoring including health status tracking, event notifications, pool statistics, and persistent state management.

## Core Entities

### 1. HealthStatus (Enum)

**Purpose**: Represents the current health state of a proxy

**Definition**:
```python
from enum import Enum

class HealthStatus(str, Enum):
    """Proxy health status enumeration."""
    
    HEALTHY = "healthy"              # Proxy passing health checks
    UNHEALTHY = "unhealthy"          # Proxy failing (under threshold)
    CHECKING = "checking"            # Health check in progress
    RECOVERING = "recovering"        # In recovery cooldown period
    PERMANENTLY_FAILED = "failed"    # Exceeded max recovery attempts
    UNKNOWN = "unknown"              # Not yet checked
```

**State Transitions**:
```
UNKNOWN → CHECKING → HEALTHY
HEALTHY → CHECKING → UNHEALTHY (after N failures)
UNHEALTHY → RECOVERING → CHECKING → HEALTHY (success)
UNHEALTHY → RECOVERING → CHECKING → UNHEALTHY (failure)
UNHEALTHY → PERMANENTLY_FAILED (max retries exceeded)
```

**Validation Rules**:
- Must be one of the enum values
- Cannot transition directly from UNKNOWN to UNHEALTHY
- Cannot recover from PERMANENTLY_FAILED

---

### 2. HealthCheckResult (Pydantic Model)

**Purpose**: Result of a single health check attempt

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `proxy_url` | `str` | Yes | - | Proxy URL checked |
| `check_time` | `datetime` | Yes | - | When check performed (UTC) |
| `status` | `HealthStatus` | Yes | - | Result status |
| `response_time_ms` | `float` | No | `None` | Response time in milliseconds |
| `status_code` | `int` | No | `None` | HTTP status code (if successful) |
| `error_message` | `str` | No | `None` | Error details (if failed) |
| `check_url` | `str` | Yes | - | Target URL used for check |

**Example**:
```python
result = HealthCheckResult(
    proxy_url="http://proxy1.example.com:8080",
    check_time=datetime.now(timezone.utc),
    status=HealthStatus.HEALTHY,
    response_time_ms=234.5,
    status_code=200,
    check_url="http://httpbin.org/status/200"
)
```

**Validation**:
- `check_time` must be timezone-aware (UTC)
- `response_time_ms` must be >= 0 if provided
- `status_code` must be in range 100-599 if provided
- `error_message` required if status is UNHEALTHY

---

### 3. HealthEvent (Pydantic Model)

**Purpose**: Notification event for significant health state changes

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `event_type` | `str` | Yes | - | Event type (proxy_down, proxy_recovered, pool_degraded) |
| `proxy_url` | `str` | No | `None` | Affected proxy URL (None for pool events) |
| `timestamp` | `datetime` | Yes | `utcnow()` | When event occurred |
| `previous_status` | `HealthStatus` | No | `None` | Previous health status |
| `new_status` | `HealthStatus` | Yes | - | New health status |
| `failure_count` | `int` | No | `0` | Consecutive failures at time of event |
| `metadata` | `dict[str, Any]` | No | `{}` | Additional context |

**Event Types**:
- `proxy_down`: Proxy marked unhealthy after threshold
- `proxy_recovered`: Unhealthy proxy passed recovery check
- `pool_degraded`: Pool health below threshold (e.g., <50% healthy)
- `pool_recovered`: Pool health returned to normal

**Example**:
```python
event = HealthEvent(
    event_type="proxy_down",
    proxy_url="http://proxy1.example.com:8080",
    timestamp=datetime.now(timezone.utc),
    previous_status=HealthStatus.HEALTHY,
    new_status=HealthStatus.UNHEALTHY,
    failure_count=3,
    metadata={"source": "free-proxy-list", "threshold": 3}
)
```

---

### 4. PoolStatus (Pydantic Model)

**Purpose**: Aggregate health statistics for proxy pool

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `total_proxies` | `int` | Yes | - | Total proxies in pool |
| `healthy_count` | `int` | Yes | - | Proxies with HEALTHY status |
| `unhealthy_count` | `int` | Yes | - | Proxies with UNHEALTHY status |
| `checking_count` | `int` | Yes | - | Proxies currently being checked |
| `recovering_count` | `int` | Yes | - | Proxies in recovery cooldown |
| `unknown_count` | `int` | Yes | - | Proxies not yet checked |
| `permanently_failed_count` | `int` | Yes | - | Proxies permanently failed |
| `health_percentage` | `float` | No | - | Computed: healthy/total * 100 |
| `last_updated` | `datetime` | Yes | `utcnow()` | When stats last computed |
| `by_source` | `dict[str, SourceStatus]` | No | `{}` | Breakdown by proxy source |

**Computed Properties**:
```python
@property
def health_percentage(self) -> float:
    if self.total_proxies == 0:
        return 0.0
    return (self.healthy_count / self.total_proxies) * 100

@property
def is_degraded(self) -> bool:
    return self.health_percentage < 50.0
```

**Example**:
```python
status = PoolStatus(
    total_proxies=1000,
    healthy_count=950,
    unhealthy_count=30,
    checking_count=15,
    recovering_count=5,
    unknown_count=0,
    permanently_failed_count=0,
    last_updated=datetime.now(timezone.utc)
)
# status.health_percentage = 95.0
# status.is_degraded = False
```

---

### 5. SourceStatus (Pydantic Model)

**Purpose**: Health statistics for a specific proxy source

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `source_name` | `str` | Yes | - | Proxy source identifier |
| `total` | `int` | Yes | - | Total proxies from this source |
| `healthy` | `int` | Yes | - | Healthy proxies |
| `unhealthy` | `int` | Yes | - | Unhealthy proxies |
| `health_percentage` | `float` | No | - | Computed: healthy/total * 100 |
| `last_check_time` | `datetime` | No | `None` | Last check for this source |
| `avg_response_time_ms` | `float` | No | `None` | Average response time |

---

### 6. HealthCheckConfig (Pydantic Model)

**Purpose**: Configuration for health check behavior

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `check_interval_seconds` | `int` | No | `300` | Seconds between checks (5 min default) |
| `check_timeout_seconds` | `int` | No | `10` | Health check request timeout |
| `failure_threshold` | `int` | No | `3` | Consecutive failures before unhealthy |
| `recovery_cooldown_base` | `int` | No | `60` | Base cooldown in seconds (exponential backoff) |
| `max_recovery_attempts` | `int` | No | `5` | Max recovery retries before permanent failure |
| `check_url` | `str` | No | `"http://httpbin.org/status/200"` | Target URL for health checks |
| `expected_status_codes` | `list[int]` | No | `[200]` | HTTP status codes considered healthy |
| `thread_pool_size` | `int` | No | `100` | Max concurrent health checks |
| `enable_jitter` | `bool` | No | `True` | Add ±10% jitter to check intervals |
| `history_retention_hours` | `int` | No | `24` | How long to keep health history |

**Validation**:
```python
@field_validator("check_interval_seconds")
def validate_interval(cls, v: int) -> int:
    if v < 10:
        raise ValueError("Check interval must be at least 10 seconds")
    return v

@field_validator("failure_threshold")
def validate_threshold(cls, v: int) -> int:
    if v < 1:
        raise ValueError("Failure threshold must be at least 1")
    return v
```

---

### 7. ProxyHealthState (Extension to Proxy Model)

**Purpose**: Health-related fields added to existing Proxy model

**New Fields** (added to `proxywhirl/models.py:Proxy`):

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `health_status` | `HealthStatus` | No | `UNKNOWN` | Current health status |
| `last_health_check` | `datetime` | No | `None` | Last check timestamp |
| `consecutive_failures` | `int` | No | `0` | Count of sequential failures |
| `consecutive_successes` | `int` | No | `0` | Count of sequential successes |
| `recovery_attempt` | `int` | No | `0` | Current recovery attempt number |
| `next_check_time` | `datetime` | No | `None` | When next check scheduled |
| `last_health_error` | `str` | No | `None` | Last error message |
| `total_checks` | `int` | No | `0` | Lifetime check count |
| `total_failures` | `int` | No | `0` | Lifetime failure count |

**Example**:
```python
proxy = Proxy(
    url="http://proxy1.example.com:8080",
    source="free-proxy-list",
    health_status=HealthStatus.HEALTHY,
    last_health_check=datetime.now(timezone.utc),
    consecutive_failures=0,
    consecutive_successes=5,
    recovery_attempt=0,
    total_checks=100,
    total_failures=5
)
```

---

## Database Schema

### Extended cache_entries Table (L3 SQLite)

```sql
-- Extends existing table from 005-caching
ALTER TABLE cache_entries ADD COLUMN health_status TEXT DEFAULT 'unknown';
ALTER TABLE cache_entries ADD COLUMN last_health_check REAL;
ALTER TABLE cache_entries ADD COLUMN consecutive_failures INTEGER DEFAULT 0;
ALTER TABLE cache_entries ADD COLUMN consecutive_successes INTEGER DEFAULT 0;
ALTER TABLE cache_entries ADD COLUMN recovery_attempt INTEGER DEFAULT 0;
ALTER TABLE cache_entries ADD COLUMN next_check_time REAL;
ALTER TABLE cache_entries ADD COLUMN last_health_error TEXT;
ALTER TABLE cache_entries ADD COLUMN total_checks INTEGER DEFAULT 0;
ALTER TABLE cache_entries ADD COLUMN total_failures INTEGER DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_health_status ON cache_entries(health_status);
CREATE INDEX IF NOT EXISTS idx_next_check_time ON cache_entries(next_check_time);
```

### New health_history Table

```sql
CREATE TABLE IF NOT EXISTS health_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proxy_key TEXT NOT NULL,
    proxy_url TEXT NOT NULL,
    check_time REAL NOT NULL,
    status TEXT NOT NULL,
    response_time_ms REAL,
    status_code INTEGER,
    error_message TEXT,
    check_url TEXT NOT NULL,
    FOREIGN KEY (proxy_key) REFERENCES cache_entries(key) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_health_history_proxy ON health_history(proxy_key);
CREATE INDEX IF NOT EXISTS idx_health_history_time ON health_history(check_time);
CREATE INDEX IF NOT EXISTS idx_health_history_status ON health_history(status);
```

---

## Relationships

### Entity Relationship Diagram

```
┌─────────────────┐
│     Proxy       │
│  (models.py)    │
├─────────────────┤
│ + health_status │◄────┐
│ + last_check    │     │
│ + failure_count │     │
└─────────────────┘     │
         │              │
         │              │
         ▼              │
┌─────────────────┐     │
│ CacheEntry      │     │
│ (cache_models)  │     │
├─────────────────┤     │
│ (inherits from  │     │
│  Proxy fields)  │     │
└─────────────────┘     │
         │              │
         │              │
         ▼              │
┌─────────────────┐     │
│ health_history  │     │
│   (SQLite)      │     │
├─────────────────┤     │
│ + check_time    │─────┘
│ + status        │
│ + response_time │
│ + error_message │
└─────────────────┘
         │
         │
         ▼
┌─────────────────┐
│ HealthChecker   │
│  (health.py)    │
├─────────────────┤
│ + check_proxy() │────► HealthCheckResult
│ + get_status()  │────► PoolStatus
└─────────────────┘
         │
         │
         ▼
┌─────────────────┐
│ HealthEvent     │
│  (emitted)      │
├─────────────────┤
│ + event_type    │
│ + proxy_url     │
│ + status change │
└─────────────────┘
```

---

## Validation Rules

### Cross-Entity Constraints

1. **Health Status Consistency**:
   - `health_status` in Proxy must match `health_status` in corresponding CacheEntry
   - Updates to either must trigger sync

2. **Failure Threshold Logic**:
   ```python
   if proxy.consecutive_failures >= config.failure_threshold:
       proxy.health_status = HealthStatus.UNHEALTHY
       emit_event(HealthEvent(event_type="proxy_down", ...))
   ```

3. **Recovery Backoff**:
   ```python
   cooldown = config.recovery_cooldown_base * (2 ** proxy.recovery_attempt)
   proxy.next_check_time = now + timedelta(seconds=cooldown)
   ```

4. **History Retention**:
   ```sql
   DELETE FROM health_history 
   WHERE check_time < (unixepoch('now') - (config.history_retention_hours * 3600));
   ```

5. **Pool Status Integrity**:
   ```python
   assert status.total_proxies == (
       status.healthy_count + 
       status.unhealthy_count + 
       status.checking_count + 
       status.recovering_count + 
       status.unknown_count +
       status.permanently_failed_count
   )
   ```

---

## Type Safety

All models use Pydantic v2 with strict validation:

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional

class HealthCheckResult(BaseModel):
    proxy_url: str = Field(..., min_length=1)
    check_time: datetime
    status: HealthStatus
    response_time_ms: Optional[float] = Field(None, ge=0)
    status_code: Optional[int] = Field(None, ge=100, le=599)
    error_message: Optional[str] = None
    check_url: str = Field(..., min_length=1)
    
    @field_validator("check_time")
    @classmethod
    def validate_timezone(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("check_time must be timezone-aware")
        return v
    
    model_config = {"frozen": True}  # Immutable after creation
```

---

## Migration Strategy

### Phase 1: Schema Extension (Non-Breaking)

```python
# In cache_tiers.py SQLiteCacheTier._init_db()
def _add_health_columns(self) -> None:
    """Add health monitoring columns if they don't exist."""
    conn = sqlite3.connect(str(self.db_path))
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(cache_entries)")
    columns = {row[1] for row in cursor.fetchall()}
    
    if "health_status" not in columns:
        cursor.execute("ALTER TABLE cache_entries ADD COLUMN health_status TEXT DEFAULT 'unknown'")
        cursor.execute("ALTER TABLE cache_entries ADD COLUMN last_health_check REAL")
        # ... add other columns
        conn.commit()
    
    conn.close()
```

### Phase 2: Proxy Model Extension

```python
# In models.py
from proxywhirl.health_models import HealthStatus

class Proxy(BaseModel):
    # Existing fields...
    url: str
    source: str
    
    # NEW: Health monitoring fields
    health_status: HealthStatus = HealthStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0
    # ... other health fields
```

---

## Examples

### Creating a Health Check Result

```python
from proxywhirl.health_models import HealthCheckResult, HealthStatus
from datetime import datetime, timezone

result = HealthCheckResult(
    proxy_url="http://proxy1.example.com:8080",
    check_time=datetime.now(timezone.utc),
    status=HealthStatus.HEALTHY,
    response_time_ms=156.3,
    status_code=200,
    check_url="http://httpbin.org/status/200"
)
```

### Emitting a Health Event

```python
from proxywhirl.health_models import HealthEvent, HealthStatus

event = HealthEvent(
    event_type="proxy_down",
    proxy_url="http://proxy1.example.com:8080",
    timestamp=datetime.now(timezone.utc),
    previous_status=HealthStatus.HEALTHY,
    new_status=HealthStatus.UNHEALTHY,
    failure_count=3
)

# Trigger notification callback
if health_checker.on_event:
    health_checker.on_event(event)
```

### Querying Pool Status

```python
from proxywhirl.health import HealthChecker

checker = HealthChecker(config=health_config)
status = checker.get_pool_status()

print(f"Pool Health: {status.health_percentage:.1f}%")
print(f"Healthy: {status.healthy_count}/{status.total_proxies}")
print(f"Degraded: {status.is_degraded}")

# By source
for source_name, source_status in status.by_source.items():
    print(f"{source_name}: {source_status.health_percentage:.1f}%")
```

---

## Performance Considerations

### Indexing Strategy

- `health_status`: Fast filtering for healthy/unhealthy proxies
- `next_check_time`: Efficient query for proxies due for check
- `check_time` in history: Time-range queries for history retention

### Caching

- Pool status cached for 1 second (reduces query load)
- Health state changes invalidate cache immediately
- Read-heavy workload optimized with RLock

### Memory Usage

- Health history bounded to 24 hours (auto-cleanup)
- Pool status computed on-demand (not stored)
- Event callbacks non-blocking (fire-and-forget)
