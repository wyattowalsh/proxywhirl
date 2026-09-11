## ADDED Requirements

### Requirement: Request lifecycle effects occur exactly once
ProxyWhirl MUST apply success, failure, retry, circuit-breaker, health, active
request, and metrics transitions exactly once for each logical request outcome,
including retry exhaustion, cancellation, and failover.

#### Scenario: Retries exhaust
- **WHEN** every attempt for one logical request fails
- **THEN** the proxy and request state record one terminal failure without double-counting a retry or circuit-breaker transition

### Requirement: Sync and async rotators have semantic parity
The synchronous and asynchronous rotators SHALL enforce the same selection,
empty-pool, health, retry, failover, session, and result-recording semantics,
with differences limited to explicit concurrency and lifecycle APIs.

#### Scenario: Equivalent workflows use both rotators
- **WHEN** the same deterministic proxy pool and outcome sequence is exercised through sync and async rotators
- **THEN** both produce equivalent proxy selections, state transitions, and terminal errors

### Requirement: Runtime resources have bounded ownership
HTTP clients, tasks, threads, locks, streams, database connections, and browser
resources MUST have an explicit owner and MUST close on normal completion,
exception, cancellation, and repeated shutdown.

#### Scenario: Async request is cancelled
- **WHEN** cancellation interrupts an in-flight request or validation operation
- **THEN** owned clients and tasks close, active-request counters settle, and a later idempotent shutdown succeeds

### Requirement: Storage backends provide contract parity
SQLite and file storage SHALL preserve the same supported proxy fields,
credential policy, filtering, ordering where documented, and error taxonomy for
equivalent operations.

#### Scenario: Backend parity corpus is exercised
- **WHEN** the same round-trip, update, removal, invalid-record, and partial-credential corpus is run against both supported backends
- **THEN** normalized results and public errors match the declared storage contract

### Requirement: Schema migration has one authoritative head
Alembic SHALL be the authoritative schema evolution mechanism, SHALL expose one
head for the `0.4` candidate, and SHALL apply safely to empty and representative
`0.3.3` databases without import-time schema mutation competing with migrations.

#### Scenario: Migration topology is inspected
- **WHEN** the candidate's Alembic graph and package resources are loaded from an isolated wheel
- **THEN** exactly one head is discoverable and upgrade-to-head succeeds for empty and upgraded databases

### Requirement: Concurrent state remains coherent
Proxy pools, strategy state, circuit breakers, rate limits, caches, sessions,
queues, and persistence operations MUST preserve documented invariants under
concurrent sync and async access.

#### Scenario: Concurrent mutation and selection overlap
- **WHEN** bounded workers select, update, remove, expire, and persist proxies concurrently
- **THEN** no deadlock, leaked task, duplicate identity, negative counter, stale index, or cache-coherence violation occurs

### Requirement: Untrusted operations fail within bounds
Parsing, regular-expression evaluation, streaming, network validation, and
shutdown paths MUST enforce explicit time, size, concurrency, and resource
bounds and return the documented public error family.

#### Scenario: Adversarial input reaches a bounded operation
- **WHEN** malformed or pathological input attempts to exceed a configured bound
- **THEN** the operation stops within the bound, releases owned resources, and returns a sanitized deterministic error
