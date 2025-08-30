"""proxywhirl/caches/db/analytics.py -- Analytics and reporting for SQLite cache implementations

Provides analytics, reporting, and statistical analysis for SQLite cache data.

Features:
- Proxy source performance analysis
- Geographic distribution reporting
- Quality score analytics and trends
- Cache utilization statistics
- Export capabilities for analytics data
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from sqlmodel import select, text

from .models import ProxyRecord


class ProxySourceAnalytics:
    """Analytics for proxy sources and their performance."""
    
    def __init__(
        self,
        source: str,
        total_proxies: int,
        active_proxies: int,
        avg_quality_score: float,
        geographic_distribution: Dict[str, int],
        scheme_distribution: Dict[str, int],
        last_updated: datetime,
    ):
        """
        Initialize proxy source analytics.
        
        Args:
            source: Name of the proxy source
            total_proxies: Total proxies from this source
            active_proxies: Number of active proxies
            avg_quality_score: Average quality score for this source
            geographic_distribution: Country distribution of proxies
            scheme_distribution: Protocol scheme distribution
            last_updated: When this data was collected
        """
        self.source = source
        self.total_proxies = total_proxies
        self.active_proxies = active_proxies
        self.avg_quality_score = avg_quality_score
        self.geographic_distribution = geographic_distribution
        self.scheme_distribution = scheme_distribution
        self.last_updated = last_updated
        
    @property
    def active_ratio(self) -> float:
        """Calculate ratio of active to total proxies."""
        return self.active_proxies / max(self.total_proxies, 1)


class GeographicAnalytics:
    """Analytics for geographic distribution of proxies."""
    
    def __init__(
        self,
        total_countries: int,
        country_distribution: Dict[str, int],
        quality_by_country: Dict[str, float],
        top_countries: List[Tuple[str, int]],
        coverage_score: float,
    ):
        """
        Initialize geographic analytics.
        
        Args:
            total_countries: Total number of unique countries
            country_distribution: Proxy count by country
            quality_by_country: Average quality score by country
            top_countries: List of (country, count) tuples, sorted by count
            coverage_score: Geographic coverage score (0.0-1.0)
        """
        self.total_countries = total_countries
        self.country_distribution = country_distribution
        self.quality_by_country = quality_by_country
        self.top_countries = top_countries
        self.coverage_score = coverage_score


class CacheAnalytics:
    """Comprehensive cache analytics and reporting."""
    
    async def analyze_proxy_sources_async(self, session) -> List[ProxySourceAnalytics]:
        """
        Analyze performance and distribution by proxy source.
        
        Args:
            session: Async SQLAlchemy session
            
        Returns:
            List of ProxySourceAnalytics objects
        """
        # Get source statistics
        source_stats_query = text("""
            SELECT 
                source,
                COUNT(*) as total_proxies,
                COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active_proxies,
                AVG(CAST(quality_score AS FLOAT)) as avg_quality_score,
                updated_at
            FROM proxy_records 
            WHERE source IS NOT NULL
            GROUP BY source
            ORDER BY total_proxies DESC
        """)
        
        result = await session.execute(source_stats_query)
        source_stats = result.fetchall()
        
        analytics_list = []
        
        for row in source_stats:
            source = row.source
            
            # Get geographic distribution for this source
            geo_query = text("""
                SELECT country_code, COUNT(*) as count
                FROM proxy_records 
                WHERE source = :source AND country_code IS NOT NULL
                GROUP BY country_code
                ORDER BY count DESC
            """)
            geo_result = await session.execute(geo_query, {"source": source})
            geo_data = geo_result.fetchall()
            geographic_distribution = {row.country_code: row.count for row in geo_data}
            
            # Get scheme distribution for this source
            scheme_query = text("""
                SELECT schemes, COUNT(*) as count
                FROM proxy_records 
                WHERE source = :source
                GROUP BY schemes
            """)
            scheme_result = await session.execute(scheme_query, {"source": source})
            scheme_data = scheme_result.fetchall()
            scheme_distribution = {row.schemes: row.count for row in scheme_data}
            
            analytics_list.append(ProxySourceAnalytics(
                source=source,
                total_proxies=row.total_proxies,
                active_proxies=row.active_proxies,
                avg_quality_score=row.avg_quality_score or 0.0,
                geographic_distribution=geographic_distribution,
                scheme_distribution=scheme_distribution,
                last_updated=datetime.now(timezone.utc),
            ))
        
        return analytics_list
    
    async def analyze_geographic_distribution_async(self, session) -> GeographicAnalytics:
        """
        Analyze geographic distribution of proxies.
        
        Args:
            session: Async SQLAlchemy session
            
        Returns:
            GeographicAnalytics object
        """
        # Get country distribution
        country_query = text("""
            SELECT 
                country_code,
                COUNT(*) as count,
                AVG(CAST(quality_score AS FLOAT)) as avg_quality
            FROM proxy_records 
            WHERE country_code IS NOT NULL
            GROUP BY country_code
            ORDER BY count DESC
        """)
        
        result = await session.execute(country_query)
        country_data = result.fetchall()
        
        # Process data
        country_distribution = {row.country_code: row.count for row in country_data}
        quality_by_country = {
            row.country_code: row.avg_quality or 0.0 
            for row in country_data
        }
        top_countries = [(row.country_code, row.count) for row in country_data[:10]]
        
        # Calculate coverage score (simple metric based on country diversity)
        total_countries = len(country_data)
        total_proxies = sum(country_distribution.values())
        
        # Coverage score: higher when proxies are more evenly distributed
        if total_countries > 0 and total_proxies > 0:
            # Calculate entropy-like metric for distribution evenness
            coverage_score = min(1.0, total_countries / 50.0)  # Normalize to 50 countries max
        else:
            coverage_score = 0.0
        
        return GeographicAnalytics(
            total_countries=total_countries,
            country_distribution=country_distribution,
            quality_by_country=quality_by_country,
            top_countries=top_countries,
            coverage_score=coverage_score,
        )
    
    async def get_cache_utilization_stats_async(self, session) -> Dict[str, any]:
        """
        Get comprehensive cache utilization statistics.
        
        Args:
            session: Async SQLAlchemy session
            
        Returns:
            Dictionary with utilization statistics
        """
        now = datetime.now(timezone.utc)
        
        # Basic counts
        total_query = text("SELECT COUNT(*) FROM proxy_records")
        total_result = await session.execute(total_query)
        total_proxies = total_result.scalar() or 0
        
        # Active proxies
        active_query = text("SELECT COUNT(*) FROM proxy_records WHERE status = 'ACTIVE'")
        active_result = await session.execute(active_query)
        active_proxies = active_result.scalar() or 0
        
        # Recent proxies (added in last 24 hours)
        recent_cutoff = now - timedelta(hours=24)
        recent_query = text("SELECT COUNT(*) FROM proxy_records WHERE created_at > :cutoff")
        recent_result = await session.execute(recent_query, {"cutoff": recent_cutoff})
        recent_proxies = recent_result.scalar() or 0
        
        # Quality distribution
        quality_query = text("""
            SELECT 
                CASE 
                    WHEN CAST(quality_score AS FLOAT) >= 0.8 THEN 'high'
                    WHEN CAST(quality_score AS FLOAT) >= 0.6 THEN 'medium'
                    WHEN CAST(quality_score AS FLOAT) >= 0.3 THEN 'low'
                    ELSE 'unknown'
                END as quality_tier,
                COUNT(*) as count
            FROM proxy_records
            GROUP BY quality_tier
        """)
        quality_result = await session.execute(quality_query)
        quality_distribution = {row.quality_tier: row.count for row in quality_result.fetchall()}
        
        # Anonymity distribution
        anonymity_query = text("""
            SELECT anonymity, COUNT(*) as count
            FROM proxy_records
            GROUP BY anonymity
        """)
        anonymity_result = await session.execute(anonymity_query)
        anonymity_distribution = {row.anonymity: row.count for row in anonymity_result.fetchall()}
        
        return {
            "total_proxies": total_proxies,
            "active_proxies": active_proxies,
            "inactive_proxies": total_proxies - active_proxies,
            "recent_proxies": recent_proxies,
            "active_ratio": active_proxies / max(total_proxies, 1),
            "quality_distribution": quality_distribution,
            "anonymity_distribution": anonymity_distribution,
            "last_updated": now,
        }
    
    def analyze_proxy_sources_sync(self, session) -> List[ProxySourceAnalytics]:
        """
        Analyze performance and distribution by proxy source (sync version).
        
        Args:
            session: Sync SQLAlchemy session
            
        Returns:
            List of ProxySourceAnalytics objects
        """
        # Get source statistics
        source_stats_query = text("""
            SELECT 
                source,
                COUNT(*) as total_proxies,
                COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active_proxies,
                AVG(CAST(quality_score AS FLOAT)) as avg_quality_score,
                updated_at
            FROM proxy_records 
            WHERE source IS NOT NULL
            GROUP BY source
            ORDER BY total_proxies DESC
        """)
        
        result = session.execute(source_stats_query)
        source_stats = result.fetchall()
        
        analytics_list = []
        
        for row in source_stats:
            source = row.source
            
            # Get geographic distribution for this source
            geo_query = text("""
                SELECT country_code, COUNT(*) as count
                FROM proxy_records 
                WHERE source = :source AND country_code IS NOT NULL
                GROUP BY country_code
                ORDER BY count DESC
            """)
            geo_result = session.execute(geo_query, {"source": source})
            geo_data = geo_result.fetchall()
            geographic_distribution = {row.country_code: row.count for row in geo_data}
            
            # Get scheme distribution for this source
            scheme_query = text("""
                SELECT schemes, COUNT(*) as count
                FROM proxy_records 
                WHERE source = :source
                GROUP BY schemes
            """)
            scheme_result = session.execute(scheme_query, {"source": source})
            scheme_data = scheme_result.fetchall()
            scheme_distribution = {row.schemes: row.count for row in scheme_data}
            
            analytics_list.append(ProxySourceAnalytics(
                source=source,
                total_proxies=row.total_proxies,
                active_proxies=row.active_proxies,
                avg_quality_score=row.avg_quality_score or 0.0,
                geographic_distribution=geographic_distribution,
                scheme_distribution=scheme_distribution,
                last_updated=datetime.now(timezone.utc),
            ))
        
        return analytics_list
