"""
Data models for ProxyWhirl analytics engine using Pydantic v2.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# ENUMS
# ============================================================================


class AnalysisType(str, Enum):
    """Types of analytics analysis."""

    PERFORMANCE      = "performance"
    USAGE_PATTERNS   = "usage_patterns"
    FAILURE_ANALYSIS = "failure_analysis"
    COST_ROI         = "cost_roi"
    PREDICTIVE       = "predictive"
    COMPREHENSIVE    = "comprehensive"


class ExportFormat(str, Enum):
    """Export format options for analytics reports."""

    CSV     = "csv"
    JSON    = "json"
    PDF     = "pdf"
    PARQUET = "parquet"


class TrendDirection(str, Enum):
    """Direction of trends in metrics."""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE     = "stable"
    VOLATILE   = "volatile"


class AnomalyType(str, Enum):
    """Types of anomalies detected in data."""

    SPIKE          = "spike"
    DROP           = "drop"
    OUTLIER        = "outlier"
    PATTERN_BREACH = "pattern_breach"


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations."""

    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


# ============================================================================
# CONFIGURATION MODELS
# ============================================================================


class AnalysisConfig(BaseModel):
    """Configuration for analytics engine."""

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # Time range configuration
    lookback_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of days to look back for analysis",
    )
    
    # Performance thresholds
    min_success_rate: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Minimum acceptable success rate threshold",
    )
    
    max_latency_ms: int = Field(
        default=5000,
        ge=0,
        description="Maximum acceptable latency in milliseconds",
    )
    
    min_uptime_hours: int = Field(
        default=24,
        ge=0,
        description="Minimum uptime required in hours",
    )
    
    # Pattern detection configuration
    anomaly_std_threshold: float = Field(
        default=3.0,
        gt=0.0,
        description="Standard deviations for anomaly detection (z-score)",
    )
    
    peak_hour_percentile: float = Field(
        default=0.90,
        ge=0.0,
        le=1.0,
        description="Percentile threshold for peak hour identification",
    )
    
    # Clustering configuration
    min_cluster_size: int = Field(
        default=3,
        ge=2,
        description="Minimum number of items to form a failure cluster",
    )
    
    # Caching configuration
    cache_results: bool = Field(
        default=True,
        description="Whether to cache analysis results",
    )
    
    cache_ttl_seconds: int = Field(
        default=3600,
        ge=0,
        description="Cache time-to-live in seconds",
    )
    
    # Performance configuration
    max_records: int = Field(
        default=1_000_000,
        ge=1,
        description="Maximum records to process in single analysis",
    )
    
    parallel_processing: bool = Field(
        default=True,
        description="Enable parallel processing for large datasets",
    )


# ============================================================================
# METRICS AND SCORES
# ============================================================================


class ProxyPerformanceMetrics(BaseModel):
    """Performance metrics for a single proxy."""

    model_config = ConfigDict(frozen=False)

    proxy_id: str = Field(description="Unique proxy identifier")
    proxy_url: str = Field(description="Proxy URL")
    
    # Core metrics
    total_requests: int = Field(default=0, ge=0)
    successful_requests: int = Field(default=0, ge=0)
    failed_requests: int = Field(default=0, ge=0)
    
    # Success rate
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Latency metrics (milliseconds)
    avg_latency_ms: float = Field(default=0.0, ge=0.0)
    min_latency_ms: float = Field(default=0.0, ge=0.0)
    max_latency_ms: float = Field(default=0.0, ge=0.0)
    p50_latency_ms: float = Field(default=0.0, ge=0.0)
    p95_latency_ms: float = Field(default=0.0, ge=0.0)
    p99_latency_ms: float = Field(default=0.0, ge=0.0)
    
    # Availability metrics
    uptime_hours: float = Field(default=0.0, ge=0.0)
    downtime_hours: float = Field(default=0.0, ge=0.0)
    availability_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Metadata
    first_seen: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)
    region: Optional[str] = Field(default=None)
    pool: Optional[str] = Field(default=None)


