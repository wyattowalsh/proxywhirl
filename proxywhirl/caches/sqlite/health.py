"""proxywhirl/caches/db/health.py -- Health monitoring and analytics for SQLite cache implementations

Provides comprehensive health monitoring, analytics, and performance tracking
for both synchronous and asynchronous SQLite cache implementations.

Features:
- Real-time health metrics collection and monitoring
- Performance analytics with trend analysis
- Connection pool health monitoring for async implementations
- Configurable health thresholds and alerting
- Detailed proxy health scoring and quality assessment
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import desc
from sqlmodel import select, text

from proxywhirl.models import Proxy

from .models import ProxyRecord


class HealthThresholds:
    """Configurable health thresholds for cache monitoring."""
    
    def __init__(
        self,
        min_healthy_ratio: float = 0.7,  # 70% healthy proxies minimum
        max_response_time_ms: float = 3000.0,  # 3 second max response time
        stale_proxy_hours: int = 24,  # Consider proxies stale after 24 hours
        critical_unhealthy_ratio: float = 0.9,  # Critical if 90%+ unhealthy
    ):
        """
        Initialize health monitoring thresholds.
        
        Args:
            min_healthy_ratio: Minimum ratio of healthy proxies (0.0-1.0)
            max_response_time_ms: Maximum acceptable response time in milliseconds
            stale_proxy_hours: Hours after which to consider a proxy stale
            critical_unhealthy_ratio: Ratio above which cache health is critical
        """
        self.min_healthy_ratio = min_healthy_ratio
        self.max_response_time_ms = max_response_time_ms
        self.stale_proxy_hours = stale_proxy_hours
        self.critical_unhealthy_ratio = critical_unhealthy_ratio


class ProxyHealthScore:
    """Detailed health scoring for individual proxies."""
    
    def __init__(
        self,
        proxy: Proxy,
        health_score: float,
        response_time_score: float,
        anonymity_score: float,
        reliability_score: float,
        freshness_score: float,
        overall_grade: str,
    ):
        """
        Initialize proxy health score.
        
        Args:
            proxy: The proxy being scored
            health_score: Basic health score (0.0-1.0)
            response_time_score: Performance score based on response time
            anonymity_score: Anonymity/security score
            reliability_score: Historical reliability score
            freshness_score: Data freshness score
            overall_grade: Letter grade (A+ to F)
        """
        self.proxy = proxy
        self.health_score = health_score
        self.response_time_score = response_time_score
        self.anonymity_score = anonymity_score
        self.reliability_score = reliability_score
        self.freshness_score = freshness_score
        self.overall_grade = overall_grade
    
    @property
    def combined_score(self) -> float:
        """Calculate combined weighted score."""
        return (
            self.health_score * 0.3 +
            self.response_time_score * 0.25 +
            self.anonymity_score * 0.2 +
            self.reliability_score * 0.15 +
            self.freshness_score * 0.1
        )


class CacheHealthStatus:
    """Comprehensive cache health status."""
    
    def __init__(
        self,
        is_healthy: bool,
        health_grade: str,
        total_proxies: int,
        healthy_proxies: int,
        unhealthy_proxies: int,
        stale_proxies: int,
        avg_response_time: float,
        health_ratio: float,
        connection_pool_health: Optional[Dict[str, Union[int, float]]] = None,
        top_performing_proxies: Optional[List[ProxyHealthScore]] = None,
        recommendations: Optional[List[str]] = None,
        last_updated: Optional[datetime] = None,
    ):
        """
        Initialize comprehensive cache health status.
        
        Args:
            is_healthy: Overall health status boolean
            health_grade: Letter grade for overall health (A+ to F)
            total_proxies: Total number of cached proxies
            healthy_proxies: Number of healthy proxies
            unhealthy_proxies: Number of unhealthy proxies
            stale_proxies: Number of stale/outdated proxies
            avg_response_time: Average response time of healthy proxies
            health_ratio: Ratio of healthy to total proxies
            connection_pool_health: Connection pool metrics (for async caches)
            top_performing_proxies: List of best performing proxies
            recommendations: List of health improvement recommendations
            last_updated: When this status was generated
        """
        self.is_healthy = is_healthy
        self.health_grade = health_grade
        self.total_proxies = total_proxies
        self.healthy_proxies = healthy_proxies
        self.unhealthy_proxies = unhealthy_proxies
        self.stale_proxies = stale_proxies
        self.avg_response_time = avg_response_time
        self.health_ratio = health_ratio
        self.connection_pool_health = connection_pool_health or {}
        self.top_performing_proxies = top_performing_proxies or []
        self.recommendations = recommendations or []
        self.last_updated = last_updated or datetime.now(timezone.utc)


class SQLiteHealthMonitor:
    """Health monitoring utility for SQLite cache implementations."""
    
    def __init__(self, thresholds: Optional[HealthThresholds] = None):
        """
        Initialize health monitor with configurable thresholds.
        
        Args:
            thresholds: Health monitoring thresholds
        """
        self.thresholds = thresholds or HealthThresholds()
    
    def calculate_proxy_health_score(self, record: ProxyRecord) -> ProxyHealthScore:
        """
        Calculate detailed health score for a single proxy record.
        
        Args:
            record: ProxyRecord from database
            
        Returns:
            ProxyHealthScore with detailed metrics
        """
        import json
        now = datetime.now(timezone.utc)
        
        # Parse proxy metadata to extract health information
        try:
            metadata = json.loads(record.proxy_metadata) if record.proxy_metadata else {}
        except (json.JSONDecodeError, TypeError):
            metadata = {}
            
        # Extract health info from metadata or use defaults
        is_healthy = metadata.get('is_healthy', record.status == 'ACTIVE')
        response_time_ms = metadata.get('response_time_ms', 0)
        is_anonymous = record.anonymity != 'TRANSPARENT'
        is_https = 'https' in record.schemes.lower() if record.schemes else False
        
        # Basic health score
        health_score = 1.0 if is_healthy else 0.0
        
        # Response time score (inverse relationship, lower is better)
        if response_time_ms and response_time_ms > 0:
            # Score from 1.0 (fast) to 0.0 (slow)
            max_time = self.thresholds.max_response_time_ms
            response_time_score = max(0.0, 1.0 - (response_time_ms / max_time))
        else:
            response_time_score = 0.0
        
        # Anonymity score
        anonymity_score = 1.0 if is_anonymous else 0.5
        if is_https:
            anonymity_score = min(1.0, anonymity_score + 0.2)
        
        # Reliability score based on quality score
        if record.quality_score:
            reliability_score = min(1.0, float(record.quality_score))
        else:
            reliability_score = 0.5  # Default for unknown reliability
        
        # Freshness score based on last check time
        if record.last_checked:
            hours_since_check = (now - record.last_checked).total_seconds() / 3600
            if hours_since_check <= 1:
                freshness_score = 1.0
            elif hours_since_check <= 6:
                freshness_score = 0.8
            elif hours_since_check <= 24:
                freshness_score = 0.6
            elif hours_since_check <= 72:
                freshness_score = 0.3
            else:
                freshness_score = 0.1
        else:
            freshness_score = 0.0
        
        # Calculate combined score and grade
        combined_score = (
            health_score * 0.3 +
            response_time_score * 0.25 +
            anonymity_score * 0.2 +
            reliability_score * 0.15 +
            freshness_score * 0.1
        )
        
        # Assign letter grade
        if combined_score >= 0.95:
            grade = "A+"
        elif combined_score >= 0.90:
            grade = "A"
        elif combined_score >= 0.85:
            grade = "A-"
        elif combined_score >= 0.80:
            grade = "B+"
        elif combined_score >= 0.75:
            grade = "B"
        elif combined_score >= 0.70:
            grade = "B-"
        elif combined_score >= 0.65:
            grade = "C+"
        elif combined_score >= 0.60:
            grade = "C"
        elif combined_score >= 0.55:
            grade = "C-"
        elif combined_score >= 0.50:
            grade = "D"
        else:
            grade = "F"
        
        # Convert record to proxy
        proxy = Proxy(
            scheme=record.schemes.split(',')[0] if record.schemes else 'http',
            host=record.host,
            port=record.port,
            username=metadata.get('username'),
            password=metadata.get('password'),
            country=record.country,
        )
        
        return ProxyHealthScore(
            proxy=proxy,
            health_score=health_score,
            response_time_score=response_time_score,
            anonymity_score=anonymity_score,
            reliability_score=reliability_score,
            freshness_score=freshness_score,
            overall_grade=grade,
        )
    
    async def assess_cache_health_async(self, session, engine=None) -> CacheHealthStatus:
        """
        Perform comprehensive cache health assessment (async version).
        
        Args:
            session: Async SQLAlchemy session
            engine: Optional async engine for connection pool metrics
            
        Returns:
            CacheHealthStatus with complete assessment
        """
        now = datetime.now(timezone.utc)
        
        # Get basic metrics
        total_result = await session.execute(text("SELECT COUNT(*) FROM proxy_records"))
        total_proxies = total_result.scalar() or 0
        
        healthy_result = await session.execute(
            text("SELECT COUNT(*) FROM proxy_records WHERE is_healthy = 1")
        )
        healthy_proxies = healthy_result.scalar() or 0
        
        unhealthy_proxies = total_proxies - healthy_proxies
        
        # Calculate stale proxies
        stale_cutoff = now - timedelta(hours=self.thresholds.stale_proxy_hours)
        stale_result = await session.execute(
            text("SELECT COUNT(*) FROM proxy_records WHERE last_checked < :cutoff"),
            {"cutoff": stale_cutoff}
        )
        stale_proxies = stale_result.scalar() or 0
        
        # Average response time for healthy proxies
        avg_response_result = await session.execute(
            text("SELECT AVG(response_time_ms) FROM proxy_records WHERE is_healthy = 1")
        )
        avg_response_time = avg_response_result.scalar() or 0.0
        
        # Health ratio
        health_ratio = healthy_proxies / max(total_proxies, 1)
        
        # Get top performing proxies based on status and quality
        top_proxies_result = await session.execute(
            select(ProxyRecord)
            .where(ProxyRecord.status == 'ACTIVE')
            .order_by(ProxyRecord.quality_score.desc(), ProxyRecord.last_checked.desc())
            .limit(10)
        )
        top_records = top_proxies_result.scalars().all()
        top_performing_proxies = [self.calculate_proxy_health_score(record) for record in top_records]
        
        # Connection pool health (for async implementations)
        connection_pool_health = {}
        if engine and hasattr(engine, 'pool'):
            pool = engine.pool
            connection_pool_health = {
                "pool_size": pool.size(),
                "checked_out": pool.checkedout(),
                "checked_in": pool.checkedin(),
                "overflow": pool.overflow(),
                "utilization_ratio": pool.checkedout() / max(pool.size(), 1),
            }
        
        # Determine overall health
        is_healthy = (
            health_ratio >= self.thresholds.min_healthy_ratio and
            avg_response_time <= self.thresholds.max_response_time_ms and
            health_ratio < self.thresholds.critical_unhealthy_ratio
        )
        
        # Calculate health grade
        if health_ratio >= 0.95 and avg_response_time <= 1000:
            health_grade = "A+"
        elif health_ratio >= 0.90 and avg_response_time <= 1500:
            health_grade = "A"
        elif health_ratio >= 0.85 and avg_response_time <= 2000:
            health_grade = "B+"
        elif health_ratio >= 0.80 and avg_response_time <= 2500:
            health_grade = "B"
        elif health_ratio >= 0.70 and avg_response_time <= 3000:
            health_grade = "C"
        elif health_ratio >= 0.60:
            health_grade = "D"
        else:
            health_grade = "F"
        
        # Generate recommendations
        recommendations = []
        
        if health_ratio < self.thresholds.min_healthy_ratio:
            recommendations.append(f"Health ratio ({health_ratio:.2%}) below threshold ({self.thresholds.min_healthy_ratio:.2%})")
        
        if avg_response_time > self.thresholds.max_response_time_ms:
            recommendations.append(f"Average response time ({avg_response_time:.0f}ms) exceeds threshold ({self.thresholds.max_response_time_ms:.0f}ms)")
        
        if stale_proxies > total_proxies * 0.1:  # More than 10% stale
            recommendations.append(f"High number of stale proxies: {stale_proxies}/{total_proxies} ({stale_proxies/max(total_proxies,1):.1%})")
        
        if total_proxies < 10:
            recommendations.append("Low proxy count - consider fetching more proxies")
        
        if connection_pool_health and connection_pool_health.get("utilization_ratio", 0) > 0.8:
            recommendations.append("High connection pool utilization - consider increasing pool size")
        
        return CacheHealthStatus(
            is_healthy=is_healthy,
            health_grade=health_grade,
            total_proxies=total_proxies,
            healthy_proxies=healthy_proxies,
            unhealthy_proxies=unhealthy_proxies,
            stale_proxies=stale_proxies,
            avg_response_time=avg_response_time,
            health_ratio=health_ratio,
            connection_pool_health=connection_pool_health,
            top_performing_proxies=top_performing_proxies,
            recommendations=recommendations,
        )
    
    def assess_cache_health_sync(self, session) -> CacheHealthStatus:
        """
        Perform comprehensive cache health assessment (sync version).
        
        Args:
            session: Sync SQLAlchemy session
            
        Returns:
            CacheHealthStatus with complete assessment
        """
        now = datetime.now(timezone.utc)
        
        # Get basic metrics
        total_result = session.execute(text("SELECT COUNT(*) FROM proxy_records"))
        total_proxies = total_result.scalar() or 0
        
        healthy_result = session.execute(
            text("SELECT COUNT(*) FROM proxy_records WHERE is_healthy = 1")
        )
        healthy_proxies = healthy_result.scalar() or 0
        
        unhealthy_proxies = total_proxies - healthy_proxies
        
        # Calculate stale proxies
        stale_cutoff = now - timedelta(hours=self.thresholds.stale_proxy_hours)
        stale_result = session.execute(
            text("SELECT COUNT(*) FROM proxy_records WHERE last_checked < :cutoff"),
            {"cutoff": stale_cutoff}
        )
        stale_proxies = stale_result.scalar() or 0
        
        # Average response time for healthy proxies
        avg_response_result = session.execute(
            text("SELECT AVG(response_time_ms) FROM proxy_records WHERE is_healthy = 1")
        )
        avg_response_time = avg_response_result.scalar() or 0.0
        
        # Health ratio
        health_ratio = healthy_proxies / max(total_proxies, 1)
        
        # Get top performing proxies
        top_proxies_result = session.execute(
            select(ProxyRecord)
            .where(ProxyRecord.is_healthy == True)
            .order_by(ProxyRecord.quality_score.desc(), ProxyRecord.response_time_ms.asc())
            .limit(10)
        )
        top_records = top_proxies_result.scalars().all()
        top_performing_proxies = [self.calculate_proxy_health_score(record) for record in top_records]
        
        # Determine overall health
        is_healthy = (
            health_ratio >= self.thresholds.min_healthy_ratio and
            avg_response_time <= self.thresholds.max_response_time_ms and
            health_ratio < self.thresholds.critical_unhealthy_ratio
        )
        
        # Calculate health grade
        if health_ratio >= 0.95 and avg_response_time <= 1000:
            health_grade = "A+"
        elif health_ratio >= 0.90 and avg_response_time <= 1500:
            health_grade = "A"
        elif health_ratio >= 0.85 and avg_response_time <= 2000:
            health_grade = "B+"
        elif health_ratio >= 0.80 and avg_response_time <= 2500:
            health_grade = "B"
        elif health_ratio >= 0.70 and avg_response_time <= 3000:
            health_grade = "C"
        elif health_ratio >= 0.60:
            health_grade = "D"
        else:
            health_grade = "F"
        
        # Generate recommendations
        recommendations = []
        
        if health_ratio < self.thresholds.min_healthy_ratio:
            recommendations.append(f"Health ratio ({health_ratio:.2%}) below threshold ({self.thresholds.min_healthy_ratio:.2%})")
        
        if avg_response_time > self.thresholds.max_response_time_ms:
            recommendations.append(f"Average response time ({avg_response_time:.0f}ms) exceeds threshold ({self.thresholds.max_response_time_ms:.0f}ms)")
        
        if stale_proxies > total_proxies * 0.1:  # More than 10% stale
            recommendations.append(f"High number of stale proxies: {stale_proxies}/{total_proxies} ({stale_proxies/max(total_proxies,1):.1%})")
        
        if total_proxies < 10:
            recommendations.append("Low proxy count - consider fetching more proxies")
        
        return CacheHealthStatus(
            is_healthy=is_healthy,
            health_grade=health_grade,
            total_proxies=total_proxies,
            healthy_proxies=healthy_proxies,
            unhealthy_proxies=unhealthy_proxies,
            stale_proxies=stale_proxies,
            avg_response_time=avg_response_time,
            health_ratio=health_ratio,
            top_performing_proxies=top_performing_proxies,
            recommendations=recommendations,
        )
        )
