# Feature Specification: Configuration Management

**Feature Branch**: `012-configuration-management-flexible`  
**Created**: 2025-11-02  
**Status**: Draft  
**Input**: User description: "Configuration management for flexible runtime settings"

## Clarifications

### Session 2025-11-02

- Q: What authorization model should be used for runtime configuration updates? → A: Role-based with admin-only write access
- Q: How should the system handle concurrent configuration update requests? → A: Last-write-wins with conflict detection and notification

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load Configuration from Multiple Sources (Priority: P1)

Developers and operators need to configure proxywhirl from multiple sources (environment variables, configuration files, command-line arguments) with clear precedence rules to support different deployment environments (development, staging, production) and enable flexible override patterns.

**Why this priority**: Configuration loading is foundational - without it, the system cannot start or adapt to different environments. This is the MVP capability that all other configuration features depend on.

**Independent Test**: Start proxywhirl with a mix of environment variables, a YAML config file, and command-line arguments, then verify that the configuration is loaded correctly with proper precedence (CLI overrides file overrides env vars).

**Acceptance Scenarios**:

1. **Given** environment variables for proxy URLs and a config file with timeout settings, **When** proxywhirl starts, **Then** both sources are loaded and merged correctly with all settings available.
2. **Given** a configuration file with proxy URLs and command-line arguments specifying a different log level, **When** proxywhirl starts, **Then** the CLI log level overrides the file setting while proxy URLs are preserved from the file.
3. **Given** conflicting settings in environment variables and config file (same proxy URL with different auth), **When** proxywhirl starts, **Then** the environment variable takes precedence following documented precedence rules.

---

### User Story 2 - Runtime Configuration Updates (Priority: P1)

Operations teams need to update configuration settings at runtime without restarting the application to enable zero-downtime configuration changes for operational parameters like timeouts, retry policies, and non-critical settings.

**Why this priority**: Runtime updates enable operational flexibility and reduce downtime. This is critical for production environments where restarts are expensive or disruptive.

**Independent Test**: While proxywhirl is running and handling requests, update a configuration setting (e.g., request timeout) and verify that new requests immediately use the updated value without application restart.

**Acceptance Scenarios**:

1. **Given** proxywhirl is running with a 5-second request timeout, **When** an operator updates the timeout to 10 seconds via API, **Then** subsequent requests use the new 10-second timeout without restarting the application.
2. **Given** a running application with specific retry settings, **When** configuration is updated to change retry count, **Then** the new retry count takes effect immediately for new operations while in-flight operations complete with old settings.
3. **Given** runtime configuration updates are enabled, **When** an invalid configuration value is provided (e.g., negative timeout), **Then** the system rejects the change and maintains the previous valid configuration with appropriate error messaging.

---

### User Story 3 - Configuration Validation and Schema Enforcement (Priority: P2)

Developers and operators need early validation of configuration files and settings against a defined schema to catch errors before deployment and receive helpful error messages for misconfiguration issues.

**Why this priority**: Validation prevents runtime failures and improves developer experience, but the system can function without it if configurations are manually verified. It's important for production readiness but not blocking for MVP.

**Independent Test**: Provide an invalid configuration file (e.g., timeout as string instead of integer, missing required field) and verify that proxywhirl detects the error during startup with a clear, actionable error message indicating the specific validation failure.

**Acceptance Scenarios**:

1. **Given** a configuration file with an invalid proxy URL format, **When** proxywhirl attempts to load the configuration, **Then** startup fails with a clear error message indicating the specific field and validation rule violated.
2. **Given** environment variables with type mismatches (e.g., timeout set to "abc"), **When** proxywhirl starts, **Then** the configuration loader detects the type error and provides a message indicating expected type and received value.
3. **Given** a configuration file with all required fields properly formatted, **When** proxywhirl validates the configuration, **Then** validation passes and startup proceeds without errors.

---

### User Story 4 - Configuration Hot Reload from Files (Priority: P2)

Operations teams need to update configuration by modifying config files and triggering a reload without restarting the application to support traditional file-based configuration workflows and enable automated configuration management tools.

**Why this priority**: Hot reload enhances operational flexibility but runtime API updates (US2) cover most use cases. File-based reload is valuable for teams using configuration management tools but not essential for initial release.

