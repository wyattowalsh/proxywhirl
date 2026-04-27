"""Proxy reputation scoring from community sources.

Integrates proxy reputation scoring from community data feeds,
tracking proxy reputation and blacklist status.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from loguru import logger


class ReputationScore:
    """Represents a proxy's reputation score."""

    def __init__(self, proxy_url: str, initial_score: float = 50.0) -> None:
        """Initialize reputation score.

        Args:
            proxy_url: Proxy URL
            initial_score: Initial score (0-100)
        """
        self.proxy_url = proxy_url
        self.score = max(0, min(100, initial_score))
        self.last_updated = datetime.now()
        self.reports: list[dict[str, Any]] = []
        self.blacklist_entries: list[dict[str, Any]] = []

    def report_abuse(self, description: str) -> None:
        """Report proxy for abuse.

        Args:
            description: Description of abuse
        """
        self.reports.append(
            {
                "timestamp": datetime.now().isoformat(),
                "description": description,
            }
        )
        self._adjust_score(-5)  # Reduce score for each report
        logger.debug(f"Reported abuse for {self.proxy_url}: {description}")

    def report_spam(self) -> None:
        """Report proxy for spam."""
        self._adjust_score(-3)
        self.reports.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "spam",
            }
        )

    def report_phishing(self) -> None:
        """Report proxy for phishing."""
        self._adjust_score(-10)
        self.reports.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "phishing",
            }
        )

    def verify_good(self) -> None:
        """Verify proxy as good/clean."""
        self._adjust_score(3)
        logger.debug(f"Verified proxy as good: {self.proxy_url}")

    def add_blacklist_entry(self, source: str, reason: str) -> None:
        """Add blacklist entry for proxy.

        Args:
            source: Source of blacklist (e.g., 'abuseipdb')
            reason: Reason for blacklist
        """
        self.blacklist_entries.append(
            {
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "reason": reason,
            }
        )
        self._adjust_score(-15)
        logger.warning(f"Blacklisted {self.proxy_url} from {source}: {reason}")

    def _adjust_score(self, delta: float) -> None:
        """Adjust reputation score."""
        self.score = max(0, min(100, self.score + delta))
        self.last_updated = datetime.now()

    def is_blacklisted(self) -> bool:
        """Check if proxy is blacklisted."""
        return len(self.blacklist_entries) > 0

    def is_trusted(self) -> bool:
        """Check if proxy is trusted (high reputation)."""
        return self.score >= 75 and not self.is_blacklisted()

    def is_suspicious(self) -> bool:
        """Check if proxy is suspicious (low reputation)."""
        return self.score < 40


class ReputationManager:
    """Manages proxy reputation scores."""

    def __init__(self) -> None:
        """Initialize reputation manager."""
        self.scores: dict[str, ReputationScore] = {}
        self.community_feeds: list[str] = []

    def get_or_create_score(self, proxy_url: str) -> ReputationScore:
        """Get or create reputation score for proxy.

        Args:
            proxy_url: Proxy URL

        Returns:
            ReputationScore object
        """
        if proxy_url not in self.scores:
            self.scores[proxy_url] = ReputationScore(proxy_url)
        return self.scores[proxy_url]

    def get_score(self, proxy_url: str) -> float:
        """Get reputation score for proxy.

        Args:
            proxy_url: Proxy URL

        Returns:
            Score 0-100 or None if not found
        """
        score_obj = self.scores.get(proxy_url)
        return score_obj.score if score_obj else 50.0

    def report_proxy(self, proxy_url: str, report_type: str, description: str = "") -> None:
        """Report a proxy.

        Args:
            proxy_url: Proxy URL
            report_type: Type of report (abuse, spam, phishing)
            description: Report description
        """
        score = self.get_or_create_score(proxy_url)

        if report_type == "abuse":
            score.report_abuse(description)
        elif report_type == "spam":
            score.report_spam()
        elif report_type == "phishing":
            score.report_phishing()

    def verify_good_proxy(self, proxy_url: str) -> None:
        """Verify proxy as good.

        Args:
            proxy_url: Proxy URL
        """
        self.get_or_create_score(proxy_url).verify_good()

    def blacklist_proxy(self, proxy_url: str, source: str, reason: str) -> None:
        """Blacklist a proxy.

        Args:
            proxy_url: Proxy URL
            source: Source of blacklist
            reason: Reason for blacklist
        """
        self.get_or_create_score(proxy_url).add_blacklist_entry(source, reason)

    def is_blacklisted(self, proxy_url: str) -> bool:
        """Check if proxy is blacklisted.

        Args:
            proxy_url: Proxy URL

        Returns:
            True if blacklisted
        """
        score = self.scores.get(proxy_url)
        return score.is_blacklisted() if score else False

    def filter_by_reputation(self, proxy_urls: list[str], min_score: float = 40.0) -> list[str]:
        """Filter proxies by reputation score.

        Args:
            proxy_urls: List of proxy URLs
            min_score: Minimum acceptable score

        Returns:
            Filtered list of proxy URLs
        """
        return [url for url in proxy_urls if self.get_score(url) >= min_score]

    def get_reputation_stats(self) -> dict[str, Any]:
        """Get reputation statistics.

        Returns:
            Dict with statistics
        """
        if not self.scores:
            return {"total": 0}

        scores = list(self.scores.values())
        avg_score = sum(s.score for s in scores) / len(scores)

        return {
            "total": len(scores),
            "avg_score": avg_score,
            "trusted": sum(1 for s in scores if s.is_trusted()),
            "suspicious": sum(1 for s in scores if s.is_suspicious()),
            "blacklisted": sum(1 for s in scores if s.is_blacklisted()),
        }

    def cleanup_old_entries(self, days: int = 90) -> int:
        """Clean up old reputation data.

        Args:
            days: Age threshold in days

        Returns:
            Number of entries cleaned
        """
        cutoff = datetime.now() - timedelta(days=days)
        cleaned = 0

        for score in self.scores.values():
            # Clean old reports
            old_count = len(score.reports)
            score.reports = [
                r for r in score.reports if datetime.fromisoformat(r["timestamp"]) > cutoff
            ]
            cleaned += old_count - len(score.reports)

            # Clean old blacklist entries
            old_count = len(score.blacklist_entries)
            score.blacklist_entries = [
                e
                for e in score.blacklist_entries
                if datetime.fromisoformat(e["timestamp"]) > cutoff
            ]
            cleaned += old_count - len(score.blacklist_entries)

        logger.info(f"Cleaned {cleaned} old reputation entries")
        return cleaned


_manager: ReputationManager | None = None


def get_reputation_manager() -> ReputationManager:
    """Get global reputation manager instance."""
    global _manager
    if _manager is None:
        _manager = ReputationManager()
    return _manager
