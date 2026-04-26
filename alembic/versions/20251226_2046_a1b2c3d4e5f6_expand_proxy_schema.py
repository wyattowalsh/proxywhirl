"""expand_proxy_schema

Revision ID: a1b2c3d4e5f6
Revises: 616bc0c6a5b5
Create Date: 2025-12-26 20:46:00.000000+00:00

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "616bc0c6a5b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema.

    This migration expands the proxies table with comprehensive analytics,
    health monitoring, geo-location, and performance tracking fields to
    support advanced rotation strategies and observability features.

    New field categories:
    - UUID tracking: proxy_uuid
    - Enhanced request tracking: requests_started, requests_completed, requests_active
    - EMA tracking: ema_response_time_ms, ema_alpha
    - Sliding window: window_start, window_duration_seconds
    - Health monitoring: consecutive_successes, recovery_attempt, next_check_time,
      last_health_error, total_checks, total_health_failures, last_health_check
    - Tags: tags_json (JSON array)
    - Geo-location: region, country_code (indexed), country_name, city, isp_name,
      asn, latitude, longitude
    - TTL fields: ttl, expires_at
    - Analytics: response_time_p50_ms, response_time_p95_ms, response_time_p99_ms,
      min_response_time_ms, max_response_time_ms, response_time_stddev_ms,
      response_samples_count, error_types_json, last_error_type, last_error_message,
      last_error_at, timeout_count, connection_refused_count, ssl_error_count,
      http_4xx_count, http_5xx_count
    - Proxy type: is_residential, is_datacenter, is_vpn, is_tor
    - Protocol support: http_version, tls_version, supports_https, supports_connect,
      supports_http2
    - Health transitions: health_status_transitions_json, last_recovered_at,
      revival_attempts
    - Source metadata: source_name, fetch_timestamp, fetch_duration_ms
    - Validation: last_validation_time, validation_method
    """
    # Use batch operations for SQLite compatibility
    with op.batch_alter_table("proxies", schema=None) as batch_op:
        # UUID tracking
        batch_op.add_column(sa.Column("proxy_uuid", sa.String(), nullable=True))

        # Enhanced request tracking (Phase 2: Intelligent Rotation Strategies)
        batch_op.add_column(
            sa.Column("requests_started", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("requests_completed", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("requests_active", sa.Integer(), nullable=False, server_default="0")
        )

        # EMA (Exponential Moving Average) tracking for performance-based strategies
        batch_op.add_column(sa.Column("ema_response_time_ms", sa.Float(), nullable=True))
        batch_op.add_column(
            sa.Column("ema_alpha", sa.Float(), nullable=False, server_default="0.2")
        )

        # Sliding window for counter staleness prevention
        batch_op.add_column(sa.Column("window_start", sa.DateTime(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "window_duration_seconds", sa.Integer(), nullable=False, server_default="3600"
            )
        )

        # Health monitoring fields (Feature 006)
        batch_op.add_column(
            sa.Column("consecutive_successes", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("recovery_attempt", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(sa.Column("next_check_time", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("last_health_error", sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column("total_checks", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("total_health_failures", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(sa.Column("last_health_check", sa.DateTime(), nullable=True))

        # Tags (stored as JSON array)
        batch_op.add_column(sa.Column("tags_json", sa.String(), nullable=True))

        # Geo-location for geo-targeted strategies
        batch_op.add_column(sa.Column("region", sa.String(), nullable=True))

        # TTL fields for automatic expiration
        batch_op.add_column(sa.Column("ttl", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("expires_at", sa.DateTime(), nullable=True))

        # Analytics: Response time percentiles
        batch_op.add_column(sa.Column("response_time_p50_ms", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("response_time_p95_ms", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("response_time_p99_ms", sa.Float(), nullable=True))

        # Analytics: Response time statistics
        batch_op.add_column(sa.Column("min_response_time_ms", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("max_response_time_ms", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("response_time_stddev_ms", sa.Float(), nullable=True))
        batch_op.add_column(
            sa.Column("response_samples_count", sa.Integer(), nullable=False, server_default="0")
        )

        # Analytics: Error tracking
        batch_op.add_column(sa.Column("error_types_json", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("last_error_type", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("last_error_message", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("last_error_at", sa.DateTime(), nullable=True))

        # Analytics: Error counters by type
        batch_op.add_column(
            sa.Column("timeout_count", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("connection_refused_count", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("ssl_error_count", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("http_4xx_count", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("http_5xx_count", sa.Integer(), nullable=False, server_default="0")
        )

        # Geo-location: Enhanced location data with INDEXED country_code
        batch_op.add_column(sa.Column("country_code", sa.String(length=2), nullable=True))
        batch_op.add_column(sa.Column("country_name", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("city", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("isp_name", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("asn", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("latitude", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("longitude", sa.Float(), nullable=True))

        # Proxy type classification
        batch_op.add_column(sa.Column("is_residential", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("is_datacenter", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("is_vpn", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("is_tor", sa.Boolean(), nullable=True))

        # Protocol support capabilities
        batch_op.add_column(sa.Column("http_version", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("tls_version", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("supports_https", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("supports_connect", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("supports_http2", sa.Boolean(), nullable=True))

        # Health status transition tracking
        batch_op.add_column(sa.Column("health_status_transitions_json", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("last_recovered_at", sa.DateTime(), nullable=True))
        batch_op.add_column(
            sa.Column("revival_attempts", sa.Integer(), nullable=False, server_default="0")
        )

        # Source metadata
        batch_op.add_column(sa.Column("source_name", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("fetch_timestamp", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("fetch_duration_ms", sa.Float(), nullable=True))

        # Validation metadata
        batch_op.add_column(sa.Column("last_validation_time", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("validation_method", sa.String(), nullable=True))

        # Create index on country_code for geo-targeted strategies
        batch_op.create_index(batch_op.f("ix_proxies_country_code"), ["country_code"], unique=False)


def downgrade() -> None:
    """Downgrade database schema.

    This migration reverts schema changes. Use with caution in production.
    Ensure data backups exist before running downgrades.

    WARNING: This will drop all data in the new columns!
    """
    with op.batch_alter_table("proxies", schema=None) as batch_op:
        # Drop index
        batch_op.drop_index(batch_op.f("ix_proxies_country_code"))

        # Drop all new columns in reverse order
        batch_op.drop_column("validation_method")
        batch_op.drop_column("last_validation_time")
        batch_op.drop_column("fetch_duration_ms")
        batch_op.drop_column("fetch_timestamp")
        batch_op.drop_column("source_name")
        batch_op.drop_column("revival_attempts")
        batch_op.drop_column("last_recovered_at")
        batch_op.drop_column("health_status_transitions_json")
        batch_op.drop_column("supports_http2")
        batch_op.drop_column("supports_connect")
        batch_op.drop_column("supports_https")
        batch_op.drop_column("tls_version")
        batch_op.drop_column("http_version")
        batch_op.drop_column("is_tor")
        batch_op.drop_column("is_vpn")
        batch_op.drop_column("is_datacenter")
        batch_op.drop_column("is_residential")
        batch_op.drop_column("longitude")
        batch_op.drop_column("latitude")
        batch_op.drop_column("asn")
        batch_op.drop_column("isp_name")
        batch_op.drop_column("city")
        batch_op.drop_column("country_name")
        batch_op.drop_column("country_code")
        batch_op.drop_column("http_5xx_count")
        batch_op.drop_column("http_4xx_count")
        batch_op.drop_column("ssl_error_count")
        batch_op.drop_column("connection_refused_count")
        batch_op.drop_column("timeout_count")
        batch_op.drop_column("last_error_at")
        batch_op.drop_column("last_error_message")
        batch_op.drop_column("last_error_type")
        batch_op.drop_column("error_types_json")
        batch_op.drop_column("response_samples_count")
        batch_op.drop_column("response_time_stddev_ms")
        batch_op.drop_column("max_response_time_ms")
        batch_op.drop_column("min_response_time_ms")
        batch_op.drop_column("response_time_p99_ms")
        batch_op.drop_column("response_time_p95_ms")
        batch_op.drop_column("response_time_p50_ms")
        batch_op.drop_column("expires_at")
        batch_op.drop_column("ttl")
        batch_op.drop_column("region")
        batch_op.drop_column("tags_json")
        batch_op.drop_column("last_health_check")
        batch_op.drop_column("total_health_failures")
        batch_op.drop_column("total_checks")
        batch_op.drop_column("last_health_error")
        batch_op.drop_column("next_check_time")
        batch_op.drop_column("recovery_attempt")
        batch_op.drop_column("consecutive_successes")
        batch_op.drop_column("window_duration_seconds")
        batch_op.drop_column("window_start")
        batch_op.drop_column("ema_alpha")
        batch_op.drop_column("ema_response_time_ms")
        batch_op.drop_column("requests_active")
        batch_op.drop_column("requests_completed")
        batch_op.drop_column("requests_started")
        batch_op.drop_column("proxy_uuid")
