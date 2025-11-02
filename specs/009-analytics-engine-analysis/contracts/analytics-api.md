# Analytics Engine API Contract

**Feature**: 009-analytics-engine-analysis  
**Date**: 2025-11-01  
**Format**: Python API (not REST - library-first architecture)

---

## Overview

The Analytics Engine provides a programmatic Python API for querying, exporting, and configuring analytics data. This contract defines the public interface that consumers will use to interact with the analytics system.

**Design Philosophy**: Library-first architecture per constitutional principle #1. No REST/HTTP dependencies required. All APIs return native Python types (pandas DataFrames, Pydantic models, primitives).

---

## Core API Classes

### AnalyticsEngine

**Primary interface for analytics operations.**

```python
from proxywhirl import AnalyticsEngine, ProxyRotator
from proxywhirl.analytics_models import (
    RetentionPolicy,
    ExportFormat,
    CostModel,
    TimeRange,
    QueryFilters,
    ComparisonResult,
    PerformanceMetrics,
    CostReport,
    ExportJob
)
from typing import Optional, List, Dict, Any
import pandas as pd

class AnalyticsEngine:
    """
    Analytics engine for tracking and analyzing proxy usage.
    
    Automatically collects telemetry from associated ProxyRotator
    and provides query, export, and configuration APIs.
    """
    
    def __init__(
        self,
        rotator: Optional[ProxyRotator] = None,
        db_path: str = "analytics.db",
        enable_collection: bool = True
    ):
        """
        Initialize analytics engine.
        
        Args:
            rotator: ProxyRotator instance to monitor (optional)
            db_path: Path to SQLite database for analytics storage
            enable_collection: Whether to automatically collect telemetry
        """
        ...
    
    # ==================================================================
    # Query API - Read-only access for all authenticated users
    # ==================================================================
    
    def query_usage(
        self,
        time_range: Union[str, TimeRange, tuple[int, int]],
        filters: Optional[QueryFilters] = None,
        group_by: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Query usage analytics with flexible filtering and grouping.
        
        Args:
            time_range: Time range for query. Accepts:
                - String shortcuts: "24h", "7d", "30d", "90d"
                - TimeRange object with start/end timestamps
                - Tuple of (start_timestamp, end_timestamp)
            filters: Optional filters for proxy_source_id, application_id,
                    target_domain, success status, HTTP status codes
            group_by: Optional list of dimensions to group by:
                     ["proxy_source_id", "application_id", "target_domain", "hour", "day"]
            metrics: Optional list of metrics to calculate:
                    ["request_count", "success_rate", "avg_latency", "p95_latency"]
                    If None, returns all available metrics
        
        Returns:
            DataFrame with requested dimensions and metrics
            
        Raises:
            ValueError: If time_range is invalid or query exceeds limits
            PermissionError: If user lacks read access
            
        Performance:
            - Target: <5 seconds for 30-day queries (p95)
            - Uses covering indexes and pre-calculated aggregates when possible
            - Automatically selects optimal data source (raw vs aggregated)
        
        Example:
            >>> analytics = AnalyticsEngine(rotator)
            >>> df = analytics.query_usage(
            ...     time_range="24h",
            ...     group_by=["proxy_source_id"],
            ...     metrics=["request_count", "success_rate", "avg_latency"]
            ... )
            >>> print(df)
                  proxy_source_id  request_count  success_rate  avg_latency
            0  free-proxy-list           1250          0.94         245.3
            1  premium-proxies            850          0.99         125.7
        """
        ...
    
    def compare_periods(
        self,
        period1: Union[str, TimeRange, tuple[int, int]],
        period2: Union[str, TimeRange, tuple[int, int]],
        dimensions: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None
    ) -> ComparisonResult:
        """
        Compare metrics across two time periods.
        
        Args:
            period1: First time period for comparison
            period2: Second time period for comparison
            dimensions: Dimensions to compare across (default: ["proxy_source_id"])
            metrics: Metrics to compare (default: all core metrics)
        
        Returns:
            ComparisonResult containing side-by-side metrics and percentage changes
            
        Example:
            >>> result = analytics.compare_periods(
            ...     period1="7d",
            ...     period2="14d_ago_7d",  # Previous week
            ...     dimensions=["proxy_source_id"]
            ... )
            >>> print(result.summary())
            Source              P1 Requests  P2 Requests  Change
            free-proxy-list          8500        7200     +18.1%
            premium-proxies          5400        5100      +5.9%
        """
        ...
    
    def get_source_performance(
        self,
        source_id: str,
        time_range: Union[str, TimeRange, tuple[int, int]] = "7d"
    ) -> PerformanceMetrics:
        """
        Get comprehensive performance metrics for a specific proxy source.
        
        Args:
            source_id: Proxy source identifier
            time_range: Time range for analysis
        
        Returns:
            PerformanceMetrics with success rate, latency stats, error breakdown
            
        Example:
            >>> perf = analytics.get_source_performance(
            ...     source_id="free-proxy-list",
            ...     time_range="30d"
            ... )
            >>> print(f"Success rate: {perf.success_rate:.1%}")
            >>> print(f"P95 latency: {perf.p95_latency_ms}ms")
        """
        ...
    
    def calculate_costs(
        self,
        time_range: Union[str, TimeRange, tuple[int, int]],
        cost_model: Optional[CostModel] = None,
        group_by: Optional[List[str]] = None
    ) -> CostReport:
        """
        Calculate costs based on usage and cost models.
        
        Args:
            time_range: Time range for cost calculation
            cost_model: Filter to specific cost model (if None, includes all)
            group_by: Dimensions to break down costs by (e.g., ["application_id"])
        
        Returns:
            CostReport with total spend, cost per request, cost trends
            
        Example:
            >>> costs = analytics.calculate_costs(time_range="30d")
            >>> print(f"Total spend: ${costs.total_cost:.2f}")
            >>> print(f"Cost per successful request: ${costs.cost_per_success:.4f}")
        """
        ...
    
    def get_access_log(
        self,
        time_range: Union[str, TimeRange, tuple[int, int]] = "24h",
        user_filter: Optional[str] = None,
        action_filter: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieve access audit log for compliance and security monitoring.
        
        Args:
            time_range: Time range for audit log
            user_filter: Filter to specific user_id (optional)
            action_filter: Filter to specific action type (optional)
        
        Returns:
            DataFrame with audit log entries
            
        Permissions:
            - Regular users can only see their own access logs
            - Admins can see all access logs
        """
        ...
    
    # ==================================================================
    # Export API - Read-only access for all authenticated users
    # ==================================================================
    
    def export_analytics(
        self,
        time_range: Union[str, TimeRange, tuple[int, int]],
        format: ExportFormat = ExportFormat.CSV,
        fields: Optional[List[str]] = None,
        filters: Optional[QueryFilters] = None
    ) -> ExportJob:
        """
        Create an export job for analytics data.
        
        Args:
            time_range: Time range to export
            format: Export format (CSV, JSON, EXCEL, PDF_REPORT)
            fields: List of fields to include (None = all fields)
            filters: Optional filters to apply before export
        
        Returns:
            ExportJob with job ID and status
            
        Example:
            >>> job = analytics.export_analytics(
            ...     time_range="90d",
            ...     format=ExportFormat.CSV,
            ...     fields=["timestamp", "proxy_source_id", "success", "response_time_ms"]
            ... )
            >>> print(f"Export job ID: {job.id}")
            >>> print(f"Status: {job.status}")
        """
        ...
    
    def get_export_status(self, job_id: str) -> ExportJob:
        """
        Check status of an export job.
        
        Args:
            job_id: Export job identifier
        
        Returns:
            Updated ExportJob with current status and progress
        """
        ...
    
    def download_export(
        self,
        job_id: str,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Download completed export file.
        
        Args:
            job_id: Export job identifier
            output_path: Optional path to save file (if None, returns bytes)
        
        Returns:
            Export file contents as bytes (if output_path is None)
            
        Raises:
            ValueError: If job is not completed or doesn't exist
        """
        ...
    
    # ==================================================================
    # Configuration API - Admin-only access
    # ==================================================================
    
    def set_retention_policy(
        self,
        policy: RetentionPolicy,
        user_id: str
    ) -> None:
        """
        Update retention policy configuration.
        
        Args:
            policy: New retention policy settings
            user_id: Administrator user ID for audit trail
        
        Raises:
            PermissionError: If user is not an administrator
            ValueError: If policy validation fails
        
        Permissions: Admin only
        """
        ...
    
    def get_retention_policy(self) -> RetentionPolicy:
        """
        Retrieve current retention policy.
        
        Returns:
            Current RetentionPolicy configuration
        """
        ...
    
    def set_sampling_thresholds(
        self,
        low_threshold_rpm: int = 10_000,
        high_threshold_rpm: int = 100_000,
        sample_rate: float = 0.1,
        user_id: str
    ) -> None:
        """
        Configure adaptive sampling thresholds.
        
        Args:
            low_threshold_rpm: Requests/minute for 100% capture
            high_threshold_rpm: Requests/minute for sampling mode
            sample_rate: Sampling rate at high threshold (0.0-1.0)
            user_id: Administrator user ID for audit trail
        
        Raises:
            PermissionError: If user is not an administrator
            ValueError: If thresholds are invalid
        
        Permissions: Admin only
        """
        ...
    
    def trigger_aggregation(
        self,
        time_range: Optional[Union[str, TimeRange, tuple[int, int]]] = None,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Manually trigger aggregation job for a time range.
        
        Args:
            time_range: Optional time range to aggregate (default: yesterday)
            user_id: Administrator user ID for audit trail
        
        Returns:
            Dictionary with aggregation job status and statistics
        
        Permissions: Admin only
        """
        ...
    
    def trigger_backup(self, user_id: str) -> str:
        """
        Manually trigger database backup.
        
        Args:
            user_id: Administrator user ID for audit trail
        
        Returns:
            Path to created backup file
        
        Permissions: Admin only
        """
        ...
```

