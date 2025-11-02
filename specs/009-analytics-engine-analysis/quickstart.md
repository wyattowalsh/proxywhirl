# Analytics Engine Quick Start Guide

**Feature**: 009-analytics-engine-analysis  
**Date**: 2025-11-01  
**Purpose**: Working examples for all user stories

---

## Installation & Setup

```bash
# Install proxywhirl with analytics support
uv add proxywhirl pandas>=2.0.0

# Or if already installed, ensure pandas is available
uv run python -c "import pandas; print(f'pandas {pandas.__version__} installed')"
```

---

## User Story 1: Track Proxy Usage Patterns

**Goal**: Understand how proxies are being used across applications, endpoints, and time periods.

### Example 1.1: Basic Usage Tracking

```python
from proxywhirl import ProxyRotator, AnalyticsEngine

# Initialize rotator and analytics
rotator = ProxyRotator()
analytics = AnalyticsEngine(rotator, enable_collection=True)

# Use rotator normally - analytics collected automatically
for url in ["https://api.example.com/users", "https://api.example.com/posts"]:
    response = rotator.request(url)
    print(f"Status: {response.status_code}")

# Query usage for last 24 hours
usage_24h = analytics.query_usage(time_range="24h")
print(usage_24h)

# Output:
#   timestamp           proxy_source_id  success  response_time_ms  http_status_code
# 0 2025-11-01 10:30:15  free-proxy-list   True    245               200
# 1 2025-11-01 10:30:16  premium-proxies   True    125               200
# ...
```

### Example 1.2: Grouped Usage Analysis

```python
# Group by proxy source to see usage distribution
usage_by_source = analytics.query_usage(
    time_range="24h",
    group_by=["proxy_source_id"],
    metrics=["request_count", "success_rate", "avg_latency"]
)

print(usage_by_source)
# Output:
#        proxy_source_id  request_count  success_rate  avg_latency
# 0  free-proxy-list            1250          0.94         245.3
# 1  premium-proxies             850          0.99         125.7
```

### Example 1.3: Application-Specific Usage

```python
from proxywhirl.analytics_models import QueryFilters

# Track usage per application
usage_by_app = analytics.query_usage(
    time_range="7d",
    group_by=["application_id", "proxy_source_id"],
    metrics=["request_count", "success_rate"]
)

# Filter to specific application
app_usage = analytics.query_usage(
    time_range="7d",
    filters=QueryFilters(application_ids=["web-scraper-prod"])
)

print(f"Web scraper made {len(app_usage)} requests in last 7 days")
print(f"Success rate: {(app_usage['success'].sum() / len(app_usage)):.1%}")
```

### Example 1.4: Period-over-Period Comparison

```python
# Compare this week vs last week
comparison = analytics.compare_periods(
    period1="7d",  # Last 7 days
    period2=(
        int(datetime.now().timestamp()) - 14*86400,  # Start: 14 days ago
        int(datetime.now().timestamp()) - 7*86400    # End: 7 days ago
    ),
    dimensions=["proxy_source_id"]
)

print(comparison.summary())
# Output:
# Source              Period 1    Period 2    Change
# free-proxy-list       8500        7200      +18.1%
# premium-proxies       5400        5100       +5.9%
```

---

## User Story 2: Analyze Proxy Source Performance

**Goal**: Evaluate which proxy sources are most reliable and performant.

### Example 2.1: Single Source Performance

```python
# Comprehensive performance analysis for a source
perf = analytics.get_source_performance(
    source_id="free-proxy-list",
    time_range="30d"
)

print(f"Source: {perf.source_id}")
print(f"Total requests: {perf.request_count:,}")
print(f"Success rate: {perf.success_rate:.1%}")
print(f"Average latency: {perf.avg_latency_ms:.0f}ms")
print(f"Median latency: {perf.median_latency_ms:.0f}ms")
print(f"P95 latency: {perf.p95_latency_ms:.0f}ms")
print(f"P99 latency: {perf.p99_latency_ms:.0f}ms")

# Error analysis
print("\nError breakdown:")
for error_code, count in perf.error_breakdown.items():
    print(f"  {error_code}: {count} occurrences")
```

### Example 2.2: Compare All Sources

```python
# Get performance metrics for all sources
all_sources = analytics.query_usage(
    time_range="7d",
    group_by=["proxy_source_id"],
    metrics=["request_count", "success_rate", "avg_latency", "p95_latency"]
)

# Sort by success rate
all_sources_sorted = all_sources.sort_values("success_rate", ascending=False)

print("Source Performance Ranking:")
print(all_sources_sorted)

# Identify underperforming sources
underperforming = all_sources_sorted[all_sources_sorted["success_rate"] < 0.90]
if not underperforming.empty:
    print("\n⚠️  Underperforming sources (success rate < 90%):")
    print(underperforming)
```

### Example 2.3: Temporal Performance Analysis

```python
# Analyze performance by time of day
hourly_perf = analytics.query_usage(
    time_range="7d",
    group_by=["hour"],  # Group by hour of day
    metrics=["request_count", "success_rate", "avg_latency"]
)

# Identify peak hours
peak_hours = hourly_perf[hourly_perf["request_count"] > hourly_perf["request_count"].quantile(0.75)]

print("Peak usage hours:")
print(peak_hours)

# Check if performance degrades during peak hours
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(hourly_perf["hour"], hourly_perf["request_count"])
plt.title("Request Volume by Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Request Count")

plt.subplot(1, 2, 2)
plt.plot(hourly_perf["hour"], hourly_perf["avg_latency"], label="Average")
plt.plot(hourly_perf["hour"], hourly_perf["p95_latency"], label="P95")
plt.title("Latency by Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Latency (ms)")
plt.legend()
plt.tight_layout()
plt.savefig("performance_by_hour.png")
```

### Example 2.4: Failure Analysis

```python
from proxywhirl.analytics_models import QueryFilters

# Analyze only failures
failures = analytics.query_usage(
    time_range="7d",
    filters=QueryFilters(success=False),
    group_by=["proxy_source_id", "error_code"],
    metrics=["request_count"]
)

print("Failure breakdown by source and error:")
print(failures.pivot_table(
    index="proxy_source_id",
    columns="error_code",
    values="request_count",
    fill_value=0
))
```

---

## User Story 3: Generate Cost and ROI Insights

**Goal**: Understand cost-effectiveness and ROI to justify infrastructure spending.

### Example 3.1: Calculate Total Costs

```python
# Calculate costs for the last month
costs = analytics.calculate_costs(time_range="30d")

print(f"Total spend: ${costs.total_cost:.2f} {costs.currency}")
print(f"Cost per request: ${costs.cost_per_request:.4f}")
print(f"Cost per successful request: ${costs.cost_per_success:.4f}")

# Cost by source
print("\nCost breakdown by source:")
for source_id, cost in costs.breakdown_by_source.items():
    print(f"  {source_id}: ${cost:.2f}")
```

### Example 3.2: Cost Allocation by Application

```python
# Allocate costs proportionally to applications
costs_by_app = analytics.calculate_costs(
    time_range="30d",
    group_by=["application_id"]
)

print("Cost allocation by application:")
for app_id, cost in costs_by_app.breakdown_by_application.items():
    print(f"  {app_id}: ${cost:.2f}")
    
# Calculate cost per application user (if you track user counts)
user_counts = {"web-scraper-prod": 500, "api-monitor": 200}
for app_id, cost in costs_by_app.breakdown_by_application.items():
    cost_per_user = cost / user_counts.get(app_id, 1)
    print(f"  {app_id} cost per user: ${cost_per_user:.2f}")
```

### Example 3.3: ROI Analysis (Premium vs Free Proxies)

```python
# Get performance and cost for premium proxies
premium_perf = analytics.get_source_performance("premium-proxies", "30d")
premium_costs = analytics.calculate_costs(
    time_range="30d",
    filters=QueryFilters(proxy_source_ids=["premium-proxies"])
)

# Get performance and cost for free proxies
free_perf = analytics.get_source_performance("free-proxy-list", "30d")
free_costs = analytics.calculate_costs(
    time_range="30d",
    filters=QueryFilters(proxy_source_ids=["free-proxy-list"])
)

# Compare ROI
print("ROI Analysis: Premium vs Free")
print("\nPremium Proxies:")
print(f"  Success rate: {premium_perf.success_rate:.1%}")
print(f"  Avg latency: {premium_perf.avg_latency_ms:.0f}ms")
print(f"  Cost per success: ${premium_costs.cost_per_success:.4f}")

print("\nFree Proxies:")
print(f"  Success rate: {free_perf.success_rate:.1%}")
print(f"  Avg latency: {free_perf.avg_latency_ms:.0f}ms")
print(f"  Cost per success: ${free_costs.cost_per_success:.4f}")

# Calculate value ratio
if free_costs.cost_per_success > 0:
    premium_value = (premium_perf.success_rate / premium_costs.cost_per_success)
    free_value = (free_perf.success_rate / free_costs.cost_per_success)
    print(f"\nValue ratio (success rate / cost): {premium_value / free_value:.2f}x")
```

### Example 3.4: Cost Trend Analysis

```python
import matplotlib.pyplot as plt

# Get daily cost trends
costs = analytics.calculate_costs(time_range="90d")

# Plot cost trends
plt.figure(figsize=(12, 6))
plt.plot(costs.trends["date"], costs.trends["daily_cost"])
plt.title("Daily Cost Trends (90 days)")
plt.xlabel("Date")
plt.ylabel(f"Cost ({costs.currency})")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("cost_trends.png")

# Identify cost spikes
daily_avg = costs.trends["daily_cost"].mean()
spikes = costs.trends[costs.trends["daily_cost"] > daily_avg * 1.5]
if not spikes.empty:
    print(f"\n⚠️  Cost spikes detected ({len(spikes)} days):")
    print(spikes)
```

---

## User Story 4: Export Analytics for Reporting

**Goal**: Export data for integration with BI tools and compliance reporting.

### Example 4.1: CSV Export

```python
from proxywhirl.analytics_models import ExportFormat
import time

# Create export job
job = analytics.export_analytics(
    time_range="90d",
    format=ExportFormat.CSV,
    fields=["timestamp", "proxy_source_id", "success", "response_time_ms", "bytes_transferred"]
)

print(f"Export job created: {job.id}")
print(f"Status: {job.status}")

# Wait for completion
while job.status == "processing":
    job = analytics.get_export_status(job.id)
    print(f"Progress: {job.progress_percent}%")
    time.sleep(1)

# Download export
if job.status == "completed":
    analytics.download_export(job.id, "analytics_export.csv")
    print(f"Export downloaded: {job.file_size_bytes / 1024 / 1024:.2f} MB")
    print(f"Row count: {job.row_count:,}")
```

### Example 4.2: JSON Export for APIs

```python
# Export as JSON for API consumption
job = analytics.export_analytics(
    time_range="30d",
    format=ExportFormat.JSON,
    filters=QueryFilters(
        proxy_source_ids=["premium-proxies"],
        success=True
    )
)

# Poll for completion
while job.status != "completed":
    time.sleep(2)
    job = analytics.get_export_status(job.id)

# Load and process JSON
analytics.download_export(job.id, "export.json")

import json
with open("export.json", "r") as f:
    data = [json.loads(line) for line in f]  # JSONL format

print(f"Exported {len(data)} records")
```

### Example 4.3: Filtered Export for Compliance

