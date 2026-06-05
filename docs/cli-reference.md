# ProxyWhirl CLI Reference

## Overview

ProxyWhirl exposes a focused Typer-based CLI for proxy requests, pool management, health checks, fetching, imports, and export workflows.

```bash
proxywhirl --help
```

## Global Options

These options apply before the subcommand name:

```text
--config, -c FILE        Path to TOML config file
--format, -f FORMAT      Output format: text, json, csv, or yaml
--verbose, -v            Enable verbose logging
--no-lock                Disable file locking for this invocation
--help                   Show help
```

## Commands

```text
request         Make an HTTP request through a rotating proxy
export          Export proxy data and statistics for the web dashboard
fetch           Fetch proxies from configured sources
health          Check health of all proxies in the pool
validate-proxy  Validate one proxy URL
import-proxies  Import proxies from JSON, CSV, or plain text
pool            Manage configured proxies
config          Manage CLI configuration
```

## request

```bash
proxywhirl request [OPTIONS] URL
```

Common options:

```text
--method, -X METHOD      HTTP method, default GET
--header, -H HEADER      Repeatable header in "Key: Value" format
--data, -d DATA          Request body data
--proxy, -p URL          Use a specific proxy instead of pool rotation
--retries INTEGER        Override configured retry count
--allow-private          Permit localhost/private target URLs
```

Examples:

```bash
proxywhirl request https://api.example.com/data
proxywhirl request -X POST -d '{"ok": true}' https://api.example.com/submit
proxywhirl --format json request https://api.example.com/data
```

## pool

```bash
proxywhirl pool COMMAND [ARGS]...
```

Subcommands:

```text
list     List configured proxies
add      Add a proxy to the active config
remove   Remove a proxy from the active config
test     Test proxy connectivity
stats    Show pool statistics
```

Examples:

```bash
proxywhirl pool list
proxywhirl pool add http://proxy.example.com:8080
proxywhirl pool add http://proxy.example.com:8080 --username user --password pass
proxywhirl pool remove http://proxy.example.com:8080
proxywhirl pool test http://proxy.example.com:8080 --target-url https://httpbin.org/ip
proxywhirl pool stats
```

## config

```bash
proxywhirl config COMMAND [ARGS]...
```

Subcommands:

```text
init    Create a starter config file
show    Print active configuration
get     Print a single config value
set     Set a config value
```

Examples:

```bash
proxywhirl config init
proxywhirl config show
proxywhirl config get rotation_strategy
proxywhirl config set rotation_strategy random
```

## health

```bash
proxywhirl health [OPTIONS]
```

Options:

```text
--continuous, -C         Run continuously
--interval, -i INTEGER   Check interval in seconds
--target-url, -t URL     URL to test connectivity against
--allow-private          Permit localhost/private target URLs
```

Examples:

```bash
proxywhirl health
proxywhirl health --continuous --interval 60
proxywhirl health --target-url https://api.example.com
```

## fetch

```bash
proxywhirl fetch [OPTIONS]
```

Options:

```text
--no-validate            Skip proxy validation
--no-save-db             Do not save to proxywhirl.db
--no-export              Do not write docs/proxy-lists outputs
--timeout INTEGER        Validation timeout in seconds
--concurrency INTEGER    Concurrent validation requests
--revalidate, -R         Re-validate existing database proxies
--revalidate-limit INT   Revalidate oldest N proxies, or 0 for all
--prune-failed           Delete failed proxies during revalidation
--https-validate / --no-https-validate
--https-timeout INTEGER  HTTPS CONNECT validation timeout
--https-max INTEGER      Maximum HTTPS-capable proxies to collect
```

Examples:

```bash
proxywhirl fetch
proxywhirl fetch --no-validate
proxywhirl fetch --timeout 5 --concurrency 50
proxywhirl fetch --revalidate --prune-failed
```

## export

```bash
proxywhirl export [OPTIONS]
```

Options:

```text
--output, -o PATH        Output directory, default docs/proxy-lists
--db PATH                SQLite database path, default proxywhirl.db
--stats-only             Export only statistics
--proxies-only           Export only proxy list
```

Examples:

```bash
proxywhirl export
proxywhirl export --output ./exports
proxywhirl export --stats-only
proxywhirl export --proxies-only --db custom.db
```

## validate-proxy

```bash
proxywhirl validate-proxy [OPTIONS] PROXY_URL
```

Options:

```text
--target, -t URL         Target URL, default https://httpbin.org/ip
--timeout FLOAT          Request timeout in seconds
```

Examples:

```bash
proxywhirl validate-proxy http://proxy.example.com:8080
proxywhirl validate-proxy socks5://proxy.example.com:1080 --timeout 5
```

## import-proxies

```bash
proxywhirl import-proxies [OPTIONS] FILE_PATH
```

Options:

```text
--format, -f FORMAT      auto, json, csv, or text
--pool, -p NAME          Target pool name, default imported
--dedup / --no-dedup     Deduplicate proxies before import
```

Examples:

```bash
proxywhirl import-proxies proxies.json
proxywhirl import-proxies proxies.csv --format csv
proxywhirl import-proxies proxies.txt --format text --pool backup
```

## Common Workflows

### Refresh and Export

```bash
proxywhirl fetch --timeout 5 --concurrency 100
proxywhirl export
```

### Revalidate Existing Database

```bash
proxywhirl fetch --revalidate --prune-failed --timeout 5 --concurrency 2000 --no-export
proxywhirl export
```

### Import a Local Proxy File

```bash
proxywhirl import-proxies proxies.txt --format text --pool imported
proxywhirl pool list
```

## Exit Codes

| Code | Meaning                                                                      |
| ---- | ---------------------------------------------------------------------------- |
| 0    | Success                                                                      |
| 1    | General error, invalid input, failed validation, or lock acquisition failure |

## Environment Variables

```bash
PROXYWHIRL_KEY                   Master encryption key
PROXYWHIRL_CACHE_ENCRYPTION_KEY  Cache encryption key
PROXYWHIRL_STORAGE_PATH          SQLite storage path for API workflows
PROXYWHIRL_API_KEY               API authentication key
```

See `docs/source/guides/cli-reference.md` for the Sphinx guide with rendered tables and examples.
