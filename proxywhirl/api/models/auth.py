"""Authentication Models

Pydantic models for authentication and authorization.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """User information model."""

    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="User email address")
    disabled: bool = Field(default=False, description="Whether user account is disabled")
    scopes: List[str] = Field(default_factory=list, description="User permissions/scopes")


class UserInDB(User):
    """User model with hashed password for database storage."""

    hashed_password: str = Field(..., description="Hashed password")


class Token(BaseModel):
    """JWT Token response model."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_expires_in: Optional[int] = Field(None, description="Refresh token expiration in seconds")
    scopes: List[str] = Field(default_factory=list, description="Granted scopes")
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Token issued timestamp")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    
    refresh_token: str = Field(..., description="Valid refresh token")


class TokenData(BaseModel):
    """JWT Token payload data for internal use."""
    
    username: Optional[str] = None
    user_id: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)
    token_type: str = Field(default="access")  # "access" or "refresh"
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None
    jti: Optional[str] = None  # JWT ID for token blacklisting


class UserCreate(BaseModel):
    """User creation model."""
    
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=100, description="User full name")
    password: str = Field(..., min_length=8, description="User password")
    scopes: List[str] = Field(default=["read"], description="User permissions/scopes")


class UserUpdate(BaseModel):
    """User update model."""
    
    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, max_length=100, description="User full name")
    disabled: Optional[bool] = Field(None, description="Whether user account is disabled")
    scopes: Optional[List[str]] = Field(None, description="User permissions/scopes")


class PasswordChange(BaseModel):
    """Password change model."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class UserResponse(BaseModel):
    """User information response model."""
    
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")
    disabled: bool = Field(default=False, description="Whether user account is disabled")
    scopes: List[str] = Field(default_factory=list, description="User permissions/scopes")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_count: int = Field(default=0, description="Total login count")


class LoginAttempt(BaseModel):
    """Login attempt tracking model."""
    
    username: str = Field(..., description="Username")
    ip_address: str = Field(..., description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    success: bool = Field(..., description="Whether login was successful")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Attempt timestamp")
    failure_reason: Optional[str] = Field(None, description="Reason for failure if unsuccessful")


class SessionInfo(BaseModel):
    """Active session information."""
    
    session_id: str = Field(..., description="Session identifier")
    username: str = Field(..., description="Username")
    ip_address: str = Field(..., description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    expires_at: datetime = Field(..., description="Session expiration timestamp")
    scopes: List[str] = Field(default_factory=list, description="Session scopes")


class BlacklistedToken(BaseModel):
    """Blacklisted token model."""
    
    jti: str = Field(..., description="JWT ID")
    token_type: str = Field(..., description="Token type (access/refresh)")
    username: str = Field(..., description="Token owner username")
    blacklisted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Blacklist timestamp")
    expires_at: datetime = Field(..., description="Original token expiration")
    reason: str = Field(default="user_logout", description="Blacklist reason")


class AuthStats(BaseModel):
    """Authentication statistics."""
    
    total_users: int = Field(..., description="Total registered users")
    active_users: int = Field(..., description="Active (non-disabled) users")
    active_sessions: int = Field(..., description="Current active sessions")
    blacklisted_tokens: int = Field(..., description="Total blacklisted tokens")
    failed_attempts_last_hour: int = Field(..., description="Failed login attempts in last hour")
    successful_logins_last_24h: int = Field(..., description="Successful logins in last 24 hours")
    top_user_agents: Dict[str, int] = Field(default_factory=dict, description="Top user agents by frequency")
    login_attempts_by_hour: Dict[str, int] = Field(default_factory=dict, description="Login attempts by hour")

