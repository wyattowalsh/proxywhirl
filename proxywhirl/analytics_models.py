"""
Data models for ProxyWhirl analytics engine using Pydantic v2.

Provides comprehensive analytics data models for performance analysis,
usage pattern detection, failure analysis, cost tracking, and predictive forecasting.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# ENUMS
# ============================================================================


class AnalysisType(str, Enum):
    """Types of analytics analysis."""

    PERFORMANCE      = "performance"
    USAGE_PATTERNS   = "usage_patterns"
    FAILURE_ANALYSIS = "failure_analysis"
    COST_ANALYSIS    = "cost_analysis"
    PREDICTIVE       = "predictive"
    COMPREHENSIVE    = "comprehensive"


class ExportFormat(str, Enum):
    """Supported export formats for analytics reports."""

    CSV  = "csv"
    JSON = "json"
    PDF  = "pdf"


class AnomalyType(str, Enum):
    """Types of anomalies detected in analytics."""

    PERFORMANCE_DEGRADATION = "performance_degradation"
    USAGE_SPIKE             = "usage_spike"
    USAGE_DROP              = "usage_drop"
    FAILURE_SPIKE           = "failure_spike"
    COST_ANOMALY            = "cost_anomaly"


class TrendDirection(str, Enum):
    """Direction of detected trends."""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE     = "stable"
    VOLATILE   = "volatile"


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations."""

    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"


# ============================================================================
# CORE DATA MODELS
# ============================================================================


class ProxyPerformanceMetrics(BaseModel):
    """Performance metrics for a single proxy.
    
    Tracks comprehensive performance statistics including success rate,
    latency percentiles, uptime, and request counts.
    """

    model_config = ConfigDict(frozen=False)

    # Identification
    proxy_id:           str                    = Field(..., description="Unique proxy identifier")
    proxy_url:          str                    = Field(..., description="Proxy URL")
    pool:               Optional[str]          = Field(None, description="Proxy pool name")
    region:             Optional[str]          = Field(None, description="Geographic region")
    
    # Request statistics
    total_requests:     int                    = Field(default=0, ge=0)
    successful_requests: int                   = Field(default=0, ge=0)
    failed_requests:    int                    = Field(default=0, ge=0)
    success_rate:       float                  = Field(default=0.0, ge=0.0, le=1.0)
    
    # Latency statistics (milliseconds)
    avg_latency_ms:     float                  = Field(default=0.0, ge=0.0)
    min_latency_ms:     float                  = Field(default=0.0, ge=0.0)
    max_latency_ms:     float                  = Field(default=0.0, ge=0.0)
    p50_latency_ms:     float                  = Field(default=0.0, ge=0.0)
    p95_latency_ms:     float                  = Field(default=0.0, ge=0.0)
    p99_latency_ms:     float                  = Field(default=0.0, ge=0.0)
    
    # Uptime tracking (hours)
    total_uptime_hours:   float                = Field(default=0.0, ge=0.0)
    total_downtime_hours: float                = Field(default=0.0, ge=0.0)
    uptime_percentage:    float                = Field(default=100.0, ge=0.0, le=100.0)
    
    # Timestamps
    first_seen:         datetime               = Field(default_factory=datetime.now)
    last_seen:          datetime               = Field(default_factory=datetime.now)
    
    # Error tracking
    error_counts:       dict[str, int]         = Field(default_factory=dict)


class PerformanceScore(BaseModel):
    """Calculated performance score for a proxy.
    
    Provides a normalized score (0-100) based on multiple performance factors
    including success rate, latency, and uptime.
    """

    model_config = ConfigDict(frozen=True)

    proxy_id:         str                      = Field(..., description="Unique proxy identifier")
    overall_score:    float                    = Field(..., ge=0.0, le=100.0)
    
    # Component scores (0-100 each)
    success_rate_score:  float                 = Field(..., ge=0.0, le=100.0)
    latency_score:       float                 = Field(..., ge=0.0, le=100.0)
    uptime_score:        float                 = Field(..., ge=0.0, le=100.0)
    reliability_score:   float                 = Field(..., ge=0.0, le=100.0)
    
    # Ranking information
    rank:             Optional[int]            = Field(None, ge=1)
    percentile:       Optional[float]          = Field(None, ge=0.0, le=100.0)
    
    calculated_at:    datetime                 = Field(default_factory=datetime.now)


