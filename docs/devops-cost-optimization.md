# Cost Optimization & Resource Management

## Cloud Spending Analysis

```yaml
monthly_budget: $5000
  compute: 40%    # ECS, EC2
  storage: 25%    # S3, RDS
  network: 15%    # Data transfer, load balancer
  other: 20%      # Backup, monitoring, licenses
```

## Cost Optimization Strategies

### Compute
- Use spot instances (70% savings)
- Right-size instances (avoid over-provisioning)
- Schedule scaling (stop non-prod at night)
- Reserved instances for baseline capacity

### Storage
- Use S3 Intelligent-Tiering (automatic cost optimization)
- Archive old data to Glacier (90% savings)
- Enable S3 lifecycle policies
- Compress backups (50% size reduction)

### Network
- Use VPC endpoints (avoid NAT gateway costs)
- Cache CloudFront (reduce origin requests)
- Regional data transfer only
- Consolidate cross-region traffic

## Monitoring & Alerts

```bash
# Daily cost report
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-02 \
  --granularity DAILY \
  --metrics BlendedCost
```

## Reserved Capacity Planning

- 1-year RI for baseline capacity
- 3-year RI for stable services
- On-demand for burst/test environments
