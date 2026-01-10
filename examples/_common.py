"""
Shared helpers for ProxyWhirl examples.

These utilities keep the example scripts short, deterministic, and offline-friendly.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Iterable, List

from proxywhirl import Proxy, ProxyPool
from proxywhirl.models import HealthStatus

EXAMPLES_DIR = Path(__file__).resolve().parent
ASSETS_DIR = EXAMPLES_DIR / "assets"


def asset_path(name: str) -> Path:
    """Return an absolute path to a bundled asset file."""
    return ASSETS_DIR / name


def base_proxies() -> List[Proxy]:
    """Seed proxies with consistent metadata for examples."""
    proxies = [
        Proxy(
            url="http://alpha.proxy.local:8000",
            country_code="US",
            region="us-east-1",
            metadata={"tier": "gold"},
        ),
        Proxy(
            url="http://bravo.proxy.local:8000",
            country_code="DE",
            region="eu-central-1",
            metadata={"tier": "silver"},
        ),
        Proxy(
            url="http://charlie.proxy.local:8000",
            country_code="SG",
            region="ap-southeast-1",
            metadata={"tier": "silver"},
        ),
    ]
    for proxy in proxies:
        proxy.health_status = HealthStatus.HEALTHY
    return proxies


def demo_pool(name: str = "demo") -> ProxyPool:
    """Create a fresh ProxyPool seeded with demo proxies."""
    return ProxyPool(name=name, proxies=[p.model_copy(deep=True) for p in base_proxies()])


def seed_random(seed: int = 42) -> None:
    """Seed RNG for reproducible selections in examples."""
    random.seed(seed)


def print_header(title: str) -> None:
    """Pretty section header for console output."""
    line = "=" * 70
    print(f"\n{line}\n{title}\n{line}")
