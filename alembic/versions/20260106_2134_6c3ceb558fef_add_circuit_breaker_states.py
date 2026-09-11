"""Checkout bridge for packaged revision 6c3ceb558fef."""

from importlib import import_module as _import_module

_revision_module = _import_module(
    "proxywhirl._alembic.versions.20260106_2134_6c3ceb558fef_add_circuit_breaker_states"
)
revision = _revision_module.revision
down_revision = _revision_module.down_revision
branch_labels = _revision_module.branch_labels
depends_on = _revision_module.depends_on
upgrade = _revision_module.upgrade
downgrade = _revision_module.downgrade
