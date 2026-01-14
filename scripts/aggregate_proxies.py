"""Script to fetch and aggregate proxies from all free sources.

This script fetches proxies from various free sources and:
1. Validates each proxy for connectivity before storage
2. Saves validated proxies to text/JSON files in docs/proxy-lists/
3. Persists validated proxies to SQLite database with health_status=healthy

Only working proxies are stored. Dead proxies are discarded.
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from loguru import logger

from proxywhirl.fetchers import ProxyValidator
from proxywhirl.models import HealthStatus, Proxy, ProxySource
from proxywhirl.sources import ALL_HTTP_SOURCES, ALL_SOCKS4_SOURCES, ALL_SOCKS5_SOURCES
from proxywhirl.storage import SQLiteStorage

# Validation settings - optimized for maximum throughput
VALIDATION_TIMEOUT = 2.0  # seconds per proxy (working proxies respond in <1s)
VALIDATION_CONCURRENCY = 1000  # parallel validations (very aggressive for faster processing)


async def fetch_proxy_list(source_config: Any) -> list[str]:
    """Fetch proxies from a single source."""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(str(source_config.url))
            response.raise_for_status()
            
            # Parse based on format
            if source_config.format == "plain_text":
                proxies = [
                    line.strip()
                    for line in response.text.split("\n")
                    if line.strip() and not line.startswith("#")
                ]
            elif source_config.format == "json":
                data = response.json()
                # Handle different JSON structures
                if isinstance(data, list):
                    proxies = [f"{p.get('ip')}:{p.get('port')}" for p in data if p.get('ip')]
                elif isinstance(data, dict) and 'data' in data:
                    proxies = [f"{p.get('ip')}:{p.get('port')}" for p in data['data'] if p.get('ip')]
                else:
                    proxies = []
            else:
                proxies = []
            
            logger.info(f"Fetched {len(proxies)} proxies from {source_config.url}")
            return proxies
    except Exception as e:
        logger.error(f"Failed to fetch from {source_config.url}: {e}")
        return []


async def aggregate_proxies() -> dict[str, set[str]]:
    """Fetch and aggregate all proxies by protocol (raw, unvalidated)."""
    aggregated = {
        "http": set(),
        "https": set(),
        "socks4": set(),
        "socks5": set(),
    }

    # Fetch HTTP/HTTPS proxies
    logger.info(f"Fetching from {len(ALL_HTTP_SOURCES)} HTTP sources...")
    http_tasks = [fetch_proxy_list(source) for source in ALL_HTTP_SOURCES]
    http_results = await asyncio.gather(*http_tasks)
    for proxies in http_results:
        aggregated["http"].update(proxies)
        aggregated["https"].update(proxies)  # HTTP sources work for both

    # Fetch SOCKS4 proxies
    logger.info(f"Fetching from {len(ALL_SOCKS4_SOURCES)} SOCKS4 sources...")
    socks4_tasks = [fetch_proxy_list(source) for source in ALL_SOCKS4_SOURCES]
    socks4_results = await asyncio.gather(*socks4_tasks)
    for proxies in socks4_results:
        aggregated["socks4"].update(proxies)

    # Fetch SOCKS5 proxies
    logger.info(f"Fetching from {len(ALL_SOCKS5_SOURCES)} SOCKS5 sources...")
    socks5_tasks = [fetch_proxy_list(source) for source in ALL_SOCKS5_SOURCES]
    socks5_results = await asyncio.gather(*socks5_tasks)
    for proxies in socks5_results:
        aggregated["socks5"].update(proxies)

    return aggregated


async def validate_proxies(
    proxies: dict[str, set[str]],
) -> dict[str, set[str]]:
    """Validate all proxies and return only working ones.

    Args:
        proxies: Dictionary mapping protocol to set of proxy addresses (ip:port)

    Returns:
        Dictionary with same structure but only containing validated proxies
    """
    validator = ProxyValidator(
        timeout=VALIDATION_TIMEOUT,
        concurrency=VALIDATION_CONCURRENCY,
    )

    validated: dict[str, set[str]] = {
        "http": set(),
        "https": set(),
        "socks4": set(),
        "socks5": set(),
    }

    # Build list of all proxies with their URLs for validation
    all_proxies: list[tuple[str, str, dict[str, Any]]] = []  # (protocol, addr, proxy_dict)

    for protocol, proxy_set in proxies.items():
        if protocol == "https":
            continue  # Skip HTTPS, it's same as HTTP

        scheme = "socks5" if protocol == "socks5" else (
            "socks4" if protocol == "socks4" else "http"
        )

        for addr in proxy_set:
            url = f"{scheme}://{addr}"
            all_proxies.append((protocol, addr, {"url": url}))

    total = len(all_proxies)
    logger.info(f"Validating {total} proxies with concurrency={VALIDATION_CONCURRENCY}...")

    start_time = time.time()
    valid_count = 0

    # Process in batches for progress reporting
    batch_size = 1000
    for i in range(0, total, batch_size):
        batch = all_proxies[i:i + batch_size]
        batch_dicts = [p[2] for p in batch]

        # Validate batch
        valid_batch = await validator.validate_batch(batch_dicts)
        valid_urls = {p["url"] for p in valid_batch}

        # Map back to protocol and address
        for protocol, addr, proxy_dict in batch:
            if proxy_dict["url"] in valid_urls:
                validated[protocol].add(addr)
                if protocol == "http":
                    validated["https"].add(addr)  # HTTP proxies work for HTTPS too
                valid_count += 1

        elapsed = time.time() - start_time
        rate = (i + len(batch)) / elapsed if elapsed > 0 else 0
        logger.info(
            f"Progress: {i + len(batch)}/{total} checked, "
            f"{valid_count} valid ({valid_count * 100 / (i + len(batch)):.1f}%), "
            f"{rate:.0f} proxies/sec"
        )

    elapsed = time.time() - start_time
    logger.info(
        f"Validation complete: {valid_count}/{total} valid "
        f"({valid_count * 100 / total:.1f}%) in {elapsed:.1f}s"
    )

    return validated


def save_proxy_lists(proxies: dict[str, set[str]], output_dir: Path) -> None:
    """Save proxy lists in various formats."""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    metadata = {
        "generated_at": timestamp,
        "total_sources": len(ALL_HTTP_SOURCES) + len(ALL_SOCKS4_SOURCES) + len(ALL_SOCKS5_SOURCES),
        "counts": {protocol: len(proxy_set) for protocol, proxy_set in proxies.items()},
    }
    
    # Save each protocol in TXT format
    for protocol, proxy_set in proxies.items():
        txt_file = output_dir / f"{protocol}.txt"
        with open(txt_file, "w") as f:
            for proxy in sorted(proxy_set):
                f.write(f"{proxy}\n")
        logger.info(f"Saved {len(proxy_set)} {protocol} proxies to {txt_file}")
    
    # Save all proxies in one file
    all_txt = output_dir / "all.txt"
    with open(all_txt, "w") as f:
        for protocol, proxy_set in proxies.items():
            f.write(f"# {protocol.upper()} Proxies ({len(proxy_set)})\n")
            for proxy in sorted(proxy_set):
                f.write(f"{proxy}\n")
            f.write("\n")
    logger.info(f"Saved all proxies to {all_txt}")
    
    # Save in JSON format
    json_file = output_dir / "proxies.json"
    json_data = {
        "metadata": metadata,
        "proxies": {protocol: sorted(list(proxy_set)) for protocol, proxy_set in proxies.items()},
    }
    with open(json_file, "w") as f:
        json.dump(json_data, f, indent=2)
    logger.info(f"Saved JSON to {json_file}")
    
    # Save metadata
    meta_file = output_dir / "metadata.json"
    with open(meta_file, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata to {meta_file}")


async def save_to_database(proxies: dict[str, set[str]], db_path: Path) -> int:
    """Save validated proxies to SQLite database.

    All proxies passed here have been validated and are marked as healthy.

    Args:
        proxies: Dictionary mapping protocol to set of proxy addresses (ip:port)
        db_path: Path to SQLite database file

    Returns:
        Total number of proxies saved
    """
    import aiosqlite

    # Ensure database uses DELETE journal mode (not WAL) for git compatibility
    # WAL mode creates -wal and -shm files which can cause merge conflicts
    async with aiosqlite.connect(str(db_path)) as db:
        await db.execute("PRAGMA journal_mode=DELETE")
        await db.commit()

    storage = SQLiteStorage(db_path)
    await storage.initialize()

    now = datetime.now(timezone.utc)
    proxy_objects: list[Proxy] = []

    for protocol_str, proxy_set in proxies.items():
        if protocol_str == "https":
            continue  # Skip https, same as http

        for proxy_addr in proxy_set:
            # Build full URL with protocol scheme
            scheme = "socks5" if protocol_str == "socks5" else (
                "socks4" if protocol_str == "socks4" else "http"
            )
            url = f"{scheme}://{proxy_addr}"

            # Create proxy with HEALTHY status since it passed validation
            proxy = Proxy(
                url=url,
                source=ProxySource.FETCHED,
                health_status=HealthStatus.HEALTHY,
                last_success_at=now,
                total_requests=1,
                total_successes=1,
                created_at=now,
                updated_at=now,
            )
            proxy_objects.append(proxy)

    # Save proxies in batches to avoid SQLite's "too many SQL variables" error
    batch_size = 500
    total_saved = 0
    for i in range(0, len(proxy_objects), batch_size):
        batch = proxy_objects[i:i + batch_size]
        await storage.save(batch)
        total_saved += len(batch)
        if (i + batch_size) % 5000 == 0:
            logger.info(f"Saved {total_saved}/{len(proxy_objects)} proxies...")

    await storage.close()

    logger.info(f"Saved {len(proxy_objects)} validated proxies to database: {db_path}")
    return len(proxy_objects)


async def main() -> None:
    """Main entry point."""
    logger.info("Starting proxy aggregation...")

    # Step 1: Fetch raw proxies from all sources
    raw_proxies = await aggregate_proxies()
    logger.info(
        f"Fetched raw proxies: {', '.join(f'{k}={len(v)}' for k, v in raw_proxies.items())}"
    )

    # Step 2: Validate all proxies (only keep working ones)
    validated_proxies = await validate_proxies(raw_proxies)
    logger.info(
        f"Validated proxies: {', '.join(f'{k}={len(v)}' for k, v in validated_proxies.items())}"
    )

    # Step 3: Save validated proxies to text/JSON files
    output_dir = Path("docs/proxy-lists")
    save_proxy_lists(validated_proxies, output_dir)

    # Step 4: Save validated proxies to SQLite database (with healthy status)
    db_path = Path("proxywhirl.db")
    await save_to_database(validated_proxies, db_path)

    logger.info("Proxy aggregation complete!")


if __name__ == "__main__":
    asyncio.run(main())
