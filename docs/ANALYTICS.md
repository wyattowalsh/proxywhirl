# ProxyWhirl Analytics Engine

Comprehensive analytics engine for proxy performance monitoring, pattern detection, failure analysis, cost tracking, and predictive forecasting.

## Features

### ?? Performance Analysis (MVP)
- **Success Rate Tracking**: Monitor request success rates across all proxies
- **Latency Analysis**: Track p50, p95, p99 latencies with statistical summaries
- **Uptime Monitoring**: Calculate and track proxy availability percentages
- **Performance Scoring**: Multi-criteria scoring (0-100) combining success rate, latency, and uptime
- **Proxy Ranking**: Automatic ranking and percentile calculations
- **Underperformance Detection**: Identify proxies failing to meet thresholds
- **Degradation Patterns**: Detect declining performance trends over time
- **Actionable Recommendations**: Auto-generated remediation suggestions

### ?? Usage Pattern Detection
- **Peak Hour Detection**: Identify high-traffic periods using statistical analysis
- **Volume Trends**: Analyze request volume changes over time
- **Geographic Distribution**: Track regional usage patterns
- **Anomaly Detection**: Detect unusual spikes/drops using 3-sigma z-score method
- **Seasonal Patterns**: Identify recurring trends and patterns

### ?? Failure Analysis
- **Multi-Dimensional Clustering**: Group failures by proxy, domain, error type, time
- **Root Cause Analysis**: Identify probable causes through correlation
- **Failure Trends**: Track failure rates and patterns
- **Remediation Recommendations**: Targeted suggestions for addressing failures

### ?? Cost & ROI Analysis
- **Cost Per Request**: Calculate cost efficiency metrics
- **Cost Per Success**: Track costs for successful requests only
- **Source Comparison**: Compare cost-effectiveness across proxy providers
- **ROI Metrics**: Comprehensive return on investment calculations
- **Cost Forecasting**: Project future costs based on historical trends
- **Optimization Opportunities**: Identify cost-saving recommendations

### ?? Predictive Analytics
- **Request Volume Forecasting**: Predict future request volumes
- **Capacity Planning**: Forecast proxy capacity needs with buffer calculations
- **Trend Detection**: Identify increasing, decreasing, stable, or volatile trends
- **Confidence Intervals**: All predictions include uncertainty estimates
- **Model Accuracy**: Track and report prediction accuracy
- **ML Support**: Optional scikit-learn integration (graceful fallback to statistical methods)

## Installation

```bash
# Install with analytics support
pip install proxywhirl[analytics]

# Or install dependencies separately
pip install pandas>=2.0.0 numpy>=1.24.0 scikit-learn>=1.3.0
```

## Quick Start

```python
from datetime import datetime, timedelta
from proxywhirl import AnalyticsEngine, AnalysisConfig

# Initialize analytics engine
config = AnalysisConfig(
    lookback_days=30,
    min_success_rate=0.75,
    max_avg_latency_ms=5000.0,
    cache_results=True,
)

engine = AnalyticsEngine(config=config)

# Record proxy requests
engine.record_request(
    proxy_id="proxy-1",
    proxy_url="http://proxy1.example.com:8080",
    success=True,
    latency_ms=250.0,
    timestamp=datetime.now(),
    pool="production",
    region="us-east-1",
    target_domain="api.example.com",
)

# Record uptime data
engine.record_proxy_uptime(
    proxy_id="proxy-1",
    uptime_hours=95.0,
    downtime_hours=5.0,
)

# Analyze performance
report = engine.analyze_performance()

# Access results
print(f"Executive Summary: {report.executive_summary}")
print(f"Total Proxies Analyzed: {report.total_proxies_analyzed}")
print(f"Total Requests: {report.total_requests_analyzed}")

for finding in report.key_findings:
    print(f"- {finding}")

# Export results
engine.export_to_json(report, "analytics_report.json")
engine.export_to_csv(report, "metrics.csv")
```

## Advanced Usage

### Custom Query Filtering

```python
from proxywhirl import AnalyticsQuery, AnalysisType

# Filter by time range, proxies, and pools
query = AnalyticsQuery(
    start_time=datetime.now() - timedelta(days=7),
    end_time=datetime.now(),
    proxy_ids=["proxy-1", "proxy-2", "proxy-3"],
    pools=["production"],
    regions=["us-east-1", "us-west-2"],
    analysis_types=[AnalysisType.PERFORMANCE],
    include_recommendations=True,
    top_n_performers=10,
)

report = engine.analyze_performance(query)
```

### Performance Scores

