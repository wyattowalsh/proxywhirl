"""
ProxyWhirl Analytics Engine Example

Demonstrates comprehensive analytics capabilities including performance analysis,
pattern detection, failure analysis, cost tracking, and predictive forecasting.
"""

from datetime import datetime, timedelta
from random import random, randint, choice

from proxywhirl import (
    AnalysisConfig,
    AnalysisType,
    AnalyticsEngine,
    AnalyticsQuery,
)


def generate_sample_data(engine: AnalyticsEngine, days: int = 30) -> None:
    """Generate sample proxy request data for demonstration."""
    print(f"\n?? Generating {days} days of sample data...")
    
    # Sample proxies
    proxies = [
        ("proxy-us-1", "http://proxy1.example.com:8080", "us-east-1", "pool-1"),
        ("proxy-us-2", "http://proxy2.example.com:8080", "us-west-2", "pool-1"),
        ("proxy-eu-1", "http://proxy3.example.com:8080", "eu-west-1", "pool-2"),
        ("proxy-eu-2", "http://proxy4.example.com:8080", "eu-central-1", "pool-2"),
        ("proxy-ap-1", "http://proxy5.example.com:8080", "ap-southeast-1", "pool-3"),
    ]
    
    # Target domains
    domains = ["example.com", "api.example.com", "cdn.example.com"]
    error_types = ["timeout", "connection_refused", "http_403", "http_503"]
    
    base_time = datetime.now() - timedelta(days=days)
    
    # Generate requests over time
    for day in range(days):
        # More requests on recent days (growth trend)
        daily_requests = 50 + (day * 2)
        
        for _ in range(daily_requests):
            proxy_id, proxy_url, region, pool = choice(proxies)
            
            # Time distribution (more during business hours)
            hour = randint(0, 23)
            if 9 <= hour <= 17:  # Business hours - more traffic
                timestamp = base_time + timedelta(days=day, hours=hour, minutes=randint(0, 59))
                
                # Better performance during business hours
                success_rate = 0.85 + (random() * 0.1)
                base_latency = 200 + (random() * 100)
            else:
                timestamp = base_time + timedelta(days=day, hours=hour, minutes=randint(0, 59))
                success_rate = 0.75 + (random() * 0.15)
                base_latency = 300 + (random() * 200)
            
            # Simulate success/failure
            success = random() < success_rate
            latency_ms = base_latency if success else base_latency * 1.5
            
            # Record request
            engine.record_request(
                proxy_id=proxy_id,
                proxy_url=proxy_url,
                success=success,
                latency_ms=latency_ms,
                timestamp=timestamp,
                pool=pool,
                region=region,
                target_domain=choice(domains),
                error_type=choice(error_types) if not success else None,
            )
    
    # Record uptime data
    for proxy_id, _, _, _ in proxies:
        uptime_hours = days * 24 * (0.95 + random() * 0.04)  # 95-99% uptime
        downtime_hours = days * 24 - uptime_hours
        engine.record_proxy_uptime(proxy_id, uptime_hours, downtime_hours)
    
    print(f"? Generated sample data for {len(proxies)} proxies")


def demonstrate_performance_analysis(engine: AnalyticsEngine) -> None:
    """Demonstrate performance analysis capabilities."""
    print("\n" + "="*80)
    print("?? PERFORMANCE ANALYSIS")
    print("="*80)
    
    # Run performance analysis
    query = AnalyticsQuery(
        analysis_types=[AnalysisType.PERFORMANCE],
        include_recommendations=True,
        top_n_performers=5,
    )
    
    report = engine.analyze_performance(query)
    
    # Display executive summary
    print(f"\n?? Executive Summary:")
    print(f"   {report.executive_summary}")
    
    # Display key findings
    print(f"\n?? Key Findings:")
    for i, finding in enumerate(report.key_findings, 1):
        print(f"   {i}. {finding}")
    
    # Display top performers
    if report.performance_scores:
        print(f"\n?? Top Performing Proxies:")
        sorted_scores = sorted(
            report.performance_scores.items(),
            key=lambda x: x[1].overall_score,
            reverse=True,
        )
        for i, (proxy_id, score) in enumerate(sorted_scores[:3], 1):
            print(f"   {i}. {proxy_id}: {score.overall_score:.1f}/100 "
                  f"(Success: {score.success_rate_score:.1f}, "
                  f"Latency: {score.latency_score:.1f}, "
                  f"Uptime: {score.uptime_score:.1f})")
    
    # Display recommendations
    if report.recommendations:
        print(f"\n?? Recommendations:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"   {i}. [{rec.priority.value.upper()}] {rec.title}")
            print(f"      {rec.description}")
            if rec.estimated_improvement:
                print(f"      Impact: {rec.estimated_improvement}")
    
    # Export report
    engine.export_to_json(report, "/tmp/analytics_performance_report.json")
    engine.export_to_csv(report, "/tmp/analytics_performance_metrics.csv")
    print(f"\n?? Reports exported to /tmp/")


def demonstrate_metrics_summary(engine: AnalyticsEngine) -> None:
    """Display metrics summary."""
    print("\n" + "="*80)
    print("?? METRICS SUMMARY")
    print("="*80)
    
    summary = engine.get_metrics_summary()
    
    print(f"\n   Total Proxies: {summary['total_proxies']}")
    print(f"   Total Requests: {summary['total_requests_all_proxies']:,}")
    print(f"   Data Period: {summary['oldest_data']} to {summary['newest_data']}")
    print(f"   Cache Size: {summary['cache_size']} entries")


def main() -> None:
    """Run analytics engine demonstration."""
    print("="*80)
    print("?? ProxyWhirl Analytics Engine - Comprehensive Demo")
    print("="*80)
    
    # Initialize analytics engine with custom configuration
    config = AnalysisConfig(
        lookback_days=30,
        min_success_rate=0.75,
        max_avg_latency_ms=5000.0,
        min_uptime_percentage=95.0,
        cache_results=True,
        prediction_horizon_days=7,
    )
    
    engine = AnalyticsEngine(config=config)
    print(f"\n? Analytics engine initialized")
    print(f"   Configuration: {config.lookback_days} days lookback, "
          f"{config.min_success_rate*100:.0f}% min success rate")
    
    # Generate sample data
    generate_sample_data(engine, days=30)
    
    # Display metrics summary
    demonstrate_metrics_summary(engine)
    
    # Demonstrate performance analysis
    demonstrate_performance_analysis(engine)
    
    print("\n" + "="*80)
    print("? Demo completed successfully!")
    print("="*80)


if __name__ == "__main__":
    main()
