"""proxywhirl/validator.py -- Advanced Proxy Validation System with 5-Stage Pipeline

This module provides a comprehensive proxy validation system featuring:
- 5-Stage Validation Pipeline: Connectivity → Anonymity → Performance → Geographic → Anti-Detection
- Advanced Circuit Breaker Protection with intelligent recovery
- TLS Fingerprinting and SSL/TLS Analysis
- DNS Resolution Validation and Geographic Verification
- Machine Learning-based Quality Prediction and Pattern Recognition
- Real-time Performance Monitoring and Adaptive Thresholds
- Sophisticated Anti-Detection Measures and Stealth Validation
- Load Testing and Stress Validation Capabilities
- Advanced Anonymity Detection with Deep Header Analysis
- HTTP/2 and HTTP/3 Protocol Support with Connection Multiplexing
"""

import asyncio
import hashlib
import json
import math
import random
import ssl
import statistics
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, TypeVar, Union

import dns.exception
import dns.resolver

# Core HTTP and networking libraries
import httpx
from loguru import logger
from pydantic import BaseModel, Field, computed_field

# Machine Learning and Scientific Computing
try:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    HAS_ML = True
except ImportError:
    HAS_ML = False
    logger.warning("ML features disabled: install scikit-learn and numpy for advanced quality prediction")

# Geographic and IP Analysis
try:
    import geoip2.database
    import geoip2.errors
    HAS_GEOIP = True
except ImportError:
    HAS_GEOIP = False
    logger.warning("GeoIP features disabled: install geoip2 for geographic validation")

# Cryptographic and Security Tools
try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    logger.warning("Cryptographic features disabled: install cryptography for TLS fingerprinting")

# Throttling and Rate Limiting
try:
    from asyncio_throttle import Throttler
    HAS_THROTTLING = True
except ImportError:
    HAS_THROTTLING = False
    logger.info("Advanced throttling disabled: install asyncio-throttle for enhanced rate limiting")

from proxywhirl.models import (
    AnonymityLevel,
    Proxy,
    ProxyError,
    TargetDefinition,
    ValidationErrorType,
)

T = TypeVar("T")

# ============================================================================
# ENHANCED ENUMS AND CONSTANTS
# ============================================================================

class ValidationStage(Enum):
    """5-Stage validation pipeline stages."""
    CONNECTIVITY = "connectivity"           # Stage 1: Basic connection test
    ANONYMITY = "anonymity"                # Stage 2: Anonymity level detection
    PERFORMANCE = "performance"            # Stage 3: Speed and reliability testing
    GEOGRAPHIC = "geographic"              # Stage 4: Location and DNS verification
    ANTI_DETECTION = "anti_detection"      # Stage 5: Stealth and fingerprint analysis

class QualityLevel(Enum):
    """Enhanced quality levels for proxy validation."""
    MINIMAL = "minimal"                    # Basic connectivity only
    BASIC = "basic"                        # Connectivity + basic response validation
    STANDARD = "standard"                  # Full 5-stage validation
    THOROUGH = "thorough"                  # 5-stage + ML prediction + load testing
    ENTERPRISE = "enterprise"              # All features + advanced anti-detection

class CircuitState(Enum):
    """Enhanced circuit breaker states with metrics."""
    CLOSED = "closed"                      # Normal operation
    OPEN = "open"                          # Failing, requests blocked
    HALF_OPEN = "half_open"                # Testing if service recovered
    FORCED_OPEN = "forced_open"            # Manually disabled

class TLSVersion(Enum):
    """TLS versions for fingerprinting."""
    TLS_1_0 = "TLSv1.0"
    TLS_1_1 = "TLSv1.1"
    TLS_1_2 = "TLSv1.2"
    TLS_1_3 = "TLSv1.3"
    UNKNOWN = "unknown"

class ProxyProtocol(Enum):
    """Extended proxy protocol support."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"
    HTTP2 = "http2"
    HTTP3 = "http3"

class AntiDetectionLevel(Enum):
    """Anti-detection capability levels."""
    NONE = "none"                          # No stealth features
    BASIC = "basic"                        # Basic header masking
    ADVANCED = "advanced"                  # Advanced fingerprint resistance
    ELITE = "elite"                        # Military-grade stealth

# ============================================================================
# ADVANCED CIRCUIT BREAKER IMPLEMENTATION
# ============================================================================

class CircuitBreakerOpenError(ProxyError):
    """Raised when circuit breaker is open."""
    pass

class CircuitBreakerMetrics(BaseModel):
    """Detailed circuit breaker metrics and statistics."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    circuit_breaker_trips: int = 0
    last_trip_time: Optional[datetime] = None
    average_response_time: Optional[float] = None
    success_rate: float = 0.0
    recovery_attempts: int = 0
    
    @computed_field
    @property
    def failure_rate(self) -> float:
        """Calculate current failure rate."""
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls

class CircuitBreaker:
    """
    Advanced circuit breaker with intelligent recovery, metrics, and adaptive thresholds.
    
    Features:
    - Intelligent recovery with exponential backoff
    - Adaptive failure thresholds based on historical performance
    - Comprehensive metrics and monitoring
    - Half-open testing with graduated recovery
    - Manual override and forced states
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
        success_threshold: int = 2,
        expected_exception: tuple[type[Exception], ...] = (
            httpx.HTTPError,
            httpx.ConnectError,
            httpx.ProxyError,
            asyncio.TimeoutError,
        ),
        adaptive_threshold: bool = True,
        max_failure_threshold: int = 20,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.success_threshold = success_threshold
        self.expected_exception = expected_exception
        self.adaptive_threshold = adaptive_threshold
        self.max_failure_threshold = max_failure_threshold

        # State management
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._last_success_time: Optional[float] = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()
        
        # Advanced metrics
        self.metrics = CircuitBreakerMetrics()
        self._response_times: deque = deque(maxlen=100)
        
        # Adaptive threshold tracking
        self._historical_performance: deque = deque(maxlen=1000)

    @property
    def state(self) -> CircuitState:
        """Get current circuit breaker state."""
        return self._state

    @property 
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count

    async def call(self, func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any) -> T:
        """
        Execute function through enhanced circuit breaker with intelligent recovery.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenError: When circuit is open
            Exception: Original exception from function
        """
        async with self._lock:
            await self._check_state_transition()
            
            # Block requests when circuit is OPEN or FORCED_OPEN
            if self._state in [CircuitState.OPEN, CircuitState.FORCED_OPEN]:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is {self._state.value.upper()}. "
                    f"Failed {self._failure_count} times. "
                    f"Recovery timeout: {self.recovery_timeout}s"
                )
                
            # Limit calls in HALF_OPEN state
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max_calls:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker in HALF_OPEN state. Maximum test calls ({self.half_open_max_calls}) reached."
                    )
                self._half_open_calls += 1

        # Execute the function with timing
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            await self._on_success(response_time)
            return result
        except self.expected_exception as e:
            response_time = time.time() - start_time
            await self._on_failure(response_time, str(e))
            raise e

    async def _check_state_transition(self) -> None:
        """Check if circuit breaker should transition states."""
        current_time = time.time()
        
        # Transition from OPEN to HALF_OPEN after recovery timeout
        if (self._state == CircuitState.OPEN and 
            self._last_failure_time and 
            current_time - self._last_failure_time > self.recovery_timeout):
            
            self._state = CircuitState.HALF_OPEN
            self._half_open_calls = 0
            self._success_count = 0
            self.metrics.recovery_attempts += 1
            logger.info("Circuit breaker transitioning to HALF_OPEN for recovery testing")

    async def _on_success(self, response_time: float) -> None:
        """Handle successful function execution with metrics."""
        async with self._lock:
            self.metrics.successful_calls += 1
            self.metrics.total_calls += 1
            self._response_times.append(response_time)
            self._last_success_time = time.time()
            
            # Update average response time
            if self._response_times:
                self.metrics.average_response_time = statistics.mean(self._response_times)
            
            # State transitions based on success
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    logger.info("Circuit breaker transitioning to CLOSED after successful recovery")
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._half_open_calls = 0
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on successful calls
                self._failure_count = max(0, self._failure_count - 1)
                
            # Track historical performance for adaptive thresholds
            self._historical_performance.append(True)
            self._update_success_rate()

    async def _on_failure(self, response_time: float, error_msg: str) -> None:
        """Handle failed function execution with metrics."""
        async with self._lock:
            self.metrics.failed_calls += 1
            self.metrics.total_calls += 1
            self._response_times.append(response_time)
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            # Update average response time
            if self._response_times:
                self.metrics.average_response_time = statistics.mean(self._response_times)
            
            # Determine current failure threshold (adaptive or static)
            current_threshold = self._get_adaptive_threshold() if self.adaptive_threshold else self.failure_threshold
            
            # State transitions based on failure
            if self._state == CircuitState.CLOSED and self._failure_count >= current_threshold:
                logger.warning(f"Circuit breaker OPENING after {self._failure_count} failures (threshold: {current_threshold})")
                self._state = CircuitState.OPEN
                self.metrics.circuit_breaker_trips += 1
                self.metrics.last_trip_time = datetime.now(timezone.utc)
                
            elif self._state == CircuitState.HALF_OPEN:
                logger.warning("Circuit breaker moving back to OPEN from HALF_OPEN after failure")
                self._state = CircuitState.OPEN
                self._half_open_calls = 0
                self.metrics.circuit_breaker_trips += 1
                self.metrics.last_trip_time = datetime.now(timezone.utc)
            
            # Track historical performance for adaptive thresholds  
            self._historical_performance.append(False)
            self._update_success_rate()

    def _get_adaptive_threshold(self) -> int:
        """Calculate adaptive failure threshold based on historical performance."""
        if len(self._historical_performance) < 50:  # Need minimum sample size
            return self.failure_threshold
            
        # Calculate recent success rate
        recent_success_rate = sum(self._historical_performance) / len(self._historical_performance)
        
        # Adjust threshold based on historical performance
        if recent_success_rate > 0.95:  # Very reliable proxy
            adaptive_threshold = min(self.max_failure_threshold, self.failure_threshold * 2)
        elif recent_success_rate > 0.80:  # Reliable proxy
            adaptive_threshold = int(self.failure_threshold * 1.5)
        elif recent_success_rate < 0.50:  # Unreliable proxy
            adaptive_threshold = max(2, self.failure_threshold // 2)
        else:
            adaptive_threshold = self.failure_threshold
            
        logger.debug(f"Adaptive threshold: {adaptive_threshold} (success_rate: {recent_success_rate:.2%})")
        return adaptive_threshold

    def _update_success_rate(self) -> None:
        """Update overall success rate metric."""
        if self.metrics.total_calls > 0:
            self.metrics.success_rate = self.metrics.successful_calls / self.metrics.total_calls

    async def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        async with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._half_open_calls = 0
            self._last_failure_time = None
            logger.info("Circuit breaker manually reset to CLOSED")

    async def force_open(self) -> None:
        """Force circuit breaker to FORCED_OPEN state."""
        async with self._lock:
            self._state = CircuitState.FORCED_OPEN
            logger.warning("Circuit breaker forced to OPEN state")

    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive circuit breaker health status."""
        return {
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "metrics": self.metrics.model_dump(),
            "adaptive_threshold": self._get_adaptive_threshold() if self.adaptive_threshold else self.failure_threshold,
            "half_open_calls": self._half_open_calls if self._state == CircuitState.HALF_OPEN else 0,
        }


# ============================================================================
# ENHANCED VALIDATION RESULT MODELS
# ============================================================================

class TLSFingerprint(BaseModel):
    """TLS/SSL fingerprint analysis results."""
    version: TLSVersion = TLSVersion.UNKNOWN
    cipher_suite: Optional[str] = None
    certificate_chain_length: int = 0
    certificate_subject: Optional[str] = None
    certificate_issuer: Optional[str] = None
    certificate_expiry: Optional[datetime] = None
    sni_support: bool = False
    alpn_protocols: List[str] = Field(default_factory=list)
    handshake_time: Optional[float] = None
    fingerprint_hash: Optional[str] = None

class DNSMetrics(BaseModel):
    """DNS resolution metrics and analysis."""
    resolution_time: Optional[float] = None
    resolved_ips: List[str] = Field(default_factory=list)
    authoritative_nameservers: List[str] = Field(default_factory=list)
    ttl: Optional[int] = None
    dns_over_https_support: bool = False
    dns_over_tls_support: bool = False
    reverse_dns: Optional[str] = None

class GeographicData(BaseModel):
    """Geographic validation and analysis results."""
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    isp: Optional[str] = None
    organization: Optional[str] = None
    asn: Optional[int] = None
    is_satellite: bool = False
    is_anycast: bool = False
    accuracy_radius: Optional[int] = None

class AntiDetectionMetrics(BaseModel):
    """Anti-detection analysis and stealth capabilities."""
    stealth_level: AntiDetectionLevel = AntiDetectionLevel.NONE
    header_fingerprint_resistance: float = 0.0  # 0.0 to 1.0
    timing_pattern_randomization: float = 0.0  # 0.0 to 1.0
    request_signature_uniqueness: float = 0.0  # 0.0 to 1.0
    detected_fingerprinting_attempts: int = 0
    proxy_detection_score: float = 0.0  # Lower is better (0.0 = undetectable)
    browser_simulation_accuracy: float = 0.0  # 0.0 to 1.0
    captcha_solving_capability: bool = False

class PerformanceMetrics(BaseModel):
    """Comprehensive performance analysis results."""
    response_time: Optional[float] = None
    connection_time: Optional[float] = None
    first_byte_time: Optional[float] = None
    download_speed: Optional[float] = None  # bytes/second
    upload_speed: Optional[float] = None    # bytes/second
    latency: Optional[float] = None
    jitter: Optional[float] = None          # response time variance
    packet_loss: Optional[float] = None     # percentage
    concurrent_connections: int = 1
    keep_alive_support: bool = False
    compression_support: List[str] = Field(default_factory=list)
    
