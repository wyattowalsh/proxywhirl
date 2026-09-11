"""Checkout bridge for packaged revision a1b2c3d4e5f6."""

from importlib import import_module as _import_module

_revision_module = _import_module(
    "proxywhirl._alembic.versions.20251226_2046_a1b2c3d4e5f6_expand_proxy_schema"
)
revision = _revision_module.revision
down_revision = _revision_module.down_revision
branch_labels = _revision_module.branch_labels
depends_on = _revision_module.depends_on
upgrade = _revision_module.upgrade
downgrade = _revision_module.downgrade
