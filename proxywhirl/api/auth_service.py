"""Authentication Service

Secure authentication service for ProxyWhirl API.
Provides user management, password hashing, and authentication.
"""

import os
from typing import List, Optional, Union

from passlib.context import CryptContext

from .models.auth import User, UserInDB

# Password context for secure hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationService:
    """Manages user authentication and credentials securely."""

    def __init__(self):
        """Initialize with environment-based credentials."""
        self.admin_username = os.getenv("PROXYWHIRL_ADMIN_USERNAME", "admin")
        self.admin_email = os.getenv("PROXYWHIRL_ADMIN_EMAIL", "admin@proxywhirl.com")
        self.admin_password = os.getenv("PROXYWHIRL_ADMIN_PASSWORD")

        self.user_username = os.getenv("PROXYWHIRL_USER_USERNAME", "user")
        self.user_email = os.getenv("PROXYWHIRL_USER_EMAIL", "user@proxywhirl.com")
        self.user_password = os.getenv("PROXYWHIRL_USER_PASSWORD")

        # Warn if using default passwords
        if not self.admin_password:
            print(
                "⚠️  WARNING: Using default admin password. Set PROXYWHIRL_ADMIN_PASSWORD environment variable!"
            )
            self.admin_password = "changeme123!"

        if not self.user_password:
            print(
                "⚠️  WARNING: Using default user password. Set PROXYWHIRL_USER_PASSWORD environment variable!"
            )
            self.user_password = "changeme123!"

        # Create hashed passwords
        self.admin_password_hash = pwd_context.hash(self.admin_password)
        self.user_password_hash = pwd_context.hash(self.user_password)

        # In-memory user database (replace with real database in production)
        self.users_db = {
            self.admin_username: {
                "username": self.admin_username,
                "email": self.admin_email,
                "hashed_password": self.admin_password_hash,
                "disabled": False,
                "scopes": ["read", "write", "validate", "config", "admin"],
            },
            self.user_username: {
                "username": self.user_username,
                "email": self.user_email,
                "hashed_password": self.user_password_hash,
                "disabled": False,
                "scopes": ["read"],
            },
        }

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash using secure comparison."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate secure password hash."""
        return pwd_context.hash(password)

    def get_user(self, username: str) -> Optional[UserInDB]:
        """Get user from database."""
        if username in self.users_db:
            user_dict = self.users_db[username]
            return UserInDB(**user_dict)
        return None

    def authenticate_user(self, username: str, password: str) -> Union[UserInDB, bool]:
        """Authenticate user credentials securely."""
        user = self.get_user(username)
        if not user:
            # Prevent timing attacks - still hash a dummy password
            pwd_context.hash("dummy_password")
            return False

        if not self.verify_password(password, user.hashed_password):
            return False

        return user

    def create_user(
        self,
        username: str,
        password: str,
        email: str = None,
        scopes: List[str] = None,
        disabled: bool = False,
    ) -> UserInDB:
        """Create a new user (for future database integration)."""
        if scopes is None:
            scopes = ["read"]

        hashed_password = self.get_password_hash(password)

        user_data = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "disabled": disabled,
            "scopes": scopes,
        }

        # Add to in-memory database
        self.users_db[username] = user_data

        return UserInDB(**user_data)


# Global authentication service instance
_auth_service = None


def get_auth_service() -> AuthenticationService:
    """Get the global authentication service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthenticationService()
    return _auth_service


# Backward compatibility aliases
UserManager = AuthenticationService
user_manager = get_auth_service()
get_user_manager = get_auth_service
