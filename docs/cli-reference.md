# ProxyWhirl CLI Reference

## Overview

ProxyWhirl includes a powerful command-line interface for managing proxies, validating sources, and monitoring performance.

```bash
proxywhirl --help
```

## Global Options

These options work with all commands:

```
--config FILE           Configuration file path
--log-level LEVEL       Log level (DEBUG, INFO, WARNING, ERROR)
--debug                 Enable debug mode
--help                  Show help message
--version               Show version
```

## Commands

### list

List proxies in the current pool.

```bash
proxywhirl list [OPTIONS]
```

**Options:**
```
--filter STATUS         Filter by status: healthy, degraded, unhealthy, inactive
--protocol PROTOCOL     Filter by protocol: http, https, socks4, socks5
--limit INTEGER         Maximum proxies to show (default: 20)
--offset INTEGER        Pagination offset (default: 0)
--tags TEXT             Filter by tags (comma-separated)
--sort-by FIELD         Sort by: host, protocol, latency, success_rate
--format FORMAT         Output format: table, json, csv (default: table)
--detailed              Show detailed information
--export FILE           Export results to file
```

**Examples:**

```bash
# List all healthy proxies
proxywhirl list --filter healthy

# List HTTPS proxies from US, sorted by latency
proxywhirl list --protocol https --tags us --sort-by latency

# Export to JSON
proxywhirl list --format json --export proxies.json

# Show detailed view
proxywhirl list --detailed --limit 5
```

### add

Add proxies to the pool.

```bash
proxywhirl add [OPTIONS]
```

**Options:**
```
--proxy PROXY           Single proxy (protocol://host:port)
--proxies TEXT          Multiple proxies (comma-separated)
--file FILE             Load proxies from file
--source ID             Fetch from proxy source
--format FORMAT         File format: json, csv, plain (default: plain)
--validate              Validate proxies before adding
--skip-duplicates       Skip duplicate proxies
--tags TEXT             Add tags to all proxies
```

**Examples:**

```bash
# Add single proxy
proxywhirl add --proxy http://192.168.1.1:8080

# Add multiple proxies
proxywhirl add --proxies http://192.168.1.1:8080,http://192.168.1.2:8080

# Load from file
proxywhirl add --file proxies.txt --format plain

# Fetch from source
proxywhirl add --source free-proxy-list

# Add and validate
proxywhirl add --file proxies.json --format json --validate

# Add with tags
proxywhirl add --proxy http://192.168.1.1:8080 --tags us,fast
```

### remove

Remove proxies from the pool.

```bash
proxywhirl remove [OPTIONS]
```

**Options:**
```
--proxy PROXY           Proxy to remove (host:port)
--filter STATUS         Remove by status: healthy, degraded, unhealthy, inactive
--tags TEXT             Remove by tags (comma-separated)
--older-than DAYS       Remove not used for N days
--all                   Clear entire pool (with confirmation)
```

**Examples:**

```bash
# Remove single proxy
proxywhirl remove --proxy 192.168.1.1:8080

# Remove unhealthy proxies
proxywhirl remove --filter unhealthy

# Remove proxies not used for 30 days
proxywhirl remove --older-than 30

# Clear pool
proxywhirl remove --all
```

### validate

Test proxies for connectivity and performance.

```bash
proxywhirl validate [OPTIONS]
```

**Options:**
```
--proxy PROXY           Validate single proxy
--all                   Validate all proxies in pool
--sample SIZE           Validate random sample (default: 100)
--url URL               Test URL (default: https://httpbin.org/ip)
--timeout SECONDS       Timeout for each test (default: 5)
--concurrent INTEGER    Concurrent tests (default: 10)
--update                Update health status
--export FILE           Export results
```

**Examples:**

```bash
# Validate all proxies
proxywhirl validate --all --concurrent 20

# Validate single proxy
proxywhirl validate --proxy 192.168.1.1:8080

# Validate sample and update status
proxywhirl validate --sample 200 --update

# Export results
proxywhirl validate --all --export validation.json
```

