---
title: CLI Reference
---

# CLI Reference

ProxyWhirl provides a full-featured command-line interface for proxy rotation, pool management, health monitoring, statistics, and data export. All commands support multiple output formats (text/JSON/CSV) and integrate with the configuration system.

## Installation

```bash
# Install with CLI support
uv pip install proxywhirl

# Or install from source
uv sync
uv run proxywhirl --help
```

## Global Options

All commands support these global options:

```{list-table}
:header-rows: 1
:widths: 25 15 60

* - Option
  - Default
  - Description
* - ``--config, -c PATH``
  - Auto-discover
  - Path to TOML configuration file
* - ``--format, -f FORMAT``
  - ``text``
  - Output format: ``text``, ``json``, or ``csv``
* - ``--verbose, -v``
  - ``false``
  - Enable verbose logging and debug output
* - ``--no-lock``
  - ``false``
  - Disable file locking (use with caution in concurrent scenarios)
```

### Config Auto-Discovery

When ``--config`` is not provided, ProxyWhirl searches for configuration in this order:

1. **Project directory**: ``./pyproject.toml`` (with ``[tool.proxywhirl]`` section)
2. **User directory**: ``~/.config/proxywhirl/config.toml`` (Linux/macOS) or ``%APPDATA%\proxywhirl\config.toml`` (Windows)
3. **Defaults**: In-memory configuration with sensible defaults

```{tip}
Use ``proxywhirl config init`` to create a starter configuration file in the current directory.
```

## Commands

### request

Make HTTP requests through rotating proxies with automatic retry and failover.

**Usage:**
```bash
proxywhirl request [OPTIONS] URL
```

**Arguments:**
- ``URL``: Target URL to request (required)

**Options:**

```{list-table}
:header-rows: 1
:widths: 30 15 55

* - Option
  - Default
  - Description
* - ``--method, -X METHOD``
  - ``GET``
  - HTTP method (GET, POST, PUT, DELETE, etc.)
* - ``--header, -H HEADER``
  - None
  - Custom headers (format: ``'Key: Value'``), repeatable
* - ``--data, -d DATA``
  - None
  - Request body data (JSON string or form data)
* - ``--proxy, -p URL``
  - None
  - Override rotation and use specific proxy URL
* - ``--retries NUM``
  - ``3``
  - Maximum retry attempts (overrides config)
```

**Examples:**

```bash
# Simple GET request
proxywhirl request https://api.example.com/data

# POST with JSON data
proxywhirl request -X POST -d '{"key":"value"}' https://api.example.com/submit

# Custom headers
proxywhirl request -H "Authorization: Bearer token123" \
  -H "User-Agent: CustomBot/1.0" \
  https://api.example.com/protected

# Force specific proxy
proxywhirl request --proxy http://proxy.example.com:8080 https://httpbin.org/ip

# JSON output for parsing
proxywhirl --format json request https://api.example.com/data
```

**Output (text format):**
```
Status: 200
URL: https://api.example.com/data
Time: 245ms
Proxy: http://proxy1.example.com:8080
Attempts: 1

Response:
{"result": "success", "data": [...]}
```

**Output (JSON format):**
```json
{
  "status_code": 200,
  "url": "https://api.example.com/data",
  "method": "GET",
  "elapsed_ms": 245.3,
  "proxy_used": "http://proxy1.example.com:8080",
  "attempts": 1,
  "body": "{\"result\": \"success\"}"
}
```

---

### pool

Manage the proxy pool: list proxies, add new ones, remove proxies, or test connectivity.

**Usage:**
```bash
proxywhirl pool [OPTIONS] ACTION [PROXY]
```

**Arguments:**
- ``ACTION``: Action to perform: ``list``, ``add``, ``remove``, or ``test``
- ``PROXY``: Proxy URL (required for ``add``, ``remove``, ``test`` actions)

**Options:**

