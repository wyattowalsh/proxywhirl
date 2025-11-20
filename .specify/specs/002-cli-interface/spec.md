# Feature Specification: CLI Interface

**Feature Branch**: `002-cli-interface`  
**Created**: 2025-10-08  
**Status**: Draft  
**Input**: User description: "Command-line tool for managing and using proxies"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Make Request Through Proxy via CLI (Priority: P1)

A user wants to quickly make HTTP requests through rotating proxies from the command line without writing any code. They run a simple command with a URL and proxy list, and get the response immediately.

**Why this priority**: This is the core CLI functionality - enabling quick proxy usage from terminal for testing, debugging, or scripting.

**Independent Test**: Can be fully tested by running a CLI command with a URL and proxy list file, verifying the request uses a proxy and returns the response.

**Acceptance Scenarios**:

1. **Given** a proxy list file, **When** user runs `proxywhirl get https://api.example.com --proxies proxies.txt`, **Then** the request is made through a proxy and response is displayed
2. **Given** multiple requests, **When** user runs the command multiple times, **Then** each request uses a different proxy from the rotation pool
3. **Given** a failed proxy, **When** making a request, **Then** the CLI automatically retries with the next proxy and displays success

---

### User Story 2 - Manage Proxy Pool from CLI (Priority: P2)

A user wants to view, add, remove, and validate proxies in their proxy pool using command-line commands, making proxy management scriptable and automatable.

**Why this priority**: Essential for operational management - users need to inspect and modify proxy pools without editing files manually.

**Independent Test**: Can be tested by running pool management commands and verifying proxies are added/removed/listed correctly.

**Acceptance Scenarios**:

1. **Given** a proxy pool, **When** user runs `proxywhirl pool list`, **Then** all active proxies are displayed with their status
2. **Given** a new proxy URL, **When** user runs `proxywhirl pool add http://proxy.example.com:8080`, **Then** the proxy is validated and added to the pool
3. **Given** a proxy in the pool, **When** user runs `proxywhirl pool remove <proxy-id>`, **Then** the proxy is removed from rotation
4. **Given** a proxy pool, **When** user runs `proxywhirl pool test`, **Then** all proxies are health-checked and status is reported

---

### User Story 3 - Configure CLI Settings (Priority: P2)

A user wants to save frequently-used settings (default proxies, rotation strategy, timeouts) in a configuration file so they don't have to specify them on every command.

**Why this priority**: Improves user experience for repeated usage - configuration management is essential for productivity.

**Independent Test**: Can be tested by setting configuration values and verifying they are applied to subsequent commands without re-specification.

**Acceptance Scenarios**:

1. **Given** a clean environment, **When** user runs `proxywhirl config init`, **Then** a configuration file is created with default settings
2. **Given** a configuration file, **When** user runs `proxywhirl config set rotation-strategy round-robin`, **Then** the setting is saved and applied to future commands
3. **Given** saved configurations, **When** user runs requests without flags, **Then** saved settings are automatically applied

---

### User Story 4 - Output Formatting and Piping (Priority: P3)

A user wants to format CLI output as JSON, plain text, or other formats for parsing in scripts or piping to other command-line tools.

**Why this priority**: Enables CLI integration with automation workflows - critical for advanced users and DevOps scenarios.

**Independent Test**: Can be tested by requesting different output formats and verifying the structure matches the specified format.

**Acceptance Scenarios**:

1. **Given** a request command, **When** user adds `--format json`, **Then** response and metadata are output as valid JSON
2. **Given** a pool list command, **When** user adds `--format table`, **Then** proxies are displayed in a formatted table
3. **Given** CLI output, **When** user pipes to another command (e.g., `| jq`), **Then** output format is parseable by standard tools

---

### Edge Cases

