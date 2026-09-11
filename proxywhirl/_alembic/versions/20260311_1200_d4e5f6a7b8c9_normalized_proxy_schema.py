"""normalized_proxy_schema (packaged)

Revision ID: d4e5f6a7b8c9
Revises: 43cb4a16de9d
Create Date: 2026-03-11 12:00:00.000000+00:00

Schema SSOT for normalized proxy storage. Creates ``proxy_identities``,
``proxy_statuses``, ``validation_results``, and ``proxies_audit``; backfills
``expires_at`` on pre-existing identity tables; installs composite indexes;
and copies legacy ``proxies`` rows into the normalized tables.

Upgrade path: ``await run_migrations(db_url, "head")`` (also used by
``SQLiteStorage.initialize()``). Do not apply runtime ``ALTER TABLE`` outside
Alembic revisions.
"""

from __future__ import annotations

from collections.abc import Sequence
from urllib.parse import urlparse

import sqlalchemy as sa
import sqlmodel.sql.sqltypes

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "43cb4a16de9d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_exists(conn: sa.Connection, name: str) -> bool:
    inspector = sa.inspect(conn)
    return name in inspector.get_table_names()


def _column_names(conn: sa.Connection, table: str) -> set[str]:
    return {col["name"] for col in sa.inspect(conn).get_columns(table)}


def _index_names(conn: sa.Connection, table: str) -> set[str]:
    return {
        name
        for index in sa.inspect(conn).get_indexes(table)
        if isinstance((name := index.get("name")), str)
    }