---

## Supporting Type Definitions

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Union
from enum import Enum

class TimeRange(BaseModel):
    """Time range specification."""
    start: int = Field(..., description="Start timestamp (Unix UTC)")
    end: int = Field(..., description="End timestamp (Unix UTC)")

class QueryFilters(BaseModel):
    """Filters for analytics queries."""
    proxy_source_ids: Optional[List[str]] = None
    application_ids: Optional[List[str]] = None
    target_domains: Optional[List[str]] = None
    success: Optional[bool] = None
    http_status_codes: Optional[List[int]] = None
    min_response_time_ms: Optional[int] = None
    max_response_time_ms: Optional[int] = None

class PerformanceMetrics(BaseModel):
    """Performance statistics for a proxy source."""
    source_id: str
    time_range: TimeRange
    request_count: int
    success_count: int
    failure_count: int
    success_rate: float  # 0.0-1.0
    avg_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_bytes: int
    unique_domains: int
    error_breakdown: Dict[str, int]  # error_code -> count

class ComparisonResult(BaseModel):
    """Results from period-to-period comparison."""
    period1: TimeRange
    period2: TimeRange
    dimensions: List[str]
    metrics: pd.DataFrame  # Side-by-side comparison with % change columns
    
    def summary(self) -> str:
        """Generate human-readable summary."""
        ...