```{list-table}
:header-rows: 1
:widths: 30 15 55

* - Option
  - Default
  - Description
* - ``--username, -u USERNAME``
  - None
  - Proxy authentication username (for ``add`` action)
* - ``--password, -p PASSWORD``
  - None
  - Proxy authentication password (for ``add`` action)
* - ``--target-url URL``
  - ``https://httpbin.org/ip``
  - Target URL for proxy testing (http/https only)
* - ``--allow-private``
  - ``false``
  - Allow testing against localhost/private IPs (use with caution)
```

**Examples:**

```bash
# List all proxies in pool
proxywhirl pool list

# List with JSON output
proxywhirl --format json pool list

# Add proxy without authentication
proxywhirl pool add http://proxy1.example.com:8080

# Add proxy with authentication
proxywhirl pool add http://proxy2.example.com:8080 \
  --username myuser \
  --password mypass

# Remove proxy
proxywhirl pool remove http://proxy1.example.com:8080

# Test proxy connectivity
proxywhirl pool test http://proxy1.example.com:8080

# Test proxy with custom target URL
proxywhirl pool test http://proxy1.example.com:8080 \
  --target-url https://api.example.com
```

**Output (list, text format):**
```
Proxy Pool Summary
Total Proxies: 3
Healthy: 2 | Degraded: 1 | Failed: 0
Strategy: round-robin

  ● http://proxy1.example.com:8080 (145ms, 98% success)
  ● http://proxy2.example.com:8080 (230ms, 95% success)
  ● http://proxy3.example.com:8080 (1245ms, 67% success)
```

**Output (test, text format):**
```
Testing proxy: http://proxy1.example.com:8080...
Target URL: https://httpbin.org/ip
✓ Proxy is working (145ms)
```

```{warning}
Proxies added via ``pool add`` are persisted to your configuration file. Use ``--config`` to specify which config file to update.
```

```{note}
The ``--allow-private`` flag bypasses SSRF protection. Only use it when testing against trusted local/internal services.
```

---

### config

Manage CLI configuration: show current settings, get/set individual values, or initialize a new config file.

**Usage:**
```bash
proxywhirl config ACTION [KEY] [VALUE]
```

**Arguments:**
- ``ACTION``: Action to perform: ``show``, ``get``, ``set``, or ``init``
- ``KEY``: Configuration key (for ``get``/``set`` actions)
- ``VALUE``: Configuration value (for ``set`` action)

**Examples:**

```bash
# Initialize new config file
proxywhirl config init

# Show entire configuration
proxywhirl config show

# Show config as JSON
proxywhirl --format json config show

# Get specific setting
proxywhirl config get rotation_strategy

# Set rotation strategy
proxywhirl config set rotation_strategy random

# Set timeout
proxywhirl config set timeout 60

# Set boolean values
proxywhirl config set verify_ssl false
```

**Configurable Keys:**

```{list-table}
:header-rows: 1
:widths: 30 15 15 40

* - Key
  - Type
  - Default
  - Description
* - ``rotation_strategy``
  - str
  - ``round-robin``
  - Proxy rotation strategy (``round-robin``, ``random``, ``weighted``, ``least-used``)
* - ``health_check_interval``
  - int
  - ``300``
  - Seconds between health checks (0 to disable)
* - ``timeout``
  - int
  - ``30``
  - Request timeout in seconds
* - ``max_retries``
  - int
  - ``3``
  - Maximum retry attempts per request
* - ``follow_redirects``
  - bool
  - ``true``
  - Follow HTTP redirects automatically
* - ``verify_ssl``
  - bool
  - ``true``
  - Verify SSL certificates
* - ``default_format``
  - str
  - ``human``
  - Default output format
* - ``color``
  - bool
  - ``true``
  - Enable colored terminal output
* - ``verbose``
  - bool
  - ``false``
  - Enable verbose logging
* - ``storage_backend``
  - str
  - ``file``
  - Storage backend type
```

**Output (show, text format):**
```
Configuration
Config file: /Users/user/project/.proxywhirl.toml

rotation_strategy: round-robin
health_check_interval: 300s
timeout: 30s
max_retries: 3
follow_redirects: True
verify_ssl: True
default_format: text
color: True
verbose: False
storage_backend: memory
storage_path: None
```

---

### health

Check health of all proxies in the pool. Supports continuous monitoring mode for long-running checks.

