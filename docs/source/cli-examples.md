# ProxyWhirl CLI Examples

ProxyWhirl exposes a focused CLI for HTTP requests, pool management, source fetching,
health checks, imports, exports, and configuration inspection.

## Installation

```bash
# Install uv first if needed
brew install uv

# Add ProxyWhirl to a uv-managed project
uv add proxywhirl

# Run the project-local CLI
uv run proxywhirl --help

# Or install the CLI as a persistent user tool
uv tool install proxywhirl
```

## Global Options

```bash
# JSON output
proxywhirl --format json pool list

# Custom config path
proxywhirl --config ./proxywhirl.toml pool list

# Verbose logging
proxywhirl --verbose health

# Disable the process lock for read-only help/probing
proxywhirl --no-lock --help
```

## Requests

```bash
# Simple GET through the configured pool
proxywhirl request https://httpbin.org/ip

# Use a specific proxy instead of pool rotation
proxywhirl request --proxy http://proxy.example.com:8080 https://httpbin.org/ip

# POST with JSON data
proxywhirl request --method POST --data '{"status":"ok"}' https://api.example.com/events

# Add headers
proxywhirl request --header "Authorization: Bearer token" https://api.example.com/me
```

## Pool Management

```bash
# List configured proxies
proxywhirl pool list

# Add a proxy
proxywhirl pool add http://proxy.example.com:8080

# Add a proxy with credentials
proxywhirl pool add http://proxy.example.com:8080 --username user --password pass

# Test one proxy against the default target
proxywhirl pool test http://proxy.example.com:8080

# Test one proxy against a custom target
proxywhirl pool test http://proxy.example.com:8080 --target-url https://httpbin.org/ip

# Remove a proxy
proxywhirl pool remove http://proxy.example.com:8080

# Show pool statistics
proxywhirl pool stats
```

## Fetching Sources

```bash
# Fetch, validate, save to database, and export files
proxywhirl fetch

# Faster source smoke test without export files
proxywhirl fetch --timeout 5 --concurrency 100 --no-export

# Revalidate existing database entries
proxywhirl fetch --revalidate --timeout 5 --concurrency 2000 --no-export

# Revalidate and prune failed proxies
proxywhirl fetch --revalidate --prune-failed --timeout 5 --concurrency 2000 --no-export

# Fetch without validation
proxywhirl fetch --no-validate
```

## Validation

```bash
# Validate a single HTTP proxy
proxywhirl validate-proxy http://proxy.example.com:8080

# Validate against a custom target
proxywhirl validate-proxy http://proxy.example.com:8080 --target https://httpbin.org/status/200

# Validate SOCKS with a shorter timeout
proxywhirl validate-proxy socks5://proxy.example.com:1080 --timeout 5
```

## Import And Export

```bash
# Import proxies from JSON, CSV, or plain text
proxywhirl import-proxies proxies.json
proxywhirl import-proxies proxies.csv --format csv --pool backup
proxywhirl import-proxies proxies.txt --format text --no-dedup

# Export proxy data and statistics for the web dashboard
proxywhirl export --output docs/proxy-lists

# Export only stats or only proxy lists
proxywhirl export --stats-only
proxywhirl export --proxies-only --db proxywhirl.db
```

## Health Checks

```bash
# One-shot health check
proxywhirl health

# Continuous health check every 60 seconds
proxywhirl health --continuous --interval 60

# Use a custom target URL
proxywhirl health --target-url https://httpbin.org/ip
```

## Configuration

```bash
# Create a starter config file
proxywhirl config init --output proxywhirl.toml

# Show effective configuration
proxywhirl config show

# Read or write a config key
proxywhirl config get timeout
proxywhirl config set timeout 30
```

## Shell Scripting

```bash
# Capture the response body from a proxied request
proxywhirl request https://httpbin.org/ip > response.txt

# Fail CI if configured proxies are unhealthy
proxywhirl health --target-url https://httpbin.org/ip

# Refresh export artifacts after a source fetch
proxywhirl fetch --timeout 5 --concurrency 100
proxywhirl export --output docs/proxy-lists
```
