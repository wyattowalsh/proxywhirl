"""Authentication Endpoints

JWT-based authentication with OAuth2 scopes and refresh tokens.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

from ...auth import get_user_manager
from ...settings import get_api_settings
from ..dependencies import get_current_active_user
from ..models.auth import Token, UserResponse

# Initialize dependencies
settings = get_api_settings()
user_manager = get_user_manager()
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token with proper expiration."""
    from jose import jwt
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, 
        settings.secret_key.get_secret_value(), 
        algorithm=settings.algorithm
    )


@router.post("/token", response_model=Token, summary="Obtain access token")
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    Authenticate user and return JWT access token.
    
    Rate limited to 5 attempts per minute to prevent brute force attacks.
    """
    # Authenticate user
    user = user_manager.get_user(form_data.username)
    if not user or not user_mgr.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_CREDENTIALS",
                "message": "Incorrect username or password",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is disabled
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "ACCOUNT_DISABLED", 
                "message": "User account is disabled",
            }
        )
    
    # Parse requested scopes
    requested_scopes = form_data.scopes if form_data.scopes else ["read"]
    
    # Filter scopes based on user permissions
    # In a real implementation, you'd check user.scopes against requested_scopes
    granted_scopes = requested_scopes  # Simplified for now
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "scopes": granted_scopes,
        },
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        scopes=granted_scopes,
        issued_at=datetime.now(timezone.utc),
    )


@router.get("/me", response_model=UserResponse, summary="Get current user info")
async def read_users_me(
    current_user: Annotated[dict, Depends(get_current_active_user)]
) -> UserResponse:
    """Get current authenticated user information."""
    return UserResponse(
        username=current_user.username,
        email=getattr(current_user, 'email', None),
        full_name=getattr(current_user, 'full_name', None),
        disabled=current_user.disabled,
        scopes=getattr(current_user, 'scopes', []),
        created_at=getattr(current_user, 'created_at', None),
        last_login=getattr(current_user, 'last_login', None),
    )
