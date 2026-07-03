# R-003: L3-Under-Lock Performance Pattern

## Question

Is holding `CacheManager._lock` while performing a synchronous L3 SQLite write an acceptable pattern, or
should the lock be released before the L3 write?

## Analysis

- Production `CacheConfig` defaults enable all three tiers; L3 writes are expected to be occasional
  (cold-start warmup, TTL-expiry backfill) rather than a hot path for every `put()`.
- The property-test timeout (RV-003) is a **test-configuration** issue, not a production hot-path issue:
  the Hypothesis property specifically constructs an L1-only invariant test but the helper leaves L3
  enabled, multiplying SQLite round-trips far beyond what any real caller would do (thousands of puts in
  a tight loop with no batching).
- Releasing the lock before L3 writes would require restructuring `CacheManager.put()`'s tier-write
  ordering and introduces a window where L1/L2/L3 could observe inconsistent state — a larger, riskier
  change than fixing the test helper.

## Recommendation

**Do not change the lock hierarchy in `cache/manager.py`.** Fix the test helper instead
(`create_cache_manager_with_max_entries` should disable L3, matching its stated intent of isolating L1
max-size behavior) — see F-006. This keeps the change surface minimal and avoids introducing concurrency
risk into production cache code for a test-only performance problem.
