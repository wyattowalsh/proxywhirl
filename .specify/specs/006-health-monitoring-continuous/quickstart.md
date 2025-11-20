# Quickstart: Continuous Health Monitoring

**Feature**: 006-health-monitoring-continuous  
**Purpose**: Get started with automatic proxy health monitoring in under 5 minutes  
**Prerequisites**: proxywhirl v0.2.0+, Python 3.9+

---

## Installation

```bash
# Health monitoring is built-in, no extra dependencies required
uv add proxywhirl>=0.2.0

# Or if already installed, sync to latest
uv sync
```

---

## Basic Usage (30 seconds)

```python
from proxywhirl import ProxyRotator
from proxywhirl.health import HealthChecker

# 1. Create a proxy rotator
rotator = ProxyRotator()
rotator.add_proxy("http://proxy1.example.com:8080")
rotator.add_proxy("http://proxy2.example.com:8080")

# 2. Create health checker (reuses rotator's cache)
checker = HealthChecker(cache=rotator.cache)

# 3. Register proxies for monitoring
for proxy in rotator._proxies:  # Internal API shown for clarity
    checker.add_proxy(proxy)

# 4. Start background monitoring
checker.start()

# 5. Query pool health
status = checker.get_pool_status()
print(f"Pool Health: {status.health_percentage:.1f}%")
print(f"Healthy: {status.healthy_count}/{status.total_proxies}")

# 6. Cleanup on exit
checker.stop()
```

**Output**:
```
Pool Health: 85.0%
Healthy: 17/20
```

---

## User Story Walkthroughs

### US1 (P1): Background Health Checks

**Scenario**: Automatically check all proxies every 5 minutes.

```python
from proxywhirl.health import HealthChecker
from proxywhirl.health_models import HealthCheckConfig

# Configure check interval
config = HealthCheckConfig(
    check_interval_seconds=300,  # 5 minutes
    check_timeout_seconds=10,
    failure_threshold=3
)

checker = HealthChecker(config=config)

# Add proxies from file
with open("proxies.txt") as f:
    for line in f:
        proxy_url = line.strip()
        checker.add_proxy(Proxy(url=proxy_url, source="file"))

# Start monitoring (runs forever in background)
checker.start()
print("Health monitoring active!")

# ... your application continues running ...

# When shutting down
checker.stop(timeout=30.0)
```

---

### US2 (P2): Real-time Status Queries

**Scenario**: Check if a specific proxy is healthy before using it.

```python
from proxywhirl.health import HealthChecker
from proxywhirl.health_models import HealthStatus

checker = HealthChecker()
checker.start()

# Wait for initial checks to complete (or query immediately)
proxy_url = "http://proxy1.example.com:8080"

# Get proxy-specific status
state = checker.get_proxy_status(proxy_url)

if state and state.health_status == HealthStatus.HEALTHY:
    print(f"✅ Proxy is healthy (checked {state.last_health_check})")
    print(f"   Response time: {state.response_time_ms}ms")
else:
    print(f"❌ Proxy is unhealthy or unknown")

# Get overall pool metrics
pool = checker.get_pool_status()
print(f"\nPool: {pool.healthy_count} healthy, {pool.unhealthy_count} unhealthy")
```

**Output**:
```
✅ Proxy is healthy (checked 2024-01-15 14:32:05)
   Response time: 234ms

Pool: 42 healthy, 3 unhealthy
```

---

### US3 (P2): Dead Proxy Detection

**Scenario**: Automatically detect and mark failed proxies within 1 minute.

```python
from proxywhirl.health import HealthChecker
from proxywhirl.health_models import HealthCheckConfig, HealthStatus

# Aggressive failure detection
config = HealthCheckConfig(
    check_interval_seconds=20,   # Check every 20 seconds
    check_timeout_seconds=5,     # Fast timeout
    failure_threshold=2          # Mark dead after 2 failures
)

checker = HealthChecker(config=config)

# Add proxy that will fail
dead_proxy = Proxy(url="http://dead-proxy.example.com:8080", source="test")
checker.add_proxy(dead_proxy)
checker.start()

# Wait for checks to run
import time
time.sleep(60)

# Check if marked as unhealthy
state = checker.get_proxy_status(dead_proxy.url)
if state.health_status in [HealthStatus.UNHEALTHY, HealthStatus.PERMANENTLY_FAILED]:
    print(f"✅ Dead proxy detected in {state.consecutive_failures * 20}s")
    print(f"   Status: {state.health_status}")
```

**Expected**: Dead proxy detected within 40-60 seconds (2 failures × 20s interval).

---

### US4 (P2): Health Event Notifications

**Scenario**: Receive alerts when proxies go down or recover.

