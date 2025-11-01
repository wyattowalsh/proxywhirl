# Feature Specification: Logging System

**Feature Branch**: `007-logging-system-structured`  
**Created**: 2025-10-08  
**Status**: Draft  
**Input**: User description: "Structured logging with multiple output formats and levels"

## Clarifications

### Session 2025-11-01

- Q: How should this feature integrate with existing loguru usage? → A: Extend existing loguru configuration and add structured output handlers
- Q: What happens when log destination becomes unavailable (disk full, network down)? → A: Log to fallback destination (stderr/console) + emit warning
- Q: How does system handle extremely high-volume logging that exceeds buffer capacity? → A: Drop oldest buffered entries + increment drop counter
- Q: What threading model should async logging use? → A: Single background thread + bounded queue with drop policy (loguru native)
- Q: How do users configure and update logging settings? → A: Environment variables + optional config file

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Structured Log Output (Priority: P1)

Developers and operators need structured logs (JSON, key-value pairs) instead of plain text to enable automated parsing, querying, and analysis in log aggregation systems.

**Why this priority**: Core logging capability - enables modern observability practices and log analysis.

**Independent Test**: Can be tested by generating logs and verifying they are formatted as structured data (JSON/structured text).

**Acceptance Scenarios**:

1. **Given** logging is configured, **When** event occurs, **Then** log entry contains structured fields (timestamp, level, message, context)
2. **Given** JSON format selected, **When** logs are written, **Then** each entry is valid JSON with consistent schema
3. **Given** structured logs, **When** queried, **Then** fields can be extracted and filtered programmatically

---

### User Story 2 - Configurable Log Levels (Priority: P1)

Users need to control logging verbosity via levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) to balance detail with performance and storage costs.

**Why this priority**: Essential for production use - prevents log flooding while ensuring critical issues are captured.

**Independent Test**: Can be tested by setting different log levels and verifying only appropriate messages are logged.

**Acceptance Scenarios**:

1. **Given** log level set to INFO, **When** DEBUG messages are generated, **Then** DEBUG messages are not logged
2. **Given** log level set to ERROR, **When** INFO messages are generated, **Then** only ERROR and CRITICAL messages appear
3. **Given** log level changes at runtime, **When** configuration reloads, **Then** new level takes effect immediately

---

### User Story 3 - Multiple Output Destinations (Priority: P2)

Operations team needs to send logs to multiple destinations simultaneously (console, file, syslog, remote aggregator) for different monitoring and archival purposes.

**Why this priority**: Operational flexibility - supports different monitoring workflows and compliance requirements.

**Independent Test**: Can be tested by configuring multiple outputs and verifying logs appear in all destinations.

**Acceptance Scenarios**:

1. **Given** console and file outputs configured, **When** log event occurs, **Then** log appears in both console and file
2. **Given** remote logging enabled, **When** logs are generated, **Then** logs are sent to remote endpoint (syslog, HTTP)
3. **Given** output destination fails, **When** logging continues, **Then** other destinations continue receiving logs

---

### User Story 4 - Contextual Logging with Metadata (Priority: P2)

Developers need to attach contextual metadata (request ID, user ID, proxy URL, operation) to log entries for correlation and debugging.

**Why this priority**: Debugging efficiency - enables tracing request flows and correlating related log entries.

**Independent Test**: Can be tested by logging with context and verifying metadata appears in log entries.

**Acceptance Scenarios**:

1. **Given** request context, **When** logging occurs, **Then** request ID is included in log entry
2. **Given** proxy operation, **When** error is logged, **Then** proxy URL and operation type are included
3. **Given** nested operations, **When** logging occurs, **Then** full context hierarchy is preserved

---

### User Story 5 - Log Rotation and Retention (Priority: P2)

System administrators need automatic log file rotation by size or time with configurable retention policies to manage disk space.

**Why this priority**: Production requirement - prevents disk exhaustion and maintains log history.

**Independent Test**: Can be tested by generating logs until rotation threshold and verifying old files are rotated/archived.

**Acceptance Scenarios**:

1. **Given** rotation size limit of 100MB, **When** log file reaches limit, **Then** file is rotated and new file is created
2. **Given** daily rotation configured, **When** day changes, **Then** log file is rotated with timestamp
3. **Given** retention of 7 days, **When** log files are older than 7 days, **Then** old files are automatically deleted

---

### User Story 6 - Performance-Optimized Logging (Priority: P3)

High-throughput applications need asynchronous logging that doesn't block main execution threads, ensuring logging overhead doesn't impact proxy performance.

**Why this priority**: Performance optimization - prevents logging from becoming a bottleneck.

**Independent Test**: Can be tested by measuring request latency with and without logging and verifying minimal impact.

**Acceptance Scenarios**:

1. **Given** async logging enabled, **When** log entry is created, **Then** logging call returns immediately without blocking
2. **Given** high log volume, **When** system is under load, **Then** logging overhead is under 5% of total CPU time
3. **Given** log queue full, **When** new logs are generated, **Then** system handles gracefully (drop or block based on policy)

---

### Edge Cases

- **Log destination unavailable** (disk full, network down): Log to fallback destination (stderr/console) and emit warning (maintains observability during infrastructure issues)
- **High-volume logging exceeds buffer**: Drop oldest buffered entries and increment drop counter metric (bounded memory, preserves recent logs)
- **Log rotation during active writes**: Use atomic file operations and write locks to ensure no data loss
- **Multiple processes writing to same file**: Use process-safe file handlers with advisory locks (loguru's `enqueue=True` provides this)
- **Structured log serialization fails** (circular references, large objects): Fall back to string representation and log serialization error
- **Logging from crash/signal handlers**: Use synchronous logging for critical paths (avoid async queue)
- **Retention policy conflicts with active files**: Skip active files, only clean up closed/rotated files

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST extend existing loguru configuration with structured output handlers (JSON, logfmt)
- **FR-002**: System MUST support standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) via loguru
- **FR-003**: System MUST allow runtime log level configuration without restart (via environment variables + optional config file reload)
- **FR-004**: System MUST support multiple simultaneous output destinations
- **FR-005**: System MUST support console, file, syslog, and HTTP remote logging outputs
- **FR-006**: System MUST include timestamp, log level, and message in all log entries
- **FR-007**: System MUST support contextual metadata attachment to log entries
- **FR-008**: System MUST provide request/operation correlation IDs in logs
- **FR-009**: System MUST implement automatic log file rotation by size
- **FR-010**: System MUST implement automatic log file rotation by time (daily, hourly)
- **FR-011**: System MUST support configurable log retention policies
- **FR-012**: System MUST support asynchronous logging with single background thread and bounded queue (using loguru's `enqueue=True`)
- **FR-013**: System MUST handle log destination failures gracefully (fallback to stderr/console with warning emission)
- **FR-014**: System MUST support custom log formatters and handlers
- **FR-015**: System MUST log all proxy operations (selection, request, failure, retry)
- **FR-016**: System MUST log health check events and status changes
- **FR-017**: System MUST support sensitive data redaction in logs (credentials, PII)
- **FR-018**: System MUST provide log filtering by component or module
- **FR-019**: System MUST support log sampling for high-volume scenarios
- **FR-020**: System MUST handle Unicode and special characters correctly in logs
- **FR-021**: System MUST track and expose dropped log count when buffer capacity exceeded (oldest entries dropped first)

### Key Entities

- **Log Entry**: Record of event with timestamp, level, message, metadata, and context (structured as JSON/logfmt)
- **Log Handler**: Output destination (console, file, remote) with formatter and filters (loguru handler with custom serializer)
- **Log Context**: Metadata attached to log entries (request ID, operation, proxy, user) via loguru's `bind()` and contextvars
- **Log Configuration**: Settings for levels, formats, outputs, rotation, and retention (environment variables + optional config file via pydantic-settings)
- **Log Rotation Policy**: Rules for when and how to rotate log files (loguru's rotation parameter with size/time triggers)
- **Drop Counter**: Metric tracking number of logs dropped when buffer capacity exceeded

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Structured logs can be parsed and queried in log aggregation tools
- **SC-002**: Log level changes take effect within 1 second of configuration update
- **SC-003**: Logging overhead adds less than 5% latency to proxy requests
- **SC-004**: Log rotation completes without data loss or corruption
- **SC-005**: System handles 10,000 log entries per second without blocking
- **SC-006**: Logs include correlation IDs for 100% of proxy operations
- **SC-007**: Sensitive data is redacted from 100% of log entries
- **SC-008**: Log files rotate within 1 minute of reaching size/time threshold
- **SC-009**: Multiple output destinations operate independently (one failure doesn't affect others)
- **SC-010**: Log retention policy cleanups execute within 5 minutes of schedule

## Assumptions

- Log storage has sufficient capacity for configured retention periods
- Operators configure appropriate log levels for their use case
- Remote log destinations (if used) are accessible and reliable (with fallback to local logging on failure)
- Log rotation thresholds are set reasonably based on log volume
- Application context for logging (request IDs, etc.) is properly maintained via contextvars
- Log parsing tools support JSON or logfmt structured formats
- Loguru library is already installed and configured in proxywhirl
- Environment variables are accessible for runtime configuration
- Bounded queue size is sufficient for typical log volumes (configurable via environment variable)

## Dependencies

- Core Python Package (001) for operation events to log
- Configuration Management (012) for logging settings via environment variables + config file
- Health Monitoring (006) for health event logging
- Metrics & Observability (008) for log volume and drop counter metrics
- Existing loguru installation in proxywhirl for log handler infrastructure
- pydantic-settings for configuration management and runtime reloading
- All features for component-specific logging
