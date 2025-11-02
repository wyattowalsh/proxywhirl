# ProxyWhirl Analytics Engine

Comprehensive analytics capabilities for proxy performance monitoring, usage analysis, failure detection, cost tracking, and predictive forecasting.

## Overview

The ProxyWhirl Analytics Engine provides five core analysis capabilities:

1. **Performance Analysis** - Track success rates, latency, uptime, and rank proxies
2. **Usage Pattern Detection** - Identify peak hours, trends, anomalies, and geographic patterns
3. **Failure Analysis** - Detect failure clusters and identify root causes
4. **Cost & ROI Analysis** - Calculate costs, efficiency, and optimization opportunities
5. **Predictive Analytics** - Forecast future capacity needs and trends

## Quick Start

```python
from proxywhirl import AnalyticsEngine, AnalysisConfig, AnalyticsQuery, AnalysisType

# Initialize analytics engine
config = AnalysisConfig(
    lookback_days=30,
    min_success_rate=0.85,
    cache_results=True,
)

engine = AnalyticsEngine(config=config)

# Record proxy requests
engine.record_request(
    proxy_id="proxy-1",
    proxy_url="http://proxy1.example.com:8080",
    success=True,
    latency_ms=250.0,
    pool="production",
    region="us-east",
)

# Generate comprehensive analysis
query = AnalyticsQuery(
    analysis_types=[
        AnalysisType.PERFORMANCE,
        AnalysisType.USAGE_PATTERNS,
        AnalysisType.FAILURE_ANALYSIS,
    ],
    lookback_days=30,
)

report = engine.analyze(query)

print(f"Key Findings: {report.key_findings}")
print(f"Recommendations: {report.recommendations}")
```

## Performance Analysis

Analyze proxy performance and identify top/underperformers:

```python
from proxywhirl import PerformanceAnalyzer

analyzer = PerformanceAnalyzer(config=config)

# Get proxy metrics
proxy_metrics = engine.get_proxy_metrics()

# Rank proxies by performance
scores = analyzer.rank_proxies(proxy_metrics)

# Top performers
for score in scores[:3]:
    print(f"#{score.rank} {score.proxy_id}")
    print(f"  Overall Score: {score.overall_score:.3f}")
    print(f"  Success Rate: {score.success_rate_score:.1%}")

# Identify underperformers
underperformers = analyzer.identify_underperforming_proxies(proxy_metrics)

for proxy_id, issues in underperformers:
    print(f"{proxy_id}: {', '.join(issues)}")

# Statistical summary
summary = analyzer.calculate_statistical_summary(proxy_metrics)
print(f"Mean Success Rate: {summary['success_rate']['mean']:.1%}")
print(f"P95 Latency: {summary['latency_ms']['p95']:.0f}ms")
```

## Usage Pattern Detection

Detect usage patterns and anomalies:

```python
from proxywhirl import PatternDetector

detector = PatternDetector(config=config)

request_data = engine.get_request_data()

# Detect peak hours
peak_hours = detector.detect_peak_hours(request_data)
print(f"Peak hours: {peak_hours}")

# Analyze volumes and trends
volume_analysis = detector.analyze_request_volumes(request_data)
print(f"Trend: {volume_analysis['trend']}")

# Geographic patterns
geo_patterns = detector.detect_geographic_patterns(request_data, top_n=5)
for region, count in geo_patterns:
    print(f"{region}: {count} requests")

# Detect anomalies
anomalies = detector.detect_anomalies(request_data)
for anomaly in anomalies:
    print(f"{anomaly.anomaly_type}: {anomaly.metric_name}")
    print(f"  Expected: {anomaly.expected_value:.1f}")
    print(f"  Actual: {anomaly.actual_value:.1f}")
```

## Failure Analysis

Analyze failure patterns and identify root causes:

```python
from proxywhirl import FailureAnalyzer

analyzer = FailureAnalyzer(config=config)

# Get failure data
failure_data = [r for r in request_data if not r["success"]]

# Analyze failures
result = analyzer.analyze_failures(failure_data)

print(f"Total Failures: {result.total_failures}")
print(f"Clusters: {result.total_clusters}")
print(f"Effectiveness: {result.clustering_effectiveness:.1%}")

# Top failure factors
for proxy_id, count in result.top_failing_proxies[:5]:
    print(f"{proxy_id}: {count} failures")

# Analyze clusters
for cluster in result.clusters:
    print(f"\nCluster ({cluster.size} failures):")
    print(f"  Root Causes: {cluster.suspected_root_causes}")
    print(f"  Remediation: {cluster.remediation_steps}")
```

## Cost & ROI Analysis

Track costs and calculate ROI:

```python
from proxywhirl import CostAnalyzer

analyzer = CostAnalyzer(config=config)

# Calculate cost metrics
cost_metrics = analyzer.calculate_cost_metrics(
    total_cost=150.0,  # $150 for period
    request_data=request_data,
    source="proxy-provider",
)

print(f"Cost per Request: ${cost_metrics.cost_per_request:.4f}")
print(f"Cost per Success: ${cost_metrics.cost_per_successful_request:.4f}")
print(f"Efficiency Score: {cost_metrics.cost_efficiency_score:.3f}")

# Calculate ROI
roi_metrics = analyzer.calculate_roi_metrics(
    total_cost=150.0,
    request_data=request_data,
    value_per_successful_request=0.10,
)

print(f"ROI: {roi_metrics['roi_percent']:.1f}%")
print(f"Break Even: {roi_metrics['break_even']}")

# Compare sources
source_metrics = [cost_metrics]  # Add more sources
ranked = analyzer.compare_source_cost_effectiveness(source_metrics)

# Optimization opportunities
opportunities = analyzer.identify_cost_optimization_opportunities(
    ranked, current_allocation={"proxy-provider": 150.0}
)
```