**Independent Test**: While proxywhirl is running, modify the configuration file and send a reload signal (SIGHUP or API call), then verify that the new configuration is loaded and applied without application restart.

**Acceptance Scenarios**:

1. **Given** proxywhirl is running with configuration from config.yaml, **When** an operator modifies config.yaml and sends SIGHUP signal, **Then** the application reloads configuration from the file and applies new settings without restart.
2. **Given** a configuration file is updated with invalid settings, **When** hot reload is triggered, **Then** the system validates the new configuration, rejects invalid changes, maintains current settings, and logs the validation errors.
3. **Given** configuration file contains settings that require restart (e.g., network port changes), **When** hot reload is triggered, **Then** the system identifies non-reloadable settings and notifies the operator that a restart is required.

---

### User Story 5 - Configuration Export and Backup (Priority: P3)

Administrators need to export the current active configuration (including all merged sources and computed defaults) to a file for backup, documentation, or sharing purposes to support disaster recovery and configuration auditing workflows.

**Why this priority**: Export capabilities are valuable for operations but not blocking - administrators can manually document configurations if needed. This enhances operational maturity but is not required for core functionality.

**Independent Test**: With proxywhirl running with configuration from multiple sources, export the active configuration to a file and verify that the exported file contains all merged settings and can be used to recreate the same configuration.

**Acceptance Scenarios**:

1. **Given** proxywhirl is running with settings from environment variables, config file, and CLI arguments, **When** an administrator exports the configuration, **Then** the exported file contains all active settings with values merged according to precedence rules.
2. **Given** an exported configuration file, **When** proxywhirl starts using only that file, **Then** the resulting runtime configuration matches the original merged configuration.
3. **Given** configuration includes sensitive credentials, **When** exporting configuration, **Then** sensitive values are redacted or encrypted in the export file with clear indication of which fields were protected.

---

### Edge Cases

- What happens when a configuration file is missing but environment variables are set? System should start successfully using environment variables and log a warning about the missing file.
- How does the system handle partially loaded configurations during hot reload failure? System should rollback to the previous valid configuration and log the failure details.
- What occurs when configuration sources conflict with incompatible values (e.g., overlapping IP ranges for different proxy pools)? System should apply precedence rules and log a warning about the conflict.
- How are cyclic dependencies in configuration references handled? System should detect cycles during validation and fail with a clear error message indicating the cycle.
- What happens when configuration updates are attempted during active operations? System should apply updates immediately using atomic swap (threading.Lock) to ensure thread safety; in-flight operations complete with old settings while new operations use updated settings.
- What occurs when multiple administrators attempt to update configuration simultaneously? System applies last-write-wins semantics, logs the conflict, and notifies all affected operators of the concurrent changes with timestamps and values.
- How does the system handle configuration files in different formats (YAML, JSON, TOML)? Initial release supports YAML format only (.yaml or .yml extension required); JSON and TOML support planned for future releases.
- What occurs when required configuration values are missing from all sources? System should fail to start with a clear error listing all missing required fields.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support loading configuration from environment variables with a consistent naming convention (e.g., PROXYWHIRL_* prefix).
- **FR-002**: The system MUST support loading configuration from YAML configuration files with hierarchical structure.
- **FR-003**: The system MUST support loading configuration from command-line arguments with standard flag syntax.
- **FR-004**: The system MUST apply configuration precedence in the order: command-line arguments (highest) > environment variables > configuration files > defaults (lowest).
- **FR-005**: The system MUST validate all configuration values against a defined schema during loading, failing early with descriptive error messages for invalid configurations.
- **FR-006**: The system MUST support runtime configuration updates for designated hot-reloadable settings via programmatic API, with access restricted to users with admin role.
- **FR-007**: The system MUST distinguish between hot-reloadable settings (timeouts, retry policies, log levels) and restart-required settings (network ports, storage paths, core architecture options).
- **FR-008**: The system MUST provide a configuration reload mechanism triggered by SIGHUP signal or API endpoint.
- **FR-009**: The system MUST validate new configuration before applying during hot reload, rolling back to previous configuration on validation failure.
- **FR-010**: The system MUST preserve in-flight operations when applying runtime configuration updates, with new settings affecting only subsequent operations.
- **FR-011**: The system MUST support exporting the current active configuration to a file with all merged values clearly indicated.
- **FR-012**: The system MUST redact or encrypt sensitive configuration values (credentials, API keys) in exported configurations.
- **FR-013**: The system MUST log all configuration loading operations including source, timestamp, and validation results.
- **FR-014**: The system MUST log all runtime configuration changes including user/source, user role verification, changed fields, old and new values, timestamp, and detection of concurrent conflicting updates.
- **FR-015**: The system MUST provide programmatic access to configuration values through a typed configuration object or API.
- **FR-016**: The system MUST handle concurrent configuration update requests using last-write-wins semantics, detecting conflicts and notifying affected operators when their changes are overwritten.
- **FR-017**: The system MUST support configuration defaults that are clearly documented and applied when values are not specified in any source.
- **FR-018**: The system MUST detect and report configuration conflicts when multiple sources provide incompatible values for related settings.
- **FR-019**: The system MUST support configuration file watching for automatic reload on file changes (optional, disabled by default).
- **FR-020**: The system MUST provide a configuration validation command or API endpoint that checks configuration without starting the application.
- **FR-021**: The system MUST document the complete configuration schema including all fields, types, constraints, default values, and whether settings are hot-reloadable.

