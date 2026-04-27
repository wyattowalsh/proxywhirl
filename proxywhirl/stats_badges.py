"""Dynamic statistics badges generator for README.

Generates shield.io badges with real-time statistics from database.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from loguru import logger


@dataclass
class Badge:
    """Represents a shield.io badge."""

    label: str
    message: str
    color: str = "blue"
    style: str = "flat-square"

    def to_markdown(self, alt_text: str = "") -> str:
        """Convert badge to Markdown format.

        Args:
            alt_text: Alt text for badge image

        Returns:
            Markdown badge string
        """
        url = f"https://img.shields.io/badge/{self.label}-{self.message}-{self.color}?style={self.style}"
        alt = alt_text or f"{self.label}: {self.message}"
        return f"![{alt}]({url})"

    def to_html(self, link: str = "") -> str:
        """Convert badge to HTML format.

        Args:
            link: Optional URL to link badge to

        Returns:
            HTML badge string
        """
        url = f"https://img.shields.io/badge/{self.label}-{self.message}-{self.color}?style={self.style}"
        img = f'<img src="{url}" alt="{self.label}: {self.message}">'
        if link:
            return f'<a href="{link}">{img}</a>'
        return img


class StatsCollector:
    """Collects statistics from various sources."""

    def __init__(self, db_path: str | None = None) -> None:
        """Initialize stats collector.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path or "proxywhirl.db"

    def get_proxy_count(self) -> int:
        """Get total proxy count from database.

        Returns:
            Number of proxies in database
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM proxy WHERE deleted_at IS NULL")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else 0
        except Exception as e:
            logger.warning(f"Failed to get proxy count: {e}")
            return 0

    def get_source_count(self) -> int:
        """Get unique source count.

        Returns:
            Number of unique proxy sources
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(DISTINCT source) FROM proxy WHERE deleted_at IS NULL"
            )
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else 0
        except Exception as e:
            logger.warning(f"Failed to get source count: {e}")
            return 0

    def get_healthy_proxy_percentage(self) -> float:
        """Get percentage of healthy proxies.

        Returns:
            Percentage of healthy proxies (0-100)
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM proxy WHERE status = 'healthy' AND deleted_at IS NULL"
            )
            healthy = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM proxy WHERE deleted_at IS NULL")
            total = cursor.fetchone()[0]
            conn.close()
            return (healthy / total * 100) if total > 0 else 0.0
        except Exception as e:
            logger.warning(f"Failed to get healthy proxy percentage: {e}")
            return 0.0

    def get_socks_coverage(self) -> dict[str, int]:
        """Get SOCKS proxy coverage.

        Returns:
            Dict with socks4 and socks5 counts
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT protocol, COUNT(*) FROM proxy WHERE deleted_at IS NULL GROUP BY protocol"
            )
            results = cursor.fetchall()
            conn.close()
            coverage = {"socks4": 0, "socks5": 0}
            for protocol, count in results:
                if protocol in coverage:
                    coverage[protocol] = count
            return coverage
        except Exception as e:
            logger.warning(f"Failed to get SOCKS coverage: {e}")
            return {"socks4": 0, "socks5": 0}


class BadgeGenerator:
    """Generates statistics badges for README."""

    def __init__(self, db_path: str | None = None) -> None:
        """Initialize badge generator.

        Args:
            db_path: Path to SQLite database
        """
        self.stats = StatsCollector(db_path)

    def generate_badges(self) -> dict[str, str]:
        """Generate all statistics badges.

        Returns:
            Dictionary of badge name to Markdown
        """
        proxy_count = self.stats.get_proxy_count()
        source_count = self.stats.get_source_count()
        healthy_pct = self.stats.get_healthy_proxy_percentage()
        socks = self.stats.get_socks_coverage()

        badges = {
            "proxies": Badge(
                label="Proxies",
                message=f"{proxy_count:,}",
                color="blueviolet",
            ).to_markdown(),
            "sources": Badge(
                label="Sources",
                message=str(source_count),
                color="green",
            ).to_markdown(),
            "health": Badge(
                label="Health",
                message=f"{healthy_pct:.1f}%",
                color="brightgreen" if healthy_pct > 80 else "orange",
            ).to_markdown(),
            "socks4": Badge(
                label="SOCKS4",
                message=str(socks["socks4"]),
                color="blue",
            ).to_markdown(),
            "socks5": Badge(
                label="SOCKS5",
                message=str(socks["socks5"]),
                color="blue",
            ).to_markdown(),
        }
        return badges

    def update_readme(self, readme_path: str = "README.md") -> bool:
        """Update README with generated badges.

        Args:
            readme_path: Path to README file

        Returns:
            True if update successful
        """
        try:
            badges = self.generate_badges()
            readme = Path(readme_path).read_text()

            # Create badge section
            badge_lines = [
                "<!-- START STATS BADGES -->",
                "",
            ]
            for badge_md in badges.values():
                badge_lines.append(badge_md)
            badge_lines.extend(["", "<!-- END STATS BADGES -->"])
            badge_section = "\n".join(badge_lines)

            # Replace or insert badge section
            if "<!-- START STATS BADGES -->" in readme:
                start_idx = readme.find("<!-- START STATS BADGES -->")
                end_idx = readme.find("<!-- END STATS BADGES -->") + len(
                    "<!-- END STATS BADGES -->"
                )
                readme = readme[:start_idx] + badge_section + readme[end_idx:]
            else:
                # Insert after first h1
                h1_idx = readme.find("#")
                next_newline = readme.find("\n", h1_idx) + 1
                readme = (
                    readme[:next_newline]
                    + "\n"
                    + badge_section
                    + "\n"
                    + readme[next_newline:]
                )

            Path(readme_path).write_text(readme)
            logger.info(f"Updated {readme_path} with statistics badges")
            return True
        except Exception as e:
            logger.error(f"Failed to update README: {e}")
            return False

    def export_json(self, output_path: str = "stats.json") -> bool:
        """Export statistics as JSON.

        Args:
            output_path: Path to output JSON file

        Returns:
            True if export successful
        """
        try:
            stats = {
                "proxy_count": self.stats.get_proxy_count(),
                "source_count": self.stats.get_source_count(),
                "healthy_percentage": round(
                    self.stats.get_healthy_proxy_percentage(), 2
                ),
                "socks_coverage": self.stats.get_socks_coverage(),
            }
            Path(output_path).write_text(json.dumps(stats, indent=2))
            logger.info(f"Exported statistics to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export statistics: {e}")
            return False