```python
from proxywhirl.health import HealthChecker
from proxywhirl.health_models import HealthEvent, HealthStatus

def handle_health_event(event: HealthEvent) -> None:
    """Custom notification handler"""
    if event.event_type == "proxy_down":
        print(f"🚨 ALERT: {event.proxy_url} is DOWN")
        print(f"   Status: {event.previous_status} → {event.new_status}")
        print(f"   Failures: {event.failure_count}")
        # Send webhook, email, Slack message, etc.
    
    elif event.event_type == "proxy_recovered":
        print(f"✅ RECOVERED: {event.proxy_url} is back online")
    
    elif event.event_type == "pool_degraded":
        print(f"⚠️  WARNING: Pool health below 50%")
        metadata = event.metadata
        print(f"   Healthy: {metadata.get('healthy_count')}/{metadata.get('total')}")

# Register callback
checker = HealthChecker(on_event=handle_health_event)
checker.start()

# Notifications logged automatically as health changes occur
```

**Output (when proxy fails)**:
```
🚨 ALERT: http://proxy3.example.com:8080 is DOWN
   Status: HEALTHY → UNHEALTHY
   Failures: 3
```

---

### US5 (P3): Historical Health Data

**Scenario**: Analyze proxy reliability over the past 24 hours.

```python
from proxywhirl.health import HealthChecker

checker = HealthChecker()
checker.start()

# Get 24-hour history for a proxy
proxy_url = "http://proxy1.example.com:8080"
history = checker.get_health_history(proxy_url, hours=24)

# Calculate uptime percentage
total_checks = len(history)
successful_checks = sum(1 for r in history if r.status == HealthStatus.HEALTHY)
uptime_pct = (successful_checks / total_checks * 100) if total_checks > 0 else 0.0

print(f"Proxy: {proxy_url}")
print(f"Checks: {total_checks} in 24 hours")
print(f"Uptime: {uptime_pct:.2f}%")
print(f"Avg response: {sum(r.response_time_ms or 0 for r in history) / total_checks:.0f}ms")

# Recent failures
recent_failures = [r for r in history[:10] if r.status != HealthStatus.HEALTHY]
if recent_failures:
    print(f"\nRecent failures:")
    for failure in recent_failures:
        print(f"  - {failure.check_time}: {failure.error_message}")
```

**Output**:
```
Proxy: http://proxy1.example.com:8080
Checks: 288 in 24 hours
Uptime: 97.22%
Avg response: 215ms

Recent failures:
  - 2024-01-15 14:15:03: Connection timeout
```

---

### US6 (P3): Manual Health Checks

**Scenario**: Verify proxy health before adding to pool.

```python
from proxywhirl.health import HealthChecker
from proxywhirl.models import Proxy

checker = HealthChecker()

# Manual check BEFORE adding to pool
candidate_proxy = Proxy(url="http://new-proxy.example.com:8080", source="manual")
result = checker.check_proxy(candidate_proxy)

if result.status == HealthStatus.HEALTHY:
    print(f"✅ Proxy verified (response: {result.response_time_ms}ms)")
    checker.add_proxy(candidate_proxy)  # Add to monitoring
else:
    print(f"❌ Proxy failed: {result.error_message}")
    # Don't add to pool
```

---

## Integration with ProxyRotator

**Recommended Pattern**: Use health monitoring to automatically filter dead proxies from rotation.

```python
from proxywhirl import ProxyRotator
from proxywhirl.health import HealthChecker
from proxywhirl.health_models import HealthStatus

rotator = ProxyRotator()
checker = HealthChecker(cache=rotator.cache)

# Add proxies
for url in ["http://proxy1.com:8080", "http://proxy2.com:8080"]:
    rotator.add_proxy(url)

# Register all with health checker
for proxy in rotator._proxies:
    checker.add_proxy(proxy)

checker.start()

# Get next proxy, excluding unhealthy ones
def get_healthy_proxy():
    """Returns only healthy proxies"""
    pool = checker.get_pool_status()
    if pool.healthy_count == 0:
        raise RuntimeError("No healthy proxies available")
    
    # Filter by health status (future: built-in to rotator)
    for _ in range(pool.total_proxies):
        proxy = rotator.get_proxy()
        state = checker.get_proxy_status(proxy.url)
        if state and state.health_status == HealthStatus.HEALTHY:
            return proxy
    
    raise RuntimeError("No healthy proxies after rotation")

# Usage
try:
    proxy = get_healthy_proxy()
    print(f"Using healthy proxy: {proxy.url}")
except RuntimeError as e:
    print(f"Error: {e}")
```

---

## Configuration Examples

### Production Settings