```python
# Export specific time range with audit trail
job = analytics.export_analytics(
    time_range=(
        int(datetime(2025, 10, 1).timestamp()),
        int(datetime(2025, 10, 31).timestamp())
    ),
    format=ExportFormat.CSV,
    fields=["timestamp", "proxy_source_id", "target_domain", "success", "http_status_code"],
    filters=QueryFilters(
        application_ids=["compliance-monitor"]
    )
)

# Wait and download
while analytics.get_export_status(job.id).status != "completed":
    time.sleep(2)

analytics.download_export(job.id, "compliance_report_oct2025.csv")

# Verify export was logged
audit_log = analytics.get_access_log(time_range="1h", action_filter="export")
print("Export recorded in audit log:")
print(audit_log[audit_log["resource"] == job.id])
```

### Example 4.4: Scheduled Exports

```python
from datetime import datetime, timedelta
import schedule

def daily_export():
    """Export yesterday's analytics data."""
    yesterday = datetime.now() - timedelta(days=1)
    start = int(yesterday.replace(hour=0, minute=0, second=0).timestamp())
    end = int(yesterday.replace(hour=23, minute=59, second=59).timestamp())
    
    job = analytics.export_analytics(
        time_range=(start, end),
        format=ExportFormat.CSV
    )
    
    # Wait for completion
    while analytics.get_export_status(job.id).status != "completed":
        time.sleep(5)
    
    # Download with date in filename
    filename = f"analytics_{yesterday.strftime('%Y%m%d')}.csv"
    analytics.download_export(job.id, filename)
    print(f"Daily export complete: {filename}")

# Schedule daily at 1 AM
schedule.every().day.at("01:00").do(daily_export)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## User Story 5: Configure Analytics Retention and Aggregation

**Goal**: Control data retention and aggregation to balance storage costs with analytical needs.

### Example 5.1: View Current Retention Policy

```python
# Check current retention settings
policy = analytics.get_retention_policy()

print("Current Retention Policy:")
print(f"  Raw data: {policy.raw_data_retention_days} days")
print(f"  Hourly aggregates: {policy.hourly_aggregate_retention_days} days")
print(f"  Daily aggregates: {policy.daily_aggregate_retention_days} days")
print(f"  Backups: {policy.backup_retention_days} days")
print(f"  Auto-aggregation: {'enabled' if policy.auto_aggregation_enabled else 'disabled'}")
print(f"  Auto-backup: {'enabled' if policy.auto_backup_enabled else 'disabled'}")
```

### Example 5.2: Update Retention Policy (Admin)

```python
from proxywhirl.analytics_models import RetentionPolicy

# Create new policy with longer retention
new_policy = RetentionPolicy(
    raw_data_retention_days=14,  # Keep raw data for 2 weeks instead of 7 days
    hourly_aggregate_retention_days=60,  # 2 months instead of 30 days
    daily_aggregate_retention_days=730,  # 2 years instead of 1 year
    backup_retention_days=30,
    auto_aggregation_enabled=True,
    auto_backup_enabled=True,
    created_at=int(datetime.now().timestamp()),
    updated_at=int(datetime.now().timestamp())
)

# Apply new policy (admin only)
try:
    analytics.set_retention_policy(new_policy, user_id="admin@example.com")
    print("✅ Retention policy updated successfully")
except PermissionError as e:
    print(f"❌ Permission denied: {e}")
```

### Example 5.3: Configure Sampling Thresholds (Admin)

```python
# Adjust sampling for higher traffic scenarios
analytics.set_sampling_thresholds(
    low_threshold_rpm=20_000,  # 100% capture up to 20K req/min
    high_threshold_rpm=200_000,  # Sample mode above 200K req/min
    sample_rate=0.05,  # 5% sampling rate at high threshold
    user_id="admin@example.com"
)

print("✅ Sampling thresholds updated")
print("  100% capture: <20K req/min")
print("  Adaptive sampling: 20K-200K req/min")
print("  5% sampling: >200K req/min")
```

### Example 5.4: Manual Aggregation Trigger (Admin)

```python
# Manually trigger aggregation for a specific time range
result = analytics.trigger_aggregation(
    time_range="7d",
    user_id="admin@example.com"
)