```python
# Access detailed performance scores
for proxy_id, score in report.performance_scores.items():
    print(f"Proxy: {proxy_id}")
    print(f"  Overall Score: {score.overall_score:.1f}/100")
    print(f"  Success Rate Score: {score.success_rate_score:.1f}")
    print(f"  Latency Score: {score.latency_score:.1f}")
    print(f"  Uptime Score: {score.uptime_score:.1f}")
    print(f"  Rank: #{score.rank} (Percentile: {score.percentile:.1f}%)")
```

### Recommendations

```python
# Review actionable recommendations
for rec in report.recommendations:
    print(f"[{rec.priority.value.upper()}] {rec.title}")
    print(f"  {rec.description}")
    print(f"  Impact: {rec.estimated_improvement}")
    print(f"  Effort: {rec.estimated_effort}")
    print(f"  Affected Proxies: {len(rec.affected_proxies)}")
```

### Pattern Detection

```python
from proxywhirl import PatternDetector

detector = PatternDetector(config=config)

# Detect peak hours
peak_pattern = detector.detect_peak_hours(request_data)
print(f"Peak Hours: {peak_pattern.peak_hours}")
print(f"Max Requests/Hour: {peak_pattern.max_requests_per_hour}")

# Analyze geographic patterns
geo_pattern = detector.detect_geographic_patterns(request_data)
print(f"Top Regions: {geo_pattern.top_regions}")

# Detect anomalies
anomalies = detector.detect_anomalies(request_data, metric="latency")
for anomaly in anomalies:
    print(f"Anomaly: {anomaly.description}")
    print(f"  Severity: {anomaly.severity:.2f}")
    print(f"  Expected: {anomaly.expected_value:.1f}")
    print(f"  Actual: {anomaly.actual_value:.1f}")
```

### Failure Analysis

```python
from proxywhirl import FailureAnalyzer

analyzer = FailureAnalyzer(config=config)

# Detect failure clusters
clusters = analyzer.detect_failure_clusters(failure_data)

for cluster in clusters:
    print(f"Cluster: {cluster.cluster_name}")
    print(f"  Failures: {cluster.failure_count}")
    print(f"  Affected Proxies: {cluster.affected_proxies}")
    print(f"  Root Causes: {cluster.probable_root_causes}")

# Generate remediation recommendations
recommendations = analyzer.generate_remediation_recommendations(clusters)
```

### Cost Analysis

```python
from proxywhirl import CostAnalyzer

analyzer = CostAnalyzer(config=config)

# Compare source cost-effectiveness
source_data = {
    "Provider A": {"cost": 100.0, "requests": 10000, "successes": 9500},
    "Provider B": {"cost": 150.0, "requests": 15000, "successes": 14000},
}

comparison = analyzer.compare_source_cost_effectiveness(source_data)

for source, metrics in comparison.items():
    print(f"{source}:")
    print(f"  Cost/Request: ${metrics['cost_per_request']:.4f}")
    print(f"  Cost/Success: ${metrics['cost_per_successful_request']:.4f}")
    print(f"  ROI Score: {metrics['roi_score']:.2f}")

# Project future costs
historical_costs = [
    (datetime(2025, 1, 1), 100.0),
    (datetime(2025, 1, 15), 110.0),
    (datetime(2025, 2, 1), 120.0),
]

prediction = analyzer.project_future_costs(historical_costs, forecast_days=30)
print(f"Predicted Cost: ${prediction.predicted_value:.2f}")
print(f"Confidence: [{prediction.lower_bound:.2f}, {prediction.upper_bound:.2f}]")
```

### Predictive Analytics

```python
from proxywhirl import PredictiveAnalytics

predictor = PredictiveAnalytics(config=config)

# Forecast request volume
historical_volume = [
    (datetime(2025, 1, 1), 10000.0),
    (datetime(2025, 1, 2), 11000.0),
    # ... more data points
]

volume_prediction = predictor.forecast_request_volume(
    historical_volume,
    forecast_days=7,
)

print(f"Predicted Volume: {volume_prediction.predicted_value:.0f} requests")
print(f"Model Accuracy: {volume_prediction.model_accuracy:.1%}")

# Forecast capacity needs
capacity_prediction = predictor.forecast_capacity_needs(
    historical_volume,
    current_capacity=100,
    forecast_days=7,
)

print(f"Recommended Capacity: {capacity_prediction.predicted_value:.0f} proxies")

# Detect trends
trend, strength = predictor.detect_trends(historical_volume)
print(f"Trend: {trend.value} (strength: {strength:.2f})")
```

## Configuration Options