**Usage:**
```bash
proxywhirl health [OPTIONS]
```

**Options:**

```{list-table}
:header-rows: 1
:widths: 30 15 55

* - Option
  - Default
  - Description
* - ``--continuous, -c``
  - ``false``
  - Run continuously with periodic checks
* - ``--interval, -i SECONDS``
  - ``300``
  - Check interval in seconds (for continuous mode)
* - ``--target-url URL``
  - ``https://httpbin.org/ip``
  - Target URL for health checks (http/https only)
* - ``--allow-private``
  - ``false``
  - Allow testing against localhost/private IPs (use with caution)
```

**Examples:**

```bash
# Single health check
proxywhirl health

# Continuous monitoring with default interval (300s)
proxywhirl health --continuous

# Continuous monitoring with custom interval
proxywhirl health --continuous --interval 60

# Health check with custom target URL
proxywhirl health --target-url https://api.example.com

# Health check with JSON output
proxywhirl --format json health
```

**Output (single check, text format):**
```
Checking proxy health...

Health Check Results
Healthy: 2 | Degraded: 1 | Failed: 0

  ● http://proxy1.example.com:8080 (145ms, 98% success)
  ● http://proxy2.example.com:8080 (230ms, 95% success)
  ● http://proxy3.example.com:8080 (1245ms, 67% success)
```

**Output (continuous mode):**
```
Continuous health monitoring (interval: 60s)
Press Ctrl+C to stop

Check #1
✓ http://proxy1.example.com:8080: 200 (145ms)
✓ http://proxy2.example.com:8080: 200 (230ms)
✗ http://proxy3.example.com:8080: Connection timeout
Status: 2 healthy | 0 degraded | 1 failed

Check #2
✓ http://proxy1.example.com:8080: 200 (152ms)
✓ http://proxy2.example.com:8080: 200 (218ms)
✓ http://proxy3.example.com:8080: 200 (890ms)
Status: 3 healthy | 0 degraded | 0 failed

...

Monitoring stopped
```

**Output (JSON format):**
```json
{
  "total_proxies": 3,
  "healthy": 2,
  "degraded": 1,
  "failed": 0,
  "rotation_strategy": "round-robin",
  "current_index": 0,
  "proxies": [
    {
      "url": "http://proxy1.example.com:8080",
      "health": "healthy",
      "response_time_ms": 145.3,
      "success_rate": 0.98
    },
    {
      "url": "http://proxy2.example.com:8080",
      "health": "healthy",
      "response_time_ms": 230.1,
      "success_rate": 0.95
    },
    {
      "url": "http://proxy3.example.com:8080",
      "health": "degraded",
      "response_time_ms": 1245.6,
      "success_rate": 0.67
    }
  ]
}
```

```{note}
The ``--allow-private`` flag bypasses SSRF protection. Only use it when testing against trusted local/internal services.
```

---

### fetch

Fetch proxies from 60+ free proxy sources, validate them, and save to database and files.

**Usage:**
```bash
proxywhirl fetch [OPTIONS]
```

**Options:**

```{list-table}
:header-rows: 1
:widths: 35 15 50

* - Option
  - Default
  - Description
* - ``--validate / --no-validate``
  - ``true``
  - Validate proxies after fetching
* - ``--save-db / --no-save-db``
  - ``true``
  - Save validated proxies to database
* - ``--export / --no-export``
  - ``true``
  - Export to text/JSON files
* - ``--output, -o DIR``
  - ``docs/proxy-lists``
  - Output directory for exported files
* - ``--db PATH``
  - ``proxywhirl.db``
  - Path to SQLite database
* - ``--timeout, -t SECONDS``
  - ``5.0``
  - Validation timeout per proxy
* - ``--concurrency, -c NUM``
  - ``500``
  - Parallel validation concurrency
```

**Examples:**

```bash
# Fetch and validate from all sources
proxywhirl fetch

# Fast fetch without validation (raw proxies)
proxywhirl fetch --no-validate

# High-concurrency validation (fast, uses more resources)
proxywhirl fetch --concurrency 2000

# Fetch to custom location
proxywhirl fetch --output ./proxies --db ./proxies.db

# Fetch without database save (files only)
proxywhirl fetch --no-save-db
```

