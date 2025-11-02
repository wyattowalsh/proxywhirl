# Feature Specification: Interactive Example Notebooks

**Feature Branch**: `015-example-notebooks-interactive`  
**Created**: 2025-11-02  
**Status**: Draft  
**Input**: User description: "Interactive example notebooks demonstrating proxywhirl features"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Getting Started Notebook (Priority: P1)

New users can open a single "Getting Started" notebook that walks them through installing proxywhirl, creating their first proxy pool, and making a proxied request with clear explanations and runnable code cells.

**Why this priority**: First-time user experience is critical for adoption. A single, focused notebook that delivers immediate value (successful proxied request) in 5 minutes or less will drive engagement and reduce support burden.

**Independent Test**: Can be fully tested by opening the notebook, running all cells sequentially, and verifying that a user with zero prior proxywhirl experience successfully makes a proxied request and sees expected output.

**Acceptance Scenarios**:

1. **Given** a user has Python 3.9+ installed, **When** they open the "Getting Started" notebook and run all cells, **Then** they successfully install proxywhirl, create a proxy pool, and make a proxied request with visible output
2. **Given** a user runs the Getting Started notebook, **When** they reach the end, **Then** they see clear next steps directing them to other feature-specific notebooks
3. **Given** a user encounters an error in the notebook, **When** they read the cell comments, **Then** they find troubleshooting guidance for common issues

---

### User Story 2 - Feature Deep-Dive Notebooks (Priority: P2)

Users can explore individual proxywhirl features (rotation strategies, health monitoring, analytics, data export, retry logic, caching) through dedicated notebooks that demonstrate real-world usage patterns with working code examples.

**Why this priority**: After initial onboarding, users need to discover and understand specific features relevant to their use cases. Feature-specific notebooks enable self-service learning and reduce documentation maintenance.

**Independent Test**: Can be tested by opening any single feature notebook (e.g., "Rotation Strategies"), running all cells, and verifying that the notebook demonstrates the feature comprehensively without requiring other notebooks or external services.

**Acceptance Scenarios**:

1. **Given** a user wants to learn about rotation strategies, **When** they open the "Rotation Strategies" notebook, **Then** they see working examples of round-robin, weighted, random, geo-targeted, session persistence, and performance-based strategies with output
2. **Given** a user wants to understand health monitoring, **When** they run the "Health Monitoring" notebook, **Then** they see examples of configuring health checks, monitoring proxy health status, and handling circuit breakers with simulated failures
3. **Given** a user wants to explore analytics, **When** they run the "Analytics" notebook, **Then** they see examples of performance analysis, failure analysis, pattern detection, cost analysis, and predictive forecasting with sample data
4. **Given** a user wants to learn about data export, **When** they run the "Data Export" notebook, **Then** they see examples of exporting to CSV/JSON/YAML/Excel/PDF, filtering exports, and scheduling automated exports
5. **Given** a user wants to understand retry logic, **When** they run the "Retry & Failover" notebook, **Then** they see examples of configuring retry policies, circuit breakers, intelligent proxy selection during retries, and monitoring retry metrics

---

### User Story 3 - Interactive REST API Notebook (Priority: P2)

Users can interact with the proxywhirl REST API through a notebook that demonstrates starting the server, making API requests, managing proxy pools, and monitoring system status without writing any server code.

**Why this priority**: The REST API is a key integration point for production deployments. An interactive notebook demonstrating API usage lowers the barrier to API adoption and validates the API design with real examples.

**Independent Test**: Can be tested by running the API notebook, which starts a test server in-process, executes API calls, and shuts down cleanly without requiring external services or manual server management.

**Acceptance Scenarios**:

1. **Given** a user runs the REST API notebook, **When** they execute the server startup cell, **Then** the FastAPI test server starts in-process and the notebook confirms the server is ready
2. **Given** the API server is running in the notebook, **When** the user runs cells demonstrating proxy pool management, **Then** they see successful API responses for adding, listing, updating, and removing proxies
3. **Given** the API server is running, **When** the user runs cells demonstrating proxied requests, **Then** they see successful proxied request/response examples with metrics
4. **Given** the user finishes exploring the API, **When** they run the shutdown cell, **Then** the server stops gracefully and releases resources

---

### User Story 4 - Advanced Integration Patterns Notebook (Priority: P3)

Experienced users can learn advanced patterns like combining multiple features (analytics + retry logic, health monitoring + caching, session persistence + geo-targeting), custom strategy implementation, and production deployment patterns through a dedicated advanced notebook.

**Why this priority**: Power users need examples of sophisticated integration patterns to maximize proxywhirl's value in production. This notebook demonstrates best practices and prevents common anti-patterns.

**Independent Test**: Can be tested by running the advanced patterns notebook and verifying that combined feature examples work correctly, custom strategy examples are functional, and production patterns are demonstrated with clear explanations.

**Acceptance Scenarios**:

1. **Given** a user wants to implement intelligent retry with performance analytics, **When** they run the "Combined Features" section, **Then** they see working examples of retry logic using performance metrics to select optimal proxies
2. **Given** a user wants to create a custom rotation strategy, **When** they run the "Custom Strategy" section, **Then** they see a complete example of implementing and testing a custom strategy class
3. **Given** a user is deploying to production, **When** they review the "Production Patterns" section, **Then** they find examples of proper error handling, logging configuration, monitoring setup, and graceful shutdown patterns

---

### User Story 5 - Quick Reference Notebook (Priority: P3)

Users can access a quick reference notebook containing minimal code snippets for common tasks (add proxy, rotate strategies, export data, configure retries) organized by task for fast copy-paste usage without extensive explanations.

