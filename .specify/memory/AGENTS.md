# Specification System Guidelines

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Constitution (7 Principles)

| # | Principle | Requirement |
|---|-----------|-------------|
| 1 | Library-First | Pure Python API, no CLI/web deps required |
| 2 | Test-First | Tests BEFORE implementation (NON-NEGOTIABLE) |
| 3 | Type Safety | ty strict + Pydantic validation |
| 4 | Independent Stories | Each story independently testable |
| 5 | Performance | <1ms selection, 1000+ concurrent |
| 6 | Security-First | 100% credential protection |
| 7 | Simplicity | Flat architecture, single responsibilities |

## Spec Structure

```
.specify/
├── memory/constitution.md     # Core principles (MANDATORY)
├── specs/###-feature-name/
│   ├── plan.md               # Technical design
│   ├── spec.md               # User stories, acceptance
│   └── tasks.md              # Test-first phases
└── templates/
```

## Feature Workflow

1. Create spec in `.specify/specs/###-feature-name/`
2. Write `plan.md` → `spec.md` → `tasks.md`
3. Branch: `feature/###-feature-name`
4. Write tests FIRST (verify fail) → implement → refactor
5. `make quality-gates` → merge

## Spec Numbering

`001-006` Core | `007-009` Observability | `010-011` Data | `012-014` Config | `015-018` DX | `019+` Extensions

## Key Rules

- **ALL Python commands:** `uv run` prefix (constitution requirement)
- **Tests come BEFORE implementation**
- **Read `constitution.md` before any feature**
- **`make quality-gates` before PR**
