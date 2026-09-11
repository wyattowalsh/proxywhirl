## ADDED Requirements

### Requirement: Non-loopback services require authentication
REST and networked MCP entry points MUST refuse a non-loopback bind unless the
corresponding authentication mode and required secret material are configured;
local development exceptions MUST remain explicit and loopback-only.

#### Scenario: Operator requests an unauthenticated public bind
- **WHEN** REST or networked MCP is configured on a non-loopback address without valid authentication settings
- **THEN** startup fails closed before accepting requests

### Requirement: Authentication policy covers the complete interface matrix
Every REST route and MCP action/resource SHALL be classified as public-read,
authenticated-read, or authenticated-write, and unknown or mutating operations
MUST fail closed.

#### Scenario: Unauthenticated mutation is attempted
- **WHEN** a client invokes any REST mutation or MCP write action without valid authorization
- **THEN** the request is rejected without performing or partially applying the mutation

### Requirement: Network targets pass SSRF policy at every hop
Source, proxy-validation, browser-rendering, health-check, redirect, and proxied
request targets MUST be validated against the shared SSRF policy before DNS use
and after every redirect or address change.

#### Scenario: Public URL redirects to a private address
- **WHEN** an initially allowed URL resolves or redirects to loopback, link-local, private, metadata, or otherwise forbidden address space
- **THEN** the request is rejected before connecting to the forbidden target

### Requirement: Streaming and parsing are bounded before accumulation
REST bodies, source downloads, decompression, line parsing, browser output, and
response streaming MUST enforce configured byte, item, time, and concurrency
limits without first buffering an unbounded payload.

#### Scenario: Peer sends an oversized streamed response
- **WHEN** a peer streams more data than the configured maximum
- **THEN** ProxyWhirl stops reading at the boundary, closes the stream, and returns a sanitized bounded-error response

### Requirement: Credentials never cross public output boundaries
Passwords, tokens, API keys, authorization headers, embedded proxy credentials,
and secret-bearing exception content MUST be redacted from logs, metrics,
traces, CLI output, REST responses, MCP results, generated docs, and exported
public proxy assets.

#### Scenario: Credential-bearing failure is rendered
- **WHEN** a downstream exception includes a credential-bearing URL or header
- **THEN** every user-visible and model-visible representation contains only the approved redacted form

### Requirement: CLI and MCP secret input is non-echoing and non-persistent by default
CLI and MCP authentication or credential values MUST be accepted only through
approved secret channels, MUST NOT appear in help schemas or command history,
and MUST NOT be persisted unless the user explicitly selects an encrypted
storage workflow.

#### Scenario: Operator supplies an MCP API key
- **WHEN** an MCP server receives a key through approved metadata, headers, or environment configuration
- **THEN** the key is excluded from tool schemas, structured results, logs, and unencrypted persistent state

### Requirement: Release dependencies have no unresolved program-blocking advisory
The exact locked Python and web dependency sets used for a release candidate
MUST pass the project's blocking audit policy, and every additional scanner
finding MUST be fixed or documented with package, advisory, reachability,
compensating control, owner, and expiry.

#### Scenario: Known Safety blocker is evaluated
- **WHEN** the candidate is checked against the findings from Security Scan run `31285534474`
- **THEN** the 11 reported vulnerabilities in cryptography, joserfc, pydantic-settings, pyjwt, and soupsieve are absent from the release lock or have an explicitly approved, time-bounded exception
