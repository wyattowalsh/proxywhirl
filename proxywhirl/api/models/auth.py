"""Authentication Models

Pydantic models for authentication and authorization.
"""

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """JWT Token response model."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    scopes: List[str] = Field(default_factory=list, description="Granted scopes")
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Token issued timestamp")


class TokenData(BaseModel):
    """JWT Token payload data for internal use."""
    
    username: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None


class UserResponse(BaseModel):
    """User information response model."""
    
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")
    disabled: bool = Field(default=False, description="Whether user account is disabled")
    scopes: List[str] = Field(default_factory=list, description="User permissions/scopes")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
