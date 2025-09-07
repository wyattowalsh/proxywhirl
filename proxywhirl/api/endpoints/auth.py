"""Authentication Endpoints

OAuth2 authentication endpoints for the ProxyWhirl API.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from ...settings import get_api_settings
from ..auth_service import get_auth_service
from ..dependencies import get_current_active_user
from ..models.auth import Token, User, UserInDB

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_api_settings()
auth_service = get_auth_service()


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token."""
    from jose import jwt
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)
    return encoded_jwt


@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    Authenticate user and return JWT access token with scopes.

    Uses OAuth2 password flow with comprehensive security features:
    - Rate limiting to prevent brute force attacks
    - Secure password verification with timing attack protection
    - Scope-based permission granting
    - Comprehensive audit logging
    """
    try:
        # Authenticate user with timing attack protection
        user_result = auth_service.authenticate_user(form_data.username, form_data.password)
        
        if not user_result or not isinstance(user_result, UserInDB):
            # Log failed authentication attempt
            logger.warning(
                f"Failed authentication attempt for user: {form_data.username} "
                f"from IP: {getattr(request.client, 'host', 'unknown')}"
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = user_result

        # Check if user account is disabled
        if user.disabled:
            logger.warning(f"Authentication attempt on disabled account: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Process requested scopes with validation
        requested_scopes = set(form_data.scopes) if form_data.scopes else set()
        available_scopes = set(user.scopes)
        
        # Grant intersection of requested and available scopes
        granted_scopes = list(requested_scopes.intersection(available_scopes))
        
        # If no scopes requested or granted, provide default read scope if available
        if not granted_scopes and "read" in available_scopes:
            granted_scopes = ["read"]
        
        # Create access token with user claims and scopes
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        token_data = {
            "sub": user.username,
            "scopes": granted_scopes,
            "iat": datetime.now(timezone.utc),
            "email": user.email,
            "token_type": "access_token"
        }
        
        access_token = create_access_token(
            data=token_data, 
            expires_delta=access_token_expires
        )

        # Log successful authentication
        logger.info(
            f"Successful authentication for user: {user.username}, "
            f"scopes: {granted_scopes}, "
            f"from IP: {getattr(request.client, 'host', 'unknown')}"
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            scopes=granted_scopes,
            issued_at=datetime.now(timezone.utc)
        )

    except HTTPException:
        # Re-raise HTTP exceptions (authentication failures)
        raise
    except Exception as e:
        # Log and handle unexpected errors
        logger.error(f"Authentication endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )


@router.get("/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Get current user information."""
    return current_user