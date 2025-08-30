"""proxywhirl/caches/analytics.py -- Elite cache analytics and performance intelligence

Advanced analytics system with:
- Real-time performance monitoring and trend analysis
- Machine learning-based predictive optimization
- Comprehensive health scoring and anomaly detection
- Resource utilization forecasting and capacity planning
- Cache behavior analysis and usage pattern recognition
- Automated performance tuning recommendations
"""

from __future__ import annotations

import asyncio
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from loguru import logger
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from proxywhirl.caches.base import CacheMetrics


@dataclass
class PerformanceSnapshot:
    """Performance metrics snapshot at a specific point in time."""
    timestamp: float
    read_latency_ms: float
    write_latency_ms: float
    throughput_ops_sec: float
    hit_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    error_rate: float
    concurrent_operations: int


@dataclass
class AnalyticsConfig:
    """Configuration for cache analytics system."""
    enable_ml_optimization: bool = True
    snapshot_interval: int = 60  # seconds
    retention_hours: int = 168   # 1 week
    anomaly_detection_threshold: float = 2.0  # standard deviations
    prediction_horizon_minutes: int = 60
    performance_samples_per_hour: int = 60
    enable_trend_analysis: bool = True
    enable_capacity_planning: bool = True


@dataclass 
class HealthScore:
    """Comprehensive health scoring for cache performance."""
    overall_score: float = 0.0  # 0-100
    performance_score: float = 0.0
    reliability_score: float = 0.0
    efficiency_score: float = 0.0
    scalability_score: float = 0.0
    factors: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation."""
    category: str  # 'performance', 'memory', 'configuration'
    priority: int  # 1-10, 10 being highest
    title: str
    description: str
    expected_improvement: float  # Percentage improvement expected
    implementation_effort: str  # 'low', 'medium', 'high'
    risk_level: str  # 'low', 'medium', 'high'


class CacheAnalytics:
    """Elite cache analytics system with ML-powered optimization."""

    def __init__(self, config: Optional[AnalyticsConfig] = None):
        self.config = config or AnalyticsConfig()
        
        # Time series data storage
        self._performance_history: deque = deque(maxlen=self._calculate_max_samples())
        self._hourly_aggregates: Dict[str, deque] = {
            'latency_p50': deque(maxlen=24 * 7),  # 1 week of hourly data
            'latency_p95': deque(maxlen=24 * 7),
            'throughput': deque(maxlen=24 * 7),
            'hit_rate': deque(maxlen=24 * 7),
            'error_rate': deque(maxlen=24 * 7),
            'memory_usage': deque(maxlen=24 * 7),
        }
        
        # Analytics models
        self._ml_models: Dict[str, Any] = {}
        self._scalers: Dict[str, StandardScaler] = {}
        self._baseline_metrics: Dict[str, float] = {}
        
        # Real-time analysis
        self._anomalies: deque = deque(maxlen=1000)
        self._trends: Dict[str, Dict[str, Any]] = {}
        self._predictions: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self._current_health_score = HealthScore()
        self._optimization_recommendations: List[OptimizationRecommendation] = []
        
        # Background task management
        self._analytics_task: Optional[asyncio.Task] = None
        self._is_running = False

    def _calculate_max_samples(self) -> int:
        """Calculate maximum samples to retain based on configuration."""
        samples_per_hour = self.config.performance_samples_per_hour
        return int(self.config.retention_hours * samples_per_hour)

    async def start_analytics(self) -> None:
        """Start the analytics engine with background processing."""
        if self._is_running:
            return
        
        self._is_running = True
        self._analytics_task = asyncio.create_task(self._analytics_loop())
        logger.info("Cache analytics engine started")

    async def stop_analytics(self) -> None:
        """Stop the analytics engine gracefully."""
        self._is_running = False
        if self._analytics_task:
            self._analytics_task.cancel()
            try:
                await self._analytics_task
            except asyncio.CancelledError:
                pass
        logger.info("Cache analytics engine stopped")

    async def _analytics_loop(self) -> None:
        """Main analytics processing loop."""
        while self._is_running:
            try:
                await asyncio.sleep(self.config.snapshot_interval)
                await self._perform_analytics_cycle()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analytics cycle error: {e}")

    async def _perform_analytics_cycle(self) -> None:
        """Perform a complete analytics cycle."""
        # Update hourly aggregates
        await self._update_hourly_aggregates()
        
        # Detect anomalies
        await self._detect_anomalies()
        
        # Update trend analysis
        if self.config.enable_trend_analysis:
            await self._analyze_trends()
        
        # Generate predictions
        if self.config.enable_ml_optimization:
            await self._update_ml_predictions()
        
        # Update health scores
        await self._calculate_health_scores()
        
        # Generate optimization recommendations
        await self._generate_recommendations()

    # === Data ingestion and processing ===

    def record_performance_snapshot(self, snapshot: PerformanceSnapshot) -> None:
        """Record a performance snapshot for analysis."""
        self._performance_history.append(snapshot)
        
        # Update baseline metrics if this is early in the process
        if len(self._performance_history) <= 100:
            self._update_baseline_metrics(snapshot)

    def record_cache_metrics(self, metrics: CacheMetrics) -> None:
        """Record cache metrics and convert to performance snapshot."""
        # Calculate derived metrics
        total_ops = metrics.cache_hits + metrics.cache_misses
        hit_rate = metrics.cache_hits / max(1, total_ops)
        
        snapshot = PerformanceSnapshot(
            timestamp=time.time(),
            read_latency_ms=metrics.avg_response_time * 1000 if metrics.avg_response_time else 0,
            write_latency_ms=0,  # Would need to be tracked separately
            throughput_ops_sec=0,  # Would need to be calculated from operation history
            hit_rate=hit_rate,
            memory_usage_mb=metrics.memory_usage_mb or 0,
            cpu_usage_percent=0,  # Would need system monitoring
            error_rate=1.0 - metrics.success_rate,
            concurrent_operations=0,  # Would need to be tracked
        )
        
        self.record_performance_snapshot(snapshot)

    def _update_baseline_metrics(self, snapshot: PerformanceSnapshot) -> None:
        """Update baseline performance metrics for comparison."""
        metrics = {
            'read_latency': snapshot.read_latency_ms,
            'write_latency': snapshot.write_latency_ms,
            'throughput': snapshot.throughput_ops_sec,
            'hit_rate': snapshot.hit_rate,
            'error_rate': snapshot.error_rate,
        }
        
        for metric, value in metrics.items():
            if metric in self._baseline_metrics:
                # Exponential moving average
                alpha = 0.1
                self._baseline_metrics[metric] = (
                    alpha * value + (1 - alpha) * self._baseline_metrics[metric]
                )
            else:
                self._baseline_metrics[metric] = value

    # === Hourly aggregation ===

    async def _update_hourly_aggregates(self) -> None:
        """Update hourly performance aggregates."""
        if len(self._performance_history) < 10:
            return
        
        # Get recent samples (last hour)
        current_time = time.time()
        hour_ago = current_time - 3600
        
        recent_samples = [
            s for s in self._performance_history 
            if s.timestamp >= hour_ago
        ]
        
        if not recent_samples:
            return
        
        # Calculate aggregates
        latencies = [s.read_latency_ms for s in recent_samples]
        throughputs = [s.throughput_ops_sec for s in recent_samples]
        hit_rates = [s.hit_rate for s in recent_samples]
        error_rates = [s.error_rate for s in recent_samples]
        memory_usage = [s.memory_usage_mb for s in recent_samples]
        
        # Store hourly aggregates
        self._hourly_aggregates['latency_p50'].append(statistics.median(latencies))
        self._hourly_aggregates['latency_p95'].append(np.percentile(latencies, 95))
        self._hourly_aggregates['throughput'].append(statistics.mean(throughputs))
        self._hourly_aggregates['hit_rate'].append(statistics.mean(hit_rates))
        self._hourly_aggregates['error_rate'].append(statistics.mean(error_rates))
        self._hourly_aggregates['memory_usage'].append(statistics.mean(memory_usage))

    # === Anomaly detection ===

    async def _detect_anomalies(self) -> None:
        """Detect performance anomalies using statistical analysis."""
        if len(self._performance_history) < 100:
            return
        
        recent_samples = list(self._performance_history)[-60:]  # Last hour
        historical_samples = list(self._performance_history)[:-60]  # Everything before
        
        if not historical_samples:
            return
        
        # Analyze key metrics for anomalies
        metrics_to_check = [
            ('read_latency_ms', 'higher_is_worse'),
            ('error_rate', 'higher_is_worse'),
            ('hit_rate', 'lower_is_worse'),
            ('throughput_ops_sec', 'lower_is_worse'),
        ]
        
        for metric, direction in metrics_to_check:
            recent_values = [getattr(s, metric) for s in recent_samples]
            historical_values = [getattr(s, metric) for s in historical_samples]
            
            if not recent_values or not historical_values:
                continue
            
            # Statistical anomaly detection
            historical_mean = statistics.mean(historical_values)
            historical_std = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
            recent_mean = statistics.mean(recent_values)
            
            if historical_std > 0:
                z_score = abs(recent_mean - historical_mean) / historical_std
                
                if z_score > self.config.anomaly_detection_threshold:
                    anomaly = {
                        'timestamp': time.time(),
                        'metric': metric,
                        'z_score': z_score,
                        'recent_value': recent_mean,
                        'historical_mean': historical_mean,
                        'direction': direction,
                        'severity': 'high' if z_score > 3.0 else 'medium',
                    }
                    self._anomalies.append(anomaly)
                    
                    logger.warning(f"Performance anomaly detected: {metric} "
                                 f"z-score={z_score:.2f}, recent={recent_mean:.2f}")

    # === Trend analysis ===

    async def _analyze_trends(self) -> None:
        """Analyze performance trends over time."""
        if len(self._hourly_aggregates['latency_p50']) < 24:  # Need at least 24 hours
            return
        
        for metric, values in self._hourly_aggregates.items():
            if len(values) < 10:
                continue
            
            # Calculate trend using linear regression
            x = np.array(range(len(values))).reshape(-1, 1)
            y = np.array(list(values))
            
            try:
                model = LinearRegression().fit(x, y)
                trend_slope = model.coef_[0]
                trend_score = model.score(x, y)  # R²
                
                # Classify trend
                if abs(trend_slope) < 0.001:
                    trend_direction = 'stable'
                elif trend_slope > 0:
                    trend_direction = 'increasing'
                else:
                    trend_direction = 'decreasing'
                
                self._trends[metric] = {
                    'direction': trend_direction,
                    'slope': trend_slope,
                    'confidence': trend_score,
                    'last_updated': time.time(),
                }
                
            except Exception as e:
                logger.debug(f"Trend analysis failed for {metric}: {e}")

    # === ML-based predictions ===

    async def _update_ml_predictions(self) -> None:
        """Update ML-based performance predictions."""
        if len(self._performance_history) < 200:  # Need sufficient data
            return
        
        # Prepare feature matrix
        features = []
        targets = {}
        
        samples = list(self._performance_history)[-1000:]  # Last 1000 samples
        
        for i, sample in enumerate(samples[:-1]):  # Exclude last sample for prediction
            # Features: time-based, performance metrics
            hour_of_day = time.localtime(sample.timestamp).tm_hour
            day_of_week = time.localtime(sample.timestamp).tm_wday
            
            feature_vector = [
                hour_of_day,
                day_of_week,
                sample.throughput_ops_sec,
                sample.hit_rate,
                sample.memory_usage_mb,
                sample.concurrent_operations,
            ]
            features.append(feature_vector)
            
            # Targets: next sample's metrics
            next_sample = samples[i + 1]
            for target_metric in ['read_latency_ms', 'hit_rate', 'error_rate']:
                if target_metric not in targets:
                    targets[target_metric] = []
                targets[target_metric].append(getattr(next_sample, target_metric))
        
        if not features:
            return
        
        # Train models for each target metric
        X = np.array(features)
        
        for target_metric, y_values in targets.items():
            try:
                y = np.array(y_values)
                
                # Scale features
                if target_metric not in self._scalers:
                    self._scalers[target_metric] = StandardScaler()
                    X_scaled = self._scalers[target_metric].fit_transform(X)
                else:
                    X_scaled = self._scalers[target_metric].transform(X)
                
                # Train model
                model = LinearRegression()
                model.fit(X_scaled, y)
                self._ml_models[target_metric] = model
                
                # Generate prediction for next hour
                current_sample = samples[-1]
                current_time = time.time()
                future_hour = time.localtime(current_time + 3600).tm_hour
                future_day = time.localtime(current_time + 3600).tm_wday
                
                future_features = np.array([[
                    future_hour,
                    future_day,
                    current_sample.throughput_ops_sec,
                    current_sample.hit_rate,
                    current_sample.memory_usage_mb,
                    current_sample.concurrent_operations,
                ]])
                
                future_features_scaled = self._scalers[target_metric].transform(future_features)
                prediction = model.predict(future_features_scaled)[0]
                
                self._predictions[target_metric] = {
                    'value': prediction,
                    'timestamp': current_time + 3600,
                    'confidence': model.score(X_scaled, y),
                    'last_updated': time.time(),
                }
                
            except Exception as e:
                logger.debug(f"ML prediction failed for {target_metric}: {e}")

    # === Health scoring ===

    async def _calculate_health_scores(self) -> None:
        """Calculate comprehensive health scores."""
        if len(self._performance_history) < 10:
            self._current_health_score = HealthScore()
            return
        
        recent_samples = list(self._performance_history)[-60:]  # Last hour
        
        # Performance score (0-100)
        avg_latency = statistics.mean([s.read_latency_ms for s in recent_samples])
        latency_score = max(0, 100 - (avg_latency / 10))  # Assuming 1000ms = 0 score
        
        avg_throughput = statistics.mean([s.throughput_ops_sec for s in recent_samples])
        throughput_score = min(100, avg_throughput / 10)  # Assuming 1000 ops/sec = 100 score
        
        performance_score = (latency_score + throughput_score) / 2
        
        # Reliability score (0-100)
        avg_error_rate = statistics.mean([s.error_rate for s in recent_samples])
        error_score = max(0, 100 - (avg_error_rate * 1000))  # 10% error = 0 score
        
        anomaly_count = len([a for a in self._anomalies if a['timestamp'] > time.time() - 3600])
        anomaly_score = max(0, 100 - (anomaly_count * 10))
        
        reliability_score = (error_score + anomaly_score) / 2
        
        # Efficiency score (0-100)
        avg_hit_rate = statistics.mean([s.hit_rate for s in recent_samples])
        hit_rate_score = avg_hit_rate * 100
        
        avg_memory = statistics.mean([s.memory_usage_mb for s in recent_samples])
        # Assuming 1GB is optimal, score decreases with higher usage
        memory_score = max(0, 100 - max(0, (avg_memory - 1024) / 50))
        
        efficiency_score = (hit_rate_score + memory_score) / 2
        
        # Scalability score (based on trends)
        scalability_score = 75  # Default score
        
        for metric, trend_info in self._trends.items():
            if metric == 'latency_p95' and trend_info['direction'] == 'increasing':
                scalability_score -= 15
            elif metric == 'throughput' and trend_info['direction'] == 'decreasing':
                scalability_score -= 15
            elif metric == 'error_rate' and trend_info['direction'] == 'increasing':
                scalability_score -= 10
        
        scalability_score = max(0, min(100, scalability_score))
        
        # Overall score
        overall_score = (
            performance_score * 0.3 +
            reliability_score * 0.3 +
            efficiency_score * 0.25 +
            scalability_score * 0.15
        )
        
        self._current_health_score = HealthScore(
            overall_score=overall_score,
            performance_score=performance_score,
            reliability_score=reliability_score,
            efficiency_score=efficiency_score,
            scalability_score=scalability_score,
            factors={
                'latency': latency_score,
                'throughput': throughput_score,
                'error_rate': error_score,
                'anomalies': anomaly_score,
                'hit_rate': hit_rate_score,
                'memory_usage': memory_score,
            }
        )

    # === Recommendations ===

    async def _generate_recommendations(self) -> None:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        # Latency recommendations
        if self._current_health_score.factors.get('latency', 0) < 70:
            recommendations.append(OptimizationRecommendation(
                category='performance',
                priority=8,
                title='High Latency Detected',
                description='Consider enabling indexing, increasing batch sizes, or optimizing queries',
                expected_improvement=25.0,
                implementation_effort='medium',
                risk_level='low'
            ))
        
        # Hit rate recommendations
        if self._current_health_score.factors.get('hit_rate', 0) < 80:
            recommendations.append(OptimizationRecommendation(
                category='performance',
                priority=7,
                title='Low Cache Hit Rate',
                description='Consider increasing cache size, improving prefetching, or reviewing cache strategy',
                expected_improvement=15.0,
                implementation_effort='medium',
                risk_level='low'
            ))
        
        # Memory recommendations
        if self._current_health_score.factors.get('memory_usage', 0) < 60:
            recommendations.append(OptimizationRecommendation(
                category='memory',
                priority=6,
                title='High Memory Usage',
                description='Consider enabling compression, reducing cache size, or implementing memory-efficient structures',
                expected_improvement=20.0,
                implementation_effort='high',
                risk_level='medium'
            ))
        
        # Trending issues
        for metric, trend_info in self._trends.items():
            if trend_info['direction'] == 'increasing' and metric in ['latency_p95', 'error_rate']:
                recommendations.append(OptimizationRecommendation(
                    category='performance',
                    priority=9,
                    title=f'Degrading {metric.replace("_", " ").title()}',
                    description=f'The {metric} is showing an increasing trend. Investigate root cause.',
                    expected_improvement=30.0,
                    implementation_effort='high',
                    risk_level='high'
                ))
        
        self._optimization_recommendations = recommendations

    # === Public API ===

    def get_health_score(self) -> HealthScore:
        """Get current health score."""
        return self._current_health_score

    def get_recommendations(self) -> List[OptimizationRecommendation]:
        """Get current optimization recommendations."""
        return self._optimization_recommendations.copy()

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        recent_samples = list(self._performance_history)[-60:] if self._performance_history else []
        
        if not recent_samples:
            return {"status": "insufficient_data"}
        
        return {
            "health_score": self._current_health_score.__dict__,
            "recent_performance": {
                "avg_read_latency_ms": statistics.mean([s.read_latency_ms for s in recent_samples]),
                "p95_read_latency_ms": np.percentile([s.read_latency_ms for s in recent_samples], 95),
                "avg_hit_rate": statistics.mean([s.hit_rate for s in recent_samples]),
                "avg_error_rate": statistics.mean([s.error_rate for s in recent_samples]),
                "avg_throughput": statistics.mean([s.throughput_ops_sec for s in recent_samples]),
            },
            "trends": self._trends,
            "predictions": self._predictions,
            "anomalies_last_hour": len([a for a in self._anomalies if a['timestamp'] > time.time() - 3600]),
            "recommendations_count": len(self._optimization_recommendations),
            "data_points": len(self._performance_history),
        }
