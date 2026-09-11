"""Checkout bridge for packaged revision d4e5f6a7b8c9."""

from importlib import import_module as _import_module

_revision_module = _import_module(
    "proxywhirl._alembic.versions.20260311_1200_d4e5f6a7b8c9_normalized_proxy_schema"
)
revision = _revision_module.revision
down_revision = _revision_module.down_revision
branch_labels = _revision_module.branch_labels
depends_on = _revision_module.depends_on
upgrade = _revision_module.upgrade
downgrade = _revision_module.downgrade
