<!--
Sync Impact Report:
- Version: 0.0.0 → 1.0.0 (Initial constitution ratification)
- Principles Added: 7 core principles (Library-First, Test-First, Type Safety, Independent User Stories, Performance Standards, Security-First, Simplicity & Flat Architecture)
- Sections Added: Technology Standards, Development Workflow, Governance
- Templates Status:
  ✅ plan-template.md - Aligned with Constitution Check and user story independence
  ✅ spec-template.md - Aligned with user story prioritization and independence
  ✅ tasks-template.md - Aligned with test-first development and user story phases
- Follow-up TODOs: None
-->

# ProxyWhirl Constitution

## Core Principles

### I. Library-First Architecture

ProxyWhirl MUST be designed as a standalone, importable Python library that provides maximum flexibility and composability. Every feature MUST:

- Be usable purely via Python API imports (no CLI/web dependencies required)
- Provide clear, documented public interfaces in `proxywhirl/__init__.py`
- Be independently testable without external service dependencies
- Have a single, well-defined purpose (no "utility" or "helpers" catch-all modules)
- Support context manager patterns for resource cleanup
- Expose type-safe APIs with full type hints (py.typed marker)

**Rationale**: Library-first design maximizes reusability, enables integration into any Python application, and ensures the package can be composed with other tools.

**Validation**: Every PR MUST demonstrate the feature works via direct Python import without requiring CLI commands or web servers.

### II. Test-First Development (NON-NEGOTIABLE)

All code MUST follow strict Test-Driven Development (TDD):

1. **Tests written FIRST** - Unit, property, and integration tests MUST be written before implementation
2. **Tests MUST fail** - Verify tests fail before any production code is written
3. **Red-Green-Refactor** - Implement minimal code to pass tests, then refactor
4. **User approval** - Test scenarios MUST map directly to spec.md acceptance criteria
5. **No untested code** - Production code without corresponding tests is prohibited

**Coverage Requirements**:

- Minimum 85% code coverage (current: 88%+)
- 100% coverage for security-critical code (credential handling, validation)
- Property-based tests required for all rotation strategies (using Hypothesis)
- Integration tests required for all user stories

**Test Organization**:

- `tests/unit/` - Fast, isolated unit tests (<10ms each)
- `tests/integration/` - End-to-end user story tests with real HTTP
- `tests/property/` - Hypothesis property-based tests
- `tests/benchmarks/` - Performance validation tests

**Rationale**: TDD ensures correctness, prevents regressions, enables fearless refactoring, and creates executable documentation.

**Validation**: Task phases MUST show tests written and failing before implementation begins.

### III. Type Safety & Runtime Validation

ProxyWhirl MUST maintain complete type safety at both static analysis and runtime:

**Static Type Safety**:

- All functions/methods MUST have complete type hints (arguments + return types)
- No `Any` types except where external APIs force it
- Pass `mypy --strict` without warnings
- Distribute `py.typed` marker for PEP 561 compliance

**Runtime Validation**:

- All data models MUST use Pydantic v2 for validation
- URL validation MUST occur before proxy usage
- Configuration validation MUST happen at initialization
- Credentials MUST use `SecretStr` to prevent accidental exposure

**Rationale**: Type safety catches errors at development time, runtime validation catches errors at usage time, together they eliminate entire classes of bugs.

**Validation**: All PRs MUST pass `mypy --strict` and demonstrate runtime validation for invalid inputs.

### IV. Independent User Stories

Every user story MUST be independently developable, testable, and deliverable:

**Independence Requirements**:
- Each user story CAN be implemented without others being complete
- Each user story MUST have its own integration tests that pass in isolation
- Each user story MUST provide standalone value (viable MVP on its own)
- User stories MUST be prioritized (P1, P2, P3...) based on user value

**Task Organization**:
- Tasks MUST be grouped by user story (Phase 3: US1, Phase 4: US2, etc.)
- Foundational phase (Phase 2) MUST complete before ANY user story work begins
- Tests for each story MUST be written and failing before implementation
- Checkpoints MUST validate each story independently before proceeding

**Parallel Development**:
- Different team members CAN work on different user stories simultaneously
- Tasks marked `[P]` within a phase CAN run in parallel
- Story integration happens AFTER independent validation

**Rationale**: Independent user stories enable incremental delivery, parallel development, reduced risk, and clear progress tracking.

**Validation**: spec.md MUST define independent test criteria for each story; tasks.md MUST group by story with clear checkpoints.

### V. Performance Standards

ProxyWhirl MUST meet strict performance benchmarks to be production-ready:

**Latency Requirements**:
- Proxy selection: <1ms for all rotation strategies (O(1) or O(log n))
- Request overhead: <50ms p95 latency added by rotation logic
- Strategy switching: <5ms to change rotation algorithms at runtime

**Throughput Requirements**:
- Support 1000+ concurrent requests without degradation
- Validate 100+ proxies per second (parallel validation)
- File I/O: <50ms to save/load 100 proxies (JSON)

**Scalability Requirements**:
- Pool management MUST be thread-safe for concurrent access
- Memory usage MUST remain constant regardless of request count
- No memory leaks over 10,000+ request cycles

**Benchmark Validation**:
- Benchmarks in `tests/benchmarks/` MUST validate all metrics
- CI MUST fail if benchmarks regress >10%
- Performance profiling results MUST be documented

**Rationale**: Production applications require predictable, low-overhead proxy rotation that doesn't become the bottleneck.

**Validation**: All releases MUST include benchmark results demonstrating compliance with performance targets.

### VI. Security-First Design

Security MUST be built into every layer, not added later:

**Credential Protection**:
- Credentials MUST use `SecretStr` from Pydantic
- Credentials MUST NEVER appear in logs (redacted as `***`)
- Credentials MUST NEVER appear in error messages or stack traces
- Credentials MUST NOT be serialized to JSON without explicit encryption

**Validation & Sanitization**:
- All proxy URLs MUST be validated before use
- Authentication headers MUST be sanitized before logging
- File paths MUST be validated to prevent path traversal

**Secure Defaults**:
- SSL verification MUST be enabled by default
- HTTP-only mode MUST require explicit opt-in
- Encryption MUST use industry-standard algorithms (cryptography library)

**Audit Requirements**:
- Security audit MUST pass before any release
- All credential handling code MUST have 100% test coverage
- Static analysis (Bandit) MUST pass without security warnings

**Rationale**: Proxy credentials are sensitive; any exposure can compromise user accounts, lead to data breaches, or enable attacks.

**Validation**: Every PR touching credentials/auth MUST demonstrate redaction in logs and pass security-focused tests.

### VII. Simplicity & Flat Architecture

ProxyWhirl MUST maintain a flat, elegant structure that is easy to navigate and understand:

**Structural Requirements**:
- Single package: `proxywhirl/` (no nested sub-packages)
- Maximum 10 modules in package root
- Each module MUST have a single, clear responsibility
- No circular dependencies between modules

**Module Responsibilities**:
- `models.py` - Pydantic data models and enums
- `rotator.py` - Core ProxyRotator class
- `strategies.py` - Rotation strategy implementations
- `fetchers.py` - Proxy fetching and parsing (future)
- `storage.py` - Storage backends (future)
- `utils.py` - Pure utility functions (no state)
- `exceptions.py` - Custom exception types

**Public API**:
- All public exports MUST be listed in `__init__.py`'s `__all__`
- Private functions MUST use `_leading_underscore` naming
- No "barrel file" re-exports creating indirection

**Code Style**:
- Follow PEP 8 via Black formatter
- Use Ruff for linting (minimal rule set)
- Prefer explicit over implicit (no magic)
- YAGNI - implement features when needed, not speculatively

**Rationale**: Flat structure reduces cognitive load, improves discoverability, simplifies debugging, and makes onboarding faster.

**Validation**: Package structure MUST remain flat; any new module MUST be justified against existing module responsibilities.

## Technology Standards

**Language & Runtime**:
- Python 3.9+ (target versions: 3.9, 3.10, 3.11, 3.12, 3.13)
- Type hints using modern syntax (from `__future__ import annotations`)

**Core Dependencies**:
- `httpx>=0.25.0` - HTTP client with proxy support
- `pydantic>=2.0.0` - Data validation and settings
- `pydantic-settings>=2.0.0` - Configuration management
- `tenacity>=8.2.0` - Retry logic with backoff
- `loguru>=0.7.0` - Structured logging

