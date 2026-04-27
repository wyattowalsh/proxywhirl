# Debugging & Diagnostic Tools

## Built-in Diagnostic Commands

```bash
# System health
proxywhirl debug system-info

# Database diagnostics
proxywhirl debug db-stats
proxywhirl debug db-connections
proxywhirl debug db-slow-queries --limit 10

# Cache diagnostics
proxywhirl debug cache-stats
proxywhirl debug cache-keys --pattern "proxy:*"

# Network diagnostics
proxywhirl debug network-test --host example.com
proxywhirl debug dns-resolution --target proxywhirl-api.example.com

# Memory diagnostics
proxywhirl debug memory-profile --duration 60s
proxywhirl debug heap-dump --output ./heap.dump
```

## Log Analysis

```bash
# Real-time logs
journalctl -u proxywhirl -f

# Error rate
journalctl -u proxywhirl -p err --since "1 hour ago" | wc -l

# Slow queries
journalctl -u proxywhirl | grep "query_time_ms" | awk '{print $NF}' | sort -n | tail -10

# Resource usage
docker stats proxywhirl --no-stream
```

## Tracing & Profiling

```bash
# Distributed tracing (Jaeger)
JAEGER_AGENT_HOST=localhost JAEGER_AGENT_PORT=6831 proxywhirl api

# CPU profiling
python -m cProfile -o profile.pstats -m proxywhirl.cli
pstats profile.pstats

# Memory profiling
python -m memory_profiler proxywhirl/api.py
```

## Common Issues & Fixes

| Issue | Diagnostic | Fix |
|-------|-----------|-----|
| High CPU | `top`, CPU profile | Optimize hot paths, add caching |
| Memory leak | Heap dump, memory profile | Review long-lived objects |
| Slow queries | Database logs, EXPLAIN ANALYZE | Add indexes, optimize WHERE clause |
| Connection exhaustion | netstat, `lsof` | Increase pool size, close idle connections |