class PerformanceScore(BaseModel):
    """Calculated performance score for a proxy."""

    model_config = ConfigDict(frozen=False)

    proxy_id: str = Field(description="Unique proxy identifier")
    
    # Component scores (0.0 to 1.0)
    success_rate_score: float = Field(ge=0.0, le=1.0)
    latency_score: float = Field(ge=0.0, le=1.0)
    availability_score: float = Field(ge=0.0, le=1.0)
    
    # Overall composite score (0.0 to 1.0)
    overall_score: float = Field(ge=0.0, le=1.0)
    
    # Weights used for calculation
    weights: dict[str, float] = Field(
        default={"success_rate": 0.5, "latency": 0.3, "availability": 0.2}
    )
    
    # Ranking
    rank: Optional[int] = Field(default=None, ge=1)
    percentile: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    
    # Performance classification
    is_top_performer: bool = Field(default=False)
    is_underperformer: bool = Field(default=False)
    
    # Recommendations
    recommendations: list[str] = Field(default_factory=list)


# ============================================================================
# PATTERN DETECTION
# ============================================================================


class UsagePattern(BaseModel):
    """Detected usage pattern in proxy traffic."""

    model_config = ConfigDict(frozen=False)

    pattern_id: UUID = Field(default_factory=uuid4)
    pattern_type: str = Field(description="Type of pattern (e.g., 'peak_hours', 'daily_cycle')")
    
    # Pattern characteristics
    description: str = Field(description="Human-readable pattern description")
    confidence: float = Field(ge=0.0, le=1.0, description="Pattern confidence score")
    
    # Time-based patterns
    peak_hours: Optional[list[int]] = Field(
        default=None,
        description="Hours of day with peak usage (0-23)",
    )
    
    peak_days: Optional[list[int]] = Field(
        default=None,
        description="Days of week with peak usage (0=Monday, 6=Sunday)",
    )
    
    # Volume patterns
    avg_requests_per_hour: Optional[float] = Field(default=None, ge=0.0)
    peak_requests_per_hour: Optional[float] = Field(default=None, ge=0.0)
    
    # Geographic patterns
    top_regions: Optional[list[tuple[str, int]]] = Field(
        default=None,
        description="Top regions by request count",
    )
    
    # Trend information
    trend: Optional[TrendDirection] = None
    
    # Detection metadata
    detected_at: datetime = Field(default_factory=datetime.now)
    data_points: int = Field(ge=0, description="Number of data points analyzed")
    time_range_start: datetime
    time_range_end: datetime


class Anomaly(BaseModel):
    """Detected anomaly in metrics."""

    model_config = ConfigDict(frozen=False)

    anomaly_id: UUID = Field(default_factory=uuid4)
    anomaly_type: AnomalyType
    
    # Anomaly details
    metric_name: str = Field(description="Name of metric with anomaly")
    expected_value: float = Field(description="Expected value based on historical data")
    actual_value: float = Field(description="Actual observed value")
    deviation: float = Field(description="Deviation from expected (in std devs or percent)")
    
    # Severity
    severity: float = Field(ge=0.0, le=1.0, description="Anomaly severity score")
    is_critical: bool = Field(default=False)
    
    # Context
    timestamp: datetime = Field(default_factory=datetime.now)
    affected_proxies: list[str] = Field(default_factory=list)
    
    # Analysis
    possible_causes: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


# ============================================================================
# FAILURE ANALYSIS
# ============================================================================


