"""Permission-based access control for API operations.

Implements role-based authorization with different access levels
for different operations on proxies and pools.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from loguru import logger


class Permission(str, Enum):
    """API operation permissions."""

    # Pool operations
    POOL_READ = "pool:read"
    POOL_CREATE = "pool:create"
    POOL_UPDATE = "pool:update"
    POOL_DELETE = "pool:delete"

    # Proxy operations
    PROXY_READ = "proxy:read"
    PROXY_CREATE = "proxy:create"
    PROXY_UPDATE = "proxy:update"
    PROXY_DELETE = "proxy:delete"

    # Admin operations
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"
    SYSTEM_CONFIG = "system:config"


class Role(str, Enum):
    """User roles with different permission sets."""

    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.VIEWER: {
        Permission.POOL_READ,
        Permission.PROXY_READ,
        Permission.ADMIN_READ,
    },
    Role.OPERATOR: {
        Permission.POOL_READ,
        Permission.POOL_UPDATE,
        Permission.PROXY_READ,
        Permission.PROXY_UPDATE,
        Permission.ADMIN_READ,
    },
    Role.ADMIN: set(Permission),  # All permissions
}


@dataclass
class User:
    """Represents an API user with roles and permissions."""

    user_id: str
    roles: set[Role]
    permissions: set[Permission] | None = None

    def __post_init__(self) -> None:
        """Calculate effective permissions from roles."""
        if self.permissions is None:
            self.permissions = set()
            for role in self.roles:
                self.permissions.update(ROLE_PERMISSIONS.get(role, set()))

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission in (self.permissions or set())

    def has_any_permission(self, permissions: set[Permission]) -> bool:
        """Check if user has any of the given permissions."""
        return bool((self.permissions or set()) & permissions)

    def has_all_permissions(self, permissions: set[Permission]) -> bool:
        """Check if user has all of the given permissions."""
        return permissions.issubset(self.permissions or set())

    def add_role(self, role: Role) -> None:
        """Add a role to the user."""
        self.roles.add(role)
        if self.permissions:
            self.permissions.update(ROLE_PERMISSIONS.get(role, set()))

    def remove_role(self, role: Role) -> None:
        """Remove a role from the user."""
        self.roles.discard(role)
        self._recalculate_permissions()

    def _recalculate_permissions(self) -> None:
        """Recalculate permissions based on current roles."""
        self.permissions = set()
        for role in self.roles:
            self.permissions.update(ROLE_PERMISSIONS.get(role, set()))


class PermissionManager:
    """Manages user permissions and access control."""

    def __init__(self) -> None:
        """Initialize permission manager."""
        self.users: dict[str, User] = {}
        self.audit_log: list[dict[str, Any]] = []

    def create_user(self, user_id: str, roles: set[Role] | None = None) -> User:
        """Create a new user with given roles."""
        if roles is None:
            roles = {Role.VIEWER}

        user = User(user_id=user_id, roles=roles)
        self.users[user_id] = user
        self._log_audit(f"User created: {user_id}", {"roles": [r.value for r in roles]})
        logger.info(f"Created user: {user_id} with roles: {roles}")
        return user

    def get_user(self, user_id: str) -> User | None:
        """Retrieve a user by ID."""
        return self.users.get(user_id)

    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        user = self.get_user(user_id)
        if not user:
            logger.warning(f"Permission check for unknown user: {user_id}")
            return False

        has_perm = user.has_permission(permission)
        self._log_audit(
            f"Permission check: {permission.value}",
            {"user_id": user_id, "allowed": has_perm},
        )
        return has_perm

    def require_permission(self, user_id: str, permission: Permission) -> None:
        """Require a permission, raise PermissionError if denied."""
        if not self.check_permission(user_id, permission):
            self._log_audit(
                f"Permission denied: {permission.value}",
                {"user_id": user_id},
            )
            raise PermissionError(f"User {user_id} does not have permission: {permission.value}")

    def update_user_roles(self, user_id: str, roles: set[Role]) -> User:
        """Update a user's roles."""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        user.roles = roles
        user._recalculate_permissions()
        self._log_audit(f"User roles updated: {user_id}", {"roles": [r.value for r in roles]})
        logger.info(f"Updated user {user_id} roles to: {roles}")
        return user

    def delete_user(self, user_id: str) -> None:
        """Delete a user."""
        if user_id in self.users:
            del self.users[user_id]
            self._log_audit(f"User deleted: {user_id}", {})
            logger.info(f"Deleted user: {user_id}")

    def _log_audit(self, action: str, details: dict[str, Any]) -> None:
        """Log an audit event."""
        self.audit_log.append({"action": action, "details": details})

    def get_audit_log(self) -> list[dict[str, Any]]:
        """Retrieve audit log."""
        return self.audit_log.copy()


_permission_manager: PermissionManager | None = None


def get_permission_manager() -> PermissionManager:
    """Get global permission manager instance."""
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager
