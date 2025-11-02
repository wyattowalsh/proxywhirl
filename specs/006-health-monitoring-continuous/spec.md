# Feature Specification: Health Monitoring

**Feature Branch**: `006-health-monitoring-continuous`  
**Created**: 2025-10-08  
**Status**: Draft  
**Input**: User description: "Continuous health checks and proxy pool status tracking"

## Clarifications

### Session 2025-11-01

- Q: What threading/concurrency model should health checks use? → A: Background thread per proxy source with shared thread pool
- Q: How should health status changes integrate with the cache layer? → A: Automatically invalidate cache entry on health failure
- Q: What health check method should be used by default? → A: HTTP HEAD request to configurable URL
- Q: How should health check state persist across restarts? → A: Store in cache tier (L3 SQLite)
- Q: What notification mechanism for health events? → A: Structured logging with event callbacks

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated Proxy Health Checks (Priority: P1)

A system needs to continuously verify that proxies in the pool are alive and functional by performing periodic health checks, automatically detecting and removing dead proxies.

**Why this priority**: Core health monitoring - prevents request failures by ensuring only working proxies are used.

**Independent Test**: Can be tested by adding proxies to pool, running health checks, and verifying dead proxies are detected and marked unavailable.

**Acceptance Scenarios**:

1. **Given** a pool of proxies, **When** health check runs, **Then** each proxy is tested with a simple HTTP request
2. **Given** a proxy fails health check, **When** failure threshold is reached (e.g., 3 consecutive failures), **Then** proxy is marked as unhealthy
3. **Given** unhealthy proxy, **When** requests are made, **Then** unhealthy proxy is excluded from rotation
4. **Given** unhealthy proxy recovers, **When** health check succeeds, **Then** proxy is restored to active pool

---

### User Story 2 - Configurable Health Check Intervals (Priority: P1)

Operations team needs to configure health check frequency based on proxy source reliability - frequent checks for unreliable sources, less frequent for stable ones.

**Why this priority**: Optimizes resource usage - prevents over-checking stable proxies while ensuring unreliable ones are monitored closely.

**Independent Test**: Can be tested by setting different check intervals and verifying health checks run at correct frequencies.

**Acceptance Scenarios**:

1. **Given** health check interval set to 5 minutes, **When** time elapses, **Then** health checks run every 5 minutes
2. **Given** different proxy sources, **When** configured with different intervals, **Then** each source is checked at its specified frequency
3. **Given** interval configuration changes, **When** system reloads, **Then** new intervals take effect without restart

---

### User Story 3 - Real-Time Pool Status Tracking (Priority: P2)

Operators need real-time visibility into proxy pool status (total, active, failed, recovering) to understand system health and capacity.

**Why this priority**: Operational visibility - enables quick problem detection and capacity planning.

**Independent Test**: Can be tested by checking status endpoint and verifying counts match actual pool state.

**Acceptance Scenarios**:

1. **Given** proxy pool, **When** status is queried, **Then** accurate counts are returned (total, healthy, unhealthy, checking)
2. **Given** proxy status changes, **When** health check completes, **Then** status counts update in real-time
3. **Given** multiple proxy sources, **When** status is requested, **Then** breakdown by source is available

---

### User Story 4 - Health Check Customization (Priority: P2)

Users need to customize health check behavior (timeout, target URL, expected response) to match their use case and target server requirements.

**Why this priority**: Flexibility - ensures health checks accurately reflect real-world proxy usage patterns.

**Independent Test**: Can be tested by configuring custom health check and verifying it uses specified parameters.

**Acceptance Scenarios**:

1. **Given** custom health check URL, **When** check runs, **Then** specified URL is used instead of default
2. **Given** custom timeout setting, **When** proxy is slow, **Then** health check respects configured timeout
3. **Given** expected response pattern, **When** response doesn't match, **Then** proxy is marked as unhealthy

---

### User Story 5 - Automatic Proxy Recovery (Priority: P2)

System needs to automatically retry unhealthy proxies after a cooldown period to detect when they become available again, maximizing pool utilization.

**Why this priority**: Self-healing capability - prevents permanent loss of temporarily unavailable proxies.

**Independent Test**: Can be tested by marking proxy unhealthy, waiting for cooldown, and verifying recovery attempt is made.

**Acceptance Scenarios**:

1. **Given** proxy marked unhealthy, **When** cooldown period expires, **Then** recovery health check is attempted
2. **Given** recovery check succeeds, **When** proxy passes, **Then** proxy is restored to active pool
3. **Given** recovery check fails, **When** max retry count is reached, **Then** proxy is permanently removed

---

### User Story 6 - Health Event Notifications (Priority: P3)

Operations team wants to receive notifications when significant health events occur (proxy down, pool degraded, recovered) for proactive monitoring.

**Why this priority**: Proactive operations - enables quick response to health issues before they impact users.

**Independent Test**: Can be tested by triggering health events and verifying notifications are sent.

**Acceptance Scenarios**:

