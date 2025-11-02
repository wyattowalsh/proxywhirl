# Feature Specification: Advanced Retry and Failover Logic

**Feature Branch**: `014-retry-failover-logic`  
**Created**: 2025-11-02  
**Status**: Draft  
**Input**: User description: "Advanced retry and failover logic with exponential backoff, circuit breakers, and intelligent proxy selection during failures"

## Clarifications

### Session 2025-11-02

- Q: Should the system queue requests when all circuit breakers are open, or immediately return an error? → A: Immediately return error (503 Service Temporarily Unavailable) without queuing
- Q: How should the 60-second failure time window work for circuit breaker thresholds? → A: Rolling window - track failures in last 60 seconds; old failures beyond window are discarded
- Q: Should circuit breaker states persist across system restarts? → A: Reset all circuit breakers to closed state on restart; let system re-learn proxy health
- Q: How long should retry metrics be retained in memory? → A: 24 hours in-memory; balances observability with memory footprint
- Q: How should users define custom retry strategies? → A: Configuration only - support parameterized built-in strategies (exponential with cap, jitter, etc.)
- Q: How does intelligent proxy selection scoring work (FR-007)? → A: Weighted formula: `score = (0.7 × success_rate) + (0.3 × (1 - normalized_latency))` where success_rate is recent success percentage (last 100 requests) and normalized_latency is proxy's avg latency divided by max observed latency across all proxies. Higher scores selected preferentially.
- Q: What are the exact parameters for configurable retry strategies (FR-012)? → A: Exponential: base_delay (0.1-60s), multiplier (1.1-10x), cap (1-300s), jitter (boolean); Linear: base_delay (0.1-60s), cap (1-300s), jitter (boolean); Fixed: delay (0.1-60s), jitter (boolean)
- Q: How is geographic region determined for geo-targeted proxy selection (US3)? → A: Optional proxy metadata - users can tag proxies with region identifier (e.g., "US-EAST", "EU-WEST") via Proxy.metadata dict. If no region metadata present, geo-targeting is skipped and selection falls back to performance-based scoring only.
- Q: What's the difference between "retry" and "failover" in this feature? → A: **Retry** = reattempting the same operation after a delay (may use same or different proxy); **Failover** = switching to a different proxy after failure. This feature implements both: automatic retries with intelligent proxy failover selection.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Request Retry with Exponential Backoff (Priority: P1)

When a proxied request fails due to transient network issues, connection timeouts, or temporary proxy unavailability, the system automatically retries the request using exponential backoff timing. This prevents overwhelming failed proxies while giving temporary issues time to resolve, improving overall request success rates without manual intervention.

**Why this priority**: Core functionality that directly impacts reliability and user experience. Without automatic retries, users experience unnecessary failures from transient issues that would succeed on retry.

**Independent Test**: Can be fully tested by sending requests through a proxy that intermittently fails, verifying automatic retries with increasing delays, and confirming eventual success or maximum retry limit. Delivers immediate value by handling temporary network glitches automatically.

**Acceptance Scenarios**:

1. **Given** a request is sent through a proxy, **When** the proxy returns a connection timeout (5xx error), **Then** the system automatically retries with a 1-second delay
2. **Given** a retry fails, **When** the second attempt also fails, **Then** the system waits 2 seconds before the third attempt (exponential backoff)
3. **Given** multiple consecutive failures, **When** maximum retry attempts are reached (default 3), **Then** the system marks the request as failed and returns an error to the user
4. **Given** a retry succeeds, **When** the response is received successfully, **Then** the system returns the response without further retries
5. **Given** requests are being retried, **When** a user queries request status, **Then** the system reports current retry attempt number and next retry time

---

### User Story 2 - Circuit Breaker Pattern for Failed Proxies (Priority: P1)