class FailureCluster(BaseModel):
    """Group of related failures with common characteristics."""

    model_config = ConfigDict(frozen=False)

    cluster_id: UUID = Field(default_factory=uuid4)
    
    # Cluster characteristics
    size: int = Field(ge=1, description="Number of failures in cluster")
    failure_rate: float = Field(ge=0.0, le=1.0)
    
    # Common factors
    common_proxies: list[str] = Field(default_factory=list)
    common_domains: list[str] = Field(default_factory=list)
    common_error_types: list[str] = Field(default_factory=list)
    common_regions: list[str] = Field(default_factory=list)
    
    # Time characteristics
    first_occurrence: datetime
    last_occurrence: datetime
    peak_time: Optional[datetime] = None
    
    # Impact
    affected_proxy_count: int = Field(ge=0)
    affected_domain_count: int = Field(ge=0)
    total_failed_requests: int = Field(ge=0)
    
    # Root cause analysis
    suspected_root_causes: list[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    
    # Correlation metrics
    proxy_correlation: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    time_correlation: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    domain_correlation: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    
    # Recommendations
    remediation_steps: list[str] = Field(default_factory=list)
    priority: RecommendationPriority = RecommendationPriority.MEDIUM


class FailureAnalysisResult(BaseModel):
    """Results of failure pattern analysis."""

    model_config = ConfigDict(frozen=False)

    analysis_id: UUID = Field(default_factory=uuid4)
    
    # Overall statistics
    total_failures: int = Field(ge=0)
    total_clusters: int = Field(ge=0)
    clustered_failures: int = Field(ge=0)
    unclustered_failures: int = Field(ge=0)
    clustering_effectiveness: float = Field(
        ge=0.0,
        le=1.0,
        description="Percentage of failures successfully clustered",
    )
    
    # Clusters
    clusters: list[FailureCluster] = Field(default_factory=list)
    
    # Top failure factors
    top_failing_proxies: list[tuple[str, int]] = Field(default_factory=list)
    top_failing_domains: list[tuple[str, int]] = Field(default_factory=list)
    top_error_types: list[tuple[str, int]] = Field(default_factory=list)
    
    # Time range
    analysis_start: datetime
    analysis_end: datetime
    
    # Overall recommendations
    recommendations: list[str] = Field(default_factory=list)


# ============================================================================
# COST AND ROI
# ============================================================================


class CostMetrics(BaseModel):
    """Cost and ROI metrics for proxies."""

    model_config = ConfigDict(frozen=False)

    # Cost breakdown
    total_cost: float = Field(ge=0.0, description="Total cost in currency units")
    cost_per_request: float = Field(ge=0.0)
    cost_per_successful_request: float = Field(ge=0.0)
    
    # Volume metrics
    total_requests: int = Field(ge=0)
    successful_requests: int = Field(ge=0)
    
    # ROI metrics
    roi_percent: Optional[float] = None
    cost_efficiency_score: float = Field(ge=0.0, le=1.0)
    
    # Source comparison
    source: str = Field(description="Proxy source identifier")
    rank_by_cost_effectiveness: Optional[int] = Field(default=None, ge=1)
    
    # Time period
    period_start: datetime
    period_end: datetime


class CostForecast(BaseModel):
    """Projected future costs based on trends."""

    model_config = ConfigDict(frozen=False)

    forecast_id: UUID = Field(default_factory=uuid4)
    
    # Forecast period
    forecast_start: datetime
    forecast_end: datetime
    
    # Projected costs
    projected_total_cost: float = Field(ge=0.0)
    projected_requests: int = Field(ge=0)
    projected_cost_per_request: float = Field(ge=0.0)
    
    # Confidence
    confidence_interval_lower: float = Field(ge=0.0)
    confidence_interval_upper: float = Field(ge=0.0)
    confidence_level: float = Field(ge=0.0, le=1.0, default=0.95)
    
    # Trend
    trend: TrendDirection
    trend_strength: float = Field(ge=0.0, le=1.0)
    
    # Recommendations
    optimization_opportunities: list[str] = Field(default_factory=list)
    estimated_savings: Optional[float] = Field(default=None, ge=0.0)


# ============================================================================
# PREDICTIVE ANALYTICS
# ============================================================================


class TimeSeriesData(BaseModel):
    """Time-series data point for analysis."""

    model_config = ConfigDict(frozen=False)

    timestamp: datetime
    value: float
    metric_name: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Prediction(BaseModel):
    """Forecast prediction for future metric values."""

    model_config = ConfigDict(frozen=False)

    prediction_id: UUID = Field(default_factory=uuid4)
    
    # Prediction details
    metric_name: str = Field(description="Name of metric being predicted")
    forecast_horizon_days: int = Field(ge=1, description="Days into future")
    
    # Predicted values
    predictions: list[TimeSeriesData] = Field(default_factory=list)
    
    # Statistical measures
    mean_prediction: float
    median_prediction: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    
    # Model accuracy
    model_type: str = Field(description="Type of prediction model used")
    accuracy_metrics: dict[str, float] = Field(
        default_factory=dict,
        description="MAE, RMSE, MAPE, etc.",
    )
    
    # Trend analysis
    detected_trend: TrendDirection
    seasonality_detected: bool = Field(default=False)
    
    # Capacity recommendations
    capacity_recommendations: list[str] = Field(default_factory=list)
    recommended_pool_size: Optional[int] = Field(default=None, ge=0)
    
    # Metadata
    trained_on_data_points: int = Field(ge=0)
    training_period_start: datetime
    training_period_end: datetime
    prediction_generated_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# ANALYSIS REPORTS
# ============================================================================


class AnalysisReport(BaseModel):
    """Comprehensive analysis report with findings and recommendations."""

    model_config = ConfigDict(frozen=False)

    report_id: UUID = Field(default_factory=uuid4)
    analysis_type: AnalysisType
    
    # Report metadata
    title: str = Field(description="Report title")
    description: str = Field(description="Report description")
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str = Field(default="ProxyWhirl Analytics Engine")
    
    # Analysis period
    analysis_start: datetime
    analysis_end: datetime
    total_duration: timedelta
    
    # Configuration
    config: AnalysisConfig
    
    # Results (polymorphic based on analysis type)
    performance_results: Optional[dict[str, ProxyPerformanceMetrics]] = None
    performance_scores: Optional[list[PerformanceScore]] = None
    
    usage_patterns: Optional[list[UsagePattern]] = None
    anomalies: Optional[list[Anomaly]] = None
    
    failure_analysis: Optional[FailureAnalysisResult] = None
    
    cost_metrics: Optional[list[CostMetrics]] = None
    cost_forecast: Optional[CostForecast] = None
    
    predictions: Optional[list[Prediction]] = None
    
    # Summary statistics
    summary_stats: dict[str, Any] = Field(default_factory=dict)
    
    # Key findings
    key_findings: list[str] = Field(default_factory=list)
    
    # Recommendations
    recommendations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of recommendations with priority and details",
    )
    
    # Visualizations (optional)
    visualization_data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Data prepared for visualization (charts, graphs)",
    )
    
    # Export info
    exported_to: Optional[list[str]] = Field(
        default=None,
        description="List of export locations/formats",
    )

    @field_validator("total_duration", mode="before")
    @classmethod
    def calculate_duration(cls, v: Any, info: Any) -> timedelta:
        """Calculate duration if not provided."""
        if isinstance(v, timedelta):
            return v
        # If duration not provided, calculate from start/end times
        if hasattr(info, "data"):
            data = info.data
            if "analysis_start" in data and "analysis_end" in data:
                return data["analysis_end"] - data["analysis_start"]
        return timedelta(seconds=0)