def _create_normalized_tables() -> None:
    """Create normalized tables when missing (idempotent)."""
    if not _table_exists(op.get_bind(), "proxy_identities"):
        op.create_table(
            "proxy_identities",
            sa.Column("url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("protocol", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("host", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("port", sa.Integer(), nullable=False),
            sa.Column("username", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("password", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("country_code", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("country_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("region", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("city", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("latitude", sa.Float(), nullable=True),
            sa.Column("longitude", sa.Float(), nullable=True),
            sa.Column("asn", sa.Integer(), nullable=True),
            sa.Column("isp_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("is_residential", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("is_datacenter", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("source", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("source_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("discovered_at", sa.DateTime(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("url"),
        )
        with op.batch_alter_table("proxy_identities", schema=None) as batch_op:
            batch_op.create_index("ix_proxy_identities_protocol", ["protocol"], unique=False)
            batch_op.create_index("ix_proxy_identities_host", ["host"], unique=False)
            batch_op.create_index(
                "ix_proxy_identities_country_code", ["country_code"], unique=False
            )
            batch_op.create_index("ix_proxy_identities_source", ["source"], unique=False)
            batch_op.create_index("ix_proxy_identities_expires_at", ["expires_at"], unique=False)
            batch_op.create_index("uq_proxy_identities_host_port", ["host", "port"], unique=True)

    if not _table_exists(op.get_bind(), "proxy_statuses"):
        op.create_table(
            "proxy_statuses",
            sa.Column("proxy_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("health_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("last_success_at", sa.DateTime(), nullable=True),
            sa.Column("last_failure_at", sa.DateTime(), nullable=True),
            sa.Column("last_check_at", sa.DateTime(), nullable=True),
            sa.Column("consecutive_successes", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("total_checks", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("total_successes", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("avg_response_time_ms", sa.Float(), nullable=True),
            sa.Column("success_rate_7d", sa.Float(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["proxy_url"], ["proxy_identities.url"]),
            sa.PrimaryKeyConstraint("proxy_url"),
        )
        with op.batch_alter_table("proxy_statuses", schema=None) as batch_op:
            batch_op.create_index(
                "ix_proxy_statuses_health_status", ["health_status"], unique=False
            )
            batch_op.create_index(
                "ix_proxy_statuses_last_success_at", ["last_success_at"], unique=False
            )
            batch_op.create_index(
                "ix_proxy_statuses_last_check_at", ["last_check_at"], unique=False
            )
            batch_op.create_index(
                "ix_proxy_statuses_success_rate_7d", ["success_rate_7d"], unique=False
            )
            batch_op.create_index("ix_proxy_statuses_updated_at", ["updated_at"], unique=False)

    if not _table_exists(op.get_bind(), "validation_results"):
        op.create_table(
            "validation_results",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("proxy_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("validated_at", sa.DateTime(), nullable=False),
            sa.Column("is_valid", sa.Boolean(), nullable=False),
            sa.Column("response_time_ms", sa.Float(), nullable=True),
            sa.Column("error_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("error_message", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.ForeignKeyConstraint(["proxy_url"], ["proxy_identities.url"]),
            sa.PrimaryKeyConstraint("id"),
        )
        with op.batch_alter_table("validation_results", schema=None) as batch_op:
            batch_op.create_index("ix_validation_results_proxy_url", ["proxy_url"], unique=False)
            batch_op.create_index(
                "ix_validation_results_validated_at", ["validated_at"], unique=False
            )

    if not _table_exists(op.get_bind(), "proxies_audit"):
        op.create_table(
            "proxies_audit",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("proxy_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("action", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("old_values", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("new_values", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("timestamp", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        with op.batch_alter_table("proxies_audit", schema=None) as batch_op:
            batch_op.create_index("ix_proxies_audit_proxy_url", ["proxy_url"], unique=False)
            batch_op.create_index("ix_proxies_audit_timestamp", ["timestamp"], unique=False)


def _ensure_expires_at_column(conn: sa.Connection) -> None:
    """Add ``expires_at`` to pre-normalized identity tables created without it."""
    if not _table_exists(conn, "proxy_identities"):
        return
    if "expires_at" in _column_names(conn, "proxy_identities"):
        return
    op.add_column(
        "proxy_identities",
        sa.Column("expires_at", sa.DateTime(), nullable=True),
    )


def _ensure_supplemental_indexes(conn: sa.Connection) -> None:
    """Create composite / covering indexes used by storage query paths."""
    index_ddl = (
        (
            "proxy_identities",
            "ix_proxy_identities_expires_at",
            "CREATE INDEX IF NOT EXISTS ix_proxy_identities_expires_at "
            "ON proxy_identities(expires_at)",
        ),
        (
            "validation_results",
            "idx_validation_proxy_time",
            "CREATE INDEX IF NOT EXISTS idx_validation_proxy_time "
            "ON validation_results(proxy_url, validated_at)",
        ),
        (
            "proxy_statuses",
            "idx_proxy_status_health",
            "CREATE INDEX IF NOT EXISTS idx_proxy_status_health "
            "ON proxy_statuses(health_status, last_success_at DESC)",
        ),
        (
            "proxy_statuses",
            "idx_proxy_status_success_rate",
            "CREATE INDEX IF NOT EXISTS idx_proxy_status_success_rate "
            "ON proxy_statuses(success_rate_7d DESC)",
        ),
        (
            "validation_results",
            "idx_validation_recent_valid",
            "CREATE INDEX IF NOT EXISTS idx_validation_recent_valid "
            "ON validation_results(is_valid, validated_at DESC)",
        ),
        (
            "proxy_statuses",
            "idx_proxy_status_recent_success",
            "CREATE INDEX IF NOT EXISTS idx_proxy_status_recent_success "
            "ON proxy_statuses(last_success_at DESC)",
        ),
    )
    for table, index_name, ddl in index_ddl:
        if not _table_exists(conn, table):
            continue
        if index_name in _index_names(conn, table):
            continue
        conn.execute(sa.text(ddl))


def _migrate_legacy_proxies(conn: sa.Connection) -> None:
    """One-shot copy from legacy ``proxies`` into normalized tables."""
    if not _table_exists(conn, "proxies"):
        return

    legacy_cols = {col["name"] for col in sa.inspect(conn).get_columns("proxies")}
    if "url" not in legacy_cols:
        return

    rows = conn.execute(sa.text("SELECT * FROM proxies")).mappings().all()
    if not rows:
        return

    for row in rows:
        url = row.get("url")
        if not url:
            continue
        exists = conn.execute(
            sa.text("SELECT 1 FROM proxy_identities WHERE url = :url"),
            {"url": url},
        ).first()
        if exists:
            continue

        protocol = row.get("protocol") or "http"
        parsed = urlparse(url if "://" in str(url) else f"{protocol}://{url}")
        host = parsed.hostname or ""
        port = parsed.port or (443 if protocol == "https" else 80)

        conn.execute(
            sa.text(
                """
                INSERT INTO proxy_identities (
                    url, protocol, host, port, username, password,
                    country_code, region, source, source_url, discovered_at, expires_at,
                    is_residential, is_datacenter
                ) VALUES (
                    :url, :protocol, :host, :port, :username, :password,
                    :country_code, :region, :source, :source_url,
                    COALESCE(:created_at, CURRENT_TIMESTAMP), :expires_at,
                    0, 0
                )
                """
            ),
            {
                "url": url,
                "protocol": protocol,
                "host": host,
                "port": port,
                "username": row.get("username"),
                "password": row.get("password"),
                "country_code": row.get("country_code") if "country_code" in legacy_cols else None,
                "region": row.get("region") if "region" in legacy_cols else None,
                "source": row.get("source") or "fetched",
                "source_url": row.get("source_url"),
                "created_at": row.get("created_at"),
                "expires_at": row.get("expires_at") if "expires_at" in legacy_cols else None,
            },
        )

        health = row.get("health_status") or "unknown"
        conn.execute(
            sa.text(
                """
                INSERT INTO proxy_statuses (
                    proxy_url, health_status, last_success_at, last_failure_at,
                    consecutive_failures, total_checks, total_successes,
                    avg_response_time_ms, updated_at
                ) VALUES (
                    :url, :health_status, :last_success_at, :last_failure_at,
                    COALESCE(:consecutive_failures, 0),
                    COALESCE(:total_checks, 0),
                    COALESCE(:total_successes, 0),
                    :avg_response_time_ms, CURRENT_TIMESTAMP
                )
                """
            ),
            {
                "url": url,
                "health_status": health,
                "last_success_at": row.get("last_success_at"),
                "last_failure_at": row.get("last_failure_at"),
                "consecutive_failures": row.get("consecutive_failures"),
                "total_checks": row.get("total_checks"),
                "total_successes": row.get("total_successes"),
                "avg_response_time_ms": row.get("average_response_time_ms")
                if "average_response_time_ms" in legacy_cols
                else row.get("avg_response_time_ms"),
            },
        )


def upgrade() -> None:
    """Upgrade to normalized schema SSOT."""
    _create_normalized_tables()
    conn = op.get_bind()
    _ensure_expires_at_column(conn)
    _ensure_supplemental_indexes(conn)
    _migrate_legacy_proxies(conn)


def downgrade() -> None:
    """Drop normalized tables (legacy proxies table is preserved)."""
    for table in (
        "proxies_audit",
        "validation_results",
        "proxy_statuses",
        "proxy_identities",
    ):
        if _table_exists(op.get_bind(), table):
            op.drop_table(table)
