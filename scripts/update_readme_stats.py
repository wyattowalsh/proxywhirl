#!/usr/bin/env python3
"""
Auto-update README.md and SVG assets with real project statistics.

This script extracts actual metrics from the codebase and updates
all documentation to reflect accurate numbers.

Usage:
    uv run python scripts/update_readme_stats.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class ProjectStats(NamedTuple):
    """Container for project statistics."""

    test_count: int
    coverage_percent: float
    strategy_count: int
    source_total: int
    source_http: int
    source_socks4: int
    source_socks5: int
    source_recommended: int
    source_api: int


def get_test_count() -> int:
    """Get total test count from pytest collection."""
    try:
        result = subprocess.run(
            ["uv", "run", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Parse "1622 tests collected" or "1622 tests collected, 3 errors"
        match = re.search(r"(\d+)\s+tests?\s+collected", result.stdout + result.stderr)
        if match:
            return int(match.group(1))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return 0


def get_coverage_percent() -> float:
    """Get coverage percentage from HTML report or run coverage."""
    # Try reading from existing HTML report
    coverage_index = Path("logs/htmlcov/index.html")
    if coverage_index.exists():
        content = coverage_index.read_text()
        match = re.search(r'class="pc_cov">(\d+(?:\.\d+)?)%', content)
        if match:
            return float(match.group(1))

    # Try JSON report
    coverage_json = Path(".coverage.json")
    if coverage_json.exists():
        try:
            data = json.loads(coverage_json.read_text())
            return data.get("totals", {}).get("percent_covered", 0.0)
        except (json.JSONDecodeError, KeyError):
            pass

    # Fallback: run coverage
    try:
        result = subprocess.run(
            ["uv", "run", "coverage", "report", "--format=total"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass

    return 0.0


def get_source_counts() -> dict[str, int]:
    """Get source counts by importing the sources module."""
    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-c",
                """
import json
from proxywhirl.sources import (
    ALL_SOURCES, ALL_HTTP_SOURCES, ALL_SOCKS4_SOURCES,
    ALL_SOCKS5_SOURCES, RECOMMENDED_SOURCES, API_SOURCES
)
print(json.dumps({
    "total": len(ALL_SOURCES),
    "http": len(ALL_HTTP_SOURCES),
    "socks4": len(ALL_SOCKS4_SOURCES),
    "socks5": len(ALL_SOCKS5_SOURCES),
    "recommended": len(RECOMMENDED_SOURCES),
    "api": len(API_SOURCES),
}))
""",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass

    return {"total": 0, "http": 0, "socks4": 0, "socks5": 0, "recommended": 0, "api": 0}


def get_strategy_count() -> int:
    """Get count of concrete rotation strategies."""
    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-c",
                """
