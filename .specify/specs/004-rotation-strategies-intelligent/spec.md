# Feature Specification: Rotation Strategies

**Feature Branch**: `004-rotation-strategies-intelligent`  
**Created**: 2025-10-08  
**Status**: Draft  
**Input**: User description: "Intelligent algorithms for proxy selection and rotation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Round-Robin Rotation (Priority: P1)

A web scraper needs to distribute requests evenly across all available proxies to prevent any single proxy from being overloaded or rate-limited.

**Why this priority**: Most fundamental rotation strategy - provides basic load distribution and is easy to understand and test.

**Independent Test**: Can be tested by making sequential requests and verifying each uses the next proxy in the pool in circular order.

**Acceptance Scenarios**:

1. **Given** a pool of 5 proxies, **When** 10 requests are made, **Then** each proxy is used exactly twice in sequential order
2. **Given** round-robin rotation, **When** last proxy in pool is used, **Then** next request wraps around to first proxy
3. **Given** a proxy fails health check, **When** round-robin rotation continues, **Then** failed proxy is skipped automatically

---

### User Story 2 - Random Selection Strategy (Priority: P2)

A user wants to randomize proxy selection to avoid predictable patterns that might be detected by target servers implementing anti-bot measures.

**Why this priority**: Enhances anonymity and evasion - critical for bypassing sophisticated detection systems.

**Independent Test**: Can be tested by making multiple requests and verifying proxy selection follows uniform random distribution.

**Acceptance Scenarios**:

1. **Given** a pool of proxies, **When** 1000 requests are made, **Then** proxy usage distribution is roughly uniform (within 10% variance)
2. **Given** random selection, **When** consecutive requests are made, **Then** same proxy can be selected multiple times (no forced rotation)
3. **Given** weighted random selection, **When** proxies have different success rates, **Then** high-performing proxies are selected more frequently

---

### User Story 3 - Least-Used Strategy (Priority: P2)

A high-volume scraping operation wants to automatically balance load by selecting the proxy that has handled the fewest requests, ensuring optimal resource utilization.

**Why this priority**: Optimizes proxy pool utilization - prevents overloading popular proxies while maximizing throughput.

**Independent Test**: Can be tested by tracking request counts and verifying least-used proxy is always selected next.

**Acceptance Scenarios**:

1. **Given** proxies with different request counts, **When** next request is made, **Then** proxy with lowest count is selected
2. **Given** multiple proxies with same lowest count, **When** request is made, **Then** selection among them is deterministic or random (configurable)
3. **Given** request completes, **When** using least-used strategy, **Then** selected proxy's counter is incremented immediately

---

### User Story 4 - Performance-Based Strategy (Priority: P2)

A performance-sensitive application needs to prioritize faster proxies while still utilizing slower ones, balancing speed against proxy diversity.

**Why this priority**: Improves user experience - reduces latency while maintaining rotation for anonymity.

**Independent Test**: Can be tested by tracking proxy latencies and verifying faster proxies are selected more frequently.

**Acceptance Scenarios**:

1. **Given** proxies with different average response times, **When** requests are made, **Then** faster proxies are selected proportionally more often
2. **Given** a proxy's performance degrades, **When** performance metrics are updated, **Then** its selection frequency decreases automatically
3. **Given** performance-based selection, **When** all proxies are slow, **Then** strategy falls back to round-robin or random

---

### User Story 5 - Session Persistence Strategy (Priority: P3)

An application needs to maintain the same proxy for a series of related requests (e.g., login session) to avoid triggering security measures.

**Why this priority**: Enables stateful operations - necessary for applications requiring consistent IP addresses across request sequences.

**Independent Test**: Can be tested by creating a session and verifying all requests within that session use the same proxy.

**Acceptance Scenarios**:

1. **Given** a session is created, **When** multiple requests are made within that session, **Then** all use the same proxy
2. **Given** session expires or is closed, **When** new session starts, **Then** a different proxy may be selected
3. **Given** session proxy fails, **When** request is made, **Then** system switches to fallback proxy and maintains new proxy for session

---

### User Story 6 - Geo-Targeted Strategy (Priority: P3)

A user wants to select proxies from specific geographic regions to access geo-restricted content or appear as requests from particular locations.

**Why this priority**: Enables location-based testing and access - important for regional content and compliance testing.

**Independent Test**: Can be tested by requesting proxies from specific regions and verifying selected proxies match the criteria.

**Acceptance Scenarios**:

1. **Given** proxies tagged with country codes, **When** request specifies target country, **Then** only proxies from that country are selected
2. **Given** no proxies available for requested region, **When** request is made, **Then** error is returned or fallback to any region (configurable)
3. **Given** multiple proxies in target region, **When** request is made, **Then** secondary strategy (round-robin, random, etc.) is applied

---

### Edge Cases