1. **Given** proxy becomes unhealthy, **When** threshold is reached, **Then** notification is sent (webhook, email, log)
2. **Given** pool health degrades below threshold, **When** detected, **Then** alert is triggered
3. **Given** proxy recovers, **When** health check passes, **Then** recovery notification is sent

---

### Edge Cases

- **Health check target URL unreachable**: Mark proxy as unhealthy, log DNS/network failure distinctly
- **All proxies simultaneously unhealthy**: Trigger pool degraded alert, allow manual override to use "least unhealthy" proxies
- **Health check timeout/hang**: Apply configured timeout (default 10s), cancel check and mark as failed
- **Concurrent health check overload**: Thread pool limits concurrent checks, queues excess checks with priority by last check time
- **Proxy fails during active request**: Mark unhealthy after request completes, do not interrupt in-flight requests
- **Partial proxy failures**: Single health check endpoint determines overall health (customize via FR-007)
- **Aggressive health check frequency**: Enforce minimum interval (10s) to prevent resource exhaustion

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST perform automated health checks on all proxies in pool using HTTP HEAD requests
- **FR-002**: System MUST support configurable health check intervals per proxy or source
- **FR-003**: System MUST mark proxies as unhealthy after configurable failure threshold
- **FR-004**: System MUST exclude unhealthy proxies from rotation automatically
- **FR-005**: System MUST track proxy status (healthy, unhealthy, checking, recovering)
- **FR-006**: System MUST provide real-time pool status counts and percentages
- **FR-007**: System MUST support custom health check URLs and endpoints
- **FR-008**: System MUST support configurable health check timeouts
- **FR-009**: System MUST validate health check responses against expected patterns (default: 2xx status codes)
- **FR-010**: System MUST implement automatic proxy recovery with cooldown periods
- **FR-011**: System MUST support configurable maximum recovery retry attempts
- **FR-012**: System MUST send health event notifications via structured logging with event callbacks
- **FR-013**: System MUST log all health check results with timestamps
- **FR-014**: System MUST track health check history per proxy
- **FR-015**: System MUST support manual health check triggering via API/CLI
- **FR-016**: System MUST handle concurrent health checks thread-safely
- **FR-017**: System MUST provide health check metrics (success rate, avg response time)
- **FR-018**: System MUST support graceful degradation when health check system fails
- **FR-019**: System MUST allow pausing/resuming health checks without stopping service
- **FR-020**: System MUST clean up resources from zombie health check tasks (zombie task defined as: thread running >2x configured check interval OR thread joined but not deregistered from active task registry)
- **FR-021**: System MUST use background thread per proxy source with shared thread pool for concurrent health checking
- **FR-022**: System MUST automatically invalidate cache entries when proxies become unhealthy
- **FR-023**: System MUST persist health check state in cache tier (L3 SQLite) for restart recovery

### Key Entities

**Terminology Note**: "Health check results" refers to runtime data structures and API responses. The database table storing historical data is named `health_history` (per FR-023).

- **Health Check**: Verification request to proxy with URL, timeout, expected response, result (uses HTTP HEAD by default)
- **Proxy Health Status**: Current state of proxy (healthy, unhealthy, checking, recovering, unknown) - persisted in L3 cache
- **Health Event**: Significant health state change (proxy down, recovered, pool degraded) - notified via callbacks
- **Pool Status**: Aggregate health statistics (total count, healthy count, unhealthy count, health percentage)
- **Health Check Configuration**: Settings for checks (interval, timeout, target URL, failure threshold, recovery settings)
- **Health Check Thread Pool**: Shared thread pool managing background threads (one per proxy source)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Health checks detect dead proxies within 1 minute of failure
- **SC-002**: System maintains 95% or higher pool health under normal conditions (normal conditions defined as: pool utilization <80%, request rate <100 req/s, no network disruptions or infrastructure failures)
- **SC-003**: Health check overhead uses less than 5% of system CPU
- **SC-004**: Pool status queries return in under 50ms
- **SC-005**: Automatic recovery restores 80% or more of temporarily failed proxies
- **SC-006**: Health check system handles 1000 concurrent checks without degradation
- **SC-007**: False positive rate for health failures is under 1%
- **SC-008**: Health events trigger notifications within 10 seconds of occurrence
- **SC-009**: Health check history is retained for at least 24 hours per proxy
- **SC-010**: System can perform health checks on 10,000 proxies within 5 minutes

## Assumptions

- Health check target URLs are generally accessible and reliable
- Network connectivity is stable enough for meaningful health checks
- Proxy failures are typically detectable via simple HTTP requests
- Health check intervals are configured reasonably (not too aggressive)
- System has sufficient resources to perform concurrent health checks
- Temporary proxy failures are common and recovery attempts are worthwhile

## Dependencies

- **Core Python Package** (001): Proxy pool access, ProxyRotator integration
- **Configuration Management** (config.py): Health check settings, intervals, thresholds
- **Logging System** (loguru): Health check event logging with structured data
- **Metrics & Observability**: Health check metrics tracking (success rate, response time)
- **Caching Mechanisms** (005): Cache invalidation on health failures, L3 persistence of health state