```python
from proxywhirl import AnalysisConfig

config = AnalysisConfig(
    # Time window
    lookback_days=30,
    
    # Performance thresholds
    min_success_rate=0.70,              # 70% minimum
    max_avg_latency_ms=5000.0,          # 5 seconds max
    min_uptime_percentage=95.0,         # 95% minimum
    
    # Performance scoring weights (must sum to 1.0)
    success_rate_weight=0.4,
    latency_weight=0.3,
    uptime_weight=0.3,
    
    # Pattern detection
    peak_hour_threshold=1.5,            # 1.5x average for peak
    anomaly_threshold=3.0,              # 3-sigma for anomalies
    min_pattern_confidence=0.8,         # 80% confidence minimum
    
    # Failure analysis
    min_cluster_size=5,                 # 5 failures minimum
    failure_correlation_threshold=0.6,  # 60% correlation
    
    # Predictive analytics
    prediction_horizon_days=7,
    min_training_days=14,
    prediction_confidence=0.95,
    
    # Cost analysis
    default_cost_per_proxy_per_month=10.0,
    
    # Caching
    cache_results=True,
    cache_ttl_seconds=3600,             # 1 hour
    
    # Performance limits
    max_proxies_analyzed=10000,
    max_records_per_query=1_000_000,
    
    # Export
    include_visualizations=True,
    export_formats=[ExportFormat.JSON, ExportFormat.CSV],
)
```

## Data Models

### ProxyPerformanceMetrics
Comprehensive performance metrics for a single proxy:
- Request counts (total, successful, failed)
- Success rate (0.0-1.0)
- Latency statistics (avg, min, max, p50, p95, p99)
- Uptime metrics (hours up/down, percentage)
- Error tracking (counts by error type)
- Temporal data (first seen, last seen)

### PerformanceScore
Calculated performance score (0-100):
- Overall score (weighted combination)
- Component scores (success rate, latency, uptime, reliability)
- Ranking information (rank, percentile)

### AnalysisReport
Comprehensive analysis report containing:
- Executive summary
- Key findings
- Performance metrics and scores
- Usage patterns
- Failure clusters
- Predictions
- Anomalies
- Recommendations
- Time-series data for visualization
- Export metadata

## Thread Safety

The analytics engine is fully thread-safe and supports concurrent data recording:

```python
import threading

def record_requests(proxy_id, count):
    for i in range(count):
        engine.record_request(
            proxy_id=proxy_id,
            proxy_url=f"http://{proxy_id}.example.com:8080",
            success=True,
            latency_ms=250.0,
        )

# Concurrent recording from multiple threads
threads = [
    threading.Thread(target=record_requests, args=(f"proxy-{i}", 1000))
    for i in range(10)
]

for t in threads:
    t.start()

for t in threads:
    t.join()

# All data safely recorded
print(f"Total requests: {engine.get_metrics_summary()['total_requests_all_proxies']}")
```

## Export Formats

### JSON Export
```python
engine.export_to_json(report, "report.json")
```

Exports complete report including:
- All metrics and scores
- Recommendations and findings
- Nested objects with full detail
- Timestamps in ISO format

### CSV Export
```python
engine.export_to_csv(report, "metrics.csv")
```

Exports performance metrics in tabular format:
- One row per proxy
- Columns: proxy_id, pool, region, success_rate, latency, uptime, etc.
- Easy to import into Excel or data analysis tools

## Performance Considerations

### Memory Usage
- In-memory data storage (consider external DB for large datasets)
- Incremental metric updates (avoid full recalculation)
- Configurable limits (`max_proxies_analyzed`, `max_records_per_query`)

### Analysis Speed
- Result caching (avoid redundant analysis)
- Efficient statistical computations
- Optional ML models (faster statistical fallback)
- Streaming-compatible design

### Recommendations
- For datasets >1M requests: Consider periodic aggregation
- For real-time monitoring: Enable caching with short TTL
- For historical analysis: Use time-range filtering
- For ML forecasting: Ensure sufficient training data (14+ days)

## Best Practices

### 1. Regular Data Collection
```python
# Record all proxy requests in real-time
def handle_request(proxy, response):
    engine.record_request(
        proxy_id=proxy.id,
        proxy_url=proxy.url,
        success=response.ok,
        latency_ms=response.elapsed.total_seconds() * 1000,
        timestamp=datetime.now(),
        pool=proxy.pool,
        region=proxy.region,
    )
```

### 2. Scheduled Analysis
```python
import schedule

def run_daily_analysis():
    report = engine.analyze_performance()
    engine.export_to_json(report, f"report_{datetime.now():%Y%m%d}.json")
    
    # Alert on critical recommendations
    for rec in report.recommendations:
        if rec.priority == RecommendationPriority.CRITICAL:
            send_alert(rec)

schedule.every().day.at("00:00").do(run_daily_analysis)
```