### stats

Show pool statistics.

```bash
proxywhirl stats [OPTIONS]
```

**Options:**
```
--by-protocol           Group by protocol
--by-location           Group by location
--by-status             Group by health status
--period DAYS           Show stats for last N days (default: 7)
--export FILE           Export to file
```

**Examples:**

```bash
# Show overall stats
proxywhirl stats

# Stats grouped by protocol
proxywhirl stats --by-protocol

# Geographic distribution
proxywhirl stats --by-location

# Weekly performance
proxywhirl stats --period 7 --export stats.json
```

### fetch

Fetch proxies from sources.

```bash
proxywhirl fetch [OPTIONS]
```

**Options:**
```
--sources TEXT          Source IDs (comma-separated, default: all recommended)
--all                   Fetch from all sources
--validate              Validate fetched proxies
--replace               Replace entire pool (with confirmation)
--output FILE           Save to file before importing
--limit INTEGER         Max proxies per source
```

**Examples:**

```bash
# Fetch from default sources
proxywhirl fetch

# Fetch from specific sources
proxywhirl fetch --sources free-proxy-list,proxy-list

# Fetch all and validate
proxywhirl fetch --all --validate

# Save to file without importing
proxywhirl fetch --output proxies.json --sources free-proxy-list
```

### sources

Manage proxy sources.

```bash
proxywhirl sources [COMMAND] [OPTIONS]
```

**Subcommands:**

#### sources list
```bash
proxywhirl sources list [--enabled-only] [--format json|table]
```

#### sources info
```bash
proxywhirl sources info ID [--detailed]
```

#### sources enable
```bash
proxywhirl sources enable ID [ID2 ...]
```

#### sources disable
```bash
proxywhirl sources disable ID [ID2 ...]
```

#### sources test
```bash
proxywhirl sources test [ID] [--timeout SECONDS]
```

**Examples:**

```bash
# List available sources
proxywhirl sources list

# Show details for a source
proxywhirl sources info free-proxy-list --detailed

# Enable source
proxywhirl sources enable proxy-list

# Test source connectivity
proxywhirl sources test free-proxy-list
```

### strategies

Manage rotation strategies.

```bash
proxywhirl strategies [COMMAND]
```

**Subcommands:**

#### strategies list
```bash
proxywhirl strategies list
```

#### strategies current
```bash
proxywhirl strategies current
```

#### strategies switch
```bash
proxywhirl strategies switch STRATEGY_ID [--config JSON]
```

**Examples:**

```bash
# List strategies
proxywhirl strategies list

# Show current strategy
proxywhirl strategies current

# Switch to weighted strategy
proxywhirl strategies switch weighted

# Switch with custom config
proxywhirl strategies switch performance_based --config '{"weight_field": "latency"}'
```

### config

Manage configuration.

```bash
proxywhirl config [COMMAND] [OPTIONS]
```

**Subcommands:**

#### config show
```bash
proxywhirl config show [--full]
```

#### config set
```bash
proxywhirl config set KEY VALUE
```

#### config reset
```bash
proxywhirl config reset [--confirm]
```

**Examples:**

```bash
# Show current config
proxywhirl config show

# Show all settings including defaults
proxywhirl config show --full

# Set option
proxywhirl config set rotation_strategy weighted

# Reset to defaults
proxywhirl config reset --confirm
```

### health

Check proxy health.

```bash
proxywhirl health [OPTIONS]
```

**Options:**
```
--proxy PROXY           Check single proxy
--all                   Check all proxies
--sample SIZE           Check random sample
--detailed              Show detailed health info
--export FILE           Export results
```

**Examples:**

```bash
# Check all proxies
proxywhirl health --all

# Detailed health check
proxywhirl health --detailed

# Check sample
proxywhirl health --sample 50
```

### export

Export proxies to file.

```bash
proxywhirl export FILE [OPTIONS]
```

**Options:**
```
--format FORMAT         Format: json, csv, text (default: json)
--filter STATUS         Export by status
--include-metadata      Include metadata
--include-stats         Include statistics
```

