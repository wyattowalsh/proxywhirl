# Contributing to ProxyWhirl

Thank you for your interest in contributing to ProxyWhirl! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Commit Message Format](#commit-message-format)
- [Project Structure](#project-structure)
- [Running the Test Suite](#running-the-test-suite)

## Code of Conduct

This project follows a standard code of conduct. Please be respectful and constructive in all interactions.

## Getting Started

Before you begin:
1. Check existing [issues](https://github.com/wyattowalsh/proxywhirl/issues) and [pull requests](https://github.com/wyattowalsh/proxywhirl/pulls)
2. For major changes, open an issue first to discuss your proposal
3. Fork the repository and create a feature branch

## Development Setup

ProxyWhirl uses `uv` for fast, reliable dependency management. Follow these steps to set up your development environment:

### Prerequisites

- Python 3.9 or higher (3.9, 3.10, 3.11, 3.12, 3.13 supported)
- `uv` package manager

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### Clone and Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/proxywhirl.git
cd proxywhirl

# Sync dependencies (creates venv and installs packages)
uv sync

# Verify installation
uv run python -c "import proxywhirl; print('Success!')"
```

This will:
- Create a virtual environment in `.venv/`
- Install all dependencies from `pyproject.toml`
- Install proxywhirl in editable mode

### Optional: Install Browser Support

For browser rendering features (Phase 2.5):

```bash
uv pip install ".[js]"
uv run playwright install chromium
```

## Code Style Guidelines

ProxyWhirl follows strict code quality standards. All code must pass linting and type checking before being merged.

### Formatting and Linting

We use `ruff` for both linting and formatting:

```bash
# Check for linting issues
uv run -- ruff check .

# Auto-fix linting issues (safe fixes only)
uv run -- ruff check . --fix

# Format code
uv run -- ruff format .

# Check formatting without changing files
uv run -- ruff format . --check
```

### Type Checking

We use `mypy` in strict mode for type safety:

```bash
# Run type checking
uv run -- mypy proxywhirl/

# Type check specific file
uv run -- mypy proxywhirl/rotator.py
```

### Code Style Rules

1. **Type Hints**: All functions must have type hints
   ```python
   # Good
   def add_proxy(self, proxy: Proxy | str) -> None:
       pass

   # Bad
   def add_proxy(self, proxy):
       pass
   ```

2. **Modern Python Syntax**: Use Python 3.9+ features
   ```python
   # Good (Python 3.9+)
   def get_proxies(self) -> list[Proxy]:
       pass

   # Bad (old style)
   from typing import List
   def get_proxies(self) -> List[Proxy]:
       pass
   ```

3. **Docstrings**: Use Google-style docstrings for all public APIs
   ```python
   def validate_proxy(self, proxy: Proxy) -> bool:
       """Validate a proxy for connectivity and anonymity.

       Args:
           proxy: The proxy to validate

       Returns:
           True if proxy is valid and healthy

       Raises:
           ValidationError: If proxy URL is malformed
       """
   ```

4. **Line Length**: Maximum 100 characters

5. **Imports**: Organize imports in order (stdlib, third-party, local)
   ```python
   # Good
   import asyncio
   from datetime import datetime

   import httpx
   from pydantic import BaseModel

   from proxywhirl.models import Proxy
   ```

## Testing Requirements

All contributions must include tests. ProxyWhirl maintains >80% code coverage.

### Writing Tests

Tests are organized by type:
- `tests/unit/` - Unit tests for individual functions/classes
- `tests/integration/` - Integration tests for component interactions
- `tests/benchmarks/` - Performance benchmarks

Example test:

```python
import pytest
from proxywhirl import ProxyRotator, Proxy


def test_add_proxy():
    """Test adding a proxy to the rotator."""
    rotator = ProxyRotator()
    proxy = Proxy(url="http://proxy.example.com:8080")

    rotator.add_proxy(proxy)

    assert len(rotator.pool.get_all_proxies()) == 1
    assert rotator.pool.get_all_proxies()[0].url == proxy.url


@pytest.mark.asyncio
async def test_health_monitor():
    """Test health monitoring functionality."""
    from proxywhirl.models import ProxyPool, HealthMonitor

    pool = ProxyPool(name="test_pool")
    pool.add_proxy(Proxy(url="http://proxy.example.com:8080"))

    monitor = HealthMonitor(pool=pool, check_interval=1)
    await monitor.start()

    assert monitor.is_running is True

    await monitor.stop()
    assert monitor.is_running is False
```

### Running Tests

```bash
# Run all tests
uv run -- pytest

# Run specific test file
uv run -- pytest tests/unit/test_rotator.py

# Run specific test function
uv run -- pytest tests/unit/test_rotator.py::test_add_proxy

# Run with coverage report
uv run -- pytest --cov=proxywhirl --cov-report=html

# Run only fast tests (exclude slow integration tests)
uv run -- pytest -m "not slow"

# Run in verbose mode
uv run -- pytest -v

# Stop on first failure
uv run -- pytest -x
```

### Coverage Requirements

- Minimum coverage: 80%
- New features must include tests
- Bug fixes must include regression tests
- View coverage report: `open logs/htmlcov/index.html`

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Run quality checks**
   ```bash
   # Linting
   uv run -- ruff check .

   # Type checking
   uv run -- mypy proxywhirl/

   # Tests
   uv run -- pytest
   ```

4. **Commit your changes**
   - Follow [commit message format](#commit-message-format)
   - Make atomic commits (one logical change per commit)

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Create a pull request on GitHub
   - Fill out the PR template
   - Link any related issues

6. **Code Review**
   - Address review feedback
   - Keep your branch up to date with `main`
   - Ensure CI passes

7. **Merge**
   - Maintainer will merge once approved
   - Your branch will be deleted after merge

## Commit Message Format

ProxyWhirl uses [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring (no functional change)
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependencies

### Examples

```
feat(rotator): add weighted rotation strategy

Implement weighted proxy selection based on success rate and
response time metrics. Proxies with higher success rates and
lower latency are selected more frequently.

Closes #123
```

```
fix(validator): handle connection timeout correctly

Previously, connection timeouts were treated as validation
failures. Now they trigger a retry with exponential backoff.

Fixes #456
```

```
docs: update README with health monitoring examples

- Add comprehensive health monitoring example
- Document HealthMonitor configuration options
- Fix typos in installation section
```

```
test(storage): add tests for SQLite query filters

Add integration tests for:
- Query by source
- Query by health status
- Query with multiple filters
```

### Commit Message Best Practices

1. **Subject line**:
   - Use imperative mood ("add feature" not "added feature")
   - Keep under 72 characters
   - Don't end with a period

2. **Body** (optional but recommended):
   - Explain what and why, not how
   - Wrap at 72 characters
   - Separate from subject with blank line

3. **Footer** (optional):
   - Reference issues: `Closes #123`, `Fixes #456`
   - Note breaking changes: `BREAKING CHANGE: description`

## Project Structure

Understanding the codebase:

```
proxywhirl/
├── proxywhirl/              # Main package
│   ├── __init__.py         # Package exports
│   ├── models.py           # Data models (Proxy, ProxyPool, etc.)
│   ├── rotator.py          # Core ProxyRotator class
│   ├── strategies.py       # Rotation strategies
│   ├── fetchers.py         # Proxy fetching and parsing
│   ├── storage.py          # Storage backends (File, SQLite)
│   ├── browser.py          # Browser rendering (Playwright)
│   ├── api.py              # REST API server (FastAPI)
│   ├── cli.py              # Command-line interface (Typer)
│   ├── exceptions.py       # Custom exceptions
│   ├── utils.py            # Utility functions
│   ├── retry_*.py          # Retry and circuit breaker logic
│   ├── cache*.py           # Caching system
│   └── sources.py          # Pre-configured proxy sources
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── benchmarks/        # Performance benchmarks
├── examples/              # Example scripts
├── specs/                 # Feature specifications
├── docs/                  # Documentation
├── pyproject.toml         # Project configuration
├── uv.lock               # Locked dependencies
└── README.md             # Project README
```

### Key Design Principles

1. **Flat Structure**: No nested packages - everything in `proxywhirl/`
2. **Type Safety**: Full type hints, mypy strict mode
3. **Async Support**: Async operations for I/O-bound tasks
4. **Pydantic Models**: Data validation and serialization
5. **Minimal Dependencies**: Only essential packages

## Running the Test Suite

### Full Test Suite

```bash
# Run everything with coverage
uv run -- pytest --cov=proxywhirl --cov-report=html --cov-report=term

# View coverage report
open logs/htmlcov/index.html  # macOS
xdg-open logs/htmlcov/index.html  # Linux
start logs/htmlcov/index.html  # Windows
```

### Quick Checks Before Committing

```bash
# Create a script: scripts/check.sh
#!/bin/bash
set -e

echo "Running linter..."
uv run -- ruff check .

echo "Running type checker..."
uv run -- mypy proxywhirl/

echo "Running tests..."
uv run -- pytest -x

echo "✅ All checks passed!"
```

Make it executable and run:
```bash
chmod +x scripts/check.sh
./scripts/check.sh
```

## Getting Help

- **Documentation**: Read the [specs/](specs/) directory for detailed feature documentation
- **Issues**: Search [existing issues](https://github.com/wyattowalsh/proxywhirl/issues) or create a new one
- **Discussions**: Use [GitHub Discussions](https://github.com/wyattowalsh/proxywhirl/discussions) for questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to ProxyWhirl! 🌀**