```python
from proxywhirl.health_models import HealthCheckConfig

config = HealthCheckConfig(
    check_interval_seconds=600,   # Check every 10 minutes
    check_timeout_seconds=15,     # Allow 15s for slow proxies
    failure_threshold=5,          # Require 5 consecutive failures
    recovery_cooldown_base=300,   # Start recovery at 5 minutes
    max_recovery_attempts=10,     # Try recovery 10 times
    thread_pool_size=50,          # Limit concurrent checks
    enable_jitter=True,           # Prevent thundering herd
    history_retention_hours=168   # Keep 7 days of history
)
```

### Development/Testing Settings

```python
config = HealthCheckConfig(
    check_interval_seconds=10,    # Fast checks for debugging
    check_timeout_seconds=3,      # Short timeout
    failure_threshold=1,          # Fail immediately
    recovery_cooldown_base=5,     # Quick recovery attempts
    thread_pool_size=10
)
```

---

## Testing Your Integration

```python
# tests/test_health_integration.py
import pytest
from proxywhirl.health import HealthChecker
from proxywhirl.health_models import HealthCheckConfig, HealthStatus
from proxywhirl.models import Proxy

def test_health_checker_basic():
    """Test basic health monitoring workflow"""
    checker = HealthChecker()
    
    # Add test proxy
    proxy = Proxy(url="http://httpbin.org/delay/0", source="test")
    checker.add_proxy(proxy)
    
    # Manual check
    result = checker.check_proxy(proxy)
    assert result.status == HealthStatus.HEALTHY
    assert result.response_time_ms > 0

def test_health_checker_background():
    """Test background monitoring"""
    config = HealthCheckConfig(check_interval_seconds=1)
    checker = HealthChecker(config=config)
    
    proxy = Proxy(url="http://httpbin.org/status/200", source="test")
    checker.add_proxy(proxy)
    
    checker.start()
    time.sleep(2)  # Wait for checks
    
    status = checker.get_pool_status()
    assert status.healthy_count >= 1
    
    checker.stop()
```

---

## Performance Tuning

**Goal**: Monitor 10,000 proxies with <5% CPU overhead (SC-003).

```python
# Calculate optimal thread pool size
num_proxies = 10_000
check_interval = 300  # 5 minutes
check_duration = 5    # Average check time (seconds)

# Proxies checked per second
checks_per_second = num_proxies / check_interval

# Required workers (with 2x buffer)
thread_pool_size = int(checks_per_second * check_duration * 2)

config = HealthCheckConfig(
    thread_pool_size=min(thread_pool_size, 500),  # Cap at 500
    enable_jitter=True  # Spread checks over interval
)
```

---

## Common Pitfalls

### ❌ Don't: Forget to stop() on shutdown

```python
# BAD: Threads never exit cleanly
checker = HealthChecker()
checker.start()
# ... application exits without checker.stop()
```

### ✅ Do: Use context managers or cleanup handlers

```python
# GOOD: Guaranteed cleanup
checker = HealthChecker()
try:
    checker.start()
    # ... application logic ...
finally:
    checker.stop(timeout=30.0)
```

### ❌ Don't: Call check_proxy() in tight loops

```python
# BAD: Synchronous checks block thread
for proxy in proxies:
    result = checker.check_proxy(proxy)  # Slow!
```

### ✅ Do: Use background monitoring + status queries

```python
# GOOD: Async monitoring with fast queries
checker.start()  # Background checks
for proxy in proxies:
    state = checker.get_proxy_status(proxy.url)  # <1ms
```

---

## Troubleshooting

**Problem**: Proxies marked unhealthy but manually work fine.

**Solution**: Adjust timeout and failure threshold.

```python
config = HealthCheckConfig(
    check_timeout_seconds=30,  # Increase timeout
    failure_threshold=10       # Require more failures
)
```

**Problem**: High false positive rate on slow connections.

**Solution**: Enable jitter and increase intervals.

```python
config = HealthCheckConfig(
    enable_jitter=True,         # Spread checks over time
    check_interval_seconds=600  # Check less frequently
)
```

**Problem**: Health checks not running.

**Solution**: Verify start() was called and no exceptions in logs.

```python
import logging
logging.basicConfig(level=logging.DEBUG)

checker = HealthChecker()
checker.start()

# Check if threads running
status = checker.get_pool_status()
print(f"Last updated: {status.last_updated}")  # Should be recent
```

---

## Next Steps

- Read full specification: `.specify/specs/006-health-monitoring-continuous/spec.md`
- Review data model: `.specify/specs/006-health-monitoring-continuous/data-model.md`
- API reference: `.specify/specs/006-health-monitoring-continuous/contracts/health-api.json`
- Integration guide: `proxywhirl/README.md`

---

**Questions?** Check logs with `loguru` at DEBUG level for detailed health check events.
