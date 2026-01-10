# Specification System Agent Guidelines

> Extends: [../../AGENTS.md](../../AGENTS.md)

Agent guidelines specific to the `.specify/` specification system and constitution compliance.

## Quick Reference

| Task | Command |
|------|---------|
| Run tests | `uv run pytest tests/` |
| Type check | `uv run ty check proxywhirl/` |
| Lint | `uv run ruff check proxywhirl/` |
| Format | `uv run ruff format proxywhirl/` |
| Run script | `uv run python script.py` |
| Add package | `uv add <package>` |
| Sync deps | `uv sync` |
| Quality gates | `make quality-gates` |

## Critical Requirements

### Python Command Execution (MANDATORY)

**ALL Python commands MUST use `uv run` prefix without exception.**

```bash
# ✅ CORRECT
uv run pytest tests/
uv run python script.py
uv run ty check proxywhirl/

# ❌ WRONG (constitution violation)
pytest tests/
python script.py
pip install package
```

### Package Management

**ONLY use `uv` commands:**

```bash
uv add httpx              # Add dependency
uv add --dev pytest       # Add dev dependency
uv sync                   # Sync environment
```

## Constitution Compliance

All development MUST follow the 7 core principles in `constitution.md`:

| # | Principle | Key Requirement |
|---|-----------|-----------------|
| 1 | **Library-First Architecture** | Pure Python API, no CLI/web dependencies required |
| 2 | **Test-First Development** | Tests written BEFORE implementation (NON-NEGOTIABLE) |
| 3 | **Type Safety** | ty strict compliance + Pydantic runtime validation |
| 4 | **Independent User Stories** | Each story independently developable and testable |
| 5 | **Performance Standards** | <1ms selection, 1000+ concurrent requests |
| 6 | **Security-First** | 100% credential protection, never exposed in logs/errors |
| 7 | **Simplicity** | Flat architecture, single responsibilities |

## Specification Structure

```
.specify/
├── memory/
│   ├── constitution.md              # Core principles (MANDATORY)
│   ├── constitution-compliance-report.md
│   └── AGENTS.md                    # This file
├── specs/
│   └── ###-feature-name/
│       ├── plan.md                  # Technical design
│       ├── spec.md                  # User stories, acceptance criteria
│       ├── tasks.md                 # Test-first implementation phases
│       ├── quickstart.md            # Getting started guide
│       ├── research.md              # Research notes
│       ├── data-model.md            # Data model documentation
│       ├── contracts/               # API contracts
│       └── checklists/              # Quality checklists
└── templates/                       # Spec-kit templates
```

## Development Workflow for New Features

1. Create spec in `.specify/specs/###-feature-name/`
2. Run constitution check (must pass)
3. Write `plan.md` (technical design)
4. Write `spec.md` (user stories, acceptance criteria)
5. Write `tasks.md` (test-first phases)
6. Create feature branch: `feature/###-feature-name`
7. Write tests FIRST (verify they fail)
8. Implement minimal code to pass tests
9. Refactor while maintaining green tests
10. Merge to main after quality gates pass

## Quality Gates (ALL must pass)

```bash
# Run all quality gates
make quality-gates

# Or individually:
uv run pytest tests/                    # All tests passing
uv run pytest tests/ --cov=proxywhirl   # Coverage check
uv run ty check proxywhirl/             # Type check (0 errors)
uv run ruff check proxywhirl/           # Lint (0 errors)
```

## Violation Reporting

If you encounter code using bare Python commands:

1. **Identify**: Note the file and line number
2. **Correct**: Update to use `uv run` prefix
3. **Verify**: Test the corrected command works
4. **Document**: Note the fix in commit message

```bash
fix: enforce uv run for Python commands

- Updated tests/integration/test_api.py to use uv run
- Constitutional compliance: all Python commands now use uv
- Refs: .specify/memory/constitution.md
```

## Spec Naming Convention

Specs are numbered sequentially with descriptive kebab-case names:

| Number Range | Category |
|--------------|----------|
| 001-006 | Core library features |
| 007-009 | Observability (logging, metrics, analytics) |
| 010-011 | Data management (reports, exports) |
| 012-014 | Configuration & resilience |
| 015-018 | Developer experience (examples, docs, CI/CD, MCP) |

## Key Reminders

- When in doubt, prefix with `uv run` — it's never wrong
- Tests come BEFORE implementation
- Read `constitution.md` before starting any feature
- Check existing specs before creating new ones
- Use `make quality-gates` before opening a PR