**Examples:**

```bash
# Export as JSON
proxywhirl export proxies.json

# Export as CSV
proxywhirl export proxies.csv --format csv

# Export with metadata
proxywhirl export proxies.json --include-metadata --include-stats

# Export only healthy proxies
proxywhirl export healthy.json --filter healthy
```

### import

Import proxies from file.

```bash
proxywhirl import FILE [OPTIONS]
```

**Options:**
```
--format FORMAT         Format: json, csv, text
--merge                 Merge with existing pool (default: replace)
--validate              Validate before importing
--skip-duplicates       Skip duplicate proxies
```

**Examples:**

```bash
# Import proxies
proxywhirl import proxies.json

# Merge with existing pool
proxywhirl import new_proxies.json --merge

# Import and validate
proxywhirl import proxies.csv --format csv --validate
```

### server

Run API server.

```bash
proxywhirl server [OPTIONS]
```

**Options:**
```
--host HOST             Host to bind (default: 0.0.0.0)
--port PORT             Port (default: 8000)
--reload                Reload on file changes
--workers INTEGER       Number of workers (default: auto)
--ssl-certfile FILE     SSL certificate file
--ssl-keyfile FILE      SSL key file
```

**Examples:**

```bash
# Run API server
proxywhirl server

# Custom host and port
proxywhirl server --host 127.0.0.1 --port 8888

# With SSL
proxywhirl server --ssl-certfile cert.pem --ssl-keyfile key.pem
```

### dashboard

Run TUI dashboard.

```bash
proxywhirl dashboard
```

Interactive real-time monitoring dashboard showing:
- Pool statistics
- Proxy health
- Request metrics
- Circuit breaker status

### version

Show version information.

```bash
proxywhirl version [--verbose]
```

## Common Workflows

### Setup Fresh Proxy Pool

```bash
# Fetch from all recommended sources
proxywhirl fetch --all --validate

# Check pool status
proxywhirl stats

# Export for backup
proxywhirl export backup.json
```

### Daily Maintenance

```bash
# Validate pool
proxywhirl validate --all --update

# Remove unhealthy proxies
proxywhirl remove --filter unhealthy

# Add new proxies
proxywhirl fetch --all

# Check stats
proxywhirl stats --period 7
```

### Performance Optimization

```bash
# Find fastest proxies
proxywhirl list --sort-by latency --limit 50

# Switch to performance-based strategy
proxywhirl strategies switch performance_based

# Monitor with dashboard
proxywhirl dashboard
```

### Troubleshooting

```bash
# Enable debug logging
proxywhirl --log-level DEBUG list

# Detailed health check
proxywhirl health --all --detailed

# Export for analysis
proxywhirl export debug.json --include-metadata --include-stats

# Check config
proxywhirl config show --full
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Validation error |
| 4 | File not found |
| 5 | Permission denied |

## Environment Variables

CLI respects these environment variables:

```bash
PROXYWHIRL_CONFIG          Configuration file path
PROXYWHIRL_LOG_LEVEL       Default log level
PROXYWHIRL_API_KEY         API key for server mode
PROXYWHIRL_STORAGE_PATH    Storage database path
```

## Tips & Tricks

### Batch Operations

```bash
# Validate 1000 proxies in parallel
proxywhirl validate --all --concurrent 100 --update

# Export and reimport to clean up
proxywhirl export clean.json && proxywhirl import clean.json --merge
```

### Piping Output

```bash
# Count proxies
proxywhirl list --format json | jq '. | length'

# Filter proxies by protocol
proxywhirl list --format json | jq '.[] | select(.protocol == "socks5")'

# Get only hosts
proxywhirl list --format json | jq -r '.[].host'
```

### Scheduling

```bash
# Cron job to refresh proxies daily
0 6 * * * proxywhirl fetch --all --validate

# Cron job to validate hourly
0 * * * * proxywhirl validate --sample 500 --update

# Cron job to clean up
0 3 * * 0 proxywhirl remove --filter unhealthy
```

