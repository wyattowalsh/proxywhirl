# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) documenting key technical decisions made in the ProxyWhirl project.

## What are ADRs?

Architecture Decision Records are lightweight documents that capture important architectural decisions along with their context and consequences. They help developers understand:

- **Why** certain technical approaches were chosen
- **What** alternatives were considered
- **How** the decision impacts the system
- **When** to revisit the decision

## ADR Format

Each ADR follows this structure:

- **Title**: Descriptive name of the decision
- **Status**: Accepted, Proposed, Deprecated, or Superseded
- **Context**: Problem statement and requirements
- **Decision**: The chosen solution with detailed explanation
- **Consequences**: Positive and negative outcomes, tradeoffs
- **Alternatives Considered**: Other approaches and why they were rejected
- **Implementation Details**: Technical specifics and code references
- **References**: Links to code, tests, and related ADRs

## Current ADRs

### [ADR-001: Three-Tier Cache Architecture](001-three-tier-cache.md)
**Status**: Accepted

Describes the three-tier caching system (L1 memory, L2 JSONL files, L3 SQLite) with automatic promotion/demotion, TTL management, and credential encryption.

**Key Topics**:
- Cache tier hierarchy and responsibilities
- Promotion/demotion strategies
- TTL-based expiration mechanisms
- Graceful degradation on tier failures
- Credential security across tiers

### [ADR-002: Circuit Breaker Pattern](002-circuit-breaker.md)
**Status**: Accepted

Documents the circuit breaker implementation for intelligent proxy failure management with three states (CLOSED, OPEN, HALF_OPEN) and optional state persistence.

**Key Topics**:
- Circuit breaker state machine
- Rolling time window failure tracking
- Automatic recovery testing
- State persistence across restarts
- Thread safety and concurrency

### [ADR-003: Strategy Pattern for Rotation](003-strategy-pattern.md)
**Status**: Accepted

Explains the strategy pattern design for proxy rotation algorithms with a registry-based plugin architecture supporting 8 built-in strategies and custom extensions.

**Key Topics**:
- RotationStrategy protocol interface
- Built-in strategies (round-robin, weighted, performance-based, etc.)
- Strategy registry for plugins
- SelectionContext for request metadata
- Thread safety patterns per strategy

### [ADR-004: Storage Backend Decisions](004-storage-backend.md)
**Status**: Accepted

Covers the choice of SQLite as the primary storage backend with multiple storage implementations (SQLite, JSON files, JSONL sharding) for different use cases.

**Key Topics**:
- SQLite async operations via aiosqlite
- ProxyTable schema design (126 columns)
- File-based storage for exports
- JSONL sharding for cache tier
- Git-tracked analytics database
- DELETE journal mode for git compatibility

## Usage Guidelines

### When to Create an ADR

Create an ADR when making decisions about:
- System architecture and design patterns
- Technology choices (databases, frameworks, libraries)
- API design and interfaces
- Performance optimizations with tradeoffs
- Security mechanisms
- Data models and schemas

### When NOT to Create an ADR

Don't create ADRs for:
- Implementation details that don't affect architecture
- Obvious or trivial choices
- Temporary workarounds or hacks
- Decisions that are easily reversible

### Updating ADRs

ADRs are **immutable** once accepted. To change a decision:
1. Create a new ADR that supersedes the old one
2. Update the old ADR's status to "Superseded by ADR-XXX"
3. Reference the old ADR in the new one

## References

- [ADR GitHub Organization](https://adr.github.io/)
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) by Michael Nygard
- [ADR Tools](https://github.com/npryce/adr-tools)

## Contributing

When adding new ADRs:
1. Use the next sequential number (ADR-005, ADR-006, etc.)
2. Follow the standard format (see existing ADRs)
3. Include code references and test locations
4. Document alternatives considered
5. Explain tradeoffs clearly
6. Keep it concise but thorough
