# ProxyWhirl Module Classification

Phase 0 audit artifact for the focused package restructuring. Classifications use the approved product boundary: keep the rotating proxy library, source fetching, validation, session cache, lightweight storage, FastAPI adapter, FastMCP adapter, and a thin CLI; remove deployment, dashboard, enterprise observability, notification, generic platform, and test-helper code from the runtime package.

## Classifications

| Module                                     | Classification | Evidence note                                                                                             |
| ------------------------------------------ | -------------- | --------------------------------------------------------------------------------------------------------- |
| `proxywhirl/__init__.py`                   | keep           | Root facade remains as a focused product export surface for rotators, models, adapters, and core helpers. |
| `proxywhirl/config.py`                     | keep           | Core configuration is needed by library, API, MCP, and CLI.                                               |
| `proxywhirl/exceptions.py`                 | keep           | Domain exceptions and URL redaction are product error contracts.                                          |
| `proxywhirl/logging_config.py`             | keep           | Small logging setup is useful without enterprise exporters.                                               |
| `proxywhirl/safe_regex.py`                 | keep           | ReDoS-safe parsing support is part of source/proxy validation safety.                                     |
| `proxywhirl/strings.py`                    | keep           | String helpers are lightweight shared utilities if still referenced after pruning.                        |
| `proxywhirl/tags.py`                       | keep           | Tag metadata is part of proxy/source filtering if still referenced after pruning.                         |
| `proxywhirl/utils.py`                      | consolidate    | Split URL parsing, redaction, model conversion, and logging into focused `utils/` modules.                |
| `proxywhirl/type_helpers.py`               | consolidate    | Keep only dependency-light typing helpers needed by the focused core.                                     |
| `proxywhirl/types.py`                      | consolidate    | Current runtime imports concrete models/cache; replace with dependency-light types or delete.             |
| `proxywhirl/models.py`                     | keep           | Flat canonical domain model export surface.                                                               |
| `proxywhirl/rotator/__init__.py`           | keep           | Public rotator package remains.                                                                           |
| `proxywhirl/rotator/_bootstrap.py`         | consolidate    | Lazy source bootstrap is product behavior but should stay lightweight.                                    |
| `proxywhirl/rotator/async_.py`             | keep           | Async drop-in library surface is core product.                                                            |
| `proxywhirl/rotator/base.py`               | keep           | Shared rotator mechanics remain core product.                                                             |
| `proxywhirl/rotator/client_pool.py`        | consolidate    | HTTP client pooling can remain only if directly used by rotators/request flow.                            |
| `proxywhirl/rotator/sync.py`               | keep           | Sync drop-in library surface is core product.                                                             |
| `proxywhirl/_proxy_views.py`               | keep           | Flat internal helpers for credential-safe adapter views; avoids a taxonomy-only service layer.            |
| `proxywhirl/fetchers.py`                   | consolidate    | Contains parsers, validator, and fetcher logic that belongs under `sources/`.                             |
| `proxywhirl/sources.py`                    | consolidate    | Built-in source registry should move to canonical `sources/registry.py` and `sources/free.py`.            |
| `proxywhirl/premium_sources.py`            | consolidate    | Keep only source definitions that support the focused source registry.                                    |
| `proxywhirl/source_auto_discovery.py`      | consolidate    | Discovery is useful only as optional source acquisition support.                                          |
| `proxywhirl/source_custom_parser.py`       | consolidate    | Parser extension pieces belong under focused source parsing.                                              |
| `proxywhirl/source_discovery.py`           | consolidate    | Discovery pieces belong under focused source acquisition.                                                 |
| `proxywhirl/source_priority.py`            | consolidate    | Source ordering belongs in the canonical source registry if retained.                                     |
| `proxywhirl/source_priority_weighted.py`   | consolidate    | Weighted source ordering belongs in source registry if retained.                                          |
| `proxywhirl/datasource.py`                 | consolidate    | Data-source abstractions overlap with proxy source fetching.                                              |
| `proxywhirl/datasource_poller.py`          | consolidate    | Keep only polling pieces that support fetching sources.                                                   |
| `proxywhirl/browser.py`                    | consolidate    | JS-rendered fetching remains optional source acquisition support.                                         |
| `proxywhirl/validators.py`                 | consolidate    | Validation helpers belong with source/proxy validation.                                                   |
| `proxywhirl/validation_performance.py`     | consolidate    | Keep only validator concurrency/performance behavior needed by product flow.                              |
| `proxywhirl/response_validation.py`        | consolidate    | Response validation belongs in proxied request logic if retained.                                         |
| `proxywhirl/proxy_filtering.py`            | consolidate    | Proxy filtering is product behavior but should stay close to source or adapter helpers.                   |
| `proxywhirl/proxy_priority.py`             | consolidate    | Proxy priority overlaps with strategy selection.                                                          |
| `proxywhirl/proxy_reputation.py`           | consolidate    | Reputation can survive only as selection metadata used by practical strategies.                           |
| `proxywhirl/proxy_chain.py`                | consolidate    | Keep only if chain support remains a core model/use case.                                                 |
| `proxywhirl/proxy_chain_validator.py`      | consolidate    | Chain validation is retained only if chain support survives.                                              |
| `proxywhirl/proxy_headers.py`              | consolidate    | Header helpers belong in request-building logic.                                                          |
| `proxywhirl/request_builder.py`            | consolidate    | Proxied request assembly belongs in rotator/API request flow.                                             |
| `proxywhirl/custom_headers.py`             | consolidate    | Custom header support belongs in request-building logic.                                                  |
| `proxywhirl/http2_support.py`              | consolidate    | Keep only if request flow tests prove it remains useful.                                                  |
| `proxywhirl/socks_upstream.py`             | consolidate    | SOCKS support is product-adjacent but should be integrated with request flow.                             |
| `proxywhirl/socks_upstream_proxy.py`       | consolidate    | SOCKS proxy server pieces survive only if needed by core request flow.                                    |
| `proxywhirl/tunnel_http_connect.py`        | consolidate    | Tunneling survives only if directly used by proxy request support.                                        |
| `proxywhirl/tunnel_multiplexer.py`         | consolidate    | Tunneling survives only if directly used by proxy request support.                                        |
| `proxywhirl/connection_pooling.py`         | consolidate    | Connection pooling should be a small rotator/request concern if retained.                                 |
| `proxywhirl/middleware.py`                 | consolidate    | Keep only lightweight adapter middleware if still needed.                                                 |
| `proxywhirl/middleware_pipeline.py`        | consolidate    | Generic middleware pipeline likely shrinks into adapter boundaries.                                       |
| `proxywhirl/fallback_chains.py`            | consolidate    | Fallback behavior belongs in rotator/resilience strategy code.                                            |
| `proxywhirl/error_recovery.py`             | consolidate    | Recovery behavior overlaps retry/circuit-breaker and should be reduced.                                   |
| `proxywhirl/timeout_adaptive.py`           | consolidate    | Adaptive timeout survives only if used by validation/request flow.                                        |
| `proxywhirl/request_deduplication.py`      | consolidate    | Deduplication survives only if rotator or adapter request tests justify it.                               |
| `proxywhirl/request_rate_limiting.py`      | consolidate    | Rate limiting should fold into the flat `proxywhirl/rate_limiting.py` surface if retained.                |
| `proxywhirl/request_queue.py`              | consolidate    | Queueing survives only if rotator flow requires backpressure.                                             |
| `proxywhirl/retry.py`                      | keep           | Flat retry policy, executor, and metrics module for practical resilience behavior.                        |
| `proxywhirl/retry_budget.py`               | consolidate    | Budgeting survives only if folded into simple retry policy.                                               |
| `proxywhirl/resilience.py`                 | consolidate    | Legacy top-level resilience should reduce into flat retry, circuit breaker, and rate limiting modules.    |
| `proxywhirl/circuit_breaker.py`            | keep           | Flat sync/async circuit breaker state machine module.                                                     |
| `proxywhirl/rate_limiting.py`              | keep           | Flat rate-limit models and limiter wrappers.                                                              |
| `proxywhirl/cache/__init__.py`             | keep           | Cache package remains session-cache product surface.                                                      |
| `proxywhirl/cache/manager.py`              | keep           | Cache manager is product behavior.                                                                        |
| `proxywhirl/cache/models.py`               | keep           | Cache entry/config/stats are output contracts.                                                            |
| `proxywhirl/cache/crypto.py`               | consolidate    | Keep only credential-at-rest protection used by file/SQLite cache.                                        |
| `proxywhirl/cache/tiers.py`                | consolidate    | Multi-tier cache should reduce to useful session cache/storage tiers.                                     |
| `proxywhirl/cache/distributed.py`          | delete         | Distributed cache is enterprise platform scope outside session cache.                                     |
| `proxywhirl/cache_optimization.py`         | consolidate    | Keep only simple cache hit/miss/TTL improvements.                                                         |
| `proxywhirl/cache_prewarmer.py`            | consolidate    | Prewarming survives only if source fetch flow needs it.                                                   |
| `proxywhirl/lru_cache_optimization.py`     | consolidate    | LRU behavior belongs inside focused cache manager.                                                        |
| `proxywhirl/response_caching.py`           | consolidate    | Response cache pieces survive only if request flow tests require them.                                    |
| `proxywhirl/storage.py`                    | consolidate    | Split file and SQLite storage only.                                                                       |
| `proxywhirl/data_persistence.py`           | consolidate    | Persistence overlaps with storage and should be folded into focused storage.                              |
| `proxywhirl/storage_dual_write.py`         | delete         | Dual-write persistence is heavy DB ops outside session cache needs.                                       |
| `proxywhirl/storage_s3.py`                 | delete         | S3 storage is heavy persistence outside product boundary.                                                 |
| `proxywhirl/storage_s3_backend.py`         | delete         | S3 backend is heavy persistence outside product boundary.                                                 |
| `proxywhirl/storage_tags_metadata.py`      | consolidate    | Keep only tag metadata that belongs in focused storage.                                                   |
| `proxywhirl/db_backup.py`                  | delete         | Database backup ops are platform scope.                                                                   |
| `proxywhirl/db_monitoring.py`              | delete         | Database monitoring ops are platform scope.                                                               |
| `proxywhirl/migrations.py`                 | consolidate    | Keep only lightweight SQLite schema setup needed by storage.                                              |
| `proxywhirl/migrations_audit.py`           | delete         | Migration audit/docs are platform scope.                                                                  |
| `proxywhirl/migration_docs.py`             | delete         | Migration docs generator is platform scope.                                                               |
| `proxywhirl/sql_migrations_reversible.py`  | delete         | Reversible migration framework is beyond lightweight storage.                                             |
| `proxywhirl/strategies.py`                 | keep           | Flat canonical strategy selection surface.                                                                |
| `proxywhirl/strategies/__init__.py`        | delete         | Superseded by flat `proxywhirl/strategies.py`.                                                            |
| `proxywhirl/strategies/core.py`            | delete         | Superseded by flat `proxywhirl/strategies.py`.                                                            |
| `proxywhirl/health_check.py`               | consolidate    | Simple health/status survives in validator/API/MCP flow.                                                  |
| `proxywhirl/health_checks_adaptive.py`     | consolidate    | Adaptive checks survive only if folded into validator or health adapter helpers.                          |
| `proxywhirl/health_checks_custom.py`       | consolidate    | Custom checks survive only as validation extension points.                                                |
| `proxywhirl/health_weighted.py`            | consolidate    | Health weighting overlaps with performance/weighted strategies.                                           |
| `proxywhirl/geo.py`                        | consolidate    | Geo enrichment survives only if source metadata supports it.                                              |
| `proxywhirl/geo_spatial_index.py`          | consolidate    | Geo index survives only if geo strategy remains product-critical.                                         |
| `proxywhirl/geolocation_accuracy.py`       | consolidate    | Geo accuracy survives only if geo metadata remains.                                                       |
| `proxywhirl/geolocation_enrichment.py`     | consolidate    | Geo enrichment survives only if source metadata remains.                                                  |
| `proxywhirl/zone_datacenter_aware.py`      | consolidate    | Datacenter awareness survives only if metadata feeds practical strategies.                                |
| `proxywhirl/enrichment.py`                 | consolidate    | Proxy enrichment survives only as source/validator metadata.                                              |
| `proxywhirl/diversity_metrics.py`          | consolidate    | Diversity metrics survive only if used by selection strategy.                                             |
| `proxywhirl/pool_optimizer.py`             | consolidate    | Pool optimization belongs in strategy or adapter helpers if retained.                                     |
| `proxywhirl/pool_snapshot.py`              | consolidate    | Snapshot output may become an adapter/debug output if still needed.                                       |
| `proxywhirl/pool_templates.py`             | consolidate    | Templates survive only if CLI/API source/pool creation needs them.                                        |
| `proxywhirl/predictive_selector.py`        | delete         | Predictive selection is advanced/non-core compared with practical strategies.                             |
| `proxywhirl/session_affinity.py`           | consolidate    | Session stickiness belongs in session strategy/cache.                                                     |
| `proxywhirl/session_pooling.py`            | consolidate    | Session pooling belongs in session strategy/cache behavior if retained.                                   |
| `proxywhirl/search.py`                     | consolidate    | Search survives only as small proxy/source lookup behavior.                                               |
| `proxywhirl/search_proxy_index.py`         | consolidate    | Indexing survives only if needed for pool lookup performance.                                             |
| `proxywhirl/clustering.py`                 | delete         | Clustering is analytics/bloat outside core rotation.                                                      |
| `proxywhirl/compression.py`                | delete         | Generic compression is not core proxy rotation.                                                           |
| `proxywhirl/formatters.py`                 | consolidate    | Keep only CLI/API rendering/formatting helpers.                                                           |
| `proxywhirl/export_formats.py`             | consolidate    | Export formats survive only for simple CLI/API data export.                                               |
| `proxywhirl/exports.py`                    | consolidate    | Export utilities survive only if simple data export remains product behavior.                             |
| `proxywhirl/data_export.py`                | consolidate    | Data export survives only as simple product output, not platform reporting.                               |
| `proxywhirl/query_builder.py`              | delete         | Generic query builder is storage/DB bloat outside focused storage.                                        |
| `proxywhirl/query_optimization.py`         | delete         | Query optimization is DB platform scope.                                                                  |
| `proxywhirl/locale_support.py`             | delete         | Localization is outside rotating proxy product core.                                                      |
| `proxywhirl/security.py`                   | consolidate    | Keep credential redaction and minimal API-key auth only.                                                  |
| `proxywhirl/auth/__init__.py`              | consolidate    | Auth package should shrink to simple API-key support if used.                                             |
| `proxywhirl/auth/api_key.py`               | consolidate    | API-key auth is needed by API/MCP write operations.                                                       |
| `proxywhirl/auth/rate_limiter.py`          | consolidate    | Auth rate limiting should fold into focused API/MCP security if needed.                                   |
| `proxywhirl/auth/signing.py`               | delete         | Request signing is broad platform security outside scope.                                                 |
| `proxywhirl/credentials_manager.py`        | consolidate    | Credential handling survives only for safe proxy credentials/redaction.                                   |
| `proxywhirl/permissions.py`                | delete         | Permission workflow is broad platform security outside scope.                                             |
| `proxywhirl/request_signing.py`            | delete         | Request signing is broad platform security outside scope.                                                 |
| `proxywhirl/user_consent_privacy.py`       | delete         | Consent workflow is platform/privacy bloat outside proxy rotation.                                        |
| `proxywhirl/api/__init__.py`               | API-adapter    | FastAPI remains a first-class adapter.                                                                    |
| `proxywhirl/api/auth.py`                   | API-adapter    | Simple API-key auth remains for write operations.                                                         |
| `proxywhirl/api/core.py`                   | API-adapter    | Current app core has route cycle and should become app factory/state/dependencies.                        |
| `proxywhirl/api/middleware/auth.py`        | API-adapter    | Keep only if minimal API auth middleware survives.                                                        |
| `proxywhirl/api/models.py`                 | API-adapter    | API response/request schemas are output contracts.                                                        |
| `proxywhirl/api/routes/__init__.py`        | API-adapter    | Route package remains with focused routers.                                                               |
| `proxywhirl/api/routes/health.py`          | API-adapter    | Health endpoint is part of adapter contract.                                                              |
| `proxywhirl/api/routes/pools.py`           | API-adapter    | Pool routes should collapse into focused proxies/cache/source routes.                                     |
| `proxywhirl/api/routes/proxies.py`         | API-adapter    | Proxy routes remain but use adapter helpers instead of a taxonomy-only service layer.                     |
| `proxywhirl/api/streaming.py`              | API-adapter    | Streaming survives only if focused proxy listing/export needs it.                                         |
| `proxywhirl/swagger_ui.py`                 | API-adapter    | Custom docs UI survives only if current FastAPI docs need it.                                             |
| `proxywhirl/mcp/__init__.py`               | MCP-adapter    | FastMCP package remains a first-class adapter.                                                            |
| `proxywhirl/mcp/auth.py`                   | MCP-adapter    | MCP API-key auth remains but should keep keys out of tool schemas.                                        |
| `proxywhirl/mcp/server.py`                 | MCP-adapter    | Current server must be rewritten to FastMCP v3 curated tools/resources/prompts.                           |
| `proxywhirl/cli.py`                        | consolidate    | CLI remains, but monolith should become a thin adapter over core helpers.                                 |
| `proxywhirl/cli_batch.py`                  | consolidate    | Batch helpers survive only if CLI still needs them.                                                       |
| `proxywhirl/cli_config_templates.py`       | consolidate    | Config template pieces survive only in thin CLI rendering.                                                |
| `proxywhirl/cli_history.py`                | delete         | CLI history is UI convenience outside core product path.                                                  |
| `proxywhirl/blue_green_deployment.py`      | delete         | Deployment generator outside product boundary.                                                            |
| `proxywhirl/canary_deployment.py`          | delete         | Deployment generator outside product boundary.                                                            |
| `proxywhirl/docker_compose_config.py`      | delete         | Deployment generator outside product boundary.                                                            |
| `proxywhirl/helm_chart.py`                 | delete         | Deployment generator outside product boundary.                                                            |
| `proxywhirl/k8s_manifests.py`              | delete         | Deployment generator outside product boundary.                                                            |
| `proxywhirl/rollout.py`                    | delete         | Deployment rollout code outside product boundary.                                                         |
| `proxywhirl/rollout_gradual.py`            | delete         | Deployment rollout code outside product boundary.                                                         |
| `proxywhirl/workflow_approval.py`          | delete         | Workflow approval code outside product boundary.                                                          |
| `proxywhirl/feature_flags.py`              | delete         | Feature-flag platform code outside product boundary.                                                      |
| `proxywhirl/tui.py`                        | delete         | TUI is explicitly outside product boundary once CLI/API/MCP remain.                                       |
| `proxywhirl/tui_async_queue.py`            | delete         | TUI support code is outside product boundary.                                                             |
| `proxywhirl/web_dashboard.py`              | delete         | Dashboard UI outside product boundary.                                                                    |
| `proxywhirl/observability_dashboard.py`    | delete         | Dashboard UI outside product boundary.                                                                    |
| `proxywhirl/advanced_logging.py`           | delete         | Enterprise logging outside simple logging needs.                                                          |
| `proxywhirl/audit_trail.py`                | delete         | Audit trail platform feature outside product boundary.                                                    |
| `proxywhirl/jaeger_tracing.py`             | delete         | Enterprise tracing exporter outside product boundary.                                                     |
| `proxywhirl/latency_monitoring.py`         | delete         | Enterprise monitoring outside simple health/stats.                                                        |
| `proxywhirl/log_aggregator.py`             | delete         | Enterprise logging aggregation outside product boundary.                                                  |
| `proxywhirl/memory_profiling.py`           | delete         | Profiling infrastructure outside runtime product.                                                         |
| `proxywhirl/metrics_collector.py`          | consolidate    | Keep only simple health/status stats if used by API/MCP.                                                  |
| `proxywhirl/metrics_otel.py`               | delete         | OTel exporter outside product boundary.                                                                   |
| `proxywhirl/monitoring_integration.py`     | delete         | Enterprise monitoring integration outside product boundary.                                               |
| `proxywhirl/observability.py`              | delete         | Broad observability platform outside simple health/stats.                                                 |
| `proxywhirl/performance_profiler.py`       | delete         | Profiling infrastructure outside runtime product.                                                         |
| `proxywhirl/prometheus_export.py`          | delete         | Prometheus exporter outside product boundary.                                                             |
| `proxywhirl/sampling_telemetry.py`         | delete         | Enterprise telemetry sampling outside product boundary.                                                   |
| `proxywhirl/service_metrics.py`            | delete         | Enterprise service metrics outside product boundary.                                                      |
| `proxywhirl/statistics_reporter.py`        | delete         | Reporting infrastructure outside product boundary.                                                        |
| `proxywhirl/stats_aggregation.py`          | delete         | Aggregation/reporting infrastructure outside product boundary.                                            |
| `proxywhirl/stats_badges.py`               | delete         | Badge/report generation outside product boundary.                                                         |
| `proxywhirl/structured_logging.py`         | delete         | Enterprise logging outside simple logging needs.                                                          |
| `proxywhirl/tracing_request_flow.py`       | delete         | Tracing exporter/instrumentation outside product boundary.                                                |
| `proxywhirl/datasource_webhooks.py`        | delete         | Webhook side channel outside product boundary.                                                            |
| `proxywhirl/notification_alerts.py`        | delete         | Notification side channel outside product boundary.                                                       |
| `proxywhirl/notifications.py`              | delete         | Notification side channel outside product boundary.                                                       |
| `proxywhirl/telegram_notifications.py`     | delete         | Notification side channel outside product boundary.                                                       |
| `proxywhirl/webhook_retry_logic.py`        | delete         | Webhook side channel outside product boundary.                                                            |
| `proxywhirl/webhook_signature_rotation.py` | delete         | Webhook side channel outside product boundary.                                                            |
| `proxywhirl/webhooks.py`                   | delete         | Webhook side channel outside product boundary.                                                            |
| `proxywhirl/deadletter.py`                 | delete         | Generic queue infrastructure outside product boundary.                                                    |
| `proxywhirl/deadletter_queue.py`           | delete         | Generic queue infrastructure outside product boundary.                                                    |
| `proxywhirl/queue_management.py`           | delete         | Generic queue infrastructure outside product boundary.                                                    |
| `proxywhirl/quota.py`                      | delete         | Quota platform feature outside product boundary.                                                          |
| `proxywhirl/quota_management.py`           | delete         | Quota platform feature outside product boundary.                                                          |
| `proxywhirl/resource_limits.py`            | delete         | Generic resource manager outside product boundary.                                                        |
| `proxywhirl/resource_management.py`        | delete         | Generic resource manager outside product boundary.                                                        |
| `proxywhirl/task_scheduling.py`            | delete         | Generic scheduler outside product boundary.                                                               |
| `proxywhirl/graceful_shutdown.py`          | delete         | Generic runtime lifecycle code outside focused adapters unless small pieces are extracted.                |
| `proxywhirl/events/__init__.py`            | delete         | Generic events package has no approved core product role.                                                 |
| `proxywhirl/plugins.py`                    | delete         | Conflicts with `proxywhirl/plugins/` and plugin system is outside core product.                           |
| `proxywhirl/plugins/__init__.py`           | delete         | Plugin package conflicts with `plugins.py` and is outside core product.                                   |
| `proxywhirl/deprecation.py`                | delete         | Compatibility/deprecation layer conflicts with breaking cleanup decision.                                 |
| `proxywhirl/upgrade_guidance.py`           | delete         | Migration guidance runtime module conflicts with no-compat cleanup.                                       |
| `proxywhirl/regression_testing.py`         | delete         | Runtime test-helper framework is outside the focused package surface.                                     |
| `proxywhirl/test_flake_isolation.py`       | delete         | Runtime test-helper module is outside the focused package surface.                                        |
| `proxywhirl/test_parametrization.py`       | delete         | Runtime test-helper module is outside the focused package surface.                                        |
| `proxywhirl/threading_pools.py`            | consolidate    | Keep only if rotator or adapter code still needs thread-pool execution.                                   |
| `proxywhirl/http_proxy_server.py`          | delete         | Built-in proxy server is a separate server product outside rotation library/API/MCP.                      |

## Follow-Up Checks

This classification intentionally marks some modules as `consolidate` rather than immediate deletion because useful code must be extracted first. A module can move from `consolidate` to `delete` after focused tests prove the behavior is duplicated or non-core.
