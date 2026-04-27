"""Tests for statistics badges module."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from proxywhirl.stats_badges import Badge, BadgeGenerator, StatsCollector


class TestBadge:
    """Test Badge class."""

    def test_to_markdown(self):
        """Test Markdown badge generation."""
        badge = Badge(label="Test", message="Value", color="blue")
        md = badge.to_markdown()
        assert "![" in md
        assert "Test" in md
        assert "Value" in md
        assert ".shields.io" in md

    def test_to_markdown_with_alt_text(self):
        """Test Markdown with custom alt text."""
        badge = Badge(label="Test", message="Value")
        md = badge.to_markdown(alt_text="Custom Alt")
        assert "Custom Alt" in md

    def test_to_html(self):
        """Test HTML badge generation."""
        badge = Badge(label="Test", message="Value", color="green")
        html = badge.to_html()
        assert "<img" in html
        assert ".shields.io" in html
        assert "Test" in html

    def test_to_html_with_link(self):
        """Test HTML badge with link."""
        badge = Badge(label="Test", message="Value")
        html = badge.to_html(link="https://example.com")
        assert "<a href=" in html
        assert "https://example.com" in html


class TestStatsCollector:
    """Test StatsCollector class."""

    def test_init(self):
        """Test initialization."""
        collector = StatsCollector(db_path="test.db")
        assert collector.db_path == "test.db"

    def test_init_default_path(self):
        """Test default database path."""
        collector = StatsCollector()
        assert collector.db_path == "proxywhirl.db"

    def test_get_proxy_count_no_db(self):
        """Test proxy count with missing database."""
        collector = StatsCollector(db_path="nonexistent.db")
        count = collector.get_proxy_count()
        assert count == 0

    def test_get_source_count_no_db(self):
        """Test source count with missing database."""
        collector = StatsCollector(db_path="nonexistent.db")
        count = collector.get_source_count()
        assert count == 0

    def test_get_healthy_proxy_percentage_no_db(self):
        """Test health percentage with missing database."""
        collector = StatsCollector(db_path="nonexistent.db")
        pct = collector.get_healthy_proxy_percentage()
        assert pct == 0.0

    def test_get_socks_coverage_no_db(self):
        """Test SOCKS coverage with missing database."""
        collector = StatsCollector(db_path="nonexistent.db")
        coverage = collector.get_socks_coverage()
        assert coverage["socks4"] == 0
        assert coverage["socks5"] == 0


class TestBadgeGenerator:
    """Test BadgeGenerator class."""

    def test_init(self):
        """Test initialization."""
        gen = BadgeGenerator()
        assert gen.stats is not None

    def test_generate_badges(self):
        """Test badge generation."""
        gen = BadgeGenerator(db_path="nonexistent.db")
        badges = gen.generate_badges()
        assert "proxies" in badges
        assert "sources" in badges
        assert "health" in badges
        assert "socks4" in badges
        assert "socks5" in badges

    def test_update_readme_no_file(self):
        """Test README update with missing file."""
        gen = BadgeGenerator()
        result = gen.update_readme(readme_path="nonexistent.md")
        assert not result

    def test_update_readme_insert_badges(self):
        """Test inserting badges into README."""
        with TemporaryDirectory() as tmpdir:
            readme_path = Path(tmpdir) / "README.md"
            readme_path.write_text("# My Project\n\nSome content\n")
            gen = BadgeGenerator()
            result = gen.update_readme(str(readme_path))
            assert result
            content = readme_path.read_text()
            assert "<!-- START STATS BADGES -->" in content
            assert "Proxies" in content

    def test_update_readme_replace_badges(self):
        """Test replacing existing badges."""
        with TemporaryDirectory() as tmpdir:
            readme_path = Path(tmpdir) / "README.md"
            content = (
                "# Title\n"
                "<!-- START STATS BADGES -->\n"
                "![Old](badge.svg)\n"
                "<!-- END STATS BADGES -->\n"
                "Text"
            )
            readme_path.write_text(content)
            gen = BadgeGenerator()
            result = gen.update_readme(str(readme_path))
            assert result
            new_content = readme_path.read_text()
            assert "Old" not in new_content

    def test_export_json(self):
        """Test JSON export."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "stats.json"
            gen = BadgeGenerator()
            result = gen.export_json(str(output_path))
            assert result
            data = json.loads(output_path.read_text())
            assert "proxy_count" in data
            assert "source_count" in data
            assert "healthy_percentage" in data
            assert "socks_coverage" in data

    def test_export_json_invalid_path(self):
        """Test JSON export with invalid path."""
        gen = BadgeGenerator()
        result = gen.export_json("/invalid/path/stats.json")
        assert not result
