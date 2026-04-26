"""Public package API contract tests."""

from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 compatibility
    import tomli as tomllib


def test_top_level_all_symbols_are_importable() -> None:
    """Every advertised top-level export should resolve on the package object."""
    import proxywhirl

    assert "__version__" in proxywhirl.__all__
    missing = [name for name in proxywhirl.__all__ if not hasattr(proxywhirl, name)]

    assert missing == []


def test_top_level_version_matches_project_metadata() -> None:
    """The runtime package version should stay aligned with pyproject metadata."""
    import proxywhirl

    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text())

    assert proxywhirl.__version__ == pyproject["project"]["version"]
