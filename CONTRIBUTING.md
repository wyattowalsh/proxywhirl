# Contributing to ProxyWhirl

Thank you for your interest in contributing to ProxyWhirl! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Committing Changes](#committing-changes)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

Be respectful, inclusive, and professional in all interactions with other contributors and maintainers.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork locally**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/proxywhirl.git
   cd proxywhirl
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/wyattowalsh/proxywhirl.git
   ```
4. **Keep your fork synced**:
   ```bash
   git fetch upstream
   git checkout develop
   git merge upstream/develop
   ```

## Development Setup

### Prerequisites

- Python 3.9+
- `uv` package manager (install from https://github.com/astral-sh/uv)

### Install Dependencies

```bash
uv sync
pre-commit install
```

This installs all dependencies and sets up git hooks for pre-commit checks.

## Making Changes

### Branching Strategy

Branch from `develop` using the naming convention:
- Feature: `feature/<description>`
- Bug fix: `fix/<description>`
- Docs: `docs/<description>`
- Refactor: `refactor/<description>`

Example:
```bash
git checkout -b feature/add-socks-support develop
```

### Code Changes

#### Type Hints

Always add type hints to public functions and classes:

```python
from __future__ import annotations

def get_proxy(proxy_id: str) -> Proxy | None:
    """Get a proxy by ID.
    
    Args:
        proxy_id: The proxy identifier
    
    Returns:
        Proxy instance or None if not found
    """
    ...
```

#### Imports

Organize imports in this order:
1. Future imports (`from __future__ import ...`)
2. Standard library
3. Third-party packages
4. Local imports

Use `from module import name` not `import module.name`.

#### Comments

Only comment code that needs clarification. Self-documenting code is preferred.

```python
# Bad: obvious comment
x = 5  # Set x to 5

# Good: explains why, not what
# Use 5 retries to balance reliability with performance
max_retries = 5
```

#### Logging

Use `loguru` for all logging (never use `print`):

```python
from loguru import logger

logger.info(f"Proxy {proxy.url} validated successfully")
logger.error(f"Failed to validate proxy: {e}", exc_info=True)
```

### Line Length

Maximum line length is **100 characters**. Format with:
```bash
uv run ruff format proxywhirl/ tests/
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
uv run pytest tests/unit/test_rotator.py -v

# Run with coverage
uv run pytest tests/ --cov=proxywhirl --cov-report=term-missing

# Run specific marker
uv run pytest -m unit
```

### Test Organization

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Property-based tests: `tests/property/`
- Benchmarks: `tests/benchmarks/`

### Writing Tests

Follow these patterns:

```python
import pytest
from proxywhirl import ProxyWhirl, Proxy

class TestProxyWhirl:
    """Tests for ProxyWhirl rotator."""
    
    def test_round_robin_rotation(self) -> None:
        """Verify round-robin strategy rotates proxies sequentially."""
        proxies = [
            Proxy(url="http://proxy1.com:8080"),
            Proxy(url="http://proxy2.com:8080"),
        ]
        rotator = ProxyWhirl(proxies=proxies, strategy="round-robin")
        
        assert rotator.get_next_proxy() == proxies[0]
        assert rotator.get_next_proxy() == proxies[1]
        assert rotator.get_next_proxy() == proxies[0]
    
    @pytest.mark.asyncio
    async def test_async_rotation(self) -> None:
        """Verify async rotator works."""
        from proxywhirl import AsyncProxyWhirl
        
        proxies = [Proxy(url="http://proxy1.com:8080")]
        rotator = AsyncProxyWhirl(proxies=proxies)
        
        proxy = await rotator.get_next_proxy()
        assert proxy is not None
```

### Test Markers

Use pytest markers for test categorization:

```python
@pytest.mark.unit          # Fast unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.slow          # Slow tests (skipped by default)
@pytest.mark.network       # Tests requiring network
@pytest.mark.benchmark     # Performance benchmarks
```

## Code Style

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `ProxyWhirl`, `CircuitBreaker`)
- **Functions/Variables**: `snake_case` (e.g., `get_proxy`, `max_retries`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private**: `_prefix` (e.g., `_internal_method`)

### Ruff Rules

The project uses `ruff` with these rules:
- E: PEP 8 errors
- F: PyFlakes
- I: isort (import sorting)
- N: pep8-naming
- W: PEP 8 warnings
- UP: pyupgrade (modern Python)
- B: flake8-bugbear
- C4: flake8-comprehensions
- SIM: flake8-simplify

Run before committing:
```bash
make lint
make format
make type-check
```

### Type Checking

```bash
# Check types with ty (not mypy!)
make type-check

# Or manually:
uv run ty check proxywhirl/
```

## Committing Changes

Use **conventional commits** format:

```
<type>(<scope>): <description>

<body>

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring (no feature change)
- `perf`: Performance improvement
- `test`: Test additions/modifications
- `chore`: Build, CI, dependencies

### Examples

```
feat(rotator): add weighted round-robin strategy

Implements weighted round-robin rotation strategy that distributes
requests proportionally based on proxy weights. Includes comprehensive
tests and documentation.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

```
fix(storage): handle missing proxies table gracefully

Fix crash when proxies table doesn't exist during initialization.
Now creates table automatically if needed.

Closes #123

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Pull Request Process

### Before Opening a PR

1. **Run full quality gates**:
   ```bash
   make quality-gates
   ```

2. **Keep commits clean**: Squash fixup commits if needed
   ```bash
   git rebase -i upstream/develop
   ```

3. **Update documentation**: If changing public APIs, update relevant docs

4. **Add tests**: All new code needs tests (aim for 85%+ coverage)

### PR Description

Use this template:

```markdown
## Description
Brief description of changes

## Motivation
Why this change is needed

## Changes
- Change 1
- Change 2

## Testing
How to verify the changes work

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Conventional commit message used
- [ ] Code passes quality gates
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Address feedback**: Commit additional changes on top (don't force-push)
2. **Request re-review**: When all feedback is addressed
3. **Squash on merge**: Maintainers will squash commits on merge (you don't need to)

## Reporting Issues

### Bug Reports

Include:
- Minimal reproducible example
- Expected vs actual behavior
- Environment (OS, Python version, etc.)
- Error traceback (if applicable)

Example:
```markdown
## Description
ProxyWhirl crashes when loading certain proxy URLs

## Steps to Reproduce
1. Create config with proxy URL `http://proxy.example.com:bad`
2. Run `proxywhirl pool list`

## Expected
Validation error with helpful message

## Actual
Traceback: AttributeError...

## Environment
- OS: macOS 13.5
- Python: 3.11.4
- ProxyWhirl: 0.5.0
```

### Feature Requests

Include:
- Use case and motivation
- Proposed behavior
- Examples of similar tools/libraries

Example:
```markdown
## Request
Add HTTP/2 proxy support

## Motivation
Many modern proxies support HTTP/2 for better performance

## Proposed Behavior
New `http2_only` flag in proxy configuration that routes requests through HTTP/2

## Related
https://github.com/example/project/issues/123
```

## Questions?

- **Documentation**: See [README.md](README.md) and [docs/](docs/)
- **Discussions**: Open a GitHub Discussion
- **Issues**: Open a GitHub Issue for bugs/features

## Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Type Hints](https://peps.python.org/pep-0484/)

---

**Thank you for contributing to ProxyWhirl!** 🚀