class UsagePattern(BaseModel):
    """Detected usage pattern in proxy requests.
    
    Represents identified patterns such as peak hours, request volumes,
    geographic distribution, or seasonal trends.
    """

    model_config = ConfigDict(frozen=True)

    pattern_id:       UUID                     = Field(default_factory=uuid4)
    pattern_type:     str                      = Field(..., description="Type of pattern detected")
    description:      str                      = Field(..., description="Human-readable description")
    
    # Pattern details
    peak_hours:       Optional[list[int]]      = Field(None, description="Peak usage hours (0-23)")
    peak_days:        Optional[list[str]]      = Field(None, description="Peak usage days")
    avg_requests_per_hour: Optional[float]     = Field(None, ge=0.0)
    max_requests_per_hour: Optional[float]     = Field(None, ge=0.0)
    
    # Geographic patterns
    top_regions:      Optional[dict[str, int]] = Field(None, description="Region -> request count")
    
    # Trend information
    trend_direction:  Optional[TrendDirection] = None
    confidence:       float                    = Field(default=0.0, ge=0.0, le=1.0)
    
    # Time period
    start_time:       datetime                 = Field(...)
    end_time:         datetime                 = Field(...)
    detected_at:      datetime                 = Field(default_factory=datetime.now)


class FailureCluster(BaseModel):
    """Group of related failures with common characteristics.
    
    Represents a cluster of failures grouped by proxy, domain, error type,
    or time period for root cause analysis.
    """

    model_config = ConfigDict(frozen=True)

    cluster_id:       UUID                     = Field(default_factory=uuid4)
    cluster_name:     str                      = Field(..., description="Human-readable cluster name")
    
    # Clustering factors
    common_proxy_ids:   Optional[list[str]]    = None
    common_domains:     Optional[list[str]]    = None
    common_error_types: Optional[list[str]]    = None
    common_regions:     Optional[list[str]]    = None
    
    # Cluster statistics
    failure_count:    int                      = Field(..., ge=1)
    affected_proxies: int                      = Field(..., ge=1)
    failure_rate:     float                    = Field(..., ge=0.0, le=1.0)
    
    # Root cause analysis
    probable_root_causes: list[str]            = Field(default_factory=list)
    correlation_factors:  dict[str, float]     = Field(default_factory=dict)
    
    # Time period
    first_failure:    datetime                 = Field(...)
    last_failure:     datetime                 = Field(...)
    detected_at:      datetime                 = Field(default_factory=datetime.now)


class Prediction(BaseModel):
    """Forecast prediction for future metrics.
    
    Provides predicted values for future time periods with confidence intervals
    and accuracy metrics.
    """

    model_config = ConfigDict(frozen=True)

    prediction_id:    UUID                     = Field(default_factory=uuid4)
    metric_name:      str                      = Field(..., description="Metric being predicted")
    
    # Prediction values
    predicted_value:  float                    = Field(...)
    lower_bound:      float                    = Field(..., description="Lower confidence bound")
    upper_bound:      float                    = Field(..., description="Upper confidence bound")
    confidence_level: float                    = Field(default=0.95, ge=0.0, le=1.0)
    
    # Prediction metadata
    prediction_horizon_days: int               = Field(..., ge=1)
    model_name:       str                      = Field(..., description="Prediction model used")
    model_accuracy:   Optional[float]          = Field(None, ge=0.0, le=1.0)
    
    # Timestamps
    prediction_date:  datetime                 = Field(...)
    created_at:       datetime                 = Field(default_factory=datetime.now)


