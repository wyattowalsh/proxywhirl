"""Tests for SQLite storage backend (T056-T075)."""

import tempfile
from pathlib import Path

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from proxywhirl.models import HealthStatus, Proxy, ProxySource


class TestSQLiteStorage:
    """Tests for SQLiteStorage backend."""

    async def test_sqlite_create_tables(self) -> None:
        """T058: Test that tables are created on initialization."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)

            # Initialize should create tables
            await storage.initialize()

            # Database file should exist
            assert db_path.exists()

            # Clean up
            await storage.close()

    async def test_sqlite_save_single_proxy(self) -> None:
        """T061: Test saving a single proxy."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxy = Proxy(url="http://proxy1.example.com:8080")
            await storage.save([proxy])

            # Load and verify
            loaded = await storage.load()
            assert len(loaded) == 1
            assert loaded[0]["url"] == proxy.url

            await storage.close()

    async def test_stats_cache_invalidates_after_mutations(self) -> None:
        """Cached aggregate stats should refresh after writes."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            empty_stats = await storage.get_stats_cached()
            assert empty_stats["total_proxies"] == 0

            proxy = Proxy(url="http://proxy-cache.example.com:8080")
            await storage.save([proxy])
            after_save = await storage.get_stats_cached()
            assert after_save["total_proxies"] == 1

            await storage.record_validation(proxy.url, True, 100.0)
            after_validation = await storage.get_stats_cached()
            assert after_validation["validations_24h"]["total"] == 1

            await storage.clear()
            after_clear = await storage.get_stats_cached()
            assert after_clear["total_proxies"] == 0

            await storage.close()

    async def test_sqlite_save_multiple_proxies(self) -> None:
        """T062: Test saving multiple proxies."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxies = [
                Proxy(url="http://proxy1.example.com:8080"),
                Proxy(url="http://proxy2.example.com:8080"),
                Proxy(url="http://proxy3.example.com:8080"),
            ]
            await storage.save(proxies)

            loaded = await storage.load()
            assert len(loaded) == 3

            await storage.close()

    async def test_sqlite_load_all_proxies(self) -> None:
        """T063: Test loading all proxies."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Save proxies
            proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(10)]
            await storage.save(proxies)

            # Load all
            loaded = await storage.load()
            assert len(loaded) == 10
            assert set(loaded[0]) == {
                "url",
                "protocol",
                "host",
                "port",
                "username",
                "password",
                "country_code",
                "source",
                "source_url",
                "discovered_at",
                "expires_at",
                "health_status",
                "last_check_at",
                "last_success_at",
                "last_failure_at",
                "avg_response_time_ms",
                "total_checks",
                "total_successes",
            }

            await storage.close()

    async def test_sqlite_query_by_source(self) -> None:
        """T064: Test querying proxies by source."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxies = [
                Proxy(url="http://proxy1.example.com:8080", source=ProxySource.USER),
                Proxy(url="http://proxy2.example.com:8080", source=ProxySource.API),
                Proxy(url="http://proxy3.example.com:8080", source=ProxySource.USER),
            ]
            await storage.save(proxies)

            # Query by source
            user_proxies = await storage.query(source="user")
            assert len(user_proxies) == 2
            assert all(p["source"] == "user" for p in user_proxies)

            await storage.close()

    async def test_sqlite_foreign_keys_enforced_for_sessions(self) -> None:
        """SQLite sessions must enforce FK constraints beyond initialization."""
        from proxywhirl.storage import ProxyStatusTable, SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            async with AsyncSession(storage.engine) as session:
                session.add(ProxyStatusTable(proxy_url="http://missing.example.com:8080"))
                with pytest.raises(IntegrityError):
                    await session.commit()

            await storage.close()

    async def test_sqlite_single_and_batch_metadata_parity(self) -> None:
        """Single and batch insert paths should persist the same identity metadata."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            single_proxy = Proxy(
                url="http://single.example.com:8080",
                source=ProxySource.API,
                source_url="https://sources.example.com/single.txt",
                country_code="US",
            )
            batch_proxy = Proxy(
                url="http://batch.example.com:8080",
                source=ProxySource.API,
                source_url="https://sources.example.com/batch.txt",
                country_code="US",
            )

            assert await storage.add_proxy(single_proxy) is True
            added, skipped = await storage.add_proxies_batch([batch_proxy])

            assert (added, skipped) == (1, 0)

            loaded = {row["url"]: row for row in await storage.load()}
            assert loaded[single_proxy.url]["source"] == ProxySource.API.value
            assert loaded[batch_proxy.url]["source"] == ProxySource.API.value
            assert loaded[single_proxy.url]["source_url"] == str(single_proxy.source_url)
            assert loaded[batch_proxy.url]["source_url"] == str(batch_proxy.source_url)
            assert loaded[single_proxy.url]["country_code"] == "US"
            assert loaded[batch_proxy.url]["country_code"] == "US"

            batch_loaded = await storage.get_proxies_batch([single_proxy.url, batch_proxy.url])
            status_loaded = {
                row["url"]: row for row in await storage.get_proxies_by_status("unknown")
            }
            revalidation_loaded = {
                row["url"]: row for row in await storage.load_revalidation_candidates()
            }

            for rows in (batch_loaded, status_loaded, revalidation_loaded):
                for proxy in (single_proxy, batch_proxy):
                    assert rows[proxy.url]["source_url"] == str(proxy.source_url)
                    assert rows[proxy.url]["country_code"] == "US"

            await storage.close()

    async def test_sqlite_query_by_health_status(self) -> None:
        """T065: Test querying proxies by health status.

        With normalized schema, proxies start as 'unknown' and become 'healthy'
        after successful validation via record_validation().
        """
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxies = [
                Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY),
                Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.UNHEALTHY),
                Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.HEALTHY),
            ]
            await storage.save(proxies)

            # With normalized schema, need to record validations to set status
            await storage.record_validation(
                "http://proxy1.example.com:8080", is_valid=True, response_time_ms=100.0
            )
            await storage.record_validation(
                "http://proxy2.example.com:8080", is_valid=False, error_type="timeout"
            )
            await storage.record_validation(
                "http://proxy3.example.com:8080", is_valid=True, response_time_ms=150.0
            )

            # Query by health status
            healthy = await storage.query(health_status="healthy")
            assert len(healthy) == 2
            assert all(p["health_status"] == "healthy" for p in healthy)

            await storage.close()

    async def test_sqlite_delete_proxy(self) -> None:
        """T066: Test deleting a proxy by URL."""
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxies = [
                Proxy(url="http://proxy1.example.com:8080"),
                Proxy(url="http://proxy2.example.com:8080"),
            ]
            await storage.save(proxies)

            # Delete one proxy
            await storage.delete("http://proxy1.example.com:8080")

            loaded = await storage.load()
            assert len(loaded) == 1
            assert loaded[0]["url"] == "http://proxy2.example.com:8080"

            await storage.close()

    async def test_sqlite_update_existing_proxy(self) -> None:
        """Test updating an existing proxy (upsert).

        With normalized schema, save() only adds identity. Re-saving is a no-op.
        Status updates happen via record_validation().
        """
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Save initial proxy
            proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.UNKNOWN)
            await storage.save([proxy1])

            # Update same proxy - with normalized schema this is a no-op for identity
            proxy2 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
            await storage.save([proxy2])

            # Should have only 1 proxy (status stays unknown since save() doesn't update status)
            loaded = await storage.load()
            assert len(loaded) == 1
            assert loaded[0]["health_status"] == HealthStatus.UNKNOWN.value

            await storage.close()

    async def test_sqlite_concurrent_access(self) -> None:
        """T072: Test concurrent read/write operations."""
        import asyncio

        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            # Concurrent writes
            async def save_proxy(i: int) -> None:
                proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
                await storage.save([proxy])

            await asyncio.gather(*[save_proxy(i) for i in range(5)])

            # Verify all saved
            loaded = await storage.load()
            assert len(loaded) == 5

            await storage.close()


class TestSQLiteStorageWave2:
    """Wave 2 storage/Alembic behavior (TM-STORE)."""

    async def test_delete_returns_false_when_missing(self) -> None:
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            assert await storage.delete("http://missing.example.com:8080") is False

            await storage.close()

    async def test_expires_at_persisted_on_save(self) -> None:
        from datetime import datetime, timedelta, timezone

        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
            proxy = Proxy(
                url="http://ttl.example.com:8080",
                expires_at=expires_at,
                allow_local=True,
            )
            await storage.save([proxy])
            restored = (await storage.load_models())[0]
            assert restored.expires_at is not None
            assert abs((restored.expires_at - expires_at).total_seconds()) < 2

            await storage.close()

    async def test_update_identity_upserts_metadata(self) -> None:
        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            url = "http://identity.example.com:8080"
            await storage.add_proxy(
                Proxy(url=url, country_code="US", allow_local=True),
            )
            updated = Proxy(url=url, country_code="CA", region="ON", allow_local=True)
            assert await storage.update_identity(updated) is True

            rows = await storage.load()
            assert rows[0]["country_code"] == "CA"

            await storage.close()

    async def test_cross_process_credential_roundtrip_fixed_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from cryptography.fernet import Fernet
        from pydantic import SecretStr

        from proxywhirl.storage import SQLiteStorage

        key = Fernet.generate_key()
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", key.decode())

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            writer = SQLiteStorage(db_path)
            await writer.initialize()
            proxy = Proxy(
                url="http://secure.example.com:8080",
                username=SecretStr("writer-user"),
                password=SecretStr("writer-pass"),
                allow_local=True,
            )
            await writer.add_proxy(proxy)
            await writer.close()

            reader = SQLiteStorage(db_path)
            await reader.initialize()
            rows = await reader.load()
            await reader.close()

            assert rows[0]["username"] == "writer-user"
            assert rows[0]["password"] == "writer-pass"

    async def test_busy_timeout_pragma_on_connection(self) -> None:
        from sqlalchemy import text

        from proxywhirl.storage import SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            async with storage.engine.connect() as conn:
                result = await conn.execute(text("PRAGMA busy_timeout"))
                timeout_ms = result.scalar()

            assert timeout_ms == 5000
            await storage.close()

    async def test_success_rate_7d_updated_after_validation(self) -> None:
        from sqlmodel.ext.asyncio.session import AsyncSession

        from proxywhirl.storage import ProxyStatusTable, SQLiteStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            url = "http://rate.example.com:8080"
            await storage.add_proxy(Proxy(url=url, allow_local=True))
            await storage.record_validation(url, True, 50.0)
            await storage.record_validation(url, False, None, error_type="timeout")

            async with AsyncSession(storage.engine) as session:
                status = await session.get(ProxyStatusTable, url)
                assert status is not None
                assert status.success_rate_7d == pytest.approx(0.5)

            await storage.close()

    async def test_initialize_alembic_only_no_runtime_alter_helpers(self) -> None:
        """SQLiteStorage.initialize must not own schema ALTER helpers."""
        from proxywhirl.storage import SQLiteStorage

        assert not hasattr(SQLiteStorage, "_migrate_normalized_schema")
        assert not hasattr(SQLiteStorage, "_ensure_supplemental_indexes")

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            from sqlalchemy import text

            async with storage.engine.connect() as conn:
                rev = (await conn.execute(text("SELECT version_num FROM alembic_version"))).scalar()
                cols = {
                    row[1]
                    for row in (await conn.execute(text("PRAGMA table_info(proxy_identities)")))
                }
            assert rev == "d4e5f6a7b8c9"
            assert "expires_at" in cols
            await storage.close()

    async def test_rejects_plaintext_credential_writes_without_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Credential writes must fail closed when encryption is unavailable."""
        from pydantic import SecretStr

        from proxywhirl.exceptions import ProxyStorageError
        from proxywhirl.storage import SQLiteStorage

        monkeypatch.delenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", raising=False)
        monkeypatch.delenv("PROXYWHIRL_ENCRYPTION_KEY", raising=False)
        monkeypatch.delenv("PROXYWHIRL_KEY", raising=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            proxy = Proxy(
                url="http://plain.example.com:8080",
                username=SecretStr("user"),
                password=SecretStr("pass"),
                allow_local=True,
            )
            with pytest.raises(ProxyStorageError, match="ENCRYPTION_KEY|Fernet key"):
                await storage.add_proxy(proxy)
            with pytest.raises(ProxyStorageError, match="ENCRYPTION_KEY|Fernet key"):
                await storage.save([proxy])

            # Proxies without credentials still work
            await storage.add_proxy(Proxy(url="http://open.example.com:8080", allow_local=True))
            rows = await storage.load()
            assert len(rows) == 1
            assert rows[0]["url"] == "http://open.example.com:8080"

            await storage.close()

    async def test_url_embedded_credentials_stripped_and_roundtrip(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """f01: persisted URLs never contain userinfo; load reconstructs credentials."""
        from cryptography.fernet import Fernet
        from sqlalchemy import text

        from proxywhirl.storage import SQLiteStorage

        key = Fernet.generate_key()
        monkeypatch.setenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", key.decode())
        credentialed = "http://user:secret@proxy.example.com:8080"
        identity = "http://proxy.example.com:8080"

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()
            await storage.save([Proxy(url=credentialed)])

            async with storage.engine.connect() as conn:
                identity_url = (
                    await conn.execute(text("SELECT url FROM proxy_identities"))
                ).scalar_one()
                status_url = (
                    await conn.execute(text("SELECT proxy_url FROM proxy_statuses"))
                ).scalar_one()
                legacy_url = (await conn.execute(text("SELECT url FROM proxies"))).scalar_one()
                username, password = (
                    await conn.execute(text("SELECT username, password FROM proxy_identities"))
                ).one()

            assert identity_url == identity
            assert status_url == identity
            assert legacy_url == identity
            assert "user:secret" not in identity_url
            assert username != "user"
            assert password != "secret"
            assert username is not None and password is not None

            loaded = await storage.load_models()
            assert len(loaded) == 1
            assert loaded[0].username is not None
            assert loaded[0].password is not None
            assert loaded[0].username.get_secret_value() == "user"
            assert loaded[0].password.get_secret_value() == "secret"
            assert "user:secret@" in loaded[0].url

            await storage.audit_log_change(credentialed, "INSERT", new_values={"url": credentialed})
            async with storage.engine.connect() as conn:
                audit_url = (
                    await conn.execute(text("SELECT proxy_url FROM proxies_audit"))
                ).scalar_one()
            assert audit_url == identity

            await storage.close()

    async def test_audit_json_redacts_credentialed_values(self) -> None:
        """Audit JSON old/new values must not persist userinfo or plaintext credentials."""
        import json

        from sqlalchemy import text

        from proxywhirl.storage import SQLiteStorage

        credentialed = "http://user:secret@proxy.example.com:8080"
        identity = "http://proxy.example.com:8080"

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()

            await storage.audit_log_change(
                credentialed,
                "UPDATE",
                old_values={
                    "url": credentialed,
                    "username": "user",
                    "password": "secret",
                },
                new_values={
                    "url": credentialed,
                    "username": "user",
                    "password": "secret",
                    "passwd": "secret",
                    "usernames": ["user"],
                    "nested": {
                        "username": "user",
                        "password": "secret",
                        "token": "secret-token",
                        "api_key": "secret",
                    },
                    "items": [
                        {
                            "credentials": "secret",
                            "url": credentialed,
                        }
                    ],
                },
            )

            async with storage.engine.connect() as conn:
                audit_url, old_json, new_json = (
                    await conn.execute(
                        text("SELECT proxy_url, old_values, new_values FROM proxies_audit")
                    )
                ).one()

            assert audit_url == identity
            blob = f"{old_json}\n{new_json}"
            assert "user:secret@" not in blob
            assert "user:pass@" not in blob
            assert "secret" not in blob

            old_payload = json.loads(old_json)
            new_payload = json.loads(new_json)
            assert old_payload["username"] == "***"
            assert old_payload["password"] == "***"
            assert new_payload["username"] == "***"
            assert new_payload["password"] == "***"
            assert new_payload["passwd"] == "***"
            assert new_payload["usernames"] == "***"
            assert new_payload["nested"]["username"] == "***"
            assert new_payload["nested"]["password"] == "***"
            assert new_payload["nested"]["token"] == "***"
            assert new_payload["nested"]["api_key"] == "***"
            assert new_payload["items"][0]["credentials"] == "***"

            await storage.close()

    async def test_url_only_credentials_refused_without_encryption_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """f02: URL-embedded creds cannot bypass the plaintext-refusal gate."""
        from proxywhirl.exceptions import ProxyStorageError
        from proxywhirl.storage import SQLiteStorage

        monkeypatch.delenv("PROXYWHIRL_CACHE_ENCRYPTION_KEY", raising=False)
        monkeypatch.delenv("PROXYWHIRL_ENCRYPTION_KEY", raising=False)
        monkeypatch.delenv("PROXYWHIRL_KEY", raising=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "proxies.db"
            storage = SQLiteStorage(db_path)
            await storage.initialize()
            proxy = Proxy(url="http://user:secret@proxy.example.com:8080")
            with pytest.raises(ProxyStorageError, match="ENCRYPTION_KEY|Fernet key"):
                await storage.add_proxy(proxy)
            await storage.close()
