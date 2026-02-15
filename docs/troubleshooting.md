# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with ProxyWhirl. Use the error codes and solutions below to quickly fix problems.

---

## Table of Contents

- [Error Codes Reference](#error-codes-reference)
- [Common Issues](#common-issues)
- [Debugging Tips](#debugging-tips)
- [FAQ](#faq)
- [Getting Help](#getting-help)

---

## Error Codes Reference

ProxyWhirl uses structured error codes for programmatic error handling. All exceptions inherit from `ProxyWhirlError` and include metadata for debugging.

### PROXY_POOL_EMPTY

**Error Class:** `ProxyPoolEmptyError`
**Retry Recommended:** No

**Cause:** No proxies are available in the pool for selection.

**Solutions:**
1. **Add proxies to the pool:**
   ```python
   rotator.add_proxy("http://proxy1.example.com:8080")
   ```

2. **Enable auto-fetch from sources:**
   ```bash
   proxywhirl fetch
   ```

3. **Load from our free proxy lists:**
   ```python
   import httpx
   response = httpx.get("https://your-docs-site.com/proxy-lists/http.txt")
   for proxy in response.text.strip().split("\n"):
       rotator.add_proxy(f"http://{proxy}")
   ```

4. **Check if proxies were filtered out by health checks:**
   ```bash
   proxywhirl pool list
   proxywhirl health
   ```

**Related Code:**
- [`proxywhirl/exceptions.py#L152-L167`](../proxywhirl/exceptions.py)
- [`proxywhirl/rotator.py`](../proxywhirl/rotator.py)

---

### PROXY_VALIDATION_FAILED

**Error Class:** `ProxyValidationError`
**Retry Recommended:** No

**Cause:** Proxy URL or configuration is invalid.

**Common Issues:**
- Invalid URL format (missing scheme, port, or hostname)
- Unsupported protocol (only `http://`, `https://`, `socks4://`, `socks5://` are supported)
- Improperly encoded credentials

**Solutions:**
1. **Verify URL format:**
   ```python
   # ✅ Correct formats
   "http://proxy.example.com:8080"
   "socks5://user:pass@proxy.example.com:1080"

   # ❌ Invalid formats
   "proxy.example.com:8080"  # Missing scheme
   "ftp://proxy.example.com:8080"  # Unsupported protocol
   ```

2. **Check credential encoding:**
   ```python
   from urllib.parse import quote
   username = quote("user@domain.com")
   password = quote("p@ssw0rd!")
   proxy_url = f"http://{username}:{password}@proxy.example.com:8080"
   ```

3. **Validate using CLI:**
   ```bash
   proxywhirl pool test http://proxy.example.com:8080
   ```

**Related Code:**
- [`proxywhirl/exceptions.py#L134-L149`](../proxywhirl/exceptions.py)
- [`proxywhirl/config.py#L132-L141`](../proxywhirl/config.py)

---

### PROXY_CONNECTION_FAILED

**Error Class:** `ProxyConnectionError`
**Retry Recommended:** Yes

**Cause:** Unable to establish connection through the proxy.

**Common Issues:**
- Proxy server is down or unreachable
- Network connectivity issues
- Firewall blocking proxy ports
- Proxy doesn't support the target protocol

**Solutions:**
1. **Test proxy connectivity:**
   ```bash
   proxywhirl pool test http://proxy.example.com:8080
   ```

2. **Check network accessibility:**
   ```bash
   curl -x http://proxy.example.com:8080 https://httpbin.org/ip
   ```

3. **Increase timeout:**
   ```python
   rotator = ProxyWhirl(
       proxies=["http://proxy1:8080"],
       timeout=60  # Default is 30 seconds
   )
   ```

4. **Verify proxy supports target protocol:**
   - HTTP proxies cannot tunnel HTTPS CONNECT requests if not configured
   - SOCKS proxies may have protocol restrictions

5. **Enable verbose logging:**
   ```python
   from loguru import logger
   logger.add("debug.log", level="DEBUG")
   ```

**Related Code:**
- [`proxywhirl/exceptions.py#L170-L186`](../proxywhirl/exceptions.py)
- [`proxywhirl/cli.py#L419-L433`](../proxywhirl/cli.py)

---

### PROXY_AUTH_FAILED

**Error Class:** `ProxyAuthenticationError`
**Retry Recommended:** No

**Cause:** Proxy authentication failed.

**Common Issues:**
- Incorrect username or password
- Credentials expired
- Proxy requires different auth method (e.g., IP whitelist instead of user/pass)

**Solutions:**
1. **Verify credentials:**
   ```python
   from pydantic import SecretStr
   proxy = Proxy(
       url="http://proxy.example.com:8080",
       username=SecretStr("correct_username"),
       password=SecretStr("correct_password")
   )
   ```

2. **Test with curl:**
   ```bash
   curl -x http://user:pass@proxy.example.com:8080 https://httpbin.org/ip
   ```

3. **Check if proxy uses IP authentication:**
   - Some proxies whitelist IPs instead of using credentials
   - Contact your proxy provider to verify authentication method

4. **Ensure credentials aren't expired:**
   - Rotating residential proxies may have time-limited credentials

**Related Code:**
- [`proxywhirl/exceptions.py#L189-L205`](../proxywhirl/exceptions.py)

---

### PROXY_FETCH_FAILED

**Error Class:** `ProxyFetchError`
**Retry Recommended:** Yes

**Cause:** Fetching proxies from external sources failed.

**Common Issues:**
- Source URL is unreachable
- API credentials invalid or expired
- Response format doesn't match expectations
- Rate limit hit

**Solutions:**
1. **Test sources manually:**
   ```bash
   proxywhirl sources --validate
   ```

2. **Check specific source:**
   ```bash
   curl https://api.proxyscrape.com/v2/?request=get&protocol=http
   ```

3. **Review source health:**
   ```bash
   proxywhirl sources -v -f  # Fail on unhealthy sources
   ```

4. **Use offline mode with cached proxies:**
   ```python
   rotator = ProxyWhirl(
       proxies=[],  # Empty, will load from storage
       storage_path="proxywhirl.db"
   )
   ```

**Related Code:**
- [`proxywhirl/exceptions.py#L208-L222`](../proxywhirl/exceptions.py)
- [`proxywhirl/cli.py#L1117-L1552`](../proxywhirl/cli.py)
- [`proxywhirl/sources.py`](../proxywhirl/sources.py)

---

### PROXY_STORAGE_FAILED

**Error Class:** `ProxyStorageError`
**Retry Recommended:** No

**Cause:** Proxy storage operations failed.

**Common Issues:**
- Insufficient file system permissions
- Disk space full
- Database corruption
- Path doesn't exist or isn't writable

**Solutions:**
1. **Check file permissions:**
   ```bash
   ls -la proxywhirl.db
   chmod 644 proxywhirl.db
   ```

2. **Verify disk space:**
   ```bash
   df -h .
   ```

3. **Check directory is writable:**
   ```bash
   mkdir -p .cache/proxies
   chmod 755 .cache/proxies
   ```

4. **Reinitialize database:**
   ```bash
   rm proxywhirl.db
   proxywhirl fetch --save-db
   ```

**Related Code:**
- [`proxywhirl/exceptions.py#L225-L241`](../proxywhirl/exceptions.py)
- [`proxywhirl/storage.py`](../proxywhirl/storage.py)

---

### CACHE_CORRUPTED

**Error Class:** `CacheCorruptionError`
**Retry Recommended:** No

**Cause:** Cache data is corrupted and cannot be recovered.

**Common Issues:**
- Disk corruption
- Interrupted write operation
- Version incompatibility after upgrade
- Encryption key mismatch

**Solutions:**
1. **Clear cache:**
   ```bash
   rm -rf .cache/proxies/*
   rm -rf .cache/db/proxywhirl.db
   ```

2. **Reinitialize cache:**
   ```python
   from proxywhirl.cache import CacheManager
   cache = CacheManager(
       l1_max_entries=1000,
       l2_dir=".cache/proxies",
       l3_db_path=".cache/db/proxywhirl.db"
   )
   await cache.clear()  # Clear all tiers
   ```

3. **Check for disk errors:**
   ```bash
   # macOS
   diskutil verifyVolume /

   # Linux
   sudo fsck /dev/sda1
   ```

**Related Code:**
- [`proxywhirl/exceptions.py#L244-L259`](../proxywhirl/exceptions.py)
- [`proxywhirl/cache/`](../proxywhirl/cache/)

---

### CACHE_STORAGE_FAILED

**Error Class:** `CacheStorageError`
**Retry Recommended:** Yes

**Cause:** Cache storage backend is unavailable.

**Common Issues:**
- Redis/Memcached server down
- Network connectivity issues
- Invalid credentials
- Backend overloaded

**Solutions:**
1. **Verify cache backend is running:**
   ```bash
   # Redis
   redis-cli ping

   # Check connection
   telnet localhost 6379
   ```

2. **Disable external cache, use local:**
   ```python
   # Use file-based L2/L3 cache instead
   config = CLIConfig(
       cache_enabled=True,
       cache_l2_dir=".cache/proxies",
       cache_l3_db_path=".cache/db/proxywhirl.db"
   )
   ```

3. **Check credentials:**
   ```bash
   export REDIS_PASSWORD="your-password"
   ```

**Related Code:**
- [`proxywhirl/exceptions.py#L262-L276`](../proxywhirl/exceptions.py)

---

### CACHE_VALIDATION_FAILED

**Error Class:** `CacheValidationError`
**Retry Recommended:** No

**Cause:** Cache entry fails validation.

**Common Issues:**
- Schema version mismatch after upgrade
- Invalid data types
- Missing required fields

**Solutions:**
1. **Clear cache and rebuild:**
   ```bash
   rm -rf .cache/
   proxywhirl fetch
   ```

2. **Check ProxyWhirl version:**
   ```bash
   pip show proxywhirl
   pip install --upgrade proxywhirl
   ```

**Related Code:**
- [`proxywhirl/exceptions.py#L279-L292`](../proxywhirl/exceptions.py)
- [`proxywhirl/cache/models.py`](../proxywhirl/cache/models.py)

---

### TIMEOUT

**Error Code:** `TIMEOUT`
**Retry Recommended:** Yes

**Cause:** Request timed out.

**Common Issues:**
- Slow proxy server
- Network congestion
- Target server slow to respond
- Timeout value too low

**Solutions:**
1. **Increase timeout:**
   ```python
   rotator = ProxyWhirl(
       proxies=["http://proxy1:8080"],
       timeout=60  # Increase from default 30s
   )
   ```

2. **Configure via CLI:**
   ```bash
   proxywhirl config set timeout 60
   ```

3. **Per-request timeout:**
   ```bash
   proxywhirl request --timeout 90 https://example.com
   ```

4. **Check proxy latency:**
   ```bash
   proxywhirl health --target-url https://httpbin.org/ip
   ```

**Related Code:**
- [`proxywhirl/exceptions.py#L25`](../proxywhirl/exceptions.py)
- [`proxywhirl/cli.py#L428-L431`](../proxywhirl/cli.py)

---

### NETWORK_ERROR

**Error Code:** `NETWORK_ERROR`
**Retry Recommended:** Yes

**Cause:** Generic network error.

**Common Issues:**
- DNS resolution failed
- Network interface down
- ISP blocking connections
- Firewall rules

**Solutions:**
1. **Test network connectivity:**
   ```bash
   ping 8.8.8.8
   curl https://httpbin.org/ip
   ```

2. **Check DNS:**
   ```bash
   nslookup proxy.example.com
   dig proxy.example.com
   ```

3. **Verify firewall rules:**
   ```bash
   # macOS
   sudo pfctl -sr

   # Linux (iptables)
   sudo iptables -L
   ```

**Related Code:**
- [`proxywhirl/exceptions.py#L26`](../proxywhirl/exceptions.py)

---

### INVALID_CONFIGURATION

**Error Code:** `INVALID_CONFIGURATION`
**Retry Recommended:** No

**Cause:** Configuration file or settings are invalid.

**Common Issues:**
- Malformed TOML syntax
- Invalid field values
- Missing required fields
- Type mismatch

**Solutions:**
1. **Validate configuration:**
   ```bash
   proxywhirl config show
   ```

2. **Reinitialize config:**
   ```bash
   proxywhirl config init
   ```

3. **Check TOML syntax:**
   ```bash
   # Use a TOML validator
   python -c "import tomllib; tomllib.load(open('.proxywhirl.toml', 'rb'))"
   ```

4. **Review allowed values:**
   - `rotation_strategy`: `round-robin`, `random`, `weighted`, `least-used`
   - `default_format`: `text`, `json`, `csv` (`human` and `table` are deprecated aliases for `text`)
   - `storage_backend`: `file`, `sqlite`, `memory`

**Related Code:**
- [`proxywhirl/exceptions.py#L27`](../proxywhirl/exceptions.py)
- [`proxywhirl/config.py#L195-L211`](../proxywhirl/config.py)

---

## Common Issues

### Issue: All proxies marked as unhealthy

**Symptoms:**
- `ProxyPoolEmptyError` after some usage
- Health check shows all proxies failed

**Diagnosis:**
```bash
proxywhirl health --verbose
proxywhirl pool list
```

**Solutions:**

1. **Check if proxies are actually dead:**
   ```bash
   for proxy in $(cat proxies.txt); do
       curl -x http://$proxy https://httpbin.org/ip -m 5 || echo "$proxy FAILED"
   done
   ```

2. **Lower health check sensitivity:**
   ```python
   from proxywhirl import ProxyWhirl
   from proxywhirl.circuit_breaker import CircuitBreaker

   # Increase failure threshold
   rotator = ProxyWhirl(
       proxies=[...],
       circuit_breaker=CircuitBreaker(
           failure_threshold=10,  # Default is 5
           recovery_timeout=60    # Retry after 1 min
       )
   )
   ```

3. **Use more lenient target URL:**
   ```bash
   # Instead of a strict endpoint
   proxywhirl health --target-url https://example.com
   ```

4. **Disable health checks temporarily:**
   ```python
   rotator = ProxyWhirl(
       proxies=[...],
       health_check_interval=0  # Disable automatic checks
   )
   ```

---

### Issue: Rate limiting / 429 errors

**Symptoms:**
- HTTP 429 Too Many Requests
- Target blocking your requests

**Diagnosis:**
```python
from loguru import logger
logger.add("requests.log", level="DEBUG")
# Check request frequency in logs
```

**Solutions:**

1. **Enable rate limiting:**
   ```python
   from proxywhirl.rate_limiting import RateLimiter

   rate_limiter = RateLimiter(
       max_requests_per_minute=30,
       max_requests_per_hour=500,
       burst_size=10
   )

   rotator = ProxyWhirl(
       proxies=[...],
       rate_limiter=rate_limiter
   )
   ```

2. **Add delays between requests:**
   ```python
   import time
   for url in urls:
       response = rotator.get(url)
       time.sleep(2)  # 2 second delay
   ```

3. **Rotate proxies more aggressively:**
   ```python
   # Use random strategy instead of round-robin
   rotator = ProxyWhirl(
       proxies=[...],
       strategy="random"
   )
   ```

4. **Use session persistence:**
   ```python
   from proxywhirl.strategies import SessionPersistenceStrategy

   rotator = ProxyWhirl(
       proxies=[...],
       strategy=SessionPersistenceStrategy(
           session_duration=300  # 5 minutes per session
       )
   )
   ```

---

### Issue: SSL/TLS verification errors

**Symptoms:**
- `SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]`
- HTTPS requests fail but HTTP works

**Diagnosis:**
```bash
proxywhirl pool test http://proxy.example.com:8080 --target-url https://httpbin.org/get
```

**Solutions:**

1. **Disable SSL verification (NOT RECOMMENDED for production):**
   ```python
   rotator = ProxyWhirl(
       proxies=[...],
       verify_ssl=False
   )
   ```

2. **Use HTTP proxy for HTTPS targets:**
   ```python
   # HTTP proxy can still tunnel HTTPS via CONNECT
   rotator.add_proxy("http://proxy.example.com:8080")
   response = rotator.get("https://secure-site.com")
   ```

3. **Install CA certificates:**
   ```bash
   # macOS
   brew install ca-certificates

   # Ubuntu/Debian
   sudo apt-get install ca-certificates

   # Update certifi
   pip install --upgrade certifi
   ```

4. **Use SOCKS proxy instead:**
   ```python
   rotator.add_proxy("socks5://proxy.example.com:1080")
   ```

---

### Issue: Memory leaks / growing memory usage

**Symptoms:**
- Memory usage grows over time
- Eventually crashes with `MemoryError`

**Diagnosis:**
```python
import tracemalloc
tracemalloc.start()

# Run your code
# ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

**Solutions:**

1. **Use LRU client pool (built-in):**
   ```python
   # ProxyWhirl automatically uses LRUClientPool (max 100 clients)
   rotator = ProxyWhirl(proxies=[...])
   ```

2. **Close rotator when done:**
   ```python
   try:
       rotator = ProxyWhirl(proxies=[...])
       # ... use rotator
   finally:
       rotator.close()  # Close all httpx clients
   ```

3. **Use context manager:**
   ```python
   with ProxyWhirl(proxies=[...]) as rotator:
       response = rotator.get("https://example.com")
   ```

4. **Clear cache periodically:**
   ```python
   await rotator.cache_manager.cleanup()
   ```

---

### Issue: Database locked (SQLite)

**Symptoms:**
- `sqlite3.OperationalError: database is locked`
- Concurrent access failures

**Diagnosis:**
```bash
lsof proxywhirl.db  # Check what's accessing it
```

**Solutions:**

1. **Use WAL mode (Write-Ahead Logging):**
   ```python
   import sqlite3
   conn = sqlite3.connect("proxywhirl.db")
   conn.execute("PRAGMA journal_mode=WAL")
   conn.close()
   ```

2. **Increase timeout:**
   ```python
   from proxywhirl.storage import SQLiteStorage

   storage = SQLiteStorage(
       "proxywhirl.db",
       timeout=30.0  # Default is 5.0
   )
   ```

3. **Use file locking:**
   ```bash
   # CLI already uses file locks by default
   proxywhirl fetch

   # Disable with --no-lock if needed
   proxywhirl fetch --no-lock
   ```

4. **Close connections properly:**
   ```python
   async with SQLiteStorage("proxywhirl.db") as storage:
       # Use storage
       pass
   # Automatically closed
   ```

---

### Issue: Proxy works in browser but not in ProxyWhirl

**Symptoms:**
- Browser proxy settings work fine
- ProxyWhirl gets connection errors

**Diagnosis:**
```bash
# Test with curl (same as ProxyWhirl)
curl -x http://proxy.example.com:8080 https://httpbin.org/ip -v
```

**Possible Causes:**

1. **Browser uses system proxy settings:**
   - Browsers may use PAC (Proxy Auto-Config) files
   - ProxyWhirl requires explicit proxy URL

2. **Browser handles auth differently:**
   - Browser may cache credentials
   - ProxyWhirl requires credentials in URL or config

3. **Browser uses SOCKS proxy:**
   ```python
   # Try SOCKS instead of HTTP
   rotator.add_proxy("socks5://proxy.example.com:1080")
   ```

4. **Check proxy type:**
   ```bash
   # Test with different protocols
   curl -x http://proxy:8080 https://httpbin.org/ip
   curl -x socks5://proxy:1080 https://httpbin.org/ip
   ```

---

### Issue: Config file not found

**Symptoms:**
- `Config file not found: /path/to/.proxywhirl.toml`
- CLI falls back to defaults

**Solutions:**

1. **Check discovery order:**
   - `--config /path/to/file` (explicit)
   - `./pyproject.toml` (project-local, needs `[tool.proxywhirl]` section)
   - `~/.config/proxywhirl/config.toml` (user-global)

2. **Initialize config:**
   ```bash
   proxywhirl config init
   ```

3. **Use explicit path:**
   ```bash
   proxywhirl --config ./custom.toml pool list
   ```

4. **Verify file exists:**
   ```bash
   ls -la .proxywhirl.toml
   cat .proxywhirl.toml
   ```

---

## Debugging Tips

### Enable Debug Logging

**Method 1: Environment Variable**
```bash
export LOGURU_LEVEL=DEBUG
proxywhirl fetch
```

**Method 2: Programmatic**
```python
from loguru import logger

# Remove default handler
logger.remove()

# Add with DEBUG level
logger.add(
    "debug.log",
    level="DEBUG",
    format="{time} {level} {message}",
    rotation="10 MB"
)

# Now all ProxyWhirl operations will log verbosely
from proxywhirl import ProxyWhirl
rotator = ProxyWhirl(proxies=["http://proxy1:8080"])
```

**Method 3: CLI Flag**
```bash
proxywhirl --verbose pool list
proxywhirl -v health
```

---

### Inspect Exception Metadata

All ProxyWhirl exceptions include rich metadata:

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyWhirlError

try:
    rotator = ProxyWhirl(proxies=[])
    rotator.get("https://example.com")
except ProxyWhirlError as e:
    # Access error details
    print(f"Error Code: {e.error_code}")
    print(f"Proxy URL: {e.proxy_url}")  # Redacted
    print(f"Error Type: {e.error_type}")
    print(f"Retry Recommended: {e.retry_recommended}")
    print(f"Attempt Count: {e.attempt_count}")
    print(f"Metadata: {e.metadata}")

    # Convert to dict for logging
    import json
    print(json.dumps(e.to_dict(), indent=2))
```

---

### Use Test Mode

Test proxies without making actual requests:

```bash
# Test individual proxy
proxywhirl pool test http://proxy.example.com:8080

# Test with custom target
proxywhirl pool test http://proxy:8080 --target-url https://api.example.com

# Allow testing against localhost (SSRF protection disabled)
proxywhirl pool test http://proxy:8080 --allow-private
```

---

### Monitor Health in Real-Time

```bash
# Continuous health monitoring
proxywhirl health --continuous --interval 30

# Output:
# Check #1
# Status: 5 healthy | 2 degraded | 1 failed
#
# Check #2
# Status: 4 healthy | 3 degraded | 1 failed
```

---

### Export Metrics for Analysis

```python
from proxywhirl.retry_metrics import RetryMetrics

# Access retry statistics
metrics = rotator.retry_executor.metrics
print(f"Total attempts: {metrics.total_attempts}")
print(f"Success rate: {metrics.success_rate:.2%}")
print(f"Avg attempts: {metrics.average_attempts_per_operation:.2f}")

# Export to JSON
import json
with open("metrics.json", "w") as f:
    json.dump(metrics.to_dict(), f, indent=2)
```

---

### Validate Sources

Check which proxy sources are working:

```bash
# List all sources
proxywhirl sources

# Validate sources (slow, tests all 60+)
proxywhirl sources --validate

# CI mode (exit with error if any unhealthy)
proxywhirl sources --validate --fail-on-unhealthy
```

---

### Check Database Health

```bash
# Open SQLite database
sqlite3 proxywhirl.db

# Check tables
.tables

# View proxy stats
SELECT url, health_status, total_requests, success_rate
FROM proxies
ORDER BY success_rate DESC
LIMIT 10;

# Check database size
.dbinfo

# Exit
.exit
```

---

## FAQ

### How do I add custom proxy sources?

**Answer:**

Edit your sources configuration in `proxywhirl/sources.py` or use the API:

```python
from proxywhirl.sources import ProxySource
from proxywhirl.fetchers import fetch_from_source

# Define custom source
custom_source = ProxySource(
    name="MyCustomSource",
    url="https://my-proxy-api.com/list",
    format="plain_text",  # or "json"
    protocol="http"
)

# Fetch proxies
proxies = await fetch_from_source(custom_source)

# Add to rotator
for proxy in proxies:
    rotator.add_proxy(proxy)
```

---

### How do I configure rotation strategies?

**Answer:**

ProxyWhirl supports multiple strategies:

**1. Round-Robin (default):**
```python
rotator = ProxyWhirl(proxies=[...], strategy="round-robin")
```

**2. Random:**
```python
rotator = ProxyWhirl(proxies=[...], strategy="random")
```

**3. Weighted (performance-based):**
```python
rotator = ProxyWhirl(proxies=[...], strategy="weighted")
# Faster proxies get more traffic
```

**4. Least-Used:**
```python
rotator = ProxyWhirl(proxies=[...], strategy="least-used")
# Balances load across proxies
```

**5. Session Persistence:**
```python
from proxywhirl.strategies import SessionPersistenceStrategy

strategy = SessionPersistenceStrategy(
    session_duration=300,  # 5 minutes
    identifier_fn=lambda req: req.url.host  # Sticky sessions per domain
)
rotator = ProxyWhirl(proxies=[...], strategy=strategy)
```

**6. Geo-Targeted:**
```python
from proxywhirl.strategies import GeoTargetedStrategy

strategy = GeoTargetedStrategy(
    target_countries=["US", "GB", "CA"]
)
rotator = ProxyWhirl(proxies=[...], strategy=strategy)
```

**7. Performance-Based:**
```python
from proxywhirl.strategies import PerformanceBasedStrategy

strategy = PerformanceBasedStrategy(
    latency_weight=0.7,
    success_rate_weight=0.3
)
rotator = ProxyWhirl(proxies=[...], strategy=strategy)
```

See [`proxywhirl/strategies.py`](../proxywhirl/strategies.py) for implementation details.

---

### How do I persist proxies across runs?

**Answer:**

Use SQLite storage:

```python
from proxywhirl import ProxyWhirl
from proxywhirl.storage import SQLiteStorage

# Initialize storage
storage = SQLiteStorage("proxywhirl.db")
await storage.initialize()

# Create rotator with storage
rotator = ProxyWhirl(
    proxies=[],  # Will load from storage
    storage=storage
)

# Add proxies (automatically persisted)
rotator.add_proxy("http://proxy1:8080")

# Proxies are now saved in proxywhirl.db
```

Or use the CLI:

```bash
# Fetch and save to database
proxywhirl fetch --save-db --db proxywhirl.db

# Later, load from database
python -c "
from proxywhirl.storage import SQLiteStorage
import asyncio

async def load():
    storage = SQLiteStorage('proxywhirl.db')
    await storage.initialize()
    proxies = await storage.load()
    print(f'Loaded {len(proxies)} proxies')

asyncio.run(load())
"
```

---

### How do I handle proxy authentication?

**Answer:**

**Method 1: Inline credentials**
```python
rotator.add_proxy("http://user:pass@proxy.example.com:8080")
```

**Method 2: Separate fields (recommended for config files)**
```python
from pydantic import SecretStr
from proxywhirl.models import Proxy

proxy = Proxy(
    url="http://proxy.example.com:8080",
    username=SecretStr("myuser"),
    password=SecretStr("mypass")
)
rotator.add_proxy(proxy)
```

**Method 3: Configuration file**
```toml
# .proxywhirl.toml
encrypt_credentials = true

[[proxies]]
url = "http://proxy.example.com:8080"
username = "myuser"
password = "mypass"
```

Credentials are automatically encrypted when `encrypt_credentials = true`.

---

### How do I handle different proxy protocols?

**Answer:**

ProxyWhirl supports HTTP, HTTPS, SOCKS4, and SOCKS5:

```python
# HTTP proxy
rotator.add_proxy("http://proxy.example.com:8080")

# HTTPS proxy
rotator.add_proxy("https://proxy.example.com:8443")

# SOCKS4 proxy
rotator.add_proxy("socks4://proxy.example.com:1080")

# SOCKS5 proxy
rotator.add_proxy("socks5://proxy.example.com:1080")

# SOCKS5 with auth
rotator.add_proxy("socks5://user:pass@proxy.example.com:1080")
```

**Protocol Selection:**
- Use HTTP/HTTPS for web scraping
- Use SOCKS5 for maximum compatibility
- Use SOCKS4 for legacy systems

**Important:** Not all proxies support all protocols. Test before deploying:

```bash
proxywhirl pool test socks5://proxy.example.com:1080
```

---

### Why are my proxies slow?

**Answer:**

**Diagnosis:**
```bash
proxywhirl health --verbose
```

**Common Causes:**

1. **Geographic distance:**
   - Proxy in different continent
   - Use geo-targeted strategy

2. **Overloaded proxy:**
   - Free proxies are often slow
   - Consider premium proxies

3. **Poor connectivity:**
   - Check network latency: `ping proxy.example.com`

4. **Target site slow:**
   - Test different targets: `proxywhirl pool test http://proxy:8080 --target-url https://example.com`

**Solutions:**

1. **Use performance-based strategy:**
   ```python
   rotator = ProxyWhirl(
       proxies=[...],
       strategy="weighted"  # Faster proxies get priority
   )
   ```

2. **Filter slow proxies:**
   ```python
   from proxywhirl.models import HealthStatus

   # Only use proxies faster than 2 seconds
   fast_proxies = [
       p for p in rotator.pool.proxies
       if p.average_response_time_ms < 2000
       and p.health_status == HealthStatus.HEALTHY
   ]
   ```

3. **Use parallel validation:**
   ```bash
   proxywhirl fetch --concurrency 1000 --timeout 3
   ```

---

### How do I use ProxyWhirl with async code?

**Answer:**

Use `AsyncProxyWhirl`:

```python
import asyncio
from proxywhirl.async_client import AsyncProxyWhirl

async def main():
    async with AsyncProxyWhirl(
        proxies=["http://proxy1:8080", "http://proxy2:8080"]
    ) as rotator:
        # Make async requests
        response = await rotator.get("https://httpbin.org/ip")
        print(response.json())

        # Multiple concurrent requests
        urls = ["https://httpbin.org/ip"] * 10
        tasks = [rotator.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)

asyncio.run(main())
```

See [`examples/python/00_quickstart.py`](../examples/python/00_quickstart.py) for more examples.

---

### How do I integrate with existing httpx code?

**Answer:**

**Option 1: Use ProxyWhirl's built-in client**
```python
rotator = ProxyWhirl(proxies=[...])
response = rotator.get("https://api.example.com")
# Same interface as httpx
```

**Option 2: Get proxy URL and use with httpx**
```python
import httpx
from proxywhirl import ProxyWhirl

rotator = ProxyWhirl(proxies=[...])
proxy = rotator.get_next()

# Use with httpx directly
with httpx.Client(proxy=proxy.url) as client:
    response = client.get("https://api.example.com")
```

**Option 3: Use as httpx transport**
```python
# Coming soon: ProxyWhirlTransport
```

---

### Can I use ProxyWhirl in production?

**Answer:**

**Yes, with precautions:**

1. **Use premium proxies for reliability:**
   - Free proxies have high failure rates
   - Consider rotating residential proxies

2. **Enable health monitoring:**
   ```python
   rotator = ProxyWhirl(
       proxies=[...],
       health_check_interval=60  # Check every minute
   )
   ```

3. **Configure retries:**
   ```python
   from proxywhirl.retry_policy import RetryPolicy

   rotator = ProxyWhirl(
       proxies=[...],
       retry_policy=RetryPolicy(
           max_attempts=5,
           exponential_base=2.0,
           max_delay=30.0
       )
   )
   ```

4. **Monitor metrics:**
   ```python
   metrics = rotator.retry_executor.metrics
   if metrics.success_rate < 0.8:
       logger.warning("Low success rate, check proxies")
   ```

5. **Use circuit breakers:**
   ```python
   from proxywhirl.circuit_breaker import CircuitBreaker

   rotator = ProxyWhirl(
       proxies=[...],
       circuit_breaker=CircuitBreaker(
           failure_threshold=5,
           recovery_timeout=30
       )
   )
   ```

6. **Enable persistence:**
   ```python
   storage = SQLiteStorage("proxywhirl.db")
   rotator = ProxyWhirl(proxies=[...], storage=storage)
   ```

---

## Getting Help

### Check Existing Documentation

- **Getting Started:** [`docs/getting_started.md`](getting_started.md)
- **Configuration:** [`docs/configuration.md`](configuration.md)
- **API Reference:** [`proxywhirl/`](../proxywhirl/)
- **Examples:** [`examples/`](../examples/)

### Search Issues

Check if your issue is already reported:
- [GitHub Issues](https://github.com/wyattowalsh/proxywhirl/issues)

### Enable Debugging

Before asking for help, collect debug information:

```bash
# Enable verbose logging
export LOGURU_LEVEL=DEBUG

# Run your command with debug output
proxywhirl --verbose pool list > debug.log 2>&1

# Collect system info
uv --version
python --version
pip show proxywhirl
```

### Create an Issue

If you can't find a solution:

1. **Search existing issues first**
2. **Include debug logs**
3. **Provide minimal reproduction**
4. **Specify your environment:**
   - ProxyWhirl version
   - Python version
   - Operating system
   - Proxy type (free/premium/residential)

**Template:**
```markdown
## Description
Brief description of the issue

## Reproduction
```python
# Minimal code to reproduce
from proxywhirl import ProxyWhirl
rotator = ProxyWhirl(proxies=["http://proxy:8080"])
rotator.get("https://example.com")  # Error here
```

## Environment
- ProxyWhirl version: 0.1.0
- Python version: 3.11.5
- OS: macOS 14.0

## Logs
```
[Paste debug logs here]
```

## Expected Behavior
What should happen

## Actual Behavior
What actually happens
```

---

## Related Documentation

- **Getting Started:** [`docs/getting_started.md`](getting_started.md)
- **Configuration:** [`docs/configuration.md`](configuration.md)
- **Error Reference:** [`proxywhirl/exceptions.py`](../proxywhirl/exceptions.py)
- **CLI Reference:** [`proxywhirl/cli.py`](../proxywhirl/cli.py)
- **Examples:** [`examples/`](../examples/)

---

**Last Updated:** 2025-12-27
**Version:** 1.0.0