When a proxy experiences repeated failures within a time window, the system automatically opens a circuit breaker, temporarily removing the proxy from the rotation pool. This prevents cascading failures by avoiding proxies that are clearly experiencing issues, while periodically testing them for recovery in a half-open state before fully restoring them to the pool.

**Why this priority**: Critical for system stability and performance. Prevents wasting time and resources on known-bad proxies, protects against cascading failures, and maintains overall system throughput.

**Independent Test**: Can be fully tested by configuring a proxy to fail consistently, verifying circuit breaker opens after threshold failures, confirming proxy removal from rotation, observing periodic recovery attempts in half-open state, and validating automatic restoration after successful recovery tests. Delivers immediate value by protecting the system from repeated failures.

**Acceptance Scenarios**:

1. **Given** a proxy fails 5 consecutive requests within a rolling 60-second window, **When** the failure threshold is met, **Then** the circuit breaker opens and the proxy is removed from rotation
2. **Given** a circuit breaker is open, **When** 30 seconds have elapsed (default timeout), **Then** the circuit breaker enters half-open state and allows one test request
3. **Given** a circuit breaker is half-open, **When** a test request succeeds, **Then** the circuit breaker closes and the proxy is restored to full rotation
4. **Given** a circuit breaker is half-open, **When** a test request fails, **Then** the circuit breaker reopens and the timeout period restarts
5. **Given** multiple proxies have open circuit breakers, **When** a user queries pool status, **Then** the system reports circuit breaker states (open/half-open/closed) with time until next retry for each proxy

---

### User Story 3 - Intelligent Proxy Failover Selection (Priority: P2)

When a request fails and needs to be retried, the system intelligently selects an alternative proxy based on recent performance metrics, geographic proximity to target, and current load. This goes beyond simple round-robin failover by choosing the most likely proxy to succeed based on historical data and current conditions.

**Why this priority**: Enhances retry success rates and reduces total request latency. While automatic retries (P1) handle the mechanics, intelligent selection improves the probability of quick success.

**Independent Test**: Can be fully tested by simulating proxy failures with varying performance characteristics, verifying the system preferentially selects better-performing proxies for retries, and measuring improved retry success rates compared to random selection. Delivers value by reducing retry cycles needed for success.

**Acceptance Scenarios**:

1. **Given** a request fails on proxy A, **When** selecting a retry proxy, **Then** the system excludes proxy A and selects from remaining proxies based on success rate metrics
2. **Given** multiple proxies are available for retry, **When** one proxy has 95% success rate and another has 60%, **Then** the system preferentially selects the higher-performing proxy
3. **Given** a retry is needed for a geo-targeted request, **When** the failed proxy served region US-EAST, **Then** the system prioritizes other US-EAST proxies over different regions
4. **Given** performance metrics show proxy B is currently overloaded (high response times), **When** selecting a retry proxy, **Then** the system deprioritizes proxy B in favor of less-loaded alternatives
5. **Given** all available proxies have circuit breakers open, **When** a retry is needed, **Then** the system immediately returns a 503 Service Temporarily Unavailable error with a clear message indicating all proxies are temporarily unavailable

---

### User Story 4 - Configurable Retry Policies (Priority: P2)

Users can configure retry behavior per request or globally, including maximum retry attempts, backoff timing strategies (exponential, linear, fixed), timeout values, circuit breaker thresholds, and which HTTP error codes trigger retries. This allows fine-tuning retry behavior for different use cases, from aggressive retries for critical requests to conservative retries for bulk operations.

**Why this priority**: Enables customization for diverse use cases without requiring code changes. Different applications have different tolerance for latency vs. success rates, and this provides the flexibility needed for production deployments.

**Independent Test**: Can be fully tested by configuring different retry policies, sending test requests with each policy, and verifying behavior matches configuration (attempt counts, timing, error handling). Delivers value by allowing users to optimize retry behavior for their specific needs.

**Acceptance Scenarios**:

1. **Given** a user sets max_retries=5 for a request, **When** the request fails, **Then** the system attempts up to 5 retries before giving up (instead of default 3)
2. **Given** a user configures linear backoff with 2-second intervals, **When** retries occur, **Then** delays are 2s, 4s, 6s instead of exponential 1s, 2s, 4s
3. **Given** a user specifies retry_on_status_codes=[502, 503, 504], **When** a 500 error occurs, **Then** the system does not retry (only specified codes trigger retries)
4. **Given** global retry policy is configured, **When** a request is sent without per-request policy, **Then** the system applies the global policy settings
5. **Given** both global and per-request policies exist, **When** a request is sent with per-request policy, **Then** the per-request policy overrides global settings

---

### User Story 5 - Retry Metrics and Observability (Priority: P3)

The system tracks and exposes detailed metrics about retry behavior, including retry counts, success rates after N retries, circuit breaker state changes, average retry latency, and retry reason distributions. Users can query these metrics via API or export them for monitoring systems to understand retry patterns, identify problematic proxies, and optimize retry configurations.

**Why this priority**: Enables data-driven optimization of retry policies and proxy pool management. While the system works without metrics, they're essential for tuning and troubleshooting in production.

**Independent Test**: Can be fully tested by generating various failure scenarios, collecting retry metrics, and verifying accurate reporting of retry counts, success rates, latency distributions, and circuit breaker events. Delivers value by providing visibility into retry effectiveness.

**Acceptance Scenarios**:

1. **Given** requests are being retried, **When** a user queries retry metrics, **Then** the system returns total retry count, success rate after 1st retry, 2nd retry, 3rd retry, etc.
2. **Given** circuit breakers are opening/closing, **When** a user queries circuit breaker metrics, **Then** the system reports state change counts and current state for each proxy
3. **Given** retry metrics are collected over time, **When** a user requests historical data, **Then** the system provides time-series data showing retry patterns for the last 24 hours (hourly, daily aggregates)
4. **Given** different retry policies are in use, **When** a user queries policy effectiveness, **Then** the system reports success rates grouped by policy configuration
5. **Given** a monitoring system integrates with the metrics API, **When** circuit breakers open frequently, **Then** the monitoring system can alert operators to investigate proxy health

---

### Edge Cases

- What happens when all proxies have open circuit breakers and a new request arrives?
  - See FR-019: System immediately returns 503 Service Temporarily Unavailable error with clear message; no request queuing performed
- How does system handle a proxy that becomes healthy during a retry cycle?
  - Circuit breaker recovery tests should detect this, but in-flight retries continue with originally selected proxies
- What happens when retry delays exceed request timeout?
  - System should fail fast and not attempt retries that would exceed the total request timeout
- How does system handle concurrent requests failing the same proxy simultaneously?
  - Circuit breaker state changes must be thread-safe to prevent race conditions
- What happens when exponential backoff delays become excessively long?
  - System should cap maximum backoff delay (e.g., 30 seconds) to prevent indefinite waits
- How does system handle retries when the original request was not idempotent (POST, PUT with side effects)?
  - Retry logic should check request method and either skip retries for non-idempotent operations or require explicit opt-in
- What happens when network connectivity is completely lost?
  - System should detect widespread failure (all proxies failing) and fail fast rather than exhausting all retries
