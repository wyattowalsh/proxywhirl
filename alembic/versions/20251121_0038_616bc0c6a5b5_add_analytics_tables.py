"""Checkout bridge for packaged revision 616bc0c6a5b5."""

from importlib import import_module as _import_module

_revision_module = _import_module(
    "proxywhirl._alembic.versions.20251121_0038_616bc0c6a5b5_add_analytics_tables"
)
revision = _revision_module.revision
down_revision = _revision_module.down_revision
branch_labels = _revision_module.branch_labels
depends_on = _revision_module.depends_on
upgrade = _revision_module.upgrade
downgrade = _revision_module.downgrade
