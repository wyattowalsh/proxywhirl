# Incident Response Procedures

## Alert Severity Levels

| Level | Response Time | Example |
|-------|---------------|---------|
| Critical | < 5 min | Service down, data loss |
| High | < 15 min | High error rate, severe latency |
| Medium | < 1 hour | Elevated CPU, memory pressure |
| Low | < 4 hours | Informational alerts |

## Response Workflow

1. **Alert triggered** → Slack/PagerDuty notification
2. **Triage** → Assess severity and scope
3. **Mitigation** → Apply temporary fix or rollback
4. **Root cause analysis** → Post-mortem investigation
5. **Prevention** → Implement preventive controls

## Runbooks

### Service Degradation
```bash
# Check service health
curl -s http://localhost:8000/health | jq
# Check logs
journalctl -u proxywhirl -n 100 -f
# Rollback if needed
proxywhirl deploy rollback --version previous
```

### Database Issues
```bash
# Check connection pool
proxywhirl db status
# Perform backup
proxywhirl db backup --destination s3://backups/
# Run recovery
proxywhirl db recover --from-backup latest
```

### Memory Leak
```bash
# Check memory usage
docker stats proxywhirl
# Capture heap dump
proxywhirl debug heap-dump --output /tmp/heap.dump
# Analyze and restart
docker restart proxywhirl
```

## Post-Incident Review

- Document timeline of events
- Identify contributing factors
- Assign action items
- Review in team meeting within 24h
- Close action items within 1 week