class CostReport(BaseModel):
    """Cost analysis report."""
    time_range: TimeRange
    total_cost: float
    currency: str
    cost_per_request: float
    cost_per_success: float
    breakdown_by_source: Dict[str, float]
    breakdown_by_application: Optional[Dict[str, float]] = None
    trends: pd.DataFrame  # Time-series of daily costs
```

---

## Usage Patterns

### Pattern 1: Basic Usage Tracking

```python
from proxywhirl import ProxyRotator, AnalyticsEngine

# Create rotator with analytics
rotator = ProxyRotator()
analytics = AnalyticsEngine(rotator, enable_collection=True)

# Use rotator normally - analytics collected automatically
response = rotator.request("https://example.com")

# Query usage patterns
usage = analytics.query_usage(
    time_range="24h",
    group_by=["proxy_source_id"],
    metrics=["request_count", "success_rate", "avg_latency"]
)
print(usage)
```

### Pattern 2: Performance Analysis

```python
# Analyze specific source performance
perf = analytics.get_source_performance(
    source_id="free-proxy-list",
    time_range="7d"
)

if perf.success_rate < 0.90:
    print(f"Warning: {perf.source_id} success rate is {perf.success_rate:.1%}")
    print(f"Error breakdown: {perf.error_breakdown}")