**Process:**
1. Fetches proxies from 60+ sources (HTTP, SOCKS4, SOCKS5)
2. Validates each proxy for connectivity (optional, parallel)
3. Saves validated proxies to SQLite database (optional)
4. Exports to text/JSON files for web dashboard (optional)
5. Enriches with GeoIP metadata when available

**Output:**
```
ProxyWhirl Fetch - Aggregating proxies from 60+ sources

Fetching from 45 HTTP sources...
Fetching from 8 SOCKS4 sources...
Fetching from 7 SOCKS5 sources...

Fetched raw proxies: 12,345 trusted (http), 234 trusted (socks4), 567 trusted (socks5)
Untrusted proxies: 45,678 (http), 1,234 (socks4), 2,345 (socks5)

✓ Trusted sources: 13,146 proxies added without validation

Validating 49,257 proxies with concurrency=500...
Progress: 10000/49257 checked, 1234 valid (12.3%), 2000 proxies/sec
Progress: 20000/49257 checked, 2567 valid (12.8%), 2050 proxies/sec
...
✓ Validation complete: 6,789/49,257 valid (13.8%) in 24.3s

Total proxies ready: 19,935

✓ Saved 6,789 http proxies to docs/proxy-lists/http.txt
✓ Saved 234 socks4 proxies to docs/proxy-lists/socks4.txt
✓ Saved 567 socks5 proxies to docs/proxy-lists/socks5.txt
✓ Saved all proxies to docs/proxy-lists/all.txt
✓ Saved JSON to docs/proxy-lists/proxies.json
✓ Saved metadata to docs/proxy-lists/metadata.json

Enriching proxies with metadata...
✓ Enriched 18,456/19,935 proxies with geo data
✓ Saved rich JSON (19,935 proxies) to docs/proxy-lists/proxies-rich.json

✓ Saved 19,935 validated proxies to database: proxywhirl.db

Proxy aggregation complete!
```

```{tip}
Use ``--concurrency 2000`` for faster validation on systems with high network capacity. Lower it to ``100`` on rate-limited networks.
```

---

### export

Export proxy data for web dashboards and analytics. Generates ``stats.json`` and ``proxies-rich.json`` files with full metadata.

**Usage:**
```bash
proxywhirl export [OPTIONS]
```

**Options:**

```{list-table}
:header-rows: 1
:widths: 30 25 45

* - Option
  - Default
  - Description
* - ``--output, -o DIR``
  - ``docs/proxy-lists``
  - Output directory for exported files
* - ``--db PATH``
  - ``proxywhirl.db``
  - Path to SQLite database
* - ``--stats-only``
  - ``false``
  - Only export stats.json
* - ``--proxies-only``
  - ``false``
  - Only export proxies-rich.json
```

**Examples:**

```bash
# Export all files
proxywhirl export

# Export to custom directory
proxywhirl export --output ./data/exports

# Export only statistics
proxywhirl export --stats-only

# Export from custom database
proxywhirl export --db ./custom.db --output ./output
```

**Output:**
```
Exporting data for web dashboard...
Output directory: docs/proxy-lists
Database: proxywhirl.db

✓ Exported stats: docs/proxy-lists/stats.json
✓ Exported proxies-rich: docs/proxy-lists/proxies-rich.json

Export complete!
```

**Generated Files:**

- ``stats.json``: Aggregate statistics (total proxies, health distribution, protocol breakdown)
- ``proxies-rich.json``: Full proxy details with geo data, response times, success rates

```{note}
The ``export`` command is used by CI/CD workflows to generate data for the web dashboard. It aggregates database content and enriches with metadata.
```

---

### setup-geoip

Set up the MaxMind GeoLite2 database for offline geo enrichment of proxy data.

**Usage:**
```bash
proxywhirl setup-geoip [OPTIONS]
```

**Options:**

```{list-table}
:header-rows: 1
:widths: 30 15 55

* - Option
  - Default
  - Description
* - ``--check``
  - ``false``
  - Only check if GeoIP database exists
```