### 3. Action on Recommendations
```python
def apply_recommendations(report):
    for rec in report.recommendations:
        if rec.category == "performance":
            # Remove underperforming proxies
            for proxy_id in rec.affected_proxies:
                remove_proxy_from_pool(proxy_id)
                
        elif rec.category == "capacity_planning":
            # Scale proxy pool
            if "scale up" in rec.title.lower():
                add_proxies_to_pool(count=10)
```

### 4. Monitor Trends
```python
# Track performance over time
daily_reports = []

for day in range(30):
    report = engine.analyze_performance(
        AnalyticsQuery(
            start_time=datetime.now() - timedelta(days=day+1),
            end_time=datetime.now() - timedelta(days=day),
        )
    )
    daily_reports.append(report)

# Analyze trends
for i, report in enumerate(daily_reports):
    avg_success = statistics.mean(
        m.success_rate for m in report.performance_metrics.values()
    )
    print(f"Day {i}: {avg_success:.1%} success rate")
```

## Troubleshooting

### Issue: No recommendations generated
**Solution**: Ensure sufficient data has been collected. Recommendations require:
- At least 10 requests per proxy
- Multiple proxies for comparison
- Variance in performance metrics

### Issue: Inaccurate percentile calculations
**Solution**: The current implementation uses incremental updates for performance. For production use with strict accuracy requirements, consider:
- Storing all latency measurements
- Using t-digest or DDSketch algorithms
- Periodic recalculation from raw data

### Issue: ML forecasting not available
**Solution**: Install scikit-learn or use statistical fallback:
```bash
pip install scikit-learn>=1.3.0
```

### Issue: Out of memory with large datasets
**Solution**: 
- Use time-range filtering in queries
- Set `max_records_per_query` limit
- Implement periodic data archival
- Consider external database storage

## API Reference

### AnalyticsEngine
Main analytics engine class.

**Methods:**
- `record_request()`: Record proxy request
- `record_proxy_uptime()`: Record uptime data
- `analyze_performance()`: Run performance analysis
- `export_to_json()`: Export to JSON
- `export_to_csv()`: Export to CSV
- `get_metrics_summary()`: Get summary statistics
- `clear_data()`: Clear all data

### PerformanceAnalyzer
Performance analysis component.

**Methods:**
- `calculate_success_rate()`: Calculate success rate
- `calculate_average_latency()`: Calculate average latency
- `calculate_uptime()`: Calculate uptime percentage
- `calculate_latency_percentiles()`: Calculate p50/p95/p99
- `calculate_performance_score()`: Calculate 0-100 score
- `rank_proxies()`: Rank proxies by performance
- `identify_underperforming_proxies()`: Find underperformers
- `detect_degradation_patterns()`: Detect performance trends
- `generate_performance_recommendations()`: Generate recommendations

### PatternDetector
Usage pattern detection component.

**Methods:**
- `detect_peak_hours()`: Identify peak traffic hours
- `analyze_request_volumes()`: Analyze volume trends
- `detect_geographic_patterns()`: Analyze regional distribution
- `detect_anomalies()`: Detect statistical anomalies

### FailureAnalyzer
Failure analysis component.

**Methods:**
- `group_failures_by_proxy()`: Group by proxy
- `group_failures_by_domain()`: Group by domain
- `group_failures_by_error_type()`: Group by error
- `detect_failure_clusters()`: Detect failure clusters
- `identify_root_causes()`: Identify root causes
- `generate_remediation_recommendations()`: Generate recommendations

### CostAnalyzer
Cost and ROI analysis component.

**Methods:**
- `calculate_cost_per_request()`: Calculate cost/request
- `calculate_cost_per_successful_request()`: Calculate cost/success
- `compare_source_cost_effectiveness()`: Compare sources
- `calculate_roi_metrics()`: Calculate ROI
- `project_future_costs()`: Forecast costs
- `identify_cost_optimization_opportunities()`: Find savings

### PredictiveAnalytics
Predictive forecasting component.

**Methods:**
- `prepare_time_series_data()`: Prepare data for modeling
- `forecast_request_volume()`: Forecast request volume
- `forecast_capacity_needs()`: Forecast capacity
- `detect_trends()`: Detect trend direction
- `generate_capacity_recommendations()`: Generate capacity recommendations

## Examples

See `examples/analytics_example.py` for a comprehensive demonstration of all features.

## Contributing

Contributions welcome! Please ensure:
- Comprehensive test coverage
- Type hints throughout
- Clear documentation
- Performance considerations

## License

MIT License - see LICENSE file for details.