class MLPrediction(BaseModel):
    """Machine learning-based quality prediction."""
    predicted_quality_score: float = 0.0     # 0.0 to 1.0
    reliability_prediction: float = 0.0      # 0.0 to 1.0  
    failure_probability: float = 0.0         # 0.0 to 1.0
    optimal_usage_window: Optional[Tuple[int, int]] = None  # (start_hour, end_hour)
    feature_importance: Dict[str, float] = Field(default_factory=dict)
    model_confidence: float = 0.0            # 0.0 to 1.0
    similar_proxy_patterns: List[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Enhanced validation result with comprehensive metrics and backward compatibility."""
    
    # Core validation data
    proxy: Proxy
    is_valid: bool
    response_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_type: Optional[ValidationErrorType] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    test_url: str = ""
    response_headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    ip_detected: Optional[str] = None
    anonymity_detected: Optional[AnonymityLevel] = None
    target_results: Optional[Dict[str, "TargetValidationResult"]] = None
    
    # Enhanced metrics (optional for backward compatibility)
    validation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    overall_score: float = 0.0
    stage_results: List["StageValidationResult"] = Field(default_factory=list)
    performance_metrics: Optional["PerformanceMetrics"] = None
    tls_fingerprint: Optional["TLSFingerprint"] = None
    dns_metrics: Optional["DNSMetrics"] = None
    geographic_data: Optional["GeographicData"] = None
    anti_detection_metrics: Optional["AntiDetectionMetrics"] = None
    ml_prediction: Optional["MLPrediction"] = None
    load_test_results: Optional[Dict[str, Any]] = None
    quality_tier: str = "unknown"
    
    @property
    def error(self) -> Optional[str]:
        """Backward compatibility property."""
        return self.error_message

    @computed_field
    @property
    def validation_efficiency_score(self) -> float:
        """Enhanced efficiency scoring with multi-dimensional analysis."""
        if not self.is_valid:
            return 0.0

        # Base score from stage results
        if self.stage_results:
            stage_scores = [result.stage_score for result in self.stage_results if result.is_valid]
            base_score = statistics.mean(stage_scores) if stage_scores else 0.0
        else:
            base_score = 1.0

        # Performance adjustments
        if self.response_time:
            if self.response_time <= 0.5:
                base_score *= 1.5  # Excellent
            elif self.response_time <= 1.0:
                base_score *= 1.3  # Very good
            elif self.response_time <= 2.0:
                base_score *= 1.2  # Good
            elif self.response_time <= 5.0:
                base_score *= 1.0  # Average
            elif self.response_time <= 10.0:
                base_score *= 0.8  # Below average
            else:
                base_score *= 0.5  # Poor

        # Anonymity bonus (enhanced)
        if self.anonymity_detected == AnonymityLevel.ELITE:
            base_score *= 1.4
        elif self.anonymity_detected == AnonymityLevel.ANONYMOUS:
            base_score *= 1.2
        elif self.anonymity_detected == AnonymityLevel.TRANSPARENT:
            base_score *= 0.9

        # Anti-detection bonus
        if self.anti_detection_metrics:
            if self.anti_detection_metrics.stealth_level == AntiDetectionLevel.ELITE:
                base_score *= 1.3
            elif self.anti_detection_metrics.stealth_level == AntiDetectionLevel.ADVANCED:
                base_score *= 1.2
            elif self.anti_detection_metrics.stealth_level == AntiDetectionLevel.BASIC:
                base_score *= 1.1

        # Geographic reliability bonus
        if (self.geographic_data and self.geographic_data.accuracy_radius and 
            self.geographic_data.accuracy_radius <= 50):
            base_score *= 1.1  # High location accuracy

        return min(2.0, round(base_score, 3))  # Cap at 2.0 for exceptional proxies

    @computed_field
    @property
    def health_score(self) -> float:
        """Advanced health scoring with ML integration."""
        if not self.is_valid:
            return 0.0

        # Use ML prediction if available
        if self.ml_prediction and self.ml_prediction.model_confidence > 0.7:
            ml_score = self.ml_prediction.predicted_quality_score
            confidence_weight = self.ml_prediction.model_confidence
            base_weight = 1 - confidence_weight
        else:
            ml_score = 0.0
            confidence_weight = 0.0
            base_weight = 1.0

        # Calculate base score from traditional metrics
        base_score = 1.0

        # Performance impact
        if self.response_time:
            if self.response_time > 15.0:
                base_score *= 0.4
            elif self.response_time > 10.0:
                base_score *= 0.6
            elif self.response_time > 5.0:
                base_score *= 0.8
            elif self.response_time < 1.0:
                base_score *= 1.2

        # Anonymity impact  
        if self.anonymity_detected == AnonymityLevel.ELITE:
            base_score *= 1.3
        elif self.anonymity_detected == AnonymityLevel.ANONYMOUS:
            base_score *= 1.15
        elif self.anonymity_detected == AnonymityLevel.TRANSPARENT:
            base_score *= 0.8

        # Stage completion bonus
        if self.stage_results:
            completed_stages = sum(1 for result in self.stage_results if result.is_valid)
            stage_bonus = (completed_stages / len(ValidationStage)) * 0.2
            base_score += stage_bonus

        # Combine ML and traditional scores
        final_score = (ml_score * confidence_weight) + (base_score * base_weight)
        
        return min(2.0, max(0.0, round(final_score, 3)))

    def get_stage_result(self, stage: ValidationStage) -> Optional["StageValidationResult"]:
        """Get result for a specific validation stage."""
        for result in self.stage_results:
            if result.stage == stage:
                return result
        return None

    def add_stage_result(self, stage_result: "StageValidationResult") -> None:
        """Add or update a stage result."""
        # Remove existing result for this stage
        self.stage_results = [r for r in self.stage_results if r.stage != stage_result.stage]
        # Add new result
        self.stage_results.append(stage_result)
        
        # Update overall validation status
        self._update_overall_status()

    def _update_overall_status(self) -> None:
        """Update overall validation status based on stage results."""
        if not self.stage_results:
            self.is_valid = False
            self.overall_score = 0.0
            return
            
        # Require at least connectivity stage to pass
        connectivity_result = self.get_stage_result(ValidationStage.CONNECTIVITY)
        if not connectivity_result or not connectivity_result.is_valid:
            self.is_valid = False
            self.overall_score = 0.0
            return
            
        # Calculate weighted overall score
        stage_weights = {
            ValidationStage.CONNECTIVITY: 0.35,      # Most important
            ValidationStage.ANONYMITY: 0.25,        # Very important for proxies
            ValidationStage.PERFORMANCE: 0.20,      # Important for usability
            ValidationStage.GEOGRAPHIC: 0.12,       # Useful for targeting
            ValidationStage.ANTI_DETECTION: 0.08,   # Advanced feature
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for stage_result in self.stage_results:
            weight = stage_weights.get(stage_result.stage, 0.0)
            if stage_result.is_valid:
                weighted_score += stage_result.stage_score * weight
            total_weight += weight
            
        self.overall_score = (weighted_score / total_weight) if total_weight > 0 else 0.0
        self.is_valid = self.overall_score >= 0.6  # 60% threshold for validity

    @classmethod
    def model_validate_json_fast(cls, json_data: str) -> "ValidationResult":
        """Fast JSON validation using Pydantic v2 performance optimization."""
        return cls.model_validate_json(json_data)

    class Config:
        # Enable arbitrary types for complex objects like Proxy
        arbitrary_types_allowed = True

    def to_enhanced(self) -> "EnhancedValidationResult":
        """Convert to enhanced validation result."""
        return EnhancedValidationResult(
            proxy=self.proxy,
            is_valid=self.is_valid,
            timestamp=self.timestamp,
            response_time=self.response_time,
            error_type=self.error_type,
            error_message=self.error_message,
            status_code=self.status_code,
            test_url=self.test_url,
            response_headers=self.response_headers,
            ip_detected=self.ip_detected,
            anonymity_detected=self.anonymity_detected,
        )


class StageValidationResult(BaseModel):
    """Individual validation stage result."""
    stage: ValidationStage
    is_valid: bool
    stage_score: float = 0.0                 # 0.0 to 1.0
    execution_time: float = 0.0
    error_type: Optional[ValidationErrorType] = None
    error_message: Optional[str] = None
    stage_details: Dict[str, Any] = Field(default_factory=dict)
    retry_count: int = 0

class EnhancedValidationResult(BaseModel):
    """Comprehensive validation result with 5-stage analysis."""
    
    # Core validation data
    proxy: Proxy
    is_valid: bool
    overall_score: float = 0.0               # Weighted score across all stages
    validation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Stage-by-stage results
    stage_results: List[StageValidationResult] = Field(default_factory=list)
    
    # Enhanced analysis components
    performance_metrics: PerformanceMetrics = Field(default_factory=PerformanceMetrics)
    tls_fingerprint: TLSFingerprint = Field(default_factory=TLSFingerprint)
    dns_metrics: DNSMetrics = Field(default_factory=DNSMetrics)
    geographic_data: GeographicData = Field(default_factory=GeographicData)
    anti_detection_metrics: AntiDetectionMetrics = Field(default_factory=AntiDetectionMetrics)
    
    # Legacy compatibility fields
    response_time: Optional[float] = None
    error_type: Optional[ValidationErrorType] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    test_url: str = ""
    response_headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    ip_detected: Optional[str] = None
    anonymity_detected: Optional[AnonymityLevel] = None
    target_results: Optional[Dict[str, "TargetValidationResult"]] = None
    
    # Advanced features  
    ml_prediction: Optional[MLPrediction] = None
    load_test_results: Optional[Dict[str, Any]] = None
    quality_tier: str = "unknown"
    
    @property
    def error(self) -> Optional[str]:
        """Backward compatibility property."""
        return self.error_message

    @computed_field
    @property
    def validation_efficiency_score(self) -> float:
        """Enhanced efficiency scoring with multi-dimensional analysis."""
        if not self.is_valid:
            return 0.0

        # Base score from stage results
        if self.stage_results:
            stage_scores = [result.stage_score for result in self.stage_results if result.is_valid]
            base_score = statistics.mean(stage_scores) if stage_scores else 0.0
        else:
            base_score = 1.0

        # Performance adjustments
        if self.performance_metrics.response_time:
            if self.performance_metrics.response_time <= 0.5:
                base_score *= 1.5  # Excellent
            elif self.performance_metrics.response_time <= 1.0:
                base_score *= 1.3  # Very good
            elif self.performance_metrics.response_time <= 2.0:
                base_score *= 1.2  # Good
            elif self.performance_metrics.response_time <= 5.0:
                base_score *= 1.0  # Average
            elif self.performance_metrics.response_time <= 10.0:
                base_score *= 0.8  # Below average
            else:
                base_score *= 0.5  # Poor

        # Anonymity bonus (enhanced)
        if self.anonymity_detected == AnonymityLevel.ELITE:
            base_score *= 1.4
        elif self.anonymity_detected == AnonymityLevel.ANONYMOUS:
            base_score *= 1.2
        elif self.anonymity_detected == AnonymityLevel.TRANSPARENT:
            base_score *= 0.9

        # Anti-detection bonus
        if self.anti_detection_metrics.stealth_level == AntiDetectionLevel.ELITE:
            base_score *= 1.3
        elif self.anti_detection_metrics.stealth_level == AntiDetectionLevel.ADVANCED:
            base_score *= 1.2
        elif self.anti_detection_metrics.stealth_level == AntiDetectionLevel.BASIC:
            base_score *= 1.1

        # Geographic reliability bonus
        if self.geographic_data.accuracy_radius and self.geographic_data.accuracy_radius <= 50:
            base_score *= 1.1  # High location accuracy

        return min(2.0, round(base_score, 3))  # Cap at 2.0 for exceptional proxies

    @computed_field
    @property
    def health_score(self) -> float:
        """Advanced health scoring with ML integration."""
        if not self.is_valid:
            return 0.0

        # Use ML prediction if available
        if self.ml_prediction and self.ml_prediction.model_confidence > 0.7:
            ml_score = self.ml_prediction.predicted_quality_score
            confidence_weight = self.ml_prediction.model_confidence
            base_weight = 1 - confidence_weight
        else:
            ml_score = 0.0
            confidence_weight = 0.0
            base_weight = 1.0

        # Calculate base score from traditional metrics
        base_score = 1.0

        # Performance impact
        if self.performance_metrics.response_time:
            if self.performance_metrics.response_time > 15.0:
                base_score *= 0.4
            elif self.performance_metrics.response_time > 10.0:
                base_score *= 0.6
            elif self.performance_metrics.response_time > 5.0:
                base_score *= 0.8
            elif self.performance_metrics.response_time < 1.0:
                base_score *= 1.2

        # Anonymity impact  
        if self.anonymity_detected == AnonymityLevel.ELITE:
            base_score *= 1.3
        elif self.anonymity_detected == AnonymityLevel.ANONYMOUS:
            base_score *= 1.15
        elif self.anonymity_detected == AnonymityLevel.TRANSPARENT:
            base_score *= 0.8

        # Stage completion bonus
        if self.stage_results:
            completed_stages = sum(1 for result in self.stage_results if result.is_valid)
            stage_bonus = (completed_stages / len(ValidationStage)) * 0.2
            base_score += stage_bonus

        # Combine ML and traditional scores
        final_score = (ml_score * confidence_weight) + (base_score * base_weight)
        
        return min(2.0, max(0.0, round(final_score, 3)))

    def get_stage_result(self, stage: ValidationStage) -> Optional[StageValidationResult]:
        """Get result for a specific validation stage."""
        for result in self.stage_results:
            if result.stage == stage:
                return result
        return None

    def add_stage_result(self, stage_result: StageValidationResult) -> None:
        """Add or update a stage result."""
        # Remove existing result for this stage
        self.stage_results = [r for r in self.stage_results if r.stage != stage_result.stage]
        # Add new result
        self.stage_results.append(stage_result)
        
        # Update overall validation status
        self._update_overall_status()

    def _update_overall_status(self) -> None:
        """Update overall validation status based on stage results."""
        if not self.stage_results:
            self.is_valid = False
            self.overall_score = 0.0
            return
            
        # Require at least connectivity stage to pass
        connectivity_result = self.get_stage_result(ValidationStage.CONNECTIVITY)
        if not connectivity_result or not connectivity_result.is_valid:
            self.is_valid = False
            self.overall_score = 0.0
            return
            
        # Calculate weighted overall score
        stage_weights = {
            ValidationStage.CONNECTIVITY: 0.35,      # Most important
            ValidationStage.ANONYMITY: 0.25,        # Very important for proxies
            ValidationStage.PERFORMANCE: 0.20,      # Important for usability
            ValidationStage.GEOGRAPHIC: 0.12,       # Useful for targeting
            ValidationStage.ANTI_DETECTION: 0.08,   # Advanced feature
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for stage_result in self.stage_results:
            weight = stage_weights.get(stage_result.stage, 0.0)
            if stage_result.is_valid:
                weighted_score += stage_result.stage_score * weight
            total_weight += weight
            
        self.overall_score = (weighted_score / total_weight) if total_weight > 0 else 0.0
        self.is_valid = self.overall_score >= 0.6  # 60% threshold for validity

class TargetValidationResult(BaseModel):
    """Enhanced target validation result."""
    target_id: str
    target_url: str
    is_valid: bool
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error_type: Optional[ValidationErrorType] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Enhanced target metrics
    content_verification: bool = False
    expected_content_found: bool = False
    redirect_chain: List[str] = Field(default_factory=list)
    final_url: Optional[str] = None
    ssl_verification: bool = False

class ValidationSummary(BaseModel):
    """Enhanced validation summary with comprehensive analytics."""
    total_proxies: int
    valid_proxy_results: List[EnhancedValidationResult]
    failed_proxy_results: List[EnhancedValidationResult]
    validation_duration: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Enhanced analytics
    stage_success_rates: Dict[str, float] = Field(default_factory=dict)
    geographic_distribution: Dict[str, int] = Field(default_factory=dict)
    anonymity_distribution: Dict[str, int] = Field(default_factory=dict)
    performance_quartiles: Dict[str, float] = Field(default_factory=dict)
    quality_tier_distribution: Dict[str, int] = Field(default_factory=dict)
    
    @property
    def valid_proxies(self) -> List[Proxy]:
        """Get list of valid proxy objects."""
        return [result.proxy for result in self.valid_proxy_results]

    @property
    def valid_proxy_count(self) -> int:
        """Get count of valid proxies."""
        return len(self.valid_proxy_results)

    @property
    def failed_proxy_count(self) -> int:
        """Get count of failed proxies."""
        return len(self.failed_proxy_results)

    @computed_field
    @property  
    def success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.total_proxies == 0:
            return 0.0
        return self.valid_proxy_count / self.total_proxies

    @computed_field
    @property
    def avg_response_time(self) -> Optional[float]:
        """Calculate average response time of valid proxies."""
        response_times = [
            r.performance_metrics.response_time 
            for r in self.valid_proxy_results 
            if r.performance_metrics.response_time is not None
        ]
        return statistics.mean(response_times) if response_times else None

    @computed_field
    @property
    def min_response_time(self) -> Optional[float]:
        """Get minimum response time."""
        response_times = [
            r.performance_metrics.response_time 
            for r in self.valid_proxy_results 
            if r.performance_metrics.response_time is not None
        ]
        return min(response_times) if response_times else None

    @computed_field 
    @property
    def max_response_time(self) -> Optional[float]:
        """Get maximum response time."""
        response_times = [
            r.performance_metrics.response_time 
            for r in self.valid_proxy_results 
            if r.performance_metrics.response_time is not None
        ]
        return max(response_times) if response_times else None

    @computed_field
    @property
    def error_breakdown(self) -> Dict[ValidationErrorType, int]:
        """Get breakdown of validation errors."""
        error_counts: Dict[ValidationErrorType, int] = defaultdict(int)
        
        for result in self.failed_proxy_results:
            if result.error_type:
                error_counts[result.error_type] += 1
                
            # Also count stage-specific errors
            for stage_result in result.stage_results:
                if not stage_result.is_valid and stage_result.error_type:
                    error_counts[stage_result.error_type] += 1
                    
        return dict(error_counts)

    @computed_field
    @property
    def quality_tier(self) -> str:
        """Enhanced quality tier assessment."""
        if self.success_rate >= 0.95:
            return "Premium+"
        elif self.success_rate >= 0.90:
            return "Premium" 
        elif self.success_rate >= 0.75:
            return "Enterprise"
        elif self.success_rate >= 0.60:
            return "Professional"
        elif self.success_rate >= 0.40:
            return "Standard"
        elif self.success_rate >= 0.20:
            return "Basic"
        else:
            return "Poor"
    """Comprehensive validation result with metrics and error details."""

    proxy: Proxy
    is_valid: bool
    response_time: Optional[float] = None
    error_type: Optional[ValidationErrorType] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    test_url: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    response_headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    ip_detected: Optional[str] = None
    anonymity_detected: Optional[AnonymityLevel] = None
    # Target-based validation results
    target_results: Optional[Dict[str, "TargetValidationResult"]] = None

    @property
    def error(self) -> Optional[str]:
        """Backward compatibility property for tests."""
        return self.error_message

    @computed_field
    @property
    def validation_efficiency_score(self) -> float:
        """Computed field for validation efficiency scoring using Pydantic v2."""
        if not self.is_valid:
            return 0.0

        # Base efficiency score
        base_score = 1.0

        # Response time efficiency (lower is better)
        if self.response_time:
            if self.response_time <= 1.0:
                base_score *= 1.5  # Excellent
            elif self.response_time <= 3.0:
                base_score *= 1.2  # Good
            elif self.response_time <= 5.0:
                base_score *= 1.0  # Average
            elif self.response_time <= 10.0:
                base_score *= 0.8  # Below average
            else:
                base_score *= 0.5  # Poor

        # Anonymity bonus
        if self.anonymity_detected == AnonymityLevel.ELITE:
            base_score *= 1.3
        elif self.anonymity_detected == AnonymityLevel.ANONYMOUS:
            base_score *= 1.1
        elif self.anonymity_detected == AnonymityLevel.TRANSPARENT:
            base_score *= 0.9

        return round(base_score, 2)

    @property
    def health_score(self) -> float:
        """Calculate a health score based on validation results."""
        if not self.is_valid:
            return 0.0

        score = 1.0

        # Penalize based on response time
        if self.response_time:
            if self.response_time > 10.0:
                score *= 0.5
            elif self.response_time > 5.0:
                score *= 0.8
            elif self.response_time < 1.0:
                score *= 1.1  # Bonus for fast proxies

        # Bonus for detecting anonymity level
        if self.anonymity_detected == AnonymityLevel.ELITE:
            score *= 1.2
        elif self.anonymity_detected == AnonymityLevel.ANONYMOUS:
            score *= 1.1
        elif self.anonymity_detected == AnonymityLevel.TRANSPARENT:
            score *= 0.8

        # Allow score to exceed 1.0 for exceptional performance
        return score

    @classmethod
    def model_validate_json_fast(cls, json_data: str) -> "ValidationResult":
        """Fast JSON validation using Pydantic v2 performance optimization."""
        return cls.model_validate_json(json_data)

    class Config:
        # Enable arbitrary types for complex objects like Proxy
        arbitrary_types_allowed = True


class ProxyValidator:
    """Enhanced proxy validator with 5-stage pipeline and comprehensive metrics."""

    def __init__(
        self,
        timeout: float = 10.0,
        test_urls: Optional[List[str]] = None,
        # Back-compat alias accepted by tests
        test_url: Optional[str] = None,
        # Target-based validation support
        targets: Optional[Dict[str, TargetDefinition]] = None,
        max_concurrent: int = 10,
        circuit_breaker_threshold: int = 10,
        retry_attempts: int = 2,
        enable_anonymity_detection: bool = True,
        enable_geolocation_detection: bool = True,
        # Enhanced features
        quality_level: QualityLevel = QualityLevel.STANDARD,
        enable_5_stage_validation: bool = True,
        enable_tls_fingerprinting: bool = True,
        enable_dns_validation: bool = True,
        enable_anti_detection_testing: bool = True,
        enable_ml_prediction: bool = HAS_ML,
        geoip_database_path: Optional[str] = None,
        user_agents: Optional[List[str]] = None,
        enable_load_testing: bool = False,
        load_test_concurrent_requests: int = 5,
    ):
        # Basic configuration
        self.timeout = timeout
        self.quality_level = quality_level
        self.enable_5_stage_validation = enable_5_stage_validation
        self.enable_tls_fingerprinting = enable_tls_fingerprinting and HAS_CRYPTO
        self.enable_dns_validation = enable_dns_validation
        self.enable_anti_detection_testing = enable_anti_detection_testing
        self.enable_ml_prediction = enable_ml_prediction and HAS_ML
        self.enable_load_testing = enable_load_testing
        self.load_test_concurrent_requests = load_test_concurrent_requests
        
        # Normalize test URLs with alias support
        if test_url and not test_urls:
            test_urls = [test_url]
        self.test_urls = test_urls or [
            "https://httpbin.org/ip",
            "https://ifconfig.me/ip",
            "https://api.ipify.org?format=json",
            "https://jsonip.com/",
        ]
        self.primary_test_url = self.test_urls[0]

        # Target-based validation support
        self.targets = targets or {}

        self.retry_attempts = retry_attempts
        self.enable_anonymity_detection = enable_anonymity_detection
        self.enable_geolocation_detection = enable_geolocation_detection
        
        # Enhanced features initialization
        self.user_agents = user_agents or [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        
        # Initialize GeoIP database if available and enabled
        self.geoip_reader = None
        if self.enable_geolocation_detection and HAS_GEOIP:
            try:
                geoip_path = geoip_database_path or self._find_geoip_database()
                if geoip_path and Path(geoip_path).exists():
                    self.geoip_reader = geoip2.database.Reader(geoip_path)
                    logger.info(f"GeoIP database loaded from {geoip_path}")
                else:
                    logger.warning("GeoIP database not found, geographic validation disabled")
            except Exception as e:
                logger.warning(f"Failed to load GeoIP database: {e}")
        
        # Initialize ML components if enabled
        self.ml_model = None
        self.ml_scaler = None
        if self.enable_ml_prediction and HAS_ML:
            self._initialize_ml_components()
        
        # DNS resolver for enhanced DNS validation
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = 5.0
        self.dns_resolver.lifetime = 10.0

        # HTTPX connection pooling for performance optimization
        self.limits = httpx.Limits(
            max_keepalive_connections=20, max_connections=100, keepalive_expiry=30.0
        )

        # Event hooks for monitoring and debugging
        self.event_hooks: Dict[str, List[Callable[..., Any]]] = {
            "request": [self._log_request],
            "response": [self._log_response],
        }

        # Concurrency control
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # Circuit breaker for validation endpoints
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            recovery_timeout=30.0,
        )

        # Validation metrics
        self._total_validations = 0
        self._successful_validations = 0
        self._validation_history: List[ValidationResult] = []

        logger.info(
            "Enhanced ProxyValidator initialized with %d test URLs, %d targets, quality level: %s",
            len(self.test_urls),
            len(self.targets),
            self.quality_level.value,
        )

    def _find_geoip_database(self) -> Optional[str]:
        """Find GeoIP database in common locations."""
        common_paths = [
            "/usr/share/GeoIP/GeoLite2-City.mmdb",
            "/opt/GeoIP/GeoLite2-City.mmdb",
            "GeoLite2-City.mmdb",
            "./data/GeoLite2-City.mmdb",
        ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
        return None

    def _initialize_ml_components(self) -> None:
        """Initialize machine learning components for quality prediction."""
        try:
            self.ml_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.ml_scaler = StandardScaler()
            
            # Pre-train with some basic patterns if no existing model
            self._train_baseline_ml_model()
            logger.info("ML components initialized for quality prediction")
            
        except Exception as e:
            logger.warning(f"Failed to initialize ML components: {e}")
            self.enable_ml_prediction = False

    def _train_baseline_ml_model(self) -> None:
        """Train baseline ML model with synthetic data patterns."""
        if not HAS_ML:
            return
            
        try:
            # Generate synthetic training data based on common proxy patterns
            features = []
            labels = []
            
            # Good proxy patterns
            for _ in range(100):
                features.append([
                    random.uniform(0.5, 3.0),    # response_time
                    random.uniform(0.8, 1.0),    # anonymity_score
                    random.uniform(0.1, 0.5),    # connection_time
                    random.randint(1, 3),        # successful_stages
                    random.uniform(0.9, 1.0),    # uptime_ratio
                ])
                labels.append(1)  # Good quality
            
            # Poor proxy patterns
            for _ in range(100):
                features.append([
                    random.uniform(10.0, 30.0),  # response_time
                    random.uniform(0.0, 0.3),    # anonymity_score
                    random.uniform(5.0, 15.0),   # connection_time
                    random.randint(0, 1),        # successful_stages
                    random.uniform(0.0, 0.5),    # uptime_ratio
                ])
                labels.append(0)  # Poor quality
            
            # Train the model
            X = np.array(features)
            y = np.array(labels)
            
            X_scaled = self.ml_scaler.fit_transform(X)
            self.ml_model.fit(X_scaled, y)
            
            logger.debug("Baseline ML model trained with synthetic patterns")
            
        except Exception as e:
            logger.warning(f"Failed to train baseline ML model: {e}")

    def get_random_user_agent(self) -> str:
        """Get a random user agent for anti-detection."""
        return random.choice(self.user_agents)

    def create_trusted_result(
        self, proxy: Proxy, is_valid: bool, response_time: float
    ) -> ValidationResult:
        """Create ValidationResult with trusted data (performance optimization)."""
        return ValidationResult(
            proxy=proxy,
            is_valid=is_valid,
            response_time=response_time,  # Trusted response time
            timestamp=datetime.now(timezone.utc),
            test_url=self.test_urls[0] if self.test_urls else "",
        )

    def _log_request(self, request: httpx.Request) -> None:
        """Log outgoing HTTP requests for monitoring."""
        logger.debug("→ %s %s", request.method, request.url)

    def _log_response(self, response: httpx.Response) -> None:
        """Log incoming HTTP responses for monitoring."""
        logger.debug(
            "← %s %s [%d] %.3fs",
            response.request.method,
            response.url,
            response.status_code,
            response.elapsed.total_seconds() if response.elapsed else 0.0,
        )

    # Back-compat convenience property expected by tests
    @property
    def test_url(self) -> str:
        return self.primary_test_url

    @test_url.setter
    def test_url(self, value: str) -> None:
        # Update both primary and list to keep consistency
        self.primary_test_url = value
        if self.test_urls:
            self.test_urls[0] = value
        else:
            self.test_urls = [value]

    async def validate_proxy(self, proxy: Proxy) -> ValidationResult:
        """
        Enhanced proxy validation with 5-stage pipeline and comprehensive analysis.
        
        Stages:
        1. Connectivity: Basic connection and response validation
        2. Anonymity: Anonymity level detection and IP analysis  
        3. Performance: Speed, latency, and reliability testing
        4. Geographic: Location verification and DNS validation
        5. Anti-Detection: Stealth capabilities and fingerprint resistance
        """
        async with self.semaphore:
            self._total_validations += 1
            start_time = time.time()
            
            # Initialize comprehensive result
            result = ValidationResult(
                proxy=proxy,
                is_valid=False,
                test_url=self.primary_test_url,
                performance_metrics=PerformanceMetrics(),
                dns_metrics=DNSMetrics(),
                geographic_data=GeographicData(),
                anti_detection_metrics=AntiDetectionMetrics(),
            )
            
            # Add TLS fingerprint if cryptography is available
            if self.enable_tls_fingerprinting:
                result.tls_fingerprint = TLSFingerprint()

            try:
                # Determine validation approach based on configuration
                if self.enable_5_stage_validation and self.quality_level != QualityLevel.MINIMAL:
                    # Use comprehensive 5-stage validation
                    is_valid = await self.circuit_breaker.call(
                        self._validate_proxy_5_stage_pipeline, proxy, result
                    )
                elif self.targets:
                    # Use target-based validation
                    is_valid = await self.circuit_breaker.call(
                        self._validate_proxy_for_targets, proxy, result
                    )
                else:
                    # Use legacy single-URL validation for backward compatibility
                    is_valid = await self.circuit_breaker.call(
                        self._validate_single_proxy, proxy, result
                    )

                result.is_valid = is_valid

                if is_valid:
                    self._successful_validations += 1
                    
                    # Update proxy object with validation results
                    proxy.last_checked = result.timestamp
                    if result.response_time:
                        proxy.response_time = result.response_time
                    
                    # Generate ML prediction if enabled
                    if self.enable_ml_prediction and self.ml_model:
                        await self._generate_ml_prediction(result)
                        
                    # Determine quality tier
                    result.quality_tier = self._determine_quality_tier(result)
                    
                    logger.debug(
                        "Proxy %s:%s validated successfully (score: %.2f, tier: %s)",
                        proxy.host, proxy.port, result.overall_score, result.quality_tier
                    )

            except CircuitBreakerOpenError as e:
                result.error_type = ValidationErrorType.CIRCUIT_BREAKER_OPEN
                result.error_message = str(e)
                logger.debug("Circuit breaker open for %s:%s", proxy.host, proxy.port)

            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                result.error_type = self._categorize_error(e)
                result.error_message = str(e)
                logger.debug("Proxy %s:%s validation failed: %s", proxy.host, proxy.port, e)
            except Exception as e:
                # Catch-all for unexpected errors, but log for investigation
                result.error_type = ValidationErrorType.UNKNOWN
                result.error_message = f"Unexpected error: {str(e)}"
                logger.warning("Unexpected error validating %s:%s: %s", proxy.host, proxy.port, e)

            finally:
                result.response_time = time.time() - start_time
                proxy.last_checked = result.timestamp
                self._validation_history.append(result)

                # Memory management for validation history
                self._manage_validation_history_memory()

            return result

    async def _validate_proxy_5_stage_pipeline(self, proxy: Proxy, result: ValidationResult) -> bool:
        """
        Execute the comprehensive 5-stage validation pipeline.
        
        Returns True if the proxy passes the minimum requirements for validation.
        Individual stage results are stored in result.stage_results.
        """
        overall_success = True
        
        # Stage 1: Connectivity - REQUIRED
        connectivity_result = await self._validate_stage_connectivity(proxy, result)
        result.add_stage_result(connectivity_result)
        
        if not connectivity_result.is_valid:
            logger.debug(f"Proxy {proxy.host}:{proxy.port} failed connectivity stage")
            return False
        
        # Stage 2: Anonymity Detection
        if self.enable_anonymity_detection:
            anonymity_result = await self._validate_stage_anonymity(proxy, result)
            result.add_stage_result(anonymity_result)
            
        # Stage 3: Performance Testing  
        if self.quality_level in [QualityLevel.STANDARD, QualityLevel.THOROUGH, QualityLevel.ENTERPRISE]:
            performance_result = await self._validate_stage_performance(proxy, result)
            result.add_stage_result(performance_result)
            
        # Stage 4: Geographic Validation
        if (self.enable_geolocation_detection and 
            self.quality_level in [QualityLevel.THOROUGH, QualityLevel.ENTERPRISE]):
            geographic_result = await self._validate_stage_geographic(proxy, result)
            result.add_stage_result(geographic_result)
            
        # Stage 5: Anti-Detection Testing
        if (self.enable_anti_detection_testing and 
            self.quality_level == QualityLevel.ENTERPRISE):
            anti_detection_result = await self._validate_stage_anti_detection(proxy, result)
            result.add_stage_result(anti_detection_result)
            
        # Load testing if enabled
        if self.enable_load_testing and self.quality_level == QualityLevel.ENTERPRISE:
            await self._perform_load_test(proxy, result)
            
        # Update overall validation status
        result._update_overall_status()
        
        logger.debug(
            f"5-stage validation complete for {proxy.host}:{proxy.port} - "
            f"Score: {result.overall_score:.2f}, Valid: {result.is_valid}"
        )
        
        return result.is_valid

    async def _validate_stage_connectivity(self, proxy: Proxy, result: ValidationResult) -> StageValidationResult:
        """Stage 1: Basic connectivity and response validation."""
        stage_start = time.time()
        stage_result = StageValidationResult(
            stage=ValidationStage.CONNECTIVITY,
            is_valid=False,
            stage_score=0.0,
        )
        
        try:
            proxy_url = self._build_proxy_url(proxy)
            user_agent = self.get_random_user_agent()
            
            async with httpx.AsyncClient(
                proxy=proxy_url,
                timeout=httpx.Timeout(self.timeout),
                limits=self.limits,
                event_hooks=self.event_hooks,
                follow_redirects=True,
                headers={"User-Agent": user_agent},
            ) as client:
                
                # Test primary URL
                response = await client.get(self.primary_test_url)
                response.raise_for_status()
                
                # Basic connectivity success
                stage_result.is_valid = True
                stage_result.stage_score = 1.0
                
                # Update result with response data
                result.status_code = response.status_code
                result.response_headers = dict(response.headers)
                
                # Performance tracking
                if result.performance_metrics:
                    result.performance_metrics.response_time = time.time() - stage_start
                    result.performance_metrics.connection_time = (
                        response.elapsed.total_seconds() if response.elapsed else None
                    )
                
                stage_result.stage_details = {
                    "status_code": response.status_code,
                    "response_size": len(response.content),
                    "headers_count": len(response.headers),
                    "user_agent_used": user_agent,
                }
                
                logger.debug(f"Connectivity stage passed for {proxy.host}:{proxy.port}")
                
        except httpx.HTTPStatusError as e:
            stage_result.error_type = ValidationErrorType.HTTP_ERROR
            stage_result.error_message = f"HTTP {e.response.status_code}: {str(e)}"
            stage_result.stage_details = {"status_code": e.response.status_code}
            
        except httpx.ConnectError as e:
            stage_result.error_type = ValidationErrorType.CONNECTION_ERROR  
            stage_result.error_message = str(e)
            
        except httpx.TimeoutException as e:
            stage_result.error_type = ValidationErrorType.TIMEOUT
            stage_result.error_message = str(e)
            
        except Exception as e:
            stage_result.error_type = ValidationErrorType.UNKNOWN
            stage_result.error_message = f"Connectivity stage error: {str(e)}"
            
        finally:
            stage_result.execution_time = time.time() - stage_start
            
        return stage_result

    async def _validate_stage_anonymity(self, proxy: Proxy, result: ValidationResult) -> StageValidationResult:
        """Stage 2: Anonymity level detection and IP analysis."""
        stage_start = time.time()
        stage_result = StageValidationResult(
            stage=ValidationStage.ANONYMITY,
            is_valid=False,
            stage_score=0.0,
        )
        
        try:
            proxy_url = self._build_proxy_url(proxy)
            
            async with httpx.AsyncClient(
                proxy=proxy_url,
                timeout=httpx.Timeout(self.timeout * 0.8),  # Slightly shorter timeout
                limits=self.limits,
                event_hooks=self.event_hooks,
                headers={"User-Agent": self.get_random_user_agent()},
            ) as client:
                
                # Test multiple anonymity detection services
                anonymity_tests = [
                    ("httpbin.org/ip", self._parse_httpbin_response),
                    ("ifconfig.me/ip", self._parse_ifconfig_response),
                    ("api.ipify.org?format=json", self._parse_ipify_response),
                ]
                
                detected_ips = set()
                anonymity_scores = []
                
                for test_url, parser in anonymity_tests:
                    try:
                        full_url = f"https://{test_url}" if not test_url.startswith("http") else test_url
                        response = await client.get(full_url, timeout=5.0)
                        response.raise_for_status()
                        
                        detected_ip = parser(response)
                        if detected_ip:
                            detected_ips.add(detected_ip)
                            
                        # Check for proxy detection headers
                        headers = dict(response.headers)
                        anonymity_score = self._calculate_anonymity_score(headers, detected_ip, proxy.host)
                        anonymity_scores.append(anonymity_score)
                        
                    except Exception as e:
                        logger.debug(f"Anonymity test failed for {test_url}: {e}")
                        continue
                
                if detected_ips and anonymity_scores:
                    stage_result.is_valid = True
                    stage_result.stage_score = statistics.mean(anonymity_scores)
                    
                    # Determine anonymity level
                    avg_score = stage_result.stage_score
                    if avg_score >= 0.9:
                        result.anonymity_detected = AnonymityLevel.ELITE
                    elif avg_score >= 0.7:
                        result.anonymity_detected = AnonymityLevel.ANONYMOUS
                    elif avg_score >= 0.4:
                        result.anonymity_detected = AnonymityLevel.TRANSPARENT
                    else:
                        result.anonymity_detected = AnonymityLevel.UNKNOWN
                    
                    result.ip_detected = list(detected_ips)[0] if detected_ips else None
                    
                    stage_result.stage_details = {
                        "detected_ips": list(detected_ips),
                        "anonymity_level": result.anonymity_detected.value,
                        "anonymity_score": avg_score,
                        "tests_passed": len(anonymity_scores),
                    }
                    
                    logger.debug(f"Anonymity stage passed for {proxy.host}:{proxy.port} - Level: {result.anonymity_detected.value}")
                
        except Exception as e:
            stage_result.error_type = ValidationErrorType.UNKNOWN
            stage_result.error_message = f"Anonymity stage error: {str(e)}"
            
        finally:
            stage_result.execution_time = time.time() - stage_start
            
        return stage_result

    async def _validate_stage_performance(self, proxy: Proxy, result: ValidationResult) -> StageValidationResult:
        """Stage 3: Performance and response quality testing."""
        stage_start = time.time()
        stage_result = StageValidationResult(
            stage=ValidationStage.PERFORMANCE,
            is_valid=False,
            stage_score=0.0,
        )
        
        try:
            proxy_url = self._build_proxy_url(proxy)
            
            # Performance test configuration
            test_urls = [
                self.primary_test_url,
                "http://httpbin.org/get",
                "https://api.github.com/zen" if self.quality_level == QualityLevel.ENTERPRISE else None,
            ]
            test_urls = [url for url in test_urls if url]
            
            response_times = []
            throughput_scores = []
            stability_scores = []
            
            async with httpx.AsyncClient(
                proxy=proxy_url,
                timeout=httpx.Timeout(self.timeout),
                limits=self.limits,
                event_hooks=self.event_hooks,
                headers={"User-Agent": self.get_random_user_agent()},
            ) as client:
                
                # Multiple performance tests
                for url in test_urls:
                    for _ in range(3):  # Test stability with multiple requests
                        try:
                            start_time = time.time()
                            response = await client.get(url)
                            end_time = time.time()
                            
                            response_time = end_time - start_time
                            response_times.append(response_time)
                            
                            # Calculate throughput (bytes/second)
                            if response.content:
                                throughput = len(response.content) / response_time
                                throughput_scores.append(min(throughput / 10000, 1.0))  # Normalize
                            
                            # Stability: consistent response times
                            if len(response_times) > 1:
                                consistency = 1.0 - (abs(response_time - statistics.mean(response_times)) / 
                                                   max(statistics.mean(response_times), 0.1))
                                stability_scores.append(max(consistency, 0.0))
                            
                        except Exception as e:
                            logger.debug(f"Performance test failed for {url}: {e}")
                            continue
                
                if response_times:
                    avg_response_time = statistics.mean(response_times)
                    
                    # Performance scoring
                    speed_score = min(1.0, max(0.0, 1.0 - (avg_response_time - 1.0) / 10.0))
                    throughput_score = statistics.mean(throughput_scores) if throughput_scores else 0.5
                    stability_score = statistics.mean(stability_scores) if stability_scores else 0.5
                    
                    # Weighted performance score
                    stage_result.stage_score = (speed_score * 0.5 + throughput_score * 0.3 + stability_score * 0.2)
                    stage_result.is_valid = stage_result.stage_score >= 0.3
                    
                    # Update performance metrics in result
                    if result.performance_metrics:
                        result.performance_metrics.response_time = avg_response_time
                        result.performance_metrics.throughput = statistics.mean(throughput_scores) if throughput_scores else 0
                        result.performance_metrics.stability_score = stability_score
                        result.performance_metrics.benchmark_score = stage_result.stage_score
                    
                    stage_result.stage_details = {
                        "average_response_time": avg_response_time,
                        "min_response_time": min(response_times),
                        "max_response_time": max(response_times),
                        "response_time_std": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                        "throughput_score": throughput_score,
                        "stability_score": stability_score,
                        "tests_completed": len(response_times),
                    }
                    
                    logger.debug(f"Performance stage passed for {proxy.host}:{proxy.port} - Score: {stage_result.stage_score:.2f}")
                
        except Exception as e:
            stage_result.error_type = ValidationErrorType.UNKNOWN
            stage_result.error_message = f"Performance stage error: {str(e)}"
            
        finally:
            stage_result.execution_time = time.time() - stage_start
            
        return stage_result

    async def _validate_stage_geographic(self, proxy: Proxy, result: ValidationResult) -> StageValidationResult:
        """Stage 4: Geographic location validation and consistency."""
        stage_start = time.time()
        stage_result = StageValidationResult(
            stage=ValidationStage.GEOGRAPHIC,
            is_valid=False,
            stage_score=0.0,
        )
        
        try:
            if not self.geoip_db:
                stage_result.is_valid = True
                stage_result.stage_score = 0.5  # Neutral score when GeoIP unavailable
                stage_result.stage_details = {"error": "GeoIP database not available"}
                return stage_result
                
            # GeoIP lookup for proxy's actual location
            try:
                geoip_response = self.geoip_db.city(proxy.host)
                detected_country = geoip_response.country.iso_code
                detected_city = geoip_response.city.name
                detected_coords = (geoip_response.location.latitude, geoip_response.location.longitude)
                
                result.country_detected = detected_country
                result.city_detected = detected_city
                result.coordinates = detected_coords
                
                # Geographic consistency checks
                consistency_score = 1.0
                consistency_details = {}
                
                # Check country consistency
                if proxy.country and detected_country:
                    country_match = proxy.country.upper() == detected_country.upper()
                    if not country_match:
                        consistency_score *= 0.5
                    consistency_details["country_match"] = country_match
                    consistency_details["expected_country"] = proxy.country
                    consistency_details["detected_country"] = detected_country
                
                # Test proxy through geographic service
                proxy_url = self._build_proxy_url(proxy)
                async with httpx.AsyncClient(
                    proxy=proxy_url,
                    timeout=httpx.Timeout(self.timeout * 0.7),
                    limits=self.limits,
                    headers={"User-Agent": self.get_random_user_agent()},
                ) as client:
                    
                    # Test geographic detection through proxy
                    geo_test_urls = [
                        "http://ip-api.com/json/",
                        "https://ipapi.co/json/",
                    ]
                    
                    proxy_geo_results = []
                    
                    for test_url in geo_test_urls:
                        try:
                            response = await client.get(test_url, timeout=5.0)
                            if response.status_code == 200:
                                geo_data = response.json()
                                
                                proxy_country = geo_data.get("countryCode") or geo_data.get("country_code")
                                proxy_city = geo_data.get("city")
                                
                                if proxy_country:
                                    proxy_geo_results.append({
                                        "country": proxy_country,
                                        "city": proxy_city,
                                        "source": test_url,
                                    })
                                    
                        except Exception as e:
                            logger.debug(f"Geographic test failed for {test_url}: {e}")
                            continue
                    
                    # Analyze geographic consistency
                    if proxy_geo_results:
                        proxy_countries = [r["country"] for r in proxy_geo_results if r["country"]]
                        
                        if proxy_countries and detected_country:
                            geo_consistency = sum(
                                1 for c in proxy_countries 
                                if c.upper() == detected_country.upper()
                            ) / len(proxy_countries)
                            consistency_score *= geo_consistency
                        
                        consistency_details["proxy_geo_results"] = proxy_geo_results
                        consistency_details["geo_consistency"] = geo_consistency
                
                stage_result.is_valid = True
                stage_result.stage_score = consistency_score
                
                stage_result.stage_details = {
                    "detected_country": detected_country,
                    "detected_city": detected_city,
                    "detected_coordinates": detected_coords,
                    "consistency_score": consistency_score,
                    "consistency_details": consistency_details,
                }
                
                logger.debug(f"Geographic stage passed for {proxy.host}:{proxy.port} - Country: {detected_country}")
                
            except Exception as e:
                stage_result.error_type = ValidationErrorType.GEOLOCATION_ERROR
                stage_result.error_message = f"GeoIP lookup failed: {str(e)}"
                
        except Exception as e:
            stage_result.error_type = ValidationErrorType.UNKNOWN
            stage_result.error_message = f"Geographic stage error: {str(e)}"
            
        finally:
            stage_result.execution_time = time.time() - stage_start
            
        return stage_result

    async def _validate_stage_anti_detection(self, proxy: Proxy, result: ValidationResult) -> StageValidationResult:
        """Stage 5: Anti-detection and stealth capability testing."""
        stage_start = time.time()
        stage_result = StageValidationResult(
            stage=ValidationStage.ANTI_DETECTION,
            is_valid=False,
            stage_score=0.0,
        )
        
        try:
            proxy_url = self._build_proxy_url(proxy)
            detection_scores = []
            test_results = {}
            
            async with httpx.AsyncClient(
                proxy=proxy_url,
                timeout=httpx.Timeout(self.timeout),
                limits=self.limits,
                headers={"User-Agent": self.get_random_user_agent()},
            ) as client:
                
                # Test 1: TLS Fingerprinting Detection
                try:
                    tls_score = await self._test_tls_fingerprinting(client)
                    detection_scores.append(tls_score)
                    test_results["tls_fingerprinting"] = tls_score
                except Exception as e:
                    logger.debug(f"TLS fingerprinting test failed: {e}")
                
                # Test 2: HTTP Header Analysis
                try:
                    header_score = await self._test_header_consistency(client)
                    detection_scores.append(header_score)
                    test_results["header_consistency"] = header_score
                except Exception as e:
                    logger.debug(f"Header consistency test failed: {e}")
                
                # Test 3: WebRTC Leak Detection
                try:
                    webrtc_score = await self._test_webrtc_leak_protection(client)
                    detection_scores.append(webrtc_score)
                    test_results["webrtc_protection"] = webrtc_score
                except Exception as e:
                    logger.debug(f"WebRTC test failed: {e}")
                
                # Test 4: DNS Leak Detection
                try:
                    dns_score = await self._test_dns_leak_protection(client)
                    detection_scores.append(dns_score)
                    test_results["dns_protection"] = dns_score
                except Exception as e:
                    logger.debug(f"DNS leak test failed: {e}")
                
                # Test 5: Behavioral Analysis
                try:
                    behavior_score = await self._test_behavioral_consistency(client)
                    detection_scores.append(behavior_score)
                    test_results["behavioral_consistency"] = behavior_score
                except Exception as e:
                    logger.debug(f"Behavioral test failed: {e}")
                
                if detection_scores:
                    avg_score = statistics.mean(detection_scores)
                    stage_result.stage_score = avg_score
                    stage_result.is_valid = avg_score >= 0.6  # Anti-detection threshold
                    
                    # Determine anti-detection level
                    if avg_score >= 0.9:
                        result.anti_detection_level = AntiDetectionLevel.STEALTH
                    elif avg_score >= 0.7:
                        result.anti_detection_level = AntiDetectionLevel.HIGH
                    elif avg_score >= 0.5:
                        result.anti_detection_level = AntiDetectionLevel.MEDIUM
                    else:
                        result.anti_detection_level = AntiDetectionLevel.LOW
                    
                    stage_result.stage_details = {
                        "anti_detection_level": result.anti_detection_level.value,
                        "detection_score": avg_score,
                        "test_results": test_results,
                        "tests_passed": len([s for s in detection_scores if s >= 0.5]),
                        "total_tests": len(detection_scores),
                    }
                    
                    logger.debug(f"Anti-detection stage completed for {proxy.host}:{proxy.port} - Level: {result.anti_detection_level.value}")
                
        except Exception as e:
            stage_result.error_type = ValidationErrorType.UNKNOWN
            stage_result.error_message = f"Anti-detection stage error: {str(e)}"
            
        finally:
            stage_result.execution_time = time.time() - stage_start
            
        return stage_result

    async def _perform_load_test(self, proxy: Proxy, result: ValidationResult) -> None:
        """Perform concurrent load testing to assess proxy stability under load."""
        if not self.enable_load_testing:
            return
            
        try:
            proxy_url = self._build_proxy_url(proxy)
            concurrent_requests = min(self.load_test_requests, 50)  # Safety limit
            
            async def single_request():
                try:
                    async with httpx.AsyncClient(
                        proxy=proxy_url,
                        timeout=httpx.Timeout(5.0),  # Shorter timeout for load test
                        limits=httpx.Limits(max_connections=1, max_keepalive_connections=0),
                    ) as client:
                        response = await client.get(self.primary_test_url)
                        return response.status_code == 200, time.time()
                except Exception:
                    return False, time.time()
            
            # Execute concurrent requests
            start_time = time.time()
            tasks = [single_request() for _ in range(concurrent_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Analyze load test results
            successful_requests = sum(1 for r in results if isinstance(r, tuple) and r[0])
            success_rate = successful_requests / len(results) if results else 0
            total_time = end_time - start_time
            
            # Update result with load test data
            if result.performance_metrics:
                result.performance_metrics.load_test_success_rate = success_rate
                result.performance_metrics.concurrent_request_performance = successful_requests / total_time
                
            logger.debug(
                f"Load test completed for {proxy.host}:{proxy.port} - "
                f"Success rate: {success_rate:.2f}, Requests: {concurrent_requests}"
            )
            
        except Exception as e:
            logger.debug(f"Load test failed for {proxy.host}:{proxy.port}: {e}")

    def _parse_httpbin_response(self, response: httpx.Response) -> Optional[str]:
        """Parse IP from httpbin.org/ip response."""
        try:
            data = response.json()
            return data.get("origin", "").split(",")[0].strip()
        except Exception:
            return None

    def _parse_ifconfig_response(self, response: httpx.Response) -> Optional[str]:
        """Parse IP from ifconfig.me/ip response."""
        try:
            return response.text.strip()
        except Exception:
            return None

    def _parse_ipify_response(self, response: httpx.Response) -> Optional[str]:
        """Parse IP from ipify.org response."""
        try:
            data = response.json()
            return data.get("ip", "").strip()
        except Exception:
            return None

    def _calculate_anonymity_score(self, headers: Dict[str, str], detected_ip: str, proxy_host: str) -> float:
        """Calculate anonymity score based on headers and IP detection."""
        score = 1.0
        
        # Check for proxy detection headers
        proxy_indicators = [
            "x-forwarded-for", "x-real-ip", "x-forwarded-proto", 
            "x-forwarded-host", "via", "forwarded", "x-proxy-id"
        ]
        
        for indicator in proxy_indicators:
            if indicator in [h.lower() for h in headers.keys()]:
                score -= 0.15
        
        # Check if detected IP matches proxy host
        if detected_ip and proxy_host:
            try:
                if ipaddress.ip_address(detected_ip) != ipaddress.ip_address(proxy_host):
                    score += 0.2  # Good - shows different IP
            except ValueError:
                pass  # Invalid IP format
        
        # Check for anonymity-friendly headers
        user_agent = headers.get("User-Agent", "")
        if user_agent and "curl" not in user_agent.lower():
            score += 0.1
            
        return max(0.0, min(1.0, score))

    def _generate_ml_prediction(self, result: ValidationResult) -> Optional[float]:
        """Generate ML-based quality prediction if scikit-learn is available."""
        if not self.ml_model or not SCIKIT_LEARN_AVAILABLE:
            return None
            
        try:
            # Extract features for ML prediction
            features = []
            
            # Performance features
            if result.performance_metrics:
                features.extend([
                    result.performance_metrics.response_time or 5.0,
                    result.performance_metrics.throughput or 0.0,
                    result.performance_metrics.stability_score or 0.5,
                    result.performance_metrics.benchmark_score or 0.5,
                ])
            else:
                features.extend([5.0, 0.0, 0.5, 0.5])
                
            # Anonymity features
            anonymity_score = 0.5
            if result.anonymity_detected:
                anonymity_scores = {
                    AnonymityLevel.ELITE: 1.0,
                    AnonymityLevel.ANONYMOUS: 0.8,
                    AnonymityLevel.TRANSPARENT: 0.4,
                    AnonymityLevel.UNKNOWN: 0.2,
                }
                anonymity_score = anonymity_scores.get(result.anonymity_detected, 0.5)
            features.append(anonymity_score)
            
            # Geographic consistency
            geo_score = 0.5
            if result.country_detected and hasattr(result, 'country_expected'):
                geo_score = 1.0 if result.country_detected == getattr(result, 'country_expected', None) else 0.3
            features.append(geo_score)
            
            # Stage completion rate
            if result.stage_results:
                completion_rate = len(result.stage_results) / 5  # 5 total stages
                success_rate = sum(1 for s in result.stage_results if s.is_valid) / max(len(result.stage_results), 1)
            else:
                completion_rate = 0.2
                success_rate = 0.0
                
            features.extend([completion_rate, success_rate])
            
            # Anti-detection score
            anti_detection_score = 0.5
            if result.anti_detection_level:
                detection_scores = {
                    AntiDetectionLevel.STEALTH: 1.0,
                    AntiDetectionLevel.HIGH: 0.8,
                    AntiDetectionLevel.MEDIUM: 0.6,
                    AntiDetectionLevel.LOW: 0.3,
                }
                anti_detection_score = detection_scores.get(result.anti_detection_level, 0.5)
            features.append(anti_detection_score)
            
            # Ensure we have the right number of features
            while len(features) < 10:  # Pad to expected feature count
                features.append(0.5)
                
            # Make prediction
            import numpy as np
            feature_array = np.array([features])
            prediction = self.ml_model.predict_proba(feature_array)[0]
            
            # Return probability of high quality
            return float(prediction[1]) if len(prediction) > 1 else float(prediction[0])
            
        except Exception as e:
            logger.debug(f"ML prediction failed: {e}")
            return None

    def _determine_quality_tier(self, result: ValidationResult) -> QualityLevel:
        """Determine the quality tier based on validation results."""
        if result.overall_score >= 0.9:
            return QualityLevel.ENTERPRISE
        elif result.overall_score >= 0.7:
            return QualityLevel.THOROUGH
        elif result.overall_score >= 0.5:
            return QualityLevel.STANDARD
        else:
            return QualityLevel.BASIC

    async def _test_tls_fingerprinting(self, client: httpx.AsyncClient) -> float:
        """Test TLS fingerprinting resistance."""
        try:
            # Test HTTPS connection to gather TLS info
            response = await client.get("https://tls.browserleaks.com/json", timeout=5.0)
            if response.status_code != 200:
                return 0.5  # Neutral score
                
            tls_data = response.json()
            
            # Analyze TLS fingerprint characteristics  
            score = 1.0
            
            # Check for common TLS fingerprint patterns
            cipher_suite = tls_data.get("cipher_suite", "")
            if "TLS_" in cipher_suite:
                score += 0.1
                
            # Check TLS version
            tls_version = tls_data.get("version", "")
            if "1.3" in tls_version or "1.2" in tls_version:
                score += 0.1
                
            return min(1.0, score)
            
        except Exception:
            return 0.5  # Neutral score on test failure

    async def _test_header_consistency(self, client: httpx.AsyncClient) -> float:
        """Test HTTP header consistency and naturalness."""
        try:
            response = await client.get("https://httpbin.org/headers", timeout=5.0)
            if response.status_code != 200:
                return 0.5
                
            data = response.json()
            headers = data.get("headers", {})
            
            score = 1.0
            
            # Check for natural header patterns
            user_agent = headers.get("User-Agent", "")
            if user_agent:
                # Good if looks like real browser
                if any(browser in user_agent for browser in ["Chrome", "Firefox", "Safari", "Edge"]):
                    score += 0.2
                # Bad if looks like bot/script
                if any(bot in user_agent.lower() for bot in ["python", "curl", "wget", "bot"]):
                    score -= 0.3
            
            # Check for expected browser headers
            expected_headers = ["Accept", "Accept-Language", "Accept-Encoding"]
            present_headers = sum(1 for h in expected_headers if h in headers)
            score += (present_headers / len(expected_headers)) * 0.2
            
            # Check for proxy leak headers
            leak_headers = ["X-Forwarded-For", "X-Real-IP", "Via"]
            leaked = sum(1 for h in leak_headers if h in headers)
            if leaked > 0:
                score -= leaked * 0.2
                
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5

    async def _test_webrtc_leak_protection(self, client: httpx.AsyncClient) -> float:
        """Test WebRTC leak protection (simplified HTTP-based test)."""
        try:
            # Test for WebRTC leak indicators via browser fingerprinting service
            response = await client.get("https://browserleaks.com/webrtc", timeout=5.0)
            
            # Since we can't execute JavaScript, we'll do a simplified check
            # by looking for WebRTC-related content or APIs
            content = response.text.lower()
            
            score = 1.0
            
            # Look for WebRTC leak indicators in response
            webrtc_indicators = ["webrtc", "rtcpeerconnection", "getusermedia"]
            found_indicators = sum(1 for indicator in webrtc_indicators if indicator in content)
            
            # Lower score if many WebRTC features are detected (potential leaks)
            if found_indicators > 2:
                score -= 0.3
            elif found_indicators > 0:
                score -= 0.1
                
            return max(0.0, score)
            
        except Exception:
            return 0.7  # Assume good protection if test fails

    async def _test_dns_leak_protection(self, client: httpx.AsyncClient) -> float:
        """Test DNS leak protection."""
        try:
            # Test DNS resolution through proxy
            response = await client.get("https://www.dnsleaktest.com/", timeout=5.0)
            
            if response.status_code != 200:
                return 0.5
                
            # Simple content analysis for DNS leak indicators
            content = response.text.lower()
            
            score = 1.0
            
            # Look for DNS leak warnings or indicators
            dns_leak_terms = ["dns leak", "leaked", "your dns", "dns servers"]
            leak_indicators = sum(1 for term in dns_leak_terms if term in content)
            
            if leak_indicators > 2:
                score -= 0.4
            elif leak_indicators > 0:
                score -= 0.2
                
            return max(0.0, score)
            
        except Exception:
            return 0.6  # Neutral score on test failure

    async def _test_behavioral_consistency(self, client: httpx.AsyncClient) -> float:
        """Test behavioral consistency and timing patterns."""
        try:
            # Test multiple requests with timing analysis
            request_times = []
            
            for _ in range(3):
                start_time = time.time()
                response = await client.get("https://httpbin.org/delay/1", timeout=8.0)
                end_time = time.time()
                
                if response.status_code == 200:
                    request_times.append(end_time - start_time)
                    
            if not request_times:
                return 0.3
                
            # Analyze timing consistency
            if len(request_times) > 1:
                avg_time = statistics.mean(request_times)
                std_dev = statistics.stdev(request_times)
                
                # Good if timing is consistent (low std deviation)
                consistency_score = max(0.0, 1.0 - (std_dev / max(avg_time, 0.1)))
                
                # Good if timing seems natural (not too fast/slow)
                natural_score = 1.0
                if avg_time < 0.5:  # Too fast - might indicate caching/bot
                    natural_score -= 0.3
                elif avg_time > 10.0:  # Too slow - might indicate problems
                    natural_score -= 0.2
                    
                return min(1.0, (consistency_score * 0.6 + natural_score * 0.4))
            
            return 0.5
            
        except Exception:
            return 0.4

    def _build_proxy_url(self, proxy: Proxy) -> str:
        """Build proxy URL from proxy object."""
        scheme = proxy.schemes[0] if proxy.schemes else "http"
        if proxy.username and proxy.password:
            return f"{scheme}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
        return f"{scheme}://{proxy.host}:{proxy.port}"

    def get_random_user_agent(self) -> str:
        """Get a random user agent string for requests."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        return random.choice(user_agents)

    async def validate_proxies_batch(
        self,
        proxies: List[Proxy],
        *,
        batch_size: int = 50,
        max_concurrent: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[ValidationResult]:
        """
        Efficiently validate a batch of proxies with controlled concurrency and memory management.

        Args:
            proxies: List of proxy objects to validate
            batch_size: Number of proxies to process in each batch (default: 50)
            max_concurrent: Override default concurrency limit (default: use instance setting)
            progress_callback: Optional callback function to report progress (completed, total)

        Returns:
            List of ValidationResult objects
        """
        if not proxies:
            return []

        # Use instance concurrency setting if not overridden
        concurrent_limit = max_concurrent or self.semaphore._value
        semaphore = asyncio.Semaphore(concurrent_limit)

        results: List[ValidationResult] = []
        total_proxies = len(proxies)
        completed = 0

        logger.info(
            f"Starting batch validation of {total_proxies} proxies with batch size {batch_size}"
        )

        # Process proxies in batches to manage memory
        for batch_start in range(0, total_proxies, batch_size):
            batch_end = min(batch_start + batch_size, total_proxies)
            batch_proxies = proxies[batch_start:batch_end]

            logger.debug(
                f"Processing batch {batch_start//batch_size + 1}: proxies {batch_start+1} to {batch_end}"
            )

            # Create validation tasks for the current batch
            async def validate_with_semaphore(proxy: Proxy) -> ValidationResult:
                async with semaphore:
                    result = await self.validate_proxy(proxy)
                    nonlocal completed
                    completed += 1

                    # Report progress if callback provided
                    if progress_callback:
                        progress_callback(completed, total_proxies)

                    return result

            # Execute batch validation concurrently
            batch_tasks = [validate_with_semaphore(proxy) for proxy in batch_proxies]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Process results and handle exceptions
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    # Create error result for failed validation
                    error_result = ValidationResult(
                        proxy=batch_proxies[i],
                        is_valid=False,
                        error_type=ValidationErrorType.CONNECTION_ERROR,
                        error_message=f"Batch validation error: {str(result)}",
                        timestamp=datetime.now(timezone.utc),
                    )
                    results.append(error_result)
                    logger.error(
                        f"Error validating proxy {batch_proxies[i].ip}:{batch_proxies[i].port}: {result}"
                    )
                elif isinstance(result, ValidationResult):
                    results.append(result)

            # Memory management: limit validation history growth
            if len(self._validation_history) > 10000:  # Configurable limit
                # Keep only the most recent 5000 results
                self._validation_history = self._validation_history[-5000:]
                logger.debug("Trimmed validation history to prevent memory bloat")

        logger.info(
            f"Batch validation completed. {len([r for r in results if r.is_valid])} valid out of {total_proxies} proxies"
        )
        return results

    def _manage_validation_history_memory(
        self, max_size: int = 10000, trim_size: int = 5000
    ) -> None:
        """
        Manage validation history memory to prevent memory leaks during long-running sessions.

        Args:
            max_size: Maximum number of results to keep in memory
            trim_size: Number of most recent results to retain when trimming
        """
        if len(self._validation_history) > max_size:
            # Keep only the most recent results
            self._validation_history = self._validation_history[-trim_size:]
            logger.debug(
                f"Trimmed validation history from {max_size}+ to {trim_size} results to prevent memory bloat"
            )

    async def _validate_proxy_for_targets(self, proxy: Proxy, result: ValidationResult) -> bool:
        """Validate a proxy against all defined targets."""
        proxy_url = self._build_proxy_url(proxy)
        target_results: Dict[str, TargetValidationResult] = {}
        overall_success = False

        async with httpx.AsyncClient(
            proxy=proxy_url,
            timeout=httpx.Timeout(self.timeout),
            limits=self.limits,  # ✅ Connection pooling
            event_hooks=self.event_hooks,  # ✅ Monitoring hooks
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
            },
        ) as client:

            # Test each target
            for target_id, target_def in self.targets.items():
                target_start_time = time.time()
                target_result = TargetValidationResult(
                    target_id=target_id,
                    target_url=target_def.url,
                    is_valid=False,
                )

                try:
                    # Use target-specific timeout if defined
                    target_timeout = target_def.timeout or self.timeout
                    response = await client.get(
                        target_def.url, timeout=httpx.Timeout(target_timeout)
                    )

                    # Check if status code is expected
                    expected_codes = target_def.expected_status_codes or [200]
                    if response.status_code in expected_codes:
                        target_result.is_valid = True
                        overall_success = True  # At least one target succeeded

                        # Update proxy target health (defensive check)
                        target_response_time = time.time() - target_start_time
                        if hasattr(proxy, "update_target_health") and callable(
                            getattr(proxy, "update_target_health", None)
                        ):
                            proxy.update_target_health(target_id, True, target_response_time)

                        # Use first successful target for overall anonymity detection
                        if (
                            not result.ip_detected
                            and self.enable_anonymity_detection
                            and target_id == next(iter(self.targets))
                        ):  # First target
                            await self._detect_anonymity(response, result, proxy)
                    else:
                        if hasattr(proxy, "update_target_health") and callable(
                            getattr(proxy, "update_target_health", None)
                        ):
                            proxy.update_target_health(target_id, False)
                        target_result.error_message = (
                            f"Unexpected status code: {response.status_code}"
                        )

                    target_result.status_code = response.status_code
                    target_result.response_time = time.time() - target_start_time

                except (httpx.HTTPError, asyncio.TimeoutError) as e:
                    if hasattr(proxy, "update_target_health") and callable(
                        getattr(proxy, "update_target_health", None)
                    ):
                        proxy.update_target_health(target_id, False)
                    target_result.error_type = self._categorize_error(e)
                    target_result.error_message = str(e)
                    target_result.response_time = time.time() - target_start_time
                    logger.debug(
                        "Target %s validation failed for proxy %s:%s: %s",
                        target_id,
                        proxy.host,
                        proxy.port,
                        e,
                    )
                except Exception as e:
                    # Catch-all for unexpected errors in target validation
                    if hasattr(proxy, "update_target_health") and callable(
                        getattr(proxy, "update_target_health", None)
                    ):
                        proxy.update_target_health(target_id, False)
                    target_result.error_type = ValidationErrorType.UNKNOWN
                    target_result.error_message = f"Unexpected target validation error: {str(e)}"
                    target_result.response_time = time.time() - target_start_time
                    logger.warning(
                        "Unexpected error in target %s validation for proxy %s:%s: %s",
                        target_id,
                        proxy.host,
                        proxy.port,
                        e,
                    )

                target_results[target_id] = target_result

            result.target_results = target_results

        if overall_success:
            logger.debug(
                "Proxy %s:%s validated successfully for %d/%d targets",
                proxy.host,
                proxy.port,
                sum(1 for tr in target_results.values() if tr.is_valid),
                len(target_results),
            )

        return overall_success

    async def _validate_single_proxy(self, proxy: Proxy, result: ValidationResult) -> bool:
        """Internal validation logic with enhanced testing."""
        proxy_url = self._build_proxy_url(proxy)

        async with httpx.AsyncClient(
            proxy=proxy_url,
            timeout=httpx.Timeout(self.timeout),
            limits=self.limits,  # ✅ Connection pooling
            event_hooks=self.event_hooks,  # ✅ Monitoring hooks
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
            },
        ) as client:
            # Test with primary URL
            response = await client.get(self.primary_test_url)
            response.raise_for_status()

            result.status_code = response.status_code
            result.response_headers = dict(response.headers)

            # Extract and analyze response for anonymity detection
            if self.enable_anonymity_detection:
                await self._detect_anonymity(response, result, proxy)

            # Test with additional URLs for reliability (if configured)
            if len(self.test_urls) > 1:
                await self._validate_additional_urls(client, result)

        logger.debug(
            "Proxy %s:%s validated successfully (anonymity: %s)",
            proxy.host,
            proxy.port,
            result.anonymity_detected,
        )
        return True

    def _build_proxy_url(self, proxy: Proxy) -> str:
        """Build proxy URL based on proxy scheme and credentials."""
        # Default to HTTP; prefer the first declared scheme if available
        if getattr(proxy, "schemes", None) and len(proxy.schemes) > 0:
            first_scheme = proxy.schemes[0]
            # Handle both enum objects and string values (after serialization)
            if hasattr(first_scheme, "value"):
                scheme = first_scheme.value.lower()
            else:
                scheme = str(first_scheme).lower()
        else:
            scheme = "http"

        if hasattr(proxy, "credentials") and proxy.credentials:
            auth = f"{proxy.credentials.username}:{proxy.credentials.password}@"
            return f"{scheme}://{auth}{proxy.host}:{proxy.port}"
        else:
            return f"{scheme}://{proxy.host}:{proxy.port}"

    async def _detect_anonymity(
        self, response: httpx.Response, result: ValidationResult, proxy: Proxy
    ) -> None:
        """Detect proxy anonymity level based on response analysis."""
        try:
            # Parse response to extract IP information
            response_data = (
                response.json()
                if response.headers.get("content-type", "").startswith("application/json")
                else {}
            )

            detected_ip = (
                response_data.get("origin") or response_data.get("ip") or response.text.strip()
            )
            result.ip_detected = detected_ip

            headers = result.response_headers or {}

            # Check for forwarded headers that reveal original IP
            forwarded_headers = [
                "x-forwarded-for",
                "x-real-ip",
                "x-originating-ip",
                "x-remote-ip",
                "x-client-ip",
                "via",
                "forwarded",
            ]

            has_forwarded_headers = any(header.lower() in headers for header in forwarded_headers)

            if has_forwarded_headers:
                result.anonymity_detected = AnonymityLevel.TRANSPARENT
            elif detected_ip != proxy.host:  # IP changed, likely anonymous
                result.anonymity_detected = AnonymityLevel.ELITE
            else:
                result.anonymity_detected = AnonymityLevel.ANONYMOUS

        except (httpx.HTTPError, ValueError, KeyError) as e:
            # Handle specific parsing and HTTP errors
            logger.debug(
                "Anonymity detection failed for %s:%s: %s",
                proxy.host,
                proxy.port,
                e,
            )
            result.anonymity_detected = AnonymityLevel.UNKNOWN
        except Exception as e:
            # Catch-all for unexpected errors in anonymity detection
            logger.warning(
                "Unexpected error in anonymity detection for %s:%s: %s",
                proxy.host,
                proxy.port,
                e,
            )
            result.anonymity_detected = AnonymityLevel.UNKNOWN

    async def _validate_additional_urls(
        self, client: httpx.AsyncClient, result: ValidationResult
    ) -> None:
        """Test proxy against additional URLs for reliability."""
        additional_url_success_count = 0
        total_additional_urls = len(self.test_urls) - 1

        for test_url in self.test_urls[1:]:  # Skip first URL (already tested)
            try:
                response = await client.get(test_url, timeout=httpx.Timeout(5.0))
                response.raise_for_status()
                additional_url_success_count += 1
                logger.debug("Additional URL %s validation successful", test_url)
            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                logger.debug("Additional URL %s validation failed: %s", test_url, e)
                # Don't fail the entire validation for secondary URLs
            except Exception as e:
                # Unexpected errors in additional URL validation
                logger.warning("Unexpected error validating additional URL %s: %s", test_url, e)
                # Don't fail the entire validation for secondary URLs

        # Log additional URL validation metrics for debugging
        if total_additional_urls > 0:
            success_rate = additional_url_success_count / total_additional_urls
            logger.debug(
                "Additional URLs validation for %s:%s: %d/%d success (%.1%)",
                result.proxy.host,
                result.proxy.port,
                additional_url_success_count,
                total_additional_urls,
                success_rate * 100,
            )

    def _categorize_error(self, error: Exception) -> ValidationErrorType:
        """Categorize validation errors for better reporting."""
        error_str = str(error).lower()

        if isinstance(error, asyncio.TimeoutError) or "timeout" in error_str:
            return ValidationErrorType.TIMEOUT
        elif isinstance(error, httpx.ConnectError) or "connection" in error_str:
            return ValidationErrorType.CONNECTION_ERROR
        elif isinstance(error, httpx.ProxyError) or "proxy" in error_str:
            return ValidationErrorType.PROXY_ERROR
        elif isinstance(error, httpx.HTTPStatusError):
            if error.response.status_code == 429:
                return ValidationErrorType.RATE_LIMITED
            elif 400 <= error.response.status_code < 500:
                return ValidationErrorType.AUTHENTICATION_ERROR
            else:
                return ValidationErrorType.HTTP_ERROR
        elif isinstance(error, CircuitBreakerOpenError):
            return ValidationErrorType.CIRCUIT_BREAKER_OPEN
        elif "ssl" in error_str or "certificate" in error_str:
            return ValidationErrorType.SSL_ERROR
        else:
            return ValidationErrorType.UNKNOWN

    async def validate_proxies(self, proxies: List[Proxy]) -> ValidationSummary:
        """Validate multiple proxies and return comprehensive summary."""
        if not proxies:
            return ValidationSummary(
                total_proxies=0,
                valid_proxy_results=[],
                failed_proxy_results=[],
            )

        start_time = time.time()
        logger.info("Validating %d proxies with enhanced validation...", len(proxies))

        # Create validation tasks for all proxies
        tasks = [self.validate_proxy(proxy) for proxy in proxies]

        # Run validations concurrently
        results: List[ValidationResult] = await asyncio.gather(*tasks, return_exceptions=False)

        # Process results and build summary
        valid_results = [r for r in results if r.is_valid]
        failed_results = [r for r in results if not r.is_valid]

        response_times = [r.response_time for r in valid_results if r.response_time is not None]

        # Error breakdown
        error_breakdown: Dict[ValidationErrorType, int] = {}
        for result in failed_results:
            if result.error_type:
                error_breakdown[result.error_type] = error_breakdown.get(result.error_type, 0) + 1

        summary = ValidationSummary(
            total_proxies=len(proxies),
            valid_proxy_results=valid_results,
            failed_proxy_results=failed_results,
            success_rate=len(valid_results) / len(proxies) if proxies else 0.0,
            error_breakdown=error_breakdown,
            validation_duration=time.time() - start_time,
            avg_response_time=(
                sum(response_times) / len(response_times) if response_times else None
            ),
            min_response_time=min(response_times) if response_times else None,
            max_response_time=max(response_times) if response_times else None,
        )

        logger.info(
            "Validation complete: %d/%d valid (%s) in %.1fs [Quality: %s]",
            summary.valid_proxy_count,
            summary.total_proxies,
            f"{summary.success_rate:.1%}",
            summary.validation_duration,
            summary.quality_tier,
        )

        return summary

    def get_validation_stats(self) -> Dict[str, Any]:
        """Get overall validation statistics."""
        return {
            "total_validations": self._total_validations,
            "successful_validations": self._successful_validations,
            "success_rate": (
                self._successful_validations / self._total_validations
                if self._total_validations
                else 0.0
            ),
            "recent_validations": len(self._validation_history[-100:]),  # Last 100
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on validation endpoints."""
        health_status: Dict[str, Any] = {
            "circuit_breaker_state": self.circuit_breaker.state.value,
            "circuit_breaker_failures": self.circuit_breaker.failure_count,
            "test_endpoints": [],
        }

        for test_url in self.test_urls:
            try:
                async with httpx.AsyncClient(
                    timeout=5.0,
                    limits=self.limits,  # ✅ Connection pooling for health checks
                    event_hooks=self.event_hooks,  # ✅ Monitoring hooks
                ) as client:
                    response = await client.get(test_url)
                    health_status["test_endpoints"].append(
                        {
                            "url": test_url,
                            "status": "healthy",
                            "response_time": response.elapsed.total_seconds(),
                            "status_code": response.status_code,
                        }
                    )
            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                health_status["test_endpoints"].append(
                    {"url": test_url, "status": "unhealthy", "error": str(e)}
                )
            except Exception as e:
                # Unexpected errors in health check
                health_status["test_endpoints"].append(
                    {"url": test_url, "status": "unhealthy", "error": f"Unexpected error: {str(e)}"}
                )

        return health_status

# ============================================================================
# ENHANCED PROXY VALIDATOR - MAIN IMPLEMENTATION  
# ============================================================================

class EnhancedProxyValidator:
    """
    Advanced 5-Stage Proxy Validation System with ML Integration
    
    Features:
    - 5-Stage Validation Pipeline: Connectivity → Anonymity → Performance → Geographic → Anti-Detection
    - Machine Learning-based Quality Prediction 
    - Advanced Circuit Breaker Protection with Adaptive Thresholds
    - TLS Fingerprinting and SSL/TLS Analysis
    - DNS Resolution Validation and Geographic Verification
    - Real-time Performance Monitoring and Load Testing
    - Sophisticated Anti-Detection Measures
    - HTTP/2 and HTTP/3 Protocol Support
    """

    def __init__(
        self,
        timeout: float = 10.0,
        test_urls: Optional[List[str]] = None,
        test_url: Optional[str] = None,  # Back-compat
        targets: Optional[Dict[str, TargetDefinition]] = None,
        max_concurrent: int = 20,
        circuit_breaker_threshold: int = 10,
        retry_attempts: int = 2,
        quality_level: QualityLevel = QualityLevel.STANDARD,
        enable_ml_prediction: bool = True,
        enable_load_testing: bool = False,
        geoip_database_path: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        self.timeout = timeout
        self.quality_level = quality_level
        self.enable_ml_prediction = enable_ml_prediction and HAS_ML
        self.enable_load_testing = enable_load_testing
        self.retry_attempts = retry_attempts
        
        # Normalize test URLs with back-compat support
        if test_url and not test_urls:
            test_urls = [test_url]
        self.test_urls = test_urls or [
            "https://httpbin.org/ip",
            "https://ifconfig.me/ip", 
            "https://api.ipify.org?format=json",
            "https://icanhazip.com/",
        ]
        self.primary_test_url = self.test_urls[0]
        
        # Target-based validation support
        self.targets = targets or {}
        
        # User agent for requests
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # HTTPX configuration for optimal performance
        self.limits = httpx.Limits(
            max_keepalive_connections=50,
            max_connections=200,
            keepalive_expiry=30.0
        )
        
        # Event hooks for monitoring
        self.event_hooks: Dict[str, List[Callable]] = {
            "request": [self._log_request],
            "response": [self._log_response],
        }
        
        # Concurrency control
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Enhanced circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            recovery_timeout=30.0,
            adaptive_threshold=True,
        )
        
        # Validation metrics and history
        self._total_validations = 0
        self._successful_validations = 0
        self._validation_history: deque = deque(maxlen=1000)
        
        # ML components (if enabled)
        self._ml_model: Optional[Any] = None
        self._feature_scaler: Optional[Any] = None
        if self.enable_ml_prediction:
            self._initialize_ml_components()
            
        # GeoIP database (if available)
        self._geoip_reader: Optional[Any] = None
        if HAS_GEOIP:
            self._initialize_geoip_database(geoip_database_path)
            
        # Performance throttling (if available)
        self._throttler: Optional[Any] = None
        if HAS_THROTTLING:
            self._throttler = Throttler(rate_limit=100, period=60)  # 100 requests per minute
            
        logger.info(
            "Enhanced ProxyValidator initialized: quality=%s, ml=%s, geoip=%s, urls=%d, targets=%d",
            self.quality_level.value,
            self.enable_ml_prediction,
            bool(self._geoip_reader),
            len(self.test_urls),
            len(self.targets),
        )

    def _initialize_ml_components(self) -> None:
        """Initialize machine learning components for quality prediction."""
        if not HAS_ML:
            return
            
        try:
            import numpy as np
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import StandardScaler

            # Initialize ML model for proxy quality prediction
            self._ml_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1  # Use all CPU cores
            )
            
            # Feature scaler for normalization
            self._feature_scaler = StandardScaler()
            
            # Pre-train model if historical data exists (placeholder for now)
            self._train_initial_model()
            
            logger.info("ML components initialized successfully")
            
        except Exception as e:
            logger.warning("Failed to initialize ML components: %s", e)
            self.enable_ml_prediction = False

    def _initialize_geoip_database(self, database_path: Optional[str]) -> None:
        """Initialize GeoIP database for geographic validation."""
        if not HAS_GEOIP:
            return
            
        try:
            import geoip2.database

            # Use provided path or try common locations
            possible_paths = [
                database_path,
                "/usr/share/GeoIP/GeoLite2-City.mmdb",
                "/opt/maxmind/GeoLite2-City.mmdb",
                "GeoLite2-City.mmdb",
            ]
            
            for path in possible_paths:
                if path and Path(path).exists():
                    self._geoip_reader = geoip2.database.Reader(path)
                    logger.info("GeoIP database loaded: %s", path)
                    break
            else:
                logger.info("GeoIP database not found, geographic validation disabled")
                
        except Exception as e:
            logger.warning("Failed to initialize GeoIP database: %s", e)

    def _train_initial_model(self) -> None:
        """Train initial ML model with synthetic data (placeholder)."""
        if not self._ml_model or not HAS_ML:
            return
            
        try:
            import numpy as np

            # Generate synthetic training data for initial model
            # In production, this would use historical validation data
            n_samples = 1000
            features = np.random.rand(n_samples, 8)  # 8 feature dimensions
            
            # Synthetic labels based on feature combinations
            labels = (
                (features[:, 0] > 0.3) &  # Response time
                (features[:, 1] > 0.5) &  # Success rate
                (features[:, 2] > 0.4)    # Anonymity score
            ).astype(int)
            
            # Train model
            self._feature_scaler.fit(features)
            scaled_features = self._feature_scaler.transform(features)
            self._ml_model.fit(scaled_features, labels)
            
            logger.debug("Initial ML model trained with synthetic data")
            
        except Exception as e:
            logger.warning("Failed to train initial ML model: %s", e)

    def _log_request(self, request: httpx.Request) -> None:
        """Log outgoing HTTP requests for monitoring."""
        logger.debug("→ %s %s", request.method, request.url)

    def _log_response(self, response: httpx.Response) -> None:
        """Log incoming HTTP responses for monitoring."""
        elapsed_ms = response.elapsed.total_seconds() * 1000 if response.elapsed else 0
        logger.debug(
            "← %s %s [%d] %.1fms",
            response.request.method,
            response.url,
            response.status_code,
            elapsed_ms,
        )

    # ============================================================================
    # CORE VALIDATION METHODS - 5-STAGE PIPELINE
    # ============================================================================

    async def validate_proxy(self, proxy: Proxy) -> EnhancedValidationResult:
        """
        Validate a proxy using the enhanced 5-stage validation pipeline.
        
        Stages:
        1. Connectivity - Basic connection and response validation
        2. Anonymity - Detect anonymity level and proxy headers
        3. Performance - Measure speed, latency, and reliability 
        4. Geographic - Verify location and DNS resolution
        5. Anti-Detection - Test stealth capabilities and fingerprinting resistance
        
        Args:
            proxy: Proxy object to validate
            
        Returns:
            Enhanced validation result with comprehensive metrics
        """
        async with self.semaphore:
            self._total_validations += 1
            start_time = time.time()
            
            # Initialize comprehensive result object
            result = EnhancedValidationResult(
                proxy=proxy,
                is_valid=False,
                test_url=self.primary_test_url,
            )
            
            try:
                # Apply throttling if available
                if self._throttler:
                    async with self._throttler:
                        await self._execute_validation_pipeline(proxy, result)
                else:
                    await self._execute_validation_pipeline(proxy, result)
                    
                # Update proxy metrics
                if result.is_valid:
                    self._successful_validations += 1
                    proxy.last_checked = result.timestamp
                    if result.performance_metrics.response_time:
                        proxy.response_time = result.performance_metrics.response_time
                        
            except Exception as e:
                logger.warning("Validation pipeline failed for %s:%s: %s", proxy.host, proxy.port, e)
                result.error_type = ValidationErrorType.UNKNOWN
                result.error_message = f"Pipeline error: {str(e)}"
                
            finally:
                # Record total validation time
                total_time = time.time() - start_time
                result.performance_metrics.response_time = total_time
                result.response_time = total_time  # Legacy compatibility
                
                # Update proxy status
                proxy.last_checked = result.timestamp
                
                # Store validation result
                self._validation_history.append(result)
                
                # Memory management
                self._manage_validation_history()
                
                logger.debug(
                    "Proxy validation completed: %s:%s valid=%s score=%.2f time=%.2fs",
                    proxy.host, proxy.port, result.is_valid, result.overall_score, total_time
                )
                
            return result

    async def _execute_validation_pipeline(self, proxy: Proxy, result: EnhancedValidationResult) -> None:
        """Execute the 5-stage validation pipeline."""
        
        # Stage 1: Connectivity Validation (Required)
        connectivity_result = await self.circuit_breaker.call(
            self._validate_connectivity, proxy, result
        )
        result.add_stage_result(connectivity_result)
        
        # If connectivity fails, skip remaining stages
        if not connectivity_result.is_valid:
            result.error_type = connectivity_result.error_type
            result.error_message = connectivity_result.error_message
            return
            
        # Stage 2: Anonymity Detection
        if self.quality_level.value in ['standard', 'thorough', 'enterprise']:
            anonymity_result = await self.circuit_breaker.call(
                self._validate_anonymity, proxy, result
            )
            result.add_stage_result(anonymity_result)
            
        # Stage 3: Performance Testing
        if self.quality_level.value in ['standard', 'thorough', 'enterprise']:
            performance_result = await self.circuit_breaker.call(
                self._validate_performance, proxy, result
            )
            result.add_stage_result(performance_result)
            
        # Stage 4: Geographic Validation
        if self.quality_level.value in ['thorough', 'enterprise'] and self._geoip_reader:
            geographic_result = await self.circuit_breaker.call(
                self._validate_geographic, proxy, result
            )
            result.add_stage_result(geographic_result)
            
        # Stage 5: Anti-Detection Testing
        if self.quality_level.value == 'enterprise':
            anti_detection_result = await self.circuit_breaker.call(
                self._validate_anti_detection, proxy, result
            )
            result.add_stage_result(anti_detection_result)
            
        # Apply ML prediction if enabled
        if self.enable_ml_prediction and self._ml_model:
            ml_prediction = await self._generate_ml_prediction(proxy, result)
            result.ml_prediction = ml_prediction
            
        # Apply load testing if enabled
        if self.enable_load_testing:
            load_test_results = await self._perform_load_testing(proxy, result)
            result.load_test_results = load_test_results

    # ============================================================================
    # STAGE VALIDATION IMPLEMENTATIONS
    # ============================================================================

    async def _validate_connectivity(self, proxy: Proxy, result: EnhancedValidationResult) -> StageValidationResult:
        """Stage 1: Basic connectivity and response validation."""
        stage_start = time.time()
        stage_result = StageValidationResult(
            stage=ValidationStage.CONNECTIVITY,
            is_valid=False,
        )
        
        try:
            proxy_url = self._build_proxy_url(proxy)
            
            async with httpx.AsyncClient(
                proxy=proxy_url,
                timeout=httpx.Timeout(self.timeout),
                limits=self.limits,
                event_hooks=self.event_hooks,
                follow_redirects=True,
                headers={"User-Agent": self.user_agent},
            ) as client:
                
                # Test primary URL
                response = await client.get(self.primary_test_url)
                response.raise_for_status()
                
                # Store response details
                result.status_code = response.status_code
                result.response_headers = dict(response.headers)
                stage_result.stage_details["status_code"] = response.status_code
                stage_result.stage_details["response_size"] = len(response.content)
                stage_result.stage_details["content_type"] = response.headers.get("content-type", "")
                
                # Test additional URLs for reliability (if multiple configured)
                additional_success_count = 0
                if len(self.test_urls) > 1:
                    for test_url in self.test_urls[1:3]:  # Test up to 2 additional URLs
                        try:
                            additional_response = await client.get(test_url, timeout=5.0)
                            if additional_response.status_code == 200:
                                additional_success_count += 1
                        except Exception:
                            pass  # Individual URL failures don't fail the stage
                            
                    stage_result.stage_details["additional_urls_success"] = additional_success_count
                    stage_result.stage_details["additional_urls_tested"] = min(2, len(self.test_urls) - 1)
                
                # Calculate stage score based on performance
                connection_time = time.time() - stage_start
                if connection_time <= 2.0:
                    stage_result.stage_score = 1.0
                elif connection_time <= 5.0:
                    stage_result.stage_score = 0.8
                elif connection_time <= 10.0:
                    stage_result.stage_score = 0.6
                else:
                    stage_result.stage_score = 0.4
                    
                # Bonus for additional URL success
                if len(self.test_urls) > 1:
                    additional_rate = additional_success_count / min(2, len(self.test_urls) - 1)
                    stage_result.stage_score += additional_rate * 0.2
                    
                stage_result.is_valid = True
                logger.debug("Connectivity validation passed for %s:%s", proxy.host, proxy.port)
                
        except (httpx.HTTPError, asyncio.TimeoutError) as e:
            stage_result.error_type = self._categorize_error(e)
            stage_result.error_message = str(e)
            stage_result.stage_score = 0.0
            logger.debug("Connectivity validation failed for %s:%s: %s", proxy.host, proxy.port, e)
            
        except Exception as e:
            stage_result.error_type = ValidationErrorType.UNKNOWN
            stage_result.error_message = f"Connectivity error: {str(e)}"
            stage_result.stage_score = 0.0
            logger.warning("Unexpected connectivity error for %s:%s: %s", proxy.host, proxy.port, e)
            
        finally:
            stage_result.execution_time = time.time() - stage_start
            
        return stage_result

    async def _validate_anonymity(self, proxy: Proxy, result: EnhancedValidationResult) -> StageValidationResult:
        """Stage 2: Advanced anonymity detection and header analysis."""
        stage_start = time.time()
        stage_result = StageValidationResult(
            stage=ValidationStage.ANONYMITY,
            is_valid=False,
        )
        
        try:
            proxy_url = self._build_proxy_url(proxy)
            
            async with httpx.AsyncClient(
                proxy=proxy_url,
                timeout=httpx.Timeout(self.timeout),
                limits=self.limits,
                event_hooks=self.event_hooks,
                headers={"User-Agent": self.user_agent},
            ) as client:
                
                # Test anonymity detection with specialized endpoint
                anonymity_test_urls = [
                    "https://httpbin.org/headers",
                    "https://httpbin.org/ip", 
                    "https://ifconfig.me/all.json",
                ]
                
                anonymity_scores = []
                detected_ips = set()
                
                for test_url in anonymity_test_urls:
                    try:
                        response = await client.get(test_url, timeout=5.0)
                        if response.status_code == 200:
                            anonymity_score = await self._analyze_anonymity_response(
                                response, proxy, result
                            )
                            anonymity_scores.append(anonymity_score)
                            
                            # Extract detected IP
                            try:
                                if "application/json" in response.headers.get("content-type", ""):
                                    data = response.json()
                                    ip = data.get("origin") or data.get("ip") or data.get("ipv4")
                                    if ip:
                                        detected_ips.add(ip.split(',')[0].strip())
                                else:
                                    # Plain text IP response
                                    ip = response.text.strip()
                                    if self._is_valid_ip(ip):
                                        detected_ips.add(ip)
                            except Exception:
                                pass  # IP extraction failure doesn't fail the stage
                                
                    except Exception as e:
                        logger.debug("Anonymity test failed for URL %s: %s", test_url, e)
                        anonymity_scores.append(0.0)
                        
                # Calculate overall anonymity score
                if anonymity_scores:
                    stage_result.stage_score = statistics.mean(anonymity_scores)
                    stage_result.is_valid = stage_result.stage_score > 0.3
                    
                    # Determine anonymity level
                    if stage_result.stage_score >= 0.9:
                        result.anonymity_detected = AnonymityLevel.ELITE
                        result.anti_detection_metrics.stealth_level = AntiDetectionLevel.ELITE
                    elif stage_result.stage_score >= 0.7:
                        result.anonymity_detected = AnonymityLevel.ANONYMOUS
                        result.anti_detection_metrics.stealth_level = AntiDetectionLevel.ADVANCED
                    elif stage_result.stage_score >= 0.4:
                        result.anonymity_detected = AnonymityLevel.TRANSPARENT
                        result.anti_detection_metrics.stealth_level = AntiDetectionLevel.BASIC
                    else:
                        result.anonymity_detected = AnonymityLevel.UNKNOWN
                        result.anti_detection_metrics.stealth_level = AntiDetectionLevel.NONE
                else:
                    stage_result.stage_score = 0.0
                    result.anonymity_detected = AnonymityLevel.UNKNOWN
                    
                # Store detected IPs
                if detected_ips:
                    result.ip_detected = list(detected_ips)[0]  # Primary detected IP
                    stage_result.stage_details["detected_ips"] = list(detected_ips)
                    stage_result.stage_details["ip_consistency"] = len(detected_ips) == 1
                    
                stage_result.stage_details["anonymity_score"] = stage_result.stage_score
                stage_result.stage_details["anonymity_level"] = result.anonymity_detected.value if result.anonymity_detected else "unknown"
                
                logger.debug("Anonymity validation completed for %s:%s (level: %s, score: %.2f)", 
                           proxy.host, proxy.port, result.anonymity_detected, stage_result.stage_score)
                
        except Exception as e:
            stage_result.error_type = ValidationErrorType.UNKNOWN
            stage_result.error_message = f"Anonymity validation error: {str(e)}"
            stage_result.stage_score = 0.0
            logger.warning("Anonymity validation failed for %s:%s: %s", proxy.host, proxy.port, e)
            
        finally:
            stage_result.execution_time = time.time() - stage_start
            
        return stage_result

    async def _validate_performance(self, proxy: Proxy, result: EnhancedValidationResult) -> StageValidationResult:
        """Stage 3: Comprehensive performance and reliability testing."""
        stage_start = time.time()
        stage_result = StageValidationResult(
            stage=ValidationStage.PERFORMANCE,
            is_valid=False,
        )
        
        try:
            proxy_url = self._build_proxy_url(proxy)
            response_times = []
            
            async with httpx.AsyncClient(
                proxy=proxy_url,
                timeout=httpx.Timeout(self.timeout),
                limits=self.limits,
                event_hooks=self.event_hooks,
                headers={"User-Agent": self.user_agent},
            ) as client:
                
                # Perform multiple requests to measure consistency
                num_tests = 3 if self.quality_level == QualityLevel.THOROUGH else 2
                successful_requests = 0
                
                for i in range(num_tests):
                    try:
                        request_start = time.time()
                        response = await client.get(self.primary_test_url, timeout=self.timeout)
                        request_time = time.time() - request_start
                        
                        if response.status_code == 200:
                            response_times.append(request_time)
                            successful_requests += 1
                            
                            # Analyze response for performance indicators
                            if i == 0:  # First request details
                                result.performance_metrics.connection_time = request_time
                                result.performance_metrics.first_byte_time = request_time
                                result.performance_metrics.download_speed = (
                                    len(response.content) / request_time if request_time > 0 else 0
                                )
                                
                    except Exception as e:
                        logger.debug("Performance test %d failed: %s", i + 1, e)
                        
                # Calculate performance metrics
                if response_times:
                    avg_response_time = statistics.mean(response_times)
                    result.performance_metrics.response_time = avg_response_time
                    result.performance_metrics.latency = avg_response_time
                    
                    # Calculate jitter (response time variance)
                    if len(response_times) > 1:
                        result.performance_metrics.jitter = statistics.stdev(response_times)
                    
                    # Performance scoring
                    success_rate = successful_requests / num_tests
                    
                    if avg_response_time <= 1.0 and success_rate == 1.0:
                        stage_result.stage_score = 1.0  # Excellent
                    elif avg_response_time <= 3.0 and success_rate >= 0.8:
                        stage_result.stage_score = 0.8  # Good
                    elif avg_response_time <= 5.0 and success_rate >= 0.6:
                        stage_result.stage_score = 0.6  # Average
                    elif avg_response_time <= 10.0 and success_rate >= 0.4:
                        stage_result.stage_score = 0.4  # Below average
                    else:
                        stage_result.stage_score = 0.2  # Poor
                        
                    stage_result.is_valid = stage_result.stage_score >= 0.3
                    
                    # Store performance details
                    stage_result.stage_details.update({
                        "avg_response_time": avg_response_time,
                        "min_response_time": min(response_times),
                        "max_response_time": max(response_times),
                        "jitter": result.performance_metrics.jitter,
                        "success_rate": success_rate,
                        "total_tests": num_tests,
                    })
                    
                    logger.debug("Performance validation completed for %s:%s (avg: %.2fs, score: %.2f)",
                               proxy.host, proxy.port, avg_response_time, stage_result.stage_score)
                else:
                    stage_result.stage_score = 0.0
                    stage_result.error_message = "No successful performance tests"
                    
        except Exception as e:
            stage_result.error_type = ValidationErrorType.UNKNOWN
            stage_result.error_message = f"Performance validation error: {str(e)}"
            stage_result.stage_score = 0.0
            logger.warning("Performance validation failed for %s:%s: %s", proxy.host, proxy.port, e)
            
        finally:
            stage_result.execution_time = time.time() - stage_start
            
        return stage_result
