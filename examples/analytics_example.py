"""
Analytics Engine Example

Demonstrates how to use ProxyWhirl's analytics capabilities:
- Performance analysis
- Usage pattern detection
- Failure analysis
- Cost/ROI tracking
- Predictive forecasting
"""

from datetime import datetime, timedelta
import random

from proxywhirl import (
    AnalyticsEngine,
    AnalysisConfig,
    AnalysisType,
    AnalyticsQuery,
    PerformanceAnalyzer,
    PatternDetector,
    FailureAnalyzer,
    CostAnalyzer,
    PredictiveAnalytics,
)


def generate_sample_data(days: int = 7) -> list[dict]:
    """Generate sample proxy request data for demonstration."""
    print(f"Generating {days} days of sample data...")
    
    data = []
    proxies = [
        ("proxy-1", "http://proxy1.example.com:8080", "us-east", "pool-1"),
        ("proxy-2", "http://proxy2.example.com:8080", "eu-west", "pool-1"),
        ("proxy-3", "http://proxy3.example.com:8080", "us-west", "pool-2"),
        ("proxy-4", "http://proxy4.example.com:8080", "asia", "pool-2"),
        ("proxy-5", "http://proxy5.example.com:8080", "us-east", "pool-1"),  # Underperformer
    ]
    
    domains = ["api.example.com", "data.example.com", "service.example.com"]
    
    start_time = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        # Simulate 100-500 requests per day with peak hours
        requests_today = random.randint(100, 500)
        
        for _ in range(requests_today):
            # Random hour with peak distribution (more during business hours)
            hour = random.choices(
                range(24),
                weights=[1, 1, 1, 1, 2, 3, 5, 10, 15, 20, 20, 15, 10, 10, 8, 5, 3, 2, 2, 1, 1, 1, 1, 1],
            )[0]
            
            timestamp = start_time + timedelta(days=day, hours=hour, minutes=random.randint(0, 59))
            
            proxy_id, proxy_url, region, pool = random.choice(proxies)
            
            # Proxy-5 is underperformer (low success rate, high latency)
            if proxy_id == "proxy-5":
                success = random.random() > 0.6  # 40% success rate
                latency_ms = random.uniform(3000, 8000)  # High latency
            else:
                success = random.random() > 0.15  # 85% success rate
                latency_ms = random.uniform(100, 2000)  # Normal latency
            
            record = {
                "proxy_id": proxy_id,
                "proxy_url": proxy_url,
                "success": success,
                "latency_ms": latency_ms,
                "timestamp": timestamp,
                "pool": pool,
                "region": region,
                "target_domain": random.choice(domains),
                "error_type": None if success else random.choice(["timeout", "connection_refused", "403_forbidden"]),
            }
            data.append(record)
    
    print(f"Generated {len(data)} request records")
    return data