**Examples:**

```bash
# Show setup instructions
proxywhirl setup-geoip

# Check if database is installed
proxywhirl setup-geoip --check
```

**Output (when database is missing):**
```
MaxMind GeoLite2 Database Setup

GeoIP database not found.

To enable geo enrichment, download the free GeoLite2-City database:

Option 1: Direct Download (Recommended)
  1. Go to: https://www.maxmind.com/en/geolite2/signup
  2. Create a free account
  3. Download 'GeoLite2-City' in MMDB format
  4. Place the file at: ~/.config/proxywhirl/GeoLite2-City.mmdb

Option 2: Using geoipupdate tool
  1. Install: brew install geoipupdate  # or apt-get install geoipupdate
  2. Configure with your MaxMind license key
  3. Run: geoipupdate
  4. Symlink or copy to: ~/.config/proxywhirl/GeoLite2-City.mmdb

Note: GeoLite2 databases are free but require registration.
Without it, enrichment still provides IP properties and port analysis.

✓ Created config directory: ~/.config/proxywhirl
```

**Output (when database is installed):**
```
✓ GeoIP database is available
  Location: ~/.config/proxywhirl/GeoLite2-City.mmdb

Proxy enrichment will include:
  • Country name and code
  • City and region
  • Timezone
  • Geographic coordinates
```

```{note}
GeoIP enrichment is optional. Without the database, ``proxywhirl fetch`` still provides IP properties and port analysis.
```

---

### sources

List and validate all configured proxy sources. Useful for identifying stale or broken sources.

**Usage:**
```bash
proxywhirl sources [OPTIONS]
```

**Options:**

```{list-table}
:header-rows: 1
:widths: 35 15 50

* - Option
  - Default
  - Description
* - ``--validate, -v``
  - ``false``
  - Validate all sources and check for broken ones
* - ``--timeout, -t SECONDS``
  - ``15.0``
  - Timeout per source in seconds
* - ``--concurrency, -c NUM``
  - ``20``
  - Maximum concurrent requests
* - ``--fail-on-unhealthy, -f``
  - ``false``
  - Exit with error code if any sources are unhealthy (for CI)
```

**Examples:**

```bash
# List all sources
proxywhirl sources

# Validate all sources
proxywhirl sources --validate

# Validate with higher concurrency
proxywhirl sources --validate --concurrency 50

# CI mode: fail if sources are unhealthy
proxywhirl sources --validate --fail-on-unhealthy

# Get results as JSON
proxywhirl --format json sources --validate
```

**Output (list mode):**
```
Configured Proxy Sources

HTTP Sources (45):
  • https://www.proxy-list.download/api/v1/get?type=http
  • https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http
  • https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt
  ...

SOCKS4 Sources (8):
  • https://www.proxy-list.download/api/v1/get?type=socks4
  • https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4
  ...

SOCKS5 Sources (7):
  • https://www.proxy-list.download/api/v1/get?type=socks5
  • https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5
  ...

Total: 60 sources

Use --validate to check source health
```

**Output (validate mode):**
```
Validating 60 proxy sources...

┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ Status  ┃ Source                           ┃ Response ┃ Size   ┃ Time   ┃ Error  ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━┩
│ ✓ OK    │ proxy-list.download HTTP         │ 200      │ 12,345 │ 234ms  │        │
│ ✓ OK    │ proxyscrape HTTP                 │ 200      │ 45,678 │ 456ms  │        │
│ ✗ FAIL  │ stale-source.example.com         │ -        │ -      │ 0ms    │ Timeout│
...
┗━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━┷━━━━━━━━┷━━━━━━━━┷━━━━━━━━┛

Summary:
  Total: 60 | Healthy: 58 | Unhealthy: 2 | Time: 5678ms

Unhealthy sources:
  • stale-source.example.com: Timeout
  • broken-source.example.com: HTTP 404
```

```{tip}
Run ``proxywhirl sources --validate --fail-on-unhealthy`` in CI to catch broken sources early.
```

---

### stats

Display retry and circuit breaker statistics for monitoring proxy performance and reliability.

