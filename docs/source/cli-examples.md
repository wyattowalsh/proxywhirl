# ProxyWhirl CLI: Comprehensive Examples

## Installation

```bash
pip install proxywhirl
# or with uv
uv pip install proxywhirl
```

## Basic Usage

### Get a Single Proxy

```bash
proxywhirl get --count 1
```

Output:
```
http://192.168.1.1:8080
```

### Get Multiple Proxies

```bash
proxywhirl get --count 5
```

### Get Proxies by Country

```bash
proxywhirl get --country US --count 3
proxywhirl get --country FR,DE --count 5
```

### Get Specific Proxy Type

```bash
proxywhirl get --type http --count 3
proxywhirl get --type socks5 --count 5
```

## Advanced Options

### Validation Levels

```bash
# Strict validation (slowest, most reliable)
proxywhirl get --validation strict

# Moderate validation (balanced)
proxywhirl get --validation moderate

# Light validation (fastest)
proxywhirl get --validation light
```

### Export Formats

```bash
# JSON output
proxywhirl get --format json --output proxies.json

# CSV output
proxywhirl get --format csv --output proxies.csv

# YAML output
proxywhirl get --format yaml --output proxies.yaml
```

### Performance Filtering

```bash
# Get fast proxies only
proxywhirl get --performance fast --count 5

# Get high-quality residential proxies
proxywhirl get --residential --performance high
```

## Health Checks

### Check Proxy Health

```bash
proxywhirl health check http://192.168.1.1:8080
```

### Batch Health Check

```bash
proxywhirl health check --file proxies.txt --timeout 30
```

### Health Statistics

```bash
proxywhirl health stats
```

## Source Management

### List Available Sources

```bash
proxywhirl source list
```

### Refresh Specific Source

```bash
proxywhirl source refresh --name free-proxy-list
```

### Refresh All Sources

```bash
proxywhirl source refresh --all
```

### Add Custom Source

```bash
proxywhirl source add \
  --name my-source \
  --url https://example.com/proxies \
  --format json
```

## Cache Management

### Clear Cache

```bash
proxywhirl cache clear
```

### Cache Statistics

```bash
proxywhirl cache stats
```

### Warm Cache

```bash
proxywhirl cache warm --file proxies.json
```

## Configuration

### Show Current Config

```bash
proxywhirl config show
```

### Set Configuration

```bash
proxywhirl config set \
  --validation strict \
  --cache-ttl 3600 \
  --max-retries 3
```

### Export Configuration

```bash
proxywhirl config export --output config.yaml
```

### Import Configuration

```bash
proxywhirl config import --file config.yaml
```

## Database Operations

### Export Database

```bash
proxywhirl db export --output backup.db
```

### Import Database

```bash
proxywhirl db import --file backup.db
```

### Database Statistics

```bash
proxywhirl db stats
```

## Batch Operations

### Validate Proxy List

```bash
proxywhirl validate --file proxies.txt \
  --timeout 30 \
  --output validated.txt
```

### Deduplicate Proxies

```bash
proxywhirl deduplicate --file proxies.txt \
  --output unique.txt
```

### Filter Proxies

```bash
proxywhirl filter --file proxies.txt \
  --country US \
  --type http \
  --output filtered.txt
```

## Performance Analysis

### Benchmark Sources

```bash
proxywhirl benchmark --timeout 60
```

### Profile Cache Performance

```bash
proxywhirl profile --duration 3600
```

## TUI Dashboard

### Launch Interactive Dashboard

```bash
proxywhirl tui
```

Dashboard includes:
- Live proxy list
- Health status
- Performance metrics
- Cache statistics
- Source status

## Common Workflows

### Fetch and Validate High-Quality Proxies

```bash
# Get fresh proxies
proxywhirl source refresh --all

# Fetch high-performance proxies
proxywhirl get --count 50 \
  --validation strict \
  --format json \
  --output proxies.json

# Export for use
proxywhirl export --file proxies.json --format csv
```

### Setup with Custom Sources

```bash
# Add custom source
proxywhirl source add --name api-source \
  --url https://api.example.com/proxies \
  --format json

# Configure validation
proxywhirl config set --validation strict

# Get proxies
proxywhirl get --count 10 --format json
```

### Monitor Proxy Quality

```bash
# Get statistics
proxywhirl health stats

# Check cache performance
proxywhirl cache stats

# Profile performance
proxywhirl profile
```

## Environment Variables

```bash
export PROXYWHIRL_VALIDATION=strict
export PROXYWHIRL_CACHE_TTL=3600
export PROXYWHIRL_LOG_LEVEL=DEBUG
proxywhirl get
```

## Piping and Scripting

### Use with wget

```bash
PROXY=$(proxywhirl get --count 1)
wget --proxy http://$PROXY https://example.com
```

### Use with curl

```bash
PROXY=$(proxywhirl get --count 1)
curl -x http://$PROXY https://example.com
```

### Batch Processing

```bash
for i in {1..5}; do
  PROXY=$(proxywhirl get --count 1)
  echo "Request $i with proxy: $PROXY"
  curl -x http://$PROXY https://example.com
done
```

