"""Shared rotator wiring helpers (sync/async)."""

from __future__ import annotations

from proxywhirl.strategies import RotationStrategy, resolve_builtin_strategy


def resolve_strategy(strategy: RotationStrategy | str | None) -> RotationStrategy:
    """Resolve a strategy instance from either a strategy object or known string name."""
    if strategy is None:
        return resolve_builtin_strategy("round-robin")

    if not isinstance(strategy, str):
        return strategy

    return resolve_builtin_strategy(strategy)
