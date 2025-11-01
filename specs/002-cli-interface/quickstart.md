# Quickstart Guide: CLI Interface

**Feature**: 002-cli-interface | **Date**: 2025-10-25

This quickstart guide helps developers understand how to implement and test the CLI Interface feature.

---

## Prerequisites

1. **Phase 1 & 2 Complete**: Core library with proxy rotation, validation, and storage
1. **Python 3.9+**: Installed and active
1. **Dependencies Installed**:

```bash
uv add typer>=0.9.0 rich>=13.0.0 filelock>=3.12.0 platformdirs>=3.0.0
```

1. **Test Framework Ready**:

```bash
uv add --dev pytest  # Typer testing uses standard pytest with typer.testing
```

---

## Development Workflow

### Step 1: Create Config Module (`proxywhirl/config.py`)

**Purpose**: Handle TOML configuration discovery, loading, encryption

**Key Functions**:

```python
def discover_config(explicit_path: Optional[Path] = None) -> Path:
    """Find config file (project → user → defaults)."""

def load_config(path: Path) -> CLIConfig:
    """Load and validate TOML configuration."""

def save_config(config: CLIConfig, path: Path) -> None:
    """Save configuration with credential encryption."""

def encrypt_credentials(config: CLIConfig, key: bytes) -> CLIConfig:
    """Encrypt all SecretStr fields using Fernet."""

def decrypt_credentials(config: CLIConfig, key: bytes) -> CLIConfig:
    """Decrypt all encrypted credential fields."""
```

**Test-First**:

```python
# tests/unit/test_config.py
def test_discover_config_project_local(tmp_path):
    """Should find ./pyproject.toml first."""

def test_load_config_valid_toml():
    """Should parse valid TOML into CLIConfig model."""

def test_save_config_encrypts_credentials():
    """Should encrypt passwords before writing."""

def test_config_file_permissions():
    """Should create config with 600 permissions."""
```

---

### Step 2: Create CLI Module (`proxywhirl/cli.py`)

**Purpose**: Typer command definitions and entry point

**Structure**:

```python
import typer
from typing import Optional
from pathlib import Path
from .config import load_config, discover_config
from .models import CommandContext

# Create main app
app = typer.Typer(
    name="proxywhirl",
    help="ProxyWhirl CLI - Proxy rotation made simple.",
    add_completion=False  # Disable shell completion for now
)

# Create command groups
pool_app = typer.Typer(help="Manage proxy pool.")
config_app = typer.Typer(help="Manage configuration.")

app.add_typer(pool_app, name="pool")
app.add_typer(config_app, name="config")

# Shared state (Typer reuses click.Context via typer.Context)
# We'll use a callback to set up shared state
@app.callback()
def main(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
    format: str = typer.Option("human", "--format", "-f", help="Output format"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """ProxyWhirl CLI - Proxy rotation made simple."""
    config_path = discover_config(config)
    config_obj = load_config(config_path)
    ctx.obj = CommandContext(
        config=config_obj,
        output_format=format,
        verbose=verbose,
        config_path=config_path
    )

# HTTP Request Commands
@app.command()
def get(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="URL to fetch"),
    proxies: Optional[Path] = typer.Option(None, "--proxies", "-p", help="Proxy list file"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Request timeout in seconds"),
):
    """Make HTTP GET request through proxy."""
    rotator = ctx.obj.get_rotator()
    # Implementation...

# Pool Management Commands
@pool_app.command("list")
def pool_list(ctx: typer.Context):
    """List all proxies."""
    # Implementation...

@pool_app.command("add")
def pool_add(
    ctx: typer.Context,
    proxy_url: str = typer.Argument(..., help="Proxy URL to add"),
    username: Optional[str] = typer.Option(None, "--username", "-u"),
    password: Optional[str] = typer.Option(None, "--password", "-p"),
):
    """Add proxy to pool."""
    # Implementation...

# Config Management Commands
@config_app.command("init")
def config_init(
    is_global: bool = typer.Option(False, "--global", "-g", help="Create global config"),
):
    """Initialize new config file."""
    # Implementation...

if __name__ == '__main__':
    app()
```

**Test-First**:

```python
# tests/unit/test_cli.py
from typer.testing import CliRunner
from proxywhirl.cli import app

runner = CliRunner()

def test_cli_help():
    """Should display help with --help flag."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert 'ProxyWhirl CLI' in result.stdout

def test_get_command_basic(mock_rotator):
    """Should make GET request through proxy."""
    result = runner.invoke(app, ["get", "https://example.com"])
    assert result.exit_code == 0

def test_pool_list_json_format():
    """Should output JSON when --format json."""
    result = runner.invoke(app, ["--format", "json", "pool", "list"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)  # Valid JSON
```

---

### Step 3: Implement Output Formatters

**Purpose**: Render data in multiple formats (human, JSON, table, CSV)

**Structure**:

```python
# In proxywhirl/cli.py or separate module

from typing import Protocol, List
from rich.console import Console
from rich.table import Table
from rich.json import JSON
import json
import csv
import io

class OutputRenderer(Protocol):
    def render_proxy_list(self, proxies: List[ProxyStatus]) -> str: ...
    def render_request_result(self, result: RequestResult) -> str: ...

class HumanRenderer:
    """Rich tables and progress bars."""
    def __init__(self):
        self.console = Console()
    
    def render_proxy_list(self, proxies):
        table = Table(title="Proxy Pool")
        table.add_column("URL")
        table.add_column("Status")
        # ...
        return self.console.print(table)

class JsonRenderer:
    """JSON output for scripting."""
    def render_proxy_list(self, proxies):
        data = [p.model_dump() for p in proxies]
        return json.dumps(data, indent=2)

# Factory function
def get_renderer(format: str) -> OutputRenderer:
    if format == 'human':
        return HumanRenderer()
    elif format == 'json':
        return JsonRenderer()
    # ...
```

---

### Step 4: Implement Lock File Management

**Purpose**: Prevent concurrent write operations

**Implementation**:

```python
from filelock import FileLock, Timeout
from pathlib import Path
import os
import json
import typer

class CLILock:
    def __init__(self, config_dir: Path):
        self.lock_path = config_dir / ".proxywhirl.lock"
        self.lock = FileLock(self.lock_path, timeout=0)
    
    def __enter__(self):
        try:
            self.lock.acquire()
            # Write PID to lock file
            with open(self.lock_path, 'w') as f:
                json.dump({
                    'pid': os.getpid(),
                    'command': ' '.join(sys.argv)
                }, f)
            return self
        except Timeout:
            # Read existing lock
            with open(self.lock_path, 'r') as f:
                lock_data = json.load(f)
            typer.secho(
                f"Another proxywhirl process is running (PID {lock_data['pid']})\n"
                f"Wait for it to finish, or use --force to override (unsafe).",
                err=True,
                fg="red",
            )
            raise typer.Exit(code=4)
    
    def __exit__(self, *args):
        self.lock.release()
        self.lock_path.unlink(missing_ok=True)
```

**Usage**:

```python
@pool_app.command("add")
def pool_add(
    ctx: typer.Context,
    proxy_url: str = typer.Argument(..., help="Proxy URL"),
):
    with CLILock(ctx.obj.config_path.parent):
        # Critical section - modify pool
        pass
```

---

### Step 5: Integration Testing

**Purpose**: Test end-to-end user stories

**Example Tests**:

```python
# tests/integration/test_cli_requests.py

def test_get_request_through_proxy(httpserver, proxy_server):
    """US1: Make request through proxy (acceptance scenario 1)."""
    from typer.testing import CliRunner
    from proxywhirl.cli import app
    
    httpserver.expect_request("/api").respond_with_json({"status": "ok"})
    
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create config with proxy
        result = runner.invoke(app, [
            'get',
            httpserver.url_for("/api"),
            '--proxy', proxy_server.url
        ])
        
        assert result.exit_code == 0
        assert "status" in result.stdout

def test_pool_management_workflow():
    """US2: Manage proxy pool (full workflow)."""
    from typer.testing import CliRunner
    from proxywhirl.cli import app
    
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Initialize config
        result = runner.invoke(app, ['config', 'init', '--local'])
        assert result.exit_code == 0
        
        # Add proxy
        result = runner.invoke(app, [
            'pool', 'add',
            'http://proxy.example.com:8080',
            '--yes'
        ])
        assert result.exit_code == 0
        
        # List proxies
        result = runner.invoke(app, ['pool', 'list', '--format', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data['total_proxies'] == 1
```