# ============================================================================
# QUERY AND FILTER MODELS
# ============================================================================


class AnalyticsQuery(BaseModel):
    """Query parameters for analytics requests."""

    model_config = ConfigDict(frozen=False)

    # Analysis type
    analysis_types: list[AnalysisType] = Field(
        default=[AnalysisType.PERFORMANCE],
        description="Types of analysis to perform",
    )
    
    # Time range
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    lookback_days: Optional[int] = Field(default=30, ge=1, le=365)
    
    # Filters
    proxy_ids: Optional[list[str]] = Field(default=None)
    pools: Optional[list[str]] = Field(default=None)
    regions: Optional[list[str]] = Field(default=None)
    sources: Optional[list[str]] = Field(default=None)
    
    # Options
    include_visualizations: bool = Field(default=False)
    export_formats: list[ExportFormat] = Field(default_factory=list)
    
    # Configuration override
    config_overrides: Optional[dict[str, Any]] = None


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "AnalysisType",
    "ExportFormat",
    "TrendDirection",
    "AnomalyType",
    "RecommendationPriority",
    # Configuration
    "AnalysisConfig",
    # Metrics and Scores
    "ProxyPerformanceMetrics",
    "PerformanceScore",
    # Pattern Detection
    "UsagePattern",
    "Anomaly",
    # Failure Analysis
    "FailureCluster",
    "FailureAnalysisResult",
    # Cost and ROI
    "CostMetrics",
    "CostForecast",
    # Predictive
    "TimeSeriesData",
    "Prediction",
    # Reports
    "AnalysisReport",
    # Query
    "AnalyticsQuery",
]