## Predictive Analytics

Forecast future capacity needs:

```python
from proxywhirl import PredictiveAnalytics

predictor = PredictiveAnalytics(config=config)

# Forecast request volume
prediction = predictor.forecast_request_volume(
    historical_data=request_data,
    forecast_days=7,
)

print(f"Mean Prediction: {prediction.mean_prediction:.0f} requests")
print(f"Confidence Interval: [{prediction.confidence_interval_lower:.0f}, {prediction.confidence_interval_upper:.0f}]")
print(f"Trend: {prediction.detected_trend}")
print(f"Recommended Pool Size: {prediction.recommended_pool_size} proxies")

# Capacity recommendations
for recommendation in prediction.capacity_recommendations:
    print(f"  - {recommendation}")

# Forecast capacity needs
capacity = predictor.forecast_capacity_needs(
    historical_data=request_data,
    forecast_days=30,
)

print(f"Future Proxies Needed: {capacity['future_proxies_needed']}")
print(f"Capacity Change: {capacity['capacity_change']:+d}")
```

## REST API Integration

Analytics endpoints are available via the REST API:

### Performance Analysis

```bash
GET /api/v1/analytics/performance?lookback_days=30
```

### Usage Patterns

```bash
GET /api/v1/analytics/patterns?lookback_days=30
```

### Failure Analysis

```bash
GET /api/v1/analytics/failures?lookback_days=30
```

### Cost Analysis

```bash
GET /api/v1/analytics/costs?total_cost=150.0&lookback_days=30
```

### Predictive Analytics

```bash
GET /api/v1/analytics/predictions?forecast_days=7
```

### Comprehensive Report

```bash
GET /api/v1/analytics/reports?lookback_days=30&analysis_types=performance,usage_patterns,failure_analysis
```

## Configuration

Customize analytics behavior with `AnalysisConfig`:

```python
from proxywhirl import AnalysisConfig

config = AnalysisConfig(
    # Time range
    lookback_days=30,
    
    # Performance thresholds
    min_success_rate=0.85,
    max_latency_ms=5000,
    min_uptime_hours=24,
    
    # Pattern detection
    anomaly_std_threshold=3.0,
    peak_hour_percentile=0.90,
    
    # Clustering
    min_cluster_size=3,
    
    # Caching
    cache_results=True,
    cache_ttl_seconds=3600,
    
    # Performance
    max_records=1_000_000,
    parallel_processing=True,
)
```

## Export Reports

Export analysis reports in multiple formats:

```python
from proxywhirl.analytics_models import ExportFormat

# JSON export
engine.export_report(report, ExportFormat.JSON, "/path/to/report.json")

# CSV export
engine.export_report(report, ExportFormat.CSV, "/path/to/report.csv")
```

## Examples

See `examples/analytics_example.py` for a complete working example demonstrating all analytics features.

## Performance Considerations

- **Data Volume**: Engine handles millions of records efficiently
- **Caching**: Enable caching for frequently-run analyses
- **Parallel Processing**: Enabled by default for large datasets
- **Memory Management**: Use `clear_data()` to free memory

## Success Criteria

The analytics engine is designed to meet the following performance targets:

- **SC-001**: Analysis completes on 1M records in <30 seconds
- **SC-002**: Top/bottom 10% proxies identified with 95% accuracy
- **SC-003**: Peak hours identified within 1-hour accuracy
- **SC-004**: 90% of failures grouped into meaningful clusters
- **SC-006**: Predictive models achieve 80% accuracy for 7-day forecasts
- **SC-008**: Analysis reports generate in <10 seconds
- **SC-009**: Process 10,000 events per second for real-time analysis

## Best Practices

1. **Regular Data Recording**: Record all proxy requests for comprehensive analytics
2. **Appropriate Lookback**: Use 7-30 days for most analyses
3. **Cache Strategy**: Enable caching for dashboard/monitoring use cases
4. **Scheduled Analysis**: Run analyses periodically (hourly/daily) for trends
5. **Act on Recommendations**: Implement suggested optimizations
6. **Monitor Accuracy**: Track prediction accuracy and retrain as needed

## Troubleshooting

### Insufficient Data

Analytics requires minimum data for meaningful results:
- Performance: 10+ requests per proxy
- Patterns: 100+ requests over multiple hours
- Predictions: 30+ days of historical data

### High Memory Usage

For large datasets:
- Clear old data with `engine.clear_data(before=cutoff_time)`
- Reduce `max_records` in config
- Use time range filters in queries

### Slow Analysis

To improve performance:
- Enable `parallel_processing`
- Use shorter lookback periods
- Enable result caching
- Filter by specific proxies/pools

## Further Reading

- See `specs/009-analytics-engine-analysis/spec.md` for detailed requirements
- Check `tests/integration/test_analytics_e2e.py` for comprehensive examples
- Review `proxywhirl/analytics_models.py` for all data models