---

## Testing Strategy

### Unit Tests (Fast, Isolated)

- Config discovery logic
- TOML parsing/writing
- Credential encryption/decryption
- Output formatters
- Lock file operations
- Typer option parsing

**Run**: `uv run pytest tests/unit/test_cli.py tests/unit/test_config.py -v`

### Integration Tests (End-to-End)

- Full CLI command workflows
- Config persistence across invocations
- Proxy rotation during requests
- Error handling and exit codes
- Interactive prompt behavior

**Run**: `uv run pytest tests/integration/test_cli_*.py -v`

### Contract Tests

- CLI schema matches implementation
- All documented commands exist
- All options work as specified
- Exit codes match documentation

---

## Development Checklist

- [ ] Create `proxywhirl/config.py` module
- [ ] Create `proxywhirl/cli.py` module with Typer commands
- [ ] Implement output formatters (human, JSON, table, CSV)
- [ ] Implement lock file management
- [ ] Write unit tests for config module (10+ tests)
- [ ] Write unit tests for CLI commands (20+ tests)
- [ ] Write integration tests for user stories (4+ tests)
- [ ] Update `pyproject.toml` with new dependencies
- [ ] Add CLI entry point to `pyproject.toml`:

```toml
[project.scripts]
proxywhirl = "proxywhirl.cli:app"
```

- [ ] Test cross-platform behavior (Linux/macOS/Windows)
- [ ] Verify TTY detection (progress bars, colors)
- [ ] Test file permissions (config file = 600)
- [ ] Run mypy --strict (0 errors)
- [ ] Run ruff check (all passing)
- [ ] Generate coverage report (85%+)

---

## Common Pitfalls

1. **Forgetting to decrypt credentials**: Always decrypt when loading config
2. **Not checking TTY**: Progress bars crash when piped
3. **Platform-specific paths**: Use `platformdirs` for config directories
4. **Lock file cleanup**: Always use context manager to ensure cleanup
5. **Exit codes**: Remember to raise `typer.Exit(code=...)` after printing errors
6. **SecretStr in JSON**: Use custom encoder to avoid serialization errors

---

## Next Steps

After implementation:

1. **Generate tasks.md**: Run `/speckit.tasks` to create detailed task breakdown
2. **Phase-by-phase implementation**: Follow test-first workflow from tasks.md
3. **Checkpoints**: Validate after each phase before proceeding
4. **Documentation**: Add examples to `examples/cli_examples.sh`
5. **README update**: Add CLI usage section with screenshots

---

## Quick Reference

**Key Files**:

- `proxywhirl/config.py` - Configuration management
- `proxywhirl/cli.py` - Typer command definitions
- `tests/unit/test_cli.py` - CLI unit tests
- `tests/integration/test_cli_*.py` - End-to-end tests

**Key Dependencies**:

- `typer` - CLI framework
- `rich` - Output formatting
- `filelock` - Concurrency control
- `platformdirs` - Cross-platform paths

**Key Constitution Principles**:

- Library-first: CLI wraps library, no duplicate logic
- Test-first: Tests written before implementation
- Type safety: All functions fully typed
- Independent user stories: Each story separately testable

---

## Example: Minimal Working CLI

```python
# proxywhirl/cli.py (simplified)

import typer
from proxywhirl import ProxyRotator, Proxy

app = typer.Typer()

@app.command()
def get(url: str):
    """Make HTTP GET request through proxy."""
    # Hardcoded for demo
    proxy = Proxy(url="http://proxy.example.com:8080")
    rotator = ProxyRotator(proxies=[proxy])

    # Make request
    response = rotator.request("GET", url)
    typer.echo(response.text)

if __name__ == '__main__':
    app()
```

**Test**:

```python
from typer.testing import CliRunner
from proxywhirl.cli import app


def test_get_basic() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ['get', 'https://example.com'])
    assert result.exit_code == 0
```

This is the minimal viable CLI. Expand from here following the full implementation plan.