**Optional Dependencies**:
- `[storage]`: `sqlmodel>=0.0.14` - SQLite storage backend
- `[security]`: `cryptography>=41.0.0` - Credential encryption
- `[js]`: `playwright>=1.40.0` - JavaScript rendering
- `[all]`: All optional dependencies combined

**Development Dependencies**:
- `pytest>=7.4.0` - Test framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-cov>=4.1.0` - Coverage reporting
- `hypothesis>=6.88.0` - Property-based testing
- `black>=23.0.0` - Code formatting
- `ruff>=0.1.0` - Linting
- `mypy>=1.5.0` - Type checking

**Testing Framework**:
- pytest with strict markers and config
- Hypothesis for property-based tests
- Coverage target: 85%+ (html reports in `htmlcov/`)

**Quality Gates**:
- All code MUST pass: `black --check .`, `ruff check .`, `mypy --strict .`, `pytest`
- CI MUST enforce all quality gates on every PR
- No warnings allowed in production code

## Development Workflow

**Specification-Driven Development**:

1. **Feature Specification** (`spec.md`)
   - Define prioritized, independent user stories (P1, P2, P3...)
   - Write acceptance scenarios (Given-When-Then)
   - Specify success criteria (measurable outcomes)

2. **Implementation Planning** (`plan.md`)
   - Constitution check MUST pass
   - Technical context documented
   - Project structure defined
   - Complexity violations justified (if any)

3. **Task Breakdown** (`tasks.md`)
   - Foundational phase MUST block user stories
   - Tasks grouped by user story
   - Tests written BEFORE implementation
   - Checkpoints validate independent story completion

4. **Test-First Implementation**
   - Write tests mapping to acceptance scenarios
   - Verify tests fail
   - Implement minimal code to pass
   - Refactor while maintaining green tests
   - Document in code or docs site (no ad-hoc .md files)

5. **Validation & Review**
   - All tests passing (unit, property, integration, benchmarks)
   - Coverage ≥85% (100% for security code)
   - Type checking passing (`mypy --strict`)
   - Performance benchmarks meeting targets
   - Security audit passing
   - Independent user story testing

**Branch Strategy**:
- Feature branches: `###-feature-name` (e.g., `001-core-python-package`)
- Branch naming must match spec directory number

**Pull Request Requirements**:
- All quality gates passing
- Constitution compliance verified
- User story independence demonstrated
- Performance benchmarks included
- Security review completed (if touching auth/credentials)

**Documentation Requirements**:
- Code documentation MUST be inline (docstrings, comments)
- Feature documentation MUST go in `specs/###-feature/`
- User guides MUST go in `docs/` site (if exists)
- NO ad-hoc standalone documentation files (e.g., `NOTES.md`)

## Governance

**Constitutional Authority**:
- This constitution supersedes all other development practices and guidelines
- Constitution compliance is MANDATORY for all features and contributions
- Violations MUST be explicitly justified in plan.md's Complexity Tracking table

**Amendment Process**:
1. Propose amendment with clear rationale
2. Document impact on existing code and templates
3. Update Sync Impact Report
4. Increment version:
   - MAJOR: Backward-incompatible principle changes
   - MINOR: New principles or material expansions
   - PATCH: Clarifications or non-semantic refinements
5. Propagate changes to templates (plan, spec, tasks)
6. Update guidance files and copilot instructions

**Compliance Enforcement**:
- All PRs MUST verify constitution compliance
- CI MUST check constitution gates (automated where possible)
- Code reviews MUST explicitly confirm principle adherence
- Complexity violations MUST be justified before merge

**Template Alignment**:
- `.specify/templates/plan-template.md` - Constitution Check section
- `.specify/templates/spec-template.md` - User story prioritization and independence
- `.specify/templates/tasks-template.md` - Test-first phases and story grouping
- `.github/copilot-instructions.md` - Auto-generated from constitution

**Living Document**:
- Constitution evolves with project needs
- Amendments require full impact analysis
- Version history tracks all changes
- Sync Impact Report documents ripple effects

**Version**: 1.0.0 | **Ratified**: 2025-10-22 | **Last Amended**: 2025-10-22
