# Agent Development Guidelines for ProxyWhirl

**Last Updated**: 2025-10-30  
**Status**: Active  
**Scope**: All AI agents, coding assistants, and automated tools working on ProxyWhirl

---

## Critical Requirements

### 1. Python Command Execution (MANDATORY)

**ALL Python commands MUST use `uv run` prefix without exception.**

#### ✅ CORRECT Usage

```bash
# Testing
uv run pytest tests/
uv run pytest tests/ --cov=proxywhirl
uv run pytest tests/unit/

# Type Checking
uv run mypy --strict proxywhirl/

# Linting & Formatting
uv run ruff check proxywhirl/
uv run ruff format proxywhirl/

# Running Python
uv run python script.py
uv run python -m module
uv run python -c "import sys; print(sys.version)"

# Jupyter/IPython
uv run jupyter notebook
uv run ipython
```

#### ❌ WRONG Usage (NEVER DO THIS)

```bash
# These are constitution violations:
pytest tests/
python -m pytest
python script.py
python -c "..."
mypy proxywhirl/
ruff check proxywhirl/
pip install <package>
python -m pip install <package>
```

### 2. Package Management

**ONLY use `uv` commands for dependency management:**

```bash
# Add dependencies
uv add httpx
uv add --dev pytest

# Sync environment
uv sync

# Remove dependencies
uv remove <package>

# NEVER use these:
pip install <package>
pip uninstall <package>
python -m pip install <package>
```

### 3. Enforcement

- Any Python command without `uv run` is a **constitution violation**
- Must be corrected immediately when detected
- No exceptions for "quick tests" or "one-off commands"
- Applies to all contexts: CI/CD, local dev, documentation examples

---

## Rationale

### Why `uv run` is Required

1. **Environment Consistency**: Ensures correct virtual environment activation across all contexts
2. **Dependency Isolation**: Prevents system Python pollution and version conflicts
3. **Reproducibility**: Lockfile-based approach ensures identical environments
4. **Speed**: 10-100x faster than pip for dependency resolution
5. **Reliability**: Eliminates common "works on my machine" issues

### Common Mistakes to Avoid

1. **Running bare `python` commands**: Always prefix with `uv run`
2. **Using `pip` directly**: Use `uv add` instead
3. **Activating venv manually**: `uv run` handles this automatically
4. **Mixing package managers**: Never mix `uv`, `pip`, `poetry`, etc.

---

## Development Workflow

### Initial Setup

```bash
# Clone repository
git clone https://github.com/wyattowalsh/proxywhirl.git
cd proxywhirl

# Create and sync environment (first time only)
uv venv
uv sync

# All subsequent commands use uv run
uv run pytest tests/
```

### Common Tasks

```bash
# Run tests
uv run pytest tests/ -v

# Type check
uv run mypy --strict proxywhirl/

# Format code
uv run ruff format proxywhirl/

# Lint code
uv run ruff check proxywhirl/

# Run specific Python script
uv run python examples/basic_usage.py

# Interactive Python
uv run python
>>> import proxywhirl
>>> # work with library
```

### Adding New Dependencies

```bash
# Production dependency
uv add httpx

# Development dependency
uv add --dev pytest-asyncio

# Specific version
uv add "pydantic>=2.0.0,<3.0.0"
```

---

## Testing Standards

### Test Execution

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/unit/test_strategies.py

# Run specific test class
uv run pytest tests/unit/test_strategies.py::TestPluginArchitecture

# Run with coverage
uv run pytest tests/ --cov=proxywhirl --cov-report=html

# Run benchmarks
uv run pytest tests/benchmarks/ -v
```

### Quality Gates

**ALL quality gates must pass before merge:**

```bash
# 1. Tests
uv run pytest tests/

# 2. Type checking
uv run mypy --strict proxywhirl/

# 3. Linting
uv run ruff check proxywhirl/

# 4. Coverage (must be ≥85%)
uv run pytest tests/ --cov=proxywhirl --cov-report=term

# Run all gates together
uv run pytest tests/ && \
uv run mypy --strict proxywhirl/ && \
uv run ruff check proxywhirl/
```

---

## Constitution Compliance

This document enforces the requirements from `.specify/memory/constitution.md`:

- **Principle I**: Library-First Architecture - `uv run` ensures clean library usage
- **Principle II**: Test-First Development - All tests must use `uv run pytest`
- **Principle III**: Type Safety - Type checking via `uv run mypy --strict`

### Violation Reporting

If you encounter code or documentation using bare Python commands:

1. **Identify**: Note the file and line number
2. **Correct**: Update to use `uv run` prefix
3. **Verify**: Test the corrected command works
4. **Document**: Note the fix in commit message

Example commit message:
```
fix: enforce uv run for Python commands

- Updated tests/integration/test_api.py to use uv run
- Constitutional compliance: all Python commands now use uv
- Refs: .specify/memory/constitution.md, .specify/memory/AGENTS.md
```

---

## Agent-Specific Instructions

### For GitHub Copilot / Claude / GPT-4

When generating code or commands:

1. **Always** prefix Python commands with `uv run`
2. **Never** suggest `pip install` - use `uv add` instead
3. **Always** verify commands follow constitution
4. **Always** check `.specify/memory/constitution.md` for latest rules

### For CI/CD Systems

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: uv run pytest tests/

- name: Type check
  run: uv run mypy --strict proxywhirl/

- name: Lint
  run: uv run ruff check proxywhirl/
```

### For Documentation Examples

All code examples in docs must show `uv run`:

````markdown
## Running Tests

```bash
uv run pytest tests/
```

## Type Checking

```bash
uv run mypy --strict proxywhirl/
```
````

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Run tests | `uv run pytest tests/` |
| Type check | `uv run mypy --strict proxywhirl/` |
| Lint | `uv run ruff check proxywhirl/` |
| Format | `uv run ruff format proxywhirl/` |
| Run script | `uv run python script.py` |
| Add package | `uv add <package>` |
| Add dev package | `uv add --dev <package>` |
| Sync deps | `uv sync` |
| Python REPL | `uv run python` |

---

## Version History

- **1.0.0** (2025-10-30): Initial agent guidelines created
  - Mandatory `uv run` requirement documented
  - Package management standards defined
  - Testing workflow specified

---

**Remember**: When in doubt, prefix with `uv run`. It's never wrong to use `uv run`, but it's always wrong to skip it.