print(f"Aggregation job status: {result['status']}")
print(f"Records processed: {result['records_processed']}")
print(f"Hourly aggregates created: {result['hourly_created']}")
print(f"Daily aggregates created: {result['daily_created']}")
print(f"Execution time: {result['execution_time_ms']}ms")
```

### Example 5.5: Manual Backup Trigger (Admin)

```python
# Trigger immediate backup
backup_path = analytics.trigger_backup(user_id="admin@example.com")

print(f"✅ Backup created: {backup_path}")

# Verify backup size
import os
backup_size_mb = os.path.getsize(backup_path) / 1024 / 1024
print(f"Backup size: {backup_size_mb:.2f} MB")
```

---

## Best Practices

### 1. Initialize Analytics Early

```python
# Initialize analytics when creating your rotator
rotator = ProxyRotator()
analytics = AnalyticsEngine(rotator, enable_collection=True)

# Analytics will automatically track all requests through this rotator
```

### 2. Use Time Range Shortcuts

```python
# Prefer shortcuts for common ranges
usage = analytics.query_usage("24h")  # Last 24 hours
usage = analytics.query_usage("7d")   # Last 7 days
usage = analytics.query_usage("30d")  # Last 30 days

# Instead of manual timestamp calculation
```

### 3. Leverage Grouping for Insights

```python
# Group by multiple dimensions for detailed analysis
multi_dim = analytics.query_usage(
    time_range="7d",
    group_by=["proxy_source_id", "application_id", "day"],
    metrics=["request_count", "success_rate"]
)

# Creates pivot-ready data for dashboards
```

### 4. Export for Large Date Ranges

```python
# For queries >30 days, prefer export API over direct query
if days > 30:
    job = analytics.export_analytics(time_range=f"{days}d", format=ExportFormat.CSV)
    # Process asynchronously
else:
    df = analytics.query_usage(time_range=f"{days}d")
    # Process immediately
```

### 5. Monitor Performance Regularly

```python
def performance_health_check():
    """Regular check of proxy source health."""
    sources = ["free-proxy-list", "premium-proxies", "backup-proxies"]
    
    for source_id in sources:
        perf = analytics.get_source_performance(source_id, "24h")
        
        if perf.success_rate < 0.85:
            print(f"⚠️  {source_id} success rate: {perf.success_rate:.1%}")
        
        if perf.p95_latency_ms > 1000:
            print(f"⚠️  {source_id} high latency: {perf.p95_latency_ms:.0f}ms")

# Run hourly
schedule.every().hour.do(performance_health_check)
```

---

## Troubleshooting

### Query Too Slow

```python
# If queries are slow, check if you're using aggregates
policy = analytics.get_retention_policy()
print(f"Aggregation enabled: {policy.auto_aggregation_enabled}")

# Manually trigger if needed
if not policy.auto_aggregation_enabled:
    analytics.trigger_aggregation(time_range="7d", user_id="admin@example.com")
```

### Export Fails

```python
# Check export job status
job = analytics.get_export_status(job_id)
if job.status == "failed":
    print(f"Export error: {job.error_message}")
    
    # Common issues:
    # - Time range too large: break into smaller chunks
    # - Disk space: check available space
    # - Permissions: verify user has export access
```

### High Storage Usage

```python
# Check current database size
import os
db_size = os.path.getsize("analytics.db") / 1024 / 1024 / 1024
print(f"Database size: {db_size:.2f} GB")

# Adjust retention if needed
if db_size > 10:  # Over 10GB
    policy = analytics.get_retention_policy()
    policy.raw_data_retention_days = 3  # More aggressive retention
    analytics.set_retention_policy(policy, user_id="admin@example.com")
```

---

**Quick Start Complete**: All 5 user stories covered with working examples.