class TimeSeriesData(BaseModel):
    """Time-series data point for analytics.
    
    Represents a single data point in a time-series for trend analysis
    and visualization.
    """

    model_config = ConfigDict(frozen=False)

    timestamp:        datetime                 = Field(...)
    metric_name:      str                      = Field(...)
    value:            float                    = Field(...)
    
    # Optional dimensions
    proxy_id:         Optional[str]            = None
    pool:             Optional[str]            = None
    region:           Optional[str]            = None
    
    # Metadata
    tags:             dict[str, str]           = Field(default_factory=dict)


class Recommendation(BaseModel):
    """Actionable recommendation from analytics.
    
    Provides specific, actionable recommendations based on analysis findings.
    """

    model_config = ConfigDict(frozen=True)

    recommendation_id: UUID                    = Field(default_factory=uuid4)
    title:            str                      = Field(..., description="Short recommendation title")
    description:      str                      = Field(..., description="Detailed recommendation")
    
    priority:         RecommendationPriority   = Field(default=RecommendationPriority.MEDIUM)
    category:         str                      = Field(..., description="Recommendation category")
    
    # Impact estimates
    estimated_improvement: Optional[str]       = Field(None, description="Expected improvement")
    estimated_effort:      Optional[str]       = Field(None, description="Implementation effort")
    
    # Related data
    affected_proxies:  list[str]               = Field(default_factory=list)
    supporting_data:   dict[str, Any]          = Field(default_factory=dict)
    
    created_at:       datetime                 = Field(default_factory=datetime.now)


class Anomaly(BaseModel):
    """Detected anomaly in analytics data.
    
    Represents an unusual pattern or outlier detected in the data.
    """

    model_config = ConfigDict(frozen=True)

    anomaly_id:       UUID                     = Field(default_factory=uuid4)
    anomaly_type:     AnomalyType              = Field(...)
    description:      str                      = Field(..., description="Anomaly description")
    
    # Anomaly details
    severity:         float                    = Field(..., ge=0.0, le=1.0, description="Severity score")
    expected_value:   float                    = Field(..., description="Expected value")
    actual_value:     float                    = Field(..., description="Actual value")
    deviation:        float                    = Field(..., description="Standard deviations from mean")
    
    # Context
    affected_entities: list[str]               = Field(default_factory=list)
    time_period_start: datetime                = Field(...)
    time_period_end:   datetime                = Field(...)
    
    detected_at:      datetime                 = Field(default_factory=datetime.now)


class AnalysisReport(BaseModel):
    """Comprehensive analytics report.
    
    Contains the complete results of an analytics analysis including findings,
    metrics, recommendations, and visualizations data.
    """

    model_config = ConfigDict(frozen=False)

    report_id:        UUID                     = Field(default_factory=uuid4)
    report_title:     str                      = Field(..., description="Report title")
    analysis_type:    AnalysisType             = Field(...)
    
    # Time period
    period_start:     datetime                 = Field(...)
    period_end:       datetime                 = Field(...)
    
    # Key findings
    executive_summary: str                     = Field(..., description="High-level summary")
    key_findings:     list[str]                = Field(default_factory=list)
    
    # Analysis results
    performance_metrics: Optional[dict[str, ProxyPerformanceMetrics]] = None
    performance_scores:  Optional[dict[str, PerformanceScore]]         = None
    usage_patterns:      list[UsagePattern]                            = Field(default_factory=list)
    failure_clusters:    list[FailureCluster]                          = Field(default_factory=list)
    predictions:         list[Prediction]                              = Field(default_factory=list)
    anomalies:           list[Anomaly]                                 = Field(default_factory=list)
    recommendations:     list[Recommendation]                          = Field(default_factory=list)
    
    # Statistical summary
    total_requests_analyzed: int               = Field(default=0, ge=0)
    total_proxies_analyzed:  int               = Field(default=0, ge=0)
    analysis_duration_seconds: float           = Field(default=0.0, ge=0.0)
    
    # Time-series data for visualization
    time_series_data: list[TimeSeriesData]     = Field(default_factory=list)
    
    # Metadata
    generated_by:     str                      = Field(default="ProxyWhirl Analytics Engine")
    created_at:       datetime                 = Field(default_factory=datetime.now)
    
    # Export metadata
    export_formats_available: list[ExportFormat] = Field(default_factory=list)


