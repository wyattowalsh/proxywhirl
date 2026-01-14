#!/usr/bin/env python3
"""Quick test script for Alembic migration functionality."""

import asyncio
import sys
import tempfile
from pathlib import Path

from proxywhirl.migrations import (
    check_pending_migrations,
    get_current_revision,
    get_head_revision,
    initialize_database,
)

__all__ = ["test_migrations"]


async def test_migrations():
    """Test basic migration functionality."""
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        db_path = Path(temp_file.name)
    db_url = f"sqlite+aiosqlite:///{db_path}"

    try:
        print("=" * 60)
        print("ProxyWhirl Alembic Migration Test")
        print("=" * 60)

        # Test 1: Get head revision
        print("\n[Test 1] Get head revision...")
        head = await get_head_revision(db_url)
        print(f"✓ Head revision: {head}")

        # Test 2: Check current revision (should be None for new DB)
        print("\n[Test 2] Check current revision (uninitialized)...")
        current = await get_current_revision(db_url)
        print(f"✓ Current revision: {current}")
        assert current is None, "Expected None for uninitialized database"

        # Test 3: Check pending migrations
        print("\n[Test 3] Check pending migrations...")
        has_pending = await check_pending_migrations(db_url)
        print(f"✓ Has pending migrations: {has_pending}")
        assert has_pending is True, "Expected pending migrations"

        # Test 4: Initialize database
        print("\n[Test 4] Initialize database...")
        await initialize_database(db_url)
        print("✓ Database initialized")

        # Test 5: Check current revision after init
        print("\n[Test 5] Check current revision (after init)...")
        current = await get_current_revision(db_url)
        print(f"✓ Current revision: {current}")
        assert current == head, f"Expected {head}, got {current}"

        # Test 6: Check pending migrations after init
        print("\n[Test 6] Check pending migrations (after init)...")
        has_pending = await check_pending_migrations(db_url)
        print(f"✓ Has pending migrations: {has_pending}")
        assert has_pending is False, "Expected no pending migrations"

        # Test 7: Verify tables created
        print("\n[Test 7] Verify database tables...")
        import sqlite3

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [t[0] for t in cursor.fetchall()]
        conn.close()
        print(f"✓ Tables created: {', '.join(tables)}")
        assert "proxies" in tables, "Expected 'proxies' table"
        assert "cache_entries" in tables, "Expected 'cache_entries' table"
        assert "alembic_version" in tables, "Expected 'alembic_version' table"

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        db_path.unlink(missing_ok=True)


if __name__ == "__main__":
    asyncio.run(test_migrations())
