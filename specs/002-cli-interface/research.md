# Research: CLI Interface

**Phase 0 Output** | **Date**: 2025-10-25 | **Feature**: 002-cli-interface

## Research Tasks

This document consolidates findings for all unknowns and technology choices identified in the Technical Context.

---

## 1. CLI Framework Selection (Typer vs. Click vs. argparse)

**Decision**: Typer 0.9+

**Rationale**:

- **Modern & Type-Safe**: Built on top of Click but with automatic type validation from Python type hints
- **Native Rich Integration**: Built-in support for Rich progress bars, tables, and formatting
- **Automatic Help Generation**: Generates comprehensive help from docstrings and type hints
- **Less Boilerplate**: Cleaner syntax than Click - function parameters become CLI options automatically
- **Pydantic Integration**: Native support for Pydantic models as CLI arguments
- **Testing Support**: Includes testing utilities compatible with Click's CliRunner
- **Command Groups**: Full support for nested commands (`proxywhirl pool add`, `proxywhirl config set`)
- **Active Development**: Modern, well-maintained, growing ecosystem

**Alternatives Considered**:

- **Click**: Mature but requires more boilerplate; manual type validation
- **argparse**: Built-in, but verbose API, manual help formatting, poor nested command support
- **Fire**: Too magical (auto-generates from function signatures), poor control over UX

**Implementation Notes**:

- Use `typer.Typer()` for app and command groups
- Use function signatures with type hints for automatic option/argument creation
- Use `typer.Option()` and `typer.Argument()` for advanced configuration
- Rich integration is automatic - no additional setup needed

---

## 2. Progress Bar & Formatting Library (Rich vs. tqdm vs. Click.progressbar)

**Decision**: Rich 13.0+

**Rationale**:

- **Comprehensive**: Single library for progress bars, tables, JSON formatting, and color output
- **Dynamic progress**: Supports expanding total count (FR-021: dynamic expansion as items added)
- **Automatic TTY detection**: Disables formatting when piped or redirected (FR-022)
- **Table rendering**: Beautiful tables for `pool list` output (FR-009)
- **JSON pretty-printing**: Syntax-highlighted JSON for `--format json`
- **Maintained**: Active development, widely adopted (over 45k GitHub stars)

**Alternatives Considered**:

- **tqdm**: Excellent progress bars, but no table/formatting support (would need additional library)
- **Click.progressbar**: Basic, but no dynamic expansion, limited styling
- **Colorama**: Only colors, would need separate progress/table libraries

**Implementation Notes**:

- Use `rich.progress.Progress` with `expand=True` for dynamic totals
- Use `rich.table.Table` for pool listings
- Use `rich.console.Console` for all output (auto-detects TTY)
- Use `rich.json.JSON` for `--format json` output
- Typer automatically uses Rich for progress bars and formatting when available

---

## 3. TOML Parsing Strategy (Python 3.9 vs. 3.11+ compatibility)

**Decision**: Conditional import - `tomllib` (Python 3.11+) with `toml` fallback (Python 3.9-3.10)

**Rationale**:

- **Future-proof**: Python 3.11+ has built-in `tomllib` (no dependency)
- **Backward-compatible**: `toml` library provides same API for Python 3.9-3.10
- **Standard compliance**: Both implement TOML 1.0.0 spec
- **Zero cost for modern Python**: No dependency on Python 3.11+

**Alternatives Considered**:

- **toml only**: Simple, but adds unnecessary dependency for Python 3.11+ users
- **tomli**: Read-only, would need separate write library
- **Require Python 3.11+**: Breaks constitution (target 3.9+)

**Implementation Notes**:

```python
try:
    import tomllib  # Python 3.11+
except ImportError:
    import toml as tomllib  # Python 3.9-3.10

# Write support (not in tomllib)
import toml  # Still needed for writing
```

---

## 4. Configuration File Discovery Strategy

**Decision**: Multi-level lookup (project-local → user-global → system defaults)

**Rationale**:

- **Project-local first**: Check `./pyproject.toml` `[tool.proxywhirl]` section (most specific)
- **User-global second**: Check `~/.config/proxywhirl/config.toml` (XDG on Linux/macOS, AppData on Windows)
- **System defaults**: Hard-coded defaults if no config file found
- **Explicit override**: Support `--config <path>` flag to override discovery

**Alternatives Considered**:

- **User-global only**: Simpler, but no per-project configuration
- **Environment variables**: Too limited for complex config structures
- **Single file location**: Inflexible for team workflows

**Implementation Notes**:

```python
def discover_config() -> Path:
    # 1. Explicit --config flag (if provided)
    # 2. ./pyproject.toml [tool.proxywhirl]
    # 3. ~/.config/proxywhirl/config.toml (via platformdirs library)
    # 4. Return None (use defaults)
```

Use `platformdirs` library for cross-platform user config directory.

---

## 5. Lock File Implementation (fcntl vs. filelock library)

**Decision**: `filelock` library 3.12+

**Rationale**:

- **Cross-platform**: Handles fcntl (Unix) and msvcrt (Windows) differences automatically
- **PID tracking**: Can store metadata in lock file (detect stale locks)
- **Timeout support**: Configurable timeout for lock acquisition
- **Context manager**: Clean API with automatic cleanup
- **Battle-tested**: Used by pip, virtualenv, tox

**Alternatives Considered**:

- **fcntl directly**: Unix-only, need separate Windows implementation
- **File existence check**: Race condition - two processes can create simultaneously
- **Process-based check**: Unreliable (PID reuse, remote filesystems)

**Implementation Notes**:

```python
from filelock import FileLock, Timeout

lock_path = config_dir / ".proxywhirl.lock"
lock = FileLock(lock_path, timeout=0)  # Fail immediately

try:
    with lock:
        # Critical section (config writes, pool updates)
except Timeout:
    # Display error with PID from lock file
```

---

## 6. Interactive Confirmation Prompts (typer.confirm vs. questionary)

**Decision**: `typer.confirm()` (built-in)

**Rationale**:

- **Zero dependencies**: Typer already a dependency
- **TTY detection**: Automatically handles non-TTY (returns default)
- **Simple API**: One-line confirmation prompts
- **Consistent UX**: Matches Typer's option/argument patterns
- **Rich integration**: Styled prompts with Rich automatically

**Alternatives Considered**:

- **questionary**: More features (multi-select, autocomplete), but overkill for y/n prompts
- **click.confirm()**: Works but Typer's version has better type safety

**Implementation Notes**:

```python
if not yes_flag and sys.stdout.isatty():
    typer.confirm("Remove proxy from pool?", abort=True)
```

---

## 7. Exit Code Conventions

**Decision**: POSIX-style exit codes

**Rationale**:

- **Standard compliance**: 0 = success, 1 = general error, 2 = misuse/syntax
- **Shell integration**: Enables `&&` and `||` chaining in scripts
- **CI/CD compatibility**: Standard across all platforms

**Exit Code Map**:

- `0`: Success (SC-010: seamless shell integration)
- `1`: General error (network failure, all proxies failed)
- `2`: Invalid usage (unknown command, missing required option)
- `3`: Configuration error (invalid config file, missing credentials)
- `4`: Lock error (another instance running)

**Implementation Notes**:

```python
try:
    # Command logic
    raise typer.Exit(0)
except ConfigError:
    typer.echo("Error: Invalid configuration", err=True)
    raise typer.Exit(3)
```

---

## 8. Output Format Architecture

**Decision**: Strategy pattern with format-specific renderers

**Rationale**:

- **Extensible**: Easy to add new formats (CSV, XML, YAML)
- **Testable**: Each renderer independently testable
- **Clean separation**: Data model decoupled from presentation

**Formats**:

- **human** (default): Rich tables with colors, progress bars
- **json**: Machine-readable, parseable by jq (SC-005)
- **table**: ASCII tables (no colors), stable for scripts
- **csv**: Comma-separated, Excel-compatible

**Implementation Notes**:

```python
class OutputRenderer(Protocol):
    def render_proxy_list(self, proxies: List[Proxy]) -> str: ...
    def render_request_response(self, response: Response) -> str: ...

class HumanRenderer(OutputRenderer): ...  # Rich tables
class JsonRenderer(OutputRenderer): ...   # JSON.dumps
class TableRenderer(OutputRenderer): ...  # ASCII tables
class CsvRenderer(OutputRenderer): ...    # csv.writer
```

---

## Summary

All technical unknowns resolved. Key decisions:

1. **Typer 0.9+** for CLI framework (modern, type-safe, Rich integration, less boilerplate)
2. **Rich 13.0+** for progress bars and formatting (comprehensive, TTY-aware, native Typer support)
3. **tomllib/toml** conditional import (Python 3.9-3.13 compatibility)
4. **Multi-level config discovery** (project → user → defaults)
5. **filelock 3.12+** for cross-platform locking (PID tracking, timeout)
6. **typer.confirm()** for interactive prompts (built-in, TTY-aware, Rich styling)
7. **POSIX exit codes** (0=success, 1-4=errors, shell-compatible)
8. **Strategy pattern** for output formats (extensible, testable)

No blocking unknowns remain. Ready for Phase 1 (Design & Contracts).