# ============================================================================
# CONFIGURATION MODELS
# ============================================================================


class AnalysisConfig(BaseModel):
    """Configuration for analytics engine.
    
    Provides comprehensive configuration options for all analytics features
    including time windows, thresholds, and caching.
    """

    model_config = ConfigDict(frozen=False)

    # Time window configuration
    lookback_days:    int                      = Field(default=30, ge=1, description="Days of historical data to analyze")
    
    # Performance analysis thresholds
    min_success_rate: float                    = Field(default=0.7, ge=0.0, le=1.0, description="Minimum acceptable success rate")
    max_avg_latency_ms: float                  = Field(default=5000.0, ge=0.0, description="Maximum acceptable average latency")
    min_uptime_percentage: float               = Field(default=95.0, ge=0.0, le=100.0, description="Minimum acceptable uptime")
    
    # Performance scoring weights (must sum to 1.0)
    success_rate_weight: float                 = Field(default=0.4, ge=0.0, le=1.0)
    latency_weight:      float                 = Field(default=0.3, ge=0.0, le=1.0)
    uptime_weight:       float                 = Field(default=0.3, ge=0.0, le=1.0)
    
    # Pattern detection thresholds
    peak_hour_threshold: float                 = Field(default=1.5, ge=1.0, description="Multiplier for peak hour detection")
    anomaly_threshold:   float                 = Field(default=3.0, ge=1.0, description="Standard deviations for anomaly detection")
    min_pattern_confidence: float              = Field(default=0.8, ge=0.0, le=1.0)
    
    # Failure analysis configuration
    min_cluster_size:    int                   = Field(default=5, ge=2, description="Minimum failures to form a cluster")
    failure_correlation_threshold: float       = Field(default=0.6, ge=0.0, le=1.0)
    
    # Predictive analytics configuration
    prediction_horizon_days: int               = Field(default=7, ge=1, description="Days to forecast into future")
    min_training_days:       int               = Field(default=14, ge=7, description="Minimum days of data for training")
    prediction_confidence:   float             = Field(default=0.95, ge=0.0, le=1.0)
    
    # Cost analysis configuration
    default_cost_per_proxy_per_month: float    = Field(default=10.0, ge=0.0, description="Default proxy cost")
    
    # Caching configuration
    cache_results:       bool                  = Field(default=True, description="Enable result caching")
    cache_ttl_seconds:   int                   = Field(default=3600, ge=60, description="Cache TTL in seconds")
    
    # Performance limits
    max_proxies_analyzed: Optional[int]        = Field(default=None, ge=1, description="Maximum proxies to analyze")
    max_records_per_query: int                 = Field(default=1_000_000, ge=1000, description="Maximum records per query")
    
    # Export configuration
    include_visualizations: bool               = Field(default=True, description="Include visualization data in reports")
    export_formats:         list[ExportFormat] = Field(default_factory=lambda: [ExportFormat.JSON])


class AnalyticsQuery(BaseModel):
    """Query parameters for analytics analysis.
    
    Provides flexible filtering and configuration for analytics queries.
    """

    model_config = ConfigDict(frozen=False)

    # Time range
    start_time:       Optional[datetime]       = None
    end_time:         Optional[datetime]       = None
    
    # Filters
    proxy_ids:        Optional[list[str]]      = None
    pools:            Optional[list[str]]      = None
    regions:          Optional[list[str]]      = None
    
    # Analysis configuration
    analysis_types:   list[AnalysisType]       = Field(default_factory=lambda: [AnalysisType.PERFORMANCE])
    include_recommendations: bool              = Field(default=True)
    include_predictions:     bool              = Field(default=False)
    
    # Result limits
    top_n_performers: int                      = Field(default=10, ge=1)
    top_n_clusters:   int                      = Field(default=5, ge=1)
    
    # Configuration override
    config:           Optional[AnalysisConfig] = None