- What happens when the proxy list file doesn't exist or is empty? *(CLI should display clear error: "Proxy list not found at `<path>`" with suggestion to use --help)*
- How does the CLI handle invalid command syntax or unknown subcommands? *(Display usage help with "Unknown command: `<cmd>`. Did you mean `<suggestion>`?")*
- What occurs when all proxies fail during a CLI request? *(Exit with code 1 and error: "All proxies failed. Check pool health with 'proxywhirl pool test'")*
- How are authentication credentials handled when specified via command-line arguments (security concern)? *(Warn users that CLI args visible in process list; prefer config file or env vars)*
- What happens when configuration file has invalid or conflicting settings? *(Validate on load, display specific errors with line numbers, fall back to defaults)*
- How does the CLI behave when network connectivity is unavailable? *(Fail fast with network error, suggest offline mode if applicable)*
- What occurs when output exceeds terminal width or buffer limits? *(Use paging for large outputs, truncate with "... and N more" indicators)*
- How does lock file handle crashes or orphaned locks? *(Include PID in lock file, check if process still running, auto-cleanup stale locks)*
- What happens during concurrent read-only operations (pool list)? *(Allow concurrent reads, only lock for write operations)*

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: CLI MUST provide a `get` command to make HTTP GET requests through proxies
- **FR-002**: CLI MUST provide a `post` command to make HTTP POST requests with body data through proxies
- **FR-003**: CLI MUST accept proxy lists from files, command-line arguments, or stdin
- **FR-004**: CLI MUST support all common HTTP methods (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
- **FR-005**: CLI MUST provide `pool list`, `pool add`, `pool remove`, and `pool test` subcommands for proxy management
- **FR-006**: CLI MUST display proxy health status (active, failed, slow) in pool listings
- **FR-007**: CLI MUST support configuration file initialization and settings management via `config` subcommand
- **FR-008**: CLI MUST allow specifying rotation strategy via command-line flag or configuration
- **FR-009**: CLI MUST support multiple output formats (human-readable, JSON, table, CSV)
- **FR-010**: CLI MUST provide `--verbose` and `--quiet` flags to control output verbosity
- **FR-011**: CLI MUST display helpful error messages with actionable suggestions (target: 90% of failures include next steps per SC-007)
- **FR-012**: CLI MUST support `--help` flag for all commands and subcommands with usage examples
- **FR-013**: CLI MUST allow setting request headers via command-line arguments
- **FR-014**: CLI MUST support timeout configuration (connection, read, total) via flags
- **FR-015**: CLI SHOULD provide `--dry-run` mode to preview actions without execution (deferred to post-MVP)
- **FR-016**: CLI MUST support reading request body from stdin (if present), else --file argument, else --data flag for POST/PUT requests
- **FR-017**: CLI MUST follow redirects by default with option to disable via flag
- **FR-018**: CLI MUST return appropriate exit codes (0 for success, non-zero for errors)
- **FR-019**: CLI MUST prompt for confirmation on destructive actions (pool remove, config reset) unless `--yes` or `-y` flag is provided
- **FR-020**: CLI MUST detect TTY status and adjust behavior: disable interactive prompts when not TTY (for automation/scripting)
- **FR-021**: CLI MUST display progress bars for long-running operations (>3 seconds expected duration: proxy validation, batch requests) with dynamic total count expansion
- **FR-022**: CLI MUST disable progress bars and ANSI colors when output is not a TTY or when `--quiet` flag is used (part of TTY awareness per FR-020)
- **FR-023**: CLI MUST use lock files to prevent concurrent execution that could corrupt configuration or pool state
- **FR-024**: CLI MUST provide clear error message when lock file exists, suggesting wait or use of `--force` flag to override (with warning)

### Key Entities

- **CLI Command**: User-invoked command with subcommands, options, and arguments
- **Request Configuration**: URL, method, headers, body, and proxy settings for HTTP requests
- **CLI Configuration**: Persistent settings stored in configuration file (proxies, rotation strategy, defaults)
- **Output Format**: Structure for displaying results (JSON, table, text, CSV)
- **Command Output**: Response data, proxy metadata, and execution status displayed to user

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can make their first proxied request in under 30 seconds after installation
- **SC-002**: CLI help documentation is accessible within 2 keystrokes for any command
- **SC-003**: 95% of common use cases require 5 or fewer command-line flags
- **SC-004**: CLI commands execute and return results in under 2 seconds for simple requests
- **SC-005**: JSON output from all commands is valid and parseable by standard tools (jq, python json module)
- **SC-006**: CLI works identically across Linux, macOS, and Windows with no platform-specific behavior
- **SC-007**: Error messages include actionable suggestions in 90% of failure scenarios
- **SC-008**: CLI binary size is under 10MB for easy distribution
- **SC-009**: Configuration changes persist across CLI sessions without data loss
- **SC-010**: CLI integrates seamlessly with shell scripts and automation workflows

## Clarifications

### Session 2025-10-25

- Q: What format should the CLI configuration file use? → A: Use pyproject.toml (existing project standard)
- Q: How should credentials be encrypted in the configuration file? → A: Reuse existing Fernet (cryptography library) - Already used in Phase 2 File Storage
- Q: Should destructive CLI actions require interactive confirmation? → A: Interactive prompts with --yes flag - Ask "Are you sure?" by default, skip with -y/--yes
- Q: Should long-running operations display progress indicators? → A: Progress bar with percentage - Dynamic expansion as items added to iterator
- Q: How should concurrent CLI executions be handled? → A: Lock file with graceful failure - Create .lock file, fail with clear error if locked

## Assumptions

- Users have basic command-line interface experience
- Terminal environment supports ANSI color codes for enhanced output (degrades gracefully if not)
- Configuration file uses TOML format (pyproject.toml) for consistency with project standards
- CLI configuration is stored in `[tool.proxywhirl]` section of pyproject.toml when project-local, or `~/.config/proxywhirl/config.toml` for global settings
- Configuration file is stored in standard OS-specific config directories (XDG on Linux, ~/Library on macOS, AppData on Windows)
- Users have read/write permissions to configuration directory
- Proxy credentials are encrypted using Fernet (cryptography library) - same implementation as Phase 2 File Storage
- Encrypted credentials are stored in configuration files with appropriate file permissions (600)
- CLI inherits environment variables from shell (e.g., HTTP_PROXY, NO_PROXY)

## Dependencies

- Core Python Package (Phase 1) for proxy rotation logic
- Storage & Health Monitoring (Phase 2) for persistent pools and proxy status tracking
- Configuration encryption (Phase 2 FileStorage) for credential security
