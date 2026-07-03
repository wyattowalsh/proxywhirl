# R-005: Bootstrap Edge Cases (`proxywhirl/rotator/_bootstrap.py`)

Preliminary read-only pass (finalized against fresh coverage data in F-012):

- Empty-sources path: bootstrap should handle `ALL_SOURCES`/candidate list being empty without raising.
- `sample_size` boundary behavior: sampling more than available sources, sampling zero, sampling exactly
  the pool size.
- Async race during concurrent bootstrap calls (two callers triggering `_fetch_bootstrap_candidates`
  concurrently) — verify no duplicate/partial state.
- Error handling when all candidate sources fail validation (pool stays empty, no unhandled exception).

See F-012 for concrete tests added against current coverage gaps.