**Usage:**
```bash
proxywhirl stats [OPTIONS]
```

**Options:**

```{list-table}
:header-rows: 1
:widths: 30 15 55

* - Option
  - Default
  - Description
* - ``--retry``
  - ``false``
  - Show retry metrics (attempts, success by attempt, etc.)
* - ``--circuit-breaker``
  - ``false``
  - Show circuit breaker state transitions
* - ``--hours, -h NUM``
  - ``24``
  - Time window in hours for statistics
```

**Examples:**

```bash
# Show retry metrics (default if no flags)
proxywhirl stats --retry

# Show circuit breaker states
proxywhirl stats --circuit-breaker

# Show both retry and circuit breaker stats
proxywhirl stats --retry --circuit-breaker

# Show stats for last 12 hours
proxywhirl stats --retry --circuit-breaker --hours 12

# Get stats as JSON
proxywhirl --format json stats --retry
```

**Output (retry metrics, text format):**
```
Retry Metrics Summary
Total Retries: 1,234
Retention: 24 hours

Success Rate by Attempt:
┏━━━━━━━━━┳━━━━━━━━━━━┓
┃ Attempt ┃ Successes ┃
┡━━━━━━━━━╇━━━━━━━━━━━┩
│    1    │    850    │
│    2    │    234    │
│    3    │    150    │
└─────────┴───────────┘

Per-Proxy Statistics:
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Proxy ID             ┃ Attempts ┃ Success ┃ Failures ┃ Avg Latency ┃ CB Opens┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━┩
│ proxy1.example.com   │   500    │ 475(95%)│    25    │    145ms    │    2    │
│ proxy2.example.com   │   400    │ 360(90%)│    40    │    230ms    │    5    │
│ proxy3.example.com   │   334    │ 200(60%)│   134    │   1245ms    │   15    │
└──────────────────────┴──────────┴─────────┴──────────┴─────────────┴─────────┘
```

**Output (circuit breaker events, text format):**
```
Circuit Breaker Events
Total Events: 45

Recent Events (last 20):
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Timestamp           ┃ Proxy ID             ┃ Transition         ┃ Failures ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ 2025-12-27 18:15:23 │ proxy1.example.com   │ closed → open      │    5     │
│ 2025-12-27 18:18:45 │ proxy1.example.com   │ open → half_open   │    0     │
│ 2025-12-27 18:19:12 │ proxy1.example.com   │ half_open → closed │    0     │
│ 2025-12-27 18:25:30 │ proxy3.example.com   │ closed → open      │    8     │
...
└─────────────────────┴──────────────────────┴────────────────────┴──────────┘
```

**Output (JSON format):**
```json
{
  "summary": {
    "total_retries": 1234,
    "retention_hours": 24,
    "success_by_attempt": {
      "1": 850,
      "2": 234,
      "3": 150
    }
  },
  "by_proxy": {
    "proxy1.example.com:8080": {
      "total_attempts": 500,
      "success_count": 475,
      "failure_count": 25,
      "avg_latency": 145.3,
      "circuit_breaker_opens": 2
    }
  }
}
```

```{note}
The ``stats`` command shows both if neither ``--retry`` nor ``--circuit-breaker`` is specified.
```

---

## Output Formats

All commands support three output formats via the ``--format`` global option:

### Text (default)

Human-readable output with colors and formatting. Ideal for interactive terminal use.

```bash
proxywhirl pool list
```

### JSON

Machine-readable JSON for parsing and automation. Includes all fields with type information.

```bash
proxywhirl --format json pool list
```

### CSV

Tabular output for spreadsheet import or data analysis. Only available for list/table commands.

```bash
proxywhirl --format csv pool list > proxies.csv
```

## Configuration File

ProxyWhirl uses TOML configuration files. Example ``~/.config/proxywhirl/config.toml``:

```toml
# Proxy pool
[[proxies]]
url = "http://proxy1.example.com:8080"

[[proxies]]
url = "http://proxy2.example.com:8080"
username = "user"
password = "pass"

# Rotation settings
rotation_strategy = "round-robin"
health_check_interval = 300

# Request settings
timeout = 30
max_retries = 3
follow_redirects = true
verify_ssl = true

# Output settings
default_format = "text"
color = true
verbose = false

# Storage settings
storage_backend = "memory"

# Security
encrypt_credentials = true
encryption_key_env = "PROXYWHIRL_KEY"
```

For project-specific configuration, use ``pyproject.toml``:

```toml
[tool.proxywhirl]
rotation_strategy = "random"
timeout = 60
max_retries = 5

[[tool.proxywhirl.proxies]]
url = "http://proxy1.example.com:8080"
```

```{seealso}
- :doc:`/getting-started/index` for quick start guide
- :doc:`/guides/advanced-strategies` for rotation strategy details
- :doc:`/guides/retry-failover` for retry and circuit breaker configuration
```

## Advanced Usage

### Scripting with JSON Output

```bash
#!/bin/bash
# Get healthy proxy count
HEALTHY=$(proxywhirl --format json health | jq '.healthy')
echo "Healthy proxies: $HEALTHY"

# Alert if less than threshold
if [ "$HEALTHY" -lt 2 ]; then
  echo "WARNING: Low proxy count!"
  exit 1
fi
```

### Automated Proxy Refresh

```bash
#!/bin/bash
# Daily proxy refresh script
proxywhirl fetch --concurrency 1000
proxywhirl health --continuous --interval 600 &
```

### CI/CD Integration

```yaml
# .github/workflows/validate-proxies.yml
name: Validate Proxy Sources
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uv sync
      - run: uv run proxywhirl sources --validate --fail-on-unhealthy
      - run: uv run proxywhirl fetch --concurrency 2000
      - run: uv run proxywhirl export
```

### Multi-Environment Configuration

```bash
# Development
proxywhirl --config dev.toml pool list

# Staging
proxywhirl --config staging.toml pool list

# Production
proxywhirl --config prod.toml pool list
```

## Troubleshooting

### Configuration Not Found

```bash
# Check discovery path
proxywhirl config show

# Initialize config
proxywhirl config init
```

### Lock File Issues

```bash
# Skip locking for debugging
proxywhirl --no-lock pool list

# Remove stale lock
rm ~/.config/proxywhirl/.proxywhirl.lock
```

### Slow Validation

```bash
# Increase concurrency
proxywhirl fetch --concurrency 2000

# Skip validation for testing
proxywhirl fetch --no-validate
```

### GeoIP Enrichment Not Working

```bash
# Check database status
proxywhirl setup-geoip --check

# Follow setup instructions
proxywhirl setup-geoip
```

### SSRF Protection Blocking Local Tests

```bash
# Use --allow-private flag for local testing
proxywhirl pool test http://proxy.example.com:8080 \
  --target-url http://localhost:8000 \
  --allow-private

# Note: Only use with trusted, internal services
```

## Environment Variables

```{list-table}
:header-rows: 1
:widths: 40 60

* - Variable
  - Description
* - ``PROXYWHIRL_KEY``
  - Encryption key for credential encryption (default key location: ``~/.config/proxywhirl/key.enc``)
* - ``PROXYWHIRL_CACHE_ENCRYPTION_KEY``
  - Encryption key for cache encryption (optional)
* - ``NO_COLOR``
  - Disable colored output (standard environment variable)
* - ``COLUMNS``
  - Override terminal width detection
```

## Exit Codes

```{list-table}
:header-rows: 1
:widths: 15 85

* - Code
  - Meaning
* - ``0``
  - Success (operation completed successfully)
* - ``1``
  - General error (invalid arguments, failed operation, validation failure, SSRF protection triggered)
```

**Common Exit Code 1 Scenarios:**
- Invalid URL format or scheme
- SSRF protection triggered (localhost/private IP access denied)
- Proxy not found in pool
- Configuration file not found or invalid
- Request failed after all retries
- Source validation failed (with ``--fail-on-unhealthy``)
- Lock acquisition timeout

---

```{note}
The CLI uses file locking by default to prevent concurrent modifications. Use ``--no-lock`` only when you're certain no other proxywhirl processes are running.
```