- When rotation strategy is changed mid-operation with active requests, new requests MUST use new strategy immediately while in-flight requests complete using the original strategy they were assigned
- How does the system handle rotation when all proxies are currently in use by other requests?
- When a rotation strategy requires metadata (performance, geo-location) that is incomplete or missing, system MUST reject selection with clear error indicating missing data and MAY use configured fallback strategy if available
- How are rotation strategies affected by concurrent proxy pool modifications (adds/removals)?
- What happens when weighted strategies have proxies with zero or negative weights?
- How does session persistence handle extremely long-lived sessions?
- What occurs when combining multiple rotation strategies (e.g., geo-filtering + performance-based)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support round-robin rotation strategy as default
- **FR-002**: System MUST support random proxy selection strategy
- **FR-003**: System MUST support least-used proxy selection strategy
- **FR-004**: System MUST support performance-based weighted selection strategy
- **FR-005**: System MUST support session persistence strategy with configurable timeout
- **FR-006**: System MUST support geo-targeted proxy selection based on country/region
- **FR-007**: System MUST allow strategy to be specified per request or globally configured
- **FR-008**: System MUST track comprehensive request metadata per proxy including: requests started, requests completed, successful requests, failed requests, and active (in-flight) requests
- **FR-009**: System MUST track response times per proxy using Exponential Moving Average (EMA) with configurable smoothing factor (alpha) for performance-based strategy
- **FR-010**: System MUST support weighted random selection with custom weights
- **FR-011**: System MUST allow combining strategies (e.g., geo-filter + round-robin)
- **FR-012**: System MUST skip unhealthy proxies in all rotation strategies
- **FR-013**: System MUST support sticky sessions with session ID or cookie-based tracking
- **FR-014**: System MUST provide strategy selection API for programmatic control
- **FR-015**: System MUST reset proxy usage counters on pool modifications AND maintain sliding time window (configurable, default 1 hour) for counter staleness prevention
- **FR-016**: System MUST support custom rotation strategies via plugin architecture
- **FR-017**: System MUST log rotation decisions for debugging and auditing
- **FR-018**: System MUST handle concurrent rotation requests thread-safely
- **FR-019**: System MUST update performance metrics in real-time or near-real-time
- **FR-020**: System MUST support strategy hot-swapping without service restart
- **FR-021**: System MUST validate required metadata availability for strategy and reject with clear error when incomplete
- **FR-022**: System MUST support optional fallback strategy configuration when primary strategy fails due to missing metadata

### Key Entities

- **Rotation Strategy**: Algorithm for selecting next proxy (round-robin, random, least-used, performance-based, session, geo-targeted)
- **Proxy Metadata**: Information used by strategies including request counts (started, completed, successful, failed, active), average latency, success rate, geo-location, health status
- **Session**: Logical grouping of requests requiring same proxy (session ID, proxy assignment, timeout)
- **Strategy Configuration**: Settings controlling strategy behavior (weights, timeouts, fallback rules, geo-preferences, EMA alpha parameter, sliding window duration)
- **Selection Context**: Request-specific parameters influencing strategy (target region, session ID, priority level)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Round-robin strategy achieves perfect distribution (±1 request) across all proxies
- **SC-002**: Random selection produces uniform distribution within 10% variance over 1000 requests
- **SC-003**: Least-used strategy maintains request count variance under 20% across all proxies
- **SC-004**: Performance-based strategy reduces average response time by 15-25% compared to round-robin
- **SC-005**: Session persistence maintains same proxy for 99.9% of same-session requests
- **SC-006**: Geo-targeted strategy selects correct region 100% of the time when proxies are available
- **SC-007**: Strategy selection adds less than 5ms overhead per request
- **SC-008**: All strategies handle 10,000 concurrent rotation requests without deadlocks
- **SC-009**: Strategy hot-swap completes within 100ms for new requests without dropping requests; in-flight requests complete with original strategy
- **SC-010**: Custom strategy plugins can be loaded and activated within 1 second

## Assumptions

- Proxy metadata (performance, location) is kept reasonably up-to-date
- Request volume is sufficient for statistical strategies (performance-based, least-used) to be meaningful
- Session timeouts are configured appropriately for application use cases
- Geo-location data for proxies is accurate and available
- Concurrent access patterns don't create extreme lock contention
- Strategy selection logic completes faster than network I/O to proxies

## Clarifications

### Session 2025-10-29

- Q: When should request counts be tracked for least-used strategy? → A: Track comprehensive metadata including requests started, requests completed, successes, failures
- Q: What averaging method should be used for tracking response times in performance-based strategy? → A: Exponential Moving Average (EMA) with configurable alpha
- Q: What happens when rotation strategy requires metadata that is incomplete or missing? → A: Reject with clear error + fallback strategy option
- Q: How should strategy hot-swapping handle in-flight requests? → A: Continue with new strategy; in-flight requests complete with old strategy
- Q: What is the reset policy for proxy usage counters during normal operations? → A: Sliding time window (e.g., last 1 hour)

## Dependencies

- Core Python Package for proxy pool management
- Health Monitoring for proxy health status
- Metrics & Observability for performance data collection
- Configuration Management for strategy settings
- Logging System for rotation decision logging
