# proxywhirl/auth.py
"""
Secure authentication module for ProxyWhirl API.

Replaces hardcoded credentials with environment variable-based user management
and provides secure password hashing and user validation.
"""

import os
from typing import List, Optional, Union

from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict

# Password context for secure hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    """User information model."""

    model_config = ConfigDict(from_attributes=True)

    username: str
    email: Optional[str] = None
    disabled: bool = False
    scopes: List[str] = []


class UserInDB(User):
    """User model with hashed password for database storage."""

    hashed_password: str


class UserManager:
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


# Global user manager instance
user_manager = UserManager()


def get_user_manager() -> UserManager:
    """Get the global user manager instance."""
    return user_manager