import proxywhirl.strategies as s
# Exclude base classes and non-strategy classes
excluded = {'RotationStrategy', 'StrategyConfig', 'StrategyRegistry', 'CompositeStrategy'}
strategies = [n for n in dir(s) if n.endswith('Strategy') and not n.startswith('_') and n not in excluded]
print(len(strategies))
""",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass

    return 0


def collect_stats() -> ProjectStats:
    """Collect all project statistics."""
    print("Collecting project statistics...")

    print("  - Counting tests...")
    test_count = get_test_count()

    print("  - Getting coverage...")
    coverage = get_coverage_percent()

    print("  - Counting strategies...")
    strategy_count = get_strategy_count()

    print("  - Counting sources...")
    sources = get_source_counts()

    stats = ProjectStats(
        test_count=test_count,
        coverage_percent=coverage,
        strategy_count=strategy_count,
        source_total=sources["total"],
        source_http=sources["http"],
        source_socks4=sources["socks4"],
        source_socks5=sources["socks5"],
        source_recommended=sources["recommended"],
        source_api=sources["api"],
    )

    print(f"\nCollected stats:")
    print(f"  Tests: {stats.test_count}")
    print(f"  Coverage: {stats.coverage_percent:.1f}%")
    print(f"  Strategies: {stats.strategy_count}")
    print(f"  Sources: {stats.source_total} total")
    print(f"    - HTTP: {stats.source_http}")
    print(f"    - SOCKS4: {stats.source_socks4}")
    print(f"    - SOCKS5: {stats.source_socks5}")
    print(f"    - Recommended: {stats.source_recommended}")
    print(f"    - API: {stats.source_api}")

    return stats


def update_readme(stats: ProjectStats, dry_run: bool = False) -> list[str]:
    """Update README.md with current stats."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        return []

    content = readme_path.read_text()
    original = content
    changes = []

    # Update test badge: tests-XXXX_passing
    pattern = r"tests-\d+_passing"
    replacement = f"tests-{stats.test_count}_passing"
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        changes.append(f"README: test count → {stats.test_count}")

    # Update coverage badge: coverage-XX%
    pattern = r"coverage-\d+%25"
    replacement = f"coverage-{int(stats.coverage_percent)}%25"
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        changes.append(f"README: coverage → {int(stats.coverage_percent)}%")

    # Update source count claims: **XX+ sources** or **XX sources**
    pattern = r"\*\*\d+\+?\s*sources\*\*"
    replacement = f"**{stats.source_total} sources**"
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        changes.append(f"README: source count → {stats.source_total}")

    # Update strategy count in headers: ## 🎯 X Strategies
    pattern = r"##\s*🎯\s*(Seven|Eight|Nine|Ten|\d+)\s*Strategies"
    num_word = {7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten"}.get(
        stats.strategy_count, str(stats.strategy_count)
    )
    replacement = f"## 🎯 {num_word} Strategies"
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        changes.append(f"README: strategy header → {num_word}")

    # Update comparison table: X strategies
    pattern = r"\|\s*Proxy Rotation\s*\|\s*\d+\s*strategies"
    replacement = f"| Proxy Rotation | {stats.strategy_count} strategies"
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)

    # Update source table counts
    source_table_updates = [
        (r"\|\s*`RECOMMENDED_SOURCES`[^|]+\|\s*\d+\s*\|", stats.source_recommended),
        (r"\|\s*`ALL_HTTP_SOURCES`[^|]+\|\s*\d+\s*\|", stats.source_http),
        (r"\|\s*`ALL_SOCKS4_SOURCES`[^|]+\|\s*\d+\s*\|", stats.source_socks4),
        (r"\|\s*`ALL_SOCKS5_SOURCES`[^|]+\|\s*\d+\s*\|", stats.source_socks5),
        (r"\|\s*`API_SOURCES`[^|]+\|\s*\d+\s*\|", stats.source_api),
    ]

    for pattern, count in source_table_updates:
        match = re.search(pattern, content)
        if match:
            old = match.group(0)
            new = re.sub(r"\|\s*\d+\s*\|$", f"| {count} |", old)
            content = content.replace(old, new)

    if source_table_updates:
        changes.append("README: source table counts updated")

    # Update project structure comments
    pattern = r"#\s*\d+\+?\s*proxy\s*sources"
    replacement = f"# {stats.source_total} proxy sources"
    content = re.sub(pattern, replacement, content)

    pattern = r"#\s*Unit\s*tests\s*\(\d+\+?\)"
    replacement = f"# Unit tests ({stats.test_count})"
    content = re.sub(pattern, replacement, content)

    if content != original:
        if not dry_run:
            readme_path.write_text(content)
        return changes

    return []


def update_svg_file(
    path: Path, replacements: list[tuple[str, str]], dry_run: bool = False
) -> list[str]:
    """Update an SVG file with regex replacements."""
    if not path.exists():
        return []

    content = path.read_text()
    original = content
    changes = []

    for pattern, replacement in replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes.append(f"{path.name}: pattern matched")

    if content != original:
        if not dry_run:
            path.write_text(content)
        return [f"{path.name}: updated"]

    return []


