# CLI Command Schema

**Feature**: 002-cli-interface | **Date**: 2025-10-25

This document defines the complete CLI command structure, options, and arguments for the ProxyWhirl CLI.

## Command Hierarchy

```text
proxywhirl
├── get <url>              # Make HTTP GET request through proxy
├── post <url>             # Make HTTP POST request through proxy
├── put <url>              # Make HTTP PUT request through proxy
├── delete <url>           # Make HTTP DELETE request through proxy
├── pool                   # Proxy pool management
│   ├── list               # List all proxies in pool
│   ├── add <proxy-url>    # Add proxy to pool
│   ├── remove <proxy-id>  # Remove proxy from pool
│   └── test               # Health-check all proxies
└── config                 # Configuration management
    ├── init               # Initialize new config file
    ├── get <key>          # Get configuration value
    ├── set <key> <value>  # Set configuration value
    └── show               # Show all configuration
```

---

## Global Options

Available for all commands:

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--config` | `-c` | PATH | (auto-discover) | Path to configuration file |
| `--format` | `-f` | CHOICE | human | Output format: human, json, table, csv |
| `--verbose` | `-v` | FLAG | false | Enable verbose output |
| `--quiet` | `-q` | FLAG | false | Suppress non-essential output |
| `--help` | `-h` | FLAG | - | Show help message and exit |
| `--version` | | FLAG | - | Show version and exit |

---

## HTTP Request Commands

### `proxywhirl get <url>`

Make HTTP GET request through rotating proxies.

**Arguments**:

- `url` (required): Target URL to fetch

**Options**:

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--proxies` | `-p` | PATH | (from config) | Path to proxy list file |
| `--proxy` | | TEXT | (from rotation) | Use specific proxy URL |
| `--strategy` | `-s` | CHOICE | round-robin | Rotation strategy |
| `--headers` | `-H` | TEXT | - | Request headers (multiple allowed) |
| `--timeout` | `-t` | INT | 30 | Request timeout (seconds) |
| `--retries` | `-r` | INT | 3 | Max retry attempts |
| `--no-redirects` | | FLAG | false | Disable redirect following |
| `--no-verify` | | FLAG | false | Disable SSL verification |
| `--output` | `-o` | PATH | (stdout) | Save response to file |

**Examples**:

```bash
# Basic request
proxywhirl get https://api.example.com

# With custom headers
proxywhirl get https://api.example.com -H "Authorization: Bearer TOKEN"

# Output as JSON
proxywhirl get https://api.example.com --format json

# Use specific proxy
proxywhirl get https://api.example.com --proxy http://proxy.example.com:8080
```

**Exit Codes**:

- `0`: Success (2xx status code)
- `1`: Request failed (all proxies failed or network error)
- `2`: Invalid usage (missing URL, invalid options)

---

### `proxywhirl post <url>`

Make HTTP POST request through rotating proxies.

**Arguments**:

- `url` (required): Target URL for POST request

**Options**:

All options from `get` command, plus:

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--data` | `-d` | TEXT | - | Request body (string) |
| `--json` | `-j` | TEXT | - | JSON request body |
| `--file` | | PATH | - | Read body from file |
| `--form` | `-F` | TEXT | - | Form data (multiple allowed) |

**Examples**:

```bash
# POST JSON data
proxywhirl post https://api.example.com/users --json '{"name": "Alice"}'

# POST from file
proxywhirl post https://api.example.com/upload --file data.json

# POST form data
proxywhirl post https://api.example.com/login \
  --form "username=user" \
  --form "password=pass"
```

---

### `proxywhirl put <url>`, `proxywhirl delete <url>`

Same structure as `post` command.

---

## Pool Management Commands

### `proxywhirl pool list`

List all proxies in the pool with health status.

**Options**:

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--status` | | CHOICE | all | Filter: all, healthy, degraded, failed |
| `--sort` | | CHOICE | url | Sort by: url, health, response_time |

**Output (human format)**:

```text
Proxy Pool (5 total, 3 healthy, 1 degraded, 1 failed)

URL                              STATUS     RESPONSE  SUCCESS  REQUESTS
http://proxy1.example.com:8080   healthy    45ms      100%     1,234
http://proxy2.example.com:8080   healthy    67ms      98%      987
http://proxy3.example.com:8080   degraded   234ms     85%      456
socks5://proxy4.example.com:1080 failed     -         0%       23
http://proxy5.example.com:8080   healthy    52ms      99%      2,001
```

**Output (json format)**:

```json
{
  "total_proxies": 5,
  "healthy": 3,
  "degraded": 1,
  "failed": 1,
  "rotation_strategy": "round-robin",
  "proxies": [
    {
      "url": "http://proxy1.example.com:8080",
      "health": "healthy",
      "response_time_ms": 45,
      "success_rate": 1.0,
      "total_requests": 1234
    }
  ]
}
```

---

### `proxywhirl pool add <proxy-url>`

Add a proxy to the pool.

**Arguments**:

- `proxy-url` (required): Proxy URL (http://host:port or socks5://host:port)

**Options**:

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--username` | `-u` | TEXT | - | Proxy username |
| `--password` | `-p` | TEXT | - | Proxy password (prompted if omitted) |
| `--validate` | | FLAG | true | Validate proxy before adding |
| `--force` | | FLAG | false | Skip confirmation prompt |

**Examples**:

```bash
# Add simple proxy
proxywhirl pool add http://proxy.example.com:8080

# Add with authentication (password prompted)
proxywhirl pool add http://proxy.example.com:8080 -u myuser

# Add without validation
proxywhirl pool add http://proxy.example.com:8080 --no-validate
```

**Exit Codes**:

- `0`: Proxy added successfully
- `1`: Validation failed (proxy unreachable)
- `2`: Invalid proxy URL format
- `3`: Proxy already exists in pool

---

### `proxywhirl pool remove <proxy-id>`

Remove a proxy from the pool.

**Arguments**:

- `proxy-id` (required): Proxy URL or numeric ID from `pool list`

**Options**:

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--yes` | `-y` | FLAG | false | Skip confirmation prompt |
| `--force` | | FLAG | false | Remove even if active requests |

**Interactive Confirmation**:

```text
Remove proxy http://proxy.example.com:8080 from pool? [y/N]:
```

---

### `proxywhirl pool test`

Health-check all proxies in the pool.

**Options**:

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--timeout` | `-t` | INT | 10 | Test timeout per proxy (seconds) |
| `--parallel` | | INT | 10 | Number of concurrent tests |

**Output**:

```text
Testing 5 proxies...

[█████████████████████         ] 60% (3/5) - 2s elapsed

✓ http://proxy1.example.com:8080 - 45ms
✓ http://proxy2.example.com:8080 - 67ms
✗ http://proxy3.example.com:8080 - Connection timeout
✓ http://proxy4.example.com:8080 - 52ms
✗ http://proxy5.example.com:8080 - 502 Bad Gateway

Results: 3 healthy, 0 degraded, 2 failed
```

---

## Configuration Commands

### `proxywhirl config init`

Initialize a new configuration file.

**Options**:

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--global` | `-g` | FLAG | false | Create global config (~/.config/proxywhirl/) |
| `--local` | `-l` | FLAG | true | Create project-local config (./pyproject.toml) |
| `--force` | | FLAG | false | Overwrite existing config |

**Output**:

```text
Created configuration file: ./pyproject.toml

[tool.proxywhirl]
rotation_strategy = "round-robin"
timeout = 30
default_format = "human"
encrypt_credentials = true
proxies = []

Edit this file to customize settings.
Run 'proxywhirl config set <key> <value>' to update.
```

---

### `proxywhirl config get <key>`

Get a configuration value.

**Arguments**:

- `key` (required): Configuration key (dot-notation for nested keys)

**Examples**:

```bash
proxywhirl config get rotation_strategy
# Output: round-robin

proxywhirl config get timeout
# Output: 30
```

---

### `proxywhirl config set <key> <value>`

Set a configuration value.

**Arguments**:

- `key` (required): Configuration key
- `value` (required): New value

**Examples**:

```bash
proxywhirl config set rotation_strategy random
proxywhirl config set timeout 60
proxywhirl config set default_format json
```

**Validation**:

- Strategy must be one of: round-robin, random, weighted, least-used
- Format must be one of: human, json, table, csv
- Timeout must be positive integer

---

### `proxywhirl config show`

Show all configuration values.

**Output (human format)**:

```text
Configuration (/Users/alice/project/pyproject.toml)

Proxy Pool:
  proxies:              2 configured
  rotation_strategy:    round-robin
  health_check_interval: 300

Request Settings:
  timeout:              30
  max_retries:          3
  follow_redirects:     true
  verify_ssl:           true

Output Settings:
  default_format:       human
  color:                true
  verbose:              false

Storage Settings:
  storage_backend:      file
  storage_path:         ~/.local/share/proxywhirl/proxies.json

Security:
  encrypt_credentials:  true
  encryption_key_env:   PROXYWHIRL_KEY
```

---

## Lock File Behavior

All write operations acquire a lock file to prevent concurrent corruption:

**Write Operations** (acquire lock):

- `pool add`
- `pool remove`
- `config set`
- `config init`

**Read Operations** (no lock):

- `get`, `post`, `put`, `delete` (read-only pool usage)
- `pool list`
- `pool test`
- `config get`
- `config show`

**Lock Error**:

```text
Error: Another proxywhirl process is running (PID 12345)
Wait for the command to finish, or use --force to override (unsafe).
```

---

## TTY Detection

Interactive features automatically disabled when not TTY:

- Progress bars → Disabled
- ANSI colors → Disabled
- Confirmation prompts → Auto-accept with `--yes` default
- Tables → Plain text format

**Check**: `sys.stdout.isatty()` and `sys.stdin.isatty()`

---

## Error Messages

Examples of helpful error messages (FR-011):

```text
Error: Proxy list file not found: proxies.txt
Tip: Create the file or use --proxy to specify a proxy URL directly.

Error: Unknown command: 'poo'
Did you mean: 'pool'?

Error: All 5 proxies failed to connect
Tip: Check pool health with 'proxywhirl pool test'

Error: Invalid rotation strategy: 'round'
Valid strategies: round-robin, random, weighted, least-used
```

---

## Summary

**Total Commands**: 15

- HTTP requests: 4 (get, post, put, delete)
- Pool management: 4 (list, add, remove, test)
- Configuration: 4 (init, get, set, show)

**Total Options**: 35+ (including global options across all commands)

**Output Formats**: 4 (human, json, table, csv)

**Exit Codes**: 5 (0=success, 1=general error, 2=usage error, 3=config error, 4=lock error)

All commands follow POSIX conventions and Click best practices.