### Key Entities

- **ConfigurationSource**: Represents a source of configuration (environment, file, CLI, API) with precedence level and loaded settings.
- **ProxyWhirlSettings**: Pydantic BaseSettings model that defines the structure, types, validation rules, and reloadability for all configuration settings (serves as the configuration schema).
- **ConfigurationSnapshot**: Represents a point-in-time view of all active configuration settings with merged values and source attribution.
- **ConfigurationUpdate**: Represents a runtime configuration change request including changed fields, new values, requester, and timestamp.
- **ValidationResult**: Contains validation outcome with success/failure status, specific errors, affected fields, and suggested corrections.

## Assumptions

- Configuration files will be in YAML format for initial release, with JSON and TOML support planned but not required.
- Configuration schema will be defined using Pydantic models (ProxyWhirlSettings) leveraging pydantic-settings for validation and type safety (reusing infrastructure from 001-core-python-package).
- Hot reloadable settings will be limited to operational parameters that can be changed safely during runtime (timeouts, retry counts, log levels) while structural settings (ports, file paths) require restart.
- Configuration export will use YAML format by default with clear comments indicating source and merge results.
- Sensitive values (passwords, API keys) will be identified using Pydantic's SecretStr type and automatically redacted in exports and logs (reusing patterns from 001-core-python-package).
- Configuration watching (FR-018) will use filesystem events where available (inotify on Linux, FSEvents on macOS) with polling fallback.
- Default configuration precedence follows common patterns (CLI > ENV > File > Defaults) unless explicitly overridden by user through configuration metadata.
- Configuration validation errors will prevent application startup rather than falling back to defaults to avoid silent misconfigurations in production.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can configure proxywhirl using any combination of environment variables, config files, and CLI arguments with correct precedence applied in 100% of test cases.
- **SC-002**: Configuration validation detects 100% of schema violations and type mismatches before application startup with clear, actionable error messages.
- **SC-003**: Runtime configuration updates for hot-reloadable settings take effect within 1 second without application restart or request failures.
- **SC-004**: Configuration hot reload from files completes within 2 seconds and applies new settings without disrupting active requests.
- **SC-005**: Exported configuration files accurately reflect all active settings and can be used to recreate the same configuration with 100% fidelity.
- **SC-006**: Configuration loading adds less than 500ms to application startup time for typical configurations (up to 100 settings).
- **SC-007**: Invalid configuration changes are rejected during hot reload with rollback to previous valid configuration in 100% of failure cases.
- **SC-008**: Sensitive configuration values (passwords, API keys) are never exposed in logs, error messages, or exported files in plain text (100% redaction coverage).
- **SC-009**: Post-release surveys show that 85% of users successfully configure proxywhirl for their environment on first attempt.
- **SC-010**: Configuration conflicts between sources are detected and logged with clear indication of precedence resolution in 100% of applicable cases.