def update_svg_assets(stats: ProjectStats, dry_run: bool = False) -> list[str]:
    """Update all SVG assets with current stats."""
    changes = []
    assets_dir = Path("docs/assets")

    # stats-animated.svg - dashboard cards
    stats_svg = assets_dir / "stats-animated.svg"
    if stats_svg.exists():
        changes.extend(
            update_svg_file(
                stats_svg,
                [
                    # Strategy count in circle
                    (
                        r'fill="#06b6d4">(\d+)</text>',
                        f'fill="#06b6d4">{stats.strategy_count}</text>',
                    ),
                    # Source count in circle
                    (
                        r'fill="#8b5cf6">(\d+\+?)</text>',
                        f'fill="#8b5cf6">{stats.source_total}</text>',
                    ),
                    # Test count in circle
                    (
                        r'fill="#22c55e">(\d+)</text>',
                        f'fill="#22c55e">{stats.test_count}</text>',
                    ),
                    # Coverage in circle
                    (
                        r'fill="#ec4899">(\d+)%</text>',
                        f'fill="#ec4899">{int(stats.coverage_percent)}%</text>',
                    ),
                    # Coverage progress bar (26% of 135px = 35px)
                    (
                        r'to="(\d+)" dur="1\.5s" begin="0\.6s"',
                        f'to="{int(135 * stats.coverage_percent / 100)}" dur="1.5s" begin="0.6s"',
                    ),
                    # Coverage circle animation (26% of 113 circumference)
                    (
                        r'values="0 113;(\d+) (\d+)"[^/]*begin="0\.6s"',
                        f'values="0 113;{int(113 * stats.coverage_percent / 100)} {113 - int(113 * stats.coverage_percent / 100)}" dur="2s" fill="freeze" begin="0.6s"',
                    ),
                ],
                dry_run,
            )
        )

    # whirl.svg - main visualization
    whirl_svg = assets_dir / "whirl.svg"
    if whirl_svg.exists():
        changes.extend(
            update_svg_file(
                whirl_svg,
                [
                    (r">\d+\s*strategies<", f">{stats.strategy_count} strategies<"),
                    (r">\d+\+?\s*sources<", f">{stats.source_total} sources<"),
                ],
                dry_run,
            )
        )

    # social-preview.svg
    social_svg = assets_dir / "social-preview.svg"
    if social_svg.exists():
        changes.extend(
            update_svg_file(
                social_svg,
                [
                    (r">\d+\s*Strategies<", f">{stats.strategy_count} Strategies<"),
                    (r">\d+\+?\s*Sources<", f">{stats.source_total} Sources<"),
                ],
                dry_run,
            )
        )

    # features-grid.svg
    features_svg = assets_dir / "features-grid.svg"
    if features_svg.exists():
        changes.extend(
            update_svg_file(
                features_svg,
                [
                    (
                        r">\d+\s*strategies,\s*hot-swap<",
                        f">{stats.strategy_count} strategies, hot-swap<",
                    ),
                    (
                        r">\d+\+?\s*sources\s*built-in<",
                        f">{stats.source_total} sources built-in<",
                    ),
                ],
                dry_run,
            )
        )

    # architecture.svg
    arch_svg = assets_dir / "architecture.svg"
    if arch_svg.exists():
        changes.extend(
            update_svg_file(
                arch_svg,
                [
                    (r">\d+\+?\s*sources<", f">{stats.source_total} sources<"),
                ],
                dry_run,
            )
        )

    return changes


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Update README and SVG assets with real project statistics"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    args = parser.parse_args()

    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    import os

    os.chdir(project_root)

    print("=" * 60)
    print("README Stats Updater")
    print("=" * 60)

    if args.dry_run:
        print("DRY RUN - No files will be modified\n")

    # Collect stats
    stats = collect_stats()

    if stats.test_count == 0 and stats.source_total == 0:
        print("\nError: Could not collect any stats. Check your environment.")
        return 1

    # Update files
    print("\nUpdating files...")

    all_changes = []

    readme_changes = update_readme(stats, args.dry_run)
    all_changes.extend(readme_changes)

    svg_changes = update_svg_assets(stats, args.dry_run)
    all_changes.extend(svg_changes)

    if all_changes:
        print(f"\n{'Would update' if args.dry_run else 'Updated'}:")
        for change in all_changes:
            print(f"  ✓ {change}")
    else:
        print("\nNo changes needed - all stats are up to date!")

    print("\n" + "=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