```

### Pattern 3: Cost Optimization

```python
# Calculate costs and identify optimization opportunities
costs = analytics.calculate_costs(time_range="30d")

print(f"Total spend: ${costs.total_cost:.2f}")
print(f"Cost per successful request: ${costs.cost_per_success:.4f}")

# Compare premium vs free proxy cost-effectiveness
comparison = analytics.compare_periods(
    period1="30d",
    period2="60d_ago_30d",
    dimensions=["proxy_source_id"]
)
print(comparison.summary())
```

### Pattern 4: Data Export for BI Tools

```python
# Export for external analysis
job = analytics.export_analytics(
    time_range="90d",
    format=ExportFormat.CSV,
    fields=["timestamp", "proxy_source_id", "success", "response_time_ms", "bytes_transferred"]
)

# Wait for completion (async in real implementation)
while job.status == ExportStatus.PROCESSING:
    job = analytics.get_export_status(job.id)
    print(f"Progress: {job.progress_percent}%")
    time.sleep(1)

# Download when ready
analytics.download_export(job.id, "analytics_export.csv")
```

### Pattern 5: Admin Configuration

```python
# Configure retention policy (admin only)
policy = RetentionPolicy(
    raw_data_retention_days=14,  # Keep raw data longer
    hourly_aggregate_retention_days=60,
    daily_aggregate_retention_days=730,  # 2 years of daily data
    backup_retention_days=30
)

analytics.set_retention_policy(policy, user_id="admin@example.com")

# Adjust sampling for higher traffic
analytics.set_sampling_thresholds(
    low_threshold_rpm=20_000,  # Higher threshold before sampling
    high_threshold_rpm=200_000,
    sample_rate=0.05,  # More aggressive sampling (5%)
    user_id="admin@example.com"
)
```

---

## Error Handling

```python
from proxywhirl.exceptions import (
    AnalyticsError,
    QueryError,
    ExportError,
    PermissionError,
    ValidationError
)

try:
    analytics.query_usage(time_range="invalid")
except ValidationError as e:
    print(f"Invalid query parameters: {e}")

try:
    analytics.set_retention_policy(policy, user_id="regular_user")
except PermissionError as e:
    print(f"Access denied: {e}")

try:
    df = analytics.query_usage(time_range="365d")  # Very large query
except QueryError as e:
    print(f"Query exceeded limits: {e}")
    # Suggestion: use export API for large date ranges
```

---

## Performance Characteristics

| Operation | Target Performance | Notes |
|-----------|-------------------|-------|
| `query_usage()` (30 days) | <5 seconds (p95) | Uses covering indexes + aggregates |
| `get_source_performance()` | <2 seconds | Pre-calculated metrics when available |
| `calculate_costs()` | <3 seconds | Joins usage with cost records |
| `export_analytics()` (create job) | <100ms | Async processing, returns immediately |
| `download_export()` | <3 minutes total | Chunked reading, streaming writes |
| Collection overhead | <5ms (p95) | Async insertion, no blocking |
| Sampling decision | <1ms | O(1) algorithm with RNG |

---

## Thread Safety

All AnalyticsEngine methods are thread-safe:
- Read operations (queries) use shared read locks
- Write operations (config changes) use exclusive write locks
- Collection happens asynchronously in background thread
- Export jobs processed in separate worker threads

```python
from concurrent.futures import ThreadPoolExecutor

analytics = AnalyticsEngine(rotator)

# Safe to query from multiple threads
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [
        executor.submit(analytics.query_usage, "24h", filters=QueryFilters(application_id=app_id))
        for app_id in application_ids
    ]
    results = [f.result() for f in futures]
```

---

**API Contract Complete**: Ready for quickstart guide generation (Phase 1, Step 3).