def main():
    """Run analytics example."""
    print("ProxyWhirl Analytics Engine Example")
    print("=" * 60)
    print()
    
    # Generate sample data
    sample_data = generate_sample_data(days=7)
    
    # Initialize analytics engine
    config = AnalysisConfig(
        lookback_days=7,
        min_success_rate=0.85,
        max_latency_ms=3000,
        cache_results=True,
    )
    
    engine = AnalyticsEngine(config=config)
    
    # Record data in analytics engine
    print("Recording data in analytics engine...")
    for record in sample_data:
        engine.record_request(
            proxy_id=record["proxy_id"],
            proxy_url=record["proxy_url"],
            success=record["success"],
            latency_ms=record["latency_ms"],
            timestamp=record["timestamp"],
            pool=record["pool"],
            region=record["region"],
            target_domain=record["target_domain"],
            error_type=record["error_type"],
        )
    
    print(f"Recorded {len(sample_data)} requests")
    print()
    
    # ========================================================================
    # PERFORMANCE ANALYSIS (User Story 1)
    # ========================================================================
    print("=" * 60)
    print("PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    analyzer = PerformanceAnalyzer(config=config)
    
    # Get proxy metrics
    proxy_metrics = engine.get_proxy_metrics()
    print(f"\nTracked {len(proxy_metrics)} proxies")
    
    # Rank proxies
    scores = analyzer.rank_proxies(proxy_metrics)
    
    print("\nTop 3 Performers:")
    for score in scores[:3]:
        print(f"  #{score.rank} {score.proxy_id}")
        print(f"      Overall Score: {score.overall_score:.3f}")
        print(f"      Success Rate: {score.success_rate_score:.1%}")
        print(f"      Latency Score: {score.latency_score:.3f}")
    
    print("\nBottom Performers:")
    underperformers = analyzer.identify_underperforming_proxies(proxy_metrics)
    for proxy_id, issues in underperformers:
        print(f"  {proxy_id}:")
        for issue in issues:
            print(f"    - {issue}")
    
    # Statistical summary
    summary = analyzer.calculate_statistical_summary(proxy_metrics)
    if summary:
        print("\nStatistical Summary:")
        print(f"  Active Proxies: {summary['active_proxies']}")
        print(f"  Mean Success Rate: {summary['success_rate']['mean']:.1%}")
        print(f"  Median Latency: {summary['latency_ms']['median']:.0f}ms")
        print(f"  P95 Latency: {summary['latency_ms']['p95']:.0f}ms")
    
    print()
    
    # ========================================================================
    # PATTERN DETECTION (User Story 2)
    # ========================================================================
    print("=" * 60)
    print("USAGE PATTERN DETECTION")
    print("=" * 60)
    
    detector = PatternDetector(config=config)
    
    # Detect peak hours
    peak_hours = detector.detect_peak_hours(sample_data)
    print(f"\nPeak Hours: {peak_hours}")
    
    # Analyze request volumes
    volume_analysis = detector.analyze_request_volumes(sample_data)
    print(f"\nVolume Analysis:")
    print(f"  Total Requests: {volume_analysis.get('total_requests', 0)}")
    print(f"  Avg Requests/Window: {volume_analysis.get('avg_requests_per_window', 0):.1f}")
    print(f"  Trend: {volume_analysis.get('trend', 'N/A')}")
    
    # Detect geographic patterns
    geo_patterns = detector.detect_geographic_patterns(sample_data, top_n=5)
    print(f"\nTop Regions:")
    for region, count in geo_patterns:
        print(f"  {region}: {count} requests")
    
    # Detect anomalies
    anomalies = detector.detect_anomalies(sample_data)
    if anomalies:
        print(f"\nDetected {len(anomalies)} anomalies")
        for anomaly in anomalies[:3]:
            print(f"  {anomaly.anomaly_type}: {anomaly.metric_name}")
            print(f"    Expected: {anomaly.expected_value:.1f}, Actual: {anomaly.actual_value:.1f}")
    else:
        print("\nNo significant anomalies detected")
    
    print()
    
    # ========================================================================
    # FAILURE ANALYSIS (User Story 3)
    # ========================================================================
    print("=" * 60)
    print("FAILURE ANALYSIS")
    print("=" * 60)
    
    failure_analyzer = FailureAnalyzer(config=config)
    
    # Get failure data
    failure_data = [r for r in sample_data if not r["success"]]
    print(f"\nTotal Failures: {len(failure_data)}")
    
    # Analyze failures
    failure_result = failure_analyzer.analyze_failures(failure_data)
    print(f"Failure Clusters: {failure_result.total_clusters}")
    print(f"Clustering Effectiveness: {failure_result.clustering_effectiveness:.1%}")
    
    print("\nTop Failing Proxies:")
    for proxy_id, count in failure_result.top_failing_proxies[:3]:
        print(f"  {proxy_id}: {count} failures")
    
    print("\nTop Error Types:")
    for error_type, count in failure_result.top_error_types[:3]:
        print(f"  {error_type}: {count} occurrences")
    
    if failure_result.clusters:
        print("\nSample Cluster Analysis:")
        cluster = failure_result.clusters[0]
        print(f"  Cluster Size: {cluster.size}")
        print(f"  Suspected Root Causes:")
        for cause in cluster.suspected_root_causes[:2]:
            print(f"    - {cause}")
    
    print()
    
    # ========================================================================
    # COST ANALYSIS (User Story 4)
    # ========================================================================
    print("=" * 60)
    print("COST & ROI ANALYSIS")
    print("=" * 60)
    
    cost_analyzer = CostAnalyzer(config=config)
    
    # Calculate costs (simulated)
    total_cost = 150.0  # $150 for the period
    cost_metrics = cost_analyzer.calculate_cost_metrics(
        total_cost=total_cost,
        request_data=sample_data,
        source="proxy-provider",
        period_start=sample_data[0]["timestamp"],
        period_end=sample_data[-1]["timestamp"],
    )
    
    print(f"\nCost Metrics:")
    print(f"  Total Cost: ${cost_metrics.total_cost:.2f}")
    print(f"  Cost per Request: ${cost_metrics.cost_per_request:.4f}")
    print(f"  Cost per Successful Request: ${cost_metrics.cost_per_successful_request:.4f}")
    print(f"  Efficiency Score: {cost_metrics.cost_efficiency_score:.3f}")
    
    # ROI calculation
    roi_metrics = cost_analyzer.calculate_roi_metrics(
        total_cost=total_cost,
        request_data=sample_data,
        value_per_successful_request=0.10,  # $0.10 value per successful request
    )
    print(f"\nROI Metrics:")
    print(f"  Total Value: ${roi_metrics['total_value']:.2f}")
    print(f"  Profit: ${roi_metrics['profit']:.2f}")
    print(f"  ROI: {roi_metrics['roi_percent']:.1f}%")
    print(f"  Break Even: {roi_metrics['break_even']}")
    
    print()
    
    # ========================================================================
    # PREDICTIVE ANALYTICS (User Story 5)
    # ========================================================================
    print("=" * 60)
    print("PREDICTIVE ANALYTICS")
    print("=" * 60)
    
    predictive = PredictiveAnalytics(config=config)
    
    # Forecast request volume
    prediction = predictive.forecast_request_volume(
        historical_data=sample_data,
        forecast_days=7,
    )
    
    print(f"\nForecast for Next 7 Days:")
    print(f"  Mean Prediction: {prediction.mean_prediction:.0f} requests")
    print(f"  Confidence Interval: [{prediction.confidence_interval_lower:.0f}, {prediction.confidence_interval_upper:.0f}]")
    print(f"  Trend: {prediction.detected_trend}")
    print(f"  Model Accuracy (MAPE): {prediction.accuracy_metrics.get('mape', 0):.1f}%")
    print(f"  Recommended Pool Size: {prediction.recommended_pool_size} proxies")
    
    print("\nCapacity Recommendations:")
    for recommendation in prediction.capacity_recommendations[:3]:
        print(f"  - {recommendation}")
    
    # Capacity forecast
    capacity_forecast = predictive.forecast_capacity_needs(
        historical_data=sample_data,
        forecast_days=30,
    )
    
    print(f"\n30-Day Capacity Forecast:")
    print(f"  Current Proxies Needed: {capacity_forecast['current_proxies_needed']}")
    print(f"  Future Proxies Needed: {capacity_forecast['future_proxies_needed']}")
    print(f"  Capacity Change: {capacity_forecast['capacity_change']:+d} proxies")
    
    print()
    
    # ========================================================================
    # COMPREHENSIVE REPORT
    # ========================================================================
    print("=" * 60)
    print("COMPREHENSIVE ANALYSIS REPORT")
    print("=" * 60)
    
    # Generate comprehensive report
    query = AnalyticsQuery(
        analysis_types=[
            AnalysisType.PERFORMANCE,
            AnalysisType.USAGE_PATTERNS,
            AnalysisType.FAILURE_ANALYSIS,
        ],
        lookback_days=7,
    )
    
    report = engine.analyze(query)
    
    print(f"\nReport ID: {report.report_id}")
    print(f"Analysis Period: {report.analysis_start} to {report.analysis_end}")
    print(f"Duration: {report.total_duration.total_seconds():.2f}s")
    print(f"\nKey Findings ({len(report.key_findings)}):")
    for finding in report.key_findings:
        print(f"  - {finding}")
    
    # Export report
    output_path = "/tmp/analytics_report.json"
    from proxywhirl.analytics_models import ExportFormat
    engine.export_report(report, ExportFormat.JSON, output_path)
    print(f"\nReport exported to: {output_path}")
    
    print()
    print("=" * 60)
    print("Analytics Example Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
