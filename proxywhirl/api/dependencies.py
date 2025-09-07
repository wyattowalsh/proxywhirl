"""FastAPI Dependencies

Centralized dependency injection for ProxyWhirl API.
Includes authentication, authorization, and resource management dependencies.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from loguru import logger
from pydantic import ValidationError

from ..models import ProxyStatus
from ..proxywhirl import ProxyWhirl
from ..settings import get_api_settings
from .auth_service import get_auth_service
from .models.auth import TokenData, User, UserInDB

# Initialize settings and auth service
settings = get_api_settings()
auth_service = get_auth_service()

# OAuth2 scheme with comprehensive scopes
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        "read": "Read proxy data and health information",
        "write": "Fetch proxies and update health data",
        "validate": "Validate proxies and run health checks", 
        "config": "Modify configuration settings",
        "admin": "Full administrative access including user management",
        "websocket": "Access real-time WebSocket connections",
    },
)


# === Core Dependencies ===

async def get_proxywhirl() -> ProxyWhirl:
    """
    Get ProxyWhirl instance with proper error handling.
    
    This dependency provides access to the main ProxyWhirl instance
    with automatic initialization and error handling.
    """
    try:
        from fastapi import Request

        # Try to get from app state if available
        try:
            # This will work when called from an endpoint with request context
            import contextlib
            with contextlib.suppress(Exception):
                from contextvars import ContextVar

                from starlette.requests import Request

                # Use a more reliable approach
                pass
        except Exception:
            pass
        
        # Create new instance if not available from state
        return ProxyWhirl(auto_validate=True)
    except Exception as e:
        logger.error(f"Failed to initialize ProxyWhirl: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error_code": "SERVICE_UNAVAILABLE",
                "message": "ProxyWhirl service is currently unavailable",
                "details": {"error": str(e)},
            }
        )


def get_request_id() -> str:
    """Generate unique request ID for tracking and correlation."""
    return str(uuid.uuid4())


# === Authentication Dependencies ===

async def get_current_user(
    security_scopes: SecurityScopes, 
    token: Annotated[str, Depends(oauth2_scheme)]
) -> UserInDB:
    """
    Get current authenticated user with comprehensive scope validation.
    
    This dependency validates JWT tokens and ensures the user has
    the required scopes for the requested operation.
    """
    # Build authentication challenge header
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{" ".join(security_scopes.scopes)}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error_code": "INVALID_CREDENTIALS",
            "message": "Could not validate credentials",
            "required_scopes": security_scopes.scopes,
        },
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        # Decode and validate JWT token
        payload = jwt.decode(
            token, 
            settings.secret_key.get_secret_value(), 
            algorithms=[settings.algorithm]
        )
        
        # Extract token data
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
        
    except (JWTError, ValidationError) as e:
        logger.warning(f"JWT validation failed: {e}")
        raise credentials_exception
    
    # Get user from auth service
    user = auth_service.get_user(token_data.username)
    if user is None:
        logger.warning(f"User not found: {token_data.username}")
        raise credentials_exception
    
    # Validate required scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            logger.warning(
                f"Insufficient permissions for user {username}. "
                f"Required: {security_scopes.scopes}, Got: {token_data.scopes}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "INSUFFICIENT_PERMISSIONS",
                    "message": f"Not enough permissions. Required scope: {scope}",
                    "required_scopes": security_scopes.scopes,
                    "user_scopes": token_data.scopes,
                },
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return user


async def get_current_active_user(
    current_user: Annotated[UserInDB, Security(get_current_user, scopes=["read"])]
) -> UserInDB:
    """
    Get current active user, ensuring the user account is not disabled.
    
    This dependency builds on get_current_user to also check if the
    user account is active and not disabled.
    """
    if current_user.disabled:
        logger.warning(f"Disabled user attempted access: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "ACCOUNT_DISABLED",
                "message": "User account is disabled",
            }
        )
    return current_user


# === Specialized Dependencies ===

async def get_admin_user(
    current_user: Annotated[UserInDB, Security(get_current_user, scopes=["admin"])]
) -> UserInDB:
    """
    Get current user with admin privileges.
    
    This dependency ensures the user has admin scope for administrative operations.
    """
    return await get_current_active_user(current_user)


async def get_websocket_user(
    token: Optional[str] = None
) -> Optional[UserInDB]:
    """
    Authenticate WebSocket connection using JWT token.
    
    For WebSocket connections, authentication is optional but when provided,
    the token must be valid. Returns None if no token or invalid token.
    """
    if not token:
        return None
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm]
        )
        
        username: Optional[str] = payload.get("sub")
        if username is None:
            return None
        
        # Check if user exists and is active
        user = auth_service.get_user(username)
        if user is None or user.disabled:
            return None
        
        # Check for websocket scope
        token_scopes = payload.get("scopes", [])
        if "websocket" not in token_scopes:
            logger.warning(f"WebSocket access denied for user {username}: missing websocket scope")
            return None
        
        return user
        
    except (JWTError, ValidationError) as e:
        logger.warning(f"WebSocket authentication failed: {e}")
        return None


# === Query Parameter Dependencies ===

class CommonQueryParams:
    """Common query parameters for list endpoints with pagination and filtering."""
    
    def __init__(
        self,
        page: int = 1,
        page_size: int = 50,
        status: Optional[ProxyStatus] = None,
        scheme: Optional[str] = None,
        country: Optional[str] = None,
        min_quality: float = 0.0,
    ):
        # Validate pagination parameters
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_PAGINATION",
                    "message": "Page number must be >= 1",
                    "field": "page",
                }
            )
        
        if not (1 <= page_size <= 1000):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_PAGE_SIZE",
                    "message": "Page size must be between 1 and 1000",
                    "field": "page_size",
                }
            )
        
        # Validate quality score
        if not (0.0 <= min_quality <= 1.0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_QUALITY_SCORE", 
                    "message": "Quality score must be between 0.0 and 1.0",
                    "field": "min_quality",
                }
            )
        
        self.page = page
        self.page_size = page_size
        self.status = status
        self.scheme = scheme
        self.country = country.upper() if country else None
        self.min_quality = min_quality
        
        # Calculate offset for database queries
        self.offset = (page - 1) * page_size


# Common query params as dependency
CommonQuery = Annotated[CommonQueryParams, Depends(CommonQueryParams)]


# === Utility Dependencies ===

def get_timestamp() -> datetime:
    """Get current UTC timestamp for consistent time handling."""
    return datetime.now(timezone.utc)


def validate_proxy_id(proxy_id: str) -> str:
    """
    Validate proxy ID format (host:port).
    
    Ensures the proxy ID follows the expected format and contains
    valid host and port components.
    """
    if ":" not in proxy_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_PROXY_ID",
                "message": "Proxy ID must be in format 'host:port'",
                "provided": proxy_id,
            }
        )
    
    try:
        host, port_str = proxy_id.split(":", 1)
        port = int(port_str)
        
        if not host.strip():
            raise ValueError("Empty host")
        
        if not (1 <= port <= 65535):
            raise ValueError(f"Port {port} out of valid range (1-65535)")
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_PROXY_ID",
                "message": f"Invalid proxy ID format: {e}",
                "provided": proxy_id,
            }
        )
    
    return proxy_id


# === Type Aliases for Common Dependencies ===

# Authentication dependencies
CurrentUser = Annotated[UserInDB, Depends(get_current_active_user)]
AdminUser = Annotated[UserInDB, Depends(get_admin_user)]

# Resource dependencies  
ProxyWhirlDep = Annotated[ProxyWhirl, Depends(get_proxywhirl)]

# Utility dependencies
RequestID = Annotated[str, Depends(get_request_id)]
Timestamp = Annotated[datetime, Depends(get_timestamp)]
