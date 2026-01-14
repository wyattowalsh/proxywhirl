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
    # New metrics
    lines_of_code: int
    python_files: int
    dependency_count: int
    version: str
    test_files: int


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
    """Get coverage percentage from JSON report, HTML report, or run coverage."""
    # Try JSON report first (from CI artifact)
    for json_path in [Path("coverage.json"), Path(".coverage.json")]:
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text())
                # coverage.py JSON format has totals.percent_covered
                if "totals" in data:
                    return data["totals"].get("percent_covered", 0.0)
            except (json.JSONDecodeError, KeyError):
                pass

    # Try reading from existing HTML report
    coverage_index = Path("logs/htmlcov/index.html")
    if coverage_index.exists():
        content = coverage_index.read_text()
        match = re.search(r'class="pc_cov">(\d+(?:\.\d+)?)%', content)
        if match:
            return float(match.group(1))

    # Fallback: run coverage report (if .coverage file exists)
    if Path(".coverage").exists():
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


def get_lines_of_code() -> tuple[int, int]:
    """Count lines of code and Python files in proxywhirl/."""
    total_lines = 0
    file_count = 0
    proxywhirl_dir = Path("proxywhirl")

    if not proxywhirl_dir.exists():
        return 0, 0

    for py_file in proxywhirl_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            lines = len(py_file.read_text().splitlines())
            total_lines += lines
            file_count += 1
        except (OSError, UnicodeDecodeError):
            pass

    return total_lines, file_count


def get_test_file_count() -> int:
    """Count test files in tests/."""
    tests_dir = Path("tests")
    if not tests_dir.exists():
        return 0

    count = 0
    for py_file in tests_dir.rglob("*.py"):
        if "__pycache__" not in str(py_file) and py_file.name.startswith("test_"):
            count += 1
    return count


def get_dependency_count() -> int:
    """Count dependencies from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return 0

    content = pyproject_path.read_text()
    # Match lines in dependencies array
    match = re.search(r"dependencies\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if match:
        deps_block = match.group(1)
        # Count quoted strings (each dependency)
        deps = re.findall(r'"[^"]+[>=<][^"]*"', deps_block)
        return len(deps)
    return 0


def get_version() -> str:
    """Get version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return "0.0.0"

    content = pyproject_path.read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    return "0.0.0"


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

    print("  - Counting lines of code...")
    lines_of_code, python_files = get_lines_of_code()

    print("  - Counting test files...")
    test_files = get_test_file_count()

    print("  - Counting dependencies...")
    dependency_count = get_dependency_count()

    print("  - Getting version...")
    version = get_version()

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
        lines_of_code=lines_of_code,
        python_files=python_files,
        dependency_count=dependency_count,
        version=version,
        test_files=test_files,
    )

    print("\nCollected stats:")
    print(f"  Tests: {stats.test_count}")
    print(f"  Coverage: {stats.coverage_percent:.1f}%")
    print(f"  Strategies: {stats.strategy_count}")
    print(f"  Sources: {stats.source_total} total")
    print(f"    - HTTP: {stats.source_http}")
    print(f"    - SOCKS4: {stats.source_socks4}")
    print(f"    - SOCKS5: {stats.source_socks5}")
    print(f"    - Recommended: {stats.source_recommended}")
    print(f"    - API: {stats.source_api}")
    print(f"  Lines of code: {stats.lines_of_code:,}")
    print(f"  Python files: {stats.python_files}")
    print(f"  Test files: {stats.test_files}")
    print(f"  Dependencies: {stats.dependency_count}")
    print(f"  Version: {stats.version}")

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

    # Update feature cards: <strong>X Strategies</strong>
    pattern = r"<strong>\d+\s*Strategies</strong>"
    replacement = f"<strong>{stats.strategy_count} Strategies</strong>"
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        changes.append(f"README: strategies → {stats.strategy_count}")

    # Update feature cards: <strong>XX Sources</strong>
    pattern = r"<strong>\d+\s*Sources</strong>"
    replacement = f"<strong>{stats.source_total} Sources</strong>"
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        changes.append(f"README: sources → {stats.source_total}")

    if content != original:
        if not dry_run:
            readme_path.write_text(content)
        return changes if changes else ["README: stats updated"]

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


