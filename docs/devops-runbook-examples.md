# Runbook Examples

## Database Failover

```bash
#!/bin/bash
set -e

echo "Starting database failover..."

# Step 1: Verify primary is down
if ! curl -s http://primary-db:5432 > /dev/null; then
    echo "✓ Primary down confirmed"
else
    echo "✗ Primary still up - abort"
    exit 1
fi

# Step 2: Promote secondary
kubectl exec -it secondary-db -- pg_ctl promote -D /var/lib/postgresql/data
echo "✓ Secondary promoted to primary"

# Step 3: Update DNS
aws route53 change-resource-record-sets --hosted-zone-id $ZONE_ID \
  --change-batch "$(cat <<BATCH
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "db.proxywhirl.local",
      "Type": "A",
      "TTL": 60,
      "ResourceRecords": [{"Value": "10.0.2.10"}]
    }
  }]
}
BATCH
)"
echo "✓ DNS updated"

# Step 4: Spin up new secondary
kubectl create -f secondary-db-pod.yaml
kubectl wait --for=condition=ready pod -l role=secondary-db --timeout=300s
echo "✓ New secondary running"

# Step 5: Replication check
sleep 10
kubectl exec secondary-db -- psql -U postgres -d proxywhirl -c "SELECT * FROM pg_stat_replication;"
echo "✓ Replication verified"
```

## API Rollback

```bash
#!/bin/bash
set -e

CURRENT_VERSION=$(kubectl get deployment proxywhirl-api -o jsonpath='{.spec.template.spec.containers[0].image}' | cut -d: -f2)
echo "Current version: $CURRENT_VERSION"

# Get previous version from deployment history
PREVIOUS_VERSION=$(kubectl rollout history deployment/proxywhirl-api | head -2 | tail -1)
echo "Rolling back to: $PREVIOUS_VERSION"

# Trigger rollback
kubectl rollout undo deployment/proxywhirl-api
kubectl rollout status deployment/proxywhirl-api

# Verify
sleep 5
curl -s http://localhost:8000/health | jq .version
echo "✓ Rollback completed"
```

## Cache Flush

```bash
#!/bin/bash

echo "Flushing cache..."
redis-cli FLUSHDB
echo "✓ Redis cleared"

# Warm up cache with frequently accessed proxies
curl -X POST http://localhost:8000/admin/cache/warm \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"top_n": 1000}'
echo "✓ Cache warmed"
```

## Disk Space Emergency

```bash
#!/bin/bash

echo "Disk usage: $(df -h / | awk 'NR==2 {print $5}')"

# Step 1: Archive old logs
find /var/log/proxywhirl -name "*.log" -mtime +30 -exec gzip {} \;
find /var/log/proxywhirl -name "*.gz" -mtime +90 -delete
echo "✓ Old logs archived"

# Step 2: Prune database
sqlite3 proxywhirl.db "DELETE FROM audit_entries WHERE created_at < datetime('now', '-90 days');"
sqlite3 proxywhirl.db "VACUUM;"
echo "✓ Database pruned"

# Step 3: Clear build artifacts
docker system prune -f
echo "✓ Docker cleaned"

echo "Disk usage now: $(df -h / | awk 'NR==2 {print $5}')"
```

## Network Partition Handling

```bash
#!/bin/bash

echo "Network partition detected - switching to local-only mode"

# Disable remote API calls
curl -X POST http://localhost:8000/admin/circuit-breaker \
  -d '{"enabled": true, "type": "network"}'

# Use cached data only
curl -X POST http://localhost:8000/admin/cache \
  -d '{"mode": "offline"}'

# Monitor and wait for network recovery
while ! timeout 1 bash -c "echo >/dev/tcp/primary-api/8000" 2>/dev/null; do
    echo "Waiting for network..."
    sleep 5
done

# Resume normal operation
curl -X POST http://localhost:8000/admin/circuit-breaker \
  -d '{"enabled": false}'
echo "✓ Network restored, normal mode resumed"
```
