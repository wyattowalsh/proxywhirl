# Maintenance Windows & Scheduled Downtime

## Maintenance Schedule

| Maintenance Type | Frequency | Duration | Window |
|-----------------|-----------|----------|--------|
| Database patching | Quarterly | 30 min | 2 AM UTC, Sunday |
| OS updates | Monthly | 15 min | 2 AM UTC, 1st Sunday |
| Dependency updates | Weekly | 5 min | 3 AM UTC, Saturday |
| Storage expansion | Quarterly | 1 hour | 2 AM UTC, Sunday |
| Certificate renewal | Quarterly | 5 min | Automated |

## Pre-Maintenance Checklist

- [ ] Notify customers (7 days before)
- [ ] Create backup (1 day before)
- [ ] Test rollback procedure
- [ ] Brief on-call team
- [ ] Document rollback plan
- [ ] Prepare status page message

## During Maintenance

```bash
# Update status page
curl -X PATCH https://status.proxywhirl.io/incidents \
  -H "Authorization: Bearer $STATUS_PAGE_TOKEN" \
  -d '{"status": "investigating", "message": "Scheduled maintenance"}'

# Enable maintenance mode
curl -X POST http://localhost:8000/admin/maintenance \
  -d '{"enabled": true, "message": "Scheduled maintenance - back in 30 min"}'
```

## Post-Maintenance Validation

```bash
# Health checks
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:8000/api/metrics | grep up

# Smoke tests
proxywhirl test smoke --environment production

# Customer communication
curl -X PATCH https://status.proxywhirl.io/incidents \
  -d '{"status": "resolved", "message": "Maintenance completed successfully"}'
```