- How does system handle partial responses or streaming data during failures?
  - Retry logic should only apply to complete failures, not partial successes; streaming requests may need different retry strategies

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement exponential backoff retry logic with configurable base delay (default 1 second) and multiplier (default 2x)
- **FR-002**: System MUST support configurable maximum retry attempts per request (default 3 attempts)
- **FR-003**: System MUST implement circuit breaker pattern with configurable failure threshold (default 5 failures), rolling time window (default 60 seconds), and timeout period (default 30 seconds) before transitioning to half-open state
- **FR-004**: System MUST track circuit breaker states (closed, open, half-open) per proxy with automatic state transitions
- **FR-005**: System MUST exclude proxies with open circuit breakers from normal request rotation
- **FR-006**: System MUST perform periodic health checks on proxies with open circuit breakers in half-open state
- **FR-007**: System MUST intelligently select alternative proxies for retries based on recent success rates, avoiding the failed proxy
- **FR-008**: System MUST support per-request retry policy configuration that overrides global defaults
- **FR-009**: System MUST track retry metrics including attempt counts, success rates by attempt number, and total retry latency, retaining data in-memory for 24 hours
- **FR-010**: System MUST respect total request timeout, canceling remaining retries if timeout would be exceeded
- **FR-011**: System MUST differentiate between retryable errors (network timeouts, 502/503/504) and non-retryable errors (authentication failures, 4xx client errors)
- **FR-012**: System MUST support configurable retry strategies via parameterized built-in options: exponential backoff (with configurable base, multiplier, cap, jitter), linear backoff, and fixed delay
- **FR-013**: System MUST provide thread-safe circuit breaker state management for concurrent request handling
- **FR-014**: System MUST cap maximum backoff delay to prevent excessive wait times (default 30 seconds)
- **FR-015**: System MUST expose circuit breaker state and retry metrics via API endpoints
- **FR-016**: System MUST log retry attempts and circuit breaker state changes with appropriate log levels
- **FR-017**: System MUST support configurable lists of HTTP status codes that trigger retries
- **FR-018**: System MUST handle non-idempotent requests (POST, PUT) by requiring explicit retry opt-in or skipping retries by default
- **FR-019**: System MUST detect widespread failures (all proxies failing) and immediately return 503 Service Temporarily Unavailable error without queuing or exhausting retries
- **FR-020**: System MUST maintain backward compatibility with existing rotation strategies while adding retry/failover capabilities
- **FR-021**: System MUST reset all circuit breaker states to closed on restart, allowing proxies to be re-evaluated for health

### Key Entities

- **RetryPolicy**: Configuration object containing max_attempts, backoff_strategy (exponential/linear/fixed with parameters like base_delay, multiplier, cap, jitter), retry_status_codes, max_backoff_delay, timeout settings. Can be defined globally or per-request.
- **CircuitBreaker**: State machine per proxy tracking failure counts within a rolling time window, state (closed/open/half-open), failure threshold, time window duration, timeout period, next test time. Manages proxy availability based on recent failures.
- **RetryAttempt**: Record of a single retry attempt containing original_request, attempt_number, proxy_used, timestamp, outcome, delay_before_retry. Used for metrics and debugging.
- **RetryMetrics**: Aggregated metrics collection containing retry attempt history, circuit breaker events, and statistical summaries. Supports querying by time range, proxy, and policy configuration.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Request success rate improves by at least 15% for transient failures (network timeouts, temporary proxy issues) compared to single-attempt requests
- **SC-002**: System reduces wasted retries on consistently-failing proxies by 80% through circuit breaker pattern (measured by retry attempts on proxies with >70% failure rate)
- **SC-003**: 95th percentile request latency for successfully-retried requests remains under 5 seconds (including all retry delays)
- **SC-004**: Circuit breaker state transitions (open/close) occur within 1 second of threshold breach for responsive failure detection
- **SC-005**: Intelligent failover selection achieves 20% higher retry success rate on first retry attempt compared to random proxy selection (baseline: random selection from available proxies without filtering by success rate or performance metrics)
- **SC-006**: System handles 1000+ concurrent requests with retry/failover logic without performance degradation (less than 5% increase in response time overhead)
- **SC-007**: Retry metrics API responds in under 100ms for metric queries covering last 24 hours of data
- **SC-008**: Zero race conditions or deadlocks in circuit breaker state management under load testing with 10,000+ concurrent requests
- **SC-009**: Users can configure and deploy custom retry policies without code changes, with configuration taking effect immediately
- **SC-010**: 90% of requests that eventually succeed do so within 2 retry attempts, minimizing total latency impact