**Why this priority**: Once users understand the concepts, they need quick access to copy-paste code snippets for common tasks. A reference notebook reduces friction for routine operations.

**Independent Test**: Can be tested by randomly selecting 10 code snippets from the reference notebook, executing them in isolation, and verifying each snippet is self-contained and functional.

**Acceptance Scenarios**:

1. **Given** a user needs to quickly add a proxy with authentication, **When** they find the "Add Authenticated Proxy" snippet, **Then** the snippet is 3-5 lines of code with inline comments and runs successfully when copied
2. **Given** a user needs to switch rotation strategies, **When** they find the "Switch Strategy" snippet, **Then** the snippet demonstrates switching between two strategies with minimal code
3. **Given** a user needs to export proxy data, **When** they find export snippets, **Then** they see minimal examples for CSV, JSON, and Excel exports that work with one-line modifications

---

### Edge Cases

- What happens when a user runs notebook cells out of order (e.g., makes a request before creating a proxy pool)?
- How does the system handle notebooks when required dependencies (FastAPI, pandas, openpyxl) are not installed?
- What happens when a user tries to start the API server twice in the same notebook?
- How does the notebook behave when proxy services referenced in examples are unavailable?
- What happens when a user runs long-running cells (e.g., health monitoring) and wants to interrupt execution?
- How does the notebook handle Python version compatibility issues (3.9 vs 3.13)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a "Getting Started" notebook that successfully installs proxywhirl, creates a proxy pool, and makes a proxied request within 15 runnable cells
- **FR-002**: System MUST provide feature-specific notebooks for: rotation strategies, health monitoring, analytics, data export, retry/failover logic, caching mechanisms
- **FR-003**: System MUST provide a REST API notebook that demonstrates starting a test server, executing API calls, and shutting down the server within the notebook environment
- **FR-004**: System MUST provide an advanced patterns notebook demonstrating feature combinations, custom strategy implementation, and production deployment patterns
- **FR-005**: System MUST provide a quick reference notebook with minimal code snippets (3-5 lines) for common tasks organized by category
- **FR-006**: All notebooks MUST use mocked/test data and services (no external proxy services required) to ensure reproducible execution
- **FR-007**: All notebooks MUST include a "Table of Contents" cell with hyperlinks to major sections for easy navigation
- **FR-008**: All notebooks MUST include a "Setup/Prerequisites" section specifying required dependencies and installation commands
- **FR-009**: All notebooks MUST include clear cell comments explaining what each code block does and expected output
- **FR-010**: Notebooks MUST detect missing dependencies and provide clear error messages with installation instructions when dependencies are unavailable
- **FR-011**: Notebooks MUST use consistent formatting: markdown cells for explanations, code cells for examples, clear section headers, emoji indicators for important notes
- **FR-012**: All code examples in notebooks MUST be tested and verified to execute successfully in Python 3.9, 3.10, 3.11, 3.12, and 3.13
- **FR-013**: Notebooks MUST avoid Python 3.10+ exclusive syntax (e.g., use `Union[X, Y]` not `X | Y`, use `datetime.timezone.utc` not `datetime.UTC`)
- **FR-014**: Notebooks MUST use `uv run` prefix for all Python commands when demonstrating CLI usage to follow project conventions
- **FR-015**: Notebooks MUST include working examples that produce visible output (printed values, returned data structures, visualizations) so users can verify execution
- **FR-016**: Each feature notebook MUST be independently executable (can be run in isolation without running other notebooks first)
- **FR-017**: Notebooks MUST include error handling examples showing common failure scenarios and proper exception handling
- **FR-018**: Advanced patterns notebook MUST demonstrate thread-safe usage patterns for concurrent operations
- **FR-019**: REST API notebook MUST use FastAPI's `TestClient` to run the server in-process without requiring separate server processes
- **FR-020**: All notebooks MUST include a "What's Next" or "Further Reading" section with links to other notebooks and documentation

### Key Entities

- **Notebook**: A Jupyter notebook file containing markdown cells (explanations) and code cells (runnable examples)
- **Code Snippet**: A minimal, self-contained code example (typically 3-10 lines) demonstrating a specific task
- **Feature Section**: A group of related code examples within a notebook demonstrating a specific feature (e.g., all rotation strategies)
- **Prerequisites Section**: An initial section in each notebook listing required dependencies and setup steps
- **Output Cell**: The result displayed after executing a code cell, used to verify expected behavior

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the "Getting Started" notebook from opening to successful proxied request in under 5 minutes
- **SC-002**: 100% of code cells in all notebooks execute successfully without errors in Python 3.9-3.13 when run sequentially
- **SC-003**: Each feature notebook (rotation strategies, health monitoring, analytics, data export, retry logic) demonstrates at least 5 distinct feature examples with visible output
- **SC-004**: The REST API notebook demonstrates at least 10 different API endpoints with working request/response examples
- **SC-005**: The quick reference notebook contains at least 30 copy-paste code snippets covering common tasks
- **SC-006**: 100% of notebooks are independently executable without requiring external services or specific ordering with other notebooks
- **SC-007**: All notebooks include error handling examples and troubleshooting guidance for at least 3 common failure scenarios
- **SC-008**: Notebooks use mocked data/services ensuring reproducible execution across different environments (no network dependencies except pip/uv installs)
- **SC-009**: 90% of code snippets in the quick reference notebook are 5 lines or fewer (excluding import statements)
- **SC-010**: Advanced patterns notebook demonstrates at least 3 feature combinations, 1 custom strategy example, and 5 production patterns
