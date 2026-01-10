# Benchmark Baselines

This directory contains baseline benchmark results used for performance regression testing in CI/CD.

## Overview

The benchmark system uses `pytest-benchmark` to track performance of critical operations:
- Strategy selection (<5ms per operation)
- Cache lookups (L1 <1ms, L2/L3 <50ms)
- Proxy validation (100+ proxies/second)
- Concurrent operations (10,000 concurrent requests)

## Baseline Files

- `*/0001_baseline.json` - Initial baseline, tracked in git
- Other `*.json` files are ignored (test runs, temporary results)

## Running Benchmarks

### Run benchmarks only (no comparison)
```bash
uv run pytest tests/benchmarks/ --benchmark-only
```

### Compare against baseline
```bash
uv run pytest tests/benchmarks/ --benchmark-only --benchmark-compare=0001
```

### Compare with regression check (fail if >10% slower)
```bash
uv run pytest tests/benchmarks/ --benchmark-only --benchmark-compare=0001 --benchmark-compare-fail=min:10%
```

### Save new results
```bash
uv run pytest tests/benchmarks/ --benchmark-only --benchmark-save=my_test
```

## CI Integration

The CI workflow runs benchmarks on every PR and compares against the baseline:
- **Pass**: Performance is within 10% of baseline
- **Fail**: Any benchmark regresses by >10%

## Updating the Baseline

To update the baseline (e.g., after intentional performance improvements):

1. Run benchmarks and save new baseline:
   ```bash
   uv run pytest tests/benchmarks/ --benchmark-only --benchmark-save=baseline
   ```

2. Replace the old baseline file:
   ```bash
   mv .benchmarks/Darwin-CPython-3.13-64bit/0001_baseline.json \
      .benchmarks/Darwin-CPython-3.13-64bit/0001_baseline.json.old
   mv .benchmarks/Darwin-CPython-3.13-64bit/0002_baseline.json \
      .benchmarks/Darwin-CPython-3.13-64bit/0001_baseline.json
   ```

3. Commit the updated baseline:
   ```bash
   git add .benchmarks/**/0001_baseline.json
   git commit -m "chore: update benchmark baseline after performance improvement"
   ```

## Performance Requirements

All benchmarks enforce these requirements from the spec:

- **SC-002**: L1 cache lookups <1ms
- **SC-003**: L2/L3 cache lookups <50ms
- **SC-007**: Strategy selection <5ms
- **SC-008**: Support 10,000 concurrent requests
- **SC-009**: Eviction overhead <10ms
- **SC-011**: Proxy validation 100+ proxies/second

## Configuration

Benchmark configuration is in `pyproject.toml`:

```toml
[tool.pytest.benchmark]
min_rounds = 5
max_time = 1.0
compare = "0001"
compare_fail = "min:10%"  # Fail if >10% regression
```

## Troubleshooting

### Benchmarks fail locally but pass in CI
- Different hardware can cause variations
- Ensure no background processes are affecting performance
- Consider increasing the threshold temporarily

### Need to skip benchmarks
```bash
pytest tests/ --benchmark-skip
```

### View detailed benchmark statistics
```bash
pytest tests/benchmarks/ --benchmark-only --benchmark-verbose
```