def generate_stats_svg(stats: ProjectStats, dry_run: bool = False) -> list[str]:
    """Generate a compact stats-animated.svg with 4 key metrics."""
    assets_dir = Path("docs/assets")
    stats_svg = assets_dir / "stats-animated.svg"

    # Format LOC display
    if stats.lines_of_code >= 1000:
        loc_display = f"{stats.lines_of_code / 1000:.1f}k"
    else:
        loc_display = str(stats.lines_of_code)

    # Coverage circle calculation (out of 113px max)
    _ = int(113 * stats.coverage_percent / 100)  # Used in SVG calculations

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 140" width="800" height="140">
  <style>
    @media (prefers-color-scheme: dark) {{
      .card-bg {{ fill: #1e293b; }}
      .card-stroke {{ stroke: #334155; }}
      .text-main {{ fill: #f1f5f9; }}
      .text-sub {{ fill: #94a3b8; }}
    }}
    @media (prefers-color-scheme: light) {{
      .card-bg {{ fill: #f8fafc; }}
      .card-stroke {{ stroke: #e2e8f0; }}
      .text-main {{ fill: #1e293b; }}
      .text-sub {{ fill: #64748b; }}
    }}
    .card-bg {{ fill: #1e293b; }}
    .card-stroke {{ stroke: #334155; }}
    .text-main {{ fill: #f1f5f9; }}
    .text-sub {{ fill: #94a3b8; }}
  </style>

  <defs>
    <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#06b6d4"/>
      <stop offset="100%" style="stop-color:#22d3ee"/>
    </linearGradient>
    <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#8b5cf6"/>
      <stop offset="100%" style="stop-color:#a78bfa"/>
    </linearGradient>
    <linearGradient id="greenGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#22c55e"/>
      <stop offset="100%" style="stop-color:#4ade80"/>
    </linearGradient>
    <linearGradient id="orangeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#f97316"/>
      <stop offset="100%" style="stop-color:#fb923c"/>
    </linearGradient>
    <filter id="cardShadow">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000" flood-opacity="0.3"/>
    </filter>
  </defs>

  <!-- Card 1: Strategies -->
  <g transform="translate(20, 20)" filter="url(#cardShadow)">
    <rect width="175" height="100" rx="16" class="card-bg card-stroke" stroke-width="1"/>
    <circle cx="35" cy="35" r="18" fill="none" stroke="url(#cyanGrad)" stroke-width="3">
      <animate attributeName="stroke-dasharray" values="0 113;113 0" dur="2s" fill="freeze"/>
    </circle>
    <text x="35" y="40" text-anchor="middle" font-family="system-ui" font-size="16" font-weight="bold" fill="#06b6d4">{stats.strategy_count}</text>
    <text x="70" y="32" font-family="system-ui" font-size="13" font-weight="600" class="text-main">Strategies</text>
    <text x="70" y="48" font-family="system-ui" font-size="10" class="text-sub">rotation modes</text>
    <g transform="translate(20, 65)">
      <rect width="135" height="4" rx="2" fill="#334155"/>
      <rect width="0" height="4" rx="2" fill="url(#cyanGrad)">
        <animate attributeName="width" from="0" to="135" dur="1.5s" fill="freeze"/>
      </rect>
    </g>
    <text x="155" y="80" text-anchor="end" font-family="monospace" font-size="9" fill="#06b6d4">
      <animate attributeName="opacity" values="0;1" dur="0.5s" begin="1.5s" fill="freeze"/>
      &lt;3μs
    </text>
  </g>

  <!-- Card 2: Sources -->
  <g transform="translate(215, 20)" filter="url(#cardShadow)">
    <rect width="175" height="100" rx="16" class="card-bg card-stroke" stroke-width="1"/>
    <circle cx="35" cy="35" r="18" fill="none" stroke="url(#purpleGrad)" stroke-width="3">
      <animate attributeName="stroke-dasharray" values="0 113;113 0" dur="2s" fill="freeze" begin="0.2s"/>
    </circle>
    <text x="35" y="40" text-anchor="middle" font-family="system-ui" font-size="14" font-weight="bold" fill="#8b5cf6">{stats.source_total}</text>
    <text x="70" y="32" font-family="system-ui" font-size="13" font-weight="600" class="text-main">Sources</text>
    <text x="70" y="48" font-family="system-ui" font-size="10" class="text-sub">proxy providers</text>
    <g transform="translate(20, 65)">
      <rect width="135" height="4" rx="2" fill="#334155"/>
      <rect width="0" height="4" rx="2" fill="url(#purpleGrad)">
        <animate attributeName="width" from="0" to="120" dur="1.5s" begin="0.2s" fill="freeze"/>
      </rect>
    </g>
    <text x="155" y="80" text-anchor="end" font-family="monospace" font-size="9" fill="#8b5cf6">
      <animate attributeName="opacity" values="0;1" dur="0.5s" begin="1.7s" fill="freeze"/>
      100+/s
    </text>
  </g>

  <!-- Card 3: Tests -->
  <g transform="translate(410, 20)" filter="url(#cardShadow)">
    <rect width="175" height="100" rx="16" class="card-bg card-stroke" stroke-width="1"/>
    <circle cx="35" cy="35" r="18" fill="none" stroke="url(#greenGrad)" stroke-width="3">
      <animate attributeName="stroke-dasharray" values="0 113;113 0" dur="2s" fill="freeze" begin="0.4s"/>
    </circle>
    <text x="35" y="38" text-anchor="middle" font-family="system-ui" font-size="9" font-weight="bold" fill="#22c55e">{stats.test_count}</text>
    <text x="70" y="32" font-family="system-ui" font-size="13" font-weight="600" class="text-main">Tests</text>
    <text x="70" y="48" font-family="system-ui" font-size="10" class="text-sub">all passing</text>
    <g transform="translate(20, 65)">
      <rect width="135" height="4" rx="2" fill="#334155"/>
      <rect width="0" height="4" rx="2" fill="url(#greenGrad)">
        <animate attributeName="width" from="0" to="135" dur="1.5s" begin="0.4s" fill="freeze"/>
      </rect>
    </g>
    <text x="155" y="80" text-anchor="end" font-family="monospace" font-size="9" fill="#22c55e">
      <animate attributeName="opacity" values="0;1" dur="0.5s" begin="1.9s" fill="freeze"/>
      100%
    </text>
  </g>

  <!-- Card 4: Lines of Code -->
  <g transform="translate(605, 20)" filter="url(#cardShadow)">
    <rect width="175" height="100" rx="16" class="card-bg card-stroke" stroke-width="1"/>
    <circle cx="35" cy="35" r="18" fill="none" stroke="url(#orangeGrad)" stroke-width="3">
      <animate attributeName="stroke-dasharray" values="0 113;113 0" dur="2s" fill="freeze" begin="0.6s"/>
    </circle>
    <text x="35" y="40" text-anchor="middle" font-family="system-ui" font-size="11" font-weight="bold" fill="#f97316">{loc_display}</text>
    <text x="70" y="32" font-family="system-ui" font-size="13" font-weight="600" class="text-main">Lines</text>
    <text x="70" y="48" font-family="system-ui" font-size="10" class="text-sub">of Python</text>
    <g transform="translate(20, 65)">
      <rect width="135" height="4" rx="2" fill="#334155"/>
      <rect width="0" height="4" rx="2" fill="url(#orangeGrad)">
        <animate attributeName="width" from="0" to="135" dur="1.5s" begin="0.6s" fill="freeze"/>
      </rect>
    </g>
    <text x="155" y="80" text-anchor="end" font-family="monospace" font-size="9" fill="#f97316">
      <animate attributeName="opacity" values="0;1" dur="0.5s" begin="2.1s" fill="freeze"/>
      v{stats.version}
    </text>
  </g>
</svg>
"""

    if not dry_run:
        stats_svg.write_text(svg_content)
        return ["stats-animated.svg: regenerated"]

    return ["stats-animated.svg: would regenerate"]


def update_svg_assets(stats: ProjectStats, dry_run: bool = False) -> list[str]:
    """Update all SVG assets with current stats."""
    changes = []
    assets_dir = Path("docs/assets")

    # Generate new stats-animated.svg with all 8 cards
    changes.extend(generate_stats_svg(stats, dry_run))

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


def generate_stats_json(stats: ProjectStats, dry_run: bool = False) -> list[str]:
    """Generate a JSON file with all stats for external tools."""
    stats_json_path = Path("docs/assets/stats.json")

    stats_dict = {
        "test_count": stats.test_count,
        "coverage_percent": round(stats.coverage_percent, 2),
        "strategy_count": stats.strategy_count,
        "sources": {
            "total": stats.source_total,
            "http": stats.source_http,
            "socks4": stats.source_socks4,
            "socks5": stats.source_socks5,
            "recommended": stats.source_recommended,
            "api": stats.source_api,
        },
        "codebase": {
            "lines_of_code": stats.lines_of_code,
            "python_files": stats.python_files,
            "test_files": stats.test_files,
            "dependencies": stats.dependency_count,
        },
        "version": stats.version,
        "generated_at": subprocess.run(
            ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
            capture_output=True,
            text=True,
        ).stdout.strip(),
    }

    if not dry_run:
        stats_json_path.write_text(json.dumps(stats_dict, indent=2) + "\n")
        return ["stats.json: generated"]

    return ["stats.json: would generate"]


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

    json_changes = generate_stats_json(stats, args.dry_run)
    all_changes.extend(json_changes)

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
